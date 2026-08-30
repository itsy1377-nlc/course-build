"""Terminal scenes: a structured step list becomes a VHS tape, then a recording.

Authors never write raw tape syntax. They write steps, and this generates the
tape. That is not tidiness, it is what makes the recording checkable: the
commands that will appear on camera can be read out of the scene list before
anything is rendered, so verify_content can confirm they resolve in labs/ and
the spoiler gate can confirm a walkthrough is not demonstrating the very cases
its own assignment asks the student to submit.

Three things here came out of a first attempt that failed:

  0. Hide stops VHS capturing frames, but the shell keeps running and the
     screen buffer keeps its contents. Setup typed inside a Hide block still
     showed up in the .ascii capture: two frames out of nineteen held
     `python -m target.app`, `[1] 144`, and a `clear` that was sitting
     unexecuted in the input buffer while `sleep 4` blocked. So setup does not
     go in the tape at all. It runs in the container before VHS starts, which
     makes the .ascii an exact record of what was on camera and lets the
     no-spoiler gate treat any hit in it as a real hit.

  1. VHS inherits the host prompt. The first render showed `(base) %n@%m %1~`,
     which is conda's prefix plus zsh escapes that bash printed literally.
     `Set Shell bash` does not isolate this. So the prompt is set explicitly
     inside a Hide block, and the recording happens in a container where there
     are no dotfiles to inherit in the first place.

  2. `Wait+Line` matches the last line, which by the time output has printed is
     the next prompt, not the output. It times out. Waiting on output means
     `Wait+Screen`.

  3. Every tape emits a plain text capture next to the video. VHS documents
     `Output x.ascii` for CI golden files, and here it is the artifact the
     no-spoiler gate greps. Checking the video would mean reading pixels;
     checking the text is a substring test.
"""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path

from . import config as _config

ROOT = _config.find_root()

# The terminal wears the same palette as the slides, so a cut between a slide
# and a shell reads as one video rather than two. A light terminal is unusual
# and is the correct choice when the deck it sits inside is light.
THEME = {
    "name": "coursevideo",
    "background": "#faf9f7", "foreground": "#16181d",
    "cursor": "#b3261e", "selection": "#d8dbe0",
    "black": "#16181d", "red": "#b3261e", "green": "#1f6b3a", "yellow": "#8a6100",
    "blue": "#1a4f9c", "magenta": "#7a2f8a", "cyan": "#0f6f75", "white": "#16181d",
    "brightBlack": "#5c6270", "brightRed": "#b3261e", "brightGreen": "#1f6b3a",
    "brightYellow": "#8a6100", "brightBlue": "#1a4f9c", "brightMagenta": "#7a2f8a",
    "brightCyan": "#0f6f75", "brightWhite": "#16181d",
}

# How long a `wait` regex may go unmatched before the recording is abandoned,
# and how often VHS re-checks the screen.
#
# These are two different things and the syntax invites confusing them. In
# `Wait+Screen@200ms /x/` the @ is the POLL INTERVAL, not the timeout. Verified
# here: a 40 second command matched fine under @200ms. The timeout is the
# separate `Set WaitTimeout`, and it is set explicitly rather than left to the
# default so a slow test suite cannot abandon a recording.
#
# When a recording does fail on a wait, the cause is almost never the clock. It
# is a regex that never matched, usually because the text scrolled off screen or
# the output differs from what the tape expected. Match on something short and
# distinctive that stays visible.
WAIT_TIMEOUT = "90s"
WAIT_POLL = "200ms"

WIDTH, HEIGHT = 1920, 1080
# 34px fills a 1080p frame with roughly 22 rows. The first pass used 26px, which
# fits 30 rows and left a third of the frame empty under typical lab output.
# Text that fills its frame is also text that survives a phone screen.
FONT_SIZE = 34
RECORDER_IMAGE = _config.load().recorder_image

# Colima does not mount every host path into its VM. A tape directory outside a
# mounted path appears empty inside the container and VHS fails with a confusing
# "no such file" on a file that plainly exists. The pipeline keeps its working
# directories under the repo, which is mounted, and this checks rather than
# trusting that.
MOUNT_HINT = ("The recording directory is not visible inside Docker.\n"
              "  Colima only mounts some host paths. Keep video work under the "
              "repository, which is mounted, rather than under /tmp.")


class TapeError(Exception):
    pass


def _q(text: str) -> str:
    """Quote a string for a VHS tape.

    VHS has no escape sequence inside a string. `Type "grep \\"to\\""` is a parse
    error, not an escaped quote. It does accept three delimiters, so pick one
    the text does not already contain. Lab commands genuinely need this: the
    evidence step is `grep '"to"' target/outbox/*.json`, which carries both
    kinds of quote and only works inside backticks.
    """
    for delimiter in ('"', "'", "`"):
        if delimiter not in text:
            return f"{delimiter}{text}{delimiter}"
    raise TapeError(
        f"This command contains all three quote characters, and VHS has no way "
        f"to escape any of them:\n  {text}\n"
        f"  Rewrite the command, or move it into a small script the tape calls.")


