"""The framework mapping tables, generated rather than typed.

    python -m tools.atlas_table            check every target is current
    python -m tools.atlas_table --write    regenerate them

This exists because of a specific failure. The week-to-technique table was
typed by hand into three files. They drifted apart, and two techniques ended
up claimed for week 7 that no case in the repository demonstrates, one of them
a jailbreak technique the Rules of Engagement forbid students from attempting.
The content gate did not catch it: both identifiers were listed in NAMED_ONLY
with correct explanations, and NAMED_ONLY cannot tell prose that names a
technique in order to rule it out from a table row that claims it.

So the tables are derived from the two things that cannot lie about coverage:

  * the case files, which are what a student copies an identifier out of, and
    which either run and produce evidence or do not exist;
  * content/course.yaml, which is the structural source Canvas is built from.

Names come from content/_shared/atlas-2026.07.yaml so no page has to spell a
technique by hand. A case citing an identifier absent from that file is an
error rather than a silent gap, because a name nobody has checked is exactly
how the wrong name gets copied forward.
"""

from __future__ import annotations

import os
import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / os.environ.get("ITSY_CONTENT", "content")
LABS = ROOT / "labs"
# Shared infrastructure lives at content/ root and serves both course trees.
SHARED = ROOT / "content" / "_shared"
NAMES_FILE = SHARED / "atlas-2026.07.yaml"

ATLAS_RE = re.compile(r"\bAML\.T\d{4}(?:\.\d{3})?\b")

BEGIN = "<!-- atlas:begin -->"
END = "<!-- atlas:end -->"

# Every file that shows the mapping. Adding one here is what keeps it from
# becoming a second hand-maintained copy. Two design records were dropped when
# they were archived: an archived document is a snapshot and regenerating into
# it would rewrite history.
TARGETS = (
    (CONTENT / "pages" / "framework-alignment.md", "page"),
)


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def load_names() -> tuple[str, dict[str, str]]:
    """Return the pinned release and identifier -> display name.

    A sub-technique is shown under its parent, because "Direct" on its own
    tells a reader nothing about what was direct.
    """
    raw = yaml.safe_load(NAMES_FILE.read_text(encoding="utf-8"))
    entries = raw["techniques"]
    names: dict[str, str] = {}
    for identifier, entry in entries.items():
        name = entry["name"]
        parent = entry.get("parent")
        if parent:
            name = f"{entries[parent]['name']}: {name}"
        names[identifier] = name
    return str(raw["release"]), names


def case_identifiers() -> dict[str, dict[str, list[str]]]:
    """Every identifier any case carries, and which cases carry it.

    Returns family -> identifier -> sorted case ids. The families are the four
    the content gate checks, kept together here so there is one reader of the
    case files rather than one per question asked of them.
    """
    families = {"atlas": "atlas", "owasp_llm": "owasp_llm",
                "owasp_agentic": "owasp_agentic", "cwe": "cwe"}
    out: dict[str, dict[str, list[str]]] = {f: {} for f in families}
    for folder in ("harness", "solution"):
        for path in sorted((LABS / folder / "cases").glob("*.yaml")):
            case = yaml.safe_load(path.read_text(encoding="utf-8"))
            case_id = case.get("id") or path.stem
            for field in families:
                for identifier in case.get(field) or []:
                    out[field].setdefault(identifier, []).append(case_id)
    for family in out.values():
        for identifier in family:
            family[identifier] = sorted(set(family[identifier]))
    return out


def with_parents(identifiers: set[str]) -> set[str]:
    """Add the parent of every sub-technique.

    A parent whose sub-technique is demonstrated is demonstrated: A1 proves
    AML.T0051.000 and A2 proves .001, so naming AML.T0051 is backed by
    evidence rather than excused. Kept here rather than in the gate so the
    generated tables and the gate cannot disagree about it.
    """
    return identifiers | {i.rsplit(".", 1)[0] for i in identifiers
                          if i.count(".") == 2}


def case_details() -> dict[str, dict[str, str]]:
    """case id -> the fields the evidence table shows."""
    out: dict[str, dict[str, str]] = {}
    for folder in ("harness", "solution"):
        for path in sorted((LABS / folder / "cases").glob("*.yaml")):
            case = yaml.safe_load(path.read_text(encoding="utf-8"))
            case_id = case.get("id") or path.stem
            out[case_id] = {
                "weakness": str(case.get("weakness_class") or "").strip(),
                "shipped_to_students": "yes" if folder == "harness" else "no",
            }
    return out


