::: intro
Your agent already judges an email and decides when a person must see it. This week it writes that judgment down for somebody else to act on, and you measure how often it's right.

The measuring surprises people.

Give this page 42 minutes, including 10 for the source at the end.
:::

::: video w7-walkthrough | What success looks like
About four minutes. One week 7 run: twenty emails, twenty notes, the score report and the exported file.
:::

::: section | Part one. Who reads a triage note
A **triage note** is the short written record an analyst leaves after judging one email. It's read later, by someone who wasn't there.

The next person to open the ticket wants the judgment and the facts behind it. Five lines are for them. The person who reported the email wants to know whether she was right, and the last line is for her.

Recording what you found and did is a step in incident handling, not a courtesy.
:::

::: section | Why the six lines never move
A fixed format buys three things. A reader knows where to look. Twenty notes in one file can be scanned. And code can write a fixed shape. `write_note()` fills the six from one result.

| Line | What it holds |
|---|---|
| Verdict | malicious or benign |
| Confidence | how sure the model is, from 0 to 1 |
| Indicators | the short facts behind the verdict |
| Recommended action | what should happen to the email next |
| Escalate | yes or no |
| Summary | two sentences for the person who reported it |

Your agent already produces four of them. The **recommended action** and the summary are new. The batch runner hands your week 6 triage a longer schema, so both arrive beside the verdict.

The action is one of five set values, and it has to fit the verdict. Your note prints it as the schema writes it.
:::

::: section | The last line is not for you
A **plain-language summary** is two short sentences for the person who reported the email, written in everyday words.

Priya Castellanos in accounts payable isn't an analyst. Write "spf softfail" and she has learned nothing. She wants to know whether anything happened to her, and what happens now.

The model writes those two sentences itself, and `write_note()` places them. A person reads them before anyone acts, because a generated summary reads as confident whether or not it's correct.
:::

::: section | One finished note
A note for email 032, whose attachment the gateway had removed.

```text
Verdict: malicious
Confidence: 0.93
Indicators: blocked attachment type; file name ends .pdf.exe; sender first seen today
Recommended action: escalate_incident
Escalate: yes
Summary: The invoice attached to this message was a program file dressed as a
PDF, and our mail gateway removed it before it reached you. Nothing ran on your
computer, and we are checking whether anyone else got a copy.
```

Every indicator on the third line names something your code pulled out. The summary names no header and no tool.

Your wording and your numbers will differ. The six lines won't.
:::

::: section | Part two. A judgment is not a measurement
Your agent has judged emails for six weeks. Nothing has said how often it was right.

A **batch run** is one sitting in which the agent reads many emails in a row. Yours reads twenty, numbered 026 to 045. Ten are malicious, ten are benign, and none appeared in an earlier week.

**Ground truth** is the correct answer for each email, written down before the agent ever ran. This course also calls it the answer key.

**Accuracy** is the share of emails the agent judged correctly. Seventeen right out of twenty is 0.85.
:::

::: section | The two errors, and what each one costs
A **false positive** is a benign email the agent called malicious. A false negative is a malicious email the agent called benign.

Devin Crowmarden is Pellgrave's whole security team.

A false positive spends his morning on a message that was fine. Enough of those and he stops believing the agent.

A false negative sends an attack back to the reporter marked safe. Priya reads that it's fine, and opens the file.

So the two counts are never added together. Three wrong out of twenty tells you nothing. Two false positives with one false negative is a different problem from one with two.
:::

::: section | One score block
Here's one score block. Yours won't match it.

```text
Scored against answer key phase0-1.0
Emails scored: 20
Correct verdicts: 17
Accuracy: 0.85
False positives: 2
False negatives: 1
Escalation agreement: 18 of 20
```

Those three counts add to twenty, which checks that the counting worked.

Escalation agreement is the share of the twenty where the agent's yes or no matched the answer key. It gets its own line because it asks a different question. Accuracy asks whether the agent judged an email correctly. This asks whether it sent the right cases to a person.

