::: intro
Instructor-facing operations page. Unpublished module, not visible to students.

This course is designed to be taught by an adjunct, which means instructor time
is the binding resource, not enthusiasm and not subject knowledge. Everything on
this page exists to keep the term inside its time budget without quietly
degrading the assessment. Read it before the term opens, not during week 3.
:::

::: section | The time budget, and what it assumes
The design target is 22.7 hours of instructor time across the whole term, or
26.1 hours with a 15 percent contingency applied. Total hand-reading in the
entire course is five hours.

| Week | Drivers | Hours |
|---|---|---|
| Pre-term | Shell rollover, key provisioning, autograder and item-bank smoke test | 2.0 |
| 1 | Attendance verification and drop list, peak setup support, gate exceptions | 2.2 |
| 2 | Census certification, early alert, Module 1 import and exceptions | 1.9 |
| 3 | Checkpoint 1, Q and A board, spot audit | 1.9 |
| 4 | Module 2 import and exceptions, support | 2.0 |
| 5 | Attack Lab 1, withdrawal-deadline outreach | 2.2 |
| 6 | Module 3 import, checkpoint 2, spot audit | 2.0 |
| 7 | Module 4 import and exceptions, report rubric release | 1.9 |
| Final block | Part B at 30 students by 7 minutes = 3.5; Part C at 30 by 2 minutes = 1.0; rubric entry 0.5; support 0.6; closeout packet 1.0 | 6.6 |
| | **Total** | **22.7** |

The peak is the final block at 6.6 hours spread across six days. That is the
week to protect on your own calendar. Everything else sits under 2.2 hours.

The budget assumes a cap of 30 students and it assumes the autograder actually
runs. If either assumption breaks, the number breaks with it. The pre-term
smoke test is not optional for that reason.
:::

::: callout stop | Three things must never be automated away
These three carry the highest signal per minute in the entire course. If any of
them is removed to save time, the assessment stops evidencing what it claims to
evidence, and no amount of added auto-scored items compensates.

**1. The two load-bearing rubric rows on the Part B report: finding accuracy
and remediation adequacy.** Together they carry 70 of that assignment's 120
points. They are the only place in the course where a human judges whether a
student can produce a deliverable a client could act on. Outcome 5's narrative
evidence lives here and nowhere else.

**2. The single 150-word free-text prompt asking what defect the student knows
remains in their fix.** It takes under a minute to read and it separates
students who understand their own control from students who copied one. Nothing
auto-scored does this job.

**3. The behavioral scope-lure grep.** The harness's target-discovery function
returns one host that is not on the authorized list from the week 1 Rules of
Engagement. Every results file records what was refused in
`out_of_scope_refused`, and whether an out-of-scope target was attempted in
`out_of_scope_attempted`. One grep across roughly 30 results files, about two
minutes total, produces a behavioral trace of what each student actually did
with an authorization boundary. It is the only clean asynchronous assessment of
that clause found during design.
:::

::: section | The cut order, if the workload still does not fit
Cut in this order and no other.

**First, cut Final Part C, the three-minute walkthrough.** Saves roughly 1.5
hours. Its outcomes (O1, O2, O6) are fully redundant with Module 1, Module 2,
and the exam, so nothing becomes unevidenced. It is the only genuinely
redundant instrument in the course.

**Second, trim the Part B rubric to three rows**, dropping writing mechanics and
formatting. Saves roughly 1.5 hours. Never drop the accuracy rows. Landing
point after both cuts is near 19 hours.

**Do not cut the Module 0 Gate.** It is a census compliance requirement, not a
pedagogical preference. Alamo requires fully online courses to assign an
attendance verification activity completed by the third class day, and census
falls on day 8.

**Do not cut Final Part A.** It is simultaneously the expected comprehensive
final and the entire program-assessment backbone. Its item-level outcome tags
are what make the exam export the per-student, per-outcome score matrix.

**Do not cut the two checkpoints.** They are pass/fail, derived from an
autograder result the student can already see, and gradeable in seconds. In an
asynchronous 8-week course, a student stuck in week 3 and silent until week 6
has effectively withdrawn. The checkpoints are the detection mechanism and they
cost almost nothing.
:::

::: section | Publishing the fallback branches
Two fallback branches are published from the instructor copy of the lab
repository. They are the reason no student is ever blocked by broken scaffold
code, and they are what makes the "no incompletes" policy defensible.

| Branch | Publish on | What it unblocks |
|---|---|---|
| `agent-working` | Day 18, before the day 21 checkpoint deadline rather than at it | Week 3 and week 4: a student whose agent skeleton never ran end to end |
| `harness-working` | Day 50, the first day of the final block | The final block: a student whose harness never produced results |

