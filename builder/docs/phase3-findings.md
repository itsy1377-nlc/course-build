# Phase 3 findings

Defects found while building weeks 3 to 8, and what each one changes. Kept as
it happens so the final QA report and the risk register are written from a
record rather than from memory.

Each entry says what was wrong, how it was found, and what now stops it coming
back. A defect with no standing check is not closed.

## 1. Every quiz in the course carried a stray question

**What was wrong.** All four quizzes built in Phase 2 held one extra item at
the end: a text-only question named "Question", reading "Question text". A
student would have seen it at the bottom of the syllabus acknowledgment, the
week 0 self-assessment and both self-checks.

**Cause.** `build_course.py` ended `make_quiz()` with a POST to the questions
endpoint carrying no body, commented as a no-op flush, meant to make Canvas
recompute `points_possible`. It is not a no-op. Canvas creates a real question
from an empty body and fills it with its own defaults.

**How it was found.** Extending the verifier for the final exam, which needs
text-only questions as its six reference blocks. The new check compares the
scored questions and the text blocks in Canvas against the source file, and it
failed on all four quizzes at once.

**Why nothing caught it before.** The Phase 2 verifier checked that every quiz
answer carries feedback. A text-only question has no answers, so it passed
through a check written around answers.

**Fixed.** The empty POST is replaced by `PUT /quizzes/:id` with
`quiz[notify_of_update]=false`, which makes Canvas recompute and creates
nothing. Measured on the live instance: after deleting the stray and
re-saving, `points_possible` stays 12.0 and `question_count` stays 6. The four
strays are deleted. `--verify` now reports 0 problems.

**What stops it coming back.** The verifier counts the scored questions and the
text blocks in Canvas and compares both against the source yaml, and it checks
that the source's points sum to the spine's figure.

## 2. The exam blueprint named a field Canvas silently ignores

**What was wrong.** Section 9 of `exam-blueprint.md` said the per-answer
feedback field in the Classic Quizzes API is `answer_comments`. It is not.
Canvas accepts an answer object carrying `answer_comments`, answers HTTP 200
and stores nothing.

**Why it matters more here than anywhere.** The exam is thirty items with four
options each: 120 pieces of feedback, and the last teaching any of them will
ever do. All 120 would have been dropped while the build reported success.

**How it was found.** Reading the blueprint against the builder before writing
the exam. `build_course.py` already used the working key, `comments`, because
Phase 2 hit the same bug on the self-checks. Confirmed by reading question 579
of quiz 16 back from the live instance: the answer object carries `id`, `text`,
`html`, `comments`, `comments_html` and `weight`, and no `answer_comments`.

**Fixed.** Sections 9 and 11 of the exam blueprint now name `comments`, say how
it was measured, and say what the wrong key does.

## 3. Module 8 was missing its wrap-up page

**What was wrong.** `course.yaml` gave Module 8 two items, an overview page and
the exam. Template conflict 27 settles it at three: Overview, the exam, and
Wrap-up. `content/AUTHORING.md` had been written to describe the two.

**How it was found.** Reading the exam blueprint's section 11, which states the
three-item set, against the spine.

**Why it matters.** This is the same defect Module 0 had in Phase 2, found and
fixed there under the same conflict. A student who finishes the exam otherwise
meets no closing step in Canvas.

**Fixed.** `w8-wrap-up` is in the spine with a comment naming the conflict, and
AUTHORING.md section 2 is corrected. The wrap-up teaches nothing new and
reviews no exam item, because week 8 adds no instruction.

## 4. Week 6's reading is two pages, and the spine had one

**What was wrong.** `course.yaml` listed one week 6 content page. The approved
week 6 spec and the survey content plan both set two pages of about 1,150 words
each: prompt injection in a triage agent, and the wider AI risk set, which
carries breadth topic B4.

**How it was found.** Reading each week's reading plan against the spine before
launching the content build.

**Fixed.** `w6-content-2` is in the spine. The readability tool keys its budget
by page stem, and the `-2` stem already works because week 2 uses it.

## 5. Three weekly rubrics would have produced no rubric at all

**What was wrong.** The approved rubric sketches for weeks 3, 4 and 5 each link
two or three criteria to the same Canvas Outcome. Week 3 links criteria 2, 3
and 4 to CLO1. Weeks 4 and 5 link two and three criteria to CLO3.

