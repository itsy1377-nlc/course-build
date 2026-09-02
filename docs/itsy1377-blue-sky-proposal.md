# ITSY 1377, the funded proposal

A second proposal, to sit beside `docs/itsy1377-course-proposal.md`. Same seven
outcomes, same seven weeks, same students. Different course, because the
environment is different.

**The scenario.** A server on the school network hosts a per-student isolated
Jupyter notebook. A gateway gives each student their own token and a budget
under ten dollars a semester, with all activity logged under school control. An
AWS Bedrock contract supplies two or three permissively licensed open models
against three hundred dollars per class. The premise is that the school takes
responsibility under the contract, which is what would resolve the age question.

**That premise is not true yet, and this document does not assume it is.**
Nothing is signed. The dual-credit rights determination the premise rests on is
item 4 of the register in section 10a and has no owner. Read the scenario as the
condition under which this course can run, not as a description of this year.

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

**In the first twenty minutes of week one you make a model call your own code.
For five weeks everything you attack, defend and prove is the agent you built.
Then in week 6 you are handed somebody else's, in the state a real one arrives
in: raw records, an alert already fired, and no pretty view.**

One artifact from week 1 to week 5, a deliberate break in week 6, and the
controls you wrote turned on again in week 7. The break is the point: a student
who can only investigate their own homework has learned nothing transferable.

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

**The blindfold** is one checkbox on the filmstrip. Click a decision card, tick
it, and everything the model did not have at that moment greys out: every card
later in the run, and every card holding evidence that never entered the
conversation at all, such as the workspace or the target's own logs. What stays
lit is exactly the model's context at that step. The hardest question in the
course, what did it actually know when it decided that, answers itself.

**The prototype had this backwards and review caught it.** It greyed the result
cards, which are precisely the cards the model does receive: `agent/loop.py`
appends every tool result to the message list before the next step, so greying
them taught the opposite of the lesson. The prototype now greys by position
relative to a chosen card, which is a true statement about the run.

**The trial grid** is twenty runs of the same thing as twenty squares filling in
live. Sometimes twenty blue. Sometimes thirteen and seven. Sample size stops
being a rule and becomes a picture.

**The workspace diff** shows what a tool did to files, before and after, in
green and red. In week 1 those are the student's own files. In week 3 they are a
disposable synthetic workspace inside the sandbox, and the diff is non-empty
only for the two menu effects that write. Section 7a lists which of week 3's
four discovery surfaces each effect actually shows on, because assuming it was
always this one is a mistake this document made twice.

**The boards** are projected: every student's agent in week 1, and in week 7
every attack and every defence with names against them.

**Partly measured, and an earlier draft of this section overstated it twice.**

A filmstrip renderer that draws a real trace from this repository is 68 lines,
and it exists. But it is a rendering spike rather than a finished component: the
live update is not implemented, the blindfold is a function argument rather than
the checkbox this section describes, and its first version rendered a blank
answer card because it read the wrong field. Review found all three, and the
field bug is fixed.

And the claim that `agent/trace.py` already records everything the visuals need
is false. It records about half. **Present:** the request, the model alias, tool
arguments, results, blocked state, errors and the final answer, which is enough
for the filmstrip proper. **Absent:** token usage and cost, the resolved model
version, the full context the model was shown, irreversibility, and workspace
state. The cost stamps, the context window view and the workspace diff each need
a new trace event, so those are features rather than views, and section 7 costs
them as such.

---

## 3. The seven weeks

