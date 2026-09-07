# Assumptions and gaps

**Phase 1 blueprint, final section. Prepared 2026-09-04 for the program manager.**

This section lists every assumption the blueprint rests on and every gap that
still needs filling. It is the last piece of the blueprint and it is written to
be read on its own.

Items are grouped four ways:

- **Group A** holds assumptions the build is proceeding on. Each says what
  happens if it turns out to be wrong.
- **Group B** holds decisions only the program manager can make.
- **Group C** holds decisions or actions that belong to the college. It opens
  with the two items the build prompt itself puts outside its scope.
- **Group D** holds measurements this build can run, each with the thing that
  blocks it today.

Every item appears in exactly one group. Each is a short label and two
sentences. Where two blueprint documents disagree with each other, the
disagreement is named inside the item it belongs to, and each one is a single
edit in Phase 2.

One item that earlier documents list as open is now closed. The three triage
tool functions exist, and a checker reports that all three agree with the corpus
manifest on every field of all 56 email records. The note in the code ledger
saying that file is empty is out of date.

## Words used here

- **Canvas Outcome.** A Canvas object that stores a mastery result for one
  course objective, so the program can pull a report on it.
- **Rubric criterion.** One scored row of a grading rubric.
- **Mastery scale.** The four rating levels shared by all six Outcomes.
- **Token.** The unit a language model counts and bills. One token is roughly
  three quarters of a word.
- **Prompt.** Everything the code sends the model on one call.
- **Reasoning mode.** A model setting that makes the model write out its
  thinking before its answer. It costs time and tokens.
- **Corpus.** The 56 synthetic emails and the data files that ship with them.
- **TODO cell.** A marked notebook cell where the student writes the week's few
  lines of code.

---

# Group A. Assumptions this build is proceeding on

## A.1 Grades, rubrics and Canvas Outcomes

**A1. Equal points inside each group.** All seven labs carry 100 points, each
discussion 20, each self-check 12, and the exam 30 items at one point. If points
differ inside a group, that group's weight lands unevenly, and five week specs
that name other totals each need one edit.

**A2. One linked criterion per rubric.** Each weekly rubric links exactly one
criterion to a Canvas Outcome. Every other criterion measures a non-objective
expectation such as submission completeness, because two linked criteria on one
rubric would post two results at the same moment and make the most recent score
ambiguous.

**A3. Week 1 links nothing, and later weeks do not relink.** Week 1's rubric
carries no Outcome link, and weeks 4 and 6 reinforce earlier objectives without
linking to them. If every week must report, week 1 needs a linked criterion, and
any new link in a later week would overwrite the primary result from the week
that owns it.

**A4. Six course-level Outcomes with labels written here.** The six sit in one
course-level group named for the course, and their rating labels were authored
for this build because the prompt fixes only the scale. If the program has
standard labels, the six Outcomes and the seven rubrics that link to them are
rebuilt once.

**A5. The exam reports no Outcome data.** The final exam creates no Outcome
results, and its supporting role for three objectives is recorded in the exam
blueprint instead. If the program wants exam data in the report, a
selected-response score enters the objective roll-up, which the build prompt
warns against.

**A6. The course is closed to the public.** Course visibility, public access for
signed-in users, open enrollment and self enrollment are all off, against a
template that sets all four on. If the template's settings were copied, the
phishing corpus and student work would be visible outside the class.

## A.2 The institutional template

**A7. Verbatim means the words.** Institution pages keep their wording, and
their markup is rebuilt so the template's accessibility defects do not travel
into this course. If verbatim also means the HTML, the zero-error accessibility
target cannot be met on those pages.

**A8. No page-styling add-on on the target instance.** The build assumes the
instance has no DesignPLUS theme, which is the add-on the template's markup is
written around. If the production instance has it, every authored page is
rebuilt in that markup.

