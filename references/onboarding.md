# First-run setup

Use when the person is new, asks to install/configure a provider, or a required tool is missing. The agent performs inspection, installation and configuration within the requested scope; do not hand back a command list and stop. Reuse working tools and credentials. Explain only meaningful choices and the next user action that actually requires their account or input.

## 1. Inspect and choose

Run `python3 scripts/doctor.py` from the skill directory; it uses the standard library, makes no API calls and reports only credential presence. If Python is missing, inspect the OS and installed package manager first. Read the repository's locked versions before installing. Native support is macOS/Linux; on Windows use an available WSL2 Linux environment and keep files and dependencies there. Do not claim native Windows support for the POSIX CLI.

Recommend a paid generation API by default for a convenient hosted production workflow, while keeping local/free options available when the person prefers them. This is a workflow recommendation, not a promise that paid output is always better. Reuse an existing subscription or connected tool when it meets the task. Explain that web subscriptions, API access and usage credits may differ. Check current pricing and account access; never invent prices or promise free usage.

| Need | Default recommendation | Other choices |
|---|---|---|
| Narration | Existing bundled Comfy Router + ElevenLabs George path | A requested TTS service or local TTS, after checking language, voice and output format |
| Thumbnail/raster artwork | The host's available image-generation tool; suggest a paid image API if none is available | Higgsfield or another user-selected provider; local image generation if hardware and licensing fit |
| Explanatory motion | Local Manim + Remotion | Generated images/clips can be imported when the concept calls for them |

Higgsfield and Comfy are examples, not required accounts. Do not install every provider or replace an explicitly requested provider with the default. Free/local generation may need model downloads, more memory, a GPU and license review; assess the actual machine before recommending it. Do not start large model downloads for a paid-API workflow.

## 2. Prepare the machine

Check existing package managers and current official install instructions, then install only missing prerequisites. On macOS with Homebrew, the relevant packages are `uv`, `node` (22+), `ffmpeg`, `pkg-config`, `cairo`, `pango`. On Debian/Ubuntu, Cairo/Pango builds generally need `build-essential`, `python3-dev`, `pkg-config`, `libcairo2-dev`, `libpango1.0-dev`; obtain a suitable Node.js and uv through their official supported paths. Check distro package versions rather than assuming `apt install nodejs` provides Node 22. If no package manager exists, use its official installer or another official installation route suitable for that machine. Avoid upgrading unrelated packages.

