# Programming Knowledge Unit Coverage: Analysis and Recommendation

**Companion to the ITSY 1377 course blueprint**
**Northeast Lakeview College, Cyber Defense A.A.S.**
**Prepared for the curriculum committee and the CAE point of contact**
**Document date:** 2026-08-27

---

## Purpose

This document answers two questions the program raised:

1. **Why can the NSA Basic Scripting and Programming knowledge unit not simply be folded into ITSY 1377?** The program needs this documented thoroughly, because adding or reassigning a course requires a written justification.
2. **Can the AICyber knowledge units be carried by courses that already exist**, rather than by adding new ones? This is the program's stated preference.

The short answers are in section 1. The evidence is in sections 2 through 6.

---

## 1. Summary of Findings

**On question 1.** ITSY 1377 cannot carry Basic Scripting and Programming (BSP). Four independent arguments each defeat it on their own, and they are set out in section 3:

| # | Argument | The finding in one line |
|---|---|---|
| 1 | **Arithmetic** | ITSY 1377 defensibly covers **9 of BSP's 18 topic elements, 50 percent**, against a required **75 percent** |
| 2 | **Outcomes** | Two of BSP's six learning outcomes cannot be defended at all: automating system administration tasks, and regular expressions |
| 3 | **Displacement** | Closing the gap needs an estimated **26 instructional hours in a 64-hour course**, and every combination of cuts that frees them destroys or reduces **at least three of ITSY 1377's six required outcomes** |
| 4 | **Assessment integrity** | ITSY 1377 **must permit AI assistance** to assess its own outcome 6, while BSP requires unassisted "write and execute" evidence. **One syllabus cannot hold both positions** |

Argument 4 is the strongest and the least obvious. It is not a scheduling problem and no redesign fixes it, because the AI policy that BSP forbids is the same policy ITSY 1377's outcome 6 requires.

**On question 2.** The answer is a qualified yes, and it is better news than expected. Section 5 gives the full carrier map. The load-bearing points:

- **BSP has two plausible existing homes already in the required plan**: COSC 1436 Programming Fundamentals I, which is retained, and ITSC 1316 Linux Installation and Configuration, which is required in Semester I and is the natural home for the regular expressions, permissions, and shell scripting that a traditional programming course omits. Whether they jointly clear 75 percent is answered in section 5.
- **Northeast Lakeview already owns nine DSAI courses** and a Data Science and Artificial Intelligence award. That is the cheapest available source of AI knowledge unit coverage and it is sitting in the college's own catalog.
- **Four knowledge units have strong existing carriers** with no action required: IT Systems Components, Cybersecurity Fundamentals, Basic Networking, and Network Defense.
- **The genuine gaps are Machine Learning Fundamentals, AI Governance, and AI for Security Assessment.** ITSY 1377 is built to close the third.

**The constraint that dominates everything.** The Cyber Defense A.A.S. is **exactly 60 semester credit hours today**, and 60 is the statutory Texas ceiling under SB 497 (2013). Exceeding it requires a THECB exemption justified by programmatic accreditation or licensure requirements, and CAE validation is voluntary, so it may not qualify. **Adding ITSY 1377 means removing 3 semester credit hours from the existing plan before any other change is considered.** Section 6 gives concrete 60-hour plans.

---

## 2. What Was Verified, and How

Every claim below is checked against a primary source. Where only a catalog description was available rather than formal end-of-course outcomes, that is stated, because descriptions are weaker evidence than outcomes and a CAE reviewer will want the stronger form.

**An evidence problem the program should know about now.** Northeast Lakeview College publishes **no end-of-course outcomes for any course** in its catalog. Each record carries a description, semester hours, a CIP code, and an "offered at" flag, and nothing more. This was verified against the current 2026-2027 catalog.

**Consequence:** no knowledge unit mapping can be produced from the catalog alone. **Collecting current syllabi for every course in the plan is a blocking prerequisite for any CAE submission**, not a clerical task to do at the end. It is also free, and it should start now, because it gates everything else in this document.

**The BSP standard being applied**, quoted verbatim from the NSA knowledge unit document:

