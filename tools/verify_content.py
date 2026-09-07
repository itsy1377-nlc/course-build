"""Check that the course content still describes the code it is about.

    python -m tools.verify_content

This is the gate that was missing, and its absence caused most of the defects
four reviews found.

Reading level was mechanically enforced from the start: a page over grade 8
fails the build. Factual accuracy was a checklist somebody was supposed to run
once a semester. Only one of those two could fail a build, so pages drifted
away from the code they describe and nothing noticed. Worse, the asymmetry had
a direction: an accurate hedged sentence ("no hits observed in five trials")
costs reading grade, and a confident wrong one ("mitigated") does not.

So this checks the things that can be checked mechanically:

  1. Every command a page tells a student to run exists.
  2. Every file path a page cites exists.
  3. Every framework identifier appears in a pinned allowlist built from the
     harness case files, which are the artifacts a student actually copies
     identifiers out of.
  4. Every harness status word a page uses is one the runner can emit.
  5. Every case-file field a page names is in the JSON schema.
  6. Points on an assignment page agree with its rubric and with course.yaml.
  7. Data the content asserts about the lab, such as which customers exist,
     matches the seed files.

None of this replaces a person reading the pages. It catches the class of
mistake that a person reading the pages reliably misses, which is a sentence
that was true when it was written.
"""

from __future__ import annotations

import os
import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _content_root() -> Path:
    """Which course this is checking.

    This tool is shared by three courses. Two live at the repository root under
    content/funded and content/constrained; the third lives in builder/ and has
    its own content root, its own docs/ and its own lab/.

    Everything below used to hang off ROOT, so running it against builder/
    checked builder's pages while reading the SIBLING courses' docs/ and
    labs/. It reported ATLAS findings from another course and said nothing
    about this one. Same failure as the readability tool had, and the same
    fix: derive the whole tree from the course being checked.
    """
    named = os.environ.get("ITSY_CONTENT")
    if named:
        return ROOT / named
    here = Path.cwd() / "content"
    if (here / "course.yaml").is_file():
        return here          # a course that lives in a subdirectory
    return ROOT / "content"


CONTENT = _content_root()
# The course's own tree, which is ROOT for the two sibling courses and
# builder/ for this one. docs/ and the lab code are siblings of content/.
COURSE = CONTENT.parent
# builder/ calls it lab/; the older trees call it labs/. Take whichever exists
# so a missing directory does not silently make every path check vacuous.
LABS = next((COURSE / n for n in ("labs", "lab") if (COURSE / n).is_dir()),
            COURSE / "labs")


class Finding:
    def __init__(self, where: str, what: str, fix: str = ""):
        self.where, self.what, self.fix = where, what, fix

    def __str__(self) -> str:
        line = f"{self.where}: {self.what}"
        return line + (f"\n      {self.fix}" if self.fix else "")


def _pages() -> list[Path]:
    out = []
    for folder in ("pages", "assignments", "discussions"):
        out += sorted((CONTENT / folder).glob("*.md"))
    return out


def _all_authored() -> list[Path]:
    """Pages AND quizzes.

    The first version of this checker scanned pages only, and a later review
    found eleven quiz items with wrong keyed answers, several of which are
    exactly the drift this file exists to catch: a status the runner cannot
    emit, a technique no case demonstrates, a path with a stale prefix. A quiz
    item is content. It is graded content, which makes it worse when it rots.
    """
    return _pages() + sorted((CONTENT / "quizzes").glob("*.yaml"))


def _fenced(text: str) -> str:
    """Only the code blocks, where commands and paths live."""
    return "\n".join(re.findall(r"```[a-z]*\n(.*?)```", text, re.DOTALL))


# ---------------------------------------------------------------------------
# 1. Commands
# ---------------------------------------------------------------------------

MODULE_RE = re.compile(r"python -m ([a-z_][a-z0-9_.]*)")
SCRIPT_RE = re.compile(r"python (?:-\w+ )*([a-z_][a-z0-9_/]*\.py)")

# Modules that come from the dependencies rather than from the labs.
INSTALLED_MODULES = {"pytest", "venv", "pip", "http.server", "json.tool"}

