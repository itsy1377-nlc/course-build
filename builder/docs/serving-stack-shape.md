# Serving stack shape: how the two course models answer

Phase 0 corpus support document for ITSY1377_builder, Agentic AI and Security Operations.
Recorded 2026-09-03 on the development machine. Weeks 2 and 4 of the course are written
against the response shapes documented here, so this file is the reference for how a
reasoning block, a JSON answer, and a tool call actually arrive over the wire.

Every request below was sent as plain HTTP (Python `urllib`, no SDK) to the
OpenAI-compatible chat completions endpoint. Every response excerpt is copied from the
saved raw JSON, with long strings cut and marked `...[trimmed]`. One model request ran at
a time. Nothing here is a mock.

## 1. Environment

| Item | Value |
|---|---|
| Machine | Apple M3 Pro, 36 GB unified memory, macOS 26.6.2 |
| Serving stack | Ollama 0.32.15 (`ollama --version` and `GET /api/version` both report `0.32.15`) |
| Endpoint | `http://localhost:11434/v1/chat/completions` (OpenAI-compatible) |
| Native endpoint (footnote only) | `http://localhost:11434/api/chat` |
| Models | `granite4.2:3b` (id 40577dc168a3, 2.2 GB on disk) and `granite4.1:3b` (id 6fd349357287, 2.1 GB on disk) |
| Client | Python 3.13.9 standard library `urllib.request` |

Terms used below. A *reasoning block* is text the model writes to itself before the
answer; on these models it is wrapped in `<think>` and `</think>` tags at the token level.
A *tool call* is a structured request from the model to run a named function with
arguments, which the calling code must execute and send back. `finish_reason` is the
field that says why generation stopped: `stop` means the model ended on its own,
`length` means it hit `max_tokens`.

### 1.1 `ollama show` facts (item 5 of the brief)

| Field | granite4.2:3b | granite4.1:3b |
|---|---|---|
| architecture | granite | granite |
| parameters | 3.7B | 3.4B |
| context length (model maximum) | 131072 | 131072 |
| embedding length | 2560 | 2560 |
| quantization | Q4_K_M | Q4_K_M |
| capabilities | tools, thinking, completion | completion, tools |
| baked-in parameters | temperature 1, top_p 0.95 | none |
| baked-in system prompt | none | none |
| license | Apache 2.0 | Apache 2.0 |

The model maximum is not what the server allocates. After loading, `ollama ps` showed
`CONTEXT 32768` for both models, so this Ollama install runs each model with a 32,768-token
window unless a request asks for a different `num_ctx` (which the OpenAI-compatible request
body cannot carry; it takes a Modelfile or a server environment variable). Memory footprint
at that window was 5.1 GB for granite4.2:3b and 5.0 GB for granite4.1:3b, both 100 percent
on GPU. No `OLLAMA_*` environment variables were set in the shell or in `launchctl`; the server is the desktop application's bundled `ollama serve` process.

### 1.2 Chat templates, as shipped inside each Ollama model

This matters because the template decides what the model literally sees, and it explains
the shapes recorded later.

`granite4.2:3b` ships a Jinja template with `enable_thinking` defaulting to `True`. With
thinking on, the generation prompt ends in `<|im_start|>assistant\n<think>\n`, so the model
starts its output already inside a reasoning block and closes it with `</think>` before
answering. With thinking off, the prompt ends in `<|im_start|>assistant\n<think></think>`
and the model answers directly. A `reasoning_effort` of `low` appends the literal string
`{reasoning effort: low}` to the last user message. Tool definitions are rendered into a
system message as a JSON list inside `<tools>` tags, and the model is told to emit calls as
`<tool_call><function=NAME><parameter=ARG>VALUE</parameter></function></tool_call>`. Tool
results are wrapped in `<tool_response>` tags inside a user turn. Assistant `reasoning_content`
in history is re-wrapped as `<think>...</think>`, and by default (`truncate_history_thinking`)
prior reasoning is stripped from turns before the last user message.

`granite4.1:3b` ships a Go template with no thinking support at all. Tools are rendered
into a system message inside `<tools>` tags, and the model is told to emit calls as
`<tool_call>{"name": ..., "arguments": {...}}</tool_call>` (JSON, not the parameter tags
the 4.2 template uses). Tool results are wrapped in `<tool_response>` tags inside a user
turn. Roles use `<|start_of_role|>` and `<|end_of_role|>` markers.

In both cases Ollama parses the tag-level output and rewrites it into OpenAI-shaped JSON,
which is what the rest of this document records.

## 2. What the vendor pages say (read on 2026-09-03)

These are the pages actually read for this document. They are cited here because the
brief asked for them; they are vendor and hosting URLs and must not be copied into any
student-facing page.

