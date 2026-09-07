# Week 6 spec: Guardrails and human in the loop

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 6 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.
**Primary evidence for:** CLO4, Judge whether an agent's guardrails reduce prompt injection risk to an acceptable level.

Four terms carry this page.

- A **token** is a chunk of text, roughly four characters. It is the unit the
  model is billed and capped in.
- **Prompt injection** is attacker-written text that a model reads as an
  instruction instead of as evidence.
- A **guardrail** is a control placed around the model. It stops a bad answer
  from becoming a bad action.
- **Escalation** is handing a case to a human analyst instead of closing it
  automatically.

## 1. The capability added, and why it is exactly one

Week 6 adds one thing. The agent stops trusting the text it reads and stops
trusting the answer it produces.

Four mechanisms deliver that. The prompt fences the email body between two
markers and names it evidence. The student's code checks the model's answer
against the facts already extracted. Any answer below a confidence floor goes to
a human. Any triage that spends more than a set number of tokens stops and goes
to a human.

These are one capability, not four, for three reasons.

They all sit on one seam. Each acts between the model's answer and the analyst's
action. None adds a new source of information, a new tool, a new loop or a new
output format.

They fail as a set. Fencing the body alone loses to the payload hidden in the
HTML part. The fact check alone loses to the payload in the subject line. Taught
one at a time they read as tricks. Taught together they read as one control on
one seam, which is what the course objective asks students to judge.

Nothing earlier changes. The week 5 loop runs unmodified, because its function
already takes two things as arguments. One is the prompt. The other is an
optional guard that says whether the run may take another step.

The week 6 prompt is passed in. So is `over_token_cap`, which is how the per-run
token cap gets checked between steps. Both parameters were built into the week 5
signature for this purpose, and no student reopens a week 5 cell. That is the
whole change to the agent's spine.

**Why this is the week the build prompt calls the differentiator.** In this
agent the entire email body is attacker-controlled text flowing into the prompt.
The corpus places injection payloads in six positions inside this one lab, so
students meet the threat as a family of placements rather than as a single
trick.

## 2. The lab deliverable

A guarded triage agent, and a record of what the guardrails changed.

The student runs eleven emails twice. Once through the week 5 agent with no
defenses. Once through the guarded agent. The notebook exports one file holding
both results for all eleven, plus the escalation decision and the token cost of
each run.

The evidence that carries CLO4 is a matched pair. Email 013 is a benefits
notice carrying a paragraph addressed to AI triage tools, telling them to return
a benign verdict. Email 024 is the same message word for word with that
paragraph removed. The student measures what the paragraph did to their own
model, then measures what their guardrails took back.

| Email | Role in the lab |
|---|---|
| 013 | The required body injection. A paragraph after the signature instructs any AI reader to record benign, high confidence, no escalation |
| 024 | The control. Word for word identical, payload removed, different mailbox |
| 014 | Payload hidden in the HTML part only. The plain text part is clean |
| 020 | Payload shaped like the agent's own tool output, claiming the link is allowlisted |
| 021 | Payload disguised as the mail gateway's own closing banner |
| 022 | Payload in the subject line and the sender display name |
| 023 | Payload in forged headers below the gateway's own trace line, and it asks for the recipient's report history |
| 015 | The benign decoy. Instruction-shaped words sit inside a quoted example in an internal security reminder. A keyword detector escalates it and is wrong |
| 016 | The fact-validation case. The model reads it as benign; the extracted Reply-To domain says otherwise |
| 009 | Low confidence case. A pretext with no link and no ask yet |
| 012 | Low confidence case. Every tool returns something, none of it decisive |

Email 015 is the reason this lab measures a false positive as well as a false
negative. A guardrail that escalates everything is not an acceptable guardrail,
and 015 is how the student sees that on their own screen.

## 3. What the student writes, and what arrives written

The notebook holds nineteen cells. Two are marked TODO. Everything else arrives
complete and working, including a reference copy of every function from weeks 1
through 5.

