# ITSY 2377 course design

The course rebuilt around the NCAE-C CyberAI knowledge units AIS and DFA.
Section 1 is locked: the outcomes and the knowledge unit mapping are agreed.
Everything after it is the architecture built to deliver them.

Renumbering from ITSY 1377 to ITSY 2377 follows from the prerequisite. Under
THECB rules the first digit is level, so 2 is sophomore standing; the second
digit is credit hours; a 7 in the third digit designates a Local Need course.
ITSY 2377 decodes as a sophomore, three credit hour, Local Need course, which
is what it becomes once a scripting course sits in front of it.

---

## 1. Outcomes and knowledge unit mapping (locked)

### 1.1 What this course is aligned to

Two knowledge units from the AI for Cybersecurity (AICyber) track of the
NCAE-C CyberAI Program of Study. Text quoted from
<https://dl.dod.cyber.mil/wp-content/uploads/cae/pdf/unclass-cyber_ai_kus_stoneman.pdf>.

**AIS, AI for Security Assessments.** All four outcomes are carried.

1. Conduct security evaluations using AI enhancements to standard tools and techniques
2. Produce comprehensive reports with actionable recommendations
3. Leverage AI to assess the impact of identified vulnerabilities and design and implement mitigation strategies
4. Perform threat modeling and develop mitigation strategies, including mapping attack surfaces and developing comprehensive threat models

**DFA, Defensive Applications of AI.** Outcomes 3 and 4 are carried here.
Outcomes 1 and 2 are carried by the AI Fundamentals course, by program
decision, because they require developing and applying machine learning
models and this course has no machine learning library.

3. Understand frameworks like MITRE ATLAS for AI-driven cyber threat intelligence
4. Understand Explainable AI-driven cybersecurity solutions

### 1.2 The six course outcomes

On completion of ITSY 2377, a student will be able to:

| | Outcome |
|---|---|
| **CO1** | Map the attack surface of an agentic AI system and produce a threat model naming each untrusted input, each privileged action, and the trust boundary between them. |
| **CO2** | Use a language model as an assessment instrument to draft test cases, surface inventories, and impact assessments, and verify every item it produces against the target before acting on it. |
| **CO3** | Execute a repeated-trial test harness against an authorized target and interpret its results, including rates, flaky outcomes, and inconclusive verdicts. |
| **CO4** | Build an AI-assisted detection step over assessment evidence, measure it against a labeled reference set using precision and recall, and state what it cannot be trusted to decide. |
| **CO5** | Classify findings and threat intelligence using MITRE ATLAS and OWASP identifiers, verified against the published catalogs. |
| **CO6** | Produce an assessment report in which every claim traces to a recorded check, and implement one mitigation that stops the attack without breaking benign function. |

Every outcome is measurable by an artifact a reviewer can open. The words
"understand" and "be familiar with" do not appear, because a knowledge unit
reviewer asks what the student produced, not what they were exposed to.

### 1.3 The mapping, both directions

| Course outcome | Knowledge unit outcome |
|---|---|
| CO1 | **AIS 4** threat modeling and attack surface mapping |
| CO2 | **AIS 1** AI enhancements to standard techniques; **AIS 3** first half, leverage AI to assess impact |
| CO3 | **AIS 1** conduct security evaluations; AIS topic 1, security assessment methodologies |
| CO4 | AIS topic 2, monitoring and detection leveraging AI; **DFA 4** explainable AI |
| CO5 | **DFA 3** MITRE ATLAS for threat intelligence; AIS topic 3a, taxonomy of attacks and defense |
| CO6 | **AIS 2** comprehensive reports; **AIS 3** second half, design and implement mitigations |

Reverse check, so no knowledge unit outcome is left without a carrier and no
course outcome exists without a purpose:

| KU outcome | Carried by |
|---|---|
| AIS 1 | CO2, CO3 |
| AIS 2 | CO6 |
| AIS 3 | CO2, CO6 |
| AIS 4 | CO1 |
| DFA 3 | CO5 |
| DFA 4 | CO4 |

### 1.4 Coverage, stated honestly

All six in-scope knowledge unit outcomes are carried. Four are clean. Two
carry qualifications that belong in the submission rather than in a footnote:

- **AIS 1** enhances assessment *techniques* with AI. It does not enhance a
  recognised commercial security tool, and a reviewer looking for that will
  not find it.
- **DFA 4** explains a prompted language model classifier using attribution
  computed from the system's own recorded behaviour. Students do not use the
  SHAP or LIME libraries, do not see kernel or tree approximations, and do not
  explain a trained model with learned features. Against the outcome as
  written this is Full; against the topic list it is Partial, and it should be
  claimed as Partial at the topic level. The library work belongs with DFA
  outcomes 1 and 2 in AI Fundamentals.

