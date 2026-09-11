"""Build the course video.

    python -m tools.video.build --all              every video that is stale
    python -m tools.video.build --id w5-concept    one of them
    python -m tools.video.build --all --force      ignore the cache
    python -m tools.video.build --id x --no-docker record on the host instead

Staleness is content addressed. A video's fingerprint covers its scene list,
the theme, the slide template, the voice, and the pages it says it explains.
Change any of them and that video rebuilds; change none and nothing runs. This
is the difference between a pipeline you re-run and one you avoid re-running.

Narration is cached separately and more finely, keyed per cue, so fixing one
sentence re-speaks one sentence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

from . import assemble, schema, tts

from . import config as _config

_CFG = _config.load()
ROOT = _CFG.root
LABS = _CFG.code_dir or ROOT
BUILD = _CFG.build_dir
CACHE = _CFG.cache_dir


# The pipeline's own code is part of a video's identity. Without this, fixing a
# renderer bug left every existing video reported as current, so the fix reached
# only the videos that happened to be rebuilt for another reason. That is how a
# slide timing bug survived in one video while being fixed in another.
#
# NOT EVERY .py IN THIS DIRECTORY RENDERS A FRAME. This used to glob all of
# them, which put check.py -- the gate that *reports* staleness -- inside the
# definition of staleness. Editing the checker therefore marked all fourteen
# videos stale and demanded a full re-render for a change that could not alter
# a single pixel. On 2026-09-11 that cost a correct accessibility fix its first
# attempt, and the fix had to be moved elsewhere to avoid the re-render.
#
# A module belongs here when its output can change a built artifact. A gate
# reads artifacts and changes none.
_NOT_RENDERING = {"check.py"}
_PIPELINE = sorted(p for p in Path(__file__).parent.glob("*.py")
                   if p.name not in _NOT_RENDERING)


def _require_the_build_interpreter() -> None:
    """Fail by name when run under the wrong python.

    Queue item Q8. The build needs tools/video/.venv, which carries kokoro,
    soundfile and torch. Run under the system python and the first thing that
    happens is `ModuleNotFoundError: No module named 'soundfile'`, which reads
    as an uninstalled dependency rather than as the wrong interpreter. It cost
    one session a wrong conclusion that the build environment was gone.
    """
    try:
        import soundfile  # noqa: F401
    except ImportError:
        venv = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
        print("This is the wrong interpreter for the video build.",
              file=sys.stderr)
        if venv.exists():
            print(f"Run it with:\n    {venv} -m tools.video.build ...",
                  file=sys.stderr)
        else:
            print(f"Expected a virtualenv at {venv.parent.parent} and found "
                  f"none. See docs/lab-fix-log.md, queue item Q8.",
                  file=sys.stderr)
        raise SystemExit(2)


def fingerprint(video: schema.Video) -> str:
    parts = [p.read_bytes() for p in _PIPELINE] + [
        video.source.read_bytes(),
        (schema.VIDEO_DIR / "theme.css").read_bytes(),
        (schema.VIDEO_DIR / "slide.html.j2").read_bytes(),
        video.voice.encode(),
        # The course config sets the slide footer and the voice engine, so a
        # change to it changes every frame. Leaving it out meant editing the
        # course name rebuilt nothing.
        (schema.VIDEO_DIR / "config.yaml").read_bytes()
        if (schema.VIDEO_DIR / "config.yaml").exists() else b"",
    ]
    # The pages this video explains are part of its identity. That is what
    # makes the freshness gate possible: edit w5-content.md and the Week 5
    # video is stale by definition rather than by somebody remembering.
    for page in video.explains:
        parts.append((ROOT / page).read_bytes())
    digest = hashlib.sha256()
    for part in parts:
        digest.update(hashlib.sha256(part).digest())
    return digest.hexdigest()[:16]


def is_stale(video: schema.Video) -> bool:
    manifest = BUILD / f"{video.id}.json"
    mp4 = BUILD / f"{video.id}.mp4"
    if not (manifest.exists() and mp4.exists()):
        return True
    try:
        return json.loads(manifest.read_text()).get("fingerprint") != fingerprint(video)
    except (ValueError, OSError):
        return True


def build_one(video: schema.Video, use_docker: bool = True, keep_work: bool = False) -> dict:
    started = time.time()
    BUILD.mkdir(parents=True, exist_ok=True)
    work = CACHE / video.id
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    engine = _CFG.voice.partition(":")[0] or "kokoro"
    voice = tts.build_voice(f"{engine}:{video.voice}")
    cache = tts.NarrationCache(CACHE / "narration", voice)

    narration, timings, per_scene = assemble.build_narration(video, cache, work)
    silent, ascii_captures = assemble.build_visual(video, per_scene, work, LABS, use_docker)

    mp4 = assemble.mux(silent, narration, BUILD / f"{video.id}.mp4")
    assemble.poster(silent, BUILD / f"{video.id}.jpg")
    assemble.write_vtt(timings, BUILD / f"{video.id}.vtt")
    assemble.write_transcript(video, timings, BUILD / f"{video.id}.transcript.md")

    # The terminal text captures are what the no-spoiler gate reads. They are
    # kept next to the video rather than in the scratch directory, because a
    # gate that depends on a temporary file is a gate that stops running.
    for source in ascii_captures:
        shutil.copy2(source, BUILD / f"{video.id}.{source.name}")

    manifest_path = assemble.write_manifest(video, BUILD, timings, mp4)
    payload = json.loads(manifest_path.read_text())
    payload["fingerprint"] = fingerprint(video)
    payload["ascii"] = [f"{video.id}.{s.name}" for s in ascii_captures]
    manifest_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if not keep_work:
        shutil.rmtree(work, ignore_errors=True)
    payload["elapsed"] = time.time() - started
    return payload


def main(argv: list[str] | None = None) -> int:
    _require_the_build_interpreter()
    parser = argparse.ArgumentParser(description="Build the course instructional video.")
    parser.add_argument("--id", action="append", default=[], help="Build only this video id.")
    parser.add_argument("--all", action="store_true", help="Build every video.")
    parser.add_argument("--force", action="store_true", help="Rebuild even if fresh.")
    parser.add_argument("--no-docker", action="store_true",
                        help="Record on the host. Faster, but the shell is not the student's.")
    parser.add_argument("--keep-work", action="store_true", help="Leave intermediates for inspection.")
    args = parser.parse_args(argv)

    try:
        videos = schema.load_all()
    except schema.SceneError as error:
        print(f"scene list error:\n  {error}", file=sys.stderr)
        return 1

    if args.id:
        wanted = set(args.id)
        videos = [v for v in videos if v.id in wanted]
        missing = wanted - {v.id for v in videos}
        if missing:
            print(f"no scene list for: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
    elif not args.all:
        parser.error("pass --all or --id")

    todo = videos if args.force else [v for v in videos if is_stale(v)]
    fresh = len(videos) - len(todo)
    if fresh:
        print(f"{fresh} video(s) already current")
    if not todo:
        print("nothing to build")
        return 0

    # Keep going after a failure. Stopping at the first one meant a single
    # video over the drift threshold silently abandoned the other sixteen, and
    # the run still exited 0 because the shell only saw the last command in a
    # pipeline. Every failure is reported together at the end instead.
    failures: list[tuple[str, str]] = []
    for video in todo:
        print(f"building {video.id} ({video.words} words, {len(video.scenes)} scenes)...", flush=True)
        try:
            result = build_one(video, use_docker=not args.no_docker, keep_work=args.keep_work)
        except Exception as error:                      # noqa: BLE001
            print(f"  FAILED: {error}", file=sys.stderr)
            failures.append((video.id, str(error)))
            continue
        print(f"  {result['duration']:.1f}s of video, {result['bytes'] / 1e6:.1f} MB, "
              f"built in {result['elapsed']:.0f}s")

    built = list(BUILD.glob("*.mp4"))
    library = sum(p.stat().st_size for p in built)
    print(f"\n{len(todo) - len(failures)} built. Library: {len(built)} videos, "
          f"{library / 1e6:.0f} MB ({library / 5e8:.0%} of the 500 MB Canvas course quota).")
    if failures:
        print(f"\n{len(failures)} failed:", file=sys.stderr)
        for video_id, error in failures:
            print(f"  {video_id}: {error.splitlines()[0]}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
