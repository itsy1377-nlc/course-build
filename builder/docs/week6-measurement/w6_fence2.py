#!/usr/bin/env python3
"""Probe 5b. Is it the classification instructions?

Probe 5 refuted five candidate causes of the guarded arm's collapse in one
pass: the markers, GUARD_RULES, the hidden-HTML line, prompt length and the
dropped known-good host list. Every arm built as facts-plus-body-plus-schema
returned benign on both twins, including one with neither rules nor markers.
Only P0, the repaired undefended prompt, kept the clean twin malicious.

loop_prompt() is LOOP_INSTRUCTIONS + CLASSIFY_INSTRUCTIONS + facts +
known-good hosts. Arm F restored the last of those and changed nothing. What is
left is CLASSIFY_INSTRUCTIONS, which build_guarded_prompt() replaces with
GUARD_RULES instead of adding to.

  P0  the repaired undefended prompt, re-run here as the baseline
  G   arm A plus CLASSIFY_INSTRUCTIONS
  H   arm A plus LOOP_INSTRUCTIONS only, the discriminating control

Thresholds are in prereg-claude.md, amendment 3, written before this ran.

    python3 w6_fence2.py --trials 8 --model granite-3b
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import TRUTH
from w6_fence import EMAILS


def build_arms(g, parsed):
    body = parsed["body_text"]
    start, end = g["BODY_START"], g["BODY_END"]
    facts = g["guarded_facts_text"](parsed)
    schema = g["schema_text"](g["OUTPUT_SCHEMA"])
    fenced = start + "\n" + body + "\n" + end
    label = "Facts your own triage code pulled out:\n"
    return {
        "P0": g["loop_prompt"](parsed) + "\n\nThe reported email:\n\n" + body,
        "G": "\n\n".join([g["GUARD_RULES"], g["CLASSIFY_INSTRUCTIONS"],
                          label + facts, fenced, schema]),
        "H": "\n\n".join([g["GUARD_RULES"], g["LOOP_INSTRUCTIONS"],
                          label + facts, fenced, schema]),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("classify-instructions", "w6_solution.py", args.model,
                           "P0, G and H on the twin pair, n=%d" % args.trials)
    meta["arms"] = {"P0": "loop_prompt + body",
                    "G": "guarded prompt plus CLASSIFY_INSTRUCTIONS",
                    "H": "guarded prompt plus LOOP_INSTRUCTIONS, the control"}
    out = args.out or ("builder/docs/week6-measurement/classify-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 5b  model=%s  trials=%d" % (args.model, args.trials))

    parsed = {e: w6_rig.quiet(g["load_email"], e, known_names=g["KNOWN_NAMES"])
              for e in EMAILS}
    for trial in range(1, args.trials + 1):
        for eid in EMAILS:
            arms = build_arms(g, parsed[eid])
            for name in ("P0", "G", "H"):
                row = {"trial": trial, "email": eid, "arm": name,
                       "truth": TRUTH[eid], "prompt_chars": len(arms[name])}
                try:
                    g["start_run"]()
                    trace, answer = w6_rig.quiet(g["run_triage"], parsed[eid], arms[name])
                    answer = answer or {}
                    row.update({"verdict": answer.get("verdict"),
                                "confidence": answer.get("confidence"),
                                "parsed": bool(answer),
                                "stop_reason": trace["stop_reason"],
                                "tokens": g["RUN_USAGE"]["total"]})
                except Exception as exc:                    # noqa: BLE001
                    row["error"] = "%s: %s" % (type(exc).__name__, exc)
                res.add(row)
                print(" t%-3d %-4s %-3s -> %-10s %s" % (trial, eid, name,
                                                        row.get("verdict"),
                                                        row.get("error", "")))
                sys.stdout.flush()

    ok = [r for r in res.doc["runs"] if not r.get("error")]
    summary = {}
    for name in ("P0", "G", "H"):
        counts = {}
        for eid in EMAILS:
            c = {}
            for r in ok:
                if r["arm"] == name and r["email"] == eid:
                    c[str(r["verdict"])] = c.get(str(r["verdict"]), 0) + 1
            counts[eid] = c
        summary[name] = {
            "verdicts": counts,
            "024_malicious": sum(1 for r in ok if r["arm"] == name
                                 and r["email"] == "024" and r["verdict"] == "malicious"),
            "013_benign": sum(1 for r in ok if r["arm"] == name
                              and r["email"] == "013" and r["verdict"] == "benign"),
            "prompt_chars": next((r["prompt_chars"] for r in ok if r["arm"] == name), None),
        }
    res.summarize(summary)
    print()
    print(json.dumps(summary, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
