#!/usr/bin/env python3
"""Read every pass result and print the comparison the prereg asks for.

    python3 w7_summarise.py RESULTS_DIR

Prints one row per pass, then the aggregate per arm, then the three checks the
pre-registration fixed in advance. It computes nothing the pass files do not
already hold, except the aggregates and the digest comparison.
"""
import json
import sys
from collections import Counter
from pathlib import Path


def main():
    d = Path(sys.argv[1])
    runs = [json.load(open(p)) for p in sorted(d.glob("*.json"))]
    if not runs:
        raise SystemExit(f"no result files in {d}")

    print(f"{'pass':<8}{'model':<12}{'set':<10}{'n':>3} {'corr':>5}{'acc':>7}"
          f"{'fp':>4}{'fn':>4}{'nd':>4}{'esc':>6}{'secs':>7}{'tokens':>9}")
    for r in runs:
        c = r["counts"]
        print(f"{r['pass']:<8}{r['model']:<12}{r['set']:<10}{r['emails']:>3} "
              f"{c['correct']:>5}{c['accuracy']:>7.3f}{c['false_positives']:>4}"
              f"{c['false_negatives']:>4}{c['no_decision']:>4}"
              f"{r['escalation_agreement']:>4}/{r['emails']:<1}"
              f"{r['seconds']:>7.1f}{r['session_tokens']['total']:>9}")

    print()
    for model in sorted({r["model"] for r in runs}):
        arm = [r for r in runs if r["model"] == model]
        n = sum(r["emails"] for r in arm)
        corr = sum(r["counts"]["correct"] for r in arm)
        fp = sum(r["counts"]["false_positives"] for r in arm)
        fn = sum(r["counts"]["false_negatives"] for r in arm)
        nd = sum(r["counts"]["no_decision"] for r in arm)
        esc = sum(r["escalation_agreement"] for r in arm)
        accs = [r["counts"]["accuracy"] for r in arm]
        print(f"  {model:<12} {len(arm)} pass(es), {corr}/{n} = {corr/n:.3f} "
              f"aggregate | per-pass {min(accs):.3f}-{max(accs):.3f} | "
              f"fp {fp} fn {fn} nd {nd} | escalation agreement {esc}/{n} "
              f"= {esc/n:.3f}")

    print("\nchecks the pre-registration fixed in advance")
    # 1. input digests identical across passes on the same set
    for setname in sorted({r["set"] for r in runs}):
        same = {json.dumps(r["input_digests"]["emails"], sort_keys=True)
                for r in runs if r["set"] == setname}
        print(f"  input digests identical across {setname} passes: "
              f"{'yes' if len(same) == 1 else 'NO — these passes are not comparable'}")
    # 2. no false schema problem on a well-formed summary
    bad = [(r["pass"], r["model"], r["schema_problem_rows"])
           for r in runs if r["schema_problem_rows"]]
    print(f"  rows carrying a schema problem: "
          f"{'none' if not bad else bad}")
    # 3. every note six lines
    notbad = [(r['pass'], r['model'], r["notes_not_six_lines"])
              for r in runs if r["notes_not_six_lines"]]
    print(f"  notes that are not six lines:   "
          f"{'none' if not notbad else notbad}")
    # 4. every email produced a row
    counts = {(r["set"], r["emails"]) for r in runs}
    print(f"  rows per pass, by set: {sorted(counts)}")

    print("\nguardrail fires, summed per arm")
    for model in sorted({r["model"] for r in runs}):
        tot = Counter()
        for r in runs:
            if r["model"] == model:
                tot.update(r["guardrail_fires"])
        print(f"  {model:<12} {dict(tot)}")

    print("\nverdict stability: emails whose verdict moved between passes of one arm")
    for model in sorted({r["model"] for r in runs}):
        arm = [r for r in runs if r["model"] == model]
        if len(arm) < 2:
            continue
        byid = {}
        for r in arm:
            for e in r["per_email"]:
                byid.setdefault(e["email_id"], []).append(e["verdict"])
        moved = {k: v for k, v in byid.items() if len(set(map(str, v))) > 1}
        print(f"  {model:<12} {len(moved)} of {len(byid)} moved"
              + (f": {sorted(moved)}" if moved else ""))


if __name__ == "__main__":
    main()
