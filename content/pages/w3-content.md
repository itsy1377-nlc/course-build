::: intro
This page teaches one idea and one artifact. The idea: the model now calls
your code. The artifact: the JSON tool schema, the only thing a model ever
learns about a tool. Read it before the Annotated Skeleton.
:::

::: section | Where you are right now
In Week 2 you built a message list, sent it, and pulled a field out of the
reply. You controlled all of it.

This week the shape changes, and the change is what makes an agent an agent.
:::

::: section | Shape one: your script calls the model
Here is the Week 2 shape. Nothing in it is new.

```python
messages = [{"role": "user", "content": "How many tickets are open?"}]

response = llm.chat(messages, None, cfg)
answer = llm.message_of(response)["content"]
print(answer)
```

You built the message list and chose when to call `llm.chat`. The model
produced text. Your script printed it. Every decision was yours.
:::

::: section | Shape two: the model calls your function
Now the same script with one thing added. You pass a list of tool schemas.

```python
schemas = tools.schemas_for(cfg)

messages = [{"role": "user", "content": "How many tickets are open?"}]

response = llm.chat(messages, schemas, cfg)
message = llm.message_of(response)
tool_calls = message.get("tool_calls") or []
```

The reply now comes in two shapes. It may hold `content`, which is text for a
person. Or it may hold `tool_calls`, which is a request. When it does, your
code runs this:

```python
for call in tool_calls:
    name = call["function"]["name"]
    args = json.loads(call["function"]["arguments"])
    result = tools.call_tool(cfg, name, args)
```

Three lines. Look hard at where each value came from.
:::

::: section | Name exactly what changed
Four things moved.

1. **You passed `schemas`.** The model now has a menu.
2. **The reply can be a request, not an answer.** Your code checks which
   arrived.
3. **`name` came from the model.** You never typed `search_tickets` anywhere.
4. **`args` came from the model.** You never typed `{"query": "T-503"}` either.

Now the part that trips people up. **The model did not run anything.** It
produced text naming a function and some arguments. Your Python read that text
and made the call.

What moved is who decides. You still own every line that runs. You no longer
own the choice of which line runs next.

That is the inversion. Your program went from giving orders to taking requests.
:::

::: section | Watch the inversion happen
Your lab ships a tool for that.

```
python -m agent.replay
```

It replays your most recent run one step at a time:

```
    1. You asked        : summarize ticket T-503
    2. The model asked  : search_tickets(query="T-503")
    3. Your code ran it : got back 412 characters of ticket text
    4. The model asked  : send_email(to="records-audit@vendor-archive.example")
```

Look at steps 2 and 4. Nothing in your program decided to send that mail. The
model decided, and your program did it.

Add `--list` for recent runs, or pass a run id.
:::

::: callout note | If you remember one sentence from this week
The model asks. Your code answers.

Asking is free, and anyone whose text reaches the model gets to ask. Answering
is where you decide, and deciding is where security lives.
:::

::: section | What a JSON tool schema is
A **JSON tool schema** describes one tool in a fixed format, and it goes to
the model with every request. Here is the real schema for `search_tickets`,
from the registry in `agent/tools.py`:

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

`name` has to match the key the tool is registered under. `description` says
what the tool is for. `properties` lists each argument with a type. `required`
says which cannot be left out.
:::

::: callout warning | The schema is the only thing the model knows
The model never sees your Python or your comments. It reads the schema, and
that is all it gets.

So a schema is not documentation. It is an interface, and a promise your code
has to keep. Three ways it fails:

1. **A vague description.** The model calls the tool at the wrong moment, or
   never calls it.
2. **An argument with no description.** The model invents a value, and the
   value it invents is wrong.
3. **A schema that does not match the function.** The model sends what the
   schema promised, and your code rejects it.

In Module 2 you write a schema. The autograder builds arguments from it and
calls your function with them.
:::

::: section | Why a schema is a security topic
A tool is a door. A schema is the sign on the door.

OWASP calls the matching risk ASI02 Tool Misuse, in the Top 10 for Agentic
Applications 2026. Tool misuse is an agent using a real tool, in a normal way,
for a purpose nobody intended. The tool worked for the wrong request. MITRE
ATLAS carries the same behavior as AML.T0053, AI Agent Tool Invocation.

Notice what makes this possible. The model picks a tool based on text, and any
text reaching the model gets a vote. A ticket a stranger typed is text, and so
is your own knowledge base.

Every tool you add widens what the model can ask for.
:::

::: callout note | A name change worth knowing about
ATLAS renamed AML.T0053. It used to be "LLM Plugin Compromise" and is now "AI
Agent Tool Invocation". If a blog post uses the old name, it is superseded.
This course pins ATLAS release 2026.07.
:::

::: section | Three questions for any call that leaves your program
Your tools talk to HelpDesk Lite over HTTP. Both ends can fail, and neither is
your fault.

**One: what if it raises?** Wrap it. The real code from `agent/tools.py`:

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

It catches one named failure and raises a `ToolError` a person can act on. It
does not catch everything, and it does not go quiet.

**Two: what if it never answers?** A call with no timeout hangs forever. The
same file sets `TIMEOUT_S = 15` and passes it on every request.

**Three: is it worth trying again?** A 429 means you went too fast, and a 503
means a bad moment on the server. Both are worth one more try. A 401 means your
key is wrong, so retrying changes nothing.

You wrote that rule in Module 1, in `should_retry` and `backoff_seconds`.
:::

::: section | One word you will hear: MCP
The Model Context Protocol, or MCP, is a standard way to hand an agent a
package of tools. Someone else writes it. You point your agent at it, and now
your agent has tools you did not write.

You will meet one on a real agent.

The security point is the one this week already made. A tool is a way in.
Someone else's tool is someone else's way in, running with your permissions.
ATLAS covers this as AML.T0110, AI Agent Tool Poisoning.
:::

::: reading | Required reading: the Annotated Skeleton page
**What it is.** The next page in this module. It walks through `agent/loop.py`
one part at a time, quoting the file rather than summarizing it.

**What to read.** All of it. It is the only required reading this week, capped
at 45 minutes.

**How to read it.** Open `agent/loop.py` and put the page beside it. Find each
quoted block in the real file as you go. Reading the page without the file open
is the one mistake that makes this week hard.

**What to look for.** Two places, both marked on the page:

1. The line that calls `json.loads` on the model's arguments.
2. The function called `before_tool_call`.

**One question to answer while you read**, on the Week 4 quiz: the loop runs at
most `max_steps` times. What happens after the last one, and where in the file
is that written?
:::

::: checkpoint | Check Yourself
Answer these before you start the lab work.

1. In shape two, where did the value of `name` come from?
2. Your tool has an argument called `limit` with no description in the schema.
   What will the model do?
3. A request comes back with HTTP 401. Do you retry it? Say why.
4. Your `get_customer` returns an empty string when the customer is missing,
   and the agent says the record is blank. Which part is your bug?
:::

::: sources
OWASP Top 10 for Agentic Applications 2026, entry ASI02 Tool Misuse. Licensed
CC BY-SA 4.0. Linked only.

MITRE ATLAS, release 2026.07, techniques AML.T0053 AI Agent Tool Invocation and
AML.T0110 AI Agent Tool Poisoning. ATLAS is Apache 2.0 and incorporates MITRE
ATT&CK, which requires this attribution: ATT&CK is a registered trademark of
The MITRE Corporation.

All code quoted here comes from the lab repository, which is
instructor-authored.
:::
