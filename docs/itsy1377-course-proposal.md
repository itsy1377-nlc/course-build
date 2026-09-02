# ITSY 1377 Agentic AI and Security Operations: proposed outcomes

Seven weeks. No prerequisite. No certification mapping. Introductory by
design: broad and light, and hands-on throughout.

This replaces two earlier designs, both archived. The first chased a
certification blueprint; the second was built around NCAE-C knowledge units
and a scripting prerequisite. Neither constraint applies now.

---

## 1. The course in three parts

The coordinator's scope has three parts and the course should have three too:
**what an agent is, what goes wrong with them, and how you would use one in
security operations.** An earlier draft of this proposal covered the first two
and left the third out, which made it a testing course wearing a broader title.

| Part | Weeks | The question it answers |
|---|---|---|
| **A. What an agent is** | 1 to 2 | What is actually happening when an AI "does something", what shape every agent has, and what each one can reach |
| **B. What goes wrong** | 3 to 5, 7 | Where the security problems come from, how you prove one, and what a control looks like |
| **C. Using one for the work** | 1, 5, 6 | Where an agent genuinely helps a security analyst, how you check it, and what you would need to learn to supervise it well |

**One idea holds all three together: evidence over assertion.** When you test an
agent you do not believe what it says it did, you look at what the system
recorded. When you *use* an agent you do not believe what it tells you either,
you check it against the source. It is the same discipline pointed in two
directions, and it is the through line of the course.

**This course assumes AI Fundamentals.** That course is sequenced before this
one and covers prompting, what generative AI is, the ethics and disclosure
frame, and evaluating AI output for plausibility. This course does not re-teach
any of it. The seam that matters is verification: Fundamentals asks whether an
output looks wrong, and this course asks whether the record supports it.
Plausibility, then provenance. `docs/course-sequence-articulation.md` works
through the whole handoff, including the one place the two currently collide.

**Coding agents are the agent every student will actually meet**, so they are
taught alongside the lab's helpdesk agent rather than mentioned in passing.
The point is that they are the same shape: a model, a set of tools, and a loop.
What differs is reach, and reach is a property of how a particular agent was
configured rather than of coding agents in general. Some are read-only. Some
gate every command behind an approval prompt. Some are sandboxed to one
directory. That variability is the lesson: the student inventories a supplied
configuration and reads what it actually permits, rather than being told that
coding agents can do anything. Putting that inventory beside the helpdesk
agent's is the cheapest way to make blast radius mean something, and it is
directly useful to a student about to start using one.

It also fixes a vocabulary problem before it confuses anybody. "Harness" is
used two ways in this field: the scaffolding that wraps a model in tools and a
loop, which is what makes an agent an agent, and a test harness that runs cases
and reports results, which is what this course's `harness/` directory is. The
course names both and says which it means.

**The course's closing argument is that you cannot supervise what you cannot
read**, and it is made by experience rather than asserted. There is no
programming prerequisite and this course does not add one. What it does is put
a student in the position of needing the skill, three times, and let them
notice:

1. **Week 1.** The agent explains two short scripts. The student checks the
   explanation against the scripts and finds where it is wrong. Their ability
   to catch it is exactly their ability to read the code.
2. **Week 2.** The coding agent's tools are read any file, write any file, run
   any command, and almost nothing is reversible. The student is the approval
   step, and an approval step that cannot read what it is approving is not one.
3. **Week 6.** The agent summarises the student's own incident and gets a claim
   wrong. They catch it only because they hold the evidence.

By the end a student should be able to say, from their own experience rather
than because they were told, why they want to learn to program: not to replace
the agent, but to be able to supervise it. That is the honest case for the
programming courses the college already offers, and this course is a feeder
into them rather than a substitute.

**Part C uses a cheap local model, and that turns out to be a feature.** A 3B
model running on a student laptop makes mistakes: it will summarise an incident
and get a detail wrong, or explain a script and invent a flag. The exercise is
verification, so the model's errors are the teaching material. A better model
would make the lesson harder to teach, not easier.

## 2. Proposed learning outcomes

Upon successful completion of this course, the student will be able to:

| # | Outcome | Bloom | Evidence |
|---|---|---|---|
| **1** | Describe how an agentic AI system operates, using its recorded run | Understand | Annotated trace |
| **2** | Interpret a short script to determine what it accesses and changes | Understand | Code-reading worksheet |
| **3** | Analyze an agent's tool configuration to identify irreversible actions | Analyze | Blast-radius inventory |
| **4** | Differentiate evidence from assertion in claims about an agent's behavior | Analyze | Evidence packs |
| **5** | Interpret repeated-trial test results, including results showing no effect | Analyze | Test report and reading |
| **6** | Apply a control at an agent's tool boundary and verify its effect | Apply | The control, measured before and after |
| **7** | Evaluate AI-generated output against source evidence | Evaluate | Verification record |

**One verb, one object, each.** An earlier draft ran to thirty-five words per
outcome and bundled three or four capabilities into each, which cannot be
scored: a student could satisfy half of one and there would be no way to say
which half. Every condition and criterion that used to sit inside an outcome now
sits in the rubric, where it belongs and where it can be changed without
re-approving the outcome.