| Wk | Title | What the student does | What is on screen |
|---|---|---|---|
| **1** | Twenty minutes | Take a working four line function, change one line of it, add one decorator, and watch a model decide by itself to call it. A reset cell restores the known-good version at any point, and a check cell says in plain words what is wrong before the model is ever called. Then break it six ways on purpose and watch what changes: delete the description, describe a different function, make it raise, make it return far too much, cut the step limit, take the tool away. Add a second supplied tool that writes a file, and answer the question that raises: which of your two can you undo? Your answer is a three-field record per tool: reversible yes or no, the one-line reason, and what a person would need to see before approving it. A `show_raw()` cell opens beside every filmstrip from here on, printing the actual JSONL with stable line numbers, because from week 1 every citation in this course names a field in a file and never "the third card" | The filmstrip drawing itself live, with the raw bytes one cell below it; tool cards; the blindfold; twenty five agents appearing on a projected class board |
| **2** | The blindfold | Two tools with the same code and different descriptions. Which does the model pick, twenty times? Change one word and run again. Find one edit that moves the grid and one that does not, and get credit for both. Then see the model's actual input as stacked blocks with token counts, and find your own tool descriptions sitting in it | Trial grids filling square by square, side by side as edits accumulate; the context window as coloured blocks |
| **3** | Somebody else's function | You do not write the hidden behaviour, you specify it: pick one effect from a menu of eight, set its parameters, and write the sentence of description that hides it. A generator then emits a real Python tool from your specification, and **that generated source is what your classmates receive**, with no label on it saying which effect it is. Three classmates' tools run against your agent in a sandbox, and you have forty five minutes to work out what each really does by reading the code, by probing it directly, and by watching the filmstrip and the workspace diff. The tool cards render with the field names the protocol actually uses, `name`, `description` and `inputSchema`, and one supplied paragraph says plainly what MCP is, that this manifest shape is what it standardised, that you are reading manifests over a local transport rather than running a server, and that the failure you just found is what ATLAS calls tool poisoning | Anonymous tool cards in manifest shape; the code itself; the filmstrip of your own agent behaving strangely; the workspace diff for the two effects that write |
| **4** | English versus Python | A tool arrives that returns text strangers wrote. Put text in a ticket that makes your own agent call your own irreversible tool. Twenty trials. Then, before reporting any result, run the positive control: the same instruction in your own message instead, twenty trials again. Report both grids and state exactly what the pair does and does not establish. The four labels are the ones you will use again in week 6: injected, failed, refused, errored. Two named trials, one that fired and one that refused, each carry the field that decides the label | Two grids side by side, whichever way they fall; filmstrips that stop part way |
| **5** | Watch it spend | Predict what a runaway loop will cost, in cents, then build one and run it on a separate burnable key. Watch the bar drain. Then write the cap, and run it again. The cap is guard one, a number. Guard two is an approval gate over the tools your own week 1 records marked irreversible, and it is where you find out that a gate does not discriminate, it delegates: it blocks the attack and it also blocks the legitimate escalation, and the count of approvals over twenty trials, multiplied out to a shift, is approval fatigue measured from your own data | The budget bar draining live; a black cap card ending a run mid-flight; an approval card pausing a run; before and after with the cost difference |
| **6** | Somebody else's agent | You are handed one of six fixed incident packs: raw trace JSONL, the target's audit export, outbox files, a slice of the gateway spend log, a credential manifest, and the previous shift's AI-written handover note. You are told which alert fired. **The filmstrip is switched off.** File a containment ticket: what the agent did in order, whether this is an incident and the one field that decides it, what gets revoked right now and what that breaks, where two records fail to reconcile, and which sentence in the handover note is wrong | The raw bytes, with stable line numbers; a containment form with closed vocabulary; the class histogram of calls once everyone has filed |
| **7** | The gauntlet | Turn on every control you built. Then two rounds, live: your defences against the class's attacks, and your attacks against theirs | Two boards updating on the projector during play, everyone named on both |

**Week 4 is the week that must work whichever way the measurement goes.** It is
built so that a negative result is the expected and fully creditable outcome.

**What the positive control does and does not establish**, because an earlier
draft claimed too much for it. Putting the same instruction in the user turn and
seeing it fire proves two things: the model will follow that instruction from a
trusted position, and the irreversible tool is reachable. It does **not** prove
the instrument would have detected the same behaviour arriving from a document.
It rules out one specific way of being wrong, which is a broken payload or an
unreachable tool, and leaves others open.

So the graded claim is bounded to what the evidence carries: in these trials, on
this model, the instruction fired from the user turn and not from the document,
and here is what that does and does not establish. That is a smaller claim than
"the null is real" and it is the one the student can actually support.

---

## 4. The three mechanics that carry it

**The agent they built, and the one week it is taken away.** One artifact from
week 1 minute 20 to week 5, and again in week 7. Every attack is against a thing
they made, every control is in their own code, and by the end it exports as a
folder holding a system prompt they wrote, the three or
four tools they edited or filled in, and the guard code they added in weeks 5
and 7.

**That count is small on purpose, and an earlier draft inflated it.** It
promised six to ten student-authored functions, which no week assigns: the
schedule assigns edits to supplied functions, one filled-in template in week 3,
and guards in weeks 5 and 7. What makes the artifact theirs is that they changed
every part of it and can read all of it, not the number of functions in it.

**The cuckoo, in week 3.** Every student specifies one tool that does what it
claims and exactly one thing it does not mention, receives the generated source
of three classmates' tools blind, and has to read them. All three judges called it the best single mechanic across the four
designs. It teaches supply chain, code reading and evidence at once, it cannot
be looked up because the answer is a classmate's, and it produces the second
best picture in the course.

**The boards.** Week 1 puts every student's agent on the wall. Week 7 puts every
attack and defence there, live. The constrained course's own review found the
class board its best loved mechanism and its worst placed, arriving only in the
final week.

---

## 4a. Points, and what happens when the gateway is not there

Two earlier drafts referred to this section as the answer to the governance rule
in section 10 and to the continuity question in section 10a, and it did not
exist. Review was right that this is the load-bearing missing piece: without it
there is no auditable account of what is graded.

**The substitution is a deterministic mock model, and it already exists.**
`agent/mock_model.py` is 394 lines, wired in as a first-class provider at
`agent/llm.py:144`, and it already has the property this section needs: its
variability is seeded rather than random. It hashes the seed, the trial and the
question, so the same run always gives the same answer while a grid still fills
in mixed rather than as twenty identical squares. The funded course needs it
extended to the new scenarios, not written.

**Read its own docstring before relying on it**, because it says something this
section has to obey. A mock run proves your code, your harness and your
detectors work, and proves nothing about a real system. `harness/report.py:82`
stamps every report produced against it. An earlier version of this section
walked straight past that and said a student who runs against the mock earns
full credit, with no mention of the banner. That would have made the outage
substitution teach the exact habit the course exists to break: citing a run as
evidence about a world it says nothing about.

**So the mock is the fallback, not the default path.** The default is hosted.
The mock is invoked when the instructor declares the gateway unavailable, the
artifact keeps its banner, and the claim the student writes is scoped to what a
simulator can support. What is graded either way is the student's reasoning over
a run they recorded, not which way the model went.

