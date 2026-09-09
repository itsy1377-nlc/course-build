# Test strategy: the holes behind the 2026-09-08 student run

**Written:** 2026-09-08
**Scope:** the verification apparatus, not the course.
**Status:** analysis. **No course file and no tool was modified.** The three
checks below are written out here and are not wired into any build.

Every defect in `docs/student-e2e-run-2026-09-08.md` is a hole in this
apparatus. This document names each hole, says whether the check was absent or
present-and-passing, and writes the three that are worth mechanising.

**What I ran.** `lab/tools/check_chain.py`, `lab/tools/check_tools.py`,
`lab/tools/check_site_files.py`, `python -m tools.verify_content` (from
`builder/`), `python -m tools.preflight --fast`, `python -m tools.cartridge
--check`, plus static analysis of the fifteen notebooks and the ten quiz files.
Nothing was run against the notebook server, Canvas or the LiteLLM proxy. No
model call was made.

**Verified** below means I reproduced it from the source or from a command in
this session. **Asserted** means I am repeating the run's claim without
independent confirmation.

---

## 0. The three findings that are not in your report

These came out of reading the apparatus rather than the course, and two of them
are the reason the rest of this list exists.

### 0.1 `verify_content` has two checks that examine zero items and print `ok`

**Verified.** `tools/verify_content.py:540 check_points()` opens with:

```python
by_ref = {r["ref"]: r for g in ("assignments", "quizzes", "discussions")
          for r in course.get(g, [])}
```

`builder/content/course.yaml` has no top-level `assignments`, `quizzes` or
`discussions` key. Its keys are `course, assignment_groups, outcomes,
student_files, never_ship, student_creates, modules`, and every assignment,
quiz and discussion lives inside `modules[].items`. So `by_ref` is empty,
the loop body never executes, and the check reports `ok`.

`check_quiz_points()` at line 639 has the same shape:
`for row in course.get("quizzes", [])` — zero rows, zero comparisons, `ok`.

Measured directly:

```
check_points by_ref size: 0
check_quiz_points rows  : 0
quiz yaml files seen    : 10
```

So **no gate has ever compared a rubric's total to the points Canvas awards
for this course, and no gate has ever added up a quiz's item points.** Both
report success. This matters beyond the arithmetic: `check_points` is the only
place in the repository that reads a rubric file at all, and it is the natural
home for the rubric/artifact check in section 2.2.

The irony is documented in the same file. Lines 660-665:

> An inapplicable check and a check that quietly found nothing look identical
> in a log, and this repository has already shipped three gates that reported
> "ok" while examining no files.

That comment sits about eighty lines below two gates that were, at the moment
it was written, reporting `ok` while examining no files.

### 0.2 `preflight` — "run every gate, in one command" — cannot run at all

**Verified.** `tools/preflight.py:38` is `LABS = ROOT / "labs"`. That directory
does not exist; this course's lab tree is `builder/lab/`. Running it:

```
$ ITSY_CONTENT=builder/content python3 -m tools.preflight --fast
FileNotFoundError: ... No such file or directory: '.../ITSY1377/labs'
```

It dies on gate 4 before reaching gate 5, having already run gates 1 to 3.
Gate 3, `tools.cartridge --check`, also crashes on this course:

```
File "tools/cartridge.py", line 86, in _titles
    titles.setdefault(item["ref"], _title_from_ref(item["ref"]))
KeyError: 'ref'
```

— the `url` item type added for this course carries no `ref`.

And the umbrella never knew about this course's real checks anyway.
**None of `check_chain.py`, `check_site_files.py`, `check_tools.py`,
`run_notebook.py` or `stage_notebook_site.py` is in `preflight`'s list.** The
five tools that actually understand this course are run by hand, one at a time,
by whoever remembers them — which is the exact failure `preflight`'s docstring
says it exists to prevent.

`tools/verify_content.py` was taught in commit `d9c59f9` to derive its tree
from the course being checked. `preflight.py` was not given the same fix in the
same commit, and `LABS` there is still hardcoded.

### 0.3 The guarded arm of week 6 reads two message fields the undefended arm never touches

**Verified**, and it is not in your list of four differences. See 1.1.

---

## 1. Each defect, and the check that should have caught it

### 1.1 Week 6's undefended prompt — and a correction

**The defect is real. Your description of it is wrong in one place that
matters.**

Verified from `lab/notebooks/w6-lab.ipynb`:

- Cell 5, `loop_prompt(parsed)` = `LOOP_INSTRUCTIONS + CLASSIFY_INSTRUCTIONS +
  facts + known-good hosts`. No body. Correct.
- Cell 6, `run_triage()`, closing call:
  `closing = prompt_text + tool results + schema_text(schema) + "Answer now
  with one JSON object and nothing else."`, then `answer =
  extract_json(ask_model(closing))`. **`ask_model()` is a fresh one-shot call,
  not a continuation of the message list**, so the verdict-producing call
  genuinely never sees the body. Correct, and this is the serious part.
- **But cell 5, `start_messages(parsed, prompt_text)` line 536:**

```python
    user = (prompt_text
            + "\n\nThe triage playbook:\n\n" + PLAYBOOK.strip()
            + "\n\nThe reported email:\n\n" + parsed["body_text"]
            + "\n\n" + tool_inputs
            + "\n\n" + TOOL_TURN)
```

The undefended loop turns carry the full unfenced body, planted paragraph and
all. So **"the guarded column is the only one ever exposed to the payload" is
false.** Both columns are exposed during the loop; only the guarded column is
exposed at the moment the verdict is written. That is a narrower and more
interesting defect than the one you wrote down, and `fenced_email()`'s own
comment in cell 9 says exactly this — "start_messages(), which pastes the body
into every turn of the run" — so the notebook knows.

Second correction: there are more than four differences. Verified additions:

5. `guarded_facts_text()` (cell 9) appends `Hidden text in the HTML part: yes,
   N characters` — **a direct injection signal, present only in the guarded
   arm.** The undefended facts block has no such line.
