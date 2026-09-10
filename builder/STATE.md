# ITSY-1377-000 build state

Written so a fresh session can continue without re-deriving anything. Update
this file at every stopping point. Last update: 2026-09-10, week 6 rebuilt, pushed and verified.
Weeks 1 to 6 are done. Week 7 is next.

## Where the build is

**Phases 0, 1 and 2 are done. Phase 3 is in progress: build weeks 3 through
8.** Phase 0 and Phase 1 were approved by the user on 2026-09-03 and
2026-09-04. Phase 2 was reported complete on 2026-09-04 and the user said
"proceed with phase 3". Nothing under `builder/` is committed to git.

Phase 1 package: `builder/docs/phase1-blueprint/` holds seventeen documents,
about 84,000 words, entry point `README.md`. The week 5 model test report is
`builder/docs/week5-model-test.md` with its raw record beside it. Every file
measures inside the program-manager bar (grade at or below 9.5, average
sentence at or below 18, no sentence over 45, no paragraph over 70).

Phase 0 package: `builder/docs/phase0-corpus-design.md` (the design, grade
7.0, 12-word sentences, no paragraph over 70 words, every count recomputed
from the manifest), the same document rendered for the program manager at
`builder/docs/phase0-corpus-design.html` with the six sample emails as an
appendix (publishing it as a hosted page was blocked by the permission
classifier; open the file locally or publish it by hand), six rendered and
verified sample emails under `builder/corpus/emails/`, `ground_truth.json`
with six records under one labeling convention, and both corpus checkers
passing (0 failures; one permitted fold-length warning on 003).

The build prompt is saved verbatim (token redacted) at
`builder/docs/build-prompt-v1.3.md`. Everything for this course lives under
`builder/`. The other trees in this repository are different courses and are
never referenced by anything that ships.

## Blockers

1. **Resolved.** The first token returned 401; the user supplied a working
   one on 2026-09-03 (kept outside the repo in the session scratchpad
   `canvas.env`; never write it into the repo). Verified: the user is the
   site admin (user id 1), root account "Test Courses" (id 1), existing
   courses 3 (funded) and 4 (constrained) untouched. The account has no
   Outcomes at any level, so the six CLOs will be course-level Outcomes.
   Classic Quizzes is enabled (a probe quiz with one question was created and
   deleted). The course shell **ITSY-1377-000 is Canvas course id 6**,
   unpublished, holding only `corpus/emails/` with the six sample files. The
   download test passed (`builder/docs/phase0-download-test.json`).
2. **Resolved.** The program manager's eight suggested outcomes were not in
   the repository; the user supplied them on 2026-09-03 and they are saved
   verbatim at `builder/docs/program-manager-suggested-outcomes.md`. The
   coverage memo is written against that file.

## Decisions taken (defaults, to be confirmed at the Phase 0 approval)

- Course files live in `builder/` (`corpus`, `docs`; later `content`,
  `notebooks`, `canvas`, `video`).
- The corpus organization is Pellgrave Mechanical Group, `pellgrave.example`,
  a Texas mechanical contractor; gateway product Sentrywick Gateway; webmail
  provider Lanternmail; bulk provider Sendbarrow Mail. All invented; business
  names were web-searched.
- 56 emails: 25 teaching (weeks 1 to 6), 20 batch (week 7, 10 malicious and
  10 benign), 11 exam-only. Seven categories map to two verdicts; spam is
  benign. Full design: `builder/docs/phase0-corpus-design.md`, section 14
  lists the fourteen decisions the program manager is asked to approve.
- Every domain under `.example`; IPs from RFC 5737 or RFC 1918; no real
  brand, company or person; attachments as a gateway-stripped stub header plus
  a body notice; bodies 7-bit text only.
- Serving stack for the proof of concept: Ollama 0.32.15 at
  `http://localhost:11434/v1`, models `granite4.1:3b` and `granite4.2:3b`,
  both pulled. Shape documented in `builder/docs/serving-stack-shape.md`:
  4.2's reasoning arrives in a separate `message.reasoning` field (never an
  inline think block on this stack); the only switch that turns it off is
  `reasoning_effort: "none"`, which 4.1 rejects with HTTP 400, so the switch
  must be gated per model; tool calls are well formed on both; at a
  1024-token cap 4.2 in reasoning mode returns empty content two times in
  three, so labs either raise the cap to 4096 or turn reasoning off.
- Writing standard mirrors the two existing course trees, as numbers:
  `builder/docs/writing-standard.md` (student pages grade about 4.4,
  11-word sentences, prior page budgets; program-manager documents grade
  about 9, 18 to 20 word sentences). Gate: `ITSY_CONTENT=builder/content
  python3 -m tools.readability`.

## Files on disk (Phase 0)

| File | State |
|---|---|
| `builder/docs/email-header-realism.md` | done; every rule cited to an RFC section; placeholder-name banner added |
| `builder/docs/nlc-template-conformance.md` | done; 32 template-versus-prompt conflicts listed (Phase 1 item 8 input) |
| `builder/docs/serving-stack-shape.md` and `serving-stack-probe/` | done; raw JSONL of 54 probe calls kept |
| `builder/docs/phase0-candidates/` | three candidate designs and manifests; judges scored A 124, B 122, C 117; A won with grafts from B and C |
| `builder/docs/phase0-corpus-design.md` | done; critic's fixes applied; edited to grade 7.0 with every fact verified against the manifest |
| `builder/docs/phase0-corpus-design.html` | the same, rendered for the program manager with the six emails as an appendix |
| `builder/corpus/spec/` | corpus-spec.json (56 records), enums.json, categories.json, ground_truth.schema.json, phase0-sample-manifest.json |
| `builder/corpus/data/` | all ten data files; playbook.md rewritten to grade 5.2, 249 words |
| `builder/corpus/tools/` | parse_eml.py (the week 1 helper), validate_corpus.py, check_spec.py; both checkers pass |
| `builder/corpus/emails/teaching/` | 003, 006, 013, 019, 021: five finished, each passed parse, realism and safety verifiers |
| `builder/corpus/emails/batch/` | 032 (attachment stub, softfail): rendered, passed all three verifiers first time |
| `builder/corpus/ground_truth.json` | six records, label_version phase0-1.0, one indicator convention, 0 schema errors |
| `builder/corpus/README.md` | rewritten to grade 6.6 |

## Workflows

Workflow 1, run id `wf_0c7d8bdd-317`, completed 2026-09-03 (46 agents, no
errors). Its critic said: design, counts and data files are internally
consistent and mechanically verified; not approve-ready until (1) the blocked
Canvas test is stated plainly, (2) the ground truth records use one labeling
convention, (3) the promised sixth email 032 is rendered, (4) file locations
and inventories are reconciled, (5) small prose errors are fixed.

Workflow 2, run id `wf_d4587b21-294`, launched 2026-09-03 about 16:10 local,
does exactly those five things plus a section-by-section readability edit of
the design doc to the program-manager bar (grade at or below 9.5, sentences
at or below 18 words, no sentence over 45, no paragraph over 70), with a
fact-preservation verifier on every section.
Script: `~/.claude/projects/-Users-aaron-workspace-dev-ITSY1377-builder-corpus/8ebfb83f-3d81-4460-8822-9754df64a237/workflows/scripts/itsy1377-builder-phase0-polish-wf_d4587b21-294.js`
Journal: `~/.claude/projects/-Users-aaron-workspace-dev-ITSY1377/8ebfb83f-3d81-4460-8822-9754df64a237/subagents/workflows/wf_d4587b21-294/journal.jsonl`
Resume from the same session: `Workflow({scriptPath, resumeFromRunId: "wf_d4587b21-294"})`.
History: the first run was cut off by the usage limit at about 15:34 after six
agents (design-doc fixes and split, email 032 authored and verified by all
three lenses); every section-edit agent and the ground-truth regeneration
failed at the API. Before resuming at about 19:15, sections caught mid-edit
(02, 03, 05, 07) were restored from their .orig copies, the split was checked
byte-for-byte against the fixed document, and the script got a null guard on
the ground-truth result. The resume replays the six cached agents and runs
the rest live under the same run id.
If it was cut off: the design doc may be split into `builder/docs/phase0-edit-work/sec-NN-*.md`
(with `.orig` siblings). Concatenate the edited files in name order with one
blank line between them back into `phase0-corpus-design.md`, delete the work
directory, then run the two corpus checkers.

## Phase 1 complete

All three jobs finished. The blueprint answers the nine Phase 1 items plus the
coverage memo, and three adversarial audits found and fixed 62 defects across
it, including seven different lab point totals, a missing grade distribution,
seven sidebars sharing three subjects, and the week 5 lab having been described
rather than written out as the build prompt requires.

**The measured week 5 answer.** 294 agent runs, both models, four lab designs,
recorded in `builder/docs/week5-model-test.json` and reported in the markdown
beside it. Standardise on granite4.2:3b with reasoning off, in the design where
the student's code owns the stop condition: 29 of 30 exact tool paths, 30 of 30
correct stop reasons, 28 of 30 correct verdicts, 3,813 tokens and 4.1 seconds
per triage. Set `reasoning_effort` to `none` on every request,
for every model. It is NOT gated by model name: re-measured on 2026-09-04,
`none` returns HTTP 200 on both models and only `low`, `medium` and `high` are
refused by granite4.1:3b, with `"granite4.1:3b" does not support thinking`. The
old name gate matched the text `granite4.2` and so failed silently against any
hosted alias, leaving reasoning on for the term. granite4.1:3b is the documented
fallback: it ends every run for the right reason but varies the tool order, so
the rubric grades the stop reason and the trace rather than the order.

Reasoning mode is out. At a 512-token answer budget it returned empty content
18 times out of 18. At 4,096 it works and costs 83 seconds and about 7,900
tokens for one email.

Re-run each term with `python3 builder/lab/eval/week5_loop_test.py --all`.

The measurement is `builder/lab/eval/week5_loop_test.py`. It waits for the six
emails to appear and stop changing, then runs 138 agent loops: granite4.1:3b
and granite4.2:3b (reasoning off) at five trials each on a free variant and a
guided variant, plus granite4.2:3b in its default reasoning mode at three
trials on the free variant. The free variant lets the model pick any of the
three tools and decide when to stop, under a hard cap of four. The guided
variant is the fallback week 5: the sender reputation call is run for the
student, and the model chooses at most one more tool. It asserts the endpoint,
the model digests and the sha256 of every email before measuring, and writes
its JSON after every single run, so a cutoff loses one trial.

