# Addenda to the Programming Knowledge Unit Coverage Analysis

Three additions to `ku-coverage-analysis.md`. Nothing in that document changes.

- **Addendum A** gives every claim a source a reviewer can open, and says plainly
  which sources could not be verified.
- **Addendum B** maps each BSP element to the numbered ITSY 1377 sub-objectives,
  which is the granularity a CAE reviewer works at.
- **Addendum C** is the same recommendation in one page of plain language, for
  readers who will not read four thousand words.

---

## Addendum A: Evidence table

Every URL below was requested and returned HTTP 200 on 2026-08-29. Where a
source could not be verified, that is stated rather than omitted, because a
missing citation a reviewer discovers is worse than one the document declares.

| # | Claim it supports | Source | Verified |
|---|---|---|---|
| A1 | The NCAE-C programme, its designations, and who runs it | https://www.caecommunity.org/about-the-ncae-c-program | Yes |
| A2 | **The 2024 CAE-CD Knowledge Units, the governing document.** Machine readable: 171,991 characters extract cleanly with `pdftotext`. This is the primary source for every BSP quotation below | https://dl.dod.cyber.mil/wp-content/uploads/cae/pdf/unclass-cae-cd_ku.pdf | Yes, text extracted and quotations checked |
| A3 | Official CAE-C publications, checked for a second copy of the KU list | https://www.caecommunity.org/cae-c-publications | Yes. The KU list is not among the six documents here; use A2 |
| A4 | The CAE-CD Requirements Document, referenced by A2 for alignment specifics | https://public.cyber.mil/ncae-c/documents-library/ | Cited inside A2; retrieve before submission |
| A5 | WECM governance, and that WECM records are the statewide authority | https://www.highered.texas.gov/about/wecm/ | Yes |
| A6 | The WECM course inventory | http://www.txhighereddata.org/institution-overviews/course-and-program-inventories/wecm/wecm-search-courses/ | Yes |
| A7 | ITSE 1359 official course description, quoted verbatim in Addendum D | https://catalog.collin.edu/preview_course_nopop.php?catoid=3&coid=4166 | Yes |
| A8 | ITSE 1359 credit and contact hours as published by a second college | https://catalog.alvincollege.edu/preview_course_nopop.php?catoid=6&coid=6577 | Yes, 3 SCH, 2 lecture + 2 lab |
| A9 | Northeast Lakeview College catalog, the basis for section 2's finding that no end-of-course outcomes are published | https://mynlccatalog.alamo.edu/ | Yes |
| A10 | The NLC catalog edition list, for citing the exact edition consulted | https://mynlccatalog.alamo.edu/misc/catalog_list.php?catoid=294 | Yes |
| A11 | The district-wide catalog, for courses taught across Alamo Colleges | https://myalamocatalog.alamo.edu/ | Yes |
| A12 | ITMT 1370 Powershell Scripting, cited in D.5a as evidence that the statewide inventory treats a Windows scripting course as a local addition rather than a standing requirement | https://www1.dcccd.edu/Cat22-23/coursedescriptions/detail.cfm?course=ITMT&number=1370 | Yes. The catalog entry reads "This is a Local Need Course and This is a WECM Course Number" |

### Three corrections to the main analysis, from the primary source

Now that A2 can be quoted directly, three things in `ku-coverage-analysis.md`
need amending. None of them changes the conclusion about ITSY 1377.

**1. BSP outcome 6 is misquoted, and the real wording is broader.** Section 3.2
gives it as "Demonstrate conceptual understanding and practical use of regular
expressions". The document says:

> "6. Demonstrate conceptual understanding and practical use of regular
> programming or scripting expressions."

The words "programming or scripting" are missing from the quotation. The topic
list is unambiguous about regular expressions (topic 3 reads "Fundamental
concepts and basic implementation of regular expressions"), so the substance of
the finding survives. But the outcome as actually written is looser than the
analysis represents it, and a reviewer reading both documents will notice. Fix
the quotation wherever it appears.

**2. Topic 6 names Python explicitly.** Section 3.1 scores element 6 "No" for
ITSY 1377 on the reasoning that the element "says 'both' explicitly". That is
correct, and the full text sharpens it:

> "6. Scripting language on both Windows and Linux (e.g. PERL, Python, BASH,
> JAVA, VB Scripting, Powershell)"

