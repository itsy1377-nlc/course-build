# Week 4 measurement, 2026-09-09

Everything here was run against the shipped stack: `granite-3b` on the LiteLLM
proxy, temperature 0.2, `reasoning_effort: "none"`, the same settings the
notebook sends. The rig is the week 4 solution notebook's own pre-written cells
plus its two reference TODOs, extracted whole, so the code under test is the
code students run.

Thresholds were written down first, in `prereg-claude.md`, before any probe
printed a row. Two of them failed. The failures are the useful part.

## The question

Objective **4.3, "Compare each email's verdict with tools against its verdict
without tools"**, is the at-risk objective. 4.1 and 4.2 are safe: a student
writes `run_tool()` and `tool_result_message()`, and cell 11 and cell 13 check
both against saved requests with no model involved.

Two ways 4.3 could be false:

- **H1** The model asks for the same tool on every email, so two of three
  branches never run live and email 018, the week's showcase, is judged on the
  half of the evidence that is clean.
- **H2** The verdict difference cell 14 displays is produced by the prompt
  difference between the two arms rather than by the tool result.

## Probe 1: which tool, and what decides it

`w4_choice.py`, 12 runs per email per condition, 216 calls,
`granite-3b-choice-12.json`.

Three conditions. The first two are shapes already in the notebook and they
differ by exactly one block, which makes them a natural experiment. The third
is the control.

| condition | what it is |
|---|---|
| bare | cell 8's shape: facts, body, tool inputs, `TOOL_TURN` |
| playbook | cell 14's shape: bare plus the triage playbook. **What ships.** |
| filler | bare plus 1,365 characters of neutral ticket-handling prose, matched to the playbook's length and saying nothing about senders, links or recipients |

Tool asked for, totalled over all six emails:

| condition | check_sender_reputation | check_urls | lookup_recipient |
|---|---|---|---|
| bare | 34 | 17 | 16 |
| playbook | **59** | 8 | 2 |
| filler | **66** | 5 | 1 |

**The control fires.** Filler concentrates the choice at least as hard as the
playbook does. So the cause is not anything the playbook says. Inserting about
1,365 characters of any prose between the facts block and the body collapses a
three-tool menu onto `check_sender_reputation` roughly seven times in eight.
Editing the playbook would have been the obvious fix and it would have been the
wrong one.

Per email, `check_urls` chosen:

| id | bare | playbook | filler |
|---|---|---|---|
| 003 | 4/12 | 2/12 | 0/12 |
| 008 | 2/12 | 0/12 | 0/12 |
| 009 | 0/12 | 0/12 | 0/12 |
| 017 | 0/9 | 0/10 | 0/12 |
| 018 | 11/11 | 6/11 | 5/12 |
| 019 | 0/11 | 0/12 | 0/12 |

**H1 as written is not confirmed.** On 018, the shipped condition asks for
`check_urls` 6 times in 11. The blind student's single run drew the sender
half on 018; that is an ordinary draw, not a systematic bias. But the weaker
claim holds and matters: in the shipped condition the model asks for
`lookup_recipient` twice in 69 calls, so one of three branches is effectively
never exercised by a live call.

**A second finding, not looked for, and corrected once.** The week 4 reading
prints a worked example of what cell 8 returns on email 017 and it names
`check_urls`. In the first run of this probe, cell 8's shape on 017 returned
`lookup_recipient` 9 times out of 9 with no tool call at all in the other 3 of
12, and an earlier draft of this file concluded from that single run that the
page's example "does not reproduce, 0 of 9."

**That was wrong.** A second run of the same probe returned `check_urls` **12
out of 12** on the same email in the same condition. Cell 8's tool on 017 is
bimodal between runs, not fixed and not absent. The page's example is therefore
not false; it is unreliable, which needs a different repair. The page must stop
naming a specific tool, because a student has a real chance of seeing any of
three.

| run | 017, cell 8's shape |
|---|---|
| 1 | `lookup_recipient` 9, no call 3 |
| 2 | `check_urls` 12 |

## Probe 2: what is the tool result actually worth

`w4_isolate.py`, 8 runs per arm per email, `granite-3b-isolate-8.json`.

Four arms, chosen so the confound decomposes. **A grounded** is exactly what
cell 14's "no tools" column shows. **B toolshape** is the with-tools prompt,
one turn, no tool offered. **C withheld** is the control: the whole two-turn
exchange, a tool call made and answered, but the tool message carries no fact.
**D real** is what ships.

