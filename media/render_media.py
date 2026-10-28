"""Render readable image excerpts of the actual completed example (Pillow authoring only)."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'media'
c=json.loads((ROOT/'examples/fosdem-2026/pack/catalog.json').read_text());p=json.loads((ROOT/'examples/fosdem-2026/pack/plan.json').read_text());d=json.loads((ROOT/'examples/fosdem-2026/pack/decisions.json').read_text())
events={e['id']:e for e in c['events']};notes={n['id']:n for n in d['decisions']}
BG='#080F1A';PANEL='#101D2E';TEXT='#F1F5FF';MUTED='#A4B5CC';MINT='#2DDDC5';CORAL='#FF617D';BLUE='#76A9FF'
fontpath='/System/Library/Fonts/Supplemental/Arial.ttf';boldpath='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(size,bold=False):return ImageFont.truetype(boldpath if bold else fontpath,size)
def canvas(label):
 im=Image.new('RGB',(1080,1350),BG);dr=ImageDraw.Draw(im)
 dr.text((64,48),'CONFERENCE DESK',fill=MINT,font=font(24,True));dr.text((64,86),label,fill=MUTED,font=font(21))
 return im,dr

def text(dr,words,xy,width,size=28,color=TEXT,bold=False,spacing=8):
 x,y=xy;f=font(size,bold)
 for para in words.split('\n'):
  line=''
  for word in para.split():
   candidate=(line+' '+word).strip()
   if dr.textlength(candidate,font=f)>width and line:
    dr.text((x,y),line,font=f,fill=color);y+=size+spacing;line=word
   else:line=candidate
  if line:dr.text((x,y),line,font=f,fill=color);y+=size+spacing
 return y

def panel(dr,box):dr.rounded_rectangle(box,22,fill=PANEL,outline='#24344A',width=2)

im,dr=canvas('ACTUAL OUTPUT EXCERPTS · HISTORICAL FOSDEM 2026')
y=text(dr,'A programme is not\na prepared visit.',(64,145),950,60,bold=True,spacing=3)
panel(dr,(64,305,1016,487));dr.text((90,328),'INVOKE $conference-desk WITH:',font=font(20,True),fill=MINT)
text(dr,'Operate self-hosted LLMs. Saturday visit.\nKeep lunch and one required session.\nReturn an agenda, questions, notes and ICS.',(90,367),895,28,spacing=5)
dr.text((64,520),'1,079 entries parsed   /   15 assessed   /   6 chosen',font=font(28,True),fill=MINT)
panel(dr,(64,583,1016,1134));dr.text((90,607),'FINISHED AGENDA · EUROPE/BRUSSELS',font=font(22,True),fill=MUTED)
labels=['API Remoting for llama.cpp','One GPU, Many Models','Supercharging LLM serving with Dynamo','Taming the LLM Zoo with Docker Model Runner','From Infrastructure to Production','AI Security Monitoring']
y=661
for id,label in zip(p['chosen'],labels):
 e=events[id];dr.text((90,y),e['start'][11:16],font=font(28,True),fill=MINT)
 y2=text(dr,label,(197,y),770,28,bold=True,spacing=4)
 dr.text((197,y2+1),e['room'],font=font(23),fill=MUTED);y=max(y+72,y2+34)
text(dr,'Delivered: offline HTML + Markdown notes + calendar file.\nNine alternatives explain the sessions left out.',(64,1170),950,28,spacing=8)
dr.text((64,1304),'Synthetic attendee brief. Session labels shortened. No attendance claim.',font=font(20),fill=MUTED)
im.save(OUT/'01_agenda.png')

im,dr=canvas('ACTUAL PREPARATION NOTES · SOURCE-LINKED QUESTIONS')
text(dr,'Decisions ready.\nQuestions ready.',(64,145),950,62,bold=True,spacing=4)
id=next(id for id in p['chosen'] if events[id]['title'].startswith('One GPU,'));e=events[id];n=notes[id]
panel(dr,(64,320,1016,836))
dr.text((90,345),'13:55–14:15 · UD2.120 · PRIORITY 5/5',font=font(23,True),fill=MINT)
y=text(dr,e['title'],(90,397),890,38,bold=True,spacing=5)
y=text(dr,n['why'],(90,y+18),890,27,spacing=7)
dr.text((90,y+18),'QUESTIONS TO TAKE IN',font=font(20,True),fill=MUTED);y+=63
for q in n['questions']:
 y=text(dr,'• '+q,(90,y),880,29,spacing=6)+15
panel(dr,(64,873,1016,1139));dr.text((90,898),'AN EXPLICIT TRADEOFF',font=font(22,True),fill=CORAL)
y=text(dr,'Island sandboxing: 15:30–15:55\nDynamo serving: 15:40–16:00',(90,945),880,29,bold=True,spacing=6)
text(dr,'The sessions overlap. The pack keeps the higher-priority serving talk and retains the sandboxing questions as an alternative.',(90,y+14),880,27,spacing=6)
text(dr,'Another brief, same workflow: the 2025 example delivers\neight sessions across two days, with ten alternatives.',(64,1172),950,27,spacing=8)
dr.text((64,1304),'Review choices and live schedule. Routes and available seats are not verified.',font=font(20),fill=MUTED)
im.save(OUT/'02_preparation.png')
print('Rendered two 1080 × 1350 actual-output image excerpts')
