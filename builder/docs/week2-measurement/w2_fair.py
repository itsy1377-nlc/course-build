#!/usr/bin/env python3
"""The FAIR confidence rule: prompt and checker agree.

The efficacy probe deliberately hid the ceiling from the prompt. A real schema
cannot do that -- schema_text() renders the same rule the checker enforces,
which is the single-sourcing week 2 is rightly proud of. So: set the ceiling in
OUTPUT_SCHEMA, let it flow into the prompt, and measure the honest first-try
rate and the honest recovery through the real classify_email loop.

Counts collapsed when the prompt was made fair (cap 4 -> 94% pass on try 1).
The question is whether a range rule collapses the same way, and -- the part
that matters more -- whether the runs that do fail still recover.
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

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
CEILING = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9
g["OUTPUT_SCHEMA"]["confidence"]["high"] = CEILING   # flows into the prompt too

print(f"ceiling {CEILING}, prompt AND checker agree   n={N} per email", flush=True)
print("  prompt line:", [l for l in g["schema_text"](g["OUTPUT_SCHEMA"]).splitlines()
                         if "confidence" in l][0], flush=True)
overall = collections.Counter(); nones = 0; conf = collections.Counter()
for eid in ("001", "002", "003", "004"):
    parsed = g["load_email"](eid)
    tries = collections.Counter(); gave_up = 0
    for _ in range(N):
        before = len(g["ATTEMPT_LOG"])
        out = g["classify_email"](parsed)
        used = len(g["ATTEMPT_LOG"]) - before
        tries[used] += 1; overall[used] += 1
        if out is None:
            gave_up += 1; nones += 1
        else:
            conf[out.get("confidence")] += 1
    print(f"  {eid}: tries {dict(sorted(tries.items()))}  gave up {gave_up}/{N}", flush=True)

n = sum(overall.values())
retried = n - overall.get(1, 0)
print(f"\n  tries overall: {dict(sorted(overall.items()))}")
print(f"  retried:        {retried}/{n} = {retried/n:.0%}")
print(f"  gave up:        {nones}/{n} = {nones/n:.0%}")
if retried:
    print(f"  of those that retried, recovered: {retried-nones}/{retried} = {(retried-nones)/retried:.0%}")
print(f"  accepted confidence values: {dict(sorted(conf.items()))}")
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls", flush=True)
