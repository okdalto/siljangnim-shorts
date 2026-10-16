---
name: siljangnim-shorts
description: Create and revise Siljangnim explanation or promotional Shorts through conversation, with custom motion graphics, a separate thumbnail, George narration and bilingual captions. Use for first-run environment/API setup, video production and visual revisions, not social scheduling.
---
# 실장님 Shorts

You are the production agent. The person talks to you; you plan, write, design, render, inspect and revise. No separate app, form, MCP connection, or nested model call is required. Use the host's file/image/video tools and internal viewer. This document is the production contract; bundled scripts handle repeatable media work.

## Improve through production

This is the author’s working skill for making Siljangnim Shorts. Improve it from actual production experience: preserve reusable fixes and established preferences in the relevant reference or helper, and keep one video's choreography in its project/example. Do not turn every revision into a universal rule or build speculative infrastructure ahead of a real need.

## First use and provider setup

For a new environment, missing dependencies, or a request to configure generation services, follow [first-run setup](references/onboarding.md). Inspect the machine, perform the needed installation, help configure credentials privately, and verify actual readiness. Recommend the established paid-API workflow by default, but honor the user's chosen provider or free/local preference. Comfy and Higgsfield are starting points, not mandatory dependencies. Discover alternatives from current official documentation and add only the task's needed integration. Keep provider defaults separate from an individual project's selection.

## Describe the product accurately

This product is a skill: production instructions plus optional helpers that an existing agent uses. The agent plans, invokes available tools, inspects and revises. Do not advertise it as a standalone app, hosted video generator, autonomous service, or guaranteed one-click automation. Explain required runtime and voice service when relevant. In promotional material say “give your agent a topic; it follows the skill; review and revise in the same conversation.” Do not promise effort-free completion or imply the skill itself is the acting model. Keep diagrams consistent with this distinction.

## Start from the conversation

Read the request and existing project before deciding what to change. Present a short shot plan with each scene's focal object, meaningful movement and corresponding speech. Keep scripts specific and Korean natural. A satire ad does not need the same structure as an explanatory experiment.

Design a separate thumbnail with a clear focal point and a short readable hook. Do not choose an arbitrary video frame. Avoid repeating a stage list for every shot or covering weak visuals with decorative cards. Real footage and explanatory graphics must remain distinguishable.

For revisions, identify whether the problem is the idea, script, composition, movement, timing or voice. Change the relevant source; do not regenerate unchanged speech or replace the visual concept with a different colour alone.

## Visual contract

- Portrait 1080×1920, 60fps. **Equal vertical padding: 270px at the top and 270px at the bottom.** This supersedes the older asymmetric 270/420 convention.
- The shared layout is `remotion/layout.tsx`: content y=270..1650, x=144..936. Use it for both video and thumbnail. Backgrounds may bleed; important text and objects stay inside.
- Korean above English, horizontally centred at x540, width792, 54/46px, at most two lines each. Anchor the caption block's bottom to y1650 so line count does not change the outer bottom padding.
- Keep subtitles and the original logo stable. Use purposeful acceleration, short overshoot and settling for objects. Tie meaningful events to measured speech cues.
- Reuse `assets/logo.svg` unchanged for the brand ending. Do not fabricate execution footage or metrics.

For the established Siljangnim explanatory tone, animate task-specific geometry in Manim at native 60fps and use Remotion for composition, speech and captions. Preserve object identity through visible transformations. Follow the user's concrete visual concept: cards are appropriate when they represent Shorts, for example. Use readable acceleration and deceleration, with anticipation and settling where appropriate. Keep small explanatory labels out of motion scenes unless requested; narration captions carry the words. Promotional shot choreography belongs to its example, not to every new video.

Plan each shot as **input → transformation → result**, tied to actual spoken words. Inspect the intermediate transformation, not only the first and last poses. A new subject needs its own explanatory geometry; do not substitute a fixed menu of diagrams. The separate thumbnail may use a concise hook, but its central image should express the same process.

Read [the design contract](references/design-contract.md) when writing the composition source. There is no fixed diagram menu. The agent authors a Visual component and separate Cover composition. Simple vector layouts belong in code; use image-generation tools when raster artwork materially improves the concept.

## Production tools

Read [production tools](references/production-tools.md) when preparing speech, importing media or rendering with the bundled helpers. Use returned revisions and measured speech cues; preserve cached audio for unchanged text. George British English through Comfy, pitch-preserving 1.05x speed, is the default. Never silently substitute the provider or voice.

## Inspect and deliver

Inspect the cover at phone size, key poses and before/after frames. Check **equal top/bottom padding**, overlap, line breaks and motion tied to speech. If it is dull or crowded, revise the design and render again. Code success is not creative approval.

Watch the continuous video with the host's internal viewer; `./shorts view` is an optional local read-only fallback. Record actual findings using `./shorts review ID --revision N --notes 'What was inspected and what remains' --pass-visual`. Distinguish full decoding, visual playback and actual audio listening. Do not claim one proves another.

For chat review, show a playable preview. For Google Drive final delivery, upload these three files per approved video:

- `<topic>_final.mp4`: final 1080×1920/60fps video with bilingual captions.
- `<topic>_thumbnail.png`: final thumbnail.
- `<topic>_caption_KO_EN.txt`: one UTF-8 file containing Korean post copy, then English post copy, then at most five shared, deduplicated hashtags. Arrange the body continuously for one-step copy and paste.

Read [Drive delivery](docs/DRIVE_DELIVERY.md) when uploading an approved final video. Publishing is separate and needs user authorization. Keep keys, private assets and output/cache folders out of Git. On failure, fix the reported cause and resume; do not loop paid generation. Only execute task-specific code you authored or reviewed; the local renderer is not an OS sandbox.
