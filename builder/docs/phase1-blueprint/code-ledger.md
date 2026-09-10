# Code ledger: what the notebook holds at the end of each week

Here is the promise students are given in week 1. Your work in the notebook
server is saved for the whole term, so nothing you write disappears. On top of
that, every week's starter notebook already contains a working version of
everything through the week before. You carry your own code forward wherever it
works. Where it does not, the starter notebook's version is right there and
runs.

A student who never finished week 4 can still open week 5 and build the loop. A
bad week costs you that week's points. It does not end the course. This ledger
is what keeps that promise true.

## 1. What this document is for

The course builds one phishing triage agent across weeks 1 to 7. Each week adds
exactly one capability. This ledger is the contract for that build. It names
every function and value in the notebook, says who writes it and in which week,
and names the file each week submits.

Three groups need it. The notebook author builds from it. The tools author
keeps `triage_tools.py` matching it. The grader knows from it what a correct
submission looks like without opening a student's notebook.

Terms used below. A *cell* is one block in a notebook that a student runs on
its own. A *TODO cell* is a cell with a comment marking the lines the student
writes. *Pre-written* means the cell arrives complete and working. A *signature*
is the function's name plus the values it takes and returns.

The *serving stack* is the software that runs the model and answers requests;
the course tested one of these and wrote down what it returned, in
`builder/docs/serving-stack-shape.md`. A *reasoning model* writes out its
thinking before its answer; that thinking is a *reasoning block*, and the course
strips it off. The *context window* is the most text the model can hold in one
request.

## 2. The parts that never change

### 2.1 The configuration cell

Every notebook, week 1 through week 7, opens with the same pre-written
configuration cell. Nothing in it is edited during a lab.

| Name | Value | Note |
|---|---|---|
| `BASE_URL` | the chat completions base address | One variable, no provider name in the code |
| `MODEL` | the model name | One variable |
| `MODEL_EXTRAS` | dictionary of extra request fields | Merged into every request |
| `API_KEY` | `os.environ.get("ITSY1377_API_KEY", "")` | Read from the environment, never typed, never printed |
| `EMAIL_DIR` | folder holding the `.eml` files | |
| `DATA_DIR` | folder holding the shipped data files | |
| `COURSE_DIR` | the folder the course files sit in | Found by looking upward from the notebook, so no path is typed |
| `TOOLS_DIR` | folder holding the shipped Python modules | Added to the import path, so `parse_eml` imports |
| `SPEC_DIR` | folder holding the shipped spec files | Set in week 2's schema cell, not in the configuration cell |

`MODEL_EXTRAS` exists because the two candidate models disagree about one
request field. The reasoning model accepts `reasoning_effort` and the other
model rejects it with an error. The dictionary holds `{"reasoning_effort":
"none"}` for the first and `{}` for the second, so one notebook runs against
either. This is recorded in the serving stack document.

`COURSE_DIR` is found rather than typed. The cell looks in the folder the
notebook is open in and then upward, and stops at the first folder holding the
mail files. `EMAIL_DIR`, `DATA_DIR` and `TOOLS_DIR` are built from it.
`SPEC_DIR` is the one path name that arrives later: week 2 sets it in the cell
that renders `OUTPUT_SCHEMA`, because no earlier week reads a spec file.

The cell prints one line saying whether a key was found. It never prints the
key, and no cell in any week does.

### 2.2 The token counter

Where it lives: in a pre-written cell in the notebook itself, directly below
the configuration cell, in every week. It is not hidden in an imported module.
Students can read it, and the number is on screen without anyone importing
anything.

How it works. Every reply from the model carries a `usage` block with three
numbers: tokens in the prompt, tokens in the answer, and the total. The
pre-written `send_request()` reads those three numbers straight from the reply
and adds them into two dictionaries.

- `USAGE` counts the whole notebook session. `show_tokens()` prints it.
  `reset_tokens()` sets it back to zero.
- `RUN_USAGE` counts one triage. `start_run()` sets it back to zero at the top
  of each email. Week 6 uses it for the per-run token cap. It exists from week
  1 so that `send_request()` is the same code in all seven notebooks.

Two rules the counter follows, both learned from the serving stack tests.

First, it reads the reported numbers and never measures the length of the
answer text. On the reasoning model the tokens spent thinking are counted in
the answer total but never appear in the text, so measuring the text would
under-report by roughly ten times.

Second, when a reply carries no `usage` block, the counter adds nothing and
prints "token count not reported" instead. A missing field is visible rather
than silent.

Every call prints one short line: the tokens for that call, and the running
total. `LAST_CALL` holds the stop reason, any reasoning text and the raw reply
from the most recent call, so a student can look at a failure without changing
any code.

### 2.3 The standing cell order

Every starter notebook uses the same order, so week 5 looks like week 2.

1. Markdown: the week, what you add, and the continuity note.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from earlier weeks. Weeks 2 to 7 only.
6. Markdown: what the new function has to do.
7. Code, TODO: the student writes it.
8. Code, pre-written: a check cell that runs the TODO cell on one known email
   and prints what a correct result looks like.
9. Steps 6 to 8 repeat where a week has two TODO cells.
10. Code, pre-written: the full run for the week.
11. Code, pre-written: the export cell.
12. Markdown: what to submit, naming the file and the screenshot.

Cell 5 carries a short markdown note above it: these are reference versions of
what you wrote before, and you may paste your own over them.

### 2.4 Two helpers that arrive in week 1 and never change

`send_request(payload)` is the only place in the course that talks to the
network. It adds the key header, sends the request, reads the reply, records
the tokens, and turns a rejected request into a sentence a student can act on.
It returns the whole reply as a dictionary.

`save_artifact(filename, content)` writes the submission file. Given a
dictionary it writes indented JSON. Given a string it writes text. Either way
it prints the full path and the first few lines, so the student sees exactly
what to attach.

