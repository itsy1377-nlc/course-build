# Beginner experience and accessibility

**Panel review, 2026-09-08.** Reviewer brief: where a real novice stops, an
audit of the student run's TAUGHT NOWHERE list, the paste-your-key design,
accessibility, loss of work, time and money, and what the course does
unusually well.

**Sources read:** `docs/student-e2e-run-2026-09-08.md`; the student's own
`REPORT.md` (976 lines) and `FINDINGS.md` (7,008 lines); and the course source
itself. **No course file was modified.**

Every claim below is marked **verified** (I read it in the file or ran it) or
**asserted** (my judgment, and I say what it rests on).

**Two corrections carried into this draft.**

- Finding 1.1 of `student-e2e-run-2026-09-08.md` has been corrected by its
  author since I read it. The planted paragraph *does* reach the undefended
  agent — `start_messages()` in `w6-lab` cell 5 pastes `parsed["body_text"]`
  into the user turn on every loop pass. What is true is narrower: the closing
  `ask_model(closing)` that writes the verdict carries no message history, and
  `closing` is built from `loop_prompt(parsed)`, which has no body. Nothing in
  this report depends on the superseded version, and section 8.2 refers to the
  corrected one.
- **Two of my own claims below were wrong and are corrected in place.** A
  commissioned independent audit of the TAUGHT NOWHERE list found that
  `.update()` and the nested dictionary literal *are* taught in week 0, in
  section 3, with an explicit forward reference to week 1. Sections 1.1, 2.1
  and 2.2 are rewritten. The argument survives, in a sharper and more specific
  form — see 1.1 and 2.2.

---

## 0. The one sentence

The prose and the accessibility engineering in this course are the best I have
seen in a first-semester technical course, and the two things a beginner needs
most — a place to practise the exact skill the first graded lab asks for, and a
copy of their work that survives the week — are the two things missing. Neither
shows up in a run by a student who already knows Python, because neither binds
until you get stuck.

The accessibility picture is the same shape. Tables, colour, captions,
contrast, resize and timing are all handled, most of them gated, several with
the WCAG criterion number written into the comment. What is missing is the
paperwork and the last mile: **there is no accommodations statement in the
syllabus**, the fourteen shipped transcripts lost their `lang` attribute and
their titles at the final build step, and the one graded artifact the course
demands in every lab — a screenshot — is required in a way a low-vision student
cannot satisfy and a blind student cannot produce.

---

## 1. Where a real beginner actually stops

The student run is a measurement of the course's *correctness*. It is not a
measurement of its *teaching*, and its own report says so. What follows is the
walk it could not do: week 0 and week 1 as somebody who has never written a
line of code.

### 1.1 The single most likely drop-out point: week 1, TODO 1, job 1

**Verified.** `lab/notebooks/w1-lab.ipynb` cell 5 (0-based; cell 6 as the
assignment page counts) tells the student:

> 1. Build the request as a dictionary. It needs four keys: `model`,
>    `messages`, `max_tokens` and `temperature`. Use the `MODEL` from the
>    configuration cell. `messages` is a list holding one dictionary, and that
>    dictionary has a `role` of `"user"` and a `content`.
> 2. Merge `MODEL_EXTRAS` into that dictionary. The `.update()` method does it
>    in one line.

and closes: *"Eight to ten lines. Week 0 sections 2 and 3 cover calls and
dictionaries."*

Now look at what the course gave the student to prepare with.

**`lab/notebooks/w1-sidebar.ipynb` — the 25-minute notebook whose entire job is
to prepare this lab — contains no dictionary.** I extracted its code: 515
characters, two examples, zero `{` outside f-string braces, zero `.update()`.
Part 1A is `boxes_in_cases(cases)` returning `cases * 6`. Part 1B is an
f-string. That is the whole sidebar. **Verified.**

Worse, the sidebar's own cell 0 misdescribes the lab it is preparing:

> The lab asks you to call a function someone else wrote, keep what it hands
> back, and print a line built from values. These two examples show that
> mechanism on a smaller problem.

That describes jobs 3 and 4. Jobs 1 and 2 — build a four-key dictionary
containing a list containing a dictionary, then merge another dictionary into
it — are not mentioned, and are the hard half.

So the ingredient list for the first graded function in the course is:

| ingredient | in the week 1 sidebar? | in week 0? |
|---|---|---|
| call a function, keep the return value | **yes**, part 1A | yes, section 2 |
| `return` a value | **yes**, part 1A | yes, section 6 |
| write a dictionary literal with four keys | **no** | yes, section 3 part two, cell 23 |
| write a list holding a dictionary | **no** | yes, section 3 part three, cell 26 |
| `.update()` | **no** | yes, cells 22-24, **with a forward reference to week 1 at cell 33** |
| **a variable as a dictionary value** | **no** | **no — see 2.2. This is the gap** |
| `reply["choices"][0]["message"]["content"]` | **no** | section 3, reading only |

Week 0 is better than I first credited it, and better than the student credited
it: cell 33 says outright *"In week 1 you build the request as a dictionary.
You fold a second dictionary into it with `.update()`."* That is a course
naming, one notebook in advance, the exact line a student is about to write.
It is excellent and I got it wrong on my first pass.

Which leaves the failure with three legs rather than five, and makes it more
specific, not less:

1. **Week 0 is optional.** The word appears on
   `content/pages/week-0-overview.md` lines 2 and 8, in `welcome-start-here.md`
   line 14, and in `week00` cell 0 in bold. The self-assessment routes a
   9-or-10 scorer past the whole notebook, and a 6-to-8 scorer past every
   section they did not miss a question on. Everything in the table's right-hand
   column is available only to a student who did the optional 4-to-6 hours.
2. **The week 1 sidebar — the 25 minutes the course *does* require — contains
   no dictionary at all**, and misdescribes the lab it is preparing.
3. **The one move nobody teaches anywhere is the one TODO 1 is made of.**
   Every dictionary and list literal in week 0 — all 33 of them — is built from
   constants. `{"title": "Dune", "due_days": 14}`. Not one puts a *name* where a
   value goes. TODO 1 asks for `{"role": "user", "content": prompt}` and
   `{"model": MODEL, "max_tokens": max_tokens, "temperature": temperature}`:
   **four variables inside two literals, and the substitution has never been
   demonstrated.** (Verified by the commissioned audit, which enumerated the
   literal assignments.)

That third point is the finding. A beginner can copy the *shape* from week 0
cell 26 and still not know that a bare name is allowed where `"Dune"` sat. It
is the same substitution f-strings teach inside braces — week 0 section 5 does
it beautifully — and nothing connects the two.

A student who takes the course's own routing at its word, skips week 0, and
does the required sidebar arrives at TODO 1 having seen a Python dictionary
exactly once: as an 18-word glossary line, `content/pages/glossary.md:51`,
*"A collection that holds values by name. **You read one** by giving its key."*

**Asserted.** This is where I would expect the largest single loss. My
estimate: of students who genuinely have no programming background and who
skipped or skimmed week 0, **30 to 45 percent stall here for more than an hour,
and 10 to 20 percent of the whole cohort never submit week 1.** In an
eight-week compressed session, a student who misses the first lab is
mathematically and psychologically behind in week 2, and week-1 non-submission
is the strongest single predictor of withdrawal I know of in this format.

The fix is small and the course already knows the pattern: give
`w1-sidebar.ipynb` a Part 1C that builds a stockroom-order dictionary **from
variables the cell above defined**, nests a list of one dictionary inside it,
and calls `.update()` on it. Same stockroom, 10 minutes, and it closes all
three legs at once — it is required rather than optional, it is a dictionary in
the sidebar, and it shows a name standing where a constant stood.

### 1.2 The first unforgiving error, and it lands in a cell the student was told not to touch

**Verified by execution.** I rebuilt `w1-lab.ipynb` cell 7 (the check cell) and
ran the four most plausible beginner versions of `ask_model()` through it.

Cell 7 is:

```python
CHECK_ANSWER = ask_model(CHECK_QUESTION)
print("Answer:  ", CHECK_ANSWER)
print()
show_tokens()

if CHECK_ANSWER.startswith("ask_model() is not written"):
```

