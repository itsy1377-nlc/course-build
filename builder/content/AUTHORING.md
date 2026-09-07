# How to author a page for this course

Every page in this course is written against this file.

## 1. The block format

Every line on a page sits inside a `:::` block. Text outside a block is a
build error. `tools/blocks.py` maps each block to the exact Cidi Labs
DesignPLUS class the institutional template uses, so keep to the list.

```
::: intro
One or two sentences saying what this page is for.
:::

::: section | An optional heading
Body text. Markdown works: **bold**, `code`, lists, tables, fenced code blocks.
:::

::: callout time | How long this takes
A table or a short list.
:::
```

| Block | Heading it renders | Where it belongs |
|---|---|---|
| `intro` | none | first block on every page |
| `keyfacts` | The short version | after `intro`, Start Here pages |
| `objectives` | Learning Objectives | overview pages |
| `tasks` | Tasks | overview pages |
| `section` | yours, after the pipe | anywhere |
| `callout` | yours; kind is `warning`, `note`, `tip`, `stop` or `time` | anywhere |
| `reading` | Before You Read This | before every external link |
| `video` | yours; write `::: video w1-overview \| Title` | overview and content pages |
| `steps` | Do this now | anything done in order |
| `directions` | Directions | assignments and discussions |
| `grading` | Grading Criteria | assignments and discussions |
| `submit` | How to Submit | assignments and discussions |
| `checkpoint` | Check Yourself | content and wrap-up pages |
| `sources` | Sources | content pages, last block |
| `learned` | What You Learned | wrap-up pages |
| `did` | What You Did | wrap-up pages |
| `next` | What's Next | overview and wrap-up pages |
| `scope` | Authorization and Scope | week 6 pages |

One table per block, because the heading becomes the caption. Give any block
holding a table a heading. A two-column facts table needs an empty markdown
header row, which the renderer drops.

## 2. Page anatomy

Structure follows the institutional template. Content and assessment follow the
build brief. `docs/phase1-blueprint/template-conflicts.md` section 1 settles
every collision. Its mapping folds the brief's eight weekly parts into the
template's page set, and section 8 records the Phase 2 amendments to it. A
weekly module holds eight items: the template's pages and assessments, plus
the sidebar notebook and the lab notebook. A week whose approved spec splits
the reading across two pages holds nine, and the second page takes the stem
`wN-content-2`. Week 2 is the first of these.

| Brief part | Where it lives | Blocks it uses |
|---|---|---|
| Overview | Page `wN-overview` | `intro` with the overview video, `objectives`, `tasks`, `callout time`, `next` |
| Objectives | the same page | `objectives`, numbered 1.1 to 1.3, each ending in its parent, such as (CLO3) |
| Read/Watch | Page `wN-content`, plus `wN-content-2` where the spec splits it | `intro`, `section` blocks, the walkthrough `video`, a `reading` block before every link, `sources` last |
| Sidebar | the same page | one `section` linking the sidebar notebook |
| Lab | Assignment `wN-lab` | `intro`, `directions`, `grading`, `submit` |
| Discussion | Discussion `wN-discussion` | `intro`, `directions`, `grading`, `submit` |
| Submit | a block, never a page | `submit` |
| Check Yourself | Quiz `wN-self-check` | YAML in `quizzes/` |

The template adds a fourth page. `wN-wrap-up` carries `learned`, `did`,
`checkpoint` and `next`, plus the self-check answers.

Module 0 holds an overview page, the ungraded self-assessment, the on-ramp
notebook and a wrap-up page, which is the four-item set template conflict 27
settles. It has no discussion and no assignment. Module 8 holds an overview
page, the exam and a wrap-up page, and no content page, because one there
would add instruction the brief forbids. That is the three-item set template
conflict 27 settles. The week 8 wrap-up closes the course: it teaches nothing
new and it reviews no exam item.

Start Here pages are scanned, not read. Each opens with `intro`, then
`keyfacts`, then short `section` and `steps` blocks. `content/course.yaml`
names every page, and its `ref` is the file stem.

The course has twelve modules, in the template's order: Orientation Module,
Student Resources, Q & A Community, then `Module 0: Programming On-Ramp` and
Modules 1 to 8. The home page is the course front page and sits in no module.
Module names follow the template pattern, `Module 5: The Bounded Loop`, and
every page and every due date still speaks in weeks. Module 1 is week 1.

## 3. Length and reading level

Length is weighted words. Prose counts in full. Table rows, list items and code
lines count at 60 percent, because a table is scanned and a paragraph is read.
The budget is a ceiling. The existing courses run about 15 percent under it.

| Page kind or stem | Budget |
|---|---|
| `welcome-start-here` | 400 |
| `meet-your-instructor` | 300 |
| `course-policies` | 650 |
| `support-resources` | 600 |
| `ai-use-policy`, `course-schedule` | 550 |
| `canvas-and-tech-support` | 450 |
| `communicating-online`, `tips-for-success` | 400 |
| `academic-integrity`, `how-to-navigate-canvas` | 350 |
| `home`, `course-material`, `olrn-0001`, `if-something-breaks` | 450 |
| Any other Start Here page | 450 |
| `glossary` | 1,800 |
| Week overview | 400 |
| Week content | 1,400 |
| Assignment | 700 |
| Discussion | 500 |
| Week wrap-up | 550 |

