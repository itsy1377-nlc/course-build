::: learned
- The agent loop is bounded. `max_steps` is a control written in code, and it
  is the reason a runaway agent stops.
- The message list only grows. Every tool result is sent again on every later
  step.
- Untrusted text and your system prompt sit in the same list, in the same
  format. The model reads them the same way.
- A tool name becomes a function through two checks: the registry, then the
  allowlist. A tool the model is never told about cannot be called.
- A failing tool returns text to the model and the loop continues. That is
  correct behavior.
- A tool that fails silently is worse than one that is missing, because the
  agent carries on as if it worked.
- Your new tool checks nothing about who is calling it. That is Week 6.
:::

::: did
- Traced one full run of the loop on paper, then ran it and compared.
- Read the response shape reference and found the type of the `arguments`
  field.
- Wrote the body of `get_customer`, including the path for a customer that does
  not exist.
- Designed a tool of your own, wrote its JSON schema, and registered it in two
  places.
- Ran `python -m pytest tests/test_module2.py -q` until it passed.
- Documented one AI suggestion you rejected, and why, in `AI-USE.md`.
:::

::: checkpoint
Answer these for yourself before Week 5 opens.

1. Your tool returned 6000 characters. What did the loop do with them, and why
   does that matter on the next step?
2. A classmate's schema says an argument is an integer. Their function expects
   a string. What does the model send, and what happens?
3. You have four tools registered now. Name one thing each of them can reach
   that a stranger should not be able to steer.
4. Your agent read a support ticket in step 1. In step 2 it called
   `send_email`. Who chose the recipient?
:::

::: next
Week 5 turns the work around. You stop building and start attacking.

Somebody has written a support ticket on purpose to steer an assistant like
yours. You will run it, watch what your agent does, and collect evidence of
what happened.

The evidence is not what the model said. It is a file in `target/outbox/` with
a recipient you never approved. That distinction is the whole second half of
this course.
:::
