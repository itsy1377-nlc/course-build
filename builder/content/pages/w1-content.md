::: intro
Two things this week. First, what a security operations center actually is, so you know where a reported email lands. Second, the three kinds of AI you'll meet in IT work, so you know which one you're building.

Every example comes from Pellgrave Mechanical Group, a heating, cooling and plumbing contractor with about 640 staff. Pellgrave isn't real. It's invented for this course.

Give this page 40 minutes.
:::

::: video w1-walkthrough | What a finished week 1 run looks like
A full pass through the lab, first cell to exported file.
:::

::: section | Part one. What a security operations center is
A security operations center is the team that watches for attacks and handles what people report. Everyone calls it a SOC.

Pictures of a SOC always show a room full of screens. Pellgrave has one security analyst, Devin Crowmarden, and his desk is the whole SOC.

The parts below are the same either way. A large team splits them across people, and a small one doesn't.
:::

::: section | The things you protect
Security work starts with knowing what you've. Four words cover most of it.

| Term | What it means | At Pellgrave |
|---|---|---|
| Asset | Anything the company owns and has to protect | The payroll system, a van tablet, the customer list |
| User | A person with an account at the company | Priya Castellanos, in accounts payable |
| Network | The equipment that connects the company computers to each other and to the internet | The office wireless, and the links to two branch offices |
| Endpoint | A computer, laptop or phone that a person works on | The laptop Priya reads her mail on |

Priya's laptop is an asset and an endpoint at the same time, which isn't a contradiction. The two words answer different questions.

Asset answers who owns it and how much it matters. Endpoint answers whether a person is typing on it. You'll need both answers to judge a single report.

Users matter most here. Almost every message you triage arrives because somebody reported it.
:::

::: section | The things that tell you something happened
Two words say that something happened, and the gap between them is most of the job.

A **log** is a record that something happened. The Pellgrave mail gateway writes a log line for every message it scans. That's thousands of lines a day, nearly all of them ordinary.

An **alert** is a record that something looked worth a person's time. Something decided that. It may be a rule in the gateway. It may be a user clicking the Report Phish button.

An alert is just a log line that someone raised a hand about. A team that treats every log line as an alert drowns in them. A team that raises none sees nothing.
:::

::: section | The things you do about it
So now you've an alert. Four more words cover what happens next.

| Term | What it means |
|---|---|
| Ticket | The record a team opens to track one piece of work to its close |
| Incident | A confirmed event that caused harm, or could have |
| Escalation | Handing a case to a person instead of closing it yourself |
| Documentation | What you write down so the next person can act without asking you |

Every alert Pellgrave keeps gets a ticket, holding who reported it, what was decided, and what was done.

Most tickets close as ordinary and a few become incidents. A password typed into a fake login page is an incident. That same fake page, clicked by nobody, isn't.

Escalation is what you do when a case sits above your line. At Pellgrave an escalated ticket goes to Devin Crowmarden, the security analyst. He is the only one, so nothing waits in a queue behind him.

Documentation is the part everybody skips. A ticket that says "phishing, closed" tells the next reader nothing. Name the sender, the link, the check that failed and what you did.
:::

::: section | The picture, and where your agent sits
Put those words in order and you get the path one reported email takes.

| Stop | What happens | Who does it |
|---|---|---|
| 1. A reported email | A user gets a strange message and clicks Report Phish | The user |
| 2. An alert | The report lands in the phishing mailbox and is raised for review | The gateway and the report button |
| 3. A ticket | Someone opens a record and judges the message | The analyst, helped by your agent |
| 4a. A closed ticket | Nothing harmful happened, and the reporter gets an answer | The analyst |
| 4b. An incident | Harm happened, or nearly did, so the case is escalated | The analyst |

Your agent sits between stop 2 and stop 3. An agent is a program that sends text to a model, reads the answer, and acts on it.