> "To complete each KU, an alignment to a minimum of 75% of the topics and sub-topics is required."

and

> "While it is not required that every learning outcome be explicitly assessed as written, applicant schools should be able to defend their coverage of the learning outcomes."

BSP presents 8 top-level topics, the eighth carrying 10 sub-topics, for **18 elements**. Seventy-five percent of 18 is 13.5, so the minimum is **14 of 18**.

**Two further rules that shape the recommendation:**

> "A KU may be covered by one or more courses, however, a course should not be aligned to an excessive number of KUs given the challenge of so many KU Outcomes coverage with a single course."

and, on the other side, four or more courses aligned to a single knowledge unit "may be more of an indication of week [sic] KU coverage than strength because it risks diluting the KU." **Two to three co-carriers per knowledge unit is the safe band.**

> "A KU should not be aligned to elective or optional course(s), as all students are required to take all courses indicated in the KU alignment documentation."

**Every course named as a carrier in this document must therefore be required for all students in the program of study.**

---

## 3. Why ITSY 1377 Cannot Carry BSP

### 3.1 Element-by-element coverage

Scoring convention. **Yes** means the element is taught, practiced, and evidenced in an assessed artifact. **Partial** means it is touched incidentally in service of another objective but is not taught as a topic and not separately assessed; because CAE alignment must be demonstrable in the syllabus, materials, and assessments, **Partial is scored as not aligned**. **No** means it does not appear.

| # | BSP topic element | Covered | Why |
|---|---|---|---|
| 1 | Basic security concepts | **Yes** | Outcomes 3 and 5 are wholly security objectives. This is the course's strongest BSP alignment |
| 2 | Permissions, bounds checking, input validation, type checking, parameter validation | Partial | Input and tool-parameter validation appear as injection and authorization defenses. Operating system permission models, buffer bounds checking, and explicit type checking do not |
| 3 | **Regular expressions** | **No** | No outcome requires pattern matching. Response parsing is structured JSON deserialization, not text extraction. No instruction, practice, or assessment exists |
| 4 | Data structures and algorithms | Partial | Students *consume* lists and dictionaries. They do not design structures, and no algorithmic content is taught |
| 5 | Boolean logic including XOR | Partial | Compound conditions occur in retry logic and harness interpretation, but Boolean operations are not taught as a topic |
| 6 | **Scripting on both Windows and Linux** | **No** | Single language, single provided environment. No Bash, no PowerShell, no second platform. The element says "both" explicitly |
| 7 | IDE, compilers and interpreters | Partial | The tooling is used; the conceptual content is not taught |
| 8 | Basic programming constructs (roll-up) | Partial | Follows its sub-topics; cannot be claimed as written while 8c and 8h are unaligned |
| 8a | Variables and types | **Yes** | Every script assigns and manipulates typed values |
| 8b | Strings, arrays, structures | **Yes** | Prompt construction, message history lists, nested JSON payloads and tool schemas |
| 8c | Sequential and parallel execution | Partial | Sequential is pervasive. Concurrency is not taught |
| 8d | Assignments | **Yes** | Throughout |
| 8e | Decisions and branching | **Yes** | Error handling and harness result branching in student-written code |
| 8f | Loops | **Yes** | The agent loop, the retry loop, harness iteration |
| 8g | Functions, procedures, calls | **Yes** | Outcome 2 is literally function authoring with a signature and a return contract |
| 8h | Debugging techniques | Partial | Students interpret results and evaluate correctness, but systematic debugging method is not taught |
| 8i | Console and file I/O | **Yes** | Console logging, environment and config reading, findings and report output |
| 8j | Libraries | **Yes** | HTTP, JSON, environment, and model libraries in nearly every assignment |

| Basis | Count | Percentage | Meets 75 percent |
|---|---|---|---|
| **Defensible, Yes only** | **9 of 18** | **50.0** | **No, five elements short** |
| Charitable, adding the three nearest Partials | 12 of 18 | 66.7 | No, two short |
| Maximal, crediting every Partial | 16 of 18 | 88.9 | Fails anyway, see below |