**Why it matters.** Canvas allows a given Outcome to align to at most one
criterion in a rubric. A rubric that aligns the same Outcome twice is refused
silently: HTTP 200, and no rubric is created. This already cost week 1 its
rubric in Phase 2, and the build reported success.

**How it was found.** Reading the rubric sketches against the constraint before
writing any rubric, rather than after.

**Resolved.** Each week's rubric links its Outcome once, on the criterion that
measures it most directly, which is the primary-evidence criterion the
alignment matrix already names. The others are written as week expectations and
say so. That is the same resolution week 1 took.

**What the program manager needs to know.** Week 3's objectives 3.2 and 3.3 no
longer have an Outcome-linked criterion of their own, and neither does week 4's
objective on reading your own results or week 5's on cost. CLO1 and CLO3 still
receive outcome data from their primary criteria. The alignment matrix's
argument that every objective should reach the outcome report cannot survive
the Canvas constraint, and this is the trade that was taken.

## 6. Weeks 1 and 2 use different unwritten-TODO placeholders

**What was wrong.** Nothing, yet. Week 1 leaves `# your code here` and returns
a sentence saying the function is not written. Week 2 leaves a different
comment and `pass`. Both keep the notebook runnable, which is the rule that
matters, but nothing had written the rule down.

**How it was found.** Building `lab/tools/run_notebook.py`, whose first
placeholder detector was written from week 2 and reported week 1's student
notebook as a solution.

**Fixed.** `lab/notebooks/AUTHORING.md` records the rule and both conventions,
so weeks 3 to 7 do not invent a third. The rule is that a student who opens the
lab and runs every cell before writing a line must see a working notebook, not
a traceback.

## 7. The course carried six emails and no data files

**What was wrong.** The build brief requires the course to contain "the
synthetic email corpus and supporting data files." Canvas held the six Phase 0
sample emails and nothing else. No `sender_reputation.json`, no
`recipients.json`, no allowlist or blocklist, no playbook, no `enums.json`, no
`parse_eml.py`, no `triage_tools.py`.

**How it was found.** Walking the brief's "what done looks like" list against
the live course, item by item, rather than against the build report.

**Why nothing caught it.** `build_course.py` uploaded notebooks and video
assets, which are the two things a module item points at. The corpus is not a
module item, so no page was ever missing and nothing failed.

**Fixed, and deliberately not by walking a folder.** `course.yaml` now carries
`student_files`, an allowlist naming exactly what ships, and `never_ship`,
naming files whose presence is a build failure. The builder uploads only what
is named and refuses to upload anything on the second list.

**The reason it is an allowlist.** `corpus/spec/corpus-spec.json` holds the
verdict, the category, the indicators, the tool returns and the expected loop
for all 56 emails. `corpus/ground_truth.json` holds the graded labels. Either
one in the course files hands every student a complete answer key, and nothing
a student ever runs would notice: every page still renders, every quiz still
scores, and the key is one click away in Files. A folder walk over
`corpus/` would have uploaded both.

**What ships.** The 45 student emails, the five data files `triage_tools.py`
opens, the display name table the week 3 check reads, the playbook the week 3
prompt carries, `enums.json` and `categories.json`, `parse_eml.py`,
`triage_tools.py`, the corpus README, and `ground_truth_batch.json`, which
week 7 scores against and which ships because nothing in this course locks.

**What stops it coming back.** `--verify` reads the file list back from Canvas
and fails on any `never_ship` name and on any allowlisted file that is absent.
It currently reports the 21 missing files, which is the defect, and it will go
quiet when the build runs.

**One thing checked while here.** `lab/tools/triage_tools.py` opens only the
five data files it names. It does not read the manifest, so the three tools do
not leak the answer key to a student who reads the source of the module they
import.

## 8. The hosting document described a gate that no longer exists, and told the college to depend on it

**What was wrong.** `instructor/environment-setup.md` section 3.3 told the
hosting team that the notebooks decide whether to send `reasoning_effort` by
reading the model's name, and that "the model name in `ITSY1377_MODEL` is
load-bearing. Name the model so the gate fires, or the course silently gets the
expensive configuration."

The notebooks do not do that. The configuration cell sends
`reasoning_effort: "none"` on every request, for every model.

**How it was found.** Reading the instructor package against the shipped
notebook while waiting on a workflow.

**Why it matters.** This is a document the college configures its environment
from. It named a wrong dependency and asked them to design around it.

