#!/usr/bin/env python3
"""Regenerate 049-redcedar-renewal-ach-change.

Rebuilds instructor/exam-emails/049-redcedar-renewal-ach-change.eml byte for
byte from the corpus seed, refreshes the prose fields of its own manifest
record in spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json.

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
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Only the b= tag needs the block indexed stream, because a 2048 bit signature
is 256 bytes and one digest is 32. bh= is one digest and is taken as one.
Neither value verifies anything: no .example domain can publish a DKIM key,
and the course reads the gateway's Authentication-Results verdict rather than
recomputing a signature.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

Where this file goes, and why the ground truth says something else.

This is an exam-only email. The manifest gives it set "exam" and week 8, and
the design keeps exam mail out of corpus/emails/ entirely so that nothing a
student can reach holds it before the exam; the rendered message is written to
instructor/exam-emails/ instead. The ground truth record still has to carry a
"file" field, and spec/ground_truth.schema.json pins that field to the pattern
^emails/(teaching|batch|exam)/[0-9]{3}-[a-z0-9-]+\\.eml$, so the record says
emails/exam/049-redcedar-renewal-ach-change.eml: the slot this message would
occupy if exam mail shipped with the rest, which is the only string the schema
accepts. Two consequences are expected rather than wrong, and both are
warnings:

  * tools/validate_corpus.py reports "exam-only record has no file under
    emails/" when it runs over corpus/emails/, which is the state the design
    asks for.
  * pointed at the instructor folder with --emails, it reports that the ground
    truth file field and the path it found disagree, for the same reason.

Two values are read back from the data files rather than typed here:
data/recipients.json gives the one store that holds ap@pellgrave.example, and
data/attachments.json gives the removed file's name, size, action, type and
reason, with its sha256 checked against sha256("<seed>|<id>|<filename>")
before the header is written. The recipient is a shared mailbox rather than a
distribution list, so the LMTP hop names the recipient itself; the reporter
appears only in X-Sentrywick-Reported-By, because a shared mailbox is worked
by several people and the person who pressed report is not the addressee. The
store is mailstore-01, the same store 005, 016 and 031 delivered to, because a
mailbox lives on exactly one store whatever path a message took.

What this message is.

The safety vendor is Redcedar Safety Training at redcedarsafety.example, a
trusted domain the organization has heard from since 2022 and whose training
and support hosts are on the url allowlist. This message comes from
redcedar-safety.example, the same name with a hyphen dropped into it. The
attacker registered it the day the message was sent, published SPF and DKIM
for it, and sent the annual renewal invoice with a new bank account under it.
Because he owns the domain he sends from, all three authentication checks pass
and pass honestly; nothing in the header block is forged. Two facts settle it,
and both are deterministic:

  * The From domain is a hyphen-insertion look-alike of the vendor's real
    domain, and the display name "Redcedar Safety Training Accounts" claims a
    vendor that data/display_names.json owns to redcedarsafety.example and to
    no other domain.
  * The body asks accounts payable to send the renewal to a new ACH account,
    which the playbook answers with a callback on the number already on file,
    and the only number in this message is the attacker's.

The amounts are the tell that is not a tell: 14 technicians at last year's
rate, $6,300.00 in total, is the figure the vendor's own renewal carries. It
looks like knowledge of the account because it is; it just did not come from
the account.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are all present because the message crossed the
    border gateway. spf=pass on the envelope domain, dkim=pass with
    d=redcedar-safety.example s=k1, dmarc=pass with policy.dmarc=none, exactly
    as data/domain_policy.json publishes them for this domain. A p=none record
    that passes is not a missing record: dmarc=none would mean no record at
    all, and this domain has one.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 3.0 match the
    received_path_hint in the manifest. The score is nonzero because the body
    is money and bank numbers, and low because everything a filter can measure
    about this message is in order.
  * X-Sentrywick-Removed-Attachment records the renewal invoice with
    action=quarantined and reason=archived-to-vault, which is normal document
    policy at this gateway and not evidence of anything. Both body parts end
    with the notice naming the file, the way section 2 of
    docs/email-header-realism.md fixes it.
  * Message-ID names webmail.redcedar-safety.example, the host at the bottom of
    the Received chain, because that front end composed the message and
    stamped the id.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because the record carries neither sender:reply_to_differs nor
sender:reply_to_lookalike_domain and this attacker has no need of one, the
From domain being his already; no In-Reply-To and no References, so thread:new
holds and nothing in the file resolves against known_threads.json; no
X-Originating-IP, because the record carries no header:x_originating_ip and
this front end records the submitting host in its Received line instead; no
Thread-Topic, which section 9 gives to the organization's own submission host
and never to mail that arrived through the gateway; no X-Priority and no
Importance, because a renewal notice does not flag itself and this record
scores no urgency; no encoded-word Subject, because the whole message is
ASCII.

Run:  python3 corpus/tools/generators/gen_049_redcedar_renewal_ach_change.py
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

EMAIL_ID = "049-redcedar-renewal-ach-change"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
# Exam mail ships in the instructor package, never under corpus/emails/.
EML_PATH = os.path.join(BUILDER, "instructor", "exam-emails", EMAIL_ID + ".eml")
# The only path spec/ground_truth.schema.json accepts for the file field; see
# the module docstring.
GT_FILE_FIELD = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "accounts@redcedar-safety.example"
SENDER_DISPLAY = "Redcedar Safety Training Accounts"
# The envelope sender is the From mailbox. The attacker owns the domain he
# sends from, so there is no envelope-versus-author split anywhere in the file
# and no Reply-To to explain.
ENVELOPE_SENDER = SENDER
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

SUBJECT = "Annual training renewal invoice and updated ACH instructions"

# The look-alike, and the domain it imitates. One hyphen is the whole trick.
SENDER_DOMAIN = "redcedar-safety.example"
IMITATED_DOMAIN = "redcedarsafety.example"
IMITATED_VENDOR = "Redcedar Safety Training"
SENDER_HOST = "mail.redcedar-safety.example"
SENDER_SUBMIT_HOST = "webmail.redcedar-safety.example"
SENDER_IP = "203.0.113.173"
SENDER_SUBMIT_IP = "192.0.2.173"
DKIM_SELECTOR = "k1"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SCAN_RESULT = "clean"
SPAM_SCORE = "3.0"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 14:50 +0000 is the same instant as 09:50 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree.
DATE_HEADER = "Tue, 28 Apr 2026 09:50:00 -0500"
SUBMIT_STAMP = "Tue, 28 Apr 2026 14:50:03 +0000"
SUBMIT_UTC = "2026-04-28 14:50:03"
GATEWAY_STAMP = "Tue, 28 Apr 2026 09:50:06 -0500"
STORE_STAMP = "Tue, 28 Apr 2026 09:50:08 -0500"
MESSAGE_ID_STAMP = "20260428145000"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break. Only the HTML part needs the encoding here: the
# plain part is ASCII and every one of its lines is already inside 78, so it
# goes out as 7bit, the way 005 sends its plain part.
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


def attachment_stub(seed):
    """The removed file, from data/attachments.json, with its digest rechecked."""
    with open(ATTACHMENTS_PATH, encoding="utf-8") as handle:
        entries = json.load(handle)["attachments"]
    for entry in entries:
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

# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries two content codes, content:payment_change_request and
# content:payment_request, so no phrase from any other content list may appear
# anywhere in either decoded part. validate_corpus.py runs every list against
# the two decoded parts joined together and fails both a phrase with no code
# and a code with no phrase; check_phrases() below repeats the pass over the
# two lists this record does carry, so the recorded values cannot drift away
# from the rendered text.
#
#   The four phrases that carry payment_change_request are "updated ACH",
#   "new routing", "new account" and "new account number". "new bank" is
#   deliberately not among them: the bank is named on a line that reads
#   "Bank: Barrowfen Savings Bank", because a vendor writing a real ACH change
#   names the bank once and does not label it new.
#   The two that carry payment_request are "invoice" and "net 30". "invoice"
#   is in the prose and in the file name the gateway notice repeats, so the
#   code would apply even if the sentence were rewritten.
#   "past due", "remit" and "amount due" are out. Nothing here is late, and
#   "remit" would rule out "remittance" with it, since the pass matches
#   substrings.
#   "today", "urgent", "immediately", "by friday", "before monday" and the rest
#   of content:urgency_keywords are out. There is no deadline in this message
#   at all: it asks for the change before the next payment run, whenever that
#   is, which is how a real accounts clerk asks and which is also why the
#   record scores no pressure. "expires in" and "lapses on" are out too, so the
#   term is written as running through a date rather than expiring on one.
#   "sign in", "log in", "password" and "credentials" are out: nothing here
#   wants an identity, and the technicians hold certifications rather than
#   credentials.
#   "download", "shared with you" and the rest of content:file_share_lure are
#   out. The invoice is described as attached, and the gateway notice says the
#   gateway archived it.
#   "was changed" and "if you did not" (content:account_change_notice) are out.
#   This message is not a notice that something changed on an account of the
#   reader's; it is an instruction to change one. The sentence about the old
#   account says it is closed rather than that it was changed.
#   "wire" (content:banking_instruction) is out, and so is every word that
#   contains it. ACH is the only rail named.
#   "call me" and "call the number on file" are out. The telephone number and
#   extension in the signature are signature lines, not an invitation, and that
#   is the point: the playbook's answer to a bank change is a callback on the
#   number already on file, which is not this one.
#   "confirm which technicians" (content:data_request) is out; the count of
#   technicians is stated, not asked for.
#   "confidential", "quietly", "reply by email", "personal address" and every
#   content:payment_timing_request phrase are out as well. Nothing asks for a
#   payment to move earlier or later; the ask is only about where the money
#   lands.
#
# The register is a vendor's accounts clerk writing to a payables department
# about a renewal she expects them to be waiting for: polite, specific about
# numbers, and offering to reissue the document if it does not match their
# purchase order. She never explains why the bank changed, because a real one
# usually does not.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

SALUTATION = "Hello,"

PARA_RENEWAL = [
    "The annual safety training renewal for Pellgrave Mechanical Group is",
    "ready and the invoice is attached. Renewal RC-2026-0412 covers 14",
    "technicians at last year's rate of $450.00 each, so the total is",
    "$6,300.00, net 30. The term runs 1 June 2026 through 31 May 2027.",
]

# The sentence the manifest fixes, word for word, broken after "the" so that
# the HTML copy of it, which carries a "<p>" and a "</p>" the plain copy does
# not, still fits inside one quoted-printable line.
PARA_ACH = [
    "Please note our updated ACH instructions: payments now go to the",
    "account below.",
]

# The three lines a vendor file is updated from. The routing number begins with
# 55, which no real routing number can, and the account number is invented;
# both sit inside the fiction the way the ones in 016, 021 and 031 do. The
# account opens 6300, which is the renewal total read back at accounts payable,
# and that is the small trick of this message: the numbers it shows are numbers
# they already recognise.
BANK_LINES = [
    "Bank: Barrowfen Savings Bank",
    "New routing number: 555014820",
    "New account number: 6300 1428 0117",
]

PARA_PREVIOUS = [
    "The previous account is closed to incoming transfers, so anything",
    "sent there comes back to us about ten days later.",
]

PARA_UPDATE = [
    "Please update the vendor record for Redcedar Safety Training with",
    "these details before your next payment run, and confirm by reply",
    "once the change is on file.",
]

PARA_REISSUE = [
    "If anything on the renewal does not match your purchase order, let",
    "me know and I will have it reissued.",
]

CLOSING = "Thank you,"

# A person and a department, with the extension a payables clerk would dial
# back on. 555-0155 is inside the 555-0100 through 555-0199 fictional range,
# and it is not a number the organization holds for the real vendor.
SIGNATURE_LINES = [
    "Nerys Calloway",
    "Accounts, Redcedar Safety Training",
    "555-0155 ext. 118",
]

NOTICE_HEAD = "[Sentrywick Gateway removed 1 attachment:"
NOTICE_TAIL = "Details are in the message headers.]"

# The phrases from spec/enums.json the ground truth records for the two content
# codes, written with the body's own capitalisation. check_phrases() rebuilds
# both sets from the rendered parts and fails if either disagrees, so a recorded
# value can never name a phrase the text does not carry, or miss one it does.
PAYMENT_CHANGE_PHRASES = ["updated ACH", "new routing", "new account",
                          "new account number"]
PAYMENT_REQUEST_PHRASES = ["invoice", "net 30"]


def notice_lines(record):
    """The section 2 removal notice, wrapped so no source line passes 78.

    The check in validate_corpus.py runs on whitespace-collapsed text, so the
    break between the file name and its size is free; what it will not accept
    is a "]" between the product name and the file name, which is why the
    gateway banner earlier in the part cannot satisfy it by accident.
    """
    return [NOTICE_HEAD + " " + record["filename"],
            "({:,} bytes). ".format(record["size"]) + NOTICE_TAIL]


def plain_part(record):
    lines = [BANNER_PLAIN, ""]
    lines += [SALUTATION, ""]
    lines += PARA_RENEWAL + [""]
    lines += PARA_ACH + [""]
    lines += BANK_LINES + [""]
    lines += PARA_PREVIOUS + [""]
    lines += PARA_UPDATE + [""]
    lines += PARA_REISSUE + [""]
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
    # No wrapper div, no table, no button, no image and no link: this sender
    # has nothing to dress up and no product to brand the mail with, and the
    # record carries url:none, so neither part may hold a link at all. The two
    # parts carry the same words in the same order, so a part-to-part diff is
    # empty.
    lines = ["<html>", "<body>", BANNER_HTML]
    lines += ["<p>" + SALUTATION + "</p>"]
    lines += paragraph_html(PARA_RENEWAL)
    lines += paragraph_html(PARA_ACH)
    lines += block_html(BANK_LINES)
    lines += paragraph_html(PARA_PREVIOUS)
    lines += paragraph_html(PARA_UPDATE)
    lines += paragraph_html(PARA_REISSUE)
    lines += ["<p>" + CLOSING + "</p>"]
    lines += block_html(SIGNATURE_LINES)
    # The removal notice, with the opening tag on a source line of its own so
    # that no line of it needs a soft break and the file name is never split
    # across one. The decoded HTML carries the tag and the notice on separate
    # lines; both the gateway-notice check and html_to_text read
    # whitespace-collapsed text, so the two parts still say the same sentence.
    notice = notice_lines(record)
    lines += ['<p style="font-size:12px;color:#6b6b6b;">',
              notice[0], notice[1] + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


def qp_tokens(line):
    """One logical line as a list of quoted-printable atoms.

    An atom is one printable ASCII character or one three-character "=XX"
    escape, so a wrap between atoms can never split an escape. The text is
    encoded as UTF-8 first, because the part declares charset=utf-8; every byte
    in this message happens to be ASCII, so the two agree here, and the encoder
    stays correct if a later edit adds a non-ASCII character.
    """
    out = []
    for byte in line.encode("utf-8"):
        if byte == 0x3D:
            out.append("=3D")
        elif 0x20 <= byte <= 0x7E:
            out.append(chr(byte))
        else:
            out.append("=%02X" % byte)
    return out


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks.

    RFC 2045 sec. 6.7: an encoded line is at most 76 characters counting the
    trailing "=", and white space may not sit at the end of an encoded line, so
    a break that would land after a space carries the space to the next line
    instead. Decoding removes the soft break, which puts the space back where
    it was.
    """
    out = []
    current = ""
    for atom in qp_tokens(line):
        if len(current) + len(atom) > QP_MAX - 1:
            stripped = current.rstrip(" \t")
            if stripped:
                carry = current[len(stripped):]
                current = stripped
            else:
                carry = ""
            out.append(current + "=")
            current = carry
        current += atom
    out.append(current)
    return out


