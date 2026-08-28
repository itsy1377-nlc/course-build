::: intro
This page lists everything you read and use in this course. It also says who
wrote each item and how it is licensed. Nothing on this list costs money.
:::

::: callout note | There is no textbook
You do not buy a book for this course. There is nothing to order and nothing to
rent. You do not need the bookstore for ITSY 1377.

Every piece of material here is one of two things:

1. **Written for this course** by your instructor, including the lab code, the
   lessons, and the practice data.
2. **Openly licensed**, published free by OWASP, MITRE, NIST, or a software
   project.

Instructor-authored content in this course is released under CC BY 4.0. That
means you may keep it, share it, and reuse it, as long as you credit the source.
:::

::: section | What you need
You need four things, and three of them are free downloads.

1. **A computer with a web browser.** Canvas works best on a laptop or a
   desktop. The Canvas mobile app can show you a grade, but do not try to do
   lab work on a phone.
2. **Python 3.11 or newer.** You do not need administrator rights to install it
   or to make a virtual environment.
3. **The lab repository.** Your instructor gives you the link in Week 1. It
   holds the agent, the target app, and the test harness.
4. **Model access.** The labs ship with an offline `mock` provider, so Lab 1
   works with no key at all. In Week 2 you add a free key of your own.

If your campus lab computer has no internet access, the repository includes an
offline package folder. The setup guide in the repository shows the command.
:::

::: callout warning | Your key is yours alone
You use your own model key. Never a shared one, and never a classmate's.

Keep it in the file named `.env`, which is never committed. The lab code checks
for a key in the wrong place and refuses to start.

Clause 3 of the Rules of Engagement is the full version. Read it.
:::

::: callout note | You are never sent to a document cold
Some readings below are written for working engineers. They are harder than the
course pages, and that is expected.

You never have to read one on your own. The week's Content page introduces each
document first. It tells you what the document is, which part to read, what to
look for, and one question to answer while you read.

Assigned outside reading is capped at 45 minutes per week.
:::

::: section | Framework documents
These four are the reading spine of the security half of the course. All four
are published by OWASP, a nonprofit that writes free security guidance. All
four are licensed CC BY-SA 4.0. This course links to them and does not copy
them.

- **[OWASP Top 10 for LLM Applications 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)**
  is a ranked list of the ten risks a group of practitioners agreed matter most
  in applications built on language models. You read three entries from it:
  LLM01 in Week 5, LLM03 and LLM02 in Week 6, and LLM10 in Week 7. This course
  covers selected OWASP risks, not the whole list.
- **[OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)**
  is the same idea, aimed at agents rather than chatbots. You read ASI01 in
  Week 5 and ASI02 and ASI03 in Week 6. It is the closest thing the field has
  to a shared vocabulary for agent risk.
