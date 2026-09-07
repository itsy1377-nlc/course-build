# Week 0 outline: the programming on-ramp

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 6.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.

| Field | Value |
|---|---|
| Module title | Module 0: Programming On-Ramp |
| Status | Optional, strongly recommended, ungraded |
| Open | Day one, and for the whole term |
| Sits | Outside the seven instructional weeks |
| Student time | 4 hours 8 minutes at the fast end, 4 hours 57 minutes planned, 5 hours 56 minutes at the careful end |
| Delivery | One runnable notebook, plus a Canvas practice quiz for the self-assessment |
| Sections | 10, in the order the course needs them |
| Self-assessment | 10 questions, one per section |
| Model calls | None |
| Tokens spent | Zero |
| API key needed | None |
| CLO mapping | None. Week 0 is not assessed and gets no Canvas Outcome. |

A note on terms. A *notebook* is the web page where students run Python. A *cell*
is one block in that notebook. A *TODO cell* is a cell marked for the student to
fill in. *Pre-written* means the cell arrives finished and working. A *traceback*
is the block of text Python prints when a line of code fails.

## What week 0 is

Students arrive from a non-technical AI literacy course. That course supplies no
Python. Every week from week 1 on asks them to write Python.

Week 0 closes that gap and nothing more. It teaches ten constructs. Every one of
them is used by a lab cell a student has to write. Nothing else is taught.

Week 0 teaches Python, not the course. Every worked example uses everyday
subject matter. No example mentions email, phishing, headers, alerts or verdicts.
That rule holds in all ten sections and in all ten self-assessment questions.

The notebook runs offline. It makes no model calls, spends no tokens, and needs
no API key. A student can finish all of week 0 before the key is issued.

## What students are told about the time cost

The build prompt requires that the front-loading be stated plainly. Here is the
text students read, on the Module 0 Overview page and again in the notebook's
first cell.

> **About the time this takes**
>
> Week 0 is extra. It sits outside the seven course weeks. Those weeks each ask
> for under six hours of your time. Week 0 asks for four to six hours on top of
> that.
>
> Most of that time lands before week 1 is due. Plan for it. Two or three
> sittings in the first week works well.
>
> You can also come back later. Week 0 stays open all term. If week 4 breaks
> something loose, open week 0 again.
>
> Week 0 is not graded. It is strongly recommended.

## Where week 0 sits in Canvas

Template conflict 27 in `template-conflicts.md` covers this. The template's
module anatomy assumes a Content page and graded work. Week 0 has neither.

Module 0 therefore uses four items, in the template's own order.

| Item | Type | What it holds |
|---|---|---|
| Module 0 Overview | Page | What week 0 is, the time statement above, the out-of-scope list, and the link to the self-assessment |
| Week 0 Self-Assessment | Classic quiz, ungraded practice | The 10 questions below |
| Week 0 notebook: Python on-ramp | Notebook file | The ten sections, the section index, and the error card in its opening cells |
| Module 0 Wrap-up | Page | What you learned, what you did, what is next |

**Amended in Phase 2.** There is no Module 0 Content page, and the notebook is a
module item rather than a link inside one.

The template's Content page holds the week's reading. In Module 0 the reading is
the notebook. A page whose only job is to link the notebook puts a click between
a student and the thing they came for.

So the notebook is the module item. The overview page names it, the section
index sits in the notebook's own opening cells, and the error card also ships as
the Canvas page **If something breaks**. The amendment to template conflict 1
records the same rule for weeks 1 to 7, where the two notebooks are module items
too.

Module 0 has no discussion and no assignment. The self-assessment also gets a
Getting Started step on the course home page and a callout in the Orientation
module, per template conflict 4.

## The on-ramp, section by section

The ten sections follow the order the build prompt lists them in. That order is
also the order the course needs them. Section numbers are load-bearing: the week
1 sidebars link to section 2 and section 5 by number, and the week 5 sidebar
links to section 8.

