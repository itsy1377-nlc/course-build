::: intro
In this lab your agent answers in a fixed shape, and your code checks that shape before it trusts the answer. You write about 16 to 20 lines in two marked TODO cells. The saved contract test and everything else are written for you. Read both parts of the **Week 2 reading** first and run all four sidebar parts. Plan about three hours.
:::

::: directions
1. Open the **Week 2 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read the output of cell 7. It shows a full model reply and a call with too little answer room.
3. Fill in **TODO 1**, cell 10. Your `extract_json(text)` calls `strip_reasoning()`, tries `json.loads()`, and returns a dictionary or `None`. That's 5 to 7 lines.
4. Run cell 11. The clean saved reply must load. The three broken replies must return `None`.
5. Read cell 12. It defines `schema_errors()`, `ATTEMPT_LOG`, `log_attempt()`, and `answer_source()`. You call them; you don't rewrite them.
6. Fill in **TODO 2**, cell 13. Use `answer` as the accepted-value sentinel. Load each reply into `data`, check it, log it, and assign `answer = data` only when the problem list is empty. Add the problems to the next prompt after a failure. Return `answer` once, after the loop. That's about 11 to 13 lines.
7. Run cell 14, the saved contract test. It uses two answers written for that cell, not model output. It must report four first-attempt problems, an attempt 2, every problem copied into prompt 2, and a passing final answer.
8. Run cell 15, the live results cell. It runs all four emails. Every row passes only when `tries` is at least 1 and `ok` is `True`. Which rows retry may change.
9. Fix any row the warning names. Read the last line of a traceback first.
10. Run cell 16, the export cell. It writes `week2_classification.json`.
11. Open the file. Confirm that `retry_demo.problems_copied` and `retry_demo.schema_ok` are true. Confirm that all four email records have `schema_ok: true`, a `problems` list, and at least one attempt.
:::

::: callout warning | Two things that stop this lab
Your retry has to add the exact problems to prompt 2. A bare re-ask isn't the mechanism objective 2.3 asks you to build.

Your loop has to stop on an accepted answer, not merely on a dictionary that loaded. Keep `answer` as `None` until `problems` is empty, and keep the three-try cap.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 15 | All three items are present and readable. |
| Output validation | 50 | The file carries four checked live answers with `schema_ok: true`. Its saved `retry_demo` records first-attempt problems, prompt 2 contains those exact problems, and attempt 2 is recorded. |
| Results screenshot | 15 | One readable image shows all four live rows, `ok=True` on each row, and the token line. |
| Written answer | 20 | Three to five sentences carry results from the student's file. The answer names a retry and copies its problem, or reports a clean run and its lowest confidence. It also names one instruction change without treating a lower confidence as greater truth. |
| **Total** | **100** | |

Nothing here is graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of cell 15, the live results cell. Show all four rows, including each `ok` value, and the token line.
2. **One file.** Attach `week2_classification.json` as itself.
3. **A written answer.** In three to five sentences, say which email took more than one try and copy the exact problem from that failed try. If all four passed on try one, say so and give the lowest confidence in your file. Either way, name one instruction change. Don't claim that a lower confidence number means the model became less sure or more accurate.

Don't screenshot the configuration cell. Your key is pasted into it. If your key appears in a post or image, tell your instructor so it can be replaced.

Due day 14, Sunday 11:59 PM Central.
:::