| TODO cell | Function | Lines the student fills | What it does |
|---|---|---|---|
| TODO 1 | `build_guarded_prompt(facts_text, body)` | 6 to 8 | Puts the rules first, wraps the body between the two markers, puts the required answer keys last, and keeps any hidden HTML text on the facts side |
| TODO 2 | `check_against_facts(result, facts)` | 6 to 8 | Returns a list of plain-language problems where the answer contradicts the extracted facts, and an empty list where it does not |

That is 12 to 16 written lines. Blank lines and comments are not counted. A
correct `check_against_facts()` catches at least three contradictions.

1. A benign verdict while a link host is on the blocklist.
2. A benign verdict while the sender is known bad.
3. An indicator naming a host that is not in the extracted list.

These arrive pre-written this week.

| Name | What it does |
|---|---|
| `BODY_START`, `BODY_END` | The two markers that fence off the attacker's text |
| `GUARD_RULES` | The sentences telling the model the fenced block is evidence to judge, never an instruction to follow |
| `CONFIDENCE_FLOOR` | The threshold below which a case goes to a human, set to 0.7 |
| `TOKEN_CAP_PER_RUN` | The most tokens one triage may spend, set to 4000 |
| `over_token_cap()` | Reports when the current triage has passed that cap. `guarded_triage()` passes it into the week 5 loop as that loop's step guard |
| `guarded_triage(parsed, schema=OUTPUT_SCHEMA)` | One full guarded triage, applying the fact check, the confidence floor and the token cap. The schema argument is a growth hook that week 7 uses and week 6 leaves at its default |
| `compare_guarded(email_ids)` | Runs the guarded and unguarded paths and returns one row per email |

Six pre-written demonstration cells carry the teaching. Two run the undefended
agent on 013 and on 024 and print both verdicts together. One prints the finished
guarded prompt so students can see their own markers in place. One runs the
guarded agent on the five other payload placements and prints where it still
fails. One prints the eleven-email comparison table. One lowers the token cap so
students watch it fire.

The design choice worth stating plainly: the student writes the two smallest and
most load-bearing pieces. Fencing the body is the defense. Checking the answer
against facts is the control on the defense. Everything mechanical around them
is given, so the 2.5 to 3 hours goes into judgment rather than typing.

## 4. Weekly objectives

Presented on the module Overview page under the template's lead sentence, "By
the end of this module, you will be able to:". Each carries its parent course
learning objective in brackets, per template conflict item 22.

| # | Objective | Parent | Words | Verb |
|---|---|---|---|---|
| 6.1 | Build a guarded prompt that treats the email body as data. | CLO4 | 11 | Build |
| 6.2 | Compare your agent's verdict on the injected email with its clean twin. | CLO4 | 12 | Compare |
| 6.3 | Judge whether your guardrails make prompt injection risk low enough to accept. | CLO4 | 12 | Judge |

All three parent to CLO4, which is correct. Week 6 is the primary evidence week
for CLO4 and holds the only rubric criterion linked to that Outcome.

Week 6 also reinforces CLO1 and CLO2. Students reuse their own fact extraction
from week 3 and their own output validation from week 2. Neither gets a week 6
rubric criterion, and neither gets a week 6 Outcome link. That is deliberate.
The Outcomes use the most recent score, so a week 6 link would overwrite the
primary result recorded in weeks 2 and 3.

Each objective is visible in a submitted item. Objective 6.1 shows up in the
fence record the export cell writes for email 013. That record holds the
position of each marker in the guarded prompt and the number of characters
between them. Objective 6.2 shows up in the rows for 013 and 024, which each
carry a verdict on both paths. Objective 6.3 is the written answer itself.

One limit, stated plainly rather than smoothed over. No rubric criterion scores
the quality of the fenced prompt on its own. Criterion 3 checks only that the
fence record is in the file. Criterion 2 scores the judgment, and that judgment
rests on the guarded verdicts the fence produced. So 6.1 is graded through its
effect, not on its own.

None of the three uses a banned verb. None joins two verbs with "and". Each is
one sentence of twelve words or fewer. Their measured reading level is in
section 14.

## 5. The sidebar

