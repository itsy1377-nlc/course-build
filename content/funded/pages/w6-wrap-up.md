::: learned | What You Learned
1. A citation names a file, a line and a field, because one line holds several
   facts.
2. A record that is missing can still be cited, by naming the file that should
   have held it.
3. An alert is a claim about what happened. The records decide.
4. A log records who claimed to be asking. Recording is not checking.
5. Containment is an ordered list with a price, and revocation does not undo
   what has already left.
:::

::: did | What You Did
1. Read six files of records you did not produce, with the filmstrip off.
2. Built the agent's sequence in order, citing a field for every step.
3. Checked the alert against the records and made the call, with its citation.
4. Ordered the revocations, marked the one that cannot be revoked, and priced
   the first one.
5. Found where two records disagree, and which sentence of the handover note is
   wrong.
:::

::: checkpoint | Check Yourself
1. Your ticket cites `trace.jsonl:14`. What is missing?
2. The spend log shows a charge with no run behind it. How do you cite that?
3. The alert fired, and every record shows normal work. What is your call, and
   what does it cost to get it wrong?
4. Which is stronger evidence: an outbox file, or the agent's final answer?
5. You revoke the gateway key first. Name two things that stop working.
6. The handover note says "no customer data left the system." The outbox holds
   a file with a customer record in it. Which drift class?
7. You revoked every credential in the manifest. Name one thing that does not
   fix.

Answers:

1. The field. A trace line can hold the text that arrived, the address it went
   to, and the value that went with it.
2. `NO SUCH RECORD`, naming the trace file that should have held the run. Then
   say what else could explain the gap.
3. Not an incident, with the field you checked. Getting it wrong costs somebody
   a working day, because a revoked key stops real work.
4. The outbox file. It is a record the world kept. The final answer is text the
   model wrote about itself.
5. Answers vary. Any two of: the agent stops running, the audit rows stop, and
   anything sharing that token stops with it.
6. Contradicted. A record shows something different, and you cite the outbox
   file.
7. Answers vary. Data that already left is still gone, and a copy somebody
   already took is still theirs.
:::

::: next | What's Next
Week 7 is the gauntlet. You turn on every control you built, including the
containment you recommended this week, and run two live rounds: your defences
against the class's attacks, then your attacks against theirs.

Keep your ticket. The blast radius table you filled in is the argument for the
control you are about to switch on.
:::
