#!/usr/bin/env python3
"""When the model writes a sentence beside its tool call, does the sentence
name the tool it actually called?

96% of tool-call replies on this stack carry answer text, and the text reads
like "I'll check the sender reputation first". If the course is going to stop
telling students that slot is empty, it has to know whether what lands there
can be trusted, because a sentence that names a different tool than the call
is a worse thing to put in front of a beginner than an empty slot.
"""
import collections, json, os, re, sys, urllib.request

BASE = "http://127.0.0.1:4000/v1"
KEY = open("/root/.w3-eval-key").read().strip()
MODEL = os.environ.get("W4_MODEL", "granite-3b")
g = {"__name__": "__main__"}
_o = sys.stdout; sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w4_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _o

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
EMAILS = ["003", "008", "009", "017", "018", "019"]

# What a sentence has to contain to be read as naming each tool.
SAYS = {
    "check_sender_reputation": r"sender'?s? reputation|reputation of the sender|check[_ ]sender",
    "check_urls": r"\burls?\b|link host|allowlist|blocklist|check[_ ]urls",
    "lookup_recipient": r"recipient|who (?:it|the message) was sent to|lookup[_ ]recipient",
}


def said(text):
    hits = [name for name, pat in SAYS.items() if re.search(pat, text, re.I)]
    return hits[0] if len(hits) == 1 else ("several" if hits else "none")


def call(parsed, with_playbook):
    facts = g["format_facts"](g["build_facts"](parsed))
    user = "Facts about the reported email:\n\n" + facts
    if with_playbook:
        user += "\n\nThe triage playbook:\n\n" + g["PLAYBOOK"].strip()
    user += ("\n\nThe reported email:\n\n" + parsed["body_text"]
             + "\n\nValues you may pass to a tool for this message:"
             + "\n  sender:  " + str(parsed["from_address"])
             + "\n  hosts:   " + str(parsed["url_hosts"])
             + "\n  address: " + str((parsed["to"] or [""])[0])
             + "\n\n" + g["TOOL_TURN"])
    payload = {"model": MODEL, "temperature": 0.2, "max_tokens": 1024,
               "reasoning_effort": "none", "tools": g["TOOL_SPECS"],
               "messages": [{"role": "system", "content": g["TOOL_INSTRUCTIONS"]},
                            {"role": "user", "content": user}]}
    req = urllib.request.Request(
        BASE + "/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + KEY,
                 "User-Agent": "itsy1377-eval/w4saydo"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.loads(r.read())
    m = ((d.get("choices") or [{}])[0].get("message") or {})
    calls = m.get("tool_calls") or []
    return (m.get("content") or "").strip(), (calls[0]["function"]["name"] if calls else None)


print(f"model={MODEL}  n={N} per email per shape")
print()
print(f"{'id':<5}{'shape':<10}{'agree':<10}{'disagree':<10}{'no sentence':<13}{'a disagreement'}")
print("-" * 110)
agree = disagree = nosent = 0
rows, examples = [], []
for eid in EMAILS:
    parsed = g["load_email"](eid)
    for label, pb in (("cell 8", False), ("cell 14", True)):
        a = d_ = ns = 0
        ex = ""
        for _ in range(N):
            text, name = call(parsed, pb)
            if name is None:
                continue
            if not text:
                ns += 1
                continue
            s = said(text)
            if s == name:
                a += 1
            elif s in ("none", "several"):
                ns += 1
            else:
                d_ += 1
                if not ex:
                    ex = f"said {s.replace('check_','')}, called {name.replace('check_','')}"
                    examples.append({"email": eid, "shape": label,
                                     "said": s, "called": name, "text": text[:200]})
        print(f"{eid:<5}{label:<10}{a:<10}{d_:<10}{ns:<13}{ex}")
        rows.append({"email": eid, "shape": label, "agree": a,
                     "disagree": d_, "unreadable": ns, "n": N})
        agree += a; disagree += d_; nosent += ns
    print()

print(f"OVERALL  agree {agree}   disagree {disagree}   no readable sentence {nosent}")
with open(os.environ.get("W4_OUT", "/home/aaron/w4/saydo.json"), "w") as h:
    json.dump({"model": MODEL, "n": N, "rows": rows,
               "totals": {"agree": agree, "disagree": disagree, "unreadable": nosent},
               "disagreement_examples": examples[:12]}, h, indent=1)
