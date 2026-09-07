#!/usr/bin/env python3
"""Probe the local Ollama OpenAI-compatible endpoint with plain HTTP (urllib only).
Usage: probe.py --model NAME --exp e1|e2|e3|extra [--think-variants] [--out FILE]
Every call is sequential. Every request/response pair is appended to the JSONL log.
"""
import argparse, json, re, sys, time, urllib.request, urllib.error

BASE = "http://localhost:11434/v1"
MAXTOK = 1024

def post(path, body, timeout=600):
    data = json.dumps(body).encode()
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status = r.status
            raw = r.read().decode()
    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read().decode()
    dt = time.perf_counter() - t0
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"_unparsed": raw}
    return status, parsed, dt

THINK_RE = re.compile(r"<think>.*?</think>\s*", re.S)
FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.S)

def strip_think(text):
    if text is None:
        return ""
    t = THINK_RE.sub("", text)
    # unclosed or orphan variants
    if "</think>" in t:
        t = t.split("</think>")[-1]
    if "<think>" in t:
        t = t.split("<think>")[0]
    return t.strip()

def strip_fences(text):
    m = FENCE_RE.match(text)
    if m:
        return m.group(1).strip()
    # fence somewhere inside
    m2 = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.S)
    if m2:
        return m2.group(1).strip()
    return text.strip()

def classify_content(content):
    """Return a coarse label for what the content looks like."""
    if content is None or content == "":
        return "empty"
    has_think = "<think>" in content or "</think>" in content
    body = strip_think(content)
    fenced = "```" in body
    inner = strip_fences(body)
    try:
        json.loads(inner)
        is_json = True
    except Exception:
        is_json = False
    if is_json and not fenced and not has_think:
        return "json_only"
    if is_json and has_think and not fenced:
        return "think_then_json"
    if is_json and fenced and not has_think:
        return "fenced_json"
    if is_json and fenced and has_think:
        return "think_then_fenced_json"
    return "prose" if not has_think else "think_then_prose"

SUFFIX = ""
def log(out, rec):
    rec["label"] = rec["label"] + SUFFIX
    with open(out, "a") as f:
        f.write(json.dumps(rec) + "\n")
    # brief console line
    resp = rec.get("response", {})
    ch = (resp.get("choices") or [{}])[0] if isinstance(resp, dict) else {}
    msg = ch.get("message", {}) if isinstance(ch, dict) else {}
    print(f"[{rec['label']}] status={rec['status']} t={rec['latency_s']:.2f}s finish={ch.get('finish_reason')} "
          f"keys={sorted(msg.keys()) if isinstance(msg, dict) else '?'} usage={resp.get('usage') if isinstance(resp, dict) else '?'}")
    c = msg.get("content") if isinstance(msg, dict) else None
    if c:
        print("   content[:300]=" + repr(c[:300]))
    for k in ("reasoning", "reasoning_content", "thinking"):
        if isinstance(msg, dict) and msg.get(k):
            print(f"   {k}[:200]=" + repr(msg[k][:200]))
    if isinstance(msg, dict) and msg.get("tool_calls"):
        print("   tool_calls=" + json.dumps(msg["tool_calls"])[:400])
    if rec.get("error"):
        print("   ERROR=" + json.dumps(resp)[:400])
    sys.stdout.flush()

def decoding_for(model):
    if model.startswith("granite4.2"):
        return {"temperature": 1.0, "top_p": 0.95}
    return {"temperature": 0}

def run_e1(model, out, think_variants):
    base = {"model": model, "messages": [{"role": "user", "content": "Why is the sky blue? Answer in two sentences."}],
            "max_tokens": MAXTOK, **decoding_for(model)}
    variants = [("e1_default", {})]
    if think_variants:
        variants += [
            ("e1_think_false", {"think": False}),
            ("e1_reasoning_false", {"reasoning": False}),
            ("e1_chat_template_kwargs", {"chat_template_kwargs": {"enable_thinking": False}}),
            ("e1_think_true", {"think": True}),
            ("e1_reasoning_effort_low", {"reasoning_effort": "low"}),
        ]
    for label, extra in variants:
        body = {**base, **extra}
        status, resp, dt = post("/chat/completions", body)
        log(out, {"model": model, "label": label, "request": body, "status": status, "response": resp,
                  "latency_s": dt, "error": status != 200})

NOTICE = ("Attention shoppers: the bakery counter will close thirty minutes early tonight for a routine oven inspection. "
          "Day-old bread on the clearance rack is half price until closing.")

def run_e2(model, out, variants_extra):
    prompt = ("Read the store notice below and classify it. Respond with strict JSON only, no prose, "
              "no code fences, with exactly these keys: verdict (one of \"informational\", \"promotional\", \"urgent\"), "
              "category (a short noun phrase), confidence (a number from 0 to 1), indicators (a list of short strings "
              "quoting the words that drove your decision).\n\nNotice:\n" + NOTICE)
    base = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": MAXTOK, **decoding_for(model)}
    variants = [("e2_default", {})] + variants_extra
    for label, extra in variants:
        for i in range(3):
            body = {**base, **extra}
            status, resp, dt = post("/chat/completions", body)
            content = None
            try:
                content = resp["choices"][0]["message"]["content"]
            except Exception:
                pass
            shape = classify_content(content) if status == 200 else "error"
            valid = False
            keys_ok = False
            if status == 200 and content is not None:
                inner = strip_fences(strip_think(content))
                try:
                    obj = json.loads(inner)
                    valid = isinstance(obj, dict)
                    keys_ok = valid and set(obj.keys()) == {"verdict", "category", "confidence", "indicators"}
                except Exception:
                    valid = False
            rec = {"model": model, "label": f"{label}_{i+1}", "request": body, "status": status, "response": resp,
                   "latency_s": dt, "error": status != 200, "shape": shape, "valid_json_after_strip": valid,
                   "exact_keys": keys_ok}
            log(out, rec)
            print(f"   shape={shape} valid={valid} exact_keys={keys_ok}")

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "Name of the city"}},
            "required": ["city"],
        },
    },
}]

