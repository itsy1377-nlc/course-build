#!/usr/bin/env python3
"""Assert the final exam against the corpus and against its own header.

WHY THIS EXISTS. On 2026-09-10 every one of the forty keys was audited by
hand, four readers over ten items each, because nothing in this repository
compares the exam to anything. That audit found no wrong key and sixteen other
defects, several of which are mechanical and should never have needed a
reader:

  * six items whose feedback named no week, against the exam description's own
    promise that every answer "names the fact that decides the question and the
    week that taught it";
  * a header block that still described the thirty-item paper the 2026-09-07
    resize replaced;
  * `temperror` and `extractor`, graded by items and defined nowhere a student
    can look;
  * an `artifact:` field in four incompatible formats, which is the only link
    from an item to the email it grades.

None of that is a judgement call. This checks the part a machine can.

    python3 builder/lab/tools/check_exam.py

It refuses to pass on an empty read: fewer than 30 scored items is a failure,
not a clean run, because that is how a check that examines nothing reports ok.
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXAM = ROOT / "content/quizzes/final-exam.yaml"
RELEASE = ROOT / "corpus/release"
PAGES = ROOT / "content/pages"
NOTEBOOKS = ROOT / "lab/notebooks"

MIN_SCORED = 30
SOURCE = re.compile(r"[Ww]eek \d|[Pp]laybook")
EMAIL_IN_STEM = re.compile(r"\bEmail (\d{3})\b|\b(\d{3})-[a-z]")


def student_facing_text():
    """Everything a student can actually read, for the untaught-term check."""
    parts = []
    for path in sorted(PAGES.glob("*.md")):
        parts.append(path.read_text(encoding="utf-8"))
    for path in sorted(NOTEBOOKS.glob("*.ipynb")):
        nb = json.loads(path.read_text(encoding="utf-8"))
        for cell in nb.get("cells", []):
            parts.append("".join(cell.get("source", [])))
    return "\n".join(parts)


def main():
    problems = []
    spec = yaml.safe_load(EXAM.read_text(encoding="utf-8"))
    questions = spec.get("questions") or []
    scored = [q for q in questions if q.get("type") == "multiple_choice"]
    blocks = [q for q in questions if q.get("type") != "multiple_choice"]

    if len(scored) < MIN_SCORED:
        print(f"check_exam: only {len(scored)} scored items found in {EXAM}.",
              file=sys.stderr)
        print("That is below the floor this check refuses to pass on. Either "
              "the file moved or it failed to parse.", file=sys.stderr)
        return 1

    # 1. One key per item, and every option carries feedback.
    for q in scored:
        answers = q.get("answers") or []
        right = [a for a in answers if a.get("correct")]
        if len(right) != 1:
            problems.append(f"{q['id']}: {len(right)} correct answers, expected 1")
        for a in answers:
            if not (a.get("feedback") or "").strip():
                problems.append(f"{q['id']}: an option carries no feedback")

    # 2. The promise in the exam's own description.
    for q in scored:
        if not any(SOURCE.search(a.get("feedback") or "") for a in q.get("answers") or []):
            problems.append(f"{q['id']}: no feedback names a week or the playbook, "
                            f"and the description promises every answer does")

    # 3. Points arithmetic against the declared total.
    total = sum(float(q.get("points") or 0) for q in scored)
    declared = float(spec.get("points") or total)
    if abs(total - declared) > 1e-6:
        problems.append(f"points sum to {total}, and the file declares {declared}")

    # 4. Every email an item names must exist in a release key.
    known = set()
    for path in sorted(RELEASE.glob("ground_truth_*.json")):
        for rec in json.loads(path.read_text(encoding="utf-8"))["emails"]:
            known.add(rec["id"])
            known.add(rec["id"][:3])
    named = set()
    for q in scored + blocks:
        for a, b in EMAIL_IN_STEM.findall(q.get("text") or ""):
            named.add(a or b)
    for eid in sorted(named):
        if eid not in known:
            problems.append(f"an item names email {eid}, which is in no release key")

    # 5. The header's own counts, against the file below it.
    header = EXAM.read_text(encoding="utf-8").split("questions:")[0]
    m = re.search(r"WHAT THE (\w+) COVER", header)
    words = {"THIRTY": 30, "FORTY": 40, "FIFTY": 50}
    if m and words.get(m.group(1)) not in (None, len(scored)):
        problems.append(f"the header says WHAT THE {m.group(1)} COVER and the "
                        f"file holds {len(scored)} scored items")

    # 6. Nothing graded may turn on a word no student can look up.
    text = student_facing_text()
    watch = ["temperror", "extractor", "permerror", "softfail"]
    for term in watch:
        used = [q["id"] for q in scored
                if term in (q.get("text") or "")
                or any(term in (a.get("text") or "") for a in q.get("answers") or [])]
        if used and term not in text:
            problems.append(f"{len(used)} item(s) use '{term}' and no page or "
                            f"notebook a student reads defines it: {', '.join(used[:4])}")

    print(f"check_exam: {len(scored)} scored items, {len(blocks)} reference "
          f"block(s), {total:g} points, {len(named)} email(s) named")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("\nthe exam agrees with the corpus, with its own header, and with the "
          "promise it makes in its directions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