| Source | URL | What it says that matters here |
|---|---|---|
| Granite 4.2 3B model card (Hugging Face) | https://huggingface.co/ibm-granite/granite-4.2-3b | Reasoning mode is the default (`enable_thinking=True`). Non-thinking mode is `enable_thinking=False`; low-effort mode is `enable_thinking=True, low_effort=True`. The card states that `temperature=1.0` and `top_p=0.95` are required across all tasks and serving backends, with `max_new_tokens` 8192 in thinking mode and 2048 in non-thinking mode. Tool calls use the OpenAI function definition schema. Context is 131072 natively. The card's own parser example strips `<think>...</think>` from raw text. For other servers it names `reasoning_content` as the field that carries reasoning, which is not the name this stack uses (see section 3.1). |
| Granite 4.2 3B `generation_config.json` (Hugging Face) | https://huggingface.co/ibm-granite/granite-4.2-3b/resolve/main/generation_config.json | `"do_sample": true, "temperature": 1.0, "top_p": 0.95`. |
| Granite 4.1 3B model card (Hugging Face) | https://huggingface.co/ibm-granite/granite-4.1-3b | No reasoning mode. Tool calling follows the OpenAI function definition schema and the model writes `<tool_call>{"name": ..., "arguments": {...}}</tool_call>`. The generation example calls `generate()` with only `max_new_tokens`, which is greedy decoding, the equivalent of temperature 0. |
| Granite 4.1 3B `generation_config.json` (Hugging Face) | https://huggingface.co/ibm-granite/granite-4.1-3b/resolve/main/generation_config.json | No `temperature`, `top_p`, or `do_sample` fields at all. The card's default is therefore greedy decoding. |
| Ollama library, granite4.2 family page | https://ollama.com/library/granite4.2 | Tags 3b, 8b, 30b, all "128K context window". States thinking is on by default (`enable_thinking` true by default, model opens a `<think>` block before answering), `/set nothink` in the CLI turns it off, and the REST API uses a `think` field. The page's generic hyperparameter example block shows temperature 0.7, top_p 0.9, top_k 50; that block is an illustration, not the tag's parameters. |
| Ollama library, granite4.2:3b tag page | https://ollama.com/library/granite4.2:3b | Params section: `"temperature": 1`, `"top_p": 0.95`. Q4_K_M, 2.2 GB, 3.66B parameters. Lists "Thinking / extended reasoning (enable_thinking, reasoning_effort)". |
| Ollama library, granite4.1:3b tag page | https://ollama.com/library/granite4.1:3b | No params listed. Q4_K_M, 2.1 GB, 3.4B parameters. No mention of thinking. |
| Ollama docs, OpenAI compatibility | https://docs.ollama.com/api/openai-compatibility | `/v1/chat/completions` supports `model`, `messages`, `frequency_penalty`, `presence_penalty`, `response_format`, `seed`, `stop`, `stream`, `stream_options`, `temperature`, `top_p`, `max_tokens`, `tools`, `reasoning_effort` (values `high`, `medium`, `low`, `max`, `none`), and `reasoning` (an object with `effort`). `tool_choice` and `logit_bias` are not supported. Context size is changed through a Modelfile `num_ctx`, not the request. The page does not say which response field carries reasoning. |
| Ollama docs, thinking | https://docs.ollama.com/capabilities/thinking | Native API uses a `think` request field and returns `message.thinking`. "Thinking is enabled by default in the CLI and API for supported models." The page does not cover the OpenAI-compatible path. |

Net of the sources: for granite4.2:3b the documented default is reasoning on, with
temperature 1.0 and top_p 0.95; for granite4.1:3b there is no reasoning mode and the
documented example decodes greedily. Those are the decoding settings used for every
request below (4.2: `temperature 1.0, top_p 0.95`; 4.1: `temperature 0`).

## 3. granite4.2:3b

### 3.1 Plain question, no system prompt (item 1)

Request and response, default settings:

```json
REQUEST
{"model": "granite4.2:3b",
 "messages": [{"role": "user", "content": "Why is the sky blue? Answer in two sentences."}],
 "max_tokens": 1024, "temperature": 1.0, "top_p": 0.95}

RESPONSE  (HTTP 200, 3.54 s)
{"id": "chatcmpl-392", "object": "chat.completion", "created": 1788456065,
 "model": "granite4.2:3b", "system_fingerprint": "fp_ollama",
 "choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "The sky appears blue because shorter blue wavelengths of sunlight scatter more effectively in Earth's atmosphere due to Rayleigh scattering. This scattered ligh ...[trimmed 80 chars]",
     "reasoning": "Okay, the user asked why the sky is blue and wants an answer in two sentences. I need to keep it concise. I'll explain Rayleigh scattering causing shorter blue  ...[trimmed 176 chars]"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 26, "completion_tokens": 115, "total_tokens": 141}}
```

Where the reasoning appears: as a separate field, `choices[0].message.reasoning`. The
`content` field held only the answer. No `<think>` or `</think>` text appeared inside
`content` in any of the 35 successful granite4.2:3b calls made for this document, including the
calls where reasoning was cut off by `max_tokens`. The field is named `reasoning`, not
`reasoning_content`.

