# Week 7 spec: Usable output and evaluation

**Course:** Agentic AI and Security Operations (ITSY 1377), Northeast Lakeview College, Cyber Defense program
**Phase 1 blueprint, item 3, week 7.** Prepared 2026-09-03.
**Audience:** the program manager. Nothing here assumes you are building the course.
**Primary evidence:** CLO5 and CLO6.
**Emails used:** the twenty batch emails, 026 to 045. Ten are malicious and ten are benign. None of them appears in any earlier week.

Eight terms carry this page.

- A **triage note** is the short written record an analyst leaves after judging one reported email.
- The **batch** is the set of twenty emails the agent reads in one sitting.
- The **answer key** is the correct verdict for each of those twenty, written when the corpus was built.
- A **false positive** is a benign email the agent called malicious.
- A **false negative** is a malicious email the agent called benign.
- **Accuracy** is the share of the twenty the agent called correctly.
- **Escalation agreement** is the share of the twenty where the agent's escalate flag matched the answer key.
- A **token** is a chunk of text, roughly four characters. It is the unit the model is billed and capped in.

## 1. The capability added, and why it is exactly one

The agent gains one thing this week. It writes its verdict as a fixed six-line note that another person can act on.

The six lines are set in order: verdict, confidence, indicators, recommended action, escalate yes or no, and a two-sentence plain summary for the employee who reported the mail. The template ships pre-written. The student writes the code that fills it.

Nothing else about the agent changes. The decision path built in week 6 runs untouched. No new tool, no new prompt rule, no new loop.

The batch run is not a second capability. It calls the same week 6 triage twenty times, once per email, and keeps going when one fails.

The scoring work is not a capability of the agent either. It is the student measuring the agent they already have. That distinction is the week's real lesson: a system that judges is not the same as a system you can trust, and only measurement closes the gap.

## 2. The lab deliverable

One text file, `week7_triage_report.txt`, written by a single pre-written export cell.

It has two headed sections. The first holds the twenty triage notes in the fixed format, in order. The second holds the score block: the counts, the accuracy rate, false positives and false negatives on separate lines, escalation agreement on its own line, the answer key version scored against, and the session token totals.

The file is text rather than JSON for one reason. Criterion 2 asks whether another analyst could act on the note. The grader has to read it the way an analyst would, and a text file lets them.

## 3. What the student writes, and what arrives pre-written

Two marked TODO cells. Together they are 13 to 17 written lines.

| Cell | What the student writes | Lines |
|---|---|---|
| TODO 1 | `write_note(result, facts)`. Fills the six-line template from one triage result and joins the indicator list into one line. | 5 to 7 |
| TODO 2 | `score_batch(rows, truth)`. Loops over the results, counts correct calls, false positives and false negatives, and returns the counts with the accuracy rate. | 8 to 10 |

**Flag: the line count runs slightly long.** The build prompt targets 5 to 15 written lines per lab. Week 7 lands at 13 to 17. Blank lines and comments are already left out of that count. The extra lines are the second and third counters in `score_batch()`, which are the objective itself and cannot be cut. The rubric never rewards shorter code.

Everything else in the notebook arrives complete and working. That includes the whole agent from weeks 1 to 6, plus seven new pre-written items: the extended output schema, the note template, the batch folder, the answer key, the file lister, the batch runner, and the report printer.

**Where the last two note lines come from.** Four of the six note lines are keys week 6 already produces. The recommended action and the plain summary are not. They arrive because `guarded_triage()` takes the answer schema as an argument, and the pre-written `run_batch()` hands it `OUTPUT_SCHEMA_V2` rather than the week 2 schema.

`guarded_triage()` returns whatever keys the schema it was given names, so both new keys come back in the same dictionary as the verdict. The week 5 signature and the week 6 signature were both built to grow this way, which is recorded in section 12 of the code ledger. No student reopens a week 6 cell to get a summary.

The two-sentence plain summary is produced by the model as its own field. `write_note()` places it. The student does not write prose into the note by hand.

Every email therefore ends with one closing model call, whatever stopped its loop. An email settled by a single decisive tool result still gets that call. The confidence, the indicators and the summary are the model's to write, and without them a note cannot be graded.

The notebook holds seventeen cells in the same order every week uses. The student runs the batch from a pre-written cell and reads a pre-written table of every email the agent got wrong, with the answer key beside it.

One point the program manager should see. The answer key for these twenty emails ships on the week 7 page, because every module opens on day one and nothing locks. Students can see the correct verdicts. That is fine, because no part of the grade rewards a correct verdict. The graded work is the quality of the note and the honesty of the measurement.

