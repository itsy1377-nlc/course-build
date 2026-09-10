#!/usr/bin/env python3
"""Extract week 7's pre-written code into one importable module.

Same method as week 6. The rig under test has to be the code students run, so
this reads the cells out of the notebooks rather than restating them. Cells
that DRIVE a run (6, 8, 10, 11, 14, 15, 16) are left out, and a kept cell is
cut at the point where it stops defining and starts demonstrating.

    python3 builder/docs/week7-measurement/mkprewritten.py OUTDIR

writes OUTDIR/w7_prewritten.py (lab notebook, TODOs unwritten) and
OUTDIR/w7_solution.py (solution notebook, TODOs written).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "builder/lab/notebooks/w7-lab.ipynb"
SOL = ROOT / "builder/instructor/solutions/w7-lab-solution.ipynb"

# 1-3 config and helpers, 4 weeks 1-6, 5 the schema and the note, 7 TODO 1,
# 9 the batch and the key, 12 TODO 2, 13 the score report.
KEEP = [1, 2, 3, 4, 5, 7, 9, 12, 13]

# Where a kept cell stops being definitions and starts being a demonstration.
CUT_AT = {
    5: '\nprint("The six keys your agent is asked for this week:")',
    9: '\nprint("Batch folder:      ", BATCH_DIR)',
    13: '\nBATCH_COUNTS = score_batch(BATCH_ROWS, GROUND_TRUTH)',
}

# The browser's package installer is an await at module level, which is legal
# in a notebook cell and a SyntaxError in a file. A plain interpreter already
# has requests, which is what the except branch says.
PIPLITE = """try:
    import piplite
    await piplite.install("requests")
except ImportError:
    pass  # a normal Jupyter server already has requests"""


def build(path):
    cells = json.load(open(path))["cells"]
    out = []
    for i in KEEP:
        src = "".join(cells[i]["source"])
        if PIPLITE in src:
            src = src.replace(PIPLITE, "# piplite block removed for the rig")
        if i in CUT_AT:
            mark = CUT_AT[i]
            if mark not in src:
                raise SystemExit(
                    f"cell {i} of {path.name} no longer contains its cut mark."
                    f" The rig must not guess. Mark was: {mark.strip()[:60]}")
            src = src[:src.index(mark)]
        out.append(f"# ===== cell {i} of {path.name} =====\n{src.rstrip()}\n")
    return "\n\n".join(out) + "\n"


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    outdir = Path(sys.argv[1])
    outdir.mkdir(parents=True, exist_ok=True)
    for path, name in ((LAB, "w7_prewritten.py"), (SOL, "w7_solution.py")):
        text = build(path)
        (outdir / name).write_text(text)
        print(f"wrote {outdir / name}  ({len(text.splitlines())} lines,"
              f" from {path.name})")


if __name__ == "__main__":
    main()
