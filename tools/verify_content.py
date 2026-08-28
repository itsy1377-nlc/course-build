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

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
LABS = ROOT / "labs"


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
            if Path(script).name in STUDENT_CREATES:
                continue
            if not (LABS / script).exists() and not (ROOT / script).exists():
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
            if "*" in cited or cited.startswith((".", "runs/")) or name in STUDENT_CREATES:
                continue
            if (LABS / cited).exists() or (ROOT / cited).exists():
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
    """
    atlas: set[str] = set()
    llm: set[str] = set()
    asi: set[str] = set()
    cwe: set[str] = set()
    for path in sorted((LABS / "harness" / "cases").glob("*.yaml")):
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        atlas |= set(case.get("atlas") or [])
        llm |= set(case.get("owasp_llm") or [])
        asi |= set(case.get("owasp_agentic") or [])
        cwe |= set(case.get("cwe") or [])
    for path in sorted((LABS / "solution" / "cases").glob("*.yaml")):
        case = yaml.safe_load(path.read_text(encoding="utf-8"))
        atlas |= set(case.get("atlas") or [])
        llm |= set(case.get("owasp_llm") or [])
        asi |= set(case.get("owasp_agentic") or [])
    return atlas, llm, asi, cwe


# Identifiers the course names but does not demonstrate. Naming one is fine;
# claiming it as covered is not, so each has to be listed here on purpose.
NAMED_ONLY = {
    "AML.T0110": "MCP tool poisoning. Named in week 3 and in Module 9, never run.",
    "AML.T0051": "The parent technique. Its sub-techniques carry the evidence.",
    "AML.T0051.000": "Direct injection, demonstrated by A1.",
    "AML.T0054": "Jailbreak. Out of scope: the course forbids attacking safety filters.",
    "AML.T0067": "Trusted output manipulation. Not demonstrated.",
    "AML.T0051.002": "Triggered injection. Not demonstrated.",
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

    source = (LABS / "harness" / "runner.py").read_text(encoding="utf-8")
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
    customers = json.loads((LABS / "target" / "seed" / "customers.json")
                           .read_text(encoding="utf-8"))
    ids = {c["id"] for c in customers}
    tickets = json.loads((LABS / "target" / "seed" / "tickets.json")
                         .read_text(encoding="utf-8"))
    ticket_ids = {t["id"] for t in tickets}

    for path in _all_authored() + [CONTENT / "AUTHORING.md", CONTENT / "QUIZZES.md"]:
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


CHECKS = [
    ("commands students are told to run", check_commands),
    ("file paths cited in the content", check_paths),
    ("framework identifiers", check_frameworks),
    ("harness status words", check_statuses),
    ("case file field names", check_case_fields),
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
