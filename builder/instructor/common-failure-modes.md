# Common failure modes: Start Here, week 0, week 1 and week 2

Northeast Lakeview College, Cyber Defense program. ITSY 1377, Agentic AI and
Security Operations. Nothing on this page is student-facing.

This is a triage list. Find the symptom, read the cause, send the fix.

Every number here comes from a file in this repository, and the file is named
where the number is used. Paths are written from the repository root,
`~/workspace/dev/ITSY1377/`. Cell numbers count from 1, the way the student
pages count them.

---

## How to use this page

**Ask two questions before anything else.** They resolve most messages on their
own.

1. **"What does the last line of the error say?"** Not the first line, not a
   screenshot of the whole block. The last line names the error type and the
   thing that failed. This is the routine the course already teaches on the page
   **If something breaks** (`builder/content/pages/if-something-breaks.md`).
2. **"What did the configuration cell print?"** It is cell 3 in week 1 and cell 2
   in week 2. It prints the model, the endpoint, the extra request fields,
   whether a key was found, and whether the email files were found. It prints no
   key material, so it is always safe to ask for.

**Never ask a student to print, paste, screenshot or read out an API key, and
never ask them to print the environment.** No cell in any notebook in this
course prints key material, and nothing on this page needs it.

**About the order below.** It runs from what will happen most often to what will
happen least, and that order is a judgment, not a measurement. Nobody has taught
this course yet. It is built from three things: the failures the week specs
already predict, the failures a pre-written cell produces on purpose so that
every student meets them, and which of the six Python errors the week 0 outline
maps to weeks 1 and 2 (`builder/docs/phase1-blueprint/week-00-outline.md`,
section 10). Re-order it after the first term from what actually lands in your
inbox.

---

## 1. A cell was run out of order, so a name is not defined

**What the student says.** "It says `ask_model` is not defined, but it is right
there on my screen." "I ran it and it worked yesterday."

**The real cause.** Notebook cells run in the order they are clicked, not the
order they are printed. A cell that was never run defines nothing, and the text
of it still sits on screen looking finished. A kernel restart has the same
effect: every name is gone while every output stays visible.

This is the failure the course calls the notebook trap, and the student page
already names it as the one that costs the most time
(`builder/content/pages/if-something-breaks.md`).

**The fix, two steps.**

1. Run the cells above the failing one, from the top.
2. If that does not do it, restart the kernel and run all cells in order. Then
   read the error again.

**Where it bites in these two weeks.**

| Week | Missing name | Because |
|---|---|---|
| 1 | `ask_model` | Cell 8, the check cell, was run before cell 7, TODO 1 |
| 1 | `parse_eml`, `email_001`, `INSTRUCTION` | Cell 9 was skipped |
| 1 | `PROMPT_001`, `SIX_ANSWERS`, `PROMPT_TOKENS_001` | The export cell 14 was run before cell 11 |
| 1 | `PROMPT_002`, `ANSWER_002` | The export cell 14 was run before cell 12 |
| 2 | `extract_json` | Cell 11, the check cell, was run before cell 10, TODO 1 |
| 2 | `schema_errors`, `ATTEMPT_LOG`, `log_attempt` | Cell 12 was skipped, and cell 13 calls all three |
| 2 | `RESULTS`, `run_sample_checks` | The export cell 16 was run before cells 15 and 11 |

One name behaves differently and is worth knowing. The week 1 export cell reads
the student's TODO 2 result with `globals().get("answer_001", "not recorded")`,
so a missing `answer_001` writes the words `not recorded` into the file instead
of raising. That costs no points. Grading notes section 4.1 covers it.

**What a rerun costs.** A full pass is about 2,560 tokens in week 1 and about
3,200 in week 2
(`builder/docs/phase1-blueprint/grade-distribution-and-tokens.md`, section 3).
Restarting and running all is cheap. Say so, because students hesitate.

---

## 2. A student who skipped week 0 cannot read a traceback

**What the student says.** "I got a huge red error and I have no idea what any
of it means." "Something about a file called `parse_eml` that I never touched."

**The real cause.** They are reading the traceback from the top. The top frames
belong to pre-written code they did not write, so the first thing they read is
code that is not theirs and not the problem. Python puts the answer at the
bottom.

