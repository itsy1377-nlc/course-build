#!/usr/bin/env python3
"""Screen discrete label probes for the week 1 temperature demonstration.

Free prose saturates: twenty distinct answers out of twenty at every
temperature the course would use, so the student sees no difference. A probe
that forces one label out of a small set turns "how different are these" into a
count anyone can read. This measures whether that count actually separates.
"""
import collections, json, re, statistics, sys, time
import urllib.error, urllib.request

KEY = open("/root/.w1-eval-key").read().strip()
URL = "http://127.0.0.1:4000/v1/chat/completions"
BODY = open("/tmp/w1_body.txt").read()

PROBES = {
    "first_check": ("This email has more than one warning sign. Which one "
                    "should an analyst check first? Answer with exactly one "
                    "label: LINK, IDENTITY, URGENCY, or REQUEST.",
                    ["LINK", "IDENTITY", "URGENCY", "REQUEST"]),
    "tag": ("Choose one tag that best describes this email. Answer with "
            "exactly one label: PAYROLL, SIGN_IN, URGENT, or EXTERNAL_LINK.",
            ["PAYROLL", "SIGN_IN", "URGENT", "EXTERNAL_LINK"]),
    "binary": ("Read the email below. Answer only PHISHING or NOT_PHISHING.",
               ["PHISHING", "NOT_PHISHING"]),
}
TEMPS = [0.0, 0.2, 1.0, 1.3, 1.5]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "granite-3b"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 40


def call(prompt, temperature):
    payload = {"model": MODEL,
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 12, "temperature": temperature,
               "reasoning_effort": "none"}
    data = json.dumps(payload).encode()
    for attempt in range(6):
        req = urllib.request.Request(
            URL, data=data, headers={"Authorization": "Bearer " + KEY,
                                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            ch = d["choices"][0]
            return ch["message"]["content"].strip(), ch.get("finish_reason")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt); continue
            return None, "http_%d" % e.code
        except Exception:
            time.sleep(2 ** attempt)
    return None, "gave_up"


def normalise(text, labels):
    up = re.sub(r"[^A-Z_ ]", " ", (text or "").upper())
    words = up.split()
    for lab in sorted(labels, key=len, reverse=True):
        if lab in words or lab in up.replace(" ", "_"):
            return lab
    return "OTHER"


out = {"model": MODEL, "n": N, "cells": []}
print(f"model={MODEL} n={N} probes={list(PROBES)} temps={TEMPS}", flush=True)
for name, (instruction, labels) in PROBES.items():
    prompt = instruction + "\n\n" + BODY
    for temp in TEMPS:
        got, lengths, errs = [], 0, 0
        for _ in range(N):
            text, finish = call(prompt, temp)
            if text is None:
                errs += 1
            else:
                got.append(normalise(text, labels))
                lengths += (finish == "length")
            time.sleep(0.12)
        if not got:
            print(f"  {name:<12} t={temp}  ALL FAILED", flush=True); continue
        counts = collections.Counter(got)
        valid = [g for g in got if g != "OTHER"]
        top, topn = counts.most_common(1)[0]
        row = {"probe": name, "temp": temp, "kept": len(got), "errors": errs,
               "length_finishes": lengths,
               "valid_rate": round(len(valid) / len(got), 3),
               "distinct_valid": len(set(valid)),
               "top_label": top, "top_share": round(topn / len(got), 3),
               "counts": dict(counts), "answers": got}
        out["cells"].append(row)
        print(f"  {name:<12} t={temp:<4} kept={len(got):2d} err={errs} "
              f"valid={row['valid_rate']:.0%} distinct={row['distinct_valid']} "
              f"top={top} {row['top_share']:.0%}  {dict(counts)}", flush=True)
json.dump(out, open("/tmp/w1_labels_%s.json" % MODEL, "w"), indent=1)
print("written /tmp/w1_labels_%s.json" % MODEL, flush=True)
