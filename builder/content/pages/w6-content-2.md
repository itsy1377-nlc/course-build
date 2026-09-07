::: intro
Injection is one risk. It isn't the whole risk. This page covers five more. Each one lands on an email or a setting from the lab you just ran.

Give this page 22 minutes. Six of those are one pass through the words. The rest is matching each risk back to your own run.
:::

::: section | Five risks that are not injection
Part 1 was about text an attacker planted. Everything on this page happens without an attacker.

Your agent can state something nobody told it. It can put information where it doesn't belong. It can hand a person a judgment that person should have made.

None of those needs a payload. None of them is stopped by the fence you wrote.

Three of the five are answered by code already in your notebook. Two aren't. Knowing which is which is the point of this page.
:::

::: section | Hallucination
**Hallucination is a model stating something that isn't in the facts it was given.**

The national guidance on generative AI calls this confabulation. Search that word if you go looking. It means the same thing. Content arrives stated with confidence and it's wrong.

You've already seen it. Your agent returns an indicator naming a host, and your facts never held that host. The model read it nowhere. It wrote a plausible one.

That isn't injection. Nobody planted it. The model filled a gap in the shape your schema asked for.

The control is code, and you wrote it. `check_against_facts()` walks the answer field by field and asks whether your facts hold each one. An indicator with no matching host is a problem. That problem goes into your export.

A published risk list names the same thing Misinformation. A confident sentence isn't a checked one.
:::

::: section | Data exposure
**Data exposure is putting information somewhere it shouldn't go.**

Email 023 is the case. Its forged headers ask your agent for two things. Return benign, and add the recipient's earlier report history to the answer.

Read that second half again. The first is a wrong verdict. The second is a leak.

That report history belongs to your company. The answer your agent writes travels back toward the person who reported the mail. On 023 the attacker chose what rides along.

The published risk list names this Sensitive Information Disclosure. It gives a whole phase to the moment a model reveals what it was handed. Often something merely asked it to summarize. The attack catalog calls the same move LLM Data Leakage.

The control is code you already have. Your schema names the four fields an answer may carry. `schema_errors()` calls any other name a key that doesn't belong, and an answer holding one doesn't pass. A report history has no field to ride in.
:::

::: section | Privacy
**What you put in a prompt is what you expose.**

Email 023 one step wider is a privacy question. The national guidance lists data privacy as its own risk. Leaked personal data is what it means.

Nothing about a model makes this special. The prompt leaves your machine and reaches a model server. What you sent is what that server saw.

Week 3 gave you the rule and the name. **Data minimization** is sending only the facts a sound judgment needs, and nothing more.

Your facts block is where that rule lives. It carries the sender, the header checks, the link hosts and the flags. It doesn't carry the recipient's home address. It doesn't carry the whole thread.

A prompt is a disclosure. Write it as though the wrong person will read it.
:::

::: section | Automation bias
**Automation bias is trusting an answer because your agent produced it.**

The national guidance is plain about it. It calls automation bias excessive deference to an automated system. It lists overreliance in the same line.

Email 015 is your case. A guardrail that fires on words alone escalates a benign internal reminder. Now picture the analyst who receives it.

The queue says the agent flagged this message. The analyst opens it, sees a security reminder, and closes it. The tenth time, the analyst stops opening them.

The risk runs both ways. Trusting a flag you should have checked is automation bias. So is trusting a clean verdict you should have checked.

No code catches this one. A person catches it, by reading the message before agreeing with the agent.
:::

::: section | Overreliance
**Overreliance is letting your agent decide something a person should decide.**

Your confidence floor exists for this. `CONFIDENCE_FLOOR` at 0.7 says nothing about how good the model is. It's a line saying which cases a person owns.

Emails 009 and 012 sit under it. Email 009 asks for nothing but a reply, and no tool result is decisive on 012. A number below the floor sends both to a person. That's the right outcome.

