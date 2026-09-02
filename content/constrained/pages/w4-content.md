::: intro
Week 3 asked whether hidden text could steer your agent. This week asks a
plainer question: what does it do when somebody simply asks? Permission is the
subject, and the audit log is where you look.
:::

::: section | Nobody has to trick it
There are two ways an agent ends up doing something it should not.

In the first, someone hides an instruction where the agent will read it. That is
week 3, and it takes effort.

In the second, a coworker asks politely on a normal day, and the agent does it.
No hidden text. No effort. This one is far more common, and it gets far less
notice.
:::

::: section | You granted the permission before the request arrived
Here is the part people miss. The moment you put a tool in the agent's list, the
permission is granted. The agent does not come back and ask you at the time.

The model reads the tool list, picks one, and the loop runs it. So the useful
question is not "will it behave itself today". The question is **what did I
already allow**.

Your week 1 tool inventory is the answer sheet for that question. Open it again
before you run anything this week.
:::

::: section | A sentence is not a control
You can write "always ask me before sending mail" in the agent's system prompt.
That is worth doing. It is not a control.

A control is something that happens whether the model cooperates or not.

| What you write | Where it lives | What it does |
|---|---|---|
| "Ask me first", in the prompt | Words the model reads | Changes what the model tends to do |
| A check before the tool runs | Code in the loop | Decides whether the call happens at all |

You build the second kind in week 6. This week you measure what is there now,
which is the honest way to start.
:::

::: section | Too much reach has a name
**Excessive agency** is the name for an agent that can do more than its job
needs. It is one of the selected OWASP risks this course covers, from the 2026
release. It has three shapes:

1. Too many tools, so the agent can reach things the work never touches.
2. One tool that reaches too far, such as mail that can go to any address.
3. Nothing between deciding and doing, for an action nobody can take back.

Notice that none of the three requires an attacker.
:::

::: callout note | The dull request is the one to watch
Nothing you send this week is clever. That is the point. If an ordinary request
can reach outside the company, an attacker never needed a clever one.
:::

::: section | What an audit log holds
The practice target writes a row for every request that matters. Each row has
five fields.

| Field | What it holds |
|---|---|
| Time | When the request arrived |
| Actor | Who the caller said it was |
| Action | What was asked for |
| Detail | Which ticket, or which customer |
| Outcome | What came back |

Read the actor line again. It records who the caller **said** it was. Hold on to
that while you read your own rows.
:::

::: section | A record is not a lock
Two jobs get mixed up all the time. Telling them apart is most of this week.

**Accountability** is writing down who did something. **Authorization** is
deciding who is allowed to do it.

A log gives you the first. Only a check gives you the second. A system can
record an action perfectly and still let anyone take it. When you read your
rows, ask which of the two you are looking at.
:::

::: section | Reading across two requests
One row on its own says very little. Rows read together say more. What did this
account touch? In what order? Was any of it part of the work it was doing?

That last question is the one the log cannot answer by itself. An audit row
holds no reason. You bring the reason, because you know which tickets you
worked. That is why this week has two requests instead of one.
:::

::: section | The evidence pack, in three parts
An evidence pack is how you report a finding in this course. It is short.

| Part | What goes in it |
|---|---|
| The claim | One sentence saying what happened |
| The record | The outbox file or the audit row, copied exactly |
| The limit | One sentence on what this does not settle |

The third part is the one students skip and the one graders read closest.
Naming a real limit is a skill, and it is worth points every week from here.
:::

::: callout warning | What is not evidence
The agent's reply is not evidence. "It told me it sent the note" is a sentence
about the reply, not about the world. The file in the outbox is evidence. The
audit row is evidence. When a reply and a record disagree, the record decides
and you report the record.
:::

::: scope | Authorization and Scope
Everything on this page is done against the practice target this course gives
you. Use your own agent and a model on your own computer. Never a commercial AI
service, and never a system you do not own. The requests this week are polite
and ordinary. That changes nothing about where you may send them. See the Rules
of Engagement page in Start Here.
:::

::: checkpoint | Check Yourself
1. Where is an agent's permission to send mail actually granted?
2. What is the difference between accountability and authorization?
3. Your agent's reply says it checked with a supervisor first. What do you look
   at?
4. Name the three shapes of excessive agency.

Answers: (1) When the tool is put in its list, before any request arrives. (2)
Accountability records who did it; authorization decides who may. (3) The
record: the audit rows and the outbox, not the reply. (4) Too many tools, one
tool that reaches too far, and nothing standing between deciding and doing.
:::

::: sources | Sources
Written for this course. The audit fields listed here are the fields the
practice target writes, and you can read that code yourself.
:::
