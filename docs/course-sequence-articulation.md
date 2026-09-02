# AI Fundamentals into ITSY 1377: how the two courses fit

AI Fundamentals is sequenced before ITSY 1377 Agentic AI and Security
Operations. This is what each should assume of the other, what must not be
taught twice, and the one place they currently collide.

Read against the AI Fundamentals course objectives document (fourteen
objectives) and the ITSY 1377 proposal (seven outcomes).

---

## 1. The one real collision, and it is fixable in a sentence each

**AI Fundamentals objective 6** is "Evaluate AI-generated content for accuracy,
quality, bias, and fitness for purpose", including "Identify common AI errors
and hallucinations". **Objective 12** includes "Select appropriate methods to
verify AI outputs".

**ITSY 1377 outcome 7** is "Evaluate AI-generated output against source
evidence".

A reviewer will read those as the same outcome taught twice, and they are not.
The distinction is worth stating in both syllabi in these words:

| | The question it teaches |
|---|---|
| **AI Fundamentals** | Does this output look wrong? Judged from the content itself: internal contradiction, implausibility, obvious bias, a citation that does not exist |
| **ITSY 1377** | Does the record support this claim? Judged from a source the output does not control: an audit row, a file, a log |

**Plausibility, then provenance.** The first is available to anyone reading
carefully. The second requires evidence that exists independently of the thing
being checked, and it is what a security analyst does. One is a reading skill;
the other is an investigative one. Naming it that way makes the sequence read as
escalation rather than repetition.

---

## 2. What ITSY 1377 should stop teaching, because Fundamentals already does

**Prompting.** Objectives 4 and 5 cover role, task, context and format
structures, multi-turn interaction, and iterative refinement. ITSY 1377 should
assume all of it. That directly improves the course: week 3 asks a student to
hide an instruction inside a document, and a student who already knows how to
construct a prompt can spend that week on placement, wording and evasion rather
than on prompt basics.

**What AI is, and what generative AI is.** Objective 1. ITSY 1377 opens by
demonstrating an agent, not by defining a model, and that only works if the
definitions are already behind them.

**The ethics and disclosure frame.** Objectives 3, 8 and 12 cover bias, privacy,
intellectual property, academic integrity and disclosure of AI use. ITSY 1377
needs an AI use policy but should adopt the same one rather than author a
second, and should reference it rather than re-teach it.

**Career framing.** Objective 14 covers résumés, job descriptions and skill
planning. ITSY 1377's optional portfolio module should point at that work rather
than duplicate it.

---

## 3. What AI Fundamentals should set up, because ITSY 1377 will land on it

**Objective 11 is the bridge, and it is currently the weakest-defined one.**
"Define common AI-supported workflow patterns and the role of human-in-the-loop
oversight", including "Explain human-in-the-loop oversight for AI agents and
automation."

That objective is at Explain. Everything ITSY 1377 does is the Apply and
Analyze version of it: outcome 3 determines what an agent can reach and what
cannot be undone, and outcome 6 puts a control at the boundary and measures
whether it held. If objective 11 is taught as a definition, the sequence works.
If it is taught thinly, ITSY 1377 has to spend a week rebuilding it.

**Objective 13's "prompter, verifier, editor" is worth teaching deliberately**,
because ITSY 1377 is seven weeks of being the verifier. Naming the role in
Fundamentals and inhabiting it in ITSY 1377 is the cleanest thread between the
two courses, and it costs nothing.

**Objective 2, "when AI should not be used", is the other one to protect.** ITSY
1377 outcome 7 ends with the student naming a task they would and would not give
an agent. That is objective 2 applied to a system that can act rather than
answer.

---

## 4. Four cheap things that would make the pair work as a sequence

**A shared vocabulary page, maintained once and used by both.** Hallucination,
verification, disclosure, human in the loop, agent, tool, prompt. Two courses
that define the same word differently is the fastest way to make a sequence feel
like two unrelated classes.

**One AI use policy, written for Fundamentals and adopted by ITSY 1377.**
Students should not meet two sets of rules about the same behaviour. ITSY 1377
adds scope rules about what may be tested, which is a different subject and
belongs to it.

**One shared worked example, appearing in both.** The helpdesk agent ITSY 1377
uses could be the illustration of human-in-the-loop oversight in Fundamentals
objective 11: here is an assistant that reads tickets, looks things up and sends
mail, and here is where a human approves. Students then arrive in ITSY 1377 at a
system they have already had described to them, and week 1 gets to skip the
setup and go straight to making it misbehave.

**A handoff artifact.** Students finish Fundamentals with a short statement of
how they use AI and how they verify it, from objective 12. ITSY 1377 week 1 asks
them to apply that same statement to a system that takes actions rather than
producing text, and to say what changes. That is fifteen minutes, it makes the
prerequisite feel real, and it opens the course on something the student wrote.

---

## 5. What neither course covers, stated so nobody assumes it

Neither teaches programming. Fundamentals does not, and ITSY 1377 teaches
recognition only: six pieces of syntax and four questions to ask of a script.
A student finishing both can read a short script and say what it touches. They
cannot write one, and no document in either course should imply otherwise.

Neither covers the operational security stack: SIEM, endpoint tooling, network
forensics, malware analysis. ITSY 1377 is one elective sitting beside those in
the Cyber Defense plan, not a replacement for any of them.

---

## 6. The sequencing argument, in one paragraph

AI Fundamentals teaches a student to use AI well and to be sceptical of what it
tells them. ITSY 1377 teaches them that an agent does not merely tell them
things, it does things, and that the difference is the whole of the security
problem. The first course ends with a student who checks whether an answer looks
right. The second ends with one who can prove what a system actually did, and
who has built a control that stopped it. That is a real escalation and it is
worth saying in both catalogue descriptions, because it is the reason to take
them in order.
