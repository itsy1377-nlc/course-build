::: intro
One page that proves you are moving. It is pass or fail, and it is a
diagnostic, not a judgment of quality. Its only job is to show that you have a
working harness, one payload of your own, and a real transcript.

Due Sunday 11:59 PM of week 6, which is day 42.
:::

::: scope
Everything here runs against HelpDesk Lite on your own computer. Nothing else.

You paste your target configuration into this checkpoint. That is how the
authorization boundary gets checked, so do not skip it.
:::

::: directions
**Do your Module 3 harness run first.** That run has to happen against the
shipped cases, unmodified. Once it is finished, come back and add a case of
your own.

**Writing one payload of your own.** A case is a small YAML file in
`harness/cases/`. No Python is involved.

1. Copy any shipped case file to a new name.
2. Give it a new `id` and a new `title`.
3. Write your own `prompt`. This is the payload.
4. Keep `authorized: true`.
5. Pick one detector: a side effect, a canary, or a tool shape.
6. Run `python -m harness.runner --list` to confirm the harness loaded it.

If the harness rejects your file, read the error. It names the field and says
what is wrong with it.

**Hand in one page with these five items, in this order.**

1. **Your payload count.** How many cases your harness loads in total. The
   `--list` command prints them.
2. **One payload you wrote yourself.** Its `id`, and its prompt text copied
   word for word. Not a description of it.
3. **A transcript excerpt, at most 15 lines.** It shows the target doing
   something it should not do. Pull it from your trace file in `runs/traces/`,
   from `runs/ledger.jsonl`, from a file in `target/outbox/`, or from the
   evidence line in your report. A near miss is fine, and see the note below.
4. **The weakness class it maps to.** One of these five: direct prompt
   injection, indirect prompt injection, injection from trusted internal
   content, excessive agency, insecure tool authorization.
5. **Your target configuration.** Paste the `target:` block from
   `config/lab.config.yaml`.

**Then one sentence, at the bottom.** Either "I am stuck on" followed by the
thing, or "I am not stuck." Both answers are fine. Only silence is a problem.
:::

::: callout note | A near miss passes
Your own payload does not have to work.

If it did not land, paste what happened anyway and label the class you were
aiming at. Say in one sentence what you think stopped it.

A documented near miss with the correct class label passes this checkpoint. A
made-up success does not.
:::

::: callout warning | The three things that fail this checkpoint
1. **A payload you did not write.** A shipped case with the ID changed is not
   your payload.
2. **A transcript you typed instead of copied.** Paste real output, including
   the ugly parts.
3. **A target address that is not on the authorized list.** That is a scope
   problem, and it is the one thing here that is serious.
:::

::: grading
| Criterion | Points |
|---|---|
| All five items present, plus the blocker sentence, with one original payload, one genuine transcript, and an in-scope target configuration | 20 |
| Anything on that list missing | 0 |
| **Total** | **20** |

This is graded pass or fail. It is not judged on elegance, on whether your
payload worked, or on how much you have finished.

Submissions are triaged by script, so your instructor reads the exceptions.
Expect a reply only if something needs attention.
:::

::: submit
Upload one file, markdown or PDF, or paste the same content into the text box.

Name it `checkpoint2-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