**On the maximal count.** Even crediting every Partial, topics 3 and 6 remain absolute zeros and BSP outcomes 1 and 6 remain unmet. A knowledge unit alignment is not only a topic-count exercise. A maximal reading passes an arithmetic test while failing the unit, and it is the reading most likely to draw an audit finding. **That risk is not confined to BSP: a finding that one knowledge unit was overclaimed puts the credibility of the program's entire mapping in question.**

### 3.2 The two outcomes that cannot be defended at all

| BSP outcome | Defensible in ITSY 1377 | Why |
|---|---|---|
| **1. Write and execute simple scripts to automate system administration tasks** | **No** | The course automates application-programming-interface interaction, not system administration. Nothing touches file-system maintenance, user or group management, permission changes, process control, service configuration, log handling, or scheduled tasks. Issuing an authenticated request to a model endpoint is not system administration, and no reviewer would accept it as such. There is no partial claim available: the course contains zero system-administration automation |
| **6. Demonstrate conceptual understanding and practical use of regular expressions** | **No** | Regular expressions appear nowhere. Worse, the one natural hook is a hook the course must actively teach *against*: outcome 3 requires students to understand that pattern-matching filters are an inadequate defense against prompt injection. Bolting regex on there would teach a technique in the single context where the course's own content says not to rely on it |

Of BSP's six outcomes: two cannot be defended, one is half-met (bounds checking is absent while input validation is strong), one would need purpose-built assessment, and two are substantively met but evidentially unsound for the reason in section 3.4.

### 3.3 The displacement argument

Closing the gap to a defensible standard, meaning taught plus practiced plus evidenced in a graded artifact, is estimated at **26 instructional hours**: 4.0 for regular expressions, 6.0 for scripting on both platforms including system administration automation, 4.0 for permissions and bounds checking, 4.0 for data structures and algorithms, 2.0 for concurrency, 1.5 for Boolean operations, 2.5 for toolchain and debugging method, and 2.0 for proctored write-and-execute evidence. Provisioning a second operating system for every student is excluded and is not free.

**Against a 64-hour course, 26 hours is 41 percent of the whole course, and available slack is zero** because the course already cut content to fit seven instructional weeks.

Taking the most favorable possible reading, in which 3.0 hours of already-compressed material is treated as free, 21 hours must still come from the blocks that carry outcomes 2 through 6:

| Combination reaching 21 hours | Outcomes destroyed or reduced |
|---|---|
| O3 (10.0) + O4 (9.0) = 19.0 | Two destroyed, **and still short** |
| O3 + O4 + O6 = 23.0 | **Three destroyed** |
| O3 + O4 + O2 extension = 25.0 | Two destroyed, one halved |
| O5 (8.0) + O4 + O2 extension = 23.0 | **Three damaged** |
| Anything avoiding O3, O4 and O5 | Caps at 14.0 hours. **Fails**, while already damaging three outcomes |

**Every combination that frees the required hours destroys or materially reduces at least three of the six fixed outcomes. No combination reaching the requirement leaves all six intact.**

Two observations make this worse rather than better. Reclaimed hours are credited at one to one, which overstates the yield, since deleted lab hours do not convert cleanly into lecture hours for foundational instruction. And the single largest block, the 11-hour Python foundation, is the block that produces the 9 BSP elements the course already covers, so spending it on BSP is a net-zero trade at best.

**The course also cannot simply be made larger.** At 2 lecture plus 2 lab it computes to 3.80 workload units. The contact hours required would push it to 2 lecture plus 4 lab at 5.60 units, or 3 lecture plus 3 lab at 5.70, both far outside the stated 3.9 ceiling. And enlarging it to 4 semester credit hours raises a degree already at exactly 60 to 61.

### 3.4 The assessment-integrity argument, which no redesign can fix

This one is independent of hours and sequencing.