| # | Section | Learning point | Everyday domain | Minutes | Week and lab construct it prepares |
|---|---|---|---|---|---|
| 1 | Variables and strings | A name holds a value, and you can change what it holds. Text joins with `+` and measures with `len()`. | A lunch order | 20 | Week 1 TODO 1 holds the prompt and the answer in variables. Week 3 TODO 2 `format_facts()` builds a labeled text block. Week 6 TODO 1 `build_guarded_prompt()` wraps text between two markers. |
| 2 | Calling functions and using return values | A call runs code and hands a value back. Store it or lose it. | A recipe scaled for guests | 25 | Week 1 TODO 1 `ask_model()` calls the pre-written `send_request()` and returns what came back. Week 1 sidebar 1A links here. Every later TODO cell calls pre-written helpers. |
| 3 | Lists, dictionaries and keys | A list holds items in order. A dictionary holds values by name. You read by key, write by key, fold one dictionary into another, and reach inside a dictionary that holds a list. | A library account | 40 | Week 1 TODO 1 builds the request dictionary, folds `MODEL_EXTRAS` into it, and reads the answer back out of a chain. Week 2 TODO 1 `extract_json()` returns a dictionary. Week 3 TODO 1 `build_facts()` reads values held inside `parsed["auth"]` and `parsed["gateway"]`. Week 4 TODO 1 `run_tool()` needs the safe lookup. |
| 4 | JSON as a dictionary in text form | JSON is a dictionary written as text. You cannot read it by name until you convert it. | A bus arrival board line | 20 | Week 2 TODO 1 `extract_json()` calls `json.loads()`. Week 2 sidebar 2B links here. Every week's export cell writes JSON. |
| 5 | f-strings | Put an `f` in front of the quote and values drop into the sentence. | A workshop name badge | 20 | Week 3 TODO 2 labels each fact. Week 7 TODO 1 `write_note()` fills a six-line template. Week 1 sidebar 1B and week 7 sidebar 7B link here. |
| 6 | Defining a function with parameters | `def` names it, parameters name what it takes, `return` hands a value back. A parameter can carry a default. | A room painting calculator | 30 | Every TODO cell in the course defines a function. Defaults are taught because `classify_email(parsed, max_tries=3)` and `run_loop(parsed, prompt_text, max_steps=MAX_STEPS)` both carry them. |
| 7 | if, elif and else | One path runs. Comparisons give true or false. `in` tests membership. | A thermostat | 25 | Week 2 TODO 2 acts on what the schema check returned. Week 4 TODO 1 picks a function from a name. Week 6 TODO 2 `check_against_facts()`. Week 7 TODO 2 `score_batch()` counts into buckets. |
| 8 | Loops: `for`, then `while` with a counter | Do the same thing to each item. Then run until a stop condition, with a cap that always ends it. | A class roster of quiz scores | 35 | Week 3 TODO 2 walks `FACT_ORDER`. Week 7 TODO 2 loops twenty rows. Week 5 TODO 1 `run_loop()` is a `while` with a four step cap and a stop condition. Week 5 sidebar links here. |
| 9 | try and except | Run code that might fail, and plan for the failure. The program keeps going. | Splitting a bill | 25 | Week 2 TODO 1 `extract_json()` catches a bad `json.loads()`. Week 2 TODO 2 retries up to three times. Week 2 sidebar 2C links here. |
| 10 | How to read an error message | Read the last line first. Find your line. Print the value. | A shopping basket | 30 | Every week. Named failures include week 1 `NameError`, week 2 `TypeError` on a `None` result, and `KeyError` in weeks 3, 4 and 7. |

### Section 1: Variables and strings

The worked example is a lunch order. Two variables hold a sandwich and a drink.
A third joins them into one order line. Then the drink changes and the line is
rebuilt, so the student sees that a name can be reassigned.

The "try changing this" cell asks the student to swap the drink. The "you try"
cell asks for an order line for two different items, with the answer in the cell
below it.

### Section 2: Calling functions and using return values

A pre-written `scale_recipe(cups, guests)` arrives already working. The student
calls it twice and stores both answers. The section then calls it once more and
throws the answer away, so the difference is on screen.

This is the section week 1 leans on hardest. Week 1 TODO 1 is a function that
calls another function and returns what it got back. A student who has not seen
a return value used cannot write that cell.

### Section 3: Lists, dictionaries and keys

