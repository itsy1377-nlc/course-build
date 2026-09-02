# ITSY 1377, the funded proposal

A second proposal, to sit beside `docs/itsy1377-course-proposal.md` rather than
replace it. Same course, same seven weeks, same outcomes, same students. What
changes is the environment.

**The scenario.** A server on the school network hosts per-student Jupyter
notebooks and labs, **each student isolated from every other**. A LiteLLM gateway runs on it, each student holding their own
token and a budget under ten dollars for the semester. Every prompt and output
is logged under school control and kept until grade appeals close. An AWS
Bedrock contract supplies two or three permissively licensed open models, billed
on usage, against three hundred dollars per class per semester. The school takes
responsibility under the contract, which resolves the age question.

---

## Status: not yet fit for a committee or a procurement office

Adversarial review found ten defects, three of them plain errors of mine, and
the verdict was that this document is not yet fit to put in front of either. It
has been corrected where correction was possible in a document, and the
remainder are recorded here rather than smoothed over.

**Corrected in this revision:** the run count said 350 against rows summing to
280; the budget claimed to be measured from recorded traces which contain no
usage data at all; the gating experiment's arithmetic did not match its own
procedure and its statistical claim was overstated; the silent-failure account
was broader than the code supports; the control fix was cosmetic; week 6 was
called unchanged while carrying the largest hosted spend; and a governance rule
forbidding hosted-only graded work was broken by four graded activities in the
same document.

**Still outstanding, and each blocks approval:** a points and fallback matrix;
a powered gating experiment with a real chain detector; a decision on where
local inference runs and measured capacity for it; exact models, versions,
regions, licences and prices with a replacement policy; and the records,
minors, access, deletion, incident response, appeals, staffing and
accessibility plans named in section 6.

**Read this as a design under review, not a submission.**

## 0. One experiment gates everything below, and it costs under a dollar

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

## 1. What the money actually buys, ranked

**1. The model becomes a variable.** This is the strongest item and it does not
depend on the injection landing. Today a student runs one model, so a rate is a
fact about a system. With three behind one gateway, a student runs their own
unchanged case across all of them and learns that susceptibility is a property
of the model as much as of the attack, and that a finding has a scope which
includes what you tested it on. `harness/report.py` already prints a banner
saying every rate belongs to one exact model, temperature and prompt. Today that
banner is a warning nobody can act on. With a gateway it becomes an experiment.

**2. Variance, which is what is actually broken today.** The injection cases are
0 of 5 on every model, payload and phrasing measured so far. That means week 3
has no dynamic range: the student who writes a careful, well-placed injection
and the one who writes a lazy one get the same number. Craft cannot be rewarded,
predictions cannot be graded against outcomes, and the class board that runs
weeks 3 to 7 shows twenty-five identical rows. A board where everyone scores the
same is not a board, and that board was the best-reviewed hour in the course.
**This is conditional on the gating experiment.**

**3. Three records of one event, and the official one is the weakest.** With a
gateway there are three logs of every action: the gateway record, the agent
trace, and the target's own outbox and audit log. Only the outbox proves a
message exists. The gateway proves only that the model asked. **The record the
school keeps, stamped official and retained until appeals close, is the one
least able to prove the claim.** That is the course's central lesson reproduced
in the classroom's own plumbing, with the student inside it rather than reading
about it.

**4. Cost as a real subject.** Ninety minutes' worth, genuinely: token
economics, context growth, rate limits, and a runaway loop that costs actual
money. The constrained proposal lists runaway cost as a case card it never
exercises.

**5. An independent record of whether the work was done.** Every artifact in the
constrained course is written by the student's own machine, so a student willing
to fabricate one can fabricate all of them, and the canary scheme does not stop
that because students are handed their own tokens on purpose. A gateway log is
the first record in this course that the student does not write. That is a real
assessment control, and it deserves counting among what the money buys.

**6. A shared incident, assembled rather than live.** Students are isolated, so
this cannot be twenty-five analysts acting on one database at the same moment,
and it should not be: that version needs concurrency the harness does not have
and would let one student break another's graded work.

