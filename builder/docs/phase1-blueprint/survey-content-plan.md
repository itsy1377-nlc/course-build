# Survey content plan: breadth topics B1 to B4

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 2.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.

| Field | Value |
|---|---|
| Topics covered | B1, B2, B3, B4 |
| Weeks that carry them | 1, 6, 7 |
| Course objectives created | None. These are not objectives |
| Canvas Outcomes created | None |
| Labs created | None |
| Added student time | None. Survey reading replaces reading, it does not add reading |

A note on terms used below. *Survey content* is reading that widens what a student
knows without asking them to build anything. A *breadth topic* is a required subject
this course carries by reading, discussion and quiz rather than by lab work. A
*self-check* is a low stakes quiz a student may retake.

Three more terms appear later. *Prompt injection* is attacker text that a model reads
as an instruction. A *false positive* is a safe message the agent calls malicious. A
*false negative* is a malicious message it calls safe.

---

## 1. What survey content is, and what it is not

The course build goes deep on one narrow thing: a phishing triage agent. Four
subjects the program needs are wider than that agent. They are carried by reading,
discussion, self-checks and the final exam.

They get no course learning objective number. They get no Canvas Outcome. They get no
lab. The build arc is not widened to reach any of them.

| Topic | Subject | Where the reading sits | Also assessed by |
|---|---|---|---|
| B1 | AI and agentic workflows in IT and security operations broadly | Week 1 reading, part two | Week 1 discussion, week 1 self-check, final exam |
| B2 | The range of AI-assisted security use cases | Week 7 reading, part three | Week 7 discussion, week 7 self-check, final exam |
| B3 | Security operations components | Week 1 reading, part one | Week 1 self-check, week 1 discussion, final exam |
| B4 | The wider AI risk set | Week 6 reading, page two | Week 6 self-check, week 6 discussion in part, final exam |

Two placement choices are worth stating plainly.

B1 and B3 sit in week 1 because a student cannot judge a phishing agent without
knowing what a security team is and what AI already does in one. B3 also does a
second job. The prerequisite course is a non-technical AI literacy course, so no
earlier course in the chain explains what a security operations center holds. Week 1
supplies that orientation.

B2 sits in week 7 for the opposite reason. A student can only generalize from
something they have already built. In week 7 they have a working agent and their own
accuracy numbers, so the question "where else does this go" has an anchor.

---

## 2. How reading time is priced

The weekly reading budget is 40 to 50 minutes. Survey content lives inside that
budget. It never adds to it.

**This section holds the one reading rate the whole course uses.** Every one of the
seven weekly specs prices its reading from the rule below, and none of them names a
different rate.

Two numbers are reported for every reading below, because they answer two different
questions.

**One pass at 200 words a minute.** This is a normal adult silent reading rate for
plain prose. It answers "how long does it take to read the words once." Every week
uses this rate and no other.

**The minutes priced in the week.** This is what the week's time table actually
charges the student. It is higher, and the difference is study time rather than
reading time. These pages carry first-time definitions, a labeled diagram and worked
examples, and students go back over those.

So the priced minutes are a study pace, not a reading pace. Each week spec shows its
own split: one pass at 200 words a minute, then one named line for each thing the page
asks beyond reading the words. The two parts add to the priced total.

Both numbers appear in every section. The gap between them is visible on purpose. The
build prompt asks for the weekly time budget to be checked against the real week 1 and
week 2 builds, and that check is what should test the study pace. The rate for one
pass is not what that check is testing.

| Week | Reading priced | Budget | Total words | Survey words | Survey share of priced minutes |
|---|---|---|---|---|---|
| 1 | 40 minutes | 40 to 50 | 1,350 | 1,350 | 40 of 40 |
| 6 | 45 minutes | 40 to 50 | 2,300 | 1,150 | 22 of 45 |
| 7 | 42 minutes | 40 to 50 | 1,250 | 390 | 10 of 42 |

The replacement rule in one sentence. In week 6, the injection page runs to 1,150
words rather than 2,300 because B4 takes the other half of the same 45 minutes.

---

## 3. B1, AI and agentic workflows in IT and security operations

**Where it lives:** week 1 reading, part two. **Also:** the week 1 discussion, part 2.

B1 covers AI across IT and security work, not only phishing. The reading separates
three things students otherwise blur together, then shows each one at work outside
email.

