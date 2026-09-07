# Week 3 spec: Grounding

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview
College, Cyber Defense program
**Phase 1 blueprint, item 3, week 3 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.

Week 3 carries the primary evidence for course learning objective 1 (CLO1):
*Extract the header, authentication, sender, and URL facts an AI model needs to
judge a suspicious email.*

Five terms are used below.

| Term | What it means |
|---|---|
| Prompt | The text sent to the AI model. |
| Facts block | A short labeled list of facts about one email, written into that prompt. |
| Grounding | Sending those facts instead of the raw message text alone. |
| SPF, DKIM and DMARC | Three checks the mail system runs on an arriving message. They test whether it really came from the domain it names. |
| TODO cell | A block in the student's notebook, marked with a comment, where the student writes the code. |

## The capability added

Students stop sending the raw email body on its own. They build a facts block
from what the shipped parser already returns, and they send that instead.

The facts block holds:

- The sender name, the sender address and the sending domain.
- The reply address and the subject.
- The three authentication results.
- Whether the displayed name matches the sending domain.
- The link hosts found in the message.
- The gateway's outside-mail flag and its scan result.
- Any attachment filename.

The prompt also carries an eleven rule phishing playbook and the list of the
organization's own domains and hosts. Both ship as data files.

This is exactly one capability because nothing else in the agent moves. The
model call, the strict JSON output, the schema check and the retry all stay as
week 2 left them. There is no tool, no loop, and no new output format.

The only change is what goes into the prompt. That is what makes the week's
lesson visible. The same code and the same schema produce a different verdict
once the facts arrive.

## The lab deliverable

Six emails run twice each. First the ungrounded way, body alone, which is week
2's path. Then the grounded way, with the facts block. The notebook prints one
comparison table and writes one file, `week3_grounding.json`.

Per email that file holds:

- The email id.
- The ungrounded verdict and its confidence.
- The grounded verdict and its confidence.
- Whether the verdict changed.
- The exact facts block that was sent.

It also holds the session token totals.

The six emails are 001, 004, 005, 006, 017 and 025. Emails 005 and 025 are the
matched pair the corpus was built around. Read on the body alone, 005 looks
malicious and 025 looks benign. The truth is the reverse.

Grounding has to correct both, in opposite directions, on the same extractor and
the same prompt. That symmetry is the point of the week. Grounding is not a way
to add suspicion. It is a way to add facts.

## What the student writes, and what arrives written

Two TODO cells. Everything else in the notebook is pre-written and working.

| Cell | What the student writes | Lines |
|---|---|---|
| TODO 1 | `build_facts(parsed)`. Picks the facts worth sending out of the parsed email and returns them as one flat dictionary. | 8 to 10 |
| TODO 2 | `format_facts(facts)`. Walks a fixed order and builds one labeled text block. | 4 to 5 |

TODO 1 is where a student decides which facts a sound judgment needs. That
decision is the week's reading put into practice. TODO 2 is the exact construct
the sidebar prepares.

These parts arrive pre-written and working:

- The configuration cell, the token counter, the request helper and the export
  helper.
- All working code from weeks 1 and 2.
- The data file loader, the known-good domain list and the playbook text.
- The known-name list that lets the display-name check fire.
- The fixed fact order and its labels, named `FACT_ORDER` and `FACT_LABELS`.
- The prompt builder and the grounded classifier.
- The routine that runs both paths over a list of emails.

Two check cells also arrive written. One runs the student's `build_facts()` on
005 and 025 and prints both results side by side. The other prints the finished
facts block for 025 and counts its characters, so students see the size of what
they are sending.

**One gap, now closed.** The code ledger set TODO 1 at 8 to 10 lines and TODO
2 at 5 to 7. Together that is 13 to 17 lines, and the build prompt's ceiling is
15 lines per lab. This spec closes the gap by shipping the fixed fact order and
its labels pre-written, as `FACT_ORDER` and `FACT_LABELS`. That takes two lines
out of TODO 2 and lands the pair at 12 to 15.