Which request fields control reasoning on this endpoint:

| Request field sent | Result | Honored? |
|---|---|---|
| (nothing) | `reasoning` field present, 115 completion tokens | default is reasoning on |
| `"think": false` | `reasoning` field present, 115 tokens | ignored silently |
| `"think": true` | `reasoning` present, 171 tokens | no visible effect (same as default) |
| `"think": "false"` | `reasoning` present, 183 tokens | ignored silently |
| `"reasoning": false` | HTTP 400, `json: cannot unmarshal bool into Go struct field ChatCompletionRequest.reasoning of type openai.Reasoning` | rejected |
| `"reasoning": {"enabled": false}` | `reasoning` present, 111 tokens | ignored silently |
| `"chat_template_kwargs": {"enable_thinking": false}` | `reasoning` present, 110 tokens | ignored silently |
| `"options": {"think": false}` | `reasoning` present, 413 tokens | ignored silently |
| `"reasoning_effort": "none"` | no `reasoning` key at all, 50 tokens, 1.01 s | honored: reasoning off |
| `"reasoning": {"effort": "none"}` | no `reasoning` key, 46 tokens, 1.03 s | honored: reasoning off |
| `"reasoning_effort": "low"` | `reasoning` = "Need two-sentence answer.\n", 55 tokens; `prompt_tokens` rose from 26 to 35 | honored: low effort (the template appends `{reasoning effort: low}` to the user turn) |
| `"reasoning": {"effort": "low"}` | same as above, 52 tokens | honored: low effort |
| native `/api/chat` with `"think": false` (footnote only) | `message.thinking` absent, 60 tokens | honored, but this is not the endpoint the course uses |

The reasoning-off request and response, for the record:

```json
REQUEST
{"model": "granite4.2:3b",
 "messages": [{"role": "user", "content": "Why is the sky blue? Answer in two sentences."}],
 "max_tokens": 1024, "temperature": 1.0, "top_p": 0.95, "reasoning_effort": "none"}

RESPONSE  (HTTP 200, 1.01 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "The sky appears blue because molecules in the atmosphere scatter shorter wavelengths of sunlight (blue light) more than longer wavelengths (red light). This sca ...[trimmed 93 chars]"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 26, "completion_tokens": 50, "total_tokens": 76}}
```

### 3.2 Strict JSON about a grocery-store notice (item 2)

The notice (synthetic, not an email, not security content):

> Attention shoppers: the bakery counter will close thirty minutes early tonight for a
> routine oven inspection. Day-old bread on the clearance rack is half price until closing.

The prompt asked for strict JSON only, no prose, no code fences, with exactly the keys
`verdict`, `category`, `confidence`, `indicators`. Validity was checked by stripping any
`<think>...</think>` block and any code fence from `content`, then `json.loads`, then
comparing the key set.

| Run | Request extras | finish_reason | completion_tokens | Latency | Shape of `content` | Valid JSON after strip | Exact keys |
|---|---|---|---|---|---|---|---|
| default 1 | `max_tokens 1024` | length | 1024 | 19.39 s | empty (reasoning used the whole budget) | no | no |
| default 2 | `max_tokens 1024` | length | 1024 | 19.15 s | empty | no | no |
| default 3 | `max_tokens 1024` | stop | 831 | 15.55 s | JSON only | yes | yes |
| default 1 | `max_tokens 4096` | stop | 1173 | 22.25 s | JSON only | yes | yes |
| default 2 | `max_tokens 4096` | stop | 861 | 16.16 s | JSON only | yes | yes |
| default 3 | `max_tokens 4096` | stop | 819 | 15.35 s | JSON only | yes | yes |
| reasoning off 1 | `reasoning_effort "none"`, `max_tokens 1024` | stop | 68 | 1.28 s | JSON only | yes | yes |
| reasoning off 2 | same | stop | 65 | 1.23 s | JSON only | yes | yes |
| reasoning off 3 | same | stop | 79 | 1.53 s | JSON only | yes | yes |
| json_object 1 | `response_format {"type": "json_object"}`, `max_tokens 1024` | length | 1024 | 19.44 s | empty | no | not checked |
| json_object 2 | same | stop | 634 | 11.90 s | JSON only | yes | not checked |
| json_object 3 | same | length | 1024 | 19.21 s | empty | no | not checked |

Counts: default reasoning with a 1024-token cap, 1 of 3 valid; default reasoning with a
4096-token cap, 3 of 3 valid; reasoning off, 3 of 3 valid; `response_format` json_object
with a 1024-token cap, 1 of 3 valid. Every failure was the same failure: the model was
still reasoning when `max_tokens` ran out, so `content` came back as an empty string with
`finish_reason: "length"`. When the model finished, it never wrapped the JSON in code
fences and never put prose or a reasoning block inside `content`; the reasoning was in the
separate `reasoning` field. In default mode the reasoning text ran 3,273 to 5,058
characters for this two-sentence notice.

