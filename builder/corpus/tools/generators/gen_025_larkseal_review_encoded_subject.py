#!/usr/bin/env python3
"""Regenerate 025-larkseal-review-encoded-subject.

Rebuilds emails/teaching/025-larkseal-review-encoded-subject.eml byte for byte
from the corpus seed, refreshes the prose fields of the matching manifest record
in spec/corpus-spec.json, and upserts the ground truth record in
ground_truth.json. It touches no other record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the corpus
derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n)       = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    share reference       = hexid("reference", 16)

No DKIM value appears: larkseal-review.example publishes no selector in
data/domain_policy.json, the gateway wrote dkim=none, and section 10 item 14
fails a file that carries a signature while Authentication-Results says none.

The delivering mail store is read from data/recipients.json rather than written
here, because a mailbox lives on exactly one store and the LMTP hop is a
property of the mailbox and not of the path the message arrived on. Lenora
Vashti is a person, so the To address, the reporter and the mailbox the file was
pulled from are the same address and there is no list expansion to unwind.

Why the authentication headers read the way they do. larkseal-review.example is
attacker owned and publishes an SPF record ending ~all, so mail sent from the
cheap relay at 198.51.100.144, which the record does not cover, earns
spf=softfail rather than a fail. The domain publishes no DKIM selector, so
dkim=none. Neither identity authenticates, so DMARC cannot align and the result
is dmarc=fail; the domain does publish a DMARC record with policy none, so the
clause carries policy.dmarc=none and the gateway delivers the message instead of
quarantining it. That combination, a soft failure and a failed DMARC on a
policy-none record, is exactly what lets a hard email land in an ordinary inbox.

The Subject. The manifest asks for an RFC 2047 encoded-word Subject whose
decoded text is

    Lenora, a document “Q2 rate sheet” was shared with you

and the manifest wrote that as one encoded word of 84 characters. RFC 2047
sec. 2 caps an encoded word at 75 characters including the charset, the
encoding and the delimiters, and docs/email-header-realism.md section 2 repeats
that cap, so the one-word form cannot ship. The text is therefore rendered as
two adjacent encoded words, 64 and 32 characters, folded onto two lines the way
RFC 2047 sec. 5 and RFC 5322 sec. 2.2.3 prescribe. Linear white space between
two adjacent encoded words is dropped on decoding, so the space before "was" is
carried inside the second word as its leading underscore, and the header decodes
to the manifest's text character for character. See MANIFEST_SUBJECT_NOTE below
for the second half of this: the manifest's own subject field held the raw
encoded word, while tools/validate_corpus.py compares that field with the
decoded Subject a parser reads, so the field is rewritten here to the decoded
text and the raw rendering is recorded in the notes instead.

Body register: this is transactional mail from a signing platform, not a note
from a person, so it carries a brand line, a detail block and a footer rather
than a signature and an extension. The share reference is the opaque identifier
such a platform issues, derived from the seed. Nothing in the prose pushes: no
deadline, no threat, no misspelling. Every fact that turns this message is a
header fact or a tool result, which is what makes it the hard half of the week 3
pair with 005.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
no In-Reply-To and no References (thread:new), no X-Sentrywick-Removed-Attachment
(attachment:none), no X-Priority and no Importance, no X-Originating-IP, no
Auto-Submitted, and no List-Unsubscribe. The unsubscribe link lives in the body
alone, which is the point of the third link host: a transactional share notice
that carries a marketing relay's unsubscribe link and none of the RFC 8058 list
headers is odd, and the oddity is in the body where a student has to find it.

Run:  python3 corpus/tools/generators/gen_025_larkseal_review_encoded_subject.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "025-larkseal-review-encoded-subject"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

# ------------------------------------------------------------------ parties

SENDER = "notify@larkseal-review.example"
SENDER_DISPLAY = "Larkseal"
FROM_DOMAIN = "larkseal-review.example"
IMITATED_DOMAIN = "larkseal.example"
RECIPIENT = "l.vashti@pellgrave.example"
RECIPIENT_NAME = "Lenora Vashti"
FIRST_NAME = "Lenora"
REPORTER = "l.vashti@pellgrave.example"

GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The sending path from the manifest's received_path_hint. The attacker's own
# notification node submits to a cheap third-party relay, and the relay's
# address is the one the gateway sees, which is why SPF softfails: the ~all
# record on larkseal-review.example covers its own mx and not this relay.
RELAY_HOST = "mta-7.cheapsend-relay.example"
RELAY_IP = "198.51.100.144"
SENDER_NODE = "notify-04." + FROM_DOMAIN
SENDER_NODE_IP = "192.0.2.174"

# Timestamps. The manifest fixes the Date at 2026-04-15T08:47:00-05:00, which is
# 13:47:00 UTC; the sender side stamps in UTC and the gateway and the store in
# local time, so the chain reads 13:47:02Z, 08:47:05 and 08:47:07 from the
# bottom up and never increases from the top down.
DATE_LOCAL = "Wed, 15 Apr 2026 08:47:00 -0500"
STAMP_SENDER = "Wed, 15 Apr 2026 13:47:02 +0000"
STAMP_GATEWAY = "Wed, 15 Apr 2026 08:47:05 -0500"
STAMP_STORE = "Wed, 15 Apr 2026 08:47:07 -0500"
MESSAGE_ID_STAMP = "20260415134700"

SCAN_RESULT = "suspect"
SPAM_SCORE = "5.1"

# ------------------------------------------------------------------ subject
#
# RFC 2047 sec. 2 caps one encoded word at 75 characters. The manifest wrote the
# whole Subject as a single 84 character word, so it is split here into two
# adjacent words of 64 and 32 characters. The leading underscore of the second
# word is the space before "was": white space between adjacent encoded words is
# ignored on decoding, so the separator has to sit inside a word.
SUBJECT_WORD_1 = "=?UTF-8?Q?Lenora=2C_a_document_=E2=80=9CQ2_rate_sheet=E2=80=9D?="
SUBJECT_WORD_2 = "=?UTF-8?Q?_was_shared_with_you?="
SUBJECT_RAW = SUBJECT_WORD_1 + " " + SUBJECT_WORD_2
SUBJECT_DECODED = "Lenora, a document “Q2 rate sheet” was shared with you"

# What the manifest's subject field held when this generator was written: the
# whole line as one 84 character encoded word, over the RFC 2047 cap.
SUBJECT_AUTHORED = ("=?UTF-8?Q?Lenora=2C_a_document_=E2=80=9CQ2_rate_sheet=E2=80=9D"
                    "_was_shared_with_you?=")

# The manifest shipped the raw encoded word in its subject field. Every other
# record holds text a reader sees, and tools/validate_corpus.py compares the
# record's subject field with the decoded Subject that
# email.message_from_bytes returns, so the raw form fails record.subject on
# this file and the ground truth cannot satisfy both that check and the
# gt.manifest check that the two subjects agree. The field is rewritten to the
# decoded text, which is what the validator, the week 1 helper and a student
# reading a mailbox all see; the exact bytes on the wire are recorded in the
# manifest notes and in the ground truth notes and indicator value, so nothing
# about the encoded-word rendering is lost.
MANIFEST_SUBJECT_NOTE = (
    "note: the manifest subject field held the raw encoded word; it now holds the "
    "decoded text, and the raw rendering is recorded in the notes and in the "
    "header:encoded_word_subject indicator value")

# ---------------------------------------------------------------------- urls
#
# The three link hosts and their exact paths come from the manifest record. The
# unsubscribe id 7731 is a design constant pinned in body_brief, a number a
# relay assigns to a list, so it is read from the design and not derived.
OPEN_URL = "https://review.larkseal-review.example/d/q2-rate-sheet"
HELP_URL = "https://help.larkseal.example/articles/shared-documents"
UNSUB_URL = "https://unsub.mailer-relay-links.example/u/7731"
URL_HOSTS = ["review.larkseal-review.example", "help.larkseal.example",
             "unsub.mailer-relay-links.example"]

# ---------------------------------------------------------------- body text
#
# Wording rules, all from the content_phrases lists in spec/enums.json. The
# record carries content:file_share_lure and content:credential_request and no
# other content code, so exactly those two lists may match and every other list
# must not; validate_corpus.py checks both directions on the decoded parts.
#
#   "shared with you" carries content:file_share_lure and "sign in" carries
#   content:credential_request, and both sit in the body rather than only in
#   the Subject, because the codes are recorded with where=body.
#   Nothing from content:urgency_keywords appears: the notice names no
#   deadline, so there is no "today", no "expires in", no "action required".
#   Nothing from content:account_change_notice appears, which is why the
#   footer explains why the notice arrived rather than saying "if you did not".
#   No "invoice", "remit" or "amount due" (content:payment_request): a rate
#   sheet is a document to read, not a bill.
#   No "call me" or "call the number on file"
#   (content:phone_verification_offered) and no "confidential"
#   (content:secrecy_request): a routine share notice offers neither.
DOCUMENT_TITLE = "Q2 rate sheet"
BRAND = "Larkseal"
SALUTATION = "Hello " + FIRST_NAME + ","
OPENING = "A document was shared with you: " + DOCUMENT_TITLE + "."
SHARED_ON = "Shared: Wednesday 15 April 2026"
OPEN_TEXT = "Open document"
SIGN_IN_LINES = [
    "You will be asked to sign in with your work email address before the",
    "document opens. The share stays in your Larkseal account, so you can",
    "come back to it whenever it suits you.",
]
SIGN_IN_PARAGRAPH = " ".join(SIGN_IN_LINES)
HELP_TEXT = "Help"
FOOTER_TAGLINE = "Larkseal, secure signatures"
NOTICE_LINES = [
    "This notice went to " + RECIPIENT + " because a document was",
    "shared with that address.",
]
NOTICE_PARAGRAPH = " ".join(NOTICE_LINES)
UNSUB_TEXT = "Unsubscribe"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;'
               'color:#5a4a00;">[External message. Sentrywick Gateway]</p>')

# The plain part is seven-bit and every line folds under 78 characters, so it
# ships as 7bit. The HTML part carries the gateway banner snippet, which is one
# unbreakable 129 character line, so that part is quoted-printable and the soft
# breaks decode away.
PLAIN_MAX = 78


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient, reporter):
    """The mailbox this copy was delivered to and the one store that holds it."""
    entry = recipient_record(recipient)
    if entry.get("mailbox_type") == "list":
        entry = recipient_record(reporter)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


def plain_part(reference):
    return [
        BANNER_PLAIN,
        "",
        BRAND,
        "",
        SALUTATION,
        "",
        OPENING,
        "",
        "Document: " + DOCUMENT_TITLE,
        "Reference: " + reference,
        SHARED_ON,
        "",
        OPEN_TEXT + ":",
        OPEN_URL,
        "",
    ] + SIGN_IN_LINES + [
        "",
        HELP_TEXT + ":",
        HELP_URL,
        "",
        FOOTER_TAGLINE,
        "",
    ] + NOTICE_LINES + [
        "",
        UNSUB_TEXT + ":",
        UNSUB_URL,
    ]


def html_part(reference):
    """The HTML source lines, before quoted-printable encoding.

    No comment and no hidden element: the record does not carry
    content:html_hidden_text, and validate_corpus.py fails a file that hides
    text the record does not declare.
    """
    return [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;font-family:sans-serif;'
         'font-size:15px;line-height:1.5;color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        ('<p style="margin:0 0 20px 0;font-size:20px;font-weight:bold;color:#1b4f8a;">'
         + BRAND + "</p>"),
        "<p>" + SALUTATION + "</p>",
        "<p>" + OPENING + "</p>",
        ('<p style="margin:0 0 16px 0;">Document: ' + DOCUMENT_TITLE
         + "<br>Reference: " + reference + "<br>" + SHARED_ON + "</p>"),
        ('<p style="margin:24px 0;"><a href="' + OPEN_URL + '" '
         'style="display:inline-block;padding:12px 22px;background-color:#1b4f8a;'
         'color:#ffffff;text-decoration:none;font-weight:bold;border-radius:4px;">'
         + OPEN_TEXT + "</a></p>"),
        "<p>" + SIGN_IN_PARAGRAPH + "</p>",
        ('<p style="margin-top:28px;padding-top:12px;border-top:1px solid #d9dee3;'
         'font-size:13px;color:#444444;">' + FOOTER_TAGLINE + '<br><a href="'
         + HELP_URL + '" style="color:#444444;">' + HELP_TEXT + "</a></p>"),
        ('<p style="font-size:12px;color:#777777;">' + NOTICE_PARAGRAPH
         + '<br><a href="' + UNSUB_URL + '" style="color:#777777;">'
         + UNSUB_TEXT + "</a></p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


# --------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: an encoded line may not exceed 76 characters including the
# trailing soft break, and a soft break may not split an =XX escape. A break
# point is either immediately before a space, so the space leads the next line
# and is never left trailing, or immediately after a double quote, which is
# where an HTML attribute ends and a long unbreakable value such as a URL
# begins. The rightmost break point at or before column 72 wins, which is what
# puts each link alone on its own line under its href attribute.
SOFT_MAX = 76
BREAK_MAX = 72


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks."""
    text = line.replace("=", "=3D")
    out = []
    while len(text) > SOFT_MAX:
        cut = None
        for index in range(min(BREAK_MAX, len(text) - 1), 0, -1):
            if text[index] == " " or text[index - 1] == '"':
                cut = index
                break
        if cut is None:
            cut = SOFT_MAX - 1
            while cut > 1 and "=" in text[max(0, cut - 2):cut]:
                cut -= 1
        out.append(text[:cut] + "=")
        text = text[cut:]
    out.append(text)
    return out


