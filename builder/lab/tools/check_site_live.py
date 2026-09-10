#!/usr/bin/env python3
"""Prove the served notebook site is the tree this repository would ship.

THE DEFECT THIS EXISTS FOR. Canvas hands students an ExternalUrl per notebook,
pointing at notebook.bashtion.dev. So the repository is not what a student
opens -- the site is. Twice now a week has been finished, pushed to Canvas and
reported done while the site still served the previous notebook:

  - the blind student run on 2026-09-08 found w7-lab.ipynb a revision behind,
    missing a committed fix, and nothing reported it;
  - week 6 on 2026-09-10 was pushed to Canvas with the site still serving the
    pre-repair w6-lab.ipynb, 112,028 bytes against 121,538.

Both were found by hand, by someone who happened to look. Every other gate in
this course passed in both cases, because every other gate reads the
repository, and the repository was right.

WHAT THIS ASSERTS, over the live site:

  1. Every file stage_notebook_site.py would ship is served, byte for byte.
     The comparison is sha256, not length: a same-size edit is the easy way to
     be wrong here.
  2. Nothing named in never_ship is reachable. An allowlist is only as good as
     the last edit to it, and the site is the place where a mistake reaches a
     student.
  3. No solution notebook is reachable, by name, whatever the allowlist says.

Run:
    python3 builder/lab/tools/check_site_live.py
    python3 builder/lab/tools/check_site_live.py --site <staged dir>
    python3 builder/lab/tools/check_site_live.py --base https://host --jobs 8

Exit 0 when the site matches, 1 when it does not. A network failure is a
failure: a gate that passes when it cannot see the thing it checks is worse
than no gate.
"""
import argparse
import concurrent.futures as futures
import hashlib
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE = "https://notebook.bashtion.dev"
TIMEOUT = 30


def stage_temporary():
    """Build the tree this repository would ship, into a scratch directory."""
    # The stager sits beside this file. An earlier version built the path from
    # ROOT, which is already builder/, and asked for builder/builder/lab/...
    # It never fired, because the one green run passed --site and skipped this
    # branch entirely. Same shape as every other defect this round: a code path
    # no check entered.
    out = Path(tempfile.mkdtemp(prefix="site-live-"))
    stager = Path(__file__).resolve().with_name("stage_notebook_site.py")
    if not stager.exists():
        raise SystemExit(f"cannot stage: {stager} is missing")
    done = subprocess.run([sys.executable, str(stager), str(out)],
                          capture_output=True, text=True)
    if done.returncode != 0:
        # A bare CalledProcessError hides the stager's own message, which is
        # the one that says what is actually wrong.
        raise SystemExit("staging the site failed:\n"
                         + (done.stderr or done.stdout or "").strip())
    return out


def fetch(url):
    """Return (status, body). A refused connection is a status, not a crash."""
    request = urllib.request.Request(url, headers={"User-Agent": "itsy1377-site-check"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as reply:
            return reply.status, reply.read()
    except urllib.error.HTTPError as problem:
        return problem.code, b""
    except Exception as problem:                            # noqa: BLE001
        return 0, str(problem).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=None,
                        help="a staged tree. Default: stage one now.")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument("--jobs", type=int, default=8)
    args = parser.parse_args()

    site = Path(args.site).resolve() if args.site else stage_temporary()
    base = args.base.rstrip("/")
    staged = sorted(p for p in site.rglob("*") if p.is_file())
    print("staged tree:", site)
    print("site:       ", base)
    print("files:      ", len(staged))

    # A gate that passes when it has nothing to compare is worse than no gate.
    # This one did exactly that once, on a tree a failed download left empty,
    # and reported the site correct. Assert the tree before trusting a pass.
    notebooks = [p for p in staged if p.suffix == ".ipynb"]
    if len(staged) < 50 or len(notebooks) < 15:
        print()
        print("refusing to run: the staged tree holds %d file(s) and %d notebook(s), "
              "and this course ships 73 and 15." % (len(staged), len(notebooks)))
        print("Stage it again before reading anything into a pass.")
        return 1

    problems = []

    def one(path):
        rel = path.relative_to(site).as_posix()
        status, body = fetch(base + "/files/" + rel)
        if status != 200:
            return ("missing", rel, "http %s" % status)
        if digest(body) != digest(path.read_bytes()):
            return ("different", rel,
                    "served %d bytes, staged %d" % (len(body), path.stat().st_size))
        return None

    with futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for found in pool.map(one, staged):
            if found:
                problems.append(found)

    # 2 and 3. What must never be reachable, checked by asking for it.
    never = ["corpus/spec/corpus-spec.json", "corpus/ground_truth.json",
             "corpus/release/ground_truth_teaching.json",
             "corpus/release/ground_truth_exam.json"]
    never += [p.name.replace("-lab.ipynb", "-lab-solution.ipynb")
              for p in staged if p.name.endswith("-lab.ipynb")]
    for rel in sorted(set(never)):
        status, _ = fetch(base + "/files/" + rel)
        if status == 200:
            problems.append(("reachable", rel, "served 200 and must not be"))

    print()
    if not problems:
        print("check_site_live: the site serves exactly the tree this repository "
              "would ship, and nothing it must not")
        return 0
    print("%d problem(s):" % len(problems))
    for kind, rel, detail in problems:
        print("  %-10s %-58s %s" % (kind, rel, detail))
    print()
    print("Re-stage and deploy before calling the week done. Canvas points "
          "students at this site, so the repository being right is not enough.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
