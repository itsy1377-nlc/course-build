#!/usr/bin/env python3
"""Which tool does the model ask for, and what decides it?

Week 4 offers three tools and TOOL_TURN says "Call exactly one tool". A blind
student's run asked for check_sender_reputation on all six emails, so two of
run_tool()'s three branches never ran live, and email 018 -- whose designed
demonstration is a BLOCKLISTED link host -- was judged on its sender instead.

Three conditions, because the two shapes already in the notebook differ by
exactly one block and that is a natural experiment:

  bare      cell 8's shape:  facts + body + tool inputs + TOOL_TURN
  playbook  cell 14's shape: bare + the triage playbook   <- what students run
  filler    the discriminating control: bare + a block of neutral text matched
            to the playbook's length. If tool choice narrows here too, the
            cause is prompt length, not the playbook's content.

Also records, free, whether a reply carrying a tool call also carries answer
text -- cell 8 tells the student that slot is always empty.
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

N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
EMAILS = ["003", "008", "009", "017", "018", "019"]
PLAYBOOK = g["PLAYBOOK"].strip()

# Neutral text, matched to the playbook's length, saying nothing about senders,
# links or recipients. Same position, same shape, no triage content.
FILLER_ONE = (
    "Ticket handling notes (week 4 excerpt)\n\n"
    "1. Every reported message opens a ticket in the queue before any work starts.\n"
    "2. The ticket number is eight digits and never changes once it is issued.\n"
    "3. Tickets are worked oldest first unless a shift lead moves one to the top.\n"
    "4. A ticket left open past the end of a shift is handed over in the log.\n"
    "5. The handover log records the ticket number, the time and who took it.\n"
    "6. Two people never work the same ticket at once. The queue enforces this.\n"
    "7. A ticket closed by mistake is reopened by the shift lead, not by the queue.\n"
    "8. The queue keeps its own clock. Times in it are the times to quote.\n"
    "9. Notes typed into a ticket are kept for one year and then removed.\n"
    "10. A ticket with no notes at all is returned to the queue unclosed.\n"
    "11. The weekly count is taken from the queue on Monday morning.\n")
FILLER = FILLER_ONE
while len(FILLER) < len(PLAYBOOK):
    FILLER = FILLER + FILLER_ONE
FILLER = FILLER[:len(PLAYBOOK)]


def build(parsed, block):
    """One turn-1 message list. block is the middle section, or None."""
    facts = g["format_facts"](g["build_facts"](parsed))
    tool_inputs = ("Values you may pass to a tool for this message:"
                   "\n  sender:  " + str(parsed["from_address"])
                   + "\n  hosts:   " + str(parsed["url_hosts"])
                   + "\n  address: " + str((parsed["to"] or [""])[0]))
    user = "Facts about the reported email:\n\n" + facts
    if block is not None:
        user = user + "\n\n" + block[0] + "\n\n" + block[1]
    user = (user + "\n\nThe reported email:\n\n" + parsed["body_text"]
            + "\n\n" + tool_inputs + "\n\n" + g["TOOL_TURN"])
    return [{"role": "system", "content": g["TOOL_INSTRUCTIONS"]},
            {"role": "user", "content": user}]


CONDITIONS = [("bare", None),
              ("playbook", ("The triage playbook:", PLAYBOOK)),
              ("filler", ("Ticket handling notes:", FILLER))]

print(f"model={os.environ['ITSY1377_MODEL']}  n={N} per email per condition")
print(f"playbook block {len(PLAYBOOK)} chars, filler block {len(FILLER)} chars")
print()
print(f"{'id':<5}{'condition':<11}{'tools asked for':<58}{'no call':<9}{'text with call'}")
print("-" * 100)

records = []
for eid in EMAILS:
    parsed = g["load_email"](eid)
    for label, block in CONDITIONS:
        names, nocall, withtext, total = collections.Counter(), 0, 0, 0
        for _ in range(N):
            content, stop, message, calls = g["ask_with_tools"](build(parsed, block))
            if not calls:
                nocall += 1
                continue
            total += 1
            names[calls[0]["function"]["name"]] += 1
            if (content or "").strip():
                withtext += 1
        shown = " ".join(f"{k.replace('check_','').replace('lookup_','')}:{v}"
                         for k, v in names.most_common())
        print(f"{eid:<5}{label:<11}{shown:<58}{nocall:<9}{withtext}/{total}")
        records.append({"email": eid, "condition": label, "n": N,
                        "tools": dict(names), "no_call": nocall,
                        "text_with_call": withtext, "calls": total})
    print()

path = os.environ.get("W4_OUT", "/home/aaron/w4/choice.json")
with open(path, "w") as h:
    json.dump({"model": os.environ["ITSY1377_MODEL"], "n": N,
               "records": records}, h, indent=1)
print("written:", path)