### 3.1 What the reading covers, section by section

| # | Section | Words | What it does |
|---|---|---|---|
| 1 | Three kinds of AI, and why the difference matters | 120 | One plain sentence for each kind. Scoring AI sorts or rates something. Generative AI writes new text or code. An agentic workflow picks its own next step and then acts |
| 2 | Scoring AI at work | 130 | Two examples outside phishing. A mail gateway rating every message. An endpoint tool scoring a file as risky. What it hands back is a number or a label |
| 3 | Generative AI at work | 130 | Two examples outside phishing. Drafting a change request for a firewall rule. Explaining an unfamiliar log line in plain words. What it hands back is new text |
| 4 | Agentic workflows at work | 130 | Two examples outside phishing. A password reset flow that checks the ticket, the account and the device before acting. A patch check that reads an inventory, looks up a version, and opens a ticket. What it hands back is a decision plus an action, inside limits |
| 5 | What stays human | 60 | All three hand their output to a person. Names the escalation point that part one defined, so B1 and B3 close together |
| | **Total** | **570** | |

Every example is set at Pellgrave Mechanical Group, the fictional company the corpus
supplies. No real company, product or brand is named.

Section 4 is the one that earns its place. The course claims that an agent is a loop
around a model call, not magic. A student who has seen a password reset flow described
as a loop of checks reads week 5 differently.

### 3.2 Word count and reading time

| Measure | Value |
|---|---|
| Words | 570 |
| One pass at 200 words a minute | 2.9 minutes |
| Priced in the week 1 time table | 10 minutes |

### 3.3 How it fits the week 1 reading budget

Week 1 has no separate technical reading page. The week's technical material, the
model call and temperature and token counts, is carried by the two short videos and by
the notebook's own markdown cells. Those are priced in the video band and the lab
band, not in the reading band.

So the whole reading band in week 1 is survey content, and it is shared by B1 and B3.

| Part of the week 1 reading | Words | Minutes priced |
|---|---|---|
| Part one, B3, the parts of a security operations center | 780 | 20 |
| Part two, B1, AI in IT and security operations | 570 | 10 |
| Opening and skimming one of the four cited sources | | 10 |
| **Total** | **1,350** | **40** |

The arithmetic: 780 plus 570 is 1,350 words. Twenty plus 10 plus 10 is 40 minutes.
Forty minutes is the floor of the 40 to 50 minute budget, not the ceiling. At 200
words a minute the whole page reads once in 6.8 minutes, so the survey content is
nowhere near what would push this week over its budget.

### 3.4 Sources it will cite

Week 1 cites four sources for both B1 and B3 together. B1 draws on these two.

| Source | Publisher and identifier | What it grounds |
|---|---|---|
| Artificial Intelligence Risk Management Framework 1.0 | NIST, report AI 100-1, January 2023, on nist.gov and the AI Resource Center | What counts as an AI system, and the place of human oversight |
| Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | NIST, report AI 600-1, July 2024, on nist.gov | What generative AI is, and how it differs from a scoring model |

A fifth source was considered and cut to hold the count at four: the MITRE ATT&CK
entry for phishing, technique T1566. It is available if the program manager wants it
added.

Every citation is checked before publication. The check has four parts: the document
is fetched, the link is confirmed to resolve, the licence is confirmed to permit use,
and an expert subagent review confirms the claim the citation is attached to. Any
claim the review cannot ground is removed or flagged, never quietly kept.

### 3.5 How the self-check and the final exam assess it

**Week 1 self-check.** Two of its six multiple choice items sit on B1. Each describes
a tool in plain words and asks which of the three kinds it is. Unlimited attempts,
highest score kept.

**Final exam.** B1 items ask a student to place a described workflow in one of the
three kinds, or to say what changes when a workflow becomes agentic. Section 10 gives
the item share. A sample stem:

> The Pellgrave help desk runs a tool on new password tickets. It reads the ticket,
> checks the user's device record, resets the password, and closes the ticket. Which
> kind of AI work is this?
>
> - A. scoring AI
> - B. generative AI
> - C. an agentic workflow
> - D. none of these

---

## 4. B2, the range of AI-assisted security use cases

**Where it lives:** week 7 reading, part three. **Also:** the week 7 discussion.

