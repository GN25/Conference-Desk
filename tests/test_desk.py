import copy
import importlib.util
import itertools
from pathlib import Path
import random
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('desk',Path(__file__).resolve().parents[1]/'conference-desk/scripts/desk.py')
desk=importlib.util.module_from_spec(spec);spec.loader.exec_module(desk)
ROOT=Path(__file__).resolve().parents[1]

class SchedulingTests(unittest.TestCase):
    def inputs(self,year=2026):
        p=ROOT/'examples'/f'fosdem-{year}'
        return [desk.load(p/(name+'.json')) for name in ('catalog','brief','decisions')]

    def test_real_packs_and_constraints(self):
        for year,count in [(2026,6),(2025,8)]:
            c,b,d=self.inputs(year);p=desk.solve(c,b,d);events={e['id']:e for e in c['events']}
            self.assertEqual(len(p['chosen']),count)
            self.assertTrue(set(b['must_attend'])<=set(p['chosen']))
            for id in p['chosen']: self.assertIsNone(desk.feasibility(c,b,events[id]))
            for a,z in zip(p['chosen'],p['chosen'][1:]):self.assertTrue(desk.compatible(events[a],events[z],b))
            desk.verify(ROOT/'examples'/f'fosdem-{year}'/'pack')

    def test_conflicting_mandatory_sessions_refused(self):
        c,b,d=self.inputs(2025)
        b['must_attend'] += [e['id'] for e in c['events'] if e['title']=='Tuning Postgres for Analytics']
        with self.assertRaisesRegex(ValueError,'Mandatory'): desk.solve(c,b,d)

    def test_stale_decisions_and_unmatched_evidence_refused(self):
        c,b,d=self.inputs();d['catalog_sha256']='old'
        with self.assertRaisesRegex(ValueError,'another catalog'):desk.solve(c,b,d)
        d['catalog_sha256']=c['catalog_sha256'];d['decisions'][0]['evidence']='Fabricated evidence from an unseen talk'
        with self.assertRaisesRegex(ValueError,'Evidence'):desk.solve(c,b,d)

    def test_optimizer_against_exhaustive_search(self):
        c,b,d=self.inputs();rng=random.Random(221)
        for trial in range(20):
            c=copy.deepcopy(c);b=copy.deepcopy(b);d=copy.deepcopy(d)
            ids=[n['id'] for n in d['decisions']];rng.shuffle(ids);ids=ids[:8]
            c['events']=[e for e in c['events'] if e['id'] in ids]
            c.pop('catalog_sha256');c['catalog_sha256']=desk.digest(c)
            d['catalog_sha256']=c['catalog_sha256'];d['decisions']=[n for n in d['decisions'] if n['id'] in ids]
            for n in d['decisions']:n['score']=rng.randint(1,5)
            b['must_attend']=[];b['max_sessions_per_day']=rng.randint(1,5)
            eligible=sorted([e for e in c['events'] if not desk.exclusion(c,b,e,next(n for n in d['decisions'] if n['id']==e['id']))],key=lambda e:e['start'])
            scores={n['id']:n['score'] for n in d['decisions']};best=0
            for count in range(1,b['max_sessions_per_day']+1):
                for selected in itertools.combinations(eligible,count):
                    if all(desk.compatible(a,z,b) for a,z in zip(selected,selected[1:])):
                        best=max(best,sum(scores[e['id']] for e in selected))
            plan=desk.solve(c,b,d)
            self.assertEqual(sum(scores[id] for id in plan['chosen']),best)

    def test_ics_unicode_folding_and_exact_instants(self):
        line='SUMMARY:'+('é界;comma, slash\\ '*30)
        folded=desk.fold(line)
        self.assertTrue(all(len(row.encode())<=75 for row in folded.split('\r\n')))
        self.assertEqual(folded.replace('\r\n ',''),line)
        self.assertEqual(desk.utc_stamp('2026-03-29T03:30:00+02:00'),'20260329T013000Z')
        self.assertEqual(desk.utc_stamp('2026-10-25T02:30:00+01:00'),'20261025T013000Z')
        self.assertEqual(desk.escape_ics('a,b;c\nd\\e'),'a\\,b\\;c\\nd\\\\e')

    def test_changed_output_detected_and_existing_folder_preserved(self):
        c,b,d=self.inputs()
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'pack';desk.build(c,b,d,target)
            with self.assertRaisesRegex(ValueError,'Output exists'):desk.build(c,b,d,target)
            (target/'agenda.ics').write_text('changed')
            with self.assertRaisesRegex(ValueError,'Changed file'):desk.verify(target)

    def test_xml_entity_input_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'bad.xml';p.write_text('<!DOCTYPE foo [<!ENTITY a "b">]><schedule/>')
            with self.assertRaisesRegex(ValueError,'entity'):desk.ingest(str(p),Path(temp)/'out.json')

if __name__=='__main__':unittest.main()
