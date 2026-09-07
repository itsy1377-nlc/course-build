::: keyfacts | The short version
| Question | Answer |
|---|---|
| What is this page | Every term this course teaches, in plain words |
| How is it ordered | Alphabetically, in six blocks |
| Fastest way to use it | Your browser's find command, not your eyes |
| The five that matter most | Agent, trace, evidence, trial, control |
| A word is missing | Ask for it on the Questions and Answers board |
:::

::: intro
This page is for looking things up. Each term is defined the way this course
uses it, and the week that teaches it is often named in the definition.
:::

::: section | A to B
| Term | What it means |
|---|---|
| **Accountability** | Writing down who did something. It is not the same as authorization. |
| **Actor** | The audit log field naming who the caller said it was. It records a claim of identity, not a checked one. |
| **Agent** | A language model, plus a list of tools, plus a program that runs those tools. A model on its own cannot act. |
| **Agentic AI** | The general name for AI systems that take actions instead of only writing text. It is the subject of this course. |
| **Alert** | A short message from a detector saying one narrow thing happened. It is a claim, not a conclusion. |
| **Assertion** | A statement that something happened, with no record behind it. It is the opposite of evidence here. |
| **Audit log** | The record the practice target writes for each request that matters. Five fields: time, actor, action, detail, outcome. |
| **Authorization** | Deciding who is allowed to do something. Only a check gives you this. A log does not. |
| **Baseline** | The measurement you take before you change anything. Without it, the number after your fix means nothing. |
| **Benign case** | Ordinary, legitimate work run through the same door your control closed. It has to finish in every trial. |
| **Blast radius** | Everything an agent can reach through its tools, including the parts it cannot undo. |
| **BLOCKED_5_OF_5** | A result word. The agent tried the action and your control refused it in all five trials. |
| **Board** | The class results board. It shows each control by handle, with a result for every pooled case. |
:::

::: section | C to D
| Term | What it means |
|---|---|
| **Canary token** | A made-up string planted in one place, with no reason to move. If it turns up elsewhere, something moved it. Yours come from your own student ID. |
| **Case file** | A small settings file that says what to send, where to send it, and what counts as a hit. It is settings, not code. |
| **Case pack** | The preserved records you investigate in week 5: two traces, an audit export, outbox messages, an analyst note, and a manifest. |
| **Class pool** | The attack cases the class wrote in week 3. Cases are shared by handle, never by name, and your instructor reads each one first. |
| **Containment** | The one change you would make to stop what you found. You name it in week 5 and build it in week 6. |
| **Control** | A rule that decides whether an action runs. In this course a control is code at the tool boundary, not a sentence in a prompt. |
| **Deny by default** | Start from no, then allow the small set of things the work needs. An allowed list, not a banned list. |
| **Detector** | A program that watches for one narrow thing and reports it. It answers fast, and it answers narrowly. |
| **Detector self-test** | A case that checks the detector can still see a hit. It runs every time, so a broken detector cannot pass as a safe result. |
| **Direct injection** | An instruction you type into the request yourself. Easy to spot, and useful for testing. |
| **Door** | The tool an attack is aimed at. Sending mail, reading a customer record, writing a file. |
:::

::: section | E to H
| Term | What it means |
|---|---|
| **ERRORED** | A result word. A trial did not finish, so it is left out of the count. |
| **Evidence** | A record of what happened in the world: a side effect, a canary token, or an audit row. What the agent said about itself is never evidence. |
| **Evidence file** | The final report, worth 20 points. Three findings, your control before and after, what the assistant got wrong, and what you would learn next. |
| **Evidence pack** | How you report a finding here, in three parts: the claim, the record behind it, and what it does not settle. |
| **Excessive agency** | An agent that can do more than its job needs. One of the selected OWASP risks this course covers, LLM06 in the 2026 release. |
| **Fail closed** | If your control raises an error, the tool call is blocked and the error is recorded. A broken guard that allows everything is worse than one that stops work. |
| **Finding** | One thing you found, written with the record that shows it and the limit on what it settles. An attack that got part way is still a finding. |
| **FLAKY** | A result word. The five trials did not agree with each other. |
| **Four-step scale** | How far an attack got. Your text reached the model, the model followed it, the agent called your door, the action landed. |
| **Gate** | A pass or fail check that keeps later work closed. There are two: the scope and safety quiz, and the scope questions inside the week 1 assignment. |
| **Handle** | The short name you go by on the class board. Results are shown by handle, not by name. |
| **Handover** | The week 5 form where you make the call: was this an incident, what in the pack decides it, what did the assistant get wrong, and what would you do. |
| **Harness** | The program that runs a case five times and prints one result word for it. |
| **Hit** | One trial in which the attack landed, judged from a record rather than from the reply. |
:::

