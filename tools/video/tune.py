"""Pre-compute settle times so a walkthrough builds in one or two rounds.

    ITSY_CONTENT=content/funded python3 -m tools.video.tune --id w1-walkthrough
    ITSY_CONTENT=content/funded python3 -m tools.video.tune --id w1-walkthrough --write

WHY THIS EXISTS. Every terminal scene has two clocks: the recording runs at
whatever the tape and machine produce, and the narration runs at whatever the
voice produces. The build fails past a 25 per cent mismatch, which is the right
gate, because past that the words stop describing what is on screen.

Getting there by rebuilding, reading the failure and adjusting one number cost
five rounds on the first walkthrough at roughly two minutes a round. The
relationship is predictable enough to solve up front instead:

    narration  ~= words / WPS
    recording  ~= typing + a pause before Enter + how long the command runs
                  + settle

so the settle that lands them together is just that rearranged. The constants
below were measured from real builds in this repository rather than guessed,
and they are approximate on purpose: the point is to start inside the gate and
let one rebuild finish the job, not to predict to the millisecond.

VHS does not honour Sleep as a clock either, which is the other reason not to
chase exactness here. A ten second sleep measures around nine and a half and
varies with load.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# Measured across the first two walkthroughs in this repository.
WORDS_PER_SECOND = 2.6      # Kokoro at the configured voice
TYPING_SECONDS_PER_CHAR = 0.055   # Set TypingSpeed 55ms in tape.py
PRE_ENTER_PAUSE = 0.45
SHELL_OVERHEAD = 0.6        # prompt redraw, capture settling

# How long a command itself takes before output lands. Anything not matched
# here is assumed instant, which is true of ls, wc, cut and friends.
RUNTIME_HINTS = (
    (re.compile(r"agent\.cli|harness\.runner"), 12.0),
    (re.compile(r"target\.seed"), 2.0),
    (re.compile(r"agent\.replay"), 1.2),
    (re.compile(r"curl"), 0.8),
)

MIN_SETTLE = 2.0
MAX_SETTLE = 16.0


def _narration_words(scene: dict) -> int:
    total = 0
    for cue in scene.get("narration") or []:
        text = cue if isinstance(cue, str) else cue.get("text", "")
        total += len(str(text).split())
    return total


def _command_runtime(command: str) -> float:
    for pattern, seconds in RUNTIME_HINTS:
        if pattern.search(command):
            return seconds
    return 0.0


def suggest(scene: dict) -> list[float]:
    """One settle per step, so the scene's recording matches its narration."""
    steps = scene.get("steps") or []
    if not steps:
        return []
    target = _narration_words(scene) / WORDS_PER_SECOND
    fixed = 0.0
    for step in steps:
        command = str(step.get("run", ""))
        fixed += (len(command) * TYPING_SECONDS_PER_CHAR
                  + PRE_ENTER_PAUSE + SHELL_OVERHEAD
                  + _command_runtime(command))
    slack = max(0.0, target - fixed)
    each = slack / len(steps)
    return [round(min(MAX_SETTLE, max(MIN_SETTLE, each)), 1) for _ in steps]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--id", required=True)
    parser.add_argument("--write", action="store_true",
                        help="Apply the suggestions to the scene list.")
    args = parser.parse_args(argv)

    from tools.video import config
    cfg = config.load()
    path = cfg.video_dir / f"{args.id}.yaml"
    if not path.exists():
        print(f"No scene list at {path}")
        return 1

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    changed = 0
    for index, scene in enumerate(raw.get("scenes") or []):
        if scene.get("type") != "terminal":
            continue
        settles = suggest(scene)
        words = _narration_words(scene)
        for step, settle in zip(scene.get("steps") or [], settles):
            command = str(step.get("run", ""))
            old = step.get("settle")
            print(f"  scene {index + 1:>2}  {words:>3}w -> "
                  f"{words / WORDS_PER_SECOND:>5.1f}s narration   "
                  f"settle {old} -> {settle}   {command[:44]}")
            if args.write and old != settle:
                pattern = re.compile(
                    r"(- run: " + re.escape(command) + r"\n(?:.*\n)*?\s*settle: )[0-9.]+")
                text, count = pattern.subn(rf"\g<1>{settle}", text, count=1)
                changed += count

    if args.write and changed:
        path.write_text(text, encoding="utf-8")
        print(f"\n  wrote {changed} settle value(s) to {path.name}")
    elif args.write:
        print("\n  nothing to change")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
