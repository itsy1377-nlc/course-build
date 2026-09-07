# Week 2 spec: Structured output

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 2 of 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.

Week 2 carries the primary evidence for course learning objective 2 (CLO2).
The build prompt fixes the wording of that objective, so it is quoted here
word for word.

> **CLO2 (Analyze):** Classify a suspicious email as malicious or benign using
> an AI model, then validate the model's output before trusting it.

The week 8 final exam adds recognition items on the same objective. The graded
proof lives here.

Eight terms are used below.

- A *cell* is one block in a notebook that a student runs on its own.
- A *TODO cell* is a cell with a comment marking the lines the student writes.
- *Pre-written* means the cell arrives complete and working.
- *JSON* is a plain text format for writing a set of named values.
- A *schema* is the written rule that says which names an answer must carry and
  which values are allowed.
- A *sidebar* is a short, ungraded practice notebook on an everyday topic.
- The *serving stack* is the software that runs the model and answers requests.
  The course tested one of these and wrote down what it returned.
- A *reasoning block* is text a model writes to itself before its answer. One of
  the two course models writes one. The course strips it off.

## Capability added

The agent answers in a fixed JSON shape, and the student's code checks that
shape before anything uses the answer.

This is exactly one capability, for three reasons.

1. The model call itself does not change. Week 1 built `ask_model()`, and week 2
   calls it with a different instruction. No new network code appears.
2. Nothing new enters the prompt. The agent still sends the same email body it
   sent in week 1, plus a fixed instruction naming the four keys. Headers,
   authentication results and tool output all stay out until later weeks.
3. The retry is part of the capability, not a second one. A shape check that
   catches a bad answer and then stops is not usable. The retry is the handler
   for the condition the check finds, so the two ship together.

The four keys are `verdict`, `category`, `confidence` and `indicators`. The
allowed values for `verdict` and `category` are rendered from
`corpus/spec/enums.json`, which is the same file that renders the week 7
scoring list. So the model is asked for the categories it will later be scored
against.

One idea drives the week: a badly shaped answer is a normal condition to
handle, not a failure. The serving stack tests recorded a model that ran out of
tokens mid-thought and returned an empty answer in 4 of 6 runs at one setting.
Students meet that condition on purpose, in a pre-written cell, before they
write anything.

## Lab deliverable

One file, `week2_classification.json`, written by a single pre-written export
cell.

For each of emails 001, 002, 003 and 004 it holds the email id, the checked
answer, `schema_ok`, `problems`, and how many tries it took. Every try is
recorded, and `schema_ok` and `problems` are written on the accepted try as
well as on the failed ones. `problems` is an empty list when the check found
nothing wrong.

That last point is what makes the file gradeable. A student who wired in
`schema_errors()` and one who skipped the check and kept the first parse would
otherwise look identical on an email that passed on the first try.

The file also holds the session token totals, the model name, and a
`sample_checks` block. That block is the four saved replies the check cell
already feeds in, one clean and three broken, each with what the check
reported.

So three recorded failures and their problem text sit in every submitted file,
whatever the model did on the day. The samples are saved text, so the block
costs no extra model calls.

The four emails are set by the corpus design. 001 is a credential phishing
message, 002 is a real internal notice, 003 is marketing spam, and 004 is a
gift-card style business email compromise attempt. Together they hit four of
the seven categories and both verdicts. 003 is the case that proves the two
fields are independent: its category is spam and its verdict is benign.

## What the student writes, what arrives pre-written

Two TODO cells. Thirteen written lines in the reference solution, up to
seventeen in the one-condition-per-line style week 0 teaches. Blank lines and
comments are not counted.

| Cell | What the student writes | Lines |
|---|---|---|
| TODO 1 | `extract_json(text)`. Calls `strip_reasoning()`, tries `json.loads()`, returns the dictionary or `None`. | 5 to 7 |
| TODO 2 | `classify_email(parsed, max_tries=3)`. Builds the prompt, calls `ask_model()`, extracts, checks with `schema_errors()`, logs the try, asks again with the problems attached, returns the checked answer or `None`. | 8 to 10 |