**A9. A fifth assignment group at zero percent.** The template's one-point
introductions board sits in a fifth group weighted at zero percent, so the
prompt's four weighted groups still total 100. If a zero-weight group is not
acceptable, either the board goes or the grade weighting changes.

**A10. Eight items per weekly module.** *Amended in Phase 2. This assumption
first read "six items per weekly module", with the two notebooks linked from
inside the Content page and the Lab assignment.* Each weekly module keeps the
template's pages and assessments and adds the sidebar notebook and the lab
notebook as items of their own. A course whose work happens in a notebook
should not put a page between a student and the notebook. The template's page
set is unchanged and every page is still filled. Module 0 carries four items on
the same rule. The reasoning is in `template-conflicts.md` section 8,
amendment A.

**A11. A fourth column in the Tasks table.** The template's three-column table
gains a column for estimated time, because the prompt requires a time on every
activity. If the three columns are fixed, the times move into one sentence under
the table.

**A12. Module titles carry no dates yet.** Titles read "Module N: Topic", and
the template's date portion waits for the term calendar. If dates are required
in titles, the nine numbered module names change at once.

**A13. Two modules drop items they cannot fill.** Module 8 has no Content page,
and module 0 has no discussion, no assignment and no Content page. If every
module must carry the template's full item set, week 8 gains a page that would
add instruction the prompt forbids.

**A14. The AI panel stays, and the course authorizes AI.** The district panel is
kept word for word, and the course policy uses that panel's own clause allowing
an assignment to authorize AI use. If the college reads the panel as a flat ban,
this course cannot require students to use AI as designed.

**A15. Institution support pages are exempt from two content rules.** The
zero-external-services rule and the open-licence rule are read as binding on
content this build writes, not on the college's own student support pages. If
they bind those pages too, sixteen vendor links and several embedded videos come
out of pages the college owns.

**A47. The Orientation page set is fixed by the writing gate.** The readability
checker reads a page's word budget from its file name and recognises a closed
list of orientation stems, so a page named outside that list is scored against
the 1400 word content budget rather than the 450 word orientation budget. The
"how the course works" material therefore sits on the Welcome page, which is
where template conflict 4 puts it. Adding a further orientation page means
adding its stem to the checker in the same change.

## A.3 Notebooks and student code

**A16. Names this build invented.** The API key variable name and the seven
submission file names are inventions, because nothing in the prompt or the
corpus fixes them. If any changes, one line changes in every notebook and the
submission instruction changes on seven pages.

**A17. The key arrives as an environment variable.** Notebooks read the key from
the environment and never display it. If the hosting cannot inject one variable
per student, the course falls back to a single course key on a page only
students can open, which the prompt allows.

**A18. No classes anywhere.** Students never write or read a class, and plain
dictionaries hold the state an object would hold. If objects were required, week
0 would have to teach something the prompt puts out of scope.

**A19. Week 0 teaches five constructs the prompt does not list.** The on-ramp
adds a while loop with a counter, lists with append, a safe key lookup with a
default, elif and in, and joining lines into one block. Without them, weeks 3 to
7 ask students for constructs no page ever taught.

**A20. Week 0 section numbers follow the prompt's own order.** Calling functions
is section 2, f-strings section 5, loops section 8. If the sections are
renumbered, four sidebar links back into week 0 need editing.

**A21. One on-ramp notebook, one practice quiz, no model calls.** The on-ramp
ships as a single notebook with an index, and the self-assessment as an ungraded
practice quiz the notebook links to. Neither calls a model, so week 0 costs
nothing and can be finished before a key is issued.

**A22. The notebook folder behaves normally.** The working folder is writable,
and the two helper files import by name with no path handling. If the hosted
setup differs, the export cell and every import line need changing.

**A23. The model call keeps one shape all term.** The ask_model function takes
text and returns text from week 1 to week 7, and tool calling gets its own
pre-written entry point in week 4. If that shape had to change, every student's
week 1 function would be rewritten and the carry-forward promise would break.