### 2.5 One loader, from week 2 on

Week 1 reads a mail file with `parse_eml(email_path(email_id))`, because week 1
needs nothing else from it. Week 2 adds `load_email(email_id,
known_names=None)`, which makes that same call and then stamps the id into the
record it hands back. From week 2 on, every week loads an email that one way.

Two reasons it exists. The attempt log records one row per try against an email
id, so the record has to carry its own id. And week 3 has a list of names the
parser needs, so the loader takes `known_names` and passes it straight through.
Week 3 supplies it. Weeks 2, 4, 5, 6 and 7 leave it empty.

The signature was written to grow for the same reason the four in section 12
were. No later week reopens the cell that defines it.

## 3. Week 1: call the model from code

**Capability added.** Send text to the model from Python and read the answer
back. An agent is a loop around this call.

**Emails used.** 001 and 002.

**What the student writes.** One function, one short use of it.

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `ask_model(prompt, max_tokens=512, temperature=0.2)` | 8 to 10 | Builds the request dictionary, merges `MODEL_EXTRAS`, calls `send_request()`, returns the answer text |
| TODO 2 | no new function | 3 to 4 | Parses email 001, sends its body with a one-sentence instruction, prints the answer |

**Everything that exists at the end of week 1.** All of it is pre-written
except the last row.

| Name and signature | What it does | Source |
|---|---|---|
| `BASE_URL`, `MODEL`, `MODEL_EXTRAS`, `API_KEY`, `EMAIL_DIR`, `DATA_DIR` | Configuration, section 2.1 | pre-written |
| `USAGE`, `RUN_USAGE`, `LAST_CALL` | Token totals and the last reply, section 2.2 | pre-written |
| `record_usage(response)` | Adds one reply's token numbers into both counters | pre-written |
| `show_tokens()` | Prints the running totals in one line | pre-written |
| `reset_tokens()` | Sets the session counter back to zero | pre-written |
| `start_run()` | Sets the per-triage counter back to zero | pre-written |
| `send_request(payload)` | Sends one request, returns the reply dictionary | pre-written |
| `save_artifact(filename, content)` | Writes the submission file and prints its path | pre-written |
| `parse_eml(path, known_names=None)` | Reads one `.eml` file into a dictionary of facts | shipped module |
| `email_path(email_id)` | Turns "001" into the full path of that `.eml` file | pre-written |
| `show_email(parsed)` | Prints subject, sender and the first 400 characters of the body | pre-written |
| `ask_model(prompt, max_tokens=512, temperature=0.2)` | Sends one prompt, returns the answer text | **student, week 1** |

**Cells in the starter notebook.** Fifteen cells.

1. Markdown: the week, and the continuity promise in full.
2. Markdown: how a notebook talks to a model.
3. Code, pre-written: imports and configuration.
4. Code, pre-written: the token counter.
5. Code, pre-written: `send_request()` and `save_artifact()`.
6. Markdown: what `ask_model()` has to do.
7. **Code, TODO 1: `ask_model()`.**
8. Code, pre-written: check cell. Asks one plain question, prints the answer
   and the token line.
9. Code, pre-written: imports `parse_eml`, parses 001, prints it with
   `show_email()`.
10. **Code, TODO 2: send the body of 001 and print the answer.**
11. Code, pre-written: sends the same prompt three times at temperature 0.2 and
    three times at 1.0, prints all six answers together.
12. Code, pre-written: parses 002, sends it, prints the answer and the tokens,
    so the token count changes with the length of the mail.
13. Markdown: what to notice in what you just ran.
14. Code, pre-written: the export cell.
15. Markdown: what to submit.

**Submission artifact.** `week1_first_calls.txt`, written by the export cell in
step 14. Plain text, laid out with headings, holding the email ids, the exact
prompt used, the six repeated answers with their temperatures, the answer for
each email, and the token totals for the session.

**Model calls in a full run.** About nine.

## 4. Week 2: strict JSON, validated, with a retry

**Capability added.** The model answers in JSON with a fixed set of keys. Your
code checks the answer against a schema and asks again when it is wrong.

**Emails used.** 001, 002, 003 and 004.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `extract_json(text)` | 5 to 7 | Calls `strip_reasoning()`, tries `json.loads()`, returns the dictionary or `None` |
| TODO 2 | `classify_email(parsed, max_tries=3)` | 8 to 10 | Builds the prompt, calls `ask_model()`, extracts, checks with `schema_errors()`, logs the try, asks again with the problems attached, returns the checked dictionary or `None` |

A design note the program manager should see. The build prompt says students
validate against a schema. The mechanical walk of a schema is not a 5 to 15
line job, so `schema_errors()` arrives pre-written. The student wires it in and
decides what to do with what it returns, which is the part that teaches the
lesson. The retry loop is theirs.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `load_email(email_id, known_names=None)` | Reads one email by its id and stamps that id into the record. The one loader from this week on, section 2.5 |
| `OUTPUT_SCHEMA` | The required answer shape: verdict, category, confidence, indicators, with the allowed values |
| `schema_text(schema)` | Renders one schema as the lines the model is given |
| `CLASSIFY_INSTRUCTIONS` | The fixed instruction text naming the keys and the allowed values |
| `build_classify_prompt(parsed)` | Joins the instructions, the rendered schema and the email body into one prompt string |
| `strip_reasoning(text)` | Removes a leading reasoning block, a stray closing reasoning tag, and code fences |
| `schema_errors(data, schema)` | Returns a list of plain-language problems, empty when the answer is good |
| `ATTEMPT_LOG` | A list holding every try, good or bad |
| `log_attempt(email_id, try_number, raw_text, problems)` | Appends one try to `ATTEMPT_LOG` |

