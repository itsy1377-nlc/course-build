# Weekly announcements, drafted and ready to send

**Course:** ITSY 1377, Agentic AI and Security Operations
**Audience:** you, the person teaching the course. Not student-facing.
**Covers:** start of term, week 1, week 2. Phase 2 builds those three weeks.

## How to use this page

Each block below is the whole announcement. Copy the subject line and the body
into a Canvas announcement and send it. Nothing needs rewriting to be sendable.

Four things before you send the first one.

1. **Announcement 1 has one bracket you must fill in.** It is the late work and
   resubmission policy. The course does not set one, and two student pages send
   students here to read yours: **Syllabus, policies and grades** says "Your
   instructor states the late work and resubmission policy in the first
   announcement of the term", and **Welcome. Start here** repeats it. If you send announcement 1 without filling that bracket, students have
   nowhere to read the policy.
2. **Send days.** Announcement 1 goes out on or before day 1, the Monday the
   term opens. Announcements 2 and 3 go out on the Monday that opens their week.
   Week 1 closes on day 7 and week 2 closes on day 14, both Sunday 11:59 PM
   Central (`content/pages/course-schedule.md`).
3. **Day numbers, not dates.** The student schedule page uses day numbers so it
   reads the same in every term, and it tells students the Canvas calendar date
   is the one their submission is measured against. These drafts follow that.
4. **One thing these drafts do not cover.** Each announcement names the sticking
   point students hit in their own code. If the class instead reports cells that
   finish with no answer while the token counter moves, that is a configuration
   problem, not a student one. Read `where-a-small-model-disappoints.md` section
   4 and send a follow-up rather than editing these.

Every figure in these drafts is taken from a build file. The sources are named
under each block, in small type meant for you and not for the student.

---

## Announcement 1: Start of term

**Subject:** Welcome to ITSY 1377. Start with the ten-question self-assessment.

Welcome to Agentic AI and Security Operations. Over eight weeks you build one
working tool, a phishing email triage assistant, one capability a week. Week 1
adds the first piece: your own code sends an email to the model and reads the
answer back. Almost nothing locks, and every week's notebook arrives holding
working code from the week before.

Do this first. Take the **Week 0 self-assessment**. Ten questions, about ten
minutes. Your score says whether to work through the week 0 Python on-ramp or
skip it. Week 0 is optional and strongly recommended. It is extra work: 4 to 6
hours on top of the under six hours each course week asks for, and most of it
lands before week 1 is due.

What trips people in week 1 is skipping that quiz, then meeting Python for the
first time inside the lab. Ten minutes now saves an evening later.

**Due by day 7, Sunday 11:59 PM Central:** the week 1 lab, the self-check, and
one discussion reply. Post to the discussion by Thursday.

**Late work and resubmission:** [state your policy here].

> **Sources.** Eight weeks and one capability a week, `docs/build-prompt-v1.3.md`.
> Almost nothing locks and the carried-forward notebook,
> `content/pages/course-schedule.md` and `content/pages/w1-overview.md`. Ten
> questions and the scoring bands, `docs/phase1-blueprint/week-00-outline.md`.
> Four to six hours on top, and under six hours a week,
> `docs/phase1-blueprint/week-00-outline.md` and `content/pages/course-policies.md`.
> Day 7, Sunday 11:59 PM Central, `content/pages/course-schedule.md`. The late
> work bracket, `content/pages/course-policies.md`.

---

## Announcement 2: Week 1

**Subject:** Week 1. Your code makes its first model call.

This week your own code talks to the model. You write one function,
`ask_model()`, use it on two emails, and watch the same prompt come back six
different ways at two temperatures. That is the whole capability. An agent is a
loop around this call, and week 5 adds the loop.

Where people get stuck: `return` against `print`. A function that prints the
answer hands nothing back, so the check cell shows `None` or the placeholder
line the notebook shipped with, and nothing after it works. If that happens, look at the last
line of your function and make sure it says `return`. If you get a `NameError`
instead, you ran a cell before the cell that makes the name. Run the cells
above it, from the top.

