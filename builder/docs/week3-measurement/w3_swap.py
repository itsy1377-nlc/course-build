#!/usr/bin/env python3
"""Is 008's flip grounding, or just the presence of a facts block?

008 and 017 carry nearly the same facts -- spf, dkim and dmarc all pass, no
display-name mismatch, a clean scan, one link on the sender's own domain, no
attachment -- and opposite truths. Both read benign from the body alone and
both go malicious once a facts block arrives. If the block is doing the work
rather than the facts in it, swapping the blocks changes nothing.

Four conditions per email: body alone, its own facts, the other email's facts,
and a facts block with every value blanked out.
"""
import json, os, re, sys, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = "granite-3b"

g = {"__name__": "__main__"}
exec(compile(open("/tmp/w3_prewritten.py").read(), "pre", "exec"), g)
exec(compile(open("/tmp/w3_solution_fns.py").read(), "sol", "exec"), g)
g["SHOW_CALL_TOKENS"] = False
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6

parsed = {e: g["load_email"](e, known_names=g["KNOWN_NAMES"]) for e in ("008", "017")}
facts = {e: g["format_facts"](g["build_facts"](parsed[e])) for e in ("008", "017")}
blank = "\n".join(line.split(":")[0] + ": (withheld)" for line in facts["008"].split("\n"))


def run(eid, facts_text, n):
    c = collections.Counter()
    for _ in range(n):
        if facts_text is None:
            out = g["classify_email"](parsed[eid]) or {}
        else:
            prompt = g["build_grounded_prompt"](facts_text, parsed[eid]["body_text"])
            data = g["extract_json"](g["ask_model"](prompt))
            out = data if isinstance(data, dict) else {}
        c[out.get("verdict")] += 1
    return c


print(f"n={N} per condition\n")
print(f"{'email':<8}{'condition':<26}{'verdict':<24}")
print("-" * 62)
for eid, truth in (("008", "malicious"), ("017", "benign")):
    other = "017" if eid == "008" else "008"
    for label, ft in (("body alone", None),
                      ("its own facts", facts[eid]),
                      (f"{other}'s facts", facts[other]),
                      ("facts, values withheld", blank)):
        c = run(eid, ft, N)
        shown = " ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0])))
        print(f"{eid:<8}{label:<26}{shown:<24}(truth {truth})")
    print()
print(f"tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