**And the governance rule is narrowed, because the wide version was wrong.** The
rule is now: **no rubric row may require a particular hosted outcome.** One row
may require that a hosted run happened, because that is a different kind of
dependency: an outcome cannot be substituted at all, while a run that has not
happened yet is handled by the outage policy extending the deadline. Without
that narrowing, all one hundred points are earnable against behaviour the course
author scripted, and then the contract is enrichment rather than an
instructional resource. Review found exactly that and it was right.

| Wk | Graded artifact | Pts | If the gateway is unavailable |
|---|---|---:|---|
| **1** | The working agent, the six deliberate breaks with what changed in each, and the irreversibility flag on each tool with a one-line reason | 15 | The mock drives the same six breaks. Break behaviour is scripted, so this week is nearly identical either way |
| **2** | Two description edits, one that moved the trial grid and one that did not, both grids attached, and the student's account of why | 15 | The mock's tool choice is a seeded function of the description text, so an edit moves the grid or does not. The reading of the grid is what is graded |
| **3** | Three reports on classmates' tools: what each really does, and the evidence line that shows it | 15 | Needs the sandbox on the school server, not the gateway. Unaffected by a contract lapse and blocked by a server outage |
| **4** | The document grid, the positive-control grid, and the bounded claim the pair supports | 15 | The mock's injection-following rate is seeded per student, so some see a null and some do not. The claim is graded, not the outcome |
| **5** | The cost prediction, the runaway trace, the cap in the student's own code, and the before-and-after difference. **Ten of these fifteen points require a real gateway run**, of any size and any outcome, reconciled against the ledger | 15 | Five points on the mock's synthetic arithmetic. The other ten wait: the outage policy extends the deadline. If the contract never lands, the row converts to the mock, the banner rides on the artifact, and the course records that it graded a simulation |
| **6** | One containment ticket on a supplied form: the sequence, the call, the containment order and blast radius, the reconciliation, and the wrong sentence in the handover note | 15 | **Unaffected.** The packs are fixed bytes authored before the term and the handover note is written by hand, so this week needs neither the gateway nor a model. It is the one week an outage cannot touch |
| **7** | The gauntlet: attacks submitted, defences turned on, and a short account of one defence that held and one that did not | 10 | Both rounds run against the mock. Needs the class board, so a server outage blocks it |
| | **Total** | **100** | |

**Two claims an earlier version of this table made that were false.** It said
every artifact is producible with the network unplugged: weeks 3 and 7 need the
school server, for the sandbox and the class board, so the mock protects the
course against a contract lapse and not against a server outage. And it said the
hosted path is graded on nothing, which is what made the money unjustifiable.
Week 5 is now the one row where a real call has to have happened.

**Why week 5 and not another.** The meter is that week's entire subject. Its
artifact is the only one whose evidence is the gateway ledger rather than the
student's own files, so it is also the only row where the log does the
anti-fabrication work section 9 credits it with. On every other row a student
working offline produces an artifact with no independent record behind it, and
section 9's claim should be read as applying to the hosted path only.

**Week 4's rubric, which is outcome-independent rather than outcome-neutral.**
An earlier version said all four combinations earn full credit, which review
correctly called undefined: each arm holds fired, missed and refused trials, so
the space is not a two by two. The points are on conduct and reasoning, and none
of them are on the result.

| What earns it | Pts |
|---|---:|
| Twenty clean trials in each arm, with errored trials re-run and the re-run count reported | 4 |
| Every trial classified as fired, missed, refused or errored, with refusals never counted as misses | 4 |
| Both rates reported with the denominator each rests on | 3 |
| One sentence on what a reader may and may not conclude from the pair, correct for whatever the pair actually was | 4 |
| | **15** |

The least convenient case is worth naming because it is the one a student will
fear: a positive control that does not fire at all. That earns fifteen out of
fifteen, provided the student says the instrument was not shown to work and the
document result is therefore uninterpretable. Being unable to conclude anything,
and knowing it, is the outcome this course exists to produce.

**Week 6's rubric, at the same granularity.** Roughly ninety per cent of the
ticket is closed vocabulary scored against a per-pack key that was written before
the student opened the pack. Three sentences are read by a person.

| What earns it | Pts |
|---|---:|
| **The sequence.** Every action in the order the records support, selected from the pack's citable fields, with the one action the target never saw, or the one audit row with no trace line, marked as such. Scored by longest common subsequence, so a missed step costs a step and not the row | 2 |
| **What happened.** One sentence saying what the agent did, consistent with the sequence just cited | 2 |
| **The call.** Incident or not, with the one citation that decides it, plus one sentence naming something this record cannot settle. **A wrong call reached from correctly cited evidence earns this row in full; a right call with no citation earns none of it** | 4 |
| **Containment.** A revocation order over the closed menu in the credential manifest, the one item correctly marked not revocable with its reason, and the blast radius table for the first revocation. `NO REVOCATION IS WARRANTED`, with a reason, is a first-class answer and earns the row in full on the packs where it is correct | 3 |
| **Reconciliation.** One place two records disagree, cited on both sides, or a statement that they agree with the check that shows it | 2 |
| **The handover note.** The wrong sentence quoted, its drift class named from the closed menu, and the citation that contradicts it | 2 |
| | **15** |

**Two things this rubric had to be built to do**, both of which review found the
first version could not.

