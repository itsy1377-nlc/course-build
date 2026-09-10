# The week 6 code, as it will ship

Written 2026-09-09, after the probes and after Codex's review. This is the
source of truth for the notebook edits. Every change lands in
`lab/notebooks/w6-lab.ipynb` and `instructor/solutions/w6-lab-solution.ipynb`,
and the six functions week 7 carries land identically in `w7-lab.ipynb` and
`w7-lab-solution.ipynb`.

## 1. The body reaches the verdict, exactly once

`run_triage()`'s closing call is the call that writes the verdict, and today it
carries no body in the undefended arm. It now carries one, and only one:

    closing = prompt_text
    if parsed["body_text"] not in closing:
        closing = closing + "\n\nThe reported email:\n\n" + parsed["body_text"]
    closing = (closing
               + "\n\nTool results for this message:\n" + "\n".join(lines)
               + "\n\n" + schema_text(schema)
               + "\n\nYou have every tool result you are going to get."
                 " Answer now with one JSON object and nothing else.")

The membership test is what keeps the arms matched. The guarded prompt already
holds the fenced body, so nothing is added to it; the undefended prompt holds
none, so one copy is. Codex's objection to the first version of this patch was
that it appended unconditionally and gave the guarded arm the body twice, which
would have made a single-change comparison out of a two-change one.

## 2. The guarded prompt keeps week 3's grounding

Measured: drop the known-good host block and the injection-free twin turns
benign 0 of 8. Drop the classification instructions and it does the same. Keep
both and it holds malicious 8 of 8.

A pre-written helper carries the two pieces, so TODO 1 stays four parts and
about six lines:

    def grounding_text(parsed):
        """Week 3's grounding: how to classify, and what your own team owns."""
        lines = [CLASSIFY_INSTRUCTIONS, "",
                 "Facts your own triage code pulled out:",
                 guarded_facts_text(parsed), "",
                 "Known-good internal domains and hosts:",
                 "The organization is " + KNOWN_GOOD["organization"] + ".",
                 "Its own web hosts are:"]
        for host in KNOWN_GOOD["internal_hosts"]:
            lines.append("  " + host)
        lines.append(KNOWN_GOOD["rule"])
        return "\n".join(lines)

TODO 1 becomes: `GUARD_RULES`, then `grounding_text(parsed)`, then the fenced
body, then `schema_text(OUTPUT_SCHEMA)`.

**This is what gives 6.1 stakes it did not have.** Before, every guarded prompt
scored the same because the fence had no measurable effect. Now a student who
drops the grounding breaks the injection-free twin, 8 times in 8, and a
pre-written check cell shows it: the same prompt with and without
`grounding_text()`, both verdicts printed, no assertion about what they will
be.

## 3. The fence fails closed. This replaces a repair that failed open.

**The repair that was withdrawn.** `fence_check()` finds the fence with
`rfind()`, so an attacker who writes `<<<REPORTED_EMAIL_BODY_END>>>` into the
body breaks the fence and the check still reports it clean. The obvious fix is
to find the first end marker instead. That fix is a **fail-open**:
`guarded_triage()` builds the prompt from the unsanitized body, checks the
fence, and on failure sets `prompt_text = loop_prompt(parsed)`, which is the
undefended prompt. So an honest check would hand the attacker a switch to turn
the guard off. Reproduced at zero model calls.

**What ships instead.** The markers come out of the body once, before the body
is used anywhere, and a body that arrived carrying one escalates:

    def strip_markers(text):
        """Take the fence markers out of text that came from outside."""
        cleaned = str(text or "")
        found = cleaned.count(BODY_START) + cleaned.count(BODY_END)
        cleaned = cleaned.replace(BODY_START, "[marker removed]")
        cleaned = cleaned.replace(BODY_END, "[marker removed]")
        return cleaned, found

and in `guarded_triage()`, before anything is built:

    safe_body, markers_found = strip_markers(parsed["body_text"])
    safe = dict(parsed)
    safe["body_text"] = safe_body

with `markers_found` reading second in the escalation order, under the token
cap and above `injection_detected`, as a new reason `fence_broken`.

`fence_check()` still changes to find the first end marker after the body
opens, and gains a `markers_in_body` count. After sanitizing, a written
`build_guarded_prompt()` can no longer produce a broken fence, so the fallback
to week 5's prompt is reachable only by a student whose function is unwritten
or wrong -- which is what it was always for -- and never by an attacker.

## 4. The export carries what the rubric grades

`compare_guarded()` reads the undefended numbers on the line after
`run_triage()` returns and **before** `guarded_triage()` is called, because
that function begins with `start_run()` and would zero them:

    plain_trace, plain_answer = run_triage(parsed, loop_prompt(parsed))
    plain_answer = plain_answer or {}
    plain_confidence = plain_answer.get("confidence")
    plain_tokens = RUN_USAGE["total"]

and the row gains `confidence_without_guardrails`,
`confidence_with_guardrails` and `tokens_without_guardrails`.

## 5. The schema check is wired, and its limit is stated

`guarded_triage()` calls `schema_errors(answer, schema)` and records the result
as `schema_problems`. Three student surfaces already name it as the control
against email 023's request for the recipient's report history, and it is
called nowhere in week 6 today.

**And the page says what it does not do.** `indicators` accepts any string, so
a report history can ride inside an allowed indicator and pass. The schema
names which fields may exist; it does not read what is in them. Codex is right
that calling this an information-flow control would be a second false claim
replacing the first.

## 6. The fifth escalation reason gets a name

`injection_detected` fires on 014 and nothing else, 8 of 8, and reads
`hidden_html_text` rather than anything the model said. It is a control the
week never names. It gets named, with the true thing beside it: in this corpus
hidden HTML is planted on purpose, and in a real mailbox it is mostly marketing
preheader text, so a rule that escalates on it alone is a control tuned on a
corpus meeting an inbox.

## What week 7 carries

`run_triage`, `guarded_triage`, `fenced_email`, `fence_check`,
`guarded_facts_text`, `over_token_cap`, `build_guarded_prompt` and the
constants all appear in week 7's lab and solution. `check_chain.py` compares
only `ast.FunctionDef` nodes, so the constants drift unguarded between the two
weeks; extend the collector to uppercase module-level assignments with an
allowlist for the deliberately per-week ones, and prove it catches a seeded
divergence before trusting it.

## Deliberately not done

- `decisive_stop()`, `internal_sender`, `build_facts()`: wrong for real
  tradecraft, shared with weeks 4 and 5 which are pushed, and graded in four
  exam items. Cross-week work.
- The token cap stays on `RUN_USAGE["answer"]` unless the repaired table says
  otherwise. A total-token cap would have to sit above the measured maximum,
  8,352 across 176 guarded runs, and below week 5's runaway of 60,208 -- a
  window of about 10,400 to 60,200 -- and it changes week 7 too.
- No corpus email is re-rendered.