B2 is the answer to "what else is this good for," asked at the only point in the
course where a student has their own results to answer it with.

### 4.1 What the reading covers, section by section

Part three of the week 7 reading walks seven use cases. A *use case* is one job people
give an AI tool. Each gets one short paragraph and answers the same three questions:
what facts does the tool need first, what does it hand back, and who checks it.

| # | Section | Words | What it does |
|---|---|---|---|
| 1 | What a use case is, and the three questions | 40 | Sets the pattern the seven paragraphs follow |
| 2 | Alert triage | 50 | Sorting a queue of alerts by what deserves a person first. Needs the alert, the asset it names, and what normal looks like |
| 3 | Log review | 50 | Reading a large log for the lines that matter. Needs the log lines and a baseline |
| 4 | Phishing analysis | 50 | The one students built. Placed here so they see their own work as one of seven, not as the whole field |
| 5 | Documentation | 50 | Drafting a ticket note or an incident summary. Needs the facts already recorded, never new ones |
| 6 | Scripting help | 50 | Writing a small script to pull or reshape data. Needs the data shape and a person who reads the script before running it |
| 7 | Vulnerability research | 50 | Explaining what a published weakness means for one specific system. Needs the software inventory and versions |
| 8 | Incident response support | 50 | Drafting a timeline or a next-step list during an incident. Needs the evidence already collected |
| | **Total** | **390** | |

Section 4 is deliberate. Students who have spent seven weeks on phishing can leave
believing phishing triage is what AI in security means. One paragraph of the same
shape as the other six fixes that.

Each paragraph names what would have to change in the agent students built. That is
what the discussion then asks them to do for one use case of their own choosing.

### 4.2 Word count and reading time

| Measure | Value |
|---|---|
| Words | 390 |
| One pass at 200 words a minute | 2.0 minutes |
| Priced in the week 7 time table | 10 minutes |

### 4.3 How it fits the week 7 reading budget

Week 7 has real technical reading. Parts one and two teach the triage note format and
how to measure the agent, and both carry a worked example that students read line by
line. B2 is part three and carries no worked example, so it is priced lower.

| Part of the week 7 reading | Words | Minutes priced |
|---|---|---|
| 1. The note, with one worked triage note | 480 | 17 |
| 2. Measuring, with one worked score block | 380 | 15 |
| 3. Where else this goes, B2 | 390 | 10 |
| **Total** | **1,250** | **42** |

The arithmetic: 480 plus 380 plus 390 is 1,250 words, inside the 1,400 word ceiling
the writing standard sets for a weekly reading. Seventeen plus 15 plus 10 is 42
minutes, inside the 40 to 50 minute budget with 8 minutes of headroom. At 200 words a
minute the whole page reads once in 6.3 minutes.

B2 takes 10 of the 42 minutes. Without it, parts one and two would be written longer
to fill the same band. That is what "replaces reading time" means here.

### 4.4 Sources it will cite

Week 7 cites four to six sources across all three parts. These six are the candidates,
and the last three carry B2.

| Source | Publisher and identifier | What it grounds |
|---|---|---|
| Incident Response Recommendations and Considerations for Cybersecurity Risk Management | NIST, Special Publication 800-61 Revision 3, April 2025, on csrc.nist.gov | Documentation and incident response support as real job steps |
| Artificial Intelligence Risk Management Framework 1.0 | NIST, report AI 100-1, January 2023, on nist.gov | Measurement and the human oversight point |
| Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | NIST, report AI 600-1, July 2024, on nist.gov | What a generative tool can and cannot be trusted to produce |
| Guide to Computer Security Log Management | NIST, Special Publication 800-92, on csrc.nist.gov | The log review use case, and why a baseline comes first |
| Known Exploited Vulnerabilities Catalog | CISA, on cisa.gov | The vulnerability research use case, and why an inventory comes first |
| Phishing Guidance: Stopping the Attack Cycle at Phase One | CISA with the NSA and the MS-ISAC, October 2023, on cisa.gov | How reported phishing is handled by a real team |

The revision in force is pinned at fetch time. NIST revises these documents, so the
writer records the revision number and the retrieval date rather than trusting the
number printed here. Every citation goes through the same four-part check described in
section 3.4.

### 4.5 How the self-check and the final exam assess it

