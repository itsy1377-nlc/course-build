::: intro
This page covers four things: functions, loops, and conditionals; the exact
shape of a chat completions request; the exact shape of the reply; and why the
labs pin every package version. Read it before Module 1.
:::

::: section | Python part two, read from the lab code
Three new pieces of Python appear in one real function from `verify_env.py`.
Open the file and find it.

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

The help text on the second to last line is shortened here. Everything else is
what ships.

| Keyword | What it does here |
|---|---|
| `def` | Names a block of steps you can run later. This one is `check_packages` |
| `for` | Runs the indented lines once per item. `name` holds `"requests"`, then the rest |
| `if` | Asks a yes or no question. An empty list counts as no |
| `return` | Ends the function and hands a value back. Two are written, one ever runs |
:::

::: section | Just enough try and except for Module 1
Module 1 asks you to catch one error and raise a clearer one in its place.

A `try` block says: run these lines, and expect trouble. An `except` block
says: if that trouble arrives, run these instead of stopping.

```python
try:
    data = json.loads(text)
except json.JSONDecodeError:
    print("that was not valid JSON")
```

**Catch one kind of error, not all of them.** The example names
`json.JSONDecodeError`, which is what `json.loads` raises when text will not
parse. Every other problem still stops the function, which is what you want.

Writing `except Exception:` instead catches everything, including bugs you have
not found yet. A typo in a variable name now prints a shrug and the program
carries on. You will lose an evening to that.

**Raise a clearer error in place of a confusing one.** Catching is half the
job. Your caller still needs to know what happened.

```python
try:
    data = json.loads(text)
except json.JSONDecodeError as exc:
    raise LLMError(f"The model's reply was not valid JSON: {exc}") from exc
```

`as exc` names the original error. `raise` sends up a new one with a message a
person can act on. `from exc` keeps the original attached, so the traceback
still shows the real cause.
:::

::: callout tip | Read the worked example in your own lab
Open `agent/llm.py`, find `chat()`, and look for the block starting
`except ValueError`.

It does all three moves at once. It catches one specific failure, the endpoint
answering 200 with a body that is not JSON. It raises `LLMError`. Its message
names the problem and shows the first 200 characters of what came back.

That block is the pattern Module 1 asks you to write in `parse_json_content`.
:::

::: section | The request: what you send
Every model in this course speaks the same shape, called the chat completions
API. Learn it once and it works everywhere.

You send one JSON object. This is the real one, from `agent/llm.py`:

```python
    payload: dict[str, Any] = {
        "model": cfg.model.model,
        "messages": messages,
        "temperature": cfg.model.temperature,
        "max_tokens": cfg.model.max_tokens,
    }
```

| Field | What it holds |
|---|---|
| `model` | The model name, as a string. It comes from your settings file |
| `messages` | A list of dictionaries. This is the whole input the model gets |
| `temperature` | How much answers vary. The labs set zero, for repeatable runs |
| `max_tokens` | A cap on how long the answer may be |
:::

::: section | The messages list, and the thing to notice about it
A messages list looks like this:

```python
messages = [
    {"role": "system", "content": "You are the HelpDesk Lite assistant."},
    {"role": "user", "content": "Summarize ticket T-501."},
]
```

Each message is a dictionary with two keys. `role` says who is talking, and
`content` is what they said.

| Role | Who it is |
|---|---|
| `system` | Your instructions to the model |
| `user` | The person asking |
| `assistant` | The model's own earlier answers |
| `tool` | The result a tool handed back |

Now notice the thing that matters. All four roles arrive in **one list**, as
text, in one request. Models are trained to weight these labels, and that
training helps. But the label is a hint carried inside the text, not a wall
around it, so it is not a security boundary.

Your instructions and a stranger's ticket travel in the same box. Week 5 is
built on that.
:::

::: section | Sending it
One line does the sending, using the `requests` library:

```python
            response = _http.post(
                url,
                headers=headers,
                json=payload,
                timeout=float(cfg.model.timeout_s),
            )
```

