# Week 5 spec: the bounded loop

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 5 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.
**Primary evidence for:** CLO3, Build an AI agent that selects and runs triage tools in a bounded loop to reach a verdict.

This is the hardest week in the course for students and the least certain week
for a small model. It therefore carries the most pre-written scaffolding and
only one TODO cell.

Three terms are used throughout. A *loop* here means the agent repeats three
actions until a rule stops it. It looks at what it has, decides what to ask for
next, and runs that request. A *step* is one pass through those three actions.

A *small model* is one of the two the course runs on. Each holds about three
billion *parameters*, which are the numbers a model learns while it is trained.
Three billion is small as these models go. It is small enough that choosing a
tool in a loop is the least reliable thing this course asks of one.

---

## 1. The capability added

Week 5 adds the loop and nothing else.

By the end of week 4 the agent can ask for one tool, get one result back, and
answer. That is one round. Week 5 changes how many rounds happen and who ends
them.

The agent may take up to four steps. After each tool result it either answers
or asks for a different tool, chosen from the result it just read. An explicit
rule ends the run early when one result settles the case.

### Why this is exactly one capability

Nothing else moves this week. The prompt parts are week 3's. The three tools
are week 4's. The answer keys are week 2's. No new tool is added, no new field
appears in the output, and no new data file ships.

The one new thing is control flow, which is the order in which code runs. The
student writes one function that counts steps, asks, checks and stops. Every
line inside it calls a helper that already exists. So the week adds a shape,
not a feature.

## 2. The lab deliverable

The student runs the finished agent over six emails and exports one record of
what happened.

The six emails are chosen so each produces a different loop shape.

| Email | Steps | Why it is here |
|---|---|---|
| 011 | 1 | The sender is inside the organization, so the first result settles it. |
| 007 | 1 | The sending domain is already known bad. |
| 005 | 2 | A trusted sender and a trusted link host agree. |
| 010 | 2 | The link host is on the block list. |
| 004 | 2 | There is no link at all, so only two tools have anything to look at. |
| 012 | 3 | No tool returns anything decisive, so the run ends with no tool left. |

Four of the five stop reasons appear in these six runs. The fifth,
`step_cap`, appears only when the model asks for a tool it has already run.
Section 3 says what the code does then.

The exported file holds, for each email: the ordered steps with the tool name,
the arguments and a one-line result, the stop reason, the number of steps used,
the final verdict, and the tokens that email spent. It also holds the session
token totals and the token count of a deliberately uncapped run.

## 3. What the student writes, and what arrives written

### The one TODO cell

| Cell | What the student writes | Lines |
|---|---|---|
| TODO 1 | `run_loop(parsed, prompt_text, max_steps=MAX_STEPS, step_guard=None)` | 13 to 15 |

That is the whole of the student's writing this week. The target for a lab is 5
to 15 written lines, and 13 to 15 sits inside it. Blank lines and comments do
not count.

The function counts steps, asks the model, stops when the model answers, runs
the tool the model asked for, checks for a decisive stop, asks the supplied
guard whether another step is allowed, and stops when no tool is left or a cap
is reached. It uses only a counter, a `while`, an `if` and a `return`. Every
action inside it is one call to a helper that arrives working.

**The fourth parameter is a growth hook, and week 5 leaves it empty.**
`step_guard` is how week 6 adds a per-run token cap without any student
reopening this cell. The student writes one `if` that calls
`guard_says_stop(step_guard)`.

In week 5 nothing is passed in, that helper always answers no, and the line
never fires. In week 6 `guarded_triage()` passes `over_token_cap` in, and the
same line starts firing between steps. The week 5 cell is never edited.

### What arrives pre-written

Everything from weeks 1 through 4 arrives as working cells, so a student who
never finished week 4 can still build the loop. Eleven new items arrive this
week:

| Name | What it does |
|---|---|
| `MAX_STEPS` | The hard cap, set to 4 |
| `LOOP_INSTRUCTIONS` | Text telling the model it may ask for one tool per step and must answer when it has enough |
| `loop_prompt(parsed)` | Joins the loop instructions to week 3's grounded prompt for one email |
| `new_trace(parsed)` | Makes an empty record of the run, and notes which tools this email can answer |
| `first_call(calls, answer, trace)` | Picks the one tool call the loop acts on, and covers the model answering with no tool at all |
| `append_turn(messages, turn, tool_call, result, trace)` | Adds the model's turn and the tool result, and writes the step into the record |
| `decisive_stop(tool_name, result, parsed)` | Returns a stop reason when one result settles the case, otherwise nothing |
| `tools_left(trace)` | Names which of the three tools have not run yet and still have something to look at |
| `guard_says_stop(step_guard)` | Answers whether a supplied guard says the run has spent its budget. Answers no when no guard was supplied |
| `out_of_room(trace)` | Names why a loop ended when nothing settled the case: `tools_exhausted` or `step_cap` |
| `show_trace(trace)` | Prints one run as a readable table, one row per step |

Three of those eleven and one changed signature came out of writing the lab in
full. Section 15.1 says which, and why each one is needed.

`decisive_stop()` is what makes the stop condition a rule rather than a guess.
It returns `internal_sender` when the mail never left the organization. It
returns `decisive_malicious` when a link host is blocked or a sender is known
bad. It returns `decisive_benign` when a trusted sender and a trusted link host
agree. The five stop reasons the corpus scores against are
`decisive_malicious`, `decisive_benign`, `internal_sender`, `tools_exhausted`
and `step_cap`.

The other two reasons end a run that nothing settled, and `tools_left(trace)`
is the test for both. The loop keeps going only while a step is left and a
usable tool is left.

A tool is usable only when it still has something to look at. `check_urls` has
nothing to check on an email with no link host in it, so it is not left on
those emails. That matches the corpus, where fifteen records end on
`tools_exhausted` after two tools rather than three.

A run that spends every usable tool without settling the case ends as
`tools_exhausted`. That is step 3 at the latest, and step 2 on an email with no
link. Email 004 is the case students see: two tools run, neither settles it,
and the run ends.

A model that asks for `check_urls` on 004 anyway is answered with an empty
result. The step still counts, so the run reaches three steps instead of two.
That is the cost of a wrong choice, and the week 5 written answer asks students
which second tool their own agent picked.

