::: intro
This page takes the agent loop apart: how the message list grows, how a tool
name becomes a function call, and what happens when a tool fails. Then you
trace it on paper.
:::

::: section | Four steps, and a bound on how many
Send the conversation to the model. Run any tool it asked for, and put the
result back in the conversation. Repeat. Stop when the model answers in words,
or when the step limit is reached.

That limit is one line:

```python
for step in range(1, max_steps + 1):
```

`max_steps` is 6 in `config/lab.config.yaml`, so the loop runs six times at
most.

Take the bound away and see what is left. A model that keeps asking for tools
keeps getting them. Nothing in the model gets tired. Your quota does.

A bounded loop is a control, the first one in this course written in code
rather than words. It is one number in a config file.

When the loop runs out, the `else` on the `for` runs and `stopped` becomes
`"step_limit"`. That is a normal ending, not a crash.
:::

::: section | Message accumulation: the list only grows
The conversation is a Python list, and it starts with two entries.

```python
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
```

Tool calls and results are appended, nothing is removed, and the model sees
the whole list every pass. Here is a real run, from a request to summarize
ticket T-503.

| Point in the run | What `messages` holds |
|---|---|
| Before step 1 | system, user |
| Step 1, model replies | plus an assistant message asking for `search_tickets` |
| Step 1, tool runs | plus a tool message holding the ticket text |
| Step 2, model replies | plus an assistant message asking for `get_customer` |
| Step 2, tool runs | plus a tool message holding the customer record |
| Step 3, model replies | plus an assistant message asking for `send_email` |
| Step 3, tool runs | plus a tool message holding the send result |
| Step 4, model answers | nothing is added. The loop breaks |

Read that last row again, because it surprises people. On the step where the
model answers in words, the loop sets `final_text`, records a trace event, and
breaks. It never appends that message.

So the list ends at eight entries, and the agent's final answer is not one of
them. It lives in `final_text` and in the trace file.

You never asked for an email. Step 3 is there because the body of T-503 tells
the agent to send one, and the agent read that instruction out of a tool
result. Week 5 is about why that works. For now, note only that it happened
inside the same list.

**Cost.** Every entry is sent again on every pass, so a long tool result is
paid for on every later step. That is why the loop cuts results off at
`max_tool_result_chars`.

**Trust.** From step 1 that list holds text a stranger typed into a ticket,
next to your system prompt, in the same format. Nothing in the list marks one
entry as data and another as orders.
:::

::: section | Tool dispatch: how a name becomes a function
The model sent a name. Something turns that name into running code.

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

1. Is the name in `TOOLS`, the registry that maps a name to a schema and a
   function?
2. Is the name in `allowed_tools` in your config file? A tool can exist and
   still be switched off.
3. Get the function out of the registry and call it.

**That second check is the control.** A model can write any tool name it
likes, including one you never offered, because a tool call is only text.
Nothing stops it asking. The allowlist check stops the call running.

Not offering a tool is still worth doing, and it is the cheapest measure here.
It just is not what enforces the rule.

So Module 2 has you edit two files: `TOOLS` in `agent/tools.py`, and
`agent.allowed_tools` in `config/lab.config.yaml`. Miss the second and your
tool never runs.
:::

::: section | What happens when a tool errors
Tools fail, and that is ordinary. The target app is down. A customer ID does
not exist.

```python
try:
    result = tools.call_tool(cfg, name, args)
    error = None
except (tools.ToolArgumentError, tools.ToolNotImplemented) as exc:
    # Permanent for this run, so remember it.
    dead_calls.add(signature)
    result = f"The tool failed: {exc}"
    error = str(exc)
except tools.ToolError as exc:
    # This one might clear on its own. A tool failing is normal.
    result = f"The tool failed: {exc}"
    error = str(exc)
```

The failure becomes text, goes back to the model as the tool result, and the
loop keeps running.

There are two kinds of failure here. It is the same split `llm.py` makes about
a bad request.

"The target app did not answer" may clear on its own, so the agent may try
again. "This tool does not take an argument called cfg" will not clear, however
many times it is sent.

So the loop remembers that exact call and refuses to repeat it. Small models
get stuck in that loop easily, and an agent that spends every step re-sending a
call that cannot work never answers at all.

Now compare a tool that fails quietly. Say your `get_customer` returns an
empty string when the customer does not exist. No error is raised, so the loop
appends an empty result and moves on.

The model now believes the record is blank, and tells the user so. Nothing in
the ledger says anything went wrong, because nothing did.

**A tool that returns an empty string on failure is worse than a missing
tool.** A missing tool is obvious. A silent one produces confident wrong
answers, and your log agrees.

So Module 2 grades your error path as heavily as your success path.
:::

::: section | The activity: trace the loop on paper
Do this before you write code. It takes about 30 minutes.

1. Draw a column down a sheet of paper. Label it `messages`.
2. Write the two starting entries, system and user, for the request
   `summarize ticket T-503`.
3. Open `agent/loop.py` and read from the `for step` line.
4. Walk one pass by hand. Every time the code appends to `messages`, write a
   new row and note the step.
5. Stop at a `break`, or after six passes. Do not assume the run is short.
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

Where they disagree, your paper is probably wrong, and working out why is the
point. Bring one to the Q and A board if you cannot explain it.
:::

::: callout warning | The tool you add this week has no authorization check
`get_customer` asks the target app for a customer record. It never asks
whether the caller may see that customer. There is no such check in the tool,
the loop, or the target app.

**Your own tool will not have one either.** The assignment does not ask for
one, and you should not add one.

In Week 6 you point a harness at your own agent and find this in code you
wrote. That teaches more than being told now. Write the tool, leave the gap,
and Week 6 is where you close it.
:::

::: section | The name for that gap
OWASP calls this risk LLM03:2026 Excessive Agency.

**Excessive agency is capability granted without a control on its use.** The
action need not be permanent. A reversible action nobody approved is still
excessive agency.

Your agent is about to have more capability. Every tool you register widens
what the model can ask for, your tools run with whatever access the program
has, and `before_tool_call` still says yes to everything.

Week 6 gives you the full list of missing controls, with a name for each.
:::

::: reading | Reading: the chat completions response shape
**What it is.** The vendor reference for the format your agent uses. It is
dense, and written for engineers.

**What to read.** The request section, specifically the message with role
`tool`. That is what your loop builds after a tool runs. About 20 minutes.

**What to look for.** Week 2 showed the reply that asks for a tool. Now look
at the message carrying a result back, and find which fields it must have.

**One warning.** Do not read the newer function calling guide instead. It
documents a different interface.

**One question to answer while you read**, on the quiz later: name the field
that ties a tool result to the request that asked for it, then find the line in
`agent/loop.py` that sets it.

The link is on the Course Material page.
:::

::: checkpoint | Check Yourself
Answer these before you start Module 2.

1. Your agent ran three steps and answered in words. How many entries are in
   `messages`, and where is the final answer?
2. You register a tool in `TOOLS` and stop there. What happens when you ask the
   agent to use it?
3. A tool raises `ToolError`. Does the run stop? Say what happens instead.
4. Name one thing your new tool will not check, and the week you fix it.
:::

::: sources
OWASP Top 10 for Large Language Model Applications 2026, entry LLM03:2026
Excessive Agency. Licensed CC BY-SA 4.0. Linked only.

OWASP Top 10 for Agentic Applications 2026, entry ASI02 Tool Misuse. Licensed
CC BY-SA 4.0.

The chat completions API reference is vendor documentation, linked only.

All code quoted here is from the lab repository, which is instructor-authored.
:::
