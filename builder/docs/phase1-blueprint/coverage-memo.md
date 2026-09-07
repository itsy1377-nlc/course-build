# Coverage memo: your eight suggested outcomes

**To:** Program manager, Cyber Defense program
**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College
**Date:** 2026-09-03

## Why this memo exists

You circulated eight suggested learning outcomes. They are not adopted and are
not the course's objectives. The course's objectives are the six course learning
objectives (CLOs) in the build prompt, and every rubric and Canvas Outcome is
built on those six.

You asked to see how the course covers your list anyway. For each of your eight:
where it is taught, how it is assessed, and how deep the coverage goes. This memo
reports; it proposes no changes.

## The depth words used here

- **Built and assessed in a lab.** A rubric criterion linked to a Canvas Outcome
  scores it.
- **Practiced in a lab but assessed indirectly.** The scored criterion measures a
  nearby judgment.
- **Carried by survey reading and discussion only.** No lab. A discussion,
  self-check, or the final exam scores it.
- **Stated as policy, not assessed.** Nothing scores it.

## The eight

### 1. Role of AI, generative AI, and agentic workflows

**Taught:** week 1 survey reading, part two. It defines three kinds of AI, with
two examples of each from IT or security work outside phishing. Breadth topic B1.

**Assessed:** the week 1 graded discussion, where each student names a place they
met AI at work and says which kind it was. Also two week 1 self-check items and
the final exam. No rubric criterion here links to a Canvas Outcome.

**Depth:** carried by survey reading and discussion only.

### 2. Common AI-assisted security use cases

**Taught:** week 7 survey reading, part three. One paragraph each on alert triage,
log review, phishing analysis, documentation, scripting help, vulnerability
research, and incident response support. Breadth topic B2.

**Assessed:** the week 7 graded discussion, where each student picks a use case
other than phishing and names one change their own agent would need. Also four
self-check items and the final exam.

**Depth:** split. The course builds one of your seven. Phishing analysis is the
whole build arc, weeks 1 to 7, built and assessed in labs. The other six are
carried by survey reading and discussion only.

### 3. Security operations components

**Taught:** week 1 survey reading, part one. It defines assets, users, networks,
endpoints, logs, alerts, tickets, incidents, escalation, and documentation. A
diagram shows a reported email becoming an alert, then a ticket, then an
incident. Breadth topic B3.

**Assessed:** three week 1 self-check items, part of the week 1 discussion, and
the final exam.

**Depth:** carried by survey reading and discussion only.

### 4. Safe prompting, data minimization, and responsible use

Four things at four depths, reported apart.

**Using AI tools for security tasks.** Every lab, weeks 1 to 7. Built and assessed
in a lab.

**Data minimization.** Taught in the week 3 reading, "What you put in the prompt
is what you expose." Students choose which facts go into the prompt. Week 3
rubric criterion 4 scores a written answer naming one fact the student left out,
and why the verdict did not need it. It links to the CLO1 Outcome. Built and
assessed in a lab.

**Safe prompting.** Taught in week 2 as schema validation with a retry, and in
week 6 as delimiting, treating body text as data, and checking output against
facts. The scored criteria measure the validation record and the judgment about
the guardrails, not the prompt wording. Practiced in a lab but assessed
indirectly.

**Responsible use.** It sits in the AI use policy and syllabus, which permit AI
use with disclosure. The syllabus acknowledgment is ungraded, and no rubric
criterion scores disclosure. Stated as policy, not assessed.

### 5. Extract and organize technical facts

**Taught:** the week 3 lab. Students build a facts block from parsed headers, the
three authentication results, display name against sender domain, and link hosts.

**Assessed:** week 3 rubric criterion 2, "Fact extraction," the primary evidence
for CLO1. Criteria 3 and 4 support it.

**Depth:** for emails and URLs, built and assessed in a lab. Your outcome also
names logs, alerts, system messages, and tickets. The week 3 reading names the
same pattern for those, and one self-check item asks about a log line. Students
never extract from a log or a ticket, so that part is survey reading and a
self-check only.

### 6. Evaluate AI-generated recommendations

**Taught:** week 2, checking output against a schema. Week 6, checking it against
extracted facts and escalating below a confidence threshold. Week 7, scoring
twenty results against ground truth.

**Assessed:** three Outcome-linked criteria, all primary evidence: week 2
criterion 2 for CLO2, week 6 criterion 2 for CLO4, week 7 criterion 3 for CLO6.

**Depth:** built and assessed in labs, the best covered item on your list.
Accuracy, completeness, and safety each have a scored home. Relevance does not;
it is discussed, never scored.

### 7. Common AI risks in security operations

**Taught:** prompt injection is the week 6 lab, with payloads in six positions, a
word-for-word control email, and a benign decoy. Hallucination, data exposure,
privacy, automation bias, and overreliance are the week 6 second reading page,
breadth topic B4. Each is tied to an email students ran.

**Assessed:** injection through week 6 rubric criterion 2, which links to the CLO4
Outcome. Of the other five risks, one is carried by a single week 6 self-check item
and one by the week 6 discussion. All five are carried by the final exam, which gives
breadth topic B4 five of its fifteen breadth items, the largest share of any topic.

**Depth:** injection is built and assessed in a lab. The other five risks are
carried by survey reading, a self-check, and the final exam.

### 8. Document and communicate for both audiences

**Taught:** week 7. The agent writes a triage note in a fixed format: verdict,
confidence, indicators, recommended action, and escalate yes or no. The note also
carries a two-sentence plain-language summary for a nontechnical reader, such as
the employee who reported the email.

**Assessed:** week 7 rubric criterion 2, "Triage note," the primary evidence for
CLO5. Its wording requires the summary to be readable by someone with no security
background, which is where the nontechnical audience is scored.

**Depth:** built and assessed in a lab. One limit: the course produces one note
format, not tickets or reports.

## Summary table

| Your outcome | Carried by | Depth |
|---|---|---|
| 1. Role of AI and agentic workflows | B1 | Survey only |
| 2. Common AI use cases | B2; CLOs for phishing | One of seven in labs; six survey only |
| 3. Security operations components | B3 | Survey only |
| 4. Prompting, minimization, responsible use | CLO1, CLO2, CLO4; nothing for responsible use | Mixed; see below |
| 5. Extract technical facts | CLO1 | Emails and URLs in a lab; other sources survey only |
| 6. Evaluate AI recommendations | CLO2, CLO4, CLO6 | Labs |
| 7. Common AI risks | CLO4 for injection, B4 for the rest | Injection in a lab; five risks survey only |
| 8. Document and communicate | CLO5 | Lab |

**The one gap.** Responsible use, inside your outcome 4, has no CLO and no breadth
topic. It lives in the AI use policy, and nothing scores it.
