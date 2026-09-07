::: keyfacts | The short version
| Question | Answer |
|---|---|
| How do I find a term? | Use your browser's find, Control-F or Command-F |
| What order is this in? | Alphabetical, in six blocks |
| Which week is a term from? | Each entry names its week in brackets |
| Two things are called a token? | Yes, and they are unrelated. Both are below |
| A term is missing. Now what? | Ask on the Questions and Answers board |
| Is this page graded? | No. It is here to be searched |
:::

::: intro
Every word this course teaches, in plain language, in alphabetical order. Terms
are defined again on the page that first uses them. This page is where you come
back when one has slipped.
:::

::: section | A
- **Agent** (week 1). A language model with two things added: a list of tools it
  may call, and a program that runs a tool when the model asks for it.
- **Approval fatigue** (week 5). What happens when a person is asked to approve
  so many actions that they stop reading them. You measure it from your own
  count rather than hearing about it.
- **Approval gate** (week 5). A check that runs before a tool runs. It pauses
  the run and asks a person. It decides nothing itself, so the control becomes
  the person answering.
- **Audit log** (week 6). The record a target system keeps on its own side,
  separate from your agent's record. Two records of one event can disagree.
:::

::: section | B and C
- **Blast radius** (weeks 1 and 6). Everything one action reaches. Also
  everything that stops working when you take a credential away.
- **Blocked** (week 7). A trial label. The model asked for a tool and one of
  your guards stopped the call. It is the only label that shows a control doing
  something.
- **Burnable key** (week 5). A second gateway key with a small ceiling, issued
  for the runaway exercise. You do not test a spending failure on the key that
  pays the bills.
- **Cap** (week 5). A number that ends a run when spending passes it. A cap has
  no opinion. It stops a runaway and a long useful job the same way.
- **Citation** (every week). A file, a line number and a field inside that line.
  "Line 4, the arguments field" is a citation. "The third box" is not.
- **Containment** (weeks 6 and 7). Taking away what an agent does not need,
  after something has gone wrong. It is an order of steps, not a list.
- **Control** (weeks 5 to 7). Something that says no at the time. A log tells
  you afterwards. That difference is the whole of week 6.
- **Cost stamp** (week 5). What your own run writes for each call: the model,
  the token counts and the price. It is your arithmetic, and it gets checked
  against the ledger.
:::

::: section | D to G
- **Decorator** (week 1). The line starting with an at sign that registers your
  function as a tool. It reads the function's name, arguments and description,
  and builds the tool listing from them.
- **Errored** (week 4 onward). A trial label. The run never finished. An
  errored trial is not a result, so you replace it and report how many
  replacements you ran.
- **Evidence** (every week). A record the world kept: a file a tool wrote, a row
  in a log, a line in a run record. What the model says about itself is never
  evidence.
- **Excessive agency** (week 5). An agent able to do more than its job needs. It
  is one of the selected OWASP risks this course covers, listed as LLM06 in the
  2026 release.
- **Failed** (week 4 onward). A trial label. The run finished and no tool call
  was ever asked for. From outside it looks like blocked, and only blocked shows
  your control working.
- **Filmstrip** (weeks 1 to 5). The picture of a run, one box per event, left to
  right in time order. It is for looking. You cite the raw record, not a box.
- **Gateway** (Start Here). The college service between your notebook and the
  models. It issues your token, meters what you spend, and records every prompt
  and every reply.
- **Grid** (weeks 2, 4 and 7). Thirty squares, one per trial, from the same
  request run thirty times. It shows how often something happens, not whether it
  can happen.
:::

::: section | H to L
- **Handle** (weeks 3 and 7). The name you choose for the class board. Rows and
  columns carry handles, so you write about a tool or an attack rather than
  about a person.
- **Handover note** (week 6). The summary the last shift left, written by a
  model. One sentence in yours is wrong. Read it after you have built your own
  sequence, not before.
