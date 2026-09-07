# Prove it runs, then predict

A text version of the walkthrough video. Every word spoken, in order.

## Prove it runs, then predict

> Two jobs. This video shows the first one,
> and none of your five predictions.

Lab 1 asks you for two things. This video shows the first one. Nothing here needs an API key. It all runs offline. You are not graded on whether every check passed. You are graded on running it and showing the result. Two failed checks with honest pasted output beat a submission with nothing pasted.

## At the terminal

Commands run, in order:

- `python verify_env.py | sed -n '1,15p'`

Run python verify env dot p y from the folder that holds it. The full output runs past one screen, so this shows the top. Nine checks print, one per line, each with a symbol. Python version passes. Then the virtual environment check warns. It says you are not in a virtual environment. A warning is not a failure, and the lab still runs. The arrow under it prints the fix, python dash m venv dot venv. Then you activate it with the line for your own system. The other seven checks all pass here. Packages, the settings file, and no key stored in it. Your canary tokens, the target files, and saving a file. The last check runs the agent, and it answered in one step.

## At the terminal

Commands run, in order:

- `python verify_env.py > verify-output.txt`
- `tail -n 9 verify-output.txt | sed -E 's/M0-.{5}-.{5}/M0-XXXXX-XXXXX/'`

Now save the output, because the assignment asks you to paste it. The redirect writes it to a file, so nothing prints here. Then read the end of that file, which is the part you need. Everything passed, and then your Module 0 Gate code. The pipe into sed hides my code on purpose. Yours comes from your student ID, so no two are the same. Copy the whole line, including the letter after the last hyphen. Paste it into the Module 0 Gate in Canvas. It is due on day 3, and it is your attendance check for the term. The last lines look ahead to week 2, when you have an API key. Run this again with dash dash live and submit the code ending in L.

## At the terminal

Commands run, in order:

- `python verify_env.py`
- `cd ..`
- `python verify_env.py | sed -n '1,3p'`

Here is the failure that costs the most time and is not a real failure. The same command, run from the wrong folder. Python cannot find the file, and it prints the path it tried. Move back one folder and run it again. It works, and the check starts printing. If a command cannot find something, check your folder first. Nine times out of ten, that is the whole problem.

## At the terminal

Commands run, in order:

- `python -m common.canary | sed -n '1,4p'`

One more command. Run python dash m common dot canary. It prints three tokens. Sysprompt, customer, and kb. The dash m flag runs a module by its dotted name. That flag is what makes the lab import lines work. Your three tokens are built from your student ID, so a classmate has three different ones. You will hunt these tokens as evidence in Week 5.

## What the grader is looking for

1. **Loses points.** Running the code first, then writing your prediction. Describing the output in a sentence instead of pasting it.
2. **Full credit.** A prediction written first, one sentence on why, and the real output pasted underneath.

Two easy ways to lose points here, and both are avoidable. The first one is predicting late. Running the code first, then writing that you predicted it. That is the one thing this lab is built to catch. Predicting badly is fine. Predicting late is not. A wrong prediction you explain in one sentence earns full credit. The second one is describing output instead of pasting it. Several graded rows are the paste itself.

## One file, four parts, in order.

> Environment check output. Five predictions with
> reasons, then the real output. Dictionary output.
> Three written answers.

One file, four parts, in this order. Your environment check output, then your five predictions with reasons and the real output. Then your dictionary output, then your three written answers. That order is the order the grader reads. Do not upload the two python files. Everything the grader needs is pasted inside the one file. If setup fights you for thirty minutes, post the whole output and start Part 2 anyway.
