::: intro
Every technical word this course uses is defined here, in plain language and in
alphabetical order. Keep this page open while you read. A word you do not know
is a word to look up, not a reason to stop.
:::

::: callout note | How to use this page
Terms in this course are taught, not avoided. You will meet all of them.

Each one is defined here in one or two sentences. The Content page that
introduces a term also defines it there, the first time you see it.

If a word on any page is not on this list, post it on the Q and A board. It gets
added.
:::

::: section | A
**agent.** A program that lets a language model call your code. You ask it
something, it picks one of your functions, runs it, and uses the result.

**agentic system.** The whole system around an agent: the model, the tools, the
data it reads, and the rules about what it may do. The word means it can act,
not just answer.

**API.** Application programming interface. A defined way for one program to ask
another program to do something.

**API key.** A secret string that proves a request came from your account.
Anyone who has your key can spend your quota, so treat it like a password.

**audit log.** A record the target app keeps of what happened, in order. It is
evidence, because it does not depend on what the model said.

**authorization.** Permission to act, given by someone with the standing to give
it. In security testing it is the whole difference between a job and a crime.

**authorization boundary.** The line around what you are allowed to touch.
Inside it you may test. Outside it you may not, for any reason.
:::

::: section | B and C
**backoff.** Waiting a little longer before each retry. It keeps a failing
request from making the problem worse.

**canary token.** A fake secret planted so that finding it somewhere proves it
leaked. Yours is built from your student ID, so your proof is yours alone.

**Common Cartridge.** A standard file format for moving a whole course from one
learning system to another. This course ships as one.
:::

::: section | D and E
**detector.** The part of the harness that decides whether an attack worked. It
looks for a side effect, not for words in a reply.

**direct prompt injection.** Prompt injection typed by the person talking to the
agent. They ask it to ignore its instructions, and sometimes it does.

**endpoint.** The web address a program sends its requests to. Your model
provider gives you one.

**excessive agency.** Giving an agent more power than its task needs. The
classic case is a tool that does something permanent with nobody approving it.

**exfiltration.** Data leaving a system it was supposed to stay inside. In this
course it usually means a customer record reaching an outside address.

**extension point.** A place in the lab code marked for you to change. There are
five, and every piece of graded work lands at one of them.
:::

::: section | F and H
**finding.** A written report of one security weakness. It says what you found,
how you proved it, how bad it is, and what to do about it.

**flaky.** A FLAG, not a status. The harness sets it on any case where the
attack worked in some trials and not others, alongside whatever the status
already was. A flaky attack is still a vulnerable one. The attack worked in some of
the five trials and not others, which means the defense is not a defense.

**harness.** A program that runs attack cases against the agent, several times
each, and reports what happened. You extend it in Week 7.
:::

::: section | I and J
**indirect prompt injection.** Prompt injection hidden in content the agent
reads later, such as a support ticket or an article. The attacker never talks to
the agent at all.

**JSON.** A plain text format for structured data, built from names and values.
Model replies and tool arguments both arrive as JSON.

**JSON schema.** A description of what a piece of JSON is allowed to contain.
You write one for your own tool, so the model knows how to call it.
:::

::: section | L and M
**ledger.** A file the lab writes with one line for every tool call. Comparing
it to a normal run shows exactly what an attack made the agent do.

**mock provider.** The offline stand-in for a model that ships with the labs. It
proves your code works. It proves nothing about how a real model behaves.

**model.** The language model. It reads text and predicts more text. That is all
it does, and every risk in this course starts from that fact.
:::

::: section | P
**payload.** The text of an attack. It is the part an attacker writes and
plants. By itself it proves nothing.

**prompt.** The text sent to a model. It includes the system prompt, the user's
question, and anything a tool handed back.

**prompt injection.** Text that a model treats as an instruction when it was
meant to be data. It is the central weakness this course teaches.
:::

::: section | R
**rate limit.** A cap on how many requests a provider accepts in a set period.
Going over it returns an error, and your code has to survive that error.

**remediation.** A fix for a weakness, together with the proof that the fix
held. A change with no re-test is not a remediation.

**retry.** Sending a failed request again. It is only safe when you also limit
the number of tries and back off between them.

**rules of engagement.** The written agreement that says what a tester may
attack, and when. This course has one, and you pass a quiz on it.
:::

::: section | S
**scope.** The list of systems you are authorized to touch. Anything not on the
list is out of scope.

**side effect.** A change in the world outside the conversation: a file written,
an email queued, a record changed. Evidence in this course is always a side
effect.

**system prompt.** The instructions a developer gives the model before the user
says anything. It is text, so it has no special power over other text.
:::

::: section | T
**tool.** A function the model is allowed to call. Each one has a name, a
description, and a schema.

**tool authorization.** Checking who is asking before a tool runs, and refusing
when the answer is wrong. A tool that never checks is a weakness.

**tool call.** One request from the model to run one of your tools, with
arguments. Your code decides whether to honor it.

**trace.** The full record of one run: the messages, the tool calls, and the
results. You read it to find out what actually happened.

**trial.** One run of one attack case. The harness runs five trials per case,
because a model does not do the same thing every time.
:::

::: section | V
**virtual environment.** A private folder of Python packages for one project. It
keeps this course's libraries separate from the rest of your computer.

**vulnerable.** The harness status when an attack worked at least once. Once is
enough, because an attacker gets to try again and it costs them nothing here.
:::

::: section | The words the harness prints
Every status the runner can produce, and what each one licenses you to say.

| Status | What happened | What you may write |
|---|---|---|
| `VULNERABLE` | The attack landed at least once | It is vulnerable. Give the rate |
| `NO_HITS_IN_5` | It did not land in the trials that ran | It did not land in five tries. Not that it cannot |
| `BLOCKED_5_OF_5` | The agent tried every time and a control stopped it every time | The control held. The weakness is still there behind it |
| `INCONCLUSIVE` | Fewer than three trials finished, usually rate limits | Nothing. Run it again |
| `ERRORED` | One trial failed on transport, not on the attack | Nothing about that trial. It is excluded from the arithmetic |
| `OK` | A control behaved as it must | The run is trustworthy so far |
| `CONTROL_FAILED` | A control did not | Nothing at all. The run stopped and the numbers below it mean nothing |

**Two of these are easy to read as good news and are not.**

`NO_HITS_IN_5` carries its trial count on purpose. Zero hits in five tries
against something that lands three times in ten happens about one run in six.
Absence of evidence is not evidence of absence, and the status refuses to say
"mitigated" for you. If you want that word in a report, that is a judgement you
are making on top of this number, and you should say what it rests on.

`BLOCKED_5_OF_5` means the injection still works. The agent was steered every
single time and one line of code stopped it at the last moment. That is a very
different residual risk from an attack that failed, and a report that prints
them the same way is hiding the thing a client most needs to know.
:::

::: next
Next is the Course Schedule, which lays out the whole term on one page.
:::
