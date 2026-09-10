#!/usr/bin/env python3
"""Probe 5c. Is the doubled schema block what collapses the clean twin?

Probes 5 and 5b refuted seven candidate causes. Every arm ran the same three
tools in the same order and ended tools_exhausted, so the evidence is identical
and the cause is in the prompt text. Two differences are left between the arm
that works and every arm that does not: the guarded arms end prompt_text with
schema_text(OUTPUT_SCHEMA), which run_triage() then appends a second time, and
loop_prompt() carries no schema at all.

  I  the shipped guarded prompt with the schema block taken out
  J  the working undefended prompt with a schema block put in
  P0 and A re-run here, so all four come from one script and one rig

Thresholds are in prereg-claude.md, amendment 4, written before this ran.

    python3 w6_schema.py --trials 8 --model granite-3b
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
    p0 = g["loop_prompt"](parsed) + "\n\nThe reported email:\n\n" + body
    return {
        "P0": p0,
        "A": "\n\n".join([g["GUARD_RULES"], label + facts, fenced, schema]),
        "I": "\n\n".join([g["GUARD_RULES"], label + facts, fenced]),
        "J": p0 + "\n\n" + schema,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("schema-block", "w6_solution.py", args.model,
                           "P0, A, I and J on the twin pair, n=%d" % args.trials)
    meta["arms"] = {"P0": "loop_prompt + body, the arm that works",
                    "A": "the shipped guarded prompt",
                    "I": "A with the schema block removed",
                    "J": "P0 with a schema block added"}
    out = args.out or ("builder/docs/week6-measurement/schema-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 5c  model=%s  trials=%d" % (args.model, args.trials))

    parsed = {e: w6_rig.quiet(g["load_email"], e, known_names=g["KNOWN_NAMES"])
              for e in EMAILS}
    for trial in range(1, args.trials + 1):
        for eid in EMAILS:
            arms = build_arms(g, parsed[eid])
            for name in ("P0", "A", "I", "J"):
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
                                "tools": [s["tool"] for s in trace["steps"]],
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
    for name in ("P0", "A", "I", "J"):
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