def encode(lines):
    out = []
    for line in lines:
        out += qp_wrap(line)
    return out


def build_eml(seed, record):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_SUBMIT_HOST + ">")
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
        # look-alike domain, because the attacker owns it and published records
        # for it. That is the lesson: a pass names a domain, not a company.
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
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        # Section 2 grammar. The document was archived to the file vault under
        # normal policy, which is why the action is quarantined rather than
        # stripped and why nothing about this header is a finding.
        'X-Sentrywick-Removed-Attachment: filename="' + record["filename"] + '";',
        "  size=" + str(record["size"]) + ";",
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


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A vendor's accounts clerk writing to a payables department about a "
    "renewal they are expecting: polite, specific about numbers, no deadline "
    "and no urgency word anywhere. It opens 'Hello,' and says the annual "
    "safety training renewal for Pellgrave Mechanical Group is ready and the "
    "invoice is attached, that Renewal RC-2026-0412 covers 14 technicians at "
    "last year's rate of $450.00 each, so the total is $6,300.00, net 30, and "
    "that the term runs 1 June 2026 through 31 May 2027. Then the line the "
    "record turns on, word for word: 'Please note our updated ACH "
    "instructions: payments now go to the account below.' Three lines follow, "
    "'Bank: Barrowfen Savings Bank', 'New routing number: 555014820' and 'New "
    "account number: 6300 1428 0117'. Do not write 'new bank': the phrase "
    "list would score it and the bank is named once, unlabelled, the way a "
    "real ACH change names it. Say the previous account is closed to incoming "
    "transfers and anything sent there comes back about ten days later; do not "
    "write 'was changed'. Ask accounts payable to update the vendor record for "
    "Redcedar Safety Training before their next payment run and to confirm by "
    "reply once the change is on file, and offer to reissue the document if "
    "it does not match their purchase order. End both parts with the gateway "
    "notice that Renewal_Invoice_2026.pdf was archived to the vault. Close "
    "'Thank you,' and sign 'Nerys Calloway' over 'Accounts, Redcedar Safety "
    "Training' and the number "
    "555-0155 ext. 118, which is not the number the organization holds for the "
    "real vendor. No link, no Reply-To, no thread."
)