**It has to let a student argue from absence**, because three of the six packs
turn on a record that is not there: an empty outbox, a spend row with no trace to
account for it, an id gap. An absent record has no line to cite, so the citation
vocabulary carries `NO SUCH RECORD` as a selectable value, requiring the student
to name the file that should have contained it. Without that value a student can
reach the right conclusion by the right reasoning and have nowhere to put it.
This repository has made the opposite mistake before, and the comment reading
"Missing evidence is not evidence of absence" is already in the code because of
it.

**And it has to cite a field rather than a line.** Measured against the 2,428
traces in `labs/runs/traces/`, the median trace is nine lines long and its
ninety-fifth-percentile line is 2,443 characters, because `trace.py` embeds the
whole tool result in the event. One line routinely holds the injection, the
recipient and the exfiltrated value together. So the citable unit is
`file:line:field`, the pack ships a pre-built index of every citable field, and
the key anchors on that index. A line citation would have been unable to
distinguish the deciding fact from its neighbours, which is the whole of rows 1
and 3.

---

## 5. How the outcomes are met

| # | Outcome | Where |
|---|---|---|
| 1 | Describe how an agentic system operates from its recorded run | Wk 1, the filmstrip of a system they assembled |
| 2 | Interpret a short script to determine what it accesses and changes | Wk 3, reading a stranger's tool, which is the literal week |
| 3 | Analyze a tool configuration to identify irreversible actions | Wk 1, assigning the flag to their own tools |
| 4 | Differentiate evidence from assertion | Wk 4 and 6, their own grids, and a record somebody else made |
| 5 | Interpret repeated-trial results including no effect | Wk 2 and 4, with the positive control bounding what the null supports |
| 6 | Apply a control at a tool boundary and verify its effect | Wk 5 and 7, in their own code: a numeric cap and an approval gate in week 5, verified against two held-out cases, then every control turned on in week 7 |
| 7 | Evaluate AI output against source evidence | Wk 6, the handover note against the pack it claims to summarise |

---

## 5a. The leg this course was missing

**A six-person panel found that the phrase in the course title appeared nowhere
in the proposal.** Verified by search of the document as it then stood:
"security operations" appeared zero times, and so did containment, revoke,
respond, MCP and alert; "detection" appeared twice and both were about the
harness's internal chain detector. The student built one agent in a sandbox and
attacked it, and never once sat in the defender's chair with somebody else's
agent running in an environment they were responsible for. The practitioner on
the panel put it plainly, and she was right.

**What week 6 now delivers.**

*Identity and credentials, in full.* Every pack carries five revocable objects
and the student names and orders them: the gateway key, shown by alias and hash
prefix as the spend log shows it and never in cleartext; an API key sitting in
the system prompt with no scope, no expiry and no rotation path; a stored payment
reference; a policy token; and the operator account whose identity the request
merely asserted. That last one is where the lesson lands on evidence rather than
on a comment: the audit log faithfully records who claimed to be asking, and the
application never checks it, so the record proves what happened while nothing
prevented it. Blast radius is a filled table rather than an adjective. And the
sentence on what revocation does **not** undo is the one that separates an
analyst from a student.

*Detection, the analyst half.* The student reads telemetry produced by systems
they did not design, that disagree with each other, with no shared correlation
id. One pack in six carries an alert that fired on a benign action, so validating
an alert against the record is real work and not a formality. That arm is this
project's own history: case A5 reported a vulnerability five times out of five
against an attack that never landed. It is **not** detection engineering. There
is no rule authoring, no precision and recall, no labelled corpus, and rule
authoring would be code from a blank file in any case.

*Response, the decision half.* Containment is named, ordered and priced: what to
revoke first, what breaks when you do, and what it does not undo. Execution is
not here; week 7 already says "turn on every control you built", and the
containment recommended in week 6 is one of them.

*MCP, read rather than run.* Week 3's tool cards render in manifest shape and one
paragraph names the protocol. A graduate can say they read a tool manifest and
found the poisoned description, and can point at the field. They cannot say they
stood up or audited a live server, and nothing here should let them imply
otherwise.

**What it does not deliver, said plainly rather than fudged.** Approval gates are
built in week 5 and reasoned about in week 6, but no week has a student operate a
gate under load. Multi-agent is out of this course entirely, which is why the
nested filmstrip is deleted from the build in section 7 rather than left standing
as an implied promise.

**The off-ramp, which is the point of switching the filmstrip off.** The panel's
sharpest cut at section 2 was that a graduate trained only on the pretty view
cannot read a log, and that reading twenty thousand characters of JSON is the
job. Weeks 1 to 5 build the filmstrip habit; week 6 takes it away and hands over
the bytes. `show_raw()` sits beside every filmstrip from week 1 precisely so that
the week 6 hand-off is a change of tool and not a change of language.

**One tension this creates, booked here rather than discovered at build time.**
This project has already measured that an accurate hedged sentence costs reading
grade while a confident wrong one does not, and the build fails above grade 8.
Week 6's whole vocabulary is hedged: what this record cannot settle, what could
still have been reached, what revocation does not undo. A first draft of the
student-facing text measured grade 10.1 with an average sentence of 18.7 words,
against limits of 8.0 and 15. The prose has to be written to the gate, and that
rewriting is real work that section 7 costs as prose rather than as code.