| id | truth | A grounded | B toolshape | C withheld | D real |
|---|---|---|---|---|---|
| 003 | benign | malicious 8 | malicious 8 | benign 8 | benign 8 |
| 008 | malicious | malicious 8 | malicious 8 | malicious 7 | malicious 8 |
| 009 | malicious | malicious 8 | malicious 8 | malicious 8 | malicious 8 |
| 017 | benign | malicious 8 | malicious 6, benign 2 | malicious 4, benign 3 | benign 7 |
| 018 | malicious | malicious 8 | malicious 8 | malicious 5, benign 2 | benign 6, malicious 2 |
| 019 | benign | malicious 8 | malicious 8 | malicious 8 | malicious 8 |

| id | C vs D differ | D vs D differ (noise floor) |
|---|---|---|
| 003 | 0/8 | 0/8 |
| 008 | 0/8 | 0/8 |
| 009 | 0/8 | 0/8 |
| 017 | 3/8 | 0/8 |
| 018 | 4/8 | **5/8** |
| 019 | 0/8 | 0/8 |

**H2 confirmed.** Summed over the six emails, A differs from D on about 22 of
48 runs and C differs from D on 7. Most of what cell 14's table displays is not
the tool's fact.

**Email 003 is the sharp case.** It moves from malicious to benign 8 times out
of 8 — and it moves exactly as far when the tool message says *"no record
available"*. The notebook's table credits the tool, the written answer asks the
student to name the fact that did it, and there is no such fact.

**Corrected, on codex's objection.** An earlier draft of this file said "the
second turn does that, not the tool." That is more than the control supports.
`{"status": "no record available"}` is itself semantic evidence, and the C and D
arms drew independent first-turn samples, so turn count is not isolated. What
the control does establish is the thing that matters: **something in the
completed tool-shaped exchange other than the retrieved fact moves 003**, and
cell 14 may not credit the fact. Naming the exact cause would need a further
arm.

**My own threshold failed, and the control is why that is worth knowing.**
Pre-registration said a real tool effect needed C to differ from D on at least
6 runs in 8. **No email met that bar under free tool choice.** And 018, the one
that looked most dramatic, has a noise floor of 5 in 8: two identical runs of
the shipped path disagree with each other more often than the withheld control
disagrees with the real one. Read alone, 018 would have produced a confident
lesson built on a coin flip. That is the third week running that a control has
caught one.

## Probe 3: take the choice away

`w4_forced.py`, 8 runs per arm per email, `granite-3b-forced-8.json`. Same
two-turn exchange every time; the only thing that differs between arms is which
tool's record the tool message carries. This is the matched-pair design 4.3
needs and does not have.

| id | truth | withheld | reputation | urls | recipient |
|---|---|---|---|---|---|
| 003 | benign | benign 8 | benign 8 | **malicious 8** | benign 6, malicious 2 |
| 008 | malicious | malicious 8 | malicious 8 | malicious 8 | malicious 8 |
| 009 | malicious | malicious 8 | malicious 8 | malicious 8 | malicious 8 |
| 017 | benign | **malicious 6**, benign 2 | **benign 8** | **benign 8** | **malicious 8** |
| 018 | malicious | malicious 8 | **benign 8** | malicious 8 | malicious 8 |
| 019 | benign | malicious 8 | malicious 8 | malicious 8 | malicious 8 |

Once the tool is fixed the verdict stops wobbling: every cell is 8/8 or 6/8.
**018's instability was instability of tool choice, not of judgment.**

Four readings, and the first two are the week the course wanted:

1. **017 is a clean demonstration of 4.3.** With no fact the agent says
   malicious, which is wrong. The sender record makes it benign, 8 of 8. The
   link check makes it benign, 8 of 8. The recipient record leaves it
   malicious, 8 of 8. Three tools, three outcomes, one email, deterministic.
2. **018 is the counter-case, and it is the more useful lesson.** With no fact
   the agent is right. The sender record — *"known_good, property management
   customer"*, a true fact — makes it **wrong, 8 of 8**. The link check, which
   returns `blocklisted`, holds it right. The one tool a beginner reaches for
   first is the one that breaks it.
3. **Half the table is inert.** 008, 009 and 019 return the same verdict in all
   four arms. Nothing a student does to those three changes anything.
4. **019 is never right.** Ground truth is benign, `legit_internal`. Every arm
   says malicious, 8 of 8, including the arm with the known-good internal-hosts
   block. The week ships it as a comparison row and never says the agent cannot
   get it.

