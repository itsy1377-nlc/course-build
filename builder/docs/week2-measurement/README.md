# Week 2 retry redesign: measurements and accepted decision

**Run:** 2026-09-08, granite-3b through the course proxy at temperature 0.2.
The sections below give the call count for each experiment.

The harness is built from week 2's pre-written cells plus the reference
`extract_json()` and `classify_email()`. The experiments first measured the
notebook as shipped, then tested candidate rules.

Objective 2.3 is **"Retry a failed answer with the schema problems added to the
new prompt."** The accepted design uses a week 2 confidence reporting ceiling
of 0.9. The fair loop retried 64 of 128 classifications, recovered all 64, and
returned no empty answers. The isolation probe showed that feedback was the
active ingredient for this range rule.

## 1. The baseline: 1 failure in 260 classifications

`w2_pool.py` — 160 calls, 40 on each of emails 001 to 004. Raw record:
`granite-3b-160-answers.json`.

159 of 160 loaded and passed the schema. The single failure, on email 003, was
a reply that stopped mid-string with a finish reason of `stop`, not `length`.
With an earlier run of 100, the measured rate is **1 in 260**. A student
classifying four emails has roughly a 1.5% chance of ever seeing a retry.

What the model actually returns:

    indicator counts   {1: 8, 3: 11, 4: 41, 5: 97, 6: 2}
    confidence         0.95 (119)   0.85 (37)   0.9 (3)      <- three values, ever
    verdicts           100% stable per email

Two incidental findings. Indicators are sentences, not phrases — median 51
characters, 8 to 9 words — although the prompt asks for "short strings" and
`schema_errors()` never enforces it. And only 6% of indicators quote the
message verbatim, which is a week 3 and week 6 concern, not a week 2 one.

## 2. Tightening the indicator count is dead

`w2_retry.py` — the real `classify_email` loop with the cap moved **and**
`schema_text()` fixed so the prompt and the checker agree. Testing a cap the
prompt does not mention would measure a contradiction, not a model.

    cap at 3, 12 runs per email
      001  tries {1:11, 2:1}      gave up  0/12
      002  tries {1:10, 2:2}      gave up  0/12
      003  tries {1:2, 2:1, 3:9}  gave up  8/12
      004  tries {3:12}           gave up 12/12
      overall: no answer at all in 20/48 = 42%

    cap at 4, 12 runs per email
      001, 002, 003  tries {1:12}     gave up 0/12
      004            tries {1:9, 3:3} gave up 3/12
      note the tries: 1 then 3, never 2. Every run that failed try 1
      also failed tries 2 and 3.

Across both caps, **28 runs retried and 23 returned `None` — an 82% give-up
rate.** granite-3b will not shorten a list when told to, however clearly
`schema_errors()` tells it.

The lesson generalises past week 2: **the failure rate was never the binding
constraint. Recoverability was.** A rule can sit at an ideal 50% and still be
unusable, and only a live loop shows that.

## 3. Forced failures recover, but the number is confounded

`w2_recover.py` — three ways to fail try 1, 8 runs on each of four emails.

    A  truncation   (max_tokens=12 on try 1)   recovered 97%   gave up 0%
    B  schema stub  (LOADS_BUT_WRONG on try 1) recovered 97%   gave up 0%
    C  vague prompt on try 1                   recovered 97%   gave up 0%

Read this carefully. In all three, try 2 is an ordinary full-prompt call, which
passes on its own about 99% of the time. So 97% shows the appended problems do
not *degrade* the next answer. It does **not** show the model *using* them.
Experiment 5 exists because of this.

## 4. What the second prompt actually carries

`w2_probs.py` — 24 calls per mode.

    A truncation    "the answer is not a JSON object"  24/24   loaded as JSON 0/24
    C vague prompt  "the answer is not a JSON object"  24/24   loaded as JSON 0/24
    B schema stub   four specific problems (verdict, category, confidence, indicators)

An under-specified prompt makes granite-3b write prose, so it fails at the load
stage and yields the same single generic line as truncation. **Under-specifying
the prompt buys nothing over forced truncation**, and neither puts schema
problems into the new prompt, which is what objective 2.3 names.

## 5. The feedback is the active ingredient

`w2_feedback.py` — an isolation probe. The prompt still asks for 0.0 to 1.0;
only the checker is tightened to 0.9. Deliberately unfair, and not a proposed
design: it makes try 1 fail whenever the model returns its habitual 0.95, and
then follows the same failure with two independent second calls.

    try-1 failures                24/48 = 50%
    WITH the problems appended    24/24 = 100% pass    returns 0.85, every time
    BARE re-ask, nothing added     0/24 =   0% pass    returns 0.95, every time

Total separation. Objective 2.3's claim is real: the problems in the new prompt
are what fixes the answer, not the fresh call. This also explains experiment 2 —
the model is not deaf to correction, it specifically cannot shorten a list while
it can move a number immediately.

## 6. The fair confidence ceiling

`w2_fair.py` — the ceiling set in `OUTPUT_SCHEMA`, so `schema_text()` renders it
into the prompt as well. Week 2's single-sourcing does the work. Prompt line
reads `"confidence": a number from 0.0 to 0.9`. The real `classify_email` loop.

    20 runs per email
      001  tries {1:20}   gave up 0/20
      002  tries {2:20}   gave up 0/20
      003  tries {2:20}   gave up 0/20
      004  tries {1:20}   gave up 0/20

    retried 40/80 = 50%    gave up 0%    of those that retried, recovered 40/40 = 100%

Confirmed twice, at n=12 and n=20 per email, identical both times: **128 runs,
64 retries, 64 recoveries, no give-ups.** Unlike every count rule, this does not
collapse when the prompt is made fair.

Across the 128 measured classifications, emails 001 and 004 passed first try
and 002 and 003 retried. That split was exact in this model sample. It is not a
promise about a future student run.

### Accepted content judgment

The model returning 0.85 instead of 0.95 is **not** evidence it is less sure or
better calibrated. It obeyed a numeric boundary. The material calls 0.9 a
reporting rule for week 2 and never a calibration or accuracy improvement.
`content/pages/w2-content.md` carries the required disclaimer.

No student-facing sentence names the emails that must retry. A live row passes
when `tries` is at least 1 and `schema_ok` is true.

### What to re-measure after any model or proxy change

Run `w2_fair.py 20 0.9` and `w2_feedback.py 12 0.9` again. Confirm that the
fair run still has both first-try accepts and retries, at least 90% of retries
recover, and no more than 5% of all classifications return no answer. Retain
the causal wording only if feedback beats a bare re-ask by at least 50
percentage points and at least 90% of feedback retries recover.

## Running these

All six scripts expect `/tmp/w2_prewritten.py` and `/tmp/w2_solution_fns.py`,
extracted from the lab and solution notebooks, and a key at
`/root/.w2-eval-key`. They run from `~/eval/builder` on the litellm guest so the
corpus path walk resolves.

`lab/tools/run_notebook.py` cannot substitute for these measurements. Line
215 defaults the model to `granite4.2:3b` and the base URL to local Ollama.
Force `ITSY1377_MODEL`, `ITSY1377_BASE_URL`, and `ITSY1377_API_KEY` when a
gate must exercise the live week 2 model.