**A24. The week 7 summary comes from the model.** The model returns the
two-sentence plain-language summary as one key in its answer, so the export
function places it rather than writing it. If it does not, that function has to
compose the summary and the student cell grows past its line budget.

**A25. A few student cells run to 16 or 17 lines.** The prompt's target is 5 to
15 written lines, and two weeks sit above it in the one-line-per-condition style
week 0 teaches. Cutting to 15 means handing students one of the checks, and in
week 6 that check carries the only evidence for CLO4.

**A26. Week 6 runs its comparison cheaply.** The unguarded comparison makes one
call per email, while the guarded path runs the full loop. If both ran the full
loop, the week's token cost would roughly double.

## A.4 Tokens, models and time

**A27. Reasoning off. This is now measured rather than assumed.** Every token,
cost and wall-time figure in this blueprint has the model's reasoning mode
switched off. The week 5 sweep settled it. In its default reasoning mode the
model spent a whole 512-token answer budget thinking and returned nothing in 18
runs out of 18. Raised to 4,096 tokens it works and still costs 83 seconds and
about 7,900 tokens for one email, against 4.1 seconds and 3,813 tokens with
reasoning off. See `builder/docs/week5-model-test.md`.

**A28. The guard numbers are placeholders, and the cap counts what the model
writes.** The confidence floor of 0.7 and the per-run cap of 4,000 tokens are
provisional, and the cap counts completion tokens rather than the tokens sent.
A cap on tokens sent would fire on nearly every email and turn a teaching
control into a broken lab.

**A29. Token totals rest on a clean run.** Weekly call counts assume the retry
usually succeeds first time and that the model asks for tools in the expected
order. Students who rerun cells while debugging spend more, and the running
counter in every notebook shows them their own total.

**A30. Sizes for unwritten material are estimates.** Body lengths for the 44
emails not yet written use the measured mean of the twelve on disk, and four
prompt parts are estimated because nobody has written them. Every other input to
the token arithmetic was measured from a file on disk.

**A31. The tool block costs more than its characters suggest.** The model's chat
template wraps every tool definition, so a character count understates it. Week
4 therefore uses about 24,000 prompt tokens as its working figure rather than
the raw floor of 21,600.

**A32. No per-token price exists.** The advisory figure of about $5 per student
is reported as a break-even price per million tokens, because no price is known.
If a price arrives, the footnote is recomputed and no lab design changes.

## A.5 Readings, citations and writing

**A33. One reading rate for the course.** Reading time is priced at 200 words a
minute for one pass, and study work is priced as named lines beside it. Three
week specs still name other rates and need one edit each.

**A34. Word counts are planning targets.** No reading is written yet, and the
week 1 reading is planned at 1,350 words. That is above the 900 to 1,050 target
and under the 1,400 ceiling, because week 1 carries two breadth topics.

**A35. The week 1 post is set at 150 words.** This blueprint sets the week 1
discussion post at about 150 words, where the week 1 spec says 200. One of the
two has to change before Phase 2.

**A36. Two-stage discussion deadlines, one graded date.** Discussions ask for a
first post by Thursday and a reply by Sunday 11:59 PM Central, and only Sunday
is graded. The template fixes everything at Sunday, so a graded two-stage
deadline would be a deviation to approve.

**A37. Citations are targets, not verified sources.** Every planned citation is
named but not yet licence-checked or confirmed to resolve, and two practices in
the readings are called common practice rather than tied to a source. Expert
review supplies replacements and reports any claim it cannot ground, as the
prompt requires.

**A38. Nothing real appears in course content.** Every example is set at the
fictional organization from the approved corpus, and no real company, product,
person, resolving domain or address appears. Student pages name the two
candidate models by role rather than by vendor, and product names appear only
where they identify a template element or a college system.

## A.6 The final exam