Nine items arrive pre-written and working this week, on top of everything week
1 established.

| Name | What it does |
|---|---|
| `load_email(email_id, known_names=None)` | Reads one email by its id and stamps that id into the record |
| `OUTPUT_SCHEMA` | The required answer shape and the allowed values, rendered from `corpus/spec/enums.json` |
| `schema_text(schema)` | Renders one schema as the lines the prompt carries |
| `CLASSIFY_INSTRUCTIONS` | The fixed instruction text naming the four keys |
| `build_classify_prompt(parsed)` | Joins the instructions, the rendered schema and the email body into one prompt |
| `strip_reasoning(text)` | Removes a leading reasoning block, a stray closing tag, and code fences |
| `schema_errors(data, schema)` | Returns a list of plain-language problems, empty when the answer is good |
| `ATTEMPT_LOG` | A list holding every try, good or bad |
| `log_attempt(...)` | Adds one try to that list |

Three design notes the program manager should see.

First, `schema_errors()` is pre-written on purpose. Walking a schema by hand is
not a 5 to 15 line job. The student wires it in and decides what to do with
what it returns, which is the part that teaches the objective. The retry loop
is theirs.

Second, `strip_reasoning()` is pre-written because the serving stack tests found
three places a model's private reasoning text can appear, and one of the two
course models produces none at all. Handing students that mess would teach
nothing about triage.

Third, `load_email()` is the loader every later week uses. Week 1 read a mail
file straight through the parser, because week 1 needed nothing else from it.
The attempt log records one row per try against an email id, so from this week
on the record has to carry its own id. The code ledger's section 2.5 fixes it
as the one loader, so weeks 3 to 7 inherit one and not two.

**Flag: the line count runs slightly long.** The build prompt targets 5 to 15
written lines per lab. Week 2 lands at 13 to 17. The extra lines are the retry
loop, which is the heart of the objective and cannot be cut. The check cells
accept both the compact style and the longer one, and the rubric never rewards
shorter code.

## Weekly objectives

Three objectives. All three carry CLO2, because week 2 is that objective's
primary evidence and adds no other.

| # | Objective, as students see it | Parent | Verb | Words |
|---|---|---|---|---|
| 2.1 | Turn the model's reply into a dictionary your code can read. | CLO2 | Turn | 11 |
| 2.2 | Check each model answer against the course output schema. | CLO2 | Check | 9 |
| 2.3 | Retry a failed answer with the schema problems added to the new prompt. | CLO2 | Retry | 13 |

Each one names something a grader can see in `week2_classification.json`
without opening a student's notebook.

- **2.1** shows up as a parsed answer under each email id.
- **2.2** shows up as the `schema_ok` and `problems` fields. They are written
  on every try, including the ones that passed first time.
- **2.3** shows up as the try count and the problems recorded against each
  failed try.

Objective 2.3 needs one extra note, because a live retry depends on the model.
The serving stack tests produced valid four-key JSON in 3 of 3 runs at the
setting week 2 recommends, so a clean four-email run is the likely case rather
than the edge case.

The file therefore also carries the `sample_checks` block described above:
three broken saved replies, each with the problems the check reported. A
grader always has a recorded failure and its problem text to read. A live try
count above one is the stronger evidence when the model supplies it.

## Sidebar

**Construct:** dictionaries and key access, JSON as text, and try/except with a
retry.

**Domain:** weather readings from a rooftop station. No email, no alerts, no
verdicts.

The build prompt allows one construct per sidebar, so this week ships three
short ones in sequence. All three share the weather domain, so students carry
one mental model through them.

