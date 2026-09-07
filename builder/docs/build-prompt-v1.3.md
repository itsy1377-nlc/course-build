# ITSY1377_builder Course Build Prompt

**Target:** Claude Fable 5.1
**Course:** Agentic AI and Security Operations (ITSY1377_builder)
**Institution:** Northeast Lakeview College, Cyber Defense program
**Version:** 1.3
**Date:** 2026-09-03
**Working repo:** `~/workspace/dev/ITSY1377/`

(Verbatim copy of the build prompt as received on 2026-09-03. The Canvas API
token that appeared in the original is redacted here; it lives outside the
repository.)

Open items outside this prompt: late work and resubmission policy; whether the
program has account-level Canvas Outcomes these should roll up into.

---

# THE JOB

Create a new course in Canvas via the API titled "Agentic AI and Security Operations,"
course identifier ITSY1377_builder. Do not modify or replace any existing course.

It is a complete, fully asynchronous, 8-week online course. Students progressively build
one working security operations agent: a phishing email triage assistant. Weeks 1 through
7 each add exactly one capability to that same agent, so it works end to end every week
and grows rather than breaks. Week 8 is the final exam only, with no new instruction. A
week 0 programming on-ramp sits outside the graded weeks.

Build all 8 weeks plus week 0. This is not a sample or an outline.

Audience: community college students in a Cyber Defense associate program. The CompTIA AI
Fundamentals-aligned first course is an enforced prerequisite. Assume no programming
background: the prerequisite is a non-technical AI literacy course and supplies no Python.
Week 0 provides an optional on-ramp and every week carries a scripting sidebar; scaffold
accordingly rather than assuming students arrive with Python. Assume they can already
write a prompt, evaluate an AI output, and define an agent conceptually. Do not re-teach
that.

# THE WHY

Northeast Lakeview College is adding two AI courses to its Cyber Defense program. This is
the second. The first builds general AI literacy; this one converts that literacy into
applied skill for the SOC analyst work these students will do in their first job.
Employers now expect entry-level analysts to work alongside agentic tooling, not just chat
interfaces.

# THE AGENT BUILD ARC

Follow this spine. Each week's lab adds one capability and nothing more.

- Week 1: Call the model from code. Students write an ask_model() function, send one email
  body, and observe nondeterminism, temperature, and token counts. Concept: an agent is a
  loop around this call, not magic. A pre-written helper parses .eml files.
- Week 2: Structured output. The agent classifies one email into strict JSON with verdict,
  category, confidence, and indicators. Students validate against a schema, handle an
  optional leading reasoning block, and retry on malformed output. Malformed output is a
  normal condition to handle, not a failure.
- Week 3: Grounding. Stop sending the raw body alone. Supply parsed headers, SPF, DKIM and
  DMARC results, display-name versus sender-domain mismatch, extracted URL domains, a
  phishing playbook snippet, and the list of known-good internal domains. Students compare
  grounded and ungrounded verdicts on the same email. Lesson: the model is a judgment layer
  over facts you extract deterministically, not a detector. No vector database. The week 3
  reading frames prompt construction as data minimization: what you put in the prompt is
  what you expose, so send the minimum a sound judgment needs. It also names the same
  extraction pattern applied to logs, alerts, tickets, and system messages, so students see
  that the skill generalizes beyond email.
- Week 4: Tools. Three deterministic Python functions are provided:
  check_sender_reputation, check_urls against a local blocklist and allowlist, and
  lookup_recipient which returns prior report history and an executive flag for BEC risk.
  The model requests one, the student's code executes it and returns the result. Introduce
  native function calling here, keeping week 2's manual validation as the fallback path.
- Week 5: The loop. A bounded observe, decide, act loop with a hard cap of 4 steps and an
  explicit stop condition. The agent chooses its next tool based on what it just learned.
  Teach runaway loops and token cost. This is the hardest week in the course for students
  without programming background, and it carries primary evidence for CLO3; pre-write more
  scaffolding here than anywhere else.
