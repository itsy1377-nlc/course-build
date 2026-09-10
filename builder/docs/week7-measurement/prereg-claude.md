# Week 7: what will be measured, written before anything runs

**Written:** 2026-09-10, after the code repairs and before the first model
call. Nothing in this file may be edited after a run starts. Corrections go in
dated amendments at the bottom, and an amendment says what it changes and why.

## Why there is a measurement at all

Week 7 is the accuracy week and its own accuracy has never been measured on the
code it ships.

The only week 7 run on record is `content/video/runs/w7.json`, recorded
2026-09-05 against `http://localhost:11434/v1` — the retired ollama endpoint —
from the solution notebook as it stood then. Since that run:

- Week 6's rebuild (6186ab6, 2026-09-09/10) changed the prompt week 7 builds.
  `build_guarded_prompt(facts_text, body)` became
  `build_guarded_prompt(grounding, body)`, fed by a new `grounding_text()`
  carrying the classification instructions, the facts block and the known-good
  host list. Week 6's own measurement showed that change moves verdicts.
- Today's repairs changed `schema_errors()`, added a `no_decision` bucket to
  `score_batch()`, and replaced the escalate flag on the note with
  `review_decision()`.

So three claims currently in the course rest on numbers that no longer describe
the code: the walkthrough video's 16 of 24, `w7-wrap-up.md`'s "granite-8b
scored a little worse than 3B on our run", and the week 7 row of
`docs/model-selection.md`.

## What is being decided

1. Whether week 7 ships on `granite-3b` or `granite-8b`.
2. Whether the wrap-up's model-size claim can stand, be reversed, or must go.
3. What `content/video/runs/w7.json` records, and whether the walkthrough video
   has to be re-recorded.

## The arms

Two arms, three complete passes each, run alternately (3b, 8b, 3b, 8b, 3b, 8b)
so that any drift in the service falls on both.

| Arm | Model | Set | Passes |
|---|---|---|---|
| A | `granite-3b` | the 24 teaching emails, 001-025 without 013 | 3 |
| B | `granite-8b` | the same 24 | 3 |

**The set is the teaching emails, not the batch, and that is deliberate.** The
walkthrough video reads the teaching set so the video never shows a student the
answers to their own twenty. Keeping the measurement on the same set is what
makes it comparable to the 2026-09-05 record. It also means this measurement
does **not** license any statement about batch accuracy.

Everything else is held: the same proxy, the same temperature, the same
`reasoning_effort`, the same code, the same order, one email per request.

## Arm C, the batch, added before any model call was made

Added 2026-09-10, while the model-call count for this measurement was still
zero. It is written here rather than as an amendment because nothing had run.

Arms A and B decide which model week 7 uses. They say nothing about the twenty
emails a student actually scores, and the reading, the rubric and the wrap-up
all describe that run. So the batch is measured too.

| Arm | Model | Set | Passes |
|---|---|---|---|
| C | whichever model arms A and B select | the 20 batch emails, 026-045 | 3 |

Arm C runs **after** A and B, on the model they choose, through the shipped
solution notebook rather than a separate rig, so what is measured is what a
student runs.

**Arm C decides nothing about the model.** It answers three questions the
content depends on:

1. Does `no_decision` ever fire on a real run, and how often?
2. What is escalation agreement under `review_decision()`, against the 10 of 20
   that the pre-repair control flag could reach at best on a working run?
3. Is the error profile false-negative-heavy on the batch as it was on the
   teaching set?

**Fixed now for arm C:** no page may quote a single pass. Anything written into
`w7-content.md`, `w7-wrap-up.md` or the video from arm C is a range across the
three passes, or it is not written.

## What gets recorded, per pass

Per email: verdict, category, confidence, indicators, recommended_action,
summary, escalate (the control flag), escalate_reason, schema_problems,
review_decision, stop_reason, tokens.

Per pass: correct, accuracy, false_positives, false_negatives, **no_decision**,
escalation agreement, guardrail fires by reason, rows with no verdict, session
tokens, wall-clock seconds.

Also recorded, because week 6's rig proved they matter: the sha256 of every
`.eml` read, of both notebooks, and of the rig itself, into the result file. A
pass whose input digests differ from the others is void.

## Thresholds, fixed now

**Harness health, all of which must hold or the run is void and is re-run, not
reported:**

- Zero uncaught exceptions in the harness.
- Every one of the 24 emails produces a row in every pass.
- `schema_errors()` raises on nothing.
- No pass shows a `schema_problems` entry naming `summary` on an answer whose
  summary is a well-formed two-sentence string. (This is today's repair. If it
  fires, the repair is wrong and the measurement stops.)