## 4. Weekly objectives

Numbered as the institutional template requires, under the lead sentence "By the end of this module, you will be able to:". Each one ends with its parent course learning objective.

- **7.1** Write a six-line triage note for all twenty emails. (CLO5)
- **7.2** Report your accuracy and your two kinds of error. (CLO6)
- **7.3** Name one place where a human must still review. (CLO6)

Each is one sentence, under 20 words, with one measurable verb. Each names something the student does in this week's lab. No objective is left without a parent.

**The two kinds of error in 7.2 are named, not hidden.** They are the false positive and the false negative, defined in the terms list at the top of this page. The lab page names them again beside the objective, and the notebook prints them on separate lines.

An earlier wording read "Report your accuracy, your false positives, and your false negatives." Scored on its own that sentence reads grade 9.55. The ceiling for student-facing text is grade 7.

The build prompt exempts required technical vocabulary from the reading level count, and this page could have claimed that exemption. It does not. The wording was changed instead, the way week 6 changed objective 6.3 rather than excusing it. Section 14 records the measured numbers.

The three of them run to 30 words, which is under the readability tool's 40 word floor, so the tool declines to score the block as it stands. The block was repeated until it cleared the floor and then scored, which is the method week 6 uses.

Repeating text does not move a Flesch-Kincaid grade, because the formula is a ratio of words to sentences and syllables to words. Measured that way, with the parent tags attached, the three objectives read at grade 4.44, with an average sentence of 9.9 words and a longest sentence of 10 words.

## 5. The sidebars

The week 7 target construct is three operations: looping over a list, counting results in more than one bucket, and calculating a rate. The sidebar rule is one construct per sidebar, so week 7 ships two short sidebars rather than one crowded one. Together they are 25 minutes.

**Chosen everyday domain: a recipe yield log.** Never email. Never security. No other sidebar in the course uses it. Four bakes, each with the number of rolls the recipe planned and the number the baker actually got.

| Sidebar | Construct | What it shows | Links back to |
|---|---|---|---|
| 7A | Loop over a list and count one bucket | Four bakes held as `{"planned": ..., "made": ...}`, read by key inside a `for` loop, counting the bakes that hit their planned number | Week 0, for loops |
| 7B | Count a second bucket, then divide for a rate | The same four bakes, counting the two ways a bake missed, then dividing the bakes that hit by the number of bakes and printing the rate | Week 0, if/else, and f-strings |

7A is ten lines. 7B is sixteen lines. Both run on their own and use only constructs week 0 teaches. Each ends with one ungraded "try changing this" prompt.

In 7A the student adds a fifth bake that hit its planned number, then watches the count move. In 7B the student adds a bake that came up short, then watches which of the two miss counts moves.

**Names and data shape.** Both sidebars take a list of dictionaries keyed `planned` and `made`. 7A defines `count_on_target(bakes)`. 7B defines `rise_rate(bakes)` and counts into `on_target`, `came_up_short` and `ran_over`. The lab cell defines `score_batch(rows, truth)` and reads a verdict out of each row. No name is shared, the lab parameter `truth` appears in neither sidebar, and no other weekly sidebar uses any of these names.

**Why pasting a sidebar into the lab fails.** The TODO 2 cell has to define `score_batch(rows, truth)`. A student who pastes `rise_rate()` there gets a NameError as soon as the next pre-written cell calls `score_batch`. Renaming it does not rescue the paste. The sidebar reads `planned` and `made` out of one list, while the lab reads a verdict out of a row and compares it against the answer key, so the next error is a KeyError on the first row.

## 6. The reading

**Title:** Writing the note, and measuring the agent.
**Length:** about 1,250 words, in three parts. The budget for a weekly reading is 1,400 words.

The page runs 200 words above the 900 to 1,050 word target the course writing standard sets, though inside its 1,400 word ceiling. Part 3 is the reason: it is survey content for breadth topic B2 and carries seven use cases. Without it the page would sit at about 860 words, inside the target.

| Part | Words | What it covers |
|---|---|---|
| 1. The note | about 480 | Who reads a triage note and when. Why the format is fixed. What each of the six lines is for. Why the summary is written for the person who reported the mail, not for another analyst. |
| 2. Measuring | about 380 | What accuracy is. What a false positive and a false negative are in a reported-mail queue. What each one costs a one-person security team. Why the two counts are never added together. Why escalation agreement is reported on its own line. |
| 3. Where else this goes (breadth topic B2) | about 390 | Seven jobs people give AI tools in security work: alert triage, log review, phishing analysis, documentation, scripting help, vulnerability research, and incident response support. One short paragraph each, saying what the tool does and what facts it would need first. |