`OUTPUT_SCHEMA` is rendered from `corpus/spec/enums.json`, so the category list
the model is asked for is the same list week 7 scores against. `schema_text()`
is what turns that dictionary into the lines the prompt carries, and
`build_classify_prompt()` puts those lines between the instructions and the
body. The prompt therefore sends three parts, not two, and the week 2 spec's
token arithmetic counts all three.

`strip_reasoning()` is pre-written because the serving stack tests found three
places a reasoning block can appear and one model that produces none at all. It
handles all of them, so a change of server does not break a student's work.

**Everything that exists at the end of week 2.** Everything from week 1, plus
the nine pre-written items above, plus `extract_json()` and
`classify_email()`, which the student wrote this week.

**Cells in the starter notebook.** Sixteen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from week 1, including a reference
   `ask_model()`, and `load_email()`, which is new this week.
6. Code, pre-written: `SPEC_DIR`, `OUTPUT_SCHEMA`, `schema_text()`,
   `CLASSIFY_INSTRUCTIONS`, `build_classify_prompt()`.
7. Code, pre-written: one raw run showing what the model actually sends back,
   including a run that fails.
8. Markdown: why the answer needs cleaning before it can be read.
9. Code, pre-written: `strip_reasoning()`.
10. **Code, TODO 1: `extract_json()`.**
11. Code, pre-written: check cell. Feeds `extract_json()` four saved samples,
    one clean and three broken, and prints what each returns.
12. Code, pre-written: `schema_errors()`, `ATTEMPT_LOG`, `log_attempt()`.
13. **Code, TODO 2: `classify_email()`.**
14. Code, pre-written: runs all four emails and prints a small results table.
15. Code, pre-written: the export cell. It writes the per-email records,
    and it also re-runs the four saved samples from cell 11 and writes what
    the check reported on each.
16. Markdown: what to submit.

**Submission artifact.** `week2_classification.json`, written by the export
cell in step 15. Holds, per email: the id, the checked answer, `schema_ok`,
`problems`, and how many tries it took. `schema_ok` and `problems` are written
on the accepted try as well as on the failed ones, so an email that passed
first time still shows that the check ran. `problems` is an empty list when
the check found nothing wrong.

The file also holds the session token totals, the model name, and a
`sample_checks` block: the four saved replies from cell 11, one clean and
three broken, each with what `extract_json()` returned and what
`schema_errors()` reported. Three recorded failures are therefore in every
submitted file. The samples are saved text, so the block adds no model calls
to the counts below.

**Model calls in a full run.** Six to fourteen, depending on retries. Six is
typical. Two of the six are the raw run in cell 7, which calls the model twice
on purpose: once with room to answer, and once with almost none, so a student
sees a stop reason of `length` live. The other four are one clean try each on
the four emails.

## 5. Week 3: grounding

**Capability added.** Stop sending the raw body alone. Build a facts block from
the parsed headers, the authentication results, the display-name check, the
link hosts, a playbook snippet and the known-good internal domains, and send
that instead.

**Emails used.** 001, 004, 005, 006, 017 and 025. Emails 005 and 025 are the
matched pair: grounding has to correct one from malicious to benign and the
other from benign to malicious, on the same code and the same prompt.

Every email this week and in weeks 4 to 7 is read with `load_email()`, the
week 2 loader. Week 3 is the one week that hands it a second argument:
`load_email(email_id, known_names=KNOWN_NAMES)`.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `build_facts(parsed)` | 8 to 10 | Picks the facts worth sending out of the parsed email and returns them as one flat dictionary |
| TODO 2 | `format_facts(facts)` | 4 to 5 | Walks the shipped fact order and builds one labeled text block |

These two carry the primary evidence for course learning objective 1. `TODO 1`
is where a student decides which facts a sound judgment needs, which is the
week's data minimization lesson: what you put in the prompt is what you expose.
`TODO 2` is the exact construct the week 3 sidebar prepares.

The facts a correct `build_facts()` returns, all read straight from the parser's
own keys: `from_display`, `from_address`, `from_domain`, `reply_to`, `subject`,
the three results inside `auth`, `display_name_mismatch`, `url_hosts`, the
`external` and `scan_result` values inside `gateway`, and the filenames inside
`attachments`.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `load_json(path)` | Reads one shipped data file into a dictionary |
| `KNOWN_GOOD` | The organization's own domain and its internal hosts, from `known_good_domains.json` |
| `PLAYBOOK` | The eleven-rule playbook snippet, from `playbook.md` |
| `KNOWN_NAMES` | Names paired with the domain each belongs to, passed to `load_email()` so the display-name check can fire |
| `FACT_ORDER` | The fixed order the facts block prints, as a list of fact keys |
| `FACT_LABELS` | The label printed in front of each fact key |
| `build_grounded_prompt(facts_text, body)` | Joins the facts block, the playbook, the known-good list and the body into one prompt |
| `classify_grounded(parsed, max_tries=3)` | Week 2's retry, run against the grounded prompt |
| `compare_runs(email_ids)` | Runs both the ungrounded and the grounded path over a list of emails and returns one row per email |

**Everything that exists at the end of week 3.** Everything from weeks 1 and 2,
plus the nine pre-written items above, plus `build_facts()` and
`format_facts()`, which the student wrote this week.

**Cells in the starter notebook.** Sixteen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from weeks 1 and 2.
6. Code, pre-written: `load_json()`, `KNOWN_GOOD`, `PLAYBOOK`, `KNOWN_NAMES`,
   `FACT_ORDER`, `FACT_LABELS`.
7. Code, pre-written: parses 005 and prints every key the parser returns, so
   students see what they have to choose from.
8. Markdown: which facts a judgment needs, and which are exposure with no
   payoff.
