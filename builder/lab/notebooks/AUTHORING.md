# How to author a notebook for this course

Every notebook in this course is written against this file and against
`builder/docs/phase1-blueprint/code-ledger.md`. The ledger is the contract: it
fixes every function name and signature, every cell and its number, what the
student writes, what arrives pre-written, and the exact submission file. This
file says how to build one and how to prove it works.

## 1. The two kinds

**A sidebar notebook** teaches one Python construct in an everyday domain. It
is ungraded, it makes no model call, and it never touches email, alerts,
headers or verdicts. It is 8 to 14 cells and takes 20 to 30 minutes.

**A lab notebook** is the week's work. It carries working code for every week
before it, adds this week's scaffolding, marks one or two TODO cells, and ends
with a pre-written export cell that writes the submission file.

## 2. The rule a student notebook must not break

**A student who opens the lab and runs every cell before writing a single line
must see a working notebook, not a traceback.**

An unwritten TODO cell therefore defines its function and returns something
harmless. The cells below it print a state that plainly says the function is
not written yet. Nothing raises.

Both finished weeks satisfy this in slightly different words, and both are
fine:

| Week | The placeholder | What the cells below print |
|---|---|---|
| 1 | `# your code here` and `return "ask_model() is not written yet."` | the sentence itself, in every answer slot |
| 2 | `# Write your lines here, in place of this comment and the line below.` and `pass` | `no answer` in the results table |

Pick whichever fits the cell, and make sure the check cell below it says
something a beginner can read. Never leave a bare `raise NotImplementedError`.

## 3. Cell shape

`nbformat` 4. Every cell carries an `id`. The metadata block copies the one in
`w2-lab.ipynb`, including the `title`.

A TODO cell opens with a banner line the tools match on:

```python
# =====================================================================
# TODO 1. Write build_facts(parsed).
# =====================================================================
```

Then, in comments, in this order: what it takes, what it gives back, what it
does as numbered steps, about how many lines, which sidebar and which week 0
section prepare it, and one line saying how to tell it worked. Then the
signature and the placeholder. Read cells 10 and 13 of `w2-lab.ipynb` and match
that shape exactly.

A pre-written cell opens with a comment saying it is pre-written and that the
student does not edit it.

## 4. What every lab notebook carries

Sections 2.1 to 2.5 of the code ledger fix the parts that never change: the
configuration cell, the token counter, `send_request()`, `save_artifact()` and
`load_email()`. Copy them from the week before, unchanged. A change to one of
them breaks every later week.

The carry-forward cell is the one that makes the continuity promise true. Week
N's cell 5 holds working versions of everything the student wrote in weeks 1 to
N-1, so a student who never finished week N-1 can still do week N. Take that
code from week N-1's own notebook so the two cannot drift.

## 5. Rules that are not negotiable

1. **No key is ever displayed.** The configuration cell reports whether a key
   was found and nothing else. No cell prints `API_KEY`, and no instruction
   asks a student to screenshot one.
2. **The export cell is pre-written and writes exactly the file the ledger
   names.** It prints the full path so a student knows what to upload.
3. **The screenshot cell is the one the rubric names.** Its printed output has
   to hold everything the rubric grades.
4. **A sidebar shares no name with its lab.** Not a function, not a parameter,
   not a variable. A student who pastes the sidebar into the TODO cell must get
   a `NameError`, and the week spec lists the names so this can be checked.
5. **No sidebar reuses another sidebar's domain.** Each of the seven weeks uses
   a different everyday subject.
6. **Nothing real.** Every company, person, domain and address comes from the
   corpus organization.
7. **No vendor name in student-facing prose.** The model is named by its role.
   The `MODEL` value is a configuration string, which is different.
8. **Markdown cells obey the course writing standard**: second person, active
   voice, short sentences, no em dashes or en dashes, no idioms.

## 6. How to prove it works

From the repository root:

```
python3 builder/lab/tools/run_notebook.py builder/lab/notebooks/w3-lab.ipynb --student
```

That runs the notebook in its own folder, the way a student's server does, and
fails on any cell that raises. It also deletes the submission file the export
cell writes, because a check run is not a submission.

For the instructor solution:

```
python3 builder/lab/tools/run_notebook.py \
    builder/instructor/solutions/w3-lab-solution.ipynb \
    --solution --expect-artifact week3_grounding.json
```

That one fails unless the export cell actually ran and printed the file name.
The solution notebook is the only proof the lab is completable, so it is not
optional.

Both call the live model. Never run either while anything else is writing to
the corpus, and never read a number out of them as a measurement. They prove
the notebook runs. How well the model does is measured in
`builder/lab/eval/`, by a harness that records the digest of every file it
reads.

## 7. Time and tokens

The week spec sets both. The lab's model call count is in the code ledger,
per week, built from the corpus. If your notebook makes more calls than the
ledger says, the week's token estimate is wrong and one of the two has to
change. Say which.
