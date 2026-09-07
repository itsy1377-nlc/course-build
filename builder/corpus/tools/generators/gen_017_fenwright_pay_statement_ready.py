#!/usr/bin/env python3
"""Regenerate 017-fenwright-pay-statement-ready.

Rebuilds emails/teaching/017-fenwright-pay-statement-ready.eml byte for byte
from the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

Every identifier in the file that looks random is derived from the corpus seed,
so rerunning this script reproduces the same bytes:

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
bytes for a 2048 bit signature, which one digest cannot supply, so that one
value comes from the block indexed stream. Neither verifies: no .example
domain can publish a DKIM key, and no lab in the course checks a signature.
The course reads the gateway's Authentication-Results verdict instead, which
is what RFC 9989 sec. 5.3.6 asks a receiver to write.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox, not
of the path the message arrived on. h.quintanilla@pellgrave.example lives on
mailstore-01, the same store that delivered 001 and 012 to him.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are present because the message crossed the border
    gateway. All three checks pass, and they pass for fenwrightpay.example,
    the payroll vendor's own domain, whose published DMARC policy is reject.
    That is the whole point of the week 3 pair: 001 also collects three
    passes, and the difference is which domain they name.
  * Auto-Submitted: auto-generated, because a batch job on the payroll
    platform sent this, not a person (RFC 3834 sec. 5). It sits with the
    author's client headers, below Message-ID, the same place 002 puts it.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 1.8 match the
    received_path_hint. The score is low because the notice asks for nothing
    but a click on the vendor's own portal.
  * The gateway banner is inserted into both parts, because the gateway stamps
    the mail it marks as external.
  * The MIME boundary prefix is =_part_, the neutral prefix the corpus gives a
    third party platform that composes its own mail: =_swk_ belongs to the
    messages the Sentrywick stack composes, and 007 and 013, the other two
    vendor platform notices, already use =_part_.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because reply_to is null in the record and the platform bounces to
the mailbox it sends from; no In-Reply-To and no References, so thread:new
holds; no X-Sentrywick-Removed-Attachment, so attachment:none holds; no
X-Priority and no Importance, because a real statement notice applies no
pressure, and 001's X-Priority: 1 is one of the things that separates the two.

Run:  python3 corpus/tools/generators/gen_017_fenwright_pay_statement_ready.py
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

EMAIL_ID = "017-fenwright-pay-statement-ready"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "notifications@fenwrightpay.example"
SENDER_DISPLAY = "Fenwright Payroll"
# The envelope sender is the From mailbox. The platform bounces to the same
# mailbox it sends from, so Return-Path, smtp.mailfrom and From are one
# address and there is no envelope versus author split for a student to chase.
ENVELOPE_SENDER = SENDER
RECIPIENT = "h.quintanilla@pellgrave.example"
RECIPIENT_DISPLAY = "Hollis Quintanilla"
REPORTER = "h.quintanilla@pellgrave.example"

SUBJECT = "Your pay statement for 4/17/2026 is available"

SENDER_DOMAIN = "fenwrightpay.example"
SENDER_HOST = "smtp-out.fenwrightpay.example"
SENDER_SUBMIT_HOST = "payroll-app-02.fenwrightpay.example"
SENDER_IP = "203.0.113.12"
SENDER_SUBMIT_IP = "192.0.2.12"
DKIM_SELECTOR = "fw1"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"
ORG_DISPLAY = "Pellgrave Mechanical Group"

# The one link. Its host is the payroll vendor's employee portal, which is the
# host on url_allowlist.json that url:host_allowlisted keys on, and its path is
# a statement path. 001 aims the same familiar name at
# my.fenwrightpay.example.secure-verify-login.example/account/login, so the
# pair differs in the host and in the path at once.
LINK = "https://my.fenwrightpay.example/statements"
LINK_LABEL = "View statement"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 10:30 +0000 is the same instant as 05:30 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. 05:30 local is the hour a
# payroll batch runs: the statements post before the branch opens.
DATE_HEADER = "Fri, 17 Apr 2026 05:30:00 -0500"
SUBMIT_STAMP = "Fri, 17 Apr 2026 10:30:02 +0000"
SUBMIT_UTC = "2026-04-17 10:30:02"
GATEWAY_STAMP = "Fri, 17 Apr 2026 05:30:05 -0500"
STORE_STAMP = "Fri, 17 Apr 2026 05:30:07 -0500"
MESSAGE_ID_STAMP = "20260417103000"

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
# record carries exactly one content code, content:credential_request, matched
# on "sign in", so no phrase from any other content list may appear in either
# decoded part; validate_corpus.py checks that both ways.
#
#   "download" is out (content:file_share_lure). A real statement notice would
#   say it, so the text says the statement is posted in the portal and the
#   link is labelled "View statement" instead. That costs nothing: the reader
#   still knows what the link does.
#   "today", "this morning", "by friday", "action required" and the rest of
#   content:urgency_keywords are out. The manifest says no deadline and no
#   warning, and a genuine statement notice has neither: the money has already
#   moved and the statement is not going anywhere.
#   "invoice", "past due", "remit" and "amount due" are out
#   (content:payment_request). This notice asks for no money.
#   "if you did not" and "was changed" are out
#   (content:account_change_notice). Nothing was changed, so the notice makes
#   no change claim and offers no undo link, which is the shape 021 uses.
#   "confidential" is out (content:secrecy_request), even though a real
#   payroll footer often carries it.
#   "w-2" and "employee list" are out (content:data_request). Nothing is asked
#   for.
#   "reply by email" is out (content:channel_restriction). The notice names
#   the Pellgrave payroll office as the place questions go, which is a real
#   channel and not a restriction on one.
#
# The footer does carry the word "automated", which is on the
# content:instruction_to_ai list. That list is in PHRASE_PASS_SKIP in
# validate_corpus.py because it holds single words that ordinary mail uses,
# and this footer is the reason the exception exists: an honest system notice
# says it is automated. The code means text that addresses an automated reader
# and states a verdict, which 013 does and this message does not, so the
# record carries no injection and no instruction_to_ai indicator.
#
# Line breaks in both parts are placed so that "sign in" and "View statement"
# each sit whole on one line, because the week 3 extractor matches phrases
# inside a part and a break between "sign" and "in" would hide the one content
# fact this record claims.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

MASTHEAD = "Fenwright Payroll"
GREETING = "Hello Hollis,"

# The subject, repeated as the opening sentence, the way a transactional
# notice repeats itself so the message reads the same in a preview pane and in
# the body. 035 reproduces this sentence word for word.
LEAD = ["Your pay statement for 4/17/2026 is available."]

# The checkable reference every legitimate message in the teaching set
# carries, in the form a payroll platform uses: the pay period and the
# sequence number of the run. 4/17/2026 is the eighth biweekly Friday of 2026,
# counting from 1/9, and the period that ends 4/11 is the fourteen days before
# it, so the three numbers agree with each other and with the corpus calendar.
PARA_STATEMENT = [
    "Statement 2026-08 covers the pay period from 3/29/2026 through",
    "4/11/2026. It is posted in the employee portal and stays there with",
    "your earlier statements.",
]

# The one pressure fact in the message, and the only reason the tier is medium
# rather than easy: a benign notice from an allowlisted sender still asks the
# reader to sign in. The ask names the account the reader already has rather
# than any credential, and nothing is typed into this message.
PARA_SIGN_IN = [
    "To open it, sign in to the portal with the same employee account you",
    "use for time entry.",
]

# Who owns which half of the payroll relationship. It is the small true
# irregularity a real vendor notice carries, and it points the reader at a
# human channel inside her own company without arguing that the message is
# safe. A body that argued its own innocence would hand a small model the
# confident read the pair with 001 exists to withhold.
PARA_QUESTIONS = [
    "Questions about a figure on the statement go to the Pellgrave payroll",
    "office. Fenwright keeps the records; Pellgrave sets the hours, the",
    "rates and the deductions.",
]

FOOTER = [
    "Fenwright Payroll on behalf of Pellgrave Mechanical Group. This is an",
    "automated message.",
]

# Phrases the week 3 extractor keys on. validate_corpus.py searches the
# decoded parts without normalizing white space, so each of these has to sit
# whole on one line of each part; the generator proves it.
LINE_SAFE_PHRASES = [
    "sign in",
    "Your pay statement for 4/17/2026 is available",
    LINK_LABEL,
]

# Wording 035 reproduces. These run past one line, so they are checked against
# the white space normalized text of each part rather than line by line.
COPIED_PHRASES = [
    "Fenwright Payroll on behalf of Pellgrave Mechanical Group. This is an "
    "automated message.",
    "sign in to the portal with the same employee account you use for time "
    "entry.",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", MASTHEAD, "", GREETING, ""]
    lines += LEAD + [""]
    lines += PARA_STATEMENT + [""]
    lines += PARA_SIGN_IN + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_QUESTIONS + [""]
    lines += FOOTER
    return lines


def html_part():
    return [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        ('<p style="margin:0 0 20px 0;font-size:20px;font-weight:bold;'
         'color:#1b4f8a;">' + MASTHEAD + "</p>"),
        "<p>" + GREETING + "</p>",
        ('<p style="font-size:17px;font-weight:bold;">' + joined(LEAD)
         + "</p>"),
        "<p>" + joined(PARA_STATEMENT) + "</p>",
        "<p>" + joined(PARA_SIGN_IN) + "</p>",
        # The href is the address the plain part prints and the button text is
        # the label the plain part prints, so a reader of either part sees the
        # same link with the same name. No image, no script, no form, no
        # hidden text.
        ('<p style="margin:24px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:12px 22px;'
         'background-color:#1b4f8a;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">' + LINK_LABEL + "</a></p>"),
        "<p>" + joined(PARA_QUESTIONS) + "</p>",
        ('<p style="margin-top:28px;padding-top:12px;'
         'border-top:1px solid #d9dee3;font-size:13px;color:#444444;">'
         + joined(FOOTER) + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


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
        # own trace field. All three checks pass, and they pass for the
        # payroll vendor's own domain, which is the fact the week 3 pair with
        # 001 turns on.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=reject",
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 1.8",
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
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # RFC 3834 sec. 5: a batch job on the payroll platform sent this, so
        # the platform marks it, and a reply to it reaches no person.
        "Auto-Submitted: auto-generated",
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
        if phrase not in plain_text:
            raise SystemExit("plain part broke the phrase across lines: " + phrase)
        if phrase not in html_text:
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
    "The real payroll vendor's automated notice that the pay statement for "
    "Friday's run can be viewed in the employee portal. It links to the "
    "portal host on the allowlist and carries the auto-generated marker."
)

BODY_BRIEF = (
    "The vendor's standard notice, greeted to Hollis under a Fenwright "
    "Payroll masthead. Open with 'Your pay statement for 4/17/2026 is "
    "available.', then name the run: 'Statement 2026-08 covers the pay period "
    "from 3/29/2026 through 4/11/2026. It is posted in the employee portal "
    "and stays there with your earlier statements.' Then the one ask: 'To "
    "open it, sign in to the portal with the same employee account you use "
    "for time entry.' One link, labeled 'View statement', to "
    "https://my.fenwrightpay.example/statements. Then who owns which half of "
    "the payroll relationship: questions about a figure go to the Pellgrave "
    "payroll office, because Fenwright keeps the records and Pellgrave sets "
    "the hours, the rates and the deductions. Footer: 'Fenwright Payroll on "
    "behalf of Pellgrave Mechanical Group. This is an automated message.' No "
    "deadline, no warning, no attachment, and no line that argues the message "
    "is safe. The word 'download' is deliberately absent, so the only content "
    "phrase in the body is 'sign in'."
)

MANIFEST_NOTES = (
    "The honest twin of 001: same recipient and same portal, arriving the "
    "morning of the pay run; the recipient reported it because 001 made him "
    "nervous. Week 3 side-by-side with 001; week 4 check_urls allowlist hit "
    "(reputation agrees, but the URL tool is the one the lab calls). "
    "content:credential_request fires on 'sign in', which is the one pressure "
    "fact against the allowlisted sender, so the tier is medium. Rendered: "
    "From is Fenwright Payroll over the vendor's own fenwrightpay.example, "
    "which display_names.json gives that name, so no display name indicator "
    "applies; spf, dkim and dmarc all pass with policy.dmarc=reject, the "
    "policy domain_policy.json publishes for the vendor; the one link host is "
    "my.fenwrightpay.example, added to url_allowlist.json on 2021-03-08; "
    "Auto-Submitted: auto-generated marks the batch job; scan result clean "
    "and spam score 1.8. url:login_path is carried by the link text rather "
    "than by the path: the path is /statements and the sentence beside it "
    "asks the reader to sign in, where 001 puts /account/login on a host that "
    "only borrows the vendor's name. 035 reproduces this body word for word "
    "against a lookalike host, so the rendered wording is the batch set's "
    "reference copy."
)

# ------------------------------------------------------------- ground truth

NOTES = (
    "The benign half of the week 3 pair with 001, and the week 4 case where "
    "the URL tool is the one that answers. Key facts a correct extractor "
    "produces: from_domain fenwrightpay.example, the payroll vendor's own "
    "domain; no Reply-To, so there is no Reply-To mismatch to find; "
    "display_name_mismatch false, because display_names.json puts the name "
    "Fenwright Payroll on fenwrightpay.example and that is the From domain, "
    "which is the single byte-level difference from 001, where the same name "
    "sits over fenwright-pay.example; spf=pass on fenwrightpay.example, "
    "dkim=pass with d=fenwrightpay.example s=fw1, dmarc=pass with policy "
    "reject, so all three checks pass and the message is aligned; one link "
    "host, my.fenwrightpay.example, carrying the single link "
    "https://my.fenwrightpay.example/statements; no attachment header; no "
    "In-Reply-To, so the message opens a thread. Received chain: "
    "payroll-app-02.fenwrightpay.example [192.0.2.12] submitted with ESMTPSA "
    "to smtp-out.fenwrightpay.example at 10:30:02 +0000, which handed off "
    "with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 05:30:05 "
    "-0500, delivered by LMTP to mailstore-01.pellgrave.example at 05:30:07 "
    "-0500; Date is 05:30:00 -0500, the same instant as 10:30:00 +0000 in the "
    "Message-ID. X-Sentrywick-External is yes, scan result clean, spam score "
    "1.8, and Auto-Submitted is auto-generated, which is header:auto_submitted. "
    "Body content: the one content phrase is 'sign in', so "
    "content:credential_request is the only content indicator; no urgency, "
    "payment, payment-change, data, file-share, secrecy or account-change "
    "phrase appears, and the word 'download' was kept out on purpose so that "
    "content:file_share_lure does not fire on a statement notice. "
    "url:login_path is recorded on the link text rather than on the path: the "
    "vocabulary entry reads 'a link path or text asks for a sign-in', the path "
    "here is /statements, and the sentence beside the link asks the reader to "
    "sign in to the portal. That is the contrast the week 3 pair needs, "
    "because 001 puts /account/login on "
    "my.fenwrightpay.example.secure-verify-login.example. The footer says the "
    "message is automated, which is the honest use of a word that also opens "
    "013's injection; the word alone is not an instruction to a model, so "
    "there is no injection object and no content:instruction_to_ai. "
    "Difficulty reason: the tier rule counts one decisive benign fact, an "
    "allowlisted sender with dmarc=pass, against one pressure fact, the "
    "credential request, so pressure equals decisive and the base tier is "
    "medium; there is no injection, and body_only_read is uncertain rather "
    "than the opposite of the verdict, so neither adjustment applies. "
    "body_only_read is uncertain because the body alone is a payroll notice "
    "that asks the reader to sign in, which is the exact shape of a "
    "credential phish: the prose cannot settle the case, and every fact that "
    "does settle it comes from a header or a tool. Week 5 use: this is the "
    "second stop-early case. check_sender_reputation returns trusted for "
    "fenwrightpay.example, first seen 2021-03-08, 212 messages in 90 days and "
    "one prior report closed benign on 2026-02-11, and check_urls returns "
    "allowlisted for my.fenwrightpay.example, so the loop stops after two "
    "steps with stop_reason decisive_benign; lookup_recipient would add "
    "nothing, because the recipient carries no flag and his prior "
    "credential-phish report is the ordinary state of a mailbox under "
    "prior_similar_report_rule. Playbook rules 1, 2 and 7 close it: the "
    "passes name a domain, the vendor's name sits over the domain the vendor "
    "owns, and the link host is on the allowlist. Nothing in the body states "
    "either tool result, so the loop has to fetch them. escalate_expected is "
    "false and the action is close_benign_reply_to_reporter: the notice moves "
    "no money, changes no bank detail and asks for no data. Full credit on "
    "the indicators criterion needs sender:allowlisted_domain and "
    "url:host_allowlisted. Story context: 001 reached this mailbox on Monday "
    "13 April and Hollis Quintanilla reported it; this is the real notice for "
    "the same pay run four days later, and he reported it too, which is why "
    "X-Sentrywick-Reported-By names him and why the reference summary tells "
    "him the check was worth making. 035 copies this body word for word onto "
    "the lookalike host my.fenwrightpay-notices.example for the week 7 batch, "
    "so the wording rendered here is the reference the batch copy is measured "
    "against. Grading note: a student who calls this malicious because it "
    "says 'sign in' has read the body and skipped the tools, and a student "
    "who runs a third tool after two decisive answers has spent a step for "
    "nothing. Rendering notes: the plain part is 7bit with hard wraps under "
    "78 characters and the HTML part is quoted-printable, because the fixed "
    "gateway banner snippet is longer than 78 characters; the banner is the "
    "first line of the plain part and the first line after the body tag in "
    "the HTML part; both parts carry the same words in the same order and the "
    "HTML part hides nothing, so there is no content:html_hidden_text. The "
    "MIME boundary prefix is =_part_, the prefix the corpus gives a third "
    "party platform that composes its own mail, the same one 007 and 013 use. "
    "There is no X-Originating-IP: the sender is a payroll platform rather "
    "than a webmail provider, so the submitting host's address 192.0.2.12 "
    "appears in the bottom Received line instead. Every identifier that looks "
    "random is derived from a SHA-256 over the corpus seed, the email id and "
    "a label, so the file regenerates byte for byte."
)

REFERENCE_SUMMARY = (
    "This is the real pay statement notice from Fenwright Payroll, sent from "
    "their own domain to the portal we use. It is safe to open, and it was "
    "smart to double-check after Monday's fake one."
)

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=fenwrightpay.example; dkim=pass "
    "header.d=fenwrightpay.example header.s=fw1 "
    "header.i=@fenwrightpay.example; dmarc=pass "
    "header.from=fenwrightpay.example policy.dmarc=reject"
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [3, 4],
    "date": "2026-04-17T05:30:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "medium",
    "body_only_read": "uncertain",
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
         "value": SENDER_DOMAIN},
        {"code": "url:host_allowlisted", "where": "check_urls",
         "value": "my.fenwrightpay.example"},
        {"code": "url:login_path", "where": "body",
         "value": "sign in to the portal"},
        {"code": "content:credential_request", "where": "body",
         "value": "sign in"},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:allowlisted_domain", "url:host_allowlisted"],
    "url_hosts": ["my.fenwrightpay.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "trusted",
            "first_seen": "2021-03-08",
            "messages_90d": 212,
            "prior_reports": 1,
            "last_report_verdict": "benign",
            "last_report_date": "2026-02-11",
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Payroll vendor; allowlisted.",
            "match_level": "domain",
        },
        "check_urls": {"my.fenwrightpay.example": "allowlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Hollis Quintanilla",
            "role": "Service Manager, Head Office Branch",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 2,
            "true_positive_count_90d": 1,
            "campaign_tags": ["credential-phish", "customer-notice"],
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
    if record["url_hosts"] != GROUND_TRUTH["url_hosts"]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("manifest carries a Reply-To but the generator writes none")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("manifest carries an attachment or an injection")
    manifest_codes = {item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]}
    rendered_codes = {item["code"] for item in GROUND_TRUTH["indicators"]}
    if manifest_codes != rendered_codes:
        raise SystemExit("indicator codes differ from the manifest: "
                         + repr(sorted(manifest_codes ^ rendered_codes)))
    if not two_sentences(LURE_SUMMARY):
        raise SystemExit("lure_summary must be exactly two sentences")

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
