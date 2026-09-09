# A blind student ran the whole course. What it found.

**Run:** 2026-09-07 to 2026-09-08
**Subject:** ITSY-1377-000 as published to Canvas course 6, notebooks as served
by notebook.bashtion.dev
**Status:** findings and a ranked worklist. **No course file has been changed
because of this run.**

A simulated student took the course end to end as a novice would: the Canvas
pages, the fourteen video transcripts, and notebook.bashtion.dev. No repository
access, no solutions, no answer keys, no looking ahead. It worked one module per
sitting, in order, and wrote its notes as it went rather than at the end.

It finished everything: orientation, student resources, Module 0, all seven
labs, all seven sidebars, all seven discussions, all nine quizzes and the final
exam. It scored **39 of 40 on the exam**, spent **$0.0106 of a $2.00 budget**,
and took **about 31 hours** against the course's own estimate of 42.

Its notes are 7,008 lines (`FINDINGS.md`) and its own report is 976
(`REPORT.md`), both under `scratchpad/student2/`. Everything below marked
**verified** was checked against the source or the live site while writing this
page.

---

## 0. Read this part first: four of its complaints were my fault

The student reported thirty-odd problems. **Four came from the harness that fed
it the course, not from the course.** All four had the same shape: my export
lost something, and the student -- correctly refusing to assume -- reported what
it could actually see.

| what it reported | what was true |
|---|---|
| "The self-check never names the section to reread" | Canvas carries per-answer feedback naming Section 1..10. My exporter dropped the `comments` field. |
| "Every cell number on the week 1 page is off by one" | The page counts from 1, as a person counts down the page. My `nb out` numbered from 0. |
| "Zero `http` on any page, five weeks running; the assigned sources are unreachable" | Eighteen pages carry links. My exporter wrote `text <url>` and then stripped anything in angle brackets as markup. |
| "Duplicated headings above tables in weeks 2 and 3" | The exporter repeating a heading, misfiring where a `::: section` marker intervened. The student found this one itself. |

Each was corrected mid-run and the student was told to strike the finding. This
matters for two reasons. It is the honest calibration on the rest of the list.
And it is a warning about the method: **a blind reviewer can only report what
the pipeline hands it**, so the pipeline has to be checked before its findings
are.

---

## 0.5 The panel's verdict, and what it changed

Five reviewers read this run against the source on 2026-09-08: instructional
design, a SOC practitioner, test strategy, beginner experience, and assessment
and measurement. Their reports are in `docs/panel-2026-09-08/`. They corrected
me three times and moved the top of the list.

**The new number one, and it was not on my list.** The SOC practitioner found
that **exam question 24 keys a payroll diversion as "close it"**. Email 050 is
"Your direct deposit account was changed" from the real payroll vendor: SPF,
DKIM and DMARC all pass with `policy.dmarc=reject`, sender trusted with 212
messages in 90 days, link host allowlisted. Body: *"If you made this change, no
action is needed. If you did not, contact your payroll administrator
immediately."* The keyed answer is **"Benign. Close it and reply to the
reporter."** The distractor marked wrong is *"Benign, but escalate, because the
message is about a bank account."*

The course's own shipped playbook, which the agent is given as grounding, says:

> **4.** Direct deposit changes happen only in the payroll portal. Never by email.
> **5.** Any change to a vendor's bank details, or to when a payment goes out,
> gets a phone call to the number on file first. **Escalate it whatever the
> verdict.**

And Casimir Hallowden **reported it**. Reporting the notice to the phishing
mailbox is the "if you did not, contact payroll immediately" branch firing. The
message is not a phish; it is the receipt for a diversion that already
succeeded. Verified against `playbook.md` and `final-exam.yaml`.

This outranks everything below it. A broken demonstration is a course that fails
to teach something. A wrong exam key is a course that teaches a wrong reflex, on
the graded instrument, about money moving. The practitioner's ruling: **the
answer key is right, week 6's escalation code is wrong, and question 24 is
wrong.** `escalate` should be derived, not self-reported --
`escalate == recommended_action in {escalate_incident,
verify_out_of_band_then_close}` holds 20 of 20 in the batch key -- week 6's flag
should be renamed `control_flag`, and playbook rule 5 should exist as code.

The assessment reviewer reached the opposite conclusion from the same file,
finding `ground_truth_exam.json` marks 050 `escalate=False` and calling the exam
internally consistent. Both are right. The key is self-consistent **and** wrong
on tradecraft, and internal consistency was never the test.