| Sidebar | Construct | What it shows | Links back to |
|---|---|---|---|
| 2A | Dictionaries and key access | A reading held as `{"station": ..., "temp_f": ..., "sky": ...}`, read by key, then read with a default when a key is missing | Week 0, dictionaries and key access |
| 2B | JSON as text | The same reading arriving as a line of text, and `json.loads()` turning it into something you can read by key | Week 0, JSON as a dictionary in text form |
| 2C | try/except with a retry | A loop that asks a fake gauge up to three times, catches a bad line, and stops on the first good reading | Week 0, try/except |

Each sidebar runs end to end and ends with one small "try changing this"
prompt. Sidebar 2C's prompt asks the student to set the gauge to fail every
time and watch what the loop does when the tries run out.

Line counts are taken the way week 1 takes them: every line in the code cell,
including the title comment and any blank line. 2A is 15 lines, 2B is 16 and
2C is 19. All three sit under the 20 line ceiling.

**Why pasting the sidebar into the lab fails.** Sidebar 2C reads its three
lines out of a list named `LINES` and keeps the good one in `reading`. It
defines no function at all. A student who pastes it where the lab calls
`extract_json(text)` gets a NameError on `LINES` and never reaches the schema
check.

## Reading

Week 2 ships two reading pages rather than one. The reason is set out at the
end of this section.

**Page 1: Why a fixed answer shape matters.** About 900 words. 20 minutes.

What it covers, in order.

1. What structured output is, and why free text cannot be acted on by code.
2. JSON as text: a set of named values written as a line of characters. Text
   that looks like a dictionary is not one until your code loads it.
3. What a schema is, in plain words, and the four keys this course uses.
4. Why valid JSON can still be a wrong answer. A reply can load cleanly and
   still carry a category the course does not use.

Two short JSON blocks are embedded: one good answer, and one that loads
cleanly but names a category the course does not use. One stop-and-think
question sits inside the page and is ungraded.

**Page 2: When the answer comes back wrong.** About 950 words. 22 minutes.

What it covers, in order.

1. Malformed output as a normal condition. The three shapes seen in testing:
   an answer wrapped in extra text, an answer cut off partway, and an empty
   answer with a stop reason of `length`.
2. The retry, and the one rule that makes it work: send the problem back with
   the request, not just the request again.
3. What a student's code should do when the tries run out, so no loop ships
   with nothing under it.
4. A short closing on cost. Every retry is another paid call.

Three short JSON blocks are embedded, one per failure shape. One
stop-and-think question sits inside the page and is ungraded.

Three citations are planned. Page 1 cites RFC 8259 for the JSON format. Page 2
cites the OWASP Top 10 for Large Language Model Applications entry on improper
output handling, and the model vendor's own documentation for the reasoning
block behavior.

Every citation is checked for licence and for whether the link resolves before
the page ships.

**Reading time: 42 minutes, inside the 40 to 50 minute band.** The course
prices one reading pass at 200 words a minute, which is section 2 of the survey
content plan. The rest of each page's minutes are study time on the JSON blocks,
the stop-and-think question and one cited source.

| Page | Prose words | One pass at 200 words a minute | Blocks, question and a second pass | One cited source | Page total |
|---|---|---|---|---|---|
| 1. Why a fixed answer shape matters | 900 | 5 | 11 | 4 | 20 |
| 2. When the answer comes back wrong | 950 | 5 | 14 | 3 | 22 |
| **Both pages** | **1,850** | **10** | **25** | **7** | **42** |

**Why two pages.** The build prompt budgets 40 to 50 minutes of reading a week.
The writing standard caps one reading page at 1,400 words and targets 900 to
1,050. No realistic pace turns one page into 40 minutes.

Splitting the week's reading settles it without bending either rule. Each page
is measured against the 1,400 word cap on its own. Each sits inside the 900 to
1,050 word target. The two together reach the reading band.

This is the rule the build follows wherever the two collide: split the
reading, not the standard. It is stated here so it is not decided again week
by week.

## Discussion prompt

