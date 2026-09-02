::: intro
Run three attacks against your own copy of HelpDesk Lite. Collect the evidence.
Write one of them up as a finding.

This is one submission with two parts and one deadline.
:::

::: scope
You may run these attacks against the HelpDesk Lite app on your own computer,
and nowhere else. Read clause 1 and clause 2 of the Rules of Engagement before
you start.

Your submission includes a copy of your `target.base_url` setting. It has to
say `http://127.0.0.1:8000`.
:::

::: video attack-lab-1-walkthrough | The three things you collect
Three minutes at the terminal, on a case you are not submitting. It shows the
three things you collect, and none of your three answers.
:::

::: directions
**Part 1: run the attacks twice.**

Start the target app and leave it running:

```
python -m target.seed
python -m target.app
```

In a second terminal, set `provider: mock` in `config/lab.config.yaml` and run
each of these three cases:

```
python -m harness.runner --case A1-direct-injection-system-prompt
python -m harness.runner --case A2-indirect-injection-ticket
python -m harness.runner --case A3-exfiltrate-customer-record
```

Then set `provider: openai_compatible` and run the same three again.

The mock falls for all three every time. Your model may not fall for all of
them. Both numbers are real results, and you report both. A run where the
attack did not land is not a wasted run, and it is not a passing grade for the
system either.

For each attack, collect three things:

1. **Both result lines**, including the rate. Copy them exactly, and label
   which provider each came from.
2. **The evidence**, from whichever run landed. Open `target/outbox/` and look
   at the files, or open the audit log at `http://127.0.0.1:8000/api/audit` in
   a browser. Find the thing that proves the attack landed. Copy the line that
   shows it.
3. **Your canary token**, if the attack involved one. Run
   `python -m common.canary` to see yours.

**Part 2: write one finding.**

Pick the attack you found most interesting. Write it up using the Findings
Report Template page. Fill in every heading. One page is enough.

The word cap is 500 words. There is no minimum. Short and exact beats long and
vague.

**Part 3: say what the difference means.**

Two or three sentences, no more. Where the two runs disagreed, say which
attacks landed on the mock and not on your model. Then answer one question: is
that system safer, or did the attack just not work this time? The Glossary
page explains what `NO_HITS_IN_5` does and does not tell you.

**What to hand in.** One file, either markdown or PDF, containing:

- A short table of your three attacks: case ID, result and rate on the mock,
  result and rate on your model.
- Your evidence for each, pasted, not described.
- Your one finding, on the template.
- Your two or three sentences on the difference.
- The line from your config showing your target address.
:::

::: callout warning | Two ways to lose points here that have nothing to do with skill
**Reporting the model's words as evidence.** "The agent said it would email the
record" proves nothing. Find the file.

**Reporting a result without its rate.** "Vulnerable" hides "1 of 5" and
"5 of 5", and those mean different things. Always give the rate.
:::

::: submit
Upload one file. Markdown or PDF.

Name it `attacklab1-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
