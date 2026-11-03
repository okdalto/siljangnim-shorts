import copy
import unittest
from shorts_app.check_render import check_probe, check_timeline


class RenderEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.probe = {'streams': [
            {'codec_type': 'video', 'width': 1080, 'height': 1920,
             'avg_frame_rate': '60/1', 'duration': '2.0'},
            {'codec_type': 'audio', 'duration': '2.0'}]}
        self.plan = [{'id': 'example', 'frames': 120, 'captions': [
            {'start': .25, 'end': 1.7, 'ko_lines': ['확인합니다.'], 'en_lines': ['Check it.']}]}]

    def test_narration_lost_in_export_is_rejected(self):
        self.probe['streams'].pop()
        self.assertIn('Narrated output has no audio stream', check_probe(self.probe))
        self.assertEqual(check_probe(self.probe, require_audio=False), [])

    def test_wrong_dimensions_fps_and_truncation(self):
        stream = self.probe['streams'][0]
        stream.update(width=720, height=1280, avg_frame_rate='30/1', duration='1.5')
        self.assertEqual(len(check_probe(self.probe, seconds=2)), 3)

    def test_invalid_rates_do_not_pass(self):
        for value in ['0/0', 'n/a', None, '60000/1001']:
            with self.subTest(value=value):
                self.probe['streams'][0]['avg_frame_rate'] = value
                self.assertTrue(check_probe(self.probe))

    def test_nan_duration_does_not_pass(self):
        self.probe['streams'][0]['duration'] = 'nan'
        self.assertTrue(check_probe(self.probe, seconds=2))

    def test_speech_crossing_cut_is_rejected(self):
        self.plan[0]['captions'][0]['end'] = 2.1
        errors, _ = check_timeline(self.plan)
        self.assertTrue(errors)

    def test_overlap_and_three_lines_are_rejected(self):
        extra = copy.deepcopy(self.plan[0]['captions'][0])
        extra.update(start=1.5, end=1.9, ko_lines=['하나', '둘', '셋'])
        self.plan[0]['captions'].append(extra)
        self.assertEqual(len(check_timeline(self.plan)[0]), 2)

    def test_valid_plan_is_not_mutated(self):
        before = copy.deepcopy(self.plan)
        self.assertEqual(check_timeline(self.plan), ([], 2))
        self.assertEqual(self.plan, before)
        self.assertEqual(check_probe(self.probe, seconds=2), [])

    def test_invalid_plan_structure(self):
        for value in [{}, [], [None], [{'frames': True}], [{'frames': 30, 'captions': []}]]:
            with self.subTest(value=value):
                self.assertTrue(check_timeline(value)[0])

    def test_malformed_cues_report_errors(self):
        for cue in [None, [], 'speech', {'start': 'nan', 'end': 1},
                    {'start': .1, 'end': float('inf')}, {'start': .1}]:
            with self.subTest(cue=cue):
                self.plan[0]['captions'] = [cue]
                self.assertTrue(check_timeline(self.plan)[0])


if __name__ == '__main__':
    unittest.main()
