# The list only grows

A text version of the concept video. Every word spoken, in order.

## The loop is one line. The list only grows.
This week you give the agent hands. You write the tools it can call. It is the heaviest week in the course. That is normal, not a sign of falling behind. First take the loop apart, and find every place a tool call can still be refused.

## Four steps, and a bound on how many

```
for step in range(1, max_steps + 1):
```

The whole agent loop is one for statement. This is it. Send the conversation to the model. Run any tool it asked for. Put the result back. Repeat. It stops when the model answers in words, or at the step limit. max steps is six, and it is set in your lab config file. So the loop runs six times at most.

## A bounded loop is a control.

> Take the bound away and a model that keeps
> asking for tools keeps getting them.

A model that keeps asking for tools keeps getting them. Nothing in the model gets tired. Your quota does. This is the first control in this course written in code rather than in words. It is one number in a settings file.

## What the message list holds

1. Start: your system prompt, then your question
2. Step 1: search_tickets, and the ticket text
3. Step 2: get_customer, and the customer record
4. Step 3: send_email, and the result it returned
5. Step 4: the model answers. Nothing is added.

The conversation is a Python list, and it only grows. It starts with two entries. Your system prompt, then a question. Walk one run. You ask the agent to summarize ticket T-503. On step one the model asks for search tickets. The ticket text is added. On step two it asks for get customer. The customer record is added. On step three it asks to send an email. That result is added too. You never asked for an email. The ticket text did. Week 5 is about that. On step four the model answers in words. Read that last line twice, because it surprises people. Nothing is added on step four. The loop saves the answer and breaks. So the list ends at eight entries, and the final answer is not one of them. It lives in the trace file.

## A list that only grows

1. **Cost.** Every entry is sent again on every later pass, so a long tool result is paid for again and again.
2. **Trust.** From step 1 that list holds text a stranger typed, next to your system prompt, in the same format.

Two things follow from a list that only grows. First, cost. Every entry is sent again on every later pass. A long tool result is paid for on every step after it. That is why the loop cuts results off. Second, trust. From step one that list holds text a stranger typed into a ticket. It sits right next to your system prompt, in the same format. Nothing in the list marks one entry as data and another as orders. That is where step three came from.

## Two checks before your function runs

1. Is the name in TOOLS, the registry?
2. Is the name in agent.allowed_tools?
3. Then the function runs.

The model sent a name. Something turns that name into running code. First, is the name in TOOLS, the registry that maps a name to a function? Second, is the name in the allowed tools list in your settings file? Only then does your function run, and that second check is the control. A model can write any tool name it likes, including one you never offered. A tool call is only text. Nothing stops it asking. The allowlist stops the call running. So Module 2 has you edit two files. Miss the second one and your tool never runs.

## Four places, and one of them is empty

*Diagram: Four layers stacked top to bottom, each a place a tool call can still be refused. max_steps bounds the loop. The TOOLS registry asks whether the name exists. agent.allowed_tools asks whether the tool is switched on, and it is marked as the control. At the bottom sits before_tool_call, which right now returns yes to everything.*

- max_steps, the bound on the loop
- The TOOLS registry, does this name exist at all
- agent.allowed_tools, is this tool switched on
- before_tool_call(), right now it says yes to everything

Here is every place a tool call can still be refused. The step limit bounds how many calls there can be. The registry asks whether the name exists at all. The allowlist asks whether that tool is switched on. This layer is the control. And one layer sits under all of them, in your loop, one line before a tool runs. Right now it says yes to everything. In Week 7 you are the one who fills it in.

## Loud is safe. Quiet is not.

1. **Raises an error.** The failure becomes text, goes back to the model, and the loop keeps going.
2. **Returns an empty string.** Nothing is raised. The model believes the record is blank, and your log agrees.

Tools fail, and that is ordinary. The target app is down. A customer ID does not exist. When a tool raises, the failure becomes text and goes back to the model. The loop keeps going, and that is correct behavior. Now compare a tool that returns an empty string when the customer is missing. Nothing is raised. The model believes the record is blank and tells the user so. Your ledger agrees, because nothing went wrong. A tool that fails quietly is worse than a tool that is missing. So Module 2 grades your error path as heavily as your success path.

## Your tool will not ask who is calling.

> get_customer never checks whether the caller
> may see that customer. Leave that gap.

One gap you are building on purpose. get customer asks the target app for a record. It never asks who is calling. Your own tool will not ask either. The assignment does not want that check, so do not add it. In Week 6 you find this gap yourself, in code you wrote. That teaches more than being told now.

## Trace one run on paper first.

> The gap already has a name.
> Excessive agency: capability granted
> without a control on its use.

That gap already has a name. Excessive agency is capability granted without a control on its use. Every tool you register widens what the model can ask for. The tool list is the list of harm the system can do. So before you open the editor, trace one run on paper. It takes about thirty minutes. Students who trace first finish Module 2 in about half the time.
