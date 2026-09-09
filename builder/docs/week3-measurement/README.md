# Why week 3's facts block does not move the verdict, measured

**Run:** 2026-09-08, granite-3b through the course proxy at temperature 0.2.
128 classifications: 8 emails, 8 runs each, both conditions. Script
`w3_ground.py`, raw record `granite-3b-8x8.json`.

The harness is built from week 3's own pre-written cells plus the solution's
`build_facts()` and `format_facts()`. Body-alone uses week 2's
`classify_email()`; with-facts uses the shipped `classify_grounded()`. Nothing
is reimplemented, so a result here is a result about the notebook as shipped.

Objective 3.2 is **"Report which verdicts changed after you added the facts
block."**

## 1. The lab runs other weeks' emails

`corpus/ground_truth.json` tags every teaching email with the weeks it belongs
to. Week 3's designed set is **001, 004, 005, 006, 017, 025**. Cell 14 runs
**001, 004, 005, 016, 017, 019**.

    016 is tagged weeks [6].   019 is tagged weeks [4].
    006 and 025 are tagged week 3 and are never run.

The blind run found the naming inconsistency and read it as the prose failing
to follow a moved email set. It is the other way round. The wrap-up, the
overview video, self-check Q3 and the notebook's own TODO cells all name 005
and 025, which is the corpus design. The assignment page, the reading and cells
7, 10, 12 and 14 drifted. Cell 10 prints the header `email 025` over 016's
values and cell 12 assigns `parsed_025 = load_email("016", ...)`. Nothing
errors, so nothing catches it.

**The prose is right. The code drifted.**

## 2. And correcting the set would not have fixed the objective

| id | truth | designed to move | body alone | with facts | moved |
|---|---|---|---|---|---|
| 001 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| 004 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| **005** | benign | malicious to benign | malicious 8 | malicious 8 | **0/8** |
| 006 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| **016** | malicious | benign to malicious | malicious 8 | malicious 8 | **0/8** |
| **017** | benign | uncertain to benign | benign 8 | **malicious 8** | **8/8** |
| **019** | benign | malicious to benign | malicious 8 | malicious 8 | **0/8** |
| **025** | malicious | benign to malicious | malicious 8 | malicious 8 | **0/8** |

**Every email designed to move stays put**, including both of the ones the
corpus intends as the demonstration pair. The only movement in the set is 017,
flipping benign to malicious 8 times out of 8, when the truth is benign and the
design was uncertain to benign. **Zero movements toward truth anywhere.**

Objective 3.2 is therefore demonstrated only by a deterministic false positive.
The course hedges the non-movement well -- three places say a row that did not
move is a real result, and the rubric scores the student's fact choices rather
than the model's answers, which is exactly what week 1 lacked -- so this costs
no student any points. The week's central claim is still unsupported.

## 3. Two things underneath it

**granite-3b reads malicious from the body alone on 7 of 8 emails**, including
005 and 019, which are benign. It will not be talked out of malicious, so
"facts exonerate a benign email" cannot demonstrate itself with this model on
this corpus. Only 017 reads benign from the body, and that is the one the facts
flip the wrong way.

**The facts block makes 017 worse.** Every fact on it is clean:

    SPF result: pass          DKIM result: pass        DMARC result: pass
    Display name mismatch: False                       Gateway scan result: clean
    Attachment names: []      Reply address: None

`format_facts()` renders every value with `str()`, so booleans arrive as
`False`, empty lists as `[]` and absent values as `None`. The blind run
reported the model citing "Display name mismatch: False" among its reasons for
calling 017 malicious.

**Hypothesis, not yet tested:** a small model reads the salient phrase and drops
the negation, so a block of clean facts reads as a block of security concerns.
Rendering booleans and empties as natural language would settle it. Codex is
reviewing whether that is the right first experiment before any calls are spent.

## What this does not yet say

The measurement covers one model at one temperature on eight emails. It does
not say the facts block is useless -- 3.1 and 3.3 are about choosing and
justifying facts, and the rubric grades those directly. It says the *verdict*
is the wrong thing for 3.2 to measure on this model, and that the pair chosen
to demonstrate movement demonstrates none.

## Running these

`w3_ground.py` expects `/tmp/w3_prewritten.py` and `/tmp/w3_solution_fns.py`,
extracted from the lab and solution notebooks, and a key at
`/root/.w3-eval-key`. It runs from `~/eval/builder` on the litellm guest so the
corpus path walk resolves. Same shape as `docs/week2-measurement/`.