**The model decision:**

- Week 7 stays on `granite-3b` unless `granite-8b` beats it by **more than five
  percentage points** of aggregate accuracy across all three passes **and**
  produces no more false negatives per pass **and** fails no more often.
- If `granite-8b` wins on that test, the cost is stated in the same sentence as
  the win. 8b is about three times the price.
- A single best pass is never quoted. All three passes are reported as a range.

**What is not a threshold.** There is no accuracy floor below which week 7
fails to ship. A prototype that measures badly still teaches measurement, which
is the week's objective. What a bad number forbids is *deployability language*:
if aggregate accuracy is below 0.50, no page may describe the agent as doing
the job, and the human-review recommendation must say review stays universal.

## Predictions, recorded now so they can be wrong

1. `granite-3b` accuracy will land between 0.55 and 0.75 on the 24 teaching
   emails — above the 0.667 of 2026-09-05, because `grounding_text()` restored
   the classification instructions and the known-good host list.
2. The error profile will stay false-negative-heavy. I expect at least twice as
   many false negatives as false positives.
3. `no_decision` will be 0 or 1 per pass.
4. Escalation agreement under `review_decision()` will be **higher** than the
   12-13 of 24 recorded on 2026-09-05, because the action route now carries it.
5. `granite-8b` will not clear the five-point bar.

Prediction 4 is the one that would most embarrass the repair if it fails, and
it is the reason this file exists.

## What would make me stop and not report

- Input digests differing between passes.
- Any pass where the proxy returns a non-zero rate of transport errors.
- A `schema_problems` entry on a well-formed summary, per the harness health
  rule above.

---

## Amendment 1, 2026-09-10, after arms A and B and before arm C

**What changed.** Arm C now runs **both** models on the batch, three passes
each, and **the model decision rests on the batch rather than on the teaching
set.** The teaching set keeps its job as the comparability check against the
2026-09-05 record.

**Why.** Arms A and B came back the opposite way round from prediction 5:

| Arm | Aggregate over 72 | Per-pass range | FP | FN | No decision |
|---|---|---|---|---|---|
| `granite-3b` | 49/72 = **0.681** | 0.667 - 0.708 | 14 | 9 | 0 |
| `granite-8b` | 66/72 = **0.917** | 0.917 - 0.917 | 6 | **0** | 0 |

That is 23.6 points, against a five-point threshold, with zero false negatives
and no verdict moving across three passes. On the rule this file fixed in
advance, week 7 switches to `granite-8b`.

**And that is exactly why the decision should not be made here.** The 24
teaching emails are the set this course's prompts were developed against. Every
week from 1 to 6 read them while its prompt was being written. Deciding a model
on the set it was tuned against is the same error this course already made once
— `model-selection.md` records that week 6's model was chosen on two
hand-written prompts no student builds, and the correction was to run the
comparison through the code the student runs. The matching correction here is
to run it over emails nobody tuned against.

The twenty batch emails, 026 to 045, appear in no earlier week. They are the
holdout. The decision moves there.

**What this does not change.** The thresholds stay exactly as written above:
more than five points, no more false negatives, no more failures, cost stated
in the same sentence as the win, no single best pass quoted. They are now
applied to arm C's numbers instead of arm A and B's.

**A coincidence, recorded so it is not read as a bug.** Both arms scored
escalation agreement 17, 15, 17 — 49 of 72 each. The per-email decisions are
not alike at all: on pass 1 the two arms agree with the key on 17 emails each
and only 11 are the same emails, six going each way. `granite-3b` sends 11 of
24 to a person and `granite-8b` sends 21. They arrive at one number by
different routes. I recomputed the count from the per-email records to be sure
it was not a degenerate calculation, and it is not.

**Predictions for arm C, recorded before it runs.**

6. `granite-8b` will still beat `granite-3b` on the batch, but by less than the
   23.6 points it won by on the teaching set.
7. `granite-3b` will be false-positive-heavy on the batch. The one batch run
   already on record, the student gate of 2026-09-10, called 8 of the 10 benign
   emails malicious. That is the opposite of its teaching-set profile, where it
   ran 14 false positives to 9 false negatives, and the opposite again of the
   2026-09-05 record of 0 false positives to 8 false negatives.
8. `granite-8b` will over-escalate. It chose a review action on 21 of 24
   teaching emails where the key wanted 14.

Prediction 7 is the one that matters for the reading, because
`w7-content.md` has to describe an error profile a student will recognise.

## Amendment 2, 2026-09-10, arms A and B are void and are being re-run

**What changed in the code.** `usable_answer()` no longer treats every schema
problem as making a note unusable. It now asks only whether a line the note
needs came back at all:

    for key in NOTE_INPUT_KEYS:
        if result.get(key) is None:
            return False
    return True