Excerpts. A capped run:

```json
RESPONSE  (HTTP 200, 19.39 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "",
     "reasoning": "We need to read the notice, classify it: verdict (one of \"informational\", \"promotional\", \"urgent\"), category (a short noun phrase), confidence (a number from 0 to 1), indicators (a list of short strings quoting the words that drove your decision).\n\nWe must respond with strict JSON only ...[trimmed 4215 chars]"},
   "finish_reason": "length"}],
 "usage": {"prompt_tokens": 127, "completion_tokens": 1024, "total_tokens": 1151}}
```

A finished run in default mode (4096 cap):

```json
RESPONSE  (HTTP 200, 22.25 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "{\n  \"verdict\": \"informational\",\n  \"category\": \"closure\",\n  \"confidence\": 0.85,\n  \"indicators\": [\"closing early\", \"half price\"]\n}",
     "reasoning": "We need to read the notice, classify it: verdict (informational, promotional, urgent), category (short noun phrase), confidence (0-1), indicators ...[trimmed 4558 chars]"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 127, "completion_tokens": 1173, "total_tokens": 1300}}
```

A reasoning-off run:

```json
REQUEST (extras)   "reasoning_effort": "none", "max_tokens": 1024, "temperature": 1.0, "top_p": 0.95

RESPONSE  (HTTP 200, 1.28 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "{\n  \"verdict\": \"informational\",\n  \"category\": \"closure\",\n  \"confidence\": 0.9,\n  \"indicators\": [\n    \"Attention shoppers\",\n    \"the bakery counter will close thirty minutes early tonight\",\n    \"routine oven inspection\"\n  ]\n}"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 127, "completion_tokens": 68, "total_tokens": 195}}
```

### 3.3 Native tool call (item 3)

One tool, `get_weather(city)`, defined in the `tools` array; the question was about a
made-up city, Pellmoor Harbor. Six first-turn calls (3 default, 3 with reasoning off) all
produced a well-formed tool call: 6 of 6.

```json
REQUEST
{"model": "granite4.2:3b",
 "messages": [{"role": "user", "content": "What is the weather right now in Pellmoor Harbor?"}],
 "tools": [{"type": "function", "function": {"name": "get_weather",
     "description": "Get the current weather for a city.",
     "parameters": {"type": "object",
       "properties": {"city": {"type": "string", "description": "Name of the city"}},
       "required": ["city"]}}}],
 "max_tokens": 1024, "temperature": 1.0, "top_p": 0.95}

RESPONSE  (HTTP 200, 3.39 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "",
     "reasoning": "Okay, the user is asking for the current weather in Pellmoor Harbor. I have the get_weather function that requires the city name. ...[trimmed 250 chars]",
     "tool_calls": [{"id": "ONWg87FslQAS8TBLwKMbHxS0CGizZJgL", "index": 0, "type": "function",
                     "function": {"name": "get_weather", "arguments": "{\"city\":\"Pellmoor Harbor\"}"}}]},
   "finish_reason": "tool_calls"}],
 "usage": {"prompt_tokens": 289, "completion_tokens": 157, "total_tokens": 446}}
```

Exact shape of `message.tool_calls`: a list; each item has `id` (a 32-character random
string on this model), `index` (integer), `type` (`"function"`), and `function` with
`name` and `arguments`. `arguments` is a JSON **string**, not an object; the caller must
`json.loads` it. `finish_reason` is `"tool_calls"`. `content` is an empty string, not
null. In default mode the `reasoning` field is present alongside `tool_calls`; with
`reasoning_effort: "none"` the message has only `role`, `content`, `tool_calls`
(34 completion tokens, 0.64 s, all three runs identical).

Second turn. The assistant message was echoed back with `content: ""` and its
`tool_calls` (the `reasoning` field was not echoed), followed by a `role: "tool"` message
with `tool_call_id` and a JSON string as `content`, with the `tools` array included again:

```json
REQUEST (messages only)
[{"role": "user", "content": "What is the weather right now in Pellmoor Harbor?"},
 {"role": "assistant", "content": "",
  "tool_calls": [{"id": "ONWg87FslQAS8TBLwKMbHxS0CGizZJgL", "index": 0, "type": "function",
                  "function": {"name": "get_weather", "arguments": "{\"city\":\"Pellmoor Harbor\"}"}}]},
 {"role": "tool", "tool_call_id": "ONWg87FslQAS8TBLwKMbHxS0CGizZJgL", "name": "get_weather",
  "content": "{\"city\": \"Pellmoor Harbor\", \"temperature_c\": 17, \"condition\": \"light fog\", \"wind_kph\": 9}"}]

RESPONSE  (HTTP 200, 3.60 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "The current weather in Pellmoor Harbor is:  \n- Temperature: 17°C  \n- Condition: Light fog  \n- Wind: 9 kph  \n\nLet me know if you'd like additional details!",
     "reasoning": "Okay, the user asked for the weather in Pellmoor Harbor. I used the get_weather tool with that city name. The response came back with temperature 17°C, light fog, and wind of 9 kph. ...[trimmed 238 chars]"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 373, "completion_tokens": 182, "total_tokens": 555}}
```

