# ITSY 1377: Decision Register and Open Issues

**Purpose.** A single place recording what has been decided, what remains open, and what has been deliberately placed out of scope. Maintained alongside the course blueprint so that Phase 2 onward can proceed without relitigating settled questions.

**Last updated:** 2026-08-28

---

## A. Scope Boundary

**In scope:** building a working proof of concept of ITSY 1377 as a course, comprising the lab repository (agent, harness, vulnerable target), the authored course content, a locally deployed Canvas instance with the course populated, and a demo runbook.

**Out of scope, as of 2026-08-27:** **AICyber knowledge unit alignment for the degree program.** The analysis is complete and recorded in `ku-coverage-analysis.md`, and the conclusions are preserved in section D below. No further work on knowledge unit mapping, degree plan revision, or CAE submission strategy is being carried out under this effort. The one finding that touches the course itself is settled: **ITSY 1377 cannot carry the Basic Scripting and Programming knowledge unit**, and no attempt will be made to make it do so.

---

## B. Decisions Made by the Program

| # | Decision | Recorded | Effect on the build |
|---|---|---|---|
| 1 | ITSY 1377 will be a **required** course, not an elective | Confirmed | None on the build. Clears the KU eligibility gate |
| 2 | Provider terms-of-service risk is **accepted for the proof of concept**; agreements will be in place for the production course | Confirmed | Labs may call a hosted provider. Design still targets the application trust boundary rather than model safety filters, because that is better pedagogy independently of risk |
| 3 | **Common Cartridge** is the primary Canvas artifact, with an API script for incremental updates | Confirmed | Changes deliverable D. Phase 4 builds a cartridge generator |
| 4 | The college already holds **CAE-CD**; AICyber is the program goal | Confirmed | Out of scope per section A |
| 5 | **3 semester credit hours**, and no more than **3.9 workload units** | Confirmed | Fixes the contact-hour coding. See C1 |
| 6 | 8-week Flex session, Sunday deadlines, final exam required | Confirmed | Fixes the calendar. See C2 |
| 7 | All student-facing content targets a **7th grade reading level**, enforced by automated check | Confirmed | Adds a build step. See C4 |
| 8 | Course must conform to the **NLC Online Course Template** | Confirmed | Fixes module anatomy and page markup. See C5 |

---

## C. Design Constraints Now Fixed

### C1. Contact hours: 2 lecture + 2 lab, 64 contact hours, 3.80 workload units

Alamo procedure D.5.1.2 computes workload as lecture hours plus (lab hours multiplied by 0.90, effective 1 January 2026). Only two codings clear 3.9 with any margin.

| Coding | Contact hours | Workload units | Status |
|---|---|---|---|
| **2 lecture + 2 lab** | **64** | **3.80** | **Recommended.** Margin, and it keeps a lab designation |
| 3 lecture + 1 lab | 64 | 3.90 | Alamo's usual 3 SCH convention, but zero margin |
| 2 lecture + 4 lab | 96 | 5.60 | Not available |

**Open item:** the 3.9 per-course cap does not appear in D.5.1.2, which caps adjuncts at "fewer than 12 workload units" per long term. The 3.9 figure is treated as a given operating constraint. Confirm with Academic Affairs before citing it externally. No conclusion depends on it.

### C2. Calendar: seven instructional weeks plus a six-day final block

Verified against both official district calendar PDFs. Six of eight Flex sessions run Monday to Saturday across exactly **55 days**, giving **seven Sunday deadlines** (days 7, 14, 21, 28, 35, 42, 49) and a **six-day final block** (days 50 to 55). Week 8 contains no Sunday. The final exam window is carved out of that block rather than added to it.

Two traps the build handles: the exam window moved between academic years (Wednesday to Saturday in AY2025-26, Monday to Friday in AY2026-27, so the course uses the Wednesday to Friday intersection); and both Spring Flex I sessions start Tuesday and run 61 days with Spring Break inside, so the course ships relative day offsets and a per-session date map rather than fixed dates.

