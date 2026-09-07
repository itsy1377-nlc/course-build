import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, ".")
from probe import post, log, decoding_for
model = sys.argv[1]; out = sys.argv[2]
base = {"model": model, "messages": [{"role": "user", "content": "Why is the sky blue? Answer in two sentences."}],
        "max_tokens": 1024, **decoding_for(model)}
variants = [
    ("e1b_reasoning_obj_effort_none", {"reasoning": {"effort": "none"}}),
    ("e1b_reasoning_obj_effort_low", {"reasoning": {"effort": "low"}}),
    ("e1b_reasoning_obj_enabled_false", {"reasoning": {"enabled": False}}),
    ("e1b_reasoning_effort_none", {"reasoning_effort": "none"}),
    ("e1b_options_think_false", {"options": {"think": False}}),
    ("e1b_think_string_false", {"think": "false"}),
]
for label, extra in variants:
    body = {**base, **extra}
    status, resp, dt = post("/chat/completions", body)
    log(out, {"model": model, "label": label, "request": body, "status": status, "response": resp,
              "latency_s": dt, "error": status != 200})
# native endpoint, for a footnote only
body = {"model": model, "messages": base["messages"], "think": False, "stream": False,
        "options": {"temperature": base.get("temperature", 0), "top_p": base.get("top_p", 1.0), "num_predict": 1024}}
data = json.dumps(body).encode()
req = urllib.request.Request("http://localhost:11434/api/chat", data=data, headers={"Content-Type": "application/json"})
t0 = time.perf_counter()
try:
    with urllib.request.urlopen(req, timeout=600) as r:
        status = r.status; raw = r.read().decode()
except urllib.error.HTTPError as e:
    status = e.code; raw = e.read().decode()
dt = time.perf_counter() - t0
resp = json.loads(raw)
with open(out, "a") as f:
    f.write(json.dumps({"model": model, "label": "native_api_chat_think_false", "request": body, "status": status,
                        "response": resp, "latency_s": dt, "error": status != 200}) + "\n")
print(f"[native_api_chat_think_false] status={status} t={dt:.2f}s keys={sorted(resp.get('message', {}).keys())} "
      f"eval_count={resp.get('eval_count')} content[:200]={resp.get('message', {}).get('content', '')[:200]!r} "
      f"thinking[:100]={resp.get('message', {}).get('thinking', '')[:100]!r}")
