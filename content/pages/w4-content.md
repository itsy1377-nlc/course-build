::: intro
This page takes the agent loop apart. You will see how the message list grows,
how a tool name becomes a function call, and what happens when a tool fails.
Then you trace the whole thing on paper before you touch code.
:::

::: section | The loop is four steps
`agent/loop.py` describes itself in four lines. Here they are again:

```
1. Send the conversation to the model.
2. If the model asked for a tool, run it and put the result in the
   conversation.
3. Go back to step 1.
4. Stop when the model answers in words, or when we hit the step limit.
```

You read that file last week. This week you take each step apart and then build
on it.
:::

::: section | The bound: why the loop counts
```python
for step in range(1, max_steps + 1):
```

`max_steps` is 6 in `config/lab.config.yaml`. The loop runs six times at most.

Take the bound away and think about what is left. A model that keeps asking for
tools keeps getting them. Nothing in the model gets tired. Your quota does.
Your target app does. Your bill does.

A bounded loop is a control. It is the first control in this course written in
code rather than in words, and it is one number in a config file.

When the loop runs out, the `else` on the `for` runs. The run ends with
`stopped` set to `"step_limit"`. That is a normal ending, not a crash.
:::

::: section | Message accumulation: the list only grows
The conversation is a Python list. It starts with two entries.

```python
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
```

Every pass through the loop adds to it. Nothing is ever removed. The model sees
the whole list on every pass.

Here is a real run. The user asked the agent to summarize ticket T-503.

| Point in the run | What `messages` holds |
|---|---|
| Before step 1 | system, user |
| Step 1, model replies | plus an assistant message asking for `search_tickets` |
| Step 1, tool runs | plus a tool message holding the ticket text |
| Step 2, model replies | plus an assistant message asking for `get_customer` |
| Step 2, tool runs | plus a tool message holding the customer record |
| Step 3, model replies | plus an assistant message in plain text, and the loop breaks |

Six entries went in. The list never shrank.

Two things follow from that, and both come back later in the course.

**Cost.** Every entry is sent again on every pass. A long tool result gets paid
for on every step after it. That is why the loop cuts results off at
`max_tool_result_chars`.

**Trust.** By step 3, that list holds text a stranger typed into a support
ticket. It sits in the same list as your system prompt, in the same format. The
model reads both the same way.
:::

::: section | Tool dispatch: how a name becomes a function
The model sent a name. Something has to turn that name into running code.

```python
result = tools.call_tool(cfg, name, args)
```

Inside `call_tool`, three things happen before your function runs:

```python
    allowed = list(cfg.agent.get("allowed_tools", []) or [])
    if name not in TOOLS:
        raise ToolError(f"There is no tool named {name!r}.")
    if name not in allowed:
        raise ToolError(f"The tool {name!r} exists but is not in agent.allowed_tools.")
    fn: ToolFn = TOOLS[name]["fn"]
```

1. Is the name in `TOOLS`? That is the registry. It maps a name to a schema and
   a function.
2. Is the name in `allowed_tools` in your config file? A tool can exist and
   still be switched off.
3. Get the function out of the registry and call it.

That second check is a real control, and it is the cheapest one in the whole
system. A tool the model is never told about is a tool the model cannot ask
for.

This is why Module 2 asks you to edit two files. You register your tool in
`TOOLS` in `agent/tools.py`. You add its name to `agent.allowed_tools` in
`config/lab.config.yaml`. Miss the second one and the model never learns your
tool exists.
:::

::: section | What happens when a tool errors
Tools fail. The target app is not running. A customer ID does not exist. The
network blinks. None of that is unusual.

```python
try:
    result = tools.call_tool(cfg, name, args)
    error = None
except tools.ToolError as exc:
    # A tool failing is normal. Tell the model and keep going.
    result = f"The tool failed: {exc}"
    error = str(exc)
```

The failure becomes text. The text goes back to the model as the tool result.
The loop keeps running. The model can try something else, or it can tell the
user what went wrong.

Now compare that with a tool that fails quietly.

Say your `get_customer` returns an empty string when the customer does not
exist. No error is raised. The loop sees a successful call with an empty
result. It appends the empty string and moves on.

