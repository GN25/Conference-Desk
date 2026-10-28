#!/usr/bin/env python3
"""Conference Desk's deterministic I/O, scheduling and portable pack support."""
import argparse
import datetime as dt
import gzip
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

UTC = dt.timezone.utc
MAX_BYTES = 20_000_000


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


class Plain(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)
    def handle_starttag(self, tag, attrs):
        if tag in ('p','br','li','div'): self.parts.append('\n')


def plain(value):
    parser = Plain(); parser.feed(value or '')
    # Remove control characters, preserve human-readable Unicode and newlines.
    return '\n'.join(' '.join(''.join(c for c in line if ord(c) >= 32 or c == '\t').split())
                     for line in ''.join(parser.parts).splitlines() if line.strip()).strip()


def safe_url(value):
    u = urlparse(value)
    if u.scheme not in ('https', 'http') or not u.netloc or any(ord(c)<32 for c in value):
        raise ValueError('Expected an HTTP(S) source link')
    return value


def instant(value):
    v = dt.datetime.fromisoformat(value)
    if v.tzinfo is None: raise ValueError('All session times must have UTC offsets')
    return v


def catalog_check(c):
    claimed = c['catalog_sha256']
    if digest({k:v for k,v in c.items() if k != 'catalog_sha256'}) != claimed:
        raise ValueError('Catalog hash mismatch')
    ZoneInfo(c['conference']['timezone'])
    ids=set()
    for e in c['events']:
        if e['id'] in ids: raise ValueError('Duplicate event ID: '+e['id'])
        ids.add(e['id'])
        if instant(e['end']) <= instant(e['start']): raise ValueError('Nonpositive duration')
        safe_url(e['url'])
        for link in e['links']: safe_url(link['url'])
    return c