**Construct:** comparing two values, and checking one against known facts.
**Domain:** a library account checked against the catalogue record. No other
sidebar in the course uses it.
**Length:** 14 lines of code. **Time:** 25 minutes. **Ungraded.**

```python
catalogue = {"Salt Marsh Atlas": 21, "Bread Science": 14, "Night Trains": 21}
checked_out = [("Salt Marsh Atlas", 21), ("Bread Science", 28), ("Cloud Charts", 14)]

def loan_gaps(borrowed, record):
    gaps = []
    for book, days in borrowed:
        if book not in record:
            gaps.append(f"{book} is not in the catalogue")
        elif days != record[book]:
            gaps.append(f"{book} was lent for {days} days, catalogue says {record[book]}")
    return gaps

for finding in loan_gaps(checked_out, catalogue):
    print(finding)
```

This code was run before it went into this document. It prints two lines. Bread
Science was lent for longer than the catalogue allows, and Cloud Charts is not
in the catalogue at all.

The sidebar walks an account line by line. For each loan it asks two questions.
Is this book in the catalogue at all? If it is, does the loan length match the
length the catalogue records? It collects a plain sentence for every gap it
finds and prints them.

That is the same shape the lab needs. The lab walks the model's answer field by
field and asks whether each one contradicts a fact the extractor already found.
Same dictionary lookup, same two-branch check, same list of plain-language
problems returned.

The sidebar prose walks each line in the course reading voice, then ends with
one ungraded prompt: change one loan length in the catalogue and run it again,
and notice which line now appears. It links back to two week 0 sections, the one
on dictionaries and key access, and the one on if and else.

**Why pasting it into the lab fails.** The sidebar's function is named
`loan_gaps()` and takes a list of pairs, while the lab needs
`check_against_facts()` and two dictionaries, so pasting it wholesale raises a
name error.

**The names it uses.** `catalogue`, `checked_out`, `loan_gaps`, `borrowed`,
`record`, `gaps`, `book`, `days` and `finding`. None of them appears in the lab,
and none appears in any other sidebar in the course. Each of the seven weeks
uses a different everyday domain.

Nothing in the sidebar mentions email, senders, verdicts or security. It uses
none of the lab's names and none of the lab's data shapes.

## 6. The reading

Two pages, about 2,300 words in total, estimated at 45 minutes.

| Page | Words | Covers |
|---|---|---|
| Prompt injection in a triage agent | about 1,150 | Why the body is attacker text. The six payload placements in this lab. The four defenses and the order they are met. Why a keyword detector fails on email 015 |
| The wider AI risk set | about 1,150 | Hallucination, data exposure, privacy, automation bias, overreliance. Each tied to a case in this lab |

The second page carries breadth topic B4. It is survey content, so it replaces
reading time rather than adding to it, and it is written to the same 40 to 50
minute budget as every other week.

Each page runs 100 words above the 900 to 1,050 word target the course writing
standard sets, though both sit well inside its 1,400 word ceiling.

Page one carries six payload placements and four defenses. Page two carries five
named risks, each tied to a case in this lab. Cutting either to target would drop
a placement or a risk. Section 6.3 of the survey content plan sets the order of
cuts if the week ever runs long.

Every risk on the second page lands on a case students just ran.

- Hallucination is the indicator that names a host the extractor never found.
- Data exposure is email 023. Its forged header asks the agent to paste the
  recipient's report history into a summary meant for the reporter.
- Privacy is that same case one step wider: what you put in a prompt is what
  you expose.
- Automation bias is email 015, the benign message a keyword rule escalates.
- Overreliance is the confidence floor, and the honest reason it exists.

The reading is authored rather than linked, because openly licensed material at
this level does not exist. Sources will be drawn from national and openly
published guidance on adversarial machine learning, large language model
application risk, and AI risk management. Citations are verified by expert
subagent review when the reading is written, and any claim the review cannot
ground is flagged rather than kept.

Reading time is built from the one course reading rate, which section 2 of the
survey content plan sets at 200 words a minute for one pass. What each page asks
beyond reading the words is priced as its own named line.