**The measurement, redone rather than recalled.** One request per cell against
the serving stack on 4 September 2026:

| Model | `reasoning_effort` | Result |
|---|---|---|
| granite4.1:3b | `none` | HTTP 200, answer returned, no reasoning text |
| granite4.1:3b | `low` | HTTP 400, `"granite4.1:3b" does not support thinking` |
| granite4.2:3b | `none` | HTTP 200, answer returned, no reasoning text |
| granite4.2:3b | `low` | HTTP 200, answer returned, 46 characters of reasoning |

`none` is safe on both. Only the graded levels are refused, and only by 4.1.

**Why the gate was worse than no gate.** It matched the literal text
`granite4.2` in the model name. A hosted alias such as `course-model` or
`ibm/granite-4-2-3b` does not match, so the field would never be sent and
reasoning would stay on for the whole term. Nothing would fail: every notebook
still runs and every answer still arrives. The course would just cost about
twice the tokens and twenty times the wall clock, and a student waiting ninety
seconds per email would assume the notebook had hung.

**Fixed** in `environment-setup.md` and `STATE.md`, with the measurement table
in the document rather than a citation to it. Three more copies of the stale
sentence are queued for correction once the content workflow stops reading
them: `docs/week5-model-test.md`, `docs/phase1-blueprint/week-05-spec.md`, and
the rendered `phase1-blueprint.html` the program manager was given.

**The general lesson, which belongs in the risk register.** A configuration
that depends on how someone spells a model name breaks when someone renames it,
and breaks silently. The course now reads no meaning out of `ITSY1377_MODEL`.

## 9. The course's main quality gate could not be run the way every instruction said to run it

**What was wrong.** `tools/readability.py --file <path>` raised a traceback on
a relative path:

    ValueError: 'builder/content/pages/w2-overview.md' is not in the subpath of
    '/Users/aaron/workspace/dev/ITSY1377'

Only an absolute path worked. `check_file()` handed the path straight to
`Path.relative_to(ROOT)`, which raises unless the path is already absolute and
inside the repository.

**Why it matters.** That is the reading level and length gate for every page in
the course, and `content/AUTHORING.md` section 7, `lab/notebooks/AUTHORING.md`
and every authoring instruction in this build tell an author to run it exactly
that way, with a relative path. A tool that dies on the documented invocation
is a gate nobody runs.

**How it was found.** Checking that the Phase 3 authoring agents could actually
measure what I had told them to measure, rather than assuming the instruction
worked.

**Fixed.** `check_file()` now resolves the path first and falls back to the
path as given for a file outside the repository. The relative form, the
absolute form and the whole-course run all work.

**What it exposed straight away.** With the gate runnable, the instructor
package and the Phase 1 blueprint measure for the first time. Grades are fine
everywhere: the blueprint's highest is 7.94 and the instructor package's is
6.18, both inside the program manager bar of 9.5. Paragraph length is not fine.

| File | Paragraphs over 70 words | Longest sentence |
|---|---|---|
| `docs/nlc-template-conformance.md` | 8 | 189 words |
| `docs/email-header-realism.md` | 8 | 56 words |
| `docs/serving-stack-shape.md` | 5 | 54 words |
| `docs/phase1-blueprint/week-02-spec.md` | 4 | 34 words |
| `docs/phase1-blueprint/template-conflicts.md` | 3 | 42 words |
| `instructor/discussion-facilitation.md` | 3 | 76 words |
| `docs/nice-verification.md` | 0 | 121 words |
| `instructor/environment-setup.md`, `grading-notes.md`, `announcements.md` | 1 each | up to 50 words |
| `docs/phase1-blueprint/alignment-matrix.md` | 1 (75 words) | 41 words |

`STATE.md` and the Phase 1 package both claim every blueprint file sits inside
the program manager bar, which is stated as grade at or below 9.5, average
sentence at or below 18, no sentence over 45 and no paragraph over 70. The
grade half of that claim holds. The paragraph and sentence half does not, in at
least nine files. The claim was made against a gate that could not be run.

Two files are exempt and stay as they are: `docs/build-prompt-v1.3.md` and
`docs/program-manager-suggested-outcomes.md` are the user's own words, kept
verbatim on purpose.

**Queued** for the final pass, so that nothing edits a file a running audit is
reading. The final QA report measures every document and reports what is still
outside the bar rather than repeating the claim.

## 10. The no-spoiler video gate had never seen a single solution notebook

