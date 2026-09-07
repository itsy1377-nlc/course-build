# Template conflicts and how this build resolves them

Phase 1 blueprint, item 8. Agentic AI and Security Operations, ITSY 1377.
Prepared 2026-09-03 for the program manager.

## What this document is

The college ships an online course template. The build prompt for this course
sets its own rules. In 32 places the two ask for different things. This
document lists all 32, says which one wins in each place, and says what the
build actually does. Two more were found later and are listed as 33 and 34.

One rule settles most of them. Structure and presentation follow the template.
Content and assessment follow the build prompt. Where that rule does not
settle a question, the question goes to the program manager or to the college.
Nothing here was resolved silently, and every resolution can still be changed
before the course is built.

One term used in the table below is defined in the alignment matrix, section 1,
and is not repeated here: a **Bloom level**, and the *Bloom verb* that carries
it, names how demanding a thinking task is.

The numbers 1 to 32 are the numbers used in section 9 of the template
conformance spec, so the two documents can be read side by side. Items 33 and
34 came out of testing the target Canvas instance in Phase 0.

The last column says who decides:

- **Build.** The build has decided. No approval is needed.
- **PM.** The program manager confirms.
- **College.** Only the college can answer. Carried into the gaps section.

---

## 1. Module anatomy and page structure

### The eight parts and the six items

The prompt names an eight-part weekly page template. The template names six
module items. The eight parts fit inside the six items with nothing invented
and nothing left empty. Every week from 1 to 7 uses this identical set, in
this order.

| Prompt part | Template item it lives in | Block it uses | Note |
|---|---|---|---|
| Overview | Page: Module N Overview | Introduction block | Also holds the 2 to 4 minute overview video |
| Objectives | Page: Module N Overview | Learning Objectives block | Numbered 1.1 to 1.3, each ending in its parent CLO |
| Read/Watch | Page: Module N Content | First topic block | Holds the authored reading and the walkthrough video |
| Sidebar | Page: Module N Content | Second topic block | Links the ungraded sidebar notebook |
| Lab | Assignment | Introduction and Directions blocks | Links the starter notebook |
| Discussion | Graded discussion | Introduction and Directions blocks | |
| Submit | Assignment, and the discussion | How to Submit block | A block, not a page of its own |
| Check Yourself | Classic quiz | Introduction and Directions blocks | The weekly low-stakes self-check |

Four template parts have no counterpart in the prompt's list. All four are
kept and filled:

| Template part | What this build puts in it |
|---|---|
| Tasks table, on the Overview page | Every activity for the week, its objective, its estimated time, its due date |
| Sources block, on the Content page | The citations for that week's authored reading |
| Grading Criteria block, on the assignment and the discussion | The rubric in plain words, so a student reads it before submitting |
| Page: Module N Wrap-up | What You Learned, What You Did, What's Next |

Two costs are worth naming. The first is a click, and Phase 2 spent it the
other way. Each weekly module holds eight items, not six: the six above plus
the sidebar notebook and the lab notebook, added beside the pages rather than
linked from inside them. The template's page set is unchanged and every page
is still filled. A course whose work happens in a notebook should not put a
page between a student and the notebook seven weeks running, which is the cost
the original resolution named and accepted. See the amendment to conflict 1 in
section 8.

The second is time. The Wrap-up page is a part the prompt never asked for. It
is short, about 2 to 3 minutes to read. That time is counted inside the 30
minutes the prompt already gives to the self-check and submission.

### Conflicts in this group

