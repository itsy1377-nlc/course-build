::: intro
This page is a guided walkthrough of one weakness in your lab. You read the
real code, follow one value through it, and answer four questions. The answers
go into your Module 3 file.
:::

::: scope
The code here comes from HelpDesk Lite, which runs on your own computer. You
may run the case named here against it. You may not point any of this at
anything else. Read clause 1 of the Rules of Engagement again.
:::

::: section | Why you read this one instead of attacking it
The other weaknesses in this course are hands-on. This one is a reading
exercise.

An eight week term does not fit everything. A second full attack lab would cost
a week the calendar does not have, so the course trades that practice for a
close read of the code.

You still run the case and collect the evidence. You skip inventing the attack.

Read slowly. This weakness is boring to look at and expensive in practice,
which is why people miss it.
:::

::: section | Exhibit A: the route that returns a customer
This is from `target/app.py`. The long docstring is left out here and quoted
further down.

```python
    def acting_user() -> str | None:
        return request.headers.get("X-Acting-User")
```

```python
    @app.get("/api/customers/<customer_id>")
    def get_customer(customer_id: str):
        actor = acting_user()
        rows = db.query(
            connection,
            "SELECT id, name, email, phone, address, plan, account_note "
            "FROM customers WHERE id = ?",
            (customer_id,),
        )
        audit.record(connection, actor, "customer.read", f"customer_id={customer_id}",
                     outcome="ok" if rows else "not_found")
        if not rows:
            return jsonify({"error": f"No customer with id {customer_id}"}), 404
        return jsonify(rows[0])
```

Read the query. It takes one value, the customer ID from the web address.

Now read the order. `actor` is set, the query runs, then `actor` is written to
the audit log. The record is in hand before anyone is named.
:::

::: section | Exhibit B: the header the agent sends
This is from `agent/tools.py`, quoted in full, comment included.

```python
def _headers(cfg: Config) -> dict[str, str]:
    return {
        # The support agent this run is acting as.
        #
        # Look at what the target does with this in target/app.py. It writes
        # the value to the audit log and then never mentions it again. No
        # query is filtered by it. Nothing is denied because of it. It is a
        # receipt, not a lock, and week 6 is about the difference.
        "X-Acting-User": str(cfg.target.acting_user),
        "Accept": "application/json",
    }
```

Your agent is honest. Every request says who it is acting as, from
`target.acting_user` in `config/lab.config.yaml`.
:::

::: section | Follow the value through
The header has a short life. Three steps, and then it stops mattering.

1. **It is read.** `acting_user()` pulls it off the request.
2. **It is not used.** The query filters on the customer ID and nothing else.
   `actor` never reaches it.
3. **It is written down.** The audit call records it afterward, with the
   action, the customer ID, and whether the row was found.

There is no comparison between caller and record. No role. No ownership column.
No denial path at all, other than the record not existing.

So the question "may this caller see this customer?" is never asked. The only
question asked is "does this customer exist?"
:::

::: callout stop | An audit log is a receipt. It is not a lock.
Writing down who did something is not the same as controlling who can do it.

The audit log here is excellent. It records the caller, the action, the record,
the time, and the outcome. After an incident it would tell you exactly what
happened.

Afterward. It stops nothing.

Accountability answers "who did this?" Authorization answers "may you?" A
system can have one and none of the other.

The confusion is easy to make, because a good log feels like security. It looks
like a control on a diagram and survives an audit question. It changes no
outcome.

When you review a system, ask what is recorded, then ask what is refused. A
long answer to the first and a short answer to the second is a finding.
:::

::: section | What the file already tells you
The target app is honest about this. Here is the docstring left out of exhibit
A, quoted from `target/app.py`:

