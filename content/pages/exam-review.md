::: intro
This page tells you what the final exam covers and how it runs. Nothing on it
is new. Every item points back at a page or a lab you have already done.
:::

::: callout note | No new content in this block
The exam does not test anything the course did not teach.

If a topic is not on this page, it is not on the exam. Study from this list and
stop.
:::

::: section | The exam rules
1. It opens on day 52 and is due on day 54 at 11:59 PM. That deadline is hard.
2. You get one attempt.
3. The time limit is three hours from the moment you open it.
4. It is asynchronous. Start it whenever you like inside the window.
5. It is open book. Use your notes, your repository, and these pages.
6. AI use is permitted and you must declare it. There is a field for that.
7. Answers are shuffled, so a classmate's letter answers are useless.

Start on day 52 or day 53, not on day 54. If your power or your internet fails
on Friday, the deadline still stands.
:::

::: callout warning | Memorizing your own lab will not be enough
Some items show you an agent setup you have never run. It might be a short
config file, a tool schema, or a few lines of a loop.

You have to name the weakness class in it.

That is deliberate. The outcome says identify a weakness. It does not say run
an attack somebody handed you. Practice by reading a case file you did not
write.
:::

::: section | What the exam covers, by outcome
Every item is tagged to one of the six course outcomes. Here is what each one
asks of you, and where to reread.

| Outcome | What the items ask | Reread |
|---|---|---|
| O1 Automate model calls | Change a request. Pull a field out of a reply. Predict what your own retry setting does | Week 2 content page, and your own `agent/llm.py` |
| O2 Configure and extend | Read a tool schema and say what it allows. Trace one pass of the loop | Week 3 annotated skeleton, week 4 content page, your own `agent/tools.py` |
| O3 Identify weaknesses | Name the weakness class in a setup you have never run | Week 5 content page, week 6 content page, the week 6 authorization walkthrough |
| O4 Run and read a harness | Read a result table. Say what a rate means. Spot a detector that proves the wrong thing | Week 7 reading results page, your own results file |
| O5 Document and remediate | State an authorization basis. Pick a severity. Choose the fix that holds | Rules of Engagement, the findings report template |
| O6 Evaluate AI output | Pick the correct function out of several. Find the defect that fails quietly | Week 1 content page, your own `AI-USE.md` |

Rereading your own run files matters more than rereading the pages. Several
items ask about numbers only your run produced.
:::

::: section | The three weakness classes you have to be able to name
These come back on the exam more than anything else. Say each one out loud in
one sentence before you sit down.

1. **Prompt injection.** Text the model treats as an instruction when it was
   meant to be data. It arrives directly from a user, or indirectly from
   content the agent reads later.
2. **Excessive agency.** The agent takes an action nobody approved, and the
   action cannot be taken back.
3. **Insecure tool authorization.** The tool never asks who is calling, so any
   caller gets any record.

For each one, be ready to say what evidence would prove it, and what fix would
hold five times out of five.
:::

::: section | One item you can prepare for exactly
On the Module 0 Gate you wrote a paragraph. It answered this question: in your
own words, what is the one thing you may never do in this course?

The exam quotes your own paragraph back to you. Then it asks you to judge it
now, with seven weeks of work behind you.

Reread the Rules of Engagement before you start. Clause 1 and clause 2 are the
ones that carry points.
:::

::: checkpoint
Answer these for yourself. If any one is shaky, you know what to reread.

1. Your harness reports 3 of 5 on an attack case. Is that a pass or a fail, and
   why?
2. A rule in the system prompt, and a check inside `before_tool_call()`. Which
   one is a control?
3. Name the three things you may attack.
4. You are shown a tool that returns any customer record to any caller. Which
   weakness class is that?
5. Where does evidence come from, and where does it never come from?
6. A fix stops the attack but the benign baseline now fails. What did you build?
:::
