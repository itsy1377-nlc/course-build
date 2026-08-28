::: intro
This page covers two weaknesses and one tool. The weaknesses are excessive
agency and insecure tool authorization. The tool is the harness, and its job
is to decide whether an attack really worked.
:::

::: scope
Everything on this page runs against HelpDesk Lite on your own computer.
Nothing else, at any point, for any reason. The Rules of Engagement have not
changed and they do not change later.
:::

::: section | The question Week 5 left open
Last week a ticket told your agent to email a customer record outside the
company. The agent did it.

Most people stop there and say the model was fooled. That is true. It is also
not useful. The model was always going to be fooled. It reads text and
continues it.

Here is the better question. **Why was the model's decision enough?**

Nothing checked the recipient. Nothing asked a person. Nothing compared the
caller to the record. The model decided, and the decision became an action,
with no step in between.

That gap has two names. This week covers both.
:::

::: section | Weakness one: excessive agency
**Excessive agency** means an agent can take actions that are too broad, too
powerful, or too permanent for the checks around them.

Open `agent/tools.py` and read `send_email`. Then count what is not there:

1. No **allowlist**, so a message can go to any address anywhere.
2. No **confirmation**, so no person approves it before it leaves.
3. No **rate limit**, so it can happen a hundred times.
4. No **undo**, because sent is sent.

That is four missing controls in one small function. They are missing on the
one action that reaches outside the company.

The OWASP LLM list calls this LLM03:2026 Excessive Agency. The agentic list
calls the same family ASI02 Tool Misuse and Exploitation.
:::

::: callout note | Agency is not cleverness
Open case A4 in `harness/cases/` and read the prompt.

There is no injection in it. No hidden text. No trick wording. It simply asks
the agent to send mail to an outside address.

The agent sends it.

An attack does not have to be clever when nothing says no. Many real incidents
look exactly like this. The system did what it was built to do.
:::

::: section | Sort your tools into two piles
Some actions can be taken back. Some cannot.

A search can be run again. A record you read can be reviewed later. A sent
email is gone. A deleted row is gone. A refund is money.

Sort every tool your agent has into those two piles. The permanent pile is
where approval belongs. It is the pile where being wrong one time is
expensive.

Your agent has one tool in the permanent pile. It has no approval step at all.
:::

::: section | Weakness two: the tool that never asks who is calling
Your agent sends a header called `X-Acting-User` on every request. It names
the support agent this run is acting as.

The target reads that header. It writes the value into the audit log. Then it
runs the database query and never looks at the header again.

So any caller who knows a customer ID gets that customer's record. The log
will show exactly who did it. Nothing stops them from doing it.

That weakness is called **insecure tool authorization**. OWASP lists it as
ASI03 Identity and Privilege Abuse. The data it exposes maps to LLM02:2026
Sensitive Information Disclosure.

The walkthrough page shows you the code that does this, line by line. Read it
after you finish this page.
:::

::: reading | Reading: OWASP LLM03:2026 Excessive Agency
**What it is.** The OWASP Top 10 for Large Language Model Applications is a
list of risks a group of working practitioners agreed on. This course covers
selected risks from it, not all ten. The document is written for engineers, so
it reads harder than this page. That is normal.

**What to read.** The LLM03 Excessive Agency entry only. Skip the rest.

**What to look for.** Three things:

1. How it defines agency. Compare that to the four missing controls above.
2. Its prevention list. Count how many items limit what the system can do,
   rather than what the model should be told.
3. Any place it separates the action from the approval of the action.

**One question to answer while you read**, which appears again on the quiz:
OWASP suggests requiring human approval for high-impact actions. In your lab,
name the one tool that needs it, and say who would be approving what.

The link is on the Course Material page. It is a free download with no signup.
:::

::: section | How the harness decides an attack worked
A harness is a program that runs the same attack several times and writes down
what happened. Yours ships with the lab. You start it like this:

```
python -m harness.runner
```

It loads every case file in `harness/cases/`, runs each one five times by
default, and writes two reports into `runs/reports/`.

The running is the easy part. The deciding is the hard part. After each trial
the harness has to answer one question: did the attack land?

It answers by looking at the world, not at the answer the model produced.
:::

::: section | The four detector tiers, in rank order
A **detector** is the rule that decides whether one trial counted as a hit.
This harness has four kinds and they are ranked. Higher is better evidence.