**Three corrections to this report.** My week 6 finding was overstated (see 1.1);
my count in 1.2 was wrong (three rubric criteria and three discussion items, not
four and four); and **1.5 was understated** -- "run the last cell of the notebook,
it builds a backup file" is wrong in **15 of 15** notebooks, not eight. Every
notebook in the course ends in a markdown cell, which runs silently and produces
nothing. Verified.

**What each reviewer wants moved:**

- **SOC practitioner:** exam question 24 to the top, as above. Also three
  early-exit rules in `decisive_stop()` that model real misses -- `internal_sender`
  stops the loop before `check_urls` ever runs, and internal is where BEC lives;
  `"allowlisted" in result.values()` returns `decisive_benign` when *any one* host
  is clean, which is the email 025 attack. And `over_token_cap()` reads
  `RUN_USAGE["answer"]`, but completions do not grow -- week 5 correctly teaches
  that prompt history does. Two of week 6's "controls that fired on nothing" are
  therefore design errors, not demonstration problems, and forcing them to fire
  would hide both.
- **Instructional design:** the real number one is that every TODO specifies its
  answer at line granularity and the granularity never fades -- week 5's TODO 1
  prints four of the student's fourteen lines verbatim. CLO3 is written at Bloom
  **Create** and its 40-point evidence is satisfiable by transcription. It also
  rejects my filing of week 2 as a missing demonstration: week 0 cell 90, sidebar
  2C and the lab all teach *stop when you have a value* while the lab needs *stop
  when the check passes*. Three documents teach the wrong shape. And it opposes my
  `shuffle_answers` fix -- shuffling is off deliberately, documented as "so you can
  compare a second attempt to your first", so **move the 43 keys off index 0
  instead**.
- **Assessment:** will not sign off on the grades. Four of six CLOs report mastery
  from a single criterion scored once, and two of those criteria are structurally
  broken, so CLO4 can never read Exceeds and CLO5 scores below mastery
  cohort-wide. The self-checks carry a **second** cue I missed: the key is the
  longest option in 27 of 43, which `shuffle_answers` does not fix. And the
  discussions -- 12% of the grade -- have no Canvas rubric at all.
- **Beginner experience:** puts the dropout point precisely. In `w1-lab.ipynb`,
  a student who writes `ask_model()` but forgets `return` gets `None`, and the
  **pre-written check cell** raises `AttributeError: 'NoneType' object has no
  attribute 'startswith'`. The course teaches a debugging routine in four places
  that says "find the last line that names your own cell" -- and there is not one.
  Week 0 cell 53 predicts this failure by name. Three lines fix it. It also
  rejects my time estimate: 42 hours came from a run that debugged nothing, and
  its estimate for the real audience is **65 to 85 hours**.
- **Test strategy:** two checks in `verify_content.py`, `check_points()` and
  `check_quiz_points()`, iterate `course["assignments"]` and `course["quizzes"]`
  while this course keeps everything under `modules[].items`. **Neither loop body
  has ever executed**, and both print `ok`. That is why 117 points of unearnable
  rubric had no owner. Its one-rule fix: every check returns the number of items
  it examined and the run fails on zero unless inapplicability is declared.

**Two things to recover before acting.** `docs/course-review-2026-09-07.md` line
19 cites a 6,600-word accessibility review that is no longer on disk. And the
fourteen shipped video transcripts lost their `lang` attribute and titles at the
final build step -- two Level A failures, three lines to fix. There is also no
accommodations statement in the syllabus.

---

## 1. Fix first

### 1.1 Week 6 cannot demonstrate the thing week 6 exists to teach

**Verified, from the code.** This is the most serious finding of the run.

The undefended verdict is produced by
`run_triage(parsed_013, loop_prompt(parsed_013))`, and:

    loop_prompt(parsed) = LOOP_INSTRUCTIONS + CLASSIFY_INSTRUCTIONS
                        + "Facts about the reported email:" + facts_text
                        + "Known-good internal domains and hosts:" + hosts

    run_triage(...)  closing = prompt_text + tool results + schema_text(schema)
                             + "Answer now with one JSON object and nothing else."

**There is no `body_text` on either of those lines.**

**Corrected after panel review.** My first draft said the payload "never reaches
the model" and that the guarded column was "the only one ever exposed to it".
Both are false, and two reviewers caught it independently. `start_messages()`
builds the user turn as `prompt_text + playbook + "The reported email:\n\n" +
parsed["body_text"] + tool_inputs + TOOL_TURN`, so the undefended agent reads the
full body, payload included, on every loop turn.