`step_cap` ends a run that reaches four steps with a tool still unused. That
happens when the model asks for a tool it has already run. The code runs the
repeat and the step still counts, which is what the cap is there to catch. The
uncapped demonstration cell drops both the cap and the no-tool-left stop, and
holds a hard stop at twenty steps.

The starter notebook holds eighteen cells. Two of them exist only to slow the
week down. One shows a single pass of the loop written out flat, with every
value printed, so a student sees one pass before writing many. The other calls
each new helper on its own and prints what it returns.

**Section 15 writes all eighteen out.** It holds the TODO cell as the student
opens it, the reference solution, every markdown cell's text, and every
pre-written cell's code.

## 4. Weekly objectives

Each is one sentence, holds one measurable verb, and names something the
student does in this week's lab.

| # | Objective | Parent | Words | Verb |
|---|---|---|---|---|
| 5.1 | Build a triage loop with a four-step cap and a stop condition. | CLO3 | 12 | Build |
| 5.2 | Record the tool order and stop reason for six triage runs. | CLO3 | 11 | Record |
| 5.3 | Compare the token cost of a capped run and an uncapped run. | CLO3 | 12 | Compare |

All three carry CLO3, which is correct for the week that holds its primary
evidence. No objective this week is left without a parent.

## 5. The sidebar

### Construct and domain

The construct is a loop that carries information between passes, with a counter
cap and a stop condition. The build prompt asks for the longest and most
careful sidebar in the course here, and this is it.

The domain is a bus timetable. No other sidebar in the course uses it.

The sidebar walks a route of four stops and reads how many minutes late the bus
is at each one. It carries three things forward: how many legs it has ridden,
which stops it has already passed, and which stops are still ahead. It stops
early when the bus is back on time. It stops anyway after three legs.

The sidebar is 19 lines, runs on its own, and prints a line per leg plus three
closing lines. It is written out below in full.

Then it links back to week 0, and that link is a blocking dependency. The
build prompt's week 0 scope names `for` loops and does not name `while`, so
the passage this sidebar needs does not exist yet. The week 0 outline,
blueprint item 6, has to add a short `while`, counter and `break` passage to
its loops section.

The sidebar is written as though that passage is new to the student. It walks
the counter, the test and the stop line by line, because for most students
this is the first place they meet `while`. Section 14 item 1 carries the same
dependency.

### The sidebar code

```python
# Sidebar 5: ride one leg at a time, and stop when a rule says stop.
timetable = {"Oak St": 4, "Vine St": 0, "Rail Yard": 2, "Depot": 3}
stops_ahead = ["Oak St", "Vine St", "Rail Yard", "Depot"]
called_out = []
legs = 0
MAX_LEGS = 3
finish_note = "rode every leg the cap allowed"
while legs < MAX_LEGS and stops_ahead:
    stop_name = stops_ahead.pop(0)
    minutes_late = timetable[stop_name]
    called_out.append(stop_name)
    legs = legs + 1
    print(f"leg {legs}: {stop_name}, {minutes_late} minutes late")
    if minutes_late == 0:
        finish_note = f"stopped at {stop_name}, the bus was back on time"
        break
print(f"legs ridden: {legs}")
print(f"stops called out: {called_out}")
print(f"why it ended: {finish_note}")
```

Nineteen lines, counted the way week 1 counts them: every line in the block,
including the title comment. The ceiling is 20. What it prints:

```
leg 1: Oak St, 4 minutes late
leg 2: Vine St, 0 minutes late
legs ridden: 2
stops called out: ['Oak St', 'Vine St']
why it ended: stopped at Vine St, the bus was back on time
```

### The walkthrough, as students read it

The first line is a comment. Python ignores it. It is there for you.

`timetable` holds one number for each stop. The number is how many minutes late
the bus is there. `stops_ahead` is the route, in order. `called_out` starts
empty. It fills up as the ride goes on.

`legs` is the counter. It starts at zero. `MAX_LEGS` is the cap. It never
changes.

`finish_note` holds the reason the ride ended. It is set before the loop runs,
so there is always a note to print.

Now the loop. `while` means keep going while both tests are true. The first
test is `legs < MAX_LEGS`. The second test is `stops_ahead`, which is true
while the list still holds a stop. Both have to be true. When either one fails,
the loop ends.

Inside the loop, `stops_ahead.pop(0)` takes the first stop off the front of the
list and hands it back. The list is one shorter after that. This is how the
loop carries what it learned into the next pass.

`timetable[stop_name]` reads the minutes for that stop. `called_out.append` adds
the stop to the list of stops already passed.

`legs = legs + 1` moves the counter. Without this line the first test never
fails, and the loop never stops on the cap.

The `print` line shows one leg per pass.

The `if` is the stop condition. When the bus is on time, `minutes_late` is
zero. The note is rewritten and `break` ends the loop at once. Nothing later in
that pass runs.

The last three lines run once, after the loop. They print the counter, the
stops called out, and the note.

### Try changing this

The one ungraded prompt the sidebar ends with, word for word:

> Change `MAX_LEGS` from 3 to 2. Run it again. Say which of the three closing
> lines changes.

The answer is none of them. The bus was on time at leg 2, so the stop condition
ended the ride before the cap could. That is the lesson the lab needs: a good
run ends on its stop condition, and the cap is the guard for the run that does
not.

**One correction the program manager should see.** An earlier draft of this
section said the prompt would ask which single closing line changes when the
cap is lowered. Writing the sidebar out showed that no arrangement of a
three-line closing block changes exactly one line. Either the stop condition
fires first, in which case nothing changes, or it never fires, in which case
two of the three change. The prompt above takes the first case, because it is
the one that teaches the distinction week 5 rests on.

### Link back

Week 0, the loops section, specifically the `while`, counter and `break`
passage that section 14 item 1 asks that section to add.

### Why pasting it into the lab fails

Pasted into the lab, the sidebar raises `NameError: name 'timetable' is not
defined`, because the lab has no `timetable` dictionary, no `stops_ahead` list
and no `MAX_LEGS` value, and its loop asks a model rather than reading a number
from a table.