6. `guarded_triage()` reads `parsed["reply_to"]`; the undefended path does not.
7. The schema appears once undefended (appended by `run_triage`) and twice
   guarded (once inside `build_guarded_prompt`, once appended again).
8. The guarded run is handed `fenced_email(parsed)`, so the body appears twice
   per turn, once fenced and once inside the prompt text.

Cell 11's "The fence is the only thing that changed" is false at least eight
ways, and finding 5 is the one that would most plausibly move a small model on
a clean twin.

**The check that should have existed:** nothing in the repository compares the
two arms of a comparison the course narrates as controlled. `check_chain.py`
compares a function against *itself in another week*; nothing compares two
functions against *each other in the same week*. Section 2.3 writes it.

`lab/eval/week6_injection_test.py` is the right instrument and, per
`docs/course-review-2026-09-07.md` section 8, has still never been run. It
would not have caught this anyway: it measures the model, and this is a defect
in the notebook's prompt assembly, which the eval does not import.

### 1.2 Week 7's `schema_errors()` never called with `OUTPUT_SCHEMA_V2`

**Verified.** `schema_errors()` is carried in the "working code from earlier
weeks" cell of every lab (w7 cell 5). Its dispatch is
`if "allowed" in rule` → `elif rule["type"] == "number"` → `else:` requires a
list. `OUTPUT_SCHEMA_V2["summary"] = {"type": "sentences", "how_many": "two"}`
falls into the `else`. Executed against a correct week 7 answer it returns
`["summary has to be a list, and it is 'Sentence one. Sentence two.'"]`.
A `summary` that *were* a list would then raise `KeyError: 'min_items'`, since
the V2 rule has no `min_items`. **Both branches of that `else` are wrong for
V2, and neither has ever executed.**

All sixteen `schema_errors(` call sites across all fifteen notebooks pass
`OUTPUT_SCHEMA`. `OUTPUT_SCHEMA_V2` reaches only `schema_text()` (rendered into
the prompt) and `guarded_triage(..., schema=OUTPUT_SCHEMA_V2)` (which does no
validation).

**The check that should have existed and does not:** *every schema this course
defines must be exercised by the validator that claims to validate it.* This is
about twelve lines — collect module-level names matching `*_SCHEMA*` from the
notebooks, collect the second-argument expressions at every `schema_errors(`
call site, and report any schema in the first set and not the second. It is
cheap, and I have not written it out below only because three others rank
higher.

The deeper hole: `run_notebook.py` proves the notebook *runs*. It has no
concept of a code path that is never entered. Coverage of the shipped helper
functions is not measured anywhere. `schema_errors` has zero coverage in week
7; so does `restore_my_work()`, which is defined in all seven labs and
**called in none of the fifteen notebooks** (verified) — the same finding
`docs/course-review-2026-09-07.md` section 5 recorded about
`backup_my_work`/`restore_my_work` never having been executed by any check, one
round ago, unfixed.

### 1.3 All 43 self-check answers in position 1

**Verified**, and my count is 43, not 44:

| file | scored items | correct at position 1 | positions used | `shuffle` |
|---|---|---|---|---|
| `w1-self-check.yaml` | 6 | 6 | `[0]` | false |
| `w2-self-check.yaml` | 6 | 6 | `[0]` | false |
| `w3-self-check.yaml` | 6 | 6 | `[0]` | false |
| `w4-self-check.yaml` | 5 | 5 | `[0]` | false |
| `w5-self-check.yaml` | 6 | 6 | `[0]` | false |
| `w6-self-check.yaml` | 6 | 6 | `[0]` | false |
| `w7-self-check.yaml` | 8 | 8 | `[0]` | false |
| `week0-self-assessment.yaml` | 10 | 3 | `[0,1,2]` | false |
| `final-exam.yaml` | 40 | 18 | `[0,1,2,3]` | **true** |
| `syllabus-acknowledgment.yaml` | 1 | 1 | `[0]` | false |

`canvas/build_course.py:591` maps the file's `shuffle` key to
`quiz[shuffle_answers]`, so the file is the authority and the seven weekly
quizzes ship unshuffled.

**The check that existed and passed anyway:** `verify_content.check_quiz_answers()`
at line 608. It reads every one of these files. It checks exactly one correct
answer per item, feedback on every option, and an outcome tag. **It never looks
at *where* the correct answer is.** Three lines from the data it already has.
Section 2.1 writes it.

Note the shape: this is the strongest possible case for a cheap check —
the file is already open, the field is already read, the loop is already
running, and the assertion is one line. It was not written because nobody
articulated "answerable without reading" as a failure mode.

### 1.4 Week 3's email named 025 while the code loads 016

**Verified.** `w3-lab.ipynb` cell 12 line 4: `parsed_025 = load_email("016",
known_names=KNOWN_NAMES)`, with `block_025` beside it and nine printed strings
naming "email 025". Cell 10 line 32 prints the column header `email 025` over
`CHECK_FACTS["016"]`. `CHECK_PAIR = ["005", "016"]`.
`025-larkseal-review-encoded-subject.eml` is a real, different message in the
corpus and week 3 never opens it.

**The check that existed and could not catch it:** `check_site_files.py:60
path_chain()` resolves only paths whose every part is a string literal:

```python
if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, str):
    return None
```

`load_email("016", ...)` builds its path inside the helper from an argument, so
the email id is invisible to the only tool that reads corpus references out of
notebooks. It examined 204 literal path references this session and passed; not
one of them was an email id.

The general check — *an identifier in a comment, a variable name or a printed
string must match the identifier on the line it describes* — is the hardest of
the six to mechanise well, and I would not write it. The tractable 80 percent
is narrow and worth having: **for each `NNN` that appears as a three-digit
email id anywhere in a lab notebook cell, the set of ids mentioned in that
cell's prose, comments and variable names must be a subset of the ids that
cell's code actually loads.** Cell 12 fails that instantly. So does cell 10.

The cross-document half — reading says 019/016, assignment page says 005/016
then 019/016, video says 005/025 — is a different check: a per-week manifest of
teaching email ids in `course.yaml`, asserted against every week-3 document and
against `CHECK_PAIR`. That is the one I would build, because it is declarative
and a human can read it.

