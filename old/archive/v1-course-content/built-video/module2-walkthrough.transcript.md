# Registered is not allowed

A text version of the walkthrough video. Every word spoken, in order.

## Registered is not the same as allowed

> The grader is a command you can run
> as often as you like.

This is what a finished Module 2 run looks like. You will see the tool that grades you, and one failure that looks like broken Python. You will not see any code, because the code is yours.

## One of them is new work

1. **Part one.** get_customer. The schema is already written for you.
2. **Part two.** A tool of your own. The schema is the graded part.

Module 2 has two parts. Part one is get_customer. Its schema is already written for you. Part two is one tool you design yourself. There, the schema is the graded part, not the Python. Writing a function is Week 4 work. Writing an interface another program has to understand is new. The model reads your description and nothing else.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module2.py -q | tail -3`

The grader is a command, and you may run it as often as you like. Run it before you write anything, so you know what failing looks like. Five failed, one passed, seven skipped. The seven skipped are waiting for the tool you have not written yet. That is a starting line, not a problem.

## At the terminal

Commands run, in order:

- `python -m pytest tests/test_module2.py -q`

Now the same command against work that is finished. Thirteen passed, in well under a second. It is the same tool that grades you. So nothing is waiting to surprise you at the deadline.

## At the terminal

Commands run, in order:

- `grep -A6 "allowed_tools:" config/lab.config.yaml`
- `python -m agent.cli "summarize ticket T-501"`

Your tool name has to go in two places. Here is the allowed list in the config file, with a new name on the end. That name was never added to TOOLS, the registry in your tools file. Now run the agent. It stops before it asks the model anything. The error names the tool that is missing, then every tool that is registered. Miss the other list instead and your tool is never offered to the model. The model never picks it, and nothing looks broken at all.

## At the terminal

Commands run, in order:

- `python -m agent.cli "summarize ticket T-501"`

Here is a good run. T-501 is an ordinary ticket with nothing hidden in it. The agent ran search_tickets and read the ticket back. Save this whole output. It is the run transcript the assignment asks for.

## At the terminal

Commands run, in order:

- `python -m agent.replay | head -13`

Replay walks that same run one step at a time. You asked for a summary. The model asked for a tool, and the line under it says nothing in your program chose that. Then your code ran the tool and got back two hundred and thirty six characters. The model asks. Your code answers.

## The three failures that cost the most points

1. A schema that lies about the function
2. A tool registered but not allowed
3. An empty string when the call fails

Three failures cost the most points here. A schema that lies about your function. The autograder builds arguments from your schema and calls your function with them. A tool registered in one list and not the other. And an empty string when the call fails. The agent carries on as if it worked, and your log agrees with it.

## One zip, five things.

> tools.py, lab.config.yaml, your run transcript,
> ANSWERS.md and AI-USE.md. No .env, no runs folder.

One zip file, holding five things. Your tools file, your config file, your run transcript, ANSWERS and AI-USE. No dot env file, and no runs folder. AI-USE needs one suggestion you turned down, with a real reason. It was wrong is not a reason. It caught every exception, which would have hidden the missing customer case, is a reason.