**What was wrong.** `builder/content/video/config.yaml` declared three
`answer_globs`. The gate resolves them against `code_dir`, which is
`builder/lab`, and against the repository root:

    solutions/**/*.ipynb
    solutions/**/*.py
    eval/week5_loop_test.py

The solution notebooks are in `builder/instructor/solutions/`, which is neither
base. The first two patterns matched nothing. The third matched, so the gate
ran, reported clean, and had compared the captured screen against the reference
loop implementation alone.

**Why it matters.** That gate is the one enforcing the build brief's rule for
every walkthrough video: show the outcome, never the steps or the code. Phase 2
reported "no solution source on screen" as passing for four videos. It was
passing because there was almost nothing to find, not because nothing leaked.
Phase 3 adds five more solution notebooks and ten more walkthroughs, all built
on that rule.

**How it was found.** Resolving the globs by hand before launching the video
stage, rather than trusting a gate that had reported green. One file came back
where two sources were expected.

**Why nothing caught it.** `Config.answer_files()` drops a pattern that matches
nothing under either base and tells nobody. A pattern pointing at the wrong
folder and a pattern with genuinely nothing to find look identical in the
output. The function's own docstring records a previous fix for the case where
*every* pattern missed and the gate said "those patterns match no files", so
the total miss was handled and the partial miss was not.

**Fixed, in two places.**

1. The config points at `builder/instructor/solutions/**/*`, one general
   pattern rather than one per file type, so a solution added later in any form
   is covered without editing the file.
2. `Config.unmatched_answer_globs()` reports every pattern that found nothing,
   and a new gate, "answer files the no-spoiler gate reads all exist", fails on
   any of them and on an empty answer set. A gate that cannot fire now says so
   instead of passing.

**Checked against the other two courses in this repository** before changing
shared tooling: both resolve every pattern, so the new gate does not regress
them. This course was the only one broken.

**One consequence.** The video fingerprint hashes `config.yaml`, because the
config sets the slide footer and the voice engine. Editing it marks all four
existing videos stale, correctly. They are rebuilt with the ten new ones, which
means weeks 1 and 2 get re-checked against a spoiler gate that can now actually
see the solutions.

## 11. Two build gates that cannot run against this course, and one now ported

**`tools/cartridge.py` cannot run against `builder/content`.** It raises
`KeyError: 'id'` on the first check, because it expects the assignment group
shape the other two courses in this repository use, where a group carries an
`id`. This spine names groups with a `key` and lets Canvas own the id.

**That is not a defect in this course.** The cartridge is an alternative
delivery path. This course is built through the Canvas API, which the build
brief requires, so the cartridge is not on its path and its schema was never
meant to fit. An audit reported it as a broken gate, which is the right thing
to report and the wrong conclusion to draw.

**One check inside it did matter, and is now ported.** `cartridge.check()`
asserts that the assignment group weights add to 100. `build_course.py
--verify` did not. Canvas scales weights that do not add to 100, silently, and
a gradebook that quietly renormalises is a grade dispute nobody can answer
afterwards.

Three checks are added to `--verify`:

1. The weights in the spine add to 100.
2. Every group exists in Canvas with the weight the spine gives it, so a weight
   changed in the Canvas UI is caught.
3. Group weighting is actually switched on for the course. The spine says
   `apply_group_weights: true`, and if Canvas has it off, every weight is being
   ignored while the gradebook still looks plausible.

**What was NOT ported, and why.** `cartridge.check()` also compares each
group's share of total points against its weight. That test assumes points
alone decide the grade, which is true of the other two courses: both are
unweighted and total 100 points, so an item's face value reads directly as a
percentage. This course weights its groups and totals 954 points, so the same
test would fail all five groups while every one of them is exactly right.
Porting it unchanged would have added a gate that is wrong by construction.

## 12. Four names for one tool parameter

**What was wrong.** The first of the three course tools was called four
different things across the artifacts that have to agree about it:

| Where | Name |
|---|---|
| `docs/phase1-blueprint/code-ledger.md` section 6, the contract | `check_sender_reputation(sender)` |
| The week 4 reading, written from the ledger | `check_sender_reputation(sender)` |
| `lab/tools/triage_tools.py`, the shipped tool | `check_sender_reputation(domain_or_address)` |
| The model-facing tool schema | the property `domain` |

A student who read the page and called the tool by keyword, which is the form
week 0 teaches, got a `TypeError` from a tool they never wrote and cannot see a
reason for.

