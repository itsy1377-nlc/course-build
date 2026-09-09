# Lab fix log

**A running record. Updated as each week is fixed.** One section per week, plus a
queue at the end of work that is not week-specific.

Its job is to be the list you work from when you circle back: every item says
what to do, where, the command to run, and how you know it worked. Nothing here
has been pushed to Canvas, and no video has been re-rendered.

**Sources.** The defects come from `student-e2e-run-2026-09-08.md` (a blind
student ran the whole course) and `panel-2026-09-08/` (five reviewers read that
run against the source). Measurement records live beside them, one folder per
week that has been measured.

---

## Status

| week | lab code | content | videos | Canvas | notes |
|---|---|---|---|---|---|
| **1** | **fixed** | **fixed** | **rebuilt** | **pushed, verified** | **done** — measured, 1,700 calls; sidebar gap closed |
| **2** | **fixed** | **fixed** | **rebuilt** | **pushed, verified** | **done** — 0.9 reporting ceiling, measured 64/64 retries recover |
| **3** | **fixed** | **fixed** | **rebuilt** | **pushed, verified** | **done** — 3.2 reworded to indicators, passes a pre-registered 6/6 |
| **4** | **fixed** | **fixed** | **rebuilt** | **pushed, verified** | **done** — 4.3 was confounded; a matched-pair cell demonstrates it 8/8, three runs |
| **5** | **fixed** | **fixed** | **rebuilt** | **pushed, verified** | **done** — the cap now fires at its real value of four, with the model taken out |
| 6 | not started | not started | — | — | verdict call has no email body |
| 7 | not started | not started | — | — | schema never validated |
| exam | not started | — | — | — | Q24 keys a payroll diversion "close it" |


---

## Week 4 — applied 2026-09-09

Objective **4.3, "Compare each email's verdict with tools against its verdict
without tools"**, is the at-risk one. 4.1 and 4.2 are safe and were never in
doubt: the student writes both functions, and cells 11 and 13 check them
against saved requests with no model involved.

Codex's wording for the defect is the one to keep:

> Week 4 operationalizes 4.3 with a five-confound comparison and then grades a
> causal explanation of it.

### The measurement

Eight probes, about 1,100 calls, all on the shipped stack. Full record in
`docs/week4-measurement/`, thresholds in `prereg-claude.md` written before each
result. Two pre-registered thresholds failed, and both failures changed the fix.

- **The comparison is confounded.** Cell 14 put `classify_grounded()` against
  `triage_with_tools()`; the arms differ in five ways besides the tool. With a
  control arm carrying a tool message that says "no record available", email
  003 still moves malicious to benign **8 of 8**. The tool's fact is not what
  moves it.
- **Three tools behave like one.** 59 of 69 calls asked for
  `check_sender_reputation`, `lookup_recipient` twice. The playbook is not the
  cause: a length-matched block of neutral filler concentrates the choice
  harder, 66 of 72. **Prompt length, not content**, so editing the playbook
  would have been the wrong fix.
- **No email met the pre-registered bar** for the tool being the active
  ingredient under free tool choice. 018's noise floor was 5 of 8.
- **Forcing the tool removes the wobble.** Every real-record arm is 8/8 and
  identical across two independent runs, all six rows. Every instability lives
  in the withheld arms. So a withheld arm must never be printed to a student as
  a baseline.
- **018 is the one confirmed matched pair**, twice over: same tool name, same
  arguments, withheld malicious 8/8, real `known_good` benign 8/8. A true fact
  about the sender walks a correct verdict backwards.
- **017 failed confirmation** and does not ship as a demonstration. Its three
  tool arms are stable; its baseline is a coin flip.
- **68 of 71 replies carrying a tool call also carried answer text**, read raw
  off the endpoint because `send_request()` overwrites empty content. The text
  names the tool actually called, **60 agree, 0 disagree**.

### What changed

| file | change |
|---|---|
| 14 notebooks (7 labs, 7 solutions) | `LAST_CALL["answer_was_empty"]`, set in `send_request()` before the notice is substituted. Additive; the chain still holds |
| `lab/notebooks/w4-lab.ipynb` + solution | **new cell 15**: email 018 judged four times, only the tool result changing. Four calls. Cells 8, 9 and 13 stop claiming a tool call carries no answer text and teach the sentence instead. Cell 14 passes `known_names=KNOWN_NAMES`. Cell 10 says four saved requests, not three |
| `content/pages/w4-content.md` | new section "One tool of three is half a read" with cell 15's table; a callout disclosing that 019 is wrong in every arm; the worked example stops naming a tool; call and token counts remeasured; the redundant sidebar section dropped to stay in budget |
| `content/assignments/w4-lab.md` | renumbered for the new cell; written answer no longer asks for a causal claim about an uncontrolled row |
| `content/rubrics/w4-lab.yaml` | criterion 3 grades reading cell 15 plus honest reporting of one cell 14 row |
| `content/quizzes/w4-self-check.yaml` | Q1's stem stops naming a tool cell 8 does not reliably return; Q3's "flips the verdict to malicious" corrected to holding it there, and the distractor feedback now points at cell 15 |
| `content/discussions/w4-discussion.md` | prediction moved from 018, which is now spoiled three ways, to **009**, with the body embedded; "read it on the lab page" removed |
| `content/pages/w4-wrap-up.md`, `w4-overview.md` | one new bullet; cell count 17 to 18 |
| `content/video/w4-overview.yaml` | the benign-to-malicious direction the lab never produces, replaced with the measured 018 contrast. Rebuilt |
| `content/video/w4-walkthrough.yaml` | one clause: its "no answer text, twenty of twenty" is true of its own run and yours may differ. Rebuilt |

### Verified, not assumed

- `check_chain.py`: the chain holds, 65 functions, 49 carried by more than one week.
- `readability`: all 74 enforced pages inside grade, length and warmth.
- `tools.video.check`: 14 videos, all checks pass, nothing stale.
- `run_notebook.py --student`: 18 cells, 2 TODO, runs clean with nothing written.
- `run_notebook.py --solution`: 18 cells, 0 TODO, artifact written, **25 calls,
  31,412 tokens**, and cell 15 reproduced the confirmed table a third time.
- Notebook server: all 15 notebooks live and md5-matched; solutions and both
  answer keys still 404.

### Not fixed, on purpose

Codex's "do not touch" list, kept: the playbook, `TOOL_TURN`,
`TOOL_INSTRUCTIONS`, `TOOL_SPECS`, `start_messages()`, `ask_with_tools()`,
`run_tool()`, `tool_result_message()` — byte-identical across weeks 4 to 7, and
week 5's measured loop behaviour rests on them. 017 is not promoted. 019's
accuracy is not chased, only disclosed. Natural tool-choice variation is left
alone. The lab's 165-minute estimate is left as it is.


---

## Week 5 — applied 2026-09-09