9. **Code, TODO 1: `build_facts()`.**
10. Code, pre-written: check cell. Runs `build_facts()` on 005 and 025 and
    prints both dictionaries side by side.
11. **Code, TODO 2: `format_facts()`.**
12. Code, pre-written: check cell. Prints the finished facts block for 025 and
    counts its characters.
13. Code, pre-written: `build_grounded_prompt()`, `classify_grounded()`,
    `compare_runs()`.
14. Code, pre-written: runs all six emails both ways and prints the comparison
    table.
15. Code, pre-written: the export cell.
16. Markdown: what to submit.

**Submission artifact.** `week3_grounding.json`, written by the export cell in
step 15. Holds, per email: the id, the ungrounded verdict and confidence, the
grounded verdict and confidence, whether the verdict changed, and the exact
facts block that was sent. Plus the session token totals.

**Model calls in a full run.** About twelve, plus any retries.

## 6. Week 4: tools

**Capability added.** The model asks for one of three tools by name. Your code
runs it and hands the result back.

**Emails used.** 003, 008, 009, 017, 018 and 019. Each was chosen because one
tool alone changes its verdict.

**The three tools.** They ship in `lab/tools/triage_tools.py` and are imported,
never written by students. Each returns exactly the block recorded for that
email in the corpus manifest, so the answer key and the tool cannot disagree.

| Signature | What it returns |
|---|---|
| `check_sender_reputation(sender)` | The reputation record for one address or domain: `status`, `match_level`, `new_domain`, `first_seen`, `messages_90d`, `prior_reports`, `last_report_verdict`, `last_report_date`, `campaign_tag`, `notes`, and `domain` or `address` depending on which matched |
| `check_urls(hosts)` | One entry per host, each `allowlisted`, `blocklisted`, `internal` or `unlisted` |
| `lookup_recipient(address)` | The recipient record: `name`, `role`, `mailbox_type`, `executive`, `handles_payments`, `chronic_reporter`, `report_count_90d`, `true_positive_count_90d`, `campaign_tags` |

`status` is one of `internal`, `trusted`, `known_good`, `neutral`, `unknown` or
`known_bad`. `match_level` is one of `address`, `domain`,
`organizational_domain` or `none`, and it says which lookup succeeded. Two
records in the corpus match on an address and carry no `domain` key, so code
that reads the result must use a safe lookup rather than assume the key.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `run_tool(name, arguments, parsed)` | 8 to 10 | Chooses which of the three functions to run based on the name the model sent, takes the argument from `arguments` or from `parsed`, returns the result or a plain message for an unknown name |
| TODO 2 | `tool_result_message(tool_call, result)` | 3 to 4 | Builds the message that carries a tool result back to the model, with the call id copied across |

`run_tool()` is the exact construct week 4 sidebar 4b prepares: choosing which
function to run based on a name. Sidebar 4a prepares the function definition it
sits inside.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `TOOL_SPECS` | The three tool definitions in the format the model expects |
| `ask_with_tools(messages, tools=TOOL_SPECS, max_tokens=1024)` | Sends a message list with the tools attached, returns the reply text, the stop reason, the raw message and any tool calls |
| `start_messages(parsed, prompt_text)` | Builds the opening message list from a prompt string |
| `triage_with_tools(parsed)` | One full round: ask, run any tool the model asked for, send the result back, then check the final answer with week 2's schema check |

`triage_with_tools()` also carries the fallback path the build prompt requires.
The endpoint has no way to force a tool call. When the model answers in prose
instead of asking for a tool, the function falls back to week 2's manual
parsing and records that it did. That fallback fired in none of nine tests, but
nothing prevents it, so students see it as a normal path rather than a bug.

**Everything that exists at the end of week 4.** Everything from weeks 1 to 3,
plus the three imported tools, plus the four pre-written items above, plus
`run_tool()` and `tool_result_message()`, which the student wrote this week.

**Cells in the starter notebook.** Seventeen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from weeks 1 to 3.
6. Code, pre-written: imports the three tools and calls each one directly, so
   students see the results before any model is involved.
7. Code, pre-written: `TOOL_SPECS`, and a printed copy of one definition.
8. Code, pre-written: one raw call showing the tool request the model sends
   back, with its id and its arguments.
9. Markdown: why the arguments arrive as text and have to be read.
10. **Code, TODO 1: `run_tool()`.**
11. Code, pre-written: check cell. Runs `run_tool()` on three saved requests,
    one per tool, and prints each result.
12. **Code, TODO 2: `tool_result_message()`.**
13. Code, pre-written: `ask_with_tools()`, `start_messages()`,
    `triage_with_tools()`.
14. Code, pre-written: runs all six emails with tools and without. Prints one
    row per email with four columns, the email id, the tool asked for, the
    verdict without tools and the verdict with tools, then closes with the
    running token line. Those five printed items are what the week 4 screenshot
    is graded on.
15. Code, pre-written: a forced fallback run, so students see the prose path
    handled.
16. Code, pre-written: the export cell.
17. Markdown: what to submit.

**Submission artifact.** `week4_tool_calls.json`, written by the export cell in
step 16. Holds, per email: the id, the tool the model asked for, the arguments
it sent, the result your code returned, the verdict without tools, the verdict
with tools, and whether the fallback path ran. It also holds two call ids per
email: the one the model sent, and the one your tool result message carried
back. Plus the session token totals. The two call ids are how a grader reads
TODO 2 without opening the notebook.

**Model calls in a full run.** About eighteen.

## 7. Week 5: the bounded loop

**Capability added.** An observe, decide, act loop with a hard cap of four
steps and an explicit stop condition. The agent picks its next tool from what
it just learned.

