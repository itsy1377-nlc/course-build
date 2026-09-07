::: intro
Week 7 is done. Your agent writes its judgment down now, and you know how often that judgment is right. Here's what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Triage note | Six fixed lines another person can act on |
| Plain-language summary | Two sentences for the person who reported the email |
| Ground truth | The correct answer, written down before your agent ran |
| Accuracy | The share of the twenty your agent judged correctly |
| False positive and false negative | A benign email called malicious, and a malicious one called benign |
| Escalation agreement | How often its yes or no matched the answer key |
| Use case | One job people give an AI tool |

Two of those carry the week. A judgment isn't a measurement. And the two error counts are never added together, because they cost different things.
:::

::: did | What you did
- You counted bakes in the sidebar, then divided for a rate.
- You wrote `write_note()`, which fills the six lines from one triage result.
- You ran the batch across all twenty emails and watched the token total climb.
- You wrote `score_batch()`, which counts correct calls and both kinds of error.
- You read the table of every email your agent got wrong, with the answer key beside it.
- You exported `week7_triage_report.txt` and read the file you turned in.

That file holds twenty notes and your score block. A grader reads both without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer sits under its question, with the reading section it comes from.

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
We ran the same batch on `granite-8b`, at about three times the cost. It scored a little worse than 3B on our run. One run is one sample, so yours will differ.

It wins on a bare body. Behind your facts block and tools, it doesn't. Size pays for judgement on thin evidence. You spent four weeks making it good.
:::

::: next
Take the **Week 7 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 7 discussion** and reply to one classmate. Both parts ask for numbers out of your own report.

Week 8 is the final exam and nothing else. No new reading, no new lab, no new video. Forty questions worth 30 points, one attempt, due Day 55. It asks about all seven weeks, so your notebooks are the study guide.
:::
