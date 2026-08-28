::: learned
- Excessive agency is an action that is too broad or too permanent for the
  checks around it.
- Count the missing controls: allowlist, confirmation, rate limit, undo. Your
  agent's mail tool is missing all four.
- An attack does not have to be clever when nothing says no.
- Insecure tool authorization is a tool that never asks who is calling. Your
  target reads the caller's name, logs it, and then ignores it.
- An audit log is a receipt, not a lock. Accountability answers who did this.
  Authorization answers may you.
- A harness decides what happened by looking at the world, not at the answer.
- The detectors are ranked: side effect, canary, tool shape, text match.
- Text matching is not merely discouraged. The case file format refuses it, so
  a refusal can never be scored as a leak.
- Your canary tokens are built from your student ID, so your proof is yours.
:::

::: did
- Read about excessive agency and about insecure tool authorization.
- Read the OWASP LLM03 entry with a reading bridge.
- Walked through the annotated authorization flaw and answered four questions
  about the real code.
- Ran the shipped harness unmodified and read every part of its output.
- Recorded rates, statuses, evidence lines, and the two control results.
- Wrote one original attack payload and submitted the Project 2 checkpoint.
:::

::: checkpoint
Answer these for yourself before Week 7 opens. They are the shape of questions
you will see again.

1. Your agent sends mail with no allowlist and no approval step. Name the two
   controls you would add first, and say which one you would add if you could
   only have one.
2. A system logs every customer lookup with the caller's name. Is that
   accountability, authorization, or both? Say how you decided.
3. A classmate reports an attack as successful because the model replied "I
   will email that record now." What is wrong with that report?
4. Your harness reports 2 of 5 on an attack case. Is the system vulnerable?
5. Why can a canary token never fire on a refusal?
:::

::: next
Week 7 is the other half of the job. You will write attack cases of your own
as small YAML files, so no Python is needed to add one.

Then you will argue with numbers. An attack that lands once in five counts.
A fix that holds four times in five does not. You will learn why those two
rules are not the same rule.

Then you fix one weakness in code and prove it held.
:::