**Emails used.** 004, 005, 007, 010, 011 and 012. Each produces a different
loop shape. Email 011 stops after one step because the sender is internal. 007
stops after one step because the sender is known bad. 005 and 010 stop after
two. 004 has no link at all, so a student sees the wrong second choice punished.
012 gets nothing decisive from any tool, so it runs all three and stops with
no tool left. The cap of four is the guard that catches a repeated tool call.

This is the hardest week in the course for students with no programming
background, and it carries the primary evidence for course learning objective
3. It therefore gets more pre-written scaffolding than any other week, and only
one TODO cell.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `run_loop(parsed, prompt_text, max_steps=MAX_STEPS, step_guard=None)` | 13 to 15 | Counts steps, asks the model, stops when it answers, runs the tool it asked for, checks for a decisive stop, asks the supplied guard whether the run may take another step, and stops when no tool is left or a cap is reached |

The loop uses only constructs week 0 covers: a counter, a `while`, an `if`, a
`return`. Every step inside it is one call to a pre-written helper, so the
student writes the shape of the loop and nothing else.

`step_guard` is the fourth parameter, and it is empty in week 5. It is the
growth hook that lets week 6 add a per-run token cap without reopening this
cell.

The student writes one `if` that calls `guard_says_stop(step_guard)` and stops
the run when it says so. In week 5 nothing is passed, the helper always answers
no, and the line never fires.

Week 6 passes `over_token_cap` in from `guarded_triage()`, and the same line
starts firing. The student's code is never edited.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `MAX_STEPS` | The hard cap, set to 4 |
| `LOOP_INSTRUCTIONS` | Text telling the model it may ask for one tool per step and must answer when it has enough |
| `loop_prompt(parsed)` | Joins `LOOP_INSTRUCTIONS` to week 3's grounded prompt for one email |
| `new_trace(parsed)` | Makes an empty record of the run: email id, usable tools, steps, stop reason, final answer, tokens |
| `first_call(calls, answer, trace)` | Picks the one tool call the loop acts on out of the list the endpoint returns, reads its arguments out of the JSON string, and covers the model answering with no tool at all |
| `append_turn(messages, turn, tool_call, result, trace)` | Adds the model's turn and the tool result to the message list, and writes the step into the trace |
| `decisive_stop(tool_name, result, parsed)` | Returns a stop reason when one tool result settles the case, otherwise `None` |
| `tools_left(trace)` | Names which of the three tools have not run yet and still have something to look at. `check_urls` is not left when the email has no link host |
| `guard_says_stop(step_guard)` | Answers whether a supplied guard says the run has spent its budget. Answers no when no guard was supplied |
| `out_of_room(trace)` | Names why a loop ended when nothing settled the case: `tools_exhausted` when no usable tool is left, `step_cap` when one is still unused |
| `show_trace(trace)` | Prints one run as a readable table, one row per step |

Two more helpers ship inside these cells and are never called from the TODO
cell: `usable_tools(parsed)`, which `new_trace()` calls once, and
`one_line(result)`, which `append_turn()` calls to shorten a tool result for
the trace table. Every one of these is written out in section 15 of
`docs/phase1-blueprint/week-05-spec.md`, which is the week 5 lab in full.

`decisive_stop()` is what makes the stop condition explicit rather than a
guess. It returns `internal_sender` when the mail never left the organization,
`decisive_malicious` when a link host is blocklisted or a sender is known bad,
and `decisive_benign` when an allowlisted sender and an allowlisted host agree.

The five stop reasons match the list the corpus scores against:
`decisive_malicious`, `decisive_benign`, `internal_sender`, `tools_exhausted`
and `step_cap`. There is no sixth value anywhere in the course.

`tools_left()` counts a tool as left only when it still has something to look
at. An email with no link host in it has nothing for `check_urls` to check, so
that tool is not left and the run ends one step earlier. Fifteen of the corpus
records stop on `tools_exhausted` after two tools for exactly this reason, and
the corpus figures every week quotes are counted that way.

**Everything that exists at the end of week 5.** Everything from weeks 1 to 4,
plus the eleven pre-written items above, plus `run_loop()`, which the student
wrote this week.

**Cells in the starter notebook.** Eighteen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from weeks 1 to 4.
6. Markdown: what a loop is here, drawn as four steps with a cap.
7. Code, pre-written: `MAX_STEPS`, `TOOL_NAMES`, `LOOP_INSTRUCTIONS`,
   `loop_prompt()`, `usable_tools()`, `new_trace()`.
8. Code, pre-written: one hand-written round of the loop, unrolled, with every
   variable printed, so students see one pass before writing many.
9. Code, pre-written: `one_line()`, `first_call()`, `append_turn()`,
   `decisive_stop()`, `tools_left()`, `guard_says_stop()`, `out_of_room()`,
   `show_trace()`.
10. Code, pre-written: each helper called once on its own, with its output
    printed.
11. Markdown: the loop in six numbered sentences, in the order the code runs.
12. **Code, TODO 1: `run_loop()`.**
13. Code, pre-written: check cell. Runs the loop on 011 alone, the shortest
    case, and prints the trace.
14. Code, pre-written: runs the loop on all six emails and prints all six
    traces.
15. Code, pre-written: a deliberately runaway version with the cap removed and
    a hard stop at twenty, printing the token cost of the difference.
16. Markdown: what the runaway run cost, and why the cap is not optional.
17. Code, pre-written: the export cell.
18. Markdown: what to submit.

**Submission artifact.** `week5_loop_trace.json`, written by the export cell in
step 17. Holds, per email: the id, the ordered steps with the tool name, the
arguments and a one-line result for each, the stop reason, the number of steps
used, the final verdict, and the tokens that email spent. Plus the session
token totals and the runaway run's token count for comparison.

**Model calls in a full run.** About eighteen to thirty, plus the runaway
demonstration.

## 8. Week 6: guardrails and human review