Written out below exactly as students will see it.

Post by Thursday. Reply to one classmate by Sunday at 11:59 PM Central. Write
about 150 words in your post. Write about 60 words in your reply.

Open your `week2_classification.json` file. Find one email where your agent
needed more than one try, or where the first answer was wrong.

In your post, give all four of these.

1. The email id, plus the verdict and category your agent ended up with.
2. The exact problem your code reported on the failed try. Copy the line.
3. Your best guess at why the model answered that way.
4. One change you would make to the instructions to stop it happening again.

If every email passed on the first try, say so. Then post the email your agent
was least sure about. Give its confidence number. Say whether you agree with
it.

Then reply to one classmate. Compare their failed try to your own. Name one
thing that was the same and one thing that was different. A reply that only
agrees does not count.

You may use AI help on this post. If you do, add one line saying what you asked
it.

**Why this cannot be answered without doing the lab.** Every part asks for the
student's own file: their email id, their problem text, their try count, their
confidence number. There is no general opinion to give.

**Time:** 20 minutes, including the reply.

## Submission artifacts

Three items. Nothing else. No zip file, no folder, no link.

**Screenshot.** One image of the output of the results cell, the one that runs
all four emails. It must show all four rows with the email id, verdict,
category, confidence and tries used, plus the token line printed under the
table. One screenshot, whole output visible. No cell in the notebook prints key
material, so no screenshot can capture it.

**File.** `week2_classification.json`, attached as itself. The export cell
prints the full path and the first few lines, so the student can see what they
are attaching.

**Written answer, 3 to 5 sentences.** Shown to students as written here.

In 3 to 5 sentences, answer this. Which of your four emails took more than one
try? Copy the exact problem your code reported on that failed try. If all four
passed on try one, say so instead. Then give the lowest confidence number you
saw. Either way, name one change you would make to the instructions.

Both paths through that prompt reach full credit on rubric criterion 4. A
student whose four emails all passed on the first try is never asked for
problem text they do not have.

All three items are gradeable without running the student's notebook.

## Rubric sketch

Four criteria, 100 points. Criterion 2 is the only one that carries a Canvas
Outcome, which matches the alignment matrix. The other three are declared
non-CLO expectations, as the build prompt requires.

Every lab in the course carries 100 points. That is what makes the seven labs
weigh equally inside the 60 percent Labs group, and the grade distribution and
token totals document holds the whole table.

| # | Criterion | Points | Levels | Canvas Outcome | What earns full credit |
|---|---|---|---|---|---|
| 1 | Submission completeness | 15 | 15 / 10 / 0 | None. Non-CLO expectation. | All three items are present and readable. |
| 2 | Output validation | 50 | 50 / 35 / 20 / 0 | CLO2: Classify and validate an AI verdict. Primary evidence. | The file carries a checked answer for all four emails. It carries `schema_ok` and `problems` on every try, the accepted try included. Every failed try is recorded with the problems that caused it. |
| 3 | Results screenshot | 15 | 15 / 10 / 0 | None. Non-CLO expectation. | The screenshot shows all four emails and the token line, and is readable. |
| 4 | Written answer | 20 | 20 / 10 / 0 | None. Non-CLO expectation. | Three to five sentences carrying the student's own numbers. It names the email that needed more than one try. It copies the problem text their code reported. For a clean run it says so and gives the lowest confidence number in their own file. Either path also names one change to the instructions. |

Every level is named and priced. Criterion 2 uses the four labels from the
alignment matrix mastery scale. Criteria 1, 3 and 4 use three labels each.

| Criterion | Level names and points, highest first |
|---|---|
| 2, Output validation | Exceeds standard 50, Meets standard 35, Approaching standard 20, No evidence 0 |
| 1, Submission completeness | Full 15, Partial 10, Missing 0 |
| 3, Results screenshot | Full 15, Partial 10, Missing 0 |
| 4, Written answer | Full 20, Partial 10, Missing 0 |

