::: intro
This page covers three things: what an agentic system is, why it fails
differently from ordinary software, and enough Python to read the lab code.
Read it before you start Lab 1. It takes about 45 minutes.
:::

::: section | Three words, in order
Almost everything in this course is built from three ideas. Learn them in this
order.

**A model** reads text and produces text. That is all it does. It cannot open a
file. It cannot send mail. It cannot reach your database.

**A tool** is an ordinary function somebody wrote. It can open a file. It can
send mail. It can reach your database. There is nothing clever about a tool.

**An agent** is a program that puts the two together in a loop:

1. Your program sends the model a question and a list of tools.
2. The model answers, or it asks for a tool by name.
3. Your program runs that tool and sends the result back to the model.
4. Steps 2 and 3 repeat until the model stops asking.

That loop is the whole idea. Your lab has one, in `agent/loop.py`. You read it
in Week 3.
:::

::: callout note | The word "agentic"
An **agentic system** is software that picks its own next step and can act on
the world.

Ordinary software follows a path a person wrote. An agent picks the path while
it is running.

That one difference is the subject of this course.
:::

::: section | Why an agent fails differently
This is the most important section on the page.

An agent fails differently from ordinary software for three reasons. None of
them is a bug. Each one is a feature somebody asked for.

**One: it can act.** A chatbot that only writes text can be wrong. An agent that
can send mail can be wrong in a way you cannot take back. The tool list is the
list of harm the system can do.

**Two: its input includes text other people wrote.** Your agent reads support
tickets. Strangers write support tickets. It reads knowledge base articles.
Coworkers write those. All of it arrives as text, from outside.

**Three: it cannot tell instructions from data.** This is the hard one. The
model does not get two separate inputs, one marked "orders from my owner" and
one marked "text I fetched." Everything arrives in one stream, as words. Your
instructions are words. The ticket is words.

Put the three together. A stranger who can get text in front of your agent can
try to give it orders. If the agent believes them, it has tools.
:::

::: section | The other difference: it does not fail the same way twice
Ordinary software has one more property you have been relying on your whole
life. It is boring. Given the same input, it does the same thing.

A bug in ordinary software is a line of code. You find the line, you fix the
line, and the bug is gone.

A model is not like that. Ask it the same question twice and you can get two
answers. So an agent can do the right thing four times and the wrong thing on
the fifth.

That changes how you test. You cannot run an attack once and write down "it
worked." You run it many times and report a rate.

Your lab harness runs every case five times. One success out of five still
counts as vulnerable, because an attacker gets to try again. You meet that idea
properly in Week 6.
:::

::: section | Scope before technique
Security testing is legal work when somebody has said yes. It is a crime when
nobody has.

The word for that yes is **authorization**. It means a person with the right to
say yes has said yes, in writing, about named systems.

In this course, your authorization is the Rules of Engagement page. It lists
three things you may attack:

1. The HelpDesk Lite target app in your lab repository.
2. Your own copy of the agent in your lab repository.
3. A language model running on your own computer.

That is the whole list. Everything else is out of scope, including every
commercial AI service and every system the college owns.

Here is why this comes first, in week 1, before any technique. A tester who
finds a serious flaw in a system nobody hired them to test has not done good
work. They have created a problem for their employer and for themselves.

Scope first. Technique second. That order never changes.
:::

::: callout note | The framework line for this week
This course maps its content to published security frameworks, so you can name
what you did in the words a hiring manager knows.

Week 1 maps to NIST AI RMF GOVERN 4.3. In plain language, it asks that an
organization have real practices in place for testing AI systems and for
sharing what the testing finds.

The Rules of Engagement page is that practice, written down. The findings report
you write in the final block is the sharing half.
:::

::: section | Python part one: read before you write
You will not write Python from a blank file this week. You will read Python that
already runs, and predict what it does.

That is not a shortcut. It is how professionals meet a codebase they did not
write. You read first, you guess, then you check.

Every snippet below is real code from your lab repository. You can open the file
and see it.
:::

::: section | Variables, and the types you need first
A **variable** is a name for a value. These two lines are real, from
`verify_env.py`:

```python
MIN_PYTHON = (3, 11)
REQUIRED_PACKAGES = ["requests", "flask", "yaml", "jsonschema", "dotenv", "pytest"]
```

A **type** is what kind of value it is. You need four types this week.

A **string** is text. It sits inside quotes. `"requests"` is a string.

An **integer** is a whole number. `11` is an integer. Note that `"11"` in quotes
is a string, not a number.

A **list** is an ordered row of values inside square brackets.
`REQUIRED_PACKAGES` is a list of six strings.

A **dictionary** is a set of labeled pairs. It gets its own section below.
:::

