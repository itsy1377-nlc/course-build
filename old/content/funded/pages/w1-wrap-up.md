::: learned | What You Learned
1. An agent is a model, a list of tools, and a loop that runs the tools.
2. The model chooses a tool by reading the description you wrote.
3. A tool's result goes straight back into the model's next input.
4. The record is the evidence. What the agent says about itself is not.
5. Some actions cannot be undone, and those are the ones that matter most.
:::

::: did | What You Did
1. Passed the scope, safety and logging gate.
2. Changed one line of a working function and added the decorator above it.
3. Watched the model decide by itself to call your tool.
4. Broke it six ways and named the field that changed each time.
5. Wrote three fields for each of your two tools, including the one that writes.
:::

::: checkpoint | Check Yourself
1. You deleted the description and the model stopped calling your tool. Did you
   break the code?
2. You cut the step limit to one. Where does the run stop?
3. A classmate writes: "the agent confirmed it wrote nothing." What is wrong
   with that sentence?
4. One tool reads a value and gives it back. The other writes a file. Which one
   is irreversible?
5. You want to try the same edits on a public chatbot to compare. May you?

Answers:

1. No. The code still runs. What changed is what the model was told about it,
   and that alone was enough to change the choice.
2. After the first tool call. The loop stops before the model can use the
   result, so you get no final answer.
3. It cites the agent instead of the record. Open the raw file and cite the line
   and the field.
4. The one that writes. A file that has been written stays written, while a read
   can be repeated with no effect.
5. No. A commercial AI service is never a permitted target. Your three are the
   practice target, your own agent, and the school gateway.
:::

::: next | What's Next
Week 2 turns "the model decides from words" into a measurement. You give two
tools the same code and two different descriptions, then run thirty trials and
count what it picked. You look for one edit that moves the result and one that
does not. Both are worth full credit, because a change that does nothing is a
finding too.

Keep your week 1 record file and your two tool records. Week 5 uses the
irreversible flag you just wrote to decide what needs approval.
:::
