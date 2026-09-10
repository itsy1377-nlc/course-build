# Week 6 repair plan, drafted 2026-09-09

Written after probes 1, 6 and 7, with probe 2 in flight. Every item says what
it changes, what settled it, and what it waits on. Items marked **pending**
are not decided yet and must not be implemented before the probe named lands.

## What is settled, and what it costs

**The eleven-email table is not a comparison.** The guard moves the verdict on
payload-free mail in 65 percent of runs and on payload-carrying mail in 37.5
percent, and the twin pair returns the same verdict in both columns 8 of 8.
The undefended verdict is written by a call that never saw the email.

**The guardrails cost accuracy on the shipped model.** 66 of 88 correct
undefended, 46 of 88 guarded; 32 new false negatives against 12 corrected
false positives. Both twins are ground-truth malicious.

**Three of the four taught controls did nothing in 88 runs.** The fact check
found 0 problems, no confidence landed under the floor, and the cap's number
peaked at 289 against 4,000. The one control that fired is a fifth one no
student surface names, and it reads a corpus property rather than a model
answer.

**The fence can be closed by the attacker**, and the notebook's own check
cannot see it happen.

**The payload does steer the agent**, 8 of 8, in data the lab already collects
and never looks at.

## Code, in `w6-lab.ipynb` and `w6-lab-solution.ipynb`

`run_triage()` and `guarded_triage()` are week 6's own and week 7 carries
copies, so **every code item below is made identically in `w7-lab.ipynb` and
`w7-lab-solution.ipynb`**, and week 7 is re-run before anything ships.

**C1. Put the body in the closing call.** One line in `run_triage()`. The
closing call carries the body of the email the loop ran on, in the same block
`start_messages()` uses, so the guarded arm keeps its fenced copy and the
undefended arm gets the plain body. **Pending probe 2**: ships only if the
payload then moves the undefended verdict at 6 of 8 or better on some model.

**C2. Record what the rubric grades.** `compare_guarded()` adds
`confidence_without_guardrails`, `confidence_with_guardrails` and
`tokens_without_guardrails`. The two undefended numbers must be read on the
line after `run_triage()` returns and **before** `guarded_triage()` is called,
because that function begins with `start_run()`. One more line in the row
dictionary cannot recover a counter that has already been reset. Settled; no
measurement needed.

**C3. Stop printing a false claim.** Cell 11's *"The two columns are the same
agent on the same message. The fence is the only thing that changed."* becomes
an enumeration of what actually differs. Same for `w6-content.md`'s *"Whatever
moves between them is what one paragraph did."*