Lists come first, because a dictionary in this course usually holds one. The
example is a library account: a list of books checked out, and a dictionary with
the card holder, the branch and a due day per book. The section runs in three
parts, on that one example.

Part one reads. Read by position. Read by key. Read with a default when the key
may be missing. Add to a list with `.append()`.

Part two writes. Assign a key with square brackets on the left of an equals
sign. Fold a second dictionary into the first one with `.update()`.

Part three opens nested data. A dictionary holds a list, each item in that list
is its own dictionary, and one chained expression reaches a field inside it.

The safe lookup is here for a specific reason. Two sender reputation records in
the corpus match on an address and carry no `domain` key. Week 4 code that
assumes the key will fail on those two.

Parts two and three are here because week 1 needs both in its first TODO cell.
The request holds a list of dictionaries under one key. `MODEL_EXTRAS` is folded
into it. The answer is then read back through a key, a list position and two more
keys. Week 3 TODO 1 reads nested values the same way. Both additions are declared
in the assumptions below.

### Section 4: JSON as a dictionary in text form

A bus arrival board sends one line as text. It looks like a dictionary and is
not one. `json.loads()` turns it into one, and then it can be read by key.
`json.dumps()` goes the other way.

The section closes by breaking it on purpose. Text that is not valid JSON raises
an error. The section names that error and points forward to section 9, which
catches it.

### Section 5: f-strings

The example builds a workshop name badge from a name, a role and a table number.
The same line is then built with `+` and quotes, right beside it. Seeing both
makes the case for the f-string without argument.

Week 7 is where this pays off. `write_note()` fills six fixed lines from one
result. That cell is short only because f-strings exist.

### Section 6: Defining a function with parameters

The example is a room painting calculator. `paint_needed(width, height,
coats=2)` returns how much paint a wall takes. It is called with two arguments
and then with three, so the default is visible.

This section also settles the most common beginner confusion in the course:
`return` hands a value back to the caller, `print` puts text on screen, and they
are not the same thing. Week 1 breaks immediately for a student who mixes them.

### Section 7: if, elif and else

A thermostat reads one temperature and picks heat, cool or nothing. Exactly one
branch runs. The section then shows `in`, testing whether a name is on a list.

Week 4 TODO 1 is a chain of `if` and `elif` that picks one of three functions by
name. That cell is the single closest match to this section anywhere in the
course.

### Section 8: Loops, in two parts

This is the longest section, because week 5 is the hardest week.

Part one is the `for` loop. The example walks a class roster of quiz scores,
building one line per student with `.append()`, then joining the lines into one
block of text. That is exactly the shape of week 3 TODO 2.

Part two is the `while` loop with a counter. The example keeps reading scores
until it finds one below passing, and stops anyway after three passes. It shows
a loop with no cap that would never end, and then the counter that ends it.

Part two is an addition to the build prompt's scope list. It is declared in the
assumptions below. Week 5's lab and sidebar both need `while`, and `week-05-spec.md`
records the same dependency.

### Section 9: try and except

The example splits a bill. One entry arrives as text that is not a number, so
the conversion fails. `try` runs the conversion and `except` handles the failure,
and the program carries on.

The section then puts the `try` inside a small loop, so one bad entry is skipped
rather than fatal. That is the shape of week 2's retry.

One practice note is stated here and not softened. Catch the error you named, not
every error. A blanket catch hides the message section 10 teaches students to
read.

## Section 10 in detail: how to read an error message

This is the highest-value section in week 0. A student debugging alone at 11pm
has no instructor and no classmate. They have a traceback and whatever they can
make of it. Section 10 is the whole answer to that.

It ships in two numbered parts, the way section 8 does, and keeps the one section
number so the sidebar links still resolve. Part one is the five step routine and
the anatomy of a traceback. Part two walks the six errors. Splitting it keeps
each part inside the per-section length budget, which the whole section was
sitting on.

### Why it is section 10 but reachable from minute one

The build prompt fixes the scope order, and reading errors comes last in it. That
order is kept, because two other blueprint documents link to sections by number.

Pedagogy is handled a different way. A short **If something breaks** card sits in
the notebook's second cell, above section 1. It fits on one screen. It carries
the five step routine and the six error table, and it links to section 10.

