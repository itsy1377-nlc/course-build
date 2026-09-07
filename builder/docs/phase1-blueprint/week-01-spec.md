# Week 1 spec: Call the model from code

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 1 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.

| Field | Value |
|---|---|
| Week title | Call the model from code |
| Supports | CLO2 |
| Primary evidence | None. Week 1 adds supporting CLO2 evidence that week 2 replaces. |
| Breadth topics carried | B1 and B3, in the reading, the discussion and the self-check |
| Emails used | 001 and 002 |
| Student time, total | 4 hours 32 minutes |
| Estimated tokens, one full lab run | about 2,560 |

A note on terms. A *model* is the AI service the course sends text to. A *notebook*
is the web page where students run Python. A *cell* is one block in that notebook.
A *TODO cell* is a cell marked for the student to fill in. *Pre-written* means the
cell arrives finished and working.

A *token* is a chunk of text, roughly four characters. It is the unit the model is
billed and capped in. *Temperature* is a setting on the model call. A low
temperature makes answers steadier. A high one makes them vary more.

A *traceback* is the block of text Python prints when a line of code fails. The
*serving stack* is the software that runs the model and answers requests.

## 1. The capability added, and why it is exactly one

Week 1 adds one thing. The student's Python code can send text to the model and
read the answer back.

That is the whole capability. Nothing is classified. Nothing is checked. Nothing
is stored in a fixed shape. The student writes one function, `ask_model()`, and
uses it twice.

Why this counts as one capability and not several. Students observe three
things this week. Answers vary. Temperature changes how much they vary. Longer
mail costs more tokens.

All three are properties of the same single call, and none of them needs new
code. The pre-written cells run the same `ask_model()` the student just wrote,
six times and then twice more. So the student writes one mechanism, then watches
it behave.

Why this is the right first capability. Every later week is this call plus one
addition. Week 2 fixes the shape of the answer. Week 3 changes what goes in.
Week 4 lets the model ask for a tool. Week 5 puts the call in a loop.

A student who never sees the bare call first will read the week 5 loop as magic.
The course's whole claim is that an agent is a loop around a call, not magic. So
the call has to come first, and it has to come alone.

Week 1 also carries the continuity promise. The first markdown cell tells
students two things in full. Their notebook work is saved for the term. Every
later starter notebook already contains a working version of everything through
the prior week.

This is said in week 1 so that nobody believes a bad week ends the course.

## 2. The lab deliverable

One text file, `week1_first_calls.txt`, written by a single pre-written export
cell.

The file holds, under plain headings: the two email ids used, the exact prompt
text sent, the six repeated answers for email 001 with the temperature beside
each one, the answer for email 002, and the session token totals.

A grader reads that file and can see whether the student's `ask_model()` worked,
whether the six answers actually differ, and what the run cost. No one has to
open or run the student's notebook.

## 3. What the student writes, and what arrives pre-written

Two TODO cells. Eleven to fourteen written lines in total, inside the course
target of 5 to 15 lines per lab. Blank lines and comments are not counted.

| TODO cell | What the student writes | Lines |
|---|---|---|
| TODO 1, notebook cell 7 | `ask_model(prompt, max_tokens=512, temperature=0.2)`. Builds the request dictionary, merges in the extra request fields, calls the pre-written `send_request()`, returns the answer text. | 8 to 10 |
| TODO 2, notebook cell 10 | No new function. Parses email 001, sends its body with a one-sentence instruction, prints the answer. | 3 to 4 |

Everything else in the notebook arrives finished. That is thirteen of fifteen
cells.

| Pre-written cell | What it gives the student |
|---|---|
| Configuration | The endpoint, the model name, the extra request fields, and the API key read from the environment |
| Token counter | A running count printed after every call |
| `send_request()` and `save_artifact()` | The one network call, and the export writer |
| `.eml` parser and `email_path()` | A raw mail file turned into a dictionary of facts |
| `show_email()` | Subject, sender and the first 400 characters printed |
| Check cell | Tests the student's `ask_model()` on one plain question |
| Temperature comparison | Six runs of the same prompt, three at 0.2 and three at 1.0 |
| Second email | Email 002 sent, with its token line |
| Export cell | Writes `week1_first_calls.txt` and prints its path |

