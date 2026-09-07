::: intro
A cell failed and you're stuck. This page is the two-minute version of what to do. It's the same card that opens the week 0 notebook, so you can reach it from any week without hunting.
:::

::: keyfacts
|  |  |
|---|---|
| Read first | The last line of the error, not the first |
| The error type | The word before the colon on that last line |
| Your line | The last line in the block that names your own cell |
| The full version | Section 10 of the week 0 notebook, about 30 minutes |
| Still stuck | Email your instructor and paste the last line of the error |
:::

::: steps | Do this now
1. Read the last line of the error first. Everything above it's context.
2. Name the error type. It's the word before the colon on that last line.
3. Find your line. Look for the last line that names your own cell.
4. Print the value on the line above the one that failed.
5. Change one thing. Run it again.
:::

::: section | Six errors you will meet
Python prints a block of text when a line of code fails. That block is called a traceback. Its last line names the error type. Here's what each type usually means.

| Error type | What it usually means |
|---|---|
| `NameError` | You used a name before it exists, or you did not run the cell that makes it |
| `SyntaxError`, `IndentationError` | Python could not read the line at all |
| `KeyError` | You asked for a name that is not in the box |
| `TypeError` | You used a value in a way its kind does not allow |
| `ValueError` | The kind was right and the content was wrong |
| `AttributeError` | You asked a value for something it does not have |
:::

::: callout tip | The one that costs the most time
In a notebook, the cell that shows the error isn't always the cell that's wrong.

Cells run in the order you click them. A name made in a cell you never ran doesn't exist. You can see it on the screen. Python has still never heard of it.

The fix, in order. Run the cells above the failing one, from the top. If that doesn't do it, restart the notebook and run every cell in order. Then read the error again.
:::

::: section | Three things not to do
1. Don't retype the whole cell. The message already names the line that failed.
2. Don't delete the error and try something else at random. Read it first.
3. Don't paste your whole notebook into an AI assistant before you read the last line. The course AI policy allows AI help with disclosure. It works far better when you can say which error you got.
:::

::: section | Where the full version lives
Section 10 of the week 0 notebook walks all of this in detail. It shows one traceback labeled part by part. It then breaks each of these six errors on purpose, so you read the real message and then the fix.

Read that section even if you skip the rest of week 0. It's the most useful half hour in the on-ramp.
:::
