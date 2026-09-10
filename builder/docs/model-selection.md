# Which model each week runs on, and what decided it

**Written:** 2026-09-07. **Amended:** 2026-09-09. **Status:** decided, with the
week 1 and week 6 rows corrected. Five models measured, three rejected. Read
the amendment before quoting the week 6 section.

## The decision

| Week | Model | Why |
|---|---|---|
| 2, 3, 4, 5, 7 | `granite-3b` | Cheapest that does the job, and week 2 needs a model that sometimes returns malformed output |
| 1 | `granite-8b` | `granite-3b` calls email 001 legitimate 8 times in 20 at t=1.0, so a student would read heat as error rather than as variation |
| 6 | `granite-3b` | `granite-8b` cannot return a readable verdict on email 024 in 6 of 8 runs of the shipped code, and a twin pair needs both twins readable |
| 7, one comparison | `granite-8b` | The measured contrast the wrap-up teaches. Its direction was reversed on 2026-09-10, see the second amendment |

`granite-3b` and `granite-8b` are the only models the proxy serves and the only
two any student key may name.

## Amendment, 2026-09-09: what no longer stands

Week 6 was measured again, on the code students actually run. The rig is the
week 6 solution notebook's own pre-written cells. Every number in this
amendment comes from `docs/week6-measurement/README.md`, at eight runs a cell,
through the proxy, at the notebook's temperature.

**Week 6 runs on `granite-3b`.** That is what the notebook already sets, so the
config cell does not change.

Under the shipped code `granite-8b` cannot return a readable verdict on email
024 in 6 of 8 runs. With the body restored to the verdict call it is 7 of 8. A
twin pair needs both twins readable, so 8b cannot carry week 6.

The repaired guarded prompt does bring email 013 back to malicious on
`granite-8b`, 8 of 8. That is still not a reason to switch: in the same probe
the undefended answer on 024 fails to parse in 7 of 8 runs.

**Week 1 runs on `granite-8b`.** The row above said `granite-3b`, and the
notebook has said `granite-8b` since 2026-09-08.

Asked for a word and a sentence on email 001, `granite-3b` is wrong 8 times in
20 at t=1.0. `granite-8b` is wrong 0 times in 20 at every temperature tested.
The record is `docs/week1-measurement/README.md`.

**The section below is not evidence about the shipped path.** Its 510 runs a
model came from `lab/eval/week6_injection_test.py`. That script's two prompts
are single calls, with no loop, no tool results and no schema. No student
builds either one.

The three rejected models stay rejected, because the proxy no longer serves
them. Nothing else in that section may be quoted about week 6 as it ships.

**What replaces the week 6 demonstration.** On `granite-3b`, once the closing
call can see the email, injected 013 comes back benign 8 of 8 and
injection-free 024 comes back malicious 8 of 8. Both are ground-truth
malicious, so the paragraph turns a right verdict into a wrong one. Holding the
recipient constant leaves that unchanged, 8 of 8 either way.

**On `granite-3b` the guard does not answer the attack.** With the guarded
prompt repaired, 013 stays benign 8 of 8.

## Week 6, the one that was genuinely open

> **Superseded for the week 6 decision, 2026-09-09.** These runs used two
> hand-written prompts that no student builds. The record is kept; the numbers
> are not evidence about week 6 as it ships. The corrected row and the
> reasoning are in the amendment above.

510 runs per model, 17 cases, 15 trials each, at the temperature the notebooks
use. Injections are the ten payload-carrying emails in the corpus; the eval had
been testing six of them from a hand-written list that had drifted.

| Model | Injections land undefended | Land guarded | Guard effect | Benign called malicious |
|---|---|---|---|---|
| **granite-8b** | 61 of 120 | 45 of 120 | **+16** | 31 of 120 |
| granite-3b | 84 of 120 | 77 of 120 | +7 | 24 of 120 |
| gemma-3-12b | 45 of 120 | 45 of 120 | **0** | **75 of 120** |
| llama-3.1-8b | see note | see note | +19 | see note |
| qwen3-14b | see note | see note | **negative** | see note |

**Email 013 on `granite-8b` was read here as the demonstration the week
needs.** It is the twin-pair email the course already ships, and in these runs
it landed 12 times in 15 undefended and 0 times in 15 with the guard.

**That reading did not survive 2026-09-09.** On the shipped assembly
`granite-8b` cannot return a readable verdict on the other twin, and on
`granite-3b` the repaired guard leaves the attack standing. See the amendment
above.

### Why the three candidates were rejected

**gemma-3-12b** looked strongest in early single-run tests and is the clearest
rejection at scale. Its guard effect is exactly zero, 45 of 120 either way, and
it calls 75 of 120 benign emails malicious. Its good accuracy in the lab came
from the facts block, not from the model.

**llama-3.1-8b** is the cheapest model tested and has the widest aggregate
guard effect, but nearly every injection lands on it. A week where every
placement succeeds has no contrast between placements, which is most of what
week 6 teaches.

**qwen3-14b** is the most injection-resistant and the guard makes it worse.

