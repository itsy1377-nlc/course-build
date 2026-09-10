::: intro
This week your agent writes its judgment down, and you find out how often it's right. It reads twenty emails, writes a six-line note for each, and you score all twenty against the answer key.

Sixteen to twenty lines of your own code, in two clearly marked TODO cells. Everything else is written for you. Read the **Week 7 reading** first and run the **Week 7 sidebar notebook**. Plan about two and three quarter hours.

Your week 6 agent doesn't have to be finished. Cell 5 carries a working version of everything through week 6, and the cells after it use it.
:::

::: directions
1. Open the **Week 7 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read cell 6. It prints the note template and one finished note. Your six lines have to match it, label for label and line for line.
3. Fill in **TODO 1**, cell 8. Your `write_note(result, facts)` returns the six lines as one triple-quoted f-string, built from one triage result, with the indicator list joined into one line. That's 5 to 7 lines.
4. Run cell 9, the check cell. It runs one email end to end and prints its note. Compare it with the example in cell 6 until the labels and the order match.
5. Read cell 10. It defines `BATCH_DIR`, `GROUND_TRUTH`, `list_batch_emails()` and `run_batch()`. You call these, you don't write them.
6. Run cell 11. It runs all twenty emails, printing one line each with the running token total. Under two minutes. Let it finish.
7. Read cell 12. It says what each kind of error costs a small security team.
8. Fill in **TODO 2**, cell 13. Your `score_batch(rows, truth)` loops over the rows. It counts correct verdicts, both errors, and rows with no verdict, then returns those with the accuracy rate. That's 11 to 13 lines.
9. Run cell 14. It prints your score report. Accuracy, both errors, no decision and escalation agreement each get a line. Escalation agreement is how often your Escalate line matched the key. **This is the cell you screenshot.**
10. Fix what breaks. Read the last line of any traceback first. It names the error and what failed.
11. Run cell 15. It lists every email your agent got wrong, with the answer key beside it. Pick one for your written answer.
12. Run cell 16, the export cell. It writes `week7_triage_report.txt` and prints its full path.
13. Open that file and read it. Check that all twenty notes carry the six lines in order, that the score block holds your counts, and that the last section names what went wrong.
:::

::: callout warning | Two things that stop this lab
Your note is one f-string that you write, not a fill of `NOTE_TEMPLATE`. The template is printed so you can read it beside your own six lines.

Keep the counts apart. A false positive and a false negative cost different things. A row with no verdict is neither: the model didn't answer at all. Test for it first, or your report calls the model wrong when it was silent.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 8 | All three items are present and readable. |
| Triage note | 36 | All six lines are present, in order, for all twenty emails, built by your own f-string. Your written answer audits one of those notes: it names a line a next-shift analyst couldn't act on, and writes that line as it should read. |
| Accuracy and human review | 56 | Your accuracy number matches the file you attached. The two errors are counted apart, with no-verdict rows in neither. Escalation agreement has its own line. Your written answer names where a human must still review, and cites your own accuracy figure and one email of your own. |
| **Total** | **100** | |

The answer key ships inside your notebook, and no points come from a correct verdict. This lab grades the note format you built and the honesty of your numbers.

Nothing here is graded by running your notebook.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 14, the score report. Capture that cell's output top to bottom, with every number readable. If it doesn't fit, lower your browser zoom and capture again.
2. **One file.** `week7_triage_report.txt`, attached as itself. Cell 16 prints its full path and its first few lines.
3. **A written answer**, typed into the submission box. Five to seven sentences. Answer this:

    Which error is worse for a one-person security team, a false positive or a false negative? Use your own counts. Name one email your agent got wrong, or the one it was least sure about. Read that email's note: name one line a next-shift analyst couldn't act on, and write it as it should read. Say where you'd keep a human analyst in the loop, and why.

Don't screenshot the configuration cell. Your key is pasted into it, so a picture of it shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key ends up in a post or an image, tell your instructor so it can be replaced.

Due day 49, Sunday 11:59 PM Central.

New to screenshots? **Using the notebook server** shows how to take one on
Windows, Mac, Chromebook and Linux, and the four ways one loses points.
:::