Six conflicts sit here. Each row gives the number used in the conformance
spec.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 1 | Four page kinds in a fixed order: Overview, Content, assessment items, Wrap-up. Overview carries a Tasks table; Content carries a Sources block. | One identical weekly page template of eight parts: Overview, Objectives, Read/Watch, Sidebar, Lab, Discussion, Submit, Check Yourself. | Template. Page structure is structure. | The eight parts fold into the template's six items, as mapped above. Submit becomes a block, not a page. The Tasks table, the Sources block and the Wrap-up page are kept and filled. | Build |
| 2 | Modules named `Module [Insert #]: [Insert Topic and Dates]`; pages named `Module [#] Overview` and so on. | One module per week, named for the week. | Template. Naming is presentation. | Modules read `Module 5: The Agent Loop`. Page titles keep the template pattern. The week is named on the Overview page and in the schedule. Dates go into the title per section, once the term calendar is known; the build has no term dates. | PM |
| 3 | Six modules ship: Faculty Resources (unpublished), Orientation, Student Resources, Respondus, Q & A, and one weekly module to duplicate. | Start Here, week 0, and weeks 1 to 8, all published from day one. | Split. The template governs which institution modules exist; the prompt governs the course's own modules. | The course has Orientation, Student Resources, Q & A, Module 0, and Modules 1 to 8. Faculty Resources is not created; it is author-facing. Respondus is not created (item 10). Every module that is created is published. | College, for item 10 |
| 22 | Objectives numbered 1.1, 1.2, 1.3 under "By the end of this module, you will be able to:", each starting with a Bloom verb. The Tasks table has no column for a parent course objective. | Two or three weekly objectives, each tagged with its parent CLO, 20 words or fewer, one measurable verb, banned verbs excluded. | Template for the numbering and the lead sentence. Prompt for the wording and the tag. | The numbering and lead sentence stay. Each objective ends with its parent in brackets, such as (CLO3). The Tasks table keeps its three template columns and gains a fourth, Estimated time, because the prompt puts a time on every activity. The weekly total is one sentence under the table. | Build |
| 26 | The Discussion, Quiz and Assignment templates ship published, with placeholders, inside the weekly module. | All modules published from day one. | Prompt. What a student reads is content. | No placeholder item is copied. Every item is created through the API with finished text. The removal checklist in section 5 of the conformance spec is run against every page before it is published. | Build |
| 27 | The module anatomy assumes a Content page and graded assessments. | Week 0 is optional and ungraded. Week 8 is the final exam with no new instruction. | Prompt. What is taught and graded is content and assessment. | Module 0 uses Overview, Content (the on-ramp), the self-assessment in the quiz slot as an ungraded practice quiz, and Wrap-up. It has no discussion and no assignment. Module 8 uses Overview, the final exam quiz, and Wrap-up. It has no Content page, since that page would sit empty or add instruction the prompt forbids. | Build |

#### Amendment to conflict 27, recorded in Phase 2

Module 0 ships the four items conflict 27 named. It briefly shipped three, with
no Wrap-up page, and `content/AUTHORING.md` had been rewritten to describe the
three. Both are corrected. `content/pages/week-0-wrap-up.md` carries What You
Learned, What You Did, a short Check Yourself and What's Next, and
`content/course.yaml` lists it after the on-ramp notebook. A student who scores 9
or 10 on the self-assessment and skips the notebook now still meets a "what is
next" step in Canvas.

One page is added to the Orientation module at the same time: **If something
breaks**, carrying the five step routine and the six error table that open the
on-ramp notebook. It is added under the same rule as the three added items in
conflict 4. The prompt's Start Here list requires a help path for a lab that will
not run, and no template page covers one. Whether each weekly module also links
that page is not settled. `week-00-outline.md` open question 3 carries it, and no
weekly module links it today.

---

## 2. Required orientation pages

