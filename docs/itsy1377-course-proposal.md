# ITSY 1377 Agentic AI and Security Operations: proposed outcomes

Seven weeks. No prerequisite. No certification mapping. Introductory by
design: broad and light, and hands-on throughout.

This replaces two earlier designs, both archived. The first chased a
certification blueprint; the second was built around NCAE-C knowledge units
and a scripting prerequisite. Neither constraint applies now.

---

## 1. The course in one sentence

**Students run a real AI agent on their own machine, catch it doing three
things nobody authorized, and prove each one with evidence a stranger can
check.**

Everything else follows from that. The agent is a helpdesk assistant with
tools: it reads tickets, looks up customers, searches a knowledge base and
sends mail. It has the problems real deployments have, and the course is
about noticing them and proving them rather than guessing.

## 2. Proposed learning outcomes

Six, measurable, each with the artifact that assesses it.

| # | Outcome | Assessed by |
|---|---|---|
| **1** | Describe how an agentic AI system works, and trace a recorded run to identify each model decision, each tool call, each untrusted input, and the point at which an action can no longer be undone. | An annotated trace of the student's own agent run |
| **2** | Given an agent's tools and configuration, classify each available action by what it reads, what it changes, whether it can be reversed, and who approves it. | A four-row tool and blast-radius inventory |
| **3** | Conduct authorized testing against an instructor-provided target, within a written scope, and demonstrate common agentic failure modes including disclosure of a system prompt, an irreversible action taken with no approval, and a privileged action taken with no authorization check. | Three evidence packs, one per failure mode |
| **4** | Support every reported finding with a recorded system side effect, an audit record, or a planted token, and reject a claim whose only support is the agent's own account of what it did. | The evidence line in each pack, plus a teardown of a supplied results file that overstates what it found |
| **5** | Run a repeated-trial test harness and interpret its output as rates rather than verdicts, distinguishing a failure caused by the model from a failure caused by a missing control, and an attack that failed from a test that never ran. | A full harness report from the student's own machine, with a written reading of it |
| **6** | Implement one control at the agent's tool boundary and verify with paired before-and-after runs that it stops the unauthorized action without breaking authorized use, and contrast that with the same rule written as an instruction in the agent's prompt. | The edited control, two harness reports side by side, and the prompt-only attempt that did not hold |

**On the wording.** Outcomes 3 through 5 are the heart of the course and they
describe security testing, so they are written the way a curriculum committee
needs to read them: authorized, scoped, against an instructor-provided target.
Outcome 1 and outcome 2 lead with description and analysis on purpose, because
they come first in the term and because they are what the course is really
about. Outcome 6 is the only one that requires writing code, and it is four
lines.

## 3. Week by week

| Wk | Title | What the student does | Artifact |
|---|---|---|---|
| 1 | Read the machine, not the language | Get the environment running. Run one ordinary request and read the replay in plain English. Annotate which line was the model deciding, which was code running, which could not be undone. Read two short scripts a coding assistant wrote and say what each one touches | Annotated trace; Rules of Engagement gate at 100 percent |
| 2 | What can it actually do | Read the agent's tool registry and its settings. Build the inventory: what each action reads, what it changes, whether it can be taken back, who finds out. Find, in the source, the one action with no way back | Tool and blast radius inventory |
| 3 | Make it talk | Ask the agent to repeat its own instructions. Watch it hand over a credential somebody stored there for convenience. Run it five times and report the rate, including the run where it refused | Evidence pack 1: disclosure |
| 4 | Make it act, make it fetch | Ask it, politely and with no trickery, to mail an outside address; nobody approves it. Then run as a support agent with no business seeing a particular customer, and get the record anyway. Open the source and find the check that is missing. Read the audit row and notice whose name is on it | Evidence packs 2 and 3 |
| 5 | Rates, not vibes | Run the whole harness. Read every part of what it prints: the provider banner, the scope refusal, the detector self test, the controls. Post your rate for week 3 on the class board and look at the spread. Take apart a supplied results file that claims more than it found | Harness report with a written reading; results teardown |
| 6 | Your case, your name on it | Write an attack case of your own against a different door. Predict the outcome in writing before running it. Report what actually happened, including a prediction that was wrong | A student-authored case, the prediction, the run |
| 7 | One rule that holds | Try to stop the disclosure by adding a firm instruction to the prompt. Measure it; it does not hold. Then add one control in code at the tool boundary. Measure again. Confirm the benign case still works | The control, paired before and after reports |
| Final | The evidence file | Assemble three findings on fixed headings, each tracing to a recorded check, plus the fix and its before and after | The report; a short exam |

