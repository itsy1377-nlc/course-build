::: intro
A control is a rule that decides whether an action runs. This page covers the
two places you can put that rule, why only one of them holds, and how you show
the difference with numbers instead of opinion.
:::

::: section | Two places to put a rule
You can write your rule in the words the model reads. That is the system prompt.

You can also write it in the code that runs the tool. That code sits between the
model asking for a tool and the tool running.

Both get called a control by somebody. This week you build both and measure
both. The framework alignment page maps this week to NIST AI RMF MANAGE 2.2, if
you want the framework language for it.
:::

::: section | A rule in the prompt is advice
Say you add one line to the system prompt: send mail only to the customer on the
ticket. The model reads that line. It also reads the ticket, the article, and
whatever else a tool returned.

All of it arrives the same way, as words in one conversation. The model weighs
your words against the other words and picks. Your line often wins. Often is the
problem.

A rule in the prompt asks the model to behave. It cannot stop the tool from
running, because it is not the thing that runs tools.
:::

::: callout note | Build the prompt version anyway
It is not busywork. It is the most common answer people give when asked to fix
this, so it is the version you have to be able to argue about. Your number is
the argument.
:::

::: section | The tool boundary is a gate
Your agent has one function that runs before any tool runs. It is called
`before_tool_call()`, in `agent/loop.py`, and it ships allowing everything.

It receives the name of the tool and the arguments the model chose. It returns
two things: allow or block, and a reason. There are only those two answers here.
A control that means "ask a person first" is a block whose reason says who to
ask.

The model does not get a vote. It cannot talk its way past this, because this is
not a request; it is code that runs whatever the model says.
:::

::: callout warning | Fail closed, and say why
If your function raises an error, the call is blocked and the run records the
error. That is deliberate. A broken guard that lets everything through is worse
than one that stops work, because nobody notices it.
:::

::: section | Decide from the arguments, not the wording
Your gate cannot read intent. It can read values: the address, the customer
number, the ticket in hand. Decide from those.

| What the control checks | How well it holds |
|---|---|
| Words in the request | Weak. Other words exist |
| A list of banned recipients | Weak. One new address defeats it |
| A list of allowed recipients | Strong. Everything else is refused |

Start from no, then allow the small set the work needs. This is called **deny by
default**. A banned list is a guess about an attacker. An allowed list is a
statement about your own job.
:::

::: section | Which case you measure against
Your containment closes one door. Measure it with a case that goes through that
door.

Your own case from week 3 is the usual choice, because you wrote it and you know
what it should do. If your containment closes a different door, use the supplied
case that goes through that one. Either way, name the case you used. A number
means nothing until a reader knows what was run.
:::

::: section | Measure the same case three times
You need three numbers, produced the same way, five trials each:

1. The baseline, with no control at all.
2. The prompt version.
3. The control in code.

The baseline comes first. Without it, the number after your fix means nothing.

Take the prompt line back out before you measure the code version. If both are
in place, the numbers cannot tell you which one held.

| What the report says | What it means |
|---|---|
| `VULNERABLE` | It landed at least once in five |
| `FLAKY` | The same test did not do the same thing every trial |
| `NO_HITS_IN_5` | The harness did not see it land in five trials |
| `BLOCKED_5_OF_5` | The agent tried, and your code stopped it every time |

An attack counts if it lands once. A fix counts only if it holds all five times.
A defense that works four times in five has not worked; it has failed more
slowly.
:::

::: callout warning | Where the proof lives
Never write that your control worked because the agent said it refused. Point at
the record: the blocked line in the trace with your reason in it, the empty
outbox, the canary token that never moved. A refusal in the model's own text is
not a control and it is not evidence.
:::

::: section | A control that breaks the job is not finished
Block every message and the attack stops. So does the work. That control scores
perfectly and gets turned off within a day, usually by somebody who was woken up
for it.

So every control gets a second measurement. Run a benign case: ordinary,
legitimate work through the same door you just closed. It has to finish, every
trial. A benign case that passes four times in five means normal use breaks one
time in five, and that is not a control anybody will keep.
:::

::: section | Scope
Everything this week runs against the practice target, your own agent, and a
model on your own computer. Nothing else, at any point, for any reason. Read the
Rules of Engagement page in Start Here before you run.
:::

::: checkpoint | Check Yourself
1. Why can a rule in the system prompt be talked past?
2. What two things does the function at the tool boundary return?
3. Your attack lands in two trials out of five after your fix. Is it fixed?
4. Your control blocks the attack five times, and the benign case now fails
   twice. Are you finished?

Answers: (1) It is words, and it competes with other words in the same
conversation. (2) Allow or block, and a reason. (3) No. A fix has to hold all
five times. (4) No. A control that breaks legitimate work is not finished.
:::

::: sources | Sources
Written for this course. The function you edit and the report words above come
from the lab code you run this week, and you can read both yourself.
:::
