::: intro
Week 6 is done. The fence didn't stop the paragraph in email 013, and the grounding you kept held its twin. Which control did the work is the week.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Prompt injection | Attacker text the model reads as an order, not as evidence |
| Delimiter | `BODY_START` and `BODY_END`, the markers around the body |
| Data rather than instructions | The fenced block is evidence, never an order |
| Fact check | `check_against_facts()`, the answer read back against your facts |
| Confidence threshold | `CONFIDENCE_FLOOR` is 0.7, and a person decides below it |
| Per-run token cap | `TOKEN_CAP_PER_RUN` is 4000, counting only the tokens the model wrote across one triage. The whole run costs more, and no cap reads it |
| Hallucination | An indicator naming a host your facts never held |
| Data exposure | An answer carrying something that should not travel |
| Automation bias and overreliance | Two risks no code in your notebook catches |

Here's the split that carries the week. The fence asks the model to behave, and it can still read the block as an order. What held was code: your grounding, the hidden-HTML check, and the rule that sends a case to a person.
:::

::: did | What you did
- You checked a library account against the catalogue in the sidebar.
- You ran email 013 with no defenses, then its injection-free twin 024. Both are malicious.
- You wrote `build_guarded_prompt()`, which keeps your week 3 grounding and puts the body between two markers.
- You wrote `check_against_facts()`, which returns a sentence for every contradiction.
- You ran the guarded agent on the five other payload spots.
- You lowered the token cap and watched it end a run.
- You exported `week6_guardrails.json` and read the file you turned in.

That file holds both verdicts and both confidences for all eleven emails, plus the escalation reason and the fence record for 013. A grader reads it without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer names the reading section it comes from.

1. Why does the email body count as text an attacker wrote?

    Somebody else wrote it. On a reported phish, that somebody is the attacker. From the body is text an attacker wrote.

2. Email 014 hides its payload in the HTML part. Which control reaches it?

    It isn't the fence. Your facts side gets a count of the hidden characters, never the text. The check on that text escalates 014 and records `injection_detected`. From six places the payload can sit.

3. What does the fact check compare, and what does it do when they disagree?

    It reads the answer against facts you already pulled out. Each disagreement becomes a plain sentence in your export. From the four controls.

4. When does the confidence floor send a case to a person?

    When the confidence the model reports sits under 0.7. The floor reads the number, not the verdict word. Read both confidence numbers on your own rows and see which cases it caught. From overreliance.

5. What does the per-run token cap stop, and what does it not stop?

    It stops one triage that keeps spending. It does nothing about a wrong answer that comes cheap. In our testing no run came near the cap. From the four controls.

6. Email 023 asks for the recipient's report history in the answer. Which risk is that?

    Data exposure. Your schema names the four fields an answer may carry, and `schema_errors()` calls any other name a key that doesn't belong. It checks names, not content. From data exposure.
:::

::: next
Take the **Week 6 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 6 discussion** and reply to one classmate.

Week 7 asks what this week can't. Nothing yet says how often your agent is right. It reads twenty emails it has never seen, and you score every call.
:::