::: section | Lists: found by position
A list keeps its items in order. You reach an item by its position.

Positions start at zero. This trips up everybody once, and then never again.

```python
REQUIRED_PACKAGES = ["requests", "flask", "yaml", "jsonschema", "dotenv", "pytest"]

print(len(REQUIRED_PACKAGES))
print(REQUIRED_PACKAGES[0])
print(REQUIRED_PACKAGES[2])
print(REQUIRED_PACKAGES[-1])
```

Predict the four lines of output before you read on.

The answers are `6`, `requests`, `yaml`, and `pytest`.

`len()` counts the items, and there are six. Position 0 is the first item.
Position 2 is the third. A negative position counts from the end, so `-1` is the
last one.
:::

::: section | Strings: the f-string
An **f-string** is a string with holes in it. The parts inside braces are
replaced by values.

This line is real, from `common/canary.py`:

```python
return f"CANARY-{name.upper()}-{digest}"
```

If `name` holds `"kb"` and `digest` holds `"9cd8ec0a8171"`, that line produces:

```
CANARY-KB-9cd8ec0a8171
```

The `f` before the first quote is what turns the braces on. `name.upper()` is a
built-in that returns the same text in capital letters.
:::

::: section | Dictionaries: found by name
A **dictionary** is a set of pairs. Each pair has a **key** and a **value**. You
look a value up by its key.

Run this from your labs folder:

```
python -m common.canary
```

It prints your three canary tokens. Inside the code, those three tokens live in
a dictionary that looks like this:

```python
{
    "sysprompt": "CANARY-SYSPROMPT-9fc911cc92a8",
    "customer":  "CANARY-CUSTOMER-c81b4f5fca56",
    "kb":        "CANARY-KB-9cd8ec0a8171",
}
```

Your own tokens are different, because they are built from your student ID.

Three rules to hold on to:

1. **You look up by key, not by position.** `tokens["kb"]` works. `tokens[2]`
   does not, because `2` is not one of the keys. It raises a `KeyError`.
2. **A missing key stops the program**, unless you ask for a default.
   `tokens.get("password", "no such key")` returns the default text instead.
3. **A value can itself be a dictionary.** That is how a model's reply is
   shaped, and it is the whole subject of Week 2.
:::

::: section | Running a script
There are two ways you will start Python code in this course. Run both from the
folder that holds `verify_env.py`.

```
python verify_env.py
python -m common.canary
```

The first one runs a file by its name.

The second one runs a module inside the repository, by its dotted name. The `-m`
flag is what makes the import lines inside the lab code work.

If either command says it cannot find something, you are in the wrong folder
nine times out of ten.
:::

::: reading | Reading: two short sections of the Python Tutorial
**What it is.** The official Python Tutorial, written by the people who make
Python. It is free and it is the reference you will keep using after this
course.

**What to read.** Two sections only, and they are short. The section on lists in
chapter 5, and the section on dictionaries in the same chapter. Skip everything
else this week. Budget about 25 minutes.

**What to look for.** Three things:

1. How the tutorial writes a list and a dictionary. Compare it to the lab code
   above and check that you would have read it the same way.
2. What happens when you ask a dictionary for a key it does not have.
3. Any method name you recognize from this page, such as `append` or `get`.

**One question to answer while you read**, which comes back in Lab 1: a list and
a dictionary can both hold six things. What is the difference in how you get one
of those things back out?

The link is on the Course Material page.
:::

::: callout tip | About the offline `mock` provider
Your labs ship with a provider named `mock`. It runs with no key and no
internet, so Lab 1 works on day one.

It is not a language model. It is a pattern matcher that pretends to be a very
gullible assistant.

A run against it proves your code works. It proves nothing about how a real
model behaves. The harness prints a banner saying so, and you must never delete
that banner or cite a mock run as a finding.
:::

::: checkpoint
Answer these for yourself before you start Lab 1. If one of them is hard, read
that section again.

1. Name the three reasons an agent fails differently from ordinary software.
2. A tool is just a function. What makes it dangerous?
3. You may attack three things. Name them without looking.
4. `REQUIRED_PACKAGES[1]` returns one string. Which one, and why is it not the
   first item?
5. You have a dictionary named `tokens`. Write the line that gets the value
   stored under the key `customer`.
:::

::: sources
The Python Tutorial, sections on lists and dictionaries. Published by the Python
Software Foundation under the PSF License, version 2. Linked, not reproduced.

NIST AI RMF 1.0, subcategory GOVERN 4.3. A United States government work.

All lab code quoted on this page is instructor-authored and lives in your lab
repository. The canary tokens shown are from the shared demo student ID, so they
are not anyone's real evidence.
:::