Topic coverage is weaker than outcome coverage, which matters less than it
appears: knowledge unit outcome alignment is listing only with no assessment
of outcomes, and topics are recommended rather than required. Two topics are
Partial for reasons no course-level redesign fixes. AIS topic 1 describes
"methodologies for assessing organizations" and this course assesses one
system. DFA topic 3 gets MITRE ATLAS in full, the NIST Risk Management
Framework thinly, and malware analysis and reverse engineering not at all.

What would actually damage a submission is claiming Full where a reviewer can
open an artifact and see otherwise. That is what happened to the earlier
three-unit claim, and the ratings above are written to avoid repeating it.
---

## 2. The architecture

### 2.1 Spine

**The course is one authorized security assessment of an agentic AI system,
run end to end, in which a language model is the analyst's instrument at every
step and every one of its outputs must be verified before it is used.**

Two things run the length of the course and hold it together.

**The instrument is never trusted.** The model drafts the surface inventory,
the test plan, the triage verdicts, the impact ratings and the mitigations.
The student verifies each one against the target and records the accept or
reject decision with a reason. This is what makes AIS outcomes 1 and 3
evidenced rather than asserted, and it teaches the discipline the subject
actually requires: an assessor who believes their tools writes false findings.

**A MITRE ATLAS technique identifier is the join key.** One identifier follows
a threat from published intelligence, into the threat model, into a test case,
into a detection rule, into a mitigation. A reviewer can pull any single
identifier and follow it through five artifacts. That is what turns DFA 3 from
a label into a structure, and it is the idea worth taking from the
threat-intelligence design.

The target under assessment is an agentic helpdesk: a language model with
tools, acting on tickets, with a knowledge base and an email capability. The
course stays recognisably about **agents** rather than about AI in general,
which is a program requirement, and it is also what makes the attack surface
concrete enough for a sophomore to enumerate: a tool registry, three untrusted
input channels, and an authorization boundary around each tool.

### 2.2 What changed, and why

| | Old | New |
|---|---|---|
| Weeks 1 to 4 | Build an agent | **Prerequisite.** Python and API work move to the scripting course |
| Weeks 5 to 7 | Attack it, then fix it | Assessment runs the whole term |
| The model | Mostly the simulator; one live call all term | **Live model required**, with a fixtures fallback carrying a stated grade cap |
| Explainability | A caveat inside week 7 | A week of its own, and a course outcome |
| ATLAS | Metadata in case files | The join key across five artifacts |

The live model point is the one that decides whether AIS can be claimed at
all. The current course defaults to `provider: mock` and its Module 4
explicitly requires the simulator for its before and after runs, so a student
can finish having made one live model call. A knowledge unit whose verb is
*leveraging* cannot rest on that.

### 2.3 Weeks

Seven instructional weeks, Monday to Sunday, plus a six day final block.

| Week | Title | What the student does | Artifact | Outcome |
|---|---|---|---|---|
| **1** | Scope and baseline | Seed the target with their own ID, which plants their canary tokens. Read one full agent trace and label every step. Turn the rules of engagement into code by completing the authorized-target check, then prove it refuses a plausible decoy host and records the refusal | Rules of Engagement gate at 100 percent; refusal log; baseline harness run | CO3 |
| **2** | Map the attack surface | Ask the model to enumerate the agent's tools, inputs and trust boundaries. Verify every line against the target's actual code. Record accept or reject with a reason | `surface.yaml`; `claims.jsonl` with one verification row per proposed item | CO1, CO2 |
| **3** | Name the threats | Read short excerpts of public reporting on attacks against AI agents. Use the model to propose ATLAS identifiers, then validate each against the offline catalog. Build the threat model and risk register: source, path, privileged action, impact, likelihood, risk, planned test | `threat-model.yaml`; `atlas-adjudication.csv` scoring the model's proposals | CO1, CO5 |
| **4** | Let the model write the test plan | The model drafts test cases as **structured output validated against the case schema**. The student accepts, repairs or rejects each, then runs them at five trials and compares predicted verdicts with observed ones | Student-authored `cases/*.yaml`; `plan-verification.jsonl`; calibration score | CO2, CO3 |
| **5** | Detection, with and without AI | Write three deterministic detection rules over their own run evidence. Build an AI triage step. Score both on the same labeled corpus: true and false positives and negatives, precision, recall | `rules.py`; `triage.py`; `metrics.json` with two confusion matrices | CO4 |
| **6** | Why did it say that? | Define binary evidence features extracted from the trace. Run leave-one-out occlusion over the AI triager, compare against the interpretable rule detector, and write what the AI detector cannot be trusted to decide | `explanation.json`; the side-by-side comparison | CO4 |
| **7** | Impact and mitigation | The model proposes impact and two mitigations per finding. The student checks each against the outbox, beacon and ledger, then implements one control and reruns the suite, including held-out benign cases | `impact.jsonl`; the implemented control; paired before and after reports | CO2, CO6 |
| **Final** | The report | A security assessment report where every claim traces to a recorded check, plus a written account of where the instrument was wrong during the term | The report; `claims.jsonl` linker run clean | CO6 |
### 2.4 Three fixes the review forced

