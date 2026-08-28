::: intro
This is Project 1. Part one is `get_customer`, whose schema is already written
for you. Part two is one tool of your own design, with a schema you write
yourself.

The schema is the graded part of part two. The Python in it is small.
:::

::: callout note | What you are being graded on
Writing a function is Week 4 work. Writing an interface another program has to
understand from the description alone is new, and that is where the points are.
:::

::: directions
Start the target app and leave it running, the way the lab README describes.
Check your work at any point with:

```
python -m pytest tests/test_module2.py -q
```

It is the same tool that grades you.

**PART ONE: finish `get_customer`.**

**Step 1. Read what is already there.** Open `agent/tools.py` and find
`EXTENSION POINT 2`. The comment above says what the function has to do, and
the schema below it is written. Read `search_tickets` higher up: yours has the
same shape.

**Step 2. Write the success path.** The target app serves customer records at
`/api/customers/` followed by the customer ID. C-1002 is a real customer.
Return a string a person could read, not a wall of raw JSON.

**Step 3. Write the error path.** This is half the assignment, and the half
students skip. Read `_get` again first. It already raises a `ToolError`
when the target answers 404. Decide whether that message names the lookup that
failed. If it does not, catch it and raise a better one.

**PART TWO: design one tool of your own.**

**Step 4. Pick something the target app can do.** Open `target/app.py` and read
the routes. Four ideas that work:

- Look up one ticket by ID and return its subject and status.
- List what is sitting in the outbox.
- Return the most recent entries from the audit log.
- Count tickets by status.

Use the `_get` helper so your tool makes a real HTTP call. Step 9 asks what
happens when that call fails.

**Step 5. Write the function.** Put it below `EXTENSION POINT 4` in
`agent/tools.py`, shaped like the shipped tools: `cfg` first, then your
arguments, and a string comes back. Raise `ToolError` on failure. Never return
an empty string.

**Step 6. Write the schema. This is the graded part.** Write it yourself rather
than copying one and changing the name. It needs a `name` matching the key you
register it under. The `description` says what the tool does and when to use
it. Every argument goes in `properties` with a `type` and a `description`, and
`required` names the ones that cannot be left out. The model has nothing else
to go on.

**Step 7. Register it in two places.** Add it to `TOOLS` in `agent/tools.py`
with its `fn` and its `schema`. Then add its name to `agent.allowed_tools` in
`config/lab.config.yaml`.

**Step 8. Make the agent call it.**

```
python -m agent.cli "your request here"
```

Save the terminal output as your run transcript. If the model never picks your
tool, the description is usually why.

**Step 9. Write `ANSWERS.md`.** Two or three sentences each:

1. What does your tool do?
2. What does it refuse to do?
3. What happens when the underlying HTTP call errors? Trace it: your function,
   then `call_tool`, then the loop, then the model.

**Step 10. Write `AI-USE.md`.** Document at least one AI suggestion you
**rejected**, with the suggestion itself and your reason. "It was wrong" is not
a reason. "It caught every exception, which would have hidden the missing
customer case" is a reason.
:::

::: callout warning | The three failures that cost the most points
**A schema that lies about the function.** The autograder builds arguments from
your schema and calls your function. Read the schema back against your function
signature before you submit.

**A tool registered but not allowed.** `TOOLS` and `agent.allowed_tools` are
two different lists. Both need your tool's name.

**An empty string on failure.** The agent carries on as if the call worked, and
the log agrees with it.
:::

::: submit
Upload one zip file named `module2-<your last name>.zip`. It holds five things:
your `agent/tools.py`, your `config/lab.config.yaml`, your run transcript as a
text file, `ANSWERS.md`, and `AI-USE.md`.

Do not include your `.env` file or `runs/`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