def weeks_from_course() -> list[tuple[int, str, list[str]]]:
    """Week, module title, and the ATLAS identifiers that module claims.

    Read from course.yaml rather than from prose, because course.yaml is what
    the cartridge is built from. A week that claims a technique here is a week
    that claims it in Canvas.
    """
    course = yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))
    rows: list[tuple[int, str, list[str]]] = []
    for module in course.get("modules") or []:
        week = module.get("week")
        if week is None:
            continue
        claimed: list[str] = []
        for entry in module.get("frameworks") or []:
            claimed += ATLAS_RE.findall(str(entry))
        if claimed:
            rows.append((int(week), str(module.get("title") or ""),
                         sorted(set(claimed))))
    return sorted(rows)


def named_only_atlas() -> tuple[dict[str, str], list[str]]:
    """ATLAS identifiers the course names but does not demonstrate.

    Imported rather than restated. The list lives in verify_content because
    that is where it is enforced; importing it late avoids a circular import,
    since verify_content calls into this module.

    Returns the ones with a pinned name, plus the ones without. An identifier
    with no pinned name is not silently dropped: it is reported under the
    table, because a technique nobody has checked the name of is precisely the
    thing that gets copied forward wrong.

    Deliberately NOT filtered by what the content currently says. The table
    replaces the text these identifiers used to live in, so reading the
    content to decide the table's rows would make the generator delete its own
    inputs on the second run.
    """
    from tools.verify_content import NAMED_ONLY
    _, names = load_names()
    named, unpinned = {}, []
    for identifier, reason in NAMED_ONLY.items():
        if not ATLAS_RE.fullmatch(identifier):
            continue
        if identifier in names:
            named[identifier] = reason
        else:
            unpinned.append(identifier)
    return named, sorted(unpinned, key=_sort_key)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _sort_key(identifier: str) -> tuple:
    parts = identifier.split(".")
    return (parts[1], parts[2] if len(parts) > 2 else "")


HEADER = """::: intro
Which security framework technique each week of this course names, and the one
authoritative spelling for each. This page is generated from the course
structure file, so it says what the course actually claims rather than what a
page remembers.
:::

"""


def build_course_only() -> str:
    """The week-claims table alone, for a course whose labs are not built yet.

    The full build() asserts that every technique a week claims is demonstrated
    by a case in the repository. That assertion is correct and stays. But the
    two rebuilt courses have no lab cases at all yet: labs/ still holds the
    previous version's code. Until those exist, the only true statement is which
    technique each week names and that nothing yet demonstrates any of them.

    Generating that, rather than typing it, is the point. The mapping drifted
    across three hand-maintained copies once already.
    """
    release, names = load_names()
    week_rows = weeks_from_course()
    claimed = sorted({i for _, _, ids in week_rows for i in ids}, key=_sort_key)
    unnamed = [i for i in claimed if i not in names]
    if unnamed:
        raise SystemExit(
            f"course.yaml names these identifiers and "
            f"{NAMES_FILE.relative_to(ROOT)} has no name for them:\n  "
            + "\n  ".join(unnamed) +
            "\n\nAdd them from the pinned release. Do not guess a name.")

    out = [BEGIN, ""]
    out.append("::: callout warning | Nothing here is demonstrated yet")
    out.append(f"This course has no lab cases built. Every technique below is "
               f"one a week **names**, taken from the course structure file, "
               f"which is what Canvas is built from. None of them is yet "
               f"backed by a case in this repository that produces evidence "
               f"for it.")
    out.append("")
    out.append("Naming a technique is legitimate. Claiming coverage of it is "
               "not, and this page will say so until the labs exist and the "
               "full generator can check each claim against a case.")
    out.append(":::")
    out.append("")
    rel = (CONTENT / "course.yaml").relative_to(ROOT).as_posix()
    out.append("::: section | Which week names which technique")
    out.append(f"Generated from `{rel}` and pinned to ATLAS "
               f"release {release}. Regenerate with "
               f"`ITSY_CONTENT={CONTENT.relative_to(ROOT).as_posix()} "
               f"python3 -m tools.atlas_table --course-only --write`.")
    out.append("")
    out.append("| Week | Module | Techniques named |")
    out.append("|---|---|---|")
    for week, title, ids in week_rows:
        joined = ", ".join(f"`{i}`" for i in ids)
        out.append(f"| {week} | {title} | {joined} |")
    out.append(":::")
    out.append("")
    out.append("::: section | The names, pinned")
    out.append("One authoritative spelling for each, so that no page has to "
               "type a technique name by hand.")
    out.append("")
    out.append("| Technique | Name |")
    out.append("|---|---|")
    for i in claimed:
        out.append(f"| `{i}` | {names[i]} |")
    out.append("")
    out.append("ATT&CK is a registered trademark of The MITRE Corporation.")
    out.append(":::")
    out.append("")
    out.append(END)
    return "\n".join(out)


