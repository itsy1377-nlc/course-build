# Why week 1's temperature demonstration does not work, measured

**Run:** 2026-09-08, granite-3b through the course proxy, **300 calls, zero
failures**. Raw record: `granite-3b-300-runs.json`. Script: `w1_study.py`.

Three prompt shapes on email 001, five temperatures, twenty runs each.

| shape | the instruction sent |
|---|---|
| `prose` | the lab's current one: "In two sentences, say whether it looks like a phishing attempt, and why." |
| `one_word` | "Answer with one word, phishing or legitimate, and nothing else." |
| `word_plus` | "Answer with one word, phishing or legitimate, then one short sentence saying why." |

## What 300 runs say

    shape      t=0.0   t=0.2   t=0.7   t=1.0   t=1.3     (distinct answers out of 20)
    prose      15/20   20/20   20/20   20/20   20/20
    one_word    1/20    1/20    1/20    2/20    2/20
    word_plus   4/20   10/20   20/20   20/20   20/20

    mean pairwise similarity
    prose      0.540   0.314   0.134   0.094   0.101
    one_word   1.000   1.000   1.000   0.914   0.912
    word_plus  0.754   0.683   0.386   0.369   0.369

**Prose saturates immediately.** At temperature 0.2 it is already twenty
distinct answers out of twenty, and it stays there. There is a real similarity
gradient underneath, but nothing a student can see by looking, and answer length
scatters just as widely at every setting (standard deviation 82 to 94 words at
all five temperatures). Length cannot be the signal either.

## What a student actually sees

Bootstrapped from the real answers, 4,000 draws per cell. "Shows it" is the
share of students whose low-temperature group has **fewer distinct answers**
than their high-temperature group.

