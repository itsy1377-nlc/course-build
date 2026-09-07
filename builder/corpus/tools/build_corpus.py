#!/usr/bin/env python3
"""Build the whole corpus from the generators, then check it.

Every .eml file in this course is rendered by one generator under
tools/generators/. Each generator writes its own .eml, refreshes its own record
in spec/corpus-spec.json, and upserts its own record in ground_truth.json. They
share those two files, so they are run here one at a time, in id order, by one
process. Running them concurrently corrupts both files.

Steps, in order:

  1. Run every generator in id order.
  2. Rebuild spec/phase0-sample-manifest.json from the rendered files.
  3. Write the three ground truth release files under release/.
  4. Validate the rendered corpus, the exam emails, the manifest and the tools.

The three release files exist because ground truth is released at three
different times. release/ground_truth_teaching.json ships in the instructor
package with the weekly answer keys. release/ground_truth_batch.json is
released with the week 7 page, because nothing in the course locks.
release/ground_truth_exam.json stays in the instructor package.

They live under release/ rather than beside ground_truth.json on purpose. The
validator loads corpus/ground_truth.json and corpus/ground_truth_*.json
together and fails a record whose id appears twice, so a split file sitting
next to the master would collide with it on all 56 records. ground_truth.json
stays the working master the generators write to.

Exam-only emails render to builder/instructor/exam-emails/, never under
corpus/emails/, so nothing a student can reach holds them before the exam. The
corpus validator warns that an exam record has no file under emails/; that
warning is expected and this script reports it as expected.

Run:  python3 builder/corpus/tools/build_corpus.py
      python3 builder/corpus/tools/build_corpus.py --no-generate   # check only
      python3 builder/corpus/tools/build_corpus.py --only 008,009  # some emails
"""

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
RELEASE_DIR = os.path.join(CORPUS, "release")
EXAM_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
GENERATORS = os.path.join(HERE, "generators")

SETS = ("teaching", "batch", "exam")

