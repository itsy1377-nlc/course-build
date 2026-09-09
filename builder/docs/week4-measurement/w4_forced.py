#!/usr/bin/env python3
"""Which of the three tools moves which email, when the choice is taken away?

Week 4 lets the model pick one tool of three, so what a student sees is one
tool's effect on each email and no way to know what the other two would have
done. Cell 6 prints all three answers for 018 and says "Either tool alone tells
you half of it", and the self-check feedback asserts that on 018 check_urls
"flips the verdict to malicious". Neither claim has been measured on the
shipped stack.

This takes the choice away. For each email it runs the same two-turn exchange
four times over: once per tool, forced, plus the withheld control that carries
no fact at all. Everything else is identical, so the tool result is the only
thing that differs between arms. That is the matched-pair design objective 4.3
needs and does not have.
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
EMAILS = (sys.argv[2].split(",") if len(sys.argv) > 2
          else ["003", "008", "009", "017", "018", "019"])
GT = {r["id"][:3]: r for r in json.load(open("corpus/ground_truth.json"))["emails"]}
TOOLS = ["check_sender_reputation", "check_urls", "lookup_recipient"]
WITHHELD = {"status": "no record available",
            "notes": "This lookup returned nothing for this message."}


def forced(parsed, tool):
    """The shipped two-turn exchange with the tool call written by us, not the
    model. tool=None withholds the fact but keeps the whole exchange."""
    msgs = g["start_messages"](parsed, "Facts about the reported email:\n\n"
                               + g["format_facts"](g["build_facts"](parsed)))
    name = tool or "check_sender_reputation"
    if name == "check_sender_reputation":
        args = json.dumps({"sender": parsed["from_address"]})
    elif name == "check_urls":
        args = json.dumps({"hosts": parsed["url_hosts"]})
    else:
        args = json.dumps({"address": (parsed["to"] or [""])[0]})
    call = {"id": "call_forced_" + name, "type": "function",
            "function": {"name": name, "arguments": args}}
    result = g["run_tool"](name, args, parsed) if tool else dict(WITHHELD)
    msgs = msgs + [{"role": "assistant", "content": None, "tool_calls": [call]},
                   g["tool_result_message"](call, result),
                   {"role": "user",
                    "content": "The tool result is above. Now judge the reported"
                               " email.\n\n" + g["schema_text"](g["OUTPUT_SCHEMA"])}]
    text, stop, message, ignored = g["ask_with_tools"](msgs, tools=None)
    data = g["extract_json"](text)
    return (data.get("verdict") if isinstance(data, dict) else None), result


print(f"model={os.environ['ITSY1377_MODEL']}  n={N} per arm per email")
print("Every arm is the same two-turn exchange. Only the tool result differs.")
print()
head = (f"{'id':<5}{'true':<11}{'withheld':<22}{'reputation':<22}"
        f"{'urls':<22}{'recipient':<22}")
print(head); print("-" * len(head))

records = []
for eid in EMAILS:
    truth = GT[eid]["verdict"]
    parsed = g["load_email"](eid)
    arms = {k: collections.Counter() for k in ["withheld"] + TOOLS}
    facts = {}
    for _ in range(N):
        for tool in [None] + TOOLS:
            v, result = forced(parsed, tool)
            arms[tool or "withheld"][v] += 1
            if tool:
                facts[tool] = result
    def fmt(c):
        return " ".join(f"{str(k)[:9]}:{v}" for k, v in c.most_common())
    print(f"{eid:<5}{truth:<11}{fmt(arms['withheld']):<22}"
          f"{fmt(arms['check_sender_reputation']):<22}"
          f"{fmt(arms['check_urls']):<22}{fmt(arms['lookup_recipient']):<22}")
    records.append({"email": eid, "truth": truth, "n": N,
                    "arms": {k: {str(a): b for a, b in v.items()}
                             for k, v in arms.items()},
                    "tool_results": facts})

print()
print("Moved away from the withheld control, and did it land on the truth?")
print(f"{'id':<5}{'true':<11}{'tool':<26}{'moved':<10}{'toward truth'}")
print("-" * 70)
for r in records:
    base = max(r["arms"]["withheld"], key=r["arms"]["withheld"].get)
    for tool in TOOLS:
        c = r["arms"][tool]
        moved = sum(v for k, v in c.items() if k != base)
        right = c.get(r["truth"], 0)
        print(f"{r['email']:<5}{r['truth']:<11}{tool:<26}"
              f"{str(moved)+'/'+str(r['n']):<10}{str(right)+'/'+str(r['n'])}")

with open(os.environ.get("W4_OUT", "/home/aaron/w4/forced.json"), "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N,
               "records": records}, h, indent=1)
