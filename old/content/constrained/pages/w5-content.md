::: intro
A detector fired, and its message is short: mail left the company. That message
is a claim. A claim is where an investigation starts, not where it ends. This
page is about turning that claim into a call you can defend.
:::

::: section | The alert says less than it sounds like
Read the alert again and notice how narrow it is. It says mail left the company.
It does not say who received the mail. It does not say what was in it. It does
not say whether anyone was harmed.

A detector answers one narrow question, and it answers fast. Your question is
wider: **was this an incident?** The work sits between the two.
:::

::: section | What your case pack holds
The pack is your evidence. It was preserved from a real run, so every record in
it can be opened and read.

| What it is | What it can tell you |
|---|---|
| Two agent traces | What the agent decided, and which tools ran |
| An audit log export | Which record was touched, by whom, and when |
| Three preserved outbox messages | Who a message went to, and what it said |
| An analyst note | What one person concluded, working fast |
| A manifest | Which of these the assistant is allowed to open |

Not every student has the same pack. Comparing answers with a classmate will not
help you, because their case may not be your case.
:::

::: section | You decide what the assistant can reach
The assistant you use this week has one tool. It reads files, and only the files
the manifest names. It cannot write. It cannot send. It cannot open anything
outside the pack.

That is not a limit of the exercise. That is you doing week 1's job from the
other side. In week 1 you listed what an agent could reach. This week you set
it.

Ask the same question you asked then: if this tool ran by mistake, could I undo
it? Reading a file can be repeated with no effect, which is why read access is
the whole grant.
:::

::: section | Ask for a timeline, with a record on every row
Do not ask the assistant what happened. Ask for a timeline in four columns.

| Column | What goes in it |
|---|---|
| Claim | One thing the assistant says happened |
| Time | When the record says it happened |
| Actor | Who or what did it |
| Record | The file and the numbered line it came from |

The last column is the one that matters. A row with no record is not evidence.
It is plausible text, and the assistant will write plausible text all day.
**A claim you cannot open is a claim you cannot use.**
:::

::: section | Check every row yourself
Now open each record the timeline names and read the line it points at. Every
row then gets one of three marks.

| Mark | What it means |
|---|---|
| Accepted | You opened the record and it says what the row says |
| Corrected | The record supports part of the row, so you rewrite the rest |
| Rejected | The record does not support the row, or there is no record |

Do this for every row, including the dull ones. An assistant that gets nine rows
right and one row wrong is harder to catch than one that gets all ten wrong,
because the nine teach you to stop looking.
:::

::: callout warning | The sentence that fails this assignment
"The assistant confirmed the agent read the ticket first." That cites the
assistant. Write this instead: "Trace line 7 shows the ticket reader ran before
any other tool." That cites the record, and a stranger can open it and see the
same thing.
:::

::: section | The note in the pack is a claim too
Your pack holds a note written by an analyst working under time pressure. It
reads like a conclusion. Treat it exactly the way you treat a row from the
assistant: open the record, or reject the line.

A confident sentence from a person and a confident sentence from a model fail
the same test. Neither one is evidence. The record is.
:::

::: section | Name what your evidence does not settle
Some questions the pack cannot answer. Saying so is part of the call, not a gap
in it.

- **Intent.** A record shows an action. It does not show why anyone took it.
- **Harm.** You can see that a message was sent. Whether it hurt anyone is
  outside the pack.
- **Severity.** A severity rating needs impact, scope, and how likely this is to
  happen again. The pack holds none of the three.

You are not asked for severity this week. You are asked what the records
support, and for the sentence that says where they stop.
:::

::: section | The call, and what you would do about it
The handover asks four things: was this an incident, what in the pack decides
it, what did the assistant get wrong, and what would you do about it.

Answer the first with a yes or a no. Not "possibly". An analyst who will not
decide has handed the decision to the next reader, and that reader has less
evidence than you.

**Your call is what is graded, not the number of citations.** A call you reach
honestly from records you checked earns full marks, even if the pack was going
to end somewhere else. A call with nothing under it does not.
:::

::: section | Your last answer is next week's build
The fourth question asks what you would do about it. Answer it with one control
at the agent's tool boundary: one thing that must be true before a tool runs.

Write it in a single sentence somebody could build. You build it yourself in
week 6, so a vague answer costs you twice.
:::

::: checkpoint | Check Yourself
1. The alert says mail left the company. Name one thing it does not say.
2. What are the four columns your timeline needs?
3. A row names no record. What mark does it get?
4. Why does the assistant get read access and nothing else?
5. Your pack shows that a message was sent. Can you say from the pack whether
   anyone was harmed?

Answers: (1) Answers vary: who received it, what was in it, or whether anyone
was harmed. (2) Claim, time, actor, and record. (3) Rejected. A claim you cannot
open is not evidence. (4) Reading can be repeated with no effect, and the work
needs nothing more. (5) No. Harm is outside the pack, and saying so is part of
the call.
:::

::: sources | Sources
Written for this course. The case pack was preserved from a real run of the lab
you have used since week 1, so you can open every record it names.
:::
