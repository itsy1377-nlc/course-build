# ITSY 1377, the funded proposal

A second proposal, to sit beside `docs/itsy1377-course-proposal.md`. Same seven
outcomes, same seven weeks, same students. Different course, because the
environment is different.

**The scenario.** A server on the school network hosts a per-student isolated
Jupyter notebook. A gateway gives each student their own token and a budget
under ten dollars a semester, with all activity logged under school control. An
AWS Bedrock contract supplies two or three permissively licensed open models
against three hundred dollars per class. The school takes responsibility under
the contract, which resolves the age question.

---

## Status

**An earlier version of this document took the constrained course and added
hosted comparison columns to it.** A panel of six readers scored that worse than
the constrained original on both interest and fun, twice, with nobody enrolling
eagerly. The diagnosis was that comparison tables and second-model re-runs are
what scarcity thinking produces when handed money, and that no amount of
adjustment to a wrong frame fixes it.

This version was designed from what the environment enables. It was one of four
independent designs judged by a student, a practitioner and an operating
instructor. It ranked first on interest with all three and first on fun with two,
scoring 8.0 for fun and 8.7 for interest against the previous version's 5.8.

**All three judges named the same fatal flaw and it is addressed in section 6.**

The environment analysis in sections 8 to 10 survives from the earlier version.
It was corrected across two adversarial reviews and is about the environment
rather than the course, so it carries over.

---

## 1. The course in one line

**In the first twenty minutes of week one you make a model call your own code,
and for six weeks afterwards everything you attack, defend and prove is the
agent you built.**

That is the whole design. One artifact, made in week 1, carried to week 7.

---

## 2. What you actually look at

Every panel round of the constrained course said the same thing: there is
nothing to look at. It produced JSON lines, YAML and terminal text, because a
terminal cannot produce anything else. A notebook can, and this is the single
largest thing the funded environment buys.

**The filmstrip** is one agent run drawn as a row of boxes, left to right in
time order. One box per thing that happened: what the student asked, what the
model decided, what it called and with which arguments, what came back, what it
answered. A coloured left edge carries the meaning: blue for an action, green
for a result, red for an error or for an action that cannot be undone. A bar
across the top shows money spent.

A student glancing at it can see whether their agent did anything irreversible
without reading a line of JSON. The current course teaches that by having them
read twenty thousand characters of it.

**The blindfold** is one checkbox on the filmstrip. Tick it and everything the
model never received greys out, leaving only what it did. The hardest question
in the course, what did it actually know when it decided that, answers itself.

**The trial grid** is twenty runs of the same thing as twenty squares filling in
live. Sometimes twenty blue. Sometimes thirteen and seven. Sample size stops
being a rule and becomes a picture.

**The workspace diff** shows what a tool did to the student's own files, before
and after, in green and red.

**The boards** are projected: every student's agent in week 1, and in week 7
every attack and every defence with names against them.

**This is measured, not estimated.** A working filmstrip renderer is 68 lines of
Python, built and rendered against a real trace from this repository. The full
set is about 440 lines, two to three days for a working version and about a week
to make it good. Section 7 has the breakdown. The reason it is cheap is that
`agent/trace.py` already records everything it needs: the filmstrip is a view,
not a feature, and the agent does not change at all.

---

## 3. The seven weeks