The code ledger now carries the same two names and the same line counts, in its
week 3 section and in its student line count table.

## Weekly objectives

Shown as students see them, under the template's lead sentence, with the parent
course objective in brackets.

By the end of this module, you will be able to do these three things.

| # | Objective | Verb | Words | Parent |
|---|---|---|---|---|
| 3.1 | Extract the sender, header, link and mail-check facts into one facts block. (CLO1) | Extract | 12 | CLO1 |
| 3.2 | Report which verdicts changed after you added the facts block. (CLO1) | Report | 10 | CLO1 |
| 3.3 | Justify which facts you left out of the prompt. (CLO1) | Justify | 9 | CLO1 |

Two notes on the wording. "Mail-check facts" is the plain-language name for the
SPF, DKIM and DMARC results, so objective 3.1 still covers all four fact groups
CLO1 names. Objective 3.2 names what the student does, which is reading the
comparison table the notebook prints and reporting what moved. The notebook, not
the student, builds that table.

All three sit under CLO1, which is correct for this week. CLO1 is the only
objective week 3 carries, and it is carried here as primary evidence. No
objective in this week lacks a parent.

Each objective is measured by a rubric criterion. Objective 3.1 is measured by
criterion 2, objective 3.2 by criterion 3, and objective 3.3 by criterion 4.
Criterion 2 is the one that links to the CLO1 Canvas Outcome, so objective 3.1
is the only one of the three that reaches the outcome roll-up. Criteria 3 and 4
carry no link, because Canvas refuses a rubric that aligns one Outcome more than
once. The rubric sketch below records that amendment and what it costs.

## The sidebar

**Construct.** Building a longer string from several parts, in a controlled
order. One construct only.

**Domain.** A class roster. The sidebar prints one line per student for a sign-in
sheet. No other sidebar in the course uses this domain. It has nothing to do with
email, alerts, headers or verdicts.

```python
# Build one roster line out of several fields, in an order you choose.
roster = {
    "surname": "Okonkwo",
    "given": "Amara",
    "seat": "B4",
}
headings = {"surname": "Last", "given": "First", "seat": "Seat"}
line_order = ["given", "surname", "seat"]

roster_lines = []
for field in line_order:
    roster_lines.append(headings[field] + ": " + roster[field])

roster_block = "\n".join(roster_lines)
print(roster_block)
```

Fifteen lines, runs as written, one construct. The walkthrough explains each
line in plain words. The first dictionary holds the student's details. The
second holds the words printed in front of them. The list sets the order. The
loop makes one line at a time. The join glues those lines into one block of
text.

**Try changing this.** Move `"seat"` to the front of `line_order`. Run it
again. The block comes out in a new order. You changed no detail to do it.

**Link back.** Week 0, the section on variables and strings, and the section on
for loops.

**Why pasting it into the lab fails.** The lab hands `format_facts()` a
dictionary named `facts`, and it ships its own order and labels as `FACT_ORDER`
and `FACT_LABELS`. Those four names are the lab's whole vocabulary for this
step, and the code ledger fixes them. The sidebar uses `roster`, `headings`,
`line_order`, `roster_lines` and `roster_block` instead. None of those five
exists in the lab, so a student who pastes the sidebar into the TODO cell gets a
`NameError`.

None of the five appears in any other weekly sidebar either. Each of the seven
weeks uses a different everyday domain and a different set of names, so no
sidebar reads as revision of one a student has already worked through.

## The reading

**Title.** What you put in the prompt is what you expose.

**Length.** About 1,050 words, plus two short header excerpts and one table.
That sits inside the 1,400 word page budget, at the top of the 900 to 1,050 word
target.