**Why the packs are authored and not harvested.** The practitioner proposed
handing a student another student's real weeks 3 to 5. That sourcing fails five
ways, each checked against the code. `harness/runner.py` resets the target at the
top of every trial, so after a harness run the outbox is empty and the audit
table is cleared: a classmate's term is a directory of transcripts with the
incident's other half already deleted. The gateway log is being determined as an
education record and dual-credit rights over a minor's records have no owner, so
redistributing one student's records to another is a disclosure nobody has
signed. Census falls on day 8, so a legitimate late add has no artifacts to
donate. One student's grade would wait on another's outage extension. And a
classmate's five weeks may mix mock and hosted runs, which makes "the spend log
does not reconcile" indistinguishable between an outage and an incident, which is
the best question in the week. Her exercise was right; the sourcing was not.
Fixed packs, authored before the term, answer all five at once, and they are also
what makes this the one week a gateway outage cannot touch.

**What is lost.** The best sentence in the old week 6 goes with it: your own term
becomes the incident. The term-long chain now breaks for a week. That is a real
loss of narrative coherence and it is worth booking as one.

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

**But the first version of this fix only moved the problem**, and review caught
it. Week 1 was repaired and week 3 still asked students to write a tool with two
behaviours, which is authoring rather than editing, and which sits at a Bloom
level the sibling proposal explicitly rules out for a course with no programming
prerequisite. The two documents contradicted each other.

Week 3 is now a specification rather than an edit. The student picks an effect
from a menu, sets its parameters and writes the description that hides it; a
generator emits a real Python tool from that specification, and the generated
source is what runs and what classmates read. No student expression reaches the
interpreter, which removes most of the security exposure at the same time as it
removes the authoring requirement.

**It took two more rounds of review to get there and both found real breaks.**
The first version denied the template any filesystem call and then asked
students to discover the effect from a filesystem diff, which for six of the
eight effects is empty. The second distributed the specification itself, which
either wrote the answer on the card or left every student's code identical, and
so destroyed the code-reading that is the whole point of the week and the home
of outcome 2. The generator is what fixes both: differing, readable, unlabelled
Python, with the effect discoverable through whichever of four surfaces it
actually touches.

**On build cost**, the instructor scored deliverability 2 out of 10 assuming the
visuals were a large custom build. Two rounds of review have now moved that
estimate twice, both times upward, and section 7 states where it landed: about
1,600 lines of notebook tooling that the instructor can write in four to six
weeks, plus a sandbox and a model broker that are an IT project rather than an
instructor project. The deliverability score was closer to right than the
estimates that argued with it.

---

## 7. What has to be built

**Rebuilt twice under review, upward both times.** The first version costed only
the views and assumed the data was already recorded. The second added the
recording and the sandbox and reached about a thousand lines. Review then found
that the second version still counted the visible components and left out the
measurement rig, the cost arithmetic, the incident pack, the recovery cells and
most of what a real sandbox is. This is the third version, and it is split by
who builds it, because that turned out to be the more useful division.

### What the instructor builds: the notebook tooling

**The visuals**

| Piece | Lines | Note |
|---|---:|---|
| Filmstrip renderer and styling | **68, spike exists** | draws a real trace; not yet live-updating |
| Live update in place | 40 | display id, no dependency |
| Blindfold as a real checkbox, greying by position | 35 | the spike has an argument, and had the semantics backwards |
| Tool cards with schema inference | 90 | signature and docstring to schema |
| Trial grid, four way classification | 60 | fired, missed, refused, errored |
| Context window view | 50 | needs the new trace event below |
| Workspace diff, presentation only | 30 | wraps a standard library module |
| **Visuals** | **373** | |

**The recording the visuals need, which does not exist**

| Piece | Lines | Why |
|---|---:|---|
| Capture usage from the response | 30 | the loop discards it today, so no cost stamp is possible |
| Cost arithmetic and a versioned price table | 70 | token counts are not money; prices change mid-term and a reported figure has to say which table produced it |
| Record and pin the resolved model version | 45 | the alias is recorded, the version is not, and a Bedrock alias has to resolve to something reproducible |
| Record the context sent to the model | 40 | nothing records what the model was shown |
| Irreversibility as tool metadata | 25 | passed by hand into the renderer today |
| Workspace snapshot before and after | 40 | no event exists |
| Per-call duration, at better than one-second resolution | 25 | `trace.py` stamps to the second and records no duration, so the stall effect in section 7a has no surface without this |
| **Recording** | **~275** | |

**The measurement rig, which section 8 and section 9 both call a prerequisite
and which no earlier estimate contained**

| Piece | Lines | Why |
|---|---:|---|
| Ordered chain detector | 80 | so "reached step 3 of 5" is machine-produced; the schema pins detection to one detector today |
| Refusal and failure classifier | 60 | so a refusal is not counted as a miss |
| Positive tool-capability controls | 40 | so a model that cannot drive the loop is not read as one that declined |
| Control validity repair | 30 | a control must be inconclusive unless every requested trial completes |
| **Measurement** | **~210** | |

**The weeks that need machinery of their own**