def build() -> dict[str, str]:
    """Everything the targets need, rendered once."""
    release, names = load_names()
    by_family = case_identifiers()
    demonstrated = by_family["atlas"]
    details = case_details()
    missing = sorted(set(demonstrated) - set(names))
    if missing:
        raise SystemExit(
            f"These identifiers are used by a case but have no name in "
            f"{NAMES_FILE.relative_to(ROOT)}:\n  " + "\n  ".join(missing) +
            "\n\nAdd them from the pinned release. Do not guess a name.")

    week_rows = weeks_from_course()
    named, unpinned = named_only_atlas()

    # An identifier cannot be both. This caught a stale NAMED_ONLY entry for
    # AML.T0051.000 the first time it ran: A1 demonstrates it, so listing it
    # as named-only put the same technique in two tables saying opposite
    # things about whether the course covers it.
    both = sorted(set(demonstrated) & set(named), key=_sort_key)
    if both:
        raise SystemExit(
            "These identifiers are listed in NAMED_ONLY and demonstrated by a "
            "case:\n  " + "\n  ".join(both) +
            "\n\nRemove them from NAMED_ONLY in tools/verify_content.py. A "
            "case demonstrating it is the whole point of that list not "
            "applying.")

    # Every week's claim has to be backed or explicitly excused, or a module
    # could quietly claim in Canvas what no page ever says out loud.
    claimed = {i for _, _, ids in week_rows for i in ids}
    unbacked = sorted(claimed - with_parents(set(demonstrated)) - set(named),
                      key=_sort_key)
    if unbacked:
        raise SystemExit(
            "content/course.yaml claims these techniques for a module, and "
            "nothing demonstrates them:\n  " + "\n  ".join(unbacked) +
            "\n\nEither a case has to carry it, or it belongs in NAMED_ONLY "
            "with a reason.")

    def demonstrated_rows() -> list[str]:
        rows = ["| Technique | Name | Evidence | In the student repository |",
                "|---|---|---|---|"]
        for identifier in sorted(demonstrated, key=_sort_key):
            cases = demonstrated[identifier]
            shipped = "yes" if any(details[c]["shipped_to_students"] == "yes"
                                   for c in cases) else "instructor only"
            rows.append(f"| `{identifier}` | {names[identifier]} | "
                        f"{', '.join(f'`{c}`' for c in cases)} | {shipped} |")
        return rows

    def named_rows() -> list[str]:
        rows = ["| Technique | Name | Why it is named at all |", "|---|---|---|"]
        for identifier in sorted(named, key=_sort_key):
            rows.append(f"| `{identifier}` | {names[identifier]} | "
                        f"{named[identifier]} |")
        return rows

    def week_rows_md() -> list[str]:
        rows = ["| Week | Module | Techniques named |", "|---|---|---|"]
        for week, title, claimed in week_rows:
            rows.append(f"| {week} | {title} | "
                        f"{', '.join(f'`{c}`' for c in claimed)} |")
        return rows

    demonstrated_intro = (
        f"Generated from the case files and pinned to ATLAS release {release}. "
        f"A technique appears here only when a case in the repository produces "
        f"evidence for it.")
    named_intro = (
        "Naming a technique is legitimate; claiming coverage of it is not. Each "
        "one below is named on purpose, with the reason. The build fails if any "
        "of them turns up in a table that was written by hand.")
    named_footnote = (
        "Also excused, with no name pinned in "
        "`content/_shared/atlas-2026.07.yaml`, so it is named here and nowhere "
        "else until somebody reads the release: "
        + ", ".join(f"`{i}`" for i in unpinned) + ".") if unpinned else ""
    week_intro = (
        "Generated from `content/course.yaml`, which is what the Canvas course "
        "is built from, so this says what the course actually claims rather "
        "than what a page remembers.")

    sections = [
        ("ATLAS techniques this course demonstrates", demonstrated_intro,
         demonstrated_rows(), ""),
        ("ATLAS techniques this course names but does not demonstrate",
         named_intro, named_rows(), named_footnote),
        ("Which week names which technique", week_intro, week_rows_md(), ""),
    ]

    page: list[str] = []
    for heading, intro, rows, footnote in sections:
        page.append(f"::: section | {heading}")
        page.append(intro)
        page.append("")
        page += rows
        if footnote:
            page.append("")
            page.append(footnote)
        page.append(":::")
        page.append("")
    page.pop()

    doc: list[str] = []
    for heading, intro, rows, footnote in sections:
        doc.append(f"**{heading}.** {intro}")
        doc.append("")
        doc += rows
        if footnote:
            doc.append("")
            doc.append(footnote)
        doc.append("")
    doc.pop()

    md = doc
    html: list[str] = []
    html.append(f"<p><strong>Techniques this course demonstrates.</strong> "
                f"Generated from the case files, pinned to ATLAS release "
                f"{release}.</p>")
    html.append('<div class="tw"><table>')
    html.append("<thead><tr><th>Technique</th><th>Name</th><th>Evidence</th>"
                "<th>In the student repository</th></tr></thead><tbody>")
    for identifier in sorted(demonstrated, key=_sort_key):
        cases = demonstrated[identifier]
        shipped = "yes" if any(details[c]["shipped_to_students"] == "yes"
                               for c in cases) else "instructor only"
        joined = ", ".join(f"<code>{c}</code>" for c in cases)
        html.append(f"<tr><td><code>{identifier}</code></td>"
                    f"<td>{names[identifier]}</td><td>{joined}</td>"
                    f"<td>{shipped}</td></tr>")
    html.append("</tbody></table></div>")
    html.append("<p><strong>Named but not demonstrated.</strong> Listed on "
                "purpose, with the reason.</p>")
    html.append('<div class="tw"><table>')
    html.append("<thead><tr><th>Technique</th><th>Name</th>"
                "<th>Why it is named at all</th></tr></thead><tbody>")
    for identifier in sorted(named, key=_sort_key):
        html.append(f"<tr><td><code>{identifier}</code></td>"
                    f"<td>{names[identifier]}</td>"
                    f"<td>{named[identifier]}</td></tr>")
    html.append("</tbody></table></div>")
    if unpinned:
        joined = ", ".join(f"<code>{i}</code>" for i in unpinned)
        html.append(f"<p>Also excused, with no name pinned in the catalog "
                    f"subset: {joined}.</p>")
    html.append('<div class="tw"><table>')
    html.append("<thead><tr><th>Week</th><th>Module</th>"
                "<th>Techniques named</th></tr></thead><tbody>")
    for week, title, claimed in week_rows:
        joined = ", ".join(f"<code>{c}</code>" for c in claimed)
        html.append(f"<tr><td>{week}</td><td>{title}</td><td>{joined}</td></tr>")
    html.append("</tbody></table></div>")

    return {"page": "\n".join(page), "doc": "\n".join(doc),
            "html": "\n".join(html)}