def encode(lines):
    out = []
    for line in lines:
        out += qp_wrap(line)
    return out


def build_eml(seed):
    reference = hexid(seed, "reference", 16)
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = "<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id") + "@" + SENDER_NODE + ">"
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)

    plain = plain_part(reference)
    for line in plain:
        if len(line) > PLAIN_MAX:
            raise SystemExit("plain 7bit line over " + str(PLAIN_MAX) + " characters: " + line)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; " + STAMP_STORE,
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=softfail smtp.mailfrom=" + FROM_DOMAIN + ";",
        "  dkim=none;",
        "  dmarc=fail header.from=" + FROM_DOMAIN + " policy.dmarc=none",
        "Received-SPF: softfail (" + GATEWAY_HOST + ": domain of",
        "  " + SENDER + " does not designate " + RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + RELAY_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=~all",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + STAMP_GATEWAY,
        "Received: from " + SENDER_NODE + " ([" + SENDER_NODE_IP + "])",
        "  by " + RELAY_HOST + " with ESMTPSA id " + sender_id + ";",
        "  " + STAMP_SENDER,
        "Date: " + DATE_LOCAL,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_NAME + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT_WORD_1,
        " " + SUBJECT_WORD_2,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(reference))
    lines += ["--" + boundary + "--", ""]

    long_lines = 0
    for line in lines:
        if len(line) > 998:
            raise SystemExit("line over 998 characters: " + line)
        if len(line) > 78:
            long_lines += 1
        line.encode("ascii")
    if long_lines:
        raise SystemExit("expected no line over 78 characters, found " + str(long_lines))
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