- Week 6: Guardrails and human-in-the-loop. The email body is entirely attacker-controlled
  text flowing into the prompt, so prompt injection is this agent's real threat model. The
  lab includes a phishing email whose body instructs the model to mark it legitimate.
  Students defend using delimiting, treating body text as data rather than instructions,
  and validating output against the extracted facts. Add a confidence threshold that
  escalates to a human analyst and a per-run token cap. The week 6 reading covers the wider
  AI risk set alongside injection: hallucination, data exposure, privacy, automation bias,
  and overreliance on AI output. This week is the course's differentiator; give it the
  strongest lab.
- Week 7: Usable output and evaluation. The agent writes a triage note in a fixed format:
  verdict, confidence, indicators, recommended action, escalate yes or no. Then it runs in
  batch over roughly 20 emails. Students score results against provided ground truth,
  report accuracy with false positives and false negatives separated, and argue which error
  type is worse in a SOC and why. The triage note also carries a two-sentence plain-language
  summary written for a nontechnical reader, such as the employee who reported the email.
  This week carries primary evidence for CLO5 and CLO6.

All emails, headers, playbooks, URL lists, sender reputation data, recipient records, and
ground truth ship with the course as synthetic .eml and data files. Attachments are
referenced by filename and hash only; no live or malicious files. No student data.

## Notebook continuity

- Student work in the hosted Jupyter instance persists for the duration of the course.
- Each week's starter notebook nonetheless contains a working version of everything through
  the prior week as pre-written cells. Students carry their own code forward where it works,
  but a student who could not finish week 4 can still start week 5.
- Say this plainly to students in week 1 so nobody believes a bad week ends the course.

# WEEK 0: PROGRAMMING ON-RAMP

Students arrive from a non-technical AI literacy prerequisite with no programming
background. The build arc requires Python from week 1 onward. Week 0 closes that gap.

- Optional but strongly recommended, ungraded, available from day one and for the whole
  term so students can return to it mid-course.
- Opens with an honest self-assessment: 8 to 10 short questions covering the exact
  constructs the course needs. Scoring tells the student plainly whether to work through
  week 0 or skip it. No shame framing.
- Target 4 to 6 hours. It sits outside the 7 instructional weeks, so state clearly that it
  is front-loaded work.
- Scope is exactly what weeks 1 through 7 need, taught in the order the course needs it:
  variables and strings, calling functions and using return values, dictionaries and key
  access, JSON as a dictionary in text form, f-strings, defining a function with parameters,
  if/else, for loops, try/except, reading a traceback to find the failing line.
- Explicitly out of scope: classes and objects, comprehensions, file I/O beyond what
  pre-written cells handle, decorators, virtual environments, pip, the command line. State
  the exclusions so students do not go hunting.
- Delivered as a runnable notebook with the same look and feel as the lab notebooks.
- Every example uses everyday subject matter, never email or security content. Week 0
  teaches Python, not the course.
- Include a "how to read an error message" section. This is the single highest-value skill
  for a student who will be debugging alone at 11pm.

# SCRIPTING SIDEBARS (EVERY WEEK)

Each week includes a short Python sidebar that prepares students for that week's lab
without handing them the answer.

Method: worked example with near transfer. Show the exact construct the lab needs, working
end to end, on a problem from a different domain. The student sees the mechanism, then
applies it to the security problem themselves. The lab answer should be the logical next
step, not a copy-paste.

Rules, all of them binding:

- Identical structure, different domain. Same loop shape, same dictionary access pattern,
  same try/except placement, but about groceries, a music playlist, a class roster, weather
  readings. Never about emails, alerts, headers, or verdicts.
- Never use the lab's variable names, function names, or data shape. A student who
  substitutes the sidebar code wholesale must get an error, not a working lab.
- Runnable and complete. The student can execute it, change a value, and see what happens.
- Under 20 lines, one construct per sidebar. Two constructs means two short sidebars.
- Plain-language walkthrough of what each line does, at the course reading level.
- Ends with one small "try changing this" prompt, ungraded.
- Links back to the relevant week 0 section.

