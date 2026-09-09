#!/usr/bin/env python3
"""Does adding the facts block move the verdict, and on which emails?

Objective 3.2 is "report which verdicts changed after you added the facts
block". The blind run saw neither of the two emails chosen to demonstrate it
move, in either of two runs, while a third moved for the wrong reason.

The corpus already records the design: every email carries body_only_read, the
verdict its body alone should produce, beside the true verdict. Where those
differ, the facts are supposed to move the answer. This measures whether they
actually do, on every email week 3 might use -- the six the lab runs now, plus
the two the corpus tags for week 3 that the lab never runs.
"""
import json, os, re, sys, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = "granite-3b"

g = {"__name__": "__main__"}
exec(compile(open("/tmp/w3_prewritten.py").read(), "pre", "exec"), g)
exec(compile(open("/tmp/w3_solution_fns.py").read(), "sol", "exec"), g)
g["SHOW_CALL_TOKENS"] = False

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
EMAILS = sys.argv[2].split(",") if len(sys.argv) > 2 else [
    "007","008","009","010","013","014","015","018","021","023","024"]

gt = {r["id"][:3]: r for r in json.load(open("corpus/ground_truth.json"))["emails"]}

print(f"model=granite-3b  n={N} per email per condition")
print(f"{'id':<5}{'true':<11}{'designed':<22}{'body alone':<22}{'with facts':<22}moved")
print("-" * 104)

out = []
for eid in EMAILS:
    truth = gt[eid]["verdict"]
    bor = gt[eid].get("body_only_read")
    parsed = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    facts_text = g["format_facts"](g["build_facts"](parsed))
    plain, grounded, moved, right_way = collections.Counter(), collections.Counter(), 0, 0
    for _ in range(N):
        p = g["classify_email"](parsed) or {}
        q = g["classify_grounded"](parsed) or {}
        pv, qv = p.get("verdict"), q.get("verdict")
        plain[pv] += 1
        grounded[qv] += 1
        if pv and qv and pv != qv:
            moved += 1
            if qv == truth:
                right_way += 1
    design = f"{bor} -> {truth}" if bor != truth else "no move designed"
    def fmt(c):
        return " ".join(f"{k}:{v}" for k, v in sorted(c.items(), key=lambda kv: str(kv[0])))
    print(f"{eid:<5}{truth:<11}{design:<22}{fmt(plain):<22}{fmt(grounded):<22}"
          f"{moved}/{N}" + (f" ({right_way} toward truth)" if moved else ""))
    out.append({"email": eid, "truth": truth, "body_only_read": bor,
                "plain": dict(plain), "grounded": dict(grounded),
                "moved": moved, "moved_toward_truth": right_way, "n": N,
                "facts_block": facts_text})

json.dump(out, open("/tmp/w3_ground.json", "w"), indent=1)
print(f"\ntokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
