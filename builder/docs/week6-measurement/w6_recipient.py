#!/usr/bin/env python3
"""Probe 3. Hold the recipient still, and see whether the payload effect stays.

With the body back in the verdict call, granite-3b calls 013 benign 8 of 8 and
024 malicious 8 of 8. That is the demonstration objective 6.2 asks for -- if
the paragraph is what did it.

It may not be. The twins do not share a mailbox. 013 goes to
t.nkemelu@pellgrave.example and 024 to payroll@pellgrave.example, and
recipients.json gives the first 5 prior reports in 90 days, three of them true
positives and one tagged credential-phish, against the second's 2 on a shared
mailbox. start_messages() pastes the bare address into every turn, run_tool()
passes it to lookup_recipient, and run_triage() re-runs every tool and puts the
whole record into the closing call. So the pair varies the paragraph AND a fact
about who was targeted, in the direction that makes 013 look worse.

Two arms, each holding the recipient constant across the pair:

  both_person   013 and 024 both addressed to t.nkemelu@pellgrave.example
  both_shared   013 and 024 both addressed to payroll@pellgrave.example

Only parsed["to"] changes. No corpus file is touched. Probe 2's own rows are
the unswapped control.

    python3 w6_recipient.py --trials 8 --model granite-3b
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import TRUTH
from w6_body import patched_source, capture_traces, CAPTURED

PAIR = ["013", "024"]
ADDRESSES = {"both_person": "t.nkemelu@pellgrave.example",
             "both_shared": "payroll@pellgrave.example"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("recipient-held", "w6_solution.py", args.model,
                           "the twin pair with one recipient, n=%d" % args.trials)
    # The repair under test is in place, because the question is whether the
    # effect probe 2 measured survives, and probe 2 measured it with the body
    # in the closing call.
    exec(compile(patched_source("body"), "run_triage-patched", "exec"), g)
    capture_traces(g)
    meta["patch_arm"] = "body"
    meta["arms"] = ADDRESSES

    out = args.out or ("builder/docs/week6-measurement/recipient-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 3  model=%s  trials=%d" % (args.model, args.trials))

    for trial in range(1, args.trials + 1):
        for arm, address in ADDRESSES.items():
            for eid in PAIR:
                row = {"trial": trial, "arm": arm, "email": eid,
                       "truth": TRUTH[eid], "recipient": address}
                try:
                    parsed = dict(w6_rig.quiet(g["load_email"], eid,
                                               known_names=g["KNOWN_NAMES"]))
                    row["own_recipient"] = (parsed["to"] or [None])[0]
                    parsed["to"] = [address]
                    del CAPTURED[:]
                    g["start_run"]()
                    trace, answer = w6_rig.quiet(g["run_triage"], parsed,
                                                 g["loop_prompt"](parsed))
                    answer = answer or {}
                    row.update({"verdict": answer.get("verdict"),
                                "confidence": answer.get("confidence"),
                                "parsed": bool(CAPTURED and CAPTURED[0]["answer_parsed"]),
                                "stop_reason": trace["stop_reason"],
                                "tools": [s["tool"] for s in trace["steps"]],
                                "tokens": g["RUN_USAGE"]["total"]})
                except Exception as exc:                    # noqa: BLE001
                    row["error"] = "%s: %s" % (type(exc).__name__, exc)
                res.add(row)
                print(" t%-3d %-12s %-4s -> %-10s %s"
                      % (trial, arm, eid, row.get("verdict"), row.get("error", "")))
                sys.stdout.flush()

    ok = [r for r in res.doc["runs"] if not r.get("error")]
    summary = {"per_arm": {}}
    for arm in ADDRESSES:
        rows = [r for r in ok if r["arm"] == arm]
        counts = {}
        for eid in PAIR:
            c = {}
            for r in rows:
                if r["email"] == eid:
                    c[str(r["verdict"])] = c.get(str(r["verdict"]), 0) + 1
            counts[eid] = c
        pairs = 0
        differ = 0
        parsed_pairs = 0
        for t in sorted({r["trial"] for r in rows}):
            a = next((r for r in rows if r["email"] == "013" and r["trial"] == t), None)
            b = next((r for r in rows if r["email"] == "024" and r["trial"] == t), None)
            if a and b:
                pairs += 1
                if a["parsed"] and b["parsed"]:
                    parsed_pairs += 1
                    differ += a["verdict"] != b["verdict"]
        summary["per_arm"][arm] = {
            "recipient": ADDRESSES[arm], "verdicts": counts,
            "pairs": pairs, "pairs_both_parsed": parsed_pairs,
            "verdict_differs": differ,
            "P3a_bar": "6 of %d" % parsed_pairs,
            "013_benign": sum(1 for r in rows if r["email"] == "013" and r["verdict"] == "benign"),
            "024_malicious": sum(1 for r in rows if r["email"] == "024" and r["verdict"] == "malicious"),
        }
    res.summarize(summary)
    print()
    print(json.dumps(summary, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
