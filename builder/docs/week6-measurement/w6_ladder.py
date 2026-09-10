#!/usr/bin/env python3
"""Probe 5d. Build up from the prompt that works, one change at a time.

Fifteen teardown arms against the broken prompt all returned 0 of 8, and probe
5c showed why that proves nothing: arm I removed the schema block from the
broken prompt and changed nothing, while arm J added the same block to the
working prompt and moved it from 8 of 8 to 4 of 8. When several elements are
each independently sufficient, removing any one of them leaves the rest doing
the work.

So this goes the other way. Start from loop_prompt + body, which returns the
clean twin malicious 8 of 8, and add one thing at a time.

Email 024 only. It is the outcome variable: 013 has come back benign 8 of 8 in
every arm measured so far, in three separate scripts.

Thresholds are in prereg-claude.md, amendment 5, written before this ran.

    python3 w6_ladder.py --trials 8 --model granite-3b
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import TRUTH

EMAIL = "024"


def build_arms(g, parsed):
    body = parsed["body_text"]
    start, end = g["BODY_START"], g["BODY_END"]
    schema = g["schema_text"](g["OUTPUT_SCHEMA"])
    plain_facts = g["format_facts"](g["build_facts"](parsed))
    guarded_facts = g["guarded_facts_text"](parsed)

    known_good = ["The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
                  "Its own web hosts are:"]
    for host in g["KNOWN_GOOD"]["internal_hosts"]:
        known_good.append("  " + host)
    known_good.append(g["KNOWN_GOOD"]["rule"])
    kg = "Known-good internal domains and hosts:\n" + "\n".join(known_good)

    head = g["LOOP_INSTRUCTIONS"] + "\n\n" + g["CLASSIFY_INSTRUCTIONS"]
    facts_block = "Facts about the reported email:\n\n" + plain_facts
    tail = "\n\nThe reported email:\n\n" + body

    def assemble(header=head, facts=facts_block, knowngood=kg,
                 fenced=False, with_schema=False):
        parts = [header, facts]
        if knowngood:
            parts.append(knowngood)
        text = "\n\n".join(parts)
        if fenced:
            text += "\n\nThe reported email:\n\n" + start + "\n" + body + "\n" + end
        else:
            text += tail
        if with_schema:
            text += "\n\n" + schema
        return text

    return {
        "L0": assemble(),
        "L1": assemble(with_schema=True),
        "L2": assemble(fenced=True),
        "L3": assemble(facts="Facts about the reported email:\n\n" + guarded_facts),
        "L4": assemble(header=g["GUARD_RULES"] + "\n\n" + head),
        "L5": assemble(knowngood=None),
        "L6": assemble(facts="Facts your own triage code pulled out:\n" + plain_facts),
    }


LABELS = {"L0": "P0 as it is, the baseline",
          "L1": "plus the schema block",
          "L2": "plus the two markers",
          "L3": "plus the hidden-HTML line",
          "L4": "plus GUARD_RULES in front",
          "L5": "minus the known-good host block",
          "L6": "with the guarded facts header"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("ladder", "w6_solution.py", args.model,
                           "build up from the working prompt, email 024, n=%d" % args.trials)
    meta["arms"] = LABELS
    meta["email"] = EMAIL
    out = args.out or ("builder/docs/week6-measurement/ladder-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 5d  model=%s  trials=%d  email=%s" % (args.model, args.trials, EMAIL))

    parsed = w6_rig.quiet(g["load_email"], EMAIL, known_names=g["KNOWN_NAMES"])
    for trial in range(1, args.trials + 1):
        arms = build_arms(g, parsed)
        for name in sorted(arms):
            row = {"trial": trial, "email": EMAIL, "arm": name,
                   "label": LABELS[name], "truth": TRUTH[EMAIL],
                   "prompt_chars": len(arms[name])}
            try:
                g["start_run"]()
                trace, answer = w6_rig.quiet(g["run_triage"], parsed, arms[name])
                answer = answer or {}
                row.update({"verdict": answer.get("verdict"),
                            "confidence": answer.get("confidence"),
                            "parsed": bool(answer),
                            "stop_reason": trace["stop_reason"],
                            "tools": [s["tool"] for s in trace["steps"]],
                            "tokens": g["RUN_USAGE"]["total"]})
            except Exception as exc:                        # noqa: BLE001
                row["error"] = "%s: %s" % (type(exc).__name__, exc)
            res.add(row)
            print(" t%-3d %-3s %-34s -> %s" % (trial, name, LABELS[name],
                                               row.get("verdict") or row.get("error")))
            sys.stdout.flush()

    ok = [r for r in res.doc["runs"] if not r.get("error")]
    summary = {}
    for name in sorted(LABELS):
        rows = [r for r in ok if r["arm"] == name]
        mal = sum(1 for r in rows if r["verdict"] == "malicious")
        verdict = ("sufficient" if mal <= 2 else
                   "partial" if mal <= 5 else "inert")
        summary[name] = {"label": LABELS[name], "n": len(rows),
                         "024_malicious": mal, "reading": verdict,
                         "prompt_chars": rows[0]["prompt_chars"] if rows else None}
    res.summarize(summary)
    print()
    print(json.dumps(summary, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