| Wk | Title | What the student does | What is on screen |
|---|---|---|---|
| **1** | Twenty minutes | Take a working four line function, change one line of it, add one decorator, and watch a model decide by itself to call it. Then break it six ways on purpose and watch what changes: delete the description, describe a different function, make it raise, make it return far too much, cut the step limit, take the tool away. Add a second tool that writes a file, and answer the question that raises: which of your two can you undo? | The filmstrip drawing itself live; tool cards; the blindfold; twenty five agents appearing on a projected class board |
| **2** | The blindfold | Two tools with the same code and different descriptions. Which does the model pick, twenty times? Change one word and run again. Find one edit that moves the grid and one that does not, and get credit for both. Then see the model's actual input as stacked blocks with token counts, and find your own tool descriptions sitting in it | Trial grids filling square by square, side by side as edits accumulate; the context window as coloured blocks |
| **3** | Somebody else's function | Write a tool that genuinely does what it says and one extra thing it does not mention. Three classmates' tools are installed blind in your agent, and you have forty five minutes to work out what each really does, from the code and from what your filesystem looks like afterwards | The workspace diff; anonymous tool cards; your own agent behaving strangely |
| **4** | English versus Python | A tool arrives that returns text strangers wrote. Put text in a ticket that makes your own agent call your own irreversible tool. Twenty trials. Then, before reporting any result, run the positive control: put the same instruction in your own message instead. If it fires there and not from the document, your instrument works and your null is real | Two grids side by side, one mixed and one solid; filmstrips that stop part way |
| **5** | Watch it spend | Predict what a runaway loop will cost, in cents, then build one and run it on a separate burnable key. Watch the bar drain. Then write the cap, in your own code, and run it again | The budget bar draining live; a black cap card ending a run mid-flight; before and after with the cost difference |
| **6** | It told me something false | An incident pack built from your own records across weeks 3 to 5, your own installs, your own runaway, with one intruder mixed in. An assistant summarises it. Check every line against the file it came from and mark each accepted, corrected or rejected | A timeline colouring green and red as your own checker runs |
| **7** | The gauntlet | Turn on every control you built. Then two rounds, live: your defences against the class's attacks, and your attacks against theirs | Two boards updating on the projector during play, everyone named on both |

**Week 4 is the week that must work whichever way the measurement goes.** It is
built so that a negative result is the expected and fully creditable outcome,
and the positive control is what makes a null mean something rather than nothing.
If the chain never completes on any model, the student still produces a real
finding, with an instrument they proved was live.

---

## 4. The three mechanics that carry it

**The agent they built.** One artifact from week 1 minute 20 to week 7. Every
attack is against a thing they made, every control is in their own code, and by
the end it exports as a folder with a system prompt they wrote, six to ten tools
that are their own functions, and the controls they added.

**The cuckoo, in week 3.** Every student writes one tool that does what it
claims and exactly one thing it does not mention, and receives three classmates'
blind. All three judges called it the best single mechanic across the four
designs. It teaches supply chain, code reading and evidence at once, it cannot
be looked up because the answer is a classmate's, and it produces the second
best picture in the course.

**The boards.** Week 1 puts every student's agent on the wall. Week 7 puts every
attack and defence there, live. The constrained course's own review found the
class board its best loved mechanism and its worst placed, arriving only in the
final week.

---

## 5. How the outcomes are met

| # | Outcome | Where |
|---|---|---|
| 1 | Describe how an agentic system operates from its recorded run | Wk 1, the filmstrip of a system they assembled |
| 2 | Interpret a short script to determine what it accesses and changes | Wk 3, reading a stranger's tool, which is the literal week |
| 3 | Analyze a tool configuration to identify irreversible actions | Wk 1, assigning the flag to their own tools |
| 4 | Differentiate evidence from assertion | Wk 4 and 6, their own grids and their own incident |
| 5 | Interpret repeated-trial results including no effect | Wk 2 and 4, with the positive control making the null real |
| 6 | Apply a control at a tool boundary and verify its effect | Wk 5 and 7, in their own code, verified against classmates |
| 7 | Evaluate AI output against source evidence | Wk 6, against evidence generated from their own term |

---

## 6. The fatal flaw, and the fix

**All three judges independently named the same thing: week 1 minute 5 asks a
student to type `def` in a course with no programming prerequisite, and
everything in weeks 2 to 7 operates on what is built in minute 20.** If a third
of the room cannot write a function, they have no substrate and no recovery
path. As designed, that is fatal rather than risky.

**The fix is the rule this project already settled:** no student writes code
from a blank file. The starter function is already written, working, and running
in the notebook before the student touches it. They change one line of it. The
decorator infers everything else from the function's own signature and
description, so nobody hand writes a schema.

What survives is the thing that matters: **it is still their code that the model
calls**, because they changed it and they can read it. What goes is the blank
line, which was never load bearing and was doing all the damage.

**The second judge concern, that this is a lot to build, is answered by section
7 and by the measurement in section 2.** The instructor scored deliverability 2
out of 10 on the assumption that the visuals were a large custom build. They are
440 lines over about a week, on top of a data format that already exists.

---

## 7. What has to be built