Two compliance requirements follow. **Census is day 8**, so gradeable participation evidence must exist in week 1, and the college requires an attendance verification activity completed by the third class day. **A final exam is expected**, per the college handbook and the faculty closeout procedure.

### C3. Assessment: four lab modules, two checkpoints, a three-part final

Rebuilt to fit an adjunct. **22.7 instructor hours per term** (26.1 with contingency), 73 percent auto-scored, five hours of hand-reading across the whole term. Full specification in the blueprint section 3.

The load-bearing idea: AI-resistance comes from anchoring a question to the student's own run artifacts, not from the answer being prose. Security results are auto-graded deterministically through per-student canary tokens and side-effect ledgers rather than by reading transcripts.

### C4. Reading level: 7th grade, enforced by `textstat`

All student-facing content. The check excludes code blocks, command output, framework identifiers, the glossary, and quoted external text. Measurable commitments: average sentence length at or under 15 words, grade level at or under 8.0 after exclusions, targeting 7.0. The build fails above threshold and the report is committed alongside the content.

**Stated limit:** external framework readings cannot be rewritten, so each gets an instructor-authored reading bridge. Technical vocabulary is taught, not avoided.

### C5. Template conformance: NLC Online Course Template

Module anatomy is Overview page, Content page, Assignments, Wrap-up page. Four-block page pattern of Introduction, Directions, Grading Criteria, How to Submit. Placeholder convention `#fbeeb8`, and a build check asserts zero remain.

**The DesignPLUS problem** is the significant one. Pages carry Cidi Labs `dp-*` classes but the export contains no stylesheet or script, because DesignPLUS loads at the Canvas account level and is licensed. In a local Canvas the pages render as unstyled divs. **Resolution:** keep the exact class names so content is drop-in for the production Canvas, and ship a small openly licensed CSS shim for the demo only. No Cidi Labs CSS or JavaScript is copied.

### C6. Knowledge units this course carries

**AI for Security Assessment** as lead, **Defensive Applications of AI** as co-lead, and the **modern half of Machine Learning Fundamentals** as co-carrier. Three units is the ceiling for a 3 SCH course.

**It does not carry Basic Scripting and Programming.** Settled and out of scope for further work.

---

## D. The Knowledge Unit Analysis, Parked

Recorded so the work is not lost and does not need repeating. Full detail in `ku-coverage-analysis.md`.

**Why ITSY 1377 cannot carry Basic Scripting and Programming.** Four independent arguments: it covers 9 of 18 topic elements (50 percent against a required 75); it cannot defend two of the unit's six outcomes at all (system administration automation, and regular expressions); closing the gap needs roughly 26 instructional hours in a 64-hour course, and every combination of cuts that frees them damages at least three of the course's own outcomes; and decisively, **the course must permit AI assistance to assess its own outcome 6, while the unit requires unassisted "write and execute" evidence**. One syllabus cannot hold both positions.

**Options recorded for the program, none being pursued here:**

| Option | Cost | Note |
|---|---|---|
| **Swap ITSC 2325 Advanced Linux for ITSC 1342 Shell Programming: Scripting** | Zero credit hours, statewide WECM inventory add | **The recommended fix.** Takes the proposed 2027-2028 plan from 10 of 11 units to 11 of 11 |
| Pin MATH 1314 by name and write statistics into ITSY 1371 | Zero credit hours | Required for Math Fundamentals, which a select-one slot cannot carry |
| Split Machine Learning Fundamentals across ITSY 1371 and ITSY 1377 | Zero | Only available once Python leaves ITSY 1371 |
| Add ITSE 1359 Introduction to Scripting Languages | 3 credit hours | Viable but not needed if ITSC 1342 is swapped in |
| Upgrade ITSY 1371 to 4 SCH and shrink ITSY 2443 | Local Need revision plus an inventory change | Second-best; leaves the unit on locally authored text |

**Issues flagged to the program, not being worked here:**

