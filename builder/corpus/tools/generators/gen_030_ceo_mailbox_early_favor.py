#!/usr/bin/env python3
"""Regenerate 030-ceo-mailbox-early-favor.

Rebuilds emails/batch/030-ceo-mailbox-early-favor.eml from the corpus seed,
refreshes the prose fields of its own record in spec/corpus-spec.json, and
upserts its ground truth record in ground_truth.json. It touches no other
record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    submission Received id = hexid("gateway-id", 12), also
                            X-Sentrywick-Message-UID
    webmail Received id   = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=sha256("<seed>|<id>|store-id")[:32],
                            version=4)

Nothing here calls time, random or uuid4 without a seeded hex, so the file is
byte reproducible. The delivering mail store is read from data/recipients.json
rather than typed here, because a mailbox lives on exactly one store and the
LMTP hop is a property of the mailbox, never of the path the message took.

Why the header block looks the way it does.

This message really was sent from a.whitcombe@pellgrave.example. It is the
organization's own mailbox on the organization's own path, so the file carries
no Authentication-Results, no Received-SPF and no DKIM-Signature, and no
X-Sentrywick-External header: the gateway does not authenticate its own
submissions (docs/email-header-realism.md sec. 8). Missing authentication is
not failed authentication, which is playbook rule 11, and an agent that reads
the three nulls as failures gets this one right for the wrong reason.

The tell is the Received chain, three hops instead of the two an internal
message normally has:

    [203.0.113.201]                -> webaccess.pellgrave.example  (ESMTPSA)
    webaccess.pellgrave.example    -> mail.pellgrave.example       (ESMTPS)
    mail.pellgrave.example         -> mailstore-01.pellgrave.example (LMTP)

The bottom hop is the company's public webmail front end accepting an
authenticated submission from a client address in 203.0.113.0/24, an RFC 5737
documentation block that is not the corporate network, and X-Originating-IP
records the same address. An employee on the corporate network submits from
10.20.30.0/24 or 10.20.31.0/24 through mail.pellgrave.example, which is the
shape 011, 019 and 055 carry. Somebody outside the network signed in to this
mailbox and sent mail as its owner, which is what
header:webmail_submission_external_ip names and what makes
internal_account_compromise an escalation reason.

There is no DKIM-Signature to derive and therefore no DKIM_B constant: an
internal message never carries one, so the seed derivations above are the whole
list.

webaccess.pellgrave.example is written without a product comment in its
Received line. data/known_good_domains.json lists the host, but no document in
the corpus names a webmail product for it, and inventing a third Sentrywick
product string for one file would put a proper noun into the corpus that
nothing else can be checked against. The two product strings the corpus does
own, Sentrywick Gateway 7.4 and Sentrywick Store 4.2, stay on the hosts that
own them.

The Message-ID right side is webaccess.pellgrave.example, the originating host
at the bottom of the chain, which is the convention in
docs/email-header-realism.md sec. 1 and the same reasoning 021 uses for putting
its Message-ID on the webmail front end that composed it.

Both parts are 7bit. The message is pure ASCII, every source line is under 78
characters, and there is no gateway banner to carry (the banner belongs to
external mail only), so quoted-printable would buy nothing and would only put
soft line breaks through phrases an extractor has to find whole.

Body wording. The three content codes the record lists are matched from the
phrase lists in spec/enums.json, and validate_corpus.py runs those lists over
the decoded parts in both directions, so the wording has to carry exactly the
phrases the record claims and no others:

    content:gift_card_request   "gift cards", whole on one line in both parts.
    content:urgency_keywords    "this morning", likewise. The message carries
                                no other phrase from that list: no "today", no
                                "as soon as possible", no "urgent".
    content:secrecy_request     "don't mention", likewise. Not "quietly" and
                                not "between us", which are 009 and 029.

The body also stays clear of every list it does not claim: no "invoice" or
"net 15" (content:payment_request), no "wire" (content:banking_instruction),
no "call me" (content:phone_verification_offered), no "email only", "can't
take calls" or "sent from my phone" (content:channel_restriction), no
"personal address" or "acting up" (content:excuse_for_external_address), and
no "credentials" or "sign in" (content:credential_request). The word for what
comes back in the reply is "codes", not "credentials", for that reason.

No party in the body resolves to anything a week 4 tool can look up. The
client is named only as "the client team we are hosting": giving it a real
customer name would hand the loop a fourth fact, and the nearest real customer,
Rookmere Medical Plaza, carries status known_good in
data/sender_reputation.json, a benign signal this answer key does not hold.
Rutger is named because the secrecy line has to name the person the secret is
being kept from, and he is an employee rather than a lookup target.

The signature is the house block for internal mail, name then role,
organization and extension, the same two-line shape 011 and 019 use for the
Accounts Payable Specialist and the Chief Financial Officer. Extension 4101 is
the CEO's; no other file in the corpus claims it, and no other record needs
her block, because 009 and 029 are the impostor's webmail messages and sign
"A." and "Adaeze" with no block at all. That the block is genuine is the point
of this email: an attacker sending from inside the mailbox inherits the
signature the owner set, so the signature proves nothing.

Run:  python3 corpus/tools/generators/gen_030_ceo_mailbox_early_favor.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "030-ceo-mailbox-early-favor"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

CRLF = "\r\n"

SENDER_DISPLAY = "Adaeze Whitcombe"
SENDER = "a.whitcombe@pellgrave.example"
RECIPIENT_DISPLAY = "Beatrix Onwuka"
RECIPIENT = "b.onwuka@pellgrave.example"
REPORTER = RECIPIENT
SUBJECT = "Need a favor before my 9:00"

# The hosts on the path. webaccess is the public webmail front end, mail is the
# internal submission host, and neither is mx.pellgrave.example: no hop is by
# the border gateway, which is what makes this an internal message.
WEBMAIL_HOST = "webaccess.pellgrave.example"
WEBMAIL_IP = "10.20.4.40"
SUBMIT_HOST = "mail.pellgrave.example"
SUBMIT_IP = "10.20.4.25"

# The client the message was composed from. 203.0.113.0/24 is RFC 5737
# TEST-NET-3, so it routes nowhere; what matters for the lesson is only that it
# is outside 10.20.0.0/16, the corporate network every other internal message
# in the corpus submits from.
CLIENT_IP = "203.0.113.201"

SCAN_RESULT = "clean"


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
# Each paragraph is one list of lines. Both parts are built from the same
# lists, so the plain and the HTML text cannot drift and a part-to-part diff of
# the decoded words is empty apart from the tags. The line breaks are placed so
# that no phrase an extractor looks for is split: "gift cards", "this morning"
# and "don't mention" each sit whole on one line in both parts.

GREETING = "Beatrix,"

# The excuse for the hour, which is also the thing that makes the message land:
# the CEO really is at a conference this week, so an early message from her is
# not strange. 009 established the trip and 029 traded on it from outside; this
# one trades on it from inside her own mailbox.
PARA_1 = [
    "Sorry for the early one. I am up ahead of the keynote and there is",
    "something I need you to pick up before the day gets away from me.",
]

# The ask. Six cards, a price, a reason, and the return channel. The reply is
# what the attacker is actually after: the codes come back into a mailbox he
# already reads, so nothing has to be posted anywhere and there is no link for
# check_urls to weigh.
PARA_2 = [
    "Can you get six gift cards this morning, $250 each? They are for",
    "the client team we are hosting, and I would rather hand them over",
    "at the lunch than promise them. When you have them, scratch the",
    "backs and send me the codes in a reply so I have them on my phone",
    "before I go on at 9.",
]

# The secrecy line, which is the sentence that keeps the one person who would
# stop this from hearing about it. Naming the CFO and the budget gives the
# request a reason to be quiet that sounds like ordinary executive housekeeping.
PARA_3 = [
    "Don't mention it to Rutger yet, it's coming out of my budget and I",
    "will square it with him when I am back in the office.",
]

PARA_4 = ["Thank you for doing this on short notice."]

SIGN_OFF = "Adaeze"

# The mailbox owner's real block, inherited by whoever is sending from her
# account. The extension is the way this case actually closes: Beatrix calls
# 4101 and the CEO says she sent nothing.
SIGNATURE = [
    "Adaeze Whitcombe",
    "Chief Executive Officer, Pellgrave Mechanical Group, ext. 4101",
]

PARAGRAPHS = [PARA_1, PARA_2, PARA_3, PARA_4]

# Phrases the record claims and the deterministic extractor keys on. main()
# refuses to write the file if any of them is missing from either decoded part.
REQUIRED_PHRASES = ["gift cards", "this morning", "don't mention"]

# Phrases from the other lists in spec/enums.json that this body must not
# carry, because validate_corpus.py runs every list over the decoded parts and
# a hit with no indicator is a failure. The list is the near misses, not the
# whole vocabulary: the wording was written around these.
FORBIDDEN_PHRASES = [
    "today", "urgent", "immediately", "as soon as possible", "same-day",
    "invoice", "net 15", "wire", "new account", "pay today", "call me",
    "email only", "can't take calls", "sent from my phone", "personal address",
    "acting up", "not working", "credentials", "sign in", "password",
    "download", "quietly", "between us", "confidential", "surprise",
    "was changed", "send me the names",
]


def plain_part():
    lines = [GREETING, ""]
    for paragraph in PARAGRAPHS:
        lines += paragraph + [""]
    lines += [SIGN_OFF, ""]
    lines += SIGNATURE
    return lines


def paragraph_html(lines):
    """One paragraph, with the plain part's line breaks kept."""
    if len(lines) == 1:
        return ["<p>" + lines[0] + "</p>"]
    return ["<p>" + lines[0]] + lines[1:-1] + [lines[-1] + "</p>"]


