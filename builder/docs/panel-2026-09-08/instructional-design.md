# ITSY 1377, instructional design review

**Reviewer:** instructional designer, panel of 2026-09-08
**Subject:** the course as it stands in `builder/`, read against the student
e2e run of 2026-09-07/08
**Scope:** design, not defects. Where I repeat a defect the student or the run
report already found, it is because the *reason* it matters is different from
the reason given.

**Nothing in the course was modified.**

---

## 0. What I checked, and how to read the marks

Every claim below is marked one of three ways.

- **Verified** — I opened the file and read the line. File, cell number and
  wording are given. Cell numbers are 0-based from the `.ipynb`, which is what
  a script sees; the Canvas pages count from 1, so subtract one from a page
  reference to get mine.
- **Verified by count** — I ran a script over the source and am reporting what
  it found.
- **Asserted** — professional judgment from teaching this population. No file
  proves it. I mark these because the run report is careful about the same
  distinction and the courtesy should be returned.

I read: `content/course.yaml`, all seven rubrics, all nine discussions, all
nine quizzes plus the seven exam part files, the week 0 / week 1 / schedule
overview pages, `docs/phase1-blueprint/alignment-matrix.md`, all seven sidebar
notebooks, `week00-python-on-ramp.ipynb` in full, and the TODO and export cells
of all seven labs. I read the run report in full and the student's `REPORT.md`;
`FINDINGS.md` I read in the sections named below.

---

## 1. Where I disagree with your severity ordering

You ranked: **1.1** week 6's broken demonstration, **1.2** the four missing
export fields, **1.3** week 7's schema, **1.4** the answer-position defect,
**1.5** week 1's TODO wording, **1.6** week 3's email identity.

I would rank: **1.4, 1.5, 1.1, 1.6, 1.2, 1.3** — and I would put a defect
neither you nor the student ranked above all six of them. Reasons, worst
disagreement first.

### 1.1 The answer-position defect is the most serious thing in the list, and it is not close

You rank it fourth and you name the right harm ("these quizzes are the course's
**routing mechanism**") and then price it as if it were a lesser harm than a
broken demonstration. It is not. It is the difference between having a
formative instrument and not having one.

**Verified by count.** Across `w1-` through `w7-self-check.yaml`, 43 scored
items, the correct answer is at index 0 in 43 of 43. `shuffle` is `false` in
every one. `week0-self-assessment.yaml` distributes 3/6/1 across the first
three positions; `final-exam.yaml` distributes 18/8/8/6 and sets
`shuffle_answers: true`.

Here is why it outranks everything else. **This course has exactly one
mechanism that tells a student, before the grade lands, that they have not
understood something.** It is not the lab: every lab check cell is designed to
pass, and the export cell writes a file even when the student's function is
missing — that is deliberate and it is right, but it means the lab tells nobody
they are lost. It is not the discussion: it is graded a week later. It is not
the rubric: same. It is the weekly self-check, and the design knows it. From
`w4-self-check.yaml`, the description a student reads before and after every
attempt:

> Every answer, right or wrong, names the section or the notebook cell to
> reopen. Use those names. Missing one twice is a sign to go back and read, not
> a sign to guess again.

And `week-0-overview.md` sets the routing rule in the same voice: "6, 7 or 8
right: work the sections your missed questions name."

That instrument is void seven times. A student who never opens a reading scores
84 of 84 and is told, seven weeks running, that they are ready. **Asserted:**
in a community-college cohort the students who exploit an obvious pattern are
disproportionately the students the routing exists to catch — the ones who are
behind, short of time, and looking for the cheapest path to the points. The
defect is not merely inert; it is selectively harmful to the population the
mechanism was built for.

And the harm is invisible upward as well as downward. The instructor's
gradebook will show 12/12 across seven weeks for the whole section and will
conclude the readings are landing. That is eight weeks of diagnostic blindness
for a cohort, every term, until someone reads the YAML.

Against that, week 6's broken demonstration damages one week's lesson, is
already hedged in the week's own walkthrough video, and is graded by a rubric
criterion that scores the *judgment*, not the direction of the result. It is
serious. It is not this.

**One correction to your fix.** You propose `shuffle_answers: true`. That
collides with a stated design decision. `w4-self-check.yaml` comment: `#
shuffle false. The options are read in order, so they stay in order.` And the
student-facing description: "The options stay in the same order on every try,
so you can compare a second attempt to your first." That affordance is real and
worth keeping — it is what makes the "missing one twice" instruction meaningful.
The correct fix is **to move the correct answer off index 0 in the 43 items**,
keeping `shuffle: false`. Cost: about an hour of careful reordering, plus a
re-read of the four feedback strings per item to be sure none of them says
"the first option". Risk: none to content; the questions are untouched. Add a
build gate asserting no quiz has more than ~40% of its keys at one index.

### 1.2 Week 1's TODO 1 belongs second, for the reason you name and then discount

You rank it fifth and lead with the lost `reasoning_effort`. The student ranks
it second and gets the reason right (`REPORT.md` §2, problem 2):

> It is the first function a student ever writes, and it teaches them that "all
> the checks passed" means "I did it right." That habit does more damage over
> seven weeks than any single lab.

**Verified.** `w1-lab.ipynb` cell 5, job 1 ends "`messages` is a list holding
one dictionary, and that dictionary has a `role` of `"user"` and a `content`."
Job 2 reads "Merge `MODEL_EXTRAS` into that dictionary." The nearest antecedent
is the message. Cell 10 goes to four lines of trouble to catch the *other*
silent failure in the same function (`inspect.signature` for `temperature`) and
does not check this one.

The instructional weight is this: the entire course is an argument that you
cannot trust an answer you did not check. Week 2's headline is "Loading isn't
checking." Week 6 exists to teach that a control that looks like it fired may
not have. Week 7 grades honest measurement. **The first graded function in the
course silently rewards the exact belief the other six weeks exist to destroy**,
and it does so in the students' first hour of graded work, which is where a
course sets its epistemic norms. That is a curriculum-level harm from a
two-word wording bug.

### 1.3 Week 7's schema is not "graded work a student cannot earn"

You place it in §1.3 and again in §3. **Verified:** `schema_errors()` has no
`sentences` branch and would reject a correct `OUTPUT_SCHEMA_V2` answer; it is
never called on V2. The bug is real.

The grading consequence is not. `w7-lab.yaml`'s own header states the grading
model: *"NOTHING HERE NEEDS THE STUDENT'S NOTEBOOK. Every level is decided from
the screenshot, the exported file and the written answer."* The 36-point
criterion reads "Every recommended action fits the verdict on the line above
it. Every summary is plain enough for the person who reported the email, and
names no header field and no tool." **A human grader with that rubric and
twenty notes in front of them can score it in ten minutes.** The points are
fully earnable. What is missing is *formative* feedback before submission —
the student cannot self-check. That is a real but ordinary gap, and it belongs
well down the list, not in a section headed "Nobody can earn these."

The same overstatement affects week 6's 72-point band. "Supports it with the
student's own before and after numbers, both of which the attached file shows"
is satisfied by counts derived from the file — 5 of 11 rows changed, 1 of 11
escalated — which is precisely what the student did. The criterion is
*hostile*, not impossible. What actually makes it unfair is the week 6
self-check question 4, which shows the student an excerpt headed "Your export
file holds this for email 012" carrying field names (`confidence:`, a bare
`verdict:`) that do not exist in the file. The course actively points the
student at the answer the rubric punishes. Fix the self-check excerpt and add
the two confidence fields, and the criterion is fine.

