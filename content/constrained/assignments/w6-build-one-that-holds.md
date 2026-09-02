::: intro
Build the containment you recommended in week 5. Build it twice, measure it three
times, and show that ordinary work still runs. Ten points, due day 42.
:::

::: scope | Authorization and Scope
Run this only against the practice target this course gives you, using your own
agent and a model on your own computer. A commercial AI service is never a
permitted target, and neither is any system you do not own. See the Rules of
Engagement page in Start Here.
:::

::: directions | Directions
1. Write your containment in one sentence. Name the tool, the argument you will
   check, and what is allowed. Example: send mail only to the address on the
   customer record for the ticket in hand.
2. Pick the case that goes through the door you are closing. Your own case from
   week 3 is the usual choice. Name it in your write-up.
3. Run the baseline. Five trials, no control in place. Save the report.
4. Add your rule to the agent's system prompt, in one or two plain sentences.
   Run the same case again, five trials. Save the report.
5. Take the prompt rule back out.
6. Write the control in code, in `before_tool_call()`. Return allow or block,
   and a reason a grader can read. Run the same case again, five trials. Save
   the report.
7. Read the benign case in that last report. It has to pass all five trials.
   Then send one ordinary request by hand and confirm it finishes.
8. Report your three numbers in a small table: the version, how many trials out
   of five it landed in, and the status word the report printed.
9. Quote the one line from a record that shows your control acting: the blocked
   line, with your reason in it. Then name the side effect you checked, such as
   an empty outbox or a canary token that never moved.
10. Write one sentence naming something your control does not cover.
:::

::: callout tip | Keep the three reports apart
Name each report file for the version it measured before you run the next one.
Reports overwrite easily, and a lost baseline costs you two points you have
already earned. If your guard raises an error, the run blocks the call and
records the error, so read the reason before you assume the control worked.
:::

::: grading | Grading Criteria
| What earns it | Points |
|---|---|
| Baseline measured over five trials, case named, report submitted | 2 |
| The prompt version built and measured the same way | 2 |
| The control in code, measured, with the record line that shows it acting | 3 |
| Legitimate work shown still running, from the record | 2 |
| One sentence naming what your control does not cover | 1 |
| **Total** | **10** |

You are graded on the measurement, not on the result. A control that did not hold,
measured honestly and reported with its number, earns far more than a claim with
no baseline behind it.
:::

::: submit | How to Submit
Submit one file with your write-up: a text file or a PDF, your name at the top,
answers under the numbered headings above. Attach your three reports and your
`before_tool_call()` code as further uploads. Due Sunday 11:59 PM, day 42.
:::