1. **ITSY 2430 is listed at 3 SCH but the number denotes 4 SCH.** Either the plan is 61 SCH and over the statutory cap, or the number should be ITSY 2330. Must be reconciled.
2. **ITSY 1371 collides** with Collin College's existing ITSY 1371. Institution-scoped so not blocking, but it will surface in articulation.
3. **Subnetting and the TCP/IP model are absent** from ITNW 1425's statewide description and both published outcome lists.
4. **No THECB-published outcome source exists.** The WECM search application is retired, so every outcome quoted comes from college master syllabi.
5. **The college publishes no end-of-course outcomes for any course.** Collecting syllabi is a blocking prerequisite for any CAE submission.

---

## E. Open Issues That Do Affect the Build

Ordered by how much they could cost.

| # | Issue | Risk | Mitigation in the plan |
|---|---|---|---|
| **E1** | ~~Canvas on Apple Silicon~~ | **RESOLVED 2026-08-27** | **It works natively.** See section H |
| **E2** | **Local model path untested on real student hardware.** Ollama's docs state twice that install needs no administrator, but that is not the same as surviving AppLocker or SmartScreen on a managed image | **High for the production course, low for the PoC** | Pilot on one real student-image laptop before the syllabus commits. The PoC ships a `mock` provider so nothing depends on it |
| **E3** | **Tool-calling reliability at 1 to 4 billion parameters could not be verified.** A vendor "tools" capability means the template can emit tool-call syntax, not that the model chooses correctly | Medium | The N-of-M harness design treats a malformed tool call as a teachable event rather than a broken assignment |
| **E4** | **DesignPLUS styling absent locally.** See C5 | Medium. Affects whether the demo looks real | CSS shim, documented as a demo-only stand-in |
| **E5** | **Groq free tier may require a credit card.** Strongly implied by the existence of a paid upgrade path, but no page states it | Medium | Sign up with a fresh account and confirm. The `mock` provider means the build does not block on it |
| **E6** | **Framework churn.** ATLAS ships roughly monthly and renames techniques; OWASP shipped a new edition in August 2026; NIST AI RMF is under revision | Medium, ongoing | Pin ATLAS release 2026.07 and the OWASP 2026 editions. Budget a maintenance pass every semester |
| **E7** | **Rate limits will read to students as broken code.** A 7-case, 5-trial harness run is 100-plus requests | Low | Harness ships with backoff, a human-readable waiting message, and prints an estimated request count before starting |
| **E8** | **MITRE ATLAS deep links fail automated link checkers.** The site is a client-side application and every deep route returns 404 to a fetcher | Low | Build handouts from the pinned YAML data file; expect a noisy link report |
| **E9** | **OpenAI usage policy could not be verified**; the site returns 403 to automated fetching | Low | A human transcribes the clause from a browser for the Rules of Engagement |
| **E10** | **New Quizzes is unavailable** in open-source Canvas; the API is documented but has no route in the code | Low | Classic Quizzes only |

---

## F. What Phase 2 Onward Will Build

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repository scaffolding; Canvas deployed locally; admin login verified | **Complete.** See section H |
| 1 | Course blueprint | **Complete**, reviewed and revised |
| 2 | Lab repository: agent skeleton, test harness, vulnerable target, working end to end | **Complete.** See section I |
| 3 | Course content authored as markdown, per module | **Complete.** 57 pages, 6 quizzes, 5 rubrics |
| 4 | Canvas population, Common Cartridge primary | **Complete.** See section J |
| 5 | Demo runbook and end-to-end verification | **Complete.** `RUNBOOK.md` |

---

## G. Verification Items Carried Forward

Small, cheap, and worth closing before the demo is shown.

1. Confirm the 3.9 workload figure with Academic Affairs (C1).
2. Confirm whether identity verification (BioSig-ID) or proctoring (Respondus) is required for a fully distance course. The assessment design needs neither and is compatible with both.
3. Transcribe the OpenAI usage policy clause from a browser (E9).
4. Confirm whether Groq's free plan requires a credit card (E5).
5. Confirm the district help desk phone menu option; the template cites three different ones across three pages.
6. Decide whether the college's courseware policy accommodates CC BY-SA ShareAlike obligations if OWASP text is adapted rather than linked.