def ingest(source, out):
    if source.startswith(('https://','http://')):
        if not source.startswith('https://'): raise ValueError('Fetch requires HTTPS')
        req=urllib.request.Request(source, headers={'User-Agent':'Conference-Desk/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                if urlparse(response.url).scheme != 'https': raise ValueError('Insecure redirect')
                raw=response.read(MAX_BYTES+1)
        except urllib.error.URLError as error:
            if not isinstance(error.reason,ssl.SSLCertVerificationError) or not shutil.which('curl'):
                raise
            # Some macOS Python distributions have no configured CA bundle.
            # Use the installed system client's verified trust store, never -k.
            result=subprocess.run(['curl','--fail','--location','--silent','--show-error',
                '--max-time','45','--max-filesize',str(MAX_BYTES),'--proto','=https',
                '--proto-redir','=https',source],capture_output=True)
            if result.returncode:
                raise ValueError('Verified system download failed: '+result.stderr.decode(errors='replace')[:500])
            raw=result.stdout
        source_url=source
    else:
        raw=Path(source).read_bytes(); source_url=None
    if len(raw)>MAX_BYTES: raise ValueError('Schedule exceeds 20 MB')
    if raw[:2] == b'\x1f\x8b':
        # Bound decompression as well as the downloaded size.
        import io
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream: raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES or b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('Oversize or entity-bearing XML is unsupported')
    root=ET.fromstring(raw)
    conf=root.find('conference')
    if conf is None: raise ValueError('Missing conference element')
    val=lambda node,key: (node.findtext(key) or '').strip()
    timezone=val(conf,'time_zone_name')
    ZoneInfo(timezone)
    base=safe_url(val(conf,'base_url'))
    events=[]
    for day in root.findall('day'):
        for room in day.findall('room'):
            for node in room.findall('event'):
                start=instant(val(node,'date'))
                # Compare exporter offset with declared timezone, catching silent DST errors.
                if start.utcoffset() != start.astimezone(ZoneInfo(timezone)).utcoffset():
                    raise ValueError('Session offset disagrees with conference timezone')
                h,m=map(int,val(node,'duration').split(':'))
                end=start+dt.timedelta(hours=h,minutes=m)
                links=[]
                for link in list(node.findall('links/link'))+list(node.findall('attachments/attachment')):
                    href=link.get('href','')
                    if href.startswith(('http://','https://')):
                        links.append({'label':plain(link.text),'url':safe_url(href)})
                events.append({'id':node.get('guid') or node.get('id'), 'title':val(node,'title'),
                    'start':start.isoformat(),'end':end.isoformat(),'room':val(node,'room') or room.get('name',''),
                    'track':val(node,'track'),'url':safe_url(val(node,'url')),
                    'speakers':[plain(p.text) for p in node.findall('persons/person')],
                    'abstract':plain(val(node,'abstract')),'description':plain(val(node,'description')),'links':links})
    c={'conference':{'id':val(conf,'acronym'),'title':val(conf,'title'),'timezone':timezone,'base_url':base},
       'source':{'url':source_url or base+'xml','sha256':hashlib.sha256(raw).hexdigest(),
                 'fetched_at':dt.datetime.now(UTC).isoformat()},'events':sorted(events,key=lambda e:(e['start'],e['id']))}
    if not events: raise ValueError('No events parsed')
    c['catalog_sha256']=digest(c); catalog_check(c); dump(out,c)
    print(json.dumps({'events':len(events),'catalog_sha256':c['catalog_sha256'],'out':str(out)}))


def clock(c,date,time):
    return dt.datetime.fromisoformat(date+'T'+time).replace(tzinfo=ZoneInfo(c['conference']['timezone']))


def brief_check(c,b):
    ZoneInfo(b['display_timezone'])
    if not 1<=b['max_sessions_per_day']<=30: raise ValueError('Session cap must be 1..30')
    for key in ['transition_minutes','same_room_minutes']:
        if not 0<=b[key]<=180: raise ValueError('Transition allowance must be 0..180 minutes')
    dates=[d['date'] for d in b['days']]
    if len(dates)!=len(set(dates)): raise ValueError('Duplicate attendance day')
    for d in b['days']+b.get('breaks',[]):
        if clock(c,d['date'],d['end'])<=clock(c,d['date'],d['start']): raise ValueError('Invalid time window')


def feasibility(c,b,e):
    start,end=instant(e['start']),instant(e['end'])
    day=next((d for d in b['days'] if d['date']==start.astimezone(ZoneInfo(c['conference']['timezone'])).date().isoformat()),None)
    if not day or start<clock(c,day['date'],day['start']) or end>clock(c,day['date'],day['end']):
        return 'Outside attendance window'
    for block in b.get('breaks',[]):
        if start<clock(c,block['date'],block['end']) and end>clock(c,block['date'],block['start']):
            return 'Overlaps '+block['label']
    return None


def exclusion(c,b,e,rating):
    return feasibility(c,b,e) or ('Below minimum relevance score' if rating['score'] < b.get('minimum_score',3) and e['id'] not in b.get('must_attend',[]) else None)


def compatible(a,b,brief):
    gap=brief['same_room_minutes'] if a['room']==b['room'] else brief['transition_minutes']
    return instant(a['end'])+dt.timedelta(minutes=gap)<=instant(b['start'])


def solve(c,b,decisions):
    catalog_check(c); brief_check(c,b)
    if type(b.get('minimum_score',3)) is not int or not 1<=b.get('minimum_score',3)<=5:
        raise ValueError('Minimum score must be 1..5')
    if decisions['catalog_sha256']!=c['catalog_sha256']: raise ValueError('Decisions belong to another catalog; review changes first')
    if len(decisions.get('review',''))<30: raise ValueError('Missing programme review note')
    events={e['id']:e for e in c['events']}; rated={}
    for d in decisions['decisions']:
        if d['id'] not in events or d['id'] in rated: raise ValueError('Unknown or duplicate decision ID')
        if type(d['score']) is not int or not 1<=d['score']<=5: raise ValueError('Score must be integer 1..5')
        e=events[d['id']]
        if len(d.get('evidence',''))<12 or d['evidence'] not in e['abstract']+'\n'+e['description']:
            raise ValueError('Evidence excerpt does not match session: '+e['title'])
        if len(d.get('why',''))<20 or len(d.get('preparation',''))<20 or len(d.get('questions',[]))<2:
            raise ValueError('Incomplete preparation note')
        rated[d['id']]=d
    required=set(b.get('must_attend',[]))
    if required-set(rated): raise ValueError('Must-attend IDs need grounded decisions')
    chosen=[]
    for day in b['days']:
        eligible=[e for id,e in events.items() if id in rated and not exclusion(c,b,e,rated[id])
                  and instant(e['start']).astimezone(ZoneInfo(c['conference']['timezone'])).date().isoformat()==day['date']]
        eligible.sort(key=lambda e:(e['start'],e['end'],e['id']))
        # DAG dynamic programming with a cardinality cap and room-dependent edges.
        paths={}; best=(0,())
        for j,e in enumerate(eligible):
            weight=rated[e['id']]['score']+(100000 if e['id'] in required else 0)
            paths[(j,1)]=(weight,(j,))
            for k in range(2,b['max_sessions_per_day']+1):
                options=[(paths[(i,k-1)][0]+weight, paths[(i,k-1)][1]+(j,))
                         for i in range(j) if (i,k-1) in paths and compatible(eligible[i],e,b)]
                if options: paths[(j,k)]=max(options,key=lambda x:(x[0],tuple(-v for v in x[1])))
            for k in range(1,b['max_sessions_per_day']+1):
                candidate=paths.get((j,k))
                if candidate and candidate[0]>best[0]: best=candidate
        chosen.extend(eligible[j]['id'] for j in best[1])
    missing=required-set(chosen)
    if missing: raise ValueError('Mandatory sessions cannot all fit: '+', '.join(events[id]['title'] for id in sorted(missing)))
    alternatives=[]
    for id,d in rated.items():
        if id in chosen: continue
        e=events[id]; reason=exclusion(c,b,e,d)
        conflicts=[x for x in chosen if not (compatible(events[x],e,b) or compatible(e,events[x],b))]
        if not reason:
            reason='Time / room-change conflict' if conflicts else 'Lower total priority under session cap'
        alternatives.append({'id':id,'reason':reason,'conflicts_with':conflicts,'score':d['score']})
    return {'chosen':chosen,'alternatives':sorted(alternatives,key=lambda a:(-a['score'],events[a['id']]['start']))}


def escape_ics(value):
    return str(value).replace('\\','\\\\').replace('\r','').replace('\n','\\n').replace(';','\\;').replace(',','\\,')


def fold(line):
    chunks=[]; current=''
    for char in line:
        if len((current+char).encode('utf-8'))>75:
            chunks.append(current);current=' '
        current+=char
    chunks.append(current)
    return '\r\n'.join(chunks)


def utc_stamp(value):
    return instant(value).astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')


def calendar(c,b,decisions,plan):
    events={e['id']:e for e in c['events']}; notes={d['id']:d for d in decisions['decisions']}
    rows=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//Conference Desk//EN','CALSCALE:GREGORIAN']
    now=dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')
    for id in plan['chosen']:
        e=events[id];d=notes[id]
        uid=hashlib.sha256((c['conference']['id']+'/'+id).encode()).hexdigest()+'@conference-desk.local'
        description=d['why']+'\n\nQuestions:\n'+'\n'.join(d['questions'])+'\n\n'+e['url']
        rows+=['BEGIN:VEVENT','UID:'+uid,'DTSTAMP:'+now,'DTSTART:'+utc_stamp(e['start']),
               'DTEND:'+utc_stamp(e['end']),'SUMMARY:'+escape_ics(e['title']),
               'LOCATION:'+escape_ics(e['room']),'DESCRIPTION:'+escape_ics(description),
               'URL:'+e['url'],'END:VEVENT']
    rows+=['END:VCALENDAR']
    return ('\r\n'.join(fold(row) for row in rows)+'\r\n').encode('utf-8')


def render(c,b,d,p):
    events={e['id']:e for e in c['events']}; notes={n['id']:n for n in d['decisions']}
    tz=ZoneInfo(b['display_timezone']);conf_tz=ZoneInfo(c['conference']['timezone']);esc=html.escape
    time=lambda e: instant(e['start']).astimezone(tz).strftime('%a %d %b · %H:%M')+'–'+instant(e['end']).astimezone(tz).strftime('%H:%M')
    h=[f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(c["conference"]["title"])} · Conference Desk</title>',
       '''<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#080f1a;color:#f1f5ff;font:17px/1.6 system-ui,sans-serif}main{max-width:1040px;margin:auto;padding:52px 24px}h1{font-size:clamp(30px,6vw,52px);line-height:1.1;margin:12px 0 24px}h2{margin-top:40px}h3{font-size:23px;line-height:1.3;margin:12px 0}p{max-width:80ch}a{color:#76a9ff;overflow-wrap:anywhere}.eyebrow,.time{color:#2dddc5;font-weight:700}.muted,small{color:#a4b5cc}.cards{display:grid;grid-template-columns:1fr 1fr;gap:20px}article,.panel{padding:24px;border:1px solid #24344a;background:#101d2e;border-radius:16px;break-inside:avoid}.tag{display:inline-block;border:1px solid #355168;padding:3px 10px;border-radius:30px;font-size:13px;color:#a4b5cc}li{margin:8px 0}details{border-bottom:1px solid #24344a;padding:18px 0}summary{cursor:pointer;font-weight:650}textarea{width:100%;min-height:90px;border:1px solid #355168;background:#080f1a;color:#f1f5ff;padding:12px;font:inherit}nav{display:flex;gap:20px;flex-wrap:wrap}@media(max-width:680px){main{padding:28px 18px}.cards{grid-template-columns:1fr}article{padding:20px}}@media print{:root{color-scheme:light}body{background:white;color:#111;font-size:11pt}main{padding:0}.cards{display:block}article,.panel{background:white;border-color:#aaa;margin:12px 0}a{color:#123}textarea{background:white}nav{display:none}.muted,small{color:#444}details{display:block}}</style>''',
       f'<main><div class="eyebrow">CONFERENCE DESK · PERSONAL PREPARATION PACK</div><h1>{esc(c["conference"]["title"])}</h1><p>{esc(b["goal"])}</p>',
       f'<nav><a href="agenda.ics">Calendar file</a><a href="agenda.md">Markdown notes</a><a href="{esc(c["conference"]["base_url"],quote=True)}">Official programme</a></nav>',
       f'<p class="muted">Display: {esc(b["display_timezone"])}. Conference: {esc(c["conference"]["timezone"])}. Source retrieved {esc(c["source"]["fetched_at"][:10])}. {len(c["events"])} programme entries; {len(d["decisions"])} sessions assessed in detail.</p>',
       f'<section class="panel"><b>Preferences and limits</b><p>{esc(b.get("assumptions",""))}</p><p>At most {b["max_sessions_per_day"]} sessions/day. Room changes: {b["transition_minutes"]} min; same room: {b["same_room_minutes"]} min. These are planning allowances, not verified walking routes or seat guarantees.</p>']
    md=[f'# {c["conference"]["title"]} · personal preparation pack','',b['goal'],'',f'Display timezone: {b["display_timezone"]}. Conference timezone: {c["conference"]["timezone"]}.',b.get('assumptions',''),'','## Attendance and protected time','']
    for day in b['days']:
        text=f'{day["date"]}: {day["start"]}–{day["end"]} ({c["conference"]["timezone"]})'
        h.append('<p>'+esc(text)+'</p>');md.append('- '+text)
    for block in b.get('breaks',[]):
        text=f'{block["label"]}: {block["date"]} {block["start"]}–{block["end"]} ({c["conference"]["timezone"]})'
        h.append('<p>'+esc(text)+'</p>');md.append('- '+text)
    h.append('</section><h2>At a glance</h2><section class="panel">')
    for id in p['chosen']:
        e=events[id]
        h.append(f'<p><span class="time">{esc(time(e))}</span><br><a href="#s-{esc(id,quote=True)}">{esc(e["title"])}</a><br><small>{esc(e["room"])}</small></p>')
    h.append('</section><h2>Session preparation</h2><div class="cards">');md+=['','## Your agenda','']
    for id in p['chosen']:
        e=events[id];n=notes[id]
        h.append(f'<article id="s-{esc(id,quote=True)}"><div class="time">{esc(time(e))}</div><h3>{esc(e["title"])}</h3><span class="tag">{esc(e["room"])}</span> <span class="tag">Priority {n["score"]}/5</span><p class="muted">{esc(", ".join(e["speakers"]))} · {esc(e["track"])}</p><p>{esc(n["why"])}</p><b>Questions to take in</b><ul>'+''.join('<li>'+esc(q)+'</li>' for q in n['questions'])+f'</ul><p><b>Prepare:</b> {esc(n["preparation"])}</p><details><summary>Programme evidence and links</summary><p>{esc(n["evidence"])}</p><a href="{esc(e["url"],quote=True)}">Official session</a><ul>'+''.join(f'<li><a href="{esc(l["url"],quote=True)}">{esc(l["label"])}</a></li>' for l in e['links'])+'</ul></details><p><b>Notes</b> · use Markdown for durable notes</p><textarea aria-label="Session notes" placeholder="Scratchpad only: copy before closing; text is not saved"></textarea></article>')
        md += [f'### {time(e)} | {e["title"]}',f'{e["room"]} · {e["track"]} · {", ".join(e["speakers"])}',f'[Official session]({e["url"]})','',n['why'],'','Questions:']+['- '+q for q in n['questions']]+['','Prepare: '+n['preparation'],'','Programme evidence: '+n['evidence'],'','Notes:','', '']
    h.append('</div><h2>Alternatives and tradeoffs</h2><p class="muted">These are alternatives, not guaranteed drop-in replacements. Check the displayed conflicts before swapping.</p>');md+=['## Alternatives and tradeoffs','']
    for a in p['alternatives']:
        e=events[a['id']];n=notes[a['id']];conflicts=', '.join(events[x]['title'] for x in a['conflicts_with'])
        text=a['reason']+('. Conflicts with: '+conflicts if conflicts else '')
        h.append(f'<details><summary>{esc(time(e))} · {esc(e["title"])} · {n["score"]}/5</summary><p>{esc(text)}</p><p>{esc(n["why"])}</p><p>{esc(n["preparation"])}</p><ul>'+''.join('<li>'+esc(q)+'</li>' for q in n['questions'])+f'</ul><p><a href="{esc(e["url"],quote=True)}">Official session</a> · {esc(e["room"])}</p></details>')
        md += [f'- [{e["title"]}]({e["url"]}) · {time(e)} · {e["room"]} · {n["score"]}/5',f'  {text}. {n["why"]}']
    tail='Review the subjective choices and the live official programme before attending. Room availability, accessibility and actual travel times are not verified. This is a snapshot, not a live calendar subscription. Importing ICS is optional; repeated imports may duplicate events. HTML scratchpad notes are not saved.'
    h += ['<h2>Review and remaining work</h2><p>'+esc(d['review'])+'</p><p>'+esc(tail)+'</p><p class="muted">Programme facts and excerpts belong to the named conference and speakers; see ATTRIBUTION.md in the project. Questions, reasons and preparation notes are agent-authored suggestions, not speaker claims.</p></main></html>']
    md+=['','## Review and remaining work','',d['review'],'',tail]
    return '\n'.join(h), '\n'.join(md)+'\n'


def build(c,b,d,out):
    p=solve(c,b,d)
    if not p['chosen']: raise ValueError('No sessions fit; revise preferences or relevance review')
    out=Path(out)
    if out.exists(): raise ValueError('Output exists; choose a new directory to preserve the previous pack')
    out.mkdir(parents=True)
    for name,obj in [('catalog.json',c),('brief.json',b),('decisions.json',d),('plan.json',p)]: dump(out/name,obj)
    page,md=render(c,b,d,p)
    (out/'index.html').write_text(page,encoding='utf-8');(out/'agenda.md').write_text(md,encoding='utf-8')
    (out/'agenda.ics').write_bytes(calendar(c,b,d,p))
    (out/'ATTRIBUTION.md').write_text(c.get('attribution', 'Programme content belongs to the conference and named speakers. Consult the source for its license: '+c['conference']['base_url'])+'\n\nProgramme facts and excerpts have been normalized from the source export. Relevance notes, questions and layout are newly generated; they are not endorsed by the conference or speakers.\n',encoding='utf-8')
    files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}
    dump(out/'manifest.json',{'files':files,'created_at':dt.datetime.now(UTC).isoformat()})
    verify(out)