LURE_SUMMARY = (
    "A hyphen-insertion copy of the safety vendor's domain, "
    "redcedar-safety.example against the real redcedarsafety.example, sends "
    "the annual renewal invoice for $6,300.00 and says payments now go to a new "
    "account at a different bank, giving a new routing and account number. The "
    "attacker owns the look-alike domain and publishes SPF and DKIM for it, so "
    "all three authentication checks pass, and the amount matches last year's "
    "renewal because he read it from a leaked copy of the invoice."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain "
    "redcedar-safety.example, which is redcedarsafety.example with a hyphen "
    "inserted into the vendor's name, so the From domain is a look-alike of a "
    "domain the corpus knows and trusts; display name 'Redcedar Safety "
    "Training Accounts', which normalizes onto the data/display_names.json "
    "entry 'Redcedar Safety Training', a vendor whose owner_domains list holds "
    "only redcedarsafety.example, so the display-name check reports "
    "sender:display_name_claims_vendor; no Reply-To, so there is no reply "
    "mismatch to find and the From address is the only sender fact; spf=pass "
    "on redcedar-safety.example, dkim=pass with d=redcedar-safety.example "
    "s=k1, dmarc=pass with policy.dmarc=none, all three honest, because the "
    "attacker owns the domain he sends from and data/domain_policy.json shows "
    "it publishing mx -all and a p=none record; no link in either part; one "
    "removed-attachment header, Renewal_Invoice_2026.pdf, 39,120 bytes, action "
    "quarantined, reason archived-to-vault, which is normal document policy at "
    "this gateway and not a finding; no In-Reply-To, so the message opens a "
    "thread. Received chain: webmail.redcedar-safety.example [192.0.2.173] "
    "submitted with ESMTPSA to mail.redcedar-safety.example at 14:50:03 +0000, "
    "which handed off with ESMTPS and TLS1_3 to mx.pellgrave.example "
    "[10.20.4.10] at 09:50:06 -0500, delivered by LMTP to "
    "mailstore-01.pellgrave.example at 09:50:08 -0500; Date is 09:50:00 -0500, "
    "the same instant as 14:50:00 +0000 in the Message-ID, whose host is the "
    "front end that composed the message. mailstore-01 is the store "
    "data/recipients.json gives ap@pellgrave.example, the same store 005, 016 "
    "and 031 delivered to, because a mailbox lives on one store whatever path "
    "a message took. X-Sentrywick-External is yes, scan result clean, spam "
    "score 3.0. Body phrases the extractor keys on, present in both parts: "
    "'updated ACH', 'new routing', 'new account' and 'new account number', all "
    "content:payment_change_request, and 'invoice' and 'net 30', both "
    "content:payment_request. No other content code applies, and the wording "
    "is held clear of every other phrase list on purpose: there is no deadline "
    "and no urgency word, the old account is described as closed rather than "
    "as changed, so content:account_change_notice does not apply, and the "
    "telephone number in the signature is a signature line rather than an "
    "invitation to call, so content:phone_verification_offered does not apply "
    "either. Difficulty reason: the tier rule counts two decisive facts "
    "(sender:lookalike_domain and sender:display_name_claims_vendor) against "
    "no pressure fact, so the base tier is easy; the body-only read is "
    "uncertain rather than opposed to the verdict, so no step is added, and "
    "there is no injection. For the instructor: this is the plain vendor fraud "
    "case on the exam, and it is deliberately the one an ungrounded reader can "
    "still get wrong in the other direction. Nothing in the body is alarming. "
    "The renewal is real, the amount is right, the rate matches last year, and "
    "the invoice the gateway archived is a normal PDF. Every fact that decides "
    "it sits in the From line and in the vendor tables: the hyphen, and a "
    "display name that claims a company owning a different domain. Three "
    "authentication passes appear on it, which is the point of pairing it with "
    "048 in the same exam: 048 fails every check while forging the vendor's "
    "real domain, and this one passes every check from a domain that merely "
    "looks like it. Authentication proved the domain in both cases and proved "
    "nothing about the company. Tools: check_sender_reputation returns unknown "
    "for redcedar-safety.example, first seen 2026-04-28, one message in 90 "
    "days, no prior reports and new_domain true, so the domain is a day old at "
    "the corpus clock, while redcedarsafety.example is trusted and has been "
    "since 2022; check_urls has nothing to look up because there is no link; "
    "lookup_recipient shows ap@ is a shared mailbox that handles payments with "
    "three prior reports, all true positives, two of them tagged "
    "vendor-invoice-fraud. The loop therefore runs check_sender_reputation and "
    "lookup_recipient and stops on tools_exhausted. "
    "recipient:prior_similar_report follows the prior_similar_report_rule: the "
    "payment change ask implies vendor-invoice-fraud and "
    "direct-deposit-change, the mailbox holds vendor-invoice-fraud, so that is "
    "the value. Full credit on the indicators criterion needs "
    "sender:lookalike_domain and content:payment_change_request. Expected "
    "action: escalate_incident under financial_or_endpoint_impact, because a "
    "new bank account aimed at an accounts payable mailbox is money about to "
    "leave. partner_account_compromise does not apply: nothing of Redcedar's "
    "is broken, and the callback the playbook asks for goes to the number "
    "already on file rather than to the 555-0155 in this signature. Grading "
    "note: a student who closes this benign because the authentication passes "
    "has read the verdict line and not the address, and a student who calls it "
    "malicious without naming the From domain or the display name has guessed."
)