The names are deliberately disjoint. The sidebar uses `timetable`,
`stops_ahead`, `called_out`, `legs`, `MAX_LEGS`, `finish_note`, `stop_name` and
`minutes_late`. The lab uses `parsed`, `messages`, `trace`, `step`,
`MAX_STEPS`, `tools_left`, `guard_says_stop` and `decisive_stop`. The shapes
differ too: the sidebar carries a list of short strings, the lab carries a
record of steps holding a tool name, arguments and a result.

None of those eight names appears in any other sidebar in the course. Each of
the seven weeks uses a different everyday domain, and section 5 of every weekly
spec lists its own names so the rule can be checked from the page.

## 6. The reading

**Word count: about 1,250 words.** Page budget is 1,400 weighted words, so this
fits. Estimated time is 40 minutes, itemized in section 11.

The page runs 200 words above the 900 to 1,050 word target the course writing
standard sets. The overshoot is the two worked runs printed as tables at the
end. This is the hardest week in the course, and those two runs are what a
student checks their own trace against.

What it covers, in order:

1. What the loop is here, drawn as observe, decide, act, with a cap.
2. What makes a stop condition explicit, and the five stop reasons by name.
3. How the agent picks its next tool from the result it just read.
4. Why a wrong second choice costs a step, using the case of an email with no
   link in it.
5. What a runaway loop is, and why every pass costs more than the one before it.
   Each pass carries the whole history, so cost grows faster than the step count.
6. Why the cap is a control rather than a convenience. It catches the run that
   spends a step on a tool it already ran, and the page names who owns that
   control in a security operations team.

The page ends with two worked runs printed as tables, one that stops after one
step and one that uses all three tools and then stops with none left. Four ungraded questions ask the student to
name the stop reason for each and say which step added nothing.

Citations planned: the NIST AI Risk Management Framework on bounding autonomous
behavior, and the OWASP Top 10 for Large Language Model Applications entry on
excessive agency. Both are openly readable. Both go to expert review with the
draft, and any claim that review cannot ground is removed rather than kept.

## 7. The discussion prompt

Written below as students will see it. Estimated 20 minutes including one reply.

> Open the file your notebook wrote, `week5_loop_trace.json`. Find the run for
> email 012. No tool result settled that case. Your agent kept going until no
> tool was left to try.
>
> Post one message with three parts.
>
> 1. Name the tools your agent chose for 012, in the order it chose them.
> 2. Give the stop reason and the step count your own file shows.
> 3. In two or three sentences, say what the last step added. Was it worth its
>    tokens?
>
> If your run for 012 stopped for another reason, say which stop reason your
> file shows and answer for that run.
>
> Then reply to one classmate. Look at the tool order in their post. Say
> whether your agent chose the same second tool. If it chose a different one,
> name what your agent had already found out by then.
>
> Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central.
>
> You may use AI help on this post. If you do, add one line saying what you
> asked it.

The prompt cannot be answered from opinion. Every part asks for a value out of
the student's own exported file, and the reply asks the student to compare that
value with a peer's.

## 8. What students submit

Three items. Nothing is zipped and no link is submitted.

**The screenshot.** One image of the printed output of the cell named "Run all
six emails". All six trace tables must be visible, with the step count and stop
reason columns readable. Do not crop off the token total printed under the last
table. No cell in the notebook prints key material, so no screenshot can expose
it.

**The file.** `week5_loop_trace.json`, written by the export cell near the end
of the notebook. The cell prints the full path of the file and its first few
lines, so the student can see exactly which file to attach. Attach that one
file.

**The written answer, 3 to 5 sentences.** Shown to students as:

> Answer in 3 to 5 sentences. Use numbers from your own run.
>
> 1. Which email used the most steps? Give that step count and its stop reason
>    from your file.
> 2. Email 004 has no link to check. Name the second tool your agent chose.
>    Say what the first result had told it.
> 3. Give both token totals your notebook printed. One is the capped run, one
>    is the uncapped run. Say what the cap saved.

## 9. Rubric sketch

One hundred points, four criteria, four performance levels each. Every weekly
lab in this course is worth 100 points, so the seven labs carry equal weight
inside the Labs group. Every criterion is gradeable from the screenshot, the
file and the written answer alone. No instructor runs a student's notebook.

| # | Criterion | Points | Levels | Canvas Outcome |
|---|---|---|---|---|
| 1 | Submission completeness. Screenshot, file and written answer are all present and readable. | 20 | 20 / 15 / 10 / 0 | None. Declared a non-CLO expectation. |
| 2 | Bounded tool loop. The file holds six runs. Each shows an ordered tool list, a step count of four or fewer, and one of the five stop reasons. | 40 | 40 / 30 / 20 / 0 | CLO3: Build a bounded triage agent. Primary evidence. |
| 3 | Reading your own trace. The written answer names the correct step count, stop reason and second tool from the student's own file. | 20 | 20 / 15 / 10 / 0 | CLO3: Build a bounded triage agent. Supporting evidence for objective 5.2. |
| 4 | Cost of an uncapped run. The written answer gives both token totals and says what the cap saved. | 20 | 20 / 15 / 10 / 0 | CLO3: Build a bounded triage agent. Supporting evidence for objective 5.3. |

Three of the four criteria post to the CLO3 Outcome, and all three appear in
the alignment matrix crosswalk. Criterion 2 carries the primary evidence. It
reads objectives 5.1 and 5.2 out of the exported file.

Criterion 3 is supporting evidence for 5.2, taken from the written answer
rather than the file. Criterion 4 is the only measure of objective 5.3, so it
is supporting evidence for that one. Criterion 1 is the only criterion with no
Outcome link, and it measures submission completeness alone.

Every criterion uses the shared mastery scale of 4, 3, 2 and 0. Criterion 2
scales it by ten and the other three scale it by five, so every rubric rating
maps onto an outcome rating with no translation step.

Two build details need confirming in Canvas. First, that a scaled outcome
criterion still posts the unscaled rating into the outcome report. Second,
which result the CLO3 roll-up keeps when one rubric posts three results to one
Outcome under the most recent score method. If that order is not fixed,
criterion 2 is the result of record and the other two stay in the outcome
detail view.

## 10. The self-check

Six items, multiple choice, auto-graded, low stakes. Self-checks are 8 percent
of the course grade spread across seven weeks.

What the six items cover:

1. Which of the five stop reasons fits the trace shown.
2. What makes a stop condition explicit.
3. Why the cap is needed when the model repeats a tool it already ran.
4. Which tool to choose second when an email has no link.
5. What the token counter reads, and what it never measures.
6. What the code does when the model answers instead of asking.