**Week 7 self-check.** Four of its eight items sit on B2. Each gives a short
description of a security job, and asks which use case it is and one fact the tool
would need first. Two attempts, highest score kept.

**Week 7 discussion.** Question 2 asks each student to pick one use case other than
phishing. Question 3 asks what they would change in the agent they built. Section 8
gives the prompt in full.

**Final exam.** B2 items give a described job and ask which use case it is, or ask
which fact the tool needs before it can judge anything. A sample stem:

> Devin wants an AI tool to help with log review instead of phishing. Which fact does
> the tool need before it can judge anything?
>
> - A. the raw log lines and what normal looks like for that host
> - B. the model temperature
> - C. the token count
> - D. the sender's display name

---

## 5. B3, security operations components

**Where it lives:** week 1 reading, part one. **Also:** the week 1 self-check.

B3 does two jobs at once. It is a required breadth topic, and it is the security
operations orientation that no earlier course in the chain supplies.

### 5.1 What the reading covers, section by section

| # | Section | Words | What it does |
|---|---|---|---|
| 1 | What a security operations center is | 70 | A plain definition. Says that at a company the size of Pellgrave it is one analyst, not a room of them |
| 2 | The things you protect: assets, users, networks, endpoints | 200 | One plain definition each, one Pellgrave example each. A laptop is an asset and an endpoint at the same time, and the reading says why that is not a contradiction |
| 3 | The things that tell you something happened: logs, alerts | 140 | A log is a record that something occurred. An alert is a record that something decided was worth a person's time. The difference is the whole job |
| 4 | The things you do about it: tickets, incidents, escalation, documentation | 230 | One plain definition each. Names who receives an escalated ticket at Pellgrave, and what documentation has to contain for the next person to act on it |
| 5 | The picture, and where your agent sits | 140 | A labeled diagram. A reported email becomes an alert, then a ticket, then either a closed ticket or an incident. A pin on that diagram marks where this course's agent sits |
| | **Total** | **780** | |

Section 5 is the section the rest of the course leans on. The pin sits between the
alert and the ticket. The agent reads the facts behind an alert and drafts the note
that goes into a ticket. It does not close anything, and it does not decide that
something is an incident.

A student who holds that picture reads two later weeks differently. The week 6
escalation threshold and the week 7 human review question become the same question,
asked twice.

The diagram ships with alt text that describes the same path in words, so the meaning
does not depend on seeing the image. That is a Web Content Accessibility Guidelines
2.2 AA requirement and it is checked before publication.

### 5.2 Word count and reading time

| Measure | Value |
|---|---|
| Words | 780 |
| One pass at 200 words a minute | 3.9 minutes |
| Priced in the week 1 time table | 20 minutes |

Ten definitions and a diagram are the slowest 780 words in the course, which is why
this part is priced at more than half of the week 1 reading band.

### 5.3 How it fits the week 1 reading budget

The week 1 table in section 3.3 covers both topics and is not repeated here. The
arithmetic for B3: 780 words of the 1,350 on the page, and 20 minutes of the 40
priced. At 200 words a minute part one reads once in 3.9 minutes.

Week 1 is also the week the build prompt names for checking the time budget against a
real build. This figure should be measured again after Phase 2 rather than trusted.

### 5.4 Sources it will cite

B3 draws on the other two of week 1's four sources.

| Source | Publisher and identifier | What it grounds |
|---|---|---|
| The NIST Cybersecurity Framework 2.0 | NIST, Cybersecurity White Paper 29, February 2024, on nist.gov and csrc.nist.gov | Assets, the identify and detect functions, and why an inventory comes before anything else |
| Incident Response Recommendations and Considerations for Cybersecurity Risk Management | NIST, Special Publication 800-61 Revision 3, April 2025, on csrc.nist.gov | The difference between an event, an alert and an incident. Escalation and documentation as defined steps |

The same four-part check in section 3.4 applies. One item needs the reviewer's
attention: the terms *ticket* and *escalation* are operational rather than defined in
either document. The reading will attribute the incident handling steps to Special
Publication 800-61 Revision 3 and will describe ticket handling as common practice
rather than as a cited requirement. That is the honest read and the reviewer is asked
to confirm it.

### 5.5 How the self-check and the final exam assess it

**Week 1 self-check.** Three of its six items sit on B3. One gives a line and asks
which part it belongs to. One asks where this course's agent sits in the picture. One
asks who receives an escalated ticket.

