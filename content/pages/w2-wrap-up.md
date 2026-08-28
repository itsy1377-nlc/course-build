::: learned
- A function is a named block of steps. A loop repeats steps once per item. A
  conditional picks between two paths.
- A chat completions request is one JSON object with four fields that matter:
  `model`, `messages`, `temperature`, and `max_tokens`.
- The messages list carries every role in one box. The role is a label on the
  text, not a wall around it.
- The model's text lives at `response["choices"][0]["message"]["content"]`.
- A tool call's arguments arrive as a **string** of JSON. You call `json.loads`
  on it before you can look anything up.
- Some HTTP errors clear on their own and some never will. Retrying the second
  kind wastes your quota and cannot succeed.
- Every package version is pinned, because installing a package runs somebody
  else's code on your computer.
:::

::: did
- Read a real function from the lab code and named its loop, its conditional,
  and its return values.
- Read the Requests Quickstart and the chat completions reference.
- Got an API key, set up your `.env` file, and set your student ID.
- Ran `python verify_env.py --live` and submitted the second gate code.
- Wrote `should_retry`, `backoff_seconds`, and `parse_json_content` in
  `agent/llm.py`.
- Checked your own work with pytest, as many times as you wanted, before the
  deadline.
- Took the Module 1 comprehension quiz.
:::

::: checkpoint
Answer these before Week 3 opens.

1. Your request returns HTTP 429. Your code waits and sends it again. Now it
   returns HTTP 400. Should it wait and send it again? Why not?
2. Your backoff waits half a second every time, forever. Name the problem with
   that.
3. `parse_json_content` gets the text `["a", "b"]`. That is valid JSON. Why does
   your function still reject it?
4. Write the chain of keys from the top of a reply down to a tool call's
   arguments. Then say what type you are holding at the end.
5. You copied a working request from a blog post and it fails against your
   provider. Name one thing worth checking first.

**Answers:**

1. No. A 400 means the request itself is wrong, so sending it again gives the
   same answer and spends your quota.
2. It never gives a rate limit time to clear, and it never stops. Waits have
   to grow, and growth needs a ceiling.
3. Your caller needs a dictionary to look keys up in. A list parses fine and
   has no keys, so it is valid JSON of the wrong shape.
4. `response["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]`.
   You are holding a string, so `json.loads` comes next.
5. The model name. Providers name their models differently, so a name yours
   does not have fails before anything else is even read.
:::

::: next
Week 3 turns everything around.

Until now, your script calls the model and waits. Next week the model calls your
functions. You give it a list of tools, it picks one, and your code runs it.

That inversion is the hardest idea in this course, and Week 3 is built entirely
around it. You get an annotated, line by line read of the agent skeleton, and
the graded work is a pass or fail checkpoint rather than a project.

You also learn what a JSON tool schema is. The short version: the description
you write in a schema is read by the model, not by a person. That makes it an
interface, and it makes it an attack surface.
:::
