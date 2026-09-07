#!/usr/bin/env python3
"""Regenerate 047-cfo-hold-payment-run.

Rebuilds the exam email byte for byte from the corpus seed, refreshes the
matching manifest fields in spec/corpus-spec.json, and upserts the ground truth
record in ground_truth.json. It touches no other record and no data file.

This is an exam-only email, so the rendered file goes to
builder/instructor/exam-emails/ and never under corpus/emails/: nothing a
student can reach holds it before the week 8 exam. The ground truth file field
still reads emails/exam/047-cfo-hold-payment-run.eml, because that is the only
shape spec/ground_truth.schema.json accepts, so the corpus validator emits one
warning saying the record's path and the file's path differ, and a second
saying an exam record has no file under emails/. Both are correct and both are
expected for every exam record.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n)         = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    stream(label, n)      = sha256("<seed>|<id>|<label>|<block>") for block 0, 1, 2 ...
    DKIM t=               = the sender-side Received timestamp in epoch seconds

Neither DKIM value verifies. They are seeded bytes of the right length, the
convention the rest of the corpus uses, because no .example domain can publish
a key and no lab checks a signature. Nothing here reads the clock, the random
module or uuid4, so two runs produce identical bytes.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

This is the exam twin of 004 and the mirror of 019. 019 is the real CFO on the
internal path asking for a payment to move, and it is benign; this one is the
same ask shape from pellgrave-corp.example, the added-word lookalike, and it is
malicious. The attacker's own domain publishes SPF and DKIM, so spf, dkim and
dmarc all pass, and the only header line that carries the lie is From. The
submission host and the client are the ones 004 used, because the reputation
record for pellgrave-corp.example says two messages in ninety days and 004 and
this message are those two.

Two authored choices the manifest brief did not spell out, both recorded again
in the notes:

1. The brief wrote the callback as "Call me on my new cell, 555-0134". The
   string "call me" is a content:phone_verification_offered phrase in
   spec/enums.json, and this record does not carry that code; the corpus
   verifier runs every phrase list over the rendered body in both directions,
   so the phrase would fail the build as a fact the record does not name. It
   would also be the wrong fact: the code means the sender offered a number the
   reader can verify against, and this number is the attacker's. The line is
   written "reach me on my new cell, 555-0134" instead, which keeps the ask, the
   number and the "new cell" phrase that carries content:channel_restriction.
2. The rendered indicator list adds thread:new beside
   thread:reply_subject_without_reference. The file carries no In-Reply-To at
   all, and section 10 of docs/email-header-realism.md reads that absence in
   both directions, so a record that named only the second would be missing a
   fact a student's extractor produces. 018 carries the same pair for the same
   reason. Both codes are neutral and neither moves the difficulty tier.
3. check_callback_is_unused() refuses to render if 555-0134 has turned up in
   another manifest record or in a data file. The whole case rests on the
   number belonging to nobody, and nothing else in the build would notice if a
   later edit gave it an owner.

Run:  python3 corpus/tools/generators/gen_047_cfo_hold_payment_run.py
"""

import base64
import calendar
import datetime
import hashlib
import json
import os
import uuid

EMAIL_ID = "047-cfo-hold-payment-run"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
# Exam only: the rendered file ships in the instructor package, never under
# corpus/emails/, so nothing a student can reach holds it before the exam.
EML_PATH = os.path.join(BUILDER, "instructor", "exam-emails", EMAIL_ID + ".eml")
# The path the ground truth record names. spec/ground_truth.schema.json fixes
# the shape as emails/<set>/<id>.eml, so an exam record names a path that no
# file sits at on purpose.
GT_FILE = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "r.palomares@pellgrave-corp.example"
SENDER_DISPLAY = "Rutger Palomares (CFO)"
RECIPIENT = "p.castellanos@pellgrave.example"
RECIPIENT_DISPLAY = "Priya Castellanos"
REPORTER = RECIPIENT
SUBJECT = "Re: vendor payment run for 4/30"