What survives is narrower and still serious. `run_triage()` ends with a **fresh
one-shot call** -- `answer = extract_json(ask_model(closing))` -- carrying no
message history. So the call that actually writes the verdict is bodyless in the
undefended arm, while the guarded arm's verdict call carries the fenced body.
The asymmetry sits exactly where the verdict is produced.

Five things differ between the two columns, not the four I first counted:

1. the instructions (`LOOP_INSTRUCTIONS + CLASSIFY_INSTRUCTIONS` -> `GUARD_RULES`)
2. the facts function (`format_facts(build_facts(...))` -> `guarded_facts_text(...)`)
3. the known-good host list, present in one and absent from the other
4. the body, at the moment the verdict is written
5. **a hidden-HTML line only the guarded arm gets.** `guarded_facts_text()`
   appends "Hidden text in the HTML part: yes, N characters" or "...: no".
   Emails 013 and 024 both carry zero hidden HTML, so both read "no" -- an
   assurance-shaped line handed to one column and a plausible contributor to the
   5-of-5 flip on both messages.

Cell 11 prints:

> The two columns are the same agent on the same message. The fence is the only
> thing that changed.

That is false on five counts.

The student's control still stands. Adding the guard changed the verdict **5 of 5
on email 013 and 5 of 5 on its clean twin 024**, malicious 0.85 -> benign 0.95.
A change that lands just as hard on the message with no planted paragraph is not
an attack being stopped. The injection moved the verdict **0 times in 10 paired
comparisons**.

This still resolves the open question from the 2026-09-07 measurement. Those
2,156 trials were sound; the lab was never running the comparison it describes.

**Fix:** put the body in the undefended prompt, so the two columns differ only
by the fence. Then re-measure, and only then decide whether the week needs
granite-8b. Until that is done, week 6's numbers mean nothing.

**Related, and it hides the above:** the probabilistic framing added on
2026-09-07 is honest -- the walkthrough video reports its own demonstration
failing, with counts, which is unusually candid teaching. But it now absorbs a
deterministic defect. This will fail the same way every time, on every model.
Reading part 1 still says the payload "moved the model in most runs".

### 1.2 Graded criteria ask for values the export files do not contain

**Verified in three places, reported in the fourth.** The student called this
the highest-value hour of work available, and it is right: each one is a single
line in the cell that builds the row.

**Corrected after panel review.** I first wrote "four rubric criteria and four
discussion items". The assessment reviewer read all seven rubrics and counted
**three rubric criteria** (one in week 6, two in week 7) and **three discussion
items** (weeks 3, 5 and 6). Weeks 3 and 5 are clean at the rubric level: the
table below is right about what the artifacts hold, and wrong about what kind of
instrument grades it.

| week | what is graded | what the artifact holds |
|---|---|---|
| 3 | discussion, 5 of 20 pts: "the indicators your model listed" | `compare_runs()` keeps both verdicts and confidences, drops `indicators` |
| 5 | discussion, 4 of 20 pts: "what the last step added" on email 012 | `one_line(result)` returns `json.dumps(result)[:80]`, hard cut mid-value |
| 6 | rubric, 72 pts: "before and after numbers... which the attached file shows" | `compare_guarded()` discards confidence; no undefended token count |
| 7 | rubric, 36 pts: three properties of the model's summary prose | nothing in the course validates them -- see 1.3 |

Week 6 is the worst of the four because the self-check quotes that same file
showing a `confidence:` line. A student who does the obvious thing loses points
for it, in every section.

### 1.3 Week 7's schema is never validated, and could not be

**Verified.** `OUTPUT_SCHEMA_V2` adds `recommended_action`, `escalate`, and
`summary` as `{"type": "sentences", "how_many": "two"}`. `schema_errors()`
branches on `"allowed" in rule`, then `rule["type"] == "number"`, then falls
through to an `else` that requires a list. A `sentences` field lands in that
`else` and returns "summary has to be a list" -- so `schema_errors` would reject
a **correct** week 7 answer.

It is never called with `OUTPUT_SCHEMA_V2` anywhere in the notebook; only week
2's `OUTPUT_SCHEMA`, inside `classify_email()`. `schema_text()` does have a
`sentences` branch, so the schema is rendered into the prompt correctly and
checked nowhere.

The consequence lands on grading: the 36-point note criterion turns on the three
fields no code in this course ever checks.

**Fix:** add the `sentences` branch, then call `schema_errors(answer,
OUTPUT_SCHEMA_V2)` where the notes are built.

