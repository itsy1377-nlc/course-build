::: intro
This is the findings document for Project 2. It is the writing sample you could
show an employer.

It carries two findings. One fix you built and verified in Part A. One fix you
specify in writing, with the test that would prove it works.

It is due day 52 at 11:59 PM and it is worth 120 points.
:::

::: scope
Everything in this report describes testing against HelpDesk Lite on your own
computer, and nothing else. Read clause 1 and clause 2 of the Rules of
Engagement again before you write.

Every finding states its authorization basis in its own heading. A report that
does not say who authorized the test is not a professional report, whatever
else is in it.

Paste your `target.base_url` setting at the end of the file. It has to say
`http://127.0.0.1:8000`.
:::

::: callout stop | The word cap is 900 and it is hard
Nothing after word 900 is read or graded.

The 150 word answer at the end is separate. It is not counted in the 900.

There is no minimum. A short exact report scores higher than a long vague one,
every time. Cutting is part of the assignment.
:::

::: directions
**Step 1: run the harness one more time.**

Do this before you write anything, so your numbers are current:

```
python -m target.seed
python -m target.app
python -m harness.runner
```

Your newest file in `runs/reports/` is the source for every number in the
report. Do not quote a run from last week.

**Step 2: write finding one, the fix you built.**

Use the Findings Report Template page. Fill in all eight headings.

This finding covers the remediation you implemented and verified in Part A. The
Verification heading needs two results side by side:

1. The attack case, re-run, with its rate.
2. The benign baseline control, showing normal use still works.

One result without the other proves nothing. A fix that stops the attack and
also breaks the product is not a fix.

**Step 3: write finding two, the fix you specify.**

Pick a second weakness your harness found. Do not build the fix. Write it.

Under Remediation applied, describe the change you would make: the file, the
function, and the rule. Then, under Verification, write the test that would
prove it worked. Be exact:

1. The case you would run, and how many trials.
2. What the detector would have to look at.
3. The result that would count as fixed, and the result that would not.

A specification a classmate could implement without asking you a question is
the bar.

**Step 4: answer the free-text prompt.**

One question, 150 words at most:

**What defect do you know remains in your fix?**

Answer it honestly. Every control has an edge it does not cover. Naming yours
is worth more here than claiming there is none. An answer of "none" scores
zero on that row.

**What to hand in.** One file, markdown or PDF, containing:

- Finding one, on the template, all eight headings.
- Finding two, on the template, all eight headings.
- Your 150 word answer, under its own heading.
- Your `target.base_url` line, pasted.
- One sentence saying whether you worked from a fallback branch.
:::

::: callout note | One fix built and one fix written is a real cost, and it is named here
This assignment used to ask for two working remediations. The shortened
calendar cut it to one built and one specified.

That is a genuine loss, not a design improvement. A written specification is
weaker evidence than a working fix. The course says so plainly rather than
pretending the smaller version teaches the same thing.

You still demonstrate the full loop once: attack, fix, re-test, confirm normal
use survives. The second finding shows you can plan the loop without running
it.
:::

::: callout warning | Three ways good work loses points here
**Evidence that is only the model's account.** Quote the outbox file, the
audit row, or the canary. Never the transcript.

**A result without a rate.** "Vulnerable" hides the gap between 1 of 5 and 5 of
5. Write the rate every time.

**A verification with only half the picture.** Attack blocked, benign baseline
not mentioned. That is an incomplete claim.
:::

::: submit
Upload one file. Markdown or PDF.

Name it `partb-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
