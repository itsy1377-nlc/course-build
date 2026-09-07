# Instructor package: ITSY 1377, Agentic AI and Security Operations

Northeast Lakeview College, Cyber Defense program. Not student-facing.

Students build one phishing triage agent across weeks 1 to 7. Each week adds one
capability, so the agent works end to end every week. Week 8 is the final exam
only. Week 0 is an optional Python on-ramp, ungraded, open all term.

## What is in this package

| File | What it holds | State |
|---|---|---|
| `README.md` | This page. | Complete |
| `environment-setup.md` | Hosting, API key injection, the model endpoint, corpus files, token budget, and a pre-term checklist. | Complete |
| `announcements.md` | A drafted announcement, ready to send, per week. | Start of term, weeks 1 and 2 |
| `discussion-facilitation.md` | How to run each week's board and how to score it. | Weeks 1 and 2 |
| `where-a-small-model-disappoints.md` | Every place a 3B model is likely to disappoint, with measured numbers. | Complete |
| `common-failure-modes.md` | Common student failures and the fix for each. | Weeks 0, 1 and 2 |
| `grading-notes.md` | How to grade a lab from its three submitted items. | Weeks 0, 1 and 2 |
| `solutions/` | One worked solution notebook per lab. | Not yet written |
| `answer-keys/` | Teaching ground truth per week. Batch and exam keys stay here. | Not yet written |

Every row that names weeks gains its week 3 to week 8 material under the same
file name. The two unwritten rows, `solutions/` and `answer-keys/`, arrive with
weeks 3 to 8.

## Read this before the term starts

1. `environment-setup.md`, then run its checklist in a test student account.
   Nothing else works until that passes.
2. `where-a-small-model-disappoints.md`. The course runs on `granite4.2:3b` with
   reasoning switched off, measured in `../docs/week5-model-test.md`. Students
   meet that model's limits and ask you about them.
3. `announcements.md` and `discussion-facilitation.md`, covering the first three
   sends and the first two boards.
4. `grading-notes.md`, because the first lab is graded in week 1, and
   `common-failure-modes.md`, because the first messages arrive in week 1 too.
   Skim both now and keep them open when grading starts.
5. `../docs/phase1-blueprint/README.md` for the design reasoning.

Every rubric is gradeable from three things: a screenshot, one exported file,
and three to five sentences. You never run a student notebook.

Grade weights are labs 60, final exam 20, discussions 12, self-checks 8,
orientation 0. Each of the seven labs is 100 points, the exam 30, each
discussion 20, each self-check 12
(`../docs/phase1-blueprint/grade-distribution-and-tokens.md`).

Planned student time is 4 hours 32 minutes in week 1
(`../docs/phase1-blueprint/week-01-spec.md`) and about 5.2 hours in week 2
(`week-02-spec.md`), against a 6 hour ceiling. Week 0 adds a front-loaded
4 hours 57 minutes (`week-00-outline.md`).

## What to do in the first week

1. Send the start of term and week 1 announcements from `announcements.md`. Fill
   in the one bracket, your late work and resubmission policy. The course leaves
   that policy to you and sends students there to read it.
2. Point students at the week 0 self-assessment. It tells them plainly whether
   to work through the on-ramp or skip it.
3. Confirm every student passed OLRN-0001 at 80 percent or better. That check is
   yours, in week 1 (`../docs/phase1-blueprint/template-conflicts.md`, item 12).
4. Post once in the Q and A board so students see it is read.
5. Answer messages in 24 to 48 hours, weekends and holidays not counted, and
   return lab grades within one week of the due date (`template-conflicts.md`,
   item 21). In an eight week session, week 1 feedback arrives while week 2 is
   built on top of it, so labs come first.
6. Read the first screenshots for anything showing key material. No cell in any
   notebook prints a key. If one appears, stop and reread
   `environment-setup.md`.
