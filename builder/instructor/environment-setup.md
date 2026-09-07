# Environment setup

ITSY 1377, Agentic AI and Security Operations. Northeast Lakeview College,
Cyber Defense program. Not student-facing.

This is the operational document. It says what the hosting has to provide, how
the API key reaches a notebook, which model answers and how, which files have to
be on disk, how the token budget works, and how to prove all of it before the
term opens.

Run the checklist in section 6 in a test student account before day one. If it
fails, nothing else in the course works.

---

## 1. What the hosting has to provide

Students have a computer, an internet connection and a browser, and nothing
else. That is stated in the build brief (`../docs/build-prompt-v1.3.md`, section
"Student technical environment") and repeated to students on the page "Your
computer and the notebook server".

| Requirement | Detail |
|---|---|
| Notebook server | One hosted Jupyter notebook instance per student, opened from Canvas in a browser |
| Persistence | Every student's work saved for the whole term, across sign-outs and across weeks |
| Python | 3.11 or newer. The development machine that produced the reference measurements ran 3.13.9 (`../docs/serving-stack-shape.md`, section 1) |
| Packages | The Python standard library, plus `requests`. Nothing else |
| Installs | None. No `pip`, no Docker, no command line, no admin rights (`../docs/build-prompt-v1.3.md`) |
| Downloads | A student must be able to download a file the notebook wrote, from the notebook server, through the browser |

**Why `requests` and nothing else.** Every network call in the course goes
through one pre-written function, `send_request()`, and that function uses
`requests` (`../lab/notebooks/w1-lab.ipynb`, configuration and helper cells).
Everything else the course imports is standard library: `json`, `os`, `sys`,
`pathlib` and `traceback` in the notebooks, `email`, `html`, `re` and `sys` in
`corpus/tools/parse_eml.py`, and `json`, `os` and `datetime` in
`lab/tools/triage_tools.py`.

**Persistence is a promise the course makes in writing.** Week 1 tells students
that their work is saved for the term, and the code ledger is built on it
(`../docs/phase1-blueprint/code-ledger.md`, opening section). A server that
resets between sessions breaks that promise on the page where it is made.

Week 0 and the seven sidebar notebooks make no model calls and need no key
(`../docs/phase1-blueprint/assumptions-and-gaps.md`, A21). They need only Python
and the notebook server. That makes them a useful first test.

---

## 2. The API key

### 2.1 How it works

The key is injected into each student's notebook environment as an environment
variable by the hosting setup. The notebook reads it with `os.environ`. Students
never type, paste, see or screenshot a key.

**The variable the notebooks read is `ITSY1377_API_KEY`.**

The configuration cell at the top of every lab notebook holds this line, and it
is the same line in `w1-lab.ipynb` and `w2-lab.ipynb`:

```python
API_KEY = os.environ.get("ITSY1377_API_KEY", "")
```

Two rules follow from that, and both are already true in the shipped notebooks.

1. The cell reports only whether a key was found. It prints `found` or
   `NOT FOUND`. It never prints the value.
2. `send_request()` adds the header `Authorization: Bearer <key>` only when
   `API_KEY` is not empty. Nothing else in the course reads the variable
   (`../docs/phase1-blueprint/code-ledger.md`, section 2.1).

The value must therefore be a bearer token the model endpoint accepts. If the
endpoint needs no key, leave the variable unset and the notebook sends no
authorization header.

### 2.2 What a student sees when the key is missing

The configuration cell prints this, exactly:

```
API key:     NOT FOUND

No API key was found in this notebook's environment.
Close this notebook, open it again, and run this cell.
If it still says NOT FOUND, email your instructor.
```

The advice to close and reopen is not filler. An environment variable is read
when the kernel starts. A variable that the hosting sets after a student's
kernel is already running is invisible to that kernel until it restarts. So the
first fix is always a restart, and the second is you.

Later, if a call is refused, `send_request()` prints the status the service
returned and then three things to check, the first of which is to run the
configuration cell again. Students are told the same thing on the "Getting help"
page: restart the notebook, run the first cell, then email the instructor, and
never type or paste a key.

### 2.3 Rules that do not bend

- No cell in any week displays a key, and no submission instruction asks for a
  screenshot of one (`../docs/build-prompt-v1.3.md`; `code-ledger.md` 2.1).
  Every lab submits a screenshot, so a cell that printed a key would put key
  material into the gradebook.
