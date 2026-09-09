#!/usr/bin/env python3
"""Is "zero shared indicators" evidence of grounding, or just rewording?

The first indicator run found no shared indicator strings between the plain and
grounded runs on any email. That looks decisive until you ask the obvious
control question: how many indicators do TWO PLAIN RUNS of the same email
share? If the answer is also near zero, the model simply rephrases every time
and the statistic says nothing about the facts block.

Three comparisons per email, same number of calls each:
  plain vs plain        the control
  grounded vs grounded  the same control on the other side
  plain vs grounded     the claim
"""
import json, os, re, sys

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W3MODEL", "granite-3b")
g = {"__name__": "__main__"}
exec(compile(open("/tmp/w3_prewritten.py").read(), "pre", "exec"), g)
exec(compile(open("/tmp/w3_solution_fns.py").read(), "sol", "exec"), g)
g["SHOW_CALL_TOKENS"] = False
EMAILS = ["001", "005", "017", "025"]


def norm(items):
    return {re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).strip() for s in (items or [])}


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


print(f"model={os.environ['ITSY1377_MODEL']}   overlap is Jaccard, 0 = nothing shared\n")
print(f"{'id':<6}{'plain vs plain':<17}{'grnd vs grnd':<15}{'plain vs grounded':<19}")
print("-" * 60)
rows = []
for eid in EMAILS:
    parsed = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    p1 = norm((g["classify_email"](parsed) or {}).get("indicators"))
    p2 = norm((g["classify_email"](parsed) or {}).get("indicators"))
    q1 = norm((g["classify_grounded"](parsed) or {}).get("indicators"))
    q2 = norm((g["classify_grounded"](parsed) or {}).get("indicators"))
    pp, qq, pq = jaccard(p1, p2), jaccard(q1, q2), jaccard(p1, q1)
    rows.append({"email": eid, "plain_vs_plain": pp, "grnd_vs_grnd": qq, "plain_vs_grnd": pq})
    print(f"{eid:<6}{pp:<17.2f}{qq:<15.2f}{pq:<19.2f}")
n = len(rows)
print(f"\n  mean plain vs plain:      {sum(r['plain_vs_plain'] for r in rows)/n:.2f}")
print(f"  mean grounded vs grounded:{sum(r['grnd_vs_grnd'] for r in rows)/n:.2f}")
print(f"  mean plain vs grounded:   {sum(r['plain_vs_grnd'] for r in rows)/n:.2f}")
json.dump(rows, open("/tmp/w3_ind_control.json", "w"), indent=1)
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
