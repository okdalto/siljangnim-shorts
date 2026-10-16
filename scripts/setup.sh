#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ "$#" -gt 0 ]; then
  if [ "$1" = '--help' ]; then
    printf '%s\n' 'Usage: scripts/setup.sh' 'Installs locked Python, alignment, Remotion and Manim dependencies.' 'System prerequisites: uv, Node.js 22+, npm, FFmpeg/ffprobe, Cairo/Pango build dependencies.'
    exit 0
  fi
  printf '%s\n' 'Unknown argument; use --help' >&2
  exit 2
fi
for cmd in uv node npm ffmpeg ffprobe; do
  command -v "$cmd" >/dev/null || { printf 'Missing %s. Follow references/onboarding.md for your OS.\n' "$cmd"; exit 1; }
done
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) { console.error("Node.js 22+ required"); process.exit(1); }'
uv sync --locked
[ -x .alignment/bin/python ] || uv venv --python 3.12 .alignment
uv pip install --python .alignment/bin/python 'stable-ts==2.19.1' 'openai-whisper==20250625' 'torch==2.6.0' 'torchaudio==2.6.0' 'numpy==1.26.4'
npm ci --prefix remotion
uv sync --project motion --locked
.venv/bin/python scripts/doctor.py
printf '%s\n' 'Dependencies prepared. Next: verify rendering and the selected provider using references/onboarding.md.'