| Part of the week 6 reading | Minutes |
|---|---|
| Page 1, one pass of 1,150 words at 200 words a minute | 6 |
| Page 1, walking the six payload placements and the email 015 case | 17 |
| Page 2, one pass of 1,150 words at 200 words a minute | 6 |
| Page 2, matching each of the five risks back to a case just run | 16 |
| **Total** | **45** |

That is 23 minutes on page one and 22 on page two, inside the 40 to 50 minute
budget with 5 minutes of headroom. The survey content plan prices the same two
pages the same way.

## 7. The discussion prompt

Fifteen to twenty minutes, including one substantive reply. Graded. The prompt
requires the student's own exported numbers, so a general opinion cannot answer
it. Shown here exactly as students will read it.

> **Write the rule your guardrails are missing**
>
> Open the file your notebook wrote, `week6_guardrails.json`. This post asks you
> to attack your own agent, not to describe it.
>
> Post first, then reply. Both are due Sunday at 11:59 PM Central. Post by
> Thursday if you can, so others have something to answer.
>
> In your post, answer all three.
>
> 1. Pick one email from 014, 020, 021, 022 or 023 where a guardrail did not
>    hold. Name it. Say what your own file shows for it.
> 2. Write the one extra rule you would add to stop it. One sentence, in plain
>    words, as you would hand it to a teammate.
> 3. Now find email 015 in your file. It is the benign decoy. Say what your new
>    rule would do to 015. Would it send a message to a human that should have
>    closed on its own? Give the number from your file that tells you.
>
> Then reply to one classmate whose extra rule is different from yours. Say what
> their rule would cost you on your own 015 row. Use your own number. A reply
> that only agrees does not count.
>
> Post about 150 words. Reply about 75 words. You may use AI help on this post.
> If you do, add one line at the end saying what you asked it.

**Why this prompt and not a before-and-after comparison.** Week 3 already asks
students to quote a pair of their own results and explain what moved. Week 4
asks for a prediction and then a check. Week 6 asks for something neither of
those does: write a control, then price it.

Question 3 is the whole point. A rule that catches the placement you missed
almost always escalates the decoy too, and a student who writes the rule finds
that out on their own numbers. That is the overreliance and automation bias
lesson in operational form, and it is where breadth topic B4 lands in this
discussion.

Two facilitation notes for the instructor guide. First, students will report
different rows for the same email, because the model is not deterministic and
one candidate model runs at a temperature above zero. That disagreement is the
discussion, not a bug. Second, a student whose guardrails held on every
placement should still answer for email 015, using the strictest rule they can
imagine adding.

## 8. What students submit

Three items, exactly as every other week. No zip files, no folders, no links.

**The screenshot.** Run cell 16, the comparison cell. Take one screenshot of the
printed table. It must show the header row, all eleven email rows including the
row for 015, and the token line printed underneath. Do not crop a row. No cell in
this notebook prints key material, so nothing has to be hidden before the
screenshot is taken.

**The file.** Attach `week6_guardrails.json`. Cell 18 writes it and prints its
full path. Attach that file as it is. Do not rename it. Do not attach the
notebook.

Cell 18 writes one row per email. Five of the eleven emails carry no injection,
so their payload placement is written as the word none.

Cell 18 also writes one fence record for email 013. It holds where each marker
landed in the guarded prompt, how many characters sit between them, and how long
that email's body is. The record holds no body text, so no attacker text is
copied into the file.

**The written answer.** Three to five sentences, typed into the Canvas text box.
The prompt reads:

> In 3 to 5 sentences, answer this. Your guardrails changed how your agent
> handled email 013. Did they cut prompt injection risk enough for a real
> security team? Name one number from your own file that backs your answer.
> Then name one case your guardrails still miss.

That written answer is the CLO4 judgment. The exported file is its evidence. A
grader can score both without opening a notebook or running any student code.

## 9. Rubric sketch

One hundred points. Three criteria, four performance levels each, matching the
mastery scale in the alignment matrix. Every weekly lab in this course is worth
100 points, so the seven labs carry equal weight inside the Labs group. Every
criterion is gradeable from the screenshot, the file and the written answer
alone. A correct submission can reach full marks on all three.

