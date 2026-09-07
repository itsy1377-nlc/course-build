::: intro
Week 6 is done. Your agent treats the email body as evidence now, and it hands the doubtful cases to a person. Here is what you covered and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Prompt injection | Attacker text the model reads as an order, not as evidence |
| Delimiter | `BODY_START` and `BODY_END`, the markers around the body |
| Data rather than instructions | The fenced block is evidence, never an order |
| Fact check | `check_against_facts()`, the answer read back against your facts |
| Confidence threshold | `CONFIDENCE_FLOOR` is 0.7, and a person decides below it |
| Per-run token cap | `TOKEN_CAP_PER_RUN` is 4000 tokens for one triage |
| Hallucination | An indicator naming a host your facts never held |
| Data exposure | An answer carrying something that should not travel |
| Automation bias and overreliance | Two risks no code in your notebook catches |

Two of those carry the week. The fence is the defense. The fact check is the control on it, because it reads your tool results, not the body.
:::

::: did | What you did
- You checked a library account against the catalogue in the sidebar.
- You ran email 013 and its clean twin 024 with no defenses.
- You wrote `build_guarded_prompt()`, which puts the body between two markers.
- You wrote `check_against_facts()`, which returns a sentence for every contradiction.
- You ran the guarded agent on the five other payload spots.
- You lowered the token cap and watched it end a run.
- You exported `week6_guardrails.json` and read the file you turned in.

That file holds both verdicts for all eleven emails, plus the escalation reason and the fence record for 013. A grader reads it without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer names the reading section it comes from.

1. Why does the email body count as text an attacker wrote?

    Somebody else wrote it. On a reported phish, that somebody is the attacker. From the body is text an attacker wrote.

2. Email 014 hides its payload in the HTML part. Which control reaches it?

    The fence. `build_guarded_prompt()` keeps hidden HTML text on the facts side, so it arrives as something the message did. From the four controls.

3. What does the fact check compare, and what does it do when they disagree?

    It reads the answer against facts you already pulled out. Each disagreement becomes a plain sentence in your export. From the four controls.

4. When does the confidence floor send a case to a person?

    When the reported number sits under 0.7. Emails 009 and 012 land there. Email 009 asks for nothing but a reply, and no tool result is decisive on 012. From overreliance.

5. What does the per-run token cap stop, and what does it not stop?

    It stops one triage that keeps spending. That run records `step_cap` for the reason `token_cap`. It never touches the course token budget. From the four controls.

6. Email 023 asks for the recipient's report history in the answer. Which risk is that?

    Data exposure. Your schema names the four fields an answer may carry, and `schema_errors()` calls any other name a key that does not belong. From data exposure.
:::

::: next
Take the **Week 6 self-check** if you have not yet. It is 12 points, unlimited tries, and the highest score counts.

Post to the **Week 6 discussion** and reply to one classmate. It asks for the rule your guardrails were missing, and what it costs you on email 015.

Week 7 asks what this week cannot. Nothing yet says how often your agent is right. Next week it writes each judgment in a fixed shape. It reads twenty emails it has never seen, and you score every call.
:::
