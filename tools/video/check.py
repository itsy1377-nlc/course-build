"""Gates for the video library. Every one exists because something went wrong.

    python -m tools.video.check

Runs as preflight gate 7. Each check is phrased as the failure it prevents,
and each one reads a real artifact rather than an intention: the captured
terminal text, the rendered stylesheet, the built file sizes, the manifest.
"""

from __future__ import annotations

import os
import json
import re
import subprocess
import sys
from pathlib import Path

from . import schema

from . import config as _config

_CFG = _config.load()
ROOT = _CFG.root
BUILD = _CFG.build_dir
LABS = _CFG.code_dir or ROOT

# Canvas default course quota is 500 MB (DEFAULT_STORAGE_QUOTA in the Canvas
# source, and confirmed on the live account). Fail well below it so an import
# fails here rather than at the college.
LIBRARY_BUDGET_MB = _CFG.library_budget_mb

# Anything that would put a graded answer on screen. Data files are fine and
# are the point of a walkthrough: the evidence step reads runs/ledger.jsonl and
# the outbox. Source files are not.
READERS = ("cat", "less", "more", "head", "tail", "bat", "vim", "vi", "nano",
           "code", "open", "diff", "sed", "awk")
SOURCE_SUFFIXES = (".py",)

# Modules that come from the environment rather than from the course's own
# code. The command gate rejected `python -m pytest`, which is the exact command
# the assignments tell students to run, so a correct walkthrough failed a gate
# for doing the right thing. tools/verify_content.py already keeps this
# allowlist for pages; the same rule has to apply to commands on camera.
INSTALLED_MODULES = {"pytest", "venv", "pip", "http.server", "json.tool", "unittest"}

CONTRAST_PAIRS = [("--ink", "--ground", 7.0), ("--mute", "--ground", 4.5),
                  ("--accent", "--ground", 4.5)]


def _fail(problems: list[str], message: str) -> None:
    problems.append(message)


def _luminance(hex_colour: str) -> float:
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = channel(r), channel(g), channel(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    high, low = max(la, lb), min(la, lb)
    return (high + 0.05) / (low + 0.05)


def check_contrast(problems: list[str]) -> None:
    """A palette edit must not quietly drop the slides below WCAG AA."""
    css = (schema.VIDEO_DIR / "theme.css").read_text(encoding="utf-8")
    values = dict(re.findall(r"(--[a-z]+):\s*(#[0-9a-fA-F]{6})", css))
    for foreground, background, minimum in CONTRAST_PAIRS:
        if foreground not in values or background not in values:
            _fail(problems, f"theme.css no longer defines {foreground} or {background}")
            continue
        ratio = contrast(values[foreground], values[background])
        if ratio < minimum:
            _fail(problems, f"theme.css: {foreground} on {background} is {ratio:.1f}:1, "
                            f"below the {minimum}:1 this course holds itself to")


def check_embedded(videos: list[schema.Video], problems: list[str]) -> None:
    """Every ::: video block resolves, and every scene list is actually used."""
    known = {v.id: v for v in videos}
    embedded: set[str] = set()
    # Only this course tree. Scanning all of content/ made the constrained
    # run fail on a funded page and the reverse, because each course has
    # its own videos and its own pages.
    for page in sorted((ROOT / os.environ.get("ITSY_CONTENT", "content"))
                       .rglob("*.md")):
        for video_id in schema.embedded_ids(page.read_text(encoding="utf-8")):
            embedded.add(video_id)
            if video_id not in known:
                _fail(problems, f"{page.relative_to(ROOT)} embeds video '{video_id}', "
                                f"and there is no content/video/{video_id}.yaml")
    for video in videos:
        if video.id not in embedded:
            _fail(problems, f"{video.id} is built but no page embeds it. Add a "
                            f"::: video block to {video.embed_on}, or delete the scene list.")


def check_built(videos: list[schema.Video], problems: list[str]) -> None:
    """A page promising a video that was never built is a broken player."""
    for video in videos:
        for suffix in (".mp4", ".vtt", ".jpg", ".json", ".transcript.md"):
            artifact = BUILD / f"{video.id}{suffix}"
            if not artifact.exists():
                _fail(problems, f"{video.id}: {artifact.name} is missing. Run "
                                f"python -m tools.video.build --id {video.id}")


def check_freshness(videos: list[schema.Video], problems: list[str]) -> None:
    """Edit the page and the video that explains it is stale, by name."""
    from .build import fingerprint
    for video in videos:
        manifest = BUILD / f"{video.id}.json"
        if not manifest.exists():
            continue
        stored = json.loads(manifest.read_text()).get("fingerprint")
        if stored != fingerprint(video):
            explains = ", ".join(video.explains) or "its scene list"
            _fail(problems, f"{video.id} is out of date with {explains}. Rebuild it.")


def check_captions(videos: list[schema.Video], problems: list[str]) -> None:
    """Captions have to cover the audio, or the video is not AA."""
    for video in videos:
        vtt, mp4 = BUILD / f"{video.id}.vtt", BUILD / f"{video.id}.mp4"
        if not (vtt.exists() and mp4.exists()):
            continue
        stamps = re.findall(r"(\d\d):(\d\d):(\d\d\.\d+) --> (\d\d):(\d\d):(\d\d\.\d+)",
                            vtt.read_text(encoding="utf-8"))
        if not stamps:
            _fail(problems, f"{video.id}.vtt has no cues")
            continue
        last = sum(x * y for x, y in zip((3600, 60, 1), map(float, stamps[-1][3:])))
        duration = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(mp4)],
            capture_output=True, text=True).stdout.strip() or 0)
        if duration - last > 3.0:
            _fail(problems, f"{video.id}: captions stop at {last:.1f}s but the video "
                            f"runs {duration:.1f}s. {duration - last:.1f}s is uncaptioned.")