Part 3 is the survey content for breadth topic B2. It carries no course objective, no Canvas Outcome and no lab. It sits here because students can only generalize once they have built something.

Two worked examples run inside the reading: one finished triage note, and one score block with the two error types apart. Students read both line by line, which is where much of the reading time goes.

**Sources.** Four to six citations. The candidates are NIST SP 800-61 on incident handling and documentation, the NIST AI Risk Management Framework on measurement and human oversight, and CISA guidance on reported phishing. Every citation goes through the expert review the build prompt requires, and every link is verified to resolve before the reading ships. Any claim that review cannot ground is flagged rather than quietly kept.

## 7. The discussion prompt

Graded. One post and one substantive reply. This is also where breadth topic B2 is assessed outside the final exam. Written out below exactly as students will see it.

> **Your numbers, and one other job for an agent**
>
> A use case is one job people give an AI tool.
>
> Open your week 7 report. Find three numbers: your accuracy, your false positive count, and your false negative count.
>
> Post by Thursday. Do three things.
>
> 1. Give your three numbers. Name one email your agent got wrong. Say which error it was.
> 2. Pick one use case from this week's reading. Do not pick phishing. Your choices are alert triage, log review, documentation, scripting help, vulnerability research, or incident response support.
> 3. Name one part of your agent you would have to change for that use case. Say what the change is. Say why it is needed.
>
> Then reply to one classmate by Sunday at 11:59 PM Central. Pick someone who chose a different use case. Say one thing their change would break or fix in your own agent. Use one number from your own report. A reply that only agrees does not count.
>
> Keep your post near 150 words. Keep your reply near 60 words.
>
> You may use AI help on this post. If you do, add one line saying what you asked it.

The prompt cannot be answered from opinion. Every part of it needs the student's own run. Two students will not have the same three numbers, because the model varies run to run.

## 8. What students submit

Three items, in one Canvas assignment. Nothing else. No folders, no links, no compressed files.

1. **One screenshot.** The printed score report from cell 14. It shows accuracy, false positives, false negatives, and escalation agreement, each on its own line. Escalation agreement prints there because `report_scores()` writes it, so one cell holds every number the rubric asks for. Students are told to capture that one cell's output, top to bottom, with the numbers readable. No cell in any week displays key material, so no screenshot can leak one.
2. **One file.** `week7_triage_report.txt`, written by the export cell. The cell prints the full path and the first few lines, so the student sees exactly what to attach.
3. **A written answer of 3 to 5 sentences**, typed into the text box. The prompt reads:

> Which error is worse for a one-person security team, a false positive or a false negative? Use your own counts from this run. Name one email your agent got wrong. Say where you would keep a human analyst in the loop. Say why.

All three items are gradeable without opening the student's notebook.

## 9. Rubric sketch

Three criteria, 100 points, four performance levels each. Criterion numbering matches the alignment matrix. Every weekly lab in this course is worth 100 points, so the seven labs carry equal weight inside the Labs group.

| # | Criterion | Points | Levels | Canvas Outcome |
|---|---|---|---|---|
| 1 | Submission completeness. The screenshot, the file and the written answer are all present and readable. | 8 | 8 / 6 / 4 / 0 | None. Declared a non-CLO expectation. |
| 2 | Triage note. All six lines present in order for all twenty emails. Each indicator names a fact your code pulled out. The recommended action fits the verdict. A reader with no security background can follow the summary. | 36 | 36 / 27 / 18 / 0 | CLO5: Document a triage decision |
| 3 | Accuracy and human review. Your accuracy number matches the file you attached. The two kinds of error are counted apart. Escalation agreement has its own line. Your written answer names where a human must still review, and cites your own accuracy figure and at least one of your own wrong emails. | 56 | 56 / 42 / 28 / 0 | CLO6: Measure triage accuracy |

**An earlier draft had a fourth criterion, and it was folded into criterion 3.** That criterion, "Own results used", was worth 15 points and carried no Outcome link. It is gone, and its requirement now sits in the last sentence of criterion 3.

The reason is a course rule rather than a week 7 preference. Clause 4 of the rubric link rule in the alignment matrix says a criterion scoring a student's use of their own results stays inside the Outcome-linked criterion. Measuring with your own numbers is CLO6 performance, not a separate expectation.

The academic integrity purpose survives the merge. A submission that cites no accuracy figure of its own, and names no wrong email of its own, still cannot reach the top level of criterion 3.