Objective **5.1, "Build a triage loop with a four-step cap and a stop
condition"**, is the at-risk one. The cap is half of it and it is the week's
headline control: one of the five stop reasons is entirely about it, the
reading gives it a section, the quiz asks about it, and the wrap-up says it
carries the week. 5.2 and 5.3 were checked rather than assumed and both hold.

### The measurement

`docs/week5-measurement/`, thresholds in `prereg-claude.md` written first.

**`step_cap` fired 0 of 48 runs, and the model never repeated a tool once.**
Every email landed on the stop reason the corpus designs for it, 8 of 8. The
loop is not broken; the cap is out of reach. With three usable tools under a
cap of four, `step_cap` needs four steps used **and** a tool untried, which
takes two wasted steps, against a `LOOP_INSTRUCTIONS` line telling the model
not to repeat. Not one of the six lab emails carries
`expected_loop.stop_reason: "step_cap"` — the corpus never planned for it.

**The cost model was estimated, never measured.**

| | the page said | measured |
|---|---|---|
| first request | about 1,500 tokens | **1,776** |
| each step adds | roughly another 100 | **71 to 164** |
| twenty-step run | its arithmetic implies 49,000 | **60,208** |
| capped run on 012 | not stated | **5,852** |

Objective 5.3 asks the student to compare those two totals. Until now no number
in the repository answered it. It is **10.3x**.

### The fix I proposed, and why it was thrown away

I proposed a cell running the student's own `run_loop()` at `max_steps=2` on
012. It passed every threshold I had pre-registered, including the control.
Codex rejected it on two grounds and both were right:

1. I called it deterministic by construction. It is not. `first_call()` passes
   the model's arguments through unvalidated and `run_tool()` honours them, so
   a model naming a different sender could end the run decisively. 8 of 8 is an
   empirical result and I was about to write a proof onto a page.
2. **5.1 says a four-step cap.** Demonstrating a cap at two shows the
   `step < max_steps` test works; it does not show the four-step cap ending a
   run. In codex's words it *"quietly substitutes a configurable two-step cap
   for a four-step cap"* — a redefinition of the objective, which is the exact
   failure this process exists to catch.

### What shipped

Codex's design. A pre-written cell stands in for `ask_with_tools()` with a
short script inside `try/finally`, drives the student's own `run_loop()` at its
real `MAX_STEPS = 4`, and restores the real function. Reproduced three times:

    012  steps: 4  stop: step_cap  tokens: 0
       tools still unused:  ['check_urls', 'lookup_recipient']
    005  steps: 1  stop: decisive_benign  tokens: 0

Deterministic, because model choice is removed rather than hoped about. Zero
model calls. The 005 control fires differently under the same script and the
same loop, so the cell demonstrates the cap and not the script.

| file | change |
|---|---|
| `lab/notebooks/w5-lab.ipynb` + solution | **new cell 15**, the scripted four-step cap with its control. Export cell rebuilds each step's full tool record into `result_full` |
| `content/pages/w5-content.md` | both false cap explanations corrected; cost figures replaced with measured ones; the uncapped run's seventeen repeats connected to the cap for the first time; two redundant sections merged to stay in budget |
| `content/pages/w5-wrap-up.md` | carried the same false arithmetic as the reading. Corrected, plus a line for the new cell |
| `content/quizzes/w5-self-check.yaml` | Q3's stem gave one repeat while its answer generalised to many. Stem now describes a run that repeats every step, and the feedback says one repeat would not do it |
| `content/assignments/w5-lab.md` | renumbered; the missing "read cell 9" step added |
| `content/pages/w5-overview.md` | eighteen cells to nineteen |
| `content/video/w5-overview.yaml`, `w5-walkthrough.yaml` | rebuilt for staleness. Neither repeated the false arithmetic, so no script changes |

### Verified, not assumed

Chain holds. All 74 pages inside grade, length and warmth. 14 videos, nothing
stale. Student run clean (19 cells, 1 TODO). Solution run clean (19 cells,
0 TODO). The export's `result_full` carries all 10 keys of a recipient record
as valid JSON, so the discussion's 4-point item is answerable.

### Not fixed, on purpose

`MAX_STEPS`, `TOOL_NAMES`, `usable_tools()`, `tools_left()`, `out_of_room()`,
`decisive_stop()`, `first_call()`, `append_turn()`, `one_line()` and
`run_loop()`'s signature are untouched. Weeks 6 and 7 inherit them and pass
their token guard through the same `step_guard`.

**Two things logged rather than fixed.** With three tools, a cap of four can
only bind after two wasted steps; a cap of three would bind after one. The
number is arguably mis-set for the tool count, but 5.1 names four and the value
is shared with two later weeks, so it is a course-level decision. And
`run_notebook.py --expect-artifact` passes when a cell merely *prints* the file
name — it never opens the file. The week 5 solution run reported the artifact
written with no such file on disk afterwards.

---

## Week 1 — done, 2026-09-08

### What changed

| file | change |
|---|---|
| `lab/notebooks/w1-lab.ipynb` | `MODEL` is now `granite-8b`; cell 11 rebuilt as a twelve-call word-plus-sentence probe at 0.2 and 1.0 with distinct-answer counts; cell 8 gained a request-shape check and a missing-`return` guard |
| `instructor/solutions/w1-lab-solution.ipynb` | same, kept in sync |
| `content/pages/w1-content.md` | teaches temperature for the first time; repetition cut to stay inside the 1,400-word budget |
| `content/pages/w1-overview.md` | objective 1.2 reworded — no direction promised |
| `content/pages/w1-wrap-up.md` | the "it makes them steadier" answer is now conditional |
| `content/assignments/w1-lab.md` | step and cell numbers, screenshot instruction, written questions |
| `content/rubrics/w1-lab.yaml` | "Variation reported" gives full credit for any honestly reported direction |
| `content/discussions/w1-discussion.md` | stale "six answers" references removed |
| `lab/notebooks/w1-sidebar.ipynb` | **new Part 1C** — a dictionary, a list inside it, and `.update()`, with the outer-versus-inner distinction made experiential |
| `content/pages/w1-overview.md` | parts 1A/1B → 1A/1B/1C; sidebar time 25 → 40 min; weekly total corrected 272 → 287, since the parts no longer summed |
| `content/video/w1-overview.yaml`, `w1-walkthrough.yaml` | scene lists rewritten |

**The sidebar gap is closed.** The beginner reviewer found that the only
*required* preparation for the first graded lab practised none of the structures
TODO 1 is built from: 516 characters of code, no dictionary literal, no
`.update()`, no list holding a dictionary. Part 1C now practises all three on the
stockroom example, and its "Try changing this" moves the merge onto the inner
dictionary so the student watches `delivery` land in the wrong place. Both
versions run clean and print happily, which the notes say out loud: *"Nothing
errors either way... when a value lands in the wrong dictionary, nothing tells
you."* That is the same failure TODO 1 invites, rehearsed once before it counts.

