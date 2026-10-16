"""Agent-owned production. No model calls, planner, or automatic creative decisions."""
import concurrent.futures
import copy
import json
import re
import shutil
import threading
import uuid
from pathlib import Path
from .model import ROOT, digest
from .graphics import wrap
from .media import Media, filehash, probe, run
from .store import save, now, Conflict


def script_check(script):
    if not isinstance(script,dict) or set(script)!={'title','shots'}:raise ValueError('Expected title and shots')
    if not isinstance(script['title'],str) or not 1<=len(script['title'])<=100:raise ValueError('Invalid title')
    if not isinstance(script['shots'],list) or not 1<=len(script['shots'])<=20:raise ValueError('Use 1–20 shots')
    ids=set()
    for shot in script['shots']:
        if set(shot)!={'id','beats'} or not isinstance(shot['id'],str) or not re.fullmatch('[a-z][a-z0-9-]{0,30}',shot['id']) or shot['id']=='brand' or shot['id'] in ids:raise ValueError('Unique safe shot IDs required; brand is reserved')
        ids.add(shot['id'])
        if not isinstance(shot['beats'],list) or not 1<=len(shot['beats'])<=8:raise ValueError('Use 1–8 speech beats per shot')
        for beat in shot['beats']:
            if set(beat)!={'en','ko'}:raise ValueError('Each beat needs en and ko')
            for lang,size in [('en',46),('ko',54)]:
                if not isinstance(beat[lang],str) or not beat[lang].strip() or len(beat[lang])>160 or len(wrap(beat[lang],size,792))>2:raise ValueError(f'Shorten {shot["id"]} {lang} to two caption lines')
    return script


