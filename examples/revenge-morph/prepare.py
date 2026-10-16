"""Import rendered geometry and write the composition; preserve existing speech."""
import argparse,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('id');args=p.parse_args()
def call(*args):return json.loads(subprocess.check_output([str(root/'shorts'),*args],cwd=root))
state=call('status',args.id);clips={}
for shot in state['speech']:
 name=shot['id']
 if name=='brand':continue
 file=root/'.cache/morph'/name/'videos/motion/1920p60'/f'{name}.mp4'
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(file)]))['streams'][0]
 assert (info['width'],info['height'],info['r_frame_rate'])==(1080,1920,'60/1')
 assert abs(float(info['duration'])-shot['frames']/60)<.1
 result=call('asset',args.id,'--revision',str(state['revision']),'--file',str(file));state=result['project'];clips[name]=result['static_file']
source=(root/'examples/revenge-morph/composition.tsx').read_text().replace('__CLIPS__',json.dumps(clips))
target=root/'.cache/morph/visual.tsx';target.write_text(source)
state=call('design',args.id,'--revision',str(state['revision']),'--file',str(target))
print(json.dumps({'id':state['id'],'revision':state['revision'],'clips':clips},indent=2))
