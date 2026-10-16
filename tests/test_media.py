import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from shorts_app.media import Media, VOICE, filehash, mark
from shorts_app import comfy
from shorts_app.model import ROOT, digest
from shorts_app.store import save

SHOT = {'id': 'hook', 'beats': [{'en': 'Make your own.', 'ko': '직접 만들어 보세요.'}]}

class MediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.media = Media(self.root)

    def test_existing_paid_voice_and_tempo_are_reused(self):
        text = SHOT['beats'][0]['en']
        key = digest({'provider': 'comfy', 'model': VOICE['model'],
                      'params': comfy.parameters(text, VOICE), 'service': comfy.BASE})
        folder = self.root / 'voice' / key
        folder.mkdir(parents=True)
        (folder / 'voice.wav').write_bytes(b'original cached audio')
        save(folder / 'complete.json', {'sha256': filehash(folder / 'voice.wav')})
        (folder / 'tempo-1.05.wav').write_bytes(b'processed cached audio')
        mark(folder, 'tempo-1.05.wav')
        save(folder / 'provider.json', {'request_id': 'preserved-request'})
        with patch('shorts_app.comfy.generate', side_effect=AssertionError('Paid call forbidden')), patch('shorts_app.media.run', side_effect=AssertionError('Cache must be reused')):
            audio, provider = self.media.voice(SHOT)
        self.assertEqual(audio.read_bytes(), b'processed cached audio')
        self.assertEqual(provider['request_id'], 'preserved-request')

    def test_alignment_cache_keeps_actual_cues_and_refreshes_korean(self):
        audio = self.root / 'voice.wav'
        audio.write_bytes(b'cached audio')
        key = digest({'audio': filehash(audio), 'text': SHOT['beats'][0]['en'],
                      'worker': filehash(ROOT / 'scripts/align.py'), 'engine': 'stable-ts2.19.1/base.en'})
        folder = self.root / 'alignment' / key
        save(folder / 'alignment.json', {'segments': [{'start': .1, 'end': 1.2, 'words': [{'word': 'Make', 'start': .1, 'end': .4}]}]})
        mark(folder, 'alignment.json')
        changed = {'id': 'hook', 'beats': [{'en': SHOT['beats'][0]['en'], 'ko': '당신도 만드세요.'}]}
        with patch('shorts_app.media.probe', return_value={'format': {'duration': '1.5'}}), patch('shorts_app.media.run', side_effect=AssertionError('Alignment cache must be reused')):
            cues, duration = self.media.align(changed, audio)
        self.assertEqual(cues[0]['ko'], '당신도 만드세요.')
        self.assertAlmostEqual(cues[0]['start'], .35)
        self.assertEqual(cues[0]['words'][0]['start'], .1)
        self.assertEqual(duration, 2)

    def test_subtitles_continue_across_shots_in_both_languages(self):
        plan = [{'frames': 120, 'captions': [{'start': .25, 'en': 'First.', 'ko': '첫째.'}, {'start': 1, 'en': 'Second.', 'ko': '둘째.'}]},
                {'frames': 60, 'captions': [{'start': .25, 'en': 'End.', 'ko': '끝.'}]}]
        self.media.subtitles(self.root, plan)
        for lang, word in [('ko', '끝.'), ('en', 'End.')]:
            text = (self.root / f'subtitles.{lang}.srt').read_text()
            self.assertIn('00:00:02,000 --> 00:00:03,000\n' + word, text)
            self.assertIn('00:00:00,000 --> 00:00:01,000', text)
