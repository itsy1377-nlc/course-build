::: intro
Instructor-facing reference. This page lives in an unpublished module and is
not visible to students. It exists so that a curriculum committee, a program
assessment cycle, or an accreditation reviewer can see the framework mapping in
one place, with its limits stated rather than implied.

Everything here is pinned to specific published editions: the OWASP Top 10 for
Large Language Model Applications 2026, the OWASP Top 10 for Agentic
Applications 2026, and MITRE ATLAS release 2026.07. Framework identifiers in
this subject change on a scale of months, not years, so a mapping that does not
name its editions is not a mapping.
:::

::: callout warning | The coverage claim, stated honestly
This course substantively covers **3 of the 10** OWASP LLM risks and touches
two more.

Every student-facing page therefore says **"selected OWASP risks"**. No course
material says "the OWASP LLM Top 10", and none should be permitted to. The
phrase implies comprehensive coverage the seven-week calendar cannot deliver,
and a reviewer who checks will find the gap in about four minutes.

The three covered substantively are LLM01 Prompt Injection, LLM02 Sensitive
Information Disclosure, and LLM03 Excessive Agency. LLM04 Supply Chain and
LLM10 Improper Output Handling are touched: named, explained in a paragraph,
and used as framing for a technical decision, but not exploited or remediated
by the student.

This is not a defect to be corrected by adding more identifiers to the syllabus.
It is the honest depth-versus-breadth trade a 3 SCH introductory course makes,
and the defensible position is to name it first rather than to be caught at it.
:::

::: section | OWASP mapping by week
Two OWASP publications carry the course. The LLM Top 10 2026 supplies the risk
vocabulary; the Top 10 for Agentic Applications 2026 (the ASI list) supplies
the agent-specific framing that the LLM list does not.

| Week | OWASP LLM Top 10 (2026) | OWASP Top 10 for Agentic Applications (2026) |
|---|---|---|
| 2 | LLM04 Supply Chain (dependency pinning) | |
| 3 | | ASI02 Tool Misuse and Exploitation |
| 4 | LLM03 Excessive Agency (introduced) | ASI02 |
| 5 | LLM01 Prompt Injection; LLM08 Hidden Context Exposure | ASI01 Agent Goal Hijack |
| 6 | LLM02 Sensitive Information Disclosure; LLM03 Excessive Agency | ASI02; ASI03 Identity and Privilege Abuse |
| 7 | LLM10 Improper Output Handling | ASI01, ASI02, ASI03 (test coverage) |
| Final block | Prevention guidance for LLM01, LLM02, LLM03 | Mitigation guidance for ASI01 to ASI03 |

A note for anyone drafting from older material or from a vendor deck: there is
no publication called the "OWASP Agentic AI Top 10". The agentic list is the
OWASP Top 10 for Agentic Applications, whose entries are numbered ASI01 through
ASI10. Material citing an "Agentic AI Top 10" is either describing this
document under an incorrect name or describing something that does not exist.

Both documents are licensed CC BY-SA 4.0. The course links them and does not
reproduce them. That decision is deliberate: adapting CC BY-SA text into
instructor-authored handouts creates a derivative work that inherits the
ShareAlike obligation, and the person who owns courseware licensing policy
should approve that before any such handout exists.
:::

::: section | MITRE ATLAS mapping, verified against pinned release 2026.07
| Week | Technique |
|---|---|
| 3, 4 | AML.T0053 AI Agent Tool Invocation |
| 5 | AML.T0051 LLM Prompt Injection, with .000 Direct, .001 Indirect, .002 Triggered; AML.T0056 Extract LLM System Prompt |
| 6 | AML.T0086 Exfiltration via AI Agent Tool Invocation; AML.T0085.001 AI Agent Tools; AML.T0080 AI Agent Context Poisoning |
| 7 | AML.T0067 LLM Trusted Output Components Manipulation; AML.T0054 LLM Jailbreak |
| Final block | Mitigation mapping across the above |

**A rename that will trip up anyone reusing older material.** ATLAS renamed
`AML.T0053` from "LLM Plugin Compromise" to "AI Agent Tool Invocation". Any
source still citing the old name is describing superseded content, and the
technique identifier alone will not reveal that.

**Pin the release, not the website.** ATLAS ships roughly monthly and technique
names change between releases. The course pins release 2026.07 from the
`atlas-data` repository releases page rather than citing the live site, so that
every identifier in every course document refers to a fixed, retrievable
artifact.

**Attribution is not optional.** ATLAS is distributed under Apache 2.0, and it
incorporates MITRE ATT&CK, whose terms of use impose a mandatory attribution
string that Apache 2.0 alone would not require. Any handout, slide, or page
carrying ATLAS content reproduces both notices. The required ATT&CK string is:
ATT&CK is a registered trademark of The MITRE Corporation.

**One unresolved tension, flagged for whoever handles copyright clearance.** The
ATLAS site footer and the data repository README assert "ALL RIGHTS RESERVED",
while the terms page and the LICENSE file grant Apache 2.0. These are not
consistent. Reproducing both notices is the safe course, and it is what this
course does.
:::