**ITSY 1377 must permit AI assistance, for two reasons.** The first is access: the course has no programming prerequisite, and a blanket prohibition would fail most of a class that has never written code. The second is structural and stronger: **outcome 6 requires students to evaluate AI-generated code and output for correctness before use.** A course that forbids AI assistance cannot assess outcome 6, because outcome 6's object of study is AI-generated code. The permission is not a concession; it is load-bearing.

**BSP requires the opposite evidentiary posture.** Four of its six outcomes begin with the words "write and execute." An alignment review asks one question of any claimed outcome: which artifact demonstrates the student did this? In ITSY 1377 every code artifact is producible with AI assistance under an explicit course policy. **No artifact in the course distinguishes a student who can write a loop from a student who can request a loop and run the result.** Both submit the same file and both are correctly assessed for ITSY 1377's own outcomes, which concern automating, extending, testing, documenting, and evaluating rather than authoring. The artifact is sound evidence for outcomes 1, 2, and 6. It is not evidence for BSP, and it will not survive a reviewer who reads the syllabus AI policy alongside the knowledge unit claim.

**An AI-prohibited island inside an AI-permitted course does not work.** It fails on enforceability, because distinguishing assisted from unassisted work in a compressed asynchronous session requires proctoring that the schedule cannot absorb. It fails on coherence, because students would be told within the same week to use AI for one assignment and not another, in a course whose premise is that AI assistance is normal, and the justification lives in an accreditation document they never see. And it fails on risk, because a policy that counterintuitive will leak, and the exposure is the credibility of the whole mapping.

**This argument is why the carrier must be a course with a conventional AI policy**, and it applies equally to COSC 1436 and to a dedicated scripting course. A traditional programming course can produce clean, unassisted write-and-execute evidence as a normal course-level policy statement. ITSY 1377 cannot, by design, and should not try.

There is a benefit running the other way that is worth stating to the committee. **The unassisted foundation that BSP requires is precisely the preparation ITSY 1377's outcome 6 assumes.** A student who has personally written and debugged code is equipped to judge whether AI-generated code is correct. A student who has not is comparing one unfamiliar text against another and calling it evaluation.

### 3.5 Conclusion, in a form that can be pasted into a justification memo

> ITSY 1377 covers 9 of the 18 topic elements in the NSA Basic Scripting and Programming knowledge unit, which is 50 percent against a required 75 percent, and it cannot demonstrate two of that unit's six required outcomes at all: automating system administration tasks, and regular expressions. Bringing the course to the required standard would take an estimated 26 additional instructional hours in a 64-hour course that has already cut content to fit a seven-week session, and every combination of cuts large enough to free that time destroys or materially reduces at least three of the course's own six required outcomes. There is also a problem that no amount of time fixes: ITSY 1377 permits AI assistance on all coding by design, because it has no programming prerequisite and because one of its outcomes requires students to evaluate AI-generated code, so nothing produced in the course can serve as evidence that a student personally wrote and executed a script, which is exactly what the knowledge unit requires. The Basic Scripting and Programming unit must therefore be carried by a course with a conventional programming pedagogy and a conventional AI policy.

---

## 4. Mapping Against the Proposed 2027-2028 Plan

The plan changed substantially, and the analysis changes with it. What follows replaces the earlier mapping.

### 4.1 What the new plan does well

**Two of the three hardest gaps close outright.** The earlier analysis flagged AI Governance and AI Fundamentals as units with no home anywhere in the catalog. The new plan creates purpose-built carriers for both:

- **ITSY 2373 IT Governance, Regulation, and Compliance** is a natural and strong carrier for **AIG**. This is the easiest win in the plan.
- **ITSY 1371 AI Fundamentals** is a natural carrier for **AIF**.

Both are Local Need courses, so the college authors their outcomes. **That is the single biggest lever available**, and section 5 specifies what to write into them.

**The credit-hour problem is solved.** The plan totals exactly 60 SCH. COSC 1436 and the two-course Cisco sequence came out to make room.

**ITSC 2325 is now required rather than an OR-option**, which matters because an OR-option can never carry a knowledge unit.

### 4.2 What the new plan breaks

