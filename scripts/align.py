"""One isolated alignment request; no estimated speech timings in final output."""
import json
import sys
from pathlib import Path
import stable_whisper
import torch

torch.set_num_threads(4)
request=json.loads(Path(sys.argv[1]).read_text())
model=stable_whisper.load_model('base.en',device='cpu')
result=model.align(request['audio'],request['text'],language='en',original_split=True,verbose=False)
if result is None:raise RuntimeError('Speech alignment failed')
segments=[s.to_dict() for s in result.segments]
expected=request['text'].splitlines()
if len(segments)!=len(expected):raise ValueError('Sentence count mismatch')
for source,segment in zip(expected,segments):
    if ''.join(source.split())!=''.join(segment['text'].split()):raise ValueError('Alignment text mismatch')
    if segment['end']<=segment['start']:raise ValueError('Empty sentence')
Path(sys.argv[2]).write_text(json.dumps({'engine':'stable-ts2.19.1/base.en','segments':segments}))
