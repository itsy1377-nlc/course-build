#!/usr/bin/env python3
"""The whole repaired week 6, every change in place, end to end.

Codex's review asked for this: the earlier repaired run implemented two of the
changes, and a table quoted to students has to come from the code that ships.
This installs all six over the solution notebook's own cells and runs the
eleven emails both ways.

  1. run_triage()'s closing call carries the body exactly ONCE in both arms.
     The membership test is what keeps the arms matched: the guarded prompt
     already holds the fenced body, so nothing is appended to it.
  2. build_guarded_prompt() keeps week 3's grounding, through grounding_text().
  3. strip_markers() takes the fence markers out of the body once, before the
     body is used anywhere, and a body that arrived with one escalates as
     fence_broken. This is the fail-closed replacement for a repair that failed
     open.
  4. fence_check() finds the FIRST end marker after the body opens, and counts
     markers found in the body.
  5. guarded_triage() calls schema_errors() and records schema_problems.
  6. compare_guarded() records both confidences and the undefended token cost,
     read before guarded_triage() calls start_run().

    python3 w6_final.py --trials 8 --model granite-3b --run 1
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w6_rig
from w6_baseline import WEEK6_EMAILS, TRUTH, summarize
from w6_body import accuracy


def install(g):
    """Every week 6 change, over the notebook's own globals."""
    BODY_START, BODY_END = g["BODY_START"], g["BODY_END"]

    def strip_markers(text):
        cleaned = str(text or "")
        found = cleaned.count(BODY_START) + cleaned.count(BODY_END)
        cleaned = cleaned.replace(BODY_START, "[marker removed]")
        cleaned = cleaned.replace(BODY_END, "[marker removed]")
        return cleaned, found

    def fence_check(prompt_text, body):
        if not isinstance(prompt_text, str):
            prompt_text = ""
        start_index = prompt_text.rfind(BODY_START)
        end_index = -1
        if start_index != -1:
            end_index = prompt_text.find(BODY_END, start_index + len(BODY_START))
        fenced_body_chars = 0
        if start_index != -1 and end_index > start_index:
            fenced_body_chars = end_index - (start_index + len(BODY_START))
        return {"body_start_index": start_index, "body_end_index": end_index,
                "fenced_body_chars": fenced_body_chars,
                "email_body_chars": len(body),
                "markers_in_body": strip_markers(body)[1]}

    def grounding_text(parsed):
        lines = [g["CLASSIFY_INSTRUCTIONS"], "",
                 "Facts your own triage code pulled out:",
                 g["guarded_facts_text"](parsed), "",
                 "Known-good internal domains and hosts:",
                 "The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
                 "Its own web hosts are:"]
        for host in g["KNOWN_GOOD"]["internal_hosts"]:
            lines.append("  " + host)
        lines.append(g["KNOWN_GOOD"]["rule"])
        return "\n".join(lines)

    def build_guarded_prompt(grounding, body):
        parts = [g["GUARD_RULES"], grounding,
                 BODY_START + "\n" + body + "\n" + BODY_END,
                 g["schema_text"](g["OUTPUT_SCHEMA"])]
        return "\n\n".join(parts)

    def run_triage(parsed, prompt_text, schema=None, step_guard=None):
        schema = schema if schema is not None else g["OUTPUT_SCHEMA"]
        trace = g["run_loop"](parsed, prompt_text, g["MAX_STEPS"], step_guard)
        if not isinstance(trace, dict):
            trace = g["new_trace"](parsed)
        if trace["stop_reason"] is None:
            trace["stop_reason"] = "step_cap"
        lines = []
        for step in trace["steps"]:
            lines.append(step["tool"] + " returned " + json.dumps(
                g["run_tool"](step["tool"], step["arguments"], parsed)))
        closing = prompt_text
        if parsed["body_text"] not in closing:
            closing = closing + "\n\nThe reported email:\n\n" + parsed["body_text"]
        closing = (closing
                   + "\n\nTool results for this message:\n" + "\n".join(lines)
                   + "\n\n" + g["schema_text"](schema)
                   + "\n\nYou have every tool result you are going to get."
                     " Answer now with one JSON object and nothing else.")
        answer = g["extract_json"](g["ask_model"](closing))
        if isinstance(answer, dict):
            trace["final_answer"] = answer
        trace["tokens"] = g["RUN_USAGE"]["total"]
        return trace, answer

    def guarded_triage(parsed, schema=None):
        schema = schema if schema is not None else g["OUTPUT_SCHEMA"]
        g["start_run"]()
        # The body is attacker text, so the markers come out of it once, here,
        # before it is used anywhere. Sanitizing inside fenced_email() alone
        # would be too late: the prompt is built from the body first.
        safe_body, markers_found = strip_markers(parsed["body_text"])
        safe = dict(parsed)
        safe["body_text"] = safe_body

        facts = g["build_facts"](safe)
        facts["url_status"] = g["check_urls"](safe["url_hosts"])
        facts["sender_status"] = g["check_sender_reputation"](safe["from_address"])["status"]
        facts["hosts_extracted"] = list(safe["url_hosts"])
        for address in ((safe["from_address"], safe["reply_to"])
                        + tuple(safe["to"] or [])):
            if address and "@" in str(address):
                host = str(address).split("@")[-1].lower()
                if host not in facts["hosts_extracted"]:
                    facts["hosts_extracted"].append(host)

        prompt_text = build_guarded_prompt(grounding_text(safe), safe_body)
        fenced = False
        if isinstance(prompt_text, str):
            checked = fence_check(prompt_text, safe_body)
            fenced = checked["fenced_body_chars"] >= checked["email_body_chars"]
        email_for_run = safe
        if fenced:
            email_for_run = g["fenced_email"](safe)
        else:
            prompt_text = g["loop_prompt"](safe)

        trace, answer = run_triage(email_for_run, prompt_text, schema,
                                   g["over_token_cap"])
        answer = answer or {}
        problems = g["check_against_facts"](answer, facts)
        if not isinstance(problems, list):
            problems = []
        schema_problems = g["schema_errors"](answer, schema) or []
        confidence = answer.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            confidence = 0.0
        hidden = (safe.get("hidden_html_text") or "").strip()

        reason = "none"
        if g["over_token_cap"]():
            reason = "token_cap"
        elif markers_found:
            reason = "fence_broken"
        elif hidden:
            reason = "injection_detected"
        elif problems:
            reason = "fact_contradiction"
        elif confidence < g["CONFIDENCE_FLOOR"]:
            reason = "low_confidence"

        result = {}
        for key in schema:
            result[key] = answer.get(key)
        result["escalate"] = reason != "none"
        result["escalate_reason"] = reason
        result["problems"] = problems
        result["schema_problems"] = schema_problems
        result["markers_in_body"] = markers_found
        result["stop_reason"] = trace["stop_reason"]
        result["tokens"] = g["RUN_USAGE"]["total"]
        result["tokens_written"] = g["RUN_USAGE"]["answer"]
        return result

    g.update({"strip_markers": strip_markers, "fence_check": fence_check,
              "grounding_text": grounding_text,
              "build_guarded_prompt": build_guarded_prompt,
              "run_triage": run_triage, "guarded_triage": guarded_triage})