# Files a student CREATES. They are absent from the repository on purpose, and
# a page telling somebody to make one is correct rather than broken. Anything
# not on this list has to exist.
STUDENT_CREATES = {
    "AI-USE.md",          # Project 1: one AI suggestion they rejected, and why
    "ANSWERS.md",         # Project 1 written answers
    "lab1.py",            # Lab 1 scaffold the student saves and edits
    "lab1_dict.py",
    "module1-pytest.txt", # their own test output, pasted
    ".env",
    "scope.yaml",
}


@lru_cache(maxsize=1)
def _student_creates() -> frozenset[str]:
    """The names above, plus whatever this course declares for itself.

    The set was written for the two courses at the repository root and named
    their artifacts only. Pointing this tool at builder/ made every "turn in
    week3_grounding.json" line a finding, sixteen of them, none real. A gate
    that cries wolf sixteen times is a gate people learn to scroll past.
    """
    names = set(STUDENT_CREATES)
    spec = CONTENT / "course.yaml"
    if spec.is_file():
        raw = yaml.safe_load(spec.read_text(encoding="utf-8")) or {}
        names.update(str(n) for n in raw.get("student_creates") or [])
    return frozenset(names)


def check_commands(findings: list[Finding]) -> None:
    for path in _all_authored():
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for module in set(MODULE_RE.findall(text)):
            if module in INSTALLED_MODULES or module.split(".")[0] in INSTALLED_MODULES:
                continue
            parts = module.split(".")
            candidates = [LABS.joinpath(*parts).with_suffix(".py"),
                          LABS.joinpath(*parts, "__main__.py"),
                          LABS.joinpath(*parts)]
            if not any(c.exists() for c in candidates):
                findings.append(Finding(
                    where, f"tells a student to run `python -m {module}`, "
                           f"which does not exist in labs/"))
        for script in set(SCRIPT_RE.findall(text)):
            if Path(script).name in _student_creates():
                continue
            if not (LABS / script).exists() and not (COURSE / script).exists():
                findings.append(Finding(
                    where, f"tells a student to run `python {script}`, "
                           f"which does not exist"))


# ---------------------------------------------------------------------------
# 2. Paths
# ---------------------------------------------------------------------------

PATH_RE = re.compile(r"`([a-zA-Z0-9_][a-zA-Z0-9_./-]*\.(?:py|yaml|yml|json|txt|jsonl|md))`")


def check_paths(findings: list[Finding]) -> None:
    for path in _all_authored():
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for cited in set(PATH_RE.findall(text)):
            if cited.startswith("labs/"):
                findings.append(Finding(
                    where, f"cites `{cited}` with a labs/ prefix",
                    "In the student repository, labs/ IS the root. Drop the prefix."))
                cited = cited[len("labs/"):]
            name = Path(cited).name
            if "*" in cited or cited.startswith((".", "runs/")) or name in _student_creates():
                continue
            if (LABS / cited).exists() or (COURSE / cited).exists():
                continue
            # Prose often names a file by its basename alone: "open llm.py".
            # That is how people talk, so resolve it that way, and only
            # complain when no file of that name exists anywhere in the labs.
            if "/" not in cited and any(LABS.rglob(name)):
                continue
            findings.append(Finding(where, f"cites `{cited}`, which does not exist"))


# ---------------------------------------------------------------------------
# 3. Framework identifiers
# ---------------------------------------------------------------------------

ATLAS_RE = re.compile(r"\bAML\.T\d{4}(?:\.\d{3})?\b")
LLM_RE = re.compile(r"\bLLM\d{2}:\d{4}\b")
ASI_RE = re.compile(r"\bASI\d{2}\b")
CWE_RE = re.compile(r"\bCWE-\d+\b")


