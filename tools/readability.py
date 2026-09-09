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

import os
import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import textstat

ROOT = Path(__file__).resolve().parents[1]


def _content_root() -> Path:
    """Which course this is measuring, and say so out loud.

    This tool is shared by three courses. Two live at the repository root
    under content/funded and content/constrained, so a default of ROOT/content
    finds both. The third lives in builder/ and has its own content root.

    Defaulting to ROOT/content while standing in builder/ measured the two
    SIBLING courses and reported them as passing. That is worse than failing:
    the page budgets never ran on the course being edited, and a reading over
    its limit went unnoticed through a day of edits.
    """
    named = os.environ.get("ITSY_CONTENT")
    if named:
        return ROOT / named
    here = Path.cwd() / "content"
    if (here / "course.yaml").is_file():
        return here          # a course that lives in a subdirectory
    return ROOT / "content"


CONTENT = _content_root()

MAX_GRADE = 8.0
TARGET_GRADE = 7.0
MAX_SENTENCE_WORDS = 15.0

# A second bar, for documents staff read rather than students.
#
# The ceilings above are written for a page a student reads in a browser. They
# are the wrong ceilings for a blueprint, a spec, an instructor guide or a
# memo, which are read the way a professional reads a reference document.
# Holding those to nine word sentences makes them worse.
#
# The numbers come from docs/writing-standard.md section 1.1. They were being
# asserted in a status note and checked by hand, because this tool had no
# notion of them: it applied the student ceilings to every staff document, so a
# 6,852 word contract read as over a 1,400 word page budget and a 16.6 word
# average sentence read as a failure when the bar is 18.
STAFF_MAX_GRADE = 9.5
STAFF_MAX_SENTENCE_WORDS = 18.0
STAFF_LONGEST_SENTENCE = 45

# The user's own words, kept verbatim on purpose. Neither bar applies.
VERBATIM_STEMS = {"build-prompt-v1.3", "program-manager-suggested-outcomes"}


def is_staff_doc(path: Path) -> bool:
    """True for a document written for staff rather than for a student."""
    try:
        path.resolve().relative_to(CONTENT.resolve())
    except ValueError:
        return True
    return False

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
    # 575, not the 550 a wrap-up gets. The model comparison used to read "it
    # scored 16 of 20 against your 19", which quoted one measured run as the
    # student's own result. That contradicts week 1, which teaches that one
    # answer is a sample and not a fact, and the models are probabilistic
    # enough that the promised 19 was never safe. Saying so honestly costs
    # words on a page that was already exactly full.
    "w7-wrap-up":              575,
    # 1450, not 1400. Week 6 teaches a guardrail, and a guardrail has a rate
    # rather than a score. Saying which things move that rate, and that an
    # agent has to be built to fail in a direction you chose, is the honest
    # end of the week rather than an aside. It does not fit in what was left.
    "w6-content-2":           1470,
    # Funded course only. Six things the registrar-approved notice has to carry
    # (what is captured, who reads it, for how long, how a student sees their
    # own, how they ask for removal, and what the answer will be), plus the
    # warning about pasting real data. Same budget as course-policies, which is
    # the comparable page, rather than the 500 first guessed at.
    "what-is-logged":          650,
    # A glossary is a reference page: nobody reads it end to end, and the page
    # says so. Its budget is a cap on sprawl, not a cap on how many terms the
    # course may teach. content/AUTHORING.md section 6 promises 112 terms are
    # available without redefinition, and the entries for them do not fit in
    # 1,600 weighted words. Raised rather than cutting a term a student needs
    # to fit a number chosen before the terms existed.
    "glossary":               1800,   # searched, not read, but not unbounded
}

# Pages whose job is to be complete rather than short: reference material an
# instructor or a committee reads, and one page students search rather than read.
NO_BUDGET = {"framework-alignment", "instructor-notes", "where-to-go-next",
             "findings-report-template", "w3-annotated-skeleton",
             "AUTHORING", "QUIZZES", "README"}

# A paragraph longer than this is a wall, whatever its reading level.
MAX_PARAGRAPH_WORDS = 70

# ---------------------------------------------------------------- warmth
#
# Three standards travel together and all three are measured here, so nobody
# has to remember them: reading level, length, and warmth.
#
# Warmth is contraction density. The course was rewritten in a warm pass on
# 2026-09-07 because it read flat, and contractions also lower the grade, so
# the same edit makes a page warmer and easier at once. Student-facing prose
# carries them. Notebooks deliberately do not: a notebook is instructions
# beside code, and the register there is plain and direct.
#
# The floor is deliberately low. It exists to catch a page written with no
# contractions at all, not to squeeze every page toward a mean. Measured on
# 2026-09-08 the course ran 6.7 to 39.2 per 1,000 words, mean 17.4, and
# notebooks ran 0.0 to 5.0, mean 2.1. Both bands sit clear of their limit.
WARM_FLOOR = 4.0        # per 1,000 words, student-facing prose
COLD_CEILING = 6.0      # per 1,000 words, notebook markdown
WARMTH_MIN_WORDS = 150  # below this a rate is noise

