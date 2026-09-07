# Alignment matrix and Canvas Outcomes plan

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 1.** Prepared 2026-09-03.
**Audience:** the program manager. No part of this document assumes you are building the course.

This file holds two deliverables. Part 1 is the alignment matrix: the six course
learning objectives, the national framework tasks each one maps to, the week that
teaches it, and the graded work that proves it. Part 2 is the Canvas Outcomes plan:
what gets created in Canvas, on what scale, and how scores reach the program's reports.

## 1. How to read this document

Nine terms carry most of the weight here.

- A **course learning objective (CLO)** is a skill the course promises a student will
  have at the end. This course has six. They are fixed by the build prompt.
- A **Bloom level** names how demanding a thinking task is. The levels used here run
  Apply, Analyze, Evaluate, Create, from least to most demanding. The level decides
  what kind of assessment can prove the objective.
- The **NICE Framework** is a national list of cybersecurity work roles. NIST publishes
  it. Each role carries a list of tasks and skills.
- A **work role** is one job description in that list. This course aligns to
  PD-WRL-001, Defensive Cybersecurity.
- A **Canvas Outcome** is a record in Canvas that stores how each student did on one
  objective. The program pulls its outcome reports from these records.
- A **rubric criterion** is one scored line on a grading rubric. Linking a criterion to
  an Outcome is what moves a score into the outcome report.
- A **mastery scale** is the set of rating levels an Outcome is scored on. It also
  names the level that counts as mastery.
- The **roll-up** is the single number the program's report shows for one objective,
  gathered from every rubric criterion linked to it.
- **Classic Quizzes** is one of the two quiz engines Canvas offers. A Classic Quiz has
  no rubric, so it cannot post a score to an Outcome.

## 2. Framework citation and verification status

The matrix cites this source:

> NICE Framework Components v2.2.0 (NIST, April 28, 2026), implementing NIST SP 800-181
> Rev. 1 (November 2020); work role PD-WRL-001 Defensive Cybersecurity, Protection and
> Defense; retrieved 2026-09-03 from niccs.cisa.gov and nist.gov.

**Date caveat.** The NIST Current Versions heading reads "2.2.0 (April 28, 2025)". The
change log dates 2.2.0 to 28 April 2026 and 2.1.0 to 3 December 2025, and the release
note URL sits under /2026/04/. The heading year is a typo. This document cites the
change log.

**Verification result.** Every id in the matrix was checked on 2026-09-03. All 21 exist
in v2.2.0 and all 21 are linked to PD-WRL-001. None is missing. None sits outside the
role. No id was substituted for another. The full record, including per-id source URLs
and the disagreements that were settled, is at
`builder/docs/nice-verification.md`.

Each id has its own page on niccs.cisa.gov. Tasks use the path
`/tools/nice-framework/task/<ID>` and skills use `/tools/nice-framework/skill/<ID>`.
Statements in section 4 are quoted from those pages and from the components JSON, never
from a role-page summary, because the summaries were seen to swap and truncate
statements.

## 3. The alignment matrix

Primary evidence placement is fixed by the build prompt, quoted here as the contract the
matrix implements:

>     CLO1 -> week 3 lab
>     CLO2 -> week 2 lab, reinforced on the final
>     CLO3 -> week 5 lab (primary), week 4 lab (supporting)
>     CLO4 -> week 6 lab
>     CLO5 -> week 7 triage notes
>     CLO6 -> week 7 evaluation report