**C4. The hidden-HTML line.** `guarded_facts_text()` states an absence as a
bare finding — *"Hidden text in the HTML part: no"* — on ten of the eleven
emails, as the last line before the evidence, and only in the guarded arm.
Reword it as scope (*"Checked for text present only in the HTML part: 0
characters found"*) or emit it only when there is something to report.
**Pending probe 5 arm B**, which measures how much of the collapse it carries.

**C5. Sanitize the fence, and let the check see an escape.** `fenced_email()`
neutralizes both markers in the body before wrapping it. `fence_check()` finds
the first end marker after the body opens rather than the last, so an escape
reports as a broken fence instead of a clean one. A pre-written cell shows the
escape and then the sanitized version, at zero model calls, which is the same
idiom weeks 4 and 5 use. Settled by probe 7.

**C6. Wire the control the pages already name.** Three surfaces say
`schema_errors()` is what stops email 023's request for the recipient's report
history. It is never called anywhere in week 6. Confirmed at zero model calls:
on an answer carrying `recipient_report_history` it returns *"the key
recipient_report_history does not belong in the answer"*, while
`guarded_triage()` today silently drops the key on the way into the record. So
the export is safe and the named mechanism is fiction. Call it in
`guarded_triage()` and record its problems alongside the fact check's, without
changing the verdict.

**C7. The token cap. Pending a decision, and it is a real choice.** The cap
reads `RUN_USAGE["answer"]`, which grows by a couple of hundred tokens a run,
against a limit of 4,000. `RUN_USAGE["total"]` is in the same dictionary and
peaked at 8,017 here, against week 5's measured runaway of 60,208. Switching
the number and setting the cap above the measured maximum would let the cap
fire on the runaway week 5 already builds, instead of only on the lowered-cap
cell. The counter-argument is that the course already says three times that
the cap cannot fire on normal work, which is honest, and that changing it
touches week 7. Decide with the probe 2 distribution in hand.

**C8. Name the control that actually fired.** `injection_detected` is a fifth
escalation reason, fires on 014 in 8 of 8, reads `hidden_html_text` rather than
anything the model said, and is read second so it masks the fact check and the
floor beneath it. Name it on a student surface, and say the true thing beside
it: in this corpus hidden HTML is planted on purpose, and in a real mailbox it
is mostly marketing preheader text, so a rule that escalates on it alone is a
control tuned on a corpus meeting an inbox.

## Content

Every item below is a sentence a student reads that the measurement
contradicts. Weeks 3, 4 and 5 each found the same false claim in the reading,
the wrap-up, the self-check **and** the video narration, so each is fixed on
every surface that carries it, not the first one found.

| # | Where | What it says | What is true |
|---|---|---|---|
| P1 | `w6-content.md:32` | "the payload moved the model in most runs" | It moved nothing, 0 of 8, and could not: the verdict call had no body |
| P2 | `w6-content.md:71` | "Email 020 is where the third fires" | The fact check found 0 problems in 88 runs |
| P3 | `w6-content.md:73`, `w6-content-2.md:78`, `w6-wrap-up.md:50`, `w6-self-check.yaml:246` | 009 and 012 sit under the 0.7 floor | 0 of 88 runs landed under it; every confidence was 0.80, 0.85 or 0.95 |
| P4 | `w6-content-2.md:42`, `w6-wrap-up.md` q6 | `schema_errors()` is the data-exposure control | It is never called in week 6. True only after C6 |
| P5 | `w6-content.md:28` | 024 is the same message "word for word" | It goes to a different mailbox, and that changes a tool result |
| P6 | `w6-content.md:49`, `w6-wrap-up.md` q2 | the fence puts 014's hidden text on the facts side | A character count goes there. The text never does, and the fence is not what does it |
| P7 | `w6-self-check.yaml:231` | an export row showing `verdict:` and `confidence:` | Neither is a key of that file. True only after C2 |
| P8 | `w6-discussion.md:16` | "give the number from your file" for 015 | The 015 row holds no number that answers the question. True only after C2 |
| P9 | `w6-content.md:77` | "a normal run here costs far less than 4000" | True of the number the cap reads, false of the run: 8,017 against 4,000 |
| P10 | both video narrations | inherited from the pages above | Re-render after the pages settle |

**P11. The week's headline changes, and this is the real work.** On the shipped
model the guarded prompt costs 23 points of accuracy and every loss is a false
negative. That is not a defect to explain away; it is the answer to objective
6.3, which asks the student to *judge whether* the guardrails reduce risk
enough to accept. `w6-content-2.md` already argues for exactly this reading —
"plan for a share of wrong answers, and decide which kind you would rather
have" — and a false negative is the kind you do not want. The week teaches the
measured result.

## Evidence documents

**E1.** `model-selection.md` puts week 6 on `granite-8b` on the strength of 510
runs whose prompts are not the notebook's, and its week 1 row is stale in the
other direction: week 1 ships `granite-8b` today. Both rows corrected once
probe 2 and probe 4 land.

**E2.** `week6-held-fix.md` says the twin pair works and the corpus needs no
change. It was produced by `lab/eval/week6_injection_test.py`, whose two
prompts are not arms any student runs. Mark what no longer stands rather than
deleting it.

**E3.** `week6-measurement/README.md`'s older run counts and the two partial
result files that lack `usable` and `failed_runs` — the exact fields the README
tells a reader to check first.

## Not doing, deliberately

- **Not editing `decisive_stop()`, `internal_sender` or `build_facts()`.** The
  SOC reviewer is right that they are wrong for real tradecraft, and all three
  are shared with weeks 4 and 5, which are pushed and verified, and are graded
  in four exam items. A week 6 fix would break the chain against a shipped
  week. Logged as cross-week work.
- **Not forcing a control to fire on the graded table.** Weeks 4, 5 and 6 all
  use a pre-written cell that takes the model out and shows the mechanism, and
  says so. That stays. What changes is the signal each control reads.
- **Not re-rendering a corpus email.** The week 5 measurement recorded digests
  for six of them.
- **Not adding a seventh corpus email for the delimiter escape** unless the
  work list says otherwise. 56 emails is a number stated in many documents.
  The escape is demonstrable at zero model calls on a copy built in the cell.

## Found while setting the week 6 baseline, and it belongs to week 5

`ITSY_CONTENT=builder/content python3 -m tools.video.check` reports two
problems **today, before any week 6 edit**:

    w5-overview is out of date with w5-overview.md, w5-content.md. Rebuild it.
    w5-walkthrough is out of date with w5-content.md, w5-lab.md. Rebuild it.

The cause is timing, and it is verifiable from the file times.
`build/video/w5-overview.json` was written at 16:54:45 and
`w5-walkthrough.json` at 16:55:35 on 2026-09-09. `w5-content.md` was modified
at **17:05:06**, ten minutes later. The commit at 17:18 records "14 videos
with nothing stale", so the gate was run before that last page edit and the
week shipped with two videos describing a page that had changed under them.

Nothing is wrong with the pages; the videos need re-rendering. Do it in the
same video pass as week 6's two, and run the gate **last**, after the final
page edit, rather than before it. That ordering is the actual lesson: this
gate only means something if it is the last thing that runs.

## Also found at the baseline: the walkthrough videos quote a retired stack

`builder/content/video/runs/` holds the recorded agent run behind each
walkthrough video. All five were recorded on 2026-09-05 against
`http://localhost:11434/v1` with model `granite4.2:3b` — the ollama stack the
course left on 2026-09-07. Only `w3.json` carries a dated note saying its
result did not reproduce on the shipped model.

Week 6's is the one in scope. `w6.json` is email 034 on granite4.2:3b, and the
walkthrough narration quotes it directly: *"Undefended, the answer parsed on 21
of 21 runs"*, *"Guarded, the answer parsed on 10 of 21"*, *"So fencing the body
made this model's output less reliable, not more."* That last sentence is the
most candid line in the course and it may still be true, but it is currently
evidence from a model no student can call. Probe 1 saw no parse failure at all
in 88 guarded runs on granite-3b.

Re-record the week 6 walkthrough run on the shipped stack in the same pass that
re-renders its video, and carry whatever it shows. Weeks 4, 5 and 7 have the
same stale provenance and are logged rather than fixed here: weeks 4 and 5 are
pushed, and week 7 has not started.

---

# Revised after Codex's review, 2026-09-09

Codex was dispatched with every number attached and asked to attack the
conclusions and the fix. Its report is at `codex-review.md`. It was right
against me on the most dangerous item, and the three load-bearing claims were
verified against the code before being accepted.

## C5 is withdrawn and replaced. It would have shipped a fail-open.

**Verified at zero model calls.** `guarded_triage()` builds `prompt_text` from
the **unsanitized** body, then checks the fence, and takes this branch:

    if fenced:
        email_for_run = fenced_email(parsed)
    else:
        prompt_text = loop_prompt(parsed)

So making `fence_check()` honest — finding the first end marker rather than the
last, which was my proposal — means an attacker who writes `BODY_END` into the
body sets `fenced = False` and **switches the guard off**, silently, landing on
the undefended prompt. I reproduced the branch. My repair would have converted
"the fence record lies" into "the attacker chooses whether the guard runs",
which is strictly worse than the defect it fixes.

**The replacement.** Sanitize the body **once, before it is used at all**, so
`build_guarded_prompt()` and `fenced_email()` both receive the neutralized
text; and **fail closed** — a body that arrived carrying a marker escalates,
and never drops to the undefended path. The teaching point improves too: the
lesson is not only that a delimiter can be escaped, but that the obvious repair
opens a worse hole if the failure branch is not designed.

## What else changed

**The 72-point criterion does not assess 6.2.** It asks for "before and after
numbers", which is unguarded against guarded. A student can earn all 72 points
without ever mentioning 024 or the twin experiment. So the objective is
displayed on screen and graded nowhere. Criterion 2 has to require the twin
comparison and an acceptance rule applied to it, or CLO4 keeps measuring
confident prose.

**Give the judgment an acceptance rule.** Codex's wording, which is better than
anything on the page today: *if an injected malicious email remains benign and
un-escalated, prompt-injection risk is not acceptable.* Then the student
applies it to 013 and 024 against ground truth.

**Drop "every guard-caused move is a false negative" from the repaired week.**
That is probe 1's body-blind baseline. With the body restored, 021 moves benign
to malicious, a **corrected** false negative, and guarded accuracy is 44 of 88
against 40 of 88 undefended. The repaired eleven-email table is not established
yet; it is running.

**The known-good claim is narrowed.** What is established is that in the P0
context, removing the block turns 024 benign 8 of 8. The broad claim that the
verdict rests on the block is not: the block alone did not repair the guarded
prompt and the instructions alone did not either, so this is a
context-dependent interaction. The confirmatory design is a randomized 2x2 —
block present or absent against classification instructions present or absent —
run through the real `guarded_triage()`, with a length-matched neutral-host
placebo and an incorrect block that names Vetchmoor, tool-result order frozen,
and a pre-registered prediction that says whether a main effect or an
interaction is expected.

**The paragraph bundles three treatments** — extra length, a fabricated factual
claim, and an imperative — so the week may not yet claim the imperative is what
works. Three more arms would separate them.

**The body is duplicated in the guarded path**, and my closing-call patch adds
a third copy. That weakens the single-change claim and has to be resolved
before the repaired table is quoted.

**`schema_errors()` is not an information-flow control.** `indicators` accepts
arbitrary strings, so the recipient's report history can ride inside an allowed
indicator and pass. C6 makes the named mechanism real but does not make the
data-exposure claim true. Test for leaked content, not for an extra key.

**Call 024 injection-free, not clean.** It is ground-truth malicious. The
course says "clean twin" throughout.

**Corpus nit, verified:** 024 is addressed to `payroll@pellgrave.example` and
its body still opens "Hello Tobias".

## What is now blocking

1. The 2x2 confirmatory run with the placebo arms, through the real
   `guarded_triage()`.
2. A decision on the body duplication, then the repaired eleven-email table,
   twice, for the noise floor.
3. The fail-closed sanitation design, and a run that proves the escalation
   fires rather than the guard dropping.