def _code_lines(path) -> list[str]:
    """The real source lines of an answer file, whatever it is stored in.

    A .py file is its own source. A notebook is JSON, and reading it as text
    yields lines like `    "def build_facts(parsed):\n",` which carry escaped
    newlines and wrapping quotes. Nothing on a slide or in a terminal can ever
    equal one of those, so a gate comparing against them cannot fire, and it
    reports clean because it found nothing rather than because nothing leaked.

    Measured on this course: 3,265 of 3,265 lines extracted from the seven
    solution notebooks were in JSON string form. The notebooks have to be
    decoded, so they are.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix != ".ipynb":
        return text.splitlines()
    try:
        notebook = json.loads(text)
    except ValueError:
        return text.splitlines()
    out: list[str] = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source")
        if isinstance(source, list):
            out.extend("".join(source).splitlines())
        elif isinstance(source, str):
            out.extend(source.splitlines())
    return out


def _solution_lines() -> set[str]:  # noqa: D401
    """Every distinctive line of the worked solution and the extension points."""
    lines: set[str] = set()
    for path in _CFG.answer_files():
        for line in _code_lines(path):
            stripped = line.strip()
            # Short or comment-only lines match by accident. A real leak is
            # a substantial line of code.
            if len(stripped) >= 24 and not stripped.startswith("#"):
                lines.add(stripped)
    return lines


def check_answer_globs(problems: list[str]) -> None:
    """Every answer pattern has to find its files, or the gate below is blind.

    check_no_spoilers compares the captured screen against the lines in the
    answer files. A pattern that matches nothing contributes no lines, and the
    gate then passes because there was nothing to find rather than because
    nothing leaked. Those two look identical in the output, so they are told
    apart here instead.
    """
    missing = _CFG.unmatched_answer_globs()
    if missing:
        _fail(problems, "answer_globs match no files: " + ", ".join(missing)
              + ". The no-spoiler gate reads those files, so it is checking "
                "less than the config says it is.")
    if not _CFG.answer_files():
        _fail(problems, "no answer files at all, so the no-spoiler gate cannot fire")


def check_no_spoilers(videos: list[schema.Video], problems: list[str]) -> None:
    """Nothing a student is graded on may appear on screen.

    Reads the .ascii capture VHS writes from the same render as the video, so
    this is a substring test over text that was genuinely on camera rather than
    a guess about what the tape might print. Setup runs outside the tape, so a
    hit here is a real hit.

    Worth being straight about what this does and does not guarantee. The
    .ascii is a sequence of frame snapshots, not a full scrollback, so output
    that scrolls past between two captured frames can be missed. That makes
    this check sound when it fires and not airtight when it passes.

    The guarantee comes from check_no_readers instead, which is static analysis
    of the tape: if no command on camera can print source in the first place,
    scrolling cannot leak it. Treat that as the control and this as defence in
    depth against output nobody predicted.
    """
    solution = _solution_lines()
    if not solution:
        if _CFG.answer_globs_declared and not _CFG.answer_globs:
            # answer_globs is present in the config and empty. That is the
            # deliberate "this course has no work students hand in as files"
            # declaration, so there is genuinely nothing to compare against and
            # nothing that could leak. A course with no code is the normal case
            # for this: no answer files, and no terminal scenes to show them in.
            return
        # A gate that cannot see anything must not report success. Without
        # answer_globs this check would pass on every video forever while
        # looking exactly like a check that ran.
        _fail(problems,
              "the no spoiler gate has nothing to compare against. Set answer_globs "
              "in content/video/config.yaml to the files holding work students are "
              "supposed to produce themselves, or set it to [] deliberately if this "
              "course has none. "
              + (f"It is set to {_CFG.answer_globs} and those patterns match no files."
                 if _CFG.answer_globs else "It is not set at all."))
        return
    for video in videos:
        manifest = BUILD / f"{video.id}.json"
        if not manifest.exists():
            continue
        for name in json.loads(manifest.read_text()).get("ascii", []):
            capture = BUILD / name
            if not capture.exists():
                _fail(problems, f"{video.id}: {name} is missing, and it is the file "
                                f"the no-spoiler gate reads. The gate cannot pass.")
                continue
            text = capture.read_text(encoding="utf-8", errors="ignore")
            for line in solution:
                if line in text:
                    _fail(problems, f"{video.id}: {name} shows a line from the worked "
                                    f"solution on screen:\n      {line[:80]}")
                    break


def check_no_readers(videos: list[schema.Video], problems: list[str]) -> None:
    """A walkthrough may read data files on camera. Never source."""
    for video in videos:
        for command in video.commands:
            for part in re.split(r"[|;&]", command):
                words = part.split()
                if not words:
                    continue
                if words[0] in READERS and any(
                        argument.endswith(SOURCE_SUFFIXES) or ".py" in argument
                        for argument in words[1:]):
                    _fail(problems, f"{video.id} runs `{part.strip()}` on camera. "
                                    f"Reading source on screen hands over the answer.")


# The identifiers a course uses for the cases a lab collects. The first is the
# A1..A6 / control naming two courses in this repository use. The second and
# third are ITSY 1377's corpus emails, which appear either as a full slug
# (013-vetchmoor-census-correction) or as prose (email 018, emails 001 and 004).
# A gate that knows only one course's naming reports clean on every other
# course, which is what happened here: the A1..A6 pattern matches nothing in
# ITSY 1377, so this check had never examined anything.
_CASE_PATTERNS = [
    re.compile(r"\b((?:A[1-6]|control)-[a-z0-9-]+)"),
    re.compile(r"\b(\d{3}-[a-z][a-z0-9-]{2,})\b"),
]
_EMAIL_PROSE = re.compile(r"\bemails?\s+((?:\d{3})(?:\s*(?:,|and|or)\s*\d{3})*)",
                          re.IGNORECASE)


def _cases(text: str) -> set[str]:
    """Every case identifier in a piece of text, normalised to its number."""
    found: set[str] = set()
    for pattern in _CASE_PATTERNS:
        for hit in pattern.findall(text):
            found.add(hit.split("-")[0] if hit[:3].isdigit() else hit)
    for run in _EMAIL_PROSE.findall(text):
        found.update(re.findall(r"\d{3}", run))
    return found


def _demonstrated_text(video: schema.Video) -> str:
    """What a walkthrough actually DEMONSTRATES, which is not what it mentions.

    The distinction is the whole check. "The fence record for email 013 is
    there" is an instruction to look at your own export file; it does not run
    013. Counting a mention as a demonstration fails a video for telling the
    student what to check, which is what a walkthrough is for.

    So: anything typed on camera, plus the body of a code scene and the items
    of a compare scene, which are where a walkthrough shows output. Narration
    and numbered checklists are excluded, because that is where a video names
    a case rather than running it.
    """
    parts: list[str] = list(video.commands)
    for scene in video.scenes:
        if scene.layout in ("code", "compare"):
            parts.append(scene.body)
            parts += scene.items
    return "\n".join(p for p in parts if p)


def _run_record_case(video: schema.Video) -> set[str]:
    """The case a walkthrough's recorded run used, when the course records one.

    This course writes content/video/runs/wN.json when it produces the real
    run a walkthrough shows. That file names the email, so it is the plainest
    possible answer to "what does this video demonstrate" and it beats reading
    the slides. Courses that record nothing fall back to the slides.
    """
    match = re.match(r"^(w\d)-", video.id)
    if not match:
        return set()
    path = schema.VIDEO_DIR / "runs" / f"{match.group(1)}.json"
    if not path.exists():
        return set()
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return set()
    # The run records were written by five different agents and carry the case
    # under four different keys. A reader that knows one of them silently falls
    # back to scanning slides, which is a weaker check that then passes by
    # luck. Look under all of them, and say nothing rather than guess.
    email = record.get("email_id")
    if not email:
        held = record.get("email") or record.get("featured_email")
        if isinstance(held, str):
            email = held
        elif isinstance(held, dict):
            email = held.get("corpus_id") or held.get("id")
    email = str(email or "").strip()
    return {email.split("-")[0]} if email else set()


def check_not_own_assignment(videos: list[schema.Video], problems: list[str]) -> None:
    """A walkthrough must not demonstrate the cases its own assignment collects."""
    for video in videos:
        if video.kind != "walkthrough":
            continue
        page = ROOT / video.embed_on
        if not page.exists():
            continue
        assigned = _cases(page.read_text(encoding="utf-8"))
        shown = _run_record_case(video) or _cases(_demonstrated_text(video))
        overlap = assigned & shown
        if overlap:
            _fail(problems, f"{video.id} demonstrates {', '.join(sorted(overlap))}, which "
                            f"{video.embed_on} asks the student to run and submit.\n"
                            f"      Demonstrate a case the assignment does not collect.")


def check_commands_resolve(videos: list[schema.Video], problems: list[str]) -> None:
    """A command typed on camera has to exist, the same rule pages already follow.

    Two ways this reported "ok" while checking nothing. It matched only
    `python -m`, so a scene running `python lab.py` was invisible to it; and
    every scene list in this course is slides, so the loop body never ran at
    all. Neither was distinguishable from a pass. It now says which case it is
    and understands both command shapes.
    """
    module_re = re.compile(r"python\s+-m\s+([a-zA-Z0-9_.]+)")
    script_re = re.compile(r"python[0-9.]*\s+([a-zA-Z0-9_./-]+\.py)")
    where = LABS.name if LABS.name else str(LABS)
    checked = 0
    for video in videos:
        for command in video.commands + video.hidden_commands:
            for module in module_re.findall(command):
                if module.split(".")[0] in INSTALLED_MODULES:
                    continue
                checked += 1
                relative = Path(module.replace(".", "/"))
                if not ((LABS / relative).with_suffix(".py").exists()
                        or (LABS / relative / "__init__.py").exists()
                        or (LABS / relative).is_dir()):
                    _fail(problems, f"{video.id} runs `python -m {module}`, which does "
                                    f"not resolve in {where}/")
            for script in script_re.findall(command):
                checked += 1
                if not (LABS / script).exists() and not any(LABS.rglob(Path(script).name)):
                    _fail(problems, f"{video.id} runs `python {script}`, which does "
                                    f"not resolve in {where}/")
    if not checked:
        print(f"  (no commands are typed on camera in {len(videos)} scene list(s): "
              f"nothing to resolve)")


def check_size(videos: list[schema.Video], problems: list[str]) -> None:
    """Import limits should fail here, not at the college."""
    built = list(BUILD.glob("*.mp4"))
    total = sum(p.stat().st_size for p in built) / 1e6
    if total > LIBRARY_BUDGET_MB:
        biggest = sorted(built, key=lambda p: -p.stat().st_size)[:3]
        listing = ", ".join(f"{p.name} {p.stat().st_size / 1e6:.0f} MB" for p in biggest)
        _fail(problems, f"the video library is {total:.0f} MB, over the {LIBRARY_BUDGET_MB} MB "
                        f"budget against a 500 MB Canvas course quota.\n      Largest: {listing}")


def main(argv: list[str] | None = None) -> int:
    try:
        videos = schema.load_all()
    except schema.SceneError as error:
        print(f"scene list error:\n  {error}", file=sys.stderr)
        return 1

    if not videos:
        print("no videos declared, nothing to check")
        return 0

    problems: list[str] = []
    checks = [
        ("palette holds WCAG AA", lambda: check_contrast(problems)),
        ("every ::: video block resolves", lambda: check_embedded(videos, problems)),
        ("every declared video is built", lambda: check_built(videos, problems)),
        ("no video is stale against its page", lambda: check_freshness(videos, problems)),
        ("captions cover the audio", lambda: check_captions(videos, problems)),
        ("answer files the no-spoiler gate reads all exist", lambda: check_answer_globs(problems)),
        ("no solution source on screen", lambda: check_no_spoilers(videos, problems)),
        ("no reader run against source", lambda: check_no_readers(videos, problems)),
        ("no walkthrough runs its own cases", lambda: check_not_own_assignment(videos, problems)),
        ("commands typed on camera resolve", lambda: check_commands_resolve(videos, problems)),
        ("library fits the course quota", lambda: check_size(videos, problems)),
    ]
    for label, run in checks:
        before = len(problems)
        run()
        status = "ok" if len(problems) == before else "FAIL"
        print(f"  {status:4}  {label}")

    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"\n{len(videos)} video(s), all checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
