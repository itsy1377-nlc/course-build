#!/usr/bin/env python3
"""Regenerate 005-slatemoor-past-due-statement.

Rebuilds emails/teaching/005-slatemoor-past-due-statement.eml byte for byte
from the corpus seed and upserts the ground truth record in ground_truth.json.

Every identifier in the file that looks random is derived from the corpus seed,
so rerunning this script reproduces the same bytes:

    hex(label, n)  = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = the first n bytes of
                       sha256("<seed>|<email id>|<label>|0")
                       || sha256("<seed>|<email id>|<label>|1") || ...

    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_swk_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=stream("store-id", 16).hex(), version=4)
    DKIM bh=              = base64(stream("dkim-bh", 32))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Two derivations differ in form from the ones in gen_002 and gen_004, and both
still come out of the seed, so nothing here is pinned as an unexplained
literal:

  * The LMTP id takes its 16 bytes from the block indexed stream, that is from
    sha256("<seed>|<id>|store-id|0"), rather than from the plain digest
    sha256("<seed>|<id>|store-id"). That is the form this file was written
    with. Reproducing the committed bytes is the requirement, so the stream
    form stays; changing it would rewrite an approved file to suit a helper.
  * The DKIM bh= and b= values come from that same stream, the way gen_001 and
    gen_012 derive theirs, so the 2048 bit synthetic signature is regenerated
    rather than carried as a constant. It verifies nothing: no .example domain
    can publish a key, and the value does not depend on the body text.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox. The
recipient here is a shared mailbox rather than a distribution list, so the
message is delivered to it directly and the LMTP hop names the recipient
itself, not the reporter. The reporter appears only in
X-Sentrywick-Reported-By, because a shared mailbox is worked by several people
and the person who pressed report is not the addressee.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are all present because this message crossed the
    border gateway. All three checks pass for slatemoorsupply.example and the
    published DMARC policy is quarantine, which is the fact the week 3 lesson
    turns on: a pass names a domain, and here the domain is the supplier's own.
  * The gateway banner is inserted into both parts, because the gateway stamps
    the mail it marks as external.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 3.1 match the
    received_path_hint in the manifest. The score is nonzero because the body
    is a collections notice with money and a deadline in it, which is exactly
    the pressure the record counts.
  * Reply-To repeats the From mailbox. It is the same address, so there is no
    Reply-To mismatch to find; a real accounts receivable clerk sends from and
    reads the same mailbox.

Headers deliberately absent, matching the manifest indicator list: no
In-Reply-To and no References, so the thread is new and 016 has something to
hijack later; no X-Sentrywick-Removed-Attachment, so attachment:none holds; no
Auto-Submitted, because a person wrote this one; no X-Priority and no
Importance, because the pressure is in the words and not in a flag.

Run:  python3 corpus/tools/generators/gen_005_slatemoor_past_due_statement.py
"""

import base64
import calendar
import email
import email.policy
import hashlib
import json
import os
import time
import uuid

EMAIL_ID = "005-slatemoor-past-due-statement"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "ar@slatemoorsupply.example"
SENDER_DISPLAY = "Slatemoor Industrial Supply - Accounts Receivable"
# The envelope sender is the From mailbox. A collections clerk sends from the
# mailbox she reads, so Return-Path, From and Reply-To are one address and
# there is no envelope-versus-author split to explain.
ENVELOPE_SENDER = SENDER
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

SUBJECT = "Past due statement, account 44170: credit hold on 4/20 if unpaid"

SENDER_DOMAIN = "slatemoorsupply.example"
SENDER_HOST = "mail.slatemoorsupply.example"
SENDER_SUBMIT_HOST = "SMS-AR-02.slatemoorsupply.example"
SENDER_IP = "203.0.113.30"
SENDER_SUBMIT_IP = "192.0.2.30"
DKIM_SELECTOR = "sm2026"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The one link. Its host is the supplier's own billing portal, the fact
# url:host_allowlisted keys on, and its path is a statement path rather than a
# sign-in path, which is what separates it from the lookalike in 016.
LINK = "https://billing.slatemoorsupply.example/statements/44170"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 14:31 +0000 is the same instant as 09:31 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree.
DATE_HEADER = "Tue, 14 Apr 2026 09:31:00 -0500"
SUBMIT_STAMP = "Tue, 14 Apr 2026 14:31:03 +0000"
SUBMIT_UTC = "2026-04-14 14:31:03"
GATEWAY_STAMP = "Tue, 14 Apr 2026 09:31:06 -0500"
STORE_STAMP = "Tue, 14 Apr 2026 09:31:08 -0500"
MESSAGE_ID_STAMP = "20260414143100"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break. The HTML part here is written as short source lines,
# so only the gateway banner runs long, and it holds no space a break could
# usefully land on. The wrap is therefore a hard one at 75 characters plus the
# "=", stepping back if a break would fall inside an "=XX" escape.
QP_MAX = 76

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
    return str(uuid.UUID(hex=stream(seed, "store-id", 16).hex(), version=4))


