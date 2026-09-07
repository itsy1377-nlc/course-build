#!/usr/bin/env python3
"""Regenerate 041-peakwright-seo-pitch.

Rebuilds emails/batch/041-peakwright-seo-pitch.eml byte for byte from the corpus
seed, refreshes the matching manifest fields in spec/corpus-spec.json, and
upserts the ground truth record in ground_truth.json. Every semantic field in
the manifest record (verdict, category, indicators, url_hosts,
tool_expectations, expected_loop, escalate_expected, recommended_action) is read
and never written, so the label and the file cannot drift.

Identifiers are derived from the corpus seed the same way the rest of the corpus
derives them, so rerunning this script reproduces the same bytes:

    hex12(label)          = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    stream(label, n)      = sha256("<seed>|<id>|<label>|<n>") for n = 0, 1, 2 ...
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    sender Received id    = hex12("sender-id")[:8]
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh               = base64(stream("dkim-bh", 32))
    DKIM b                = base64(stream("dkim-b", 256))

Neither DKIM value verifies. They are seeded bytes of the right length, the same
convention the rest of the corpus uses, because no .example domain can publish a
key and no lab checks a signature. The DKIM t= value is the Unix time of the
Date header, 1776692400 for Mon, 20 Apr 2026 13:40:00 +0000, so the signature
timestamp and the stamped time are the same instant.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. The To address, the reporter and the
mailbox the file was pulled from are all Lenora Vashti, so there is no list
expansion to unwind: recipients.json gives her mailstore-01 and the LMTP hop
names it.

Why the authentication headers read the way they do. This is the corpus case
where all three checks pass and none of it matters. Peakwright Leads owns
peakwright-leads.example, sends from its own server, publishes SPF (mx -all) and
signs with selector pw1, so spf=pass on its own MAIL FROM domain, dkim=pass with
d=peakwright-leads.example, and DMARC passes on an aligned identity against a
published policy of none. Nothing is forged, because there is nothing to forge:
the sender is exactly who the headers say. What makes the message unwanted is
that nobody asked for it, which no authentication result can express. The
gateway says so in the only place that carries the judgment: scan result
suspect, X-Sentrywick-Spam-Score 7.2, which is the decisive benign fact under
the tier rule (a score at or above 5.0 with no ask in the body).

The message deliberately carries no bulk headers. A cold pitch typed by one
salesperson into an ordinary client is not a mailing: no List-Unsubscribe, no
List-Unsubscribe-Post, no List-Id, no Precedence, no Feedback-ID, and no
tracking token on the one link. That is the contrast with 003, where the same
verdict and the same category arrive through a bulk provider with the full RFC
8058 footer. A student who has learned to read list headers as the mark of spam
has nothing to read here, and has to reach the same verdict from the score and
the absence of an ask.

Headers deliberately absent, matching the manifest indicator list: no Reply-To
(the manifest sets reply_to null), no In-Reply-To and no References
(thread:new), no X-Sentrywick-Removed-Attachment (attachment:none), no
X-Priority and no Importance, no Auto-Submitted, and no X-Originating-IP, which
is reserved for webmail submissions; the salesperson's client address sits in
the bottom Received line instead. X-Mailer names Marrowdale Mail 5.2, the
corpus's ordinary desktop client, because that is what the message is.

Wording rules the body obeys, all from spec/enums.json content_phrases. The
manifest record carries no content code, so no phrase from any content list may
appear in either decoded part; validate_corpus.py checks that both ways and
build_eml checks it again here before writing. The pitch therefore offers a free
15 minute audit rather than anything with a deadline (no content:urgency
phrase), links to a calendar rather than to an account (no
content:credential_request), sells a service rather than billing for one (no
content:payment_request), and describes a screen share rather than a file (no
content:file_share_lure). The one ask in the message is for a meeting, and
"a meeting" is not an ask code, which is what keeps the category spam and the
verdict benign under the spam_rule in spec/categories.json.

Run:  python3 corpus/tools/generators/gen_041_peakwright_seo_pitch.py
"""