The points moved with the requirement. Criterion 3 was 40 and is now 56. Criterion 2 moved from 35 to 36 and criterion 1 from 10 to 8, so that every Outcome-linked criterion is an exact multiple of the four-point mastery scale and the lab still totals 100.

The four levels use the same wording across the course: exceeds standard, meets standard, approaching standard, no evidence. They map onto the mastery scale in the alignment matrix with no translation step.

## 10. The self-check

A Classic Quiz. Eight multiple choice items, two attempts, highest score kept, no time limit. Low stakes, and part of the 8 percent self-check weight.

| Items | What they cover |
|---|---|
| 4 | Breadth topic B2. Given a short description of a security job, name which use case it is, and name one fact the tool would need first. |
| 2 | Given a small result table, say whether a named miss is a false positive or a false negative. |
| 1 | Given a note with a line missing, name the missing line. |
| 1 | Say why escalation agreement is reported apart from verdict accuracy. |

Every stem is drawn from this course's own agent and corpus. None is answerable from general phishing knowledge.

## 11. Time estimate

| Activity | Minutes |
|---|---|
| Overview video | 3 |
| Walkthrough video, what success looks like | 4 |
| Reading, about 1,250 words with two worked examples | 42 |
| Sidebar notebook | 25 |
| Lab: read the notebook and run the pre-written cells | 35 |
| Lab: TODO 1, `write_note()` | 30 |
| Lab: TODO 2, `score_batch()` | 45 |
| Lab: run the batch and wait for it | 25 |
| Lab: read the wrong-answer table, export, screenshot | 30 |
| Discussion, one post and one reply | 18 |
| Self-check, submission, and the wrap-up page | 30 |
| **Total** | **287 minutes, or 4 hours 47 minutes** |

The lab totals 165 minutes, inside the 2.5 to 3 hour band. Every other line sits inside its own band. The week is under the 6 hour ceiling with 73 minutes of slack, which is 360 minus 287.

One warning about the batch wait. Sixty-five model calls at roughly 1.3 seconds each is 85 seconds of machine time, still under two minutes.

The default reasoning mode is far slower. The same sixty-five calls take 15 to 22 seconds each. That is 16 to 24 minutes of a student sitting and watching, which alone would push the lab over its band. This week therefore supports the recommendation to run with reasoning switched off.

## 12. Token estimate for one full lab run

One triage sends about 5,800 characters of prompt. Five of the parts are shared with earlier weeks and are measured once for the whole blueprint, in section 2 of the grade distribution and token totals document.

| Prompt part | Characters | Source |
|---|---|---|
| Guard rules | 700 | Authored, estimated. Week 6 sends the same block |
| Loop instructions | 400 | Authored, estimated. Week 6 sends the same block |
| The answer schema, `OUTPUT_SCHEMA_V2` | 615 | Shared |
| Playbook snippet | 1,366 | Shared |
| Known-good domain list | 668 | Shared |
| Facts block | 343 | Measured on this week's emails |
| Email body | 729 | Measured mean of the twelve rendered files |
| The three tool definitions | 964 | Shared |

Those add to 5,785 characters, which at four characters per token is 1,446 tokens per call.

A full batch makes 65 model calls. Forty-five are calls where the model asks for a tool. The other twenty are closing calls, one per email, where the model writes the answer that fills the note.

Every email gets a closing call, including the five that stop early on a decisive tool result. That is why the count is 65 rather than 60.

Each later call in one email re-sends the earlier turns, which adds 79 increments of about 88 tokens. The 79 follows from the tool-request distribution the corpus manifest sets, so it can be checked line by line.

| Tool requests the email makes | Emails | Calls each, one closing call included | History increments each | Increments |
|---|---|---|---|---|
| 1 | 4 | 2 | 1 | 4 |
| 2 | 7 | 3 | 3 | 21 |
| 3 | 9 | 4 | 6 | 54 |
| **Total** | **20** | **65 calls** | | **79** |

The check: 4 plus 14 plus 27 is 45 tool requests, and 8 plus 21 plus 36 is 65 calls. So 65 x 1,446 + 79 x 88 = 100,942 prompt tokens.

Completions add 45 x 34 + 20 x 160 = 4,730 tokens, and the one check-cell run before the batch adds about 5,900 more. **A full week 7 lab run is about 112,000 tokens.** Retries push it toward 120,000. This is the second heaviest week in the course, behind week 6.

If the reasoning model is left in its default mode instead, completions rise to roughly 155 tokens for a tool request and roughly 1,110 for a closing note. That is 45 x 155 + 20 x 1,110, or 29,175 completion tokens, the check-cell run rises to about 9,600, and the run reaches about 140,000 tokens.