# The attacker's own submission host and client, the same pair 004 came from.
# data/sender_reputation.json gives pellgrave-corp.example two messages in
# ninety days, and 004 and this message are those two.
SENDER_SMTP = "smtp.pellgrave-corp.example"
SENDER_SMTP_IP = "203.0.113.151"
SENDER_CLIENT = "client-04.pellgrave-corp.example"
SENDER_CLIENT_IP = "192.0.2.62"
GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# Local is -0500 all the way through; the sender side stamps UTC, as every
# sender-side hop in the corpus does.
DATE_LOCAL = "Mon, 27 Apr 2026 11:15:00 -0500"
SENDER_STAMP = "Mon, 27 Apr 2026 16:15:02 +0000"
GATEWAY_STAMP = "Mon, 27 Apr 2026 11:15:05 -0500"
STORE_STAMP = "Mon, 27 Apr 2026 11:15:07 -0500"
# Message-ID left side is the Date in UTC, the house convention.
MESSAGE_STAMP = "20260427161500"
# The sender-side Received timestamp in epoch seconds, for DKIM t=.
DKIM_TIME = calendar.timegm(datetime.datetime(2026, 4, 27, 16, 15, 2).utctimetuple())

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break.
QP_MAXLEN = 76


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def signature(seed):
    """344 base64 characters, the length of a 2048 bit RSA signature."""
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


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
# Three short paragraphs and a signature block, the length of note a chief
# financial officer types to the accounts payable desk between meetings. It
# names the run by the date already in the subject, gives a reason that cannot
# be checked without reaching him, moves the callback off the number in the
# directory, and closes with the block anyone can copy off a signed message.
#
# The record names exactly two content codes, and the phrase lists in
# spec/enums.json decide them, so the wording is written to the lists and
# assert_content_phrases() below refuses to write the file if that stops being
# true:
#
#   "hold the run" -> content:payment_timing_request, the required ask.
#   "new cell"     -> content:channel_restriction, the reason the number on
#                     file will not reach him.
#
# Phrases the wording stays clear of, because this record names no other
# content code and validate_corpus.py runs every list in both directions:
#
#   "call me" is out (content:phone_verification_offered). The brief wrote the
#   callback that way; "reach me" carries the same ask without claiming the
#   sender offered a number anyone can verify him on.
#   "invoice", "past due" and "remit" are out (content:payment_request): what
#   is being held is the run, not a document, and the vendor is never named.
#   "new account", "new bank" and "update the vendor account" are out
#   (content:payment_change_request): nothing is said about where money goes,
#   only about when it goes, which is the whole distinction from 049.
#   "today", "same-day", "credit hold" and "before 3" are out
#   (content:urgency_keywords): the deadline is Thursday and the message never
#   presses for speed. It presses for silence, which is a different lever.
#   "confidential", "quietly" and "between us" are out
#   (content:secrecy_request); nothing is asked to be kept off the record.
#   "wire" is out (content:banking_instruction), "download" and "shared with
#   you" are out (content:file_share_lure), "sign in", "password" and
#   "credentials" are out (content:credential_request), and "was changed" is
#   out (content:account_change_notice): the vendor account "is being
#   corrected", which is the near miss kept on purpose.
#
# No link and no attachment, which is what url:none and attachment:none key on
# and what leaves the week 8 loop with two calls and tools_exhausted.

GREETING = "Priya,"

# Both parts carry these words. The plain part breaks the lines where a mail
# client would; the HTML part joins each paragraph into one run, so both
# phrases above sit unbroken in both parts and an extractor reading either one
# finds them.
PARA_1 = [
    "Hold the run on Thursday until you hear from me. One of the vendor",
    "accounts is being corrected and I do not want the 4/30 file going out",
    "against it.",
]
PARA_2 = [
    "I am out of the office the rest of the week, so before you release",
    "anything, reach me on my new cell, 555-0134. The desk line rolls to",
    "voicemail and I will not pick it up.",
]
PARA_3 = [
    "Nothing else changes. I should have this settled by Wednesday.",
]

SIGN_OFF = "Rutger"

