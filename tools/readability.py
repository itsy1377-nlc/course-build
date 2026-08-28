"""Enforce the plain-language standard on every authored page.

    python -m tools.readability                 check everything, print a report
    python -m tools.readability --json          machine-readable
    python -m tools.readability --file <path>   check one page

The course commits to a 7th grade reading level for student-facing content. A
readability formula counts syllables, so a page that has to say "authorization
boundary" and "prompt injection" will score above grade 7 no matter how well it
is written. Pretending otherwise produces either dishonest numbers or a course
that cannot name its own subject.

So the check measures the part a writer actually controls, and it says out
loud what it excluded:

  EXCLUDED   code blocks, command output, tables of identifiers, the glossary,
             quoted external text, framework identifiers (LLM01:2026,
             AML.T0051.001, ASI03), URLs, and file paths
  ENFORCED   average sentence length at or under 15 words
             Flesch-Kincaid grade at or under 8.0 on what is left, target 7.0

The report is committed next to the content so a reviewer can read the numbers
instead of taking the claim on faith.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import textstat

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

MAX_GRADE = 8.0
TARGET_GRADE = 7.0
MAX_SENTENCE_WORDS = 15.0

# The Rules of Engagement is the one page where misreading has consequences,
# so it is held to a tighter bar.
STRICTER = {"rules-of-engagement": 7.0}

# Pages measured for information but not enforced. Two kinds: reference pages
# whose job is to be complete rather than easy, and instructor-facing pages
# written for a curriculum committee.
EXEMPT_STEMS = {"glossary", "framework-alignment", "instructor-notes",
                "AUTHORING", "QUIZZES", "README"}

# Student-facing text that does not live under content/. The plain-language
# standard is only enforced where the checker can see it, and the lab README is
# the first page a student reads.
EXTRA_PAGES = [Path("labs/README.md"), Path("labs/harness/fixtures/README.md")]

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
DIRECTIVE_RE = re.compile(r"^:::.*$", re.MULTILINE)
BLOCKQUOTE_RE = re.compile(r"^>.*$", re.MULTILINE)
TABLE_RE = re.compile(r"^\|.*\|\s*$", re.MULTILINE)
URL_RE = re.compile(r"https?://\S+|`[^`]+`")
FRAMEWORK_RE = re.compile(
    r"\b(?:LLM\d{2}:\d{4}|ASI\d{2}|AML\.T\d{4}(?:\.\d{3})?|"
    r"NIST\s+AI\s+\d+[\w\-]*|MEASURE\s+\d[\d.]*|MAP\s+\d[\d.]*|"
    r"GOVERN\s+\d[\d.]*|MANAGE\s+\d[\d.]*|AIVSS|ITSY\s*\d{4}|OWASP|MITRE ATLAS)\b"
)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HEADING_RE = re.compile(r"^#{1,6}\s+", re.MULTILINE)
LIST_MARKER_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+", re.MULTILINE)
PATH_RE = re.compile(r"\b[\w./\\-]+\.(?:py|md|yaml|yml|json|txt|html|sh|jsonl)\b")


@dataclass
class PageReport:
    path: str
    enforced: bool
    limit: float
    words: int
    sentences: int
    grade: float
    reading_ease: float
    avg_sentence_words: float
    longest_sentence_words: int
    longest_sentence: str
    excluded_chars: int
    passed: bool
    problems: list[str]


def strip_for_measurement(text: str) -> tuple[str, int]:
    """Remove everything a readability formula would score dishonestly."""
    before = len(text)
    text = FENCE_RE.sub(" ", text)
    text = TABLE_RE.sub(" ", text)
    text = BLOCKQUOTE_RE.sub(" ", text)
    text = DIRECTIVE_RE.sub(" ", text)
    text = IMAGE_RE.sub(" ", text)
    text = LINK_RE.sub(r"\1", text)
    text = URL_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    text = PATH_RE.sub(" ", text)
    text = FRAMEWORK_RE.sub(" ", text)
    text = HEADING_RE.sub("", text)
    text = LIST_MARKER_RE.sub("", text)
    text = re.sub(r"[*_#>]+", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip(), before - len(text)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    return [p.strip() for p in parts if len(p.split()) >= 3]


def check_text(text: str, name: str, limit: float, enforced: bool) -> PageReport:
    clean, excluded = strip_for_measurement(text)
    sentences = _sentences(clean)
    words = len(clean.split())

    if words < 40 or not sentences:
        return PageReport(name, enforced, limit, words, len(sentences), 0.0, 0.0, 0.0,
                          0, "", excluded, True,
                          ["too short to measure, not scored"])

    grade = round(textstat.flesch_kincaid_grade(clean), 2)
    ease = round(textstat.flesch_reading_ease(clean), 1)
    lengths = [len(s.split()) for s in sentences]
    average = round(sum(lengths) / len(lengths), 1)
    longest_index = lengths.index(max(lengths))

    problems = []
    if grade > limit:
        problems.append(
            f"grade level {grade} is above the limit of {limit}. Shorten sentences "
            f"and replace long words where a short one exists."
        )
    if average > MAX_SENTENCE_WORDS:
        problems.append(
            f"average sentence is {average} words, and the limit is {MAX_SENTENCE_WORDS}. "
            f"Split the long ones."
        )
    if max(lengths) > 40:
        problems.append(f"one sentence is {max(lengths)} words long. Break it up.")

    return PageReport(
        path=name, enforced=enforced, limit=limit, words=words, sentences=len(sentences),
        grade=grade, reading_ease=ease, avg_sentence_words=average,
        longest_sentence_words=max(lengths), longest_sentence=sentences[longest_index][:200],
        excluded_chars=excluded, passed=(not problems) or not enforced, problems=problems,
    )


def check_file(path: Path) -> PageReport:
    stem = path.stem
    enforced = stem not in EXEMPT_STEMS
    limit = STRICTER.get(stem, MAX_GRADE)
    return check_text(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)),
                      limit, enforced)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the reading level of course content.")
    parser.add_argument("--file", help="Check one file instead of everything.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--out", help="Write the JSON report here as well.")
    args = parser.parse_args(argv)

    if args.file:
        paths = [Path(args.file)]
    else:
        paths = sorted(CONTENT.rglob("*.md"))
        paths += [ROOT / extra for extra in EXTRA_PAGES if (ROOT / extra).exists()]
    if not paths:
        print(f"No markdown found under {CONTENT}")
        return 2

    reports = [check_file(path) for path in paths]
    failures = [r for r in reports if not r.passed]

    if args.json or args.out:
        payload = {
            "limit_grade": MAX_GRADE,
            "target_grade": TARGET_GRADE,
            "limit_avg_sentence_words": MAX_SENTENCE_WORDS,
            "pages": [asdict(r) for r in reports],
            "passed": not failures,
        }
        text = json.dumps(payload, indent=2)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
        if args.json:
            print(text)
            return 0 if not failures else 1

    print(f"{'page':52} {'grade':>6} {'ease':>6} {'avg':>6} {'words':>6}")
    print("-" * 82)
    for report in sorted(reports, key=lambda r: -r.grade):
        flag = "  " if report.passed else "!!"
        note = "" if report.enforced else "  (not enforced)"
        print(f"{flag}{report.path:50} {report.grade:6.2f} {report.reading_ease:6.1f} "
              f"{report.avg_sentence_words:6.1f} {report.words:6d}{note}")

    scored = [r for r in reports if r.words >= 40 and r.enforced]
    if scored:
        mean = sum(r.grade for r in scored) / len(scored)
        print("-" * 82)
        print(f"{len(scored)} enforced pages, mean grade {mean:.2f}, "
              f"limit {MAX_GRADE}, target {TARGET_GRADE}")

    if failures:
        print(f"\n{len(failures)} page(s) over the limit:\n")
        for report in failures:
            print(f"  {report.path}")
            for problem in report.problems:
                print(f"    - {problem}")
            if report.longest_sentence:
                print(f"    longest sentence ({report.longest_sentence_words} words):")
                print(f"      {report.longest_sentence}")
            print()
        return 1

    print("\nAll enforced pages are within the limit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