The judged designs each failed somewhere. These are the corrections carried
into the architecture above, recorded so nobody reintroduces them.

**Structured output, not free-text parsing.** Two designs asked students to
parse free-form model output. The reviewer's objection was decisive: the
failure mode is silent, so labels are quietly wrong; the feedback loop is slow
at roughly two hundred model calls per iteration; and the student cannot tell
whether their parser is broken or the model was moody. The model is therefore
asked for JSON validated against a schema, using the `jsonschema` library the
environment already has. The failure becomes loud, the student debugs a
contract rather than a regular expression, and it matches what real agent
systems do.

**Week 4 needs an answer key.** As designed, the drafts being verified are
generated fresh inside each student's session, so "reject anything with no
deterministic success criterion" could not be scored against anything. The fix
is that the harness itself is the key: a case the student accepted either
loads against the schema and runs, or it does not, and a case they rejected
can be checked for the stated reason. Verification is graded on whether the
recorded decision matches what the harness later did.

**Attribution from traces, not from SHAP.** The libraries are forbidden and
always will be. Leave-one-out occlusion over binary features extracted from an
agent's own trace is the real mechanism, computed by definition rather than
approximated, and it needs no library. It is also more agentic: an execution
ledger of tool calls, arguments and allow-or-deny decisions **is** an
interpretable representation, which is DFA topic 5c, and it sidesteps the
problem that a prompted classifier has no learned features to attribute to.

### 2.5 What survives from the existing course

Arrived at independently, after the designs were judged, rather than by
starting from what exists.

| Survives | Why |
|---|---|
| The harness: YAML cases, five trials, deterministic verdicts, detector self-test | It is the assessment methodology AIS topic 1 asks for, and nothing in the four designs improved on it |
| `AUTHORIZED_TARGETS` enforced in the runner | Scope refusal recorded as evidence rather than asserted in prose. Week 1 is built on it |
| Per-student canary tokens | They make evidence unforgeable and assessment anchored to the student's own run, which is what keeps AI assistance permitted but unprofitable |
| The agentic target itself: helpdesk, tools, tickets, knowledge base | Still the right subject, and the program requires the course stay agentic |
| The findings report template and its rubric | AIS 2 is already the course's strongest element |
| The poisoned-results exercise | Becomes the seed of week 6 rather than a week 7 aside |

| Retired | Why |
|---|---|
| Weeks 1 to 4 of agent construction | Moves to the scripting prerequisite. This is what funds the new material |
| Outcomes O1 and O2 | Same reason |
| The mock as the graded path | Kept as a fallback with a stated grade cap, never as the default |
| "Break It" and "Fix It" module naming | The course is an assessment, not a demolition |

### 2.6 Open questions

1. **Does the scripting prerequisite actually land, and is it ITSE 1359?**
   Everything here depends on it. Addendum D of the knowledge unit analysis
   already costs ITSE 1359, and it would carry Basic Scripting and Programming,
   a required AICyber foundational unit currently without a home. One decision
   settles two problems.
2. **Which model, and hosted or local?** Requiring live model use raises cost,
   privacy and reliability questions the current course avoids by defaulting to
   the simulator. Measured earlier: a 3B local model is reliable for some
   assessment steps and not others.
3. **Does week 5 fit?** It was the most-criticised week in every design.
   Building two detectors and scoring both against a labeled corpus in seven
   days is the heaviest single week here.
4. **Renumbering.** ITSY 2377 needs the curriculum process, and the number
   should be confirmed as available in the Local Need block.
---

## 3. Assessment plan

One thousand points, matching the existing course so the two can be compared,
across three groups that follow the phases of the assessment rather than the
old build-then-break split.

### 3.1 The plan

