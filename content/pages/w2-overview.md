::: intro
This week you put a real model on the other end of the line. You add an API key,
send a request, and pull one value out of the reply that comes back.
:::

::: objectives
By the end of this week, you will be able to:

- 2.1. Read a loop, a conditional, and a function in the lab code, and say what
  each one does.
- 2.2. Name every field in an OpenAI-compatible chat completions request and say
  what it is for.
- 2.3. Pull a value out of a nested dictionary in a model's reply, including the
  tool call arguments.
- 2.4. Explain why the labs pin every package to an exact version.
:::

::: scope
You attack nothing this week either. You do point code at a real service for the
first time, so clause 2 and clause 3 of the Rules of Engagement now apply to
you in practice.

You send ordinary requests to your provider. You never test its safety filters.
That is out of scope for the whole course.
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

The assignment and the quiz share a deadline. Do the assignment first. Several
quiz questions ask about your own results.
:::

::: callout warning | Set up your key early, not on day 14
Getting a key involves a signup, and signups sometimes take a day. Providers
also change their free tiers without warning.

Do this on day 8 or day 9. If your provider is not working, you have a week to
switch to another one, and the Course Material page lists more than one.

Your key goes in a file named `.env`, and nowhere else. Never in
`lab.config.yaml`, never in a forum post, never in a screenshot.
:::

::: callout time | About how long this takes
The content page: about 60 minutes.

The two readings: about 35 minutes in total.

Getting a key and running `verify_env.py --live`: about 30 minutes.

Module 1, the three functions plus testing: about 4 hours.

The comprehension quiz: about 45 minutes.

That is about 7 hours in total.

The three functions in Module 1 are small. If one of them takes you more than an
hour, you are probably guessing instead of reading the test file. The tests say
exactly what is expected.
:::

::: next
Week 3 flips the direction of everything you learned this week.

So far your script calls the model. Next week the model calls your functions.
That inversion is the hardest idea in the course, and the whole week is built
around it.

You will also learn what a JSON tool schema is, and why the description you
write in it is read by the model rather than by a person.
:::