**Style checked, not assumed.** The new sidebar prose measures grade 1.89,
average sentence 7.1 words, longest 14 — against the surrounding sidebar's 2.34 /
7.3 / 30 and a course page mean of 3.74. It carries no contractions, which is
correct: warmth is a content convention and notebooks are not warmed. See Q6b.

Evidence: `docs/week1-measurement/`. The old demonstration landed in its claimed
direction **11% of the time**; the new one measures **98%**, with zero wrong
verdicts. First live run gave 2 distinct answers at 0.2 and 6 at 1.0.

### Still to do for week 1

**1. Re-render two videos. DONE, 2026-09-08.**

`w1-overview` (134.8s, 4.5 MB) and `w1-walkthrough` (131.6s, 4.5 MB) rebuilt.
`tools/video/check.py` now reports **14 videos, all checks pass**, including
`no video is stale against its page` and `captions cover the audio`. Library is
85 MB, 17% of the 500 MB Canvas quota.

**My earlier "the build environment is gone" was wrong.** The venv lives at
`tools/video/.venv`, and I had searched only the repository root. It was intact:
kokoro 0.9.4, soundfile, torch 2.13.0. The build must be run with that
interpreter, not the system one:

    ITSY_CONTENT=builder/content tools/video/.venv/bin/python -m tools.video.build --id w1-overview
    ITSY_CONTENT=builder/content tools/video/.venv/bin/python -m tools.video.build --id w1-walkthrough
    ITSY_CONTENT=builder/content tools/video/.venv/bin/python -m tools.video.check

Running `python3 -m tools.video.build` instead fails with `No module named
'soundfile'`, which reads like a missing dependency rather than the wrong
interpreter. Worth a line in the build's own help.

**2. Push to Canvas. DONE, 2026-09-08.** 154 objects, `--verify` reports 0
problems. The JupyterLite site was re-staged and rebuilt **first**, because
Canvas links out to it: `w1-lab.ipynb` and `w1-sidebar.ipynb` are live with
granite-8b and Sidebar 1C, and the instructor solutions and `corpus-spec.json`
still return 404.

Verified on the live course, not assumed: no duplicate pages, assignments,
quizzes, discussions or modules; exactly 42 video assets with no repeated names;
both week 1 videos embedded with poster, MP4 and a captions track, every media
URL returning 200; no `$IMS-CC-FILEBASE$` placeholders left; the lab assignment
at 100 points with its four-criterion rubric attached.

**3. Week 1's own verification depended on a workaround.** `run_notebook.py`
substitutes its own model for the notebook's, so the solution run had to be
forced with `ITSY1377_MODEL=granite-8b` on the command line. The run was real and
it passed — 15 cells, 0 TODO, 21.2s, artifact written, and cell 11 produced 2
distinct answers at 0.2 against 6 at 1.0 — but the gate would not have caught a
wrong model on its own. See **Q6**. Re-verify week 1 once Q6 is done.

**4. Cost note.** Week 1 now runs on granite-8b at $0.06/$0.25 per million
against granite-3b's $0.03/$0.12, and makes twelve calls where it made six. A
week 1 pass measured $0.0004 before; expect roughly three to four times that,
which is still hundredths of a cent against a $2 student budget.

### Closed, not deferred: the confidence-instability thread

A rejected number probe surfaced the idea that week 1 could be where a student
first watches the model's self-reported confidence move between identical runs,
foreshadowing week 2's `confidence` field, week 6's `CONFIDENCE_FLOOR = 0.7` and
week 7's note.

**Closed rather than carried, because the course already teaches the concept.**
`content/pages/w2-content.md` line 37:

> **Confidence** is a number saying how sure the model is. It runs from 0 to 1.
> Read it as the model's own report, not as a fact about the email. A high
> number on a wrong answer is still wrong.

and `content/pages/w6-content-2.md` line 76:

> `CONFIDENCE_FLOOR` at 0.7 says nothing about how good the model is. It's a
> line saying which cases a person owns.

The course never claims the number is calibrated; it says the opposite, twice,
at the two places it matters. Week 2's assignment already asks for "the lowest
confidence number you saw" across four emails, so students engage with its spread
in graded work.

**What is genuinely absent** is any week showing *the same email* produce a
different number on a repeated run. That is a narrower claim than "the number
varies between emails", which a student expects anyway. It belongs with the
control it would inform — see the carried note for week 6 below — and only if
week 6's rebuild leaves room for it.

**It does not answer the SOC finding.** The practitioner's objection is that the
control is built on the wrong signal, not that the course over-claims
calibration. That is week 6's to fix by changing the control.

**No assessment consequence.** Four exam items reference confidence, including
item 11 (the floor) and item 33 (a 0.62 answer). All four are answerable from
week 2 and week 6 as written.

Week 1 is complete. Objective 1.2 is demonstrated at 98%.

---

## Week 2 — applied 2026-09-08

Objective **2.3, "Retry a failed answer with the schema problems added to the
new prompt"**, is the at-risk one. Objectives 2.1 and 2.2 are sound: cell 7
already forces a malformed reply on purpose (`max_tokens=12`), and cell 11
ships four saved replies, three of them broken, one per failure shape. The week
forces malformed output twice before the student writes a line. What it never
does is let `classify_email()` take a **second attempt**.

### The measurement

Built from week 2's own pre-written cells (2, 3, 4, 5, 6, 9, 12) plus the
reference `extract_json` and `classify_email` out of
`instructor/solutions/w2-lab-solution.ipynb`. Ran on granite-3b against the
live proxy, 25 runs per email.

| email | first-try schema failures | tries used |
|---|---|---|
| 001 | 0 / 25 | 1 every run |
| 002 | 0 / 25 | 1 every run |
| 003 | 0 / 25 | 1 every run |
| 004 | 0 / 25 | 1 every run |

**0 of 100 in the first run.** A later 160-call pool found one malformed
answer, making the combined baseline 1 in 260. The practical conclusion did not
change: a four-email student run almost never exercised the retry before the
reporting rule was added. Note what this means: the model is behaving *well*.
The fix was never to degrade it.

### The four defects, ranked

**1. The discussion's reply task cannot be completed by anyone.**
`w2-discussion.md` hedges the post — "If every email passed on the first try,
say so" — and does not hedge the reply: *"Compare their failed try to your own.
Name one thing that was the same and one thing that was different."* Worth
**6 of the discussion's 20 points**, and the board adds "Same here, good post
isn't a reply and earns no points." With a 0% failure rate, no classmate has a
failed try to compare against. This is not a per-student risk; it is the whole
section, every term. The post half is safe, the reply half is not.

**2. Sidebar 2C teaches the loop shape that makes the retry impossible.**
Cell 9's loop is `while reading is None and attempts_made < 3:`, assigning
`reading = json.loads(gauge_line)` straight into its own test, and cell 10 says
in as many words: *"The loop stops the moment `reading` holds something.
Nothing has to break it."* TODO 2 must stop when the **check passes**, and an
answer that fails the check is not `None` — it is a good dictionary with wrong
contents. A student who carries 2C across writes the version whose retry can
never fire on a schema failure. That is 50 of the lab's 100 points.

