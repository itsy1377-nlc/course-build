# Week 4 spec: Tools

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 4 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.
**Evidence role:** supporting evidence for course learning objective 3 (CLO3). Week 5 carries the primary evidence.

Four terms used throughout. A *tool* here is an ordinary Python function that the
course ships, such as one that looks up a sender's history. A *tool call* is the
model asking, in a structured reply, for one of those functions to run. The
model never runs anything. The student's code does.

## The capability added, and why it is exactly one

Week 3 left the agent sending a block of extracted facts and getting a verdict
back. Week 4 adds one thing: the model may ask for one of three named tools, and
the student's code runs it and hands the result back. Nothing else moves. The
same facts block, the same answer keys, and the same retry from week 2 all stay
as they were.

It is one capability because the agent still asks once and answers once. There
is no loop, no choosing a second tool from what the first returned, and no cap
on steps. That is week 5. A student who finishes week 4 has an agent that works
end to end, and it is one round longer than last week's.

## The three tools

They ship in `lab/tools/triage_tools.py` and are imported, never written by
students. Each returns exactly the record the corpus holds for that email, so
the answer key and the tool can never disagree.

Two of the three read a list. An *allowlist* is a list of link hosts the
organization has already cleared. A *blocklist* is a list of link hosts it has
already judged bad. The course ships both as small data files.

| Tool | What it answers |
|---|---|
| `check_sender_reputation(sender)` | Has this sender or its domain been seen before, and how did those reports close |
| `check_urls(hosts)` | Is each link host on the allowlist, on the blocklist, internal, or on no list |
| `lookup_recipient(address)` | Who is this recipient, are they an executive, and what have they reported before |

## The six emails, and why each one

The lab runs six emails from the corpus. Four of them turn on one tool alone, so
a student can see exactly which tool did the work. A fifth, 019, turns on one
tool plus the internal delivery path. The sixth, email 003, does not change
verdict at all. It is there to show what a recipient's report history looks like
when the answer was already right.

| Email | Tool the week uses | What the student sees |
|---|---|---|
| 008 | `check_sender_reputation` | A calm, well-written quote from a vendor. Every header check passes. The domain has three prior reports for the same trick, so the verdict flips to malicious. |
| 018 | `check_urls` | A real customer's short note. The sender is a known-good customer, but the link host is on the blocklist, so the verdict flips to malicious. |
| 017 | `check_urls` | A payroll notice that reads like a phishing message. The link host is on the allowlist, so the verdict flips to benign. |
| 009 | `lookup_recipient` | Three sentences in the chief executive's name from a free webmail account. The recipient record carries the executive flag and prior reports of the same scam. |
| 019 | `lookup_recipient` | The chief financial officer asks accounts payable to move a payment. The message never left the company. The verdict is benign, and it still escalates for a phone callback. |
| 003 | `lookup_recipient` (no verdict change) | A marketing mailing, benign before and after. The recipient has reported eleven messages in ninety days, and none was a real threat. |

Email 019 is the one that teaches the hardest point: a verdict of benign and a
decision to escalate are two separate answers, not one.

## The lab deliverable

One exported file, `week4_tool_calls.json`, written by a single pre-written
cell. It holds one record per email. Each record carries six things.

- The email id.
- The tool the model asked for, and the arguments it sent.
- The result the student's code returned.
- The call id the model sent, and the call id the student's tool result message
  carried back.
- The verdict without tools, and the verdict with tools.
- Whether the fallback path ran.

The pair of call ids is there so a grader can read the second TODO cell from the
file. Matching ids mean the student's message carried the model's own id back.
That is the only evidence in the submission for weekly objective 4.2, so it has
to be in the file.

The file also holds the session token totals. A grader reads that file and the
screenshot. A grader never opens the student's notebook.

## What the student writes, and what arrives pre-written

The student fills two clearly marked TODO cells. A *TODO cell* is a notebook
cell with a comment marking the lines the student writes; every other cell
arrives complete and working.

| Cell | Function | Lines the student writes | What it does |
|---|---|---|---|
| TODO 1 | `run_tool(name, arguments, parsed)` | 8 to 10 | Picks which of the three functions to run from the name the model sent, takes the argument from the model's request or from the parsed email, and returns the result. An unknown name returns a plain sentence, not an error. |
| TODO 2 | `tool_result_message(tool_call, result)` | 3 to 4 | Builds the message that carries the tool result back to the model, copying the call id across |

That is 11 to 14 written lines, inside the course target of 5 to 15. Everything
else in the seventeen-cell notebook arrives pre-written and working.