Seven conflicts sit here. The module keeps its template name and page order,
and gains three items the prompt requires.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 4 | A module named "Orientation Module" opening with "Welcome! Start Here:", holding ten fixed items. | A "Start Here" module holding: how the course works, the week 0 self-assessment, how to get help (including a dead notebook kernel, a timed-out session, and the API key), the AI use policy, and the syllabus with an acknowledgment. | Template for the module name and page set. Prompt for the five contents. | The module keeps the name "Orientation Module" and the template's page order. The Welcome page carries how the course works, the build arc, what persists between weeks, and what to do after a bad week. Three items are added, because no template page covers them: a Course Syllabus page, a Syllabus Acknowledgment (ungraded practice quiz), and a Notebook and API Key Help page. The AI use policy is its own page (item 7). The week 0 self-assessment gets a fifth Getting Started step on the home page and a callout on the Welcome page. | PM, for the three added items |
| 5 | Four completion requirements on the Orientation module, and a home page sentence saying students must finish orientation to reach the next module. The export implements no lock. | No completion requirements, no module prerequisites, nothing locks. | Prompt. Locking decides who can reach an assessment, so it is an assessment question. The template's own export does not implement the lock either. | No requirements, no prerequisites, no lock dates anywhere. The home page sentence is removed, because in this course it would be false. | College |
| 11 | A pinned, ungraded, course-wide Q & A board in its own module. | Names a help path but neither requires nor forbids a board. | Template. There is no conflict of substance. | Kept as shipped, ungraded and pinned. It gives students a public place to ask why a notebook stopped working, which suits an asynchronous course. One wording error copied from the introductions board ("type your introduction") is corrected. | Build |
| 16 | The Syllabus tab is hidden, the syllabus body is empty, and the home page sends students to a "Course Syllabus" item in the left menu that is an external tool. No acknowledgment activity. | Syllabus and a syllabus acknowledgment in Start Here. The syllabus states the token budget policy and the AI use policy. | Prompt for the content. Template for the placement and the hidden tab. | The syllabus is a Canvas page in the Orientation module titled Course Syllabus. It carries the six CLOs, the grade weights, the prerequisite, the token budget policy, the AI use policy and the course week. The Syllabus tab stays hidden. The acknowledgment is an ungraded practice quiz with one item, so no weight changes. On the target instance the external syllabus tool does not exist, so the home page points at the page instead. | College |
| 23 | Textbook images, author, publisher, edition, ISBN, bookstore details, and a required statement that students need not buy from the college bookstore. | No textbook. Readings are authored and live in the course. | Template for the page. Prompt for what the page says. | The page is kept and says plainly that the course needs no textbook and no purchase. It lists what students do need: a browser, an internet connection, and the hosted notebook environment. The bookstore statement is kept word for word. | College |
| 31 | The home page ends the online-class paragraph by sending students to "Using Zoom as a Student" for attending class remotely. | The course is fully asynchronous and has no meetings. | Prompt. A sentence that is untrue is a content error. | The sentence is removed. The Zoom page itself stays in Student Resources, because the college supplies it to every section. | College or instructor |
| 32 | First-person text by the template's author, including a personal story about failing a class, plus third-party video embeds. | Instructional prose at or below 7th grade, measured per page. External links openly licensed, attributed, and verified to resolve. | Split. Template for the page and its four headings. Prompt for the words. | The page keeps its four headings (Effort, Failure, Time Management, Study Skills) and is rewritten in the second person at the course reading level. The personal story goes. The uploaded study skills handout stays. A video embed stays only if the link check passes and the license is clear. | PM |

---

## 3. Third-party tools and services