**Estimated time.** 45 minutes, inside the 40 to 50 minute weekly budget. It is
built the way every week is built: one pass at the course rate of 200 words a
minute, then a named line for everything the page asks beyond reading the words
once. The rate is stated once for the whole course, in section 2 of the survey
content plan.

| Part of the reading | Minutes |
|---|---|
| One pass of 1,050 words at 200 words a minute | 5 |
| Reading the two header excerpts and the table | 15 |
| A second pass over the data minimization section | 15 |
| Opening and skimming one cited source | 10 |
| **Total** | **45** |

The reading covers four things.

- Why a model is a judgment layer over facts you pull out yourself, not a
  detector.
- The facts worth pulling: who sent the message, whether the three checks
  passed, whether the displayed name matches the sending domain, and where the
  links point.
- Data minimization, which means sending only what a decision needs. Every line
  you add to a prompt is a line you have handed to an outside service.
- The same extraction pattern applied to logs, alerts, tickets and system
  messages, so students see that the skill is not about email.

Citations come from NIST, CISA and the published mail authentication standards.
Every one is checked to resolve before the reading ships.

## The discussion prompt

Written below word for word, as students will see it.

> **Grounding changed a verdict. Which one, and on what fact?**
>
> Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central.
>
> Your notebook ran six emails twice. Once on the body alone. Once with your
> facts block.
>
> In your post, do three things.
>
> 1. Name one email whose verdict changed. Give the email id. Give the verdict
>    before and the verdict after.
> 2. Paste the one line from your facts block that you think changed the answer.
>    One line only.
> 3. Say what your model listed as its indicators for that email. Did it name
>    the fact you pasted?
>
> Then reply to one classmate. Look at the line they pasted. Say what your own
> run on that same email did. Name a number or a line from your own output. A
> reply that only agrees does not count.
>
> Write about 150 words in your post. Write about 60 words in your reply. Use
> your own results only.
>
> You may use AI help on this post. If you do, add one line saying what you
> asked it.

**Time.** 20 minutes. That covers reading two or three posts, writing one, and
writing one reply. It sits inside the 15 to 20 minute budget.

The prompt cannot be answered from general opinion. Every part of it asks for a
value the student's own run produced.

## What students submit

Three items, and nothing else. No zip file, no repository link, and no cell that
shows key material.

1. **Screenshot.** The printed comparison table from cell 14. It shows all six
   email ids with the ungrounded and grounded verdicts side by side, and the
   token line under it. One image.
2. **File.** `week3_grounding.json`, written by the pre-written export cell. The
   cell prints the full path, so students see exactly which file to upload. Attach
   the file itself.
3. **Written answer, 3 to 5 sentences.** The prompt students see: *Name one fact
   you chose not to send to the model. Say why a sound verdict does not need it.
   Then name the one fact that changed a verdict in your run. Give the email
   id.*

The rubric is gradeable from those three items alone. Nobody has to run a
student's notebook.

## Rubric sketch

Four criteria, twenty-five points each, one hundred points. Four rating levels,
matching the mastery scale in the alignment matrix: exceeds standard, meets
standard, approaching standard, no evidence.

Every lab in the course carries 100 points. That is what makes the seven labs
weigh equally inside the 60 percent Labs group, and the grade distribution and
token totals document holds the whole table.

Two scales sit on each Outcome-linked row, as they do in week 2. The rating the
grader picks is what Canvas records against the Outcome, on the shared scale of
4, 3, 2 and 0. The criterion points are what the grade uses: 25 for exceeds
standard, 19 for meets, 13 for approaching, 0 for no evidence. Those are the
mastery ratings scaled by 6.25 and rounded to whole points.

| # | Criterion | Points | Judged from | Canvas Outcome |
|---|---|---|---|---|
| 1 | Submission completeness | 25 | All three items present and readable | None. Non-CLO expectation |
| 2 | Fact extraction | 25 | The facts block in the exported file, per email, plus both verdicts recorded side by side | CLO1: Extract email triage facts (primary) |
| 3 | Verdict comparison | 25 | All six emails are in the file, with both paths and the changed flag correct. The same six rows are readable in the screenshot. | None. Week expectation |
| 4 | Written answer | 25 | Name one fact you left out. Say why it was not needed. Name the fact that moved a verdict, with its email id. | None. Week expectation |