Every stem is drawn from this week's own agent and corpus. None can be answered
from general phishing knowledge.

## 11. Time estimate

| Activity | Minutes |
|---|---|
| Overview video and success walkthrough video | 10 |
| Sidebar | 30 |
| Reading | 40 |
| Lab | 180 |
| Discussion, including one reply | 20 |
| Self-check and submission | 30 |
| **Total** | **310 minutes, or 5 hours 10 minutes** |

The total sits under the 6 hour ceiling with 50 minutes of slack. Every item
sits inside its band: video under 12 minutes, sidebar 20 to 30, reading 40 to
50, lab 2.5 to 3 hours, discussion 15 to 20, self-check and submission 30.

The lab takes the top of its band and the sidebar takes the top of its band.
Both are deliberate. This is the week where a student with no programming
background is most likely to stall.

The 40 minute reading figure is not 40 minutes of prose. It is built from the
one course reading rate, which section 2 of the survey content plan sets at 200
words a minute for one pass, plus named lines for what the page asks beyond
reading.

| Part of the reading | Minutes |
|---|---|
| One pass of 1,250 words at 200 words a minute | 6 |
| Stepping through the two worked runs printed as tables | 22 |
| Answering the four ungraded questions | 12 |
| **Total** | **40** |

If a later week needs slack, the reading is what gets cut, never the sidebar and
never lab scaffolding.

## 12. Estimated tokens per full lab run

Character counts below come from the corpus files and from the rendered emails
for 004, 005, 007, 010, 011 and 012. Completion figures come from the measured
serving stack document, using the reasoning-off setting it leans toward.

The four shared parts below are measured once for the whole blueprint, in
section 2 of the grade distribution and token totals document. Weeks 4, 6 and 7
send the same figures.

```
Prompt, fixed per call:  loop instructions 900 + answer schema 347
  + three tool definitions 964 + playbook 1,366 + known-good list 668
  = 4,245 chars; plus this email's facts block and body, 347 + 749 on average
  = 5,341 chars, about 1,335 tokens. Each finished step adds about 430 chars
  of history, about 108 tokens.
Calls in a full run: 16 across the six emails, 3 in the check and demo cells,
  20 in the uncapped demonstration = 39 calls.
  Six-email run:   16 x 1,335 + 15 history increments x 108 = 23,000 tokens.
  Check and demo:   3 x 1,335                               =  4,000 tokens.
  Uncapped run:    20 x 1,335 + 190 increments x 108        = 47,200 tokens.
  Prompt total = 23,000 + 4,000 + 47,200 = about 74,000 tokens.
Completion, measured: 34 tokens per tool request, about 75 per JSON verdict.
  30 tool requests + 9 verdicts = about 1,700 tokens.
Total per full lab run = about 76,000 tokens.
```

The 190 increments in the uncapped run are the sum of 0 through 19, because
call twenty carries nineteen earlier turns. That growth is the week's lesson
about cost, written as arithmetic.

Two notes the program manager should have. First, the uncapped demonstration is
roughly 47,000 of those 76,000 tokens. That the demonstration costs more than
the lab is itself the week's lesson, and the file records both numbers so the
student sees it. Second, if the reasoning model runs in its documented default
mode instead, completion rises to roughly 13,000 tokens and the run total
reaches roughly 87,000.

## 13. What the measurement found, and what ships

The reliability measurement is done. It ran 294 complete agent runs across both
course models and four lab designs, on exactly these six emails. The full report
is `builder/docs/week5-model-test.md` and the raw record is
`builder/docs/week5-model-test.json`.

**The design in this spec is the one that works.** The shape above gives the
model one job: choose the next tool. `decisive_stop()` in the student's code ends
the run. On Granite 4.2 with reasoning off, that shape produced the exact expected
tool path in 29 of 30 runs. It ended the run for the right reason in 30 of 30, and
reached the right verdict in 28 of 30. The fallback below is not needed. It stays
written down as the contingency for a future model version.

**Why the stop condition belongs in code, now measured.** When the model was left
to decide for itself when to stop, it chose the correct first tool almost every
time and still produced the correct whole path only 25 of 60 times. The gap was
the model not stopping once it had enough. On email 007, whose sender is already
known bad, it ran the link check anyway, reached the right verdict, and spent an
extra step doing it. Moving the stop into `decisive_stop()` closed that gap
completely: across every model and every email in that design, the run ended for
the right reason 88 of 90 times.

**The model to standardise on.** Granite 4.2 3B with reasoning switched off. The
configuration cell sets `reasoning_effort` to `none` for every model, not gated by model name,
because Granite 4.1 rejects that field with an HTTP 400. In its default reasoning
mode Granite 4.2 spent an entire 512-token answer budget thinking and returned
nothing 18 times out of 18. Raised to 4,096 tokens it works, and still should not
ship: 83 seconds and about 7,900 tokens for one triage, against 4.1 seconds and
3,813 tokens for the recommended setting.

**Granite 4.1 3B is the documented fallback, with one caveat.** In this same
design it ends the run for the right reason in 30 of 30 runs, but it picks a
different tool order, matching the expected path 0 of 30 times while still
reaching the right verdict 20 of 30. The order is what varies, not the
termination. This is why the rubric below scores the stop reason and the trace
rather than the tool order. A rubric that graded order would fail students for
the model's behaviour, and would fail them on one model and not the other.

**One thing the measurement changed in this spec.** Email 012 was recorded as
ending at the step cap. Three tools exist under a cap of four, so a well-behaved
agent runs out of tools first, and every run confirmed it. The corpus record, its
ground truth entry and section 2 of this spec now all read `tools_exhausted`. The
cap is still taught, through the deliberately uncapped run in section 15.

**One thing the measurement says about grading.** Email 012 splits the
configurations. It is a real vendor on a new domain, with a link host on neither
list, asking for names, and most designs read that as an attack. The recommended
configuration answered it correctly in 4 runs of 5. Every other configuration
together managed 9 of 44, and Granite 4.1 called it malicious in all 20 of its
runs.

So the verdict on 012 is not stable across models, and the week 5 rubric awards
no points for it. The discussion prompt in section 8 uses it as the example of a
wrong answer worth reporting, which holds whichever model the college serves.