The parser is worth naming for the program manager. Reading a raw mail file into
headers, authentication results, links and body text is not a 5 to 15 line job.
It is also not what week 1 teaches. So it ships as a module the student imports
and never edits.

The same is true of `send_request()`, which is the only place in the whole course
that touches the network. Students call it. They do not write it.

The configuration cell reads the API key from the student's environment. It
prints one line saying whether a key was found. It never prints the key, and no
cell in any week does.

## 4. Weekly objectives

Three objectives. All three parent to CLO2. Each names one observable thing the
student does in this week's lab.

On the page they sit under the template's lead sentence, "By the end of this
module, you will be able to:". Each one ends with its parent in brackets. That
is the resolution recorded as conflict 22 in the template conflicts document,
applied here rather than left open.

| # | Objective, as students see it | Verb | Words | Parent |
|---|---|---|---|---|
| 1.1 | Classify one email using a model call from your own code. (CLO2) | Classify | 11 | CLO2 |
| 1.2 | Record how the six answers to one email differ at two temperatures. (CLO2) | Record | 12 | CLO2 |
| 1.3 | Name one thing to check before trusting the model's answer. (CLO2) | Name | 10 | CLO2 |

Each is one sentence, under 20 words, with one measurable verb. None joins two
verbs with "and". None uses a banned verb. The bracketed parent is a tag rather
than part of the sentence, so the word column does not count it.

Why all three parent to CLO2. CLO2 asks a student to classify an email with a
model, then check the model's output before trusting it.

Objective 1.1 is that first act at its plainest depth. One email goes to the
model from the student's own code, and a phishing judgment comes back. Objective
1.2 produces the reason checking is needed, because one input gives six different
answers. Objective 1.3 is the first act of checking, done in plain language
before any code does it in week 2.

One act in this lab carries no parent, and this spec says so rather than
inventing one. The student writes `ask_model()`. Writing a Python function is not
named by any of the six course objectives.

The build prompt calls an unparented weekly objective an error to report, not a
reason to add a course objective. So the function is the means here, not an
objective in its own right. What the week measures is the classification the
function produces.

Depth is the other thing to notice. Week 1 collects supporting evidence for CLO2.
The primary evidence is the week 2 lab. Section 9 states how the two scores
interact.

## 5. The sidebars

The week 1 target names three things: calling a function, using what it returns,
and f-strings. An f-string is a Python string that drops values into a sentence.

Two sidebars cover the three, and the merge is worth arguing rather than
assuming. Calling a function and using what it returns are one construct, not
two. A return value only exists because a call was made, so a sidebar that showed
one without the other would show nothing.

Sidebar 1A carries that single construct. F-strings are a separate construct, so
they get sidebar 1B. Together the two are 25 minutes.

Line counts below are taken the same way for both sidebars: every line in the
code block, including the title comment and any blank line. Both sit well under
the 20 line ceiling.

**Chosen everyday domain: a grocery stockroom.** Never email. Never security.

### Sidebar 1A: call a function and keep what it hands back

Eleven lines. Runnable and complete.

```python
# Sidebar 1A: call a function and keep what it hands back
def boxes_in_cases(cases):
    return cases * 6

morning_boxes = boxes_in_cases(4)
afternoon_boxes = boxes_in_cases(9)
day_total = morning_boxes + afternoon_boxes

print(morning_boxes)
print(afternoon_boxes)
print(day_total)
```

The walkthrough explains it line by line at the course reading level.
`boxes_in_cases()` takes a number of cases. It hands back a number of boxes.

The three lines below it do the part the lab needs. Each call hands a value back.
Each value is kept in a name, so it can be used again. `day_total` is built from
two kept values. That works only because nothing was thrown away.