def one_pair(g, eid, trial):
    row = {"trial": trial, "email": eid, "truth": TRUTH[eid],
           "carries_payload": eid in {"013", "014", "020", "021", "022", "023"}}
    parsed = w6_rig.quiet(g["load_email"], eid, known_names=g["KNOWN_NAMES"])
    row["hidden_html_chars"] = len((parsed.get("hidden_html_text") or "").strip())
    try:
        g["start_run"]()
        trace, answer = w6_rig.quiet(g["run_triage"], parsed, g["loop_prompt"](parsed))
        answer = answer or {}
        # Read the undefended numbers BEFORE guarded_triage() calls start_run().
        row["plain"] = {"verdict": answer.get("verdict"),
                        "confidence": answer.get("confidence"),
                        "stop_reason": trace["stop_reason"],
                        "tools": [s["tool"] for s in trace["steps"]],
                        "tokens": g["RUN_USAGE"]["total"],
                        "tokens_written": g["RUN_USAGE"]["answer"]}
        guarded = w6_rig.quiet(g["guarded_triage"], parsed)
        row["guarded"] = {k: guarded.get(k) for k in
                          ("verdict", "confidence", "escalate", "escalate_reason",
                           "problems", "schema_problems", "markers_in_body",
                           "stop_reason", "tokens", "tokens_written")}
        row["conditions"] = {
            "token_cap": (guarded.get("tokens_written") or 0) > g["TOKEN_CAP_PER_RUN"],
            "fence_broken": bool(guarded.get("markers_in_body")),
            "injection_detected": row["hidden_html_chars"] > 0,
            "fact_contradiction": bool(guarded.get("problems")),
            "low_confidence": (guarded.get("confidence") or 0) < g["CONFIDENCE_FLOOR"],
        }
        row["verdict_changed"] = (row["plain"]["verdict"] is not None
                                  and row["guarded"]["verdict"] is not None
                                  and row["plain"]["verdict"] != row["guarded"]["verdict"])
    except Exception as exc:                                # noqa: BLE001
        row["error"] = "%s: %s" % (type(exc).__name__, exc)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=8)
    ap.add_argument("--model", default="granite-3b")
    ap.add_argument("--run", default="1")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    g, meta = w6_rig.start("final", "w6_solution.py", args.model,
                           "every change in place, n=%d, run %s" % (args.trials, args.run))
    install(g)
    meta["changes"] = ["body once in the closing call", "grounding kept",
                       "markers stripped once, fail closed", "fence_check first marker",
                       "schema_errors called", "undefended numbers recorded"]
    meta["run_label"] = args.run

    out = args.out or ("builder/docs/week6-measurement/final-%s-%d-run%s.json"
                       % (args.model, args.trials, args.run))
    res = w6_rig.Result(w6_rig.ROOT / out, meta)
    print("final week 6  model=%s  trials=%d  run=%s" % (args.model, args.trials, args.run))
    for trial in range(1, args.trials + 1):
        for eid in WEEK6_EMAILS:
            row = one_pair(g, eid, trial)
            res.add(row)
            print(" t%-3d %-4s plain=%-10s guarded=%-10s esc=%-18s" % (
                trial, eid, row.get("plain", {}).get("verdict"),
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
