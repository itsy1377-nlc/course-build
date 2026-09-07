::: intro
Week 5 is done. Your agent takes more than one step now, and your own code decides when it stops. Here's what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Bounded loop | A loop a rule and a cap can both end |
| Observe, decide, act | One step: read what you have, name one tool, run it |
| Stop condition | `decisive_stop()`, the rule that ends a run early |
| The five stop reasons | `decisive_malicious`, `decisive_benign`, `internal_sender`, `tools_exhausted`, `step_cap` |
| Step cap | `MAX_STEPS` is 4, and it catches the run no rule ended |
| Runaway loop | Every pass carries the whole history, so cost grows faster than the step count |

Two of those carry the week. The rule ends the run that has its answer. The cap ends the run that never gets one.
:::

::: did | What you did
- You rode a bus route in the sidebar, with a counter, a cap and an early stop.
- You read one pass of the loop written out flat, with every value printed.
- You wrote `run_loop()`, the one cell that was yours this week.
- You ran it on email 011 alone, then on all six emails.
- You ran one email again with the cap removed, and read both token totals.
- You exported `week5_loop_trace.json` and read the file you turned in.

That file holds the tool order, the step count and the stop reason for all six runs. A grader reads it without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer sits under its question, with where it comes from.

1. A trace shows one step, and the sender is inside Pellgrave. Which stop reason ended that run?

    `internal_sender`. The first result settled the case. From the stop condition is a rule in your code.

2. What makes a stop condition explicit?

    It's written in your code, not left to the model. `decisive_stop()` returns a reason, or nothing. From the stop condition is a rule in your code.

3. The model asks again for a tool it already ran. Why is the cap needed there?

    No rule ends that run, and the repeat still counts. At four steps `out_of_room()` returns `step_cap`. From the cap is a control, and a person owns it.

4. Email 004 has no link in it, and the reputation check is done. Which tool comes second?

    `lookup_recipient`, the one still with something to look at. `check_urls` comes back empty, and the step counts anyway. From a wrong second choice costs a step.

5. What does the token counter read, and what does it never measure?

    It reads the numbers each reply reports. It never measures the length of the answer text, and it never says whether a run learned anything. From the Week 5 lab notebook, the token counter cell.

6. The model answers instead of asking for a tool. What does your loop do?

    `first_call()` keeps the answer, then names the first tool the run hasn't used. The run carries on. From the Week 5 lab notebook, cell 9.
:::

::: next
Take the **Week 5 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 5 discussion** and reply to one classmate.

Week 6 stops trusting the text your agent reads. Somebody else wrote every email body. On a reported phish, that somebody is the attacker. Next week one of those bodies gives your agent orders, and you build the checks that catch it.
:::