**How it was found.** A content audit reported that the week 4 reading prints a
signature the shipped tool does not have. It was right, and checking the other
sources turned one disagreement into four names.

**Fixed** by renaming the parameter to `sender` in `triage_tools.py`, because
the ledger is the contract and six notebooks are written against it. The
docstring now records why the name is what it is, so the next person to think
`domain_or_address` reads better knows what it costs.

Verified after: `check_tools.py` still reports all three tools agreeing with
the manifest on every field of all 56 records, and
`check_sender_reputation(sender="support@fenwright-pay.example")` now works.

**The fourth name is left alone deliberately.** The tool schema's property is
what the MODEL puts in its arguments, and `run_tool()` reads it out of there.
It is a different interface from the Python signature and it does not have to
match it. It does have to match what the week 4 notebook declares, which is
something the notebook stage has to get right; the ledger names both.

**Why the timing mattered.** This was fixed before the notebook stage ran. Five
notebooks and five instructor solutions are about to be written against these
names, and a rename afterwards would have meant editing ten notebooks whose
carry-forward cells copy each other.

## 13. Every Canvas Outcome was rolling up the wrong way, and it overstated mastery

**What was wrong.** All six Outcomes were built with
`calculation_method: highest`. The approved plan is most recent score, which
the Canvas API calls `latest`.

This is not a detail. The calculation method is the entire meaning of the
number the program reports for each course learning objective.

**The approved plan rejected "highest" by name, and gave the reason.**
`docs/phase1-blueprint/alignment-matrix.md` section 9:

> Two other methods were considered and rejected. Highest score would let a
> strong week 4 mask a weak week 5, which would overstate CLO3 mastery.

The course was built doing exactly that. CLO3 is the case the document uses to
make the point: week 4's tool criterion is supporting evidence, week 5's loop
criterion is primary, and week 5 comes last. Under "highest", a student who did
well in week 4 and badly in week 5 reports the week 4 number as their CLO3
result.

The error runs one way. It overstates, and it overstates in the direction
nobody audits.

**A second, quieter consequence.** Rubric levels floor at 0 in every week but
week 1, whose linked criterion floors at 6, mapping to Beginning rather than No
evidence. Under "highest" that floor would beat week 2's 0 forever, so a
student with no evidence in either week would report Beginning for CLO2. Under
"latest" the week 2 result simply replaces it, which is what the alignment
matrix says should happen.

**How it was found.** A content audit reported that the mastery scale the week
3 rubric reports into is not the approved one. That was about the rating list,
and checking it against the blueprint turned up the calculation method sitting
beside it.

**Why nothing caught it.** The builder wrote `calculation_method` from the
spine and never read it back. `--verify` checked that outcomes existed and that
rubric criteria linked to them. It never checked what an Outcome does with the
results once it has them, and no page or report would look different if it were
wrong.

**Fixed in both places.** `course.yaml` now says `latest`, with the rejection
quoted in a comment so the next person to think "highest sounds fine" reads why
it is not. All six live Outcomes were updated: six HTTP 200s, each returning
`latest`.

**What stops it coming back.** `--verify` now reads every Outcome back in full
and compares the calculation method, the mastery points and the whole rating
scale against the spine. That check needed `outcome_style=full` on the API
call; without it Canvas returns an abbreviated outcome with those three fields
absent, and the check reads None and fails for the wrong reason. It is on the
verify fetch only, because the build fetch uses the same endpoint just to map
titles to ids.

**Still open, for the program manager.** Week 1's linked criterion floors at 6
where every other week floors at 0, so the two map onto different ends of the
five-point scale. With `latest` the practical effect is gone, because week 2
supersedes week 1 for CLO2. The inconsistency in what a grader records is real
and is a grading-policy call, not a mechanical fix, so it is reported rather
than changed.

## 14. The repair stage judged its auditors instead of obeying them

Worth recording because it is the behaviour the whole arrangement depends on,
and because it was not guaranteed.

Three independent audits ran against each built week. A repair agent then read
their findings. It **rejected three, escalated five and applied four**.

**What it rejected, and why each rejection was right.**

1. An audit reported that the week 4 reading prints
   `check_sender_reputation(sender)` while the shipped tool has a different
   signature. The repair agent opened `lab/tools/triage_tools.py`, found `def
   check_sender_reputation(sender)`, and rejected the finding. It was correct:
   the audit was right when it ran, and I had renamed the parameter in the
   meantime. An agent that trusted the finding would have "fixed" a page that
   was already right.