def run_e3(model, out, variants_extra):
    q = "What is the weather right now in Pellmoor Harbor?"
    base = {"model": model, "messages": [{"role": "user", "content": q}], "tools": TOOLS, "max_tokens": MAXTOK,
            **decoding_for(model)}
    variants = [("e3_default", {})] + variants_extra
    for label, extra in variants:
        for i in range(3):
            body = {**base, **extra}
            status, resp, dt = post("/chat/completions", body)
            well_formed = False
            tc = None
            msg = {}
            try:
                msg = resp["choices"][0]["message"]
                tcs = msg.get("tool_calls") or []
                if len(tcs) >= 1:
                    tc = tcs[0]
                    fn = tc.get("function", {})
                    args = fn.get("arguments")
                    if isinstance(args, str):
                        args_obj = json.loads(args)
                    else:
                        args_obj = args
                    well_formed = (fn.get("name") == "get_weather" and isinstance(args_obj, dict)
                                   and isinstance(args_obj.get("city"), str) and len(args_obj["city"]) > 0)
            except Exception as e:
                well_formed = False
            rec = {"model": model, "label": f"{label}_{i+1}_turn1", "request": body, "status": status, "response": resp,
                   "latency_s": dt, "error": status != 200, "well_formed_tool_call": well_formed,
                   "arguments_type": (type(tc["function"]["arguments"]).__name__ if tc and "function" in tc else None)}
            log(out, rec)
            print(f"   well_formed={well_formed} args_type={rec['arguments_type']}")
            if not well_formed:
                continue
            # second turn: echo assistant message back, then tool result
            assistant_msg = {"role": "assistant", "content": msg.get("content") or "", "tool_calls": msg["tool_calls"]}
            tool_msg = {"role": "tool", "tool_call_id": tc.get("id", ""), "name": "get_weather",
                        "content": json.dumps({"city": "Pellmoor Harbor", "temperature_c": 17, "condition": "light fog", "wind_kph": 9})}
            body2 = {**base, "messages": [{"role": "user", "content": q}, assistant_msg, tool_msg]}
            body2 = {**body2, **extra}
            status2, resp2, dt2 = post("/chat/completions", body2)
            log(out, {"model": model, "label": f"{label}_{i+1}_turn2", "request": body2, "status": status2,
                      "response": resp2, "latency_s": dt2, "error": status2 != 200})

def run_extra(model, out):
    """Optional: response_format json_object on the same notice, 3x."""
    prompt = ("Read the store notice below and classify it. Respond with strict JSON only, with exactly these keys: "
              "verdict (one of \"informational\", \"promotional\", \"urgent\"), category (a short noun phrase), "
              "confidence (a number from 0 to 1), indicators (a list of short strings).\n\nNotice:\n" + NOTICE)
    base = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": MAXTOK,
            "response_format": {"type": "json_object"}, **decoding_for(model)}
    for i in range(3):
        status, resp, dt = post("/chat/completions", base)
        content = None
        try:
            content = resp["choices"][0]["message"]["content"]
        except Exception:
            pass
        shape = classify_content(content) if status == 200 else "error"
        valid = False
        if status == 200 and content is not None:
            try:
                obj = json.loads(strip_fences(strip_think(content)))
                valid = isinstance(obj, dict)
            except Exception:
                pass
        log(out, {"model": model, "label": f"extra_json_object_{i+1}", "request": base, "status": status,
                  "response": resp, "latency_s": dt, "error": status != 200, "shape": shape,
                  "valid_json_after_strip": valid})
        print(f"   shape={shape} valid={valid}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--exp", required=True)
    ap.add_argument("--think-variants", action="store_true")
    ap.add_argument("--e2-variants", default="")  # comma list: think_false,ctk
    ap.add_argument("--e3-variants", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-tokens", type=int, default=1024)
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    MAXTOK = a.max_tokens
    SUFFIX = a.suffix
    vmap = {"think_false": ("_think_false", {"think": False}),
            "ctk": ("_ctk_nothink", {"chat_template_kwargs": {"enable_thinking": False}}),
            "reasoning_false": ("_reasoning_false", {"reasoning": False}),
            "none": ("_effort_none", {"reasoning_effort": "none"})}
    if a.exp == "e1":
        run_e1(a.model, a.out, a.think_variants)
    elif a.exp == "e2":
        vs = [("e2" + vmap[v][0], vmap[v][1]) for v in a.e2_variants.split(",") if v]
        run_e2(a.model, a.out, vs)
    elif a.exp == "e3":
        vs = [("e3" + vmap[v][0], vmap[v][1]) for v in a.e3_variants.split(",") if v]
        run_e3(a.model, a.out, vs)
    elif a.exp == "extra":
        run_extra(a.model, a.out)
