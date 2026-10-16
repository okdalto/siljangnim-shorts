#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo 'Install uv first: https://docs.astral.sh/uv/'; exit 1; }
command -v ffmpeg >/dev/null || { echo 'Install ffmpeg first.'; exit 1; }
command -v node >/dev/null || { echo 'Install Node.js 22 or later first.'; exit 1; }
uv sync --locked
[ -x .alignment/bin/python ] || uv venv --python 3.12 .alignment
uv pip install --python .alignment/bin/python 'stable-ts==2.19.1' 'openai-whisper==20250625' 'torch==2.6.0' 'torchaudio==2.6.0' 'numpy==1.26.4'
npm ci --prefix remotion
printf '%s\n' 'Ready. Configure Comfy; use the skill in your agent. No app or MCP connection required.'
