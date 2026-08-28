::: learned
- Your script used to call the model. Now the model asks your code to run a
  function. That flip is called the inversion, and it is what makes an agent an
  agent.
- The model cannot run anything. It produces text. Your code decides whether to
  act on it.
- A JSON tool schema is an interface, not documentation. It is the only thing
  the model ever knows about a tool.
- A tool call's arguments arrive as a string, and `json.loads` turns that string
  into data your program can use.
- Every call that leaves your program needs three things: a `try`, a timeout,
  and a rule about when a retry is worth it.
- A tool that fails loudly is working. A tool that fails quietly is broken.
- `before_tool_call` runs after the model asks and before the tool acts. That is
  the last moment anything can be stopped.
:::

::: did
- Compared the Week 2 shape with the Week 3 shape and named what changed.
- Read a real JSON tool schema and identified its four working parts.
- Applied try, except, a timeout, and a retry rule to code in the scaffold.
- Read `agent/loop.py` end to end with the file open, in 45 minutes.
- Got at least one tool call to run and land in `runs/ledger.jsonl`.
- Submitted the Project 1 checkpoint, on your own run or on the fallback branch.
:::

::: checkpoint
Answer these for yourself before Week 4 opens. They are the shape of the quiz
questions coming up.

1. Your agent called `send_email`. Who chose the recipient address, and where
   did that address come from?
2. You add a tool and forget to put its name in `agent.allowed_tools`. The model
   never calls it. Why not?
3. The model sends `{"customer_id": 1002}` and your function expects a string.
   Which part of your work was wrong, the Python or the schema?
4. Name the one place in `agent/loop.py` where a tool call can still be stopped.
:::

::: next
Week 4 takes the loop apart, one step at a time. You will trace it on paper
before you write any code, because the paper version is what makes the code
readable.

Then you build. You finish `get_customer`, and you design a tool of your own
with a schema you write yourself. That is Project 1.

One thing to carry forward. The tool you add next week will have no check on
who is allowed to call it. That is on purpose, and you will find it yourself in
Week 6, in your own code.
:::
