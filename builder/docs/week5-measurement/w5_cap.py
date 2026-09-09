#!/usr/bin/env python3
"""Does week 5's step cap ever fire, and does the candidate fix make it fire?

Objective 5.1 is "Build a triage loop with a four-step cap and a stop
condition". The cap is half of it and it is the week's headline control. The
loop is `while step < max_steps and tools_left(trace)` with MAX_STEPS = 4 and
at most three usable tools, so out_of_room() can only say step_cap after four
steps with a tool still untouched, which needs two repeated tools on a
three-tool email. LOOP_INSTRUCTIONS tells the model not to repeat.

Probe 1 runs the shipped loop and counts stop reasons.
Probe 2 runs the student's own run_loop() with max_steps=2 on email 012, which
should be step_cap by construction, and on email 005, which should not be
because decisive_stop() ends it. 005 is the discriminating control: it shows
the cell reports the cap rather than reporting max_steps=2.
"""
import collections, json, os, sys

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W5_MODEL", "granite-3b")

g = {"__name__": "__main__"}
_o = sys.stdout; sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w5_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _o
g["SHOW_CALL_TOKENS"] = False

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
LAB_EMAILS = ["011", "007", "005", "010", "004", "012"]


def one_run(eid, max_steps=None):
    parsed = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    g["start_run"]()
    kw = {} if max_steps is None else {"max_steps": max_steps}
    trace = g["run_loop"](parsed, g["loop_prompt"](parsed), **kw)
    tools = [s["tool"] for s in trace["steps"]]
    repeat_at = next((i + 1 for i, t in enumerate(tools) if t in tools[:i]), None)
    return {"stop": trace["stop_reason"], "steps": len(trace["steps"]),
            "tools": tools, "repeat_at": repeat_at, "tokens": trace["tokens"],
            "usable": trace["usable_tools"]}


print(f"model={os.environ['ITSY1377_MODEL']}  n={N}")
print()
print("PROBE 1  the shipped loop, MAX_STEPS =", g["MAX_STEPS"])
print(f"{'id':<5}{'usable':<8}{'stop reasons':<52}{'steps':<10}{'repeats'}")
print("-" * 92)
p1, cap_hits, total = [], 0, 0
for eid in LAB_EMAILS:
    stops, steps, repeats = collections.Counter(), collections.Counter(), 0
    firsts = collections.Counter()
    for _ in range(N):
        r = one_run(eid)
        stops[r["stop"]] += 1
        steps[r["steps"]] += 1
        total += 1
        if r["stop"] == "step_cap":
            cap_hits += 1
        if r["repeat_at"]:
            repeats += 1
            firsts[r["repeat_at"]] += 1
        p1.append(dict(r, email=eid))
    f = lambda c: " ".join(f"{k}:{v}" for k, v in c.most_common())
    print(f"{eid:<5}{len(p1[-1]['usable']):<8}{f(stops):<52}{f(steps):<10}"
          f"{repeats}/{N}" + (f" first at {f(firsts)}" if repeats else ""))

print()
print(f"P1a  step_cap fired {cap_hits} of {total} runs "
      f"({'CONFIRMED, under 3' if cap_hits < 3 else 'NOT confirmed'})")
allrep = collections.Counter(r["repeat_at"] for r in p1 if r["repeat_at"])
print(f"P1b  repeats by step position: {dict(allrep) or 'none at any position'}")

print()
print("PROBE 2  the candidate fix: the student's own run_loop at max_steps=2")
print(f"{'id':<5}{'expected':<14}{'stop reasons':<40}{'steps':<12}{'verdict'}")
print("-" * 88)
p2 = {}
for eid, want, why in (("012", "step_cap", "nothing decisive, 3 usable tools"),
                       ("005", "not step_cap", "trusted + allowlisted, decisive_benign")):
    stops, steps = collections.Counter(), collections.Counter()
    for _ in range(N):
        r = one_run(eid, max_steps=2)
        stops[r["stop"]] += 1
        steps[r["steps"]] += 1
    got = stops.get("step_cap", 0)
    ok = (got == N) if want == "step_cap" else (got == 0)
    f = lambda c: " ".join(f"{k}:{v}" for k, v in c.most_common())
    print(f"{eid:<5}{want:<14}{f(stops):<40}{f(steps):<12}{'PASS' if ok else 'FAIL'}")
    print(f"       ({why})")
    p2[eid] = {"stops": dict(stops), "steps": dict(steps), "want": want, "pass": ok}

print()
print("P2a 012 step_cap 8/8:", "PASS" if p2["012"]["pass"] else "FAIL")
print("P2b 012 exactly 2 steps:", "PASS" if p2["012"]["steps"].get(2) == N else "FAIL")
print("P2c 005 control is not step_cap:", "PASS" if p2["005"]["pass"] else "FAIL")

with open(os.environ.get("W5_OUT", "/home/aaron/w4/w5cap.json"), "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N,
               "probe1": p1, "probe1_step_cap_hits": cap_hits,
               "probe1_total": total,
               "repeat_positions": {str(k): v for k, v in allrep.items()},
               "probe2": p2}, h, indent=1)
print("written")