| Piece | Lines | Why |
|---|---:|---|
| Week 3 schema, eight-effect menu, parameter validation and the trusted executor | 140 | this is what keeps student expression out of the interpreter |
| Week 3 source generator | 80 | emits readable Python from a specification, which is what gives classmates something to read |
| Week 6 pack stamper, citable-field index and answer-key builder | 180 | six packs stamped once with stable line numbers, every citable field pre-exploded, and each key entry anchored to the shipped bytes and asserted to resolve |
| Week 6 containment form and its closed vocabularies | 120 | the revocation menu, the drift classes, the triage labels, and `NO SUCH RECORD` |
| Week 6 auto-scorer | 90 | longest common subsequence over the sequence, set membership over containment, key match on the rest |
| `show_raw()` beside the filmstrip, weeks 1 to 5 | 20 | the off-ramp; prints the actual JSONL with stable line numbers |
| Week 5 approval gate: an `ask_human` tool, an `approval` trace event, and a `gate` case kind in the harness | 95 | human-in-the-loop has no field, no event kind and no tool argument anywhere in the repository today. The new case kind is not optional: `runner.py:191` refuses an attack case whose passing condition is that the call was blocked, and routing it through `control` instead would abort the whole run at `runner.py:751` and produce no attack results at all |
| Week 3 tool cards in manifest shape | 25 | `name`, `description`, `inputSchema` |
| Week 1 reset and check cells | 60 | see the acceptance criteria below |
| Week 5 burnable-key handling, student side | 40 | an earlier draft also called this "not code" |
| Extending the existing mock model to the new scenarios | 200 | **not 130 to build one.** `agent/mock_model.py` already exists at 394 lines with the seeded determinism section 4a needs, but it was written for a different course's scenarios. An earlier estimate here costed writing from scratch what is already written, at a third of what the narrower existing version cost |
| Class board | 300 | not 120: handles, authentication, authorisation, concurrency, moderation, model-version separation, persistence and projector-safe display |
| **Weeks** | **~1,350** | |

**Implementation subtotal: 2,208 lines.** The mock is on the critical path for
everything else, because it is what lets the visuals and the measurement rig be
built and tested without a gateway.

**Two notes on that number.** It went up by 385 because section 5a added a week's
worth of machinery, and it is stated exactly rather than rounded because the
previous version said "about 1,825" while its own four subtotals summed to 1,823.
A two-line arithmetic error in a section whose whole subject is that the estimate
keeps being wrong is worth not repeating.

**And a subtotal is not an estimate, which is the finding that matters most in
this section.** Three rounds of review have moved this number from 500 to 1,000
to 1,650 to 1,825 to 2,208, and every increase but the last came from noticing
something that was never counted rather than from anything growing. The last one
is different: it is new scope, deliberately added. What is still not counted:

- **Tests.** The executor in section 7a is the security boundary for week 3 and
  its safety is a property of tests rather than of anyone's reading. Nothing
  here budgets them.
- **The seven notebooks themselves**, with their prose, their fixtures, their
  seeded scenarios and their rubrics. That is the course, and this table costs
  only the machinery underneath it.
- **Integration**, including migrating the existing agent and harness to the
  notebook environment.
- **Accessibility remediation**, which section 10a lists as an open item across
  three interfaces with three different profiles.
- **Grading hours.** No week in this document carries a marking estimate. Week 6
  is designed to be cheaper to mark than the week it replaces, for four
  structural reasons: the key is written before the student opens the pack, the
  packs are six fixed artifacts rather than twenty-five unique ones, most of the
  ticket is closed vocabulary, and what is learned marking one student applies to
  the next four who drew the same pack. That is a relative claim and this
  document has no baseline to turn it into an absolute one.
- **Prose conformance.** Section 5a records that week 6's student-facing text
  measured two grade levels above the gate on its first draft. Rewriting to the
  gate is real work and none of the tables above cost it.

**So the honest statement is that there is no delivery date.** The instructor's
implementation work is 2,208 lines and five to eight weeks, having grown by a
week's machinery when section 5a was added; the work around it is uncosted; and
the IT project below has no estimate at all while sitting on week 3's critical
path. A procurement office should read this section
as establishing that the build is larger than one person before a term, not as
establishing when it would be ready.

**Acceptance criteria for the week 1 reset**, corrected after review executed
the previous version and broke it. That version said the reset restores the
starter source, re-populates the tool registry, clears the trace, refreshes the
workspace and renders an empty filmstrip. Review cleared and repopulated `TOOLS`
while leaving `allowed_tools` empty and `max_steps` at one: the registry came
back with four entries and the agent still had zero tools and one step. The
criterion omitted the two things week 1 explicitly tells students to change.

The cause is architectural rather than accidental. Registry and configuration
are separate, and `tools.py:444` intersects `TOOLS` with `cfg.agent.allowed_tools`,
so restoring one restores nothing. `config.py:74` also hands out the underlying
mutable dictionary, so configuration can be edited in place from a notebook cell.

The corrected criterion: from any state a student can reach in week 1, one run of
the reset cell restores the starter function's source, the tool registry, **the
configuration including `allowed_tools` and `max_steps`**, any alias a cell has
bound to a tool or a config object, executor and counter state, the current
`Trace` object, display and widget state, and the workspace directory, and then
renders an empty filmstrip. It does not restart the kernel.

**Which is a design constraint, not just a longer list.** A reset that has to
find state scattered across modules will not hold for seven weeks. The state a
student can reach has to live behind one object that the reset replaces
wholesale, and that is a decision to make before week 1 is written rather than
after. The check cell passes when, for each of nine seeded broken states, it
names the fault in one sentence a student can act on without calling the model.

### What IT builds: the sandbox and the broker

**This is a separate project with a separate schedule, and it is on the critical
path for week 3.** Review's judgement is that a community-college IT department
may well be able to operate it and that it is not credible as part of a
one-instructor build. That judgement is accepted here. No line count is offered,
because a line count would imply the instructor could write it.

