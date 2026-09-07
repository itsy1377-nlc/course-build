::: intro
Week 2 is done. Your agent now answers in a fixed shape, and your code checks that shape before it trusts the answer. Here is what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Structured output | You ask for named values, not a paragraph |
| JSON as text | A reply is characters until `json.loads()` opens it |
| Schema | The written rule for which names and which values are allowed |
| Malformed output | A normal condition to handle, not a rare bug |
| Stop reason | The label saying why the model stopped writing |
| Reasoning block | Text the model writes to itself, stripped before the load |
| Retry | Asking again, with the reported problems added to the prompt |

Two of those carry the whole week. Loading is not checking. And a retry that sends the same request twice is a retry you paid for and learned nothing from.
:::

::: did | What you did
- You read a raw reply and saw what the model actually sends back.
- You wrote `extract_json()`, which strips the reasoning block and loads the text.
- You ran it against four saved replies, one clean and three broken.
- You wrote `classify_email()`, your first loop with a cap on it.
- You classified four emails and recorded every try, good or bad.
- You exported `week2_classification.json` and read the file you turned in.

That file holds the check result on every try, including the ones that passed first time. That is the evidence a grader reads without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these five before you move on. The answer sits under each one.

1. Your code loads a reply with no error. Is the answer safe to use?

    Not yet. The load only proved the text is JSON. The schema check is what says the answer is usable.

2. What are the four names the course schema requires?

    `verdict`, `category`, `confidence` and `indicators`.

3. The reply is empty and the stop reason is `length`. What happened?

    The model hit the token limit before it wrote the answer. Usually it spent the budget on a reasoning block.

4. Your first try failed. What must the second prompt carry?

    The problems your check reported, in plain words. Without them you are sending the same request again.

5. All three tries failed. What does your function hand back?

    `None`, with the failures recorded. Nothing downstream treats that as a verdict, because the email is unanswered rather than benign.
:::

::: next
Take the **Week 2 self-check** if you have not yet. It is 12 points, unlimited tries, and the highest score counts.

Post to the **Week 2 discussion** and reply to one classmate.

Week 3 changes what you send. Right now your agent sends the whole email body and hopes. Next week it sends the facts instead: who really sent the message, whether the checks on the sender passed, and where the links actually point. Those facts are what make a verdict worth trusting.
:::
