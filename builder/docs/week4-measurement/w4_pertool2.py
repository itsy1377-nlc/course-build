#!/usr/bin/env python3
"""One withheld control PER TOOL, which probe 3 did not have.

Codex's objection to probe 3 is correct: its arms differ in tool NAME and
ARGUMENTS as well as in the returned fact, so only the reputation arm is
matched against the withheld arm (both carry the reputation name and the same
arguments). The urls and recipient arms show an outcome without establishing
that the result CONTENT produced it.

This pairs every tool with its own withheld twin: identical tool name,
identical arguments, identical everything, and the only difference is whether
the tool message carries the real record or "no record available". Three
matched pairs instead of one.
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
EMAILS = (sys.argv[2].split(",") if len(sys.argv) > 2 else ["017", "018"])
GT = {r["id"][:3]: r for r in json.load(open("corpus/ground_truth.json"))["emails"]}
TOOLS = ["check_sender_reputation", "check_urls", "lookup_recipient"]
WITHHELD = {"status": "no record available",
            "notes": "This lookup returned nothing for this message."}


def args_for(name, parsed):
    if name == "check_sender_reputation":
        return json.dumps({"sender": parsed["from_address"]})
    if name == "check_urls":
        return json.dumps({"hosts": parsed["url_hosts"]})
    return json.dumps({"address": (parsed["to"] or [""])[0]})


def run(parsed, name, real):
    """Same tool name, same arguments, both arms. Only the record differs."""
    msgs = g["start_messages"](parsed, "Facts about the reported email:\n\n"
                               + g["format_facts"](g["build_facts"](parsed)))
    args = args_for(name, parsed)
    call = {"id": "call_pair_" + name, "type": "function",
            "function": {"name": name, "arguments": args}}
    result = g["run_tool"](name, args, parsed) if real else dict(WITHHELD)
    msgs = msgs + [{"role": "assistant", "content": None, "tool_calls": [call]},
                   g["tool_result_message"](call, result),
                   {"role": "user", "content": "The tool result is above. Now judge the"
                    " reported email.\n\n" + g["schema_text"](g["OUTPUT_SCHEMA"])}]
    text, stop, message, ignored = g["ask_with_tools"](msgs, tools=None)
    data = g["extract_json"](text)
    return data.get("verdict") if isinstance(data, dict) else None


print(f"model={os.environ['ITSY1377_MODEL']}  n={N}")
print("Each pair holds tool name and arguments constant. Only the record differs.")
print()
print(f"{'id':<5}{'true':<11}{'tool':<26}{'withheld twin':<22}{'real record':<22}{'pair differs'}")
print("-" * 110)
out = []
for eid in EMAILS:
    truth = GT[eid]["verdict"]
    parsed = g["load_email"](eid)
    for name in TOOLS:
        w = collections.Counter()
        r = collections.Counter()
        differ = 0
        for _ in range(N):
            a = run(parsed, name, False)
            b = run(parsed, name, True)
            w[a] += 1
            r[b] += 1
            if a is not None and b is not None and a != b:
                differ += 1
        f = lambda c: " ".join(f"{str(k)[:9]}:{v}" for k, v in c.most_common())
        print(f"{eid:<5}{truth:<11}{name:<26}{f(w):<22}{f(r):<22}{differ}/{N}")
        out.append({"email": eid, "truth": truth, "tool": name, "n": N,
                    "withheld": {str(k): v for k, v in w.items()},
                    "real": {str(k): v for k, v in r.items()},
                    "pair_differs": differ})
    print()

with open(os.environ.get("W4_OUT", "/home/aaron/w4/pertool.json"), "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N, "rows": out}, h, indent=1)
print("written")
