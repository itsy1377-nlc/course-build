# Week 4 pre-registration (mine), written 2026-09-09 before any probe result

Written before `w4_choice.py` printed a single row and before `w4_isolate.py`
was run at all. Codex is composing its own independently; the two get compared
without either being edited afterwards.

## The claim under test

Week 4's objective 4.3 is "Compare each email's verdict with tools against its
verdict without tools." The week is built on the argument that the tool's one
fact is what moves the verdict. Two things could make that false:

  H1  The model asks for the same tool on every email, so two of three tool
      branches never run live and email 018 -- the week's showcase -- is judged
      on the half of the evidence that is clean.
  H2  The verdict difference the notebook's table displays is produced by the
      prompt difference between the two arms, not by the tool result.

## Probe 1, tool choice. Pre-registered readings.

Conditions: bare (cell 8's shape), playbook (cell 14's shape, shipped), filler
(bare plus neutral text matched to the playbook's length). n=12 per email per
condition, 6 emails, 216 calls. n=12 because a 6/6 or 0/12 result is what the
fix hinges on and 12 puts a one-sided 95% bound near 22% on a 0/12.

  P1a  H1 CONFIRMED if, in the playbook condition, check_sender_reputation is
       the modal tool on at least 5 of the 6 emails AND check_urls is chosen on
       018 in fewer than 3 of 12 runs. 018 is the case that matters: its
       designed demonstration is a blocklisted host.
  P1b  The playbook is the CAUSE if bare shows check_urls on 018 in at least
       6 of 12 while playbook shows it in fewer than 3. Anything less separated
       than that is not a cause I will act on.
  P1c  DISCRIMINATING CONTROL. If filler narrows the choice as much as playbook
       does, the cause is prompt length, not the playbook's content, and any
       fix that edits the playbook is wrong. Control passes only if filler's
       018 check_urls rate sits within 3 of bare's, not within 3 of playbook's.

  What would tell me I am wrong: bare and playbook agreeing on 018. Then tool
  choice is a property of the model and the email, the playbook is innocent,
  and the fix has to be structural -- which email week 4 showcases, or how many
  tools it is allowed to call -- not a prompt edit.

## Probe 2, what the tool result is worth. Pre-registered readings.

Four arms, n=8 per email: A grounded (the shipped "no tools" column),
B toolshape (the with-tools prompt, one turn, no tool), C withheld (the whole
two-turn exchange with an uninformative tool message), D real (shipped).

  P2a  H2 CONFIRMED, and 4.3's comparison is unattributable as shipped, if the
       A-to-D verdict difference is at least twice the C-to-D difference summed
       over the six emails. That is the case where most of what the table shows
       is the prompt.
  P2b  The tool result is a REAL active ingredient only where C differs from D
       on at least 6 of 8 runs for that email.
  P2c  NOISE FLOOR, the control that caught week 3. D is run twice per
       iteration. Any email whose D-vs-D disagreement is 2 of 8 or more cannot
       carry a demonstration, whatever its C-vs-D number, because run-to-run
       variation alone explains that size of effect.

  What would tell me I am wrong: C sitting far from D on most emails, with a
  noise floor at 0. Then the tool fact really is doing the work, the confound
  is cosmetic, and the fix is to say so on the page rather than to rebuild the
  comparison.

## Accuracy, recorded but not a gate

Truth is benign for 003, 017, 019 and malicious for 008, 009, 018. Accuracy is
recorded per arm. It is not a pass/fail threshold: week 4 teaches a mechanism,
not a detector, and a fix that chased accuracy would be optimising the wrong
thing. It is here so that a fix which makes the agent measurably worse is
visible rather than invisible.

## The claim on the page, tested for free

Cell 8, the reading, cell 9 and cell 13 all tell the student that a reply
carrying a tool call carries no answer text. The video's recorded run
(content/video/runs/w4.json, granite4.2:3b on ollama) has answer_text "", so
the claim was true when measured. Probe 1 counts the rate on the shipped proxy.

  P3  The three prose claims and cell 8's unconditional print must be hedged if
      answer text is present in more than 1 of 60 replies in any condition.
      One occurrence is enough: a beginner reading a sentence that argues with
      the four lines above it is the defect, not the rate.

---

# Confirmatory pre-registration, written 2026-09-09 after probes 1-5, before probe 6

Probe 3 (forced tools) was designed after probe 2's threshold failed, so it is
exploratory. A fix built on it needs a confirmatory run against thresholds
fixed in advance. These are those thresholds. Fresh runs, same rig, n=8.

The fix I am inclined toward is a pre-written cell that runs ONE email through
all three tools with everything else held constant and prints three verdicts
side by side. For that cell to be honest about what a student will see, the
effect has to be reproducible.

  C1  Email 017 ships as the demonstration only if all four hold on a fresh run:
        withheld    -> malicious in at least 6 of 8
        reputation  -> benign    in at least 7 of 8
        urls        -> benign    in at least 7 of 8
        recipient   -> malicious in at least 7 of 8
      017 is the case where two tools fix a wrong answer and the third does not.

  C2  Email 018 ships as the counter-case only if all four hold on a fresh run:
        withheld    -> malicious in at least 7 of 8
        reputation  -> benign    in at least 7 of 8
        urls        -> malicious in at least 7 of 8
        recipient   -> malicious in at least 7 of 8
      018 is the case where a true fact about the sender walks a correct verdict
      backwards.

  C3  If either fails, the cell must PRINT what it got rather than assert what
      it will get, and no page may state the outcome as a fact. This is the rule
      week 1 needed and did not have.

  C4  Passing known_names=KNOWN_NAMES into cell 14's load_email(), which is the
      one-line correctness fix for email 009, must not move any verdict on any
      of the six emails by more than 1 run in 8 against the same arm without it.
      If it does, it is not a silent correctness fix and has to be measured and
      described on its own.

  What would tell me the whole approach is wrong: 017 and 018 both failing.
  Then no single email carries a stable three-tool contrast, the demonstration
  has to be built from more than one email or from a hand-built trace the way
  week 5 cell 10 does, and the fix is larger than a cell.

---

# Second confirmatory pre-registration, written before probe 8

Probe 7 (one withheld twin per tool) answered codex's objection to probe 3 and
in doing so produced two candidate demonstrations that probe 3 could not see.
Probe 7 generated that hypothesis, so it cannot also confirm it. These are the
thresholds, fixed before probe 8 runs, fresh samples.

Both candidates are FULLY MATCHED pairs: the same tool name and the same
arguments in both arms, so the only thing that differs is whether the tool
message carries the real record or "no record available".

  C5  017 with check_urls ships as the "a fact repairs a wrong answer"
      demonstration only if, on a fresh run:
        withheld twin -> malicious in at least 7 of 8
        real record   -> benign    in at least 7 of 8

  C6  018 with check_sender_reputation ships as the "a true fact breaks a right
      answer" demonstration only if, on a fresh run:
        withheld twin -> malicious in at least 7 of 8
        real record   -> benign    in at least 7 of 8

  C7  The two null arms must stay null, or the pair of demonstrations is not
      the contrast it is being sold as:
        018 with check_urls,        both arms malicious, pair differs <= 1 of 8
        017 with lookup_recipient,  both arms malicious, pair differs <= 1 of 8

  If C5 fails and C6 passes, the cell is built on 018 alone and says nothing
  about repair. If C6 fails and C5 passes, the reverse. If both fail, no single
  matched pair is stable and the demonstration has to be hand-built the way
  week 5 cell 10 builds its trace.

  Note on why C1 failed earlier: probe 6's withheld arm for 017 carried the
  check_sender_reputation NAME and arguments. Probe 7 shows 017's withheld
  baseline depends on which tool name sits in the exchange -- malicious 8/8
  under the check_urls name, 4/8 to 6/8 under the reputation name. That is a
  finding in its own right and it means C1's failure was an artifact of an
  unmatched control, not evidence that 017 is unstable.
