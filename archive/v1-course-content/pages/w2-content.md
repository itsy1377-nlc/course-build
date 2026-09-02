::: intro
This page covers functions, loops, and conditionals, the shape of a chat
completions request and its reply, and why the labs pin every version. Read it
before Module 1.
:::

::: section | Python part two, read from the lab code
Three new pieces of Python appear in one function from `verify_env.py`. Open
it.

```python
def check_packages() -> Check:
    check = Check("Required packages")
    missing = []
    for name in REQUIRED_PACKAGES:
        try:
            __import__(name)
        except ImportError:
            missing.append(name)
    if missing:
        return check.fail(f"missing: {', '.join(missing)}", "Install everything.")
    return check.ok(f"all {len(REQUIRED_PACKAGES)} present")
```

The help text on the second to last line is shortened here.

- `def` names a block of steps you can run later.
- `for` runs the indented lines once per item.
- `if` asks a yes or no question. An empty list counts as no.
- `return` ends the function and hands back a value.
:::

::: section | Just enough try and except for Module 1
Module 1 asks you to catch one error and raise a clearer one in its place.

`try` says: run these lines, and expect trouble. `except` says: if that trouble
arrives, run these instead of stopping.

```python
try:
    data = json.loads(text)
except json.JSONDecodeError as exc:
    raise LLMError(f"The model's reply was not valid JSON: {exc}") from exc
```

**Catch one kind of error, not all of them.** `json.JSONDecodeError` is what
`json.loads` raises when text will not parse. `except Exception:` would swallow
bugs you have not found yet, including a typo.

**Then raise a clearer error.** `as exc` names the original. `raise` sends up a
new one a person can act on. `from exc` keeps the original attached, so the
traceback still shows the real cause.

For a worked example, read the `except ValueError` block in `agent/llm.py`.
:::

::: section | The request: what you send
Every model here speaks the chat completions shape. You send one JSON object,
built in `agent/llm.py`:

```python
    payload: dict[str, Any] = {
        "model": cfg.model.model,
        "messages": messages,
        "temperature": cfg.model.temperature,
        "max_tokens": cfg.model.max_tokens,
    }
```

`model` comes from your settings file. `messages` is the conversation, and the
whole input the model gets. `temperature` controls how much answers vary, and
the labs set zero. `max_tokens` caps the length.

One call to `_http.post` sends it, and it is the only HTTP call to a model in
your labs. It passes `timeout=float(cfg.model.timeout_s)`, which is 60, so the
call gives up instead of hanging.
:::

::: section | The messages list, and the thing to notice about it
A messages list looks like this:

```python
messages = [
    {"role": "system", "content": "You are the HelpDesk Lite assistant."},
    {"role": "user", "content": "Summarize ticket T-501."},
]
```

`role` says who is talking. `content` is what they said. Four roles exist:
`system` for your instructions, `user` for the person asking, `assistant` for
the model's earlier answers, and `tool` for a tool result.

Now notice the thing that matters. All four arrive in **one list**, as text, in
one request. Models are trained to weight these labels, and that helps. But a
label is a hint carried inside the text, not a wall around it, so it is not a
security boundary.

Your instructions and a stranger's ticket travel in the same box. Week 5 builds
on that.
:::

::: reading | Reading: the Requests Quickstart
**What it is.** The documentation for `requests`, the library your labs use to
talk to a model.

**What to read.** The Quickstart page, through sending a POST request and
reading a JSON response. Budget about 20 minutes.

**What to look for.** Three things:

1. The difference between `requests.get` and `requests.post`.
2. What passing `json=` does for you.
3. What `response.json()` gives back, and what type it is.

**One question to answer while you read**, on the quiz later: how do
`response.text` and `response.json()` differ?

The link is on the Course Material page.
:::

::: section | The reply: what comes back
A reply, with `id`, `model`, and `usage` left out:

```json
{
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "What do you need?"},
      "finish_reason": "stop"
    }
  ]
}
```

The answer sits four levels down. You will write this chain a hundred times:

```python
text = response["choices"][0]["message"]["content"]
```

`choices` is a list because the API can return more than one answer. Here it
always returns one, so the index is always `0`. `finish_reason` says why the
model stopped, and `stop` means it finished its sentence.

`agent/llm.py` has a function named `message_of` that does this lookup and
catches a bad key.
:::