| CLO ID | Objective text | Bloom level | Canvas Outcome name | Primary NICE task | Supporting NICE tasks | Weeks taught | Primary assessment artifact | Rubric criterion that measures it |
|---|---|---|---|---|---|---|---|---|
| CLO1 | Extract the header, authentication, sender, and URL facts an AI model needs to judge a suspicious email. | Apply | CLO1: Extract email triage facts | T1085, Identify potential threats to network resources | T1084, Identify anomalous network activity; S0600, Skill in collecting relevant data from a variety of sources; S0712, Skill in evaluating data source quality | 3 (primary); reinforced in 4 and 6 | Week 3 lab: the exported fact set for one email, with the grounded and ungrounded verdicts for the same email side by side | Week 3 rubric, criterion 2: Fact extraction (primary), and the only Outcome-linked criterion in that rubric. See the amendment under section 11 |
| CLO2 | Classify a suspicious email as malicious or benign using an AI model, then validate the model's output before trusting it. | Analyze | CLO2: Classify and validate an AI verdict | T1348, Distinguish between benign and potentially malicious cybersecurity attacks and intrusions | T1112, Validate network alerts; T1387, Validate intrusion detection system alerts | 1 (supporting); 2 (primary); reinforced in 6; recognition items on the week 8 final | Week 2 lab: the exported classification in strict JSON, with the schema check result and the record of any retry | Week 2 rubric, criterion 2: Output validation; week 1 rubric, criteria 2 to 4, supporting |
| CLO3 | Build an AI agent that selects and runs triage tools in a bounded loop to reach a verdict. | Create | CLO3: Build a bounded triage agent | T0020, Develop content for cyber defense tools | T1299, Determine causes of network alerts | 5 (primary); 4 (supporting) | Week 5 lab: the exported run record for one email, showing each tool chosen, the steps used against the cap of 4, and the stop reason | Week 5 rubric, criterion 2: Bounded tool loop (primary). Week 5 rubric, criterion 3: Reading your own trace, and criterion 4: Cost of an uncapped run (both supporting). Week 4 rubric, criterion 2: Tool call handled end to end, and criterion 3: Reading your own results (both supporting) |
| CLO4 | Judge whether an agent's guardrails reduce prompt injection risk to an acceptable level. | Evaluate | CLO4: Judge guardrails against prompt injection | T1177, Determine if security control technologies reduce identified risk to acceptable levels | T1176, Determine if cybersecurity-enabled products reduce identified risk to acceptable levels; S0509, Skill in evaluating security products; S0667, Skill in assessing security controls | 6 (primary); recognition items on the week 8 final | Week 6 lab: the exported results for the injected email and its word-for-word control, before and after the guardrails, with the student's written judgment | Week 6 rubric, criterion 2: Guardrail judgment |
| CLO5 | Document a triage decision, its indicators, and its recommended action so another analyst can act on it. | Apply | CLO5: Document a triage decision | T1241, Document cybersecurity incidents | T1349, Communicate cybersecurity attacks and intrusions alerts; T1242, Escalate incidents that may cause ongoing and immediate impact to the environment; T1428, Notify designated managers, cyber incident responders, and cybersecurity service provider team members of suspected cybersecurity incidents | 7 (primary); the escalation rule it records is set in 6 | Week 7 lab: the exported triage notes in the fixed format (verdict, confidence, indicators, recommended action, escalate yes or no, plus the two-sentence plain-language summary) | Week 7 rubric, criterion 2: Triage note |
| CLO6 | Measure agent triage accuracy across a batch of emails and recommend where human review stays required. | Evaluate | CLO6: Measure triage accuracy | T0164, Perform cyber defense trend analysis and reporting | T1020, Determine the operational and safety impacts of cybersecurity lapses; T1290, Communicate daily network event and activity reports; S0892, Skill in performing trend analysis | 7 (primary) | Week 7 lab: the exported batch evaluation report over the 20-email batch, with accuracy and with false positives and false negatives reported separately | Week 7 rubric, criterion 3: Accuracy and human review |

Framework citation for the matrix: NICE Framework Components v2.2.0 (NIST, April 28,
2026), implementing NIST SP 800-181 Rev. 1 (November 2020); work role PD-WRL-001
Defensive Cybersecurity, Protection and Defense; retrieved 2026-09-03.

Four notes on reading the table.

1. Ids beginning with T are tasks. Ids beginning with S are skills, not tasks. The build
   prompt lists both under "supporting", so both appear in the supporting column.
