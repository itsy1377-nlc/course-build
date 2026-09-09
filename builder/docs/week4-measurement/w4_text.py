#!/usr/bin/env python3
"""Does a reply that carries a tool call also carry answer text?

Cell 8 prints, unconditionally: "One line above says the model sent no answer
text ... A reply that asks for a tool carries the request and no answer text."
The reading, cell 9 and cell 13's comment all say the same. The video's own
recorded run (content/video/runs/w4.json, granite4.2:3b on ollama, 2026-09-05)
has answer_text "", so the claim was true when it was measured.

send_request() OVERWRITES empty content with a notice, so nothing inside the
notebook can measure this. This talks to the endpoint directly and reads the
raw content field before anything touches it.

Two shapes: cell 8's (no playbook) and cell 14's (with playbook).
"""
import json, os, sys, urllib.request, collections

BASE = "http://127.0.0.1:4000/v1"
KEY = open("/root/.w3-eval-key").read().strip()
MODEL = os.environ.get("W4_MODEL", "granite-3b")

g = {"__name__": "__main__"}
_o = sys.stdout; sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w4_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _o

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
EMAILS = ["003", "008", "009", "017", "018", "019"]


def user_text(parsed, with_playbook):
    facts = g["format_facts"](g["build_facts"](parsed))
    body = ("Facts about the reported email:\n\n" + facts)
    if with_playbook:
        body += "\n\nThe triage playbook:\n\n" + g["PLAYBOOK"].strip()
    body += ("\n\nThe reported email:\n\n" + parsed["body_text"]
             + "\n\nValues you may pass to a tool for this message:"
             + "\n  sender:  " + str(parsed["from_address"])
             + "\n  hosts:   " + str(parsed["url_hosts"])
             + "\n  address: " + str((parsed["to"] or [""])[0])
             + "\n\n" + g["TOOL_TURN"])
    return body


def raw_call(parsed, with_playbook):
    payload = {"model": MODEL, "temperature": 0.2, "max_tokens": 1024,
               "reasoning_effort": "none",
               "messages": [{"role": "system", "content": g["TOOL_INSTRUCTIONS"]},
                            {"role": "user", "content": user_text(parsed, with_playbook)}],
               "tools": g["TOOL_SPECS"]}
    req = urllib.request.Request(
        BASE + "/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + KEY,
                 "User-Agent": "itsy1377-eval/w4text"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    ch = (d.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    return (msg.get("content") or ""), (msg.get("tool_calls") or []), ch.get("finish_reason")


print(f"model={MODEL}  n={N} per email per shape")
print()
print(f"{'id':<5}{'shape':<12}{'tool calls':<12}{'answer text NOT empty':<24}{'a first line'}")
print("-" * 110)
tot = collections.Counter()
samples = []
for eid in EMAILS:
    parsed = g["load_email"](eid)
    for label, pb in (("cell 8", False), ("cell 14", True)):
        withtext, calls_back, first = 0, 0, ""
        for _ in range(N):
            content, calls, finish = raw_call(parsed, pb)
            if calls:
                calls_back += 1
                tot["tool_call_replies"] += 1
                if content.strip():
                    withtext += 1
                    tot["with_text"] += 1
                    if not first:
                        first = content.strip().split("\n")[0][:52]
        print(f"{eid:<5}{label:<12}{str(calls_back)+'/'+str(N):<12}"
              f"{str(withtext)+'/'+str(calls_back):<24}{first}")
        samples.append({"email": eid, "shape": label, "n": N,
                        "tool_call_replies": calls_back, "with_text": withtext,
                        "example_first_line": first})
    print()

print(f"OVERALL: {tot['with_text']} of {tot['tool_call_replies']} replies that carried a "
      f"tool call also carried answer text.")
with open(os.environ.get("W4_OUT", "/home/aaron/w4/text.json"), "w") as h:
    json.dump({"model": MODEL, "n": N, "totals": dict(tot), "rows": samples}, h, indent=1)