def verify(out):
    out=Path(out);manifest=load(out/'manifest.json')
    for name,sha in manifest['files'].items():
        if Path(name).name!=name: raise ValueError('Invalid manifest filename')
        if hashlib.sha256((out/name).read_bytes()).hexdigest()!=sha: raise ValueError('Changed file: '+name)
    c=load(out/'catalog.json');b=load(out/'brief.json');d=load(out/'decisions.json');p=load(out/'plan.json')
    if solve(c,b,d)!=p: raise ValueError('Plan no longer matches inputs')
    ics=(out/'agenda.ics').read_bytes()
    if any(len(line)>75 for line in ics.split(b'\r\n')): raise ValueError('ICS line exceeds 75 octets')
    unfolded=ics.decode().replace('\r\n ','')
    blocks=unfolded.split('BEGIN:VEVENT\r\n')[1:]
    events={e['id']:e for e in c['events']}
    if len(blocks)!=len(p['chosen']): raise ValueError('ICS entry count mismatch')
    for id,block in zip(p['chosen'],blocks):
        e=events[id]
        for line in ['DTSTART:'+utc_stamp(e['start']),'DTEND:'+utc_stamp(e['end']), 'SUMMARY:'+escape_ics(e['title']), 'URL:'+e['url']]:
            if line+'\r\n' not in block: raise ValueError('ICS mismatch: '+line)
    print(json.dumps({'verified':True,'chosen':len(p['chosen']),'alternatives':len(p['alternatives']),'directory':str(out)}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='cmd',required=True)
    q=sub.add_parser('ingest');q.add_argument('--source',required=True);q.add_argument('--out',required=True)
    for cmd in ['index','read']:
        q=sub.add_parser(cmd);q.add_argument('--catalog',required=True)
        q.add_argument('--tracks',nargs='+')
        if cmd=='read':q.add_argument('--ids',nargs='+')
    q=sub.add_parser('build')
    for key in ['catalog','brief','decisions','out']: q.add_argument('--'+key,required=True)
    q=sub.add_parser('verify');q.add_argument('--out',required=True)
    q=sub.add_parser('changes');q.add_argument('--before',required=True);q.add_argument('--after',required=True)
    args=parser.parse_args()
    if args.cmd=='ingest':ingest(args.source,args.out)
    elif args.cmd=='verify':verify(args.out)
    elif args.cmd=='build':build(load(args.catalog),load(args.brief),load(args.decisions),args.out)
    elif args.cmd=='changes':
        a=catalog_check(load(args.before));b=catalog_check(load(args.after))
        x={e['id']:e for e in a['events']};y={e['id']:e for e in b['events']}
        dump_data={'added':[y[id] for id in sorted(y.keys()-x.keys())],'removed':[x[id] for id in sorted(x.keys()-y.keys())],
            'changed':[{'id':id,'title':y[id]['title'],'fields':[k for k in y[id] if x[id].get(k)!=y[id][k]]} for id in sorted(x.keys()&y.keys()) if x[id]!=y[id]]}
        print(json.dumps(dump_data,ensure_ascii=False,indent=2))
    else:
        c=catalog_check(load(args.catalog))
        print(json.dumps({'conference':c['conference'],'events':len(c['events']),'catalog_sha256':c['catalog_sha256']},ensure_ascii=False))
        if args.cmd=='index':
            from collections import Counter
            print(json.dumps({'tracks':dict(sorted(Counter(e['track'] for e in c['events']).items()))},ensure_ascii=False))
        for e in c['events']:
            if args.cmd=='read':
                if not args.ids and not args.tracks: raise ValueError('Choose --ids or --tracks')
                if e['id'] not in (args.ids or []) and e['track'] not in (args.tracks or []): continue
                print(json.dumps(e,ensure_ascii=False))
            else:
                if args.tracks and e['track'] not in args.tracks: continue
                print(' | '.join([e['id'],e['start'],e['end'][11:16],e['room'],e['track'],e['title']]))


if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,ET.ParseError,OSError) as error:
        print('ERROR: '+str(error),file=sys.stderr);sys.exit(1)
