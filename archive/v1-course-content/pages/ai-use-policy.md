::: keyfacts
| | |
|---|---|
| AI on coding | Permitted, on all of it |
| Also permitted on | The final exam (open book) |
| You must declare it | Wherever a submission asks |
| Project 1 must include | `AI-USE.md`, with one suggestion you rejected |
| Never send a model | An API key, or anyone's personal information |
| Detection | None. No submission is scanned |
| Breaking a condition | An academic integrity violation |
:::

::: intro
This policy is different from the college default, and it is the written
permission the district procedure requires.
:::

::: section | Why AI is permitted here
Outcome 6 of this course is to evaluate AI-generated code for correctness before
use. That outcome is graded.

To grade it, you have to produce AI-generated code and then judge it. **A course
that bans AI cannot assess that skill.** It can only assert it.

You will work beside these tools all your career. Checking their output is the
job.
:::

::: section | The four conditions
**1. Declare it where you are asked.** Say which tool and what for. One or two
sentences.

**2. Project 1 needs an `AI-USE.md` file.** It lists your tools, what you used
them for, and **at least one suggestion you rejected, and why.** Paste the
suggestion, then say what was wrong with it. A file that accepted everything
does not meet the requirement.

**3. Never paste a key or personal information into a model.** A key in a prompt
is a leaked key: turn it off at the provider and make a new one. A free hosted
model may use what you send it to improve the provider's products.

**4. You own what you submit.** "The model wrote it" is not a defense. If the
code is wrong, you are wrong. Every engineering job works this way.
:::

::: section | What is actually assessed
The code is not the whole grade. Understanding it is. Every comprehension
question is anchored to your own run, not to a topic.

1. Enter the value of the `tool` field on line 3 of your own `ledger.jsonl`.
2. Given your retry settings, how many requests reach the endpoint?
3. Here are six versions of this function. Exactly one is correct. Which one?
4. Which line number in this file creates the injection sink?

No model has seen your run, your canary token, or your settings. So AI is
permitted, and on the questions that decide your grade it does not help.
:::

::: callout warning | Where AI quietly costs you
AI is good at code that runs and is wrong in a way you will not notice for two
weeks. Three failures show up every term:

1. **Invented functions** that exist in some other library.
2. **The missing error path.** The retry, the timeout, and the bad response are
   skipped.
3. **The confident wrong explanation** about the wrong file.

Run it. Read it. Then decide.
:::

::: section | This course does not try to detect AI use
Detectors produce false positives, and the accused student then has to prove a
negative. That lands hardest on students writing in a second language. Correct
Python for a small function looks the same whoever wrote it.

So the design removes the incentive instead of policing the behavior. Cheating
is still cheating: a classmate's work, a fabricated result, or an undeclared AI
use is still a violation.
:::

::: next
Next is the Rules of Engagement, the page you take a quiz on before Week 2
opens.
:::