The noun is singular: one scripting **language**, on two platforms. The
parenthesis is a menu of acceptable languages, and Python is on it alongside
PERL and Java, which are also cross-platform. So the element asks for one
language demonstrated on both Windows and Linux, not for a Windows language and
a Linux language. A Python course clears the language half automatically and
clears the platform half only if students actually execute on both. See D.5a.

**3. Two thresholds appear, not one, and they do not obviously agree.** Section
2 quotes the 75 percent rule, which is real and appears in the Model KU
Structure. The alignment guidance a few pages earlier says something weaker:

> "The majority of the KU topics must be addressed in the aligned courses. KU
> topics are deliberately broad so schools can apply their discretion and
> subject matter expertise."

Keep using 75 percent, because it is the stricter of the two and the arithmetic
already passes on that basis. But note the "deliberately broad" sentence in the
memo: it is the document's own authority for a locally tailored syllabus, and it
is the sentence Addendum D rests on.

**One further rule the analysis does not quote, which decides Addendum D:**

> "Programs should not align multiple courses to a KU purely to show the
> strength of coverage. There is no such thing as 110% coverage; either a KU is
> covered or it is not... If there are multiple courses that cover a KU, then
> schools should align only the minimal set or the single course with the
> primary coverage."

---

## Addendum B: BSP elements against ITSY 1377 sub-objectives

Section 3.1 judges each BSP element against the course as a whole. This maps the
same elements to the numbered sub-objectives that appear on the weekly Overview
pages, which is the level a CAE reviewer actually reads.

Coverage verdicts are carried over from section 3.1 unchanged. The added column
is which sub-objectives, if any, touch the element. **An element with no
sub-objective listed is unaligned**, and that is the whole argument in one column.

| # | BSP element | Verdict | ITSY 1377 sub-objectives that touch it |
|---|---|---|---|
| 1 | Basic security concepts | **Yes** | 1.2, 1.3, 5.1, 5.3, 6.1, 6.2, 7.2 |
| 2 | Permissions, bounds checking, input validation, type checking, parameter validation | Partial | 3.3, 4.3, 4.4, 7.4 (input and parameter validation only; **no bounds checking**) |
| 3 | **Regular expressions** | **No** | **none** |
| 4 | Data structures and algorithms | Partial | 2.3, 4.1 (structures are consumed, never designed; no algorithms) |
| 5 | Boolean logic including XOR | Partial | 3.3, 7.3 (compound conditions only; **XOR never appears**) |
| 6 | **Scripting on both Windows and Linux** | **No** | **none** (one language, one provided environment) |
| 7 | IDE, compilers and interpreters | Partial | 1.4, 2.4 (tooling used, concepts untaught) |
| 8 | Basic programming constructs, roll-up | Partial | follows 8a to 8j below |
| 8a | Variables and types | **Yes** | 1.4, 2.1, 2.3 |
| 8b | Strings, arrays, structures | **Yes** | 2.2, 2.3, 4.1 |
| 8c | Sequential and parallel execution | Partial | 3.4, 4.1 (sequential only; **concurrency never taught**) |
| 8d | Assignments | **Yes** | 1.4, 2.1 |
| 8e | Decisions and branching | **Yes** | 3.3, 7.3, 7.4 |
| 8f | Loops | **Yes** | 2.1, 3.4, 4.1 |
| 8g | Functions, procedures, calls | **Yes** | 2.1, 4.3, 4.4 |
| 8h | Debugging techniques | Partial | 6.3, 7.3 (results interpreted; **no systematic method taught**) |
| 8i | Console and file I/O | **Yes** | 5.2, 5.4, 6.3, 7.1 |
| 8j | Libraries | **Yes** | 2.2, 3.3, 6.3 |

### What the grid shows that the prose does not

**Two elements have no sub-objective at all.** Regular expressions and
cross-platform scripting are not thin, they are absent. Nothing in twenty-eight
sub-objectives touches either one. That is a stronger statement than "not
covered" and it is checkable in one column.

**The four Partials fail for four different reasons**, and only one of them
could be fixed by writing a new sub-objective:

