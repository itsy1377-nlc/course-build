::: learned | What You Learned
1. A control is a rule that decides whether an action runs.
2. A rule in the prompt is advice. It competes with every other word the model
   reads, and it does not run the tool.
3. Code at the tool boundary decides. It sees the tool name and the arguments,
   and it returns allow or block with a reason.
4. Deny by default. A list of what is allowed holds better than a list of what is
   banned.
5. A control that breaks legitimate work is not finished.
:::

::: did | What You Did
1. Turned your week 5 recommendation into one sentence naming a tool and an
   argument.
2. Measured a baseline over five trials, with nothing in place.
3. Wrote the rule into the system prompt and measured it the same way.
4. Wrote the control in code at the tool boundary and measured it again.
5. Confirmed ordinary work still finishes, and quoted the record that shows your
   control acting.
:::

::: checkpoint | Check Yourself
1. Your prompt version comes back FLAKY. What does that tell you about it?
2. Why do you take the prompt rule out before measuring the code version?
3. Your control blocks the tool and the agent replies that it has sent the mail.
   What decides?
4. Your report shows no hits in five trials. May you write "this attack is
   impossible now"?
5. A classmate blocks every outbound message and reports a perfect result. What
   is wrong with it?

Answers:

1. It held in some trials and not others. A fix has to hold all five times, so
   it has failed.
2. So the numbers say which rule held. With both in place, they cannot.
3. The record. Look for the blocked line with your reason, and check the outbox.
   What the agent says about itself never decides anything here.
4. No. Five clean trials mean the harness did not see it land. That is a smaller
   claim, and it is the honest one.
5. It stops the work as well as the attack. Their benign case will fail, and a
   control nobody can live with gets turned off.
:::

::: next | What's Next
Week 7 puts your control in front of the whole class pool, live, while the board
updates. You get one revision and one more run.

Then you point the finished control at your week 3 case and find the part it
cannot touch. Bring this week's three reports; you compare against them.
:::
