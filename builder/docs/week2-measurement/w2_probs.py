#!/usr/bin/env python3
"""What does the SECOND prompt actually carry, under each forced failure?

Objective 2.3 says "with the schema problems added to the new prompt". A mode
that fires the retry but hands the model an uninformative problem satisfies the
loop and not the objective. This records the try-1 problem list per mode.
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

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
VAGUE = ("You are a triage assistant. Say whether this reported email is a"
         " problem, how sure you are, and why.")

for mode in ("A", "C"):
    seen = collections.Counter()
    loaded = 0
    for eid in ("001", "002", "003", "004"):
        parsed = g["load_email"](eid)
        for _ in range(N):
            if mode == "A":
                raw = g["ask_model"](g["build_classify_prompt"](parsed), max_tokens=12)
            else:
                raw = g["ask_model"](VAGUE + "\n\nThe reported email:\n\n"
                                     + parsed["body_text"])
            data = g["extract_json"](raw)
            if isinstance(data, dict):
                loaded += 1
            probs = g["schema_errors"](data, g["OUTPUT_SCHEMA"])
            seen[" | ".join(p.split(",")[0][:46] for p in probs)] += 1
    print(f"--- mode {mode}: try-1 loaded as JSON {loaded}/{N*4} ---")
    for text, count in seen.most_common(6):
        print(f"   {count:3}x  {text}")
    print()
print(f"tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