Criterion 2 carries the primary link for CLO1. That matches the alignment
matrix, which names week 3 criterion 2 as the primary link.

**Amended 4 September 2026.** This sketch gave criteria 3 and 4 supporting links
to CLO1 as well. They carry no link. Canvas allows one Outcome to align to one
criterion in a rubric, and a rubric that aligns CLO1 three times is refused
silently: the API answers HTTP 200 and creates no rubric at all. That is what
cost the week 1 lab its rubric while the build reported success. The constraint
and its consequences are recorded in the last section of the alignment matrix,
and the amendment under matrix section 11 records this change.

Criterion 2 is the criterion that keeps the link, because it is the one that
reads the extracted facts themselves, which is what CLO1 names.

Criterion 3 measures objective 3.2, the verdict comparison. Criterion 4 measures
objective 3.3, the data minimization judgment the week's reading teaches. Both
stay in the rubric at 25 points each, and both are still graded and reported to
the student. Neither reaches the outcome roll-up.

**What that costs.** CLO1's outcome data comes from criterion 2 alone, and week
3 is the only week that links to CLO1, so that one criterion is the whole
outcome record for it. Objectives 3.2 and 3.3 produce no outcome data. The
alternative is no rubric at all, so this is the lesser loss, but the program
manager should know the outcome report for CLO1 rests on one criterion.

Criteria 1, 3 and 4 are the non-CLO expectations in this rubric. Criterion 1
measures submission completeness. Criteria 3 and 4 measure whether the student
reported what they saw, which the matrix names as a non-CLO expectation.

## The self-check

Six items, multiple choice. Practice attempts are unlimited until the due date.
The score goes into the self-check group.

The six items cover:

- Which facts belong in a prompt, and which are exposure with no payoff.
- What a failed DMARC check on the organization's own domain means.
- Why a link host on neither list is unknown rather than clean.
- Why internal mail carries no authentication results at all.
- What changed between the two verdicts for email 005.
- How the same extraction step applies to a log line rather than an email.

## Time

| Activity | Minutes |
|---|---|
| Overview video | 3 |
| What success looks like walkthrough video | 4 |
| Sidebar | 25 |
| Reading | 45 |
| Lab | 165 |
| Discussion | 20 |
| Self-check and submission | 30 |
| **Total** | **292** |

Two hundred ninety two minutes is 4.9 hours, under the six hour ceiling. Video
totals 7 minutes, under 12. Every other line sits inside its own band. Nothing
had to be cut, so the reading keeps its full length and the lab keeps all of its
scaffolding.

## Tokens per lab run

Character counts are measured from the real corpus files. **Recomputed 4
September 2026, with all six week 3 emails rendered.** The average email body is
737 characters, the mean of `body_text` over 001, 004, 005, 006, 017 and 025,
which measure 807, 499, 1,065, 620, 705 and 724. `body_text` is the key the labs
send. This read 706, the mean over 004, 005 and 006 alone, and those three
figures were taken before the verify-and-fix rounds re-rendered those files, so
the old mean was stale in two ways at once. The average facts block is still 344
characters from three emails; it cannot be remeasured until the week 3 notebook
ships `FACT_ORDER` and `FACT_LABELS`, which fix what a facts block contains. The
playbook file is 1,366 characters, checked on the same date.

The rendered known-good domain list is 668 characters and the rendered output
schema is 347. Both are measured once for the whole blueprint, in section 2 of
the grade distribution and token totals document. The system prompt is 184
characters, so the system prompt with the output schema is 531.