The lab does the same thing one layer down. The student's code calls a function
someone else wrote. It keeps what comes back and passes it on.

Nothing here needs a dictionary, a default value, or a comparison. Those belong
to later weeks. This sidebar stays inside what week 0 section 2 already taught.

**Try changing this.** Change the 9 to a 2. Predict all three printed lines
before you run it.

**Week 0 link.** Section 2, calling functions and using return values.

### Sidebar 1B: build a sentence from values with an f-string

Seven lines. Runnable and complete.

```python
# Sidebar 1B: build a sentence from values with an f-string
shelf_name = "rice"
on_hand = 4
low_mark = 5
note = f"{shelf_name}: {on_hand} boxes on hand, reorder at {low_mark}."
print(note)
print(f"Short by {low_mark - on_hand} box.")
```

The walkthrough shows that the `f` before the quote is what makes the braces
work, and that anything inside braces is worked out first and then dropped into
the sentence.

**Try changing this.** Add the day of the week to the note.

**Week 0 link.** Section 5, f-strings.

### Why pasting a sidebar into the lab fails

Neither sidebar shares a single name with the lab. The lab's check cell calls
`ask_model()`, which no sidebar defines, so a student who pastes sidebar code
into the TODO cell and runs the check cell gets `NameError: name 'ask_model' is
not defined` rather than a working lab.

## 6. The reading

One authored page, about 1,350 words, inside the 1,400 word ceiling the course
writing standard sets for a reading. It carries breadth topics B1 and B3, and it
is the only place either is taught before the final exam.

Worth naming for the program manager: 1,350 words is above the 900 to 1,050 word
target the same standard sets, though below its ceiling. This page carries two
breadth topics rather than one, which is why it runs long.

What it covers, in two parts.

Part one is B3, the parts of a security operations center. It defines ten things
in plain words: assets, users, networks, endpoints, logs, alerts, tickets,
incidents, escalation, and documentation.

A labeled diagram then shows how a reported email becomes an alert, then a
ticket, then either a closed ticket or an incident. The last paragraph puts a pin
on that diagram where this course's own agent sits, between the alert and the
ticket. This part doubles as the orientation the prerequisite course does not
supply.

Part two is B1, AI in IT and security operations broadly. It separates three
things students will otherwise blur together. Scoring AI sorts or rates
something, such as a spam filter. Generative AI writes new text or code, such as
a chat assistant. An agentic workflow decides its own next step and then acts.

Each of the three gets one plain definition and two examples from IT or security
work outside phishing. Students see the breadth before the course narrows.

Citations. The reading cites four authoritative sources and every one is checked
to resolve before publishing. Any claim an expert review cannot ground is
removed or flagged rather than kept quietly.

Estimated time: 40 minutes, which is the floor of the 40 to 50 minute reading
budget. It breaks down in three parts.

| Part of the reading | Words | Minutes |
|---|---|---|
| Part one, B3, the ten parts of a security operations center | 780 | 20 |
| Part two, B1, the three kinds of AI | 570 | 10 |
| Opening and skimming one of the four cited sources | | 10 |
| **Total** | **1,350** | **40** |

The course prices one reading pass at 200 words a minute, which is section 2 of
the survey content plan. At that rate this page reads once in 6.8 minutes. The
other 33 minutes are study time on ten first-time definitions, a labeled
diagram and one cited source. The same three-part split appears in sections 3.3
and 5.3 of the survey content plan, so the two documents now agree.

Week 1 is the week the build prompt names for verifying the time budget against a
real build. This figure should be re-measured after Phase 2 rather than trusted.

Week 1 also carries the course's heaviest first-time friction. Students open the
notebook server for the first time, meet a traceback for the first time, and find
out what a token counter is.

That friction is why the week wants slack, and section 11 shows where the slack
sits. It is not a reason to price the reading below its band, so the reading is
priced at the band.

## 7. The discussion prompt

