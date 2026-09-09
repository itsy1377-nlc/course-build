#!/usr/bin/env python3
"""What does a week 5 run actually cost, and what does the reading claim?

w5-content.md says the first request is "about 1,500 tokens", each finished
step adds "roughly another 100 tokens", and over twenty steps you pay for 190
extra pieces of history. Its own arithmetic therefore implies
20 x 1500 + 190 x 100 = 49,000 tokens for the uncapped run.

Objective 5.3 is "Compare the token cost of a capped run and an uncapped run",
so both totals have to be numbers this course has measured rather than
numbers it has estimated. Nothing in the repository records them.

This runs the capped loop on 012 and then the uncapped twenty-step loop that
cell 15 ships, recording the size of every single request.
"""
import json, os, sys

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W5_MODEL", "granite-3b")

g = {"__name__": "__main__"}
_o = sys.stdout; sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w5_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _o
g["SHOW_CALL_TOKENS"] = False

# Record the prompt size of every call by wrapping the one function that sends.
PROMPTS = []
_real = g["send_request"]
def spy(payload):
    reply = _real(payload)
    usage = (reply or {}).get("usage") or {}
    PROMPTS.append({"prompt": usage.get("prompt_tokens"),
                    "answer": usage.get("completion_tokens"),
                    "total": usage.get("total_tokens")})
    return reply
g["send_request"] = spy

parsed = g["load_email"]("012", known_names=g["KNOWN_NAMES"])

g["start_run"]()
PROMPTS.clear()
capped = g["run_loop"](parsed, g["loop_prompt"](parsed))
capped_calls = list(PROMPTS)
capped_total = capped["tokens"]

g["start_run"]()
PROMPTS.clear()
messages = g["start_messages"](parsed, g["loop_prompt"](parsed))
runaway = g["new_trace"](parsed)
step = 0
while step < 20:
    step += 1
    answer, finish, turn, calls = g["ask_with_tools"](messages)
    call = g["first_call"](calls, answer, runaway)
    result = g["run_tool"](call["name"], call["arguments"], parsed)
    g["append_turn"](messages, turn, call, result, runaway)
runaway_calls = list(PROMPTS)
runaway_total = runaway["tokens"]

print(f"model={os.environ['ITSY1377_MODEL']}")
print()
print("CAPPED run on 012, the one cell 14 makes")
print(f"  steps: {len(capped['steps'])}  stop: {capped['stop_reason']}  "
      f"total: {capped_total} tokens")
for i, c in enumerate(capped_calls, 1):
    print(f"    call {i}: prompt {c['prompt']}, answer {c['answer']}")

print()
print("UNCAPPED twenty-step run on 012, the one cell 15 makes")
print(f"  steps: {len(runaway['steps'])}  total: {runaway_total} tokens")
first = runaway_calls[0]["prompt"]
print(f"  first request:        {first} tokens   (page says 'about 1,500')")
deltas = [runaway_calls[i]["prompt"] - runaway_calls[i - 1]["prompt"]
          for i in range(1, len(runaway_calls))]
print(f"  per-step growth:      min {min(deltas)}, max {max(deltas)}, "
      f"mean {sum(deltas) / len(deltas):.0f}   (page says 'roughly another 100')")
implied = 20 * 1500 + 190 * 100
print(f"  the page's arithmetic: 20 x 1500 + 190 x 100 = {implied}")
print(f"  measured:              {runaway_total}   "
      f"({(runaway_total - implied) / implied * 100:+.0f}% against the page)")
tools = [s["tool"] for s in runaway["steps"]]
repeats = sum(1 for i, t in enumerate(tools) if t in tools[:i])
firstrep = next((i + 1 for i, t in enumerate(tools) if t in tools[:i]), None)
print(f"  repeated tools:        {repeats} of 20, first repeat at step {firstrep}")
print(f"  usable tools on 012:   {runaway['usable_tools']}")
print()
print(f"5.3 comparison: capped {capped_total} vs uncapped {runaway_total} "
      f"({runaway_total / max(capped_total, 1):.1f}x)")

with open(os.environ.get("W5_OUT", "/home/aaron/w4/w5cost.json"), "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"],
               "capped": {"steps": len(capped["steps"]),
                          "stop_reason": capped["stop_reason"],
                          "total": capped_total, "calls": capped_calls},
               "uncapped": {"steps": len(runaway["steps"]), "total": runaway_total,
                            "calls": runaway_calls, "tools": tools,
                            "repeats": repeats, "first_repeat_step": firstrep},
               "page_arithmetic": implied}, h, indent=1)
print("written")
