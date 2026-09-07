::: intro
Part 1 covered the shape you ask for and the check that proves you got it. This page covers the other half: what your code does when the answer comes back wrong.

Give this page 22 minutes. With part 1 that is the 42 minutes of reading this week.
:::

::: section | A wrong shape is a normal condition
**Malformed output is an answer that does not match the shape you asked for.**

It is not a rare bug. It is a normal condition, and your code handles it like any other.

Nothing in the model promises you a shape. It writes one likely character after another. A schema in the prompt makes the right shape far more likely. It does not make it certain.

Three shapes turn up, and the lab shows you all three.

**Extra text around the answer.** The model adds a sentence, or wraps the answer in code fences.

```text
Here is the classification you asked for:
{"verdict": "benign", "category": "spam", "confidence": 0.6}
```

Your load fails on the first word, because "Here" is not the start of any JSON object. The answer itself was fine. It just did not arrive alone.

**Cut off partway.** The answer stops in the middle, so the brackets never close.

```text
{"verdict": "malicious", "category": "credential_ph
```

This one starts right and ends nowhere. Python reads to the end of the text, finds no closing bracket, and raises an error.

**Nothing at all.** The reply is empty and the stop reason is `length`.

```text
content: ""      stop reason: length
```

A **stop reason** is the short label saying why the model stopped writing. `length` means it ran into the token limit you set. A **reasoning block** is text a model writes to itself before its answer. When the model spends the whole limit on that block, the answer never starts.

This is measured, not imagined. In one set of course tests, at one token limit, most runs came back empty with a stop reason of `length`. Another set would not give the same count. Your notebook turns the reasoning block off, so your own runs should not look like that.

`strip_reasoning()` arrives written for you. It takes off a leading reasoning block, a stray closing tag and any code fences. Run it before you load. It fixes the first shape outright, and it costs nothing on the other two.
:::

::: section | The retry, and the one rule that makes it work
**A retry is asking again when the answer came back in the wrong shape.**

One rule decides whether a retry is worth the call. **Send the problem back with the request.** Do not send the same request twice.

An unchanged request gives the model nothing new. It is free to make the same mistake again. Adding the problems changes the prompt, so it changes the odds.

Your second prompt carries the plain words your check reported. It reads something like this.

```text
Your last answer had these problems. Fix them.
- category is 'phishing', and it has to be one of credential_phish, bec,
  vendor_fraud, malware_delivery, spam, legit_external, legit_internal
```

Now the model has something to fix. It is being told what was wrong, in the same words your own code used.

Cap the tries. Three is the cap this lab uses. A cap is not pessimism. It is the line between a loop that ends and a loop that does not. Week 5 makes that idea the whole subject.

A retry does not fix everything. It fixes shape. It does not make a wrong verdict right, because a well shaped answer passes the check whether or not the judgment is any good. Week 7 is where you measure that.
:::

::: section | When the tries run out
A loop that runs out of tries still has to do something. Never nothing.

Your `classify_email()` returns `None` when no try passed. That is a plain signal, and the code that called it can read it.

Three things then have to be true.

1. The failure is recorded, with the problems that caused it.
2. The run keeps going. One bad email does not stop the other three.
3. Nothing downstream treats `None` as a verdict.

The third one matters most on a real team. An email with no usable answer is not benign. It is unanswered, and a person picks it up.

That is why your lab records every try, good or bad. A grader reads your file and sees that the check ran. You read it later and see what the model actually said.

Write the failure down where a person will find it. An email your agent could not answer is work nobody has done yet. Nobody knows that unless the file says so.
:::

::: callout note | Stop and think
Your first try fails the check. You are about to ask again.

What goes into the second prompt that was not in the first? Answer before you read the next line.

The problems your check reported. Without them you have sent the same request twice and paid for it twice.
:::

::: section | Every retry is another paid call
Each try costs tokens. An email that takes three tries costs about three times an email that takes one.

Four emails is small. Four thousand is not, and that is the size a real queue runs at. Retries are the line item that grows fastest when nobody is watching it.

Two habits are worth building now.

- Ask well the first time. A clear instruction is cheaper than a retry.
- Keep the cap small. Three tries is plenty for this work.

Your token counter prints a line after every call. Watch it while you work.
:::

::: section | Then open the lab
The lab notebook does all of this on four saved emails. You write two functions.

`extract_json()` cleans a reply and loads it. `classify_email()` checks the answer, asks again with the problems attached, and gives up after three tries.

Keep both reading pages open beside the notebook.
:::

::: reading | Why output gets checked
This is one entry, named Improper Output Handling, from a list of the ten most common security problems in software that uses a language model. It is published by a nonprofit that writes open security guidance.

Read the summary and the prevention steps. Ask yourself one thing while you read. Which prevention step is the schema check you build this week?

[Top 10 for Large Language Model Applications, 2026 edition, OWASP Gen AI Security Project](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/)
:::

::: sources | Sources
| Source | What it gives this page |
|---|---|
| *Top 10 for Large Language Model Applications*, 2026 edition. OWASP Gen AI Security Project. Read the entry named Improper Output Handling. [genai.owasp.org](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) | Why model output is checked before anything downstream uses it. Creative Commons Attribution-ShareAlike 4.0 |

The measured token numbers on this page come from the course's own tests of the model server this class uses.
:::
