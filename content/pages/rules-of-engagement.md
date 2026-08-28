::: intro
This page is the most important one in the course. It says what you are
allowed to attack, and what you are never allowed to attack. Read all of it.
You have to pass a quiz on it before Week 2 opens.
:::

::: callout stop | The short version
You may attack three things. The lab target app. Your own copy of the agent.
A model running on your own computer.

Nothing else. Ever. Not for a minute. Not to test something.
:::

::: scope | Why a course has rules like this
Security testing is legal work when someone has said yes. It is a crime when
nobody has.

The word for that yes is **authorization**. In a real job, it comes as a
signed document. It names the systems you may touch. It names the dates. It
names what you may not do.

That document is called the rules of engagement. This page is yours.

Real security work starts with scope, not with tools. A tester who finds a
serious bug in a system nobody hired them to test has not done good work. They
have caused a problem for their employer and for themselves.

Scope first. Technique second. That order never changes.
:::

::: section | Clause 1: What you may attack
You **may** attack these three things:

1. **The HelpDesk Lite app** in your lab repository. It runs on your own
   computer. It was built to be broken. Breaking it is the assignment.
2. **Your own copy of the agent** in your lab repository. You may change it,
   break it, and attack it however you like.
3. **A language model running on your own computer**, such as one you started
   with Ollama.

That is the whole list.
:::

::: section | Clause 2: What you may never attack
You **may never** point any tool from this course at:

1. Any website, app, or server that is not on the list in clause 1.
2. Any commercial AI service. This includes ChatGPT, Claude, Gemini, Groq, and
   any other hosted model.
3. Any system owned by the college, including Canvas, ACES, and campus Wi-Fi.
4. Any system owned by your job, your friends, or your family.
5. Any system you found by accident and think might be vulnerable.

"I only tried it once" is not a defense. "It was already broken" is not a
defense. "I wanted to see if it worked" is not a defense.
:::

::: callout warning | Attacking a hosted AI service is a real risk
Every commercial AI provider bans adversarial testing in its terms of use.

Google's policy bans getting around safety filters. It has no research
exception at all.

Groq's policy bans prompts meant to get around its safety systems. It does
offer a way to ask for written permission first.

If you break these terms, the provider can close your account. You lose the
key you need for this course. That is a graded problem as well as a real one.

This is why every attack lab in this course points at the lab app instead. You
attack the application's trust boundary. You do not attack the model's safety
filters. That is also better practice, because the trust boundary is where
real incidents happen.
:::

::: section | Clause 3: Your API key
1. You use **your own key**, not a shared one, and not anyone else's.
2. You keep your key in a file named `.env`. That file is never committed.
3. You never paste a key into `lab.config.yaml`, into a forum post, into a
   screenshot, or into a chat with a classmate.
4. If you think your key leaked, you turn it off at the provider and make a
   new one. Then you tell your instructor. Nobody is in trouble for reporting
   this quickly.

The lab code checks for a key in the wrong place and refuses to start. That
check is a safety net. It is not permission to be careless.
:::

::: section | Clause 4: The data in your labs
Everything in HelpDesk Lite is made up. The customers are not real. The email
addresses use domains that cannot receive mail. The secrets are fake strings
placed there so you can find them.

You may not add real data to it. Not a real person's name. Not a real address.
Not a real password. Not a real ticket from a job you have.

If a lab ever asks you to use real data, that is a mistake in the lab. Report
it and do not do it.
:::

::: section | Clause 5: Sharing your work
You may share:

- Your code with your instructor.
- Your ideas and your questions on the Q and A board.
- Your finished work with an employer, after the term ends.

You may not share:

- Your API key, with anyone, for any reason.
- A working attack aimed at any system outside clause 1.

You may talk with classmates about how an attack works. That is how the field
learns. Your evidence still has to be your own. Your lab contains fake secrets
built from your student ID, so your proof is different from everyone else's.
A classmate can hand you a payload. They cannot hand you your proof.
:::

::: section | Clause 6: If you find something real
One day, outside this course, you will notice a real problem in a real system.
It happens to people who learn this material.

Here is what to do:

1. **Stop.** Do not test it further. Looking is one thing. Poking is another.
2. **Write down what you saw**, with the time and date.
3. **Tell one person** who can act: the system owner, or your manager, or your
   instructor.
4. **Do not post it publicly.** Not on social media, not in a group chat.
5. **Do not use it**, even to prove it is real.

Reporting is the skill. Exploiting is not.
:::

::: section | Clause 7: What happens if you break these rules
Breaking clause 1 or clause 2 is a violation of the Alamo Colleges student code
of conduct, and it may also break state or federal law.

In this course, it means a zero on the work involved and a referral to the
Dean of Student Success. Depending on what happened, it can mean more.

This is not here to scare you. It is here so nobody can say they did not know.
:::

::: checkpoint | Before you take the quiz
Ask yourself each of these. If you are not sure of an answer, read the clause
again.

1. Name the three things you may attack.
2. A classmate posts a working prompt injection against a public chatbot. May
   you try it? Which clause says so?
3. Your key stopped working. Where do you put the new one?
4. You find a login page at your job that accepts any password. What are the
   five steps?
5. In your own words, what is the one thing you may never do in this course?

That last question is on the quiz, and it is a writing question. Your answer is
quoted back to you in the final exam.
:::

::: sources
Alamo Colleges District Student Code of Conduct.

Google Generative AI Prohibited Use Policy, and the Groq Acceptable Use and
Responsible AI Policy, both linked on the Course Material page.

This page maps to NIST AI RMF GOVERN 4.3, which asks that an organization have
practices in place for AI testing and for sharing what testing finds.
:::
