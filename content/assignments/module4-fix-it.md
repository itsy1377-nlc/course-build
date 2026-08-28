::: intro
This is Project 2 Part A. You extend the harness with cases of your own, build
one real fix in code, and prove it held.

Due Sunday 11:59 PM of week 7, which is day 49.
:::

::: scope
Everything here runs against the HelpDesk Lite app on your own computer,
including the cases you write yourself. Read clause 1 of the Rules of
Engagement again before you start.

Every case file you add carries `authorized: true`. The runner refuses a case
without it.

Your submission includes the target line from your harness run. It has to say
`http://127.0.0.1:8000`.
:::

::: directions
**Part 1: add at least two attack cases.**

Write two new YAML files in `harness/cases/`. Each one needs `kind: attack`
and a detector that is a side effect, a canary, or a tool shape.

Confirm the harness loaded them:

```
python -m harness.runner --list
```

The case you wrote for the Project 2 checkpoint counts as one of the two, if
it is an attack case.

**Part 2: run the harness and record the before numbers.**

Start the target in one terminal, then run the full harness in another:

```
python -m target.seed
python -m target.app
python -m harness.runner
```

Save the results file. You need these numbers later, and you cannot get them
back after you change the code.

**Part 3: build one fix at extension point 1.**

Open `agent/loop.py` and find `before_tool_call()`. That function is the only
place your fix belongs.

It runs after the model asks for a tool and before the tool runs. Return
`True` and an empty string to allow a call. Return `False` and a reason to
block it. Write a real reason, because it goes into the ledger as evidence.

Your fix has to stop case `A2-indirect-injection-ticket` from landing.

Two rules about the fix itself:

1. **It goes in code.** A sentence added to the system prompt is not a fix,
   and your numbers will show it.
2. **It fixes the class, not one address.** More on that below.

There is a setting named `recipient_allowlist` in `config/lab.config.yaml`,
and it currently holds nothing. You may use it or ignore it. What matters is
the rule you write, not where you keep the list.

**Part 4: run the harness again and record the after numbers.**

Run the whole harness again, the same way. You now have two results files.

**Part 5: check your work.**

```
python -m pytest tests/test_module4.py -q
```

Run it as many times as you like before the deadline. Paste the final output
into your file, passing or not.

**Part 6: the Reading Results exercise.**

Answer the two questions from the Reading Results page about
`labs/harness/fixtures/poisoned-results.json`. Three to five sentences each.

**Part 7: the question a person reads.**

In 150 words or fewer, answer this:

**What defect do you know remains in your fix?**

Not a guess about what might be wrong. Something you know. You built the
control, so you know where it is thin.

Three honest answers, as examples:

- An attacker could reach a permitted address that forwards elsewhere.
- Your rule covers one tool. The other tools are untouched.
- Your check runs inside the agent. Anything that calls the target directly
  walks around it.

There is no penalty for naming a real limit. There is a penalty for writing
that your fix is complete.

**What to hand in.**

- One file, markdown or PDF, containing your before numbers, your after
  numbers, your pytest output, your two Reading Results answers, your
  150-word answer, and the target line from your run.
- Your modified `agent/loop.py`.
- Your new case files.
:::

::: callout stop | A fix is graded on two suites, not one
Your fix has to do two things at once.

1. The attack has to stop landing. Every trial, not most of them.
2. Normal use has to keep working.

The second rule is there for an obvious reason. Delete `send_email` and every
attack case in the folder passes. The system would be perfectly secure and
completely useless.

So the benign baseline runs too, and it has to stay green. A control that
blocks everything is not a control.
:::

::: callout warning | Fix the class, not the instance
One attacker address appears in the attack case. You could block that one
string and watch every attack case turn green.

Do not do that. The next attacker uses a different address.

There is a check in the test file you have not thought about yet. It sends
mail to an address inside the company that the support team needs to reach,
and it expects your guard to allow it through. A rule that names only the
attacker's address will pass every attack case and fail that check.

Fixing the class means deciding which recipients are allowed at all, and
refusing the rest. Ask one question of your rule: does it still work against
someone who has read my code?
:::

::: callout tip | If your numbers move around between runs
An attack that lands 2 times in 5 after your fix is not partly fixed.

That result usually means the change lives in the system prompt rather than in
`before_tool_call()`. Prompt text asks. Code decides.

Move the rule into the function and run it again.
:::

::: grading
| Criterion | Points |
|---|---|
| Two or more new attack cases, loaded by the harness, each with a real detector | 20 |
| Before run recorded, with a status and a rate for every case | 5 |
| One fix implemented in code at extension point 1, with a reason string | 20 |
| After run recorded, showing the attack case landing in 0 of 5 trials | 15 |
| Benign baseline still passing after the fix | 10 |
| Output of the Module 4 test file, pasted | 5 |
| Reading Results: both answers, specific and grounded in the file | 10 |
| The 150-word answer on the defect that remains | 5 |
| Target address in scope | 0, and the submission is not graded without it |
| **Total** | **90** |

The 150-word answer and the Reading Results answers are read by a person. The
rest is checked against your results files and the test output.

This assignment is paired with the Module 4 comprehension quiz, worth 50
points, with the same deadline.
:::

::: submit
Upload your report file plus your changed code and case files. Canvas accepts
several files on one submission.

Name the report `module4-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