### 1.4 One correction inside 1.1, which changes the fix

Your finding is right. Your mechanism is not, and the difference matters.

You write: "**There is no `body_text` on any of those lines.**" **Verified,
and it is only true of the closing call.** `run_triage()` calls
`run_loop(parsed, prompt_text, ...)`, which calls `start_messages(parsed,
prompt_text)`, and `start_messages` builds its user turn as

    prompt_text + playbook + "\n\nThe reported email:\n\n" + parsed["body_text"]
    + tool_inputs + TOOL_TURN

So the **loop turns of the undefended run do carry the injected paragraph.**
The course knows this and says so: `fenced_email()`'s own docstring in
`w6-lab.ipynb` cell 8 reads *"Your run_loop() hands the email to
start_messages(), which pastes the body into every turn of the run."*

The asymmetry is narrower and sharper than you state: **the call that produces
the verdict** — `answer = extract_json(ask_model(closing))` in cell 5 — is a
fresh single-turn call built from `prompt_text + tool results + schema`, and for
the undefended path `prompt_text` is `loop_prompt(parsed)`, which has no body.
For the guarded path it is `build_guarded_prompt(...)`, which has the fenced
body. So the verdict-producing call sees the payload on the guarded side and
never on the undefended side.

This explains the run's null result exactly. Undefended 013 and undefended 024
produce near-identical closing prompts — the payload is not in either — so a
0-for-10 result is the only possible outcome, deterministically. It also means
your proposed fix ("put the body in the undefended prompt") is right in
direction but should be aimed at `run_triage()`'s `closing`, not at
`loop_prompt()`. Putting it in `loop_prompt()` would double the body in every
loop turn and cost tokens for nothing — which the notebook's own comment above
`LOOP_INSTRUCTIONS` already warns against.

**Asserted, and worth a paragraph in the fix:** the cleanest repair is to make
the closing call a continuation of the message list rather than a new prompt.
That makes the two columns differ by the fence and by the rules, which is the
week's claim, and it removes the last place in the course where the same agent
is really two agents.

---

## 2. The defect I would rank above all six

### 2.1 The scaffolding never fades, so the labs assess transcription, and CLO3 is measured below its own Bloom level

This is the thing the student could feel and could not name, and the thing an
instructional designer is for.

**Verified.** The TODO cells specify their answers at line granularity, and the
granularity does not change from week 1 to week 6. Week 4 cell 9, TODO 1, step
2:

> When name is "check_sender_reputation", return the answer of
> `check_sender_reputation(values.get("sender", parsed["from_address"]))`.

That is the finished line with `if` and `return` removed. Week 5 cell 11, TODO
1, steps 3 and 4 print four lines verbatim:

>     answer, finish, turn, calls = ask_with_tools(messages)
>     tool_call = first_call(calls, answer, trace)
>     result = run_tool(tool_call["name"], tool_call["arguments"], parsed)
>     append_turn(messages, turn, tool_call, result, trace)

and step 2 says "join them with and", and the note under step 5 says "one if
with two tests joined by or". The student's count (`FINDINGS.md` L4105–4119):
"Of the fourteen lines in my `run_loop()`, **six are printed in the TODO cell's
comment, character for character**... **I made one decision this week.**"

Week 6 cell 13, TODO 2 prints the expression to use
(`"blocklisted" in facts["url_status"].values()`). Week 7 is the exception and
the student says so plainly (`FINDINGS.md` L6093–6100): "**Week 7 hands me
none.**"

**Why this is a design defect and not just generosity.** Heavy worked-example
support is *correct* for this audience — Sweller's worked-example effect is
strongest exactly for novices with no schema, and a course for students with no
programming background that threw them at a blank cell would fail them. The
error is not the support. It is that the support **never fades**. Renkl and
Atkinson's fading sequence — worked example, then completion problem, then
problem — is the whole mechanism by which worked examples produce transferable
skill rather than a copied artifact. Week 0 executes that sequence *perfectly*
inside every one of its ten sections: example cell, "What each line does",
"Try changing this", "You try.", "The answer." (**verified**, e.g. cells 79–84
and 87–94). **The labs never execute it across weeks.** Week 7's TODO 2 still
says "Steps 3, 4 and 5 are one if, one elif and one else." Week 1's TODO 1 says
"The `.update()` method does it in one line." Same altitude, six weeks apart.

**The alignment consequence is concrete and it is the one an accreditor would
find.** CLO3 is written at Bloom **Create**: "Build an AI agent that selects and
runs triage tools in a bounded loop to reach a verdict." `alignment-matrix.md`
§3 labels it Create. Its primary evidence is `w5-lab.yaml` criterion 2, and
that criterion in full reads:

> The file holds six runs. Each shows an ordered tool list, a step count of
> four or fewer, and one of the five stop reasons.

That is a check on the contents of a file written by a pre-written export cell.
It is satisfied by transcribing six lines out of the TODO comment. **The
objective claims Create; the taught task is Apply; the assessed evidence is at
recall-and-transcribe.** Nothing in week 4 or week 5 requires the student to
decide anything about the loop, which is the object of the objective. This is
the single largest alignment gap in the course, it sits on the objective the
course is named after, and it is worth 40 of 100 points in the week the matrix
calls primary.

**What I recommend, with its cost and its risk.**