Per-week sidebar targets:

- Week 1: calling a function, using what it returns, f-strings.
- Week 2: dictionaries and key access; JSON as text; try/except with a retry.
- Week 3: building a longer string from several parts, in a controlled order.
- Week 4: defining a function with parameters and a return value; choosing which function
  to run based on a name.
- Week 5: a loop that carries information between passes, with a counter cap and a stop
  condition. Give it the longest and most careful sidebar in the course.
- Week 6: comparing two values and validating one against known facts.
- Week 7: looping over a list of files, counting results, calculating a rate.

Sidebars are ungraded and count against the weekly time budget at 20 to 30 minutes.

# GUARDRAILS

## Institutional template

Before building anything in Canvas, read every file in the NLC online course template at
`~/workspace/dev/ITSY1377/NLC Online Course Template/`. Conform to its page structure,
navigation, required pages, and styling.
Where the template conflicts with anything in this prompt, follow the template for
structure and presentation, follow this prompt for content and assessment, and list every
conflict in the blueprint. Do not silently resolve a conflict either way.

## Learning objectives and standards alignment

Use these six course learning objectives exactly as written. They are the course's
objectives and the basis for all assessment. Do not add, remove, or reword them. If you
believe one is wrong, say so in your blueprint and wait.

- **CLO1 (Apply):** Extract the header, authentication, sender, and URL facts an AI model
  needs to judge a suspicious email.
- **CLO2 (Analyze):** Classify a suspicious email as malicious or benign using an AI model,
  then validate the model's output before trusting it.
- **CLO3 (Create):** Build an AI agent that selects and runs triage tools in a bounded loop
  to reach a verdict.
- **CLO4 (Evaluate):** Judge whether an agent's guardrails reduce prompt injection risk to
  an acceptable level.
- **CLO5 (Apply):** Document a triage decision, its indicators, and its recommended action
  so another analyst can act on it.
- **CLO6 (Evaluate):** Measure agent triage accuracy across a batch of emails and recommend
  where human review stays required.

Week 0 and the sidebars support these objectives but are not assessed and get no mapping.

### Breadth topics carried by survey content

The build arc goes deep on a narrow slice. The following breadth topics are required in the
course but are carried by survey reading, discussion, self-checks, and the final exam rather
than by a lab. They are not course objectives and get no CLO number, no Canvas Outcome, and
no lab. Do not widen the build arc to chase any of them.

- **B1, AI and agentic workflows in IT and security operations broadly.** Week 1 survey
  reading and the week 1 discussion. Covers AI, generative AI, and agentic workflows across
  IT and security operations, not only phishing. The discussion asks students where they
  have already encountered each.
- **B2, the range of AI-assisted security use cases.** Week 7 survey reading and the week 7
  discussion, placed there because students can only generalize once they have built
  something. The reading walks alert triage, log review, phishing analysis, documentation,
  scripting, vulnerability research, and incident response support. The discussion asks each
  student to pick one use case other than phishing and describe what would change in the
  agent they built.
- **B3, security operations components.** Week 1 survey reading, which doubles as the SOC
  orientation the prerequisite chain does not supply. Cover assets, users, networks,
  endpoints, logs, alerts, tickets, incidents, escalation, and documentation, and show where
  the course's own agent sits in that picture. Reinforced by the week 1 self-check.
- **B4, the wider AI risk set.** Week 6 reading covers hallucination, data exposure, privacy,
  automation bias, and overreliance alongside the injection work students actually perform.

Survey content replaces existing reading time rather than adding to it. It must fit inside
the stated weekly reading budget. If it does not, shorten it; do not extend the week.

