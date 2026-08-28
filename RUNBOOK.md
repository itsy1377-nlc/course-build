# ITSY 1377: Demo Runbook

Everything needed to stand this up from nothing and show it to somebody.

Two audiences are covered. **Part 1** is the operator: build it, verify it,
know what breaks. **Part 2** is a ten minute walkthrough for a program manager
or a curriculum committee, with the honest answers to the questions they will
ask.

---

## What this is

A working proof of concept of **ITSY 1377: Agentic AI and Security Operations**,
a 3 credit hour, 8 week Flex, fully asynchronous course, running in a real
Canvas LMS.

| Piece | Where | What it is |
|---|---|---|
| Canvas | `canvas/deploy/` | Canvas LMS built from `instructure/canvas-lms`, running locally |
| Course content | `content/` | 57 authored pages, 6 quizzes, 5 rubrics, all from one `course.yaml` |
| Lab repository | `labs/` | The agent, the vulnerable target, and the test harness |
| Build tooling | `tools/` | Cartridge generator, Canvas importer, reading level check |
| Blueprint | `docs/course-blueprint.md` | The design, its costs, and what it cannot do |

---

# Part 1: Standing it up

## Before you start

- Docker with at least 8GB allocated, and about 25GB of free disk.
  On macOS: `colima start --cpu 6 --memory 16 --disk 60`
- Python 3.11 or newer
- About 40 minutes, most of it the Canvas image build

## One time, from nothing

```bash
# 1. Canvas. Slow the first time: it clones 723MB and builds an image.
./canvas/deploy/setup.sh

# 2. Build tooling for the course content
pip install -r tools/requirements.txt

# 3. Build the course, import it, and verify what actually arrived
python -m tools.import_cartridge

# 4. The labs
cd labs
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
echo "LAB_STUDENT_ID=demo-instructor" > .env
python verify_env.py
python -m target.seed
```

Canvas is then at **http://localhost:3000**, `admin@itsy1377.local` /
`Itsy1377demo!`, with the course at `/courses/1`.

## Bringing it back up later

```bash
./canvas/deploy/setup.sh --start          # Canvas
cd labs && source .venv/bin/activate
python -m target.app                      # the vulnerable app, leave running
```

## Rebuilding after editing content

```bash
python -m tools.readability               # reading level, fails the build if over
python -m tools.cartridge --check         # validate without building
python -m tools.import_cartridge          # build, import, verify
```

The import is idempotent. Running it again updates the course rather than
duplicating it, because every identifier is derived from the content ref.

## What "verified" means here

`python -m tools.import_cartridge` does not trust the word "completed". After
the migration it reads the course back through the API and checks it against
`content/course.yaml`: every module and its item count, every assignment group
and its weight, the points on every graded item, the question count on every
quiz, the rubrics, and that no page still carries a template placeholder.

That check is not decoration. It is what caught the finding in the next
section.

---

## Three things that went wrong, and what they cost

These are recorded because somebody will hit them again.

### 1. Canvas silently drops every quiz in every cartridge

**Symptom.** The import reports `completed`, with no error, no warning, and no
migration issue. The course has all its pages, assignments, modules, rubrics
and outcomes. It has zero quizzes.

**Cause.** Canvas converts QTI by shelling out to an external Python program,
`migrate.py` from the QTIMigrationTool. `gems/plugins/qti_exporter/lib/qti.rb`
looks for it in two vendored paths and then on `PATH`, and registers the
`qti_converter` plugin as `enabled: python_converter_found`. Open-source Canvas
does not ship that program, so the plugin is disabled and quizzes are skipped
without comment.

**How we know it is the environment and not the file.** The NLC template's own
cartridge, exported by Instructure's own Canvas, imports zero of its two
quizzes into this instance too. That test is what separated "my file is wrong"
from "this Canvas cannot read any file", and it took two minutes.

**The fix, and what it means for the deliverable.** `tools/populate_canvas.py`
creates the quizzes over the REST API instead, and `tools/import_cartridge.py`
runs it automatically. On Alamo's Canvas, which is Instructure-hosted and has
the converter, the cartridge carries the quizzes and this step is unnecessary
and harmless. So the cartridge is the deliverable, the API script is what makes
a local demo complete, and both are needed for different reasons.

### 2. Passenger listens on port 80 inside the container, not 3000

Mapping `3000:3000` gives a host port that silently refuses connections while
Rails is perfectly healthy. Every symptom points at a dead application. The fix
is `3000:80` and it is in `canvas/deploy/docker-compose.override.yml`.