### 1.5 Four export cells missing fields the rubrics grade

**Verified in all four.**

| week | cell | function | what is graded | what the row holds |
|---|---|---|---|---|
| 3 | 13 | `compare_runs()` | discussion item 3, 5 pts: "the indicators your model listed" | 7 keys; no `indicators`, and no `category` either |
| 5 | 9 | `one_line()` | discussion, 4 pts: "what the last step added" | `return json.dumps(result)[:80]`, written into the persisted trace at cell 9, not display-only. The export also drops `final_answer` |
| 6 | 15 | `compare_guarded()` | rubric 72 pts: "before and after numbers, both of which the attached file shows" | 11 keys; no `confidence`; `tokens`/`tokens_written` both come from `guarded`, and `guarded_triage()` calls `start_run()` on its first line, so the undefended cost is zeroed before it is read |
| 7 | 16 | export | rubric 56 pts + discussion 3 pts: which email was wrong and which error | cell 15 computes `wrong_rows` and prints it; cell 16 never references it |

The w6 rubric's own text makes it unearnable rather than merely unhelpful.
Top band: "Supports it with the student's own before and after numbers, **both
of which the attached file shows**." The 36-point band: "cites a number the
attached file does not show." So the obvious student action — copy the two
confidences your screen printed — is specifically penalised, and the top band
cannot be reached by anyone in any section.

`w6-self-check.yaml` question `w6-q4` compounds it, verified:

```
<pre><code>verdict: benign
confidence: 0.61
problems: []
stop_reason: tools_exhausted
escalate: true
</code></pre>
```

introduced as "Your export file holds this for email 012". `problems`,
`stop_reason` and `escalate` are real keys. `verdict` and `confidence` are not
— the row uses `verdict_without_guardrails` / `verdict_with_guardrails` and
carries no confidence at all.

**The check that should have existed:** nothing anywhere relates a rubric, a
discussion item or a quiz stem to the keys the notebook writes.
`verify_content` has `check_paths` (does the file exist) but no notion of the
file's *shape*. `run_notebook.py --expect-artifact` checks only that some cell
printed the artifact's **name** (line 121, `artifact_written()` is a substring
search over cell output text) — it never opens the file, never parses it, and
would pass on a zero-byte artifact whose name got printed. Section 2.2 writes
the real one.

This is the same defect class as `docs/course-review-2026-09-07.md` section 3:
"the rubric asks for an artifact the lab does not produce". That round counted
47 points of it. This round counts 117. It was diagnosed and not mechanised.

### 1.6 Week 1's TODO 1 points at the wrong dictionary

**Verified.** `MODEL_EXTRAS = {"reasoning_effort": "none"}` at cell 3.
Cell 6 (markdown), job 2: "Merge `MODEL_EXTRAS` into that dictionary" with the
message dictionary as nearest antecedent. The check cell is **cell 8, not cell
10** (cell 10 is TODO 2), and it asserts exactly one thing:

```python
if CHECK_ANSWER.startswith("ask_model() is not written"):
```

There is no `assert` statement anywhere in `w1-lab.ipynb`. Nothing inspects the
payload. The wrong merge produces a working call, six answers and a complete
export.

**The check that should have existed:** the previous round already named this
one. `docs/course-review-2026-09-07.md` section 5, "second highest": *no check
cell is ever tested against a wrong answer.* `run_notebook.py` runs each
notebook twice — TODOs empty (`--student`) and TODOs correct (`--solution`).
There is no third mode. The check cells are this course's real test suite, and
the suite has no failing fixture.

The specific fix is a **mutation mode**: `run_notebook.py --wrong
<mutation-set>`, where each mutation is a plausible student error drawn from
`instructor/common-failure-modes.md`, and the assertion is that the check cell
*reports a problem*. Week 1's mutation is "merge into `messages[0]` instead of
`payload`". That mode does not exist, and building it is the largest single
piece of work on this list — a day, not an hour — which is why it is not one of
the three below.

### 1.7 The orientation's backup instructions

**Verified.** `budget_left`, `backup_my_work` and `restore_my_work` are defined
in the working-code cell of the seven lab notebooks only (w1 cell 5, w2-w7 cell
4). They are in none of the seven sidebars and not in
`week00-python-on-ramp.ipynb`, whose last cell (130 of 130) is markdown.
`using-the-notebook-server.md` says "any cell", "the last cell of the notebook"
and "in any notebook".

**The check that should have existed:** `verify_content.check_commands()` at
line 154 already does this job for shell commands and `python -m` invocations.
It has no equivalent for **a Python name a page tells a student to call in a
notebook**. The extension is short: extract ``` `name()` ``` from the
orientation pages, and assert the name is defined in every notebook the
sentence's scope claims ("any notebook" → all fifteen). This is a genuine
generalisation of an existing check rather than a new one, which makes it a
good candidate for the round after the three below.

---

## 2. The three checks, written

Written in `verify_content`'s style: a function taking a `findings` list,
appending `Finding(where, what, fix)`. Each returns the number of items it
examined, for reasons in section 3. All three were executed against this
course in this session and their real output is shown.

### 2.1 No scored bank may be answerable by position

