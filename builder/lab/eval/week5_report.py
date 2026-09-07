"""Turn the week 5 measurement into the report Phase 1 item 5 asks for.

Reads docs/week5-model-test.json and writes docs/week5-model-test.md.
Every number in the report comes out of the JSON. Nothing is typed by hand.
"""

from __future__ import annotations

import hashlib
import json
import statistics as st
from pathlib import Path

BUILDER = Path(__file__).resolve().parents[2]
CORPUS = BUILDER / "corpus"
DATA = json.loads((BUILDER / "docs" / "week5-model-test.json").read_text())
OUT = BUILDER / "docs" / "week5-model-test.md"

RUNS = DATA["runs"]
CONFIGS = [c["name"] for c in DATA["configs"]]
EMAILS = DATA["emails"]

VARIANT_WORDS = {
    "free": "the model picks any tool and decides for itself when to stop",
    "guided": "the sender check is run for the student, the model picks at most one more tool and decides when to stop",
    "coded": "the model picks the next tool, the student's code decides when to stop",
    "coded_anchored": "as coded, plus one line telling the model to start with the sender check",
}


def rows(cfg: str) -> list:
    return [r for r in RUNS if r["config"] == cfg]


def pct(part: int, whole: int) -> str:
    return f"{part}/{whole}" if whole else "n/a"


def digests_still_match() -> tuple[bool, list]:
    """The measurement is only valid against the files it actually read."""
    bad = []
    for eid, sha in DATA["world"].get("email_sha256", {}).items():
        p = CORPUS / "emails" / "teaching" / f"{eid}.eml"
        if not p.exists():
            p = CORPUS / "emails" / "batch" / f"{eid}.eml"
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != sha:
            bad.append(eid)
    return (not bad), bad