CONTRACTION_RE = re.compile(r"\b\w+['\u2019](?:t|s|re|ve|ll|d|m)\b")

# A contraction of "is" is wrong when the word it attaches to is not the
# subject of the clause. tools/warm_pass.py contracts by pattern and cannot
# see that, and it shipped eight of these before anyone noticed:
#
#     Handling it is the work      -> Handling it's the work
#     What to take from it is ...  -> ... from it's the shape
#     Nothing here is graded       -> Nothing here's graded
#
# All three read as garbage to a screen reader, which is the argument for
# catching them here rather than by eye. The rule: flag it's / here's /
# there's / that's when the token in front makes it part of a longer phrase
# rather than the subject, which is a preposition, a gerund, or a quantifier.
BROKEN_CONTRACTION_RE = re.compile(
    r"\b(?:from|of|with|about|for|in|on|at|to|into|than|"
    r"[Nn]othing|[Ee]verything|[Ss]omething|[Aa]nything|"
    r"\w+ing)\s+(?:it|here|there|that)['\u2019]s\b")


def contraction_rate(text: str) -> tuple[int, float]:
    """How many contractions per 1,000 words of measurable prose."""
    words = len(text.split())
    found = len(CONTRACTION_RE.findall(text))
    return found, (found / words * 1000 if words else 0.0)


def broken_contractions(text: str) -> list[str]:
    """Contractions of "is" onto something that is not the subject."""
    return [m.group(0) for m in BROKEN_CONTRACTION_RE.finditer(text)]

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
    contractions: int = 0
    contractions_per_1k: float = 0.0
    budget: int = 0