It works asynchronously instead, and the asynchronous version is better. In the
48 hours before the session each student spends ten minutes working four tasks
in their own environment, one of which they are not told is different from
anybody else's. The instructor exports and merges those logs into one incident
pack. The session then works that pack, where the timeline holds twenty-five
actors and every student can prove their own rows and nobody's else's.

That preserves the thing worth having, which is a claim that cannot be settled
from one person's evidence, while removing the concurrency risk entirely. It is
also the only affordance the constrained design cannot reach at all, and it
carries the heaviest build cost on this list. See section 5.

---

## 2. The seven weeks, and most of them barely change

Everything five review rounds proved out is preserved: something happens in the
first half hour, the student writes their own attack, a class pool and board
across weeks 3 to 7, a real mystery, the spoiler rule, evidence over assertion.

| Wk | Change from the constrained version | Why |
|---|---|---|
| 1 | **Minimal.** The cold open still runs on the local model. The inventory gains one column, the scope gate gains three clauses | The best half hour in the course must not depend on a network service during a specific fifty minutes |
| 2 | **Changed most, and cheaply.** Adds a model sweep, about forty minutes | The week already asks what varies. The model is one more thing that varies |
| 3 | **Changed, but less than expected.** Local run and hand-marking first, hosted comparison second | Hosted first would make trace reading confirmatory instead of load bearing, which is the most valuable thing week 3 does |
| 4 | **Adds three-source reconciliation**, about twenty-five minutes | Week 4 is already the audit log week |
| 5 | **Changed most structurally.** A shared multi-actor incident replaces the solo case pack as the session, with the packs kept as fallback | The one thing the constrained design cannot reach |
| 6 | **Pedagogically unchanged, but not free** | The control arc rests on the two cases that land 5 of 5 on every model, so money buys the *lesson* nothing. It does buy iteration: the budget assigns week 6 sixty hosted runs, which is the largest single line, because measuring a control before and after on more than one model is how a student learns the control is not model-specific. Saying the lesson is unchanged while the spend is not is the honest version |
| 7 | **Runs local**, with a ten-minute hosted coda | Throughput, not money. See section 4 |
| Final | Adds one case: the loop that paid | Fills a gap the constrained proposal already names |

**Week 2's sweep is the best value in the whole proposal.** One line of config
changes. Run two cases at five trials across three hosted models, then put the
local model beside them as a fourth column and the deterministic simulator as a
fifth, where it is 5 of 5 on everything by construction and carries its honesty
banner. The simulator sitting in the same table as three real models is the
cleanest possible teaching of why that banner exists, and it costs nothing.

The mandatory column is **why each miss missed**: refused in words, called no
tool, right tool with the wrong argument, stopped after the first result. That
is the difference between a table and a leaderboard. The graded output is two
sentences: the sentence a vendor would put on a slide from this table, and the
sentence the evidence actually supports.

**Week 3's ordering is the whole design.** Prediction sealed before any run.
Author the case. Five trials local. Hand-mark the local traces. Then change one
line and run the same case on two hosted models. **The graded claim is the
divergence step, not the outcome:** which step did the models part at, and what
does each result establish and not establish. A student who writes "it worked on
the big model" has not answered the question.

**Week 4's reconciliation is the sharpest hour this environment enables.** One
question: for each of your three records separately, write the strongest single
sentence that record supports on its own. Then the closing line, written into
the evidence pack: "if I were investigated using only my log, the thing it could
not show about me is ___." That is the entire privacy lesson, from the student's
own position as the data subject, with no worksheet.

---

## 3. A procurement decision that has to be made before the contract

**Do not buy three peers.** Three recent, heavily safety-tuned models of similar
size will produce three near-identical columns and a dull hour. Buy a capability
spread.