**A39. Thirty items, one sitting, opening in week 8.** The exam is one quiz of
30 multiple-choice items at one point each, and it opens at the start of week 8
rather than on day one. Week 8 carries no other work, so a late open strands
nobody, but it is a narrow exception to the no-lock rule.

**A40. Presentation blocks are not questions.** Six items share one header block
shown once as a presentation-only item, so every scored item is still multiple
choice. If that rule is read more strictly, the header is repeated in six stems.

**A41. The exam quotes only its own eleven emails.** Scenario items quote the
eleven emails reserved for the exam, never one students have already seen. If
the corpus cut of the last three exam emails is taken, four items go, and two of
them are the only items testing a partial authentication failure.

**A42. The answer key appears at submission.** Correct answers and per-answer
feedback appear as soon as a student submits. In a last-week course, a delayed
key is usually read after the term ends or never.

## A.7 The alignment matrix and the coverage memo

**A43. The framework citation.** The matrix cites NICE Framework Components
version 2.2.0, retrieved 2026-09-03, using the change log's 2026 date rather
than a typo in the NIST heading. All 21 ids were confirmed to exist in that
version and to sit in the target work role, so if the heading's year is right
after all, only the version note changes and no mapping moves.

**A44. The memo splits one suggested outcome into four.** One of the program
manager's eight is reported as four separate things, because the course teaches
them at four different depths. Reporting them on one line would have overstated
coverage.

**A45. Safe prompting is read as defensive prompt construction.** The memo reads
that phrase as the schema checks, the delimiting and the fact validation taught
in weeks 2 and 6. No criterion scores a student's own prompt wording, so the
memo reports it as assessed indirectly.

**A46. The memo predates the exam blueprint.** Its claims about final exam
coverage came from the build prompt, because the exam blueprint did not exist
when the memo was written. Those lines now need one check against the blueprint.

---

# Group B. Gaps that need a decision from the program manager

**B1. Reading time against reading length.** The prompt's 40 to 50 minute
reading band and the writing standard's 1,400-word page ceiling cannot both be
met at an honest pace. Which rule wins, and should the 1,350-word week 1 reading
split into two pages?

**B2. One exported file in week 7.** Week 7 carries the primary evidence for two
objectives but exports one file, with the triage notes and the scores as two
headed sections. Is one file acceptable, or does week 7 get an exception to the
one-artifact rule?

**B3. Where the week 7 answer key lives.** The batch answer key ships on the
week 7 page, which follows from the rule that nothing locks, and no part of the
rubric rewards a correct verdict. If the key should stay with the instructor,
the pre-written comparison table is replaced by one the instructor runs after
submission.

**B4. A pre-written schema checker.** Students wire in a pre-written function
that checks the model's answer against the schema, rather than writing that
check themselves. A mechanical schema walk does not fit the 5 to 15 line budget,
so this trade needs accepting or rejecting.

**B5. Live or replayed runaway demonstration.** Week 5 shows what an uncapped
loop does, currently as a live run that spends real tokens to show a mistake. A
saved transcript is cheaper and less convincing.

**B6. Mastery threshold and calculation method.** The plan reports the most
recent score and sets mastery at 3 of 4. Both need confirming before Phase 2,
because each is one field on every Outcome.

**B7. A weak supporting id on CLO6.** One supporting task on CLO6 is about daily
reports, and the week 7 report is one-time. The prompt forbids substituting a
different id, so the choice is to keep it with the note or drop it from the
supporting list.

**B8. Three added Orientation items.** The build adds a Course Syllabus page, a
syllabus acknowledgment practice quiz, and a notebook and API key help page to
the Orientation module. All three sit outside the template's fixed contents and
need approval.

**B9. Zoom office hours.** The template's minimal skills list requires students
to use Zoom for office hours. If the instructor holds none, that line and the
pointer to the Zoom page stay out.

**B10. Depth on the fourth breadth topic.** The wider AI risk set is carried by
one self-check item and part of one discussion question, the thinnest coverage
of the four topics outside the exam. Raise the week 6 self-check from eight
items to ten, or leave the topic mostly to the exam?

