#!/usr/bin/env python3
"""Regenerate 036-sandmarsh-positive-pay-exception.

Rebuilds emails/batch/036-sandmarsh-positive-pay-exception.eml byte for byte
from the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

Every identifier in the file that looks random is derived from the corpus
seed, so rerunning this script reproduces the same bytes:

    hex(label, n)    = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = the first n bytes of
                       sha256("<seed>|<email id>|<label>|0")
                       || sha256("<seed>|<email id>|<label>|1") || ...

    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=hex("store-id", 32), version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

The bh= tag is the plain digest, which is already the 32 bytes a SHA-256 body
hash is, so no block indexed stream is needed for it. The b= tag needs 256
bytes for a 2048 bit signature, which one digest cannot supply, so that value
comes from the block indexed stream. Neither verifies: no .example domain can
publish a DKIM key, and no lab in the course checks a signature. The course
reads the gateway's Authentication-Results verdict instead, which is what
RFC 9989 sec. 5.3.6 asks a receiver to write.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox, not
of the path the message arrived on. r.palomares@pellgrave.example lives on
mailstore-01.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are present because the message crossed the border
    gateway. All three checks pass. They pass for the bank, and the way they
    pass is the point of this file: SPF is evaluated on the alerts subdomain,
    which publishes its own record (ip4:203.0.113.70 -all in
    data/domain_policy.json), while the DKIM signature is the parent domain's,
    d=sandmarshbank.example s=smb1. The parent shares the organizational
    domain of the From host, so DKIM aligns under relaxed alignment and DMARC
    passes against the parent's published policy of reject.
  * Auto-Submitted: auto-generated, because a positive pay exception alert is
    written by the bank's overnight presentment run and not by a person
    (RFC 3834 sec. 5). It sits with the author's client headers, below
    Message-ID, the same place 002 and 017 put it.
  * X-Priority: 1 with Importance: high, because a bank stamps an item that
    has a same day cutoff. The corpus puts the same pair on the anchor lure
    001, so a priority flag is a fact seen on both verdicts and never a
    verdict of its own.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 3.7 match the
    received_path_hint. The score is not low because the body carries money, a
    deadline and a link, which is exactly the pressure the record counts.
  * The gateway banner is inserted into both parts, because the gateway stamps
    the mail it marks as external.
  * The MIME boundary prefix is =_part_, the neutral prefix the corpus gives a
    third party platform that composes its own mail; =_swk_ belongs to the
    messages the Sentrywick stack composes.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because reply_to is null in the record and the alerting platform
bounces to the mailbox it sends from; no In-Reply-To and no References, so
thread:new holds; no X-Sentrywick-Removed-Attachment, so attachment:none
holds; no X-Originating-IP, which belongs to webmail submissions.

Run:  python3 corpus/tools/generators/gen_036_sandmarsh_positive_pay_exception.py
"""

import base64
import calendar
import email
import email.policy
import hashlib
import json
import os
import re
import time
import uuid

EMAIL_ID = "036-sandmarsh-positive-pay-exception"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "alerts@alerts.sandmarshbank.example"
SENDER_DISPLAY = "Sandmarsh Community Bank Alerts"
# The envelope sender is the From mailbox. The alerting platform bounces to
# the same mailbox it sends from, so Return-Path, smtp.mailfrom and From are
# one address and there is no envelope versus author split for a student to
# chase. That also keeps SPF on the exact domain that publishes the record:
# an SPF record never covers subdomains, and alerts.sandmarshbank.example
# publishes its own.
ENVELOPE_SENDER = SENDER
RECIPIENT = "r.palomares@pellgrave.example"
RECIPIENT_DISPLAY = "Rutger Palomares"
REPORTER = "r.palomares@pellgrave.example"

SUBJECT = "Positive pay exception: decision required by 1:00 PM CT today"

