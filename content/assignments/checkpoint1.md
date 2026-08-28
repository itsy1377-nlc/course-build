::: intro
One page. It proves you are unblocked and nothing else.

This is pass/fail and worth 20 points. It is not judged on quality, elegance,
or completeness. If one real tool call happened, you pass.
:::

::: callout stop | The pass bar, stated plainly
**One real tool call, with a real tool name, pasted from your own log.**

That is the bar. Not a good tool. Not a finished agent. One call.

If you cannot get there, there is a fallback path below, and using it still
passes. Read it before you decide you are stuck.
:::

::: directions
**Step 1. Make one tool call happen.**

Start the target app and leave it running:

```
python -m target.seed
python -m target.app
```

In a second terminal, ask the agent for something that needs a tool:

```
python -m agent.cli "summarize ticket T-501"
```

The shipped config uses the offline `mock` provider, so this works with no API
key. The tools still talk to the target app, so the app has to be running.

**Step 2. Find your ledger line.**

Open `runs/ledger.jsonl`. Every tool call your agent has ever made is in there,
one call per line.

Find a line where `"allowed"` is `true` and `"tool"` holds a real tool name.
Copy the whole line. Do not clean it up, reformat it, or shorten it.

A line looks like this:

```
{"allowed": true, "args": {"query": "T-501"}, "error": null, "reason": "", "result_chars": 212, "run_id": "20260315-141002-a91c4d", "step": 1, "tool": "search_tickets", "ts": "2026-03-15T14:10:02Z"}
```

The `"ts"` field is your timestamp. It has to be in what you paste.

**Step 3. Paste the schema for that tool.**

Open `agent/tools.py` and find the `TOOLS` registry. Copy the `schema` for the
tool named in your ledger line. Copy it exactly as it is registered. Do not
retype it from memory.

**Step 4. Write one sentence about the tool.**

Say what it does and what it refuses to do. One sentence covering both.

An example of the right shape: "`send_email` queues one message to one
recipient, and it refuses to run at all when the `to` argument is empty."

Look at the function itself before you write this. Find a line that says no to
something.

**Step 5. Write your status sentence.**

Write exactly one of these sentences, filling in the blank if you use one that
has one:

```
I am stuck on ___.
```

```
I am not stuck.
```

```
I am stuck on ___, so I used the agent-working branch.
```

Be specific in the blank. "I am stuck on the target app refusing to start on
Windows" is useful. "I am stuck on everything" is not.

Nobody loses points for being stuck. This sentence is how your instructor finds
you before it costs you a grade.
:::

::: callout tip | The fallback path, and using it is fine
If your own agent will not run, do this instead.

1. Get the instructor's working branch. It is published on day 18, three days
   before this is due:

```
git fetch origin
git switch agent-working
```

2. Run steps 1 and 2 above on that branch. It works.
3. Use its ledger line and its schema for steps 2 and 3.
4. In step 5, write: `I am stuck on ___, so I used the agent-working branch.`

**This passes.** It is worth the same 20 points as any other submission. The
branch exists for exactly this, and telling your instructor you used it is the
whole reason it exists.

The day 18 announcement repeats these two commands.
:::

::: callout warning | Two things that fail this, and both are easy to avoid
**An edited ledger line.** If you tidy the JSON, retype it, or drop the
timestamp, it no longer proves a run happened. Paste it whole.

**A schema for a tool your ledger line does not name.** The schema and the
ledger line have to be about the same tool. Check the names match before you
submit.
:::

::: submit
Upload one file, markdown or PDF, or paste the same content into the text box.

Name it `checkpoint1-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