- Do not write the key into a file inside a student's persisted work folder. It
  survives the term there and it travels with any export of that folder.
- Do not put the key in a notebook, a shared drive, an email, or a Canvas page
  that is not restricted.
- If key material ever appears on a screen, treat the key as spent. Rotate it
  and tell the student to post it nowhere. That is the instruction students
  already have.

### 2.4 The fallback, and why it is worse

The build brief allows one fallback. If the hosting cannot inject one
environment variable per student, the course uses a single course key published
on a Canvas page only students can open
(`../docs/build-prompt-v1.3.md`, "Student technical environment";
`../docs/phase1-blueprint/assumptions-and-gaps.md`, A17).

Use it only if per-student injection is genuinely unavailable. It is worse in
five ways, and they compound.

1. **One key for everyone, so usage cannot be attributed.** The token budget in
   section 5 is per student. With one shared key, central accounting cannot tell
   whose spend is whose. The in-notebook counter still shows a student their own
   session, but the budget stops being enforceable and the top-up conversation
   stops being evidence-based.
2. **Revocation is all or nothing.** One leaked key ends the course for every
   student until a new key is issued and the page is edited.
3. **It puts key material on a screen.** The course tells students that no page,
   cell or screenshot ever shows a key, and that they should report it if one
   appears. The fallback makes that statement false and trains students to
   handle a secret by hand.
4. **It needs a cell that takes a pasted value.** Every lab submits a screenshot
   of notebook output. A pasted key sits one scroll above that output.
5. **A restricted Canvas page is a permission, not a secret store.** Anyone with
   a student role reads it, and it persists in course copies and exports.

If the fallback is unavoidable: publish the page to students only, say plainly
in the syllabus that this term uses a shared key, tell students the paste cell
is never part of a screenshot, check the first week's screenshots yourself, and
rotate the key at the end of the term.

---

## 3. The model endpoint

### 3.1 The three variables

| Variable | What it sets | Notebook fallback when unset |
|---|---|---|
| `ITSY1377_BASE_URL` | The OpenAI-compatible chat completions base address | `http://localhost:11434/v1` |
| `ITSY1377_MODEL` | The model name | `granite4.2:3b` |
| `ITSY1377_API_KEY` | The bearer token, see section 2 | empty |

The fallbacks after the comma exist for a local run on a development machine.
The hosting sets all three.

`send_request()` builds its address as `BASE_URL` with any trailing slash
removed, plus `/chat/completions` (`../lab/notebooks/w1-lab.ipynb`). So
`ITSY1377_BASE_URL` must stop at the `/v1` level. Do not include
`/chat/completions` in it.

### 3.2 Which model

**Standardise on `granite4.2:3b` with reasoning switched off.** That is the
measured recommendation in `../docs/week5-model-test.md`, taken from 294
complete agent runs across both candidate models and four lab designs. In the
design the course ships, that configuration produced the exact expected tool
path 29 times out of 30, the correct stop reason 30 out of 30, and the correct
verdict 28 out of 30, at 3,813 tokens and 4.1 seconds per triage.

**`granite4.1:3b` is the documented fallback**, with one caveat. In the same
design it ends the run for the right reason every time, but it chooses a
different tool order. The week 5 rubric grades the stop reason and the trace
rather than the order, which is what makes either model safe to teach on
(`../docs/week5-model-test.md`).

### 3.3 The reasoning setting, and why it is not gated by model name

Set `reasoning_effort` to `none`. The configuration cell does it on every
request, for every model:

```python
MODEL_EXTRAS = {}
if os.environ.get("ITSY1377_REASONING", "off").strip().lower() != "on":
    MODEL_EXTRAS = {"reasoning_effort": "none"}
```

**An earlier version of this page described a gate that read the model's name
and sent the field only to Granite 4.2. That gate is gone, and the reason it is
gone matters to you.** It was built on the belief that Granite 4.1 rejects the
field. It does not. It rejects only the levels it cannot do.

Measured against the serving stack on 4 September 2026, one request per cell:

| Model | `reasoning_effort` | Result |
|---|---|---|
| Granite 4.1 3B | `none` | HTTP 200, answer returned, no reasoning text |
| Granite 4.1 3B | `low` | HTTP 400, `"granite4.1:3b" does not support thinking` |
| Granite 4.2 3B | `none` | HTTP 200, answer returned, no reasoning text |
| Granite 4.2 3B | `low` | HTTP 200, answer returned, 46 characters of reasoning |