If the model never answers at all, the notebook still runs and still writes
`week1_first_calls.txt`. Attach that file anyway, say in your written answer
what happened, and email me. A dead endpoint is not a late assignment.

Budget about 4 hours 32 minutes. You write 11 to 14 lines in two marked cells.
Everything else in the notebook arrives finished.

**Due by day 7, Sunday 11:59 PM Central:** the lab (a screenshot,
`week1_first_calls.txt`, three to five sentences), your discussion reply, and
the self-check. Post to the discussion by Thursday.

> **Sources.** `ask_model()`, two emails, six answers at two temperatures, and
> the loop framing, `docs/phase1-blueprint/week-01-spec.md` and
> `content/pages/w1-overview.md`. Return against print named as the most common
> beginner confusion in the course, and week 1 breaking on it,
> `docs/phase1-blueprint/week-00-outline.md` section 6. `NameError` from running
> the check cell before the TODO cell, same file, section 10 table, and
> `content/pages/if-something-breaks.md`. The placeholder text the stub returns,
> the TODO 1 cell in `lab/notebooks/w1-lab.ipynb`. The outage sentence is here
> because week 1's closing cell does not carry one: `lab/notebooks/w1-lab.ipynb`
> cell 15 tells the student the file was still written and to email you, while
> `lab/notebooks/w2-lab.ipynb` cell 16 also tells them to attach it anyway. See
> `grading-notes.md` section 6.3. 272 minutes, or 4 hours 32 minutes, and 11
> to 14 lines in two TODO cells, `docs/phase1-blueprint/week-01-spec.md` sections
> 3 and 11. The three submission items and the due day,
> `content/assignments/w1-lab.md`.

---

## Announcement 3: Week 2

**Subject:** Week 2. An answer your code can check.

This week the model answers in JSON with four named keys, and your code checks
that shape before it trusts the answer. When the check finds a problem, your
code asks again with the problem attached. A badly shaped answer is a normal
condition to handle, not a failure. You meet one on purpose, in a cell we wrote
for you, before you write anything.

Where people get stuck: the retry that is not a retry. Sending the same prompt
a second time changes nothing, and your exported file will show three identical
tries. The rule is one line. Send the problem back with the request, not just
the request again. Second thing: your loop needs the `max_tries=3` cap to stop,
or it can run until your token budget is gone.

Budget about 5.2 hours. This is the first week you write a loop, so give the lab
two sittings if you can.

**Due by day 14, Sunday 11:59 PM Central:** the lab (a screenshot,
`week2_classification.json`, three to five sentences), your discussion reply,
and the self-check. Post to the discussion by Thursday.

> **Sources.** Four keys, the check, the retry, and a bad answer as a normal
> condition, `docs/phase1-blueprint/week-02-spec.md` and
> `content/pages/w2-overview.md`. The retry that resends the same prompt and the
> three identical tries, `content/assignments/w2-lab.md`, the warning callout.
> "Send the problem back with the request, not just the request again,"
> `docs/phase1-blueprint/week-02-spec.md` and the TODO 2 instructions in
> `lab/notebooks/w2-lab.ipynb`. `max_tries=3` and the budget warning, `content/assignments/w2-lab.md`. 310
> minutes, about 5.2 hours, and two sittings for the first loop,
> `docs/phase1-blueprint/week-02-spec.md` and `content/pages/w2-overview.md`. The
> three submission items and day 14, `content/assignments/w2-lab.md`.

---

## Weeks 3 to 7

The build prompt asks for one announcement per instructional week, which is
seven. Phase 2 builds Start Here, week 0, week 1 and week 2, so the three above
are the three that have content behind them.

The announcements for weeks 3 to 7 arrive with those weeks, in Phase 3. Each one
will follow the same shape: two or three sentences on what the week adds, the
one thing students most commonly get stuck on and what to do about it, and what
is due on which day.

Do not write them ahead. The sticking point named in each announcement is meant
to come from that week's spec and from the measured model behaviour, and both
are still being settled for weeks 3 to 7.