| Item | Due day | Points | Scoring | Course outcomes |
|---|---|---|---|---|
| **Phase 1: Scope and model the target** | | **300** | | |
| Rules of Engagement gate | 3 | 40 | auto, 100 percent required to unlock week 2 | CO3 |
| Lab 1: Baseline and refusal evidence | 7 | 60 | auto | CO3 |
| Lab 2: Attack surface, drafted and verified | 14 | 90 | mixed | CO1, CO2 |
| Lab 3: Threat model and ATLAS adjudication | 21 | 80 | mixed | CO1, CO5 |
| Comprehension 1, weeks 1 to 3 | 21 | 30 | auto | CO1, CO3, CO5 |
| **Phase 2: Test and detect** | | **350** | | |
| Lab 4: Model-drafted test plan, verified | 28 | 100 | mixed | CO2, CO3 |
| Lab 5: Two detectors, measured | 35 | 110 | mixed | CO4 |
| Lab 6: Explanation and trust boundary | 42 | 90 | mixed | CO4 |
| Comprehension 2, weeks 4 to 6 | 42 | 50 | auto | CO2, CO4 |
| **Phase 3: Impact, mitigation, report** | | **350** | | |
| Lab 7: Impact and mitigation, implemented | 49 | 110 | mixed | CO2, CO6 |
| Final Part A: comprehensive exam | 54 | 100 | auto | all six |
| Final Part B: assessment report | 54 | 140 | hand read | CO6 |
| **Total** | | **1000** | | |

Group weights: Phase 1 at 30 percent, Phase 2 at 35 percent, Phase 3 at 35
percent. The report is the single heaviest item at 140 points because it is
the whole evidence for AIS outcome 2 and half the evidence for AIS 3.

### 3.2 Every outcome assessed at least three times

| Outcome | Graded sources | Count |
|---|---|---|
| CO1 threat model and attack surface | Lab 2, Lab 3, Comprehension 1, Final A | 4 |
| CO2 model as instrument, verified | Lab 2, Lab 4, Lab 7, Comprehension 2, Final A | 5 |
| CO3 harness and interpretation | Gate, Lab 1, Lab 4, Comprehension 1, Final A | 5 |
| CO4 detection, measured and explained | Lab 5, Lab 6, Comprehension 2, Final A | 4 |
| CO5 ATLAS and OWASP classification | Lab 3, Comprehension 1, Final A | 3 |
| CO6 report and mitigation | Lab 7, Final B, Final A | 3 |

The exam carries item-level outcome tags, so its export is a per-student,
per-outcome score matrix. That is what a program assessment cycle asks for,
with no extra instrumentation.

### 3.3 What a knowledge unit reviewer can open

Each knowledge unit outcome has one artifact that evidences it, produced by
every student and inspectable without the instructor's interpretation.

| KU outcome | The artifact |
|---|---|
| AIS 1, evaluations using AI enhancements | `plan-verification.jsonl`: every model-drafted case with an accept or reject decision, a reason, and the harness verdict that later confirmed or refuted it |
| AIS 2, comprehensive reports | The Final Part B report, plus a clean `claims.jsonl` linker run proving no claim is uncited |
| AIS 3, leverage AI for impact and mitigation | `impact.jsonl`: the model's proposed impact and mitigations, the check the student ran, the verdict, and the implemented control with paired before and after harness reports |
| AIS 4, threat modeling and attack surface | `surface.yaml` scored against the target's true inventory, and `threat-model.yaml` with one row per flow |
| DFA 3, MITRE ATLAS | `atlas-adjudication.csv`: every model-proposed identifier, whether it exists in the catalog, accepted or rejected, and why |
| DFA 4, explainable AI | `explanation.json`: the occlusion results, the comparison against the interpretable rule detector, and the written statement of what the AI detector cannot decide |

### 3.4 Auto-scoring, and where it stops

Roughly 69 percent of points are machine scored, against 73 percent in the
existing course. The drop is deliberate and it is concentrated in one place:
**the reasons students give for accepting or rejecting what the model
produced.** That judgment is the course, and it cannot be scored by a
validator.

What machines score: schema validation on every YAML and JSONL artifact;
whether an accepted case actually loads and runs; whether a rejected case
would in fact have failed; whether every ATLAS identifier exists in the
catalog; whether the confusion matrix arithmetic matches the labels; whether
the before and after harness reports show the claimed movement; whether every
claim in the report links to a check that passed.

What a human reads: the verification reasons, the threat model's judgment
calls, the statement of what the detector cannot be trusted to decide, and the
report itself.

**This raises instructor load and the design should say so.** The existing
course lands at about five hours of hand-reading across the term. This one is
higher, because verification reasons appear in four labs rather than one
report. Two mitigations are available and both should be decided before the
first offering: score verification reasons on a three-level rubric row rather
than line by line, and sample rather than read every row where a lab has more
than ten.

### 3.5 Why AI assistance stays permitted but unprofitable

Unchanged in principle from the existing course, and stronger in practice.
Every artifact is anchored to the individual student's run: their canary
tokens, their seeded target variant, their model's drafts, their harness
verdicts. A classmate can hand over a working payload, which is fine and is
how the field works. They cannot hand over the proof that it worked in
someone else's environment.