import base64
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "041-peakwright-seo-pitch"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "marcus@peakwright-leads.example"
SENDER_DISPLAY = "Marcus at Peakwright"
SENDER_DOMAIN = "peakwright-leads.example"
SENDER_MTA = "mail." + SENDER_DOMAIN
SENDER_MTA_IP = "203.0.113.170"
SENDER_CLIENT = "PW-SALES-0217." + SENDER_DOMAIN
SENDER_CLIENT_IP = "192.0.2.119"
DKIM_SELECTOR = "pw1"
# Unix time of the Date header, Mon, 20 Apr 2026 13:40:00 +0000.
DKIM_TIME = "1776692400"

RECIPIENT = "l.vashti@pellgrave.example"
RECIPIENT_NAME = "Lenora Vashti"
REPORTER = "l.vashti@pellgrave.example"

GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SUBJECT = "Quick question about pellgrave.example's search ranking"
SCAN_RESULT = "suspect"
SPAM_SCORE = "7.2"

# The one link. Its host is the sender's own domain, on neither url list, which
# is why check_urls answers unlisted and playbook rule 7 reads that as unknown
# rather than clean. There is no per-recipient token on it: this is not a
# campaign platform, it is a calendar page.
LINK = "https://peakwright-leads.example/book/marcus"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient, reporter):
    """The mailbox this file was pulled from and the one store that holds it.

    A person or a shared mailbox receives the message itself, so the LMTP hop
    names the recipient. Only a distribution list needs the reporter's own
    mailbox substituted, because a list is delivered by expansion and the copy
    the corpus keeps is the one that landed in a member's store.
    """
    entry = recipient_record(recipient)
    if entry.get("mailbox_type") == "list":
        entry = recipient_record(reporter)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


# ---------------------------------------------------------------- body text
#
# Each paragraph is written once as the plain-part lines, hard wrapped under 72
# characters. The HTML part joins the same lines with single spaces, so the two
# parts cannot drift and the HTML part hides nothing.
#
# The register is one salesperson at a small marketing shop typing to a name off
# a prospect list. He writes the domain, pellgrave.example, rather than the
# company name, because the domain is what the list gave him; that is the tell a
# reader recognizes as cold outreach, and it is the same string the subject
# carries. He names the searches he ran, offers something free and small, and
# closes by inviting a refusal. Nothing in it asks for a sign-in, a payment, a
# file or a name.

GREETING = "Hi Lenora,"

PARA_1 = [
    "I was putting together a short list of mechanical contractors in the",
    "region this week and pellgrave.example came up, so I ran a few of the",
    "searches your buyers would run. Two smaller shops sit above you on",
    "every one of them.",
]

PARA_2 = [
    "The three I tried were industrial chiller repair, boiler service",
    "contract and emergency HVAC service. Neither of the two shops ahead of",
    "you has more pages than you do, which usually means your own service",
    "pages are competing with each other rather than losing on content.",
    "That is the cheap kind of problem to have.",
]

PARA_3 = [
    "I run a free 15 minute audit for a few contractors a month. It is a",
    "screen share, there is no slide deck, and you keep the notes whether or",
    "not you ever work with us. Most of what turns up is title text and",
    "internal linking, which your own web person can fix in an afternoon.",
]

PARA_4 = [
    "Is that worth 15 minutes to you? My calendar is open, so pick",
    "whatever slot suits you",
]

PARA_5 = [
    "If this isn't relevant, just let me know and I'll stop. I would rather",
    "hear that once than keep turning up in your inbox.",
]

CLOSING = "Best,"

# The house block for an external human signer: name, organization, a dialable
# number. 555-0172 is unused elsewhere in the corpus. A salesperson at a small
# shop signs with a direct line and an extension rather than a bare internal
# extension, because an outside recipient has to be able to dial it.
SIGNATURE = [
    "Marcus Oyelaran-Pike",
    "Peakwright Leads",
    "555-0172 ext. 118",
]

PARAGRAPHS = [PARA_1, PARA_2, PARA_3, PARA_4, PARA_5]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += PARA_3 + [""]
    lines += PARA_4[:-1] + [PARA_4[-1] + ":"] + [""]
    lines += [LINK, ""]
    lines += PARA_5 + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE
    return lines


