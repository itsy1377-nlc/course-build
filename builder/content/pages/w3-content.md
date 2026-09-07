::: intro
Your agent still sends the whole email body and nothing else. This week you choose what goes in beside it, and that choice turns out to be most of the job.

This page covers which facts a verdict needs, and what each extra line in the prompt costs you.

Give this page 45 minutes.
:::

::: video w3-walkthrough | What success looks like
About four minutes. Six emails run twice, the table that compares the two runs, and the file the notebook writes.
:::

::: section | The model is not a detector
**Grounding is sending the facts about a message instead of the message alone.** A **facts block** is a short labeled list of those facts, written into the prompt.

Start with what the model can't do. It never opens the mail file, it runs no checks, and it looks nothing up.

It reads the text you sent and hands back a judgment, so it's a judgment layer over facts you pulled out yourself. Whatever you leave out doesn't exist to it.

Week 2 sent the body alone, so your verdict rested on wording. A confident answer isn't evidence.
:::

::: section | Two emails, and the reason for all this
Two of this week's six emails were built for this lesson. Email 019 reads like trouble. The finance director asks for a payment to be moved today, and wants a call before three.

Email 016 reads like ordinary business. A supplier you buy from every month sends new bank details for the next invoice.

The truth runs the other way. 019 is your own finance director, and the message never left the company. 016 is a stranger, and the address it asks you to reply to drops one letter from the supplier's own. No care with the body separates them. The facts block holds both answers.
:::

::: section | The email that does not settle this week
Email 005 doesn't settle this week, and that isn't your code. The two facts that clear it are that Slatemoor is an approved supplier, and that the link host is theirs. Neither is a header, so no facts block can carry them.

They arrive in week 5, when your agent can ask two tools for itself. Grounding isn't the last thing you add. It's the first.

::: section | What goes in the facts block
A **header** is one named line above the body, such as `From:` or `Subject:`. Your mail gateway adds headers of its own before a message reaches a mailbox.

Your notebook ships a parser, which reads one mail file and hands back its parts by name. These are the parts that go into the prompt.

| Fact | What it answers |
|---|---|
| Sender name, address and domain | Who the message says it is from |
| Reply address | Where your answer would go |
| Subject | What it claims to be about |
| The three check results | Whether the mail came from the domain it names |
| Display-name mismatch | Whether that name belongs to that domain |
| Link hosts | Where a click would land |
| Outside-mail flag and scan result | What the gateway already decided |
| Attachment filename | What arrived with the message |

You write `build_facts()`, which picks those values out of the parsed email. Then you write `format_facts()`, which prints them as labeled lines in a fixed order.
:::

::: section | What a passed check really means
Three headers carry the sender checks.

- **SPF** asks whether the sending server is allowed to send for the sender's domain.
- **DKIM** checks a signature that the sending domain put on the message.
- **DMARC** asks whether either of those passed for the domain shown in `From:`, then applies that domain owner's published rule.

Your gateway already ran all three and wrote the results down, and your code reads them rather than repeating the work. Here are two headers from email 004.

```text
From: Rutger Palomares <r.palomares@pellgrave-corp.example>
Authentication-Results: mx.pellgrave.example;
  spf=pass smtp.mailfrom=pellgrave-corp.example;
  dkim=pass header.d=pellgrave-corp.example header.s=k1
    header.i=@pellgrave-corp.example;
  dmarc=pass header.from=pellgrave-corp.example policy.dmarc=none
```

Three passes, and the message is malicious anyway.

A pass says the mail really came from `pellgrave-corp.example`, and that somebody set that domain up properly. That somebody is the attacker, because Pellgrave's own domain is `pellgrave.example`.

So a pass is one answered question, not a clean message. Now the same two headers on email 006.

```text
From: Pellgrave IT Help Desk <helpdesk@pellgrave.example>
Authentication-Results: mx.pellgrave.example;
  spf=fail smtp.mailfrom=pellgrave.example;
  dkim=none;
  dmarc=fail header.from=pellgrave.example policy.dmarc=quarantine
```

That one claims your own help desk and fails all three. Both results are facts, and neither is a verdict.

One case has no results at all. Pellgrave's gateway checks what arrives from outside, so mail sent inside the company carries no such header. Missing isn't failed.
:::

::: section | The name over the address
Rutger Palomares is Pellgrave's chief financial officer, and his mail comes from `pellgrave.example`. The message above puts his name over another domain.

**A display-name mismatch is a name that belongs to one domain sitting over an address at another.**