*Fade the last three labs.* Weeks 1–3 keep their present granularity. Week 5's
TODO 1 loses the four verbatim lines and keeps the six English sentences. Week
6's TODO 2 loses the printed expression. Week 7 is already right and is the
model. The removed lines move into a **separate, clearly-labelled "If you are
stuck" cell immediately below each TODO**, which the student chooses to open —
so the support still exists and the student's decision to take it is visible to
them.

*Cost.* Rewriting three TODO comment blocks and adding three hint cells: half a
day. Re-recording nothing; the walkthrough videos show the check-cell output,
not the TODO text. Re-measuring nothing.

*Risk, and why it is acceptable here.* Fading raises the failure rate on the
week it is applied to. In most courses that is a serious risk. In this one it is
already mitigated by the best structural decision in the whole build: every
week N+1 notebook ships a working reference version of everything through week
N, and the course says so in plain words on the front of every lab —
`w1-lab.ipynb` cell 0: *"So a hard week costs you that week's points. It does
not end the course."* That safety net is exactly what makes fading safe here,
and it is currently paying for nothing. The residual risk is that a student who
takes the hint cell every week learns no more than today; that is a real
outcome, but it is a *visible* one, which today's design is not.

*If you do only one thing:* fade week 5 alone. It is the CLO3 primary, it is
where the alignment gap is measurable, and it is one cell.

---

## 3. Alignment: objective, taught, practised, assessed

**Verified** against `course.yaml`, `alignment-matrix.md` §3, the seven
rubrics, and the TODO/export cells.

| CLO | Bloom claimed | Taught in | What the student actually *does* | Assessed by | Verdict |
|---|---|---|---|---|---|
| CLO1 Extract facts | Apply | w3 reading + w3 lab | Copies 12 named keys out of a parsed dict, per a 6-step recipe naming every key | w3 rubric crit. 2, 25 pts | **Aligned.** Apply taught, Apply assessed. The recipe is heavy but Apply tolerates it. |
| CLO2 Classify and validate | Analyze | w1 (supporting), w2 (primary), w6 | Writes `extract_json` (5 lines) and `classify_email` (8–10 lines from a 6-step recipe) | w2 rubric crit. 2, 50 pts | **Mostly aligned.** The 50-pt criterion is about the retry log, which is genuinely diagnostic. Weakened by §5.1 below. |
| CLO3 Build a bounded agent | **Create** | w4 (supporting), w5 (primary) | Transcribes 6 of 14 lines; makes one decision (`return` vs `break`) | w5 rubric crit. 2, 40 pts — *contents of a file* | **Misaligned by two Bloom levels.** §2.1. |
| CLO4 Judge guardrails | Evaluate | w6 | Writes two small functions; then writes a **judgment** with evidence | w6 rubric crit. 2, 72 pts | **Aligned, and well done.** The criterion is genuinely evaluative. Its evidence base is broken (§1.4) but its design is right. |
| CLO5 Document a decision | Apply | w7 | Writes the note function unaided; produces 20 notes | w7 rubric crit. 2, 36 pts | **Aligned.** Best-matched pair in the course. |
| CLO6 Measure accuracy | Evaluate | w7 | Writes `score_batch` unaided; then must name where a human must still review, cite own accuracy, name own wrong email | w7 rubric crit. 3, 56 pts | **Aligned, and the best criterion in the course.** It cannot be answered without the run. |

Three structural observations the run did not raise.

**(a) Three of six objectives rest on a single submission, and two of those are
in the last graded week.** CLO3's only primary evidence is week 5; CLO5 and
CLO6's only evidence is week 7. `calculation_method` is `latest`
(`course.yaml`, and `alignment-matrix.md` §9 defends the choice well). The
course also says, correctly and humanely, that almost nothing locks and a bad
week costs only that week. Put those together: **a student who submits week 7
late or not at all reports "No evidence" on two of six program outcomes with no
recovery path anywhere in the course.** In an 8-week build-forward course the
last graded week is the likeliest one to be missed. **Asserted:** in a section
of 25, expect two to four such records per term, and the program report will
read them as unmastered rather than unattempted. The cheapest mitigation is to
let the week 6 written judgment post a supporting CLO5 result (it already
documents a decision), or to add a CLO6-supporting criterion to week 5's "Cost
of an uncapped run", which is already a measurement. Cost: one `outcome:` line
per rubric plus a note in the matrix. Risk: Canvas permits one criterion per
Outcome per rubric, which the file already documents; these are different
rubrics, so the constraint is not touched.

**(b) The exam's `taught_in` audit field is excellent practice and has at least
one false entry.** **Verified.** Every exam item in `content/quizzes/exam-parts/`
carries `assesses`, `level`, and `taught_in`. That is stronger alignment
documentation than most accredited programs produce. Item 19
(`exam-19-dkim-temperror`, `CLO1.yaml`) carries `taught_in: "Week 3 reading,
what a passed check really means, where email 004 shows three passes and email
006 shows fail and none."` **That section teaches pass, fail and none. It does
not contain the word `temperror`** (verified by grep across `content/` — the
only occurrences outside the exam are in `w7-content.md:41`, where `softfail`
appears as an example of jargon *not* to write to a user).

Your fix — "teach it or drop the item" — is one option. There is a better one.
The item is answerable by reasoning from what *is* taught: the reading's own
line is "Both results are facts, and neither is a verdict" and "Missing isn't
failed," and all three distractors name states the reading covers. It is a
legitimate **transfer** item. What is wrong is that it is labelled `level:
Recognition`, and recognition presumes prior exposure. Relabel it `Analysis`
and correct the `taught_in` to say what it actually rests on. Cost: two lines.
Risk: none. The same treatment fits the `softfail` half of item 26.

**(c) The exam correctly carries no CLO3, CLO5 or CLO6 items and says why.**
`alignment-matrix.md` §6: "Selected response can show that a student recognizes
a correct read. It cannot show that a student built, judged, or documented
anything." That is exactly right and it is rarer than it should be. Protect it.

---

## 4. Cognitive load, week 0 and week 1 — where this cohort drops

Three findings, in order of how many students they cost.

### 4.1 Week 0 is optional, routed by an invalid instrument, and lands on top of week 1

**Verified.** `week-0-overview.md`: "Optional, ungraded, strongly recommended",
"Time | 4 to 6 hours, on top of the seven course weeks", "Due date | None."
`course-schedule.md`: "Week 0 asks for 4 to 6 hours on top of that. **Most of it
lands before week 1 is due**, so plan for it early." `w1-overview.md` prices
week 1 at 272 minutes.

