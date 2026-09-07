# What a student run and four reviewers found

**Written:** 2026-09-07
**Status:** findings and a worklist. **Nothing in the course has been changed
because of it.**

A blind agent took the whole course as a novice would: Canvas pages and
notebook.bashtion.dev only, no access to this repository, no answer keys. It
finished all eight modules, wrote all fourteen TODO cells correctly on the
first attempt, and spent $0.0114 of a $2 budget. Four reviewers then read its
report against the source: instructional design, a SOC practitioner, test
strategy, and beginner experience.

Their full reports:

    scratchpad/student/REPORT.md              the run, 29 numbered problems
    scratchpad/student/FINDINGS.md            notes written after each module
    scratchpad/review-instructional-design.md 5,900 words
    scratchpad/review-accessibility.md        6,600 words

Items marked **verified** were checked against the source or the live site
while writing this page. The rest are reported and not yet confirmed.

---

## 1. Fix today

### 1.1 The batch answer key is being served to students

**Verified.** `corpus/release/ground_truth_batch.json` returns HTTP 200 from
the public site, 192,858 bytes. Week 7 reads three fields from it. It ships
thirty-four per record, including `indicators`, `required_indicators`,
`reference_summary`, `recommended_action` and `escalation_reasons` -- which are
what week 7's triage note is graded on.

`never_ship` is a basename denylist and cannot see inside a file.
`stage_notebook_site.py` printed `NOTE: shipping ... allowlisted on purpose`,
the name was checked, the contents were not.

**Fix:** emit a student projection carrying `id`, `verdict`,
`escalate_expected` and `label_version` -- about 3.1 KB -- and add a content
gate asserting every staged JSON's record keys are a declared subset.

### 1.2 Week 7 does not run for any student

**Verified.** `w7-lab.ipynb` cell 8 loads
`corpus/release/ground_truth_teaching.json`. The file is in `never_ship` and
absent from `student_files`, so the site returns 404. Uncaught
`FileNotFoundError`, Run All stops, and the two submission artifacts below the
crash are never produced.

**Do not fix this by shipping the file.** It is the complete answer key for
weeks 1 to 6. The student's report recommends shipping it; three reviewers
independently refused. Inline the one record week 7 needs, or generate a
three-field projection.

### 1.3 Following the week 6 reading crashes a pre-written cell

`content/assignments/w6-lab.md` line 16 tells the student to write a fourth
fact check on Reply-To. Cell 15's sample dictionaries carry no `reply_to` key
and the call is not guarded, so the cell raises `KeyError`. The reviewer
reproduced it. The blind student escaped only by choosing the notebook's three
rules.

---

## 2. Week 1 loses people, and two of the holes are silent

Week 1 is where a beginner decides whether the course is survivable. Both of
these were verified in the source.

**A student can fake the experiment without knowing it.** Cell 10 calls
`ask_model(PROMPT_001, temperature=temperature)` six times. A beginner whose
`ask_model()` ignores the parameter -- which the spec invites by saying "the
default is 0.2" -- sends six identical requests. The only check is
`CHECK_ANSWER.startswith("ask_model() is not written")`, which passes. The cell
then labels the six answers by temperature, the screenshot looks right, and
half the week's grade turns on a written analysis of an experiment that never
ran.

**A student who does the work correctly can lose the marks silently.** Cell 9
is `# your code here`: the only TODO in the course with no stub and no
sentinel. Nothing reads the student's variable except the export cell, which
writes `str(globals().get("prompt_001", "not recorded"))`. Name the variable
anything else and the graded file contains the words "not recorded", with no
warning anywhere.

Both fixes are one line each.

---

## 3. The pattern under most of the rest

Two reviewers reached the same root cause from opposite directions.

Instructional design: the contingency clauses live in the notebooks and the
discussion prompts, and never reach the assignment pages or the rubrics, which
are what set the grade.

Test strategy, counting the same thing: **259 of 700 lab points sit in criteria
that cannot discriminate.** Forty-seven of those are points a correct
submission cannot earn, because the rubric asks for an artifact the lab does
not produce -- week 2's "every failed try" when nothing failed, week 7's "one
of your own wrong emails" when none were wrong.

The notebooks already print the right fallback in both cases. The rubric never
caught up.

---

## 4. The accreditation problem

`content/quizzes/exam-parts/` holds seven files: `B1 B2 B3 B4 CLO1 CLO2 CLO4`.
**CLO3, CLO5 and CLO6 have no exam coverage**, and fifteen of thirty exam items
map to no CLO at all.

With `calculation_method: latest` and one Outcome per rubric, CLO5 rests
entirely on one rubric row and CLO6 on one other -- both in week 7, the lab
that crashes. CLO6's evidence is the accuracy figure computed against a sorted
answer key.

