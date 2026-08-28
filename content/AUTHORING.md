# How to author a page for this course

Read this before writing anything. Then read the four exemplar files, which are
the standard everything else is measured against:

- `content/pages/rules-of-engagement.md`
- `content/pages/w5-overview.md`
- `content/pages/w5-content.md`
- `content/assignments/attack-lab-1.md`

---

## 1. The block format

Every line on a page sits inside a `:::` block. Text outside a block is a build
error. Blocks map to the Cidi Labs DesignPLUS classes the NLC Online Course
Template uses, so keep to the list.

```
::: intro
One or two sentences saying what this page is for.
:::

::: section | An optional heading
Body text. Markdown works: **bold**, `code`, lists, tables, fenced code blocks.
:::

::: callout warning | An optional heading
Callout kinds: warning, note, tip, stop, time
:::
```

Available blocks and where each belongs:

| Block | Use it on | Heading |
|---|---|---|
| `intro` | every page, first block | none |
| `objectives` | Overview pages | Learning Objectives |
| `tasks` | Overview pages | Tasks |
| `section` | anywhere | your own, after `\|` |
| `callout` | anywhere | your own; takes a kind |
| `reading` | Content pages, before every external link | Before You Read This |
| `checkpoint` | Content and Wrap-up pages | Check Yourself |
| `scope` | any page with an attack in it | Authorization and Scope |
| `directions` | Assignment pages | Directions |
| `grading` | Assignment pages | Grading Criteria |
| `submit` | Assignment pages | How to Submit |
| `learned` | Wrap-up pages | What You Learned |
| `did` | Wrap-up pages | What You Did |
| `next` | Overview and Wrap-up pages | What's Next |
| `sources` | Content pages | Sources |

**Page anatomy, fixed by the template.** Every week has exactly four parts:
an Overview page, a Content page, the graded Assignments, and a Wrap-up page.

- **Overview** = `intro`, `objectives`, `scope` (if the week involves attacks),
  `tasks` table, a `callout time` with an honest time estimate, `next`.
- **Content** = `intro`, several `section` blocks, a `reading` block before
  every external link, `callout` blocks for the things students get wrong, and
  a `sources` block at the end.
- **Assignment** = `intro`, `scope` (if attacks), `directions`, `grading`
  table with points that add up, `submit`.
- **Wrap-up** = `learned`, `did`, `checkpoint`, `next`.

---

## 2. The writing standard

This is enforced by `python -m tools.readability`, which fails the build. The
exemplars score between grade 3.7 and 5.0. Aim there.

- **Average sentence at or under 15 words.** Shorter is better. The exemplars
  average 8 to 11.
- **Grade level at or under 8.0**, target 7.0, measured after code blocks,
  tables, URLs, framework identifiers, and quoted text are removed.
- **Second person, active voice.** "You add a tool", not "a tool is added".
- **The common word.** use not utilize. start not commence. show not
  demonstrate. fix not remediate, in narrative prose.
- **One idea per paragraph. One job per sentence.**
- **Front-load the point.** The first sentence of a section says what the
  section is for.
- **Instructions are numbered steps**, never prose.

**Technical vocabulary is taught, not avoided.** Words like *prompt injection*,
*tool authorization*, *JSON schema*, and *authorization boundary* are the
subject of the course. Define each in plain language the first time it appears
on a page, then use it consistently. Do not paraphrase a term differently every
time; that is harder for a struggling reader, not easier.

**Punctuation.** Use commas, colons, parentheses, and semicolons. Do not use em
dashes anywhere.

**Tone.** Professional practitioner. Never "hacker". No edgy framing, no
glorifying breaking things, no language that would embarrass a student who
showed this work to an employer. No idioms, no sports or military metaphors, no
humor that needs shared cultural knowledge. The audience is adults of mixed
ages and first languages.

---

## 3. Rules that are not negotiable

1. **Every external link gets a `reading` block first.** It says what the
   document is, which part to read, what to look for, and one question to
   answer while reading. Students are never sent to a professional document
   cold. Keep assigned external reading under 45 minutes per week.
2. **Never invent a citation, a statistic, a URL, or a quotation.** If you are
   not certain a resource exists and is openly licensed, do not include it. Use
   only resources already listed in `docs/course-blueprint.md` section 6.
3. **Every page that involves an attack carries a `scope` block** pointing back
   at the Rules of Engagement. The brief requires the Rules of Engagement to be
   referenced in every attack lab.
4. **Evidence language.** Never write that a result is proven by what the model
   said. Evidence is a side effect, a canary token, or an audit row.
5. **Say "selected OWASP risks", never "the OWASP LLM Top 10".** The course
   covers three of ten substantively.
6. **Pin versions.** OWASP LLM Top 10 **2026**, OWASP Top 10 for Agentic
   Applications **2026**, MITRE ATLAS release **2026.07**.
7. **Time estimates must be honest**, in a `callout time` on every Overview
   page. The whole course budgets 19 to 21 hours per week including reading.
8. **Grading tables must add up** to the points in `content/course.yaml`.
9. **Placeholders are forbidden.** No `[bracketed text]`, no TODO, no
   `#fbeeb8`. The build asserts zero of these.
10. **Days, not dates.** Write "due Sunday 11:59 PM" or "day 35". Never a
    calendar date; the course ships relative offsets.

---

## 4. Facts you may rely on

The lab repository is at `labs/`. Students run:

```
python verify_env.py
python -m target.seed
python -m target.app
python -m agent.cli
python -m harness.runner
python -m pytest tests/ -q
```

The five marked extension points:

| # | Where | Module | What the student does |
|---|---|---|---|
| 1 | `agent/loop.py` `before_tool_call()` | 4 | every defense; ships permissive |
| 2 | `agent/tools.py` `get_customer()` | 2 | write the body and its error path |
| 3 | `agent/llm.py` retry and JSON parsing | 1 | survive a rate limit; parse a reply |
| 4 | `agent/tools.py` a tool of their own | 2 | design it, write its schema, register it |
| 5 | `harness/cases/*.yaml` | 3 | add attack cases, YAML only |

The target app is HelpDesk Lite. Customers are C-1001 through C-1005. Tickets
are T-501 through T-506. T-503 carries an indirect injection that leads to
customer data leaving. T-504 carries a system prompt leak. Knowledge base
article KB-02 carries an injection from trusted internal content. Three canary
tokens exist per student: `sysprompt`, `customer`, `kb`.

The harness runs each case five times. An attack that lands once out of five is
VULNERABLE. A fix counts only if it holds all five times. A result between the
two is FLAKY. Transport errors are ERRORED and are excluded from the
arithmetic. Two controls run every time: a detector self-test and a benign
baseline.

Never grade the model's prose. Grade the world.

---

## 5. Check your work

```
python -m tools.readability --file content/pages/your-page.md
```

Fix anything it flags before you consider a page finished.
