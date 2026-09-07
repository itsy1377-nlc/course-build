# NLC Online Course Template: Conformance Specification

**Course:** Agentic AI and Security Operations (ITSY1377_builder)
**Purpose:** Let a builder reproduce the institutional template's structure, navigation, required pages, and styling without opening the template export.
**Source:** The Canvas Common Cartridge export titled "NLC-DLC Online Template" (Common Cartridge 1.1.0 with Canvas extensions, export date 2026-07-13), located at `NLC Online Course Template/` in the working repository.
**Companion document:** `builder/docs/build-prompt-v1.3.md` (the build prompt). Section 9 of this document lists every point where the build prompt and the template appear to conflict. It does not resolve them.

## How to read this document

- A **Common Cartridge** is a zipped export format for a Canvas course. Its `imsmanifest.xml` lists every resource; `course_settings/` carries course-level XML; `wiki_content/` carries pages as HTML; discussions, assignments, and quizzes are separate XML files.
- **DesignPLUS** is a page-authoring add-on for Canvas made by Cidi Labs. Its markup is identified by `dp-` class prefixes. The classes only render as designed when the DesignPLUS theme (its CSS and JavaScript, including the Font Awesome icon font) is installed on the target Canvas instance. Without it the pages still display as plain, valid HTML, but panels do not collapse and icon elements render empty. Confirm the target instance has DesignPLUS before relying on the interactive parts.
- Product names appear in this document only where needed to identify a template element. No hyperlinks, street addresses, phone numbers, email addresses, personal names, or Canvas-generated identifiers from the template are reproduced here. Where a page must be kept verbatim, the template file name is given so the builder can copy it from the source.
- Export placeholders in HTML snippets (`$WIKI_REFERENCE$`, `$CANVAS_OBJECT_REFERENCE$`, `$CANVAS_COURSE_REFERENCE$`, `$IMS-CC-FILEBASE$`) are Common Cartridge link tokens. When building through the Canvas API, replace them with course-relative paths (`/courses/:id/pages/:slug`, `/courses/:id/discussion_topics/:id`, `/courses/:id/files/:id/preview`, and so on).
- Canvas attaches `data-api-endpoint`, `data-api-returntype`, `data-course-type`, `data-published`, and `data-content-user-id` attributes to links and images when a page is saved in the editor. Those attributes are generated, tied to the source course, and are omitted from every snippet below. Do not copy them.

---

## 1. Module list and order

The template ships six modules. Positions, publication states, and item types come from `course_settings/module_meta.xml`. "Published" means `workflow_state` is `active`; the Canvas UI shows the same state as a green check.