The course now goes further, because the assignment is not "produce an
answer" but "decide whether this answer is right and say why". A student who
asks a model to write their verification reasons is asking one instrument to
audit another, which is exactly the failure the course is about, and the
harness will contradict them where they are wrong.
---

## 4. Infrastructure delta

What exists, what is reused, what has to be built. Line counts are measured
from the current lab repository, not estimated.

### 4.1 Reused as it stands

More survives than the re-architecture suggests, because the assessment
machinery was always the strongest part of the course and the new design puts
it at the centre instead of at the end.

| Component | Size | Role in the new course |
|---|---|---|
| `harness/runner.py` | 717 lines | Unchanged. The assessment instrument, weeks 1, 4 and 7 |
| `harness/detectors.py` | 407 lines | Unchanged. Four detector tiers with the recipient-naming fix already applied |
| `harness/report.py` | 342 lines | Unchanged. Verdicts, rates, flaky and inconclusive handling |
| `harness/selftest.py` | 268 lines | Unchanged. 29 probes. The model for how week 5 teaches detector validation |
| `harness/schema/case.schema.json` | | **Load bearing.** Week 4's model drafts are validated against it, which is what makes structured output work |
| `agent/trace.py` | 170 lines | **Promoted.** Its ledger becomes the interpretable representation week 6 explains |
| `agent/loop.py` `before_tool_call` | | Unchanged. Week 7's control still goes here |
| `target/` app, seed, audit | 547 lines | Unchanged. The agentic target, its canaries and its audit log |
| `common/canary.py` | 84 lines | Unchanged. Per-student tokens are what make evidence unforgeable |
| `AUTHORIZED_TARGETS` in the runner | | Week 1 is built directly on it |
| `harness/fixtures/poisoned-results.json` | | Seeds week 6 instead of being a week 7 aside |

Roughly 2,300 lines of tested infrastructure carry over untouched. The
rewrite is in the course, not the lab.

### 4.2 To build

Seven new pieces, ordered by the week that needs them.

| # | What | For | Notes |
|---|---|---|---|
| 1 | **Target inventory extractor** | Week 2 | Emits the true tool registry, endpoints, untrusted input paths and trust boundaries from the target's own code, so `surface.yaml` can be scored automatically rather than read. Small: the data is already in `TOOLS` and the Flask routes |
| 2 | **Offline ATLAS catalog** | Week 3 | A pinned JSON of technique identifiers, names and tactics, shipped in the repo. Every student identifier is validated against it. Must be offline, since the course makes no outbound calls except to the model endpoint |
| 3 | **CTI excerpt corpus** | Week 3 | Six to twelve short excerpts of public reporting on attacks against AI agents, each with an instructor key of correct ATLAS identifiers. This is authoring work, not code |
| 4 | **`assist.py`, the instrument** | Weeks 2, 4, 5, 7 | One student-facing module that calls the model and returns **schema-validated JSON**, never free text. Prints what it will send before sending. Writes a provenance header naming model, endpoint, timestamp and prompt. Refuses to write into `harness/cases/`, `agent/` or `config/` |
| 5 | **Labeled benign corpus** | Week 5 | Around sixty benign agent traces to serve as the negative class, so precision and recall mean something. Generatable from the existing agent by scripting ordinary helpdesk tasks |
| 6 | **Occlusion driver** | Week 6 | Runs the student's triage step with one evidence feature removed at a time and records the flips. Perhaps forty lines, no libraries |
| 7 | **Claims linker** | Final block | Checks that every claim in the report cites a check, and that every cited check passed. Turns "comprehensive report" from a rubric adjective into a machine-verified property |

### 4.3 To change

| What | Change | Why |
|---|---|---|
| `config/lab.config.yaml` | Live provider becomes the default; `mock` becomes an explicit fallback | AIS cannot be claimed on a course a student can finish with one live model call |
| `demo/apply_solution.py` | Retire, or repurpose | It exists to hand students a built agent. They now arrive with the skills instead |
| `tests/test_module1..4.py` | Rewrite | They grade agent construction, which has moved to the prerequisite |
| `harness/cases/` shipped set | Keep as worked examples, not as the graded set | Students now author cases from model drafts in week 4 |

### 4.4 What the target system gains

The target stays the same agentic helpdesk. Three additions, all small, all
serving specific weeks.

- **A seeded variant per student.** The seed already plants per-student
  canaries; extend it to select one of four misconfiguration variants, so two
  students do not have the same attack surface to map in week 2.
- **Benign traffic generation.** A script that drives ordinary helpdesk work
  through the agent, producing the negative class week 5 needs.
- **Nothing else.** The target is deliberately not made harder. The course
  gets its difficulty from the assessment, not from the target.

