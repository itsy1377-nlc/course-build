#!/usr/bin/env python3
"""Rebuild spec/phase0-sample-manifest.json from the rendered .eml files.

The manifest is the integrity record for the rendered corpus: one row per
rendered file, carrying the byte count and the SHA-256 digest of that file plus
the category, verdict and difficulty the manifest in spec/corpus-spec.json
assigns it. Nothing here is typed by hand. Every row is computed from the file
on disk and from spec/corpus-spec.json, so a row can never claim a digest the
file does not have and can never claim a label the manifest does not carry.

The rule the file has to satisfy, and the rule tools/validate_corpus.py
enforces on every run: the manifest covers every rendered .eml under
corpus/emails, no more and no less, and each recorded byte count and digest
equals the file.

Run:  python3 corpus/tools/gen_sample_manifest.py
      python3 corpus/tools/gen_sample_manifest.py --check

--check writes nothing. It rebuilds the manifest in memory, compares it with
the file on disk and exits 1 on any difference, which is what a build step
wants.
"""

import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.dirname(HERE)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
MANIFEST_PATH = os.path.join(CORPUS, "spec", "phase0-sample-manifest.json")
EMAILS_DIR = os.path.join(CORPUS, "emails")

MANIFEST_NOTE = ("ITSY-1377-000 rendered emails, every rendered .eml file "
                 "under corpus/emails, not only the Phase 0 sample")
FILE_NOTE = ("file is the path relative to the corpus folder, the same path "
             "the ground truth file field carries: emails/teaching/<id>.eml "
             "for the teaching set and emails/batch/<id>.eml for the batch "
             "set. bytes and sha256 are computed over the raw file.")
RENDERED = "2026-09-03"

FIELDS = ("id", "file", "set", "bytes", "sha256", "category", "verdict", "difficulty")


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def rendered_files():
    """Every rendered file under corpus/emails, id to path, sorted by id.

    A file may be named <id>.eml or <id>.eml.txt; the second form exists so a
    learning system that refuses .eml uploads can still serve the file. Either
    way the id is the stem and the recorded path is the .eml name, which is the
    path the ground truth file field carries.
    """
    found = {}
    for root, dirs, names in os.walk(EMAILS_DIR):
        dirs.sort()
        for name in sorted(names):
            if name.endswith(".eml.txt"):
                stem = name[:-8]
            elif name.endswith(".eml"):
                stem = name[:-4]
            else:
                continue
            path = os.path.join(root, name)
            if stem in found:
                raise SystemExit("two rendered files carry the id " + stem)
            found[stem] = path
    return dict(sorted(found.items()))


def relative(path):
    rel = os.path.relpath(path, CORPUS).replace(os.sep, "/")
    if rel.endswith(".eml.txt"):
        rel = rel[:-4]
    return rel


def build():
    spec = load(SPEC_PATH)
    spec_records = {record["id"]: record for record in spec["emails"]}
    truth = {}
    if os.path.exists(GT_PATH):
        truth = {record["id"]: record for record in load(GT_PATH)["emails"]}

    rows = []
    for email_id, path in rendered_files().items():
        record = spec_records.get(email_id)
        if record is None:
            raise SystemExit(email_id + ": rendered but absent from spec/corpus-spec.json")
        with open(path, "rb") as handle:
            raw = handle.read()
        row = {
            "id": email_id,
            "file": relative(path),
            "set": record["set"],
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "category": record["category"],
            "verdict": record["verdict"],
            "difficulty": record["difficulty"],
        }
        label = truth.get(email_id)
        if label is not None:
            for field in ("set", "category", "verdict", "difficulty"):
                if label.get(field) != row[field]:
                    raise SystemExit(email_id + ": ground truth " + field + " is "
                                     + str(label.get(field)) + " but the manifest says "
                                     + str(row[field]))
            if label.get("file") not in (None, row["file"]):
                raise SystemExit(email_id + ": ground truth file field is "
                                 + str(label.get("file")) + " but the file is at " + row["file"])
        rows.append({field: row[field] for field in FIELDS})

    previous = load(MANIFEST_PATH) if os.path.exists(MANIFEST_PATH) else {}
    return {
        "manifest": MANIFEST_NOTE,
        "spec_version": spec["spec_version"],
        # The render date belongs to the corpus, not to this run: every file is
        # rebuilt byte for byte from the seed, so re-running a generator does
        # not make the corpus newer. The value already on disk is kept.
        "rendered": previous.get("rendered", RENDERED),
        "ground_truth_file": "ground_truth.json",
        "file_note": FILE_NOTE,
        "count": len(rows),
        "emails": rows,
    }


def main(argv):
    parser = argparse.ArgumentParser(description="Rebuild the rendered-email integrity manifest.")
    parser.add_argument("--check", action="store_true",
                        help="compare with the file on disk and exit 1 on any difference")
    args = parser.parse_args(argv)

    manifest = build()
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        on_disk = open(MANIFEST_PATH, encoding="utf-8").read() if os.path.exists(MANIFEST_PATH) else ""
        if on_disk != text:
            print("gen_sample_manifest: spec/phase0-sample-manifest.json is out of date; "
                  "run this script without --check")
            return 1
        print("gen_sample_manifest: " + str(manifest["count"]) + " row(s), manifest matches the rendered files")
        return 0

    with open(MANIFEST_PATH, "w", encoding="utf-8") as handle:
        handle.write(text)
    print("wrote " + MANIFEST_PATH + " with " + str(manifest["count"]) + " row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
