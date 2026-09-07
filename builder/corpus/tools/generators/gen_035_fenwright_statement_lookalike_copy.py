#!/usr/bin/env python3
"""Regenerate 035-fenwright-statement-lookalike-copy.

Rebuilds emails/batch/035-fenwright-statement-lookalike-copy.eml byte for byte
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
The course reads the gateway's Authentication-Results verdict instead.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox, not
of the path the message arrived on. t.nkemelu@pellgrave.example lives on
mailstore-01.

What this email is. It is a word for word copy of 017, the genuine Fenwright
Payroll statement notice, aimed at a second employee twenty two minutes after
the real notice went out, with one byte level difference that matters: the
sender and the link sit on fenwrightpay-notices.example, an added word
lookalike the attacker registered on 2026-04-13 and the payroll vendor does
not own. He owns it, so he publishes SPF and DKIM for it and collects
spf=pass, dkim=pass and dmarc=pass, exactly as the attacker behind 001 does
on his own lookalike. Nothing in the prose is a tell, which is the point: the
body_only_read is benign and the record is false-negative bait.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are present because the message crossed the border
    gateway. All three checks pass, and they pass for
    fenwrightpay-notices.example, whose published DMARC policy is none, which
    is what domain_policy.json records for an attacker owned domain.
  * Auto-Submitted: auto-generated, copied from the real notice along with the
    rest of it (RFC 3834 sec. 5). It sits with the author's client headers,
    below Message-ID, the same place 017 puts it.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 2.1 match the
    received_path_hint. The score is a little above 017's 1.8 and still far
    below any threshold: the gateway has nothing to hold against a polite
    notice from a domain that authenticates.
  * The gateway banner is inserted into both parts, because the gateway stamps
    the mail it marks as external.
  * The MIME boundary prefix is =_part_, the neutral prefix the corpus gives a
    third party platform that composes its own mail. A copy that reproduces
    the notice down to its footer reproduces its boundary prefix too, and
    =_swk_ stays reserved for the messages the Sentrywick stack composes.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because reply_to is null in the record and the copy keeps the real
notice's single mailbox; no In-Reply-To and no References, so thread:new
holds; no X-Sentrywick-Removed-Attachment, so attachment:none holds; no
X-Priority and no Importance, because the real notice applies no pressure and
neither does the copy.

One deliberate departure from a literal reading of body_brief. The brief says
to reproduce 017's body exactly and that nothing else differs, which is about
the wording; the greeting is a per recipient field, not wording. 017 greets
"Hello Hollis," because it was addressed to Hollis Quintanilla, and this copy
greets "Hello Tobias," because it was addressed to Tobias Nkemelu. A copy that
greeted the wrong employee would be a body level tell, and the record says
body_only_read is benign and that nothing in the body is unusual, so the name
follows the recipient. The wording, the sentence order, the link label and the
footer are 017's, byte for byte, and the generator proves it against the
constants below.

Run:  python3 corpus/tools/generators/gen_035_fenwright_statement_lookalike_copy.py
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

EMAIL_ID = "035-fenwright-statement-lookalike-copy"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "notifications@fenwrightpay-notices.example"
SENDER_DISPLAY = "Fenwright Payroll"
# The envelope sender is the From mailbox, the way the real notice does it.
# Return-Path, smtp.mailfrom and From are one address, so there is no envelope
# versus author split for a student to chase and no Reply-To to compare: every
# fact that settles this message is the domain itself.
ENVELOPE_SENDER = SENDER
RECIPIENT = "t.nkemelu@pellgrave.example"
RECIPIENT_DISPLAY = "Tobias Nkemelu"
RECIPIENT_FIRST_NAME = "Tobias"
REPORTER = "t.nkemelu@pellgrave.example"

SUBJECT = "Your pay statement for 4/17/2026 is available"

# The added word lookalike. fenwrightpay.example is the payroll vendor;
# fenwrightpay-notices.example is a different registration that merely reads
# like a subdomain of it, and sender_reputation.json first saw it on
# 2026-04-13, four days before this message.
SENDER_DOMAIN = "fenwrightpay-notices.example"
IMITATED_DOMAIN = "fenwrightpay.example"
SENDER_HOST = "mail.fenwrightpay-notices.example"
SENDER_SUBMIT_HOST = "WEB-CLIENT-4.fenwrightpay-notices.example"
SENDER_IP = "203.0.113.167"
SENDER_SUBMIT_IP = "192.0.2.167"
# domain_policy.json gives this domain the selector k1, the same selector the
# attacker behind 001 publishes on his own lookalike.
DKIM_SELECTOR = "k1"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The one link. Its host is the lookalike, and its path is the real notice's
# statement path: /statements, not a sign-in path. The sign-in ask is in the
# sentence beside the link, exactly where 017 puts it, so a reader comparing
# the two messages finds one difference and it is the host.
LINK = "https://my.fenwrightpay-notices.example/statements"
LINK_LABEL = "View statement"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 10:52 +0000 is the same instant as 05:52 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. 05:52 local is twenty two
# minutes after the real notice at 05:30: the attacker watched the pay
# calendar and sent his copy into the same hour, before the branch opens and
# while the genuine notice is still the newest thing in the mailbox.
DATE_HEADER = "Fri, 17 Apr 2026 05:52:00 -0500"
SUBMIT_STAMP = "Fri, 17 Apr 2026 10:52:02 +0000"
SUBMIT_UTC = "2026-04-17 10:52:02"
GATEWAY_STAMP = "Fri, 17 Apr 2026 05:52:05 -0500"
STORE_STAMP = "Fri, 17 Apr 2026 05:52:07 -0500"
MESSAGE_ID_STAMP = "20260417105200"

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
# This is 017's body. The manifest's body_brief asks for the vendor's notice
# word for word, including the footer, with the link pointed at the lookalike
# host and nothing else changed, and that is what these constants hold: the
# same masthead, the same lead sentence, the same statement paragraph, the same
# sign-in sentence, the same link label, the same paragraph about who owns
# which half of the payroll relationship, and the same automated-message
# footer. The greeting carries the recipient's first name, as it does in 017.
#
# Wording rules the text obeys, all from spec/enums.json content_phrases. The
# record carries exactly one content code, content:credential_request, matched
# on "sign in", so no phrase from any other content list may appear in either
# decoded part; validate_corpus.py checks that both ways. The real notice was
# already written that way and the copy inherits it:
#
#   "download" is out (content:file_share_lure). The statement is described as
#   posted in the portal and the link is labelled "View statement".
#   "action required", "today", "within 24 hours" and the rest of
#   content:urgency_keywords are out. The manifest says not to add urgency
#   words the real notice lacks, and this is the reason the instruction
#   matters: the pressure a phish usually supplies is what a reader looks for,
#   so leaving it out is what makes the copy dangerous.
#   "invoice", "past due" and "remit" are out (content:payment_request).
#   "was changed" and "if you did not" are out
#   (content:account_change_notice). Nothing claims a change, so there is no
#   undo link to click, which is the shape 021 uses.
#   "confidential" is out (content:secrecy_request).
#   "w-2" and "employee list" are out (content:data_request).
#   "reply by email" is out (content:channel_restriction). The notice names
#   the Pellgrave payroll office as the place questions go, which is a real
#   channel and not a restriction on one, and pointing the reader at his own
#   employer is the line most likely to get the message believed.
#
# The footer carries the word "automated", which is on the
# content:instruction_to_ai list. That list is in PHRASE_PASS_SKIP in
# validate_corpus.py because it holds single words that ordinary mail uses.
# The code means text that addresses an automated reader and states a verdict.
# This footer states that the message itself is automated, which is what an
# honest system notice says and what a copy of one repeats, so the record
# carries no injection and no instruction_to_ai indicator.
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
GREETING = "Hello " + RECIPIENT_FIRST_NAME + ","

# The subject, repeated as the opening sentence, the way a transactional
# notice repeats itself so the message reads the same in a preview pane and in
# the body. 017's lead sentence, unchanged.
LEAD = ["Your pay statement for 4/17/2026 is available."]

# 017's checkable reference, copied along with everything else: the pay period
# and the sequence number of the run. 4/17/2026 is the eighth biweekly Friday
# of 2026 and the period that ends 4/11 is the fourteen days before it, so the
# numbers agree with the corpus calendar. They agree because the attacker took
# them from a real notice, which is why a student who checks them learns
# nothing.
PARA_STATEMENT = [
    "Statement 2026-08 covers the pay period from 3/29/2026 through",
    "4/11/2026. It is posted in the employee portal and stays there with",
    "your earlier statements.",
]

# The ask, and the only content code in the record. It names the account the
# reader already has rather than any credential, and nothing is typed into the
# message; what the reader types goes into whatever stands behind the link.
PARA_SIGN_IN = [
    "To open it, sign in to the portal with the same employee account you",
    "use for time entry.",
]

# Who owns which half of the payroll relationship. In 017 it is the small true
# irregularity a real vendor notice carries. Copied here it is the strongest
# line in the lure, because it points the reader at a human channel inside his
# own company and so reads as a message with nothing to hide.
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

# The wording copied from 017, written out here as literal strings rather than
# assembled from the constants above. These are the sentences the manifest
# calls the reference copy, so the check below is a real comparison against
# 017's rendered text and not a tautology: if an edit here changed a word, the
# generator would stop rather than ship a copy that is not a copy.
COPIED_PHRASES = [
    "Fenwright Payroll",
    "Your pay statement for 4/17/2026 is available.",
    "Statement 2026-08 covers the pay period from 3/29/2026 through 4/11/2026. "
    "It is posted in the employee portal and stays there with your earlier "
    "statements.",
    "To open it, sign in to the portal with the same employee account you use "
    "for time entry.",
    "Questions about a figure on the statement go to the Pellgrave payroll "
    "office. Fenwright keeps the records; Pellgrave sets the hours, the rates "
    "and the deductions.",
    "Fenwright Payroll on behalf of Pellgrave Mechanical Group. This is an "
    "automated message.",
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
        # same link with the same name. The copy hides nothing in the HTML,
        # because a mismatch between the label and the href is the one tell a
        # careful reader of the body could still catch, and this message is
        # built to give him none. No image, no script, no form, no hidden text.
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
        # own trace field. All three checks pass, and they pass for the domain
        # the attacker registered, which is the whole lesson: authentication
        # proves the mail came from the domain it names, not that the name is
        # the vendor's.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=none",
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 2.1",
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
        # RFC 3834 sec. 5. The real notice carries this because a batch job
        # sent it; the copy carries it because the copy carries everything.
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
            raise SystemExit("plain part lost 017's wording: " + phrase)
        if phrase not in " ".join(html_text.split()):
            raise SystemExit("html part lost 017's wording: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if LINK not in plain_text or 'href="' + LINK + '"' not in html_text:
        raise SystemExit("the one link must appear in both parts")
    if IMITATED_DOMAIN + "/" in plain_text or "@" + IMITATED_DOMAIN in plain_text:
        raise SystemExit("the body must never use the real vendor domain")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

LURE_SUMMARY = (
    "Matches the real payroll vendor's statement notice word for word, "
    "including the footer, with a sign-in link on the lookalike domain. "
    "Nothing in the body is unusual, and the recipient gets this exact notice "
    "every pay period."
)

BODY_BRIEF = (
    "017's body, reproduced word for word with one host changed. Under a "
    "Fenwright Payroll masthead, greeted to the recipient by first name: "
    "'Your pay statement for 4/17/2026 is available.', then 'Statement "
    "2026-08 covers the pay period from 3/29/2026 through 4/11/2026. It is "
    "posted in the employee portal and stays there with your earlier "
    "statements.', then the one ask, 'To open it, sign in to the portal with "
    "the same employee account you use for time entry.' One link, labeled "
    "'View statement', pointing at "
    "https://my.fenwrightpay-notices.example/statements instead of the real "
    "portal. Then 017's paragraph on who owns which half of the payroll "
    "relationship, and 017's footer: 'Fenwright Payroll on behalf of "
    "Pellgrave Mechanical Group. This is an automated message.' No deadline, "
    "no warning, no attachment, and no urgency word the real notice lacks. "
    "The only content phrase in the body is 'sign in', and the only "
    "difference from the genuine notice is the link host."
)

MANIFEST_NOTES = (
    "False-negative bait; pairs with 017, the genuine notice, and with 050. "
    "The deciding facts are the exact-domain check against the vendor record "
    "and the new-domain flag. Auto-contain. Rendered: From is Fenwright "
    "Payroll over fenwrightpay-notices.example, an added-word lookalike of "
    "the vendor's fenwrightpay.example that display_names.json puts on the "
    "vendor domain alone, so the display-name check reports "
    "sender:display_name_claims_vendor; the attacker owns the lookalike, so "
    "spf, dkim and dmarc all pass for it with policy.dmarc=none, the policy "
    "domain_policy.json publishes for that domain, and the DKIM selector is "
    "k1; the one link host is my.fenwrightpay-notices.example, which is in "
    "url_unlisted.json and on neither list; Auto-Submitted: auto-generated "
    "was copied from the real notice with the rest of it; scan result clean "
    "and spam score 2.1. The message lands at 05:52, twenty two minutes after "
    "017 goes out at 05:30, and reaches a second employee, so the two notices "
    "sit in different mailboxes on the same morning. url:login_path is "
    "carried by the link text rather than by the path, exactly as in 017: the "
    "path is /statements and the sentence beside it asks the reader to sign "
    "in. The body carries no urgency phrase, because adding one is the single "
    "change that would give the game away."
)

# ------------------------------------------------------------- ground truth

NOTES = (
    "The batch set's false negative. Key facts a correct extractor produces: "
    "from_domain fenwrightpay-notices.example, an added-word lookalike of the "
    "payroll vendor's fenwrightpay.example, registered and first seen on "
    "2026-04-13; no Reply-To, so there is no Reply-To mismatch to find; "
    "display_name_mismatch true once display_names.json is consulted, because "
    "that file puts the name Fenwright Payroll on fenwrightpay.example alone "
    "and this From domain is not it, which is the single byte-level "
    "difference from 017; spf=pass on fenwrightpay-notices.example, dkim=pass "
    "with d=fenwrightpay-notices.example s=k1, dmarc=pass with policy none, "
    "so all three checks pass and the message is aligned to the attacker's "
    "own domain; one link host, my.fenwrightpay-notices.example, carrying the "
    "single link https://my.fenwrightpay-notices.example/statements; no "
    "attachment header; no In-Reply-To, so the message opens a thread. "
    "Received chain: WEB-CLIENT-4.fenwrightpay-notices.example [192.0.2.167] "
    "submitted with ESMTPSA to mail.fenwrightpay-notices.example at 10:52:02 "
    "+0000, which handed off with ESMTPS and TLS1_3 to mx.pellgrave.example "
    "[10.20.4.10] at 05:52:05 -0500, delivered by LMTP to "
    "mailstore-01.pellgrave.example at 05:52:07 -0500; Date is 05:52:00 "
    "-0500, the same instant as 10:52:00 +0000 in the Message-ID. "
    "X-Sentrywick-External is yes, scan result clean, spam score 2.1, and "
    "Auto-Submitted is auto-generated, which is header:auto_submitted; the "
    "attacker copied that header along with the body, so it argues for "
    "nothing. Body content: the body is 017's, word for word, including the "
    "statement number, the pay period, the link label and the "
    "automated-message footer, with the greeting carrying this recipient's "
    "first name and the link pointed at the lookalike host. The one content "
    "phrase is 'sign in', so content:credential_request is the only content "
    "indicator; no urgency, payment, payment-change, data, file-share, "
    "secrecy or account-change phrase appears, and none was added, because "
    "the absence of pressure is what makes the copy work. url:login_path is "
    "recorded on the link text rather than on the path, the same way 017 "
    "records it: the vocabulary entry reads 'a link path or text asks for a "
    "sign-in', the path here is /statements, and the sentence beside the link "
    "asks the reader to sign in to the portal. The footer says the message is "
    "automated, which is the honest wording of the notice it copies; the word "
    "alone is not an instruction to a model, so there is no injection object "
    "and no content:instruction_to_ai. Difficulty reason: three decisive "
    "facts (the lookalike From domain, the display name claiming the payroll "
    "vendor, the lookalike link host) and no pressure against them, so the "
    "base tier is easy; there is no injection, and the body-only read is "
    "benign, the opposite of the verdict, which adds one step and makes the "
    "tier medium. body_only_read is benign because the body alone is a "
    "correct payroll notice: every sentence in it was written by the real "
    "vendor, the numbers check out against the pay calendar, and nothing in "
    "the prose can settle the case. Week 7 use: this is the message a student "
    "who grades on tone gets wrong. check_sender_reputation returns unknown "
    "for fenwrightpay-notices.example, first seen 2026-04-13, one message in "
    "90 days, no prior reports and new_domain true, and check_urls returns "
    "unlisted for my.fenwrightpay-notices.example, so neither tool answers "
    "decisively on its own; the bounded loop runs all three and ends with "
    "none left to try, and lookup_recipient adds that the mailbox belongs to "
    "the Payroll and Benefits Coordinator, who handles payments. The deciding "
    "step is the comparison a tool does not make for you: the vendor record "
    "in sender_reputation.json is fenwrightpay.example, this domain is a "
    "different registration, and it is four days old. "
    "recipient:prior_similar_report does not apply: a credential ask maps to "
    "no campaign tag under prior_similar_report_rule, and the sender record "
    "carries none, so his earlier credential-phish report is the ordinary "
    "state of a mailbox. escalate_expected is false and the action is "
    "block_and_purge: block the URL host, purge copies, reply to the "
    "reporter. Full credit on the indicators criterion needs "
    "sender:lookalike_domain and url:lookalike_host. Story context: 017 "
    "reached Hollis Quintanilla at 05:30 that morning and this copy reached "
    "Tobias Nkemelu at 05:52; 001 ran the same lure from a different "
    "lookalike four days earlier, and 050 is the genuine deposit-change "
    "confirmation the exam contrasts with both. Grading note: a student who "
    "calls this benign has read the body and skipped the domain check, and a "
    "student who calls it malicious because it says 'sign in' reached the "
    "right answer for 017's reason rather than this one. Rendering notes: the "
    "plain part is 7bit with hard wraps under 78 characters and the HTML part "
    "is quoted-printable, because the fixed gateway banner snippet is longer "
    "than 78 characters; the banner is the first line of the plain part and "
    "the first line after the body tag in the HTML part; both parts carry the "
    "same words in the same order and the HTML part hides nothing, so there "
    "is no content:html_hidden_text, and the button label matches the href. "
    "The MIME boundary prefix is =_part_, the prefix the corpus gives a third "
    "party platform that composes its own mail, and a copy of a platform "
    "notice copies that too. There is no X-Originating-IP: the sender is the "
    "attacker's own mail server rather than a webmail provider, so the "
    "submitting client's address 192.0.2.167 appears in the bottom Received "
    "line instead. Every identifier that looks random is derived from a "
    "SHA-256 over the corpus seed, the email id and a label, so the file "
    "regenerates byte for byte."
)

REFERENCE_SUMMARY = (
    "This looks exactly like the real Fenwright notice, but the sender and "
    "the link use a domain registered four days ago that Fenwright does not "
    "own. Your real statement is in the portal as usual; this copy has been "
    "blocked."
)

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=fenwrightpay-notices.example; dkim=pass "
    "header.d=fenwrightpay-notices.example header.s=k1 "
    "header.i=@fenwrightpay-notices.example; dmarc=pass "
    "header.from=fenwrightpay-notices.example policy.dmarc=none"
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-17T05:52:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "medium",
    "body_only_read": "benign",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass",
             "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": AUTH_VALUE},
        {"code": "sender:lookalike_domain", "where": "From",
         "value": IMITATED_DOMAIN},
        {"code": "sender:display_name_claims_vendor", "where": "From",
         "value": SENDER_DISPLAY},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-13"},
        {"code": "url:lookalike_host", "where": "body",
         "value": "my.fenwrightpay-notices.example"},
        {"code": "url:host_unlisted", "where": "check_urls",
         "value": "my.fenwrightpay-notices.example"},
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
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": RECIPIENT},
    ],
    "required_indicators": ["sender:lookalike_domain", "url:lookalike_host"],
    "url_hosts": ["my.fenwrightpay-notices.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "unknown",
            "first_seen": "2026-04-13",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "Registered and first seen four days before its lure.",
            "match_level": "domain",
        },
        "check_urls": {"my.fenwrightpay-notices.example": "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Tobias Nkemelu",
            "role": "Payroll and Benefits Coordinator",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": True,
            "chronic_reporter": False,
            "report_count_90d": 5,
            "true_positive_count_90d": 3,
            "campaign_tags": ["benefits-notice", "credential-phish",
                              "direct-deposit-change", "payroll-notice"],
        },
    },
    # No tool answers decisively on its own: the reputation record is unknown
    # rather than known_bad and the link host is unlisted rather than
    # blocklisted, so the bounded loop runs all three tools and ends because
    # there is none left to try, not because it hit the cap.
    "expected_loop": {"tools": ["check_sender_reputation", "check_urls",
                                "lookup_recipient"],
                      "stop_reason": "tools_exhausted"},
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "block_and_purge",
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
                         ("weeks", GROUND_TRUTH["weeks"]),
                         ("date", GROUND_TRUTH["date"]),
                         ("verdict", GROUND_TRUTH["verdict"]),
                         ("category", GROUND_TRUTH["category"]),
                         ("difficulty", GROUND_TRUTH["difficulty"]),
                         ("body_only_read", GROUND_TRUTH["body_only_read"]),
                         ("arrival_path", GROUND_TRUTH["arrival_path"]),
                         ("recommended_action", GROUND_TRUTH["recommended_action"]),
                         ("escalate_expected", GROUND_TRUTH["escalate_expected"]),
                         ("escalation_reasons", GROUND_TRUTH["escalation_reasons"]),
                         ("required_indicators", GROUND_TRUTH["required_indicators"])):
        if record.get(field) != value:
            raise SystemExit("manifest " + field + " is " + repr(record.get(field))
                             + " but the generator renders " + repr(value))
    for method in ("spf", "dkim", "dmarc"):
        if record["auth"][method] != GROUND_TRUTH["auth"][method]:
            raise SystemExit("manifest auth." + method + " does not match the generator")
    if record["url_hosts"] != GROUND_TRUTH["url_hosts"]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("manifest carries a Reply-To but the generator writes none")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("manifest carries an attachment or an injection")
    if record["tool_expectations"] != GROUND_TRUTH["tool_expectations"]:
        raise SystemExit("tool_expectations differ from the manifest")
    if record["expected_loop"] != GROUND_TRUTH["expected_loop"]:
        raise SystemExit("expected_loop differs from the manifest")
    if record["reference_summary"] != REFERENCE_SUMMARY:
        raise SystemExit("reference_summary differs from the manifest")
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