::: section | I to N
| Term | What it means |
|---|---|
| **Indirect injection** | An instruction placed in data the agent will read later, such as a ticket or an article. The person who sends the request has done nothing wrong. |
| **Irreversible action** | An action you cannot undo. Sending mail, deleting a record, charging a card. Reading a file can be repeated with no effect. |
| **Knowledge base article** | Stored internal text the agent can read. Trusted text is still text, so an instruction hidden there reaches the model like any other. |
| **Local model** | A language model running on your own computer. It is the only kind this course uses. |
| **Loop** | The program that sends the conversation to the model, runs the tool the model asks for, and puts the tool's result back into the conversation. |
| **Manifest** | The list of files an assistant is allowed to open. You set one in week 5. |
| **Model** | A program that reads text and writes text. On its own it cannot send, read, or change anything. |
| **NO_HITS_IN_5** | A result word. Nothing landed in five trials, and nothing was refused either. |
:::

::: section | O to R
| Term | What it means |
|---|---|
| **Outbox** | Where the practice target keeps the messages it sent, so you can open them and see who received what. |
| **Practice target** | The small application this course gives you. It runs on your own computer and holds invented customers, tickets and records. |
| **Prediction** | What you expect a run to do, written down before you run it. Written afterwards, it is a description with the surprise taken out. |
| **Prompt** | The text sent to the model. |
| **Prompt injection** | Text written to steer a model that reads it. It is one of the selected OWASP risks this course covers, LLM01:2026, and a named technique in MITRE ATLAS release 2026.07. |
| **Run** | One pass of the agent, from your request to its final answer. Each run writes one trace. |
:::

::: section | S to Z
| Term | What it means |
|---|---|
| **Scope** | What you are allowed to attack. Yours is three things: the practice target, the agent you build, and a model on your own computer. The Rules of Engagement page holds the rule. |
| **Set** | The group of runs you are comparing. In this course a set is five runs. |
| **Side effect** | A change a run left behind in the world: mail sent, a file written, a record changed. |
| **System prompt** | Standing instructions given to the model before your request arrives. They are words, so a rule written there is advice. |
| **Target** | The system a case runs against. Yours is always the practice target, on your own computer. |
| **Ticket** | One unit of work in the practice target, with a body the agent reads. A ticket body is a place an instruction can hide. |
| **Timeline** | The four-column table you ask an assistant for in week 5: claim, time, actor, and the record each claim came from. |
| **Tool** | A function the agent is allowed to call. Tools are how a model reaches anything outside its own text. |
| **Tool boundary** | The point between the model asking for a tool and the tool running. Your control goes here, in code, where the model gets no vote. |
| **Tool description** | The sentence you write to explain what a tool does. The model picks tools by reading these, so the wording changes the choice. |
| **Trace** | The file a run writes, with one line per thing that happened. The trace is the evidence for what the agent did. |
| **Trial** | One run inside a set you are comparing. Five trials is the standard here, because one run settles nothing. |
| **Verdict** | The single word the harness prints for a case. It is a summary, so read the five traces as well. |
| **VULNERABLE** | A result word. The attack landed at least once in the five trials. Once is enough. |
:::

::: callout note | Two pairs students mix up
Accountability is not authorization: a log records an action, and only a check
stops one. Evidence is not assertion: a record shows what happened, and a reply
only says so.
:::
