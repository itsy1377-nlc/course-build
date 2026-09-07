::: learned | What You Learned
1. The model picks a tool from a card, never from the code behind it.
2. The card has three fields, and MCP is where those field names come from.
3. A description can be entirely true and still hide what the tool does.
4. A description that does not match the code is called tool poisoning.
5. Twelve probes find faults that three probes hide.
6. Two of the eight effects leave a file behind. Those are the ones you cannot
   take back.
:::

::: did | What You Did
1. Picked one effect from the menu of eight and set its parameters.
2. Wrote a description sentence that was true and left the effect out.
3. Received three classmates' generated tools with no labels on them.
4. Probed each tool at least twelve times and read its code.
5. Ran your agent with each tool and checked the workspace diff.
6. Filed three reports, each citing a file, a line and a field.
:::

::: checkpoint | Check Yourself
1. Your agent chose a tool that writes to a file. What did it read to decide?
2. A card says "reads a customer record". The code reads it and also appends a
   line to a log. Is the card false?
3. You probe a tool four times and get four correct answers. What have you
   shown?
4. The workspace diff is empty after all your probes. What does that rule out?
5. A classmate writes: "the tool reported that it only reads." What is wrong
   with that sentence?
6. Which standard gives the three field names on a tool card?
7. You have twelve probes and no idea where to start. What do you vary first?
8. May you run a classmate's tool against the practice target outside the
   sandbox?

Answers:

1. The card, which is the tool's name, its description and its input schema.
   Never the code.
2. Not false, and that is the point. It is true and incomplete, which is what
   poisoning usually looks like.
3. Very little. One effect on the menu is wrong on one call in three, and four
   correct answers happen often.
4. Two of the eight effects, the two that write files. The other six leave
   nothing behind, so an empty diff rules out nothing else.
5. It cites the tool instead of the record. A poisoned tool describes itself
   incorrectly on purpose. Point at the raw record.
6. MCP, the Model Context Protocol. It settled the manifest shape your cards
   use.
7. Nothing. Call it twelve times with the same argument first. That alone finds
   three of the eight effects.
8. No. A classmate's tool runs inside the supplied sandbox, against your own
   agent, and nowhere else.
:::

::: next | What's Next
Week 4 keeps this question and moves the false sentence. This week it sat in a
tool card that a classmate wrote. Next week it sits in a ticket that a stranger
wrote, and your own agent reads it in the middle of a run.

Keep your three reports. The habit you built here, naming a field in a file
rather than describing an impression, is what week 6 is built on.
:::