### The fallback, kept for a future model version

A fixed two-step sequence. Step one is not a choice: the code always calls
`check_sender_reputation` first, with no model involved. `decisive_stop()` runs
on that result exactly as it does now.

If it fires, the run ends and the model is asked once for the verdict. If it does
not, the model is handed the first result and picks the second tool from the two
that are left, by name. The code runs it, `decisive_stop()` runs again, and the
run ends.

The same six emails, the same five stop reasons, the same `decisive_stop()`, the
same trace record, the same export file, the same rubric and the same submission.
`MAX_STEPS` stays at 4 and still guards the code.

Under the fallback the TODO cell becomes `run_sequence(parsed, prompt_text)` at 8
to 10 lines, with two written-out passes instead of a `while`. Lab time drops to
about 150 minutes and the estimate drops to roughly 23,000 tokens per lab run.

The agent then chooses one tool instead of up to three, so the trace shows one
free choice rather than a sequence of them. CLO3 still reads true. The evidence
is thinner, and the alignment matrix would need a one-line note saying so.

Objective 5.1 does not survive that change. It would have to read: Build a
two-step triage sequence with an explicit stop condition. That is ten words, one
verb, parent CLO3. Objectives 5.2 and 5.3 hold word for word.

## 14. Assumptions and gaps

1. **Week 0 must cover `while` loops.** The build prompt's week 0 scope names
   `for` loops and does not name `while`. The week 5 lab and sidebar both need
   a `while` with a counter. The week 0 outline therefore has to add a short
   passage on it. That passage is the target of the sidebar's week 0 link in
   section 5, so it blocks the sidebar. The sidebar teaches the construct from
   scratch in either case.
2. **`LOOP_INSTRUCTIONS` is budgeted at 900 characters.** The text is not
   written yet. Every other character count in section 12 is measured, either
   from a real corpus file, a rendered email, or the rendered prompt parts in
   section 2 of the grade distribution and token totals document.
3. **The known-good domain list is 668 characters** as rendered into a prompt.
   The shipped data file is 892 characters of JSON, which is not the form the
   prompt carries. The rendered form is printed and measured once for the whole
   blueprint, in section 2 of the grade distribution and token totals document,
   and weeks 3, 4, 6 and 7 use the same figure.
4. **A full lab run is defined as** the six-email run, the check cell on 011,
   the single unrolled pass, and the uncapped demonstration. A student who
   reruns cells while debugging will spend more.
5. **The scaled outcome criterion in section 9** assumes Canvas posts the
   unscaled mastery rating into the outcome report. Confirm before the build.
6. **The reading's two citations are planned, not verified.** Both go to expert
   review with the draft.
7. **Email 012 now stops on `tools_exhausted`, not `step_cap`.** Three tools
   exist, so a run that repeats none of them ends by step 3. The build prompt
   fixes the cap at four, so the cap cannot be lowered to three to fit the old
   figure. The corpus manifest entry for 012 now reads `tools_exhausted`, and
   so does its record in the rendered ground truth file. Three other lines
   changed with them: both notes fields and the phase 0 week-by-week table,
   plus the week 5 entry in the code ledger. No other record in the corpus
   used `step_cap`, and nothing else moved. `check_spec.py` still reports all
   rules holding on all 56 records. This is a change to an approved phase 0
   artifact and the program manager should see it as one.
8. **Three rubric criteria post to one Outcome.** Section 9 links criteria 2, 3
   and 4 to CLO3. Confirm which result the most recent score method keeps when
   three arrive from one rubric at once. The fallback is stated in section 9.
9. **Writing the lab out added three pre-written helpers and changed one
   signature.** `loop_prompt()`, `first_call()` and `out_of_room()` are new,
   and `new_trace(email_id)` becomes `new_trace(parsed)`. Section 15.1 gives
   the reason for each. The code ledger's week 5 section now carries the same
   eleven names. Nothing the student writes changed: the TODO cell is still one
   function of 13 to 15 lines.
10. **Two small helpers ship inside the pre-written cells and are not counted
    in the eleven.** `usable_tools(parsed)` is called once by `new_trace()`,
    and `one_line(result)` is called by `append_turn()` to shorten a tool
    result for the trace table. Both are printed in section 15.4. Neither is
    ever called from the TODO cell.
11. **The `email_id` key comes from `load_email()`, not from the parser.**
    Section 15's code reads `parsed["email_id"]`. Week 2 ships
    `load_email(email_id, known_names=None)`, which calls the parser and then
    stamps the id into the record it hands back. Every week from 2 on loads an
    email that one way, so `run_loop()` needs no fourth argument. The code
    ledger's section 2.5 fixes it.
12. **The sidebar's "try changing this" prompt changed shape.** An earlier
    draft said one closing line would change when the cap is lowered. No
    three-line closing block can change exactly one line. Section 5 states the
    prompt that ships and the reason.
13. **The sidebar is 19 lines, not 18.** Counted the way week 1 counts, which
    includes the title comment. The binding ceiling is 20.

## 15. The week 5 lab, written out

The build prompt asks for this week to be written in full before the other six
weeks depend on its pattern. This section is that. It holds the one TODO cell
as the student meets it, the reference solution, every markdown cell's text,
and every pre-written cell's code.

### 15.1 What writing it out changed

Writing the loop out found three gaps in the eight helpers section 3 lists.
All three are named here rather than resolved quietly. Section 3's table and
the code ledger now carry them.

| Name | Why the loop needs it |
|---|---|
| `loop_prompt(parsed)` | Four cells build the same prompt: `LOOP_INSTRUCTIONS`, then week 3's grounded prompt. Without one helper, those two lines are copied into four pre-written cells. |
| `first_call(calls, answer, trace)` | Week 4's `ask_with_tools()` hands back a list of tool calls, because the wire format allows more than one. The loop needs exactly one. This helper takes the first, reads the arguments out of the JSON string the model sends, and covers the case where the model answers in prose and asks for no tool. |
| `out_of_room(trace)` | Names why a loop ended when nothing settled the case. It returns `tools_exhausted` when no usable tool is left, and `step_cap` when one is still unused. Without it the student writes a four line if and else, and the TODO cell goes over its line budget. |

