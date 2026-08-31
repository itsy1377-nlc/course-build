# Serving the model in a browser: assessment and decision

**Decision: technically possible, not worth building as the primary path.**
Two experiments are worth running anyway, and one of them matters to the path
we have already chosen.

The question was whether `bashtion-wasm`, a working x86_64 Linux VM in a
browser tab, could also serve a language model, giving the locked-down loaner
student a course that needs no executable on disk at all.

Assessed 31 August 2026. Every number below was read from source, measured, or
fetched. Where something is unmeasured it says so.

---

## 1. Inside the VM: no, on arithmetic

`bashtion-wasm` runs real QEMU compiled to WebAssembly, booting an unmodified
kernel with systemd as PID 1, restoring a pre-booted snapshot to a login
prompt in 13 to 15 seconds. It is an impressive answer to the same problem
student C has. It cannot host the model.

| Constraint | Value | Source |
|---|---|---|
| Guest RAM | 512 MB | `snapshot/make-snapshot.sh:28` |
| Guest CPUs | 1, emulated | `snapshot/make-snapshot.sh:27` |
| wasm module budget | `MEMORY=2300` MB | `.github/workflows/build.yml:62` |
| wasm32 address space | 4 GB, hard | the format |

The capability floor measured in section 11 of the course design is 3.4B
parameters. A Q4_K_M build of that is about 2.24 GB against 512 MB of guest
RAM, and raising guest RAM does not help: weights plus KV cache plus userspace
is roughly 3 GB, which exceeds the entire wasm module's budget before the
emulator, the translation buffers or device state are counted.

Speed makes it academic even if memory did not. Two penalties stack: wasm SIMD
is AVX-class only, and the one published wasm-versus-native ratio is 3 to 4x;
then QEMU TCG translates x86-64 guest code on one emulated vCPU with no AVX2
fast path. The 116-call suite is 4.3 minutes of inference natively and
plausibly over two hours in the guest.

**The structural point:** running in the VM is strictly dominated by running
in the page. You pay the wasm penalty either way. In the VM you additionally
pay TCG, the 512 MB cage and single-vCPU serialisation, and you gain nothing,
because the guest does not need the model to be local. It needs it reachable
at a URL.

## 2. In the page, with the guest reaching it: yes, and the channel is cheap

**WebLLM is disqualified, and this was measured rather than read.** Its native
`tools` parameter is gated by a hardcoded five-entry allowlist at
`src/config.ts:336-345`; the catalog has 167 models and five can receive a
tools request. Four of the five are Llama Community licensed. Running
`postInitAndCheckFields()` against Qwen3-8B, Qwen2.5-7B, Phi-4-mini and three
others returns `UnsupportedModelIdError` for every one.

Worse, the multi-turn loop is structurally broken. The engine returns
`{content: null, tool_calls: [...]}`, and feeding that back on turn two throws
`ContentTypeError` at `conversation.ts:506-509`. The obvious `content: ""`
workaround makes it silently worse: `tool_calls` is dropped from the rendered
prompt entirely, so the model receives a tool result with no record of the call
that produced it. That is silent corruption of exactly the shape this project
has spent its recent work removing. There is also no Granite anywhere in MLC:
zero of 51 registered architectures.

**wllama is the runtime that would work.** Its v3 wraps llama.cpp's
`server-context.cpp`, so it inherits llama.cpp's templates and native tool-call
parser, and it consumes GGUF directly, which means the artifact the course has
already measured is the input. `agent/llm.py` would need a `base_url` change
and nothing else, which preserves the design property that it "needs to know
nothing about which path a student took."

**The channel is the cheap part.** virtio-serial is already compiled into the
shipped 41 MB wasm binary, and the guest kernel has `CONFIG_VIRTIO_CONSOLE=y`
built in. Measured from the course's own 2,301 recorded traces, the channel
needs 0.8 to 1.5 KB/s sustained with 7.5 KB bursts, strictly sequential. That
is three orders of magnitude below what the transport does.

