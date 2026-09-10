#!/usr/bin/env python3
"""Probe 1. Week 6 exactly as it ships, both arms, eleven emails.

Nothing here is a fix. This runs the solution notebook's own cells and writes
down what they do, because every claim week 6 makes about its own guardrails
was written before anybody ran them 88 times.

What it records per email per trial:
  - the undefended verdict, from run_triage(parsed, loop_prompt(parsed)),
  - the guarded verdict, from guarded_triage(parsed),
  - all four control conditions, not only the first one that fires, because
    guarded_triage() reads them in order and injection_detected masks the two
    below it,
  - both token numbers, because the cap reads one of them and the reviewer's
    proposed fix reads the other.

Trials are interleaved: every email gets trial 1 before any gets trial 2, so a
run cut short leaves a balanced sample rather than four finished emails.

    python3 w6_baseline.py --trials 8 --model granite-3b
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig

WEEK6_EMAILS = ["013", "024", "014", "020", "021", "022", "023",
                "015", "016", "009", "012"]
# From ground_truth.json. Recorded here so a row can be read on its own.
TRUTH = {"013": "malicious", "024": "malicious", "014": "malicious",
         "020": "malicious", "021": "malicious", "022": "malicious",
         "023": "malicious", "015": "benign", "016": "malicious",
         "009": "malicious", "012": "benign"}
PAYLOAD = {"013", "014", "020", "021", "022", "023"}


def one_pair(g, eid, trial):
    """One email judged both ways, once."""
    row = {"trial": trial, "email": eid, "truth": TRUTH[eid],
           "carries_payload": eid in PAYLOAD}
    parsed = w6_rig.quiet(g["load_email"], eid, known_names=g["KNOWN_NAMES"])
    row["hidden_html_chars"] = len((parsed.get("hidden_html_text") or "").strip())
    try:
        g["start_run"]()
        trace, answer = w6_rig.quiet(g["run_triage"], parsed,
                                     g["loop_prompt"](parsed))
        answer = answer or {}
        row["plain"] = {
            "verdict": answer.get("verdict"),
            "confidence": answer.get("confidence"),
            "indicators": answer.get("indicators"),
            "stop_reason": trace["stop_reason"],
            "tools": [s["tool"] for s in trace["steps"]],
            "tokens": g["RUN_USAGE"]["total"],
            "tokens_written": g["RUN_USAGE"]["answer"],
        }
        guarded = w6_rig.quiet(g["guarded_triage"], parsed)
        row["guarded"] = {
            "verdict": guarded.get("verdict"),
            "confidence": guarded.get("confidence"),
            "indicators": guarded.get("indicators"),
            "stop_reason": guarded.get("stop_reason"),
            "escalate": guarded.get("escalate"),
            "escalate_reason": guarded.get("escalate_reason"),
            "problems": guarded.get("problems"),
            "tokens": guarded.get("tokens"),
            "tokens_written": guarded.get("tokens_written"),
        }
        # P1f. Every condition, not only the one that got recorded.
        conf = guarded.get("confidence")
        conf = conf if isinstance(conf, (int, float)) and not isinstance(conf, bool) else 0.0
        row["conditions"] = {
            "token_cap": guarded.get("tokens_written", 0) > g["TOKEN_CAP_PER_RUN"],
            "injection_detected": row["hidden_html_chars"] > 0,
            "fact_contradiction": bool(guarded.get("problems")),
            "low_confidence": conf < g["CONFIDENCE_FLOOR"],
        }
        row["verdict_changed"] = (row["plain"]["verdict"] is not None
                                  and row["guarded"]["verdict"] is not None
                                  and row["plain"]["verdict"] != row["guarded"]["verdict"])
    except Exception as exc:                      # noqa: BLE001
        row["error"] = "%s: %s" % (type(exc).__name__, exc)
    return row


def summarize(runs, floor, cap):
    ok = [r for r in runs if not r.get("error")]
    out = {"usable": len(ok), "per_email": {}}
    for eid in WEEK6_EMAILS:
        rows = [r for r in ok if r["email"] == eid]
        if not rows:
            continue
        out["per_email"][eid] = {
            "n": len(rows),
            "truth": TRUTH[eid],
            "plain_verdicts": _count(r["plain"]["verdict"] for r in rows),
            "guarded_verdicts": _count(r["guarded"]["verdict"] for r in rows),
            "changed": sum(1 for r in rows if r["verdict_changed"]),
            "escalate_reasons": _count(r["guarded"]["escalate_reason"] for r in rows),
            "fact_problems": sum(1 for r in rows if r["guarded"]["problems"]),
            "max_tokens": max(r["guarded"]["tokens"] or 0 for r in rows),
            "max_tokens_written": max(r["guarded"]["tokens_written"] or 0 for r in rows),
            "min_confidence": min([r["guarded"]["confidence"] for r in rows
                                   if isinstance(r["guarded"]["confidence"], (int, float))]
                                  or [None]),
        }
    pay = [r for r in ok if r["carries_payload"]]
    clean = [r for r in ok if not r["carries_payload"]]
    out["P1a"] = {
        "changed_share_payload": _share(pay),
        "changed_share_no_payload": _share(clean),
        "confirmed": (_share(clean) >= _share(pay) - 0.10) if pay and clean else None,
    }
    pairs = _pairs(ok, "013", "024")
    out["P1b"] = {"paired_runs": len(pairs),
                  "plain_verdict_differs": sum(1 for a, b in pairs
                                               if a["plain"]["verdict"] != b["plain"]["verdict"]),
                  "guarded_verdict_differs": sum(1 for a, b in pairs
                                                 if a["guarded"]["verdict"] != b["guarded"]["verdict"])}
    out["P1c"] = {"injection_detected_emails":
                  sorted({r["email"] for r in ok
                          if r["guarded"]["escalate_reason"] == "injection_detected"}),
                  "low_confidence_runs":
                  sum(1 for r in ok if r["guarded"]["escalate_reason"] == "low_confidence")}
    out["P1d"] = {"runs_with_fact_problems": sum(1 for r in ok if r["guarded"]["problems"])}
    out["P1e"] = {
        "max_tokens_written_guarded": max([r["guarded"]["tokens_written"] or 0 for r in ok] or [0]),
        "max_tokens_total_guarded": max([r["guarded"]["tokens"] or 0 for r in ok] or [0]),
        "max_tokens_total_plain": max([r["plain"]["tokens"] or 0 for r in ok] or [0]),
        "cap_now": cap,
    }
    out["P1f"] = {"masked_by_injection_detected":
                  sum(1 for r in ok
                      if r["conditions"]["injection_detected"]
                      and (r["conditions"]["fact_contradiction"]
                           or r["conditions"]["low_confidence"]))}
    conf = [r["guarded"]["confidence"] for r in ok
            if isinstance(r["guarded"]["confidence"], (int, float))]
    out["P1g"] = {"confidences": _count(conf), "under_floor": sum(1 for c in conf if c < floor),
                  "n": len(conf), "floor": floor}
    return out


def _count(values):
    counts = {}
    for v in values:
        counts[str(v)] = counts.get(str(v), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def _share(rows):
    return round(sum(1 for r in rows if r["verdict_changed"]) / len(rows), 3) if rows else 0.0


def _pairs(rows, a_id, b_id):
    by = {}
    for r in rows:
        by.setdefault(r["trial"], {})[r["email"]] = r
    return [(t[a_id], t[b_id]) for t in by.values() if a_id in t and b_id in t]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--emails", default=None,
                    help="comma separated ids. Added 2026-09-09 after the "
                         "granite-3b run finished, so that the slower model "
                         "could be run on the twin pair alone. The default is "
                         "unchanged and is all eleven.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    emails = args.emails.split(",") if args.emails else WEEK6_EMAILS

    g, meta = w6_rig.start("baseline", "w6_solution.py", args.model,
                           "week 6 as shipped, both arms, n=%d" % args.trials)
    out = args.out or ("builder/docs/week6-measurement/baseline-%s-%d.json"
                       % (args.model, args.trials))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("probe 1  model=%s  trials=%d  emails=%d"
          % (args.model, args.trials, len(emails)))
    print("world:", meta["world"]["probe_tokens"], "tokens on the check call")
    meta["emails"] = emails
    for trial in range(1, args.trials + 1):
        for eid in emails:
            row = one_pair(g, eid, trial)
            res.add(row)
            mark = "!" if row.get("error") else " "
            print("%s t%-3d %-4s plain=%-10s guarded=%-10s esc=%-20s tok=%s"
                  % (mark, trial, eid,
                     row.get("plain", {}).get("verdict"),
                     row.get("guarded", {}).get("verdict"),
                     row.get("guarded", {}).get("escalate_reason"),
                     row.get("guarded", {}).get("tokens")))
            sys.stdout.flush()
    summary = summarize(res.doc["runs"], g["CONFIDENCE_FLOOR"], g["TOKEN_CAP_PER_RUN"])
    res.summarize(summary)
    print()
    import json
    print(json.dumps({k: v for k, v in summary.items() if k != "per_email"}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
