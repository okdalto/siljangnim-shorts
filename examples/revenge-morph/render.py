import os,subprocess
from pathlib import Path
import argparse, json
parser=argparse.ArgumentParser(description='Render the five promo Manim scenes from a prepared project.')
parser.add_argument('project',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
folder=root/'.cache/morph';folder.mkdir(parents=True,exist_ok=True)
project=json.loads(args.project.read_text())
for shot in project['speech']:
 if shot['id']!='brand':(folder/(shot['id']+'.json')).write_text(json.dumps(shot))
for name in ['flood','revenge','production','edit','proof']:
 env={**os.environ,'SHORTS_GEOMETRY_TIMELINE':str(root/'.cache/morph'/f'{name}.json')}
 with (root/'.cache/morph'/f'{name}.log').open('w') as log:
  subprocess.run([str(root/'motion/.venv/bin/python'),'-m','manim','render',str(root/'examples/revenge-morph/motion.py'),'Promo','--resolution','1080,1920','--fps','60','--disable_caching','--media_dir',str(root/'.cache/morph'/name),'-o',name],env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
 print(name,flush=True)
