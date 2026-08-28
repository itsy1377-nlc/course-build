::: intro
This page teaches one idea and one artifact. The idea is that the model now
calls your code. The artifact is the JSON tool schema, which is the only thing
a model ever learns about a tool. Read this page before the Annotated Skeleton.
:::

::: section | Where you are right now
In Week 2 you wrote a script that talked to a model. You built a message list.
You sent it. You read the reply and pulled a field out of a dictionary.

That script had one shape, and you controlled all of it.

This week the shape changes. The change is what makes an agent an agent. It is
also the hardest thing in this course to see the first time, so this page goes
slowly and puts both shapes side by side.
:::

::: section | Shape one: your script calls the model
Here is the Week 2 shape. Nothing in it is new.

```python
messages = [{"role": "user", "content": "How many tickets are open?"}]

response = llm.chat(messages, None, cfg)
answer = llm.message_of(response)["content"]
print(answer)
```

Read what happens, in order:

1. You built the message list.
2. You called `llm.chat`. You chose when.
3. The model produced text.
4. Your script printed that text.

The model never touched anything. It made words. Your script decided what to do
with them. Every decision in those lines was yours.
:::

::: section | Shape two: the model calls your function
Now the same script, with one thing added. You pass a list of tool schemas.

```python
schemas = tools.schemas_for(cfg)

messages = [{"role": "user", "content": "How many tickets are open?"}]

response = llm.chat(messages, schemas, cfg)
message = llm.message_of(response)
tool_calls = message.get("tool_calls") or []
```

The reply now comes in two possible shapes. It may hold `content`, which is
text for a person to read. Or it may hold `tool_calls`, which is a request.

When it holds `tool_calls`, your code does this:

```python
for call in tool_calls:
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])
    result = tools.call_tool(cfg, name, args)
```

Three lines. Look hard at where each value came from.
:::

::: section | Name exactly what changed
Put the two shapes next to each other. Four things moved.

1. **You passed `schemas`.** The model now has a menu. It did not have one
   before.
2. **The reply can be a request instead of an answer.** Your code has to check
   which one arrived.
3. **`name` came from the model.** You never typed `search_tickets` anywhere.
   The model picked it.
4. **`args` came from the model.** You never typed `{"query": "T-503"}`
   anywhere either.

Now the part that trips people up. Read it twice.

**The model did not run anything.** It cannot. It produced text that names a
function and some arguments. Your Python read that text and made the call.

Nothing moved from your computer to the model. What moved is who decides. You
still own every line that runs. You no longer own the choice of which line runs
next.

That is the inversion. Your program went from giving orders to taking requests.
:::

::: callout note | If you remember one sentence from this week
The model asks. Your code answers.

Asking is free, and anyone whose text reaches the model gets to ask. Answering
is where you decide. Deciding is where security lives.
:::

::: section | What a JSON tool schema is
A **JSON tool schema** is a written description of one tool. It uses a fixed
format, and it is sent to the model with every request.

Here is a real one. This is the schema for `search_tickets`, taken from the
registry in `agent/tools.py` and written out as JSON:

```json
{
  "type": "function",
  "function": {
    "name": "search_tickets",
    "description": "Search the support ticket queue and return matching tickets, including the customer's own words.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Words to search for in the subject and body."
        },
        "limit": {
          "type": "integer",
          "description": "How many tickets to return at most."
        }
      },
      "required": ["query"]
    }
  }
}
```

Four parts do all the work:

- `name` is what the model writes when it wants the tool. It has to match the
  key it is registered under.
- `description` says what the tool is for and when to use it.
- `properties` lists each argument, with a type and a description.
- `required` says which arguments cannot be left out.
:::

::: callout warning | The schema is the only thing the model knows
This is the sentence to hold on to this week.

The model never sees your Python. It never reads your comments. It never runs
your function and watches what happens. It reads the schema. That is all it
gets.

So a schema is not documentation. It is an interface. It is a promise your code
has to keep.

Three ways a schema goes wrong:

1. **A vague description.** The model calls the tool at the wrong moment, or it
   never calls the tool at all.
2. **An argument with no description.** The model invents a value, and the value
   it invents is wrong.
3. **A schema that does not match the function.** The model sends what the
   schema promised. Your code rejects it.

In Module 2 you write a schema yourself. The autograder builds arguments from
your own schema and calls your function with them. A schema that lies about the
function fails there.
:::

::: section | Why a schema is a security topic
A tool is a door. A schema is the sign on the door.

OWASP calls the matching risk ASI02 Tool Misuse, in the Top 10 for Agentic
Applications 2026. Tool misuse is what happens when an agent uses a real tool,
in a normal way, for a purpose nobody intended. Nothing is broken into. The
tool works. It worked for the wrong request.

MITRE ATLAS carries the same behavior as technique AML.T0053, AI Agent Tool
Invocation.