**There is no longer any programming or scripting course in the degree.** COSC 1436 is gone and no DSAI course is present, so both carriers the previous analysis relied on are unavailable. That puts Basic Scripting and Programming back in jeopardy, and this time the Linux sequence cannot rescue it.

### 4.3 The Linux sequence cannot carry BSP, and the reason is precise

This was the most promising hypothesis, and it fails on the evidence. **Across all eight WECM end-of-course outcomes for ITSC 1316 and ITSC 2325 combined, there is not one verb about writing, executing, or debugging a script.** No "write," no "script," no "automate." Neither course's WECM description mentions scripting.

| Course | WECM end-of-course outcomes, verbatim |
|---|---|
| **ITSC 1316** Linux Installation and Configuration | (1) Install, administer, and manage a Linux system. (2) Demonstrate proficiency with Linux utilities, commands, and applications. (3) Identify and resolve security-based issues. (4) Integrate a Linux system into an existing network. |
| **ITSC 2325** Advanced Linux | (1) Install, administer, and manage advanced network environment using a Linux system. (2) Demonstrate advanced skills and proficiency with Linux utilities and configurations. (3) Deploy secure networks. (4) Integrate Linux networks with existing networks. |

Shell scripting, regular expressions, permissions, and cron **are** taught in these courses at most colleges. Blinn's ITSC 1316 schedule lists "Scripting" in weeks 13 and 14; the standard Eckert textbook has a "Shell Scripts" section; Laredo builds ITSC 2325 on Red Hat RH134, which teaches writing bash scripts. **But none of it is in the state record.** It is local syllabus content, which means a different instructor can drop all of it and remain fully WECM-compliant.

That matters because the WECM Protocol Manual designates end-of-course outcomes as the "heart" of a course and the minimum "meant to be taught and measured." Resting a required knowledge unit on content that sits entirely below that line is exactly the weak position a reviewer probes.

**Two BSP items are not covered even locally:** input and parameter validation, and script debugging. Neither could be verified in any ITSC 1316 or ITSC 2325 syllabus.

**And the Windows half is a confirmed negative.** Neither ITNW 1308 nor ITNW 2405 covers PowerShell or any authored Windows scripting at outcome level. ITNW 1308's five WECM outcomes never mention scripting or automation; the closest ITNW 2405 outcome is "Utilize various operating system utilities and commands," which is command usage, not authored scripting. BSP element 6 requires **both** platforms explicitly.

### 4.4 The fix already exists in the WECM as a statewide course

**ITSC 1342 Shell Programming: Scripting** (3 SCH, statewide, already articulated at Collin and Dallas). Its WECM description reads:

> "Reading, writing, and debugging shell scripts. Development of scripts to automate frequently executed sequences of commands. Covers conditional logic, user interaction, loops, and menus to enhance the productivity and effectiveness of the user."

That single description puts **authored scripting, debugging, automation of repeated command sequences, conditional logic, and loops** into the state course record, where a reviewer can read them without depending on any one college's syllabus. It is close to a purpose-written answer to BSP Outcome 1, "write and execute simple scripts to automate system administration tasks."

Two adjacent statewide options exist if a different number suits better: **ITSC 1307 UNIX Operating System I**, whose WECM description includes "and writing script files," and **ITSC 2337 UNIX Operating System II**, whose description includes "scripting languages."

---

## 5. The Capacity Collision, Which Is the Real Blocker

**The plan as written fails validation, and not for the reason it looks like.**

With optimal local authoring, the plan carries 10 of 11 units. That still fails, because the unit it drops sits inside a block where **all** units are required. And the failure is not a content gap. It is a **capacity collision**: ITSY 1371 is structurally required to be two courses at once.

If ITSY 1371 must carry BSP (because nothing else can), it has to teach Python from zero, which costs four to five weeks. That displaces the machine learning content it also needs to carry:

| ITSY 1371 configuration | AIF coverage | MLF coverage | Verdict |
|---|---|---|---|
| AIF + MLF + Python for BSP | 7 of 7 | **10 of 14, 71%** | **MLF fails.** Python displaces neural networks, NLP, and generative AI |
| AIF + MLF, no Python | 7 of 7 | 11 of 14, 79% | Passes, but single-carrier and one disagreement from failure |
| **ITSY 1371 (classical) + ITSY 1377 (modern half)** | 7 of 7 | **14 of 14, 100%** | **Passes robustly, two carriers** |