```python
def check_answer_positions(findings: list[Finding]) -> int:
    """A bank whose right answer is always in the same slot is answerable
    without reading it.

    Both halves are checked, because either alone is a false negative. The
    authored distribution is what a student sees if Canvas does not shuffle,
    and `shuffle` is what decides whether Canvas shuffles. The seven weekly
    self-checks ship with 43 of 43 right answers in slot one and shuffle
    false, which scores 84 points for a student who reads nothing -- and
    these quizzes are the course's routing mechanism, so it also tells that
    student, seven times, that they are ready.
    """
    examined = 0
    for path in sorted((CONTENT / "quizzes").glob("*.yaml")):
        quiz = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        where = path.relative_to(ROOT).as_posix()
        slots = []
        for question in quiz.get("questions") or []:
            answers = question.get("answers") or []
            correct = [i for i, a in enumerate(answers) if a.get("correct")]
            if len(correct) == 1 and len(answers) > 1:
                slots.append(correct[0])
        if len(slots) < 4:
            continue                      # too few items to say anything
        examined += 1
        counts = Counter(slots)
        top, hits = counts.most_common(1)[0]
        widest = max(len(q.get("answers") or []) for q in quiz["questions"])
        if hits / len(slots) <= 0.67:
            continue                      # spread enough to be unguessable
        findings.append(Finding(
            where,
            f"{hits} of {len(slots)} scored items put the right answer in "
            f"position {top + 1} of {widest}",
            "Answering by position scores full marks without reading."))
        if not quiz.get("shuffle", False):
            findings.append(Finding(
                where, "and shuffle is false, so Canvas will not redistribute it",
                "canvas/build_course.py maps this key to quiz[shuffle_answers]. "
                "Set it true, and fix the authored distribution as well: a "
                "shuffle is a delivery setting and the file is the record."))
    return examined
```

Real output, this session:

```
answer positions: examined 9; 14 problem(s)
  - content/quizzes/w1-self-check.yaml: 6 of 6 scored items put the right
    answer in position 1 of 4
  - content/quizzes/w1-self-check.yaml: and shuffle is false, ...
  [... w2 through w7, and nothing on week0-self-assessment or final-exam]
```

Fourteen findings, seven quizzes, no false positives: the two properly
distributed banks are silent. Five minutes of work protects 84 points and the
132 wrong-answer feedback entries that are currently unreachable.

### 2.2 Nothing may be graded on a field the artifact does not carry

This is the highest-value check on the list: 117 points across four weeks, and
it is the one that turns "the rubric asks for an artifact the lab does not
produce" from a recurring observation into a build failure.

```python
def _artifact_schema(week: int) -> tuple[str | None, set[str]]:
    """The exact key set the week's export cell writes.

    Resolved statically, one hop back. The export cell calls
    save_artifact("weekN_x.json", record); `record` is a dict literal that
    embeds names; each such name is followed to the function that produced
    it, and that function's dict literals are the row schema. Reading every
    dict literal in the notebook instead would be wrong in a way that hides
    the defect: week 6 prints a screen table carrying `confidence` two cells
    above the export, which is precisely the number the file does not hold.
    """
    export, funcs, assigns = None, {}, {}
    for index, source, tree in _code_cells(week):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs[node.name] = node
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Name):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigns[target.id] = node.value.func.id
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "save_artifact" and len(node.args) == 2:
                export = (node.args[0], node.args[1], tree)
    if not export:
        return None, set()
    name_node, record, tree = export
    artifact = name_node.value if isinstance(name_node, ast.Constant) else None
    keys, seen = set(), set()

    def harvest(node):
        for inner in ast.walk(node):
            if isinstance(inner, ast.Dict):
                keys.update(k.value for k in inner.keys
                            if isinstance(k, ast.Constant) and isinstance(k.value, str))
            if isinstance(inner, ast.Name) and inner.id in assigns \
                    and assigns[inner.id] not in seen:
                seen.add(assigns[inner.id])
                if assigns[inner.id] in funcs:
                    harvest(funcs[assigns[inner.id]])

    target = record.id if isinstance(record, ast.Name) else None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == target for t in node.targets):
            harvest(node)
    harvest(record)
    return artifact, keys


# A page names a field of the artifact when it shows a `name:` line inside a
# block introduced as the file's contents.
FIELD_LINE = re.compile(r"^\s*([a-z][a-z0-9_]{2,})\s*:", re.MULTILINE)


def check_graded_fields_exist(findings: list[Finding]) -> int:
    """Every field a rubric, discussion or quiz shows the attached file
    holding has to be a key the export cell actually writes.

    Week 6's 72-point criterion says "before and after numbers, both of which
    the attached file shows", and its 36-point band punishes citing a number
    the file does not show. compare_guarded() writes eleven fields and
    confidence is not one of them, so the top band is unreachable in every
    section and the band below it is where the obvious student action lands.
    Nothing compared the two documents.
    """
    examined = 0
    for week in range(1, 8):
        artifact, keys = _artifact_schema(week)
        if not keys:
            continue                      # a .txt week; see the note below
        for path in (CONTENT / "rubrics" / f"w{week}-lab.yaml",
                     CONTENT / "discussions" / f"w{week}-discussion.md",
                     CONTENT / "assignments" / f"w{week}-lab.md",
                     CONTENT / "quizzes" / f"w{week}-self-check.yaml"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            where = path.relative_to(ROOT).as_posix()
            blocks = re.findall(r"<pre><code>(.*?)</code></pre>", text, re.S) \
                + re.findall(r"```(?:json|text)?\n(.*?)```", text, re.S)
            for block in blocks:
                named = set(FIELD_LINE.findall(block))
                if not (named & keys):
                    continue              # not a picture of this file
                examined += len(named)
                missing = sorted(named - keys)
                if missing:
                    findings.append(Finding(
                        where,
                        f"shows {artifact} holding field(s) it does not carry: "
                        + ", ".join("`" + m + "`" for m in missing),
                        "The export cell writes only: " + ", ".join(sorted(keys))))
    return examined
```

Real output, this session:

```
graded fields: examined 5, 1 problem(s)
  - content/quizzes/w6-self-check.yaml: shows week6_guardrails.json holding
    field(s) it does not carry: `confidence`, `verdict`
      The export cell writes only: body_end_index, body_start_index,
      confidence_floor, email_body_chars, email_id, emails, escalate,
      escalate_reason, fenced_body_chars, final_answer, guard_fence_check,
      model, payload_placement, problems, session_tokens, steps, stop_reason,
      token_cap_per_run, tokens, tokens_written, usable_tools, verdict_changed,
      verdict_with_guardrails, verdict_without_guardrails, week
```

**It catches one of the four, and I want to be honest about why.** The
literal-block form is the only form this version can read. The other three
name their field in prose — "the indicators your model listed", "what the last
step added", "before and after numbers". Those need a declaration, not a
parser.