Every section ends with the same one-line pointer to that card. The card also
ships as a Canvas page, **If something breaks**, in the Orientation module. So a
student meets it in the first two minutes and can reach it from the course
navigation at any point in the term.

Linking that page from inside each weekly module is not built. The template's
weekly module has no slot for a standing reference link, so the placement is
open question 3 below. Until that is settled, no weekly module links the page.

### The routine, five steps

The card and the section both carry these, in this order.

1. Read the last line of the error first. Everything above it is context.
2. Name the error type. It is the word before the colon on that last line.
3. Find your line. Scan the trace for the last line that names your cell.
4. Print the value on the line above the one that failed.
5. Change one thing. Run it again.

Step 1 is the one that changes outcomes. Students read tracebacks top down, hit
file paths from code they did not write, and conclude the error is unreadable.
The section says plainly that Python puts the answer at the bottom.

### The anatomy walk

One traceback is walked line by line, on a shopping basket example. The walk
labels four parts on screen: the header line, the frames, the arrow at the
failing line, and the error type with its message.

The phrase "most recent call last" is explained in plain words, because it is
the reason the useful part is at the bottom.

### The six errors, and where each one shows up

Each error gets a cell that breaks on purpose. The student predicts the error,
runs the cell, reads the message, then fixes it. The fix is in the cell below.

| Error | What it usually means | Where the course produces it |
|---|---|---|
| `NameError` | A name is used before it exists, or the cell that makes it has not been run | Week 1, running the check cell before the TODO cell. Also every sidebar pasted into a lab cell. |
| `SyntaxError` and `IndentationError` | Python could not read the line at all. A missing colon, an unclosed bracket, uneven indenting | Any week a student writes a `def`, an `if` or a loop |
| `KeyError` | A dictionary was asked for a key it does not have | Week 3 facts, week 4 tool results, week 7 batch rows |
| `TypeError` | A value was used in a way its kind does not allow, often a `None` where a dictionary was expected | Week 2, when `extract_json()` returns `None` and the next line reads a key from it |
| `ValueError`, including the JSON decode error | The kind was right and the content was wrong. Text that is not JSON | Week 2, the exact failure that try/except catches |
| `AttributeError` | A method was called on a value that does not have it, such as a string method on a list | Weeks 3 and 6, when a fact arrives as a list and is treated as text |

Those six were chosen from the failures the week specs already predict, not from
a general list of Python errors.

### The notebook trap

One page of section 10 covers a failure that is specific to notebooks. The cell
that raises the error is not always the cell that is wrong.

Cells run in whatever order a student clicks them. A name defined in a cell that
was never run does not exist, even though it is on screen. The section says this
plainly, and gives the fix: run the cells above, or restart and run all.

This is here because the hosted notebook is the whole environment. There is no
command line and no other way to run the code.

### What not to do

Three habits waste the most time, and the section names them.

1. Do not retype the whole cell. The message says which line failed.
2. Do not delete the error and try something else at random. Read it first.
3. Do not paste the whole notebook into an AI assistant before reading the last
   line. The course AI policy permits AI help with disclosure. It works far
   better when you can say which error you got.

### Time and payoff

Section 10 is planned at 30 minutes, between 26 and 36. Week 1 already holds back
10 minutes of its budget for one traceback, so the payoff starts in week 1.

## The time arithmetic

Three columns. Fast is a student who has programmed before and is checking.
Planned is the figure the blueprint uses. Careful is a student meeting all of it
for the first time and doing every optional cell.

| Section | Fast | Planned | Careful |
|---|---|---|---|
| Front matter, the time statement, the out-of-scope list, and the self-assessment | 12 | 15 | 18 |
| 1. Variables and strings | 16 | 20 | 24 |
| 2. Calling functions and using return values | 20 | 25 | 30 |
| 3. Lists, dictionaries and keys | 34 | 40 | 48 |
| 4. JSON as a dictionary in text form | 16 | 20 | 24 |
| 5. f-strings | 16 | 20 | 24 |
| 6. Defining a function with parameters | 26 | 30 | 36 |
| 7. if, elif and else | 22 | 25 | 30 |
| 8. Loops, both parts | 30 | 35 | 42 |
| 9. try and except | 20 | 25 | 30 |
| 10. How to read an error message | 26 | 30 | 36 |
| Closing: where each section shows up in the course | 10 | 12 | 14 |
| **Total minutes** | **248** | **297** | **356** |
| **Total time** | **4 h 8 m** | **4 h 57 m** | **5 h 56 m** |