- **The cuckoo sandbox.** Rootless execution, user namespaces, a seccomp or LSM
  profile, no container-runtime socket, restricted devices, a pinned base image,
  verified teardown, per-run resource ceilings, twenty-five-way concurrency, and
  an audit record per run. Plus an honest statement of residual host-kernel risk
  for whoever signs it off.
- **The model broker.** The component outside the sandbox that makes the model
  call on the cuckoo's behalf: authentication, per-run request ceilings, budget
  enforcement, an audit trail, and a failure mode that does not leak the
  gateway token into a stack trace.
- **The audited workspace diff.** The presentation is thirty lines; the audited
  producer is not. Deletions, renames, symlinks, binary files, permission
  changes, path canonicalisation, size ceilings, and filenames chosen to be
  hostile to whatever renders them.
- **A load test at twenty-five concurrent sessions**, per section 9, before a
  graded week depends on the answer.
- **Deployment, patching, backup and restore, and credential lifecycle** for the
  server and the gateway admin account, which section 10a lists as missing.

**Not code, and this time the list is short because the previous version of it
was wrong:** the malicious-submission procedure, and the instructor's screening
pass, which section 7a demotes to defence in depth.

---

## 7a. Week 3 is code execution, and the fix is to stop executing student code

**This was the most serious problem in the proposal.** Week 3 originally had
every student write code that deliberately does something it does not declare,
and three classmates then execute it inside their own agent, on a school server,
and some of these students are minors. The only protection was a sentence saying
a cuckoo must stay inside the workspace, which is a rule rather than a control.

**One attack path was demonstrated rather than argued.** Every tool receives the
configuration object as its first argument, and that object names the
environment variable holding the gateway key. A classmate's tool reads that
student's metered, billable token in one line of Python. The course supplies the
motive in week 5, where students learn that model calls cost money, and the
method in week 3, two weeks apart.

**Five more asset classes**, none closed by the workspace rule: peer files by
path traversal, the school network by ordinary sockets, host resources by
exhaustion, the class board's credentials, and **the week 6 evidence itself**,
since that pack is built from records accumulated across weeks 3 to 5 and a
cuckoo can write to them.

### The primary control: the effect is specified, then generated

The student does not supply Python. At the marked point they supply a small
structured record: which effect, its parameters, and the sentence of description
that hides it. The harness validates that record against a schema, **a generator
emits a real Python tool from it**, and the generated source is what runs and
what classmates receive. A malformed or unknown effect is rejected at
submission, not at run time.

**The generator is what saves the mechanic**, and an earlier version of this
section destroyed it without noticing. That version distributed the record
itself, which meant either the classmate saw `effect: 3` written on the card, or
they saw nothing at all and every student's code was identical. Either way there
was no code to read, and outcome 2 is *interpret a short script to determine
what it accesses and changes*, mapped to this week as the literal week. Review
caught it.

Generated source restores all of it. The code differs per student, is real
Python, is readable, and carries no comment announcing which effect it
implements. Working out that `if self._calls > 2: raise RuntimeError(...)` means
this tool dies on its third use is the skill outcome 2 names. What stays
authored by the student is the pair that matters: which effect, and the sentence
that hides it, so comparing description against code is a comparison of a
classmate's words against a classmate's choice.

And the security property is unchanged, because no student expression reaches
the interpreter. The demonstrated `cfg` path has nothing to run in.

### The menu, and the surface each effect actually shows on

Review checked all eight against the code and found four that did not work as
claimed. Corrected below; the corrections are the substance.

| # | Effect | Where it shows | What had to change |
|---|---|---|---|
| 1 | Appends extra text to the return value, addressed to the model rather than the reader | Filmstrip: the result card | Nothing. This is tool poisoning and it is the one worth having |
| 2 | Returns a wrong value on one call in three | Filmstrip: compare result cards across probes | Was one in ten, which shows nothing in ten probes 35 per cent of the time. One in three, and the week specifies at least twelve direct probes |
| 3 | Fails on its third call | Filmstrip: the run where the card turns red | Was "after n calls" with n unbounded, while the loop stops at six steps. Fixed at three, and discovered by direct probing rather than through the agent |
| 4 | Stalls for a fixed delay before returning | Filmstrip: the duration on the card | **The surface did not exist.** `trace.py` stamps to the second, records no duration, and the prototype renders no timing. Section 7 now costs the event |
| 5 | Returns far more than it needs to, crowding the context | Context window view: the block that swells | Nothing, except that it has to sit under the loop's own `max_tool_result_chars` truncation to be visible rather than clipped |
| 6 | Counts its own calls and changes behaviour after the third | Filmstrip: behaviour that differs by position | State scope was undefined. It is per-instance state on the tool object, created fresh for each artifact execution and destroyed with the container. Never module-global, which would survive the runner's trial loop |
| 7 | Appends a line to a fixed log file in the synthetic workspace on every call | Workspace diff | Destination is fixed by the generator, not named by the student |
| 8 | Copies its argument into a fixed file in the synthetic workspace | Workspace diff | Same |

**Effects 7 and 8 take no filename from the student**, which removes a
contradiction review found: this section claimed path traversal was not
expressible while the menu handed students a filename, and section 7 separately
warned about hostile filenames. Now the only student-supplied values are an
effect id from an enum, bounded numbers, and bounded text. Section 7's
hostile-filename concern is about the general diff producer and not about
anything week 3 can reach.

