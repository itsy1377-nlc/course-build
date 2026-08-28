::: intro
Run the shipped harness against your own agent, without changing it. Read
every part of what it prints. Capture the results, the evidence, and the two
control lines. Then answer the four questions from the walkthrough page.

This is one file with one deadline, due Sunday 11:59 PM of week 6, which is
day 42.
:::

::: scope
You run this against the HelpDesk Lite app on your own computer, and nowhere
else. Read clause 1 and clause 2 of the Rules of Engagement before you start.

Your submission includes the target line from your run. It has to say
`http://127.0.0.1:8000`.

The harness also finds a second address during discovery and refuses to touch
it. That refusal is part of what you hand in.
:::

::: directions
**Step 1: start the target.**

Open a terminal and leave this running:

```
python -m target.seed
python -m target.app
```

**Step 2: run the whole harness, unmodified.**

In a second terminal:

```
python -m harness.runner
```

Do not pass `--case`. Do not pass `--trials`. Do not edit any case file for
this assignment. You are reading the shipped tool as it ships.

This takes a while. The harness pauses between trials so a free endpoint does
not cut you off. Let it finish.

**Step 3: capture six things from the run.**

1. **The banner.** Provider, student ID, target address, case counts, pacing.
2. **The out-of-scope line.** The address the harness found and refused.
3. **The detector self-test line**, with the number of probes that passed.
4. **The control result** for the benign baseline.
5. **The results table**, with a status and a rate for every case.
6. **The evidence line** for at least three cases. Copy it. Do not describe it.

The two reports in `runs/reports/` have all of this. Paste from the markdown
one rather than retyping.

**Step 4: answer one short question about the controls.**

In two sentences, say what would be true about your results if the detector
self-test had failed, and why the harness prints nothing when it does.

**Step 5: answer the four walkthrough questions.**

They are at the end of the Week 6 authorization walkthrough page. Two or three
sentences each. Quote code or name lines where it helps.

**What to hand in.** One file, markdown or PDF, containing:

- The six captured items from step 3.
- Your two-sentence answer from step 4.
- Your four walkthrough answers from step 5.
:::

::: callout warning | Two ways to lose points that have nothing to do with skill
**Reporting a status with no rate.** The word "vulnerable" hides the
difference between 1 of 5 and 5 of 5. Always give the rate.

**Reporting what the model said as evidence.** The agent announcing that it
will email a record proves nothing. The evidence is a file in the outbox, a
row in the audit log, or a canary token found where it does not belong.
:::

::: callout tip | If the run stops before it prints results
That is the harness doing its job, not breaking.

A failed control means either the target was not reset, or something is left
in `target/outbox/`, or the detectors are broken. Fix the cause and run again.

Report the failure honestly if it happens more than once. A run that stopped
is a real finding about your environment, and it is worth more than a made-up
table.
:::

::: submit
Upload one file. Markdown or PDF.

Name it `module3-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