The published risk list is blunt about why a floor is needed. People treat fluent, confident, well ordered answers as authoritative. Your agent writes fluent answers on every email, including the ones it got wrong.

The risk management framework asks for human oversight that's defined, assessed and written down. Your floor is that writing. It says, before any run, which answers a person will see.

The same framework lists what a trustworthy system is asked to show. Being explainable is on that list. So is being accountable. Neither survives a control nobody wrote down.
:::

::: section | What to do about all five
None of this needs a new control. Three of the five are answered by code already in your notebook.

| Risk | What answers it |
|---|---|
| Hallucination | The fact check, field by field against your facts |
| Data exposure | The answer names your schema allows, and nothing else |
| Privacy | A facts block holding only what a judgment needs |
| Automation bias | A person who reads the message, not only the flag |
| Overreliance | A person deciding every case under the floor |

Two of those rows aren't code. No version of your notebook will make them code. That's the honest end of this page.

Your discussion this week is where you price one of them. You write the extra rule your run needed. Then you say what it costs you on email 015.
:::

::: section | Why your numbers will not match ours
Run this lab twice and you get two different tables. That isn't a fault in your code.

A model picks each word from a set of likely ones, so one prompt can give two answers. Week 1 showed you that with six runs of one question.

Several things move the result, and the model is only one.

| What varies | What it changes |
|---|---|
| The model | A smaller one misses more. A larger one isn't simply better |
| The temperature | Higher settings wander further from one prompt |
| Where the payload sits | The same words in a subject line and a body aren't one attack |
| The exact wording | One sentence rewritten can be the difference |
| Your own prompt | The guard rules are text, and text can be worded well or badly |

A guardrail has no score. It has a rate, and the rate moves.

One control moves less than the rest. Text sitting in the HTML part and nowhere else was written for a machine, and your code sees that without asking a model. A check on structure holds steadier than one on meaning.

That's the shape of the real job. An agent that must be right every time can't be built. One that's right often enough, fails in the direction you chose, and escalates what it's unsure about, can be. It's why every week ends with a person reading the output.

So plan for a share of wrong answers, and decide which kind you would rather have. A false positive costs an analyst ten minutes. A false negative leaves an attack in an inbox. Those aren't equal, and choosing between them is your job, not the model's.
:::

::: reading | Two more of the ten risks
This is the list you read for part 1. Read the entry named Sensitive Information Disclosure and the entry named Misinformation. Skip the rest.

Ask yourself one thing while you read. Which of the two describes what email 023 asked your agent to do?

[Top 10 for Large Language Model Applications, 2026 edition, OWASP Gen AI Security Project](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
:::

::: sources | Sources
Five sources sit behind this reading. The three NIST reports are United States government works, in the public domain and free to read. The other two are openly licensed and free to read. Only the fourth carries a link, because this page uses its entry names.

| Source | What it grounds here |
|---|---|
| *Adversarial Machine Learning: A Taxonomy and Terminology of Attacks and Mitigations*. NIST, AI 100-2e2025, March 2025 | Prompt injection as a named attack class, both direct and indirect. Why a model reads planted text as an instruction. Privacy loss through an injected instruction |
| *Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile*. NIST, AI 600-1, July 2024 | Hallucination, which it calls confabulation. Data privacy. Automation bias and overreliance |
| *Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. NIST, AI 100-1, January 2023 | Human oversight as a written process, and what a trustworthy system is asked to show |
| *Top 10 for Large Language Model Applications*, 2026 edition. OWASP Gen AI Security Project. [genai.owasp.org](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | The entries named Prompt Injection, Sensitive Information Disclosure, Excessive Agency and Misinformation. Creative Commons Attribution-ShareAlike 4.0 |
| *ATLAS*, content version 2026.08. MITRE | Two named techniques, LLM Prompt Injection and LLM Data Leakage. Apache License 2.0 |

The email cases on this page come from the course corpus. Every risk name and every control here traces to one of the five sources above.
:::
