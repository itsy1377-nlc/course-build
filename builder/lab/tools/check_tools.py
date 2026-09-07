#!/usr/bin/env python3
"""
check_tools.py: prove that triage_tools.py agrees with the corpus manifest.

The manifest, corpus/spec/corpus-spec.json, records for every email the exact
result each of the three tools must return. This checker walks all 56 records,
calls the three tools with that record's own inputs, and compares the answers
field by field with the manifest.

Run it from anywhere:

    python3 builder/lab/tools/check_tools.py

Output is one line per mismatch, naming the record id, the tool, the field, the
expected value and the actual value. Exit status 1 means the tools and the
manifest disagree, so nothing built on them can be trusted yet. Exit status 0
means all 56 records agree on every field.

This checker is for the course build. Students never run it.

Only the Python standard library is used.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Import triage_tools from the folder this file sits in.
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import triage_tools


def find_manifest():
    """Return the path to corpus-spec.json, or raise a clear error."""
    candidates = []
    from_variable = os.environ.get("CORPUS_SPEC")
    if from_variable:
        candidates.append(from_variable)
    candidates.append(
        os.path.join(HERE, os.pardir, os.pardir, "corpus", "spec", "corpus-spec.json"))
    candidates.append(
        os.path.join(os.getcwd(), "builder", "corpus", "spec", "corpus-spec.json"))
    candidates.append(os.path.join(os.getcwd(), "corpus", "spec", "corpus-spec.json"))
    for candidate in candidates:
        path = os.path.abspath(candidate)
        if os.path.exists(path):
            return path
    places = ", ".join(candidates)
    raise FileNotFoundError("could not find corpus-spec.json. Looked in: " + places)


def show(value):
    """Render one value for a mismatch line, compactly and unambiguously."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def compare(record_id, tool_name, expected, actual, problems):
    """Compare two dictionaries field by field and record every difference."""
    if not isinstance(actual, dict):
        problems.append(
            "%s | %s | <whole result> | expected a dict | got %s"
            % (record_id, tool_name, show(actual)))
        return
    fields = []
    for field in expected:
        fields.append(field)
    for field in actual:
        if field not in fields:
            fields.append(field)
    for field in fields:
        if field not in expected:
            problems.append(
                "%s | %s | %s | expected <field absent> | actual %s"
                % (record_id, tool_name, field, show(actual[field])))
        elif field not in actual:
            problems.append(
                "%s | %s | %s | expected %s | actual <field absent>"
                % (record_id, tool_name, field, show(expected[field])))
        elif expected[field] != actual[field]:
            problems.append(
                "%s | %s | %s | expected %s | actual %s"
                % (record_id, tool_name, field, show(expected[field]), show(actual[field])))


def check_record(record, problems):
    """Run all three tools against one manifest record."""
    record_id = record["id"]
    expectations = record["tool_expectations"]

    compare(record_id, "check_sender_reputation",
            expectations["check_sender_reputation"],
            triage_tools.check_sender_reputation(record["sender_address"]),
            problems)

    compare(record_id, "check_urls",
            expectations["check_urls"],
            triage_tools.check_urls(record["url_hosts"]),
            problems)

    compare(record_id, "lookup_recipient",
            expectations["lookup_recipient"],
            triage_tools.lookup_recipient(record["recipient"]),
            problems)


def main():
    manifest_path = find_manifest()
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    records = manifest["emails"]

    problems = []
    for record in records:
        check_record(record, problems)

    print("manifest:   " + manifest_path)
    print("data files: " + triage_tools.find_data_directory())
    print("records:    %d" % len(records))
    print("")

    if problems:
        for line in problems:
            print(line)
        print("")
        print("check_tools: %d mismatch(es) across %d records" % (len(problems), len(records)))
        return 1

    print("check_tools: %d records, all three tools agree with the manifest on every field"
          % len(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
