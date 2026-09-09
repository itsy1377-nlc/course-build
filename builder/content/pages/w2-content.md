::: intro
Last week the model answered you in sentences. A sentence reads well, and your code can't do anything with it, so this week the answer comes back as named values your code reads one at a time.

This page covers what that shape is and why your code needs it. Part 2 covers what to do when the shape comes back wrong, because sooner or later it will.

Give this page 20 minutes. Part 2 takes another 22.
:::

::: video w2-walkthrough | What success looks like
About four minutes. A full week 2 run: four emails, a failed try, a retry, and the file the notebook writes.
:::

::: section | Why a sentence is not an answer
**Structured output is an answer that arrives in a fixed shape your code can read.**

Free text is the other thing. Ask the model about an email and you get a paragraph. Ask again and you get a different paragraph. Both may be right. Neither can be sorted, counted or scored.

Picture forty emails and one hour of your shift. You want the bad ones at the top of the list. You want a count of each kind before you go home. You want the doubtful ones handed to a person.

Every one of those jobs is your code reading a value. A paragraph holds no values. It holds words about values, and the words move every time you ask.

So you ask for named values instead.

This week your agent asks for four names.

| Name | What it holds |
|---|---|
| `verdict` | malicious or benign |
| `category` | one of seven kinds of email |
| `confidence` | a number from 0 to 0.9 in this lab |
| `indicators` | short facts that support the verdict |

A **verdict** is the agent's judgment on one email. Two values are allowed and nothing else. That's what lets your code group forty answers into two piles.

A **category** is the kind of email the agent thinks this is. The seven kinds come from one file in the course corpus. In week 7 you score your agent against that same list. So the words you ask for now are the words you're measured on later.

**Confidence** is the model's own report of how sure it is. It isn't a fact about the email, and a high number on a wrong answer is still wrong. Week 2 uses 0.9 as a reporting limit so you can see the contract reject and repair a number.

`0.9` is a reporting limit in this lab. It doesn't make the model less sure or more accurate. When `0.95` is rejected and `0.85` comes back, the model corrected its report to fit the contract. It didn't prove that its judgment changed.

An **indicator** is one short fact behind the verdict, such as a web address that imitates a real one. Ask for a few of these, not an essay. They're the part a person can check.
:::

::: section | Text that looks like a dictionary is not one
The model sends back characters. That's all it can send. A reply arrives over the network as text.

JSON is a plain text way to write named values. A line of JSON can look exactly like a Python dictionary. It's still text until your code loads it.

```json
{"verdict": "malicious", "category": "credential_phish",
 "confidence": 0.9,
 "indicators": ["asks for a password", "web address imitates a real one"]}
```

You can't ask that for its `verdict` yet. Ask, and Python hands you one character. `json.loads()` is the step that turns the text into a dictionary. After it runs, `answer["verdict"]` works.

Week 0 section 4 covers this move. Sidebar 2B runs it again on a weather reading.
:::

::: section | What a schema buys you
**A schema is the written rule saying which names an answer must carry and which values are allowed.**

The course schema sets these rules in week 2.

1. The answer has exactly four names.
2. `verdict` is malicious or benign.
3. `category` is one of the seven course categories.
4. `confidence` is a number from 0 to 0.9.
5. `indicators` is a list with one to six text items.

That one rule does two jobs. The notebook writes it into the prompt in plain words. The checker reads the same rule before anything else uses the answer.

Change the high value in `OUTPUT_SCHEMA`, and the request and check move together. That single source matters: a prompt asking for 0 to 1 while a checker enforces 0 to 0.9 would be an unfair contract.

Your notebook ships `schema_errors()` already written. Hand it an answer and it hands back a list of problems in plain words. An empty list means the answer passed the contract.

Passing the contract doesn't prove the verdict or confidence is true. Part 2 shows what to do with the problem list.
:::

::: section | Valid JSON can still be a wrong answer
A reply can load cleanly and still be no use.

```json
{"verdict": "malicious", "category": "phishing_attempt",
 "confidence": 0.8, "indicators": ["urgent tone"]}
```

`json.loads()` accepts that. Every bracket and quote is in place. The category is still not one this course uses.

Nothing downstream can act on `phishing_attempt`. A count by category would grow an eighth column that nobody asked for.

Loading isn't checking. Loading asks one question: is this text JSON? Checking asks a different one: is this an answer I can act on?

You need both, in that order. Nothing can be checked until the text is a dictionary.
:::

::: callout note | Stop and think
Your code loads a reply and no error comes back. Its `confidence` is `0.95`.

Which step rejects it in this lab, the load or the schema check? Answer before you read the next line.

The schema check. `0.95` is a valid JSON number, so the load is happy. The week 2 reporting rule stops at `0.9`. Rejecting the number proves a contract mismatch, not that the model became less sure.
:::

::: section | The sidebar
Run the **Week 2 sidebar notebook** before you open the lab. All four parts use weather readings from a rooftop station.

2A reads values out of a dictionary. 2B turns JSON text into a dictionary. 2C loads a candidate and accepts it only after a check. 2D shows why an empty problem list means the candidate passed.

The lab makes those same moves on email. The names are different, so you can't paste sidebar code into the lab.
:::

::: section | Read part 2 next
Part 2 of this week's reading is **When the answer comes back wrong**. It covers load failures, a live range failure, and the retry that sends the exact problems back.

Read it before you open the lab.
:::

::: reading | The JSON standard
This is the standard that defines JSON itself. It's short, and free to read with no account. Read section 1 and section 4, which covers objects.

Ask yourself one thing while you read. Does the standard say anything about which names an object must carry?

[The JavaScript Object Notation (JSON) Data Interchange Format, RFC 8259](https://www.rfc-editor.org/rfc/rfc8259)
:::

::: sources | Sources
| Source | What it gives this page |
|---|---|
| *The JavaScript Object Notation (JSON) Data Interchange Format*. RFC 8259, Internet Engineering Task Force, December 2017. [rfc-editor.org](https://www.rfc-editor.org/rfc/rfc8259) | The JSON format itself. Free to read, no account |

The seven categories this page refers to are read from a course corpus file, the same file the lab notebook loads.
:::
