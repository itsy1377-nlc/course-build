::: keyfacts
| | |
|---|---|
| Textbook | None. Nothing to buy, nothing to rent |
| Cost | Zero. Every item on this page is free |
| You need | A computer, Python 3.11 or newer, the lab repository, model access |
| Instructor-written material | CC BY 4.0 |
| Assigned outside reading | Capped at 45 minutes a week |
| Pinned versions | OWASP lists 2026, ATLAS 2026.07, AIVSS 0.8 |
:::

::: intro
Everything you read and use this term is listed here, with who wrote it and how
it is licensed.
:::

::: section | What you need
1. **A computer with a browser.** Use a laptop or a desktop for lab work.
2. **Python 3.11 or newer.** You do not need administrator rights.
3. **The lab repository.** Your instructor gives you the link in Week 1.
4. **Model access.** Lab 1 runs on the offline `mock` provider with no key at
   all. In Week 2 you add a free key of your own.

If your campus computer has no internet, the repository holds an offline package
folder. The setup guide shows the command.

Your key is yours alone. Keep it in `.env`, and read clause 3 of the Rules of
Engagement.
:::

::: callout note | You are never sent to a document cold
Some readings below are written for working engineers. They are harder than the
course pages, and that is expected.

The week's Content page introduces each one first: what it is, which part to
read, what to look for, and one question to answer while you read.
:::

::: section | Framework documents you are assigned
| Document | What it is | Licence | Read in |
|---|---|---|---|
| [OWASP Top 10 for LLM Applications 2026](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | Ranked risks in applications built on language models. You read three entries | CC BY-SA 4.0 | Weeks 5, 6, 7 |
| [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | The same idea, aimed at agents rather than chatbots | CC BY-SA 4.0 | Weeks 5 and 6 |
| [MITRE ATLAS](https://atlas.mitre.org/) | Real attack techniques against AI systems, each with an identifier. Pinned to [release 2026.07](https://github.com/mitre-atlas/atlas-data/releases) | Apache 2.0 | Your findings |
| [NIST AI Risk Management Framework 1.0](https://nist.gov/itl/ai-risk-management-framework) | Government guidance on governing AI risk. You use two small parts | US government work | Weeks 1 and 7 |

This course covers selected OWASP risks, not a whole top ten list. ATLAS is
pinned because its technique names change roughly monthly.
:::

::: section | Framework documents that are optional
| Document | Licence |
|---|---|
| [OWASP Agentic AI: Threats and Mitigations v1.1](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/) | CC BY-SA 4.0 |
| [OWASP Securing Agentic Applications Guide 1.0](https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/) | CC BY-SA 4.0 |
| [NIST AI 600-1 Generative AI Profile](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf) | US government work |
| [NIST AI 100-2e2025 Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) | US government work |

Cite the first one as v1.1. The download is newer than its page says.
:::

::: section | Technical documentation
| Reference | Licence |
|---|---|
| [The Python Tutorial](https://docs.python.org/3/tutorial/), sections 4.8, 5.1, 5.5, and 8.3 only | PSF License v2, examples 0BSD |
| [The Python json module](https://docs.python.org/3/library/json.html) | PSF License v2 |
| [Requests Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/) | Apache 2.0 |
| [The OpenAI chat completions reference](https://developers.openai.com/api/docs/api-reference/chat/create) | Vendor documentation, linked only |
| [The OpenAI API specification](https://github.com/openai/openai-openapi) | MIT |

Keep the first three open in a tab.
:::

::: callout warning | One trap in the OpenAI documentation
OpenAI publishes two descriptions of tool calling, and they do not match. The
**function calling guide** documents the newer Responses API.

Every endpoint you can reach in this course implements the older **chat
completions** shape instead. Read the guide, then call Groq or Gemini or Ollama,
and your fields land in the wrong places.

**Use the chat completions reference above.** That is the contract your provider
actually implements.
:::

::: section | Model providers
| Provider | What it is | Licence or policy |
|---|---|---|
| The offline `mock` provider | Ships with the labs and needs nothing. It proves your code works, and nothing about a real model | Course material, CC BY 4.0 |
| [Groq](https://console.groq.com/docs/openai) | Recommended. A published free plan, and it documents tool calling | [Acceptable Use and Responsible AI Policy](https://console.groq.com/docs/legal/ai-policy) |
| [Gemini](https://ai.google.dev/gemini-api/docs/openai) | The backup, and it needs no credit card | [Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy). Docs CC BY 4.0 |
| [Ollama](https://docs.ollama.com/windows) | Runs a small model on your own computer. Its [endpoint](https://docs.ollama.com/api/openai-compatibility) supports tool calling | MIT |

Read both provider policies. Clause 2 of the Rules of Engagement is built on
them, and never put personal information into any hosted model.
:::

::: section | Severity ratings
Severity comes from [OWASP AIVSS](https://aivss.owasp.org/), pinned at version
0.8 and licensed CC BY-SA 4.0. You use a short table built from it, on the
Findings Report Template page. You never compute a score by hand.
:::

::: section | The credit line MITRE requires
If you reuse ATLAS or ATT&CK content anywhere you publish, including a report
you show an employer, include this line:

```
ATT&CK is a registered trademark of The MITRE Corporation.
```

The full [terms of use](https://attack.mitre.org/resources/legal-and-branding/terms-of-use/)
say why. Every page here that cites ATLAS carries that line.
:::

::: section | After the course ends
Module 9, Where To Go Next, lists open tools and practice targets you can keep
using. That includes a guide to secure MCP server development, CC BY-SA 4.0.

Nothing on that page is required, and nothing on it changes the Rules of
Engagement.
:::
