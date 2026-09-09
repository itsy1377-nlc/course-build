::: intro
You write one function this week, `ask_model()`. It sends text to the model and hands back the answer. Then you use it on two emails and watch how the answers behave.

Eleven to fourteen lines of your own code, in two clearly marked TODO cells. Everything else in the notebook is written for you. Plan about two and a half hours.
:::

::: directions
Work down the notebook in order. Run every cell, including the ones you didn't write.

1. Open the **Week 1 lab notebook** at **notebook.bashtion.dev**. It's already there, so there's nothing to download. Read the first two markdown cells.
2. Paste your key into the configuration cell, on the line reading `API_KEY = ""`, then run that cell. It prints **pasted in** once it has your key. If it still says NOT PASTED IN YET, check that you pasted between the two quotation marks.
3. Run the token counter cell, then the cell holding `send_request()` and `save_artifact()`. Read both. You use them in every week of this course.
4. Read the markdown cell that says what `ask_model()` has to do.
5. Fill in **TODO 1**, cell 7. Your `ask_model()` builds the request, merges in `MODEL_EXTRAS`, calls `send_request()`, and returns the answer text. That's 8 to 10 lines.
6. Run the check cell, cell 8. It first checks the outgoing request without contacting the model. If the request is built correctly, it asks the model one plain question. A passed request check, an answer and a token line mean your function works.
7. Run cell 9. It reads email 001 and prints the subject, the sender and the first part of the body.
8. Fill in **TODO 2**, cell 10. Send that body to the model with the instruction the cell gives you, then print the answer. That's 3 to 4 lines. The instruction is one sentence:

```
Read the email below. In two sentences, say whether it looks like a phishing attempt, and why.
```

9. Run cell 11, the temperature comparison. It asks for one word and one short sentence six times at temperature 0.2 and six times at 1.0. It prints two labelled groups and the number of distinct answers in each. **This is the cell you screenshot.**
10. Run cell 12. It sends email 002 and prints the answer with its token line. Compare that token count with the one from email 001, and notice which mail cost more.
11. Read cell 13. A higher temperature often allows more variation, but your small run may show more, the same number or fewer distinct answers. Every direction is a real result.
12. Run cell 14, the export cell. It writes `week1_first_calls.txt` and prints the full path to it.
13. Open the printed file and read it. Everything a grader needs is in there.

If a cell fails, read the last line of the traceback first. The **If something breaks** page carries the five step routine.
:::

::: grading | Grading Criteria
| Criterion | Points |
|---|---|
| Submission completeness. Screenshot, file and written answer are all present and readable. | 25 |
| The call works. The file shows both temperature groups for email 001 and one prose answer for email 002. It shows the prompt text used. | 25 |
| Variation reported. The written answer gives both distinct-answer counts and honestly reports whether the higher-temperature group showed more, the same number or fewer. | 25 |
| First judgment. The written answer names one specific thing to check before trusting the answer. | 25 |
| **Total** | **100** |
:::

::: submit
Three things, and nothing else. No folders, no zip files, no links.

1. **One screenshot.** Capture the output of cell 11, the temperature comparison. Use one image with both labelled groups, all twelve short answers and both distinct-answer counts readable. That cell prints no key material, so it's safe to capture.
2. **One file.** `week1_first_calls.txt`, attached as a file. Cell 14 writes it and names it. Find it in the file list on the left, right-click it, choose **Download**, then attach it here. Don't paste its text into the box.
3. **One written answer**, typed into the submission box. Answer all three questions in 3 to 5 sentences.

> Answer all three questions in 3 to 5 sentences. (1) How many distinct answers appeared at each temperature, and did the 1.0 group show more, the same number or fewer than the 0.2 group? (2) What happened to the token count on email 002, and why? (3) What would you check before trusting this answer in a real ticket?

Due Sunday 11:59 PM Central. You may use AI help on the written answer. If you do, add one line saying what you asked it.

New to screenshots? **Using the notebook server** shows how to take one on
Windows, Mac, Chromebook and Linux, and the four ways one loses points.
:::
