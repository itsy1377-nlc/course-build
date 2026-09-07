::: intro
Last week you ran the agent once. This week you run it ten times and compare
them. This page explains why runs differ, what to compare them on, and what a set
of five runs can honestly tell you.
:::

::: section | Why the same request can give a different run
A model writes one word at a time. At each step several words would fit, and it
picks one of them. Pick a different word early and the sentence goes somewhere
else.

In an agent that matters more than it would in a chat window. One of those picks
is which tool to call. A different pick at step two changes every step after it.
:::

::: section | Run, trial, set
Three words, used the same way for the rest of the course.

| Word | What it means |
|---|---|
| Run | One pass of the agent, from your request to its final answer, with one trace |
| Trial | One run inside a group you are comparing |
| Set | The group itself, which is five runs in this course |

A run becomes a trial when you plan to compare it. Nothing about the run changes.
What changes is what you are going to do with it.
:::

::: section | Compare on things you can count
Reading two traces side by side and forming an impression is slow, and two people
doing it get two answers. Instead, pick features you can read off every trace and
write down.

Four that work well this week:

1. How many tool calls the run made.
2. Which tools it called, in order.
3. Whether a tool you name appeared at all.
4. Whether the run reached a final answer.

Each one is a number, a short list, or a yes or no. **That is what makes a
comparison table possible**, and a table is something your reader can check
against your traces.
:::

::: callout note | The final answer is the weakest feature
Two runs can print nearly the same reply and have done different things to get
there. Compare the tool calls first. The wording of the reply is the last thing
to look at, and on its own it settles nothing.
:::

::: section | Read down the columns, not across the rows
Put one row per run in your table, and one column per feature, with the run
number first. Then read each column from top to bottom instead of each row from
left to right.

A column where every row matches is a part that held. A column where the rows
differ is a part that varied. Write down both. A part that held across five runs
is a result, not the absence of one.
:::

::: section | Five is a small number, so say five
Report what you saw as a count out of the trials you ran. "The agent called the
lookup tool in 4 of 5 runs" is a sentence somebody else can check against your
traces. "The agent usually looks things up" is not.

The count carries two limits with it, and both matter for the rest of the course.

| What you saw | What it does not mean |
|---|---|
| 0 of 5 | It never happens |
| 5 of 5 | It always happens |

A thing that did not happen in five runs can still happen in the sixth. That is
not a reason to stop counting. It is the reason you say how many trials the count
came from, every single time.
:::

::: section | This is why the course runs five trials
If one run settled a question, week 3 would be one attempt and a verdict. It is
not, and now you can say why in your own words.

From here on, the number of trials belongs in the sentence with the result. A
claim without it is not exactly wrong. It is unreadable, because nobody can tell
how much weight to give it.
:::

::: section | Change one thing at a time
The second half of this week sends five different requests. Only the request
changes. Same target, same agent, same model, same settings.

Change two things at once and you cannot say which one caused the difference you
see. Holding everything else still is what lets you name a cause, and it is most
of what makes a test worth running.
:::

::: section | Counting by hand does not scale
Ten traces is already tedious to count by hand, and later weeks ask you for many
more than ten. This course supplies a short script that reads a trace and reports
how many tool calls it holds.

Read it before you run it, and answer two questions about it: what does this
read, and what does it change. Then make the one-line change the assignment asks
for, so it reports across a whole folder instead of one file.

You are not asked to write that script. You are asked to be able to say what it
does.
:::

::: callout note | A broken run is not a trial
Sometimes a run stops before it reaches the model, because the target was not
running or the connection failed. That is a broken run, not a result.

Do not count it as one of your five. Note that it happened, say why, and run
another. Counting a broken run as a quiet one would tell your reader the agent
did nothing, which is not what happened.
:::

::: callout warning | Do not ask the agent whether it did the same thing twice
It cannot tell you. Each run starts fresh, so it has no record of the other four.
A model asked about its own behavior produces plausible text about it, and
plausible text is not a measurement. Your evidence is the ten traces and the
counts you take from them.
:::

::: checkpoint | Check Yourself
1. Why can two runs of the same request end differently?
2. Name two features of a run you can count.
3. Your five runs all called the same three tools in the same order. Is that a
   result?
4. A classmate writes: "the agent almost always looks up the customer first."
   What is missing?
5. You want to know whether a longer request changes anything, so you also switch
   models. What have you given up?

Answers:

1. The model picks among several words that would fit. One of those picks is
   which tool to call.
2. Answers vary: the number of tool calls, the tools in order, whether a named
   tool appeared, whether the run finished.
3. Yes. A part that held across five trials is a result. You report it as 5 of 5.
4. The count, and the number of trials it came from.
5. The ability to say which of the two changes caused the difference.
:::

::: sources | Sources
Written for this course. Every number in your write-up comes from your own
traces, which you keep and can be asked for.
:::
