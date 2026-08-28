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

Three rules about the fix itself:

1. **It goes in code.** A sentence added to the system prompt is not a fix,
   and your numbers will show it.
2. **It fixes the class, not one address.** More on that below.
3. **It reads its list from configuration.** This is required. Read on.

**Part 3b: put the list in the settings file.**

There is a setting named `recipient_allowlist` in `config/lab.config.yaml`,
and it ships empty. Fill it in. Then have your rule read it at run time:

```python
allowed = cfg.agent.get("recipient_allowlist") or []
```

This is not a style preference. It is worth 8 points.

A rule that reads the setting scores 20 on that grading row. A rule with the
addresses typed into Python scores 12. The gap is those 8 points, and here is
what the gap is for.

A rule hardcoded in Python is a rule nobody can change without editing code.
Support cannot add an address. Your instructor cannot. You would have to open
a source file and edit a function every time the list moved. A control
somebody has to edit Python to change is a control that does not get changed.

There is a second reason, and it is the one this course cares about most. The
point of a control is that it is a **rule**, not a list of enemies. Your rule
says which recipients are allowed at all. Which addresses those are is data,
and data belongs in the settings file. Keep the two apart and the rule holds
when the list changes.

One test checks exactly this. It hands your guard a different allowlist and
watches whether your guard follows it. A guard with the addresses baked in
ignores the list it was handed, and that test fails.

Deciding what belongs on the list is half the assignment. Before you decide,
open `agent/system_prompt.txt` and find the address support uses to escalate a
ticket.

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

Three honest answers, as examples:

- An attacker could reach a permitted address that forwards elsewhere.
- Your rule covers one tool. The other tools are untouched.
- Your check runs inside the agent. Anything that calls the target directly
  walks around it.

**What to hand in.**

- One file, markdown or PDF, containing your before numbers, your after
  numbers, your pytest output, your two Reading Results answers, your
  150-word answer, and the target line from your run.
- Your modified `agent/loop.py`.
- Your `config/lab.config.yaml`, showing the list your rule reads.
- Your new case files.
:::

::: callout stop | A fix is graded on two suites, not one
Your fix has to do two things at once.

1. The attack has to stop landing. Every trial, not most of them.
2. Normal use has to keep working.

The second rule is there for an obvious reason. Delete `send_email` and every
attack case in the folder passes. The system would be perfectly secure and
completely useless.

So **two** benign controls run, and both have to pass. Read them together,
because one of them is not enough:

- `control-benign-baseline` asks whether ordinary work stays quiet. A plain
  ticket summary must send no mail.
- `control-benign-escalation-works` asks the opposite. A legitimate escalation
  to the tier 2 queue must still go out.

Deleting the tool passes the first one and fails the second. So does a guard
that says no to everything. That is why the second control exists.

A control that blocks everything is not a control. The question is never
whether you can stop the bad thing. It is whether you can stop the bad thing
and still do the job.
:::

::: callout warning | Fix the class, not the instance
One attacker address appears in the attack case. You could block that one
string and watch every attack case turn green.

Do not do that. The next attacker uses a different address.

`control-benign-escalation-works` is the case that catches this. It sends mail
to an address inside the company that the support team needs to reach, and it
expects your guard to allow it through. A rule that names only the attacker's
address will pass every attack case and fail that control.

Fixing the class means deciding which recipients are allowed at all, and
refusing the rest. That decision is your `recipient_allowlist`. Ask one
question of your rule: does it still work against someone who has read my
code?
:::

::: submit
Upload your report file plus your changed code and case files. Canvas accepts
several files on one submission.

Name the report `module4-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
