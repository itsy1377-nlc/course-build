#!/usr/bin/env python3
"""Collect a pool of real granite-3b week 2 answers, once.

The point is to stop spending calls per hypothesis. Every candidate for
"tighten the schema so the retry fires honestly" is a rule over the SAME
answers, so collect the answers once and score the rules offline.

Records, per call: the raw text, whether extract_json read it, the parsed
answer, and the derived facts a candidate rule might key on (indicator count,
indicator lengths, indicator casing and punctuation, the confidence value and
its granularity, verdict and category).

Writes /tmp/w2_pool.json. Prints no key and no answer text.
"""
import json, os, re, sys, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w2-eval-key").read().strip())
MODEL = sys.argv[1] if len(sys.argv) > 1 else "granite-3b"
os.environ["ITSY1377_MODEL"] = MODEL
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40

g = {"__name__": "__main__"}
src = open("/tmp/w2_prewritten.py").read()
src = re.sub(r"try:\n\s+import piplite\n.*?except ImportError:\n\s+pass[^\n]*\n", "", src, flags=re.S)
exec(compile(src, "prewritten", "exec"), g)
exec(compile(open("/tmp/w2_solution_fns.py").read(), "solution", "exec"), g)
g["SHOW_CALL_TOKENS"] = False

EMAILS = ["001", "002", "003", "004"]
pool = []
print(f"model={MODEL}  n={N} per email  ({N*len(EMAILS)} calls)", flush=True)

for eid in EMAILS:
    parsed = g["load_email"](eid)
    prompt = g["build_classify_prompt"](parsed)
    for i in range(N):
        raw = g["ask_model"](prompt)
        data = g["extract_json"](raw)
        rec = {"email": eid, "n": i,
               "stop_reason": g["LAST_CALL"]["stop_reason"],
               "raw_len": len(raw or ""),
               "loaded": isinstance(data, dict),
               "schema_problems": g["schema_errors"](data, g["OUTPUT_SCHEMA"])}
        if isinstance(data, dict):
            ind = data.get("indicators")
            rec.update({
                "keys": sorted(data.keys()),
                "verdict": data.get("verdict"),
                "category": data.get("category"),
                "confidence": data.get("confidence"),
                "n_indicators": len(ind) if isinstance(ind, list) else None,
                "ind_lens": [len(x) for x in ind if isinstance(x, str)] if isinstance(ind, list) else None,
                "ind_words": [len(x.split()) for x in ind if isinstance(x, str)] if isinstance(ind, list) else None,
                "ind_has_upper": [any(c.isupper() for c in x) for x in ind if isinstance(x, str)] if isinstance(ind, list) else None,
                "ind_has_punct": [bool(re.search(r"[.,;:!?]", x)) for x in ind if isinstance(x, str)] if isinstance(ind, list) else None,
                # does the indicator quote something actually in the email?
                "ind_in_body": [x.lower() in parsed["body_text"].lower()
                                for x in ind if isinstance(x, str)] if isinstance(ind, list) else None,
            })
        else:
            rec["raw_head"] = (raw or "")[:120]
        pool.append(rec)
    done = [r for r in pool if r["email"] == eid]
    nload = sum(1 for r in done if r["loaded"])
    nfail = sum(1 for r in done if r["schema_problems"])
    cnt = collections.Counter(r.get("n_indicators") for r in done)
    print(f"  {eid}: loaded {nload}/{len(done)}  schema-fail {nfail}/{len(done)}  "
          f"indicator counts {dict(sorted(cnt.items(), key=lambda kv: (kv[0] is None, kv[0])))}", flush=True)

json.dump(pool, open("/tmp/w2_pool.json", "w"), indent=1)
print(f"\nwrote /tmp/w2_pool.json  ({len(pool)} answers)", flush=True)
print(f"tokens this run: {g['USAGE']['total']} over {g['USAGE']['calls']} calls", flush=True)