The three checks test domains, and none of them looks at the name. The name is the part a reader actually reads.

Email 005 passes the same three checks and is benign. Its name and its domain belong to the same supplier.

Your notebook ships a list of names and the domain each belongs to. The parser compares them and hands back `display_name_mismatch`, so send it.
:::

::: section | Where the links point
A **link host** is the part of a web address right after the slashes, such as `billing.slatemoorsupply.example`.

The host decides where a click lands, not the words on the button. So the host is the fact.

Your prompt carries two shipped files beside the facts. The **known-good domain** list names Pellgrave's own domain and its own web hosts, and the **playbook** holds the eleven rules Pellgrave triage follows.

One rule matters most here. A host that isn't on the known-good list is unknown rather than clean. Week 4 gives your agent a way to look one up.
:::

::: section | What you leave out is also a decision
**Data minimization means keeping and sending the least data the work needs.**

Every line you add to a prompt is a line you've handed to an outside service. The model runs on somebody else's computers, so whatever you send, you've disclosed.

The parser hands back far more than the table above. Ask two questions of anything else.

1. Would a sound verdict change if this were missing?
2. What does it cost the company if this leaves the building?

Plenty of values fail both. The routing hops, the whole raw header list, the message id, the address of the colleague who reported it. None of those moves a verdict, and each is a real detail about a real person.

Your written answer names one fact you left out and why. Choose it while you write the code, not afterwards.
:::

::: section | The same move on a log line
Nothing on this page is really about email.

A log line, an alert, a ticket or a machine notice arrives with more fields than any one judgment needs. You drop the fields nobody needs, put the rest in one steady shape, and send that.

Log work named those two steps long before anyone sent text to a model. Dropping unneeded fields is event reduction, and making each field consistent is normalization.

`build_facts()` is the first step and `format_facts()` is the second.
:::

::: section | The sidebar, then the lab
Run the **Week 3 sidebar notebook** first. It builds one line per student for a class sign-in sheet, out of several fields, in an order you choose. That's the move `format_facts()` makes. The names differ, so sidebar code pasted into the lab fails.

In the lab, cell 14 runs all six emails both ways and prints the comparison table.
:::

::: reading | One source to open
This is a free guide to email security from a United States standards agency. Read section 4.2, which runs about two pages.

Ask yourself one thing while you read. If all three checks passed, what has still not been checked?

Ten minutes. You're skimming this, not studying it.

[Trustworthy Email, NIST SP 800-177 Revision 1](https://csrc.nist.gov/pubs/sp/800/177/r1/final)
:::

::: sources | Sources
The three NIST publications are United States government work, free to reuse. The CISA guidance is marked TLP:CLEAR, so it may be shared freely. The four standards are free to read with no account. Only the first is assigned, so only it carries a link.

| Source | What it grounds here |
|---|---|
| [Trustworthy Email](https://csrc.nist.gov/pubs/sp/800/177/r1/final). NIST, SP 800-177 Revision 1, February 2019 | The facts a faked message gets wrong, and why a passing check is not a clean message |
| *Phishing Guidance: Stopping the Attack Cycle at Phase One*. CISA, NSA, FBI and MS-ISAC, October 2023 | What the three checks do, and what a failed check means |
| *Sender Policy Framework (SPF) for Authorizing Use of Domains in Email, Version 1*. RFC 7208, Internet Engineering Task Force, April 2014 | What SPF checks, and why a pass says nothing about the address you see |
| *DomainKeys Identified Mail (DKIM) Signatures*. RFC 6376, Internet Engineering Task Force, September 2011 | What a signature claims, and why the signing domain is worth comparing |
| *Domain-Based Message Authentication, Reporting, and Conformance (DMARC)*. RFC 9989, Internet Engineering Task Force, May 2026 | The match against the From domain, and display names sitting outside it |
| *Message Header Field for Indicating Message Authentication Status*. RFC 8601, Internet Engineering Task Force, May 2019 | The header your facts block reads, and why the results are written down |
| *Guide to Protecting the Confidentiality of Personally Identifiable Information (PII)*. NIST, SP 800-122, April 2010 | Data minimization, and keeping the least amount the work needs |
| *Guide to Computer Security Log Management*. NIST, SP 800-92, September 2006 | The same pattern on a log line: drop the fields nobody needs |

Two things here are the course's own. The **known-good domain** list and the playbook are Pellgrave files. And no document above calls a model a judgment layer over facts.
:::