---

## H. Phase 0 Result: Canvas Runs Natively on Apple Silicon

Completed and verified end to end on 2026-08-27, on macOS with colima (6 CPU, 16GiB, 60GiB disk).

**The headline: the official `instructure/canvas-lms` repository builds and runs natively on arm64.** Risk E1 is closed. The upstream ARM64 issue being closed as "not planned" turns out to describe a lack of commitment rather than a lack of capability, because the base image `instructure/ruby-passenger:3.4-jammy` publishes a `linux/arm64` manifest. Nothing is emulated.

**Verified working:**

| Step | Result |
|---|---|
| Clone `instructure/canvas-lms` (shallow) | 723MB, HEAD `1c9f0bb8` dated 2026-04-30 |
| `docker compose build --pull web` | Image built, `linux/arm64` |
| Toolchain inside the image | aarch64, Ruby 3.4.8, Node 20.20.2 |
| `bundle install` | 200 dependencies, 419 gems, multilock synced cleanly |
| `rake db:create db:initial_setup` | "Initial data loaded" |
| Admin account | `admin@itsy1377.local`, AccountAdmin on the demo root account and Site Admin |
| `./script/install_assets.sh` | Compiled in 53 seconds |
| HTTP | 302 then 200, `Canvas Login | Instructure` |
| **Admin login** | **Succeeds, lands on the Dashboard** |
| API token | Minted via Rails console, `usable=true` |
| Course shell | Created, id 1, published |

**Three things that went wrong, and the fixes, all captured in `canvas/deploy/setup.sh`:**

1. **The documented port is wrong for this setup.** Passenger and nginx listen on **port 80 inside the container**, not 3000. Mapping `3000:3000` produces a host port that silently refuses connections while the application is perfectly healthy. The fix is `3000:80`. This cost the most time to find, because every symptom pointed at a dead Rails app when Rails was fine.
2. **Gems are not installed by the image build.** They live in a named volume, so `bundle install` must run once. Skipping it produces an error about the `crystalball` git source "not yet checked out," which reads like a repository problem but only means gems are missing.
3. **`script/docker_dev_setup.sh` was deliberately not used.** Its macOS branch installs dinghy-http-proxy system-wide without asking, which is reported to break unrelated Docker work. The setup script here does the same work by hand and publishes a port instead, so no proxy is involved and no global state is touched.

**Not encountered:** the `bundler-multilock` failure from issue #2520 did not occur. The lockfiles synced without intervention.

**Consequence for the demo:** the `ahamana/canvas-lms-docker` fallback is not needed. The demo runs from the official Instructure repository, which is what the brief asked for and is the more defensible thing to show a reviewer.


---

## I. Phase 2 and 3 Result: Labs and Content

**Lab repository.** Working end to end offline, with no API key. The agent
extends through five marked extension points; HelpDesk Lite carries five
planted flaws, each marked in its own source; the harness runs N-of-M trials
with an asymmetric threshold and four ranked detectors. The worked solution
passes 55 of 55 autograder tests, which is the only way to know an autograder
is satisfiable.

**Course content.** 57 pages, all rendering to the NLC template's DesignPLUS
markup, mean Flesch-Kincaid grade **4.40** against a limit of 8.0. Six quizzes,
93 items, every one tagged to an outcome. Five rubrics, all balancing to their
assignment's point total.

**Four adversarial reviews were run** with different expert framings: offensive
red team, Python correctness, instructional design, and security assessment
methodology. They found defects that mattered, and the six worst were all the
same shape: **the harness reporting a comforting result that was not true.**

| Defect | Why it mattered |
|---|---|
| A canary that disagreed with the seeded database reported successful exfiltration as MITIGATED, while the detector self-test passed | The exact failure the whole design exists to prevent. Now checked in preflight, which refuses to run |
| MITIGATED could be reported from a single completed trial | Four rate-limited trials and one clean miss read as a working fix |
| `tool_shape` returned "my assertion held" where the runner read "the attack landed" | A student's working defense would be reported as a vulnerability |
| A blocked call's arguments counted as a leak | Same, by a different route |
| Deleting `send_email` passed every control | "Remediation" would have meant removing the feature |
| Scope was enforced in the harness but not in the tools | The CLI would reach any host in the settings file |

