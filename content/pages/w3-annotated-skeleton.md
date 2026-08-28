::: intro
This is the required reading for Week 3. It walks through `agent/loop.py`, the
file that is the whole agent. Every code block below is copied from that file.
Budget 45 minutes.
:::

::: callout stop | Do not read this page on its own
Open `agent/loop.py` in your editor first. Put this page next to it.

For each block below, find the same lines in the real file. That habit is what
makes this page work. Reading it like an article does not.
:::

::: section | What the file says about itself
The file opens with its own summary. Here it is, word for word:

```python
"""The tool-calling loop.

This is the whole agent. It is about a hundred lines and there is no magic in
any of them:

    1. Send the conversation to the model.
    2. If the model asked for a tool, run it and put the result in the
       conversation.
    3. Go back to step 1.
    4. Stop when the model answers in words, or when we hit the step limit.
"""
```

Four steps. That is the agent. Everything else in the file is detail hanging off
one of those four.

Step 3 is the one that matters. Sending a conversation to a model is a chatbot.
Sending it, running what came back, and sending the result in again is an agent.
:::

::: section | What one run produces
```python
class AgentResult:
    """What one run produced."""

    def __init__(self, final_text: str, trace: Trace, steps: int, stopped: str):
        self.final_text = final_text
        self.trace = trace
        self.steps = steps
        self.stopped = stopped  # "answered", "step_limit", or "error"
```

A run produces four facts. What the agent said. What it did, in the trace. How
many steps it took. Why it stopped.

That last field is worth noticing now. The values `"answered"` and
`"step_limit"` are very different endings. You will read this field a lot in
Week 7.
:::

::: section | Extension point 1: the function every defense lands in
This is the most important function in the lab repository. Here is its comment
block from the file, unchanged:

```python
# ===========================================================================
# EXTENSION POINT 1 of 5   (this is the important one)
#
# Every defense you build in this course lands in this function. It runs after
# the model has asked for a tool and before the tool actually runs, which is
# the last moment anything can be stopped.
#
# It ships wide open: it says yes to everything.
#
#   Return (True, "")             to let the call through.
#   Return (False, "reason")      to block it. The reason goes back to the
#                                 model as the tool result, and it lands in
#                                 the ledger, so a blocked call leaves proof.
# ===========================================================================


def before_tool_call(name: str, args: dict[str, Any], cfg: Config) -> tuple[bool, str]:
    """Decide whether one tool call is allowed to run."""
    return True, ""
```

Two lines of body. It says yes to everything, every time.

Read the timing again, because the timing is the whole point. This function
runs **after** the model has asked for a tool. It runs **before** the tool does
anything at all.

That gap is the only place in the system where a decision can still be made.
Once the tool runs, the email is queued and the record is read. There is no
undo.

You do not change this function in Week 3. You change it in Module 4. Learn
where it sits now, because you will come back to it four times.

The file also says what does not belong here:

```python
# What does NOT belong here is a rule that reads the model's prose and decides
# whether it "seems like" an attack. Not because such things are worthless:
# input and output classifiers are real and production systems run them. They
# are a layer, and they guess. This function is the layer that does not have
# to, because it decides on facts you already have: which tool, which
# arguments, which recipient. Put the certain check here and let anything
# probabilistic sit in front of it, never behind it.
```

That is the difference between a guess and a control. Week 5 comes back to it.
:::

::: section | Setting up one run
```python
    schemas = tools.schemas_for(cfg)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
```

Two things get built before the loop starts.

`schemas` is the menu. It holds the tool schemas the model is allowed to see.
Only tools named in `agent.allowed_tools` in your config file end up in it.

`messages` is the conversation. It starts with two entries and it grows. Every
pass through the loop adds to it. Week 4 spends a whole page on that growth.
:::

::: section | Checking the settings before trusting them
```python
    try:
        max_steps = int(cfg.agent.max_steps)
        max_chars = int(cfg.agent.max_tool_result_chars)
    except (TypeError, ValueError) as exc:
        raise ConfigError(
            f"agent.max_steps and agent.max_tool_result_chars in "
            f"config/lab.config.yaml both have to be whole numbers. {exc}"
        ) from exc
    if max_steps < 1:
        raise ConfigError(
            f"agent.max_steps is {max_steps}. It has to be at least 1, or the "
            f"agent never gets a turn. Six is a good starting value."
        )
```

Here is `try` and `except` doing an ordinary job before the interesting part
starts.