Written out below exactly as students will see it. It carries B1 and B3. It
requires the student's own exported results, so a general opinion cannot answer
it. Estimated time 20 minutes, including one substantive reply.

This text is word for word the same as section 7 of the survey content plan. An
earlier draft here asked for about 200 words and set no reply length. Weeks 6
and 7 both ask for about 150 words and about 60, so 150 and 60 is the course
figure and this week now matches it.

---

**Where you have already met AI at work**

Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central.

Write about 150 words in your post. Write about 60 words in your reply.

**Part 1. Your own results.**

Open your file `week1_first_calls.txt`. Find the six answers your notebook gave to
the same email. Quote one short line from one answer. Say which temperature produced
it. Then name one thing that answer got right. Name one thing it got wrong or left
out. Use your own file. Do not use a classmate's.

**Part 2. Where you have met this before.**

Name one place you have already met AI in IT work or security work. It can be from a
job, from school, from home, or from the news. Then say which of these three kinds it
was.

- Scoring AI, which sorts or rates something. A spam filter is one.
- Generative AI, which writes new text or code. A chat assistant is one.
- An agentic workflow, where a tool picks its own next step and then acts.

Then name one part of a security operations center that your example touched. Pick
from this week's reading: assets, users, networks, endpoints, logs, alerts, tickets,
incidents, escalation, or documentation.

**Your reply.**

Reply to one classmate who named a different kind than you did. In two or three
sentences, say what would change in their example if the tool were agentic. Point to
a line in their post. A reply that only agrees does not count.

You may use AI help on this post. If you do, add one line saying what you asked it.

---

## 8. The submission artifacts

Three items. Nothing else. No zip files, no folders, no links.

**1. The screenshot.** One image of the output of notebook cell 11, the
temperature comparison cell. It must show all six answers. Cell 11 prints no key
material, and the lab page says so.

That cell prints no token line, so the screenshot requirement asks for none. The
code ledger sets cell 11 as six answers and nothing else. Token evidence reaches
the grader through the exported file instead, which section 2 lists as holding
the session token totals.

**2. The file.** `week1_first_calls.txt`, attached as a file. The pre-written
export cell in notebook cell 14 writes it and prints its full path, so the
student can see exactly what to attach.

**3. The written answer.** Three to five sentences, typed into the submission
box. The prompt reads:

> Answer all three questions in 3 to 5 sentences. (1) Which of your six answers
> differed most, and at which temperature? (2) What happened to the token count
> on email 002, and why? (3) What would you check before trusting this answer in
> a real ticket?

All three items are gradeable without running the student's notebook.

## 9. Rubric sketch

Four criteria, 100 points, four performance levels each. The four levels match
the mastery scale used across the course, so a rating maps straight across with
no translation step.

Every lab in the course carries 100 points, which is what makes the seven labs
weigh equally inside the 60 percent Labs group. The grade distribution and
token totals document holds the whole table.

| # | Criterion | Points | Canvas Outcome |
|---|---|---|---|
| 1 | Submission completeness. Screenshot, file and written answer are all present and readable. | 25 | None. Non-CLO expectation. |
| 2 | The call works. The file shows six answers for email 001. It shows one answer for email 002. Both show the prompt text you used. | 25 | CLO2, supporting evidence |
| 3 | Variation reported. The written answer names which answer differed most and at which temperature. | 25 | CLO2, supporting evidence |
| 4 | First judgment. The written answer names one specific thing to check before trusting the answer. | 25 | CLO2, supporting evidence |

Why three of the four link to CLO2. Each of the three measures an act named in a
week 1 objective, and all three objectives parent to CLO2. Section 4 sets that
out. The build prompt lets a criterion go unlinked only when it measures a
non-CLO expectation such as submission completeness. Criterion 1 is that case.
The other three are not, so they link.

This is a settled design, not an exception request. No exception to the
Outcome-link rule is being asked for in week 1.