**Week 1 discussion.** Part 2 asks each student to name one part of a security
operations center that their own example touched, chosen from the ten the reading
defined.

**Final exam.** B3 items give a short scene from the corpus and ask which component it
names, or where the agent sits relative to it. A sample stem:

> The mail gateway writes a record for every message it scans. One record is marked
> for a person to look at. What is that marked record called?
>
> - A. an asset
> - B. a log
> - C. an alert
> - D. an incident

---

## 6. B4, the wider AI risk set

**Where it lives:** week 6 reading, page two. **Also:** the week 6 self-check, and one
question of the week 6 discussion.

Week 6 is the week students attack their own agent. The lab work is prompt injection.
B4 is the rest of the risk set, and every risk on the page lands on a case the student
just ran.

### 6.1 What the reading covers, section by section

| # | Section | Words | What it does |
|---|---|---|---|
| 1 | Five risks that are not injection | 100 | Says plainly that injection is one risk among several, and that the other five need different controls |
| 2 | Hallucination | 210 | A model stating something that is not in the facts it was given. The case: an indicator naming a host the extractor never found. The control: validate every output field against the extracted facts |
| 3 | Data exposure | 210 | Putting information somewhere it should not go. The case: email 023, whose forged header asks the agent to paste the recipient's report history into a summary written for the reporter. The control: an output validator that rejects any field the note format does not define |
| 4 | Privacy | 200 | The same case one step wider. What you put in a prompt is what you expose. Repeats the week 3 rule: send the minimum a sound judgment needs, and no more |
| 5 | Automation bias | 200 | Trusting a tool because it is a tool. The case: email 015, the benign message a keyword rule escalates. A person who trusts the tool stops looking at the message |
| 6 | Overreliance | 180 | Letting the tool decide what a person should decide. The case: the confidence floor, and the honest reason it exists |
| 7 | What to do about all five | 50 | A short list pointing at the four controls the lab already built, so the page ends in the student's own notebook |
| | **Total** | **1,150** | |

Two things about this page are worth the program manager's attention.

First, it is not an abstract risk list. Each of the five names an email or a setting
from the lab the student finished that same week. Automation bias is not a concept
here, it is email 015 escalating when it should not.

Second, it teaches the difference between the risk and the control. Hallucination is
caught by validating output against facts. Data exposure is caught by an output
validator. Automation bias and overreliance are not caught by code at all, which the
page says out loud.

### 6.2 Word count and reading time

| Measure | Value |
|---|---|
| Words | 1,150 |
| One pass at 200 words a minute | 5.8 minutes |
| Priced in the week 6 time table | 22 minutes |

### 6.3 How it fits the week 6 reading budget

Week 6 carries two reading pages of equal length. Page one is technical and belongs to
the lab. Page two is B4.

| Page of the week 6 reading | Words | Minutes priced |
|---|---|---|
| 1. Prompt injection in a triage agent | 1,150 | 23 |
| 2. The wider AI risk set, B4 | 1,150 | 22 |
| **Total** | **2,300** | **45** |

The arithmetic: 1,150 plus 1,150 is 2,300 words. Twenty three plus 22 is 45 minutes,
inside the 40 to 50 minute budget with 5 minutes of headroom. At 200 words a minute
both pages read once in 11.5 minutes.

This is the clearest case of the replacement rule in the course. Week 6 spends 45
minutes on reading either way. B4 takes half of that, so the injection page is written
to 1,150 words instead of 2,300. Nothing was added to the week.

Week 6 also carries the strongest lab in the course, so it has the least slack. If the
real build shows this week over 6 hours, the build prompt says to cut reading first.
The order of cuts on this page is stated here so it is not decided under pressure: cut
section 4 into section 3, then shorten sections 5 and 6. Do not cut a risk entirely.

### 6.4 Sources it will cite