# The From host is the bank's alert subdomain; the signing domain is the
# parent. data/domain_policy.json records both, and the split is the whole
# lesson of this file.
FROM_DOMAIN = "alerts.sandmarshbank.example"
SIGNING_DOMAIN = "sandmarshbank.example"
SENDER_HOST = "alerts-out.sandmarshbank.example"
SENDER_SUBMIT_HOST = "presentment-03.alerts.sandmarshbank.example"
SENDER_IP = "203.0.113.70"
SENDER_SUBMIT_IP = "192.0.2.70"
DKIM_SELECTOR = "smb1"
SPF_MECHANISM = "ip4:203.0.113.70"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The one link. Its host is the bank's own alert subdomain, which nobody ever
# put on url_allowlist.json even though business.sandmarshbank.example has
# been on it for years. That gap is the fact url:host_unlisted keys on, and it
# is the reason the message is benign and still escalates: playbook rule 7
# says a host on neither list is unknown, not clean. The path is an exception
# path and not a sign-in path, so url:login_path does not apply.
LINK = "https://alerts.sandmarshbank.example/positive-pay/exceptions"
LINK_LABEL = "Review exception"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 14:02 +0000 is the same instant as 09:02 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. 09:02 local is minutes after
# the bank opens its exception window, which is why a 1:00 PM cutoff is a
# working morning and not a countdown.
DATE_HEADER = "Thu, 23 Apr 2026 09:02:00 -0500"
SUBMIT_STAMP = "Thu, 23 Apr 2026 14:02:02 +0000"
SUBMIT_UTC = "2026-04-23 14:02:02"
GATEWAY_STAMP = "Thu, 23 Apr 2026 09:02:05 -0500"
STORE_STAMP = "Thu, 23 Apr 2026 09:02:07 -0500"
MESSAGE_ID_STAMP = "20260423140200"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break. The wrap below breaks at the last space that fits
# and carries that space to the next line, so decoding restores the logical
# line byte for byte.
QP_MAXLEN = 76

