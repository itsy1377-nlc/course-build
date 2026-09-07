::: intro
The course is over. Here is what you built, what you have to show for it, what this course did not cover, and where the work goes next.
:::

::: learned | What you learned
You built one agent. Each week added one capability to it, and nothing was thrown away.

| Week | What you added |
|---|---|
| 1 | Your code sends text to a model and reads the answer back |
| 2 | The answer arrives in a fixed shape, your code checks it, and asks again when the shape is wrong |
| 3 | The model judges facts you pulled out of the email, not the raw message |
| 4 | The model may ask for three lookups, and your code runs them |
| 5 | The agent picks its own next step, inside a cap, and stops when it has enough |
| 6 | Four guardrails stand between a bad answer and a bad action |
| 7 | Every judgment becomes a six-line note, and twenty of them are scored |

What you finished with reads a reported email and checks the facts in it. It decides what to check next. It writes a note another analyst can act on, and it carries a number saying how often it was right.
:::

::: did | What you did
Seven export files, one a week. Each one is the record of a run you made.

| Week | File |
|---|---|
| 1 | `week1_first_calls.txt` |
| 2 | `week2_classification.json` |
| 3 | `week3_grounding.json` |
| 4 | `week4_tool_calls.json` |
| 5 | `week5_loop_trace.json` |
| 6 | `week6_guardrails.json` |
| 7 | `week7_triage_report.txt` |

Behind those seven files sit seven sidebars, seven labs, seven discussions and seven self-checks.
:::

::: checkpoint | What this course did not cover
Seven weeks is a narrow slice. Knowing where its edges are is part of knowing what you built.

- **One kind of input.** Reported email, and nothing else. Week 1 named alerts, logs, endpoints and networks. You worked on none of them.
- **One model, called one way.** The course never covered how a model is built or trained, and you never changed one.
- **A notebook, not a service.** Your agent runs when you run it. Nothing starts it on a schedule, and nothing files its notes into a real ticket.
- **Invented mail, fixed lookups.** The three tools read a file that ships with the course. Neither the mail nor the lookups came from a live system.
- **Twenty emails is a small measurement.** Real accuracy work uses far more, and it is repeated as the mail changes.
- **A narrow slice of Python.** The course left out files, packages, classes and the command line on purpose.
- **The agent's own security.** The course set three things for you: who may run it, where its key lives, and what it records for a later review.
- **What happens after escalation.** The investigation, the response and the report a team writes come after the point where your agent stops.
:::

::: next
**Keep your files.** Your work sits on the notebook server until the term closes. Before the last day, download the seven export files and your notebooks, and put them somewhere you control. They are yours.

They are also evidence. If someone asks whether you have used AI on real work, hand them `week7_triage_report.txt`. It holds twenty judgments and the score behind them.

**Where this goes in a security job.** A first analyst role is mostly four jobs. Read reported mail. Check what a header really says. Write the note that goes in the ticket. Know which cases a person has to see. You did all four this term. The tools change from one employer to the next. Those four questions do not.

Four habits are worth keeping. Pull the facts before you judge. Check the shape of an answer before you read it. Ask who verified a claim before you act on it. And put a number on how often you are right.

Thank you for the term.
:::
