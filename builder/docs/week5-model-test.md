# Week 5 model test: can a 3B model drive the bounded loop?

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program  
**Phase 1 blueprint, item 5.** Prepared 2026-09-04.  
**Audience:** the program manager. Nothing here assumes you are building the course.

Week 5 is the week this course is most likely to fail. The agent has to choose its next check from what it just learned, stop when it has enough, and never run away. That is the least certain behaviour on a small model. It is also the hardest week for students, who arrive with no programming background. So it was measured before the lab was written.

## What was measured

294 complete agent runs. Each run is one email triaged from start to finish, so a run is several model calls, not one. The six emails are the six the week 5 lab uses, one per loop shape. Every run was scored against the corpus record for that email: the tools it should call, the order, the reason the run should end, and the verdict.

Four lab designs were tested, because the point of the exercise was to find one that works rather than to grade a single guess.

| Design | What the model decides |
|---|---|
| free | the model picks any tool and decides for itself when to stop |
| guided | the sender check is run for the student, the model picks at most one more tool and decides when to stop |
| coded | the model picks the next tool, the student's code decides when to stop |
| coded anchored | as coded, plus one line telling the model to start with the sender check |

### The world, asserted before measuring

- Serving stack: ollama version is 0.32.15, OpenAI-compatible endpoint at `http://localhost:11434/v1`.
- Model `granite4.1:3b`, blob digest `6fd349357287c7ff`.
- Model `granite4.2:3b`, blob digest `40577dc168a3a9ad`.
- Step cap: 4. One model request at a time, never two.
- Tool results: Tool results come from spec/corpus-spec.json tool_expectations, which lab/tools/check_tools.py asserts the shipped tools reproduce exactly.
- Every email file still carries the exact digest recorded when it was read. The measurement is against the files that ship.

That last check is not decoration. An earlier sweep of 234 runs was thrown away because an authoring job regenerated four of the six emails while the measurement was reading them. The digests caught it.

## The result

| Configuration | Model | Design | Right tool path | Right stop reason | Right verdict | Valid answer | Tokens per run | Seconds per run |
|---|---|---|---|---|---|---|---|---|
| granite4.1-free | granite4.1:3b | free | 15/30 | not applicable | 25/30 | 30/30 | 4,791 | 2.9 |
| granite4.1-guided | granite4.1:3b | guided | 15/30 | not applicable | 25/30 | 30/30 | 2,508 | 1.9 |
| granite4.2-noreason-free | granite4.2:3b reasoning off | free | 10/30 | not applicable | 21/30 | 30/30 | 6,508 | 4.8 |
| granite4.2-noreason-guided | granite4.2:3b reasoning off | guided | 20/30 | not applicable | 21/30 | 30/30 | 2,246 | 2.2 |
| granite4.2-reason-free | granite4.2:3b reasoning on, 512 token budget | free | 1/18 | not applicable | 0/18 | 0/18 | 2,224 | 10.7 |
| granite4.1-coded | granite4.1:3b | coded | 0/30 | 30/30 | 20/30 | 30/30 | 3,432 | 2.7 |
| granite4.2-noreason-coded | granite4.2:3b reasoning off | coded | 29/30 | 30/30 | 28/30 | 29/30 | 3,813 | 4.1 |
| granite4.1-coded-anchored | granite4.1:3b | coded anchored | 15/30 | 30/30 | 25/30 | 30/30 | 3,268 | 2.4 |
| granite4.2-noreason-coded-anchored | granite4.2:3b reasoning off | coded anchored | 27/30 | 28/30 | 28/30 | 28/30 | 3,774 | 3.8 |
| granite4.2-reason-free-4096 | granite4.2:3b reasoning on, 4096 token budget | free | 9/18 | not applicable | 12/18 | 12/18 | 8,108 | 81.0 |
| granite4.2-reason-coded-4096 | granite4.2:3b reasoning on, 4096 token budget | coded | 13/18 | 18/18 | 16/18 | 17/18 | 7,639 | 84.6 |

Right tool path means the exact tools in the exact order the corpus record expects. Right stop reason applies only to the designs where code owns the stop, and means the run ended for the reason the corpus records. Valid answer means the final reply parsed as the JSON the lab asks for.

## What the numbers say

### 1. The models choose tools well and stop badly

Across the runs where the model was free to choose, it picked the correct first tool 25/30 times but produced the correct whole path only 15/30 times. The gap is the model not stopping once it had enough. On the email whose sender is already known bad, it ran the link check anyway, reached the right verdict, and spent an extra step doing it.

### 2. Moving the stop condition into code fixes it

