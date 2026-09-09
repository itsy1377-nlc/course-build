#!/usr/bin/env python3
"""Confirmatory run. Thresholds C1-C4 were written before this printed a row.

C1  017: withheld malicious >=6/8, reputation benign >=7/8, urls benign >=7/8,
         recipient malicious >=7/8
C2  018: withheld malicious >=7/8, reputation benign >=7/8, urls malicious >=7/8,
         recipient malicious >=7/8
C4  known_names=KNOWN_NAMES in load_email() moves no arm by more than 1 in 8
"""
import collections, json, os, sys

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W4_MODEL", "granite-3b")

g = {"__name__": "__main__"}
_o = sys.stdout; sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w4_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _o
g["SHOW_CALL_TOKENS"] = False

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
TOOLS = ["check_sender_reputation", "check_urls", "lookup_recipient"]
WITHHELD = {"status": "no record available",
            "notes": "This lookup returned nothing for this message."}


def forced(parsed, tool):
    msgs = g["start_messages"](parsed, "Facts about the reported email:\n\n"
                               + g["format_facts"](g["build_facts"](parsed)))
    name = tool or "check_sender_reputation"
    args = json.dumps({"sender": parsed["from_address"]} if name == "check_sender_reputation"
                      else {"hosts": parsed["url_hosts"]} if name == "check_urls"
                      else {"address": (parsed["to"] or [""])[0]})
    call = {"id": "call_forced_" + name, "type": "function",
            "function": {"name": name, "arguments": args}}
    result = g["run_tool"](name, args, parsed) if tool else dict(WITHHELD)
    msgs = msgs + [{"role": "assistant", "content": None, "tool_calls": [call]},
                   g["tool_result_message"](call, result),
                   {"role": "user", "content": "The tool result is above. Now judge the"
                    " reported email.\n\n" + g["schema_text"](g["OUTPUT_SCHEMA"])}]
    text, stop, message, ignored = g["ask_with_tools"](msgs, tools=None)
    data = g["extract_json"](text)
    return data.get("verdict") if isinstance(data, dict) else None


CRITERIA = {
    "017": [("withheld", None, "malicious", 6), ("reputation", TOOLS[0], "benign", 7),
            ("urls", TOOLS[1], "benign", 7), ("recipient", TOOLS[2], "malicious", 7)],
    "018": [("withheld", None, "malicious", 7), ("reputation", TOOLS[0], "benign", 7),
            ("urls", TOOLS[1], "malicious", 7), ("recipient", TOOLS[2], "malicious", 7)],
}

print(f"model={os.environ['ITSY1377_MODEL']}  n={N}   FRESH RUN, thresholds fixed first")
print()
print(f"{'id':<5}{'arm':<13}{'required':<28}{'got':<24}{'verdict'}")
print("-" * 88)
allpass, out = True, {}
for eid, rows in CRITERIA.items():
    parsed = g["load_email"](eid)
    out[eid] = {}
    for label, tool, want, floor in rows:
        c = collections.Counter(forced(parsed, tool) for _ in range(N))
        got = c.get(want, 0)
        ok = got >= floor
        allpass = allpass and ok
        out[eid][label] = {"counts": {str(k): v for k, v in c.items()},
                           "want": want, "floor": floor, "got": got, "pass": ok}
        shown = " ".join(f"{str(k)[:9]}:{v}" for k, v in c.most_common())
        print(f"{eid:<5}{label:<13}{want + ' >= ' + str(floor) + '/' + str(N):<28}"
              f"{shown:<24}{'PASS' if ok else 'FAIL'}")
    print()

print("C1" if out["017"] and all(v["pass"] for v in out["017"].values()) else "C1",
      "017:", "PASS" if all(v["pass"] for v in out["017"].values()) else "FAIL")
print("C2 018:", "PASS" if all(v["pass"] for v in out["018"].values()) else "FAIL")

# C4: does known_names change any verdict?
print()
print("C4  known_names=KNOWN_NAMES in load_email(), all six emails")
print(f"{'id':<5}{'mismatch off':<16}{'mismatch on':<16}{'without':<22}{'with':<22}{'moved'}")
print("-" * 96)
c4 = {}
for eid in ["003", "008", "009", "017", "018", "019"]:
    a = g["load_email"](eid)
    b = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    ca = collections.Counter(forced(a, "check_sender_reputation") for _ in range(N))
    cb = collections.Counter(forced(b, "check_sender_reputation") for _ in range(N))
    top_a = max(ca, key=ca.get)
    moved = N - cb.get(top_a, 0)
    c4[eid] = {"without": {str(k): v for k, v in ca.items()},
               "with": {str(k): v for k, v in cb.items()},
               "mismatch_without": a["display_name_mismatch"],
               "mismatch_with": b["display_name_mismatch"], "moved": moved}
    f = lambda c: " ".join(f"{str(k)[:9]}:{v}" for k, v in c.most_common())
    print(f"{eid:<5}{str(a['display_name_mismatch']):<16}{str(b['display_name_mismatch']):<16}"
          f"{f(ca):<22}{f(cb):<22}{moved}/{N}")
worst = max(v["moved"] for v in c4.values())
print()
print(f"C4: {'PASS' if worst <= 1 else 'FAIL'}  (largest shift {worst}/{N}, allowed 1)")

with open(os.environ.get("W4_OUT", "/home/aaron/w4/confirm.json"), "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N,
               "C1_C2": out, "C4": c4}, h, indent=1)