Notice what makes this possible. The model chooses which tool to call, and it
chooses based on text. Any text that reaches the model gets a vote. A ticket a
stranger typed is text. So is an article from your own knowledge base. Week 5
is built on that fact.

For now, hold one idea. Every tool you add widens what the model can ask for.
:::

::: callout note | A name change worth knowing about
ATLAS renamed AML.T0053. It used to be called "LLM Plugin Compromise". It is
now "AI Agent Tool Invocation".

If you find a blog post or a course video using the old name, what it describes
is superseded. This course pins ATLAS release 2026.07. Use the current name.
:::

::: section | Three questions for any call that leaves your program
Your tools talk to HelpDesk Lite over HTTP. Your model client talks to an
endpoint over HTTP. Both can fail, and neither failure is your fault.

Ask three questions of every one of those calls.

**One: what if it raises?** Wrap it. Here is the real code from
`agent/tools.py`:

```python
    try:
        response = _session().get(url, params=params, headers=_headers(cfg), timeout=TIMEOUT_S)
    except requests.RequestException as exc:
        raise ToolError(
            f"Could not reach HelpDesk Lite at {url}. Is it running?\n"
            f"Start it with:  python -m target.app\n"
            f"  {exc}"
        ) from exc
```

`try` runs the risky line. `except` catches one named kind of failure.

Notice what it does not do. It does not catch every possible error, and it does
not stay quiet. It raises a `ToolError` with a message a person can act on.

**Two: what if it never answers?** A call with no timeout can hang forever. The
same file sets one:

```python
TIMEOUT_S = 15
```

That value goes into every request. Fifteen seconds, then give up.

**Three: is it worth trying again?** Some failures clear on their own. A 429
means you went too fast. A 503 means the server had a bad moment. Both are
worth one more try after a wait.

Other failures never clear. A 401 means your key is wrong. Retrying a 401 burns
quota and changes nothing.

You wrote that rule in Module 1, in `should_retry` and `backoff_seconds` in
`agent/llm.py`. Open both again this week. The agent loop depends on them now.
:::

::: callout tip | A failing tool is normal and must not stop the agent
Here is what the loop does when a tool raises:

```python
try:
    result = tools.call_tool(cfg, name, args)
    error = None
except tools.ToolError as exc:
    # A tool failing is normal. Tell the model and keep going.
    result = f"The tool failed: {exc}"
    error = str(exc)
```

The failure becomes a message. The message goes back to the model. The loop
keeps running.

That is the pattern for the whole course. A tool that fails loudly is a working
tool. A tool that fails quietly is a broken one, because the agent carries on
as if nothing went wrong.
:::

::: section | One word you will hear: MCP
The Model Context Protocol, or MCP, is a standard way to hand an agent a
package of tools. Someone else writes the package. You point your agent at it.
Your agent now has tools you did not write.

You do not build one in this course. You will meet one during your first week
on a real agent, so it gets named here.

The security point is the one this week already made. A tool is a way in.
Someone else's tool is someone else's way in, running with your permissions.

ATLAS covers this as AML.T0110, AI Agent Tool Poisoning. Module 9 points you at
the OWASP guide on building these servers safely, if you want it later.
:::

::: reading | Required reading: the Annotated Skeleton page
**What it is.** The next page in this module. It walks through `agent/loop.py`,
the file that is the whole agent, one part at a time. Every code block on it is
copied from the file rather than summarized.

**What to read.** All of it. It is the only required reading this week, and it
is capped at 45 minutes.

**How to read it.** Open `agent/loop.py` in your editor. Put the page beside
it. Find each quoted block in the real file as you go. Reading the page without
the file open is the single mistake that makes this week hard.

**What to look for.** Two places, and both are marked on the page:

1. The line that calls `json.loads` on the model's arguments.
2. The function called `before_tool_call`.

**One question to answer while you read**, which comes back on the Week 4 quiz:
the loop runs at most `max_steps` times. What happens on the step after the last
one, and where in the file is that written?
:::

::: checkpoint | Check Yourself
Answer these before you start the lab work.

1. In shape two, where did the value of `name` come from?
2. Your tool has an argument called `limit` and no description for it in the
   schema. What is the model going to do?
3. A request comes back with HTTP 401. Do you retry it? Say why.
4. Your `get_customer` returns an empty string when the customer is missing.
   The agent tells the user the record is blank. Which part of that is your bug?
:::

::: sources
OWASP Top 10 for Agentic Applications 2026, entry ASI02 Tool Misuse. Licensed
CC BY-SA 4.0. Linked, not reproduced. The link is on the Course Material page.

MITRE ATLAS, release 2026.07, techniques AML.T0053 AI Agent Tool Invocation and
AML.T0110 AI Agent Tool Poisoning. ATLAS is Apache 2.0 and incorporates MITRE
ATT&CK, which requires this attribution: ATT&CK is a registered trademark of
The MITRE Corporation.

All code quoted on this page comes from the course lab repository, which is
instructor-authored.
:::
