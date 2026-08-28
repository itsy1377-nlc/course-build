::: intro
This page takes the agent loop apart. You will see how the message list grows,
how a tool name becomes a function call, and what happens when a tool fails.
Then you trace the whole thing on paper before you touch code.
:::

::: section | The loop is four steps
`agent/loop.py` describes itself in four lines:

```
1. Send the conversation to the model.
2. If the model asked for a tool, run it and put the result in the
   conversation.
3. Go back to step 1.
4. Stop when the model answers in words, or when we hit the step limit.
```

You read that file last week. This week you take each step apart.
:::

::: section | The bound: why the loop counts
```python
for step in range(1, max_steps + 1):
```

`max_steps` is 6 in `config/lab.config.yaml`, so the loop runs six times at
most.

Take the bound away and think about what is left. A model that keeps asking for
tools keeps getting them. Nothing in the model gets tired. Your quota does.
Your target app does. Your bill does.

A bounded loop is a control. It is the first control in this course written in
code rather than words, and it is one number in a config file.

When the loop runs out, the `else` on the `for` runs, and `stopped` is set to
`"step_limit"`. That is a normal ending, not a crash.
:::

::: section | Message accumulation: the list only grows
The conversation is a Python list. It starts with two entries.

```python
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
```

Tool calls and tool results are appended. Nothing is ever removed, and the
model sees the whole list on every pass.

Here is a real run. The user asked the agent to summarize ticket T-503.

| Point in the run | What `messages` holds |
|---|---|
| Before step 1 | system, user |
| Step 1, model replies | plus an assistant message asking for `search_tickets` |
| Step 1, tool runs | plus a tool message holding the ticket text |
| Step 2, model replies | plus an assistant message asking for `get_customer` |
| Step 2, tool runs | plus a tool message holding the customer record |
| Step 3, model answers | nothing is added. The loop breaks |

Read that last row again, because it surprises people. On the step where the
model answers in words, the loop sets `final_text`, records a trace event, and
breaks. It never appends that message.

So the list ends at six entries, and the agent's own final answer is not one of
them. You find that answer in `final_text` and in the trace file, not in
`messages`.

**Cost.** Every entry is sent again on every pass, so a long tool result is
paid for on every step after it. That is why the loop cuts results off at
`max_tool_result_chars`.

**Trust.** By step 3, that list holds text a stranger typed into a support
ticket. It sits beside your system prompt, in the same format.
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

1. Is the name in `TOOLS`? That is the registry, mapping a name to a schema and
   a function.
2. Is the name in `allowed_tools` in your config file? A tool can exist and
   still be switched off.
3. Get the function out of the registry and call it.

**That second check is the control.** A model can write any tool name it likes,
including one you never offered it, because a tool call is just text the model
produced. Nothing stops it asking. The allowlist check is what stops the call
from running.

Not offering a tool is still worth doing, and it is the cheapest measure in the
whole system. It just is not the thing that enforces the rule.

This is why Module 2 asks you to edit two files. You register your tool in
`TOOLS` in `agent/tools.py`. You add its name to `agent.allowed_tools` in
`config/lab.config.yaml`. Miss the second one and your tool never runs.
:::

::: section | What happens when a tool errors
Tools fail. The target app is not running. A customer ID does not exist. None
of that is unusual.

```python
try:
    result = tools.call_tool(cfg, name, args)
    error = None
except tools.ToolError as exc:
    # A tool failing is normal. Tell the model and keep going.
    result = f"The tool failed: {exc}"
    error = str(exc)
```

The failure becomes text, the text goes back to the model as the tool result,
and the loop keeps running. The model can try something else or tell the user
what went wrong.

Now compare that with a tool that fails quietly. Say your `get_customer`
returns an empty string when the customer does not exist. No error is raised.
The loop sees a successful call with an empty result, appends it, and moves on.

The model now believes the lookup worked and the record is blank. It tells the
user the account has no details. Nothing in the ledger says anything went
wrong, because as far as the ledger knows, nothing did.

**A tool that returns an empty string on failure is worse than a tool that is
missing.** A missing tool is obvious. A silent one produces confident wrong
answers, and your log agrees with them.

That is why Module 2 grades your error path as heavily as your success path.
:::

::: section | The activity: trace the loop on paper
Do this before you write any code this week. It takes about 30 minutes.

1. Get a sheet of paper. Draw a column down the left and label it `messages`.
2. Write the two starting entries: system, then user. Use the request
   `summarize ticket T-503`.
3. Open `agent/loop.py` and start reading at the `for step` line.
4. Walk one pass by hand. Every time the code appends to `messages`, write a
   new row and note which step you are on.
5. Stop at a `break`, or when you have written six passes.
6. Now run it for real. Start the target app:

```
python -m target.seed
python -m target.app
```

7. In a second terminal, run the same request:

```
python -m agent.cli "summarize ticket T-503"
```

8. Compare your paper to what printed and to `runs/ledger.jsonl`.

Where the two disagree, your paper is probably wrong. Working out why is the
point of the exercise. Bring one disagreement to the Q and A board if you
cannot explain it.
:::

::: callout warning | The tool you add this week has no authorization check
`get_customer` asks the target app for a customer record. It never asks whether
the person running the agent is allowed to see that customer. There is no such
check in the tool, none in the loop, and none in the target app either.

**Your own tool will not have one either.** The assignment does not ask for
one, and you should not add one.

That is deliberate. In Week 6 you point a test harness at your own agent and
find this yourself, in code you wrote. Finding it in your own work teaches more
than being told about it now.

Write the tool. Leave the gap. Week 6 is where you close it.
:::

::: section | The name for that gap
OWASP calls this risk LLM03:2026 Excessive Agency.

**Excessive agency is capability granted without a control on its use.** The
action does not have to be permanent to count. A reversible action that nobody
approved is still excessive agency.

Your agent is about to have more capability. Every tool you register widens
what the model can ask for. Your tools run with whatever access the program
has, which is usually all of it. And `before_tool_call` still says yes to
everything.

Week 6 gives you the full list of missing controls and a name for each one.
:::

::: reading | Reading: the chat completions response shape
**What it is.** The vendor reference for the request and response format your
agent uses. It is written for working engineers, so it is dense. You are not
expected to read all of it.

**What to read.** The request section, and specifically the message with the
role `tool`. That is the message your loop builds after a tool runs. About 20
minutes.

**What to look for.** Week 2 showed you the reply that asks for a tool. This
week you look at the other direction: the message that carries a result back.
Find which fields that message is required to have.

**One warning that will save you an evening.** Do not read the newer function
calling guide instead of this reference. It documents a different interface
than your labs use, and the shapes will not match.

**One question to answer while you read**, on the quiz later: a tool result
message carries a field tying it to the request that asked for it. Name that
field, then find the line in `agent/loop.py` that sets it.

The link is on the Course Material page.
:::

::: checkpoint | Check Yourself
Answer these before you start Module 2.

1. Your agent ran three steps and answered in words. How many entries are in
   `messages` at the end, and where is the final answer?
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

The chat completions API reference is vendor documentation, linked on the
Course Material page.

All code quoted here comes from the lab repository, which is
instructor-authored.
:::
