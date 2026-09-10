::: intro
This page defines every technical word this course uses.
:::

::: keyfacts
|  |  |
|---|---|
| What this page is | Every technical word the course uses, in plain language |
| How it is ordered | A to Z |
| The last column | Where that word first shows up |
:::

::: section | How to use this page
You don't read this page from top to bottom. You come here when a word stops you. Search it with Control and F, or Command and F on a Mac. **Start** in the last column means the orientation pages. **0** means the optional week 0 on-ramp.
:::

::: section | A to B
| Term | What it means | First used |
|---|---|---|
| **Accuracy** | The share of emails the agent judged correctly. | 7 |
| **Agent** | A program that sends text to a model, reads the answer, and acts on it. | Start |
| **Agentic workflow** | Software that picks its own next step and then takes it, inside set limits. | 1 |
| **Alert** | A record that something looked worth a person's time. | 1 |
| **Allowlist** | A list of link hosts your organization has already checked and cleared. | 4 |
| **Analyst** | The person who reviews reported items and decides what happens next. | 1 |
| **API** | A way for one program to ask another program for something. | 1 |
| **API key** | A secret string that proves your code may use the model. The course sets it for you and never shows it. | Start |
| **Asset** | Anything the organization owns and has to protect, such as a laptop or a file server. | 1 |
| **Authentication** | Checks a mail system runs to test whether a message really came from the domain it names. | 3 |
| **Automation bias** | Trusting an answer because your agent produced it. | 6 |
| **Batch run** | One sitting in which the agent reads many emails in a row. | 7 |
| **Bec** | `bec`, business email compromise. A trusted person's name used to get money, gift cards, a payroll change, data or a quiet reply. Usually no link and no file. Malicious. | 2 |
| **Blocklist** | A list of link hosts your organization has already judged bad. | 4 |
| **Bounded loop** | A loop with a hard limit on how many times it may repeat. It always ends. | 5 |
| **Business email compromise** | The full name for `bec`. See that entry above. | 2 |
:::

::: section | C to D
| Term | What it means | First used |
|---|---|---|
| **Call** | Running a function by writing its name with parentheses after it. | 0 |
| **Category** | The kind of email the model reports. Seven are allowed, and each one belongs to exactly one verdict. They are listed under their own names below, and in `corpus/spec/categories.json`. | 2 |
| **Cell** | One block in a notebook that you run on its own. | Start |
| **Confidence** | A number from 0 to 1 saying how sure the model is of its answer. | 2 |
| **Confidence threshold** | A floor you set. Any answer below it goes to a person. | 6 |
| **Counter** | A variable that holds a running total and goes up by one each time around a loop. | 0 |
| **Credential phish** | `credential_phish`. A link or sign-in request meant to capture a password, dressed as a vendor, a system or a share notice. Malicious. | 2 |
| **Data exposure** | Putting information somewhere it should not go. | 6 |
| **Data minimization** | Sending only the facts a sound judgment needs, and nothing more. | 3 |
| **Data, not instructions** | Treating text inside an email as evidence to read, never as an order to follow. | 6 |
| **Default** | A value a function uses for a parameter when you do not supply one. | 0 |
| **Delimiter** | A marker placed before and after a block of text to show where it starts and ends. The pair around your email body is the fence. Your code takes both markers out of the body before it uses the body, and a message that arrived carrying one escalates with the reason `fence_broken`. | 6 |
| **Dictionary** | A collection that holds values by name. You read one by giving its key. | Start |
| **Disclosure** | A short note saying where and how you used an AI tool on your work. | Start |
| **Display name** | The name shown beside an address in your mail app. Anyone can set it to anything. | 3 |
| **Display-name mismatch** | A name from one domain sitting over an address at another. | 3 |
| **DKIM** | DomainKeys Identified Mail. A signature on a message. A pass means the signed parts were not changed on the way. | 3 |
| **DMARC** | Domain-based Message Authentication, Reporting and Conformance. It checks that a passing SPF or DKIM matches the visible sender domain. | 3 |
| **Domain** | The part of an email address after the at sign. | 3 |
:::

