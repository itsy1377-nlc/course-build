::: learned
- A model reads text and writes text. A tool does things. An agent is a loop
  that joins the two.
- An agent fails differently for three reasons: it can act, its input includes
  text strangers wrote, and it cannot reliably tell instructions from data.
- An agent does not fail the same way twice, so you test it many times and
  report a rate.
- Authorization comes before technique. You may attack three things and nothing
  else.
- A list is found by position, starting at zero. A dictionary is found by key.
- A value inside a dictionary can be another dictionary. That is how a model
  reply is built.
:::

::: did
- Set up Python and a virtual environment, with no other installs.
- Ran `python verify_env.py` and read all nine checks.
- Passed the Module 0 Gate, which verified your attendance for the term.
- Read the Rules of Engagement and were graded on it.
- Read two short sections of the Python Tutorial.
- Read real lab code and predicted what it printed, then checked yourself.
- Answered three questions about what a dictionary lookup returned.
:::

::: checkpoint
Answer these before Week 2 opens. They are the shape of questions you will see
again.

1. Your agent has one tool that reads tickets and one tool that sends mail. Why
   is that pair more dangerous than either tool alone?
2. A classmate says the fix is to tell the model to ignore instructions inside
   ticket text. Name one reason that might not hold.
3. You ran an attack once and it worked. What can you honestly write down?
4. `tokens["kb"]` returns a string. `tokens[2]` raises an error. Explain why in
   one sentence.
5. You may attack three things. If you cannot name all three from memory, open
   the Rules of Engagement again now.

**Answers:**

1. Reading brings in text a stranger wrote. Sending acts on the world outside.
   Together they give a stranger's words a path to a real action.
2. A system prompt is a request, not a control. The model reads the rule and
   the ticket in the same list, so it can be talked out of the rule.
3. That it worked once. An agent does not fail the same way twice, so you run
   it several times and report a rate.
4. A dictionary is found by key, and `2` is not one of its keys. Position only
   works on a list.
5. The HelpDesk Lite app, your own copy of the agent, and a model running on
   your own computer. Nothing else, ever.
:::

::: next
Week 2 puts a real model on the other end of the line.

You add an API key, you send your first request, and you read what comes back.
The reply is a dictionary with a list inside it and more dictionaries inside
that. Getting one value out of it is the skill the whole week is built on.

You also meet the reason the labs pin every package to an exact version. The
short answer is that installing a package runs somebody else's code on your
computer.

One thing to do before day 8: get an API key. The Course Material page lists the
free options. Do not put it anywhere yet.
:::