The prompt's rule is strict: zero external services is the target, and any
unavoidable one must permit users aged 13 and up, cost nothing, need no
account holding personal information, and come with a cited terms-of-service
clause. Three template items cannot meet that rule. None of the three is a
course design choice, so the build states what it does and hands the decision
to the college.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 9 | A 1 point external-tool assignment that enrolls each student in a biometric identity check, with a must-submit requirement, plus a vendor row in the privacy table. | Zero external services. Any unavoidable one needs no account holding personal information, and its terms clause must be cited. | Prompt for this course's own design. College for an institution-wide requirement. | This build does not create the BioSig page or assignment. A biometric password is personal information, so no clause can be cited that satisfies the prompt, and nothing here depends on verified identity: the exam is open book and unproctored. If the college requires identity verification in every online section, the page and assignment are copied from the template without change, the point goes in a 0 percent assignment group, and the risk register carries the privacy note. | College |
| 10 | A module telling students to download and install a locked testing browser, and a 1 point practice quiz that requires it, in its own assignment group. | The final exam is open book, online, and unproctored. Students have a computer, internet and a browser, nothing else, with no local installs and no admin rights. | Prompt for this course's exam. College for the institution requirement. | The build does not create the Respondus module, and the final exam leaves the lockdown setting off. A required desktop install would shut out any student on a borrowed or managed machine, and it buys nothing for an open book exam. If the college requires the module in every online section, it is copied as shipped, its practice quiz goes in the 0 percent group, and the final still does not require the browser. | College |
| 12 | Students new to online courses must complete a free orientation mini-course, and the instructor checks for 80 percent or better in the first week. | Names one enforced prerequisite, the AI fundamentals course, and does not mention this requirement. | College. This is an enrollment rule, not a course design choice. It is also a college-run Canvas course rather than an outside service, so the zero-external-services rule does not reach it. | The page is kept word for word. Nothing in this course is graded on it. The instructor's duty to check the result in week 1 moves into the instructor guide. | College |
| 18 | Students must save files in .doc or .docx with a named desktop word processor, edit its formatting, upload writing assignments in that format, and use Zoom for office hours. | A browser is the only tool. Every submission is a screenshot, one exported .txt or .json file, and 3 to 5 sentences in a text box. | Prompt. The list describes what students must be able to do in this course, which is content. | The browser paragraph and the paragraph about technical difficulties stay word for word. The skills list is rewritten to this course's real submissions: take a screenshot and save it, download the file the notebook writes, upload both, type in a text box, post and reply in a discussion, and find due dates and rubrics in Canvas. No word processor is named. The Zoom line stays only if the instructor holds Zoom office hours. | PM, with the instructor |
| 19 | Institution pages embed videos from public platforms and a walkthrough vendor, link a citation generator, an online tutoring service, a plagiarism service and a conferencing service, and list sixteen vendors in a privacy table. | Zero external services is the target, and anything linked out must be openly licensed, attributed, and verified to resolve. | Split. The prompt's rule is written for course content the build authors. The support pages are institution content the college supplies to every section. | The seven Student Resources pages are kept as they ship, with their vendor links and the privacy table. No graded activity in this course requires any of them. Every link on every kept page is checked before publishing, and any that fails is reported rather than quietly repaired. The licensing rule is applied in full to the readings, videos and links this build writes. | PM |

---

## 4. Assessment and grading