**B11. A fifth week 1 source.** A public attack-technique id for phishing was
considered and cut, to hold week 1 to the four citations its spec names. Add it
or leave it out?

**B12. Exam difficulty curve.** The 30 items run eight easy, thirteen medium and
nine hard, leaning to the middle because the exam is open book. Is that right
for this cohort, or should it be gentler?

**B13. Item-level exam data.** The exam reports one score and no objective data
by design. If the program wants breadth data item by item, Canvas item analysis
supplies it, and someone has to own pulling and reading it each term.

**B14. Who sees week 0 self-assessment results.** Canvas records the attempt
either way, and that data would support early outreach and the attrition
tracking the risk register promises. It could also feel like surveillance, and
the scoring text currently promises the score is private.

**B15. Where the error card lives.** The "if something breaks" card should be
one page linked from all seven weekly modules, and the template's weekly module
has no slot for a standing reference link. That placement needs deciding.

**B16. Responsible use has no assessed home.** Nothing in the course scores
responsible use on its own, which the coverage memo reports plainly. Should that
also go in the risk register, or is acknowledging it enough?

**B17. Three small confirmations on the memo.** Relevance is reported as a
qualifier rather than a gap, and the course produces one triage note format
rather than tickets and reports. Confirm both readings, and confirm the file
format the memo should ship in.

---

# Group C. Gaps that need a decision or an action from the college

The first two items are the ones the build prompt itself puts outside its scope.

**C1. Late work and resubmission.** Nothing is set, while the template says late
work is not accepted and that activities lock after the deadline. The policy has
to cover four cases here: a late lab, a regraded resubmission that would replace
an earlier Outcome result, an exam retake after a technical failure, and the
token top-up the prompt already exempts from penalty.

**C2. Account-level Outcomes, checked and answered.** This was checked on
2026-09-03 against the target instance, which holds no Outcomes at any level, so
all six are created at course level. If a district account elsewhere holds
matching Outcomes, or the program wants these shared across courses, a district
Canvas administrator has to create them at account level and the course relinks
to them.

**C3. The critical-thinking Outcomes and their rubric.** The template ships five
critical-thinking Outcomes on a zero-point rubric, and none matches a course
objective. Does the college collect that data from every course, and if so,
which item carries the rubric, given that Canvas allows one rubric per
assignment?

**C4. Identity verification and the locked browser.** The template requires a
biometric identity check and a locked testing browser, and this build leaves out
both. The exam is open book and unproctored by the prompt, and some students
cannot install software on the machine they use.

**C5. AI use and AI detection.** May a course authorize AI use with disclosure
under the district procedure the template cites? And will AI detection software
run on a course that requires students to use AI?

**C6. The syllabus of record.** Is the external syllabus system the record of
truth? If so, does the Canvas syllabus page repeat it or replace it?

**C7. Orientation gating.** The template's home page says students must finish
the Orientation module before reaching the next one, and the template's own
export implements no such lock. The prompt says nothing locks, so the college
has to say which is true.

**C8. The online learning orientation.** Is the free orientation mini-course
still required this term? And does the instructor still check its 80 percent
post-test result in week 1?

**C9. The production Canvas instance.** Does it have the page-styling add-on
installed, and which institution tools sit in its course menu? Both change the
markup and the navigation of every page this build writes.

**C10. What verbatim means.** When an institution page is kept verbatim, is that
the words or the HTML? Fixing the template's accessibility defects changes the
HTML, and the zero-error target cannot be met otherwise.

**C11. Build method.** Is the course built through the Canvas API from scratch,
which is the current plan, or by importing the template cartridge and editing
it? An import carries nine unrelated question banks and nine unrelated rubrics
that then have to be removed.

**C12. Ownership and licence.** Who owns this course, and under what licence
does it ship? The build leaves the licence at the Canvas default rather than
copying the template's.

