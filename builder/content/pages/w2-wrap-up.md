::: intro
Week 2 is done. Your agent now answers in a fixed shape, and your code checks that shape before it trusts the answer. Here's what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Structured output | You ask for named values, not a paragraph |
| JSON as text | A reply is characters until `json.loads()` opens it |
| Schema | One rule supplies both the prompt limits and the check |
| Reporting limit | Week 2 accepts confidence from 0 to 0.9 without claiming the number is calibrated |
| Malformed output | A normal condition to handle, not a rare bug |
| Retry | Asking again, with the reported problems added to the prompt |

Three distinctions carry the week. Loading isn't checking. Accepted isn't the same as accurate. And a retry needs new information, not merely another paid call.
:::

::: did | What you did
- You wrote `extract_json()`, which cleans and loads model text.
- You tested it against four saved replies, one clean and three broken.
- You wrote `classify_email()` with an accepted-answer sentinel and a cap.
- You ran a saved contract test that forced four schema problems into prompt 2.
- You classified four emails and recorded every live try, good or bad.
- You checked every result for `schema_ok: true`.
- You exported `week2_classification.json` and read the file you turned in.

The saved test proves your code took the retry path. The live rows show what this model did on your run. Neither a passing schema nor a lower reported confidence proves the judgment is correct.
:::

::: checkpoint | Check yourself
Answer these five before you move on. The answer sits under each one.

1. Your code loads a reply with no error. Is the answer ready to accept?

    Not yet. Loading proves the text is JSON. The schema check decides whether it fits the contract. Even then, the verdict can still be wrong.

2. What are the four names the course schema requires?

    `verdict`, `category`, `confidence` and `indicators`.

3. The reply is empty and the stop reason is `length`. What do you know?

    The model reached the answer limit before usable JSON arrived. Record the failed try and send the common JSON recovery action. The stop reason alone doesn't prove what the model wrote before the answer.

4. Your first try reports confidence 0.95. What must prompt 2 carry?

    The exact problem from the check: confidence is 0.95, and it has to be from 0.0 to 0.9. That's a reporting correction, not proof that the model became less sure.

5. All three tries failed. What does your function hand back?

    `None`, with the failures recorded. Nothing downstream treats that as a verdict, because the email is unanswered rather than benign.
:::

::: next
Take the **Week 2 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 2 discussion** and reply to one classmate.

Week 3 changes what you send. Right now your agent sends the whole email body and hopes. Next week it sends the facts instead: who really sent the message, whether the checks on the sender passed, and where the links actually point. Those facts are what make a verdict worth trusting.
:::
