"""Run every gate, in one command, and say plainly what failed.

    python -m tools.preflight              everything
    python -m tools.preflight --fast       skip the lab test suite

There are five gates now and they grew one at a time, which means somebody
running only the one they remember can ship a course that fails the other four.
This runs all of them.

    1. Reading level and page length      tools/readability
    2. Content against code               tools/verify_content
    3. Course structure and cartridge     tools/cartridge --check
    4. The lab autograder, worked         labs/, with the solution applied
    5. The student repository is clean    labs/scripts/build_student_repo

Gate 4 is the one worth explaining. It applies the worked solution, runs the
autograder, and puts everything back. An autograder nobody has satisfied is not
an assessment, it is a rumor, and the only way to know it is satisfiable is to
satisfy it. It has caught a broken assertion twice.

Gate 5 exists because the working repository contains the complete answer to
every graded extension point, and three README files promised that would not
reach students. A promise is not a control.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABS = ROOT / "labs"

BOLD, DIM, RED, GREEN, RESET = "\033[1m", "\033[2m", "\033[31m", "\033[32m", "\033[0m"


def run(label: str, args: list[str], cwd: Path = ROOT,
        env_extra: dict[str, str] | None = None) -> tuple[bool, str]:
    import os
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    started = time.time()
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, env=env)
    elapsed = time.time() - started
    ok = result.returncode == 0
    mark = f"{GREEN}pass{RESET}" if ok else f"{RED}FAIL{RESET}"
    print(f"  {mark}  {label:44} {elapsed:5.1f}s")
    return ok, (result.stdout + result.stderr)


def python_for(directory: Path) -> str:
    """Use a directory's own virtual environment when it has one."""
    candidate = directory / ".venv" / "bin" / "python"
    return str(candidate) if candidate.exists() else sys.executable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fast", action="store_true",
                        help="Skip the lab autograder, which needs the target app.")
    args = parser.parse_args(argv)

    print(f"\n{BOLD}ITSY 1377 preflight{RESET}\n")
    failures: list[tuple[str, str]] = []
    lab_python = python_for(LABS)
    # The video pipeline lives in its own environment because it pulls torch,
    # and tools/requirements.txt is deliberately two small pure-python packages.
    video_python = python_for(ROOT / "tools" / "video")

    checks = [
        ("reading level and page length", [sys.executable, "-m", "tools.readability"], ROOT, None),
        ("content agrees with the code", [sys.executable, "-m", "tools.verify_content"], ROOT, None),
        ("course structure and cartridge", [sys.executable, "-m", "tools.cartridge", "--check"], ROOT, None),
        ("the worked solution still applies", [lab_python, "demo/apply_solution.py", "check"], LABS, None),
        ("student repository has no answers", [lab_python, "scripts/build_student_repo.py",
                                               str(ROOT / "build" / "student-check"), "--force"], LABS, None),
    ]

    # Only worth running when the pipeline is installed. A contributor who has
    # not built any video should not be blocked by a gate about video.
    # The course tree is chosen by ITSY_CONTENT, exactly as it is for every
    # other gate. A hardcoded content/video pointed at no tree at all when a
    # course lived somewhere else, so the video gate stayed silent instead of
    # failing on pages that embed a video id no scene list produces.
    video_dir = ROOT / os.environ.get("ITSY_CONTENT", "content") / "video"
    if (ROOT / "tools" / "video" / ".venv").exists() and any(video_dir.glob("*.yaml")):
        checks.append(("video is current, captioned, and gives nothing away",
                       [video_python, "-m", "tools.video.check"], ROOT, None))

    for label, command, cwd, env_extra in checks:
        ok, output = run(label, command, cwd, env_extra)
        if not ok:
            failures.append((label, output))

    if not args.fast:
        ok, output = run("the autograder is satisfiable",
                         [lab_python, "-c", _AUTOGRADER_PROBE], LABS,
                         {"LAB_STUDENT_ID": "preflight-check"})
        if not ok:
            failures.append(("the autograder is satisfiable", output))

    print()
    if failures:
        print(f"{RED}{len(failures)} gate(s) failed.{RESET}\n")
        for label, output in failures:
            print(f"{BOLD}{label}{RESET}")
            tail = [line for line in output.splitlines() if line.strip()][-25:]
            for line in tail:
                print(f"  {line}")
            print()
        return 1

    print(f"{GREEN}All gates pass.{RESET}\n")
    return 0


# Applies the worked solution, runs the autograder, and puts everything back,
# even if the tests blow up. Written inline so preflight stays one file.
_AUTOGRADER_PROBE = r"""
import subprocess, sys, os
from pathlib import Path

os.environ.setdefault("LAB_STUDENT_ID", "preflight-check")
python = sys.executable


def sh(*args, **kw):
    return subprocess.run([python, *args], capture_output=True, text=True, **kw)


sh("-m", "target.seed")
app = subprocess.Popen([python, "-m", "target.app"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
applied = False
try:
    import time, urllib.request
    for _ in range(30):
        try:
            urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=1)
            break
        except Exception:
            time.sleep(0.5)

    result = sh("demo/apply_solution.py", "apply")
    if result.returncode != 0:
        print(result.stdout + result.stderr)
        raise SystemExit(1)
    applied = True

    # Run the harness once first. One autograder test checks that a results
    # file exists under this student's own ID, which is the point of that test:
    # you cannot pass Module 3 by reading about the harness.
    harness = sh("-m", "harness.runner")
    if harness.returncode != 0:
        print(harness.stdout[-1500:] + harness.stderr[-500:])
        raise SystemExit(1)

    tests = sh("-m", "pytest", "tests/", "-q")
    print(tests.stdout[-1500:])
    if tests.returncode != 0:
        raise SystemExit(1)
finally:
    if applied:
        sh("demo/apply_solution.py", "revert")
    app.terminate()
"""


if __name__ == "__main__":
    sys.exit(main())
