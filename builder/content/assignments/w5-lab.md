::: intro
This week your agent takes more than one turn. It asks for a tool, reads the result, and decides what to ask for next. A rule stops it, and a cap stops it when the rule does not.

Thirteen to fifteen lines of your own code, in one clearly marked TODO cell. Everything else in the notebook is written for you. Read the **Week 5 reading** first and run the **Week 5 sidebar notebook**. Plan about three hours.
:::

::: directions
1. Open the **Week 5 lab notebook**. Run every cell from the top, in order. Stop when you reach the TODO cell.
2. Read the output of cell 8. It runs one pass of the loop with every value printed, so you see one pass before you write many.
3. Read cell 10. It calls each new helper on its own and prints what it hands back.
4. Read cell 11. It states the loop in six numbered sentences, in the order the code runs.
5. Fill in **TODO 1**, cell 12. Your `run_loop(parsed, prompt_text, max_steps=MAX_STEPS, step_guard=None)` writes those six sentences as code. It counts the step, asks the model for a tool, runs it, and records the result. It stops when a result settles the case. When nothing settles it, `out_of_room(trace)` names why the run ended. That is 13 to 15 lines, and every line calls a helper that already works.
6. Run cell 13, the check cell. It runs your loop on email 011 alone, the shortest case, and prints the trace. It says whether you got one step and the stop reason `internal_sender`.
7. Run cell 14, the cell named "Run all six emails". It prints one trace table per email, then the token total under the last table. **This is the cell you screenshot.**
8. Fix what breaks. Read the last line of any traceback first. It names the error type and the thing that failed.
9. Run cell 15. It runs email 012 again with the cap taken out, stopping only at twenty steps, and prints both token totals. Read cell 16 next.
10. Run cell 17, the export cell. It writes `week5_loop_trace.json` and prints the full path and the first few lines.
11. Open that file and read it. Check that each of the six runs carries its tools in the order they ran, a step count, and a stop reason.
:::

::: callout warning | Two things that stop this lab
Your `while` line carries two tests and no third one. A step has to be left, and a usable tool has to be left. Drop either test and the run keeps asking for tools it already ran.

Leave `step_guard` empty this week, and still write the `if` line that calls `guard_says_stop(step_guard)`. Nothing is passed in, so it cannot fire yet. Next week passes a guard in, and you never reopen this cell.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 20 | All three items are present and readable. |
| Bounded tool loop | 40 | The file holds six runs. Each shows an ordered tool list, a step count of four or fewer, and one of the five stop reasons. |
| Reading your own trace | 20 | The written answer names the correct step count, stop reason and second tool from your own file. |
| Cost of an uncapped run | 20 | The written answer gives both token totals and says what the cap saved. |
| **Total** | **100** | |

Which tool the model asks for second is its choice, not yours. Any second tool earns full credit when your answer names the one your run picked.

Nothing here is graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, the cell named "Run all six emails". All six trace tables have to be visible, with the step count and the stop reason readable on each. Keep the token total under the last table in the picture. If the six tables do not fit, lower your browser zoom and capture again.
2. **One file.** `week5_loop_trace.json`, attached as itself. Cell 17 prints its full path and its first few lines, so you can see exactly what you are attaching.
3. **A written answer**, typed into the submission box. Answer this:

    Answer in 3 to 5 sentences. Use numbers from your own run.

    1. Which email used the most steps? Give that step count and its stop reason from your file.
    2. Email 004 has no link to check. Name the second tool your agent chose. Say what the first result had told it.
    3. Give both token totals your notebook printed. One is the capped run, one is the uncapped run. Say what the cap saved.

Do not screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 35, Sunday 11:59 PM Central.
:::