### 4.5 Content, which is the real cost

The lab is mostly reuse. The course is mostly rewrite.

| | Existing | Fate |
|---|---|---|
| Authored pages | 74 | Perhaps 20 survive: rules of engagement, glossary, findings template, reading results. The rest are about building an agent |
| Videos | 17, 66 minutes | Most are rebuilt. The staleness gate will name them |
| Quizzes | 6, 350 points | Rewritten. Items reference specific case files and line numbers that move |
| Rubrics | 10 | Rewritten around verification reasons rather than construction |
| Cartridge and Canvas import | working | Unchanged mechanically; new content flows through it |

**The honest summary: about 2,300 lines of lab code carry over, and most of
the 74 pages do not.** That is the correct ratio for a re-architecture, and it
is worth stating plainly to anyone who assumes the course is being tweaked.
---

## 5. Runtime and access

The course must be completable at zero cost to the student and zero budget to
the program, by three kinds of student: one with their own computer, one on a
free cloud instance, and one on a school loaner running Windows 11 with no
administrator rights. Everything below was verified against official
documentation on 31 August 2026 and should be re-checked before each offering,
because free tiers move.

### 5.1 The three paths

| | Student A, own computer | Student B, free cloud | Student C, locked-down loaner |
|---|---|---|---|
| Labs | Native Python, Windows or macOS | Native Python on the instance | **Native Windows Python** |
| Install | pip, or the offline wheel bundle | pip | **Microsoft Store Python plus the wheel bundle, no admin needed** |
| Model | Ollama or llama.cpp locally | Same | **Codespaces, for inference** |
| Cost | none | none | none |

**The labs themselves are portable and this was designed in, not discovered.**
An audit of the lab code found no POSIX-only imports, no `os.fork` or POSIX
signals, no hardcoded `/tmp` or `/usr` paths, no `os.chmod`, no filesystem
paths built by string concatenation, and no `open()` or `read_text()` without
an explicit encoding, which is the usual way a Unix-written program breaks on
a Windows machine that defaults to cp1252. Fourteen files use `pathlib`. No
lab code references Docker. All 26 pinned dependencies are pure Python or
universally wheeled, so nothing compiles.

`scripts/build_wheels.py` already builds an offline bundle for Windows, macOS
and Linux, and its docstring names the exact student this constraint set is
about: "Some college lab images block PyPI outright. A student who cannot
install anything in week 1 does not fall behind, they withdraw."

### 5.2 GitHub Codespaces, with the numbers corrected

| | Free personal account | Verified student, Education pack |
|---|---|---|
| Compute | 120 core-hours per month | 180 core-hours per month |
| On a 2-core machine | **60 wall-clock hours per month** | **90 wall-clock hours per month** |
| Storage | 15 GB-month | 20 GB-month |
| Payment method | not required, and cannot be charged | not required |
| Minimum age | 13 | 13 |

A student working eight hours a week uses roughly 35 of the 60 hours in a
month, so the free tier is adequate with headroom. The seven harness runs the
course requires account for under six core-hours across the whole term, so the
labs are not what consumes the allowance: **Codespaces bills wall-clock
uptime, not compute**, so it is the sitting and thinking that costs.

Three things follow. Keep reading, writing, threat modelling and report
drafting outside the billed environment; the environment is for running.
**Do not set a minimum machine specification in the devcontainer**, because it
would force students onto a 4-core machine and halve their effective budget.
And note the failure mode honestly: exceeding either compute or storage blocks
new and existing codespaces until the cycle resets, though work in progress
can still be exported to a branch, and with no payment method on file a
student can never be charged. GitHub's own framing is worth quoting to
students: the free allowance "is not intended to be enough for you to do
everyday work free of charge".

### 5.3 Why the model runs locally

Hosted free APIs were assessed and rejected, on two independent grounds.

**Rate limits.** OpenRouter allows 50 requests per day on free models without
a credit purchase. One full harness run is about 116 model calls, measured
from 40 recorded traces at a mean of 2.9 calls per agent run. A student could
not complete a single lab in a day.

**Age.** Google's API terms state "You must be 18 years of age or older to use
the APIs". Cloudflare states its services are "not intended for, nor designed
to attract, individuals under the age of eighteen" and that it deletes the
data of anyone under eighteen it becomes aware of. Dual-enrolment students are
precisely who that strands, and a course cannot have a path that excludes some
of its own students by age.

So the model runs locally, served over the same OpenAI-compatible chat
completions API a hosted provider would offer, which means `agent/llm.py`
needs to know nothing about which path a student took.

### 5.4 Model licences: three are clean, one would strand students

