#!/usr/bin/env python3
"""Measure how much granite-3b's answer moves with temperature, three ways.

Week 1 asks a student to see that a low temperature gives steadier answers. The
lab shows six free-prose answers and asks them to eyeball it. This measures
whether that is visible at all, and whether a shorter answer shape shows it
better. Nothing here writes to the course.
"""
import difflib
import json
import re
import statistics
import sys
import time
import urllib.error
import urllib.request

KEY = open("/root/.w1-eval-key").read().strip()
URL = "http://127.0.0.1:4000/v1/chat/completions"
BODY = open("/tmp/w1_body.txt").read()

ARMS = {
    "prose": "Read the email below. In two sentences, say whether it looks "
             "like a phishing attempt, and why.",
    "one_word": "Read the email below. Answer with one word, phishing or "
                "legitimate, and nothing else.",
    "word_plus": "Read the email below. Answer with one word, phishing or "
                 "legitimate, then one short sentence saying why.",
}
TEMPS = [0.0, 0.2, 0.7, 1.0, 1.3]
N = 20
MODEL = sys.argv[1] if len(sys.argv) > 1 else "granite-3b"


def call(prompt, temperature):
    payload = {"model": MODEL,
               "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 512, "temperature": temperature,
               "reasoning_effort": "none"}
    data = json.dumps(payload).encode()
    for attempt in range(6):
        req = urllib.request.Request(
            URL, data=data,
            headers={"Authorization": "Bearer " + KEY,
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            return d["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            time.sleep(2 ** attempt)
    return None


def verdict(text):
    low = (text or "").lower()
    bad = any(w in low for w in ("phishing", "suspicious", "malicious", "scam"))
    good = any(w in low for w in ("legitimate", "benign", "not phishing", "safe"))
    if "not phishing" in low or "not a phishing" in low:
        return "legitimate"
    if bad and not good:
        return "phishing"
    if good and not bad:
        return "legitimate"
    return "mixed" if bad and good else "unclear"


def first_sentence(text):
    return re.split(r"(?<=[.!?])\s", (text or "").strip())[0]


def pairwise_similarity(answers):
    ratios = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            ratios.append(difflib.SequenceMatcher(None, answers[i], answers[j]).ratio())
    return statistics.mean(ratios) if ratios else 0.0


out = {"model": MODEL, "n": N, "runs": []}
print(f"model={MODEL} n={N} arms={list(ARMS)} temps={TEMPS}", flush=True)
for arm, instruction in ARMS.items():
    prompt = instruction + "\n\n" + BODY
    for temp in TEMPS:
        answers, failed = [], 0
        for _ in range(N):
            a = call(prompt, temp)
            if a is None:
                failed += 1
            else:
                answers.append(a)
            time.sleep(0.15)
        if not answers:
            print(f"  {arm:<10} t={temp}  ALL {N} CALLS FAILED", flush=True)
            continue
        words = [len(a.split()) for a in answers]
        verdicts = [verdict(a) for a in answers]
        top = max(set(verdicts), key=verdicts.count)
        row = {
            "arm": arm, "temp": temp, "kept": len(answers), "failed": failed,
            "distinct_exact": len(set(answers)),
            "distinct_first_sentence": len(set(first_sentence(a) for a in answers)),
            "mean_similarity": round(pairwise_similarity(answers), 3),
            "words_min": min(words), "words_max": max(words),
            "words_mean": round(statistics.mean(words), 1),
            "words_stdev": round(statistics.stdev(words), 1) if len(words) > 1 else 0.0,
            "verdict_top": top,
            "verdict_agreement": round(verdicts.count(top) / len(verdicts), 2),
            "answers": answers,
        }
        out["runs"].append(row)
        print(f"  {arm:<10} t={temp:<4} kept={row['kept']:2d} fail={failed} "
              f"exact={row['distinct_exact']:2d}/{row['kept']:2d} "
              f"sim={row['mean_similarity']:.3f} "
              f"words={row['words_min']}-{row['words_max']} "
              f"(sd {row['words_stdev']}) "
              f"verdict={top} {row['verdict_agreement']:.0%}", flush=True)
json.dump(out, open("/tmp/w1_study_%s.json" % MODEL.replace("/", "_"), "w"), indent=1)
print("written /tmp/w1_study_%s.json" % MODEL.replace("/", "_"), flush=True)