So for the student this course is written for — no programming background — the
real week-1 load is **272 minutes plus up to 360 minutes, about 10.5 hours**,
against roughly 5 hours in every week that follows. **Asserted, and I would
stake a lot on it:** that is the drop week. Community-college attrition in
8-week online technical courses concentrates in the first fourteen days, and it
concentrates on load shape rather than load total. A course that front-loads
double its steady-state hours onto the unfamiliar week, and marks that work
*optional and ungraded*, has told the student under time pressure exactly which
item to cut. It is also the one item they cannot afford to cut.

**And the routing instrument cannot do its job.** `week-0-overview.md` step 2:
"9 or 10 right: skip week 0 and start week 1." The student's analysis
(`FINDINGS.md` L290–319) is correct and I confirmed the shape of it: the
self-assessment tests recall of syntax that nobody in the target audience has
been shown — `FINDINGS.md` L302–319 notes that the word `def` appears nowhere in
the orientation pages or the Glossary, and that seven of ten items are
answerable from the Glossary alone. A placement test that a prepared reader can
pass from a glossary, given to students who by definition have no prior
exposure, does not measure readiness in either direction. It will pass some
students who should be routed in and it will send others through five hours they
did not need.

**Recommendation.** Do not make week 0 mandatory — that changes the course's
credit shape and its promise. Do three cheaper things. (i) Give week 0 its own
calendar space by moving week 1's lab due date to day 10 in the first term
offering, or by publishing a two-week "week 1" and compressing later. (ii)
Replace the ten recall items with five *code-reading* items — show four lines,
ask what prints — which measure the only skill week 0 actually needs a student
to have, and which a true novice can genuinely fail. (iii) Change the "9 or 10:
skip" advice to "9 or 10: skim sections 8, 9 and 10 and skip the rest," because
those three are where every later lab's gaps live (§4.3). Cost: rewriting one
10-item quiz and one date. Risk: (i) is a registrar/term-shape conversation, not
a content one; (ii) makes the quiz harder and some students will read that as
the course being harder — mitigate with the existing ungraded, unlimited-attempt
framing, which is already good.

### 4.2 The orientation asks for actions it has not yet taught, in the first hour

**Verified.** `using-the-notebook-server.md` line 32 tells the student to run
`budget_left()`, line 37 to run the last cell, line 46 to run
`restore_my_work(...)`. The student's note (`FINDINGS.md` L120–124): "Both are
given as things to run, in an orientation page, with parentheses and quotation
marks that mean something. Nobody has told me yet what a function is or why the
quotes are there. The Glossary's 'Call' and 'Function' entries are marked
first-used in week 0 — i.e. after this page asks me to do it."

Your §5 catches the harder half of this (the three helpers are defined only in
the seven lab notebooks, so the instruction is false for eight of fifteen). The
softer half is the design point: **the orientation module is sequenced before
the only module that teaches the vocabulary the orientation uses.** Two more
instances, both verified: `welcome-start-here.md` line 33 says "Take the week 0
self-assessment" first, while line 51 says "Work down this module in order" and
the self-assessment lives two modules later; and the syllabus acknowledgment
quiz sits at item 6 of the Orientation module while "Using AI in this course" is
item 8, so the student attests to a policy they have not been shown.

**Asserted:** none of these three loses a student on its own. Together they set
the tone in the first sitting that the course's own instructions do not
reliably work, which is the belief that makes a student stop reading
instructions — and this course depends more than most on students reading
instructions carefully.

**Also verified, and it should be fixed today because of where it sits:**
`welcome-start-here.md` line 43, under the heading about a week that went badly,
reads in full: "**Submit what you've.**" A truncated sentence, in the paragraph
an at-risk student reads at the worst moment of their term.

### 4.3 Week 0's promise is broken in exactly the weeks that matter, and the breaks are one line each

**Verified by count.** I searched every code cell of `week00-python-on-ramp.ipynb`
for the constructs the labs require:

| Construct | Occurrences in week 0 | First required |
|---|---|---|
| `or` inside an `if`/`while` | **0** | w5 TODO 1, step 5 |
| bare truthiness (`if x:` / `while x:`) | **0** | w5 TODO 1, step 2 (`tools_left(trace)`) |
| `if not x:` | **0** | w2 TODO 2, step 6 |
| tuple unpacking (`a, b, c = f()`) | **0** | w5 TODO 1, step 3 |
| `break` | **0** | w2 TODO 2 (early exit), w5 sidebar |