def _allowed_identifiers() -> tuple[set[str], set[str], set[str], set[str]]:
    """The identifiers the labs actually stand behind.

    Built from the case files rather than from a hand-kept list, because the
    case files are what a student copies identifiers out of, and because a
    case file's notes have to justify each one.

    Read through tools.atlas_table so that the generated mapping tables and
    this gate cannot disagree about what a case demonstrates. Two readers of
    the same files answering the same question differently is the shape of the
    bug this whole area exists to prevent.
    """
    from tools import atlas_table
    families = atlas_table.case_identifiers()
    atlas = set(families["atlas"])
    llm = set(families["owasp_llm"])
    asi = set(families["owasp_agentic"])
    cwe = set(families["cwe"])
    atlas = atlas_table.with_parents(atlas)
    return atlas, llm, asi, cwe


# Identifiers the course names but does not demonstrate. Naming one is fine;
# claiming it as covered is not, so each has to be listed here on purpose.
#
# Being on this list buys prose, not a table row. A technique nothing
# demonstrates has no business in a table, because every table in this course
# reads as a coverage claim: that is exactly how AML.T0054 and AML.T0067 came
# to be claimed for a week that ran nothing. check_named_only_stays_in_prose
# enforces the distinction, and tools/atlas_table.py fails if an identifier is
# listed here and demonstrated by a case at the same time.
NAMED_ONLY = {
    "AML.T0110": "MCP tool poisoning. Named in week 3 and in Module 9, never run.",
    "AML.T0054": "Jailbreak. Out of scope: the course forbids attacking safety filters.",
    "AML.T0067": "Trusted output manipulation. Not demonstrated.",
    "AML.T0051.002": "Triggered injection. Not demonstrated.",
    "AML.T0080": "Agent memory and thread poisoning. Named only where the design "
                 "record explains why A5 was corrected away from it to AML.T0070.",
    "LLM04:2026": "Supply chain, taught as why dependencies are pinned.",
    "LLM08:2026": "Hidden context exposure. Named in the alignment table only.",
    "LLM10:2026": "Improper output handling. Named in the alignment table only.",
    "ASI10": "Not a claim. The alignment page says the agentic list runs ASI01 "
             "through ASI10, which is a fact about the publication's length.",
}


def check_frameworks(findings: list[Finding]) -> None:
    atlas, llm, asi, cwe = _allowed_identifiers()
    for path in _all_authored():
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for found, allowed, label in (
            (ATLAS_RE.findall(text), atlas, "MITRE ATLAS technique"),
            (LLM_RE.findall(text), llm, "OWASP LLM identifier"),
            (ASI_RE.findall(text), asi, "OWASP Agentic identifier"),
            (CWE_RE.findall(text), cwe, "CWE identifier"),
        ):
            for identifier in sorted(set(found)):
                if identifier in allowed or identifier in NAMED_ONLY:
                    continue
                findings.append(Finding(
                    where, f"cites {label} {identifier}, which no case file uses",
                    f"Either a case has to demonstrate it, or add it to NAMED_ONLY "
                    f"in tools/verify_content.py with a reason."))


def _mapping_documents() -> list[Path]:
    """Design records that also carry framework identifiers.

    These are not course content, so they are not in _all_authored(). They are
    checked anyway, because the wrong claim survived for as long as it did by
    sitting in exactly these files where no gate was looking.
    """
    docs = COURSE / "docs"
    # archive/ is deliberately excluded. Those documents are snapshots of what
    # was believed when they were written, and holding a snapshot to today's
    # case files would either falsify the record or block the build on history.
    return sorted(docs.glob("*.md")) + sorted(docs.glob("*.html"))


def check_frameworks_in_docs(findings: list[Finding]) -> None:
    """The same rule, applied to the design records."""
    atlas, llm, asi, cwe = _allowed_identifiers()
    for path in _mapping_documents():
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for found, allowed, label in (
            (ATLAS_RE.findall(text), atlas, "MITRE ATLAS technique"),
            (LLM_RE.findall(text), llm, "OWASP LLM identifier"),
            (ASI_RE.findall(text), asi, "OWASP Agentic identifier"),
        ):
            for identifier in sorted(set(found)):
                if identifier in allowed or identifier in NAMED_ONLY:
                    continue
                findings.append(Finding(
                    where, f"cites {label} {identifier}, which no case file uses",
                    f"Either a case has to demonstrate it, or add it to NAMED_ONLY "
                    f"in tools/verify_content.py with a reason."))