def body_brief(reference):
    return (
        "A quiet, well formatted share notice from the signing platform, in the "
        "register of transactional mail rather than a note from a person. Brand line "
        "'Larkseal', then 'Hello Lenora,' and the opening sentence 'A document was "
        "shared with you: Q2 rate sheet.', so the body itself carries the "
        "content:file_share_lure phrase 'shared with you' and not only the Subject. "
        "Detail block of Document, 'Reference: " + reference + "' (the 16 hex "
        "character share identifier a signing platform issues, derived from the "
        "corpus seed as sha256(seed|id|reference) truncated to 16) and 'Shared: "
        "Wednesday 15 April 2026'. Three links, in this order in both parts: 'Open "
        "document' to " + OPEN_URL + ", 'Help' to " + HELP_URL + " on the vendor's "
        "genuine allowlisted host, and 'Unsubscribe' to " + UNSUB_URL + " on a "
        "third-party relay. Under the open link, the sentence that carries "
        "content:credential_request and url:login_path: the reader will be asked to "
        "'sign in' with her work email address before the document opens. Footer "
        "imitates the vendor's own ('Larkseal, secure signatures') and explains why "
        "the notice arrived, worded so that no phrase from the "
        "content:account_change_notice list appears. No urgency word, no threat, no "
        "misspelling, no deadline: nothing in the prose decides the case. The "
        "unsubscribe link sits in the body only; the message carries no "
        "List-Unsubscribe header, which is the oddity a student has to find by "
        "reading the links rather than the headers."
    )


