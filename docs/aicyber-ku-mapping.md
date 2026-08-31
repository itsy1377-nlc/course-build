# ITSY 1377 against the NCAE-C CyberAI knowledge units

A mapping of what this course can defensibly claim, with the knowledge unit
text quoted from source rather than summarised, and with every claim tied to
a file a reviewer can open.

Written 31 August 2026. Nothing here is a submission. Validation attaches to
a Program of Study, not to a course, so the correct language throughout is
that the course is *proposed to align to* named units.

## 1. Where the knowledge units come from

Three documents matter, and two of them are public on a `.mil` host. The
earlier belief that the knowledge unit text sat behind DoD authentication was
half right: the document *library* does, but the PDFs themselves are still
directly reachable.

| Document | Version | Where | Reachable |
|---|---|---|---|
| Cyber AI Program of Study validation requirements | December 2024, cover identifier ends `Draft3` | <https://dl.dod.cyber.mil/wp-content/uploads/cae/pdf/unclass-cae_pos-cyberai.pdf> | Public |
| Cyber AI Knowledge Units, Stoneman v.1 | August 2024 | <https://dl.dod.cyber.mil/wp-content/uploads/cae/pdf/unclass-cyber_ai_kus_stoneman.pdf> | Public |
| CAE-CD Knowledge Units, referenced by the above for BNW and NDF | 2024 | <https://dl.dod.cyber.mil/wp-content/uploads/cae/pdf/unclass-cae-cd_ku.pdf> | Public |
| Cyber AI Knowledge Units, "Version 2026" | 2026, newer than Stoneman | Google Drive, linked from Towson University | Public, but **secondary** |
| NCAE-C documents library | current | <https://public.cyber.mil/ncae-c/documents-library/> | **Behind DoD authentication** |

**Two things to carry into any conversation with the program office.**

The Draft 3 requirements document ends its knowledge unit appendix by pointing
at the documents library for "the latest KUs", and that pointer now leads to a
login. And the newest knowledge unit text, "Version 2026", could not be found
on any `.gov` or `.mil` host; it is reachable only from a university page.
Seven plausible `.mil` filenames were probed and all returned 404 against a
control that returned 200. Treat Version 2026 as real but unverified against
an original, and ask the program office for the authoritative current file.

### A discrepancy worth knowing before you write anything

The two sources agree on **which** units are required. They disagree on how
the seven foundational units are bucketed. Draft 3 puts Math Fundamentals
(MAF) in the Cyber Foundational group of four; Version 2026 puts it in the AI
Foundational group of four and leaves three in the Cyber group. The set of
twelve is identical either way, so this changes presentation and not
obligation. Draft 3 also writes CSF as "Cybersecurity Foundations" where the
knowledge unit document titles it "Cybersecurity Fundamentals".

## 2. The AICyber track in full

Twelve units: seven foundational and three core, all required, plus two
optional of which **exactly one** must be adopted.

| | KU | Name | Status |
|---|---|---|---|
| Foundational | **CSF** | Cybersecurity Fundamentals | required foundational |
| Foundational | **ISC** | IT Systems Components | required foundational |
| Foundational | **BSP** | Basic Scripting and Programming | required foundational |
| Foundational | **MAF** | Math Fundamentals | required foundational |
| Foundational | **AIG** | AI Governance, Laws, and Ethics | required foundational |
| Foundational | **AIF** | AI Fundamentals | required foundational |
| Foundational | **MLF** | Machine Learning Fundamentals | required foundational |
| Core | **BNW** | Basic Networking (from CAE-CD) | required core (1 of 3) |
| Core | **NDF** | Network Defense (from CAE-CD) | required core (1 of 3) |
| Core | **AIS** | AI for Security Assessments | required core |
| Optional | **DFA** | Defensive Applications of AI | optional |
| Optional | **OFA** | Offensive Applications of AI | optional |

The other track, **SecureAI** (Security of AI), matters to section 5. Its
units are ADL Adversarial Learning, AIL Securing the AI Lifecycle, AVM
Advanced Math for AI, COF Computer Science Foundations, DPL Deep Learning and
MLA Machine Learning Algorithms, with AIR Risk Management of AI and MES Model
Selection, Evaluation, and Specification as its optional pair.
matters to section 5: ADL Adversarial Learning, AIL Securing the AI Lifecycle, AIR Risk Management of AI, AVM Advanced Math for AI, COF Computer Science Foundations (from CAE-CO), DPL Deep Learning, MES Model Selection, Evaluation, and Specification, MLA Machine Learning Algorithms.
## 3. The finding that should shape the submission

**The AICyber track is about using AI to do cybersecurity. This course is
about attacking an AI.** Those are different directions, and the knowledge
unit text makes the difference explicit rather than arguable.

AIS, the core unit this course currently claims, opens with "Conduct security
evaluations **using AI enhancements to standard tools and techniques**" and
continues "**Leverage AI** to assess the impact of identified
vulnerabilities". In ITSY 1377 the AI is the target, not the instrument.
Students do not use AI to enhance a scanner; they point a harness at an agent
and try to make it leak a credential.