| Source | Publisher and identifier | What it grounds |
|---|---|---|
| Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations | NIST, report AI 100-2, on csrc.nist.gov | Injection and data extraction as named attack classes, with the edition pinned at fetch |
| Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile | NIST, report AI 600-1, July 2024, on nist.gov | Hallucination, data privacy, and the human configuration risks behind automation bias |
| Artificial Intelligence Risk Management Framework 1.0 | NIST, report AI 100-1, January 2023, on nist.gov | Human oversight, and what a trustworthy system is asked to show |
| The OWASP Top 10 for Large Language Model Applications | The OWASP Foundation, on owasp.org | The entries titled Prompt Injection, Sensitive Information Disclosure, Excessive Agency and Misinformation |
| ATLAS | MITRE, on atlas.mitre.org | The named techniques for prompt injection against a language model and for data leakage through one |
| Joint guidance on securing data used in AI systems | CISA with the NSA and international partners, on cisa.gov | Data exposure as an operational risk, not only a model property |

Two verification notes for the writer. The OWASP list is versioned by year and its
numbering changes between versions, so the reading quotes the entry titles and pins
the version in force at publication. The MITRE technique identifiers are confirmed
against the live site at fetch time rather than written from memory. Every citation
goes through the same four-part check described in section 3.4.

### 6.5 How the self-check and the final exam assess it

**Week 6 self-check.** One of its six items sits on B4. It asks which wider risk the
forged header case in email 023 shows.

**Week 6 discussion.** The discussion is a course objective 4 activity and belongs to
the injection work. One of its three questions also lands on B4. It asks the student
to write the extra guardrail rule their own run needed, then to price that rule
against email 015, the benign decoy, using a number from their own file. That is the
overreliance and automation bias question in operational form.

**A gap this plan reports rather than hides.** B4 has the thinnest assessment of the
four topics outside the exam: one self-check item and part of one discussion question.
The other three each carry two or more graded touches. Two options are offered and
neither is taken without approval. Raise the week 6 self-check from six items to
eight, adding one item on hallucination and one on automation bias. Or leave it at six
and accept that the exam carries most of B4. The second option is defensible, because
B4 is the topic selected response suits best, and because the exam blueprint now gives
B4 the largest share of the breadth half for this reason.

**Final exam.** B4 items give an agent output or a setting and ask which risk it
shows. A sample stem:

> Your triage note lists an indicator that names a host your extractor never found in
> the email. Which risk does this show?
>
> - A. hallucination
> - B. data exposure
> - C. automation bias
> - D. overreliance

---

## 7. The week 1 discussion prompt

Graded. One post and one substantive reply. Estimated student time 20 minutes,
inside the 15 to 20 minute band the build prompt sets. The estimate appears in the
week 1 Tasks table on the module overview page, which is where the institutional
template puts activity times.

The prompt carries B1 and B3. Part 1 requires the student's own exported file, so a
general opinion cannot answer it. Two students will not have the same six answers,
because the model is not deterministic.

**Reply requirement:** one reply, to a classmate who named a different kind of AI than
the poster did, in two or three sentences, pointing to a line in that classmate's
post. A reply that only agrees does not count.

Written out below exactly as students will see it.

> **Where you have already met AI at work**
>
> Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central.
>
> Write about 150 words in your post. Write about 60 words in your reply.
>
> **Part 1. Your own results.**
>
> Open your file `week1_first_calls.txt`. Find the six answers your notebook gave to
> the same email. Quote one short line from one answer. Say which temperature produced
> it. Then name one thing that answer got right. Name one thing it got wrong or left
> out. Use your own file. Do not use a classmate's.
>
> **Part 2. Where you have met this before.**
>
> Name one place you have already met AI in IT work or security work. It can be from a
> job, from school, from home, or from the news. Then say which of these three kinds it
> was.
>
> - Scoring AI, which sorts or rates something. A spam filter is one.
> - Generative AI, which writes new text or code. A chat assistant is one.
> - An agentic workflow, where a tool picks its own next step and then acts.
>
> Then name one part of a security operations center that your example touched. Pick
> from this week's reading: assets, users, networks, endpoints, logs, alerts, tickets,
> incidents, escalation, or documentation.
>
> **Your reply.**
>
> Reply to one classmate who named a different kind than you did. In two or three
> sentences, say what would change in their example if the tool were agentic. Point to
> a line in their post. A reply that only agrees does not count.
>
> You may use AI help on this post. If you do, add one line saying what you asked it.

Why this cannot be answered from opinion. Part 1 needs a file the student's own
notebook wrote, a line quoted from it, and the temperature that produced it. Part 2
needs a real place the student has been. The reply needs a specific classmate's post
and a specific line in it.