LURE_SUMMARY = (
    "A calm share notification in the e-signature vendor's name says a rate sheet was "
    "shared and offers an Open document button. Three links are present: the open link "
    "on a lookalike host, a help link on the vendor's genuine allowlisted host, and an "
    "unsubscribe link on a third relay host."
)

MANIFEST_NOTES = (
    "The malicious half of the week 3 pair (with 005): the body reads as routine and "
    "only the extracted facts turn it, which are the lookalike sender, the three mixed "
    "hosts with one genuine decoy among them, and softfail plus dmarc fail on a "
    "policy-none record. Extraction practice for an RFC 2047 encoded-word Subject with "
    "curly quotes and for listing every host. Not escalated: ordinary recipient, no "
    "interaction. Rendering: the Subject ships as two adjacent encoded words, "
    "'" + SUBJECT_WORD_1 + "' and '" + SUBJECT_WORD_2 + "', folded onto two lines, "
    "because RFC 2047 sec. 2 caps one encoded word at 75 characters and the single "
    "84 character word the manifest first carried is over that cap; white space "
    "between adjacent encoded words is dropped on decoding, so the space before 'was' "
    "rides inside the second word as its leading underscore and the header decodes to "
    "'" + SUBJECT_DECODED + "'. The subject field above now holds that decoded text, "
    "which is what a parser and a reader both see and what tools/validate_corpus.py "
    "compares against the file. Week 5 loop: no tool is decisive on its own, so the "
    "loop spends all three and stops with tools_exhausted; reputation returns unknown "
    "and first seen the same day, check_urls returns unlisted, allowlisted and "
    "unlisted across the three hosts, and lookup_recipient returns an ordinary "
    "mailbox. The allowlisted help host is the pressure fact: a loop that stops on it "
    "calls the message benign."
)