### 1.4 Every correct answer in every weekly self-check is the first option

**Verified in the source and in the Canvas settings.**

| quiz | scored items | correct is first | positions used | `shuffle_answers` |
|---|---|---|---|---|
| w1..w7 self-checks | 43 | **43** | `[0]` only | **false** |
| syllabus acknowledgment | 1 | 1 | `[0]` | false |
| week 0 self-assessment | 10 | 3 | `[0,1,2]` | false |
| final exam | 40 | 18 | `[0,1,2,3]` | true |

A student can score 84 of 84 across all seven self-checks by choosing the first
option every time, without reading a word.

The harm is not grade fraud -- unlimited attempts, highest score counts, so
these are nearly free points anyway. The harm is that these quizzes are the
course's **routing mechanism**. Their feedback names the section to reread, and
the week 0 page tells a student scoring 6 to 8 to go and work those sections. A
student who scores 12 of 12 without reading is told they are ready, seven times
running.

The two bookend quizzes are properly distributed, which shows the convention was
known and simply not applied in between.

**Fix:** `shuffle_answers: true` on the seven weekly quizzes. Five minutes, no
question touched.

### 1.5 Week 1's TODO 1 points at the wrong dictionary, and nothing catches it

**Verified.** Cell 6's step 1 names three dictionaries in four lines: the
request, "a list holding one dictionary", and "that dictionary has a `role`".
Step 2 then says **"Merge `MODEL_EXTRAS` into that dictionary."** Read
literally, the nearest antecedent is the message.

A student who does that builds a request the proxy accepts. `reasoning_effort`
is silently never applied: the check cell passes, six answers return, the export
completes, the token counts are non-zero. Nothing anywhere says it went wrong.

Cell 10 already inspects `ask_model`'s signature to catch the *other* silent
failure in this same function, so the notebook knows this class of bug exists.
It does not check the one its own wording invites. This is the first graded lab
in the course.

**Fix:** name the dictionary -- "merge `MODEL_EXTRAS` into the request
dictionary" -- and have the check cell assert `reasoning_effort` reached the
payload.

### 1.6 Week 3's teaching emails are named three ways, and the code runs a pair no document endorses

**Verified.**

| source | the pair it names |
|---|---|
| the reading, lines 24-28 | **019 and 016** |
| assignment page, steps 5 and 7 | **005 and 016** |
| assignment page, step 10 | **019 and 016** |
| video script, notebook prose, variable names, wrap-up | **005 and 025** |
| quiz Q3 | **025** |
| **the code that runs** | **005 and 016** |

Cell 12 is the clearest instance. Its comment says "builds the finished facts
block for email 025", its variables are `parsed_025` and `block_025`, its error
messages say "for email 025", and the line under them is
`parsed_025 = load_email("016", ...)`. Cell 10 prints the header `email 025`
over 016's data.

Email 025 is a real and different message
(`025-larkseal-review-encoded-subject.eml`). So the wrap-up tells students they
compared something they never opened, and the assignment page contradicts itself
between step 5 and step 10. Nothing errors, because loading 016 is valid.

---

## 2. Mechanisms the course teaches and never demonstrates

This is a pattern, not a list of accidents. Four of the seven weeks build a
lesson on a mechanism whose firing the student never sees.

**Week 2's retry never runs.** Sixteen cells, and not one forces a malformed
reply: no stub, no injected bad sample for TODO 2. Broken samples exist for
TODO 1's `extract_json` and nothing equivalent for the retry loop. The
student's four emails passed first try on eight calls; it had to stub
`ask_model()` itself to prove its loop worked. **granite-3b was chosen for week
2 because it sometimes returns malformed output** -- that choice is now carrying
the whole teaching load of the week, on a sample of four, with no fallback if
the model behaves. Verified.

