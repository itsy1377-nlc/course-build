::: intro
This week your agent stops sending the email body on its own. You pull the facts out of the message and send those with it. The same code and schema then reach different verdicts.

Twelve to fifteen lines of your own code, in two clearly marked TODO cells. Everything else in the notebook is written for you. Read the **Week 3 reading** first and run the **Week 3 sidebar notebook**. Plan about two and three quarter hours.
:::

::: directions
1. Open the **Week 3 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read the output of cell 7. It parses email 005 and prints every key the parser hands back.
3. Read cell 8. It says which facts a verdict needs, and which ones are exposure with no payoff.
4. Fill in **TODO 1**, cell 9. Your `build_facts(parsed)` picks the facts worth sending out of the parsed email and returns them as one flat dictionary. That is 8 to 10 lines.
5. Run cell 10, the check cell. It runs your function on emails 005 and 016 and prints both results side by side. Fix your function until each fact you meant to send is there.
6. Fill in **TODO 2**, cell 11. Your `format_facts(facts)` walks `FACT_ORDER` and builds one labeled text block, using the label `FACT_LABELS` gives each key. That is 4 to 5 lines.
7. Run cell 12, the second check cell. It prints the finished facts block for email 016 and counts its characters. Read that count. Every call now carries it.
8. Read cell 13. It defines `build_grounded_prompt()`, `classify_grounded()` and `compare_runs()`. You do not write these. You call them.
9. Run cell 14. It runs all six emails both ways and prints the comparison table. **This is the cell you screenshot.**
10. Look at the rows for emails 019 and 016. Those two were built to move in opposite directions. Say what your own run did with them, whichever way it went. A row that did not move is a result, not a mistake.
11. Fix what breaks. Read the last line of any traceback first. It names the error type and the thing that failed.
12. Run cell 15, the export cell. It writes `week3_grounding.json` and prints the full path and the first few lines.
13. Open that file and read it. Every email carries both verdicts, both confidence numbers, and the exact facts block you sent.
:::

::: callout warning | Two things that stop this lab
Send the parser's values, not your own words. A fact you retype by hand is a fact you can get wrong, and the grader reads what is in the file.

Do not send everything the parser returns. Cell 12 prints the size of your block. Each line in it is a line you have disclosed.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 25 | All three items are present and readable. |
| Fact extraction | 25 | Every email in the file carries the facts block you sent. Each block holds the sender facts, the three check results, the display-name mismatch, the link hosts, the gateway values and any attachment name. It uses the shipped labels and the shipped order, and its values match the parser. |
| Verdict comparison | 25 | All six emails are in the file. Each one carries both verdicts, both confidence numbers, and a changed flag that agrees with them. The same six rows are readable in the screenshot. |
| Written answer | 25 | Three to five sentences. It names one fact you left out and why a sound verdict does not need it. It names the fact that moved a verdict, with the email id. |
| **Total** | **100** | |

No credit depends on which way a verdict moved. This lab scores the facts you chose and what you report, not the answers the model gave.

Nothing is graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, the cell that runs all six emails both ways. It has to show all six rows, each with the email id and both verdicts, plus the token line under them. Capture the whole output in one image. If the rows do not fit, lower your browser zoom and capture again.
2. **One file.** `week3_grounding.json`, attached as itself. Cell 15 prints its full path and its first few lines, so you can see exactly what you are attaching.
3. **A written answer**, typed into the submission box. Three to five sentences. Answer this:

    Name one fact you chose not to send to the model. Say why a sound verdict does not need it. Then name the one fact that changed a verdict in your run. Give the email id.

Do not screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 21, Sunday 11:59 PM Central.
:::
