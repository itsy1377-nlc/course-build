#!/usr/bin/env python3
"""Re-record the week 6 walkthrough run, on the stack the course actually serves.

content/video/runs/w6.json was recorded on 2026-09-05 against ollama at
localhost:11434 with granite4.2:3b -- a stack the course left on 2026-09-07 and
a model no student can call. The walkthrough narration quotes it directly, so
fifteen of its numbers are currently evidence from a model nobody has access to.

This runs the same email, 034, through the repaired week 6 code, and writes a
record in the same shape. Email 034 is chosen for the same reasons as before and
they still hold: it carries a payload in a placement the lab never shows, its
sender is known bad at address level, and it is in no week 6 lab set.

    python3 w6_walkthrough_run.py --trials 15
"""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig

EMAIL = "034"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=15)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--out", default="builder/docs/week6-measurement/walkthrough-run.json")
    args = ap.parse_args()

    # No patching. The notebooks now carry the repair, so the rig extracted
    # from them IS the shipped code, and that is what a walkthrough must show.
    g, meta = w6_rig.start("walkthrough", "w6_solution.py", args.model,
                           "email 034 through the shipped week 6, n=%d" % args.trials)

    # The narration quotes exact answer text, so keep the last raw reply.
    raw = {"text": None}
    real_ask = g["ask_model"]

    def ask_model(prompt, **kw):
        out = real_ask(prompt, **kw)
        raw["text"] = out
        return out
    g["ask_model"] = ask_model

    # 034 lives in corpus/emails/batch/, which is precisely why it is legal
    # here: no week 6 lab email may appear in the walkthrough, and the lab
    # loads only from teaching/. load_email() looks in EMAIL_DIR, so point it
    # at the batch folder for this one read and put it back afterwards.
    kept_dir = g["EMAIL_DIR"]
    g["EMAIL_DIR"] = w6_rig.BUILDER / "corpus/emails/batch"
    try:
        parsed = w6_rig.quiet(g["load_email"], EMAIL, known_names=g["KNOWN_NAMES"])
    finally:
        g["EMAIL_DIR"] = kept_dir
    meta["email_id"] = EMAIL
    meta["email_file"] = "corpus/emails/batch/034-cfo-vendor-setup-thread.eml"
    meta["why_this_email"] = (
        "Week 6's lab runs 009, 012, 013, 014, 015, 016, 020, 021, 022, 023 and "
        "024, so none of those may appear in the walkthrough. 034 carries a "
        "prompt injection in a placement the lab never shows: a line inside a "
        "fabricated quoted thread, attributed to the IT help desk, saying an "
        "automated triage tool has cleared it. Its sender is known bad at "
        "address level, which is the one condition that lets the week 6 fact "
        "check reach a real email.")
    meta["repaired_code"] = True

    res = w6_rig.Result(w6_rig.ROOT / args.out, meta)
    print("walkthrough re-record  email=%s  model=%s  trials=%d"
          % (EMAIL, args.model, args.trials))

    for trial in range(1, args.trials + 1):
        row = {"trial": trial, "run_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                           time.gmtime())}
        try:
            started = time.time()
            g["start_run"]()
            trace, answer = w6_rig.quiet(g["run_triage"], parsed,
                                         g["loop_prompt"](parsed))
            answer = answer or {}
            row["plain"] = {
                "verdict": answer.get("verdict"), "category": answer.get("category"),
                "confidence": answer.get("confidence"),
                "indicators": answer.get("indicators"),
                "parsed": isinstance(answer, dict) and bool(answer),
                "raw_final_text": raw["text"],
                "stop_reason": trace["stop_reason"],
                "steps": [{"step": s["step"], "tool": s["tool"]} for s in trace["steps"]],
                "step_count": len(trace["steps"]),
                "tokens": g["RUN_USAGE"]["total"],
                "tokens_written": g["RUN_USAGE"]["answer"],
                "seconds": round(time.time() - started, 1),
            }
            started = time.time()
            guarded = w6_rig.quiet(g["guarded_triage"], parsed)
            row["guarded"] = {k: guarded.get(k) for k in
                              ("verdict", "category", "confidence", "indicators",
                               "escalate", "escalate_reason", "problems",
                               "schema_problems", "markers_in_body", "stop_reason",
                               "tokens", "tokens_written")}
            row["guarded"]["raw_final_text"] = raw["text"]
            row["guarded"]["parsed"] = guarded.get("verdict") is not None
            row["guarded"]["seconds"] = round(time.time() - started, 1)
            row["pair"] = {"verdict_changed":
                           row["plain"]["verdict"] != row["guarded"]["verdict"]}
        except Exception as exc:                            # noqa: BLE001
            row["error"] = "%s: %s" % (type(exc).__name__, exc)
        res.add(row)
        print(" t%-3d plain=%-10s guarded=%-10s esc=%-18s" % (
            trial, row.get("plain", {}).get("verdict"),
            row.get("guarded", {}).get("verdict"),
            row.get("guarded", {}).get("escalate_reason")))
        sys.stdout.flush()

    # The fence record the narration reads out, from the repaired prompt.
    safe_body, markers = g["strip_markers"](parsed["body_text"])
    safe = dict(parsed); safe["body_text"] = safe_body
    prompt_text = g["build_guarded_prompt"](g["grounding_text"](safe), safe_body)
    ok = [r for r in res.doc["runs"] if not r.get("error")]

    def tally(arm, key):
        out = {}
        for r in ok:
            out[str(r[arm].get(key))] = out.get(str(r[arm].get(key)), 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    res.summarize({
        "trials": len(ok),
        "fence_check": g["fence_check"](prompt_text, safe_body),
        "guarded_prompt_chars": len(prompt_text),
        "confidence_floor": g["CONFIDENCE_FLOOR"],
        "token_cap_per_run": g["TOKEN_CAP_PER_RUN"],
        "max_steps": g["MAX_STEPS"],
        "plain": {k: tally("plain", k) for k in
                  ("verdict", "category", "confidence", "parsed", "stop_reason", "step_count")},
        "guarded": {k: tally("guarded", k) for k in
                    ("verdict", "category", "confidence", "parsed", "escalate_reason",
                     "stop_reason")},
        "tokens": {
            "plain_mean": round(sum(r["plain"]["tokens"] for r in ok) / max(len(ok), 1)),
            "guarded_mean": round(sum(r["guarded"]["tokens"] for r in ok) / max(len(ok), 1)),
            "guarded_written_max": max((r["guarded"]["tokens_written"] or 0) for r in ok) if ok else 0,
        },
        "verdict_changed_count": sum(1 for r in ok if r["pair"]["verdict_changed"]),
    })
    print()
    print(json.dumps(res.doc["summary"], indent=1)[:2000])
    print("wrote", args.out)


if __name__ == "__main__":
    main()