`week-0-overview.md` states: "Every line you write in a lab uses only what is in
the notebook." **That promise fails, and it fails hardest in week 5** — the
CLO3 week — where all four of the missing constructs sit inside the two lines
the lab asks the student to write (`FINDINGS.md` L4186–4189: "This is the first
week where everything the course failed to teach me is concentrated in the two
lines it asked me to write").

**This is the load finding that matters most for design**, because it interacts
with §2.1. The reason the TODO cells hand over the lines is, I think, that the
author knew the constructs were untaught and compensated by dictating them.
That is the wrong compensation: it removes the difficulty instead of removing
the gap. **Add one part to week 0 section 7 covering `or`, bare truthiness and
`if not x:`, and one part to section 6 or 8 covering tuple unpacking**, and the
justification for dictating week 5's lines disappears. The two fixes are the
same fix.

Cost: two new week-0 sections in the existing five-cell pattern (example, "what
each line does", "Try changing this", "You try.", "The answer."), about half a
day, plus one line in the `week-0-overview.md` section count and one in the
wrap-up table. Risk: week 0 grows from 10 to 12 sections and from 4–6 hours to
perhaps 5–7, which worsens §4.1. Mitigate by folding them into existing sections
7 and 8 rather than adding sections, which is where they belong anyway.

---

## 5. Does the sidebar/lab split work as scaffolding?

Verdict: **the split is the right instructional structure and it is executed
well in four weeks of seven.** The design is a near-transfer isolated-practice
notebook on a non-security surface (a stockroom, a rooftop weather station, a
class sign-in sheet, a bus route, a library account, a recipe log), run
immediately before the lab, with an explicit "Where this was taught" pointer
back to a week 0 section and an explicit "These names are not the lab's names.
Copy a cell from here into the lab and you get an error." That is a textbook
structure-mapping design and I would keep it unchanged.

It fails in three specific ways, and two of them are the same failure.

### 5.1 Two sidebars teach the surface shape the lab must *not* use

This is the most important thing about the sidebars and it is a
counter-transfer defect, not a coverage gap.

**Verified.** `w2-sidebar.ipynb` cell 8, part 2C:

    while reading is None and attempts_made < 3:

and cell 9 explains it: "**The loop stops the moment `reading` holds something.
Nothing has to break it.**" The lab's `classify_email()` must stop when the
*schema check passes* — and an answer that fails the check is not `None`, it is
a perfectly good dictionary with wrong contents. The sidebar's own summary cell
11 says the words correctly ("Your code loads it, **checks** it, and asks again
when the answer is wrong") while its code shape says the opposite.

**Novices transfer surface structure, not deep structure.** That is the single
most replicated finding in the transfer literature, and it is precisely why the
sidebar design works when the shapes match. Here the shape is nearly identical
to the target and encodes the wrong stopping rule, so the sidebar does not fail
to help — **it actively teaches the error**. The student built the broken
version and confirmed it passes the lab's own stated success test
(`REPORT.md` §2, problem 1). Cell 12 of the lab says "A row passes when it shows
a verdict, a category and a tries count of 1 or more" — three conditions, and
the `ok` column is not one of them.

**And the root is one section earlier than anyone has looked.** `week00-python-on-ramp.ipynb`
cell 90 reads: "Put the `try` inside a `while` loop with a counter... **This is
the exact shape of the week 2 retry.**" Cell 91 then writes
`while value is None and tries < 3:`. So week 0 installs "loop until you have a
value" as the canonical retry, calls it the week 2 shape by name, the week 2
sidebar reinforces it, and the week 2 lab needs "loop until the check passes."
**Three documents agree with each other and disagree with the lab.** That is why
the student ranked this first at 50 points; I agree with the student and not
with the run report, which files this under §2's "never demonstrated" heading
where it does not belong.

The same failure recurs mildly in week 6: **verified via the student's reading**
(`FINDINGS.md` L4546–4560), `w6-sidebar.ipynb` cell 5 teaches `elif` in bold —
"`elif` is what keeps the two paths apart. Exactly one of them runs on each
pass" — and the lab's TODO 2 needs three independent `if`s so that all three
disagreements are reported. Milder, because the check cell catches it with no
model call, but the sidebar's sharpest sentence points the wrong way in the week
whose sidebar is the only preparation for that TODO.

**Fix, and it is small.** Give 2C a second example that *loads successfully* and
is still out of range, so the loop must continue on a value it already holds;
and change week 0 cell 90's sentence from "the exact shape of the week 2 retry"
to "close to the shape of the week 2 retry — week 2 stops on a check, not on a
value." Add "and an `ok` of True" to w2-lab cell 12's success sentence. In week
6, add one line to the sidebar noting that the lab wants every problem reported,
so three `if`s and not `elif`. Cost: under two hours total. Risk: none. **Value:
this is the highest instructional return per hour available anywhere in the
build**, higher than the answer-position fix, because it converts a
counter-example into the contrast case the week actually needs.

### 5.2 Two sidebars cover only the smaller half of their lab

**Verified.** `w3-sidebar.ipynb` is a single part, building a block of text —
which prepares `format_facts()` (4–5 lines) completely and prepares
`build_facts()` (11–12 lines) not at all. `w6-sidebar.ipynb` prepares TODO 2 and
gives nothing to TODO 1. In both cases the *larger* TODO is the unprepared one,
and in week 3 the unprepared TODO is **the CLO1 primary**. The lab is honest
about it — w3 cell 8 routes to three separate week 0 sections and asks the
student to combine them — but "combine three sections you met four weeks ago"
is not scaffolding, it is the absence of it.

Add a second part to the week 3 sidebar that lifts a value out of a nested
dictionary and walks a list of dictionaries pulling one key from each. That is
one cell pair and it closes the largest preparation gap in the course's
CLO1 week. Cost: two hours. Risk: adds ten minutes to a 30-minute sidebar.

### 5.3 The course tells the student four different orders for one week

**Verified in week 1 and reported for weeks 4–7** (`FINDINGS.md` L874–888,
L6221–6227). `w1-overview.md`'s Tasks table lists videos, sidebar, reading, lab;
its `::: next` block ends "Start with the reading. Then work the two sidebars.
Then open the lab."; `course.yaml`'s module item order is overview, reading,
sidebar, lab; the overview video says start with the sidebar.

**Asserted:** this is not cosmetic. The sidebar-before-lab ordering is the whole
mechanism of §5's design — isolated practice must precede the composite task or
it is just extra reading. Four documents disagreeing means a real fraction of
each cohort runs the sidebar after the lab, where it does nothing. Pick one
order, put it in `course.yaml` and every overview page, and re-cut the four
seconds of narration that disagrees. Cost: one afternoon plus one video edit
per week. Risk: none.

---

## 6. Do the discussions do real instructional work?

**Yes, emphatically, and they are the most under-credited asset in the build.**
Your report mentions them only as points a solo run cannot earn. That
undersells them badly.

**Verified across all seven.** Every prompt is anchored to an artifact that is
unique to the student, because the model is nondeterministic; every one says so
in its `::: intro` ("Every part of the prompt asks for a value out of your own
file, so do the lab first"); every one forbids the empty reply ("A reply that
only agrees doesn't count"); and every one names what a weak post looks like
("A summary of the reading with no numbers in it's a weak post"). That
combination — non-shareable evidence, a specificity standard, and a named
failure mode — is what separates a discussion that teaches from participation
theatre, and I do not often see all three.

**There is also a genuine Bloom progression across the seven**, which I do not
think was written down anywhere:

| Week | What the post requires |
|---|---|
| 1 | Quote and identify (Remember/Understand) |
| 2 | Diagnose a failure and propose an instruction change (Analyze) |
| 3 | Attribute a verdict change to a specific fact (Analyze) |
| 4 | Predict, then compare prediction to outcome (Analyze + metacognition) |
| 5 | Judge the marginal value of a step against its cost (Evaluate) |
| 6 | Design a control, then price it against a benign decoy (Evaluate + Create) |
| 7 | Transfer the design to a use case outside phishing (Create) |

Week 6's is the best single assessment item in the course. It asks the student
to attack their own agent, write the missing rule, and then compute what that
rule costs on email 015, the benign decoy. **That is the precision/recall
tradeoff taught as an experience rather than a definition**, and it is exactly
the judgment the job requires. Do not touch it except to fix its evidence.

Three holes, all of the same shape and all cheap.

1. **Verified.** Week 3's 5-point item asks "what your model listed as its
   indicators", and `compare_runs()` drops `indicators`. Week 5's 4-point item
   asks "what the last step added" and `one_line()` truncates at 80 characters.
   Week 7's 3-point item asks the student to "name one email your agent got
   wrong" and the wrong-email list is printed on screen and never written to the
   report. You caught the first two; the third is the same defect and is not in
   your list.

2. **Week 4's prediction task is spoiled twice inside its own module, and this
   is the one I would fix first among the three.** **Verified.** The discussion
   says "This board has two halves, and the order matters. Half one is your
   prediction. Write it before you open your file." Then `w4-lab.ipynb` cell 5
   — which the assignment page orders the student to run as step two of the lab
   — prints all three tool results for email 018 and then prints, in English:
   "This company has taken mail from that sender since 2023 and never reported
   one. **The link host is one the team already blocks.** Either tool alone
   tells you half of it." And `w4-self-check.yaml` question 3 asks the
   discussion's question outright ("You want to know whether that link host is
   on the blocklist. Which tool answers that?") with the answer in its feedback.

   A prediction-before-reveal task is one of the highest-yield activities in the
   whole learning-science literature — it is the generation effect and the
   pretesting effect in one move, and this course designed one deliberately and
   then leaked the answer twice in the same module, for 5 graded points the
   student cannot honestly earn. The student says so about itself
   (`FINDINGS.md` L2946–2950): "I could not honestly claim I worked it out."

   **Fix:** move the prediction out of the discussion and into the lab, as a
   markdown cell and a free-text cell *before* cell 5, and have cell 5 open with
   "Before you run this: which one tool would you have asked for?" The
   discussion then reports the comparison rather than manufacturing the
   prediction. Cost: one cell and a rewrite of half the discussion prompt. Risk:
   the discussion loses 5 points of its own and needs them re-allocated.
   Alternative and cheaper: change cell 5 to print only the *sender* tool
   result, move the other two below the prediction. Cost: twenty minutes.

3. **Asserted:** all seven posts are ~150 words with a ~60-word reply and the
   same four-part structure. The thinking escalates but the *form* does not, and
   by week 5 a student is executing a template. Consider varying the form once —
   week 6 would carry a 250-word single post with no reply requirement, given
   what it asks — rather than adding requirements. Low priority.

---

## 7. Do the rubrics measure what the objectives claim?

Mostly yes. Specifics, all **verified** against the seven YAML files.

**What is right, and unusually so.**

- Four levels, top level equal to criterion points, mapping one-to-one onto the
  Canvas mastery scale with no translation step. `alignment-matrix.md` §8 gives
  the reason and the reason is correct.
- The 2/0 gap is deliberate and defended: 2 means attempted-and-partial, 0 means
  the work shows nothing. That distinction is the one most rubrics collapse.
- `w7-lab.yaml`'s header: "**NO POINTS FOR A CORRECT VERDICT.** The answer key
  ships with the notebook, because nothing in this course locks... What is
  graded is the quality of the note and the honesty of the measurement." That is
  the right response to an open-book design and it is the sentence I would put
  on the front of the course.
- Every rubric header says every level is decided from the screenshot, the file
  and the written answer, and nothing needs the student's notebook. That makes
  the rubrics gradeable at scale by an adjunct, which for this program is not a
  nicety.

**What is wrong.**

- **CLO3's criterion measures a file, not a build** (§2.1). This is the one
  substantive rubric defect.
- **Criterion 1 in every rubric is submission completeness, and it is expensive.**
  25 points in week 1, 32 in week 4, 20 in week 5. **Asserted:** a completeness
  criterion worth a third of the grade rewards compliance over learning and
  compresses the range on the criteria that measure the objective. Week 6 gets
  this right at 8 points and week 7 at 8; weeks 1 and 4 do not. Bringing weeks
  1–5 down to 10 and redistributing into the outcome-linked criterion would cost
  nothing and would widen the measurement band where it matters. Risk: it also
  raises the penalty for a missing screenshot, which for this cohort is a real
  and non-instructional failure mode. I would do it in weeks 3, 4 and 5 only.
- **Every rubric carries a screenshot criterion and the screenshot proves
  nothing the file does not.** Ten instances. **Asserted:** its real function is
  anti-plagiarism, which the nondeterministic artifact already handles better.
  Worth revisiting only if grading load becomes a complaint.

---

## 8. "Mechanisms taught but never demonstrated" — one problem, three, or none?

Your §2 groups week 2's retry, week 5's step cap, week 6's controls and week 1's
temperature claim under one heading. **I think the heading merges two different
defects and one non-defect, and separating them changes what you should do.**

### 8.1 A hand-built demonstration is not a compromise; it is the correct method

Take this one head-on. You ask whether a hand-built demonstration is
pedagogically fine. It is better than fine — **for teaching a mechanism, a
constructed input is superior to a live one**, for the same reason a physics
demonstration uses a track and a cart rather than a car on a road: it isolates
the variable, it is deterministic, it is reproducible across every student in
the section, and it removes the confound the course is otherwise fighting all
term (a model that does not answer the same way twice). A student who watches
`step_cap` fire on a hand-built trace has seen the mechanism. A student who
watches it fail to fire on six live runs has seen nothing.

And the course already does this, deliberately and with its reasoning stated.
**Verified:** `w5-lab.ipynb` cell 10 demonstrates `step_cap` on a hand-built
trace and says so. `w6-lab.ipynb` cell 14 runs the fact check on three made-up
answers where all three disagreements fire. `w6-lab.ipynb` cell 15's own output
anticipates the null result and explains it in the student's own words:

> That is a result, not a broken function. None of these eleven emails has a
> blocklisted link host or a known-bad sender... Cell 15 ran your function on
> three made-up answers, and that is where you see all three fire.

**And week 0 already demonstrates both of the two mechanisms you list as never
firing.** Verified: cell 81 is headed "Watch the cap do its job. No score in
this list is below passing, so only the cap can end the loop." Cell 92 is headed
"Put a bad entry in every slot and watch the cap stop the loop," and exhausts
the retry.

So on the demonstration axis, **week 5's step cap and week 6's controls are not
defects at all.** They are correctly-designed constructed demonstrations plus an
honest live measurement, which is the right pairing and which the course states
out loud. I would not spend an hour on either.

### 8.2 The one genuine demonstration gap is week 2, and it is a different problem than you have it filed under

**Verified.** Week 2's lab has broken samples for TODO 1's `extract_json` (cell
10 feeds four saved replies) and **nothing equivalent for the retry loop**. So
the only place a student can watch their own retry fire is a live run against a
model chosen because it "sometimes" misbehaves. On a sample of four emails and
eight calls, it did not.

But the reason this matters is not "the mechanism did not fire." It is §5.1:
the student's retry may be the *wrong* retry, three documents taught them the
wrong shape, and the lab's own success test passes the wrong shape. A
demonstration that forced a schema-failing-but-loadable reply would fire the
retry **and** discriminate the two shapes in one cell. That is one cell —
`STUBBED_REPLIES = [...]` plus a `fake_ask_model` — and it is worth more than
everything else in your §2 combined.

### 8.3 The real pattern is not "never demonstrated". It is "stated as fact, contradicted by the run"

This is a genuine pattern with at least six instances and it is corrosive in a
way the demonstration question is not.

**Verified.** `w1-wrap-up.md` line 37: "It makes them steadier. The same prompt
comes back more alike each time you run it." Unhedged, three-runs-a-side, and
this run's 0.2 group held the biggest outlier. `w5-content.md` line 26: "Three
tools exist under a cap of four, which leaves room for one wasted step and no
more" — arithmetically true, and it invites a conclusion (`step_cap` will fire)
that `tools_left()`'s name-based comparison makes almost impossible. You verified
four more in week 6 (009 and 012 under the 0.7 floor).

**Why this is the serious version.** The course's best feature, running through
every discussion and both week 6 and week 7 rubrics, is *argue from your own
numbers*. Every unhedged claim the run contradicts teaches the opposite: that
the course's stated facts and the student's own evidence are two different
things, and that when they disagree you write down what the course said. That is
the precise habit the week 7 criterion — "cites the accuracy figure from this
run and names one email this run got wrong" — exists to build.

Note that the course already knows how to write this correctly. `w1-lab.ipynb`
cell 12: "Most runs give several different answers, and two runs can land on the
same words." Hedged, honest, still teaches the point. `w1-wrap-up.md` line 37 is
the same claim with the hedge removed. **The fix is a pass over the seven
wrap-ups and the readings to bring every result claim to the cell-12 standard,
and a rule for future authoring: no page states a run result it has not measured
at n≥30, and every result claim carries its n.** Cost: a day. Risk: the hedged
version is weaker prose and a student may read "sometimes" as "the course does
not know." Mitigate by giving the number: "In our own 200-run measurement, X
happened in N of 200."

**Summary answer to your question.** Not one problem and not three. **One
non-defect** (constructed demonstrations, weeks 5 and 6 — leave them and
protect the pattern), **one genuine demonstration gap** (week 2, and its real
value is discriminating the two loop shapes), and **one calibration defect with
six instances** (unhedged result claims). Renaming the section that way will
also stop the week 6 measurement-validity bug (§1.4) from hiding inside it,
which you correctly worry about.

---

## 9. Sequencing and workload

**The advertised 42 hours excludes the only 4–6 hours the target audience
uniquely needs.** Verified: `course-schedule.md` gives "Weekly total | Under 6
hours" ×7 = 42, and lists week 0's 4–6 hours separately. The honest number for a
student with no programming background is **46 to 48 hours**, and it is not
evenly spread (§4.1).

**Asserted:** for an 8-week community-college course, 46–48 hours is *low*, not
high. The load problem is not the total. It is entirely the shape: 10.5 hours in
week 1, then five, then a lab that the course itself calls the hardest in the
course three separate times.

**Which brings me to the estimates, and here the student's finding is more
serious than either of you treats it.** Verified in the overview pages: weeks 5,
6 and 7 each price the lab at 180/180/165 minutes and each say "Give it two
sittings." The student came in 55 to 117 minutes under **every** weekly estimate,
across all seven, and its explanation is correct: it never had to debug, because
there was nothing to debug (§2.1).

Your reading — "read 42 hours as realistic for a real beginner, not generous" —
is the charitable one and it may hold. I do not think it does, and here is the
test I would apply: **an estimate is only wrong in one direction if the work is
open-ended.** These labs are not. Fourteen TODOs, of which twelve are dictated
at line granularity and two (week 7's) are described in English. A true novice
who reads carefully and types what the comment says will be slow — perhaps
twice the student's time — but they will not be *stuck*, because there is no
decision available to be stuck on. My estimate for a genuine beginner on week 5
is 90 to 120 minutes, not 180.

**Asserted, and this is the part that matters:** the cost of an inflated warning
is not lost time. It is credibility. "This is the hardest week in the course, so
start early" appears three times in week 5 and the week is transcription. A
student who takes that warning seriously and finds nothing there discounts the
next warning, and the next warning is week 6 — the week that actually is hard,
and the week whose whole lesson is that a control which looks like it fired may
not have. Fixing §2.1 fixes this too: fade the TODOs and the 180 minutes becomes
true.

**One sequencing note nobody raised.** Week 7 carries two objectives (CLO5 and
CLO6), two TODOs, twenty emails, a 100-point rubric with a 36 and a 56, a
discussion that transfers to a new domain, and an 8-item self-check — in the
last graded week, immediately before an exam week. It is priced at 287 minutes,
the same as weeks 3 and 4. **Asserted:** it is the heaviest week in the course
by cognitive demand and the lightest by scaffolding change, and it is where
students are most likely to be behind. Consider moving the batch evaluation
(CLO6) into week 6 alongside the guardrail measurement, which is already a
measurement week, and leaving week 7 to the note (CLO5). That also fixes §3(a).
Cost: substantial — it is a module restructure, one term's worth of work. Risk:
high. I raise it as a design observation for the next major revision, not as a
fix for this one.

---

## 10. What is genuinely good, and must survive any fix

I am specific here because the list above is long and the run does not support a
verdict of "this course is broken." It is a well-designed course with a set of
correctable defects, and several of its decisions are better than what I see in
courses that have run for five years.

1. **Week 0's five-cell teaching pattern.** Worked example → "What each line
   does" (line by line) → "Try changing this" (with a prediction asked for) →
   "You try." → "The answer." → "**Where this shows up**" naming the exact
   future week. Ten times, without variation. That is the worked-example-to-
   completion-problem sequence executed correctly, with an explicit transfer
   signpost that most textbooks omit. **Verified across all ten sections.** It is
   the best-designed artifact in the build and it is also the template for
   fixing §2.1 — the labs need to do to weeks what week 0 does to cells.

2. **"A bad week costs you that week's points. It does not end the course."**
   Verified on `w1-lab.ipynb` cell 0, `w1-overview.md`, `course-schedule.md`, and
   implemented as a working reference version of every prior week in every
   starter notebook. Cascade failure is the number one attrition mechanism in
   build-forward technical courses and this course has engineered it out. Do not
   trade this away for anything, including for §2.1 — it is what makes fading
   the TODOs safe.

3. **The discussions.** §6. Non-shareable evidence, a named specificity
   standard, a named failure mode, and a real Bloom progression. Week 6's in
   particular — attack your own agent, write the missing rule, price the rule
   against the benign decoy — is the best assessment item in the course.

4. **The self-check item writing.** Verified in `w4-self-check.yaml`. Distractors
   are real misconceptions ("The model looked the host up and sent back what it
   found"), and every one of the four answers carries its own feedback that
   diagnoses the specific error and names the section. That is expert item
   writing. It makes §1.1 worse, not better: an excellent instrument with a void
   scoring key.

5. **`w7-lab.yaml`'s "NO POINTS FOR A CORRECT VERDICT."** The correct answer to
   an open-book design, stated as a principle rather than worked around.

6. **The exam's `taught_in` field, and `alignment-matrix.md` §6.** Every exam
   item carries where it was taught, at what level, on what artifact. And the
   blueprint refuses to let selected response stand as primary evidence for
   anything above Analyze. Both are stronger than what most accredited programs
   document.

7. **Cost design.** Week 0 requires no key and makes no model calls, so five
   hours of Python practice carries zero financial risk. The whole course costs
   about a cent against a $2.00 budget. `send_request()` waits out a 429 and
   tells the student nothing is broken while it waits. **Verified** in
   `w1-lab.ipynb` cell 4. That is care for a population that cannot absorb a
   surprise.

8. **Defensive shipped code.** Every export cell writes a file even when the
   student's function is missing, and says so. Every check cell degrades to a
   message rather than a traceback. The student ran ~200 cells across nine
   notebooks and reported nothing broke that the course did not break on purpose.
   For this audience that is worth more than any single lesson.

9. **The 013/024 twin.** A word-for-word control message differing only in the
   planted paragraph is exactly the right instrument, and building one into the
   corpus was a good decision. §1.4 is a plumbing bug in front of a well-designed
   experiment, not a design error.

10. **The week 6 walkthrough reporting its own demonstration failing, with
    counts.** You already credit this and you are right to. It is rare, it models
    the honesty the week 7 rubric grades, and it should survive the §1.4 fix —
    keep the candour, change what it is candid about.

---

## 11. Recommended order, with cost and risk

| # | Change | Cost | Risk | Why here |
|---|---|---|---|---|
| 1 | Move the correct answer off index 0 in the 43 self-check items; keep `shuffle: false`; add a build gate | ~1 h + gate | none | Restores the course's only formative instrument, all 7 weeks (§1.1) |
| 2 | Fix week 2's loop shape in three places: week 0 cell 90's sentence, sidebar 2C's second example, w2-lab cell 12's success sentence; add a stubbed malformed reply | ~3 h | none | Removes an actively-taught error worth 50 points and fires the retry (§5.1, §8.2) |
| 3 | Week 1 TODO 1: "into **the request** dictionary", plus a `reasoning_effort` assertion in the check cell | 20 min | none | First graded function; the belief it installs (§1.2) |
| 4 | Add the body to `run_triage()`'s **closing** call on the undefended path; re-measure | 1 h + a measurement run | the re-measurement may still show no effect, which is a content decision, not a bug | §1.4 |
| 5 | Settle week 3's email identity on one pair across code, notebook, page, video, quiz and wrap-up | ~3 h | video re-cut | Sits in the CLO1 evidence week and breaks a contrast pair (§1.4 of your report) |
| 6 | Add the four missing export fields; fix week 6 self-check q4's excerpt; add the wrong-email list to week 7's report | ~1 h | none | Recovers discussion and rubric points (§6) |
| 7 | Fold `or`, bare truthiness, `if not x:` and tuple unpacking into week 0 sections 7 and 8 | ~4 h | week 0 grows slightly | Removes the justification for dictating week 5's lines (§4.3) |
| 8 | **Fade week 5's TODO 1**; move the four verbatim lines into a labelled hint cell | ~2 h | raises week 5 failure rate; mitigated by the reference-version safety net | The CLO3 alignment gap (§2.1) |
| 9 | Move week 4's prediction into the lab before cell 5, or trim cell 5's reveal | 20 min–2 h | the discussion loses 5 points and needs re-allocation | Recovers the best cognitive activity in the module (§6.2) |
| 10 | Hedge every unmeasured result claim to the `w1-lab` cell 12 standard; adopt an authoring rule (n≥30, state the n) | ~1 day | weaker prose | The calibration pattern, six instances (§8.3) |
| 11 | Add a second part to the week 3 sidebar covering nested lift and list-of-dicts | ~2 h | +10 min sidebar | Largest preparation gap, in the CLO1 week (§5.2) |
| 12 | Settle one sidebar/reading/lab order across `course.yaml`, all overview pages and the videos | 1 afternoon + 7 video edits | none | The sidebar design depends on it (§5.3) |
| 13 | Fix `welcome-start-here.md` line 43 ("Submit what you've."); move the syllabus acknowledgment after the AI policy page; reconcile the two "start here" instructions | 30 min | none | First-hour credibility (§4.2) |
| 14 | Relabel exam item 19 `Analysis` and correct its `taught_in`; same for the `softfail` half of item 26 | 20 min | none | The audit field must be true or it is worse than absent (§3b) |
| 15 | Add a supporting CLO5 or CLO6 outcome link to a week 5 or week 6 criterion | 30 min | none | Two of six objectives currently rest on one week-7 submission (§3a) |
| 16 | Replace the week 0 self-assessment's 10 recall items with 5 code-reading items; change the "9 or 10: skip" advice | ~3 h | students may read it as harder | The placement instrument cannot currently measure the thing it routes on (§4.1) |
| 17 | Give week 0 calendar space in the first term offering | registrar conversation | term-shape change | The 10.5-hour week 1 is where this cohort drops (§4.1) |

Items 1 through 6 are one week of work and address everything in your Fix First
section plus the two things I would put above it. Items 8 and 16 are the ones
that change what the course *teaches* rather than what it *reports*, and I would
not ship another term without at least item 8.