You write `score_batch()`, which counts the verdicts and the two errors. Your own numbers will differ, because the model varies from run to run. The next cell lists the emails yours got wrong.
:::

::: section | Part three. Six other jobs, and yours
A **use case** is one job people give an AI tool. Here tool means a whole AI system, not a week 4 helper. Phishing triage is one. Six more follow.

Each answers the same three questions. What facts does it need first? What does it hand back? Who checks it?
:::

::: section | Three jobs that sort what already arrived
Alert triage. The tool needs the alert, the asset it names, and what normal looks like there. It hands back an order for the queue, with a reason for each. An analyst still works the ticket.

Log review. A mail gateway writes thousands of ordinary lines a day. The tool needs those lines, and what normal looks like there. You learn normal by reading part of the log daily. It hands back the few lines worth a look.

Phishing analysis. The one you built. It needs the headers, the links and the sender history. It hands back a verdict and a note. A person still decides.
:::

::: section | Two jobs where the tool writes a draft
Documentation. Drafting a ticket note or an incident summary. It needs the facts already recorded, and nothing else. It hands back a draft in your team's shape. The ticket owner reads it first.

Scripting help. Writing a small script to pull or reshape data. It needs the shape of the data and what you want out. It hands back code. You read that code, then run it on a copy.
:::

::: section | Two jobs that help you decide what is next
Vulnerability research. Explaining what a published weakness in software means for the systems you run. It needs a list of that software, with versions. It hands back an explanation and a place in the queue. Weaknesses already used in attacks go first.

Incident response support. Drafting a timeline or a list of next steps during an incident. It needs the evidence already collected. It hands back an order of events. The responder checks each line against that evidence.

Seven jobs, and the third answer never changed. A person checks it.
:::

::: section | The sidebar, then the lab
Run the **Week 7 sidebar notebook** first. It uses a bakery yield log: four bakes, with rolls planned and rolls made. 7A counts the bakes that hit their number. 7B counts the two ways a bake missed, then divides for the rate.

Then open the lab. It runs the batch and writes `week7_triage_report.txt`. Sidebar code pasted into it fails. The name is wrong, and renaming doesn't help. The sidebar reads `planned` and `made` from one list. The lab reads a verdict from a row and checks it against the answer key.
:::

::: reading | One source to open
A free framework document from a United States standards agency, on managing the risk in an AI system. Read section 3.1, Valid and Reliable. It runs two pages.

Ask yourself one thing while you read. What does it say every accuracy measurement should be paired with?

Ten minutes. Skim it, don't study it.

[Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10)
:::

::: sources | Sources
Five of these six are United States government publications, free to read and free to reuse. The sixth is a joint agency guide marked TLP:CLEAR, so anyone may share it. Only the first is assigned, so only it carries a link.

| Source | What it grounds here |
|---|---|
| [Artificial Intelligence Risk Management Framework (AI RMF 1.0)](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10). NIST, AI 100-1, version 1.0, January 2023 | Accuracy as a measured number, the two error rates inside it, and where a person sets the threshold |
| *Incident Response Recommendations and Considerations for Cybersecurity Risk Management*. NIST, SP 800-61 Revision 3, April 2025 | Triaging a report, and recording what you found and what you did |
| *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*. NIST, AI 600-1, July 2024 | Why a written summary is checked before anyone acts on it |
| *Guide to Computer Security Log Management*. NIST, SP 800-92, September 2006 | Log review, and why knowing what normal looks like comes first |
| *Phishing Guidance: Stopping the Attack Cycle at Phase One*. CISA, NSA, FBI and MS-ISAC, October 2023 | How a real team handles the mail its own users report |
| *Known Exploited Vulnerabilities Catalog*. CISA, catalog version 2026.09.04 | Vulnerability research, and which published weaknesses come first |

Three things here come from practice, not from those documents. The six line note format is ours. So is the rule that the two error counts are never added together. And the catalog does not say you need a software list first. Every entry names a product, so you have to know what you run.
:::