All three totals land inside the 4 to 6 hour target. The planned figure sits 63
minutes below the ceiling. The careful figure sits 4 minutes below it, which is
almost no slack.

Section 3 is what took that slack. It grew from 30 planned minutes to 40 when the
write moves and the nested read were added, because week 1 cannot be written
without either. If the careful column has to come back down, the place to look is
section 3, not the two sections that carry week 5.

The three sections with the most spread are 3, 8 and 10. All three are deliberate.
Section 3 now carries week 1's first TODO cell in full. Section 8 carries the
`while` loop that week 5 depends on. Section 10 is the one section a student is
expected to reread later in the term.

These are planned figures and not measured ones. No timing data exists for this
student population. They should be re-measured after the Phase 2 build.

## What week 0 leaves out

The build prompt requires the exclusions be stated so students do not go hunting.
Here is the text students read, on the Overview page and in the notebook.

> **What this notebook leaves out**
>
> You do not need these for this course. You do not have to go find them.
>
> - Classes and objects.
> - Comprehensions.
> - Reading and writing files, past the cells we wrote for you.
> - Decorators.
> - Virtual environments.
> - Pip, and installing packages.
> - The command line.
>
> Every line you write in a lab uses only what is in this notebook. Say a web
> search hands you one of the things on this list. You can close that tab.

## The self-assessment

Ten questions, one per section. Every question uses everyday subject matter. None
mentions email or security.

Delivery. The self-assessment ships as a Canvas ungraded practice quiz, which
scores itself and shows the answers. That follows template conflict 27, which
puts it in Module 0's quiz slot. The notebook's first cell links to it and
reprints the scoring rule, so the two never drift.

Feedback per question names the section the question came from. That is what
makes the middle scoring band usable. The name used is the notebook's own
heading, word for word, because that is the heading a student scrolls to look
for.

### The questions, as students see them

**Question 1.** Section 1, variables and strings.

You run these three lines. What prints?

```python
color = "blue"
color = "green"
print(color)
```

- A. blue
- B. green
- C. blue green
- D. An error

**Answer: B.**

**Question 2.** Section 2, calling functions and using return values.

You run these four lines. What prints?

```python
def add_fee(price):
    return price + 1

total = add_fee(4)
print(total)
```

- A. 5
- B. 4
- C. Nothing. The function returns, so nothing reaches the screen.
- D. An error, because print cannot take a number.

**Answer: A.**

**Question 3.** Section 3, lists, dictionaries and keys.

You run these two lines. What prints?

```python
sizes = {"small": 8, "medium": 12, "large": 16}
print(sizes["medium"])
```

- A. medium
- B. 12
- C. 1
- D. An error

**Answer: B.**

**Question 4.** Section 4, JSON, a dictionary in text form.

A program hands you this, and it is text.

```python
line = '{"city": "Austin", "high": 96}'
```

You want to read the high by name. What do you do first?

- A. Nothing. You can read it by name already.
- B. Turn the text into a dictionary with `json.loads()`.
- C. Turn it into text with `json.dumps()`.
- D. Count the characters in it.

**Answer: B.**

**Question 5.** Section 5, f-strings.

You run these three lines. What prints?

```python
name = "Sam"
cups = 3
print(f"{name} drank {cups} cups.")
```

- A. {name} drank {cups} cups.
- B. Sam drank 3 cups.
- C. f Sam drank 3 cups.
- D. An error

**Answer: B.**

**Question 6.** Section 6, writing your own function.

Which line starts a function that takes two values?

- A. `def area(width, height):`
- B. `area(width, height)`
- C. `def area = width, height`
- D. `function area(width, height):`

**Answer: A.**

**Question 7.** Section 7, if, elif and else.

A parcel desk picks a shipping class from a weight in pounds. You run these
lines. What prints?

