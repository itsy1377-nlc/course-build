::: intro
This page covers three things: what an agentic system is, why it fails
differently from ordinary software, and enough Python to read the lab code.
Read it before you start Lab 1. It takes about 45 minutes.
:::

::: section | Three words, in order
Almost everything in this course is built from three ideas.

**A model** reads text and produces text. That is all it does. It cannot open a
file. It cannot send mail. It cannot reach your database.

**A tool** is an ordinary function somebody wrote. It can do all three. There
is nothing clever about a tool.

**An agent** is a program that puts the two together in a loop:

1. Your program sends the model a question and a list of tools.
2. The model answers, or it asks for a tool by name.
3. Your program runs that tool and sends the result back.
4. Steps 2 and 3 repeat until the model stops asking.

Your lab has one, in `agent/loop.py`. You read it in Week 3.
:::

::: callout note | The word "agentic"
An **agentic system** is software that picks its own next step and can act on
the world.

Ordinary software follows a path a person wrote. An agent picks the path while
it is running. That one difference is the subject of this course.
:::

::: section | Why an agent fails differently
Three reasons, and none of them is a bug. Each one is a feature somebody asked
for.

**One: it can act.** A chatbot that only writes text can be wrong. An agent
that can send mail can be wrong in a way you cannot take back. The tool list is
the list of harm the system can do.

**Two: its input includes text other people wrote.** Strangers write support
tickets. Coworkers write knowledge base articles. Your agent reads both.

**Three: it cannot reliably tell instructions from data.** Messages do carry a
role label, such as `system` or `user`, and models are trained to weight those
labels. But a label is a learned habit, not an enforced boundary. Everything
still arrives in one stream, as words.

Put the three together. A stranger who can get text in front of your agent can
try to give it orders. If the agent believes them, it has tools.
:::

::: section | It does not fail the same way twice
Ordinary software is boring. Given the same input, it does the same thing, so a
bug is a line of code and fixing the line ends the bug.

A model is not like that. Ask it the same question twice and you can get two
answers. An agent can do the right thing four times and the wrong thing on the
fifth.

So you never run an attack once and write down "it worked." You run it many
times and report a rate. Your lab harness runs every case five times, and one
success out of five still counts as vulnerable.
:::

::: section | Scope before technique
Security testing is legal work when somebody has said yes. It is a crime when
nobody has.

The word for that yes is **authorization**. A person with the right to say yes
has said yes, in writing, about named systems.

Your authorization is the Rules of Engagement page. It lists three things you
may attack:

1. The HelpDesk Lite target app in your lab repository.
2. Your own copy of the agent in your lab repository.
3. A language model running on your own computer.

Everything else is out of scope, including every commercial AI service and
every system the college owns. A tester who finds a serious flaw in a system
nobody hired them to test has not done good work. Scope first, technique
second.
:::

::: callout note | The framework line for this week
Week 1 maps to NIST AI RMF GOVERN 4.3. It asks that an organization have real
practices for testing AI systems and for sharing what the testing finds. The
Rules of Engagement page is that practice, written down.
:::

::: section | Python: the four types you need this week
You will read Python that already runs and predict what it does. That is how
professionals meet a codebase they did not write.

These two lines are real, from `verify_env.py`:

```python
MIN_PYTHON = (3, 11)
REQUIRED_PACKAGES = ["requests", "flask", "yaml", "jsonschema", "dotenv", "pytest"]
```

A **variable** is a name for a value. A **type** is what kind of value it is.

| Type | What it is | Example |
|---|---|---|
| string | text inside quotes | `"requests"` |
| integer | a whole number | `11` |
| list | ordered values in square brackets | `REQUIRED_PACKAGES` |
| dictionary | labeled pairs, looked up by name | shown below |

Note that `"11"` in quotes is a string, not a number.
:::

::: section | Lists: found by position
A list keeps its items in order, and positions start at zero. That trips up
everybody once, and then never again.