The contact-hour arithmetic is blunt: AIF's seven topic areas take roughly five weeks, classical machine learning another five, neural networks two, and Python from zero another four to five. **That is 16 to 17 weeks of new content in a 16-week term with no room for assessment.** It does not fit at any lecture and lab coding, because the lab hours are already consumed by the machine learning work.

**So BSP must leave ITSY 1371. That is what unlocks everything else.**

---

## 6. The Single Smallest Change

> **Replace ITSC 2325 Advanced Linux (3 SCH) with ITSC 1342 Shell Programming: Scripting (3 SCH) in the Advanced Core.**

Why this change specifically:

- **Zero credit-hour cost.** Three out, three in. The plan stays at 60. Nothing else moves.
- **No THECB Local Need approval.** ITSC 1342 is a statewide WECM course, so adding it is an inventory action.
- **It puts BSP evidence into the state record**, rather than a local syllabus a reviewer must take on faith and a future instructor can silently drop.
- **It costs almost nothing pedagogically.** ITSC 2325's four outcomes carry **no knowledge unit that is not already carried elsewhere**: its Linux network administration content overlaps ITNW 2405 and ITSY 2301. It is the least unit-productive course in the plan.
- **It unlocks Machine Learning Fundamentals**, by removing the Python burden from ITSY 1371.

**Second best, if the committee will not drop Advanced Linux:** upgrade ITSY 1371 to a 4 SCH Local Need course and recover the hour by moving ITSY 2443 Forensics to a 3 SCH sibling. That costs a Local Need revision plus a second inventory change, and still leaves BSP resting entirely on locally authored text. Prefer the swap.

---

## 7. Carrier Map for the Proposed Plan

Assumes the ITSC 1342 swap and the local authoring in section 8. **Every unit has two or three carriers, every course carries three or fewer units, and every carrier is mandatory for all students.**

| KU | Primary carrier | Co-carriers | Fit | Evidence required |
|---|---|---|---|---|
| **ISC** IT Systems Components | ITNW 1308 | ITSC 1316, ITNW 2405 | **Strong** | Document the virtualization labs both courses already run; that is the only thin spot |
| **CSF** Cybersecurity Fundamentals | ITSY 1342 | ITSY 2301 | **Strong** | No action needed |
| **BSP** Basic Scripting and Programming | **ITSC 1342** | ITSC 1316, ITSY 1371 | **Strong once swapped** | Local syllabus must pin PowerShell alongside bash, regular expressions including sed and awk, and input validation |
| **MAF** Math Fundamentals | **MATH 1314, pinned** | ITSY 1371 | Partial until fixed | Requires both the pin and statistics outcomes in ITSY 1371. See section 9 |
| **AIG** AI Governance, Laws, Ethics | **ITSY 2373** | ITSY 2442 | **Strong** | Easiest win in the plan |
| **AIF** AI Fundamentals | **ITSY 1371** | ITSY 2373 | **Strong** | 7 of 7 topics as authored |
| **MLF** Machine Learning Fundamentals | ITSY 1371 | **ITSY 1377** | Strong only with both | Requires the split. See section 9 |
| **BNW** Basic Networking | ITNW 1425 | ITNW 2405 | **Partial** | **Subnetting and the TCP/IP model are absent** from ITNW 1425's statewide description and both published outcome lists. Needs a documented local addendum |
| **NDF** Network Defense | ITSY 2301 | ITSY 2430, ITSY 2442 | **Strong** | Best-covered unit in the plan |
| **AIS** AI for Security Assessment | **ITSY 1377** | ITSY 2443, ITSY 2442 | **Strong** | ENGL 1301 and SPCH 1321 are mandatory and named, so they support the reporting outcome, but cite them as supporting rather than as carriers |
| **DFA** Defensive Applications of AI | **ITSY 1377** | ITSY 2430, ITSY 2442 | **Strong** | **Elect DFA, not OFA.** There is no ethical hacking or penetration testing course anywhere in this plan, so OFA would have a single carrier in a degree titled Cyber Defense |