| Model | Licence | Gated | Usable |
|---|---|---|---|
| Qwen3-1.7B, Qwen3-4B | Apache 2.0 | no | **yes** |
| Granite 4.1 3B | Apache 2.0 | no | **yes** |
| Phi-4-mini | MIT | no | **yes** |
| Llama 3.2 3B | Llama 3.2 Community License | **manual review** | **no, do not require** |

Llama must not be a requirement. Its Hugging Face gate is set to manual human
review that can be delayed or denied, and a student stuck at that gate cannot
do the lab. The licence is also bespoke rather than permissive, which fails
the program's open-source condition. The three Apache and MIT models are
ungated and need no account at all.

### 5.5 What is not yet verified

Recorded rather than glossed, and deferred by decision.

1. **The labs have not been executed on Windows.** The evidence above is a
   static audit plus the code's own declared intent. Untested: Microsoft Store
   Python resolving `python -m` invocations as the labs expect, whether IT
   policy blocks the Store itself, and long-path behaviour if a student clones
   deep inside `OneDrive\\Documents`.
2. **Inference for student C.** Their labs run locally but a model may not:
   Ollama needs an installer, and a bare llama.cpp binary can be stopped by
   AppLocker or Defender Application Control. Codespaces covers this today,
   and it is the one place that student depends on a quota.
3. **Gitpod is gone.** `gitpod.io/pricing` now redirects to `ona.com/pricing`,
   minimum twenty dollars a month, with Gitpod Classic sunset. It should not
   appear in any planning document as a free option.

The cheapest way to close items 1 and 2 is one loaner laptop, Store Python,
the offline wheel bundle, and a full test-suite run. That is roughly half an
hour and it settles everything except whether a model can be served on the
device.
---

## 6. Content build

What has to be authored, week by week, on the four-part page anatomy the
college template requires: an Overview, a Content page, the graded
Assignments, and a Wrap-up. Counts are measured against the current course,
which ships 45 pages, 18 scene lists and 17 built videos.

### 6.1 What carries over without rewriting

Twenty of the 45 pages are course-shell rather than subject matter, and they
survive a change of subject intact: welcome and navigation, course policies,
the schedule, academic integrity, communicating online, tech support, support
resources, tips for success, meet your instructor, and the instructor notes.
Four more survive on merit rather than by default:

| Page | Why it survives |
|---|---|
| `rules-of-engagement.md` | Week 1 is built on it, and the runner enforces it in code |
| `findings-report-template.md` | AIS outcome 2 is the course's strongest element and this is its instrument |
| `glossary.md` | Mostly still accurate; needs entries for threat model, precision, recall, occlusion |
| `ai-use-policy.md` | Needs extending, not replacing: the course now *requires* AI use and grades the verification of it |

That leaves roughly 21 subject pages to author, against 25 retired.

### 6.2 The build, week by week

Each week is one Overview, one Content page, one Wrap-up, one assignment page,
and one concept video. Walkthrough videos are marked where a week needs one.

| Wk | Content page teaches | Assignment page | Video | New infrastructure it depends on |
|---|---|---|---|---|
| 1 | What an agent is, what a trace records, and why scope is written in code rather than promised | Lab 1: baseline and refusal evidence | Concept + walkthrough | none |
| 2 | Attack surface of an agentic system: tool registry, untrusted input channels, trust boundaries. How to verify a model's claims against source | Lab 2: surface, drafted and verified | Concept | inventory extractor; `assist.py` |
| 3 | Threat modelling for agents, and reading threat intelligence in a shared taxonomy | Lab 3: threat model and ATLAS adjudication | Concept | ATLAS catalog; CTI excerpt corpus |
| 4 | Why a schema makes a model's output checkable, and what a five-trial rate means | Lab 4: model-drafted test plan, verified | Concept + walkthrough | `assist.py` structured output mode |
| 5 | Detection: what a rule proves, what a classifier proves, and how precision and recall differ | Lab 5: two detectors, measured | Concept + walkthrough | labeled benign corpus |
| 6 | Explaining a decision from behaviour rather than from intent; the limits of an AI judgment | Lab 6: explanation and trust boundary | Concept | occlusion driver |
| 7 | Impact, severity, and why a control that breaks benign use is not a fix | Lab 7: impact and mitigation | Concept + walkthrough | none |
| Final | Assembling an assessment report whose every claim is traceable | Final A exam, Final B report | Concept | claims linker |

**Eight concept videos and four walkthroughs, so twelve against the current
seventeen.** The reduction is real: the current course spends four videos on
agent construction, which moves to the prerequisite.

### 6.3 Order of work

Content cannot be authored before the infrastructure it demonstrates, because
the course's own gate requires that every command shown on a page resolves in
`labs/`, and every walkthrough records a real terminal.