**C13. The bookstore statement.** The template requires a statement that
students need not buy from the college bookstore. Is it required on a course
that assigns no textbook?

**C14. Term dates.** What are the start and end dates of the 8-week session, and
what is the last day the term accepts a grade? Module titles, every due date and
the exam window all wait on the answer.

**C15. Notebook availability.** Is the hosted notebook server available to
students on day one, since week 0 must be open then? And do students get course
access before the term opens, which would make four to six hours of front-loaded
work far easier?

**C16. Key injection and the serving stack.** Can the hosting inject one API key
per student as an environment variable, and which serving stack and version does
it run? The notebooks' parsing is written against one stack's answer shape.

**C17. Names in the corpus.** The twelve employee names, the vendor contacts and
the applicant are invented combinations, and none was checked on its own. Should
the college run them through whatever check it uses, and does any match a person
at the college?

**C18. Distribution channel.** Do the corpus files reach students through Canvas
Files, the notebook data folder, or both? The download test is written for both,
and the fallback is the notebook folder alone.

**C19. Token price and budget owner.** Is there a per-token price for the hosted
models, and who owns the central token budget? The prompt sets the top-up
policy, but not the price and not the person.

---

# Group D. Gaps that need a measurement, and what blocks each one

**D1. Closed on 2026-09-04.** The sweep of 294 agent loops finished and the
report is `builder/docs/week5-model-test.md`. It recommends Granite 4.2 3B with
reasoning off, in the design where the student's code owns the stop condition,
which is the design this blueprint already describes. Granite 4.1 3B is the
documented fallback, with the caveat that it varies the tool order while still
ending every run for the right reason. What remains open is the per-run token
cap value, which week 6 sets and which no measurement has yet exercised.

**D2. Closed on 2026-09-04.** The manifest, that email's ground truth record and
the week 5 spec now all read `tools_exhausted`. Every one of the 294 runs
confirmed it: three tools exist under a cap of four, so an agent runs out of
tools before it reaches the cap.

**D3. The other 44 emails and the batch answer key.** Twelve of the 56 emails
exist, the week 7 answer key does not, and every token estimate is refreshed
once they are written. Blocker: before generation the manifest needs the
injection text its schema requires, several path hints that use bare host names
need fixing, and the checker needs a dated snapshot of the public list of
top-level domains.

**D4. The names table for week 3.** Week 3's display-name check needs a table of
names to organizations, built from the recipient records plus a vendor list.
Blocker: that file does not exist, and without it week 3 loses a fact the build
prompt names.

**D5. Citation checks.** Every planned citation has to be confirmed to resolve
and to be openly licensed or free vendor documentation. Blocker: no reading is
drafted yet, so the check runs with expert review as each one is authored.

**D6. Two Canvas behaviors.** What a linked criterion posts when its points are
scaled, and whether the delayed answer key setting works on this instance, are
both unverified. Blocker: neither was exercised in the 2026-09-03 probe, and
each is one API call during the Phase 2 build.

**D7. The weekly time budget.** The prompt requires the budget to be checked
against the real week 1 and week 2 builds, the reading rate included. Blocker:
Phase 2 is not built.

**D8. The production endpoint probe.** The probe that documented how the models
answer has to be rerun against the hosted environment before the Phase 2
notebooks are final. Blocker: no access to that environment, though the saved
scripts and logs make it a ten-minute job once there is.

**D9. The endpoint download test.** Saving an email file on a college-managed
device may trip its endpoint protection, which the Canvas half of the test could
not show. Blocker: the college has not supplied a managed laptop of each type it
issues, a managed browser-only device, or a sandbox Canvas course.

**D10. Week 0 timing and attrition.** The four to six hour figure for week 0 is
planned, not measured, and the risk register promises to track attrition among
students who skip it. Blocker: no student data exists until the first offering,
and the attrition measure also waits on item B14.
