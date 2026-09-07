::: intro
Every pass of the loop costs money, and nothing in the loop is watching the
money. This page is about the two guards you add this week: a cap, which is a
number, and an approval gate, which is a person.
:::

::: section | Each pass of the loop is billed
Every message your agent sends to the model is a **call**, and every call is
billed. The bill is counted in **tokens**. A token is a chunk of text. Short
words are one token, longer ones are more.

Step 1 of the loop sends the whole conversation and the tool list. So does the
next pass, and the one after that. Each pass sends everything again, plus
whatever the last pass added.

The cost of a run does not grow in a straight line. It grows as the
conversation grows.
:::

::: section | A runaway loop is a loop with no reason to stop
Step 5 sends the loop back to step 1. That is normal. It becomes a problem when
every pass hands the model something new to do.

A tool that always gives back another ticket to read will do it. So will a tool
that fails in a way the model keeps retrying. The agent is not broken and it is
not under attack. It is working, and it is spending.
:::

::: section | Write the prediction before you run
You write your number first, in cents. A number you write afterwards is not a
prediction. It is a copy of the answer.

The notebook prints what you need: the price the gateway charges for the model
you picked, your step limit, and the size of the conversation so far. Multiply
those out and write the total down.

Being wrong is normal here. Most people are wrong by a lot. **The gap between
your number and the ledger is the thing worth writing about.**
:::

::: section | The burnable key
You do not run this on your term token. Your instructor issues a second key with
a small ceiling, for this week only. When it is empty the gateway refuses the
call and the run ends.

That is not a classroom rule. It is how the work is done. You do not test a
spending failure on the account that pays the bills.
:::

::: section | Two records of the same spend
Your run writes a **cost stamp** on each call. The gateway keeps its own
**ledger**, a row per call, under school control. Both describe the same events.

Reconciling means putting the two totals side by side and saying whether they
agree. If they do not, say by how much and where you looked.

The ledger row is the record. Your notebook total is your own arithmetic over
the same run, and arithmetic can be wrong. Never report a cost from what the run
printed alone.
:::

::: section | Too much reach has a name
An agent that can do more than its job needs has a name: **excessive agency**.
It is one of the selected OWASP risks this course covers, from the 2026 release,
where it is LLM06.

Spending with no ceiling is one shape of it. Acting on something you cannot undo
with nobody in the way is another. This week you put something in the way of
each.
:::

::: section | Guard one: the cap
The guard is supplied and it already works. One condition is left blank, and
that blank is yours.

```python
def budget_guard(spent_cents, cap_cents):
    if ____:                    # the one line you fill in
        return "stop"
    return "go"
```

The loop calls this before every model call. Return `"stop"` and the run ends
where it stands. A black **cap card** appears in the filmstrip, and a line in
the record says the cap ended the run.
:::

::: callout warning | A cap has no opinion
The cap does not know why your agent is spending. It cannot tell a runaway from
a long job that was going to finish.

It stops both. That is the trade you are making when you set the number, and you
should be able to say it out loud.
:::

::: section | Guard two: the approval gate
Week 1 asked you for three fields on each tool. The third was what a person
would need to see before approving it. This week that field becomes code.

```python
def approval_guard(tool_name, irreversible):
    if ____:                    # the one line you fill in
        return "ask_human"
    return "go"
```

When the guard returns `"ask_human"`, the run pauses and an **approval card**
appears. An approval event goes into the record with the tool name and the
arguments it was called with. Your answer is written down too.
:::

::: section | Where each guard sits in the loop
The two guards run at different moments, and that is why they catch different
things.

| Guard | Runs before | What it is protecting |
|---|---|---|
| The cap | Step 1, the model call | Money |
| The gate | Step 3, running the tool | An action nobody can take back |

A cap cannot stop a single tool call from doing damage, because one call is
cheap. A gate cannot stop a run from spending, because it only wakes up when a
tool is about to run. You need both, and neither covers the other.
:::

::: callout note | Neither guard stops an injection
Nothing you build this week keeps text in a ticket from being read as an order.
Week 4 showed you that, and week 7 is where you try to hold it.

What these guards do is bound the damage when it happens anyway. A control that
limits what an attack can reach is worth having even when it prevents nothing.
:::

::: section | A gate does not discriminate, it delegates
Run your week 4 ticket text again with the gate on. The call is blocked. That
looks like a win.

Now send an ordinary request that needs the same tool for a good reason. That
one is blocked as well.

| The run | Why the tool was called | What the gate did |
|---|---|---|
| Your week 4 ticket | Text a stranger wrote | Paused and asked |
| An ordinary request | You asked for it | Paused and asked |

The gate cannot tell those two apart, and it does not try. It moves the decision
to a person. **The control is now that person, not the code.**
:::

::: section | Count the cost of asking
Turn the gate on and run twenty ordinary requests. Count the approval cards.

Then multiply. Name a number of requests a real shift would handle, say where
that number came from, and work out how many approvals that is. Your own data,
your own arithmetic.

A person who approves that many things stops reading them. That is called
**approval fatigue**, and this is the week you measure it rather than hear about
it.
:::

::: callout note | Why twenty here and not thirty
Thirty trials is the floor when you are measuring how often a rare thing
happens. This is not that. Every run that reaches an irreversible tool raises a
card, so you are counting, not estimating.
:::

::: scope | Authorization and Scope
Everything here runs against your own agent, in your own notebook, on the
burnable key your instructor issued. The three permitted targets are the
practice target, the agent you built, and a model reached through the school
gateway with your own token.

Never an AI service you signed up for yourself. Never another student's key.
Clause 1 and clause 3 of the Rules of Engagement page in Start Here hold the
full rules.
:::

::: checkpoint | Check Yourself
1. Why does the cost of a run grow faster than the number of passes?
2. Your notebook says nine cents and the ledger says fourteen. Which do you
   report?
3. Your cap ended a run that was going to finish. Did the cap fail?
4. The gate blocked your week 4 attack. What else did it block?
5. What does the approval count tell you about a real shift?

Answers: (1) Each pass sends the whole conversation again, and the conversation
keeps growing. (2) Both, side by side, with the gap named. The ledger is the
record. (3) No. A cap is a number and it has no opinion about why. (4) The
ordinary request that needed the same tool. (5) Only what your own multiplying
supports, from the number of requests you named.
:::

::: sources | Sources
Written for this course. The two guard functions shown here are the ones in the
week 5 notebook, with the same blank in each, and you can read all of the code
around them.
:::