This is the same defect as week 1's sidebar gap: the sidebar's *code shape*
contradicts the reading's *words*, and the sidebar is what sits open beside the
lab. The fix is the same shape too — a second gauge example where a line loads
cleanly and is still out of range (a temperature of 900), so the loop has to
keep going on a value it already holds.

**3. The stated success test accepted a broken answer.** The old cell 13 text
required a verdict, category, and positive try count but omitted `ok`. The old
results warning checked only a zero try count. The revised TODO requires
`ok=True`, and final cell 15 warns on either zero tries or a false `schema_ok`.
The assignment and screenshot rubric require all four live rows to show
`ok=True`.

**4. Load failures now carry a common recovery action.** `extract_json()` still
returns a dictionary or `None`. When it returns `None`, `schema_errors()`
reports: "The answer did not load as JSON. Return one complete JSON object with
no words before or after it." The attempt log keeps the raw text, so the prompt
gets one actionable instruction without changing the beginner-facing return
contract.

### What we measured next, and what it killed

About 750 more granite-3b calls. The whole record — six scripts, the 160-answer
pool, and what each experiment killed — is preserved in
`docs/week2-measurement/`, alongside week 1's.

**The baseline is 1 in 260, not 0.** A second pool of 160 calls turned up one
real failure on email 003 — a reply that stopped mid-string with a finish
reason of `stop`, not `length`. So the retry does fire, roughly once every 260
classifications. A student running four emails has about a 1.5% chance of ever
seeing it.

**Tightening the indicator count is dead, and not for the reason expected.**
The rate was never the problem; recoverability was. With the cap at 3 and
`schema_text()` fixed so the prompt and checker agree, **42% of runs ended with
no answer at all** — email 004 gave up 12 times out of 12. With the cap at 4,
every run that failed try 1 also failed tries 2 and 3; tries went 1 to 3 and
never 2. Across both caps, 28 runs retried and 23 returned `None`: an **82%
give-up rate**. granite-3b will not shorten a list when told to, however clearly
it is told. A rule can sit at a perfect failure rate and still be unusable.

**An under-specified prompt buys nothing over forced truncation.** It makes the
model write prose, so it fails at the load stage: `"the answer is not a JSON
object"`, 24 of 24, none loading as JSON. Identical to truncation.

**The feedback is the active ingredient — this was worth proving.** Every
recovery measured up to that point was confounded: try 2 is an ordinary full
call, which passes on its own anyway, so a successful retry proved nothing
about the problems being appended. An isolation probe settled it. Prompt left
asking 0.0 to 1.0, checker alone tightened to 0.9, then the same failure
followed by two independent second calls:

| second call | passes | confidence returned |
|---|---|---|
| with the problems appended | **24/24 = 100%** | 0.85, every time |
| bare re-ask, nothing added | **0/24 = 0%** | 0.95, every time |

Total separation. Objective 2.3 is not teaching a mechanism whose active
ingredient is unproven. It also explains the count result: the model is not
deaf to feedback, it specifically cannot shorten a list while it can move a
number instantly.

### Accepted design: a week 2 confidence reporting ceiling

`confidence <= 0.9` ships as a week-2-only reporting rule. It lives in
`OUTPUT_SCHEMA`, so `schema_text()` renders the same limit the checker
enforces. The fair loop was run twice, at 12 and 20 classifications per email:

| email | measured tries | gave up |
|---|---|---|
| 001 | 1 in all 32 measured runs | 0 |
| 002 | 2 in all 32 measured runs | 0 |
| 003 | 2 in all 32 measured runs | 0 |
| 004 | 1 in all 32 measured runs | 0 |

Across 128 classifications, 64 retried, all 64 recovered, and none returned no
answer. The split is stable evidence, not a promise about named emails in
future runs, and no student-facing sentence names which email retries.

The content states the limit honestly:

> `0.9` is a reporting limit in this lab. It does not make the model less sure
> or more accurate. When `0.95` is rejected and `0.85` comes back, the model
> corrected its report to fit the contract. It did not prove that its judgment
> changed.

A short `LOADS_BUT_WRONG` contract test remains as deterministic assessment
support. Both of its answers are saved inputs, not model output. The live
four-email run is the teaching event.

**Scope note, and a deviation from the plan.** D4 changes the body of
`schema_errors()`, which weeks 3 to 7 carry verbatim. The plan expected to
leave `check_chain.py` reporting five known mismatches. That would have shipped
the course in a state its own gate calls broken, so the one changed string was
propagated to the five later labs and their five solutions instead. Nothing
else in those files was touched, the message is identical in all six weeks, and
no behaviour changes anywhere: the string is only what a load failure reports.
`check_chain.py` holds.

### Assessment consequence

Rubric criterion 2 is 50 points and the primary CLO2 evidence. Its *Exceeds*
level is distinguished from *Meets* by "Every failed try is recorded with the
problems that caused it." With no failed tries, that clause is unverifiable and
the two levels collapse into one. Every student lands on Exceeds by default,
and the criterion measures submission completeness rather than output
validation.

### Found after shipping: the contract test could be bypassed silently

Asked whether week 2 was good to go, the honest answer was no, and the defect
was one I had introduced the day before.

`classify_email()` has to fetch its reply through `answer_source()` for the
saved contract test to work. A student who writes `ask_model()` instead --
which week 1 taught, and which the previous version of this TODO named -- gets
a function that is correct in every way the objective cares about. Their four
live rows pass. But the contract test then talked to the live model while
printing **"Saved input, not model output."**, reported `problems_copied:
False`, and exported `source: "two saved test answers, not model output"` as
the provenance of an attempt that came from the model.

The rubric's Exceeds level requires `problems_copied`, so that student lost the
top level of the 50-point criterion with nothing anywhere naming the line to
change. A check that reports confidently while examining the wrong thing, which
is the defect class this whole review has been cataloguing.

`answer_source()` is the only thing that moves `TEST_ANSWER_INDEX`, so the cell
now reads it before resetting and says exactly what to do:

    This test did not run. Your classify_email() never called
    answer_source(), so the saved answers were never used and this
    cell talked to the live model instead.

    In TODO 2, step 3, change the line that gets the reply to:
        raw_text = answer_source(prompt)

`retry_demo` carries `used_saved_answers`, and its `source` label now tells the
truth in both cases. A run that used the fixture but failed to copy every
problem gets its own line rather than a bare `False`.

A second, smaller one from the same test: a notebook with the TODOs unwritten
reported `problems: ['The answer did not load as JSON...']` on all four rows,
which sends a student to fix JSON they have not written. A row with no tries now
says so instead.

Three paths were run against the live model afterwards: the correct solution
(4 problems, attempt 2, every problem copied, all four rows `ok=True`), the
`ask_model` mistake (clear diagnostic, honest export label), and the shipped
notebook with both TODOs empty (no crash, accurate message).