**Course load audit:** ITSY 1371 carries three (AIF, MLF, MAF), ITSY 1377 three (AIS, DFA, MLF), ITSY 2442 three (NDF, AIS, AIG). All others carry two or fewer. Nothing exceeds the ceiling.

---

## 8. What to Write Into the Three Locally Authored Courses

These are Local Need courses, so the college writes their outcomes. This is the cheapest lever in the whole package.

**ITSY 1371 AI Fundamentals** should carry AIF outright, the classical half of MLF, and the statistics that MAF needs: AI principles and terminology; classical search and optimization; knowledge representation and reasoning; intelligent agents; supervised, unsupervised, semi-supervised, and reinforcement learning; decision trees, support vector machines, k-nearest neighbors, clustering, dimensionality reduction, and overfitting; and descriptive statistics, probability, and elementary inferential methods. **Do not put Python fundamentals here**, and do not duplicate the governance content that belongs to ITSY 2373.

**ITSY 1377 Agentic AI and Security Operations** should carry AIS, DFA, and the modern half of MLF: transformer and large language model architecture with its lineage from convolutional and recurrent networks; natural language processing applied to security data; prompt engineering and fine-tuning; agentic workflows with tool calling and human-in-the-loop control; AI-enhanced security evaluation; vulnerability impact assessment and prioritized mitigation; threat modeling and attack-surface mapping; comprehensive assessment reporting; AI applied to anomaly detection, alert triage, and classification; and the risks specific to AI in security operations, including prompt injection, poisoning, hallucination, and unsafe autonomous action.

**ITSY 2373 IT Governance, Regulation, and Compliance** should carry AIG outright: COBIT, the NIST Cybersecurity Framework, and ISO/IEC 27001; US federal and state law including HIPAA, GLBA, and CCPA; the GDPR and the EU AI Act with their extraterritorial reach; the NIST AI Risk Management Framework and ISO/IEC 42001; fairness and bias, transparency, accountability, and non-discrimination; societal responsibility and human oversight; and compliance gap assessment.

**Keep ITSY 2373 as a Local Need course rather than substituting a statewide number.** ITSY 2341 Security Management Practices and ITSY 2359 Security Assessment and Auditing cover the cyber governance ground well, but **neither covers AI governance**. No WECM course in the ITSY rubric names the EU AI Act, the NIST AI RMF, ISO/IEC 42001, algorithmic bias, or AI transparency. This is the one place where a locally authored course is genuinely the right answer, and the submission should say so.

---

## 9. Math and Machine Learning, Specifically

### 9.1 Math Fundamentals has two blockers

**Blocker one: the slot cannot carry a unit at all.** "Mathematics, 1 course, MATH 1314 given as example" means a student may satisfy the degree with MATH 1332, MATH 1342, or MATH 1350. **A select-one slot carries nothing regardless of content**, because carriers must be mandatory for every student. This is definitional.

**Blocker two: even pinned, MATH 1314 fails on content.** Scored against the ACGM outcomes:

| MAF bucket | MATH 1314 | MATH 1342 |
|---|---|---|
| Algebra | Partial | No |
| Function analysis | Yes | No |
| Composition and inverses | Yes | No |
| Sequences and series | No (ACGM says these "may be included") | No |
| Descriptive statistics | No | Yes |
| Inferential statistics | No | Yes |
| Probability | No | Yes |
| **Score** | **3 of 7, 43%** | **3 of 7, 43%** |

**No single Texas ACGM mathematics course covers both halves**, because ACGM deliberately splits the algebra, statistics, and quantitative reasoning pathways. MATH 1314 and MATH 1342 are near-perfect complements, which is why the knowledge unit's own note says it is "likely covered by multiple math courses."