It reads the facts behind an alert and drafts the note that goes into the ticket. That's all it does.

It doesn't close a ticket, and it doesn't decide that something is an incident. A person does both, every time. Weeks 6 and 7 come back to this.
:::

::: section | Part two. Three kinds of AI
People use the word AI for three quite different things. They behave differently, cost differently, and fail differently.

| Kind | What it does | What it hands back |
|---|---|---|
| Scoring AI | Sorts or rates something | A number or a label |
| Generative AI | Writes new text or code | New text |
| Agentic workflow | Picks its own next step and then acts, inside set limits | A decision and an action |

You're building the third kind, and you start this week with a plain call to the second.
:::

::: section | Scoring AI at work
Scoring AI reads something and puts a number or a label on it. It writes nothing new at all.

The Pellgrave help desk rates every new ticket for urgency. A high score moves the ticket up the queue. A low score leaves it where it's. The score is a number, not a sentence.

The tool on Priya's laptop scores a new file as risky or ordinary before she opens it.

Both run fast, and both run on everything. Reach for scoring when you've far more items than people.
:::

::: section | Generative AI at work
Generative AI writes new text. It doesn't sort what's already there.

A Pellgrave technician asks it to draft a change request for a new firewall rule. A firewall rule decides which traffic may cross the network. The draft comes back in the right shape, and a person edits it before filing it.

Yolanda pastes an unfamiliar log line into it and asks what the line means. She gets a plain sentence back.

Both answers are useful, and neither is proof. Generative AI writes what reads well, and it doesn't check itself.
:::

::: section | Agentic workflows at work
An agentic workflow picks its own next step and then takes it, inside limits somebody set.

Pellgrave runs one on password resets. It reads the ticket, checks the account, and checks whether the device belongs to that user. If all three agree, it resets the password and closes the ticket. If any one doesn't, it stops and asks a person.

A second one checks patches. It reads the equipment list, checks each version, and opens a ticket for every machine that's behind.

Neither one is magic. Each is a short run of checks with a hard stop at the end.
:::

::: section | What stays human
All three kinds hand their output to a person. The urgency score reorders a queue, and a person still works the ticket. A person files the drafted change request. The password workflow stops and asks whenever a check fails.

That stop is escalation, the word from part one. Every tool in this course has one.
:::

::: section | Practice before the lab
Two short sidebars sit in the week 1 sidebar notebook. Sidebar 1A calls a function and keeps what it hands back, and sidebar 1B builds a sentence from values with an f-string.

Both use a grocery stockroom rather than email. They take about 25 minutes together. Work them before you open the lab.
:::

::: reading | One source to open
This is a free framework document from a United States standards agency. Read section 2, the introduction to the Core. It runs about two pages and names six Functions: Govern, Identify, Protect, Detect, Respond and Recover.

Ask yourself one thing while you read: which Function covers finding and analyzing a possible attack?

Ten minutes, and you're skimming this, not studying it.

[The NIST Cybersecurity Framework (CSF) 2.0](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final)
:::

::: sources | Sources
All four are United States government publications, free to read and free to reuse. Only the first is assigned, so only it carries a link.

| Source | What it grounds here |
|---|---|
| [The NIST Cybersecurity Framework (CSF) 2.0](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final). NIST, CSWP 29, February 2024 | Assets, detection, and why a list of what you own comes first |
| *Incident Response Recommendations and Considerations for Cybersecurity Risk Management*. NIST, SP 800-61 Revision 3, April 2025 | The gap between an event and an incident, and response as defined steps |
| *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST, AI 100-1, January 2023 | What counts as an AI system, and where human oversight belongs |
| *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*. NIST, AI 600-1, July 2024 | What generative AI is, and how it differs from a scoring model |

Two words on this page come from practice, not from those documents. **Ticket** and **escalation** are how teams work. Neither is a defined term in the NIST publications above. Every other claim here traces to one of the four.
:::