| Piece | Lines | Note |
|---|---:|---|
| Filmstrip renderer and styling | **68, done** | prototyped against a real trace |
| Live update in place | 40 | built into the notebook, no dependency |
| Tool cards with schema inference | 90 | the real work: signature and docstring to schema |
| Blindfold | 15 | a style toggle |
| Trial grid, four way classification | 60 | hit, miss, refused, error |
| Context window view | 50 | stacked blocks with token counts |
| Workspace diff | 30 | wraps a standard library module |
| Nested filmstrip | 25 | recursion once cards exist |
| Class boards | 120 | the only piece needing shared state |
| **Total** | **~500** | two to three days working, about a week good |

**Three things that would blow that estimate.** The class boards are the only
genuinely hard piece, because they need state shared across students. The
notebook target must be pinned to one, since update behaviour differs between
them. And no widget library: the prototype avoids it entirely, which avoids a
whole category of version conflict in a shared server.

**Also to build, and not visuals:** the cuckoo distribution and screening, the
per student incident pack generator for week 6, the burnable key mechanism, and
the week 7 board. Plus the four items in section 9 that make measurement
trustworthy at all.

---

## 8. The measurement that gates week 4

The chain may or may not complete on capable hosted models, and the course is built so that either answer is a good week. It is still worth knowing before the term.

**The obvious reason to want this environment is wrong, or at least unmeasured.**
The appeal is that a capable hosted model would complete the indirect injection
chain, which a local 3B model does not. This project's own evidence points the
other way.

Model size was explicitly ruled out. `qwen2.5:7b`, `qwen3:8b`, `llama3.1:8b` and
`mistral:7b` all measured 0 of 5 on the exfiltration case, alongside
`granite4.1:3b`. Four payload variants and a rewritten agent role moved nothing.
The only thing that moved the number was rewriting the user's request to
authorise what the injection wanted, which stops it being an indirect injection
at all.

And the step that fails is recipient selection, which is exactly what safety
post-training targets hardest. **Capability and susceptibility plausibly move in
opposite directions on that last step.** A better model may be less likely to
comply, not more.

**But "model size was ruled out" is overstated, and the correction matters.**
Zero hits in five trials has a 95 per cent upper bound of roughly 45 per cent on
the true rate. An attack that succeeds one time in five shows zero in five about
a third of the time. Five trials cannot rule out a capability effect; they can
only fail to find one. The evidence is also confounded: at least one of those
models does not complete the two-turn loop at all, so its zero says nothing
about recipient refusal.

The honest statement is that the direction is unknown and the cheap evidence
leans against the optimistic reading. That is still a reason to measure before
building, and not a reason to claim the answer.

**So before a page is written, run a powered experiment rather than a screen.**
The version in an earlier draft of this document was incoherent: it said ninety
runs for three cases at five trials across three models, which is forty-five,
and it named a harness runner that cannot select individual cases and would
instead run the full suite at one hundred and eight. Neither number matched the
procedure.

What is actually needed:

- **At least thirty trials per model per case**, not five. Five is what produced
  the ambiguity in the first place.
- **An ordered chain detector**, so "reached step 3 of 5" is machine-produced
  rather than hand-marked. The schema currently pins detection to exactly one
  detector, so this is a prerequisite rather than a nicety.
- **A refusal and failure classifier**, so a refusal is not counted as a miss.
- **Positive tool-capability controls**, so a model that cannot drive the loop
  is not mistaken for one that declined.
- **Resolved model versions recorded**, randomised run order, and a repeat on a
  second day.

Cost is still small: roughly 270 runs at about 5,500 tokens is under 1.5 million
tokens, which is a few dollars at current open-model prices. **Two hours is the
part that is not credible**, since a local 8B probe measured 25 seconds per call
and hosted latency and quotas are unknown. Budget a day, and budget separately
for classifying the misses, which is the part that cannot be automated until the
chain detector exists.

**Write the course so either answer is a good week.** If the chain still does
not complete across three hosted models at thirty trials, that is a far stronger
finding than the constrained course has today.
---

## 9. The risk that sits under every number

**A gateway adds three new ways for a run to fail silently, and they are
indistinguishable from the course's proudest finding.**