- **[MITRE ATLAS](https://atlas.mitre.org/)** is a catalog of real attack
  techniques against AI systems, each with an identifier such as AML.T0051. You
  use it to name what you did in a finding, so that a reader anywhere can look
  it up. This course pins **release 2026.07**, because ATLAS ships updates
  roughly monthly and technique names change. The pinned data files are on the
  [ATLAS release page](https://github.com/mitre-atlas/atlas-data/releases).
  ATLAS is licensed Apache 2.0.
- **[NIST AI Risk Management Framework 1.0](https://nist.gov/itl/ai-risk-management-framework)**
  is a United States government publication about governing AI risk. You use
  two small parts of it: GOVERN 4.3 in Week 1, which asks that an organization
  have practices for testing AI and sharing what testing finds, and MEASURE 2.1
  and 2.7 in Week 7. It is a work of the United States government and is not
  subject to United States copyright.

These four are optional. Read them if a topic interests you, or if you want
more than the course assigns.

- **[OWASP Agentic AI: Threats and Mitigations v1.1](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)**
  goes deeper on the same threats, with defenses. Licensed CC BY-SA 4.0. Cite
  it as v1.1, because the download is newer than the page says.
- **[OWASP Securing Agentic Applications Guide 1.0](https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/)**
  is the build-side companion to the agentic top ten. Licensed CC BY-SA 4.0.
- **[NIST AI 600-1 Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)**
  applies the framework above to generative AI. Government work.
- **[NIST AI 100-2e2025 Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)**
  is a taxonomy of attacks on machine learning. It is the hardest document on
  this page. Government work.
:::

::: section | Severity ratings
When you rate how bad a finding is, you use a short table built from
**[OWASP AIVSS](https://aivss.owasp.org/)**, the AI Vulnerability Scoring
System. Its idea is the one this course teaches: the same flaw is worse when
the system can act on the world without asking a person first.

The course pins **version 0.8**. AIVSS is still in development, so treat any
newer version as a change to check rather than a drop-in replacement. You are
never asked to compute a full score by hand. The table is on the Findings
Report Template page. The site is licensed CC BY-SA 4.0.
:::

::: section | Technical documentation
These are the references you use while writing code. Keep the first three open
in a tab.

- **[The Python Tutorial](https://docs.python.org/3/tutorial/)** is the official
  guide. You are assigned four short sections only: 4.8, 5.1, 5.5, and 8.3.
  Licensed under the PSF License v2, with code examples under 0BSD.
- **[The Python json module reference](https://docs.python.org/3/library/json.html)**
  covers reading and writing JSON, which is how the model's replies arrive.
  PSF License v2.
- **[Requests Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)**
  covers the library the labs use to make web requests. Apache 2.0.
- **[The OpenAI chat completions reference](https://developers.openai.com/api/docs/api-reference/chat/create)**
  defines the request and response shape every provider in this course accepts.
  Read the callout below before you use it. Vendor documentation, linked only.
- **[The OpenAI API specification](https://github.com/openai/openai-openapi)**
  is the machine-readable version of the same contract. MIT licensed. Useful if
  you want the exact field names in one file.
:::

::: callout warning | One trap in the OpenAI documentation
OpenAI publishes two descriptions of tool calling, and they do not match.

The **function calling guide** documents the newer Responses API. Every
OpenAI-compatible endpoint you can reach in this course implements the older
**chat completions** shape instead. If you read the guide and then call Groq or
Gemini or Ollama, your fields will be in the wrong places and nothing will work.

**Use the chat completions reference linked above.** That is the contract this
course teaches, and it is the one your provider actually implements.
:::

::: section | Model providers
You need a model to talk to. You have four ways to get one, and all four are
free. Your Week 2 lesson walks you through the choice.

- **The offline `mock` provider** ships with the labs and needs nothing. It is
  a pattern matcher pretending to be a very gullible assistant. It proves your
  code works. It proves nothing about how a real model behaves.
- **[Groq](https://console.groq.com/docs/openai)** is the recommended hosted
  option. It has a published free plan with real limits, and it documents tool
  calling. Its rules for you are in the
  [Groq Acceptable Use and Responsible AI Policy](https://console.groq.com/docs/legal/ai-policy).
- **[Gemini](https://ai.google.dev/gemini-api/docs/openai)** is the backup
  hosted option, and it needs no credit card. Its rules for you are in the
  [Google Generative AI Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy).
  Google documentation content is CC BY 4.0, and its code samples are
  Apache 2.0.
- **[Ollama](https://docs.ollama.com/windows)** runs a small model on your own
  computer. Its installer does not require administrator rights. Its
  [OpenAI-compatible endpoint](https://docs.ollama.com/api/openai-compatibility)
  supports tool calling. The software is MIT licensed.

Read both provider policies linked above. They are short, and clause 2 of the
Rules of Engagement is built on them. Attacking a hosted service breaks those
terms and can close your account.
:::

::: callout stop | A privacy rule that applies to every hosted model
A free hosted model may use what you send it to improve the provider's own
products. Google says plainly not to submit sensitive, confidential, or
personal information to its unpaid services.

So never put personal information into a model prompt. Not yours, not a
classmate's, not a customer's, not a real ticket from your job. The Course
Policies page says more about this.
:::

::: section | The credit line MITRE requires
MITRE ATLAS builds on MITRE ATT&CK, and ATT&CK's terms of use require a
specific credit line. If you reuse ATLAS or ATT&CK content in anything you
publish, including a report you show an employer, include this sentence:

```
ATT&CK is a registered trademark of The MITRE Corporation.
```

The full terms are on the
[MITRE ATT&CK Terms of Use page](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/).
Every page in this course that cites ATLAS carries that line, and your findings
report should too.
:::

::: section | More resources after the course ends
The Module 9 page, Where To Go Next, lists open tools and practice targets you
can keep using after the term. That includes a guide to secure MCP server
development, published by OWASP under CC BY-SA 4.0.

Do not go there for graded work. Nothing on that page is required, and nothing
on it changes the Rules of Engagement.
:::