### 3. Gems are not in the image

They live in a named volume, so `bundle install` has to run once. Skipping it
produces an error about the `crystalball` git source "not yet checked out",
which reads like a repository problem and only means gems are missing.

**Also worth knowing:** `script/docker_dev_setup.sh` is deliberately not used.
Its macOS branch installs dinghy-http-proxy system-wide without asking, which
is reported to break unrelated Docker work. The setup script does the same work
by hand and publishes a port.

---

## Running the labs

```bash
cd labs && source .venv/bin/activate

python -m target.seed          # build the lab data with your canary tokens
python -m target.app           # the vulnerable app, leave this running

# in a second terminal
python -m agent.cli "summarize ticket T-503"
python -m agent.replay         # watch that run step by step, in plain language
python -m harness.runner       # run the attack cases
python -m pytest tests/ -q     # the autograder
```

Everything above runs offline with no API key. The `mock` provider is a small
simulator, not a model, and every report it produces says so at the top.

### The five minute demo of the whole arc

```bash
./demo/run_demo.sh
```

Attack lands, fix goes in, attack stops, normal use survives. It puts every
file back the way it found it when it finishes.

### Producing the repository students actually get

```bash
python scripts/build_student_repo.py ../itsy1377-labs-student
```

This matters. The working repository contains the complete worked answer to
every graded extension point, in `solution/`, `reference/`, and `demo/`. Those
directories each say "not in the student repository" in their own README, and
that was a promise with no mechanism behind it until this script existed. It
strips them, strips anything a previous run produced, and then **refuses to
finish** if any forbidden path or any answer string survived, or if the five
extension points are no longer stubs.

---

# Part 2: The ten minute walkthrough

Have Canvas open at `http://localhost:3000/courses/1` and a terminal in `labs/`
with the target app already running.

### Minute 1: the course exists and it is a real course

Open the course home. Walk the module list: Start Here, seven weekly modules,
the Final Block, Where To Go Next, and an unpublished instructor module.

Open **Week 5: Prompt Injection**. Show the four part anatomy the NLC template
requires: an Overview page, a Content page, the graded assignment, and a
Wrap-up. Every week is built that way. It is not a mock-up of one week.

### Minute 2: it is written for the students who take it

Open the Week 5 Content page. Then run:

```bash
python -m tools.readability | tail -5
```

54 enforced pages, mean Flesch-Kincaid grade **4.40** against a limit of 8.0.
The check excludes code, tables, framework identifiers and quoted text, because
scoring those would make the number dishonest, and it says so. The report is
committed at `docs/readability-report.json` so a reviewer can read the numbers
rather than take the claim on faith.

The Rules of Engagement page is held to a tighter bar than the rest and scores
**4.0**. It is the one page where misreading has consequences.

### Minute 3: the one rule, and how it is enforced

Open the **Rules of Engagement** page. Seven numbered clauses. Students may
attack three things and nothing else. They pass a quiz on it before Week 2
opens, and it is referenced in every attack lab.

Then show that it is a control rather than a policy:

```bash
cd labs
python - <<'EOF'
from agent import tools
from agent.config import load_config
cfg = load_config().with_overrides({"target": {"base_url": "http://example.com"}})
try:
    tools._get(cfg, "/api/tickets")
except tools.ToolError as e:
    print(e)
EOF
```

The tools refuse at the socket, not at the grader. An earlier version enforced
scope only in the harness, which meant the CLI would happily send requests
anywhere the settings file pointed.

### Minutes 4 to 6: the attack, and why it is the interesting one

```bash
python -m agent.cli "Please read ticket T-503 and give me a short summary."
python -m agent.replay
```

Walk the replay output. The support agent asked for a summary. That is all they
did. The instruction to email a customer record to an outside address came out
of the ticket body, written by whoever opened the ticket, sitting in a database
waiting for an assistant to read it.

Then show the evidence rather than the transcript:

```bash
ls target/outbox/ && cat target/outbox/*.json | head -20
```

A file exists, addressed outside the company, containing the customer's stored
payment reference. That file either exists or it does not. That is what the
course grades on.

### Minutes 7 to 9: the harness, and the number that makes the argument

```bash
python -m harness.runner
```

Point at four things while it runs:

1. **It refuses an out-of-scope target and writes the refusal down.** "I stayed
   in scope" is a claim. A results file showing the tool declining is evidence.
2. **The detectors pass a 20 probe self-test first**, in both directions: every
   detector has to fire when the attack clearly worked and stay quiet when
   nothing happened. A detector hardcoded to return True passes a one direction
   test and is worse than no detector.