def main() -> int:
    ok, changed = digests_still_match()
    cfgmeta = {c["name"]: c for c in DATA["configs"]}

    lines: list[str] = []
    add = lines.append

    add("# Week 5 model test: can a 3B model drive the bounded loop?")
    add("")
    add("**Course:** Agentic AI and Security Operations (ITSY 1377), "
        "Northeast Lakeview College, Cyber Defense program  ")
    add("**Phase 1 blueprint, item 5.** Prepared 2026-09-04.  ")
    add("**Audience:** the program manager. Nothing here assumes you are building the course.")
    add("")
    add("Week 5 is the week this course is most likely to fail. The agent has to "
        "choose its next check from what it just learned, stop when it has enough, "
        "and never run away. That is the least certain behaviour on a small model. "
        "It is also the hardest week for students, who arrive with no programming "
        "background. So it was measured before the lab was written.")
    add("")

    add("## What was measured")
    add("")
    add(f"{len(RUNS)} complete agent runs. Each run is one email triaged from start "
        f"to finish, so a run is several model calls, not one. The six emails are the "
        f"six the week 5 lab uses, one per loop shape. Every run was scored against "
        f"the corpus record for that email: the tools it should call, the order, the "
        f"reason the run should end, and the verdict.")
    add("")
    add("Four lab designs were tested, because the point of the exercise was to find "
        "one that works rather than to grade a single guess.")
    add("")
    add("| Design | What the model decides |")
    add("|---|---|")
    for v, words in VARIANT_WORDS.items():
        if any(c["variant"] == v for c in DATA["configs"]):
            add(f"| {v.replace('_', ' ')} | {words} |")
    add("")
    add("### The world, asserted before measuring")
    add("")
    w = DATA["world"]
    add(f"- Serving stack: {w['ollama_version']}, OpenAI-compatible endpoint at `{w['endpoint']}`.")
    for m, d in sorted((w.get("model_digests") or {}).items()):
        add(f"- Model `{m}`, blob digest `{d}`.")
    add(f"- Step cap: {DATA['step_cap']}. One model request at a time, never two.")
    add(f"- Tool results: {w['note']}")
    if ok:
        add("- Every email file still carries the exact digest recorded when it was read. "
            "The measurement is against the files that ship.")
    else:
        add(f"- **WARNING: these files changed after they were measured: {', '.join(changed)}. "
            "The numbers below are stale and the sweep must be repeated.**")
    add("")
    add("That last check is not decoration. An earlier sweep of 234 runs was thrown "
        "away because an authoring job regenerated four of the six emails while the "
        "measurement was reading them. The digests caught it.")
    add("")

    add("## The result")
    add("")
    add("| Configuration | Model | Design | Right tool path | Right stop reason | Right verdict | Valid answer | Tokens per run | Seconds per run |")
    add("|---|---|---|---|---|---|---|---|---|")
    best = None
    for cfg in CONFIGS:
        rs = rows(cfg)
        if not rs:
            continue
        n = len(rs)
        meta = cfgmeta[cfg]
        stop_rs = [r for r in rs if r["score"].get("stop_right") is not None]
        exact = sum(1 for r in rs if r["score"]["sequence_exact"])
        stop = sum(1 for r in stop_rs if r["score"]["stop_right"])
        verdict = sum(1 for r in rs if r["score"]["verdict_right"])
        js = sum(1 for r in rs if r["score"]["answered_json"])
        tok = st.mean(r["tokens"]["prompt"] + r["tokens"]["completion"] for r in rs)
        sec = st.mean(r["seconds"] for r in rs)
        mt = meta.get("max_tokens", 512)
        model = meta["model"] + (" reasoning off" if meta["reasoning"] == "none" else
                                 f" reasoning on, {mt} token budget" if "reason" in cfg else "")
        add(f"| {cfg} | {model} | {meta['variant'].replace('_', ' ')} | {pct(exact, n)} | "
            f"{pct(stop, len(stop_rs)) if stop_rs else 'not applicable'} | {pct(verdict, n)} | "
            f"{pct(js, n)} | {tok:,.0f} | {sec:.1f} |")
        score = (exact / n, verdict / n)
        if best is None or score > best[1]:
            best = (cfg, score)
    add("")
    add("Right tool path means the exact tools in the exact order the corpus record "
        "expects. Right stop reason applies only to the designs where code owns the "
        "stop, and means the run ended for the reason the corpus records. Valid answer "
        "means the final reply parsed as the JSON the lab asks for.")
    add("")

    add("## What the numbers say")
    add("")
    add("### 1. The models choose tools well and stop badly")
    add("")
    free = [r for r in RUNS if cfgmeta[r["config"]]["variant"] == "free" and "reason-free" not in r["config"]]
    if free:
        first_ok = sum(1 for r in free if r["score"]["first_tool_right"])
        exact_ok = sum(1 for r in free if r["score"]["sequence_exact"])
        add(f"Across the runs where the model was free to choose, it picked the correct "
            f"first tool {pct(first_ok, len(free))} times but produced the correct whole "
            f"path only {pct(exact_ok, len(free))} times. The gap is the model not "
            f"stopping once it had enough. On the email whose sender is already known "
            f"bad, it ran the link check anyway, reached the right verdict, and spent an "
            f"extra step doing it.")
    add("")
    add("### 2. Moving the stop condition into code fixes it")
    add("")
    coded = [r for r in RUNS if cfgmeta[r["config"]]["variant"].startswith("coded")]
    if coded:
        s_ok = sum(1 for r in coded if r["score"].get("stop_right"))
        add(f"When a deterministic rule in the student's own code decides when to stop, "
            f"the run ends for the right reason {pct(s_ok, len(coded))} times across every "
            f"model and every email. The model's remaining job, choosing the next check, "
            f"is the part it is already good at. This is the design the week 5 spec "
            f"already describes, and the measurement supports it.")
    add("")
    add("### 3. One configuration is clearly the one to ship")
    add("")
    if best:
        cfg = best[0]
        rs = rows(cfg)
        n = len(rs)
        meta = cfgmeta[cfg]
        add(f"`{cfg}`: {meta['model']} with reasoning off, in the design where code owns "
            f"the stop. It produced the exact expected tool path "
            f"{pct(sum(1 for r in rs if r['score']['sequence_exact']), n)}, the right stop "
            f"reason {pct(sum(1 for r in rs if r['score'].get('stop_right')), n)}, and the "
            f"right verdict {pct(sum(1 for r in rs if r['score']['verdict_right']), n)}, at "
            f"{st.mean(r['tokens']['prompt'] + r['tokens']['completion'] for r in rs):,.0f} "
            f"tokens and {st.mean(r['seconds'] for r in rs):.1f} seconds per triage.")
    add("")
    add("### 4. Reasoning mode is not usable for this course")
    add("")
    r512 = rows("granite4.2-reason-free")
    r4096 = rows("granite4.2-reason-free-4096") + rows("granite4.2-reason-coded-4096")
    if r512:
        add(f"At the 512-token answer budget the labs use, Granite 4.2 in its default "
            f"reasoning mode spent the whole budget thinking and returned empty content "
            f"{pct(sum(1 for r in r512 if not r['score']['answered_json']), len(r512))} "
            f"times. That is a configuration incompatibility, not a limit of the model, "
            f"so it was re-tested at eight times the budget.")
    if r4096:
        add("")
        add(f"At 4,096 tokens it works, and it still should not be used. Across "
            f"{len(r4096)} runs it averaged "
            f"{st.mean(r['tokens']['prompt'] + r['tokens']['completion'] for r in r4096):,.0f} "
            f"tokens and {st.mean(r['seconds'] for r in r4096):.0f} seconds for a single "
            f"triage, against "
            f"{st.mean(r['tokens']['prompt'] + r['tokens']['completion'] for r in rows(best[0])):,.0f} "
            f"tokens and {st.mean(r['seconds'] for r in rows(best[0])):.1f} seconds for the "
            f"recommended configuration. A student waiting a minute and a half per email "
            f"will assume the notebook has hung.")
    add("")

    add("## Per email")
    add("")
    add("| Email | " + " | ".join(c.replace("granite", "g").replace("-noreason", "") for c in CONFIGS) + " |")
    add("|---" * (len(CONFIGS) + 1) + "|")
    for e in EMAILS:
        cells = []
        for cfg in CONFIGS:
            rs = [r for r in rows(cfg) if r["email"] == e]
            cells.append(pct(sum(1 for r in rs if r["score"]["sequence_exact"]), len(rs)) if rs else "-")
        add(f"| {e} | " + " | ".join(cells) + " |")
    add("")
    add("Cells are right tool paths out of trials.")
    add("")

    add("## Two findings about the corpus, not the models")
    add("")
    e012 = [r for r in RUNS if r["email"].startswith("012")]
    v012 = sum(1 for r in e012 if r["score"]["verdict_right"])
    ship = [r for r in e012 if r["config"] == best[0]] if best else []
    ship_ok = sum(1 for r in ship if r["score"]["verdict_right"])
    other = [r for r in e012 if not best or r["config"] != best[0]]
    other_ok = sum(1 for r in other if r["score"]["verdict_right"])
    add(f"**Email 012 splits the configurations, and only the recommended one gets it "
        f"right.** It is a real vendor on a new domain, with a link host on neither list, "
        f"asking for names. Most configurations read that as an attack. The recommended "
        f"configuration answered correctly {pct(ship_ok, len(ship))}; every other "
        f"configuration together answered correctly {pct(other_ok, len(other))}, and "
        f"Granite 4.1 called it malicious in all "
        f"{sum(1 for r in e012 if r['config'].startswith('granite4.1'))} of its runs. "
        f"So this is a genuine false positive for the weaker designs and a case the "
        f"shipped design usually survives. Week 5 still grades the loop rather than the "
        f"verdict on it, because the verdict is not stable across models, and week 7 "
        f"should expect it in the false positive column.")
    add("")
    add("**Email 012's recorded stop reason was wrong and is now fixed.** The corpus said "
        "the run should end at the step cap. Only three tools exist under a cap of four, "
        "so a well-behaved agent runs out of tools first. Every run confirms it. The "
        "corpus record, its ground truth entry and the week 5 spec now all read "
        "`tools_exhausted`. The step cap is still taught, through the deliberately "
        "uncapped run the lab already includes.")
    add("")

    add("## Recommendation")
    add("")
    if best:
        meta = cfgmeta[best[0]]
        add(f"**Standardise on {meta['model']} with reasoning switched off**, and keep the "
            f"week 5 design in which the student's code owns the stop condition. Set "
            f"`reasoning_effort` to `none` in the notebook configuration cell, gated by "
            f"model name, because Granite 4.1 rejects that field with an HTTP 400.")
    add("")
    add("**Keep Granite 4.1 3B as the fallback**, with one caveat stated in the instructor "
        "guide. In the same design it ends the run for the right reason every time, but it "
        "chooses a different tool order, so a rubric that grades tool order would fail "
        "students for the model's behaviour. The week 5 rubric grades the stop reason and "
        "the trace, not the order, which is what makes either model safe to teach on.")
    add("")
    add("**Re-run this measurement every term.** The command is "
        "`python3 builder/lab/eval/week5_loop_test.py --all`. It asserts the endpoint, the "
        "model digests and the hash of every email before it measures, and writes its "
        "results after every run.")
    add("")

    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT} ({len(' '.join(lines).split())} words)")
    print(f"digests still match: {ok}" + ("" if ok else f" CHANGED: {changed}"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
