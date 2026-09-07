# Writing standard for ITSY-1377-000

Every student-facing word in this course is held to the same measured standard
as the college's two existing course trees in this repository. This file states
that standard as numbers, so that a page either meets it or does not.

The gate is `tools/readability.py`. Run it on this course with:

```
ITSY_CONTENT=builder/content python3 -m tools.readability
```

## 1. Reading level

| Measure | Ceiling (build fails above it) | Target (write to this) |
|---|---|---|
| Flesch-Kincaid grade, after exclusions | 8.0 | 4.0 to 5.0; course mean near 4.4 |
| Average sentence length | 15 words | 9 to 12 words |
| Longest sentence on a page | 40 words | under 25 |
| Paragraph length | 70 words | 30 to 50 |
| Flesch reading ease | none | about 80 or higher |

The exclusions are the tool's: fenced code, command output, tables, block
quotes, URLs, file paths, framework identifiers, headings and list markers.

### 1.1 The second bar, for documents staff read

The table above is the student bar. It is written for a page a student reads in
a browser, and it is the right bar for everything under `content/`.

It is the wrong bar for a blueprint, a spec, an instructor guide or a memo.
Those are written for the program manager, for a curriculum committee or for an
adjunct, and they are read the way a professional reads a reference document.
Holding them to nine word sentences would make them worse, not better.

| Measure | Ceiling for a document under `docs/` or `instructor/` |
|---|---|
| Flesch-Kincaid grade, after exclusions | 9.5 |
| Average sentence length | 18 words |
| Longest sentence | 45 words |
| Paragraph length | 70 words |
| Page length | not capped |

**Why this is written here now.** The bar itself is not new: the Phase 1
package claimed every blueprint file measured inside it. What was missing is
this table. The numbers lived in a status note, `tools/readability.py` had no
notion of them, and so the claim was made against a bar the tool could not
check. The tool applied the student ceilings to every staff document instead,
which marked a 6,852 word contract document as over a 1,400 word page budget
and reported an average sentence of 16.6 words as a failure when the bar is 18.

The tool now reads this table for anything outside `content/`, so the claim is
checkable rather than asserted.

Two files are exempt from both bars and stay exactly as written:
`docs/build-prompt-v1.3.md` and `docs/program-manager-suggested-outcomes.md`
are the user's own words, kept verbatim on purpose.
Email headers and JSON are code and are excluded. Every technical term is
defined in plain words the first time it appears on a page, and again in the
glossary.

## 2. Length

Length is measured in weighted words: prose counts in full, and table rows,
list items and code lines count at 60 percent. The budget is the ceiling. The
target is what the existing courses actually run to.

| Page kind | Budget | Target | Existing courses measured |
|---|---|---|---|
| Start Here page | 450 (policy pages 650, AI use policy 550) | 400 | about 430 |
| Week overview | 400 | 350 to 390 | about 370 |
| Week content (reading) | 1,400 | 900 to 1,050 | about 1,000 |
| Lab page (assignment) | 700 | 350 to 450 | about 400 |
| Discussion | 500 | 330 to 400 | about 370 |
| Week wrap-up | 550 | 300 to 350 | about 320 |
| Glossary | 1,600 | as needed | reference, not enforced |
| Instructor pages, alignment matrix, risk register | none | complete rather than short | measured near grade 6 |

Kinds this course adds, mapped to the closest existing kind:

| New kind | Treated as | Budget | Target |
|---|---|---|---|
| Scripting sidebar prose (around the code) | discussion | 500 | 250 to 350 |
| Starter notebook markdown cells, per notebook | assignment | 700 | 400 to 550 |
| Week 0 on-ramp, per section or numbered part | content | 1,400 | 250 to 800 |
| Weekly announcement | overview intro | 250 | 150 to 200 |
| Quiz stem plus options | one item | 90 words | 40 to 70 |
| Video narration, per video | governed by the instructional-video skill | | 2 to 4 minutes spoken |
| Corpus playbook snippet | content | 250 | 150 to 250 |

**Why the week 0 target moved.** It was first set at 600 to 900 by analogy with
a week's reading page. That is the wrong analogy. A reading page is prose. An
on-ramp section is a worked example: a short setup, a runnable cell, a
line-by-line walkthrough written as a list, a cell to change, a task, and the
answer. The prose around the code is deliberately thin, because the student's
time goes into running cells rather than reading about them.

Measured on the shipped notebook, with code counted at the scan weight, the
sections run from 272 to 762 weighted words. Sections 8 and 10 are the two long
ones and each ships in two numbered parts, which measure 288 and 451, then 421
and 1,153. Section 10 part two, the walkthrough of six errors, is the one part
that runs near the budget, and it earns it: it is the section a student rereads
in week 3 and again in week 5.

The alternative was to grow eight sections to 600 words each. That would add
roughly 80 minutes to a notebook already planned at 4 hours 57 minutes, against
the build prompt's 6 hour ceiling for week 0. Length was not the thing to
change, so the target was.

## 3. Reading time

One rate governs every reading estimate in this course, so that seven weekly
budgets are built the same way and can be compared.

**The rate is 200 words a minute, and it prices one pass over the words.** That
is a normal adult silent reading rate for plain prose. It is a floor, not a
plan, and no weekly reading is ever budgeted at the rate alone.

Anything a page asks a student to do beyond reading the words once is priced as
its own named line in the week's reading table, with the minutes shown beside
it. That is where the study time lives. Named lines the course uses:

| Named line | What it prices |
|---|---|
| A second pass over defined terms | Rereading a block of first-time definitions |
| A labeled diagram | Reading a diagram and matching it back to the prose |
| A worked example | Stepping through a finished example line by line |
| Embedded code or data blocks | Reading a JSON block, a header excerpt or a table |
| A stop-and-think question | Answering an ungraded question inside the page |
| One cited source | Opening one citation and skimming it |

Two rules keep the rate honest.

- Never lower the rate to make a page fill its budget. Add a named line, or
  write more page.
- Never raise the rate to make a page fit. Cut words.

Section 2 of the survey content plan states the same rate and shows the split
for the three weeks that carry survey content. Every weekly spec prints its own
table, and every one of them adds to the minutes the week's time budget charges.

The rate is a planning figure, not a measurement. No reading rate has been
measured for this student population. The build prompt asks for the weekly time
budget to be checked against the real week 1 and week 2 builds, and that check
is what should settle it.

## 4. Voice

- Second person, active voice. "You add a tool," not "a tool is added."
- The common word: use, start, show, fix, check. Not utilize, commence,
  demonstrate, remediate, validate (in narrative prose).
- One idea per paragraph. One job per sentence. Front-load the point.
- Instructions are numbered steps, never prose.
- No em dashes anywhere. Commas, colons, parentheses and semicolons are fine.
- No idioms, sports or military metaphors, or humor that needs shared culture.
  The audience is adults of mixed ages and first languages.
- Professional practitioner tone. Never "hacker."
- Days, not dates. "Due Sunday 11:59 PM" or "day 35."
- No bracketed placeholders, no TODO, no highlight color left from a template.

## 5. How the measurement reaches everything

The gate reads markdown under `builder/content/`. Everything else student-facing
is extracted to markdown and measured the same way before it ships:

- Notebook markdown cells (starter notebooks, sidebars, week 0), per notebook.
- Quiz stems and options, per item and per quiz.
- Discussion prompts, announcements, rubric rating text.
- Video narration, through the instructional-video skill's own check.

The readability report for the whole course is committed beside the content so
a reviewer reads the numbers rather than the claim.