**So the check has a second half, and the second half is the real design.**
Add to each rubric criterion and each discussion item an optional
`requires_fields:` list, and assert it against `_artifact_schema(week)`:

```yaml
# content/rubrics/w6-lab.yaml
- description: Guardrail judgment
  points: 72
  requires_fields: [confidence_without_guardrails, confidence_with_guardrails]
```

That is one line per graded criterion, about fifteen lines across the course,
and it makes the relation the rubric asserts machine-checkable in both
directions: a rubric that names a field the export drops fails, and an export
cell edited to drop a field a rubric names fails. It also gives weeks 1 and 7 —
whose artifacts are `.txt` and have no parseable schema — a hook, by letting
`requires_fields` name a line label the writer must emit (`Recommended
action:`) and grepping the notebook's `report_lines.append(` literals for it.

`check_points()` (section 0.1) is where this belongs, and fixing that function
to read `modules[].items` is a prerequisite.

### 2.3 Both arms of a narrated comparison must read the same message

```python
def _fields_read(name, funcs, param=0, seen=None) -> set[str]:
    """Keys read off a function's `param`-th argument, followed into calls.

    A taint walk, not a type checker. The argument's name is tainted, an
    assignment from it taints the target, and passing it to a local function
    recurses with that function's matching parameter. It reports what a code
    path can see of one object, which is the only question here.
    """
    seen = seen or set()
    if (name, param) in seen or name not in funcs:
        return set()
    seen.add((name, param))
    function = funcs[name]
    args = [a.arg for a in function.args.args]
    if param >= len(args):
        return set()
    tainted, found = {args[param]}, set()
    for node in ast.walk(function):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name) \
                and node.value.id in tainted:
            tainted |= {t.id for t in node.targets if isinstance(t, ast.Name)}
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and node.value.id in tainted and isinstance(node.slice, ast.Constant):
            found.add(node.slice.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == "get" \
                and isinstance(node.func.value, ast.Name) \
                and node.func.value.id in tainted \
                and node.args and isinstance(node.args[0], ast.Constant):
            found.add(node.args[0].value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            for position, arg in enumerate(node.args):
                if isinstance(arg, ast.Name) and arg.id in tainted:
                    found |= _fields_read(node.func.id, funcs, position, seen)
    return found


# Each entry is a comparison the course narrates as controlled: the week, what
# the page claims, and the entry points of the two arms. A week that adds one
# adds a line here, which is the point -- the claim becomes a declaration
# somebody has to write down before the page can make it.
CONTROLLED_COMPARISONS = [
    (6, "cell 11's 'the fence is the only thing that changed'",
     ["run_triage", "loop_prompt"], ["guarded_triage"]),
    (3, "week 3's grounded / ungrounded comparison",
     ["classify_email"], ["classify_grounded"]),
]


def check_comparison_arms(findings: list[Finding]) -> int:
    """The two arms of a comparison the course calls controlled must read the
    same fields of the same message.

    Week 6 prints "The two columns are the same agent on the same message. The
    fence is the only thing that changed." The guarded arm reads
    hidden_html_text -- which is where the injection lives, and which the
    undefended arm never touches -- so the guarded column is told the attack is
    there and the undefended column is not. A student's control on the clean
    twin moved 5 of 5, which is what a second variable looks like.
    """
    for week, claim, arm_a, arm_b in CONTROLLED_COMPARISONS:
        funcs = _notebook_functions(week)
        a = set().union(*[_fields_read(n, funcs) for n in arm_a])
        b = set().union(*[_fields_read(n, funcs) for n in arm_b])
        if a == b:
            continue
        findings.append(Finding(
            f"lab/notebooks/w{week}-lab.ipynb",
            f"{claim}: the two arms do not read the same message. "
            f"only {'+'.join(arm_a)}: {sorted(a - b) or 'none'}; "
            f"only {'+'.join(arm_b)}: {sorted(b - a) or 'none'}",
            "Any field one arm reads and the other does not is a second "
            "variable in an experiment the page calls controlled."))
    return len(CONTROLLED_COMPARISONS)
```

Real output on week 6, this session:

```
lab/notebooks/w6-lab.ipynb: cell 11's 'the fence is the only thing that
changed': the two arms do not read the same message.
only run_triage+loop_prompt: none; only guarded_triage:
['hidden_html_text', 'reply_to']
```

Two fields, one of them the injection channel itself. This check would have
fired the day `guarded_facts_text()` was written, and it fires on a static read
with no model call, in under a second.

**What it does not catch.** It compares *inputs*, not *instructions*. The
`LOOP_INSTRUCTIONS + CLASSIFY_INSTRUCTIONS` → `GUARD_RULES` swap and the
dropped known-good host list are constants, not message fields, so this check
is silent on them. A companion assertion — the set of module-level string
constants each arm concatenates must differ only by the constants the claim
names — is the natural next piece and I have not written it.

---

## 3. Recurrence: why the apparatus did not generalise

**Six of this round's findings are the same defect class as last round's.**

| this round | last round, `course-review-2026-09-07.md` | class |
|---|---|---|
| 1.5, four export cells missing graded fields (117 pts) | §3, "the rubric asks for an artifact the lab does not produce" (47 pts) | a value that is sent but never read back |
| 1.6, week 1 TODO 1 wording, check cell passes the wrong answer | §5, "no check cell is ever tested against a wrong answer" | a check with no failing fixture |
| 1.2, `schema_errors()` never called with V2 | §5, `backup_my_work`/`restore_my_work` "have never been executed by any check" | shipped code with zero coverage |
| 1.1, week 6's comparison is not the comparison described | §8, `week6_injection_test.py` "built and never run" | a claim about the guardrails with no evidence |
| §2 of your report, mechanisms that never fire | §4, `score_batch()` "passes just as happily when the counters are swapped" | a check that runs over zero interesting cases |
| the site freshness gap | §5, "the gate's filesystem is a strict superset of the student's" | the gate runs where the bug cannot appear |

