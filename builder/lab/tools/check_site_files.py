#!/usr/bin/env python3
"""Prove every course file a notebook opens is a file the site actually serves.

THE DEFECT THIS EXISTS FOR. `w7-lab.ipynb` cell 9 loads
`corpus/release/ground_truth_teaching.json`. That file is in the repository and
it is in `never_ship`, so `stage_notebook_site.py` does not stage it and the
site returns 404. The lab crashes there and the two submission artifacts below
the crash are never produced.

Every gate missed it, and one reason explains all of them:
`run_notebook.py` executes a notebook in `lab/notebooks/`, so the notebook's
upward COURSE_DIR walk lands on `builder/`, where every `never_ship` file is
present and readable. The gate's filesystem is a strict superset of the
student's, and the delta is exactly the set of files students must never see.
The check ran in the one environment where the bug cannot appear.

WHAT THIS ASSERTS. For every literal path expression rooted at one of the
notebook's own directory names -- COURSE_DIR, EMAIL_DIR, DATA_DIR, TOOLS_DIR,
LAB_TOOLS_DIR -- the named file exists inside the staged site tree. It reads
the notebooks as JSON and the cells as an AST. It executes nothing, calls no
model, and takes about a second.

It deliberately covers the solution notebooks too. The week 7 solution carries
the same line, so the solution gate proved nothing about it either.

Run:
    python3 builder/lab/tools/stage_notebook_site.py /tmp/site
    python3 builder/lab/tools/check_site_files.py /tmp/site

Or let it stage a throwaway tree itself:
    python3 builder/lab/tools/check_site_files.py

Exit status 1 means a notebook opens a file the site does not serve.
"""

import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

BUILDER = Path(__file__).resolve().parents[2]

# The directory names the configuration cell defines, and where each one sits
# relative to COURSE_DIR. COURSE_DIR itself is the site root.
ROOTS = {
    "COURSE_DIR":    Path("."),
    "EMAIL_DIR":     Path("corpus/emails/teaching"),
    "DATA_DIR":      Path("corpus/data"),
    "TOOLS_DIR":     Path("corpus/tools"),
    "LAB_TOOLS_DIR": Path("lab/tools"),
    "SPEC_DIR":      Path("corpus/spec"),
    "BATCH_DIR":     Path("corpus/emails/batch"),
}

SEARCHED = [BUILDER / "lab" / "notebooks", BUILDER / "instructor" / "solutions"]


def path_chain(node):
    """Turn `COURSE_DIR / "a" / "b.json"` into ("COURSE_DIR", ["a", "b.json"]).

    Returns None for anything with a non-literal part, because a path built
    from a variable cannot be resolved without running the notebook.
    """
    parts = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, str):
            return None
        parts.insert(0, node.right.value)
        node = node.left
    if isinstance(node, ast.Name) and node.id in ROOTS:
        return node.id, parts
    return None


def references(notebook_path):
    """Every literal course-file path the notebook opens. (cell number, root, parts)."""
    notebook = json.loads(Path(notebook_path).read_text(encoding="utf-8"))
    found = []
    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        # A JupyterLite cell may carry a top level await, which ast rejects.
        source = source.replace("await ", "")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.BinOp):
                continue
            chain = path_chain(node)
            if not chain:
                continue
            root, parts = chain
            if not parts:
                continue
            found.append((index + 1, root, parts))
    return found


def stage_temporary():
    """Build a throwaway site tree with the shipping tool, and return its path."""
    out = Path(tempfile.mkdtemp(prefix="itsy1377-site-")) / "site"
    result = subprocess.run(
        [sys.executable, str(BUILDER / "lab" / "tools" / "stage_notebook_site.py"), str(out)],
        capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit("staging failed, so there is nothing to check against")
    return out


def main(argv):
    site = Path(argv[1]).resolve() if len(argv) > 1 else stage_temporary()
    if not site.is_dir():
        print("no staged site at " + str(site))
        return 2

    problems = []
    checked = 0
    for folder in SEARCHED:
        if not folder.is_dir():
            continue
        for notebook in sorted(folder.glob("*.ipynb")):
            for cell, root, parts in references(notebook):
                target = site / ROOTS[root].joinpath(*parts)
                # A path with no suffix is a directory the notebook lists or
                # globs. Those are checked as directories; files are checked
                # as files.
                wanted_file = bool(Path(parts[-1]).suffix)
                checked += 1
                if wanted_file and not target.is_file():
                    problems.append(
                        f"{notebook.relative_to(BUILDER)}  cell {cell}:  "
                        + root + " / " + " / ".join(parts)
                        + "\n      is not on the site. It is in the repository, so every "
                          "gate that runs\n      in the repository will pass. A student gets "
                          "a 404 and the notebook stops.")
                elif not wanted_file and not target.is_dir():
                    problems.append(
                        f"{notebook.relative_to(BUILDER)}  cell {cell}:  "
                        + root + " / " + " / ".join(parts) + "\n      is not a folder on the site.")

    print(f"site:       {site}")
    print(f"notebooks:  {sum(len(list(f.glob('*.ipynb'))) for f in SEARCHED if f.is_dir())}")
    print(f"references: {checked} literal course-file path(s)")
    print()
    if problems:
        for line in problems:
            print("MISSING  " + line)
        print()
        print(f"check_site_files: {len(problems)} reference(s) the site does not serve")
        return 1
    print("check_site_files: every course file the notebooks open is on the site")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