Most of these students took the week 0 self-assessment, scored low, and skipped
the notebook anyway. Week 0 is optional and open all term
(`builder/docs/phase1-blueprint/week-00-outline.md`).

**The fix, two steps.**

1. Send the five step routine. It is on the page **If something breaks**, which
   is in the Orientation module and reachable from every week. Read the last line
   first. Name the error type, which is the word before the colon. Find the last
   line that names your own cell. Print the value on the line above the one that
   failed. Change one thing and run it again.
2. Send them to section 10 of the week 0 notebook, and say what it is: thirty
   minutes, one traceback walked line by line, then six errors broken on purpose
   so they read the real message and then the fix
   (`builder/lab/notebooks/week00-python-on-ramp.ipynb`, section 10).

Say plainly that section 10 is worth doing even if they skip the other nine
sections. Week 1 already holds back ten minutes of its time budget for one
traceback (`builder/docs/phase1-blueprint/week-01-spec.md`, section 11), so this
is expected work, not lost time.

**The four errors these two weeks actually produce.**

| Error | What it means here | Where |
|---|---|---|
| `NameError` | A name is used before it exists, or its cell was never run | Failure mode 1 above, and every sidebar pasted into a lab cell |
| `TypeError` | A value used in a way its kind does not allow, usually a `None` where a dictionary was expected | Week 2, when `extract_json()` returns `None` and the next line reads a key from it |
| `ValueError`, including the JSON decode error | The kind was right and the content was wrong. Text that is not JSON | Week 2, the exact failure `try`/`except` is there to catch |
| `SyntaxError`, `IndentationError` | Python could not read the line at all | Any week a student writes a `def`, an `if` or a loop |

`KeyError` and `AttributeError` belong to weeks 3, 4, 6 and 7 and are rare in
these two weeks (`builder/docs/phase1-blueprint/week-00-outline.md`, section 10).

---

## 3. The model returns something that will not parse

**What the student says.** "My `extract_json` keeps returning `None`." "It says
the answer is not a JSON object." "The model returned nothing at all."

**The real cause, five shapes, and the first two are the common ones.**

1. **The model ran out of room.** The stop reason is `length` and the content is
   empty. `send_request()` writes a plain sentence into the content slot in that
   case, beginning `No answer text came back. The model used all of its room`, so
   `extract_json()` receives prose and correctly returns `None`
   (`builder/lab/notebooks/w2-lab.ipynb`, cell 4). Week 2 cell 7 produces this on
   purpose with `max_tokens=12`, so **every student meets it before they write
   anything**. Some of them report it as a bug.
2. **A reasoning block in front of the answer.** On the reasoning model the
   thinking arrives in a separate field and `send_request()` moves it out of the
   way. A stray closing tag with no opener can still arrive inside the content,
   because that model's template starts it inside the block
   (`builder/docs/serving-stack-shape.md`, section 6, item 1). `strip_reasoning()`
   handles the block, the stray closer and the fences. It is pre-written in
   cell 9.
3. **Code fences around the JSON.** Same fix, same pre-written function.
4. **JSON cut off partway**, such as `{"verdict": "malicious", "category":
   "credential_ph`. Nothing loads that. `None` is the right answer.
5. **Valid JSON that is still wrong.** It loads cleanly and names a category the
   course does not use, or a confidence above 1.0, or an empty indicator list.
   That is not a parse failure. `schema_errors()` reports it, and the retry is
   what handles it. Students confuse this with a parse failure constantly.

**The fix, two steps.**

1. Check the order inside their `extract_json()`. It has to call
   `strip_reasoning()` first, then `json.loads()`, with the load inside a
   `try`/`except` that returns `None`. A student who loads first and strips
   afterwards fails on the clean sample.
2. Check what the configuration cell printed on the line `Extra fields:`. On a
   `granite4.2` model it must read `{'reasoning_effort': 'none'}`. If it reads
   `{}` the model is thinking inside its token budget, and that changes
   everything: measured at 819 to 1,173 completion tokens and 15 to 22 seconds
   for one classification with reasoning on, against 65 to 79 tokens and about
   1.3 seconds with it off, and 4 of 6 default-mode JSON runs exhausted a
   1,024 token cap (`builder/docs/serving-stack-shape.md`, sections 3.4 and 5).