2. An audit claimed the page's token figure sat well below what the
   repository's measurement implies. The repair agent recomputed from the raw
   record, got a mean of 1,711.6 tokens and a minimum of 1,578 across the
   thirty granite4.2 reasoning-off free runs, and rejected the auditor's
   arithmetic. The page's figure has a different problem, which it escalated
   separately.
3. An audit called a rubric header comment "only half true". The agent read the
   alignment matrix and quoted the sentence that makes the comment accurate.

**What it escalated rather than acted on.** Both of the false positives my own
concurrent scheduling created:

- *the missing corpus emails.* It confirmed the count on disk and escalated
  instead of changing which emails week 4 uses. Silently swapping an email
  would have changed what the week teaches.
- *the ten video ids with no scene list.* It escalated instead of deleting the
  `::: video` blocks. Deleting them would have removed a required deliverable
  from five weeks.

It also escalated the CLO3 reporting gap, which is the Canvas one-Outcome trade
and a decision for the program manager, not for a repair pass.

**Why this matters beyond week 4.** The audits are deliberately adversarial and
were run against a half-built world. A repair stage that treats findings as
instructions turns every false positive into a regression, and the regressions
would be invisible: a removed video block and a swapped email both leave a page
that renders and passes every gate. The instruction that carried it was one
sentence, "judge each finding before you act on it, an auditor can be wrong,
and a wrong fix is worse than the finding," and it did the work.

The agent reported `clean: false` while escalations remained open, which is the
honest answer rather than the flattering one.

## 15. Whether the audit layer earns its cost, tested deliberately

I found three wrong numbers in the new readings by hand, while the audits were
still running, and deliberately did not fix them. The question was whether an
independent adversarial pass would find the same things, because that is what
decides whether the verification layer is worth what it costs.

**One was found and fixed without me.** `w5-content.md` claimed the coded stop
condition ended runs correctly "88 times in 90". No grouping of the measured
runs gives that: the coded rows are 30/30, 30/30, 30/30, 28/30 and 18/18, and
the report's own figure is 136 of 138. The page now reads **136 times in 138**,
which is the number I had derived and had not applied. The audit chain reached
it independently.

**One was found from the wrong direction.** `w4-content.md` gives a full run as
"about 24,000 tokens". An auditor claimed the figure sat *below* what the
repository's measurement implies. The repair agent recomputed, found the
auditor's arithmetic did not hold, and rejected it, then escalated the separate
and correct point that the page states a projected figure without the
blueprint's own caveat. The real defect is that the week 4 spec derives 21,342
tokens line by line and the page rounded it up by 13 percent with no working
shown. Half caught.

**One was not found.** `w7-content.md` introduces a worked score block with
"Your notebook prints this", which reads as a promise about the student's own
numbers rather than as an example. A student scoring 0.70 would think they had
broken something.

**What that says.** Three lenses per week, run adversarially, caught one of
three cleanly, one partly and from a wrong premise, and missed one. That is
worth having and it is not sufficient on its own. The cheap hand pass over
every number in a new page found all three in a few minutes, and the two
methods do not overlap as much as either would suggest alone.

The queued corrections are in `<scratchpad>/apply-queued.py`, which refuses to
change anything it cannot match exactly. It reported the week 5 line as already
corrected rather than applying a second edit, which is how I learned the audit
had got there first.

## 16. A corpus vendor name was a real company

**What was wrong.** The benefits broker in the corpus was Tidefern Benefits, on
`tidefernbenefits.example`. The token is an exact match for TIDEFERN LIMITED, a
real New Zealand company: NZBN 9429049122558, company number 8168656,
registered 10 March 2021 to 2 May 2022, status Removed, industry "G425310
Jewellery retailing". Confirmed from two independent sources.

The corpus rule is absolute. No real brand, company, product, person or
trademark, every proper noun invented. The Phase 0 design tells the program
manager that every business name was web-searched.

**Why the mitigating facts did not change it.** The company is dissolved, it is
a one-person jewellery retailer, and no trademark was found for it. But the
match is exact rather than near, the rule has no exception for a dissolved
company, and the name sits on a vendor whose domain is spoofed in a credential
phish. Tying a real company to a phishing lure is the association the rule
exists to prevent.