The model now believes the lookup worked and the record is blank. It tells the
user the account has no details. Nothing in the ledger says anything went
wrong, because as far as the ledger knows, nothing did.

**A tool that returns an empty string on failure is worse than a tool that is
missing.** A missing tool is obvious. A silent one produces confident wrong
answers, and your log agrees with them.

That is why Module 2 grades your error path as heavily as your success path.
:::

::: section | The activity: trace the loop on paper
Do this before you write any code this week. It takes about 30 minutes, and it
is the reason the code makes sense afterward.

1. Get a sheet of paper. Draw a column down the left and label it `messages`.
2. Write the two starting entries: system, then user. Use the request
   `summarize ticket T-503`.
3. Open `agent/loop.py`. Start reading at the `for step` line.
4. Walk one pass by hand. Every time the code appends to `messages`, write a new
   row on your paper. Note which step you are on.
5. Stop when you reach a `break`, or when you have written six passes.
6. Now run it for real. Start the target app:

```
python -m target.seed
python -m target.app
```

7. In a second terminal, run the same request:

```
python -m agent.cli "summarize ticket T-503"
```

8. Compare your paper to what printed, and to `runs/ledger.jsonl`.

Where the two disagree, your paper is probably wrong. Working out why is the
whole point of the exercise.

Bring one disagreement to the Q and A board if you cannot explain it.
:::

::: callout warning | The tool you add this week has no authorization check
This needs saying plainly, because it is the setup for Week 6.

`get_customer` asks the target app for a customer record. It never asks whether
the person running the agent is allowed to see that customer. There is no such
check in the tool. There is no such check in the loop. There is no such check
in the target app either.

**Your own tool will not have one either.** The assignment does not ask for
one, and you should not add one.

That is deliberate. In Week 6 you will point a test harness at your own agent
and find this yourself, in code you wrote, with your name on it. Finding it in
your own work teaches more than being told about it now does.

Write the tool. Leave the gap. Week 6 is where you close it.
:::

::: section | The name for that gap
OWASP calls this risk LLM03:2026 Excessive Agency.

**Excessive agency** means an agent can take actions that are too broad, too
powerful, or too permanent for the checks around them.

Your agent is about to have more of all three. Every tool you register widens
what the model can ask for. Your tools run with whatever access the program
has, which is usually all of it. And `before_tool_call` still says yes to
everything.

Write that down somewhere you will find again. Week 6 gives you the full list
of missing controls and a name for each one.
:::

::: reading | Reading: the chat completions response shape
**What it is.** The vendor reference for the request and response format your
agent uses. It is written for working engineers, so it is dense. You are not
expected to read all of it, and you are not expected to follow every line.

**What to read.** The request section, and specifically the message with the
role `tool`. That is the message your loop builds after a tool runs. About 20
minutes.

**What to look for.** Week 2 showed you the reply that asks for a tool. This
week you are looking at the other direction: the message that carries a result
back. Find which fields that message is required to have.

**One warning that will save you an evening.** Do not read the newer function
calling guide instead of this reference. It documents a different interface than
the one your labs and most endpoints use. The shapes will not match.

**One question to answer while you read**, which comes back on the quiz: a tool
result message carries a field that ties it to the request that asked for it.
Name that field, then find the line in `agent/loop.py` that sets it.

The link is on the Course Material page.
:::

::: checkpoint | Check Yourself
Answer these before you start Module 2.

1. Your agent ran three steps. How many entries are in `messages` at the end,
   and which of them did the model write?
2. You register a tool in `TOOLS` and stop there. What happens when you ask the
   agent to use it?
3. A tool raises `ToolError`. Does the run stop? Say what happens instead.
4. Name one thing your new tool will not check, and name the week you fix it.
:::

::: sources
OWASP Top 10 for Large Language Model Applications 2026, entry LLM03:2026
Excessive Agency. Licensed CC BY-SA 4.0. Linked, not reproduced.

OWASP Top 10 for Agentic Applications 2026, entry ASI02 Tool Misuse. Licensed
CC BY-SA 4.0.

The chat completions API reference is vendor documentation. It is linked on the
Course Material page, not reproduced here.

All code quoted on this page comes from the course lab repository, which is
instructor-authored.
:::
