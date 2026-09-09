#!/usr/bin/env python3
"""Does granite-3b FIX the problem when the retry tells it what was wrong?

A tightened schema rule only works as teaching if the second attempt passes.
If the model re-offends, classify_email() exhausts max_tries and returns None,
and the lab is worse than it is today. This runs the real retry loop under a
tightened rule and reports the distribution of tries used, and how many runs
end with no answer at all.
"""
import json, os, re, sys, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w2-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = "granite-3b"

g = {"__name__": "__main__"}
src = open("/tmp/w2_prewritten.py").read()
src = re.sub(r"try:\n\s+import piplite\n.*?except ImportError:\n\s+pass[^\n]*\n", "", src, flags=re.S)
exec(compile(src, "prewritten", "exec"), g)
exec(compile(open("/tmp/w2_solution_fns.py").read(), "solution", "exec"), g)
g["SHOW_CALL_TOKENS"] = False

MAX_IND = int(sys.argv[1]) if len(sys.argv) > 1 else 3
N = int(sys.argv[2]) if len(sys.argv) > 2 else 10

# The tightened rule. Only the cap moves; nothing else about the week changes.
g["OUTPUT_SCHEMA"]["indicators"]["max_items"] = MAX_IND

# schema_text() hardcodes "one to six short strings", so the prompt would still
# ask for six while the checker demands three. That is not a fair test of the
# model -- it is a test of a contradiction. Render the real numbers.
NUM = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six"}
def schema_text(schema):
    lines = ["Answer with one JSON object and nothing else."
             " It must hold exactly these four keys."]
    for key in schema:
        rule = schema[key]
        if "allowed" in rule:
            lines.append(f'"{key}": one of ' + ", ".join(rule["allowed"]))
        elif rule["type"] == "number":
            lines.append(f'"{key}": a number from {rule["low"]} to {rule["high"]}')
        else:
            lines.append(f'"{key}": a list of {NUM[rule["min_items"]]} to'
                         f' {NUM[rule["max_items"]]} short strings, each naming'
                         ' a fact you used')
    return "\n".join(lines)
g["schema_text"] = schema_text

print(f"indicators capped at {MAX_IND}   n={N} per email", flush=True)
print(g["schema_text"](g["OUTPUT_SCHEMA"]).splitlines()[-1], flush=True)
print(flush=True)

overall = collections.Counter()
none_total = 0
for eid in ("001", "002", "003", "004"):
    parsed = g["load_email"](eid)
    tries = collections.Counter()
    nones = 0
    first_fail = 0
    for _ in range(N):
        before = len(g["ATTEMPT_LOG"])
        out = g["classify_email"](parsed)
        used = len(g["ATTEMPT_LOG"]) - before
        tries[used] += 1
        overall[used] += 1
        if out is None:
            nones += 1
            none_total += 1
        if used > 1:
            first_fail += 1
    print(f"  {eid}: tries {dict(sorted(tries.items()))}  "
          f"retried {first_fail}/{N}  gave up (None) {nones}/{N}", flush=True)

n = sum(overall.values())
solved_by_2 = sum(v for k, v in overall.items() if k <= 2)
print(f"\n  tries overall: {dict(sorted(overall.items()))}")
print(f"  finished within 2 tries: {solved_by_2}/{n} = {solved_by_2/n:.0%}")
print(f"  gave up with no answer:  {none_total}/{n} = {none_total/n:.0%}")
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls", flush=True)
