::: intro
In this lab your agent answers in a fixed shape, and your code checks that shape before it trusts the answer. Thirteen to seventeen lines of your own code, in two clearly marked TODO cells. Everything else in the notebook is written for you. Read both parts of the **Week 2 reading** first and run the sidebar. Plan about three hours.
:::

::: directions
1. Open the **Week 2 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read the output of cell 7. It shows what the model actually sends back, including a run that fails. Look at the stop reason on that one.
3. Fill in **TODO 1**, cell 10. Your `extract_json(text)` calls `strip_reasoning()`, tries `json.loads()`, and returns the dictionary. When the load fails it returns `None`. That's 5 to 7 lines.
4. Run cell 11, the check cell. It feeds your function four saved replies, one clean and three broken, and prints what each one returns. Fix your function until the clean one loads and the three broken ones return `None`.
5. Read cell 12. It defines `schema_errors()`, `ATTEMPT_LOG` and `log_attempt()`. You don't write these. You call them.
6. Fill in **TODO 2**, cell 13. Your `classify_email(parsed, max_tries=3)` builds the prompt with `build_classify_prompt()`, calls `ask_model()`, extracts the answer, checks it with `schema_errors()`, and logs the try. When the check reports problems, it asks again with those problems added to the prompt. It returns the checked answer, or `None` when no try passed. That's 8 to 10 lines.
7. Run cell 14, the results cell. It runs all four emails and prints one row each, then a token line under the table.
8. Fix what breaks. Read the last line of any traceback first. It names the error type and the thing that failed.
9. Run cell 15, the export cell. It writes `week2_classification.json` and prints the full path and the first few lines.
10. Open that file and read it. Check that every email has a `schema_ok` field and a `problems` list, including the emails that passed on the first try.
:::

::: callout warning | Two things that stop this lab
Your retry has to add the problems to the prompt. Sending the same prompt again isn't a retry, and the file will show three identical tries.

Your loop has to stop. `max_tries=3` is the cap. A loop with no cap can run until your token budget is gone.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 15 | All three items are present and readable. |
| Output validation | 50 | The file carries a checked answer for all four emails. It carries `schema_ok` and `problems` on every try, the accepted try included. Every failed try is recorded with the problems that caused it. |
| Results screenshot | 15 | The screenshot shows all four emails and the token line, and is readable. |
| Written answer | 20 | Three to five sentences carrying your own numbers. It names the email that needed more than one try. It copies the problem text your code reported. For a clean run it says so and gives the lowest confidence number in your own file. Either path also names one change to the instructions. |
| **Total** | **100** | |

Nothing here's graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, the results cell that runs all four emails. It has to show all four rows, each with the email id, verdict, category, confidence and tries used, plus the token line printed under the table. Capture the whole output in one image.
2. **One file.** `week2_classification.json`, attached as itself. The export cell prints its full path, so you can see exactly what to attach.
3. **A written answer**, typed into the submission box. Three to five sentences. Answer this:

    In 3 to 5 sentences, answer this. Which of your four emails took more than one try? Copy the exact problem your code reported on that failed try. If all four passed on try one, say so instead. Then give the lowest confidence number you saw. Either way, name one change you would make to the instructions.

Don't screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 14, Sunday 11:59 PM Central.
:::