# A Markdown table row, or an HTML one. Both read as a coverage claim.
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$|<t[dh][ >]", re.M)


def check_named_only_stays_in_prose(findings: list[Finding]) -> None:
    """A technique nothing demonstrates may be named, but not tabulated.

    This is the check that was missing. AML.T0054 and AML.T0067 sat in
    NAMED_ONLY with accurate reasons and simultaneously sat in a table headed
    "MITRE ATLAS mapping", which every reader takes as a claim of coverage.
    NAMED_ONLY buys a sentence, not a row.

    The generated block is exempt, and only the generated block: it exists to
    state the distinction, and it is machine written from this same list.
    """
    from tools import atlas_table
    generated = re.compile(re.escape(atlas_table.BEGIN) + r".*?"
                           + re.escape(atlas_table.END), re.S)
    for path in _all_authored() + _mapping_documents():
        text = generated.sub("", path.read_text(encoding="utf-8"))
        where = path.relative_to(ROOT).as_posix()
        for line in text.splitlines():
            if not _TABLE_ROW_RE.search(line):
                continue
            for identifier in sorted(set(ATLAS_RE.findall(line))):
                if identifier not in NAMED_ONLY:
                    continue
                findings.append(Finding(
                    where, f"puts {identifier} in a table row, and no case "
                           f"demonstrates it",
                    f"A table reads as a coverage claim. {NAMED_ONLY[identifier]} "
                    f"Say it in a sentence, or let tools/atlas_table.py "
                    f"generate the row."))


def check_mapping_is_generated(findings: list[Finding]) -> None:
    """The generated tables match what the sources say right now.

    A course declares which mode it is in. `framework_mapping: course-only`
    means it has no lab cases yet, so the page carries what each week names and
    says plainly that nothing demonstrates it. The full mode additionally checks
    every claim against a case that produces evidence for it.
    """
    import yaml as _yaml
    from tools import atlas_table
    course = _yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))
    mode = (course.get("course") or {}).get("framework_mapping", "full")
    target = CONTENT / "pages" / "framework-alignment.md"
    if mode == "none":
        # A course that cites no framework has no table to generate. Say so,
        # rather than reporting "ok" and letting a reader think the mapping was
        # checked, and rather than crashing on shared data it never needed.
        if target.exists():
            findings.append(Finding(
                target.relative_to(ROOT).as_posix(),
                "exists, but the course declares framework_mapping: none",
                "Either delete the page or declare the mode it is really in."))
        return
    if mode == "course-only":
        if not target.exists():
            findings.append(Finding(
                target.relative_to(ROOT).as_posix(), "does not exist",
                "Run `python -m tools.atlas_table --course-only --write`."))
            return
        current = target.read_text(encoding="utf-8")
        block = atlas_table.build_course_only()
        if block not in current:
            findings.append(Finding(
                target.relative_to(ROOT).as_posix(),
                "the framework mapping is out of date",
                "Run `python -m tools.atlas_table --course-only --write`."))
        return
    for problem in atlas_table.apply(write=False):
        findings.append(Finding("tools/atlas_table.py", problem,
                                "Run `python -m tools.atlas_table --write`."))


# ---------------------------------------------------------------------------
# 4. Harness vocabulary
# ---------------------------------------------------------------------------

STATUS_RE = re.compile(r"\b(VULNERABLE|MITIGATED|FLAKY|INCONCLUSIVE|CONTROL_FAILED|OK|"
                       r"ERRORED|ATTEMPTED_BLOCKED|NO_HITS(?:_IN_\d+)?|BLOCKED_\d+_OF_\d+)\b")