- The configuration cell, the token counter, and the network helper.
- All working code from weeks 1 to 3.
- The three tool definitions, in the format the model expects.
- The helper that sends a message list with the tools attached.
- The helper that runs one full round of ask, run, and answer.
- The comparison run over all six emails.
- The forced fallback demonstration.
- The export cell that writes the submission file.

`run_tool()` is the cell sidebar 4b prepares. Criterion 2 of the rubric scores
both TODO cells.

One pre-written helper deserves a note. The serving endpoint has no way to force
a tool call. When the model answers in prose instead of asking for a tool, the
helper falls back to week 2's manual parsing and records that it did. That
fallback fired in none of nine recorded tests, but nothing prevents it, so
students meet it as a normal path rather than as a bug.

## Weekly objectives

By the end of week 4 you will be able to:

| # | Objective | Parent CLO | Words | Verb | Reported by |
|---|---|---|---|---|---|
| 4.1 | Write one function that runs the tool the model names. | CLO3 | 10 | Write | Rubric criterion 2 |
| 4.2 | Build the message that carries a tool result back to the model. | CLO3 | 12 | Build | Rubric criterion 2 |
| 4.3 | Compare each email's verdict with tools against its verdict without tools. | CLO3 | 11 | Compare | Rubric criterion 3 |

All three name something the student does in this week's lab. All three carry a
parent. None joins two verbs with "and", and none uses a banned verb.

Every objective is reported. Criterion 2 reads 4.1 and 4.2 from the exported
file. Criterion 3 reads 4.3 from the screenshot and the written answer. Both
criteria link to the CLO3 Outcome, so all three objectives produce outcome data
for the program.

All three sit under CLO3 rather than under CLO1, and that is
deliberate. Week 3 carries the primary evidence for CLO1. The outcome
calculation is most recent score, so a week 4 result linked to CLO1 would
replace the week 3 primary result in the program's report. Section "Rubric
sketch" keeps week 4 off CLO1 for the same reason.

## The sidebar, in two parts

The build prompt sets one construct per sidebar, and says that two constructs
mean two short sidebars. Its week 4 target names two: defining a function with
parameters and a return value, and choosing which function to run from a name.
Week 4 therefore ships two short sidebars rather than one. That follows the
binding rule and still teaches both constructs.

**Domain for both:** a music playlist. Never email, never security.
**Time:** 25 minutes for the pair. That is the single sidebar line in the time
table below, so the week does not get longer.

### Sidebar 4a: write a function that hands an answer back

**Construct:** defining a function with parameters and a return value.
**Length:** 12 lines, runnable.

The sidebar opens with a dictionary holding two playlists. It then defines two
small functions. One counts the songs in a named playlist. The other turns that
count into playing minutes. Each takes the playlist name and the dictionary, and
each returns a number instead of printing one.

The walkthrough explains every line in ordinary words, at the course reading
level. It ends with one ungraded prompt: add a third playlist, then call the
counting function on it. It links back to the week 0 section "Defining a
function with parameters".

### Sidebar 4b: pick the function from a name

**Construct:** choosing which function to run based on a name.
**Length:** 8 new lines, runnable.

Sidebar 4b opens with the two functions from 4a already written. The only new
idea is the choosing. It defines a third function that takes a report name as
text and runs one of the two. When the name matches neither, it returns a plain
sentence instead of crashing.

The walkthrough explains every line the same way. It ends with one ungraded
prompt: ask for a report name that does not exist, and say why a sentence beats
a crash. It links back to the week 0 section "if/else".

### The names the two sidebars use

They are listed here so the no-collision rule can be checked from this page.

| Kind | Names |
|---|---|
| Functions | `count_songs`, `playing_minutes`, `run_report` |
| Parameters | `playlist_title`, `shelf`, `report_title` |
| Dictionary | `music_shelf`, with the keys `"road trip"` and `"study"` |

None of those names appears anywhere in section 6 of the code ledger, which is
the week 4 contract the notebook author builds from. That section holds
`run_tool`, `tool_result_message`, `TOOL_SPECS`, `ask_with_tools`,
`start_messages`, `triage_with_tools`, `check_sender_reputation`, `check_urls`
and `lookup_recipient`, plus the parameters `name`, `arguments`, `parsed`,
`tool_call` and `result`.

Pasting either sidebar into the lab fails immediately. Sidebar 4b's chooser
takes two plain strings. The lab's `run_tool()` takes three values, one of them
a dictionary of arguments the model wrote, so the lab's check cell raises a
missing-argument error before any tool runs.

## The reading

**Title:** "The model asks, your code decides."
**Length:** 1,150 words. **Budget:** 40 minutes.