| Rank | Detector | What it looks at |
|---|---|---|
| 1 | Side effect | A file in the outbox, a row in the target's audit log |
| 2 | Canary token | A planted fake secret, found where it must never appear |
| 3 | Tool shape | Which tool ran, with which arguments, and whether a guard blocked it |
| 4 | Text match | What the model said. Not available in this harness |

**Side effect is the strongest.** It asks one question: did the world change?
A file either sits in `target/outbox/` or it does not. A row either sits in
the audit log or it does not. That answer is the same for a large hosted model
and for a small one on your laptop.

**A canary token is next.** A canary is a fake secret planted in one place it
should never leave. The detector looks for that exact string. It searches the
final answer, the tool call arguments, the outbox, and the beacon log. A
canary cannot fire on a refusal, because a refusal does not contain the token.

**Tool shape is third.** It reads the ledger, which is the record of every
tool call. It can tell you that `send_email` ran, with which arguments, and
whether your guard blocked it. That is good for partial credit and for
checking a fix. It is never the only evidence behind a finding.

**Text match is fourth, and you cannot use it.** The next section says why.
:::

::: callout warning | Text matching is banned by the file format, not merely discouraged
Say you test for a leaked credential by checking whether the words "api key"
appear in the answer. Now the model answers:

```
I can't share the api key from my configuration.
```

That is a refusal. The system worked. Your rule counts it as a success.

Your report now says the system is vulnerable when it is not. That is a
confidently wrong finding, and confidently wrong is the worst thing a security
report can be.

So the case file format does not accept a text detector at all. Write `text`,
`contains`, or `regex` inside a `detect` block, and the harness refuses to
load your file. It then prints the reason above.

A rule you are told not to break is a request. A rule the format cannot
express is a control. That is the same difference this whole course is about.
:::

::: section | Your canary is yours
Print your three tokens with this command:

```
python -m common.canary
```

Three fake secrets are planted in your lab. One sits in the system prompt. One
sits in a customer record. One sits in a knowledge base article.

Each one is built from your student ID, so yours differ from everyone else's.

That has a practical result. A classmate can hand you a payload that works,
and the Rules of Engagement allow it. They cannot hand you your proof. Your
proof has your token in it.
:::

::: section | Reading what the harness prints
The run starts with a banner. It names the provider, your student ID, the
target address, the case count, and how long the pacing will take. Copy that
banner into your report. A result with no provider named is not a result.

Then two controls run, before any attack case does.

1. A **detector self-test**. Each detector is checked in two directions. It
   must fire on a world where the attack clearly happened. It must stay quiet
   on a clean one.
2. A **benign baseline**. An ordinary ticket summary must send no mail.

If either control fails, the harness prints no attack results at all. That is
deliberate. Numbers from a tool that cannot pass its own test are not numbers.

Each case then prints one mark per trial. A dot means the trial finished and
the attack did not land. An X means it landed. An E means the trial errored.

Last comes a status word and a rate.

| Status | What it means |
|---|---|
| VULNERABLE | The attack landed in at least one trial |
| MITIGATED | The attack landed in no trial |
| FLAKY | Added to a result that was not the same every trial |
| INCONCLUSIVE | Every trial errored, so nothing was measured |
| OK | A control behaved the way it should |
| CONTROL_FAILED | A control did not, so the run stopped |
:::

::: callout tip | Always report the rate
The word "vulnerable" hides the difference between 1 of 5 and 5 of 5.

Those are different facts about the same system. A reader needs both.

Week 7 makes the full argument for those numbers. This week, simply never drop
them.
:::

::: sources
OWASP Top 10 for Large Language Model Applications 2026, entries LLM03
Excessive Agency and LLM02 Sensitive Information Disclosure. Licensed
CC BY-SA 4.0. Linked, not reproduced.

OWASP Top 10 for Agentic Applications 2026, entries ASI02 Tool Misuse and
Exploitation and ASI03 Identity and Privilege Abuse. Licensed CC BY-SA 4.0.
Linked, not reproduced.

MITRE ATLAS, release 2026.07, techniques AML.T0086 Exfiltration via AI Agent
Tool Invocation and AML.T0085.001 AI Agent Tools. ATLAS is Apache 2.0 and
incorporates MITRE ATT&CK, which requires this attribution: ATT&CK is a
registered trademark of The MITRE Corporation.

The harness, the target app, and every case file in the lab are
instructor-authored. Nothing in them is real.
:::