When a deterministic rule in the student's own code decides when to stop, the run ends for the right reason 136/138 times across every model and every email. The model's remaining job, choosing the next check, is the part it is already good at. This is the design the week 5 spec already describes, and the measurement supports it.

### 3. One configuration is clearly the one to ship

`granite4.2-noreason-coded`: granite4.2:3b with reasoning off, in the design where code owns the stop. It produced the exact expected tool path 29/30, the right stop reason 30/30, and the right verdict 28/30, at 3,813 tokens and 4.1 seconds per triage.

### 4. Reasoning mode is not usable for this course

At the 512-token answer budget the labs use, Granite 4.2 in its default reasoning mode spent the whole budget thinking and returned empty content 18/18 times. That is a configuration incompatibility, not a limit of the model, so it was re-tested at eight times the budget.

At 4,096 tokens it works, and it still should not be used. Across 36 runs it averaged 7,874 tokens and 83 seconds for a single triage, against 3,813 tokens and 4.1 seconds for the recommended configuration. A student waiting a minute and a half per email will assume the notebook has hung.

## Per email

| Email | g4.1-free | g4.1-guided | g4.2-free | g4.2-guided | g4.2-reason-free | g4.1-coded | g4.2-coded | g4.1-coded-anchored | g4.2-coded-anchored | g4.2-reason-free-4096 | g4.2-reason-coded-4096 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 004-cfo-quick-task | 5/5 | 5/5 | 3/5 | 0/5 | 0/3 | 0/5 | 5/5 | 0/5 | 5/5 | 0/3 | 3/3 |
| 005-slatemoor-past-due-statement | 5/5 | 5/5 | 0/5 | 5/5 | 0/3 | 0/5 | 5/5 | 5/5 | 5/5 | 3/3 | 2/3 |
| 007-larkseal-contract-signature | 0/5 | 0/5 | 0/5 | 5/5 | 0/3 | 0/5 | 5/5 | 0/5 | 5/5 | 0/3 | 3/3 |
| 010-ferncrate-rfq-share | 5/5 | 5/5 | 1/5 | 5/5 | 1/3 | 0/5 | 5/5 | 5/5 | 4/5 | 2/3 | 1/3 |
| 011-po-20431-thread-reply | 0/5 | 0/5 | 1/5 | 5/5 | 0/3 | 0/5 | 5/5 | 5/5 | 4/5 | 3/3 | 3/3 |
| 012-elmhollow-badge-access | 0/5 | 0/5 | 5/5 | 0/5 | 0/3 | 0/5 | 4/5 | 0/5 | 4/5 | 1/3 | 1/3 |

Cells are right tool paths out of trials.

## Two findings about the corpus, not the models

**Email 012 splits the configurations, and only the recommended one gets it right.** It is a real vendor on a new domain, with a link host on neither list, asking for names. Most configurations read that as an attack. The recommended configuration answered correctly 4/5; every other configuration together answered correctly 9/44, and Granite 4.1 called it malicious in all 20 of its runs. So this is a genuine false positive for the weaker designs and a case the shipped design usually survives. Week 5 still grades the loop rather than the verdict on it, because the verdict is not stable across models, and week 7 should expect it in the false positive column.

**Email 012's recorded stop reason was wrong and is now fixed.** The corpus said the run should end at the step cap. Only three tools exist under a cap of four, so a well-behaved agent runs out of tools first. Every run confirms it. The corpus record, its ground truth entry and the week 5 spec now all read `tools_exhausted`. The step cap is still taught, through the deliberately uncapped run the lab already includes.

## Recommendation

**Standardise on granite4.2:3b with reasoning switched off**, and keep the week 5 design in which the student's code owns the stop condition. Set `reasoning_effort` to `none` in the notebook configuration cell, on every request and for every model. It is NOT gated by model name. Re-measured 2026-09-04: `none` returns HTTP 200 on both models, and only `low`, `medium` and `high` are refused by granite4.1:3b, with `"granite4.1:3b" does not support thinking`. A name gate matched the literal text `granite4.2`, so any hosted alias would have left reasoning on for the term, silently.

**Keep Granite 4.1 3B as the fallback**, with one caveat stated in the instructor guide. In the same design it ends the run for the right reason every time, but it chooses a different tool order, so a rubric that grades tool order would fail students for the model's behaviour. The week 5 rubric grades the stop reason and the trace, not the order, which is what makes either model safe to teach on.

**Re-run this measurement every term.** The command is `python3 builder/lab/eval/week5_loop_test.py --all`. It asserts the endpoint, the model digests and the hash of every email before it measures, and writes its results after every run.