### Codex's adversarial review, and the alignment it restored

Asked whether week 2 was done, codex said **not done**, kept every instructional
decision, and found two blocking defects plus a construct-validity problem I had
argued myself into.

**The alignment problem.** Every cell in the lab maps to an objective except the
saved contract test, and that cell had pulled five names into the notebook that
teach nothing: `answer_source`, `TEST_ANSWER_MODE`, `TEST_ANSWERS`,
`TEST_ANSWER_INDEX`, `PROMPT_LOG`. Worse, the rubric gated **both** top levels of
the 50-point CLO2 criterion on the fixture, so a student whose live run
demonstrated 2.1, 2.2 and 2.3 on real model output could still be denied Exceeds
for not using the seam. Codex put it exactly: *"the deterministic fixture earns
its place; requiring one particular provider function to reach it does not."*

My own answer had been to delete the fixture. Codex's is better: keep it and move
the substitution **below** `ask_model`, the name week 1 taught. The contract cell
now swaps the global `ask_model` for one run inside `try/finally`. The student's
loop calls `ask_model(prompt)` and needs no special code, the fixture still
supplies the only record of prompt 2 that the file carries, and the
construct-irrelevant gate is gone rather than diagnosed.

**Blocking 1: the fixture could leak into the live run.** The old cell set test
mode and reset it at the bottom with no `try/finally`. A normal beginner error --
`parsed["id"]` for `parsed["email_id"]` -- raises before the reset, and the
provider clamps an exhausted index to the last saved answer. The next cell,
labelled the live run, would then return `GOOD` for all four emails with **no
model call**: benign, legit_internal, 0.9, one try, `ok=True`. A fabricated pass.
Now restored in `finally`, and the live cell puts the real `ask_model` back
defensively before it runs. Verified: after a deliberate `KeyError` inside the
student's function, `ask_model` is the real one again.

**Blocking 2: reruns mixed old attempts into the export.** `ATTEMPT_LOG` was only
initialised when cell 12 ran, while the displayed `tries` was a per-call delta.
The ordinary repair workflow -- run a broken TODO, read the warning, fix it,
rerun -- exported both runs, with try numbers restarting at 1 twice. The live
cell now drops its own four emails from the log before it starts and keeps the
contract test's entries.

**Two silent false passes, now caught.** A `for` loop with no `break` kept asking
after an answer was accepted, three calls per email, and every check went green.
Try numbers counted from zero printed "Attempt 2 recorded: True" because the
check tested list length. The contract test now records `try_numbers` and
`calls` and requires exactly `[1, 2]` and 2, with a message naming which mistake
it saw.

Nine plausible implementations were run against the live model afterwards. The
reference, an early-`return` `for` loop, and a pasted week 1 `ask_model` all
pass. The 2C loop shape, a summarised retry, a missing `log_attempt`, the
no-`break` loop and zero-based counting are each caught, and each is told
something different.

**Surfaces.** Eight instructor references still pointed at the old cell numbers,
and `grading-notes.md` described the pre-redesign criterion, including that four
`answer: null` records could take full credit. Repaired, along with the six-call
claim (now eight) and the quiz's stale section label.

Codex's remaining items are course-level, not week 2: screenshot mechanics before
week 1, and category boundaries before week 7 scores against `enums.json`.

### The seven categories: they were never missing, only unreachable

The blind run logged "what separates the seven categories" as taught nowhere,
and said the glossary had no entry for `bec` or `vendor_fraud`. Both halves
needed checking and one of them was wrong.

**The definitions already existed, and already shipped.**
`corpus/spec/categories.json` carries a one-line definition for each of the
seven, each mapped to its verdict, plus a `spam_rule` explaining why spam is
benign. It is listed in `student_files`, it is on the notebook server, and it
returns HTTP 200. **Not one student-facing page, notebook or video has ever
named it.** `course.yaml` is the only file in the course that mentions it.

**The glossary did define them**, on one row under Category, run together in a
single sentence. So the finding as written was wrong: they were defined. But a
student who has just been handed `bec` by their own agent searches the glossary
for `bec`, and that search fails. Defined and unfindable is close enough to
undefined that the student's conclusion was right even though the premise was
not.

Fixed in three places:

- Week 2 reading part 1 gains **The seven categories**, its own section: all
  seven with their verdicts and what each means, sourced from
  `categories.json` and naming that file so a student can go read it. Plus the
  two boundaries that actually catch people. Spam is benign because it asks for
  nothing but a click, and a bulk message that asks for a password or a payment
  change is not spam but whichever malicious category the ask implies. And
  `bec` and `vendor_fraud` both chase money, so the difference is who is
  imitated: a person you work with, or a supplier's invoice.
- The glossary gains **seven findable rows**, each keyed on the enum spelling a
  student would search, in A-to-Z order. The Category row now points at them
  instead of running them together.
- The blind student's own hard case is now answerable: an executive-impersonation
  payment request is `bec`; the same money chased through a supplier's invoice
  is `vendor_fraud`.

**The prompt was deliberately left alone.** Adding definitions to
`CLASSIFY_INSTRUCTIONS` would probably improve the model's category accuracy,
which would move the measured retry split and undercut the walkthrough's best
moment, where an allowed category is wrong and the schema passes it anyway. The
gap was the student not knowing, not the model.

The builder caught a real structural error on the way: the new table sat in the
same `:::` block as the four-field table, and two tables in one block would
share a caption. That is the same defect class as the duplicated headings the
blind run found, and this time the gate refused the push.

### The screenshot gap: 242 points on a skill the course never taught

The blind run raised this five times, once per week it reached, and it was the
one finding I kept deferring as "not week-specific". It is worth more than
anything else in the queue.

**Ten rubric criteria across the seven labs depend on a screenshot: 242
points.** Not the 15 I had been quoting, which was only week 2's named
criterion. Every week's Submission completeness criterion requires one too, and
week 7's 56-point accuracy criterion reads one.

What the course said about taking one, in full, before today:

- `using-the-notebook-server.md`: never put your key in one.
- `canvas-and-tech-support.md`: you need a real computer, because you save one.

That is the whole of it. Two warnings about screenshots and no instruction for
taking one, against 242 points.

**Fixed on `using-the-notebook-server.md`**, which is where the rest of the
environment is explained and which sits in the Orientation Module ahead of week
1. It gains a keystroke table for Windows, Mac, Chromebook and Linux, a browser
print-to-PDF fallback for anyone whose keys do not work, the four ways a
screenshot loses points (a cut-off row, text too small to read, the wrong cell,
and the configuration cell with the key in it), and the steps to attach it in
Canvas.

All seven lab assignments now point at it from the end of their submit block.
That matters more than the page: a student in week 5 is not going to reopen
orientation on their own.

