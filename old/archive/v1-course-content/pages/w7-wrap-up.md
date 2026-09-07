::: learned
- Extending the harness means writing a small YAML file, not writing Python.
- The schema checks your case before any request goes out, and the error
  message names the field that is wrong.
- An attack that lands once in five is a working attack, because an attacker
  gets to try again.
- A fix that holds four times in five has not worked. It failed more slowly.
- Those two rules point in opposite directions on purpose, because being wrong
  is expensive in different directions.
- A trial that errored is not a trial the attack failed. Scoring a rate limit
  as a clean result reads exactly like a working defense.
- A fix that blocks one attacker address fixes an instance. A rule about which
  recipients are allowed at all fixes the class.
- Remediation is graded on two suites. The attack has to stop, and normal work
  has to keep working.
:::

::: did
- Added at least two attack cases of your own to the harness.
- Ran the full harness and recorded the rates before any fix.
- Built one real control in `before_tool_call()`, in code, with a reason
  string that lands in the ledger.
- Ran the harness again and showed the attack landing in zero trials.
- Showed the benign baseline still passing, so the fix was not an outage.
- Read a poisoned results file and said what you would check first.
- Named a defect that you know remains in your own fix.
:::

::: checkpoint
Answer these for yourself before the final block opens.

1. Your fix holds in 5 of 5 trials. Name one attacker who still gets through,
   and say how.
2. A run reports an attack at 0 of 5, with 4 trials errored. What do you write
   in the report?
3. Somebody proposes removing the mail tool to close the finding. Give the
   two-sentence answer.
4. You have your before numbers and your after numbers. Which single line from
   each is the evidence in your finding?
5. In your own words, why does a fix have to hold every time when an attack
   only has to work once?

**Answers:**

1. Anyone who reaches an address on your allowlist that forwards elsewhere.
   Your rule checks the recipient, not where the message ends up.
2. One trial completed, and it did not land. Report 0 of 1 completed with 4
   errored, because an errored trial is not a trial the attack failed.
3. It stops every attack case and it also stops the product. A control that
   blocks everything is not a control.
4. The result line for that one case, with its rate, from each run. The two
   rates side by side are the claim.
5. An attacker gets to try again, so one hit is a win. A defense that fails
   once has already let the thing through.
:::

::: next
The final block opens on day 50 and adds no new content: the findings report
due day 52, the exam due day 54, and a three minute walkthrough of your own
repository. Late work from weeks 1 through 7 closes on day 51, so clear your
backlog first.
:::