One facilitation note for the instructor guide. Students will name spam filters far
more than anything else. The instructor's own reply should name an agentic example
from IT work, so the third kind does not stay abstract.

---

## 8. The week 7 discussion prompt

Graded. One post and one substantive reply. Estimated student time 18 minutes, inside
the 15 to 20 minute band. The estimate appears in the week 7 Tasks table.

The prompt carries B2. It requires three numbers from the student's own batch run, so
it cannot be answered from opinion or from a classmate's post.

**Reply requirement:** one reply, to a classmate who chose a different use case, naming
one thing that classmate's change would break or fix in the replier's own agent, and
citing one number from the replier's own report. A reply that only agrees does not
count.

Written out below exactly as students will see it.

> **Your numbers, and one other job for an agent**
>
> A use case is one job people give an AI tool.
>
> Open your week 7 report. Find three numbers: your accuracy, your false positive
> count, and your false negative count.
>
> Post by Thursday. Do three things.
>
> 1. Give your three numbers. Name one email your agent got wrong. Say which error it
>    was.
> 2. Pick one use case from this week's reading. Do not pick phishing. Your choices are
>    alert triage, log review, documentation, scripting help, vulnerability research, or
>    incident response support.
> 3. Name one part of your agent you would have to change for that use case. Say what
>    the change is. Say why it is needed.
>
> Then reply to one classmate by Sunday at 11:59 PM Central. Pick someone who chose a
> different use case. Say one thing their change would break or fix in your own agent.
> Use one number from your own report. A reply that only agrees does not count.
>
> Keep your post near 150 words. Keep your reply near 60 words.
>
> You may use AI help on this post. If you do, add one line saying what you asked it.

Why this cannot be answered from opinion. The three numbers come from a batch the
student ran themselves, and no two students will have the same three. The wrong email
has to be one their own run got wrong. Question 3 requires them to name a real part of
the agent they built.

One facilitation note for the instructor guide. A student who picks documentation or
scripting help will often say nothing would change. That is the teachable moment. The
facts the tool needs first change completely, which is the point of every use case
paragraph in the reading.

---

## 9. Reading level

Every student-facing block in this document was measured with the course readability
tool. The tool excludes code, tables, file paths and headings, and measures what is
left.

| Block | Grade | Average sentence | Longest sentence | Limit |
|---|---|---|---|---|
| Week 1 discussion prompt, section 7 | 3.09 | 8.8 words | 17 words | grade 7, average 12 |
| Week 7 discussion prompt, section 8 | 3.03 | 8.3 words | 20 words | grade 7, average 12 |
| The four sample exam stems, sections 3.5, 4.5, 5.5 and 6.5 | 3.89 | 7.7 words | 19 words | grade 7, average 12 |
| This document as a whole | 6.30 | 14.0 words | 37 words | grade 9.5, average 18 |

**How each block was measured.** The two discussion prompts are the blockquoted text
in sections 7 and 8. The stem row is the four blockquoted sample stems, taken together,
with the leading `>` removed from each line so the tool reads them as prose rather than
skipping them as a quotation. Each stem on its own is under the tool's 40 word floor or
close to it, so the four are scored as one block. Scored one at a time the two that
clear the floor read 3.06 and 2.53.

**One earlier number corrected.** An earlier draft of this table reported the stem row
at grade 4.97 with an average sentence of 9.4 words. That draft wrote every option list
as one inline sentence beginning "Options:", which pushed the B2 stem to an average of
15.7 words, over the 12 word limit for a student-facing stem. All four stems now write
one option per list line, which is the form the week 8 exam blueprint already uses. The
row above is what the tool returns on the rewritten stems.

Both discussion prompts pass at grade 7 or below with room to spare. Both hold an
average sentence under 12 words. This document is a program manager document, so it is
held to grade 9.5, and it passes with no paragraph over 70 words.

The readings themselves are measured when they are written, not now. Each one is held
to the same 7th grade standard, and each measured score is reported per page in the
final quality report.

---

## 10. What the final exam carries

The final exam is multiple choice and its primary job is these four topics. Roughly
half its items sit on B1 through B4. The other half are scenario reads drawn from the
course's own agent and corpus.

The exam blueprint is item 7 of this phase and it sets the item count. It sets a
thirty item exam, fifteen of them breadth items. This plan sets what each topic is
owed inside that breadth half, and the two documents carry the same numbers.

