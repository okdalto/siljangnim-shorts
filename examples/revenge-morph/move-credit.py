"""Move the opening proof sentence after the punchline hold; keep existing media.
Usage: python move-credit.py SOURCE_FOLDER NEW_OUTPUT_FOLDER THUMBNAIL_PNG
The output is an edited delivery with an explicit edit decision list, not a new
agent-root timeline. Rebuild it from the source delivery using this script.
"""
import json,shutil,subprocess,sys
from pathlib import Path
src,out,thumb=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=False)
plan=json.loads((src/'timeline.json').read_text())
proof_index=next(i for i,s in enumerate(plan) if s['id']=='proof')
before=sum(s['frames'] for s in plan[:proof_index])/60
proof=plan[proof_index];split=159/60;after=before+proof['frames']/60
total=sum(s['frames'] for s in plan)/60
segments=[(0,before),(before+split,after),(before,before+split),(after,total)]
(out/'edit-decisions.json').write_text(json.dumps({'source':str(src.resolve()),'segments':segments,'note':'Credit moved after the retained 1-second punchline hold.'},indent=2))
shutil.copy(src/'timeline.json',out/'source-timeline.json')
shutil.copy(thumb,out/'thumbnail.png')
filters=[]
for i,(a,b) in enumerate(segments):
 # The incoming resource beat used to morph from the now-relocated credit ring.
 # Start on its first settled electricity frame; retain timing with a visual hold.
 visual_head = 25/60 if i == 1 else 0
 video = f'[0:v]trim=start_frame={round((a+visual_head)*60)}:end_frame={round(b*60)},setpts=PTS-STARTPTS'
 if visual_head: video += f',tpad=start_mode=clone:start_duration={visual_head}'
 filters.extend([video+f'[v{i}]',f'[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS[a{i}]'])
filters.append(''.join(f'[v{i}][a{i}]' for i in range(4))+'concat=n=4:v=1:a=1[v][a]')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'film.mp4'),'-filter_complex',';'.join(filters),'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'film.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'film.mp4'),'-vf','scale=720:1280','-r','30','-c:v','libx264','-crf','21','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'preview.mp4')],check=True)
captions=[];cursor=0
for s in plan:
 for i,c in enumerate(s['captions']):
  end=s['frames']/60 if s['id']=='proof' and i==len(s['captions'])-1 else c['end']
  captions.append({**c,'start':cursor+c['start'],'end':cursor+end})
 cursor+=s['frames']/60
ordered=[];cursor=0
for a,b in segments:
 for c in captions:
  if a<=c['start']<b:ordered.append({**c,'start':cursor+c['start']-a,'end':cursor+min(c['end'],b)-a})
 cursor+=b-a
(out/'captions.json').write_text(json.dumps(ordered,ensure_ascii=False,indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for lang in ['en','ko']:
 (out/f'subtitles.{lang}.srt').write_text('\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c[lang]}\n" for i,c in enumerate(ordered)))
print('Final seconds:',total)
