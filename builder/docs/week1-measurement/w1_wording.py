#!/usr/bin/env python3
"""Does the number probe give a number that is not nonsense?

The first wording scored email 001 -- a credential phish -- at 0.00 on twenty
runs out of twenty. The temperature statistic was perfect and the answer was
wrong, which is worse than no demonstration. This tries four wordings and
prints the values, not just the spread.
"""
import collections, json, re, statistics, time
import urllib.error, urllib.request

KEY = open("/root/.w1-eval-key").read().strip()
URL = "http://127.0.0.1:4000/v1/chat/completions"
BODY = open("/tmp/w1_body.txt").read()
N = 20

WORDINGS = {
 "A_original": "Read the email below. Answer with one number from 0.00 to 1.00 "
               "giving the chance that it is a phishing attempt. Answer with "
               "the number and nothing else.",
 "B_anchored": "Read the email below. How likely is it that this email is a "
               "phishing attempt? Answer with one number, where 0.00 means "
               "certainly safe and 1.00 means certainly a phishing attempt. "
               "Answer with the number and nothing else.",
 "C_higher":   "Read the email below. Answer with one number between 0 and 1 "
               "for how likely it is that this email is a phishing attempt. "
               "A higher number means more likely to be phishing. Answer with "
               "the number and nothing else.",
 "D_verdict":  "Read the email below. Answer with one word, phishing or "
               "legitimate, then a space, then a number from 0.00 to 1.00 for "
               "how confident you are in that word. Nothing else.",
}


def call(prompt, temperature):
    payload = {"model": "granite-3b",
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 512, "temperature": temperature,
               "reasoning_effort": "none"}
    data = json.dumps(payload).encode()
    for attempt in range(6):
        req = urllib.request.Request(URL, data=data,
              headers={"Authorization": "Bearer " + KEY,
                       "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read())["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt); continue
            return None
        except Exception:
            time.sleep(2 ** attempt)
    return None


out = {"n": N, "cells": []}
for name, instruction in WORDINGS.items():
    prompt = instruction + "\n\n" + BODY
    for temp in (0.2, 1.0):
        got = [a for a in (call(prompt, temp) for _ in range(N)) if a]
        nums = []
        for a in got:
            m = re.search(r"(?<![\d.])(?:1(?:\.0+)?|0?\.\d+|0(?:\.0+)?)(?![\d])", a)
            if m:
                try: nums.append(float(m.group(0)))
                except ValueError: pass
        counts = collections.Counter(got)
        row = {"wording": name, "temp": temp, "kept": len(got),
               "distinct": len(set(got)),
               "values": sorted(set(nums)),
               "mean": round(statistics.mean(nums), 3) if nums else None,
               "answers": got}
        out["cells"].append(row)
        print(f"  {name:<11} t={temp:<4} kept={len(got):2d} distinct={row['distinct']:2d} "
              f"mean={row['mean']} values={row['values'][:9]}", flush=True)
        print(f"              most common: {counts.most_common(3)}", flush=True)
json.dump(out, open("/tmp/w1_wording.json", "w"), indent=1)
print("written /tmp/w1_wording.json", flush=True)