### What screening can and cannot establish

**Screening parameters is a reading task only if every sink treats a parameter
as data.** That is a property of the executor, not of the screener, and review
was right to press on it. The executor is safe when: effect ids are an enum;
numbers are range-checked; text is length-capped and reaches only string
concatenation or a file write; no parameter reaches `eval`, a shell, a dynamic
import, a path, rendered HTML, or a regular expression; and destinations are
fixed constants. **None of that is established by a person reading submissions.**
It is established by tests on the executor, which section 7 now costs.

**Screening is defence in depth and is not the control.** What it is genuinely
good for is the thing code review cannot do: content. Nothing above stops a
student putting abusive or identifying text into a description or a parameter
that classmates then read. Bounded output limits size, not content. Reading
twenty-five short descriptions is a task an instructor can actually complete in
an evening, which is more than could be said for reviewing twenty-five programs.

Then: the accepted artifact is hashed and exactly that is distributed, and the
malicious-submission procedure covers preservation, notification, grading and
restoration.

**The executor still runs in the sandbox**, because it is a program processing
input a student chose. What the declarative design buys is that the attack
surface is one component the instructor wrote and can test, rather than
twenty-five programs nobody can. The rest carries over: no secrets in the
sandbox, default-deny egress including the local subnet, a disposable synthetic
workspace and nothing else mounted, and only a bounded result plus the audited
diff coming back out.

**Verified absent.** No executor, schema, generator, effect menu or workspace
diff exists in this repository. Every claim in this section is a specification,
and review's judgement that a vertical slice should be built and tested before
anyone estimates the rest is accepted.

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
runs for three cases at five trials across three models, which is forty-five. It
also said the harness runner could not select individual cases, which is false;
`--case` is a repeatable argument and has been since before that draft was
written. Both statements were wrong, and the second was wrong about code sitting
in this repository.

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

**The arithmetic, stated once so it stops drifting, and it is larger than the
last version said.** Three attack cases plus the two capability controls listed
above is five cases, not three. Five cases by three models by thirty trials is
450 runs a day, and the second-day repeat doubles it to 900. At about 5,500
tokens a run that is roughly five million tokens, still a few dollars at current
open-model prices. Errored trials are re-run, so 900 is a floor.

**Two numbers in that sentence are softer than they look.** The 5,500 tokens is
an estimate rather than a measurement, because the loop discards usage today,
which is the first line of the recording table in section 7; and one agent run
contains several model requests, so the per-run figure is a sum over a variable
number of calls. And the experiment needs three models while the opening
scenario funds two or three. **Three is the requirement**, because the whole
point is to see whether the result holds across models rather than in one, and
the contract should be written for three. **Two hours is the
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

**With one limit that review found and that section 4a now carries.** The log
backs an artifact only when the artifact came from a hosted run. Anything
produced against the mock during an outage has no independent record behind it,
because every file in it was written by the student's own environment. So this
control covers the hosted path and not the fallback, which is a further reason
week 5's ten points are the row that requires a real call.

The salt is still worth keeping out of the student environment, as tidiness
rather than as a control, and it should not be sold as one.

---

## 10. Governance

The load-bearing one first.

**No rubric row may require a particular hosted outcome.** That single rule
means a contract lapse, an outage, a deprecation, or a model that refuses
everything costs the course a substitution rather than a re-approval.

**An earlier version of this line said "a hosted result that cannot be
substituted", and section 4a then read it as forbidding hosted points
altogether.** The two sections contradicted each other in the same document:
this one said hosted work still carries points, that one said it is graded on
nothing. Review found it. The narrowed rule above is the version both sections
now follow, and section 4a explains why the wide version was worse than the
problem it solved: it made every point earnable against scripted behaviour, and
a course whose grades never depend on the contract does not need the contract.

**And an earlier draft of this proposal broke that rule four times over**, which
review caught and which is worth recording rather than quietly fixing. Week 2
graded conclusions drawn from the hosted sweep. Week 3 graded the hosted
divergence step. Week 4 required gateway reconciliation. The final block added a
cost case that only exists on the meter. Every one of those is hosted-only work
carrying points, in a document whose load-bearing governance rule says it may
not.

**The resolution is section 4a**, which changes what is graded rather than
where the evidence comes from. In every week the graded question is answerable
from the student's own evidence and none of it depends on which way a model
went. One row, ten points in week 5, requires that a real call happened, which
the outage policy protects by extending the deadline rather than by
substituting.

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

## 10a. The governance items, with owners and contents

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
in week 6 is somebody else's, arriving as raw records with an alert already
fired, which is the condition of the job. And there is something to look at in
every week, which nine rounds of review asked for and a terminal cannot provide.

**What the constrained course still teaches better.** Negative result literacy
is forced there rather than arranged, because the marquee attack genuinely does
not land. Evidence lives on the student's own machine, so they are its custodian
rather than the subject of a record somebody else keeps. There is no
infrastructure excuse available. And it exists next August regardless of what a
procurement office decides.

**The honest comparison** is that this version is a better course and a more
fragile one. It depends on a contract, an IT-owned sandbox and broker, and about
2,208 lines of notebook tooling that one person has to maintain, plus the
uncosted work around it. The constrained course depends on nothing and teaches
the harder half of the job. Run both if the college can:
this one when the environment exists, the other as the thing that still works
when it does not.
