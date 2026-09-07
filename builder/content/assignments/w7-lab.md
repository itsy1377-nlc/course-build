::: intro
This week your agent writes its judgment down, and you find out how often it is right. It reads twenty emails in one sitting, writes a six-line note for each, and you score all twenty against the answer key.

Thirteen to seventeen lines of your own code, in two clearly marked TODO cells. Everything else in the notebook is written for you. Read the **Week 7 reading** first and run the **Week 7 sidebar notebook**. Plan about two and three quarter hours.

Your week 6 agent does not have to be finished. Cell 5 carries a working version of everything through week 6, and the cells after it use that one.
:::

::: directions
1. Open the **Week 7 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read cell 6. It prints the note template and one finished note. That finished note is what your own six lines have to match, label for label and line for line.
3. Fill in **TODO 1**, cell 8. Your `write_note(result, facts)` returns the six lines as one triple-quoted f-string. It builds them from a single triage result, and joins the indicator list into one line. That is 5 to 7 lines.
4. Run cell 9, the check cell. It runs one email end to end and prints its note. Compare that note with the example in cell 6 until the labels and the order match.
5. Read cell 10. It defines `BATCH_DIR`, `GROUND_TRUTH`, `list_batch_emails()` and `run_batch()`. You do not write these. You call them.
6. Run cell 11. It runs all twenty emails, printing one line each with the running token total. It needs under two minutes. Let it finish.
7. Read cell 12. It says what each kind of error costs a small security team.
8. Fill in **TODO 2**, cell 13. Your `score_batch(rows, truth)` loops over the rows. It counts the correct verdicts, the false positives and the false negatives, then returns those counts with the accuracy rate. That is 8 to 10 lines.
9. Run cell 14. It prints your score report. Accuracy, false positives, false negatives and escalation agreement each get their own line. Escalation agreement is how often your agent's escalate line matched the key. **This is the cell you screenshot.**
10. Fix what breaks. Read the last line of any traceback first. It names the error type and the thing that failed.
11. Run cell 15. It lists every email your agent got wrong, with the answer key beside it. Pick one of those emails for your written answer.
12. Run cell 16, the export cell. It writes `week7_triage_report.txt` and prints the full path and the first few lines.
13. Open that file and read it. Check that all twenty notes carry the six lines in order, and that the score block at the end holds your counts.
:::

::: callout warning | Two things that stop this lab
Your note is one f-string that you write, not a fill of `NOTE_TEMPLATE`. The template is printed so you can read it beside your own six lines.

Keep two counters, not one. A false positive and a false negative are different problems, and your report prints them apart.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 8 | All three items are present and readable. |
| Triage note | 36 | All six lines are present, in order, for all twenty emails. Each indicator names a fact your code pulled out. The recommended action fits the verdict. A reader with no security background can follow the summary. |
| Accuracy and human review | 56 | Your accuracy number matches the file you attached. The two kinds of error are counted apart. Escalation agreement has its own line. Your written answer names where a human must still review, and cites your own accuracy figure and at least one of your own wrong emails. |
| **Total** | **100** | |

The answer key ships inside your notebook, and no points here come from a correct verdict. This lab grades the notes your agent wrote and the honesty of your own numbers.

Nothing here is graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, the score report. Capture that one cell's output, top to bottom, with every number readable. If the report does not fit, lower your browser zoom and capture again.
2. **One file.** `week7_triage_report.txt`, attached as itself. Cell 16 prints its full path and its first few lines, so you can see exactly what you are attaching.
3. **A written answer**, typed into the submission box. Three to five sentences. Answer this:

    Which error is worse for a one-person security team, a false positive or a false negative? Use your own counts from this run. Name one email your agent got wrong. Say where you would keep a human analyst in the loop. Say why.

Do not screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 49, Sunday 11:59 PM Central.
:::