Nine conflicts sit here. This is where the prompt governs most often, because
grading and integrity are assessment.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 6 | "I do NOT accept late work", plus a statement that Canvas locks activities after the deadline. | Nothing locks. The late and resubmission policy is not yet set. A student who runs out of tokens gets a top-up with no grade penalty and no late penalty. | Prompt for the lock and the token clause. College for the penalty. | The Late Work panel stays and its text is rewritten to what is true here: work is due Sunday at 11:59 PM, nothing locks, late work can still be submitted, and a token top-up costs no points and no time. The size of the late penalty is left open until the college sets it. | College |
| 7 | Students may not use AI tools unless an assignment authorizes them in writing. Faculty may run detection software, a flagged student must show drafts and revision history, and a violation scores zero. | Students will use AI on this work. Write a course policy that permits it with disclosure. | Prompt for the course policy. The district text is quoted, never rewritten. | The district panel stays word for word. Its own clause lets an assignment authorize AI use in writing, so this course exercises that clause. A separate AI Use Policy page permits AI use with disclosure, and every lab and discussion repeats the authorization in its Directions block. Two points go to the college: whether detection software runs on a course that requires AI use, and how a student shows original work when the tool is the subject. | College |
| 8 | The introductions board is graded at 1 point in the Assignments group and is required for module completion. | Discussions are 12 percent of the grade and are tied to that week's lab results. Weights total 100. | Template for keeping the board. Prompt for the weights. | The board is kept and graded at 1 point, in an Orientation assignment group weighted 0 percent. A 0 percent group adds nothing to the final grade, so the four weighted groups still total 100. The 12 percent divides across the seven weekly boards only. The must-contribute requirement goes with all other completion requirements (item 5). | Build |
| 13 | Two assignment groups at zero weight with equal weighting. Two letter schemes, neither enabled: A/B/C/D/F at 90, 80, 70, 60; and an "LC" scheme of A, B, C at 74, and IP. | Labs 60, final exam 20, discussions 12, self-checks 8. No letter scheme named. | Prompt. | Five assignment groups: Labs 60, Final Exam 20, Discussions 12, Self-Checks 8, Orientation 0. Group weighting is set to percent. **This course uses the standard A/B/C/D/F scheme at 90, 80, 70 and 60, and enables it.** The LC scheme with the IP mark belongs to developmental courses, not to a 3 SCH ITSY course. The points inside each group, item by item, are in the grade distribution and token totals document. | PM confirms the scheme |
| 14 | Five account-derived Critical Thinking outcomes plus "Student Degree Pathway", all attached to a zero-point rubric whose criteria are ignored for scoring. | Six Canvas Outcomes, one per CLO, one mastery scale, each linked to the rubric criterion that measures it. Check for account-level outcomes first. | Prompt. Outcomes are assessment. | The build creates six course-level Outcomes, one per CLO, on one mastery scale. Phase 0 checked the target instance: the account has no outcomes at any level, so there is nothing to link to and the six must be course-level. **The five Critical Thinking outcomes and their zero-point rubric are not recreated.** They came from another instance's account, they measure nothing this course assesses, and Student Degree Pathway is a demographic tag rather than a skill. | College. See the note below |
| 15 | Discussion rubrics with three criteria and three levels, no outcome links, and an interaction criterion asking for 2 to 3 posts a week, or one post to a peer and one to the instructor. | Three to five criteria, three to four levels, explicit points, each criterion linked to its Outcome, all gradeable without running student code. | Template for the shape. Prompt for the criteria and the links. | The template's three criteria and three levels fit the prompt and are kept as the shape. The build writes its own criteria, links each to its CLO Outcome, and allows one unlinked criterion for submission completeness. The template's interaction wording is not used. This course asks for one post and one substantive reply, inside 15 to 20 minutes. | Build |
| 20 | The course week runs Monday to Sunday, with everything due Sunday at 11:59 PM Central. | Due dates are set per week. No day or time zone named. | Template. | Adopted as written. Every weekly due date is Sunday at 11:59 PM Central. | Build. Term dates still needed |
| 21 | Messages answered in 24 to 48 hours, not counting weekends and holidays. Grades and feedback within one week of the due date. | A stated feedback turnaround commitment on labs, with no number given. | Template supplies the number the prompt asks for. | Adopted as written, and repeated on the lab pages. In an 8 week session, one week means week N feedback arrives while week N+1 is being built on top of it, so the instructor guide names labs as the grading priority. | PM confirms it is workable |
| 30 | A weekly announcement that also wraps up the prior week, plus a welcome email or a 1 to 2 minute welcome video before the term. | A weekly announcement, drafted and ready to send, that previews the week and names the common sticking point. | Both fit in one announcement. | Each of the seven weekly announcements opens with two sentences closing the prior week, then previews the week and names the sticking point. A week 0 welcome announcement is drafted too. The welcome video is the instructor's to record; the build supplies the script. | PM |

### Note on item 14, which has a real cost

Canvas allows one rubric per assignment. If the college collects Critical
Thinking outcome data from every course, that zero-point rubric cannot simply
sit beside a lab rubric on the same assignment. There are two ways out, and
neither is free.

The first is to add the five criteria, ignored for scoring, inside one week's
rubric. That pushes the rubric to eight or ten criteria, past the prompt's cap
of five, and makes a lab rubric harder for a student to read.

The second is to create one 0 point item in the Orientation group whose only
job is to carry the rubric. That adds an assignment students must submit to
for no credit, in a course whose whole submission design is meant to be
trivially easy.

The prior question is whether the data is collected at all. That is the
college's to answer, and it is in the gaps list.

---

## 5. Navigation and settings