So `none` is safe on both, and only `low`, `medium` and `high` are refused by
4.1. The field is therefore sent every time rather than guessed from a name.

**Why the gate was worse than useless.** It matched the text `granite4.2` in
the model name. A hosted alias such as `course-model` or `ibm/granite-4-2-3b`
does not match, so the field would never be sent and reasoning would stay on,
silently, for the whole term. The failure was invisible: every notebook still
ran, every answer still came back, and every lab cost about twice the tokens
and twenty times the wall clock. A configuration that depends on how you spell
a model name is a configuration that breaks when someone renames it.

**One consequence for you, and it is now the only one.** You may name the model
whatever you like in `ITSY1377_MODEL`. Nothing in the course reads that string
for meaning.

**If a future model rejects `reasoning_effort` outright**, set
`ITSY1377_REASONING` to `on` in the student environment. The field is then left
out and the model runs in whatever mode it defaults to. Read the next paragraph
before you do.

**Reasoning left on is not a small tax.** At the 512-token answer budget the
labs use, Granite 4.2 in its default reasoning mode spent the whole budget
thinking and returned empty content 18 times out of 18. Re-tested at 4,096
tokens it works, and across 36 runs it averaged 7,874 tokens and 83 seconds for
a single triage, against 3,813 tokens and 4.1 seconds with reasoning off
(`../docs/week5-model-test.md`). A student waiting a minute and a half per
email assumes the notebook has hung.

### 3.4 The response shape the notebooks are written against

The reference stack is Ollama 0.32.15, OpenAI-compatible endpoint at
`http://localhost:11434/v1/chat/completions`
(`../docs/serving-stack-shape.md`, section 1). On that stack, reasoning arrives
in a separate `message.reasoning` field and never as inline `<think>` tags in
the content. The notebooks tolerate both: `send_request()` reads `reasoning` or
`reasoning_content`, and also strips a `</think>` block out of the content if
one is there.

Two more facts from the same probe. That Ollama install ran both models with a
32,768-token context window, not the 131,072-token model maximum
(`../docs/serving-stack-shape.md`, section 1.1). And `send_request()` waits 120
seconds for one answer before it gives up (`REQUEST_TIMEOUT` in
`../lab/notebooks/w1-lab.ipynb`).

If the hosted stack is not Ollama, re-run the probe before the term. Weeks 2 and
4 are written against the response shape recorded in that document, and the
parsing follows it.

---

## 4. The corpus and data files

### 4.1 What has to be present

Every student environment needs a folder containing `corpus/`. Contents, from
`../corpus/README.md`:

| Path | What it is | Needed from |
|---|---|---|
| `corpus/emails/teaching/` | The `.eml` files weeks 1 to 6 read | Week 1 |
| `corpus/emails/batch/` | The `.eml` files the week 7 batch reads | Week 7 |
| `corpus/data/` | Ten JSON data files plus `playbook.md` | Week 3 |
| `corpus/tools/parse_eml.py` | The pre-written email reader week 1 imports | Week 1 |
| `corpus/spec/` | `corpus-spec.json`, `enums.json`, `categories.json`, `ground_truth.schema.json` | Week 2 |
| `lab/tools/triage_tools.py` | The three deterministic tools | Week 4 |

Thirteen teaching emails are rendered today: 001 through 007, 010 through 013,
019 and 021. One batch email is rendered, 032. Weeks 1 and 2 need 001, 002, 003
and 004, and all four exist (`../lab/notebooks/w1-lab.ipynb`,
`../lab/notebooks/w2-lab.ipynb`). The remaining emails arrive with weeks 3 to 8.

Every file is plain seven-bit text with no attachment parts, no base64, no
scripts and no images. Every domain ends in `.example` and never resolves
(`../corpus/README.md`, safety statement). Students open them in the notebook or
a text editor, never in a mail client.

The ground truth files are not all student-facing. The teaching answer key and
the exam key stay in the instructor package. The batch key is released with the
week 7 page (`../corpus/README.md`).

### 4.2 How a notebook finds them

The configuration cell searches, and takes the first folder that contains
`corpus/emails/teaching` (`../lab/notebooks/w1-lab.ipynb`):

1. The path in `ITSY1377_COURSE_DIR`, if that variable is set.
2. The folder the notebook is open in.
3. Each parent of that folder, in turn.

