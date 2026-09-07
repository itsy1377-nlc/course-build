#!/usr/bin/env python3
"""Regenerate 050-fenwright-deposit-change-confirmation.

Rebuilds builder/instructor/exam-emails/050-fenwright-deposit-change-confirmation.eml
byte for byte from the corpus seed, refreshes the prose fields of its own
manifest record in spec/corpus-spec.json, and upserts its ground truth record
in ground_truth.json. It touches no other record in either file.

This one is exam-only, so it renders into builder/instructor/exam-emails/ and
never under corpus/emails/. Nothing a student can reach holds it before the
week 8 exam. tools/validate_corpus.py warns that an exam record has no file
under emails/; that warning is correct, and tools/build_corpus.py validates the
rendered file by pointing the validator at the instructor folder with
release/ground_truth_exam.json.

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
of the path the message arrived on. c.hallowden@pellgrave.example lives on
mailstore-01.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are present because the message crossed the border
    gateway. All three checks pass, and they pass for fenwrightpay.example,
    the payroll vendor's own domain, whose published DMARC policy is reject.
    That is the whole exam question: 001 collects three passes too, and the
    difference is which domain they name.
  * Auto-Submitted: auto-generated, because the employee portal sent this when
    the change was saved, not a person (RFC 3834 sec. 5). It sits with the
    author's client headers, below Message-ID, where 017 puts it.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 2.4 match the
    received_path_hint in the manifest. The score is higher than 017's 1.8 and
    lower than a real lure's, because the notice carries an urgency word and a
    sign-in ask that a bulk scanner counts and a reputation lookup does not.
  * The sender-side hop is portal-app-04.fenwrightpay.example [192.0.2.13]
    rather than the payroll-app-02 node 017 came from. A statement notice is
    written by the payroll batch and a deposit-change confirmation is written
    by the self-service portal, so the two notices leave the vendor from
    different application nodes and meet at the same smtp-out host.
  * The MIME boundary prefix is =_part_, the neutral prefix the corpus gives a
    third party platform that composes its own mail. =_swk_ belongs to the
    messages the Sentrywick stack composes, and 017, the other Fenwright
    notice, already uses =_part_.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because reply_to is null in the record and the platform bounces to
the mailbox it sends from; no In-Reply-To and no References, so thread:new
holds; no X-Sentrywick-Removed-Attachment, so attachment:none holds; no
X-Priority and no Importance, because the pressure in this message is one word
in the body and not a flag, which is exactly what the exam asks a student to
weigh against the tools.

Run:  python3 corpus/tools/generators/gen_050_fenwright_deposit_change_confirmation.py
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

EMAIL_ID = "050-fenwright-deposit-change-confirmation"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EXAM_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EXAM_DIR, EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "notifications@fenwrightpay.example"
SENDER_DISPLAY = "Fenwright Payroll"
# The envelope sender is the From mailbox. The platform bounces to the same
# mailbox it sends from, so Return-Path, smtp.mailfrom and From are one
# address and there is no envelope versus author split for a student to chase.
ENVELOPE_SENDER = SENDER
RECIPIENT = "c.hallowden@pellgrave.example"
RECIPIENT_DISPLAY = "Casimir Hallowden"
REPORTER = "c.hallowden@pellgrave.example"

SUBJECT = "Your direct deposit account was changed"

SENDER_DOMAIN = "fenwrightpay.example"
SENDER_HOST = "smtp-out.fenwrightpay.example"
SENDER_SUBMIT_HOST = "portal-app-04.fenwrightpay.example"
SENDER_IP = "203.0.113.12"
SENDER_SUBMIT_IP = "192.0.2.13"
DKIM_SELECTOR = "fw1"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The one link. Its host is the payroll vendor's employee portal, the host on
# url_allowlist.json that url:host_allowlisted keys on, and its path is the
# account page of that portal. 001 aims the same familiar name at
# my.fenwrightpay.example.secure-verify-login.example/account/login, so the
# pair differs in the host and in the depth of the path, not in the word.
LINK = "https://my.fenwrightpay.example/account"
LINK_LABEL = "Review your account"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 21:14 +0000 is the same instant as 16:14 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. 16:14 local is three minutes
# after the change the body reports, which is how long a portal takes to hand
# a confirmation to its outbound queue.
DATE_HEADER = "Mon, 27 Apr 2026 16:14:00 -0500"
SUBMIT_STAMP = "Mon, 27 Apr 2026 21:14:02 +0000"
SUBMIT_UTC = "2026-04-27 21:14:02"
GATEWAY_STAMP = "Mon, 27 Apr 2026 16:14:05 -0500"
STORE_STAMP = "Mon, 27 Apr 2026 16:14:07 -0500"
MESSAGE_ID_STAMP = "20260427211400"

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
# record carries exactly three content codes, and the phrases that match them
# are "was changed" and "if you did not" (account change notice), "sign in"
# (credential request) and "immediately" (urgency). No phrase from any other
# content list may appear in either decoded part, and validate_corpus.py checks
# that both ways. The lists that came closest to being tripped:
#
#   "new account" and "new account number" are out
#   (content:payment_change_request). A confirmation is written from the
#   vendor's side after the fact, so it reports the account it now holds and
#   the last four digits of it rather than announcing a new one. That single
#   word is what separates this message from 021, where the attacker asks
#   payroll to move the deposit to a "new account".
#   "call me" and "call the number on file" are out
#   (content:phone_verification_offered). The line that matters says to
#   contact the payroll administrator, which is a person inside Pellgrave and
#   the right channel, and it names no number for the reader to dial back into
#   the message.
#   "download" is out (content:file_share_lure). Nothing is attached and
#   nothing is fetched; the details sit in the portal.
#   "invoice", "past due" and "remit" are out (content:payment_request), and
#   "today's run", "earlier run" and "hold the payment" are out
#   (content:payment_timing_request). This notice asks for no money and moves
#   no run.
#   "action needed" is out even though "no action is needed" says almost the
#   same thing, because the phrase list matches on the exact run of words and
#   the honest form of the sentence is the negative one.
#   "confidential" is out (content:secrecy_request), and "reply by email" is
#   out (content:channel_restriction), though a real payroll footer often
#   carries one or the other.
#
# The footer carries the word "automated", which is on the
# content:instruction_to_ai list. That list is in PHRASE_PASS_SKIP in
# validate_corpus.py because it holds single words ordinary mail uses, and an
# honest system notice saying it is automated is why the exception exists. The
# code means text that addresses an automated reader and states a verdict, and
# this footer does neither, so the record carries no injection.
#
# Line breaks in both parts are placed so that "was changed", "if you did not",
# "immediately", "sign in" and "sign in to the employee portal" each sit whole
# on one line, because the week 3 extractor matches phrases inside a decoded
# part and a break inside one would hide a fact the record claims.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

MASTHEAD = "Fenwright Payroll"
GREETING = "Hello Casimir,"

# The subject, repeated as the opening sentence with the date added, the way a
# transactional notice repeats itself so the message reads the same in a
# preview pane and in the body.
LEAD = ["Your direct deposit account was changed on 4/27/2026."]

# The checkable reference every legitimate message in the corpus carries, in
# the form a payroll platform uses: when the change was recorded, which
# deposit it lands on, the last four digits of the account now on file, and a
# confirmation number. 5/1/2026 is the next biweekly Friday after 4/17, so the
# effective date agrees with the corpus payroll calendar, and the last four
# digits are not the ones 021 tried to plant, which is the detail the exam
# stem turns on when a student compares the two.
PARA_DETAIL = [
    "The change was recorded in the employee portal at 4:11 pm Central and",
    "applies to the deposit dated 5/1/2026. The account we hold for you now",
    "ends in 2210. Your confirmation number is DD-31408.",
]

# The two sentences the manifest fixes, word for word. They are the reason the
# file is hard: read alone they are the shape of a scare, and read against the
# headers and the tools they are the shape of an honest confirmation. A real
# vendor writes them because the notice exists to catch a change the employee
# did not make.
PARA_CHECK = [
    "If you made this change, no action is needed. If you did not, contact",
    "your payroll administrator immediately.",
]

# The one credential-shaped ask, and the only reason this benign message
# carries a pressure fact at all. It names the account the reader already has
# and asks nothing to be typed into this message.
PARA_SIGN_IN = [
    "To see the details we hold for you, sign in to the employee portal with",
    "the same employee account you use for time entry.",
]

# The footer 017 renders, word for word, because both notices come off the
# same platform and a student who lines them up should find the vendor's
# boilerplate identical.
FOOTER = [
    "Fenwright Payroll on behalf of Pellgrave Mechanical Group. This is an",
    "automated message.",
]

# Phrases the week 3 extractor keys on. validate_corpus.py lowercases the
# decoded parts and searches them without normalizing white space, so each of
# these has to sit whole on one line of each part; the generator proves it
# below, matching the validator by lowercasing first.
LINE_SAFE_PHRASES = [
    "was changed",
    "if you did not",
    "immediately",
    "sign in",
    "sign in to the employee portal",
    "your direct deposit account was changed on 4/27/2026.",
    LINK_LABEL.lower(),
]

# The wording the manifest fixes and the wording 017 shares. These run past one
# line, so they are checked against the white space normalized text of each
# part rather than line by line.
FIXED_WORDING = [
    "If you made this change, no action is needed. If you did not, contact "
    "your payroll administrator immediately.",
    "Fenwright Payroll on behalf of Pellgrave Mechanical Group. This is an "
    "automated message.",
]

# Phrase lists in spec/enums.json that this body must not touch, spelled out
# here so the generator fails rather than the validator when an edit reaches
# for the obvious word.
FORBIDDEN_PHRASES = [
    "new account", "new account number", "new bank", "new routing",
    "changed banks", "updated remittance", "invoice", "past due", "remit",
    "amount due", "download", "call me", "call the number on file",
    "action required", "action needed", "today", "confidential",
    "reply by email", "wire", "earlier run", "today's run",
    "confirm your account", "confirm your direct deposit", "verify your account",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", MASTHEAD, "", GREETING, ""]
    lines += LEAD + [""]
    lines += PARA_DETAIL + [""]
    lines += PARA_CHECK + [""]
    lines += PARA_SIGN_IN + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
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
        "<p>" + joined(PARA_DETAIL) + "</p>",
        "<p>" + joined(PARA_CHECK) + "</p>",
        "<p>" + joined(PARA_SIGN_IN) + "</p>",
        # The href is the address the plain part prints and the button text is
        # the label the plain part prints, so a reader of either part sees the
        # same link with the same name. No image, no script, no form, no
        # hidden text.
        ('<p style="margin:24px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:12px 22px;'
         'background-color:#1b4f8a;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">' + LINK_LABEL + "</a></p>"),
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
        # own trace field. All three checks pass, and they pass for
        # fenwrightpay.example, the vendor's own domain. That is the fact the
        # exam question turns on, because 001 collects three passes too and
        # they name secure-verify-login.example instead.
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
        "X-Sentrywick-Spam-Score: 2.4",
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
        # RFC 3834 sec. 5: the employee portal sent this when the change was
        # saved, so the platform marks it, and a reply to it reaches no person.
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
        if phrase not in plain_text.lower():
            raise SystemExit("plain part broke the phrase across lines: " + phrase)
        if phrase not in html_text.lower():
            raise SystemExit("html part broke the phrase across lines: " + phrase)
    for phrase in FIXED_WORDING:
        if phrase not in " ".join(plain_text.split()):
            raise SystemExit("plain part lost the wording: " + phrase)
        if phrase not in " ".join(html_text.split()):
            raise SystemExit("html part lost the wording: " + phrase)
    both = (plain_text + "\n" + html_text).lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in both:
            raise SystemExit("the body carries a phrase from a content list the "
                             "record does not claim: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if LINK not in plain_text or 'href="' + LINK + '"' not in html_text:
        raise SystemExit("the one link must appear in both parts")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

LURE_SUMMARY = (
    "The real payroll vendor's automatic confirmation that the recipient "
    "changed his direct deposit account in the portal, with a link to review "
    "the account and a line telling him to contact his payroll administrator "
    "immediately if he did not make the change. The wording is almost the "
    "same as the phishing lure in 001, and every fact that separates them "
    "sits in a header or in a tool result."
)

BODY_BRIEF = (
    "The vendor's standard confirmation, greeted to Casimir under a Fenwright "
    "Payroll masthead. Open with 'Your direct deposit account was changed on "
    "4/27/2026.', then give the platform's reference detail: 'The change was "
    "recorded in the employee portal at 4:11 pm Central and applies to the "
    "deposit dated 5/1/2026. The account we hold for you now ends in 2210. "
    "Your confirmation number is DD-31408.' Then the two sentences that carry "
    "the message: 'If you made this change, no action is needed. If you did "
    "not, contact your payroll administrator immediately.' Then the one ask: "
    "'To see the details we hold for you, sign in to the employee portal with "
    "the same employee account you use for time entry.' One link, labeled "
    "'Review your account', to https://my.fenwrightpay.example/account. "
    "Footer as in 017: 'Fenwright Payroll on behalf of Pellgrave Mechanical "
    "Group. This is an automated message.' The words 'was changed', "
    "'immediately' and 'sign in' are the three content phrases; 'new account' "
    "is deliberately absent, because a confirmation reports the account the "
    "vendor now holds rather than announcing a new one, and that single word "
    "is what separates this body from 021. No deadline, no attachment, and no "
    "line that argues the message is safe."
)

MANIFEST_NOTES = (
    "Exam-only, so it renders under builder/instructor/exam-emails/ and never "
    "under corpus/emails/. The warehouse supervisor really changed his "
    "account on 4/27 after the SOC called him about 021, then reported the "
    "confirmation. The stem contrasts it with 001, 021 and 035. Rendered: "
    "From is Fenwright Payroll over the vendor's own fenwrightpay.example, "
    "which display_names.json gives that name, so no display name indicator "
    "applies; spf, dkim and dmarc all pass with policy.dmarc=reject, the "
    "policy domain_policy.json publishes for the vendor; the one link host is "
    "my.fenwrightpay.example, on url_allowlist.json since 2021-03-08, and the "
    "path is /account; Auto-Submitted: auto-generated marks the portal job; "
    "scan result clean and spam score 2.4. The body carries exactly three "
    "content phrases, 'was changed' and 'if you did not' for the account "
    "change notice, 'sign in' for the credential request and 'immediately' "
    "for the urgency, and url:login_path is carried by the sentence beside "
    "the link rather than by the path. The tier rule counts one decisive "
    "benign fact, an allowlisted sender with dmarc=pass, against two pressure "
    "facts, so the base tier is hard, and body_only_read is malicious, which "
    "is the opposite of the verdict and adds a step the cap absorbs. The "
    "sender-side hop is portal-app-04.fenwrightpay.example [192.0.2.13], the "
    "self-service portal node, where 017 comes from the payroll batch node "
    "payroll-app-02; both leave the vendor through "
    "smtp-out.fenwrightpay.example [203.0.113.12]."
)

# ------------------------------------------------------------- ground truth

NOTES = (
    "The exam case where the body and the facts point opposite ways and only "
    "the tools settle it. Key facts a correct extractor produces: from_domain "
    "fenwrightpay.example, the payroll vendor's own domain; no Reply-To, so "
    "there is no Reply-To mismatch to find; display_name_mismatch false, "
    "because display_names.json puts the name Fenwright Payroll on "
    "fenwrightpay.example and that is the From domain, which is the single "
    "byte-level difference from 001, where the same name sits over "
    "fenwright-pay.example; spf=pass on fenwrightpay.example, dkim=pass with "
    "d=fenwrightpay.example s=fw1, dmarc=pass with policy reject, so all "
    "three checks pass and the message is aligned; one link host, "
    "my.fenwrightpay.example, carrying the single link "
    "https://my.fenwrightpay.example/account; no attachment header; no "
    "In-Reply-To, so the message opens a thread. Received chain: "
    "portal-app-04.fenwrightpay.example [192.0.2.13] submitted with ESMTPSA "
    "to smtp-out.fenwrightpay.example at 21:14:02 +0000, which handed off "
    "with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 16:14:05 "
    "-0500, delivered by LMTP to mailstore-01.pellgrave.example at 16:14:07 "
    "-0500; Date is 16:14:00 -0500, the same instant as 21:14:00 +0000 in the "
    "Message-ID. X-Sentrywick-External is yes, scan result clean, spam score "
    "2.4, and Auto-Submitted is auto-generated, which is "
    "header:auto_submitted. Body content: three content codes and no others. "
    "content:account_change_notice matches 'was changed' and 'if you did "
    "not'; content:credential_request matches 'sign in'; "
    "content:urgency_keywords matches 'immediately'. No payment, "
    "payment-change, payment-timing, banking, data, file-share, secrecy or "
    "channel phrase appears, and the words 'new account' were kept out on "
    "purpose, because a confirmation reports the account the vendor now holds "
    "rather than announcing a new one; that is the one word that separates "
    "this body from 021's ask. url:login_path is recorded on the link text "
    "rather than on the path: the vocabulary entry reads 'a link path or text "
    "asks for a sign-in', the path here is /account, and the sentence beside "
    "the link asks the reader to sign in to the employee portal. The footer "
    "says the message is automated, the honest use of a word that also opens "
    "013's injection; the word alone addresses no automated reader and states "
    "no verdict, so there is no injection object and no "
    "content:instruction_to_ai. Difficulty reason: the tier rule counts one "
    "decisive benign fact, an allowlisted sender with dmarc=pass, against two "
    "pressure facts, the credential request and the urgency word, so pressure "
    "exceeds decisive and the base tier is hard; there is no injection, and "
    "body_only_read is malicious, the opposite of the verdict, which adds a "
    "step that the cap absorbs. body_only_read is malicious rather than "
    "uncertain because the body alone reads as the classic direct-deposit "
    "scare: an account change the reader is told to disown at once, a "
    "sign-in ask and a portal link, which is the shape 001 wears. Week 8 use: "
    "this is the case that fails a student who triages on prose. "
    "check_sender_reputation returns trusted for fenwrightpay.example, first "
    "seen 2021-03-08, 212 messages in 90 days and one prior report closed "
    "benign on 2026-02-11, and check_urls returns allowlisted for "
    "my.fenwrightpay.example, so the loop stops after two steps with "
    "stop_reason decisive_benign. lookup_recipient would add nothing to the "
    "verdict: it says Casimir Hallowden is a chronic reporter with eleven "
    "reports and no true positives in the window, which is context for how "
    "the reply is written and not evidence about the message. Playbook rules "
    "1, 2 and 7 close it: the passes name a domain, the vendor's name sits "
    "over the domain the vendor owns, and the link host is on the allowlist. "
    "Nothing in the body states either tool result, so the loop has to fetch "
    "them. escalate_expected is false and the action is "
    "close_benign_reply_to_reporter: the notice reports a change the reader "
    "made himself, asks for no data and moves no money, and no callback rule "
    "fires because the message carries no payment-change, payment-timing or "
    "banking phrase. Full credit on the indicators criterion needs "
    "sender:allowlisted_domain and url:host_allowlisted. Story context: 021 "
    "reached payroll on 22 April in Casimir's name and asked for his deposit "
    "to be moved; the SOC caught it and called him. On 27 April he signed in "
    "to the portal himself and changed the account, Fenwright's portal sent "
    "this confirmation three minutes later, and he reported it, which is why "
    "X-Sentrywick-Reported-By names him. The exam stem lines it up against "
    "001, 021 and 035, three malicious messages that share its vocabulary, "
    "its vendor and in one case its wording. Grading note: a student who "
    "calls this malicious because it says a deposit account was changed and "
    "then says 'immediately' has read the body and skipped the tools, and a "
    "student who escalates a confirmation the reporter caused has read the "
    "playbook's callback rule onto a message that asks for nothing. "
    "Rendering notes: the plain part is 7bit with hard wraps under 78 "
    "characters and the HTML part is quoted-printable, because the fixed "
    "gateway banner snippet is longer than 78 characters; the banner is the "
    "first line of the plain part and the first line after the body tag in "
    "the HTML part; both parts carry the same words in the same order and the "
    "HTML part hides nothing, so there is no content:html_hidden_text. The "
    "MIME boundary prefix is =_part_, the prefix the corpus gives a third "
    "party platform that composes its own mail, the same one 017 uses. There "
    "is no X-Originating-IP: the sender is a payroll platform rather than a "
    "webmail provider, so the submitting host's address 192.0.2.13 appears in "
    "the bottom Received line instead. Every identifier that looks random is "
    "derived from a SHA-256 over the corpus seed, the email id and a label, "
    "so the file regenerates byte for byte."
)

REFERENCE_SUMMARY = (
    "This is the real confirmation from Fenwright for the bank change you "
    "made in the portal on Monday. It is safe, and it is exactly the notice "
    "you should expect after that change."
)

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=fenwrightpay.example; dkim=pass "
    "header.d=fenwrightpay.example header.s=fw1 "
    "header.i=@fenwrightpay.example; dmarc=pass "
    "header.from=fenwrightpay.example policy.dmarc=reject"
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/exam/" + EMAIL_ID + ".eml",
    "set": "exam",
    "weeks": [8],
    "date": "2026-04-27T16:14:00-05:00",
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
         "value": SENDER_DOMAIN},
        {"code": "url:host_allowlisted", "where": "check_urls",
         "value": "my.fenwrightpay.example"},
        {"code": "url:login_path", "where": "body",
         "value": "sign in to the employee portal"},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "content:account_change_notice", "where": "body",
         "value": "was changed; if you did not"},
        {"code": "content:credential_request", "where": "body",
         "value": "sign in"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "immediately"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:chronic_reporter", "where": "lookup_recipient",
         "value": RECIPIENT},
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
            "name": "Casimir Hallowden",
            "role": "Warehouse Supervisor",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": True,
            "report_count_90d": 11,
            "true_positive_count_90d": 0,
            "campaign_tags": ["internal-notice", "marketing", "vendor-notice"],
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
    for field, value in (("set", GROUND_TRUTH["set"]),
                         ("subject", SUBJECT),
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
    if record["auth"] != {"spf": "pass", "dkim": "pass", "dmarc": "pass"}:
        raise SystemExit("manifest auth is " + repr(record["auth"]))
    manifest_codes = {item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]}
    rendered_codes = {item["code"] for item in GROUND_TRUTH["indicators"]}
    if manifest_codes != rendered_codes:
        raise SystemExit("indicator codes differ from the manifest: "
                         + repr(sorted(manifest_codes ^ rendered_codes)))
    if record["tool_expectations"] != GROUND_TRUTH["tool_expectations"]:
        raise SystemExit("tool_expectations differ from the manifest")
    if record["expected_loop"] != GROUND_TRUTH["expected_loop"]:
        raise SystemExit("expected_loop differs from the manifest")
    if not two_sentences(LURE_SUMMARY):
        raise SystemExit("lure_summary must be exactly two sentences")

    data = build_eml(seed)
    os.makedirs(EXAM_DIR, exist_ok=True)
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