| Topic | Items | Share of the breadth half |
|---|---|---|
| B1 | 3 | 20.0 percent |
| B2 | 4 | 26.7 percent |
| B3 | 3 | 20.0 percent |
| B4 | 5 | 33.3 percent |
| **Total** | **15 of 30** | **100 percent** |

B4 gets the largest share for two reasons. It has the thinnest assessment elsewhere,
as section 6.5 states. And it is the course's differentiator, so the program has the
most reason to see a number on it.

B3 yields the item that B4 gains. B3 has the thickest coverage outside the exam: the
whole first part of the week 1 reading, plus three of the six week 1 self-check items.
It can afford three exam items where B4 cannot.

Two rules bind every breadth item. No item is answerable from general phishing
knowledge, and every stem is drawn from this course's own corpus or its own agent. The
four sample stems above meet both.

---

## 11. Citation verification, stated once

Every citation in every survey reading is verified before publication. The check has
four parts.

1. The document is fetched and read, not cited from memory.
2. The link is confirmed to resolve, and its licence is confirmed to permit use in a
   course. Documents from NIST, CISA and MITRE are public. The OWASP material is
   openly licensed and the exact licence is recorded.
3. An expert subagent review confirms that the claim the citation is attached to is
   actually supported by the document.
4. Any claim the review cannot ground is removed or flagged in the risk register. It
   is never quietly kept.

The revision number and the retrieval date are recorded for each source, because these
documents are revised. Where a revision printed in this plan turns out to be
superseded, the reading cites the current one and the change is reported rather than
silently made.

---

## 12. Assumptions

1. **Reading rate.** The 200 words a minute figure is a standard adult silent reading
   rate for plain prose. No reading rate has been measured for this student
   population. The priced minutes are a study pace, and they are the numbers the week
   budgets use. Section 2 states the rate once for the whole course, and the seven
   week specs price from it rather than from a rate of their own.
2. **Word counts are targets, not measurements.** These readings are not written yet.
   Each count is what the section is planned to run to, inside the 1,400 word ceiling
   the writing standard sets for a weekly reading.
3. **Week 1 has no separate technical reading page.** The week's technical material
   reaches students through the two videos and the notebook markdown. If that changes
   in Phase 2, the week 1 reading band has to be re-split.
4. **This plan holds the only text of the week 1 and week 7 discussion prompts.** The
   week 1 and week 7 specifications now carry the same words, copied from sections 7
   and 8 of this document. Where the two ever differ again, this plan is the source.
5. **The Pellgrave organization supplies every example.** No real company, product,
   person, domain or address appears in any survey reading.
6. **Escalation and ticket handling are described as common practice** rather than
   attributed to a cited requirement, because neither cited document defines them.

---

## 13. Open questions for the program manager

1. **Reading rate. Settled, and recorded here rather than left open.** An earlier
   draft priced week 1 at 100 words a minute, week 6 at 50, and this plan by section.
   All seven weeks now use one rate: 200 words a minute for one pass over the words,
   with everything a page asks beyond that priced as its own named line. The rate is
   stated once, in section 2 above, and every week spec points at it. Every weekly
   reading total is unchanged, because only the way each total is built has changed.
   One question is left for the program manager: should the rate and the named lines
   be shown to students on the module page, or held in the course documents?
2. **B4 assessment depth.** Section 6.5 offers two options: raise the week 6 self-check
   from six items to eight, or leave it at six and let the exam carry most of B4.
   Neither is taken without a decision. The exam blueprint now gives B4 five of the
   fifteen breadth items, the largest share of any topic, which narrows the gap either
   way.
3. **The fifth week 1 source.** The MITRE ATT&CK phishing entry was cut to hold week 1
   to four citations. Add it or leave it out.
4. **Discussion due-day wording.** This plan uses "post by Thursday, reply by Sunday at
   11:59 PM Central" in both prompts. The week 6 prompt words it slightly differently.
   One wording should be chosen and used in all seven weekly discussions.
5. **Whether the week 1 reading should be split into two pages.** It runs to 1,350
   words, above the 900 to 1,050 word target the writing standard sets, because it
   carries two breadth topics. Splitting it into two pages would meet the target but
   would add a page to the module. This plan keeps one page.