All six second turns answered from the tool result with `finish_reason: "stop"` and no
further tool call. Reasoning-off second turns took 27 to 47 completion tokens and 0.61 to
0.99 s.

### 3.4 Usage fields and latency (item 4)

Every successful non-streaming response carried `usage.prompt_tokens`,
`usage.completion_tokens`, and `usage.total_tokens`. `completion_tokens` includes the
reasoning tokens: the capped JSON runs report 1024 completion tokens with an empty
`content`. Wall-clock latency measured around the whole HTTP call from Python, model
already loaded:

| Call type | Mode | n | Latency min / mean / max | prompt_tokens | completion_tokens min / mean / max |
|---|---|---|---|---|---|
| plain question | default reasoning | 1 | 3.54 s | 26 | 115 |
| plain question | reasoning off | 2 | 1.01 / 1.02 / 1.03 s | 26 | 46 to 50 |
| JSON classify, 1024 cap | default reasoning | 3 | 15.55 / 18.03 / 19.39 s | 127 | 831 / 960 / 1024 |
| JSON classify, 4096 cap | default reasoning | 3 | 15.35 / 17.92 / 22.25 s | 127 | 819 / 951 / 1173 |
| JSON classify | reasoning off | 3 | 1.23 / 1.35 / 1.53 s | 127 | 65 / 71 / 79 |
| JSON classify, json_object, 1024 cap | default reasoning | 3 | 11.90 / 16.85 / 19.44 s | 113 | 634 / 894 / 1024 |
| tool call, turn 1 | default reasoning | 3 | 2.70 / 3.08 / 3.39 s | 289 | 145 / 155 / 164 |
| tool call, turn 2 | default reasoning | 3 | 2.47 / 2.93 / 3.60 s | 373 | 123 / 147 / 182 |
| tool call, turn 1 | reasoning off | 3 | 0.64 / 0.64 / 0.64 s | 289 | 34 |
| tool call, turn 2 | reasoning off | 3 | 0.61 / 0.75 / 0.99 s | 373 | 27 / 34 / 47 |

Throughput implied by the capped runs is roughly 53 completion tokens per second. The
first call after a model load took longer (the 4.1 first call below shows the same
effect); every latency in these tables is from a warm model except where noted.

### 3.5 Context and quantization (item 5)

From `ollama show granite4.2:3b`: context length 131072, quantization Q4_K_M, 3.7B
parameters, capabilities `tools`, `thinking`, `completion`, baked-in parameters
`temperature 1` and `top_p 0.95`. Served window per `ollama ps`: 32768.

## 4. granite4.1:3b

### 4.1 Plain question, no system prompt (item 1)

```json
REQUEST
{"model": "granite4.1:3b",
 "messages": [{"role": "user", "content": "Why is the sky blue? Answer in two sentences."}],
 "max_tokens": 1024, "temperature": 0}

RESPONSE  (HTTP 200, 2.67 s; this was the first call after load, later identical calls took 0.78 s)
{"id": "chatcmpl-174", "object": "chat.completion", "created": 1788456317,
 "model": "granite4.1:3b", "system_fingerprint": "fp_ollama",
 "choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "The sky appears blue because the Earth's atmosphere scatters sunlight in all directions, and blue light is scattered more than other colors because it travels as shorter wavelengths. This phenomenon is known as Rayleigh scattering."},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 19, "completion_tokens": 42, "total_tokens": 61}}
```

Reasoning does not appear at all: no `reasoning` field, no `<think>` text in `content`.
The message has exactly `role` and `content`.

| Request field sent | Result | Honored? |
|---|---|---|
| (nothing) | plain answer, 42 tokens | n/a, no reasoning to control |
| `"think": false` | identical answer, 42 tokens | ignored silently |
| `"think": true` | identical answer, 42 tokens | ignored silently |
| `"chat_template_kwargs": {"enable_thinking": false}` | identical answer, 42 tokens | ignored silently |
| `"reasoning": false` | HTTP 400, same unmarshal error as 4.2 | rejected |
| `"reasoning_effort": "low"` | HTTP 400, `"granite4.1:3b" does not support thinking` | rejected |

The last row matters for the notebooks: any `reasoning_effort` value, including `"none"`,
is a hard error on 4.1 because the server checks the model's capabilities before it looks
at the value. The error body:

```json
{"error": {"message": "\"granite4.1:3b\" does not support thinking",
           "type": "invalid_request_error", "param": null, "code": null}}
```

At `temperature 0` the four successful plain-question calls returned byte-identical text.

### 4.2 Strict JSON about the same grocery-store notice (item 2)