One signature changed with them. `new_trace(email_id)` becomes
`new_trace(parsed)`. Section 3 says `tools_left(trace)` names the tools that
have not run yet **and still have something to look at**. A trace built from an
id alone cannot know whether the email has a link host in it, so it cannot
answer the second half. Built from the parsed email, it can, and
`tools_left(trace)` keeps its one argument.

That makes eleven pre-written items this week rather than eight. Week 5 is the
week the build prompt tells us to pre-write more scaffolding than anywhere
else, so the count moving up is the intended direction.

Two more small helpers ship inside the pre-written cells and are never called
from the TODO cell: `usable_tools(parsed)`, which `new_trace()` calls once, and
`one_line(result)`, which `append_turn()` calls to shorten a tool result for
the trace table. They are printed below with the cells that hold them.

### 15.2 The TODO cell, as the student opens it

This is notebook cell 12, and it is the only cell in the week with anything
missing.

```python
# TODO 1. Write run_loop().
#
# The six sentences in the cell above are the six things this function does.
# Use only helpers already defined in this notebook. Write no new helper.
#
#   trace     the record of this run. new_trace() makes an empty one.
#   messages  the message list. start_messages() builds the first one.
#   step      your counter. It starts at 0 and goes up by 1 each pass.
#
# The loop keeps going while a step is left and a usable tool is left.
# Stop as soon as trace["stop_reason"] is set. Hand back the trace either way.

def run_loop(parsed, prompt_text, max_steps=MAX_STEPS, step_guard=None):
    # your code here
    return trace
```

### 15.3 The reference solution

Fifteen written lines, inside the 13 to 15 this week commits to. Every line
calls something that already exists.

```python
def run_loop(parsed, prompt_text, max_steps=MAX_STEPS, step_guard=None):
    trace = new_trace(parsed)
    messages = start_messages(parsed, prompt_text)
    step = 0
    while step < max_steps and tools_left(trace):
        step = step + 1
        answer, finish, turn, calls = ask_with_tools(messages)
        tool_call = first_call(calls, answer, trace)
        result = run_tool(tool_call["name"], tool_call["arguments"], parsed)
        append_turn(messages, turn, tool_call, result, trace)
        trace["stop_reason"] = decisive_stop(tool_call["name"], result, parsed)
        if trace["stop_reason"] or guard_says_stop(step_guard):
            return trace
    trace["stop_reason"] = out_of_room(trace)
    return trace
```

Four notes on it. The `while` line carries the two tests section 3 names and no
third one. `guard_says_stop()` always answers no in week 5, because nothing is
passed in, so that half of the `if` cannot fire until week 6.

The last two lines run only when the loop ran out of steps or ran out of tools.
`tools_left(trace)` is never empty at the top of a pass, because the `while`
line just tested it, so `first_call()` can always name a tool to fall back to.

### 15.4 The eighteen cells, written out

Cells 2, 3, 4 and 5 carry code the student already has. They arrive from the
week 4 notebook unchanged, and the code ledger names every function in them.
They are listed here by what they define rather than reprinted, because
reprinting four weeks of working code inside a week 5 spec would bury the week
5 content this section exists to show.

**Cell 1. Markdown.**

> # Week 5: the bounded loop
>
> This week your agent takes more than one turn. It asks for a tool, reads the
> result, and decides what to ask for next. A rule stops it. A cap stops it
> too, when the rule does not.
>
> Everything you built in weeks 1 to 4 is already in this notebook and working.
> If your own week 4 code never finished, that is fine. Start here and build
> the loop.

**Cell 2. Code, pre-written.** Imports and the configuration cell from code
ledger section 2.1: `BASE_URL`, `MODEL`, `MODEL_EXTRAS`, `API_KEY`, `EMAIL_DIR`
and `DATA_DIR`. It prints one line saying whether a key was found. It never
prints the key.

**Cell 3. Code, pre-written.** The token counter from code ledger section 2.2:
`USAGE`, `RUN_USAGE`, `LAST_CALL`, `record_usage()`, `show_tokens()`,
`reset_tokens()` and `start_run()`.

**Cell 4. Code, pre-written.** `send_request(payload)` and
`save_artifact(filename, content)`.

**Cell 5. Code, pre-written.** Working code from weeks 1 to 4: `ask_model()`,
`parse_eml()`, `email_path()`, `load_email()`, `show_email()`, `OUTPUT_SCHEMA`,
`strip_reasoning()`, `schema_errors()`, `extract_json()`, `classify_email()`,
`KNOWN_GOOD`, `PLAYBOOK`, `KNOWN_NAMES`, `FACT_ORDER`, `FACT_LABELS`,
`build_facts()`, `format_facts()`, `build_grounded_prompt()`,
`classify_grounded()`, the three imported tools, `TOOL_SPECS`, `run_tool()`,
`tool_result_message()`, `ask_with_tools()` and `start_messages()`.

**Cell 6. Markdown.**

> ## What a loop is here
>
> One step is three actions. The agent looks at what it has. It picks one
> tool. Your code runs that tool and hands back the result.
>
> The agent may take four steps at most. That number is `MAX_STEPS`, and it is
> the cap.
>
> Most runs end sooner. One tool result can settle the case on its own. When it
> does, `decisive_stop()` names the reason and the run ends.
>
> There are five stop reasons. Three come from a settled case:
> `decisive_malicious`, `decisive_benign` and `internal_sender`. Two come from
> a case nothing settled. `tools_exhausted` means no usable tool was left.
> `step_cap` means the run hit four steps with a tool still unused.

**Cell 7. Code, pre-written.** The cap, the instructions the model gets, the
prompt builder, and an empty run record.

```python
MAX_STEPS = 4
TOOL_NAMES = ["check_sender_reputation", "check_urls", "lookup_recipient"]

LOOP_INSTRUCTIONS = (
    "You are triaging one reported email. You may ask for one tool per step. "
    "Ask for the tool that answers the question you still have. Do not ask "
    "for a tool you have already run. When you have enough to judge the "
    "email, answer with the JSON keys you were given and ask for no more "
    "tools."
)

def loop_prompt(parsed):
    facts_text = format_facts(build_facts(parsed))
    return LOOP_INSTRUCTIONS + "\n\n" + build_grounded_prompt(facts_text,
                                                              parsed["body"])

def usable_tools(parsed):
    # check_urls has nothing to look at on an email with no link host in it.
    if parsed["url_hosts"]:
        return list(TOOL_NAMES)
    return ["check_sender_reputation", "lookup_recipient"]

def new_trace(parsed):
    return {
        "email_id": parsed["email_id"],
        "usable_tools": usable_tools(parsed),
        "steps": [],
        "stop_reason": None,
        "final_answer": None,
        "tokens": 0,
    }
```