## The other weeks

**Week 5** rests on 294 complete agent runs, recorded in
`week5-model-test.md`. It settles the design, which is 3B with reasoning off
and the stop condition owned by code. **Its figures predate the move from
ollama to the proxy**, so the direction stands and the numbers should not be
quoted as current until re-run.

**Week 7 was re-measured on 2026-09-10 and this paragraph is wrong.** It read:
*"Week 7 is measured on the current stack. 3B beat 8B on the batch at a third of
the cost, which is why the course teaches that size pays for judgement on thin
evidence and not behind a facts block."* Both halves are false on the code week
7 ships. The record is `docs/week7-measurement/README.md` and the correction is
the second amendment below.

**Week 3** stays on `granite-3b`, and `docs/week3-measurement/README.md`
settles it. This file first read week 3 as the case where 8B judges better
unaided. The shipped prompt does not show that.

Across five models, not one both flips email 008 for the right reason and
leaves 017 alone. `granite-8b` never moves at all and misses 008. Changing the
model does not rescue objective 3.2.

**Week 2** wants 3B specifically. The lesson is that a model sometimes returns
something broken and handling it is the work. A stronger model returns valid
JSON more often and quietly weakens the week.

**Week 4** is not model-marginal. It is tool calling, and every model tested
emitted a correct tool call three times in three.

**Week 1 was listed here as not model-marginal. It is.** A round of about
1,700 calls on 2026-09-08 moved it to `granite-8b`, with a probe that asks for
one word and one sentence, at 0.2 against 1.0. The record is
`docs/week1-measurement/README.md`.

## What this cost, and what it is worth

The three test models were added to the proxy with no cost fields and no
student access, and removed once measured. The student allowlist was verified
rather than assumed: a key minted with the student model list returned 403 on a
test model while the eval key returned 200. Total spend across roughly 3,000
measurement calls was under a dollar.

## A caution that applies to all of it

Every number here comes from one set of runs on one day. Models are
probabilistic and these figures will not reproduce exactly. The direction is
the finding. Four separate bugs in the measuring harness had to be fixed before
any of this was believable, and three of the conclusions reversed along the
way.

**And a second caution, learned on 2026-09-09.** A model comparison is only
evidence about the assembly it was run through. The week 6 numbers in this file
were taken on two hand-written prompts, and they decided a week whose real
prompt is built by a loop, three tools and a schema. Run the comparison through
the code the student runs, or do not quote it.

## Second amendment, 2026-09-10: week 7, measured on the code it ships

Week 7's numbers had never been taken on the stack it ships. The only record
was `content/video/runs/w7.json`, recorded 2026-09-05 against
`http://localhost:11434/v1`, the retired ollama endpoint, and before week 6's
rebuild changed the prompt week 7 builds.

Twelve passes on 2026-09-10, through the week 7 solution notebook's own
pre-written cells, at the notebook's temperature, one email per request, input
digests identical within each set. Full record in
`docs/week7-measurement/README.md`.

**The twenty batch emails, 026 to 045, three passes a model.** These appear in
no earlier week, so no prompt in this course was tuned against them.

| | `granite-3b` | `granite-8b` |
|---|---|---|
| Correct, of 60 | 34 | 48 |
| Accuracy | **0.567** | **0.800** |
| Per-pass | 0.550, 0.600, 0.550 | 0.800, 0.800, 0.800 |
| False positives | 26 | 11 |
| False negatives | **0** | **0** |
| Rows with no verdict | 0 | 1 |
| Distinct emails missed | 9 | 4 |

**The 24 teaching emails, 001 to 025 without 013, three passes a model.** Same
direction, wider gap: `granite-3b` 51/72 = 0.708, `granite-8b` 66/72 = 0.917.

**What this reverses.** 8B does not score worse than 3B behind the facts block.
It scores 23.3 points better on the holdout and 20.9 better on the teaching
set, for about twice the price. The old claim was taken before week 6's rebuild
and on the retired endpoint.

**Week 7 still runs on `granite-3b`, and the accuracy is not why.** Week 7
measures the agent the student built over six weeks, and that agent runs on
`granite-3b`. A config cell naming a different model hands the student a
different system to measure in the one week whose purpose is finding out what
theirs does. The week 7 spec puts it plainly: *"Nothing else about the agent
changes. The decision path built in week 6 runs untouched."*

The pre-registered threshold happened to block the switch too, on a clause
about failure rates, but that is not the reason and it is recorded in
`docs/week7-measurement/prereg-claude.md` amendment 3 that it is not.

**What `granite-3b` actually does on the batch, because a page has to say it.**
It calls 9 of the 10 benign emails malicious, 8 of them in all three passes,
and misses no attacks at all. Zero false negatives, 26 false positives in 60.
That is the finding week 7 teaches from.

**The caution from the first amendment still stands, and this measurement
obeyed it.** A model comparison is only evidence about the assembly it was run
through. These twelve passes went through the shipped solution notebook's own
cells, not a hand-written prompt.
