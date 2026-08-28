# ITSY 1377: Decision Register and Open Issues

**Purpose.** A single place recording what has been decided, what remains open, and what has been deliberately placed out of scope. Maintained alongside the course blueprint so that Phase 2 onward can proceed without relitigating settled questions.

**Last updated:** 2026-08-27

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
| 2 | Lab repository: agent skeleton, test harness, vulnerable target, working end to end | Next |
| 3 | Course content authored as markdown, per module | |
| 4 | Canvas population, Common Cartridge primary | |
| 5 | Demo runbook and end-to-end verification | |

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
