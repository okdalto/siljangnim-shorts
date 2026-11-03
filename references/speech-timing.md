# Speech timing and safe pause editing

Use this when preparing narration, regenerating a line, or changing pauses. Alignment alone is not an acoustic edit boundary: it can end before a final consonant or include silence before a word.

## Consistent rhythm

For ordinary explanatory sentences, start with an audible gap of about 0.6 seconds (roughly 0.5–0.7), then adapt to delivery and content. This is an editorial default, not a required value for every sentence. Explicit user timings override it. Preserve demonstration holds, listening comparisons and emphatic pauses. Measure cross-shot gaps as well as gaps within one audio file. A request to add 0.3 seconds means add to the existing gap, not replace it with 0.3.

## Analysis before edits

1. Keep original provider audio. Align the exact script, apply the intended pitch-preserving tempo, and update all cue times. Analyze narration-only PCM, before music and final encoding.
2. Inspect waveform plus log-magnitude spectrogram / short-window energy around each aligned boundary. Broadband RMS and high-frequency energy help expose weak consonants such as the end of “points”; they are conservative signals, not perfect VAD. Do not infer clear pronunciation merely from successful forced alignment.
3. Confirm a contiguous quiet interval between sentences, with protected word handles. Prefer cutting the middle of that interval. If alignment and acoustic evidence disagree, retain the audio and flag manual review rather than trim by timestamps alone. Do not silently regenerate paid speech for an editing artifact.
4. Never trim the first word onset to the first aligned timestamp. Keep original attack and at least 80–120 ms of available pre-onset audio plus the normal composition lead-in. Preserve word endings. Check edit seams for amplitude jumps; any microfade must remain within confirmed silence, never across consonants.
5. Edit audio and map every subsequent word, bilingual caption and visual event through the same time transform. Retain the previous caption during the pause. Do not globally slow a physics simulation merely to create a speech gap: hold the pre-event frame or shift the event instead.
6. Re-audit the assembled timeline and inspect the encoded result. Listen to edited seams and regenerated beginnings when audio listening is available; otherwise disclose that acoustic metrics and decoding do not prove audible quality.

## Helper

`scripts/speech_pauses.py` provides conservative `quiet_run` / `normalize` functions and a read-only audit CLI. It expects mono PCM16 WAV and plan cues that include the existing 0.25s composition lead-in. Use NumPy; plotting additionally needs Matplotlib. Other schemas/lead-ins require an adapter, not guessed offsets.

```sh
python scripts/speech_pauses.py /absolute/plan.json --out /absolute/pause-audit --plot
```

The report includes within-shot quiet spans and cross-shot aligned gaps. Plots show waveform, spectrogram and aligned boundaries. Default 20ms windows/5ms hops, broadband −55 dBFS and high-band −60 dBFS thresholds are conservative starting points for clean TTS. Failure to find silence means review, not permission to raise thresholds until a cut passes. No automatic video or audio changes occur in CLI mode. For edits, `normalize` raises if a requested shortening exceeds verified silence; preserve explicit pauses and review the output.

## File endpoints are separate edit seams
Check the original, tempo-processed and final decoded audio at both file boundaries, not only inter-sentence edits. A large last sample is a discontinuity when padding starts, even when all internal edits pass. Report endpoint sample amplitude and final 20ms RMS; the helper flags absolute endpoint amplitude above .002 for review. This is a diagnostic threshold, not an audibility guarantee. A sudden terminal burst or incomplete consonant requires original/provider review or regeneration with an adequate tail. Do not label the complete voice clean based solely on internal seam checks, and do not blindly fade or cut the final phoneme.
