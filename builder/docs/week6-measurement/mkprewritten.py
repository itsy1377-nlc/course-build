#!/usr/bin/env python3
"""Extract week 6's pre-written code into one importable module.

The rig under test has to be the code students run, so this reads the cells
out of the notebooks rather than restating them. Cells that DRIVE a run (5's
closing demonstration, 6, 10, 11, 15, 16, 17) are cut at their first
top-level statement, because a probe decides for itself what to run.

    python3 builder/docs/week6-measurement/mkprewritten.py OUTDIR

writes OUTDIR/w6_prewritten.py (lab notebook, TODOs unwritten) and
OUTDIR/w6_solution.py (solution notebook, TODOs written).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = ROOT / "builder/lab/notebooks/w6-lab.ipynb"
SOL = ROOT / "builder/instructor/solutions/w6-lab-solution.ipynb"

# Cells that define things. 6, 10, 11, 15, 16 and 17 only drive.
KEEP = [1, 2, 3, 4, 5, 8, 9, 13, 14]
# Where a kept cell stops being definitions and starts being a demonstration.
CUT_AT = {5: "\nstart_run()\n", 8: '\nprint("Fence markers:")'}

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
        src = "".join(cells[i]["source"]).replace(PIPLITE, "pass")
        marker = CUT_AT.get(i)
        if marker and marker in src:
            src = src.split(marker)[0]
        out.append("# ===== cell %d =====\n%s" % (i, src))
    return "\n\n\n".join(out) + "\n"


if __name__ == "__main__":
    outdir = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    outdir.mkdir(parents=True, exist_ok=True)
    for name, path in (("w6_prewritten.py", LAB), ("w6_solution.py", SOL)):
        text = build(path)
        (outdir / name).write_text(text)
        print("wrote", outdir / name, len(text), "chars")
