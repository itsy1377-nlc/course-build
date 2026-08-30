"""Put the pieces together: stills, recordings, narration, captions, transcript.

Everything here is driven by measured audio durations. A slide holds for
exactly as long as the cues spoken over it. A caption cue starts and ends where
its audio does. Nothing is estimated and nothing is recognised.

Terminal scenes are the one place two clocks meet. A recording runs at whatever
pace the tape and the machine produce; narration runs at whatever pace the
voice produces. They are reconciled by holding the last frame or by padding the
audio with silence, whichever is short. A mismatch past MAX_DRIFT is a build
failure rather than a silent stretch, because past that point the words no
longer describe what is on screen and a human needs to fix the script or the
tape. That is a real limitation of narrating over a recording, not a solved
problem.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from . import slides, tape as tape_mod

# Past this the narration and the recording have genuinely diverged.
MAX_DRIFT = 0.25

FPS = 25
# ffmpeg 9 removed -vsync in favour of -fps_mode. The concat demuxer needs an
# explicit constant frame rate here, or a still held for 3.6 seconds becomes a
# single frame with a 3.6 second duration and some players show nothing.
# CRF 26 with stillimage tuning measured 251 kbps on a slide-heavy clip, which
# puts the whole seventeen video library at about 143 MB against a 500 MB
# Canvas course quota. There is no reason to spend more.
CRF = "26"
AUDIO_BITRATE = "96k"
# Broadcast-ish loudness. Raw Kokoro output measured -26.9 dB mean, which is
# quiet enough that a student would reach for the volume between this and
# everything else they watch.
LOUDNESS_TARGET = "I=-16:TP=-1.5:LRA=11"


@dataclass
class CueTiming:
    index: int
    text: str
    start: float
    end: float


def _run(command: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(command[:6])} ... failed:\n{result.stderr[-1200:]}")


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(result.stdout.strip())


def _timestamp(seconds: float) -> str:
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{secs:06.3f}"


CAPTION_LINE = 42
CAPTION_LINES = 2
# No caption should flash. Below about a second a viewer registers movement
# rather than words, which is worse than the long line it replaced.
MIN_CUE = 1.0


def _wrap(text: str, width: int = CAPTION_LINE) -> list[str]:
    """Greedy wrap at word boundaries."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _split_evenly(text: str, parts: int) -> list[str]:
    """Break text into roughly equal parts at word boundaries.

    Balanced, not greedy. Filling the first cue to capacity and dumping the
    remainder into the next produced 78 cues under a second across the library,
    the worst a 0.14 second flash of the word "2." Because cue duration is
    apportioned by character count, equal-length parts give equal-length cues,
    which is what stops the stub appearing at all.
    """
    words = text.split()
    if parts <= 1 or len(words) <= parts:
        return [text]
    target = len(text) / parts
    chunks, current = [], ""
    for index, word in enumerate(words):
        candidate = f"{current} {word}".strip()
        remaining = len(words) - index - 1
        # Close this chunk once it has reached its share, provided every
        # remaining chunk can still be given at least one word.
        if current and len(candidate) > target and remaining >= parts - len(chunks) - 1:
            chunks.append(current)
            current = word
            if len(chunks) == parts - 1:
                current = " ".join([word, *words[index + 1:]])
                break
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def write_vtt(timings: list[CueTiming], out: Path) -> Path:
    """WebVTT from authored text and measured audio. Exact by construction.

    Cues are wrapped to two display lines, and an authored line too long for
    two is split into evenly sized timed cues. An unwrapped cue renders as one
    strip across the video: 86 percent of this library's cues were over 42
    characters before this existed.
    """
    blocks, number = ["WEBVTT", ""], 0
    for cue in timings:
        span = cue.end - cue.start
        parts = max(1, -(-len(_wrap(cue.text)) // CAPTION_LINES))
        # Never split so far that a piece would flash.
        while parts > 1 and span / parts < MIN_CUE:
            parts -= 1
        chunks = _split_evenly(cue.text, parts)
        total = max(sum(len(c) for c in chunks), 1)
        clock = cue.start
        for position, chunk in enumerate(chunks):
            last = position == len(chunks) - 1
            stop = cue.end if last else clock + span * (len(chunk) / total)
            number += 1
            blocks += [str(number),
                       f"{_timestamp(clock)} --> {_timestamp(stop)}",
                       "\n".join(_wrap(chunk)), ""]
            clock = stop
    out.write_text("\n".join(blocks), encoding="utf-8")
    return out


def write_transcript(video, timings: list[CueTiming], out: Path) -> Path:
    """The text alternative. A student who cannot or will not watch reads this
    and misses nothing, which is what WCAG 1.2.3 is actually asking for."""
    lines = [f"# {video.title}", "",
             f"A text version of the {video.kind} video. Every word spoken, in order.", ""]
    for scene, group in _group_by_scene(video, timings):
        if scene.type == "slide":
            heading = (scene.heading or scene.body).replace("\n", " ").strip()
            lines.append(f"## {heading}" if heading else "## Slide")
            if scene.diagram:
                # The whole reason alt is required. A reader of the transcript
                # gets the picture described, in place, rather than a gap where
                # the diagram was.
                lines += ["", f"*Diagram: {scene.diagram.alt}*", ""]
                labels = [n.label + (f", {n.sub}" if n.sub else "")
                          for n in ([scene.diagram.source] if scene.diagram.source else [])
                          + scene.diagram.parts]
                if labels:
                    lines += [f"- {label}" for label in labels] + [""]
                if scene.diagram.loop:
                    lines += [f"- Return path: {scene.diagram.loop}", ""]
            if scene.body:
                # 61 slides across the library carried body text that the
                # transcript silently dropped, including the eight report
                # headings a student is graded on. The transcript is the
                # alternative to watching, so anything on the slide belongs in
                # it. Code layouts keep their fencing so the literal survives.
                if scene.layout == "code":
                    lines += ["", "```", scene.body, "```", ""]
                else:
                    lines += ["", *[f"> {line}" for line in scene.body.splitlines()], ""]
            if scene.items:
                # A compare slide stores its two halves as "Label | Text". On
                # screen those become separate panels, so the transcript has to
                # split them too. Left alone, the reader gets a raw pipe
                # character in the middle of a sentence, in the one artifact
                # that exists for people who are not watching.
                rendered = []
                for i, item in enumerate(scene.items, 1):
                    label, sep, rest = str(item).partition("|")
                    rendered.append(f"{i}. **{label.strip()}.** {rest.strip()}"
                                    if sep else f"{i}. {item}")
                lines += ["", *rendered, ""]
        else:
            lines.append("## At the terminal")
            lines += ["", "Commands run, in order:", ""]
            lines += [f"- `{step['run']}`" for step in scene.steps]
            lines.append("")
        lines += [" ".join(c.text for c in group), ""]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def _group_by_scene(video, timings: list[CueTiming]):
    position = 0
    for scene in video.scenes:
        count = len(scene.cues)
        yield scene, timings[position:position + count]
        position += count


def build_narration(video, cache, work: Path) -> tuple[Path, list[CueTiming], list[list[float]]]:
    """Speak every cue, measure it, and lay them end to end."""
    work.mkdir(parents=True, exist_ok=True)
    timings: list[CueTiming] = []
    per_scene: list[list[float]] = []
    pieces: list[Path] = []
    clock = 0.0
    index = 0

    for scene in video.scenes:
        durations = []
        for cue in scene.cues:
            wav, spoken, _ = cache.speak(cue.text)
            padded = work / f"cue{index:03d}.wav"
            # The pause after a line is part of that line's slot, so a slide
            # does not swap the instant a sentence ends.
            _run(["ffmpeg", "-y", "-v", "error", "-i", str(wav),
                  "-af", f"apad=pad_dur={cue.hold}", "-c:a", "pcm_s16le", str(padded)])
            total = spoken + cue.hold
            timings.append(CueTiming(index, cue.text, clock, clock + spoken))
            clock += total
            durations.append(total)
            pieces.append(padded)
            index += 1
        per_scene.append(durations)

    listing = work / "narration.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in pieces), encoding="utf-8")
    narration = work / "narration.wav"
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", listing.name, "-c", "copy", narration.name], cwd=work)
    return narration, timings, per_scene


def build_visual(video, per_scene: list[list[float]], work: Path, labs: Path,
                 use_docker: bool = True) -> tuple[Path, list[Path]]:
    """One silent video track: stills held to their cues, recordings inline."""
    segments: list[Path] = []
    ascii_captures: list[Path] = []

    for number, (scene, durations) in enumerate(zip(video.scenes, per_scene)):
        stem = f"scene{number:02d}"
        if scene.type == "slide":
            reveal_for = []
            current = len(scene.items) if not any(c.reveal is not None for c in scene.cues) else 0
            for cue in scene.cues:
                if cue.reveal is not None:
                    current = cue.reveal
                reveal_for.append(current)
            for state in sorted(set(reveal_for)):
                slides.render_png(scene, state, work / f"{stem}-r{state}.png")
            # One clip per cue, at an exact frame count taken off a running
            # clock. Not a concat listing of `duration` directives.
            #
            # The obvious approach is a concat file with one `duration` per
            # still and a trailing repeat of the last image. ffmpeg 9's concat
            # demuxer does not honour that the way it reads: a scene asking for
            # 8.0s of stills came out 4.7 to 7.5s longer, and across a video the
            # picture track ran 289s against 231s of narration. Every slide sat
            # late, the closing slide never appeared, and the mux's -shortest
            # trimmed the tail so the total duration still looked correct. All
            # ten gates passed. It was found by pulling a frame and seeing the
            # wrong slide.
            #
            # Deriving each clip's length from a cumulative total, rather than
            # rounding each cue independently, keeps rounding error from
            # accumulating across a long scene.
            clips: list[str] = []
            elapsed = 0.0
            for index, (reveal, seconds) in enumerate(zip(reveal_for, durations)):
                start_frame = round(elapsed * FPS)
                elapsed += seconds
                frames = max(1, round(elapsed * FPS) - start_frame)
                clip = f"{stem}-c{index:03d}.mp4"
                _run(["ffmpeg", "-y", "-v", "error",
                      "-loop", "1", "-framerate", str(FPS),
                      "-i", f"{stem}-r{reveal}.png",
                      "-frames:v", str(frames), "-r", str(FPS),
                      "-c:v", "libx264", "-preset", "slow", "-crf", CRF,
                      "-tune", "stillimage", "-pix_fmt", "yuv420p",
                      "-g", str(FPS * 2), clip], cwd=work)
                clips.append(clip)
            listing = work / f"{stem}.txt"
            listing.write_text("".join(f"file '{c}'\n" for c in clips), encoding="utf-8")
            segment = work / f"{stem}.mp4"
            _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                  "-i", listing.name, "-c", "copy", segment.name], cwd=work)
            shown = probe_duration(segment)
            spoken = sum(durations)
            if abs(shown - spoken) > 0.15:
                raise RuntimeError(
                    f"{video.id} scene {number + 1}: the stills run {shown:.2f}s but "
                    f"their narration runs {spoken:.2f}s. They have to match, because "
                    f"nothing downstream can tell that a slide is late.")
        else:
            tape_file = tape_mod.write_tape(scene, work, stem)
            raw, ascii_path = tape_mod.render(tape_file, work, labs, use_docker=use_docker,
                                              setup=scene.setup)
            ascii_captures.append(ascii_path)
            spoken = sum(durations)
            shown = probe_duration(raw)
            drift = abs(shown - spoken) / max(spoken, 0.001)
            if drift > MAX_DRIFT:
                raise RuntimeError(
                    f"{video.id} scene {number + 1}: the recording runs {shown:.1f}s but its "
                    f"narration runs {spoken:.1f}s, a {drift:.0%} mismatch.\n"
                    f"  Past {MAX_DRIFT:.0%} the words stop describing what is on screen.\n"
                    f"  Either change the narration length or change the step timings.")
            segment = work / f"{stem}.mp4"
            if spoken > shown:
                # Hold the last frame rather than slowing the recording down,
                # which would make the typing look wrong.
                _run(["ffmpeg", "-y", "-v", "error", "-i", raw.name,
                      "-vf", f"tpad=stop_mode=clone:stop_duration={spoken - shown:.3f}",
                      "-r", str(FPS), "-c:v", "libx264", "-preset", "slow",
                      "-crf", CRF, "-pix_fmt", "yuv420p", segment.name], cwd=work)
            else:
                _run(["ffmpeg", "-y", "-v", "error", "-i", raw.name, "-t", f"{spoken:.3f}",
                      "-r", str(FPS), "-c:v", "libx264", "-preset", "slow",
                      "-crf", CRF, "-pix_fmt", "yuv420p", segment.name], cwd=work)
        segments.append(segment)

    listing = work / "segments.txt"
    listing.write_text("".join(f"file '{s.name}'\n" for s in segments), encoding="utf-8")
    silent = work / "visual.mp4"
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", listing.name, "-c", "copy", silent.name], cwd=work)
    return silent, ascii_captures