| Run | Request extras | finish_reason | completion_tokens | Latency | Shape of `content` | Valid JSON after strip | Exact keys |
|---|---|---|---|---|---|---|---|
| default 1 | `max_tokens 1024`, `temperature 0` | stop | 46 | 1.09 s | JSON only | yes | yes |
| default 2 | same | stop | 46 | 0.85 s | JSON only | yes | yes |
| default 3 | same | stop | 46 | 0.85 s | JSON only | yes | yes |
| json_object 1 | `response_format {"type": "json_object"}` | stop | 49 | 1.10 s | JSON only | yes | not checked |
| json_object 2 | same | stop | 49 | 0.92 s | JSON only | yes | not checked |
| json_object 3 | same | stop | 49 | 0.91 s | JSON only | yes | not checked |

Counts: 3 of 3 valid in the default run, 3 of 3 with `response_format`. No code fences, no
prose, no reasoning block. All three default runs returned the same bytes:

```json
RESPONSE  (HTTP 200, 1.09 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "{\n  \"verdict\": \"promotional\",\n  \"category\": \"sale\",\n  \"confidence\": 0.85,\n  \"indicators\": [\"bakery\", \"clearance rack\", \"half price\"]\n}"},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 116, "completion_tokens": 46, "total_tokens": 162}}
```

Note the two models disagree about this notice: 4.2 called it `informational` in 8 of 8
finished runs and 4.1 called it `promotional` in 6 of 6. Both readings are defensible. The
course corpus ground truth must be written so that this kind of honest split cannot
happen on graded items.

### 4.3 Native tool call (item 3)

Same tool, same question, three runs: 3 of 3 well-formed tool calls, and the three
first-turn responses were identical except for the `id`.

```json
RESPONSE  (HTTP 200, 0.76 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "",
     "tool_calls": [{"id": "call_2nrvkm67", "index": 0, "type": "function",
                     "function": {"name": "get_weather", "arguments": "{\"city\":\"Pellmoor Harbor\"}"}}]},
   "finish_reason": "tool_calls"}],
 "usage": {"prompt_tokens": 185, "completion_tokens": 24, "total_tokens": 209}}
```

Shape: identical to 4.2 except the `id` format (`call_` plus 8 lowercase alphanumerics
here, versus a 32-character string on 4.2) and the absence of any `reasoning` field.
`arguments` is again a JSON string. `content` is an empty string. `finish_reason` is
`"tool_calls"`. Prompt tokens are lower than on 4.2 (185 versus 289) because the two chat
templates render the tool list differently.

Second turn, same message structure as for 4.2 (assistant echo with `tool_calls`, then a
`role: "tool"` message with `tool_call_id`):

```json
RESPONSE  (HTTP 200, 0.76 s)
{"choices": [{"index": 0,
   "message": {"role": "assistant",
     "content": "The current weather in Pellmoor Harbor is **17 °C** with **light fog** and a wind speed of **9 kph**."},
   "finish_reason": "stop"}],
 "usage": {"prompt_tokens": 253, "completion_tokens": 34, "total_tokens": 287}}
```

All three second turns produced this same sentence.

### 4.4 Usage fields and latency (item 4)

| Call type | n | Latency min / mean / max | prompt_tokens | completion_tokens |
|---|---|---|---|---|
| plain question (first call after load) | 1 | 2.67 s | 19 | 42 |
| plain question (warm) | 3 | 0.78 / 0.79 / 0.80 s | 19 | 42 |
| JSON classify | 3 | 0.85 / 0.93 / 1.09 s | 116 | 46 |
| JSON classify, json_object | 3 | 0.91 / 0.98 / 1.10 s | 102 | 49 |
| tool call, turn 1 | 3 | 0.45 / 0.55 / 0.76 s | 185 | 24 |
| tool call, turn 2 | 3 | 0.74 / 0.76 / 0.78 s | 253 | 34 |

`usage` was present on every successful response with the same three fields as 4.2.

### 4.5 Context and quantization (item 5)

From `ollama show granite4.1:3b`: context length 131072, quantization Q4_K_M, 3.4B
parameters, capabilities `completion`, `tools`, no baked-in parameters, no baked-in
system prompt. Served window per `ollama ps`: 32768, 5.0 GB resident, 100 percent GPU.

## 5. Summary table per model