2. Every lab submits the same three items: a screenshot of the working output, one file
   the notebook exports with a single pre-written cell, and a written answer of 3 to 5
   sentences. The artifact column names the exported file and the answer, because those
   two carry the evidence.
3. Week 7 has one rubric that carries two objectives. CLO5 takes criterion 2 and CLO6
   takes criterion 3.
4. Criterion 1 in every weekly rubric is submission completeness. It is a non-CLO
   expectation and carries no Outcome link. Section 10 states that rule.

## 4. The NICE statements behind the matrix

Every statement below is the exact wording from the verified source.

| CLO | ID | Type | Role in the mapping | Statement |
|---|---|---|---|---|
| CLO1 | T1085 | task | primary | Identify potential threats to network resources |
| CLO1 | T1084 | task | supporting | Identify anomalous network activity |
| CLO1 | S0600 | skill | supporting | Skill in collecting relevant data from a variety of sources |
| CLO1 | S0712 | skill | supporting | Skill in evaluating data source quality |
| CLO2 | T1348 | task | primary | Distinguish between benign and potentially malicious cybersecurity attacks and intrusions |
| CLO2 | T1112 | task | supporting | Validate network alerts |
| CLO2 | T1387 | task | supporting | Validate intrusion detection system alerts |
| CLO3 | T0020 | task | primary | Develop content for cyber defense tools |
| CLO3 | T1299 | task | supporting | Determine causes of network alerts |
| CLO4 | T1177 | task | primary | Determine if security control technologies reduce identified risk to acceptable levels |
| CLO4 | T1176 | task | supporting | Determine if cybersecurity-enabled products reduce identified risk to acceptable levels |
| CLO4 | S0509 | skill | supporting | Skill in evaluating security products |
| CLO4 | S0667 | skill | supporting | Skill in assessing security controls |
| CLO5 | T1241 | task | primary | Document cybersecurity incidents |
| CLO5 | T1349 | task | supporting | Communicate cybersecurity attacks and intrusions alerts |
| CLO5 | T1242 | task | supporting | Escalate incidents that may cause ongoing and immediate impact to the environment |
| CLO5 | T1428 | task | supporting | Notify designated managers, cyber incident responders, and cybersecurity service provider team members of suspected cybersecurity incidents |
| CLO6 | T0164 | task | primary | Perform cyber defense trend analysis and reporting |
| CLO6 | T1020 | task | supporting | Determine the operational and safety impacts of cybersecurity lapses |
| CLO6 | T1290 | task | supporting | Communicate daily network event and activity reports |
| CLO6 | S0892 | skill | supporting | Skill in performing trend analysis |

Two ids also appear under other work roles. T1387 is also under PD-WRL-002 and T1299 is
also under PD-WRL-003. Both are still inside PD-WRL-001, so both are valid here.

## 5. Mapping rationale

### 5.1 The two mapping notes from the build prompt

Both are reproduced word for word, as the build prompt requires.

> Several PD-WRL-001 tasks are worded around network activity. Phishing triage is a
> user-layer activity. T1348 and T0020 are the layer-neutral anchors and carry the
> weight; T1112 and T1084 are supporting only.

> No PD-WRL-001 task references AI, agents, or prompt injection, because the framework
> predates them. CLO4 therefore maps to the control evaluation tasks (T1176, T1177),
> since students are assessing whether a control reduces risk. State this openly.

In plain terms: the framework was written for a job that watches networks. This course
teaches a job that reads mail sent to people. The two overlap, and the wording of some
tasks shows the gap. The framework also predates agentic AI, so no task names it.
Neither gap is hidden by a substitution.

### 5.2 Two observations the verification record raises

The NICE verification record raises two points that the build prompt's notes do not
cover. Both are stated here rather than resolved, and no id is changed.

**Observation 1. The CLO1 primary is itself network-worded.** T1085 reads "Identify
potential threats to network resources". That is network wording. The build prompt's
note names only T1084 and T1112 as the network-worded ids, so it understates the
problem. T1085 stays as the CLO1 primary because the build prompt sets it and because
the evidence step of phishing triage is a threat identification step. A reviewer should
know that the CLO1 primary shares the same layer mismatch as the supporting ids.

