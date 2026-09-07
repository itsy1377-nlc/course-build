# Where a small model disappoints

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College
**Instructor package, 2026-09-04.** Not student facing.

This page exists so you do not grade a student for the model's behaviour.

Every number comes from `builder/docs/week5-model-test.json` (294 agent runs, six emails,
eleven configurations), its write-up `week5-model-test.md`, `serving-stack-shape.md`
beside it, or `builder/docs/phase1-blueprint/grade-distribution-and-tokens.md`. Every rate
below is measured. The course-level token counts in section 4 are projections, and they say
so where they appear. The shipped configuration is
`granite4.2:3b` with reasoning off, in the design where the student's code owns the stop.
Granite 4.1 3B is the fallback.

---

## 1. It does not stop when it has enough

**What you will see.** A week 5 trace that starts with the right check, reaches a sound
verdict, then runs one or two more checks it did not need, at a token count above the
walkthrough video. The verdict is usually still right.

**What causes it.** Nothing in the model marks "I now have enough" as a place to stop. An
available tool reads as an invitation.

**What to tell the student.** The loop is bounded by their code, not the model's judgment. A
longer trace that ends for the recorded reason is a passing run.

**Measured.** In the 60 runs where the model chose freely and stopped for itself
(`granite4.1-free` and `granite4.2-noreason-free`, 30 each), the first tool was the expected
one 55 times, but the exact expected path came back only 25 times. 30 of those 60 ran the
expected path and then kept going; none stopped short. Granite 4.1 alone:
first tool 25/30, whole path 15/30. Where code owns the stop, the run ended for the recorded
reason 136 times out of 138.

---

## 2. Tool order differs between the two models

**What you will see.** Two students with correct code submit traces in different orders. On
Granite 4.1 the trace may never start with the sender check at all.

**What causes it.** The two models order the same three tools differently under the same
prompt. That is the model, not the student's loop.

**What to tell the student.** Order is not graded. Their job is a bounded loop that ends for
a defensible reason and records what it did.

**Measured, in the shipped week 5 design.** `granite4.2:3b` with reasoning off started with
`check_sender_reputation` 29 times in 30 and produced the exact expected path 29/30. In the
same design `granite4.1:3b` started with the sender check 0 times in 30, opening with
`check_urls` 20 times and `lookup_recipient` 10, for an exact path of 0/30. It still ended
the run for the recorded reason 30/30 and reached the right verdict 20/30. One line telling
4.1 to start with the sender check moved first-tool-right only to 15/30.

That is why the week 5 rubric grades the stop reason and the trace, not the order. A rubric
that graded order would fail students on whichever model was loaded that week.

---

## 3. Email 012 is called malicious, and the answer is benign

**The email.** `012-elmhollow-badge-access`. Ground truth in `builder/corpus/spec/corpus-spec.json`
is `verdict: benign`, `difficulty: hard`. SPF, DKIM and DMARC all pass. The sender has no
record in the reputation file, the portal host is on neither list, and the message asks for
technician names and truck numbers.

**What you will see.** Students reporting their agent "got it wrong" on 012.

**What causes it.** A first-seen sender on an unlisted host asking for a list of names is
what business email compromise looks like. The model reads real indicators and is wrong
anyway.

**What to tell the student.** This is a false positive, not a bug. Ask which single fact
drove the call. That is the question week 6 and week 7 are built on.

**Measured.** 49 runs touched that email and the verdict was right 13 times. Granite 4.1
called it malicious in all 20 of its runs, across all four designs. Granite 4.2 with reasoning
off called it malicious 5/5 in the free and guided designs, and benign in 8 of 10 runs where
code owns the stop.

Week 5 grades the loop here, never the verdict. Week 7 should expect 012 in its false
positive column.

---

## 4. Reasoning mode returns nothing at all

**What you will see.** A cell that finishes with no error and no answer, while the token
counter jumps anyway. Students will call this a broken notebook.

**What causes it.** Granite 4.2 has reasoning on by default, and reasoning tokens come out
of the same answer budget. The budget runs out mid-thought, `content` comes back empty,
`finish_reason` is `length`, and the thinking sits in a separate `reasoning` field the
notebooks never read.

**What to tell the student.** Check that the configuration cell printed
`{'reasoning_effort': 'none'}` on its Extra fields line and that `MODEL` is unedited.

