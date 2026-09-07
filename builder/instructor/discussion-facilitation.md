# Discussion facilitation: weeks 1 and 2

**Course:** ITSY 1377, Agentic AI and Security Operations
**Audience:** you, the person teaching the course. Not student-facing.
**Covers:** the week 1 and week 2 boards. Weeks 3 to 7 arrive with those weeks.

Read `where-a-small-model-disappoints.md` alongside this page. It carries the
measured model behaviour behind several of the judgment calls below, and it is
the page to quote when a student says their agent "got it wrong".

## The one rule that settles most judgment calls

Both prompts ask for the student's own results. They do not ask for a working
agent, a correct verdict, or agreement with anyone.

So a post that reports a failure with real numbers is a full-credit post. A post
that reports a success with no numbers is not. Section 4 below works that rule
through both rubrics.

## What the two boards are worth

| | Week 1 | Week 2 |
|---|---|---|
| Points | 20 | 20 |
| Post length asked for | about 150 words | about 150 words |
| Reply length asked for | about 60 words | about 60 words |
| Student time | 15 to 20 minutes for post and reply together | same |
| Post due | Thursday | Thursday |
| Reply due | Day 7, Sunday 11:59 PM Central | Day 14, Sunday 11:59 PM Central |
| Point split | 6 / 4 / 5 / 5 | 12 / 6 / 2 |

Discussions are 12 percent of the course grade across seven boards, so each
board is 1.71 percent. Source: `docs/phase1-blueprint/grade-distribution-and-tokens.md`
section 1.1. The splits are in `content/discussions/w1-discussion.md` and
`content/discussions/w2-discussion.md`.

That 1.71 percent is worth keeping in view. These boards are where you meet the
class, not where the grade is decided. Grade them fast and spend the time you
save in the threads.

---

## 1. Week 1: "Where you have already met AI at work"

The prompt has two parts and a reply. Part 1 asks for one quoted line from the
student's own `week1_first_calls.txt`, the temperature that produced it, one
thing that answer got right and one thing it got wrong or left out. Part 2 asks
where they have already met AI in IT or security work, which of three kinds it
was, and one part of a security operations center it touched.

### What a good post looks like

- The quoted line is short and is clearly from their own file. Two students do
  not have the same six answers.
- The temperature is named and is either 0.2 or 1.0. Those are the only two the
  lab runs (`content/assignments/w1-lab.md`, step 9).
- The miss is specific. "It never mentioned the link" is a good post. "It was
  vague" is a thin one.
- Part 2 uses a real example, not one looked up for the assignment.
- The kind and the security operations center part are both named, from the ten
  the week 1 reading defines.
- The reply points at a line in the other post and says what would change if the
  tool were agentic.

Full credit does not require the model to have been right. A student whose model
called a legitimate internal notice malicious has a strong post available to
them, and it is a better one than a clean run.

### Two or three prompts to push a thin post

Pick one. Reply in the thread, not in the gradebook, so the rest of the class
reads the standard.

1. "You said the answer was vague. Which words in it were vague? Paste that line
   and put the temperature beside it."
2. "That quote came from one of six answers to the same email. Did any of the
   other five disagree with it, and on what?"
3. "You named a spam filter, which is scoring AI. What would that same tool have
   to do differently to count as an agentic workflow?"

---

## 2. Week 2: the failed try

The prompt asks the student to open `week2_classification.json`, find one email
that needed more than one try or whose first answer was wrong, and give four
things: the email id with the verdict and category it landed on, the exact
problem line their code reported, their guess at why, and one change to the
instructions. If every email passed on the first try, they say so and post the
email their agent was least sure about, with its confidence number.

### What a good post looks like

- One email id, not four.
- The problem line is quoted word for word from their own file, not paraphrased.
- The guess is about that reply, not about models in general.
- The proposed change is one sentence you could paste into the instructions
  tomorrow.
- The reply names one thing that was the same and one thing that was different
  between the two students' failed tries.

The clean-run path is a full post, not a fallback. It asks for a real number
from their own file and a judgment about it.