**And apply the licence bar this project already set.** The constrained analysis
rejected two otherwise capable models for carrying the Llama Community licence
rather than a permissive one. Much of the open tier on Bedrock is Llama
Community. Either the model list is narrower than the scenario assumes, or the
course contradicts its own recorded analysis. That needs settling before signing,
not after.

---

## 4. The budget is affordable, and it is an estimate rather than a measurement

**A correction to an earlier draft, which claimed this was measured.** It is
not. The 2,428 recorded traces contain **zero provider usage fields**, because
the agent loop takes only the assistant message from each response and discards
the rest. The traces support a defensible estimate of workload shape, meaning
how many model calls an agent run makes and roughly how much context it carries.
They cannot support a token measurement, and this document should not have said
they did.

**Workload shape, which the traces do support:** about 2.9 model calls per agent
run across 7,055 inferred requests.

**Token allowance, which is planning judgement:** 5,000 input tokens per run is
defensible. **500 output tokens is not safe**, because a reasoning model can
spend a thousand tokens producing no visible content at all, and this project has
already measured one needing about four thousand. Plan output at 2,000 per run,
and treat six loop steps each consuming a completion allowance as the real
ceiling rather than a single flat worst case.

| | Hosted runs per student |
|---|---|
| Week 2 variance and sweep | 40 |
| Week 3 hosted comparison and board revisions | 40 |
| Week 4 evidence packs | 20 |
| Week 5 shift | 10 |
| Week 6 (see below: this is why week 6 is not "unchanged") | 60 |
| Week 7 coda | 10 |
| Slack, experiments, failed runs | 100 |
| **Total** | **280** |

An earlier draft printed 350 against rows that sum to 280, which is a 25 per
cent overstatement and a plain arithmetic error. Use 280 as the plan and 350 as
the headroom figure, and say which is which.

**Costed against real published prices rather than a generic tier**, because the
price varies by model far more than by parameter count:

| Model | Price per million in / out | 280 runs |
|---|---|---|
| Ministral 8B | 0.15 / 0.15 | about 6 dollars a class |
| Qwen3 Next 80B | 0.15 / 1.20 | about 9 dollars a class |
| Mistral Large 3 | 0.50 / 1.50 | about 23 dollars a class |

**A class of twenty-five costs somewhere between six and twenty-five dollars
against three hundred**, depending entirely on which models are chosen. Verify
every price and region at contract time; none of these should be carried forward
from this document.

**What is missing from the run count**, and should be added before anyone signs:
the final block's cost case, grading re-runs and accommodations, appeals,
billed attempts lost to timeouts, model evaluation and development work, and the
gateway's own monitoring, log storage and administration. None of those is large.
Together they are not nothing.

**Instructor consumption needs its own key with its own ceiling.** The gating
experiment alone, at thirty trials, is larger than the earlier draft assumed.
Add a per-term baseline across three models, case-pack regeneration, and a load
test with twenty-five simulated keys before week 7.

**Week 7 runs local, and that raises a question this proposal has to answer
rather than assume.** Twenty-five controls against twenty-five pooled cases at
five trials over two rounds is over six thousand runs in one session. The
dollars survive it; the throughput does not, and this project has already
predicted that rate limits read to students as broken code. But **"runs local"
is not free in this architecture, and the earlier draft did not say where local
means.** If it means the student's own laptop, the funded course has quietly
re-inherited the unverified deployment assumption it was supposed to remove. If
it means the server, that is roughly two and a half to three gigabytes resident
per model instance, times twenty-five, plus contention. **Name it, and measure
it, before week 7 depends on it.**

---

## 5. The biggest risk is the failure this course exists to teach

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

## 6. What has to be written down before a single prompt is logged

The load-bearing one first.

**No learning outcome and no rubric row may cite a hosted-only result.** That
single rule means a contract lapse, an outage, a deprecation, or a model that
refuses everything costs the course pages rather than a re-approval.

**And an earlier draft of this proposal broke that rule four times over**, which
review caught and which is worth recording rather than quietly fixing. Week 2
graded conclusions drawn from the hosted sweep. Week 3 graded the hosted
divergence step. Week 4 required gateway reconciliation. The final block added a
cost case that only exists on the meter. Every one of those is hosted-only work
carrying points, in a document whose load-bearing governance rule says it may
not.

