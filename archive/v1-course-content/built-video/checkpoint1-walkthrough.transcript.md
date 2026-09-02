# One real tool call

A text version of the walkthrough video. Every word spoken, in order.

## One real tool call

> Pass or fail, twenty points.
> Not a good tool. Not a finished agent. One call.

This checkpoint has one bar, and it is a low one. One real tool call, with a real tool name, pasted from your own log. Not a good tool. Not a finished agent. One call. It is pass or fail, and it is worth twenty points. Nobody grades it on quality, elegance or completeness.

## At the terminal

Commands run, in order:

- `curl -s http://127.0.0.1:8000/api/health`
- `python -m agent.cli "summarize ticket T-501"`

The target app runs in a second terminal. Check that it is up first. It answers ok, service helpdesk lite. That is all you need from it. Now ask the agent for something that needs a tool. Ticket T-501 is an ordinary one. A customer cannot sign in to the parts portal. Nothing is hidden in it. That comes later in the course. The shipped config uses the offline mock provider, so this works with no API key. The tools still reach the target app, so the app has to be running. Read the first line. Your code ran search tickets. That is one real tool call.

## At the terminal

Commands run, in order:

- `tail -1 runs/ledger.jsonl`

Every tool call your agent has ever made lands in the ledger file, one call per line. The last line is the run you just watched. Read the fields out loud. Allowed is true. Tool holds a real tool name, search tickets. Step is one, and ts is your timestamp. Copy the whole line. Do not tidy it, retype it, or shorten it.

## Both are easy to avoid

1. An edited ledger line
2. A schema for a tool your line does not name

Two things fail this checkpoint, and both are easy to avoid. An edited ledger line stops proving that a run happened. If you tidy the JSON or drop the timestamp, it is no longer evidence. Second, a schema for a tool your ledger line does not name. Step three asks you to paste the schema from the registry. Check that the two names match before you submit.

## Using it is fine

```
git fetch origin
git switch agent-working
```

If your own agent will not run, take the fallback path. Fetch the instructor branch, then switch to it. It is published on day eighteen, three days before this is due, and it works. It is worth the same twenty points as any other submission. Telling your instructor you used it is the whole reason it exists.

## Write the status sentence.

> "I am not stuck."
> Or "I am stuck on ..." and be specific.

Last, the status sentence at the bottom of your page. Write, I am not stuck. Or write, I am stuck on, and then be specific. The target app refusing to start on Windows is useful. Everything is not. Nobody loses points for being stuck. That sentence is how your instructor finds you before it costs you a grade.