# RFC 6376 sec. 3.5 folds the b= tag across continuation lines. 72 base64
# characters per line keeps every line inside the 78 character fold width.
DKIM_FOLD = 72


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def store_id(seed):
    return str(uuid.UUID(hex=hexid(seed, "store-id", 32), version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def signature(seed):
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


def dkim_time():
    """Unix time of the sender-side Received stamp, so the two cannot drift."""
    return calendar.timegm(time.strptime(SUBMIT_UTC, "%Y-%m-%d %H:%M:%S"))


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
# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries exactly two content codes: content:banking_instruction on
# "positive pay exception", "approve or return" and "decision required", and
# content:urgency_keywords on "by 1:00 pm" and "today". No phrase from any
# other content list may appear in either decoded part, and no further phrase
# from those two lists may appear either, because validate_corpus.py checks
# the phrase lists both ways and checks that every recorded value is an entry
# in its list. The generator recomputes the match itself before writing, so a
# reworded sentence fails here rather than in the validator.
#
#   "wire" is out, though it is on the banking_instruction list. A positive
#   pay exception is a paper item presented against an account, and a bank
#   that said "wire" in this notice would be describing a different product.
#   "invoice", "past due", "remit" and "amount due" are out
#   (content:payment_request). Nothing is owed to the bank; the money is the
#   company's own and the bank is asking what to do with it. The amounts are
#   therefore labelled "Amount presented" and "Amount on the issued file".
#   "sign in", "log in" and "password" are out (content:credential_request).
#   The alert names Business Online Banking as a second place the same
#   decision can be recorded, and never asks for an identity. That is the
#   difference between this file and 046, which imitates the same bank and
#   does ask.
#   "download" is out (content:file_share_lure). Nothing is offered as a file.
#   "if you did not" and "was changed" are out
#   (content:account_change_notice). Nothing about the account changed; an
#   item was presented and is waiting on a decision.
#   "call me" and "call the number on file" are out
#   (content:phone_verification_offered), and so is any dialable number. The
#   fraud line points at the number printed on the back of the card, which is
#   what a bank prints and what makes the SOC's callback possible without the
#   message supplying the number to call. A benign email that handed over a
#   phone number would be handing over the very thing the callback exists to
#   check.
#   "hold the payment", "pay today" and the rest of
#   content:payment_timing_request are out. Nothing is moved, held or released
#   early; a decision either lets an item through or sends it back.
#   "confidential" is out (content:secrecy_request), even though a real bank
#   footer often carries it.
#   "automated" is not used either. It sits on the content:instruction_to_ai
#   list, which validate_corpus.py skips because ordinary mail uses the word
#   honestly, and 017 does use it. Here the Auto-Submitted header already
#   says the same thing to the only reader that needs it, so the footer says
#   nothing about who typed the message.
#
# The deadline is a bank cutoff written once, as a time of day with a stated
# consequence, rather than a countdown. That is what makes this the hard
# negative: the body alone reads malicious, and every fact that settles it
# comes from a header or a tool.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

MASTHEAD = "Sandmarsh Community Bank"
SUBHEAD = "Treasury Services"
HEADING = "Positive pay exception"
GREETING = "Dear Rutger Palomares,"

PARA_LEAD = [
    "One item presented against your operating account ending 4021 does not",
    "match the issued file, so it is being held as a positive pay exception.",
]

# The item, in the order a bank prints it. The two amounts are the reason the
# item stopped: 20891 was issued for 418.00 and arrived for 4,180.00. The
# exception reference is the checkable string every legitimate message in the
# corpus carries, and it is the string the analyst reads out when the callback
# in playbook rule 5 happens.
DETAIL_LINES = [
    "Check number: 20891",
    "Amount presented: $4,180.00",
    "Amount on the issued file: $418.00",
    "Presented: 4/23/2026",
    "Exception: the amount does not match the issued item",
    "Exception reference: PP-20260423-0007",
]

PARA_DECISION = [
    "Decision required by 1:00 PM CT today. Open the exception and tell us",
    "whether to approve or return the item. If no decision is recorded by",
    "1:00 PM CT the item is returned unpaid and the account is not charged.",
]

PARA_ALTERNATIVE = [
    "The same decision can be recorded in Business Online Banking under",
    "Positive Pay.",
]

PARA_FRAUD = [
    "Sandmarsh Community Bank will never ask you for account details by",
    "email. To report fraud, use the number printed on the back of your",
    "card.",
]

FOOTER = [
    "Sandmarsh Community Bank, Treasury Services",
    "This mailbox is not monitored.",
]

# Phrases the week 3 extractor keys on. validate_corpus.py lowercases the
# decoded parts and searches them without normalizing white space, so each of
# these has to sit whole on one line of each part; the generator proves it
# below, matching case-insensitively the way the validator does.
LINE_SAFE_PHRASES = [
    "positive pay exception",
    "decision required",
    "by 1:00 PM CT today",
    "approve or return",
    LINK_LABEL,
]

# Wording 046 reproduces when it imitates this bank's footer.
COPIED_PHRASES = [
    "Sandmarsh Community Bank will never ask you for account details by "
    "email. To report fraud, use the number printed on the back of your card.",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", MASTHEAD, SUBHEAD, "", HEADING, "", GREETING, ""]
    lines += PARA_LEAD + [""]
    lines += DETAIL_LINES + [""]
    lines += PARA_DECISION + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_ALTERNATIVE + [""]
    lines += PARA_FRAUD + [""]
    lines += FOOTER
    return lines


def detail_html():
    """The item block as one paragraph, the same six lines in the same order."""
    block = [line + "<br>" for line in DETAIL_LINES[:-1]]
    block[0] = '<p style="font-family:monospace;font-size:14px;">' + block[0]
    block.append(DETAIL_LINES[-1] + "</p>")
    return block


def html_part():
    lines = [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#eef1f4;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#1f1f1f;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 30px;'
         'background-color:#ffffff;border:1px solid #d5dae0;">'),
        ('<p style="margin:0;font-size:20px;font-weight:bold;'
         'color:#14472f;">' + MASTHEAD + "</p>"),
        ('<p style="margin:2px 0 20px 0;font-size:13px;color:#556;">'
         + SUBHEAD + "</p>"),
        ('<p style="font-size:17px;font-weight:bold;">' + HEADING + "</p>"),
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_LEAD) + "</p>",
    ]
    lines += detail_html()
    lines += ["<p>" + joined(PARA_DECISION) + "</p>"]
    # The href is the address the plain part prints and the button text is the
    # label the plain part prints, so a reader of either part sees the same
    # link with the same name. No image, no script, no form, no hidden text.
    lines += [
        ('<p style="margin:24px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:12px 22px;'
         'background-color:#14472f;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">' + LINK_LABEL + "</a></p>"),
        ('<p style="font-size:13px;color:#555555;">If the button does not '
         'open, the address is ' + LINK + "</p>"),
        "<p>" + joined(PARA_ALTERNATIVE) + "</p>",
        ('<p style="margin-top:26px;padding-top:12px;'
         'border-top:1px solid #d5dae0;font-size:13px;color:#444444;">'
         + joined(PARA_FRAUD) + "</p>"),
        ('<p style="font-size:12px;color:#777777;">'
         + "<br>".join(FOOTER) + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]
    return lines


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start
    of the next line; when no space fits, hard-break at 75 characters plus the
    soft line break, never inside an =XX escape.
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


# --------------------------------------------------------- phrase self-check
#
# validate_corpus.py runs the enums.json phrase lists against the decoded body
# parts in both directions: a phrase with no indicator fails, and an indicator
# with no phrase fails, and every recorded value has to be built from the list
# it belongs to. The same computation runs here, against the same lists, so a
# reworded sentence stops this script instead of shipping a file the validator
# will reject. content:non_english_body and content:instruction_to_ai are left
# out for the reason validate_corpus.py leaves them out: their lists are
# stopwords and single ordinary words rather than a membership test.

PHRASE_PASS_SKIP = ("content:non_english_body", "content:instruction_to_ai")


def content_matches():
    """{code: "phrase; phrase"} for every body phrase list the parts match."""
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    where_of = {}
    for entry in enums["indicator_vocabulary"]:
        where_of[entry["code"]] = entry.get("where")
    body = ("\n".join(plain_part()) + "\n" + "\n".join(html_part())).lower()
    found = {}
    for code, phrases in enums["content_phrases"].items():
        if code in PHRASE_PASS_SKIP or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases if phrase.lower() in body]
        if hits:
            found[code] = "; ".join(hits)
    return found


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # RFC 8601 sec. 4: the gateway writes Authentication-Results above its
        # own trace field. SPF is checked on the alerts subdomain, which
        # publishes its own record; the signature is the parent domain's and
        # aligns with the From domain under relaxed alignment (RFC 7489 sec.
        # 3.1), so DMARC passes against the parent's policy of reject.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + FROM_DOMAIN + ";",
        "  dkim=pass header.d=" + SIGNING_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SIGNING_DOMAIN + ";",
        "  dmarc=pass header.from=" + FROM_DOMAIN + " policy.dmarc=reject",
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom;",
        "  mechanism=" + SPF_MECHANISM,
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 3.7",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_HOST,
        "  (" + SENDER_HOST + " [" + SENDER_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + SENDER_SUBMIT_HOST,
        "  ([" + SENDER_SUBMIT_IP + "])",
        "  by " + SENDER_HOST + " with ESMTPSA id " + sender_id + ";",
        "  " + SUBMIT_STAMP,
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SIGNING_DOMAIN + "; s=" + DKIM_SELECTOR + "; t=" + str(dkim_time()) + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash(seed) + ";",
    ]
    blob = signature(seed)
    chunks = [blob[index:index + DKIM_FOLD] for index in range(0, len(blob), DKIM_FOLD)]
    lines.append("  b=" + chunks[0])
    for chunk in chunks[1:]:
        lines.append("   " + chunk)
    lines += [
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # RFC 3834 sec. 5: the overnight presentment run sent this, not a
        # person, and a reply to it reaches no one.
        "Auto-Submitted: auto-generated",
        # RFC 4021 sec. 2.1.52 for Importance. A same day cutoff is why a bank
        # stamps these; 001 stamps the same pair with nothing behind it.
        "X-Priority: 1",
        "Importance: high",
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
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += qp_body(html_part())
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part())
    html_text = "\n".join(html_part())
    for phrase in LINE_SAFE_PHRASES:
        if phrase.lower() not in plain_text.lower():
            raise SystemExit("plain part broke the phrase across lines: " + phrase)
        if phrase.lower() not in html_text.lower():
            raise SystemExit("html part broke the phrase across lines: " + phrase)
    for phrase in COPIED_PHRASES:
        if phrase not in " ".join(plain_text.split()):
            raise SystemExit("plain part lost the wording: " + phrase)
        if phrase not in " ".join(html_text.split()):
            raise SystemExit("html part lost the wording: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if LINK not in plain_text or 'href="' + LINK + '"' not in html_text:
        raise SystemExit("the one link must appear in both parts")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

LURE_SUMMARY = (
    "The company's bank reports a check that does not match the issued file "
    "and asks the CFO to approve or return it before the afternoon cutoff. "
    "The link goes to the bank's alerts subdomain, which is not on the "
    "allowlist even though the bank's business banking host is."
)

BODY_BRIEF = (
    "The bank's standard exception alert, under a Sandmarsh Community Bank "
    "and Treasury Services masthead, headed 'Positive pay exception' and "
    "addressed to Rutger Palomares by name. Open with 'One item presented "
    "against your operating account ending 4021 does not match the issued "
    "file, so it is being held as a positive pay exception.' Then the item, "
    "printed the way a bank prints it: check number 20891, amount presented "
    "$4,180.00, amount on the issued file $418.00, presented 4/23/2026, "
    "exception the amount does not match the issued item, exception "
    "reference PP-20260423-0007. Then the ask: 'Decision required by 1:00 PM "
    "CT today. Open the exception and tell us whether to approve or return "
    "the item. If no decision is recorded by 1:00 PM CT the item is returned "
    "unpaid and the account is not charged.' One link, labeled 'Review "
    "exception', to https://alerts.sandmarshbank.example/positive-pay/"
    "exceptions, then a line that the same decision can be recorded in "
    "Business Online Banking under Positive Pay. Footer: the bank will never "
    "ask for account details by email, and fraud is reported on the number "
    "printed on the back of the card, so no dialable number appears in the "
    "body. Close with 'Sandmarsh Community Bank, Treasury Services' and "
    "'This mailbox is not monitored.' The only content phrases in the body "
    "are 'positive pay exception', 'approve or return' and 'decision "
    "required' for the banking instruction, and 'by 1:00 pm' and 'today' for "
    "the urgency."
)

MANIFEST_NOTES = (
    "Real, and the allowlist is incomplete, which is how allowlists are: the "
    "reputation tool matches the organizational domain sandmarshbank.example "
    "(trusted) but the alerts host is not on the URL allowlist. Benign with "
    "escalation: the playbook requires callback verification before acting on "
    "any bank instruction, and the SOC adds the subdomain to the allowlist "
    "afterward. Escalation reasons: callback_verification. Rendered: From is "
    "Sandmarsh Community Bank Alerts over alerts.sandmarshbank.example, the "
    "bank's own alert subdomain, and display_names.json puts the bank's name "
    "on sandmarshbank.example, which is that host's organizational domain, so "
    "no display name indicator applies; spf=pass on the subdomain, which "
    "publishes its own record, dkim=pass with d=sandmarshbank.example "
    "s=smb1, and dmarc=pass with policy reject, because the parent's "
    "signature aligns with the subdomain under relaxed alignment; "
    "Auto-Submitted: auto-generated marks the presentment run and X-Priority "
    "1 with Importance high marks the cutoff, the same pair 001 stamps with "
    "nothing behind it; scan result clean and spam score 3.7. The body names "
    "check 20891 presented for $4,180.00 against an issued $418.00 and gives "
    "the exception reference PP-20260423-0007, which is the string the "
    "analyst reads out on the callback. No dialable number appears in the "
    "body on purpose: the fraud line points at the number printed on the back "
    "of the card, so the message cannot supply the very channel the callback "
    "exists to check. 046 imitates this bank and copies this footer."
)

# ------------------------------------------------------------- ground truth

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=alerts.sandmarshbank.example; dkim=pass "
    "header.d=sandmarshbank.example header.s=smb1 "
    "header.i=@sandmarshbank.example; dmarc=pass "
    "header.from=alerts.sandmarshbank.example policy.dmarc=reject"
)

