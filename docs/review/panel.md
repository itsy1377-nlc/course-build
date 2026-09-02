# The review panel, and how to run it again

The roster was not written down the first time and had to be reconstructed from
memory of a prior session. This file exists so that does not happen again. It
holds the roster, the prompt structure, the scores, and the findings each
panelist produced that were verified against the repository afterwards.

---

## The roster

Six readers. Three are students who would take the course, three are the
professionals who would endorse, teach, or approve it. Each reads **one document
only** and is told not to read the sibling proposal, the archives, or the code,
so that the panel judges the proposal a reader would actually be handed.

| # | Name | Who they are | The question only they can answer |
|---|---|---|---|
| 1 | **Maya** | 17, dual-credit high school senior, has never written a line of code, four other classes and a part-time job, uses a chatbot for essays | What would scare her off, and where would she check out |
| 2 | **Reggie** | 34, retail manager, evening student in the Cyber Defense AAS, family, can read a bash line but not write Python | Is each week worth the evening it costs him, and what can he say in an interview |
| 3 | **Dev** | 20, second year, already codes, home lab, CTFs, runs local models for fun | Where is the ceiling, and where would he break it |
| 4 | **Priya** | Senior SOC analyst, nine years, sits on a college advisory board, hires from this program | What can a graduate do on day one that another applicant cannot |
| 5 | **Tom** | Full-time instructor, 5/5 load, no TA, 25 students of mixed ability | The Tuesday problem: minute 40, six students stuck. And grading hours |
| 6 | **Dr. Alvarez** | Department chair, sitting curriculum committee member, Texas community college district | The bus test, institutional risk, and whether outcomes are assessed or asserted |

## The prompt structure

Every panelist gets the same three scored items so results are comparable across
rounds, then their own specialist questions.

1. **FUN, 1 to 10.** How much would a student enjoy the weeks.
2. **INTERESTING, 1 to 10.** Scored separately. Is the content worth knowing.
3. **A commitment question**, phrased for the seat: would you enrol eagerly,
   would you endorse it, would you teach it, would you approve it.

Then two to five seat-specific questions, then always:

- **The worst moment.** Where would you disengage, drop, or stop paying
  attention. Be blunt.
- **One change.** The single change that would most raise your score.

Instructions given to every panelist: stay in character, be honest including
unflattering honesty, do not try to please the author, judge the course as it
would be to sit through rather than as a piece of writing, and cite specific
parts of the document.

**Do not tell the panel the prior scores.** Comparing across rounds only works if
each round is a cold read.

---

## Round 1, 2026-09-01: the funded proposal after three Codex review rounds

| Reader | Fun | Interesting | Verdict |
|---|---:|---:|---|
| Maya | 6 | 8 | would enrol eagerly |
| Reggie | 7 | 8 | would enrol eagerly |
| Dev | 6 | 7 | would enrol eagerly |
| Priya | 8 | 8 | endorse the design, vote against scheduling it |
| Tom | 8 | 8 | would teach it; deliverability **3/10** |
| Alvarez | 7 | 8 | **DEFER** |
| **Mean** | **7.0** | **7.83** | 5 of 6 would take or teach it |

### Findings that were verified against the repository afterwards

**The course was missing the third leg of its own title (Priya).** "Security
operations" appeared zero times in the 921-line proposal, along with
containment, revoke, respond, MCP and alert. "Detection" appeared twice, both
about the harness's internal chain detector. Fixed in section 5a; week 6 was
swapped whole.

**Effect 1 was an injection channel into a classmate's agent (Dev).** Section
7a's safety argument was "no student expression reaches the interpreter", which
is true of Python and false of the model. Student-supplied text lands in a
classmate's context inside their agent loop, one week before the course teaches
injection.

**The money never added up (Dev and Alvarez, independently).** 25 students at $10
is $250 of a $300 class budget before the instructor's development, the gating
experiment, re-runs, or week 5 asking every student to build a runaway loop on
purpose. No section sums one student's mandated trial counts against their $10,
and section 9 already documents that a budget cap can return a well-formed 200
with empty content that the runner scores as a clean miss: a student who runs dry
mid-week-4 gets a false null on the one week built around nulls.

**Six of seven graded artifacts were a written explanation of something the
student just watched (Maya).** "That is a writing class with a terminal in it."

**Nobody scores the liar (Maya).** Week 3 has 15 points for reports on
classmates' tools and nothing for whether your own cuckoo fooled anybody.

**The week 3 draw is unfair (Tom).** Effect 1 shows on the first result card,
effect 4 may have no surface at all. A student who draws 1, 7 and 8 is done at
minute 25; one who draws 3, 4 and 6 is dead at minute 45. Nothing balances
difficulty and nothing in the rubric compensates.

**Roster churn against an identity-chained course (Tom, and Alvarez separately).**
Census is day 8, everything descends from an artifact made in week 1 minute 20,
and there is no late-add path. Drops leave dangling assignments in week 3's
distribution graph.

**No contact-hour model (Tom).** A duration is specified exactly twice in 921
lines. No session plan, no in-class versus homework split, no differentiation
plan.

**Grading was priced at 45 to 50 hours** across the term for 25 students, week 6
alone at 13 to 17 (Tom). Not a document figure; his estimate. Later review
established that neither proposal contains any grading-hours figure at all.

**The filmstrip has no off-ramp (Priya).** "Reading twenty thousand characters of
JSON is the job. Nothing in my environment renders a filmstrip." A graduate
trained only on the pretty view may be worse off than one never coddled.

**Section 8 demanded thirty trials and week 4's rubric paid for twenty (Priya).**
At a true 5 per cent rate, twenty trials show zero 35.8 per cent of the time.

**Three judges to one decimal place (Alvarez).** The Status section reported "8.0
for fun and 8.7 for interest" from three judges, in a document whose section 8
correctly argues that n=5 cannot rule out an effect. "If n=5 is not enough to
rule out a capability effect, n=3 is not enough to support an 8.7."

### The observation worth keeping longest

Alvarez, on whether the document's constant self-correction helps or hurts:

> "The correction count is itself evidence about a base rate. The honest reading
> is not that the document is now correct. It is: the error density here is high,
> the reviewed fraction is unknown, and the unreviewed sections should be assumed
> to contain errors at a similar rate."

And:

> "Candor can function as armor. A document that pre-concedes every objection is
> very hard to argue with, because each of my points has already been written
> down, conceded in a paragraph, and left in place. A course that is candidly not
> ready and a course that is obliviously not ready arrive in August in the same
> condition."

Both were borne out within the hour: the panel found six contradictions three
Codex rounds had passed over, and a later design workflow found four false claims
in a design built from a fresh reading of the same document.

### What each reader wanted most

| Reader | Their one change |
|---|---|
| Maya | Put the class board on the wall every week, not only weeks 1 and 7 |
| Reggie | Give week 3 a second session, paid for by folding week 2's grid work into week 4 |
| Dev | Let students who want to write a real cuckoo write one, into the sandbox that is being built anyway |
| Priya | Rebuild week 6 as incident response on somebody else's raw trace and gateway log, filmstrip off |
| Tom | A loadable known-good checkpoint for every week, and every rubric rewritten to grade reasoning over whichever agent the student actually ran |
| Alvarez | Signatures rather than specifications, a named second instructor, and one built vertical slice before seven notebooks are written |

Priya's change was adopted, with its sourcing replaced: see the funded proposal's
section 5a for why authored packs beat harvested student records.
