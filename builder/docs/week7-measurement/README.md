# Week 7, measured on the code it ships

**Run:** 2026-09-10. **Twelve passes, 828 model calls**, through
`https://api.bashtion.dev/v1` at the notebook's own temperature, one email per
request. **Read `prereg-claude.md` first.** It was written before the first
call and carries three dated amendments, two of which void or overturn
something below.

## Why this had to happen

Week 7 is the accuracy week and its own accuracy had never been measured on the
code it ships.

The only record was `content/video/runs/w7.json`, recorded 2026-09-05 against
`http://localhost:11434/v1` — the retired ollama endpoint — from the solution
notebook as it stood then. Week 6's rebuild (6186ab6) afterwards replaced
`build_guarded_prompt(facts_text, body)` with
`build_guarded_prompt(grounding, body)` fed by a new `grounding_text()`, which
week 6's own measurement showed moves verdicts. Three shipped claims rested on
the stale numbers: the walkthrough video, the wrap-up's model-size section, and
the week 7 row of `docs/model-selection.md`.

## The rig

`mkprewritten.py` extracts the solution notebook's own pre-written cells into
an importable module. `w7_pass.py` runs one pass through them. Nothing restates
a function the student runs, and `w7_summarise.py` computes only aggregates.

Two refusals, carried over from week 6:

- The rig will not start unless one live call returns non-zero tokens.
- Every input is digested into the result file — each `.eml`, both notebooks,
  the rig, the driver. Passes whose digests differ are not comparable, and the
  reader can check that without trusting the script.

Digests were identical across all six teaching passes and all six batch passes.

## The holdout, where the decision was made

Twenty batch emails, 026 to 045. They appear in no earlier week, so no prompt
in this course was tuned against them. Three passes a model.

| | `granite-3b` | `granite-8b` |
|---|---|---|
| Correct, of 60 | 34 | 48 |
| Accuracy | **0.567** | **0.800** |
| Per-pass | 0.550, 0.600, 0.550 | 0.800, 0.800, 0.800 |
| False positives | 26 | 11 |
| False negatives | **0** | **0** |
| Rows with no verdict | 0 | 1 |
| Distinct emails missed | 9 | 4 |
| Escalation agreement | 37/60 = 0.617 | 39/60 = 0.650 |
| Verdicts that moved across passes | 1 of 20 | 2 of 20 |

`granite-3b` misses nine of the ten benign emails, eight of them in all three
passes. It misses no attacks at all.

`granite-8b` misses four: 036, 037 and 041 every pass, 045 twice.

## The teaching set, kept as the comparability check

Twenty-four emails, 001 to 025 without 013, the same set the 2026-09-05 video
run scored. Three passes a model.

| | `granite-3b` | `granite-8b` |
|---|---|---|
| Correct, of 72 | 51 | 66 |
| Accuracy | 0.708 | 0.917 |
| Per-pass | 0.708, 0.708, 0.708 | 0.917, 0.917, 0.917 |
| False positives | 12 | 6 |
| False negatives | 9 | **0** |
| Escalation agreement | 48/72 = 0.667 | 53/72 = 0.736 |

Against 2026-09-05's `granite-3b` on the same set: 16/24 = 0.667 then, 0.708
now, and the error profile inverted — 0 false positives and 8 false negatives
then, 12 and 9 now. The prompt changed underneath it, which is the whole reason
this measurement exists.

## What was decided, and what was not

**Week 7 stays on `granite-3b`.** Not because it scored better. It did not.
Because week 7 measures the agent the student built across six weeks, and that
agent runs on `granite-3b`. Amendment 3 of the pre-registration carries the
reasoning and the record that the pre-registered threshold, which also happened
to block the switch, is not the reason.

**The wrap-up's model claim is reversed.** It said 8B "scored a little worse
than 3B" and that size does not pay behind a facts block. Both halves are false
on the shipped code, in both directions, and the page now carries the measured
table instead.

**No page may say the agent does the job.** Aggregate holdout accuracy is 0.567
and human review stays universal, under the rule fixed in the pre-registration
before anything ran.

## What the repairs did, measured

The four code repairs were made before this ran. What the passes show about
them:

- **`schema_errors()` no longer rejects a correct answer.** Zero rows in 144
  carried the false `summary has to be a list`. Before the repair every week 7
  row carried it.
- **The `sentences` branch found a real behaviour instead.** `granite-8b`
  writes one semicolon-joined sentence where the schema asks for two. Under the
  first version of `review_decision()` every one of those forced a human
  review — 12 of 72 rows — which is why amendment 2 narrowed `usable_answer()`
  and voided six passes.
- **`no_decision` fired once in 120 batch rows**, on `granite-8b` pass 3, email
  035: a closing answer that came back with every key missing. It was recorded
  as no decision rather than as a false negative, escalated to a person, and
  the note still printed six lines. That is the whole repair working on a real
  failure.
- **Every note was six lines in every pass**, both models, both sets.

## The coincidence, recorded so it is not read as a bug

In the voided first run, both arms scored escalation agreement 17, 15, 17 —
49 of 72 each. The per-email decisions were not alike: on pass 1 each arm
agreed with the key on 17 emails and only 11 were the same emails, six going
each way. `granite-3b` sent 11 of 24 to a person, `granite-8b` sent 21. The
count was recomputed from the per-email records to confirm it was not a
degenerate calculation. It was not.

## Files

| File | What it is |
|---|---|
| `prereg-claude.md` | Written before the first call. Three dated amendments |
| `mkprewritten.py` | Extracts the notebook's own cells into a module |
| `w7_pass.py` | Runs one pass, writes one result file with input digests |
| `w7_summarise.py` | The tables above, and the pre-registered checks |
| `teaching-granite-{3b,8b}-pass{1,2,3}.json` | Six teaching passes |
| `batch-granite-{3b,8b}-pass{1,2,3}.json` | Six holdout passes |

## What this measurement does not license

It says nothing about any set other than these two, nothing about any model
other than these two, and nothing about mail outside this synthetic corpus. The
batch is balanced ten and ten, and `sender:lookalike_domain` is a required
indicator on 16 of the 31 malicious records in the corpus, so accuracy here is
accuracy on this batch and not an estimate of phishing accuracy anywhere else.