And the seventh is the sharpest: **section 0.1 of this document is §5's own
lesson recurring inside the tool written to apply it.** Commit `d9c59f9` is
titled "Three gates were reading another course, and two were checking
nothing", it added the `HARNESS_CHECKS` skip-and-announce mechanism, and it
left `check_points` and `check_quiz_points` iterating empty lists and printing
`ok`. The fix was applied to the two checks that were noticed and not to the
class.

**Why it did not generalise. Three reasons, in order of how much they explain.**

**1. The lesson was recorded as prose and the fix as a special case.** "A check
that runs over zero items and passes loudly" is written down in
`verify_content.py` lines 660-665 as a comment, and enforced by a hand-curated
set literal, `HARNESS_CHECKS`, naming two checks. A comment cannot fail a
build and a hand-curated set does not grow when someone adds a check. The
generalisation is mechanical and takes twenty lines: **make every check return
the number of items it examined, and fail the run when a check that is not
explicitly declared inapplicable examines zero.** Every check in section 2
returns that number for this reason.

```python
for label, check in CHECKS:
    findings = []
    examined = check(findings)
    if examined == 0 and label not in DECLARED_INAPPLICABLE:
        findings.append(Finding(label, "examined nothing and reported ok",
                                "A check with no items is not a passing check. "
                                "Either its input moved or its selector is wrong."))
```

Run today, that turns `check_points` and `check_quiz_points` from green to red
in one line each, without anyone having to notice them.

**2. Each fix was scoped to the artifact that failed, not the relation that
failed.** Week 7's missing file produced `check_site_files.py`, which asserts
*this* relation (notebook opens X → site serves X) beautifully and asserts no
other. The 47 unearnable points produced a note in a review document and no
code. The pattern across both rounds is that a **defect in a file** reliably
produces a tool, and a **defect in a relation between two files** reliably
produces a paragraph. Every one of this round's six confirmed findings is a
relation: notebook↔rubric, notebook↔quiz, notebook↔page, prompt A↔prompt B,
repo↔served site, schema↔validator. The apparatus has one relation checker
(`check_chain.py`, function↔function across weeks) and it is the best tool in
the repository.

**3. The umbrella was broken, so nothing forced the parts to be run together.**
`preflight` has not been able to complete against this course since `builder/`
existed (section 0.2). The five lab tools are not in it. When there is no
single command, "run the gates" becomes "run the gate I am thinking about",
and a gate nobody runs is indistinguishable from a gate that passes. This is
the cheapest of the three to fix and it is the one that makes fixes 1 and 2
stick.

---

## 4. The site freshness gap: the gate

The live site served a `w7-lab.ipynb` that predated `6f7c0d4`. Fourteen of
fifteen notebooks matched by hash, one did not, nothing reported it. The
student then reviewed a week 7 that was missing the false-positive attribution
check — the very cell added to fix the previous round's §4 finding.

`stage_notebook_site.py` builds the correct tree and, per
`course-review-2026-09-07.md` §5, had zero callers. It now has one:
`check_site_files.py` stages a throwaway tree to check against. **Nothing
compares either tree to what is actually being served.**

### The design

Three parts. The first is the gate; the second and third are what make the gate
mean something.

**Part 1 — a manifest, produced by the tool that does the staging.**
`stage_notebook_site.py` already walks every file it stages. Have it write
`site-manifest.json` into the output tree as its last act:

```json
{"built_at": "2026-09-08T04:12:09Z",
 "source_commit": "6f7c0d4",
 "source_tree_dirty": false,
 "files": {"w7-lab.ipynb": "sha256:1f3c…", "corpus/data/playbook.md": "sha256:…"}}
```

`source_commit` from `git rev-parse HEAD`, `source_tree_dirty` from `git status
--porcelain` over the staged sources. A manifest built from a dirty tree is a
manifest that cannot be checked against a commit, and saying so is the point.

**Part 2 — `check_site_fresh.py <base-url>`: fetch, hash, compare.**

```
GET <base>/site-manifest.json          -> the manifest the site was built from
for each entry: GET <base>/<path>      -> sha256 it, compare
```

Then re-stage locally from the current working tree and compare that manifest
to the served one. Three outcomes, and the third is the one that matters:

- **fresh** — served manifest hashes match the served files, and the served
  manifest matches a local re-stage.
- **behind** — the served manifest names a commit that is an ancestor of HEAD.
  Report the commit distance and every path whose hash differs. This is a
  deploy that has not happened; it should fail a release gate and warn on a
  content gate.
- **inconsistent** — a served file's hash does not match the served manifest's
  own entry for it. **This is the case that produced the defect**: a partial
  or interrupted deploy, where fourteen files updated and one did not. The
  manifest alone cannot catch it, which is why part 2 fetches the files and not
  just the manifest.

It needs no credentials, makes fifteen-odd GETs, and is read-only against the
site. It is the only check in this apparatus that would have to run against
`notebook.bashtion.dev`, and it must run there — every other gate in this
repository runs against the repository, which is the structural complaint from
last round's §5 restated.

**Part 3 — make the manifest the deploy's own precondition.** The rebuild
script (`/usr/local/sbin/jupyterlite-rebuild`, per `STATE.md`, which already
refuses to swap a build failing its `pyodideUrl` assertion) refuses to swap a
tree whose manifest does not verify against the tree it just built. That turns
"one file did not update" from a silent condition into a refused deploy, at the
only moment anyone can act on it.

**When it runs.** After every deploy, and — this is the part that would have
caught this run — **as the first action of any review, human or agent, that
claims to be reviewing the published course.** A review of a stale site is a
review of a different course, and the reviewer cannot tell.

**What it is not.** It does not check that the served site *works*. A student's
JupyterLite kernel, `piplite`, the CORS preflight and the proxy are separate
concerns with their own probes in `STATE.md`. This gate answers exactly one
question — *is the thing being served the thing in the repository* — and
answering that one question cleanly is worth more than answering it as part of
something larger.

---

## 5. Judging the existing checks

### Load-bearing