MANIFEST_INDICATORS = [
    "auth:spf_softfail",
    "auth:dkim_none",
    "auth:dmarc_fail",
    "sender:lookalike_domain:larkseal.example",
    "sender:display_name_claims_vendor:Larkseal",
    "sender:first_seen",
    "header:encoded_word_subject",
    "url:multiple_hosts",
    "url:lookalike_host:review.larkseal-review.example",
    "url:host_unlisted:review.larkseal-review.example",
    "url:host_allowlisted:help.larkseal.example",
    "url:host_unlisted:unsub.mailer-relay-links.example",
    "url:login_path",
    "content:file_share_lure",
    "content:credential_request",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
]

GT_INDICATORS = [
    {"code": "auth:spf_softfail", "where": "Authentication-Results",
     "value": "spf=softfail smtp.mailfrom=" + FROM_DOMAIN},
    {"code": "auth:dkim_none", "where": "Authentication-Results", "value": "dkim=none"},
    {"code": "auth:dmarc_fail", "where": "Authentication-Results",
     "value": "dmarc=fail header.from=" + FROM_DOMAIN + " policy.dmarc=none"},
    {"code": "sender:lookalike_domain", "where": "From", "value": IMITATED_DOMAIN},
    {"code": "sender:display_name_claims_vendor", "where": "From", "value": SENDER_DISPLAY},
    {"code": "sender:first_seen", "where": "check_sender_reputation", "value": "2026-04-15"},
    {"code": "header:encoded_word_subject", "where": "Subject", "value": SUBJECT_RAW},
    {"code": "url:multiple_hosts", "where": "body", "value": ", ".join(URL_HOSTS)},
    {"code": "url:lookalike_host", "where": "body", "value": URL_HOSTS[0]},
    {"code": "url:host_unlisted", "where": "check_urls", "value": URL_HOSTS[0]},
    {"code": "url:host_allowlisted", "where": "check_urls", "value": URL_HOSTS[1]},
    {"code": "url:host_unlisted", "where": "check_urls", "value": URL_HOSTS[2]},
    {"code": "url:login_path", "where": "body", "value": OPEN_URL},
    {"code": "content:file_share_lure", "where": "body", "value": "shared with you"},
    {"code": "content:credential_request", "where": "body", "value": "sign in"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
]

REFERENCE_SUMMARY = (
    "This share notice is fake: the sender and the Open link use a look-alike of "
    "Larkseal's name, even though the Help link points to their real site. Nobody "
    "shared a rate sheet with you, and the link has been blocked."
)

GT_NOTES = (
    "Attacker-owned added-word lookalike of the electronic signature vendor, rendered "
    "as an ordinary share notice. larkseal-review.example publishes an SPF record "
    "ending ~all and a DMARC record with policy none and publishes no DKIM selector, "
    "so mail from the cheap relay at 198.51.100.144 earns spf=softfail, dkim=none and "
    "dmarc=fail policy.dmarc=none, and the message is delivered rather than "
    "quarantined. The display name Larkseal claims the vendor whose real domain is "
    "larkseal.example, which data/display_names.json records with the mismatch "
    "indicator sender:display_name_claims_vendor. Key facts: from_domain "
    "larkseal-review.example, first seen 2026-04-15, one message in 90 days and no "
    "prior report, so reputation is unknown rather than known_bad; reply_to none; "
    "three link hosts in both parts, review.larkseal-review.example (unlisted, and a "
    "lookalike of larkseal.example), help.larkseal.example (allowlisted, the vendor's "
    "real help site) and unsub.mailer-relay-links.example (unlisted); no attachment; "
    "no In-Reply-To; no List-Unsubscribe header even though the body carries an "
    "unsubscribe link. Playbook rule 2: a vendor's name over a domain the vendor does "
    "not own is impersonation, whatever the other links do. Difficulty hard: three "
    "decisive facts (sender:lookalike_domain, sender:display_name_claims_vendor, "
    "url:lookalike_host) against one fact pushing the other way, the allowlisted help "
    "host recorded as url:host_allowlisted, which puts the base tier at medium, and "
    "body_only_read benign moves it one step to hard. The Subject is an RFC 2047 "
    "encoded word, which is extraction practice and not a malicious signal: it ships "
    "as two adjacent encoded words, '" + SUBJECT_WORD_1 + "' and '" + SUBJECT_WORD_2
    + "', folded onto two lines, because RFC 2047 sec. 2 caps one word at 75 "
    "characters, and it decodes to '" + SUBJECT_DECODED + "'. The curly quotes around "
    "the document title live in the Subject alone; both body parts are seven-bit ASCII. "
    "url:login_path is carried by the link text and the sentence beside it rather than "
    "by the path: the anchor reads 'Open document' and the next sentence says the "
    "reader will be asked to sign in with her work email address before the document "
    "opens, which is what the vocabulary entry means by 'a link path or text asks for "
    "a sign-in'. body_only_read is benign because the prose alone is an ordinary share "
    "notice: it names a plausible document, sets no deadline, threatens nothing and "
    "misspells nothing, so a reader who never looks at a header or a host closes it as "
    "safe. That reversal is what makes this the hard half of the week 3 pair with 005, "
    "where the body pushes toward malicious and the facts say benign. Week 5 loop: "
    "check_sender_reputation returns unknown at domain level with first_seen "
    "2026-04-15 and no prior report, which is suggestive and not decisive; check_urls "
    "returns unlisted, allowlisted and unlisted, which is decisive for no single host; "
    "lookup_recipient returns an ordinary mailbox with three prior reports and one "
    "true positive. Nothing stops the loop early, so it spends all three tools and "
    "stops with tools_exhausted, and the verdict comes from reading the sender and the "
    "hosts together rather than from any one result. Grading note: a loop that stops "
    "when check_urls returns allowlisted for help.larkseal.example has read one host "
    "out of three, and a loop that reads unknown reputation as clean has confused an "
    "absent history with a good one. Does not escalate: l.vashti carries no executive "
    "or payments flag, she did not interact with the message, the organization's own "
    "domain was not forged and no trusted sender failed authentication, so the action "
    "is block_and_purge. Deliberate omissions, matching the manifest indicator list: "
    "no Reply-To, no X-Priority, no Auto-Submitted, no X-Originating-IP, no "
    "DKIM-Signature and no list headers."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [3],
    "date": "2026-04-15T08:47:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "hard",
    "body_only_read": "benign",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT_DECODED,
    "arrival_path": "external_gateway",
    "auth": {"spf": "softfail", "dkim": "none", "dmarc": "fail", "dmarc_policy": "none"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:lookalike_domain", "url:lookalike_host"],
    "url_hosts": list(URL_HOSTS),
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": FROM_DOMAIN,
            "status": "unknown",
            "first_seen": "2026-04-15",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {
            URL_HOSTS[0]: "unlisted",
            URL_HOSTS[1]: "allowlisted",
            URL_HOSTS[2]: "unlisted",
        },
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
    "recommended_action": "block_and_purge",
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
    reference = hexid(seed, "reference", 16)

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    # Semantic fields are the specification and are read, never rewritten. The
    # indicator list is written back only after it is proved identical, so a
    # later edit to the manifest shows up as a loud failure here instead of
    # being silently overwritten.
    if record["indicators"] != MANIFEST_INDICATORS:
        raise SystemExit("manifest indicator list for " + EMAIL_ID
                         + " differs from the list this generator renders")
    if record["subject"] not in (SUBJECT_AUTHORED, SUBJECT_DECODED):
        raise SystemExit("manifest subject for " + EMAIL_ID + " is unexpected: "
                         + repr(record["subject"]))

    data = build_eml(seed)
    with open(EML_PATH, "wb") as handle:
        handle.write(data)

    # Read it back the way the week 1 helper does.
    parsed = email.message_from_bytes(data, policy=email.policy.default)
    if parsed.defects:
        raise SystemExit("defects: " + repr(parsed.defects))
    for part in parsed.walk():
        if part.defects:
            raise SystemExit("part defects: " + repr(part.defects))
    if str(parsed["Subject"]) != SUBJECT_DECODED:
        raise SystemExit("decoded Subject is " + repr(str(parsed["Subject"])))

    subject_rewritten = record["subject"] != SUBJECT_DECODED
    record["subject"] = SUBJECT_DECODED
    record["indicators"] = list(MANIFEST_INDICATORS)
    record["body_brief"] = body_brief(reference)
    record["lure_summary"] = LURE_SUMMARY
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
    print("updated the manifest prose and upserted ground truth for " + EMAIL_ID)
    if subject_rewritten:
        print(MANIFEST_SUBJECT_NOTE)


if __name__ == "__main__":
    main()