`url` is your provider's address plus `/chat/completions`. `headers` carries
your API key. `json=payload` turns your dictionary into JSON text.
`timeout_s` is 60 in `config/lab.config.yaml`, so the call gives up rather than
hanging forever.

Then `response.json()` turns the reply back into a Python dictionary.
`agent/llm.py` is the only file in your labs that makes an HTTP call to a
model.
:::

::: reading | Reading: the Requests Quickstart
**What it is.** The documentation for `requests`, the one Python library your
labs use to talk to a model. It is short and has runnable examples.

**What to read.** The Quickstart page, from the top through the parts on
sending a POST request and reading a JSON response. Stop there. Budget about 20
minutes.

**What to look for.** Three things:

1. The difference between `requests.get` and `requests.post`.
2. What passing `json=` does for you, compared to building the text yourself.
3. What `response.json()` gives you back, and what type it is.

**One question to answer while you read**, which comes back on the quiz: your
request came back and you have a variable named `response`. What is the
difference between `response.text` and `response.json()`?

The link is on the Course Material page.
:::

::: section | The reply: what comes back
Here is a reply captured from the offline `mock` provider in your lab. A real
provider returns the same shape.

```json
{
  "id": "mock-cf85742b6411",
  "object": "chat.completion",
  "model": "mock/qwen3:1.7b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I am the HelpDesk Lite assistant. What do you need?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
}
```

The model's answer is buried five levels down:

```python
text = response["choices"][0]["message"]["content"]
```

| Step | What you have now |
|---|---|
| `response` | a dictionary |
| `response["choices"]` | a list |
| `response["choices"][0]` | the first item, a dictionary |
| `["message"]` | a dictionary |
| `["content"]` | a string, at last |

`choices` is a list because the API can return more than one answer. In this
course it always returns one, so the index is always `0`.

**`finish_reason`** tells you why the model stopped. `stop` means it finished
its sentence.
:::

::: callout tip | When the path is wrong, the error names the step
Get one key wrong and Python raises a `KeyError` naming the key it could not
find. Get the list index wrong and it raises an `IndexError`.

Read the error, then print the piece one level up and look at what is there.

`agent/llm.py` has a short function named `message_of` that does this lookup
and catches those errors. Read it.
:::

::: section | The tool call reply, and the one fact this week is built on
When the model wants a tool, the reply looks different:

```json
{
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_7a9c9d2c44",
            "type": "function",
            "function": {
              "name": "search_tickets",
              "arguments": "{\"query\": \"T-501\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

Three changes. **`content` is `null`**, which becomes `None` in Python, because
the model wants a tool before it writes an answer. **`finish_reason` is
`tool_calls`**, which is how your code knows to look. And **`tool_calls` is a
list**, because the model can ask for more than one tool at a time.
:::

::: callout warning | The arguments are a STRING of JSON, not a dictionary
This is the most important line on this page:

```python
args = response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
```

`args` **looks** like a dictionary. It is a string. Look at the raw JSON above
and you can see the quotes wrapped around the whole thing, with the inner
quotes escaped.

So `args["query"]` fails:

```
TypeError: string indices must be integers, not 'str'
```

You have to parse it first:

```python
data = json.loads(args)
print(data["query"])
```

Only now is it a dictionary, and only now does `data["query"]` give you
`T-501`.
:::

::: section | Why that one line is a security lesson
Somebody has to call `json.loads` on that string. In your labs that somebody is
you, in `agent/loop.py`.

Think about where the text inside the string came from. The model wrote it,
after reading whatever your last tool handed back, which may have been a ticket
a stranger typed.

So the arguments to your next tool call are text that untrusted content had a
hand in shaping. Your code then runs a function with it.

You do not have to solve that this week. You do have to see it. Week 3 spends a
whole lab on that line.
:::

::: reading | Reading: the chat completions API reference
**What it is.** The vendor's reference page for the chat completions endpoint.
Every OpenAI-compatible provider copies this shape, which is why one lab works
against several providers.

**What to read.** The create chat completion reference entry, at `chat/create`.
Read the request body fields `model` and `messages`, then read the example
response. Budget about 15 minutes.

**Read that reference, not the newer function calling guide.** The guide
documents a different API than the one OpenAI-compatible endpoints implement.
Read it and call another provider, and the shapes will not match.

**What to look for.** Three things:

1. Which fields are required and which have defaults.
2. The example response, and whether it matches the JSON on this page.
3. Where `tool_calls` sits in the reply.

**One question to answer while you read**, which comes back on the quiz: write
out the full chain of keys from the top of the reply down to the model's text.

The link is on the Course Material page.
:::

::: section | Adding your API key
Do this on day 8 or day 9, not on day 14.

1. Copy `.env.example` to a new file named `.env`, in the same folder.
2. Open `.env`. Put your key after `LAB_API_KEY=`, with no quotes and no
   spaces.
3. On the `LAB_STUDENT_ID=` line, put your college ID.
4. Open `config/lab.config.yaml`. Change `provider: mock` to
   `provider: openai_compatible`.
5. In that same file, set `base_url` and `model` for your provider. The Course
   Material page lists the settings for each one.
6. Run the check with a real request:

```
python verify_env.py --live
```

7. It prints a second code, ending in `-L`. Paste that into the Module 0 Gate.
:::

::: callout stop | Your key never goes in `lab.config.yaml`
`lab.config.yaml` is tracked by git. A key written there gets published the
moment you push. `.env` is listed in `.gitignore`, which is why your key goes
there.

`agent/config.py` scans the config file for anything shaped like a credential
and refuses to start if it finds one. That check is a safety net, not
permission to be careless.

If you think your key leaked, turn it off at the provider, make a new one, and
tell your instructor. Nobody is in trouble for reporting this quickly.
:::

::: section | Why LAB_STUDENT_ID matters more than it looks
Your labs contain **canary tokens**. A canary is a fake secret planted
somewhere it should never leave. If it turns up somewhere it does not belong,
something carried it there.

Your tokens are built from your student ID, so they are yours alone. A
classmate can hand you a working attack, which is fine and is how the field
learns. They cannot hand you the proof it worked in your environment, because
your proof contains your token.

Leave the field blank and you get the shared demo ID, and your evidence looks
identical to everyone else's. Fix it now, not in Week 5.
:::

::: section | Why every version is pinned
Open the two requirements files in your lab repository and compare them.

`requirements.in` lists six packages by name, with a comment on each. That is
the file a person edits.

`requirements.txt` lists twenty-four packages with exact version numbers. It is
generated, and you never edit it by hand. It holds the six you asked for plus
everything those six depend on.

When you run `pip install`, you download and run code written by strangers. Six
of those strangers you chose. Eighteen you have never heard of. If somebody
publishes a bad version of any one of them, an unpinned install picks it up
quietly.

This is one of the selected OWASP risks this course covers: LLM04:2026, Supply
Chain. It covers the whole chain a system depends on, including packages,
models, and datasets. It is also why this course names an exact version for
every framework it cites.
:::

::: checkpoint
Answer these before you start Module 1.

1. In `check_packages`, what is in the list named `missing` when everything is
   installed? What does `if missing:` decide then?
2. A messages list has a system message and a user message. What actually keeps
   them apart when the model reads them?
3. Write the full chain of keys that gets the model's text out of a reply.
4. `args` holds the arguments of a tool call. What type is it, and what one
   line turns it into a dictionary?
5. Your provider returns HTTP 401. Should your code send the request again?
   Explain in one sentence.
:::

::: sources
Requests documentation, Quickstart page. The Requests project is licensed
Apache 2.0. Linked, not reproduced.

OpenAI chat completions API reference. Vendor documentation, linked only.

OWASP Top 10 for Large Language Model Applications 2026, entry LLM04 Supply
Chain. Licensed CC BY-SA 4.0. Linked, not reproduced.

The two JSON replies shown here were captured from the offline `mock` provider
in the lab repository, which is instructor-authored.
:::
