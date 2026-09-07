::: keyfacts
| | |
|---|---|
| Opens | Day 52 |
| Due | Day 54, 11:59 PM, hard |
| Attempts | One |
| Time limit | Three hours from the moment you open it |
| Open book | Yes. Your repository and these pages |
| AI | Permitted, and you declare it in the field provided |
:::

::: intro
This is the whole study list for the final exam. Nothing off it is on the
exam.
:::

::: callout warning | Memorizing your own lab will not be enough
Some items show an agent configuration you have never run: a config file, a
tool schema, or a few lines of a loop. Name the weakness class in it.

Practice by reading a case file you did not write.
:::

::: section | What the exam covers, by outcome
| Outcome | What the items ask | Reread |
|---|---|---|
| O1 Automate model calls | Change a request. Pull a field from a reply. Predict your retry setting | Week 2 content, `agent/llm.py` |
| O2 Configure and extend | Read a tool schema and say what it allows. Trace one loop pass | Week 3 skeleton, week 4 content, `agent/tools.py` |
| O3 Identify weaknesses | Name the weakness class in a setup you never ran | Weeks 5 and 6 content, the walkthrough |
| O4 Run and read a harness | Read a result table. Say what a rate means. Spot a bad detector | Week 7 reading results, your results file |
| O5 Document and remediate | State an authorization basis. Pick a severity. Choose the fix that holds | Rules of Engagement, the report template |
| O6 Evaluate AI output | Pick the correct function. Find the defect that fails quietly | Week 1 content, your `AI-USE.md` |

Several items ask about numbers only your run produced.
:::

::: section | The three weakness classes you have to name
1. **Prompt injection.** Text the model treats as an instruction when it was
   meant to be data.
2. **Excessive agency.** The agent takes an action nobody approved, and it
   cannot be taken back.
3. **Insecure tool authorization.** The tool never asks who is calling, so any
   caller gets any record.

For each, say what evidence proves it and what fix holds five of five.
:::

::: checkpoint
If one is shaky, you know what to reread.

1. A harness reports 3 of 5 on an attack case. Pass or fail?
2. A rule in the system prompt, or a check in `before_tool_call()`. Which is a
   control?
3. Name the three things you may attack.
4. A tool returns any customer record to any caller. Which weakness class?
5. Where does evidence come from, and where does it never come from?
6. A fix stops the attack but the benign baseline fails. What did you build?
:::