**`check_chain.py`** — the best tool here. It compares 60 functions across
seven notebooks, 49 of them carried by more than one week, plus every
instructor solution against its lab, using `ast.unparse` so formatting
differences do not register. It found 11 real drifts when it was written
(`STATE.md`, 2026-09-05). It ran clean this session. It is the one relation
checker in the repository and it is the template for sections 2.2 and 2.3.
One caveat: `functions()` skips any cell matching `TODO_BANNER`, which is
correct for TODO cells and means the student-written code is out of scope by
design — that is a stated limit, not a hole.

**`check_tools.py`** — 56 records, three tools, every field compared against
`corpus-spec.json`. Genuinely exhaustive over its domain, ran clean, and its
domain is the one place where "the tools and the manifest disagree" would
poison everything downstream. Load-bearing and finished.

**`check_site_files.py`** — the model of a check written from a specific
defect. 204 literal path references across 22 notebooks, checked against a
tree staged by the shipping tool rather than the repository. Its docstring
explains the environment mismatch that made every other gate blind. It is
narrow *on purpose* and its narrowness is documented at line 60-65 (non-literal
paths are skipped, because they cannot be resolved without running the
notebook). That is honest. The consequence — every email id in the course is
invisible to it (1.4) — is a gap in the apparatus, not a fault in the tool.

**`stage_notebook_site.py`** — load-bearing and better than it was. The
`project()` key projection and `unprojected_labels()` content gate are the
right answers to last round's §1.1: they moved the decision from "is this
filename allowed" to "which fields of this file ship". `never_ship` remains a
basename denylist, and `unprojected_labels()` is what covers for that. One
soft spot: `unprojected_labels()` recognises an answer key by a fixed set of
seven telling field names at line 61. A future answer file using none of those
seven names ships silently. That set should be derived from the corpus schema,
not typed.

### Theatre

**`tools/preflight.py`** — currently the most misleading artifact in the
repository. It is titled "run every gate, in one command", it crashes on this
course before finishing, three of its five gates target a directory that does
not exist, and none of the five checks that understand this course are in it.
A contributor who runs it and reads the traceback learns nothing; a contributor
who runs it in a hurry sees three green lines first. Either point it at this
course and add the five, or make it refuse to run against a tree it does not
support.

**`verify_content.check_points()` and `check_quiz_points()`** — vacuous, and
loudly green (0.1). Not theatre by intent; theatre by outcome, which is worse,
because their names describe exactly the check whose absence cost 117 points.

**`run_notebook.py --expect-artifact`** — the flag reads like an artifact
assertion and is a substring search over printed cell output (`artifact_written()`,
line 121). It passes if any cell prints the filename. It does not open the
file, does not parse it, does not check it is non-empty. Every one of the four
export-cell defects in 1.5 would pass it, and did.

### One edit from vacuous

**`verify_content.check_quiz_answers()`** — the most valuable check in the file
and one line from being much more valuable (1.3). Also one edit from being
vacuous in the other direction: `CONTENT / "quizzes"` is a glob, so a quiz
directory renamed or a course whose quizzes live elsewhere makes it silently
examine nothing, with no announcement. The coverage counter in section 3 fixes
that class for the whole file at once.

**`verify_content.check_paths()` and `check_commands()`** — currently real
(they scan 73 authored files). Both are selector-driven: `check_commands` fires
on `python -m X` and `python X.py` patterns only, and `d9c59f9`'s own commit
message records that `check_commands_resolve` was vacuous twice for exactly
this reason — "it matched only `python -m`, so a scene running `python lab.py`
was invisible to it, and every scene list in this course is slides, so the loop
never ran". A regex selector over authored prose is one house-style change away
from matching nothing, every time.

**`check_chain.py`'s solution comparison** — `SOLUTIONS.glob("w?-lab-solution.ipynb")`
at line 115. If the solutions move or are renamed, the loop runs zero times and
the tool still prints "every solution matches its lab". Same shape, same fix.

### `litellm-verify`

**Not assessable from this repository.** It is referenced three times in
`STATE.md` (53 checks, then 62 of 62) and its source is not in the tree; I
found no file, no script and no reference to it outside those three lines. What
`STATE.md` records about it is the strongest evidence in the repository that it
is load-bearing: it caught a missing `access-control-allow-origin` on the Caddy
short-circuit that **every curl-based check passed before and after**, and it
asserts model pricing because "without the rates LiteLLM records tokens and
stores spend 0.0 while looking healthy". Both are real assertions about what
the server did rather than what the request asked for.

Two things follow. **A tool that is load-bearing and lives outside version
control is a single point of failure with no history** — its 53 checks became
62 with no diff anyone can read. And **the course's own budget and cost figures
rest on it**: the student's `$0.010571` reading and every per-week cost in the
run report are LiteLLM's computed spend, which is correct only because
`litellm-verify` asserts the per-deployment rates. That is a lot of weight on
an unversioned script. It should be in this repository, and it should be the
sixth entry in a working `preflight`.

---

## 6. The harness was wrong four times: what that means for agent-driven review

Four of roughly thirty reported problems were the export pipeline, not the
course: dropped `comments` feedback, 0-based cell numbering, links stripped as
angle-bracket markup, duplicated headings. A fifth (the student's own
"I know the exam's answer positions") was the student's script globbing too
widely.

**The important structural fact is that the student was right every time.**
It reported, accurately, what the artifact in front of it contained. The
information was destroyed before it arrived. That is not a reasoning failure
and no amount of "be more careful" would have prevented it.

**Three of the four were claims about an absence** — a missing section name, a
missing URL, a shifted number. The student worked this out itself and wrote the
rule down mid-run: *a claim whose whole evidence is an absence is a claim about
my copy, not the course.* That is the correct generalisation, it is better
stated than most test-strategy documents manage, and it is the reason its
section 2 survives intact: every finding kept there is a claim about something
**present and wrong** — a label printed over data it does not describe, a
variable named 025 loading 016, a check cell that passes a broken answer.

So the conclusion is not "trust agent review less". It is narrower and more
useful:

**An agent reviewer's evidence is its pipeline, and the pipeline is untested
software written for one run.** The course's own tooling gets three gates and a
staging tool; the export that fed the reviewer got none. A reviewer's input
channel deserves the same treatment as a student's — because it *is* a
student's, with one extra transformation in the way.