**Measured.** At the 512 token answer budget the labs use, `granite4.2-reason-free` returned
no answer in 18 of 18 runs, every one ending with `finish_reason` `length` and empty content,
at 2,224 tokens and 10.7 seconds per run. At a 4,096 token budget it works and
still should not be used: across those 36 runs, 7,874 tokens and 82.8 seconds per triage, one
run at 174.3 seconds, against 3,813 tokens and 4.1 seconds for the shipped configuration.
Reasoning left on is also projected to cost about 164,000 extra tokens per student across
the course. That is the gap between a 552,300 token course total with reasoning on and
388,560 with it off (`builder/docs/phase1-blueprint/grade-distribution-and-tokens.md`,
section 3.1). It is a projection, not a run: the totals it subtracts are built partly from
the projected figures that document's section 3.3 lists, and the week 6 row that dominates
the gap was never run.

Two traps. Granite 4.1 rejects any `reasoning_effort` value with an HTTP 400 reading
`"granite4.1:3b" does not support thinking`, so the configuration cell sets that field by
model name. And `"think": false`, `chat_template_kwargs` and `options.think` are silently
ignored, so switching thinking off the wrong way gives no error and no change.

---

## 5. Two identical runs give two different answers

**What you will see.** Students finding their results do not match each other, or your
walkthrough.

**What causes it.** The model samples each word, so one run is one sample. This is week 1's
entire lesson, arriving early.

**What to tell the student.** One run is evidence of one run. Any claim about the agent needs
several.

**Measured.** Of the 66 configuration-and-email cells that ran one email more than once, 17
produced more than one distinct tool sequence and 12 more than one distinct verdict. The
shipped configuration disagreed with itself too: on 012 it returned benign four times and
malicious once in five runs, and on `011-po-20431-thread-reply` one run in five returned an
answer that would not parse.

**The opposite failure, also real.** Granite 4.1 at temperature 0 returned byte-identical
text on four identical plain questions. Week 1 sends one prompt six times, three at 0.2 and
three at 1.0. Three low-temperature answers that look alike is still a correct run. The
criterion asks which answer differed most and at which temperature, which the 1.0 runs
supply.

---

## 6. Malformed JSON, which week 2 treats as normal

**What you will see.** A `tries` column showing 2 or 3, sometimes a row reading `no answer`
with `ok` False, sometimes a `TypeError` from a `None` result, which week 0 section 10 names.

**What causes it.** The reply did not load as JSON, or it loaded and broke the schema.

**What the retry does.** `classify_email(parsed, max_tries=3)` asks again with the reported
problems attached, up to three tries, then returns `None`. Every try, passed or failed, is
written to `week2_classification.json` with its `problems` text.

**What to tell the student.** A try count above 1 is the design working. All four passing on
try one is the likely case; their file carries three recorded failures in its `sample_checks`
block regardless.

**Measured.** Across the 240 runs with reasoning off, the final answer failed to parse 3
times, once in the shipped configuration's own 30 runs. Strict JSON came back valid 3 of 3 on
both models with reasoning off, no code fences and no prose. With reasoning on at a 1,024
token cap, an empty answer arrived in 4 of 6 runs.

---

## What was not measured

- **Only week 5 was measured end to end.** Weeks 1, 2, 3, 4, 6 and 7 have no run sweep. The
  serving stack figures are single-digit run counts on a grocery notice, not the corpus.
- **Only six emails**, one per loop shape. The rest of the corpus, including whatever week 7
  batches, has no per-email measurement.
- **Prompt injection was not measured.** Week 6 is the course differentiator and no number
  here says how either model behaves against the injected email.
- **The hosting was not measured.** What the week 5 sweep records is Ollama 0.32.15 and one
  model request at a time (`week5-model-test.md`, "The world, asserted before measuring").
  The machine and the thermal state are not in those results at all. The Phase 0 probe beside
  them ran on an Apple M3 Pro, warm (`serving-stack-shape.md`, sections 1 and 3.4), and the
  week 5 sweep is assumed to have run the same way. Cold starts, concurrent students and the
  college's own stack are unknown, so the seconds figures will not transfer.
- **Student-edited prompts were not measured.** Every run used one of the five system prompts
  written into `builder/lab/eval/week5_loop_test.py`, one per design plus one for the closing
  verdict turn. There is no week 5 lab yet for a prompt to belong to, so no run measured a
  prompt a student had edited.
- **Model versions drift.** These numbers are tied to two blob digests, `6fd349357287c7ff`
  and `40577dc168a3a9ad`. Re-run `python3 builder/lab/eval/week5_loop_test.py --all` each term
  before trusting a rate here.
- **Small samples.** Five trials per cell, three in the reasoning configurations. A rate like
  29/30 is a strong signal, not a precise one.