- Element 2 is missing **bounds checking** specifically, while input and
  parameter validation are strong. A narrow gap.
- Element 4 has students **consume** structures rather than design them. A depth
  gap.
- Element 5 never uses **XOR**. A single missing operation.
- Element 8c never teaches **concurrency**, and 8h never teaches a **debugging
  method**. Two content gaps.

**The nine Yes elements cluster in Weeks 2, 3 and 4.** Sub-objectives 2.1, 2.3,
4.1 and 4.3 each carry three or more elements. That concentration is worth
naming to a reviewer: the course's BSP alignment is real but narrow, sitting
almost entirely in the three weeks where students write code.

---

## Addendum C: The recommendation in plain language

*Written for a reader who needs the decision and the reason, not the analysis.
Everything here is argued in full in the main document.*

### What was asked

Can ITSY 1377 be the course that carries the Basic Scripting and Programming
knowledge unit for the CAE application?

### The answer

No. Four separate reasons each settle it on their own.

**It covers half of what is required.** The knowledge unit lists 18 topics. A
course has to cover at least 14 of them. ITSY 1377 covers 9. Two topics are
missing outright: regular expressions, and scripting on both Windows and Linux.

**Two required outcomes cannot be met.** The knowledge unit asks students to
automate system administration tasks, and to use regular expressions. This
course does neither, and nothing in it comes close.

**Adding the missing material would break the course.** The gap is about 26
hours of teaching. The course is 64 hours. Every way of freeing that time
damages at least three of the six outcomes ITSY 1377 already has to deliver.

**The two courses want opposite things from students.** ITSY 1377 has to let
students use AI help, because one of its outcomes is judging AI-written code.
Basic Scripting and Programming needs students to write code unassisted, so a
grader can tell what the student can do alone. One course cannot hold both
rules at once. No redesign fixes this, and it is the reason that matters most.

### What to do instead

The knowledge unit already has two better homes in the required plan.
Programming Fundamentals I is one. The Linux course sequence is another, and it
covers part of it today. Neither needs a new course.

### One thing to start now, because it blocks everything

The college publishes course descriptions but no end-of-course outcomes.
A knowledge unit map cannot be built from a description. Someone has to collect
the current syllabus for every course in the plan. It costs nothing, nobody can
skip it, and every other piece of the application waits on it.

### One thing worth saying out loud

Keeping these two courses apart helps both. Students who write code without help
first are better at judging AI-written code later. Splitting them is not a
compromise. It is the right order to teach them in.

---

## Addendum D: ITSE 1359 as the BSP carrier, costed

Section 6 recommends ITSC 1342 Shell Programming. This addendum sets out a
second option that was not considered there: **ITSE 1359 Introduction to
Scripting Languages**, taught in Python and executed on both Windows and Linux,
carrying BSP under a locally tailored syllabus.

It was reviewed adversarially on four lenses before being written up. Three
returned "sound with conditions" and one returned "serious problems". The
findings that survived are in the risks below rather than hidden.

### D.1 Why it is worth considering

**The four arguments in section 3 are arguments about ITSY 1377, not about
scripting courses.** Two of them do not transfer at all:

- **Displacement (3.3) does not apply.** The 26 hours are fatal in ITSY 1377
  because six other outcomes compete for them. ITSE 1359 has nothing to
  displace, because scripting is the course.
- **Assessment integrity (3.4) does not apply**, and this is the argument the
  analysis calls strongest and unfixable. ITSY 1377 must permit AI assistance to
  assess its own outcome 6. A dedicated scripting course can require unassisted
  proctored authoring with no policy conflict.

**The KU document authorises the tailoring.** Its alignment guidance says KU
topics "are deliberately broad so schools can apply their discretion and subject
matter expertise". The WECM description uses "including", which is not
exhaustive, and adds "Topics may adapt to changes in industry practices".

**It prefers a single carrier.** The same guidance says schools "should align
only the minimal set or the single course with the primary coverage", and that
there "is no such thing as 110% coverage". Adding two courses to look thorough
is explicitly discouraged.

**Regular expressions is named in the statewide course description**, which is
better evidence than a local syllabus for the element the analysis scores as an
absolute zero.

### D.2 What the state record carries, and what it does not

