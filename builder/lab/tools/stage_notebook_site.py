#!/usr/bin/env python3
"""Assemble everything the notebook server should serve, and nothing else.

The notebooks are baked into the site now, so a student opens them instead of
downloading them from Canvas. That makes what goes into this folder a shipping
decision, not a convenience.

It is driven by `student_files` in course.yaml, never by a folder walk.
`corpus/tools` alone is 2.7 MB and holds the generators and corpus-spec.json,
which is the complete answer key. A recursive copy would publish it. Every
name in `never_ship` is checked for by hand afterwards, because an allowlist
is only as good as the last edit to it.

Usage:
    python3 lab/tools/stage_notebook_site.py <output-dir>
"""
import glob
import json
import os
import shutil
import sys
from pathlib import Path

import yaml

BUILDER = Path(__file__).resolve().parents[2]


def project(src: Path, dst: Path, keys: list) -> None:
    """Copy a labelled JSON file carrying only the fields declared for students.

    An answer key is not one decision. `ground_truth_batch.json` is on the
    allowlist for a good reason -- week 7 has students score their own batch
    against it -- and it shipped thirty-four fields per record, including the
    four the note is graded on. The name was checked and the contents were not.
    """
    data = json.loads(src.read_text(encoding="utf-8"))
    records = data.get("emails")
    if not isinstance(records, list):
        raise SystemExit(f"{src.name}: declared keys but holds no 'emails' list")
    dropped = sorted({k for r in records for k in r} - set(keys))
    data["emails"] = [{k: r[k] for k in keys if k in r} for r in records]
    dst.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    saved = src.stat().st_size - dst.stat().st_size
    print(f"  projected {src.name}: kept {keys}, dropped {len(dropped)} field(s), "
          f"{saved/1024:.0f} KB smaller")


def unprojected_labels(out: Path, declared: set) -> list:
    """Any staged JSON holding labelled records that nobody declared keys for."""
    loose = []
    for f in sorted(out.rglob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        records = data.get("emails") if isinstance(data, dict) else None
        if not isinstance(records, list) or not records:
            continue
        fields = {k for r in records if isinstance(r, dict) for k in r}
        telling = fields & {"verdict", "category", "indicators", "required_indicators",
                            "recommended_action", "reference_summary", "escalation_reasons"}
        if telling and str(f.relative_to(out)) not in declared:
            loose.append((str(f.relative_to(out)), sorted(telling)))
    return loose


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    out = Path(argv[1]).resolve()
    spine = yaml.safe_load((BUILDER / "content" / "course.yaml").read_text())
    never = set(spine.get("never_ship") or [])

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    staged = []

    # 1. Every student-facing notebook, at the site root, so the notebook's own
    #    upward path walk lands on the site root as COURSE_DIR.
    for src in sorted((BUILDER / "lab" / "notebooks").glob("*.ipynb")):
        shutil.copy2(src, out / src.name)
        staged.append(src.name)

    # 2. The corpus and tool files the allowlist names.
    for entry in spine.get("student_files") or []:
        if "glob" in entry:
            matches = sorted(glob.glob(str(BUILDER / entry["glob"])))
            if not matches:
                print(f"  WARNING: no files matched {entry['glob']}")
            sources = [Path(m) for m in matches]
        else:
            sources = [BUILDER / entry["path"]]
        for src in sources:
            if not src.is_file():
                print(f"  WARNING: missing {src}")
                continue
            rel = src.relative_to(BUILDER)
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if entry.get("keys"):
                project(src, dst, entry["keys"])
            else:
                shutil.copy2(src, dst)
            staged.append(str(rel))

    # 3. Refuse to hand back a tree holding anything from never_ship.
    leaked = [p for p in staged if Path(p).name in never]
    if leaked:
        print("  REFUSING: never_ship files were staged:")
        for p in leaked:
            print("    " + p)
        shutil.rmtree(out)
        return 1
    # A second look at anything whose NAME reads like an answer key. This does
    # not refuse: corpus/release/ground_truth_batch.json is deliberately given
    # to students, because week 7 has them score their own batch against it.
    # never_ship above is the authority. This exists so a file of that shape
    # cannot be added to the allowlist without somebody reading the line.
    suspicious = [p for p in staged
                  if any(w in Path(p).name.lower() for w in ("solution", "answer", "ground_truth"))]
    for p in suspicious:
        print(f"  NOTE: shipping {p} -- allowlisted on purpose, not in never_ship")

    # A file can carry answers under an innocent name. Refuse any staged JSON
    # holding labelled records unless course.yaml declared which fields ship.
    declared = {e["path"] for e in (spine.get("student_files") or [])
                if e.get("keys") and "path" in e}
    loose = unprojected_labels(out, declared)
    if loose:
        print("  REFUSING: labelled records staged with no declared keys:")
        for name, fields in loose:
            print(f"    {name} carries {fields}")
        shutil.rmtree(out)
        return 1

    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"  staged {len(staged)} file(s), {total/1024:.0f} KB")
    print(f"    notebooks: {sum(1 for p in staged if p.endswith('.ipynb'))}")
    print(f"    emails:    {sum(1 for p in staged if p.endswith('.eml'))}")
    print(f"    other:     {sum(1 for p in staged if not p.endswith(('.ipynb', '.eml')))}")
    print(f"  never_ship checked: {len(never)} name(s), none present")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
