::: intro
This week you build. You finish the customer lookup tool, and you design a tool
of your own with a schema you write yourself. That work is Project 1, and it is
due on day 28.
:::

::: objectives
By the end of this week, you will be able to:

- 4.1. Trace one run of the agent loop by hand and say what the message list
  holds at each step.
- 4.2. Explain how a tool result gets back to the model, and why that matters.
- 4.3. Write a tool function with a working error path.
- 4.4. Design a tool and write the JSON schema that describes it.

These serve course outcomes O2 (extending an agent with tools), O1 (scripting
against a model API), and O6 (checking AI-written code).
:::

::: tasks
| Activity | Objectives | Due |
|---|---|---|
| Read the Week 4 content page | 4.1, 4.2 | Wednesday |
| Trace the loop on paper, then run it and compare | 4.1 | Wednesday |
| Reading: the chat completions response shape, with the bridge on the content page | 4.2 | Wednesday |
| Module 2: Give It Hands, both parts | 4.3, 4.4 | Sunday 11:59 PM, day 28 |
| Module 2 comprehension quiz | 4.1, 4.2 | Sunday 11:59 PM, day 28 |

Module 2 and the quiz are separate items in Canvas. They share one deadline.
:::

::: callout note | Do the paper trace first
The paper trace is not a warm-up and it is not optional busywork.

Students who trace the loop before they open the editor finish Module 2 in
about half the time. Students who skip it spend that time in the debugger
instead, working out what the message list holds.

Directions are on the content page. It takes about 30 minutes.
:::

::: callout time | About how long this takes
The content page: about 45 minutes.
The reading, with the bridge: about 20 minutes.
The paper trace: about 30 minutes.
Module 2 part one, `get_customer`: about 2 hours.
Module 2 part two, your own tool: about 3 hours.
Written answers and `AI-USE.md`: about 1 hour.
The comprehension quiz: about 30 minutes.

That is about 8 hours of assigned work in total, which is the heaviest week in
the course.

If programming is new to you, the coding parts commonly take two to three
times as long. That wider range is normal, not a sign of falling behind.

Part two takes longer than part one, and the extra time goes into the schema
rather than the Python. That is the design of the assignment, not a problem
with it.
:::

::: next
Week 5 is where the security arc starts. You will write an attack instead of a
feature.

You will find out what happens when someone writes a support ticket on purpose
to steer your agent. The agent you attack is the one you built this week, with
the tools you chose.
:::
