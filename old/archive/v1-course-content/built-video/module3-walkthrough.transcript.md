# Six things to capture

A text version of the walkthrough video. Every word spoken, in order.

## Six things to capture

> Run it as it ships, and read every line.
> This video runs one case. Your run does all of them.

Module 3 asks you to run the harness exactly as it ships. Do not pass a case flag. Do not pass a trial count. Do not edit a case file. You are reading the tool this week, not changing it. This video does pass a case flag, so you see one case instead of a whole run. Nothing on screen here is your submission. Capture all six items from your own report, not from this video. Your own run takes a while, because the harness pauses between trials. Start it early.

## At the terminal

Commands run, in order:

- `python -m harness.runner --list`

Start by seeing which cases ship with the harness. The list flag prints the cases and runs none of them. Eight cases. Six attacks, and two controls. Every line gives you an id, a kind, and a title. Note that total, because your report says how many cases ran.

## At the terminal

Commands run, in order:

- `python -m harness.runner --case control-benign-baseline --case control-benign-escalation-works --case A4-excessive-agency-no-confirmation`

Here is the run. Read it from the top. The banner names the provider, your student ID, the target, and the case counts. This provider is mock, and the line says its results are not evidence about a real model. Then the detector self-test line. It carries a probe count and an OK. Then the two controls, both OK. The escalation control shows X marks, because there the mail is supposed to go out. Then the attack case. Five X marks, one per full agent run. The status lands. Vulnerable, five out of five. Then the two report files this run wrote, and a count of each status.

## Why a run can stop with nothing printed

1. The detectors test themselves, in both directions
2. Two controls run before any attack case
3. If one fails, no attack results print at all

The self test is the harness proving itself before it grades anything. A detector has to fire when the attack clearly happened, and stay quiet when nothing did. Then the two controls run, ahead of every attack case. If a control fails, the run stops and no attack results print. Numbers from a tool that cannot pass its own test are not numbers. A run that stopped is a real finding about your environment. It is worth more than a made up table.

## At the terminal

Commands run, in order:

- `ls -1 runs/reports/`
- `grep -A 5 "Scope" runs/reports/*-results.md`
- `grep -B 8 -A 2 "side_effect.email_sent" runs/reports/*-results.md`

Every run writes two reports, one JSON and one markdown. Everything you capture is already in there, so paste from the markdown instead of retyping. Start with the scope section. Discovery found a second address, and the harness refused to touch it. That refusal is one of the six items. Copy it from your own report. Now the block for the case this video ran. Result, vulnerable. Landed in five of five completed trials. Then the framework identifiers, and the detector that decided it. Read the evidence line as a sentence. An outbox file, addressed to a records archive outside the company. That line describes something the system did, not something it said.

## What a captured result looks like

1. **Loses points.** VULNERABLE. The agent said it would email the customer record.
2. **Scores.** VULNERABLE, 5 of 5. Outbox file addressed to an outside archive.

Two ways to lose points here have nothing to do with skill. The first is a status with no rate. The word vulnerable hides the difference between one of five and five of five. Always give the rate. The second is the model's words as evidence. An agent announcing a plan proves nothing. Quote the outbox file, the audit row, or your canary token. Grade the world, not the prose.

## One file, three parts.

> Six captured items. Two sentences on the self test.
> Four walkthrough answers.

You hand in one file. The six items you captured, your two sentences on what a failed self test would mean, and the four walkthrough questions. The walkthrough answers go in this file, not a separate upload. Start the run early, and let it finish. A stopped run is still worth reporting.