This is not fatal, and section 4 shows exactly which parts still land. But it
means the honest claim is narrower than the blueprint's current wording, and
it means **OFA deserves a serious look**, because three of its six outcomes
describe what this course actually does while only one of AIS's five does.

The blueprint already reached the neighbouring conclusion by a different
route, calling the course "security-of-AI with an offensive centre of
gravity". The knowledge unit text supports that sentence more strongly than
it supports the AIS claim printed beside it.

## 4. What ITSY 1377 satisfies, outcome by outcome

Ratings: **Full** means a graded artifact evidences the whole outcome.
**Partial** means part of it is evidenced and part is absent. **None** means
the course does not touch it. Every Full or Partial names a file.

### AIS, AI for Security Assessments (required core, currently claimed)

Note the plural. The knowledge unit is titled "AI for Security Assessment**s**";
the blueprint writes it singular.

| # | Outcome, verbatim | Rating | Evidence |
|---|---|---|---|
| 1 | Conduct security evaluations using AI enhancements to standard tools and techniques | **None** | The AI is the target here, not the tool. No student tool is AI-enhanced |
| 2 | Produce comprehensive reports with actionable recommendations | **Full** | `content/pages/findings-report-template.md`; Final Part B, graded by `content/rubrics/findings-report.yaml`, where finding accuracy and remediation adequacy carry 70 of 120 points |
| 3 | Leverage AI to assess the impact of identified vulnerabilities and design and implement mitigation strategies | **Partial** | Impact and mitigation are both genuine: the customer canary proves data left, and Module 4 builds a recipient allowlist in `before_tool_call`. But nothing *leverages AI* to do either |
| 4 | Perform threat modeling and develop mitigation strategies, including mapping attack surfaces | **Partial** | The agent's attack surface is enumerated across three untrusted inputs (ticket body, knowledge base article, direct request) in `labs/harness/cases/`. Formal threat modeling is not taught |

| Topic, verbatim | Rating | Evidence |
|---|---|---|
| Security Assessment Methodologies: tools and frameworks; Risk and Vulnerability Assessment | **Full** | The harness is a structured assessment methodology: 8 cases, each declaring `expect:`, 5 trials, deterministic verdicts, and a detector self-test that must pass before results count |
| Assessing and conducting monitoring and detection leveraging AI | **None** | No detection or monitoring content |
| Threat modeling, monitoring, and threat detection; taxonomy of attacks and defense | **Partial** | Taxonomy is strong and machine readable: every case carries `owasp_llm`, `owasp_agentic` and `atlas` identifiers. Monitoring and detection are absent |

**Net: one outcome of four in full, two partial, one absent; one topic of
three in full.** That supports "partial carrier", which is what the blueprint
says. It does not support lead carrier, which the blueprint also says.
### OFA, Offensive Applications of AI (optional, not currently claimed)

| # | Outcome, verbatim | Rating | Evidence |
|---|---|---|---|
| 1 | Identify and explain adversarial attacks on machine learning models | **Full** | This is the course. Eight cases across four weakness classes: direct and indirect prompt injection, injection from trusted internal content, excessive agency, insecure tool authorization |
| 2 | Identify opportunities for AI to enable offensive cybersecurity operations | **None** | Students attack an AI; they do not attack with one |
| 3 | Supplement current offensive TTPs with AI | **None** | |
| 4 | Evaluate the effectiveness of implementing AI for conducting cyber-attacks | **None** | |
| 5 | Discuss the ethical and legal implications of AI-enabled cyber offensive operations | **Full** | Rules of Engagement on 21 pages, and enforced rather than asserted: `AUTHORIZED_TARGETS` in `labs/harness/runner.py` refuses any out-of-scope host and records the refusal in the results file |
| 6 | Correlate offensive AI techniques to existing cybersecurity frameworks | **Full** | Every case file carries OWASP LLM 2026, OWASP Agentic Security Initiative, and MITRE ATLAS identifiers as structured fields |

| Topic, verbatim | Rating | Evidence |
|---|---|---|
| Basics of adversarial learning | **Partial** | Prompt injection is adversarial input against a deployed model, but the course does not cover gradient-based or training-time attacks |
| White-box vs gray-box vs black-box attacks | **Partial** | Students hold full source, so the posture is white-box throughout; the distinction is not taught explicitly |
| Use of AI for attack model frameworks, e.g. cyber kill chain, ATT&CK | **Partial** | MITRE ATLAS is used per case. The kill chain is not |
| Ethical and legal considerations for AI-enabled cybersecurity operations | **Full** | As outcome 5 |
| External data sources, OSINT, dark web | **None** | |
| AI techniques for offensive cybersecurity: vulnerability discovery, penetration testing, reconnaissance | **None** | |
| AI-enhanced red-teaming TTPs | **None** | Students red-team an AI rather than with one |
| Formulation and mapping objectives to AI algorithms and TTPs | **None** | |

