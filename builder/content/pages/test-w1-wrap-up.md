::: intro
You made your first model call this week. Here's what you covered, what you did, and where each piece turns up next.
:::

::: learned | What you learned
| Idea | Where the course uses it next |
|---|---|
| The ten parts of a security operations center | Week 6, week 7 and the final exam |
| Where your agent sits, between an alert and a ticket | Week 6 and week 7 |
| Scoring AI, generative AI and agentic workflows | The final exam |
| A model call: a prompt goes out, an answer comes back | Every week |
| Temperature, and why the same prompt gives different answers | Every later call, held at the steady 0.2 setting |
| A token count read from the reply, not from the answer text | Week 6 |

One sentence carries this whole course: an agent is a loop around a model call. This week you wrote the call, and week 5 adds the loop.
:::

::: did | What you did
- You wrote `ask_model()` and sent a prompt from your own code.
- You sent one phishing email and one ordinary internal notice.
- You ran one prompt six times, three at temperature 0.2 and three at 1.0.
- You watched the token count rise with the length of the mail.
- You exported `week1_first_calls.txt` and turned it in.
:::

::: checkpoint | Check yourself
Answer these five without looking anything up. The answers are right below them, so cover them first.

1. What does a low temperature do to your answers?
2. Where does the running token count come from?
3. A report lands in the phishing mailbox. What does your agent do with it, and what does it never do?
4. A tool reads a ticket, checks the account, resets a password and closes the ticket. Which of the three kinds of AI is that?
5. Name one thing to check before you trust the model's answer in a real ticket.

**Answers.**

1. It makes them steadier. The same prompt comes back more alike each time you run it.
2. From the usage numbers in the model's reply, and never from the length of the answer text.
3. It reads the facts behind the alert and drafts the note for the ticket. It never closes the ticket, and it never decides that something is an incident. A person does both.
4. An agentic workflow. It picks its own next step and then acts, inside set limits.
5. Any one of these counts. The sender's domain. Where the link really goes. Whether the answer changed when you ran it again. Whether the answer names something the email never said.
:::

::: next
Week 2 makes the answer strict. Right now the model writes you a sentence, and a sentence is hard for code to use. Next week it hands back the same fields every time, in a shape your code can check. You'll write that check yourself, and you decide what happens when the shape comes back wrong.

Before you start, make sure your `ask_model()` still runs. If it doesn't, open the week 2 starter notebook anyway. It carries a working version of everything from this week, so you're never stuck behind last week's code.
:::
