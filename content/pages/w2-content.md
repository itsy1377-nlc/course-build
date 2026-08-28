::: intro
This page covers four things: loops and conditionals and functions, the exact
shape of a chat completions request, the exact shape of the reply, and why the
labs pin every package version. Read it before you start Module 1.
:::

::: section | Python part two, read from the lab code again
Three new pieces of Python this week. All three appear in one real function from
`verify_env.py`. Open the file and find it.

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
exactly what ships.

Read it one piece at a time.

**A function** starts with `def`. This one is named `check_packages`. It takes
nothing, and it hands back a `Check`. A function is a named block of steps you
can run whenever you want.

**A loop** starts with `for`. `for name in REQUIRED_PACKAGES:` runs the indented
lines once for each item in the list. The first time through, `name` holds
`"requests"`. The last time, it holds `"pytest"`.

**A conditional** starts with `if`. `if missing:` asks a yes or no question. An
empty list counts as no. A list with anything in it counts as yes.

**`return`** ends the function right there and hands a value back to whoever
called it. This function has two of them, and only one ever runs.

The `try` and `except` lines get their own section further down this page. For
now, read them as "try this, and if it breaks, do that instead."
:::

::: section | Just enough try and except for Module 1
Module 1 asks you to catch one error and raise a clearer one in its place. This
section teaches exactly that much and no more. Week 3 goes deeper.

**What `try` and `except` do.** Python normally stops a function the moment
something goes wrong. A `try` block says: run these lines, and expect trouble.
An `except` block says: if that trouble arrives, run these lines instead of
stopping.

```python
try:
    data = json.loads(text)
except json.JSONDecodeError:
    print("that was not valid JSON")
```

The `try` lines run first. If nothing goes wrong, the `except` block is skipped
completely.

**Catch one kind of error, not all of them.** The example above names
`json.JSONDecodeError`. That is the one error `json.loads` raises when the text
will not parse. Every other problem still stops the function, which is what you
want.

Now compare it to this:

```python
except Exception:
    print("something went wrong")
```

That catches everything, including bugs you have not found yet. A typo in a
variable name now prints "something went wrong" and the program carries on. You
will lose an evening to that.

Name the error you expect. Let the rest through.

**Raise a clearer error in place of a confusing one.** Catching is only half
the job. Whoever called your function still needs to know what happened.

```python
try:
    data = json.loads(text)
except json.JSONDecodeError as exc:
    raise LLMError(f"The model's reply was not valid JSON: {exc}") from exc
```

Three moves are in those three lines. `as exc` gives the original error a name.
`raise` sends up a new error with a message a person can act on. `from exc`
keeps the original attached, so the full traceback still shows the real cause.
:::

::: callout tip | Read the worked example in your own lab
Open `agent/llm.py` and find the function named `chat()`. Look for the block
that starts `except ValueError`.

It does all three moves at once. It catches one specific failure, the endpoint
answering 200 with a body that is not JSON. It raises `LLMError`. Its message
names the problem and shows the first 200 characters of what actually came
back.

That block is the pattern Module 1 asks you to write in `parse_json_content`.
Read it before you start step 4.

Week 3 returns to error handling and goes further. There you meet errors that
cross more than one function, and what an agent should do when a tool fails in
the middle of a run. This week is only the three moves above.
:::

::: section | The request: what you send
Every model you talk to in this course speaks the same shape, called the chat
completions API. Learn it once and it works everywhere.

You send one JSON object. Here is the real one, from `agent/llm.py`:

```python
payload = {
    "model": cfg.model.model,
    "messages": messages,
    "temperature": cfg.model.temperature,
    "max_tokens": cfg.model.max_tokens,
}
```

Four fields. Two of them matter now.

**`model`** is the name of the model you want, as a string. Different providers
use different names, which is why it comes from your settings file instead of
being written into the code.

**`messages`** is a list of dictionaries. This is the conversation. It is the
whole input the model gets.

**`temperature`** controls how much the answers vary. The labs set it to zero so
runs are as repeatable as possible.

**`max_tokens`** caps how long the answer may be.
:::

::: section | The messages list, and the thing to notice about it
A messages list looks like this:

```python
messages = [
    {"role": "system", "content": "You are the HelpDesk Lite assistant."},
    {"role": "user", "content": "Summarize ticket T-501."},
]
```

Each message is a dictionary with two keys. `role` says who is talking.
`content` is what they said.