**Two scales on one row, kept apart on purpose.** Criterion 2 reports into
CLO2, so its row carries two numbers that do different jobs. The rating label
the grader picks is what Canvas records against the Outcome, on the shared
scale of 4, 3, 2 and 0.

The criterion points on the same row are what the grade uses, on 50, 35, 20 and
0. The four labels line up one to one, so the grader picks once and both
scales follow. The criterion points are not the outcome result and are never
reported as one.

One build detail to confirm in Canvas before Phase 2. An Outcome-linked
criterion may keep its own point values, or it may inherit the Outcome's 4, 3,
2, 0.

If Canvas forces the inherited values, criterion 2 is worth 4 points and the
rubric totals 54. The other three criteria are then rescaled to bring the lab
back to 100. Week 5 raises the same question about its own scaled criterion.

Nothing in this rubric needs the instructor to run a student's code.

## Self-check

Six items, multiple choice, low stakes. Unlimited attempts, highest score
kept. Self-checks are 8 percent of the course grade in total.

The six cover:

1. Which four key names the course output schema requires.
2. What a stop reason of `length` means, and what your code should do next.
3. Why the model's private reasoning text has to come off before the answer is
   loaded.
4. Which line of an error message names the thing that failed.
5. What a retry must add to the second request to be worth making.
6. Why an answer can load cleanly and still fail the schema check.

Items 1, 5 and 6 sit on this week's objectives. Items 2, 3 and 4 are the three
failures students are most likely to meet alone at 11pm.

## Time estimate

| Activity | Minutes |
|---|---|
| Overview video plus the "what success looks like" video | 8 |
| Sidebars 2A, 2B and 2C | 30 |
| Reading, both pages | 42 |
| Lab: read the notebook, run the pre-written cells | 30 |
| Lab: TODO 1, `extract_json()` | 30 |
| Lab: TODO 2, `classify_email()` | 60 |
| Lab: run all four emails, fix what breaks | 40 |
| Lab: export the file and check it | 20 |
| Discussion, post plus one reply | 20 |
| Self-check and submission | 30 |
| **Total** | **310 minutes, about 5.2 hours** |

The lab totals 180 minutes, at the top of its 2.5 to 3 hour band. Every other
line sits inside its own band too, reading included. Nothing in this week now
runs short of a stated band.

The week comes in 50 minutes under the 6 hour ceiling. That margin is the
slack week 2 needs, because it is the first week a student writes a loop.

## Token estimate per full lab run

Prompt parts measured from the real corpus files. Week 2 sends no facts block
and no tool results; those start in weeks 3 and 4.

Line 1. Fixed parts, measured on the shipped notebook. `CLASSIFY_INSTRUCTIONS`
is 628 characters. `OUTPUT_SCHEMA` rendered from `corpus/spec/enums.json` is
347 characters, which is the figure section 2 of the grade distribution and
token totals document holds, and weeks 3, 4, 5 and 6 send the same 347.
`build_classify_prompt()` also puts a blank line between the two and the line
`The reported email:` in front of the body, which is 25 more characters. So
1,000 characters go out on every call.

Line 2. Email bodies, plain text part, measured with the course parser on the
rendered files: 001 is 807 characters, 002 is 874, 003 is 1,150 and 004 is 499.
The four average 833. Prompt per call is (1,000 + 833) / 4 = 458 tokens.

Line 3. Completion per call is counted at 90 tokens, just above the highest
reasoning-off measurement of 79 for a four-key JSON answer. The extra allows
for the longer category names and up to six indicators.

A typical run makes 6 calls, and they are not all the same size. Two of the six
are the raw run in cell 7. That cell calls the model twice on the same prompt:
once with room to answer, and once capped at 12 tokens, so a student sees a
stop reason of `length` live. The other four are one clean try each on the four
emails. The table below is the run, call by call.