Two placement lessons on the way. The pointer first went in directly after the
screenshot item in each numbered list, which split the list and merged with the
items below it into an 87-word paragraph; the readability gate caught all five
failures. And changing all seven assignments made all seven walkthrough videos
stale, because each one fingerprints its own week's assignment page. Both
rebuilt and green.

### Struck: a fifth false finding from my own harness

The blind run reported that both week 2 assigned sources appear as bare domains
with no link, "third week running". **That is my dumper, not the course.**
`w2-content.md:121` and `w2-content-2.md:120` both carry full markdown links,
and the corrected dump renders them as
`rfc-editor.org [https://www.rfc-editor.org/rfc/rfc8259]`. This is the same
href-stripping bug already struck four times; the student's grep ran against a
pre-fix dump. Nothing to fix in week 2. The finding is withdrawn.

### Minor, confirmed

- **Cell 4 ends with a bare `budget_left()`**, so Jupyter echoes `1.9995875`
  under the labelled output with no explanation. `budget_left(quiet=True)` or
  `_ = budget_left()` fixes it. Same shape as week 0 cell 82's `5 None`.
- **Three items taught nowhere**, all three needed by TODO 2: that an empty
  list is false (`if not problems:` — the idiom the course's own pre-written
  cells use, in cells 12 and 14), returning early out of a loop, and what
  `isinstance()` does. Candidate home for the first two: a fourth sidebar part,
  which is also where defect 2's fix goes.
- **Reading part 2's third broken shape did not reproduce** — cell 7 returned a
  truncated answer, not an empty one. Recorded as a hedge that worked: the page
  says in advance that it may not reproduce, and why. No fix needed.

### What shipped

Week 0 cells 91 to 93 and 96, sidebar 2C, a new sidebar 2D, the week 2 lab and
its solution, all four content pages, the assignment, discussion, rubric,
self-check and both videos. The overview time table went from 310 to 325
minutes, and it adds up.

Gates: `check_chain.py` holds, `verify_content.py` reports the content and the
code agree, readability passes with every week 2 page inside its budget, and
all 14 videos pass. A live run of the solution against granite-3b produced 001
and 004 accepted on try 1, 002 and 003 retried and recovered, every row
`ok=True`, and the contract test green.

**Shipped 2026-09-08.** Notebook site staged at 73 files and deployed; a
file-by-file diff against the staged tree showed only the eight notebooks that
changed, and AppleDouble files that BSD tar leaked onto the public site were
removed, after which the served tree matched exactly. Canvas: 154 objects, 0
skipped, `--verify` 0 problems. All four week 2 pages carry no
`$IMS-CC-FILEBASE$` placeholder, their six media references all return 200, and
all 14 course videos are present with no duplicate filenames.

**A tool bug found on the way out.** `tools/warm_pass.py` contracts `is` onto
whatever precedes it, including phrase subjects. It had already shipped eight
broken sentences: "Handling it's the work", "What to take from it's the shape",
and six of "Nothing here's graded". All eight fixed; six videos went stale and
were rebuilt. **The tool is still wrong and will reintroduce them.** See Q11.

## Week 3 — diagnosed, not yet fixed

Objective **3.2, "Report which verdicts changed after you added the facts
block"**, is the at-risk one, and it fails in a worse way than week 1's
temperature or week 2's retry. 3.1 and 3.3 are sound: the student writes
`build_facts()` and `format_facts()`, and the rubric grades their choices
rather than the model's answers, which is exactly what week 1 lacked.

Full numbers and the harness are in `docs/week3-measurement/`.

### The lab runs other weeks' emails

`corpus/ground_truth.json` tags every teaching email with the weeks it belongs
to. Week 3's designed set is **001, 004, 005, 006, 017, 025**. Cell 14 runs
**001, 004, 005, 016, 017, 019**, where 016 is tagged week 6 and 019 week 4,
and 006 and 025 are never run.

The blind run read this as the prose failing to follow a moved email set. It is
the other way round: the wrap-up, the overview video, self-check Q3 and the
notebook's own TODO cells all name 005 and 025, which is the corpus design.
The assignment page, the reading and cells 7, 10, 12 and 14 drifted. Cell 10
prints the header `email 025` over 016's values; cell 12 assigns
`parsed_025 = load_email("016", ...)`. **The prose is right and the code is
wrong**, which reverses the fix.

### Correcting the set would not have fixed the objective

128 live classifications, 8 per email per condition. **Every email designed to
move stays put, 0 of 8, including both halves of the intended demonstration
pair.** The only movement anywhere is email 017 flipping benign to malicious
**8 times out of 8**, when the truth is benign and the design was uncertain to
benign. Zero movements toward truth.

So 3.2 is demonstrated only by a deterministic false positive.

### Two things underneath it

granite-3b reads malicious from the body alone on 7 of the 8 emails, including
005 and 019, which are benign. It will not be talked out of malicious, so
"facts exonerate a benign email" cannot demonstrate itself on this model and
this corpus.

And the facts block makes 017 worse, on an email whose every fact is clean.
`format_facts()` renders values with `str()`, so booleans arrive as `False` and
empty lists as `[]`. The blind run reported the model citing "Display name
mismatch: False" among its reasons for calling it malicious. The untested
hypothesis is that a small model reads the salient phrase and drops the
negation, so clean facts read as concerns.

### Also confirmed, both small

- The discussion is worth 20 points and item 3 asks what the model listed as its
  indicators, but `compare_runs()` drops `indicators` when it builds its rows,
  so no artifact carries the value the page tells the student to paste. One key
  in one dictionary in cell 13.
- Cell 7 prints "every key the parser returns" as the menu the student picks
  from, and carriage returns inside `body_text` and `body_html` overwrite their
  own key names, so two of twenty-six keys have no label. Cell 8 then discusses
  one of them by name. A `.replace("\r", " ")` beside the existing newline one.

### Applied 2026-09-09

**Option B was disproven before it shipped and objective 3.2 was reworded.**
The full measurement record is in `docs/week3-measurement/`, nine sections and
about 700 calls.

Option B would have added email 008 as the demonstration: genuinely malicious,
benign 6/6 from the body, malicious 6/6 with facts. Its facts turned out to be
nearly identical to 017's, whose truth is the opposite. The control settled it:
**a facts block with every value replaced by "(withheld)" flips both emails to
malicious, 6 times out of 6.** The content does nothing. 008's "correct" flip
is the same artifact as 017's wrong one, landing on the right answer by luck.
That is the week 1 number-probe failure again, and it was one commit from
shipping as the week's demonstration.

Section isolation found no single culprit: on 017 the facts block alone causes
the wrong flip, on 008 the playbook alone and the known-good list alone each do.
The shipped grounded prompt pushes granite-3b toward malicious more or less
regardless of the email.

**Five models were tested and none rescues verdict-based 3.2.** granite-3b
flips both regardless of content; granite-8b never moves and misses the phish;
gemma3-12b reads the facts and reaches the wrong answer; llama31-8b mostly
ignores them; qwen3-14b cannot return schema-valid JSON on a grounded prompt,
which would break week 2's contract too. Changing the model was rejected on
measurement, not taste.

