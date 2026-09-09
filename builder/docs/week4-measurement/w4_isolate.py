#!/usr/bin/env python3
"""What does the tool result actually change? Objective 4.3, de-confounded.

Cell 14's table puts classify_grounded() in the "no tools" column and
triage_with_tools() in the "with tools" column, and the written answer asks the
student to say what the tool's one fact changed. But the two arms differ in at
least five ways besides the tool result: different system instruction, a schema
on turn 1 or not, a known-good internal-hosts block present or absent, one turn
or two, and week 2's retry on or off. Any verdict difference is unattributable.

Four arms, chosen so the confound decomposes:

  A grounded   classify_grounded()  -- exactly what the "no tools" column shows
  B toolshape  the tools-shape prompt, one turn, schema attached, no tool
               offered. A vs B is the prompt-shape contribution alone.
  C withheld   the full two-turn exchange, a tool call made and answered, but
               the tool message carries no information. THE CONTROL: everything
               the tool machinery does, minus the fact.
  D real       the full two-turn exchange with the real tool record. Shipped.

C vs D is the honest measure of what the tool's fact is worth. A vs D is what
the notebook's table shows. If C already sits where D sits, the notebook's
table is reporting the prompt, not the tool.

Also runs D twice per email to get the run-to-run noise floor, because week 3
nearly shipped a demonstration that turned out to be noise.
"""
import collections, json, os, sys

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W4_MODEL", "granite-3b")

g = {"__name__": "__main__"}
_out = sys.stdout
sys.stdout = open(os.devnull, "w")
exec(compile(open("/tmp/w4_prewritten.py").read(), "pre", "exec"), g)
sys.stdout = _out
g["SHOW_CALL_TOKENS"] = False

N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
EMAILS = ["003", "008", "009", "017", "018", "019"]
GT = {r["id"][:3]: r for r in json.load(open("corpus/ground_truth.json"))["emails"]}

WITHHELD = {"status": "no record available",
            "notes": "This lookup returned nothing for this message."}
SECOND_TURN = ("The tool result is above. Now judge the reported email.\n\n")


def verdict_of(text):
    data = g["extract_json"](text)
    return data.get("verdict") if isinstance(data, dict) else None


def arm_grounded(parsed):
    return (g["classify_grounded"](parsed) or {}).get("verdict")


def arm_toolshape(parsed):
    """The with-tools prompt, one turn, schema attached, no tools offered."""
    msgs = g["start_messages"](parsed, "Facts about the reported email:\n\n"
                               + g["format_facts"](g["build_facts"](parsed)))
    user = msgs[1]["content"]
    # Drop TOOL_TURN (which forbids a verdict) and ask for the verdict instead.
    user = user[:user.rfind(g["TOOL_TURN"])].rstrip()
    user = user + "\n\nJudge the reported email.\n\n" + g["schema_text"](g["OUTPUT_SCHEMA"])
    text, stop, message, calls = g["ask_with_tools"](
        [{"role": "system", "content": g["TOOL_INSTRUCTIONS"]},
         {"role": "user", "content": user}], tools=None)
    return verdict_of(text)


def arm_twoturn(parsed, real):
    """The shipped two-turn exchange. real=False withholds the tool's fact."""
    msgs = g["start_messages"](parsed, "Facts about the reported email:\n\n"
                               + g["format_facts"](g["build_facts"](parsed)))
    text, stop, message, calls = g["ask_with_tools"](msgs)
    if not calls:
        return None, None            # prose path; no tool to withhold
    call = calls[0]
    name = call["function"]["name"]
    result = (g["run_tool"](name, call["function"].get("arguments") or "{}", parsed)
              if real else dict(WITHHELD))
    msgs = msgs + [{"role": "assistant", "content": None, "tool_calls": calls},
                   g["tool_result_message"](call, result),
                   {"role": "user",
                    "content": SECOND_TURN + g["schema_text"](g["OUTPUT_SCHEMA"])}]
    text, stop, message, ignored = g["ask_with_tools"](msgs, tools=None)
    return verdict_of(text), name


print(f"model={os.environ['ITSY1377_MODEL']}  n={N} per arm per email")
print()
head = (f"{'id':<5}{'true':<11}{'A grounded':<20}{'B toolshape':<20}"
        f"{'C withheld':<20}{'D real':<20}")
print(head)
print("-" * len(head))

records = []
for eid in EMAILS:
    truth = GT[eid]["verdict"]
    parsed = g["load_email"](eid)
    arms = {k: collections.Counter() for k in "ABCD"}
    tools_seen = collections.Counter()
    d_pairs = 0          # D run twice: how often the two runs disagree
    cd_diff = 0          # C vs D disagreement, run for run
    for _ in range(N):
        arms["A"][arm_grounded(parsed)] += 1
        arms["B"][arm_toolshape(parsed)] += 1
        c, cname = arm_twoturn(parsed, real=False)
        d, dname = arm_twoturn(parsed, real=True)
        d2, _ = arm_twoturn(parsed, real=True)
        arms["C"][c] += 1
        arms["D"][d] += 1
        if dname:
            tools_seen[dname] += 1
        if d is not None and d2 is not None and d != d2:
            d_pairs += 1
        if c is not None and d is not None and c != d:
            cd_diff += 1

    def fmt(c):
        return " ".join(f"{str(k)[:9]}:{v}" for k, v in c.most_common())
    print(f"{eid:<5}{truth:<11}{fmt(arms['A']):<20}{fmt(arms['B']):<20}"
          f"{fmt(arms['C']):<20}{fmt(arms['D']):<20}")
    records.append({"email": eid, "truth": truth, "n": N,
                    "A_grounded": {str(k): v for k, v in arms["A"].items()},
                    "B_toolshape": {str(k): v for k, v in arms["B"].items()},
                    "C_withheld": {str(k): v for k, v in arms["C"].items()},
                    "D_real": {str(k): v for k, v in arms["D"].items()},
                    "tool_asked": dict(tools_seen),
                    "D_vs_D_disagree": d_pairs,
                    "C_vs_D_disagree": cd_diff})

print()
print("The two numbers that decide it, per email:")
print(f"{'id':<5}{'C vs D differ':<16}{'D vs D differ (noise)':<24}{'tool asked'}")
print("-" * 70)
for r in records:
    tools = " ".join(f"{k.replace('check_','').replace('lookup_','')}:{v}"
                     for k, v in r["tool_asked"].items())
    print(f"{r['email']:<5}{str(r['C_vs_D_disagree']) + '/' + str(N):<16}"
          f"{str(r['D_vs_D_disagree']) + '/' + str(N):<24}{tools}")

path = os.environ.get("W4_OUT", "/home/aaron/w4/isolate.json")
with open(path, "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N,
               "records": records}, h, indent=1)
print()
print("written:", path)