# ---------------------------------------------------------------------------
# Applying
# ---------------------------------------------------------------------------

def _replace(text: str, body: str) -> str:
    start, end = text.index(BEGIN) + len(BEGIN), text.index(END)
    return text[:start] + "\n" + body + "\n" + text[end:]


def apply(write: bool) -> list[str]:
    blocks = build()
    problems: list[str] = []
    for path, flavour in TARGETS:
        where = path.relative_to(ROOT).as_posix()
        if not path.exists():
            problems.append(f"{where}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        if BEGIN not in text or END not in text:
            problems.append(
                f"{where}: has no {BEGIN} / {END} markers, so the generated "
                f"mapping has nowhere to go. Add them, then run with --write.")
            continue
        wanted = _replace(text, blocks[flavour])
        if wanted == text:
            continue
        if write:
            path.write_text(wanted, encoding="utf-8")
        else:
            problems.append(
                f"{where}: the framework mapping is out of date. "
                f"Run `python -m tools.atlas_table --write`.")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="Rewrite the generated block in every target.")
    parser.add_argument("--course-only", action="store_true",
                        help="Emit only what course.yaml claims, for a course "
                             "whose lab cases are not built yet.")
    args = parser.parse_args(argv)

    if args.course_only:
        target = CONTENT / "pages" / "framework-alignment.md"
        block = build_course_only()
        if args.write:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and BEGIN in target.read_text(encoding="utf-8"):
                old_text = target.read_text(encoding="utf-8")
                head = old_text.split(BEGIN)[0]
                tail = old_text.split(END)[1] if END in old_text else "\n"
                target.write_text(head + block + tail, encoding="utf-8")
            else:
                target.write_text(HEADER + block + "\n", encoding="utf-8")
            print(f"  framework mapping: written to "
                  f"{target.relative_to(ROOT)}")
        else:
            print(block)
        return 0

    problems = apply(args.write)
    if problems:
        for problem in problems:
            print(f"  {problem}")
        return 1
    print("  framework mapping: ok" if not args.write
          else "  framework mapping: written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