Canvas Outcomes: the program pulls outcome data from Canvas, so each CLO must exist as a
Canvas Outcome and be linked to the rubric criteria that measure it. Create the six
Outcomes, use one consistent mastery scale across all of them, and link every rubric
criterion to its Outcome. A rubric criterion with no linked Outcome is an error unless it
measures a non-CLO expectation such as submission completeness. Breadth topics B1 through
B4 do not get Outcomes. Before creating course-level Outcomes, check whether matching
account-level Outcomes already exist for the program and link to those instead; report which
path you took.

Primary evidence placement, given a multiple choice final:

    CLO1 -> week 3 lab
    CLO2 -> week 2 lab, reinforced on the final
    CLO3 -> week 5 lab (primary), week 4 lab (supporting)
    CLO4 -> week 6 lab
    CLO5 -> week 7 triage notes
    CLO6 -> week 7 evaluation report

The final exam is selected response and therefore provides supporting evidence only, never
sole evidence, for any CLO above the Analyze level. Its primary job is the breadth topics
B1 through B4, which selected response suits well. Do not claim it measures a CLO on its
own.

Alignment target: NICE Framework work role PD-WRL-001, Defensive Cybersecurity
(NIST SP 800-181r1, Protection and Defense category). Cite the framework version and
retrieval date in the matrix. Mappings:

    CLO1 -> T1085, supported by T1084, S0600, S0712
    CLO2 -> T1348, supported by T1112, T1387
    CLO3 -> T0020, supported by T1299
    CLO4 -> T1177, supported by T1176, S0509, S0667
    CLO5 -> T1241, supported by T1349, T1242, T1428
    CLO6 -> T0164, supported by T1020, T1290, S0892

Verify every ID against niccs.cisa.gov before publishing. If an ID does not exist in the
cited version, flag it. Do not substitute a different ID on your own.

Two mapping notes to reproduce in the matrix rationale, not hide:

- Several PD-WRL-001 tasks are worded around network activity. Phishing triage is a
  user-layer activity. T1348 and T0020 are the layer-neutral anchors and carry the weight;
  T1112 and T1084 are supporting only.
- No PD-WRL-001 task references AI, agents, or prompt injection, because the framework
  predates them. CLO4 therefore maps to the control evaluation tasks (T1176, T1177), since
  students are assessing whether a control reduces risk. State this openly.

CAE-CD Knowledge Unit mapping is out of scope. Other courses in the program carry those.
Do not produce a KU column. If a design choice could raise a question in an NSA CAE review,
flag it in the risk register.

Deliver an alignment matrix with these columns: CLO ID, objective text, Bloom level, Canvas
Outcome name, primary NICE task, supporting NICE tasks, weeks taught, primary assessment
artifact, rubric criterion that measures it.

Separately, deliver a short coverage memo addressed to the program manager. He circulated a
suggested list of eight learning outcomes for this course; they are not adopted and are not
course objectives, but he wants to see how the course covers them. The list is in the
repository. For each of his eight, state where it is taught, how it is assessed, and its
depth honestly. Anything carried only by survey content must say so plainly. Do not
overstate coverage, and do not propose changing the course to improve it.

Weekly objectives:

- 2 to 3 per week, maximum.
- Each names one observable thing the student does in that week's lab.
- Each is tagged with its parent CLO. A weekly objective with no parent is an error; report
  it rather than inventing a new CLO.

Objective writing rules, applied to CLOs and weekly objectives alike:

- One sentence, 20 words or fewer, one measurable verb.
- Banned verbs: understand, know, learn, appreciate, be familiar with, be exposed to.
- No compound objectives joining two verbs with "and."
- Same 7th grade reading level as the rest of the course.

## Canvas structure

- One module per week, named for the week. Week 0 is its own module. A Start Here module
  precedes them all.
- All modules published and available from day one. No completion requirements, no module
  prerequisites. This is deliberate: sequential locking would strand any student who falls
  behind, and the starter notebooks already let them re-enter.
- Due dates are set per week, but nothing locks.

## Start Here module

Following the NLC template where it specifies content, and including at minimum:

- How the course works: the build arc, what persists, what to do after a bad week.
- The week 0 self-assessment, prominently placed.
- How to get help: instructor contact and response time, campus tech support, what to do
  when the Jupyter kernel dies or the session times out, who to contact about the API key.
- The AI use policy.
- Syllabus and a syllabus acknowledgment.

## Instructor presence and interaction

The course must satisfy regular and substantive interaction expectations for asynchronous
distance education. Build in:

- One graded discussion per week, tied to that week's lab. Students post one specific thing
  from their own agent's behavior (what it got wrong, what surprised them, what they had to
  change) and respond substantively to one peer. Keep it to 15 to 20 minutes of student
  time. Prompts must require the student's own results, not general opinion.
- A weekly instructor announcement, drafted and ready to send, that previews the week and
  names the common sticking point.
- A stated feedback turnaround commitment on labs.
- Instructor participation expectations documented in the instructor guide.

## Student technical environment

- Students have a computer, internet, and a browser. Nothing else.
- The school provides a hosted Jupyter Notebook instance with work persisted for the term.
- API key handling: the key is injected into each student's Jupyter environment as an
  environment variable by the hosting setup, and notebooks read it with os.environ. Students
  never type, paste, see, or screenshot a key. If the hosting cannot inject per-student
  environment variables, fall back to a single course key on a student-restricted Canvas
  page, and say so in the blueprint. Screenshot instructions must never include a cell that
  displays key material.
- Token budget: the instructor and program control the budget centrally. Every notebook
  displays a running token count so students can see their own usage. Policy, stated in the
  syllabus: a student who exhausts their budget emails the instructor and receives a top-up,
  with no grade penalty and no late penalty for the delay. Do not build hard cutoffs into
  the labs.
- Advisory budget is roughly $5 per student per course, but per-token cost is not yet known.
  Report estimated token counts per lab and a course total as a footnote. Do not compromise
  lab design to hit a dollar figure.
- Models: IBM Granite 4.2 3B and Granite 4.1 3B. Test every lab against both and recommend
  which to standardize on. 4.2 has a reasoning mode enabled by default, so responses may
  contain a `<think>` block before the answer, and it uses different decoding parameters
  (temperature 1.0, top_p 0.95). Write all parsing to tolerate an optional reasoning block
  regardless of which model is chosen.
- Week 5 is the risk point: bounded tool selection in a loop is the least certain behavior
  on a 3B model, and it is also the hardest week for students. Test it first, on both
  models. If neither is reliable enough, say so and propose a simpler week 5 rather than
  shipping a lab that fails half the time.
- Serving stack: use whatever runs best on the development machine for the proof of concept.
  Document which stack, which version, and how tool calls and reasoning blocks appear under
  it, since that shape is what weeks 2 and 4 are written against.
- All notebooks target an OpenAI-compatible chat completions endpoint with base URL and
  model name as variables at the top. No hardcoded provider, no local installs, no Docker,
  no CLI, no admin rights.
- Keep prompts tight and single-purpose, keep context small, never require multi-step
  autonomous planning.

## Content sourcing

- Openly licensed readings written at this level for agentic AI security largely do not
  exist. Expect to author most readings rather than link out.
- For every authored reading, use expert subagent review to check technical accuracy and to
  supply citations to authoritative sources (NIST, CISA, MITRE, OWASP, vendor documentation,
  peer-reviewed work). Include the citations in the reading.
- Anything linked externally must be openly licensed (CC BY, CC BY-SA, public domain, or
  free vendor documentation readable without an account), attributed, and verified to
  resolve. List any link you could not verify.
- Flag any authored claim the subagent review could not ground. Do not quietly keep it.

## Workload

- 3 SCH delivered in an 8-week Flex session, but hold actual student time to under 6 hours
  per week. Split: video under 12 minutes, sidebar 20 to 30 minutes, reading 40 to 50
  minutes, lab 2.5 to 3 hours, discussion 15 to 20 minutes, self-check and submission 30
  minutes.