### What would make the next run trustworthy

**1. Round-trip the export before the reviewer sees it.** For each page,
re-render from the exporter's output and diff against the Canvas source on the
properties that matter: link count, heading count and order, code-block count,
list-item count, and — for quizzes — the presence of every `feedback` and
`comments` field. Four of the four harness defects are a count changing. All
four are caught by one diff that takes seconds and needs no model. This is the
single highest-value fix for the method, and it is smaller than any check in
section 2.

**2. Freeze and hash the reviewed artifact.** Run `check_site_fresh.py`
(section 4) as the first action of the review and record the manifest in the
reviewer's notes. Then the question "which revision was reviewed" has an
answer, and the week 7 staleness is a line in the log rather than a discovery
three weeks later.

**3. Show the reviewer the raw form on request.** Give it one verb —
"show me the unprocessed source of this page" — used only when it is about to
file a claim about an absence. Three of the four defects die there, at the cost
of a handful of calls.

**4. Keep asking for mechanisms, not outcomes.** "Did the thing this week
teaches actually fire in your run?" produced 1.1 and the two never-firing
mechanisms in weeks 2 and 5, and it is the question no static check can ask.
That is where an agent reviewer earns its cost, and it is worth protecting from
the noise the first three items remove.

**5. Two reviewers on one pipeline is one measurement.** Both the 2026-09-07
and 2026-09-08 runs used the same export, and the link defect survived four
weeks of one run without being recognised. A second reviewer reading the same
export would have confirmed the false finding rather than caught it. Independent
confirmation means an independent channel, not a second reader.

---

## 7. Verified / asserted ledger

**Verified in this session, from source or from a command I ran:**

- `check_points` and `check_quiz_points` iterate zero rows and print `ok`;
  `course.yaml` has no top-level `assignments`/`quizzes`/`discussions`.
- `preflight` raises `FileNotFoundError` on `ROOT/"labs"`; `cartridge --check`
  raises `KeyError: 'ref'`; neither has ever completed against `builder/`.
- The five `lab/tools/` checks are absent from `preflight`'s check list.
- 43 scored self-check items across w1-w7, all correct at position 0, all with
  `shuffle: false`; `week0-self-assessment` and `final-exam` distributed.
- `build_course.py:591` maps `shuffle` → `quiz[shuffle_answers]`.
- `compare_runs()` (w3 cell 13) drops `indicators` **and `category`**.
- `one_line()` (w5 cell 9) is `json.dumps(result)[:80]` and is written into the
  persisted trace, not only the screen; the w5 export also drops `final_answer`.
- `compare_guarded()` (w6 cell 15) writes 11 keys, no `confidence`; both token
  fields come from `guarded`, and `guarded_triage()` calls `start_run()` first.
- `w6-self-check.yaml` q4 shows `verdict:` and `confidence:` as fields of
  `week6_guardrails.json`; neither is a key of that file.
- w6 rubric top band requires numbers "which the attached file shows"; the
  36-point band penalises citing a number it does not show.
- `loop_prompt()` has no body; `run_triage()`'s closing call is a fresh
  `ask_model()` with no body; **`start_messages()` line 536 does put
  `parsed["body_text"]` in every undefended loop turn.**
- `guarded_facts_text()` appends a `Hidden text in the HTML part:` line;
  `guarded_triage()` reads `parsed["reply_to"]`; neither reaches the
  undefended arm. Taint analysis: guarded-only fields are
  `['hidden_html_text', 'reply_to']`.
- `w3-lab.ipynb` cell 12 line 4 is `parsed_025 = load_email("016", ...)`;
  cell 10 prints header `email 025` over `CHECK_FACTS["016"]`;
  `CHECK_PAIR = ["005", "016"]`.
- `w1-lab.ipynb` has no `assert`; the check cell is **cell 8** and tests only
  `CHECK_ANSWER.startswith("ask_model() is not written")`.
- `budget_left` / `backup_my_work` / `restore_my_work` are defined in the seven
  labs only, in none of the sidebars, and not in week 0, whose cell 130 of 130
  is markdown. `restore_my_work()` is called in none of the fifteen notebooks.
- `check_chain.py` (60 functions, 49 shared), `check_tools.py` (56 records) and
  `check_site_files.py` (204 references, 22 notebooks) all pass and all examine
  a non-trivial number of items.
- All three checks in section 2 execute and produce the output shown.

**Asserted, from your report or the student's, not independently checked:**

- `schema_errors()` returns "summary has to be a list" for a correct week 7
  answer, and `schema_errors(` is never called with `OUTPUT_SCHEMA_V2` at any
  of its sixteen call sites. *(Read out of the notebooks by a subagent in this
  session; I read the dispatch chain and `OUTPUT_SCHEMA_V2` myself and agree,
  but I did not execute the function.)*
- Week 5's `step_cap` cannot fire; week 2's retry never fires; week 6's four
  controls fired 0 of 11.
- The served `w7-lab.ipynb` predated `6f7c0d4` and fourteen of fifteen hashes
  matched.
- Every measurement in the run: 39/40, $0.010571, ~31 hours, 5-of-5 verdict
  flips on 013 and 024.
- `litellm-verify`'s 62 checks and their content. The tool is not in this
  repository.

---

## 8. If only three things are built

1. **The coverage counter in `verify_content`** (section 3, reason 1). Twenty
   lines. It fails two gates today that have been green since this course
   existed, it fixes the class rather than the instances, and every other check
   written from here on inherits it. This is the one that makes the rest
   trustworthy.
2. **`check_graded_fields_exist` plus `requires_fields:`** (section 2.2). 117
   points across four weeks, in criteria no student in any section can
   currently earn, and it makes the rubric↔artifact relation declarative for
   the first time.
3. **`check_site_fresh.py`** (section 4). It is the only gate that would run
   where the course is actually delivered, which is the structural complaint
   from the previous round, still unaddressed.

`check_answer_positions` (2.1) is not on that list only because it is five
minutes of work and does not need a decision. Do it first anyway.
