#!/usr/bin/env python3
"""Regenerate 039-cfo-pay-marlstone-today.

Rebuilds emails/batch/039-cfo-pay-marlstone-today.eml from the corpus seed,
refreshes the prose fields of its own record in spec/corpus-spec.json, and
upserts its ground truth record in ground_truth.json. It touches no other
record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_swk_" + hexid("boundary", 12)
    submission Received id = hexid("gateway-id", 12), also
                            X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256("<seed>|<id>|store-id")[:32],
                            version=4)

Nothing here calls time, random or uuid4 without a seeded hex, so the file is
byte reproducible. There is no sender-side hop and no DKIM-Signature on an
internally submitted message, so hexid("sender-id", 8) and the DKIM body hash
have nothing to sign here and are not derived. The delivering mail store is
read from data/recipients.json rather than typed in, because a mailbox lives on
exactly one store and the LMTP hop is a property of the mailbox, never of the
path the message took. The To address, the reporter and the mailbox this copy
was pulled from are all Priya Castellanos, so there is no list expansion to
unwind: recipients.json puts her on mailstore-01 and the LMTP hop names it.

This is the batch analog of 019. Same sender, same recipient, same two-hop
internal path, the same kind of ask one week later, and the same answer key
shape: benign verdict, escalation true. 019 teaches it in week 4; this one is
graded in week 7 with no worked example in front of the student.

Why this message carries no Authentication-Results, no Received-SPF, no
DKIM-Signature and no X-Sentrywick-External. The CFO's own laptop on the head
office network handed it to mail.pellgrave.example over an authenticated
submission, so the border gateway never saw it, never authenticated it and
never stamped it as external, and neither body part carries the gateway banner
(docs/email-header-realism.md sec. 8, and sec. 10 items 8 and 17). Missing is
not failed, which is playbook rule 11 and the most common wrong answer on this
record: an agent that reads three null results as three failures gets a
malicious verdict out of a message the headers clear. The gateway still writes
X-Sentrywick-Scan-Result on its own submissions, and X-Sentrywick-Reported-By,
because every corpus message was reported by someone.

The Received chain, two hops, top down:

    mail.pellgrave.example          -> mailstore-01.pellgrave.example (LMTP)
    PMG-LT-1042.corp.pellgrave.example [10.20.30.142]
                                    -> mail.pellgrave.example (ESMTPSA)

Both client addresses are RFC 1918 private space and the submission host is the
same 10.20.4.25 the rest of the internal corpus uses. PMG-LT-1042 is the same
laptop 019 was submitted from, because it is the same person at the same desk.

The boundary prefix names the product that composed the message. This one was
composed on a Pellgrave workstation and submitted through the organization's
own host, so it takes the internal prefix "=_swk_", the same one 002, 011, 015
and 019 carry (the rule is written out in gen_015's docstring).

Both parts are 7bit. The message is pure ASCII, every source line is under 78
characters, and there is no gateway banner to carry, so quoted-printable would
buy nothing and would only put soft line breaks through phrases an extractor
has to find whole.

Headers deliberately absent, matching the manifest indicator list: no Reply-To
(the author sends from his own client, so the RFC 5321 envelope identity and
the RFC 5322 author are the same mailbox and there is nothing to split), no
In-Reply-To and no References (thread:new, checked both ways by
validate_corpus.py), no Thread-Topic (the internal submission host stamps it
only on threaded mail and this message starts a thread), no
X-Sentrywick-Removed-Attachment (attachment:none), no Auto-Submitted (a person
typed this at a laptop), no X-Originating-IP (reserved for webmail
submissions, and header:x_originating_ip is checked both ways), no X-Priority
and no Importance. The subject already carries the deadline, so a priority
header would double the pressure the body is measured on and would add a
header:x_priority_high fact the record does not claim.

Body wording. The content codes are matched from the phrase lists in
spec/enums.json, and validate_corpus.py runs every list over both decoded parts
in both directions, so the wording has to carry exactly the phrases the record
claims and no others. Present, each whole on one line in both parts:

    content:payment_timing_request  "pay today", the required one.
    content:urgency_keywords        "today" (inside "pay today") and
                                    "before the 2 PM cutoff".
    content:phone_verification_offered  "call me".

The wording stays clear of every list the record does not claim, and the near
misses are worth naming because this message sits one word away from several:

    content:payment_request. "invoice", "past due", "remit", "net 30" and
    "amount due" are all out. See the departure note below: the thing being
    paid is named by its document number and the mass noun "billing", the way
    011 writes "billed" rather than "invoice".
    content:payment_change_request. Nothing about where the money goes
    changes, only when it goes, which is the whole distinction between this
    record and 023, the attacker who works the same vendor with a bank change.
    So no "new account", "new routing", "changed banks" or "update the vendor
    account".
    content:banking_instruction. No "wire", no "approve or return", no
    "decision required". The CFO is asking accounts payable to move a run
    date, not to decide a banking item.
    content:channel_restriction. This sender asks to be phoned, which is the
    opposite move from 004, the malicious CFO twin that says "email only" and
    "can't take calls".
    content:secrecy_request. Nothing is asked to be kept off the record.
    content:credential_request and content:file_share_lure. There is no link
    to sign in to and no file to fetch, which is what url:none and
    attachment:none key on and what leaves the week 5 loop with two calls and
    tools_exhausted.

ONE DELIBERATE DEPARTURE FROM THE AUTHORED body_brief, reported rather than
made quietly. The authored brief asked the body to name "the Marlstone April
invoice". "invoice" is an entry in the content:payment_request phrase list in
spec/enums.json, and the record does not carry that code, so
validate_corpus.py's phrase pass fails any body that uses the noun. The body
therefore names the same document as "Marlstone's April billing, 2026-04-PMG
against PO 20388": the same vendor, the same document number and the same
purchase order the brief names, in the mass-noun form the trade uses, with the
noun left out. The subject line is authored and keeps the word "invoice"; the
phrase pass reads only the decoded body parts, so the subject is untouched and
the file is clean. body_brief is rewritten below to record the decision.

Two things about this record are reported rather than changed, because both are
semantic and neither is the generator's to settle:

  1. The subject the manifest authors, "Marlstone invoice: pay today before the
     2 PM cutoff", carries "invoice", a content:payment_request phrase, while
     the record lists no content:payment_request. Nothing fails, because the
     phrase pass reads the body only, but a student whose extractor also reads
     the subject will produce a code the answer key does not hold.
  2. This message is dated Thu 2026-04-23 and asks for a document numbered
     2026-04-PMG, which is the same number the vendor's own covering mail
     carries in 037, dated Fri 2026-04-24. So the April billing is in the
     accounts payable queue a day before the vendor emails it. 023 makes the
     same assumption from 2026-04-22, and the vendor's allowlisted portal at
     portal.marlstonefleet.example carries the document, so the corpus already
     reads as a place where the billing is known before the covering mail
     lands. It is still a timeline a reader can trip over.

The ask is legitimate and reads badly, which is the point of the record. It
names the vendor, the document, the purchase order, the run it is on, the run
it should move to and the reason, and the verification it asks for is a phone
call to the extension the signature already carries, which is what an analyst
would have asked for anyway. The amount is deliberately not in the message: the
call is what confirms it, so quoting a figure here would make the call
pointless and the note would stop reading like a person who intends to pick up
the phone. That is the same reasoning 019 uses.

Run:  python3 corpus/tools/generators/gen_039_cfo_pay_marlstone_today.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "039-cfo-pay-marlstone-today"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER_DISPLAY = "Rutger Palomares"
SENDER = "r.palomares@pellgrave.example"
# The author sends from his own client, so the envelope sender and the From
# mailbox are the same address and the file carries no Sender header.
ENVELOPE_SENDER = SENDER
RECIPIENT_DISPLAY = "Priya Castellanos"
RECIPIENT = "p.castellanos@pellgrave.example"
# The person who received it is the person who reported it, so the mailbox the
# corpus copy was pulled from is the To address itself.
REPORTER = RECIPIENT

SUBJECT = "Marlstone invoice: pay today before the 2 PM cutoff"

# The CFO's laptop, named the way the head office asset tag names it, on the
# corporate client range. RFC 1918 throughout, and the submission host is the
# same 10.20.4.25 the rest of the internal path uses. 019 was submitted from
# this same laptop.
SUBMISSION_HOST = "PMG-LT-1042.corp.pellgrave.example"
SUBMISSION_IP = "10.20.30.142"
SUBMIT_HOST = "mail.pellgrave.example"
SUBMIT_IP = "10.20.4.25"

SCAN_RESULT = "clean"

# Thu 23 Apr 2026 11:40:00 -0500, the manifest date. The submission host stamps
# one second later, the store one second after that, and the Message-ID left
# side is the same instant in UTC: 11:40:00 -0500 is 16:40:00 UTC.
DATE_HEADER = "Thu, 23 Apr 2026 11:40:00 -0500"
SUBMIT_STAMP = "Thu, 23 Apr 2026 11:40:01 -0500"
STORE_STAMP = "Thu, 23 Apr 2026 11:40:02 -0500"
MESSAGE_ID_STAMP = "20260423164000"


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode("ascii")).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode("ascii")).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def mailstore(address):
    """The one store that delivers this mailbox, from data/recipients.json."""
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            store = record.get("mailstore")
            if not store:
                raise SystemExit("recipients.json has no mailstore for " + address)
            return store
    raise SystemExit("recipients.json has no record for " + address)


# ---------------------------------------------------------------- body text
#
# Each paragraph is one list of lines. Both parts are built from the same lists,
# so the plain text and the HTML text cannot drift and a part-to-part diff of
# the decoded words is empty apart from the tags. The line breaks are placed so
# that no phrase an extractor looks for is split: "pay today", "before the 2 PM
# cutoff" and "Call me" each sit whole on one line in both parts.

GREETING = "Priya,"

# The ask. Vendor, document number, purchase order, the run it is queued on,
# the run it should go out on, and the reason. "pay today" is the required
# content:payment_timing_request phrase and carries "today" with it, which is
# one of the two content:urgency_keywords hits.
PARA_1 = [
    "Marlstone's April billing, 2026-04-PMG against PO 20388, is queued for",
    "next week's run. Please pay today instead, in the 2 PM run, so the",
    "fleet lease stays current into May.",
]

# The verification. He asks to be phoned at the extension his own signature
# carries, which is the control an analyst would have asked for, and he says
# what does not change, which is the sentence that separates this record from
# 023 and from 016: the timing moves, the vendor account does not.
PARA_2 = [
    "Call me at ext. 4102 before the 2 PM cutoff and we will confirm the",
    "amount together before you release it. Nothing else about it changes:",
    "same vendor, same terms, only the run it goes out on.",
]

# The small irregularity real mail has: the reason the window is narrow, said
# in the way a person says it rather than in the way a policy says it.
PARA_3 = [
    "I am in the plant review from one o'clock, so the earlier you can",
    "catch me the better.",
]

SIGN_OFF = ["Thanks,", "Rutger"]

# The CFO's standard two-line block: name, then role, organization and the four
# digit extension. 019 and 055 carry the same block, and ext. 4102 is the number
# the body tells her to call, so the note names one number and names it twice.
SIGNATURE = [
    "Rutger Palomares",
    "Chief Financial Officer, Pellgrave Mechanical Group, ext. 4102",
]

PARAGRAPHS = [PARA_1, PARA_2, PARA_3]

# The phrases the record's content codes are matched from. Both decoded parts
# have to carry all of them, lowercased.
REQUIRED_PHRASES = ["pay today", "before the 2 pm cutoff", "call me", "today"]

# Phrases from the other lists in spec/enums.json that this body must not carry,
# because validate_corpus.py runs every list over the decoded parts and a hit
# with no indicator is a failure. The list is the near misses, not the whole
# vocabulary: the wording was written around these.
FORBIDDEN_PHRASES = [
    "invoice", "past due", "remit", "payment is due", "net 15", "net 30",
    "amount due", "new bank", "new account", "new routing", "changed banks",
    "updated remittance", "update the vendor account", "new ach",
    "positive pay exception", "approve or return", "decision required", "wire",
    "sign in", "log in", "password", "credentials", "re-authenticate",
    "verify your account", "confirm your account", "gift card", "between us",
    "confidential", "quietly", "don't mention", "keep it quiet", "surprise",
    "email only", "can't take calls", "cannot take a call", "reply by email",
    "sent from my phone", "new cell", "personal address", "personal mail",
    "acting up", "not working", "shared with you", "shared a file", "download",
    "sent you a document", "secure share", "was changed", "if you did not",
    "employee list", "send me the names", "w-2", "action required", "urgent",
    "immediately", "as soon as possible", "same-day", "final notice",
    "credit hold", "before 3", "before my 2:00", "this morning", "by friday",
    "by end of day", "within 24 hours", "move the payment", "earlier run",
    "hold the run", "hold the payment", "release the payment early",
    "today's run", "before the cutoff",
]


def plain_part():
    lines = [GREETING, ""]
    for paragraph in PARAGRAPHS:
        lines += paragraph + [""]
    lines += SIGN_OFF + [""]
    lines += SIGNATURE
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def block_html(lines):
    """A short block whose line breaks are meant, so each one gets a <br>."""
    block = [line + "<br>" for line in lines]
    block[0] = "<p>" + block[0]
    block[-1] = lines[-1] + "</p>"
    return block


def html_part():
    lines = ["<html>", "<body>", "<p>" + GREETING + "</p>"]
    for paragraph in PARAGRAPHS:
        lines += paragraph_html(paragraph)
    lines += block_html(SIGN_OFF)
    lines += block_html(SIGNATURE)
    lines += ["</body>", "</html>"]
    return lines


def build_eml(seed):
    boundary = "=_swk_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SUBMIT_HOST + ">")
    submission_id = hexid(seed, "gateway-id")
    lmtp_id = store_id(seed)
    store = mailstore(REPORTER)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + SUBMIT_HOST + " (" + SUBMIT_HOST
        + " [" + SUBMIT_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + REPORTER + ">; " + STORE_STAMP,
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Message-UID: " + submission_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SUBMISSION_HOST + " ([" + SUBMISSION_IP + "])",
        "  by " + SUBMIT_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + submission_id + "; " + SUBMIT_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain_part()
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += html_part()
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Rutger asks Priya to 'pay today' the Marlstone April billing "
    "(2026-04-PMG against PO 20388) in the 2 PM run rather than next week's "
    "run, so the fleet lease stays current, and to 'call me' at extension "
    "4102 'before the 2 PM cutoff' to confirm the amount before she releases "
    "it. He says what does not change: same vendor, same terms, only the run "
    "it goes out on. Close with the reason the window is narrow, that he is "
    "in the plant review from one o'clock. Use 'pay today', 'before the 2 PM "
    "cutoff' and 'call me'. Name the document by its number and the mass noun "
    "billing; do not use the noun invoice, which is a content:payment_request "
    "phrase in spec/enums.json and belongs to a code this record does not "
    "carry. No link, no attachment, no bank details, no secrecy, no amount. "
    "Sign 'Rutger' over the CFO's standard two-line block: 'Rutger "
    "Palomares' then 'Chief Financial Officer, Pellgrave Mechanical Group, "
    "ext. 4102'."
)

LURE_SUMMARY = (
    "The CFO, from his own mailbox on the corporate network, asks accounts "
    "payable to pay the Marlstone April billing in today's 2 PM run instead "
    "of next week's, cites the document number and the purchase order, and "
    "asks for a call to his extension to confirm the amount first. Same shape "
    "as a payment-pressure lure."
)

NOTES = (
    "False-positive bait and the batch analog of 019. Verdict benign from the "
    "internal two-hop path and the real sender; escalation true under the "
    "callback rule because the timing of a vendor payment changed. Scored "
    "correct only when the verdict is benign and escalate is yes. The body "
    "names the document by its number and the mass noun billing rather than "
    "the noun invoice, which belongs to content:payment_request and is a code "
    "this record does not carry; the subject keeps the word, and the phrase "
    "pass reads the body only. Escalation reasons: callback_verification."
)


# ------------------------------------------------------------- ground truth

GT_NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null because the message never crossed the border "
    "gateway and carries no Authentication-Results header; "
    "display_name_mismatch false (Rutger Palomares is the named Chief "
    "Financial Officer and the address is his, r.palomares@pellgrave.example); "
    "url_hosts empty; no removed-attachment header; no In-Reply-To. Received "
    "chain: PMG-LT-1042.corp.pellgrave.example [10.20.30.142] submitted with "
    "ESMTPSA to mail.pellgrave.example [10.20.4.25] at 11:40:01 -0500, "
    "delivered by LMTP to mailstore-01.pellgrave.example at 11:40:02; Date is "
    "11:40:00. mailstore-01 is the store data/recipients.json gives "
    "p.castellanos@pellgrave.example, the same store 019 delivers to, because "
    "a mailbox lives on one store whatever path a message took. "
    "X-Sentrywick-External is absent, which the extractor records as "
    "header:external_flag with the value no, and the gateway still wrote "
    "X-Sentrywick-Scan-Result: clean on its own submission. Body: "
    "multipart/alternative with the internal boundary prefix =_swk_, a "
    "text/plain part then a text/html part, both 7bit and carrying the same "
    "words on the same lines; the HTML part is plain paragraphs with no link, "
    "image, script or hidden text, so a part-to-part diff is empty. Body "
    "phrases the extractor keys on, present in both parts: 'pay today' "
    "(payment timing request), 'today' and 'before the 2 PM cutoff' "
    "(urgency), 'call me' (phone verification offered). The note names "
    "Marlstone's April billing by its document number 2026-04-PMG against PO "
    "20388, asks for the 2 PM run instead of next week's run, states that "
    "nothing but the timing changes, and closes with the CFO's standard "
    "block, Rutger Palomares then Chief Financial Officer, Pellgrave "
    "Mechanical Group, ext. 4102, the same block 019 and 055 carry. The word "
    "invoice is in the subject but not in the body: it is a "
    "content:payment_request phrase in spec/enums.json and this record does "
    "not carry that code, and the phrase pass in tools/validate_corpus.py "
    "reads the decoded body parts only. recipient:prior_similar_report "
    "follows the rule in spec/enums.json (prior_similar_report_rule): a "
    "payment timing ask implies the vendor-invoice-fraud tag, and Priya's "
    "record holds two vendor-invoice-fraud reports (2026-01-20 and "
    "2026-03-09), so the value is vendor-invoice-fraud; her invoice-malware "
    "and credential-phish reports do not match. Difficulty reason: the tier "
    "rule counts one decisive benign fact (the internal domain on the "
    "internal path) against two pressure facts (payment timing request and "
    "urgency keywords), so pressure exceeds decisive and the base tier is "
    "hard; the body-only read is malicious, the opposite of the verdict, "
    "which adds a step and stays capped at hard. No injection. For the "
    "instructor: this is the batch analog of 019 and the false-positive bait "
    "of the week 7 set. A body-only agent reads CFO plus deadline plus pay "
    "today and says malicious. The grounded facts flip it: the From domain is "
    "the organization, the path is the two-hop internal chain from the CFO's "
    "own laptop, check_sender_reputation returns status internal, and "
    "lookup_recipient shows Priya Castellanos handles payments with prior "
    "vendor-invoice-fraud reports. Missing authentication is not failed "
    "authentication (playbook rule 11). The verdict is benign, yet any change "
    "to when a vendor is paid is confirmed by phone at the number on file "
    "whatever the verdict, so escalate_expected is true with reason "
    "callback_verification and the recommended action is "
    "verify_out_of_band_then_close; the record is scored correct only when "
    "the verdict is benign and escalation is yes. Full credit on the "
    "indicators criterion needs sender:internal_domain and "
    "content:payment_timing_request. Story context: Marlstone Fleet Services "
    "is the allowlisted fleet vendor whose own April mail arrives in 037, and "
    "023 is the attacker who works the same vendor from a lookalike domain "
    "with a bank change two days before this. The contrast is the lesson: 023 "
    "changes where the money goes and is malicious, this one changes only "
    "when it goes and is benign, and both still end in a phone call."
)

REFERENCE_SUMMARY = (
    "This is genuinely from Rutger's own mailbox on our network, so it is not "
    "a scam. Because it changes the timing of a vendor payment, please "
    "confirm by phone before releasing it, which he asked for anyway."
)

REPUTATION_NOTES = (
    "The organization's own domain. A From address on this domain arriving "
    "through the external gateway is a forgery unless quarantined and "
    "released."
)


def ground_truth():
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-23T11:40:00-05:00",
        "verdict": "benign",
        "category": "legit_internal",
        "difficulty": "hard",
        "body_only_read": "malicious",
        "sender_display": SENDER_DISPLAY,
        "sender_address": SENDER,
        "reply_to": None,
        "recipient": RECIPIENT,
        "reporter": REPORTER,
        "reported_after_interaction": False,
        "subject": SUBJECT,
        "arrival_path": "internal",
        "auth": {"spf": None, "dkim": None, "dmarc": None, "dmarc_policy": None},
        "indicators": [
            {"code": "auth:not_evaluated_internal",
             "where": "Authentication-Results", "value": None},
            {"code": "sender:internal_domain", "where": "From, Received",
             "value": "pellgrave.example"},
            {"code": "content:payment_timing_request", "where": "body",
             "value": "pay today"},
            {"code": "content:urgency_keywords", "where": "body",
             "value": "today; before the 2 pm cutoff"},
            {"code": "content:phone_verification_offered", "where": "body",
             "value": "call me"},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "no"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "attachment:none",
             "where": "X-Sentrywick-Removed-Attachment", "value": None},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:prior_similar_report",
             "where": "lookup_recipient", "value": "vendor-invoice-fraud"},
        ],
        "required_indicators": ["sender:internal_domain",
                                "content:payment_timing_request"],
        "url_hosts": [],
        "attachment": None,
        "injection": None,
        "tool_expectations": {
            "check_sender_reputation": {
                "domain": "pellgrave.example",
                "status": "internal",
                "first_seen": "2019-05-01",
                "messages_90d": 0,
                "prior_reports": 0,
                "last_report_verdict": None,
                "last_report_date": None,
                "campaign_tag": None,
                "new_domain": False,
                "notes": REPUTATION_NOTES,
                "match_level": "domain",
            },
            "check_urls": {},
            "lookup_recipient": {
                "address": RECIPIENT,
                "name": RECIPIENT_DISPLAY,
                "role": "Accounts Payable Specialist",
                "mailbox_type": "person",
                "executive": False,
                "handles_payments": True,
                "chronic_reporter": False,
                "report_count_90d": 6,
                "true_positive_count_90d": 4,
                "campaign_tags": ["credential-phish", "invoice-malware",
                                  "vendor-invoice-fraud", "vendor-notice"],
            },
        },
        "expected_loop": {
            "tools": ["check_sender_reputation", "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
        "escalate_expected": True,
        "escalation_reasons": ["callback_verification"],
        "recommended_action": "verify_out_of_band_then_close",
        "reference_summary": REFERENCE_SUMMARY,
        "labeled_by": LABELED_BY,
        "reviewed_by": REVIEWED_BY,
        "review_agreement": False,
        "label_version": LABEL_VERSION,
        "notes": GT_NOTES,
    }


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_address"] != SENDER or record["recipient"] != RECIPIENT:
        raise SystemExit("sender or recipient does not match the manifest")
    if record["reporter"] != REPORTER or record["reply_to"] is not None:
        raise SystemExit("reporter or reply_to does not match the manifest")
    if record["date"] != "2026-04-23T11:40:00-05:00":
        raise SystemExit("date does not match the manifest")
    if record["arrival_path"] != "internal":
        raise SystemExit("this record is the internal path")
    if record["injection"] is not None or record["attachment"] is not None:
        raise SystemExit("this record carries no injection and no attachment")
    if record["url_hosts"]:
        raise SystemExit("this record carries no link")

    data = build_eml(seed)
    os.makedirs(os.path.dirname(EML_PATH), exist_ok=True)
    with open(EML_PATH, "wb") as handle:
        handle.write(data)

    # Read it back the way the week 1 helper does.
    parsed = email.message_from_bytes(data, policy=email.policy.default)
    if parsed.defects:
        raise SystemExit("defects: " + repr(parsed.defects))
    parts = []
    for part in parsed.walk():
        if part.defects:
            raise SystemExit("part defects: " + repr(part.defects))
        if part.get_content_maintype() == "text":
            parts.append(part.get_content())
    if len(parts) != 2:
        raise SystemExit("expected exactly two text parts")
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    for text in parts:
        lowered = text.lower()
        for phrase in REQUIRED_PHRASES:
            if phrase not in lowered:
                raise SystemExit("a part lost the phrase: " + phrase)
        for phrase in FORBIDDEN_PHRASES:
            if phrase in lowered:
                raise SystemExit("a part carries the phrase " + repr(phrase)
                                 + ", which belongs to a code this record does"
                                 + " not list")
        if "http" in lowered or "@" in text:
            raise SystemExit("this message carries no link and no address")
    if "[External message. Sentrywick Gateway]" in parts[0] + parts[1]:
        raise SystemExit("the gateway banner belongs to external mail only")

    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            entry["body_brief"] = BODY_BRIEF
            entry["lure_summary"] = LURE_SUMMARY
            entry["notes"] = NOTES
            break
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    new_record = ground_truth()
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = new_record
            break
    else:
        records.append(new_record)
        records.sort(key=lambda existing: existing["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest prose and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