def _runner_statuses() -> set[str]:
    """The statuses the runner can actually produce.

    Parsed from the syntax tree, not from the text. A first version grepped the
    source, which matched the word MITIGATED inside a comment that explained
    why MITIGATED had been removed, and then cheerfully told every page it was
    still a valid status. A checker that reads prose has the same problem as
    the content it is checking.
    """
    import ast

    runner = LABS / "harness" / "runner.py"
    if not runner.is_file():
        # This course has no attack-run harness. Returning an empty set makes
        # check_statuses report any status token it finds, which is the right
        # answer: a page claiming MITIGATED with nothing to produce it is the
        # failure this check exists for.
        return set()
    source = runner.read_text(encoding="utf-8")
    tree = ast.parse(source)
    found: set[str] = set()

    # Only inside the function whose whole job is to decide a status, plus the
    # one place a status is promoted afterwards. Walking the whole module picks
    # up environment variable names and HTTP verbs.
    sources = [n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef)
               and n.name in ("verdict_for", "run_case")]

    for function in sources:
        for node in ast.walk(function):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                word = node.value.strip()
                if word.isupper() and word.replace("_", "").isalnum() and len(word) > 2:
                    found.add(word)
            if isinstance(node, ast.JoinedStr):
                # Only the FIRST literal chunk. f"BLOCKED_{n}_OF_{n}" also
                # contains "_OF_", which is not a status.
                first = next((v.value for v in node.values
                              if isinstance(v, ast.Constant) and isinstance(v.value, str)), "")
                root = first.strip().rstrip("_")
                if root and root.replace("_", "").isalnum() and root.isupper():
                    found.add(root)

    # The matcher strips the trial counts before comparing, so the roots are
    # what has to be here. ERRORED, OK and FLAKY come from elsewhere in the
    # runner and the report, so they are added rather than parsed.
    # ast.walk visits the literal chunks of an f-string as Constants too, so
    # f"BLOCKED_{n}_OF_{n}" contributes "BLOCKED_" and "_OF_" as well as the
    # root. Fragments start or end with an underscore; statuses do not.
    roots = {re.sub(r"_IN$", "", s.strip("_")) for s in found}
    roots = {s for s in roots
             if len(s) > 2 and not s.startswith("_") and not s.endswith("_")}
    return (roots - {"HIT"}) | {"ERRORED", "OK", "FLAKY"}


def check_statuses(findings: list[Finding]) -> None:
    known = _runner_statuses() | {"ERRORED", "FLAKY", "OK", "NO_HITS", "BLOCKED"}
    if not (LABS / "harness" / "runner.py").is_file():
        # Say which case this is. A course with no harness and no status tokens
        # is fine; the same silence would otherwise be indistinguishable from a
        # check that ran and found nothing, which is how three vacuous gates in
        # this repository came to report "ok" for months.
        used = {t for p in _all_authored()
                for t in STATUS_RE.findall(p.read_text(encoding="utf-8"))}
        if not used:
            print("  (no attack-run harness in this course, and no status "
                  "tokens in its content: nothing to check)")
            return
    for path in _all_authored():
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for status in sorted(set(STATUS_RE.findall(text))):
            root_word = re.sub(r"_(IN_\d+|\d+_OF_\d+)$", "", status)
            if root_word in known:
                continue
            findings.append(Finding(
                where, f"uses the harness status {status}, which the runner "
                       f"cannot produce",
                f"The runner emits: {', '.join(sorted(known))}"))


# ---------------------------------------------------------------------------
# 5. Case file fields
# ---------------------------------------------------------------------------


def check_case_files_have_no_duplicate_keys(findings: list[Finding]) -> None:
    """A repeated key in a case file silently discards the first one.

    A5 shipped with two `notes:` blocks. YAML keeps the last, so three
    paragraphs of instructor reasoning about why two of that case's labels had
    been wrong were parsed away and nobody ever saw them. Nothing failed, and
    the file looked right in an editor, which is this project's recurring
    failure exactly.
    """
    key_re = re.compile(r"^([a-z_][a-z0-9_]*):", re.M)
    for folder in ("harness", "solution"):
        for path in sorted((LABS / folder / "cases").glob("*.yaml")):
            text = path.read_text(encoding="utf-8")
            seen: dict[str, int] = {}
            for key in key_re.findall(text):
                seen[key] = seen.get(key, 0) + 1
            for key, count in sorted(seen.items()):
                if count > 1:
                    findings.append(Finding(
                        path.relative_to(ROOT).as_posix(),
                        f"defines `{key}:` {count} times, so YAML keeps only the last",
                        "Merge them. The earlier blocks are being discarded silently."))


