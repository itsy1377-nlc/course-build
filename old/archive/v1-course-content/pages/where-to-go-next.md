::: intro
This page is a list of places to go after this course. It is open from day 1
and it stays open. Nothing on it is graded, assigned, or required.

Pick the path that matches what you want to do next. You do not need all five.
:::

::: scope
Several things listed here are real tools that really work. The Rules of
Engagement still apply to every one of them.

You run these against systems you own or that were built to be attacked. Never
against anything else. Leaving this course does not change clause 2. It only
removes the person checking.

The two practice targets below both self-host. That is why they are on this
list and other well-known targets are not.
:::

::: section | Path 1: go deeper on the frameworks
Take this path if the OWASP and MITRE identifiers in your report felt like
labels you copied rather than documents you read.

You have already read one entry from each of the first two. The rest of each
document is written the same way.
:::

::: reading | Before you read the framework documents
**What they are.** These are practitioner documents, not textbooks. They were
written by working engineers for working engineers, so they read harder than
this course does. That is normal.

**What to read.** Pick one entry, not a whole document. Good next entries after
this course: LLM02 Sensitive Information Disclosure, LLM03 Excessive Agency,
and ASI03 Identity and Privilege Abuse. You met all three in weeks 6 and 7.

**What to look for.** In each entry, separate the mitigations that are controls
from the mitigations that are requests. You have a sharp eye for that
difference now. Most readers do not.

**One question to answer while you read.** The document lists ten risks. Which
three did this course actually cover, and what does that tell you about how
much of the field you have seen?

| Resource | Where | License |
|---|---|---|
| OWASP Top 10 for LLM Applications 2026 | `genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` | CC BY-SA 4.0 |
| OWASP Top 10 for Agentic Applications 2026 | `genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` | CC BY-SA 4.0 |
| OWASP Agentic AI: Threats and Mitigations v1.1 | `genai.owasp.org/resource/agentic-ai-threats-and-mitigations/` | CC BY-SA 4.0 |
| OWASP Securing Agentic Applications Guide 1.0 | `genai.owasp.org/resource/securing-agentic-applications-guide-1-0/` | CC BY-SA 4.0 |
| OWASP Gen AI Security Project hub | `genai.owasp.org/` | CC BY-SA 4.0 |
| MITRE ATLAS | `atlas.mitre.org/` | Apache 2.0 |
| MITRE ATLAS data, pinned release 2026.07 | `github.com/mitre-atlas/atlas-data/releases` | Apache 2.0 |
| NIST AI RMF 1.0 | `nist.gov/itl/ai-risk-management-framework` | US Government work |
| NIST AI 600-1 Generative AI Profile | `nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` | US Government work |
| NIST AI 100-2e2025 Adversarial Machine Learning | `csrc.nist.gov/pubs/ai/100/2/e2025/final` | US Government work |
| NIST AI RMF Playbook | `airc.nist.gov/airmf-resources/playbook/` | US Government work |

Two notes. The Agentic AI resource page says v1.0, but the file it serves is
v1.1, so cite v1.1. And ATLAS ships new releases often and renames techniques
when it does, so always write down which release you read.
:::

::: section | Path 2: learn a real red-teaming tool
Take this path if you liked the harness and want the professional version of
it.

Your harness taught you the idea: run the same case many times, use a detector
that checks the world, and publish the rate. These tools do that at scale, with
payload libraries somebody else maintains.

Start with promptfoo or garak. Both are gentler than they look.
:::

::: reading | Before you open a red-teaming tool
**What they are.** Scanners. You point one at a model or an application, it
runs a library of probes, and it reports what got through.

**What to read.** The repository README and the quick start only. Skip the
plugin lists on the first pass.

**What to look for.** Find where the tool decides that a probe succeeded. Every
one of these has a detector, exactly like yours did, and every detector can be
wrong in the same way yours could.

**One question to answer while you read.** Does this tool report a rate across
several runs, or a single yes or no? You know why that matters.

| Tool | Where | License | Note |
|---|---|---|---|
| promptfoo | `github.com/promptfoo/promptfoo` | MIT | Gentlest on-ramp. Cases are declarative YAML, like yours |
| NVIDIA garak | `github.com/NVIDIA/garak` | Apache 2.0 | The best first real scanner. Actively maintained |
| Microsoft PyRIT | `github.com/microsoft/PyRIT` | MIT | Use this exact address. The older `Azure/PyRIT` repository is archived |
| DeepEval | `github.com/confident-ai/deepeval` | Apache 2.0 | Think of this one as evaluation rather than attack |

