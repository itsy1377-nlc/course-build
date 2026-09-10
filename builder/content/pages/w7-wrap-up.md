::: intro
Week 7 is done. Your agent writes its judgment down now, and you know how often that judgment is right.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Triage note | Six fixed lines another person can act on |
| Plain-language summary | Two sentences for the person who reported the email |
| Ground truth | The correct answer, written down before your agent ran |
| Accuracy | The share of the twenty your agent judged correctly |
| False positive and false negative | A benign email called malicious, and a malicious one called benign |
| No decision | A row where no verdict came back. Not a wrong answer |
| Escalation agreement | How often its yes or no matched the answer key |
| Use case | One job people give an AI tool |

Two of those carry the week. A judgment isn't a measurement. And the two error counts are never added together, because they cost different things.
:::

::: did | What you did
- You counted bakes in the sidebar, then divided for a rate.
- You wrote `write_note()`, which fills the six lines from one result.
- You ran the batch across all twenty emails.
- You wrote `score_batch()`, which counts correct calls, both errors, and the rows that never answered.
- You read the table of every email your agent got wrong, with the answer key beside it.
- You exported `week7_triage_report.txt` and read the file you turned in.

That file holds twenty notes, your score block, and what the run got wrong.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer names the reading section it comes from.

1. A tool reads a day of log lines and hands back the few worth a look. Which job is it, and what does it need first?

    Log review. It needs those lines, and what normal looks like there. From three jobs that sort what already arrived.

2. A tool turns facts already on a ticket into a written note. Which job is it, and who reads it first?

    Documentation. The ticket owner reads the draft before anyone files it. From two jobs where the tool writes a draft.

3. Your report lists a benign email your agent called malicious. Which error is that, and what does it cost?

    A false positive. An analyst loses a morning on a message that was fine. Enough of those and he stops believing the agent. From the two errors, and what each one costs.

4. Your counts are two false positives and one false negative. Why not report three wrong?

    Three wrong tells the reader nothing. Two of one and one of the other is a different problem. From the two errors, and what each one costs.

5. A note reads verdict, confidence, indicators, escalate, summary. Which line is missing, and where does it belong?

    Recommended action, between the indicators and the escalate line. From why the six lines never move.

6. Why does escalation agreement get a line of its own?

    It asks a different question. Accuracy asks whether the verdict was right. This asks whether the right cases reached a person. From one score block.
:::

::: section | Would a bigger model have done better?
Yes. We ran your twenty emails on `granite-8b` three times, beside three runs of your `granite-3b`.

| Over three runs | 3B | 8B |
|---|---|---|
| Correct, of 60 | 34 | 48 |
| Accuracy | 0.567 | 0.800 |
| False positives | 26 | 11 |
| False negatives | 0 | 0 |

Twice the price, fourteen more calls right. Neither missed a single attack. Both spent every error on mail that was fine.

Size paid here, behind your facts block and your tools. Knowing that is worth more than a better score. You measured a system, found where it fails, and can say what a better one buys.
:::

::: next
Take the **Week 7 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 7 discussion** and reply to one classmate. Both ask for numbers from your own report.

Week 8 is the final exam and nothing else. No new reading, no new lab, no new video. Forty questions worth 30 points, one attempt, due Day 56. Your notebooks are the study guide.
:::