- Ungrounded prompt = 531 + 737 = 1,268 characters, divided by 4, is 317 tokens.
  Grounded prompt = 531 + 344 + 1,366 + 668 + 737 = 3,646 characters, divided by
  4, is 912 tokens.
- The full run sends six emails both ways, so twelve calls: (317 + 912) times 6
  = 7,374 prompt tokens.
- Completion runs 65 to 79 tokens per JSON answer with reasoning switched off,
  from the serving stack record. Round to 100 for this week's longer indicator
  list: 12 times 100 = 1,200. Add one retry, about 1,000. **Total is about 9,600
  tokens per full lab run.**

One caveat belongs beside that number. The serving stack record shows the
reasoning model spending 819 to 1,173 completion tokens on the same kind of call
when reasoning runs at its default setting. At that rate the same lab costs
about 20,600 tokens, more than double. Switching reasoning off is therefore a
cost decision as well as a reliability one.

## Assumptions and gaps

1. **Closed 4 September 2026.** All six week 3 emails are rendered. 001 was
   already rendered when this assumption was written, so the sentence naming it
   was wrong the day it shipped; 017 and 025 have now been generated from
   `gen_017_fenwright_pay_statement_ready.py` and
   `gen_025_larkseal_review_encoded_subject.py`, their ground truth records
   upserted, `spec/phase0-sample-manifest.json` rebuilt, and the three release
   files rewritten. `validate_corpus.py` reports 16 files, 16 ground truth
   records, 0 failures, and the one permitted fold-length warning on 003.
   `check_spec.py` reports 56 records, all rules hold. The token estimate above
   is recomputed over all six. One part of it is not closed: the facts block
   average is still 344 characters from three emails, because no facts block
   exists to measure until the week 3 notebook ships `FACT_ORDER` and
   `FACT_LABELS`. Remeasure it when the notebook lands.
2. The line count fix above assumes `FACT_ORDER` and `FACT_LABELS` ship
   pre-written. The code ledger now names both and sets TODO 2 at 4 to 5 lines.
   Anyone who changes that ships a lab over the 15 line ceiling.
3. The lab carries 100 rubric points, the same as every other lab. All seven
   labs sit in one assignment group weighted at 60 percent. A percent-weighted
   group scores as points earned over points possible inside it, so the point
   total on one lab does set that lab's weight against the other six. Equal
   points are what make them equal. The grade distribution and token totals
   document sets the points for every graded item in the course.
4. The token estimate counts one full pass. Students who rerun cells while
   debugging will spend more. The running token counter in the notebook shows
   them their own total.
5. Week 3 sends no tool results, because tools arrive in week 4. The token
   arithmetic reflects that.
6. Due dates follow the template: Sunday at 11:59 PM Central. Term dates are
   still needed before any due date can be set.

## Measured readability

Measured with the course readability gate on 2026-09-03. This is a program
manager document, so the whole page is held to grade 9.5. Student-facing text
drafted inside it is held to grade 7.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 5.56 | 12.1 words | 34 words |
| The three objectives, with their lead sentence | 3.8 | 11.5 words | 15 words |
| The discussion prompt | 1.8 | 7.0 words | 14 words |
| The sidebar "try changing this" prompt | too short to score | 5.7 words | 8 words |
| The written answer prompt | too short to score | 9.0 words | 12 words |
| The rubric criterion and judged-from columns | 5.10 | 9.9 words | 16 words |

No prose paragraph on this page runs over 70 words. Two rows are under the
gate's 40 word floor, so the tool reports no grade for them and their sentence
measures are counted by hand. The rubric row is the criterion column and the
judged-from column, each cell read as one line, with the header row left out.

**One number that moved.** The rubric's judged-from column read grade 7.05 with
an average sentence of 18.2 words, over the 12 word limit for text a student
reads to find out what earns the points. Two cells ran long, at 22 and 29
words. Both are now two or three short sentences, and the column reads 5.10
with an average of 9.9 words.
