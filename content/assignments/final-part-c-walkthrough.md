::: intro
Walk somebody through your own repository in three minutes. Show your code.
Show your harness results. Say what you built and what you fixed.

It is due day 54 at 11:59 PM and it is worth 30 points.
:::

::: scope
You are showing results from attacks against HelpDesk Lite on your own
computer. Nothing else may appear in your walkthrough.

Before you record, close any browser tab that is not your own lab. A stray tab
in a screen recording is the fastest way to raise a scope question about work
that was fine.
:::

::: callout note | Three ways to submit, all worth the same
Nobody is graded on equipment or on comfort being filmed. Pick any one of
these:

1. **A screen recording with narration.** Your screen, your voice, three
   minutes.
2. **A slide deck with narration.** Screenshots on slides, recorded audio, three
   minutes.
3. **A written walkthrough with screenshots.** No audio and no video. Up to 600
   words, with a screenshot for each of the three parts below.

The written option is a full-credit option, not a fallback. Choose it for any
reason or for none.
:::

::: directions
Cover three parts, in this order. The timings are the whole structure, so
nobody has to guess what fits.

**Part 1, from 0:00 to 1:00. What you built.**

1. Open `agent/tools.py` on screen.
2. Show the tool you designed and its JSON schema.
3. Say in one sentence what the tool does, and one sentence on what it refuses
   to do.

**Part 2, from 1:00 to 2:00. What you broke, and how you know.**

1. Open your newest results file in `runs/reports/`.
2. Point at one attack case and read its result and its rate out loud.
3. Show the evidence for it: the outbox file, the audit row, or your canary.
4. Say which weakness class it is.

**Part 3, from 2:00 to 3:00. What you fixed, and what remains.**

1. Open your `before_tool_call()` change in `agent/loop.py`.
2. Show the same case re-run, with its new rate.
3. Show the benign baseline still passing.
4. Say one thing your fix still does not cover.

If you take the written option, use those same three headings with the same
content, and one screenshot each.
:::

::: callout tip | How to fit three minutes
Do one practice take with a timer before the real one. Almost everybody runs
long on part 1 and then rushes part 3.

Open every file you need before you start recording. Do not search on camera.

Read your rate off the screen. Do not try to remember it.
:::

::: submit
Submit either a media recording or a link.

If you upload a video or audio file, use the Canvas media upload.

If you host it somewhere, paste the link and check that it opens for your
instructor. A link nobody can open scores zero.

If you take the written option, upload one file named
`partc-<your last name>.md` or `.pdf`.

Helpful resource: [Canvas Student Guide: How to Submit an Assignment](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)
:::