def write_tape(scene, out_dir: Path, stem: str) -> Path:
    """Render one terminal scene to a .tape file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    # The raw suffix matters. The assembler pads or trims this recording to
    # match its narration and writes the result as {stem}.mp4, and ffmpeg
    # refuses when input and output are the same path.
    lines = [
        f"Output {stem}-raw.mp4",
        f"Output {stem}.ascii",
        "Set Shell bash",
        f"Set WaitTimeout {WAIT_TIMEOUT}",
        f"Set FontSize {getattr(scene, 'font_size', 0) or FONT_SIZE}",
        'Set FontFamily "JetBrains Mono"',
        f"Set Width {WIDTH}",
        f"Set Height {HEIGHT}",
        "Set Padding 40",
        "Set Margin 60",
        'Set MarginFill "#faf9f7"',
        "Set BorderRadius 12",
        "Set TypingSpeed 55ms",
        f"Set Theme {json.dumps(THEME)}",
        "",
        "# Setup runs off camera. Nothing here is ever shown.",
        "Hide",
        f"Type {_q(f'cd {scene.cwd}')}",
        "Enter",
        # A fixed two character prompt. The student's own prompt carries a
        # username and a path that differ on every machine, and a recording
        # that shows one particular person's home directory reads as somebody
        # else's screen rather than as the student's own.
        f"Type {_q(chr(39).join(['PS1=', '$ ', '']))}",
        "Enter",
        'Type "clear"',
        "Enter",
    ]
    lines += ['Type "clear"', "Enter", "Show", "Sleep 900ms", ""]

    for step in scene.steps:
        lines.append(f"Type@{step['typing']} {_q(step['run'])}")
        lines.append("Sleep 450ms")          # the beat before a person presses return
        lines.append("Enter")
        if step["wait"]:
            # Screen, not Line. Line matches the prompt that follows the output.
            lines.append(f"Wait+Screen@{WAIT_POLL} /{step['wait']}/")
        lines.append(f"Sleep {step['settle']}s")
        lines.append("")

    path = out_dir / f"{stem}.tape"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def recorder_available() -> bool:
    if not shutil.which("docker"):
        return False
    result = subprocess.run(["docker", "image", "inspect", RECORDER_IMAGE],
                            capture_output=True)
    return result.returncode == 0


def build_recorder(labs: Path, quiet: bool = True) -> None:
    """Build the recording container from the same base image students get."""
    dockerfile = Path(__file__).with_name("Dockerfile.recorder")
    command = ["docker", "build", "-f", str(dockerfile), "-t", RECORDER_IMAGE, str(labs)]
    result = subprocess.run(command, capture_output=quiet, text=True)
    if result.returncode != 0:
        raise TapeError(f"Recorder image build failed.\n{(result.stderr or '')[-1500:]}")


def render(tape: Path, out_dir: Path, labs: Path, use_docker: bool = True,
           setup: list[str] | None = None) -> tuple[Path, Path]:
    """Run a tape. Returns (mp4, ascii).

    Inside the container by default, so the shell in the video is the shell
    students actually get. The lab tree is mounted read only and copied to a
    writable /work first, because the recording runs commands that seed and
    write files and must not touch the instructor's own checkout.
    """
    stem = tape.stem
    setup = setup or []
    if use_docker:
        # Copy rather than bind mount read-write: the recording seeds a database
        # and writes to runs/, and none of that belongs in the real repository.
        # .venv and wheels are excluded because the image already has the
        # dependencies installed and copying 52 MB per scene is pure latency.
        # Newlines, not semicolons. A setup line that backgrounds a server
        # ends in "&", and "&;" is a bash syntax error rather than a sequence.
        prelude = ("\n".join(setup) + "\n") if setup else ""
        bootstrap = (
            "mkdir -p /work && "
            "tar -C /src --exclude=.git --exclude=.venv --exclude=wheels -cf - . "
            "| tar -C /work -xf - && "
            f"cd {shlex.quote(scene_cwd(tape))} 2>/dev/null || cd /work; "
            "python -m target.seed >/dev/null 2>&1; "
            f"\n{prelude}"
            f"cd /tapes && vhs {shlex.quote(tape.name)}"
        )
        command = [
            "docker", "run", "--rm",
            "-v", f"{out_dir.resolve()}:/tapes",
            "-v", f"{labs.resolve()}:/src:ro",
            "-w", "/tapes", RECORDER_IMAGE, "bash", "-c", bootstrap,
        ]
    else:
        command = ["vhs", tape.name]

    result = subprocess.run(command, cwd=out_dir, capture_output=True, text=True)
    mp4, ascii_path = out_dir / f"{stem}-raw.mp4", out_dir / f"{stem}.ascii"
    if not mp4.exists():
        combined = (result.stdout or "") + (result.stderr or "")
        hint = f"\n\n{MOUNT_HINT}" if "no such file" in combined.lower() else ""
        raise TapeError(f"VHS produced no video for {stem}.{hint}\n{combined[-1200:]}")
    if not ascii_path.exists():
        raise TapeError(
            f"{stem} rendered a video but no .ascii capture, and the no-spoiler "
            f"gate reads that file. Check the tape has an 'Output {stem}.ascii' line.")
    return mp4, ascii_path


def scene_cwd(tape: Path) -> str:
    """The working directory a tape cds into, read back out of the tape."""
    for line in tape.read_text(encoding="utf-8").splitlines():
        if line.startswith('Type "cd '):
            return line.split('cd ', 1)[1].rstrip('"')
    return "/work"