Already verified: `check_tools.py` reports all three tools agree with the
manifest on every field of all 56 records. The harness mechanics were smoke
tested against rendered emails and correctly caught a model calling one tool
twice.

**Two earlier measurements were thrown away, and the reason matters.** The
authoring workflow's verify-and-fix rounds regenerated four of the six week-5
emails while the sweep was reading them, so 234 runs scored the models against
files that no longer exist. The harness had recorded each input file's sha256
inside its own result JSON, so one comparison proved it. Everything was
re-measured against the final files in a single run. The digests in the final
record still match the files on disk, checked by
`builder/lab/eval/week5_report.py`, which refuses to report otherwise. Never
start a sweep while any agent can still write to its inputs, and always compare
the recorded digests before reading a number.

**Corpus defect, found by measurement and now fixed everywhere:** the manifest
gave email 012 the stop reason `step_cap`, but three tools exist under a cap of
four, so an agent runs out of tools first. All 294 runs stopped on
`tools_exhausted`. The manifest, that email's ground truth entry and the week 5
spec now agree. The cap is still taught, through the deliberately uncapped run
in the lab.

**A second finding for week 7:** email 012 is the corpus's genuine false
positive. It is a real vendor on a new domain with an unlisted link host asking
for names, and nothing any tool returns settles it. The recommended
configuration calls it correctly 4 times in 5; every other configuration
measured got it right 9 times in 44, and granite4.1:3b 0 times in 20. So week 5
awards no points for the verdict on it, and week 7 should expect it in the false
positive column. `week5_report.py` computes that split from the data rather than
quoting it.

## Phase 2 complete, 2026-09-04

Start Here, week 0 and weeks 1 and 2 are built and in Canvas (course id 6):
6 modules, 39 items, six course-level Outcomes, both labs at 100 points with
rubrics, every quiz answer carrying its own feedback, and four videos embedded
and playing.

**Decided in Phase 2 and still binding.** Course content is markdown using the
`:::` block format, which `tools/blocks.py` renders to the exact Cidi Labs
DesignPLUS classes the institutional template uses, so `tools/readability.py`
runs on it unchanged with `ITSY_CONTENT=builder/content`. Page file stems match
the names in that tool's budget table, so each page gets the right budget
automatically. The authoring contract is `builder/content/AUTHORING.md`; read it
before writing any page.

**The spine and the builder.** `builder/content/course.yaml` names all twelve
modules, 74 items, the five assignment groups summing to 100, and the six Canvas
Outcomes with one mastery scale. `builder/canvas/build_course.py` renders and
pushes it, is idempotent, and refuses to create an item whose source file does
not exist, naming it instead. It reads `CANVAS_BASE` and `CANVAS_TOKEN` from the
environment and never stores them. Three modes: `--check` (dry run), no flag
(build), and `--verify` (read Canvas back and compare against the spine).

**Six builder bugs found and fixed in Phase 2.** Each one is a trap the
remaining weeks would hit again.

1. `default_view=wiki` is refused until the front page exists, so settings are
   applied in two passes around the front page.
2. Outcomes need the course-scoped endpoint; the bare one returns 404.
3. `submission_types` must be repeated parameters, never comma-joined.
4. Canvas derives a new page's URL from its **title** and ignores the url in
   the path. The builder now looks the url up by title.
5. Answer feedback's key is `comments`. Canvas accepts `answer_comments`,
   answers HTTP 200 and stores nothing.
6. **One Outcome may align to at most one criterion per rubric.** Canvas
   answers HTTP 200 and creates no rubric at all. Week 1's lab had three
   criteria linked to CLO2 and therefore had no rubric while the build reported
   success. Recorded in `docs/phase1-blueprint/alignment-matrix.md`, last
   section. **Every week 3 to 7 rubric must obey it:** each Outcome links once,
   on the criterion that measures it most directly; the others are declared
   week expectations.

A seventh, in the video path: a page's video block renders a Common Cartridge
placeholder that an API build does not resolve, so every player would have
pointed at nothing with no error anywhere. `build_course.py` now uploads each
asset, rewrites `$IMS-CC-FILEBASE$/video/...`, and refuses to push a page
referencing an unbuilt asset.

**The verifier was strengthened** after it passed while an independent read-back
found four real defects. It now checks that every lab has a rubric, that the
criteria sum to the assignment points, that outcome links match the source file,
that quiz answers carry feedback, and that no stray assignment groups exist.

**Phase 2 gate results, 2026-09-04.** Canvas verify 0 problems. Video gates 4
videos all pass. Readability 30 pages, mean grade 3.83, limit 8.0. Corpus
validator 14 files 0 failures. check_spec 56 records all rules hold. check_tools
agree with the manifest on every field of all 56 records.

## Phase 3 in progress, from 2026-09-04

Phase 3 builds weeks 3 through 8, then the risk register, the final QA report
and the Canvas build.

### Where Phase 3 actually stands, 2026-09-05

There is no Phase 4. The build prompt defines phases 0 to 3 and ends at "WHAT
DONE LOOKS LIKE", which is the acceptance list for the whole build. The
instructor package, the risk register, the final QA report and the coverage
memo all sit inside Phase 3.

**Done and verified.**

| Thing | State |
|---|---|
| The corpus | Finished. 56 emails, 45 student and 11 exam, build clean, byte reproducible, three release files at 25/20/11, tools agreeing on every field. |
| The week 5 measurement | Intact. All six recorded digests still match the files on disk. |
| Weeks 3 to 7 content | 36 files written and audited: overview, reading, wrap-up, lab, discussion, rubric and self-check per week, plus w6-content-2. |
| Readability | 56 pages, mean grade 3.66, every page inside its budget. |
| Rubrics | All seven sum to 100, no Outcome linked twice, every top level equals its criterion points. |
| Self-checks | Points sum to 12, every answer carries feedback, one correct option each. |
| Discussion prompts | 109 sentences, verbatim from the approved specs, zero deviations. |
| The six CLOs | Verbatim from the build prompt in the spine and in the live Canvas Outcomes. |

**Not done.** `build_course.py --check` reports 111 objects built and 23
skipped, and the 23 are the work left:

- ten lab and sidebar notebooks for weeks 3 to 7, and six instructor solutions
- ten videos, two per week for weeks 3 to 7, plus rebuilding the four existing
  ones, which the config change correctly marked stale
- week 8: the overview page, the wrap-up page and the 30-item final exam
- the instructor package carried to weeks 3 to 8, the risk register and the
  final QA report
- the Canvas build of weeks 3 to 8
- the week 6 injection measurement, whose harness is written and which refuses
  to start until nothing else can write to the corpus

The notebooks are the critical path. The lab chain is serial because week N
carries week N-1's working code, the instructor solutions are the only proof
each lab is completable, and the walkthrough videos record real runs from them.

**Two things still want a decision.**

1. `docs/manifest-concerns.json` holds 133 self-contradictions the corpus
   authors reported rather than silently fixing. About a third are one bug in
   how `received_path_hint` counts hops. The triage workflow is written at
   `<scratchpad>/phase3-manifest-triage.js`. **Do not run it while anything
   else reads the corpus.**
2. Week 1's rubric floors its levels at 6 where every other week floors at 0,
   so the two map onto different ends of the mastery scale. With the
   calculation method corrected to `latest` the practical effect is gone. The
   inconsistency in what a grader records is a grading-policy call.

### Tools built in Phase 3, and what each one stops

`corpus/tools/build_corpus.py` runs every generator in id order from one
process, writes the three ground truth release files under `corpus/release/`,
and runs every validator. It also checks that the six emails the week 5
measurement recorded digests for are byte identical to what was measured. That
check is what stops a generator quietly invalidating the measurement that chose
the model and the week 5 design.

`lab/tools/run_notebook.py` executes a notebook the way a student's server
does. `--student` proves the notebook runs top to bottom with every TODO still
unwritten, which is the rule that matters most for a class with no programming
background. `--solution` proves the lab is completable and that the export cell
really wrote its artifact. All five existing notebooks pass.

`lab/notebooks/AUTHORING.md` is the notebook contract, written because weeks 1
and 2 use different unwritten-TODO placeholders and nothing recorded the rule.

`docs/phase3-findings.md` is the running defect log. Six entries so far,
including two silent Canvas failures found before they shipped. The final QA
report and the risk register are written from it.

**Stage A, the corpus.** Workflow `wf_59419446-c57` authors the 42 remaining
emails: one agent per email writes its generator, renders it and runs both
validators in a private scratch copy, then two independent verifiers check it,
one for fidelity to the manifest and one for safety and realism. Only the
generator file is written back to `builder/corpus/tools/generators/`; the
generators are run against the real tree afterwards, in id order, by one
process. That is deliberate: 42 agents writing `corpus-spec.json` and
`ground_truth.json` at once would corrupt both, which is the trap recorded in
`memory/itsy1377-measurement-traps.md`.

Exam-only emails 046 to 056 render to `builder/instructor/exam-emails/`, never
under `corpus/emails/`, so nothing a student can reach holds them before the
exam. `validate_corpus.py --emails` points at that folder.

Still to do after Stage A:
- Split `ground_truth.json` into `ground_truth_teaching.json`,
  `ground_truth_batch.json` and `ground_truth_exam.json`. Week 7 loads the
  batch file; the other two ship in the instructor package.
- Rebuild `spec/phase0-sample-manifest.json` from the rendered files.
- Weeks 3 to 7: overview, reading, wrap-up, lab assignment, discussion, rubric,
  self-check, sidebar notebook and lab notebook. Week 8: overview page and the
  30-item final exam.
- Ten videos, two per week for weeks 3 to 7.
- Instructor package: solution notebooks for weeks 2 to 7, announcements for
  weeks 3 to 7, and the updates to grading notes and failure modes.
- Risk register, final QA report, Canvas build and verification.

**Never re-render the existing 14 emails.** The week 5 measurement recorded the
sha256 of 004, 005, 007, 010, 011 and 012 inside its own result file. Changing
those bytes invalidates the measurement that chose the model and the week 5
design.

### Week 3 repair pass, 2026-09-04