**Week 1 answers the coordinator's scripting ask without becoming a
programming course.** Nothing is written from a blank file. The student reads a
recorded run rendered as numbered English, then reads two short scripts and
answers one question about each: what does this touch, and can it be undone.
That is recognition, which is what was asked for.

## 4. Three problems in this design, and how each is handled

Three independent reviews of four competing designs converged on the same
three, so they are written down rather than discovered later.

**Weeks 3 and 4 risk being the same assignment twice.** Run a shipped case,
read the rate, paste the evidence. The fix is that each week does a different
kind of work: week 3 is a model failure that varies run to run, week 4 is a
system defect that lands every time and has to be found in the source rather
than pointed at. The class board in week 5 is where the two become one lesson.

**Every graded week from 3 onward needs a model running locally.** That is a
real risk for a student on a locked-down laptop, and the assumption that a
college loaner will run the no-install bundle is untested.
**So the course ships instructor-recorded evidence bundles as a fallback for
weeks 3 through 5.** A student whose machine will not run the model does the
same analysis on a real recorded run, produces the same artifacts, and is
graded the same. This costs one build script and it removes the single largest
equity risk in the design.

**Six outcomes about making software misbehave is a syllabus optics problem,
in a course open to students under 18 whose parents may read it.** Handled by
the wording in section 2, by the scope document being week 1 and itself graded,
and by outcome 6 being remediation. It is worth naming to the committee rather
than hoping nobody asks.

## 5. Portfolio: optional, ungraded, and separate

Students produce three things as ordinary graded coursework. **Packaging any of
them for a portfolio is optional and carries no points**, because not every
student wants one and nobody should be graded on choosing.

| Artifact | Why it is worth showing |
|---|---|
| The evidence file | A short assessment report on a live agentic system, every claim traced to a recorded check. Most entry-level portfolios have nothing like it |
| One case, five trials | The student's own test case, the prediction written before the run, and the observed rate. It shows judgment under uncertainty, including a prediction that was wrong |
| A three-minute walkthrough | From an ordinary-looking request to the proof. Optional, and the one most students will enjoy making |

Two things the optional module has to teach, because both are real: the canary
tokens in a student's evidence are derived from their college ID and must be
scrubbed before anything is published, and the repository needs a licence
before anyone is encouraged to publish from it.

## 6. What makes this different from what other schools teach

Stated honestly, because parts of it are common.

Not distinctive: prompt injection demonstrations, AI policy discussion, and
"try to jailbreak a chatbot" appear on many syllabi.

Distinctive, specifically:

- **The student is responsible for the agent, not attacking someone else's.**
  Almost all agentic AI security teaching is offense-shaped. This is the job
  the market is creating.
- **Findings are graded on side effects, not on what the model said.** The case
  format will not accept a text-match detector. A student reports "4 of 5 with
  the token pasted", never "it worked".
- **Evidence cannot be copied.** Tokens are derived per student, so a classmate
  can share a working payload, which is fine and is how the field works, and
  cannot share the proof that it worked in your environment.
- **It runs on a locked-down laptop with no account, no key and no internet.**

## 7. What has been verified, and what has not

**Verified by measurement**, on the model the course would ship, over 46 agent
runs on the real student path: the agent discloses its system prompt and the
credential in it 4 times in 5; it sends mail outside the company with no
approval 5 times in 5; any caller can read any customer record 5 times in 5,
with the audit log recording it perfectly and stopping nothing.

**Not verified:** that a college loaner will execute the bundle. That is a
policy question for whoever owns the image, and the recorded-evidence fallback
in section 4 is what makes the course survive a no.

**A limit worth stating to students in week 1:** indirect prompt injection, the
attack everyone has heard of, does not reliably complete on a small local
model. Hidden instructions do steer the agent into fetching a record it was not
asked for; the final step does not land. The course teaches that as a real
result about a real system rather than pretending otherwise, which is a better
lesson than a staged success.
