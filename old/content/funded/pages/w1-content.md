::: intro
An agent is a language model that has been given tools and permission to use
them. This page explains the loop, the record every run writes, and why one of
your two tools is not like the other.
:::

::: section | A model on its own cannot do anything
A language model reads text and writes text. That is all it does. It cannot read
a file, send mail, or change a record. Ask a plain model to save a file and it
writes you a friendly reply about saving files. Nothing on disk changes.

An **agent** is that same model with two things added. First, a list of tools it
is allowed to call. Second, a program that runs the tool when the model asks for
it. That program is called the **loop**.
:::

::: section | Your tool is a function you can read
The notebook opens with a working function of four lines. It runs before you
touch it. You change one line, and that line decides what the tool gives back.

Then you add one line above it. That line is a **decorator**: it starts with an
at sign, and it registers the function as a tool. It reads the function's own
name, its arguments and its description, and builds the tool listing from those.
You never write that listing by hand.
:::

::: callout note | You are not writing code from a blank page
Every week in this course starts from working code. You edit it. Nothing here
asks you to invent a function, and nothing here grades typing.
:::

::: section | The loop, one pass at a time
The loop is short. It repeats these steps until the model stops asking for tools.

1. Send the conversation and the tool list to the model.
2. The model replies. It either answers, or it asks to call a tool.
3. If it asked for a tool, run that tool.
4. Put the tool's result back into the conversation.
5. Go to step 1.

**Step 4 is where the security problems live.** Whatever a tool gives back goes
straight into the model's next input. Week 4 is about exactly that.
:::

::: section | The model decides, and it decides from words
You do not tell the agent which tool to use. The model picks. It picks by reading
the name and the description you wrote for each tool.

That is worth sitting with. The thing choosing what runs is choosing from a
sentence you typed. Change the sentence and the choice can change. Week 2
measures how much.
:::

::: section | Two views of one run
Your run draws a **filmstrip**: one box per thing that happened, left to right in
time order. What you asked, what the model decided, what it called, what came
back, what it answered. A coloured edge marks an action, a result, or an error.

Under it sits a cell called `show_raw()`. That prints the same run as the file it
really is, one record per line, with line numbers.

The filmstrip is for looking. The file is for citing.
:::

::: callout warning | How to cite in this course
Name a file, a line number and a field inside that line. "Line 4, the arguments
field" is a citation. "The third box" is not. Every graded claim from this week
on needs the first kind. A claim without one earns no credit.
:::

::: section | The record is the evidence
A model can say it did something it did not do. It can also do something and
never mention it. Neither is lying in any useful sense. It writes text that
sounds right, and text that sounds right is not a report.

| The agent says | The record shows | Which one counts |
|---|---|---|
| "I saved that file." | No tool call at all | The record |
| "I could not read it." | A result came back | The record |
| "I changed nothing." | A write in the record | The record |
:::

::: section | Six breaks, on purpose
Once your tool works, you break it six ways. Each break is one small edit, and
each one changes something you can point at.

| The break | What to watch for |
|---|---|
| Delete the description | Whether the model still picks the tool |
| Describe a different function | Which tool it calls, and with what |
| Make it raise an error | What step 4 puts back in front of the model |
| Make it give back far too much | How much of the run is your own output |
| Cut the step limit to one | Where the run stops |
| Take the tool away | What the model does with nothing to call |

Two cells make this safe. The **reset cell** puts the known-good version back at
any point. The **check cell** reads your current setup and says in plain words
what is wrong, before the model is called at all.
:::

::: section | Some doors do not close again
Your second tool is supplied, and it writes a file. So ask one question of each
tool: if this runs by mistake, can I undo it?

Reading is fine. Run it twice and nothing changes. Writing a file is not. Once
the file is written, it is written. An action you cannot undo is called
**irreversible**.

For each of your two tools you write three fields:

1. Reversible: yes or no.
2. The reason, in one line.
3. What a person would need to see before approving it.

The third field is the hard one. It is also the one weeks 5 and 6 build on.
:::

::: section | Scope, before any of it
This course teaches you to attack an agent. That skill is lawful on systems you
own and unlawful on systems you do not. There is nothing in between.

You have three permitted targets: the practice target this course gives you, the
agent you build, and a model reached through the school gateway. Anything else is
out of scope. Read the Rules of Engagement page and pass the gate quiz before you
run this week's assignment.
:::

::: checkpoint | Check Yourself
1. What two things does a plain model need before it becomes an agent?
2. Which step of the loop puts a tool's output in front of the model?
3. Your agent says it wrote no file. Where do you look to check?
4. Which of your two tools is irreversible, and why?

Answers: (1) a list of tools it may call, and a program that runs them. (2) Step
4. (3) The raw record, at the line for that tool call. (4) The one that writes a
file. A write cannot be taken back, while a read can be repeated safely.
:::

::: sources | Sources
Written for this course. The loop, the decorator and the two cells described here
are the ones in the notebook you open this week, and you can read all of them.
:::