Two things weaken a post, and `content/discussions/w2-discussion.md` already
tells students both: a summary of the reading with no numbers in it, and a
problem line copied from a classmate rather than from their own file. The second
one is visible. Problem text is generated per run and rarely matches exactly.

### Two or three prompts to push a thin post

1. "Paste the problem line exactly as your code reported it. Which key did
   `schema_errors()` name?"
2. "You would 'make the instructions clearer'. Write the one sentence you would
   add, in the words you would use."
3. "You had a clean run. What was the lowest confidence number in your file, and
   which email carried it? Do you agree with that verdict?"

---

## 3. When every student reports the same thing

This is not a discipline problem and it is usually not a cheating problem. It is
the board telling you something about the run.

### Week 1: nobody has any variation to report

The lab runs the same prompt six times, three at temperature 0.2 and three at
1.0. If the whole class reports six near-identical answers, look at the served
model before you look at the students.

First, separate two cases. Three answers at temperature 0.2 that look alike is
the expected result, not a problem, and the student has done the lab correctly.
The rubric asks which answer differed most and at which temperature, and the
three runs at 1.0 are what supply that. `where-a-small-model-disappoints.md`
section 5 states this and is the page to read before you reply to anyone.

The case worth investigating is all six answers matching, the 1.0 runs included.
Granite 4.1 at temperature 0 returned byte-identical text on four identical
plain questions, and the serving stack probe notes that the week 1
nondeterminism observation needs a temperature above 0 on that model. On
granite4.2:3b at the documented temperature of 1.0 the variation showed on its
own, including three different `indicators` lists for the same notice. Sources:
`where-a-small-model-disappoints.md` section 5, `docs/serving-stack-shape.md`
section 5 and section 6 item 8. The recommended configuration is granite4.2:3b
with reasoning switched off (`docs/week5-model-test.md`).

What to do, in order.

1. Grade it as reported. Six near-identical answers are the student's own
   result. Do not deduct for the model being steady.
2. Move the axis. Ask the board what the answers left out rather than how they
   differed, and point students at the two token counts in their own file. Email
   001 and email 002 are different lengths, so those numbers move even when the
   words do not.
3. Post the comparison yourself. One short instructor post showing two answers
   that did differ gives the class something to reply to.
4. If it repeats, check which model the hosted endpoint is actually serving. The
   probe scripts under `docs/serving-stack-probe/` re-run in about ten minutes,
   and `docs/serving-stack-shape.md` open question 1 already flags that the
   production stack is not the one that was measured.

### Week 1: everyone names a spam filter

Part 2 asks students to reply to a classmate who named a **different kind** than
they did. If the whole board names scoring AI, that requirement cannot be met.

Say so on the board rather than grading against it. Post one example of each of
the other two kinds, then tell students the reply may go to any post whose
example is different from theirs. Do not deduct the 5 reply points for a
constraint the board made impossible.

### Week 2: everyone had a clean run

Expect this. The serving stack tests produced valid four-key JSON in 3 of 3 runs
at the setting week 2 recommends, so a clean four-email run is the likely case
rather than the edge case (`docs/phase1-blueprint/week-02-spec.md`).

The prompt already handles it, and so does the file. Every submitted
`week2_classification.json` carries a `sample_checks` block: four saved replies,
one clean and three broken, each with what the check reported. Three recorded
failures are in every student's file whatever the model did on the day
(`docs/phase1-blueprint/code-ledger.md` section 4).

A real parse failure is rare rather than impossible, so believe the student who
reports one. Across the 240 measured runs with reasoning off, the final answer
failed to parse 3 times, once inside the shipped configuration's own 30 runs
(`where-a-small-model-disappoints.md` section 6).

So when the board fills with clean runs, point them at that block. "Open
`sample_checks` in your own file. Pick one of the three broken replies. What did
the check say was wrong with it, and what change to the instructions would have
prevented it?" That gives every student failure text to discuss without anyone
having to fake a failure.

### What not to do

- Do not lower a grade because the class converged. The rubric asks for the
  student's own numbers, not for a different answer from their neighbour.