Probe 3 was designed after probe 2's threshold failed, so it is exploratory,
not confirmatory. Its effects are 8/8 and would clear any threshold worth
setting, but a fix built on it has to be re-run against thresholds fixed in
advance before it ships.

## Probe 4: the claim about tool replies

`w4_text.py`, raw content read straight off the endpoint,
`granite-3b-text-6.json`. This cannot be measured from inside the notebook:
`send_request()` overwrites empty content with a notice before anything sees it.

**68 of 71 replies that carried a tool call also carried answer text.**

**Three** places tell the student the opposite, all of them in the notebook:

- cell 8, unconditionally, after printing the text: *"One line above says the
  model sent no answer text"*
- cell 9: *"the answer text is empty ... You will see that line once per tool
  call in the full run."*
- cell 13's comment: *"A reply that carries a tool call carries no answer
  text."*

The blind student's report attributed a fourth instance to the reading page.
Checked: `grep "answer text" content/pages/w4-content.md` returns nothing. The
sentence they quoted is cell 8's printed output, not the page.

The claim was true when it was measured. `content/video/runs/w4.json` records
`answer_text: ""` on granite4.2:3b through ollama on 2026-09-05. The same model
through the proxy behaves differently, and nothing re-checked it.

## Probe 5: can that text be trusted

`w4_saydo.py`, `granite-3b-saydo-6.json`. If the course stops saying the slot is
empty, it has to know whether what lands there can be believed, because a
sentence naming a different tool than the call is worse in front of a beginner
than an empty slot.

**60 agree, 0 disagree**, over the readable sentences in 72 calls. The text says
*"I'll check the allowlist/blocklist status of the link host"* and the call is
`check_urls`. It announces the choice, and it is right every time.

## What the corpus already knew

`ground_truth.json` carries `tool_expectations` for all three tools on every
email, and an `expected_loop`. On 018 it records
`{"secure-doc-viewer.example": "blocklisted"}` and
`expected_loop.stop_reason: "decisive_malicious"` after two tools. Week 4 allows
exactly one — `TOOL_TURN` says *"Call exactly one tool"* — so the corpus's own
design for 018 needs a mechanism week 4 does not have and week 5 adds.

## One more, found while reading

Cell 14 calls `load_email(email_id)` without `known_names=KNOWN_NAMES`; week 3's
`compare_runs()` passes it. Checked directly against `parse_eml`, this changes
exactly one of the six: **009**, the CEO-impersonation BEC, has
`display_name_mismatch` **True** with the names and **False** without. Week 4
drops, for its own impersonation case, the fact week 3 exists to teach.

## Probe 6: the confirmatory run

`w4_confirm.py`, fresh runs, `granite-3b-confirm-8.json`. Thresholds C1 to C4
were written into `prereg-claude.md` before this printed a row, because probe 3
was designed after probe 2 failed and an exploratory result cannot license a
claim on a page.

| id | arm | required | got | |
|---|---|---|---|---|
| 017 | withheld | malicious ≥ 6/8 | malicious 4, **benign 4** | **FAIL** |
| 017 | reputation | benign ≥ 7/8 | benign 8 | pass |
| 017 | urls | benign ≥ 7/8 | benign 8 | pass |
| 017 | recipient | malicious ≥ 7/8 | malicious 8 | pass |
| 018 | withheld | malicious ≥ 7/8 | malicious 8 | pass |
| 018 | reputation | benign ≥ 7/8 | benign 8 | pass |
| 018 | urls | malicious ≥ 7/8 | malicious 8 | pass |
| 018 | recipient | malicious ≥ 7/8 | malicious 8 | pass |

**C1 fails. C2 passes.**

017's three tool arms are rock solid and identical to the exploratory run. What
moved is its **baseline**: with no fact at all, 017 came back malicious 6 of 8
in the first run and 4 of 8 in this one. So the sentence *"the agent said
malicious until the tool told it otherwise"* is not a claim this course may make
about 017, and C3 applies: any cell built on 017 has to print what it got rather
than assert what it will get.

This is the whole reason the confirmatory step exists. On the exploratory run
017 looked like the week's demonstration — a wrong answer that two of three
tools repair. One fresh run of the baseline showed that half of it was a coin
flip. Week 1 shipped exactly this mistake and it took a blind student to find it.

