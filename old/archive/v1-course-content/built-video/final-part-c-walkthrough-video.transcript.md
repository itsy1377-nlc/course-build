# Three minutes, three parts

A text version of the walkthrough video. Every word spoken, in order.

## Three minutes, three parts

*Diagram: Three boxes left to right. What you built, from zero to one minute. What you broke and how you know, from one to two minutes. What you fixed and what remains, from two to three minutes, drawn as the part people run out of time for.*

- What you built, 0:00 to 1:00
- What you broke, 1:00 to 2:00, and how you know
- What you fixed, 2:00 to 3:00, and what remains

Part C is three minutes on your own repository. Minute one is what you built. Minute two is what you broke, and how you know. Minute three is what you fixed, and what still remains. The timings are the whole structure. Nothing is left for you to guess.

## Three ways to hand this in

1. A screen recording with narration
2. A slide deck with narration
3. A written walkthrough with screenshots

There are three ways to hand this in, and all three are worth the same. A recording of your screen, with your voice. A slide deck with screenshots and recorded audio. Or a written walkthrough with screenshots and no audio at all. The written option is full credit, not a fallback. Choose it for any reason, or for none.

## Your tool, and its schema

> One sentence on what it does.
> One sentence on what it refuses to do.

Start with what you built. On your own screen, open your tools file and show the tool you designed. Show its schema next to it. Then say one sentence on what the tool does. And one sentence on what it refuses to do. This video never opens that file, because your code is yours. Most people run long here, and then rush part three.

## At the terminal

Commands run, in order:

- `ls runs/reports`
- `sed -n "/^### A5/,/^- Evidence/p" runs/reports/*-results.md`
- `grep "^| .A5" runs/reports/*-results.md`

Minute two is what you broke, and how you know. Run the harness once more before you record, so your numbers are current. Then list your reports folder. The newest file is your source. Print the finding for one attack case. This is the knowledge base case from Week 5, article KB dash 02. Staff wrote that article, and it still carries an instruction. Read the result off the screen. Vulnerable, five of five. The three framework lines are labels from OWASP and MITRE ATLAS. They are not the weakness class. That is a separate field. The last line names the evidence. An outbox file, addressed outside the company. Now print the table row, where the Class column lives. It reads indirect prompt injection from trusted internal content.

## At the terminal

Commands run, in order:

- `ls target/outbox/`
- `grep '"to"' target/outbox/*.json`

Now show the evidence itself, not the report's summary of it. There is one file in the outbox, and the recipient is in the file name. One line out of that file is the whole finding. An address nobody at the company authorized. Then say which weakness class it is. The Class column has the words. Grade the world, not the prose.

## At the terminal

Commands run, in order:

- `grep "^| control" runs/reports/*-results.md`
- `sed -n "/^### A5/,/^- Evidence/p" runs/reports/*-results.md`

Minute three is what you fixed, and what remains. Show your guard on your own screen, then run the harness again. Read the controls first. Both pass, so normal support work still gets through. Now the same case, in your new report. It reads blocked, five out of five. That is not the same as an attack that failed. The agent asked every time. Your code refused every time. The evidence line says no message left the company. Finish by naming one thing your fix still does not cover.

## Two habits make this fit.

> One practice take with a timer.
> Every file open before you start.

Do one practice take with a timer before the real one. Open every file you need before you press record, and do not search on camera. Close any browser tab that is not your own lab. A stray tab raises a scope question about work that was fine. If you host the file somewhere, check the link opens for your instructor. A link nobody can open scores zero.