**Narrower than an earlier draft claimed, and the narrowing matters.** An
ordinary rate limit arrives as a non-200 response, which the transport layer
raises on and the runner counts as an errored trial. That path is safe. What is
not safe is any failure that arrives as a well-formed 200 carrying empty or
declining content, which is what a content filter, a policy refusal, and some
budget-cap configurations produce. `agent/llm.py` returns that message and raises nothing. The loop then
produces a run with no tool calls. **That is not an errored trial**, so it enters
the denominator as completed with zero hits, and the verdict reads
`NO_HITS_IN_5`: exactly what a correctly conducted test of an attack that did not
land looks like.

The control path is worse. A control verdict prints a bare `OK` when hits equal
completed, with no sample size in the word, so a control whose last two trials
died on a budget wall reports `OK` on three trials against the harness's own rule
that a fix counts only if it holds all five. **Attacks carry their denominator;
controls do not.**

This invalidates every injection number in the course rather than one week's, and
the gateway is the first thing that makes it happen at classroom scale.

**Build before the first measurement, not after:**

1. A refusal and failure classifier with a distinct `REFUSED` status, separate
   from an errored trial and from a clean miss. Nothing else matters if this is
   skipped.
2. **Fix control validity, not only its display.** An earlier draft proposed
   putting the sample size into the control verdict. That makes an invalid
   result legible rather than making it invalid: the harness accepts three hits
   out of three completed trials after two errored, because its floor is three,
   and printing `OK 3/3` does not change that. **A control must be inconclusive
   unless every requested trial completes**, or errored trials must be re-run
   until five clean ones exist.
3. Capture token usage from the model response, which the loop currently
   discards, so a report can be reconciled against the gateway ledger.
4. Record the resolved, versioned model identifier rather than the gateway
   alias, and make the board refuse to mix versions. The pool stands for five
   weeks; a silently re-versioned endpoint makes it meaningless.

**One question isolation raises that a shared service did not.** Twenty-five
concurrent environments, each running a Flask target and an agent loop, is not
heavy, but it is twenty-five of everything: processes, ports, database files and
notebook kernels. That is a capacity question for whoever runs the server, and
the answer wants measuring with twenty-five simulated sessions before a graded
week depends on it, not on the morning of one. It belongs in the same load test
as the gateway ceiling.

### Two findings that change what is possible, not just what is risky

**Per-student isolation resolves the worst of these, and it is worth stating
what it has to mean.** The runner posts `/api/reset` before every trial, and the
target clears the outbox, the audit log and the beacon log. On one shared target
that means a student's trial silently deletes a classmate's evidence, and the
detector then reports a clean miss on an attack that actually landed. Isolation
removes that entirely, provided each student gets **their own target process and
their own database file**, not merely their own notebook against a common
service. The preflight assertion is still worth keeping: this project has twice
produced verdicts against the wrong tree at a scale of two, and a class is
twenty-five.

**On the canary question, an earlier draft of this section was wrong.** The
correction is below, and it turns out to favour this proposal rather than count
against it.

**A note correcting an earlier draft of this section.** It called classmate
token forgery a new hosted risk. That was wrong twice over, and the correction
is more useful than the claim was.

It is not much of a threat, because forging a classmate's token would need their
student ID and would achieve nothing anyway. The anti-copying property is that a
classmate can hand you a working payload, which is fine and is how the field
works, and cannot hand you the proof it worked in *your* environment, because
that proof carries *your* token. To cheat, a student does not need anybody
else's token. They need their own.

And their own was never a secret. `common/canary.py` prints it when run
directly, `show_my_tokens.py` is a week 1 starter script whose whole purpose is
printing it, and students need it from week 3 onward to find their own evidence.
**Fabricating your own evidence has always been possible, in both versions of
this course, by design.** The canary scheme was never a control against
fabrication. It is a control against copying, and at copying it works.

**What is genuinely new here is the first real control against fabrication, and
it sits on the funded side.** A gateway log independently records whether a
student made the model calls at all. A fabricated outbox file carrying a
correctly computed token sits beside a gateway record showing no traffic in that
window, or traffic that does not match. Nothing on an isolated laptop can do
that, because every record is written by the student's own machine and a student
willing to fabricate one will fabricate the rest.

