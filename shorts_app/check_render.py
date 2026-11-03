"""Read-only checks for an authored video and its speech-aligned timeline."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess


def check_probe(probe, *, width=1080, height=1920, fps=60, seconds=None, require_audio=True):
    errors = []
    videos = [s for s in probe.get('streams', []) if s.get('codec_type') == 'video']
    audio = [s for s in probe.get('streams', []) if s.get('codec_type') == 'audio']
    if len(videos) != 1:
        errors.append('Expected exactly one video stream')
    else:
        stream = videos[0]
        if (stream.get('width'), stream.get('height')) != (width, height):
            errors.append(f'Expected {width}x{height}')
        try:
            rate = float(Fraction(stream.get('avg_frame_rate', '0/0')))
            if not math.isclose(rate, fps, abs_tol=.001):
                errors.append(f'Expected {fps} fps, got {rate}')
        except (ValueError, TypeError, ZeroDivisionError):
            errors.append('Missing or invalid frame rate')
        if seconds is not None:
            try:
                duration = float(stream['duration'])
                if not math.isfinite(duration) or abs(duration-seconds) > max(2/fps, .05):
                    errors.append('Video duration differs from timeline')
            except (KeyError, ValueError, TypeError):
                errors.append('Missing video duration')
    if require_audio and not audio:
        errors.append('Narrated output has no audio stream')
    return errors


def check_timeline(plan, fps=60):
    """Check timing and the already-authored two-line layout; no text rewriting."""
    errors, total = [], 0
    if not isinstance(plan, list) or not plan:
        return ['Timeline must be a non-empty shot list'], 0
    for index, shot in enumerate(plan):
        if not isinstance(shot, dict):
            errors.append(f'Shot {index} is not an object')
            continue
        name = shot.get('id', str(index))
        frames = shot.get('frames')
        if type(frames) is not int or frames <= 0:
            errors.append(f'{name}: invalid frame count')
            continue
        total += frames
        cues = shot.get('captions')
        if not isinstance(cues, list) or not cues:
            errors.append(f'{name}: missing aligned captions')
            continue
        previous = -1
        for cue in cues:
            if not isinstance(cue, dict):
                errors.append(f'{name}: invalid speech cue')
                continue
            try:
                start, end = float(cue['start']), float(cue['end'])
                if not (math.isfinite(start) and math.isfinite(end) and
                        0 <= start < end <= frames/fps and start >= previous):
                    errors.append(f'{name}: speech cue overlaps or leaves the shot')
                previous = end
                for lang in ('ko', 'en'):
                    lines = cue.get(lang+'_lines')
                    if (not isinstance(lines, list) or not 1 <= len(lines) <= 2 or
                            any(not isinstance(line, str) or not line.strip() for line in lines)):
                        errors.append(f'{name}: invalid {lang} caption lines')
            except (KeyError, TypeError, ValueError):
                errors.append(f'{name}: invalid speech cue')
    return errors, total/fps


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--timeline', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--width', type=int, default=1080)
    parser.add_argument('--height', type=int, default=1920)
    parser.add_argument('--fps', type=int, default=60)
    parser.add_argument('--allow-silent', action='store_true', help='Only for explicitly silent drafts')
    args = parser.parse_args(argv)
    if min(args.width, args.height, args.fps) <= 0:
        parser.error('width, height and fps must be positive')
    if args.output.resolve() in {args.video.resolve(), args.timeline.resolve() if args.timeline else None}:
        parser.error('output must not overwrite an input')
    report = {'video': str(args.video), 'errors': [], 'full_decode': False,
              'visual_review': 'not assessed', 'audio_listening': 'not assessed',
              'physics_validity': 'not assessed'}
    try:
        with args.video.open('rb') as source:
            report['sha256'] = hashlib.file_digest(source, 'sha256').hexdigest()
        seconds = None
        if args.timeline:
            errors, seconds = check_timeline(json.loads(args.timeline.read_text()), args.fps)
            report['errors'].extend(errors)
            report['timeline_seconds'] = seconds
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                                '-of', 'json', str(args.video)], capture_output=True, text=True, check=True)
        report['probe'] = json.loads(probe.stdout)
        report['errors'].extend(check_probe(report['probe'], width=args.width, height=args.height,
                                            fps=args.fps, seconds=seconds, require_audio=not args.allow_silent))
        decode = subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(args.video),
                                 '-f', 'null', '-'], capture_output=True, text=True)
        report['full_decode'] = decode.returncode == 0 and not decode.stderr.strip()
        if not report['full_decode']:
            report['errors'].append('Full decode failed')
            report['decode_error'] = decode.stderr[-4000:]
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        report['errors'].append(f'{type(error).__name__}: {error}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'passed': not report['errors'], 'report': str(args.output),
                      'errors': report['errors']}, ensure_ascii=False))
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
