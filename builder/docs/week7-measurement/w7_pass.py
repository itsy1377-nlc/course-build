#!/usr/bin/env python3
"""Run one measurement pass of week 7 and write one JSON result file.

    python3 w7_pass.py --set teaching|batch --model NAME --pass-name P --out FILE
                       [--limit N]

The code under test is the solution notebook's own pre-written cells, extracted
by mkprewritten.py. Nothing here restates a function the student runs.

Two refusals, both learned from week 6:

  * The rig will not start unless one live call comes back with non-zero
    tokens. A measurement against a dead endpoint is worse than no measurement,
    because it looks like a result.
  * Every input is digested into the result file: each .eml, both notebooks and
    the rig module. Two passes whose digests differ are not comparable and the
    reader can see that without trusting this script.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", required=True, choices=["teaching", "batch"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--pass-name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rig", required=True, help="dir holding w7_solution.py")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    os.environ["ITSY1377_MODEL"] = args.model
    sys.path.insert(0, args.rig)
    import w7_solution as w7            # noqa: E402  the code under test

    if w7.MODEL != args.model:
        raise SystemExit(f"the notebook read MODEL={w7.MODEL!r}, not {args.model!r}")

    # Refusal 1. One live call, and it has to cost tokens.
    probe = w7.ask_model("Reply with the single word ok.", max_tokens=8)
    used = dict(w7.USAGE)
    if not used.get("total"):
        raise SystemExit(f"the endpoint returned no tokens. probe={probe!r}")
    print(f"live: {args.model} answered {probe!r}, {used['total']} tokens")

    if args.set == "teaching":
        folder = ROOT / "builder/corpus/emails/teaching"
        keyfile = ROOT / "builder/corpus/release/ground_truth_teaching.json"
        skip = {"013"}          # week 7's own check cell runs 013
    else:
        folder = ROOT / "builder/corpus/emails/batch"
        keyfile = ROOT / "builder/corpus/release/ground_truth_batch.json"
        skip = set()

    truth = {}
    for rec in json.load(open(keyfile))["emails"]:
        truth[rec["id"]] = {"verdict": rec["verdict"],
                            "escalate": rec["escalate_expected"],
                            "action": rec["recommended_action"]}

    paths = sorted(p for p in folder.glob("*.eml") if p.stem[:3] not in skip)
    if args.set == "batch":
        paths = w7.list_batch_emails()
    if args.limit:
        paths = paths[:args.limit]

    digests = {"emails": {p.stem: sha(p) for p in paths},
               "w7-lab.ipynb": sha(ROOT / "builder/lab/notebooks/w7-lab.ipynb"),
               "w7-lab-solution.ipynb": sha(
                   ROOT / "builder/instructor/solutions/w7-lab-solution.ipynb"),
               "rig": sha(Path(args.rig) / "w7_solution.py"),
               "this_script": sha(__file__)}

    started = time.time()
    w7.USAGE.update({"prompt": 0, "answer": 0, "total": 0, "calls": 0})
    rows = w7.run_batch(paths)
    seconds = round(time.time() - started, 1)

    # Everything below reads the shipped functions. None of it recomputes.
    counts = w7.score_batch(rows, truth)
    agreed = w7.escalation_agreement(rows, truth)
    fires = w7.guardrail_fires(rows)

    per_email = []
    for row in rows:
        key = truth.get(row["email_id"], {})
        note = w7.write_note(w7.note_values(row), row.get("facts") or {})
        per_email.append({
            "email_id": row["email_id"],
            "verdict": row.get("verdict"),
            "key_verdict": key.get("verdict"),
            "correct": row.get("verdict") == key.get("verdict"),
            "confidence": row.get("confidence"),
            "recommended_action": row.get("recommended_action"),
            "key_action": key.get("action"),
            "control_flag": bool(row.get("escalate")),
            "escalate_reason": row.get("escalate_reason"),
            "schema_problems": row.get("schema_problems"),
            "policy_review": w7.policy_review(row),
            "review_decision": w7.review_decision(row),
            "key_escalate": key.get("escalate"),
            "escalate_agrees": w7.review_decision(row) == bool(key.get("escalate")),
            "stop_reason": row.get("stop_reason"),
            "tokens": row.get("tokens"),
            "note_lines": len(note.splitlines()) if isinstance(note, str) else None,
            "summary": row.get("summary"),
        })

    result = {
        "pass": args.pass_name,
        "set": args.set,
        "model": args.model,
        "endpoint": w7.BASE_URL,
        "temperature": 0.2,
        "request_extras": w7.MODEL_EXTRAS,
        "emails": len(rows),
        "counts": counts,
        "escalation_agreement": agreed,
        "escalation_agreement_rate": round(agreed / len(rows), 3) if rows else None,
        "guardrail_fires": fires,
        "rows_with_no_verdict": len([1 for r in rows if r.get("verdict") is None]),
        "notes_not_six_lines": [e["email_id"] for e in per_email
                                if e["note_lines"] != 6],
        "schema_problem_rows": [e["email_id"] for e in per_email
                                if e["schema_problems"]],
        "session_tokens": dict(w7.USAGE),
        "seconds": seconds,
        "answer_key": keyfile.name,
        "answer_key_version": w7.ANSWER_KEY_VERSION,
        "input_digests": digests,
        "per_email": per_email,
    }
    Path(args.out).write_text(json.dumps(result, indent=1))
    c = counts
    print(f"\n{args.pass_name} [{args.model} / {args.set}] "
          f"correct {c['correct']}/{len(rows)} acc {c['accuracy']:.3f} "
          f"fp {c['false_positives']} fn {c['false_negatives']} "
          f"nd {c['no_decision']} | escalation agreement {agreed}/{len(rows)} "
          f"| {seconds}s | fires {fires}")


if __name__ == "__main__":
    main()