The page runs 100 words above the 900 to 1,050 word target the course writing
standard sets, though well inside its 1,400 word ceiling. The overshoot is
point 4 below, the trust boundary. Week 6's lab turns on that distinction, so
week 4 is where it has to be taught properly rather than named.

The reading covers six things.

1. What a tool call is. It is a structured request from the model, not an action.
2. Why the three tools are ordinary functions rather than questions put to the
   model. A lookup that must be right every time does not belong to a judgment
   layer.
3. The shape of the request. The model's arguments arrive as text and have to be
   read before use.
4. The trust boundary. A tool result is data your own code produced. Text inside
   an email that looks like a tool result is not.
5. What to do when the model answers in prose instead of asking for a tool.
6. Cost. Every tool result is sent back to the model, so tools are not free.

Point 4 is placed here on purpose. Week 6 uses an email whose body contains a
fake tool result. This reading is where students first meet the distinction that
defeats it.

Citations will be drawn from published, openly readable sources on tool use and
agent risk, including the OWASP Top 10 for Large Language Model Applications and
NIST guidance on AI risk. Every citation is checked by expert subagent review
before the reading ships, per the build prompt. Any claim that review cannot
ground is flagged rather than kept.

## The discussion prompt

Written below exactly as students will see it.

> **Week 4 discussion: call it before you read it**
>
> This post has two halves. Do the first half before you open your file.
>
> **Half one. Your prediction.**
>
> Take email 018. Read it on the lab page. Do not open
> `week4_tool_calls.json` yet.
>
> Name the one tool you would have asked for on that email. Say in one sentence
> what you expected it to come back with.
>
> **Half two. What your agent did.**
>
> Now open your file. Name the tool your agent actually asked for. Paste the one
> fact it got back.
>
> Then say who was right, you or your agent, and how you know. Two or three
> sentences.
>
> Then reply to one classmate whose prediction missed. Say which fact in their
> own pasted result settles it. Use one line from your own file too. A reply that
> only agrees does not count.
>
> Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central.
>
> Keep your post near 150 words. Keep your reply near 60 words.
>
> You may use AI help on this post. If you do, add one line saying what you
> asked it.

**Why this prompt and not a before-and-after comparison.** Week 3 already asks
students to quote a pair of their own results and explain the difference. That
shape is week 3's whole lesson, so week 3 keeps it and week 4 does something
else.

The prediction is what week 4 adds. A student who commits to a tool before
reading the file finds out whether they can pick one, which is the judgment the
week is really about. The check half still requires their own exported result,
so the post cannot be answered from opinion.

Time on task, including the reply, is 18 minutes.

## What students submit

Three items, and nothing else. No folders, no archives, no links.

1. **One screenshot.** The output of the cell titled "All six emails, with tools
   and without". That cell prints one row per email with four columns: the email
   id, the tool asked for, the verdict without tools, and the verdict with tools.
   It closes with the running token line, which must be in the shot. Section 6 of
   the code ledger now names the same five printed items for that cell, so the
   spec and the ledger describe one screenshot. Students are told not to
   screenshot the configuration cell. That cell prints only whether a key was
   found, and no cell in any week prints key material.
2. **One file.** `week4_tool_calls.json`, written by the export cell near the end
   of the notebook. The cell prints the full path and the first few lines, so the
   student can see what they are attaching.
3. **A written answer of 3 to 5 sentences**, typed into the submission box. The
   prompt reads: "Pick the email where the tool changed your agent's verdict.
   Name the email and the tool. Give the one fact the tool returned. Then say
   what your agent decided before it had that fact. If no verdict changed on your
   run, say which email came closest and why."

## Rubric sketch

One hundred points. Every weekly lab in this course is worth 100 points, so the
seven labs carry equal weight inside the Labs group. Every criterion is
gradeable from the screenshot, the file, and the written answer alone.

| # | Criterion | Points | Levels | Canvas Outcome |
|---|---|---|---|---|
| 1 | Submission completeness. All three items present and readable. | 32 | 32 / 21 / 0 | None. Non-CLO expectation: submission completeness. |
| 2 | Tool call handled end to end. For each of the six emails the file records one of two things. Either the tool the model asked for, its arguments, the result your code returned, and a tool result message carrying the model's call id. Or the fallback record, showing the prose path was handled. Recorded results match the shipped tool records. | 40 | 40 / 30 / 20 / 0 | CLO3: Build a bounded triage agent (supporting evidence) |
| 3 | Reading your own results. The written answer names one email, one tool and one returned fact, then says what that fact changed. The screenshot shows the same email's two verdicts. | 28 | 28 / 21 / 14 / 0 | CLO3: Build a bounded triage agent (supporting evidence) |

