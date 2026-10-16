# Production tools

Run commands from this skill's directory (the repository root). The `shorts` helper uses uv; `scripts/setup.sh` prepares rendering dependencies when needed. It does not start a server or another agent.

```sh
./shorts create 'Brief from the conversation'
./shorts script PROJECT_ID --revision 0 --file /absolute/script.json
./shorts design PROJECT_ID --revision 1 --file /absolute/visual.tsx
./shorts speech PROJECT_ID
./shorts preview PROJECT_ID
./shorts status PROJECT_ID
./shorts render PROJECT_ID
```

Use the actual revision returned by the previous command. `script.json` is `{title,shots:[{id,beats:[{en,ko}]}]}`. `speech` returns real alignment cues in the project state. Commands return JSON; long renders can run as a host background shell task. Do not start a duplicate job while one is running.

`preview` returns paths for a separate thumbnail, representative frames and padding-guide images. Open the actual images with the host's image viewer. For event inspection, pass explicit global frame indices: `./shorts preview ID --frames 30 60 90`. For assets, use `./shorts asset ID --revision N --file /absolute/media.mp4` and the returned static filename.

George British English through Comfy is the current voice default. Preserve pitch at 1.05x, align actual speech, cache paid requests, and never silently replace the provider. A different provider or language is possible when the person requests it; update the production contract accordingly. Design-only edits preserve speech. Script edits rebuild cues while reusing unchanged scene audio.


## Runtime and storage

Run `scripts/setup.sh` when using bundled media helpers. They require macOS/Linux, Python 3.12, uv, Node.js 22+ and FFmpeg/ffprobe. The setup script includes locked Manim installation; Cairo/Pango system dependencies must be prepared first. For first-time setup or another provider, follow [onboarding](onboarding.md).

Provide the Comfy key through `COMFY_API_KEY` or `~/.config/siljangnim-shorts/comfy-token`. Paid speech uses service credits. Store work in `agent-projects/` and caches in `.cache/`, both ignored by Git. `SHORTS_AGENT_DATA`, `SHORTS_CACHE_DIR` and `SHORTS_ALIGNMENT_PYTHON` override local paths.
