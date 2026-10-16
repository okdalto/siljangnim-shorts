import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

keys = module('configure_key', 'configure-key.py')
doctor = module('doctor', 'doctor.py')

class OnboardingTests(unittest.TestCase):
    def test_private_key_storage_and_explicit_replacement(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / 'config'
            path = keys.save_key('example', 'test-only-secret', directory)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(directory.stat().st_mode & 0o777, 0o700)
            with self.assertRaises(ValueError):
                keys.save_key('example', 'different', directory)
            self.assertEqual(path.read_text(), 'test-only-secret\n')
            keys.save_key('example', 'replacement', directory, replace=True)
            self.assertEqual(path.read_text(), 'replacement\n')

    def test_invalid_provider_and_multiline_key_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            for provider, value in [('../escape', 'secret'), ('comfy', ''), ('comfy', 'a\nb')]:
                with self.assertRaises(ValueError):
                    keys.save_key(provider, value, temp)
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_doctor_uses_same_file_precedence_as_comfy(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'TEST_KEY': 'env-secret'}):
            path = Path(temp) / 'key'
            self.assertTrue(doctor.credential_present(path, 'TEST_KEY'))
            path.write_text('')
            self.assertFalse(doctor.credential_present(path, 'TEST_KEY'))
            path.write_text('saved-secret')
            self.assertTrue(doctor.credential_present(path, 'TEST_KEY'))

    def test_missing_runtime_is_a_failed_check(self):
        self.assertFalse(doctor.check_command(['/nonexistent/shorts-runtime']))

    def test_setup_installs_manim_and_rejects_old_node_before_installing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'scripts').mkdir()
            (root / 'scripts/setup.sh').write_text((ROOT / 'scripts/setup.sh').read_text())
            bin_dir = root / 'bin'
            bin_dir.mkdir()
            log = root / 'calls'
            for name in ('uv', 'node', 'npm', 'ffmpeg', 'ffprobe', 'dirname'):
                body = '#!/bin/sh\n'
                if name == 'dirname':
                    body += 'exec /usr/bin/dirname "$@"\n'
                else:
                    body += f'echo "{name} $*" >> "$CALL_LOG"\n'
                    if name == 'node': body += '[ "${OLD_NODE:-0}" = 0 ] || exit 1\n'
                path = bin_dir / name
                path.write_text(body)
                path.chmod(0o755)
            for name in ('.alignment/bin/python', '.venv/bin/python'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('#!/bin/sh\nexit 0\n')
                path.chmod(0o755)
            env = {**os.environ, 'PATH': str(bin_dir), 'CALL_LOG': str(log)}
            result = subprocess.run(['/bin/sh', str(root / 'scripts/setup.sh')], env=env, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('uv sync --project motion --locked', log.read_text())
            log.write_text('')
            result = subprocess.run(['/bin/sh', str(root / 'scripts/setup.sh')], env={**env, 'OLD_NODE': '1'}, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('uv sync', log.read_text())
