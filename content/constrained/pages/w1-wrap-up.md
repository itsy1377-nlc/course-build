::: learned | What You Learned
1. An agent is a model plus a tool list plus a loop that runs the tools.
2. The model chooses tools by reading the descriptions you wrote.
3. A tool's output goes back into the model's next input.
4. The trace is the evidence. What the agent says about itself is not.
5. Some actions cannot be undone, and those are the ones that matter most.
:::

::: did | What You Did
1. Passed the scope and safety gate.
2. Set up Python and a local model on your own computer.
3. Sent the supplied request and recorded what came back.
4. Read your own trace and found the line for each tool call.
5. Listed every tool your agent can reach and marked the irreversible ones.
:::

::: checkpoint | Check Yourself
1. You ran the same request twice and got two different runs. Is your setup
   broken?
2. Where in the loop does text written by somebody else reach the model?
3. Your tool list has `read_ticket`, `send_email`, and `delete_customer`. Which
   are irreversible?
4. A classmate writes: "the agent confirmed it did not send anything." What is
   wrong with that sentence?
5. You want to test an attack on a public chatbot to compare. May you?

Answers:

1. No. Models vary between runs. That is why this course never draws a
   conclusion from one run.
2. Step 4, when a tool result is added to the conversation.
3. `send_email` and `delete_customer`. Reading a ticket can be repeated with no
   effect.
4. It cites the agent instead of the record. The trace decides, not the summary.
5. No. A commercial AI service is outside scope, always. Your three permitted
   targets are the practice target, your own agent, and a local model.
:::

::: next | What's Next
Week 2 turns this week's "models vary" from a warning into a measurement. You
will send one request five times, compare what the agent did each time, and start
using the word **trial** the way the rest of the course uses it.

Keep your week 1 trace. You will compare against it.
:::