**The resolution is a points and fallback matrix, published with the syllabus**,
and it has to be built rather than asserted. For each graded artifact: the
points it carries, whether it is reachable on the local path, and if it is not,
the supplied evidence a student receives when the gateway is unavailable. The
honest version is probably that hosted work carries participation credit and
feeds a graded artifact that can also be produced locally, so that an outage
costs a student a comparison rather than a grade. That is a real design
constraint on weeks 2, 3 and 4, and it is not yet done.

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

## 7. What each version teaches better

**The funded version teaches, and the constrained one cannot:** that
susceptibility is a property of the model; which of your findings survive a
model upgrade; reconciling a claim against records somebody else holds; sample
size seen rather than asserted, your five against the class's hundred and
twenty-five; three records of one event where the official one is weakest; and
token economics with real money.

**The constrained version teaches better, and the first two are not close:**

**Negative-result literacy, forced rather than elective.** Its marquee attack
usually fails, so "what a negative result does not establish" is learned by
necessity rather than covered in a lecture. Where attacks land reliably, that
lesson has to be manufactured, and manufactured lessons are the ones students
correctly discount.

**The chain that stops at four steps is the best teaching artifact in the
course, and a hosted success degrades it.** The verdict says no hits; the student
must read the trace to discover four steps landed anyway. **The constrained
course makes trace reading load bearing; the funded one risks making it
confirmatory.**

Also: chain of custody, because the student holds their own evidence rather than
being the subject of a record somebody else keeps. Diagnosability, because on a
laptop there is one causal chain and no external excuse available, whereas "the
server was slow" is always available and sometimes true. Reproducibility, from a
pinned model and greedy decoding. And it still exists next August regardless of
what any procurement office decides.

---

## 8. The recommendation, and the case against it

**The strongest argument against what I am about to recommend**, and it is a
good one. The constrained course's core delivery assumption, that a locked-down
loaner will run the portable bundle, is explicitly unverified. The funded
scenario supplies equitable hardware, central support, model comparison, real
cost evidence and independently held logs. Negative-result literacy can be
preserved with one deliberately retained losing case and the simulator; it does
not require running a second production stack. And the claim that a hosted
negative result would be "manufactured" while a local one is honest is
sentiment, not measured pedagogy. I wrote that line, and I cannot support it.

**What I actually recommend.**

Run both, as one course with two paths: the local model as the graded baseline
and the reproducible control, the hosted models as the comparison column. The
finding worth having is not "the attack works now" but **"it works there and not
here, and I can tell you which step turned and why"**, and that sentence needs
both machines to say it.

**But the two-path production course is not yet operationally credible**, and
that is the honest state of this document. Section 4 does not say where local
inference runs. Section 6 has a governance rule that sections 2 and 4 break.
The control validity fix was cosmetic until this revision. Until those are
closed, "run both" is a design intention rather than a plan.

**If the college can genuinely run only one**, the case is closer than an
earlier draft of this document allowed. The constrained version teaches
negative-result literacy by necessity, keeps the student as custodian of their
own evidence, removes every infrastructure excuse, and exists next August
regardless of any procurement decision. The funded version removes the one
unverified assumption the constrained version cannot remove by itself, which is
whether the thing runs at all on the hardware the poorest students have.

**That is the trade, stated plainly:** the constrained course teaches the harder
half of the job and might not run for the students who need it most. The funded
course will certainly run and has to work harder to teach the same lesson. On
that framing I would take the funded environment and defend the pedagogy
deliberately, rather than take the constrained one and hope the loaner test
passes.

**What the money is really worth buying** is not a better model. It is the
second column, the third record, an independent record of whether the work was
done, and ninety minutes on what a runaway loop costs. Those are worth having,
they cost about twenty-five dollars a class, and none of them requires the
injection chain to land.
