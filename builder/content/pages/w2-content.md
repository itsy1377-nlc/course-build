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
| `confidence` | a number from 0 to 1 |
| `indicators` | short facts that support the verdict |

A **verdict** is the agent's judgment on one email. Two values are allowed and nothing else. That's what lets your code group forty answers into two piles.

A **category** is the kind of email the agent thinks this is. The seven kinds come from one file in the course corpus. In week 7 you score your agent against that same list. So the words you ask for now are the words you're measured on later.

**Confidence** is a number saying how sure the model is. It runs from 0 to 1. Read it as the model's own report, not as a fact about the email. A high number on a wrong answer is still wrong. The number is good for sorting, and for picking out the ones a person should see.

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

The course schema says four things.

1. All four names have to be there.
2. `verdict` has to be malicious or benign.
3. `category` has to be one of the seven.
4. `confidence` has to be a number from 0 to 1.

That rule does two jobs at once. It tells the model what to write, because your notebook puts the rule into the prompt in plain words. It also lets your code decide whether a reply is usable, before anything else touches it.

One written rule doing both jobs is the part worth noticing. Change it in one place, and the request and the check move together.

Your notebook ships `schema_errors()` already written. Hand it an answer and it hands back a list of problems in plain words. An empty list means the answer is good.

You never have to guess what went wrong. Part 2 shows you what to do with the list.
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
Your code loads a reply and no error comes back. Then you look at it. The `confidence` value is the word "high" instead of a number.

Which step catches that, the load or the schema check? Answer before you read the next line.

The schema check. Text is a fine JSON value, so the load is happy. The schema is the only rule that says this field holds a number from 0 to 1.
:::

::: section | The sidebar
Run the **Week 2 sidebar notebook** before you open the lab. All three parts use weather readings from a rooftop station.

2A reads values out of a dictionary by name. 2B turns a line of JSON text into a dictionary. 2C asks a fake gauge up to three times and stops on the first good reading.

The lab does those same three moves on email. The names are different, so you can't paste sidebar code into the lab.
:::

::: section | Read part 2 next
Part 2 of this week's reading is **When the answer comes back wrong**. It covers the three shapes a broken answer arrives in, and the retry that fixes most of them.

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