- This leaves little slack. If any week exceeds 6 hours, cut reading length first, never the
  sidebar and never lab scaffolding.
- Week 0 is additional and front-loaded at 4 to 6 hours. State this plainly to students.
- State an estimated time for every activity and show the weekly total.
- Most notebook cells are pre-written and working. Students fill 5 to 15 lines per lab in
  clearly marked TODO cells.

## Submission and grading

- Submission must be trivially easy. Each lab submits: a screenshot of the working output,
  one exported artifact (a .txt or .json file the notebook writes with a single pre-written
  cell), and a short written answer of 3 to 5 sentences.
- Every rubric must be gradeable from those three items alone, without the instructor
  running the student's notebook.
- Tell students exactly what to screenshot and exactly which file to attach. No ambiguity,
  no zip files, no repository links, and nothing that displays credentials.

## Grade weighting

Labs 60, final exam 20, discussions 12, self-checks 8. Total 100. Week 0 and sidebars are
ungraded.

## Week 8 final exam

- Classic Quizzes, created via the Canvas Classic Quizzes API. Not New Quizzes.
- Multiple choice only. Open book, online, no proctor, no time pressure beyond a generous
  window.
- Scenario-based stems drawn from the course's own agent and corpus: given this output,
  given this header set, given this guardrail, what is the correct read. No questions
  answerable from general phishing trivia and no questions answerable without having built
  the agent.
- Assesses breadth topics B1 through B4 as its primary job, plus CLO1, CLO2, and CLO4 at
  the recognition and analysis level as supporting evidence. Primary evidence for every CLO
  lives in the labs.
- Question mix: roughly half the items on the breadth topics, half on scenario reads drawn
  from the agent and corpus.
- Verify the token scopes needed for Classic Quizzes creation before Phase 1 and report if
  the instance has Classic Quizzes disabled.

## Design and accessibility

- Canvas pages: WCAG 2.2 AA and the NLC template. Semantic HTML, correct heading hierarchy,
  alt text, table headers, no meaning carried by color alone, descriptive link text. Zero
  errors in the Canvas Accessibility Checker.
- Captions and a text transcript for every video.
- One identical page template every week, within whatever the NLC template specifies:
  Overview, Objectives, Read/Watch, Sidebar, Lab, Discussion, Submit, Check Yourself.
- Jupyter notebook accessibility is out of scope for this proof of concept. Note it in the
  risk register.

## Reading level

- Instructional prose at or below 7th grade Flesch-Kincaid, including week 0, sidebars,
  discussion prompts, and quiz stems. Report the measured score per page.
- Code, email headers, log excerpts, and required technical vocabulary are exempt, but every
  technical term is defined in plain language on first use and appears in a course glossary.
- Simplify sentences, not concepts.

## Third-party services

Zero external services is the target. If one is unavoidable it must permit users aged 13 and
up, require no payment, and require no account with personal information. Cite the specific
terms-of-service clause.

## Academic integrity

- Students will use AI on this work. Assume it and write a course AI use policy that permits
  it with disclosure.
- Lab written answers and discussion posts require students to reference their own agent's
  specific behavior and numbers, which is difficult to outsource.

# PROCESS

**Phase 0, corpus.** Deliver the synthetic email corpus design and a sample of 5 finished
emails before anything else: total count, mix of phishing types plus spam and legitimate
mail, header and authentication realism, how ground truth is labeled, how difficulty is
distributed, and confirmation that the sample .eml files download cleanly through Canvas
without tripping endpoint protection. Stop for approval.

**Phase 1, blueprint.** After corpus approval:

1. The full alignment matrix with verified NICE task IDs and the Canvas Outcomes plan,
   including whether account-level Outcomes already exist.
2. The survey content plan for breadth topics B1 through B4: what the week 1 and week 7
   survey readings will cover, their word counts, their estimated reading time against the
   weekly budget, and the week 1 and week 7 discussion prompts in full.