**Why.** Arm A and B showed what the old definition did. `granite-8b` writes
one semicolon-joined sentence where the schema asks for two, on **12 of 72
rows**, and under the old definition every one of those forced a human review.

Escalating a case because the model's prose ran to one sentence instead of two
is the same category error this week's rubric repair removed a few hours
earlier: scoring a system on a stylistic property of model output. A
one-sentence summary is a thin note. It is not an unreadable one. The check
still records it, the student still reads it, and it no longer sends a case to
a person.

**What this voids.** Every escalation-agreement number in arms A and B. The
accuracy, false positive, false negative and no-decision counts are untouched
by this change, because `review_decision()` feeds none of them. Even so, the
six pass files are discarded and both arms are re-run, because a result file
whose input digests no longer match the shipped notebook is not evidence about
the shipped notebook, and picking through which fields survived would be
exactly the kind of selective reporting this file exists to prevent.

**Recorded so the re-run cannot quietly improve on it.** What arms A and B said
before they were voided:

| Arm | Aggregate | Per-pass | FP | FN | ND | Escalation agreement |
|---|---|---|---|---|---|---|
| `granite-3b` | 49/72 = 0.681 | 0.667-0.708 | 14 | 9 | 0 | 49/72 |
| `granite-8b` | 66/72 = 0.917 | 0.917 | 6 | **0** | 0 | 49/72 |

`granite-3b` missed 8 distinct emails, `granite-8b` missed 2 — 012 and 019,
both false positives, in all three passes. Both arms missed those same two.

If the re-run moves accuracy at all, that is a finding in itself and it gets
written down, because nothing in this change touches the verdict path.

## Amendment 3, 2026-09-10: the decision, and a question that should not have been asked

**Week 7 stays on `granite-3b`.** The config cell does not change.

**The threshold did not decide it.** For the record, here is what the holdout
said, twenty unseen emails, three passes each, input digests identical:

| Arm | Aggregate | Per-pass | FP | FN | ND | Escalation agreement |
|---|---|---|---|---|---|---|
| `granite-3b` | 34/60 = **0.567** | 0.550, 0.600, 0.550 | 26 | **0** | 0 | 37/60 = 0.617 |
| `granite-8b` | 48/60 = **0.800** | 0.800, 0.800, 0.800 | 11 | **0** | 1 | 39/60 = 0.650 |

`granite-8b` beat `granite-3b` by 23.3 points and cleared the five-point bar.
It also returned one malformed answer in 60 rows where `granite-3b` returned
none, and the rule fixed in advance says the challenger must "fail no more
often". By the letter, the switch was blocked.

**And the letter did not matter, because the question was wrong.** Week 7 does
not ask which model scores best. It asks the student to measure *the agent they
built*, and they built it on `granite-3b` across six weeks. The week 7 spec
says so: *"Nothing else about the agent changes. The decision path built in
week 6 runs untouched."* A config cell naming a different model would hand the
student a different system to measure, in the one week whose whole purpose is
finding out what theirs actually does.

This file said as much before anything ran, in the section headed *What is not
a threshold*: **"A prototype that measures badly still teaches measurement,
which is the week's objective."** I wrote that, got a number I did not like,
and went looking for a better model anyway. The user asked "why switch?" and
there was no answer that survived the question.

**The worse agent is the better week.** `granite-3b` calls 9 of the 10 benign
batch emails malicious, 8 of them in all three passes, and misses **no attacks
at all**. That is a real failure mode with a name, and the reading already
teaches it: *"A false positive spends his morning on a message that was fine.
Enough of those and he stops believing the agent."* At 26 false positives in 60
that lands. Objective 7.3 — *"Name one place where a human must still review"*
— is then answered from the student's own evidence rather than from a gesture.

**Cost was not the constraint either, and it should not have been argued.** A
student's batch run costs about $0.005 on 3b and $0.011 on 8b against a $2.00
key. Twice almost nothing.

**What the 8b arm is for instead.** It is content. `w7-wrap-up.md` currently
tells students that 8b "scored a little worse than 3B on our run" and that
"size pays for judgement on thin evidence" but not behind a facts block. On the
shipped stack that is false in both directions: 8b scored 0.800 against 3b's
0.567, behind the facts block, on the same twenty emails. The page and the week
7 row of `docs/model-selection.md` are corrected from these numbers.

**What no page may claim.** Aggregate accuracy on the holdout is 0.567, below
0.50 only for benign mail. Under the rule fixed above, no page describes the
agent as doing the job, and the human-review recommendation stays universal.