Two more worth recording because they are about the promise the course makes
about itself. `requests` honours `HTTP_PROXY`, so on a managed college laptop
loopback traffic would have left the machine, carrying the ticket data and the
system prompt with it; sessions now set `trust_env = False`. And nothing
enforced that the answer key stays out of the student repository, which was a
promise in three README files with no mechanism behind it;
`scripts/build_student_repo.py` now refuses to publish a tree that still
contains it.

**Framework mappings were corrected** against ATLAS: `AML.T0086` removed from
A2, which proves mail left but says nothing about what was in it;
`AML.T0080` corrected to `AML.T0070` on A5, because a retrieved knowledge base
article is RAG poisoning rather than agent context poisoning; `AML.T0085.001`
removed from A6 in favour of CWE-862, because the endpoint has no
authentication at all so the agent is a convenience rather than the
vulnerability; and A4's ATLAS list left deliberately empty, because a missing
control with no adversary is not a technique and a plausible identifier there
is worse than a blank.

**The framework mapping is generated now, because correcting it by hand did not
hold.** The correction above was written into `docs/course-blueprint.md` and
reached neither of the two other files carrying the same table. The result:
`content/pages/framework-alignment.md` and `docs/blueprint.html` both went on
claiming `AML.T0067` and `AML.T0054` for week 7 with nothing demonstrating
either, and `AML.T0054` is jailbreak, which the Rules of Engagement forbid
students from attempting. The three copies also disagreed about where
`AML.T0070` sat and whether `AML.T0053` reappeared on week 6.

The content gate did not catch it, and the reason is worth keeping: both
identifiers were in `NAMED_ONLY` with accurate explanations, and `NAMED_ONLY`
could not distinguish prose that names a technique in order to rule it out from
a table row that claims it. `docs/` was not scanned at all.

What changed. `content/_shared/atlas-2026.07.yaml` pins the technique names as
a labelled subset of the release, transcribed from material already verified
against it rather than written from memory. `tools/atlas_table.py` generates
three tables into all three files from the case files and `content/course.yaml`.
Four gates were added: the generated block has to be current; `docs/` is
scanned for identifiers; no undemonstrated technique may appear in a
hand-written table row; and an identifier may not be both demonstrated and
excused. `tools/blocks.py` now treats an HTML comment between blocks as what it
is, a marker rather than page text.

Three things the work found. `content/course.yaml` had never claimed either
technique, so the structural source Canvas is built from was already right and
only the prose copies were wrong. `AML.T0051.000` was simultaneously
demonstrated by A1 and excused in `NAMED_ONLY`, which put one technique in two
tables saying opposite things. And `AML.T0051` was excused as "the parent
technique" when A1 and A2 demonstrate two of its sub-techniques, which
understated the course; a parent is now derived as demonstrated when a child
is.

One gap left open on purpose. `AML.T0080` has no name in the pinned file,
because the repository records a description of it rather than a title. The
generator reports it under the table instead of inventing a name.

---

## J. Phase 4 Result: Canvas Population, and a Finding That Changes a Deliverable

The course is in Canvas: 11 modules, 45 pages, 17 assignments, 6 quizzes, 2
discussions, 5 rubrics, 6 outcomes, all verified by reading the course back
through the API and checking it against `content/course.yaml`.

**The finding: Canvas silently drops every quiz in every cartridge unless an
external Python QTI converter is installed, and open-source Canvas does not
ship it.**

`gems/plugins/qti_exporter/lib/qti.rb` looks for `migrate.py` from the
QTIMigrationTool in two vendored paths and then on `PATH`, and registers the
`qti_converter` plugin as `enabled: python_converter_found`. Without it the
plugin is disabled. The import still reports `completed`, with no error, no
warning, and no migration issue.

