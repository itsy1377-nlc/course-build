# Assessment and measurement review

**Course:** ITSY 1377, Agentic AI and Security Operations, 8 weeks, asynchronous
**Reviewed:** 2026-09-08
**Scope:** ten scored instruments, seven lab rubrics, eight discussion point tables,
the outcome scale in `content/course.yaml`, and the delivery code in
`canvas/build_course.py`
**Method:** every count below was produced by parsing the source YAML, the lab
notebooks and the corpus release files. Scripts are in a scratch directory and
touched no course file. Nothing in `content/`, `lab/` or `corpus/` was modified.

Each section separates **Verified** (read out of a file or computed from one) from
**Asserted** (my professional judgment, which another reviewer could dispute).

---

## 0. The three rulings that matter

1. **Four of the six CLOs report mastery from a single rubric criterion, and two of
   those four criteria have a top band that no student in any section can reach.**
   CLO4 and CLO5 are capped below their own top rating for structural reasons, and
   the modal honest student behaviour scores them *below* the mastery threshold.
   This is the only finding in this review that is fatal on appeal.

2. **The seven weekly self-checks carry two independent giveaway cues, not one.**
   The correct option is first in 43 of 43 items, and it is also the longest option
   in 27 of 43 (63 percent against a 25 percent chance rate, p ≈ 1.8e-07). Turning
   on `shuffle_answers` removes the first cue and leaves the second intact. The
   proposed five-minute fix is necessary and not sufficient.

3. **The final exam is sound in design and damaged in one specific place.** The ten
   items added in the 30-to-40 resize are distinguishable from the original thirty
   on four separate surface features, including authored answer position: all ten
   sit at position 1. They are also the only exam evidence for CLO3, CLO5 and CLO6.

---

## 1. Instrument inventory

Verified, from the ten YAML files and `content/course.yaml`.

| Instrument | Entries | Scored | Points | Attempts | Shuffle | Counts toward grade |
|---|---|---|---|---|---|---|
| Week 0 self-assessment | 10 | 10 | 10 | unlimited | false | no (`ungraded: true`) |
| Syllabus acknowledgment | 1 | 1 | 1 | unlimited | false | no (`ungraded: true`) |
| W1 self-check | 6 | 6 | 12 | unlimited | false | yes |
| W2 self-check | 6 | 6 | 12 | unlimited | false | yes |
| W3 self-check | 6 | 6 | 12 | unlimited | false | yes |
| W4 self-check | 5 | 5 | 12 | unlimited | false | yes |
| W5 self-check | 6 | 6 | 12 | unlimited | false | yes |
| W6 self-check | 6 | 6 | 12 | unlimited | false | yes |
| W7 self-check | 8 | 8 | 12 | unlimited | false | yes |
| Final exam | 46 | 40 | 30 | 1 | **true** | yes |

**Correction to the e2e report.** The seven weekly self-checks hold **43** scored
items, not 44. The student's report says 44 twice. Your report says 43 and is right.

**Grade weights** (`course.yaml`): Labs 60, Final Exam 20, Discussions 12,
Self-Checks 8, Orientation 0.

---

## 2. Item analysis

### 2.1 Answer-position and answer-length cues

Verified. Simulation of three read-nothing strategies against every authored form.

| Strategy | Self-checks (43) | Final exam (40) | Week 0 (10) |
|---|---|---|---|
| Always choose option 1 | **43 / 43 (100%)** | 18 / 40 (45%) | 3 / 10 (30%) |
| Always choose the longest option | **27 / 43 (63%)** | 14 / 40 (35%) | 3 / 10 (30%) |
| Always choose the shortest option | 5 / 43 (12%) | 8 / 40 (20%) | 3 / 10 (30%) |

Tail probabilities against a 25 percent chance rate:

| Cue | Self-checks | Final exam |
|---|---|---|
| Key at position 1 | p = 1.3e-26 | p = 0.0047 |
| Key is the longest option | p = 1.8e-07 | p = 0.103 |

**The length cue by week.** Verified.

| Week | Items | Longest option is the key |
|---|---|---|
| 1 | 6 | 3 |
| 2 | 6 | 3 |
| 3 | 6 | 4 |
| 4 | 5 | 1 |
| 5 | 6 | **6 of 6** |
| 6 | 6 | **6 of 6** |
| 7 | 8 | 4 |

Weeks 5 and 6 are perfectly cued on length. A student who reads nothing and picks
the longest option scores 12/12 on both. Shuffling does not touch this.