Three details would bite whoever built it: use `virtserialport` rather than a
second `-serial`, because the 16550 model drops bytes silently after four
retries and on a length-prefixed stream that is permanent desync; never give
the data port a `mon:` prefix, because the mux intercepts `0x01` and `0x01 0x78`
is `qmp_quit`; and touching `-serial` at all sets `default_serial = 0`, which
breaks the implicit `mon:stdio` mux the restore-resume path depends on and
produces a VM that restores paused forever with no error.

## 3. Why it is still the wrong path

The bundle runs natively: 2.2 seconds per call, a measured 12 to 22 minute
suite. The browser path on the same machine is 3 to 15 times slower in the
**good** case. The bad cases are what settle it, and every one is silent:

| Failure | What the student sees |
|---|---|
| `HardwareAccelerationModeEnabled=false`, set routinely for VDI | `navigator.gpu` still exists and feature detection passes; `requestAdapter()` resolves to null, giving `TypeError: Cannot read properties of null`. There is no software fallback: CPU adapters and the D3D11 backend are both unconditionally blocklisted |
| Session-only cookies | The whole origin is hard-capped at 300 MB (`quota_settings.cc:113-116`). A 2 GB model dies partway with `QuotaExceededError`, shards persist, the retry fails identically. It cannot be pre-flighted: `navigator.storage.estimate()` fabricates `usage + 10 GiB` on any machine with 10 GB of disk |
| `ClearBrowsingDataOnExitList` | Wipes the cache, except when the browser exits uncleanly, in which case it survives. Intermittent and unreproducible |
| Two GPU context losses | Blocks 3D for that origin specifically while every other site works, so "the course site is broken" |

**The failure asymmetry is the whole answer.** The bundle fails loudly:
the executable does not launch, immediately, reproducibly, one email to IT.
Every browser failure above is silent, per-machine, and invisible to the
instructor. This project's own record is that silent failures have one shape
and are the expensive kind. Adopting a delivery channel whose entire failure
surface is silent is moving the wrong way.

It also saves nothing. It is roughly 2 GB of model shards against a 2.2 GB
bundle: the same bytes, made less durable and harder to diagnose.

**The one thing it genuinely offers:** no executable ever touches disk, so
application control and SmartScreen cannot block it. If the fleet blocks the
bundle, that is decisive. If it does not, it is worth nothing.

## 4. Two experiments worth running

**Experiment A, half a day, no browser involved, and it matters regardless.**
The most likely kill condition is not browser policy at all: **no
licence-clean model under 2 GB has ever been tested at Q4 for the two-turn
tool loop.** Section 11 measured the floor at 3.4B under Ollama at its default
quantisation. The in-range Apache 2.0 candidates are granite-4.2-3b and
SmolLM3-3B, and Q4 is exactly the kind of change that breaks a marginal
capability.

Serve each under `llama-server` and run `build/modeltest/student_run.py`
against it, not a bespoke script, per this project's own measurement notes.
The pass condition is specific: after the first tool result comes back, does
the model emit a **second** `tool_calls`. **This question matters to the
portable bundle too**, because the bundle ships a Q4 model to a CPU-only
machine, so it should be run whatever is decided here.

**Experiment B, half a day, needs real loaners, and the artifact is reusable.**
A small static page served from the live host so it inherits the production
CSP and headers, printing four things: whether `requestAdapter()` returns an
adapter and its five relevant limits; how far a chunked write into the Cache
API gets before `QuotaExceededError`, which is the only reliable probe for the
300 MB cap; whether `crossOriginIsolated` holds with a second wasm module
alongside QEMU; and the browser's own GPU report.

Ship that page as the course's troubleshooting page whatever the outcome. It
is not throwaway code, and it answers the same questions the bundle's own
preflight needs.

## 5. What would flip this

Experiment B showing that application control blocks the bundle from executing
on the actual fleet. Then the browser path is not an improvement, it is the
only path, and it is worth the week.

Even then, one thing should be fixed from the start: do not ship the 116-call
suite to a browser tab. Ship the interactive single run there. The full sweep,
and certainly the per-term model comparison, is an instructor and CI workload
and always will be.