**That is the practical gain.** Outcome 6 says apply a control and verify its
effect. It does not say which control, at which boundary, against which attack,
measured over how many trials. So the week that delivers it can change, the
target can change, and the number of trials can change, without touching a
document that went through committee. The current design uses a recipient
allowlist over five trials; nothing in the outcomes requires that, and nothing
breaks if it moves.

**The Bloom spread is deliberate for a course with no prerequisite:** two at
Understand in the opening weeks, three at Analyze through the middle, one Apply
and one Evaluate in the final third, after the scaffolding. Nothing sits at
Remember, because a course that only asks students to recall would not need a
lab; nothing sits at Create, because authoring something genuinely novel in
seven weeks without a prerequisite would be a promise this course could not
keep.

**Two notes a reviewer will want.**

Outcome 2 is the scripting requirement made assessable. The course teaches
recognition rather than a language, and this is the line that says so and makes
it gradeable.

Outcome 5 is worded so that a correct test showing no effect is a pass. A
student whose trials all come back negative has done the work correctly, and
saying what a negative result does not establish is the harder skill anyway.

**Mapping to the three parts:** outcomes 1 to 3 are what an agent is, 4 to 6 are
what goes wrong with them, and 7 is using one for security work.

## 3. Week by week

| Wk | Part | Title | What the student is asked to do | Artifact |
|---|---|---|---|---|
| 1 | A, B | Ask it something it should not answer | In the first half hour, before anything is explained, send the supplied request and record what comes back. Then two questions the rest of the course answers: how would you know whether it did that or only said it did, and what else can it reach? Answer the second one now by inventorying its tools: what each reads, what each changes, what cannot be taken back. The six pieces of syntax and the four questions arrive next, as the tools for reading that configuration, stepped in a visual debugger rather than taught on a worksheet | What came back; the blast-radius inventory; the code-reading worksheet; Rules of Engagement gate at 100 percent |
| 2 | A | Does it do the same thing twice? | Send the same request five times and compare what the agent did each time. Then send five different ordinary requests and compare again. Use the starter scripts to count and compare, making the one-line change each asks for. Report what varies and what does not, and answer the question the comparison raises: if it does not do the same thing twice, what does one run prove | A comparison across ten runs, and a written answer to what one run proves |
| 3 | B | Hide an instruction and see how far it gets | Write your own. Plant an instruction inside a ticket or a knowledge base article, in your own words, aimed at a door you choose. Predict what will happen before you run it. Run five trials, then read your own traces to score it: in each run, mark the first model decision, the first tool call, the step where your text entered, and the furthest point the agent got on the four-step scale. **Your case joins the class pool at the end of this week, and the board goes up** | The case file, the prediction, the marked traces, the four-step result, a place on the board |
| 4 | B | Two requests and an audit log | Ask the agent, politely and with no trickery, to send a note to an outside address, and record what happens. Then run as a support agent working two tickets that have nothing to do with customer C-1002, ask for that record, and record what happens. Then read the audit log and say who it says did it | Evidence packs 1 and 2 |
| 5 | C | The case, and the call | An alert fired: mail left the company. Give the assistant read access to the evidence pack and ask for a timeline: claim, time, actor, and the record each claim came from. Check every row against its source. Then make the call in the handover form: was this an incident, what in the pack decides it, what did the assistant get wrong, and what would you do about it | The evidence-linked timeline and the completed handover |
| 6 | B | Build one that holds | Take the containment you recommended and build it. First as an instruction in the agent's prompt; measure it. Then in code at the tool boundary; measure again, and confirm the benign escalation still works | The control, paired before and after reports |
| 7 | B | Head to head | Run your control against the class pool, live, in the room. The board updates as it goes. You get one revision after the first round and one more run. Then point your finished control at what happened in week 1, and report what you find | The pool standing, the revision, and two sentences on the last result |
| Final | | The evidence file | Three findings on fixed headings, each tracing to a recorded check, plus your control with its before and after, plus what the assistant got wrong in week 5, plus a short note on what you would learn next and why. The exam is open book and evidence based: you are given a results file, a trace excerpt and an audit row you have not seen, and asked what each does and does not establish | The report; the where-next note; the exam |

**Three weeks changed, and no outcome did.** That is the point of cutting the
outcomes to one verb each: the schedule below moved substantially and the
document that goes to committee did not have to.

**Week 2 stopped being a worksheet, and this is the third time that hour has
been rebuilt.** It was named the worst hour by five of six readers in the last
round, all quoting the same activity: read the replay and mark five lines. The
diagnosis was that a previous fix had moved the interesting half of the week
into week 1 and left the highlighting behind.

Trace reading is a real skill and the course needs it. What it did not need was
an hour of marking a log because the syllabus said to. So the marking moves to
week 3, where a student reads their own traces to score their own attack and
therefore has a reason to read closely, and week 2 becomes a question worth
answering: run the same request five times, and see whether the agent does the
same thing twice.

It does not. That is the finding, the student produces it themselves, and it is
the reason the whole course runs five trials rather than one. The convention
stops being a rule they were given and becomes a conclusion they reached.

**The exam changed with it.** A recall exam is a strange ending for a course
whose argument is that assertions do not count and evidence does. It is now open
book and evidence based: a results file, a trace excerpt and an audit row the
student has not seen, and the question is what each one does and does not
establish. That is the same task as every graded week, on unfamiliar material,
which is what an exam should be here.