**Asserted.** The length cue is a by-product of good feedback writing, not
carelessness. The keys in weeks 5 and 6 are long because they are precise
("It runs the tool again and the step still counts. A run that keeps repeating
reaches four steps, and `out_of_room()` returns `step_cap`.") and the distractors
are short because they are wrong in one clean way. The fix is not to shorten the
key. It is to lengthen two distractors per item so the key is not the outlier.

### 2.2 Distractor quality

Verified counts of a classic cue, the absolute term (`always`, `never`, `all`,
`none`, `every`, `only`, `must`, `cannot`, `no `):

| Instrument | Keys containing an absolute | Distractors containing one |
|---|---|---|
| W1-W7 self-checks | 8 / 43 | 20 / 129 |
| Final exam | 5 / 40 | 22 / 120 |

That ratio is healthy. Absolutes are not concentrated in the distractors, which is
the failure mode this cue usually flags. The self-checks are clean here.

**Asserted, from reading all 43 self-check items.** Distractor functionality is
uneven. My classification:

| Category | Items | Examples |
|---|---|---|
| All three distractors plausible to a partially prepared student | 18 | w2-q2, w3-q2, w3-q5, w4-q1, w5-q1, w5-q4, w6-q3, w7-q3 |
| One distractor implausible on register grounds | 15 | w2-q3 ("Because it is private and you are not allowed to see it"), w3-q1, w6-q5 |
| Two or more distractors non-functional | 10 | w1-q3 ("Nobody. Escalating a ticket closes it."), w4-q4 ("Run whichever of the three tools is closest"), w5-q6 |

The strongest distractor set in the course is week 4's. Every option in w4-q1 is a
statement a novice actually believes about tool calling, and only one is right. The
weakest is w1-q3, where three of four options are self-refuting.

**A structural defect in week 7.** Verified. Items w7-q5 through w7-q8 share one
template: "Which of this week's seven use cases is that, and what would it need
first?" In all four, the correct use-case name appears in **two** of the four
options, with the distinguishing clause in the second half. A student who can name
the use case and cannot judge the prerequisite is at 50 percent, not 25. Those four
items are 6 of week 7's 12 points and they measure one construct, not four. Week 7
has 8 items and roughly 5 independent measurements.

### 2.3 Items answerable without the week's content

**Asserted**, from reading each item against its own `section:` tag.

| Reason | Count of the 43 | Items |
|---|---|---|
| The stem states the mechanism the key names | 5 | w1-q4, w1-q5, w2-q2, w6-q1, w6-q6 |
| General technical literacy suffices | 7 | w2-q4, w2-q6, w4-q2, w4-q4, w5-q6, w7-q2, w7-q3 |
| Two or more distractors are self-refuting | 5 | w1-q3, w3-q3, w3-q4, w5-q2, w7-q1 |
| **Total judged answerable without the week's material** | **~17 of 43 (40%)** | |

The two clearest cases are w1-q4 and w1-q5. The stem of q4 says the tool "gives
each one a number from 0 to 100" and "writes nothing else"; the key is "Scoring AI."
The stem of q5 says the tool "looks up the version running on each machine, opens a
ticket for every machine that is behind, and stops after fifty machines"; the key is
"An agentic workflow." Both stems are the definitions.

w6-q1 is the same shape at higher stakes: the stem says the paragraph "is addressed
to AI triage tools and tells them to record benign and not escalate," and the key is
that the model "can read that paragraph as an order instead of as evidence."

### 2.4 Items testing recall of a specific value

Verified. Four of 43.

| Item | The value | Comment |
|---|---|---|
| w2-q1 | the four schema key names | Legitimate. The student wrote the schema check. |
| w5-q1 | the five stop reasons | Legitimate; the stem supplies the trace. |
| w5-q3 | `MAX_STEPS = 4` | Borderline. The stem does not give the cap. |
| **w6-q4** | `CONFIDENCE_FLOOR = 0.7` | The stem gives 0.61 and requires the constant from memory. |

This is a low rate and it is to the course's credit. The exam is cleaner still:
every scenario item supplies its own facts.

### 2.5 One self-check item quotes a file that does not exist

Verified against `lab/notebooks/w6-lab.ipynb` cell 14, `compare_guarded()`.

w6-q4's stem reads "Your export file holds this for email 012" and prints five
fields. The row `compare_guarded()` actually writes holds eleven keys:

```
email_id, verdict_without_guardrails, verdict_with_guardrails, verdict_changed,
payload_placement, problems, escalate, escalate_reason, stop_reason,
tokens, tokens_written
```

| Field quoted by w6-q4 | Present in `week6_guardrails.json` |
|---|---|
| `verdict:` | **no** (the row uses two prefixed names) |
| `confidence: 0.61` | **no** (`compare_guarded()` never copies it) |
| `problems: []` | yes |
| `stop_reason:` | yes |
| `escalate: true` | yes |

Two of five field names in a quoted artifact excerpt are absent from the artifact.
The item is still answerable, because the reasoning does not depend on the file. But
a student who opens the file to check is told, by their own evidence, that they ran
the lab wrong. This is the same missing `confidence` field that breaks the week 6
rubric in section 4.

### 2.6 Difficulty

There is no response data, so classical item difficulty (p-values) cannot be
computed and no discrimination index (point-biserial) exists for any item in this
course. That is worth stating plainly to a program chair: **no item in ITSY 1377
has ever been item-analysed against student responses.** The only empirical
evidence is one run by a subject who already knew Python and scored 84/84 and
39/40, which establishes a ceiling and nothing else.

The exam carries an authored difficulty tag. Verified distribution: 10 easy, 18
medium, 12 hard. The file header says "8 easy, 13 medium, 9 hard," which was the
thirty-item distribution. The header is stale.

---

## 3. CLO alignment and coverage

### 3.1 The only path to a Canvas Outcome is a rubric criterion

Verified, `canvas/build_course.py`. `attach_rubric()` sets
`rubric[criteria][i][learning_outcome_id]` from a criterion's `outcome:` key
(line 505). No other code path posts an outcome alignment. `make_quiz()` posts no
outcome result of any kind.

**Consequence.** The `outcome:` keys on the 40 exam items are documentation. They
reach Canvas nowhere. Every CLO result in the program's outcome report comes from a
rubric criterion, and from nothing else. The exam is 20 percent of the grade and 0
percent of the outcome evidence.

The exam file's own header states this rule correctly ("The exam reports into no
Canvas Outcome") and then contradicts itself by tagging 25 items with CLO keys and
saying every item carries `outcome: "none"`. Both statements are in the same
header. Verified: 15 items are tagged `none`, 25 are tagged CLO1-CLO6.

### 3.2 What the 15 `none` tags actually are

Verified. They are not a coverage gap. They are the four breadth topics the
build brief requires, and they partition exactly:

| Breadth topic | Exam items |
|---|---|
| B1, AI and agentic workflows in IT and security operations | 3 |
| B2, the range of AI-assisted security use cases | 4 |
| B3, security operations components | 3 |
| B4, the wider AI risk set | 5 |
| **Total tagged `none`** | **15** |

The 43 self-check items are also all tagged `none`, correctly: the self-checks
cover breadth topics and the file headers say so.

**Ruling:** the `none` tags are correct and well documented. This is not a defect.

### 3.3 Outcome evidence, by CLO

Verified, from the seven rubrics and `calculation_method: latest`.

| CLO | Verb in the outcome text | Rubric criteria | Points | Weeks | **Reported mastery comes from** |
|---|---|---|---|---|---|
| CLO1 Extract email facts | Extract | 1 | 25 | w3 | week 3, one criterion |
| CLO2 Classify and validate | Classify, validate | 2 | 75 | w1 (25), w2 (50) | **week 2 only** |
| CLO3 Build a bounded agent | Build | 2 | 80 | w4 (40), w5 (40) | **week 5 only** |
| CLO4 Judge guardrails | Judge | 1 | 72 | w6 | week 6, one criterion |
| CLO5 Document a decision | Document | 1 | 36 | w7 | week 7, one criterion |
| CLO6 Measure accuracy | Measure | 1 | 56 | w7 | week 7, one criterion |

**Four of six CLOs rest on a single criterion scored once.** Under `latest`, CLO2
and CLO3 also reduce to a single observation, because the later week overwrites the
earlier. So **all six** reported CLO results are n = 1.

The `course.yaml` header defends `latest` on the grounds that "for every CLO the
primary artifact is also the last one scored." That is true and it is the right
choice. It is also the reason there is no redundancy anywhere in the outcome
report: a single grader error, or a single defective criterion, propagates
undiluted into the program's mastery data. Section 4 shows two such criteria.

### 3.4 Depth against the verb

**Asserted**, with the evidence named.

| CLO | Verb claims | Criterion measures | Depth met? |
|---|---|---|---|
| CLO1 | Extract | Whether all six emails carry a labeled facts block in the shipped order with shipped labels | **Partly.** The top band grades format compliance and value agreement, not the *choice* of facts. The choice is graded by the un-linked "Written answer" criterion beside it. |
| CLO2 | Classify **and validate** | w2 "Output validation," 50 pts, the retry log | **Yes, in principle.** In practice the week's mechanism cannot be made to fire, so most submissions evidence a retry loop that never ran. |
| CLO3 | **Build** an agent | w5 "Bounded tool loop," 40 pts, read off the exported trace | **No.** The criterion grades the artifact the loop produced, and the student report documents that six of fourteen lines of `run_loop()` are printed verbatim in the TODO comment. A file six transcribed lines produce cannot evidence "build." |
| CLO4 | **Judge** whether guardrails reduce risk | w6 "Guardrail judgment," 72 pts, a written argument with before/after numbers | **Yes, and it is the best-designed criterion in the course.** It is also the one whose top band cannot be earned. |
| CLO5 | Document a decision so another analyst can act | w7 "Triage note," 36 pts | **No.** Three of the four top-band requirements are properties of prose the *model* wrote and the student is instructed not to edit. |
| CLO6 | Measure accuracy and recommend where review stays | w7 "Accuracy and human review," 56 pts | **Yes.** This is the strongest outcome alignment in the course. |

CLO3 is the sharpest mismatch: 80 rubric points and a verb ("Build") that the
instrument cannot see, because nothing in the graded artifact distinguishes a
student who understood the loop from one who copied it.

### 3.5 Is the exam's 40-item / 30-point structure proportional?

Verified. Comparing exam sampling with rubric weight:

| CLO | Exam items | Exam points | Share of the 25 CLO items | Rubric points | Share of the 344 outcome-linked lab points |
|---|---|---|---|---|---|
| CLO1 | 6 | 4.50 | 24% | 25 | **7%** |
| CLO2 | 5 | 3.75 | 20% | 75 | 22% |
| CLO3 | 4 | 3.00 | 16% | 80 | **23%** |
| CLO4 | 4 | 3.00 | 16% | 72 | 21% |
| CLO5 | 3 | 2.25 | 12% | 36 | 10% |
| CLO6 | 3 | 2.25 | 12% | 56 | 16% |
| breadth (`none`) | 15 | 11.25 | — | 0 | — |

**Ruling: broadly proportional, with one inversion.** CLO2, CLO4, CLO5 and CLO6 are
sampled within a few points of their rubric weight. CLO1 is over-sampled by a factor
of three and CLO3 is under-sampled. That is defensible on its face — header reading
is easy to test in multiple choice and agent-building is not — and the exam header
says exactly that. I would not change it.

**The real proportionality problem is elsewhere.** 15 of 40 items (37.5 percent of
the exam, 11.25 of 30 points, 7.5 percent of the whole course grade) assess breadth
topics that carry **no** rubric weight, no outcome, and no lab evidence anywhere.
Breadth is a build-brief requirement, so this is a policy question rather than a
defect, but a program chair should know that 7.5 points of every student's final
grade come from material that is assessed once, in one format, and never practised.

### 3.6 The ten items added in the resize

Verified. The exam grew from 30 items to 40 to give CLO3, CLO5 and CLO6 exam
coverage. The ten added items (`exam-q31` through `exam-q40`) differ from the
original thirty on four independent surface features:

| Feature | Original 30 | Added 10 |
|---|---|---|
| Authored key position | 8 / 8 / 8 / 6 across the four slots | **10 / 0 / 0 / 0 — all at position 1** |
| `artifact:` field | 21 name a reserved email or a named constant | **9 of 10 are `none`** |
| `level:` vocabulary | Recall, Apply, Analyze, Recognition, Analysis | adds **Comprehension (4), Application (2), Evaluation (1)** |
| Reference block | 13 items read one of six shared emails | none read a block |

Consequences, in order of seriousness:

1. **The whole exam's authored position-1 rate is now 18 of 40 (45%, p = 0.0047).**
   The file header still claims "first in 8, second in 8, third in 8 and fourth in
   6" and warns, correctly, that `tools/qti.py` "emits no shuffle metadata at all,
   so on that path the authored order is the delivered order and the spread above is
   the only protection there is." The spread the header relies on no longer exists.
   On the QTI path a first-option strategy scores 18/40 and **10/10 on the ten items
   that are the only exam evidence for CLO3, CLO5 and CLO6.**
2. **Nine of ten are context-free.** The exam's stated design is that every scenario
   item hands over a new email's facts. These ten do not, which makes them exactly
   the recall-shaped items the header says an open-book exam should avoid.
3. The `level:` taxonomy now has eight labels where the header documents five, with
   two duplicate pairs (Apply/Application, Analyze/Analysis).

**This is a five-minute fix and it is the highest-value exam edit available:**
redistribute the ten authored positions and normalise the three level labels.

---

## 4. Rubric quality

### 4.1 Structure

Verified across the seven lab rubrics: 25 criteria, 700 points.

| Rubric | Criteria | Levels per criterion | Total | Floor if every criterion is scored at its lowest level |
|---|---|---|---|---|
| w1 | 4 | 4 / 4 / 4 / 4 | 100 | **24** |
| w2 | 4 | 3 / 4 / 3 / 3 | 100 | 0 |
| w3 | 4 | 4 / 4 / 4 / 4 | 100 | 0 |
| w4 | 3 | 3 / 4 / 4 | 100 | 0 |
| w5 | 4 | 4 / 4 / 4 / 4 | 100 | 0 |
| w6 | 3 | 4 / 4 / 4 | 100 | 0 |
| w7 | 3 | 4 / 4 / 4 | 100 | 0 |

**Week 1 is the outlier and it is a real defect.** Its four criteria bottom out at
6 points, not 0, so any submission at all scores at least 24/100. Its own header
calls that level "Beginning" — the exact label `course.yaml` says was removed
because "no rubric in `content/` has a fifth level, so that rating was unreachable."
Week 1 is that rubric. Its floor level maps positionally onto the scale's fourth
rating, "No evidence" (0 points), while awarding 24 percent of the criterion. On
the outcome-linked criterion ("First judgment," CLO2), a student who "names nothing
to check" is recorded as 6/25 in the gradebook and "No evidence" on CLO2. Those two
records disagree. Week 1 is not the latest CLO2 evidence, so the outcome report
survives it, but the gradebook floor is unjustified and inconsistent with the other
six labs.

**Three-level criteria.** Verified: five of 25 criteria offer three levels rather
than four (w2 x3, w4 x1, and w2's 50-pointer is four). A three-level criterion
cannot map onto a four-rating mastery scale, and none of the five is
outcome-linked, so no outcome result is affected. It is a consistency issue, not a
measurement one.

### 4.2 Do the levels discriminate?

**Asserted.** Mostly yes, and unusually well for a community-college technical
course. The good pattern, which appears in nineteen of twenty-five criteria, is
that each level names a *countable* condition rather than a quality adjective:

> Meets standard. All six emails carry a labeled facts block in the shipped order.
> **One** fact group is missing from every block, or **one** email's block is
> missing a value the other five carry.

A grader can count fact groups. Two graders will agree. That is the whole game and
this course plays it well most of the time.

Where discrimination fails, it fails for one of two reasons:

| Criterion | Points | Failure |
|---|---|---|
| w6 "Guardrail judgment" | 72 | Top and second band are separated by "before and after numbers, **both of which the attached file shows**." The file shows neither. The band is unreachable, so 72 and 54 do not discriminate — they are one band. |
| w7 "Triage note" | 36 | Top band requires "every recommended action fits the verdict" and "every summary... names no header field and no tool." Both are properties of model-written prose. The criterion discriminates between models, not between students. |
| w2 "Submission completeness" | 15 | Three levels, 15 / 10 / 0. The gap between 10 and 0 is the difference between "one item hard to read" and everything else. |
| w4 "Submission completeness" | 32 | Three levels on a 32-point criterion — the largest compliance criterion in the course, with the coarsest scale. |

### 4.3 Observability by a grader who did not watch the student work

The w1 rubric header states the rule explicitly and it is the right rule:

> EVERY CRITERION IS GRADEABLE FROM THE SCREENSHOT, THE EXPORTED FILE AND THE
> WRITTEN ANSWER. Nobody opens or runs a student's notebook to grade this.

Verified: 22 of 25 criteria meet it. Three do not.

| Criterion | Points | What the grader cannot see |
|---|---|---|
| w6 "Guardrail judgment" | 72 | The before/after numbers the top band requires are not in `week6_guardrails.json`. `compare_guarded()` writes eleven fields and `confidence` is not one of them; the undefended run's token count is discarded. |
| w7 "Triage note" | 36 | Nothing in the course validates the three prose properties. `schema_errors()` has no `sentences` branch and is never called with `OUTPUT_SCHEMA_V2`, so a *correct* week 7 answer fails the shipped validator. |
| w7 "Accuracy and human review" | 56 | The top band requires the student to "name one email this run got wrong." `week7_triage_report.txt` holds aggregate counts only — `Correct calls`, `Accuracy`, `False positives`, `False negatives`, `Escalation agreement`. There is no per-email correctness anywhere in the file. |

**Note on the third one:** this is an *observability* failure, not an unearnable
band. The student can see the wrong emails in cell 15 and write one down. The
grader cannot check it against the artifact, so the criterion is unverifiable and
therefore unappealable in either direction.

### 4.4 Where I differ from the e2e report on this point

Your report says "**Four rubric criteria** ask for values the export file does not
contain (weeks 3, 5, 6, 7)." I checked all four against the export cells.

| Week | The claim | What I found |
|---|---|---|
| 3 | rubric asks for a value the file lacks | **Not the rubric.** `compare_runs()` writes `ungrounded_confidence` **and** `grounded_confidence`, so the "Verdict comparison" criterion (25 pts) is fully earnable. The missing field is `indicators`, and it is asked for by the **discussion**, item 3, 5 points. |
| 5 | rubric asks for a value the file lacks | **Not the rubric.** The export cell writes `uncapped_run: {email_id, steps_used, tokens}` plus per-email `tokens`, so "Cost of an uncapped run" (20 pts) is fully earnable. The truncated field is the tool result at 80 characters, asked for by the **discussion**, 4 points. |
| 6 | rubric asks for a value the file lacks | **Confirmed.** 72 points, top band. |
| 7 | rubric asks for a value the file lacks | **Confirmed, twice** — the 36-point criterion (unvalidatable properties) and the 56-point criterion (unverifiable claim). |

So the correct statement is **three rubric criteria and three discussion items**,
not four and four. The discussion items matter less, and the two extra rubric
criteria I found in week 7 matter more, because the second of them carries CLO6.

### 4.5 What this does to score distributions

Verified arithmetic. Each lab is 100 points; the Labs group is 60 percent of the
grade across seven labs, so **one lab point = 0.0857 percentage points** of the
final grade.

**Week 6, the 72-point criterion.**

| Student behaviour | Band | Criterion | Lab | Effect on final grade |
|---|---|---|---|---|
| Reaches a judgment, cites the two confidences printed on screen (the obvious act) | **36** — "cites a number the attached file does not show" | 36/72 | 64/100 | −3.09 pp |
| Reaches a judgment, cites a count derived from the file | 54 — "at least one number the attached file shows" | 54/72 | 82/100 | −1.54 pp |
| Does everything the top band asks | **unreachable** | — | — | — |

The cohort ceiling on week 6 is **82/100**. The spread between the two honest
behaviours is 18 lab points, and the *more* natural behaviour is the one that
scores lower. That is an inverted discrimination: the criterion penalises the
student who read their own screen.

**Week 7, the 36-point criterion.** Using the one empirical measurement available
(the e2e student parsed its own twenty notes): one action contradicted its verdict,
nine summaries named a header field or a tool, fourteen ran past two sentences. The
Meets band tolerates "one or two notes thin in one place." Nine is not one or two.

| Band | Requires | Achievable? |
|---|---|---|
| 36, Exceeds | every note clean on all three properties | no |
| 27, Meets | one or two notes thin | no, on the one run measured |
| **18, Approaching** | format holds, content thin | **the expected outcome** |

That is 18 lost lab points, another −1.54 pp, for something the student is
instructed not to touch.

**Combined systematic loss for a fully compliant student: 36 lab points across two
labs, −3.09 percentage points of the final grade**, before any judgment about the
quality of their actual work. If the week 6 student does the obvious thing, the
figure is −4.63 pp.

**What it does to the outcome report.** This is worse than the grade effect. The
four criterion levels map positionally onto the four-rating mastery scale
(4 Exceeds / 3 Meets / 2 Approaching / 0 No evidence), and `mastery_points: 3`.

| CLO | Best attainable rating | Expected rating for a compliant student | Meets mastery? |
|---|---|---|---|
| CLO4 | **Meets (3)** — Exceeds is unreachable | Approaching (2) if they cite screen numbers | **no** |
| CLO5 | **Approaching (2)** on the one run measured | Approaching (2) | **no** |

**No student in any section can be recorded as Exceeding CLO4, and the expected
recorded result for CLO5 is below the mastery threshold.** Because
`calculation_method` is `latest` and each of these is a single observation, there
is no other evidence in the system to dilute it. If this course runs and the
program reports outcome attainment, CLO5 will read as a cohort-wide failure caused
entirely by an instrument.

### 4.6 Grade appeal exposure

**Asserted, and I would say this to a hearing.**

A week 6 appeal is unanswerable on the merits. The student's claim is: *the top band
requires evidence from an artifact your own code does not produce, and I can show
you the line.* The line is `lab/notebooks/w6-lab.ipynb` cell 14, and the eleven keys
`compare_guarded()` appends. The institution has no counter-argument. It would have
to grant the appeal and, having granted one, would have to grant every one in the
section, in every section, retroactively.

A week 7 "Triage note" appeal is the same shape with an aggravating factor: the
assignment page's own warning box says "You write no prose into the note by hand."
The rubric then grades that prose. A student who quotes both documents wins.

A week 7 "Accuracy and human review" appeal runs the other way — the *institution*
cannot defend a deduction, because the artifact does not record which emails were
wrong, so a grader disputing a student's claim has no evidence either.

Three of the seven labs currently carry a criterion I would advise the college not
to defend.

### 4.7 Discussions: 12 percent of the grade with no rubric

Verified, `canvas/build_course.py`, `make_discussion()`. A graded board posts
`title`, `message`, `discussion_type`, `require_initial_post`, points and an
assignment group. **It attaches no rubric.** There is no `attach_rubric()` call and
no rubric file exists under `content/rubrics/` for any discussion.

The scoring criteria live in a markdown table inside the discussion body. Verified
totals: 20 points each on w1-w7, 140 points, 12 percent of the grade. Every line is
dichotomous — 5 points or 0 — with no level descriptions and no partial credit.

| Week | Lines | Reply-dependent points | Timeliness points that require the reply |
|---|---|---|---|
| 1 | 4 | 5 | 0 |
| 2 | 3 | 6 | 2 |
| 3 | 5 | 4 | 1 |
| 4 | 5 | 4 | 1 |
| 5 | 4 | 6 | 2 |
| 6 | 5 | 6 | 2 |
| 7 | 6 | 5 | 1 |
| **Total** | | **36** | **9** |

45 of 140 discussion points (32 percent) require a classmate to have posted first.
Four boards give an instruction that a thin or new board cannot satisfy ("Read a
post nobody has answered yet"). In an under-enrolled section, or in the first two
days of any section, no fallback is stated.

Three discussion lines ask for values no artifact carries — w3 item 3 (5 pts,
`indicators`), w5 item 2 (4 pts, an 80-character truncation), w7 item 2 (3 pts, the
per-email error list). That is 12 of 140 points, 0.86 pp of the final grade.

**Ruling.** 12 percent of the grade is scored from prose, with no rubric object in
Canvas, no criterion levels, no anchor descriptions and no outcome link. Under
appeal that is the weakest-documented component in the course, weaker than any lab.

### 4.8 Compliance weight

Verified. Criteria named "Submission completeness" total **133 of 700 lab points**
(19 percent), which is 11.4 percentage points of the final grade for attaching
three readable files. Adding the 8 percent self-check group (see section 6), a
student who submits everything and reads nothing is at roughly **19 points of 100
before any judgment of their work is made.**

Separately, criteria whose level text mentions a screenshot total **242 of 700
points (35 percent)**. No page in the course explains how to take a screenshot, to
a population for whom this is the first college technology course.

---

## 5. The exam's validity problems: four rulings

### 5.1 `temperror` and `softfail`

**Verified by grep across `content/`, `lab/`, `corpus/emails/` and the student file
allowlist in `course.yaml`. These two are not the same case and should not get the
same remedy.**

| Token | In seven weeks of prose | In an email a student's own parser reads | Graded on |
|---|---|---|---|
| `temperror` | **nowhere** | **nowhere** — the only corpus message carrying it is 052, in `instructor/exam-emails/`, reserved | exam item 19 (delivered position 15), entirely |
| `softfail` | once, `content/pages/w7-content.md` line 41, as an example of jargon **not** to write to a reporter | **four times**: teaching emails 010 and 025, batch emails 032 and 037 | exam item 23 (delivered position 26), partly |

Week 3's `build_facts()` copies `parsed["auth"]["spf"]` and `FACT_LABELS` renders it
as "SPF result". Email 010 is in `LAB_EMAILS` for week 5 and emails 032 and 037 are
in the week 7 batch of twenty. **So a student who did the work has seen
`SPF result: softfail` printed in their own facts block at least three times.** They
have never seen it explained, and the one place the course prints the word in prose
tells them not to use it.

Week 3 teaches `pass`, `fail` and `none` and teaches the principle "missing is not
failed," which is strong enough to reason from to both answers.

**Ruling.**

- **Item 19 (`temperror`): drop it or teach it.** The exam is testing recognition
  of a token that appears in no artifact a student can reach. There is no path from
  the course as shipped to this item except inference from a principle stated about
  a different value. It is a fair *reasoning* item and an unfair *recognition* item,
  and its own `level:` tag says Recognition. One row added to week 3's "what a
  passed check really means" section — a check can pass, fail, be absent, or fail
  to run — fixes it and improves the week.
- **Item 23 (`softfail`): keep it, and add one sentence to week 3.** The student has
  seen the token in their own output. What is missing is that it is a *weak* fail,
  not a strong one, and that the item's real content is auth failure on a trusted
  sender, which is taught. This is a documentation gap, not a validity failure.

### 5.2 The escalation rule

**Verified, and my ruling differs materially from the e2e report.**

Your report says the exam "grades an escalation rule that contradicts the shipped
answer key the course tells students to read." I checked both keys.

`corpus/release/ground_truth_exam.json` — the exam's own key:

| Email | Verdict | `escalate_expected` | `escalation_reasons` |
|---|---|---|---|
| 050-fenwright-deposit-change-confirmation | benign | **False** | [] |
| 053-vetchmoor-plan-documents | benign | **True** | `auth_failure_on_trusted_sender` |

`corpus/release/ground_truth_batch.json` — the key that ships to students in week 7:

| Email | Verdict | `escalate_expected` | `escalation_reasons` |
|---|---|---|---|
| 036-sandmarsh-positive-pay-exception | benign | True | `callback_verification` |
| 037-marlstone-april-invoice | benign | True | `auth_failure_on_trusted_sender` |
| 039-cfo-pay-marlstone-today | benign | True | `callback_verification` |
| 043-larkseal-bank-change-letter | benign | True | `callback_verification` |

**The two keys do not contradict each other.** They use one taxonomy consistently.
Exam item 24 keys 050 as no-escalate, and the exam key agrees. Exam item 23 keys 053
as escalate for `auth_failure_on_trusted_sender`, and the same reason escalates
batch email 037. The exam is internally consistent with the corpus, and the corpus
is internally consistent with itself.

**The defect is different and, I think, worse.** There are three escalation rule
sets in this course:

| Rule set | Reasons | Where a student meets it | Taught? |
|---|---|---|---|
| Week 6 code (`guarded_triage()`) | `token_cap`, `injection_detected`, `fact_contradiction`, `low_confidence` | written by the student, in the lab | **yes**, in full |
| The corpus taxonomy | `financial_or_endpoint_impact`, `executive_target`, `callback_verification`, `auth_failure_on_trusted_sender`, `injection_detected`, `partner_account_compromise`, `internal_account_compromise` | as raw JSON in `ground_truth_batch.json` | **no** |
| The exam | grades the corpus taxonomy | four items, positions 12, 20, 23, 26 | — |

Overlap between the taught set and the graded set: **one reason of eleven**
(`injection_detected`).

So the exam grades a rule set the course exposes only as data. A student who does
the reasonable thing — reads the shipped key, notices that four benign
money-movement emails escalate, and generalises "money movement escalates" — gets
item 26 right and item 20 wrong. The distinction the exam actually turns on is that
050 is a *notification of a completed change* while 043 is a *request to change*.
That distinction is real, it is defensible SOC practice, and **it is stated nowhere
in the course.**

Aggravating: item 24's third distractor feedback reads "Escalation is for a case the
facts leave open... Week 6 reading." That sentence appears in no week 6 page. The
nearest text is one subordinate clause in `w6-content-2.md` line 122 ("escalates
what it's unsure about"). The citation is to a rule the cited week does not state
and its code does not implement.

**Ruling.** Item 24 is *keyed correctly* and *unteachable as shipped*. On appeal I
would not defend it, because the student can show that the only escalation rule the
course ever states in words is week 6's four controls, and week 6's four controls do
not escalate email 050 either — which means the keyed answer and the taught rule
happen to agree, for reasons the course never gives. That is luck, not measurement.

Two fixes, either sufficient:

- One line in week 7's cell 12, which already names the disagreement and stops one
  sentence short: say that the corpus escalates on impact and the student's four
  controls escalate on uncertainty, and that a person applies both.
- Or drop the two contested items and keep the two (positions 12 and 28) that turn
  on rules the course states.

**I disagree with the e2e report's framing** and I think the difference matters for
the fix: this is not two contradictory keys, it is one taxonomy shipped as data and
graded as if it had been taught.

### 5.3 The week 8 overview's question count

Verified. `content/pages/w8-overview.md`:

```
line  8:  | Questions | 30, multiple choice |
line  9:  | Points | 30, across 40 questions |
line 35:  | Fifteen questions on the readings | 23 |
line 36:  | Fifteen questions on emails and your agent | 45 |
```

The exam file, its description, the assignment page and the syllabus all say 40.
The time table on lines 35-36 budgets 68 minutes for thirty questions, and the
90-minute total is built on that.

**Ruling: fix immediately, before any section runs.** A one-attempt, 20-percent,
no-time-limit summative whose orientation page understates its length by 25 percent
is a defect a student can name in an appeal, and one that disadvantages exactly the
students the course is written for — the ones who plan their sitting from the
overview table. Three edits: line 8, and the two rows in the time table.

### 5.4 "The questions ask what your own runs showed you"

Verified, and worse than reported: **the same page contradicts itself two lines
apart.**

```
w8-overview.md line 19: "The questions ask what your own runs showed you, so an
                         open file helps only if you did the work."
w8-overview.md line 21: "Each question hands you the facts and asks what your
                         agent should report."
```

Line 21 is true. Line 19 is false, and the same false claim appears a third time in
the exam's own description ("This exam is written so that having those open helps
you only if you did the work").

**Ruling.** The exam design is right and the description is wrong, in three places.
Handing over the facts and grading the judgment is the correct choice for an
open-book asynchronous final; it is more valid than testing record-keeping. Replace
all three sentences with the accurate one: *every question carries the facts it
needs; your files are allowed and you will not need them.* This also recovers the
12 minutes the overview's own table budgets for hunting through files.

---

## 6. Academic integrity and what the grade means

### 6.1 The exposure, component by component

| Component | Weight | Attempts | Key visible to student? | Effective variance |
|---|---|---|---|---|
| Self-checks | 8% | unlimited, highest counts | yes, in per-answer feedback after any attempt | **~zero** |
| Labs, "Submission completeness" criteria | 11.4% | 1 | n/a | near zero for anyone who submits |
| Labs, remaining criteria | 48.6% | 1 | week 7's answer key ships to students | real |
| Discussions | 12% | 1 | n/a | real but scored without a rubric |
| Final exam | 20% | 1 | after submission, immediately | real |

**The self-checks cannot discriminate at all, and the reason is not the option-1
defect.** Unlimited attempts plus highest-score-counts plus per-answer feedback that
names the correct option means every student who tries twice scores 84/84. That is
the stated design, and the file descriptions say so honestly ("Take it as many times
as you like. Your highest score is the one that counts."). The option-1 defect does
not change the score anyone gets. It destroys the only thing the instrument was for.

**This is the most important thing to say about the self-checks, and the e2e report
says it correctly.** They are a routing mechanism, not a measurement. The week 0
page tells a student scoring 6 to 8 to go back and work those sections. A student
who answers A seven times is told they are ready seven times, and never reads a
single one of the 129 wrong-answer feedback strings — which are, on my reading, the
best assessment writing in the course.

### 6.2 The exam's integrity posture

Verified from the exam settings and `make_quiz()`:

- One attempt, no time limit, open book, no proctoring, no lockdown.
- `show_correct_answers: true`, `one_time_results: false` — the full key and all
  160 feedback strings are visible to the student immediately on submit and
  reopenable thereafter.
- **A single fixed form.** No question groups, no item pool, no variants. Every
  student sees the same 40 items in the same order; only answer order shuffles.

In an 8-week asynchronous course, students submit the exam at different times over a
window. The first submitter holds the complete key. There is no technical control
against sharing it and the course states, correctly, that nothing locks.

**Mitigations that are real and that I credit:**

- Eleven of the emails are new and reserved (`instructor/exam-emails/`), so no
  student has run an agent on one.
- Roughly 25 of 40 items hand over a new email's facts and ask for a judgment.
  Those cannot be answered by recognising a phrase from a page — which is exactly
  the failure mode of the self-checks.
- The corpus answer keys for the exam and for weeks 1-6 are excluded from Canvas by
  an explicit allowlist in `course.yaml`, with the reasoning written out.

**The residual risk is a shared answer sheet, and a fixed form has no defence
against it.** The 8 percent self-check group and the 11.4 percent compliance floor
mean a student with a shared key and no learning lands around 19 + 20 = 39 percent
before doing a single lab. Add lab submission and discussion participation and they
pass.

### 6.3 Is the final grade defensible?

**No, not as it stands, and the reasons are narrow and fixable.**

I would defend the following without hesitation:

- The final exam as an instrument, once the ten added items are repositioned. It is
  well constructed, well cited, genuinely mixed, and its feedback does real teaching.
- The seven labs' *design*: three artifacts, criteria that name countable
  conditions, graded from what arrives rather than by running a student's notebook.
- The week 7 CLO6 criterion, which is the best outcome alignment in the course.
- The exclusion of the corpus answer keys from Canvas, and the reasoning written in
  the allowlist.

I would not defend the following:

1. **Three lab criteria totalling 164 points (23 percent of all lab points) whose
   top band a student cannot reach or a grader cannot verify.** Two of the three
   carry a CLO. This is the disqualifying item.
2. **Six CLO results, all n = 1, two of which are structurally capped below their
   own top rating.** A program outcome report built on this would misreport
   CLO4 and CLO5 for every student.
3. **12 percent of the grade scored from a prose table with no rubric, no levels
   and no partial credit.**
4. **Two exam items grading material the course does not teach** (positions 15 and
   20), worth 1.5 of 30 exam points — small, and the kind of thing that decides an
   appeal.

### 6.4 What I would tell the program chair

Six sentences.

The instruments in this course are better written than most, and the grade they
produce is not currently defensible, for reasons that are structural rather than
sloppy. Twenty-three percent of the lab points sit behind bands that the course's
own exported files cannot evidence, and two of those bands are the sole mastery
evidence for two of your six outcomes — so the outcome report will show a cohort-wide
CLO5 shortfall caused by the instrument, not the students. Eight percent of the
grade, the weekly self-checks, measures nothing at all and was never meant to;
that is fine, but say so in the syllabus rather than letting it read as assessment.
Twelve percent, the discussions, is scored without a rubric object in Canvas, which
is your weakest position at a hearing. The final exam is the only instrument here
that measures anything, it is well built, and two of its forty items test material
the course never presents. Fix the three lab criteria before the course runs; nothing
else on this list changes a single letter grade.

---

## 7. What is well built

Specific, and each one verified.

**The answer feedback is the best assessment writing I have read in a
community-college technical course.** Every option in every instrument carries its
own explanation, right and wrong alike — 129 wrong-answer strings in the
self-checks and 120 in the exam. The exam file header states the rule and the
reason: "This course is fully asynchronous, and nobody walks a student through a
missed question. Once the exam closes, the feedback a student reads on a wrong
option is the only teaching that item will ever do." The constraints it sets on
itself — name the deciding fact, quote the option's words rather than a letter
because answers shuffle, forty words or fewer, point back to the week, answer no
other item — are the right constraints and they are met.

**The rubric levels name countable conditions rather than quality adjectives.**
Nineteen of twenty-five criteria do this. "One fact group is missing from every
block, or one email's block is missing a value the other five carry" is a rule two
graders will apply the same way. This is the single hardest thing to get right in
rubric design and this course mostly has it.

**The instruments document their own failure modes.** Three examples, all verified
in file headers: the Canvas limit of one outcome alignment per rubric, measured
against the live instance and recorded with the date; the fact that Canvas accepts
`answer_comments`, returns HTTP 200 and stores nothing, so 120 feedback strings
would vanish silently under the wrong key name; and the rejection of `highest` as
an outcome calculation method with the reason written out ("Highest score would let
a strong week 4 mask a weak week 5"). I have not seen a course carry that kind of
record before.

**`build_course.py` refuses to build a rubric whose criteria do not sum to the
assignment's points, and says so.** `raise CanvasError(f"rubric {ref}: criteria sum
to {total}, assignment is {assignment['points_possible']}. Fix the rubric, not this
check.")` That last sentence is the right instinct.

**The corpus answer-key exclusion is an allowlist, not a denylist, and the reason is
written down:** "one wrong path hands every student the answer key." Six specific
files are named as never shippable, and `ground_truth_batch.json` is named as an
exception with its justification.

**The exam solved the open-book problem instead of pretending it away.** Eleven
reserved emails, 25 of 40 items handing over facts and grading judgment, and a
stated design principle that a recall-only item measures little when the book is
open. The six shared reference blocks are a genuine improvement on reprinting one
message three times, and the counts are right.

**Week 7's CLO6 criterion is the best outcome alignment in the course.** It requires
the screenshot and the file to report the *same* accuracy number, the two error
types counted separately, escalation agreement on its own line, and a written
recommendation that cites the student's own figure. That is measurement literacy
assessed as measurement literacy.

**Week 3's fact-extraction criterion discriminates on the right axis.** It grades
whether every value agrees with the email it came from, not whether the model
answered correctly. The week 3 discussion says the same thing out loud: "No credit
depends on which way a verdict moved." Grading the student's choices rather than the
model's output is the correct decision for a course built on a stochastic system,
and it is applied consistently.

**The exam arithmetic is exact.** Forty items at 0.75 = 30.00. The rescale from
thirty one-point items moved no grading weight, and the header says so.

---

## 8. Prioritised worklist

Ordered by grade defensibility, not by effort.

| # | Action | Points at stake | Effort |
|---|---|---|---|
| 1 | Add `confidence_without_guardrails` and `confidence_with_guardrails` to the row in `w6-lab.ipynb` cell 14, and carry the undefended token count. | 72-pt criterion, CLO4 mastery for every student | one line |
| 2 | Rewrite the w7 "Triage note" top and Meets bands to grade the student's *format and indicator sourcing* only, and move the three prose properties into an ungraded observation the student reports on. | 36-pt criterion, CLO5 mastery for every student | rubric edit |
| 3 | Add per-email correctness to `week7_triage_report.txt` so the 56-pt criterion is verifiable in both directions. | 56-pt criterion, CLO6 | one loop |
| 4 | Redistribute the authored answer positions of `exam-q31`-`q40`, which are all at position 1, and normalise the three off-taxonomy `level:` labels. | 10 items, all CLO3/5/6 evidence | 15 minutes |
| 5 | `shuffle_answers: true` on the seven self-checks, **and** lengthen two distractors per item in weeks 5 and 6. | routing validity of 43 items | half a day |
| 6 | Fix `w8-overview.md` line 8 and the two time-table rows; replace the "your own runs" sentence in all three places. | exam fairness | three edits |
| 7 | One line in `w7-lab.ipynb` cell 12 naming which escalation rule applies where. | exam items at positions 20 and 26 | one line |
| 8 | Add a `temperror` row to week 3's "what a passed check really means," or drop exam item 19. | 0.75 exam points | one row |
| 9 | Give the discussions a Canvas rubric object with levels, rather than a prose table. | 12% of the grade | one afternoon |
| 10 | Fix the week 1 rubric floor from 6 to 0 on all four criteria, matching the other six labs and the mastery scale. | gradebook consistency | four edits |
| 11 | Add `"indicators"` to the w3 export row and widen `one_line()` past 80 characters in w5. | 9 discussion points | two lines |

Items 1 through 3 are the ones I would require before the course runs. Everything
else can follow.

---

## Appendix: what was verified and how

| Claim | Source |
|---|---|
| Answer positions, lengths, option counts, outcome tags, level and difficulty tags | parsed from the ten quiz YAML files |
| Rubric criteria, levels, points, outcome links, floors | parsed from the seven rubric YAML files |
| Outcomes reach Canvas only via rubric criteria | `canvas/build_course.py` lines 505-508, and the absence of any outcome call in `make_quiz()` |
| Discussions carry no rubric | `canvas/build_course.py`, `make_discussion()` |
| `compare_guarded()` writes no confidence and no undefended token count | `lab/notebooks/w6-lab.ipynb` cell 14 |
| `compare_runs()` **does** write both confidences | `lab/notebooks/w3-lab.ipynb` cell 12 |
| The w5 export **does** carry both token totals | `lab/notebooks/w5-lab.ipynb` cell 16 |
| `week7_triage_report.txt` holds no per-email correctness | `lab/notebooks/w7-lab.ipynb` cell 15 |
| `temperror` and `softfail` reachability | grep across `content/`, `lab/`, `corpus/emails/`, checked against the `student_files` allowlist in `course.yaml` |
| Escalation keys | `corpus/release/ground_truth_exam.json`, `corpus/release/ground_truth_batch.json`, `lab/notebooks/w6-lab.ipynb` `guarded_triage()` |
| Week 8 overview contradiction | `content/pages/w8-overview.md` lines 8, 9, 19, 21, 35, 36 |
| Grade weights | `content/course.yaml` lines 51-55 |

Not verifiable, and stated as such throughout: item difficulty (p-values), item
discrimination (point-biserial), internal consistency (KR-20), and inter-rater
agreement on any rubric criterion. **No instrument in this course has response data
behind it.** Every difficulty judgment in section 2 is authored, not measured.