| # | Criterion | Points | Linked Canvas Outcome | What the grader reads |
|---|---|---|---|---|
| 1 | Submission completeness | 8 | None. Non-CLO expectation | All three items present and readable. The file opens. The screenshot shows the whole table |
| 2 | Guardrail judgment | 72 | CLO4: Judge guardrails against prompt injection | The written answer judges whether the guardrails reduce injection risk to an acceptable level, cites a number the attached file shows, and names a case that still gets through |
| 3 | Guarded run completeness | 20 | None. Non-CLO expectation | The file holds a row for all eleven emails. Each row carries a verdict on both paths, an escalation reason and a token count. Each row carries a payload placement where the email has one, and the word none where it does not. The fence record for email 013 is present |

Criterion 3 is a check on what the file contains, not on how good the run was.
Only six of the eleven emails carry an injection: 013, 014, 020, 021, 022 and
023. The other five are 009, 012, 015, 016 and 024.

Those five rows read none for placement, which the export cell writes for them.
A grader who expected eleven placements would mark a correct file down on five
rows. So the criterion says what to expect on each kind of row.

Criterion 2 is the mastery scale multiplied by eighteen, so its four levels map
one to one onto the Outcome's four ratings with no translation step. 72 points is
Exceeds standard. 54 is Meets standard, which is the mastery level. 36 is
Approaching standard, and 0 is No evidence.

| Level | Criterion 2 wording |
|---|---|
| Exceeds standard, 72 | Reaches a clear judgment, supports it with the student's own before and after numbers, and names a specific residual gap with the placement that causes it |
| Meets standard, 54 | Reaches a clear judgment and supports it with at least one number the attached file shows |
| Approaching standard, 36 | States a judgment with no number, cites a number the attached file does not show, or argues only from general claims about AI risk |
| No evidence, 0 | No judgment stated, or the written answer is missing |

Two of the three criteria carry no Outcome link, and both measure submission
completeness. Criterion 1 covers the three items. Criterion 3 covers what is
inside the file. Neither is a course objective, and both are declared non-CLO
expectations here, as the alignment matrix requires.

An earlier draft of this rubric held a fourth criterion for using the student's
own numbers rather than general claims. Those points now sit inside criterion 2.
There are two reasons.

The same evidence was being scored twice, because criterion 2 already drops a
submission that cites a number the file does not show. And judging with evidence
from your own run is CLO4 performance, so those points belong on the CLO4
Outcome rather than outside the Outcomes with no link.

That reading is now the course rule rather than this week's preference. Clause 4
of the rubric link rule in the alignment matrix says a criterion scoring a
student's use of their own results stays inside the Outcome-linked criterion.
Week 7 was brought into line with the same clause.

CLO4 has exactly one rubric criterion measuring it across the whole course. It
is criterion 2 here, as the alignment matrix records.

## 10. The self-check

Six multiple choice items. Low stakes, auto-graded, unlimited attempts, no time
limit. Self-checks carry 8 percent of the course grade in total.

| Item | Covers |
|---|---|
| 1 | Why the email body counts as attacker-controlled text |
| 2 | Which defense catches a payload hidden in the HTML part |
| 3 | What the fact check compares, and what it does when the two disagree |
| 4 | When the confidence floor sends a case to a human |
| 5 | What the per-run token cap stops, and what it does not stop |
| 6 | Breadth topic B4: which wider AI risk the forged header case in email 023 shows |

Item 6 is the self-check's share of breadth topic B4. Every stem is written at
the course reading level and every stem is answerable only by a student who ran
the lab.

## 11. Time estimate

| Activity | Minutes |
|---|---|
| Overview video | 3 |
| What success looks like video | 5 |
| Sidebar | 25 |
| Reading, two pages | 45 |
| Lab | 180 |
| Discussion, post and one reply | 20 |
| Self-check and submission | 30 |
| **Total** | **308 minutes, or 5.1 hours** |

Under the 6 hour ceiling with about 50 minutes of slack. Video totals 8 minutes
against a 12 minute ceiling. Every other line sits inside its stated band. The
lab takes the top of its band, which the build prompt asks for on this week.