**The fix costs zero credit hours:** pin MATH 1314 by name in the degree plan rather than as an example; elect and document sequences and series in the local MATH 1314 syllabus, which the ACGM explicitly permits; and write descriptive statistics, probability, and elementary inferential methods into ITSY 1371. That reaches 7 of 7, or 6 of 7 if a reviewer discounts inferential statistics taught in a non-mathematics course. Either clears 75 percent.

**One institutional check is required, and it is the only place in this analysis where a unit could be genuinely lost.** Confirm that a program may narrow a core curriculum slot to a single named course. Most Texas institutions permit this; some forbid programs from restricting core options. **If MATH 1314 cannot be pinned, MAF cannot be carried**, because there is no in-major substitute for function composition and inverses. That is one email to the core curriculum office.

### 9.2 Machine Learning Fundamentals needs the split

Fourteen topics, so eleven are required. ITSY 1371 can reach eleven only if it is not also teaching Python. Adding ITSY 1377's transformer, natural language processing, and generative AI content brings it to fourteen of fourteen with two carriers.

**This is not a paper split.** ITSY 1377 genuinely cannot teach agentic AI without transformers, embeddings, prompt engineering, and fine-tuning. The two courses cover complementary halves.

---

## 10. Verdict

| Configuration | Units carried | Validates |
|---|---|---|
| Plan exactly as written, no local authoring | **5 of 11** | **No** |
| Plan as written, optimal local authoring only | **10 of 11** | **No.** Whichever of BSP or MLF loses the ITSY 1371 contest fails, and either loss kills a required block |
| **Plan + ITSC 1342 swap + MATH 1314 pinned + outcomes authored** | **11 of 11** | **Yes** |

**Does validation require a course change? Yes.** Local authoring alone is not sufficient, because the blocker is capacity rather than content.

**The total cost is one course substitution and one degree-plan pin.** No new Local Need approvals beyond the three courses already planned, no credit-hour growth, and no THECB new-course action.

---

## 11. Items to Resolve Before Submission

**A credit-hour discrepancy that will be caught.** The plan lists **ITSY 2430 Intrusion Detection at 3 SCH**, but under WECM numbering the second digit is the credit value, so 2430 denotes **4 SCH**. Every other course in the plan is internally consistent. The stated Advanced Core total of 22 and grand total of 60 hold only if it is 3 SCH. **If the number is right, the plan is 61 SCH and exceeds the cap. If the credit value is right, the number should be ITSY 2330**, which is the 3 SCH intrusion detection course in the statewide inventory. This does not affect any unit mapping, but it must be reconciled.

**A course number collision.** **ITSY 1371 is already in use in Texas under other titles**, including at Collin College ("OSINT and Introductory Security Analysis"). Local Need numbers are institution-scoped so this does not block the college, but it will collide in any articulation or transfer discussion. Consider a different number in the 1370 to 1379 band and confirm availability with the curriculum office. **ITSY 2373 appears unclaimed**, though that cannot be proven statewide because the THECB Local Need registry search is retired.

**A networking gap worth documenting.** **Subnetting and the TCP/IP model are absent** from ITNW 1425's statewide description and from both published outcome lists. Del Mar College's local description adds "protocols and subnetting," which shows colleges do this locally. Document a local addendum with graded lab artifacts. Note also that Del Mar's catalog states ITNW 1425 "does not fulfill CCNA requirements," so do not claim anything the Cisco sequence carried beyond Basic Networking.

**A sourcing caveat for the package.** **No WECM or ACGM outcome quoted in this analysis comes from a THECB-published source.** The THECB WECM interactive search application is retired: its form target returns HTTP 404 and the successor host does not resolve. Every outcome here is transcribed from college master syllabi, strongest where El Paso Community College publishes them under an explicit heading reading "THECB Learning Outcomes (WECM)," corroborated across six or more colleges with near-exact agreement. Three items should be confirmed with the curriculum office before submission: ITNW 1425's authoritative outcomes (two colleges publish five-item lists sharing almost no wording), ITSC 1342's end-of-course outcomes (the description is confirmed and is doing the heavy lifting for BSP, but the outcomes were not retrievable), and the two Local Need number questions above.
