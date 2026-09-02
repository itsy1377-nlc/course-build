::: intro
An agent is a language model that has been given tools and permission to use
them. This page explains what that means, what the loop looks like, and why the
record of a run matters more than what the agent tells you.
:::

::: section | A model on its own cannot do anything
A language model reads text and writes text. That is all it does. It cannot send
mail, read a file, or change a record. Ask a plain model to email somebody and it
will write you a nice reply about emailing somebody. Nothing leaves the room.

An **agent** is that same model with two things added. First, a list of tools it
is allowed to call. Second, a program that actually runs the tool when the model
asks for it. That program is called the **loop**.
:::

::: section | The loop, one pass at a time
The loop is short. It repeats these steps until the model stops asking for tools.

1. Send the conversation and the tool list to the model.
2. The model replies. It either answers, or it asks to call a tool.
3. If it asked for a tool, run that tool.
4. Put the tool's result back into the conversation.
5. Go to step 1.

**Step 4 is where the security problems live.** Whatever the tool returns goes
straight into the model's next input. If a tool returns text somebody else wrote,
the model reads it. You will spend week 3 on exactly that.
:::

::: section | The model decides, and it decides from words
You do not tell the agent which tool to use. The model picks. It picks by reading
the name and the description you wrote for each tool.

That is worth sitting with. The thing choosing whether to send mail is choosing
based on a sentence you typed. Change the sentence and the choice can change.
Week 2 measures how much.
:::

::: callout note | This is not a bug
People expect a program to do the same thing every time. A model does not. Send
the same request twice and you can get two different runs. That is normal, and it
is the reason a single run never proves anything in this course.
:::

::: section | What the record holds
Every run in this course writes a **trace**. A trace is a file with one line per
thing that happened: what you asked, what the model decided, which tool ran, what
that tool returned, and the final answer.

The trace is the evidence. The agent's own summary is not.

| The agent says | The record shows | Which one counts |
|---|---|---|
| "I have sent that email." | No send in the trace | The record |
| "I could not find the file." | The file was read | The record |
| "I did not change anything." | A write in the trace | The record |

A model can say it did something it did not do. It can also do something it does
not mention. Neither is lying in any useful sense. It writes plausible text, and
plausible text is not a report.
:::

::: callout warning | The habit this course is built on
Never write that something happened because the agent said so. Point at the line
in the record. Every graded assignment in this course asks for that line, and an
answer without one earns no credit for the claim.
:::

::: section | Some doors do not close again
Look at any tool and ask one question: if this runs by mistake, can I undo it?

Reading a file is fine. Run it twice and nothing changes. Sending mail is not.
Once mail leaves, it has left. Deleting a record is not. Charging a card is not.

An action you cannot undo is called **irreversible**. Marking which of your tools
are irreversible is your first real security task, and you do it this week. It is
also the whole reason the rest of the course cares which tool the model picks.
:::

::: section | Scope, before any of it
This course teaches you to attack an agent. That skill is lawful on systems you
own and unlawful on systems you do not. There is no grey area in the middle.

You have three permitted targets: the practice target this course gives you, the
agent you build, and a model running on your own machine. Anything else is
outside scope. Read the Rules of Engagement page and pass the gate quiz before
you run this week's assignment.
:::

::: checkpoint | Check Yourself
1. What two things does a plain language model need before it becomes an agent?
2. In the loop, which step puts a tool's output in front of the model?
3. Your agent tells you it deleted nothing. Where do you look to check?
4. Name one irreversible tool and one that is not.

Answers: (1) a list of tools it may call, and a program that runs them. (2) Step
4. (3) The trace, at the line for that tool call. (4) Answers vary: sending mail
and deleting a record cannot be undone; reading a file can be repeated safely.
:::

::: sources | Sources
Written for this course. The loop described here is the one in the lab code you
run this week, and you can read that code yourself.
:::