**Week 5's step cap cannot fire.** The loop is `while step < max_steps and
tools_left(trace)`, `MAX_STEPS = 4`, and `tools_left()` compares tool *names*,
so a repeat does not shrink it. Three distinct calls empty `tools_left` after
step 3 and the loop exits as `tools_exhausted`; one wasted step still ends with
no tools left, so `out_of_room()` still says `tools_exhausted`. `step_cap`
requires four steps used **and** a tool unused, which takes at least two wasted
steps. `w5-content.md` line 26 says "Three tools exist under a cap of four,
which leaves room for one wasted step and no more" -- the arithmetic is right
and the conclusion it invites is wrong. Verified analytically; the student's six
runs hit it zero times.

**Week 6's controls fired on nothing.** Fact check 0 of 11, confidence floor 0
of 11, token cap 0 of 11 across the graded table. The only escalation came from
`injection_detected`, which is not one of the four taught controls.

**Week 1's temperature claim did not reproduce.** `w1-wrap-up.md` line 37
answers its own check question with "It makes them steadier. The same prompt
comes back more alike each time you run it." At three runs a side that often
will not hold, and this student's 0.2 group held the biggest outlier. The rubric
is safe -- "Variation reported" asks only which answer differed most and at what
temperature, not in which direction.

**Four documents state an unhedged result this run contradicts.**
`w6-content.md` line 73, `w6-content-2.md` line 78, `w6-wrap-up.md` line 50 and
`w6-self-check.yaml` line 246 all assert that emails 009 and 012 land under the
0.7 confidence floor. This run had 0 of 11 rows under it. This is the same
defect the 2026-09-07 pass worked to remove from weeks 2, 5 and 7 -- results
from one set of runs quoted as fact -- surviving in the one week whose own
reading warns that numbers vary. Verified.

**The course also gets this right, five times, and those are the model.** Week
5's cell 10 demonstrates `step_cap` with a hand-built trace and says so. Week
6's cell 17 lowers the token cap on purpose so the student watches it fire.
Week 7's false-positive / false-negative detector -- added on 2026-09-07
precisely because a clean run made a swapped counter undetectable -- caught a
deliberate swap of the student's own counters and said out loud that it cannot
decide on an error-free run. Week 3 promised email 005 would be settled in week
5, named the two facts and the mechanism, and it happened exactly. The student
called that the best thing in five weeks.

---

## 3. Graded work a student cannot earn

**Nobody can earn these, in any section:**

- Week 6's 72-point criterion, in the top band, because the file lacks the
  numbers it names (1.2).
- Week 7's 36-point note criterion, checked by nothing (1.3).
- Week 3's 5 discussion points for indicators no artifact carries (1.2).
- Week 5's 4 discussion points for a field truncated at 80 characters (1.2).

**Artifacts of a one-student run, not defects:** every discussion's reply
requirement (an empty board, eight times, ~33 points) and every screenshot
criterion (this harness cannot capture images, ten times). A real cohort earns
both. They are listed only so the scores below are read correctly.

---

## 4. Exam and content gaps the exam depends on

**Two incompatible escalation rules, and the exam grades one of them without
saying which.** Verified. `ground_truth_batch.json` expects escalation on 4 of
its 10 benign emails -- 036, 037, 039 and 043 -- and every one is about money
moving. Week 6's code escalates for four reasons, none of which fires on a clean
message about money. The student answered exam question 20 (a benign
direct-deposit-change notice) with "benign, escalate" from the shipped answer
key it is told to read, and the exam marked it wrong. It was the only question
it missed. Week 7's cell 12 already names the disagreement and stops one
sentence short of resolving it.

**Two authentication states are tested and never taught.** Verified.
`temperror` appears nowhere in seven weeks of content -- only in the exam -- and
it is the whole of question 15. `softfail` appears once, in `w7-content.md`
line 41, as an example of jargon *not* to write to a user, and it is half of
question 26.

**The week 8 overview contradicts itself two rows apart.** Verified, and it is a
partial regression from the 2026-09-07 exam resize. Line 8: "Questions | 30,
multiple choice". Line 9: "Points | 30, across 40 questions". The time budget
below it still adds fifteen plus fifteen.

**"The questions ask what your own runs showed you"** (`w8-overview.md` line 19)
did not hold for any of the forty questions the student sat; each hands over its
own facts. Reported, not independently recounted.

---

## 5. Orientation

**The backup instructions do not work when they are given.** Verified.
`using-the-notebook-server.md` line 32 says "Any cell can tell you what is left.
Run `budget_left()`", line 37 says "Run the last cell of the notebook. It builds
a backup file", and line 46 says "In any notebook, run `restore_my_work(...)`".
All three helpers are defined **only in the seven lab notebooks**. They are
absent from all seven sidebars and from `week00-python-on-ramp.ipynb`, whose
last cell is markdown. "Any notebook" is false for eight of the fifteen,
including the only one a student has when they read that page -- and the same
page warns that all work lives in browser storage and vanishes if you switch
machines. Week 0 is where a beginner spends five hours.

**The glossary still describes the key design that was replaced.** Verified.
`glossary.md` line 27: "The course sets it for you and never shows it." Two
other pages tell students to paste it into `API_KEY = ""`. The JupyterLite move
corrected three pages; this entry was missed.

**Week 0 cell 77 requires running a cell out of order**, which cells 0 and 123
twice tell the student never to do, and in a top-to-bottom run the numbers it
promises (316 / 79.0) never appear. Verified.

---

## 6. What the course does well

Said plainly, because the list above is long and the run does not support a
verdict of "this course is broken".

- **The student finished it, first try, on every TODO.** Fourteen TODO cells,
  all correct on the first attempt, and it never once needed the instructor.
- **Weeks 4 and 7 are clean.** Week 4: eleven cell references correct, email
  identity consistent across all seven documents, the sidebar covering both
  TODOs, and every graded field present in the export. Week 7 is the only lab
  in the course with no Python gap -- it hands over no code, only English, and
  every ingredient really is in week 0 or the sidebar.
- **The cell-number convention is right in six weeks of seven.** Week 1 is the
  outlier, not the pattern.
- **Week 3 to week 5 is a genuine through-line.** A promise made in week 3 about
  email 005 was kept exactly in week 5, with the mechanism named in advance.
- **The week 6 walkthrough video reports its own demonstration failing, with
  counts.** That is rare and it is right, even though it is currently absorbing
  a defect that is not variance.
- **Cost control works.** The whole course, including the student's own extra
  measurements, cost **$0.0106 of $2.00**. The per-key budget, the model
  allowlist and the rate limits all held.

---

## 7. Scores, time and money

**Quizzes.** Week 0 self-assessment 10/10; weekly self-checks 12/12 in every
one of weeks 1 to 7; syllabus acknowledgment 1/1. **Final exam 39/40, 29.25 of
30.** Read those weekly scores against 1.4: answering the first option would
have produced the same result.

**These numbers measure the course, not a beginner.** The student already knew
Python and could not unknow it, which is why the run's value is in what it
recorded about *where* the course expects knowledge it never gave, not in
whether it passed.

**Time: about 31 hours**, of which roughly 26 was the course as assigned, against
the course's own 42-hour estimate. It came in under every weekly estimate
because it never had to debug a TODO -- so read 42 hours as realistic for a real
beginner, not generous.

**Money: $0.010571 of $2.00.** Week 6 was the most expensive at $0.0042 (160
calls). A clean single pass through week 1 is about two hundredths of a cent.
The $2.00 budget is roughly 190 times what the course costs.

---

## 8. Suggested order of work

1. **Put the email body in week 6's undefended prompt** (1.1), then re-measure.
   Everything else in week 6 is downstream of this.
2. **Add the four missing fields to the four export cells** (1.2). One line
   each, and it recovers points nobody in any section can currently earn.
3. **`shuffle_answers: true` on the seven weekly quizzes** (1.4). Five minutes.
4. **Fix week 1's TODO 1 wording and add the `reasoning_effort` assertion**
   (1.5). It is the first graded lab and the failure is silent.
5. **Settle week 3's email identity on one pair** (1.6) and make the notebook,
   the video, the quiz and the wrap-up agree with the code.
6. **Add the `sentences` branch to `schema_errors` and call it on V2** (1.3).
7. **Resolve the escalation rule** (section 4) and say which one the exam grades.
8. **Move `budget_left`, `backup_my_work` and `restore_my_work` into a shared
   cell** every notebook carries, including week 0 (section 5).
9. **Force week 2's retry and week 5's step cap to fire at least once** in a way
   the student watches (section 2).
10. **Fix the week 8 overview's two question counts** and either teach
    `temperror` and `softfail` or drop the two exam items that need them.

---

## 9. About the method

The run cost about eight hours of wall time across nine sittings, one module
each, and $0.0106 in model spend. Each sitting read the previous sittings' notes
and could not look ahead.

Two things are worth keeping for next time. **Check the pipeline before
believing the reviewer** -- four of this run's findings were my export, and one
of them (links) had the student reporting the same false problem for four weeks
running. And **ask the reviewer to check mechanisms, not just outcomes**: the
instruction "does the thing this week teaches actually fire in your run?" is
what produced 1.1, and the two never-firing mechanisms in weeks 2 and 5.

The live notebook site was also one revision behind the repository when the run
started -- `w7-lab.ipynb` was missing the false-positive attribution check
committed as 6f7c0d4. Fourteen of fifteen notebooks matched by hash and one did
not, and nothing reported it. There is no gate comparing the served site to the
repo. That is worth adding.
