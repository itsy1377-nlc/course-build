#!/usr/bin/env python3
"""Does adding the schema problems to the new prompt do any measurable work?

Objective 2.3 claims the retry works because the problems go back with the
request. Every recovery measured so far is confounded: try 2 is an ordinary
full call, which passes on its own ~99% of the time, so a successful retry
proves nothing about the feedback.

This isolates it. The PROMPT still asks for 0.0 to 1.0; only the CHECKER is
tightened to 0.9. That is a deliberately unfair schema -- it is a probe, not a
proposed design -- and it makes try 1 fail by construction whenever the model
returns its habitual 0.95. Then the same failure is followed by two
independent second calls:

    WITH    the same prompt plus "confidence is 0.95, and it has to be
            from 0.0 to 0.9"      <- carries information the first prompt lacked
    BARE    the same prompt again, nothing appended

If WITH beats BARE, the feedback is the active ingredient and a range rule is a
live mechanism that counts can never be. If they match, the feedback is inert
and week 2 should not claim otherwise.
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

# The isolation prompt asks for 0.0 to 1.0 even though the shipped week 2
# schema now ends at 0.9. Only this probe creates that mismatch.
g["OUTPUT_SCHEMA"]["confidence"]["high"] = CEILING

first_fail = 0
trials = 0
with_ok = bare_ok = 0
with_conf = collections.Counter()
bare_conf = collections.Counter()

print(f"checker ceiling {CEILING}, prompt asks 0.0 to 1.0   n={N} per email", flush=True)
for eid in ("001", "002", "003", "004"):
    parsed = g["load_email"](eid)
    g["OUTPUT_SCHEMA"]["confidence"]["high"] = 1.0
    prompt = g["build_classify_prompt"](parsed)
    g["OUTPUT_SCHEMA"]["confidence"]["high"] = CEILING
    for _ in range(N):
        raw = g["ask_model"](prompt)
        data = g["extract_json"](raw)
        problems = g["schema_errors"](data, g["OUTPUT_SCHEMA"])
        if not problems:
            continue
        first_fail += 1
        trials += 1
        notes = ("\n\nYour last answer had these problems:\n"
                 + "\n".join(problems))
        d1 = g["extract_json"](g["ask_model"](prompt + notes))
        d2 = g["extract_json"](g["ask_model"](prompt))
        if not g["schema_errors"](d1, g["OUTPUT_SCHEMA"]):
            with_ok += 1
        if not g["schema_errors"](d2, g["OUTPUT_SCHEMA"]):
            bare_ok += 1
        with_conf[d1.get("confidence") if isinstance(d1, dict) else None] += 1
        bare_conf[d2.get("confidence") if isinstance(d2, dict) else None] += 1
    print(f"  {eid} done", flush=True)

n = N * 4
print(f"\n  try-1 failures: {first_fail}/{n} = {first_fail/n:.0%}")
if trials:
    print(f"  paired second calls: {trials}")
    print(f"    WITH problems appended: {with_ok}/{trials} = {with_ok/trials:.0%} pass")
    print(f"    BARE re-ask:            {bare_ok}/{trials} = {bare_ok/trials:.0%} pass")
    print(f"    confidence WITH: {dict(sorted(with_conf.items(), key=lambda kv:(kv[0] is None, kv[0])))}")
    print(f"    confidence BARE: {dict(sorted(bare_conf.items(), key=lambda kv:(kv[0] is None, kv[0])))}")
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls", flush=True)