**What to say, once, in the week 2 announcement.** A badly shaped answer is a
normal condition to handle, not a failure and not their fault. That sentence is
the week's whole lesson, and it is already in the notebook's opening cell. The
model limits page in this folder carries the longer version.

---

## 4. The notebook kernel dies, or the session times out

**What the student says.** "Everything stopped." "It says the kernel is
restarting." "I came back in the morning and nothing works." "The circle next to
the cell just stays filled in."

**The real cause.** The notebook server restarted the kernel, or the browser
session expired while the notebook sat idle. Files on disk survive. Names in
memory do not. A long single call can look the same: `send_request()` waits up
to 120 seconds for one answer and then reports that the model took too long
(`builder/lab/notebooks/w1-lab.ipynb`, cell 5, `REQUEST_TIMEOUT`).

**The fix, two steps.**

1. Reload the page. If it asks, sign out of the notebook server and sign back
   in. The page **Your computer and the notebook server** carries the full
   sequence, including trying a different browser
   (`builder/content/pages/canvas-and-tech-support.md`).
2. Restart the kernel and run all cells from the top.

**Three things to tell them, because they will assume the worst.**

- Their notebook file is still there, and so is any file the export cell already
  wrote. The server keeps their work for the whole term.
- Rerunning costs tokens again: about 2,560 in week 1 and about 3,200 in week 2.
  That is not a reason to avoid restarting.
- The token counter starts at zero on a restart. `USAGE` is a plain dictionary in
  the notebook, so the totals in an exported file only cover the session that
  wrote it (`builder/docs/phase1-blueprint/code-ledger.md`, section 2.2).

That last point matters when you grade. A small `Calls counted` in week 1 or a
small `tokens.calls` in week 2 usually means a restart, not idleness. Grading
notes sections 4.2 and 5.2 say what to do with it.

---

## 5. The API key environment variable is missing

**What the student says.** "The first cell says `API key: NOT FOUND`." "Every
call says the model service answered with status 401."

**The real cause.** The key is placed into each student's notebook environment by
the hosting setup, and the configuration cell reads it with `os.environ`
(`builder/docs/phase1-blueprint/code-ledger.md`, section 2.1). A kernel that
started before the injection, or a session that lost it, has no key. Students
never type, paste, see or screenshot a key at any point in this course.

Note the second symptom is not a Python error. `send_request()` only sets the
authorization header when a key is present, so against an endpoint that requires
one the failure arrives as a printed line reading `This call did not work. The
model service answered with status 401.`

**The fix, two steps.**

1. Close the notebook, open it again, and run the configuration cell. That
   starts a fresh kernel, which re-reads the environment. The notebook says this
   itself when the key is missing.
2. If it still says `NOT FOUND`, stop. This one cannot be fixed from inside the
   notebook. The student emails you and you take it to the hosting setup. The
   environment setup page in this folder is where that lives.

**Two rules for you.**

- Ask for the printed lines from the configuration cell. Nothing else. Those
  lines are the whole diagnosis and they contain no key.
- Never send a student a key, never ask them to type one into a cell, and never
  accept a screenshot that shows one. If key material ever appears on screen in
  this course, that is an incident to report, not a workaround to use.

---

## 6. A student cannot find the corpus files