Reading level is measured after code, tables, headings, links and framework
identifiers are stripped out.

| Measure | Build fails above | Write to |
|---|---|---|
| Flesch-Kincaid grade | 8.0 | 4.0 to 5.0 |
| Average sentence | 15 words | 9 to 12 words |
| Longest sentence | 40 words | under 25 |
| Longest paragraph | 70 words | 30 to 50 |
| Reading ease | none | about 80 |

Reading time is priced at 200 words a minute for one pass. Anything beyond one
pass gets its own named line and minutes. Never move the rate to make a page
fit. Cut words, or add a line.

## 4. Voice

- Second person, active voice. "You add a tool", not "a tool is added".
- The common word. Use, start, show, fix, check. Not utilize, commence,
  demonstrate, remediate.
- One idea per paragraph. One job per sentence. Front-load the point.
- Instructions are numbered `steps`, never prose.
- No em dashes and no en dashes. Commas, colons, parentheses and semicolons
  are fine.
- No idioms, sports or military metaphors, or humor that needs shared culture.
  The audience is adults of mixed ages and first languages.
- Professional practitioner tone. Never "hacker".
- Bold the load-bearing phrase once per block at most.

Technical vocabulary is taught, not avoided. Define each term in plain words
the first time a page uses it, then use the same word every time.

## 5. Rules that are not negotiable

1. **Every external link gets a `reading` block first.** It says what the
   document is, which part to read, and one question to answer while reading.
2. **Never invent a citation, a statistic, a URL or a quotation.** If you are
   not certain a resource exists and is openly licensed, leave it out and
   report it.
3. **Grading tables must add up** to the points in `course.yaml`: 100 a lab,
   20 a discussion, 12 a self-check, 30 for the exam.
4. **No placeholders.** No bracketed text, no TODO, no leftover highlight
   color. The build asserts zero of these.
5. **Days, not dates.** Write "due Sunday 11:59 PM" or "day 35".
6. **Time estimates are honest**, in a `callout time` on every overview page,
   itemized and totalled. A week is under 6 hours. Week 0 is 4 to 6 hours on
   top of that, and says so.
7. **Nothing real appears in content.** Examples use the corpus organization.
   Pages name the model by its role, never by vendor.
8. **A key is never shown.** No cell, screenshot instruction or page displays
   key material.
9. **Sidebar examples never use lab subject matter.** Groceries, playlists,
   rosters, weather. Never email, alerts, headers or verdicts.

## 6. What a page may assume the student already knows

A term is defined once, on the page that first needs it, and used plainly
after that. This table fixes where each definition lives. Defining
one late leaves a page unreadable.

| Defined in | Terms every later page may use without defining |
|---|---|
| Start Here | module, week, self-check, sidebar, lab, notebook, cell, TODO cell, pre-written, notebook server, API key, token, token budget, disclosure, agent, phishing, triage, Python, dictionary, traceback, export file, rubric |
| Week 0 | variable, function, call, return value, list, dictionary, key, JSON, f-string, parameter, default, if and else, for loop, while loop, counter, try and except, traceback, error type |
| Week 1 | model, prompt, request, response, temperature, token count, the agent as a loop around one call, asset, user, network, endpoint, log, alert, ticket, incident, escalation, scoring AI, generative AI, agentic workflow |
| Week 2 | structured output, schema, verdict, category, confidence, indicator, malformed output, retry, reasoning block, stop reason |
| Week 3 | grounding, facts block, header, SPF, DKIM, DMARC, display-name mismatch, link host, playbook, known-good domain, data minimization |
| Week 4 | tool, tool call, function calling, sender reputation, allowlist, blocklist, recipient record, business email compromise |
| Week 5 | bounded loop, observe, decide, act, step, step cap, stop condition, runaway loop |
| Week 6 | prompt injection, delimiter, data, not instructions, fact check, confidence threshold, human review, per-run token cap, hallucination, data exposure, automation bias, overreliance |
| Week 7 | triage note, batch run, ground truth, accuracy, false positive, false negative, plain-language summary |

Two rules follow. A week may not use a term from a later row. And every term
here appears in the glossary in the same plain words the page used.

Three definitions are written once and repeated word for word, because a Start
Here page is scanned rather than read and a student may meet any of them first:

- **Agent.** "An agent is a program that sends text to a model, reads the
  answer, and acts on it."
- **Cell.** "A cell is one block in a notebook that you run on its own."
- **API key.** "An API key is a secret string that proves your code may use
  the model."

*Agent* is the whole thing a student builds, in every week. *Tool* is a week 4
helper function and nothing else. The two are never swapped.

## 7. How to measure a page

Run this from the repository root, on every page, before you call it finished.

```
ITSY_CONTENT=builder/content python3 -m tools.readability --file <path>
```

It reports the grade, the weighted word count and the budget for that page
kind. It fails a page over budget, a paragraph over 70 words, a sentence over
40 words, or an average sentence over 15 words. The file name decides the
budget, so use the stem `course.yaml` names.

Drop `--file` to measure the whole course, and commit that report beside the
content.