**Week 6 is gone as a writing week.** Across three rounds of independent review
it was named the worst hour every time, by half the readers each time, and
shortening it twice did not move that once. The diagnosis was consistent: it
existed to write up a decision already reached the week before. The
investigation and the call now happen together in week 5, while the evidence is
still live, and the handover form is the artifact of that week rather than a
week of its own.

**Week 2's inventory moved into week 1.** It was the second most-named worst
hour, and the reason was placement: a configuration-reading exercise landing the
week after the most interesting thirty minutes in the course. It is now the
answer to a question the student has just been made to want. They watched the
agent do something it should not; the immediate next question is what else it
can reach, and the inventory answers it while they still care.

**The freed week became the live head to head.** The pool was already the
best-reviewed hour in the course and it was asynchronous: submit, wait, read a
board. Week 7 is now a session in the room. Your control runs against the class
pool while the board updates, you get one revision and one more run, and only
then do you point the finished control at week 1 and find the thing it cannot
touch. The course ends on a competition and a limit rather than a report.

**What that costs the instructor** is a session to run and a board to keep,
against a week of forms to grade. That is a favourable trade but it is not a
free one, and it is the one thing here that adds staff time rather than removing
it.

### 3a. The spoiler rule

**This proposal tells the reader what happens in each week. The student's
assignment sheet must not.** That distinction is the single change most likely
to raise how much students enjoy this course, and it costs nothing to make.

Six readers judged an earlier draft and four of them named the same cause:
every exercise announced its own outcome. The draft said the agent "hands over
the credential", that "nobody approves it", that the student would "get the
record anyway", that "the alert is true and the conclusion drawn from it is
wrong", and that a control pointed at the week 1 disclosure would "find it does
nothing". A student told all of that in advance is not investigating. They are
confirming.

So the rule for whoever writes the pages: **the assignment asks; the debrief
tells.** Every sentence in this document that names an outcome belongs after the
student has run the thing, in the wrap-up, where it is a payoff rather than a
spoiler. The week table above is written the way the assignment should read.
The commentary below it is written for you.

The same rule applies to the lab source. The current target announces its own
flaws in comments above the code, which means a student who reads the source in
week 2, as this course asks them to, is handed week 4's answer. Those comments
move to an instructor build.

**What this does not mean.** Nothing is hidden that a student needs for safety,
scope or grading. The Rules of Engagement, the rubric, what is being assessed
and how, and every constraint on what may be tested stay stated plainly and up
front. The only thing that moves is the answer.

**The class pool runs from week 3 to week 7, and it ends live.** In an earlier
draft it was a single activity in the final week. Every reader called it the
best hour in the course, and then several made the same point: it is in week 7,
and the weeks before it are a person alone at a laptop reading files. So it
became a ladder that ends in a room.

- **End of week 3:** every case goes into the pool and the board goes up,
  showing how far each attack got on the four-step scale, by handle not by name.
- **Weeks 4 to 6:** the board stays up. Anyone may revise and resubmit, and it
  moves when they do.
- **Week 7:** every control runs against the pool live, the board updates as it
  goes, and each student gets one revision and one more run.

That is a standing, visible thread across five weeks and a competitive finish,
for the cost of one file, one page, and one session to run.

**The screening is not optional.** A pooled attack is the one artifact in this
course written by one student and run by another, and some of those students are
under 18. The instructor reads every case before it is redistributed.

**Per-student tokens survive the pool**, because a canary detector derives the
token at run time from whoever is running it. A classmate's case looks for
*your* token in *your* environment, so evidence stays unforgeable even though
the attack is shared.

**Week 5 ships four case packs, and no student is told which one they have.**
This is the other half of the spoiler rule. If there is one pack, the answer is
known to the whole class within an hour of the first person finishing, and the
week becomes a scavenger hunt with the answer printed at the bottom. With four
variants, two of which are incidents and two of which are not, the student has
to actually make the call.

**And the call is what is graded, not the citations.** A student who reaches the
wrong conclusion from correctly cited evidence has done something more
interesting than one who reaches the right conclusion by pattern matching, and
the rubric should be able to tell them apart. Marking every row accepted,
corrected or rejected is the method; deciding whether this was an incident is
the work.

**Something happens in the first half hour, and that is deliberate.** An earlier
draft opened with environment setup, then six pieces of syntax, then a
worksheet, and the first misbehaving agent arrived in week 3. That is twenty-nine
percent of the term before anything worth telling a friend about. Now the
credential falls out of the agent before anything is explained, and the syntax
arrives forty minutes later as the tool for answering the question that
demonstration raises. The same content, in the order that makes a student want
it.

**Week 3 is the student's own attack, and it is the week the course was
missing.** Every prompt in an earlier draft was handed to the student in a file,
which made them a copy-and-wait operator for five weeks. Cases are YAML, so
authoring one needs no Python: a prompt, a door, a detector, a prediction.

