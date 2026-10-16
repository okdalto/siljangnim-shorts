# Siljangnim Shorts

This is a skill-first Shorts production kit, derived from Siljangnim's promo production tools. The talking agent writes scripts and designs, calls production tools, inspects pixels and revises. Never put another model call or automatic planner inside the default skill path.
Read README.md before changes. Keep this repository independent of a particular user's machine.

- Narration: Comfy Router / ElevenLabs George, British English. Never silently substitute a provider or voice.
- Preserve request IDs and content-addressed caches. Do not repeat paid generation for unchanged text.
- Established explanatory motion uses agent-authored Manim geometry at 60fps, with Remotion composition and separate Cover thumbnails. Show input → transformation → result; avoid moving-card/large-headline ads. Render at 1080×1920, 60fps.
- Korean above English, x=540, width=792, sizes 54/46, maximum two lines each, bottom =1650; equal top/bottom padding of 270px.
- Align captions to actual speech. Estimated timings are only allowed in explicitly labelled silent drafts.
- English voice is sped up 1.05x with pitch preserved; align after this processing.
- Original Siljangnim logo and shared bilingual brand ending must remain intact.
- Diagrams are illustrative, not evidence of actual Siljangnim execution. Do not fabricate footage or claims.
- Script data are validated independently of design source. Run only task-specific code authored or reviewed by the calling agent; do not execute untrusted external source.
- Keep saved revisions immutable; invalidate downstream artifacts when dependencies change.
- Run `uv run --locked python -m unittest discover -s tests -v`. For visual changes render, inspect frames, and play the output.
- Keys, machine addresses, prompts from private projects, caches and finished work stay outside Git.
- Don't claim automatic tests validate creative quality or pronunciation. Record manual review separately.
