# Frame-accurate composition and 60fps verification

Read this before patching, retiming, compositing or exporting an existing video. A 60fps container can still repeat frames while skipping source motion. During Diffusion production, native motion updated every frame but timestamp-offset patch overlays introduced a recurring three-frame cadence. Restoring the native frames fixed the motion without changing narration or duration.

## Rerender choreography when timing or continuity changes

The default for changed scene durations, revised narration or a disconnected explanatory sequence is a fresh source render on the revised full timeline. Keep a persistent scene state: the object that leaves one explanation is the object that enters the next. Match endpoint positions, shape, colour, scale and velocity; include camera motion in the same timing plan. A speech pause may leave the motion running. Recalculate all downstream frame ranges after timing changes.

Do not join previously rendered fragments and blend between them as a substitute for designing the transition. Whole-frame blending cannot fix a reset particle, a mismatched camera, an unfinished transformation or an animation that restarts at the next sentence. Object-level fading can be intentional choreography; it must not conceal mismatched clips or fade narration captions.

The patch mechanics below are for narrow corrections that leave the surrounding choreography and timing intact, or for an explicitly requested edit. They are not the default for rebuilding a video. For a full continuity revision, render the explanation as one continuous native-frame source, then add speech and captions independently. Verify the final output against that new source and watch every scene boundary.

## Assemble by frame number

- Keep an immutable lossless editing master (for example FFV1 video with PCM audio). Use original renders and cached narration as sources. Export the delivery H.264/AAC once from the new master; never use successive delivery MP4s as editing masters. Lossless storage prevents further degradation but cannot restore already-lost detail.
- Record each patch as `output_start`, `output_end_exclusive`, `source_start`, source path and affected layers/rectangle. All positions are integer frames on the current timeline. Update the map after every cut, insertion or retime; old project timestamps are not the current EDL.
- For a same-rate patch, decode sequential source frames and place source frame `source_start + (n - output_start)` at output frame `n`. Write exactly one frame for each output index to a 60fps encoder. Assert decoded frame lengths, patch lengths and total output count; fail on premature EOF rather than silently padding a missing render.
- Decode without implicit frame-rate conversion. Verify seek/frame indexing at patch boundaries; for exact selection, trim by decoded frame index. Preserve the approved pixel format, colour range and colour metadata. Direct YUV plane copying avoids unnecessary RGB round trips; 4:2:0 rectangles need even coordinates. Do not apply blanket colour correction to fix timing.
- Do not use timestamp-offset `overlay` as the default patch assembler. In particular, offsetting millisecond-timebase clips by `start/60` can make framesync repeat/skip frames. If a timestamp-based pipeline is unavoidable, prove its mapping against native source frames; setting `-r 60` or `fps=60` alone is not a fix.
- For a deliberate retime, specify a continuous source-frame mapping and review its endpoint velocity. Rerender procedural motion at every target frame when possible. Do not claim duplicated frames or interpolated low-rate footage are native 60fps. An intentional voice pause does not freeze motion unless requested.
- Preserve audio by stream copy from the approved lossless master for visual-only edits. When the edit changes duration, update audio/caption timing explicitly. Keep a per-version source map and verification report with the project, outside the public skill repository.

The essential same-rate loop is:

```text
for output_frame in range(total_frames):
    frame = next(approved_master)
    for patch active at output_frame:
        source_frame = next(patch_source)
        replace only patch's intended layer or rectangle
    encode(frame)  # one output frame, at 60fps
```

## Keep captions independent

Graphics transitions do not determine subtitle opacity. Composite narration captions after graphics transitions, or preserve/replace the caption region separately when editing a burned-in master. Default to fully opaque, speech-aligned caption changes; do not crossfade outgoing and incoming sentences together. Keep both languages on the same cue and preserve the established layout. A deliberately requested caption animation is an exception, not a reason to blend captions at every scene change.

Inspect the boundary frames and a short continuous clip. A correct graphics fade must not reveal a leftover subtitle for one frame. For caption-only fixes, compare decoded graphics hashes before and after; for graphics-only fixes, compare the unchanged caption region. Audio must remain identical when no audio edit was requested.

## Verify actual cadence before delivery

1. **Structure:** fully decode the final export and check 1080×1920, nominal/average rate 60/1, expected decoded frame count and duration (`frames / 60`). Inspect monotonic presentation timestamps; a 1/1000 container timebase may alternate 16/17ms intervals, which is normal and is not itself evidence of stutter.
2. **Motion:** inspect frame-to-frame differences across the whole graphics timeline, excluding captions from the motion measurement. Use exact duplicates for lossless sources and calibrated near-duplicate differences for compressed delivery. Look for regular low/high change patterns (for example every third frame) during continuous movement. Separately account for intentional holds, tiny subpixel motion and discrete denoising steps; do not smooth every still frame automatically.
3. **Source comparison:** for suspicious intervals, compare consecutive native-render frames with the assembled master and delivery. Native motion changing on each frame while the composite repeats frames is a composition failure. Check representative motion windows and at least several frames on both sides of every patched boundary. A frame count, successful encode, or a single still cannot establish smooth 60fps motion.
4. **Continuity:** review the moving result at normal speed, including camera acceleration, object motion, title drawing, colour/background continuity and subtitle cuts. Verify unchanged audio with decoded PCM or stream hashes and unchanged layers with decoded pixel comparisons where applicable. Record automated checks separately from visual playback and actual audio listening.
5. **Report:** retain the source/output frame ranges, intentional holds, duplicate/cadence findings, audio checks and unresolved limitations in the project. Deliver only after explaining or repairing suspicious motion windows. Do not assert that every frame differs: still scenes legitimately repeat.

Useful structural checks (substitute the actual output file):

```sh
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_read_frames,time_base -of json final.mp4
ffmpeg -v error -i final.mp4 -f null -
```

These checks are necessary but must be paired with the motion/source comparison above.
