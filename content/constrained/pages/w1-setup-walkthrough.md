::: intro
This page gets your own computer ready for the course. Work through the steps in
order. Each one says what success looks like, and what to do when it does not
work.
:::

::: callout time | How long this takes
| Part | Minutes |
|---|---|
| Python and the lab folder | 15 |
| The packages | 10 |
| The model, including the download | 30 to 60 |
| Settings and the two checks | 20 |
| **Total** | **75 to 105** |

The model download is the slow part, and your internet speed decides it. Start
early in the week. Day 4 is the deadline, not the plan.
:::

::: callout note | Two hours is normal
Setup is the hardest part of week 1 for most students. Two hours is a normal
first pass, and slower than that happens too.

**A slow setup is not a sign that you do not belong here.** It says nothing
about how you will do in this course. Everybody taking this course meets an
error message they have never seen before. The skill is not avoiding them. The
skill is reading one line at a time and asking for help with the exact text.
You will do that all term.
:::

::: section | What you are setting up
Four pieces, and nothing else.

| Piece | What it is |
|---|---|
| Python | The language the labs are written in |
| The lab folder | The agent, the practice target, and the test runner |
| A model on your computer | The thing your agent asks for decisions |
| The practice data | Invented customers and tickets for the target |

After the downloads, none of this reaches the internet. The model runs on your
machine and the practice target listens on your machine only.
:::

::: steps | Do this now
1. **Check your Python version.** In a terminal, run `python3 --version` on
   macOS or Linux, or `py --version` on Windows. Done when it prints 3.11 or
   higher. If the number is lower, or the command is not found, install Python
   from the link in the Week 1 module in Canvas.

2. **Get the lab folder.** Download it from the Week 1 module and unzip it. Put
   it somewhere you can write, such as your Documents folder. Done when the
   folder holds `verify_env.py`. A network drive or a locked system folder will
   fail later, so move it now rather than at step 9.

3. **Open a terminal in that folder.** Done when listing the folder shows the
   lab files. Use `ls` on macOS or Linux, and `dir` on Windows. If you see
   something else, you are in the wrong folder.

4. **Make a virtual environment.** This keeps the course's packages apart from
   the rest of your computer. Run `python3 -m venv .venv` on macOS or Linux, or
   `py -3 -m venv .venv` on Windows.

5. **Turn the virtual environment on.** Run `source .venv/bin/activate` on macOS
   or Linux, or `.venv\Scripts\activate` on Windows. Done when your prompt
   starts with `(.venv)`. If Windows refuses to run the activate script, post
   the exact message on the Questions and Answers board.

6. **Install the packages.** Run `pip install -r requirements.txt`. Done when it
   finishes and lists what it installed. If your computer has no internet, ask
   your instructor for the offline package folder and use
   `pip install --no-index --find-links wheels -r requirements.txt` instead.

7. **Install Ollama.** This is the program that runs a language model on your
   own computer. The download is in the Week 1 module. Done when
   `ollama --version` prints a version number.

8. **Start it and download the model.** Run `ollama serve` in a second terminal
   window and leave that window open. Back in your lab terminal, run
   `ollama pull granite4.1:3b`. Done when `ollama list` shows that model. The
   download is about 2 GB, so give it time.

9. **Point the labs at your model.** Open `config/lab.config.yaml` in a text
   editor. Change `provider: mock` to `provider: openai_compatible`, and change
   the `model:` line to `granite4.1:3b`. Save it. Done when both lines read that
   way. Never put a password or a key in this file. A model on your own machine
   needs neither.

10. **Run the environment check.** Run `python verify_env.py`. Done when nine
    checks print and a short gate code appears at the end. Paste that code into
    the scope and safety gate in Start Here. Any check that fails prints an
    arrow line under it saying what to do.

11. **Check that the model answers.** Run `python verify_env.py --live`. Done
    when the last check reports that the model answered `ready`. If it waits and
    then gives up, make sure `ollama serve` is still running in its own window.

12. **Build the practice data.** Run `python -m target.seed`. Done when it prints
    `Database rebuilt` and lists the canary tokens it planted for you. If it
    cannot write, move the lab folder into your Documents folder and run it
    again.
:::

::: section | If your laptop will not let you install things
Some college laptops are set to run programs only from certain folders. That is
a policy on the laptop. You have not broken anything, and there is a path for
you.

1. Ask for the course bundle on the Questions and Answers board. Ask in week 1,
   not in week 4. Nothing in it is installed.
2. Copy the whole folder into your Documents folder.
3. Double-click `start-here.cmd`. It starts the model and opens a command window
   already inside the lab folder.

Then join the list above at step 9. If Windows blocks the bundle, write down the
message you saw and message your instructor. Do not look for a way around it.
:::

::: callout note | If 2 GB is too much for your computer
There is a smaller model the labs still run on: `qwen3:0.6b`, about a quarter of
the size. Pull it the same way, and put that name on the `model:` line instead.

**It costs you something real.** Some attacks that work on the larger model do
not work on this one, so your runs will show less. That is a fact about the
model, not about your work. Name the model you used in every assignment, so your
instructor reads your evidence correctly.
:::

::: section | When something goes wrong
| What you see | What to do |
|---|---|
| `command not found` | Wrong folder, or the virtual environment is off. Turn it on again |
| A check prints `FAIL` | Read the arrow line under it. It names the fix |
| A warning about a demo student ID | Expected in week 1. You set your own before week 5 |
| The model download stops partway | Run the pull command again. It picks up where it stopped |
| The live check waits, then gives up | The model runner is not running. Start it again |
| Two hours have gone and nothing works | Stop. Post on the Questions and Answers board |
:::

::: callout warning | How to ask for help well
Post the text, never a photograph of your screen. Copy the whole output of the
environment check, from the first line to the last.

Then add two sentences: what you expected, and what you tried already. That is
the same shape as every report you write this term. A question in that form
usually gets answered the same day.
:::

::: sources | Sources
Written for this course. Every command on this page is one you run inside your
own lab folder, and the environment check tells you what it looked at.
:::
