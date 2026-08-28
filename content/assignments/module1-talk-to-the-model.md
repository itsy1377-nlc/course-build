::: intro
Complete three small functions in `agent/llm.py` so your model client survives a
rate limit and reads a structured reply.

You do not write a file from scratch. Everything else in `agent/llm.py` already
works. You fill in three marked bodies.
:::

::: callout note | These tests run offline
Nothing in this assignment needs a network or an API key. The three functions
are pure logic, so pytest checks them with no requests at all.

You still need your key working for the rest of Week 2, and the Module 0 Gate
still wants your live code. That is separate from this assignment.
:::

::: directions
**Step 1: find the work.**

Open `agent/llm.py`. Look for this banner:

```
EXTENSION POINT 3 of 5   (Module 1: Talk to the Model)
```

Three functions sit under it. Each one has a docstring that tells you what it
must do. Read all three docstrings before you write anything.

**Step 2: write `should_retry(status_code)`.**

This function takes an HTTP status code and returns `True` or `False`. It
answers one question: is this request worth sending again?

Some failures clear on their own. The server was busy, or you sent requests too
fast. Waiting a moment and trying again can work. Those are worth a retry.

Other failures never clear. Your request itself was wrong, or your key is not
allowed, or the address does not exist. Sending the same request again produces
the same failure every time.

The docstring lists which codes fall in which group. Your job is to turn that
list into a rule. Return a real `True` or a real `False`, not a number and not a
string.

**Step 3: write `backoff_seconds(attempt)`.**

This function takes an attempt number, counting from 1, and returns how many
seconds to wait before that attempt.

Three things it must do:

1. **Never return zero.** A wait of zero is not a wait.
2. **Grow.** Wait number 3 must be longer than wait number 1. If you wait the
   same short time over and over, a rate limit never gets a chance to clear.
3. **Have a ceiling.** Without a cap, attempt 20 waits for many minutes and your
   run looks frozen. The tests check that attempt 20 waits 60 seconds or less.

Return a number. It may have a decimal part.

**Step 4: write `parse_json_content(text)`.**

This step needs `try` and `except`. Read the section named **Just enough try
and except for Module 1** on the Week 2 content page before you start. It
teaches the three moves this step needs, and it points you at a worked example
inside `agent/llm.py`. Week 3 goes further with error handling. You do not need
that yet.

This function takes the text of a model's reply and returns a dictionary.

Models are asked for JSON and do not always deliver it. Sometimes you get clean
JSON. Sometimes you get an apology and no JSON at all. Sometimes you get an
empty string. Your function has to handle all of it.

Four rules:

1. When `text` is valid JSON describing a dictionary, return the dictionary.
2. When it is not, raise `LLMError` with a message a person could act on.
3. Never let a raw `json.JSONDecodeError` escape to whoever called you. Catch it
   and raise `LLMError` instead.
4. Valid JSON is not the same as the right shape. `["a", "b"]` parses fine and
   is a list, not a dictionary. Reject it. An empty string is an error too, not
   an empty dictionary.

`LLMError` is already defined at the top of the same file. You do not create it.

**Step 5: check your work.**

```
python -m pytest tests/test_module1.py -q
```

Run it as many times as you want before the deadline. The tests are the same
ones the grader uses. Each failure message tells you which rule was broken.

Open `tests/test_module1.py` and read it. It is short, and it is the clearest
statement of what is expected. Reading the test is not cheating. It is the job.

**Step 6: save your proof.**

When every test passes, run it one more time and save the output:

```
python -m pytest tests/test_module1.py -q > module1-pytest.txt
```

Open that file and check that it is not empty.
:::

::: callout warning | The mistake that costs real money
Write `should_retry` so it returns `True` for 4xx codes and everything looks
fine. The code runs. Nothing crashes.

Then think about what happens on a 401, which means your key is not accepted.
Your loop retries. The key is still not accepted. It retries again.

Every one of those attempts counts against your provider's daily limit. You burn
your whole quota on a request that could never succeed, and you do it in about
four seconds.

Then you are locked out until tomorrow, and your assignment is due tonight.

This is not a made-up example. A retry loop that retries on 4xx is one of the
defect classes the AI Code Audit exercises use later in the course, because it
is exactly the kind of bug that looks correct.
:::

::: callout tip | If you get stuck
Work in this order.

1. Run the tests first, before writing anything. Read which ones fail.
2. Do `should_retry` first. It is the smallest.
3. Print things. `print(status_code)` inside the function tells you what it is
   actually receiving.
4. If a test message does not make sense, paste the test name and the message on
   the Q and A board. Do not paste your answer.
:::

::: submit
Upload two files.

1. Your modified `agent/llm.py`. Keep the filename `llm.py`.
2. Your saved pytest output, named `module1-pytest-<your last name>.txt`.

Do not upload the whole repository, and do not upload your `.env` file. Your
`.env` file holds your API key.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
