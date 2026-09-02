::: learned | What You Learned
1. The model picks a tool from three things: the name, the description, and the
   input schema. It never sees the code.
2. A description is a control surface. Whoever writes it steers the agent.
3. One run is an anecdote. A grid of thirty trials is a measurement.
4. A grid that did not move is a real result, and it supports a narrow claim.
5. Your tool descriptions sit in the model's input and are paid for on every
   call.
:::

::: did | What You Did
1. Ran two tools with the same code and different descriptions, thirty times.
2. Re-ran your errored trials and reported how many that took.
3. Changed one word, ran thirty more trials, and put the two grids side by side.
4. Found one edit that moved the split and one that did not.
5. Opened the model's real input and found your own words in it, with a token
   count.
6. Cited a file, a line and a field for the tool that ran.
:::

::: checkpoint | Check Yourself
1. A classmate writes: "my edit made no difference." What is wrong with that
   sentence?
2. Your split went from 18 and 12 to 17 and 13 across thirty trials each. Did
   the edit work?
3. You changed the description and the tool name in the same pass. What did you
   lose?
4. Six trials errored. Do those six squares belong in your grid of thirty?
5. Your description is 40 tokens long and the run makes eight calls. How often
   is that description sent?

Answers:

1. It claims more than a grid can carry. Write what you tested: this edit did
   not clearly move the split in thirty trials on this model.
2. You cannot say. That is a small shift, and thirty trials cannot separate it
   from ordinary variation.
3. The comparison. Two things changed, so nothing tells you which one mattered.
4. No. Re-run them until they finish, then count thirty finished trials. Report
   the number of re-runs.
5. Eight times. Every call carries the whole tool list, so a long description is
   charged again on each one.
:::

::: next | What's Next
Week 3 puts you on the other side of this. You choose one hidden effect from a
menu, then write the description that keeps it quiet. A generator turns your
plan into real Python, and three classmates receive it with no label on it. You
receive three of theirs and get forty five minutes to work out what each one
really does.

This week you learned that words steer the model. Next week you find out what
happens when the words are chosen to mislead a person instead.
:::