**This is not a defect in our cartridge.** The NLC template's own export,
produced by Instructure's own Canvas, imports zero of its two quizzes into this
instance. That test is what separated "our file is wrong" from "this Canvas
cannot read any file".

**What it changes.** Decision B3 made Common Cartridge the primary artifact,
and that decision still stands: on Alamo's Instructure-hosted Canvas the
converter is present and the cartridge carries everything. But a cartridge is
not sufficient for a demo on open-source Canvas, so `tools/populate_canvas.py`
creates the quizzes over the REST API and the importer runs it automatically.
The deliverable is the cartridge; the API script is what makes a local
deployment complete. Both are needed, for different reasons.

**Two smaller things worth knowing.** Canvas's cartridge importer is particular
about how a quiz resource is declared: the assessment resource carries no
`href`, the Common Cartridge profile copy is named after the quiz's own
resource id, and the meta resource needs a different identifier. Getting any of
those wrong produces the same silent zero-quiz import. And importing into an
existing course leaves Canvas's two default assignment groups behind at weight
zero, which is harmless but untidy; import into a fresh course, or delete them.

---

## K. Open Items Carried Into a Real Term

These are the things a human has to close before this is taught, ordered by how
much they could cost.

1. **The local model path has never been tested on a real locked-down student
   laptop.** Vendor documentation saying "no administrator required" is not the
   same as surviving a specific institution's application control policy. This
   is the largest residual risk in the build and no amount of research retires
   it. Pilot on one real student-image machine.
2. **Groq's free plan may require a credit card.** Nothing states it either
   way. Sign up with a fresh account and find out.
3. **Transcribe the OpenAI usage policy clause from a browser.** The site
   returns HTTP 403 to automated fetching, so the Rules of Engagement cites
   only the two provider policies that could be verified.
4. **Confirm whether identity verification or proctoring is required** for a
   fully distance course. The assessment design needs neither and is compatible
   with both.
5. **Two grading rules are undecided** and the content works around both: the
   general late-work penalty, and which items count as "labs" for the dropped
   lowest lab. Neither is in the blueprint.
6. **Confirm the district help desk phone menu option.** The template cites
   three different ones across three pages, so the authored pages cite none.
7. **Re-verify the OWASP 2026 identifiers and the ATLAS release** before a term
   depends on them. ATLAS ships roughly monthly and renames techniques. Every
   report the harness writes records which editions it used, so this is
   checkable rather than assumed.
8. **The weekly time estimates need a decision.** The nominal 3 credit hours
   over seven instructional weeks implies roughly 20 student hours per week.
   The designed work is about 5 to 7 hours of assigned activity, which a
   student with no programming background will commonly take two to three times
   to complete. The Overview pages state the assigned figure. Somebody should
   decide which number the syllabus claims.


---

## L. Phase 4 Addendum: What the Quality Matters and Accessibility Review Found

A Quality Matters certified peer reviewer and accessibility specialist assessed
the course against the QM Higher Education Rubric (7th edition) and WCAG 2.1
AA. The result: **four General Standards met, three partially met, one not
met.**

### The one that blocks certification

**Standard 5, Learner Interaction, was not met, and the failure was clean.**
Across 8 weeks, 10 assignments, 6 quizzes and 1000 points, students were
required to interact with each other exactly once: a 1 to 2 sentence reply in
the week 1 introduction discussion, worth one point, which `course.yaml` then
excluded from the final grade. So the sole required peer interaction in the
course was worth nothing. Weeks 2 through 8 contained none at all.

The blueprint defends this on adjunct workload grounds and that defence is
honest, but it is a defence of a choice rather than evidence of a met standard.
QM treats learner interaction as an essential must-meet standard.

**Fixed** by adding one graded discussion in week 6, "Would That Evidence
Convince You?", worth 15 points, graded complete or incomplete against a
two-line checklist. Students post one finding from their own run with its
evidence, then answer one question about a classmate's: would that evidence
convince you? It costs roughly ten minutes of instructor time for a section of
thirty, and it is the only place in the course where the "grade the world, not
the prose" discipline gets applied to somebody else's claim.