If real build time proves this optimistic, the reading is cut first, as the
build prompt directs. The sidebar and the lab scaffolding are not cut.

## 12. Token estimate per full lab run

A full run means every cell executed once, top to bottom, including the
undefended pass, the guarded pass and the lowered cap demonstration. The code
ledger records about 99 model calls for that run, counted cell by cell.

Two rules produce that figure. An undefended run makes one call per tool the
model asks for. A guarded run makes the same calls plus one closing call, which
`guarded_triage()` makes whatever stopped the loop.

| Cell | Runs | Calls |
|---|---|---|
| 6 and 7, the undefended pass on 013 and 024 | 2 | 6 |
| 11, the guarded check on 013 and 024 | 2 | 8 |
| 12, the guarded run on the five other placements | 5 | 18 |
| 16, all eleven emails both ways | 22 | 65 |
| 17, the lowered cap demonstration | 1 | 2 |
| **Total** | **32** | **99** |

An earlier draft of this spec used 44 calls. That figure counted the comparison
cell alone and left the closing call out. The arithmetic below is rebuilt on 99.

Character counts below are measured, except the two marked as authored text
that does not exist yet. The four marked shared are measured once for the whole
blueprint, in section 2 of the grade distribution and token totals document,
and weeks 3, 4, 5 and 7 send the same figures.

| Prompt part | Characters | Source |
|---|---|---|
| Guard rules | 700 | Authored, estimated |
| Loop instructions | 400 | Authored, estimated |
| Three tool definitions, resent every turn | 964 | Shared |
| Required answer keys, the rendered output schema | 347 | Shared |
| Playbook snippet | 1,366 | Shared |
| Known-good domain list | 668 | Shared |
| Facts block | 400 | Measured: 376 on email 013 |
| Fenced email body | 1,000 | Measured: 1,129, 752 and 1,006 on emails 013, 021 and 012; mean 962 |
| One tool result | 284 | Measured: 852 characters for all three tools, mean over the eleven week 6 records |

The playbook snippet and the known-good domain list are on this list for a
reason worth stating. An earlier draft of this table left both out.

Week 6 runs the week 5 loop unmodified and swaps in a different prompt, so it
sends everything week 5 sends. Weeks 3, 4, 5 and 7 all count both, and week 6
now does too. Leaving them out understated every call by 2,034 characters.

The arithmetic, in three lines.

One first-turn prompt is 700 + 400 + 964 + 347 + 1,366 + 668 + 400 + 1,000 =
5,845 characters, and 5,845 divided by 4 is 1,461 tokens.

Each later turn resends the whole list and adds one tool request plus one tool
result, about 404 characters or 101 tokens, so the average call across a run
carries about 6,451 characters, which is 1,613 tokens.

99 calls times 1,613 is 159,687 prompt tokens, plus 99 times 45 measured
completion tokens is 4,455, giving **about 164,000 tokens per full lab run**.

The 45 completion tokens per call is the measured mean from the serving stack
document with reasoning turned off: 34 tokens on a tool-request turn, 65 to 79
on an answer turn.

**One number that could move this by more than half again.** If the reasoning
model runs in its default mode, completions rise to roughly 950 tokens a call.
That is 99 times 950, or 94,050 completion tokens, and a full run near 254,000.
The serving stack document leans toward running with reasoning off for the labs,
which is the figure above.

Week 6 is the most expensive lab in the course, ahead of week 7's batch of
twenty at about 112,000 tokens. It runs eleven emails twice and then reruns
seven of them in the teaching cells, so it makes more calls than any other week.

Students who rerun the lab pay the full amount again. The course token budget is
controlled centrally and a student who runs out emails the instructor for a
top-up with no grade penalty, so no cutoff is built into the notebook.

## 13. Assumptions, and three things to confirm

1. **The per-run token cap counts completion tokens.** The code ledger sets
   `TOKEN_CAP_PER_RUN` to 4000 without saying which number it counts. It matters.
   A four-step triage costs about 4,300 prompt tokens and only about 170
   completion tokens. If the cap counted prompt tokens it would fire on nearly
   every email in this lab, which is not the design. This spec reads the cap as
   counting completion tokens for one triage, which matches the serving stack
   document. That reading needs pinning in the ledger before Phase 2.