| Question | granite4.2:3b | granite4.1:3b |
|---|---|---|
| Reasoning by default | Yes. Arrives in `message.reasoning`, a separate field. `content` holds only the answer. | No reasoning at all. |
| Inline `<think>` in `content` | Never observed (35 calls). | Never observed (16 calls). |
| How to turn reasoning off on `/v1/chat/completions` | `"reasoning_effort": "none"` or `"reasoning": {"effort": "none"}`. `"think": false`, `chat_template_kwargs`, `options.think`, `reasoning.enabled` are ignored silently; `"reasoning": false` is HTTP 400. | `"reasoning_effort": "none"` is accepted, HTTP 200, verified 4 September 2026. Only `low`, `medium` and `high` are HTTP 400 ("does not support thinking"). An earlier reading of this table generalised the rejection to every value, which is wrong and would have pushed the notebooks into guessing the setting from the model name. |
| Low effort | `"reasoning_effort": "low"` honored; reasoning shrinks to one line. | HTTP 400. |
| Strict JSON, 3 runs, default mode | 1 of 3 at a 1024-token cap (two ran out of tokens while reasoning); 3 of 3 at a 4096-token cap. | 3 of 3. |
| Strict JSON, 3 runs, reasoning off | 3 of 3 (65 to 79 tokens, about 1.3 s). | same as default |
| JSON shape when finished | JSON only, no fences, no prose. | JSON only, no fences, no prose. |
| `response_format: json_object` | Accepted; does not stop reasoning; 1 of 3 finished inside 1024 tokens. | Accepted; 3 of 3. |
| Tool call well-formed, 3 runs | 3 of 3 default, 3 of 3 reasoning off. | 3 of 3. |
| `tool_calls` shape | list of `{id, index, type: "function", function: {name, arguments}}`; `arguments` is a JSON string; `id` is 32 random characters. | same; `id` is `call_` plus 8 characters. |
| `finish_reason` on a tool call | `"tool_calls"` | `"tool_calls"` |
| `content` on a tool call | `""` (empty string), plus `reasoning` in default mode | `""` |
| Second turn after a `role: "tool"` message | Grounded answer, `finish_reason: "stop"`, 6 of 6. | Grounded answer, 3 of 3, byte-identical at temperature 0. |
| `usage` fields | `prompt_tokens`, `completion_tokens`, `total_tokens` on every response; `completion_tokens` includes reasoning tokens. | same three fields. |
| Latency, plain question (warm) | 1.0 s reasoning off, 2 to 3.5 s default | 0.8 s |
| Latency, JSON classify | 1.2 to 1.5 s reasoning off, 15 to 22 s default | 0.9 to 1.1 s |
| Latency, tool call turn 1 | 0.64 s reasoning off, 2.7 to 3.4 s default | 0.45 to 0.76 s |
| Decoding used | temperature 1.0, top_p 0.95 (documented as required) | temperature 0 (documented example is greedy) |
| Repeatability | Varies run to run at temperature 1.0. | Byte-identical across repeats at temperature 0. |
| Context: model maximum / served | 131072 / 32768 | 131072 / 32768 |
| Quantization, size resident | Q4_K_M, 5.1 GB | Q4_K_M, 5.0 GB |
| Error shape | HTTP 400 with `{"error": {"message", "type": "invalid_request_error", "param": null, "code": null}}` | same |

## 6. What the notebooks must tolerate

Weeks 2 and 4 are written against the shapes above. The list below is what the shared
`ask_model()` helper and the week 2 parser must handle so that the same notebook runs
against either model, and survives a different serving stack if the hosted environment is
not Ollama.

1. **Reasoning in three possible places, or nowhere.** On this stack it is
   `message.reasoning`. Other OpenAI-compatible servers name it `reasoning_content`, and a
   server with no reasoning parser leaves it inline as `<think>...</think>` at the front of
   `content`. granite4.1:3b never produces any. The parser must: read `content`; strip a
   leading `<think>...</think>` block if present; also strip a stray leading `</think>`
   with no opener (the 4.2 template starts the model inside the block, so a raw stack can
   return only the closer); then strip code fences; then `json.loads`. Read
   `message.get("reasoning") or message.get("reasoning_content") or ""` only for display.

2. **Empty `content` is a normal condition, with two meanings.** With
   `finish_reason: "tool_calls"` the answer is in `tool_calls`. With
   `finish_reason: "length"` the model ran out of tokens, on 4.2 usually while still
   reasoning; `content` is `""` and there is nothing to parse. Treat this as malformed
   output and retry. The week 2 retry loop should check `finish_reason` before it checks
   the JSON.

3. **`max_tokens` counts reasoning tokens.** In default mode 4.2 spent 819 to 1173
   completion tokens and 15 to 22 s on a two-sentence classification, and it exhausted a
   1024-token cap in 4 of 6 default-mode JSON runs. The same call with reasoning off spent
   65 to 79 tokens and about 1.3 s. Any per-run token cap (week 6) and the running token
   counter must read `usage.completion_tokens`, never the length of `content`. If 4.2 runs
   in default mode, `max_tokens` needs to be at least 2048 for a JSON task and the
   estimated cost per lab rises by roughly ten times.

4. **The reasoning switch is model-specific and must be gated.** The only field this
   endpoint honors is `reasoning_effort` (`"none"`, `"low"`, `"medium"`, `"high"`) or the
   object form `reasoning: {"effort": ...}`. Sending it to granite4.1:3b is an HTTP 400.
   The notebook configuration cell should therefore hold, next to `BASE_URL` and `MODEL`,
   a `MODEL_EXTRAS` dictionary that is `{"reasoning_effort": "none"}` for 4.2 and `{}` for
   4.1, and `ask_model()` should merge it into every request. Do not send `think`,
   `chat_template_kwargs`, or `options`; they are ignored without any warning, which is the
   worst kind of failure for a student to debug.

