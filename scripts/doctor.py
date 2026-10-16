"""Read-only local readiness checks. Never prints credentials or calls paid APIs."""
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check_command(args):
    try:
        return subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def credential_present(path, env):
    try:
        return bool(path.read_text().strip()) if path.is_file() else bool(os.environ.get(env, '').strip())
    except OSError:
        return False


def report():
    alignment = os.environ.get('SHORTS_ALIGNMENT_PYTHON', str(ROOT / '.alignment/bin/python'))
    checks = {name: bool(shutil.which(name)) for name in ('uv', 'node', 'npm', 'ffmpeg', 'ffprobe')}
    checks['node_22_plus'] = check_command(['node', '-e', 'process.exit(Number(process.versions.node.split(".")[0]) >= 22 ? 0 : 1)'])
    checks['base_python'] = check_command([str(ROOT / '.venv/bin/python'), '-c', 'import PIL'])
    checks['alignment'] = check_command([alignment, '-c', 'import stable_whisper, torch, torchaudio'])
    checks['manim'] = check_command([str(ROOT / 'motion/.venv/bin/python'), '-c', 'import manim, cairo, manimpango'])
    checks['remotion'] = check_command(['node', '--input-type=module', '-e',
        f'import({json.dumps((ROOT / "remotion/node_modules/@remotion/renderer/dist/index.js").as_uri())})'])
    config = Path.home() / '.config/siljangnim-shorts'
    return {'platform': platform.system(), 'architecture': platform.machine(), 'checks': checks,
            'credentials': {'comfy': credential_present(Path(os.environ.get('COMFY_KEY_FILE', str(config / 'comfy-token'))), 'COMFY_API_KEY'),
                            'higgsfield': credential_present(config / 'higgsfield-token', 'HF_API_KEY')},
            'note': 'Credential presence is not API validation. Rendering and provider access need separate smoke checks.'}


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