From the folder it finds, it sets `EMAIL_DIR` to `corpus/emails/teaching`,
`DATA_DIR` to `corpus/data`, and `TOOLS_DIR` to `corpus/tools`, and it puts
`TOOLS_DIR` on `sys.path` so `from parse_eml import parse_eml` works. The cell
then prints `Email files: found` and the path, or `NOT FOUND` and the path it
looked for.

**Simplest layout that works with no extra variables.** Put `corpus/` at the top
of each student's persisted work folder, and put the week's notebook beside it
or one level below it. Then set `ITSY1377_COURSE_DIR` anyway, so a student who
opens a notebook from an unexpected folder still gets a working path.

**`triage_tools.py` finds its data separately**, from week 4 onward. It reads
`TRIAGE_DATA_DIR` if that variable is set, and otherwise searches five relative
places for `sender_reputation.json` (`../lab/tools/triage_tools.py`). Set
`TRIAGE_DATA_DIR` to the absolute path of `corpus/data` and the search never
runs. If nothing is found the tool raises `FileNotFoundError` and lists every
folder it looked in.

**One thing to settle before week 4.** The notebooks put `corpus/tools` on
`sys.path`, and `triage_tools.py` ships in `lab/tools/`
(`../docs/phase1-blueprint/code-ledger.md`, section 12). Either the file moves
next to `parse_eml.py`, or the deployed layout adds `lab/tools` to the path.
Weeks 1 and 2 are unaffected because they import only `parse_eml`.

### 4.3 Where submissions land

`save_artifact()` writes the submission file into the folder the notebook is
open in, then prints the full path and the first lines of the file
(`../lab/notebooks/w1-lab.ipynb`). Week 1 writes `week1_first_calls.txt` and
week 2 writes `week2_classification.json`
(`../docs/phase1-blueprint/code-ledger.md`, section 10). A student has to be
able to find that file in the server's file browser and download it. Test that.

---

## 5. The token budget

### 5.1 Controlled centrally, visible locally

