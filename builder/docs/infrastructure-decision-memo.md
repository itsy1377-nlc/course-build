# Moving the labs to JupyterLite, LiteLLM and DeepInfra

**For:** the program manager and whoever owns the lab hosting
**Written:** 2026-09-06
**Status:** a decision memo, not a change. Nothing in the course has been
edited because of it.

The proposal is to run the labs on the remote lab machine rather than on a
local model server: JupyterLite for the notebooks, LiteLLM as the model proxy,
and a DeepInfra key giving Granite 4.2 3B and Granite 4.2 8B.

This is closer to production than what the course was built and measured
against, and that is the point of it. It is also the reason it needs recording:
**three things the course currently states as fact stop being true on that
infrastructure, and one design rule the build brief sets cannot be met by
JupyterLite at all.**

---

## 1. The short version

| Piece | Verdict |
|---|---|
| LiteLLM as the proxy | Take it. It closes two open items and costs nothing to adopt. |
| DeepInfra as the model host | Take it, and re-measure. Its API is wider than the one the course was built on. |
| Granite 4.2 8B alongside 3B | Worth having, and it invalidates the measurement the week 5 design rests on until it is redone. |
| JupyterLite for the notebooks | **Decide first.** It cannot meet the brief's key-handling rule, and it breaks the network call every notebook makes. |

---

## 2. LiteLLM: adopt it, and it fixes two things that are open today

The notebooks already speak the OpenAI chat completions shape, so pointing them
at LiteLLM is a change to one environment variable and nothing else.

Two open items close with it.

**The token budget policy becomes enforceable.** Today it is instructor
managed, and nothing stops a student spending. LiteLLM issues a virtual key per
student with a real budget attached.

**The five dollar per student figure becomes measurable.** The blueprint could
only express cost as a break-even price, because per-token cost was unknown.
One clean pass through all seven labs is about 388,000 tokens per student. So
the model has to cost under $12.89 per million tokens, or under $6.44 if every
lab is rerun once. With a real price and per-student logs, that stops being an
estimate.

A third thing improves. The configuration cell currently carries `MODEL_EXTRAS`
so it can send `reasoning_effort`. That cell is byte identical across all seven
lab notebooks and all seven instructor solutions, so every change to it is a
fourteen file edit that `lab/tools/check_chain.py` then has to police. If the
proxy owns the setting, that coupling goes away.

**One carve-out if the proxy enforces reasoning off.** Keep one path that can
still turn it on. `lab/eval/week5_loop_test.py` takes reasoning as a
per-configuration parameter, and that is how the course knows reasoning mode
costs 83 seconds and about 7,900 tokens for one triage against 4.1 seconds and
3,813 tokens with it off. That measurement is the whole justification for the
setting. Force it off on student keys; leave the measurement key alone.

---

## 3. What DeepInfra supports that the course says is impossible

DeepInfra's parameter list for Granite 4.2 3B is wider than the endpoint the
course was built against. Three entries matter.

### 3.1 `reasoning_effort` is supported, so the notebooks are already right

Allowed values are none, minimal, low, medium, high, xhigh and max. The
notebooks send `none` on every request. No change is needed.

One caution in DeepInfra's own wording: none "disables reasoning entirely **if
the model supports**". A setting that is accepted and quietly ignored is the
failure this build has hit four separate times. Section 6 says what to do about
it.

### 3.2 `tool_choice: required` exists, and three approved documents say it does not

`docs/phase1-blueprint/code-ledger.md` line 437 and
`docs/phase1-blueprint/week-04-spec.md` lines 109 and 330 all state that the
serving endpoint has no way to force a tool call.

That claim is the stated reason `triage_with_tools()` carries a prose fallback,
and why week 4's notebook spends cell 15 demonstrating it. The ledger notes the
fallback fired in none of nine tests, "but nothing prevents it, so students see
it as a normal path rather than a bug".

On DeepInfra the claim is false. `tool_choice` accepts none, auto and required.

**This does not make the fallback wrong.** Teaching a student to handle a model
that does not cooperate is sound, and a real system does need that branch. What
is wrong is the justification: the course explains a design choice with an
infrastructure limit that stops existing the moment the course moves. A student
or a reviewer who reads the DeepInfra docs will find the contradiction.

**Decision needed.** Either keep the fallback and rewrite the three passages to
justify it on its merits rather than on a limit, or use `tool_choice: required`
and remove the fallback path from week 4 entirely. The first is cheaper and
keeps the lesson. Neither is a code change to the tools themselves.

### 3.3 `response_format` json exists, and week 2 is built on malformed output

Week 2 teaches that the model sometimes returns something broken, that this is
normal rather than a sign the student did something wrong, and that handling it
is the work. The retry loop and `ATTEMPT_LOG` exist for that.

If the platform can constrain output to valid JSON, a sharp student will ask
why they are writing a retry at all.

The answer is already in the course and it is a good one. Week 2 also teaches
that a check on the shape cannot tell you the content is right. The week 2
walkthrough video shows exactly that: the schema passes and the category is
wrong. But the *malformed output* half of the motivation weakens.

**Decision needed.** Recommended: keep the retry, do not use `response_format`,
and add one sentence to the week 2 reading saying the constraint exists, that
this course does not use it, and why validation is still required. Hiding the
existence of the feature is the option that ages worst.

Neither `response_format` nor `tool_choice` is used anywhere in the course
today, so both of these are documentation decisions rather than code changes.

---

## 4. JupyterLite: the part that needs a decision before anything is built

### 4.1 It cannot meet the brief's key-handling rule

The build brief, lines 341 to 345, is explicit:

> the key is injected into each student's Jupyter environment as an environment
> variable by the hosting setup, and notebooks read it with os.environ. Students
> never type, paste, see, or screenshot a key.

JupyterLite runs Python in the browser through WebAssembly. There is no
server-side environment. Anything `os.environ` can read in that notebook, the
student can read, and it has already been delivered to their machine.

**LiteLLM makes this survivable, but it is still a change to a stated rule.**
If LiteLLM issues a per-student virtual key, the real DeepInfra key never
reaches a browser, and a leaked student key costs that student's budget rather
than the course's. The brief anticipates something like this: it provides a
documented fallback for the case where the hosting cannot inject per-student
environment variables, and requires that the fallback be written down.

**Decision needed, and it belongs to the program.** Accept per-student virtual
keys as the fallback the brief allows, and record it, or keep a server-side
Jupyter where the original rule holds.

### 4.2 Three things break mechanically

These are engineering costs, not policy questions, but they are not small.

1. **`import requests` does not work under Pyodide.** Every notebook's
   `send_request()` uses it. It would become `pyodide.http` or a fetch shim.
   That is a change to the one pre-written cell that is byte identical across
   fourteen files.
2. **The corpus has to reach a virtual filesystem.** The configuration cell
   walks `Path.cwd().parents` looking for `corpus/emails/teaching`. JupyterLite
   would need the 45 emails and the 7 data files bundled or fetched.
3. **`save_artifact()` writes the file a student uploads to Canvas.** In a
   browser that is virtual storage plus an explicit download step, and every
   assignment page currently says to attach the file.

None is unsolvable. Together they are a real piece of work on the exact cells
the course is most careful about.

---

## 5. Granite 4.2 8B, and what it costs to add

The week 5 design rests on a measurement, not an opinion. Across 294 agent runs
the 3B model chose the right first tool 25 times in 30 but produced the right
whole path only 15 times in 30. It picks well and stops badly. That is why the
stop condition lives in six lines the student writes, and it is the week's
lesson.

If 8B stops well, the lesson still stands as a design principle, but the course
can no longer say it was measured on the model students use.

**What has to be re-run, and it is a day of compute rather than a rewrite:**

| Artifact | Why |
|---|---|
| `lab/eval/week5_loop_test.py` | It takes `--models`. It is the measurement the week 5 design cites. |
| `lab/eval/week6_injection_test.py` | Built and never run. Week 6 is the differentiator week and its guardrails have never been measured on any model. |
| The token estimates per week | Week 6 makes about 112 model calls and week 7 about 65. Both figures were derived against the old endpoint. |
| `instructor/where-a-small-model-disappoints.md` | Every entry in it is a measured 3B behaviour. |

Offering both sizes is arguably better teaching than replacing one with the
other: the same lab, two models, and the student sees what capability buys.

---

## 6. The rule that should survive whatever is decided

**Assert what the server did, not what the request asked for.**

This build has shipped four separate defects of exactly one shape, each of
which passed every check while checking nothing:

- answer feedback written to a field Canvas accepts and stores nowhere
- a reasoning switch gated on a model name, which any hosted alias defeats
- a no-spoiler gate whose file patterns matched no files
- an assignment gate carrying a different course's identifier regex

Each was invisible because the thing being sent was never read back. Every item
in this memo has the same risk profile. A proxy that silently drops
`reasoning_effort`, a `models` fallback array that quietly serves a different
model, a `response_format` that is honoured on one model and not another: none
of them raises an error.

The observables already exist and cost nothing.

- The serving stack probe found Granite 4.2 returns its thinking in a separate
  `message.reasoning` field, and the week 2 notebook already prints **reasoning
  text length: 0**. That line reads the response. If a proxy stopped enforcing,
  the number goes non-zero and somebody sees it.
- DeepInfra's `models` fallback array reflects the model that actually served
  in the response's `model` field. If fallback fires, a student is measuring
  something other than what they think, and that field is the only place it
  shows.

Whatever is adopted, print what came back beside what was asked for.

---

## 7. Cost levers this infrastructure adds

Two are worth measuring, one is worth refusing.

**Prompt caching. Worth measuring, probably the largest lever.**
`prompt_cache_key` with a TTL is directly aimed at this course's shape. Week 6
makes about 112 calls and week 7 about 65, and every call resends the same
facts block, the same playbook and the same known-good host list. That prefix
is exactly what caching is for, and it lands on the five dollar figure.

**`service_tier: flex`. Measure with it, ship without it.** It is a discount
for lower priority work, and DeepInfra says a flex request may be retried or
timed out under load. A student waiting mid-lab is the wrong place to spend
that. Use it for the eval sweeps, which are unattended and rerunnable.

**`models` as an ordered fallback array. Useful, with the caveat in section 6.**
It would implement the documented Granite 4.1 fallback natively rather than by
an instructor changing a variable.

---

## 8. What is being asked for

| # | Decision | Who |
|---|---|---|
| 1 | Accept per-student virtual keys as the brief's documented key fallback, or keep a server-side Jupyter | Program |
| 2 | Keep week 4's prose fallback and rejustify it, or adopt `tool_choice: required` and remove it | Program, with the course author |
| 3 | Keep week 2's retry and name `response_format` without using it | Course author |
| 4 | Fund the JupyterLite port of the network cell, the corpus mount and the artifact download | Hosting |
| 5 | Re-run the week 5 and week 6 measurements on whichever models ship | Course author |

Nothing here blocks the course as it stands. It runs today on the endpoint it
was measured against. Everything above is the cost of moving it somewhere
better, stated before the move rather than discovered after it.