def html_part():
    return [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#ffffff;">',
        BANNER_HTML,
        ('<div style="max-width:620px;margin:18px auto;padding:0 22px;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#1f1f1f;">'),
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        "<p>" + joined(PARA_3) + "</p>",
        "<p>" + joined(PARA_4) + ":</p>",
        '<p><a href="' + LINK + '">',
        LINK + "</a></p>",
        "<p>" + joined(PARA_5) + "</p>",
        "<p>" + CLOSING + "</p>",
        "<p>" + "<br>".join(SIGNATURE) + "</p>",
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: an encoded line may not exceed 76 characters including the
# trailing soft break, and a soft break may not split an =XX escape.

QP_MAXLEN = 76


def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start of
    the next line so no encoded line ends in white space; when no space fits,
    hard-break at 75 characters plus the soft line break, never inside an =XX
    escape.
    """
    out = []
    rest = line
    while len(rest) > QP_MAXLEN:
        cut = rest.rfind(" ", 1, QP_MAXLEN)
        if cut <= 0:
            cut = QP_MAXLEN - 1
            while rest[cut - 2:cut - 1] == "=" or rest[cut - 3:cut - 2] == "=":
                cut -= 1
        out.append(rest[:cut] + "=")
        rest = rest[cut:]
    out.append(rest)
    return out


def qp_body(lines):
    out = []
    for line in lines:
        out.extend(qp_wrap(qp_escape(line)))
    return out


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_swk_" + hex12(seed, "boundary")
    message_id = ("<20260420134000." + hex12(seed, "message-id")
                  + "@" + SENDER_MTA + ">")
    gateway_id = hex12(seed, "gateway-id")
    sender_id = hex12(seed, "sender-id")[:8]
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; Mon, 20 Apr 2026 08:40:09 -0500",
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=none",
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + SENDER + " designates " + SENDER_MTA_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + SENDER_MTA_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + SENDER_MTA + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_MTA,
        "  (" + SENDER_MTA + " [" + SENDER_MTA_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Mon, 20 Apr 2026 08:40:07 -0500",
        "Received: from " + SENDER_CLIENT + " ([" + SENDER_CLIENT_IP + "])",
        "  by " + SENDER_MTA + " with ESMTPSA id " + sender_id + ";",
        "  Mon, 20 Apr 2026 13:40:04 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SENDER_DOMAIN + "; s=" + DKIM_SELECTOR + "; t=" + DKIM_TIME + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: Mon, 20 Apr 2026 08:40:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_NAME + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "X-Mailer: Marrowdale Mail 5.2",
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
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += qp_body(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part())
    html_text = "\n".join(html_part())
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    check_no_content_phrases(plain_text + "\n" + html_text)
    if plain_text.count(LINK) != 1 or html_text.count(LINK) != 2:
        raise SystemExit("the calendar link must appear once in the plain part"
                         " and twice in the HTML part (href and link text)")

    return "\r\n".join(lines).encode("ascii")


def check_no_content_phrases(body):
    """Prove the body carries no phrase from any content list in enums.json.

    The manifest record lists no content code, and validate_corpus.py runs the
    phrase lists against the rendered parts both ways: a phrase in the body with
    no indicator is a failure. Catching it here names the phrase and the list it
    came from instead of leaving the validator to report a code mismatch.

    The two lists validate_corpus.py skips are skipped here for the same
    reasons: content:non_english_body is a proportion judgment over Spanish
    stopwords that sit inside ordinary English words, and
    content:instruction_to_ai holds single words the corpus also puts inside
    quoted examples on benign mail.
    """
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    lowered = body.lower()
    for code, phrases in sorted((enums.get("content_phrases") or {}).items()):
        if code in skip:
            continue
        for phrase in phrases:
            if phrase.lower() in lowered:
                raise SystemExit("the body carries the " + code + " phrase "
                                 + repr(phrase) + " but the record lists no content code")


# ------------------------------------------------------------ manifest text

LURE_SUMMARY = (
    "A cold sales pitch offering a free website audit, with a calendar link on "
    "the sender's own domain. No credential ask, no attachment, no payment "
    "instruction; just unwanted."
)

BODY_BRIEF = (
    "A chatty cold pitch typed by one salesperson, not a mailing. Marcus writes "
    "that he was building a list of mechanical contractors, that "
    "pellgrave.example came up, and that on the three searches he ran "
    "(industrial chiller repair, boiler service contract, emergency HVAC "
    "service) two smaller shops rank above them; he reads that as the "
    "company's own service pages competing with each other rather than a "
    "content problem. He offers a free 15 minute audit, a screen share with no "
    "slide deck whose notes the recipient keeps either way, asks \"Is that "
    "worth 15 minutes to you?\" so the subject line's promised question "
    "actually arrives, and links to "
    "https://peakwright-leads.example/book/marcus to pick a time. Ends with "
    "\"If this isn't relevant, just let me know and I'll stop.\" No sign-in, no "
    "deadline, no attachment, no ask beyond a meeting. Sign with a name "
    "(Marcus Oyelaran-Pike), the company, and a dialable number in the 555-01xx "
    "block."
)

MANIFEST_NOTES = (
    "Cold outreach without bulk headers and with all three checks passing on "
    "the sender's own domain: authentication says nothing about wantedness. "
    "Verdict benign, category spam. Peakwright Leads really owns "
    "peakwright-leads.example, really publishes SPF and DKIM for it, and really "
    "sent the message, so there is nothing in the header block to catch; the "
    "only header that carries a judgment is the gateway's own, scan result "
    "suspect with a spam score of 7.2. That score with no ask in the body is "
    "the decisive benign fact the tier rule counts, which is what makes this "
    "the easy end of the batch set. The contrast is with 003, the same verdict "
    "and the same category arriving through a bulk provider with the full list "
    "header footer: a student who has learned to read List-Unsubscribe as the "
    "mark of spam has nothing to read here."
)

NOTES = (
    "The batch set's cold outreach case, and the corpus example where every "
    "authentication check passes and none of it decides anything. Key facts: "
    "the From domain peakwright-leads.example belongs to Peakwright Leads, a "
    "marketing shop the organization has never dealt with, under the display "
    "name Marcus at Peakwright, which display_names.json records as a name that "
    "domain owns, so there is no display-name mismatch; no Reply-To; "
    "Return-Path marcus@peakwright-leads.example, the sender's own address "
    "rather than a provider bounce address; spf=pass on that same domain by the "
    "mx mechanism of its published record mx -all; dkim=pass with "
    "d=peakwright-leads.example s=pw1; dmarc=pass with policy.dmarc=none, "
    "because both passing identities align with the From domain and the domain "
    "publishes a record whose policy is none; scan result suspect with "
    "X-Sentrywick-Spam-Score 7.2; one link host, peakwright-leads.example, "
    "carrying the single calendar link "
    "https://peakwright-leads.example/book/marcus, which check_urls answers "
    "unlisted; no attachment; a new thread; the recipient is the Director of "
    "Sales, an ordinary mailbox with no executive or payments flag and three "
    "prior reports, one of them a true positive. The message carries no bulk "
    "headers at all: no List-Unsubscribe, no List-Unsubscribe-Post, no List-Id, "
    "no Precedence, no Feedback-ID, and no per-recipient token on the link, "
    "because a pitch typed into a desktop client (X-Mailer: Marrowdale Mail "
    "5.2) is not a mailing. That is the whole difficulty of the file and the "
    "reason it sits in the batch: 003 teaches spam through the bulk provider "
    "and hands the student list headers to read, and this one withholds them "
    "while keeping the verdict identical. Playbook rule 10 decides it: unwanted "
    "marketing that asks for nothing is spam, spam is benign, close it and "
    "block nothing. Playbook rule 1 is the guard on the other side, since three "
    "passes prove only that the mail came from the domain it names, and rule 7 "
    "keeps the unlisted calendar host from being read as clean. Difficulty "
    "easy: the tier rule scores one decisive benign fact, a spam score of 7.2 "
    "at or above the 5.0 threshold with no ask code in the indicator list, and "
    "nothing pushes the other way; there is no injection and the body-only read "
    "already agrees with the verdict, so neither adjustment applies. The body "
    "carries no phrase from any content list in enums.json, which is what "
    "keeps the record free of content codes and what makes the message spam "
    "rather than the malicious category an ask would imply under the spam_rule "
    "in categories.json: the offer is a meeting, and a meeting is not an ask "
    "code. Week 4 use: check_sender_reputation matches "
    "peakwright-leads.example at the domain level with status unknown, first "
    "seen 2026-04-20 and new_domain true, so sender:first_seen is present and "
    "means new rather than bad; check_urls returns unlisted for the calendar "
    "host; lookup_recipient shows an ordinary mailbox. Week 5 use: no tool "
    "answers decisively, so the bounded loop runs check_sender_reputation, "
    "check_urls and lookup_recipient in turn and ends with no tool left to try. "
    "Grading note: a student who escalates this has confused unwanted with "
    "dangerous, a student who calls it malicious because the spam score is high "
    "has read the score backwards (it is the gateway agreeing that the mail is "
    "junk, not that it is an attack), and a student who calls it clean because "
    "all three checks pass has skipped playbook rule 1. Rendering notes: the "
    "plain part is 7bit with hard wraps under 78 characters and the HTML part "
    "is quoted-printable, because the fixed gateway banner snippet is longer "
    "than 78 characters; the banner is the first line of the plain part and the "
    "first line after the body tag in the HTML part; both parts carry the same "
    "words and the HTML part hides nothing, so there is no "
    "content:html_hidden_text, and the link text in the HTML part is the link "
    "itself, so the visible address and the href agree. Every identifier that "
    "looks random is derived from a SHA-256 over the corpus seed, the email id "
    "and a label, so the file regenerates byte for byte."
)

REFERENCE_SUMMARY = (
    "This is a cold sales pitch from a marketing company we have never dealt "
    "with. It is unwanted but harmless, so we closed it as spam and blocked "
    "nothing."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-20T08:40:00-05:00",
    "verdict": "benign",
    "category": "spam",
    "difficulty": "easy",
    "body_only_read": "benign",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=" + SENDER_DOMAIN + "; "
                   "dkim=pass header.d=" + SENDER_DOMAIN
                   + " header.s=" + DKIM_SELECTOR
                   + " header.i=@" + SENDER_DOMAIN + "; "
                   "dmarc=pass header.from=" + SENDER_DOMAIN
                   + " policy.dmarc=none")},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-20"},
        {"code": "url:host_unlisted", "where": "check_urls",
         "value": SENDER_DOMAIN},
        {"code": "header:spam_score", "where": "X-Sentrywick-Spam-Score",
         "value": SPAM_SCORE},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["header:spam_score", "sender:first_seen"],
    "url_hosts": [SENDER_DOMAIN],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "unknown",
            "first_seen": "2026-04-20",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "Cold outreach; first seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {SENDER_DOMAIN: "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_NAME,
            "role": "Director of Sales",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 3,
            "true_positive_count_90d": 1,
            "campaign_tags": ["credential-phish", "marketing"],
        },
    },
    "expected_loop": {
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_spam_reply_to_reporter",
    "reference_summary": REFERENCE_SUMMARY,
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": NOTES,
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
    for field, want in (("subject", SUBJECT), ("sender_address", SENDER),
                        ("sender_display", SENDER_DISPLAY), ("recipient", RECIPIENT),
                        ("reporter", REPORTER), ("verdict", "benign"),
                        ("category", "spam"), ("difficulty", "easy")):
        if record[field] != want:
            raise SystemExit(field + " does not match the manifest: "
                             + repr(record[field]) + " against " + repr(want))
    if record["url_hosts"] != [SENDER_DOMAIN]:
        raise SystemExit("url_hosts does not match the manifest")

    data = build_eml(seed)
    os.makedirs(os.path.dirname(EML_PATH), exist_ok=True)
    with open(EML_PATH, "wb") as handle:
        handle.write(data)

    # Read it back the way the week 1 helper does.
    parsed = email.message_from_bytes(data, policy=email.policy.default)
    if parsed.defects:
        raise SystemExit("defects: " + repr(parsed.defects))
    for part in parsed.walk():
        if part.defects:
            raise SystemExit("part defects: " + repr(part.defects))
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))

    record["lure_summary"] = LURE_SUMMARY
    record["body_brief"] = BODY_BRIEF
    record["notes"] = MANIFEST_NOTES
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    for index, entry in enumerate(records):
        if entry["id"] == EMAIL_ID:
            records[index] = GROUND_TRUTH
            break
    else:
        records.append(GROUND_TRUTH)
        records.sort(key=lambda entry: entry["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
