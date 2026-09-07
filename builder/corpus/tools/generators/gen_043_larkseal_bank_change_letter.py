#!/usr/bin/env python3
"""Regenerate 043-larkseal-bank-change-letter.

Rebuilds emails/batch/043-larkseal-bank-change-letter.eml byte for byte from
the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record and no data file.

Every identifier in the file that looks random is derived from the corpus
seed, so rerunning this script reproduces the same bytes:

    hexid(label, n)  = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = the first n bytes of
                       sha256("<seed>|<email id>|<label>|0")
                       || sha256("<seed>|<email id>|<label>|1") || ...

    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also
                            X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=hexid("store-id", 32), version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Only the b= tag needs the block indexed stream, because a 2048 bit signature
is 256 bytes and one digest is 32. bh= is one digest and is taken as one,
which is the form gen_007 and gen_016 use. Neither value verifies anything:
no .example domain can publish a DKIM key, and the course reads the gateway's
Authentication-Results verdict rather than recomputing a signature.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

Two values are read back from the data files rather than typed here:
data/recipients.json gives the one store that holds ap@pellgrave.example, and
data/attachments.json gives the removed file's name, size, action, type and
reason, with its sha256 rechecked against sha256("<seed>|<id>|<filename>")
before the header is written. The recipient is a shared mailbox rather than a
distribution list, so the LMTP hop names the recipient itself; the reporter
appears only in X-Sentrywick-Reported-By, because a shared mailbox is worked
by several people and the person who pressed report is not the addressee.

What this message is.

This is the benign twin of 016. Larkseal really did move its receivables, the
letter really is signed, the mail really did leave the vendor's own outbound
server, and the vendor itself asks accounts payable to telephone before
anything is changed. Everything a nervous reader reaches for is here: a bank
change, an archived PDF, a shared payments mailbox with two prior
vendor-invoice-fraud reports. None of it is a finding. The verdict is benign
and the record still escalates, because playbook rule 5 puts a callback on
every bank change whatever the verdict, which is the one lesson this file
carries: verdict and escalation are separate decisions.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are all present because the message crossed the
    border gateway. spf=pass on larkseal.example, dkim=pass with
    d=larkseal.example s=ls2026, dmarc=pass with policy quarantine, exactly as
    data/domain_policy.json publishes them. The published SPF record is
    "mx -all", so the Received-SPF mechanism is mx and the client address is
    the vendor's own mail exchanger.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 2.8 match the
    received_path_hint in the manifest. The score is low and not zero: a
    filter sees a bank and a date in a first message on a new thread, and
    nothing else it dislikes.
  * X-Sentrywick-Removed-Attachment records the signed letter with
    action=quarantined and reason=archived-to-vault, which is normal document
    policy at this gateway and, by playbook rule 8, proves nothing. Both body
    parts end with the notice naming the file, the way section 2 of
    docs/email-header-realism.md fixes it.
  * mx-out.larkseal.example is the vendor's outbound host, named by the
    manifest's received_path_hint. data/domain_policy.json lists app., mail.
    and help. in its notes because those are the hosts the URL lists and the
    reputation record care about; the outbound relay is new here and appears
    only in the trace layer, never in a link.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because the clerk sends from the mailbox she reads and the record
says reply_to is null; no In-Reply-To and no References, so thread:new holds
even though the body refers to a telephone call, which leaves no header
behind; no X-Priority and no Importance, because a vendor giving five weeks of
notice does not flag its own mail; no Auto-Submitted, because a person wrote
it; no X-Originating-IP, because the sender is the vendor's own server rather
than a webmail provider, so the author's workstation address sits in the
bottom Received line instead.

One phrase note, and it is the reason this file is worth reading twice.

The record's content codes are content:payment_change_request and
content:phone_verification_offered, and the prose is held clear of every other
phrase list in spec/enums.json: no "invoice", no "remittance", no "past due",
no "wire", no "today", no "sign in", no "download", no "was changed". The
rendered body still carries one more code, and the ground truth record below
lists it: content:payment_request, on the phrase "remit". It comes from the
gateway notice, which section 2 requires in both parts and which has to name
the archived file byte for byte, and the file is called
Larkseal_Remittance_Change_Letter_2026-04.pdf. "remit" is a substring of
"Remittance", the phrase pass in tools/validate_corpus.py is a lowercased
substring test over both decoded parts, and no wrapping escapes it, because a
break inside the name would stop the notice check from finding the filename.
The same collision is already answered the other way in three sibling records:
032, 037 and 049 all carry an Invoice_*.pdf stub and all three list
content:payment_request in the manifest. This record does not, and the
mismatch is left in place rather than fixed here, because content:payment_request
carries polarity PB: adding it to the manifest indicator list moves pressure
from 1 to 2 against 1 decisive fact, and tools/check_spec.py would then
recompute the tier as hard where the record is authored medium. That is a
semantic change to an authored field, so it is reported rather than made. The
ground truth records what an extractor actually finds; the manifest keeps what
was authored.

Run:  python3 corpus/tools/generators/gen_043_larkseal_bank_change_letter.py
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

EMAIL_ID = "043-larkseal-bank-change-letter"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "ar@larkseal.example"
SENDER_DISPLAY = "Larkseal Accounts Receivable"
# The envelope sender is the From mailbox. An accounts receivable clerk sends
# from the mailbox she reads, so Return-Path and From are one address and there
# is no envelope-versus-author split and no Reply-To to explain.
ENVELOPE_SENDER = SENDER
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

SUBJECT = "Signed remittance change letter, per Tuesday's call"

SENDER_DOMAIN = "larkseal.example"
SENDER_HOST = "mx-out.larkseal.example"
SENDER_SUBMIT_HOST = "LS-AR-0118.larkseal.example"
SENDER_IP = "203.0.113.51"
SENDER_SUBMIT_IP = "192.0.2.51"
DKIM_SELECTOR = "ls2026"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SCAN_RESULT = "clean"
SPAM_SCORE = "2.8"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 19:05 +0000 is the same instant as 14:05 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. 22 April 2026 is a Wednesday and
# the Tuesday the body names is the day before.
DATE_HEADER = "Wed, 22 Apr 2026 14:05:00 -0500"
SUBMIT_STAMP = "Wed, 22 Apr 2026 19:05:03 +0000"
SUBMIT_UTC = "2026-04-22 19:05:03"
GATEWAY_STAMP = "Wed, 22 Apr 2026 14:05:06 -0500"
STORE_STAMP = "Wed, 22 Apr 2026 14:05:08 -0500"
MESSAGE_ID_STAMP = "20260422190500"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break. The HTML part here is written as short source lines,
# so only the gateway banner runs long, and it holds no space a break could
# usefully land on. The wrap is therefore a hard one at 75 characters plus the
# "=", stepping back if a break would fall inside an "=XX" escape. Soft breaks
# decode away, so they cannot split a phrase the week 3 extractor looks for.
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
    return str(uuid.UUID(hex=hexid(seed, "store-id", 32), version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def signature(seed):
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


def dkim_time():
    """Unix time of the sender-side Received stamp, so the two cannot drift."""
    return calendar.timegm(time.strptime(SUBMIT_UTC, "%Y-%m-%d %H:%M:%S"))


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def mailstore(address):
    """The one store that delivers this mailbox, from data/recipients.json."""
    for record in load_json(RECIPIENTS_PATH)["recipients"]:
        if record["address"] == address:
            store = record.get("mailstore")
            if not store:
                raise SystemExit("recipients.json has no mailstore for " + address)
            return store
    raise SystemExit("recipients.json has no record for " + address)


def attachment_stub(seed):
    """The removed file, from data/attachments.json, with its digest rechecked."""
    for entry in load_json(ATTACHMENTS_PATH)["attachments"]:
        if entry["email_id"] != EMAIL_ID:
            continue
        want = hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + entry["filename"]).encode()).hexdigest()
        if entry["sha256"] != want:
            raise SystemExit("attachments.json sha256 for " + entry["filename"]
                             + " is not sha256(seed|id|filename)")
        return entry
    raise SystemExit("attachments.json has no entry for " + EMAIL_ID)


# ---------------------------------------------------------------- body text

# Wording rules this text obeys, all from spec/enums.json content_phrases.
#
#   The one content:payment_change_request phrase is "new bank", sitting whole
#   on one line of both parts. "changed banks", "new routing", "new account
#   number", "new account", "updated remittance", "update the remit-to",
#   "new ach", "updated ach" and "update the vendor account" are all out, so
#   the ask reads "update the vendor record" and the numbers stay in the signed
#   letter where a careful vendor puts them rather than in the mail body.
#   The two content:phone_verification_offered phrases are "as discussed on
#   Tuesday's call" and "call the number on file", each whole on one line.
#   "call me" is out: this clerk does not want to be called back on a number
#   she supplied, which is the whole point of the paragraph.
#   "remit" and "remittance" are out of the prose (content:payment_request),
#   and so are "invoice", "past due", "amount due", "net 15", "net 30" and
#   "payment is due". The Subject still reads "Signed remittance change
#   letter", because the phrase pass reads the decoded body parts and not the
#   header. The gateway notice at the end of both parts does carry "remit"
#   inside the archived file name; see the module docstring.
#   "today", "by friday", "before monday", "urgent", "immediately",
#   "as soon as possible" and the rest of content:urgency_keywords are out.
#   The dates here are a five week notice period, not a countdown.
#   "wire" (content:banking_instruction), "download" and "shared with you"
#   (content:file_share_lure), "sign in" and "password"
#   (content:credential_request), "was changed" and "if you did not"
#   (content:account_change_notice), "confidential" and "quietly"
#   (content:secrecy_request), "reply by email" and "cannot take a call"
#   (content:channel_restriction), "not working" and "personal address"
#   (content:excuse_for_external_address) and every
#   content:payment_timing_request phrase are all out. Nothing here asks for a
#   payment to move, be held or be released early: the 4/24 run and every run
#   after it stays exactly where it was.
#
# The register is a vendor doing this correctly. She gives the effective date,
# she attaches a signed letter, she tells accounts payable not to act on the
# mail alone, and she apologises for the paperwork. That is what makes the file
# hard: everything an anxious reader reaches for is present, and none of it is
# a finding.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

BRAND = "Larkseal"
SALUTATION = "Priya,"

PARA_OPENING = [
    "Thank you for the time on Tuesday. As discussed on Tuesday's call,",
    "Larkseal has moved its receivables to a new bank, and the change",
    "takes effect 5/1.",
]

PARA_LETTER = [
    "The signed letter is attached. It is on our letterhead, our",
    "controller signed it on 4/20, and it gives the bank name, the",
    "routing number and the last four digits of the account it replaces.",
]

# The paragraph the whole record exists for. The vendor asks for the callback
# itself, and asks for it on the number accounts payable already holds rather
# than on anything printed below, which is the one instruction a forged copy of
# this message could not usefully imitate.
PARA_CALLBACK = [
    "Please do not change anything on our record from this message on",
    "its own. Call the number on file for Larkseal, not a number out of",
    "this mail, ask for accounts receivable, and have someone read the",
    "details back to you before you update the vendor record.",
]

PARA_SCOPE = [
    "Nothing else about the account moves. Your terms, your billing",
    "contacts and the open orders stay as they are.",
]

PARA_TIMING = [
    "Anything issued on the old details up to 4/30 still reaches us.",
    "After that the old account is closed, and a payment sent there",
    "comes back to your bank about a week later.",
]

PARA_APOLOGY = [
    "Sorry to add paperwork to your week. We are doing this by telephone",
    "with every customer, so you are not the only one being asked to make",
    "a call.",
]

CLOSING = "Thank you,"

# The four line block an external human signer uses, ending in a dialable
# number in the reserved 555-0100 to 555-0199 range. 555-0171 is unused
# elsewhere in the corpus. The number is a signature line and not the
# instruction: the instruction above says to use the number already on file.
SIGNATURE_LINES = [
    "Ines Halvorsen-Duque",
    "Accounts Receivable",
    "Larkseal",
    "Main line 555-0171",
]

# Section 2 of docs/email-header-realism.md fixes the removal notice. The check
# in validate_corpus.py runs on whitespace-collapsed text and looks for the
# product name, then at most 160 characters holding no "]", then the file name,
# so the name has to sit whole on one line and the wrap goes before it.
NOTICE_HEAD = "[Sentrywick Gateway removed 1 attachment:"
NOTICE_TAIL = "Details are in the message headers.]"

# Every phrase the record claims, checked against the rendered parts below so a
# line break can never quietly split one. The comparison is lowercased, the way
# the phrase pass in tools/validate_corpus.py matches, because the body writes
# two of these at the start of a sentence.
REQUIRED_PHRASES = [
    "new bank",
    "as discussed on tuesday's call",
    "call the number on file",
]


def notice_lines(record):
    """The section 2 removal notice, wrapped so no line passes 78 characters.

    The file name alone is 45 characters and the head is 41, so the notice
    needs three lines. The break goes before the name and after it, never
    inside it: the check collapses whitespace before it looks, so a break
    inside the name would put a space in the middle of it and the notice would
    stop naming the file at all.
    """
    return [NOTICE_HEAD,
            record["filename"] + " ({:,} bytes).".format(record["size"]),
            NOTICE_TAIL]


def plain_part(record):
    lines = [BANNER_PLAIN, ""]
    lines += [SALUTATION, ""]
    lines += PARA_OPENING + [""]
    lines += PARA_LETTER + [""]
    lines += PARA_CALLBACK + [""]
    lines += PARA_SCOPE + [""]
    lines += PARA_TIMING + [""]
    lines += PARA_APOLOGY + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE_LINES
    lines += [""] + notice_lines(record)
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def block_html(lines):
    """A run of short lines as one <p> with <br> between them."""
    block = [line + "<br>" for line in lines[:-1]]
    block[0] = "<p>" + block[0]
    block.append(lines[-1] + "</p>")
    return block


def html_part(record):
    # No image, no script, no form, no link and no hidden text: the HTML part
    # carries the same words on the same lines as the plain part, so a
    # part-to-part diff is empty and there is no content:html_hidden_text.
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#f3f4f6;">',
        BANNER_HTML,
        ('<div style="max-width:600px;margin:20px auto;padding:22px 26px;'
         'background-color:#ffffff;border:1px solid #dcdfe3;'),
        "  font-family:sans-serif;font-size:15px;line-height:1.5;",
        '  color:#222222;">',
        ('<p style="margin:0 0 18px 0;font-size:18px;font-weight:bold;'
         'color:#1b4f8a;">' + BRAND + "</p>"),
        "<p>" + SALUTATION + "</p>",
    ]
    lines += paragraph_html(PARA_OPENING)
    lines += paragraph_html(PARA_LETTER)
    lines += paragraph_html(PARA_CALLBACK)
    lines += paragraph_html(PARA_SCOPE)
    lines += paragraph_html(PARA_TIMING)
    lines += paragraph_html(PARA_APOLOGY)
    lines += ["<p>" + CLOSING + "</p>"]
    lines += block_html(SIGNATURE_LINES)
    notice = notice_lines(record)
    lines += ['<p style="font-size:12px;color:#6b6b6b;">' + notice[0]]
    lines += notice[1:-1]
    lines += [notice[-1] + "</p>"]
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


def build_eml(seed, record, store):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # RFC 8601 sec. 4: the gateway writes Authentication-Results above its
        # own trace field. All three checks pass, and they pass for the
        # vendor's own domain, because the vendor's own server sent this.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=quarantine",
        # RFC 7208 sec. 9.1. larkseal.example publishes "mx -all", so the
        # mechanism that matched is mx and the client address is the vendor's
        # own mail exchanger.
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        # Section 2 grammar, folded so no line passes 78 characters. The file
        # was archived to the document vault under normal policy, which is why
        # the action is quarantined rather than stripped and why playbook rule
        # 8 says the header proves nothing.
        "X-Sentrywick-Removed-Attachment:",
        '  filename="' + record["filename"] + '"; size=' + str(record["size"]) + ";",
        "  sha256=" + record["sha256"] + ";",
        "  action=" + record["action"] + "; type=" + record["type"]
        + "; reason=" + record["reason"],
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
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain_part(record)
    lines += [
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(record))
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------- self checks

# The content codes this record is allowed to produce. The generator runs every
# phrase list in spec/enums.json against both rendered parts, exactly the way
# tools/validate_corpus.py does, and fails on any code outside this set, so a
# stray "invoice" or "today" cannot reach the file.
ALLOWED_CONTENT_CODES = {
    "content:payment_change_request",
    "content:phone_verification_offered",
    "content:payment_request",
}
# The two lists validate_corpus.py skips, because their entries are single
# words and Spanish stopwords rather than a membership test.
PHRASE_PASS_SKIP = {"content:non_english_body", "content:instruction_to_ai"}


def phrase_hits(enums, plain_text, html_text):
    """{code: [phrase]} for every content list, the way the validator matches."""
    body = (plain_text + "\n" + html_text).lower()
    hits = {}
    for code, phrases in sorted((enums.get("content_phrases") or {}).items()):
        if code in PHRASE_PASS_SKIP:
            continue
        found = [phrase for phrase in phrases if phrase.lower() in body]
        if found:
            hits[code] = found
    return hits


def self_check(record, enums):
    plain_text = "\n".join(plain_part(record))
    html_text = "\n".join(html_part(record))
    for phrase in REQUIRED_PHRASES:
        for label, text in (("plain", plain_text.lower()), ("HTML", html_text.lower())):
            if phrase not in text:
                raise SystemExit(label + " part lost the phrase " + repr(phrase)
                                 + "; a line break may have split it")
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    for label, text in (("plain", plain_text), ("HTML", html_text)):
        if record["filename"] not in text:
            raise SystemExit(label + " part does not name the archived file")
    hits = phrase_hits(enums, plain_text, html_text)
    stray = set(hits) - ALLOWED_CONTENT_CODES
    if stray:
        code = sorted(stray)[0]
        raise SystemExit("the body carries " + code + " on " + repr(hits[code][0])
                         + ", which this record does not claim")
    for code in ALLOWED_CONTENT_CODES:
        if code not in hits:
            raise SystemExit("the body carries no phrase for " + code)
    return hits


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A careful accounts receivable note, addressed to Priya at the shared "
    "accounts payable mailbox. It opens 'Thank you for the time on Tuesday. "
    "As discussed on Tuesday's call,' and says Larkseal has moved its "
    "receivables to a 'new bank' with the change taking effect 5/1. The "
    "signed letter is attached: on the vendor's letterhead, signed by the "
    "controller on 4/20, carrying the bank name, the routing number and the "
    "last four digits of the account it replaces, so no bank number is "
    "written in the mail itself. The paragraph the record exists for asks "
    "accounts payable not to change anything from this message on its own, "
    "to 'call the number on file' for Larkseal rather than a number out of "
    "the mail, to ask for accounts receivable and to have the details read "
    "back before the vendor record is updated. Then: nothing else about the "
    "account moves, terms and billing contacts and open orders stay as they "
    "are; anything issued on the old details up to 4/30 still reaches the "
    "vendor and after that the old account is closed; and an apology for the "
    "paperwork, with the note that every customer is being telephoned. Do "
    "not use 'remit' or 'remittance' in the body, and no wording from the "
    "urgency, credential, payment timing, file share or secrecy phrase "
    "lists: the record carries content:payment_change_request and "
    "content:phone_verification_offered and nothing else from the prose. The "
    "subject keeps 'Signed remittance change letter', which the phrase pass "
    "does not read. No link. End both parts with the gateway notice that "
    "Larkseal_Remittance_Change_Letter_2026-04.pdf was archived to the "
    "vault. Sign with the four line block an external human signer uses: "
    "Ines Halvorsen-Duque, Accounts Receivable, Larkseal, and the main line "
    "555-0171."
)

LURE_SUMMARY = (
    "Following Tuesday's telephone call, the e-signature vendor's own "
    "accounts receivable team sends its signed bank change letter from its "
    "own domain and asks accounts payable to call the number on file and "
    "have the details read back before the vendor record is touched. The "
    "gateway archived the PDF to the document vault under normal policy."
)

MANIFEST_NOTES = (
    "Benign but escalate_expected is true: playbook rule 5 requires a phone "
    "confirmation of every bank change regardless of verdict, so the "
    "escalation reason is callback_verification and the action is "
    "verify_out_of_band_then_close. Shows that an archived attachment plus a "
    "bank change is not automatically fraud, and that verdict and escalation "
    "are separate decisions. It is the benign twin of 016, which reaches the "
    "same accounts payable mailbox with the same archived-PDF header and the "
    "same bank change and is fraud, and the difference is not in the body: "
    "016 carries a lookalike Reply-To and never invites a call, while 043 has "
    "no Reply-To and asks for the callback itself. Rendering note on one "
    "indicator, reported rather than fixed here: the gateway notice that "
    "section 2 of docs/email-header-realism.md requires in both body parts "
    "has to name the archived file, the file is "
    "Larkseal_Remittance_Change_Letter_2026-04.pdf, and 'remit' is a "
    "content:payment_request phrase and a substring of 'Remittance', so the "
    "phrase pass in tools/validate_corpus.py finds content:payment_request in "
    "the rendered body. The ground truth record lists it, because that is "
    "what a student's extractor produces. This indicator list does not, "
    "because content:payment_request carries polarity PB and adding it would "
    "take pressure to 2 against 1 decisive fact and move the authored tier "
    "from medium to hard. Records 032, 037 and 049 carry an Invoice_*.pdf "
    "stub and list content:payment_request for exactly this reason, so the "
    "omission here looks like an oversight rather than a decision, and it is "
    "left for the corpus owner to settle."
)

REFERENCE_SUMMARY = (
    "This is a real letter from Larkseal about their new bank, sent from "
    "their own domain after a call with accounts payable. Because it changes "
    "where money goes, our rule is a phone confirmation before anything is "
    "updated, which they asked for too."
)

GT_NOTES = (
    "Key facts a correct extractor produces: from_domain larkseal.example "
    "under the display name Larkseal Accounts Receivable, which "
    "data/display_names.json resolves to the Larkseal entry whose owner "
    "domain is larkseal.example, so display_name_mismatch is false; no "
    "Reply-To, so there is nothing to compare against From; spf=pass on "
    "larkseal.example, dkim=pass with d=larkseal.example s=ls2026, dmarc=pass "
    "with policy quarantine, so all three checks pass and the message is "
    "aligned; no link in either part; one removed-attachment header, "
    "Larkseal_Remittance_Change_Letter_2026-04.pdf, 112,480 bytes, action "
    "quarantined, reason archived-to-vault; no In-Reply-To, so the thread is "
    "new even though the body refers to a telephone call, which leaves no "
    "header behind. Received chain: LS-AR-0118.larkseal.example [192.0.2.51] "
    "submitted with ESMTPSA to mx-out.larkseal.example at 19:05:03 +0000, "
    "which handed off with ESMTPS and TLS1_3 to mx.pellgrave.example "
    "[10.20.4.10] at 14:05:06 -0500, delivered by LMTP to "
    "mailstore-01.pellgrave.example at 14:05:08 -0500; Date is 14:05:00 "
    "-0500, the same instant as 19:05:00 +0000 in the Message-ID. "
    "mailstore-01 is the store data/recipients.json gives ap@pellgrave.example, "
    "the same store 005 and 016 deliver to, because a mailbox lives on one "
    "store whatever path a message took. X-Sentrywick-External is yes, scan "
    "result clean, spam score 2.8. Body phrases the extractor keys on, "
    "present in both parts: 'new bank' (payment change request), and 'as "
    "discussed on Tuesday's call' and 'call the number on file' (phone "
    "verification offered). The prose is held clear of every other phrase "
    "list, and one more code still appears: content:payment_request on "
    "'remit', which occurs only inside the archived file name in the gateway "
    "notice, because 'remit' is a substring of 'Remittance' and section 2 of "
    "docs/email-header-realism.md requires the notice to name the file in "
    "both parts. It is recorded here because a student's extractor finds it; "
    "the manifest indicator list omits it, and that difference is written up "
    "in the manifest record's notes. Difficulty reason: the tier rule counts "
    "one decisive benign fact, an allowlisted sender with dmarc=pass, against "
    "one pressure fact, the payment change request, so pressure does not "
    "exceed decisive and the base tier is medium; there is no injection and "
    "the body only read is uncertain rather than the opposite of the verdict, "
    "so neither adjustment applies and it stays medium. The body only read is "
    "uncertain because the prose alone cannot settle it: a request to change "
    "where money goes reads like fraud, and the same paragraph asks for the "
    "telephone check that fraud never asks for. No injection. For the "
    "instructor: this is the benign twin of 016 and the record that separates "
    "verdict from escalation. Both messages reach the same shared payments "
    "mailbox, both carry an archived PDF, both ask for a bank change, and "
    "both pass all three authentication checks. 016 is fraud on one field a "
    "parser can quote, the lookalike Reply-To, and on the fact that it never "
    "invites a call; 043 has no Reply-To at all and asks for the callback "
    "itself. Playbook rules 1, 5 and 8 apply: three passes name a domain and "
    "prove nothing about intent, a bank change gets a telephone call to the "
    "number on file whatever the verdict, and a document archived to the "
    "vault is normal. Week 5 loop: check_sender_reputation returns trusted "
    "for larkseal.example, first seen 2023-02-20, 158 messages in 90 days and "
    "two prior reports both closed benign, which is real support for the "
    "benign verdict but decides nothing about the ask; check_urls has nothing "
    "to look up because there is no link; lookup_recipient shows ap@ is a "
    "shared mailbox that handles payments with three prior reports, all true "
    "positives, two of them tagged vendor-invoice-fraud. So the loop runs "
    "check_sender_reputation and lookup_recipient and stops on "
    "tools_exhausted, and no tool contradicts the body. "
    "recipient:prior_similar_report follows the prior_similar_report_rule: "
    "the payment change ask implies vendor-invoice-fraud and "
    "direct-deposit-change, the mailbox holds vendor-invoice-fraud, so that "
    "is the value, and it is context rather than evidence here. Full credit "
    "on the indicators criterion needs sender:allowlisted_domain and "
    "content:payment_change_request. Grading note: a student who calls this "
    "malicious because a vendor asked to be paid somewhere new has skipped "
    "the reputation record and the callback sentence, and a student who "
    "closes it benign without escalating has read the verdict rule and missed "
    "playbook rule 5, which is the more expensive mistake of the two."
)

MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:allowlisted_domain",
    "content:payment_change_request",
    "content:phone_verification_offered",
    "attachment:archived_to_vault:Larkseal_Remittance_Change_Letter_2026-04.pdf",
    "header:external_flag:yes",
    "url:none",
    "thread:new",
    "recipient:handles_payments",
    "recipient:shared_mailbox",
    "recipient:prior_similar_report",
]


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-22T14:05:00-05:00",
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
                 "dmarc_policy": "quarantine"},
        "indicators": [
            {"code": "auth:all_pass", "where": "Authentication-Results",
             "value": ("spf=pass smtp.mailfrom=larkseal.example; dkim=pass "
                       "header.d=larkseal.example header.s=ls2026 "
                       "header.i=@larkseal.example; dmarc=pass "
                       "header.from=larkseal.example policy.dmarc=quarantine")},
            {"code": "sender:allowlisted_domain", "where": "check_sender_reputation",
             "value": SENDER_DOMAIN},
            {"code": "content:payment_change_request", "where": "body",
             "value": "new bank"},
            {"code": "content:phone_verification_offered", "where": "body",
             "value": "as discussed on tuesday's call; call the number on file"},
            # Not in the manifest indicator list. The phrase "remit" reaches
            # the body only inside the archived file name in the gateway
            # notice, which section 2 requires in both parts; an extractor
            # finds it, so ground truth records it. See the module docstring.
            {"code": "content:payment_request", "where": "body", "value": "remit"},
            {"code": "attachment:archived_to_vault",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:shared_mailbox", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:prior_similar_report", "where": "lookup_recipient",
             "value": "vendor-invoice-fraud"},
        ],
        "required_indicators": ["sender:allowlisted_domain",
                                "content:payment_change_request"],
        "url_hosts": [],
        "attachment": {
            "filename": record["filename"],
            "size": record["size"],
            "sha256": record["sha256"],
            "action": record["action"],
            "type": record["type"],
            "reason": record["reason"],
        },
        "injection": None,
        "tool_expectations": {
            "check_sender_reputation": {
                "domain": SENDER_DOMAIN,
                "status": "trusted",
                "first_seen": "2023-02-20",
                "messages_90d": 158,
                "prior_reports": 2,
                "last_report_verdict": "benign",
                "last_report_date": "2026-03-26",
                "campaign_tag": None,
                "new_domain": False,
                "notes": "E-signature vendor; allowlisted.",
                "match_level": "domain",
            },
            "check_urls": {},
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
        "expected_loop": {"tools": ["check_sender_reputation", "lookup_recipient"],
                          "stop_reason": "tools_exhausted"},
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
    spec = load_json(SPEC_PATH)
    seed = spec["seed"]
    enums = load_json(os.path.join(CORPUS, "spec", "enums.json"))

    manifest = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            manifest = entry
            break
    if manifest is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if manifest["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if manifest["sender_address"] != SENDER or manifest["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("From does not match the manifest")
    if manifest["reply_to"] is not None:
        raise SystemExit("the manifest carries a Reply-To; this file writes none")
    if manifest["recipient"] != RECIPIENT or manifest["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if manifest["url_hosts"] != []:
        raise SystemExit("url_hosts do not match the manifest")
    if manifest["indicators"] != MANIFEST_INDICATORS:
        raise SystemExit("the manifest indicator list is not the one this file renders")

    stub = attachment_stub(seed)
    for key in ("filename", "size", "sha256", "action", "type", "reason"):
        if manifest["attachment"][key] != stub[key]:
            raise SystemExit("attachment " + key + " disagrees with attachments.json")

    self_check(stub, enums)
    store = mailstore(RECIPIENT)
    data = build_eml(seed, stub, store)
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
    if parsed["Reply-To"] is not None:
        raise SystemExit("the file carries a Reply-To header")

    manifest["body_brief"] = BODY_BRIEF
    manifest["lure_summary"] = LURE_SUMMARY
    manifest["notes"] = MANIFEST_NOTES
    write_json(SPEC_PATH, spec)

    truth = load_json(GT_PATH)
    records = truth["emails"]
    record = ground_truth(stub)
    for index, entry in enumerate(records):
        if entry["id"] == EMAIL_ID:
            records[index] = record
            break
    else:
        records.append(record)
        records.sort(key=lambda entry: entry["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
