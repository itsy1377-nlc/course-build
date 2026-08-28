::: intro
This is Project 1. It has two parts and one deadline.

Part one is `get_customer`, whose schema is already written for you. Part two
is one tool of your own design, with a schema you write yourself.

The schema is the graded part of part two. The Python in it is small.
:::

::: callout note | What you are being graded on
Writing a function is Week 4 work and you have done it before.

Writing an interface that another program has to understand from the
description alone is new. That is what part two is, and it is where the points
are.
:::

::: directions
**Before you start.** Get the target app running and leave it running:

```
python -m target.seed
python -m target.app
```

Check your work at any point with:

```
python -m pytest tests/test_module2.py -q
```

Run that as often as you like. It is the same tool that grades you.

---

**PART ONE: finish `get_customer`.**

**Step 1. Read what is already there.**

Open `agent/tools.py` and find `EXTENSION POINT 2`. The comment block above the
function tells you what it has to do. The schema below it, in `TOOLS`, is
already written.

Read `search_tickets`, higher up the same file. Your function has the same
shape: call the `_get` helper, then build a readable string out of what comes
back.

**Step 2. Write the success path.**

The target app serves customer records at `/api/customers/` followed by the
customer ID. C-1002 is a real customer, so use that one while you work.

Return a string a person could read. The record has a name, an email, a phone
number, an address, a plan, and an account note. A wall of raw JSON is not a
readable summary.

Check it:

```
python -m pytest tests/test_module2.py -q -k right_record
```

**Step 3. Write the error path.**

This is half the assignment, and it is the half students skip.

Run this and read what it asks for:

```
python -m pytest tests/test_module2.py -q -k does_not_exist
```

The tests want three things when a customer ID does not exist:

1. A `ToolError` is raised, not returned.
2. The message is not empty.
3. The message names the lookup that failed, so the agent can tell the user
   something useful.

Read `_get` again before you write anything. It already raises a `ToolError`
when the target answers 404. Decide for yourself whether the message it raises
meets those three requirements. If it does not, catch it and raise a better
one.

---

**PART TWO: design one tool of your own.**

**Step 4. Pick something the target app can actually do.**

Open `target/app.py` and read the list of routes. Your tool has to use a route
that exists.

Four ideas that work:

- Look up one ticket by ID and return only its subject and status.
- List what is sitting in the outbox.
- Return the most recent entries from the audit log.
- Count tickets by status, and return the counts.

Pick one. One good tool beats three vague ones.

Use the `_get` helper so that your tool makes a real HTTP call. One of the
written answers in step 9 is about what happens when that call fails, and you
cannot answer it about a tool that never leaves your program.

The last idea is the one named in the comment in `tools.py`, so it is the
safest choice and also the most common one. Either is fine. You are graded on
the schema you write, not on which idea you picked.

**Step 5. Write the function.**

Put it below `EXTENSION POINT 4` in `agent/tools.py`. Give it the same shape as
the shipped tools: `cfg` first, then your arguments, and a string comes back.

Handle its failure the way you handled `get_customer`. Raise `ToolError` with a
message. Never return an empty string.

**Step 6. Write the schema. This is the graded part.**

Write the schema yourself. Do not copy one and change the name.

Your schema needs:

- A `name` that exactly matches the key you register it under.
- A `description` that says what the tool does and when to use it. One vague
  sentence is not enough. The model has nothing else to go on.
- Every argument in `properties`, each with a `type` and a `description`.
- A `required` list naming the arguments that cannot be left out.

**Step 7. Register it in two places.**

First, add it to `TOOLS` in `agent/tools.py`, with its `fn` and its `schema`.
The commented example at the bottom of `TOOLS` shows the shape.

Second, add its name to `agent.allowed_tools` in `config/lab.config.yaml`. Miss
this and the model is never told your tool exists.

**Step 8. Make the agent actually call it.**

Run the agent and ask for something your tool is the right answer to:

```
python -m agent.cli "your request here"
```

Save the terminal output. That is your run transcript.

If the model never picks your tool, the description is usually why. Say more
clearly what the tool is for and try again.

---

**Step 9. Write the short answers.**

Create a file called `ANSWERS.md`. Answer three questions about your own tool,
in two or three sentences each.

1. What does your tool do?
2. What does it refuse to do?
3. What happens when the underlying HTTP call errors? Trace it: your function,
   then `call_tool`, then the loop, then the model.

**Step 10. Write `AI-USE.md`.**

Document at least one AI suggestion you **rejected**, and why you rejected it.

Include the suggestion itself and your reason. "It was wrong" is not a reason.
"It caught every exception, which would have hidden the missing customer case"
is a reason.

This is graded on the rejection, not on the amount of AI you used. AI use is
permitted in this course and it has to be declared.
:::

::: callout warning | The three failures that cost the most points
**A schema that lies about the function.** The autograder builds arguments from
your own schema and calls your function with them. If your schema says
`limit` is an integer and your function expects a string, that fails. Read your
schema back against your function signature before you submit.

**A tool registered but not allowed.** `TOOLS` and `agent.allowed_tools` are
two different lists. Both need your tool's name.

**An empty string on failure.** A tool that returns `""` when something goes
wrong is worse than a tool that is missing. The agent carries on as if it
worked, and the log agrees with it.
:::

::: submit
Upload one zip file named `module2-<your last name>.zip`.

It contains exactly five things:

1. Your `agent/tools.py`
2. Your `config/lab.config.yaml`
3. Your run transcript, as a text file
4. `ANSWERS.md`
5. `AI-USE.md`

Do not include your `.env` file. Do not include `runs/`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
