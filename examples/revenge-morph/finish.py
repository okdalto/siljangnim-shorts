"""Build the approved opening and tighten remaining promo narration from originals.
Usage: python examples/revenge-morph/finish.py PROJECT_JSON OUTPUT_FOLDER
Then: node remotion/agent-render.mjs OUTPUT_FOLDER render
"""
import copy, json, math, os, shutil, subprocess, sys, wave
from pathlib import Path
root=Path(__file__).resolve().parents[2]
project=json.loads(Path(sys.argv[1]).read_text()); out=Path(sys.argv[2]).resolve()
original=out/'original'; (original/'public').mkdir(parents=True,exist_ok=True)
for s in project['speech']:
 shutil.copy(s['audio'],original/'public'/f"{s['id']}.wav")
for name in ['font.otf','logo.svg']:
 shutil.copy(root/'agent-projects'/project['id']/project['delivery']['folder']/'public'/name,original/'public'/name)
(original/'timeline.json').write_text(json.dumps(project['speech'][:2]))
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-opening.py')),str(original),str(out)],check=True)
plan=json.loads((out/'timeline.json').read_text())
# Silence interiors measured with ffmpeg -38dB; preserve consonants and breaths.
cuts_by_id={'production':[(1.34,18),(3.30,18),(6.65,25),(8.20,18)],
 'edit':[(1.66,32)],'proof':[(2.39,25),(3.90,38)],'brand':[(2.37,12)]}
for raw in project['speech'][2:]:
 s=copy.deepcopy(raw); cuts=[(a,a+n/60) for a,n in cuts_by_id[s['id']]]
 with wave.open(raw['audio'],'rb') as wav:
  params=wav.getparams(); data=wav.readframes(params.nframes)
 stride=params.nchannels*params.sampwidth; chunks=[]; cursor=0
 for a,b in cuts:
  left=round(a*params.framerate)*stride;right=round(b*params.framerate)*stride
  chunks.append(data[cursor:left]);cursor=right
 chunks.append(data[cursor:])
 with wave.open(str(out/'public'/f"{s['id']}.wav"),'wb') as wav:
  wav.setparams(params);wav.writeframes(b''.join(chunks))
 def shifted(t):return t-sum(max(0,min(t,b)-a) for a,b in cuts)
 for c in s['captions']:
  for k in ['start','end']:c[k]=shifted(c[k]-.25)+.25
  for w in c['words']:
   for k in ['start','end']:w[k]=shifted(w[k])
 duration=(len(b''.join(chunks))/stride)/params.framerate
 # A short ending breath plus 0.25 s narration lead-in; no long scene holds.
 s['frames']=math.ceil((duration+.35)*60)
 s['audio']=str(out/'public'/f"{s['id']}.wav")
 plan.append(s)
(out/'timeline.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
shutil.copy(Path(__file__).with_name('opening.tsx'),out/'opening.tsx')
shutil.copy(Path(__file__).with_name('final.tsx'),out/'design.tsx')
for s in plan:
 if s['id'] not in ['production','edit','proof']:continue
 timeline=out/f"{s['id']}.json";timeline.write_text(json.dumps(s))
 env={**os.environ,'SHORTS_GEOMETRY_TIMELINE':str(timeline)}
 with (out/f"{s['id']}.log").open('w') as log:
  subprocess.run([str(root/'motion/.venv/bin/python'),'-m','manim','render',str(root/'examples/revenge-morph/motion.py'),'Promo','--resolution','1080,1920','--fps','60','--disable_caching','--media_dir',str(out/'geometry'/s['id']),'-o',s['id']],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 clip=out/'geometry'/s['id']/'videos/motion/1920p60'/f"{s['id']}.mp4"
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(clip)]))['streams'][0]
 if abs(float(info['duration'])-s['frames']/60)>.1:raise RuntimeError(f"Scene timing overrun: {s['id']}")
 shutil.copy(clip,out/'public'/f"{s['id']}.mp4")
 print('Geometry ready:',s['id'],flush=True)
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
for lang in ['en','ko']:
 lines=[];offset=0
 for s in plan:
  for c in s['captions']:
   lines.append(f"{len(lines)+1}\n{stamp(offset+c['start'])} --> {stamp(offset+min(c['end'],s['frames']/60))}\n{c[lang]}\n")
  offset+=s['frames']/60
 (out/f'subtitles.{lang}.srt').write_text('\n'.join(lines))
print('Final duration:',sum(s['frames'] for s in plan)/60,flush=True)
