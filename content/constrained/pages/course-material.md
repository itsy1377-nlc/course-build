::: keyfacts | The short version
| Question | Answer |
|---|---|
| What does this course cost? | Nothing |
| Do I need a credit card? | No. Not at any point, for any part |
| Do I need an account anywhere? | No sign-up, no key, no paid service |
| Is there a textbook? | No. The course pages are the reading |
| What do I need? | Python, a model runner, a small model, the lab folder, an editor |
| Do I need administrator rights? | No |
| What if my laptop is locked down? | There is a bundle that installs nothing |
:::

::: intro
This page lists everything you need for the course and what each part costs. The
total is zero. All of it is free and open source, and you keep it when the course
ends.
:::

::: callout note | Nothing here is metered
No part of this course sends your work to a paid service. There is no key to
buy, no usage to watch, and no free trial that runs out. If a page ever seems to
ask you for money, stop and post on the Questions and Answers board.
:::

::: section | What you need, and what each part costs
| What | Why you need it | Cost and licence |
|---|---|---|
| Python 3.11 or newer | Runs the agent, the practice target, and the test harness | Free, PSF licence |
| A model runner | Runs a language model on your own computer | Free, MIT licence |
| A small language model, about 2 GB | The model your agent talks to | Free, Apache 2.0 licence |
| The lab folder | The agent, the practice target, and the test harness | Provided with the course |
| A text editor | Reading code, and changing a few marked lines | Free. Any editor you like |

The week 1 setup walkthrough gives the exact steps for Windows, macOS, and
Linux. Follow it in order, and install nothing else first.
:::

::: section | What your computer needs
- About 3 GB of free disk space for the model, plus room for the lab folder.
- About 3 GB of free memory while the model is running.
- Windows, macOS, or Linux. All three are supported.
- No administrator rights. Nothing here installs into the system.

An older laptop is slower, not blocked. One request may take several seconds to
answer. That costs you patience, not points.
:::

::: section | Check that setup worked
Run one command when you finish the setup walkthrough:

```
python verify_env.py
```

It prints **ready** when everything is in place. If it prints anything else,
copy that text onto the Questions and Answers board. Do not start week 1 until
it prints ready.
:::

::: section | If your laptop refuses installers
Some college and work laptops block installers. There is a second path and it is
supported.

Your instructor can give you a bundle of about 2 GB that installs nothing. You
copy it into your own user folder and run it from there. It carries the model
runner, the model, a copy of Python, and the lab folder.

Ask for it on the Questions and Answers board. Ask in week 1, not in week 4.
:::

::: section | If your computer cannot hold the model
A smaller model, about 500 MB, will run everything in this course. It costs you
something real, so here is the honest trade.

The small model still shows the problems that come from tools and permissions,
which is most of the course. What it does not show is the model itself giving
way. Week 1 asks the agent for something it should not hand over, and the small
model will usually refuse.

Use it if you need it, and tell your instructor that you did. Your results will
differ from your classmates, and week 7 compares results across the class.
:::

::: callout warning | Nothing here reaches the internet
The practice target runs on your own computer and stays there. Mail it sends is
written to a folder on your disk. Keep it that way: no real data goes in, and it
never goes on a network.
:::

::: section | There is no textbook
The course pages are the reading. Where a week needs a professional document,
that week's Content page names it and says which part to read.

Nothing you are asked to read costs money. Keep your own notes in one file from
week 1. You reuse them in the evidence file at the end.
:::

::: section | What you keep afterwards
The licences on this software let you keep using it after the course. The model
runner is MIT. The model is Apache 2.0. Python is under the PSF licence.

The pages your instructor wrote are released under CC BY 4.0, so you keep those
too. None of that is true of a rented account, which is one reason this course
does not use one.
:::