NOTES = (
    "The hard negative of the week 7 batch: a real bank alert that reads like "
    "a phishing lure and is settled only by the headers and the tools. Key "
    "facts a correct extractor produces: from_domain "
    "alerts.sandmarshbank.example, the bank's own alert subdomain; no "
    "Reply-To, so there is no Reply-To mismatch to find; "
    "display_name_mismatch false, because display_names.json puts the name "
    "Sandmarsh Community Bank on sandmarshbank.example and that is the "
    "organizational domain of the From host; spf=pass on "
    "alerts.sandmarshbank.example, which publishes its own SPF record "
    "(ip4:203.0.113.70 -all), dkim=pass with d=sandmarshbank.example s=smb1, "
    "and dmarc=pass with policy reject, because the parent's signature shares "
    "the organizational domain of the From header and therefore aligns under "
    "relaxed alignment; one link host, alerts.sandmarshbank.example, carrying "
    "the single link "
    "https://alerts.sandmarshbank.example/positive-pay/exceptions, whose path "
    "is an exception path and not a sign-in path, so url:login_path does not "
    "apply; no attachment header; no In-Reply-To, so the message opens a "
    "thread. Received chain: presentment-03.alerts.sandmarshbank.example "
    "[192.0.2.70] submitted with ESMTPSA to alerts-out.sandmarshbank.example "
    "at 14:02:02 +0000, which handed off with ESMTPS and TLS1_3 to "
    "mx.pellgrave.example [10.20.4.10] at 09:02:05 -0500, delivered by LMTP "
    "to mailstore-01.pellgrave.example at 09:02:07 -0500; Date is 09:02:00 "
    "-0500, the same instant as 14:02:00 +0000 in the Message-ID. "
    "X-Sentrywick-External is yes, scan result clean, spam score 3.7, "
    "Auto-Submitted is auto-generated, and X-Priority 1 with Importance high "
    "is the pair the corpus also puts on the anchor lure 001, so a priority "
    "flag is a fact seen on both verdicts and never a verdict of its own. "
    "Body content: the phrases are 'positive pay exception', 'approve or "
    "return' and 'decision required' for content:banking_instruction, and "
    "'by 1:00 pm' and 'today' for content:urgency_keywords. No credential, "
    "payment, payment-change, payment-timing, data, file-share, secrecy, "
    "channel or account-change phrase appears; the word 'wire' was kept off "
    "the banking list on purpose, because a positive pay exception is a paper "
    "item and not a transfer. The two decisive-looking amounts, $4,180.00 "
    "presented against $418.00 issued, and the exception reference "
    "PP-20260423-0007, are the checkable facts the callback quotes. No "
    "dialable number appears in the body: the fraud line points at the number "
    "printed on the back of the card, so the message never supplies the "
    "channel the out-of-band check is supposed to use. Difficulty reason: the "
    "tier rule counts one decisive benign fact, an allowlisted sender with "
    "dmarc=pass, against two pressure facts, the banking instruction and the "
    "urgency, so pressure exceeds decisive and the base tier is hard; there "
    "is no injection, and the body-only read is malicious, the opposite of "
    "the verdict, which adds a step and stays capped at hard. The body-only "
    "read is malicious because money, a same-day cutoff and a link to a host "
    "nobody recognizes is the exact shape of a bank-themed lure, and 046 "
    "imitates this same bank with the same footer. Week 7 use: this is the "
    "case where every tool answers and nothing is decisive. "
    "check_sender_reputation matches the organizational domain and returns "
    "trusted for sandmarshbank.example, first seen 2020-08-17, 88 messages "
    "in 90 days and no prior reports, which is a match on the parent and not "
    "on the host in the link; check_urls returns unlisted for "
    "alerts.sandmarshbank.example, because business.sandmarshbank.example was "
    "allowlisted years ago and the alerts host never was; lookup_recipient "
    "returns the CFO, executive and handling payments, with three prior "
    "reports and two true positives. The loop runs all three tools and stops "
    "with stop_reason tools_exhausted. Playbook rules 1, 5 and 7 decide it: "
    "the passes name a domain and prove nothing about the instruction, a host "
    "on neither list is unknown rather than clean, and any instruction about "
    "money gets a phone call to the number on file first and escalates "
    "whatever the verdict. So the verdict is benign, escalate_expected is "
    "true with the single reason callback_verification, and the action is "
    "verify_out_of_band_then_close. Full credit on the indicators criterion "
    "needs sender:allowlisted_domain and content:banking_instruction. "
    "recipient:prior_similar_report does not apply: a banking instruction "
    "maps to no campaign tag under prior_similar_report_rule, so the CFO's "
    "earlier cfo-impersonation and vendor-invoice-fraud reports say nothing "
    "about this message. Grading note: a student who calls this malicious "
    "because the link host is unlisted has turned rule 7 into a verdict, and "
    "a student who calls it benign and closes it has skipped rule 5. Story "
    "context: this is the real bank behind the corpus, the same bank whose "
    "account ending 3318 is the remit-to on the Slatemoor thread, and 046 "
    "imitates it in the exam set with a lookalike host and an output-shaped "
    "block. The SOC's own follow-up is to add alerts.sandmarshbank.example to "
    "the allowlist after the callback confirms the item. Rendering notes: the "
    "plain part is 7bit with hard wraps under 78 characters and the HTML part "
    "is quoted-printable, because the fixed gateway banner snippet is longer "
    "than 78 characters; the banner is the first line of the plain part and "
    "the first line after the body tag in the HTML part; both parts carry the "
    "same words in the same order and the HTML part hides nothing, so there "
    "is no content:html_hidden_text. The MIME boundary prefix is =_part_, the "
    "prefix the corpus gives a third party platform that composes its own "
    "mail. There is no X-Originating-IP: the sender is a bank's alerting "
    "platform rather than a webmail provider, so the submitting node's "
    "address 192.0.2.70 appears in the bottom Received line instead. Every "
    "identifier that looks random is derived from a SHA-256 over the corpus "
    "seed, the email id and a label, so the file regenerates byte for byte."
)