def check_case_fields(findings: list[Finding]) -> None:
    schema = json.loads((LABS / "harness" / "schema" / "case.schema.json")
                        .read_text(encoding="utf-8"))
    valid = set(schema["properties"])
    # Field names a page presents as things to write in a case file.
    field_re = re.compile(r"`(owasp|atlas|cwe|trials|expect|detect|kind|authorized|"
                          r"weakness_class|acting_user|provider|notes|severity_inputs|"
                          r"owasp_llm|owasp_agentic|id|title|prompt)`")
    for path in _pages():
        text = path.read_text(encoding="utf-8")
        if "case" not in text.lower():
            continue
        where = path.relative_to(ROOT).as_posix()
        for field in sorted(set(field_re.findall(text))):
            if field not in valid:
                findings.append(Finding(
                    where, f"names a case-file field `{field}` that the schema "
                           f"rejects",
                    f"The schema allows: {', '.join(sorted(valid))}"))


# ---------------------------------------------------------------------------
# 6. Points
# ---------------------------------------------------------------------------


def check_points(findings: list[Finding]) -> None:
    course = yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))
    by_ref = {r["ref"]: r for g in ("assignments", "quizzes", "discussions")
              for r in course.get(g, [])}
    for ref, row in by_ref.items():
        if not row.get("rubric"):
            continue
        rubric = yaml.safe_load(
            (CONTENT / "rubrics" / f"{row['rubric']}.yaml").read_text(encoding="utf-8"))
        if rubric["points"] != row["points"]:
            findings.append(Finding(
                f"content/rubrics/{row['rubric']}.yaml",
                f"is worth {rubric['points']} points but {ref} is worth {row['points']}"))
        page = CONTENT / "assignments" / f"{ref}.md"
        if page.exists() and re.search(r"^::: grading", page.read_text(encoding="utf-8"),
                                       re.MULTILINE):
            findings.append(Finding(
                page.relative_to(ROOT).as_posix(),
                "has a hand-written grading block, and it has a rubric",
                "The build generates the table from the rubric and replaces this "
                "block. Two tables on one page drifted apart last time. Delete it "
                "and move anything it says into the rubric's guidance field."))


# ---------------------------------------------------------------------------
# 7. Lab data the content asserts
# ---------------------------------------------------------------------------


def check_lab_data(findings: list[Finding]) -> None:
    seed = LABS / "target" / "seed"
    if not (seed / "customers.json").is_file():
        # No seeded target application in this course. The ids this check
        # polices are C-#### and T-###; if the content never uses one there is
        # nothing to verify, and saying so beats printing "ok".
        used = {m for p in _all_authored()
                for m in re.findall(r"\bC-\d{4}\b|\bT-\d{3}\b",
                                    p.read_text(encoding="utf-8"))}
        if not used:
            print("  (no seeded target app in this course, and no C-/T- ids "
                  "in its content: nothing to check)")
            return
        findings.append(Finding(
            "content", f"cites seed ids {', '.join(sorted(used))} but "
            f"{seed.relative_to(ROOT).as_posix()} does not exist"))
        return
    customers = json.loads((seed / "customers.json").read_text(encoding="utf-8"))
    ids = {c["id"] for c in customers}
    tickets = json.loads((seed / "tickets.json").read_text(encoding="utf-8"))
    ticket_ids = {t["id"] for t in tickets}

    # Shared infrastructure lives at content/ root and serves both course trees.
    shared_docs = [CONTENT / "AUTHORING.md", CONTENT / "QUIZZES.md",
                   ROOT / "content" / "AUTHORING.md", ROOT / "content" / "QUIZZES.md"]
    for path in _all_authored() + [p for p in shared_docs if p.exists()]:
        text = path.read_text(encoding="utf-8")
        where = path.relative_to(ROOT).as_posix()
        for cid in sorted(set(re.findall(r"\bC-\d{4}\b", text))):
            if cid not in ids:
                findings.append(Finding(
                    where, f"refers to customer {cid}, which is not in the seed data",
                    f"Customers are {', '.join(sorted(ids))}."))
        for tid in sorted(set(re.findall(r"\bT-\d{3}\b", text))):
            if tid not in ticket_ids:
                findings.append(Finding(
                    where, f"refers to ticket {tid}, which is not in the seed data"))