```python
weight = 3
if weight > 20:
    print("freight")
elif weight > 10:
    print("ground")
else:
    print("letter")
```

- A. freight
- B. ground
- C. letter
- D. All three

**Answer: C.**

The domain is deliberately not a thermostat. Section 7's own worked example is a
thermostat with a `temp` of 41, and it attaches different words to the branches.
A question that looked like that cell would punish a student for remembering it.

**Question 8.** Section 8, loops, in two parts.

You run these lines. What prints?

```python
counts = [2, 5, 1]
total = 0
for c in counts:
    total = total + c
print(total)
```

- A. 3
- B. 8
- C. 2
- D. 251

**Answer: B.**

**Question 9.** Section 9, try and except.

What does a try and except block do?

- A. It stops the program the moment a line fails.
- B. It runs some code, and runs a backup plan if that code fails.
- C. It makes the code run faster.
- D. It repeats the code until the code works.

**Answer: B.**

**Question 10.** Section 10, how to read an error message.

Your code failed and printed this.

```text
Traceback (most recent call last):
  File "shopping.py", line 7, in <module>
    print(basket["pears"])
KeyError: 'pears'
```

Which line failed, and why?

- A. Line 7. The basket has no key named pears.
- B. Line 1. The file could not be opened.
- C. Line 7. The word print is spelled wrong.
- D. There is no way to tell from this message.

**Answer: A.**

### The scoring rule, as students read it

> **What your score means**
>
> This quiz is not graded. It does not count toward anything. Take it as many
> times as you like.
>
> Each answer names the week 0 section it came from. Use those names.
>
> **9 or 10 right.** Skip week 0 and start week 1. Keep the notebook handy. Open
> a section when you want it.
>
> **6, 7 or 8 right.** Work through the sections your missed questions name. Skip
> the rest. That is about one to two hours.
>
> **5 or fewer right.** Work through the whole notebook, in order. Plan about
> five hours. Most students in this course have never written Python. That is
> what this notebook is for, and week 1 reads much better after it.
>
> You do not have to finish week 0 before week 1 starts. Week 0 stays open all
> term.

## Look and feel

The build prompt requires the same look and feel as the lab notebooks. The
on-ramp follows the standing cell order in `code-ledger.md` section 2.3, with the
parts week 0 does not have removed.

What is the same. Markdown cell, then a code cell that runs, then a plain
walkthrough, then a check. Headings in the same style. A "try changing this"
prompt at the end of each part, as the sidebars have.

What is different, and why. There is no configuration cell, no token counter, no
`send_request()` and no export cell. Week 0 talks to no network and submits
nothing. `json` is the only import, so nothing needs installing.

Each of the ten sections runs the same seven cells.

1. Markdown: what this is, and where it shows up in the course.
2. Code: the worked example, running end to end.
3. Markdown: the walkthrough, one plain sentence per line of code.
4. Code: try changing this.
5. Code: you try. One small task.
6. Code: the answer to step 5.
7. Markdown: the link line, naming the week and lab cell this prepares, and the
   pointer to the error card.

Step 6 ships revealed rather than hidden. Week 0 is ungraded, so a hidden answer
costs a stuck student time and protects nothing.

## Readability

Measured with `tools/readability.py`. Code blocks, tables and block quotes are
excluded by the tool, which is why the student-facing blocks were extracted and
measured on their own.

| Text measured | Grade | Average sentence | Longest sentence | Ceiling on grade and average |
|---|---|---|---|---|
| This document, prose only | 4.72 | 11.2 | 30 | 9.5 grade, 18 words |
| Self-assessment questions and options | 1.41 | 6.5 | 13 | 7.0 grade, 12 words |
| The scoring rule students read | 1.39 | 6.5 | 12 | 7.0 grade, 12 words |
| Questions and scoring rule together | 1.39 | 6.5 | 13 | 7.0 grade, 12 words |
| The time statement students read | 1.77 | 7.8 | 12 | 7.0 grade, 12 words |
| The out-of-scope list students read | 3.52 | 8.2 | 14 | 7.0 grade, 12 words |