::: section | NIST AI RMF mapping
The findings documentation work maps to four subcategories of the NIST AI Risk
Management Framework 1.0 (NIST AI 100-1). The text of each is quoted verbatim
below.

| Subcategory | Text, quoted verbatim from NIST AI 100-1 | Where it is carried |
|---|---|---|
| MEASURE 2.7 | "AI system security and resilience, as identified in the MAP function, are evaluated and documented." | Project 2, weeks 7 to the final block |
| MAP 5.1 | "Likelihood and magnitude of each identified impact ... are identified and documented." | The severity rating column of the findings template, final block |
| MANAGE 4.3 | "Incidents and errors are communicated to relevant AI actors ... Processes for tracking, responding to, and recovering from incidents and errors are followed and documented." | The findings report, final block |
| GOVERN 4.3 | "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing." | Rules of Engagement, week 1 |

The ellipses inside MAP 5.1 and MANAGE 4.3 are elisions of the original text,
not paraphrase. Anyone reproducing these in a submission packet should pull the
full sentences from NIST AI 100-1 directly.

**Two honest notes a reviewer is entitled to.**

First, which subcategories fit is an editorial judgment. NIST publishes no
official mapping for coursework, so no external authority validates the four
chosen here. They were selected because the assignment produces the artifact
the subcategory describes, not because a crosswalk asserts the pairing.

Second, AI RMF 1.0 was published in January 2023 and predates the current
agent-security landscape. It contains no agent-specific subcategories at all.
That is why NIST AI 100-2e2025, Adversarial Machine Learning, carries the
attack vocabulary in this course instead, and why the AI RMF is used for the
governance and documentation half rather than the technical half.

**Maintenance flag.** AI RMF 1.0 is under active revision. A revision would very
likely change subcategory identifiers, which would silently invalidate the
table above. Re-verify the four identifiers against the current published
edition before each term, as part of the semester maintenance pass described on
the instructor notes page.

NIST publications are US Government works and are not subject to US copyright.
Cite the NIST reuse terms page rather than 17 U.S.C. 105, because NIST invokes
Public Law 100-519 section 107. NIST also states that foreign rights are
reserved, which is relevant only if this course is distributed outside the
United States.
:::

::: section | How the frameworks are used pedagogically, not decoratively
Worth stating for a curriculum reviewer, because framework identifiers are easy
to sprinkle on a syllabus and hard to actually teach.

Every framework identifier in this course is attached to something the student
does, not to a topic they are told about. The identifiers appear in three
places, all of them load-bearing:

1. **In the harness case files themselves.** Each YAML case in
   `harness/cases/` carries `owasp:` and `atlas:` fields. When a student runs
   the harness, the generated results file prints those identifiers next to the
   result and the evidence. The mapping arrives attached to a number the
   student produced.
2. **In the findings template.** "Framework identifiers" is a required heading
   with points attached. A student who cannot map their own finding loses those
   points.
3. **On the content pages**, where each identifier is introduced with a plain
   language definition before the code appears.

The instructional claim is therefore modest and checkable: students can map a
weakness they have exploited to the correct published identifier, and can read
the corresponding entry with a reading bridge. They are not claimed to have
comprehensive framework knowledge.
:::

::: section | What a program assessment cycle can take directly from this course
Three artifacts exist with no additional instrumentation required.

**The exam export is the per-student, per-outcome score matrix.** Final Part A
carries item-level outcome tags across all six outcomes. Exporting it produces
exactly the matrix a program assessment cycle asks for.

**Module 3, "Break It", is the hands-on lab to submit for knowledge unit
alignment.** It is unambiguously security work rather than a programming
exercise, and it already carries the artifacts reviewers ask about: a defined
authorization boundary, a reproducible environment, and deterministic pass
criteria.

**The behavioral scope evidence is a single grep.** The harness records refused
out-of-scope targets in the `out_of_scope_refused` field of every results file.
That is a trace of what students actually did with an authorization boundary,
not a claim about a hypothetical, and it is the strongest available evidence
for the boundary clause of outcome 5.

Lead with outcome 6 at a program review. It is the best-evidenced outcome in
the course, with eight independent auto-scored sources. Outcome 1 is the
thinnest, and the instructor notes page states why.
:::

::: sources
OWASP Top 10 for Large Language Model Applications 2026, and OWASP Top 10 for
Agentic Applications 2026. Both CC BY-SA 4.0, published by the OWASP Gen AI
Security Project. Linked, not reproduced.

MITRE ATLAS, pinned release 2026.07, distributed under Apache 2.0. ATLAS
incorporates MITRE ATT&CK, which requires this attribution: ATT&CK is a
registered trademark of The MITRE Corporation.

NIST AI Risk Management Framework 1.0 (NIST AI 100-1), January 2023, and NIST
AI 100-2e2025 Adversarial Machine Learning. US Government works, not subject to
US copyright.

OWASP AIVSS, the AI Vulnerability Scoring System, version 0.8. Source of the
simplified four-row severity table used in the final block.

Full resource table with addresses and license notes: blueprint sections 6.1
and 6.3. Mapping source: blueprint section 7.
:::
