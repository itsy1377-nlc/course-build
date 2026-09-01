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
| **C. Using one for the work** | 1, 6, and throughout | Where an agent genuinely helps a security analyst, how you check it, and what you would need to learn to supervise it well |

**One idea holds all three together: evidence over assertion.** When you test an
agent you do not believe what it says it did, you look at what the system
recorded. When you *use* an agent you do not believe what it tells you either,
you check it against the source. It is the same discipline pointed in two
directions, and it is the through line of the course.

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

Seven, and each one is a single observable claim. An earlier draft had six that
each bundled three or four capabilities together, which cannot be scored: a
student could satisfy half of one and there would be no way to say which half.
The criteria live in the rubric, not inside the outcome.

| # | Part | Outcome | Assessed by |
|---|---|---|---|
| **1** | A | Describe what an agentic AI system did during a recorded run, identifying each step as a model decision, a tool call, or a returned result. | An annotated trace of the student's own run |
| **2** | A | Read a short script and state what it reads, what it changes or sends, and what condition decides whether it acts. | A code-reading worksheet in week 1, and the located missing check in week 4 |
| **3** | A | Determine, from an agent's tool configuration, which of its actions cannot be undone. | The blast-radius inventory |
| **4** | B | Support a claim about an agent's behavior with recorded system evidence, and reject a claim whose only support is the agent's own account of what it did. | The evidence line in each pack; a teardown of a supplied results file that claims more than it found |
| **5** | B | Report the result of a repeated-trial test as a rate with its controls, and state what a no-hit result does and does not establish. | A harness report with a written reading of it |
| **6** | B | Implement a control at an agent's tool boundary and verify with paired runs that it stops the unauthorized action while authorized use still works. | The control, two reports side by side |
| **7** | C | Verify an AI assistant's output against source evidence, recording each claim as accepted, corrected or rejected with the reason. | The verification record |

**Outcome 2 is new and it is the coordinator's scripting ask, made assessable.**
An earlier draft had no code-reading outcome at all; it put students in front of
an agent's explanation of a script and asked them to find the error, which
requires exactly the skill the course had declined to teach. That is not
instruction, it is a trap. Week 1 now teaches the four questions and the course
assesses them.

**Outcome 5 is worded so that a correct test with no hits is a pass.** A student
whose five trials all refuse has done the work correctly and must be able to
show mastery. Stating what a no-hit result does not establish is the harder
skill anyway.

**A note for the committee on levels.** Outcomes 1 to 3 are describe and
determine, which is right for weeks 1 and 2 of a course with no prerequisite.
Outcomes 4 and 5 are the analytical core. Outcomes 6 and 7 are apply and
verify, and both are reached in the last third, after the scaffolding.

## 3. Week by week

| Wk | Part | Title | What the student does | Artifact |
|---|---|---|---|---|
| 1 | A | Four questions you can ask any code | Get the environment running. Meet four questions to ask about any short script: what does it read, what does it change or send, can that be undone, and what decides whether it happens. One worked example, then the starter scripts from 3c, which operate on their own data and which they run before they read. The last is one a coding agent wrote. Anyone who wants more than that is pointed at the shelf in 3b rather than taught a language | Code-reading worksheet; Rules of Engagement gate at 100 percent |
| 2 | A | What is actually happening | Run one ordinary request and read the replay in plain English: which line was the model deciding, which was code running, which returned a result. Meet the shape every agent has: a model, tools, and a loop. Inventory what this agent can reach, using week 1's four questions on the tool source itself. Then change one setting, the loop's step limit, predict what a run will look like afterwards, and check | Annotated trace; blast-radius inventory; the predicted and observed effect of one setting |
| 3 | B | Make it talk | Ask the agent to repeat its own instructions; watch it hand over a credential stored there for convenience. Five trials, report the rate, including the trials where it refused | Evidence pack 1: disclosure |
| 4 | B | Make it act, make it fetch | Ask it politely to mail an outside address; nobody approves it. Then run as a support agent with no business seeing a customer, and get the record anyway. Find the missing check in the source. Read the audit row and notice whose name is on it | Evidence packs 2 and 3 |
| 5 | B | Rates, not vibes | Run the whole harness and read every part of it: provider banner, scope refusal, detector self test, controls. Post your week 3 rate on the class board and look at the spread. Take apart a supplied results file that claims more than it found | Harness report with a written reading; results teardown |
| 6 | C | Put it to work, then check it | Give the agent read access to your own evidence from weeks 3 to 5 and ask it three checkable questions: what happened, in what order, and who does the audit log name. Check every claim against the file it came from. Mark each accepted, corrected or rejected | Verification record; judgment note |
| 7 | B | One rule that holds, and one that cannot | Try to stop the outbound mail with a firm instruction in the prompt. Measure it. Then add a recipient allowlist in code and measure again, confirming the benign escalation still works. Then try the same control against the week 3 disclosure and find that it does nothing, because that disclosure never crosses a tool boundary | The control, paired reports, and a written account of why the second attempt could not work |
| Final | | The evidence file | Three findings on fixed headings, each tracing to a recorded check, plus the control with its before and after, plus what the assistant got wrong in week 6, plus a short note on what you would learn next and why | The report; the where-next note; a short exam |

