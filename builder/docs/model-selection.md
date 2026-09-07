# Which model each week runs on, and what decided it

**Written:** 2026-09-07. **Status:** decided. Five models measured, three rejected.

## The decision

| Week | Model | Why |
|---|---|---|
| 1, 2, 3, 4, 5, 7 | `granite-3b` | Cheapest that does the job, and week 2 needs a model that sometimes returns malformed output |
| 6 | `granite-8b` | The only model where the guardrail visibly answers the attack |
| 7, one comparison | `granite-8b` | The measured contrast the wrap-up teaches |

`granite-3b` and `granite-8b` are the only models the proxy serves and the only
two any student key may name.

## Week 6, the one that was genuinely open

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

**Email 013 on `granite-8b` is the demonstration the week needs.** It is the
twin-pair email the course already ships, and it lands 12 times in 15
undefended and 0 times in 15 with the guard. That is objective 6.2 and
objective 6.3 in one comparison, with enough variance to be honest about.

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

**Week 5** is the best-measured week in the course: 294 complete agent runs,
recorded in `week5-model-test.md`. It settles the design, which is 3B with
reasoning off and the stop condition owned by code. **Its figures predate the
move from ollama to the proxy**, so the direction stands and the numbers should
not be quoted as current until re-run.

**Week 7** is measured on the current stack. 3B beat 8B on the batch at a third
of the cost, which is why the course teaches that size pays for judgement on
thin evidence and not behind a facts block.

**Week 3** is the case where 8B is better at unaided judgement. That is the
week's own point: the model is not asked to judge unaided, it is given facts.

**Week 2** wants 3B specifically. The lesson is that a model sometimes returns
something broken and handling it is the work. A stronger model returns valid
JSON more often and quietly weakens the week.

**Weeks 1 and 4** are not model-marginal. Week 1 is a single call. Week 4 is
tool calling, and every model tested emitted a correct tool call three times
in three.

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
