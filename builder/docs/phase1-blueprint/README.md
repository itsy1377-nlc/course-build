# Phase 1 blueprint: Agentic AI and Security Operations

**Course:** ITSY 1377, Agentic AI and Security Operations
**Institution:** Northeast Lakeview College, Cyber Defense program
**Prepared:** 2026-09-04
**Audience:** the program manager. Nothing here assumes you are building the course.

This is the design for an eight-week online course in which students build one
working security tool, a week at a time. The tool is a phishing email triage
assistant. By week 7 it reads a reported email, gathers facts, decides what to
check next, writes a note another analyst can act on, and is measured for
accuracy over twenty emails.

The corpus this course runs on was approved on 2026-09-03. This blueprint is
the second of three stages. Building the course follows approval of this one.

---

## What to read, depending on how much time you have

**Ten minutes.** This page, then the coverage memo, which answers how the course
covers the eight outcomes you circulated.

**An hour.** Add the alignment matrix, the week 5 model test, and the
assumptions and gaps.

**Everything.** The sixteen documents listed below, about 83,000 words.

---

## The nine things you asked for

| # | Item | Where it is |
|---|---|---|
| 1 | Alignment matrix and the Canvas Outcomes plan | `alignment-matrix.md` |
| 2 | Survey content plan for the four breadth topics, with both discussion prompts in full | `survey-content-plan.md` |
| 3 | A specification per week | `week-01-spec.md` through `week-07-spec.md` |
| 4 | The week 5 sidebar and lab, written in full | `week-05-spec.md`, sections 5 and 15 |
| 5 | Week 5 model test results and a recommendation | `../week5-model-test.md` |
| 6 | Week 0 outline and its self-assessment | `week-00-outline.md` |
| 7 | Week 8 exam blueprint | `exam-blueprint.md` |
| 8 | Every conflict between the institutional template and the build brief | `template-conflicts.md` |
| 9 | Every assumption and every gap | `assumptions-and-gaps.md` |

Three supporting documents carry numbers that belong to the whole course rather
than to one week. `code-ledger.md` fixes what code exists by the end of each
week. `grade-distribution-and-tokens.md` sets points and token budgets. And
`coverage-memo.md` is addressed to you.

---

## The seven decisions worth your attention

**1. One capability a week, and the agent works every week.**
Week 1 calls the model from code. Week 2 gets a strict answer out of it. Week 3
stops sending the raw email and starts sending extracted facts. Week 4 gives it
three checks it can run. Week 5 lets it choose which check to run next.

Week 6 defends it against an email written to fool it. Week 7 makes it write a
useful note and measures how often it is right. Nothing is rebuilt. A student
who could not finish week 4 can still start week 5.

**2. The stop condition lives in the student's code, not in the model.**
This was measured, not assumed. Left to decide for itself, the model picks the
right first check almost every time and then keeps going after it already has
the answer. Moving the stop into six lines the student writes closed that gap
completely, and it is also the better lesson.

**3. Granite 4.2 3B, with its reasoning mode switched off.**
In the design above it produced the exact expected sequence of checks in 29 runs
out of 30. Reasoning mode costs 83 seconds and about 7,900 tokens for one email,
against 4.1 seconds and 3,813 tokens with it off. Granite 4.1 3B is the
documented fallback.

**4. Every lab is worth 100 points, and the rubrics are gradeable from three
things.** A screenshot, one exported file, and three to five sentences. No
instructor ever runs a student's notebook.

**5. The breadth topics are carried by reading, discussion and the exam, not by
labs.** Four topics the course must cover are wider than the phishing tool. They
are taught in the week 1 and week 7 readings, assessed in discussions,
self-checks and the final exam, and they get no learning objective and no Canvas
Outcome. The coverage memo says plainly which of your eight outcomes this
applies to.

**6. Week 0 is optional, ungraded, and open all term.**
Students arrive from a non-technical prerequisite with no Python. Week 0 teaches
exactly what weeks 1 to 7 need and nothing else, using everyday examples rather
than security ones. It opens with a self-assessment that tells a student plainly
whether to work through it or skip it.

**7. Cost is reported as a break-even price, because per-token cost is not yet
known.** One clean pass through all seven labs is about 388,000 tokens per
student. At the advisory figure of $5 per student, that fits if the model costs
under $12.89 per million tokens. If every lab is rerun once, which is the case
to plan for, the price has to be under $6.44.

---

## What is not settled

`assumptions-and-gaps.md` holds all of it, in four groups: what this build is
proceeding on, what needs a decision from you, what needs a decision from the
college, and what needs a measurement that something is currently blocking.

The four that matter most:

- **Late work and resubmission policy.** Not set. It was outside the brief.
- **Three institutional template requirements** conflict with the rule that this
  course uses no external services and needs no installs. They are identity
  verification, a lockdown browser, and an orientation course requirement.
  The college decides these, not this build.
- **Forty-four of the 56 corpus emails are not yet rendered.** Twelve are. The
  rest are specified and generate from the same manifest.
- **The readings are planned but not written**, so their citations are not yet
  verified to resolve and to be openly licensed.

---

## How the work was checked

Three independent audits ran against this blueprint. One checked coherence
across weeks. One recomputed every number. One measured every page for reading
level and checked that every term was defined before use.

They found 62 problems and all 62 were fixed. Among them: seven different lab
point totals, a missing grade distribution, seven sidebars sharing three
subjects, and the week 5 lab having been described rather than written out.

The model test was run twice. The first run was thrown away because an
authoring job regenerated four of the six test emails while the measurement was
reading them. The measurement records a hash of every file it reads, which is
how that was caught rather than reported as a result.
