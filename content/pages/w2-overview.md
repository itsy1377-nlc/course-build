::: intro
This week you put a real model on the other end of the line. You add an API key,
send a request, and read the reply.
:::

::: objectives
By the end of this week, you will be able to:

- 2.1. Read a loop, a conditional, and a function in the lab code.
- 2.2. Name every field in an OpenAI-compatible chat completions request.
- 2.3. Pull a value out of a nested dictionary in a model's reply.
- 2.4. Explain why the labs pin every package to an exact version.

These serve course outcomes O1 (scripting against a model API) and O6
(checking AI-written code).
:::

::: scope
You attack nothing this week. You do point code at a real service for the first
time, so clauses 2 and 3 of the Rules of Engagement now apply in practice.

Never test your provider's safety filters.
:::

::: tasks
| Activity | Objectives | Due |
|---|---|---|
| Read the Week 2 content page | 2.1, 2.2, 2.3 | day 10 |
| Reading: the Requests Quickstart, with the bridge on the content page | 2.2 | day 10 |
| Reading: the chat completions reference, with its bridge | 2.2, 2.3 | day 10 |
| Get an API key, set up `.env`, run `python verify_env.py --live` | 2.2 | day 11 |
| **Module 1: Talk to the Model**, 90 points | 2.1, 2.3 | day 14, Sunday 11:59 PM |
| **Module 1 Comprehension** quiz, 50 points, one attempt | 2.2, 2.3, 2.4 | day 14, Sunday 11:59 PM |

Do the assignment first. Several quiz questions ask about your own results.
:::

::: callout warning | Set up your key on day 8, not day 14
Signups sometimes take a day, and free tiers change without warning. Start
early and you can still switch. The Course Material page lists more than one
provider.

Your key goes in `.env`, and nowhere else.
:::

::: callout time | About how long this takes
The content page: about 60 minutes.
The two readings: about 35 minutes in total.
Getting a key and running `verify_env.py --live`: about 30 minutes.
Module 1, the three functions plus testing: about 4 hours.
The comprehension quiz: about 45 minutes.

That is about 7 hours of assigned work in total.

If programming is new to you, the coding parts commonly take two to three
times as long. That wider range is normal, not a sign of falling behind.
:::

::: next
Week 3 flips the direction. The model calls your functions, and the whole week
is built around that.
:::