**Week 3 also puts indirect prompt injection back, honestly.** The measured
result is that on a small local model the agent does read the planted document,
does obey it, and does call a tool it was not asked to call, and then fails at
the last step. An earlier draft treated that as a reason to leave the attack out.
It is a better reason to put it in and grade what the student observed: the
harness gives its terminal verdict, usually no hits, and the student reads the
trace and reports how far the chain went. "The verdict says no and here is what
did happen" is the most useful sentence in agent security, and there is no
honest way to teach it with a staged success.

**Weeks 5 to 7 are now one continuing case, and that is the biggest change in
this draft.** They used to be three separate exercises: read a harness report,
then hand the assistant some evidence, then implement a control. Review found
the real problem with that, and it was not any one week. It was that the course
had no mystery in it. Every vulnerability is announced in the source comments
before the student meets it, so there was never an unknown to resolve, never
two sources disagreeing, and never a decision that mattered. Four weeks of ask,
run five times, read the report.

Now week 5 hands the student a case with a genuine conflict in it, and the
conflict is one that really happened to this project rather than one invented
for the exercise. An alert says mail left the company, and it is correct: the
outbox holds a message addressed outside the organisation. The obvious
conclusion is that customer data was exfiltrated. The evidence says otherwise:
the recipient is the customer, at their own address, and the planted token is
not in the message. The agent answered a customer, which is its job.

That case, A5, reported VULNERABLE five times out of five for weeks against an
attack that never landed, because its detector asked only whether mail had left
the company. Naming the recipient is what turned a claim about mail into a
claim about theft. The students are being handed the exact false positive that
fooled the people who built the course, which is a better week than any
scenario written to be a good scenario.

Week 5 ends in the call, week 6 builds the control that call implies, and week
7 runs it against the class. **The control the student builds in week 6 is the
one they themselves recommended at the end of week 5**, which turns the best
moment of the course from a demonstration into a payoff.

**An earlier version of this section described a different conflict** and it
was false: it said the agent's trace would claim the mail was sent while the
outbox showed the guard had stopped it. Checking `agent/loop.py` showed the
trace records a blocked call as blocked, with the reason, so the two sources
would agree and there would be no mystery at all. The scenario above is
producible because it has already been produced.

The analyst note in the pack carries a plausible wrong claim, which is where
the old "take apart a supplied poisoned report" exercise went. It is the same
skill, in a case the student cares about, instead of a worksheet.

**Week 7 was wrong in an earlier draft and the fix improves it.** It paired
the week 3 disclosure with a control at the tool boundary. That control cannot
work: the disclosure appears in the model's own text, and a tool-boundary check
gates tool calls, not text. The week now pairs the control with the outbound
mail, which it genuinely stops, and then runs it against the disclosure as a
deliberate negative result. "Here is a control that works, here is the same
control failing, and here is why" is a better week than the one that was
broken.

**The `read_evidence` tool is the one real build this needs, and it is not
twenty lines.** Review was right to push on that. Evidence spans JSONL traces,
JSON reports, exported audit rows and outbox messages, and the outbox lives
outside `runs/`. The tool has to be read-only and bound to a manifest that
names what it may open: canonicalise the path, reject traversal, accept only
the listed files, cap the size, and return numbered records so a claim can cite
one. The agent gets no write tool and no send tool. That is a day's work, not
an afternoon, and it is also the week's second lesson: the student has just
scoped an agent's access, which is week 2's inventory turned around.

**Severity is not asked for.** An earlier draft wanted the agent to rate
severity. Severity is not recoverable from an audit row; it needs impact, scope
and likelihood the evidence does not contain. Every question asked instead is
checkable against a file, which is the point.

**What ships in the case pack**, generated once from a real run so nothing in
it is invented: two agent traces, an exported `audit.jsonl` so the exercise
does not depend on a running database, three preserved outbox messages, one
analyst note containing a confident wrong claim, and a manifest naming what the
agent is allowed to read.

### 3a. Where the code reading actually lives

The coordinator asked for enough scripting to recognise things in the output of
coding agents. That is one week of concentrated teaching and then a thread
through the rest, because a skill taught once in week 1 and never used again is
a skill nobody keeps.

| Wk | What kind of reading | Whose code |
|---|---|---|
| 1 | The four questions, taught and practised: what does it read, what does it change or send, can that be undone, what decides whether it happens | Four supplied scripts of rising length, the last written by a coding agent |
| 2 | The same four questions, on the system under study. Then change one setting, predict the effect on a run, and check | The agent's own tool definitions and configuration |
| 4 | Reading for absence, which is harder: find the check that is not there | The target's customer lookup, which never asks who is calling |
| 6 | Verifying somebody else's claim about code | The assistant's account of what the evidence shows |
| 7 | The smallest possible write: one list and a four-line guard | Their own |

**No student writes code from a blank file, and the only authoring is in week
7.** The progression is deliberate: read someone else's code, read the code that
runs your lab, notice what is missing from it, check a claim about it, change
it. Each rung is small and each one is grounded in something the student has
already seen.

**This is also how the course makes its closing argument.** A student who has
spent seven weeks finding that they can *almost* read the code, and that the
almost is what stands between them and catching the agent's mistake, does not
need to be told to go learn programming.

### 3b. The reference shelf, which does the work the course does not