def check_quiz_answers(findings: list[Finding]) -> None:
    """Every scored item needs exactly one right answer and feedback on all of them.

    An item with no correct option cannot be answered. An item with two is a
    trick. Both have shipped here before, so both are checked.
    """
    for path in sorted((CONTENT / "quizzes").glob("*.yaml")):
        quiz = yaml.safe_load(path.read_text(encoding="utf-8"))
        where = path.relative_to(ROOT).as_posix()
        for question in quiz.get("questions") or []:
            qid = question.get("id", "?")
            kind = question.get("type")
            answers = question.get("answers") or []
            if kind in ("multiple_choice", "true_false"):
                correct = [a for a in answers if a.get("correct")]
                if len(correct) != 1:
                    findings.append(Finding(
                        where, f"{qid} has {len(correct)} correct answers, needs exactly 1"))
            if kind == "multiple_answers" and not any(a.get("correct") for a in answers):
                findings.append(Finding(where, f"{qid} has no correct answer"))
            for answer in answers:
                if not answer.get("feedback"):
                    findings.append(Finding(
                        where, f"{qid} has an answer with no feedback",
                        "In an asynchronous course, feedback is the only teaching a "
                        "student gets after answering wrong."))
                    break
            if not question.get("outcome"):
                findings.append(Finding(where, f"{qid} carries no outcome tag"))


def check_quiz_points(findings: list[Finding]) -> None:
    course = yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))
    for row in course.get("quizzes", []):
        path = CONTENT / "quizzes" / f"{row['ref']}.yaml"
        if not path.exists():
            findings.append(Finding("content/course.yaml",
                                    f"quiz {row['ref']} has no YAML file"))
            continue
        quiz = yaml.safe_load(path.read_text(encoding="utf-8"))
        total = sum(float(q.get("points", 0)) for q in quiz.get("questions") or [])
        if abs(total - row["points"]) > 0.01:
            findings.append(Finding(
                path.relative_to(ROOT).as_posix(),
                f"items add to {total:g} points, course.yaml says {row['points']}"))


# Checks that only mean something for a course with the attack-run harness.
# Skipping them is announced rather than silent: an inapplicable check and a
# check that quietly found nothing look identical in a log, and this repository
# has already shipped three gates that reported "ok" while examining no files.
HARNESS_CHECKS = {"case file field names",
                  "no case file discards a repeated key"}


def _has_harness() -> bool:
    return (LABS / "harness").is_dir()


CHECKS = [
    ("commands students are told to run", check_commands),
    ("file paths cited in the content", check_paths),
    ("framework identifiers", check_frameworks),
    ("framework identifiers in the design records", check_frameworks_in_docs),
    ("undemonstrated techniques stay out of tables", check_named_only_stays_in_prose),
    ("the framework mapping is generated, not typed", check_mapping_is_generated),
    ("harness status words", check_statuses),
    ("case file field names", check_case_fields),
    ("no case file discards a repeated key", check_case_files_have_no_duplicate_keys),
    ("points, rubrics, and grading blocks", check_points),
    ("lab data the content asserts", check_lab_data),
    ("quiz answers and feedback", check_quiz_answers),
    ("quiz point totals", check_quiz_points),
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", help="Run one check by name fragment.")
    args = parser.parse_args(argv)

    total = 0
    for label, check in CHECKS:
        if args.only and args.only not in label:
            continue
        if label in HARNESS_CHECKS and not _has_harness():
            print(f"\n{label}: skipped, this course has no lab/harness")
            continue
        findings: list[Finding] = []
        check(findings)
        status = "ok" if not findings else f"{len(findings)} problem(s)"
        print(f"\n{label}: {status}")
        for finding in findings:
            print(f"  - {finding}")
        total += len(findings)

    print()
    if total:
        print(f"{total} place(s) where the content and the code disagree.\n")
        return 1
    print("The content and the code agree.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
