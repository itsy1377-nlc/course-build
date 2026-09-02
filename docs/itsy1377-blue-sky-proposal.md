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

**So before a page is written:** run the three injection cases at five trials
against each candidate Bedrock model, through `build/modeltest/student_run.py`
and not a purpose-built rig. That is about ninety runs, roughly half a million
tokens, under a dollar, and two hours of wall clock.

**Write the course so either answer is a good week.** If the chain still does not
complete across three hosted models, that is a stronger finding than the
constrained course has today: three columns of zeros with three different
reasons for the zeros. It costs nothing to be ready for that.

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

**5. A shared incident, assembled rather than live.** Students are isolated, so
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
| 6 | **Unchanged, deliberately** | The control arc rests on the two cases that land 5 of 5 on every model. Money buys week 6 nothing, and saying so is the honest part of this proposal |
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

## 4. The budget works, by a wide margin

Measured from 2,428 recorded traces rather than estimated. Plan on 5,000 input
and 500 output tokens per agent run, 8,000 worst case.

| | Hosted runs per student |
|---|---|
| Week 2 variance and sweep | 40 |
| Week 3 hosted comparison and board revisions | 40 |
| Week 4 evidence packs | 20 |
| Week 5 shift | 10 |
| Week 6 control iterations | 60 |
| Week 7 coda | 10 |
| Slack, experiments, failed runs | 100 |
| **Total** | **about 350** |

At mid-tier open-weight prices that is well under a dollar per student, and at
70B-class prices about a dollar. **A class of twenty-five costs roughly ten to
thirty dollars against a three hundred dollar budget.** Prices must be verified
at contract time rather than carried from this document.

**Two things the arithmetic reveals.**

The ten dollar per student cap is about ten times larger than the course needs,
which means it will never bind in normal use and will only ever be hit by a
runaway loop. That makes it a good teaching instrument and a poor guardrail: set
a separate, small, deliberately burnable key for the cost lab rather than letting
a student spend their working budget on it.

**Instructor consumption is unbudgeted in every version of this**, and needs its
own key with its own ceiling: the gating sweep, a per-term baseline across three
models, case-pack regeneration, and a load test with twenty-five simulated keys
before week 7. Call it five dollars and give it a separate line.

**Week 7 runs local, and this is the recommendation most likely to be argued
with.** Twenty-five controls against twenty-five pooled cases at five trials over
two rounds is over six thousand runs inside one hundred-minute session. The
dollars survive that; the throughput does not, and this project already predicted
that rate limits read to students as broken code. Local is free, unthrottled,
deterministic, and cannot be broken by a classmate. Then a ten-minute hosted
coda: point your finished control at a second model and find the allowlist blocks
the disallowed recipient regardless of which model asked. Before and after
identical across models, while the attack rates were not. That is the strongest
available evidence for where controls belong, for about three cents.

---

## 5. The biggest risk is the failure this course exists to teach

**A gateway adds three new ways for a run to fail silently, and they are
indistinguishable from the course's proudest finding.**

A content filter, a provider refusal, a rate limit, or a student hitting their
budget cap can each return a well-formed response with empty or declining
content. `agent/llm.py` returns that message and raises nothing. The loop then
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
2. Put the sample size in the control verdict too.
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

**Isolation does not fix the canary forgery problem.** That one is about
arithmetic rather than access, and it is addressed below.

**A student can still forge a classmate's proof, and isolation does not stop
it.** Canary tokens are derived as a keyed hash of the term salt and the student
ID, the default salt is published in the source, and the student sets their own
ID. Forging a classmate's token requires no access to their environment at all:
it requires the salt, which is in the source, and their ID, which is guessable.
Isolation prevents a student from touching another's files. It does nothing
about a student computing another's token in their own notebook and pasting it
into their own evidence.

**So the launcher must inject only that student's three tokens, and the salt must
never enter a student-readable environment.** On laptops this was a theoretical
concern nobody had a reason to act on. In a hosted environment with a class board
and a common image it is the single control that keeps "evidence cannot be
copied" true, and it is worth doing whether or not any week is shared.

---

## 6. What has to be written down before a single prompt is logged

The load-bearing one first.

**No learning outcome and no rubric row may cite a hosted-only result.** That
single rule means a contract lapse, an outage, a deprecation, or a model that
refuses everything costs the course pages rather than a re-approval. It is also
what keeps the local model and the simulator as live paths rather than
decorative ones.

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

## 8. The recommendation

**Run both, as one course with two paths, rather than choosing.**

Keep the local model as the graded default and the reproducible baseline. Add
the hosted models as the comparison column. The finding worth having is not "the
attack works now" but **"it works there and not here, and I can tell you which
step turned and why"**, and that sentence needs both machines to say it.

If the college can genuinely run only one, run the constrained course. Not from
caution: it teaches the harder half of the job and cannot be talked out of it,
every genuinely new thing the funded version buys is an upgrade to an hour
rather than a week, and its most seductive lesson, that the big model fell for
it, is the one a student is most likely to misread as "the fix is a better
model". That is exactly wrong, and refuting it is what weeks 6 and 7 are for.

**What the money is really worth buying** is not a better model. It is the
second column, the third record, and ninety minutes on what a runaway loop
costs. Those are worth having, they cost about thirty dollars a class, and they
do not require the injection chain to land.
