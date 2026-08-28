::: intro
This page is the AI policy for ITSY 1377. It is different from the default
policy at the college, so read it even if you have read one before. It is also
the written permission that the district procedure requires.
:::

::: callout note | The short version
**AI assistance is permitted on all coding in this course.** You may use a
chat assistant, an editor that completes your code, or any similar tool.

Four conditions come with that permission:

1. You declare AI use wherever a submission asks for it.
2. Your Project 1 repository includes a file named `AI-USE.md` that documents
   at least one AI suggestion you **rejected**, and why.
3. You never paste an API key or personal information into a model.
4. You are responsible for everything you submit, including code you did not
   write yourself.

Break one of those and it is an academic integrity violation.
:::

::: section | Why AI is permitted here
Outcome 6 of this course is this: evaluate AI-generated code and output for
correctness before use.

That outcome is graded. To grade it, you have to produce AI-generated code and
then judge it. A course that bans AI cannot assess that skill at all. It can
only assert it.

So the ban would cost the course one of its six outcomes, and would buy nothing
in return. That is a bad trade, and this course does not make it.

There is a second reason, and it is the honest one. You are going to work
beside these tools for your whole career. Learning to check their output is the
job. Pretending they do not exist for eight weeks does not prepare you for a
single day of it.
:::

::: section | What is actually assessed
The code is not the whole grade. Understanding it is.

Every comprehension question in this course is anchored to your own run. Not to
a topic. To a file on your computer that nobody else has.

Here is the kind of question you get:

1. Enter the value of the `tool` field on line 3 of your own `ledger.jsonl`.
2. Given your retry settings, how many requests reach the endpoint before the
   exception?
3. Here are six versions of this function. Exactly one is correct. Which one?
4. Which line number in this file creates the injection sink?

A model cannot answer the first two. It has never seen your run, your canary
token, or the settings you chose. It can attempt the last two, and so can you,
and that is the point: those items assess whether you can spot a defect.

So AI is permitted, and on the questions that decide your grade it does not
help. That is a more honest position than a rule nobody can enforce.
:::

::: section | The four conditions in full
**1. Declare it where you are asked.**

Assignments that involve AI carry a short declaration box. Say which tool you
used and what you used it for. One or two sentences is enough. The final exam
is open book and AI is permitted on it, and it asks for the same declaration.

Declaring costs you nothing. Not declaring is the violation.

**2. Project 1 needs an `AI-USE.md` file.**

Your Project 1 repository has to include a file named `AI-USE.md`. It documents
three things:

- Which tools you used.
- What you used them for, in general terms.
- **At least one suggestion the tool gave you that you rejected, and why.**

That third item is the one that is graded. Paste the suggestion, then say what
was wrong with it. Maybe it called a function that does not exist. Maybe it
skipped the error path. Maybe it worked but ran the tool without checking who
was asking.

A file that says you accepted everything does not meet the requirement. If you
truly rejected nothing, you did not evaluate anything, and outcome 6 is exactly
that evaluation.

**3. Never paste a key or personal information into a model.**

An API key in a prompt is a leaked key. Treat it as leaked, turn it off at the
provider, and make a new one.

Personal information is the same problem in a different shape. A free hosted
model may use what you send it to improve the provider's products. Never send
your own details, a classmate's, or anything real from your job.

**4. You own what you submit.**

"The model wrote it" is not a defense, and it will not be treated as one.

If the code you submit is wrong, you are wrong. If it is insecure, you shipped
an insecure change. If it copied someone else's licensed work, you plagiarized.

This is not a course rule invented to be strict. It is how every engineering
job you will ever hold works. The person who commits the code owns the code.
:::

::: callout warning | Where AI quietly costs you
AI is very good at producing code that runs and is wrong in a way you will not
notice for two weeks.

Three failures show up every term in this course:

1. **Invented functions.** The model calls something that does not exist in
   your repository, because it exists in a different library.
2. **The missing error path.** The happy path works. The retry, the timeout,
   and the bad response are silently skipped.
3. **The confident wrong explanation.** You ask why a test failed, and you get
   a fluent answer about the wrong file.

Run it. Read it. Then decide. That order never changes.
:::

::: section | This course does not try to detect AI use
No detection tool is used here. No submission is scanned. Nobody is asked to
prove they wrote something.

That is a deliberate choice. Here is the reasoning, in full, so you can see it
is not an oversight.

**Detectors do not work well enough to accuse someone.** They produce false
positives. When they do, the student has to prove a negative, which is nearly
impossible and lands hardest on students who write in a second language.

**Detection would not work on code anyway.** Correct Python for a small function
looks the same no matter who or what wrote it.

**A rule nobody can enforce teaches the wrong lesson.** It tells students that
rules are theater and that the skill being rewarded is not getting caught.

So the design removes the incentive instead of policing the behavior. Anchor
the questions to your own run, and AI use becomes permitted and unprofitable at
the same time. That took work to build, and it is a better answer than
suspicion.

**None of this makes cheating acceptable.** Submitting a classmate's work is
still a violation. Fabricating a result is still a violation. Not declaring AI
use where asked is still a violation. The course simply does not pretend it can
detect what it cannot.
:::

::: callout tip | One place to leave the AI closed
Every week carries a Check Yourself block, on the content page or the wrap-up
page. Those questions are not graded. Nothing stops you from using AI on them.

Try them closed anyway. They are the cleanest measure you get of what you
actually understand. Getting one wrong there costs you nothing.

The graded work is where AI stops helping. Every comprehension item is anchored
to your own run, and no model can read your run. A gap you find on Wednesday in
a Check Yourself block is a gap you can close before Sunday.
:::

::: section | If you break a condition
An undeclared AI use, a missing or empty `AI-USE.md`, a key pasted into a
prompt, or code you cannot explain is handled as an academic integrity
violation. See the Academic Integrity page for what follows.

If you are unsure whether a use is allowed, ask on the Q and A board before you
submit. That question has never gotten anyone in trouble.
:::

::: next
Next is the Rules of Engagement. It is the most important page in the course,
and it is the one you take a quiz on before Week 2 opens.
:::