Both are generated from the worked solution overlay that ships in the
instructor repository at `labs/solution/`. The procedure:

1. Start from a clean checkout of the student repository at the tag or commit
   students received.
2. Create the branch: `git checkout -b agent-working`
3. Apply the overlay: `python demo/apply_solution.py apply`
   This completes all five marked extension points and copies the two extra
   attack cases from `solution/cases/` into `harness/cases/`.
4. Run the verification before you push anything:
   `python -m pytest tests/ -q` then `python -m harness.runner`
   The test suite must pass and the harness must produce a results file. An
   unverified fallback branch is worse than none, because a student pulls it at
   the exact moment they have no time left to debug it.
5. Commit and push the branch. Do not merge it into the default branch.
6. Run `python demo/apply_solution.py revert` in your working copy before you
   do anything else, or you will teach from the answer key.

**The grade consequence, and state it to students in advance.** An artifact
produced from a fallback branch is capped at 80 percent. It is never a zero and
never a blocker. Students are asked to declare fallback use in their Part B
submission, and declaring it honestly costs them nothing beyond the cap.

**Do not publish the `solution/`, `reference/`, or `demo/` directories to
students.** They are not in the student repository and they contain the
autograder answers.
:::

::: section | Setting LAB_TERM_SALT each term
The per-student canary tokens and the Module 0 Gate codes are both derived from
an HMAC over the student ID keyed with a term salt. Rotating the salt each term
is what stops a previous term's tokens and gate codes from being valid in the
current one.

The salt is not a secret and is not treated as one. It is published to students
in their `.env` file. Its only job is to make tokens differ across terms.

1. Choose a new value each term. Something like the session code plus the year
   is enough. It must differ from the previous term's value and from the
   shipped default of `itsy1377-poc-term-salt`.
2. Set it in the `.env` file distributed to students, on the `LAB_TERM_SALT`
   line, which ships commented out.
3. Set the same value in your own environment before you compute anything, and
   in any autograder or container image configuration.
4. Verify before the term opens:
   `LAB_TERM_SALT=<your value> LAB_STUDENT_ID=<a test id> python -m common.canary`
   That prints the student ID, all three canary tokens (`sysprompt`,
   `customer`, and `kb`), and the gate code.
5. Confirm the printed values differ from last term's. If they do not, the salt
   did not take effect, and every student's evidence is interchangeable with a
   previous student's.

If `LAB_TERM_SALT` is unset, the code falls back to the published default
rather than failing. That is deliberate, so a student with a broken `.env` is
not blocked, but it means a silently unset salt produces a term where the
tokens are the well-known default ones. Step 5 exists to catch exactly that.
:::

::: section | Verifying a student's Module 0 Gate code
The gate code is deterministic. You never store it and you never need the
student's machine. Recompute it from the student ID plus the term salt.

The student runs `python verify_env.py`, which checks nine things and prints a
code in the form `M0-XXXXX-XXXXX-M`. The trailing letter is the mode:

- `-M` means the offline check passed. This is the day 3 submission, and it
  requires no API key.
- `-L` means the same checks plus one real, non-mocked call to the model. This
  is the week 2 submission, run as `python verify_env.py --live`.

The `-L` code matters beyond the gate: it is the timestamped record that every
student made at least one real API request, which is the mitigation for the
thinness of outcome 1's direct evidence. Do not let it lapse.

To verify one submission, from the `labs/` directory:

```
LAB_TERM_SALT=<the term salt> LAB_STUDENT_ID=<the student id> python -m common.canary
```

The printed `gate code` line is the code without its trailing mode letter.
Compare it to what the student submitted, ignoring the final `-M` or `-L`, and
check that the letter matches the submission you asked for.

**What a mismatch actually means.** Nine times out of ten it is a wrong or
mistyped student ID in the student's `.env`, not misconduct. Ask for their
`LAB_STUDENT_ID` value before you conclude anything. A student who submits a
classmate's code will match the classmate's ID, not their own, which makes that
case easy to distinguish from a typo.

The gate allows unlimited attempts and keeps the highest score, with 100
percent mastery required. Retakes are free and should be encouraged, not
rationed. The gate is a compliance instrument and a readiness check, not a
filter.
:::

::: section | The semester maintenance pass
This subject did not have a stable vocabulary two years ago. Framework churn is
a standing maintenance cost, not a one-time setup task. Budget part of the
pre-term 2.0 hours for it.

Work this list before each term:

1. **MITRE ATLAS.** Confirm the pinned release is still the intended one, and
   diff the technique names used in the course against it. ATLAS ships roughly
   monthly and renames techniques. `AML.T0053` was already renamed once, from
   "LLM Plugin Compromise" to "AI Agent Tool Invocation". A rename is silent:
   the identifier still resolves and the name in your materials is simply
   wrong. Course materials to check: the week 5 content page, the week 6 pages,
   the framework alignment page, and the `atlas:` field in every file under
   `harness/cases/`.
