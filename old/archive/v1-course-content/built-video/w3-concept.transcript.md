# The inversion

A text version of the concept video. Every word spoken, in order.

## The inversion

> Your script stops giving orders
> and starts taking requests.

This week the direction flips. Until now your script called the model. From here the model calls your code. That is one line of difference, and it changes who is in charge.

## What changed between the weeks

1. **Week 2.** You built the message list. You called the model. It sent back text. Your script printed it.
2. **Week 3.** You pass a list of tools. The reply can name one of them. Your code runs it.

Here is the Week 2 shape. You built the message list. You chose when to call the model. It produced text, and your script printed it. Every decision was yours. Now the Week 3 shape. You add one line, and you pass a list of tool schemas. The reply can still be text. Or it can be a request for one of your functions. The model did not change. The call you send did not change much either. One argument did.

## Four things moved

1. You passed a menu
2. The reply can be a request
3. The tool name came from the model
4. The arguments came from the model

Four things moved when you added that line. First, you passed a menu. The model now knows what your tools are. Second, the reply can be a request instead of an answer. Your code checks which one arrived. Third, the tool name came from the model. You never typed search tickets anywhere. Fourth, the arguments came from the model too. You never typed that query either. Nothing about the model changed. What changed is where the next decision comes from.

## The model did not run anything.

> It produced text naming a function and some arguments.
> Your Python read that text and made the call.

Here is the part that trips people up. The model did not run anything. It produced text. That text named a function and some arguments. Your Python read the text, and your Python made the call. You still own every line that runs. You no longer own the choice of which line runs next. That is the inversion, and it is what makes an agent an agent.

## The model asks. Your code answers.
If you keep one sentence from this week, keep this one. The model asks. Your code answers. Asking is free. Anyone whose text reaches the model gets to ask. Answering is where you decide, and deciding is where security lives.

## A schema is not documentation. It is a promise your code has to keep.

> The model never sees your Python.
> It never sees your comments.

Now the one thing the model ever learns about a tool. It never sees your Python. It never sees your comments. It reads the schema, and that is all it gets. So a schema is not documentation. It is an interface, and a promise your code has to keep.

## When the sign on the door is wrong

1. A vague description, so the tool runs at the wrong moment
2. An argument with no description, so the model invents a value
3. A schema that does not match the function

A schema fails in three ways, and you will meet all three. One. A vague description, so the tool runs at the wrong moment, or never runs at all. Two. An argument with no description. The model invents a value, and the value it invents is wrong. Three. A schema that does not match the function. Your code then rejects exactly what the schema promised. In Module 2 you write one of these yourself. The autograder builds arguments from your schema and calls your function with them.

## Watch the inversion happen

```
python -m agent.replay
```

You do not have to take my word for any of this. Run python dash m agent dot replay. It walks your last run one step at a time. Next to the step where the model asked for a tool, it prints one line. Nothing in your program chose this.

## The Week 1 picture, with one new box

*Diagram: Four boxes left to right. You ask. The model picks a tool and its arguments. Then before_tool_call decides, drawn in the accent colour as the one place a call can still be stopped. Then the tool runs. A return path runs from the end back to the start, because the result becomes another message and the loop runs again.*

- You ask, one message in
- The model picks a tool, and its arguments
- before_tool_call(), your code decides
- The tool runs, and there is no undo

- Return path: the result becomes another message, and the loop runs again

This is the Week 1 picture with one new box in it. You ask. The model picks a tool and its arguments. Then before tool call decides. It runs after the arguments are parsed, one line before the tool runs. That gap is the last moment anything can be stopped. Then the tool runs. A record is read, or an email is queued, and there is no undo. The result becomes another message, and the loop runs again.

## It ships wide open.

> before_tool_call says yes to everything.
> You do not change it in Week 3. You learn where it sits.

Right now that function says yes to everything, every time. You do not change it this week. You come back to it in Module 4, four weeks from now. Learn where it sits, and remember one thing about it. A blocked call still gets a line in the ledger. That line is your proof the guard did something. Your job this week is smaller than it sounds. Get one real tool call into your log. That is the checkpoint, and it is pass or fail. Working code is not the bar.
