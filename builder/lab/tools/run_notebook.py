#!/usr/bin/env python3
"""Run a lab notebook the way a student runs it, and say what broke.

A student notebook has to survive two runs, and this checks both.

  --student   Every TODO cell is still unwritten. The notebook must still run
              from top to bottom without raising. A TODO cell defines its
              function and returns None, so the cells below it print the
              unwritten-function state instead of crashing. A student who
              opens the notebook and runs everything before writing a line
              must see a working notebook, not a traceback.

  --solution  Every TODO cell is filled in. The notebook must run clean and
              must write its submission artifact. This is the instructor
              solution, and it is the only proof the lab is completable.

It runs the notebook in place with nbclient, in the notebook's own folder, so
the configuration cell finds the course files the same way a student's does.
Nothing is written back into the notebook file: the executed copy is thrown
away unless --save-executed names somewhere to put it.

Run:
    python3 builder/lab/tools/run_notebook.py builder/lab/notebooks/w3-lab.ipynb --student
    python3 builder/lab/tools/run_notebook.py builder/instructor/solutions/w3-lab-solution.ipynb \\
        --solution --expect-artifact week3_grounding.json
    python3 builder/lab/tools/run_notebook.py builder/lab/notebooks/ --all --student

The endpoint and model come from the environment, exactly as they do for a
student:

    ITSY1377_BASE_URL   default http://localhost:11434/v1
    ITSY1377_MODEL      default granite4.2:3b
    ITSY1377_API_KEY    any non-empty string satisfies a local server

This tool calls the model. Never run it while anything else is writing to the
corpus, and never treat its output as a measurement: it proves the notebook
runs, not how well the model does. The measurement lives in
builder/lab/eval/week5_loop_test.py and records the digest of every file it
reads.
"""

import argparse
import glob
import json
import os
import shutil
import sys
import tempfile
import time

try:
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError
except ImportError:  # pragma: no cover
    print("this needs nbformat and nbclient: python3 -m pip install nbformat nbclient")
    raise SystemExit(2)

import re

# A TODO cell opens with a banner line of the form "# TODO 1. Write ...".
# Nothing else in a notebook matches that, so a cell that merely mentions the
# word TODO in prose is not counted as one.
TODO_BANNER = re.compile(r"^#\s*TODO\s+\d+\.", re.MULTILINE)
# The two finished weeks use different placeholder wording, and both are
# fine. What matters is that the cell is plainly unwritten and that the
# notebook still runs. These are the markers in use; a new week adds its
# wording here rather than inventing a third convention silently.
PLACEHOLDERS = (
    "your code here",
    "Write your lines here",
    "is not written yet",
)


def todo_cells(notebook):
    """Indexes of the cells that carry a TODO the student fills in."""
    return [index for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "code" and TODO_BANNER.search(cell.source)]


def unfilled(notebook):
    """Indexes of TODO cells that are still waiting for the student."""
    found = []
    for index in todo_cells(notebook):
        source = notebook.cells[index].source
        if any(mark in source for mark in PLACEHOLDERS):
            found.append(index)
        elif source.rstrip().endswith("pass"):
            found.append(index)
    return found


def run(path, timeout, kernel):
    """Execute one notebook in its own folder. Return (notebook, error)."""
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=kernel,
        resources={"metadata": {"path": os.path.dirname(os.path.abspath(path))}},
        allow_errors=False,
    )
    try:
        client.execute()
        return notebook, None
    except CellExecutionError as error:
        return notebook, error


def failing_cell(notebook):
    """The first cell whose output holds an error, and its traceback."""
    for index, cell in enumerate(notebook.cells):
        for output in cell.get("outputs", []) or []:
            if output.get("output_type") == "error":
                trace = "\n".join(output.get("traceback", []))
                return index + 1, output.get("ename", ""), output.get("evalue", ""), trace
    return None, "", "", ""


def artifact_written(notebook, name):
    """True when some cell's printed output names the artifact file."""
    for cell in notebook.cells:
        for output in cell.get("outputs", []) or []:
            text = output.get("text") or ""
            if isinstance(text, list):
                text = "".join(text)
            if name in text:
                return True
            data = output.get("data", {}) or {}
            if name in str(data.get("text/plain", "")):
                return True
    return False