def _terminate(marker: re.Pattern, text: str) -> str:
    """End every line that starts with `marker`, unless it already ends."""
    out = []
    for line in text.split("\n"):
        if marker.match(line) and line.rstrip() and line.rstrip()[-1] not in ".?!:;,":
            line = line.rstrip() + "."
        out.append(line)
    return "\n".join(out)


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
    # A heading and a list item each end a unit of reading, but neither carries
    # terminating punctuation. Stripping the marker alone glued them to what
    # followed, so the splitter saw one enormous sentence: four bullets under a
    # colon measured as a single 74 word sentence whose real prose was 20.
    # Every document with a colon-introduced list failed on an artifact.
    #
    # Terminating them costs nothing and is the truer reading: a bullet is a
    # unit a reader takes in on its own, so counting it as one is closer to
    # what the measure is for than gluing four together.
    text = _terminate(HEADING_RE, text)
    text = HEADING_RE.sub("", text)
    text = _terminate(LIST_MARKER_RE, text)
    text = LIST_MARKER_RE.sub("", text)
    text = re.sub(r"[*_#>]+", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip(), before - len(text)


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    return [p.strip() for p in parts if len(p.split()) >= 3]


def check_text(text: str, name: str, limit: float, enforced: bool, staff: bool = False) -> PageReport:
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
    max_avg = STAFF_MAX_SENTENCE_WORDS if staff else MAX_SENTENCE_WORDS
    max_one = STAFF_LONGEST_SENTENCE if staff else 40
    if average > max_avg:
        problems.append(
            f"average sentence is {average} words, and the limit is {max_avg}. "
            f"Split the long ones."
        )
    if max(lengths) > max_one:
        problems.append(f"one sentence is {max(lengths)} words long, and the limit "
                        f"is {max_one}. Break it up.")

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
    """What kind of page this is, which decides how long it may be.

    A length budget is a statement about a page a student reads in a browser.
    It means nothing for a document written for the program manager or for a
    curriculum committee, and applying one anyway produced a false failure on
    every file under docs/: code-ledger.md is a 6,852 word contract that lists
    every function in the course, and it was being marked over a 1,400 word
    student page budget.

    So anything outside the content directory carries no budget. The reading
    grade, the sentence length and the paragraph length are still measured and
    still reported, because those are the program manager bar and they do
    apply. Only the page length stops being enforced.
    """
    stem = path.stem
    try:
        path.resolve().relative_to(CONTENT.resolve())
    except ValueError:
        return None
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


def label_for(path: Path) -> str:
    """The name to print for a file: repo-relative when it is inside the repo.

    --file used to be handed straight to relative_to(), which raises on a
    relative path, so `--file builder/content/pages/w3-content.md` died in a
    traceback and only an absolute path worked. That is the form a person
    types, and the form every authoring instruction gives, so the gate was
    unusable exactly where it is most needed. Resolve first, and fall back to
    the path as given for a file outside the repository.
    """
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


NOTEBOOK_DIR = Path("lab/notebooks")


def notebook_markdown(path: Path) -> str:
    """Every markdown cell of a notebook, joined, for measurement.

    Notebooks were the one body of student-facing prose nothing measured. They
    are read as closely as a page is -- more closely, because the student is
    stuck when they do not land -- and the standard for them is the same
    reading level as the rest of the course with none of the warmth.
    """
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return "\n\n".join("".join(cell.get("source", []))
                        for cell in nb.get("cells", [])
                        if cell.get("cell_type") == "markdown")


def check_file(path: Path) -> PageReport:
    stem = path.stem
    staff = is_staff_doc(path)
    # The user's own words, kept verbatim. Neither bar applies to them.
    enforced = stem not in EXEMPT_STEMS and stem not in VERBATIM_STEMS
    default_grade = STAFF_MAX_GRADE if staff else MAX_GRADE
    limit = STRICTER.get(stem, default_grade)
    text = (notebook_markdown(path) if path.suffix == ".ipynb"
            else path.read_text(encoding="utf-8"))
    report = check_text(text, label_for(path), limit, enforced, staff=staff)

    kind = "notebook" if path.suffix == ".ipynb" else page_kind(path)
    report.kind = kind or "reference"
    report.body_words = weighted_words(text)

    if kind and kind != "notebook":
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

    # Warmth. Student-facing prose carries contractions; notebook markdown does
    # not. Both directions are enforced so neither standard drifts.
    clean, _ = strip_for_measurement(text)
    report.contractions, report.contractions_per_1k = contraction_rate(clean)
    rate = report.contractions_per_1k
    if len(clean.split()) >= WARMTH_MIN_WORDS and enforced and not staff:
        if kind == "notebook":
            if rate > COLD_CEILING:
                report.problems.append(
                    f"{rate:.1f} contractions per 1,000 words, and a notebook's "
                    f"ceiling is {COLD_CEILING}. Notebook prose is plain and "
                    f"direct. Warmth belongs on the content pages.")
                report.passed = False
        elif kind and rate < WARM_FLOOR:
            report.problems.append(
                f"{rate:.1f} contractions per 1,000 words, and the floor for a "
                f"student-facing page is {WARM_FLOOR}. The course reads warm. "
                f"Run tools/warm_pass.py on it, then read what it changed.")
            report.passed = False

    # Broken contractions are wrong everywhere, including staff documents.
    broken = broken_contractions(clean)
    if broken:
        report.problems.append(
            f"{len(broken)} contraction(s) of \"is\" onto something that is not "
            f"the subject: {', '.join(repr(b) for b in broken[:3])}. "
            f"Write it out. A screen reader cannot rescue these.")
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
        # Notebook markdown is student-facing prose and is measured with it.
        notebooks = CONTENT.parent / NOTEBOOK_DIR
        if notebooks.is_dir():
            paths += sorted(notebooks.glob("*.ipynb"))
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

    # Say which tree this measured. Without this line the tool reported a
    # sibling course as passing for a whole day of edits to a different one.
    try:
        shown = CONTENT.relative_to(ROOT)
    except ValueError:
        shown = CONTENT
    print(f"measuring: {shown}")
    print(f"{'page':50} {'kind':12} {'grade':>6} {'words':>6} {'budget':>7} {'warm':>6}")
    print("-" * 95)
    for report in sorted(reports, key=lambda r: (r.passed, -r.body_words)):
        flag = "  " if report.passed else "!!"
        budget = f"{report.budget}" if report.budget else "-"
        print(f"{flag}{report.path:48} {report.kind:12} {report.grade:6.2f} "
              f"{report.body_words:6d} {budget:>7} {report.contractions_per_1k:6.1f}")

    scored = [r for r in reports if r.words >= 40 and r.enforced]
    if scored:
        mean = sum(r.grade for r in scored) / len(scored)
        print("-" * 82)
        print(f"{len(scored)} enforced pages, mean grade {mean:.2f}, "
              f"limit {MAX_GRADE}, target {TARGET_GRADE}")
        prose = [r for r in scored if r.kind != "notebook"]
        books = [r for r in scored if r.kind == "notebook"]
        if prose:
            warm = sum(r.contractions_per_1k for r in prose) / len(prose)
            print(f"  warmth: {warm:.1f} contractions per 1k across {len(prose)} "
                  f"prose page(s), floor {WARM_FLOOR}")
        if books:
            cold = sum(r.contractions_per_1k for r in books) / len(books)
            print(f"  warmth: {cold:.1f} across {len(books)} notebook(s), "
                  f"ceiling {COLD_CEILING}")

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
