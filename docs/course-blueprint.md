# ITSY 1377: Agentic AI and Security Operations
## Course Blueprint for Review

**Institution:** Northeast Lakeview College, Alamo Colleges District
**Program:** Cyber Defense, A.A.S.
**Format:** 8-week Flex session, fully online, fully asynchronous
**Level:** Introductory (WECM level 1, Local Need)
**Credit:** 3 semester credit hours
**Enrollment assumption:** 30 students maximum
**Materials:** Open educational resources and instructor-authored content only. No purchased or rented textbooks.
**Contact hours:** 2 lecture + 2 lab, 64 per semester, 3.80 workload units (see section 0.8)
**Term shape:** 7 instructional weeks plus a 6-day final block (see section 0.7)
**Course shell:** Built on the NLC Online Course Template (see section 5.6)
**Reading level:** All student-facing content targets 7th grade, enforced by an automated check (see section 5.8)

**Status:** Draft for human review. Phase 1 of the build. Nothing has been built yet: no Canvas scaffolding, no course content, no lab code.

**Document date:** 2026-08-27

---

## 0. Read This First: Corrections and Structural Constraints

Research for this blueprint verified every external claim against primary sources, and several claims in the original brief turned out to be wrong or incomplete. This section carries those corrections plus three structural constraints that arrived with the program's decisions and that reshape the course.

**What changed since the first draft of this blueprint.** The program has confirmed that ITSY 1377 will be **required** rather than elective, that it already holds **CAE-CD** designation with **AICyber** as the target track, that **COSC 1436 is being removed** from the degree as this course is added, that a **Common Cartridge** is the accepted primary Canvas artifact, and that provider terms-of-service risk is **accepted for the proof of concept** with agreements to be in place for the production course. Two of those decisions clear gates that previously blocked the build. Two of them create new constraints, in sections 0.6 and 0.7, that are more restrictive than anything in the original brief.

### 0.1 There is no publication called the "OWASP Agentic AI Top 10"