def check(path, mode, expect_artifact, timeout, kernel, save_executed):
    label = os.path.relpath(path, os.getcwd())
    source = nbformat.read(path, as_version=4)
    todos = todo_cells(source)
    open_todos = unfilled(source)

    problems = []
    if mode == "student" and todos and not open_todos:
        problems.append("every TODO cell is already filled in; this is a solution, "
                        "not a student notebook")
    if mode == "solution" and open_todos:
        problems.append("TODO cell(s) " + ", ".join(str(i + 1) for i in open_todos)
                        + " are still unwritten")

    started = time.time()
    notebook, error = run(path, timeout, kernel)
    seconds = time.time() - started

    if error is not None:
        number, ename, evalue, trace = failing_cell(notebook)
        problems.append("cell " + str(number) + " raised " + ename + ": " + evalue)
        tail = [line for line in trace.splitlines() if line.strip()][-4:]
        for line in tail:
            problems.append("    " + line)

    if mode == "solution" and expect_artifact and not artifact_written(notebook, expect_artifact):
        problems.append("no cell printed the name " + expect_artifact
                        + ", so the export cell did not run")

    for stray in glob.glob(os.path.join(os.path.dirname(os.path.abspath(path)),
                                        "week*_*.json")) + \
                 glob.glob(os.path.join(os.path.dirname(os.path.abspath(path)),
                                        "week*_*.txt")):
        # The export cell writes the student's submission file next to the
        # notebook. A check run is not a submission, so it does not leave one
        # behind for the next run to find and mistake for its own.
        os.remove(stray)

    if save_executed:
        os.makedirs(save_executed, exist_ok=True)
        out = os.path.join(save_executed, os.path.basename(path))
        nbformat.write(notebook, out)

    print(("FAIL " if problems else "ok   ") + label
          + "  (" + mode + ", " + str(len(source.cells)) + " cells, "
          + str(len(todos)) + " TODO, " + str(round(seconds, 1)) + "s)")
    for line in problems:
        print("       " + line)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a lab notebook and say what broke.")
    parser.add_argument("path", help="a notebook, or a folder with --all")
    parser.add_argument("--all", action="store_true", help="run every .ipynb in the folder")
    parser.add_argument("--student", action="store_true", help="TODO cells are unwritten")
    parser.add_argument("--solution", action="store_true", help="TODO cells are filled in")
    parser.add_argument("--expect-artifact", help="the submission file name the export cell prints")
    parser.add_argument("--timeout", type=int, default=1800, help="seconds per cell")
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--save-executed", help="write the executed copies here")
    args = parser.parse_args(argv)

    mode = "solution" if args.solution else "student"

    if args.all:
        paths = sorted(glob.glob(os.path.join(args.path, "*.ipynb")))
    else:
        paths = [args.path]
    if not paths:
        print("no notebooks found at " + args.path)
        return 1

    # The notebooks now default to the live proxy, because that is what a
    # student's browser must reach. A gate run has to say otherwise, or every
    # check fires real requests at production: one run put 201 failed calls
    # into the proxy's log before this was noticed. The endpoint is declared
    # here, where the gate owns its own test environment.
    os.environ.setdefault("ITSY1377_BASE_URL", "http://localhost:11434/v1")
    os.environ.setdefault("ITSY1377_MODEL", "granite4.2:3b")
    if not os.environ.get("ITSY1377_API_KEY"):
        os.environ["ITSY1377_API_KEY"] = "local-run"

    # Say where the calls are going. A run that silently pointed at the live
    # proxy put 201 failed requests into the students' endpoint before anyone
    # noticed, and nothing in the output said which endpoint was in use.
    endpoint = os.environ["ITSY1377_BASE_URL"]
    print(f"endpoint:  {endpoint}")
    print(f"model:     {os.environ['ITSY1377_MODEL']}")
    if "localhost" not in endpoint and "127.0.0.1" not in endpoint:
        print("           this is NOT a local endpoint. These runs cost real")
        print("           money and count against a real key's rate limits.")

    failures = 0
    for path in paths:
        problems = check(path, mode, args.expect_artifact, args.timeout,
                         args.kernel, args.save_executed)
        if problems:
            failures += 1

    print()
    print(str(len(paths)) + " notebook(s), " + str(failures) + " failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