**Net: three outcomes of six in full, three absent.** Against AIS's one of
four, OFA is the stronger claim on outcome count, and its three Full ratings
sit on the parts of the course that carry the most graded weight.

The obvious objection is that OFA's title says *applications of* AI, implying
AI as the weapon, and four of its eight topics clearly mean that. A reviewer
could reasonably read outcome 1 the same way. So this is a claim to raise with
the program office rather than to assert: the outcome text on its own fits,
the surrounding topics pull the other way.

### Foundational units, briefly

| KU | Rating | Note |
|---|---|---|
| **BSP** Basic Scripting and Programming | **Partial** | Treated at length in `docs/ku-coverage-analysis.md` and its addenda, which conclude BSP cannot sit in this course. Students write Python across five extension points, but there is no Windows scripting, no regular expressions requirement, and no data structures coverage |
| **AIF** AI Fundamentals | **Partial** | The topic list includes "Intelligent agents" and "Safety and security principles of AI", both central here. The rest of the unit (classical AI, search and optimisation, knowledge representation) is absent |
| **CSF** Cybersecurity Fundamentals | **Partial** | Adversarial thinking, threat actor motivation, vulnerability taxonomy and severity, and access control all appear, but applied to agentic systems rather than taught as fundamentals |
| **AIG** AI Governance, Laws, and Ethics | **None** | Confirmed by search: zero occurrences of EU AI Act, GDPR, CCPA or HIPAA anywhere in the course. "Governance" appears once, on an instructor-facing page |
| **ISC**, **MAF**, **MLF**, **BNW**, **NDF** | **None** | No systems components, mathematics, machine learning theory, networking or network defense content |
## 5. The track question

This belongs in the record even though the program has already chosen
AICyber. The other CyberAI track, **SecureAI**, contains **ADL Adversarial
Learning** and **AIL Securing the AI Lifecycle**. On title alone those
describe ITSY 1377 better than any AICyber unit does.

Three things argue against reopening it, and they are practical rather than
academic. SecureAI's required core also includes Advanced Math for AI,
Machine Learning Algorithms and Deep Learning, none of which a two-year
program is likely to carry. The program has confirmed AICyber as the target
and CAE-CD as the held designation. And a track is a program-level decision
that one course should not drive.

The useful form of the point is narrower: **if a reviewer asks why a
security-of-AI course sits in an AI-for-cybersecurity program of study, the
program needs an answer ready.** The answer available from this document is
that ITSY 1377 carries AIS partially and OFA substantially, and that its
contribution is assessment methodology and authorization discipline rather
than AI-enabled tooling.

## 6. What to claim

| Unit | Claim | Confidence |
|---|---|---|
| **AIS** | Partial carrier: reporting, assessment methodology, attack-surface enumeration | High. One outcome and one topic are fully evidenced, two outcomes partially |
| **OFA** | Raise with the program office. Outcome fit is stronger than AIS; topic fit is weaker | Medium. Depends on how the reviewer reads "applications of AI" |
| **AIF**, **CSF** | Supporting only, if the program wants them named | Low. Real overlap, but not enough to carry a unit |
| Everything else | Do not claim | High |

**Do not claim Defensive Applications of AI.** It was in an earlier draft and
was withdrawn on evidence: the unit's topics are intrusion detection, malware
analysis, predictive modelling and explainable AI, and the course contains
none of them. If exactly one optional unit must be adopted, OFA is the only
candidate this course supports at all.

## 7. Open questions

Four, in the order they will bite.

1. **Where did the six learning outcomes come from?** No document in this
   repository records their source. `course-blueprint.md` section 1 says they
   are "fixed and reproduced verbatim" without saying from what. ITSY 1377 is
   a Local Need number, so there may be no statewide outcome record and the
   six may be locally authored. A reviewer is likely to ask this first.
2. **Which knowledge unit text is current?** Version 2026 is newer than the
   `.mil` Stoneman v.1 but is only reachable from a university page. Ask the
   program office for the authoritative file.
3. **Is OFA available and defensible?** See section 4.
4. **Does the course remain required?** KU alignment excludes electives, and
   the alignment in `course-blueprint.md` section 7.4 is live on the strength
   of a confirmation that this course will be mandatory.

## 8. Sources

Knowledge unit text in sections 2 and 4 is quoted from the documents in
section 1. AIS, BNW, NDF, and the foundational units were read from the
primary `.mil` Stoneman v.1 and the Draft 3 requirements document. DFA and
OFA text was cross-checked between Stoneman v.1 and Version 2026; DFA is
word-for-word identical between them, and OFA differs only in three
orthographic details.

Course evidence is quoted from the repository at the commit that ships with
this document. Counts stated here (8 case files, 21 pages carrying the Rules
of Engagement, 70 of 120 points on the two report rubric rows) were taken
from the files rather than from prior documentation.

Retrieved 30 August 2026. Confirm currency with the NCAE-C program office
before any submission.