**What shipped instead.** Objective 3.2 now reads:

> **3.2** Compare the model's stated indicators before and after you add the
> facts block, and report what changed.

Codex fixed the acceptance threshold **before** seeing any indicator numbers:
map each indicator to one of thirteen canonical fact concepts, keep concepts
stable across 75% of replies, and qualify a row only when the grounded set adds
a fact concept and the symmetric difference over the union is at least 0.50.
Pass on 4 of 6. **Result: 6 of 6, D = 1.00 on every row.** On five of six
emails the ungrounded run names no fact concept at all, because it has none to
name; the grounded run names SPF, DMARC, the link host, the sender domain and
the display-name check. A separate control showed two ungrounded runs are
byte-identical, so the turnover cannot be sampling.

The email set is the corpus's own 001, 004, 005, 006, 017, 025. Nothing from
weeks 4 or 6 is loaded any more, including the attachment example, which is now
a labelled fixture dropped into a copy of 005. `indicators` flow through
`compare_runs` into the export, so the discussion's 5 points are earnable;
that change is additive and was propagated to weeks 4 to 7 to keep the chain.
Carriage returns no longer eat two key names.

Every surface that promised a verdict change was rewritten: the reading, the
assignment, the discussion, the wrap-up, the rubric's two affected criteria,
the notebook submission cell, the self-check's framing, and both videos. The
walkthrough keeps its best moment, the model quoting the facts block back, and
no longer promises a student the same flip. `content/video/runs/w3.json` now
records that email 009 does not reproduce its 2026-09-05 result.

A wrap-up question was added for the one row that does move: a verdict that
moved is not a verdict that improved, and week 7 is where accuracy is measured.

**A pre-existing defect found on the way:** `w3-content.md` had an unclosed
`::: section` block, so two sections rendered merged. Every other page in the
course balances; this was the only one.

**Not done, deliberately.** Semantic rendering in `format_facts()` and the
shape of `build_grounded_prompt()` are both carried by weeks 4 to 7, so
changing either changes their prompts and their measured behaviour. Both are
logged as cross-week items.

### Superseded: option B as planned

**Reword 3.2 to indicators, and put email 008 into the set.** Either alone
leaves a gap.

> **3.2** Compare the model's stated indicators before and after you add the
> facts block, and report what changed.

Observable even when the answer is "nothing changed", still CLO1 (which facts
entered the judgment), and it stops the course promising an effect the model
does not produce. Rubric criterion 2 and its CLO1 link do not move.

The set becomes **001, 004, 005, 008, 017, 025**, 008 replacing 006. Measured:

| id | truth | body alone | with facts | what it shows |
|---|---|---|---|---|
| 001 | malicious | malicious | malicious | a control, no movement |
| 004 | malicious | malicious | malicious | a control, no movement |
| 005 | benign | malicious | malicious | facts did not rescue a benign email |
| **008** | malicious | **benign 6/6** | **malicious 6/6** | **the demonstration, correct** |
| 017 | benign | benign 8/8 | **malicious 8/8** | facts pushed it the wrong way |
| 025 | malicious | malicious | malicious | no movement |

008 is tagged week 4. Overriding that is deliberate: the tags encode design
intent, were never validated against the shipped model, and measurement wins
where they disagree. Week 4 uses 008 for tools rather than grounding, and the
corpus already shares 017 across weeks 3 and 4 and 005 across 3 and 5.

**017 stays in and its wrong-way flip is taught, not hidden.** Dropping it
would be selecting the set to flatter the lesson, which is the failure this
review keeps finding. Under the reworded objective the student compares
indicators and reports that the facts entered the reasoning and pushed the
wrong way, which is a real CLO1 observation.

Not done, deliberately: semantic rendering in `format_facts()`. Carried by
weeks 4 to 7, so changing it changes their grounded prompts and measured
behaviour. Diagnosis only, logged as a cross-week item.

### Superseded question

Whether 3.2 should be rescued or reworded. A facts block that cannot move this
model's verdict may mean the objective should measure what the facts changed
about the model's stated indicators or reasoning, which is still CLO1, rather
than about its verdict. Codex is reviewing that against the alternatives before
any more calls are spent.

Nothing in week 3 has been changed.

## Carried notes for weeks not yet started

Things learned while fixing an earlier week that the later week should know
before it starts. Not defects in themselves.

### Week 6

