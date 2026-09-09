::: intro
Until now your agent asked for one tool and answered. This week it can ask four times, picking the next tool from the result it just read. The hard part isn't the asking. It's knowing when to stop.

This page covers the loop, the rule that ends it, and the cap that catches the rest.

Give this page 40 minutes. Most is the two worked runs and the questions under them.
:::

::: video w5-walkthrough | What success looks like
A full week 5 run: six emails, six traces, and the uncapped run that costs many times more.
:::

::: section | One step is three actions
**A bounded loop is a loop that can't run forever, because a rule and a cap both end it.**

One step is three actions, in a fixed order.

1. The agent looks at what it has so far.
2. It decides which single tool it wants next.
3. Your code runs that tool and hands the result back.

Observe, decide, act. That's one **step**. Then the loop begins again.

Week 4 gave you one round. Week 5 lets your agent go around again.

It can't go around forever. `MAX_STEPS` is 4, and that number is the **step cap**. Three tools sit under a cap of four. A run asking for each once uses three steps, so the tools run out before the steps do.
:::

::: section | The stop condition is a rule in your code
Most runs finish well before the cap, because one result can settle the case.

**A stop condition is the rule that ends a run early.** In your notebook it's `decisive_stop()`, pre-written. Hand it a tool name, a result and the parsed email, and it hands back a reason or nothing.

Week 2 gave stop reason a different meaning: why the model stopped writing. Here it says why a run ended. There are five, and no sixth.

| Stop reason | What it means |
|---|---|
| `decisive_malicious` | A link host is on the block list, or the sender is known bad |
| `decisive_benign` | A trusted sender and a trusted link host agree |
| `internal_sender` | The mail never left the organization |
| `tools_exhausted` | Nothing settled it, and no usable tool was left |
| `step_cap` | Nothing settled it, and four steps went by with a tool untried |

The first three come from a settled case. The last two say it ran out of room.

The rule lives in your code, not in the model, and the course measured why. A model left to decide when to stop kept calling tools after it had its answer. It got the whole path right in well under half of those runs. With the rule in code, nearly every run ended right.

Those counts come from one set of tests, so read the direction, not the figures.
:::

::: section | The agent picks its next tool from what it just read
After each result the agent does one of two things. It answers, or it names one more tool. That choice comes from the result that just arrived, not from a sequence written in advance.

Say the reputation check returns `unknown` on a domain first seen the day the mail arrived. That settles nothing, so the agent asks for `check_urls` and looks at the link instead. Had it come back `known_bad`, your stop condition would have ended the run before the agent chose again.

So the model chooses. Your code decides whether anything is left to choose from, and a tool counts as left only while it has something to look at.
:::

::: section | A wrong second choice costs a step
Email 004 has no link, so `check_urls` never appears in the tools left for it.

A model can still ask for it. Your code returns an empty result, the step counts, and it taught nothing.

A step you can't use is a step you paid for. Your written answer asks which second tool your agent picked on 004.
:::

::: section | Why a runaway loop gets more expensive every pass
**A runaway loop is a loop that keeps calling the model with nothing new to learn.**

Cost is why it matters. Every request carries the whole conversation so far: instructions, facts, email, and every turn taken.

The first request is about 1,800 tokens. Each finished step adds another 70 to 165 tokens to every request after it.

So step twenty carries nineteen turns of history that step one didn't. You pay for 190 extra pieces, not 20. **The cost grows faster than the step count.**

Measured on this course's service, that run cost about 60,000 tokens. The capped run on the same email cost about 5,900. Ten times the price, for nothing new.

Your notebook runs one deliberately. It takes 012, removes the cap and the test for tools left, and stops hard at twenty steps.

Watch what it asks for. With the tools-left test gone, 012 runs out of new tools after three steps, then repeats one it already ran, seventeen times in twenty. That is the only place this course shows you a repeating model, and it is the case the cap exists for.
:::

::: section | The cap is a control, and a person owns it
The stop condition ends a run that got its answer. The cap ends one that never gets one.

The case it catches is the model asking again for tools it already used. Your code runs them again and every step counts.

Count it through. One repeat gives four steps with all three tools tried, so `out_of_room()` reads `tools_exhausted`. The cap ends a run only when four steps go by **and** a tool was never tried, which takes two wasted steps.

So it's the line you don't expect to touch. Your six runs won't reach it, and cell 15 fires it on purpose so you see it work. It's a threshold on how many times the agent may act, and it stops one bad run spending a week of tokens.

A control also needs an owner. At Pellgrave that's Devin Crowmarden, the security analyst. He sets the cap, reviews the traces, and turns the agent off when it works outside what it was built for.

Published guidance asks for exactly that: a way to stop a system acting outside its intended use, owned by a named person.

A cap nobody owns is a number in a file.
:::

::: section | A run that stops on the first result
A **trace** is the record of one run, one row per step. Your notebook prints one for every email. Email 011 is a reply between two Pellgrave employees.

| Step | Tool the agent asked for | What came back | What `decisive_stop()` returned |
|---|---|---|---|
| 1 | `check_sender_reputation` | status `internal` | `internal_sender` |

One step, and the loop returns with two tools never touched. The stop condition ended that run, not the counter.
:::

::: section | A run that spends every tool it has
Email 012 is a notice from a real customer on a domain nobody has seen before.

| Step | Tool the agent asked for | What came back | What `decisive_stop()` returned |
|---|---|---|---|
| 1 | `check_sender_reputation` | status `unknown`, first seen the day the mail arrived | nothing |
| 2 | `check_urls` | the one link host is on neither list | nothing |
| 3 | `lookup_recipient` | a service manager who handles no payments | nothing |

Three results, and nothing decisive in any of them. After step 3 no usable tool is left, so `out_of_room()` returns `tools_exhausted`. The cap never fired here.
:::

::: checkpoint | Check yourself
Four questions about the two runs above. The answer sits under each one.

1. Run one ended after a single step. Which stop reason ended it?

    `internal_sender`. The first result settled the case, so the loop returned immediately.

2. Run two ran all three tools. Which stop reason ended it, and why not `step_cap`?

    `tools_exhausted`. The cap is four and the run used three, so a tool ran out before a step did.

3. In run two, which step added nothing you could act on?

    Step 3. It named who received the mail, which settles no verdict and cost an entire request.

4. Neither run came near the cap. What's the cap for, then?

    For the run that meets no stop condition, usually the model asking again for a tool it already ran.
:::

::: section | Then open the lab
Run the **Week 5 sidebar notebook** first. It carries a counter, a cap and a rule that ends the ride early, which is your loop's shape on a bus route. The names differ, so sidebar code pasted into the lab won't run.

The lab then runs your loop over six emails, one for every loop shape. You write one function, `run_loop()`, and every line inside it calls a helper that works already. The notebook exports `week5_loop_trace.json`, and that file is what you turn in.
:::

::: sources | Sources
Both are free to read, with no account and no payment. Neither is assigned, so neither carries a link.

| Source | What it grounds here |
|---|---|
| *Excessive Agency*. OWASP Gen AI Security Project, Top 10 for Large Language Model Applications, 2026 edition | The loop that calls the model again with the result it just read, and the step cap as a threshold that halts a run. Creative Commons Attribution-ShareAlike 4.0 |
| *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST, AI 100-1, January 2023 | Why a named person owns the control that stops a system acting outside its intended use. A United States government publication, in the public domain |

Some of this page comes from the course, not from those documents. The five stop reasons, the six emails and the token numbers are ours, and the numbers are measured. Observe, decide and act is how this course draws the loop.
:::