**Cell 8. Code, pre-written.** One pass of the loop, written out flat, with
every value printed. Students see one pass before they write many.

```python
# One pass, unrolled. Email 011 is the shortest run in this lab.
start_run()
parsed = load_email("011", known_names=KNOWN_NAMES)
prompt_text = loop_prompt(parsed)

trace = new_trace(parsed)
messages = start_messages(parsed, prompt_text)
print("tools usable on this email:", trace["usable_tools"])
print("tools left at the start:", tools_left(trace))

answer, finish, turn, calls = ask_with_tools(messages)
print("finish reason:", finish)

tool_call = first_call(calls, answer, trace)
print("tool the model asked for:", tool_call["name"])
print("arguments it sent:", tool_call["arguments"])

result = run_tool(tool_call["name"], tool_call["arguments"], parsed)
print("what the tool returned:", result)

append_turn(messages, turn, tool_call, result, trace)
print("steps in the record now:", len(trace["steps"]))
print("tools left now:", tools_left(trace))
print("stop reason:", decisive_stop(tool_call["name"], result, parsed))
show_tokens()
```

**Cell 9. Code, pre-written.** The five helpers the loop calls, and the two
small ones they call.

```python
def one_line(result):
    return json.dumps(result)[:80]

def first_call(calls, answer, trace):
    # The wire format allows more than one call. The loop wants exactly one.
    if calls:
        return {"id": calls[0]["id"],
                "name": calls[0]["function"]["name"],
                "arguments": json.loads(calls[0]["function"]["arguments"])}
    # The model answered instead of asking for a tool. Keep what it said, then
    # keep the run moving with the first tool it has not used yet.
    trace["final_answer"] = extract_json(answer)
    return {"id": "no-call", "name": tools_left(trace)[0], "arguments": {}}

def append_turn(messages, turn, tool_call, result, trace):
    messages.append(turn)
    messages.append(tool_result_message(tool_call, result))
    trace["steps"].append({
        "step": len(trace["steps"]) + 1,
        "tool": tool_call["name"],
        "arguments": tool_call["arguments"],
        "result": one_line(result),
    })
    trace["tokens"] = RUN_USAGE["total_tokens"]

def decisive_stop(tool_name, result, parsed):
    if tool_name == "check_sender_reputation":
        if result.get("status") == "internal":
            return "internal_sender"
        if result.get("status") == "known_bad":
            return "decisive_malicious"
    if tool_name == "check_urls":
        if "blocklisted" in result.values():
            return "decisive_malicious"
        sender = check_sender_reputation(parsed["from_address"])
        if "allowlisted" in result.values() and sender["status"] == "trusted":
            return "decisive_benign"
    return None

def tools_left(trace):
    used = [step["tool"] for step in trace["steps"]]
    return [name for name in trace["usable_tools"] if name not in used]

def guard_says_stop(step_guard):
    # Week 5 passes nothing in, so this always answers no. Week 6 passes a
    # token guard in, and the same line in run_loop() starts firing.
    if step_guard is None:
        return False
    return step_guard()

def out_of_room(trace):
    if tools_left(trace):
        return "step_cap"
    return "tools_exhausted"

def show_trace(trace):
    print(f"{trace['email_id']}  steps: {len(trace['steps'])}  "
          f"stop: {trace['stop_reason']}  tokens: {trace['tokens']}")
    for step in trace["steps"]:
        print(f"   {step['step']}. {step['tool']}({step['arguments']}) "
              f"-> {step['result']}")
```

`decisive_stop()` calls `check_sender_reputation()` a second time on the
`check_urls` branch. That is a local file lookup and costs no model call, and
it is what lets the function keep the three arguments the code ledger fixes for
it. The alternative was to hand it the whole trace.

**Cell 10. Code, pre-written.** Each helper called once on its own, so students
see what each one hands back before meeting it inside a loop.

```python
demo = new_trace(parsed)
print("empty trace:", demo)
print("tools left on an empty trace:", tools_left(demo))
print("out_of_room says:", out_of_room(demo))
print("guard with nothing passed in says:", guard_says_stop(None))

rep = run_tool("check_sender_reputation", {"sender": parsed["from_address"]},
               parsed)
print("reputation result:", rep)
print("decisive_stop on it:", decisive_stop("check_sender_reputation", rep,
                                            parsed))

append_turn(messages, turn, tool_call, rep, demo)
show_trace(demo)
print("tools left now:", tools_left(demo))
```

**Cell 11. Markdown.**

> ## The loop in six sentences
>
> Write these six sentences as code in the next cell.
>
> 1. Start an empty record of the run, and build the first message list.
> 2. Keep going while a step is left and a usable tool is left.
> 3. Count the step, then ask the model which tool it wants.
> 4. Run that tool and add the result to the record.
> 5. If the result settles the case, stop and hand back the record.
> 6. If nothing settled it, name why the loop ran out and hand back the record.

**Cell 12. Code, TODO 1.** Printed in section 15.2. The reference solution is
in section 15.3.

**Cell 13. Code, pre-written.** The check cell. It runs the loop on 011 alone,
the shortest case in the lab, so a student sees one working run before running
six.

```python
start_run()
parsed = load_email("011", known_names=KNOWN_NAMES)
trace = run_loop(parsed, loop_prompt(parsed))
show_trace(trace)

if trace["stop_reason"] == "internal_sender" and len(trace["steps"]) == 1:
    print("Good. One step, and the stop reason is internal_sender.")
else:
    print("Not yet. Expected one step and internal_sender.")
    print("Read the table above and check your while line.")
```

**Cell 14. Code, pre-written.** Named "Run all six emails". Its printed output
is the graded screenshot.

```python
LAB_EMAILS = ["011", "007", "005", "010", "004", "012"]
runs = []

for email_id in LAB_EMAILS:
    start_run()
    parsed = load_email(email_id, known_names=KNOWN_NAMES)
    trace = run_loop(parsed, loop_prompt(parsed))
    runs.append(trace)
    show_trace(trace)
    print()

show_tokens()
```