| Call | Prompt characters | Prompt tokens | Completion tokens |
|---|---|---|---|
| Cell 7, email 001, room to answer | 1,807 | 452 | 90 |
| Cell 7, email 001, capped at 12 tokens | 1,807 | 452 | 12 |
| Cell 14, email 001 | 1,807 | 452 | 90 |
| Cell 14, email 002 | 1,874 | 469 | 90 |
| Cell 14, email 003 | 2,150 | 538 | 90 |
| Cell 14, email 004 | 1,499 | 375 | 90 |
| **Total, 6 calls** | | **2,738** | **462** |

So a typical run is **6 calls and about 3,200 tokens**. A worst case is 14
calls: the same two in cell 7, plus three tries on each of the four emails.
That is 6,406 prompt tokens plus 1,182 completion, call it **7,600**.

Those figures were taken by running the notebook's pre-written cells against a
stub model, with a reference solution in each of the two TODO cells, and
reading the counter the notebook prints.

One warning for the budget. If the reasoning model runs with reasoning left on,
measured completion rises to between 819 and 1,173 tokens per call. The five
uncapped calls then cost about 1,000 each and the capped one still costs 12,
so a typical run costs about 2,738 + 5,012 = 7,750 tokens, call it 7,800. That
is nearly two and a half times as much. The configuration cell turns reasoning
off for that model, and this is why.

## Assumptions and gaps

1. All four emails this week are rendered as files, and every character count
   above is measured on them rather than estimated. A change to any of the four
   bodies moves the token figure, so it is re-measured when the corpus changes.
2. The call count of 6 typical and 14 worst case was taken by executing the
   notebook's pre-written cells, not read off a plan. Two of the six are the
   raw run in cell 7, which calls the model twice on purpose.
3. The lab is scored out of 100 points, the same as every other lab. The seven
   labs are 60 percent of the course grade in total, and a percent-weighted
   group scores as points earned over points possible inside it. Equal points
   across the seven labs are therefore what makes the seven weigh equally. The
   grade distribution and token totals document sets the points for every graded
   item in the course.
4. Criterion 2 is the only Outcome-linked criterion this week, which keeps the
   alignment matrix exact. If the program wants a second criterion reporting
   into CLO2, say so before Phase 2.
5. The 42 minute reading figure is one pass at 200 words a minute plus study
   time on the five JSON blocks, the two stop-and-think questions, and one cited
   source per page. It is a working-pace figure, not a comfortable-reading one.
   It is re-measured after Phase 2, as week 1 is.
6. Late work and resubmission policy is still unset, so the rubric says nothing
   about a resubmitted file.

## Measured readability

Measured with the course readability gate on 2026-09-04. This is a program manager
document, so the whole page is held to grade 9.5, an average sentence of 18
words and no sentence over 45. Student-facing text drafted inside it is held to
grade 7 and an average sentence of 12 words.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 5.67 | 13.3 words | 34 words |
| The three objectives | 4.79 | 11.0 words | 13 words |
| The discussion prompt | 2.87 | 8.5 words | 18 words |
| The written answer prompt | 3.43 | 9.5 words | 11 words |
| The rubric criterion and full-credit columns | 6.17 | 10.8 words | 17 words |

No prose paragraph on this page runs over 70 words.

**How the short blocks were scored.** The readability tool declines to score
anything under 40 words. A block under that floor was repeated until it cleared
it and then scored, which is the method week 6 uses. Repeating text does not
move a Flesch-Kincaid grade, because the formula is a ratio of words to
sentences and syllables to words. A rubric row is the criterion column, each
cell read as one line, with the header row left out.

**One number that moved.** The rubric's criterion and full-credit text read an
average sentence of 15.1 words, over the 12 word limit for text a student reads
to find out what earns the points. The driver was a 37 word either-or sentence
in criterion 4. That sentence is now three short ones, criterion 2's opening
sentence was split as well, and the column reads 10.8.