Three audits reported eleven findings against week 3. Seven were acted on, two
were rejected on the evidence, and two are escalated because they cannot be
closed inside week 3.

**Fixed.**

1. **Emails 017 and 025 rendered.** `gen_017_fenwright_pay_statement_ready.py`
   and `gen_025_larkseal_review_encoded_subject.py` were run individually, not
   through `build_corpus.py`, so none of the existing 14 emails was re-rendered
   and the week 5 digests still hold. Ground truth is 16 records, the manifest
   was rebuilt with `gen_sample_manifest.py`, and the three release files were
   rewritten by calling `build_corpus.split_ground_truth()` on its own.
   `validate_corpus.py`: 16 files, 0 failures, the one permitted 003 warning.
   `check_spec.py`: 56 records, all rules hold. The 005/025 matched pair is now
   real: 005 is benign with `body_only_read` malicious, 025 is malicious with
   `body_only_read` benign, and 025's display-name check fires against
   `larkseal.example`.
2. **Week 3 token estimate recomputed** over all six emails, using `body_text`,
   the key the labs send. Mean body is 737, not 706. Per-run total is about
   9,600 rather than 9,500, and `grade-distribution-and-tokens.md` carries the
   new row and course totals. The facts block term is still 344 from three
   emails and cannot be remeasured until the week 3 notebook ships `FACT_ORDER`
   and `FACT_LABELS`.
3. **`course.yaml` outcome scale** now matches `alignment-matrix.md` sections 8,
   9 and 10: four ratings with the standard labels. `calculation_method` had
   already been corrected to `latest` earlier in the day; the five-level scale
   with its unreachable 1-point "Beginning" rating had not.
4. **The blueprint now agrees with the shipped rubric.** `alignment-matrix.md`
   section 11 and the section 3 CLO1 row no longer claim supporting CLO1 links
   on week 3 criteria 3 and 4, and carry a dated amendment saying CLO1's outcome
   data comes from criterion 2 alone. `week-03-spec.md` carries the same
   amendment in its rubric sketch and its objectives section. **The rubric was
   not changed:** the Canvas one-link constraint is real and already recorded.
5. **Glossary** gained a "Display-name mismatch" row, which AUTHORING section 6
   requires. The page was at 1,594 of 1,600, so the intro's second sentence, a
   duplicate of both the keyfacts row and the "How to use this page" section,
   came out to make room. Now 1,596.
6. **Two overclaims removed.** `w3-wrap-up.md` and `w3-self-check.yaml` q5 told
   students what their own run did, as fact, while the lab and the discussion
   hedged the same outcome and nothing in the repository measures it. Both now
   read in the lab's register.
7. **An unsupported model claim removed** from `w3-content.md`: it attributed
   verdicts to week 1, which produces none, and asserted that urgent words score
   high, which no artifact records.

**Rejected, with reasons in the repair report.** The suggestion to change
`tools/cartridge.py` to read `group["key"]`, `path.stem` and `criterion["levels"]`
would break `content/funded` and `content/constrained`, which are what that tool
actually serves. And the suggestion to add the continuity promise to
`w3-overview.md` would make week 3 the only week besides week 1 to carry it on a
page; week 2 carries it in the overview video narration and in notebook cell 1,
which is where the code ledger puts it.

**Escalated, both blocked outside week 3.**

- **The two week 3 videos.** `w3-overview.yaml` and `w3-walkthrough.yaml` do not
  exist and no w3 mp4 is built, so `w3-overview.md` and `w3-content.md` cannot be
  pushed. This is Stage E, which waits on Stage C: a walkthrough shows a real run,
  `builder/lab/notebooks/` holds weeks 0, 1 and 2 only, and
  `builder/instructor/solutions/` holds `w1-lab-solution.ipynb` alone, so the no
  spoiler gate has nothing to read. Week 3 cannot ship until Stage C runs.
- **No rubric ladder gate runs on `builder/content`.** `tools/cartridge.py`
  cannot load this tree at all. The ladders were checked by hand instead: all
  seven rubrics sum to 100 and match the spine, no Outcome is linked twice, and
  every ladder is strictly descending with a unique top equal to its criterion
  points. Week 1 is the exception worth a decision: its four ladders floor at 6
  rather than 0, so its lowest rating does not map onto the "No evidence 0"
  mastery rating. Untouched, because week 1 is not this pass.

### The carry-forward chain reconciled, 2026-09-05

`lab/tools/check_chain.py` is new and it reported 11 drifts. Six repair agents
fixed six weeks in parallel and each could write only its own week, which was
the right rule, so a fix to week 2's `strip_reasoning()` never reached the copy
of it in weeks 3 to 7. All 11 are closed, in 12 files: the six lab notebooks
for weeks 2 to 7 and their six instructor solutions. No name, no signature and
no cell number changed.

The rule applied is that the week which first defines a function owns it, and
every pair was read before it was propagated.

| Function | Owner | What was actually different |
|---|---|---|
| `strip_reasoning()` | 2 | Docstring and comments only. Weeks 3 to 7 claimed it strips "any code fences"; it strips only a fence that starts the answer. Week 2's wording carried forward. |
| `loop_prompt()` | 5 | Weeks 6 and 7 called `build_grounded_prompt()`, which sends the playbook and the body a second time (`start_messages()` already sends both) and puts the answer schema in the first turn, which is what week 4 measured as the thing that stops tool calls. Week 5's version is also the one `lab/eval/week5_loop_test.py` measured. Week 5's version carried forward. |
| `guarded_triage()` | 6 | Week 7 had lost the recipient addresses from `hosts_extracted` and the `tokens_written` key, which is the number `TOKEN_CAP_PER_RUN` caps. Week 6's version carried forward. |
| `hosts_named_in()` | 6 | Week 7 had lost the line that drops a scheme and a path, so a host written as a full link was missed. Week 6's version carried forward. |
| `run_triage()` | 6 | Week 7 set a sixth stop reason, `"run_loop() is not written yet"`, on a branch that cannot run because week 7 ships `run_loop()` pre-written. Week 6's version carried forward. |
| `schema_text()` | 2, promoted from 7 | **The one that went the other way.** Week 7's body renders any key count and a `sentences` rule, and week 7's own comment read "Two lines of this are new in week 7", which is a later week editing an earlier week's cell. Week 2 now carries `KEY_COUNT_WORDS` and both rules, and weeks 3 to 7 carry the same. On a four-key schema the rendered block is byte-identical to what week 2 printed before. |

**Ledger and spec changes this asks for, and which were not made here.**

1. Section 12 says "Five signatures were designed to grow". It is six.
   `schema_text(schema)` belongs on the list: it takes the schema and now
   renders any key count and a sentence rule, so week 7 passes
   `OUTPUT_SCHEMA_V2` without reopening week 2's cell.
2. Week 2's pre-written table and its cell 6 list need `KEY_COUNT_WORDS` beside
   `OUTPUT_SCHEMA` and `schema_text()`.
3. Week 2's table describes `strip_reasoning()` as removing "code fences". It
   removes one that starts the answer.
4. Week 5's table row, and `week-05-spec.md` sections 3 and 15.1, describe
   `loop_prompt()` as joining `LOOP_INSTRUCTIONS` to "week 3's grounded
   prompt". The shipped function joins them to `CLASSIFY_INSTRUCTIONS`, the
   facts block and the known-good list only.
5. Week 6's paragraph lists five keys `guarded_triage()` adds. It adds six;
   `tokens_written` is missing.
6. Week 6 ships `run_triage()`, `hosts_named_in()`, `fence_check()`,
   `fenced_email()` and `guarded_facts_text()` pre-written, and the ledger's
   week 6 table names none of them. Two of the five are functions that drifted.