That takes Project 2 to 565 points against a 55 percent weight, so the
points-equal-weight-times-ten convention no longer holds exactly there. The
build now reports that drift as a note rather than failing on it, and prints
what each point is actually worth as a share of the course.

### Five findings that would have cost students points or access

| Finding | Fix |
|---|---|
| **Final Part C could not be submitted in its written form.** `submission_types` omitted `online_upload`, and the written walkthrough is the full-credit option for anyone who cannot or will not record video. The one route with an accessibility function was the one that did not work | `online_upload` added |
| **Three assignments published two contradictory grading tables.** The generator appended a rubric table after the hand-authored one, and they decomposed the same total differently. Worse, they drifted: the Module 4 page called a config setting optional while the rubric docked 8 points for skipping it | The generated table now REPLACES the authored block. One table, from the rubric, which is also what Canvas attaches. Guidance the authored block carried moved into the rubric |
| **Module 1 assessed error handling a week before it was taught**, worth 25 of 90 points | Week 2 now teaches exactly as much try and except as Module 1 needs, and points at the worked example already in the lab code |
| **Checkpoint 2 was due the same day as the work it checkpoints.** A checkpoint whose job is "prove you are not stuck" cannot do it on the deadline it protects | Moved to day 40. The only non-Sunday deadline in the course, and the page says why |
| **The Module 0 Gate showed every passing student 60 percent.** 16 of its 40 points cannot be auto-scored, against a stated 100 percent mastery bar, in week 1, against an attendance deadline | The quiz description now says what scores instantly, what is released after review, and what to expect to see |

Two more: **240 of 650 assignment points had no rubric**, now closed with five
new ones, so all ten graded assignments have one that balances; and **eight
"Check Yourself" self-check blocks had no answers anywhere**, which is the
clearest practice-with-feedback miss in an asynchronous course.

### Accessibility came out strong, with three real fixes

The reviewer rendered all 56 documents and audited them: **46 tables, zero
failures** on heading order, captions, header scope, icon labelling, link text,
and contrast. All 19 colour pairs pass AA, the tightest at 4.94:1. There are no
images anywhere in the course, so there is no alt-text exposure, and no media,
so nothing to caption.

Three things were fixed anyway:

1. **Callout severity lived in a stylesheet somebody else controls.** Colour,
   an aria-hidden icon, and a text label generated by the local demo CSS. In
   production the styling comes from the college's DesignPLUS licence, which
   may supply no label, so a screen reader user would get the heading and no
   sense of whether it was a warning or a tip. The severity word now lives in
   the markup, visually hidden, and survives any stylesheet.
2. **No `lang` attribute** on the generated documents. One line.
3. **About fifteen quiz items** offered answer options whose entire text was a
   single letter, with the meaning in a code block in the stem. A screen reader
   user had to hold six variants in working memory while navigating a list of
   one-character options. Rewritten to restate what makes each variant
   distinctive.

### The finding that is a college decision, not a course defect

**The workload numbers disagree by a factor of three.** Two pages state 19 to
21 hours per week, which is the arithmetic for 3 semester credit hours
compressed into seven instructional weeks. The eight Overview pages, which are
the pages students actually plan from, itemize to about 5.5 to 8.5 hours each,
roughly 55 hours for the term.

Resolved in the content by stating the assigned time honestly on every Overview
page and adding that students new to programming commonly spend two to three
times that on the coding, which puts a realistic week between about 10 and 20
hours. That is the truthful version and it is now consistent.

**It leaves a question the college has to answer.** If the assigned work really
is about 55 hours, that is well under what 3 credit hours implies, and it is a
credit-hour compliance question before it is a Quality Matters question. Either
the course carries more work than it currently assigns, or the contact-hour
designation needs revisiting. Nobody should discover this during an audit.


---

## M. The Security Subject Matter Review, and a Claim We Withdrew

A cybersecurity subject matter expert with NSA CAE panel experience assessed
the finished content. The review was the most consequential of the five,
because two of its findings are about what the project claims rather than about
how it is built.