::: section | E to G
| Term | What it means | First used |
|---|---|---|
| **Endpoint** | A computer, laptop or phone that a person works on. | 1 |
| **Error type** | The name Python gives a failure, such as NameError. | 0 |
| **Escalation** | Handing a case to a person instead of closing it yourself. | 1 |
| **Escalation reason** | The short label saying why a case went to a person. Your guarded row records one reason: `token_cap`, `fence_broken`, `injection_detected`, `fact_contradiction`, `low_confidence`, or `none`. | 6 |
| **Export file** | The file a lab writes at the end of your run. You hand it in. | Start |
| **Fact check** | Comparing the model's answer against facts you already pulled out, and rejecting what you cannot find. | 6 |
| **Facts block** | A short labeled list of facts about one email, written into the prompt. | 3 |
| **False negative** | A malicious email the agent called benign. This is the costly mistake. | 7 |
| **False positive** | A benign email the agent called malicious. It wastes a person's time. | 7 |
| **for loop** | Code that does the same thing to each item in a list. | 0 |
| **f-string** | A string with an f before the opening quote. Values in braces drop into the text. | 0 |
| **Function** | A named block of code you can run again. It takes values in and hands one back. | 0 |
| **Function calling** | The setting that lets a model ask, in a fixed shape, for one of your functions to run. | 4 |
| **Generative AI** | AI that writes new text, code or images. | 1 |
| **Ground truth** | The correct answer for each email, written down before the agent ever ran. | 7 |
| **Grounding** | Sending extracted facts to the model instead of raw text alone. | 3 |
| **Guardrail** | A control placed around the model, meant to stop a bad answer becoming a bad action. Whether one does is measured, not assumed. | 6 |
:::

::: section | H to L
| Term | What it means | First used |
|---|---|---|
| **Hallucination** | A model stating something that is not in the facts it was given. | 6 |
| **Header** | A labeled line at the top of an email carrying facts about the message. | 3 |
| **Human review** | A rule that sends a case to a person before anything happens to it. | 6 |
| **if, elif and else** | Code that picks one path out of several based on a test. | 0 |
| **Incident** | A confirmed event that caused harm, or could have. | 1 |
| **Indicator** | One short fact that supports a verdict, such as a web address that imitates a real one. | 2 |
| **JSON** | A plain text way to write named values. Code converts it before reading those values. | 0 |
| **Key** | The name you use to read one value out of a dictionary. | 0 |
| **Kernel** | The part of the notebook server that runs your code. Restarting it clears most stuck cells. | Start |
| **Known-good domain** | A domain your organization owns or has already cleared. | 3 |
| **Lab** | The graded build work each week. Each one submits three things. | Start |
| **Legit external** | `legit_external`. Real mail from vendors, customers, banks and lists you subscribed to, including the ones that look alarming. Benign. | 2 |
| **Legit internal** | `legit_internal`. Real mail from inside the organization: people, the help desk, the ticket system, the gateway digest. Benign. | 2 |
| **Link host** | The site name inside a web address. It says which server you would reach. | 3 |
| **List** | A collection that holds items in order. You read one by its position. | 0 |
| **Log** | A record that something happened. Most log lines are ordinary. | 1 |
| **Loop** | Code that repeats. It runs the same lines again until a rule stops it. | 0 |
:::

::: section | M to P
| Term | What it means | First used |
|---|---|---|
| **Malformed output** | An answer that does not match the shape you asked for. | 2 |
| **Malicious and benign** | The two verdicts this course grades. Malicious means the message is an attack. Benign means it is safe. | 2 |
| **Malware delivery** | `malware_delivery`. A file the gateway removed for a blocked extension or a macro, or a link to a download host. Malicious. | 2 |
| **Model** | The AI service your code sends text to. It reads the text and writes an answer back. | 1 |
| **Module** | One part of the course, listed under Modules in the left menu. This course has the Orientation Module, Student Resources, Q and A, and one module per week. | Start |
| **Network** | The equipment that connects the organization's computers to each other and the internet. | 1 |
| **Notebook** | A web page where you write and run Python in blocks. | Start |
| **Notebook server** | The college's hosted service that runs your notebooks. Nothing installs on your computer. | Start |
| **Observe, decide, act** | The three things the agent repeats in a loop. It looks, it picks the next request, it runs it. | 5 |
| **Overreliance** | Letting your agent decide something a person should decide. | 6 |
| **Parameter** | A name in a function definition for a value the function takes in. | 0 |
| **Per-run token cap** | A cap that counts only the tokens the model wrote, added up across one triage. `TOKEN_CAP_PER_RUN` is 4000. The whole run costs more than that, and no cap reads it. | 6 |
| **Phishing** | A message written to trick you into giving up a password, a payment or data. | Start |
| **Plain-language summary** | Two short sentences for the person who reported the email, written in everyday words. | 7 |
| **Playbook** | A written list of rules an analyst follows when judging a message. | 3 |
| **Pre-written** | A cell that arrives finished and working. You run it. You do not write it. | Start |
| **Prompt** | The text you send to the model. | 1 |
| **Prompt injection** | Attacker text that a model reads as an instruction instead of as evidence. | 6 |
| **Python** | The programming language this course uses. | Start |
:::

