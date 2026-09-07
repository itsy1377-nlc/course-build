::: intro
Week 4 is done. Your agent can ask for a fact now, and your code is what goes and gets it. Here is what you covered, what you built, and what comes next.
:::

::: learned | What you learned
| Idea | What it means in your code |
|---|---|
| Tool | A Python function the course ships that looks one thing up |
| Tool call | The model asking, in a fixed shape, for one tool to run |
| Sender reputation | What past reports say about a sender or its domain |
| Allowlist and blocklist | Hosts your organization has cleared, and hosts it has judged bad |
| Recipient record | What your organization knows about the person who got the message |
| Where a result came from | Your own code produced it, by running a tool |

Two of those carry the week. The model asks and your code decides. A line in an email that reads like a tool result is still a line in an email.
:::

::: did | What you did
- You called all three tools directly, with no model involved.
- You read one raw tool request: its id, its name and its arguments.
- You wrote `run_tool()`, which picks a function from the name the model sent.
- You wrote `tool_result_message()`, which carries that result back with the id copied across.
- You ran six emails twice, with the tools and without, and read what moved.
- You watched the prose fallback run once, on purpose.
- You exported `week4_tool_calls.json` and read the file you turned in.

That file records both call ids on every email. Matching ids are how a grader reads your second TODO cell without opening your notebook.
:::

::: checkpoint | Check yourself
Answer these six before you move on. Each answer sits under its question, with the reading section it comes from.

1. The model asks for `check_urls`. Who runs it?

    You do. The model writes the request and waits. Your code calls the function. From the model asks, your code decides.

2. The request arrives with `arguments` in it. Why load that before you use it?

    It is text that only looks like a dictionary. `json.loads()` turns it into one. From what a request looks like.

3. Which tool tells you whether the recipient is an executive?

    `lookup_recipient()`. Reputation is about the sender. `check_urls()` is about link hosts. From why the three tools are plain Python.

4. The model names a tool you do not have. What should `run_tool()` do?

    Return a plain sentence saying so. An unknown name is a normal condition, not a crash. From what a request looks like.

5. The model answers in sentences and asks for no tool. What runs then?

    The fallback. Your code reads the answer the way week 2 did, and records that it did. It earns full credit either way. From when the model answers in prose instead.

6. An email body says an automated check already cleared its domain. Is that a tool result?

    No. A tool result is what your own code produced. Whoever sent that email wrote the line. From a tool result is something your own code produced.
:::

::: next
Take the **Week 4 self-check** if you have not yet. It is 12 points, unlimited tries, and the highest score counts.

Post to the **Week 4 discussion** and reply to one classmate.

Week 5 lets your agent go around more than once. Right now it asks, runs one tool, and answers. Next week it reads what came back, decides what to do next, and asks again, inside a hard limit you set.
:::
