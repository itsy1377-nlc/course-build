::: intro
Your agent picks a tool by reading a sentence you wrote. It cannot see the code
behind that sentence. This page is about how much the sentence decides, and how
you measure it without fooling yourself.
:::

::: section | The blindfold belongs to the model
When your agent decides which tool to call, it has three things.

- The tool's name.
- The description you wrote for it.
- The input schema, which lists the fields the tool takes.

That is the whole list. The body of the function is never sent. The model has
not run it and cannot run it. It is choosing with a blindfold on.

So a description is not documentation. **It is the control surface.** Whoever
writes it steers the agent.
:::

::: section | Two tools, one difference
The notebook gives you two tools this week. Both run the same four lines of
code. Both take the same input. They are named `lookup_a` and `lookup_b`, so the
names tell the model nothing. Only the descriptions differ.

That is a controlled comparison. One thing differs, so anything that changes is
down to that one thing.

Keep it that way. If you change two words at once and the split moves, you
cannot say which word moved it.
:::

::: callout note | One run is an anecdote
Send the same request twice and you can get two different choices. Nothing is
broken. A model's pick is not fixed, so one run cannot tell you what a
description does. It tells you what happened once.
:::

::: section | The grid
`run_trials(30)` sends the same request thirty times and fills in thirty
squares. One square per trial, coloured by what the agent did.

| Square | What it means |
|---|---|
| A | The agent called `lookup_a` |
| B | The agent called `lookup_b` |
| Neither | It answered with no tool call |
| Errored | The trial did not finish |

An errored trial is not a result. Re-run it, and write down how many re-runs you
needed. A grid of thirty means thirty finished trials, not thirty attempts.
:::

::: section | Why thirty and not five
Five trials cannot rule much out. Say an edit really works one time in five. Run
it five times and you can still see nothing at all, and that happens about one
run in three. You would report no effect, and you would be wrong.

Thirty is the floor in this course. It is not a magic number and it is not
enough for a small effect. It is enough to stop you calling a coin fair after
two flips.
:::

::: section | The grid that does not move
Some edits shift the split. Some change nothing you can see. Both are results,
and this week pays the same for each.

What a still grid supports is narrow, and saying it exactly is the skill:

| Claim | Supported? |
|---|---|
| This edit did not clearly move the split in thirty trials, on this model, with this request | Yes |
| This edit has no effect | No |
| Wording does not matter | No |

Write the first one. Never write the other two. A test that finds nothing has
ruled out a large effect, not every effect.
:::

::: section | What the model was actually sent
The input view shows the real thing sent to the model, as stacked blocks with a
token count on each. A **token** is a chunk of text, and it is how a model
counts what it reads. It is not the gateway token you log in with.

Each block is one part of the input: the system prompt, both tool descriptions,
your request, and every tool result so far.

Two things become obvious once you look. Your descriptions are in the input on
every single call, so they are paid for every time. And the input grows as the
run goes on, because results keep getting added to it.
:::

::: callout tip | Tokens are the meter
Your gateway budget is small on purpose. The token count on each block is where
that budget goes. A long description is a real cost, charged once per call, and
a run with ten calls pays for it ten times.
:::

::: section | The blindfold checkbox
Click a decision card on the filmstrip and tick the blindfold box. Everything
later in the run greys out. What stays lit is what the agent had been told when
it made that choice.

Use it before you explain any choice. Many wrong explanations come from
crediting a model with something it had not been shown yet.

One honest limit. The box greys by position, so it shows what had arrived in the
conversation by that step. It does not show you what never entered the
conversation at all.
:::

::: callout warning | Do not ask the model why it chose
You can ask your agent why it picked a tool. It will answer, and the answer will
read well. That answer is text it produced, not a record of what happened.

Your evidence is the raw record of the trial: the file, the line number, and the
field naming the tool that ran. `show_raw()` prints those lines with stable
numbers. Cite that, every time.
:::

::: scope | Authorization and Scope
This week you steer a model on purpose. That is the first half of an attack you
meet in week 3, so do it only where you are allowed.

You have three permitted targets: the practice target this course gives you, the
agent you build, and the school gateway with the token issued to you. A
commercial AI service is never a permitted target. Read the Rules of Engagement
page in Start Here.
:::

::: checkpoint | Check Yourself
1. Name the three things the model has when it picks a tool.
2. You changed a word and the split went from 20 and 10 to 19 and 11. What may
   you claim?
3. Four of your thirty-four trials errored. How many results do you have?
4. Where do you look to see what the agent knew before a decision?
5. Your agent says it picked `lookup_b` because it was faster. Is that evidence?

Answers: (1) the name, the description, and the input schema. (2) That this edit
did not clearly move the split in thirty trials on this model. (3) Thirty. The
four that errored are not results. (4) The filmstrip with the blindfold box ticked
on that decision card. (5) No. It is text the model wrote. Cite the raw record.
:::

::: sources | Sources
Written for this course. The tools, the grid and the input view described here
are the ones in your week 2 notebook, and you can read every line of them.
:::