The instructor and the program own the budget. There are no hard cutoffs in the
labs, by design (`../docs/build-prompt-v1.3.md`, "Student technical
environment"). Enforcement, if any, belongs to whatever issues the keys, not to
the notebooks.

A student sees their own usage in the notebook. A pre-written token counter sits
directly below the configuration cell in every week's notebook
(`../docs/phase1-blueprint/code-ledger.md`, section 2.2). Every call prints one
line with that call's tokens and the running session total. `show_tokens()`
prints the totals on demand, in this form:

```
Tokens this session: 0 total, 0 sent, 0 answered, over 0 calls.
```

Two behaviours of that counter matter when you read a student's numbers. It
reads the reported `usage` block from the reply and never measures the length of
the answer text, because a reasoning model spends tokens that never appear in
the text. And when a reply carries no `usage` block it adds nothing and prints
`token count not reported`, so a missing figure is visible rather than silent.

### 5.2 How much to budget

All figures from `../docs/phase1-blueprint/grade-distribution-and-tokens.md`,
section 3, for one full lab run with reasoning off.

| Week | Model calls | Tokens |
|---|---|---|
| 1, call the model from code | 9 | 2,560 |
| 2, structured output | 6 | 3,200 |
| 3, grounding | 13 | 9,500 |
| 4, tools | 18 | 21,300 |
| 5, the bounded loop | 39 | 76,000 |
| 6, guardrails | 99 | 164,000 |
| 7, output and evaluation | 69 | 112,000 |
| **Course total, one clean pass** | **253** | **388,560** |

Weeks 1 and 2 are measured from a full run of the shipped notebooks. The rest
are still projected.

Budget for the rerun case, not the clean one. Students debug, and every rerun
cell is another call. The same document prices every lab rerun once at 777,120
tokens per student.

Against the advisory figure of roughly $5 per student, one clean pass fits if
the model costs under $12.89 per million tokens, and the rerun case fits under
$6.44 (same document, section 3.1). No per-token price exists yet, and no owner
has been named for the central budget
(`../docs/phase1-blueprint/assumptions-and-gaps.md`, C19). Settle both before
the term.

Weeks 6 and 7 are the expensive ones, together about 71 percent of the course
total. A per-student cap that looks generous in week 2 can run out in week 6.

### 5.3 The top-up policy

Stated in the syllabus and on the student policies page. A student who exhausts
their budget emails the instructor and receives a top-up. **There is no grade
penalty for running out, and no late penalty for the days spent waiting**
(`../docs/build-prompt-v1.3.md`; `../content/pages/course-policies.md`).

Two operational consequences.

- Make the top-up a two-minute job for whoever performs it, and make sure it can
  be done without you. A top-up that waits on one person is a late penalty
  wearing a different name.
- Set the per-student cap high enough that running out is rare. The policy costs
  nothing when it is rarely used and costs you the term's grading calendar when
  it is used weekly.

---

## 6. Before the term: the checklist

Run every step in a test student account on the real hosted environment, not on
an instructor account and not on a laptop. Each step names what to expect.

**Environment**

1. Open the notebook server as the test student.
   Expect a file browser showing `corpus/` and the week's notebook.
2. In a new cell, run `import sys; print(sys.version)`.
   Expect 3.11 or newer.
3. In a new cell, run `import requests; print(requests.__version__)`.
   Expect a version string. An `ImportError` here stops the course.

**Configuration**

4. Open `w1-lab.ipynb` and run the configuration cell.
   Expect five lines: the model name, the endpoint, the extra fields, `API key:
   found`, and `Email files: found` with a path. Expect no `NOT FOUND` anywhere.
5. Read the extra fields line.
   Expect `Extra fields: {'reasoning_effort': 'none'}` when the model is Granite
   4.2, and `Extra fields: {}` when it is Granite 4.1. An empty dictionary
   against a 4.2 model means the model name did not match the gate in section
   3.3, and reasoning is on.
6. Run the token counter cell.
   Expect `Tokens this session: 0 total, 0 sent, 0 answered, over 0 calls.`
7. Run the helper cell.
   Expect `send_request() and save_artifact() are ready.`

**The key**

8. Restart the kernel and run the configuration cell again.
   Expect `API key: found` a second time. This proves the variable comes from
   the environment and not from something that ran earlier in the session.
9. Search the saved notebook file for the word `Bearer`.
   Expect no match in any cell output. Do not add a cell that prints `API_KEY`,
   and do not print the environment.

**The model**

10. Make one call. In a new cell below the helper cell, build the request the
    way the lab does and send it:

    ```python
    payload = {"model": MODEL,
               "messages": [{"role": "user", "content": "Say hello in one sentence."}],
               "max_tokens": 512, "temperature": 0.2}
    payload.update(MODEL_EXTRAS)
    reply = send_request(payload)
    print(reply["choices"][0]["message"]["content"])
    ```

    Expect a short answer, then a line reading `this call: N tokens. Session
    total so far: N`, with N in the low hundreds.
11. In a new cell, run `print(len(LAST_CALL["reasoning"]))`.
    Expect `0`. Any other number means reasoning is still on, and section 3.3
    says what that costs.
12. Time one call.
    Expect a few seconds. A call near 80 seconds is the reasoning-on
    configuration (`../docs/week5-model-test.md`).
13. Deliberately break the endpoint by pointing `ITSY1377_BASE_URL` at a wrong
    port in a scratch copy, and make one call.
    Expect `This call did not work.` followed by a plain sentence and three
    numbered things to check. The three checks print once per session, so use a
    fresh kernel. Expect no traceback. This is the message a student gets at
    11pm, so read it once yourself.

**The files**

14. Run `from parse_eml import parse_eml` and parse email 001.
    Expect a dictionary of parsed headers, not a `FileNotFoundError`.
15. Write a file the way a lab does. In a new cell, run
    `save_artifact("setup_check.txt", "environment check")`.
    Expect the full path printed, then the first lines of the file, and the file
    itself visible in the server's file browser. The real week 2 artifact,
    `week2_classification.json`, needs the two TODO cells filled first, so use
    this instead until a solution notebook ships.
16. Download `setup_check.txt` from the notebook server through the browser.
    Expect a normal download with no security warning. The equivalent test for
    `.eml` files through Canvas has already passed
    (`../docs/phase0-download-test.json`).

**Persistence and week 0**

17. Sign out, then sign back in the next day.
    Expect the notebook and `setup_check.txt` both still there, with your edits
    intact. This is the promise week 1 makes in writing.
18. Open `week00-python-on-ramp.ipynb` and run every cell.
    Expect every cell to run with no key and no network, because week 0 makes no
    model calls.

**Each term after the first**

19. Re-run the week 5 measurement with
    `python3 builder/lab/eval/week5_loop_test.py --all`.
    Expect it to assert the endpoint, the model digests and the hash of every
    email before it measures, and to write its results after every run. Model
    versions change; this is the test that says whether week 5 still works
    (`../docs/week5-model-test.md`).
