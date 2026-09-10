#!/usr/bin/env python3
"""Probe 9. The confirmatory 2x2, through the real guarded_triage().

Probe 5d was exploratory: it was designed after three registered hypotheses
failed, and it built prompt strings by hand. This runs the whole shipped
guarded path -- fact check, confidence floor, token cap, escalation -- and
varies only what build_guarded_prompt() puts in front of the model.

Six arms. Four are the 2x2 on the two elements that interact; two are placebos
that separate the known-good block's content from its mere presence.

Thresholds are in prereg-claude.md, amendment 7, written before this ran.

    python3 w6_factorial.py --trials 8 --model granite-3b
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import TRUTH
from w6_body import patched_source, capture_traces, CAPTURED

EMAILS = ["013", "024", "012"]

# Placebo N. Length matched to the real known-good block, naming no real host.
NEUTRAL_BLOCK = """Notes on how this queue records hosts:
Each reported message is logged with the hosts it mentions.
The log is written once when the message arrives:
  it is not updated after the case is closed
  it is kept for ninety days and then removed
  it is read by the shift lead at handover
A host appears in the log whether or not anyone looked at it."""


def blocks(g):
    real = ["The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
            "Its own web hosts are:"]
    for host in g["KNOWN_GOOD"]["internal_hosts"]:
        real.append("  " + host)
    real.append(g["KNOWN_GOOD"]["rule"])
    real_block = "Known-good internal domains and hosts:\n" + "\n".join(real)

    # Placebo W. The same shape, with the attacker's own domain added.
    wrong = list(real)
    wrong.insert(-1, "  vetchmoor-benefits.example")
    wrong_block = "Known-good internal domains and hosts:\n" + "\n".join(wrong)
    return real_block, wrong_block


ARMS = {
    "F": ("no instructions, no block -- the shipped prompt", False, None),
    "G": ("instructions, no block", True, None),
    "H": ("no instructions, block present", False, "real"),
    "K": ("both -- the candidate repair", True, "real"),
    "N": ("both, block replaced by neutral prose -- placebo", True, "neutral"),
    "W": ("both, block wrongly names the attacker domain -- placebo", True, "wrong"),
}


def install(g, with_instructions, which_block, real_block, wrong_block):
    chosen = {None: None, "real": real_block, "wrong": wrong_block,
              "neutral": NEUTRAL_BLOCK}[which_block]

    def build_guarded_prompt(facts_text, body):
        parts = [g["GUARD_RULES"]]
        if with_instructions:
            parts.append(g["CLASSIFY_INSTRUCTIONS"])
        parts.append("Facts your own triage code pulled out:\n" + facts_text)
        if chosen:
            parts.append(chosen)
        parts.append(g["BODY_START"] + "\n" + body + "\n" + g["BODY_END"])
        parts.append(g["schema_text"](g["OUTPUT_SCHEMA"]))
        return "\n\n".join(parts)

    g["build_guarded_prompt"] = build_guarded_prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("factorial", "w6_solution.py", args.model,
                           "2x2 plus two placebos, through guarded_triage, n=%d" % args.trials)
    exec(compile(patched_source("body"), "run_triage-patched", "exec"), g)
    capture_traces(g)
    real_block, wrong_block = blocks(g)
    meta["arms"] = {k: v[0] for k, v in ARMS.items()}
    meta["neutral_block_chars"] = len(NEUTRAL_BLOCK)
    meta["real_block_chars"] = len(real_block)

    out = args.out or ("builder/docs/week6-measurement/factorial-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 9  model=%s  trials=%d" % (args.model, args.trials))
    print("neutral placebo %d chars against the real block at %d"
          % (len(NEUTRAL_BLOCK), len(real_block)))

    for trial in range(1, args.trials + 1):
        for eid in EMAILS:
            parsed = w6_rig.quiet(g["load_email"], eid, known_names=g["KNOWN_NAMES"])
            for name, (label, instr, block) in ARMS.items():
                install(g, instr, block, real_block, wrong_block)
                row = {"trial": trial, "email": eid, "arm": name, "label": label,
                       "truth": TRUTH[eid]}
                try:
                    del CAPTURED[:]
                    guarded = w6_rig.quiet(g["guarded_triage"], parsed)
                    row.update({"verdict": guarded.get("verdict"),
                                "confidence": guarded.get("confidence"),
                                "escalate": guarded.get("escalate"),
                                "escalate_reason": guarded.get("escalate_reason"),
                                "problems": guarded.get("problems"),
                                "stop_reason": guarded.get("stop_reason"),
                                "tools": CAPTURED[0]["tools"] if CAPTURED else None,
                                "parsed": CAPTURED[0]["answer_parsed"] if CAPTURED else None,
                                "tokens": guarded.get("tokens")})
                except Exception as exc:                    # noqa: BLE001
                    row["error"] = "%s: %s" % (type(exc).__name__, exc)
                res.add(row)
                print(" t%-3d %-4s %-2s -> %-10s esc=%-18s" % (
                    trial, eid, name, row.get("verdict") or row.get("error"),
                    row.get("escalate_reason")))
                sys.stdout.flush()

    ok = [r for r in res.doc["runs"] if not r.get("error")]
    summary = {"per_arm": {}, "tool_orders": {}}
    for name in ARMS:
        cell = {}
        for eid in EMAILS:
            rows = [r for r in ok if r["arm"] == name and r["email"] == eid]
            counts = {}
            for r in rows:
                counts[str(r["verdict"])] = counts.get(str(r["verdict"]), 0) + 1
            cell[eid] = {"verdicts": counts,
                         "correct": sum(1 for r in rows if r["verdict"] == TRUTH[eid])}
        cell["024_malicious"] = sum(1 for r in ok if r["arm"] == name
                                    and r["email"] == "024" and r["verdict"] == "malicious")
        cell["label"] = ARMS[name][0]
        summary["per_arm"][name] = cell
    orders = {}
    for r in ok:
        orders.setdefault(str(r["tools"]), 0)
        orders[str(r["tools"])] += 1
    summary["tool_orders"] = orders
    summary["P9-5_single_tool_order"] = len(orders) == 1
    res.summarize(summary)
    print()
    print(json.dumps(summary, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