What the link costs, stated plainly. The six Outcomes report the most recent
score, so a week 2 result replaces a week 1 result. CLO2's primary evidence is
the week 2 lab, which comes after this one. Nothing recorded here survives in the
reported number.

That replacement is the intended behavior. The week 1 score is not for the
roll-up. It gives the instructor a reading on every student one week before the
score that counts. A student whose own code cannot get an answer out of the model
in week 1 will struggle in week 2, and this criterion shows it a week early.

The alignment matrix states the same three links in its own table of rubric
criteria, so the two documents agree.

## 10. The self-check

Six multiple choice items in a Classic Quiz. Unlimited attempts, highest score
kept, no time limit. Low stakes by design, and part of the 8 percent that
self-checks carry across the course.

| Items | What they cover |
|---|---|
| 3 | B3, the parts of a security operations center. One asks which part a given line belongs to. One asks where this course's agent sits. One asks who receives an escalated ticket. |
| 2 | B1, the three kinds of AI. Each describes a tool in plain words and asks which kind it is. |
| 1 | The token counter. Asks what the running count is read from, and why it is not the length of the answer text. |

Every stem is scenario based and written at the same reading level as the rest of
the course. The last item matters more than it looks: on one of the two candidate
models the tokens spent thinking are billed but never shown, so a student who
measures the visible text would under-report by roughly ten times.

## 11. Time estimate

| Activity | Minutes | Budget |
|---|---|---|
| Overview video and the "what success looks like" walkthrough video | 10 | under 12 |
| Sidebars 1A and 1B | 25 | 20 to 30 |
| Reading | 40 | 40 to 50 |
| Lab | 150 | 150 to 180 |
| Discussion, post plus one reply | 20 | 15 to 20 |
| Self-check | 12 | 30 combined |
| Submission, screenshot and upload | 15 | 30 combined |
| **Total** | **272 minutes, 4 hours 32 minutes** | **under 360** |

The 150 lab minutes break down like this.

| Lab step | Minutes |
|---|---|
| Open the notebook, run the configuration and token cells | 15 |
| Read the pre-written helpers | 15 |
| TODO 1 and its check cell | 40 |
| TODO 2 | 20 |
| Run the temperature comparison, read six answers | 20 |
| Second email and its token count | 15 |
| Export cell and the screenshot | 15 |
| Held back for one traceback | 10 |

The week finishes 88 minutes under the 6 hour ceiling. Every item sits inside its
own band, and the slack is what is left over once each one is priced honestly.

That slack is not headroom to fill. It is what absorbs the first-run friction
described in section 6. The build prompt allows reading to be cut only when a
week runs past 6 hours, and this week does not, so no cut is taken.

## 12. Estimated tokens per full lab run

Week 1 sends no system prompt, no facts block, no tool results and no schema.
Those arrive in later weeks. The only prompt parts this week are a one-sentence
instruction and an email body.

The instruction the lab supplies is one sentence, 94 characters, plus a blank
line:

```
Read the email below. In two sentences, say whether it looks like a phishing attempt, and why.
```

The arithmetic, in three lines. Every character count is measured on the
shipped notebook and the rendered mail files.

1. A full run makes 9 calls. One is the plain check question, 56 characters, or
   14 tokens. Seven carry email 001: one in TODO 2 and six in the temperature
   cell. Its prompt is 96 characters of instruction and blank line plus 807
   characters of body, which is 903 characters, or 226 tokens. One carries
   email 002, whose body is 874 characters, so its prompt is 970 characters, or
   243 tokens. The prompt side is 14 plus 7 times 226 plus 243, which is 1,839
   tokens.
2. The serving stack measurements recorded 46 to 79 completion tokens for a short
   answer with reasoning switched off. Taking the top of that range and rounding
   up to 80 gives 9 times 80, which is 720 completion tokens.
3. One full run is 1,839 plus 720, which is **about 2,560 tokens**.

Those figures were taken by running the notebook's pre-written cells against a
stub model, with a reference solution in each of the two TODO cells, and reading
the counter the notebook prints.

