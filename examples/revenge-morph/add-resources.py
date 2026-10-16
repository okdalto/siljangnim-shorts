"""Insert cached resource satire into the approved complete promo.
Usage: python add-resources.py SOURCE_FOLDER RESOURCE_SPEECH_JSON NEW_OUTPUT_FOLDER
The resource speech JSON uses the normal Media.voice/align contract.
"""
import copy,json,math,os,shutil,subprocess,sys,wave
from pathlib import Path
root=Path(__file__).resolve().parents[2]
src,speech_file,out=map(Path,sys.argv[1:]);src=src.resolve();out=out.resolve()
out.mkdir(parents=True,exist_ok=False)
resources=json.loads(speech_file.read_text());plan=json.loads((src/'timeline.json').read_text())
for name in ['design.tsx','opening.tsx','thumbnail.png']:shutil.copy(src/name,out/name)
shutil.copytree(src/'public',out/'public')
proof=next(s for s in plan if s['id']=='proof');insert=2.4
with wave.open(resources['audio']) as audio:
 params=audio.getparams();data=audio.readframes(params.nframes)
stride=params.nchannels*params.sampwidth;rate=params.framerate
# Tighten only the verified silence between the new sentences.
data=data[:round(1.2*rate)*stride]+data[round(1.5*rate)*stride:]
length=len(data)//stride;added_frames=math.ceil(length/rate*60);added=added_frames/60
padded_frames=round(added*rate)
data+=bytes((padded_frames-length)*stride)
with wave.open(str(src/'public/proof.wav')) as audio:
 assert audio.getnchannels()==params.nchannels and audio.getframerate()==rate
 original=audio.readframes(audio.getnframes())
point=round(insert*rate)*stride
with wave.open(str(out/'public/proof.wav'),'wb') as audio:
 audio.setparams(params);audio.writeframes(original[:point]+data+original[point:])
new_cues=copy.deepcopy(resources['captions'])
def shortened(t):return t-max(0,min(t,1.5)-1.2)
for c in new_cues:
 for k in ['start','end']:c[k]=insert+shortened(c[k]-.25)+.25
 for w in c['words']:
  for k in ['start','end']:w[k]=insert+shortened(w[k])
for c in proof['captions'][1:]:
 for k in ['start','end']:c[k]+=added
 for w in c['words']:
  for k in ['start','end']:w[k]+=added
proof['captions'][1:1]=new_cues;proof['frames']+=added_frames
proof['audio']=str(out/'public/proof.wav')
(out/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(out/'proof.json').write_text(json.dumps(proof))
env={**os.environ,'SHORTS_GEOMETRY_TIMELINE':str(out/'proof.json')}
with (out/'geometry.log').open('w') as log:
 subprocess.run([str(root/'motion/.venv/bin/python'),'-m','manim','render',str(Path(__file__).with_name('resource-motion.py')),'ResourcePromo','--resolution','1080,1920','--fps','60','--disable_caching','--media_dir',str(out/'geometry'),'-o','proof'],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
shutil.copy(out/'geometry/videos/resource-motion/1920p60/proof.mp4',out/'public/proof.mp4')
shot=out/'proof-render';shot.mkdir();shutil.copytree(out/'public',shot/'public')
for name in ['design.tsx','opening.tsx']:shutil.copy(out/name,shot/name)
(shot/'timeline.json').write_text(json.dumps([proof]))
subprocess.run(['node',str(root/'remotion/agent-render.mjs'),str(shot),'render'],check=True)
before=sum(s['frames'] for s in plan[:next(i for i,s in enumerate(plan) if s['id']=='proof')])/60
old_after=before+(proof['frames']-added_frames)/60
filters=f'[0:v]split[v0][v1];[v0]trim=end={before},setpts=PTS-STARTPTS[pre];[v1]trim=start={old_after},setpts=PTS-STARTPTS[post];[0:a]asplit[a0][a1];[a0]atrim=end={before},asetpts=PTS-STARTPTS[apre];[a1]atrim=start={old_after},asetpts=PTS-STARTPTS[apost];[1:v]trim=end={proof["frames"]/60},setpts=PTS-STARTPTS[mid];[1:a]atrim=end={proof["frames"]/60},asetpts=PTS-STARTPTS[amid];[pre][apre][mid][amid][post][apost]concat=n=3:v=1:a=1[v][a]'
subprocess.run(['ffmpeg','-v','error','-y','-i',str(src/'film.mp4'),'-i',str(shot/'film.mp4'),'-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-crf','18','-preset','fast','-c:a','aac','-movflags','+faststart',str(out/'film.mp4')],check=True)
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
print(json.dumps({'seconds':sum(s['frames'] for s in plan)/60,'inserted_seconds':added}))
