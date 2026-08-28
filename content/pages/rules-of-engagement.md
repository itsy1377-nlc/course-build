::: keyfacts
| | |
|---|---|
| You may attack | The lab app, your own agent, a model on your own computer |
| Everything else | Never. Not once, not to test |
| To open Week 2 | 100 percent on the Module 0 Gate quiz |
| Your API key | Yours alone, kept in `.env`, never shared |
| Lab data | All invented. Never add anything real |
| Breaking clause 1 or 2 | A zero, and a Dean of Student Success referral |
:::

::: intro
This page says what you may attack and what you may never attack. You take a
quiz on it before Week 2 opens.
:::

::: scope | Why a course has rules like this
Security testing is legal work when someone has said yes. Without that yes it
**can be a crime**, and it breaks the student code of conduct either way.

The word for that yes is **authorization**. In a real job it is a signed
document naming the systems, the dates, and the limits. This page is yours.

Scope first. Technique second. That order never changes.
:::

::: section | Clause 1: What you may attack
You **may** attack these three things:

1. **The HelpDesk Lite app** in your lab repository. It runs on your own
   computer and was built to be broken.
2. **Your own copy of the agent** in your lab repository.
3. **A language model running on your own computer**, such as one you started
   with Ollama.

That is the whole list.
:::

::: section | Clause 2: What you may never attack
You **may never** point any tool from this course at:

1. Any website, app, or server not named in clause 1.
2. Any commercial AI service, including ChatGPT, Claude, Gemini, and Groq.
3. Any system owned by the college, including Canvas, ACES, and campus Wi-Fi.
4. Any system owned by your job, your friends, or your family.
5. Any system you found by accident and think might be vulnerable.

"I only tried it once" is not a defense. Neither is "it was already broken".
:::

::: callout warning | Hosted AI services are out of scope
Providers restrict adversarial testing in their terms of use. Some offer a
written permission path. Some run a disclosure program with good-faith research
terms.

None of that applies to you here. You have permission for the three things in
clause 1 and for nothing else.

Break a provider's terms and it can close your account, along with the key you
need here.

So every attack lab points at the lab app. You attack the application's trust
boundary, not the model's safety filters. That is where real incidents happen.
:::

::: section | Clause 3: Your API key
1. Use **your own key**, not a shared one and not anyone else's.
2. Keep it in a file named `.env`. That file is never committed.
3. Never paste a key into `lab.config.yaml`, a post, a screenshot, or a chat.
4. If a key leaks, turn it off at the provider, make a new one, and tell your
   instructor. Nobody is in trouble for reporting this quickly.

The lab code refuses to start when a key is in the wrong place. That is a safety
net, not permission.
:::

::: section | Clause 4: The data in your labs
Everything in HelpDesk Lite is invented. The secrets are fake strings placed
there for you to find.

Add no real data: no name, address, password, or ticket from your job.

If a lab asks you for real data, that is a mistake. Report it and do not do
it.
:::

::: section | Clause 5: Sharing your work
Share your code with your instructor, your questions on the Q and A board, and
your work with an employer after the term.

Never share your API key, or an attack aimed outside clause 1.

Talk with classmates about how an attack works. Your evidence still has to be
your own. A classmate can hand you a payload, not your proof.
:::

::: steps | Clause 6: If you find something real outside this course
1. **Stop.** Looking is one thing and poking is another. That is a habit, not
   the legal line.
2. **Write down what you saw**, with the time and date. Notes only. Do not copy,
   download, or screenshot any data. Keeping it is more exposure.
3. **Report it in writing to someone who can act.** At work that is the security
   team or the published reporting channel, not your instructor. Keep a copy of
   what you sent.
4. **With no obvious owner**, try three places: a security.txt file at the site
   root, the organization's published vulnerability disclosure program, or a
   national coordination body.
5. **Do not post it publicly**, and **do not use it**, even to prove it is real.

Reporting is the skill. Exploiting is not.
:::

::: section | Clause 7: What happens if you break these rules
Breaking clause 1 or clause 2 violates the Alamo Colleges student code of
conduct. It may also break state or federal law.

Here it means a zero on that work and a referral to the Dean of Student
Success. It can mean more.

This is here so nobody can say they did not know.
:::

::: checkpoint | Before you take the quiz
1. Name the three things you may attack.
2. A classmate posts an attack on a public chatbot. May you try it? Which clause
   says so?
3. Your key stopped working. Where does the new one go?
4. You find a login page at work that takes any password. What do you do?
5. What is the one thing you may never do in this course?
:::

::: sources
Alamo Colleges District Student Code of Conduct.

Google Generative AI Prohibited Use Policy and the Groq Acceptable Use and
Responsible AI Policy, both linked on the Course Material page.

This page maps to NIST AI RMF GOVERN 4.3, on practices for AI testing and for
sharing what it finds.
:::