| Carried by the WECM description | Left to the local syllabus |
|---|---|
| 3 regular expressions | 1 basic security concepts |
| 4 data structures (as "basic data types") | 2 permissions and bounds checking |
| 8a variables and types | 6 both Windows and Linux |
| 8e, 8f control structures | 7 IDE and interpreters |
| 8i console and file I/O | 8c parallel execution |
| 8b strings, via "textual analysis" | 8h debugging method |

**Six of eighteen elements come from the state record. Twelve do not.** That is
the central weakness of this option and it must be stated plainly in any memo,
because it is the same weakness section 4.3 used to reject the Linux sequence.

ITSE 1359's three statewide end-of-course outcomes are "design programming
solutions using scripting languages", "write scripts", and "test and debug
scripts". None mentions security, automation, regular expressions, or a second
platform. **Regex is in the course description, not in the outcomes**, and the
WECM Protocol Manual treats outcomes as the part "meant to be taught and
measured".

### D.3 The hour budget, honestly

An earlier draft of this option claimed 37 of 64 hours. **That figure is wrong
and should not be shown to the committee.** It reused ITSY 1377's 11-hour Python
block, which teaches scaffold completion to students who already passed a
programming prerequisite, under a policy that permits AI assistance.

| Item | Hours |
|---|---|
| Python from zero, standalone, from section 5's own estimate of four to five weeks | 16 to 20 |
| The BSP gap list from section 3.3, less the correction below | 23 |
| Element 1, basic security concepts, which ITSE 1359 does not inherit | 2 to 3 |
| **Total** | **41 to 46 of 64, or 64 to 72 percent** |

**The correction.** Section 3.3 budgets 6.0 hours for "scripting on both
platforms including system administration automation". That figure assumes
teaching a second language's syntax. Under the singular reading of topic 6 the
course teaches one language and runs it in two places, so roughly 3.0 hours
covers the platform differences, path and permission handling, and the second
run environment. The automation content stays; only the second syntax goes.

It fits with room. The free margin after review and final assessment is roughly
**10 to 15 hours**, and Windows provisioning still has to come out of it or be
funded separately.

**A contact-hour question has to be settled first.** Alvin College publishes
ITSE 1359 as 2 lecture plus 2 lab. The Alamo District course inventory codes it
**(3-3-1)**, which is 48 lecture and 16 lab. Both total 64 contact hours, but the
second halves the lab budget, and the CAE-CD document requires hands-on coverage
for every KU except one. Under 16 lab hours, the proctored authoring,
cross-platform work and regex practice alone consume 12 of 16.

### D.4 Cost

**Zero net semester credit hours**, on the same swap section 6 already
identifies: ITSC 2325 Advanced Linux out, ITSE 1359 in. The plan stays at 60,
which is the statutory ceiling.

**One consequence of that swap must be written down rather than discovered.**
With ITSC 2325 gone, element 2 permissions and the Linux half of element 6 rest
on ITSC 1316 Linux Installation and Configuration alone. ITSC 1316 is already
required in Semester I, so naming it as a second carrier costs nothing and keeps
the count at two, well inside the four-carrier dilution warning.

### D.5 Conditions, if this option is chosen

1. **Require the same scripts to run on both Windows and Linux, and evidence it.**
   Topic 6 reads "Scripting **language** on both Windows and Linux". The noun is
   singular, so the requirement is one language demonstrated on two platforms,
   not two languages. Python satisfies it, and so would PERL or Java. Set two
   graded artifacts: a system administration script executed on Linux and one
   executed on Windows, each with its own run evidence. Some bash remains useful
   for Linux administration idiom, but bash is not what satisfies this topic.
   The cost is provisioning a second platform, not teaching a second language.
2. **File the augmented outcomes in the college master syllabus**, not an
   instructor's term syllabus. Adopt the three WECM outcomes verbatim and add
   locally authored outcomes for regex and for cross-platform system
   administration. This is what stops a future instructor silently dropping them.
3. **Settle the contact-hour split with the district before writing the memo.**
4. **Name an owner and a budget for the Windows environment.** The 26-hour
   estimate explicitly excluded provisioning a second operating system, and it
   is still unfunded.
5. **Decide the prerequisite question in writing.** El Paso, Austin, Dallas and
   both Alamo sibling campuses all prerequisite this course. NLC would be filing
   it without one, and a reviewer can see that.