| beginner mistake | what the check cell does |
|---|---|
| wrote the body, forgot `return` | `AttributeError: 'NoneType' object has no attribute 'startswith'` |
| returned the whole reply instead of the text | `AttributeError: 'dict' object has no attribute 'startswith'` |
| merged into the message dictionary | **passes silently** (the instructor's 1.5) |
| left the placeholder `return` in place | correctly caught, with a plain-English instruction |

The last row is good design. The first two are the problem.

Forgetting `return` is not a hypothetical. `week00-python-on-ramp.ipynb` cell
53 says so in its own words: *"This is the most common mix-up in the course. It
breaks week 1 on the first cell."* Week 0 predicts this failure precisely, one
notebook away — and the cell where it lands has no branch for it.

Two consequences a novice cannot get past unaided:

1. **The traceback names the wrong cell.** The failing line is in cell 7, a
   cell headed *"Pre-written. A check on the function you just wrote."* Step 3
   of the five-step routine — printed in `if-something-breaks.md:18`, in
   `tips-for-success.md:23`, in `week00` cell 1 and again in cell 97 — is
   *"Find your line. Look for the last line that names your own cell."* There
   is no such line. The routine the course teaches four times over dead-ends on
   the first error the course produces.
2. **The error type is the least helpful of the six.** `if-something-breaks.md`
   line 33 defines `AttributeError` as *"You asked a value for something it
   does not have."* Week 0's own worked `AttributeError` (cell 119) is
   `items.upper()` on a list. Its worked `None` case (cell 111) is a
   *`TypeError`*, `'NoneType' object is not subscriptable`. A beginner has to
   combine two separate lessons from two separate cells to reach "I forgot to
   return."

Three lines in cell 7 close it:

```python
if CHECK_ANSWER is None:
    print("ask_model() handed back None. Every path through it needs a return.")
    print("Week 0, section 6, 'The difference between return and print'.")
```

**Asserted.** Recovery rate without that guard: I would put it at **50 to 60
percent within an hour** for a genuinely determined novice, and near zero for a
student working at 11 pm on a Sunday, which is the scenario `week00` cell 96
itself invokes.

### 1.2a And week 1 is the one notebook that never says how to run a cell

**Verified, and it is a small thing that lands in a bad place.** Fourteen of the
fifteen notebooks pair the mouse verb with the keystroke — `week00` cell 0:
*"Click a cell, then press Shift and Enter to run it. Run the cells in order,
from the top."* `w1-lab.ipynb` cell 0 carries only the second sentence: *"Run
the cells in order, from the top."* No method.

For a student who skipped the optional week 0 — which is the student this whole
section is about — the first graded notebook in the course opens by telling
them to do something without saying how. `using-the-notebook-server.md:24`
covers it ("Run the first cell"), several days and one module earlier, and also
without a keystroke. The nearest instruction is in the notebook they did not
open.

One sentence, copied from the other fourteen.

### 1.3 Week 1's lab has the smallest time budget in the course and the least prepared student

**Verified.** From the seven `w*-overview.md` time tables:

| week | lab minutes | named debugging allowance |
|---|---|---|
| 1 | **150** | none |
| 2 | 180 (split five ways) | 40 min, *"run all four emails, fix what breaks"* |
| 3 | 165 | none |
| 4 | 165 | none |
| 5 | 180 | none |
| 6 | 180 | none |
| 7 | 165 (split five ways) | none |

Week 1 is the lowest number in the column, and it is the only week where the
student has never written a line of this course's Python. Week 2 is the only
week that budgets for things going wrong, and it budgets 40 minutes.

The student, who knew Python and debugged nothing, spent 195 minutes on the
week 1 lab against the 150 budgeted. **Asserted:** a novice who has to debug
the `return` will spend 4 to 6 hours on week 1's lab alone, which is the whole
week's budget, in the first week, before the discussion and the self-check.

### 1.4 Cognitive load: how much a beginner reads inside the notebook

**Verified.** `tools/readability.py` gates `content/**/*.md` and nothing else —
`_content_root()` resolves to `builder/content`, and the walk collects markdown.
It never sees `lab/notebooks/*.ipynb`, which is where the student spends 150 to
180 minutes a week, and it never sees `content/video/*.yaml`, which is what the
narrator says out loud.

I ran the tool's own `check_text()` over the notebooks. Reading level holds up
beautifully — the discipline extends to the ungated surface, and that is worth
saying plainly:

| notebook | markdown grade | code-comment grade | total instruction words |
|---|---|---|---|
| `w1-lab` | 2.29 | 4.29 | ~1,817 |
| `w5-lab` | 2.23 | 3.96 | ~3,863 |
| `w6-lab` | 3.63 | 4.31 | ~5,146 |
| `w7-lab` | 4.12 | 4.33 | ~5,725 |
| `week00` | 2.08 | 2.17 | ~6,887 |

Every one is under the gate's grade-8 ceiling, most far under. **But the word
budget is not.** `tools/readability.py` caps a *reading page* at 1,400 words
(`WORD_BUDGET["content"]`), and the comment block accompanying it says why:
*"A page can score grade 4 and still be twelve hundred words of unbroken prose,
which is not readable in any sense a student would recognise."*

That reasoning applies with more force to a notebook, and no budget applies
there. The week 7 lab notebook asks the student to read **about 5,700 words of
instruction — four times the ceiling the course sets for a reading page** — in
a surface with no navigation, no headings visible in a table of contents, and
no way to skim. Week 6 is 5,146. Week 0 is 6,887 across 130 cells.

**Asserted.** This is the quiet reason the later labs run long even for capable
students. The reading pages are budgeted to the minute and the notebooks, which
carry three to four times as much text, are budgeted not at all.

### 1.5 Unexplained vocabulary, and where it actually bites

The glossary is 123 terms, plain-language, and the course inlines a definition
at first use with real discipline (`welcome-start-here.md:23` defines "model" on
the spot; `canvas-and-tech-support.md:23` re-defines "notebook" and "cell").
That is unusually good and I want it credited.

Two gaps that bite in week 1 specifically:

- **`.update()`**, **verified**: named in `w1-lab` cell 5 as *"The `.update()`
  method does it in one line"*, and it is in no glossary entry and no week 0
  section. See 2.1.
- **Domain / subdomain / link host**, **verified**: `w1-content.md` defines
  asset, user, network, endpoint, log, alert, ticket, incident, escalation and
  documentation. The week 1 lab's 25-point criterion asks the student to name
  *"one specific thing to check before trusting the answer"*, and the obvious
  check on email 001 is that
  `my.fenwrightpay.example.secure-verify-login.example` is not Fenwright.
  Nothing in week 1 teaches reading a hostname right to left. The glossary's
  **Allowlist** entry (`glossary.md:25`) uses the phrase "link hosts" and is
  marked first-used in week 4.

**Verified, minor:** the glossary advertises its last column as *"Where that
word first shows up"* (`glossary.md:9`). Cross-checking 123 terms against the
actual reading order, 15 appear earlier than the column says. Most are
homonyms ("key" in "key facts", "call your instructor"); the real ones are
**Model**, **Prompt** and **API**, all used in Orientation and all marked
first-used in week 1. All three are inlined at the point of use, so the harm is
confined to a student who trusts the column.

### 1.6 A defect class the automated gates cannot see, concentrated in week 1

**Verified, and I believe new to this review.** A mechanical contraction pass
has broken at least twelve student-facing sentences by contracting an auxiliary
that is doing real work:

| file:line | as published | intended |
|---|---|---|
| `content/pages/home.md:32` | "so your instructor and your classmates know who you're." | who you are |
| `content/pages/welcome-start-here.md:43` | "Submit what you've." | what you have |
| `content/discussions/introductions.md:9` | "Your program, and how far along you're." | how far along you are |
| `content/discussions/introductions.md:13` | "Say what you've in common" | what you have in common |
| `content/pages/w1-overview.md:20` | "and if it sounds thin, it's." | it is |
| `content/pages/w1-content.md:22` | "Security work starts with knowing what you've." | what you have |
| `content/pages/w1-content.md:49` | "So now you've an alert." | you have an alert |
| `content/pages/w1-content.md:100` | "A low score leaves it where it's." | where it is |
| `content/pages/olrn-0001.md:25` | "which start date fits the week you've?" | the week you have |
| `content/pages/w8-overview.md:17` | "when you've a clear ninety minutes" | when you have |
| `content/pages/w8-wrap-up.md:2` | "what you've to show for it" | what you have |
| `content/video/w7-overview.yaml:55` | "It's you measuring the agent you've." | the agent you have |

**Nine of the twelve are in material read in the first seven days**, including
the course front page and the first sentence of step 1 of "After a week that
went badly". The twelfth is a narration line: it is spoken aloud by the TTS
voice and written into the caption track.

Two things make this worse than a typo list.

First, **the readability gate rewards it.** Flesch-Kincaid counts words and
syllables. "Submit what you've." is three words and four syllables; "Submit
what you have." is four words and five. The broken sentence scores *better*.
The course's mean grade of 3.72 is real and good, and this is the one place
where optimising for it damages the page.

Second, **the audience.** A fluent reader sees a typo. A first-time college
student, an ESL student, or a student with a reading disability reads it twice,
concludes they misread it, and reads it a third time. On the front page of the
course, in the first minute.

---

## 2. Audit of the student's TAUGHT NOWHERE list

The student recorded, per module, the knowledge it needed that the course never
gave. I checked each week 0 and week 1 item against the source myself, and had
the weeks 2 to 7 items checked independently. Verdicts:
**(A) genuinely untaught · (B) taught, the student missed it · (C) taught, but
too far from the point of need to help.**

The promise being audited, **verified verbatim** in two places —
`week00-python-on-ramp.ipynb` cell 2 and `content/pages/week-0-overview.md:50`:
*"Every line you write in a lab uses only what is in this notebook."* Note the
scope it actually claims: **lines you write.** Constructs that appear only in
cells marked "Pre-written. You do not edit this cell" fall outside it, and I
score those separately.

Headline: **of the seventeen items checked, five were wrong or overstated, and
the survivors cluster hard.** Two of the five were mine.

### 2.1 `.update()` — **(B): taught, and both I and the student missed it**

**Corrected.** `.update()` is taught in week 0 section 3, part two.
**Cell 22:** *"`.update()` folds a second dictionary into the first one."*
**Cell 23** runs it on an `account` dictionary. **Cell 24** explains the merge
semantics — *"`branch` was already a key, so its old value is replaced.
`card_expires` was not there, so it is added"* — which is the exact behaviour
`MODEL_EXTRAS` relies on. **Cell 33** forward-references week 1 by name.

And `w1-lab` cell 5's routing note, *"Week 0 sections 2 and 3"*, is **correct**:
section 3 is where it is.

The only residue is that `.update()` has no glossary entry, which is trivial.
This item is closed. The student read section 3 part one and stopped.

### 2.2 Writing `[{"role": "user", "content": prompt}]` — **(B) for the shape, (A) for the move that matters**

**Corrected, and this is the better version of the finding.**

Week 0 *does* construct the nested literal: **cell 26** builds
`holds = {"branch": ..., "books": [{"title": "Dune", "due_days": 14}, ...]}`
across seven lines, and **cell 27** narrates it: *"Lines 1 to 7 make one
dictionary with two keys… Each item in that list is its own dictionary with two
keys."* Cells 74 and 84 build more. "Week 0 taught only reading" is false.

What is genuinely untaught is narrower and harder: **every dictionary and list
literal in week 0 is built from constants.** All 33 literal assignments were
enumerated; not one places a variable inside a literal. TODO 1 needs four:
`prompt` inside the message dictionary, and `MODEL`, `max_tokens`,
`temperature` inside the request.

That is a real conceptual step — the same "a name can stand for a value here"
move that f-strings teach inside braces at week 0 section 5, and nothing in the
course connects the two. It is also, I think, the single most likely place a
beginner's first attempt at TODO 1 goes wrong, because the alternative reading
(`"content": "prompt"`) is syntactically valid and produces a model answer to
the wrong question with no error at all.

**(A), and the fix is one example, not one sentence.**

### 2.3 What goes in `content` — **(A), and it is a real ambiguity**

**Verified.** Cell 5 job 1 says the message dictionary *"has a `role` of
`"user"` and a `content`."* It supplies the value for `role` and not for
`content`. The only sensible value is `prompt`. Nothing says so. A student who
is not already guessing has nothing to go on, and a student who puts the wrong
thing there gets a model answer to the wrong question with no error.

### 2.4 `max_tokens` as a guillotine — **(C), one week late**

**Verified.** `w1-lab` cell 5 defines it as *"the most tokens the answer may
use. The default is 512."* That reads as a budget. The consequence is taught —
in **week 2**: `w2-content-2.md:25` (*"**Cut off partway.** The answer stops in
the middle, so the brackets never close"*) and line 39 (*"`length` means it ran
into the token limit you set"*). One week after the student meets it.

`send_request()` in cell 4 **does** handle it, and handles it well: if the
content is empty and `finish_reason == "length"` it prints *"The model ran out
of room before it answered"* and substitutes an explanation. But that path only
fires when the answer is **entirely** empty. The student's actual experience —
answer 1 of six truncated mid-word, with text present — takes neither branch
and prints nothing. **Verified from the code.** So the one case a student will
actually meet is the one case that is silent.

### 2.5 Reading a URL right-to-left — **(A)**, and 25 points ride on it

Covered in 1.5, and the independent audit widened it: **the concept is absent
course-wide, not merely from week 1.** Zero occurrences of "subdomain",
"rightmost", "right to left" or "registered domain" anywhere in `content/` or
`lab/` outside `lab/tools/triage_tools.py`, which students never open. Even
week 3, which owns the topic, says only (`w3-content.md:105`) *"A **link host**
is the part of a web address right after the slashes"* — which, applied to
email 001's `my.fenwrightpay.example.secure-verify-login.example`, hands the
student the whole 46-character string and no rule for finding the real host
inside it.

The week 1 rubric's "First judgment" criterion (25 points) is where it is
needed, and the week 1 discussion's model of a strong post is literally *"it
never mentioned the link."*

### 2.6 `inspect.signature()` in `w1-lab` cell 10 — **(A), and harmless**

**Verified.** It sits in a pre-written cell, and `week00` cell 2 covers the
case: *"Pre-written cells sometimes use more. You only have to read those."*
The student's own note says it was the first line that made it wonder whether
it was supposed to understand something. That is a real, small cost and I would
add one comment line, not a section.

### 2.7 `IndexError` — **(A), and it is a loaded footgun**

**Verified**, with one correction to the student's version. `week00` section 8's
`while` loops index by counter (`scores[steps]`), and cell 82 says *"Raise the
cap to 5 and run it again."* At 5 the list has exactly 5 elements, so **the
invitation itself is safe** — the student's account implied otherwise. It is
the obvious next nudge that breaks: a cap of 6 raises `IndexError`, and so does
cell 92 (`readings` of 3, `tries < 3`) at any cap above 3.

`IndexError` is not in the six-error table at cell 1, not in
`if-something-breaks.md`'s table, and not in the glossary. So the one section
that promises to name every error a student will meet hands them a "Try
changing this" cell one increment away from an error it does not name. One row
closes it.

Related and confirmed: cell 82 also asks for a change that is already made —
the cell ships with `max_steps = 5`.

### 2.8 `.keys()` and `round()` — **(A) for `.keys()`, (A)-but-fine for `round()`**

**Verified.** `week00` cells 109 and 127 recommend `print(basket.keys())` as
the way to see what a dictionary really holds — good advice — and section 3
never teaches it, nor does the notebook prepare the student for the
`dict_keys([...])` output shape, which looks like nothing else in the notebook.
`round()` is in a pre-written cell and is covered by the cell 2 exemption.

### 2.9 Weeks 2, 3 and 5 — the student's counts hold, and week 5 is worse than it said

Independently verified. Taking the student's four week 5 items and its week 2
and week 3 items in turn:

| claim | verdict | evidence |
|---|---|---|
| iterating a list of dicts (week 3 TODO 1) | **(B)** — taught, thoroughly | week 0 cells 74, 75, 76, 83, 84; and `w3-lab` cell 8 cites section 8 part one by name. The student is being asked to redo something it already did twice with an answer key. |
| empty-list truth test `if not problems:` (week 2) | **(A)** for the construct, **but the TODO admits a taught route** | zero `if not` in week 0 or any sidebar. But `w2-lab` cell 12 says only *"Return the answer as soon as the problem list is empty"*, and `len(problems) == 0` is week-0-writable. The mismatch is with the posted solution, not the task. |
| early `return` / `break` (week 2) | **(C)** — three weeks late | zero `break` in week 0. Taught in `w5-sidebar` cells 8-10. `w2-sidebar` cell 9 offers a taught sentinel alternative and says so. |
| bare list as a truth test (week 5) | **(A)** for the rule, TODO admits an escape | all 21 conditionals in week 0 use an explicit operator. `w5-lab` cell 11 phrases it as *"tools_left(trace) is not empty"*, so `len(...) > 0` works. Nothing anywhere states that an empty list is false. |
| **`or` in a condition (week 5)** | **(A), and no workaround exists** | zero `or` inside any `if`/`elif`/`while` in week 0 **and in all seven sidebars**. Week 0 teaches `and` five times and explains it (cell 80: *"Both parts must be true"*). `w5-lab` cell 11 step 5 requires it by name: *"one if with two tests joined by or."* A student cannot reach this from `and`. |
| **truthiness of a string that may be `None` (week 5)** | **(A), and week 0 drills the opposite habit** | cell 21, cell 66 (`### Asking whether a name holds nothing`) and cell 68 (*"Use `is` for `None`"*), plus five `while ... is None` loops. Nothing anywhere says a non-empty string is true and `None` is false. |
| tuple unpacking (week 5) | **(A)** | zero occurrences in week 0 and all seven sidebars. Exposed three times in pre-written cells before use, explained nowhere; the nearest thing is a docstring reading *"Hand back four things."* |

**The sharpest version of the finding, which neither the student nor I had:**
the two items with no taught workaround — `or`, and string-versus-`None`
truthiness — **land on the same line of code**:

```python
if trace["stop_reason"] or guard_says_stop(step_guard):
```

That is one line, in the cell `week00` cell 85 itself calls *"the hardest cell
in the course"*, carrying two constructs the course has never named, one of
which it has actively trained the student out of. Week 5's TODO cell prints six
of the fourteen lines verbatim, which is why nobody noticed: the student
transcribes it and it works.

The consequence is exactly what the student said: not lost points, but a
student who copies three rules nobody stated and cannot adapt them. That is the
difference between finishing and learning.

**And the course has already written the fix, twice.** `w6-lab` cell 13 says
*"Week 0 does not cover .values(), so step 1 above says what it does"*
(confirmed verbatim). `w5-sidebar` cell 10 says *"`break` is new here. Week 0
ends a loop by turning its test false."* Exactly two departures are flagged
that honestly. **Six more pass in silence:** `or`, string truthiness, tuple
unpacking, empty-list truthiness, `IndexError`, and a variable inside a literal.

### 2.10 "The command line", reported three times — **not a course defect**

**Verified.** `week00` cell 2 lists the command line among things the student
does not need. The student's access method *was* a command line. That is the
harness, and the student itself flagged it. `content/pages/course-material.md`
line 25 and `canvas-and-tech-support.md` line 25 both correctly promise a
browser and nothing installed.

---

## 3. The paste-your-key design

### 3.1 The design itself is sound, and the record of it is exemplary

**Verified.** `docs/jupyterlite-notebook-port.md` section 4 records the
decision, names the rule it overrides (build prompt lines 341-345, *"never
type, paste, see, or screenshot a key"*), invokes the documented fallback the
brief allows, and lists what makes it survivable: a LiteLLM virtual key rather
than the provider credential, its own budget, rate limit and expiry, scoped to
two models with no admin route.

That is correct, and the blast radius really is one student's allowance. The
student's whole course cost $0.0106 of $2.00. I have no objection to the
design. My objections are to what happened to the course text afterwards.

### 3.2 The memo's own action item was not completed, and four places still say the opposite

Section 4 of that memo states the required follow-up: *"Any instruction that
says a key is injected, or that a screenshot must never show a key, needs
rewording."* Four places still say it. **Verified:**

| where | what it says |
|---|---|
| `content/pages/glossary.md:27` | "The course sets it for you and never shows it." |
| `content/pages/support-resources.md:17` | "The course sets it for you." |
| `content/pages/support-resources.md:45` | "No page, cell or screenshot in this course ever shows one. **If you think a key has appeared on your screen, email your instructor and post it nowhere.**" |
| `lab/notebooks/w1-lab.ipynb`, cell 1 | "Your API key is placed in this notebook for you. **You never type it**, and no cell in this course prints it." |

The instructor's report found the first. The other three are new here, and the
last two are the serious ones.

- **`support-resources.md:45` tells a student that seeing their key on screen
  is an incident.** Every student sees their key on screen, in cell 2, every
  week, by design. The page instructs them to email the instructor about it.
- **`w1-lab.ipynb` cell 1 contradicts cell 2 of the same notebook.** Cell 1
  says "You never type it." Cell 2, the next cell, says
  `PASTE YOUR KEY BETWEEN THE QUOTES ON THE NEXT LINE`. This is the first
  notebook a student opens after week 0, and the contradiction is one scroll
  apart. It is also byte-identical in
  `instructor/solutions/w1-lab-solution.ipynb:57`.

**Asserted:** for a first-time student, a flat contradiction between two
adjacent cells in the first graded notebook does more damage than the security
exposure does. It teaches that the course's own instructions cannot be trusted
at face value, in week 1, which is precisely when a beginner most needs to take
instructions at face value.

### 3.3 The one week without the warning is the week the student first pastes a key

**Verified, and this is the finding I would fix first in this section.** Six of
the seven lab assignment pages carry this paragraph verbatim:

> Don't screenshot the configuration cell. Your key is pasted into it, so a
> picture of that cell shows your key to anyone who sees it. Screenshot only
> the cell this assignment names. If your key does end up in a post or an
> image, tell your instructor so it can be replaced.

`content/assignments/w2-lab.md:45`, `w3:52`, `w4:51`, `w5:54`, `w6:51`,
`w7:53`. **`content/assignments/w1-lab.md` does not have it.** Week 1 instead
carries a narrower, positive assurance at line 44: *"That cell prints no key
material, so it's safe to capture."*

That assurance is true and it is careful work. But it says one cell is safe; it
does not say any cell is unsafe. Week 1 is the only week in which the student
has never handled a key before, has just been told by cell 1 that they never
type one, and is being asked for a screenshot for the first time. It is the
week that most needs the warning and the only week without it.

### 3.4 The safety instruction that cannot be followed

**Verified.** `content/pages/using-the-notebook-server.md:30` says *"Never put
it in a discussion post, an email, or a screenshot."* `communicating-online.md:32`
says *"Never post an API key either."* Both good.

But the course also asks students, seven times, to attach an exported file
downloaded from the notebook drive, and `backup_my_work()` bundles **every
`.ipynb` in the drive root** into a zip the student is told to keep on "your
college drive or a USB stick". The backup zip contains `w1-lab.ipynb` with
`API_KEY = "..."` saved in cell 2. Nothing anywhere says so. The submitted
`.txt`/`.json` artifacts are clean — I checked `save_artifact()` — so the
submission path is safe. The *backup* path is where a key leaves the browser,
and it is the path the course actively instructs.

**Asserted, low severity, easy fix:** two lines in `backup_my_work()`'s printed
output — "this zip holds your notebooks, and your key is in them; keep it where
you would keep a password."

### 3.5 Verdict

As a **safety** design: acceptable, well-reasoned, correctly scoped, honestly
recorded. As a **beginner-experience** design: currently poor, not because of
the paste but because the course text was never brought into line with it, and
the residue actively misinforms in four places, one of which is inside the
notebook itself.

---

## 4. Accessibility

Scope: fourteen videos, 60 Canvas pages rendered from markdown, and fifteen
notebooks served as JupyterLite. This section combines my own reading with a
commissioned audit that measured things I could not by hand — per-scene
narration coverage, caption-to-narration equivalence across all 615 cues, and
the built HTML artifacts rather than the source.

**A correction to my own method.** My first pass read the markdown and inferred
what Canvas would receive. That was wrong and produced four findings that do
not survive. The course does not ship markdown; it ships HTML from
`tools/blocks.py` and a cartridge from `tools/cartridge.py`, and **both were
written by somebody who knew the criteria by number.** Everything below marked
verified was checked in the renderer, in the built output, or computed.

### 4.1 What is already right, and it is a great deal

**Tables — 1.3.1 (A). Compliant, verified.** Because `blocks.py:129` raises on
any text outside a `:::` block, **every one of the 102 tables in the course
necessarily passes through `_accessible_tables()`** (`blocks.py:266`), which
adds a `<caption>` from the block heading, `scope="col"` on every head cell,
and `<th scope="row">` on the first cell of every body row. Zero tables lack a
caption; zero empty `<th>`; no layout tables. The `::: keyfacts` empty header
row — the one thing I had flagged as at risk — **is detected and removed**
(`blocks.py:297-307`), for the stated reason that empty `<th>` cells are *"what
every accessibility checker flags and what a screen reader announces as
nothing."*

**Colour — 1.4.1 (A). Compliant, verified, and unusually thorough.** Callout
severity is carried three ways — colour, icon, and a `dp-sr-only` text label
(`blocks.py:195-234`). Decorative icons are `aria-hidden="true"` with a written
justification. And a grep for colour words (`red|green|yellow|blue|orange|grey|
highlighted in`) across `pages/`, `assignments/` and `discussions/` **returns
nothing at all**.

**Images — 1.1.1 (A). No exposure.** Zero `![` and zero `<img>` in the entire
authored corpus. The only non-text content is video. Diagram alt text is
build-enforced: `tools/video/schema.py:202` fails the build with *"this diagram
has no 'alt'"*.

**Text resize — 1.4.4 (AA), on pages.** `_heading()` deliberately strips the
institutional template's `style="font-size: 14pt;"` because *"A fixed point size
ignores a reader who has set a larger default font, which is a real
accessibility problem for a real part of this audience."*

**Headings.** Zero markdown `#` headings anywhere; all headings come from block
directives. Rendered across all 60 files: levels `[2, 3]` only, one `<h2>` per
page, 362 `<h3>`, **zero skipped levels**.

**Non-ASCII: zero.** Across the content corpus *and* all 25,248 notebook source
lines. No emoji, no ✓/✗ pass-fail glyphs, no ANSI, no unicode arrows. This
follows from a prose rule in `content/AUTHORING.md:140` about dashes, and the
accessibility payoff is enormous and largely accidental.

**Timing — 2.2.1 (A). Fully satisfied.** `content/quizzes/final-exam.yaml:43`:
*"THERE IS NO time_limit KEY, on purpose."* Plus
`one_question_at_a_time: false`, `cant_go_back: false`, unlimited self-check
attempts, and no proctoring or lockdown browser anywhere. That combination
removes an entire class of accommodation request before it is made, and it is
worth naming because nobody ever gets credit for it.

### 4.2 Video — an excellent pipeline with two Level A defects at the last step

**Captions, 1.2.2 (A): compliant, and verbatim by construction.** The audit did
not take the pipeline's word for it: it concatenated every `narration` cue from
all 14 scene lists, concatenated every cue in all 14 built `.vtt` files, and
compared. **All fourteen are byte-identical after whitespace normalisation, 615
cues.** The same string is fed to the TTS and written to the caption file;
there is no transcription step to drift. `blocks.py:257` emits
`<track default kind="captions" label="English" srclang="en">` — selectable,
default-on, not burned in — with the attribute set checked against Canvas's own
sanitizer allowlist rather than guessed.

Cue quality: zero cues under 1 second, zero lines over 42 characters, 150-177
wpm. Two small defects — two three-line cues (`w4-walkthrough.vtt` at 2:42,
`w6-walkthrough.vtt` at 2:20) that slipped past a `CAPTION_LINES = 2` guard,
and cues that split mid-phrase because `_split_evenly` balances by character
count rather than clause. Neither is a conformance failure.

**Contrast, 1.4.3 / 1.4.11 (AA): compliant, gated, and measured.**
`check.py:69` is a build gate — *"A palette edit must not quietly drop the
slides below WCAG AA"* — with a correct sRGB luminance implementation. Computed
from `builder/content/video/theme.css`: `--ink` on `--ground` **16.88:1** (gate
7.0), `--mute` **5.81:1**, `--accent` **6.21:1**. Text on `--wash`, which is
ungated, passes anyway at 15.60 / 5.37 / 5.74. The terminal palette in
`tape.py`, also ungated, passes throughout — worst case yellow at **5.27:1** —
and every `bright*` variant is set identical to its normal variant so nothing
can land in a low-contrast zone.

**And now the two defects, both Level A, both verified in the built artifact.**

The course has two build paths, and **they disagree.** `tools/cartridge.py:341`
writes each transcript correctly, with `<html lang="en">` and
`<title>Transcript: w1 overview</title>`. `builder/canvas/build_course.py:383`
— the path `builder/STATE.md:242` describes as the one in use — writes:

```html
<!doctype html><meta charset=utf-8><title>w1-overview.transcript</title><h1>...
```

- **No `<html>` element, therefore no `lang`. WCAG 3.1.1 Language of Page (A):
  FAIL.** `grep -l 'lang=' build/video/*.transcript.html` returns **0 of 14**.
- **`<title>` is a filename. WCAG 2.4.2 Page Titled (A): FAIL.** The human
  title sits three characters later in the `<h1>` and is simply not used.

These are the most serious conformance defects in the course, precisely because
**the transcripts are the text alternative for the video.** The fix is three
lines: copy what `cartridge.py:341` already does.

**Audio description, 1.2.5 (AA): FAIL, and it is measurable.** WCAG 1.2.3 (A)
*is* satisfied — `assemble.write_transcript()` produces a genuine media
alternative including diagram alt inline, slide body text with code fencing
intact, and compare panels split rather than left as a raw pipe. Its docstring
names the standard. But 1.2.5 at AA asks for description of visual information
not in the audio, and the audit measured the gap: for each of the 94 scenes it
computed what fraction of on-screen content words appear in the narration.
**23 of 94 scenes fall below 55 percent.** The nine `layout: code` scenes are
unambiguous failures:

- `content/video/w7-walkthrough.yaml:22-41`, **14 percent**. The slide shows a
  ten-line triage report — `Verdict: benign / Confidence: 0.85 / Indicators:
  SPF result: pass; ...`. The narration is *"Here's one note from that run. Six
  lines, in the order the template sets."* Not one value is read aloud.
- `content/video/w3-walkthrough.yaml:22-38`, **14 percent**. The slide is the
  entire phishing email body. The narration says *"Here's the entire message.
  Two hundred and fifty-one characters. **Read what isn't in it.**"* — an
  instruction that cannot be followed without sight, which is also a 1.3.3
  problem.
- `w3-walkthrough.yaml:56`: *"Then this line. The name belongs to the company.
  The address doesn't."* One of four items, unidentifiable by ear.

**The cheapest remediation is not an audio-description track.** It is rewriting
nine narrations to read what is on screen, which improves the video for
everybody watching on a phone or with the picture off.

**A gate that cannot fail.** `check.py:126`, labelled *"captions cover the
audio"*, checks only that the last cue ends within 3 seconds of the ffprobe
duration. It validates no reading rate, no cue count, no overlap, and not that
the text matches the narration — **a single cue spanning the whole video would
pass.** Worse, line 138 does `float(subprocess.run([...]).stdout.strip() or 0)`:
if ffprobe is missing or errors, duration becomes `0`, the comparison is false,
and **the gate passes silently on every video.** That is the exact
silent-failure shape this codebase elsewhere works hard to eliminate. (The
underlying reality is fine — measured uncaptioned tails are 0.30 to 0.41
seconds of trailing silence.)

**A dead variable.** `content/video/theme.css:53` and `:105` both use
`var(--dim)`, and `--dim` is defined nowhere. The declaration is invalid at
computed-value time, so **the progressive-reveal dimming does not happen at
all** across 17 numbered and 6 diagram scenes. It fails safe for contrast, and
the one colour nobody checked is the one that does not exist.

### 4.3 The screenshot requirement — the sharpest finding in the review

**Verified, and the audit found the part that makes it indefensible.**

Six of the seven lab assignment pages instruct: *"If the rows don't fit,
**lower your browser zoom** and capture again"* — `w1-lab.md:44`, `w3:46`,
`w4:45`, `w5:44`, `w6:45`, `w7:47`. Week 6 adds *"Don't crop a row"* over an
eleven-row seven-column table. All require **one image**.

**And two rubrics then deduct points for the result.**
`content/rubrics/w1-lab.yaml:47` grades the screenshot *"present and
readable"*. `content/rubrics/w6-lab.yaml:96` scores a band as *"One is hard to
read... or the text is small."*

So: the course tells a student to shrink the output, and then penalises them
for the text being small. A low-vision student browsing at 200 percent is being
instructed to defeat their own accommodation and is graded down when they
comply. The tables **cannot** fit at 400 percent zoom by construction — the
week 6 rule is 88 characters and the week 3 rule is 104, against roughly 38
visible characters.

Three criteria are engaged:

1. **1.4.4 Resize Text (AA)** — the instruction is the violation.
2. **1.4.10 Reflow (AA)** — untested at 320 CSS px, but arithmetically hopeless.
3. **1.1.1 Non-text Content (A), inverted** — an image is the sole graded
   evidence, graded on visual qualities, with no equivalent alternative offered
   anywhere. A blind student cannot produce it, verify it, or know whether they
   earned the points.

And **the course never explains how to take a screenshot.** Verified by
exhaustive search of `content/` and `lab/`: zero occurrences of "Print Screen",
"PrtScr", "Snipping", "Shift-Command-4" or "screen capture". The stated
audience has completed no other technology class, and at least 65 of 700 lab
points ride on the skill.

**The content being captured is plain text.** One line per assignment page
closes all of it at zero cost to what is actually assessed:

> If a screenshot is difficult for you, paste the cell's printed output into a
> text file and attach that instead. It carries the same information and scores
> the same.

### 4.4 The notebooks

**Clean, verified with hard counts:** zero box-drawing characters, zero
non-ASCII of any kind, zero ANSI, zero `colorama`/`rich`, no images, no
pre-rendered outputs, no `tqdm`/`ipywidgets`/`clear_output`/`\r` — so no
churning live region for a screen reader to fight. 154 ATX headings, no skipped
levels. **WCAG 1.4.1 has no findings in the notebooks at all.**

**The real finding: nine space-aligned stdout tables — 1.3.1 (A).** Each prints
a header row and then unlabelled data rows. A screen reader collapses
whitespace, so a row reads as an unpunctuated string with no association to a
header far back in the buffer. **Seven of the nine are the cells the rubric
names for the screenshot.** The worst is `w6-lab.ipynb` course cell 16 —
seven columns, eleven rows — which reads aloud as *"013 body malicious benign
True injection detected 1420"*. **A blind student cannot tell which verdict was
the defended one**, which is the entire point of week 6.

Two things make this an inconsistency rather than house style. 93 label/value
prints across the notebooks terminate the label with a colon before padding, so
the colon carries the relationship. And `w5-lab.ipynb` cell 13 is the one
screenshot cell with no padded table, because it delegates to `show_trace()`,
which labels every field. That is the model the other six should copy.

There is a sharp irony: `blocks.py:266-282` contains the team's own correct
statement of exactly this defect — *"A screen reader then has no way to tell
which header belongs to which cell, which turns a comparison table into a flat
list of words"* — written for Canvas HTML and never applied to stdout.

**Mouse gestures with no keyboard alternative — 2.1.1 (A), 2.5.7 (AA).
Count: 46.** Four strings live in every lab's byte-identical helpers cell
(*"right-click it, choose Download"*, *"Drag it into the file list first"*),
plus `using-the-notebook-server.md:23` (double-click, step 3 of the first thing
a student ever does), `:39` (right-click, the backup procedure), `:45` (drag),
and `assignments/w1-lab.md:45` inside a graded submission instruction.
JupyterLab has a keyboard route for each; none is mentioned.

**And one that lands directly on section 1 of this report.** Fourteen of
fifteen notebooks pair the mouse verb with the keystroke — *"Click a cell, then
press Shift and Enter."* **`w1-lab.ipynb` cell 0 is the exception.** It says
only *"Run the cells in order, from the top"*, with no method at all. It is the
first graded lab in the course.

**Keyboard documentation, complete inventory across the whole tree:** `Ctrl+S`,
`Ctrl+F` for the glossary, `Shift+Enter` in 14 notebooks. That is all. Not
documented anywhere: Esc/Enter for command versus edit mode, arrow-key cell
navigation, Ctrl+Enter, Alt+Enter, or the shortcuts palette. A keyboard-only
student is told how to *run* a cell and never how to *reach* one.

**"accessibility", "screen reader", "assistive technology", "WCAG", "508",
"low vision", "magnification": zero occurrences in any student-facing file.**

**No JupyterLite configuration exists in this repo** — no `index.html`, no
`jupyter-lite.json`, no `overrides.json`. The served page's `lang`, `<title>`,
theme and font all come from stock upstream and are outside this repo's
control.

### 4.5 Program access, which is the largest institutional risk here

**There is no disability-services or accommodations statement anywhere in the
course.** `content/pages/course-policies.md` is 100 lines and is the syllabus
body (`course.yaml:35`); it covers grading, privacy, late work and AI use, and
carries no accommodations paragraph. For an Alamo Colleges syllabus that is a
required element, and it is a Section 508 / program-access exposure independent
of any WCAG criterion. **This is the cheapest and highest-value item in the
whole review: one paragraph.**

Related: there is **no VPAT or accessibility disclosure for
notebook.bashtion.dev**, which is where the graded work happens.

### 4.6 Prior work that should be recovered before anyone starts

`builder/docs/course-review-2026-09-07.md:19` lists
`scratchpad/review-accessibility.md — 6,600 words`. That directory is
gitignored and no longer exists on disk, its findings appear nowhere in
`STATE.md`, and `STATE.md` mentions accessibility nowhere at all. **Recover it
before commissioning remediation** — it may already contain much of the above.

**No accessibility checker has ever been run against this course.** No UDOIT
artifacts, no axe or WAVE output, no scan of the `.imscc`. And no gate in
`tools/preflight.py` checks accessibility, though at least five of the findings
below are greppable.

### 4.7 Ranked, with the split I was asked for

**Level A, verified, three lines in one file:**

1. All 14 transcript HTML files have no `lang` — 3.1.1. `build_course.py:383`.
2. All 14 transcript `<title>` values are filenames — 2.4.2. Same lines.
   `cartridge.py:341` already does both correctly.

**Level AA, verified:**

3. **1.2.5 Audio Description** — 23 of 94 scenes below 55 percent narration
   coverage; nine `layout: code` scenes near zero.
4. `pages/w1-wrap-up.md:27` — *"The answers are right below them, so cover them
   first"*, with `**Answers.**` at `:35` as bold rather than a heading. A
   screen-reader user has the answers read to them in sequence with nothing to
   cover and no heading to skip past. **1.3.3 / 1.3.1.** Week 1 is the only
   wrap-up that does this; the other seven interleave each answer under its
   question. Making w1 match them is the whole fix.
5. `pages/w6-content.md:47` *"Read that middle column again"*; `glossary.md:10`
   and `:14` *"the last column"* — **1.3.3**.
6. Nine space-aligned notebook tables, seven of them graded screenshot cells —
   **1.3.1**.
7. 46 mouse-only instructions — **2.1.1, 2.5.7**.
8. 37 empty `<td>` cells, 31 of them the "Due" column of the weekly Tasks
   tables — **1.3.1**. One word each.

**Program access, higher institutional risk than anything above:**

9. **No accommodations statement in the syllabus.** One paragraph.
10. **The screenshot requirement** (4.3), including two rubrics that penalise
    the result of the instruction the course gives.
11. No VPAT for the notebook host.

**Tooling:**

12. `check_captions` validates only an end timestamp and passes silently if
    ffprobe fails.
13. `--dim` used and never defined; the reveal dimming is inert.
14. Every block heading is a hardcoded `<h3>`, so a multi-part page such as
    `w7-content.md` renders 15 flat siblings and a screen-reader user cannot
    tell which subsection belongs to which part.
15. `scope="row"` applied unconditionally yields meaningless numeric row headers
    in six tables.
16. No accessibility gate in `tools/preflight.py`.

### 4.8 Untested, and the test that settles each

These cannot be settled from files, and the first two would silently disable
the two things the course did best.

1. **Does the caption track load in production Canvas?** `<track src>` points at
   a `download_frd=1` file URL, which on Instructure-hosted Canvas 302s
   cross-origin to a signed files domain. **A cross-origin `<track>` with no
   `crossorigin` attribute fails to load silently, taking the captions with
   it.** It works locally because everything is same-origin. *Test:* publish,
   open a page, confirm the CC button offers English and shows text.
2. **Does the transcript link open, or download a file?** Same URL shape;
   `download_frd=1` forces `Content-Disposition: attachment`. *Test:* click it
   in the built course.
3. **Does DesignPLUS define `.dp-sr-only`?** If it does not, the words
   *"Warning."* and *"Stop. Read this before going further."* render **visibly**
   on every callout in the course. *Test:* publish one page per callout flavour
   and look.
4. **Does JupyterLite announce cell output at all?** The output area is not an
   ARIA live region by default, and `w7-lab.ipynb` cell 10 runs for minutes.
   *Test:* NVDA/Firefox and VoiceOver/Safari against notebook.bashtion.dev.
5. **Is a 977-line CodeMirror cell (`w7-lab.ipynb` cell 4) navigable by
   keyboard?** *Test:* VoiceOver, reach cell 5 from cell 3, and time it.
6. **Do the padded tables survive 400 percent zoom or a 320px viewport
   (1.4.10)?** *Test:* the w6 screenshot cell at 400 percent on a 1280px window.
7. **Is the Canvas course Language field set?** `course.yaml` sets no locale.
8. **Does the served JupyterLite page set `lang` and a real `<title>`?**
   *Test:* `curl -s https://notebook.bashtion.dev/ | grep -o '<html[^>]*>'`.
9. **Is the 2019-2020 institutional handbook PDF at
   `pages/academic-integrity.md:31` tagged?** The page instructs *"It starts on
   page 43"*, which is unfulfillable in an untagged PDF.
10. **Is the Spanish half of email 031 marked `lang="es"` where a student reads
    it?** Almost certainly not — it prints as plain text. **3.1.2.**

### 4.9 Summary

The page-and-video engineering is better than any course library I have
audited: tables, colour, icons, resize, captions, contrast and timing are all
compliant, most of them gated, and several of them documented with the criterion
number in the comment.

**Three things would fail a complaint today**, and none of them is about the
platform. They are the two Level A transcript defects (three lines), the
audio-description gap on nine code slides (nine narration rewrites), and the
screenshot requirement (one line per assignment page). **The missing
accommodations statement is not a WCAG matter at all and is the single cheapest
and most consequential fix in this report.**

The screen-reader question on JupyterLite remains the one unknown whose cost
cannot be estimated. Given the standard of everything else, that gap is
conspicuous rather than characteristic — and the build brief
(`docs/build-prompt-v1.3.md:438`) explicitly scoped it out and asked for it to
be entered in the risk register. It should now come off that register.

---

## 5. Loss of work

### 5.1 The instruction does not work in any of the fifteen notebooks

The instructor's report says the backup routine fails in 8 of 15 notebooks. It
is worse than that. **Verified by inspecting all fifteen:**

`using-the-notebook-server.md:37` says: *"Run the last cell of the notebook. It
builds a backup file and prints its name."*

- **All fifteen notebooks end with a markdown cell.** In a notebook, running a
  markdown cell renders it and produces no output. A beginner who follows this
  instruction literally clicks the last cell, presses Shift+Enter, sees the
  text render, and gets nothing. There is no error, no message, and no file.
- In the seven lab notebooks the backup call is in the **last code** cell —
  `w1` cell 14 of 15, `w2` 15 of 16, `w3` 15 of 16, `w4` 16 of 17, `w5` 17 of
  18, `w6` 18 of 19, `w7` 16 of 17 — always with exactly one markdown cell
  after it.
- In the other eight — `week00-python-on-ramp.ipynb` and all seven sidebars —
  **`backup_my_work`, `restore_my_work` and `budget_left` are not defined at
  all.** Calling them raises `NameError`, which is the first row of the six-error
  table the course spends thirty minutes teaching a beginner to fear.

So the instruction is off by one in seven notebooks and impossible in eight,
and the silent-failure mode in the seven is worse than the loud one in the
eight, because the student concludes the backup worked.

### 5.2 Week 0 is the largest block of unprotected work in the course

**Verified.** Week 0 is 130 cells, ~6,900 words, 11 "You try" exercises, and a
stated 4 to 6 hours — the single longest sitting the course asks for. It has no
backup cell, and the only page that tells a student their work is fragile is
the page whose protective instructions do not work there.

`using-the-notebook-server.md:14-17` is a box marked Warning:

> Nothing you write is kept at the college. It sits in the browser you used, on
> the computer you used. Clear your history, switch browsers, or sit at a
> different machine, and your work won't be there.

That warning is correct, well-placed and well-written. It is also incomplete in
one specific and important way.

### 5.3 The fourth way to lose everything, which is automatic and on the course's own schedule

**Verified externally.** JupyterLite persists notebooks in browser storage via
localForage, which selects IndexedDB where available. WebKit's Intelligent
Tracking Prevention deletes **all script-writable storage — IndexedDB,
localStorage, service worker caches — after seven days without user interaction
with the site.** This has been WebKit behaviour since Safari 13.1 / iOS 13.4.

The course's own cadence is Monday-to-Sunday with everything due Sunday
11:59 PM (`welcome-start-here.md:9`, `course-schedule.md:8-9`). A student who
does their lab on Sunday and returns the following Sunday is **exactly on the
seven-day boundary.** A student who takes a week off — which the course
explicitly permits and encourages, `course-schedule.md:17-19`, *"if you fall
behind, you can still open any week"* — is past it, and their entire term's work
is gone with no warning and no error.

Safari is the default browser on every Mac. The course tells students what
computer they need (`canvas-and-tech-support.md:16-19`) and never tells them
what browser.

The warning box names three ways to lose work — clear your history, switch
browsers, change machine — and none of them is this one, which is the only one
that happens **without the student doing anything at all.** The box also names
the wrong action for one of the three it does list: in Chrome, clearing
*history* does not clear IndexedDB; clearing *cookies and other site data*
does. A student who reads "clear your history" as the hazard, and then clears
site data believing that is something different, loses everything.

### 5.4 Modelling the cost

**Asserted, with the mechanisms above verified.**

| scenario | what is lost | likelihood over an 8-week term |
|---|---|---|
| Safari/WebKit 7-day eviction after a missed week | everything | high for any Safari user who skips a week; the course invites skipping |
| College loaner laptop returned (offered at `canvas-and-tech-support.md:47`) | everything | certain for the students who need it most |
| Shared/lab machine with an auto-clear policy | everything | moderate |
| Student clears "cookies and site data" for an unrelated reason | everything | moderate |
| Week 0 work, in every scenario above | 4-6 hours, unrecoverable by any documented route | whenever any of the above happens before week 1 |

**My estimate: 10 to 20 percent of a real cohort loses non-trivial work at
least once**, and the students it happens to are disproportionately the ones on
borrowed or shared hardware — the same students least able to absorb it. The
severity is total rather than partial, because the loss is per-origin, not
per-file.

Mitigations, cheapest first, none of which requires re-architecting anything:

1. Move `budget_left`, `backup_my_work` and `restore_my_work` into a shared
   first cell that **every** notebook carries, including week 0 and the seven
   sidebars. (This is the instructor's item 8 and I agree with it.)
2. Change `using-the-notebook-server.md:37` from *"the last cell"* to *"the
   last cell that has code in it — the one that writes your file"*, and add a
   week 0 backup cell.
3. Add a fourth line to the warning box naming the automatic case: *"Safari and
   other Apple browsers delete this kind of storage after seven days without a
   visit. If you use Safari, back up every week without fail, or use Chrome,
   Edge or Firefox for this course."*
4. Have the notebook itself nag. `backup_my_work()` already knows the date;
   a config-cell check that prints *"Your last backup was 9 days ago"* costs
   nothing and reaches the student where they are.

---

## 6. Time and money

### 6.1 The 42-hour figure, and why I think it is optimistic

**Verified arithmetic.** Summing the seven weekly time tables plus week 8:
272 + 310 + 292 + 285 + 310 + 308 + 287 + 90 = **2,154 minutes = 35.9 hours**.
Add week 0 at 4 to 6 and the published figure is **40 to 42 hours**. That
matches the "42" in the instructor's report and the "under 6 hours a week"
promise, which appears on `welcome-start-here.md:11`,
`course-schedule.md:10 and 53`, `tips-for-success.md:8`, `week-0-overview.md:26`
and in `week00` cell 0.

**Verified.** `docs/build-prompt-v1.3.md:387` sets the constraint: *"3 SCH
delivered in an 8-week Flex session, but hold actual student time to under 6
hours per week."*

Two observations.

**First, the estimates contain no debugging.** Only week 2 has a line item for
it (40 minutes). Weeks 1, 3, 4, 5 and 6 give a single undifferentiated lab
number. The student that produced the 31-hour figure debugged nothing at all —
thirteen of fourteen TODOs correct on the first attempt — and *still* spent 195
minutes on the week 1 lab against a 150-minute budget.

**Second, and this is where I part company with the instructor's report.** That
report concludes: *"read 42 hours as realistic for a real beginner, not
generous."* I do not think that follows.

The inference is: an expert took 26 hours on the assigned work, the course says
42, therefore 42 has enough headroom for a novice. But the gap between an
expert and a novice on introductory programming is not a 1.6x multiplier; on
debugging specifically it is the largest individual-differences effect in the
literature on novice programmers, and it is measured in multiples, not
percentages. A student who cannot yet read `AttributeError: 'NoneType' object
has no attribute 'startswith'` does not spend 1.6 times as long on that cell as
one who can. They spend an evening, or they stop.

**My estimate for a genuine novice who completes the course: 65 to 85 hours,
week 0 included.** That is 8 to 11 hours a week, not "under 6".

Set against the credit award, that number is not alarming — it is closer to
correct. **3 SCH under the federal credit-hour definition is about 135 hours of
student work**, and the course as published budgets roughly a third of it. So
the honest reading is not "the course underestimates"; it is that **the course
is budgeted to a workload cap that is well below what its credit award
implies**, and a novice's real experience will land between the two.

**Asserted, and this is the beginner-experience consequence, which is what I
was asked about:** the published number is the one a student uses to decide
whether they can take this course alongside a job and a family. When it is off
by 50 to 100 percent, the student does not conclude that the estimate was
wrong. They conclude that they are slow, and slow students withdraw. Expectation
violation in week 2 or 3 of a compressed session is a stronger withdrawal
driver than difficulty is.

I am **not** recommending inflating the published figure — that has its own
cost, and the 6-hour cap is an instruction from above. I am recommending one
sentence per lab estimate, of the kind week 2 already models:

> These minutes assume the code works the first time. Most people spend an
> extra hour or two on their first two labs. That is normal and it does not
> mean you are behind.

That is free, it is true, and it converts an expectation violation into a
prediction the course made and kept — which is the thing this course does
better than any I have read (see 7.3).

### 6.2 "Give it two sittings"

**Verified via the student.** That phrase sits on the week 5, 6 and 7 overview
pages beside lab estimates of 180, 180 and 165 minutes, and the student found
that none of the three needed two sittings, because in all three the TODO cell
prints most of the answer. For a novice the warning may well come true — but
for the wrong reason, and it is attached to the three weeks with the most
scaffolding rather than to week 1, which has the least.

**Asserted:** move it to week 1.

### 6.3 Money

**Verified.** The whole course, including the student's own extra measurement,
cost **$0.0106 of a $2.00 budget** — about 190 times headroom. The design that
produces that is genuinely good and worth naming: week 0 requires no key and
spends nothing (`week-0-overview.md:13`, *"A browser and the notebook server.
No key"*); `budget_left()` is proven free in both spend and rate limit
(`docs/jupyterlite-notebook-port.md` 6.3, measured, with a control); week 5's
cell 13 runs the loop with the cap set to zero specifically so a student who
wrote the `while` line wrong is stopped at a cost of nothing.

**Does the budget framing help or scare?**

**Asserted: on balance it helps, with one exception.** The number a student is
told to watch is $0.25, and everything they will ever spend is a fortieth of
it. The framing is concrete, it is always available, and it is one of the few
places in an intro course where a student can see a real operational constraint
and find that they are nowhere near it. That builds confidence rather than
anxiety.

The exception is the **first** encounter. `using-the-notebook-server.md:32`
tells a student to *"Run `budget_left()`"* — with parentheses that mean
something — on the fourth page of the orientation, before the course has
explained what a function is, what a call is, or what a notebook cell looks
like. The glossary marks **Call** and **Function** as first used in week 0,
i.e. after this page. And in week 0, where the student is standing, that call
raises `NameError`. So the student's first experience of the cost machinery is
being told to type something they do not understand, which then fails.

That is the whole of the scare, and fixing 5.4 item 1 fixes it too.

---

## 7. What this course does unusually well

I want to be as specific here as in the rest, because several of these are
better than anything I expected and two of them are things I would copy.

### 7.1 The plain writing holds up, and it holds up where nobody is checking

**Verified.** `tools/readability.py` over `content/`: **59 enforced pages, mean
Flesch-Kincaid grade 3.72 against a limit of 8.0 and a target of 7.0. Every
page inside its length budget.** The lowest is `w4-overview.md` and
`w3-discussion.md` at 2.58 and 2.45; the highest student page is
`course-material.md` at 5.23.

The part that impressed me is that **it holds on the surfaces the gate cannot
see.** I ran the same measurement over the notebooks, which are outside the
gate entirely: week 0's markdown is grade 2.08 across 6,193 words; `w1-lab`'s
markdown is 2.29; the code comments, which are where the TODO instructions
live, run 3.9 to 4.3 across all seven labs. Nobody was checking and the
discipline held anyway. That is a property of the author, not of the tool, and
it is the single best thing about this course.

Two honest caveats. Grade level measures sentence length and syllables; it does
not measure conceptual load, and a grade-3.7 page containing "SPF", "DMARC",
"prompt injection" and "allowlist" is easy to read and not easy to understand.
And section 1.6 documents the one way optimising for that number makes a page
worse.

### 7.2 The error-handling is written for the student, not for the developer

**Verified in `w1-lab.ipynb` cell 4.** `send_request()` handles a 429 by
waiting, *saying* it is waiting, and saying *"Nothing is broken"*; handles a 401
by naming the exact fix ("the key goes between the two quotation marks, with no
spaces around it"); strips `<think>` blocks so the student never sees a model's
reasoning; fills a placeholder so the notebook keeps running and still writes
the submission file when the service is down; and prints the full
troubleshooting list once per session rather than six times. There is a comment
explaining *why* the retry waits rather than advising ("the only fix is to
wait, so this waits for you rather than printing advice you cannot use").

I have not seen better in a course codebase.

### 7.3 It predicts its own failures out loud, and then they happen

This is the pattern I would take away and use elsewhere.

- **`week00` cell 53**, on `return` versus `print`: *"This is the most common
  mix-up in the course. It breaks week 1 on the first cell."* Named, one
  notebook in advance, correctly.
- **`week00` cell 55**: *"Section 10 shows you that exact error."* It does.
- **`week00` cell 100**, on why the demonstration cells use bare
  `except Exception:` when section 9 just told the student not to. The notebook
  catches itself contradicting itself and explains the exception rather than
  hoping nobody notices.
- **Week 6's walkthrough video reports its own demonstration failing, with
  counts.** For a security course, where the professional habit being taught is
  "report what you measured, not what you hoped", that is the right thing
  modelled at the right moment.
- **Week 7's split detector says out loud which case it cannot decide**: *"This
  run made no wrong calls, so both error counters are zero... It also means
  this cell cannot tell whether your two error branches are the right way
  round."*
- **Week 6's readings end with a table saying which risks are answered by code
  and which two are not** — *"No version of your notebook will make them code.
  That's the honest end of this page."*

A course that tells a beginner in advance what is about to go wrong, and is
right, buys trust that it can then spend. This one earns it repeatedly. Every
recommendation in section 6.1 is really just an instruction to spend more of it.

**And it does the same thing for its own gaps, twice.** `w6-lab` cell 13:
*"Week 0 does not cover `.values()`, so step 1 above says what it does."*
`w5-sidebar` cell 10: *"`break` is new here. Week 0 ends a loop by turning its
test false. `break` ends one part way through a pass."* Both are one sentence,
in the cell where the gap lives, and both are the correct fix for every item in
section 2.9. The course wrote the template; it just has not applied it six more
times.

### 7.4 Week 7 is the model, and I confirmed it independently

**Verified.** The student called week 7 the only lab with no Python gap. It
checks out. Every ingredient of both TODOs traces to a named source: the
triple-quoted f-string to `week00` cell 45 (which forward-references week 7 at
cell 49 — *"In week 7 you fill a six-line note"*); the single-quoted key inside
double-quoted f-string braces to cell 74 and to `w7-sidebar` cell 6, which
states the quoting rule; if/elif/else and the counter-then-divide pattern to
section 7 and cells 74-76; and `w7-sidebar` cell 5 is structurally the same
function as TODO 2.

One qualification: `truth[row["email_id"]]["verdict"]` subscripts a dictionary
with a *computed* key, which week 0 never does — every week 0 dict subscript
uses a literal string. It is taught, in `w3-sidebar` and `w5-sidebar`, which is
the course's own model working correctly; it just is not week 0.

Week 7's TODO cells print no code at all — six values named in order, six steps
in English — and they are the answer to section 2.9. Whatever is done about
week 5, this is the shape to copy.

### 7.5 The five-step error routine, repeated in four places

**Verified.** The identical five steps appear in `week00` cell 1 (the first
thing a student reads), `week00` cell 97 (the full treatment),
`if-something-breaks.md:15-21` (a standalone Canvas page), and
`tips-for-success.md:23` (in prose). For a beginner, the single most valuable
thing a course can do is make one small routine unavoidable, and this one is.
My criticism in 1.2 is that step 3 breaks on the course's own first error — not
that the routine is wrong. It is the right routine.

### 7.6 The design decisions that protect a beginner's money and time

- **Week 0 needs no key and spends nothing.** Stated up front and true. It
  means the five hardest hours of the course carry no financial anxiety at all.
- **Week 5's cell 13 runs the loop with the cap at zero** — which cannot call
  the model — to find out whether the student's `while` line carries the cap,
  *and says why*: a loop with no cap "could call the model on every pass." That
  is a course spending an argument on protecting the student's budget rather
  than its own marks.
- **Week 4's cell 15 and week 6's cell 17 force a mechanism to fire on
  purpose**, cheaply, with the page saying in advance that it will not fire on
  its own. This is the fix for four other problems in the run, and it was
  already shipped twice.
- **`week00` breaks six cells on purpose and prints six real tracebacks**
  rather than pictures of them.

### 7.7 The accessibility engineering, which nobody was going to notice

I did not expect to put this here, and I got it wrong on my first pass by
reading the wrong layer. `tools/blocks.py` and `tools/cartridge.py` do work
that most course teams never do and no student will ever see: a purpose-built
accessible-table function that captions, scopes and strips empty header rows;
callout severity carried three ways so colour is never load-bearing; icons
hidden from assistive technology with a written justification for why that is
safe; the institutional template's fixed heading font size deliberately removed
because *"a fixed point size ignores a reader who has set a larger default
font."* `tools/video/schema.py` makes diagram alt text a **build failure**.
`tools/video/check.py` gates the slide palette at 7.0:1 for body text — AAA,
not AA.

And the caption pipeline is the best I have audited: captions are generated
from the same string the voice speaks, so they are verbatim by construction
rather than by transcription, and an independent check confirmed all fourteen
byte-identical across 615 cues.

Two things follow. The gaps in section 4 are almost all in the *last* step —
the shipped artifact, the syllabus, the rubric wording — rather than in the
design, which means they are cheap. And the standard set here is the reason the
screen-reader question is worth answering: a team that gated slide contrast at
AAA will want to know.

### 7.8 Honest about its own edges

`w8-wrap-up.md`'s "What this course did not cover" is eight bullets naming real
limits — one kind of input, one model called one way, a notebook rather than a
service, invented mail, *"twenty emails is a small measurement"*, a narrow slice
of Python on purpose, the agent's own security, and what happens after
escalation. A course that closes by telling a beginner where its own edges are
is teaching the habit it spent seven weeks describing.

---

## 8. Where I disagree with the instructor's report

Three places, in order of how much I think it matters.

### 8.1 The 42-hour conclusion

`docs/student-e2e-run-2026-09-08.md` section 7: *"so read 42 hours as realistic
for a real beginner, not generous."*

Section 6.1 above sets out the argument. Briefly: 42 is derived from a run that
did no debugging, and every weekly estimate except week 2's contains no
debugging line. The expert-to-novice ratio on debugging is not 1.6x. My figure
is 65 to 85 hours, which is *closer to* what 3 SCH implies, not further from
it. The practical consequence is not that the number should change; it is that
the course should say, in the place a student reads it, that the first two labs
usually run over — which converts a broken promise into a kept one.

### 8.2 The ordering of the worklist, for retention specifically

The suggested order of work opens with week 6's bodyless closing call (item 1,
as corrected) and the four missing export fields (item 2). Both are correct and
both should be done. But read against retention rather than correctness, the
ordering is inverted: **the students who are going to leave this course will
have left before week 6.** Week 6's defect costs a student who is still
enrolled some points and a wrong lesson. Week 1's sidebar gap, the missing
`None` guard in the week 1 check cell, and the backup instruction that does not
work in week 0 decide whether that student reaches week 6 at all.

If I were sequencing for completion rate rather than for correctness, the first
four items would be: the week 1 sidebar's missing dictionary example (1.1); the
three-line `None` guard in `w1-lab` cell 7 (1.2); the shared backup cell in all
fifteen notebooks (5.4); and the twelve broken sentences, nine of which are in
week ≤1 (1.6). Together they are perhaps three hours of work and none of them
touches a model call.

### 8.3 The screenshot criterion is not a harness artifact

Section 3 of the report files the screenshot criteria under *"Artifacts of a
one-student run, not defects... this harness cannot capture images, ten times.
A real cohort earns both."*

The harness part is right. But something real survives that the report drops,
and it is worse than either report has it. The course requires an image as the
sole evidence for 65+ points, never explains how to make one, instructs
students six times to lower their browser zoom to fit it — **and then two
rubrics deduct points because "the text is small"** (`rubrics/w6-lab.yaml:96`,
`rubrics/w1-lab.yaml:47`). The tables cannot fit at 400 percent zoom by
construction: an 88- and a 104-character rule against roughly 38 visible
characters. A low-vision student is told to undo their magnification and then
marked down for complying.

The student's own report kept the narrow version ("the course never explains
*how* to take a screenshot"); the instructor's report filed the whole thing
under "not defects". It belongs in section 1, and the fix — accept a pasted
text capture as an equal alternative, since every cell being captured prints
plain text — costs one line per assignment page and nothing at all in what is
assessed.

---

## 9. Ranked worklist, for beginner outcomes

Ordered by expected effect on the number of students who finish and on the
number who can take the course at all, not by severity of the defect.

**Under an hour, and two of them are compliance:**

1. **Add an accommodations / disability-services paragraph to
   `course-policies.md`.** One paragraph. It is a required syllabus element,
   it is absent, and it is the cheapest consequential fix in this review. (4.5)
2. **Fix the two Level A transcript defects** — `lang` and `<title>` — in
   `builder/canvas/build_course.py:383`. Three lines, copied from
   `tools/cartridge.py:341`, which already does it right. (4.2)
3. **Add the `None` guard to `w1-lab.ipynb` cell 7**, naming week 0 section 6.
   Three lines, on the first error the course produces. (1.2)
4. **Add the text-capture alternative to all seven screenshot instructions**,
   drop "lower your browser zoom", and remove "the text is small" from the two
   rubrics. Resolves 1.4.4, 1.1.1 and the missing how-to together. (4.3)
5. **Reword the four remaining "the course sets the key for you" statements** —
   most urgently `w1-lab.ipynb` cell 1 and `support-resources.md:45` — and add
   the week 2-7 screenshot warning to `w1-lab.md`. (3.2, 3.3)
6. **Add "Click a cell, then press Shift and Enter" to `w1-lab.ipynb` cell 0**,
   which is the one notebook in fifteen that omits it, and is the first graded
   lab. (4.4)
7. **Fix the twelve broken contractions**, nine in the first week's material
   and one narrated aloud. (1.6)
8. **Rewrite `w1-wrap-up.md:27` to interleave its answers**, the way the other
   seven wrap-ups already do. (4.7)

**A morning each:**

9. **Give `w1-sidebar.ipynb` a Part 1C**: build a dictionary **from variables**,
   nest a list of one dictionary in it, call `.update()` on it. It is the only
   required preparation a student who skipped week 0 ever sees. (1.1, 2.2)
10. **Move `budget_left`, `backup_my_work` and `restore_my_work` into a shared
    cell in all fifteen notebooks**, fix `using-the-notebook-server.md:37` to
    name the last *code* cell, and add the Safari seven-day line to the warning
    box. (5.1-5.4, 6.3)
11. **Rewrite the nine `layout: code` narrations** so they read what is on the
    slide. Closes 1.2.5 without an audio-description track and makes the videos
    better for everyone. (4.2)
12. **Label the nine space-aligned stdout tables**, copying `show_trace()` from
    `w5-lab` cell 13 — the one screenshot cell that already does it right.
    Seven of the nine are the graded screenshot cells. (4.4)
13. **Apply the `w6-lab` cell 13 sentence six more times** — `or`, string
    truthiness, tuple unpacking, empty-list truthiness, `IndexError`, and a
    variable inside a literal. One sentence each, in the cell where the gap
    lives. The cheapest thing here that changes whether students *learn* rather
    than whether they *finish*. (2.2, 2.7, 2.9)
14. **Add one sentence to each lab time estimate** saying the first two labs
    usually run over. (6.1)

**Find out, before anything else is decided:**

15. **Recover `scratchpad/review-accessibility.md`** — 6,600 words, referenced
    at `docs/course-review-2026-09-07.md:19`, gone from disk, absent from
    `STATE.md`. It may already contain much of section 4. (4.6)
16. **Publish to production Canvas and check three things**: whether the caption
    `<track>` loads across the signed-files origin, whether the transcript link
    opens or downloads, and whether DesignPLUS defines `.dp-sr-only`. Any of the
    three failing would silently undo the best accessibility work in the course.
    (4.8)
17. **Test JupyterLite with a screen reader and a keyboard**, week 1 lab, end to
    end. The only item whose cost is unknown, which is exactly why it should be
    found out now. The build brief scoped it out and asked for it on the risk
    register; it should come off. (4.4, 4.8)

---

## 10. Method note

Two checks were commissioned alongside my own reading.

The **TAUGHT NOWHERE verification** returned and is folded into section 2. It
corrected two of my claims and three of the student's. That is the right
outcome and it is worth stating why it happened: three of the five wrong claims
— mine included — were claims that something was **absent**. The student set
itself a rule after making the same mistake four times: *"a claim whose whole
evidence is an absence is a claim about my copy, not the course."* I made it
anyway, on `.update()`, by reading section 3 part one and stopping. The general
lesson for this panel is that absence claims need a second reader, and presence
claims mostly do not.

The **accessibility audit** also returned, and section 4 was rewritten around
it. It corrected four more of my claims — I had said no transcripts existed
(they do, and they are good), that the `keyfacts` header row was at risk (it is
stripped deliberately), that table captions were absent (every table has one),
and that slide contrast was unmeasured (it is gated at AAA for body text). All
four errors had the same cause: **I read the markdown and inferred the HTML.**
The course ships HTML from `tools/blocks.py`, and the accessibility work lives
there, not in the content.

That is a method note worth keeping for this panel. **Three of my six wrong
claims came from reading a source file and predicting an artifact instead of
reading the artifact.** The audit found the two Level A failures by opening
`build/video/w1-overview.transcript.html` and looking at line 1. Nothing else
would have found them, because the source is correct and one of the two build
paths is not.

What survived my errors, and what I would stand behind without either
commissioned check, is section 1 and section 5: the week 1 sidebar has no
dictionary, the check cell has no `None` guard, and the backup instruction
works in none of the fifteen notebooks. Those are claims about text that is
present and wrong, which is the class of claim a single reader can make safely.