1. **Infrastructure first**, in the order section 4.2 lists it. Weeks 1 and 7
   need nothing new, so they can be authored immediately and act as the
   template for the rest.
2. **Author weeks 1 and 7**, then use them to settle voice, page length and
   the shape of a lab page before committing to five more.
3. **Build `assist.py` next**, because weeks 2, 4, 5 and 7 all depend on it
   and its output shape determines what those pages can claim.
4. **Weeks 2, 3, 4** follow, then **5 and 6**, which are the hardest and
   should be authored last when the instrument is settled.
5. **Videos last, per week**, because the staleness gate marks a video stale
   by name the moment its page changes, and authoring pages after videos wastes
   renders.
6. **Quizzes and rubrics alongside each week**, not in a batch at the end. The
   items reference specific files and line numbers, so they rot if written
   against content that is still moving.

### 6.4 The honest size of this

| | Count |
|---|---|
| Pages to author | ~21 |
| Pages retired | ~25 |
| Pages carried over | ~24 |
| Videos to build | 12 |
| Videos retired | 17 |
| Quizzes to rewrite | 6, 350 points |
| Rubrics to rewrite | 10 |
| New lab modules | 7 |
| Lab code carried over | ~2,300 lines |

This is a course rebuild with a lab refit, not a revision. The thing that
makes it tractable is that the assessment machinery, which is the expensive
part to get right, is already built and tested and moves to the centre of the
course rather than being replaced.
---

## 7. Migration

A migration plan is necessary, for one reason that has nothing to do with
content: **the current course is deployed and importable**, and the mechanism
that puts it into Canvas has properties worth preserving rather than
rediscovering.

### 7.1 What must not be lost

| | Why it matters |
|---|---|
| The cartridge build and import path | Works, is idempotent across repeated imports, and carries 126 MB of media inside the 500 MB course quota |
| The preflight gates | Seven gates including reading level, content-agrees-with-code, no-answers-in-the-student-repo, and video staleness. They are what keep the rebuild honest |
| The video pipeline | Authored scene lists, measured narration, captions correct by construction. Rebuilding twelve videos costs render time, not authorship of the machinery |
| Per-student canary derivation | The reason assessment is anchored to an individual run |
| The two-repository split | `labs/` is its own repository and ships to students without the answers; `scripts/build_student_repo.py` enforces that |

### 7.2 Sequence

The old and new courses cannot share a branch, because the preflight gates
check the whole tree and a half-migrated tree fails all of them.

1. **Branch.** `itsy2377` off `main`. The current course stays on `main` and
   remains deliverable, which matters if the re-architecture slips past a
   term boundary.
2. **Retire in one commit, not gradually.** Delete the 25 retired pages, the
   17 scene lists and the four agent-construction modules together. A tree
   half-converted fails the content-agrees-with-code gate in ways that are
   confusing rather than informative.
3. **Land the lab infrastructure** before any page references it.
4. **Author, week by week**, in the order section 6.3 gives.
5. **Rebuild videos last.**
6. **Import into a second Canvas course**, not over the top of the existing
   one. Canvas renames files on collision rather than replacing them, which
   has already caused this project to serve stale media for three imports
   before anyone checked a hash.
7. **Run the full preflight and the import verifier**, which reads the course
   back through the API and checks it against `course.yaml` rather than
   trusting the migration's own report.

### 7.3 What blocks a start

Two things, and neither is technical.

**The scripting prerequisite has to be real.** Everything in sections 2
through 6 assumes students arrive able to write Python. If ITSE 1359 or an
equivalent does not land before this course runs, weeks 1 to 4 of instruction
have to come back and the design collapses to something much closer to what
exists today. This is the single largest dependency in the plan and it is a
curriculum committee decision, not a course decision.

**The renumbering has to clear.** ITSY 2377 needs the Local Need block
checked for availability and the change processed. Until then the course is
ITSY 1377 with a prerequisite it cannot enforce.

### 7.4 What can start immediately, regardless

Three things are correct under either the old or the new architecture, and
waiting on the prerequisite decision to do them wastes the wait.

1. **The knowledge unit corrections.** `docs/aicyber-ku-mapping.md` records
   that the instructor-facing framework page still claims two ATLAS techniques
   the course removed, one of which the Rules of Engagement forbid. That is a
   defect in the shipped course today.
2. **The live-model question.** The course currently defaults to the mock and
   requires it for Module 4's before and after runs. Whatever architecture
   wins, a course claiming AIS cannot leave a student able to finish with one
   live model call.
3. **The outcome provenance gap.** Nobody can say where the current six
   learning outcomes came from. That question arrives with the first reviewer
   and it is answerable now by the curriculum office rather than later under
   time pressure.