Four conflicts sit here. Three of the four are settings a template shell
carries that a live section should not.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 17 | A student menu of Home, Announcements, Modules, Discussions, Grades, plus eleven institution tools. Syllabus, Assignments, Quizzes, Pages, Files, People, Outcomes, Rubrics, Conferences and Collaborations are hidden. | Conform to the template's navigation. The course depends on outcome reporting, Classic Quizzes, and rubric-graded assignments. | Template. Navigation is presentation. | The visible set is matched exactly. Hiding a tab hides it from students; it does not turn the feature off, so outcome reporting, quizzes and rubrics all still work for staff. Files stays hidden and corpus files are linked from the pages that use them, which the Phase 0 download test confirmed works. | Build. See item 34 |
| 24 | Public visibility, public to authenticated users, open enrollment and self enrollment are all switched on. | Silent on visibility. | The prompt's content rules decide it by consequence: the course carries a phishing corpus and student work. | All four are switched off. The template's values suit a shell that faculty copy, not a live section. | PM confirms |
| 25 | A Creative Commons Attribution NonCommercial ShareAlike license, in the manifest and in course settings. | Lists course ownership and licensing as unresolved. | Neither. This is an ownership question, not a design question. | The license is left at the Canvas default, private and copyrighted, until ownership is settled. Setting a Creative Commons license would grant rights this build has no standing to grant. | College |
| 29 | A Common Cartridge export carrying nine unrelated question banks, nine unrelated rubrics, five outcomes and a faculty module. | "Create a new course in Canvas via the API." | Prompt. | The course is built through the API from scratch, reproducing the template's structure from the conformance spec. Institution text that must stay verbatim is copied from the template files word for word. Nothing unrelated comes across, so no cleanup pass is needed. If the college requires the cartridge to be imported and edited instead, the build order changes and the leftovers must be deleted after import. | College |

---

## 6. Accessibility

One conflict sits here, and it is a real one.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 28 | Institution pages as shipped, which carry an untitled iframe, a link whose only content is a screen-reader span, a link that goes to `#`, an empty heading wrapped around an image, fourteen stacked line breaks, headings nested inside panel bodies, and 59 uses of a scanner-suppression class. | Zero errors in the Canvas Accessibility Checker, WCAG 2.2 AA, semantic HTML, correct heading order, alt text, table headers, and descriptive link text. | Prompt. Accessibility is a legal obligation, and fixing markup does not change what a page says. | Every page is authored fresh from the template's markup patterns with the known defects fixed: a title on every iframe, no empty and no "#" links, no empty heading, no stacked line breaks, headings in order, the aria-hidden attribute on the two icons that lack it, and the suppression class used nowhere. Institution text is kept word for word; only the markup around it changes. Placeholder highlighting and red placeholder text cannot survive, because no placeholder is copied. | College. See the question below |

The college question here is narrow. When the template says an institution
page is kept verbatim, does that mean the words or the HTML? This build reads
it as the words. If it means the HTML, the zero-error target cannot be met on
those pages, and the QA report will say so.

---

## 7. Found after the conformance spec was written

Two items, both facts about the Canvas instance rather than differences of
opinion between the two documents.

| # | Template requires | Build prompt requires | Which governs, and why | Resolution | Decision |
|---|---|---|---|---|---|
| 33 | Every page uses DesignPLUS markup: wrappers, content blocks, collapsing tab and accordion panels, callout cards, a link grid, buttons and icon fonts. | Conform to the template's page structure and styling. | Both, as far as they can. The target instance has no DesignPLUS theme installed, so the classes carry no styling and the pages render as plain HTML. | Every class is kept exactly as the template writes it, so the pages are right the moment the theme is installed and the block names survive either way. Every page is also written to read correctly with no styling at all. Panels become stacked sections with their headings intact. Lead sentences such as "select each tab below to expand" are replaced with wording that is true with or without the theme. No meaning is carried by a card, a color or an icon. Icons stay as hidden elements, which render as nothing. | College |
| 34 | Eleven institution external tools in the student menu, one of which is the Course Syllabus item the home page tells students to click. | Build the course on the named Canvas instance through the API. | Neither. This is a fact about the instance. | The target instance is a test instance and has none of those tools installed, so the menu shows only the built-in tabs. Page text that points at a tool which is not there would be wrong, so the home page points to the Course Syllabus page in the Orientation module instead. Moving the course to the college's production instance restores the tools and may mean changing that sentence back. | College |