**The deeper defect.** No search had ever been recorded. The Phase 0 claim rested
on nothing a reader could check, so nothing could have caught this except
someone re-running the search by hand.

**What changed.** The name is now Vetchmoor. The rename covered 320 occurrences
across 17 source files in one pass, and the build re-rendered the four emails
that carry it. Four generator filenames and four email ids changed with it:
`013-vetchmoor-census-correction`, `024-vetchmoor-census-control`,
`053-vetchmoor-plan-documents` and `056-vetchmoor-quarterly-update`. The
broker's DKIM selector `tf1`, which was the old name's initials, is now `vm1`.

Emails 013 and 024 are a deliberate control pair, so a partial rename would have
desynchronised them. They were renamed together and re-rendered together, and
the rendered pair still shares every body line in both parts.

None of the six emails whose digests the week 5 measurement recorded was
touched, and `build_corpus.py` confirms it on every run.

**What now stops it coming back.** `docs/corpus-naming-record.md` is new. It
records the register, the searches that cleared Vetchmoor, what each source
returned, and which sources were blocked and therefore did not count. It ends
with the eight-step method for the next name. That file is the answer to "how do
you know these names are invented", which `corpus/README.md` claims and could
not previously show.

**Still open, and not closed by this pass.**

- The other twenty register names have no recorded evidence. Phase 0 says they
  were web-searched; nothing shows it. Phase 0 section 15 item 6 already asks
  for the search to be re-run before the corpus ships, and that is now the job
  that clears them.
- Names inside email bodies, such as payees and projects, are in no register at
  all.
- `docs/manifest-concerns.json` and `docs/phase0-download-test.json` still carry
  the old token, deliberately. The first quotes what the authoring agents said
  at the time and is rebuilt from immutable workflow journals. The second is a
  Canvas measurement whose recorded sha256 and byte count describe the old file.
  Editing either would falsify a record. Both need re-running or annotating by
  their owners, not editing.

## 17. A real company's name was in the corpus, and the naming claim could not be shown

**What was wrong.** The vendor "Tidefern" is not invented. It is an exact token
match for TIDEFERN LIMITED, a New Zealand company: NZBN 9429049122558, company
number 8168656, registered 10 March 2021 to 2 May 2022, status Removed,
industry "G425310 Jewellery retailing". Confirmed from two independent sources
and then checked again by hand against the register that holds it.

The corpus rule has no exception: no real brand, company, product, person or
trademark, every proper noun invented. The Phase 0 design document tells the
program manager that every business name was web-searched.

**Why it mattered more than a coincidence.** In this corpus "Tidefern" is a
benefits vendor **whose domain is spoofed in a credential phish**, in emails
013 and 024, and it appears in three more. Attaching a real registered name to
a phishing lure is the association the rule exists to prevent.

The mitigating facts were reported honestly by the verifier that found it and
do not change the decision: the company is dissolved, it is a one-person
jewellery retailer, it holds no trademark anyone could find, and it shares no
industry with a benefits broker. The match is exact rather than near.

**How it was found.** The safety lens of the corpus verification, which
web-searches every proper noun a message introduces, at eight to ten searches
per email. This is the check that justifies that cost.

**Fixed.** Renamed corpus-wide to **Vetchmoor**, in one pass across five
generators, five data files, the manifest, the ground truth, four documents and
the injection harness, including the file stems and the manifest ids for 013,
024, 053 and 056, both domain labels, the display name and the DKIM selector.
Emails 013 and 024 are a deliberate byte-twin control pair, so a one-file
rename would have desynchronised them.

The six emails the week 5 measurement recorded digests for were untouched, and
the build confirms they are still byte identical.

**The new name was earned rather than assumed.** Vetchmoor was checked against
the New Zealand register that caught Tidefern, UK Companies House, the
Australian ABN lookup, US business entities, the Canadian trademark database,
domain and brand searches, and a trademark sweep. One earlier candidate,
Quillmarsh, was rejected for an exact match with a location in a published
novel. Six further checks were BLOCKED by CAPTCHA or authentication and are
recorded as blocked, because a check that did not run is not a pass.

**What stops it coming back.** `docs/corpus-naming-record.md` now holds the
evidence for the names, which is the thing the corpus README claimed and could
not previously show.

**Two files still carry the old token on purpose.**
`docs/phase0-download-test.json` is a Canvas measurement record, and editing it
to match the renamed files would falsify a measurement, which is the failure
shape this project has a memory file about. `docs/manifest-concerns.json` is
generated from immutable workflow journals. Both need re-running rather than
editing, and that is recorded rather than hidden.