**Capability added.** Stop trusting the text the agent reads and the answer it
produces. The fenced prompt, the fact check, the confidence floor and the token
cap are four parts of that one control, not four capabilities. The week 6 spec
argues the point in full.

The whole email body is text an attacker wrote. Prompt injection is therefore
this agent's real threat, and this is the course's differentiator week.

**Emails used.** Eleven. 013 carries the required body injection and 024 is its
word-for-word twin without the payload, so a student measures what the
injection changed on their own model. 014 hides the payload in the HTML part.
020 fakes the agent's own tool output. 021 imitates the mail gateway's banner.
022 puts the payload in the subject and the display name. 023 forges gateway
headers. 015 is a benign decoy holding instruction-shaped text inside a quote,
which a keyword detector gets wrong. 016 is the case where the model says
benign and an extracted fact says otherwise. 009 and 012 are the low-confidence
cases the escalation threshold has to catch.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `build_guarded_prompt(grounding, body)` | 6 to 8 | Wraps the body between the two markers, puts the rules and week 3's grounding before it and the required answer keys after it |
| TODO 2 | `check_against_facts(result, facts)` | 6 to 8 | Returns a list of problems where the answer contradicts the extracted facts, empty when it does not |

`check_against_facts()` is the exact construct the week 6 sidebar prepares:
comparing two values and checking one against known facts. A correct version
catches at least three contradictions: a benign verdict while a link host is
blocklisted, a benign verdict while the sender is known bad, and an indicator
naming a host that is not in the extracted list.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `BODY_START`, `BODY_END` | The two markers that fence off the attacker's text |
| `GUARD_RULES` | The sentences telling the model the fenced block is evidence to judge, never an instruction to follow |
| `CONFIDENCE_FLOOR` | The threshold below which a case goes to a human, set to 0.7 |
| `TOKEN_CAP_PER_RUN` | The most tokens one triage may spend, set to 4000 |
| `over_token_cap()` | Returns true when `RUN_USAGE` has passed the cap |
| `guarded_triage(parsed, schema=OUTPUT_SCHEMA)` | One full guarded triage: build facts, build the guarded prompt, run the week 5 loop with `over_token_cap` as its step guard, make one closing model call for the schema answer whatever stopped the loop, apply the fact check, the confidence floor and the token cap, return a verdict with an escalation decision |
| `compare_guarded(email_ids)` | Runs the guarded and unguarded paths over a list of emails and returns one row per email |

`guarded_triage()` returns whatever keys the schema it was handed names, plus
`escalate`, `escalate_reason`, `problems`, `stop_reason` and `tokens`. Called
with the default `OUTPUT_SCHEMA` it returns `verdict`, `confidence`,
`indicators` and those five. Week 7 hands it `OUTPUT_SCHEMA_V2` and gets
`recommended_action` and `summary` in the same dictionary, without editing this
function or any week 6 cell.

`escalate_reason` is one of five plain values: `low_confidence`,
`fact_contradiction`, `injection_detected`, `token_cap` or `none`.

**Two escalation vocabularies, kept apart on purpose.** These five are the
agent's own reasons, and they are deliberately not the ten ground-truth
escalation reasons the corpus records in `corpus/spec/enums.json`. The corpus
reasons say why a human analyst would escalate. The agent's reasons say which
of its own controls fired. Only `injection_detected` appears in both lists.
Week 7 therefore scores escalation agreement on the yes-or-no flag alone and
never compares the two reason strings.

The per-run cap uses the counter from section 2.2. `start_run()` zeroes
`RUN_USAGE` at the top of each triage. `guarded_triage()` then passes
`over_token_cap` into `run_loop()` as its `step_guard`, so the check runs
between steps without any week 5 cell being reopened. The student's loop calls
`guard_says_stop(step_guard)`, which it has called since week 5.

A run that hits the cap records the stop reason `step_cap` and escalates with
`escalate_reason` set to `token_cap`. `step_cap` is the corpus value for a run
a cap ended rather than a decision, and `escalate_reason` says which cap fired.

No new stop reason is invented. A week 6 export file and every week 7 batch row
therefore carry only values the corpus, the week 5 rubric and the week 5
self-check already treat as valid.

This is a cap on one triage inside the lab. It is not the course token budget,
which the instructor controls and which never cuts a student off.

**Everything that exists at the end of week 6.** Everything from weeks 1 to 5,
plus the seven pre-written items above, plus `build_guarded_prompt()` and
`check_against_facts()`, which the student wrote this week.

**Cells in the starter notebook.** Nineteen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from weeks 1 to 5.
6. Code, pre-written: runs the week 5 agent on 013 with no defenses, and prints
   the verdict the injection produced.
7. Code, pre-written: runs the same agent on 024, the twin without the payload,
   and prints both verdicts together.
8. Markdown: what just happened, in plain language.
9. Code, pre-written: `BODY_START`, `BODY_END`, `GUARD_RULES`.
10. **Code, TODO 1: `build_guarded_prompt()`.**
11. Code, pre-written: check cell. Prints the guarded prompt for 013 and reruns
    the agent on 013 and 024 with it.
12. Code, pre-written: runs the guarded agent on 014, 020, 021, 022 and 023,
    the five other payload placements, and prints where it still fails.
13. Markdown: why a better prompt is not enough on its own.
14. **Code, TODO 2: `check_against_facts()`.**
15. Code, pre-written: `CONFIDENCE_FLOOR`, `TOKEN_CAP_PER_RUN`,
    `over_token_cap()`, `guarded_triage()`, `compare_guarded()`.
16. Code, pre-written: runs all eleven emails both ways and prints the
    comparison table, including 015, the decoy that must not escalate.
17. Code, pre-written: a run with `TOKEN_CAP_PER_RUN` lowered, so students see
    the cap fire.
18. Code, pre-written: the export cell.
19. Markdown: what to submit.

