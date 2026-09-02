# Four roles, one box

A text version of the concept video. Every word spoken, in order.

## Four roles. One box.
This week you put a real model on the other end of the line. You send one request. You read one reply. Both are plain JSON, and there are fewer moving parts than you expect.

## One JSON object, four fields

1. model: which model you are calling
2. messages: the conversation, and the whole input
3. temperature: how much answers vary, set to zero
4. max_tokens: a cap on the length of the reply

Everything you send sits in one JSON object, built in the file agent llm dot py. Model names the model you are calling. It comes from your settings file. Messages is the conversation. It is also the whole input the model gets. Temperature controls how much answers vary. The labs set it to zero. Max tokens caps how long the reply can be. One call to post sends that object. It waits sixty seconds, then gives up instead of hanging forever. That is the only place your labs talk to a model over the network.

## Four roles, and who each one speaks for

1. system: your instructions to the agent
2. user: the person asking
3. assistant: the model's earlier answers
4. tool: a result your code sent back

Every entry in that list has a role and some content. System holds your instructions to the agent. User is the person asking. Assistant is what the model already said. And tool is a result your own code handed back.

## All four arrive in one list, as text, in one request.

> A label is a hint carried inside the text.
> It is not a wall around it.

Now the fact this course is built on. All four arrive in one list, as text, in one request. Models are trained to weight those labels, and that does help. But a label is a hint carried inside the text, not a wall around it. Your instructions and a stranger's ticket travel in the same box. That is not a bug you can patch. It is the shape of the interface.

## The answer sits four levels down

```
text = response["choices"][0]["message"]["content"]
```

Now the reply, which is also JSON. The text you want is four levels down. Response, then choices, then zero, then message, then content. You will write that chain many times this term. Choices is a list because the API can return more than one answer. Here it always returns one, so the index is always zero. Your lab code has a function called message of that does this lookup for you. It catches a missing key and says so, rather than failing four levels deep.

## A reply message goes one of two ways

*Diagram: The reply message splits into two tracks. One track is content, which is text written for a person to read. The other track is tool calls, which is a request for your own code to run a function. The tool calls track is marked as the one that matters.*

- The reply message, one object, two possible shapes
- content, text for a person to read
- tool_calls, a request for your code to run something

Look at the shape of that message, because the rest of the course lives inside it. One way, the message carries content. That is text written for a person to read. The other way, it carries tool calls. That is a request for your code to run something. When the model wants a tool, content is null and the finish reason becomes tool calls. Tool calls is a list, because the model can ask for several at once.

## The arguments look like a dictionary. They are a string of JSON.

> So asking for args of query raises TypeError.
> Parse the string first.

Here is the line that costs people the most time this week. A tool call carries arguments, and on screen they look like a dictionary. They are a string. So asking for args of query raises a TypeError. You call json dot loads on that string first, and then you have a dictionary. Now notice who wrote that string. The model did, after reading whatever your last tool returned. That may have been a ticket a stranger typed. Hold on to that until Week 5.

## Which errors are worth trying again

1. **Retry.** 429 means you went too fast. 503 is a bad moment on the server. Both clear on their own.
2. **Do not retry.** 401 means your key is not accepted. No amount of trying again can change that.

Two kinds of failure, and telling them apart is Module 1. A 429 means you went too fast. A 503 is a bad moment on the server. Both are worth another try. A 401 means your key is not accepted. Retrying that one burns your whole daily quota in about four seconds, on a request that could never succeed. Then you are locked out until tomorrow, and the assignment is due tonight. So Module 1 asks you to decide, in code, which errors get a second try.

## Get the key working early. Then write the three functions.

> Every package is pinned to an exact version,
> because pip install runs code written by strangers.
> That risk has a name: LLM04, Supply Chain.

One last habit, and it comes from the same careful thinking. Every package in your labs is pinned to an exact version. Pip install downloads and runs code written by strangers. Six of them you chose. Eighteen you have never heard of. That risk has a name in this course. LLM04, Supply Chain. So set up your key on day eight, not day fourteen. Signups can take a day. Your key goes in the file named dot e n v, and nowhere else. Then write the three functions in Module 1. Nothing in them needs a network or a key.