**What the student says.** "It says `FileNotFoundError: No mail file starts with
001`." "It says `No module named 'parse_eml'`." "The first cell says
`Email files: NOT FOUND`."

**The real cause.** All three are the same fault. The configuration cell works
out where the course files are by looking, in order, at the `ITSY1377_COURSE_DIR`
setting, then the notebook's own folder, then each folder above it, for one that
contains `corpus/emails/teaching`. A notebook that was copied, downloaded or
uploaded somewhere outside the course tree has no such folder above it. Because
the tools folder is worked out from the same place, `parse_eml` also fails to
import for the same reason.

`email_path("001")` then looks for a file starting `001-` in that folder and
raises when it finds none.

**The fix, two steps.**

1. Move the notebook back into the course folder, the one that contains
   `corpus`, and run the configuration cell again. It has to print
   `Email files: found` before anything else will work.
2. If the course folder is missing entirely from the server, that is a hosting
   problem, not a student problem. Escalate it. Do not have the student download
   the corpus by hand.

**What should be there.** Weeks 1 and 2 use four files, all in
`corpus/emails/teaching`: `001-payroll-deposit-verify.eml`,
`002-it-maintenance-window.eml`, `003-inkmoor-spring-catalog.eml`,
`004-cfo-quick-task.eml`.

---

## 7. A student edited a pre-written cell and cannot get back

**What the student says.** "I changed something in a cell I was not supposed to
touch and now nothing runs." "I deleted a cell by accident."

**The real cause.** There is no version history on the notebook server and no
undo that survives a kernel restart. Pre-written cells are load-bearing: one of
them defines the only function in the course that talks to the network, cell 5 in
week 1 and cell 4 in week 2, and everything after it depends on that function.

**The fix, two steps.**

1. Open a fresh copy of that week's starter notebook from the module in Canvas
   and save it under a new name. Every module carries its lab notebook as an
   item (`builder/content/course.yaml`).
2. Copy only the TODO cells across from the broken notebook. Two cells in week 1,
   two in week 2. Then run the fresh notebook from the top.

Never copy a pre-written cell out of the broken notebook into the fresh one.
That carries the edit across, which is the thing you are trying to undo.

**Say this once, in the week 1 announcement.** Two cells are yours in each lab
and everything else arrives finished and working. The one thing that is safe to
change in a pre-written cell is nothing.

**The reassurance that goes with it.** A broken week 1 notebook does not block
week 2. Week 2 cell 5 arrives with a working `ask_model()` and the week 1 email
reader already in it, and students may paste their own version over it if they
prefer (`builder/lab/notebooks/w2-lab.ipynb`, cell 5).

---

## 8. The token budget runs out

**What the student says.** "All of my calls suddenly stopped working." "It says
the model service answered with a status and some text."

**The real cause.** The budget is controlled centrally by you and the program,
and no lab contains a hard cutoff. So exhaustion arrives as an error from the
service rather than as a message from the notebook, and the exact wording depends
on the hosting. `send_request()` turns any non-200 answer into one printed line
that starts `This call did not work. The model service answered with status`,
followed by whatever the service said, and prints three things to check the
first time it happens.

**The fix, two steps.**

1. The student messages you and asks for a top-up. Policy, from the syllabus:
   running out costs no points, and waiting for a top-up costs no late penalty
   (`builder/content/pages/course-policies.md`, "Your token budget").
2. You top up, they rerun, you grade the rerun.

**Numbers to sanity-check a claim, all from
`builder/docs/phase1-blueprint/grade-distribution-and-tokens.md`, section 3, and
the two week specs.**

| Case | Tokens |
|---|---|
| Week 1, one clean pass | about 2,560 |
| Week 1, with one debugging rerun | about 5,100 |
| Week 2, typical run, six model calls | about 3,200 |
| Week 2, worst case, fourteen model calls | about 7,600 |
| Whole course, one clean pass through seven labs | 388,560 |
| Whole course, every lab rerun once | 777,120 |

A student showing tens of thousands of tokens in week 2 has rerun a great deal.
That is normal, it is what the rerun row plans for, and it is not misconduct.

**Where the student sees their own number.** Every call prints one line reading
`this call: N tokens. Session total so far: N.` and `show_tokens()` prints
`Tokens this session:` with four numbers. The counter reads the numbers the
service reports and never measures the length of the answer text, because on the
reasoning model the tokens spent thinking are billed and never shown
(`builder/docs/phase1-blueprint/code-ledger.md`, section 2.2).

**The one thing that burns a budget fast** is a loop with no cap. Week 2's
`max_tries=3` is that cap, and the lab page warns about it in a callout
(`builder/content/assignments/w2-lab.md`).

---

## Four more, less often

### 9. The model service is unreachable, or one call takes far too long

**Symptom.** "It just sat there and then said the model service did not answer."

**Cause.** The endpoint is down, or a single call is slow.
`send_request()` gives up after 120 seconds and reports it in plain words. For
scale: on the recommended configuration a classification takes about 1.2 to 1.5
seconds (`builder/docs/serving-stack-shape.md`, section 3.4). With reasoning left
on, the week 5 measurement recorded means of 81.0 and 84.6 seconds for a single
triage
(`builder/docs/week5-model-test.md`), which is long enough that a student assumes
the notebook has hung.

**Fix.** Rerun the configuration cell and read the three checks the notebook
prints. If the service is genuinely down, the student submits what they have and
messages you. Week 2's closing cell tells them exactly that: attach the file
anyway, email the instructor, "A dead endpoint is not a late assignment"
(`builder/lab/notebooks/w2-lab.ipynb`, cell 17). Week 1's closing cell tells them
the notebook still ran and still wrote the file, and to rerun the configuration
cell and email you what it printed, but it does not tell them to submit
(`builder/lab/notebooks/w1-lab.ipynb`, cell 15), so say that part yourself in the
week 1 announcement. Grading notes section 6.3 says how to handle the
submission.

### 10. The sidebar was pasted into the lab and does not work

**Symptom.** "I copied the example from the sidebar into the lab and it broke."

**Cause.** By design. No sidebar shares a single name with a lab. Week 1's
sidebars define `boxes_in_cases`, `shelf_name`, `on_hand`, `low_mark` and `note`
about a grocery stockroom. Week 2's build a weather reading keyed on `station`
and `temp_f` out of a list named `LINES`, and define no function at all. The
lab check cells call `ask_model()` and `extract_json()`, which no sidebar
defines, so a paste produces a `NameError` rather than a working lab
(`builder/docs/phase1-blueprint/week-01-spec.md`, section 5, and
`week-02-spec.md`, sidebar section).

**Fix.** Read the sidebar for the shape of the thing, then write the lab function
using the names the TODO comment gives. Every sidebar links back to the week 0
section that teaches its construct.

### 11. The retry is not a retry (week 2)

**Symptom.** "My retry runs three times and gets the same wrong answer every
time."

**Cause.** The second and third requests send the first prompt again. The
problems from the failed try were never added to it.

**Fix.** One step. Build the prompt with `build_classify_prompt(parsed)`, then
from try 2 onward append the previous try's problems to it. The TODO 2 comment
in cell 13 states the rule, and the lab page repeats it in a warning callout.

**Grading consequence.** The file shows three tries carrying identical problem
text. That is still a complete record of a validation that ran, so it still earns
credit on criterion 2. It costs three model calls instead of one.

### 12. There is no file to attach

**Symptom.** "I cannot find the file it wants."

**Cause.** The export cell was never run, or it was run before the cells that
build what it writes, which is failure mode 1.

**Fix.** Run the export cell last. It is cell 14 in week 1 and cell 16 in week 2.
It prints the full path of the file it wrote and the first few lines of it, so
the student can see exactly what to attach. Tell them to attach the file itself
and not to paste its text into the box.

---

## What to put in an announcement

One sentence each, in the weekly announcements, ahead of the failure rather than
after it. The drafted announcements in this folder already carry a sticking point
per week; these are the lines worth keeping in them.

- **Week 1.** Two cells are yours. Everything else arrives finished. If a name is
  not defined, restart the kernel and run every cell from the top before you
  change a thing.
- **Week 1.** Read the last line of an error first. The rest is context.
- **Week 2.** A badly shaped answer is a normal condition, not your fault, and
  handling it is the whole point of the week.
- **Week 2.** Your retry has to send the problem back with the request. Sending
  the same prompt again is not a retry.
- **Either week.** If the configuration cell says no key was found, or the model
  service is down, message me and submit what you have. Neither is a late
  assignment.

## What this page could not settle

1. **The frequency order is a judgment.** No offering of this course has been
   taught. Re-order after the first term from your own inbox.
2. **The hosted serving stack is not confirmed.** Everything above about
   reasoning blocks, the reasoning switch and error shapes was measured against
   the development stack recorded in `builder/docs/serving-stack-shape.md`, whose
   own open questions say the probe must be rerun against the production endpoint
   before the notebooks are final. If the production stack differs, failure mode 3
   is the entry that changes.
3. **The exact wording a student sees when a token budget is exhausted is not
   known**, because the budget mechanism sits in the hosting rather than in the
   labs. Failure mode 8 describes the shape of it, not the text.
4. **Late work and resubmission is unset**, so how a rerun after an outage or a
   top-up is dated is your call. State it in your first announcement.
5. **The two lab notebooks give different advice after an outage.** Week 2's
   closing cell tells the student to submit anyway; week 1's does not. Failure
   mode 9 works around it by asking you to say so in the week 1 announcement. The
   cleaner fix is for `builder/lab/notebooks/w1-lab.ipynb`, cell 15, to match
   `builder/lab/notebooks/w2-lab.ipynb`, cell 17, which this package does not
   own.