REFERENCE_SUMMARY = (
    "This is a real alert from our bank about a check that needs a decision "
    "today. Because it involves money, please confirm the item by phone with "
    "the bank before approving anything, which is our normal rule."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-23T09:02:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "hard",
    "body_only_read": "malicious",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass",
             "dmarc_policy": "reject"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": AUTH_VALUE},
        {"code": "sender:allowlisted_domain", "where": "check_sender_reputation",
         "value": SIGNING_DOMAIN},
        {"code": "url:host_unlisted", "where": "check_urls",
         "value": "alerts.sandmarshbank.example"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "by 1:00 pm; today"},
        {"code": "content:banking_instruction", "where": "body",
         "value": "positive pay exception; approve or return; decision required"},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "header:x_priority_high", "where": "X-Priority, Importance",
         "value": "1, high"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:executive", "where": "lookup_recipient",
         "value": RECIPIENT},
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": RECIPIENT},
    ],
    "required_indicators": ["sender:allowlisted_domain",
                            "content:banking_instruction"],
    "url_hosts": ["alerts.sandmarshbank.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SIGNING_DOMAIN,
            "status": "trusted",
            "first_seen": "2020-08-17",
            "messages_90d": 88,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": "The company's bank; allowlisted.",
            "match_level": "organizational_domain",
        },
        "check_urls": {"alerts.sandmarshbank.example": "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Rutger Palomares",
            "role": "Chief Financial Officer",
            "mailbox_type": "person",
            "executive": True,
            "handles_payments": True,
            "chronic_reporter": False,
            "report_count_90d": 3,
            "true_positive_count_90d": 2,
            "campaign_tags": ["cfo-impersonation", "marketing",
                              "vendor-invoice-fraud"],
        },
    },
    "expected_loop": {
        # Three tools exist. The reputation answer is a match on the parent
        # domain rather than on the host in the link, the URL answer is
        # "unlisted", which playbook rule 7 calls unknown and not clean, and
        # the recipient answer adds context rather than a verdict. Nothing is
        # decisive, so the run ends because there is no tool left to try.
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
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
    "notes": NOTES,
}


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def two_sentences(text):
    return len([part for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part]) == 2


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

    # The manifest is the specification. Every semantic field the generator
    # renders is read back from it before anything is written, so a drift
    # between the two stops the run instead of shipping a file.
    for field, value in (("subject", SUBJECT),
                         ("sender_address", SENDER),
                         ("sender_display", SENDER_DISPLAY),
                         ("recipient", RECIPIENT),
                         ("reporter", REPORTER),
                         ("set", GROUND_TRUTH["set"]),
                         ("date", GROUND_TRUTH["date"]),
                         ("verdict", GROUND_TRUTH["verdict"]),
                         ("category", GROUND_TRUTH["category"]),
                         ("difficulty", GROUND_TRUTH["difficulty"]),
                         ("body_only_read", GROUND_TRUTH["body_only_read"]),
                         ("arrival_path", GROUND_TRUTH["arrival_path"]),
                         ("recommended_action", GROUND_TRUTH["recommended_action"]),
                         ("escalate_expected", GROUND_TRUTH["escalate_expected"])):
        if record.get(field) != value:
            raise SystemExit("manifest " + field + " is " + repr(record.get(field))
                             + " but the generator renders " + repr(value))
    if record["weeks"] != GROUND_TRUTH["weeks"]:
        raise SystemExit("weeks do not match the manifest")
    if record["auth"] != {"spf": "pass", "dkim": "pass", "dmarc": "pass"}:
        raise SystemExit("auth does not match the manifest")
    if record["url_hosts"] != GROUND_TRUTH["url_hosts"]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["escalation_reasons"] != GROUND_TRUTH["escalation_reasons"]:
        raise SystemExit("escalation_reasons do not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("manifest carries a Reply-To but the generator writes none")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("manifest carries an attachment or an injection")
    if record["required_indicators"] != GROUND_TRUTH["required_indicators"]:
        raise SystemExit("required_indicators do not match the manifest")
    manifest_codes = {item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]}
    rendered_codes = {item["code"] for item in GROUND_TRUTH["indicators"]}
    if manifest_codes != rendered_codes:
        raise SystemExit("indicator codes differ from the manifest: "
                         + repr(sorted(manifest_codes ^ rendered_codes)))
    if not two_sentences(LURE_SUMMARY):
        raise SystemExit("lure_summary must be exactly two sentences")
    if not two_sentences(REFERENCE_SUMMARY):
        raise SystemExit("reference_summary must be exactly two sentences")

    # The phrase pass, run here against the same lists validate_corpus.py uses.
    matched = content_matches()
    recorded = {item["code"]: item["value"] for item in GROUND_TRUTH["indicators"]
                if item["code"].startswith("content:")}
    if matched != recorded:
        raise SystemExit("content phrases in the body are " + repr(matched)
                         + " but the record says " + repr(recorded))

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
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    if str(parsed["From"]) != SENDER_DISPLAY + " <" + SENDER + ">":
        raise SystemExit("unfolded From is " + repr(str(parsed["From"])))

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
    print("updated manifest prose and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
