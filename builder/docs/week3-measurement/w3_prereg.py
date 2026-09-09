#!/usr/bin/env python3
"""Codex's pre-registered decision rule for indicator-based objective 3.2.

The rule was fixed before any of these numbers were visible. It maps indicator
strings to canonical fact-field concepts, keeps only concepts stable across at
least 75% of replies, and asks two things of each email row:

    G - P contains at least one fact-field concept, and
    D = |P symmetric-difference G| / |P union G|  is at least 0.50

Pass on 4, 5 or 6 of six rows. Fail on 0, 1 or 2. Exactly 3 is borderline and
must be replicated at eight replies before deciding.

No synonym is added to CONCEPTS after results are visible.
"""
import json, math, os, re, sys, unicodedata, collections

os.environ.setdefault("ITSY1377_BASE_URL", "http://127.0.0.1:4000/v1")
os.environ.setdefault("ITSY1377_API_KEY", open("/root/.w3-eval-key").read().strip())
os.environ["ITSY1377_MODEL"] = os.environ.get("W3MODEL", "granite-3b")
g = {"__name__": "__main__"}
exec(compile(open("/tmp/w3_prewritten.py").read(), "pre", "exec"), g)
exec(compile(open("/tmp/w3_solution_fns.py").read(), "sol", "exec"), g)
g["SHOW_CALL_TOKENS"] = False
N = int(sys.argv[1]) if len(sys.argv) > 1 else 8
EMAILS = ["001", "004", "005", "006", "017", "025"]
NEEDED = math.ceil(0.75 * N)


def canon(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = re.sub(r"[^a-z0-9@._-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def concepts(text, f):
    """Which of the thirteen fact fields this one indicator string mentions."""
    t = canon(text)
    toks = set(t.split())
    out = set()
    def val(k):
        return canon(f.get(k)) if f.get(k) not in (None, "", []) else None
    if (val("from_display") and val("from_display") in t) or ("sender" in t and "name" in t):
        out.add("from_display")
    if (val("from_address") and val("from_address") in t) or (("sender" in t or "from" in t) and "address" in t):
        out.add("from_address")
    if (val("from_domain") and val("from_domain") in toks) or (("sender" in t or "from" in t) and "domain" in t):
        out.add("from_domain")
    if (val("reply_to") and val("reply_to") in t) or "reply to" in t or "reply address" in t:
        out.add("reply_to")
    if (val("subject") and val("subject") in t) or "subject" in toks:
        out.add("subject")
    for a in ("spf", "dkim", "dmarc"):
        if a in toks:
            out.add(a)
    if "display" in t and ("match" in t or "mismatch" in t):
        out.add("display_name_mismatch")
    hosts = [canon(h) for h in (f.get("url_hosts") or [])]
    if any(h in toks for h in hosts) or "link host" in t or "url host" in t:
        out.add("url_hosts")
    if "external" in t or "outside company" in t or "outside organization" in t:
        out.add("external")
    if "scan" in t or "scanner" in t or "gateway scan" in t:
        out.add("scan_result")
    names = [canon(n) for n in (f.get("attachments") or [])]
    if any(n and n in t for n in names) or "attachment" in t or "attached file" in t:
        out.add("attachments")
    return out


def stable(replies, f):
    counter = collections.Counter()
    for r in replies:
        seen = set()
        for s in (r or []):
            seen |= concepts(s, f)
        counter.update(seen)
    return {c for c, n in counter.items() if n >= NEEDED}


print(f"model={os.environ['ITSY1377_MODEL']}  N={N} replies per condition, "
      f"stable at >= {NEEDED}\n")
print(f"{'id':<5}{'|P|':<5}{'|G|':<5}{'G-P (new fact concepts)':<40}{'D':<7}qualifies")
print("-" * 78)
rows, qualifying = [], 0
for eid in EMAILS:
    parsed = g["load_email"](eid, known_names=g["KNOWN_NAMES"])
    f = g["build_facts"](parsed)
    P_r = [(g["classify_email"](parsed) or {}).get("indicators") for _ in range(N)]
    G_r = [(g["classify_grounded"](parsed) or {}).get("indicators") for _ in range(N)]
    P, G = stable(P_r, f), stable(G_r, f)
    union = P | G
    D = len(P ^ G) / len(union) if union else 0.0
    new = G - P
    ok = bool(new) and D >= 0.50
    qualifying += ok
    rows.append({"email": eid, "P": sorted(P), "G": sorted(G),
                 "new": sorted(new), "D": round(D, 3), "qualifies": ok})
    print(f"{eid:<5}{len(P):<5}{len(G):<5}{', '.join(sorted(new))[:38]:<40}{D:<7.2f}{ok}")

print(f"\n  qualifying rows: {qualifying} of 6")
verdict = ("PASS - keep indicator-based 3.2" if qualifying >= 4 else
           "BORDERLINE - replicate at N=8 before deciding" if qualifying == 3 else
           "FAIL - do not build the objective on indicator change")
print(f"  pre-registered verdict: {verdict}")
json.dump({"n": N, "needed": NEEDED, "rows": rows, "qualifying": qualifying,
           "verdict": verdict}, open("/tmp/w3_prereg.json", "w"), indent=1)
print(f"  tokens: {g['USAGE']['total']} over {g['USAGE']['calls']} calls")