There are four roles you will meet:

| Role | Who it is |
|---|---|
| `system` | Your instructions to the model |
| `user` | The person asking |
| `assistant` | The model's own earlier answers |
| `tool` | The result a tool handed back |

Now notice the thing that matters. All four roles arrive in **one list**, as
text, in one request. The role is a label on the text. It is not a wall around
it.

Your instructions and a stranger's ticket travel in the same box. Hold that
thought. Week 5 is built on it.
:::

::: section | Sending it
One line does the sending, using the `requests` library:

```python
response = requests.post(url, headers=headers, json=payload, timeout=60)
```

Four things go in:

1. **`url`** is your provider's address plus `/chat/completions`.
2. **`headers`** carries your API key, as `Authorization: Bearer` and then the
   key.
3. **`json=payload`** turns your dictionary into JSON text and sends it.
4. **`timeout=60`** gives up after 60 seconds instead of hanging forever.

Then one more line turns the reply back into a Python dictionary:

```python
data = response.json()
```

Those two lines are the entire network layer of this course. `agent/llm.py` is
the only file in your labs that makes an HTTP call to a model.
:::

::: reading | Reading: the Requests Quickstart
**What it is.** The documentation for `requests`, the one Python library your
labs use to talk to a model. It is short and it has runnable examples.

**What to read.** The Quickstart page, from the top through the parts on sending
a POST request and on reading a JSON response. Stop after that. Skip anything
about files, cookies, and redirects. Budget about 20 minutes.

**What to look for.** Three things:

1. The difference between `requests.get` and `requests.post`.
2. What passing `json=` to a request does for you, compared to building the text
   yourself.
3. What `response.json()` gives you back, and what type it is.

**One question to answer while you read**, which comes back on the quiz: your
request came back and you have a variable named `response`. What is the
difference between `response.text` and `response.json()`?

The link is on the Course Material page.
:::

::: section | The reply: what comes back
Here is a real reply, captured from the offline `mock` provider in your lab
repository. A real provider returns the same shape.

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

The model's actual answer is buried five levels down. Here is the path to it:

```python
text = response["choices"][0]["message"]["content"]
```

Walk it one step at a time, because you will do this a hundred times:

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
its sentence. You will see a different value in a moment.
:::

::: callout tip | When the path is wrong, the error names the step
Get one key wrong and Python raises a `KeyError` with the key it could not find.
Get the list index wrong and it raises an `IndexError`.

That is useful. Read the error, then print the piece one level up and look at
what is actually there.

`agent/llm.py` has a small function named `message_of` that does this lookup and
catches those errors. Read it. It is short, and it shows you the pattern.
:::

::: section | The tool call reply, and the one fact this week is built on
When the model wants a tool, the reply looks different. Here is a real one, from
the same offline provider:

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

Three changes from before.

**`content` is `null`.** In Python that becomes `None`. The model did not write
an answer, because it wants a tool first.

**`finish_reason` is `tool_calls`.** That is how your code knows to look for
one.

**`tool_calls` is a list.** The model can ask for more than one tool at a time.

Now the important part.
:::

::: callout warning | The arguments are a STRING of JSON, not a dictionary
This is the single most important line on this page:

```python
args = response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
```

Look at what `args` holds:

```python
print(type(args))
print(args)
```

```
<class 'str'>
{"query": "T-501"}
```

It **looks** like a dictionary. It is a string. Look at the raw JSON above and
you can see the quotes wrapped around the whole thing, with the inner quotes
escaped.

So this line fails:

```python
args["query"]
```

```
TypeError: string indices must be integers, not 'str'
```

You have to parse it first:

```python
import json
data = json.loads(args)
print(data["query"])
```

```
T-501
```

Only now is it a dictionary.
:::

::: section | Why that one line is a security lesson and not a trivia question
Somebody has to call `json.loads` on that string. In your labs that somebody is
you, in `agent/loop.py`.

Think about where the text inside that string came from. The model wrote it. The
model wrote it after reading whatever your last tool handed back, which may have
been a ticket a stranger typed.

So the arguments to your next tool call are text that untrusted content had a
hand in shaping. Your code then takes that text and runs a function with it.

You do not have to solve that this week. You do have to see it. Week 3 spends a
whole lab on that one line, and Week 5 shows you what happens when nobody
checks it.
:::