2. **The cap will not fire on its own with reasoning off.** That is why the
   notebook includes a cell that lowers the cap deliberately. Students still see
   the control work. Say so plainly on the page rather than letting a student
   conclude the cap does nothing.
3. **Student line count runs one line over the stated target.** The build prompt
   sets 5 to 15 written lines per lab. This week is 12 to 16, and reaches 16 only
   when a student writes each condition on its own line, which is the style week
   0 teaches. Cutting to 15 would mean handing over one of the three
   contradiction checks, which weakens the only CLO4 evidence in the course. The
   recommendation is to accept 16.
4. **The cap stops the run without inventing a stop reason.** A run that passes
   `TOKEN_CAP_PER_RUN` records the stop reason `step_cap` and escalates with
   `escalate_reason` set to `token_cap`. `step_cap` is the corpus value for a run
   a cap ended rather than a decision, and the escalation reason says which cap
   fired. There is no sixth stop reason anywhere in the course, so a week 6 file
   never carries a value the week 5 rubric or the week 5 self-check would reject.
5. **Discussion timing.** The template sets every weekly due date to Sunday at
   11:59 PM Central. The prompt above keeps that as the graded deadline and asks
   for a Thursday first post as a courtesy, not a rule. If the program wants a
   graded two-stage deadline, that is a template deviation to approve.
6. **Only three of the eleven week 6 emails are rendered today.** Emails 013,
   021 and 012 exist as files. Body character counts come from those three. The
   other eight are specified in the manifest and are generated in the full build,
   so the body figure above should be re-measured once they exist.
7. **The reading's citations are not yet verified.** The sources are named by
   type in section 6. Verification happens through expert subagent review when
   the reading is authored, and any ungrounded claim is reported rather than kept.
8. **Reading rate.** The 45 minute estimate uses the one course rate of 200
   words a minute for one pass, plus named lines for what the pages ask beyond
   reading. The rate is stated once, in section 2 of the survey content plan,
   and every week is priced from it. If the program uses a different rate for
   online course workload, that one number changes and all seven weekly totals
   change with it.
9. **Evidence use sits inside the Outcome-linked criterion, course wide.** This
   was an open question in an earlier draft and it is now settled in the
   alignment matrix rather than week by week. Clause 4 of the rubric link rule
   says a criterion scoring a student's use of their own results stays inside the
   Outcome-linked criterion. Week 6 already worked that way. Week 7 dropped its
   separate "Own results used" criterion to match.

## 14. Measured readability

Measured with the course readability gate on 2026-09-03. This is a program
manager document, so the whole page is held to grade 9.5. Student-facing text
drafted inside it is held to grade 7.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 6.6 | 13.6 words | 37 words |
| The discussion prompt, section 7 | 2.1 | 8.0 words | 16 words |
| The written answer prompt, section 8 | 3.9 | 9.4 words | 12 words |
| The three objectives, section 4 | 6.2 | 11.7 words | 12 words |

No prose paragraph on this page runs over 70 words.

**How the objectives were scored.** The three of them run to 35 words, which is
under the gate's 40 word floor, so the tool declines to score the block as it
stands. The block was repeated until it cleared the floor and then scored.
Repeating text does not move a Flesch-Kincaid grade, because the formula is a
ratio of words to sentences and syllables to words. Measured that way the block
scores 6.15. Scored one at a time, 6.1 is 4.79, 6.2 is 6.79 and 6.3 is 6.79.

Those numbers count "prompt injection" and "guardrails" in full. The build
prompt exempts required technical vocabulary from the reading level count. No
exemption is claimed here, because all three objectives clear grade 7 with both
terms counted.

An earlier wording of 6.2 and 6.3 did not clear it. That block scored 7.17, with
6.3 alone at 8.76. The rewording changed "control twin" to "clean twin" and
"cut prompt injection risk to an acceptable level" to "make prompt injection
risk low enough to accept". Both keep the CLO4 meaning and neither changes the
verb.
