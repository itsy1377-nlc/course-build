# Grading notes: Start Here, week 0, week 1 and week 2

Northeast Lakeview College, Cyber Defense program. ITSY 1377, Agentic AI and
Security Operations. Nothing on this page is student-facing.

This page is written for use, not for reading. Grade from it with the rubric
open beside you.

Every number here comes from a file in this repository, and the file is named
where the number is used. Paths are written from the repository root,
`~/workspace/dev/ITSY1377/`.

---

## 1. The one rule, and the three items

**You never run a student's notebook.** Not to check an answer, not to see what
went wrong, not to be fair. Every criterion in every rubric was written so that
it can be decided from three things and no more.

1. One screenshot.
2. One exported file the notebook wrote.
3. Three to five sentences typed into the Canvas box.

That rule is a design commitment, not a preference. It is stated in the build
brief, in `builder/docs/phase1-blueprint/README.md` under decision 4, and again
at the foot of both rubric files. Three practical reasons back it up.

- A student's notebook does not run in your account. The corpus path, the model
  name and the key all come from that student's environment.
- Running it spends tokens from a budget the program pays for. One full week 1
  run is about 2,560 tokens and one full week 2 run about 3,200
  (`builder/docs/phase1-blueprint/grade-distribution-and-tokens.md`, section 3).
- Nothing you would learn by running it appears in any criterion. The criteria
  ask what the file records, not what the code does.

Section 6 below says what to do instead when a submission looks wrong.

## 2. The turnaround you committed to, and how to hit it

**The commitment.** A grade and written feedback on each lab **within one week
of its due date**. It is printed in four student-facing places, so students will
hold you to it: `builder/content/pages/course-policies.md` (the key facts table
and the section "Feedback on your labs"),
`builder/content/pages/meet-your-instructor.md`,
`builder/content/pages/support-resources.md`, and
`builder/content/pages/home.md`.

**The second commitment.** Messages answered in 24 to 48 hours, not counting
weekends and holidays (`builder/content/pages/course-policies.md`).

**Everything is due Sunday 11:59 PM Central** (same file). So a lab due at the
end of week 1 must be graded and returned before the end of week 2.

### How to hit it

The session is eight weeks long. Week 1 feedback lands while students are
building week 2 on top of week 1, so labs are graded before discussions and
before self-checks. Self-checks are auto-scored by Canvas and need nothing from
you.

Budget four minutes per lab submission. That is the number this page is built
around. For a section of 25 students, four minutes each is 100 minutes for the
whole lab, in one sitting. Sit down once, on the Monday or Tuesday after the due
date, and finish the pile.

Four things keep a submission inside four minutes.

1. **Grade in the order below, not in the order the student uploaded.** The
   fastest path through week 1 is section 4.6; through week 2, section 5.6.
2. **Use the Canvas rubric in SpeedGrader.** Click a level on each criterion.
   Do not type a score.
3. **Build the comment bank before you grade the first paper.** Sections 4.7 and
   5.7 give the comments to paste. Add one sentence of your own naming the
   student's own number or their own line. One sentence is enough, and it is the
   part a student reads.
4. **Do not open the notebook.** This is where the minutes go.

If you fall behind, return the scores first and the written comment second.
A score with a one line comment inside the week beats a paragraph after it.

## 3. Start Here and week 0: nothing to grade, two things to watch

Neither module carries a graded lab. Your work here is completion tracking and
one outreach message.

| Item | Where | Points | What you do |
|---|---|---|---|
| Syllabus acknowledgment | Orientation module | Ungraded practice quiz, unlimited attempts | Check who has not taken it by the end of week 1 |
| Introduce yourself | Orientation module | 1 point, Orientation group weighted 0 percent | Post or 0. It changes no grade |
| Week 0 self-assessment | Module 0 | Ungraded practice quiz, unlimited attempts | Read the scores. Do not grade them |
| Week 0 notebook | Module 0 | Ungraded | Nothing |

