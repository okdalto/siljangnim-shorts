"""Conservative PCM pause analysis; never equate low energy with proven non-speech."""
import wave
import numpy as np

def read(path):
 with wave.open(str(path)) as f:
  if f.getsampwidth()!=2 or f.getnchannels()!=1:raise ValueError('Expected mono PCM16 WAV')
  return np.frombuffer(f.readframes(f.getnframes()),'<i2').astype(float)/32768,f.getframerate()

def quiet_run(x,sr,start,end):
 # 20ms windows / 5ms hops; broadband + high-frequency energy protect weak consonants.
 win=round(.02*sr);hop=round(.005*sr);rows=[]
 for a in range(max(0,round(start*sr)),min(len(x)-win,round(end*sr)-win)+1,hop):
  z=x[a:a+win];rms=np.sqrt(np.mean(z*z));spec=np.fft.rfft(z*np.hanning(win));freq=np.fft.rfftfreq(win,1/sr);high=np.sqrt(np.sum(abs(spec[freq>=1500])**2))/win
  rows.append((a,rms<10**(-55/20) and high<10**(-60/20)))
 runs=[];begin=None
 for a,ok in rows+[(round(end*sr),False)]:
  if ok and begin is None:begin=a
  if not ok and begin is not None:
   if a-begin>=round(.04*sr):runs.append((begin,a))
   begin=None
 if not runs:raise ValueError('No sufficiently quiet interval: retain audio and inspect waveform/spectrogram')
 a,b=max(runs,key=lambda ab:ab[1]-ab[0]);return a/sr,b/sr

def normalize(x,sr,cues,targets):
 edits=[];report=[]
 for i,target in targets.items():
  a,b=cues[i:i+2];gap=b['start']-a['end'];delta=float(target)-gap
  if abs(delta)<.005:continue
  lo,hi=quiet_run(x,sr,a['end']-.25+.06,b['start']-.25-.06)
  # Preserve 20ms additional handles inside an already verified quiet span.
  lo+=.02;hi-=.02
  if delta<0 and hi-lo < -delta:raise ValueError('Requested shortening exceeds verified silence')
  cut=(lo+hi)/2;end=cut if delta>0 else cut-delta
  if end>hi:cut=hi+delta;end=hi
  edits.append((cut,end,max(0,delta)))
  report.append({'sentence':i,'old_gap':gap,'new_gap':target,'quiet_span':[lo,hi],'edit':[cut,end,max(0,delta)]})
 out=[];cursor=0
 for a,b,pad in edits:
  out.append(x[cursor:round(a*sr)]);out.append(np.zeros(round(pad*sr)));cursor=round(b*sr)
 out.append(x[cursor:]);y=np.concatenate(out)
 def shift(t):
  raw=t-.25;return t+sum(pad-(b-a) for a,b,pad in edits if raw>=b)
 for c in cues:
  for item in [c,*c['words']]:item['start']=shift(item['start']);item['end']=shift(item['end'])
 return y,report

def write(path,x,sr):
 with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr);f.writeframes(np.clip(np.round(x*32768),-32768,32767).astype('<i2').tobytes())

if __name__=='__main__':
 import argparse,json
 from pathlib import Path
 p=argparse.ArgumentParser(description='Read-only waveform/spectral pause audit of a narration plan')
 p.add_argument('plan',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--plot',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);plan=json.loads(a.plan.read_text());report=[]
 for s in plan:
  x,sr=read(s['voice']);rows=[]
  for i,(left,right) in enumerate(zip(s['captions'],s['captions'][1:])):
   row={'after_sentence':i,'aligned_gap':right['start']-left['end']}
   try:row['verified_quiet_span']=quiet_run(x,sr,left['end']-.25+.06,right['start']-.25-.06)
   except ValueError as e:row['review_required']=str(e)
   rows.append(row)
  report.append({'shot':s['id'],'source':s['voice'],'peak':float(abs(x).max()),'start_sample':float(x[0]),'end_sample':float(x[-1]),'end_20ms_rms_dbfs':float(20*np.log10(np.sqrt(np.mean(x[-max(1,round(sr*.02)):]**2))+1e-10)),'endpoint_review_required':bool(max(abs(x[0]),abs(x[-1]))>.002),'gaps':rows})
  if a.plot:
   import matplotlib;matplotlib.use('Agg')
   import matplotlib.pyplot as plt
   fig,ax=plt.subplots(2,1,figsize=(12,5),sharex=True);t=np.arange(len(x))/sr;ax[0].plot(t[::24],x[::24],lw=.4);ax[1].specgram(x,Fs=sr,NFFT=1024,noverlap=768,cmap='magma',vmin=-100,vmax=-20);ax[1].set_ylim(0,8000)
   for c in s['captions']:
    for pane in ax:pane.axvline(c['start']-.25,color='cyan',lw=.6);pane.axvline(c['end']-.25,color='lime',lw=.6)
   for r in rows:
    if 'verified_quiet_span'in r:
     for pane in ax:pane.axvspan(*r['verified_quiet_span'],color='white',alpha=.15)
   ax[0].set_title(s['id']+' — alignment is approximate; inspect weak consonants');ax[1].set_xlabel('Audio seconds (before 0.25s composition lead-in)');fig.tight_layout();fig.savefig(a.out/(s['id']+'.png'),dpi=130);plt.close(fig)
 for left,right in zip(plan,plan[1:]):
  report.append({'transition':left['id']+' → '+right['id'],'aligned_gap':right['start']+right['captions'][0]['start']-left['start']-left['captions'][-1]['end'],'note':'Includes intentional demonstration holds; do not normalize automatically.'})
 (a.out/'pause-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(a.out/'pause-audit.json')