A second point sits alongside it. T1348 says "attacks and intrusions". It is not
literally layer-neutral either, although it is the closest fit in the role. The
build prompt's phrase "layer-neutral anchors" is a relative claim, not an exact one.

**Observation 2. T1290 is a weak supporting fit for CLO6.** T1290 reads "Communicate
daily network event and activity reports". The week 7 evaluation report is written once,
not daily, and it reports agent accuracy rather than network events. Keeping T1290 is a
design choice, not a match. It stays because the build prompt lists it and because no id
may be substituted. The CLO6 mapping does not depend on it: T0164 and S0892 carry the
objective.

**No substitutions.** Where a fit is weak, this document says so and keeps the id. That
is the rule the build prompt sets, and it is the rule followed here.

## 6. What the final exam does and does not measure

The week 8 final exam is selected response. Every item is multiple choice. Selected
response can show that a student recognizes a correct read. It cannot show that a
student built, judged, or documented anything.

So the final exam is supporting evidence only for any CLO above the Analyze level. It is
never sole evidence for any CLO. Primary evidence for every CLO lives in a lab. The
matrix places it there.

The exam's primary job is the four breadth topics, B1 through B4. Roughly half its items
sit on those topics, which selected response suits well. The other half are scenario
reads drawn from the course's own agent and corpus. Those scenario items add supporting
evidence for CLO1, CLO2, and CLO4 at the recognition and analysis level.

The exam does not claim to measure a CLO on its own, and it produces no Canvas Outcome
result. Section 10 explains that choice.

---

## Part 2. The Canvas Outcomes plan, sections 7 to 15

## 7. Finding: no account-level Outcomes exist on this instance

The build prompt requires a check for matching account-level Outcomes before any
course-level Outcome is created, and a report of which path was taken.

**The check.** On 2026-09-03 the `outcome_groups` and `outcome_group_links` endpoints
were called on both accounts on the instance canvas.bashtion.dev, including the root
account, id 1. Both accounts returned zero outcome groups and zero outcome group links.

**The finding.** The instance has no Canvas Outcomes at either account. There are no
account-level Outcomes for this program to link to.

**The path taken.** All six Outcomes are created at course level, in the new course,
Canvas course id 6. This is the second of the two paths the build prompt names. The
first path, linking to existing account-level Outcomes, is not available on this
instance.

One related point belongs in the record. The institutional template ships five
critical-thinking Outcomes that were copied from an account on a different Canvas
instance. Those account-level Outcomes do not exist here, and none of the five
corresponds to a course objective. Whether the program wants them recreated is
unresolved. It is listed as conflict 14 in `builder/docs/nlc-template-conformance.md`.

## 8. The mastery scale

All six Outcomes use one scale. Four rating levels, 4 points possible, mastery at 3.

| Rating label | Points | What it means |
|---|---|---|
| Exceeds standard | 4 | Does the task correctly. Explains the judgment using the evidence. |
| Meets standard | 3 | Does the task correctly. This is the mastery level. |
| Approaching standard | 2 | Does part of the task, or does it with errors. |
| No evidence | 0 | Nothing submitted that shows the skill. |

**Why this scale.** Four levels match the three to four rubric levels the build prompt
allows, so a rubric rating maps straight onto an outcome rating with no translation
step. Mastery sits at 3 because correct triage work with sound evidence is the
entry-level job these students are hired to do, and level 4 is held for work that also
explains the judgment.

The gap between 2 and 0 is deliberate. A student who attempts the task and gets part of
it right scores 2. Zero means the submitted work shows nothing about the skill.

## 9. Calculation method

**Method: most recent score.** In the Canvas API this is `calculation_method` set to
`latest`.

**Why.** For every CLO, the primary artifact is also the last artifact scored, so the
recorded result is always the primary evidence. CLO3 is the case that proves it: the
week 4 tool criterion is supporting, the week 5 loop criterion is primary, and week 5
comes last.