Criteria 2 and 3 use the mastery scale set in the alignment matrix: 4 exceeds
standard, 3 meets standard, 2 approaching standard, 0 no evidence. Criterion 2
is that scale multiplied by ten and criterion 3 is the same scale multiplied by
seven, so each one can actually award its top level and a rating maps across
with no translation step.

An earlier draft priced criterion 3 at 3 points on a four-level scale, which
made its top level unreachable. Both Outcome-linked criteria are now exact
multiples of four.

Both are declared supporting evidence. Week 4 stays a supporting result under
CLO3, week 5 stays the primary one, and week 4 stays clear of CLO1, whose
primary result is week 3's.

Criterion 2 scores the student's code, not the model's choice. The endpoint
cannot force a tool call. When the model answers in prose instead, a correctly
written fallback record earns the top level, exactly as a recorded tool call
does. The rating text says that in those words, so no student loses points for a
path the model picked.

Criterion 2 also carries objectives 4.1 and 4.2. The tool, the arguments and the
result report 4.1. The returned call id reports 4.2: when it matches the id the
model sent, the student's tool result message was built correctly.

Criterion 3 carries objective 4.3. It links to the CLO3 Outcome because it
reports a stated objective with a parent CLO. It does not score the writing
itself. Criterion 1 is the only week 4 criterion with no Outcome link, and it
measures submission completeness alone.

## The self-check

Five multiple choice items, auto-graded, low stakes, unlimited attempts. Here is
what they cover.

1. Who asks for a tool, and who runs it.
2. Why the arguments the model sends have to be read as text first.
3. Which of the three tools answers a given question.
4. What should happen when the model names a tool that does not exist.
5. What the code does when the model answers in prose instead.

Stems are written at the course reading level.

## Time estimate

| Activity | Minutes |
|---|---|
| Overview video | 3 |
| "What success looks like" walkthrough video | 4 |
| Sidebars 4a and 4b, together | 25 |
| Reading | 40 |
| Lab | 165 |
| Discussion, including one reply | 18 |
| Self-check and submission | 30 |
| **Total** | **285 minutes, or 4 hours 45 minutes** |

That is inside the 6 hour ceiling with 75 minutes of slack, and every line sits
inside its own budget. Video is 7 minutes against a ceiling of 12. The lab is 2
hours 45 minutes against a range of 2.5 to 3 hours. If week 4 runs long in the
first offering, the reading is the first thing cut, and the sidebars and the lab
scaffolding are never cut.

## Token estimate per full lab run

Measured from the corpus files and the recorded serving stack behavior. A *full
lab run* means every cell in the notebook run once, top to bottom.

One email's first request is 4,653 characters. The four parts marked shared are
measured once for the whole blueprint, in section 2 of the grade distribution
and token totals document, and weeks 5, 6 and 7 send the same figures.

| Part | Characters | Source |
|---|---|---|
| System prompt and the rendered answer schema | 531 | Shared: 184 plus 347 |
| Facts block from the parsed email | 352 | Measured on this week's emails |
| Playbook snippet | 1,366 | Shared |
| Known-good domain list | 668 | Shared |
| Email body | 772 | Measured mean of the eleven rendered teaching bodies |
| The three tool definitions | 964 | Shared |

Divided by 4, that is 1,163 tokens. The second request repeats all of it. It
adds the model's tool request and the tool result, about 500 characters more, so
1,288 tokens. The no-tools comparison call drops the tool definitions. That
leaves 3,689 characters, or 922 tokens.

A full run makes 18 calls. Six emails run with tools at two calls each. Six run
without tools at one call each.

Prompt side: (6 x 1,163) + (6 x 1,288) + (6 x 922) = 20,238 tokens. Completion
side, using the measured reasoning-off figures of 34 tokens for a tool request
and about 75 for a JSON verdict: (6 x 34) + (6 x 75) + (6 x 75) = 1,104 tokens.

**Week 4 total: about 21,300 tokens per full run.**

Two figures belong beside that number. First, if the reasoning model is left in
its default mode, measured completions rise to roughly 155 tokens for a tool
request and roughly 950 for a JSON verdict. The same run then costs about 32,600
tokens.

Second, character count understates the tool block. On the recorded stack, one
small tool definition of about 250 characters added 263 prompt tokens, because
the chat template wraps tool definitions in extra text.

Twelve of this week's eighteen calls carry the tool block. Treat 21,300 as a
floor and roughly 23,700 as the working figure for the reasoning-off path.
Section 3.2 of the grade distribution and token totals document carries the same
allowance for weeks 5, 6 and 7.

