# Week 6 injection measurement, raw runs

Five models, 17 cases, 15 trials per case per path, 2026-09-07. Produced by
`lab/eval/week6_injection_test.py` against the LiteLLM proxy on loopback at the
temperature the notebooks use.

| File | Runs | State |
|---|---|---|
| `granite-3b.json` | 510 | complete |
| `granite-8b.json` | 510 | complete |
| `test-gemma3-12b.json` | 510 | complete |
| `test-llama31-8b.json` | 257 | **partial**, stopped once the decision was settled |
| `test-qwen3-14b.json` | 369 | **partial**, same |

The three `test-` models were served only for this measurement and have been
removed from the proxy. Nothing in the course can call them.

Read `world.email_sha256` in any file against the corpus before quoting a
number out of it. Read `usable` and `failed_runs` too: a run that never reached
the model still fills the summary with zeros, which reads exactly like a
guardrail that held.

The conclusion is in `../model-selection.md`. These are the runs behind it.
