::: intro
This page is the advice your instructor would give you in person on day one. It
is short, it is specific to this course, and every item on it comes from a way
students have gotten stuck before.
:::

::: callout time | Plan the hours before the term starts
Assigned work runs about **5 to 9 hours a week**, reading included. Every
Overview page itemizes its own week, so plan from those numbers.

Coding takes longer when it is new. Students with no programming background
commonly spend two to three times the assigned time on the coding parts. That
puts a realistic week between about **10 and 20 hours**. The range is normal,
not a sign of falling behind.

Open a calendar right now and block the wider figure. Four sittings a week
works better than one long day, because most problems here need a night of not
thinking about them.

If those hours are not available to you this term, talk to an advisor now
rather than in week five. That is a scheduling problem, not a failure.
:::

::: section | A weekly rhythm that works
Every week has the same four parts, so you can run the same routine each time.

1. **Early in the week, read the Overview page.** It says what is due and about
   how long each piece takes. Five minutes here saves hours later.
2. **Read the Content page before you touch the lab.** Students who open the
   lab first spend their time confused instead of building.
3. **Do the outside reading midweek.** It is capped at 45 minutes, and the
   Content page tells you exactly which part to read.
4. **Start the lab with days left, not hours.** Setup problems take a day to
   solve. They do not take an hour.
5. **Submit on Saturday.** The deadline is Sunday at 11:59 PM Central. Treat
   Sunday as your spare day, not your work day.
:::

::: section | The habit that matters most: ask on day one
The most common way to fail this course is to get stuck quietly.

A student stuck on Tuesday who posts on Tuesday loses an hour. The same student
who waits until Sunday loses the week, and then starts the next week behind.
That is how one bad week turns into four.

So set yourself a rule: **thirty minutes of no progress, and you post.** Not
because you gave up. Because that is what an engineer does.

The Q and A Discussion Board is checked every weekday, and answers usually
arrive within one business day. Your question is almost never unique.
:::

::: section | How to ask so you get an answer
A good question gets fixed in one reply. A vague one takes four.

Include four things:

1. What you were trying to do.
2. The exact command you ran.
3. What you expected.
4. What happened, with the **error text copied and pasted**, not described.

Never paste your API key, and never post a screenshot showing one.
:::

::: section | Use the autograder as a tool, not a verdict
Most of your code is scored by tests you can run yourself, as many times as you
want, before the deadline.

```
python -m pytest tests/ -q
```

Run it the moment you start, so you can see what failing looks like. Run it
after every small change. A test that just turned green tells you exactly which
change worked.

Do not save it for the end. A student who first runs the tests on Sunday night
finds out on Sunday night.
:::

::: callout warning | Week 3 is the hard one
Week 3 carries the biggest idea in the course. Up to then, your script calls the
model. From then on, the model calls your function. That flip confuses almost
everyone the first time.

The course is built to absorb it. The Week 3 checkpoint is pass or fail, not
graded on quality. A working branch is published on day 18, before the deadline.
The common errors are posted on day 15, before you hit them.

So if week 3 feels hard, nothing has gone wrong. Slow down, read the annotated
skeleton line by line, and post your question early.
:::

::: section | Read the error, all of it
Beginners skim errors. The habit that separates people who get unstuck is
reading the whole thing.

1. Read the **last** line first. It names the actual problem.
2. Then find the line in the trace that names **your** file. That is where you
   look.
3. Copy the exact error text into a search or into the board.

Most errors in this course are one of three things: a name spelled differently
than you remember, a file in a different folder than you thought, or a key you
have not set yet.
:::

::: section | Keep your evidence
Your grade in the second half of the term comes from artifacts, not memory.
Several quiz items ask for a value out of your own run files.

So keep them. Do not clear your results folder to tidy up. When something works,
write down the command that made it work.

A plain text file with your working commands, your result lines, and short notes
is worth more here than any set of notes on the reading.
:::

::: section | About failing at something
You will run something and it will not work. That is not a sign you are behind.
It is most of the job.

Security work in particular is built on negative results. An attack that fails
five times out of five is a finding, and a real one. A fix that holds is only
interesting because you first watched the attack land.

The two checkpoints in this course exist for this reason. They are pass or fail
and they are diagnostic. Their only question is whether you are stuck, so that
someone can help before it costs you a grade.
:::

::: callout tip | Five small things that pay off
1. **Work offline first.** The labs ship with an offline provider, so you can
   build and test with no key and no internet.
2. **Turn on Canvas notifications** for announcements and due dates.
3. **Reread the Rules of Engagement in week 5**, when the attacks start.
4. **Write your findings the day you run the attack**, while the details are in
   front of you.
5. **Back up your repository** somewhere other than one laptop.
:::

::: next
Next is How to Navigate Canvas, which covers the buttons and settings you use
every week.
:::