- Do not add a requirement mid-week that the posted prompt does not carry.
- Do not treat matching numbers as copying on their own. Matching **problem
  text** in week 2 is worth a look, because that text varies per run. Matching
  verdicts are not, because the four week 2 emails each carry one labelled
  answer in the corpus.

Write down any week where the whole class converged. Two of the open items in
this build depend on that observation: the note that verdicts can differ between
the two models on the same input (`docs/serving-stack-shape.md` section 6 item
11), and the standing instruction to re-run the model test every term
(`docs/week5-model-test.md`).

---

## 4. Grading a post that is honest about a failed run

**Full credit.** The discussion asks for the student's own results, not for a
success. A student who reports what broke, with the real text and the real
numbers, has done exactly what was asked and has usually done more work than the
student whose run was clean.

### What counts as the student's own results when the run failed

Any of these, quoted rather than described:

- The last line of the traceback, with the error type.
- The cell number where it stopped.
- The token count at the point it stopped, from their own token line.
- The placeholder or empty answer the notebook produced instead of a real one.
- What they changed, and what happened when they ran it again.

### How that maps onto the two rubrics

**Week 1, the 6-point row** asks for one quoted line from their own file and the
temperature. A student whose `ask_model()` never returned still has a file: the
export cell writes whatever the six runs produced, and it writes "not recorded"
for the TODO 2 answer rather than stopping (the export cell in
`lab/notebooks/w1-lab.ipynb`). Accept that quote, plus the error text, as the own-results evidence. The
4-point row, the 5-point part 2 row and the 5-point reply row are unaffected by
a failed run and are graded normally.

**Week 2, the 12-point row** asks for four items. A student whose
`classify_email()` never returned can still supply all four from the
`sample_checks` block and their own error text: the email id, the exact problem
line, a guess at why, and one change to the instructions. Full credit. The
6-point reply row and the 2-point timeliness row are unaffected.

### What is still a partial post

"It didn't work" with nothing attached. No error text, no cell number, no
numbers. Score it partial and reply asking for one thing: the last line of the
error. That single line is what the support pages ask students to send, and it
usually decides the answer (`content/pages/if-something-breaks.md` and
`content/pages/meet-your-instructor.md`).

### What never costs points

- A wrong verdict. Week 2's rubric measures the check and the record, not the
  model's accuracy (`docs/phase1-blueprint/week-02-spec.md`, rubric criterion 2).
- A low confidence number.
- Disagreeing with the model, as long as the student says why.
- Reporting that every email passed on the first try. That is a real result and
  the prompt names it as an acceptable path.

### One thing to do beyond the grade

A failed week 1 or week 2 run is the earliest signal of the programming gap the
risk register names. Do not leave it in the gradebook. Message the student,
name the week 0 section that covers the construct they were missing, and point
at section 10, how to read an error message. Week 1 breaks most often on the
difference between `return` and `print`, which is week 0 section 6
(`docs/phase1-blueprint/week-00-outline.md`).

---

## 5. Your own presence on the board

The course tells students three things about you. Keep them true.

| What students are told | Where it is said |
|---|---|
| Your instructor reads the weekly discussion board and joins the conversation there | `content/pages/meet-your-instructor.md` |
| Messages answered in 24 to 48 hours, not counting weekends and holidays | `content/pages/meet-your-instructor.md` |
| Labs graded with written feedback within one week of the due date | `content/pages/course-policies.md` |

A working cadence that satisfies the first of those, offered as a suggestion
rather than a policy:

1. Post one short seed on the board before Thursday. In week 1, one answer that
   differed and what you noticed in it. In week 2, one broken reply from the
   `sample_checks` block and what the check said about it.
2. On Friday, read the posts and reply to the thin ones with one of the prompts
   in sections 1 and 2. Two or three replies is enough to set the standard.
3. On Monday, grade the board in one sitting. The point splits are small and the
   evidence is in the post.

Reply in the thread rather than only in the gradebook wherever you can. A
student whose agent failed in week 1 or week 2 is the student most likely to
disappear in week 3.