::: section | Q to S
| Term | What it means | First used |
|---|---|---|
| **Rate limit** | A cap on how fast a key may send. This course allows 30 requests and 40,000 tokens a minute. Reaching it is normal in a busy cell, and the notebook waits and tries again. | 1 |
| **Reasoning block** | Text a model writes to itself before its answer. This course turns it off. | 2 |
| **Recipient record** | What your organization knows about the person who got the message. | 4 |
| **Recommended action** | What the triage note says should happen to the email next. | 7 |
| **Request** | One message your code sends to the model. | 1 |
| **Response** | What the model sends back. | 1 |
| **Retry** | Asking again when the answer came back in the wrong shape. | 2 |
| **Return value** | The value a function hands back. Store it or it is gone. | 0 |
| **Rubric** | The table of criteria your work is scored against. | Start |
| **Runaway loop** | A loop with no working stop rule. It repeats until something outside it stops it. | 5 |
| **Schema** | The written rule saying which names an answer must carry and which values are allowed. | 2 |
| **Scoring AI** | AI that sorts or rates things, such as a filter that scores every message. | 1 |
| **Security operations center** | The team that watches for attacks and handles what people report. At a small company it may be one person. | 1 |
| **Sender reputation** | What is already known about a sender from past reports. Good, bad, or never seen. | 4 |
| **Self-check** | A short graded quiz each week, worth 12 points, that checks whether the reading landed. | Start |
| **Sidebar** | A short ungraded practice notebook on an everyday topic. | Start |
| **Spam** | `spam`. Unsolicited commercial mail that asks for nothing but a click or a reply. Benign, because the team closes it and blocks nothing. A bulk message that asks for a password, a payment change, gift cards or data is not spam. | 2 |
| **SPF** | Sender Policy Framework. It checks whether the sending server is one the sender's domain allows. | 3 |
| **Step** | One pass through the loop: one look, one decision, one request. | 5 |
| **Step cap** | The largest number of steps a run may take before it has to answer. | 5 |
| **Stop condition** | The rule that ends a loop early once the answer is settled. | 5 |
| **Stop reason (loop)** | The short label saying why a run ended. | 5 |
| **Stop reason (model)** | The short label saying why the model stopped writing. | 2 |
| **String** | Text held in a variable, written inside quotation marks. | 0 |
| **Structured output** | An answer that arrives in a fixed shape your code can read. | 2 |
:::

::: section | T to Z
| Term | What it means | First used |
|---|---|---|
| **Temperature** | A setting on the model call. A low number makes answers steadier. A high one makes them vary. | 1 |
| **Ticket** | The record a team opens to track one piece of work to its close. | 1 |
| **TODO cell** | A cell with a comment marking the lines you write. | Start |
| **Token** | A chunk of text, roughly four characters. The model is measured and capped in tokens. | Start |
| **Token budget** | The tokens set aside for your work this term. Email your instructor if you run out. | Start |
| **Token count** | How many tokens a request and its answer used. Your notebook shows a running count. | 1 |
| **Tool** | A Python function the course ships that looks something up for the agent. | 4 |
| **Tool call** | The model asking, in a fixed shape, for one tool to run. Your code runs it, not the model. | 4 |
| **Traceback** | The block of text Python prints when a line fails. Read its last line first. | Start |
| **Triage** | Sorting reported items so the ones that need a person get one first. | Start |
| **Triage note** | The short written record an analyst leaves after judging one email. | 7 |
| **try and except** | Code that runs a line that might fail and says what to do if it does. | 0 |
| **User** | A person with an account at the organization. | 1 |
| **Variable** | A name that holds a value. You can change what it holds. | 0 |
| **Vendor fraud** | `vendor_fraud`. A supplier's invoice or thread, real or imitated, that sends payment to new bank details. Malicious. The difference from `bec` is who is imitated: a supplier, not a person you work with. | 2 |
| **Verdict** | The agent's judgment on one email: malicious or benign. | 2 |
| **Week** | One numbered part of the term. This course has seven teaching weeks, an exam week, and an optional week 0 on-ramp. | Start |
| **while loop** | Code that repeats until a stop rule is met. Always give it a cap. | 0 |
:::