| shape | temperatures | n per side | mean distinct, low | mean distinct, high | shows it |
|---|---|---|---|---|---|
| **prose (today's lab)** | 0.2 vs 1.0 | **3** | **2.87** | **2.86** | **11%** |
| prose | 0.2 vs 1.0 | 8 | 6.72 | 6.73 | 34% |
| word_plus | 0.2 vs 1.0 | 6 | 4.12 | 5.31 | 73% |
| word_plus | 0.0 vs 1.0 | 5 | 2.31 | 4.52 | 97% |
| **word_plus** | **0.0 vs 1.0** | **6** | **2.43** | **5.31** | **99%** |
| word_plus | 0.0 vs 1.0 | 10 | 2.78 | 8.03 | 100% |

**The current demonstration is not weak. It is absent.** Its two group means are
2.87 and 2.86 -- the same number -- and it lands in the claimed direction 11% of
the time, which is worse than a coin. Raising the sample size does not rescue it,
because prose is saturated at every temperature the course would use. The
2026-09-07 student was not unlucky; the experiment has never worked.

## What does work

A one-word verdict followed by one short sentence, at **0.0 against 1.0, six runs
a side**: 99%. It also fixes a second problem nobody had connected to this one.
The assignment asks for "one screenshot... with all six answers readable in it",
and prose answers run 33 to 403 words. `word_plus` answers run 9 to 28.

The remaining 1% has to be designed for, not hidden: the notebook should count
the repeats itself and print the count, and the assignment must accept a run that
did not separate. A student who sees it fail should be told that is a result.

---

# Round two: five models, four probe shapes, and two rejections

Added 2026-09-08 after the first round. About 1,700 live calls in total, zero
lost to errors. Raw records are the JSON files beside this page.

## The decision

**Week 1 uses granite-8b, with a word-and-one-sentence probe, at 0.2 against
1.0, six runs a side.** Measured at 98% of student-sized batches showing the
effect, and **zero answers with a wrong verdict at either temperature**.

## Why not the number probe, which measured perfectly

It was recommended, approved, and then killed by looking at the values instead
of the spread.

Email 001 is `malicious / credential_phish`. Asked for "one number from 0.00 to
1.00 giving the chance that it is a phishing attempt", granite-3b answers
**`0.00` twenty times out of twenty** at both 0.0 and 0.2. The separation
statistic was a flawless 100% and the answer underneath was wrong, which is
worse than no demonstration at all. Four rewordings were tried
(`wording-study.json`):

| wording | at t=0.2 | verdict |
|---|---|---|
| "the chance that it is a phishing attempt" | `0.00` x20 | wrong |
| "0.00 means certainly safe, 1.00 certainly phishing" | `0.00` x13, `1.00` x7 | incoherent |
| "a higher number means more likely to be phishing" | `0.2` x19 | wrong |
| one word, then a confidence number | `phishing 0.99` x20 | right, but 3 distinct at t=1.0 |

This is the same trap the rest of this project keeps finding: a summary number
that looks right sitting on top of content that is not. **Print the values.**

## Why not granite-3b at all

granite-3b is not accurate enough on this email to run the experiment honestly.
Asked for a word and a sentence, it calls a credential phish *legitimate*:

    t=0.0    0 of 20 wrong
    t=0.2    2 of 20 wrong
    t=1.0    8 of 20 wrong

A student running that would learn "a high temperature makes the model wrong",
conflating variation with accuracy. granite-8b is 0 of 20 wrong at every
temperature tested.

## Why not the label probe

The design proposed LINK / IDENTITY / URGENCY / REQUEST and counting how many
different labels appeared. On granite-3b the count is 2 at both temperatures --
IDENTITY 39/40 at t=0.0, IDENTITY 26 / LINK 14 at t=1.0 -- so it separates in
**11% of batches at n=10**. A `tag` variant reaches 94% but only at temperature
1.3, and its vocabulary (PAYROLL / SIGN_IN / URGENT / EXTERNAL_LINK) matches
nothing else in the course; week 2's category enum is `credential_phish`, `bec`,
`vendor_fraud`, `malware_delivery`, `spam`, `legit_external`, `legit_internal`.

## The full ranking, separation and correctness together

| model | shape | pair | n=6 | wrong at low T | wrong at high T |
|---|---|---|---|---|---|
| **granite-8b** | **word+sentence** | **0.2 v 1.0** | **98%** | **0%** | **0%** |
| granite-8b | word+sentence | 0.0 v 1.0 | 100% | 0% | 0% |
| granite-8b | prose | 0.0 v 1.0 | 99% | 0% | 0% |
| gemma-3-12b | prose (prompt unchanged) | 0.2 v 1.0 | 99% | 0% | 0% |
| granite-3b | `tag` label | 0.2 v 1.3 | 94% | 0% | 0% |
| granite-3b | word+sentence | 0.0 v 1.0 | 99% | 0% | **40%** |
| granite-3b | prose (today's lab) | 0.2 v 1.0 | **30%** | 0% | 20% |
| qwen3-14b | any | any | 26-61% | — | ignores "one word" entirely |
| gemma-3-12b | number | any | **0%** | — | identical at every temperature |

Two models were briefly re-served for this and removed again; the proxy is back
to granite-3b and granite-8b, and the study key is revoked. **Qwen3-14B is
disqualified generally**: it answers a request for one word with 150 to 400
words, at every temperature, with `reasoning_effort: none` set.

**No single model and shape works everywhere.** gemma is the best model on
prose and the worst on numbers. granite-8b is the best overall and flat on two
of the three label probes. That is worth saying in the course rather than
hiding.

## A correction to this page's first round

The first round reported granite-8b's verdict stability at 80% at t=1.0. That
was an artifact of a crude extractor counting an answer as "mixed" when the
*rationale* contained the word legitimate. Checking whether the answer opens
with a wrong verdict: granite-8b is **0 of 20 wrong** at every temperature.

## Deferred, to re-evaluate

The rejected number probe surfaced a real thread: `confidence` is a field in
week 2's schema (`{"type": "number", "low": 0.0, "high": 1.0}`), the value week
6's `CONFIDENCE_FLOOR = 0.7` routes on, and a line in week 7's note -- and the
SOC practitioner's review calls that floor "an uncalibrated model self-report".
Week 1 could be where a student first watches that number move.

**Not built now.** It is a curriculum decision rather than a measurement one, it
would add weight to the least-prepared week, and the probe that would carry it
returns a wrong number on granite-3b. Revisit when week 6 is fixed, since that
is where the floor lives.
