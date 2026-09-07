# How to author a quiz for this course

Quizzes live in `content/quizzes/<ref>.yaml`. The cartridge generator turns
them into Classic Quizzes and QTI question banks.

**Classic Quizzes only.** New Quizzes is not available in open-source Canvas.

---

## The file format

```yaml
ref: m1-comprehension
title: "Module 1 Comprehension"
description: |
  Plain-language text shown before the quiz starts. Say what it covers, how
  many attempts, and that AI use is permitted but unprofitable here.
shuffle_answers: true
questions:
  - id: m1-q1
    type: multiple_choice
    item_type: defect_injection
    outcome: O1
    points: 5
    text: |
      Question text. Markdown works, including fenced code blocks.
    answers:
      - text: "The correct one"
        correct: true
        feedback: "Why it is right, in one sentence."
      - text: "A wrong one that a confused student would pick"
        correct: false
        feedback: "Why it is wrong, and what to reread."
    general_feedback: |
      Shown to everyone after they answer. This is where the teaching goes.
```

**Types supported:** `multiple_choice`, `true_false`, `multiple_answers`,
`short_answer`, `numerical`, `essay`.

`short_answer` takes a list of accepted strings, matched case-insensitively:

```yaml
    type: short_answer
    accepted: ["3", "three"]
```

`numerical` takes an exact value with optional tolerance:

```yaml
    type: numerical
    value: 4
    tolerance: 0
```

`essay` is hand-read, so use it sparingly. The whole course budgets five hours
of hand-reading. Every essay item must be justified in a `note:` field.

---

## The six item types, and why they exist

AI assistance is permitted throughout this course and the design does not try
to detect it. Instead, every comprehension item is anchored to something that
exists only inside that student's own run. That makes AI use permitted but
unprofitable, which is a more honest position than a ban nobody can enforce.

Set `item_type` on every question to one of these:

| `item_type` | What it does | Why a model cannot do it for them |
|---|---|---|
| `indexical` | "Enter the value of the `tool` field on line 3 of your `ledger.jsonl`." | The model has no access to their run |
| `output_prediction` | "Given this input and *your* retry settings, how many requests reach the endpoint before the exception?" | Depends on choices they made |
| `defect_injection` | Six versions of a function; exactly one is correct. Or: "which line number introduces the injection sink?" | Directly assesses outcome 6; guessing is 1 in 6 |
| `two_tier` | Tier 1 asks what happens, tier 2 asks why. Credit only when both are right. | Collapses lucky guessing to 1 in 36 |
| `structured_findings` | Submit a finding as fixed-schema JSON: attack class, affected tool, evidence line, remediation control, in-scope boolean. | Evidences outcome 5 classification at zero grading cost |
| `scope_classification` | Eight candidate actions; mark each in or out of authorization. | Evidences the authorization clause of outcome 5 |
| `recall` | Plain knowledge check. | Use sparingly, and never for more than a third of a quiz. |

**Every comprehension quiz carries at least three `defect_injection` items.**
That is where outcome 6 lives and it is the cheapest high-quality evidence in
the course.

---

## Rules

1. **Tag every item with an `outcome`.** The exam export is the per-student,
   per-outcome score matrix that program assessment asks for, and it only works
   if every item is tagged.
2. **Points in a quiz must add up to the points in `content/course.yaml`.**
3. **Feedback on every answer, right and wrong.** A wrong-answer feedback line
   says why it is wrong and what to reread. This is the only teaching a student
   gets after a wrong answer in an asynchronous course.
4. **No trick questions.** A distractor should be something a confused student
   would genuinely believe, never a word game.
5. **Reading level applies.** Short sentences, common words, one idea per
   sentence. Code inside a fenced block is exempt.
6. **Never grade on the model's prose.** An item asking "did the output contain
   the words 'api key'" teaches the exact mistake the course exists to correct.
7. **No em dashes.**
8. **Invent nothing.** Every framework identifier, version, and quotation must
   be one already used in `docs/course-blueprint.md` or the lab code.

---

## Facts you can build items on

Lab file paths: `agent/llm.py`, `agent/tools.py`, `agent/loop.py`,
`agent/trace.py`, `agent/mock_model.py`, `agent/system_prompt.txt`,
`target/app.py`, `harness/runner.py`, `harness/detectors.py`,
`harness/cases/*.yaml`, `runs/ledger.jsonl`, `runs/traces/*.jsonl`,
`runs/reports/*.json`, `config/lab.config.yaml`.

Run artifacts a student has: `runs/ledger.jsonl` with one JSON line per tool
call carrying `run_id`, `ts`, `step`, `tool`, `args`, `allowed`, `reason`,
`error`, `result_chars`. Harness reports carry `status`, `hits`, `completed`,
`errored`, `rate`, `flaky`, `detector`, `evidence`, `owasp`, `atlas`.

Their three canary tokens are `CANARY-SYSPROMPT-...`, `CANARY-CUSTOMER-...`,
`CANARY-KB-...`, derived from their student ID.

Defect classes worth using for `defect_injection` items, chosen because
language-model reviewers systematically miss them:

- a retry loop that retries on 4xx and burns the daily quota
- `except Exception: pass` swallowing a tool error
- validation that checks a key is present but never checks its type
- raw tool output going back into the system prompt
- a path allowlist checked before use but not at use (time of check, time of use)
- a recipient allowlist that compares before lowercasing
- a canary check that uses `in` on the wrong haystack
- a detector that returns True on a refusal because it matched a keyword
