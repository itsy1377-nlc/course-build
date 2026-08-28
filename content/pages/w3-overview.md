::: intro
This week the direction flips. Until now your script called the model, and from
here the model calls your function.
:::

::: callout stop | The hardest week, and it is built so you cannot fall out
Four protections are already in place. Read them before you start.

| Protection | What it means |
|---|---|
| The checkpoint is pass or fail | A student whose own code will not run still passes, on time, with the grade intact |
| A working branch on day 18 | Your instructor publishes `agent-working` three days before the deadline, not on it |
| Reading capped at 45 minutes | The Annotated Skeleton page. Nothing else is assigned |
| Nothing else due day 21 needs working code | Only the checkpoint, and it has the fallback above |
:::

::: objectives
By the end of this week, you will be able to:

- 3.1. Describe the difference between a script that calls a model and a model
  that calls your function.
- 3.2. Explain what a JSON tool schema is, and what a model learns by reading
  one.
- 3.3. Apply try, except, a timeout, and a retry to code in the lab scaffold.
- 3.4. Walk through the agent loop in `agent/loop.py` and say what each part
  does.

These serve course outcomes O1 (scripting against a model API), O2 (extending
an agent with tools), and O6 (checking AI-written code).
:::

::: tasks
| Activity | Objectives | Due |
|---|---|---|
| Read the Week 3 content page | 3.1, 3.2 | Wednesday |
| Required reading: the Annotated Skeleton page, with the file open | 3.4 | Wednesday |
| Add error handling to the scaffold and get one tool call to run | 3.3 | Friday |
| Project 1 Checkpoint, pass/fail, 20 points | 3.2, 3.4 | Sunday 11:59 PM, day 21 |

The checkpoint is the only graded item this week. A thread called "Top 10 Week
3 Errors" is pinned on the Q and A board from day 15. Read it the moment
something breaks.
:::

::: callout time | About how long this takes
The content page: about 45 minutes.
The Annotated Skeleton reading: 45 minutes, and it is capped there.
Hands-on work in the lab: about 4 hours.
The checkpoint write-up: about 30 minutes.

That is about 6 hours of assigned work in total. This is the hardest week in
the course, and it is not the longest. Week 4 and Week 7 both assign more
hours.

If programming is new to you, the coding parts commonly take two to three
times as long. That wider range is normal, not a sign of falling behind.

Past 6 hours of lab work with the agent still not running? Use the
`agent-working` branch and submit the checkpoint.
:::

::: next
Week 4 takes the loop apart one step at a time. You trace it on paper, then you
design a tool of your own, which is Project 1.
:::