3. A one-paragraph spec per week: capability added, lab deliverable, what students write
   versus what is pre-written, weekly objectives with parent CLOs, sidebar construct and its
   chosen domain, discussion prompt, submission artifacts, estimated time, estimated tokens.
4. The week 5 sidebar and week 5 lab, written in full. Week 5 is the hardest week for both
   the model and the students, and it is where the near-transfer sidebar approach is most
   likely to fail. Build it first so the pattern is proven before six other weeks depend on
   it.
5. Week 5 model test results across Granite 4.2 3B and 4.1 3B, with a recommendation.
6. The week 0 outline and its self-assessment questions.
7. The week 8 exam blueprint: question count, breadth topic and CLO coverage per question,
   and sample stems.
8. Every conflict found between the NLC template and this prompt.
9. Every assumption you made and every gap you need filled.

Stop for approval. This blueprint goes to the program manager for review, so write it to be
read by someone who is not building it.

**Phase 2.** Build Start Here, week 0, and weeks 1 and 2 in full. Stop for feedback.

**Phase 3.** Build weeks 3 through 8.

# WHAT DONE LOOKS LIKE

A new course created in canvas.bashtion.dev via the Canvas API using the token supplied
outside this file, conforming to the NLC online template, containing:

- Start Here module as specified.
- Syllabus, course description, the six CLOs, alignment matrix, glossary, AI use policy,
  token budget policy, and the enforced prerequisite stated in the description.
- Six Canvas Outcomes, one per CLO, linked to the rubric criteria that measure them.
- The coverage memo for the program manager, delivered alongside the course rather than
  inside it.
- The synthetic email corpus and supporting data files.
- Week 0 module: self-assessment and on-ramp notebook, marked optional and ungraded.
- 7 weekly modules, each with:
  - An overview video, 2 to 4 minutes.
  - A "what success looks like" walkthrough video showing the finished lab behaving
    correctly. Show the outcome and how to recognize it. Never show the steps or code.
  - Authored reading with citations and estimated time.
  - The scripting sidebar as a runnable notebook, ungraded.
  - A starter notebook containing working code through the prior week, plus scaffolding,
    marked TODO cells, and a pre-written export cell for the submission artifact.
  - A graded discussion tied to that week's lab results.
  - A Canvas rubric of 3 to 5 criteria with explicit points, 3 to 4 performance levels, each
    criterion linked to its Canvas Outcome, and each gradeable without running student code.
  - A low-stakes self-check.
- Week 8 module: the classic quiz final exam. No new instruction.
- Gradebook scheme weighted labs 60, final 20, discussions 12, self-checks 8.
- Instructor package: solution notebooks, seven drafted weekly announcements, discussion
  facilitation notes, common student failure modes and fixes, grading notes, environment
  setup steps including API key injection, and a list of every place a 3B model is likely to
  disappoint.
- Videos produced with the `/instructional-video` skill installed in
  `~/workspace/dev/ITSY1377/`, which outputs both a script and a finished video. Deliver
  both.

Risk register, delivered as a course document, covering at minimum:

- The programming gap. Week 0 and the sidebars narrow it but do not close it, particularly
  at week 5. The prerequisite chain supplies no Python. Expect attrition among students who
  skip week 0, and track it in the first offering.
- Late work and resubmission policy. Not yet set.
- Course rot. Labs are pinned to a specific small model family that ships new versions
  frequently. Name where source artifacts live and what has to be re-tested each term.
- Weekly time budget has little slack; verify against real week 1 and 2 builds.
- Jupyter notebook accessibility, out of scope here.
- Course ownership and licensing, unresolved.
- Anything week 5 testing revealed about small model reliability.
- Any authored claim that subagent review could not ground.

Final QA report: reading level per page including week 0, sidebars, discussion prompts and
quiz stems; accessibility results; link and citation verification; token estimates per lab
and per course against the $5 advisory figure; model comparison results; NLC template
conformance including any unresolved conflicts; the completed alignment matrix with Canvas
Outcome links, and the coverage memo; and every unresolved gap.