---

## What only the college can answer

These are carried into the blueprint's gaps section. The first three are the
ones that change what gets built.

1. Is identity verification required in every online section, and must this
   course carry it? The build leaves it out. The exam is open book and
   unproctored, so nothing here depends on it.
2. Is the locked testing browser module required in every online section? The
   build leaves it out. Some students have no rights to install software on
   the machine they use.
3. Does the college collect Critical Thinking outcome data from every course?
   If it does, which item carries the zero-point rubric, given that Canvas
   allows one rubric per assignment?
4. May a course authorize AI use with disclosure under the district AI
   procedure, and will AI detection software be run on a course that requires
   students to use AI?
5. What is the late work penalty, and does the college require anything to
   lock after a deadline? The build locks nothing.
6. Is the external syllabus system the record of truth? If it is, does the
   Canvas syllabus page repeat it or replace it?
7. Must the Orientation module gate access to later modules? The template's
   home page says it does; the template's own export does not implement it.
8. Is the free online-learning orientation mini-course still required this
   term, and does the instructor still check the post-test result in week 1?
9. Does the college's production Canvas instance have the DesignPLUS theme
   installed, and which institution tools sit in its course menu?
10. When an institution page is kept verbatim, does that mean the words or the
    HTML? Fixing the template's accessibility defects changes the HTML.
11. Is the course built through the API from scratch, which is the current
    plan, or by importing the template cartridge and editing it?
12. Who owns this course, and under what license does it ship?
13. Is the bookstore statement required on a course that assigns no textbook?
14. What are the term dates for the 8 week Flex session, so module titles can
    carry dates the way the template asks?


---

## 8. Amendments recorded in Phase 2

Phase 2 built the Orientation module, Student Resources, the Q & A board and
Module 0. Eight resolutions above changed while that was built, or were found
to describe something the build had not done. Each one is recorded here rather
than corrected in place, so the two versions can be read side by side.

### A. Conflict 1. The weekly module holds eight items, not six

The two notebooks are module items. The reason and the cost are in the rewritten
paragraph in section 1 above. Nothing about the template's page set changes:
Overview, Content, the three assessment items and Wrap-up all exist and are
filled. `content/pages/how-to-navigate-canvas.md` tells students the same
eight. Module 0 carries four items on the same rule, which the amendment to
conflict 27 already records. **Decision: Build.**

### B. Conflict 2. Modules take the template's names. Item titles do not

`content/course.yaml` had named the modules for the week, which contradicted
this item, `week-00-outline.md` and assumption A12. The modules are renamed to
the template's pattern: `Module 0: Programming On-Ramp` through
`Module 8: Final Exam`, with `Orientation Module`, `Student Resources` and
`Q & A Community` named as the template names them.

Page and item titles inside a module do **not** take the template's
`Module N Content` pattern. They say what the item is: "Week 1 reading",
"Week 0 self-assessment", "Syllabus, policies and grades".

The reason is that everything else in this course speaks in weeks. Every due
date, every schedule row and every discussion prompt does. A student should not
have to turn a module number into a week number to find what is due.

The mapping is stated twice, where a student meets it. The course schedule page
and the navigation page both say that Module 1 is week 1. **Decision stays PM.**
This is the half of the item the program manager should look at hardest.

### C. Conflict 3. Student Resources and Q & A now exist in the spine

Both modules were resolved as kept and neither was built. Both are now in
`content/course.yaml`, in the template's order: Orientation Module, Student
Resources, Q & A Community, Module 0, Modules 1 to 8.

Four of the template's seven Student Resources pages are authored for this
course. They move out of the Orientation module and into this one. They are How
to Navigate Canvas as a Student (built as "Finding your way around"),
Communicating Online, Academic Integrity, and Canvas and Tech Support.

The other three are institution pages this build does not author. They are Using
Zoom as a Student, Academic & Student Support Resources, and Uploading a Paper
to Turnitin Using Canvas. Item 19 keeps them as they ship. They are not in the
spine, and that gap is in the open questions below.