That belongs in the proposal rather than in a security footnote: **the honest
anti-cheating argument for the funded version is the log, not the canary.** It
should also be said plainly to students in the week 1 notice, because a control
nobody knows about deters nobody, and one students discover later feels like a
trap.

The salt is still worth keeping out of the student environment, as tidiness
rather than as a control, and it should not be sold as one.

---

## 10. Governance

The load-bearing one first.

**No rubric row may require a hosted result that cannot be substituted.** That
single rule means a contract lapse, an outage, a deprecation, or a model that
refuses everything costs the course a substitution rather than a re-approval.
Section 4a shows how it is satisfied while hosted work still carries points,
which an earlier version got wrong in the other direction.

**And an earlier draft of this proposal broke that rule four times over**, which
review caught and which is worth recording rather than quietly fixing. Week 2
graded conclusions drawn from the hosted sweep. Week 3 graded the hosted
divergence step. Week 4 required gateway reconciliation. The final block added a
cost case that only exists on the meter. Every one of those is hosted-only work
carrying points, in a document whose load-bearing governance rule says it may
not.

**The resolution is section 4a**, which changes what is graded rather than
where the evidence comes from. In every week the graded question is answerable
from the student's own local evidence, and the hosted work is enrichment that
carries no points. That is a real reduction in what the hosted path is graded
on, particularly in week 3, and it is the only version of this rule that
survives an outage without an argument.

Then, and these are gating rather than advisable:

- **A registrar-signed records determination** naming the gateway log as an
  education record, with the retention schedule item, the destruction date, and
  the job that actually performs the deletion. "Kept until appeals close" is only
  a policy if somebody deletes.
- **The vendor agreement** with school-official language and a no-training-on-
  inputs term confirmed in the signed contract rather than cited from a web page.
- **The region and exact model identifiers**, with an explicit decision on
  cross-region inference, which if enabled quietly falsifies anything told to a
  parent about where a minor's text is processed.
- **A dual-credit rights determination** from the registrar and the school
  district, not the instructor.
- **The student notice**, delivered inside week 1's existing gate so it is
  provably read: what is captured, who reads it, for how long, how to see your
  own, how to ask for removal, and what the answer will be. A sixteen-year-old
  who pastes a real password and asks for it back deserves a decided answer
  rather than one invented on the spot.
- **The logging posture, version controlled.** The gateway's prompt-storage and
  redaction settings are toggleable from an admin interface without a restart.
  The notice given in week 1 can become false in week 4 through a click by
  someone who never read it.
- **Pseudonymous handles as the gateway key**, with the identity map held once
  by the instructor. The board already works by handle, and this keeps the
  college ID out of the vendor's records entirely.
- **A cap on instructor log reading**, with a recorded reason. The audit log
  needs its own audit log, which is week 4's lesson, and it is worth saying out
  loud to the class.
- **An outage policy** that auto-extends a deadline by the outage duration.
  Seven weeks with no slack week and census on day 8.
- **A deliberately kept losing case.** If attacks start landing, the path of
  least resistance is to grade the hit, and the provision that a correct negative
  result is a pass survives on paper and dies in the marking.

---

## 6a. The governance items, with owners and contents

Review found these named but not specified. Each entry below says what the
document must contain and who signs it, so that "write a records policy" becomes
a task somebody can complete rather than a heading.

