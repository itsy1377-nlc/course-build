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

::: directions
**Part 1: run the attacks.**

Start the target app and leave it running:

```
python -m target.seed
python -m target.app
```

In a second terminal, run each of these three cases and watch what happens:

```
python -m harness.runner --case A1-direct-injection-system-prompt
python -m harness.runner --case A2-indirect-injection-ticket
python -m harness.runner --case A3-exfiltrate-customer-record
```

For each attack, collect three things:

1. **The result line** the harness printed, including the rate. Copy it exactly.
2. **The evidence.** Open `target/outbox/` and look at the files, or open the
   audit log at `http://127.0.0.1:8000/api/audit` in a browser. Find the thing
   that proves the attack landed. Copy the line that shows it.
3. **Your canary token**, if the attack involved one. Run
   `python -m common.canary` to see yours.

**Part 2: write one finding.**

Pick the attack you found most interesting. Write it up using the Findings
Report Template page. Fill in every heading. One page is enough.

The word cap is 500 words. There is no minimum. Short and exact beats long and
vague.

**What to hand in.** One file, either markdown or PDF, containing:

- A short table of your three attacks: case ID, result, rate.
- Your evidence for each, pasted, not described.
- Your one finding, on the template.
- The line from your config showing your target address.
:::

::: callout warning | Two ways to lose points here that have nothing to do with skill
**Reporting the model's words as evidence.** "The agent said it would email the
record" proves nothing. Find the file.

**Reporting a result without its rate.** "Vulnerable" hides "1 of 5" and
"5 of 5", and those mean different things. Always give the rate.
:::

::: grading
| Criterion | Points |
|---|---|
| Three attacks run, with the exact result line for each | 20 |
| Evidence is a side effect or a canary, pasted, not paraphrased | 20 |
| Each attack correctly labeled direct, indirect, or trusted-source | 15 |
| Finding uses every heading on the template | 15 |
| Framework identifiers correct for the attack described | 5 |
| Severity stated with a reason | 5 |
| Target address in scope | 0, and the submission is not graded without it |
| **Total** | **80** |

The finding is read by your instructor. The rest is checked against your
harness results file.
:::

::: submit
Upload one file. Markdown or PDF.

Name it `attacklab1-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