def body_hash(seed):
    return base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")


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

# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries content:urgency_keywords on "credit hold" and
# content:payment_request on "past due", "invoice" and "remit", and those are
# the only content codes it carries, so no phrase from any other content list
# may appear in either decoded part; validate_corpus.py checks both ways.
#
#   "sign in", "log in", "password" and "credentials" are out: this notice asks
#   for money on terms already agreed and never for an identity.
#   "download" is out (content:file_share_lure), so the statement is described
#   as being on the billing portal and the link is labelled "View statement".
#   "was changed", "update your", "if you did not" and the rest of
#   content:account_change_notice are out, and the remit-to details are stated
#   as the ones already on file rather than as anything new. That is the whole
#   point of the file: a genuine collections notice changes nothing about where
#   money goes, and 016 later hijacks this same thread to change exactly that.
#   "call me", "call the number on file" and the rest of
#   content:phone_verification_offered are out. The clerk asks for a reply on
#   this message, which is the channel it arrived on, and the phone number in
#   the signature is a signature line and not an instruction.
#   "wire" and "gift card" are out (content:payment_method_unusual): the remit
#   is to a bank account the organization already pays.
#
# The deadline is stated as a dated consequence of the account terms, not as a
# countdown, so the pressure is real business pressure. That is what makes this
# the hard negative: the body alone reads malicious and the facts say benign.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

HEADING = "Account 44170: past due balance"
SALUTATION = "Hello,"

PARA_BALANCE = [
    "Two invoices on account 44170 are unpaid, and the balance is now 45",
    "days past due.",
]

# The two invoices and the total. The HTML part renders these as one paragraph
# with <br> between the lines and the total in bold, so both parts carry the
# same three lines in the same order and a part-to-part diff is empty.
INVOICE_LINES = [
    "Invoice 44170-104, dated 1/29, due 2/28: $5,118.45",
    "Invoice 44170-109, dated 1/29, due 2/28: $4,194.35",
]
TOTAL_LINE = "Total past due: $9,312.80"

PARA_TERMS = [
    "The terms on this account move it to credit hold once a balance",
    "reaches 45 days. If the full amount does not reach us by Monday 4/20,",
    "account 44170 goes on credit hold that morning, and open orders will",
    "not ship until the balance clears.",
]

# The one paragraph whose line breaks differ between the parts. The plain part
# fits it on a single 68 character line; in the HTML part the "<p>" prefix and
# the "</p>" suffix push that past the width the rest of the block wraps at, so
# the HTML copy breaks after "billing". The words are identical either way.
PARA_STATEMENT_PLAIN = [
    "The statement with copies of both invoices is on the billing portal.",
]
PARA_STATEMENT_HTML = [
    "<p>The statement with copies of both invoices is on the billing",
    "portal.</p>",
]

PARA_REMIT = [
    "Remit to Sandmarsh Community Bank, account ending 3318, and put both",
    "invoice numbers in the payment reference so we can apply the funds to",
    "the right lines.",
]

PARA_SCHEDULED = [
    "If a payment is already scheduled, reply to this message with the date",
    "and the amount and I will note it on the account.",
]

# A person's signature, not a mailbox signature: the name, the function, the
# company and the phone number the organization already has on file for this
# account. 555-0147 is inside the 555-0100 through 555-0199 fictional range.
SIGNATURE_LINES = [
    "Marisol Etxeberria",
    "Accounts Receivable",
    "Slatemoor Industrial Supply",
    "555-0147",
]

LINK_LABEL = "View statement"