::: reading | Reading: the chat completions API reference
**What it is.** The vendor's reference page for the chat completions endpoint.
Every OpenAI-compatible provider copies this shape, which is why one lab works
against several providers.

**What to read.** The create chat completion reference entry, which is the page
at `chat/create`. Read the request body fields `model` and `messages`, then read
the example response. Budget about 15 minutes.

**Read the chat/create reference, not the newer function calling guide.** This
matters and it is not a style preference. That guide documents a different API
than the one every OpenAI-compatible endpoint actually implements. If you read
the guide and then call another provider, the shapes will not match, and you
will lose an evening to it. The reference page is the one that describes what
your labs send and receive.

**What to look for.** Three things:

1. Which fields are required and which have defaults.
2. The example response, and whether it matches the JSON on this page.
3. Where `tool_calls` sits in the reply.

**One question to answer while you read**, which comes back on the quiz: write
out the full chain of keys from the top of the reply down to the model's text,
the way this page did.

The link is on the Course Material page.
:::

::: section | Adding your API key
Do this on day 8 or day 9, not on day 14.

1. Copy `.env.example` to a new file named `.env`, in the same folder.
2. Open `.env`. Put your key after `LAB_API_KEY=`, with no quotes and no spaces.
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

`.env` is listed in `.gitignore`, so it is never committed. That is why your key
goes there.
:::

::: callout stop | Your key never goes in `lab.config.yaml`
`lab.config.yaml` is tracked by git. A key written there gets published the
moment you push.

`agent/config.py` scans that file for anything shaped like a credential and
refuses to start if it finds one. That check is a safety net, not permission to
be careless.

If you think your key leaked, turn it off at the provider, make a new one, and
tell your instructor. Nobody is in trouble for reporting this quickly.
:::

::: section | Why LAB_STUDENT_ID matters more than it looks
Setting `LAB_STUDENT_ID` is one line in a file, and it decides whether your
evidence is worth anything later.

Your labs contain **canary tokens**. A canary is a fake secret planted somewhere
it should never leave. If it turns up somewhere it does not belong, something
carried it there.

Your tokens are built from your student ID, so they are yours alone. That has a
practical result. A classmate can hand you a working attack, which is fine and
is how the field learns. They cannot hand you the proof that it worked in your
environment, because your proof contains your token.

If you leave the field blank, you get the shared demo ID and your evidence looks
identical to everyone else's. `verify_env.py` warns you about this. Fix it now,
not in Week 5.
:::

::: section | Why every version is pinned
Open the two requirements files in your lab repository and compare them.

`requirements.in` lists six packages by name, with a comment on each. That is
the file a person edits.

`requirements.txt` lists twenty-four packages with exact version numbers. That
file is generated, and you never edit it by hand. It holds the six you asked for
plus everything those six depend on.

Here is why that matters. When you run `pip install`, you download and run code
written by strangers on your own computer. Six of those strangers you chose.
Eighteen you have never heard of.

If somebody publishes a bad version of any one of them, an unpinned install
picks it up quietly. A pinned install keeps using the version that was checked.

This is one of the selected OWASP risks this course covers. It is
LLM04:2026, Supply Chain. It covers the whole chain a system depends on:
packages, models, and datasets.

That is why your lab requirements are pinned. It is also why the pins live in a
generated file you never edit by hand. And it is why this course names an exact
version for every framework it cites.
:::

::: checkpoint
Answer these for yourself before you start Module 1.

1. In `check_packages`, what is in the list named `missing` when everything is
   installed? What does `if missing:` decide in that case?
2. A messages list has a system message and a user message. What actually keeps
   them apart when the model reads them?
3. Write the full chain of keys that gets you the model's text out of a reply.
4. `args` holds the arguments of a tool call. What type is it, and what one line
   turns it into a dictionary?
5. Your provider returns HTTP 401. Should your code send the request again?
   Explain in one sentence.
:::

::: sources
Requests documentation, Quickstart page. The Requests project is licensed
Apache 2.0. Linked, not reproduced.

OpenAI chat completions API reference. Vendor documentation, linked only.

OWASP Top 10 for Large Language Model Applications 2026, entry LLM04 Supply
Chain. Licensed CC BY-SA 4.0. Linked, not reproduced.

The two JSON replies shown on this page were captured from the offline `mock`
provider in the lab repository, which is instructor-authored. A real provider
returns the same shape with different values.
:::