Two settings come out of a file a person edited. `int()` raises if that person
typed `six` instead of `6`. The `except` catches it and says which two settings
to look at.

Then a second check. A `max_steps` of zero is a number, so `int()` accepts it
happily. The loop would then run zero times and the agent would never get a
turn. So the code says no to that separately.

Notice the pattern. Catch what can raise. Then check what cannot raise but is
still wrong.
:::

::: section | The loop, and the bound on it
```python
    step = 0
    stopped = "step_limit"
    final_text = ""

    for step in range(1, max_steps + 1):
        response = llm.chat(messages, schemas, cfg)
        message = llm.message_of(response)
        tool_calls = message.get("tool_calls") or []
```

`max_steps` is 6 in the shipped config. The loop cannot run more than six times.

That bound is not a style choice. Without it, a model that keeps asking for
tools keeps getting them. It runs until your quota is gone, or your card is
charged, or the target app falls over.

Notice that `stopped` starts as `"step_limit"`. The code assumes the worst
ending and only changes it when something better happens.
:::

::: section | The ordinary exit: the model answered in words
```python
        if not tool_calls:
            final_text = message.get("content") or ""
            trace.event("assistant_message", step=step, content=final_text)
            stopped = "answered"
            break
```

No tool calls means the model is finished asking. It produced text instead.

That text becomes the final answer. The event is written to the trace. The
ending is recorded as `"answered"`, and `break` leaves the loop.
:::

::: section | Order matters: the request goes in before the result
```python
        # The assistant's tool-call message has to go into the history before
        # the results do, or the next request is malformed.
        messages.append(message)
```

The model asked for a tool. That request itself joins the conversation before
the answer to it does.

Get the order backwards and the endpoint rejects your next request. The comment
is in the file because this is an easy mistake to make.
:::

::: section | The line Week 3 is about
Here is the block, with the file's own comment on it:

```python
        for call in tool_calls:
            function = call.get("function") or {}
            name = function.get("name") or ""
            raw_arguments = function.get("arguments")

            # ---------------------------------------------------------------
            # The one line week 3 is about.
            #
            # `raw_arguments` is a STRING of JSON, not a dictionary, and the
            # text inside it was shaped by whatever the model just read. If
            # the model read a poisoned ticket, this is where the poison
            # arrives. Parsing it can fail, and a failure here must not take
            # the whole agent down.
            # ---------------------------------------------------------------
            try:
                args = json.loads(raw_arguments) if isinstance(raw_arguments, str) else (raw_arguments or {})
                if not isinstance(args, dict):
                    raise ValueError("arguments were not a JSON object")
```

Take this in three passes.

**Pass one: the shape.** `raw_arguments` is a string. It is not a dictionary.
On the wire it looks like this:

```
'{"to": "someone@example.com", "body": "hello"}'
```

Quote marks on the outside. That is text, and text is not something your
program can use yet. `json.loads` is what turns it into a dictionary.

**Pass two: where the text came from.** The model wrote that string. It wrote
it after reading everything in `messages`.

`messages` holds your system prompt. It holds the user's question. It holds
every tool result from every earlier step, including ticket text a stranger
typed.

So the arguments your program is about to act on were shaped by content you do
not control. `json.loads` does not check that. It cannot. All it checks is
whether the text is valid JSON.

**Pass three: what happens when parsing fails.** Models produce malformed JSON.
It is not rare.

```python
            except (json.JSONDecodeError, ValueError) as exc:
                text = (
                    f"Your tool call could not be read: {exc}. "
                    f"Send the arguments as a JSON object."
                )
                trace.tool_call(step, name, {"_unparsed": raw_arguments}, text,
                                allowed=False, reason="unparsable arguments", error=str(exc))
                messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                                 "name": name, "content": text})
                continue
```

The failure gets caught. It gets written down. It gets handed back to the model
as a tool result. Then `continue` moves on to the next call.

The agent does not crash. It tells the model what went wrong and keeps going.
That is the try and except pattern from the content page, doing real work.
:::

::: callout warning | Why this one line carries the course
Follow the chain once, slowly.

A stranger types text into a support ticket. Your `search_tickets` tool fetches
it. The text goes into `messages`. The model reads it. The model writes a tool
call. `json.loads` turns that call into arguments. Your code runs them.

Nothing in that chain was broken into. Every part did exactly its job.

That is what makes this hard to fix. It is also why the fix goes in
`before_tool_call` rather than anywhere upstream of it.
:::