**Gates, 2026-09-05.** `python3 builder/lab/tools/check_chain.py`: "the chain
holds: every function carried forward matches the week that defined it, and
every solution matches its lab". `python3 builder/lab/tools/run_notebook.py
builder/lab/notebooks/ --all --student`: "15 notebook(s), 0 failure(s)", weeks
6 and 7 taking 147s and 208s of real model calls.



## 2026-09-09, evening — week 6 measured, not yet repaired

**Week 6 is in progress.** Nothing is fixed yet and nothing is pushed. What
exists is a pre-registration, a rig, and one completed probe whose result is
decisive. Everything is under `docs/week6-measurement/`.

**The rig.** `mkprewritten.py` lifts week 6's pre-written cells out of both
notebooks into one importable module, so the code under test is the code
students run. `w6_rig.py` is the shared harness: it refuses to start unless a
live call comes back with a non-zero token count, and it writes the sha256 of
every corpus email, both notebooks and the rig into every result file. Set
`W6_RIG_DIR` to a directory holding `w6_solution.py` and export
`ITSY1377_API_KEY`. The key and the Canvas token are in this session's
scratchpad, copied forward from the 2026-09-03 session; they are never in the
repository.

**Written before any probe ran:** `docs/week6-measurement/prereg-claude.md`,
with two dated amendments. Amendment 2 states plainly that it was written with
probe 1 at 49 of 88 rows and lists what had already been seen.

**Probe 1, the week as it ships. 88 runs, 0 failures, granite-3b.**
`baseline-granite-3b-8.json`.

  - **P1a confirmed.** The guard changes the verdict on payload-FREE emails in
    65 percent of runs and on payload-carrying ones in 37.5 percent. The
    eleven-email table is not tracking the attack.
  - **P1b.** Undefended 013 and undefended 024 return the same verdict in 8 of
    8 paired runs, and the guarded pair does too. The payload moves nothing.
  - **P1d.** The fact check found 0 problems in all 88 runs, so the reading's
    "email 020 is where the third rule fires" is measured false.
  - **P1g.** Every confidence returned was 0.80, 0.85 or 0.95. Nothing landed
    under the 0.7 floor in 88 runs, against four documents naming 009 and 012.
  - **P1c.** The only escalation reason that ever fired was
    `injection_detected`, on 014, 8 of 8 — and it reads a corpus property, not
    a model judgement. 014 is the only lab email with hidden HTML text.
  - **P1e.** Largest tokens_written was 289 against a cap of 4000. Largest
    total was 8,017.
  - **Accuracy: 66 of 88 undefended, 46 of 88 guarded.** Every guard-caused
    loss is a false negative. Both twins are ground-truth malicious, so the
    guarded arm's moves on 013 and 024 are false negatives, not artifacts.

**Probe 7, zero model calls, already done.** `fence-escape.json`. An attacker
who writes `<<<REPORTED_EMAIL_BODY_END>>>` into the body moves 142 characters
of their own text onto the team's side of the fence, and `fence_check()` still
reports the whole body inside, because it finds the fence with `rfind()`.

**Probe 2, the one-line patch that puts the body back in `run_triage()`'s
closing call. 88 runs on granite-3b, 0 failures.** The payload effect appears
at the ceiling: undefended 013 comes back **benign 8 of 8** and undefended 024
comes back **malicious 8 of 8**, both ground-truth malicious. P2a and P2b pass.

**And the guard fails both of its own thresholds.** P2c: guarded 013 stays
benign 8 of 8, so the guard does not take the attack back. P2d: guarded 024
moves from correct to wrong 8 of 8, so the guard breaks the message with no
attack in it.

**Probe 3, the recipient held still. 32 runs, 0 failures.** With both twins
addressed to the same mailbox, either mailbox, 013 is benign 8 of 8 and 024 is
malicious 8 of 8. The payload is the cause and the recipient record is not, so
6.2's demonstration is single-variable.

**The model question is closed, and the answer is granite-3b.** On granite-8b,
under the **shipped** code, the undefended answer on 024 is unreadable in 6 of
8 runs, and 7 of 8 under the patch, so the parse failure is the model's and not
the repair's. `model-selection.md` puts week 6 on granite-8b and is wrong; its
week 1 row is stale in the other direction.

**Probe 6, computed from probe 1's own rows at no cost.** The payload steers
tool order in 8 of 8 paired runs: 013 goes sender, recipient, urls and 024 goes
sender, urls, recipient. Both end `tools_exhausted`, so nothing is lost -- the
paragraph delays the link check by one step, every time.

**Probe 5, the decomposition, running.** At 59 of 112 rows it has already
refuted five candidate causes of the guarded arm's collapse: the markers, the
rules, the hidden-HTML line, prompt length and the dropped known-good list.
Every arm shaped facts-plus-body-plus-schema returns benign on both twins,
including one carrying neither rules nor markers. Only `loop_prompt()` keeps
the clean twin malicious, and the one thing it has that no guarded arm has is
`CLASSIFY_INSTRUCTIONS`. Probe 5b tests exactly that and is chained behind it;
its thresholds are in amendment 3, written before it ran.

**Probe 5d found it, and 5e confirmed it.** The build-up design -- add one
thing at a time to the prompt that works, instead of removing one thing at a
time from the prompt that fails -- found the cause on the first pass. Removing
week 3's known-good host block from the working prompt turns the injection-free
twin benign **0 of 8**; adding the markers, `GUARD_RULES`, the hidden-HTML line
or the relabelled facts header does nothing at all. Restoring both the
classification instructions and the known-good block to the guarded prompt
returns it to malicious **8 of 8**, with or without the schema block, while 013
stays benign 8 of 8.

**The teardown design was the error, not the sample size.** Fifteen arms all
returned 0 of 8 and I read that as fifteen candidates cleared. When several
elements are each independently sufficient, removing any one leaves the rest
doing the work, and teardown cannot find a cause however many arms it runs.

**Codex reviewed it and was right against me on the most dangerous item.**
Report at `docs/week6-measurement/codex-review.md`, prompt beside it. **My
proposed fence repair was a fail-open and is withdrawn.** `guarded_triage()`
builds the prompt from the unsanitized body, checks the fence, and on failure
sets `prompt_text = loop_prompt(parsed)` -- the undefended prompt. Making
`fence_check()` honest would therefore let an attacker who writes `BODY_END`
into the body switch the guard off. Reproduced at zero model calls. The
replacement is to sanitize once before any use and to **fail closed** by
escalating.

Codex also established that the 72-point CLO4 criterion asks for
unguarded-against-guarded numbers and never for the twin comparison, so
objective 6.2 is displayed and graded nowhere; that "every guard-caused move is
a false negative" belongs to probe 1's body-blind baseline and not to the
repaired week, where 021 is a corrected false negative and guarded accuracy is
44 of 88 against 40; and that the known-good finding is a context-dependent
interaction needing a 2x2 with placebo arms before it may be stated as a cause.

**The repaired eleven-email table changed the headline again, and made it
cleaner.** With the body in the verdict call AND week 3's grounding restored to
the guarded prompt, the two columns are **identical on all eleven emails: 0
verdict changes, 8 of 8 in every row**, undefended accuracy 40 of 88, guarded
accuracy 40 of 88.

So "the guardrails cost 23 points of accuracy", from probe 1, was **entirely an
artifact of the guarded prompt dropping week 3's grounding**. With the grounding
back, the fence's effect on the verdict is exactly zero: not harmful, not
helpful. Its only observable effect anywhere in the lab is the
`injection_detected` escalation on 014, which reads a corpus property and is not
the fence.

That is the strongest version of the week. 6.2 is demonstrated 8 of 8 in **both**
columns, so the twin comparison works whichever agent the student runs. 6.3 gets
a crisp evidenced answer: the guardrail changes no verdict in 88 runs and does
not stop the injection, so it is not acceptable. And 6.1 gains stakes it never
had, because building the prompt without the grounding breaks the injection-free
twin 8 of 8. It also confirms, by measurement, what the SOC reviewer argued from
field judgment: delimiters plus "treat this as data" are advisory, and reduce a
rate rather than creating a boundary.

**Caveat on that table.** It came from the interim patch, which appended the
body unconditionally and so gave the guarded arm two copies -- exactly Codex's
objection. `w6_final.py` implements all six changes including the membership
test, the fail-closed sanitation and the schema call, and is the run that
measures what ships. It needs a second run for the noise floor before any
number reaches a page.

**The code that will ship is written down** at
`docs/week6-measurement/final-code-shape.md`, including why the naive fence
repair was withdrawn and what fail-closed looks like.

**All measurement is finished.** The confirmatory 2x2 (144 runs) and the
noise-floor pair (two runs of 88) are in, with results in
`docs/week6-measurement/README.md` and thresholds in amendments 5 to 7.

  - **The cause is confirmed with a placebo.** Both the classification
    instructions and the known-good host block are needed: K returns the
    injection-free twin to malicious 8 of 8, and F, G and H each leave it
    benign 0 of 8. Neutral prose of the same length in the same position
    restores nothing, so it is the block's content and not its bulk.
  - **Unpredicted, and the best thing in the week.** Adding the attacker's own
    domain to the known-good list flips the verdict back to benign 6 of 8. The
    model reads that list as evidence.
  - **The noise floor is the cleanest result of the pass.** Two independent
    runs of 88: every email 8 of 8 identical in both arms, both times, 0
    verdict changes, 0 under the confidence floor, 0 fact-check problems.
    Accuracy 40 of 88 in both arms in both runs. `schema_errors()` fires 9 and
    11 times of 88.
  - **Two results reported against the hypothesis.** 012 is ground-truth
    benign and the grounding makes the model call it malicious, so the repair
    fixes 024 and breaks 012. And the tool-order control did not hold globally
    (10 of 144); all ten deviations are outside the decisive cell, which is
    single-order 8 of 8.

**Codex reviewed the repair and was right against me.** `codex-review.md`. My
fence fix was a fail-open and is withdrawn: `guarded_triage()` fell back to
`loop_prompt()` when the fence check failed, so an honest check would have let
an attacker switch the guard off. The replacement sanitizes once before any use
and escalates as `fence_broken`. **Verified end to end after the edit:**
`strip_markers` finds the marker and leaves none, the prompt still fences the
whole body, and `guarded_triage` returns `escalate: True, reason: fence_broken`.

## What has been edited, 2026-09-09 late

**Content and docs: 155 edits across 18 files.** Applied by one agent per file
against canonical wordings, then verified: every YAML parses, every `:::` block
balances, `tools.readability` passes at 74 pages, warmth 17.7 per 1k. Four
edits that the agents correctly refused to guess at were resolved by hand once
the numbers landed, including the retracted "emails 009 and 012 sit under the
floor", which is now gone from every page.

**The four notebooks carry all six code changes.** 47 insertions and 5
deletions each, JSON shape preserved. `check_chain.py`: 69 functions, 51
carried, the chain holds. `run_notebook.py --student`: 19 cells, 2 TODO, 0
failures.

Two gaps found in my own first pass and closed: week 7's
`build_guarded_prompt` has a different body and did not match the first
replacement, which would have left its `guarded_triage` calling a changed
contract; and five more call sites per week 6 notebook still passed the bare
facts where the grounding now goes.

**Week 6 is done, pushed and verified.** 39 objects to Canvas, `--verify` 0
problems. The full record is `docs/lab-fix-log.md` under "Week 6", the numbers
are in `docs/week6-measurement/README.md`, the code that shipped is described in
`final-code-shape.md`, and Codex's review is `codex-review.md`.

Also closed on the way: week 5's two videos, which had been stale since before
this pass began because `w5-content.md` was edited ten minutes after they
rendered and the gate ran before that edit. All four videos re-rendered; 14
videos, nothing stale.

## Blocking, and it needs a hand: the notebook site is behind

**Week 6 is on Canvas and not yet in front of a student.** Canvas hands out
`ExternalUrl` items pointing at `notebook.bashtion.dev`, and that site still
serves the pre-repair notebook: 112,028 bytes live against 121,538 in the
repository. Everything the week 6 pass fixed in the lab code stops at the
Canvas link.

The tree is staged and checked at 73 files, 1,108 KB, 15 notebooks, no
`never_ship` name present and no solution file in it; `check_site_files.py`
passes. It needs syncing to `/var/www/jupyterlite` on the jupyterlite guest.

**I cannot reach that guest.** It is off the tailnet, which was deliberate and
is the residual item in `docs/lab-open-issues.md`. No ssh host here resolves
it. Re-stage with:

    python3 builder/lab/tools/stage_notebook_site.py <dir>
    python3 builder/lab/tools/check_site_files.py <dir>

**Do it before anyone opens week 6, not after.** This repository's own
measurement says a redeployed notebook never reaches a student who already
opened it: the browser copy shadows it permanently, with no merge and no
warning, and corrections have to ship under a new filename. The course is
unpublished, so today that costs nothing.

**And the gate that would have caught this does not exist.** The blind run
found the site one revision behind the repository and nothing reported it;
`lab-fix-log.md` carries it as queue item Q9. Two weeks running have now shipped
against a stale site. A check comparing the served files to the staged tree is
cheap, and it belongs before week 7 rather than after.

## Week 7 is next

Its logged defect is that the schema is never validated. Note two things this
pass leaves on its doorstep.

**Week 7 carries week 6's repaired code** and was re-run to prove it: its
solution is clean at 321 seconds on the changed `run_triage` and
`guarded_triage`. But its own measured numbers predate the repair, so anything
week 7 states about what those functions do has to be re-checked before it
ships.

**`check_chain.py` compares only `ast.FunctionDef` nodes**, so every constant
week 6 owns -- `GUARD_RULES`, `BODY_START`, `BODY_END`, `TOKEN_CAP_PER_RUN`,
`CONFIDENCE_FLOOR` -- drifts between weeks 6 and 7 unguarded. Extending the
collector to uppercase module-level assignments, with an allowlist for the
deliberately per-week ones, is cheap and would have caught a real class of
error. Prove it flags a seeded divergence before trusting it.

**Still open from this pass, deliberately.** The delimiter-escape paragraph is
not on any student page: the code now sanitizes and fails closed, but no
teaching email carries a marker, so nothing a student runs demonstrates it. It
wants either a corpus email with a written-in marker or a pre-written cell that
builds one, and that is a week 7 or corpus decision rather than a week 6 one.

**Two workflows completed and their output is in the repository.**
`audit-findings.json` holds 50 findings that survived an adversarial verifier
(71 raised, 21 refuted) plus a synthesis with six ranked measurement
questions. `panel-reconciliation.raw.txt` holds the merged week 6 work list
from the blind student run and the five panel reports, 84 items, with twelve
reviewer disagreements and the evidence that settles each.

**The three things that decide the shape of the week, and none is settled yet.**

1. Does the payload move the verdict once the closing call carries the body?
   Probe 2 answers it.
2. What causes the guarded arm's malicious-to-benign collapse? The candidates
   are the markers, `GUARD_RULES`, the dropped known-good host block, the
   hidden-HTML line, and prompt length. Probe 5 takes them apart one at a time
   and is not written yet.
3. Which model week 6 ships. The notebook defaults to `granite-3b`;
   `model-selection.md` says `granite-8b` on the strength of 510 runs whose
   prompts are not the notebook's, so that decision has to be re-earned.

## 2026-09-09, later — week 5's cap made to fire

Weeks 1 to 5 are done, pushed and verified. Week 5 went out as 38 objects in
3m14s with `--week 5`, and `--verify` reports 0 problems. Detail in
`docs/lab-fix-log.md` under "Week 5", numbers in `docs/week5-measurement/`.

`step_cap` fired **0 of 48** runs and the model never repeated a tool once.
With three usable tools under a cap of four, the cap needs two wasted steps to
bind, and the model is told not to repeat. The corpus never planned for it
either: no lab email carries `expected_loop.stop_reason: "step_cap"`.

Three things worth carrying forward:

1. **A pre-registered pass is not a correct fix.** My `max_steps=2` cell met
   every threshold I set, control included, and was still wrong: objective 5.1
   says a *four*-step cap, and demonstrating one at two silently redefines it.
   Codex caught that. Check the fix against the objective's wording, not only
   against the thresholds.
2. **The idiom is now consistent across three weeks.** Week 4 swaps `ask_model`
   for a fixture to test the contract, week 5 swaps `ask_with_tools` for a
   script to fire the step cap, week 6 cell 17 lowers the token cap on purpose.
   Forcing a control and saying so is how this course demonstrates mechanisms.
3. **Fixing a page is not fixing the week.** The same false cap arithmetic sat
   in the reading, the wrap-up and the self-check. Two of the three were only
   found because the question "does this still align?" was asked after the
   reading was already fixed.

Logged, not done: with three tools a cap of four only binds after two wasted
steps, so the number is arguably mis-set — but 5.1 names four and weeks 6 and 7
share the value. And `run_notebook.py --expect-artifact` passes when a cell
merely prints the file name; it never opens the file.

Week 6 is next. Its logged defect is that the verdict call has no email body.
It inherits `run_loop()` and every week 5 helper unchanged and passes its token
guard through `step_guard`.

## 2026-09-09 — week 4 rebuilt around a matched pair

Weeks 1, 2, 3 and 4 are done, pushed and verified. Week 4 went out as 38
objects in 3m32s with `--week 4`, and `--verify` reports 0 problems.
Everything is in `docs/lab-fix-log.md` under "Week 4", with the numbers in
`docs/week4-measurement/` (eight probes, ~1,100 calls, README plus the
pre-registration written before results).

The defect, in codex's wording: *week 4 operationalized objective 4.3 with a
five-confound comparison and then graded a causal explanation of it.* Cell 14
put week 3's grounded prompt against this week's two-turn tool prompt and
called the difference the tool's doing. A control arm carrying a tool message
that reads "no record available" moves email 003 the full distance anyway.

Two pre-registered thresholds failed and both failures changed the fix. No
email met the bar for the tool being the active ingredient under free tool
choice. Email 017 failed confirmation and does not ship. **Email 018 passed
twice at 8/8 on all four arms** and carries the new cell 15: the same email
judged four times, only the tool result changing, showing a true fact about the
sender walking a correct verdict backwards.

Three things worth carrying forward:

1. **Prompt length, not the playbook, collapses tool choice.** A length-matched
   block of neutral filler concentrates the model onto
   `check_sender_reputation` harder than the playbook does, 66 of 72 against 59
   of 69. Do not "fix" tool diversity by editing prompt text.
2. **Real records pin the verdict; withheld controls wobble.** Every
   real-record arm was 8/8 and identical across two runs. Every instability was
   in the withheld arms. A withheld arm belongs in a measurement record, never
   printed to a student as a baseline.
3. **`LAST_CALL["answer_was_empty"]` now exists in all 14 lab notebooks**, set
   in `send_request()` before the empty-slot notice is substituted. It was
   added because nothing inside a notebook could tell an empty answer from the
   notice standing in for one. Weeks 5, 6 and 7 can use it. The edit is exactly
   +9/-1 in every file and the chain still holds.

Week 5 is next. Its logged defect is `step_cap` unreachable. Note that week 5
inherits `TOOL_TURN`, `TOOL_INSTRUCTIONS`, `TOOL_SPECS`, `start_messages()`,
`ask_with_tools()`, `run_tool()` and `tool_result_message()` byte-identical
from week 4, and none of them were touched.

The three `test-` models are still in `/etc/litellm/config.yaml` from the week 3
study (backup `config.yaml.bak-w3study`). No student key can reach them.

## 2026-09-08 — week 2 rebuilt around a measured retry

**The defect.** Objective 2.3 is "retry a failed answer with the schema
problems added to the new prompt", and the retry fired **once in 260**
classifications. The blind student's clean run was not luck. Three related
defects came with it: sidebar 2C and week 0 cell 92 both taught a loop that
stops when a value *arrives* rather than when a check *passes* (week 0 cell 91
called that shape "the exact shape of the week 2 retry", which was false and
made the retry impossible); cell 13's stated success test omitted the `ok`
column, so a schema-failing answer passed it; and every load failure collapsed
into one unactionable sentence.

**What the measurement killed.** Tightening the indicator count looked ideal
and is dead: with the cap at 3, **42% of runs ended with no answer at all**,
and across both caps 28 retries produced 23 give-ups. granite-3b will not
shorten a list when told to. An under-specified prompt buys nothing over
forced truncation — both fail at the load stage and yield the same generic
line.

**What proved the mechanism.** Every recovery measured up to that point was
confounded, because try 2 is an ordinary call that passes anyway. An isolation
probe settled it: with the problems appended, 24 of 24 passed and returned
0.85; on a bare re-ask, 0 of 24 passed and every reply stayed at 0.95.

**The design.** A week-2-only confidence reporting ceiling of 0.9, living once
in `OUTPUT_SCHEMA` so `schema_text()` renders the same limit `schema_errors()`
enforces. Measured twice, at 12 and 20 runs per email: 001 and 004 accept on
try 1, 002 and 003 retry and recover, **128 classifications, 64 retries, 64
recoveries, zero give-ups.** The material calls 0.9 a reporting rule and never
a calibration improvement — the model obeying a boundary is not the model
becoming less sure. No student-facing sentence names which email retries.

**Shipped.** Week 0 cells 91-93 and 96; sidebar 2C rewritten and a new sidebar
2D for empty-list falsiness and `isinstance()`; the lab and solution as one
atomic unit, 16 cells to 17, with `answer_source()`, a saved contract test and
`retry_demo` in the export; all four content pages, assignment, discussion,
rubric, self-check, both videos. Time table 310 to 325 minutes and it adds up.

**One deviation.** D4 changes the body of `schema_errors()`, which weeks 3 to 7
carry verbatim, so the plan would have left `check_chain.py` red with five
mismatches. The single changed string was propagated to those five labs and
five solutions instead. No behaviour changes anywhere; it is only what a load
failure reports.

**A tool bug found on the way out.** `tools/warm_pass.py` contracts `is` onto
whatever precedes it, including phrase subjects, and had already shipped eight
broken sentences: "Handling it's the work", "What to take from it's the shape",
and six of "Nothing here's graded". All eight fixed, which made six videos
stale; all six rebuilt. **The tool is still wrong and will reintroduce them on
the next warm pass.**

**Records.** `docs/week2-measurement/` holds six scripts, the 160-answer pool
and a README covering what each experiment killed and what to re-measure after
any model change. `docs/lab-fix-log.md` carries the full week 2 section.

**Gates.** Chain holds. Content and code agree. Readability passes, week 2 at
grade 3.8 to 4.0 against a course mean of 3.77, every page inside budget,
contractions at 17.4 per 1k against a course mean of 17.4. All 14 videos pass.
Site staged at 73 files and deployed to notebook.bashtion.dev, verified file by
file against the staged tree, solutions still 404. Canvas: 154 objects, 0
skipped, `--verify` 0 problems, no `$IMS-CC-FILEBASE$` placeholders on any week
2 page, six media references all 200, 14 videos present with no duplicates.

Nothing is committed.

## 2026-09-07 — the course moved onto the notebook server

All fifteen student notebooks and the corpus are baked into
notebook.bashtion.dev. Canvas no longer hands out `.ipynb` files.

**Notebooks.** All fourteen lab and solution files carry the browser stack: a
guarded `piplite.install("requests")`, a pasted key with an environment
fallback for automated runs, `NOTEBOOK` as the one line that differs per week,
per-request tags, `budget_left()` and `backup_my_work()`. Cell counts and every
markdown cell are unchanged, because the Canvas assignment pages cite cell
numbers. Seven distinct configuration cells, one helper cell byte identical
across all fourteen, `check_chain.py` green.

**The site.** `lab/tools/stage_notebook_site.py` builds what the server serves
from `student_files` in course.yaml, never from a folder walk, and refuses to
hand back a tree holding anything named in `never_ship`. 73 files, 1.2 MB:
15 notebooks, 45 emails, 13 data and tool files. Solutions and
`corpus-spec.json` return 404 from the public site, checked.

**Canvas.** The fifteen File items became `ExternalUrl` items pointing straight
at `notebook.bashtion.dev/lab/index.html?path=<name>.ipynb`. build_course.py
gained a `url` item type for it. `--verify` reports 0 problems.

### Three things that had stopped being true

`canvas-and-tech-support` promised "your files stay on the server all term" and
advised trying a different browser. Both were false and the second destroys
work. Corrected, and the new orientation page **Using the notebook server**
(grade 3.14, 297 words) carries backup, restore and the limits.

Week 1 told students a key would be found in their environment. It is pasted
now.

Weeks 3 and 4 said "no cell in this course prints key material, so no
screenshot of one can show any". The key is pasted into the configuration cell,
so a screenshot of it now leaks the key. That was the most consequential of the
three.

### Two properties measured, both load bearing

**A redeployed notebook never reaches a student who already opened it.** Their
browser copy shadows it permanently: no merge, no warning. Corrections have to
ship under a new filename. Tested with a persistent browser profile.

**Student work exists only in one browser on one machine.** `?reset` destroys
it. Hence `backup_my_work()` in every export cell, proven in a real browser to
capture a saved edit into a downloadable zip.

### A near miss worth remembering

`run_notebook.py` injects `ITSY1377_API_KEY=local-run` for a local server that
ignores keys. Once the notebooks defaulted to the live proxy, every gate run
fired at production: 201 failed calls before the operator noticed the log. The
gate now declares `ITSY1377_BASE_URL` itself; a full run went from 215 request
lines on the proxy to 0. Nothing in the tooling objected to a check aiming at
production, and nothing would today.

## 2026-09-06 — lab infrastructure

Two guests on remotelab, both built, both on reserved addresses after a
duplicate-address stop (recorded below).

| guest | lab ip | mac | tailnet |
|---|---|---|---|
| litellm | 10.171.0.40 | 52:54:00:d1:30:65 | litellm.bopp-quail.ts.net |
| jupyterlite | 10.171.0.41 | 52:54:00:fc:7a:80 | jupyterlite.bopp-quail.ts.net |

**litellm** runs LiteLLM 1.100.0 in a venv under a system user, bound to
`127.0.0.1:4000` and nothing else, with Postgres 17 on loopback for virtual
keys and budgets. Caddy on `127.0.0.1:8080` is the student plane: a
default-deny allowlist that proxies only `/v1/chat/completions`,
`/v1/completions`, `/v1/embeddings` and `/v1/models` and 404s everything
else. Admin is `tailscale serve` on the tailnet only. Secrets are root-only
600 files under `/etc/litellm`, and the service user cannot read them --
systemd loads them as root before dropping privileges.

**jupyterlite** runs JupyterLite 0.8.3 built to `/var/www/jupyterlite`,
served by Caddy on `127.0.0.1:8080`.

Both tunnels are up and verified against the public URLs, not from config:
`api.bashtion.dev` -> litellm :8080, `notebook.bashtion.dev` -> jupyterlite
:8080. Unauthenticated `/v1/models` is 401, a budgeted student key is 200,
and `/ui`, `/key/*`, `/user/*`, `/team/*`, `/sso/*`, `/metrics` and
`/health/liveliness` are all 404. The admin UI answers only on
`litellm.bopp-quail.ts.net`.

Outstanding: the DeepInfra key at `/etc/litellm/deepinfra.env`, confirmation
of guest autostart, and two Cloudflare-side decisions below.

**Cloudflare challenges non-browser user agents on api.bashtion.dev.** From
the guest's datacenter IP, curl gets a 403 "Just a moment..." interstitial
with or without a key; the same request with a browser User-Agent gets 200.
From a residential IP curl is not challenged. Students in JupyterLite send a
real browser UA and are fine, but every script-based path -- the week 5 and
week 6 eval harnesses, any instructor testing, a server-side Jupyter fallback
-- gets HTML instead of JSON. Needs a WAF skip rule for the hostname.

**Pyodide is now bundled.** It was not: the first build had zero .wasm files
in 790 and pulled its Python runtime from
`https://cdn.jsdelivr.net/pyodide/v314.0.5/full/pyodide.mjs`, so a college
network that blocked jsdelivr would have stopped every cell from running, and
it would have looked like a hang rather than a network failure.

Rebuilt with `jupyter lite build --pyodide pyodide-314.0.5.tar.bz2`. The site
is 445 MB across 1210 files and serves its own runtime:

    /static/pyodide/pyodide.mjs          200  17,931 bytes  text/javascript
    /static/pyodide/pyodide.asm.wasm     200   9.6 MB       application/wasm
    /static/pyodide/python_stdlib.zip    200   2.5 MB       application/zip

`application/wasm` matters: `WebAssembly.instantiateStreaming` refuses any
other content type, and Caddy gets it right without configuration.

Two `cdn.jsdelivr.net` strings survive in the bundled JavaScript. Both are
`||` / `??` fallbacks reached only when the configured value is missing --
`a.pyodideUrl || "https://cdn.jsdelivr.net/..."` -- and `jupyter-lite.json`
sets `pyodideUrl` to `./static/pyodide/pyodide.mjs`. Verified by reading the
served config, not by assuming.

**356 packages ship locally**, 379 wheels, including `micropip`, `requests`,
`urllib3`, `pydantic` and `openai`.

### What a real browser says, tested with Playwright

Driving headless Chromium against the live site, executing cells in the actual
Pyodide kernel:

| step | result |
|---|---|
| execute anything | `42` |
| `import requests` | **ModuleNotFoundError** |
| `await piplite.install("requests")` | requests 2.33.1 |
| `requests.get(".../v1/models")` | 401, JSON body read back |
| `requests.post(".../v1/chat/completions")` | 401, LiteLLM's own auth error JSON |

**The memo's work item shrinks but does not vanish.** It prices in rewriting
`send_request()` to `pyodide.http` across fourteen byte-identical cells. That
is not needed: `requests` works once installed, the CORS preflight passes, and
Python reads the response body. What is needed is one
`await piplite.install("requests")` before the import. A one-line addition, not
a rewrite of the most carefully guarded cell in the course.

No credential was used. An invalid bearer token still exercises the preflight,
the request and the response read; a 401 carrying LiteLLM's JSON means only the
key was wrong.

### The test found a bug I had introduced

The first run returned `ConnectionError('Failed to fetch')` on the GET. Cause:
the Caddy short circuit added for issue 3 answers unauthenticated requests
itself, and it was not setting `access-control-allow-origin`. LiteLLM sets that
header on its own responses, so bypassing LiteLLM dropped it. A browser then
blocks the 401 and the student sees `Failed to fetch` instead of "Missing
Authorization header" -- an opaque failure for the commonest student mistake,
a missing key.

Fixed, and asserted in `litellm-verify` (53 checks). Every curl based check
passed before and after; only a browser could see it.

### Self contained, confirmed by a browser that fetched nothing else

`comm-0.2.3` was the last external dependency: `ipykernel` ships locally but
depends on it, so piplite fetched it from PyPI at every kernel boot. It is now
bundled with `--piplite-wheels`, which copies the wheel into a site level
`/pypi/` index and prepends that index to `pipliteUrls`.

Final browser run, headless Chromium against the live site:

| step | result |
|---|---|
| `await piplite.install("requests")` | requests 2.33.1, resolved locally |
| `requests.get(".../v1/models")` | 401, clean JSON |
| `requests.post(".../v1/chat/completions")` | 401, LiteLLM's auth error JSON |
| **non-bashtion.dev URLs fetched** | **none** |

**The doit cache is the trap, and it fails silently.** `jupyter lite build`
caches task state in `.jupyterlite.doit.db`. On a rebuild it skipped
`post_build:...pyodide:patch:jupyter-lite.json` as up to date, which dropped
`pyodideUrl` from the output. The site still worked and quietly loaded the
whole Python runtime from cdn.jsdelivr.net. Nothing in the build output said
so; only the browser's request log did. `/usr/local/sbin/jupyterlite-rebuild`
clears the cache and then asserts `pyodideUrl` is local and `comm` is indexed,
refusing to swap a build that fails either.

**Do not set `loadPyodideOptions.packageBaseUrl`.** It was tried and broke the
kernel outright -- cells stopped executing with `eval_code_async` errors. It is
also unnecessary: pyodide derives its package base from `pyodideUrl`.

**Model pricing is configured, so spend is real.** DeepInfra publishes
granite-4.2-3b at $0.03/M input and $0.12/M output, and 4.2-8b at $0.06/M and
$0.25/M, with cached input at 25%. Both are set per deployment, and LiteLLM's
computed spend now matches DeepInfra's own `estimated_cost` to the digit
(3.45e-06 and 5.63e-06 on a two-call check). Asserted in `litellm-verify`,
because without the rates LiteLLM records tokens and stores spend 0.0 while
looking healthy.

That turns the blueprint's break-even into a measurement. It could only say the
model had to cost under $12.89 per million tokens; the real worst case is $0.25
per million. A full pass through all seven labs is about 388,000 tokens, so
**under ten cents per student**, and the $5 per-key budget buys about 52
complete passes. Two consequences are recorded as deferred decisions D1 and D2
in `docs/lab-open-issues.md`.

Per-notebook attribution works: a `metadata.tags` entry set in a notebook cell
survives browser, Cloudflare, Caddy and LiteLLM into the `request_tags` column
with its token count and, now, its cost. Proven from a real browser cell, not
from curl. `User-Agent` cannot carry this -- browsers forbid setting it, and
LiteLLM already fills that slot with the student's own browser string.

### LiteLLM hardening, and what each item was proven against

Applied and verified by running the attack, not by reading the config:

| Control | Evidence |
|---|---|
| `api_base` / `base_url` / `user_config` / `model_list` / `input_cost_per_token` in the request body | all rejected; `allow_client_side_credentials` is unset, which is the default that makes that hold |
| per-key `rpm_limit` | 35 rapid requests against `rpm_limit: 30` gave 28x200 and 7x429 |
| request size | 100K body 200, 1.5M a clean 400 from LiteLLM, 2.9M cut by Caddy's `request_body max_size 2MB` |
| `max_request_size_mb: 2`, `max_response_size_mb: 8` | in `general_settings` |
| proxy-wide `max_budget: 200` + `budget_duration: 30d` | backstop for a key minted without a budget |
| `turn_off_message_logging: true` | set; keeps prompts and completions out of spend logs. Not independently verified |
| team `itsy1377-students` | a key minted with ONLY `team_id` and no limits still inherits the model restriction and the budget -- "team not allowed to access model" |

**Mint student keys against the team, so a forgotten parameter cannot widen
access:**

    POST /key/generate  {"key_alias":"<student>","team_id":"b245df2b-c11e-47d7-9e59-d869291a3358",
                         "max_budget":5.0,"budget_duration":"30d","duration":"120d",
                         "rpm_limit":30,"tpm_limit":40000,"max_parallel_requests":2}

**A hardening change broke the proxy and the logs lied about why.** Setting
`litellm_settings.max_budget` without `budget_duration` makes LiteLLM refuse to
start. It crash-looped, and the log lines that survived blamed a missing prisma
package -- which was importable the whole time. The real line was
`Exception: budget_duration not set on Proxy`. `systemctl is-active` said
`active` throughout, because the restart loop keeps flipping it.

**Still open, and not mine to close:** a client-supplied `api_key` in the
request body IS forwarded to the provider -- DeepInfra rejected it, but LiteLLM
honoured it rather than refusing like the other banned params. A student could
bill their own DeepInfra account and bypass our spend accounting. It widens
nothing on this proxy, but it is worth knowing before someone reports it as a
bug.

**Only the two Granite models are reachable, and the list is no longer
mutable at runtime.** `granite-3b` and `granite-8b` resolve to
`deepinfra/ibm-granite/granite-4.2-3b` and `-8b`. Everything else is refused
from the public URL with a scoped student key: the 30b sibling, the same
models provider-prefixed, Llama, gpt-4o, `openai/gpt-4o`, `claude-opus-5`,
a literal `*`.

Two layers do this. A key carries a `models` list and rejects anything outside
it; independently, the router refuses any name absent from `model_list` even
for a key with no restriction at all.

A third gap was found and closed. With `STORE_MODEL_IN_DB=True`, `/model/new`
added a Llama-3.3-70B deployment at runtime that was immediately routable by an
unrestricted key and appeared on the public `/v1/models`. That was demonstrated,
not theorised. It is now `False`, the proxy model table is empty, `/model/new`
refuses, and `config.yaml` is the single source of truth -- the model list
cannot change without editing the file and restarting the service.

**`reasoning_effort` was being silently discarded, and it is a 33x cost.**
LiteLLM's provider table claims deepinfra does not support `reasoning_effort`.
It does. With `drop_params: true` the parameter was dropped without a word and
every request reasoned anyway; with `drop_params: false` the same request is a
hard 400. Measured on "reply with exactly the word: ready", granite-3b:

| path | reasoning chars | output tokens |
|---|---|---|
| straight at DeepInfra, `reasoning_effort: none` | 0 | 2 |
| straight at DeepInfra, nothing sent | 441 | 100 |
| through LiteLLM before the fix | 288 | 67 |
| through LiteLLM after the fix | 0 | 2 |

The fix is `allowed_openai_params: ["reasoning_effort"]` per model in
`config.yaml`, alongside `reasoning_effort: none`. Both models verified at
0 reasoning characters and 2 output tokens afterwards.

This is the fourth defect of the shape the infrastructure memo names: a
setting accepted and quietly ignored. It also defeated my own first check,
which read `message.reasoning` and reported "reasoning is off" while the text
was sitting in `message.reasoning_content`. Read the field the server actually
fills.

A student who sends `reasoning_effort: high` still wins -- 293 chars, 72
tokens. The proxy sets a default, not a guard, which is what the memo's
carve-out wanted: `lab/eval/week5_loop_test.py` can still measure reasoning
mode by passing the parameter explicitly.

CORS was checked and is fine: LiteLLM returns `access-control-allow-origin: *`
on both the preflight and the real response, so browser calls from
notebook.bashtion.dev to api.bashtion.dev work.

### Three things worth remembering

**The lease table is not identity.** Both guests came up on 10.171.0.128 at
once: jupyterlite held it, rebooted, litellm took the lease, and jupyterlite
kept using the address anyway. The status wrapper showed one tidy binding and
was wrong. `scratchpad/lab.sh` resolves a guest by name and refuses to run
unless the box that answers reports the hostname asked for; its first real
call caught the collision. Fixed by operator DHCP reservations.

**A Caddy site address is also a Host matcher.** `127.0.0.1:8080 { }` did not
constrain the listener -- `ss` showed `*:8080` -- and it 400d every request
whose Host was not `127.0.0.1`, which through a tunnel is all of them. The
correct shape is `:8080` plus an explicit `bind 127.0.0.1`. Both mistakes are
invisible in config review and obvious in `ss` and a curl with a spoofed Host.

**`systemctl is-active` said `active` while the unit was crash-looping.**
Restart=on-failure means the state flickers. The port check is what caught it.

## 2026-09-06 — lab infrastructure, stopped on a duplicate address (resolved)


Both guests are built on remotelab and running: `litellm`
(mac 52:54:00:d1:30:65) and `jupyterlite` (mac 52:54:00:fc:7a:80), each
2 vcpu / 4096 MB / 40 GB.

Nothing is configured on either. No LiteLLM, no Caddy, no cloudflared, no
secrets placed, no inbound port opened, and no change to any other guest or
to the host.

**Blocked:** both guests are using 10.171.0.128 at the same time. Proven by
probing that address repeatedly and reading the answering box's own MAC:
it comes back as jupyterlite (52:54:00:fc:7a:80) and litellm
(52:54:00:d1:30:65) on alternating connections, each reporting
10.171.0.128/24 on its own interface. The libvirt lease table shows only
litellm's binding, so the wrapper's `lab ip` line is not a safe identity.

Configuring by address here would be a coin flip about which guest receives
the work, and the losing case puts the DeepInfra key and LiteLLM's admin
plane on the guest whose tunnel has no allowlist in front of it. That is the
one outcome the build brief calls the worst available.

The operator has to add DHCP reservations for both MACs on the `lab` network;
`virsh net-update` is not in the three-command sudo grant. Resume after that.

`scratchpad/lab.sh` is the guard that caught it: it re-resolves the address
from the guest name on every call and refuses to run unless the box that
answers reports the hostname that was asked for.

---

## 2026-09-07 — narration warmth test: rewrite adopted, engine rejected

**Judged.** The warm rewrite won. VoxCPM lost on listening, and every
measurement had called the two engines equivalent — a reminder that
faithfulness, pace and level do not add up to "sounds good".

VoxCPM is fully removed. `tools/video/{tts,schema,build,config}.py` are
byte-identical to their committed versions (`git diff` clean). The worker,
`design_voice.py`, the voice profile, `.venv-voxcpm`, the second scene list
and its built video are deleted.

The test module now carries the warm rewrites of all three week 1 pages **and
both week 1 videos** rendered with the existing Kokoro voice: the overview and
the walkthrough, whose narration was rewritten in the same pass. Objectives and
CLO tags in the rewritten pages are byte-identical to the originals, and the
module holds pages only, so no graded artifact was touched.

Still to decide: whether to promote the rewrites over the real week 1 pages,
and whether to extend the same pass to weeks 2 through 8 (7 more readings,
7 overviews, 7 wrap-ups, 14 more video scripts).

## 2026-09-07 — narration warmth test, deployed for judgement

A thirteenth module, `Test: Module 1 rewritten (review only)` (Canvas course 6,
module id 51, published), holds warm rewrites of the three week 1 pages and the
same overview script narrated by two engines. **No existing page, module,
assignment, quiz or video was edited.** Verified after the push: 13 modules,
Module 1 still has its original 8 items, both test videos resolve HTTP 200 with
no `$IMS-CC-FILEBASE$` placeholders left, `--verify` reports 0 problems.

New files: `content/pages/test-w1-{overview,content,wrap-up}.md`,
`content/video/test-w1-overview{,-voxcpm}.yaml`,
`docs/narration-voice-test-2026-09-07.md`.

Pipeline changes are additive and the default is unchanged (`kokoro:af_heart`).
`tools/video/` gains `VoxCPMVoice`, `voxcpm_worker.py`, `design_voice.py`, a
per-engine voice audit in `schema.py`, and `resolve_voice_spec()` in
`build.py`. VoxCPM lives in its own venv (`.venv-voxcpm`) because it needs
torch 2.14 and Kokoro is pinned to 2.13. Kokoro was re-run after the edits and
renders identically.

**The finding that matters if this is adopted:** VoxCPM designs a new speaker on
every call. Description-only mode measured 0.66 mean timbre similarity across
six cues and 0.25 at worst, which is a different narrator between slides, and it
paraphrased. Cloning from the committed `tools/video/voices/course-warm.wav`
holds 0.97/0.92 and transcribes at 98.9% against the scene list, identical to
Kokoro. The reference clip is not optional.

**Nobody has listened to any of it yet.** Take 3 was promoted on measurements
alone. `design_voice.py course-warm --description "..." --choose N` re-picks.

Open, unchanged from before: `w7-walkthrough` stale against its content; the
CLO3/5/6 exam gap; a second rubric row for CLO5/CLO6; `week6_injection_test.py`
built and never run; `builder/` still not in git; `check_commands_resolve` is
vacuous for this course; the Canvas token in the transcript still awaits
rotation.

---

## 2026-09-07, later — the warm pass, and week 6 measured properly

**The course is warmer and the numbers in it are honest.** All on branch
`course-warmth-rewrite`, twelve commits, nothing pushed to a remote.

**Writing.** 328 lines of prose and 98 spoken cues gain contractions, applied
by `builder/tools/warm_pass.py` and `warm_narration.py` rather than by hand.
Both refuse to touch anything that is not prose: fenced and inline code,
tables, headings, block directives, bare link lines, `::: sources` citations,
and in a scene list everything except the spoken cue. Connective tissue was
done by hand on the six weekly reading intros, because joining two sentences
with a "so" is a judgement about the argument.

Week 1's warm rewrite replaced the originals and the test module is gone. That
closed the false claim that notebook work "stays on the notebook server for the
whole term".

**No hard numbers are quoted as fact any more.** Four places did, and one of
them predicted the student's own score: "it scored 16 of 20 against your 19".
A student scoring 17 would have thought they broke something. Week 1 teaches
that one answer is a sample and not a fact, and the course was contradicting
itself.

**Week 6 is measured.** 2,156 runs under `docs/week6-measurement/`, conclusion
in `docs/model-selection.md`. Email 013 lands 12 times in 15 undefended on
granite-8b and 0 times in 15 guarded, which is objective 6.2 and 6.3 in one
comparison. The reading now says the payload moves the model in most runs and
not all, and part 2 gains a section on why a guardrail has a rate rather than a
score, what moves that rate, and why an agent has to be built to fail in a
direction you chose.

**Four bugs were fixed in the measuring before any of it was believable**, and
three conclusions reversed along the way. `one_run()` read payload keys that do
not exist; there was no rate limit backoff, so a run lost 130 of 160 requests
and still wrote a tidy summary of zeros; the known-good list omitted the
organisation's own domain; and both eval scripts pointed at an ollama that no
longer exists. The eval harness was also pinned at temperature 0 while the
notebooks use 0.2, which is why its answers kept disagreeing with the lab.

**Models: granite-3b everywhere, granite-8b for week 6 and the week 7
comparison.** Qwen3-14B, Llama-3.1-8B and Gemma-3-12B were served briefly,
measured, and removed. Gemma looked best at n=1 and worst at n=510: zero guard
effect and 75 of 120 benign emails called malicious. The proxy is back to two
models and `litellm-verify` passes 62 of 62.

**Also closed:** the exam gap (CLO3, CLO5, CLO6 now have items; 40 items at
0.75 points, still 30 points); `verify_content` was checking another course's
docs; `check_commands_resolve` was vacuous two ways; `qti.py` accepted
`outcome: "none"` as a tag; week 7's score report could not tell a swapped
error branch from a correct one; and `builder/` is now in git.

**Still open.** The week 5 measurement (294 runs, the most rigorous in the
repo) predates the move off ollama, so its figures are not current. The Canvas
token still awaits rotation. The `GUARD_RULES` rewrite was tried and retracted:
it fixed neither failure and made granite-3b slightly worse.

---

## 2026-09-08 — a blind student ran the whole course

**A simulated novice took the published course end to end** — Canvas pages, the
fourteen video transcripts and notebook.bashtion.dev, no repository, no
solutions, no looking ahead, one module per sitting. It finished everything,
scored **39 of 40** on the final exam, spent **$0.0106 of $2.00** and took about
31 hours. Report: `docs/student-e2e-run-2026-09-08.md`. Raw notes:
`scratchpad/student2/FINDINGS.md` (7,008 lines) and its own `REPORT.md` (976).
**No course file was changed because of the run.**

**The finding that matters most: week 6 cannot demonstrate what week 6 teaches.**
The undefended verdict comes from `run_triage(parsed_013, loop_prompt(parsed_013))`,
and `loop_prompt()` is instructions + facts + known-good hosts. There is no
`body_text` in it. The planted paragraph never reaches the call it is supposed to
move. The guarded prompt *adds* the body, so cell 11's "the fence is the only
thing that changed" is false five ways. **Corrected by the panel:** the
undefended agent does see the body during the loop -- `start_messages()` pastes
it into the user turn. Only the closing one-shot call that writes the verdict is
bodyless, and that is where the asymmetry lands. The student's control: the guard flipped the verdict
5 of 5 on 013 **and 5 of 5 on its clean twin 024**. The injection moved nothing in
10 paired comparisons.

**This resolves the open question from the 2026-09-07 measurement.** Those 2,156
trials were sound; the lab was never running the comparison it describes. It is
not "grounding defeats the payload", it is a missing variable in a prompt.

**Also confirmed:** four graded criteria ask for values the export files do not
carry (weeks 3, 5, 6, 7 — 117 points, one line each to fix); `schema_errors()`
has no `sentences` branch so week 7's schema is never validated and would reject
a correct answer; **every correct answer in all 43 weekly self-check questions is
the first option and `shuffle_answers` is false** on all seven; week 1's TODO 1
points at the wrong dictionary and nothing catches it; week 3 names its two
teaching emails three ways across seven documents while the code runs a pair none
of them endorses; the orientation's `budget_left()` / `restore_my_work()` /
"run the last cell" instructions do not work in week 0.

**Mechanisms taught and never demonstrated:** week 2's retry branch is never
entered, week 5's `step_cap` cannot fire at all (proved from the loop condition),
week 6's four controls fired 0 of 11. Weeks 5 and 6 each also contain a cell that
demonstrates a mechanism properly — those are the pattern to copy.

**Four of the student's reported defects were the harness, not the course** —
quiz feedback, cell numbering, links, duplicated headings. All corrected mid-run
and listed in the report. Check the pipeline before believing the reviewer.

**Two housekeeping items.** The live notebook site was one revision behind the
repo when the run started (`w7-lab.ipynb`, missing the fix from 6f7c0d4);
fourteen of fifteen hashes matched and nothing reported the one that did not.
There is no gate comparing the served site to the repo. And the student key
`student-e2e-20260907c` is still live: $2.00, 30 days, team `itsy1377-students`.
Two earlier keys were minted and revoked after I leaked them into the transcript
from my own debug probes; both confirmed dead (401). `jlstudent.py` now redacts
the key from everything it prints.

---

## 2026-09-08, later — week 1 fixed, and the temperature lesson measured

**Week 1 is the first of the panel's findings to be closed.** Design was argued
out with codex, then settled by measurement rather than by argument: about 1,700
live calls across five models and four prompt shapes, recorded under
`docs/week1-measurement/`.

**The old demonstration had never worked.** Cell 11 sent free prose six times,
three at 0.2 and three at 1.0, and asked the student to eyeball the difference.
Prose saturates: twenty distinct answers out of twenty at every temperature the
course would use. Bootstrapped at the lab's own n=3, the two group means are
**2.87 and 2.86**, and it lands in the claimed direction **11% of the time**.
Raising n does not rescue it.

**Two candidate fixes were killed by looking at the values, not the statistic.**
A number probe measured a perfect 100% separation and answered `0.00` -- no
chance of phishing -- twenty times out of twenty on email 001, which is
`malicious / credential_phish`. Four rewordings failed the same way. And
granite-3b with a word-and-sentence probe reaches 99% but calls that phish
*legitimate* 8 times in 20 at t=1.0, which would teach that a high temperature
makes the model wrong. Codex's own label probe was screened and rejected too: on
granite-3b it separates in 11% of batches at n=10.

**What shipped, at the user's decision.** Week 1 now runs on **granite-8b**, with
a one-word-plus-one-sentence probe, six calls at 0.2 and six at 1.0. Measured at
**98%** of student-sized batches showing the effect and **zero wrong verdicts at
either temperature**. The first live solution run produced **2 distinct answers
at 0.2 and 6 at 1.0**, all twelve correct, in 21 seconds.

The prose calls stay in TODO 2 and the email 002 cell, so week 1's hand-off to
week 2 -- "a sentence is hard for code to use" -- is still true.

**Also closed in week 1:** the `MODEL_EXTRAS` antecedent, now backed by a check
that swaps `send_request` for a capture function behind `try/finally` and asserts
with sentinel values that `reasoning_effort`, `temperature`, `max_tokens` and
`model` reached the outgoing payload -- and that `reasoning_effort` is *not*
inside the message. The missing-`return` trap now prints a message naming TODO 1
and week 0 cell 53 instead of raising `AttributeError` inside a pre-written cell.
`w1-content.md` teaches temperature for the first time, funded by cutting
repetition, and the notebook's own prose now counts cells from 1 like every
assignment page.

**Gates:** `check_chain` holds, readability 59 pages within limit (w1-content
5.43, 1383/1400 words), `verify_content` reports "the content and the code
agree", student and solution notebook runs both pass.

**Two things left open.**

1. **Resolved the same day. Both week 1 videos are rebuilt** and
   `tools/video/check.py` reports 14 videos, all checks pass. My report that the
   build environment was gone was wrong: the venv is at `tools/video/.venv` and I
   had searched only the repository root. Build with
   `tools/video/.venv/bin/python -m tools.video.build`, never the system python,
   which fails with a misleading `No module named 'soundfile'`.
2. **`run_notebook.py` cannot test a notebook's own model.** Line 215 does
   `os.environ.setdefault("ITSY1377_MODEL", "granite4.2:3b")`, which overrides the
   notebook's default, so the harness proves the notebook runs against whatever
   the harness picked. Week 1's run had to be forced to granite-8b by hand. Same
   defect class as the checks the panel found examining zero items.

**Closed, not deferred:** the confidence-instability thread. The rejected number
probe surfaced that `confidence` is a week 2 schema field, the value week 6's
`CONFIDENCE_FLOOR = 0.7` routes on, and a line in week 7's note. It was going to
be carried as week 1 work until the source was checked. **The course already
teaches the concept:** `w2-content.md` line 37 tells students to read the number
"as the model's own report, not as a fact about the email. A high number on a
wrong answer is still wrong", and `w6-content-2.md` line 76 says the floor "says
nothing about how good the model is. It's a line saying which cases a person
owns". Week 2's assignment already asks for the lowest confidence number seen
across four emails.

What is genuinely absent is any week showing *the same email* return a different
number on a repeated run -- a narrower claim -- and that belongs beside the
control in week 6, carried as a note in `docs/lab-fix-log.md`. It does not
answer the SOC finding either: that objection is to the control's design, not to
an over-claim about calibration. Four exam items reference confidence and all
four are answerable from weeks 2 and 6 as written, so there is no assessment
consequence. **Week 1 is complete.**
