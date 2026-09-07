#!/usr/bin/env python3
"""Pull every manifest concern the corpus authors raised into one file.

Forty-two agents rendered the corpus, one email each, and every one of them was
told the same thing: if a field in the manifest record looks wrong, REPORT it,
and never quietly change a semantic field. They reported a great deal. This
collects it out of the workflow journal so the concerns can be triaged as
classes rather than one email at a time, which matters because a third of them
are the same bug written thirty-three times.

It reads the journal a workflow run leaves behind, keeps every agent result
that carries manifest_concerns, classifies each concern by the field it is
about, and writes builder/docs/manifest-concerns.json.

Run:
    python3 builder/corpus/tools/collect_concerns.py <journal.jsonl> [more...]
    python3 builder/corpus/tools/collect_concerns.py --find

--find locates the journals itself under the Claude projects directory.
"""

import argparse
import collections
import glob
import json
import os
import re
import sys
from pathlib import Path

BUILDER = Path(__file__).resolve().parents[2]
OUT = BUILDER / "docs" / "manifest-concerns.json"

JOURNAL_GLOB = os.path.expanduser(
    "~/.claude/projects/*/*/subagents/workflows/*/journal.jsonl")

# Ordered, because the first match wins and the earlier patterns are the more
# specific ones. A concern that matches nothing lands in "other", which is the
# bucket a human reads line by line.
CLASSES = [
    ("received_path_hint", r"received_path_hint|\bhops?\b|Received chain"),
    ("indicators", r"\bindicator"),
    ("tool_expectations", r"tool_expectations|sender_reputation|recipients\.json|"
                          r"check_urls|check_sender_reputation|lookup_recipient"),
    ("expected_loop", r"expected_loop|stop_reason|tools_exhausted|step_cap|"
                      r"decisive_(malicious|benign)|internal_sender"),
    ("escalation", r"escalate_expected|escalation_reasons|recommended_action"),
    ("lure_summary", r"lure_summary"),
    ("body_brief", r"body_brief"),
    ("attachment", r"attachment"),
    ("injection", r"injection|payload"),
    ("difficulty", r"difficulty"),
]

# A concern that says this about itself is a note for the record, not a defect.
NOTE = re.compile(r"not an error|not a defect|only a note|flagged only|"
                  r"no change needed|for the record|decision on the record",
                  re.I)

# The six emails the week 5 measurement recorded digests for. A manifest change
# that re-renders any of these invalidates the measurement that chose the model
# and the whole week 5 design. Anything touching them needs saying out loud.
MEASURED = {
    "004-cfo-quick-task",
    "005-slatemoor-past-due-statement",
    "007-larkseal-contract-signature",
    "010-ferncrate-rfq-share",
    "011-po-20431-thread-reply",
    "012-elmhollow-badge-access",
}


def classify(text: str) -> str:
    for name, pattern in CLASSES:
        if re.search(pattern, text, re.I):
            return name
    return "other"


def read_journal(path: str) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "result":
                continue
            result = row.get("result")
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except ValueError:
                    continue
            if isinstance(result, dict) and "manifest_concerns" in result:
                out.append(result)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("journals", nargs="*", help="journal.jsonl files to read")
    parser.add_argument("--find", action="store_true", help="locate journals automatically")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    paths = list(args.journals)
    if args.find or not paths:
        paths += sorted(glob.glob(JOURNAL_GLOB))
    if not paths:
        sys.exit("no journal files found; pass one, or use --find")

    results, seen = [], set()
    for path in paths:
        for result in read_journal(path):
            key = result.get("email_id")
            if key in seen:
                continue
            seen.add(key)
            results.append(result)

    concerns = []
    for result in results:
        email = result.get("email_id", "?")
        for text in result.get("manifest_concerns") or []:
            concerns.append({
                "email": email,
                "measured_by_week5": email in MEASURED,
                "field": classify(text),
                "self_declared_note": bool(NOTE.search(text)),
                "concern": text,
            })

    by_class = collections.Counter(c["field"] for c in concerns)
    notes = sum(1 for c in concerns if c["self_declared_note"])
    touching_measured = sorted({c["email"] for c in concerns if c["measured_by_week5"]})

    payload = {
        "what_this_is": (
            "Every place a corpus author believed the approved manifest record "
            "contradicts itself or contradicts a correct rendering of it. The "
            "authors were told to report rather than change a semantic field, "
            "and they did: no author edited verdict, category, indicators, "
            "url_hosts, tool_expectations, expected_loop, escalate_expected or "
            "recommended_action, and no author edited a data file."),
        "how_to_use_it": (
            "Triage by field, not by email. A third of these are one bug in how "
            "received_path_hint counts hops, written once per email. Fixing the "
            "class fixes them all."),
        "the_constraint": (
            "Emails 004, 005, 007, 010, 011 and 012 have digests recorded inside "
            "docs/week5-model-test.json. A manifest change that re-renders any of "
            "them invalidates the measurement that chose the model and the week 5 "
            "design. build_corpus.py fails on that, but decide it deliberately "
            "rather than discovering it."),
        "emails_reporting": len({c["email"] for c in concerns}),
        "authors_read": len(results),
        "total": len(concerns),
        "self_declared_notes": notes,
        "stated_as_problems": len(concerns) - notes,
        "by_field": dict(by_class.most_common()),
        "concerns_touching_measured_emails": touching_measured,
        "concerns": sorted(concerns, key=lambda c: (c["field"], c["email"])),
    }
    Path(args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(f"read {len(results)} author result(s) from {len(paths)} journal(s)")
    print(f"{len(concerns)} concern(s) from {payload['emails_reporting']} email(s): "
          f"{payload['stated_as_problems']} stated as problems, {notes} self-declared notes")
    for name, count in by_class.most_common():
        print(f"  {count:>4}  {name}")
    if touching_measured:
        print("\nTOUCHES THE WEEK 5 MEASURED EMAILS: " + ", ".join(touching_measured))
    print("\nwrote " + args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