| Pos | Module title (exact) | Module published | Items in order (type, published) |
|---|---|---|---|
| 1 | `Faculty Resources DO NOT PUBLISH THIS MODULE` | No | 1. How to Use This Layout (Page, unpublished) 2. Teaching Checklist-OnlineHybrid Education Courses (File attachment, PDF, unpublished; the item position is recorded as 3, so a middle item was deleted before export) |
| 2 | `Orientation Module` | Yes | 1. Welcome! Start Here: (Page) 2. Meet Your Instructor (Page) 3. Course Material (Page) 4. Course Policies, Expectations, and Student Privacy (Page) 5. Course Evaluation (Page) 6. Course Schedule (Page) 7. Tips for Success (Page) 8. OLRN-0001 is Required for this Course (Page) 9. BioSig Instructions and Practice Assignment (Assignment, external tool) 10. Introduce Yourself Discussion Board (Graded discussion). All ten items published. |
| 3 | `Student Resources` | Yes | 1. How to Navigate Canvas as a Student 2. Using Zoom as a Student 3. Communicating Online (title carries a trailing space in the export) 4. Academic Integrity 5. Canvas and Tech Support 6. Academic & Student Support Resources 7. Uploading a Paper to Turnitin Using Canvas. All Pages, all published. |
| 4 | `Respondus LockDown Browser` | Yes | 1. Download and Install Respondus LockDown Browser (Page) 2. Test Respondus LockDown Browser- Requires Respondus LockDown Browser (Classic quiz). Both published. |
| 5 | `Q & A Community` | Yes | 1. Q & A Discussion Board (Ungraded discussion, pinned). Published. |
| 6 | `Module [Insert #]: [Insert Topic and Dates].      (Module to be duplicated and pages MUST be edited)` | Yes | 1. Module [#] Overview (Page) 2. Module [#] Content (Page; title has a trailing space) 3. Discussion Template (Graded discussion) 4. Quiz Template (Classic quiz, zero questions) 5. Assignment Template (Assignment) 6. Module [#] Wrap-up (Page; title has a trailing space). All six published. |

Notes on the module list:

- Module 6 is the placeholder "to be duplicated." Its title says so in the title text itself. Every item in it carries bracketed placeholders and must be edited.
- The three assessment items in module 6 (Discussion Template, Quiz Template, Assignment Template) are published in the export even though the faculty guidance page says they "are unpublished and can be found on your Assignments page." Treat them as templates, not deliverables.
- The Orientation Module carries completion requirements in the export: `must_view` on Course Material, `must_view` on Course Schedule, `must_contribute` on Introduce Yourself Discussion Board, `must_submit` on BioSig Instructions and Practice Assignment. No module in the export declares a prerequisite on another module, and `require_sequential_progress` is `false` everywhere, so the requirements are recorded but nothing is locked behind them in the export itself. The home page text nonetheless tells students they must complete the orientation to reach the next module (see section 9).
- No module in the export is locked or date-restricted (`locked` is `false` on every module).
- The Respondus module is the only one whose XML omits `require_sequential_progress`; Canvas treats the missing value as `false`.
- There is no "Week 0" module, no final exam module, and no glossary or instructor-guide item in the template. The template supplies one generic weekly module pattern only.

---

## 2. Anatomy of a weekly module

### 2.1 What the template says a module is

From the faculty page "How to Use This Layout" (`wiki_content/how-to-use-this-layout.html`), quoted:

> "Each module is organized into four sections: 1. Overview page 2. Content page 3. Assignments (to be added by Instructor) 4. Wrap-up page"

> "This layout is built with 1 learning module for you to customize and copy for your remaining course modules."

> "How many modules your course will ultimately have will depend on the duration of the course and how you choose to divide your content. For example, a 8-week course would likely have an Orientation Module and then eight weekly modules."

Its per-page recommendations, quoted:

> **Overview Page.** "The overview provides an orientation for the material to be learned. This is the guiding light for the module. You provide a brief narrative about the specific topic under study in the module. State your learning objectives. List the tasks the students are responsible for completing in that module."

> **Content Page.** "This is a page where you would put any course readings, class notes, videos, or links to material/ content/ to be learned. (You can think of this as your 'lecture' content)."

> **Assignments.** "Be sure to add assignments to your module for students to complete. Canvas provides 3 different types of assignments: quizzes, discussions, or assignments. Templates for each type of assignment can be found unpublished on your Assignments page."

> **Wrap-up Page.** "This page provides an opportunity to briefly review the learning that took place in this module. It provides a moment of reflection and reinforces the learning material for the students. The Wrap-up could be in the form of text or a video of you talking to the students."

Two further instructions from the same page that bind module construction:

> "Be sure to properly weight your assignments on the Assignments page."

> "The Online Course Layout was designed to assist Alamo Colleges faculty with building online courses. This layout was constructed using research-based best practices to ensure a quality student learning experience and meets 25 Quality Matters Standards."

(Quality Matters is a nonprofit that publishes online course design standards. The template does not say which 25 standards it meets.)

### 2.2 What the Teaching Checklist requires

The checklist is a two-page PDF (`web_resources/Alternate Files/Uploaded Media 2/Teaching Checklist-OnlineHybrid Education Courses_pdf.pdf`, duplicated without extension under `web_resources/Uploaded Media/`). The wiki page of the same name only links to it. Requirements that bear on how a module is built, quoted:

Before the semester:

> "Check dates and settings for assignments, tests/quizzes, journals, discussion boards, etc."

> "Hide/Set 'Delay Delivery' dates for announcements copied over."

> "Check the broken links to documents, websites, images, and videos in your Modules using UDOIT or Validate links Tools in Canvas. Ensure the videos have closed captions."

> "Check Course Accessibility (alt-text for images, color contrast, video captions or transcripts, etc.)."

> "Publish Your Course: Provide access to the course early so that students can review your expectations and get familiar with the layout." With the note: "Instructors do not have to provide early access to lessons or learning materials, but it is preferred that students have access to the layout and syllabus, especially for shorter courses."

> "Email students to welcome them to the course" including "Introduce yourself and the course via email or by sending a brief (1-2 min) welcome video," "Send student (n)etiquette guidelines," "Send students information on how they can access their Canvas course," and "Provide students with Canvas and Technical support information."

During the semester:

> "Remind students of class activities each week. Send an email and/or announcement in Canvas at the beginning of each week. The email/announcement can include the following: Wrap up the weekly activities with a video or an announcement. Tell them what they learned and why it's important. Remind them a list of activities and assignments that needed to complete that week."

> "Monitor student activity. Send reminders to students who are not logging in and completing activities in accordance with the prescribed timelines."

> "Monitor Discussions (if any). Encourage your students to comment on the topics. Ask questions and comment on students' responses."

> "Prompt Feedback. Provide prompt feedback to student questions. Also, provide timely grading on class activities, typically within seven days of the due date for assignments that require heavy grading, but always within a sufficient time frame to support student learning and progress."

End of semester:

> "Remind students to complete any missing or last-minute assignments as soon as possible."

> "Instructors can make sure all submitted assignments have been graded well before the final week and any missing assignments have been given a zero in the gradebook."

### 2.3 Page-by-page anatomy

Every module page uses the same outer shell: a DesignPLUS wrapper, a header bar with the page title as an `h2`, then one or more content blocks. Section headings inside content blocks are `h3` with an icon. Subsection headings are `h4`. There is never an `h1` in page HTML because Canvas renders the page title as the `h1`.

#### 2.3.1 Module [#] Overview (`wiki_content/module-number-overview.html`)

Order of blocks:

1. **Header.** Title uses the split "pre-title" pattern: `Module` + ` [#] Overview` at 18pt.
2. **Introduction block** (`dp-content-block kl_introduction`). One paragraph. Placeholder: `[Briefly introduce the main topic of the unit/module]`.
3. **Learning Objectives block** (`dp-content-block kl_objectives2`). Heading `h3` with the bullseye icon, text "Learning Objectives" at 14pt. Lead sentence: "By the end of this module, you will be able to:". Then a circle-bulleted list numbered `1.1.`, `1.2.`, `1.3.` Placeholder on the first item: `[List the Learning Objectives, beginning each with a Bloom's Taxonomy action verb.] (make sure to remove the highlight from the text)`. Bloom's Taxonomy is a ladder of thinking-skill verbs (remember, understand, apply, analyze, evaluate, create) used to write measurable objectives.
4. **Tasks block** (`dp-content-block kl_assignments2`). Heading `h3` with the tasks icon, text "Tasks" at 14pt. Placeholder instruction: `[List all activities and assignments students are responsible for completing in the table below.] (Remove this line after you complete)`. Lead sentence: "Learners will be required to complete the following module activities and assignments:". Then a three-column table with caption "Activities and assignments for this module" and column headers **Activities and Assignments**, **Learning Objectives (LOs)**, **Due date/Time (CST)**. The first column cell of each body row is a row header (`th scope="row"`). Sample rows shipped: "Name of the activities or assignments | LO(s) that align with the activity and assignment | (blank)", "Assignment 1 | 1.1 | (blank)", "Assignment 2 | 1.2 - 1.3 | (blank)".
5. **Closing line.** A horizontal rule, then in italics: "When you are ready, click the **Next** button on the bottom right of this page to begin working through this module."

#### 2.3.2 Module [#] Content (`wiki_content/module-number-content.html`)

1. **Header.** Title "Module [#] Content" at 18pt using `dp-header-title`.
2. **Introduction block** (`kl_introduction`). Placeholder: `[Briefly introduce the main topic of this page here.]`.
3. **Topic block** (`kl_custom_block_1`). Heading `h3` (no icon) whose text is itself a placeholder: `[Insert topic/concept here]` at 14pt. Body placeholders: `[Insert content here. Content could include text, images, links, embedded videos, etc. Create more headings as needed for additional concepts or topics]` and a bracketed "Helpful Resource" line linking to vendor how-to videos (remove).
4. **Sources block** (`kl_custom_block_3`). Heading `h3` with the open-folder icon, text "Sources" at 14pt. Placeholder: `[List the sources used to create this content page here and/or permissions for use.]`.

The template explicitly invites more topic blocks: "Create more headings as needed for additional concepts or topics." Each additional topic is another `dp-content-block` with an `h3`.

#### 2.3.3 Discussion Template (`g847792aeffe6dda52129a8c2043151e8.xml`, graded discussion)

The discussion body uses the same wrapper and header. Title: "Module [#] Discussion" at 18pt. Blocks, all `h3` with icons at 14pt:

1. **Introduction** (info-circle icon). Placeholder: `[Briefly introduce the topic of discussion.]`.
2. **Directions** (list icon). Placeholder lead: `[Add very specific instructions about your discussion here.  Be sure to include:]` followed by four bracketed bullets: `[The information you want your students to review.]`, `[The location of the information.]`, `[The discussion prompt or questions you want them to answer.]`, `[How many classmates' post they need to respond to.]`.
3. **Grading Criteria** (check-square icon). Placeholders: `[A grading scale and/or a rubric should be provided to give specific and descriptive criteria for the students' work.]`, `[You can add a grading scale or rubric as a file or build a rubric into Canvas (see resource below).` and a bracketed helpful-resource link to the vendor guide on adding a rubric (remove).
4. **How to submit** (download icon). Fixed text: "Click the **Reply** button at the bottom of this box and type your reply in the text box below. Click **Post Reply** at the bottom-right of the text box to post your reply." "You may reply to your classmates by clicking the **Reply** button under their message." Then "Helpful Resource:" with a link to the vendor's student guide on replying to a discussion.

#### 2.3.4 Quiz Template (`g393030ef9fcbd8bad83607baa3955ef3/assessment_meta.xml`, classic quiz)

The quiz description uses the wrapper and the split pre-title header: `Module [` + `#] Quiz`. Blocks:

1. **Introduction** (info-circle). Placeholder: `[Briefly introduce the quiz.]`.
2. **Directions** (list icon). Placeholder lead: `[Add very specific instructions about your quiz. Be sure to include:]` with five bracketed bullets: `[The number of questions in the quiz.]`, `[The maximum time limit for the quiz.]`, `[OPTIONAL: The type of questions included.]`, `[The number of times your students can take the quiz.]`, `[A caution statement about closing/submitting the quiz without answering all of the questions.]`.
3. **How to Submit** (download icon). Fixed text: "Canvas will save your quiz as you go through it. When you are finished, click **Submit Quiz** at the bottom of the page. Depending on the settings selected by your instructor, you may be able to view the quiz results immediately after to find out your score." Then a helpful-resource link to the vendor's student guide on taking a quiz.

#### 2.3.5 Assignment Template (`g065eabf68adfdd4808adcef508c6f13f/assignment-template.html`)

Title: "Module [#] Assignment" at 18pt. Blocks:

1. **Introduction** (info-circle). Placeholder: `[Briefly introduce the assignment.]`.
2. **Directions** (list icon). Placeholder lead `[Add very specific instructions about your assignment here.  Be sure to include:]` with three bracketed bullets: `[The information you want your students to review.]`, `[The location of the information.]`, `[The assignment prompt and any necessary steps to complete the assignment.]`.
3. **Grading Criteria** (check-square). Same two rubric placeholders as the discussion, plus a bracketed helpful-resource link to the vendor guide on creating a rubric.
4. **How to Submit** (upload icon). Fixed text: "To submit this assignment, click the **Submit Assignment** button at the top-right of the page." Placeholder: `[Specify how you want them to post (Text entry, File Upload, Media Recordings, Website URL, etc.)]`. Then a helpful-resource link to the vendor's student guide on submitting an assignment.
5. A closing horizontal rule.

#### 2.3.6 Module [#] Wrap-up (`wiki_content/module-number-wrap-up.html`)

Title "Module [#] Wrap-up" at 18pt. Three blocks, each an `h3` with icon at 14pt followed by a bulleted list containing one placeholder item:

1. **What You Learned!** (open-book icon). `[Briefly list the key concepts that were covered in this module. This should align with the learning objectives.]`
2. **What You Did!** (clipboard-check icon). `[List the task/activities completed in the unit/module.]`
3. **What's Next?** (arrow-circle-right icon). `[Include a brief introduction of what will be covered in the next unit/module.]`

### 2.4 Named content blocks summary

| Page | Block class | Heading text | Icon class |
|---|---|---|---|
| Overview | `kl_introduction` | (none) | |
| Overview | `kl_objectives2` | Learning Objectives | `fas fa-bullseye` |
| Overview | `kl_assignments2` | Tasks | `fas fa-tasks` |
| Content | `kl_introduction` | (none) | |
| Content | `kl_custom_block_1` | [Insert topic/concept here] | (none) |
| Content | `kl_custom_block_3` | Sources | `far fa-folder-open` |
| Discussion | `kl_custom_block_0` | Introduction | `fas fa-info-circle` |
| Discussion | `kl_custom_block_1` | Directions | `fas fa-list-alt` |
| Discussion | `kl_custom_block_2` | Grading Criteria | `fas fa-check-square` |
| Discussion | `kl_custom_block_3` | How to submit | `fas fa-download` |
| Quiz | `kl_custom_block_0` | Introduction | `fas fa-info-circle` |
| Quiz | `kl_custom_block_1` | Directions | `fas fa-list-alt` |
| Quiz | `kl_custom_block_3` | How to Submit | `fas fa-download` |
| Assignment | `kl_custom_block_0` | Introduction | `fas fa-info-circle` |
| Assignment | `kl_custom_block_1` | Directions | `fas fa-list-alt` |
| Assignment | `kl_custom_block_2` | Grading Criteria | `fas fa-check-square` |
| Assignment | `kl_custom_block_3` | How to Submit | `fas fa-upload` |
| Wrap-up | `kl_custom_block_0` | What You Learned! | `dp-icon fas fa-book-open` |
| Wrap-up | `kl_custom_block_1` | What You Did! | `fas fa-clipboard-check` |
| Wrap-up | `kl_custom_block_2` | What's Next? | `fas fa-arrow-alt-circle-right` |

The `kl_` classes are legacy DesignPLUS block identifiers. They carry no styling of their own in current DesignPLUS releases but are how the template marks which block is which. Keep them on rebuilt pages so the block names survive.

---

## 3. DesignPLUS markup used in the template

Every snippet below is copied from the template with Canvas-generated attributes removed. Font Awesome 5 icon classes (`fas` solid, `far` regular) are loaded by the DesignPLUS theme.

### 3.1 Page shell: wrapper and header bar

Standard form (used on 23 of 24 pages):

```html
<div id="dp-wrapper" class="dp-wrapper dp-basic-bar">
<header class="dp-header dp-basic-bar ">
<h2 class="dp-heading"><span class="dp-header-title" style="font-size: 18pt;">Page Title Here</span></h2>
</header>
<!-- content blocks follow, still inside #dp-wrapper -->
</div>
```

Title size conventions in the export: 18pt on module pages, home page, and most resource pages; 24pt on several orientation pages (Welcome, Meet Your Instructor, Course Material, Course Evaluation, Course Schedule, Tips for Success, Introduce Yourself). Both sizes appear; the module pages use 18pt.

Split pre-title form (Module Overview page and Quiz Template):

```html
<header class="dp-header dp-basic-bar ">
<h2 class="dp-heading"><span style="font-size: 18pt;"><span class="dp-header-pre"><span class="dp-header-pre-1">Module</span><span class="dp-header-pre-2"> [#] <span style="font-size: 18pt;">Overview</span></span></span></span></h2>
</header>
```

Wrapper with DesignPLUS metadata (Course Policies page and the Respondus practice quiz). The `data-img-url` in the export points to a vendor-hosted banner image; do not copy that value.

```html
<div id="dp-wrapper" class="dp-wrapper dp-basic-bar" data-header-class="dp-header dp-basic-bar" data-nav-class="container-fluid dp-link-grid dp-bb-1" data-img-url="">
```

### 3.2 Content block

```html
<div class="dp-content-block kl_custom_block_0">
<h3 class="dp-has-icon"><i class="fas fa-info-circle dp-i-size-small" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 14pt;">Introduction</span></h3>
<p>Body text.</p>
</div>
```

Named variants seen: `kl_introduction`, `kl_objectives2`, `kl_assignments2`, `kl_readings2`, `kl_panel_block_0`, `kl_custom_block_0` through `kl_custom_block_4`. One block on the Welcome page carries `data-title="Banner Image" data-category="Layout"`; the Respondus quiz block carries `data-id="content-<number>"`. A block may also have no `kl_` class at all (`<div class="dp-content-block">`).

### 3.3 Section heading with icon

Two equivalent forms appear. The first omits `dp-icon`; the second includes it. Both work.

```html
<h3 class="dp-has-icon"><i class="fas fa-bullseye dp-i-size-small" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 14pt;">Learning Objectives</span></h3>
```

```html
<h3 class="dp-has-icon"><i class="dp-icon fas fa-book-open dp-i-size-small" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 14pt;">What You Learned!</span></h3>
```

Rules the template follows: the `<i>` carries `aria-hidden="true"`; the hidden `<span class="dp-icon-content">` is always present inside it; `dp-i-size-small` sets the icon size; visible text sits in a `<span>` with an inline `font-size`. Section headings are 14pt on module pages and 18pt on orientation pages. Subsection `h4` headings sometimes carry `dp-has-icon` too (home page "Getting Started" cards).

### 3.4 Banner image

Home page (full-width banner, informative alt text):

```html
<div class="dp-banner-image"><img class="dp-full-width" style="width: 100%; height: auto; max-width: 100%;" src="$IMS-CC-FILEBASE$/external_imports/1100x330-NLC-cidilab-banner20250701_150015.jpg" alt="Northeast Lakeview College" loading="lazy"></div>
```

The shipped banner is 1100 by 330 pixels: the college name in white block capitals on a green gradient at left, campus buildings under a blue sky at right, a small college mark bottom right. The "How to Use This Layout" page tells faculty to delete a banner that reads "District Support Office" and insert their college banner from the College Banners folder; the export already carries the NLC banner on the home page, and the Files export has no "College Banners" folder (it has "College Logos", which are 1589 by 187 pixel support-services buttons, not banners).

Welcome page (decorative banner pulled from a vendor image host in the export; replace with a course file):

```html
<div class="dp-content-block" data-title="Banner Image" data-category="Layout">
<div class="dp-banner-image"><img role="presentation" src="" alt="" loading="lazy"></div>
</div>
```

### 3.5 Link grid (home page quick links)

```html
<nav class="container-fluid dp-link-grid dp-link-grid-angle-r dp-bc-1">
<ul class="row g-3">
<li class="col-sm-12 col-md-3 col-lg-3"><a class="dp-has-icon" title="Course Schedule" href="$WIKI_REFERENCE$/pages/course-schedule" target="_blank"><i class="far fa-calendar-alt" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Course Schedule</a></li>
<li class="col-sm-12 col-md-3 col-lg-3"><a class="dp-has-icon" title="Academic &amp; Student Support Resources" href="$WIKI_REFERENCE$/pages/academic-and-student-support-resources-2" target="_blank"><i class="fas fa-user-graduate"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Student Support</a></li>
<li class="col-sm-12 col-md-3 col-lg-3"><a class="dp-has-icon" title="Canvas and Technical Support" href="$WIKI_REFERENCE$/pages/canvas-and-tech-support"><i class="fas fa-headset" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Tech Support</a></li>
<li class="col-sm-12 col-md-3 col-lg-3"><a class="dp-has-icon" title="Q &amp; A Discussion Board" href="$CANVAS_OBJECT_REFERENCE$/discussion_topics/q-and-a" target="_blank"><i class="far fa-question-circle" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> Q &amp; A </a></li>
</ul>
</nav>
```

Four tiles, each a quarter width on medium screens and full width on small. The second tile's icon lacks `aria-hidden` in the export; add it.

### 3.6 Panels: tabs and accordions

DesignPLUS "panels" are a wrapper of `dp-panel-group` children. Each group is a heading plus a content div. The wrapper classes decide the presentation.

Vertical tab buttons (Course Policies, Student Support, Navigate Canvas):

```html
<div class="dp-panels-wrapper dp-panel-active-color-success dp-panel-hover-color-dp-gray dp-panel-color-dp-primary dp-tabs-buttons-vertical">
<div class="dp-panel-group">
<h3 class="dp-panel-heading dp-has-icon"><i class="dp-icon fas fa-calendar-alt" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i> <span style="font-size: 14pt;">&nbsp;Course Week</span></h3>
<div class="dp-panel-content">
<p><span style="font-size: 12pt;">Panel body.</span></p>
</div>
</div>
<div class="dp-panel-group">
<h3 class="dp-panel-heading">Second Panel</h3>
<div class="dp-panel-content">
<p>Second body.</p>
</div>
</div>
</div>
```

Horizontal tab buttons (Canvas and Tech Support): same markup with `dp-tabs-buttons` in place of `dp-tabs-buttons-vertical`.

Accordion (Academic Integrity, Using Zoom): `dp-expander-default dp-no-expander-controls` in place of the tabs class.

```html
<div class="dp-panels-wrapper dp-expander-default dp-no-expander-controls dp-panel-color-dp-primary dp-panel-active-color-success dp-panel-hover-color-dp-gray">
```

Vertical tabs without expander controls (Navigate Canvas): `dp-no-expander-controls dp-panel-color-dp-primary dp-panel-active-color-success dp-panel-hover-color-dp-gray dp-tabs-buttons-vertical`.

Color modifiers used: `dp-panel-color-dp-primary` (panel color), `dp-panel-active-color-success` (active tab), `dp-panel-hover-color-dp-gray` (hover). Panel headings are `h3.dp-panel-heading` everywhere except the Student Privacy panels on the Course Policies page, which use `h4.dp-panel-heading`. The heading may carry `dp-has-icon` and an icon like any other heading. The page introduces every panel set with a sentence such as "Please select each tab below to expand and learn more." or "Click on each item for additional information."

### 3.7 Callouts

Solid danger, centered (Course Material bookstore statement; BioSig help-desk note):

```html
<div class="dp-callout dp-callout-color-lg-danger  card dp-callout-position-default dp-callout-type-solid text-center">
<div class="card-body" style="padding: 5px;"><strong>Statement text.</strong></div>
</div>
```

Solid success (OLRN page lead):

```html
<div class="dp-callout card dp-callout-position-default dp-callout-type-solid dp-callout-color-success">
<div class="card-body">
<p class="card-text">Callout text.</p>
</div>
</div>
```

Info callout with side emphasis icon and title (OLRN "Unable to self-register?", Respondus "PLEASE NOTE", Student Support "Note for Dual Credit Students"):

```html
<div class="dp-callout dp-callout-placeholder card dp-callout-position-default dp-callout-type-info dp-callout-color-lg-success">
<div class="dp-callout-side-emphasis"><i class="dp-icon dp-default-icon fas fa-check">&#8203;</i></div>
<div class="card-body">
<h3 class="card-title"><span style="font-size: 14pt;">Callout title</span></h3>
<p class="card-text">Callout body.</p>
</div>
</div>
```

The side-emphasis icon in the export contains a zero-width space rather than the hidden `dp-icon-content` span. The Student Support variant uses `fas fa-info-circle` for the side icon.

### 3.8 Tables

All data tables follow one pattern: an optional scroll wrapper, Canvas `ic-Table` classes, a caption, `th scope="col"` in the header row, and `th scope="row"` on the first cell of body rows where the row has a name.

```html
<div class="dp-table-scroll">
<table class="ic-Table table-bordered ic-Table--striped ic-Table--hover-row ic-Table--condensed" style="border-collapse: collapse;" data-active-table="true">
<caption class="dp-caption-t text-center">Activities and assignments for this module</caption>
<thead>
<tr>
<th scope="col"><strong>Activities and Assignments</strong></th>
<th scope="col"><strong>Learning Objectives (LOs)</strong></th>
<th scope="col"><strong>Due date/Time (CST)</strong></th>
</tr>
</thead>
<tbody>
<tr>
<th scope="row">Assignment 1</th>
<td>1.1</td>
<td></td>
</tr>
</tbody>
</table>
</div>
```

Class variants seen: `ic-Table table-bordered ic-Table--striped ic-Table--hover-row` (Welcome page links table, Tech Support college table), plus `ic-Table--condensed` on the Overview tasks table and Course Schedule; the Privacy Policies and Library tables use Bootstrap `table-bordered table table-striped` instead. `dp-caption-t` places the caption on top. The Overview table in the export carries pixel widths and heights on cells and `width: 100.009%` on the table; those are editor artifacts and can be dropped.

### 3.9 Buttons

Primary call to action (home page "Start Here"):

```html
<a class="btn btn-sm btn-dp-primary cph-bg-success" title="Welcome! Start Here" href="$WIKI_REFERENCE$/pages/welcome-start-here">Start Here</a>
```

Large resource button with icon (Student Support panels):

```html
<a class="dp-course-link cph-bg-secondary btn-lg btn btn-success dp-ext-ignore" href=""><i class="dp-icon fas fa-hand-point-right " aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i>&nbsp;<span style="font-size: 12pt;">Academic Advising</span></a>
```

Smaller variants: `cph-bg-secondary btn btn-success dp-ext-ignore` and `cph-bg-dp-gray btn btn-success dp-ext-ignore`. `cph-bg-*` sets the button background from the DesignPLUS palette; `dp-ext-ignore` suppresses the external-link icon DesignPLUS would otherwise add.

### 3.10 Embedded media

Video from a video platform (iframe with a title):

```html
<div class="dp-embed-wrapper"><iframe title="Descriptive title of the video" src="" width="560" height="315" loading="lazy" allowfullscreen="allowfullscreen" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"></iframe></div>
```

Uploaded course video with a caption track (Communicating Online page). The caption track itself is stored in `course_settings/media_tracks.xml` as an English subtitles track in SubRip format:

```html
<div class="dp-embed-wrapper" style="text-align: center;"><video class="phpally-ignore" style="width: 640px; height: 360px; display: inline-block;" title="Communication Guidelines.mp4" data-media-type="video" loading="lazy" allowfullscreen="allowfullscreen" allow="fullscreen"><source src="$IMS-CC-FILEBASE$/Uploaded%20Media/Communication%20Guidelines-1080p-231129.mp4" data-media-type="video"></video></div>
```

The page then tells the viewer to select the closed-caption icon (an uploaded SVG icon image, alt text empty, `role="presentation"`) and the full-screen icon.

### 3.11 Images

Bordered screenshot:

```html
<img class="dp-image-padded dp-image-bordered dp-image-shadow" src="" alt="Zoom link in the left-hand course navigation" width="167" height="267" loading="lazy">
```

Floated photo, informative:

```html
<img class="float-end ms-3 mb-3 object-fit-cover dp-ratio-16-9" style="float: right; height: auto;" src="" alt="Student at a computer" width="339" height="226" loading="lazy">
```

Floated photo, decorative:

```html
<img class="float-end ms-3 mb-3 object-fit-cover dp-ratio-4-5" style="float: right;" role="presentation" src="" alt="" width="279" height="419" loading="lazy">
```

Left-floated textbook cover: `class="float-start me-3 mb-3" role="presentation" alt=""`. Centered roadmap graphic on the home page: `class="dp-padding-direction-tblr" style="display: block; margin-left: auto; margin-right: auto; padding-top: 5px; width: 246px;" role="presentation" alt=""`. The roadmap graphic is a dashed winding path between two map pins on white, 1100 by 1650 pixels.

### 3.12 Instructor information card (home page)

```html
<div class="dp-user-details-wrapper dp-user-details-h-legacy" style="width: 100%; border: none; max-width: unset;" data-content-selected-role="all">
<div class="dp-card card h-100">
<div class="card-body">
<p class="dp-user-details dp-heading-ignore"><span style="background-color: #ffffff;"><i class="fas fa-tag" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><strong><span style="font-size: 12pt;"> Instructor's name:&nbsp;</span></strong></span></p>
<p class="dp-user-details dp-heading-ignore"><span style="background-color: #ffffff; font-size: 12pt;"><i class="fas fa-envelope" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><strong> Email:&nbsp;</strong></span></p>
<p class="dp-user-details dp-heading-ignore"><span style="background-color: #ffffff; font-size: 12pt;"><i class="fas fa-phone" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><strong> Preferred Method of Contact</strong>: Canvas Inbox or ACES Email</span></p>
<p class="dp-user-details dp-heading-ignore"><span style="background-color: #ffffff; font-size: 12pt;"><i class="fas fa-university" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><strong> Department:&nbsp;</strong></span></p>
<p class="dp-user-details dp-user-other2 dp-heading-ignore"><span style="font-size: 12pt;"><i class="fas fa-clock" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><strong>Contact Hours:</strong></span></p>
</div>
</div>
</div>
```

The export also carries a `data-content-user-id` on the wrapper that ties the card to a specific user; omit it. "ACES" is the district's student portal; the phrase "Canvas Inbox or ACES Email" is institutional wording.

### 3.13 Two-column layout (home page "Getting Started")

Bootstrap grid inside a content block:

```html
<div class="container-fluid">
<div class="row">
<div class="col"> <!-- image column --> </div>
<div class="col-md-8">
<div class="container-fluid">
<div class="row dp-margin-direction-tblr dp-padding-direction-all" style="padding: 5px;">
<div class="col-md-6">
<h4 class="cp-txt-dp-secondary dp-has-icon"><i class="dp-icon fas fa-book-open dp-i-size-small" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 14pt;">Read the Syllabus</span></h4>
<p class="dp-heading-ignore">Step text.</p>
</div>
<div class="col-md-6">
<h4 class="dp-has-icon"><i class="dp-icon fas fa-exclamation-circle" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i><span style="font-size: 14pt;">&nbsp;Explore the "Orientation" Module</span></h4>
<p>Step text.</p>
</div>
</div>
</div>
</div>
</div>
</div>
```

`cp-txt-dp-secondary` colors heading text with the DesignPLUS secondary color. Note one `col-md-6` opening tag in the export is split across lines with stray whitespace inside the attribute; write it on one line.

### 3.14 Pop-up definitions (Academic Integrity page)

A list of terms, each a modal trigger, followed by hidden modal content blocks:

```html
<a id="dpPopup3" class="dp-modal-trigger" href="#dpPopup3Content">Cheating</a>

<div id="dpPopup3Content" class="dp-modal-content dp-popup-content" style="border: 1px solid #A9A9A9; background: #f7f7f7; padding: 10px; width: 600px; max-width: 100%; margin: auto;">
<h4 class="dp-modal-title dp-ignore-theme" style="margin-top: 0;"><span style="font-size: 12pt;"><strong>Cheating</strong></span></h4>
<p class="dp-heading-ignore"><span style="font-size: 12pt;">Definition text.</span></p>
</div>
```

### 3.15 Progress bar placeholder

Placed as the last content block on each Student Resources page:

```html
<div class="dp-content-block kl_custom_block_0">
<p class="dp-progress-placeholder dp-module-progress-basic" style="display: none;">Basic Progress Bar (built in browser, hidden in app)</p>
</div>
```

DesignPLUS replaces it in the browser with a module progress bar. It is hidden in the mobile app.

### 3.16 Helper classes and legacy icons

| Class | Meaning in the template |
|---|---|
| `dp-heading-ignore` | On a `<p>`, tells DesignPLUS not to treat the paragraph as a heading in its page outline. Used heavily on paragraphs that start with bold text. |
| `dp-ext-ignore` | On an `<a>`, suppresses the external-link icon DesignPLUS adds to off-site links. |
| `phpally-ignore` | Tells the accessibility scanner (UDOIT, whose scanning engine is called PHPAlly) to skip the element. The template applies it to yellow placeholder spans, video iframes, and one privacy-policy link. |
| `dp-course-link` | Marks a link as an internal course link. |
| `dp-i-size-small` | Icon size. |
| `dp-icon-content` | Always-hidden span inside an icon; required by DesignPLUS. |
| `dp-caption-t` | Caption on top of a table. |
| `text-center`, `float-start`, `float-end`, `ms-3`, `me-3`, `mb-3`, `object-fit-cover`, `h-100`, `g-3` | Bootstrap 5 utilities available under the theme. |
| `dp-ratio-16-9`, `dp-ratio-4-5` | Image aspect ratios. |
| `dp-padding-direction-all`, `dp-padding-direction-tblr`, `dp-margin-direction-tblr` | DesignPLUS spacing helpers. |
| `inline_disabled` | Canvas editor class on links that should not open inline. |
| `instructure_file_link instructure_scribd_file` | Canvas file-link classes (with `data-canvas-previewable="false"` for a plain download). |
| `external` plus `<span class="external_link_icon" role="presentation"><span class="screenreader-only">Links to an external site.</span></span>` | Canvas external-link marker with screen-reader text. |
| `icon-pin`, `icon-question`, `icon-feedback icon-Solid` | Canvas's own icon font (not Font Awesome); used inline as `<i class="icon-pin" aria-hidden="true"><span class="dp-icon-content" style="display: none;">&nbsp;</span></i>`. |

### 3.17 Icon catalog

Every Font Awesome icon the template uses, with where it appears:

| Icon | Used for |
|---|---|
| `fas fa-info-circle` | Introduction headings (discussion, quiz, assignment, Q&A), dual-credit callout side icon |
| `fas fa-list-alt` | Directions headings |
| `fas fa-check-square` | Grading Criteria headings |
| `fas fa-upload` | How to Submit (assignment, Introduce Yourself, Q&A) |
| `fas fa-download` | How to submit (discussion template, quiz template), Respondus download heading |
| `fas fa-bullseye` | Learning Objectives, Course Learning Outcomes, Overview headings |
| `fas fa-tasks` | Tasks heading |
| `far fa-folder-open` | Sources heading |
| `dp-icon fas fa-book-open` | What You Learned!, Read the Syllabus |
| `fas fa-clipboard-check` | What You Did! |
| `fas fa-arrow-alt-circle-right` | What's Next?, OLRN self-register heading, "What is Canvas?", "What is Zoom?" |
| `fas fa-chevron-circle-right` | Next Step: Orientation Module |
| `fas fa-globe-americas` | Course Tour |
| `dp-icon fas fa-book`, `fa-book fas` | Course Overview, Materials |
| `fas fa-chalkboard-teacher` | Instructor Information, Instructor Introduction |
| `far fa-envelope`, `fas fa-envelope` | Contact Me, Email |
| `fas fa-tag`, `fas fa-phone`, `fas fa-university`, `fas fa-clock` | Instructor card rows |
| `fas fa-desktop` | Instructional Delivery, Technology Requirements |
| `fas fa-angle-double-right` | Getting Started |
| `fas fa-exclamation-circle` | Explore the Orientation Module |
| `fas fa-user-check` | Introduce Yourself (home) |
| `fas fa-question-circle`, `far fa-question-circle` | Review Student Resources, Q&A tile, Help references |
| `fas fa-hands-helping` | Welcome heading (home) |
| `far fa-calendar-alt`, `dp-icon fas fa-calendar-alt` | Course Schedule tile and heading, Course Week panel |
| `fas fa-user-graduate` | Student Support tile |
| `fas fa-headset` | Tech Support tile |
| `dp-icon fas fa-balance-scale` | Course Policies, Academic Integrity Policies |
| `dp-icon fas fa-bell-slash` | Late Work panel |
| `dp-icon fas fa-at` | AI Tools panel |
| `dp-icon fas fa-comments` | Netiquette panel |
| `dp-icon fas fa-bookmark` | Course Expectations |
| `dp-icon fas fa-users`, `dp-icon fas fa-user-alt` | Students / Instructor expectation panels |
| `dp-icon fas fa-exclamation-triangle` | Student Privacy |
| `fas fa-hospital-user`, `fas fa-check-double`, `fas fa-hourglass-half`, `fas fa-sticky-note` | Tips for Success section headings (Effort, Failure, Time Management, Study Skills) |
| `dp-icon fas fa-paperclip` | NLC Student Support Resources |
| `fas fa-clipboard-list` | Additional Resources |
| `fas fa-hand-point-right` | Resource buttons |
| `dp-icon fas fa-key` | Key Points from the Video |
| `dp-icon fas fa-video` | Zoom Communications |
| `dp-icon fas fa-book-reader` | Using LockDown Browser for Online Exams |
| `dp-icon dp-default-icon fas fa-check` | Callout side icon |
| `fas fa-asterisk` | Helpful Hint (Q&A) |
| `fas fa-expand` | Full-screen instruction |

### 3.18 Standard closing line

Orientation and module pages end with a navigation sentence in italics, sometimes after a horizontal rule:

```html
<hr>
<p><em>When you are ready, click the <strong>Next </strong>button on the bottom right of this page to begin working through this module.</em></p>
```

Variants: "Click the **Next** button on the bottom right of this page to continue in the module." and "Click the **Next** button on the bottom right corner of this page to continue throughout this module."

### 3.19 Typographic conventions

- Body text is wrapped in `<span style="font-size: 12pt;">` on most institution pages; module template pages leave body text unstyled.
- Section headings: `<span style="font-size: 14pt;">` on module pages, `18pt` on orientation pages.
- Page title: `18pt` or `24pt` as noted in 3.1.
- Emphasis on dates and rules uses bold plus a dark red (`#ba372a`), so the meaning is not carried by color alone.
- Several `<span style="background-color: #ffffff;">` wrappers are editor artifacts with no visible effect.

---

## 4. Orientation module, home page, and Student Resources: required pages and what each contains

Legend: **Instructor edits** means the page is scaffolding the course author fills in. **Institution boilerplate, keep verbatim** means the page is district or college text; copy it from the named template file without change, apart from stripping placeholders noted. **Institution boilerplate, service-specific** means the text is institutional but describes a service or tool; keep or drop is a course decision (see section 9).

### 4.1 Home page (`wiki_content/home.html`, front page, published)

Instructor edits. Set as the course front page (`front_page` true; course `default_view` is `wiki`). Blocks in order:

1. Header: `[Insert Course Title]` at 18pt.
2. Banner image (section 3.4).
3. Link grid: Course Schedule, Student Support, Tech Support, Q & A (section 3.5).
4. "Welcome to [insert course name and number]" (`h3`, hands-helping icon) with `[Insert a welcome message or brief description of the course]`.
5. "Instructor Information" (`h3`, chalkboard icon) with the instructor card (section 3.12): name, email, preferred contact ("Canvas Inbox or ACES Email"), department, contact hours.
6. "Instructional Delivery" (`h3`, desktop icon). Three variant paragraphs, of which the builder keeps one and deletes two:
   - "**Online Classes Only:** This ##-week fully online course is scheduled to begin (Insert Date here). This course does not have a meeting date or time associated with it."
   - "**Hybrid Classes Only:** ..." (meeting days, building, room).
   - "**Remote Classes Only:** ..." (days, times, recurring video-meeting link).
   - A trailing sentence pointing to the "Using Zoom as a Student" page for attending remotely.
   The `##`, `(Insert Date here)`, `(insert date)`, `Day`, `___`, `a.m`, and `(insert hyperlink...)` fragments are red-text placeholders (section 5).
7. "Getting Started" (`h3`, double-angle icon): the roadmap image beside four `h4` steps: "Read the Syllabus" ("First, carefully read through the syllabus by clicking on **Course Syllabus** in the left-hand navigation menu to understand the course structure, requirements, and objectives."), "Explore the 'Orientation' Module" (with the **Start Here** button; then "You must complete all tasks in the Orientation Module to access the next module of this course."), "Introduce Yourself" ("Introduce yourself to the instructor and peers by posting on the 'Introduce Yourself' discussion forum."), "Review Student Resources" ("to learn more about the Canvas system and discover how the college can best assist you during your academic journey.").
8. Footer block after a rule, centered: "Canvas Help is always available by clicking on the **Help** button in the left-hand navigation." and a line giving the district help desk phone number and option (institutional; copy from the file).

### 4.2 Welcome! Start Here: (`wiki_content/welcome-start-here.html`)

Instructor edits. Title "Welcome! Start Here: COURSE TITLE" at 24pt.

1. Decorative banner block (section 3.4, second form).
2. "Course Overview" (`h3`, book icon, 18pt): yellow placeholder "Provide the catalog description of your course here."
3. "Course Learning Outcomes (CLOs)" (`h3`, bullseye): "At the end of this course, you will be able to:" then an ordered list with placeholder `[List your course outcomes (from your Simple syllabus) here.]`. ("Simple syllabus" refers to the college's external syllabus system.)
4. "Course Tour" (`h3`, globe): placeholder `[Provide brief instructions to students on how to navigate your course. This can be a typed list or a short video!]`.
5. "Next Step: Orientation Module" (`h3`, chevron): fixed text "The links below provide an orientation to this course and the online learning environment at Northeast Lakeview College. Please review each item in this module in sequential order, as some information changes from semester to semester. Keep in mind you can always come back to this page at any point in the semester to review the information again." Then a two-column table (caption "Getting Started/Student Resources", headers "Getting Started in this Course" and "Student Resources") whose cells are bulleted link lists:
   - Left: Meet Your Instructor; Textbook (links to Course Material); Course Schedule; OLRN-0001 is Required for this Course; Course Policies, Expectations, and Student Privacy; BioSig Instructions and Practice Assignment; Introduce Yourself to the Class.
   - Right: How to Navigate Canvas as a Student; Using Zoom as a Student; Academic Integrity; Academic & Student Support Resources; Communicating Online; Tech Support; Uploading a Paper to Turnitin Using Canvas.
   Note the left list omits Course Evaluation and Tips for Success even though both are module items.
6. Closing "Next" line.

### 4.3 Meet Your Instructor (`wiki_content/meet-your-instructor.html`)

Instructor edits. Title at 24pt.

1. "Instructor Introduction" (`h3`, chalkboard, 18pt). A right-floated 191 by 191 pixel blank avatar image (`personal-file.png`, alt "Blank Image ") wrapped in an empty `h2` (an editor artifact; the image should be moved into a paragraph). Instruction text: "Provide a brief introduction about yourself for your students. Include details about how long you have been teaching and/or practical experience in your field of discipline and place a picture of yourself." "If you have an introduction video, you can also post it here."
2. "Contact Me" (`h3`, envelope, 18pt): `[Provide your contact information and any office hours that you will provide.]`.

### 4.4 Course Material (`wiki_content/course-material.html`)

Instructor edits, with one institutional statement. Title at 24pt.

1. Intro: "Before our course gets started, be sure to secure access to the required textbooks."
2. "Materials" (`h3`, book, 18pt; block `kl_readings2`). Four yellow placeholders: `[Add an image for each textbook.]`, `[List the name of your course textbooks, the author(s), ISBNs, and publisher's name on this page.]`, `[If an e-book is required be sure to provide access directions.]`, "Below is an example of textbook information". Then an example block: a left-floated cover image (decorative), Author/Publisher/Edition/ISBN lines with bracketed sample values, a sentence naming the campus bookstore and online retailers, a bookstore link, and the bookstore's street address and phone (institutional).
3. Danger callout, centered, bold: "A student of this institution is not under any obligation to purchase a textbook from a college-affiliated bookstore. The same textbook may also be available from an independent retailer, including an online retailer." This is institution boilerplate; keep verbatim if the page is kept.

### 4.5 Course Policies, Expectations, and Student Privacy (`wiki_content/course-policies-expectations-and-student-privacy.html`)

Mixed. Title at 18pt. Three sections, each a vertical tab panel set.

**Course Policies** (`h3`, balance-scale, 18pt). Lead: "The following is a basic compilation of course policies for an online class; a full list can be found in the Course Syllabus linked in the Course Navigation menu at the left. The course schedule, final evaluation, college/institutional policies, and the student learning outcomes for this course are located in the Course Syllabus as well." Panels:

- **Course Week** (institution default wording, instructor may edit): "The Course Week in this class starts on **Monday** and ends on **Sunday at 11:59 PM**. This means that unless otherwise indicated, all activities and assignments for the week are due by **11:59 PM on Sunday**. All the course content is published at the beginning of the semester, so you can look ahead at what's coming up in each module."
- **Late Work** (instructor policy, shipped as a default): "It is important to make a commitment to yourself to meet the deadlines for the course activities and assignments. Please note that I do **NOT** accept late work, so plan your work time accordingly so that you do not miss any deadlines. Also, keep in mind that the Canvas LMS is designed to automatically 'lock' activities and assignments after the deadline."
- **Timely Feedback** (instructor policy, shipped as a default): "**Instructor Communication:** Please note that messages must be sent to me through the Canvas Inbox or your ACES student email accounts ONLY. I will respond within **24-48 hours**, NOT including holidays or weekends. I cannot guarantee messages sent through a personal email or via text will receive a timely response." "**Grades and Guided Feedback:** I will provide grades and any applicable feedback **one week** from the due date of the assignment, except when otherwise indicated. Most T/F or multiple-choice quizzes will provide an immediate grade unless there is a short answer included, which will then be subject to the one-week turnaround time for feedback and final grade."
- **Technology Requirements** (institution boilerplate): browser requirements paragraph; "Canvas works best on a **laptop** or **desktop computer**..." with a link to a district technical-information page; a paragraph that "Technical difficulties do not excuse you from participating in online tasks or submitting assignments on time" and that students need a backup plan; then `h4` "Minimal Technical Skills Needed:" with seven bullets: save documents in .doc or .docx using a named desktop word processor (or convert to that format or PDF); edit word-processor formatting; access and download materials from Canvas; navigate Canvas for due dates, assignments, rubrics, grades; post and reply in discussion forums; upload writing assignments in the assigned format; access Zoom and navigate a meeting (for office hours).
- **Artificial Intelligence (AI) Tools** (institution boilerplate as shipped): states that violating the syllabus AI policy may be an academic integrity violation under district procedure F.4.2.2, lists example tools, says faculty may use AI detection software, that "Students are **NOT** allowed to use any Artificial Intelligence (AI) tools for the course and/or any course assignments unless specifically authorized to do so in the written instructions of the assignment," that assignment instructions will state which tools may be used and how to cite them, that violations receive a **Zero**, that a student flagged by detection must demonstrate originality with drafts and revision history, that composing in a named cloud document tool with revision history is "strongly suggested," that a named desktop office suite does not track revision history, and that violations are documented and may lead to an automatic "F."
- **Netiquette** (institution boilerplate): definition of netiquette and three bullets: Be courteous; Be a good classmate; Be professional.

**Course Expectations** (`h3`, bookmark, 18pt). Lead: "To be successful in this course, it is important that there are clearly communicated expectations. Below, I have outlined what I expect of you and what you can expect of me. These expectations should serve as a guide for how to succeed in this course." Panels **Students** ("In this course, you will be expected to:" plus placeholder `[briefly list your expectations of students]`) and **Instructor** ("In this course, you can expect me to:" plus placeholder `[briefly list what students can expect of you (i.e., responsiveness, turnaround for grading, etc.)]`). Instructor edits.

**Student Privacy** (`h3`, warning-triangle, 18pt). "Click on each item for additional information." Panels (`h4` headings): **Protect Your Privacy!** (three paragraphs: protect your privacy and respect peers'; do not share personal email, home address, or login information; do not share course materials, meeting links, or peers' personal information outside the course) and **Privacy Policies and Accessibility Statements** (a three-column table, caption "Accessibility and Privacy Statements", columns Application / Accessibility Statement / Privacy Policy, sixteen vendor rows covering the learning platform, the identity-verification tool, the locked browser, the plagiarism checker, the video-conferencing tool, the online tutoring service, a public video platform, a document and creative software vendor, two browser or office software vendors, and six textbook publishers, each with two external links). Institution boilerplate.

Closing "Next" line.

### 4.6 Course Evaluation (`wiki_content/course-evaluation.html`)

Instructor edits. Title at 24pt. Single intro block with the instruction "On this page, you can provide information regarding your course grading and evaluation." Nothing else. This is where the template expects the grading breakdown.

### 4.7 Course Schedule (`wiki_content/course-schedule.html`)

Instructor edits. Title at 24pt. "Schedule" (`h3`, calendar, 18pt). Placeholder: `[Please fill in the schedule below or attach your course schedule as an accessible Word or PDF document.]`. Table (caption "Below is the schedule for this class:", columns **Module**, **Activities and Assignments**, **Due Date**) with six sample rows "Module 1" through "Module 6"; row 1's middle cell reads "Listing the names of activities and assignments." The Module column cells are plain `td`, not row headers.

### 4.8 Tips for Success (`wiki_content/tips-for-success.html`)

Instructor-authored sample content written in the first person by the template author, including a personal anecdote about failing a class. Title at 24pt. Intro paragraph on the meaning of success, then four sections: **Effort**, **Failure**, **Time Management** (each embedding a video from a public video platform in a `dp-embed-wrapper`, with a linked article or two), and **Study Skills** (`h4` "Study Habits" and "Note-Taking" link lists, including one uploaded handout "Online Study Skills_pdf.pdf" linked as "Study Smarter Handout"). Ends with the progress-bar placeholder. If kept, the first-person anecdote and the third-party embeds must be reviewed by the instructor.

### 4.9 OLRN-0001 is Required for this Course (`wiki_content/olrn-0001-is-required-for-this-course.html`)

Institution boilerplate, keep verbatim if kept. Title at 18pt. Success callout: "If you are new to online/hybrid courses, or if you will be taking EDUC-1300 at Northeast Lakeview College, you are required to enroll in a free Orientation to Online Learning (OLRN-0001) mini-course. However, if you have completed OLRN, you do **NOT** have to retake it." Then: OLRN-0001 is a "**no-fee and 0-credit 'mini-course'**", "100% **online, self-paced**", "approximately **1-2 hours**", must be completed "by the first week of class, as your instructor will be checking for proof of successful completion (80% or higher on the post-test)." Section "Instructions to self-register" (`h3`, arrow icon, 18pt) links the OLRN student page, the district registration tutorial, and the college's instructional innovation center contact; an info callout "Unable to self-register?" gives the advising office contact. Closing "Next" line.

### 4.10 BioSig Instructions and Practice Assignment (`g7f9f34566cb7bf279429de1d99ab82cc/`)

Institution boilerplate, service-specific. An assignment with `submission_types` = `external_tool`, 1.0 point, assignment group "Assignments", published, no due date, launched through an identity-verification LTI (Learning Tools Interoperability, the standard for plugging outside tools into Canvas) provider. Body: title "BioSig ID Instructions" at 18pt; right-floated vendor logo (decorative); "As part of the Alamo Colleges' initiative to improve student success, instructors have been asked to confirm each student's identity using the BioSig-ID tool." "In this assignment, you will create a biometric password. This password cannot be replicated by anyone but you. Please watch this video to learn how to use BioSig." An embedded video from a public video platform (iframe without a `title`, marked "(This video is Closed Captioned)"). "Throughout this course, you will be asked to verify your identity by entering your BioSig password..." "**When you are ready, create or enter your BioSig-ID Password in the window below:**" Danger callout: technical issues go to the district help desk, "Do **NOT** contact Canvas, as they cannot resolve BioSig problems." The vendor logo lives at `web_resources/course_image/BioSig logo.jpg`.

### 4.11 Introduce Yourself Discussion Board (`g9459aa5eaf64b59f4a908e4827a7848c.xml`)

Institution default wording; instructor may edit. Settings in section 7. Body title at 24pt. Blocks (`h3`, 18pt): **Introduction** ("Hello, everyone! Let's take a minute to get to know one another before starting this course together."), **Directions** ("Please introduce yourself to the class. Here are some suggestions for topics to share:" then three numbered prompts: name and a little about yourself; why you took the course and what you hope to learn, degree or career plans; something unique, with an optional photo; then a privacy caution not to share phone numbers, email, or addresses), **How to Submit** (Reply / Post Reply instructions; "I encourage you to read through some of your peers' responses and 'like' or respond to at least one post from another participant. Remember to use names when you reply to your classmates..."; helpful-resource link to the vendor student guide).

### 4.12 Student Resources module pages

All seven are institution boilerplate. Keep verbatim from the named file if the page is kept; each embeds third-party media or links to district services.

| Page | File | Contents summary | Notes |
|---|---|---|---|
| How to Navigate Canvas as a Student | `how-to-navigate-canvas-as-a-student.html` | "What is Canvas?" intro with a right-floated photo (alt "Student at a computer"); vertical tab panels: Navigating in Canvas (embedded guided walkthrough iframe), Setting Up Your User Profile and Notification Settings (link plus embedded walkthrough), Canvas Support (Help menu: phone, live chat, instructor link, student guides, videos, and one link whose href is only `#`), the immersive reader feature built into Canvas. Progress-bar placeholder. | Two iframe embeds from a guided-walkthrough vendor with `sandbox` attributes. One dead link (`href="#"`). |
| Using Zoom as a Student | `using-zoom-as-a-student.html` | "What is Zoom?" with a decorative photo; note that online classes have no scheduled meetings and students should not create an account; accordion panels: How to Access Zoom in Canvas (two screenshots), How to Access Zoom via a Link (screenshots, one with fourteen stacked `<br>` tags), Zoom Screen Guide (annotated screenshot, eleven numbered items), Accessing Zoom Class Recordings, Adjusting Audio and Video in Zoom (embedded video), Zoom Support. | An `<a>` with only a screen-reader span and no visible text appears in the intro. Screenshots live under `web_resources/external_imports/`. |
| Communicating Online | `communicating-online-3.html` | Intro sentence; uploaded MP4 with English caption track and closed-caption instruction; "Key Points from the Video" (ten numbered netiquette points); "Zoom Communications" (six points plus a note on video-meeting intrusions). Progress-bar placeholder. | The only page whose body content sits directly under the wrapper rather than inside `dp-content-block` divs (apart from the last block). |
| Academic Integrity | `academic-integrity.html` | "Overview" with photo (alt "Student writing a paper on a laptop"), links to each college's student code of conduct; "Academic Integrity Policies and Resources"; accordion: Types of Academic Integrity Violations (seven pop-up definitions: Sale of Academic Product, Academic Enticement or Influence, Academic Misconduct, Cheating, Fabrication, Collusion, Plagiarism), What is Plagiarism and How Do I Avoid It? (definition, link, embedded video, three real-world plagiarism cases naming actual people), Citation Tools and Resources (citation generator link, three style-guide links, five-college library table with caption "College Library Information", columns College / Email / Phone). Progress-bar placeholder. | The pop-up definitions are the district's Student Code of Conduct definitions. The accordion wrapper is inside a bare `div#kl_panel_block_0` rather than a `dp-content-block`. |
| Canvas and Tech Support | `canvas-and-tech-support.html` | "Overview": help desk issues list (password reset, browser, pop-ups, equipment checkout, Zoom, low-cost internet, troubleshooting) and information to have ready (last four of SSN, ACES ID, date of birth, Banner ID); horizontal tab panels: Canvas Support (Student Quick Guide, Help menu resources, phone option), District Help Desk (phone, toll-free, email, hours), College Help Desk (loaner laptops and hotspots; five-college phone table with caption). Progress-bar placeholder. | |
| Academic & Student Support Resources | `academic-and-student-support-resources-2.html` | "Overview" list of services; "NLC Student Support Resources" vertical tabs: Academic Advising, Library, Tutoring Service (campus tutoring plus a third-party online tutoring service reachable from the portal or a course-navigation link), Veteran Affairs, Mental Health Counseling, Student Accessibility Services (with the dual-credit info callout and the accommodations office contact); "Additional Resources": five linked college support-services banner images (alt text "<College> Support Services Button"). Progress-bar placeholder. | Banner images live under `web_resources/College Logos/`. |
| Uploading a Paper to Turnitin Using Canvas | `uploading-a-paper-to-turnitin-using-canvas.html` | One block: embedded video, file limits (under 40 MB, at least 20 words, under 400 pages), link to the vendor's system requirements, district support phone. | |

### 4.13 Respondus LockDown Browser module

Institution boilerplate, service-specific.

- **Download and Install Respondus LockDown Browser** (`download-and-install-respondus-lockdown-browser.html`): explains the locked testing browser, embeds a 1:20 vendor video with a linked transcript (`web_resources/Uploaded Media 2/Introduction to Respondus LockDown Browser for Students Transcript.docx`), gives download links for two desktop operating systems and one tablet platform with the institution's download id, the instruction to choose the production Canvas environment on launch, incompatibility with phones and with the other major mobile platform, two campus computer labs, help-desk numbers, an info callout to reinstall the latest version, and "Using LockDown Browser for Online Exams" with five exam-day rules.
- **Test Respondus LockDown Browser** (quiz; settings in section 7).

### 4.14 Q & A Community module

- **Q & A Discussion Board** (`gbfac8569c65b90b366b86a88acdb34cf.xml`): instructor-default wording. Title at 18pt. **Introduction**: "Welcome to our Question and Answer Discussion Board!" "This is a great place for asking questions about our course and interacting with your classmates." Helpful hint about the Subscribe button. **Directions**: "Please comment below if you are confused by an assignment, don't understand a concept, or just have a general reflection on the course material that you would like to share with the class." "I will be responding to your questions here, but you should also feel free to respond to one another." "If you know the answer, please jump in!" **How To Submit**: Reply / Post Reply text (it says "type your introduction," a leftover from the Introduce Yourself board) and the vendor student-guide link. Settings in section 7.

### 4.15 Syllabus

`course_settings/syllabus.html` has an empty body. The Canvas Syllabus tab is hidden in the navigation (section 6.3). The Welcome page refers to "your Simple syllabus" and the home page tells students to click "Course Syllabus" in the left navigation, which must therefore be one of the external tools in the tab list. The template supplies no syllabus content and no syllabus acknowledgment activity.

---

## 5. Placeholder convention and what must be removed

Quoted instruction from "How to Use This Layout":

> "Throughout the layout you will see text that is highlighted yellow and/or placed in brackets to signify that this is an element for you to edit. For example: **Welcome to [Insert course title here]!** First, you want to enter edit mode by clicking **Edit** at the top-right of the page you are working on. Next, delete the yellow highlighted text and replace it with your course information. **Be sure to remove yellow highlighting** when you are done. For example: Welcome to Introduction to Chemistry!"

### 5.1 Forms the placeholders take

1. **Yellow highlight with brackets** (the standard form, 49 occurrences):
   ```html
   <span class="phpally-ignore" style="background-color: #fbeeb8;">[Briefly introduce the main topic of the unit/module]</span>
   ```
   The color is `#fbeeb8` (pale yellow). The `phpally-ignore` class keeps the accessibility scanner from flagging the low-contrast highlight. Both the span and the class go away with the text.
2. **Yellow highlight without brackets**: "Provide the catalog description of your course here." (Welcome), "Below is an example of textbook information" (Course Material), the topic heading `[Insert topic/concept here]` where the whole `h3` text is highlighted.
3. **Brackets without highlight**: `[Insert Course Title]`, `[insert course name and number]`, `[Insert a welcome message or brief description of the course]` (home); `[Provide your contact information and any office hours that you will provide.]` (Meet Your Instructor); `[Enter author's name]`, `[enter publisher's name e.g., ...]` (the example names a real publisher), `[enter edition, e.g., 8th]`, `[ enter number, e.g., ...]` (the example is a 13-digit ISBN) (Course Material); `Module [#]` and `Module [Insert #]: [Insert Topic and Dates]` in page and module titles.
4. **Red text placeholders** on the home page Instructional Delivery block: `##`, `(Insert Date here)`, `(insert date)`, `(Insert days and times)`, `(insert Building and Room number)`, `Day`, `___`, `a.m`, `(insert hyperlink to recurring session)`, styled `color: #ca1325`, `#cf311f`, `#df0000`, or `#cb2b19` with `background-color: #ffffff; font-style: normal;`.
5. **Capitalized token**: `COURSE TITLE` in the Welcome page title.
6. **Parenthetical instructions** appended to a placeholder: "(make sure to remove the highlight from the text)", "(Remove this line after you complete)", "(Module to be duplicated and pages MUST be edited)".
7. **Instruction sentences in plain text** that read as directions to the author, not to students: "Provide a brief introduction about yourself for your students..." (Meet Your Instructor), "On this page, you can provide information regarding your course grading and evaluation." (Course Evaluation).
8. **Sample data**: the three sample rows in the Overview tasks table, the six "Module N" rows in the Course Schedule, the example textbook block, the blank avatar image (alt "Blank Image "), the `1.2.` and `1.3.` empty objective items.
9. **Bracketed "Helpful Resource" links** to the vendor's instructor and student guides, wrapped in the yellow highlight: on Content, Discussion, Quiz, and Assignment templates. Unbracketed "Helpful Resource:" lines in the How to Submit blocks are student-facing and were left by the template author as permanent text.

### 5.2 Removal checklist

Before a page is published, none of the following may remain:

- Any `background-color: #fbeeb8` style.
- Any `[` ... `]` bracket text that is a placeholder (bracket text that is genuine content, such as a citation, is fine).
- Any red-text delivery placeholder and the two delivery variants that do not apply.
- The parenthetical author instructions.
- The plain-text author instructions on Meet Your Instructor and Course Evaluation.
- Sample table rows, the example textbook block, the blank avatar, and the empty numbered objective items.
- The bracketed helpful-resource links.
- `COURSE TITLE`, `[#]`, `[Insert #]`, `[Insert Topic and Dates]` in titles.
- The `phpally-ignore` class wherever it existed only to hide a placeholder.
- The "Faculty Resources DO NOT PUBLISH THIS MODULE" module and its two items, which are author-facing.

---

## 6. Course settings, learning outcomes, and rubrics

### 6.1 Course settings (`course_settings/course_settings.xml`)

| Setting | Template value | Note |
|---|---|---|
| title, course_code | `NLC-DLC Online Template` | Replace. |
| default_view | `wiki` | Home page is the front page (`home.html`). |
| syllabus_course_summary | `true` | Assignment summary shows on the Syllabus page. |
| group_weighting_scheme | `equal` | Assignment groups are **not** weighted in the export. |
| grading_standard_enabled | `false` | No letter scheme is applied. |
| license | `cc_by_nc_sa` | Creative Commons Attribution NonCommercial ShareAlike, also declared in the manifest metadata with copyright "yes". |
| is_public | `true` | Course content visible without login. |
| is_public_to_auth_users | `true` | |
| open_enrollment | `true` | |
| self_enrollment | `true` | Anyone with the join link may enroll. |
| indexed | `false` | |
| allow_student_wiki_edits | `false`; default_wiki_editing_roles `teachers` | Pages are teacher-editable only. |
| allow_student_discussion_topics | `true` | Students may create discussion topics. |
| allow_student_discussion_editing | `true` | |
| allow_student_forum_attachments | `true` | |
| allow_student_organized_groups | `false` | |
| lock_all_announcements | `false` | |
| show_announcements_on_home_page | `false`; home_page_announcement_limit `1` | |
| hide_final_grade, hide_distribution_graphs | `false`, `false` | |
| show_total_grade_as_points | `false` | |
| restrict_student_future_view, restrict_student_past_view | `false`, `false` | |
| restrict_enrollments_to_course_dates | `false` | |
| usage_rights_required | `false` | |
| conditional_release | `false` | |
| enable_course_paces | `false` | |
| default_post_policy.post_manually | `false` | Grades post automatically. |
| filter_speed_grader_by_student_group | `false` | |
| storage_quota | `524000000` | About 500 MB. |
| start_at, conclude_at | empty | |
| homeroom_course, horizon_course, content_library, career_learning_library_only | `false` | |

The public, open-enrollment, and self-enrollment flags are template-shell settings; whether they belong on a live section is a decision outside this document (section 9).

### 6.2 Assignment groups (`course_settings/assignment_groups.xml`)

| Position | Title | Weight |
|---|---|---|
| 1 | Assignments | 0.0 |
| 2 | Respondus LockDown Browser | 0.0 |

Every template assessment (Introduce Yourself, Discussion Template, Quiz Template, Assignment Template, BioSig) sits in "Assignments"; the Respondus practice quiz sits in "Respondus LockDown Browser". With `group_weighting_scheme` = `equal`, the weights are ignored and the total is points-based.

### 6.3 Grading standards (`course_settings/grading_standards.xml`)

Ten grading standard records are shipped, all version 2, `points_based` false, `scaling_factor` 1.0. They reduce to two distinct schemes:

- **Untitled, two copies:** A 0.90, B 0.80, C 0.70, D 0.60, F 0.00.
- **"LC" (four titled copies) and four untitled copies:** A 0.90, B 0.80, C 0.74, IP 0.00. ("IP" is the college's "in progress" mark used in place of D and F on some developmental courses.)

None is enabled (`grading_standard_enabled` false), so the template applies no letter scheme.

### 6.4 Tab configuration (course navigation)

The `tab_configuration` array lists tabs in display order, with `hidden: true` on those removed from the student menu. Built-in tabs are numeric; external tools are `context_external_tool_<id>`. Numeric ids interpreted with the standard Canvas course tab constants (verify against the target instance's Tabs API, which reports string ids such as `home`, `modules`, `syllabus`, before applying):

Visible, in order:

1. `0` Home
2. `14` Announcements
3. an external tool (unidentified)
4. `10` Modules
5. `8` Discussions
6. `5` Grades
7. ten external tools, in this order: two unidentified, then `context_external_tool_gf48f9fe3d8b380c499b7a9fd7db5c1b3` (this one is identified by the LTI file `gf48f9fe3d8b380c499b7a9fd7db5c1b3.xml` as **"NLC One-Click Tutoring"**, an LTI 1.1 redirect tool, privacy level anonymous, course-navigation enabled and public, redirecting to the college tutoring page), then seven more unidentified.

Hidden (in the order listed): `18` Rubrics, one external tool, `1` Syllabus, `4` Quizzes, `3` Assignments, `2` Pages, `11` Files, `15` Outcomes, `12` Conferences, `16` Collaborations, thirty-one further external tools, `6` People, and twelve more external tools.

So the student left menu is Home, Announcements, Modules, Discussions, Grades, and eleven institution tools (one of which must be the "Course Syllabus" item the home page refers to). Syllabus, Assignments, Quizzes, Pages, Files, People, Outcomes, Rubrics, Conferences, and Collaborations are hidden. External tool identities other than the tutoring redirect cannot be recovered from the export; they are account-level installs on the source instance.

Two other tool records ship: `lti_resource_links/gcc3273761a68b67ebf92be3bcf1caf2b.xml` is an LTI 1.3 resource link for a video hosting platform (described as "Video creation and playback") that nothing in the export references; `external_content/lti_96176.json` records no LTI assignments (`"assignments":[]`).

### 6.5 Files (`course_settings/files_meta.xml` and `web_resources/`)

Folders `Uploaded Media`, `Icon Maker Icons`, and `Uploaded Media 2` are hidden from students. `udoit.json` and the Teaching Checklist PDF are locked (instructor-only). Most individual media files are hidden (linked from pages but not browsable). The college logo file and the Study Skills PDF are visible.

Media files under `web_resources/`, by path:

- `Online Study Skills_pdf.pdf` (PDF, study-skills handout)
- `udoit.json` (22 bytes; see section 8)
- `Uploaded Media/Communication Guidelines-1080p-231129.mp4` (MP4, about 12 MB, captioned via media_tracks.xml)
- `Uploaded Media/Cover page example` (PNG, 200 by 247, sample textbook cover, no extension)
- `Uploaded Media/Student using laptop` (JPEG, 640 by 427, stock photo, no extension)
- `Uploaded Media/Teaching Checklist-OnlineHybrid Education Courses` (PDF, 2 pages, no extension)
- `Uploaded Media/person-using-a-mac-book-pro-4050287-1.jpg` (JPEG, 213 by 320, stock photo)
- `Uploaded Media/personal-file.png` (PNG, 512 by 512, blank avatar)
- `Uploaded Media 2/Introduction to Respondus LockDown Browser for Students Transcript.docx` (Word transcript)
- `Alternate Files/Uploaded Media 2/2E_Online_PG_StudySkills_pdf.pdf` (duplicate of the study-skills PDF)
- `Alternate Files/Uploaded Media 2/Teaching Checklist-OnlineHybrid Education Courses_pdf.pdf` (PDF, 2 pages, the copy linked from the faculty module)
- `College Logos/alamo_nelake_logo` (JPEG, 1589 by 187, no extension), `alamo_nwvista_logo.jpg`, `alamo_paloalto_logo.jpg` (1651 by 196), `alamo_sanantonio_logo.jpg`, `alamo_stphillips_logo.jpg` (support-services banner buttons)
- `course_image/BioSig logo.jpg` (JPEG, 514 by 74, vendor logo)
- `Icon Maker Icons/Closed Caption icon.svg` (SVG, category `icon_maker_icons`)
- `external_imports/1100x330-NLC-cidilab-banner20250701_150015.jpg` (JPEG, 1100 by 330, home banner)
- `external_imports/Roadmap20250701_150023.png` (PNG, 1100 by 1650, roadmap graphic)
- `external_imports/5cf751d9-8d9d-4409-bb19-475227e187fc20260112_144937.png` (PNG, 464 by 290, "please wait for the host" screenshot)
- `external_imports/Accessing a Recording in Canvas.jpg` (JPEG, 1130 by 380, screenshot)
- `external_imports/How_to_Join_a_Zoom_Meeting_-_Canvas_Student.pdf` (PDF, 2 pages)
- `external_imports/Zoom Link.jpg` (JPEG, 212 by 339, screenshot)
- `external_imports/Zoom Meetings - Student.jpg` (JPEG, 1151 by 367, screenshot)
- `external_imports/Zoom Start from Browser.jpg` (JPEG, 1213 by 568, screenshot)
- `external_imports/person-writing-on-notebook-4145194-1.jpg` (JPEG, 427 by 640, stock photo)
- `external_imports/zoom user interface student.jpg` (JPEG, 3216 by 1746, about 1.7 MB, annotated screenshot)

At least one stock photo ("Student using laptop") carries embedded copyright metadata from a stock-photo agency, and a second carries professional camera metadata; treat both as licensed to the college, not freely reusable.

### 6.6 Learning outcomes (`course_settings/learning_outcomes.xml`)

Five outcomes ship. Each was copied from an account-level outcome (each has a `copied_from_outcome_id`), so account-level outcomes exist on the source instance at least for these. All use `calculation_method` = `highest`, `points_possible` 4.0, `mastery_points` 0.0, five ratings (4, 3, 2, 1, 0), and each is aligned to the same rubric (`g3d5cb49863589104687f188ba2fd9e88`, "Critical Thinking Skills Rubric") with `mastery_type` = `explicit_mastery`.

| Outcome title | Rating labels (4 to 0) |
|---|---|
| Explanation of Issues | Excellent / Good / Fair / Poor / No Evidence, with full descriptors for how clearly the issue is stated and described |
| Evidence | Excellent / Good / Fair / Poor / No Evidence, on interpretation and evaluation of expert sources (the Excellent and Good descriptors are identical in the export) |
| Position/Analysis presented (perspective, thesis/hypothesis) | Excellent / Good / Fair / Poor / No Evidence |
| Conclusions and related outcomes (implications and consequences) | Excellent / Good / Fair / Poor / No Evidence |
| Student Degree Pathway | AAS 4 / AS 3 / AAT 2 / AA 1 / Other 0 (a demographic tag, not a skill) |

These are institution-wide critical-thinking assessment outcomes. None corresponds to a course learning objective.

### 6.7 Rubrics (`course_settings/rubrics.xml`)

Eleven rubrics ship. None has an association to a template assignment recorded in the export. All are `reusable` false, `public` false, `read_only` false, `hide_score_total` false, `free_form_criterion_comments` false.

**The outcome-linked rubric:**

- **Critical Thinking Skills Rubric**, `points_possible` 0.0, `rating_order` descending, five criteria each worth 4.0 with `mastery_points` 0.0 and `ignore_for_scoring` true, each linked by `learning_outcome_identifierref` to one of the five outcomes above and carrying the outcome's five ratings verbatim. Because every criterion is ignored for scoring, this rubric records outcome results without affecting the grade.

**Discussion rubrics** (three-level, no outcome links):

- **Discussion Post Rubric New (1)**, 10 points: Development of ideas (4: "Well-developed ideas; introduces new ideas; stimulates discussion" / 2: "Developing ideas; sometimes stimulates discussion" / 0: "Did not enter the discussion."); Evidence of critical thinking (4: "Clear evidence of critical thinking (application, analysis, synthesis, and evaluation)..." / 2: "Some evidence of critical thinking. Postings tend to address peripheral issues." / 0); Response to instructor and other students (2: "Interacts at least 1 time per week with classmates and 1 time per week with instructor" / 1: "Interacts at least once with the instructor and/or classmates." / 0).
- **Discussion Post Rubric (short)**, 6 points: the same three criteria at 2 / 1 / 0, with the response criterion reading "Interacts at least 2-3 times per week with the instructor and/or classmates."
- **Ice Breaker Discussion Post Rubric**, 10 points: Background Information (5: "Well-developed reply including all requested information" / 2.5: "Reply includes only partial and/or incomplete information" / 0: "Did not post in the discussion."); Response to students (5: "Well developed response to at least 1 participant's post" / 2.5 / 0). This is the rubric shaped for the Introduce Yourself board.
- **B: Module 1 Discussion**, 15 points: four criteria (three "Addressed multiple means of representation / action/expression / engagement" at 4 / 2 / 0 and "Responded to colleague (thoughtfully)" at 3 / 1.5 / 0). Leftover from a faculty training course.

**Leftover rubrics from other courses** (Full Marks / Partial Marks / No Marks pattern unless noted): Accessibility Action Plan (10 pts, 3 criteria); Accessible PPT (13 pts, 6 criteria); Captioned Video (11 pts, 3 criteria); Accessible Canvas Page (11 pts, 5 criteria: sections with headings, heading hierarchy, image alt text, table with caption and header row/column, descriptive hyperlink); Accessible Doc (13 pts, 6 criteria); Lab Skills Grade Rubric (100 pts, 14 criteria, five-level, culinary lab).

The "Accessible Canvas Page" rubric is worth noting as a statement of what the institution treats as an accessible page: distinct sections with appropriate headings, correct heading hierarchy, alt text on images, tables with a caption and header row or column, and descriptive link text.

### 6.8 Question banks (`non_cc_assessments/`)

Nine question banks ship in addition to the two quizzes. None is attached to a module quiz. They are leftovers and should not be recreated:

- "Unfiled Questions" (5 items: multiple choice and true/false about a sister college's founding and Canvas features)
- "Unfiled Questions" (8 items: same kind, plus dated items)
- "Unfiled Questions" (9 items: assorted sample questions including arithmetic and algebra)
- "Unfiled Questions" (2 true/false items at 10 points each about a discussion rubric and a two-week non-participation drop policy)
- "Imported Questions" (four identical banks of 8 essay items surveying faculty about a training course)
- "Color Swatches" (22 multiple-choice items asking whether a foreground/background color pair is accessible)

---

## 7. Quizzes and discussions the template ships

### 7.1 Discussions

| Setting | Introduce Yourself Discussion Board | Discussion Template | Q & A Discussion Board |
|---|---|---|---|
| File | `g9459aa5eaf64b59f4a908e4827a7848c.xml` + meta `g6216ed2469df8e0e164c6ac8cc7333b5.xml` | `g847792aeffe6dda52129a8c2043151e8.xml` + meta `g6494c5ce0bd5689b7dfdd4697d2d7ec2.xml` | `gbfac8569c65b90b366b86a88acdb34cf.xml` + meta `g8cbaa92159bded84edd4ec82edff4416.xml` |
| Module | Orientation, item 10 | Weekly template, item 3 | Q & A Community, item 1 |
| type | topic | topic | topic |
| discussion_type | threaded | threaded | not_threaded |
| pinned | (not set) | (not set) | true |
| graded | yes (assignment attached) | yes (assignment attached) | no |
| points_possible | 1.0 | 0.0 | (none) |
| grading_type | points | points | |
| assignment group | Assignments | Assignments | |
| submission_types | discussion_topic | discussion_topic | |
| workflow_state | active / assignment published | active / assignment published | active |
| allow_rating (likes) | true | false | false |
| only_graders_can_rate, sort_by_rating | false, false | false, false | false, false |
| sort_order / locked | desc / false | desc / false | desc / false |
| expanded / locked | false / false | false / false | false / false |
| due, unlock, lock dates | none | none | none |
| peer reviews | off | off | |
| group discussion | no | no | no |
| todo_date | none | none | none |
| module completion requirement | must_contribute | none | none |

### 7.2 Quizzes (Classic Quizzes)

| Setting | Quiz Template | Test Respondus LockDown Browser |
|---|---|---|
| Files | `g393030ef9fcbd8bad83607baa3955ef3/assessment_meta.xml`, `assessment_qti.xml`, `non_cc_assessments/g393030ef9fcbd8bad83607baa3955ef3.xml.qti` | `gb9857bd64f455aeeb8e384ec0f04e701/assessment_meta.xml`, `assessment_qti.xml`, `non_cc_assessments/gb9857bd64f455aeeb8e384ec0f04e701.xml.qti` |
| Module | Weekly template, item 4 | Respondus LockDown Browser, item 2 |
| quiz_type | assignment (graded) | assignment (graded) |
| points_possible | 0.0 | 1.0 |
| assignment group | Assignments | Respondus LockDown Browser |
| questions | 0 | 1 true/false: "I was able to download, install and launch Respondus Lockdown Browser, and I am ready to use this software with my online quizzes and exams." Correct: True. Feedback on True: "Excellent! You've successfully installed and launched Respondus LDB." On False: "Oops! Do you want to try that again? :)" |
| allowed_attempts | 1 | unlimited (-1) |
| scoring_policy | keep_highest | keep_highest |
| time_limit | none | 2 minutes |
| shuffle_answers | false | false |
| show_correct_answers | true | true |
| show_correct_answers_last_attempt | false | false |
| hide_results | (empty: results shown) | (empty) |
| one_question_at_a_time / cant_go_back | false / false | false / false |
| require_lockdown_browser | false | true |
| require_lockdown_browser_for_results / monitor | false / false | false / false (monitor data blob present) |
| anonymous_submissions | false | false |
| available / could_be_locked | true / true | true / true |
| one_time_results | false | false |
| disable_timer_autosubmission | false | false |
| due, unlock, lock dates | none | none |
| workflow_state | published | published |
| description | the Quiz Template body (section 2.3.4) | three sentences: objective is to learn to use the locked browser; answer the question to confirm; contact the IT help desk with installation issues |

QTI (Question and Test Interoperability, the XML format for quiz questions) metadata on the Quiz Template: `cc_profile` cc.exam.v0p1, `qmd_assessmenttype` Examination, `qmd_scoretype` Percentage, `cc_maxattempts` 1.

### 7.3 Assignments

| Setting | Assignment Template | BioSig Instructions and Practice Assignment |
|---|---|---|
| Files | `g065eabf68adfdd4808adcef508c6f13f/assignment_settings.xml`, `assignment-template.html` | `g7f9f34566cb7bf279429de1d99ab82cc/assignment_settings.xml`, `biosig-instructions-and-practice-assignment.html` |
| Module | Weekly template, item 5 | Orientation, item 9 |
| submission_types | online_text_entry, online_upload | external_tool |
| points_possible | 0.0 | 1.0 |
| grading_type | points | points |
| assignment group | Assignments | Assignments |
| allowed_extensions | (none) | (none) |
| workflow_state | published | published |
| due, unlock, lock | none | none |
| peer reviews, group, moderated, anonymous grading | off | off |
| turnitin_enabled | false | false |
| omit_from_final_grade | false | false |
| post policy | automatic | automatic |
| external tool | | LTI launch to the identity-verification vendor, `external_tool_new_tab` false |
| module completion requirement | none | must_submit |

### 7.4 Syllabus quiz or acknowledgment

None. The template ships no syllabus quiz, no acknowledgment assignment, and no orientation quiz.

---

## 8. Accessibility guidance the template carries

### 8.1 `web_resources/udoit.json`

The file's entire content is a single JSON object with one key, `courseId`, whose value is the source course's numeric id. It is a marker written by UDOIT (Universal Design Online content Inspection Tool, the district's Canvas accessibility scanner) to tie scan history to the course. It contains no findings, no rules, and no guidance. It is locked (instructor-only) in Files. Do not copy it into a new course; the target instance's scanner will create its own if it is installed.

### 8.2 Written guidance

- Teaching Checklist: "Check Course Accessibility (alt-text for images, color contrast, video captions or transcripts, etc.). Consult with your institution's accessibility services office, especially if you have students with documented requests for accommodations that could be impacted by the differing class delivery modalities (i.e., hybrid/blended course, online)." and "Check the broken links to documents, websites, images, and videos in your Modules using UDOIT or Validate links Tools in Canvas. Ensure the videos have closed captions."
- Course Schedule placeholder: "...or attach your course schedule as an accessible Word or PDF document."
- The "Accessible Canvas Page" rubric (section 6.7) lists the institution's page criteria: distinct sections with appropriate headings, correct heading hierarchy, image alt text, tables with caption and header row or column, descriptive hyperlinks.
- The Navigate Canvas page promotes the immersive reader feature built into Canvas (font customization, syllable splitting, sentence highlighting, text-to-speech) as an accessibility feature students can activate once.
- The Course Policies privacy table gives students each vendor's accessibility statement.

### 8.3 Conventions observed in the markup

**Headings.**
- No `h1` in any page body. The page title is an `h2.dp-heading` inside the header bar (Canvas supplies the `h1`).
- Major sections are `h3`; subsections are `h4`. Panel (tab or accordion) headings are `h3.dp-panel-heading` at the same level as section headings, except the Student Privacy panels, which drop to `h4`.
- Heading text is never carried by an icon alone; the `<i>` is `aria-hidden` and the text follows in a span.
- Paragraphs that begin with bold text carry `dp-heading-ignore` so DesignPLUS does not mistake them for headings.
- Deviations present in the template (do not reproduce): an empty `h2` wrapping an image (Meet Your Instructor); `h3` headings nested inside panel content (Zoom, Academic Integrity); a heading whose only text is a highlighted placeholder (Content page).

**Images.**
- Informative images get descriptive alt text: "Northeast Lakeview College" (banner), "Student at a computer", "Student writing a paper on a laptop", "Zoom link in the left-hand course navigation", "Cloud recordings tab on the Zoom page in Canvas", "Screen view of a Zoom meeting", "When launching Zoom from a link, click start from your browser on the bottom of the page.", "Pop-up screen that reads 'please wait for the host to start this meeting'", "<College> Support Services Button" on linked banner buttons.
- Decorative images get `role="presentation"` and `alt=""`: the welcome banner, the roadmap graphic, the textbook cover example, the photo on the Zoom page, one Zoom screenshot, the vendor logo, the closed-caption icon.
- Every image carries explicit `width` and `height` and `loading="lazy"`.
- One placeholder alt ("Blank Image ") must be replaced with the instructor's photo alt text.

**Tables.**
- Every data table has a `<caption>`, a `<thead>` with `th scope="col"`, and where rows have names, `th scope="row"` in the body (Overview tasks table). The Course Schedule and privacy tables use plain `td` in the first column.
- Wide tables sit inside `div.dp-table-scroll` so they scroll horizontally on small screens instead of breaking the page.
- Layout is never done with tables; the grid uses Bootstrap rows and columns.

**Links.**
- Link text is descriptive ("Canvas Student Guide: How do I reply to a discussion as a student?", "Study Smarter Handout"), with two exceptions to avoid: a link whose visible text is only a screen-reader span, and a link with `href="#"`.
- Off-site links open in a new tab (`target="_blank"`) and carry the Canvas `external` class or `dp-ext-ignore`; when the Canvas marker is used, a `screenreader-only` span says "Links to an external site."

**Media.**
- Every video iframe has a `title` attribute, except the vendor video on the BioSig assignment (missing); six use the video platform's generic "video player" title and one says only "embedded content." Descriptive titles ("Canvas Overview (Students)", "How do I manage my Canvas notification settings?") are the better pattern in the template.
- The one uploaded video has an English caption track in `media_tracks.xml` and an on-page instruction to turn captions on. The Respondus video links a Word transcript. The BioSig video is labeled "(This video is Closed Captioned)".

**Color and contrast.**
- Emphasis on dates and rules uses bold together with dark red `#ba372a`; the meaning does not depend on color alone.
- The yellow placeholder highlight `#fbeeb8` is marked `phpally-ignore` because it fails contrast; it must not survive into published pages.
- Red placeholder text on the home page (`#ca1325` and similar) likewise must not survive.

**Text size.**
- Sizes are set with inline `font-size` in points (12, 14, 18, 24). This is the Canvas editor convention; it is not a semantic signal.

**Icons.**
- Icons are always `<i class="fas fa-..." aria-hidden="true">` with the hidden `dp-icon-content` span, so screen readers skip them. The template's own lapses (`fas fa-user-graduate` tile icon and the `fa-hand-point-right` button icons without `aria-hidden`) should be corrected when copied.

**Scanner suppression.**
- `phpally-ignore` appears 59 times. Apart from placeholders, it suppresses warnings on third-party iframes and one vendor link. A rebuilt page should need it nowhere.

---

## 9. Conflicts and gaps between the build prompt and the template

Each item states what the template does and what the build prompt says. None is resolved here. Section references are to this document; prompt quotations are from `builder/docs/build-prompt-v1.3.md`.

1. **Weekly page structure.** The prompt requires "One identical page template every week, within whatever the NLC template specifies: Overview, Objectives, Read/Watch, Sidebar, Lab, Discussion, Submit, Check Yourself." The template specifies four separate module items in a fixed order: an Overview page (introduction, Learning Objectives, Tasks table with LO alignment and due dates, Next line), a Content page (topic blocks and a Sources block), assignment items (discussion, quiz, assignment as separate Canvas objects with their own Introduction / Directions / Grading Criteria / How to Submit bodies), and a Wrap-up page (What You Learned!, What You Did!, What's Next?). The prompt's eight sections do not map one-to-one onto the template's pages, and the template's Sources, Tasks table, and Wrap-up page have no counterpart in the prompt's list.

2. **Module naming.** The template names modules `Module [Insert #]: [Insert Topic and Dates]` and pages `Module [#] Overview` and so on. The prompt says "One module per week, named for the week." The template's convention includes a topic and dates in the module title.

3. **Which modules exist.** The prompt lists Start Here, Week 0, and Weeks 1 through 8. The template ships Faculty Resources (unpublished), Orientation Module, Student Resources, Respondus LockDown Browser, Q & A Community, and one weekly module, and its guidance text describes "an Orientation Module and then eight weekly modules." The prompt does not mention Student Resources, Respondus, or Q & A modules; the template does not have a Week 0 or an exam-only module. The prompt's "All modules published" cannot apply to the Faculty Resources module, which is labeled "DO NOT PUBLISH."

4. **Start Here naming and contents.** The prompt calls the first module "Start Here" and lists its minimum contents (how the course works, week 0 self-assessment, how to get help including help for a dead notebook kernel and API key contacts, AI use policy, syllabus and acknowledgment). The template calls it "Orientation Module," opens with a page titled "Welcome! Start Here:", and has fixed contents (Meet Your Instructor, Course Material, Course Policies, Course Evaluation, Course Schedule, Tips for Success, OLRN-0001, BioSig, Introduce Yourself). None of the prompt's five minimum items has a dedicated template page, and several template pages (Course Material for textbooks, Tips for Success) have no counterpart in the prompt.

5. **Completion requirements and locking.** The prompt: "All modules published and available from day one. No completion requirements, no module prerequisites... Due dates are set per week, but nothing locks." The template's Orientation Module carries four completion requirements (view Course Material, view Course Schedule, contribute to Introduce Yourself, submit BioSig), and the home page states "You must complete all tasks in the Orientation Module to access the next module of this course." The export records no module prerequisite, so the sentence describes an intended lock that the export does not implement.

6. **Late work.** The template's Course Policies page ships "I do **NOT** accept late work" and "the Canvas LMS is designed to automatically 'lock' activities and assignments after the deadline." The prompt says late work and resubmission policy is "Not yet set," that "nothing locks," and that a student who exhausts the token budget gets a top-up "with no grade penalty and no late penalty for the delay."

7. **AI use policy.** The template's "Artificial Intelligence (AI) Tools" panel prohibits AI tools unless an assignment authorizes them, reserves the right to run AI detection, requires students flagged by detection to prove originality with drafts and revision history, recommends composing in a specific cloud document tool, and sets a zero for violations with possible course failure. The prompt: "Students will use AI on this work. Assume it and write a course AI use policy that permits it with disclosure." The two policies point in opposite directions, and the template's text cites a district procedure number.

8. **Introduce Yourself discussion and the grade scheme.** The template's Introduce Yourself board is graded at 1 point, threaded, with likes on, in the "Assignments" group, and required for module completion. The prompt's grade weighting is "Labs 60, final exam 20, discussions 12, self-checks 8. Total 100," with discussions defined as "One graded discussion per week, tied to that week's lab" whose prompts "must require the student's own results." An orientation introduction fits neither the weekly-lab definition nor any named category, and the prompt does not say where its point would count.

9. **BioSig identity verification.** The template requires a 1-point external-tool assignment through a biometric identity-verification vendor, described as a district initiative, with a `must_submit` completion requirement, and lists the vendor in the privacy table. The prompt: "Zero external services is the target. If one is unavoidable it must permit users aged 13 and up, require no payment, and require no account with personal information. Cite the specific terms-of-service clause." The prompt also says nothing may display credentials; the BioSig activity creates a credential.

10. **Respondus LockDown Browser.** The template ships a module that instructs students to download and install a locked browser (two desktop operating systems and one tablet platform; not phones) and a 1-point practice quiz that requires it, in a dedicated "Respondus LockDown Browser" assignment group. The prompt: the final is "Open book, online, no proctor," and the student environment is "No local installs, no Docker, no CLI, no admin rights."

11. **Q & A Discussion Board.** The template ships a pinned, ungraded, non-threaded course-wide Q&A board in its own module, linked from a home-page tile, in which the instructor promises to respond. The prompt's help path is "instructor contact and response time, campus tech support, what to do when the Jupyter kernel dies or the session times out, who to contact about the API key." The prompt neither requires nor excludes a Q&A board.

12. **OLRN-0001.** The template states that students new to online courses "are required to enroll in a free Orientation to Online Learning (OLRN-0001) mini-course" and that the instructor "will be checking for proof of successful completion (80% or higher on the post-test)" in the first week. The prompt names one enforced prerequisite (the AI fundamentals course) and does not mention OLRN-0001.

13. **Grading standard and assignment groups.** The template ships two letter schemes (A/B/C/D/F at 90/80/70/60, and "LC" A/B/C/IP at 90/80/74/0), neither enabled, and two assignment groups ("Assignments" and "Respondus LockDown Browser") at zero weight with `group_weighting_scheme` = `equal`. The prompt requires four weighted groups (labs 60, final 20, discussions 12, self-checks 8) and does not name a letter scheme. The template's own guidance says "Be sure to properly weight your assignments," so weighting is expected, but the template's groups and scheme do not match the prompt's.

14. **Learning outcomes.** The template ships five account-derived critical-thinking outcomes plus "Student Degree Pathway," all aligned to a zero-point "Critical Thinking Skills Rubric" whose criteria are ignored for scoring. The prompt requires six Canvas Outcomes, one per CLO, "one consistent mastery scale," each linked to the rubric criteria that measure it, and says breadth topics get no Outcomes. The prompt also says to check for account-level Outcomes matching the program before creating course-level ones; the template proves account-level Outcomes exist on the source instance, but for critical thinking, not for the CLOs. Whether the template's five outcomes and rubric are kept alongside the six CLO outcomes is not addressed by either document.

15. **Rubric shape.** The prompt requires "A Canvas rubric of 3 to 5 criteria with explicit points, 3 to 4 performance levels, each criterion linked to its Canvas Outcome, and each gradeable without running student code." The template's discussion rubrics have three criteria and three levels (fits) but no outcome links, and their interaction criterion expects "at least 2-3 times per week" or "1 time per week with classmates and 1 time per week with instructor," while the prompt sets one post plus one substantive peer reply at 15 to 20 minutes. The template's other nine rubrics belong to unrelated courses.

16. **Syllabus.** The prompt places "Syllabus and a syllabus acknowledgment" in Start Here and says the syllabus states the token budget policy and the AI use policy. The template's Canvas Syllabus tab is hidden, `syllabus.html` is empty, the Welcome page says outcomes come "from your Simple syllabus," and the home page directs students to a "Course Syllabus" item in the left navigation that is an external tool not present in the export. The template has no acknowledgment activity.

17. **Course navigation.** The prompt says to conform to the template's navigation. The template's visible menu is Home, Announcements, Modules, Discussions, Grades, and eleven external tools whose identities (except a tutoring redirect) cannot be recovered from the export; Syllabus, Assignments, Quizzes, Pages, Files, People, Outcomes, Rubrics, Conferences, and Collaborations are hidden. The prompt relies on Outcomes ("the program pulls outcome data from Canvas"), Classic Quizzes, and rubric-graded assignments; hiding those tabs does not disable the features, but the prompt's "Verify the token scopes needed for Classic Quizzes" and outcome reporting assume the tools are reachable by staff.

18. **Technology requirements and minimal skills.** The template's Course Policies page requires students to save documents in .doc or .docx using a named desktop word processor, edit word-processor formatting, "Upload writing assignments in the assigned format," and "Access Zoom and navigate the essential functions of a Zoom meeting (for office hours)." The prompt: "Students have a computer, internet, and a browser. Nothing else," submissions are a screenshot, one exported .txt or .json file, and a short text answer, and the course is "fully asynchronous."

19. **Third-party services in Student Resources.** The template's Student Resources and orientation pages embed videos from public video platforms and a guided-walkthrough vendor, link a citation-generator site, a third-party online tutoring service, a plagiarism-detection service page, and a video-conferencing service page, and the privacy table lists sixteen vendors. The prompt: "Zero external services is the target" and "Anything linked externally must be openly licensed ... attributed, and verified to resolve." The prompt's rule is written for course content; whether it extends to institution-supplied resource pages is not stated.

20. **Course week and due day.** The template fixes the course week as Monday through Sunday 11:59 PM with everything due Sunday, and the Overview tasks table column is "Due date/Time (CST)." The prompt says "Due dates are set per week" without naming a day or a time zone. Not contradictory, but the template constrains the choice.

21. **Feedback turnaround.** The template ships specific commitments: messages answered within 24 to 48 hours excluding weekends and holidays, grades and feedback one week from the due date; the Teaching Checklist says "typically within seven days." The prompt requires "A stated feedback turnaround commitment on labs" without a value. Compatible; the template supplies the default numbers.

22. **Weekly objectives format.** The template numbers objectives `1.1`, `1.2`, `1.3`, opens with "By the end of this module, you will be able to:", asks for "a Bloom's Taxonomy action verb," and maps activities to LOs in a table with no column for a parent course objective. The prompt requires 2 to 3 objectives per week, each "tagged with its parent CLO," 20 words or fewer, with banned verbs. The template's table has no place for the CLO tag.

23. **Course Material page.** The template expects textbook images, author, publisher, edition, ISBN, bookstore information, and a mandatory statement that students need not buy from the college bookstore. The prompt says "Expect to author most readings rather than link out" and names no textbook. The page's purpose does not apply, but the bookstore statement is institutional text.

24. **Course visibility and enrollment flags.** The template's `is_public`, `is_public_to_auth_users`, `open_enrollment`, and `self_enrollment` are all `true`. The prompt says nothing about visibility or enrollment. Copying the template's settings would make the new course publicly visible and self-joinable.

25. **License.** The template is licensed CC BY-NC-SA in both the manifest and course settings. The prompt lists "Course ownership and licensing, unresolved" as a risk-register item.

26. **Placeholder assessment items are published.** The template's Discussion Template, Quiz Template, and Assignment Template are published in the export and placed in the weekly module, while the template's own guidance says they are unpublished and live on the Assignments page. The prompt says all modules are published from day one. A copied-but-unedited template item would be visible to students.

27. **Week 0 and Week 8 have no template pattern.** The template's module anatomy assumes graded assignments and a Content page. Week 0 is "Optional but strongly recommended, ungraded" with a self-assessment; Week 8 is "the final exam only, with no new instruction." Neither fits Overview / Content / assessments / Wrap-up without leaving blocks empty.

28. **Accessibility checker zero-error target versus template markup.** The prompt requires "Zero errors in the Canvas Accessibility Checker." The template pages carry an iframe with no title, a link whose only content is a screen-reader span, a link to `#`, an empty `h2` around an image, fourteen stacked line breaks, headings nested inside panel bodies, and `phpally-ignore` suppressions. Keeping institution pages verbatim may carry those issues into the new course; editing them departs from verbatim.

29. **Question banks and leftover rubrics.** The template ships nine unrelated question banks and nine unrelated rubrics (section 6.7 and 6.8). The prompt builds the course through the API, so they would not be carried unless the cartridge is imported as a base. Neither document says whether the cartridge is imported or the course is built from scratch to match it.

30. **Instructor announcement pattern.** The Teaching Checklist asks for a weekly announcement at the start of each week that also wraps up the prior week ("Tell them what they learned and why it's important") and for a welcome email or 1 to 2 minute welcome video before the term. The prompt asks for "A weekly instructor announcement, drafted and ready to send, that previews the week and names the common sticking point" and an overview video of 2 to 4 minutes per week. Compatible, but the template's announcement carries a wrap-up element the prompt's does not.

31. **Home page "Instructional Delivery" and Zoom pointer.** The online-class variant on the home page ends by pointing students to "Using Zoom as a Student" for attending class remotely. The prompt's course has no synchronous component. Whether the sentence and the Zoom page stay is unstated.

32. **Tips for Success.** The page is first-person instructor text with a personal anecdote and third-party video embeds. The prompt requires instructional prose at or below 7th grade reading level, reported per page, and openly licensed, verified links. Whether an institution-shipped orientation page is "instructional prose" under the prompt's rule is unstated.

---

## Appendix A. File-to-page map

| Template file | Canvas object | Section |
|---|---|---|
| `wiki_content/home.html` | Home page (front page) | 4.1 |
| `wiki_content/welcome-start-here.html` | Page: Welcome! Start Here: | 4.2 |
| `wiki_content/meet-your-instructor.html` | Page | 4.3 |
| `wiki_content/course-material.html` | Page | 4.4 |
| `wiki_content/course-policies-expectations-and-student-privacy.html` | Page | 4.5 |
| `wiki_content/course-evaluation.html` | Page | 4.6 |
| `wiki_content/course-schedule.html` | Page | 4.7 |
| `wiki_content/tips-for-success.html` | Page | 4.8 |
| `wiki_content/olrn-0001-is-required-for-this-course.html` | Page | 4.9 |
| `g7f9f34566cb7bf279429de1d99ab82cc/` | Assignment: BioSig | 4.10, 7.3 |
| `g9459aa5eaf64b59f4a908e4827a7848c.xml`, `g6216ed2469df8e0e164c6ac8cc7333b5.xml` | Discussion: Introduce Yourself | 4.11, 7.1 |
| `wiki_content/how-to-navigate-canvas-as-a-student.html` | Page | 4.12 |
| `wiki_content/using-zoom-as-a-student.html` | Page | 4.12 |
| `wiki_content/communicating-online-3.html` | Page | 4.12 |
| `wiki_content/academic-integrity.html` | Page | 4.12 |
| `wiki_content/canvas-and-tech-support.html` | Page | 4.12 |
| `wiki_content/academic-and-student-support-resources-2.html` | Page | 4.12 |
| `wiki_content/uploading-a-paper-to-turnitin-using-canvas.html` | Page | 4.12 |
| `wiki_content/download-and-install-respondus-lockdown-browser.html` | Page | 4.13 |
| `gb9857bd64f455aeeb8e384ec0f04e701/`, `non_cc_assessments/gb9857bd64f455aeeb8e384ec0f04e701.xml.qti` | Quiz: Test Respondus | 7.2 |
| `gbfac8569c65b90b366b86a88acdb34cf.xml`, `g8cbaa92159bded84edd4ec82edff4416.xml` | Discussion: Q & A | 4.14, 7.1 |
| `wiki_content/module-number-overview.html` | Page: Module [#] Overview | 2.3.1 |
| `wiki_content/module-number-content.html` | Page: Module [#] Content | 2.3.2 |
| `g847792aeffe6dda52129a8c2043151e8.xml`, `g6494c5ce0bd5689b7dfdd4697d2d7ec2.xml` | Discussion Template | 2.3.3, 7.1 |
| `g393030ef9fcbd8bad83607baa3955ef3/`, `non_cc_assessments/g393030ef9fcbd8bad83607baa3955ef3.xml.qti` | Quiz Template | 2.3.4, 7.2 |
| `g065eabf68adfdd4808adcef508c6f13f/` | Assignment Template | 2.3.5, 7.3 |
| `wiki_content/module-number-wrap-up.html` | Page: Module [#] Wrap-up | 2.3.6 |
| `wiki_content/how-to-use-this-layout.html` | Page (unpublished, faculty) | 2.1 |
| `wiki_content/teaching-checklist-online-slash-fully-distance-education-courses.html` | Page (unpublished, faculty; not in any module; links the PDF) | 2.2 |
| `course_settings/syllabus.html` | Syllabus (empty) | 4.15 |
| `course_settings/course_settings.xml` | Course settings | 6.1, 6.4 |
| `course_settings/assignment_groups.xml` | Assignment groups | 6.2 |
| `course_settings/grading_standards.xml` | Grading standards | 6.3 |
| `course_settings/learning_outcomes.xml` | Outcomes | 6.6 |
| `course_settings/rubrics.xml` | Rubrics | 6.7 |
| `course_settings/module_meta.xml` | Modules | 1 |
| `course_settings/files_meta.xml` | File visibility | 6.5 |
| `course_settings/media_tracks.xml` | Caption track for the communication video | 3.10, 8.3 |
| `course_settings/context.xml` | Source course and account identifiers (do not copy) | |
| `course_settings/canvas_export.txt` | Export marker (a joke line; ignore) | |
| `gf48f9fe3d8b380c499b7a9fd7db5c1b3.xml` | LTI 1.1 course-navigation redirect tool "NLC One-Click Tutoring" | 6.4 |
| `lti_resource_links/gcc3273761a68b67ebf92be3bcf1caf2b.xml` | LTI 1.3 resource link for a video platform (unreferenced) | 6.4 |
| `external_content/lti_96176.json` | No LTI assignments | 6.4 |
| `non_cc_assessments/*.xml.qti` (nine others) | Leftover question banks | 6.8 |
| `web_resources/udoit.json` | Scanner marker | 8.1 |
| `web_resources/**` | Media | 6.5 |

## Appendix B. Minimal skeleton of a conforming weekly module

Item order and types, as the template ships them:

1. Page `Module N Overview` (2.3.1)
2. Page `Module N Content` (2.3.2)
3. Graded discussion (2.3.3 body pattern)
4. Classic quiz (2.3.4 description pattern)
5. Assignment (2.3.5 body pattern)
6. Page `Module N Wrap-up` (2.3.6)

Each page body begins with the shell in 3.1 and uses the block, heading, icon, table, and closing-line patterns in 3.2, 3.3, 3.8, and 3.18. Placeholders are removed per section 5. Module settings: published, not locked, no sequential progress, no completion requirements recorded on the weekly template.
