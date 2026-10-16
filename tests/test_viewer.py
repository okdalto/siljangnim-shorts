import tempfile
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from shorts_app.agent_workspace import Workspace
from shorts_app.agent_viewer import start_viewer

class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.w = Workspace(self.temp.name)
        self.addCleanup(self.w.pool.shutdown)
        self.server = start_viewer(self.w, 0)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.media = Path(self.temp.name) / 'abc/renders/check/film.mp4'
        self.media.parent.mkdir(parents=True)
        self.media.write_bytes(b'0123456789')

    def test_video_range_and_project_listing(self):
        request = urllib.request.Request(self.url + '/media/abc/renders/check/film.mp4', headers={'Range': 'bytes=2-5'})
        with urllib.request.urlopen(request) as response:
            self.assertEqual(response.status, 206)
            self.assertEqual(response.read(), b'2345')
        with urllib.request.urlopen(self.url + '/api/projects') as response:
            self.assertEqual(response.read(), b'[]')

    def test_host_and_private_files_are_rejected(self):
        requests = [urllib.request.Request(self.url, headers={'Host': 'evil.example'}),
                    urllib.request.Request(self.url + '/media/abc/project.json'),
                    urllib.request.Request(self.url + '/media/../../secret.mp4')]
        for request in requests:
            with self.assertRaises(urllib.error.HTTPError) as result:
                urllib.request.urlopen(request)
            self.assertEqual(result.exception.code, 403)

    def test_viewer_has_no_edit_endpoint(self):
        request = urllib.request.Request(self.url + '/api/projects', data=b'{}', method='POST')
        with self.assertRaises(urllib.error.HTTPError) as result:
            urllib.request.urlopen(request)
        self.assertEqual(result.exception.code, 501)