The supporting result does not vanish. It stays visible in the Canvas outcome detail
view, where an instructor or reviewer can see both scores for a student. Only the
reported roll-up uses the most recent one.

CLO3 has one open build detail. The week 5 rubric posts three results to that
Outcome at once, one primary and two supporting. Confirm which one the most recent
score method keeps. If the order is not fixed, the build reports criterion 2 as the
result of record and leaves the other two in the outcome detail view. Week 5 spec,
section 9, states the same fallback.

Two other methods were considered and rejected. Highest score would let a strong week 4
mask a weak week 5, which would overstate CLO3 mastery. A decaying average would blend a
supporting result into a primary one, which is exactly what the build prompt's evidence
rules forbid.

## 10. The six Canvas Outcomes

Each Outcome's description is the CLO text, word for word. Every Outcome uses the scale
in section 8 and the method in section 9.

| Outcome title | Description (the CLO text, verbatim) |
|---|---|
| CLO1: Extract email triage facts | Extract the header, authentication, sender, and URL facts an AI model needs to judge a suspicious email. |
| CLO2: Classify and validate an AI verdict | Classify a suspicious email as malicious or benign using an AI model, then validate the model's output before trusting it. |
| CLO3: Build a bounded triage agent | Build an AI agent that selects and runs triage tools in a bounded loop to reach a verdict. |
| CLO4: Judge guardrails against prompt injection | Judge whether an agent's guardrails reduce prompt injection risk to an acceptable level. |
| CLO5: Document a triage decision | Document a triage decision, its indicators, and its recommended action so another analyst can act on it. |
| CLO6: Measure triage accuracy | Measure agent triage accuracy across a batch of emails and recommend where human review stays required. |

Settings applied to all six:

| Field | Value |
|---|---|
| Location | Course 6, in one outcome group named "ITSY 1377 Course Learning Objectives" under the course root outcome group |
| `calculation_method` | `latest` |
| `mastery_points` | 3 |
| `points_possible` | 4 |
| Ratings | 4 Exceeds standard, 3 Meets standard, 2 Approaching standard, 0 No evidence |

## 11. The rule the build follows for rubric links

The rule has three parts.

1. Every rubric criterion that measures a CLO links to that CLO's Canvas Outcome.
2. A rubric criterion with no linked Outcome is an error.
3. The one exception is a criterion that measures a non-CLO expectation, such as
   submission completeness. That criterion carries no Outcome link and must be named in
   the weekly spec as a non-CLO expectation.
4. A criterion that scores a student's use of their own results stays inside the
   Outcome-linked criterion. It is never a separate line beside it.

Clause 4 settles a question the weekly specs raised twice. Judging with your own
numbers is part of the CLO4 performance. Measuring with your own numbers is part of
the CLO6 performance. Neither is a separate expectation, so neither gets its own
unlinked criterion.

The academic integrity purpose survives the merge. A criterion that requires the
student's own accuracy figure and their own wrong email still fails a submission that
cites neither. It just does that inside the Outcome-linked line rather than beside it.

Two rubrics were brought into line with clause 4. Week 6 already folded its evidence
check into criterion 2, so it changes nothing. Week 7 dropped its separate "Own results
used" criterion and moved that requirement, and its points, into criterion 3.

These are the criteria that carry CLO evidence. They are the links the build creates.