- **Consider, only if the rebuild leaves room:** a demonstration that the same
  email returns a different confidence number on a repeated run. The concept is
  already taught (see week 1's closed thread above); what is missing is the
  observation. It would sit naturally beside `CONFIDENCE_FLOOR`, which is the
  control it informs.
- **The SOC review says two of the four taught controls measure the wrong
  thing.** `over_token_cap()` reads `RUN_USAGE["answer"]`, but completion tokens
  do not grow across a loop — prompt history does, which week 5 teaches
  correctly. And the confidence floor routes on an uncalibrated self-report.
  Forcing either to fire would hide the defect rather than fix it.
- **Four documents state that emails 009 and 012 sit under the 0.7 floor**
  (`w6-content.md:73`, `w6-content-2.md:78`, `w6-wrap-up.md:50`,
  `w6-self-check.yaml:246`). The blind run had **0 of 11** rows under it. Fix the
  claim or the corpus, not both.

## Not week-specific — the queue

These affect every week and are cheaper to do once. Ordered by value.

### Q1. Re-key final exam question 24, and derive escalation

**Verified.** Email 050 is *"Your direct deposit account was changed"* from the
real payroll vendor, reported by the employee. The keyed answer is "Benign. Close
it and reply to the reporter"; the distractor marked wrong is "Benign, but
escalate". `corpus/data/playbook.md` rule 5 says *"Escalate it whatever the
verdict."* The employee reporting it **is** the "if you did not, contact payroll
immediately" branch firing.

*How:* change the key in `content/quizzes/final-exam.yaml` (and the matching
`exam-parts/` file). Then make the rule derivable rather than self-reported —
`escalate == recommended_action in {escalate_incident,
verify_out_of_band_then_close}` holds 20 of 20 in the batch key. Rename week 6's
model-set flag to `control_flag` so a control the model can change is not called
a control. **Done when** the exam key and `playbook.md` cannot disagree.

### Q2. Add the missing fields to the export cells

**Three rubric criteria and three discussion items are graded on values the
export files do not contain.** One line each, in the cell that builds the row.

| week | add | to |
|---|---|---|
| 3 | `indicators` | `compare_runs()` |
| 5 | the untruncated tool result | `one_line()` is `json.dumps(result)[:80]` |
| 6 | confidence, and the undefended token count | `compare_guarded()` |
| 7 | validate the three note fields | see Q3 |

**Done when** every value named in a rubric or discussion prompt can be found in
the file the student attaches.

### Q3. Give `schema_errors()` a `sentences` branch, and call it

`OUTPUT_SCHEMA_V2` declares `summary` as `{"type": "sentences", "how_many":
"two"}`. `schema_errors()` branches on `allowed`, then `number`, then falls
through to an `else` that requires a list — so it would reject a *correct* week 7
answer, and it is never called with V2 anywhere. **Done when** the 36-point note
criterion has code behind it.

### Q4. Move the self-check keys off position 1

All 43 scored questions in weeks 1–7 have the correct answer first, and
`shuffle_answers` is `false` on all seven quizzes in Canvas. **Do not fix this
with shuffling** — the instructional designer says shuffling is off deliberately
and documented, so students can compare a second attempt to their first. Move the
keys instead. The assessment reviewer found a second cue: the key is also the
**longest option in 27 of 43**, which shuffling would not have fixed either.

### Q5. Give the discussions a Canvas rubric

12% of the grade. `make_discussion()` in `build_course.py` attaches none; scoring
lives in a prose table with no levels and no partial credit.

### Q6. `run_notebook.py` cannot prove a notebook works as shipped

**Verified while fixing week 1, and it affects every week's verification.**
`lab/tools/run_notebook.py` lines 214-217:

    os.environ.setdefault("ITSY1377_BASE_URL", "http://localhost:11434/v1")
    os.environ.setdefault("ITSY1377_MODEL", "granite4.2:3b")
    if not os.environ.get("ITSY1377_API_KEY"):
        os.environ["ITSY1377_API_KEY"] = "local-run"

**The defaults are deliberate and the reason is good.** The comment above them
records it: *"one run put 201 failed calls into the proxy's log before this was
noticed."* A gate must not fire real requests at the students' endpoint. Keep
that property. The problem is what the defaults cost.

**Three consequences, in order of severity.**

1. **The gate cannot test the model a notebook ships with.** A notebook's
   configuration cell reads `os.environ.get("ITSY1377_MODEL", "granite-8b")`.
   `setdefault` fills that variable in before the notebook runs, so the
   notebook's own default is unreachable from the gate. Whatever a lab declares,
   the gate tests something else. Week 1's verification had to be forced to
   granite-8b by hand on the command line; had I not, it would have "passed"
   against a model the notebook does not use.

2. **The default endpoint is dead.** `localhost:11434` is ollama, and this course
   moved off ollama — `STATE.md` records that both eval scripts pointed at "an
   ollama that no longer exists". So the default configuration cannot complete
   any notebook that makes a call. It only appears to work in `--student` mode,
   where the TODO cells are unwritten and no call is made. That run passes in
   under a second having proved nothing about the model path.

3. **The banner reads as if it were the notebook's setting.** It prints
   `model:     granite4.2:3b` with no indication that this is the harness's
   substitution rather than the notebook's declaration. That line is what nearly
   let a wrong verification through on week 1.

This is the same shape as the two `verify_content.py` checks in Q7: a gate that
passes loudly while examining the wrong thing.

**How to fix it, keeping the safety property.**

- Parse the notebook's configuration cell for its declared `ITSY1377_MODEL`
  default and print both lines: `notebook declares: granite-8b` and
  `this run uses: <x>`.
- **Fail** when they differ, unless the operator passes an explicit
  `--allow-model-substitution`. A gate may substitute; it may not do so silently.
- Replace the dead ollama default with a hard error when no endpoint is
  configured, and add an explicit `--live` flag that opts into the real proxy so
  that reaching production is always a typed decision.
- In `--student` mode, say plainly that no model call was made, so a
  sub-second pass cannot be mistaken for evidence about the model path.

**Done when** running the gate with no environment set on a notebook that
declares `granite-8b` either tests granite-8b or refuses to run — and never
prints a model the notebook did not choose.

### Q6b. Measure notebook markdown for reading level, and only for that

**Done, 2026-09-08.** `tools/readability.py` now measures every markdown cell under
`lab/notebooks/` beside every content page, in one table. Notebooks are held to
the same reading grade and carry no length budget, because a notebook is worked
through rather than read straight down. 74 pages enforced, up from 59.

### Q6c. `build_course.py` has no per-week scope, and its dry run is not dry

**Done, 2026-09-08.** `build_course.py --week N` builds one module. It takes a number,
a comma list, `start` for orientation, and is repeatable; `--list-weeks` prints
the mapping. Three things narrow together: modules written, video assets
uploaded, student lab files. A scoped run still walks the whole spine so each
module keeps its position. Measured: week 2 alone is 39 objects and 6 video
assets in 228s, against 154 objects and 42 assets for the full course.

The dry run was also not dry: `--check` uploaded all 42 video assets for real
while printing `[dry]` for everything else. It now maps each placeholder to a
`[dry-run: ...]` label and touches nothing.

### Q7. Make every check report how many items it examined

`check_points()` and `check_quiz_points()` in `tools/verify_content.py` iterate
`course["assignments"]` and `course["quizzes"]`, but this course keeps everything
under `modules[].items`. **Neither loop body has ever executed**, and both print
`ok`. Twenty lines — every check returns a count and the run fails on zero unless
inapplicability is declared. Turns two green gates red today, and every future
check inherits it.

### Q8. Say which interpreter the video build needs

**Not a missing environment — a misleading error.** The venv is at
`tools/video/.venv` (kokoro 0.9.4, soundfile, torch 2.13.0) and it is intact. Run
with the system python and the build dies on `No module named 'soundfile'`, which
reads like an uninstalled dependency. It cost this session a wrong "the build
environment is gone" report and a deferred week 1 video render.

*How:* have `tools/video/build.py` check on startup that it is running under
`tools/video/.venv` and, if not, say so by name instead of letting an import
fail. One line in the module docstring too, since that is where a reader looks
first. **Done when** the wrong interpreter produces "run this with
tools/video/.venv/bin/python" rather than an ImportError.

### Q9. Gate the served notebook site against the repository

When this round started, `w7-lab.ipynb` on notebook.bashtion.dev was one revision
behind the repo. Fourteen of fifteen notebooks matched by hash, one did not, and
nothing reported it. Add a check comparing the staged tree to the live site.

### Q10. Two Level A accessibility failures

The fourteen shipped transcripts lost their `lang` attribute and their titles at
the final build step — three lines to fix. There is no accommodations statement
in the syllabus. Also: `docs/course-review-2026-09-07.md` line 19 cites a
6,600-word accessibility review that is no longer on disk; recover it before
commissioning remediation.

---

### Q11. `warm_pass.py` produces ungrammatical contractions

**Done, 2026-09-08.** `tools/warm_pass.py` now refuses to contract when a preposition,
a gerund or a quantifier sits in front of the pronoun, so the pronoun is part of
a longer phrase rather than the subject. `tools/readability.py` enforces the
same rule on the output, everywhere, including staff documents. The gate found
four more instances the original grep had missed, in `w3-lab.md`,
`w3-overview.md`, `w5-discussion.md` and `w6-discussion.md`; all four are
fixed.
