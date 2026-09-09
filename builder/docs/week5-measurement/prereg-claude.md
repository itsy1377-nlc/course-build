# Week 5 pre-registration, written 2026-09-09 before any probe ran

## The claim under test

Objective **5.1, "Build a triage loop with a four-step cap and a stop
condition"**, is the at-risk one. 5.2 (record tool order and stop reason) and
5.3 (compare capped and uncapped token cost) are provisionally sound and are
checked here rather than assumed.

The cap is half of 5.1 and it is the week's headline control: one of the five
stop reasons is entirely about it, the reading gives it a section, the quiz
asks about it, and the wrap-up says it carries the week.

## What is already provable without a model

`MAX_STEPS = 4`. `usable_tools()` returns three names when the email has a link
host and two when it does not. The loop is
`while step < max_steps and tools_left(trace)`, and `out_of_room()` returns
`step_cap` only when a usable tool is still unused after the loop stops.

So on a three-tool email `step_cap` needs four steps used **and** one tool
untouched, which takes at least two repeated tools. On a two-tool email it
takes three. And `LOOP_INSTRUCTIONS` tells the model in as many words: *"Do not
ask for a tool you have already run."*

The corpus agrees it was never planned for. Not one of the six lab emails
carries `expected_loop.stop_reason: "step_cap"`; they carry `internal_sender`,
`decisive_malicious` twice, `decisive_benign` and `tools_exhausted` twice.

## Probe 1: does the shipped loop ever reach the cap

Six lab emails, n=8 runs each, the solution's `run_loop()` at `MAX_STEPS = 4`.

  P1a  The defect is CONFIRMED if `step_cap` is the stop reason in fewer than
       3 of 48 runs. I expect zero and I am recording the number rather than
       asserting it.
  P1b  Record, per run: steps used, the tool order, whether any tool repeated,
       and at which step position a repeat first appeared. The blind student
       reports that repeats begin at step 4 in the uncapped run, one step after
       the guard has already closed the loop. If repeats appear at step 2 or 3
       at any measurable rate, the cap is reachable and the fix is different.

  What would tell me I am wrong: `step_cap` appearing in 3 or more of 48 runs.
  Then the control does fire, rarely, and the fix is to make the week honest
  about the rate rather than to force it.

## Probe 2: the candidate fix

The fix I am inclined toward adds a pre-written cell that calls the student's
own `run_loop()` with `max_steps=2` on email 012. `run_loop` already takes
`max_steps` as a parameter, so nothing shared changes, and the cell proves the
student's own cap works rather than demonstrating a hand-built trace.

This should be deterministic by construction, not merely likely: two steps
cannot exhaust three usable tools, so `tools_left` is never empty and
`out_of_room()` must return `step_cap`. Email 012's reputation is `unknown`
and its one host is `unlisted`, so no branch of `decisive_stop()` can fire and
end the run early.

  P2a  The cell ships only if `step_cap` is the stop reason in **8 of 8** runs
       on 012 at `max_steps=2`. A construction argument that fails even once
       in eight is a construction argument I have got wrong, and the cell would
       have to print what it got rather than assert.
  P2b  Steps used must be exactly 2 in 8 of 8. A run that stops at 1 step means
       `decisive_stop()` fired somewhere I did not expect.
  P2c  The same call on email 005 must NOT give `step_cap`, because 005's
       reputation is `trusted` and its host `allowlisted`, so `decisive_stop()`
       should end it. This is the discriminating control: it shows the cell is
       reporting the cap rather than reporting `max_steps=2`.

## Probe 3: the cost model the reading teaches

The reading says the first request is "about 1,500 tokens" and each finished
step adds "roughly another 100 tokens", and its worked arithmetic predicts
about 20,500 tokens for the twenty-step uncapped run. The blind student
measured 1,696 to 1,896, 138 to 174, and **64,016**.

  P3a  Record the real first-request size, the real per-step increment, and the
       real twenty-step total. Any figure the page states that sits outside the
       measured range gets replaced by the measured one, or by a range.
  P3b  5.3 asks the student to compare a capped run against an uncapped one.
       Record both totals on 012 so the comparison the objective names is
       backed by a number this course has actually seen.

## What I will not do

`MAX_STEPS`, `TOOL_NAMES`, `usable_tools()`, `tools_left()`, `out_of_room()`,
`decisive_stop()`, `first_call()`, `append_turn()` and `run_loop()`'s signature
are shared with weeks 6 and 7, which pass a `step_guard` into the same loop.
Week 6's measured guardrail behaviour rests on them. None of them is edited
unless a measurement forces it, and if one is, weeks 6 and 7 get re-run before
anything ships.

