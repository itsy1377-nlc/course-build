#!/usr/bin/env python3
"""Probe 5e. Put both missing pieces back, and see what the guard then does.

Probe 5d found that removing week 3's known-good host block from the working
prompt collapses the clean twin 0 of 8, while adding the markers, the rules,
the hidden-HTML line or the guarded facts header changes nothing. Two earlier
arms complete the picture: arm F restored the known-good block to the guarded
prompt and did not rescue it, and arm G restored the classification
instructions without the block and did not either. So the verdict holds only
when both are present, and build_guarded_prompt() drops both.

  K   GUARD_RULES + CLASSIFY_INSTRUCTIONS + facts + known-good + fenced body
      + schema, which is the repaired guarded prompt
  K2  the same without the schema block, because probe 5c and probe 5d
      disagree about what the schema does
  P0  the working undefended prompt, re-run as the baseline

The 013 column is the one that decides week 6's headline. Both readings are
registered in prereg-claude.md, amendment 5e, written before this ran.

    python3 w6_restore.py --trials 8 --model granite-3b
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import TRUTH

EMAILS = ["013", "024"]


def build_arms(g, parsed):
    body = parsed["body_text"]
    start, end = g["BODY_START"], g["BODY_END"]
    schema = g["schema_text"](g["OUTPUT_SCHEMA"])
    facts = g["guarded_facts_text"](parsed)

    known_good = ["The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
                  "Its own web hosts are:"]
    for host in g["KNOWN_GOOD"]["internal_hosts"]:
        known_good.append("  " + host)
    known_good.append(g["KNOWN_GOOD"]["rule"])
    kg = "Known-good internal domains and hosts:\n" + "\n".join(known_good)

    fenced = start + "\n" + body + "\n" + end
    label = "Facts your own triage code pulled out:\n"
    core = [g["GUARD_RULES"], g["CLASSIFY_INSTRUCTIONS"], label + facts, kg, fenced]
    return {
        "P0": g["loop_prompt"](parsed) + "\n\nThe reported email:\n\n" + body,
        "K": "\n\n".join(core + [schema]),
        "K2": "\n\n".join(core),
    }


LABELS = {"P0": "the working undefended prompt",
          "K": "guarded, with the instructions and the known-good block back",
          "K2": "the same, without the schema block"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("restore", "w6_solution.py", args.model,
                           "both missing pieces restored, n=%d" % args.trials)
    meta["arms"] = LABELS
    out = args.out or ("builder/docs/week6-measurement/restore-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 5e  model=%s  trials=%d" % (args.model, args.trials))

    parsed = {e: w6_rig.quiet(g["load_email"], e, known_names=g["KNOWN_NAMES"])
              for e in EMAILS}
    for trial in range(1, args.trials + 1):
        for eid in EMAILS:
            arms = build_arms(g, parsed[eid])
            for name in ("P0", "K", "K2"):
                row = {"trial": trial, "email": eid, "arm": name,
                       "label": LABELS[name], "truth": TRUTH[eid],
                       "prompt_chars": len(arms[name])}
                try:
                    g["start_run"]()
                    trace, answer = w6_rig.quiet(g["run_triage"], parsed[eid], arms[name])
                    answer = answer or {}
                    row.update({"verdict": answer.get("verdict"),
                                "confidence": answer.get("confidence"),
                                "parsed": bool(answer),
                                "stop_reason": trace["stop_reason"],
                                "tools": [s["tool"] for s in trace["steps"]],
                                "tokens": g["RUN_USAGE"]["total"]})
                except Exception as exc:                    # noqa: BLE001
                    row["error"] = "%s: %s" % (type(exc).__name__, exc)
                res.add(row)
                print(" t%-3d %-4s %-3s -> %-10s" % (trial, eid, name,
                                                     row.get("verdict") or row.get("error")))
                sys.stdout.flush()

    ok = [r for r in res.doc["runs"] if not r.get("error")]
    summary = {}
    for name in ("P0", "K", "K2"):
        counts = {}
        for eid in EMAILS:
            c = {}
            for r in ok:
                if r["arm"] == name and r["email"] == eid:
                    c[str(r["verdict"])] = c.get(str(r["verdict"]), 0) + 1
            counts[eid] = c
        pairs = differ = 0
        for t in sorted({r["trial"] for r in ok}):
            a = next((r for r in ok if r["arm"] == name and r["email"] == "013" and r["trial"] == t), None)
            b = next((r for r in ok if r["arm"] == name and r["email"] == "024" and r["trial"] == t), None)
            if a and b:
                pairs += 1
                differ += a["verdict"] != b["verdict"]
        summary[name] = {
            "label": LABELS[name], "verdicts": counts,
            "024_malicious": sum(1 for r in ok if r["arm"] == name
                                 and r["email"] == "024" and r["verdict"] == "malicious"),
            "013_malicious": sum(1 for r in ok if r["arm"] == name
                                 and r["email"] == "013" and r["verdict"] == "malicious"),
            "pair_differs": differ, "pairs": pairs,
            "prompt_chars": next((r["prompt_chars"] for r in ok if r["arm"] == name), None),
        }
    res.summarize(summary)
    print()
    print(json.dumps(summary, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