REFERENCE_SUMMARY = (
    "This invoice comes from a look-alike of Redcedar's domain and tries to "
    "redirect our payment to a new bank account. Do not pay it; accounts "
    "payable will confirm the real renewal with Redcedar by phone."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": GT_FILE_FIELD,
        "set": "exam",
        "weeks": [8],
        "date": "2026-04-28T09:50:00-05:00",
        "verdict": "malicious",
        "category": "vendor_fraud",
        "difficulty": "easy",
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
                 "dmarc_policy": "none"},
        "indicators": [
            {"code": "auth:all_pass", "where": "Authentication-Results",
             "value": ("spf=pass smtp.mailfrom=redcedar-safety.example; "
                       "dkim=pass header.d=redcedar-safety.example header.s=k1 "
                       "header.i=@redcedar-safety.example; dmarc=pass "
                       "header.from=redcedar-safety.example policy.dmarc=none")},
            {"code": "sender:lookalike_domain", "where": "From",
             "value": IMITATED_DOMAIN},
            {"code": "sender:display_name_claims_vendor", "where": "From",
             "value": IMITATED_VENDOR},
            {"code": "sender:first_seen", "where": "check_sender_reputation",
             "value": "2026-04-28"},
            {"code": "content:payment_change_request", "where": "body",
             "value": "; ".join(PAYMENT_CHANGE_PHRASES)},
            {"code": "content:payment_request", "where": "body",
             "value": "; ".join(PAYMENT_REQUEST_PHRASES)},
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
        "required_indicators": ["sender:lookalike_domain",
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
                "status": "unknown",
                "first_seen": "2026-04-28",
                "messages_90d": 1,
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
        "escalation_reasons": ["financial_or_endpoint_impact"],
        "recommended_action": "escalate_incident",
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


def check_phrases(parsed):
    """The two content lists, run both ways against the rendered parts.

    validate_corpus.py runs every list in spec/enums.json over the decoded body
    and fails a phrase whose code the record does not carry as loudly as a code
    whose phrase is missing. This repeats that pass for the two lists this
    record does carry, so the recorded values cannot name a phrase the text
    lacks or miss one it holds, and it names the codes whose phrases must stay
    out of the text so a later edit that reaches for one fails here first.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        phrase_lists = json.load(handle)["content_phrases"]
    body = ""
    for part in parsed.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            body += part.get_content() + "\n"
    lowered = body.lower()
    recorded = {"content:payment_change_request": PAYMENT_CHANGE_PHRASES,
                "content:payment_request": PAYMENT_REQUEST_PHRASES}
    for code, listed in recorded.items():
        found = {phrase for phrase in phrase_lists[code] if phrase.lower() in lowered}
        said = {phrase.lower() for phrase in listed}
        if said != found:
            raise SystemExit(code + ": the body carries " + repr(sorted(found))
                             + " but the record records " + repr(sorted(said)))
    # Every other list, except the two the phrase pass skips, has to be empty
    # against this body.
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    for code, listed in phrase_lists.items():
        if code in recorded or code in skip:
            continue
        for phrase in listed:
            if phrase.lower() in lowered:
                raise SystemExit("body carries the phrase " + repr(phrase)
                                 + ", whose code " + code + " this record does not list")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    manifest = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            manifest = entry
            break
    if manifest is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if manifest["sender_address"] != SENDER or manifest["reply_to"] is not None:
        raise SystemExit("From or Reply-To does not match the manifest")
    if manifest["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if manifest["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if manifest["recipient"] != RECIPIENT or manifest["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if manifest["date"] != "2026-04-28T09:50:00-05:00":
        raise SystemExit("date does not match the manifest")
    if manifest["url_hosts"] != []:
        raise SystemExit("url_hosts do not match the manifest")
    if manifest["injection"] is not None:
        raise SystemExit("the manifest carries an injection; this generator renders none")

    stub = attachment_stub(seed)
    for key in ("filename", "size", "sha256", "action", "type", "reason"):
        if manifest["attachment"][key] != stub[key]:
            raise SystemExit("attachment " + key + " disagrees with attachments.json")

    data = build_eml(seed, stub)
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
    if str(parsed["From"]) != SENDER_DISPLAY + " <" + SENDER + ">":
        raise SystemExit("unfolded From is " + repr(str(parsed["From"])))
    if parsed["Reply-To"] is not None:
        raise SystemExit("a Reply-To was written; this record has none")
    if parsed["In-Reply-To"] is not None or parsed["References"] is not None:
        raise SystemExit("a thread header was written; this record is thread:new")
    check_phrases(parsed)

    manifest["body_brief"] = BODY_BRIEF
    manifest["lure_summary"] = LURE_SUMMARY
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
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