5. **`tool_calls[i].function.arguments` is a string.** Always `json.loads` it, and be
   ready for it to fail to parse (not observed here, but the model writes it). Treat `id`
   as opaque; the two models use different formats. Copy `id` into `tool_call_id` on the
   `role: "tool"` message. Echo the assistant message back with `content: ""` and its
   `tool_calls`; the `reasoning` field does not need to be echoed. Send the `tools` array
   again on the second turn.

6. **`tool_choice` is not supported.** The notebook cannot force a tool call, so week 4
   must treat "the model answered in prose instead of calling the tool" as a normal path
   and fall back to week 2's manual JSON parsing. It did not happen in 9 of 9 first turns
   here, but nothing prevents it.

7. **Errors come back as HTTP 400 JSON.** `urllib` raises `HTTPError`; the helper must
   catch it, read the body, and show `error.message` in plain words. Unknown top-level
   fields are ignored, not rejected, so a misspelled field does not raise.

8. **Repeats are identical at temperature 0.** granite4.1:3b returned byte-identical JSON
   three times and byte-identical tool calls three times. The week 1 nondeterminism
   observation needs `temperature` above 0 on 4.1; on 4.2 at the documented 1.0 the
   variation shows on its own (three different `indicators` lists for the same notice).

9. **`response_format: json_object` is a belt, not the trousers.** It is accepted by the
   server and both models returned valid JSON when they finished, but it does not stop 4.2
   from reasoning first, does not extend the token budget, and does not enforce the key
   set. Schema validation in student code stays required.

10. **Context is 32768 served, not 131072.** Plenty for a single email with headers,
    playbook snippet, and tool results, but the week 7 batch must be one request per email,
    never the whole corpus in one prompt. The window cannot be changed from the request
    body on this stack.

11. **Verdicts can differ between the two models on the same input** (informational
    versus promotional above). Ground truth in the corpus must be unambiguous on graded
    items, and the model comparison in the blueprint should report disagreements, not
    just accuracy.

## 7. Open questions

1. The hosted Jupyter environment's serving stack is not yet known. If it is not Ollama
   0.32.x, the reasoning field name, the tool-call `id` format, and the reasoning switch
   may all differ. This probe must be rerun against the production endpoint before Phase 2
   notebooks are finalized; the scripts and raw logs in `serving-stack-probe/` make that a
   ten-minute job.
2. Whether the course runs 4.2 with reasoning off (`reasoning_effort: "none"`: fast,
   cheap, 3 of 3 valid JSON, 6 of 6 tool calls) or in its documented default mode (15 to
   22 s and roughly 1,000 tokens per classification, and a token-cap failure mode students
   will hit). The week 5 loop test on both models should settle this; this document leans
   toward reasoning off for the labs, with one optional cell that shows the reasoning
   field for interest.
3. The "temperature 0" default for 4.1 rests on the model card's greedy example and an
   empty `generation_config.json`; Ollama's own fallback temperature for a model with no
   baked-in parameters was not verified in this session.
4. Streaming responses were not tested; the notebooks should stay non-streaming so
   `usage` is always present in one place.
5. Whether a newer Ollama release starts honoring `think: false` on the OpenAI path, or
   renames `reasoning`, is exactly the course-rot risk the risk register names. Re-run the
   probe each term.
6. This document cites vendor and hosting URLs because the brief asked for them. Nothing
   in it should be pasted into a student-facing page without removing those URLs and the
   product names.

## 8. Evidence files

All raw request and response JSON, one line per call, and the scripts that produced them:

- `/Users/aaron/workspace/dev/ITSY1377/builder/docs/serving-stack-probe/probe.py`: the harness (plain `urllib`, sequential calls, experiments `e1`, `e2`, `e3`, `extra`, with `--max-tokens` and `--suffix`).
- `/Users/aaron/workspace/dev/ITSY1377/builder/docs/serving-stack-probe/flags.py`: the extra reasoning-control field sweep and the single native-endpoint footnote call.
- `/Users/aaron/workspace/dev/ITSY1377/builder/docs/serving-stack-probe/summarize.py` and `excerpt.py`: the readers used to build the tables and excerpts above.
- `/Users/aaron/workspace/dev/ITSY1377/builder/docs/serving-stack-probe/granite4.2-3b.jsonl`: 37 records (36 OpenAI-compatible requests, one of them rejected with HTTP 400, plus one native-endpoint call).
- `/Users/aaron/workspace/dev/ITSY1377/builder/docs/serving-stack-probe/granite4.1-3b.jsonl`: 18 records (16 successful calls plus 2 rejected requests).

To rerun against another endpoint, change `BASE` at the top of `probe.py` and run the
four experiments for each model, one process at a time.