| Rubric criterion | Linked Outcome | Role |
|---|---|---|
| Week 1 rubric, criterion 2: The call works | CLO2: Classify and validate an AI verdict | supporting |
| Week 1 rubric, criterion 3: Variation reported | CLO2: Classify and validate an AI verdict | supporting |
| Week 1 rubric, criterion 4: First judgment | CLO2: Classify and validate an AI verdict | supporting |
| Week 2 rubric, criterion 2: Output validation | CLO2: Classify and validate an AI verdict | primary |
| Week 3 rubric, criterion 2: Fact extraction | CLO1: Extract email triage facts | primary |
| Week 4 rubric, criterion 2: Tool call handled end to end | CLO3: Build a bounded triage agent | supporting |
| Week 4 rubric, criterion 3: Reading your own results | CLO3: Build a bounded triage agent | supporting |
| Week 5 rubric, criterion 2: Bounded tool loop | CLO3: Build a bounded triage agent | primary |
| Week 5 rubric, criterion 3: Reading your own trace | CLO3: Build a bounded triage agent | supporting |
| Week 5 rubric, criterion 4: Cost of an uncapped run | CLO3: Build a bounded triage agent | supporting |
| Week 6 rubric, criterion 2: Guardrail judgment | CLO4: Judge guardrails against prompt injection | primary |
| Week 7 rubric, criterion 2: Triage note | CLO5: Document a triage decision | primary |
| Week 7 rubric, criterion 3: Accuracy and human review | CLO6: Measure triage accuracy | primary |

**Amendment, 4 September 2026: week 3 criteria 3 and 4.** This table listed week 3
criteria 3 and 4 as supporting links to CLO1. It no longer does. The Canvas constraint
recorded in the last section of this document allows one Outcome to align to one
criterion per rubric, and a rubric that aligns CLO1 three times creates no rubric at
all. Criterion 2, Fact extraction, carries the link, because it is the criterion that
reads the extracted facts themselves, which is what CLO1 names. Criteria 3 and 4 are
written as week expectations under clause 3 above: "you reported what you saw" is a
non-CLO expectation that section already names. The built rubric,
`content/rubrics/w3-lab.yaml`, states the same thing on both criteria.

**What it costs, stated plainly.** CLO1's outcome data comes from week 3 criterion 2
alone. No other week links to CLO1, so that one criterion is the whole outcome record
for it. Objectives 3.2 and 3.3 are still graded, at 25 points each, and still reported
to the student; they no longer reach the outcome roll-up. The week 3 spec is amended
to match.

Each weekly rubric holds 3 to 5 criteria. Criterion 1 is always submission completeness:
the screenshot, the exported file, and the written answer are all present and readable.
It carries no Outcome link and is declared a non-CLO expectation. The remaining criteria
are set in the per-week specs, and each one must either link to an Outcome or be
declared a non-CLO expectation there.

Week 1 is the one week whose Outcome links are all supporting. Its three CLO-bearing
criteria measure acts named in the week 1 objectives, and all three of those objectives
parent to CLO2, so leaving the criteria unlinked would contradict the week 1 spec. Only
criterion 1, submission completeness, is a non-CLO expectation there.

Because the Outcomes report the most recent score, the week 2 result replaces the week 1
result for CLO2. Nothing from week 1 survives in the reported number. The week 1 score
exists to give the instructor an early reading, not to feed the roll-up. The week 1 spec
states the same thing in its section 9.

Discussion rubrics carry no Outcome links. They measure participation and whether the
student used their own agent's results. Both are non-CLO expectations, declared as such.

The final exam is a Classic Quiz, not a rubric-graded assignment, so it creates no
outcome results. Its supporting role for CLO1, CLO2, and CLO4 is reported in the week 8
exam blueprint instead. This keeps a selected-response score out of the outcome roll-up,
which is what the build prompt's evidence rule requires.

## 12. What gets no Outcome

Breadth topics B1 through B4 get no Canvas Outcome. They are not course objectives, they
carry no CLO number, and they have no lab.

| Breadth topic | Where it is carried |
|---|---|
| B1, AI and agentic workflows in IT and security operations broadly | Week 1 survey reading, week 1 discussion, week 8 final |
| B2, the range of AI-assisted security use cases | Week 7 survey reading, week 7 discussion, week 8 final |
| B3, security operations components | Week 1 survey reading, week 1 self-check, week 8 final |
| B4, the wider AI risk set | Week 6 reading, week 8 final |

Week 0 and the weekly scripting sidebars are ungraded. They support the objectives and
get no mapping and no Outcome.

## 13. One template interaction the builder must handle