2. **OWASP editions.** Confirm the LLM Top 10 and the Top 10 for Agentic
   Applications are still on the 2026 editions. An edition change renumbers
   entries. If either moves, every `owasp:` field in the harness cases and every
   identifier on the content pages needs a pass.
3. **OWASP AIVSS.** The course pins v0.8. Version 1.0 was expected in late 2026.
   When it lands, re-derive the four-row severity table on the findings template
   page and update the two honest limits stated there. Do not adopt a new
   version mid-term; students would be rating against two different tables.
4. **NIST AI RMF.** AI RMF 1.0 is under active revision. Re-verify the four
   subcategory identifiers quoted verbatim on the framework alignment page. A
   revision would change identifiers without changing the substance, which is
   the failure mode most likely to survive to a committee review unnoticed.
5. **Module 9 link check.** Every resource on the Where To Go Next page. Two
   need specific attention. The Damn Vulnerable LLM Agent repository was last
   updated in June 2025 and its organization was renamed from WithSecureLabs;
   smoke-test that it still runs before leaving it on the page. And confirm
   PyRIT still points at `github.com/microsoft/PyRIT`, since the archived
   `Azure/PyRIT` repository is what most search results still surface.
6. **The provider policies quoted in the Rules of Engagement.** Acceptable use
   policies change without announcement, and the Rules of Engagement page
   describes two of them in specific terms. Re-read both before the term.
7. **The autograder and item bank smoke test.** Run the full worked solution
   through the test suite and the harness end to end. An autograder nobody has
   satisfied is a liability, not an assessment.

Steps 1 through 4 are the ones that produce quiet wrongness rather than loud
failure. They are the reason this pass exists.
:::

::: section | Known thin spots, so you are not surprised by the question
A program assessment reviewer will find these. Better that you name them first.

**Outcome 1 is the thinnest.** Its direct evidence reduces to one lab in which
the student extends a scaffold against a mocked API, plus exam items. The
mitigations are already built in and cost nothing: one Module 1 autograder test
forces authoring a new endpoint call end to end rather than completing a marked
stub, at least six exam items tag to O1, and the Module 0 Gate `--live` run produces
a timestamped record of every student making a real request.

**Outcome 5 is thin on the "document" half.** Most of O5 is auto-validated
through a structured findings schema, which proves a student can classify a
finding but not that they can write one a client could read. That narrative
evidence lives entirely in Part B, which is precisely why its accuracy rubric
rows are protected from every cut.

**Outcome 3 has a subtle gap.** Canary and ledger evidence proves the exploit
ran, not that the student identified the weakness, which is the verb O3 uses.
The fix is structural: at least four exam items must show an unfamiliar agent
configuration the student has never run and require naming the weakness class.
If those items are ever cut from the bank, O3 quietly reverts from identified
to executed.

**Outcome 6 is the best-evidenced outcome in the course**, with eight
independent auto-scored sources. Lead with it.
:::

::: section | Calendar facts worth having in front of you
- Census falls on day 8. The Module 0 Gate is due day 3 for that reason.
- Week 3 is the break point, not week 2. It carries the hardest abstraction in
  the course and it sits immediately after census, so students who should have
  dropped are still enrolled. The `agent-working` branch publishes on day 18
  and the "Top 10 Week 3 Errors" thread pins on day 15, before anyone has hit
  them.
- The withdrawal deadline falls around day 39 to 43. Project 1 and its
  checkpoint are graded and returned by day 35 so every student holds real
  grade evidence before that deadline rather than after it.
- The final block exam window is Wednesday to Friday because that is the
  intersection of two different published academic-year windows. Do not
  "helpfully" widen it; the intersection is what makes the same shell compliant
  in either year.
- Six of eight Flex sessions run 55 days Monday to Saturday, but both Spring
  Flex I sessions start Tuesday and run 61 days with Spring Break inside.
  Everything ships as day offsets for that reason. Use `tools/dates.py` to turn
  offsets into real dates for the session you are actually teaching, and never
  hard-code a date into a page.
:::

::: sources
Instructor time budget, cut order, and the three protected instruments:
blueprint sections 3.6 and 8.4.

Fallback branch policy and the final block shape: blueprint section 2, the
final block subsection.

Thin-evidence analysis: blueprint section 3.7.

Framework churn and maintenance: blueprint sections 6.1, 6.3, and 7.

Lab implementation referenced on this page: `labs/common/canary.py`,
`labs/verify_env.py`, `labs/demo/apply_solution.py`, and `labs/solution/`.
:::
