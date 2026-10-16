"""Prepare an opening preview with tighter pauses throughout the narration.

Usage: python examples/revenge-morph/prepare-opening.py SOURCE_FOLDER OUTPUT_FOLDER
SOURCE_FOLDER must contain the original, unedited flood.wav, revenge.wav and timeline.json.
"""
import json
from pathlib import Path
import shutil
import sys
import wave

source, output = map(Path, sys.argv[1:])
if source.resolve() == output.resolve():
    raise SystemExit('Use a separate output folder to preserve the source audio.')
output.mkdir(parents=True, exist_ok=True)
shutil.copytree(source / 'public', output / 'public', dirs_exist_ok=True)
shutil.copy(Path(__file__).with_name('opening.tsx'), output / 'design.tsx')
# Cuts lie strictly inside measured silence in the ORIGINAL audio. Durations
# are whole video frames, so speech, captions and motion stay synchronized.
cuts_by_shot = {
    'flood': [(2.28, 30), (4.58, 54)],
    'revenge': [(0.90, 28), (2.58, 24), (4.75, 34)],
}
plan = json.loads((source / 'timeline.json').read_text())
for shot in plan:
    cuts = [(start, start + frames / 60) for start, frames in cuts_by_shot[shot['id']]]
    with wave.open(str(source / f"public/{shot['id']}.wav"), 'rb') as audio:
        params = audio.getparams()
        data = audio.readframes(params.nframes)
    stride = params.nchannels * params.sampwidth
    chunks, cursor = [], 0
    for start, end in cuts:
        left = round(start * params.framerate) * stride
        right = round(end * params.framerate) * stride
        chunks.append(data[cursor:left])
        cursor = right
    chunks.append(data[cursor:])
    with wave.open(str(output / f"public/{shot['id']}.wav"), 'wb') as audio:
        audio.setparams(params)
        audio.writeframes(b''.join(chunks))
    def shifted(t):
        return t - sum(max(0, min(t, end) - start) for start, end in cuts)
    shot['frames'] -= sum(frames for _, frames in cuts_by_shot[shot['id']])
    # Remove the extra post-question shot hold; retain the next shot's lead-in.
    if shot['id'] == 'flood':
        shot['frames'] -= 15
    for caption in shot['captions']:
        for key in ('start', 'end'):
            caption[key] = shifted(caption[key] - .25) + .25
        for word in caption.get('words', []):
            for key in ('start', 'end'):
                word[key] = shifted(word[key])
(output / 'timeline.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2))
print(f"Prepared {sum(s['frames'] for s in plan)/60:.2f}s opening; speech samples preserved.")