## Assumptions and things to confirm

1. **Per-lab points.** Every weekly lab in this course is worth 100 points. All
   seven weekly specs now carry that total, and the Labs group weight of 60
   percent divides equally across the seven.
2. **Reading time is built from the one course rate.** The course prices one
   reading pass at 200 words a minute, which is section 2 of the survey content
   plan, and prices anything a page asks beyond that as its own named line. Week
   4 reads 1,150 words in 6 minutes at that rate, then adds 18 for the worked
   example of a tool request, 6 for the two tables, and 10 for opening one cited
   source. That is 40 minutes, the floor of the reading band, and it is how the
   reading line is reported.
3. **Four of the six emails are not yet rendered.** Emails 003 and 019 exist as
   finished files. Emails 008, 009, 017, and 018 are fully specified in the corpus
   spec, with their tool records written, but have not been generated. Every fact
   quoted above comes from that spec.
4. **One figure in the token table is projected.** The 500 characters added by
   the model's tool request and the tool result is an estimate, because that text
   only exists at run time. The system prompt, the answer schema, the facts
   block, the playbook, the known-good list, the tool definitions and the email
   bodies are all measured.
5. **Body length.** The 772 character body figure is the mean of the eleven
   rendered teaching emails, which run from 396 to 1,129 characters. It was
   measured with the course's own `corpus/tools/parse_eml.py` on the body text,
   with line endings normalised. Of the two week 4 emails that exist, 019 at 396
   characters is the shortest of the eleven, and 003 at 1,118 is close to the
   longest, which is 013 at 1,129. Individual emails will land above and below
   the mean. Rerun the figure when the remaining teaching emails are generated.
6. **Model not yet chosen.** The estimate assumes the reasoning-off path. The
   model recommendation is blueprint item 5 and depends on week 5 testing.
7. **Template conflicts that touch this week.** Conflict 1, the prompt's eight
   weekly sections do not map onto the template's four pages. Conflict 15, the
   template's discussion rubric expects two to three posts per week and this
   course expects one post plus one reply. Conflict 20, the template makes
   everything due Sunday, and this discussion asks for a first post by Thursday
   so that a peer has something to reply to. Conflict 22, the template's
   objectives table has no column for a parent CLO, and this week's three
   objectives all carry one. None is resolved here.
8. **No week 4 criterion links to CLO1.** Stated above, and repeated here because
   it is a reporting decision, not a content one. If the program wants week 4 to
   feed CLO1, the outcome calculation method has to change first.
9. **Three edits made in the code ledger.** Section 6 of
   `docs/phase1-blueprint/code-ledger.md` is the week 4 contract the notebook
   author builds from, so it was brought into line with this spec. Its cell 14
   now names the five items that cell prints, which is what the graded screenshot
   shows. Its submission artifact now carries the two call ids. Its sidebar note
   now points at 4b rather than at a single sidebar. Nothing else in the ledger
   moved.
10. **The alignment matrix now carries both week 4 criteria.** Section 11 of
    `docs/phase1-blueprint/alignment-matrix.md` lists every rubric criterion that
    links to an Outcome. It names week 4 criterion 2, "Tool call handled end to
    end", and week 4 criterion 3, "Reading your own results", both as supporting
    evidence for CLO3. The CLO3 row of the main matrix names the same two. The
    criterion names in both documents match this spec word for word.

## Measured readability

Measured with the course readability gate on 2026-09-04. This is a program manager
document, so the whole page is held to grade 9.5, an average sentence of 18
words and no sentence over 45. Student-facing text drafted inside it is held to
grade 7 and an average sentence of 12 words.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 5.97 | 13.6 words | 36 words |
| The three objectives | 5.31 | 11.5 words | 12 words |
| The discussion prompt | 1.90 | 7.7 words | 14 words |
| The written answer prompt | 2.90 | 11.1 words | 24 words |
| The rubric criterion column | 4.53 | 11.2 words | 24 words |

No prose paragraph on this page runs over 70 words.

**How the short blocks were scored.** The readability tool declines to score
anything under 40 words. A block under that floor was repeated until it cleared
it and then scored, which is the method week 6 uses. Repeating text does not
move a Flesch-Kincaid grade, because the formula is a ratio of words to
sentences and syllables to words. A rubric row is the criterion column, each
cell read as one line, with the header row left out.

Nothing on this page had to be reworded to reach these numbers. The one change
made here was to the terms note, which now defines allowlist and blocklist
before the tool table uses them.