**Submission artifact.** `week6_guardrails.json`, written by the export cell in
step 18. Holds, per email: the id, the verdict without guardrails, the verdict
with guardrails, whether the injection changed the answer, the payload
placement, the problems the fact check found, the escalation decision and its
reason, the stop reason, and the tokens that run spent. Plus the session token
totals and the two threshold values used.

Five of the eleven emails carry no injection: 009, 012, 015, 016 and 024. For
those the export writes `payload_placement` as the string `none`, exactly the
way `escalate_reason` already carries `none`. The key is present on every row,
so a grader reads a value rather than a missing field, and a correct file shows
six placements and five nones.

The export also writes one `guard_fence_check` block for email 013, read from
the prompt the student's `build_guarded_prompt()` returned. It holds four
numbers: `body_start_index`, `body_end_index`, `fenced_body_chars` and
`email_body_chars`. An index of -1 means that marker was not found in the
prompt. The block copies no body text, so no attacker text reaches the artifact.
It is what lets a grader see that the body was fenced without opening the
notebook.

**Model calls in a full run.** About ninety-nine. The count is built from the
corpus, one line per cell that calls the model.

| Cell | Runs | Calls |
|---|---|---|
| 6 and 7, the undefended pass on 013 and 024 | 2 | 6 |
| 11, the guarded check on 013 and 024 | 2 | 8 |
| 12, the guarded run on the five other placements | 5 | 18 |
| 16, all eleven emails both ways | 22 | 65 |
| 17, the lowered cap demonstration | 1 | 2 |
| **Total** | **32** | **99** |

Two rules produce those figures. An undefended run makes one call per tool the
model asks for. A guarded run makes the same calls plus one closing call, which
`guarded_triage()` makes whatever stopped the loop. Tool counts per email come
from the corpus manifest, and they add to 27 across the eleven emails.

An earlier draft of this ledger recorded about forty-four calls. That figure
counted cell 16 alone and left the closing call out. Ninety-nine is the whole
notebook with the closing call in it, and the week 6 spec's token arithmetic is
rebuilt on it.

## 9. Week 7: the triage note and the batch

**Capability added.** Write the verdict as a fixed six-line note another analyst
can act on. The batch run and the scoring are the same note applied twenty times
and then measured, not new capabilities. The week 7 spec argues the point in
full.

This week carries the primary evidence for course learning objectives 5 and 6.

**Emails used.** The twenty batch emails, 026 to 045. Ten are malicious and ten
are benign. None appears in any earlier week.

**What the student writes.**

| Cell | Signature | Lines | What it does |
|---|---|---|---|
| TODO 1 | `write_note(result, facts)` | 5 to 7 | Returns the six-line note as one triple-quoted f-string built from one triage result, joining the indicator list into one line |
| TODO 2 | `score_batch(rows, truth)` | 8 to 10 | Loops over the results, counts correct calls, false positives and false negatives, and returns the counts with the accuracy rate |

`score_batch()` is the exact construct the two week 7 sidebars prepare between
them: looping over a list and counting one bucket in 7A, counting a second
bucket and dividing for a rate in 7B. The two-sentence plain-language
summary for the person who reported the email is produced by the model as a
`summary` key, so `write_note()` places it rather than writing it.

**The note format.** Six labeled lines, fixed, in this order: verdict,
confidence, indicators, recommended action, escalate yes or no, and the
two-sentence summary. The line order ships as `NOTE_TEMPLATE`.

**How the note is built. Settled here.** `write_note()` returns one
triple-quoted f-string that the student writes. It does not call
`NOTE_TEMPLATE.format()`. `str.format()` is taught nowhere in this course, and
adding it would widen week 0 for one cell. Week 0 section 5 teaches the
triple-quoted f-string, so that is the only mechanism the student has been given
and it is the one week 7 uses. `NOTE_TEMPLATE` is a reference the student reads
beside their own f-string, printed once in cell 6. It is not a string they fill.

**What arrives pre-written this week.**

| Name and signature | What it does |
|---|---|
| `OUTPUT_SCHEMA_V2` | Week 2's schema with three keys added: `recommended_action`, `escalate` and `summary` |
| `NOTE_TEMPLATE` | The fixed six-line note format, printed as a reference. It fixes the line order and the labels. It is not filled by code. |
| `BATCH_DIR` | The folder holding the twenty batch emails |
| `GROUND_TRUTH` | The answer key, loaded from `ground_truth_batch.json` |
| `list_batch_emails()` | Returns the twenty file paths in order |
| `run_batch(paths)` | Runs `guarded_triage(parsed, schema=OUTPUT_SCHEMA_V2)` over every path, keeps going when one email fails, returns one row per email |
| `report_scores(counts, rows, truth)` | Turns the counts into a printed report with accuracy, false positives and false negatives kept apart, and escalation agreement on its own line |

`run_batch()` sends one request per email and never puts the corpus in one
prompt. The served context window is 32,768 tokens, which is ample for one
email and far too small for twenty.

Every email ends with one closing model call, whatever stopped its loop, so
every note carries a confidence, an indicator list, a recommended action and a
summary. `guarded_triage()` makes that call even when a decisive tool result
already settled the verdict.

The last two of those four keys exist because `run_batch()` hands
`OUTPUT_SCHEMA_V2` to `guarded_triage()`, which returns whatever keys the
schema it was given names. No week 6 cell is edited to get them. `report_scores()` prints escalation agreement on its own
line inside the score report, so one screenshot of that cell holds every number
the rubric asks for.

**Everything that exists at the end of week 7.** Everything from weeks 1 to 6,
plus the seven pre-written items above, plus `write_note()` and
`score_batch()`, which the student wrote this week. That is the finished agent.

**Cells in the starter notebook.** Seventeen cells.

