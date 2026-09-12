#!/usr/bin/env python3
"""Repair and audit a term section copied from the master shell.

The shell (``canvas_id`` in course.yaml) is the only course this repo builds.
A term section is made by Canvas course copy, not by the publisher, because the
publisher rebuilds module items destructively and publishes what it touches --
see the refusal in build_course.py's main(). Course copy is the right tool and
it is not a lossless one, so this script exists to close the gap it leaves.

WHAT IT REPAIRS

1. Video poster frames. Canvas's course_copy_importer translates ``src`` and
   ``href`` but not the ``poster`` attribute, so every ``<video poster=...>``
   arrives holding an untranslated ``$CANVAS_COURSE_REFERENCE$/file_ref/<id>``
   macro that resolves to HTTP 404. Measured on 2026-09-12: 14 of 44 pages in
   the first section, 0 of 44 in the shell. The repo already documents the same
   Canvas omission on the cartridge path in tools/populate_canvas.py.

   Substituting the macro is not enough -- the ``file_ref`` route 404s too -- so
   the poster is re-derived: the shell's copy of the same page names the real
   file, and the section's own file list maps that filename to its new id.

2. The catalog description. Course copy drops ``public_description`` with no
   visual cue anywhere in Canvas, so a section can look finished and go live
   with an empty catalog blurb.

WHAT IT ONLY REPORTS

Publish state, term, dates, enrollments, license, the section's own name and
the late policy are per-term decisions, not content. This script will not guess
them. It prints them so the checklist is in front of you, and compares the
section's object counts against the shell so a partial copy is caught here
rather than by a student -- the failure that prompted all of this was a copy
that silently dropped all ten quizzes and reported success.

USAGE

    export CANVAS_BASE=... CANVAS_TOKEN=...       # and CF_ACCESS_* if gated
    python3 builder/canvas/section_fixups.py --section 10            # repair
    python3 builder/canvas/section_fixups.py --section 10 --check    # dry run

Run it after every copy. A later copy re-breaks the posters, which is the point
of it being a script rather than a note in a runbook.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_course import Canvas, CanvasError  # noqa: E402

CONTENT = HERE.parent / "content"

# The unresolved macro course copy leaves behind, e.g.
#   $CANVAS_COURSE_REFERENCE$/file_ref/g18bc557b.../download?download_frd=1
MACRO = re.compile(r'poster="(\$CANVAS_COURSE_REFERENCE\$/file_ref/[^"]*)"')
SHELL_POSTER = re.compile(r'poster="/courses/\d+/files/(\d+)/[^"]*"')
# Canvas appends a verifier to every file link when it RENDERS a page, so a body
# read back through the API carries tokens the stored body never had. Writing
# that back would bake a permission-bypassing token into the page HTML, so they
# come off before any PUT. The builder's own pages are stored without them.
VERIFIER = re.compile(r"(&amp;|&)verifier=[A-Za-z0-9]+")


def files_by_name(canvas: Canvas, course: int) -> dict[str, int]:
    """display_name -> file id, for one course."""
    out: dict[str, int] = {}
    for f in canvas.get(f"/courses/{course}/files"):
        out[f["display_name"]] = f["id"]
    return out


def names_by_id(canvas: Canvas, course: int) -> dict[int, str]:
    return {f["id"]: f["display_name"] for f in canvas.get(f"/courses/{course}/files")}


def repair_posters(canvas: Canvas, shell: int, section: int, dry: bool) -> list[str]:
    """Rewrite every unresolved poster in the section. Returns a report."""
    report: list[str] = []
    shell_names = names_by_id(canvas, shell)
    section_ids = files_by_name(canvas, section)
    shell_pages = {p["url"] for p in canvas.get(f"/courses/{shell}/pages")}

    for page in canvas.get(f"/courses/{section}/pages"):
        url = page["url"]
        body = (canvas.get(f"/courses/{section}/pages/{url}").get("body") or "")
        broken = MACRO.findall(body)
        if not broken:
            continue
        if url not in shell_pages:
            report.append(f"  SKIP {url}: {len(broken)} broken poster(s) and no such page "
                          f"in the shell, so the real file cannot be identified")
            continue
        shell_body = (canvas.get(f"/courses/{shell}/pages/{url}").get("body") or "")
        want = SHELL_POSTER.findall(shell_body)
        if len(want) != len(broken):
            # Positional matching is only sound while the two bodies agree on how
            # many posters they have. They should: the section is a copy of the
            # shell. If they do not, the section has diverged and guessing which
            # poster is which would put the wrong still frame on a video.
            report.append(f"  SKIP {url}: {len(broken)} broken poster(s) but the shell's "
                          f"copy has {len(want)} -- the page has diverged, fix it by hand")
            continue

        replacements: list[str] = []
        for shell_fid in want:
            name = shell_names.get(int(shell_fid))
            if not name:
                replacements.append("")
                continue
            sid = section_ids.get(name)
            replacements.append(
                f"/courses/{section}/files/{sid}/download?download_frd=1" if sid else "")
        if not all(replacements):
            missing = [want[i] for i, r in enumerate(replacements) if not r]
            report.append(f"  SKIP {url}: shell file id(s) {missing} have no counterpart "
                          f"in the section's files by name")
            continue

        i = iter(replacements)
        fixed = MACRO.sub(lambda _m: f'poster="{next(i)}"', body)
        fixed = VERIFIER.sub("", fixed)
        if dry:
            report.append(f"  [dry] {url}: would fix {len(broken)} poster(s) -> "
                          f"{replacements[0].rsplit('/', 2)[1]}...")
            continue
        canvas.put(f"/courses/{section}/pages/{url}", data={"wiki_page[body]": fixed})
        report.append(f"  fixed {url}: {len(broken)} poster(s)")
    return report


def repair_description(canvas: Canvas, spec: dict[str, Any], section: int, dry: bool) -> str:
    want = " ".join((spec["course"].get("description") or "").split())
    if not want:
        return "  no description in the spine, nothing to set"
    got = (canvas.get(f"/courses/{section}", **{"include[]": "public_description"})
           .get("public_description") or "")
    if got.strip() == want:
        return "  catalog description already matches the spine"
    if dry:
        return f"  [dry] would set public_description ({len(want)} chars)"
    canvas.put(f"/courses/{section}", data={"course[public_description]": want})
    return f"  set public_description ({len(want)} chars)"


def audit(canvas: Canvas, shell: int, section: int) -> tuple[list[str], list[str]]:
    """Compare the section with the shell. Returns (counts, decisions)."""
    kinds = {"quizzes": "/quizzes", "assignments": "/assignments", "pages": "/pages",
             "files": "/files", "modules": "/modules", "discussions": "/discussion_topics",
             "rubrics": "/rubrics", "outcome links": "/outcome_group_links"}
    counts = []
    for label, path in kinds.items():
        a = len(canvas.get(f"/courses/{shell}{path}"))
        b = len(canvas.get(f"/courses/{section}{path}"))
        flag = "" if a == b else "   <-- MISMATCH"
        counts.append(f"  {label:<14} shell {a:>4}   section {b:>4}{flag}")

    unpublished = [q["title"] for q in canvas.get(f"/courses/{section}/quizzes")
                   if not q.get("published")]
    if unpublished:
        counts.append(f"  unpublished quizzes in the section: {', '.join(unpublished)}")

    # Per-term container state. Reported, never set: these are decisions.
    c = canvas.get(f"/courses/{section}", **{"include[]": "term"})
    try:
        late = canvas.get(f"/courses/{section}/late_policy")
    except CanvasError:
        late = None
    # The shell's clock is authoritative: the course wording says Central and a
    # section that drifted off it would score every deadline in the wrong hour,
    # in a way nothing else reports.
    shell_tz = canvas.get(f"/courses/{shell}").get("time_zone")
    tz_flag = "" if c.get("time_zone") == shell_tz else f"   <-- shell is {shell_tz}"
    decisions = [
        f"  publish state    {c.get('workflow_state')}",
        f"  name / code      {c.get('name')!r} / {c.get('course_code')!r}",
        f"  term             {(c.get('term') or {}).get('name')}",
        f"  start / end      {c.get('start_at')} / {c.get('conclude_at')}"
        f"   (restrict to course dates: {c.get('restrict_enrollments_to_course_dates')})",
        f"  time zone        {c.get('time_zone')}{tz_flag}",
        f"  license          {c.get('license')}",
        f"  late policy      {'present' if late else 'ABSENT (Canvas default-creates one)'}",
        f"  students         {len(canvas.get(f'/courses/{section}/enrollments', **{'type[]': 'StudentEnrollment'}))}",
    ]
    return counts, decisions


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--section", type=int, required=True,
                    help="the Canvas course id of the term section to repair")
    ap.add_argument("--shell", type=int,
                    help="the master shell's course id (default: canvas_id from the spec)")
    ap.add_argument("--spec", default=str(CONTENT / "course.yaml"))
    ap.add_argument("--check", action="store_true", help="say what would change, write nothing")
    args = ap.parse_args(argv)

    base, token = os.environ.get("CANVAS_BASE"), os.environ.get("CANVAS_TOKEN")
    if not base or not token:
        sys.exit("Set CANVAS_BASE and CANVAS_TOKEN in the environment. They are never stored here.")
    spec = yaml.safe_load(Path(args.spec).read_text())
    shell = args.shell or spec["course"]["canvas_id"]
    if shell == args.section:
        sys.exit(f"--section {args.section} is the shell itself. This script repairs a COPY; "
                 f"run build_course.py against the shell instead.")

    canvas = Canvas(base, token)
    who = canvas.get("/users/self")
    print(f"Canvas {base} as {who.get('name')} (id {who.get('id')})")
    print(f"shell {shell} -> section {args.section}"
          f"{'  [dry run]' if args.check else ''}\n")

    print("video posters (course copy does not translate the poster attribute):")
    lines = repair_posters(canvas, shell, args.section, args.check)
    print("\n".join(lines) if lines else "  nothing broken")

    print("\ncatalog description (course copy drops it, with no visual cue):")
    print(repair_description(canvas, spec, args.section, args.check))

    counts, decisions = audit(canvas, shell, args.section)
    print("\nobject counts, section against shell:")
    print("\n".join(counts))
    print("\nper-term decisions, reported not set:")
    print("\n".join(decisions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