### D. Conflict 11. The Q & A board is built

`content/discussions/qa-board.md`, ungraded and pinned, in the Q & A Community
module. The template's "type your introduction" wording is corrected to "type
your question". The builder gained support for an ungraded discussion, which
carries no assignment, no group and no points. An ungraded board also does not
require an initial post, because a student reading the board to find an answer
should not have to post one first.

### E. Conflicts 12 and 23. Both institution pages are built

`content/pages/olrn-0001.md` and `content/pages/course-material.md` exist. Each
keeps its institution statement word for word in a block quote, and the rest of
each page is written at the course reading level.

- The bookstore statement is kept word for word on the Course Material page.
  The course material page says plainly that there is no textbook and nothing to
  buy, and lists what students do need.
- The OLRN page keeps the enrollment requirement, the "1 to 2 hours" and the
  "80 percent or higher on the post-test" figures, and the two college contacts.

Four links in those two template files were checked. Three resolve: the OLRN
student page, the district registration page, and the college bookstore page.
The bookstore's separate online store answered the check with HTTP 403.

One of the four is carried, the OLRN student page. It is the only one a student
here has to open. Neither page needs the other three. This course assigns no
textbook, and the two college phone numbers reach a person faster than a
registration tutorial does.

### F. Conflict 16 and template item 5. Course Evaluation is folded into the syllabus

The template's Course Evaluation page is not created. Conformance section 4.6
says that page is where the template expects the grading breakdown. In this
build the grading breakdown is on the syllabus page,
`content/pages/course-policies.md`, which already carries the four weighted
groups, the points per item and the letter scale. Two pages holding one grade
table is how the two numbers drift apart. **Decision: Build.**

### G. Conflicts 4, 31 and 34. The home page is built

`content/pages/home.md` is built and set as the course front page, and
`course[default_view]` is `wiki`, which is what the template sets. It carries
the welcome, the catalog description, the delivery paragraph for a course with
no meetings, the instructor contact block, the template's four Getting Started
steps and the fifth step this build adds for the week 0 self-assessment.

Two template sentences are not carried, as those items resolved: the sentence
sending students to Zoom for attending class remotely (item 31), and the
sentence saying the Orientation module must be completed before the next module
opens (item 5). The syllabus step points at the Course Syllabus page rather than
an external tool that the target instance does not have (item 34).

`content/pages/meet-your-instructor.md` is built at the same time, as the
template's second Orientation item. It carries the contact channel, the reply
time, the feedback turnaround and what the instructor does each week. It carries
no instructor name, email address, photo or contact hours, because the build
does not know them and a placeholder is not allowed. That is in the open
questions below.

### H. Conflict 13. The letter scheme and the course description are applied

`course.yaml` declared `default_view`, `description_page` and the A/B/C/D/F
scheme. The builder read none of the three. They looked applied in the
repository and were absent in Canvas.

`build_course.py` now creates the grading standard at 90, 80, 70 and 60 and sets
it on the course. It also sets `default_view`, sets the front page, sets the
catalog description as `public_description`, and renders the syllabus page into
`syllabus_body`.

The letter table students read on the syllabus page is now the table Canvas
applies. `--verify` checks all of it and fails if any of it is missing.

The catalog description states the enforced prerequisite, which the build prompt
requires the course description to carry.

### Open questions this amendment adds

1. **Who is the instructor, and what are the contact hours?** The Meet Your
   Instructor page and the home page instructor card both want a name, an email
   address and contact hours. The build has none of the three and wrote none of
   them. They go in when the section is assigned.
2. **Are the three unbuilt Student Resources pages copied in?** Using Zoom as a
   Student, Academic & Student Support Resources, and Uploading a Paper to
   Turnitin Using Canvas. None is used by any graded activity here. The Zoom
   page conflicts with item 31 and the Turnitin page describes a submission
   type this course does not use.
3. **Does the program manager accept week-named items inside module-named
   modules?** Amendment B.