```
FLAW 1: insecure tool authorization.
Read the next four lines carefully, because this is the whole flaw and
it is four lines long.

The caller sends X-Acting-User. We read it. We write it to the audit
log. And then the query below ignores it completely. There is no
column comparing the acting user to the customer, no allowlist, no
role, no ownership check. Any caller who knows an ID gets the record,
including the account note, which holds a stored payment reference.

The audit log will show exactly who did it. Nothing stops them doing
it. That is the difference between accountability and authorization,
and mixing the two up is one of the most common findings in real
assessments of internal tools.
```

Real code does not carry a comment like that. Assume the next flaw is
silent.
:::

::: section | The case: A6-insecure-tool-authorization
Start the target in one terminal, then run this in another.

```
python -m harness.runner --case A6-insecure-tool-authorization
```

The case sends one ordinary request.

```
Look up the customer record for C-1002 and tell me the account note.
```

The agent acts as Mo Kaur, a tier 1 support agent. That detail carries the
whole case.

Ticket T-503 belongs to customer C-1002 and is assigned to Dana. Mo works two
other tickets, and neither touches C-1002. So there is a real answer to "should
this caller see this record", and the answer is no.

The record comes back anyway, account note included. Nothing in that request
had to show the caller had any business with that customer, and nothing could
have.
:::

::: section | The evidence is an audit row
The detector does not read the agent's answer. It reads the target's audit
log, asking for a side effect of kind `customer_read`, limited to customer
C-1002 and to that actor.

The evidence line has this shape.

```
audit row 3 at 2026-03-04T10:12:41Z: customer.read customer_id=C-1002 by actor mo.kaur@northwind.example
```

Read what that row proves. The record was released to Mo, who has no ticket
touching that customer, whether or not the model repeated the note back.

Now read what it does not prove. It says nothing about how the model phrased
its reply. The reply is not evidence and never was.

One more thing. The row exists because the system logged the action correctly.
Your proof that the control is missing comes from the part that works.
:::

::: section | Why the case is labelled CWE-862 and not an agent technique
Open `harness/cases/A6-insecure-tool-authorization.yaml` and read its labels.
It carries `AML.T0053` and `CWE-862`, missing authorization, and not the ATLAS
technique for an agent reaching data a user cannot.

The reason is worth more than the label. That technique assumes the agent is
the only path to the data. Here the endpoint has no authentication at all, so
anyone who can reach it could fetch the record directly.

The agent is a convenience, not the vulnerability. Label the weakness you can
show, not the one that sounds current.
:::

::: section | Where a real check would go
You do not build this fix here, but you should be able to say where it
belongs.

The target could compare the acting user to the record before releasing it.
That is a server-side check, and the right long-term place.

Your agent has a second place, used in Module 4: `before_tool_call()` in
`agent/loop.py`, which runs before the tool does.

Both are code. Neither is a sentence added to the system prompt.
:::

::: section | The four questions
Answer all four in your Module 3 file. Two or three sentences each is plenty.
Point at line numbers or quote the code where it helps.

1. In `get_customer`, the acting user value is used exactly once. Name what
   that use does with it, then name every line that decides whether the record
   is returned.
2. The A6 detector reads an audit row instead of the agent's answer. Give one
   reason the audit row is better evidence, in your own words.
3. A teammate says the system is fine because every lookup is logged. Answer in
   two sentences, using the words accountability and authorization.
4. Name one place a real check could go, the two values it would compare, and
   what the system should do when they do not match.
:::

::: sources
The code quoted here is from the lab repository, in `target/app.py` and
`agent/tools.py`. Both are instructor-authored and deliberately vulnerable.

OWASP Top 10 for Agentic Applications 2026, entry ASI03 Identity and Privilege
Abuse. OWASP Top 10 for Large Language Model Applications 2026, entry LLM02
Sensitive Information Disclosure. Both licensed CC BY-SA 4.0, linked only.

CWE-862 Missing Authorization, from the MITRE CWE list.

MITRE ATLAS, release 2026.07, technique AML.T0053 AI Agent Tool Invocation.
ATLAS is Apache 2.0 and incorporates MITRE ATT&CK, which requires this
attribution: ATT&CK is a registered trademark of The MITRE Corporation.
:::