Sources: `builder/content/quizzes/syllabus-acknowledgment.yaml`,
`builder/content/discussions/introductions.md`,
`builder/content/quizzes/week0-self-assessment.yaml`,
`builder/content/course.yaml`.

**The one thing worth your time here.** The week 0 self-assessment is ten
questions, and its scoring rule tells a student who gets 5 or fewer right to
work the whole notebook, about five hours
(`builder/docs/phase1-blueprint/week-00-outline.md`, "The scoring rule, as
students read it"). Canvas shows you those scores.

Message every student who scored 5 or fewer and has not opened the week 0
notebook, in week 1, before the first lab is due. Say that week 0 is open all
term and that section 10, how to read an error message, is worth thirty minutes
on its own. That one message is the highest-value thing you do in week 1.
The programming gap is the course's largest named risk, and it does not close
itself.

## 4. Week 1 lab: your first model call

100 points. Four criteria at 25 each. Rubric:
`builder/content/rubrics/w1-lab.yaml`. Student page:
`builder/content/assignments/w1-lab.md`.

Cell numbers below count from 1, the way the student page counts them.

### 4.1 The exported file: what it should contain

One plain text file named `week1_first_calls.txt`, written by cell 14. Its
headings are fixed, because a pre-written cell writes them
(`builder/lab/notebooks/w1-lab.ipynb`, cell 14 counting from 1).

```
ITSY 1377 week 1: first calls
Model configured: <model name>
Emails used: 001, 002
--- The prompt sent for email 001 ---
--- Your own first call, from TODO 2 ---
--- Six answers for email 001 ---
    Answer 1 of 6, temperature 0.2      (through Answer 6 of 6, temperature 1.0)
--- The prompt sent for email 002 ---
--- Answer for email 002 ---
--- Token totals for this session ---
    Calls counted / Prompt tokens / Answer tokens / Total tokens
    Prompt tokens, email 001 / Prompt tokens, email 002
```

What has to be there for full credit on criterion 2: six answers under the
six-answer heading, one answer under the email 002 heading, and both prompt
blocks with text in them.

**Four strings to search for. Each one settles a score in seconds.**

| Search for | What it means | What to do |
|---|---|---|
| `ask_model() is not written yet.` | TODO 1 was never written. The placeholder answered all six times | Criterion 2, bottom level, 6 points |
| `No answer came back.` | The request never reached the model. Service outage, missing key, or no network | Read section 6.3 before you score |
| `No answer text came back.` | The model was reached and returned nothing usable | Read section 6.3 before you score |
| `not recorded` under "Your own first call" | The student did not create a variable named `answer_001` in TODO 2 | **Do not deduct.** See below |

**The "not recorded" line is not a deduction.** The export cell reads a variable
named `answer_001`. A student who did TODO 2 correctly but named their variable
something else gets "not recorded" in a file that is otherwise complete. No
criterion asks for that line. Mention it in the comment so the student knows,
and score criterion 2 on the six answers and the email 002 answer, which are
written by pre-written cells and are the evidence the criterion names.

### 4.2 How to tell at a glance that it is the student's own run

Three checks, about twenty seconds.

1. **The token block is per-session and specific.** "Calls counted" is 9 on a
   clean top-to-bottom run: one check question, one TODO 2 call, six temperature
   calls, one email 002 call (`builder/docs/phase1-blueprint/code-ledger.md`,
   section 3, "Model calls in a full run"). A number other than 9 is normal and
   is not a problem. A restart resets the counter, so a student who restarted
   partway will show fewer calls and smaller totals.
2. **The six answers are prose the model wrote that day.** Read two of them.
   They are about email 001, a payroll deposit message. Three at temperature 0.2
   sit close together and three at 1.0 spread out. Answers that are all six
   identical are possible on a low temperature and are not by themselves a
   problem.
3. **The written answer has to name numbers that are in the file.** This is the
   real check, and the course tells students it is coming
   (`builder/content/pages/ai-use-policy.md`: "Your grader reads the file and the
   answer side by side"). If the written answer quotes a token count or a
   temperature that appears nowhere in the attached file, that is the mismatch to
   act on.

**What one file cannot tell you.** Nothing in a single submission proves whose
run it was. Two submissions whose token blocks match digit for digit is the
signal, and it only appears when you have both files. If you see it, route it
through the process on `builder/content/pages/academic-integrity.md` rather than
settling it in the gradebook.

### 4.3 The screenshot

One image of the output of **cell 11**, the temperature comparison. It has to
show all six answers. Look for the repeated header line
`--- Answer 1 of 6, temperature 0.2 ---` through `Answer 6 of 6`.

Three rules that save arguments.

- **Two images are allowed.** The student page tells students to take two if six
  answers do not fit in one (`builder/content/assignments/w1-lab.md`). Two images
  that together show six answers are full credit.
- **There is no token line in this screenshot, and there should not be.** Cell 11
  switches the per-call token report off so the six answers sit together. Do not
  deduct for a missing token line. Token evidence reaches you through the file
  (`builder/docs/phase1-blueprint/week-01-spec.md`, section 8).
- **The screenshot is scored only inside criterion 1** in week 1. There is no
  separate screenshot criterion this week. Week 2 has one.

No cell in this notebook prints key material, so no week 1 screenshot can carry
a key. If you ever see key material in one, stop grading and read the
environment setup page in this folder.

### 4.4 The written answer: what full credit looks like

Three questions, three to five sentences, in the Canvas box
(`builder/content/assignments/w1-lab.md`).

> (1) Which of your six answers differed most, and at which temperature?
> (2) What happened to the token count on email 002, and why?
> (3) What would you check before trusting this answer in a real ticket?

Criteria 3 and 4 both live in these sentences. Question 2 is not scored by any
criterion on its own, so a weak answer to it costs nothing.

**A full-credit answer, written the way a student writes it.** The numbers in
this example are made up to show the shape. Do not compare a student's numbers
against them.

> Answer 5 differed the most. It ran at temperature 1.0 and it was the only one
> that called the message a "payroll scam" instead of just phishing, and it
> named the deadline as well. My three answers at 0.2 all said nearly the same
> thing in nearly the same words. Email 002 cost me more prompt tokens than 001,
> 241 against 198, because its body is longer and I pay for the text I send, not
> for the number of questions. Before I trusted this in a real ticket I would
> check the sending domain against our known-good list, because the body on its
> own never shows who actually sent the mail.
> AI use: none.

Why that is full credit on both criteria. Criterion 3 wants a named answer plus
a temperature, and this names answer 5 at 1.0. Criterion 4 wants one specific
check plus why it matters here, and this names the sending domain and says why
the body alone cannot settle it.

**A thin answer, written the way a student writes it.**

> The six answers were all a bit different from each other. The temperature
> setting changed how different they were. The token count went up on the second
> email. I would check the answer carefully before I trusted it.

Why that is thin. It never points to one of the six answers, so criterion 3 is
13. "Check the answer carefully" is the general check the rubric names by
example, so criterion 4 is 13. Criterion 1 is unaffected. That answer scores 26
of the 50 points that live in the written response.

### 4.5 Criterion by criterion

Levels are 25, 19, 13 and 6. There is no zero level in week 1.

**Criterion 1, Submission completeness, 25 points. No Outcome.**

| Score | When |
|---|---|
| 25 | Screenshot, file and written answer all present. Six answers readable in the image, across one or two images. File attached as a file |
| 19 | All three present, one hard to read. One or two of the six answers cut off |
| 13 | One of the three missing, or the screenshot cannot be read |
| 6 | Two of the three missing, or a zip file or a link was turned in instead of the file |

Read this criterion first. It is the only one that needs all three items in
front of you at once.

**Criterion 2, The call works, 25 points. Outcome CLO2, supporting evidence.**

| Score | When |
|---|---|
| 25 | Six answers for 001, one answer for 002, and both prompt blocks carry text |
| 19 | Both emails answered, but the prompt text is missing or shows for only one |
| 13 | One email only, or fewer than six answers for 001 |
| 6 | No answer from the model anywhere, or an error where an answer should be |

This is decided entirely inside the file. Count the "Answer N of 6" headings.
The bottom level is the case where the four search strings in section 4.1 turn
up `ask_model() is not written yet.` or one of the two "No answer" sentences on
every line.

**Criterion 3, Variation reported, 25 points. Outcome CLO2, supporting.**

| Score | When |
|---|---|
| 25 | Names which of the six differed most, and gives the temperature |
| 19 | Names the answer but no temperature, or gives a temperature but names no answer |
| 13 | Says the six varied, but points to no particular one |
| 6 | Says nothing about the six answers |

"Answer 5" and "the third one at 1.0" both count as naming one. A quoted line
from an answer counts too.

**Criterion 4, First judgment, 25 points. Outcome CLO2, supporting.**

| Score | When |
|---|---|
| 25 | Names one specific check, and says why it matters for this email |
| 19 | Names one specific check |
| 13 | Names only a general check, such as making sure the answer is right |
| 6 | Names nothing to check |

Specific means a thing you could go and look at: the sender domain, the link
host, the authentication results, whether the deadline is real, whether the
payroll vendor is the one the company uses. General means "check it is correct",
"verify the output", "make sure it is accurate".

Week 1's three CLO2 links are overwritten by week 2, which carries the primary
evidence for CLO2 (`builder/content/rubrics/w1-lab.yaml`, header comment). The
week 1 score is your early reading on who will struggle in week 2. Treat a 13
on criterion 2 as a name to message that week.

**One arithmetic fact to know before a student asks.** The lowest level on each
criterion is 6, so a submitted but empty week 1 lab floors at 24 of 100. Week 2
has zero levels and floors at 0. That difference is in the two rubric files and
is listed in section 7 as an open question.

### 4.6 The four minute pass

1. **20 seconds.** Three items present? Score criterion 1.
2. **60 seconds.** Open the file. Jump to "Six answers for email 001". Count six
   headings. Check the email 002 answer is not one of the "No answer" sentences.
   Check both prompt blocks carry text. Score criterion 2.
3. **60 seconds.** Read the written answer. Score criteria 3 and 4.
4. **20 seconds.** Glance at the image. Six answers readable? Adjust criterion 1
   if needed.
5. **40 seconds.** Paste a comment from 4.7 and add one sentence naming their own
   number.

### 4.7 Comments to paste

- **Full marks.** "Clean run. Your six answers and both prompt blocks are all in
  the file, and you named answer N at temperature T rather than saying they just
  varied. That is the habit week 2 builds on."
- **Criterion 3 at 13.** "You said the six answers varied, which is right, but
  the criterion asks which one varied most and at what temperature. Open your
  file, find the six answers, and pick the odd one out. That is the whole ask."
- **Criterion 4 at 13.** "Checking that the answer is correct is not yet a
  check. Name a thing you could go and look at, such as the sending domain or the
  link host, and say what it would tell you. Week 3 is built on exactly this
  move."
- **Criterion 2 at 6, placeholder text in the file.** "Your file shows the
  placeholder answer, which means TODO 1 was not finished when the export cell
  ran. Your notebook is still there and every cell is still there. Open it, write
  `ask_model()` in cell 7, run cell 8 to check it, then run down to cell 14
  again. Message me if cell 8 does not print an answer."
- **Missing file, text pasted into the box instead.** "Attach the file itself
  rather than pasting it. Cell 14 prints the full path when it runs. Use the
  Attach button under the submission box."
- **"not recorded" line.** "One small thing that cost you nothing: your file says
  `not recorded` under 'Your own first call'. The export cell looks for a
  variable named `answer_001`. Name yours that in week 2 and the line fills in."

## 5. Week 2 lab: a strict answer

100 points, four criteria at 15, 50, 15 and 20. Rubric:
`builder/content/rubrics/w2-lab.yaml`. Student page:
`builder/content/assignments/w2-lab.md`.

Criterion 2 is worth half the lab and is the **primary evidence for CLO2 in the
whole course**. Spend your minutes there.

### 5.1 The exported file: what it should contain

One JSON file named `week2_classification.json`, written by cell 15
(`builder/lab/notebooks/w2-lab.ipynb`). Its shape is fixed by a pre-written
cell:

```
week            2
model           the model name from the student's environment
emails          a list of four records, ids 001, 002, 003, 004. Each holds:
                  email_id, answer, schema_ok, problems, tries, tokens,
                  attempts  (a list, one entry per try, each with
                             try_number, schema_ok, problems, answer_text)
sample_checks   four entries, one per saved reply, each with
                  sample, parsed_ok, extracted, problems
tokens          prompt, answer, total, calls
```

For full credit on criterion 2, the `emails` list holds four records, every
record carries `schema_ok` and `problems`, and every record's `attempts` list
holds one entry per try with its own `schema_ok` and `problems`. `problems` is an
empty list when the check found nothing wrong, and an empty list is correct, not
missing.

**Three checks that settle criterion 2 in about ninety seconds.**

1. Does `emails` hold four records?
2. Does every record have a non-empty `attempts` list?
3. Does every entry inside `attempts` carry both `schema_ok` and `problems`?

**Two fields that tell you instantly what was not written.**

| What you see | What it means |
|---|---|
| `sample_checks[0].parsed_ok` is `false` | `extract_json()` was not finished. The first sample is a clean answer with a reasoning block in front, and a working function loads it |
| Every email shows `tries: 0` and an empty `attempts` list | `classify_email()` was not finished, or it never called `log_attempt()` |

**A null answer is not automatically a low score.** A record with `answer: null`,
`schema_ok: false`, `tries: 3` and three `attempts` entries each carrying real
problem text is a complete record of a validation that ran three times and never
passed. That is full credit on criterion 2. The criterion measures whether the
check ran and was recorded, not whether the model was right.

**Verdicts are not graded in week 2.** No criterion scores them. For your own
reading, ground truth for the four emails is in `builder/corpus/ground_truth.json`:
001 malicious, credential_phish. 002 benign, legit_internal. 003 benign, spam.
004 malicious, bec. Email 003 is the one that proves verdict and category are
independent, and students commonly call it malicious. That costs no points.

### 5.2 How to tell at a glance that it is the student's own run

1. **`tokens.calls`.** A typical run is six calls, and the range is six to
   fourteen depending on retries. Two of the six are the raw run, which calls
   the model twice on purpose, and the other four are one try each on the four
   emails (`builder/docs/phase1-blueprint/code-ledger.md`, section 4). `calls: 0` with
   four answers filled in means no model call happened in that session, which
   points to a restart between the results cell and the export cell rather than
   to anything sinister. Ask for a rerun.
2. **`attempts[].answer_text`.** This is the first 300 characters of what the
   model actually returned, saved raw. It is the one field in the file that
   varies between two students who both did the work. Two files whose
   `answer_text` matches word for word across all four emails is the signal
   worth acting on.
3. **`sample_checks` is identical for every student who wrote `extract_json()`
   correctly.** It is built from four saved replies that ship inside the
   notebook. Do not read it as evidence of anybody's own run. It proves the
   student's function ran, nothing more.
4. **The written answer has to quote problem text that appears in the file.**
   Criterion 4 asks the student to copy the exact problem their code reported.
   Search the file for their quoted string.

### 5.3 The screenshot

One image of the output of **cell 14**, the results cell. It has to show all
four rows and the token line under the table.

What the rows look like: a header reading `id verdict category conf tries ok`,
a rule of dashes, then four rows, ids 001 through 004.

What the token line looks like: it starts `Tokens this session:` and carries
four numbers.

Unlike week 1, this screenshot is a criterion of its own, worth 15 points, and
the token line is part of it. The student page says plainly not to crop it off.
Cropping it is Partial, 10.

### 5.4 The written answer: what full credit looks like

> In 3 to 5 sentences, answer this. Which of your four emails took more than one
> try? Copy the exact problem your code reported on that failed try. If all four
> passed on try one, say so instead. Then give the lowest confidence number you
> saw. Either way, name one change you would make to the instructions.

**Two paths reach full credit**, and this matters, because on the recommended
model a clean four-email run is the likely case, not the edge case
(`builder/docs/phase1-blueprint/week-02-spec.md`). A student whose emails all
passed first time is never asked for problem text they do not have.

- Path A, something failed: name the email, copy the problem text, give the
  lowest confidence, name one change.
- Path B, nothing failed: say so, give the lowest confidence from their own
  file, name one change.

A student on path B loses nothing. Do not deduct for the absence of a failure.

**A full-credit answer, path A, written the way a student writes it.** The
numbers here are made up to show the shape. The problem text is the real string
the pre-written `schema_errors()` produces, so it is worth recognising.

> Email 004 took two tries. On the first one my code reported "confidence is 1.2,
> and it has to be from 0.0 to 1.0", so the answer loaded fine and still failed
> the check. I think the model read confidence as how bad the email was rather
> than how sure it was. The lowest confidence I actually saw was 0.61, on email
> 003. I would add one line to the instructions saying the confidence is never
> above 1.0 and is about how sure you are.
> AI use: I asked an assistant to shorten my second sentence.

**A full-credit answer, path B.**

> All four of my emails passed on the first try, so I have no failed try to copy.
> The lowest confidence in my file was 0.55, on email 003, which is the marketing
> one, and my agent still called it benign. That is the one I would trust least.
> I would change the instructions to say what to do when the message is
> annoying but not dangerous, because spam and benign together seem to confuse
> it.
> AI use: none.

**A thin answer, written the way a student writes it.**

> All four of my emails passed on the first try. The model did pretty well on
> them. I would make the instructions a bit clearer next time.

Why that is thin. It takes path B and then supplies none of what path B asks
for: no confidence number from their own file, and "a bit clearer" is not a
change. That is Partial, 10 of 20.

**The line that is not scored.** Every written answer should carry an "AI use:"
line, and "AI use: none" is a complete answer
(`builder/content/pages/ai-use-policy.md`). It does not count toward the three to
five sentences, and no criterion scores it. Ask for it in a comment when it is
missing. Do not deduct.

### 5.5 Criterion by criterion

**Criterion 1, Submission completeness, 15 points. No Outcome. Three levels.**

| Score | When |
|---|---|
| 15 | All three present and readable. The file attached as itself, under the name the export cell gave it |
| 10 | One of the three missing, or the file arrived as a zip or a link |
| 0 | Two or three of the items absent |

`week2_classification.json` renamed by the student is still the file. Score 15
and mention it.

**Criterion 2, Output validation, 50 points. Outcome CLO2, primary evidence.
Four levels.**

| Score | Level name | When |
|---|---|---|
| 50 | Exceeds standard | Four emails carry a checked answer. `schema_ok` and `problems` written on every try, the accepted try included. Every failed try recorded with the problems that caused it, and a reader can follow why each answer was accepted |
| 35 | Meets standard | Four emails carry a checked answer and the check result is recorded, but one try or one email is missing its `problems`, or `problems` is left out where the check found nothing wrong |
| 20 | Approaching standard | Answers for some emails, or answers with no check result recorded. It shows the model was called. It does not show the answer was checked |
| 0 | No evidence | No file, or a file with no classification in it |

How to tell 50 from 35 fast: 35 is the file with a hole in it. One email with an
empty `attempts` list while the other three are complete. Or `problems` present
only on failures and dropped on the accepted try, which is the single most
common shape, because a student writes the log call inside the failure branch
only.

How to tell 35 from 20: 20 is the file where nothing records a check at all.
Answers are there, `attempts` is empty everywhere, and `schema_ok` never
appears inside a try.

**The rating label is what Canvas records against CLO2**, on the shared scale of
4, 3, 2 and 0. The criterion points on the same row are what the grade uses. You
pick once and both follow (`builder/content/rubrics/w2-lab.yaml`, header
comment). Do not type a raw score into this criterion; click the level.

**Criterion 3, Results screenshot, 15 points. No Outcome. Three levels.**

| Score | When |
|---|---|
| 15 | One image, four rows each with id, verdict, category, confidence and tries, plus the `Tokens this session:` line. Readable |
| 10 | Rows or the token line cut off, or the text too small to read |
| 0 | No screenshot, or an image of a different cell |

The most common 10 is a crop that ends at the fourth row and loses the token
line.

**Criterion 4, Written answer, 20 points. No Outcome. Three levels.**

| Score | When |
|---|---|
| 20 | Three to five sentences carrying the student's own numbers, taking either path in full, and naming one change to the instructions |
| 10 | Under three sentences, or a part missing. No number of their own, or no change named |
| 0 | No written answer, or one carrying none of their own results |

Cross-check one thing and no more: if they quoted problem text, search the file
for it. If it is not there, that is a 10 and a message, not a 20.

### 5.6 The four minute pass

1. **20 seconds.** Three items present? Score criterion 1.
2. **90 seconds.** Open the JSON. Four records under `emails`? Every record with
   a non-empty `attempts` list? Every attempt carrying `schema_ok` and
   `problems`? Score criterion 2. Check `sample_checks[0].parsed_ok` on the way
   past.
3. **60 seconds.** Read the written answer. If it quotes problem text, search the
   file for that string. Score criterion 4.
4. **20 seconds.** Screenshot: four rows plus the token line. Score criterion 3.
5. **30 seconds.** Paste a comment from 5.7 and add one sentence of your own.

### 5.7 Comments to paste

- **Full marks.** "Your file records the check on every try, including the ones
  that passed first time, which is the part most people drop. That record is what
  makes an agent's answer defensible, and it is exactly what CLO2 asks for."
- **Criterion 2 at 35, problems dropped on the accepted try.** "Everything is
  here except one thing: your file records `problems` on the failed tries and
  leaves it off the try that passed. Move your `log_attempt()` call so it runs on
  every try, not just inside the failure branch. A passed check that leaves no
  record looks the same as a check that never ran."
- **Criterion 2 at 20, no attempts recorded.** "Your four answers came back and
  the model clearly ran. What the file does not show is that anything was
  checked: `attempts` is empty for all four. `log_attempt()` is written for you
  in cell 12. Call it once per try inside `classify_email()`, then run cells 14
  and 15 again."
- **`sample_checks[0].parsed_ok` false.** "Your first sample check did not parse,
  and that one is the clean answer. It has a reasoning block in front of it, so
  `extract_json()` has to call `strip_reasoning()` before `json.loads()`. Cell 11
  will tell you the moment it works."
- **Criterion 4 at 10, path B with no number.** "Saying all four passed on the
  first try is a complete answer to the first half. The second half asks for the
  lowest confidence number in your own file. Open the file, look at
  `confidence` on each of the four, and give me the smallest one."
- **Criterion 3 at 10, cropped token line.** "The screenshot needs the line
  starting `Tokens this session:` that prints under the table. It is one line
  below the fourth row."

## 6. When a submission looks wrong

### 6.1 The routine

1. **Read the file again for the failure itself.** The export files record
   failures on purpose. Week 1 writes the "No answer" sentences into the answer
   slot. Week 2 writes `problems` and `attempts`. The evidence of what broke is
   usually already in your hands.
2. **Score what the evidence supports.** Where a criterion's evidence is genuinely
   absent, pick the level that says so. Do not score a guess in either direction.
3. **Send one message that names a cell number and a line.** Not "your code has a
   bug". "Your `attempts` list is empty for all four emails, so `log_attempt()` is
   not being called inside `classify_email()`, cell 13."
4. **Point at the fix, not at the answer.** `common-failure-modes.md` in this
   folder holds the fix for everything students actually break. Name the entry.
5. **If you have to see the behaviour, run your own copy.** The solution notebook
   for that week, in your own environment, on the same emails. Never the
   student's notebook and never their file path.

### 6.2 Never ask for these

- Never ask a student to print, paste, screenshot or read out an API key, and
  never ask them to print the environment. No cell in any notebook in this course
  prints key material, and no troubleshooting step needs it.
- If you need to know what their environment did, ask for the printed output of
  the configuration cell, cell 3 in week 1 and cell 2 in week 2. It prints the
  model, the endpoint, the extra request fields, whether a key was found, and
  whether the email files were found. It prints no key.
- Never ask for a zip file, a folder or a link. Three items, always.

### 6.3 The two cases that are not the student's fault

**The model service was down or unreachable.** In week 1 the file carries
`No answer came back.` in the answer slots and the notebook still exported. In
week 2 the answers are null and `problems` reads that the answer is not a JSON
object. The two notebooks do not say the same thing here. Week 2's closing cell
tells the student to attach the file anyway and email you, and ends with "A dead
endpoint is not a late assignment" (`builder/lab/notebooks/w2-lab.ipynb`, cell
16). Week 1's closing cell tells them the notebook still ran and still wrote the
file, and to rerun the configuration cell and email you what it printed, but it
never tells them to submit (`builder/lab/notebooks/w1-lab.ipynb`, cell 15). So
say it yourself in the week 1 announcement: a dead endpoint is not a reason to
hold a submission. When you can confirm the outage, hold the score, tell the
student to rerun, and regrade. The wording for this sits in
`common-failure-modes.md` in this folder.

**The token budget ran out.** Policy, from the syllabus: a student who exhausts
their budget messages you and receives a top-up, with no grade penalty and no
late penalty for the delay (`builder/content/pages/course-policies.md`, "Your
token budget"). Top up, tell them to rerun, regrade. Do not score the run they
could not finish.

Both cases run into the late work and resubmission policy, which the course does
not set. You state it in your first announcement. Decide before week 1 is due how
a rerun after an outage is dated, and say it there.

## 7. Open questions, flagged rather than resolved

1. **The two rubrics floor differently.** Week 1's lowest level on each criterion
   is 6 points, so an empty submission scores 24 of 100. Week 2's lowest levels
   are 0. Both are internally consistent with the mastery scale in
   `builder/content/course.yaml`, which carries both a Beginning rating at 1 and
   a No evidence rating at 0. Whether week 1 should also floor at 0 is a program
   decision, not a grading decision. Grade the rubric as it ships.
2. **Whether an Outcome-linked criterion keeps its own points in Canvas.**
   `builder/docs/phase1-blueprint/week-02-spec.md` records this as a build
   detail to confirm: if Canvas forces criterion 2 to inherit the Outcome's 4, 3,
   2, 0, the week 2 rubric totals 54 and the other three criteria have to be
   rescaled to reach 100. Confirm in the built course before the first lab is
   due.
3. **Late work and resubmission is unset.** Named as unresolved in
   `builder/docs/phase1-blueprint/assumptions-and-gaps.md` and left to the
   instructor by `builder/content/pages/course-policies.md`. It decides how you
   handle every rerun in section 6.3.
4. **Week 1's lab notebook does not tell a student to submit after an outage,
   and week 2's does.** Section 6.3 works around it by putting the sentence in
   your week 1 announcement instead. The cleaner fix is for
   `builder/lab/notebooks/w1-lab.ipynb`, cell 15, to match
   `builder/lab/notebooks/w2-lab.ipynb`, cell 16. That is a change to the lab
   notebooks, which this package does not own.
5. **Discussion and self-check grading is not covered here.** Discussions are 20
   points each and self-checks 12, both auto-weighted by group. The discussion
   facilitation notes are a separate file in this package.
