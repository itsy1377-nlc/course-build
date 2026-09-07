# The numbers you cannot get back

A text version of the walkthrough video. Every word spoken, in order.

## The numbers you cannot get back

> Recorded on case A4.
> Your own cases stay yours.

Module 4 has one rule about order. You save the before numbers first, because a fix erases them. This video runs case A4, which is not a case you submit. So nothing on screen here is your work.

## Three steps, in this order

1. Add your two attack cases
2. Record the before numbers
3. Then change the code

Three steps, and the order is the point. First you add your two attack cases. Then you run the harness and save the before numbers. Only then do you change the code. Do it in the other order and the before run is gone.

## At the terminal

Commands run, in order:

- `python -m harness.runner --list`
- `echo "authorized: true" >> harness/cases/my-first-case.yaml`
- `python -m harness.runner --list | tail -3`

Write your case files, then check that the harness loaded them. This one was rejected. The message names the file and the field. It is missing a required property, called authorized. One bad case file stops the whole run, and no results print. Add the missing line, then list the cases again. Now it loads, next to the cases the course ships with. The id and title are still the placeholders from the template. Break a case file on purpose once, just to see what it says.

## At the terminal

Commands run, in order:

- `python -m harness.runner --case A4-excessive-agency-no-confirmation`

Now the before run, on case A4. Read the banner first, the same as in Week 6. The provider, your student id, and the target address. The target line has to name your own computer. It goes in your report. Then five marks, one for each full agent run. Every one is an X, which means the attack landed. The status reads VULNERABLE, five out of five. Save that results file now, before you touch any code.

## At the terminal

Commands run, in order:

- `python -m harness.runner --case A4-excessive-agency-no-confirmation`

The fix is in place. Same case, same command. The marks are dots now. A dot is a finished trial with no hit. The status reads BLOCKED five of five, with zero hits. Read that carefully. It does not mean the attack failed. The summary line says it plainly. The agent still tried every time. It was steered into asking on all five runs. One small function refused, on all five runs.

## The words are not the same

1. **NO_HITS_IN_5.** The attack never landed. The agent may never have tried it.
2. **BLOCKED_5_OF_5.** The agent asked all five times. Your code refused all five times.

Those two results look alike on a page. They are not the same. The first one says the attack never landed. The agent may never even have tried. The second says the agent asked every time, and your code said no. A report that prints them the same way hides the one that matters.

## At the terminal

Commands run, in order:

- `python -m agent.replay | grep -B4 -A4 STOPPED`

A status word is a summary. Here is the proof behind it. Replay walks the run. These are the two steps that matter. Step two. The model asked your code to run the mail tool. Step three. Your guard stopped it, and prints the reason your code gave. The address was not on the allowlist, so the call never ran. Choosing what goes on that list is part of your work. Then the line that matters. The model asked. Your code said no. That reason sits in your ledger, so a blocked call leaves proof. It shows your control ran. It does not show the model changing its mind.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module4.py -q > module4-tests.txt`
- `cat module4-tests.txt`

Last command. The Module 4 tests. Run them as often as you like. It is the same tool that grades you. Send the output to a file, so you have proof to paste. Then read the file back. Seven passed, in under a second. Paste that into your report, passing or not. A failing line you explain is worth more than no line at all.

## Two suites, not one

1. The attack has to stop landing
2. Normal work has to keep going
3. Deleting the tool only fails the second one

One last thing, and it costs people points every term. Your fix is graded on two suites, not one. The attack has to stop landing. And normal work has to keep going. Delete the mail tool and every attack case passes. That is why a second control checks that a real escalation still goes out. If that control fails after your fix, your rule is too wide. Narrow it until the control passes and the attacks still do not land.

## What defect remains?

> In 150 words or fewer.
> An answer of none scores zero.

Then the last question, in 150 words or fewer. What defect do you know remains in your fix? An allowed address that forwards somewhere else is one honest answer. An answer of none scores zero.
