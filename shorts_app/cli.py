"""On-demand skill helpers. No server, GUI, or nested agent required."""
import argparse
import json
import os
import time
from pathlib import Path
from .agent_workspace import Workspace


def main():
 parser=argparse.ArgumentParser(description='Siljangnim Shorts skill helpers; the agent directs each stage.')
 sub=parser.add_subparsers(dest='command',required=True)
 p=sub.add_parser('create');p.add_argument('brief')
 for name in ('status','speech','preview','render','design','script','asset','review'):
  p=sub.add_parser(name);p.add_argument('id')
  if name in ('script','design','asset','review'):p.add_argument('--revision',type=int,required=True)
  if name in ('script','design','asset'):p.add_argument('--file',type=Path,required=True)
  if name in ('preview','render'):p.add_argument('--frames',type=int,nargs='*')
  if name=='review':p.add_argument('--notes',required=True);p.add_argument('--pass-visual',action='store_true')
 p=sub.add_parser('view');p.add_argument('--port',type=int,default=4319)
 args=parser.parse_args();w=Workspace(os.environ.get('SHORTS_AGENT_DATA'))
 try:
  if args.command=='status':result=w.read(args.id)
  elif args.command=='view':
   from .agent_viewer import start_viewer
   server=start_viewer(w,args.port);print(f'http://127.0.0.1:{args.port}',flush=True)
   try:
    while True:time.sleep(1)
   except KeyboardInterrupt:server.shutdown()
   return
  else:
   import fcntl
   lock=(w.root/'.lock').open('a')
   try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   except BlockingIOError:parser.error('Another production command owns this workspace. Read status or wait for it to finish.')
   w.recover()
   if args.command=='create':result=w.create(args.brief)
   elif args.command=='script':result=w.script_write(args.id,args.revision,json.loads(args.file.read_text()))
   elif args.command=='design':result=w.design_write(args.id,args.revision,args.file.read_text())
   elif args.command=='asset':result=w.asset_import(args.id,args.revision,str(args.file))
   elif args.command=='review':result=w.review(args.id,args.revision,args.notes,args.pass_visual)
   else:
    w.start(args.id,args.command,getattr(args,'frames',None))
    while w.read(args.id)['job']['status'] in ('queued','running'):time.sleep(.25)
    result=w.read(args.id)
    if result['job']['status']=='failed':raise RuntimeError(result['job']['error'])
  print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
 finally:w.pool.shutdown(wait=True)

if __name__=='__main__':main()
