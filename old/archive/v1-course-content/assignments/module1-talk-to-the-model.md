::: intro
Complete three small functions in `agent/llm.py` so your model client survives a
rate limit and reads a structured reply. Everything else in that file already
works.
:::

::: video module1-walkthrough | The tests are the assignment
Three minutes at the terminal. It shows the tool that grades you, and never
opens the file you are writing.
:::

::: callout note | These tests run offline
Nothing in this assignment needs a network or an API key. The three functions
are pure logic, so pytest checks them with no requests at all.

You still need your key working for the rest of Week 2.
:::

::: directions
**Step 1: find the work.**

Open `agent/llm.py` and look for the banner `EXTENSION POINT 3 of 5`. Three
functions sit under it. Read all three docstrings before you write anything.

**Step 2: write `should_retry(status_code)`.**

It takes an HTTP status code and answers one question: is this request worth
sending again?

Some failures clear on their own, such as a busy server or too many requests.
Others never clear, because the request itself was wrong. The docstring lists
which codes fall in which group. Turn that list into a rule, and return a real
`True` or `False`.

**Step 3: write `backoff_seconds(attempt)`.**

It takes an attempt number, counting from 1, and returns how many seconds to
wait. Three rules:

1. **Never return zero.** A wait of zero is not a wait.
2. **Grow.** Wait 3 must be longer than wait 1, or a rate limit never gets a
   chance to clear.
3. **Have a ceiling.** The tests check that attempt 20 waits 60 seconds or
   less.

**Step 4: write `parse_json_content(text)`.**

Read the section **Just enough try and except for Module 1** on the Week 2
content page first. It teaches the three moves this step needs, and it points
you at a worked example inside `agent/llm.py`.

The function takes the text of a model's reply and returns a dictionary. Models
are asked for JSON and do not always deliver it. Four rules:

1. Valid JSON describing a dictionary: return the dictionary.
2. Anything else: raise `LLMError` with a message a person could act on.
3. Never let a raw `json.JSONDecodeError` reach your caller.
4. Valid JSON is not the same as the right shape. `["a", "b"]` parses fine and
   is a list. Reject it, and reject an empty string.

`LLMError` is already defined at the top of the file.

**Step 5: check your work.**

```
python -m pytest tests/test_module1.py -q
```

Run it as often as you like before the deadline. Then open
`tests/test_module1.py` and read it. It is the clearest statement of what is
expected, and reading it is the job.

**Step 6: save your proof.**

When every test passes, run it once more and save the output:

```
python -m pytest tests/test_module1.py -q > module1-pytest.txt
```

Open that file and check that it is not empty.
:::

::: callout warning | The mistake that costs real money
Write `should_retry` so it returns `True` for 4xx codes and nothing crashes.

Then a 401 arrives, which means your key is not accepted. Your loop retries. It
retries again. Every attempt counts against your provider's daily limit, so you
burn the whole quota in about four seconds on a request that could never
succeed.

Then you are locked out until tomorrow, and your assignment is due tonight.
:::

::: callout tip | If you get stuck
1. Run the tests before writing anything. Read which ones fail.
2. Do `should_retry` first. It is the smallest.
3. Print things. `print(status_code)` shows what the function receives.
4. Paste the test name and the message on the Q and A board. Do not paste your
   answer.
:::

::: submit
Upload two files: your modified `agent/llm.py`, and your saved pytest output
named `module1-pytest-<your last name>.txt`.

Do not upload the whole repository, and never upload your `.env` file.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
