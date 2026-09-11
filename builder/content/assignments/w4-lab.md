::: intro
This week your agent may ask for a fact before it answers. The model names a tool, your code runs it, and the result goes back to the model.

Eleven to fourteen lines of your own code, in two marked TODO cells. Everything else is written for you. Read the **Week 4 reading** first and run the **Week 4 sidebar notebook**.
:::

::: directions
1. Open the **Week 4 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read the output of cell 6. It calls all three tools directly, with no model involved, so you see what each hands back.
3. Read cell 7. It prints one of the three tool definitions your notebook sends with the prompt.
4. Run cell 8. It makes one call and prints the tool request that comes back, with its call id and its arguments. Read cell 9 next. It says why those arguments arrive as text.
5. Fill in **TODO 1**, cell 10. Your `run_tool(name, arguments, parsed)` picks one of the three functions from the name the model sent. It takes the value it needs from `arguments` or `parsed`, then returns the result. An unknown name returns a plain sentence, not an error. That's 8 to 10 lines.
6. Run cell 11, the check cell. It feeds your function four saved requests. Three name one tool each. The fourth sends no values, so it tests your fallbacks. Fix your function until all four come back with a record.
7. Fill in **TODO 2**, cell 12. Your `tool_result_message(tool_call, result)` builds the message that carries the result back to the model, with the call id copied across unchanged. That's 3 to 4 lines.
8. Read cell 13. It defines `ask_with_tools()`, `start_messages()` and `triage_with_tools()`. You don't write these. You call them.
9. Run cell 14. It runs all six emails with tools and without, prints one row each, and closes with the token line. **This is the cell you screenshot.**
10. Run cell 15. It judges email 018 four times. Only the tool result changes between the runs. Read the four verdicts against each other. You need them for your written answer.
11. Run cell 16. It forces the prose path, so you see the model answer in sentences instead of asking for a tool.
12. Fix what breaks. Read the last line of any traceback first. It names the error and what failed.
13. Run cell 17, the export cell. It writes `week4_tool_calls.json` and prints the full path and the first few lines.
14. Open that file and read it. Every email carries two call ids: the one the model sent and the one your message carried back. Check each pair matches.
:::

::: callout warning | Two things that stop this lab
`arguments` arrives as text, not as a dictionary. Read it with `json.loads()` before you take a value out of it.

An unknown tool name has to return a plain sentence. Raise an error instead and one name you don't have ends the run for all six emails.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 32 | All three items are present and readable. |
| Tool call handled end to end | 40 | For each of the six emails the file records one of two things. Either the tool the model asked for, its arguments, the result your code returned, and a tool result message carrying the model's call id. Or the fallback record, showing the prose path was handled. Recorded results match the shipped tool records. |
| Reading your own results | 28 | The written answer reads cell 15's four verdicts on email 018, names the fact that moved one of them off the key, and reports one row of your own cell 14 table with its tool and fact. It says what that row does and does not settle. |
| **Total** | **100** | |

Nothing here can force the model to ask for a tool. A fallback record earns the same credit as a tool call. This lab scores your code, not the model's choice.

Nothing is graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, titled "All six emails, with tools and without". It has to show all six rows plus the token line under them. Capture the whole output in one image. If the rows don't fit, lower your browser zoom and capture again.
2. **One file.** `week4_tool_calls.json`, attached as itself. Cell 17 prints its full path and its first few lines.
3. **A written answer**, typed into the submission box. Three to five sentences. Answer this:

    Cell 15 judged email 018 four times, changing only what the tool answered. Name the tool whose fact moved the verdict off the answer key, and give that fact.

    Then take your own cell 14 table. Name one email whose two verdicts differ, with the tool your file records. Those two runs differ in more than the tool, so say what that row does and doesn't tell you.

Don't screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 28, Sunday 11:59 PM Central.

New to screenshots? **Using the notebook server** shows how to take one on
Windows, Mac, Chromebook and Linux, and the four ways one loses points.
:::