6. **Do not claim ITSE 1359 can serve as ITSY 1377's Python prerequisite.**
   ITSY 1377 runs in an 8-week Flex session; a 16-week course cannot gate it in
   the same term.
7. **Budget 3 to 4 hours of proctored authoring**, not 2.0, split into a Linux
   practical and a Windows practical, each written from a blank file.
8. **Get a written curriculum-office opinion** that the enhanced description
   passes the WECM Protocol Manual's test that local additions "must not be so
   extensive that they result in a substantially different course".

### D.5a A reading that was considered and rejected

An adversarial review of this option argued that topic 6 needs two scripting
languages, bash for Linux and PowerShell for Windows, on the grounds that if one
cross-platform language counted then "every Python course in the country would
satisfy element 6 for free". That reading was checked against the primary source
and rejected. A reviewer may raise it, so the answer is recorded here.

- **The noun is singular.** "Scripting **language** on both Windows and Linux".
  A two-language requirement would read "languages", or "a scripting language on
  each of".
- **Half the example list is cross-platform.** PERL, Python and Java are named
  alongside BASH, VB Scripting and PowerShell. A list intended to pair one
  Windows language with one Linux language would not lead with three portable
  ones.
- **The document writes per-platform requirements when it means them.** Topic 2
  of this same KU reads "Permissions (e.g., Linux, Windows, MacOS)". Topic 6 is
  not written that way.
- **PowerShell appears exactly once in the whole document**, in this parenthesis.
  It is required by no KU, no outcome and no topic.

- **Texas treats a PowerShell course as a local addition, not a standing
  requirement.** The one PowerShell course found in the WECM inventory, Dallas
  College's ITMT 1370 Powershell Scripting, is published as "a Local Need Course
  and a WECM Course Number" (A12). Local Need is the category for a course a
  single district needed and the state never adopted; it carries a 7 in the third
  digit of the number. Its description ("basic data types, control structures,
  regular expressions, input/output, and textual analysis") is the ITSE 1359
  pattern with one language swapped in, which is what a local variant looks like.
  If Windows scripting were an expectation the state held for this content area,
  it would have a statewide record, and it does not.

  Stated carefully: this is not a proof that no such statewide course exists
  anywhere in the inventory, which is a negative that would need an exhaustive
  search to establish. It is the result of looking, and finding that the closest
  match is local.
- **The "free for every Python course" objection is empirically wrong.** Most
  Python courses never require execution on a second platform. Requiring and
  evidencing it is the distinguishing work, and it is what this condition asks
  for.
- **Windows competence is carried elsewhere.** Operating Systems Concepts
  outcome 4 is "Install, configure, and harden operating systems in a virtual
  environment", against topics naming "Linux distros, Windows". Windows belongs
  to OSC, not to BSP.

### D.6 The two questions that gate both options

Neither is answerable from inside this repository, and both cost one email.

1. **What carries BSP in the college's currently validated CAE-CD program of
   study?** It is named nowhere in these documents. Everything else waits on it.
2. **Does removing ITSC 2325 endanger Operating Systems Concepts?** OSC is a
   Technical Core KU and ITSC 1316 would become the plan's only OS carrier. This
   applies equally to section 6's recommendation and to this one.

A third, specific to choosing between them: **what are ITSC 1342's actual WECM
end-of-course outcomes?** The main analysis could not retrieve them, and neither
could four reviewers. If they name data structures, types or libraries rather
than only shell mechanics, section 6's recommendation gets considerably stronger
and this addendum becomes the second choice rather than the first.

### D.7 Recommendation

**Prefer ITSE 1359 over ITSC 1342**, subject to D.5 and D.6, for one reason that
outranks the others: it is the only option that covers regular expressions from
a statewide course record, and regex is one of the two elements the analysis
scores as an absolute zero.

Both options carry roughly six of eighteen elements from their state records and
rest the remainder on local text. Neither is evidentially clean. ITSE 1359 is
preferred because the twelve elements it leaves to local authoring are ordinary
introductory programming content that any competent syllabus covers, while the
elements ITSC 1342 leaves out are the ones the analysis has already identified
as hardest to defend.
