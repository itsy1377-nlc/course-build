::: intro
This week your agent stops trusting the text it reads and the answer it writes. You run eleven emails twice, once with no defenses and once guarded, and then you judge what the guardrails bought you.

Twelve to sixteen lines of your own code, in two clearly marked TODO cells. Everything else in the notebook is written for you. Read both parts of the **Week 6 reading** first and run the **Week 6 sidebar notebook**. Plan about three hours.

Your week 5 loop doesn't have to be finished. Cell 5 carries a working version of everything through week 5, and the cells after it use that one.
:::

::: directions
1. Open the **Week 6 lab notebook**. Run every cell from the top, in order. Stop when you reach the first TODO cell.
2. Read the output of cells 6 and 7. They run your week 5 agent on email 013 and on email 024 with no defenses, and print both verdicts together. Email 024 is 013 word for word without the planted paragraph.
3. Read cell 9. It gives you `BODY_START`, `BODY_END` and `GUARD_RULES`. You don't write these. You use them.
4. Fill in **TODO 1**, cell 10. Your `build_guarded_prompt(facts_text, body)` puts the rules first, wraps the body between the two markers, and puts the required answer names last. Hidden HTML text stays on the facts side. That's 6 to 8 lines.
5. Run cell 11, the check cell. It prints your finished prompt for email 013, then runs 013 and 024 again with it. Look for both markers sitting around the body.
6. Run cell 12. It runs the guarded agent on 014, 020, 021, 022 and 023, and prints where the fence doesn't reach. Read cell 13 next.
7. Fill in **TODO 2**, cell 14. Your `check_against_facts(result, facts)` returns problems in plain words, and an empty list when it finds none. It catches three contradictions. Two are a benign verdict over a blocklisted link host or a known bad sender. The third is an indicator naming a host your facts never held. That's 6 to 8 lines.
8. Read cell 15. It defines `CONFIDENCE_FLOOR`, `TOKEN_CAP_PER_RUN`, `over_token_cap()`, `guarded_triage()` and `compare_guarded()`. You call these. You don't write them.
9. Run cell 16, the comparison cell. It runs all eleven emails both ways, prints one row each, and prints a token line under the table. **This is the cell you screenshot.**
10. Fix what breaks. Read the last line of any traceback first. It names the error type and the thing that failed.
11. Run cell 17. It lowers the token cap on purpose so you watch the cap fire. A normal run here spends far less than 4000.
12. Run cell 18, the export cell. It writes `week6_guardrails.json` and prints the full path.
13. Open that file and read it. Check that all eleven emails have a row, that five rows read `none` for placement, and that the fence record for email 013 is there.
:::

::: callout warning | Two things that stop this lab
The markers go around the body and nothing else. Wrap your facts block inside them and you've told the model your own facts are the attacker's text.

`check_against_facts()` hands back a list. An empty list means it found nothing wrong. Return `True` or `None` instead and `guarded_triage()` can't read it.
:::

::: grading | Grading Criteria
| Criterion | Points | What earns full credit |
|---|---|---|
| Submission completeness | 8 | All three items are present and readable. |
| Guardrail judgment | 72 | Your written answer reaches a clear judgment, supports it with your own before and after numbers, and names one case that still gets through and the payload spot behind it. |
| Guarded run completeness | 20 | The file holds a row for all eleven emails. Each row carries a verdict on both paths, an escalation reason and a token count. Placement is named where the email has one and reads `none` where it does not. The fence record for email 013 is present. |
| **Total** | **100** | |

Nothing here's graded by running your notebook. The three items you turn in carry all of it.
:::

::: submit
Three items. Nothing else. No zip file, no folder, no link to a repository.

1. **A screenshot.** One image of the output of cell 16, the comparison cell. It has to show the header row, all eleven email rows including the row for 015, and the token line printed under the table. Don't crop a row. If the table doesn't fit, lower your browser zoom and capture again.
2. **One file.** `week6_guardrails.json`, attached as itself. Cell 18 prints its full path, so you can see exactly what you're attaching. Don't rename it, and don't attach the notebook.
3. **A written answer**, typed into the submission box. Answer this:

    In 3 to 5 sentences, answer this. Your guardrails changed how your agent handled email 013. Did they cut prompt injection risk enough for a real security team? Name one number from your own file that backs your answer. Then name one case your guardrails still miss.

Don't screenshot the configuration cell. Your key is pasted into it, so a picture of that cell shows your key to anyone who sees it. Screenshot only the cell this assignment names. If your key does end up in a post or an image, tell your instructor so it can be replaced.

Due day 42, Sunday 11:59 PM Central.
:::