**Verified:** ids 026-035 are all malicious, 036-045 all benign, processed in
id order. "Call the first ten malicious" scores 100%.

Interleaving alone does not fix it. `score_batch()` asks the student to
separate false positives from false negatives and self-checks only that the
three counts total twenty; on a perfect run both error counters are zero, so a
student who swapped the branches passes and cannot tell. At least one email has
to land wrong. Emails 033 and 040 are a designed near-pair and are the
candidates.

---

## 5. Why no gate caught any of it

**The gate's filesystem is a strict superset of the student's, and the delta is
exactly `never_ship`.** Every file the course promises students will never see
is a file the gate silently supplies. That is not one bug; it is a structural
guarantee that this class cannot be caught.

`stage_notebook_site.py` builds the correct tree and has **zero callers**.

Nine dimensions differ between where the checks run and where the course is
delivered: filesystem, endpoint, model, rate limits, budget and auth, Python
runtime, persistence, key entry, and the network edge.

Two consequences nobody is testing. `budget_left()` fails against the test
endpoint and the exception is swallowed. And `backup_my_work()` and
`restore_my_work()` -- the only defence against a student losing a term's
work -- early-return outside the browser, so they **have never been executed by
any check**.

The repository already wrote down the rule it needed, in
`docs/infrastructure-decision-memo.md`: *assert what the server did, not what
the request asked for.* Week 7 is that rule applied to the filesystem.

**The single highest-yield change** is to run the notebook checks inside the
staged site tree rather than the source folder. A forty-line static path
resolver catches week 7 in about a second in the meantime.

**Second highest:** no check cell is ever tested against a wrong answer.
`run_notebook.py` runs TODOs empty or correct, never wrong. The check cells are
the course's real test suite and nothing tests them. The failure modes are
already enumerated in `instructor/common-failure-modes.md`.

---

## 6. Where the reviewers overruled the student

Worth recording, because the student's report is otherwise sound and these are
the places acting on it would do harm.

**Shipping `ground_truth_teaching.json`** would publish the answers to six
weeks. The reviewer's explanation of the mistake is the useful part: when the
gate runs where the answer key is present, "just ship the missing file" looks
like a one-line fix to everyone who reads the failure.

**The `.example` domains are not the defect.** The student reported that
reserved domains break the model's judgement and implied the corpus should
change. Substituting plausible domains would train students to trust a
familiar-looking name, which is the reflex BEC monetises. The real gap:
**nothing anywhere tells the model the corpus is synthetic** -- verified, zero
mentions in any page or notebook. About twenty tokens of prompt fixes it.

**The sorted key did not corrupt the student's own score.** `run_batch()` sends
one email per request with state reset between, so the model never sees the
order. The 20/20 was clean. Distrusting it was a correlation-causation error --
and, as the reviewer notes, exactly the reasoning error week 7 exists to train
out.

**"Grounding made the agent worse" rests on one email of six.** Email 017 is a
false positive with a defensible reading; its ground truth records
`body_only_read: uncertain`, not benign.

---

## 7. What is good, and should survive the edits

- **The check cells and the failure-first ordering.** Week 5 runs the student's
  loop with the cap at zero, for free, to catch a missing stop condition. Week
  7 diffs the note line by line and, when only spacing differs, counts the
  leading spaces and says so in words.
- **The rubrics repeatedly refuse to grade the model's behaviour.** That is
  what saved weeks 3 and 6 for the student when the model misbehaved.
- **The authentication teaching in week 3** -- email 004 passing all three
  checks and being malicious anyway, then 006 failing all three and being
  legitimate -- was rated better than most commercial training.
- **Playbook rule 5**, that any change to bank details gets a callback whatever
  the verdict, is the control that actually prevents these losses, and it is
  correctly stated as process rather than detection.
- **Email 015**, a benign notice built to punish a keyword rule, teaches that a
  detection has a cost. Almost no curriculum does.
- **The existing gates are better than most production suites.** The failure is
  placement, not rigour.

The student's own summary is the fairest line written about the course:

> Every failure I hit was in pre-written code, the corpus, or the
> documentation -- never in a TODO cell. The course teaches everything it asks
> students to write.

---

## 8. Still unmeasured

`lab/eval/week6_injection_test.py` is well built -- a two-by-two on payload and
guard, a word-for-word twin pair to isolate the payload, a cry-wolf control,
input hashes recorded -- and **has never been run**. Week 6 makes two claims
about its guardrails and neither has evidence. The student's single run
contradicts both.

It is blocked by the Cloudflare rule that challenges non-browser user agents.
Add the skip rule, run it, and publish the real number even if it is poor.
