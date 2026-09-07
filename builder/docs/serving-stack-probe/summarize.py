import json, sys
def trim(s, n=220):
    if s is None: return None
    s = str(s)
    return s if len(s) <= n else s[:n] + " ...[trimmed]"
for path in sys.argv[1:]:
    print("#####", path)
    for line in open(path):
        r = json.loads(line)
        resp = r["response"]
        row = {"label": r["label"], "status": r["status"], "latency_s": round(r["latency_s"], 2)}
        if isinstance(resp, dict) and resp.get("choices"):
            ch = resp["choices"][0]; msg = ch.get("message", {})
            row["finish_reason"] = ch.get("finish_reason")
            row["msg_keys"] = sorted(msg.keys())
            row["usage"] = resp.get("usage")
            row["content"] = trim(msg.get("content"), 160)
            if msg.get("reasoning") is not None: row["reasoning"] = trim(msg.get("reasoning"), 100)
            if msg.get("tool_calls"): row["tool_calls"] = msg["tool_calls"]
        elif isinstance(resp, dict) and resp.get("message"):
            row["native_msg_keys"] = sorted(resp["message"].keys()); row["eval_count"] = resp.get("eval_count"); row["prompt_eval_count"] = resp.get("prompt_eval_count")
        else:
            row["error_body"] = trim(json.dumps(resp), 200)
        for k in ("shape", "valid_json_after_strip", "exact_keys", "well_formed_tool_call", "arguments_type"):
            if k in r: row[k] = r[k]
        print(json.dumps(row, ensure_ascii=False))