RELEASE_NOTE = {
    "teaching": ("Ground truth for the emails used in weeks 1 to 6. Ships in the "
                 "instructor package with the weekly answer keys. Students never "
                 "receive it."),
    "batch": ("Ground truth for the twenty week 7 batch emails. Released with the "
              "week 7 page, because nothing in this course locks and the week 7 "
              "lab scores against it."),
    "exam": ("Ground truth for the eleven emails reserved for the week 8 final "
             "exam. Stays in the instructor package. Students never receive it, "
             "and the emails themselves ship in builder/instructor/exam-emails/."),
}


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def run(argv, label):
    """Run one command from the repository root. Return (code, output)."""
    proc = subprocess.run(argv, cwd=os.path.dirname(BUILDER),
                          capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out.rstrip("\n"), label


# ---------------------------------------------------------------- generators

def generator_paths(only):
    paths = sorted(glob.glob(os.path.join(GENERATORS, "gen_*.py")))
    if only:
        wanted = {part.strip() for part in only.split(",") if part.strip()}
        paths = [p for p in paths
                 if os.path.basename(p).split("_")[1] in wanted]
    return paths


def one_pass(only, quiet=False):
    """Run every generator once, in id order. Return the failures."""
    paths = generator_paths(only)
    if not quiet:
        print("running " + str(len(paths)) + " generator(s), in id order")
    failures = []
    for path in paths:
        name = os.path.basename(path)
        code, out, _ = run([sys.executable, path], name)
        if code != 0:
            failures.append((name, out))
            if not quiet:
                print("  FAIL " + name)
                for line in out.splitlines()[-6:]:
                    print("       " + line)
        elif not quiet:
            print("  ok   " + name)
    return failures


def generate(only, passes=3):
    """Run the generators until the build stops changing, then report.

    One pass is not enough, and finding that out cost a false pass. A
    generator writes its own prose fields back into spec/corpus-spec.json:
    body_brief, lure_summary and notes. Generators run in id order, so a name
    that gen_033 writes into the manifest is not visible to gen_004 until the
    NEXT run. gen_004 carries a guard that its BEC payee appears in no other
    manifest record, and that guard is load-bearing for the week 5 lesson.

    What that produced: the first build after gen_033 was written came back
    "corpus build clean" while the collision already existed, and the second
    build failed. A single pass can therefore pass on a corpus that is not
    consistent with itself.

    So the pass is repeated until it is clean or nothing is left to converge,
    and a build that needed more than one pass says so. The generators are
    deterministic, so a fixed point is reached or the failure is real.
    """
    failures = one_pass(only)
    if not failures:
        return failures
    for attempt in range(2, passes + 1):
        print("  ... " + str(len(failures)) + " generator(s) failed. A generator's "
              "prose reaches the manifest only on the next pass, so running again "
              "(pass " + str(attempt) + " of " + str(passes) + ")")
        failures = one_pass(only, quiet=True)
        if not failures:
            print("  converged on pass " + str(attempt) + ". Everything is consistent now, "
                  "but a corpus that needs two passes is worth a look: it means a "
                  "generator changed something another generator reads.")
            return failures
    return failures


# ------------------------------------------------------------ release files

def split_ground_truth():
    """Write the three release files from the master and the manifest."""
    spec = load(SPEC_PATH)
    truth = load(GT_PATH)
    by_set = {record["id"]: record["set"] for record in spec["emails"]}

    buckets = {name: [] for name in SETS}
    unknown = []
    for record in truth["emails"]:
        where = by_set.get(record["id"])
        if where not in buckets:
            unknown.append(record["id"])
            continue
        buckets[where].append(record)

    os.makedirs(RELEASE_DIR, exist_ok=True)
    written = []
    for name in SETS:
        records = sorted(buckets[name], key=lambda record: record["id"])
        payload = {
            "schema_version": truth.get("schema_version", "1.0"),
            "generated_for": "ITSY-1377-000 " + name + " release",
            "release_note": RELEASE_NOTE[name],
            "count": len(records),
            "emails": records,
        }
        path = os.path.join(RELEASE_DIR, "ground_truth_" + name + ".json")
        write_json(path, payload)
        written.append((os.path.basename(path), len(records)))
    return written, unknown


def release_readme():
    path = os.path.join(RELEASE_DIR, "README.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(
            "# Ground truth, split by release time\n"
            "\n"
            "These three files are written by `tools/build_corpus.py` from\n"
            "`../ground_truth.json`. Do not edit them by hand. Edit a generator,\n"
            "rerun the build, and they are rewritten.\n"
            "\n"
            "| File | Who gets it, and when |\n"
            "|---|---|\n"
            "| `ground_truth_teaching.json` | The instructor package, with the weekly answer keys. |\n"
            "| `ground_truth_batch.json` | Released with the week 7 page. The week 7 lab scores against it. |\n"
            "| `ground_truth_exam.json` | The instructor package only. The emails ship in `builder/instructor/exam-emails/`. |\n"
            "\n"
            "They sit here rather than beside `ground_truth.json` because the\n"
            "corpus validator loads `ground_truth.json` and `ground_truth_*.json`\n"
            "together and fails any id it sees twice. `ground_truth.json` stays the\n"
            "working master that the generators write to.\n")


# ------------------------------------------------------------------- checks

def rendered_count():
    return len(glob.glob(os.path.join(CORPUS, "emails", "**", "*.eml"), recursive=True))


def exam_count():
    return len(glob.glob(os.path.join(EXAM_DIR, "*.eml")))


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def reproducible(only):
    """Rerun every generator and confirm no rendered file changed."""
    before = {}
    for pattern in (os.path.join(CORPUS, "emails", "**", "*.eml"),
                    os.path.join(EXAM_DIR, "*.eml")):
        for path in glob.glob(pattern, recursive=True):
            before[path] = digest(path)
    failures = generate(only)
    changed = []
    for path, was in before.items():
        if not os.path.exists(path):
            changed.append(os.path.basename(path) + " disappeared")
        elif digest(path) != was:
            changed.append(os.path.basename(path) + " changed on a second run")
    return failures, changed


MEASURED = os.path.join(BUILDER, "docs", "week5-model-test.json")


def measurement_digests_hold():
    """The week 5 model test recorded the sha256 of the six emails it measured.

    Those digests chose the model and the week 5 lab design. If a generator
    changes any of those six files, the measurement no longer describes the
    course. This is the check that catches it, and it is the reason the
    existing fourteen generators are never edited.
    """
    if not os.path.exists(MEASURED):
        return ["week5-model-test.json is missing, so the measured digests cannot be checked"]
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "email_sha256" and isinstance(value, dict):
                    found.append(value)
                else:
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(load(MEASURED))
    if not found:
        return ["week5-model-test.json records no email digests"]
    problems = []
    for recorded in found:
        for email_id, was in recorded.items():
            matches = glob.glob(os.path.join(CORPUS, "emails", "**", email_id + ".eml"),
                                recursive=True)
            if not matches:
                problems.append(email_id + " is measured but no longer rendered")
                continue
            now = digest(matches[0])
            if now != was:
                problems.append(email_id + " changed since the week 5 measurement: "
                                + was[:12] + " became " + now[:12])
    return problems


def checks():
    tools = os.path.join("builder", "corpus", "tools")
    lab = os.path.join("builder", "lab", "tools")
    exam_gt = os.path.join("builder", "corpus", "release", "ground_truth_exam.json")
    return [
        ([sys.executable, os.path.join(tools, "gen_sample_manifest.py")],
         "rebuild the rendered-email manifest"),
        ([sys.executable, os.path.join(tools, "validate_corpus.py"), "--no-dns"],
         "validate the rendered corpus"),
        ([sys.executable, os.path.join(tools, "validate_corpus.py"), "--no-dns",
          "--emails", os.path.join("builder", "instructor", "exam-emails"),
          "--ground-truth", exam_gt],
         "validate the exam emails"),
        ([sys.executable, os.path.join(tools, "check_spec.py")],
         "recompute every derived manifest field"),
        ([sys.executable, os.path.join(lab, "check_tools.py")],
         "the three tools agree with the manifest"),
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build and check the corpus.")
    parser.add_argument("--no-generate", action="store_true",
                        help="skip the generators; check what is already rendered")
    parser.add_argument("--only", help="run only these email numbers, comma separated")
    parser.add_argument("--check-reproducible", action="store_true",
                        help="run every generator twice and fail if any file changed")
    args = parser.parse_args(argv)

    problems = []

    if args.check_reproducible:
        print("== generators, twice ==")
        failures, changed = reproducible(args.only)
        problems += [name + ": " + out.splitlines()[-1] for name, out in failures]
        problems += changed
        if not changed:
            print("every rendered file is byte identical on a second run")
    elif not args.no_generate:
        print("== generators ==")
        failures = generate(args.only)
        problems += [name + ": " + out.splitlines()[-1] for name, out in failures]

    print("\n== release files ==")
    written, unknown = split_ground_truth()
    release_readme()
    for name, count in written:
        print("  " + name + ": " + str(count) + " record(s)")
    if unknown:
        problems.append("ground truth holds " + str(len(unknown))
                        + " record(s) with no manifest record: " + ", ".join(unknown))

    print("\n== checks ==")
    for argv_, label in checks():
        code, out, _ = run(argv_, label)
        last = out.splitlines()[-1] if out.strip() else "(no output)"
        print(("  ok   " if code == 0 else "  FAIL ") + label)
        print("       " + last)
        if code != 0:
            problems.append(label + ": " + last)

    print("\n== the week 5 measurement ==")
    drift = measurement_digests_hold()
    if drift:
        for line in drift:
            print("  FAIL " + line)
        problems += drift
    else:
        print("  ok   the six measured emails are byte identical to what was measured")

    print("\n== totals ==")
    print("  rendered under corpus/emails: " + str(rendered_count()))
    print("  rendered under instructor/exam-emails: " + str(exam_count()))
    print("  generators: " + str(len(generator_paths(None))))

    if problems:
        print("\n" + str(len(problems)) + " problem(s):")
        for line in problems:
            print("  - " + line)
        return 1
    print("\ncorpus build clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