| # | Document | Owner | It is not done until it contains |
|---|---|---|---|
| 1 | **Records determination** | Registrar | That the gateway log is an education record; the retention schedule item it falls under; the destruction date; and the named job or person that performs the deletion. A retention policy with no deletion step is a storage policy |
| 2 | **Vendor agreement terms** | Contracts office | School-official designation, and a no-training-on-inputs term confirmed in the signed agreement rather than cited from a web page |
| 3 | **Region and processing determination** | IT and contracts | The exact region, the resolved model identifiers, and an explicit decision on cross-region inference. If cross-region routing is enabled, anything told to a parent about where a minor's text is processed is false |
| 4 | **Dual-credit rights determination** | Registrar with the school district | Who holds the rights over these records for a student under 18 attending a postsecondary course, and who may request them. This is a question somebody will ask and the instructor must not be the one answering it |
| 5 | **Student notice** | Instructor, approved by the registrar | Delivered inside week 1's existing gate so it is provably read: what is captured, who may read it, for how long, how a student sees their own, how they ask for removal, and **what the answer will be**. A sixteen-year-old who pastes a real password and asks for it back deserves a decided answer rather than an improvised one |
| 6 | **Logging posture, version controlled** | IT | The gateway's prompt-storage and redaction settings, held in configuration under change control. Both are toggleable from an admin interface without a restart, so the notice given in week 1 can silently become false in week 4 |
| 7 | **Access log for the access log** | Instructor | When an individual student's prompts may be opened, which is to build a class aggregate or to adjudicate a disputed artifact, and a recorded reason each time. This is week 4's own lesson applied to the course, and it should be said out loud to the class |
| 8 | **Incident response for the course itself** | IT with the instructor | What happens when a student sends something to the gateway that should not have been sent: real credentials, personal data, or content requiring a safeguarding response. Who is told, in what order, and what is preserved |
| 9 | **Appeals procedure** | Department | How a grade dispute uses the logs, and the consequence that the retention date is set by the appeals window rather than the term end |
| 10 | **Continuity and staffing** | Department | Who runs the server when the instructor is absent, who holds the gateway admin credentials, and what happens to the course if the contract is not renewed. The answer to the last one is section 4a, which is why that matrix is load bearing rather than administrative |
| 11 | **Accessibility** | Instructor with the accessibility office | Jupyter in a browser, a terminal, and a class board are three interfaces with three different accessibility profiles. Screen reader behaviour over a notebook and over harness output should be checked before a graded week depends on either |
| 12 | **Outage policy** | Instructor, in the syllabus | A deadline auto-extends by the outage duration. Seven weeks has no slack week and census falls on day 8 |

**Six of these gate collection, not two.** An earlier draft said numbers 1 and
2. Review was right that the processing region, the student notice, the logging
configuration, the identity and access rules, and the incident response plan all
have to be settled before a single student prompt is collected, because each one
determines something a student is being told or a regulator would ask. Numbers
1, 2, 3, 5, 6 and 8, then, before collection. The rest before the term.

**And this register is a requirements list, not an approval package.** Twelve
specifications are not twelve policies, and nothing here is signed.

**Missing from the list above, and needed for a real institutional review:**
a security and data-flow review; identity and access management with
multi-factor authentication and a credential lifecycle for the gateway admin
account; patching and vulnerability ownership for the server; encryption and key
management; backup and restore; contractual breach-notice terms; subprocessor
review; and termination, export and deletion terms. Also the two controls this
proposal names elsewhere and the register omits: pseudonymous gateway keys with
governance of the identity map, and the deliberately retained losing case.

**On the vendor terms specifically**, school-official designation and a
no-training term are necessary and not sufficient. The institution has to
establish direct control over use and maintenance, restrictions on use and
redisclosure, a legitimate educational interest determination, and reasonable
access controls. That is a contracts-office conversation rather than a checkbox,
and it should start early because it is the long pole.

**One thing this list deliberately does not do** is treat the logging as a
problem to be minimised. The log is one of the genuinely valuable things the
money buys, per section 1. The point of specifying twelve documents is that a
record worth keeping is worth governing, and a course that teaches students to
ask who can see a log should be able to answer the question about its own.

---

## 11. Against the constrained version

**What this teaches that the constrained course cannot.** Students build an
agent rather than being handed one. They read a classmate's code rather than a
fixture. Cost is a decision with a price rather than a case card. The incident
in week 6 is built from their own term. And there is something to look at in
every week, which nine rounds of review asked for and a terminal cannot provide.

**What the constrained course still teaches better.** Negative result literacy
is forced there rather than arranged, because the marquee attack genuinely does
not land. Evidence lives on the student's own machine, so they are its custodian
rather than the subject of a record somebody else keeps. There is no
infrastructure excuse available. And it exists next August regardless of what a
procurement office decides.

**The honest comparison** is that this version is a better course and a more
fragile one. It depends on a server, a contract, and about five hundred lines of
notebook tooling that one person has to maintain. The constrained course depends
on nothing and teaches the harder half of the job. Run both if the college can:
this one when the environment exists, the other as the thing that still works
when it does not.