**018 passes on all four arms across two independent runs, 8 of 8 every time.**
It is the email that can carry an asserted demonstration, and the demonstration
it carries is the more useful one: with no fact the agent is right; a **true**
fact about the sender — `known_good`, "Property management customer" — makes it
wrong; the link check, `blocklisted`, holds it right.

**C4 passes, cleanly.** Passing `known_names=KNOWN_NAMES` into cell 14's
`load_email()` flips email 009's `display_name_mismatch` from False to True and
moves **no verdict on any of the six emails, 0 of 8 in every case**. It is a
silent correctness fix and can be made as one.

| id | mismatch without | mismatch with | verdict without | verdict with | moved |
|---|---|---|---|---|---|
| 003 | False | False | benign 8 | benign 8 | 0/8 |
| 008 | False | False | malicious 8 | malicious 8 | 0/8 |
| 009 | False | **True** | malicious 8 | malicious 8 | 0/8 |
| 017 | False | False | benign 8 | benign 8 | 0/8 |
| 018 | False | False | benign 8 | benign 8 | 0/8 |
| 019 | False | False | malicious 8 | malicious 8 | 0/8 |

## What the six probes leave standing

- **4.1 and 4.2 are safe.** The student writes both functions and cell 11 and
  cell 13 check them against saved requests with no model involved. Nothing
  measured here touches them.
- **4.3 as shipped is not demonstrated.** Its comparison is unattributable, the
  email that moves furthest moves without the tool, three of six emails move on
  nothing, and one is wrong in every arm.
- **4.3 is demonstrable, on 018, deterministically, when the choice is forced.**
- **Three claims printed to students are false on this stack**: the four "no
  answer text" statements, the reading's worked `check_urls` example for cell 8,
  and the "three saved requests" count in two places against cell 11's four.

## Probes 7 and 8: one withheld twin per tool, and its confirmation

Codex objected to probe 3, correctly: its arms vary the tool **name** and
**arguments** as well as the returned fact, so only the reputation arm is
matched against the withheld arm. `w4_pertool.py` pairs every tool with its own
withheld twin — same name, same arguments, the only difference being whether the
tool message carries the real record or `"no record available"`. Probe 7 is the
first run; probe 8 is a fresh one against C5 to C7, fixed in advance.

| id | tool | withheld run 1 | withheld run 2 | real run 1 | real run 2 |
|---|---|---|---|---|---|
| 018 | reputation | malicious 8 | malicious 8 | **benign 8** | **benign 8** |
| 018 | urls | malicious 8 | malicious 5, benign 3 | malicious 8 | malicious 8 |
| 018 | recipient | malicious 8 | malicious 8 | malicious 8 | malicious 8 |
| 017 | reputation | malicious 6, benign 2 | malicious 6, benign 2 | benign 8 | benign 8 |
| 017 | urls | **malicious 8** | **benign 8** | benign 8 | benign 8 |
| 017 | recipient | malicious 8 | malicious 8 | malicious 8 | malicious 8 |

**C5 fails. C6 passes. C7 fails on one of its two null arms.**

- **C5, 017 with `check_urls`:** required the withheld twin at malicious ≥ 7/8.
  Got **benign 8/8**, a complete reversal of run 1's malicious 8/8. 017 does not
  ship as a demonstration. **Codex's "do not promote 017" was right and my
  reading of probe 7 was wrong** — I had one run and treated it as a result.
- **C6, 018 with `check_sender_reputation`:** withheld malicious 8/8 in both
  runs, real benign 8/8 in both runs, pair differs 8/8 twice. **This is the
  week's one confirmed causal demonstration**, and it is fully matched: same
  tool name, same arguments, only the record differs.
- **C7:** 018 with `check_urls` moved 3/8 against an allowance of 1. 017 with
  `lookup_recipient` held at 0/8.

**The pattern under all of it, and it is the useful one.** Every *real record*
arm is 8/8 and identical across both runs — all six rows, no exceptions. Every
instability lives in the *withheld* arms. A real record pins the answer; "no
record available" leaves the model to wobble, and it wobbles differently from
run to run.

That has a direct consequence for the fix: **the withheld arm must not be
printed in a student-facing cell as a baseline**, because it is the unstable
one. It belongs here, in the measurement record, as the causal control. What a
student cell can honestly show is the three *real* tool results side by side,
which are deterministic:

| id | truth | reputation | urls | recipient |
|---|---|---|---|---|
| 018 | malicious | **benign** (wrong) | malicious | malicious |
| 017 | benign | benign | benign | **malicious** (wrong) |

Both rows reproduced exactly, twice, at 8/8 per cell.