```python
print(len(REQUIRED_PACKAGES))
print(REQUIRED_PACKAGES[0])
print(REQUIRED_PACKAGES[2])
print(REQUIRED_PACKAGES[-1])
```

Predict the output before you read on. The answers are `6`, `requests`, `yaml`,
and `pytest`. Position 0 is the first item, position 2 is the third, and a
negative position counts from the end.
:::

::: section | Strings: the f-string
An **f-string** is a string with holes in it. The parts inside braces are
replaced by values, and the `f` before the first quote turns the braces on.
This line is real, from `common/canary.py`:

```python
return f"CANARY-{name.upper()}-{digest}"
```

If `name` holds `"kb"` and `digest` holds `"9cd8ec0a8171"`, that line produces
`CANARY-KB-9cd8ec0a8171`.
:::

::: section | Dictionaries: found by name
A **dictionary** is a set of pairs. Each pair has a **key** and a **value**,
and you look a value up by its key.

Run this from your labs folder:

```
python -m common.canary
```

It prints your three canary tokens. In the code they live in a dictionary:

```python
{
    "sysprompt": "CANARY-SYSPROMPT-9fc911cc92a8",
    "customer":  "CANARY-CUSTOMER-c81b4f5fca56",
    "kb":        "CANARY-KB-9cd8ec0a8171",
}
```

Your own tokens differ, because they are built from your student ID.

1. **You look up by key, not by position.** `tokens["kb"]` works. `tokens[2]`
   raises a `KeyError`.
2. **A missing key stops the program**, unless you ask for a default.
   `tokens.get("password", "no such key")` returns that default instead.
3. **A value can itself be a dictionary.** That is how a model's reply is
   shaped, and it is the subject of Week 2.
:::

::: section | Running a script
Run both of these from the folder that holds `verify_env.py`.

```
python verify_env.py
python -m common.canary
```

The first runs a file by its name. The second runs a module by its dotted name,
and the `-m` flag is what makes the lab's import lines work. If either command
cannot find something, you are in the wrong folder nine times out of ten.
:::

::: reading | Reading: two short sections of the Python Tutorial
**What it is.** The official Python Tutorial, written by the people who make
Python. It is free, and you will keep using it after this course.

**What to read.** Two short sections in chapter 5: lists, and dictionaries.
Skip everything else this week. Budget about 25 minutes.

**What to look for.** Three things:

1. How the tutorial writes a list and a dictionary. Compare it to the lab code
   above and check that you would have read it the same way.
2. What happens when you ask a dictionary for a key it does not have.
3. Any method name you recognize from this page, such as `append` or `get`.

**One question to answer while you read**, which comes back in Lab 1: a list
and a dictionary can both hold six things. What is the difference in how you
get one of those things back out?

The link is on the Course Material page.
:::

::: callout tip | About the offline `mock` provider
Your labs ship with a provider named `mock`. It runs with no key and no
internet, so Lab 1 works on day one.

It is not a language model. It is a pattern matcher that pretends to be a very
gullible assistant.

A run against it proves your code works and proves nothing about a real model.
The harness prints a banner saying so. Never delete that banner, and never cite
a mock run as a finding.
:::

::: checkpoint
Answer these before you start Lab 1. If one is hard, read that section again.

1. Name the three reasons an agent fails differently from ordinary software.
2. A tool is just a function. What makes it dangerous?
3. You may attack three things. Name them without looking.
4. `REQUIRED_PACKAGES[1]` returns one string. Which one, and why is it not the
   first item?
5. You have a dictionary named `tokens`. Write the line that gets the value
   stored under the key `customer`.
:::

::: sources
The Python Tutorial, sections on lists and dictionaries. Published by the
Python Software Foundation under the PSF License, version 2. Linked, not
reproduced.

NIST AI RMF 1.0, subcategory GOVERN 4.3. A United States government work.

All lab code quoted on this page is instructor-authored and lives in your lab
repository. The canary tokens shown are from the shared demo student ID, so
they are not anyone's real evidence.
:::