**Week 7 was wrong in the previous draft and the fix improves it.** It paired
the week 3 disclosure with a control at the tool boundary. That control cannot
work: the disclosure appears in the model's own text, and a tool-boundary check
gates tool calls, not text. The week now pairs the control with the outbound
mail, which it genuinely stops, and then runs it against the disclosure as a
deliberate negative result. "Here is a control that works, here is the same
control failing, and here is why" is a better week than the one that was
broken.

**Week 6 needs one new tool and is better for it.** The agent has no way to read
a trace or an audit log, so an earlier draft was really asking students to paste
text into a chat window and call it agentic. Adding a single `read_evidence`
tool, scoped to the student's own `runs/` directory, makes the exercise real. It
is also a teaching moment: the student has just granted an agent filesystem
read, so they run week 2's inventory on it and see the blast radius grow.

**Severity is not asked for.** An earlier draft wanted the agent to rate
severity. Severity is not recoverable from an audit row; it needs impact, scope
and likelihood that the evidence does not contain. The three questions asked
instead are all checkable against a file, which is the point.

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

The course teaches recognition and stops there. It does not teach a language,
and it should not pretend to in seven weeks with no prerequisite. What it does
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

| Script | What it does for the student | The change they are asked to make |
|---|---|---|
| `show_my_tokens.py` | Prints their three canary tokens, which they need from week 3 onward | Print the gate code as well |
| `count_tool_calls.py` | Reads one trace and reports how many tool calls the agent made | Report the busiest run across a whole folder |
| `search_outbox.py` | Searches the outbox for a string, which is how they find their own evidence | Report which message it was in, not just whether it was there |
| `read_report.py` | Reads a harness report and prints each case with its rate | Sort so the vulnerable cases come first |
| `who_touched_what.py` | Reads the audit log and prints who did what to which customer | Filter to one actor, which is week 4's whole point |

Each is twenty to forty lines, commented in the course's voice, and does one
thing. The requested change is one or two lines and is checkable by running it.
None requires writing from a blank file, which is the line the course does not
cross.

**One of them needs care, and checking found it.** The harness clears the
outbox before every trial, so a student who has just run the suite has an empty
outbox and `search_outbox.py` finds nothing. It works after a single agent run,
not after a harness run. That is worth teaching rather than hiding: a test that
does not clean up between trials reports trial one's mail as trial two's
success, which is the same reasoning the whole course is built on. But the
script's instructions have to say when to run it, and the evidence-preservation
fix in section 7 has to land, or a student's own evidence will be gone by the
time they go to show it.

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

## 5b. What this course does not cover

Seven weeks at introductory depth cannot cover the agentic security surface, and
a course calling itself broad should say what it leaves out rather than imply
completeness. Named in week 2 and in the closing week, at awareness level only,
with no exercise: memory and context poisoning; the supply chain of tools,
models and extensions; unsafe execution of generated code; validating an agent's
output before acting on it; sensitive data accumulating in logs and traces;
monitoring agents in production; runaway cost; and multi-agent systems where one
agent's output becomes another's instruction.

Naming them takes one page and one wrap-up discussion. Leaving them unnamed
would let a student finish believing agent risk is prompt injection plus broad
tools, which is the misconception this field most needs to stop producing.

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

| Item | Who or what settles it |
|---|---|
| Contact hours, points and rubrics are not yet allocated | Needs doing before submission. Two weeks look heavy on their face, week 4 with two investigations and week 7 with a control plus two measured runs, and that should be costed rather than assumed |
| Student college IDs are written into harness reports | District records policy, for students under 18 |
| Neither repository has a licence file | Whoever owns courseware IP, before any student is encouraged to publish |
| The mock needs per-case target rates | A small change to `agent/mock_model.py`, plus one authored rate per case |
| Week 6 needs a `read_evidence` tool | Roughly twenty lines, scoped to the student's own runs directory |
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