def html_part():
    lines = ["<html>", "<body>", "<p>" + GREETING + "</p>"]
    for paragraph in PARAGRAPHS:
        lines += paragraph_html(paragraph)
    lines += ["<p>" + SIGN_OFF + "</p>"]
    lines += ["<p>" + SIGNATURE[0] + "<br>", SIGNATURE[1] + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    # 05:40:00 -0500 is 10:40:00 UTC, and the Message-ID stamp is UTC.
    message_id = ("<20260423104000." + hexid(seed, "message-id")
                  + "@" + WEBMAIL_HOST + ">")
    submit_id = hexid(seed, "gateway-id")
    webmail_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from " + SUBMIT_HOST + " (" + SUBMIT_HOST + " [" + SUBMIT_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Thu, 23 Apr 2026 05:40:07 -0500",
        # The submission host still scans its own traffic and still stamps the
        # message UID and the reporter, exactly as it does on 011 and 019. What
        # it does not write is Authentication-Results, Received-SPF or
        # X-Sentrywick-External, because it is not authenticating a stranger.
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Message-UID: " + submit_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + WEBMAIL_HOST,
        "  (" + WEBMAIL_HOST + " [" + WEBMAIL_IP + "])",
        "  by " + SUBMIT_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  id " + submit_id + "; Thu, 23 Apr 2026 05:40:05 -0500",
        # The hop that decides the case. The webmail front end took an
        # authenticated submission from a client that is not on the corporate
        # network, and the client address is repeated in X-Originating-IP
        # below.
        "Received: from [" + CLIENT_IP + "]",
        "  by " + WEBMAIL_HOST + " with ESMTPSA id " + webmail_id + ";",
        "  Thu, 23 Apr 2026 05:40:02 -0500",
        "Date: Thu, 23 Apr 2026 05:40:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "X-Originating-IP: [" + CLIENT_IP + "]",
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
    return CRLF.join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "In the CEO's real voice and over her real signature block: she is up "
    "before the conference keynote and needs Beatrix to pick up six gift "
    "cards 'this morning' at $250 each for the client team the company is "
    "hosting, scratch the backs and send the codes back in a reply so she has "
    "them before she goes on at 9 and can hand them over at the lunch. She closes "
    "the ask with 'Don't mention it to Rutger yet, it's coming out of my "
    "budget'. Use 'gift cards', 'this morning' and 'don't mention'. Name no "
    "customer and no vendor: the client is 'the client team we are hosting', "
    "so the body hands the week 5 loop nothing further to look up and the "
    "two-call path stands. No link, no attachment, no amount owed and no bank "
    "detail. Sign 'Adaeze' over the two-line block 'Adaeze Whitcombe' then "
    "'Chief Executive Officer, Pellgrave Mechanical Group, ext. 4101'."
)

LURE_SUMMARY = (
    "From the CEO's real mailbox, submitted through the company's webmail "
    "host from an outside address at 5:40 AM, asking her assistant to buy six "
    "gift cards for a client and send the codes back in a reply. The "
    "signature is the CEO's own block, and nothing in the wording is off."
)

NOTES = (
    "The hardest realistic false negative: internal path, real address, real "
    "signature, no Authentication-Results. The deterministic tell is the "
    "bottom Received hop (webaccess.pellgrave.example accepting an "
    "authenticated submission from 203.0.113.201, a documentation-block "
    "address off the corporate network) plus the matching X-Originating-IP, "
    "and the gift-card ask under playbook rule 6. Missing authentication is "
    "not failed authentication (rule 11), so the three nulls decide nothing. "
    "The CEO is traveling, which makes webmail plausible and is exactly why "
    "this is hard. Escalation reasons: financial_or_endpoint_impact, "
    "executive_target, internal_account_compromise."
)


# ------------------------------------------------------------- ground truth

GT_NOTES = (
    "The batch set's account-takeover case, and the hardest false negative in "
    "the corpus: every sender fact an agent normally leans on is genuine. Key "
    "facts a correct extractor produces: from_domain pellgrave.example, the "
    "organization itself; the address a.whitcombe@pellgrave.example really is "
    "the Chief Executive Officer's, so display_name_mismatch is false and "
    "sender:display_name_matches_employee does not apply; no Reply-To; spf, "
    "dkim, dmarc and dmarc_policy all null, because the message never crossed "
    "the border gateway and carries no Authentication-Results header; "
    "X-Sentrywick-External is absent, which the extractor records as "
    "header:external_flag with the value no, and the submission host still "
    "wrote X-Sentrywick-Scan-Result: clean on its own traffic; url_hosts "
    "empty; no removed-attachment header; no In-Reply-To. Received chain, "
    "three hops rather than the two an internal message normally has: the "
    "client [203.0.113.201] submitted with ESMTPSA to "
    "webaccess.pellgrave.example at 05:40:02 -0500, webaccess handed the "
    "message to mail.pellgrave.example [10.20.4.25] at 05:40:05, and "
    "mailstore-01.pellgrave.example took it by LMTP at 05:40:07; Date is "
    "05:40:00. mailstore-01 is the store data/recipients.json gives "
    "b.onwuka@pellgrave.example, the same store 007, 009 and 029 deliver to, "
    "because a mailbox lives on one store whatever path a message took. "
    "X-Originating-IP repeats the client address. That address is the whole "
    "case: 203.0.113.0/24 is a documentation block and not the corporate "
    "network, while every other internal message in the corpus submits from "
    "10.20.30.0/24 or 10.20.31.0/24 through mail.pellgrave.example. Somebody "
    "outside signed in to the CEO's mailbox and sent as her, which is what "
    "header:webmail_submission_external_ip names. Body: multipart/alternative "
    "with a text/plain part then a text/html part, both 7bit and carrying the "
    "same words, so a part-to-part diff is empty; the HTML part is plain "
    "paragraphs with no link, image, script or hidden text. Body phrases the "
    "extractor keys on, present whole on one line in both parts: 'gift cards' "
    "(gift card request), 'this morning' (urgency) and 'don't mention' "
    "(secrecy). The wording carries no other phrase from any list in "
    "spec/enums.json, so no payment, credential, data or channel code "
    "belongs here. The message names no customer and no vendor: the client is "
    "'the client team we are hosting', a phrase with no domain, no address "
    "and no reputation record behind it, so the body hands the loop nothing "
    "further to look up. The signature is the CEO's own two-line block, "
    "Adaeze Whitcombe then Chief Executive Officer, Pellgrave Mechanical "
    "Group, ext. 4101, the same house shape 011 and 019 carry; an attacker "
    "inside the mailbox inherits it, so the signature proves nothing, and "
    "extension 4101 is how the case actually closes. Difficulty reason: the "
    "tier rule counts one decisive fact (the webmail submission from an "
    "external address) against two pressure facts (the From domain is the "
    "organization on the internal path, and there is neither a link nor an "
    "attachment, so check_urls has nothing to check), so pressure exceeds "
    "decisive and the base tier is hard; there is no injection, and the "
    "body-only read is uncertain rather than benign, so no adjustment "
    "applies. Playbook rules that decide the case: rule 6, executives do not "
    "ask for gift cards, wire transfers or secrecy by email, and this message "
    "asks for two of the three; rule 11, internal mail carries no "
    "authentication results and a missing check is not a failed check, which "
    "is the rule that stops an agent from reaching the right verdict for the "
    "wrong reason. For the instructor: this is the file where a header-only "
    "reader and a body-only reader both fail. The headers say internal, the "
    "address is genuine and reputation returns status internal, so an agent "
    "that stops at the sender says benign; the body is a plausible note from "
    "a traveling executive, so a reader without the Received chain is left "
    "uncertain. The two facts that settle it are the submission hop with "
    "X-Originating-IP and the gift-card ask, and a student who names both has "
    "the whole answer. Tools: check_sender_reputation matches at domain level "
    "and returns status internal, which is a fact about the domain and not a "
    "clearance for the message; lookup_recipient shows Beatrix Onwuka is the "
    "executive assistant to the CEO, carrying the executive flag, with four "
    "reports and three true positives in 90 days and three of those tagged "
    "ceo-impersonation; check_urls has nothing to look up, so the loop stops "
    "on tools_exhausted after two calls. That is why the stop reason is not "
    "internal_sender: an internal result closes 011, where nothing is being "
    "asked for, and closes nothing here. recipient:prior_similar_report "
    "follows the prior_similar_report_rule: content:gift_card_request implies "
    "ceo-impersonation and cfo-impersonation, the sender record carries no "
    "campaign tag of its own, and the mailbox holds three ceo-impersonation "
    "reports, so the value is ceo-impersonation; her marketing report does "
    "not match. Expected action: escalate_incident with reasons "
    "financial_or_endpoint_impact (a malicious BEC always escalates), "
    "executive_target (the recipient carries the executive flag) and "
    "internal_account_compromise (the webmail submission from outside). "
    "Beatrix reported the message before buying anything, so user_interacted "
    "does not apply. The correct close is to buy nothing, reach the CEO on "
    "extension 4101 rather than by replying, lock the mailbox and pull the "
    "webmail sign-in history for 203.0.113.201. Story context: 009 is the "
    "impostor's pretext from a webmail lookalike address on 20 April and 029 "
    "is its gift-card follow-through on 22 April, both to this same mailbox "
    "and both reported; this message arrives the morning after, from inside "
    "the real account, which is how the campaign escalates when a lookalike "
    "address stops working."
)


def ground_truth():
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-23T05:40:00-05:00",
        "verdict": "malicious",
        "category": "bec",
        "difficulty": "hard",
        "body_only_read": "uncertain",
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
            {"code": "header:webmail_submission_external_ip",
             "where": "Received, X-Originating-IP",
             "value": "from [" + CLIENT_IP + "] by " + WEBMAIL_HOST
                      + " with ESMTPSA"},
            {"code": "header:x_originating_ip", "where": "X-Originating-IP",
             "value": "[" + CLIENT_IP + "]"},
            {"code": "header:off_hours_timestamp", "where": "Date",
             "value": "Thu, 23 Apr 2026 05:40:00 -0500"},
            {"code": "content:gift_card_request", "where": "body",
             "value": "gift cards"},
            {"code": "content:secrecy_request", "where": "body",
             "value": "don't mention"},
            {"code": "content:urgency_keywords", "where": "body",
             "value": "this morning"},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "no"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "attachment:none",
             "where": "X-Sentrywick-Removed-Attachment", "value": None},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:executive", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:prior_similar_report",
             "where": "lookup_recipient", "value": "ceo-impersonation"},
        ],
        "required_indicators": [
            "header:webmail_submission_external_ip",
            "content:gift_card_request",
            "recipient:executive",
        ],
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
                "notes": ("The organization's own domain. A From address on "
                          "this domain arriving through the external gateway "
                          "is a forgery unless quarantined and released."),
                "match_level": "domain",
            },
            "check_urls": {},
            "lookup_recipient": {
                "address": RECIPIENT,
                "name": "Beatrix Onwuka",
                "role": "Executive Assistant to the CEO",
                "mailbox_type": "person",
                "executive": True,
                "handles_payments": False,
                "chronic_reporter": False,
                "report_count_90d": 4,
                "true_positive_count_90d": 3,
                "campaign_tags": ["ceo-impersonation", "marketing"],
            },
        },
        "expected_loop": {
            "tools": ["check_sender_reputation", "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
        "escalate_expected": True,
        "escalation_reasons": [
            "financial_or_endpoint_impact",
            "executive_target",
            "internal_account_compromise",
        ],
        "recommended_action": "escalate_incident",
        "reference_summary": (
            "This came from Adaeze's real account, but it was sent through "
            "our webmail from an outside network at 5:40 AM and asks for gift "
            "cards, which she never does by email. We believe her account has "
            "been broken into; do not buy anything, and we are locking the "
            "account now."
        ),
        "labeled_by": LABELED_BY,
        "reviewed_by": REVIEWED_BY,
        "review_agreement": False,
        "label_version": LABEL_VERSION,
        "notes": GT_NOTES,
    }


# ------------------------------------------------------------------- checks

def check_client_is_off_network():
    """The submitting client must not be on the corporate network.

    The whole record turns on this one address. A later edit that moved it
    into 10.20.0.0/16 would leave every label in place and quietly delete the
    only decisive fact, so the check runs on every render.
    """
    if CLIENT_IP.startswith("10.") or CLIENT_IP.startswith("192.168.") \
            or CLIENT_IP.startswith("172.16."):
        raise SystemExit("the submitting client must be off the corporate "
                         "network: " + CLIENT_IP)
    if not CLIENT_IP.startswith("203.0.113."):
        raise SystemExit("the client address must sit in an RFC 5737 "
                         "documentation block: " + CLIENT_IP)


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
    if record["injection"] is not None or record["attachment"] is not None:
        raise SystemExit("this record carries no injection and no attachment")

    check_client_is_off_network()

    data = build_eml(seed)
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
