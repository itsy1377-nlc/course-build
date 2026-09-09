#!/usr/bin/env python3
"""Which part of the grounded prompt flips the verdict?

The grounded prompt adds three things the plain one does not have: the facts
block, the triage playbook, and the known-good host list. Withholding every
fact value still flips the verdict, so the facts are not doing it. This
isolates the three sections.
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


def known_good_text():
    lines = ["The organization is " + g["KNOWN_GOOD"]["organization"] + ".",
             "Its own web hosts are:"]
    for host in g["KNOWN_GOOD"]["internal_hosts"]:
        lines.append("  " + host)
    lines.append(g["KNOWN_GOOD"]["rule"])
    return "\n".join(lines)


def prompt_for(eid, want_facts, want_playbook, want_known):
    p = g["CLASSIFY_INSTRUCTIONS"] + "\n\n" + g["schema_text"](g["OUTPUT_SCHEMA"]) + "\n\n"
    if want_facts:
        p += "Facts about the reported email:\n\n" + facts[eid] + "\n\n"
    if want_playbook:
        p += "The triage playbook:\n\n" + g["PLAYBOOK"].strip() + "\n\n"
    if want_known:
        p += "Known-good internal domains and hosts:\n" + known_good_text() + "\n\n"
    return p + "The reported email:\n\n" + parsed[eid]["body_text"]


CONDS = [("body alone (week 2)",        False, False, False),
         ("facts only",                 True,  False, False),
         ("playbook only",              False, True,  False),
         ("known-good only",            False, False, True),
         ("facts + playbook",           True,  True,  False),
         ("everything (shipped)",       True,  True,  True)]

print(f"n={N} per condition\n")
print(f"{'email':<7}{'condition':<24}verdict")
print("-" * 58)
for eid, truth in (("008", "malicious"), ("017", "benign")):
    for label, f, pb, kg in CONDS:
        c = collections.Counter()
        for _ in range(N):
            d = g["extract_json"](g["ask_model"](prompt_for(eid, f, pb, kg)))
            c[(d or {}).get("verdict")] += 1
        print(f"{eid:<7}{label:<24}" + " ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))))
    print(f"        (truth: {truth})\n")
print(f"tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
