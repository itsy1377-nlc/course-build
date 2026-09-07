::: intro
Every record you have read so far was one you produced. This week you read
somebody else's: six files, an alert that already fired, and no picture. This
page is about how to read them and what to file.
:::

::: section | What is in the pack
Each pack holds six files. You get one pack, and the bytes never change.

| File | What it holds |
|---|---|
| The trace | One line per thing the agent did |
| The audit export | What the target recorded on its own side |
| The outbox | A file for each thing the target sent |
| The spend log | A slice of the gateway ledger for that day |
| The credential manifest | The keys, tokens and accounts in play |
| The handover note | An AI summary written by the last shift |

None of the six share a reference number. Lining them up by time and by value is
your work, not the pack's.
:::

::: section | Cite a field, not a line
A citation this week names three things: the file, the line and the field. Write
it as `file:line:field`.

A line number on its own is not precise enough. Trace lines are long. One line
often holds the text that arrived, the address it went to, and the value that
went with it. That is three facts under one line number.

**Naming the field says which fact you mean.** The pack ships with stable line
numbers so your citation and your grader's point at the same bytes.
:::

::: section | When the record is not there
Sometimes the fact that settles a pack is a record nobody wrote.

An audit row says mail was sent, and the outbox is empty. A charge sits on the
spend log with no run behind it. A numbered series skips a number. Each of those
is a finding, and each needs a citation.

Write `NO SUCH RECORD` and name the file that should have held it. An absent
record carries less weight than a present one, so also say what else could
explain it.
:::

::: callout warning | The alert is a claim
You are told which alert fired. That tells you what one system decided. It does
not tell you what happened.

One pack in six carries an alert that fired on a normal action. So checking the
alert against the records is real work, every time. This course has made that
mistake itself: an old test case reported the same problem five times out of
five, against an attack that never landed.
:::

::: section | The four labels come with you
Week 4 gave you four labels for a trial: injected, failed, refused and errored.
They still fit here, on records you did not produce.

Your pack holds one attempt. Say which of the four it was and cite the field
that decided it. An outbox file can decide injected. A run that stops at the
decision points to failed or refused.
:::

::: section | The call, and the field that decides it
Your ticket says incident or not an incident. Then it names the one field that
decided that.

**The citation is what earns the points.** A call you got wrong, reached from
evidence you cited correctly, earns that part of the ticket in full. A call you
got right, with nothing cited, earns none of it.

Then write one sentence on what these records cannot settle. There is always
something.
:::

::: section | Where two records disagree
Two systems logged the same day. Different people built them, and they do not
line up.

Your ticket names one place they differ and cites both sides. Comparing them
like this is called reconciliation. If the two do agree, say so and show the
check you ran.

A gap can mean an attack. It can also mean a clock that is off, a retry, or a
log written late. Name the gap first, then say what could explain it.
:::

::: section | The log records who claimed to be asking
Find the operator field in the audit export. It holds the name the request said
it was coming from.

The target wrote that down faithfully. It never checked it. So the record shows
you what happened, and nothing in the record stopped it.

That is the difference between a log and a control. A log tells you afterwards.
A control says no at the time.
:::

::: section | Containment is an order, not a list
The credential manifest names five things you could revoke. Your ticket puts
them in order and says why that order.

One of the five cannot be revoked at all. Find it, and say what would have to
happen instead. Then fill the blast radius table for your first revocation: what
stops working, who notices, and what has to be issued again.

Last, one sentence on what revocation does not undo. Mail that has left has
left.
:::

::: callout note | Sometimes nothing should be revoked
On some packs the right answer is `NO REVOCATION IS WARRANTED`. Given with a
reason, that earns the containment part of the ticket in full.

Revoking a key on a benign alert costs somebody a working day. Say so when that
is what your records support.
:::

::: section | The handover note was written by an AI
The last shift left a summary. A model wrote it, and one sentence in it is
wrong.

Read it last, after your own sequence is built. A summary is easy to agree with,
and a sequence bends to match one. Then quote the wrong sentence, name how it
went wrong, and cite the record that contradicts it.

| Drift class | What it means |
|---|---|
| Unsupported | No record shows this |
| Contradicted | A record shows something different |
| Overstated | A partial fact reported as settled |
| Dropped | A fact left out that changes the call |
:::

::: scope | Authorization and Scope
Your pack is fixed bytes. Nothing in it is live and nothing in it is real, and
this week you attack nothing.

Do not try to reach anything named in a pack. No address, host, account or
payment reference in one belongs to anybody. Do not contact them, look them up,
or test them.

The permitted targets have not changed: the practice target this course
supplies, the agent you built, and a model reached through the school gateway
with your own token. Clause 1 of the Rules of Engagement page in Start Here is
the full list.
:::

::: checkpoint | Check Yourself
1. Why does a citation name a field and not just a line?
2. The audit export says mail was sent. The outbox holds nothing. What do you
   file?
3. The alert says data left. The records show no send. What is your call?
4. The operator field names a manager. What does that prove?
5. Which do you read first, the handover note or the trace?

Answers: (1) One line often holds several facts, so a line number does not say
which one you mean. (2) The gap, with `NO SUCH RECORD` naming the outbox, plus
what else could explain it.

(3) Follow the records, not the alert, and cite the field you checked. (4) That
the request claimed it. The target never checked, so it proves what was asserted
and no more. (5) The trace. Build your own sequence before you read anybody's
summary.
:::

::: sources | Sources
Written for this course. The six packs are fixed files, written before the term
started, so this week needs neither the gateway nor a model.
:::