# The CFO's real two line block, the same one 019, 023, 039 and 055 carry, down
# to the extension. It is on every message he has ever signed, so copying it is
# the cheapest part of the impersonation, and it leaves the contradiction an
# analyst reads: the block gives the number the directory holds and the
# paragraph above it routes her to a mobile that the directory does not.
SIGNATURE = [
    "Rutger Palomares",
    "Chief Financial Officer, Pellgrave Mechanical Group, ext. 4102",
]


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += PARA_3 + [""]
    lines += [SIGN_OFF, ""]
    lines += SIGNATURE
    return lines


def html_part():
    """The same words, in the plain paragraphs a desktop mail client writes."""
    return [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#ffffff;">',
        BANNER_HTML,
        ('<div style="font-family:sans-serif;font-size:14px;color:#222222;'
         'padding:14px 12px;">'),
        "<p>" + GREETING + "</p>",
        "<p>" + " ".join(PARA_1) + "</p>",
        "<p>" + " ".join(PARA_2) + "</p>",
        "<p>" + " ".join(PARA_3) + "</p>",
        "<p>" + SIGN_OFF + "</p>",
        "<p>" + SIGNATURE[0] + "<br>",
        SIGNATURE[1] + "</p>",
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start of
    the next line; when no space fits, hard break at 75 characters plus the soft
    line break, never inside an "=XX" escape.
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


# ------------------------------------------------------------------- checks

# The two codes this record names, with the phrase each one is written to.
CLAIMED_PHRASES = {
    "content:payment_timing_request": "hold the run",
    "content:channel_restriction": "new cell",
}


def assert_content_phrases(plain_text, html_text):
    """The rendered body matches the two claimed phrase lists and no other.

    validate_corpus.py runs the lists in spec/enums.json over the decoded parts
    in both directions, so a phrase from an unnamed code fails the build as a
    fact the record does not carry, and a named code with no phrase fails as a
    fact the corpus extraction mechanism cannot find. Both directions are
    checked here so the failure names the phrase rather than the file. The two
    lists the phrase pass skips are skipped here too: content:non_english_body
    is Spanish stopwords that sit inside English words, and
    content:instruction_to_ai is single words the corpus also uses inside
    quoted examples.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    for part_name, text in (("plain", plain_text), ("html", html_text)):
        haystack = text.lower()
        for code, phrases in sorted(enums["content_phrases"].items()):
            if code in skip or where_of.get(code) != "body":
                continue
            hits = [p for p in phrases if p.lower() in haystack]
            if code in CLAIMED_PHRASES:
                if CLAIMED_PHRASES[code] not in hits:
                    raise SystemExit("the " + part_name + " part must carry the " + code
                                     + " phrase " + repr(CLAIMED_PHRASES[code]))
            elif hits:
                raise SystemExit("the " + part_name + " part carries the " + code
                                 + " phrase " + repr(hits[0])
                                 + " but this record does not name that code")


# The callback number, and the files that must not already hold it.
CALLBACK = "555-0134"
DATA_FILES = ("data/sender_reputation.json", "data/recipients.json",
              "data/display_names.json", "data/domain_policy.json",
              "data/url_allowlist.json", "data/url_blocklist.json",
              "data/url_unlisted.json", "data/known_good_domains.json",
              "data/attachments.json", "data/known_threads.json",
              "data/playbook.md")


def check_callback_is_unused(spec):
    """Refuse to write a callback number anything else in the corpus uses.

    The tell this record turns on is that the number the message gives is not
    the number anyone holds for Rutger. If a later edit gave 555-0134 to a real
    mailbox, a vendor or another record, the message would stop being a lie in
    the one place it is supposed to be one, and nothing else in the build would
    notice. So the check runs on every render rather than once.
    """
    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            continue
        if CALLBACK in json.dumps(record):
            raise SystemExit("the callback number " + CALLBACK + " already appears in "
                             "record " + record["id"] + "; pick a number nothing else uses")
    for rel in DATA_FILES:
        path = os.path.join(CORPUS, rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as handle:
            if CALLBACK in handle.read():
                raise SystemExit("the callback number " + CALLBACK + " appears in " + rel
                                 + "; the number must belong to nobody")


def assert_no_links(plain_text, html_text):
    """url:none, so neither part may carry a URL of any scheme."""
    for part_name, text in (("plain", plain_text), ("html", html_text)):
        lowered = text.lower()
        for scheme in ("http://", "https://", "mailto:", "ftp://", "www."):
            if scheme in lowered:
                raise SystemExit("the " + part_name + " part carries " + scheme
                                 + " but the record says url:none")


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = "<" + MESSAGE_STAMP + "." + hexid(seed, "message-id") + "@" + SENDER_SMTP + ">"
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # The gateway writes Authentication-Results above its own trace fields
        # (RFC 8601 sec. 4). data/domain_policy.json gives pellgrave-corp.example
        # spf "mx -all", dkim selector k1 and dmarc policy none, and the attacker
        # owns all three, so all three pass and align. That is the week 3 lesson
        # this record exists for: a pass names the domain, never the person.
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=pellgrave-corp.example;",
        "  dkim=pass header.d=pellgrave-corp.example header.s=k1",
        "    header.i=@pellgrave-corp.example;",
        "  dmarc=pass header.from=pellgrave-corp.example policy.dmarc=none",
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + SENDER + " designates " + SENDER_SMTP_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + SENDER_SMTP_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + SENDER_SMTP + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        # Clean and a middling score. There is no link, no attachment and no
        # word the filters weight, so nothing the gateway measures is wrong
        # with this message. The whole case sits in the From line and the body.
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 3.3",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_SMTP,
        "  (" + SENDER_SMTP + " [" + SENDER_SMTP_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        # The bottom hop is the same desktop client on the same attacker
        # submission host that sent 004 thirteen days earlier, which is why the
        # reputation record counts two messages in ninety days.
        "Received: from " + SENDER_CLIENT + " ([" + SENDER_CLIENT_IP + "])",
        "  by " + SENDER_SMTP + " with ESMTPSA id " + sender_id + ";",
        "  " + SENDER_STAMP,
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=pellgrave-corp.example; s=k1; t=" + str(DKIM_TIME) + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type:x-mailer;",
        "  bh=" + body_hash(seed) + ";",
    ]
    chunks = signature(seed)
    for index in range(0, len(chunks), 72):
        lines.append(("  b=" if index == 0 else "   ") + chunks[index:index + 72])
    lines += [
        "Date: " + DATE_LOCAL,
        # The display name carries a parenthesised role, so RFC 5322 sec. 3.4
        # needs it quoted: bare parentheses in a display name are a comment.
        'From: "' + SENDER_DISPLAY + '" <' + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        # "Re:" with nothing under it. There is no In-Reply-To and no
        # References, so the prefix claims a conversation no store can resolve,
        # which is thread:reply_subject_without_reference; the file also carries
        # no In-Reply-To at all, which is thread:new. The payment run is a real
        # standing subject between these two mailboxes, so the prefix is what
        # makes the message read as the next line of a thread Priya is already
        # in.
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # The same client 004 named. No Reply-To: replies go to the attacker's
        # own mailbox on the lookalike domain, so nothing needs redirecting.
        "X-Mailer: Marrowdale Mail 5.2",
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    # The plain part is pure ASCII under 78 characters a line, so it stays 7bit
    # (docs/email-header-realism.md sec. 2). The HTML part carries the banner
    # snippet, which is longer than 78, so that part is quoted-printable.
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
    for text, label in ((plain_text, "plain"), (html_text, "html")):
        if text.count(BANNER_PLAIN) != 1:
            raise SystemExit("the gateway banner must appear once in the " + label + " part")
    if plain_text.splitlines()[0] != BANNER_PLAIN:
        raise SystemExit("the plain part must open with the gateway banner")
    if plain_text.splitlines()[1] != "":
        raise SystemExit("an empty line must follow the gateway banner")
    assert_content_phrases(plain_text, html_text)
    assert_no_links(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Three short paragraphs in Rutger's voice, the length of note he types to "
    "the accounts payable desk between meetings. Salutation 'Priya,', then "
    "'Hold the run on Thursday until you hear from me. One of the vendor "
    "accounts is being corrected and I do not want the 4/30 file going out "
    "against it.', then 'I am out of the office the rest of the week, so "
    "before you release anything, reach me on my new cell, 555-0134. The desk "
    "line rolls to voicemail and I will not pick it up.', then 'Nothing else "
    "changes. I should have this settled by Wednesday.' Sign 'Rutger', then "
    "the CFO's real two line block ending 'ext. 4102', which the attacker "
    "copies off any message Rutger has signed and which leaves the number in "
    "the directory sitting under the mobile that is not in it. Use the phrase "
    "'hold the run', which carries content:payment_timing_request, and the "
    "phrase 'new cell', which carries content:channel_restriction, and keep "
    "both unbroken on one line in both body parts. Write the callback as "
    "'reach me on my new cell' and never 'call me': that string is a "
    "content:phone_verification_offered phrase in spec/enums.json, this record "
    "does not name that code, and the code would be wrong here because the "
    "number is the attacker's rather than one the reader can verify against. "
    "Name no vendor and no amount, so the body hands the week 8 loop nothing "
    "to look up. No link, no attachment, no bank details and no quoted text "
    "under the 'Re:'."
)

LURE_SUMMARY = (
    "The CFO's name over a lookalike domain asks accounts payable to hold "
    "Thursday's payment run and to reach him on a new mobile number before "
    "anything is released. There is no link and no attachment, and all three "
    "authentication checks pass for the lookalike domain."
)

MANIFEST_NOTES = (
    "Exam-only twin of 004 and the mirror of 019: the same ask shape from the "
    "lookalike domain instead of the internal path, so a student who read 019 "
    "as 'the CFO asking about a payment run is fine' and 004 as 'the CFO in a "
    "hurry is bad' has learned neither rule. Stems: which header line shows "
    "the lie, and why three passes do not make it safe. The rendered indicator "
    "list adds thread:new beside thread:reply_subject_without_reference, "
    "because the file carries no In-Reply-To at all and the corpus verifier "
    "reads that absence both ways; the authored list named only the second. "
    "018 carries the same pair for the same reason, both codes are neutral and "
    "neither moves the tier. The callback is written 'reach me on my new cell' "
    "rather than the brief's 'call me', because 'call me' is a "
    "content:phone_verification_offered phrase and this record does not name "
    "that code; the ask, the number and the 'new cell' phrase are unchanged. "
    "Escalation reasons: financial_or_endpoint_impact."
)

MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:display_name_matches_employee:Rutger Palomares",
    "sender:lookalike_domain:pellgrave.example",
    "sender:first_seen",
    "content:payment_timing_request",
    "content:channel_restriction",
    "header:external_flag:yes",
    "url:none",
    "attachment:none",
    "thread:new",
    "thread:reply_subject_without_reference",
    "recipient:handles_payments",
    "recipient:prior_similar_report",
]

GT_INDICATORS = [
    {"code": "auth:all_pass", "where": "Authentication-Results",
     "value": ("spf=pass smtp.mailfrom=pellgrave-corp.example; dkim=pass "
               "header.d=pellgrave-corp.example header.s=k1 "
               "header.i=@pellgrave-corp.example; dmarc=pass "
               "header.from=pellgrave-corp.example policy.dmarc=none")},
    {"code": "sender:display_name_matches_employee", "where": "From",
     "value": "Rutger Palomares"},
    {"code": "sender:lookalike_domain", "where": "From",
     "value": "pellgrave.example"},
    {"code": "sender:first_seen", "where": "check_sender_reputation",
     "value": "2026-04-14"},
    {"code": "content:payment_timing_request", "where": "body",
     "value": "hold the run"},
    {"code": "content:channel_restriction", "where": "body",
     "value": "new cell"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "url:none", "where": "body", "value": None},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
    {"code": "thread:reply_subject_without_reference", "where": "Subject, In-Reply-To",
     "value": SUBJECT},
    {"code": "recipient:handles_payments", "where": "lookup_recipient",
     "value": RECIPIENT},
    {"code": "recipient:prior_similar_report", "where": "lookup_recipient",
     "value": "vendor-invoice-fraud"},
]

GT_NOTES = (
    "Business email compromise with no link and no attachment, held back for "
    "the week 8 exam because it is the pair to two teaching records a student "
    "has already been graded on. Key facts a correct extractor produces: "
    "from_domain pellgrave-corp.example; display name 'Rutger Palomares "
    "(CFO)', which data/display_names.json gives to pellgrave.example alone, "
    "so the name is the company's real Chief Financial Officer and his address "
    "is r.palomares@pellgrave.example; reply_to_domain none, because there is "
    "no Reply-To header and replies land in the attacker's own mailbox on the "
    "lookalike; spf pass, dkim pass, dmarc pass with policy none; url_hosts "
    "empty; no removed-attachment header; no In-Reply-To and no References. "
    "The one header line that carries the lie is From, and every other line in "
    "the file is true. pellgrave-corp.example is an added-word lookalike the "
    "attacker registered and publishes for: data/domain_policy.json gives it "
    "owner_class attacker, spf 'mx -all', dkim selector k1 and dmarc policy "
    "none, so all three checks pass and align on a domain that is not ours. "
    "Playbook rule 1 says what that proves and rule 2 decides the case: an "
    "employee's name over an address outside pellgrave.example is "
    "impersonation until a phone call proves otherwise, and the call goes to "
    "the extension the message itself prints, not to the mobile it asks for. "
    "Rule 5 also applies and is the reason this escalates whatever anyone "
    "decides about the verdict: a change to when a payment goes out gets a "
    "phone call to the number on file first. The Subject begins 'Re:' with "
    "nothing under it, so both thread facts are recorded: thread:new, because "
    "the store files this as the start of a thread, and "
    "thread:reply_subject_without_reference, because the prefix claims a "
    "conversation nothing can resolve. The manifest's authored list named only "
    "the second; the rendered record adds thread:new because the file carries "
    "no In-Reply-To and the section 10 verifier reads that absence in both "
    "directions. Both are neutral. Difficulty medium: the tier rule counts two "
    "decisive facts (sender:display_name_matches_employee and "
    "sender:lookalike_domain) against one pressure point, url:none with "
    "attachment:none, which is decisive over pressure without a tie; there is "
    "no injection, and the body-only read is uncertain rather than benign, so "
    "no adjustment applies. auth:all_pass counts for nothing, exactly as it "
    "does on any attacker-owned domain. Content: the ask is to hold Thursday's "
    "run until the sender is heard from, the reason given is a vendor account "
    "being corrected that is never named, the callback is moved to a mobile, "
    "555-0134, which appears in no other manifest record and in none of the "
    "data files, so nothing any tool returns can confirm the number is his, "
    "and the close says nothing else changes. The two content codes are the "
    "phrase lists in spec/enums.json decide: 'hold the run' for "
    "content:payment_timing_request and 'new cell' for "
    "content:channel_restriction, both unbroken on one line in both parts. The "
    "wording stays clear of every other list, which is why the vendor account "
    "'is being corrected' rather than 'was changed', why the run is held "
    "rather than paid 'today', why no invoice is named, and why the callback "
    "reads 'reach me on my new cell' rather than 'call me': 'call me' is a "
    "content:phone_verification_offered phrase and this sender is offering the "
    "opposite of verification. Corroborating context rather than a scored "
    "indicator: the signature block is the CFO's real one, 'Rutger Palomares' "
    "over 'Chief Financial Officer, Pellgrave Mechanical Group, ext. 4102', "
    "the same block 019, 023, 039 and 055 carry, so the message prints the "
    "number in the directory two lines under the mobile it tells her to use "
    "instead. An analyst should read that, and a student who finds it is "
    "right, but the indicator vocabulary in spec/enums.json has no code for a "
    "signature that disagrees with the body; the phrase itself is already "
    "carried by content:channel_restriction. Body: multipart/alternative with "
    "a text/plain part in 7bit then a text/html part in quoted-printable, the "
    "same words in both, three paragraphs and a signature block with no link, "
    "image, script or hidden text. Received chain: "
    "client-04.pellgrave-corp.example [192.0.2.62] submitted with ESMTPSA to "
    "smtp.pellgrave-corp.example at 16:15:02 +0000, which is 11:15:02 local; "
    "smtp.pellgrave-corp.example [203.0.113.151] handed it to "
    "mx.pellgrave.example over TLS1_3 at 11:15:05 -0500; the gateway delivered "
    "by LMTP to mailstore-01.pellgrave.example at 11:15:07; Date is 11:15:00. "
    "That submission host and that client are the ones 004 came from thirteen "
    "days earlier, which is why data/sender_reputation.json counts two "
    "messages in ninety days for pellgrave-corp.example: 004 and this one. "
    "mailstore-01 is the store data/recipients.json gives "
    "p.castellanos@pellgrave.example, the same store 004, 011, 019 and 021 "
    "deliver to, because a mailbox lives on one store whatever path a message "
    "took. X-Sentrywick-External is yes, the scan is clean and the spam score "
    "is 3.3: nothing the gateway measures is wrong with this message, which is "
    "the point of putting it on an exam. Week 8 loop: "
    "check_sender_reputation is the natural first call and returns status "
    "unknown at domain level with new_domain true and first_seen 2026-04-14, "
    "which is suggestive and not decisive; lookup_recipient then shows Priya "
    "Castellanos is an ordinary mailbox that handles payments, with six "
    "reports and four true positives in ninety days and a prior "
    "vendor-invoice-fraud report, which is context and not decisive either; "
    "check_urls has nothing to look up, so the loop stops on tools_exhausted "
    "after two calls rather than spending a step on a tool with no input. The "
    "verdict has to come from the From line read against "
    "data/display_names.json, which no tool call returns. "
    "recipient:prior_similar_report is present by the prior_similar_report_rule: "
    "content:payment_timing_request is an ask code and maps to "
    "vendor-invoice-fraud, and Priya's record holds two prior "
    "vendor-invoice-fraud reports, both true positives, so the matched tag is "
    "vendor-invoice-fraud. Full credit on the indicators criterion needs "
    "sender:lookalike_domain and sender:display_name_matches_employee, because "
    "a note that says only 'the CFO would not do this' has not named the fact "
    "that settles it. Escalates under financial_or_endpoint_impact, because a "
    "malicious BEC always escalates whatever the recipient's flags say. Priya "
    "is not an executive, so executive_target does not apply, and she reported "
    "the message before acting on it, so user_interacted does not apply. The "
    "correct close is to reach Rutger at ext. 4102, block "
    "pellgrave-corp.example, tell accounts payable that the 4/30 run stands, "
    "and add 555-0134 to the numbers the desk refuses. Deliberate omissions, "
    "matching the indicator list: no Reply-To, no In-Reply-To or References, "
    "no X-Priority or Importance, no Auto-Submitted, no X-Originating-IP, no "
    "List headers and no removed attachment."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": GT_FILE,
    "set": "exam",
    "weeks": [8],
    "date": "2026-04-27T11:15:00-05:00",
    "verdict": "malicious",
    "category": "bec",
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
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:lookalike_domain",
                            "sender:display_name_matches_employee"],
    "url_hosts": [],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "pellgrave-corp.example",
            "status": "unknown",
            "first_seen": "2026-04-14",
            "messages_90d": 2,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Priya Castellanos",
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
    "expected_loop": {"tools": ["check_sender_reputation", "lookup_recipient"],
                      "stop_reason": "tools_exhausted"},
    "escalate_expected": True,
    "escalation_reasons": ["financial_or_endpoint_impact"],
    "recommended_action": "escalate_incident",
    "reference_summary": ("This did not come from Rutger; the address is on a "
                          "look-alike domain, and the 'new cell' number is not in "
                          "our directory. Do not call that number or hold any "
                          "payments on its say-so."),
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

    check_callback_is_unused(spec)

    os.makedirs(os.path.dirname(EML_PATH), exist_ok=True)
    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            record["indicators"] = list(MANIFEST_INDICATORS)
            record["body_brief"] = BODY_BRIEF
            record["lure_summary"] = LURE_SUMMARY
            record["notes"] = MANIFEST_NOTES
            break
    else:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    for index, record in enumerate(records):
        if record["id"] == EMAIL_ID:
            records[index] = GROUND_TRUTH
            break
    else:
        records.append(GROUND_TRUTH)
        records.sort(key=lambda record: record["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH)
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