- **Incident pack** (week 6). Six fixed files describing one day on an agent you
  did not build. Nothing in a pack is live and nothing in it is real.
- **Injected** (week 4 onward). A trial label. Your irreversible tool ran. It
  is decided by the record that tool left behind, never by what the model said.
- **Irreversible action** (week 1 onward). Something you cannot undo. Writing a
  file, sending mail, charging a card. Reading is reversible, because you can
  read twice and nothing changes.
- **Ledger** (week 5). The gateway's own record, one row per call, held under
  school control. The ledger is the record. Your notebook total is arithmetic
  over the same events.
- **Loop** (week 1). The program that runs your agent. It sends the conversation
  to the model, runs any tool the model asks for, puts the result back in, and
  repeats.
:::

::: section | M to R
- **MCP** (week 3). The Model Context Protocol, a published standard for how a
  program tells a model which tools exist. The field names `name`,
  `description` and `inputSchema` come from it.
- **Notebook** (every week). Your own workspace on the school server, opened in
  a browser. It is yours alone, and a classmate's notebook is never a target.
- **Positive control** (week 4). The second run that checks your instrument. You
  put the same instruction where the model has every reason to follow it. If it
  never fires, your other grid cannot be read.
- **Practice target** (every week). The system your agent works against, given
  to you inside your own notebook. Its customers, tickets and records are
  invented, and they stay invented.
- **Prompt injection** (weeks 4, 6 and 7). Text that a model reads as an order.
  Direct means you typed it yourself. Indirect means it arrived inside content a
  tool read, such as a ticket.
- **Reconciliation** (weeks 5 and 6). Putting two records of the same events
  side by side and saying whether they agree. When they do not, say by how much
  and where you looked.
- **Refused** (week 4 onward). A trial label. The run finished with a decline
  and no tool call. It rests on what the model wrote, so it is the weakest label
  of the five.
- **Revocation** (weeks 6 and 7). Taking a credential away so it stops working.
  It does not undo what was already done. Mail that has left has left.
:::

::: section | S and T
- **Sandbox** (weeks 3 and 7). The walled space on the course server where a
  classmate's tool runs, and where the week 7 board runs everyone's attacks.
  Nothing inside it reaches anything outside it.
- **Schema** (weeks 2 and 3). The list of arguments a tool takes, with their
  types. The model reads it alongside the tool's name and description.
- **Scope** (Start Here). The list of what you are allowed to attack. Four
  things, in clause 1 of the Rules of Engagement page. Anything not on that list
  is out of scope.
- **System prompt** (weeks 2 and 7). The standing instructions sent to the
  model ahead of your own request. It is one block in the input view, and it is
  paid for on every call.
- **Token, the gateway kind** (Start Here). Your credential for the college
  gateway. It identifies you, it carries your budget, and you never share it.
- **Token, the model kind** (weeks 2 and 5). A chunk of text. Models count what
  they read and write in tokens, and the gateway prices a call from that count.
  It has nothing to do with the credential above.
- **Tool** (week 1). A function your agent is allowed to run. The model asks for
  it by name, the loop runs it, and the result goes back to the model.
- **Tool description** (week 2). The sentence you write about a tool. It is the
  only account of that tool the model ever sees, so it is not documentation. It
  is the control surface.
- **Tool poisoning** (week 3). A tool whose description is true and incomplete
  while its code does more. MITRE ATLAS release 2026.07 calls it AI Agent Tool
  Poisoning, AML.T0110.
- **Trace** (week 1 onward). The file a run writes, one record per line: what
  you asked, what the model decided, what ran, what came back. It is the thing
  you cite.
- **Trial** (week 2 onward). One run of the same request under the same
  conditions. Thirty clean trials is the floor in this course. A trial that
  never finished is errored, and an errored trial is not a result.
:::

::: callout note | Two words worth keeping straight
Evidence is a record. A claim is a sentence. Every graded piece of work in this
course asks you to attach the first to the second, and the citation is how you
do it.
:::