::: section | Where the guard actually runs
```python
            # The guard gets a COPY. It used to get the same dictionary that
            # was then executed and then written to the ledger, so a guard that
            # quietly rewrote the recipient and returned True produced a ledger
            # showing a call that was never requested. The ledger is the
            # evidence file; it has to record what was asked for.
            requested = copy.deepcopy(args)
            try:
                allowed, reason = before_tool_call(name, copy.deepcopy(args), cfg)
            except Exception as exc:  # noqa: BLE001
                # A broken guard must fail closed, and must say so plainly. The
                # most common mistake here is `return True` instead of
                # `return True, ""`.
                allowed, reason = False, (
                    f"before_tool_call() raised {type(exc).__name__}: {exc}. "
                    f"It must return two things: True or False, and a reason string. "
                    f"For example:  return True, \"\""
                )
            if not allowed:
                text = f"Blocked by the agent's own guard: {reason}"
                trace.tool_call(step, name, requested, text, allowed=False, reason=reason)
                messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                                 "name": name, "content": text})
                continue
```

This is `before_tool_call` from earlier in the file, being used.

Look at where it sits. The arguments have been parsed. The tool has not run
yet. One line later, it will.

Three things here are worth your time.

**`requested` is a copy.** The dictionary written to the ledger is not the same
object the tool runs on. The comment explains why. A guard that quietly changed
an argument used to produce a ledger showing a call nobody made. The ledger is
your evidence file, so it has to record what was asked for.

**A broken guard fails closed.** If `before_tool_call` raises, the call is
blocked, not allowed. That direction is a choice, and it is the safe one. A
guard that crashes and lets everything through is worse than no guard, because
you would believe it was working.

**A blocked call still gets a ledger line.** The model gets told too. Both
matter. The ledger line is your proof that the guard did something.
:::

::: section | Running the tool, and surviving it
```python
            try:
                result = tools.call_tool(cfg, name, args)
                error = None
            except tools.ToolError as exc:
                # A tool failing is normal. Tell the model and keep going.
                result = f"The tool failed: {exc}"
                error = str(exc)

            if len(result) > max_chars:
                result = result[:max_chars] + f"\n[...truncated at {max_chars} characters]"

            trace.tool_call(step, name, requested, result, allowed=True, reason="", error=error)
            messages.append({"role": "tool", "tool_call_id": call.get("id", ""),
                             "name": name, "content": result})
```

Four things happen here, in order.

1. The tool runs. If it raises `ToolError`, the error text becomes the result.
2. A long result is cut at `max_tool_result_chars`, which is 4000 in the config.
3. The call is written to the trace and to the ledger, using `requested`.
4. The result is appended to `messages`, so the model sees it on the next pass.

Step 4 is step 2 of the file's four-step summary. The loop is now closed.

Notice that a tool result is just another message. The model reads it the same
way it reads yours.
:::

::: section | The ending nobody expects: for and else
```python
    else:
        final_text = (
            f"I stopped after {max_steps} steps without finishing. "
            f"Raise agent.max_steps in config/lab.config.yaml if this was expected."
        )
        trace.event("assistant_message", step=max_steps, content=final_text)
```

Python lets a `for` loop have an `else`. It is unusual, and it confuses people,
so here is the rule.

The `else` runs when the loop finished without hitting `break`.

In this file, `break` only happens when the model answers in words. So the
`else` runs exactly when the agent used all six steps and never finished. The
run ends with `stopped` still set to `"step_limit"`.

That is not an error. It is a bounded system doing what it was told.
:::

::: section | The last two lines
```python
    trace.event("run_end", stopped=stopped, steps=step, final_text=final_text)
    return AgentResult(final_text=final_text, trace=trace, steps=step, stopped=stopped)
```

The run gets closed out. The result goes back to whoever called it.

That is the file. About a hundred lines, and you have now read every part that
matters.
:::

::: checkpoint | Check Yourself
Do these with the file open. Give a line number for each answer.

1. Find the line that turns the model's text into arguments your code can use.
2. Find the last moment a tool call can still be stopped.
3. Find the value that keeps the loop from running forever.
4. A tool raises `ToolError`. Find the two lines that keep the agent alive.
5. In your own words: why does a tool result go into `messages` instead of
   being printed?
:::

::: sources
All code on this page is quoted from `agent/loop.py` in the course lab
repository, which is instructor-authored.

The extension point comments and the file docstring are part of that file, and
they appear here unchanged.
:::
