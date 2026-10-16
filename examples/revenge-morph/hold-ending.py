"""Add a one-second punchline hold before the brand ending, without rerendering earlier motion.
Usage: python hold-ending.py SOURCE_FOLDER NEW_OUTPUT_FOLDER
"""
import json, math, shutil, subprocess, sys
from pathlib import Path
src,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=False)
plan=json.loads((src/'timeline.json').read_text()); proof=next(s for s in plan if s['id']=='proof')
new_frames=math.ceil((proof['captions'][-1]['end']+1)*60)
added=new_frames-proof['frames'];assert added>0
cut=sum(s['frames'] for s in plan[:next(i for i,s in enumerate(plan) if s['id']=='brand')])/60
hold=added/60
for name in ['design.tsx','opening.tsx','thumbnail.png']:
 shutil.copy(src/name,out/name)
shutil.copytree(src/'public',out/'public')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'public/proof.mp4'),'-vf',f'tpad=stop_mode=clone:stop_duration={hold}','-an','-c:v','libx264','-crf','18',str(out/'public/proof.mp4')],check=True)
proof['frames']=new_frames
(out/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
filters=f'[0:v]split[v0][v1];[v0]trim=end={cut},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={hold}[pre];[v1]trim=start={cut},setpts=PTS-STARTPTS[post];[0:a]asplit[a0][a1];[a0]atrim=end={cut},asetpts=PTS-STARTPTS,apad=pad_dur={hold}[apre];[a1]atrim=start={cut},asetpts=PTS-STARTPTS[apost];[pre][apre][post][apost]concat=n=2:v=1:a=1[v][a]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'film.mp4'),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'film.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'film.mp4'),'-vf','scale=720:1280','-r','30','-c:v','libx264','-crf','21','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'preview.mp4')],check=True)
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for lang in ['en','ko']:
 lines=[];offset=0
 for s in plan:
  for c in s['captions']:
   end=s['frames']/60 if s['id']=='proof' and c==s['captions'][-1] else c['end']
   lines.append(f"{len(lines)+1}\n{stamp(offset+c['start'])} --> {stamp(offset+end)}\n{c[lang]}\n")
  offset+=s['frames']/60
 (out/f'subtitles.{lang}.srt').write_text('\n'.join(lines))
print(json.dumps({'hold_added':hold,'brand_start':cut+hold,'seconds':sum(s['frames'] for s in plan)/60}))
