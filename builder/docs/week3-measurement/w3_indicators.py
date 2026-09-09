#!/usr/bin/env python3
"""Do the model's stated indicators change when the facts block is added?

The reworded objective 3.2 asks the student to compare indicators before and
after. That only works if they move. If they are as insensitive as the
verdicts, one undemonstrable objective has been swapped for another.

Measured three ways per email, because "different" needs a definition:
  overlap   how many indicator strings are shared, after lowercasing
  new       indicators present only in the grounded run
  grounded  grounded indicators that quote a value from the facts block
The last one is the one that matters: it says the facts reached the reasoning.
"""
import json, os, re, sys, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W3MODEL", "granite-3b")
g = {"__name__": "__main__"}
exec(compile(open("/tmp/w3_prewritten.py").read(), "pre", "exec"), g)
exec(compile(open("/tmp/w3_solution_fns.py").read(), "sol", "exec"), g)
g["SHOW_CALL_TOKENS"] = False
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
EMAILS = ["001", "004", "005", "006", "017", "025"]


def norm(items):
    return {re.sub(r"[^a-z0-9 ]", " ", str(s).lower()).strip() for s in (items or [])}


def facts_tokens(facts_text):
    """Distinctive values from the facts block, for spotting quotation."""
    out = set()
    for line in facts_text.split("\n"):
        if ":" not in line:
            continue
        val = line.split(":", 1)[1].strip().strip("[]'\" ")
        for piece in re.split(r"[,\s]+", val):
            piece = piece.strip("'\"[] ").lower()
            if len(piece) > 6 and piece not in ("false", "true", "none"):
                out.add(piece)
    return out


print(f"model={os.environ['ITSY1377_MODEL']}  n={N} per email per condition\n")
print(f"{'id':<5}{'plain ind':<11}{'grnd ind':<10}{'shared':<9}{'new in grounded':<17}quotes a fact")
print("-" * 74)
rows = []
for eid in EMAILS:
    parsed = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    ftext = g["format_facts"](g["build_facts"](parsed))
    toks = facts_tokens(ftext)
    npl = ngr = shared = newc = quoting = 0
    for _ in range(N):
        p = g["classify_email"](parsed) or {}
        q = g["classify_grounded"](parsed) or {}
        a, b = norm(p.get("indicators")), norm(q.get("indicators"))
        npl += len(a); ngr += len(b)
        shared += len(a & b); newc += len(b - a)
        quoting += sum(1 for s in b if any(t in s for t in toks))
    rows.append({"email": eid, "plain": npl/N, "grounded": ngr/N,
                 "shared": shared/N, "new": newc/N, "quoting": quoting/N})
    print(f"{eid:<5}{npl/N:<11.1f}{ngr/N:<10.1f}{shared/N:<9.1f}{newc/N:<17.1f}{quoting/N:.1f}")
tot = len(rows)
print(f"\n  mean shared per email:   {sum(r['shared'] for r in rows)/tot:.2f}")
print(f"  mean new in grounded:    {sum(r['new'] for r in rows)/tot:.2f}")
print(f"  mean quoting a fact:     {sum(r['quoting'] for r in rows)/tot:.2f}")
json.dump(rows, open("/tmp/w3_indicators.json", "w"), indent=1)
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