::: section | The tool call reply, and the one fact this week is built on
When the model wants a tool, the message looks different:

```json
"message": {
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_7a9c9d2c44",
      "type": "function",
      "function": {"name": "search_tickets", "arguments": "{\"query\": \"T-501\"}"}
    }
  ]
}
```

`content` is `null`, because the model wants a tool first. `finish_reason`
becomes `tool_calls`. And `tool_calls` is a list, because the model can ask for
several at once.
:::

::: callout warning | The arguments are a STRING of JSON, not a dictionary
This is the most important line on this page:

```python
args = message["tool_calls"][0]["function"]["arguments"]
```

`args` **looks** like a dictionary. It is a string. In the raw JSON above you
can see quotes around the whole thing, with the inner quotes escaped. So
`args["query"]` raises `TypeError`. Parse it first with `json.loads(args)`.

In your labs the code that parses it is yours, in `agent/loop.py`. The model
wrote that string after reading whatever your last tool returned, which may
have been a ticket a stranger typed. Week 3 spends a lab here.
:::

::: reading | Reading: the chat completions API reference
**What it is.** The vendor's reference for this endpoint. Every
OpenAI-compatible provider copies the shape, which is why one lab works against
several.

**What to read.** The create chat completion entry, at `chat/create`. Read the
fields `model` and `messages`, then the example response. Budget 15 minutes.
Read that entry, not the newer function calling guide, which documents a
different API.

**What to look for.** Three things:

1. Which fields are required and which have defaults.
2. Whether the example response matches the JSON above.
3. Where `tool_calls` sits in the reply.

**One question to answer while you read**, on the quiz later: write out the
full chain of keys down to the model's text.

The link is on the Course Material page.
:::

::: section | Adding your API key
Do this on day 8 or 9, not on day 14.

1. Copy `.env.example` to a new file named `.env`, in the same folder.
2. In `.env`, put your key after `LAB_API_KEY=`, with no quotes or spaces.
3. On the `LAB_STUDENT_ID=` line, put your college ID.
4. In `config/lab.config.yaml`, change `provider: mock` to
   `provider: openai_compatible`, then set `base_url` and `model`. The Course
   Material page lists both for each provider.
5. Run the check with a real request:

```
python verify_env.py --live
```

6. Paste the second code, ending `-L`, into the Module 0 Gate.
:::

::: callout stop | Your key never goes in `lab.config.yaml`
`lab.config.yaml` is tracked by git, so a key written there is published the
moment you push. `.env` is in `.gitignore`, which is why your key goes there.

`agent/config.py` scans the config file for anything shaped like a credential
and refuses to start if it finds one. That is a safety net, not permission to
be careless.

If a key leaks, turn it off at the provider and tell your instructor.
:::

::: section | Why LAB_STUDENT_ID matters more than it looks
Your labs contain **canary tokens**: fake secrets planted where they should
never leave. Yours are built from your student ID, so they are yours alone.

A classmate can hand you a working attack, but not the proof it worked in your
environment. Your proof holds your token.
:::

::: section | Why every version is pinned
Compare the two requirements files in your lab repository.

`requirements.in` lists six packages by name, and a person edits it.
`requirements.txt` lists twenty-four with exact versions. It is generated, and
you never edit it by hand.

`pip install` downloads and runs code written by strangers. Six of them you
chose. Eighteen you have never heard of. If somebody publishes a bad version of
any one, an unpinned install picks it up quietly.

That is LLM04:2026, Supply Chain, one of the selected OWASP risks this course
covers.
:::

::: checkpoint
Answer these before you start Module 1.

1. In `check_packages`, what is in `missing` when everything is installed, and
   what does `if missing:` decide then?
2. A messages list has a system message and a user message. What actually keeps
   them apart when the model reads them?
3. Write the full chain of keys that gets the model's text out of a reply.
4. `args` holds a tool call's arguments. What type is it, and what line turns
   it into a dictionary?
5. Your provider returns HTTP 401. Should your code retry? One sentence.
:::

::: sources
Requests documentation, Quickstart page. Licensed Apache 2.0. Linked only.

OpenAI chat completions API reference. Vendor documentation, linked only.

OWASP Top 10 for Large Language Model Applications 2026, entry LLM04 Supply
Chain. Licensed CC BY-SA 4.0. Linked, not reproduced.

The JSON here was captured from the offline `mock` provider, which is
instructor-authored.
:::