One caveat the program manager should see.

The reasoning switch is what keeps this number small. One of the two candidate
models thinks before it answers by default, and those thinking tokens are billed.
The same short call measured 819 to 1,173 completion tokens in that mode, a mean
of 951. Nine calls at that mean would put a full run near 10,400 tokens, about
four times the 2,560 above.

The gap is wider on completion tokens alone, which is the side the switch acts
on: about 720 with reasoning off against about 8,600 with it on.

The notebook configuration cell turns that mode off. It sends `reasoning_effort`
set to `"none"`, and the Phase 2 author should use that field rather than
re-derive it. Two request forms turn reasoning fully off on this endpoint; the
other is `reasoning` set to an effort of none.

Five further ways of asking for the same thing were tested. Every one was
accepted and then ignored, with no warning and no error. A sixth was rejected
outright with an HTTP 400 error, so that one at least fails loudly. The five
ignored fields and the rejected one are listed in the serving stack document.

Practical budgeting figure: a student who debugs and reruns the lab once spends
about 5,100 tokens in week 1.

This week's figure and the six others sit in one table in the grade distribution
and token totals document, together with the course total.

## 13. Assumptions and open questions

1. Emails 001 and 002 are rendered as files, and the token estimate is measured
   on them rather than estimated. A change to either body moves the figure, so
   it is re-measured when the corpus changes.
2. Week 0 section numbers follow the order the build prompt lists them in.
   Calling functions and using return values is section 2. F-strings is section
   5. If the week 0 outline renumbers them, both sidebar links change.
3. The week 1 lab is worth 100 points, the same as every other lab. The Labs
   group is weighted 60 percent, and a percent-weighted group scores as points
   earned over points possible inside it. Equal points across the seven labs are
   therefore what makes the seven weigh equally. The grade distribution and
   token totals document sets the points for every graded item in the course.
4. Two videos are counted as 10 minutes together. The build prompt sets a 2 to 4
   minute overview video and a separate walkthrough video, with a combined
   ceiling of 12 minutes.
5. The self-check is set to unlimited attempts with the highest score kept. This
   is a judgment call about what "low stakes" means and it is easy to change
   before Phase 2.
6. The reading is priced at one pass of 200 words a minute plus study time, the
   one rate the course uses. No reading-rate measurement exists for this student
   population. Section 2 of the survey content plan states the rate and section
   6 above shows this page's split. The figure should be checked against a real
   week 1 build.

## Measured readability

Measured with the course readability gate on 2026-09-04. This is a program manager
document, so the whole page is held to grade 9.5, an average sentence of 18
words and no sentence over 45. Student-facing text drafted inside it is held to
grade 7 and an average sentence of 12 words.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 5.63 | 12.5 words | 39 words |
| The three objectives, section 4 | 5.81 | 11.0 words | 12 words |
| The discussion prompt, section 7 | 3.09 | 8.8 words | 17 words |
| The written answer prompt, section 8 | 4.54 | 11.5 words | 13 words |
| The rubric criterion column, section 9 | 4.75 | 8.3 words | 13 words |

No prose paragraph on this page runs over 70 words.

**How the short blocks were scored.** The readability tool declines to score
anything under 40 words. A block under that floor was repeated until it cleared
it and then scored, which is the method week 6 uses. Repeating text does not
move a Flesch-Kincaid grade, because the formula is a ratio of words to
sentences and syllables to words. A rubric row is the criterion column, each
cell read as one line, with the header row left out.

**Two numbers that moved.** Objective 1.1 read "Classify one suspicious email
using a model call from your own code." Scored on its own that sentence reads
grade 7.77, over the grade 7 ceiling. Dropping the word "suspicious" brings it
to 5.86 and loses nothing, because week 1 sends one phishing message and one
ordinary internal notice.

The rubric criterion column read grade 7.14, driven by an 18 word criterion 2.
Criterion 2 is now three short sentences and the column reads 4.75.