---

# Results, and what the pre-registration caught

## Probe 1, the shipped loop. n=8 per email, 48 runs.

| id | usable tools | stop reasons | steps | repeats |
|---|---|---|---|---|
| 011 | 2 | `internal_sender` 8 | 1 | 0/8 |
| 007 | 3 | `decisive_malicious` 8 | 1 | 0/8 |
| 005 | 3 | `decisive_benign` 8 | 2 | 0/8 |
| 010 | 3 | `decisive_malicious` 8 | 2 | 0/8 |
| 004 | 2 | `tools_exhausted` 8 | 2 | 0/8 |
| 012 | 3 | `tools_exhausted` 8 | 3 | 0/8 |

**P1a confirmed: `step_cap` fired 0 of 48.** P1b: no repeat at any step
position, in any run. Every email landed on the stop reason the corpus designs
for it, 8 of 8. The loop is not broken. The cap is simply out of reach.

That also corrects the blind student's reading of cell 15. The seventeen
repeats they saw there are **forced**, not chosen: the uncapped loop drops the
`tools_left` test, so once three tools are spent every later step must repeat
one. Repeats begin at step 4 because that is the first step at which no
unused tool exists, which is one step after the capped loop has already closed.

## Probe 2, the candidate fix, and why it was thrown away

My proposed cell ran the student's own `run_loop()` at `max_steps=2` on 012.
It passed everything I pre-registered: `step_cap` 8 of 8, exactly 2 steps 8 of
8, and the 005 control came back `decisive_benign` 8 of 8 rather than
`step_cap`.

**It was still the wrong fix, and codex is why.** Two objections, both correct:

1. I called it deterministic by construction. It is not. `first_call()` passes
   the model's arguments through without validation and `run_tool()` honours
   them, so a model that names a different sender could get `internal` or
   `known_bad` back and end the run decisively. 8 of 8 is an empirical result,
   and I was about to write a proof onto a page.
2. Objective 5.1 says **a four-step cap**. Demonstrating a cap at two shows the
   `step < max_steps` test works; it does not show the four-step cap ending a
   run. In codex's words, it *"quietly substitutes a configurable two-step cap
   for a four-step cap"*. That is a redefinition of the objective, which is the
   failure this whole process exists to catch.

The 005 control was fragile for a third reason codex spotted: 005 is only
decisive through `check_urls`, so a run that happened to pick reputation then
recipient would return `step_cap` and the control would fail against correct
code.

## What shipped instead

Codex's design. A pre-written cell stands in for `ask_with_tools()` with a
short script inside `try/finally`, drives the student's own `run_loop()` at its
real `MAX_STEPS = 4`, and restores the real function afterwards. The script
asks for one non-decisive tool over and over on 012, with empty arguments so
`run_tool()` falls back to that email's own values.

Measured, in the notebook, three times:

    012  steps: 4  stop: step_cap  tokens: 0
       tools still unused:  ['check_urls', 'lookup_recipient']

    005  steps: 1  stop: decisive_benign  tokens: 0

Deterministic, because model choice is removed rather than hoped about. Zero
model calls. The 005 control fires differently under the same script and the
same loop, so the cell demonstrates the cap rather than demonstrating a script.

## Probe 3, the cost model. What the page claimed, and what it costs.

| | the page said | measured |
|---|---|---|
| first request | about 1,500 tokens | **1,776** |
| each finished step adds | roughly another 100 | **71 to 164, mean 126** |
| twenty-step run | its arithmetic implies 49,000 | **60,208** (+23%) |
| capped run on 012 | not stated | **5,852**, 3 steps, `tools_exhausted` |

**A correction to my own record.** I repeated the blind student's claim that
the reading predicts 20,500 and that 64,016 is "three times" it. Codex checked
the page's arithmetic: `20 x 1500 + 190 x 100 = 49,000`. The measured run is
about a quarter over, not triple. The student's figure and mine, 64,016 and
60,208, are two runs of the same thing.

Objective 5.3 asks the student to compare a capped run against an uncapped one.
Until now no number in the repository answered that. It is **10.3x**.

## A gate weakness found on the way

`run_notebook.py --expect-artifact` passes when *some cell printed the file
name*. It never opens the file. The week 5 solution run reported the artifact
written and no such file was on disk afterwards. Logged, not fixed here.
