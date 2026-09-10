#!/usr/bin/env python3
"""The repaired week 6, end to end: all eleven emails, both arms.

Two changes from what ships, and nothing else:

  1. run_triage()'s closing call carries the body of the email the loop ran
     on, so the call that writes the verdict has seen the message. Probe 2.
  2. build_guarded_prompt() builds on top of week 3's grounding instead of
     replacing it: the classification instructions and the known-good host
     block join GUARD_RULES, the facts and the fenced body. Probes 5d and 5e.

This is both the confirmatory run P5e-3 asks for and the "after" table every
week 6 surface will be rewritten against. Run it twice; P2e will not let a
page quote an arm whose two runs disagree by more than one in eight.

    python3 w6_repaired.py --trials 8 --model granite-3b --run 1
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import WEEK6_EMAILS, summarize
from w6_body import patched_source, capture_traces, richer_pair, accuracy


def install_repaired_prompt(g):
    """build_guarded_prompt(), with week 3's grounding kept."""
    known_good = ["The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
                  "Its own web hosts are:"]
    for host in g["KNOWN_GOOD"]["internal_hosts"]:
        known_good.append("  " + host)
    known_good.append(g["KNOWN_GOOD"]["rule"])
    kg = "Known-good internal domains and hosts:\n" + "\n".join(known_good)

    def build_guarded_prompt(facts_text, body):
        parts = [g["GUARD_RULES"],
                 g["CLASSIFY_INSTRUCTIONS"],
                 "Facts your own triage code pulled out:\n" + facts_text,
                 kg,
                 g["BODY_START"] + "\n" + body + "\n" + g["BODY_END"],
                 g["schema_text"](g["OUTPUT_SCHEMA"])]
        return "\n\n".join(parts)

    g["build_guarded_prompt"] = build_guarded_prompt
    return kg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--run", default="1")
    ap.add_argument("--emails", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    emails = args.emails.split(",") if args.emails else WEEK6_EMAILS

    g, meta = w6_rig.start("repaired", "w6_solution.py", args.model,
                           "both repairs in place, n=%d, run %s" % (args.trials, args.run))
    exec(compile(patched_source("body"), "run_triage-patched", "exec"), g)
    capture_traces(g)
    kg = install_repaired_prompt(g)
    meta["repairs"] = {
        "1": "run_triage()'s closing call carries the body",
        "2": "build_guarded_prompt() keeps CLASSIFY_INSTRUCTIONS and the "
             "known-good host block",
    }
    meta["known_good_block"] = kg
    meta["run_label"] = args.run
    meta["emails"] = emails

    out = args.out or ("builder/docs/week6-measurement/repaired-%s-%d-run%s.json"
                       % (args.model, args.trials, args.run))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("repaired week 6  model=%s  trials=%d  run=%s" % (args.model, args.trials, args.run))
    for trial in range(1, args.trials + 1):
        for eid in emails:
            row = richer_pair(g, eid, trial)
            res.add(row)
            print(" t%-3d %-4s plain=%-10s guarded=%-10s esc=%-20s"
                  % (trial, eid,
                     row.get("plain", {}).get("verdict"),
                     row.get("guarded", {}).get("verdict"),
                     row.get("guarded", {}).get("escalate_reason")))
            sys.stdout.flush()

    summary = summarize(res.doc["runs"], g["CONFIDENCE_FLOOR"], g["TOKEN_CAP_PER_RUN"])
    summary["accuracy"] = accuracy(res.doc["runs"])
    res.summarize(summary)
    print()
    print(json.dumps({k: v for k, v in summary.items() if k != "per_email"}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
