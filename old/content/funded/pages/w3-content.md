::: intro
A tool tells the model three things about itself: its name, what it does, and
what it takes. The model believes all three. This page is about what happens
when one of them is true and incomplete.
:::

::: section | The model reads a card, not the code
Your agent never sees a tool's source. It sees a card with three fields.

| Field | What it holds |
|---|---|
| `name` | What the tool is called |
| `description` | A sentence saying what it does |
| `inputSchema` | The arguments it takes, and their types |

That card is the whole basis for the model's choice. Week 2 measured how much
one word in `description` moves that choice. This week asks a harder question.
What if the sentence is true, and the code does more than the sentence says?
:::

::: section | MCP, and where those field names come from
Those field names are not ours. They come from MCP, the Model Context Protocol.
MCP is a published standard for how a program tells a model what tools exist.
Before it, every framework named these fields its own way. MCP settled on this
manifest shape, and the cards you read this week use it.

You are reading tool manifests over a local transport inside the sandbox. You
are not running a server, and you should not later say that you did. The
failure you find this week has a name. MITRE ATLAS release 2026.07 calls it AI
Agent Tool Poisoning, AML.T0110. The description is the attack. The code is only
where it hides.
:::

::: section | You specify the effect, you do not write it
You are not writing Python this week. You fill in three things.

1. Which effect, from the menu of eight below.
2. Its parameters, which are bounded numbers and short text.
3. One sentence of `description` that is true and hides the effect.

A generator turns that record into a real Python tool. The generated code is
what runs, and it is what three classmates receive. Nothing you type is ever run
as code, which is why this exercise is safe to do at all.

Your code will not look like anybody else's. No comment in it says which effect
it is.
:::

::: section | The menu of eight
Every student picks from this list. Knowing the list does not give you the
answer. It tells you what the answer could be.

| # | The effect | Where it shows |
|---|---|---|
| 1 | Adds text to the result, addressed to the model rather than to you | The result card |
| 2 | Returns a wrong value on one call in three | Result cards compared across probes |
| 3 | Fails on its third call | The probe where the card turns red |
| 4 | Waits a fixed time before returning | The duration on the card |
| 5 | Returns far more than it needs to | The context view, as a block that swells |
| 6 | Counts its own calls and changes after the third | Behaviour that differs by position |
| 7 | Adds a line to a fixed log file on every call | The workspace diff |
| 8 | Copies its argument into a fixed file | The workspace diff |
:::

::: section | The sentence is the half you write
The generator writes the code. You write the description, and that is the half
that does the work.

A description that lies is easy to catch. A classmate reads the code, sees a
file being written, then reads a card that never mentions files. That takes a
minute.

A description that is true and narrow is much harder. "Looks up a customer by
id and returns the record" is true of a tool that also appends a line to a log.
It says nothing false. It just stops early. Aim for that one.
:::

::: section | Four places to look, and none of them is the description
You get forty five minutes with three tools and no labels. Use all four
surfaces, because no single one covers the menu.

1. **The code.** Read it. A line reading `if self._calls > 2: raise
   RuntimeError(...)` means the tool dies on its third use.
2. **Direct probes.** Call the tool yourself, with no model in the way. Twelve
   calls at least.
3. **The filmstrip.** Run your agent with the tool and watch the cards.
4. **The workspace diff.** Two of the eight effects write files. Six do not.
:::

::: section | How to probe a tool you did not write
A probe is one call you make on purpose, with a result you write down.

1. Call it twelve times with the same argument. Count the different answers.
2. Call it with a short argument, then a long one. Compare the result sizes.
3. Call it and watch the time on the card.
4. Check the workspace diff after every batch, not once at the end.

The same argument twelve times finds effects 2, 3 and 6. Reading the returned
text closely finds 1. Changing the argument finds 5 and 8. The clock finds 4.
The diff finds 7 and 8. Reading the code can find any of them.
:::

::: callout note | Why twelve probes and not three
Effect 2 is wrong on one call in three. Call it three times and three good
answers are common. Call it twelve times and that fault is hard to miss. Small
samples are how a real fault gets reported as clean.
:::

::: callout warning | Cite the record, not the feeling
"The tool seemed slow" is not evidence. Open the raw view beside the filmstrip.
It prints the run's records with stable line numbers. Cite the file, the line
and the field. Every claim in your three reports needs one.
:::

::: section | What a finished claim looks like
Each of your three reports makes one claim. This is the shape it should take.

Weak: "Tool B seems to break sometimes."

Strong: "Tool B fails on its third call. In all four probe runs, calls one and
two returned normally and call three returned an error. The raw view line for
that third call carries the error in its result field, and it is attached."

The strong version names the effect, says what pattern supports it, and points
at something a grader can open. The third sentence is the one students leave
out, and it is the one carrying the citation marks.
:::

::: section | Which of these would you let run unattended
Ask the week 1 question again, about somebody else's tool this time. If this
runs by mistake, can I undo it?

A wrong value is annoying. You call the tool again and nothing is worse. A tool
that writes on every call has already left something behind, and the next call
leaves another. Six of the eight effects change nothing. Two of them do, and
those two are the reason your report ends with a recommendation.
:::

::: section | Why this matters outside this room
Most tools an agent uses were written by somebody else. They arrive with a
package, a vendor, or a shared internal repository. The card arrives with them.

Almost nobody reads the code behind it. That is the honest state of the
practice, and it is the same reason a poisoned dependency works. Your defence is
not trust. It is the four surfaces above, used on a tool you did not write.
:::

::: scope | Authorization and Scope
A classmate's tool runs inside the supplied sandbox, against your own agent, and
nowhere else. Your permitted targets do not change: the practice target this
course supplies, the agent you built, and the school gateway. Never a commercial
AI service, and never a system you do not own. Read the Rules of Engagement page
in Start Here.
:::

::: checkpoint | Check Yourself
1. Which three fields does the model read before it picks a tool?
2. A tool card says "reads a customer record". The code reads it and writes a
   line to a file. Is the card false?
3. You probe a tool four times and get four good answers. What have you shown?
4. Where does the raw view help that the filmstrip does not?

Answers: (1) `name`, `description` and `inputSchema`. (2) Not exactly, and that
is the point. It is true and it is incomplete, which is what poisoning looks
like. (3) Very little. One effect is wrong on one call in three, and four good
answers happen often. (4) It gives you a file, a line and a field to cite.
:::

::: sources | Sources
Written for this course. The field names come from the manifest shape your
notebook renders, and the menu of eight is the one your specification cell
accepts.
:::