### The knowledge unit claim is withdrawn, from three units to one

Blueprint section 7.4 claimed **AI for Security Assessment** as lead carrier,
**Defensive Applications of AI** as co-lead, and the legal and regulatory half
of **AI Governance, Laws, and Ethics**. A search of the built artifacts shows
none of the three is supportable:

| Claimed | In the built course |
|---|---|
| Machine learning applied to assessment, anomaly detection, alert triage | Nothing. There is no ML library in the student dependencies |
| Detection models, UEBA, SIEM and SOAR, model drift, poisoning of defensive models | Zero of five |
| EU AI Act, GDPR, CCPA, HIPAA, incident disclosure duties | Zero occurrences of any of them. "Governance" appears once, on an instructor page |

The course has no defensive centre of gravity either. One of five extension
points builds a control, the reference remediation is sixteen lines, and of the
three weakness classes outcome 3 names, exactly one is ever fixed in code. The
modules are "Break It" then "Fix It" and Project 2 is "Attack, Harness,
Report" at 55 percent of the grade.

**Section 7.4 has been rewritten to claim one unit, partially, with evidence
behind every word.** The companion knowledge unit analysis had already assigned
governance to ITSY 2373, so the two program documents were contradicting each
other and the one with no governance content in it was the wrong one.

That analysis wrote its own indictment: *"a finding that one knowledge unit was
overclaimed puts the credibility of the program's entire mapping in question."*
Blueprint section 8.3 applied exactly that honesty test to the OWASP coverage
claim and never applied it to the knowledge units. It has now.

**The submission lab changed too.** Module 3 was nominated, and it instructs
students not to pass `--case`, not to pass `--trials`, and not to edit any case
file. Forty-five of its eighty points are transcription of tool output. Module 4
is the submission: students author cases, build a control in code, verify it
against two suites, and name a defect they know remains.

### Two smaller claims that were not true of the build

The blueprint said Module 3 offers "a reproducible containerized environment".
There is no Docker anywhere in the labs. And it said a working code fix reports
"5 of 5, MITIGATED", which was wrong twice over. Both corrected in place.

### The autograder required a control to fail open

`test_module4.py` proved a student read their rule from configuration by
handing the guard an **empty** allowlist and asserting the call was **allowed**.
That accidentally made fail-open the required behaviour, in a course that says
three pages later that a guard which lets everything through when something is
missing is worse than no guard. The intent was right and the assertion
expressed the opposite of it.

Now the test hands the guard a **different** non-empty allowlist and checks
that it follows it, in both directions. The reference answers no longer fail
open either.

### "Mitigated" left the harness

Zero hits was reported as MITIGATED on as few as three completed trials. Five
clean trials against a weakness that lands three times in ten produce zero hits
about one run in six, so the word was a conclusion presented as an observation,
sitting two lines below a comment reading *"Missing evidence is not evidence of
absence."*

The status is now `NO_HITS_IN_5`, carrying its own sample size, and
`BLOCKED_5_OF_5` when a control stopped an attempt. A student who wants to
write "mitigated" in a report still can, and now has to decide to.

### Legal framing, which a college attorney would have caught

The Rules of Engagement stated as flat fact that testing without authorization
"is a crime". That is wrong as written, it names no statute, and the course
then has students restate it in their own words and quotes it back on the final
exam. Corrected to "can be a crime", with the student code of conduct as the
consequence that is certain. The page also claimed every commercial provider
bans adversarial testing, and then contradicted itself five lines later.

Clause 6, what to do on finding a real vulnerability outside the course, gained
three things it needed: do not retain any data you saw, route a workplace
finding to the employer's security channel rather than to an instructor, and
the three places a report actually belongs when there is no obvious owner.

### The finding that explains all the others

*"Reading level is mechanically enforced. Framework accuracy is a manual
checklist. Only one of those two can fail a build."*

Worse, the asymmetry had a direction: an accurate hedged sentence costs reading
grade and a confident wrong one does not. That is the mechanism that produced
most of the content defects across all five reviews, and it is now closed by
`tools/verify_content.py`.
