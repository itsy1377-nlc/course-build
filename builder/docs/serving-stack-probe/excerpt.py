import json, sys, copy
def trim_val(v, n):
    if isinstance(v, str) and len(v) > n:
        return v[:n] + " ...[trimmed " + str(len(v) - n) + " chars]"
    return v
def trim_obj(o, n=200, keep_full=()):
    if isinstance(o, dict):
        return {k: (v if k in keep_full else trim_obj(v, n, keep_full)) for k, v in o.items()}
    if isinstance(o, list):
        return [trim_obj(x, n, keep_full) for x in o]
    return trim_val(o, n)
path = sys.argv[1]; labels = sys.argv[2].split(","); n = int(sys.argv[3]) if len(sys.argv) > 3 else 200
for line in open(path):
    r = json.loads(line)
    if r["label"] in labels:
        req = copy.deepcopy(r["request"]); resp = copy.deepcopy(r["response"])
        print(f"### {r['label']}  (HTTP {r['status']}, {r['latency_s']:.2f} s)")
        print("REQUEST:"); print(json.dumps(trim_obj(req, 400), indent=2, ensure_ascii=False))
        print("RESPONSE:"); print(json.dumps(trim_obj(resp, n), indent=2, ensure_ascii=False)); print()
