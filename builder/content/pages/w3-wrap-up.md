::: intro
Week 3 is done. Your agent now sends facts about the message, not the message alone. Here's what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Grounding | Facts about a message, sent instead of the message alone |
| Facts block | A short labeled list, printed in one fixed order |
| Header | A named line above the body, such as `From:` |
| SPF, DKIM and DMARC | Three checks your gateway ran and wrote down |
| Display-name mismatch | A name from one domain over an address at another |
| Link host | The part of a web address that decides where a click lands |
| Known-good domains and the playbook | Your organization's own hosts, and the rules it triages by |
| Data minimization | Sending only what the decision needs |

Two of those carry the week. A passed check is one answered question, not a clean message. And every line you send is a line you've handed to an outside service.
:::

::: did | What you did
- You printed every key the parser returns, and chose from that list.
- You wrote `build_facts()`, which picks the facts a verdict needs.
- You wrote `format_facts()`, which prints them as labeled lines in a set order.
- You ran six emails twice, on the body alone and then with your facts.
- You compared each email's two indicator lists, and read what the facts changed.
- You exported `week3_grounding.json` and read the file you turned in.

That file holds the facts block you sent for each email, beside both verdicts. A grader reads your choices without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these seven before you move on. Each answer sits under its question, with the reading section it comes from.

1. Which belongs in the facts block: the link hosts, or the reporter's address?

    The link hosts. The reporter's address moves no verdict and names a real person. From what you leave out is also a decision.

2. A message claims your own domain and fails DMARC. What does that say?

    It didn't come from the domain it names. That's a fact to send, not a verdict. From what a passed check really means.

3. A link host is on no list you hold. Is it clean?

    No. It's unknown, which is a different answer. Week 4 gives your agent a way to look one up. From where the links point.

4. Why does mail sent inside the company carry no check results?

    Your gateway checks what arrives from outside. Nothing ran, so nothing was written down. Missing isn't failed. From what a passed check really means.

5. Your verdict on an email is the same before and after the facts block. How can you tell whether the model used the facts at all?

    Compare the two indicator lists. The grounded run usually names things the body alone could not, such as the check results or the link host. No difference is still a result. From what the facts block can and can't do.

6. One of your rows did change verdict. Does that mean the facts made it right?

    No. Whether it moved toward the truth is a separate question, and week 7 is where you measure that. A row that changed for the wrong reason looks exactly like one that changed for the right one.

7. You've a log line instead of an email. What changes?

    The field names. You still drop what no judgment needs and send the rest in one steady shape. From the same move on a log line.
:::

::: next
Take the **Week 3 self-check** if you haven't yet. It's 12 points, unlimited tries, and the highest score counts.

Post to the **Week 3 discussion** and reply to one classmate.

Week 4 lets the model ask for a fact you didn't send. It names what it wants, and your code goes and gets it. You write the part that runs it.
:::