The template hides the Outcomes tab and the Rubrics tab from course navigation. Hiding a
tab does not turn the feature off, and outcome results still record. Staff who need to
read outcome data reach it through the API, or by unhiding the tab for teachers.

This is conflict 17 in the template conformance document. It is raised here because the
build prompt depends on the program pulling outcome data from Canvas.

## 14. Assumptions

1. The Outcomes check on the instance is reported as it was run on 2026-09-03. If a
   program account elsewhere in the district holds CLO-shaped Outcomes that this
   instance cannot see, the course-level path would need revisiting.
2. Each weekly module has one rubric. Week 7 therefore carries CLO5 and CLO6 on one
   rubric, as criteria 2 and 3.
3. Criterion 1 of every weekly rubric is submission completeness. This fixes the
   criterion numbering used throughout this document.
4. Every weekly lab is worth 100 points, so the seven labs carry equal weight inside
   the 60 percent Labs group. Every Outcome-linked criterion names four level values,
   its top level equals its points, and the four map one to one onto the mastery
   ratings, so a grader picks once and both scales follow. Where the arithmetic allows
   it the criterion is an exact multiple of 4 and the mapping is exact; where it does
   not, the middle levels are the mastery ratings scaled and rounded to whole points,
   and the weekly spec prints them. The grade distribution and token totals document
   holds the whole table.
5. The final exam creates no Canvas Outcome results. Its supporting role is documented
   in the exam blueprint.
6. The artifact descriptions in the matrix name what each exported file must contain.
   The file names themselves are set in the per-week specs, which are blueprint item 3.
7. Supporting NICE ids that are skills rather than tasks are listed in the supporting
   column, because the build prompt groups them there.

## 15. Open questions for the program manager

1. **Calculation method.** Most recent score is proposed here. If the program's own
   reporting expects highest score, or a decaying average, say so before Phase 2. It is
   a one-field change per Outcome while the course is still unbuilt.
2. **Mastery threshold.** Mastery is set at 3 of 4. Some programs report at 2 of 4 to
   raise pass rates. Confirm 3 is what the program wants reported.
3. **The template's five critical-thinking Outcomes.** They do not exist on this
   instance and none maps to a CLO. Should they be recreated at course level alongside
   the six, left out, or raised with the district for account-level creation?
4. **Account-level Outcomes for the program.** All six live at course level today. If
   the program later wants them shared across courses, they should be created at account
   level and imported. That is a district Canvas admin action, not a course action.
5. **T1290 on CLO6.** It is kept because the build prompt lists it and no id may be
   substituted. Confirm that a weak supporting fit is acceptable in the matrix the
   program submits, or ask for it to be dropped from the supporting list.
6. **Resubmission policy.** Most recent score means a regraded resubmission replaces the
   earlier outcome result. The late work and resubmission policy is still unset, and it
   changes what the outcome report shows.

## Canvas constraint found while building, and what it changes

**One Outcome may align to at most one criterion in a rubric.** Canvas refuses a
rubric that aligns the same Outcome twice, and the refusal is silent: the API
answers HTTP 200 and creates nothing at all. Measured against the live instance
on 4 September 2026, one link succeeds and two or more produce no rubric.

This was found because the week 1 lab appeared in Canvas with no rubric while
the build reported success. The builder now verifies that every lab has a rubric,
that its criteria sum to the assignment's points, and that the number of
outcome-linked criteria matches the source file, so the same silence cannot pass
again.

What it changes for the remaining weeks. Each week's rubric links each Outcome
once. Where several criteria measure the same Outcome, the one that measures it
most directly carries the link. The others are written as week expectations
rather than course outcomes.

Week 1 is the worked example. Three criteria originally linked to CLO2. Now the
criterion about validating the model's output before trusting it carries the
link, because that is what CLO2 says.

The build prompt's rule still holds. A criterion with no linked Outcome is an
error unless it measures a non-CLO expectation, and "the code ran" and "you
reported what you saw" are non-CLO expectations.