Use [uv installation](https://docs.astral.sh/uv/getting-started/installation/), [Node.js downloads](https://nodejs.org/en/download), [FFmpeg downloads](https://ffmpeg.org/download.html), and [Manim installation](https://docs.manim.community/en/stable/installation/uv.html) as discovery starting points. The repository pins Manim 0.19.0; current documentation may describe a newer release, so preserve the lockfile and resolve version-specific build requirements. LaTeX is only needed for scenes that use TeX; ordinary geometry and text do not require installing a full TeX distribution.

Run `./scripts/setup.sh`. It installs the base Python environment, speech alignment tools, Remotion and the locked Manim environment. System packages are installed by the agent using the detected OS, not blindly inside the script. If privileged installation requires user interaction, complete independent work and identify the exact missing dependency. Re-run the doctor after fixing a failure. Never report readiness from package installation alone.

## 3. Discover and configure the selected provider

For an unfamiliar provider, search its current official developer docs. Confirm model availability for the task, account/API entitlement, key creation, authentication format, model-specific schema, output format, polling/cancellation, limits, pricing and usage rights. Record the selected provider/model, official documentation links and verification date in a local project setup note, with no secrets. Read the smallest relevant documentation set; do not build a universal provider framework.

Starting points, checked 2026-10-16 (recheck at setup time):

- **Comfy Router:** the bundled adapter is `shorts_app/comfy.py`, using `https://api.comfy.org` with `X-API-Key`. It currently supports the established ElevenLabs v3 / George narration path. The code is an existing implementation, not proof of current account access. Find current official documentation through the provider's site/account before adding models or changing endpoints. Comfy Router is not the same thing as a local ComfyUI server; clarify this if the user's request is ambiguous.
- **Higgsfield:** begin with the [official API quickstart](https://open.higgsfield.ai/quick-start) and [documentation index](https://docs.higgsfield.ai/docs/llms.txt), then the selected model's documentation. The current quickstart uses `https://api.higgsfield.ai` and `Authorization: Key <complete copied credential>`. Preserve the credential exactly as issued; do not ask users to reconstruct it from remembered formats. Verify the chosen SDK's environment variables independently. API access and web subscription billing can differ.
- **Other providers:** use their official docs and user-selected model. A provider name or saved key alone does not mean this repo already has an adapter for it.

Prefer the host's secure credential store if available. Otherwise have the person enter the credential in a private terminal prompt:

```sh
python3 scripts/configure-key.py comfy
python3 scripts/configure-key.py higgsfield
# Or the selected provider's lowercase name.
```

The helper saves a mode-0600 file under `~/.config/siljangnim-shorts/<provider>-token`. It never accepts a key as a command-line argument and does not overwrite an existing key without `--replace`. Run it in a terminal the person can use; do not request keys in chat. If a key already exists in a supported environment variable or credential file, reuse it without displaying it. Do not read entire environment files or print environment dumps.

Comfy automatically reads `comfy-token`, `COMFY_KEY_FILE`, or `COMFY_API_KEY` (file takes precedence). Other provider files are storage only: the agent's adapter must read them and pass the documented authentication header/SDK option. Never imply merely saving a Higgsfield key enables `./shorts speech` for Higgsfield. Keep secrets out of source, logs, URLs, browser bundles and project artifacts. Report presence and validation status only.

## 4. Connect only the needed capability

Use an existing connected tool or supported adapter before writing another one. For a requested image provider, create a small task-local helper from its official SDK/REST examples, save its output file, and import it using `./shorts asset`. For a separate raster thumbnail, place the approved image in the Cover composition or final delivery and inspect its actual dimensions and padding.

For alternate narration, the current `./shorts speech` command remains the bundled Comfy path. Implement a task-local `Media` subclass overriding `voice(shot)` and pass it to `Workspace(root, media=adapter)`; inherit `align()` and `subtitles()`. `voice` returns `(audio_path, metadata)`. Normalize returned audio to a local WAV, preserve pitch when applying the requested tempo once, and let the existing alignment stage measure that processed audio. Support the brand shot as well as script shots. Use `Workspace.start(id, 'speech')`, wait for its job, then use normal CLI preview/render on the same workspace. Do not run the custom workspace concurrently with CLI writes. Keep the default provider unchanged for other projects.

Cache generated output by provider, model, voice, input and relevant settings; persist request IDs before polling. Reuse completed media and resume an existing job after a timeout. Do not repeat a billable request as a connection test. Review generated helper code before execution and preserve each provider's documented credential boundaries.

## 5. Verify and hand off

1. Run the doctor and import Manim plus its Cairo/Pango dependencies. Render a short Circle→Square clip containing a `Text` object to verify geometry, text and encoding. Check 1080×1920/60fps with ffprobe. If Chromium is missing for Remotion, use the installed renderer/CLI's documented browser installation path, then retry.
2. Render a short Remotion composition with a separate Cover, logo and bilingual captions. Verify actual images and full MP4 decoding. Silent synthetic audio is acceptable for this local installation smoke test only; label it as a test, never as finished narration.
3. For the selected API, use a documented non-generating authentication/account check when available. Do not invent a health endpoint. If validation requires paid generation, explain the minimum test and its cost basis, and proceed only within the user's existing generation/budget authorization; otherwise report “configured; generation unverified” and ask for that specific missing decision. Setup alone does not authorize purchases, subscriptions or arbitrary generation spend.
4. On the first authorized production request, verify one real output before expanding the batch. Do not claim paid API success from a saved key or installed SDK.
5. Summarize what is ready, the selected provider/model and pricing basis, what was actually tested, and any remaining account step. Store only nonsecret setup results locally. The user should be able to continue by describing a video in the same conversation.
