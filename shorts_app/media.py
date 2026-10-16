"""Content-addressed speech, forced alignment, and bilingual subtitle export."""
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from . import comfy
from .graphics import wrap
from .model import ROOT, digest
from .store import save

VOICE={'provider':'comfy','voice':'George (male, british)','model':'elevenlabs/eleven_v3',
       'speed':1.0,'stability':.5,'seed':42,'voice_id':comfy.GEORGE}
RATE=1.05


def run(args, **kwargs):
    result=subprocess.run([str(a) for a in args],capture_output=True,text=True,**kwargs)
    if result.returncode:
        # Subprocess diagnostics stay local; never return provider payloads to the browser.
        folder=ROOT/'.cache/diagnostics';folder.mkdir(parents=True,exist_ok=True)
        log=folder/(digest(result.stderr)[:12]+'.log');log.write_text(result.stdout+'\n'+result.stderr)
        raise RuntimeError(f'{Path(str(args[0])).name} 실행에 실패했습니다. 설정을 확인한 뒤 이어서 제작하세요. 진단: {log.name}')
    return result.stdout


def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path],timeout=60))


def filehash(path):
    with Path(path).open('rb') as file: return hashlib.file_digest(file,'sha256').hexdigest()


def valid_artifact(folder,name):
    target=folder/name; marker=folder/(name+'.complete.json')
    return target.is_file() and marker.is_file() and json.loads(marker.read_text()).get('sha256')==filehash(target)


def mark(folder,name): save(folder/(name+'.complete.json'),{'sha256':filehash(folder/name)})



class Media:
    def __init__(self,cache=None):
        self.cache=Path(cache or os.environ.get('SHORTS_CACHE_DIR',ROOT/'.cache'))
        self.cache.mkdir(parents=True,exist_ok=True)

    def voice(self,shot):
        text=' '.join(b['en'] for b in shot['beats'])
        key=digest({'provider':'comfy','model':VOICE['model'],'params':comfy.parameters(text,VOICE),'service':comfy.BASE})
        folder=self.cache/'voice'/key;folder.mkdir(parents=True,exist_ok=True)
        audio=folder/'voice.wav'
        # Existing production caches use complete.json, so retain their request and audio.
        legacy=folder/'complete.json'
        cached=audio.exists() and legacy.exists() and json.loads(legacy.read_text()).get('sha256')==filehash(audio)
        if not cached and not valid_artifact(folder,'voice.wav'):
            source=comfy.generate(text,VOICE,folder)
            pending=folder/'voice.pending.wav'
            run(['ffmpeg','-v','error','-y','-i',source,'-ar','48000','-ac','1',pending],timeout=120)
            if float(probe(pending)['format']['duration'])<.1:raise ValueError('Empty narration')
            pending.replace(audio);mark(folder,'voice.wav')
        tempo=folder/'tempo-1.05.wav'
        if not valid_artifact(folder,tempo.name):
            pending=folder/'tempo.pending.wav'
            run(['ffmpeg','-v','error','-y','-i',audio,'-af',f'atempo={RATE}','-c:a','pcm_s16le',pending],timeout=120)
            pending.replace(tempo);mark(folder,tempo.name)
        return tempo, json.loads((folder/'provider.json').read_text())

    def align(self,shot,audio):
        text='\n'.join(b['en'] for b in shot['beats'])
        worker=ROOT/'scripts/align.py'
        key=digest({'audio':filehash(audio),'text':text,'worker':filehash(worker),'engine':'stable-ts2.19.1/base.en'})
        folder=self.cache/'alignment'/key;folder.mkdir(parents=True,exist_ok=True)
        target=folder/'alignment.json'
        if not valid_artifact(folder,target.name):
            request=folder/'input.json';save(request,{'audio':str(audio),'text':text})
            python=os.environ.get('SHORTS_ALIGNMENT_PYTHON',str(ROOT/'.alignment/bin/python'))
            run([python,worker,request,folder/'pending.json'],timeout=600)
            (folder/'pending.json').replace(target);mark(folder,target.name)
        segments=json.loads(target.read_text())['segments']
        duration=float(probe(audio)['format']['duration'])
        if len(segments)!=len(shot['beats']):raise ValueError('음성 정렬 문장 수가 다릅니다.')
        cues=[];last=-1
        for b,s in zip(shot['beats'],segments):
            if not 0 <= s['start'] < s['end'] <= duration+.15 or s['start']<last:
                raise ValueError('잘못된 음성 정렬 시점입니다.')
            last=s['end']
            cues.append({**b,'start':s['start']+.25,'end':s['end']+.25,
                         'words':s.get('words',[]),'ko_lines':wrap(b['ko'],54,792),'en_lines':wrap(b['en'],46,792)})
        return cues,math.ceil((duration+.5)*60)/60

    @staticmethod
    def subtitles(folder,plan):
        def stamp(t):
            ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
            return f'{h:02}:{m:02}:{s:02},{ms:03}'
        for lang in ('ko','en'):
            rows=[];cursor=0
            for shot in plan:
                cues=shot['captions']
                for i,c in enumerate(cues):
                    start=0 if i==0 else c['start']
                    end=cues[i+1]['start'] if i+1<len(cues) else shot['frames']/60
                    rows.append(f'{len(rows)+1}\n{stamp(cursor+start)} --> {stamp(cursor+end)}\n{c[lang]}\n')
                cursor+=shot['frames']/60
            (folder/f'subtitles.{lang}.srt').write_text('\n'.join(rows))