class Workspace:
    def __init__(self,root=None,media=None):
        self.root=Path(root or ROOT/'agent-projects');self.root.mkdir(parents=True,exist_ok=True)
        self.media=media or Media();self.lock=threading.RLock()
        self.pool=concurrent.futures.ThreadPoolExecutor(max_workers=1)

    def recover(self):
        for path in self.root.glob('*/project.json'):
            p=json.loads(path.read_text())
            if p.get('job',{}).get('status') in ('queued','running'):
                p['job']['status']='interrupted';p['job']['error']='Production process stopped. Call the stage again; cached speech is preserved.';save(path,p)

    def folder(self,id):
        if not re.fullmatch('[a-f0-9]{12}',id):raise ValueError('Invalid project ID')
        return self.root/id

    def read(self,id):return json.loads((self.folder(id)/'project.json').read_text())
    def list(self):return [json.loads(p.read_text()) for p in sorted(self.root.glob('*/project.json'))]
    def put(self,p):p['updated']=now();save(self.folder(p['id'])/'project.json',p);return p

    def create(self,brief):
        if not isinstance(brief,str) or not 1<=len(brief)<=4000:raise ValueError('Brief: 1–4000 characters')
        p={'id':uuid.uuid4().hex[:12],'brief':brief,'revision':0,'title':brief[:80],'script':None,'design':None,'assets':{},'speech':None,'preview':None,'delivery':None,'review':None,'job':{},'created':now()}
        return self.put(p)

    def editable(self,id,revision):
        p=self.read(id)
        if p['revision']!=revision:raise Conflict('Revision changed; read the current project first')
        if p.get('job',{}).get('status') in ('queued','running'):raise Conflict('Wait for the current stage before editing')
        return p

    def revise(self,p):
        p['revision']+=1;p['preview']=None;p['delivery']=None;p['review']=None
        save(self.folder(p['id'])/'history'/f'{p["revision"]:04}.json',p)
        return self.put(p)

    def script_write(self,id,revision,script):
        script_check(script)
        with self.lock:
            p=self.editable(id,revision);p['script']=copy.deepcopy(script);p['title']=script['title']
            # Alignment can be reused by the media cache, but returned cues must reflect edits.
            p['speech']=None
            return self.revise(p)

    def design_write(self,id,revision,source):
        if not isinstance(source,str) or not 1<=len(source)<=150000:raise ValueError('Design source: 1–150000 characters')
        with self.lock:
            p=self.editable(id,revision)
            name=digest(source)+'.tsx';path=self.folder(id)/'designs'/name;path.parent.mkdir(exist_ok=True);path.write_text(source)
            p['design']='designs/'+name
            return self.revise(p)

    def asset_import(self,id,revision,path):
        source=Path(path).expanduser().resolve()
        if source.suffix.lower() not in ('.png','.jpg','.jpeg','.webp','.mp4','.wav','.mp3','.svg'):raise ValueError('Unsupported media asset')
        if not source.is_file() or source.stat().st_size>100*1024*1024:raise ValueError('Media file missing or larger than 100 MB')
        with self.lock:
            p=self.editable(id,revision);name=filehash(source)[:16]+source.suffix.lower()
            target=self.folder(id)/'assets'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
            p['assets'][name]={'file':'assets/'+name};self.revise(p)
            return {'project':p,'static_file':name}

    def start(self,id,stage,frames=None):
        if stage not in ('speech','preview','render'):raise ValueError('Stage must be speech, preview, render')
        frames=frames or []
        if len(frames)>16 or any(type(f)!=int or f<0 for f in frames):raise ValueError('Up to 16 nonnegative frame indices')
        with self.lock:
            p=self.read(id);self.editable(id,p['revision'])
            if not p['script']:raise ValueError('Write the script first')
            if stage!='speech' and (not p['speech'] or not p['design']):raise ValueError('Prepare speech and write a design before rendering')
            job={'id':uuid.uuid4().hex[:12],'status':'queued','stage':stage,'revision':p['revision'],'error':None}
            p['job']=job;self.put(p);self.pool.submit(self._run,id,job,frames)
            return job

    def _run(self,id,job,frames):
        try:
            with self.lock:p=self.read(id);p['job']['status']='running';self.put(p)
            if job['stage']=='speech':
                brand=json.loads((ROOT/'templates/brand.json').read_text())
                shots=[*p['script']['shots'],{'id':'brand','beats':[{k:b[k] for k in ('en','ko')} for b in brand['caption_groups']]}]
                timeline=[]
                for shot in shots:
                    audio,_=self.media.voice(shot);cues,seconds=self.media.align(shot,audio)
                    timeline.append({'id':shot['id'],'frames':round(seconds*60),'captions':cues,'audio':str(audio)})
                p['speech']=timeline
            else:
                folder=self.folder(id)/'renders'/job['id'];public=folder/'public';public.mkdir(parents=True)
                for name in p['assets']:shutil.copy2(self.folder(id)/p['assets'][name]['file'],public/name)
                shutil.copy2(ROOT/'assets/logo.svg',public/'logo.svg');shutil.copy2(ROOT/'assets/fonts/Pretendard-Bold.otf',public/'font.otf')
                for shot in p['speech']:shutil.copy2(shot['audio'],public/(shot['id']+'.wav'))
                shutil.copy2(self.folder(id)/p['design'],folder/'design.tsx')
                timeline=[{k:v for k,v in s.items() if k!='audio'} for s in p['speech']]
                if any(f>=sum(s['frames'] for s in timeline) for f in frames):raise ValueError('Frame outside film duration')
                save(folder/'timeline.json',timeline)
                run(['node',ROOT/'remotion/agent-render.mjs',folder,job['stage'],','.join(map(str,frames))],timeout=1800)
                result={'folder':str(folder.relative_to(self.folder(id))),'revision':p['revision'],'thumbnail':'thumbnail.png','frames':sorted(x.name for x in (folder/'stills').glob('*.png'))}
                if job['stage']=='render':
                    master=folder/'film.mp4';preview=folder/'preview.mp4';info=probe(master)
                    video=next(s for s in info['streams'] if s['codec_type']=='video')
                    if (video['width'],video['height'],video['r_frame_rate'])!=(1080,1920,'60/1') or not any(s['codec_type']=='audio' for s in info['streams']):raise ValueError('Invalid video format or missing audio')
                    total=sum(s['frames'] for s in timeline)/60
                    if abs(float(info['format']['duration'])-total)>.2:raise ValueError('Invalid film duration')
                    run(['ffmpeg','-v','error','-y','-i',master,'-vf','scale=720:1280','-r','30','-c:v','libx264','-crf','21','-preset','fast','-c:a','aac','-movflags','+faststart',preview],timeout=600)
                    for file in (master,preview):run(['ffmpeg','-v','error','-i',file,'-f','null','-'],timeout=300)
                    self.media.subtitles(folder,timeline)
                    result.update(master='film.mp4',preview='preview.mp4',seconds=total,full_decode=True)
                    p['delivery']=result;p['review']=None
                p['preview']=result
            p['job']['status']='complete';self.put(p)
        except Exception as error:
            with self.lock:p=self.read(id);p['job'].update(status='failed',error=str(error)[:1800]);self.put(p)

    def image_path(self,id,name):
        p=self.read(id);result=p.get('preview')
        if not result:raise ValueError('Render a preview first')
        if name=='thumbnail.png':relative=name
        elif name in result['frames']:relative='stills/'+name
        else:raise ValueError('Unknown rendered image')
        return self.folder(id)/result['folder']/relative

    def review(self,id,revision,notes,visual_pass):
        with self.lock:
            p=self.editable(id,revision)
            if not p['delivery']:raise ValueError('Render final video before recording final review')
            if not isinstance(notes,str) or len(notes.strip())<20:raise ValueError('Describe inspected frames, playback, and remaining concerns')
            p['review']={'revision':revision,'render':p['delivery']['folder'],'notes':notes,'visual_pass':bool(visual_pass),'at':now()}
            return self.put(p)