The three quiz rows are measured on the shipped file,
`content/quizzes/week0-self-assessment.yaml`, with its HTML tags and its code
blocks stripped, so the numbers describe what a student actually reads on
screen. Re-run them against that file rather than against this document.

## Assumptions

1. **Section numbers follow the build prompt's scope order.** Calling functions
   is section 2 and f-strings is section 5, which is what `week-01-spec.md`
   assumes. Loops are section 8, which is what the week 5 sidebar links to. A
   renumbering breaks four sidebar links.
2. **`while` with a counter is added to section 8.** The build prompt's scope
   names `for` loops only. Week 5 TODO 1 is a `while` loop with a step cap, and
   `week-05-spec.md` records this as a blocking dependency. Declared here rather
   than resolved quietly.
3. **Lists are added to section 3.** The scope list names dictionaries and not
   lists. A `for` loop needs something to walk, `FACT_ORDER` is a list, and the
   `indicators` key holds one. `.append()` comes with them.
4. **A safe key lookup with a default is added to section 3.** Two sender
   reputation records in the corpus match on an address and carry no `domain`
   key, so week 4 code that assumes the key fails on those two.
5. **`elif` and `in` are added to section 7.** Week 4 TODO 1 is an `elif` chain,
   and week 6 TODO 2 tests membership.
6. **Joining a list into text is added to section 8.** Week 3 TODO 2 and week 7
   TODO 1 both build one block of text out of several lines.
7. **Time figures are planned, not measured.** They should be re-measured after
   the Phase 2 build, alongside the week 1 and week 2 time check the build prompt
   already asks for.
8. **The self-assessment is a Canvas ungraded practice quiz.** It is set to
   unlimited attempts with the answers shown after each submission. That matches
   the judgment made for the weekly self-checks in `week-01-spec.md`.
9. **Week 0 gets no CLO mapping and no Canvas Outcome.** This follows the build
   prompt and `alignment-matrix.md`.
10. **The on-ramp ships as one notebook, not ten.** One link, one place to come
    back to, and a section index at the top. Ten files would be easier to reopen
    at one section and harder to find.
11. **Writing to a dictionary is added to section 3.** The scope list names key
    access and does not say whether that means reading or writing. Week 1 TODO 1
    folds `MODEL_EXTRAS` into the request dictionary, which needs `.update()`, and
    `code-ledger.md` section 3 records that merge. Assigning a key is taught
    beside it because it is the same move.
12. **Nested access is added to section 3.** The scope list does not name it. Week
    1 TODO 1 builds `{"messages": [{"role": ..., "content": ...}]}`, a list of
    dictionaries held under a key, and reads the answer back with four chained
    lookups and a list position in the middle. `serving-stack-shape.md` fixes both
    shapes. Week 3 TODO 1 reads two values out of nested dictionaries. Without
    this part a student meets chained access for the first time in the first cell
    they are asked to write.

## Open questions

1. **Should the instructor see who took the self-assessment, and what they
   scored?** A Canvas practice quiz records the attempt either way. That data
   would support early outreach, and it could also feel like surveillance to a
   student told the quiz does not count. The scoring text currently says no one
   sees the score but the student. That sentence has to change or stay based on
   your answer.
2. **Is the notebook server available to students on day one?** Week 0 must be
   open from day one. If the hosted notebooks are not provisioned until week 1
   opens, week 0 cannot be run when it is needed, and the front-loading promise
   fails. A downloadable copy is a poor substitute, because students have a
   browser and nothing else.
3. **How does each weekly module point at the error card?** The card now ships
   two ways: as the notebook's second cell, and as a Canvas page called **If
   something breaks** in the Orientation module. What is still undecided is the
   weekly link. The template's weekly module has no slot for a standing reference
   link. The two candidates are one line in each week's Overview page, or the same
   page added as a repeated module item in all seven weeks. This needs a decision
   before week 3 is built.
4. **How is week 0 attrition tracked?** The risk register commits to tracking
   attrition among students who skip week 0. That measurement needs the quiz
   attempt data from question 1.
5. **Do students get access before the term opens?** Four to six hours of
   front-loaded work is easier in the week before the term than in the first week
   of it. This is a college scheduling question, not a build question.