## 18. The corpus build could pass on a corpus that contradicts itself

**What was wrong.** `build_corpus.py` ran every generator once and reported the
result. One pass is not enough.

A generator writes its own prose fields back into `spec/corpus-spec.json`:
`body_brief`, `lure_summary` and `notes`. Generators run in id order. So text
that `gen_033` writes into the manifest is invisible to `gen_004` until the
**next** run.

**What that hid.** `gen_004` reserves the BEC payee name "Quillbeck Controls"
and guards it: the name must appear in no other manifest record, because email
004 has no link, and the week 5 lesson is that `check_urls` is the wrong second
move and the loop stops on `tools_exhausted` after two calls. A payee an agent
could look up breaks that.

Email 033, written in this phase, coined `quillbeck-castings.example` for a
held message in a fake quarantine digest. A different company, the same token.
Its author checked the data files and the other emails, exactly as its own
comment says; the reservation lived in a generator constant and in manifest
prose, which that check did not cover. Both authors followed a correct rule and
neither rule covered the other's ground.

**The false pass.** The first build after `gen_033` existed came back **corpus
build clean**, because `gen_004` read the manifest before `gen_033` had written
to it. The next build failed. A single pass can pass on a corpus that is not
consistent with itself, and it did.

**Fixed, in two places.**

1. Email 033's company is renamed to **Tarnfield Castings**, checked against UK
   Companies House, the New Zealand Companies Register and the Australian ABN
   lookup, none of which holds the token, and absent from every shipped file.
   The reason is written into `gen_033` where the next reader will look.
2. `build_corpus.py` now runs the generator pass to a fixed point rather than
   once, and says so when a build needed more than one pass, because a corpus
   that needs two passes means one generator changed something another
   generator reads.

Verified: the build is clean on a first run from a settled tree, and
`--check-reproducible` still confirms every rendered file is byte identical on
a second run.

## 19. The exam assembler made the right change and described it wrongly

**What happened.** One of the seven exam part files, `exam-parts/CLO2.yaml`,
wrote code names in answer feedback as markdown backticks where the other six
used `<code>`. Canvas stores question text and answer feedback as HTML, so
backticks would have reached students as literal backtick characters.

The assembler converted them. That is the correct fix and the shipped exam is
right: `final-exam.yaml` carries 77 `<code>` spans and no student-visible
backtick. The three backticks left in the file are in `section` fields, which
are author metadata that `make_quiz()` never sends to Canvas.

**What is wrong is the report.** The assembler stated that "every stem, option
and piece of feedback diffed against exam-parts/ - zero mismatches", and
separately raised the backticks as a concern it had "carried verbatim rather
than silently rewritten". Both cannot be true, and neither describes what it
did: five student-visible strings differ between the part file and the shipped
exam.

**Why it matters more than the typo does.** A build that reports a clean diff
while changing content is the shape of every silent failure in this project's
record. Here the change was an improvement, so nothing is broken. The next one
might not be. The claim is the defect, not the edit.

**What stops it.** Nothing yet, and that is the honest state. A source-to-built
diff for the exam would need `make_quiz()`'s own transformation applied first,
so the check is "does the built file equal the parts once the documented
conversions are applied", not "are they identical". Recorded for the QA report
rather than papered over.

## 20. A second export path the exam cannot use

`tools/qti.py` cannot build `final-exam.yaml`, and `canvas/build_course.py`
can. Three reasons, all structural:

- `CANVAS_TYPE` has no `text_only_question`, so `qti.item()` raises
  `ValueError` on all six reference blocks.
- `qti._metadata` reads `question["type"]` directly, so it raises `KeyError` on
  the thirty scored items, which correctly carry no `type` key.
- `qti.validate()` requires an outcome on every item and returns 42 problems on
  a file the Canvas API builder accepts cleanly. The exam creates no Canvas
  Outcome results by design, which the exam blueprint sets and the alignment
  matrix explains: a selected-response score must stay out of the outcome
  roll-up.

This is the same shape as `tools/cartridge.py`, recorded in finding 11: a
second delivery path whose schema this course does not use. The build brief
requires the Canvas API, so neither is on the path. Both are worth naming in
the QA report so nobody reads a red gate as a broken course.

`tools/` is shared with two other courses and was not changed.