The real document is **OWASP Top 10 for Agentic Applications 2026** (version 2026, dated December 2025, published by the OWASP Gen AI Security Project's Agentic Security Initiative). Its risk IDs are prefixed ASI, not AGENTIC: ASI01 Agent Goal Hijack, ASI02 Tool Misuse and Exploitation, ASI03 Identity and Privilege Abuse. It is a final release, not a draft.

A separate and genuinely distinct document, **Agentic AI: Threats and Mitigations** (version 1.1, December 2025), also exists. The Top 10 is the ranked risk list; the Threats and Mitigations guide is the underlying threat model. The course must not conflate them.

**Action taken:** the blueprint uses the real names throughout.

### 0.2 The current OWASP LLM list is the 2026 edition, not 2025

**OWASP Top 10 for LLM Applications 2026** was published August 4, 2026. It renumbers the 2025 list and adds a new entry. The numbering that matters for this course:

- LLM01:2026 Prompt Injection
- LLM02:2026 Sensitive Information Disclosure
- LLM03:2026 Excessive Agency
- LLM08:2026 Hidden Context Exposure (new in 2026)
- LLM10:2026 Improper Output Handling

Note a live inconsistency the course has to handle: OWASP's own per-risk web pages (for example the prompt injection deep dive) still render 2025 numbering, while the PDF is 2026. Students who click a link will see different numbers than the assigned PDF. **Recommendation:** cite the 2026 PDF as authoritative, label the web pages as the 2025 text where they are used, and say so on the page.

### 0.3 The NSA CyberAI knowledge unit claim is materially wrong in two ways

An NSA/NCAE-C Cyber AI Program of Study does exist. Two corrections:

1. **The two named knowledge units are not peers.** CyberAI splits into two tracks: Security of AI (SecureAI) and AI for Cybersecurity (AICyber). Both named KUs sit in AICyber only. "AI for Security Assessment" (AIS) is one of three **required core** KUs. "Offensive Applications of AI" (OFA) is one of two **optional** KUs, of which exactly one must be adopted.

2. **A course cannot carry validation.** Validation attaches to a Program of Study, not to a course. Correct committee language is that the course is *proposed to align to* named KUs within a PoS submission.

Two hard gates were identified, and **both are now cleared** by decisions recorded in section 10:

- **Eligibility: CLEARED.** CyberAI PoS validation is open only to institutions already holding a current CAE Cyber Defense (CAE-CD) or CAE Cyber Operations (CAE-CO) designation. Research could not verify a designation for any Alamo college from public sources, but the program has confirmed it **already holds CAE-CD**, and **AICyber is the target track**. The gate is satisfied.
- **The elective disqualifier: CLEARED.** The requirements document states that KU-aligned courses must be mandatory for all students in the program, and that no elective or optional courses may be included in the KU alignment. The program has confirmed **ITSY 1377 will be a required course**. The gate is satisfied.

Because both gates are cleared, the KU alignment in section 7.4 is live rather than conditional. One consequence follows immediately and is treated in section 0.7: removing COSC 1436 from the degree may move a foundational programming knowledge unit onto this course.

On the mapping burden, the news is good: KU outcome alignment is "listing only, no assessment of outcomes," and KU topics are recommended rather than required. What each KU-aligned course must supply is a syllabus from the last three years plus guidelines for one hands-on lab. This course produces both easily.

Caveat on currency: the authoritative PoS document's own internal filename identifies it as Draft 3, and the canonical NCAE-C document library is now behind DoD authentication, so newer versions could not be checked. Confirm current requirements with the NCAE-C program office before committing curriculum.

### 0.4 The WECM number is well formed, and the Local Need test has three criteria, not one

ITSY 1377 decodes correctly under THECB rules: first digit 1 = introductory, second digit 3 = three semester credit hours, and a 7 in the third digit is what designates a Local Need course. The second 7 is only sequence position within the 70 to 79 Local Need block and carries no independent meaning. No statewide WECM course can be numbered ITSY 1377, because that block is reserved for institution-specific Local Need courses. The number is fit for purpose.

Two corrections:

1. **The governing document changed.** GIPWE has been replaced by the THECB Workforce Education Division "Career and Technical Education Guidelines," effective April 1, 2025, following House Bill 8 (88th Legislature).

2. **"No equivalent course exists" is one of three approval criteria**, not the whole test. Under 19 TAC section 2.329 the Assistant Commissioner considers: (1) no WECM course has equivalent end-of-course outcomes; (2) the course is designated SCH or CEU with assigned contact hours; and (3) the submission is administratively complete. The Guidelines separately require that "evidence of need for the course should be substantiated by support from business and industry in the local geographical area." **Someone needs to gather industry letters. That is not a writing task and it has a lead time.**

**The highest equivalence risk found:** Houston Community College holds **ITAI 1372, "Artificial Intelligence (AI) in Cybersecurity"** (3 credit hours, 2 lecture + 4 lab), still active as of the 2025-26 catalog. It is itself a Local Need number. Whether an existing Local Need course at another institution counts against this proposal is genuinely unresolved: the rule bars approval where an equivalent course is "in the WECM database," while the Guidelines glossary says Local Need courses "are not contained in" that database and are added only to the originating institution's inventory. **This ambiguity should be put to THECB directly (512-427-6101) before the submission is written.** The distinguishing argument is available and strong: ITAI 1372 is about applying AI to cyber defense, while ITSY 1377 is about securing agentic AI systems, which is the opposite direction.

**Contact hours.** For 3 SCH the THECB preferred range is 48 to 96 contact hours per semester, and Local Need courses must fall between 16 and 176. The split cannot be chosen on curricular grounds alone, because the adjunct workload cap constrains it. **Section 0.8 works this out and recommends 2 lecture + 2 lab, 64 contact hours.** Note that HCC codes its comparable courses (ITAI 1372 and ITSY 1372) at 2 lecture + 4 lab, which would be the natural curricular choice here and is not available to us.

### 0.5 The degree currently requires programming, and that is changing

The brief states there is no enforced programming prerequisite. That was true in a narrow sense and misleading as written. It is now being overtaken by a curriculum decision.

Verified against the 2026-2027 NLC catalog: **COSC 1436 Programming Fundamentals I is currently a required course in the Cyber Defense, A.A.S. plan (Semester II)**, and in Semester I of the Level I Certificate. It has been in the plan since at least 2023-2024. Its own prerequisites are developmental, not programming.

**The program has now confirmed that COSC 1436 is being removed from the Cyber Defense A.A.S., and ITSY 1377 is being added in its place.** That resolves the original wording problem and creates a larger one, which section 0.7 treats separately.

**Recommended wording for the committee, valid after the change:** "The Cyber Defense A.A.S. does not require a programming course. ITSY 1377 assumes no prior programming and teaches Python inside the course, scoped narrowly to calling an API."

That is accurate and simple. It is also a claim the program should make deliberately rather than by accident, because it is a real reduction in the degree's programming content.

### 0.6 The programming knowledge unit is resolved, and it does not live in this course

**Status: resolved.** This was the blocking finding in the previous draft. A companion document, `ku-coverage-analysis.md`, works it through in full. The summary:

**ITSY 1377 cannot carry the NSA Basic Scripting and Programming (BSP) knowledge unit**, for four independent reasons: it defensibly covers 9 of BSP's 18 topic elements (50 percent against a required 75); it cannot defend two of BSP's six outcomes at all (system administration automation, and regular expressions); closing the gap needs roughly 26 instructional hours in a 64-hour course, and every combination of cuts that frees them damages at least three of this course's own six outcomes; and, decisively, **this course must permit AI assistance to assess its own outcome 6, while BSP requires unassisted "write and execute" evidence.** One syllabus cannot hold both positions.

**That last argument is why the carrier must be a conventional programming course, and it is also why no redesign of ITSY 1377 fixes this.** It is not a scheduling problem.

**The resolution uses courses the college already owns.** COSC 1436 is retained. BSP is carried jointly by **COSC 1436 plus DSAI 1373 Computing Foundations plus ITSC 1316**, reaching 77.8 percent, or 88.9 percent once ITSC 1316's local objectives are revised. **No new scripting course is required.** One verification item decides it: whether DSAI 1373's syllabus teaches regular expressions and documents Python execution on both Windows and Linux. DSAI 1373 is a Local Need course, so the college owns those outcomes and can insert them if absent.

**What ITSY 1377 carries instead:** AI for Security Assessment as lead, Defensive Applications of AI as co-lead, and the legal and regulatory half of AI Governance as a supporting carrier. Three knowledge units is the ceiling for a 3 SCH course and this sits exactly on it. Two of the three have no other possible home in the catalog, which is the strongest available justification for the course. **It must not be listed as a BSP carrier.**

**One consequence the committee should see plainly.** The Cyber Defense A.A.S. is exactly 60 semester credit hours, and 60 is the statutory Texas ceiling under SB 497 (2013). **Adding this course means removing 3 credit hours from the existing plan.** The companion document gives concrete 60-hour plans and recommends assembling a separate "AI Cyber Defense" program of study from existing Cyber Defense and DSAI courses, rather than deleting forensics and incident response from a degree whose identity depends on them.

### 0.7 The 8-week Flex session is seven instructional weeks, not eight

Confirmed against both official district calendar PDFs (AY2025-26 and AY2026-27), not assumed. **Six of the eight published Flex sessions run Monday to Saturday and span exactly 55 inclusive days, which is 7 full weeks plus 6 days.**

With work due Sundays at 11:59 PM Central, the session contains exactly **seven Sunday deadlines** (days 7, 14, 21, 28, 35, 42, and 49), followed by a **six-day final block from Monday to Saturday** (days 50 to 55). An eighth Sunday deadline would fall on day 56, after the session has closed. Week 8 has no Sunday in it.

**And the final exam is carved out of that block, not added to it.** Every Flex session has a separately printed final exam window, and it sits inside the last week rather than after instruction. Mapped onto the grid, it opens on day 1, 2, or 3 of week 8 and runs to the end of the session. No extra time is granted for it.

| | |
|---|---|
| Session length | 55 days (7 weeks, 6 days) |
| Sunday deadlines available | **7** |
| Final block | 6 days, Monday to Saturday, with no Sunday |
| Final exam window | Carved out of the final block, opening day 1 to 3 of week 8 |
| Census date | **Day 8** in seven of eight sessions |
| Last day to withdraw | Roughly day 39 to 43 |

**Two scheduling traps the build must handle:**

1. **The exam window moved between academic years.** AY2025-26 runs Flex finals **Wednesday to Saturday**, ending on the session's last day. AY2026-27 runs them **Monday to Friday**, ending one day before close. A course that assumes one will misalign in the other. The safe intersection is **Wednesday to Friday**, which is compliant in both, and that is what section 2 uses.
2. **Spring Flex I breaks the 55-day model entirely.** Both Spring Flex I sessions start on a **Tuesday** (MLK Day takes the Monday) and span **61** days because a 7-day Spring Break sits inside them. Net of the break they are 54 active days, materially the same shape, but any template with hard-coded dates or a hard-coded Monday start will be wrong. **Build the course to relative day offsets and publish a per-session date map.**

**Two compliance requirements that follow from the calendar, and that the design must satisfy:**

- **Census is day 8, so gradeable evidence of participation must exist inside week 1.** Alamo requires that fully online courses assign an **attendance verification activity completed by the third class day**. The Module 0 gate in section 3 is that activity, which is why it is due on day 3 rather than day 7.
- **A final exam is expected.** The St. Philip's College student handbook states that "a comprehensive final evaluation, not to exceed three hours in length, shall be given at the end of each course at the official scheduled final exam time," and the NLC Faculty Handbook closeout procedure requires submitting a copy of the final exam with an answer key. Both are college-level rather than confirmed district board policy, so verify with the department chair, but design to them.

**Consequence: the course has seven instructional weeks plus a final block, and the original eight-week grid does not fit.** The revised schedule is in section 2. This is a structural correction rather than a tuning adjustment, and it removes recovery room that section 8.2 had already identified as missing.

### 0.8 The contact-hour split is decided by the workload cap, and 2 lecture + 4 lab is not available

Direct answer to the question asked: **2 lecture + 4 lab does not fit under 3.9 workload hours. It comes to 5.60.** It is not close, and it is not viable under any weighting convention found anywhere in Texas.

Alamo Colleges District procedure **D.5.1.2, Faculty Teaching Loads**, states the formula verbatim: "A workload unit is defined as one faculty lecture hour." The load table gives lecture at **1.0 workload unit per lecture hour** and laboratory at **0.80 workload unit per faculty class contact hour per week**, with a footnote that "Effective, January 1, 2026, the lab loading will be **0.90** workload units per faculty class contact hour per week." As of now the governing factor is 0.90. The document's own worked example confirms the arithmetic: a 3-3-2 course is 3 + (2 x 0.80) = 4.60 workload units.

So: **workload units = lecture hours + (lab hours x 0.90)**.

| WECM split | Contact hours per semester | Workload units | Under 3.9? |
|---|---|---|---|
| 3 lecture + 0 lab | 48 | **3.00** | Yes |
| **2 lecture + 2 lab** | **64** | **3.80** | **Yes, recommended** |
| 3 lecture + 1 lab | 64 | 3.90 | Exactly at the cap, no headroom |
| 2 lecture + 3 lab | 80 | 4.70 | No |
| 1 lecture + 4 lab | 80 | 4.60 | No |
| 2 lecture + 4 lab | 96 | **5.60** | **No** |

**Recommendation: 2 lecture + 2 lab, 64 contact hours per semester, 3.80 workload units.** It is the best available option on four counts. It stays under the cap with real headroom, unlike 3+1 which lands exactly on it. It is a THECB **preferred** combination for a 3 SCH course, comfortably inside both the 48 to 96 preferred band and the 16 to 176 band for Local Need courses. It preserves a **formal laboratory designation**, which matters because under THECB's definitions lab is "skill development, application, and practice of knowledge," which describes weeks 3 through 7, and because a lab designation materially strengthens the hands-on lab evidence a CAE knowledge unit submission requires. And it keeps the course at 3 SCH, so the 4 SCH non-starter never arises.

The alternative, 3 lecture + 0 lab at 3.00 units, is safe on workload but gives up the lab designation entirely, which is the wrong trade for a course that is mostly hands-on.

**On the number 3.9 itself.** D.5.1.2 never states it. What it does state is that "full-time faculty includes all faculty teaching 12 or more workload units" and that "adjunct faculty will be assigned fewer than 12 workload units" in a long term. Three courses at 3.9 is 11.7, just under 12; three at 4.0 would be exactly 12 and would trip full-time classification. That derivation is an inference rather than a quoted rule, but it explains the constraint, and both TRS membership rules and the Affordable Care Act are documented drivers of adjunct load caps across Texas community colleges.

### 0.9 Two smaller factual items

- **Location:** every official NLC page gives the city as Universal City, Texas 78148. No official source names Live Oak. Remove it.
- **Degree name:** the catalog prints **"Cyber Defense, A.A.S."** Sibling colleges use different names (San Antonio College: "Information Assurance and Cybersecurity, A.A.S."; St. Philip's College: "Information Technology Cybersecurity Specialist, A.A.S."). Only NLC uses the Cyber Defense name.

---

## 1. The Six Learning Outcomes

These are fixed and reproduced verbatim. Every module traces to at least one.

| # | Outcome |
|---|---|
| **O1** | Automate interaction with language model APIs using scripts, including request construction, response parsing, and error handling. |
| **O2** | Configure and extend an agentic system that integrates a language model with external tools. |
| **O3** | Identify security weaknesses in agentic systems, including prompt injection, excessive agency, and insecure tool authorization. |
| **O4** | Execute and extend a structured test harness against an agentic system and interpret the results. |
| **O5** | Document security findings and apply remediations within defined authorization boundaries. |
| **O6** | Evaluate AI-generated code and output for correctness before use. |

Section 8 states plainly where two of these over-reach what 8 weeks can deliver, and how the assessment design compensates without rewording them.

---

## 2. Week-by-Week Outline

**The calendar is seven instructional weeks plus a six-day final block.** See section 0.7. Weeks run Monday to Sunday with work due Sunday 11:59 PM Central. The final block is Monday to Saturday and contains the final exam.

**Every weekly module is built to the NLC template's four-part anatomy:** an Overview page, a Content page, the graded Assignments, and a Wrap-up page. The tables below describe what goes into those four parts; they are not a separate structure. All student-facing text is written to the plain-language standard in section 5.8.

**Build to relative day offsets, not fixed dates.** Six of eight Flex sessions are the 55-day Monday-to-Saturday shape, but both Spring Flex I sessions start Tuesday and run 61 days with Spring Break inside. The course ships a per-session date map rather than hard-coded dates.

**On currency.** This course teaches a subject that did not have a stable vocabulary two years ago, so material is pinned to the most recent published sources rather than the ones most textbooks still cite: the OWASP LLM Top 10 **2026** edition, the OWASP Top 10 for Agentic Applications **2026**, and MITRE ATLAS release **2026.07**. Section 8.9 is blunt about the maintenance cost.

### The schedule at a glance

| Wk | Days | Focus | Graded deliverable | Due | Outcomes |
|---|---|---|---|---|---|
| **0/1** | 1 to 7 | Orientation, rules of engagement, environment, Python part 1 | **Module 0 Gate** (day 3) + Lab 1 | day 3, day 7 | O5, O1 |
| **2** | 8 to 14 | Python part 2, first model calls, response parsing | **Module 1: Talk to the Model** | day 14 | O1, O6 |
| **3** | 15 to 21 | Error handling, tool schemas, reading the agent skeleton | **Project 1 checkpoint** (pass/fail) | day 21 | O1, O2, O6 |
| **4** | 22 to 28 | The agent loop, adding a tool | **Module 2: Give It Hands** (Project 1 due) | day 28 | O2, O1, O6 |
| **5** | 29 to 35 | Direct and indirect prompt injection | Attack Lab 1 + one-page practice finding | day 35 | O3, O5, O6 |
| **6** | 36 to 42 | Excessive agency, insecure tool authorization, harness intro | **Module 3: Break It** + **Project 2 checkpoint** (pass/fail) | day 42 | O3, O4 |
| **7** | 43 to 49 | Extending the harness, interpreting results, remediation | **Module 4: Fix It** (Project 2 Part A) | day 49 | O4, O5, O3 |
| **F** | 50 to 55 | Findings report and final assessment | **Part B report** (day 52) + **Final Exam** (day 54) | see below | O3, O4, O5, O6 |

Weeks 1 through 4 protect Python. Weeks 5 through 7 are the security arc. The final block adds no new content.

### Module 0 and Week 1: Orientation, rules of engagement, environment, Python part 1

| | |
|---|---|
| **Topics** | What an agentic system is and why it fails differently; authorization and scope before technique; Python part 1 (variables, types, strings, lists, dictionaries, running a script) |
| **Activities** | Ungraded entry diagnostic; environment setup with a screencast per platform; read-and-predict exercises on provided code |
| **Graded** | **Module 0 Gate, due day 3**: run `verify_env.py`, paste the per-student hash it prints, and pass the Rules of Engagement mastery quiz (100% required, unlimited attempts, gates Module 1). **Lab 1 due day 7** |
| **Outcomes** | **O5** (authorization boundaries introduced and graded here), **O1** begins |
| **Framework** | NIST AI RMF GOVERN 4.3 |

**The day-3 deadline is a compliance requirement, not a design preference.** Census falls on day 8, and Alamo requires fully online courses to assign an attendance verification activity completed by the third class day. The Module 0 Gate is that activity. It does three jobs at once: it satisfies attendance verification, it produces the graded Rules of Engagement acknowledgment the brief requires in week 1, and it proves the student has a working environment before any content depends on it.

The Rules of Engagement are course content, not a legal disclaimer. Twelve scenario items, not definitions ("You want to run your harness against your roommate's Discord bot. Permitted? Cite the clause."). Two required free-text fields: a typed signature block, and "in my own words, the one thing I may never do in this course." That paragraph is quoted back to the student in the final exam.

The diagnostic is **deliberately ungraded**. Grading it would make students optimize it with AI and destroy the only clean baseline in the course.

### Week 2: Python part 2, first model calls, response parsing

| | |
|---|---|
| **Topics** | Loops, conditionals, functions; the OpenAI-compatible chat completions request and response shape; pulling a field out of a nested dictionary |
| **Graded** | **Module 1: Talk to the Model.** Extend the provided client with retry and backoff on 429 and 5xx, parse and validate a structured JSON response, and handle a malformed body |
| **Outcomes** | **O1**, **O6** |
| **Framework** | OWASP LLM04:2026 Supply Chain (why dependencies are pinned) |

Substantial helper code is pre-baked and read rather than authored. Students modify and extend; they do not write from nothing.

### Week 3: Error handling, tool schemas, reading the agent skeleton

| | |
|---|---|
| **Topics** | try/except, timeouts, retry applied to the scaffold; what a JSON tool schema is; guided line-by-line read of the agent skeleton |
| **Graded** | **Project 1 checkpoint (pass/fail, diagnostic).** The skeleton runs end to end and one tool is registered, plus three sentences on what happens when the model decides to call it |
| **Outcomes** | **O1**, **O2**, **O6** |
| **Framework** | OWASP ASI02 Tool Misuse; MITRE ATLAS `AML.T0053` AI Agent Tool Invocation |

**This is now the week most likely to break students**, and the design treats it as such. It carries the hardest abstraction in the course, which is the inversion from "my script calls the model" to "the model calls my function." It also sits immediately after census, so students who should have dropped are still enrolled.

Mitigations, all concrete: the checkpoint is pass/fail and has a fallback path, so a stuck student still passes and still enters week 4 on schedule; an instructor-published `agent-working` branch is released on day 18, before the deadline rather than at it; required reading for the week is capped at 45 minutes and spent entirely on the annotated skeleton; and a "Top 10 Week 3 Errors" thread is pinned on day 15, before anyone has hit them.

Note for anyone drafting from older material: ATLAS renamed `AML.T0053` from "LLM Plugin Compromise" to "AI Agent Tool Invocation." Any source citing the old name is describing superseded content.

**MCP is named here, and only named.** Students will meet the Model Context Protocol the moment they touch a real agent, so the Content page explains what it is in one short section: a standard way to hand an agent a package of tools, often written by someone else. That lands the security point the week is already making, which is that a tool is an attack surface and someone else's tool is someone else's attack surface. ATLAS carries `AML.T0110` AI Agent Tool Poisoning, whose description explicitly covers MCP servers. Students do not build or attack an MCP server here; that is Module 9.

### Week 4: The agent loop, adding a tool

| | |
|---|---|
| **Topics** | The bounded loop; message accumulation; tool dispatch; what happens when a tool errors |
| **Activities** | Trace the loop by hand on paper before touching code |
| **Graded** | **Module 2: Give It Hands. This is Project 1.** Register and implement a second, student-designed tool with a student-authored JSON schema, and wire the allowlist |
| **Outcomes** | **O2**, **O1**, **O6** |
| **Framework** | OWASP LLM03:2026 Excessive Agency, foreshadowed: the tool students just added has no authorization check, which they discover in week 6 |

The autograder requires a **student-designed** tool with a **student-authored** schema, verified by invoking it with generated arguments. That is deliberate: it converts "filled in the registry" into "designed an interface," which is what outcome 2's verb actually asks for. Do not drop it under time pressure.

### Week 5: Direct and indirect prompt injection

| | |
|---|---|
| **Topics** | Direct injection; indirect injection from untrusted content; indirect injection from "trusted internal" content; why prompt-level defenses are probabilistic |
| **Graded** | Attack Lab 1 against the shared target, plus a **one-page practice finding** on the report template |
| **Outcomes** | **O3**, **O5** begins, **O6** |
| **Framework** | OWASP LLM01:2026; ASI01 Agent Goal Hijack; ATLAS `AML.T0051` with `.000` Direct, `.001` Indirect, `.002` Triggered; `AML.T0056` Extract LLM System Prompt |

The practice finding is a rehearsal for the graded report in the final block, on the identical template. It is the only rehearsal the compressed calendar allows, down from two.

### Week 6: Excessive agency, insecure tool authorization, harness introduction

| | |
|---|---|
| **Topics** | Excessive agency: irreversible actions with no confirmation. Insecure tool authorization: the tool that never asks who is calling. How a harness decides an attack succeeded |
| **Activities** | Attack Lab 2 hands-on for excessive agency; insecure tool authorization as a **guided walkthrough** of an annotated exploit; run the provided harness unmodified and read its output format |
| **Graded** | **Module 3: Break It** and the **Project 2 checkpoint (pass/fail, diagnostic)** |
| **Outcomes** | **O3**, **O4** |
| **Framework** | OWASP LLM03:2026, LLM02:2026; ASI02, ASI03; ATLAS `AML.T0086`, `AML.T0085.001` |

**This week carries the biggest deliberate cut in the course.** Insecure tool authorization is no longer a hands-on exploitation lab; it is a guided walkthrough students read and answer questions about. Section 8.3 states the cost plainly.

Moving the harness introduction here, rather than into week 7, is what makes week 7 extension-only instead of introduction plus extension.

### Week 7: Extending the harness, interpreting results, remediation

| | |
|---|---|
| **Topics** | Adding structured attack cases; N-of-M trials and what a 3 of 5 result means; classifying pass, fail, and inconclusive; fixing the class of bug rather than the instance |
| **Activities** | Add at least two new attack cases (YAML, no Python required); run against the target; interpret a deliberately poisoned results file; implement one remediation and re-run |
| **Graded** | **Module 4: Fix It. This is Project 2 Part A** |
| **Outcomes** | **O4**, **O5**, **O3** |
| **Framework** | OWASP LLM10:2026 Improper Output Handling; NIST AI RMF MEASURE 2.1, MEASURE 2.7 |

The poisoned-results exercise is worth calling out: every student receives a results file in which all payloads report SUCCESS, because the detector matches the payload string appearing anywhere in the transcript, including inside refusals. The question is "what would you conclude, and what is the first thing you would check?" It is auto-gradeable by keyword and it targets the exact failure mode that ruins real security reports.

**Remediation is graded on two suites, not one.** The attack suite must go from succeeding to failing, **and** the benign functionality suite must still pass. Without the second clause, deleting the tool would "remediate" everything. With it, the student must produce a scoped fix rather than a lobotomy.

### The final block: days 50 to 55, Monday to Saturday

| Day | What happens | Due |
|---|---|---|
| 50 (Mon) | Exam review module released. **No new content.** Late window opens on Part A at 90% credit | |
| 51 (Tue) | Backlog day. **Hard close on all late work from weeks 1 to 7** | Late work, 11:59 PM |
| 52 (Wed) | **Project 2 Part B due.** **Final exam opens** | Part B, 11:59 PM |
| 53 (Thu) | Exam window open | |
| 54 (Fri) | **Final exam due, hard** | Final exam, 11:59 PM |
| 55 (Sat) | No student deliverable. Instructor grading and submission | |

**Why Wednesday to Friday.** The published Flex exam window is Wednesday to Saturday in AY2025-26 and Monday to Friday in AY2026-27. Wednesday to Friday is the intersection, so the same course shell is compliant in either year with no re-dating.

**Project 2 Part B (due day 52)** is the findings report: one remediation implemented and verified with harness evidence, a second specified in writing with the test that would verify it, and the whole thing written inside the stated authorization boundary. Severity uses the simplified table derived from OWASP AIVSS described below.

**The final exam (opens day 52, due day 54, three-hour cap, asynchronous, open book, AI use permitted but must be declared)** has three parts, specified in section 3.

**How a student who is behind still finishes.** Every scaffold-dependent artifact has an instructor-published fallback branch. A student whose harness never ran pulls `harness-working` on Monday and does the analysis, remediation, and exam against it. That caps the artifact at 80 percent, but it is not a zero and not a blocker. The exam is graded against whatever the student submitted, fallback branches included, so it is always completable. Monday and Tuesday exist so backlog clears **before** the exam window opens.

**Because there is no recovery room after day 54, every grade-protection mechanism is front-loaded:** unlimited gate retakes, a dropped lowest lab, fallback branches, and a 90 percent late window on Part A. There are no incompletes and no post-exam make-up work. That is stated in week 1 and repeated on day 50.

**Severity rating uses a simplified table derived from OWASP AIVSS**, the AI Vulnerability Scoring System, rather than an invented rubric. AIVSS extends CVSS with the idea that agentic capability *amplifies* a vulnerability: the same flaw is worse when the system can act on the world without asking. That is precisely what weeks 5 through 7 teach. Two honest limits: AIVSS is at **v0.8** and still in development, with v1.0 expected late 2026, and its calculator is hosted on a personal domain. The course **pins v0.8**, ships a four-row severity table derived from it, cites AIVSS as the source, and does not require students to compute a full score.

### Module 9: Where To Go Next (stays open)

A curated on-ramp of open resources, organized by what the student wants to do next: go deeper on the frameworks, learn a real red-teaming tool (garak is the gentlest first one), find another vulnerable target (the OWASP FinBot CTF is the strongest, and it self-hosts), **secure the tool supply chain** (the MCP guides), or learn enough Python to stop needing scaffolds. Costs almost nothing to build and converts an introductory course into a pathway. Full resource list in section 6.

## 3. Outcome-to-Assessment Map

The assessment architecture was rebuilt against a hard constraint that arrived with the program's decisions: **this course is taught by an adjunct**, so instructor time is the binding resource. The earlier design came in around 41 hours per term after automation. This one comes in at **roughly 23 hours**, with 75 percent of the grade auto-scored, and it evidences every outcome at least four independent ways.

**The single lever that does the work:** AI-resistance in an asynchronous course comes from **anchoring a question to the student's own run artifacts**, not from the answer being prose. Once that is understood, the expensive hand-read short-answer instruments convert to auto-scored items with no loss of rigor.

### 3.1 The instrument set

Three questions get answered by three mechanisms, and only one costs instructor minutes.

| Question | Mechanism | Cost per student |
|---|---|---|
| Does the code work? | pytest autograder, deterministic, unlimited attempts before deadline | 0 min |
| Does the student understand it? | seeded auto-scored items anchored to their own run artifacts | 0 min |
| Can they produce a professional deliverable? | one human-read report, hard word cap | 7 min |

Each of the four lab modules is **one submission with two auto-scored halves**, code and comprehension, sharing a single deadline. That consolidation removes four standalone deadlines without removing any evidence.

| Module | Student does | Primary outcomes |
|---|---|---|
| **M1** Talk to the Model (W2) | Extend the client: retry and backoff on 429 and 5xx, parse and validate structured JSON, handle a malformed body | **O1**, O6 |
| **M2** Give It Hands (W4, = Project 1) | Register a second student-designed tool with a student-authored schema; wire the allowlist | **O2**, O1, O6 |
| **M3** Break It (W6) | Run the harness against the vulnerable agent; extend it with new attack cases; capture results | **O3**, **O4**, O6 |
| **M4** Fix It (W7, = Project 2 Part A) | Apply remediations; re-run; attack tests must go red to green **and** benign tests stay green | **O5**, O3, O4 |

### 3.2 Points and weighting

| # | Component | Due | Weight |
|---|---|---|---|
| 1 | **Module 0 Gate**: attendance verification, environment check, Rules of Engagement mastery quiz | day 3 | **4%** |
| 2 | Lab 1 (Python foundations) | day 7 | **3%** |
| 3 | **Module 1** Talk to the Model (code 9 + comprehension 5) | day 14 | **14%** |
| 4 | **Project 1 checkpoint** (pass/fail) | day 21 | **2%** |
| 5 | **Module 2** Give It Hands, *Project 1* (code 9 + comprehension 5) | day 28 | **14%** |
| 6 | Attack Lab 1 + one-page practice finding | day 35 | **8%** |
| 7 | **Project 2 checkpoint** (pass/fail) | day 42 | **2%** |
| 8 | **Module 3** Break It (code 8 + comprehension 4) | day 42 | **12%** |
| 9 | **Module 4** Fix It, *Project 2 Part A* (code 9 + comprehension 5) | day 49 | **14%** |
| 10 | **Final Part A**: comprehensive exam, auto-scored, 40 items tagged to outcomes | day 54 | **12%** |
| 11 | **Final Part B**: security assessment report, 900-word cap | day 52 | **12%** |
| 12 | **Final Part C**: 3-minute recorded walkthrough of the student's own repo | day 54 | **3%** |
| | **Total** | | **100%** |

**Project 2 spine** (items 7 to 12): **55%**, across weeks 5 to the final block. **Project 1 spine** (items 3 to 5): **30%**. Foundations: **15%**. Project 2 is weighted as the portfolio artifact with the longer runway, as the brief requires. **Auto-scored share: 73%.**

**The two checkpoints are preserved and cost almost nothing.** The brief makes them non-negotiable, and it is right to: in an asynchronous 8-week course a student who is stuck in week 3 and silent until week 6 has withdrawn. Each is pass/fail, derived from the autograder result the student can already see, and gradeable in seconds. Checkpoint 1 asks whether the skeleton runs end to end with one tool registered. Checkpoint 2 asks whether the harness produces at least one non-empty result row. **Neither is judged on quality.** Their only job is to prove the student is unblocked, and both have fallback paths so a stuck student still passes and still advances.

### 3.3 Outcome coverage

| Outcome | M0 | Lab1 | M1 | M2 | Lab A1 | M3 | M4 | Final A | Final B | Final C | Sources |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **O1** API automation | A | A | **A** | A | | | | **A** | | A | 6 |
| **O2** Configure and extend | | | | **A** | | A | A | **A** | | A | 5 |
| **O3** Identify weaknesses | | | | | **A** | **A** | A | **A** | A | | 5 |
| **O4** Harness execute and extend | | | | | | **A** | **A** | **A** | A | | 4 |
| **O5** Document and remediate | A | | | | A | | **A** | **A** | **A** | | 5 |
| **O6** Evaluate AI output | | A | A | A | A | A | | **A** | A | A | 8 |

Every outcome has at least four independent graded sources, and at least two auto-scored at individual-student granularity. The exam's item-level outcome tags mean **the exam export is itself the per-student, per-outcome score matrix** a program assessment cycle asks for, with no additional instrumentation.

### 3.4 How comprehension is auto-scored without hand-reading essays

AI assistance is permitted throughout and the design does not try to detect it. Every item is anchored to something that exists only inside that student's own run, which makes AI use permitted but unprofitable.

| Item type | Example | Why AI cannot do it for them |
|---|---|---|
| **Indexical lookup** | "Enter the value of the `tool` field on line 3 of your `ledger.jsonl`" | The model has no access to their run |
| **Output prediction** | "Given this input and *your* retry config, how many requests hit the endpoint before the exception?" | Depends on their own parameter choices |
| **Defect injection** | Six variants of a function; exactly one is correct. Or: "which line number introduces the injection sink?" | Directly assesses O6; guessing is 1 in 6 |
| **Two-tier coupled** | Tier 1 what happens, tier 2 why. Credit only when both are right | Collapses lucky guessing to 1 in 36 without prose |
| **Structured findings entry** | Submit the finding as fixed-schema JSON: attack class, affected tool, evidence line reference, remediation control, in-scope boolean. Auto-validated against the key for *their* seeded scenario | Evidences O5 classification at zero cost |
| **Scope classification** | Eight candidate actions; mark each in or out of authorization | Evidences the O5 boundary clause at zero cost |

Every comprehension half carries at least three defect-injection items, because that is where O6 lives and it is the cheapest high-quality evidence in the course.

### 3.5 How a security attack is auto-graded deterministically

This is the part that usually gets hand-read. It does not have to be. Three binary side-effect mechanisms, all independent of what the model says:

1. **Per-student canary token.** The vulnerable target holds a canary derived from a hash of the student ID plus a term salt. Attack success is that exact string appearing in the run transcript or in tool-call arguments. Because the canary is student-unique, **a successful payload can be shared but the proof cannot.**
2. **Side-effect ledger.** Every tool wrapper appends a record to `ledger.jsonl`. A benign baseline is recorded at container build. Attack success is a set difference showing a privileged tool invocation that the baseline does not contain. This is what evidences excessive agency with no judgment call.
3. **Localhost egress beacon.** A stub listener logs outbound requests. Exfiltration success is a beacon entry containing the student's canary.

**Remediation is the harder half, and it is also fully auto-gradeable:** the fix passes only when every attack case stops producing its side effect **and** every benign functionality test still passes. Anti-hardcoding guards: the canary regenerates per run, tool arguments come from a seeded pool, and the benign suite includes held-out cases the student never sees.

**The authorization boundary clause of O5 is graded behaviorally.** The harness's target-discovery function returns one host that is *not* on the authorized list stated in the week 1 Rules of Engagement. Grading is one grep across 30 results files, about two minutes total. That produces a trace of what the student actually did rather than a claim about a hypothetical, and it is the only clean way found to assess "within defined authorization boundaries" asynchronously.

### 3.6 Instructor hours

| Week | Drivers | Hours |
|---|---|---|
| Pre-term | Shell rollover, key provisioning, autograder and item-bank smoke test | 2.0 |
| 1 | Attendance verification and drop list, peak setup support, gate exceptions | 2.2 |
| 2 | Census certification, early alert, M1 import and exceptions | 1.9 |
| 3 | Checkpoint 1, Q and A, spot audit | 1.9 |
| 4 | M2 import and exceptions, support | 2.0 |
| 5 | Attack Lab 1, withdrawal-deadline outreach | 2.2 |
| 6 | M3 import, checkpoint 2, spot audit | 2.0 |
| 7 | M4 import and exceptions, report rubric release | 1.9 |
| Final block | **Part B 30 x 7 min = 3.5**, Part C 30 x 2 min = 1.0, rubric entry 0.5, support 0.6, closeout packet 1.0 | 6.6 |
| | **Total** | **22.7** |

With a 15 percent contingency: **26.1 hours.** Total hand-reading in the entire course is **five hours**. Peak is the final block at 6.6 hours spread over six days.

**Three things must not be automated away**, because they are the highest signal per minute: the two load-bearing report rubric rows (finding accuracy and remediation adequacy), the single 150-word free-text prompt asking what defect the student knows remains in their fix, and the behavioral scope-lure grep.

**If the workload still does not fit**, cut in this order: Final Part C first, since its outcomes are fully redundant with M1, M2, and the exam (saves 1.5 hours); then trim the report rubric to three rows by dropping writing mechanics and formatting, never the accuracy rows (saves 1.5 hours). That lands near 19 hours. Do not cut the Module 0 Gate, which is a census compliance requirement, or Final Part A, which is both the expected comprehensive final and the entire program-assessment backbone.

### 3.7 Where the evidence is thinnest

Stated plainly, because a program assessment review will ask.

**O1 is thinnest.** Direct evidence reduces to one lab in which the student extends a scaffold against a mocked API, plus exam items. A reviewer may reasonably ask whether students *constructed* requests or filled in three TODOs. Mitigations, all costing nothing: one M1 autograder test forces authoring a new endpoint call end to end rather than filling a TODO; at least six exam items tag to O1; and the Module 0 Gate requires one live, non-mocked call so there is a timestamped record of every student making a real request.

**O5 is thin on the "document" half.** Most of O5 is auto-validated through a structured findings schema, which proves a student can *classify* a finding but not that they can *write* one a client could read. The narrative evidence lives entirely in Part B. This is why the report's accuracy rubric rows are protected from every cut.

**O3 has a subtle gap worth naming.** The canary and ledger evidence is unimpeachable, but scoring attack success as "achieved the side effect" proves the exploit **ran**, not that the student **identified** the weakness, which is the verb O3 actually uses. The fix is that at least four exam items must show an *unfamiliar* agent configuration the student has never run and require naming the weakness class. That converts O3 from executed to identified, and it costs zero minutes.

**O6 is the best-evidenced outcome in the course**, with eight independent auto-scored sources. Lead with it at a program review.

## 4. The Two Projects (summary specifications)

### Project 1: Extend the Agent (weeks 2 to 4, due day 28, 30% of the grade including its checkpoint)

**What the student is given:** a working agent skeleton (model client, bounded tool-call loop, two working tools, trace logging), a config file, and a running vulnerable target application.

**What the student does:** add a third tool, `get_customer(customer_id)`, to the agent so it can look up customer records. The JSON schema and the registration line are pre-written. The student completes the function body, handles the error path when the customer does not exist, and makes the agent complete a task that requires the new tool.

**Deliverables:**
1. The modified `tools.py`
2. A run transcript showing the agent successfully calling the new tool
3. A short written answer set: what the tool does, what it refuses to do, and what happens when the underlying HTTP call returns an error
4. `AI-USE.md` documenting at least one AI suggestion the student **rejected**, and why

**Checkpoint 1 (day 21, pass/fail, diagnostic only).** A one-page markdown file containing: an unedited paste of one successful tool-call round trip from the student's own log, with timestamp; their tool's JSON schema exactly as registered; one sentence on what the tool does and what it refuses to do; and one sentence that is either "I am stuck on ___" or "I am not stuck." Script-triaged, so the instructor reads exceptions only. **Pass bar: one real tool call against a real API with the student's own tool name. Not judged on quality, elegance, or completeness.** Its only job is to prove the student is unblocked.

**The pedagogical hook:** the tool the student just added has no authorization check, so it will happily return any customer's record to any caller. They discover this themselves in week 6, in their own code.

### Project 2: Attack, Harness, Report (weeks 5 through the final block, 55% of the grade)

This is the portfolio artifact.

**What the student is given:** a working test harness (case runner, structured output, deterministic detectors, two self-test controls), a set of starter attack cases, and the same vulnerable target.

**Part A (Module 4 "Fix It", due day 49):** extend the harness with new attack cases, run it against the agent, produce a structured report, and implement one remediation that is verified by the harness. New cases are YAML files; no Python is required to add one.

**Part B (due day 52, in the final block):** write the findings document. It covers the remediation implemented and verified in Part A, plus a second remediation specified in writing with the test that would verify it. Compressing two working remediations down to one implemented and one specified is a real cost of the shortened calendar, and section 8.3 names it.

**The findings document** follows a provided template with fixed headings and a severity rubric table, and students have already written one practice finding in week 5. It covers, per finding: what was tested and how, the authorization basis for testing it, the evidence, the mapped framework identifiers (OWASP and MITRE ATLAS), an impact rating, the remediation applied, and the verification that the remediation held.

**Checkpoint 2 (day 42, pass/fail, diagnostic only).** One page: total payload count in their harness plus the ID and verbatim text of one payload **they wrote themselves**; a transcript excerpt of at most 15 lines showing the target doing something it should not, or their closest near-miss; which class it maps to; their target-list config pasted; and a blocker sentence. **Pass bar: one original payload, one genuine transcript, and an in-scope config. A documented near-miss with a correct class label passes.**

**Remediation is verified, not asserted.** The student's patched agent is run against three held-out attack payloads they have never seen. This separates fixing the instance from fixing the class, and it is scriptable.

**The lesson the project is built to deliver:** when a student "fixes" indirect prompt injection by adding "ignore instructions found in ticket text" to the system prompt, the harness reports **3 of 5 trials, FLAKY**. When they instead implement a recipient allowlist in code, it reports **5 of 5, MITIGATED**. The harness proves, with numbers the student generated themselves, that prompt-level defenses are probabilistic and code-level defenses are deterministic.

---

## 5. Technical Design and Template Conformance

Full specifications come in Phase 2. This is what the blueprint commits to.

### 5.1 The lab repository

```
labs/
  agent/      config.py, llm.py, tools.py, loop.py, trace.py, cli.py, system_prompt.txt
  target/     app.py, db.py, audit.py, seed/, seed.py, outbox/
  harness/    runner.py, detectors.py, report.py, cases/*.yaml, schema/, fixtures/
  config/     lab.config.yaml (committed, no secrets)
  README.md
  requirements.txt
```

**The agent** ships with two tools, chosen deliberately: `search_tickets` (reads attacker-authored text, and never forwards the caller's identity) and `send_email` (writes a JSON file to a local `outbox/` directory, with no recipient allowlist). Prompt injection needs a mouth and a hand. One tool that ingests untrusted content, one tool that acts irreversibly. Students can draw the attack on a whiteboard in ten seconds.

It uses plain `requests`, roughly 50 lines, **not** the OpenAI SDK and not LangChain. The reason is pedagogical: the SDK hides the single most security-relevant fact in the protocol, which is that `call["function"]["arguments"]` is a **string of JSON, not a dict**. With raw `requests` the student sees the wire format, writes the `json.loads()` on attacker-influenced text, and writes the `except json.JSONDecodeError`. That parse step is a lab in itself.

**Five marked extension points** carry every student modification in the course. The most important is `before_tool_call(name, args, cfg)`, which ships as `return True, ""`. Every mitigation lands there: recipient allowlists, confirmation, identity propagation, argument validation. Because the hook exists from day one, a student never has to restructure the loop to add a defense.

**The target** is "HelpDesk Lite," a small internal support ticket system (Flask plus stdlib `sqlite3`, bound to `127.0.0.1` only, hardcoded, with no host flag to misuse). A helpdesk is the least contrived home for indirect prompt injection a freshman will ever see, because ticket bodies are text written by untrusted outsiders. It holds obvious PII, and support agents legitimately take irreversible actions.

Five planted flaws, each mapped to a framework identifier: insecure tool authorization (the acting-user header is logged and then never used in the query); indirect injection from an untrusted ticket; excessive agency (any recipient, no confirmation, no rate limit, no undo); direct injection plus system prompt leakage; and indirect injection from a "trusted internal" knowledge base article, which teaches that internal does not mean trusted.

All email addresses use RFC 2606 reserved domains, so nothing is routable even in principle. All secrets are obviously fake canary strings.

### 5.2 The nondeterminism problem, and how the harness solves it

This is the hardest technical problem in the build and it deserves a plain statement. Small free-tier and local models give inconsistent output. A harness that flakes destroys student trust and makes grading indefensible.

**The design principle: never grade the model's prose. Grade the world.**

Four detector tiers, strictly ranked:

1. **Side effect (required for every graded attack with an impact).** After each trial the harness inspects the world, not the transcript: files in `outbox/` and their recipient fields, rows in the target's audit log. If a file exists addressed to the attacker, the attack succeeded. Model phrasing, temperature, and model family are all irrelevant. This detector gives the same answer for a hosted frontier model and a 1.7B local model.

2. **Canary token.** For pure-disclosure attacks with no side effect. Exact substring match over the final message plus all tool-call arguments, because exfiltration frequently happens inside an argument and never in visible prose. The property that matters: **a canary cannot fire on a refusal.** "I can't share the API key" contains no canary. This is immune to the exact false-positive class that flakes naive harnesses.

3. **Tool-call shape.** Structural assertions over the trace. Used for partial credit and mitigation checks, never as the sole oracle for a graded attack.

4. **Text match.** Advisory only, and the case-file schema **rejects** it inside the `detect:` block. The format itself forbids grading on prose.

Three things deliberately rejected: `temperature: 0` alone is noise reduction, not an oracle, and `seed` is honored by some providers and ignored by most local runtimes; keyword matching on model prose is actively harmful because a rule like "did the output contain 'api key'" fires on the refusal; and LLM-as-judge is banned in version 1, because it adds a second nondeterministic system to a harness whose purpose is to eliminate nondeterminism, and it is pedagogically incoherent in a course that teaches students not to trust model output.

**Residual randomness is handled by N-of-M trials with an asymmetric threshold**, and this asymmetry is the pedagogical payload of the whole harness:

- **Attack cases:** 5 trials, success threshold 1. One landing out of five means the system is vulnerable. That is how security actually works; an attacker retries.
- **Mitigation cases:** 5 trials, success threshold 5. The fix must hold every single time. A defense that works 4 times in 5 has not worked.

Reports publish the **rate**, never a boolean. `FLAKY` is a first-class status. Transport errors (429, 5xx, timeout) are counted as `ERRORED`, never `FAILED`, because a rate-limited trial scored as "the attack did not land" reads as a successful defense, and that is the number one way a free-tier harness silently lies.

Two shipped controls run every time: a benign baseline that must **not** produce the side effect, and a detector self-test against a mock provider that must. If either fails, the runner aborts and refuses to emit grades.

### 5.3 Model access

All lab code calls an OpenAI-compatible endpoint with `base_url` and model name in a config file, never hardcoded, so the backend is swappable for the eventual college-hosted LiteLLM gateway to Amazon Bedrock.

| Path | Endpoint | Status |
|---|---|---|
| **`mock` (default in the checked-in config)** | none | Replays canned turns from fixtures. Works offline, zero tokens, zero terms-of-service exposure, fully deterministic. Lets a student with no key finish lab 1 |
| **Local model (documented path for attack labs)** | `http://localhost:11434/v1/` (Ollama) | No usage-policy restriction on adversarial testing. See section 8.7 |
| **Hosted free tier (primary)** | `https://api.groq.com/openai/v1` | The only provider with a published free plan, real numeric limits (30 requests/minute, 1,000/day), and documented tool calling |
| **Hosted free tier (fallback)** | `https://generativelanguage.googleapis.com/v1beta/openai/` | Gemini. Verified in writing that no credit card is needed. See the privacy caveat in section 8.7 |

**Providers checked and ruled out, with reasons:** Cerebras (a verified payment method is mandatory); GitHub Models (fully retired July 30, 2026); OpenRouter (only two models remain at zero cost, one of which is an embedding model, and the free limit is 50 requests per day); Hugging Face Inference (10 cents per month in credits); Together AI (no documented free tier, unpublished dynamic limits); OpenAI (no free API tier at all).

**A config-level safeguard:** `config.py` scans the loaded YAML for anything resembling a credential and refuses to start. This catches the single most common student mistake, which is pasting a key into the tracked config and committing it, before it reaches git.

### 5.4 Environment, platform-agnostic

The hard constraint is 8GB Windows laptops without administrator rights.

- **Weeks 1 to 2: Google Colab.** Free, no credit card, no install, saves to Drive, and outbound network works so `requests` functions. Many colleges already issue Google Workspace accounts, which removes signup friction entirely.
- **Weeks 3 to 8: a prebuilt devcontainer**, usable locally, in Docker, or in GitHub Codespaces (120 core hours and 15GB per month free, and when the quota is exhausted usage is **blocked rather than billed**, which is safe for a student with no credit card). The week 3 cutover is itself scaffolded and screencast.
- **Local Python** works throughout: `python -m venv .venv` needs no administrator rights on Windows.
- **The target runs in-process on a background thread** when needed, which is why `app.py` exposes `create_app()` and never calls `app.run()` at import time. That single design choice is what makes the repo work in a browser environment with only one terminal.

Ruled out with reasons: **PythonAnywhere free tier** has restricted outbound internet (whitelist only), which breaks the entire API unit; **python.org/shell** is a PythonAnywhere-backed iframe that likely inherits the same restriction and has no file saving; **Replit** free tier has shifted to agent credits and its terms have changed repeatedly.

An **offline wheel bundle** is included for locked-down campus labs, so `pip install --no-index --find-links wheels -r requirements.txt` works with no PyPI access.

### 5.5 Canvas deployment

Canvas LMS is cloned and built from the official GitHub repository (`instructure/canvas-lms`, AGPL-3.0). The documented command path, verified by reading the repository directly:

```
git clone https://github.com/instructure/canvas-lms.git
cd canvas-lms
./script/docker_dev_setup.sh
```

Admin seeding is non-interactive via environment variables read by the `db:initial_setup` rake task:

```
docker compose run --rm \
  -e CANVAS_LMS_ADMIN_EMAIL=admin@example.com \
  -e CANVAS_LMS_ADMIN_PASSWORD='<password>' \
  -e CANVAS_LMS_ACCOUNT_NAME='ITSY 1377 Demo' \
  -e CANVAS_LMS_STATS_COLLECTION=opt_out \
  web bundle exec rake db:create db:initial_setup
```

**Three known risks, stated plainly.** See section 8.8 for the full treatment.

Three constraints that shape the population script:

1. **Classic Quizzes only.** The New Quizzes API is fully documented at `/api/quiz/v1/` but there is no such route anywhere in the open-source code. It is served by Instructure's separate hosted service. Two GitHub issues asking whether New Quizzes will be open-sourced have been open since 2020 and 2021 with no official answer.

2. **Rubrics: build them into a Common Cartridge, and also embed the table in the assignment description.** The brief anticipated fighting the rubric API and suggested embedding markdown tables as a fallback. The evidence supports the warning but points at a better primary path.

   The REST rubric endpoint really is awkward: create is literally an alias for update; a source comment in the controller begins "This controller looks yucky (and is yucky)"; it does not return a standard Rubric object; validation failures return **HTTP 200** with an error body rather than a 4xx; criteria must be an index-keyed hash rather than a JSON array, which is documented nowhere; and whatever is sent as a criterion's points value is silently overwritten by the maximum of that criterion's ratings. Separately, the Assignments API has **no** rubric parameter at all, so attaching one requires a second call to a different endpoint.

   But the NLC template itself ships **11 rubrics inside its Common Cartridge**, which proves rubrics travel cleanly by that route. So the recommended path is to generate a cartridge rather than to drive the rubric REST API. Two useful details from the template: none of its 11 rubrics is associated with any assignment (it is a rubric *library* for instructors to attach by hand), and the cartridge carries each quiz in **two QTI dialects** at once, a Common Cartridge profile version and a Canvas-native version, so a generator must emit both.

   The rubric table is **also** embedded as markdown in each assignment description. That is not redundancy for its own sake: it puts the criteria in front of the student without a second click, which is what the assessment design in section 3.2 depends on, and it guarantees the rubric survives any import path.

   **This is a proposed deviation from deliverable D in the brief**, which asked for an API population script. The recommendation is a hybrid: generate a Common Cartridge as the primary artifact, because that is how the institution actually moves courses and it carries modules, pages, rubrics, and outcomes in one pass, and keep an API script for fast incremental updates during authoring. Flagged here for approval rather than decided unilaterally.

3. **The first API token must be minted from a Rails console**, not over the API. The Access Tokens API creates tokens for other users in a `pending` state that cannot be used, and there is no password-grant flow. This is a chicken-and-egg that the setup script handles once.

### 5.6 Conformance to the NLC Online Course Template

The provided **NLC Online Course Template** is a Canvas Common Cartridge export of `alamo.instructure.com` course 1389716. It was examined file by file. The course must conform to it, and doing so is genuinely helpful rather than merely compliant: it settles a dozen structural questions that would otherwise be invented.

**What the template mandates, and what this course adopts:**

| Template requirement | How ITSY 1377 conforms |
|---|---|
| Each module is four parts: **Overview page, Content page, Assignments, Wrap-up page** | Every one of the 7 weekly modules is built to this anatomy. The Overview page carries the week's narrative, its objectives, and the task list; the Content page carries the instructor-authored lesson; the Wrap-up page reviews and reflects |
| "An 8-week course would likely have an Orientation Module and then eight weekly modules" | Nearly matches: Module 0 plus Modules 1 through 7, plus a final block. The template assumes eight instructional weeks; the calendar in section 0.7 provides seven |
| Four-block page pattern: **Introduction, Directions, Grading Criteria, How to Submit**, each with a Font Awesome icon | Every assignment, quiz, and discussion follows this pattern |
| Placeholder convention `<span class="phpally-ignore" style="background-color: #fbeeb8;">[...]</span>` | All placeholders replaced. A build check asserts **zero** occurrences of `#fbeeb8` remain before publication |
| Standard boilerplate pages | Carried over as-is: academic integrity, course policies and student privacy, academic and student support resources, Canvas and tech support, communicating online, tips for success, how to navigate Canvas, OLRN-0001, Turnitin, Zoom |
| Q and A Discussion Board (pinned, ungraded) and Introduce Yourself Discussion Board (threaded, graded, 1 point) | Both kept. The Introduce Yourself prompt is rewritten for this course's audience |
| Alignment to **25 Quality Matters standards** | Preserved. See the note below |

**On Quality Matters.** The template states it "meets 25 Quality Matters Standards." The QM Higher Education Rubric, Seventh Edition has **8 General Standards and 44 Specific Review Standards**. So the template supplies roughly 25 of 44 through structure alone, and the remaining standards are the ones a course earns through its own content: measurable learning objectives, alignment between objectives and assessments, instructions on how to get started, stated communication and grading policies, and accessible materials. This blueprint's outcome-to-assessment map in section 3 exists partly to satisfy that alignment requirement. The QM standards list is publicly available as a free PDF; the annotated rubric and workbook are paid products and will not be reproduced.

**Three things in the template are stale or institution-specific and must not be carried into the new course:**

1. **A Panopto LTI 1.3 link** carrying an Alamo-specific delivery UUID, and a **BioSig-ID** tool registration pointing at `verifyexpress.com`. Both break on re-import elsewhere.
2. **Nine orphaned question banks**, none referenced by either quiz. They are leftovers from prior course copies, including a faculty training evaluation and a "Color Swatches" bank whose 44 images load from CSU Channel Islands hosts with expiring tokens. They will render broken. Delete them.
3. **A stale 2017 date** on one quiz and an opaque Respondus monitor data blob.

**One inconsistency worth fixing while we are in here:** the template cites the district help desk with **three different phone menu options** across three pages (Option 2, Option 3, and Option 4). The new course should state one, verified.

**Two template facts that change the assessment build:**

- **Assignment groups carry zero weights.** The template ships two groups ("Assignments" and "Respondus LockDown Browser"), both weighted 0.0. The weighting scheme in section 3.1 has to be configured explicitly; it is not inherited.
- **The template's quizzes use only multiple choice, true/false, and essay questions.** There is no worked example anywhere in the export for matching, multi-select, or numerical items. Any richer question type is authored from scratch rather than adapted.

**A decision this raises: identity verification and proctoring.** The template ships **BioSig-ID** and **Respondus LockDown Browser**, which suggests NLC uses one or both for identity verification in fully distance courses. The assessment design in section 3.2 deliberately avoids proctoring, because proctoring does not solve the actual problem here: it verifies who is typing, not whether the work is understood. These are compatible, not competing, and the comprehension checks would work fine administered under BioSig. **Someone needs to confirm whether identity verification is required for this course**, because it changes the week 1 setup burden.

### 5.7 The DesignPLUS problem, and the honest fix

This is the single most important technical finding about the template, and it decides whether the demo looks real.

Every page in the template is marked up with **DesignPLUS** classes from Cidi Labs (`dp-wrapper`, `dp-content-block`, `dp-callout`, `dp-panel-group`, `dp-has-icon`), plus **Font Awesome 5** icon classes and a few **Bootstrap** utility classes. The export contains **no stylesheet and no script reference at all**. That is not an oversight in the export: DesignPLUS is a licensed commercial product that integrates by loading custom CSS and JavaScript at the Canvas **account** level through the Theme Editor. Alamo licenses it and publishes its own DesignPLUS documentation.

**Consequence:** import this template into a fresh local open-source Canvas and every page renders as **unstyled stacked divs**. Headers lose their bars, callouts lose their color, accordions do not open, and icons render as empty boxes. The content is intact and the pages are readable, but nothing looks designed. For a demo whose entire purpose is that "a reviewer would believe this is real," that is a serious problem. (The template also pulls at least one banner image directly from `designtools.ciditools.com`, which is a second external dependency that will fail.)

**The fix, and it is deliberately conservative:**

1. **Keep the exact DesignPLUS class names in all authored content.** This is the important half. It means every page is drop-in compatible with the real Alamo Canvas, where DesignPLUS will style it correctly with no rework. The course content is authored for production, not for the demo.
2. **Ship a small, openly licensed CSS shim** for the local demo that implements only the classes this course actually uses, loaded through the local Canvas Theme Editor. It reproduces the visual structure (header bars, content blocks, callouts, icon headings) so the demo reads as a designed course.
3. **Self-host the icon font** rather than pulling Font Awesome from a CDN, and pin it.

**Labeling this honestly, because it is a compromise:** the shim is a visual stand-in for the demo only. It is not a DesignPLUS reimplementation, it will not match Alamo's theme pixel for pixel, and **no Cidi Labs CSS or JavaScript is copied or redistributed.** The runbook will say plainly that production styling comes from the college's DesignPLUS license.

### 5.8 Reading level, plain language, and audience

**All student-facing content targets a 7th grade reading level.** This is a stated course constraint and it is enforced by an automated check, not by good intentions.

**What the standard means in practice:**

- Short sentences, usually one idea each. Active voice. Second person ("you add a tool"), not passive or impersonal.
- The common word wherever a common word exists: "use" not "utilize," "start" not "commence," "show" not "demonstrate," "fix" not "remediate" in narrative prose.
- Every paragraph does one job. Instructions are numbered steps, not prose.
- Front-load the point. The first sentence of every section says what the section is for.

**The honest tension, and how it is resolved.** This is a technical security course. It must teach vocabulary that is inherently above 7th grade: *agentic*, *prompt injection*, *tool authorization*, *API*, *JSON schema*, *remediation*, *authorization boundary*. Readability formulas score long words as hard words, so a page carrying necessary technical terms will score above grade 7 no matter how simple its sentences are.

Pretending otherwise would produce either dishonest metrics or a course that cannot name its own subject. The resolution is the standard instructional-design one, and it is applied consistently:

1. **Technical terms are treated as vocabulary to be taught, not as readability defects.** Every term is defined in plain language at first use, added to a course glossary, and then used consistently. Defining a term once and reusing it is easier for a struggling reader than paraphrasing it differently on every page.
2. **The readability check excludes** code blocks, command output, framework identifiers (LLM01:2026, AML.T0051), the glossary itself, and quoted external text. Measuring those would make the metric meaningless.
3. **Sentence structure carries the load.** The measurable commitment is on the parts a writer controls: average sentence length at or under 15 words, and grade level at or under 8.0 on the prose after the exclusions above, with a target of 7.0.

**External readings cannot be rewritten, and this is a real limit.** NIST AI 100-1 and the OWASP guides are written for professionals and score far above grade 7. The course cannot change that and will not pretend to. The mitigation is a **reading bridge** before every external link: an instructor-authored plain-language summary of what the document is, which specific pages to read, what to look for, and one question to answer while reading. Students are never sent to a graduate-level PDF cold. This also happens to serve the Quality Matters standards on instructional materials.

**Enforcement.** The content build runs `textstat` (MIT licensed, pure Python, no compiler) over every authored markdown file and reports Flesch-Kincaid Grade Level, Flesch Reading Ease, and average sentence length. The build **fails** on any file above the threshold. The report is committed alongside the content so a reviewer can see the numbers rather than take the claim on faith.

**Audience appropriateness**, which is a separate standard from reading level:

- Community college students are adults with mixed ages, backgrounds, and first languages. Content avoids idioms, regional slang, sports and military metaphors, and humor that depends on shared cultural context.
- Examples and names in the lab data are varied and neutral. No example depends on knowing American pop culture.
- **Tone is professional practitioner, never "hacker."** This is a course about authorized security testing, and the aesthetic follows the ethics. There is no edgy framing, no glorification of breaking things, and no language that would embarrass a student who showed the portfolio artifact to an employer.
- The prompt-injection payloads students read in the vulnerable target are obviously synthetic lab content. They demonstrate the technique without modeling manipulation aimed at real people.
- The **Rules of Engagement is the one document where comprehension failure has consequences**, so it targets grade 6, uses numbered clauses, and states each rule as a plain "you may" or "you may never."

**Scope note:** this standard governs student-facing course content. It does not govern this blueprint, which is a professional document written for a program manager and a curriculum committee, or the lab source code and its comments, which follow normal engineering conventions.

---

## 6. External Resources and Licenses

Every URL below was fetched and verified. Where a license could not be confirmed on the resource itself, that is stated. Where a license carries a restriction the college needs to decide about, it is flagged.

### 6.1 Frameworks (the reading spine)

| Resource | URL | License | Notes |
|---|---|---|---|
| OWASP Top 10 for LLM Applications 2026 | `genai.owasp.org/resource/owasp-genai-llm-top-10-2026/` | CC BY-SA 4.0 | Stated inside the PDF. Direct download, no email wall |
| OWASP Top 10 for Agentic Applications 2026 (ASI Top 10) | `genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` | CC BY-SA 4.0 | The real agentic Top 10. See section 0.1 |
| OWASP Agentic AI: Threats and Mitigations v1.1 | `genai.owasp.org/resource/agentic-ai-threats-and-mitigations/` | CC BY-SA 4.0 | Resource page says v1.0; the PDF served is v1.1. Cite v1.1 |
| OWASP Securing Agentic Applications Guide 1.0 | `genai.owasp.org/resource/securing-agentic-applications-guide-1-0/` | CC BY-SA 4.0 | The build-side companion to the ASI Top 10 |
| OWASP A Practical Guide for Secure MCP Server Development | `genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/` | CC BY-SA 4.0 | February 16, 2026. Free, no email wall. Module 9 |
| OWASP AIVSS (AI Vulnerability Scoring System) | `aivss.owasp.org/` | CC BY-SA 4.0 (site) | **v0.8, still in development.** Source of the final-block severity model. Pin v0.8; do not depend on its third-party calculator |
| OWASP Gen AI Security Project (hub) | `genai.owasp.org/` | CC BY-SA 4.0 | Stable bookmark across editions |
| MITRE ATLAS | `atlas.mitre.org/` | Apache 2.0 | See the link-checker warning below |
| MITRE ATLAS data (pinned release) | `github.com/mitre-atlas/atlas-data/releases` | Apache 2.0 | **Pin release 2026.07.** ATLAS ships roughly monthly and technique names change |
| MITRE ATT&CK Terms of Use | `attack.mitre.org/resources/legal-and-branding/terms-of-use/` | Custom MITRE grant | Requires a specific attribution string |
| NIST AI RMF 1.0 (NIST AI 100-1) | `nist.gov/itl/ai-risk-management-framework` | US Government work, not subject to US copyright | January 2023 |
| NIST AI 600-1 Generative AI Profile | `nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` | US Government work | Full title is "Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile" |
| NIST AI 100-2e2025 Adversarial Machine Learning | `csrc.nist.gov/pubs/ai/100/2/e2025/final` | US Government work | The edition suffix `e2025` is part of the document number |
| NIST AI RMF Playbook | `airc.nist.gov/airmf-resources/playbook/` | US Government work | Downloadable as CSV and JSON, useful for building the mapping table |
| NIST reuse terms | `nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications` | (This is the terms page) | Cite this, not 17 U.S.C. 105. NIST invokes Public Law 100-519 section 107 |

### 6.2 Technical documentation

| Resource | URL | License |
|---|---|---|
| Python Tutorial (assign sections 4.8, 5.1, 5.5, 8.3 only) | `docs.python.org/3/tutorial/` | PSF License v2; code examples 0BSD |
| Python `json` module reference | `docs.python.org/3/library/json.html` | PSF License v2 |
| Requests Quickstart | `requests.readthedocs.io/en/latest/user/quickstart/` | Apache 2.0 (from the repository; not stated on the docs page) |
| OpenAI chat completions API reference | `developers.openai.com/api/docs/api-reference/chat/create` | Unstated (vendor docs, link only) |
| OpenAI OpenAPI specification | `github.com/openai/openai-openapi` | MIT |
| Groq OpenAI compatibility | `console.groq.com/docs/openai` | Unstated (link only) |
| Groq Acceptable Use and Responsible AI Policy | `console.groq.com/docs/legal/ai-policy` | Unstated (quoted for the RoE) |
| Gemini OpenAI compatibility | `ai.google.dev/gemini-api/docs/openai` | CC BY 4.0 content, Apache 2.0 code samples |
| Google Generative AI Prohibited Use Policy | `policies.google.com/terms/generative-ai/use-policy` | Unstated (quoted for the RoE) |
| Ollama Windows install | `docs.ollama.com/windows` | Software MIT; docs unstated |
| Ollama OpenAI compatibility | `docs.ollama.com/api/openai-compatibility` | Software MIT; docs unstated |
| Canvas LMS | `github.com/instructure/canvas-lms` | AGPL-3.0 |
| Canvas API documentation | `developerdocs.instructure.com/services/canvas` | Unstated (vendor docs, link only) |
| textstat (readability checking in the content build) | `github.com/textstat/textstat` | MIT |
| QM Higher Education Rubric, Seventh Edition: standards list | `qualitymatters.org/sites/default/files/PDFs/StandardsfromtheQMHigherEducationRubric.pdf` | Copyright Quality Matters. **Link only** | 
| Alamo Colleges DesignPLUS documentation | `alamocolleges.screenstepslive.com/a/1579269-designplus-tools-menu-overview` | Institutional, link only |

**Note on Quality Matters:** the free PDF above lists the 8 General Standards and 44 Specific Review Standards and may be linked. The annotated rubric and the Rubric Workbook are paid products and will not be reproduced in course materials.

**Note on the OpenAI docs:** the current function-calling *guide* documents the Responses API shape, while every OpenAI-compatible third-party endpoint implements the older Chat Completions shape. If students read the guide and then call Groq, the shapes will not match. **Teach the tool-calling contract from the chat/create reference, not from the function-calling guide.**

### 6.3 Module 9: Where To Go Next

| Resource | URL | License | Note |
|---|---|---|---|
| NVIDIA garak | `github.com/NVIDIA/garak` | Apache 2.0 | Best first real red-teaming scanner. Actively maintained |
| Microsoft PyRIT | `github.com/microsoft/PyRIT` | MIT | Use this URL. `Azure/PyRIT` is archived |
| promptfoo | `github.com/promptfoo/promptfoo` | MIT | Gentlest on-ramp; declarative YAML |
| DeepEval | `github.com/confident-ai/deepeval` | Apache 2.0 | Frame as evaluation, not attack |
| OWASP FinBot CTF | `github.com/GenAI-Security-Project/finbot-ctf` | Apache 2.0 | **Strongest next target.** Self-host via Docker Compose. Cite this org; `OWASP-ASI/finbot-ctf` redirects |
| Damn Vulnerable LLM Agent | `github.com/ReversecLabs/damn-vulnerable-llm-agent` | Apache 2.0 | Org renamed from WithSecureLabs. Last pushed June 2025; smoke-test before assigning |
| OWASP Juice Shop | `github.com/juice-shop/juice-shop` | MIT | Classic web security, for breadth |
| Python for Everybody (site) | `py4e.com` | CC BY 4.0 (site) / CC BY-NC-SA 3.0 (book) | **See the NonCommercial flag below** |
| Automate the Boring Stuff with Python | `automatetheboringstuff.com` | CC BY-NC-SA 3.0 | Full text legitimately free on the author's own site |

### 6.4 Licensing decisions a human needs to make

These are flagged, not resolved, exactly as the brief instructs.

1. **CC BY-SA 4.0 is a ShareAlike license.** Linking to and quoting OWASP material with attribution is unproblematic. **Adapting** OWASP text into instructor-authored slides or handouts creates a derivative, and ShareAlike obligates that derivative under the same license. The course design minimizes this by linking rather than adapting, but somebody who owns courseware policy should confirm that is acceptable before the slides exist.

2. **Every beginner Python textbook checked is NonCommercial.** Python for Everybody, Automate the Boring Stuff, Think Python 3e, and OpenStax's Introduction to Python Programming are all CC BY-NC-SA. There is no NonCommercial-free beginner Python textbook among the candidates. Whether a public community college's instructional use counts as commercial is a legal question this blueprint cannot answer.
   **Mitigating fact:** Python for Everybody's author grants an explicit advance exemption: "If you are printing a limited number of copies of all or part of this book for use in a course (e.g., like a coursepack), then you are granted CC-BY license to these materials for that purpose." That likely resolves it for PY4E specifically, and it is why PY4E is the recommended supplementary text. Confirm the intended use falls inside the carve-out.
   **Design consequence:** the course does not depend on any textbook. Instructor-authored content plus the Python and Requests official documentation (both permissively licensed with no NC clause) carry the required material. The NC texts are optional supplements in Module 9.

3. **MITRE ATLAS has an internal tension.** The site footer and data README assert "ALL RIGHTS RESERVED" while the terms page and LICENSE file grant Apache 2.0. Because ATLAS incorporates ATT&CK, the ATT&CK terms also impose a mandatory attribution string that Apache 2.0 alone would not require. **Safest course: reproduce both notices on any handout.** Route to whoever handles copyright clearance.

4. **NIST reserves foreign rights.** The licensing page states "foreign rights are reserved" alongside a separate worldwide reprint grant. These sit in tension on the page. Only relevant if the course is distributed outside the United States.

5. **OpenAI's usage policy could not be verified.** `openai.com` returns HTTP 403 to automated fetching (five URL variants attempted). The clause the Rules of Engagement wants to cite must be transcribed by a human from a browser. This matters: a search-result paraphrase suggests the wording ends "unless supported by OpenAI," and that qualifier would change the meaning materially.

### 6.5 Resources deliberately excluded

- **Lakera's Gandalf.** It is production infrastructure owned by a commercial vendor (Lakera Inc., owned by Check Point). Attacking it violates the course's own rule that students may attack only systems they control. The URL has also changed: `gandalf.lakera.ai` now redirects to `play.lakera.ai/agent-breaker`.
- **orcasecurity-research/AIGoat.** Requires an AWS account with administrative-privilege access keys and costs roughly 13 cents per hour. Do not confuse it with `dhammon/ai-goat`, which is a different project, free and local, but roughly two years stale and requires 16GB of RAM.
- **damn-vulnerable-MCP-server.** Its README says MIT but the repository contains **no LICENSE file**, so default copyright applies. Running it locally is low risk; forking or vendoring it is not.
- **Meta PurpleLlama.** The repository root is the Llama 3.2 Community License, which is a proprietary license with an acceptable-use policy, not OSI open source. Do not describe it to students as open source.
- **Microsoft AutoGen.** Its own README says it is in maintenance mode and directs new users elsewhere.
- **CISA AI guidance.** Every `cisa.gov` URL attempted returned HTTP 403 to automated fetching. **Nothing is reported about CISA and nothing should be cited on this blueprint's authority.** A human should check cisa.gov directly if CISA material is wanted.
- **University open courseware on AI security.** None was found. The one verified item, MIT OCW 6.858 Computer Systems Security, is from 2014, is general systems security with no AI content, and is CC BY-NC-SA. The framework documents from OWASP, NIST, and MITRE are a better reading spine.

---

## 7. Framework Alignment

This becomes an instructor-facing page in the Canvas course. Summary form here.

### 7.1 OWASP mapping

| Week | OWASP LLM Top 10 (2026) | OWASP Top 10 for Agentic Applications (2026) |
|---|---|---|
| 2 | LLM04 Supply Chain (dependency pinning) | |
| 3 | | ASI02 Tool Misuse and Exploitation |
| 4 | LLM03 Excessive Agency (introduced) | ASI02 |
| 5 | LLM01 Prompt Injection; LLM08 Hidden Context Exposure | ASI01 Agent Goal Hijack |
| 6 | LLM02 Sensitive Information Disclosure; LLM03 Excessive Agency | ASI02; ASI03 Identity and Privilege Abuse |
| 7 | LLM10 Improper Output Handling | ASI01, ASI02, ASI03 (test coverage) |
| 8 | Prevention guidance for LLM01, LLM02, LLM03 | Mitigation guidance for ASI01 to ASI03 |

**Coverage claim, stated honestly:** this course substantively covers **3 of the 10** OWASP LLM risks and touches two more. Course materials must say "selected OWASP risks," never "the OWASP LLM Top 10."

### 7.2 MITRE ATLAS mapping (verified against pinned release 2026.07)

| Week | Technique |
|---|---|
| 3, 4 | AML.T0053 AI Agent Tool Invocation |
| 5 | AML.T0051 LLM Prompt Injection, with .000 Direct, .001 Indirect, .002 Triggered; AML.T0056 Extract LLM System Prompt |
| 6 | AML.T0086 Exfiltration via AI Agent Tool Invocation; AML.T0085.001 AI Agent Tools; AML.T0080 AI Agent Context Poisoning |
| 7 | AML.T0067 LLM Trusted Output Components Manipulation; AML.T0054 LLM Jailbreak |
| 8 | Mitigation mapping across the above |

### 7.3 NIST AI RMF mapping

The findings documentation assignment maps to four subcategories, quoted verbatim from NIST AI 100-1:

| Subcategory | Text | Where |
|---|---|---|
| MEASURE 2.7 | "AI system security and resilience, as identified in the MAP function, are evaluated and documented." | Project 2, weeks 7 to 8 |
| MAP 5.1 | "Likelihood and magnitude of each identified impact ... are identified and documented." | Severity rating column, final block |
| MANAGE 4.3 | "Incidents and errors are communicated to relevant AI actors ... Processes for tracking, responding to, and recovering from incidents and errors are followed and documented." | Findings report, final block |
| GOVERN 4.3 | "Organizational practices are in place to enable AI testing, identification of incidents, and information sharing." | Rules of Engagement, week 1 |

Two honest notes: which subcategories fit is an editorial judgment, since NIST publishes no official mapping for coursework. And AI RMF 1.0 predates the current agent-security landscape and contains no agent-specific subcategories, which is why NIST AI 100-2e2025 carries the attack vocabulary instead. AI RMF 1.0 is also under active revision; a revision would change the subcategory identifiers, so re-check before the term.

### 7.4 NSA knowledge unit alignment

Both gates are cleared: the program holds CAE-CD and this course will be required. Full treatment, including the carrier map across the whole degree, is in the companion document `ku-coverage-analysis.md`. This section states only what ITSY 1377 itself carries.

**Map it to exactly three knowledge units.** Three is the ceiling for a 3 SCH course, and this sits exactly on it.

| KU | Role | What this course owns |
|---|---|---|
| **AI for Security Assessment (AIS)** | **Lead carrier** | Machine learning applied to vulnerability assessment and prioritization; automated threat detection; log and alert triage; anomaly detection on security telemetry; evaluating AI tool output for false positives, confidence, and explainability; adversarial robustness of security models. Co-carrier: DSAI 1374 |
| **Defensive Applications of AI (DFA)** | **Co-lead** | Detection and classification models; user and entity behavior analytics; AI in SIEM and SOAR workflows; model drift and retraining; poisoning and evasion attacks against defensive models. Co-carrier: ITSY 2430 Intrusion Detection |
| **AI Governance, Laws, and Ethics (AIG)** | **Supporting, legal and regulatory half only** | NIST AI RMF; EU AI Act risk tiers; GDPR, CCPA, and HIPAA as applied to AI systems and training data; AI incident disclosure duties; organizational AI acceptable-use policy. **This half exists nowhere else in the catalog.** Co-carriers: DSAI 1371, DSAI 2378 |

**Choose DFA rather than OFA.** ITSY 2430's anomaly and behavioral detection content is a genuine defensive anchor, and nothing at the college supports an offensive-AI claim.

**Do not map this course to Basic Scripting and Programming**, for the reasons in section 0.6, nor to Cybersecurity Fundamentals, Machine Learning Fundamentals, or AI Fundamentals, all of which are better carried elsewhere and would trigger the dilution flag.

**Two of these three units have no other possible home** in the college's catalog, because the DSAI courses contain no security content and the ITSY courses contain no AI content. That gap is the strongest available justification for creating this course.

**The efficiency lever worth knowing.** KU alignment is lighter than it looks: KU outcomes are "listing only, no assessment of outcomes," and topics are "recommended and not required." Assessment evidence is required at the **program** outcome level, not per unit. Each aligned course supplies a syllabus plus guidelines for one hands-on lab, and **Module 3, "Break It," is the lab to submit**: it is unambiguously security work rather than a programming exercise, it maps directly to three AIS outcomes, it has the artifacts reviewers ask about (a defined authorization boundary, a reproducible containerized environment, deterministic pass criteria), and its marginal cost is zero because those artifacts must exist anyway.

**A structural asset:** this is a Local Need course, so the college authors its outcomes. They can be written line by line against the AIS and DFA element lists before submission, rather than reverse-engineered from a standardized description afterward.

## 8. Where the Scope Does Not Fit

The brief asked for this stated plainly. Here it is, ordered by how much it should worry a reviewer.

### 8.1 Two outcomes over-claim what 8 weeks can deliver

The outcomes are fixed and this blueprint does not reword them. But the committee should know what will actually be assessable.

**O1 says "automate ... including request construction, response parsing, and error handling."** Read as authorship, this cannot be met. Reaching blank-file authoring competence takes 45 to 60 hours of CS1 instruction plus practice, and introductory programming pass rates sit around 67 to 72 percent even with that. **Fifteen to twenty hours buys modify-and-run competence, not author-from-blank competence.**

What the course will actually evidence: given a working request template, the student modifies it to change the model, parameters, and system prompt; completes a response-parsing function from a provided signature and docstring; and adds exception handling for a specified error class. That is real, it is assessable, and it is honest. Every code deliverable is a stub completion inside a working scaffold. Never a blank file.

**O6 says "evaluate AI-generated code and output for correctness."** A student with twenty hours of Python cannot evaluate arbitrary AI-generated Python for correctness. That is a senior skill.

What the course will actually evidence: the student verifies AI-generated code against a provided specification by executing it, comparing output to expected results, and identifying cases where generated code fails silently. The AI Code Audit exercises supply the defective code and withhold the answer key, with defects drawn from the classes that language-model reviewers systematically miss (time-of-check to time-of-use on a path allowlist, `except Exception: pass` swallowing tool errors, validation that checks key presence but not type, raw tool output re-entering the system prompt, a retry loop that retries on 4xx).

**O4 says "interpret the results."** Against a nondeterministic model this is a hole unless the harness fixes it. A case that passes 7 of 10 runs is neither pass nor fail, and freshmen have no statistical framing for that. The N-of-M design in section 5.2 is what makes O4 assessable: the harness reports the rate with a fixed threshold, and the student reads and explains it. **Without that design decision, O4 is not assessable and the course should not claim it.**

**This is a curriculum committee question, not an instructor question.** If the outcomes must be assessed at the verb level as written, O1 and O6 are unmeetable in 8 weeks with no programming prerequisite. If they can be assessed at the "extend and configure" level the outcome verbs elsewhere imply, the design meets them.

### 8.2 Seven weeks of calendar, eight weeks of content, and week 3 is now the break point

The original grid assumed eight instructional weeks. The calendar provides seven plus a final block whose exam window is carved out of it, not added to it. **Roughly a week and a half of content had to go**, and section 8.3 names exactly what.

Compressing also raises the per-week ceiling. A 3 SCH course implies roughly 135 to 150 total student hours; across seven instructional weeks plus a light final block that is about **19 to 21 hours per week**, up from 17 to 19. That is a half-time job, and Alamo students commonly take two or three of these concurrently while employed.

**The break point moved from week 2 to week 3.** In the eight-week draft, week 2 was the disaster week at 17 to 22 hours. Moving error handling out of it and into week 3 defused that. Week 3 is now the failure point, for four converging reasons:

1. It absorbs the tail of the old week 2 *and* all of the old week 3, so it is the only week carrying compression residue from two source weeks.
2. It contains the single hardest abstraction in the course for a student with no programming background: the inversion from "my script calls the model" to "the model calls my function." Freshmen do not get this on first contact.
3. It carries the Project 1 checkpoint.
4. It sits immediately after census on day 8, so students who should have dropped are still enrolled and are hitting the hardest week of the term with no exit having occurred.

**Mitigations, all specified in section 2 and all cheap:** the checkpoint is pass/fail with a fallback path, so a stuck student still passes and still advances; the `agent-working` branch publishes on day 18, before the deadline rather than at it; required reading is capped at 45 minutes and spent entirely on the annotated skeleton; a "Top 10 Week 3 Errors" thread is pinned on day 15 before anyone has hit them; and nothing due on day 21 requires working code except the checkpoint, which has the fallback. The week cannot produce a cascading failure.

**A calendar detail the design exploits:** the last day to withdraw falls around day 39 to 43. Project 1 and its checkpoint are therefore graded and returned **by day 35**, so every student holds real grade evidence before the withdrawal deadline rather than after it.

### 8.3 What this course cannot deliver, and must not claim

- **Not OWASP LLM Top 10 coverage.** Three of ten risks substantively. Say "selected OWASP risks."
- **Not agent development.** Students extend a scaffold. They cannot build an agent from an empty directory.
- **Not Python competence.** No object orientation, no algorithms, no data structures beyond lists and dictionaries, no testing discipline, no meaningful version control. **This course does not articulate into COSC 1436 and must not be listed as preparation for it.**
- **Not red teaming or penetration testing.** Students run pre-authored attack classes against one known-vulnerable instructor-built target. That is exercise, not discovery. No novel vulnerability identification, no scoping negotiation, no client interaction.
- **Not production hardening.** No sandboxing, no identity architecture, no secrets management beyond a `.env` file, no monitoring, no deployment.
- **Out of scope entirely:** MCP server security (named only), multi-agent systems, RAG and vector-store security, model supply chain.

**What the shortened calendar specifically cost, named rather than glossed:**

| Cut or compressed | What it was | What it is now | The cost |
|---|---|---|---|
| **Insecure tool authorization** | A hands-on exploitation lab | A guided walkthrough of an annotated exploit that students read and answer questions about | **The biggest real loss.** Outcome 3 names three weakness classes and students get hands-on exploitation experience with only two. A student leaves able to describe insecure tool authorization without having broken one |
| **Remediation** | Implement and re-test two remediations | Implement and verify one; specify the second in writing with the test that would verify it | Students demonstrate the remediation loop once, not twice. A written specification is weaker evidence than a working fix, and it still counts toward outcome 5 |
| **Practice findings write-up** | Two rehearsals before the graded report | One, attached to Attack Lab 1 | Report quality on the graded submission will be measurably lower |
| **Response parsing** | Taught as a topic | Taught as "pull this field out of this response," repeated across three labs | Students can navigate the response shapes this course uses and will be lost on an unfamiliar API |

**Protected and not cut:** all Python instruction, both project checkpoints, the Module 0 gate, prompt injection as a hands-on lab, and the attack-and-fix pair that carries outcomes 3, 4, and 5.

**The honest bar:** a student who completes this course can modify a working agent, run a structured attack harness against it, explain three classes of agentic vulnerability, and produce a findings document they could show an employer.

### 8.4 Instructor workload now fits, and that was not free

The earlier design came in at roughly 41 hours per term after automation and about 60 without. Against an adjunct carrying this course, that did not fit. The rebuilt architecture in section 3 lands at **22.7 hours, or 26.1 with contingency**, with 73 percent of the grade auto-scored and total hand-reading across the entire course of five hours.

That was achieved by converting the expensive hand-read comprehension instruments into auto-scored items anchored to each student's own run artifacts, consolidating eleven graded components into eight with fewer deadlines, and auto-grading the security work deterministically through canary tokens and side-effect ledgers rather than reading transcripts.

**What it cost.** The narrative evidence for outcome 5 is now concentrated in a single 900-word report rather than spread across multiple written artifacts, and outcome 1's direct evidence reduces to one lab plus exam items. Section 3.7 states both plainly, along with the zero-cost mitigations. This is a genuine trade of evidentiary breadth for instructor sustainability, and it is the right trade for an adjunct-taught course, but it is a trade.

**Three things must not be automated away**, because they are the highest signal per minute in the course: the report's finding-accuracy and remediation-adequacy rubric rows, the 150-word prompt asking what defect the student knows remains in their fix, and the behavioral scope-lure grep.

### 8.5 Environment setup is the week-1 attrition risk

Planning assumption, and it is labeled as an assumption rather than a finding because no citable study for this population was found: **20 to 30 percent of students will need help beyond self-service documentation, and 5 to 15 percent will not resolve it within week 1.** At 30 students that is 6 to 9 students needing intervention and 2 to 5 at risk of never starting.

In an asynchronous course the usual fix, walking up to the instructor, does not exist. That is the most-cited reason setup failures become withdrawals rather than delays.

Mitigations: no local installs in week 1 (browser notebook only); Module 0 opens five to seven days early with a day-3 artifact; one optional live setup clinic in week 1, or a per-platform screencast plus daily forum staffing for the first five days; and the `mock` provider, which means a student with no API key can still complete lab 1.

### 8.6 The Rules of Engagement are a real constraint, not a formality

This is the sharpest liability issue in the packet and it needs a decision before the term.

Verified provider policy language:

- **Google's Generative AI Prohibited Use Policy** prohibits "Circumvention of abuse protections or safety filters," with **no research or red-teaming exception** anywhere in the policy.
- **Groq's Acceptable Use Policy** (effective October 15, 2025) prohibits prompts "to intentionally circumvent any aspect of the Cloud Services or AI Model Services, including abuse protections or safety mechanisms," but does provide a written exception path: "Customers who have implemented adequate safeguards and require additional flexibility for lawful business or research purposes, may contact Groq to request an exception."
- **OpenRouter** section 7.10 bans "prompt injection, jailbreaking, or taking any other adversarial action" without prior written approval, and operates the only documented authorized red-teaming program found (safety@openrouter.ai, roughly five business days). It is not viable as a backend, but it is excellent teaching material about what authorized testing actually looks like.

**The practical consequence, and it is also good pedagogy:** the attack labs must target **the vulnerable application's trust boundary and tool authorization**, not the model's safety filters. Students attack their own agent and the instructor's target, not the provider's model. That is a defensible distinction, and every lab case must be written that way deliberately.

Three requirements before the term starts:

1. Someone requests the Groq exception in writing, or the labs run entirely on local models and the mock provider.
2. **Per-student keys, never a shared instructor key.** With a shared key, the instructor is the party who agreed not to red-team while 30 students proceed to do so.
3. A privacy note in the syllabus if Gemini is used: its free tier explicitly uses submitted content to improve Google products, and Google's own terms say "Do not submit sensitive, confidential, or personal information to the Unpaid Services." That is a FERPA-adjacent concern independent of the adversarial-testing question.

### 8.7 The local-model path is viable on paper and untested in practice

The good news is real and verified. Ollama's official Windows documentation states twice and unambiguously: "The Ollama install does not require Administrator, and installs in your home directory by default." Its OpenAI-compatible endpoint at `http://localhost:11434/v1/` supports tool calling. Two Apache 2.0 models fit comfortably in 8GB: `qwen3:1.7b` (1.4GB) and `granite4.1:3b` (2.1GB).

Six honest caveats:

1. **None of this was tested on an actual locked-down student machine.** Vendor documentation saying "no Administrator required" is not the same as surviving a specific institution's AppLocker, Windows Defender Application Control, or SmartScreen policy. Many managed education environments block user-space executables precisely to stop no-admin installers. **This must be piloted on one real student-image laptop before the syllabus commits to it.** It is the largest residual risk in the build and no amount of documentation research retires it.
2. **`tool_choice` is not supported** on Ollama's OpenAI-compatible route. The agent skeleton must work with model-discretion tool calling only.
3. **Ollama publishes no minimum RAM requirement anywhere.** The historically quoted 8GB line has been removed from current documentation. Any RAM number in course materials is an engineering estimate and should be labeled as one.
4. **Disk may bite before RAM does.** The installer is a 1.57GB download, plus 4GB for the install, plus 1.4 to 2.5GB per model. Budget laptops often ship with nearly full 128GB or 256GB drives.
5. **Tool-calling quality at 1 to 4 billion parameters is the real academic risk and it could not be verified.** A vendor-declared "tools" capability means the chat template can emit tool-call syntax. It does not mean the model reliably picks the right tool or formats arguments correctly. Expect materially higher failure rates than a hosted model. **The labs must be designed so a malformed tool call is a teachable event rather than a broken assignment**, which is exactly what the N-of-M harness design does.
6. A GitHub issue (closed as not planned, no maintainer reply) claims the Windows GUI app requires administrator rights. The mitigation is to use the CLI or the standalone zip rather than the GUI.

**Fallback if Ollama is blocked:** llama.cpp ships an 18MB prebuilt Windows CPU zip with no installer, no registry writes, and no administrator rights. Tool calling is **off by default** and requires launching `llama-server` with the `--jinja` flag.

**Also ruled out:** LM Studio (its own docs recommend 16GB, double the target hardware, and it is proprietary closed source under a restrictive EULA); GPT4All (roughly 15 months without a commit, tool calling undocumented); llamafile (genuinely no-install and actively maintained, but tool calling is undocumented and Windows cannot run executables over 4GB).

### 8.8 Canvas deployment is the riskiest part of Phase 0

The brief anticipated this and it was right to. Three specific risks, all verified from the repository and its issue tracker:

1. **Apple Silicon is not supported and never has been.** The "ARM64 support" issue sat open from November 2020 and was closed as **not planned** in March 2026. No arm64 support was ever documented. Cutting the other way, the official Dockerfile's base image does publish a native linux/arm64 manifest and `Gemfile.lock` already lists `aarch64-linux`, so the build is not architecturally hopeless. Upstream has simply never committed to it.

2. **`docker_dev_setup.sh` makes global changes to your Docker environment on macOS.** It installs the dinghy HTTP proxy system-wide without asking. One reported case required reinstalling Docker and clearing browser localStorage to recover. **Do not run it on a workstation with other Docker work on it.**

3. **The documented setup has a known silent failure mode.** In the representative recent issue, the setup script runs to completion, the containers come up, and the browser shows only the Dinghy proxy page, because the Rails application died on a `bundler-multilock plugin is not installed` error that the setup script never surfaced. Related: re-running the setup script over an existing environment still fails on `db:drop`, with the fix sitting unmerged.

Two more facts worth knowing: the public `master` branch is roughly four months behind, while the API documentation is generated from Instructure's current production code, **so the docs and the code you can clone are not the same version**; and the documentation itself is internally stale (it references a Mutagen sidecar that does not exist in any compose file).

**Local machine check:** Docker CLI 29.7.2 and Compose v5.3.1 are installed here, but the daemon (colima) is not currently running. Canvas's own documentation requires at least 8GB allocated to Docker, and the repository alone is 2.2GB.

**Recommended approach for Phase 0:** attempt the official repository path first, as directed, with a hard time-box. If it fails, document exactly what failed and fall back to `ahamana/canvas-lms-docker` (MIT wrapper, actively maintained with daily rebuilds, prebuilt **arm64** Debian images, and non-interactive admin creation already wired to the same rake task). That project builds its image by cloning `instructure/canvas-lms` from GitHub, so the fallback still satisfies the requirement that Canvas comes from the official repository. **Use a Debian tag, not Alpine: the Alpine tags are amd64 only.**

One licensing note for the record: the community wrappers are MIT or Apache 2.0, but the images they publish **embed Canvas LMS, which is AGPL-3.0, including its network-use clause.** That matters only if the demo is ever exposed over a network to third parties, which it should not be.

### 8.9 Smaller risks worth naming

- **Rate limits will read as broken code.** Groq's 8,000 tokens-per-minute free limit, against an agent loop carrying accumulated history plus tool schemas, is roughly two to three calls per minute before throttling. A 7-case, 5-trial harness run is 100-plus requests. Students will read 429s as their own bug. **The harness must ship with backoff and a human-readable "rate limited, waiting" message**, and it must print an estimated request count and wall time before it starts.
- **MITRE ATLAS deep links will fail automated link checkers.** The site is now a client-side single-page application on GitHub Pages, and every deep route returns HTTP 404 to a fetcher while rendering correctly in a browser. Only the homepage and the Navigator app return 200. Canvas link validation will flag these as dead. Build course handouts from the pinned YAML data file instead of scraping the site, and expect the link report to be noisy.
- **Framework churn is fast.** ATLAS ships roughly monthly and renames techniques. OWASP shipped a new LLM Top 10 edition in August 2026. NIST AI RMF 1.0 is under revision. **Pin a specific ATLAS release and a specific OWASP edition in course materials, and re-verify before each term.** This course will need a maintenance pass every semester, which is a real ongoing cost the program should budget for.
- **The `77` slot may already be taken.** The live THECB WECM database could not be queried (the search tool is a Power BI embed and the update application requires a CBPass login), so whether some institution already holds an approved Local Need ITSY 1377 is unresolved. NLC should confirm via CBPass or by calling THECB before relying on the number.

### 8.10 The demo will not look like the real thing without a styling shim

Covered in full in section 5.7. Stated here because it is the risk most likely to undercut the demo itself: the NLC template's visual design comes from **DesignPLUS**, a licensed Cidi Labs product loaded at the Canvas account level, and it is not in the export. In a local Canvas the pages import intact but render as unstyled divs.

The mitigation (keep the real class names, ship an open CSS shim for the demo only) is sound, but it should be understood as a compromise with two consequences. First, **the demo's appearance will not match the production course exactly**, and the runbook must say so rather than let a reviewer assume otherwise. Second, **this is a genuine production dependency**: if the course is ever deployed anywhere other than Alamo's Canvas, the styling has to be solved again. That is worth knowing before the program commits to the template as a distribution format.

### 8.11 A 7th grade reading level and a graduate-level source base cannot both be fully satisfied

Covered in full in section 5.8. The short version for a reviewer: the plain-language standard is achievable and enforced by an automated check for **all instructor-authored content**. It is **not** achievable for the external framework documents, because NIST and OWASP publish for professionals and the course cannot rewrite them.

Two things follow, and both are stated plainly rather than papered over. **The measured grade level on technical pages will sit above 7.0 even when the writing is good**, because readability formulas count syllables and this subject's vocabulary is polysyllabic; the enforceable commitments are therefore on sentence length and on defining every term at first use. And **every external reading needs an instructor-authored bridge**, which is real authoring work that has to be budgeted in Phase 3 rather than assumed.

If a reviewer requires a hard grade-7 score on every page including technical vocabulary, that cannot be delivered without removing the vocabulary, and removing the vocabulary would prevent the course from meeting outcomes 3 and 5. That is a genuine trade-off and it belongs to the committee, not to the instructor.

### 8.12 The programming knowledge unit sits outside this course, by necessity

Resolved; see section 0.6 and the companion document `ku-coverage-analysis.md`. Retained here because a reviewer will ask why a course that teaches Python does not carry the scripting knowledge unit.

The answer that matters most is not about hours. **This course must permit AI assistance on all coding, because its outcome 6 requires students to evaluate AI-generated code, and a course that bans AI cannot assess that.** The knowledge unit requires evidence that a student personally wrote and executed a script. No artifact produced under this course's AI policy can serve as that evidence. The two positions are contradictory inside one syllabus, and an AI-prohibited island inside an AI-permitted course fails on enforceability, coherence, and risk.

There is a benefit running the other way worth stating: **the unassisted foundation the knowledge unit requires is exactly the preparation this course's outcome 6 assumes.** A student who has written and debugged their own code can judge whether generated code is correct. A student who has not is comparing one unfamiliar text against another.

**The residual constraint is credit hours, not knowledge units.** The degree is at exactly 60 SCH against a statutory ceiling, so adding this course requires removing 3 SCH. That is a program decision, treated in the companion document.

---

## 9. What Was Assumed and What Could Not Be Verified

Listed as the brief requires.

**Assumed:**
- 3 semester credit hours, and a total student time budget of 135 to 150 hours (the standard US convention). The weekly workload arithmetic in section 8.2 rests on this.
- 2 lecture + 4 lab = 96 contact hours is the recommended WECM designation. Not yet decided by anyone.
- ITSY 1377 is a proposed Local Need course that does not yet exist. This is consistent with the numbering rules and with its absence from the NLC catalog.
- Attrition percentages in section 8.5 are a planning range, not a finding.
- Instructor grading-load hours are estimates from the assessment design, not measurements.

**Could not be verified:**
- Whether Groq's free plan requires a credit card. It clearly has a free plan with published limits and a paid upgrade path, which strongly implies no card, but no page states it. **This is the single highest-value unverified fact in the report, because Groq is the recommended primary provider.** Someone should sign up with a fresh account and confirm.
- Gemini and Mistral free-tier numeric rate limits. Both providers have removed them from public documentation and now defer to a login-gated console. **Do not print free-tier numbers in the syllabus.**
- OpenAI's usage policy text (HTTP 403 to all automated fetching).
- All CISA AI guidance (HTTP 403 to all automated fetching).
- **RESOLVED by the program:** CAE-CD designation is held, and the course will be required. Both KU gates are cleared.
- Whether the **CyberAI requirements** on record are current. The document retrieved is explicitly labeled a December 2024 **Draft 3**, and the pilot has since concluded. The NCAE-C documents index is behind DoD authentication, so newer versions could not be enumerated. **Verify with the NCAE-C program office before committing curriculum.**
- Whether the **final exam requirement** is district policy. The "comprehensive final evaluation, not to exceed three hours" language comes from the St. Philip's College student handbook, corroborated by the NLC Faculty Handbook closeout procedure. No equivalent district board policy was found. Verify with the department chair.
- Whether any Alamo-specific **regular and substantive interaction** policy exists. The federal obligation applies, but no local definition or checklist was found. Do not attribute RSI specifics to Alamo.
- Whether an approved Local Need ITSY 1377 already exists at another Texas institution.
- Whether HCC's ITAI 1372 counts against the Local Need equivalence test. The two governing documents are in genuine tension.
- Whether ITSY sections are actually scheduled in Flex I or Flex II terms at NLC. The Flex structure and all eight session date ranges are confirmed from the official calendars; a live section schedule was not checked.
- The **Spring 2027 Flex II withdrawal date is misprinted** in the official AY2026-27 calendar PDF: it reads "Thursday, April 30, 2026," which is the wrong year, and 30 April 2027 is a Friday. Confirm with the Registrar.
- The NLC Faculty Handbook (2020-2021) and student handbook (2019-2020) are the sources for the excessive-absence threshold and the closeout procedure. Both are dated and may have been superseded.
- Whether Alamo's Banner/ACES systems technically enforce the one published ITSY prerequisite, or whether it is advisory catalog text.
- Whether NLC requires **BioSig-ID identity verification** or **Respondus LockDown Browser** for a fully distance course. Both ship in the template, which is suggestive but not proof. This changes the week 1 setup burden.
- Which **Quality Matters rubric edition** the template's "25 standards" claim was measured against. The claim is undated in the template, and the current rubric is the Seventh Edition. The count may not still hold.
- Whether content authored with DesignPLUS classes but **written outside the DesignPLUS sidebar** renders correctly in Alamo's production Canvas. The class names were copied from the template's own pages, so this is likely, but it was not tested against a live DesignPLUS theme.
- **Nothing in this blueprint was boot-tested.** No Docker setup was run, no model was called, no Canvas instance was started, and **the NLC template was never imported into a Canvas instance**. It was analyzed as files on disk. Every arm64 claim comes from inspecting registry manifests, not from a container that started.

---

## 10. Decisions and Open Items

### Settled by the program

| # | Decision | Consequence |
|---|---|---|
| 1 | **ITSY 1377 will be required**, not elective | KU alignment gate cleared. Section 0.3 |
| 2 | **Provider terms-of-service risk accepted for the proof of concept**, with agreements in place for production | Section 8.6 stands as the production requirement. Labs remain scoped to the application trust boundary rather than the model's safety filters, because that is better pedagogy independent of risk |
| 3 | **Common Cartridge is the primary Canvas artifact** | Deliverable D changes accordingly. Section 5.5 |
| 4 | **CAE-CD is already held; AICyber is the goal** | Eligibility gate cleared, and section 0.6 becomes urgent |
| 5 | **COSC 1436 is being removed** as this course is added | Creates the conflict in section 0.6 |
| 6 | **3 SCH, no more than 3.9 workload hours** | Decides the contact-hour split. Section 0.8 |
| 7 | **8-week Flex, Sunday deadlines, final exam required** | Seven instructional weeks plus a six-day final block. Section 0.7 |

### The blocking decision is resolved

The previous draft flagged one blocker: removing COSC 1436 while pursuing AICyber. **That is resolved.** COSC 1436 is retained, the scripting knowledge unit is carried jointly by COSC 1436, DSAI 1373, and ITSC 1316, and no new scripting course is required. See section 0.6 and the companion document `ku-coverage-analysis.md`.

**What replaces it is a program-level decision rather than a course-level one:** the degree sits at exactly 60 semester credit hours against a statutory ceiling, so adding this course requires removing 3 credit hours. The companion document gives three concrete 60-hour plans and recommends assembling a separate "AI Cyber Defense" program of study from existing Cyber Defense and DSAI courses, rather than deleting forensics and incident response from a degree that depends on them.

**Nothing in that decision changes this course's build.** ITSY 1377 is the same course in every scenario, so Phase 2 can proceed while the program question is settled.

**Five verification items should run in parallel**, all free: pull actual syllabi for the carrier courses; confirm whether DSAI 1373 teaches regular expressions and documents cross-platform Python; confirm Local Need approval and expiry dates for the nine DSAI courses and this one; confirm which program of study currently holds CAE-CD; and pin the mathematics core slot to MATH 1342.

### Answers to the two questions asked

**"The most time and resource efficient way to handle that and still meet the KU and outcomes."** Section 3 is that answer: four lab modules with auto-scored code and comprehension halves, two near-free pass/fail checkpoints, and a three-part final, landing at **22.7 instructor hours** with 73 percent auto-scored and five hours of hand-reading across the whole term. The lever specific to the KU goal is that **KU alignment requires no per-KU assessment instrumentation**: KU outcomes are listed rather than assessed, and KU topics are recommended rather than required. Each aligned course needs a syllabus plus guidelines for one hands-on lab, and section 7.4 nominates Module 3 for that.

**"If 2 lecture + 4 lab still results in that then good."** It does not. Under Alamo procedure D.5.1.2 it is **5.60 workload units**. Section 0.8 recommends **2 lecture + 2 lab, 64 contact hours, 3.80 workload units**, which stays under the cap with headroom, keeps a formal laboratory designation, and remains a THECB preferred combination for 3 SCH.

### Smaller items, settleable during Phase 2

1. Whether identity verification (BioSig-ID) or proctoring (Respondus) is required. The assessment design needs neither and is compatible with both.
2. Whether the college's courseware policy accommodates CC BY-SA ShareAlike obligations if OWASP text is adapted rather than linked.
3. Whether Canvas runs from the official repository path or the documented arm64 fallback. Phase 0 answers this empirically.
4. Who transcribes the OpenAI usage policy clause from a browser for the Rules of Engagement.
5. Confirming the current CyberAI requirements version with the NCAE-C program office, and the final exam policy with the department chair.

## Appendix: Deviations From the Brief's Proposed Structure

The brief invited adjustments with justification. The first four are course-design changes; the last two change named deliverables or the shape of the term.

| # | Change | From | To | Why |
|---|---|---|---|---|
| 1 | **Term structure** | 8 instructional weeks | **7 instructional weeks plus a 6-day final block** | Forced by the calendar, not chosen. A Monday-to-Saturday Flex session is 55 days and contains only seven Sunday deadlines, and the final exam window is carved out of the last week rather than added to it. Section 0.7 |
| 2 | **Contact-hour split** | 2 lecture + 4 lab implied by comparable courses | **2 lecture + 2 lab, 64 contact hours** | Forced by the 3.9 workload cap. 2 + 4 is 5.60 workload units under Alamo procedure D.5.1.2. Section 0.8 |
| 3 | Practice findings write-up | Week 8 | **Week 5** | Week 5 held the only slack in the term; the final block has none. Makes the graded report the student's second attempt at the genre rather than their first |
| 4 | Insecure output handling and harness introduction | Weeks 6 and 7 | **Week 6** | Moving the harness introduction earlier makes week 7 extension-only rather than introduction plus extension |
| 5 | Comprehension gate | Week 4 (first check) | **End of week 2, plus a day-3 Module 0 gate** | Week 2 is where failure is silent. The day-3 gate is separately required: census falls on day 8 and Alamo mandates an attendance verification activity by the third class day |
| 6 | Canvas artifact | API population script | **Common Cartridge, with an API script for incremental updates** | Approved by the program. It is how the institution actually moves courses, and it carries rubrics and outcomes the REST API handles badly. Section 5.5 |

**What the brief required and this design preserves:** scaffolded rather than blank-page work throughout, exactly two projects, a low-stakes pass/fail checkpoint at each project's midpoint, one shared reference target, Python taught in-course and scoped to API calling, AI assistance permitted with comprehension assessed instead, and the graded week-one Rules of Engagement referenced in every attack lab.

**One brief constraint came under pressure and was protected deliberately.** The lean assessment rebuild in section 3 could have deleted both project checkpoints, on the argument that a visible autograder score already tells a student where they stand. That was rejected. The brief is right that in an asynchronous 8-week course a student who is stuck in week 3 and silent until week 6 has withdrawn, so both checkpoints survive as pass/fail items derived from the autograder result, costing almost no instructor time.

**Relative to the NLC Online Course Template**, the course adds two things and changes one. Module 0 plus seven weekly modules and a final block is as close to the template's own recommendation as the calendar permits. The two additions are **Module 9: Where To Go Next**, which the template does not contemplate but which costs almost nothing and converts the course into a pathway, and an **instructor-facing framework alignment page** carrying the mapping tables in section 7, which serves the WECM submission and the KU alignment rather than the students. The change is that the template assumes eight instructional weeks and the calendar provides seven.

---

*Prepared for review. No course content, lab code, or Canvas scaffolding has been built. The NLC Online Course Template was read but not modified and not imported. Awaiting approval or revision before Phase 2.*