def plain_part():
    lines = [BANNER_PLAIN, ""]
    lines += [HEADING, ""]
    lines += [SALUTATION, ""]
    lines += PARA_BALANCE + [""]
    lines += INVOICE_LINES + [TOTAL_LINE, ""]
    lines += PARA_TERMS + [""]
    lines += PARA_STATEMENT_PLAIN + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_REMIT + [""]
    lines += PARA_SCHEDULED + [""]
    lines += SIGNATURE_LINES
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def invoice_html():
    block = [line + "<br>" for line in INVOICE_LINES]
    block[0] = "<p>" + block[0]
    block.append("<b>" + TOTAL_LINE + "</b></p>")
    return block


def signature_html():
    block = [line + "<br>" for line in SIGNATURE_LINES[:-1]]
    block[0] = "<p>" + block[0]
    block.append(SIGNATURE_LINES[-1] + "</p>")
    return block


def html_part():
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f2f2f2;">',
        BANNER_HTML,
        '<div style="max-width:600px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#222222;">',
        '<p style="margin:0 0 18px 0;font-size:17px;font-weight:bold;',
        '  color:#5b3a1a;">' + HEADING + "</p>",
        "<p>" + SALUTATION + "</p>",
    ]
    lines += paragraph_html(PARA_BALANCE)
    lines += invoice_html()
    lines += paragraph_html(PARA_TERMS)
    lines += PARA_STATEMENT_HTML
    # The href is the same address the plain part prints, and the button text
    # is the same label, so a reader of either part can see where the link
    # goes. No image, no script, no form, no hidden text.
    lines += [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#5b3a1a;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
    ]
    lines += paragraph_html(PARA_REMIT)
    lines += paragraph_html(PARA_SCHEDULED)
    lines += signature_html()
    lines += ["</div>", "</body>", "</html>"]
    return lines


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks."""
    text = line.replace("=", "=3D")
    out = []
    while len(text) > QP_MAX:
        cut = QP_MAX - 1
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
    boundary = "=_swk_" + hexid(seed, "boundary")
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
        # own trace field. All three checks pass, and they pass for the
        # supplier's own domain, which is what makes this the benign half of
        # the week 3 pair.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=quarantine",
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 3.1",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_HOST,
        "  (" + SENDER_HOST + " [" + SENDER_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + SENDER_SUBMIT_HOST + " ([" + SENDER_SUBMIT_IP + "])",
        "  by " + SENDER_HOST + " with ESMTPSA id " + sender_id + ";",
        "  " + SUBMIT_STAMP,
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SENDER_DOMAIN + "; s=" + DKIM_SELECTOR + "; t=" + str(dkim_time()) + ";",
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
        # RFC 5322 sec. 2.2.3: the From line folds before the angle-addr, so
        # the display name and the address stay on lines of their own and the
        # unfolded value is the mailbox byte for byte.
        "From: " + SENDER_DISPLAY,
        " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Reply-To: " + SENDER,
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
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part())
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


NOTES = (
    "Key facts a correct extractor produces: from_domain "
    "slatemoorsupply.example; reply_to ar@slatemoorsupply.example, the same "
    "mailbox as From, so there is no Reply-To mismatch; display_name_mismatch "
    "false, since Slatemoor Industrial Supply - Accounts Receivable names the "
    "domain owner; spf=pass on slatemoorsupply.example, dkim=pass with "
    "d=slatemoorsupply.example s=sm2026, dmarc=pass with policy quarantine, so "
    "all three checks pass and the message is aligned; one link host, "
    "billing.slatemoorsupply.example, carrying the single link "
    "https://billing.slatemoorsupply.example/statements/44170, whose path is a "
    "statement path and not a sign-in path; no attachment header; no "
    "In-Reply-To, so the message opens a thread. Received chain: "
    "SMS-AR-02.slatemoorsupply.example [192.0.2.30] submitted with ESMTPSA to "
    "mail.slatemoorsupply.example at 14:31:03 +0000, which handed off with "
    "ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 09:31:06 -0500, "
    "delivered by LMTP to mailstore-01.pellgrave.example at 09:31:08 -0500; "
    "Date is 09:31:00 -0500, the same instant as 14:31:00 +0000 in the "
    "Message-ID. X-Sentrywick-External is yes, scan result clean, spam score "
    "3.1. Body phrases the extractor keys on, present in both parts: 'past "
    "due', 'invoice' and 'remit' (payment request), and 'credit hold' "
    "(urgency). The body names two invoices, 44170-104 for $5,118.45 and "
    "44170-109 for $4,194.35, a total of $9,312.80, a credit hold on Monday "
    "4/20, and the remit-to details already on file at Sandmarsh Community "
    "Bank, account ending 3318. It never asks for a credential, a bank change "
    "or a payment timing change, so none of those content codes apply, and "
    "recipient:prior_similar_report does not apply either: a plain payment "
    "request implies no campaign tag under prior_similar_report_rule. "
    "Difficulty reason: the tier rule counts one decisive benign fact (an "
    "allowlisted, dmarc=pass sender) against two pressure facts (urgency "
    "keywords and a payment request), so pressure exceeds decisive and the base "
    "tier is hard; the body-only read is malicious, the opposite of the "
    "verdict, which adds a step and stays capped at hard. No injection. For the "
    "instructor: this is the benign half of the week 3 pair with 025, and "
    "grounding has to move it in the opposite direction. Ungrounded, the "
    "urgency and the money read as phishing. Grounded, the facts answer: "
    "check_sender_reputation returns trusted for slatemoorsupply.example, first "
    "seen 2022-06-14, with 2 prior reports both closed benign, and check_urls "
    "returns allowlisted for billing.slatemoorsupply.example. Playbook rules 1 "
    "and 7 close it. Nothing in the body states either tool result, so the loop "
    "has to fetch them. Week 5 use: this is the stop-early case. The agent "
    "calls check_sender_reputation, learns the sender is trusted, calls "
    "check_urls on the one host, learns it is allowlisted, and stops after two "
    "steps with stop_reason decisive_benign; a third call is wasted tokens. The "
    "verdict is benign and escalate_expected is false, because the message asks "
    "for payment on terms already agreed and changes nothing about how or where "
    "money moves. Full credit on the indicators criterion needs "
    "sender:allowlisted_domain and url:host_allowlisted. Story context: this is "
    "the real collections notice behind account 44170. AP's reply promising the "
    "4/24 run is in known_threads.json, 019 is the CFO asking to move that "
    "payment before the 4/20 hold, and 016 later hijacks the same thread with a "
    "lookalike Reply-To and a bank change. Grading note: a student who calls "
    "this malicious because it is urgent has skipped the tools, and a student "
    "who treats a vendor link as suspicious without running check_urls has "
    "skipped rule 7."
)

REFERENCE_SUMMARY = (
    "This is a real collections notice from Slatemoor about two overdue "
    "invoices, and the bank details in it match our records. Please pass it to "
    "accounts payable to pay as usual; nothing about it is a scam."
)


GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [3, 5],
    "date": "2026-04-14T09:31:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "hard",
    "body_only_read": "malicious",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": SENDER,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass",
             "dmarc_policy": "quarantine"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=slatemoorsupply.example; dkim=pass "
                   "header.d=slatemoorsupply.example header.s=sm2026 "
                   "header.i=@slatemoorsupply.example; dmarc=pass "
                   "header.from=slatemoorsupply.example policy.dmarc=quarantine")},
        {"code": "sender:allowlisted_domain", "where": "check_sender_reputation",
         "value": SENDER_DOMAIN},
        {"code": "url:host_allowlisted", "where": "check_urls",
         "value": "billing.slatemoorsupply.example"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "credit hold"},
        {"code": "content:payment_request", "where": "body",
         "value": "past due; invoice; remit"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": RECIPIENT},
        {"code": "recipient:shared_mailbox", "where": "lookup_recipient",
         "value": RECIPIENT},
    ],
    "required_indicators": ["sender:allowlisted_domain", "url:host_allowlisted"],
    "url_hosts": ["billing.slatemoorsupply.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "trusted",
            "first_seen": "2022-06-14",
            "messages_90d": 96,
            "prior_reports": 2,
            "last_report_verdict": "benign",
            "last_report_date": "2026-04-02",
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Parts supplier; allowlisted.",
            "match_level": "domain",
        },
        "check_urls": {"billing.slatemoorsupply.example": "allowlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Accounts Payable Shared Mailbox",
            "role": "shared mailbox",
            "mailbox_type": "shared",
            "executive": False,
            "handles_payments": True,
            "chronic_reporter": False,
            "report_count_90d": 3,
            "true_positive_count_90d": 3,
            "campaign_tags": ["invoice-malware", "vendor-invoice-fraud"],
        },
    },
    "expected_loop": {"tools": ["check_sender_reputation", "check_urls"],
                      "stop_reason": "decisive_benign"},
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_benign_reply_to_reporter",
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
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["url_hosts"] != GROUND_TRUTH["url_hosts"]:
        raise SystemExit("url_hosts do not match the manifest")

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
    print("upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