3. **Two benign controls.** One checks that ordinary work stays quiet. The
   other checks that a legitimate escalation still goes out, which is what
   stops "delete the tool" from counting as a remediation.
4. **Rates, never a yes or no.** `5/5`, `3/5 FLAKY`, `0/5 MITIGATED`.

Then the payload of the whole design:

```bash
python demo/apply_solution.py apply
python -m harness.runner
python demo/apply_solution.py revert
```

Four cases flip to `ATTEMPTED_BLOCKED 0/5`. Three stay `VULNERABLE`. That is the
honest result and it is the lesson: a recipient allowlist fixes one class of
weakness. It does nothing about system prompt disclosure or a missing
authorization check. Different weakness, different control.

`ATTEMPTED_BLOCKED` is worth pausing on. It means the agent was still fully
hijacked and asked to send the record every single time, and one line of code
stopped it. That is a very different residual risk from an attack that failed,
and a report that prints them identically is hiding the thing a client most
needs to know.

### Minute 10: what it cannot do

Open `docs/course-blueprint.md` section 8.3, or say it from memory:

- Not OWASP LLM Top 10 coverage. Three of ten substantively. The materials say
  "selected OWASP risks" and never "the OWASP LLM Top 10".
- Not agent development. Students extend a scaffold and cannot build one from
  an empty directory.
- Not Python competence. This course does not articulate into COSC 1436 and
  must not be listed as preparation for it.
- Not red teaming. Pre-authored attack classes against one known-vulnerable
  instructor-built target is exercise, not discovery.
- Insecure tool authorization is a guided walkthrough, not a hands-on lab. That
  is the biggest thing the seven week calendar cost, and it is named in the
  blueprint rather than glossed.

---

## Questions you will be asked

**"Does it look like our real courses?"**
Not exactly, and the difference is documented. Every page carries the exact
Cidi Labs DesignPLUS class names the NLC template uses, so the content is
drop-in for Alamo's Canvas where the real DesignPLUS will style it correctly
with no rework. Locally there is no DesignPLUS license, so `canvas/theme/`
supplies a small openly licensed stylesheet that reproduces the structure. No
Cidi Labs CSS or JavaScript is copied. It is a stand-in for the demo and it
will not match the production theme.

**"How much of the grade is automatic?"**
73 percent. Total hand-reading across the whole term is about five hours, and
the design lands at 22.7 instructor hours, or 26.1 with contingency. The lever
is that comprehension questions are anchored to each student's own run
artifacts, so AI assistance is permitted and simply does not help on them.

**"Can students just use AI to do it?"**
On the coding, yes, and they are told to. Outcome 6 requires them to evaluate
AI-generated code for correctness, and a course that bans AI cannot assess
that. What is graded instead is whether they understand what they submitted,
through questions only their own run can answer, and through defect-injection
items where they have to find the bug in code that looks right.

**"What if a student cheats?"**
Canary tokens are derived from the student ID, so a classmate can share a
working payload and cannot share the proof. Be straight about the limit: the
term salt has to be on every student machine for the labs to work, so a
determined student could compute another's tokens. This is a local lab, not an
exam hall. The controls raise the cost; they do not eliminate it.

**"Is it ready to teach?"**
No, and the blueprint says what is missing. The largest item is that the local
model path has never been tested on a real locked-down student laptop, and no
amount of documentation research retires that. Section 9 of the blueprint lists
everything assumed and everything that could not be verified.

---

## Teardown

```bash
cd canvas/canvas-lms && docker compose stop        # keep the data
docker compose down -v                             # delete everything
pkill -f "target.app"                              # the lab app
```

---

## If something is wrong

| Symptom | Cause | Fix |
|---|---|---|
| `HTTP 000` from Canvas, containers healthy | port mapped `3000:3000` | `3000:80`, see the override file |
| `crystalball ... not yet checked out` | gems not installed | `docker compose run --rm --no-deps web bundle install` |
| Import completes, no quizzes | Canvas has no QTI converter | expected; `tools/populate_canvas.py` handles it |
| Harness refuses to start, canary mismatch | `.env` changed after seeding | `python -m target.seed` |
| Harness refuses, "shared demo student ID" | `LAB_STUDENT_ID` unset | set it in `.env`, then reseed |
| A control fails and the run stops | usually a stale outbox | this is the harness working; read what it says |
| `tests/` shows many failures | expected on a fresh clone | those are the student's work, not defects |
