::: intro
Part 1 covered the shape you ask for and the check that proves you got it. This page covers the other half: what your code does when the answer comes back wrong.

Give this page 22 minutes. With part 1 that's the 42 minutes of reading this week.
:::

::: section | A wrong answer is a normal condition
**A failed answer is one your code can't load or one that doesn't match the schema.**

It isn't a reason to stop the run. Your code records the problem and decides whether to try again.

Nothing in the model promises you a shape. It writes one likely character after another. A schema in the prompt makes the right shape far more likely. It doesn't make it certain.

Four shapes matter in this lab.

**Extra text around the answer.** The model adds a sentence, or wraps the answer in code fences.

```text
Here is the classification you asked for:
{"verdict": "benign", "category": "spam", "confidence": 0.6}
```

The load fails on the first word. "Here" isn't the start of a JSON object.

**Cut off partway.** The answer stops before the brackets close.

```text
{"verdict": "malicious", "category": "credential_ph
```

Python reaches the end, finds no closing quote or brace, and raises an error.

**Nothing at all.** The reply is empty and the stop reason is `length`.

```text
content: ""      stop reason: length
```

A **stop reason** says why the model stopped writing. `length` means it reached the answer limit. A **reasoning block** is text a model writes to itself before its answer. When the model spends the whole limit on that block, the answer never starts.

This is measured, not imagined. In one set of course tests, at one token limit, most runs came back empty with a stop reason of `length`. Another set wouldn't give the same count. Your notebook turns the reasoning block off, so your own runs shouldn't look like that.

**JSON that breaks a schema rule.** This answer loads, but its confidence is over this lab's reporting limit.

```json
{"verdict": "malicious", "category": "credential_phish",
 "confidence": 0.95, "indicators": ["lookalike sign-in page"]}
```

`strip_reasoning()` arrives written for you. It removes a leading reasoning block, a stray closing tag, or a fence that starts the answer. It doesn't rescue JSON buried after ordinary prose. `extract_json()` returns `None` when the cleaned text still won't load. The schema check catches the fourth shape after loading succeeds.
:::

::: section | The retry, and the one rule that makes it work
**A retry is asking again after an answer fails to load or fails the schema.**

One rule decides whether a retry is worth the call. **Send the problem back with the request.** Don't send the same request twice.

Your live range retry carries the checker's own words:

```text
Your last answer had these problems:
confidence is 0.95, and it has to be from 0.0 to 0.9
```

The added line does measurable work for this rule. In course tests, 24 of 24 replies changed to 0.85 and passed when the range problem was added. A bare re-ask changed none of 24; every reply stayed at 0.95.

That result is specific to the number rule. The same model usually failed when it was asked to shorten a list. Exact feedback can help without making every problem recoverable. Keep the three-try cap.

A load failure can't tell the checker whether the text was cut off, empty, or wrapped in prose. Those shapes share one recovery action:

```text
The answer did not load as JSON. Return one complete JSON object with no words before or after it.
```

The attempt record keeps the raw reply so a person can inspect the original shape. The next prompt carries the common action the model can follow.

A retry fixes the contract, not the judgment. Returning 0.85 instead of 0.95 doesn't prove the model became less sure. A well-shaped wrong verdict or an allowed but wrong category can still pass. Week 7 measures that.
:::

::: section | When the tries run out
A loop that runs out of tries still has to do something. Never nothing.

Your `classify_email()` returns `None` when no try passed. That's a plain signal, and the code that called it can read it.

Three things then have to be true.

1. The failure is recorded, with the problems that caused it.
2. The run keeps going. One bad email doesn't stop the other three.
3. Nothing downstream treats `None` as a verdict.

The third one matters most on a real team. An email with no usable answer isn't benign. It's unanswered, and a person picks it up.

That's why your lab records every try, good or bad. A grader reads your file and sees that the check ran. You read it later and see what the model actually said.

Write the failure down where a person will find it. An email your agent couldn't answer is work nobody has done yet. Nobody knows that unless the file says so.
:::

::: callout note | Stop and think
Your first try reports `confidence: 0.95`. The week 2 check rejects it.

What goes into the second prompt that wasn't in the first? Answer before you read the next line.

The exact range problem from `schema_errors()`. In the controlled course test, adding that problem changed the next answer. Sending the unchanged prompt didn't.
:::

::: section | Every retry is another paid call
Each try costs tokens. An email that takes three tries costs about three times an email that takes one.

Four emails is small. Four thousand isn't, and that's the size a real queue runs at. Retries are the line item that grows fastest when nobody is watching it.

Two habits are worth building now.

- Ask well the first time. A clear instruction is cheaper than a retry.
- Keep the cap small. Three tries is plenty for this work.

Your token counter prints a line after every call. Watch it while you work.
:::

::: section | Then open the lab
The lab notebook does all of this on four saved emails. You write two functions.

`extract_json()` cleans and loads a reply. `classify_email()` checks a candidate, asks again with the problems attached, and stops after an answer is accepted or three tries are used.

A short saved contract test checks your code the same way every time. The four-email run is where you observe the live model. Which email retries may change.

Keep both reading pages open beside the notebook.
:::

::: reading | Why output gets checked
This is one entry, named Improper Output Handling, from a list of the ten most common security problems in software that uses a language model. It's published by a nonprofit that writes open security guidance.

Read the summary and the prevention steps. Ask yourself one thing while you read. Which prevention step is the schema check you build this week?

[Top 10 for Large Language Model Applications, 2026 edition, OWASP Gen AI Security Project](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
:::

::: sources | Sources
| Source | What it gives this page |
|---|---|
| *Top 10 for Large Language Model Applications*, 2026 edition. OWASP Gen AI Security Project. Read the entry named Improper Output Handling. [genai.owasp.org](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | Why model output is checked before anything downstream uses it. Creative Commons Attribution-ShareAlike 4.0 |

The measured token numbers on this page come from the course's own tests of the model server this class uses.
:::