**Cell 15. Code, pre-written.** The runaway demonstration. The cap is gone and
the no-tool-left test is gone, so only a hard stop at twenty ends it.

```python
start_run()
parsed = load_email("012", known_names=KNOWN_NAMES)
messages = start_messages(parsed, loop_prompt(parsed))
runaway = new_trace(parsed)

step = 0
while step < 20:
    step = step + 1
    answer, finish, turn, calls = ask_with_tools(messages)
    tool_call = first_call(calls, answer, runaway)
    result = run_tool(tool_call["name"], tool_call["arguments"], parsed)
    append_turn(messages, turn, tool_call, result, runaway)

runaway["stop_reason"] = "hard_stop_20"
show_trace(runaway)
print("capped run on 012 spent:", runs[5]["tokens"], "tokens")
print("uncapped run on 012 spent:", runaway["tokens"], "tokens")
```

That cell drops both stops on purpose. With no cap and no tools-left test, the
model is asked twenty times and keeps asking for tools it has already run. The
trace shows the repeats, one row per step, and that is exactly the behaviour
the cap exists to catch.

The cell is the only place in the course where a loop is allowed to run past its
guard, and it is pre-written so no student writes one by accident.

**Cell 16. Markdown.**

> ## What the runaway run cost
>
> Look at the two token totals the last cell printed. One is your capped run on
> email 012. The other is the uncapped run on the same email.
>
> The uncapped run costs many times more, and nothing about it is smarter. It
> asks for tools it has already run. Every request carries the whole history
> with it, so each step costs more than the one before.
>
> The cap is not a convenience. It is the control that stops one bad run from
> spending a week of budget.

**Cell 17. Code, pre-written.** The export cell.

```python
report = {
    "week": 5,
    "model": MODEL,
    "runs": runs,
    "uncapped_run": {"email_id": runaway["email_id"],
                     "steps": len(runaway["steps"]),
                     "tokens": runaway["tokens"]},
    "session_tokens": USAGE,
}
save_artifact("week5_loop_trace.json", report)
```

**Cell 18. Markdown.**

> ## What to submit
>
> Three things, and nothing else.
>
> 1. One screenshot of the output of the cell named "Run all six emails". All
>    six tables must be readable, with the step count and the stop reason
>    showing. Keep the token total under the last table in the picture.
> 2. The file `week5_loop_trace.json`. The export cell printed its full path.
>    Attach that one file. Do not zip it.
> 3. A written answer of 3 to 5 sentences, typed into the box on the
>    assignment page.
>
> No cell in this notebook prints your key, so no screenshot can show one.

### 15.5 What the six runs produce

Each run is checked against the corpus record for that email. The table below
is the expected shape, taken from the six manifest entries, not from a model
run. Section 13 says what happens if a measurement shows the models cannot hold
this shape.

| Email | Tools, in order | Steps | Stop reason |
|---|---|---|---|
| 011 | `check_sender_reputation` | 1 | `internal_sender` |
| 007 | `check_sender_reputation` | 1 | `decisive_malicious` |
| 005 | `check_sender_reputation`, `check_urls` | 2 | `decisive_benign` |
| 010 | `check_sender_reputation`, `check_urls` | 2 | `decisive_malicious` |
| 004 | `check_sender_reputation`, `lookup_recipient` | 2 | `tools_exhausted` |
| 012 | `check_sender_reputation`, `check_urls`, `lookup_recipient` | 3 | `tools_exhausted` |

Email 004 has no link host, so `usable_tools()` leaves `check_urls` out and the
run ends after two steps. A model that asks for `check_urls` on 004 anyway is
answered with an empty result, the step still counts, and the run reaches three
steps instead of two. That is the cost section 3 describes, and the written
answer asks each student which second tool their own agent picked.

### 15.6 The markdown cells against their budget

The writing standard budgets a notebook's markdown cells at 700 weighted words
and targets 400 to 550. The five markdown cells above run to 479 words
together, inside the target. Measured with the course readability tool they
read at grade 2.8, with an average sentence of 10.0 words and a longest
sentence of 17 words.

## 16. Measured readability

Measured with the course readability gate on 2026-09-04. This is a program
manager document, so the whole page is held to grade 9.5, an average sentence
of 18 words and no sentence over 45. Student-facing text drafted inside it is
held to grade 7 and an average sentence of 12 words.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 5.67 | 14.3 words | 45 words |
| The three objectives, section 4 | 4.29 | 11.5 words | 12 words |
| The sidebar walkthrough, section 5 | 1.21 | 7.7 words | 17 words |
| The sidebar "try changing this" prompt, section 5 | 0.50 | 5.3 words | 8 words |
| The discussion prompt, section 7 | 2.59 | 9.4 words | 21 words |
| The written answer prompt, section 8 | 1.48 | 7.3 words | 11 words |
| The rubric criterion column, section 9 | 2.78 | 9.7 words | 20 words |
| The five notebook markdown cells, section 15.4 | 2.80 | 10.0 words | 17 words |
| The TODO cell comment scaffold, section 15.2 | 2.41 | 7.6 words | 15 words |

No prose paragraph on this page runs over 70 words. The longest sentence on the
page is 45 words, which is the ceiling for a program manager document and not
in student-facing text. It is the sentence in section 3 that lists what
`run_loop()` does, and it lists seven things in order on purpose.

**How the short blocks were scored.** The readability tool declines to score
anything under 40 words. A block under that floor was repeated until it cleared
it and then scored, which is the method week 6 uses. Repeating text does not
move a Flesch-Kincaid grade, because the formula is a ratio of words to
sentences and syllables to words. The rubric row is the criterion column, each
cell read as one line, with the header row left out. The sidebar walkthrough
and the markdown cells were scored as written, with fenced code and inline code
excluded by the tool.

**Lengths against their budgets.** The sidebar walkthrough runs 279 words
against a target of about 300. The five notebook markdown cells run 479 words
together, against a budget of 700 weighted words and a target of 400 to 550.
The sidebar code is 19 lines against a ceiling of 20. The TODO cell is one
function of 15 written lines, against this week's committed 13 to 15 and the
build prompt's ceiling of 15.
