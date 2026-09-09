#!/usr/bin/env python3
"""Does the retry mechanism work at all, once the first try has failed?

Three ways to make try 1 fail, then measure whether try 2 recovers:

  A  truncation      try 1 called with max_tokens=12, so nothing loads.
                     The problem sent back is the generic "not a JSON object".
  B  schema stub     try 1 returns the notebook's own LOADS_BUT_WRONG answer.
                     The problems sent back are four specific, actionable ones.
  C  vague prompt    try 1 uses an under-specified instruction, so whatever
                     comes back is the model's own genuine mistake.

Reports, per variant: did try 2 pass, and how many tries the loop used.
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

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
EMAILS = ("001", "002", "003", "004")

LOADS_BUT_WRONG = ('{"verdict": "suspicious", "category": "phishing",'
                   ' "confidence": 1.4, "indicators": []}')
VAGUE = ("You are a triage assistant. Say whether this reported email is a"
         " problem, how sure you are, and why.")


def loop(parsed, first_try_mode, max_tries=3):
    """The reference classify_email, with try 1 made to fail on purpose."""
    notes = ""
    for try_number in range(1, max_tries + 1):
        if try_number == 1 and first_try_mode == "B":
            raw = LOADS_BUT_WRONG                      # no call spent
        elif try_number == 1 and first_try_mode == "A":
            raw = g["ask_model"](g["build_classify_prompt"](parsed), max_tokens=12)
        elif try_number == 1 and first_try_mode == "C":
            raw = g["ask_model"](VAGUE + "\n\nThe reported email:\n\n"
                                 + parsed["body_text"])
        else:
            raw = g["ask_model"](g["build_classify_prompt"](parsed) + notes)
        data = g["extract_json"](raw)
        problems = g["schema_errors"](data, g["OUTPUT_SCHEMA"])
        if not problems:
            return data, try_number, problems
        notes = ("\n\nYour last answer had these problems:\n"
                 + "\n".join(problems))
    return None, max_tries, problems


for mode, label in (("A", "truncation  (max_tokens=12 on try 1)"),
                    ("B", "schema stub (LOADS_BUT_WRONG on try 1)"),
                    ("C", "vague prompt on try 1")):
    tries = collections.Counter()
    nones = 0
    for eid in EMAILS:
        parsed = g["load_email"](eid)
        for _ in range(N):
            out, used, probs = loop(parsed, mode)
            tries[used] += 1
            if out is None:
                nones += 1
    n = sum(tries.values())
    by2 = tries.get(1, 0) + tries.get(2, 0)
    print(f"{mode}  {label}", flush=True)
    print(f"     tries {dict(sorted(tries.items()))}   "
          f"recovered on try 2: {tries.get(2,0)}/{n} = {tries.get(2,0)/n:.0%}   "
          f"no answer at all: {nones}/{n} = {nones/n:.0%}", flush=True)

print(f"\ntokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls", flush=True)