1. Markdown: the week, and a one-line continuity reminder.
2. Code, pre-written: imports and configuration.
3. Code, pre-written: the token counter.
4. Code, pre-written: `send_request()` and `save_artifact()`.
5. Code, pre-written: working code from weeks 1 to 6.
6. Code, pre-written: `OUTPUT_SCHEMA_V2` and `NOTE_TEMPLATE`, with one finished
   example note printed. The example is what the student's f-string has to
   match, line for line.
7. Markdown: who reads a triage note, and what each line is for.
8. **Code, TODO 1: `write_note()`.**
9. Code, pre-written: check cell. Runs one email end to end and prints its note.
10. Code, pre-written: `BATCH_DIR`, `GROUND_TRUTH`, `list_batch_emails()`,
    `run_batch()`.
11. Code, pre-written: runs the batch. Prints a progress line per email and the
    running token total.
12. Markdown: what a false positive and a false negative cost a real analyst.
13. **Code, TODO 2: `score_batch()`.**
14. Code, pre-written: `report_scores()`, and the printed report. Accuracy,
    false positives, false negatives and escalation agreement each print on
    their own line.
15. Code, pre-written: prints every email the agent got wrong, with the answer
    key beside it.
16. Code, pre-written: the export cell.
17. Markdown: what to submit.

**Submission artifact.** `week7_triage_report.txt`, written by the export cell
in step 16. Plain text in two headed sections. The first holds the twenty
triage notes in the fixed format, in order. The second holds the score block:
the counts, the accuracy rate, false positives and false negatives on separate
lines, escalation agreement on its own line, the label version of the answer
key that was scored against, and the session token totals.

Text rather than JSON, for one reason. The rubric for course learning objective
5 asks whether another analyst could act on the note. A grader has to read the
note the way an analyst would, and a text file lets them.

**Model calls in a full run.** About sixty-five: forty-five tool requests
across the twenty emails, plus one closing call for each email.

## 10. Submission artifacts at a glance

Every artifact is written by a single pre-written export cell. Students attach
one file, one screenshot and three to five sentences. No zip files, no
folders, no links.

| Week | File name | Format | What the grader reads in it |
|---|---|---|---|
| 1 | `week1_first_calls.txt` | text | Six repeated answers with their temperatures, and the token totals |
| 2 | `week2_classification.json` | JSON | The checked answer for four emails, `schema_ok` and `problems` on every try, tries used, plus the four saved sample checks |
| 3 | `week3_grounding.json` | JSON | Ungrounded and grounded verdicts for six emails, and the facts block sent |
| 4 | `week4_tool_calls.json` | JSON | The tool asked for, the result returned, and the verdict before and after |
| 5 | `week5_loop_trace.json` | JSON | The ordered steps, the stop reason and the step count for six emails |
| 6 | `week6_guardrails.json` | JSON | Verdicts with and without guardrails, fact-check problems, escalation reasons, payload placement or none, and the fence record for email 013 |
| 7 | `week7_triage_report.txt` | text | Twenty notes in the fixed format, then accuracy with the two error types apart |

## 11. Student line counts

The build prompt sets a target of 5 to 15 written lines per lab. Blank lines
and comments are not counted.

| Week | TODO cells | Lines | Notes |
|---|---|---|---|
| 1 | 2 | 11 to 14 | One function, one short use of it |
| 2 | 2 | 13 to 17 | The retry loop is the larger half |
| 3 | 2 | 12 to 15 | Both cells are short, and both are course learning objective 1 |
| 4 | 2 | 11 to 14 | The dispatch, plus a four-line message builder |
| 5 | 1 | 13 to 15 | One cell only, by design; every step inside it is a helper call |
| 6 | 2 | 12 to 16 | Two small cells, both prepared by the sidebar |
| 7 | 2 | 13 to 17 | One template fill, one counting loop |

Weeks 2 and 7 can reach 17 lines when a student writes each condition on its
own line, which is the style week 0 teaches. Week 6 reaches 16 the same way,
which is what its own spec recommends accepting. The rubrics never reward
shorter code, and the check cells accept both styles.

## 12. What this ledger commits other builders to

- `lab/tools/triage_tools.py` must expose exactly `check_sender_reputation`,
  `check_urls` and `lookup_recipient` with the signatures in section 6, must
  return exactly the `tool_expectations` block recorded for that email, and
  must need nothing installed.
- Every function name and signature here is fixed. Weeks 2 to 7 carry earlier
  weeks as pre-written cells, so a name change breaks six notebooks.
- One loader, not two. Week 2 defines `load_email()` and weeks 3 to 7 call it.
  No week after week 1 writes `parse_eml(email_path(...))` again.
- Five signatures were designed to grow, so that no later week edits an earlier
  week's cell. `load_email(email_id, known_names=None)` takes the name list
  week 3 needs, so week 3 passes it and no other week has to.
  `start_messages(parsed, prompt_text)` and
  `run_loop(parsed, prompt_text, max_steps, step_guard)` both take the prompt as
  an argument, and week 6 swaps in the guarded prompt without touching week 5's
  code. `run_loop()` also takes an optional step guard, which is empty in week 5
  and is `over_token_cap` in week 6, so the per-run token cap is checked between
  steps without the student reopening the loop cell. `guarded_triage(parsed,
  schema=OUTPUT_SCHEMA)` takes the answer schema, so week 7 passes
  `OUTPUT_SCHEMA_V2` and gets `recommended_action` and `summary` back without
  touching week 6's code.
- `OUTPUT_SCHEMA` and `OUTPUT_SCHEMA_V2` are rendered from
  `corpus/spec/enums.json`. A checked-in schema that differs from a fresh
  render fails the build.
- The week 8 exam draws its scenario stems from these artifacts. A stem may
  quote a loop trace, a facts block or a triage note, because every student has
  produced one.
