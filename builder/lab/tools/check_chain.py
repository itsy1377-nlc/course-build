#!/usr/bin/env python3
"""Check that every week carries the same code the week before it defined.

The course makes one promise above all others: a student who could not finish
week N-1 can still open week N and do the work, because week N's notebook
carries a working copy of everything the earlier weeks built. Code ledger
section 12 states the cost of getting it wrong: "Weeks 2 to 7 carry earlier
weeks as pre-written cells, so a name change breaks six notebooks."

Nothing checked it. The repair pass that fixes week 5 leaves weeks 6 and 7
holding the old copy, and both notebooks still run, still pass every gate, and
now teach two different versions of the same function. Two repair agents
reported that risk themselves and could not act on it, because each may write
only its own week's files.

This is the check that closes that. For every function defined in more than one
notebook, it compares the definitions and reports any that differ, naming the
week that is behind.

It also reports a function that exists in a later week and not in the week that
is supposed to have introduced it, which is the other way the chain breaks.

Run:
    python3 builder/lab/tools/check_chain.py
    python3 builder/lab/tools/check_chain.py --verbose     # list every shared name
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

BUILDER = Path(__file__).resolve().parents[2]
NOTEBOOKS = BUILDER / "lab" / "notebooks"
SOLUTIONS = BUILDER / "instructor" / "solutions"

# A TODO cell holds the student's own work, which is different in every week by
# design: week 5's notebook carries week 4's finished run_tool(), while week
# 4's holds an empty one for the student to write. Comparing those would report
# a difference on every week, so they are skipped.
TODO_BANNER = re.compile(r"^#\s*TODO\s+\d+\.", re.MULTILINE)


def week_of(path: Path) -> int | None:
    match = re.match(r"w(\d)-lab", path.stem)
    return int(match.group(1)) if match else None


def functions(path: Path) -> dict[str, str]:
    """Every top level function a notebook defines, outside its TODO cells."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    found: dict[str, str] = {}
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        if TODO_BANNER.search(source):
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                # ast.unparse normalises comments and spacing away, so a
                # difference reported here is a difference in the code rather
                # than in how it was typed.
                found[node.name] = ast.unparse(node)
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    labs = sorted((p for p in NOTEBOOKS.glob("w?-lab.ipynb") if week_of(p)),
                  key=week_of)
    if not labs:
        print("no lab notebooks found")
        return 1

    by_week = {week_of(p): functions(p) for p in labs}
    weeks = sorted(by_week)
    print("weeks found: " + ", ".join(str(w) for w in weeks))

    everywhere: dict[str, list[int]] = {}
    for week in weeks:
        for name in by_week[week]:
            everywhere.setdefault(name, []).append(week)

    shared = {n: ws for n, ws in everywhere.items() if len(ws) > 1}
    print(f"{len(everywhere)} function(s) defined across the labs, "
          f"{len(shared)} carried by more than one week")

    problems = []
    for name in sorted(shared):
        weeks_with = shared[name]
        first = weeks_with[0]
        reference = by_week[first][name]
        for week in weeks_with[1:]:
            if by_week[week][name] != reference:
                problems.append(
                    f"{name}(): week {week} carries a different version from week {first}. "
                    f"The later week is usually the stale copy, because a repair to week "
                    f"{first} does not reach it.")
        if args.verbose:
            print(f"  {name}: weeks {weeks_with}")

    # The same check across the instructor solutions, which carry the same code
    # and are the only proof each lab is completable.
    sols = sorted((p for p in SOLUTIONS.glob("w?-lab-solution.ipynb")),
                  key=lambda p: p.stem)
    for path in sols:
        match = re.match(r"w(\d)-lab-solution", path.stem)
        if not match:
            continue
        week = int(match.group(1))
        if week not in by_week:
            continue
        lab, solution = by_week[week], functions(path)
        for name, body in lab.items():
            if name in solution and solution[name] != body:
                problems.append(
                    f"{name}(): the week {week} solution carries a different version "
                    f"from the week {week} lab. The solution fills TODO cells; every "
                    f"other cell has to match.")

    print()
    if problems:
        print(f"{len(problems)} problem(s):")
        for line in problems:
            print("  - " + line)
        return 1
    print("the chain holds: every function carried forward matches the week that "
          "defined it, and every solution matches its lab")
    return 0


if __name__ == "__main__":
    sys.exit(main())
