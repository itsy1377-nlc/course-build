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

# How long a page is allowed to be, by what kind of page it is.
#
# Reading level and length are different problems and only one of them was
# being enforced. A page can score grade 4 and still be twelve hundred words of
# unbroken prose, which is not readable in any sense a student would recognise.
# The orientation module ran to 12,588 words across 13 pages: roughly fifty
# minutes of reading before anybody touched anything.
#
# The budgets below are per page and they are deliberately tight. A student
# skims an orientation page, finds the one thing they came for, and leaves.
# Anything that does not survive the budget was not going to be read.
WORD_BUDGET = {
    "orientation": 450,   # Start Here pages. Scanned, not read.
    "overview":    400,   # a week's front page
    # 550, not 400. A wrap-up carries what you learned, what you did, a
    # self-check WITH its answers, and what is next. The answers were the thing
    # that broke the earlier number, and cutting them would have meant an
    # asynchronous course with self-checks a student cannot check.
    "wrapup":      550,
    "content":    1400,   # the week's actual lesson, the one place length earns itself
    "assignment":  700,
    "discussion":  500,
}

# One page gets more room, and only one. The Rules of Engagement is a policy
# document a student has to be able to cite a clause from, and it is the one
# page in the course where being incomplete costs more than being long. It is
# also held to a tighter reading grade than anything else, which is the trade.
# Per page, because "orientation page" covers a signpost and a policy document
# and those are not the same job. Every number below is a decision about what
# that page has to carry, and together they take the Start Here module from
# 12,588 words to about 5,800: fifty minutes of reading down to twenty.
PAGE_BUDGET = {
    "welcome-start-here":      400,   # a signpost. It points, it does not explain
    "meet-your-instructor":    300,
    "course-policies":         650,   # deadlines, late work, privacy, FERPA
    "academic-integrity":      350,   # the district policy, then a pointer
    "ai-use-policy":           550,   # course-specific and load-bearing
    "rules-of-engagement":     900,   # seven clauses a student has to cite
    "support-resources":       600,   # a routing table for ten services
    "canvas-and-tech-support": 450,
    "communicating-online":    400,
    "tips-for-success":        400,
    "how-to-navigate-canvas":  350,
    "course-schedule":         550,   # mostly a table
    "exam-review":             450,
    "course-material":         900,   # a resource list with licences
    "glossary":               1600,   # searched, not read, but not unbounded
}

# Pages whose job is to be complete rather than short: reference material an
# instructor or a committee reads, and one page students search rather than read.
NO_BUDGET = {"framework-alignment", "instructor-notes", "where-to-go-next",
             "findings-report-template", "w3-annotated-skeleton",
             "AUTHORING", "QUIZZES", "README"}

# A paragraph longer than this is a wall, whatever its reading level.
MAX_PARAGRAPH_WORDS = 70

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
    kind: str = "reference"
    body_words: int = 0
    budget: int = 0


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


ORIENTATION = {"welcome-start-here", "meet-your-instructor", "course-policies",
               "academic-integrity", "ai-use-policy", "support-resources",
               "canvas-and-tech-support", "communicating-online", "tips-for-success",
               "how-to-navigate-canvas", "course-schedule", "rules-of-engagement",
               "exam-review", "final-overview", "final-wrap-up"}


def page_kind(path: Path) -> str | None:
    """What kind of page this is, which decides how long it may be."""
    stem = path.stem
    if stem in NO_BUDGET:
        return None
    if path.parent.name == "assignments":
        return "assignment"
    if path.parent.name == "discussions":
        return "discussion"
    if stem.endswith("-overview"):
        return "overview"
    if stem.endswith("-wrap-up"):
        return "wrapup"
    if stem.endswith("-content") or stem.endswith("-walkthrough") \
            or stem.endswith("-results") or stem.endswith("-skeleton"):
        return "content"
    if stem in ORIENTATION:
        return "orientation"
    return "content"


# A word in a table cell is still a word, but a table is scanned and a
# paragraph is read, and the budget is a proxy for how long a page takes rather
# than for how many words are in it. Charging both at the same rate penalised
# exactly the formatting the course wants, which an author noticed while trying
# to convert prose into a table and finding it cost them budget.
#
# So table rows, list items and fenced code count at a discount. The discount
# is not generous enough to make a page of tables free, and paragraph length is
# capped separately, so this cannot be used to smuggle prose past the gate.
SCAN_WEIGHT = 0.6


def weighted_words(text: str) -> int:
    """Roughly how much reading a page asks for, not how many words it holds."""
    body = re.sub(r"^:::.*$", "", text, flags=re.MULTILINE)
    scanned = 0
    prose_lines = []
    in_fence = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("|") or stripped.startswith(("-", "*", ">")) \
                or re.match(r"^\d+\.", stripped):
            scanned += len(stripped.split())
        else:
            prose_lines.append(line)
    prose = len(" ".join(prose_lines).split())
    return int(prose + scanned * SCAN_WEIGHT)


def _paragraphs(text: str) -> list[str]:
    """Prose paragraphs only. Tables, lists, and code are not paragraphs."""
    body = re.sub(r"^:::.*$", "", text, flags=re.MULTILINE)
    body = FENCE_RE.sub(" ", body)
    out = []
    for chunk in re.split(r"\n\s*\n", body):
        chunk = chunk.strip()
        if not chunk or chunk.startswith(("|", "-", "*", ">")) or re.match(r"^\d+\.", chunk):
            continue
        out.append(chunk)
    return out


def check_file(path: Path) -> PageReport:
    stem = path.stem
    enforced = stem not in EXEMPT_STEMS
    limit = STRICTER.get(stem, MAX_GRADE)
    text = path.read_text(encoding="utf-8")
    report = check_text(text, str(path.relative_to(ROOT)), limit, enforced)

    kind = page_kind(path)
    report.kind = kind or "reference"
    report.body_words = weighted_words(text)

    if kind:
        budget = PAGE_BUDGET.get(stem, WORD_BUDGET[kind])
        report.budget = budget
        if report.body_words > budget:
            report.problems.append(
                f"{report.body_words} words against a {budget} word budget for a "
                f"{kind} page, {report.body_words - budget} over. Length is a "
                f"readability problem too. Cut, or split it.\n"
                f"      Tables and lists count at 60 percent, because a table is "
                f"scanned and a paragraph is read.")
            report.passed = False

    paragraphs = _paragraphs(text)
    long_ones = [p for p in paragraphs if len(p.split()) > MAX_PARAGRAPH_WORDS]
    if long_ones:
        worst = max(long_ones, key=lambda p: len(p.split()))
        report.problems.append(
            f"{len(long_ones)} paragraph(s) over {MAX_PARAGRAPH_WORDS} words. "
            f"The longest is {len(worst.split())}. Break them up: "
            f"\"{' '.join(worst.split()[:12])}...\"")
        if enforced:
            report.passed = False
    return report


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

    print(f"{'page':50} {'kind':12} {'grade':>6} {'words':>6} {'budget':>7}")
    print("-" * 88)
    for report in sorted(reports, key=lambda r: (r.passed, -r.body_words)):
        flag = "  " if report.passed else "!!"
        budget = f"{report.budget}" if report.budget else "-"
        print(f"{flag}{report.path:48} {report.kind:12} {report.grade:6.2f} "
              f"{report.body_words:6d} {budget:>7}")

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