def _measure_loudness(source: Path) -> dict:
    """First loudnorm pass. Returns what the second pass needs."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(source),
         "-af", f"loudnorm={LOUDNESS_TARGET}:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    tail = result.stderr[result.stderr.rfind("{"):result.stderr.rfind("}") + 1]
    try:
        return json.loads(tail)
    except ValueError:
        return {}


def mux(silent: Path, narration: Path, out: Path) -> Path:
    """One MP4, loudness normalised, ready to stream from Canvas.

    Two passes, not one. Single pass loudnorm is a dynamic normaliser that does
    not know what is coming, and the first build of this came out at a mean of
    -17.2 dB with peaks at 0.0 dBFS, which is clipping. Measuring first and then
    applying the measurement hits the target and respects the true peak ceiling.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    # -shortest below will happily trim a too-long picture track and produce a
    # file whose duration looks right while every slide inside it is late. So
    # the two tracks are compared before they are joined.
    picture, spoken = probe_duration(silent), probe_duration(narration)
    if abs(picture - spoken) > 0.5:
        raise RuntimeError(
            f"the picture track is {picture:.2f}s and the narration is {spoken:.2f}s, "
            f"a {picture - spoken:+.2f}s difference.\n"
            f"  Joining these would slide every scene out of sync, and -shortest "
            f"would hide it by trimming the tail.")
    measured = _measure_loudness(narration)
    if measured:
        filt = (f"loudnorm={LOUDNESS_TARGET}"
                f":measured_I={measured['input_i']}"
                f":measured_TP={measured['input_tp']}"
                f":measured_LRA={measured['input_lra']}"
                f":measured_thresh={measured['input_thresh']}"
                f":offset={measured.get('target_offset', 0)}"
                f":linear=true:print_format=summary")
    else:
        filt = f"loudnorm={LOUDNESS_TARGET}"
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(silent), "-i", str(narration),
          "-af", filt,
          "-c:v", "copy", "-c:a", "aac", "-b:a", AUDIO_BITRATE, "-ac", "1", "-ar", "44100",
          "-movflags", "+faststart", "-shortest", str(out)])
    return out


def poster(silent: Path, out: Path, at: float = 0.6) -> Path:
    """A still for the player before it is pressed. Without one the browser
    shows a black rectangle, which reads as broken."""
    _run(["ffmpeg", "-y", "-v", "error", "-ss", str(at), "-i", str(silent),
          "-frames:v", "1", "-q:v", "3", str(out)])
    return out


def write_manifest(video, out_dir: Path, timings: list[CueTiming], mp4: Path) -> Path:
    """What the cartridge and the gates read instead of re-deriving anything."""
    payload = {
        "id": video.id, "title": video.title, "kind": video.kind,
        "module": video.module, "embed_on": video.embed_on, "blurb": video.blurb,
        "voice": video.voice, "explains": video.explains,
        "duration": probe_duration(mp4),
        "bytes": mp4.stat().st_size,
        "words": video.words,
        "commands": video.commands,
        "cues": [asdict(c) for c in timings],
    }
    path = out_dir / f"{video.id}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