Section 13 lists which of these inputs were measured and which are projected.

## 13. Assumptions and open questions

1. **Some token inputs are measured and some are projected.** The measured ones are the playbook snippet at 1,366 characters, the answer schema, the known-good domain list, the three tool definitions, the facts block, and the mean rendered body. The playbook figure is the byte count of the corpus playbook file. The 34-token tool-call completion is measured too, from the serving stack probe.
   - Projected: the guard rules, the loop instructions, the 160-token closing completion, the 88-token turn increment, and the check-cell run.
   - The serving stack recorded 65 to 79 completion tokens for a four-key JSON answer, and 27 to 47 for a short answer after a tool result. Nothing measured reaches 160. That figure is a projection for the larger six-field note, and Phase 2 should measure it.
   - One more caution sits outside this list. The chat template inflates tool definitions beyond their character count, so every call that carries `TOOL_SPECS` costs more than the table above says. Section 3.2 of the grade distribution and token totals document carries the course-wide allowance for that.
2. **Body length is a mean over twelve rendered emails.** Only one of the twenty batch emails is rendered today. Across the twelve files that exist the plain bodies run 258 to 1,129 characters, with a mean of 729, counted with line endings normalised. If the remaining nineteen run longer, the token figure rises in proportion.
3. **Reading minutes are built from the one course rate.** The course prices one reading pass at 200 words a minute, which is section 2 of the survey content plan, and prices anything a page asks beyond that as its own named line. Week 7 reads 1,250 words in 6 minutes at that rate, then adds 26 minutes for the two worked examples and 10 for opening one cited source, giving 42. The build prompt asks for this to be checked against the real week 1 and week 2 builds, and it should be.
4. **Sixty-five calls assumes the expected loop paths hold.** The count comes from the corpus manifest: forty-five tool requests across the twenty emails, plus one closing call each. By stop reason, fifteen emails run their tools out and five stop early on a decisive result. By tool count, which is what the history arithmetic needs, four emails make one request, seven make two and nine make three. The two views agree, because an email runs out of tools as soon as no untried tool has anything to look at. A model that asks for tools in a different order changes the count, not the shape.
5. **The closing call pins a behavior week 6 left implicit.** The code ledger describes the week 5 loop as stopping on a decisive tool result without asking the model again. Week 7 needs a schema answer for every email, so `guarded_triage()` makes one closing call whatever the stop reason. The ledger records that, and the week 6 spec's own call count and token arithmetic are built on it.
6. **Open question for the program manager.** The answer key ships to students on the week 7 page. That follows from the rule that nothing locks. If the program would rather the key stayed with the instructor, the week still works, but the wrong-answer table has to be replaced with a graded comparison the instructor runs later.

## Measured readability

Measured with the course readability gate on 2026-09-04. This is a program manager
document, so the whole page is held to grade 9.5, an average sentence of 18
words and no sentence over 45. Student-facing text drafted inside it is held to
grade 7 and an average sentence of 12 words.

| Text measured | Flesch-Kincaid grade | Average sentence | Longest sentence |
|---|---|---|---|
| This whole page | 6.60 | 14.1 words | 38 words |
| The three objectives, section 4 | 4.44 | 9.9 words | 10 words |
| The discussion prompt, section 7 | 3.03 | 8.3 words | 20 words |
| The written answer prompt, section 8 | 4.24 | 10.2 words | 16 words |
| The rubric criterion column, section 9 | 6.59 | 9.6 words | 25 words |

No prose paragraph on this page runs over 70 words.

**How the short blocks were scored.** The readability tool declines to score
anything under 40 words. A block under that floor was repeated until it cleared
it and then scored, which is the method week 6 uses. Repeating text does not
move a Flesch-Kincaid grade, because the formula is a ratio of words to
sentences and syllables to words. A rubric row is the criterion column, each
cell read as one line, with the header row left out.

**Two numbers that moved, and one exemption not claimed.** Objective 7.2 read
"Report your accuracy, your false positives, and your false negatives." Scored
on its own that sentence reads grade 9.55. It now reads "Report your accuracy
and your two kinds of error." and scores 6.28. Section 4 says where the two
kinds are named.

The rubric criterion column read grade 7.99. Criterion 2 and criterion 3 were
reworded and the column now reads 6.59.

The build prompt exempts required technical vocabulary from the reading level
count. No exemption is claimed on this page. "Accuracy", "false positive",
"false negative", "triage note" and "escalation agreement" are all counted in
full in the numbers above, and every one of them is defined in the terms list
at the top of the page.
