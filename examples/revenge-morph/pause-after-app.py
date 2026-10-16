"""Add 0.5 seconds after No separate app, preserving all other timing.
Usage: python pause-after-app.py SOURCE_FOLDER NEW_OUTPUT_FOLDER
"""
import json,re,shutil,subprocess,sys
from pathlib import Path
src,out=map(Path,sys.argv[1:]);out.mkdir(parents=True,exist_ok=False)
cut=1424/60;hold=.5
filters=f'[0:v]split[v0][v1];[v0]trim=end_frame=1424,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={hold}[pre];[v1]trim=start_frame=1424,setpts=PTS-STARTPTS[post];[0:a]asplit[a0][a1];[a0]atrim=end={cut},asetpts=PTS-STARTPTS,apad=pad_dur={hold}[apre];[a1]atrim=start={cut},asetpts=PTS-STARTPTS[apost];[pre][apre][post][apost]concat=n=2:v=1:a=1[v][a]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'film.mp4'),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'film.mp4')],check=True)
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out/'film.mp4'),'-vf','scale=720:1280','-r','30','-c:v','libx264','-crf','21','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'preview.mp4')],check=True)
shutil.copy(src/'thumbnail.png',out/'thumbnail.png')
captions=json.loads((src/'captions.json').read_text())
for c in captions:
 if c['start']>=cut:
  c['start']+=hold;c['end']+=hold
 elif 'No separate app.' in c['en']:c['end']=cut+hold
(out/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2))
(out/'edit-decisions.json').write_text(json.dumps({'source':str(src.resolve()),'insert_silence_and_hold_at_frame':1424,'added_frames':30},indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for lang in ['en','ko']:
 (out/f'subtitles.{lang}.srt').write_text('\n'.join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c[lang]}\n" for i,c in enumerate(captions)))