Point them at your own lab, at a model on your own computer, or at one of the
practice targets below.
:::

::: section | Path 3: find another target to practice on
Take this path if you want to keep attacking, legally.

Both of these run on your own machine. That is the whole point. You own the
system, so you have authorization by definition.
:::

::: reading | Before you set up a practice target
**What they are.** Deliberately vulnerable applications, published so people
can learn on them. HelpDesk Lite was a small one of these.

**What to read.** The setup section of the README, and any file that describes
the challenges. Read the challenge list before you start, so you know what you
are hunting.

**What to look for.** Ask where the untrusted content enters. In your lab it
was a ticket body and a knowledge base article. Find the equivalent here before
you send a single payload.

**One question to answer while you read.** What can this application's agent
actually do, and which of those actions cannot be taken back?

| Target | Where | License | Note |
|---|---|---|---|
| OWASP FinBot CTF | `github.com/GenAI-Security-Project/finbot-ctf` | Apache 2.0 | The strongest next target. Self-hosts with Docker Compose. Use this organization name; the older address redirects |
| Damn Vulnerable LLM Agent | `github.com/ReversecLabs/damn-vulnerable-llm-agent` | Apache 2.0 | The organization was renamed from WithSecureLabs. It was last updated in June 2025, so test that it still runs before you rely on it |
| OWASP Juice Shop | `github.com/juice-shop/juice-shop` | MIT | Classic web application security, with no AI in it. Good for breadth |

Juice Shop is here on purpose. Most agent security problems are ordinary
application security problems with a model in the middle.
:::

::: section | Path 4: secure the tool supply chain
Take this path if week 3 stuck with you, where you learned that a tool is an
attack surface.

The course named the Model Context Protocol and stopped there. It is a standard
way to hand an agent a package of tools, often written by somebody else.
Somebody else's tool is somebody else's attack surface.

This is the fastest growing gap in the field right now, and almost nobody
entering it has read the guidance.
:::

::: reading | Before you read the MCP guidance
**What it is.** A build-side guide. It tells you how to write a tool server
that does not become the way in.

**What to read.** The section on trust between the agent and the tool server.
That is the part that connects to what you already did.

**What to look for.** Look for anything that matches your allowlist. You wrote
a control that decided whether a tool call was allowed to run. Find where that
same decision lives in this design.

**One question to answer while you read.** If a tool server you did not write
returns text into your agent's context, what have you just trusted?

| Resource | Where | License |
|---|---|---|
| OWASP A Practical Guide for Secure MCP Server Development | `genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/` | CC BY-SA 4.0 |
| OWASP Securing Agentic Applications Guide 1.0 | `genai.owasp.org/resource/securing-agentic-applications-guide-1-0/` | CC BY-SA 4.0 |

One warning. There is a well-known deliberately vulnerable MCP server project
that this course does not point you at, because its repository carries no
license file. Practice on the targets in path 3 instead.
:::

::: section | Path 5: learn enough Python to stop needing scaffolds
Take this path if the code was the hard part.

Say the honest thing out loud first. This course gave you working programs and
marked the lines you changed. That is real, and it is not the same as writing a
program from an empty file.

Closing that gap takes practice, not talent. Both books below are free, in
full, on the author's own site.
:::

::: reading | Before you start a Python book
**What they are.** Complete beginner courses in book form, both widely used and
both legitimately free.

**What to read.** Do not start at chapter 1 and read forward. Start with the
chapters on functions and on dictionaries, because those are the two ideas the
agent code leans on hardest.

**What to look for.** Type every example by hand and run it. Reading code and
writing code are different skills, and only one of them transfers.

**One question to answer while you read.** Can you now write, from an empty
file, a function that takes a dictionary and returns one value out of it? That
is the bar this course did not have time to get you to.

| Book | Where | License |
|---|---|---|
| Python for Everybody | `py4e.com` | Site CC BY 4.0. The book itself is CC BY-NC-SA 3.0 |
| Automate the Boring Stuff with Python | `automatetheboringstuff.com` | CC BY-NC-SA 3.0 |

Both books are NonCommercial licensed. You may read them and use them yourself.
Reusing them inside a paid product is a different question, and the answer is
not automatically yes.
:::

::: callout note | What this course did not cover
So you know what is still missing, in one list:

1. Building an agent from nothing.
2. Multi-agent systems.
3. Retrieval systems and vector store security.
4. Model supply chain security.
5. Production hardening: sandboxing, identity design, secrets management,
   monitoring, and deployment.

None of those are beyond you. They were beyond eight weeks.
:::