The course teaches six pieces of syntax and then recognition, and stops there.
Naming assignment, a function call, `if`, `for`, `import` and opening a file is
about forty minutes, and without it the four questions are a ritual: a student
who cannot tell a function call from a variable cannot say what a script
touches, and the supervision argument the course rests on does not stand up. It
does not teach a language beyond that, and should not pretend to in seven weeks
with no prerequisite. What it does
instead is hand every student a short shelf and tell them plainly which one to
open for which problem. A student who wants to go further has somewhere to go
on the day they want it, which is the only moment that matters.

All six are free, need no account, and were checked on 31 August 2026.

| Resource | What it is for | Access and licence |
|---|---|---|
| [Python Tutor](https://pythontutor.com/) | Paste a script, step through it one line at a time, and watch what changes. This is the single best fit for the four questions, because it answers them visually | Free, runs in the browser, no account |
| [futurecoder](https://futurecoder.io/) | A full beginner course that runs entirely in the browser with nothing installed | Free and open source, no account |
| [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/) | The friendliest first book, and the one whose examples look most like scripts a student will actually meet | Free to read online, CC BY-NC-SA 3.0 |
| [Python for Everybody](https://www.py4e.com/) | The same ground with video, for a student who would rather be shown than read | Free |
| [Software Carpentry: Programming with Python](https://swcarpentry.github.io/python-novice-inflammation/) | A structured lesson written for researchers, useful for a student who wants exercises with answers | CC-BY 4.0 |
| [The Python Tutorial](https://docs.python.org/3/tutorial/) | The authoritative reference, for looking up what something means rather than learning from scratch | Free, part of the language documentation |

**Two of these run in a browser with nothing installed**, which matters: the
student most likely to want more help is the one on a locked-down laptop, and
Python Tutor and futurecoder both work there.

**One licence note for whoever assembles the pages.** Automate the Boring Stuff
is CC BY-NC-SA 3.0, so the course links to it and does not copy passages into
its own handouts. Reproducing it would create a derivative work carrying the
ShareAlike obligation, which is the same trap the framework documents present.

**The shelf is also the honest answer to the closing argument.** A course that
tells students they will want to learn programming, and then does not say where
to start, has given advice instead of a path.

### 3c. Scripts they can run, read, and change

The shelf in 3b is for a student who wants to learn a language. The corpus
below is for the other twenty-four: short working scripts that do something
they actually want done, operating on their own data, which they read first,
run second, and change third.

This is the better teaching corpus because motivation is built in. "Read this
example" is an assignment. "This prints your own canary tokens, and here is how
to make it print the ones in your outbox too" is a reason.

| Script | Week | What it does for the student | The change they are asked to make |
|---|---|---|---|
| `show_my_tokens.py` | 1 | Prints their three canary tokens, which they need from week 3 onward | Print the gate code as well |
| `count_tool_calls.py` | 1 | Reads one trace and reports how many tool calls the agent made | Report the busiest run across a whole folder |
| `read_report.py` | 1 | Reads a harness report and prints each case with its rate | Sort so the vulnerable cases come first |
| `who_touched_what.py` | 4 | Reads exported audit rows and prints who did what to which customer | Filter to one actor, which is week 4's whole point |
| `search_outbox.py` | 5 | Searches preserved outbox messages for a string | Report which message it was in, not just whether it was there |

**Week 1 uses the first three, against bundled sample data**, because a student
in week 1 has generated nothing yet. The other two arrive in the week whose
evidence they read.

Each is twenty to forty lines, commented in the course's voice, and does one
thing. The requested change is one or two lines and is checkable by running it.
None requires writing from a blank file, which is the line the course does not
cross.

**One of them needed care, and checking found it.** The harness clears the
outbox before every trial, so a student who has just run the suite has an empty
outbox and a search over it finds nothing. That is why `search_outbox.py` now
sits in week 5, against the preserved messages in the case pack, rather than in
week 1 against nothing. It is also worth teaching rather than hiding: a test
that does not clean up between trials reports trial one's mail as trial two's
success, which is the reasoning the whole course is built on.

The other four have data: traces and reports accumulate per run, the audit log
is read over the API, and the tokens are derived rather than stored. Verified
against a real suite run: 3,080 traces and 212 reports present, outbox empty.

**They are also the answer to the four questions, applied to code the student
has a reason to care about.** `who_touched_what.py` reads a file, changes
nothing, cannot do harm, and runs unconditionally. `search_outbox.py` reads a
directory. Neither sends anything anywhere. A student who can say that about
these five can say it about a script a coding agent hands them, which is what
the coordinator asked for.

**Most of this already exists in some form.** `python -m common.canary` already
prints the tokens; the harness already writes the reports these read. What is
needed is the small, commented, single-purpose versions, and they are cheap.

## 4. The deterministic backstop, and what it fixes

**The problem.** Models are unpredictable, and an outcome that depends on one
misbehaving is an outcome graded on luck. In week 3 one student's five trials
can all refuse while a classmate's leak four times, from identical correct
work. The measured disclosure rate is 4 of 5, which means roughly one student
in a class of 25 sees zero.

**The fix is already half built.** The course ships an offline `mock` provider:
about 400 lines of pattern matching that behaves like a very gullible
assistant. It is deterministic, and its variability is a seeded hash rather
than randomness (`agent/mock_model.py:155`), so the same student always gets
the same answer and can re-run to check their own work.

**What changes.** The mock gains a per-case target rate, so the course author
decides what each case demonstrates, and the pattern of which trials hit is
derived from the student's own ID. Every student sees the same rate; no two see
the same pattern; nobody's evidence is copyable.

**How it is used.** The live local model is the default, because that is where
the real lesson is. The mock is the backstop, in three situations:

1. **A machine that cannot run a model.** This replaces the recorded evidence
   bundles an earlier draft proposed, and it is strictly better: the student
   runs it on their own machine, with their own tokens, and gets a real
   interactive loop rather than watching someone else's recording. It also
   covers weeks 1 and 2, which the recording fallback did not.
2. **A guaranteed outcome when the course needs one.** Week 6's lesson requires
   the assistant to make a catchable mistake. A real model may make a subtle one,
   or none.
3. **The instructor's demonstration**, which has to work in front of a class.

**The honesty rule stays, and it is not negotiable.** Every report already
carries a banner when the provider is mock, saying the numbers are not evidence
about how any real model behaves. The course keeps it, teaches why it is there,
and treats a student who cites a mock run as evidence about a model as having
made the exact error the course exists to correct. Where a student has both
runs, the comparison is itself a finding: the simulator falls for it every
time, and the real model did not.

## 5. Portfolio: optional, ungraded, and separate

Every artifact below is produced as ordinary graded coursework. **Packaging any
of it for a portfolio is optional and carries no points**, because not every
student wants one and nobody should be graded on choosing. An earlier draft
listed two artifacts the weeks did not actually assign, which would have made
the optional portfolio an unannounced extra project during the final crunch.
These three are assigned.

| Artifact | Produced in | Why it is worth showing |
|---|---|---|
| The evidence file | Final block | A short assessment report on a live agentic system, every claim traced to a recorded check. Most entry-level portfolios have nothing like it |
| The verification record | Week 6 | Where an AI assistant was right, where it was wrong, and how the student knew. This is the rarest thing in the list and the most current |
| The control, measured | Week 7 | A fix with a before and after, and a benign case proving it did not just delete the feature |

Two things the optional module has to teach, because both are real: canary
tokens in a student's evidence are derived from their college ID and must be
scrubbed before anything is published, and neither repository has a licence file
yet, so nothing should be encouraged into public view until one exists.

## 5a. Safety, privacy, and what to tell a parent

The course asks students, some of them sixteen, to make an AI system disclose a
credential. That deserves a plain answer rather than a wording strategy, and the
technical facts are better than the optics suggest.

| Question | Answer |
|---|---|
| Is anything real? | No. The credential is invented, the customers are invented, and the mail domains are reserved example domains that cannot receive mail |
| Can it reach anything? | No. The target listens on the loopback address only. The runner refuses to test any host that is not the authorized target and records the refusal |
| What are students forbidden to do? | Anything outside the provided target, their own agent, and a local model. Never a commercial AI service, never a third-party system. This is week 1, it is graded, and it gates the rest of the course |
| What if a student finds something real? | They stop and tell the instructor. The course says so and says why |
| What personal data is in a student's work? | Their college ID is written into harness reports, and their canary tokens are derived from it. This is deliberate, so that evidence cannot be copied between students. **It is also why publishing is optional and why scrubbing is taught.** For students under 18 this should be reviewed against district records policy before the course runs |

That last row is an open item, not a solved one. It is flagged here so it is
decided by the right person rather than by default.

## 5b. Breadth, as three cases with evidence and a decision

Seven weeks cannot cover the agentic security surface, and two earlier attempts
at this section were both wrong. The first named the omitted risks on one page,
which is a glossary. The second made seven ten-minute cards asking the same four
questions of seven one-line scenarios, which review correctly called a glossary
converted into a repeated worksheet.

Three cases instead, twenty-five minutes each, in the final block. Each carries
evidence to read and ends in a decision the student has to defend, which is the
same shape as weeks 5 and 6 and therefore needs no new skill.

**Case one: the agent remembers.** A support agent tells the assistant something
in confidence on Monday. On Tuesday a different customer gets it back. You are
shown two conversation records and a configuration file. Decide: is this a bug in
the agent, a bug in the deployment, or working as designed, and what would you
turn off tonight?

**Case two: the helpful tool.** Your team installs a package of tools written by
someone else. One tool's description, which the model reads and the humans do
not, carries a sentence aimed at the model rather than at you. You are shown the
tool manifest and one trace. Decide: what did the agent do, who authorized it,
and where does the review have to happen so it cannot recur?

**Case three: the script that ran.** The assistant writes a script and something
executes it before a person reads it. You are shown the script and the log.
Decide: apply week 1's four questions, say what it touched, and name the single
control that would have stopped it.

**The same four questions run through all three:** what crossed a trust
boundary, what authority was available at that moment, what evidence would show
whether it happened, and where must the control live. A student who can ask
those of a scenario they have never seen has a method, and the method is what
transfers. The remaining risks (data retention in traces, runaway cost,
multi-agent chains) are named in the wrap-up without a case, and this proposal
says so rather than implying coverage.

## 5c. What job this prepares a graduate for

A committee will ask, and the honest answer is narrower and more useful than
"AI security".

**The realistic first role for a Cyber Defense graduate is tier one security
operations**: an analyst who receives alerts, works out what actually happened,
decides whether it is an incident, contains it or escalates it, and writes it
down so the next person can act. That is the job this course is aimed at.

**It does not produce an AI security specialist, and should not claim to.** What
it produces is a tier one analyst who is not helpless the first time an agent
shows up in their queue, which is a thing that is now starting to happen and
which almost nobody arrives able to do.

| Outcome | The task it maps to on shift |
|---|---|
| 1. Describe how an agentic system operates from its recorded run | Reconstructing what happened from an unfamiliar telemetry source. The specific source is new; the skill of reading a log you have not seen before and saying what the system did is the daily work |
| 2. Interpret a short script to determine what it accesses and changes | Triaging a flagged script. "This one-liner fired an alert, what does it touch" is among the most common tier one questions, and increasingly the script was machine written |
| 3. Analyze an agent's tool configuration to identify irreversible actions | Scoping and impact assessment. What could this account or service have done, and what cannot be undone, which is what decides urgency |
| 4. Differentiate evidence from assertion | The single most valuable discipline on a tier one desk. The alert claims something; does the recorded evidence support the claim. This is what separates an analyst who escalates well from one who escalates everything |
| 5. Interpret repeated-trial results, including results showing no effect | Detection reliability. Understanding that one clean run is not proof, that a negative result has a confidence attached, and that "no alert" is not "no problem" |
| 6. Apply a control at a tool boundary and verify its effect | Containment and validation. Did the block actually work, and did it break something legitimate. The second half is what gets a containment reversed at 2am |
| 7. Evaluate AI generated output against source evidence | The newest of these and the most immediately employable. Security tooling now summarises, triages and drafts. Analysts are being asked to act on that output, and a graduate who verifies it against the source rather than forwarding it is worth more than one who does not |

**Outcomes 4, 5 and 7 are the ones worth arguing for in front of a hiring
manager.** They are transferable off the lab entirely: they are about how to
treat a claim, and they apply to a SIEM alert, a vendor report or a model's
summary equally.

**What this course does not prepare anyone for**, stated so nobody oversells it:
no SIEM, no endpoint tooling, no network forensics, no malware analysis, no
Windows or directory internals. It is one elective. The Cyber Defense degree's
identity rests on forensics and incident response, and this complements that
rather than substituting for any of it.

**One programme-level consequence, recorded because it is easy to forget.** The
Cyber Defense AAS sits at exactly 60 semester credit hours, which is the Texas
statutory ceiling. Adding a three credit hour course to the degree plan means
removing three from it. That is a programme decision and not a course decision,
and it is separate from offering this course as an elective or in a certificate.

### The NICE Framework mapping, verified

Checked against NICE Framework components **version 2.2.0, released 28 April
2025**, downloaded from the NIST Cybersecurity and Privacy Reference Tool rather
than recalled.

The target role is **PD-WRL-001 Defensive Cybersecurity**, in the Protection and
Defense category. **PD-WRL-003 Incident Response** is adjacent and shares much of
the mapping.

| Outcome | NICE task statements it serves |
|---|---|
| 1. Describe how an agentic system operates from its recorded run | T1391 Reconstruct malicious attacks; T1299 Determine causes of network alerts; T1489 Correlate incident data |
| 2. Interpret a short script to determine what it accesses and changes | T1348 Distinguish between benign and potentially malicious cybersecurity attacks and intrusions; T1370 Collect intrusion artifacts |
| 3. Analyze an agent's tool configuration to identify irreversible actions | T1351 Determine impact of malicious activity on systems and information; T1020 Determine the operational and safety impacts of cybersecurity lapses; T1252 Determine the scope, urgency, and impact of cyber defense incidents; T1548 Determine adequacy of access controls |
| 4. Differentiate evidence from assertion | **T1112 Validate network alerts; T1387 Validate intrusion detection system alerts.** The outcome is close to a restatement of these two |
| 5. Interpret repeated-trial results, including results showing no effect | T1254 Determine the effectiveness of an observed attack; T1583 Determine effectiveness of system implementation and testing processes |
| 6. Apply a control at a tool boundary and verify its effect | T1177 Determine if security control technologies reduce identified risk to acceptable levels; T1371 Mitigate potential cyber defense incidents; T1251 Recommend incident remediation strategies |
| 7. Evaluate AI generated output against source evidence | **No task in the framework.** See below |

The week 5 handover form serves T1332 Produce incident findings reports, T1333
Communicate incident findings to appropriate constituencies, T1316 Document
cyber defense incidents from initial detection through final resolution, and
T1242 Escalate incidents that may cause ongoing and immediate impact.

### The gap this course actually fills, and it is a real one

**NICE 2.2.0 contains 962 task statements and not one of them mentions AI.**
Checked directly against the component file.

AI appears in the framework only as a competency area, **NF-COM-002 Artificial
Intelligence (AI) Security**, carrying six knowledge statements and three
skills. One of those skills is **S0957, identifying possible mistakes or
hallucinations in AI generated outputs**, which is outcome 7 almost word for
word.

**No work role carries any of them.** PD-WRL-001 Defensive Cybersecurity holds
none of NF-COM-002's knowledge or skill statements, and neither does any other
role in the framework.

So the position to take to a committee is precise: this course teaches a
competency area NICE has defined and named, to students entering work roles
NICE has not yet connected it to. That is not the course being out of step with
the framework. It is the course being where the framework is going, one revision
early, and it is the strongest single argument for offering it now rather than
waiting.

## 6. What makes this different from what other schools teach

Stated honestly, because parts of it are common.

Not distinctive: prompt injection demonstrations, AI policy discussion, and
"try to jailbreak a chatbot" appear on many syllabi.

Distinctive, specifically:

- **The student is responsible for the agent, not attacking someone else's.**
  Almost all agentic AI security teaching is offense-shaped. This is the job
  the market is creating.
- **Findings are graded on side effects, not on what the model said.** The case
  format will not accept a text-match detector. A student reports "4 of 5 with
  the token pasted", never "it worked".
- **Evidence cannot be copied.** Tokens are derived per student, so a classmate
  can share a working payload, which is fine and is how the field works, and
  cannot share the proof that it worked in your environment.
- **It runs on a locked-down laptop with no account, no key and no internet.**

## 7. What is verified, what is not, and what is still open

**Verified by measurement**, on the model the course would ship, over 46 agent
runs through the real student path: the agent discloses its system prompt and
the credential in it 4 times in 5; it sends mail outside the company with no
approval 5 times in 5; any caller can read any customer record 5 times in 5,
with the audit log recording it perfectly and stopping nothing.

**Not verified: that a college loaner will run the bundle.** That is a policy
question for whoever owns the image, and it is why the deterministic backstop in
section 4 exists. With the backstop, a blocked machine costs a student the live
comparison, not the course.

**A limit to state to students in week 1:** indirect prompt injection, the
attack everyone has heard of, does not reliably complete on a small local model.
Hidden instructions do steer the agent into fetching a record it was not asked
for; the last step does not land. The course teaches that as a real result about
a real system, which is a better lesson than a staged success.

### Open items, each needing a decision or a build

**The lab in `labs/` still implements the previous course, and that is
expected rather than a defect.** This proposal is a clean sheet. The existing
implementation was built for a version that assumed students would construct an
agent over four weeks, so it carries student exercises this course does not
assign: writing the retry logic in `llm.py`, writing `get_customer`, designing a
second tool and its schema, and a README that tells students to obtain an API
key in week 2. None of that is a contradiction to resolve. It is the old course,
waiting to be rebuilt against the new one.

What carries over is the machinery rather than the assignments: the target, the
agent loop, the trace, the harness, the detectors, the canary derivation, the
cartridge build and the video pipeline. What gets rewritten is everything that
told a student what to do.

Two reviews of this proposal read the existing lab as though it were the
implementation of this design and reported the mismatch as a fault. It is worth
recording that it is not, because the same reading will happen again.

**The rebuild list, then:** ship `get_customer` working rather than as an
exercise; retire the Module 1 to 4 extension points; align the README, the
config and the portable bundle on a local model with no key; add the
`read_evidence` tool and the case pack; give the mock per-case target rates; and
make the outbox evidence string carry its content.

| Item | Who or what settles it |
|---|---|
| Contact hours, points and rubrics are not yet allocated | Needs doing before submission. Week 1 now carries the demonstration, the inventory, the syntax and the scope gate, and the final block carries a report, a where-next note, an open book exam and three cases. Both were flagged by readers as uncosted, and both should be costed rather than assumed |
| Student college IDs are written into harness reports | District records policy, for students under 18 |
| Neither repository has a licence file | Whoever owns courseware IP, before any student is encouraged to publish |
| The mock needs per-case target rates | A small change to `agent/mock_model.py`, plus one authored rate per case |
| Weeks 5 and 6 need a `read_evidence` tool and a case pack | A day, not an afternoon: read-only, manifest-bound, path-canonicalised, size-capped, returning numbered records. Plus the pack itself, generated once from a real run |
| The outbox detector cites a file that the next trial deletes | The evidence string should carry the message content, the way the canary and audit-row detectors already do. Small fix, and it is what makes "evidence a stranger can check" true rather than nearly true |

### How this proposal was reviewed

Four course concepts were designed independently and judged by three lenses: a
dual-credit student, the curriculum committee, and the instructor who has to
build it. All three ranked the same concept first and all three named the same
three flaws, which are handled above rather than left to be found later.

The result was then reviewed adversarially by a separate agent working from the
repository rather than the proposal, which found thirteen defects. The
consequential ones are fixed here: the outcomes were compound and are now single
claims; week 1 expected novices to catch an agent's mistake using skills the
course declined to teach, and now teaches them; week 7 paired an attack with a
control that could not touch it; week 6 asked an agent to read files it had no
tool to open, and to rate a severity the evidence could not support; the
portfolio promised work the weeks no longer assigned; and the coding-agent
comparison asserted a maximum-privilege agent that does not exist.

One finding was checked and found half right: the harness deletes outbox files
between trials, so an evidence string naming a file no longer resolves, but the
canary and audit-row detectors carry their content inline and stand on their
own. One was checked and found wrong in its reasoning but right in its
conclusion, which is the week 7 control above.
