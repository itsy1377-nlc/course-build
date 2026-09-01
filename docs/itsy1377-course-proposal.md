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
| **1** | A | Describe what an agentic AI system did during a recorded run, identifying each step as a model decision, a tool call, or a returned result. | The week 2 annotated trace of the student's own run |
| **2** | A | Read a short script and state what it reads, what it changes or sends, and what condition decides whether it acts. | The week 1 code-reading worksheet, and the missing check located in week 4 |
| **3** | A | Determine, from an agent's tool configuration, which of its actions cannot be undone. | The week 2 blast-radius inventory |
| **4** | B | Support a claim about an agent's behavior with recorded system evidence, and reject a claim whose only support is the agent's own account of what it did. | The evidence line in each pack (weeks 2 and 4); the wrong analyst claim caught in week 5 |
| **5** | B | Report the result of a repeated-trial test as a rate with its controls, and state what a no-hit result does and does not establish. | The week 3 run: a prediction, a rate, and an account of how far the chain went |
| **6** | B | Implement a control at an agent's tool boundary and verify with paired runs that it stops the unauthorized action while authorized use still works. | The week 7 control, and two reports side by side |
| **7** | C | Verify an AI assistant's output against source evidence, recording each claim as accepted, corrected or rejected with the reason. | The week 5 evidence-linked timeline and the week 6 handover note |

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
| 1 | A, B | Make it leak, then ask how you know | In the first half hour, before anything is explained: type the supplied request and watch the agent hand over the credential in its own instructions. Then the question the rest of the course answers, on the same page: how do you know it did that, rather than said it did? Only then the six pieces of syntax and the four questions, which arrive as the tools for answering it | The screenshot and the question answered in one paragraph; Rules of Engagement gate at 100 percent |
| 2 | A | What is actually happening | Read the replay in plain English: which line was the model deciding, which was code running, which returned a result. Meet the shape every agent has. Inventory what this one can reach, using week 1's four questions on the tool source. Change one setting, predict the effect on a run, and check. Then go back and prove week 1's leak properly, with the token, over five trials | Annotated trace; blast-radius inventory; evidence pack 1, disclosure |
| 3 | B | Hide an instruction and see how far it gets | Write your own. Plant an instruction inside a ticket or a knowledge base article, in your own words, aimed at a door you choose. Predict in writing what will happen before you run it. Run five trials. Then read the traces and report how far it actually got: did the agent read your document, did it obey, did it call a tool it was not asked to call, did anything leave | The student's own case file, the prediction, and the run with a written account of how far the chain went |
| 4 | B | Make it act, make it fetch | Ask it politely to mail an outside address; nobody approves it. Then run as a support agent with no business seeing a customer, and get the record anyway. Find the missing check in the source. Read the audit row and notice whose name is on it | Evidence packs 2 and 3 |
| 5 | C | The case | An alert fired: mail left the company. Give the assistant read access to the evidence pack and ask for a timeline: claim, time, actor, and the exact record each claim came from. Check every row against the source. The alert is true and the conclusion drawn from it is wrong, and the pack holds an analyst note stating the wrong conclusion confidently | The evidence-linked timeline, every row marked accepted, corrected or rejected |
| 6 | C | What you would do about it | Work out what happened from the evidence rather than from the assistant or the analyst note. Choose one containment step, say what evidence supports it, and say what you are not recommending and why. Write it as a one-page handover the next person could act on | The SOC handover note |
| 7 | B | One rule that holds, and one that cannot | Implement the containment you recommended. First as a firm instruction in the agent's prompt, and measure. Then as a recipient allowlist in code, and measure again, confirming the benign escalation still works. Then try the same control against week 1's disclosure and find it does nothing, because that disclosure never crosses a tool boundary | The control, paired reports, and a written account of why the second attempt could not work |
| Final | | The evidence file | Three findings on fixed headings, each tracing to a recorded check, plus the control with its before and after, plus what the assistant got wrong in week 5, plus a short note on what you would learn next and why | The report; the where-next note; a short exam |

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

Week 6 turns that into a decision, and week 7 implements the decision.
**The control the student writes in week 7 is the one they recommended in week
6**, which turns the best moment of the course from a demonstration into a
payoff.

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
| Contact hours, points and rubrics are not yet allocated | Needs doing before submission. Two weeks look heavy on their face, week 4 with two investigations and week 7 with a control plus two measured runs, and that should be costed rather than assumed |
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
