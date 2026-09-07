#!/usr/bin/env python3
"""Regenerate 031-slatemoor-invoice-ach-update.

Rebuilds emails/batch/031-slatemoor-invoice-ach-update.eml byte for byte from
the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
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
is 256 bytes and one digest is 32. bh= is one digest and is taken as one,
the form gen_016 uses. Neither value verifies anything: no .example domain can
publish a DKIM key, and the course reads the gateway's Authentication-Results
verdict rather than recomputing a signature.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

The MIME boundary prefix is "=_part_" rather than the "=_swk_" that 005 and
016 carry. That is deliberate: those two messages leave the parts supplier's
own mail system, and this one leaves a look-alike domain registered a day
before the corpus clock and running whatever generic library came with its
hosting. The prefix is not an indicator and no tool reads it; it is texture,
and it is the one place where the attacker's stack is visibly not the
vendor's.

Two values are read back from the data files rather than typed here:
data/recipients.json gives the one store that holds ap@pellgrave.example, and
data/attachments.json gives the removed file's name, size, action, type and
reason, with its sha256 checked against sha256("<seed>|<id>|<filename>")
before the header is written. The recipient is a shared mailbox rather than a
distribution list, so the LMTP hop names the recipient itself; the reporter
appears only in X-Sentrywick-Reported-By, because a shared mailbox is worked
by several people and the person who pressed report is not the addressee. The
store is mailstore-01, the same store 005 and 016 delivered to, because a
mailbox lives on exactly one store whatever path a message took.

What this message is.

This is the plain vendor fraud case, and it is plain on purpose. The attacker
did not break into anything. He registered slatemoor-supply.example, a hyphen
inserted into the parts supplier's slatemoorsupply.example, published SPF and
DKIM for it, and sent a bilingual accounts receivable notice that attaches a
bill and moves the bank account. Because he owns the domain he sends from, all
three authentication checks pass and pass honestly; the header block is not
forged anywhere. Two facts settle it, and both are deterministic:

  * The From domain is a look-alike of the supplier's real domain, and the
    display name "Slatemoor Industrial Supply AR" claims a vendor that
    data/display_names.json owns to slatemoorsupply.example and not to this
    one.
  * The body asks accounts payable to send future money to a new ACH account,
    which the playbook answers with a callback rule no email can satisfy.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are all present because the message crossed the
    border gateway. spf=pass on the envelope domain, dkim=pass with
    d=slatemoor-supply.example s=k1, dmarc=pass with policy.dmarc=none,
    exactly as data/domain_policy.json publishes them for this domain. A
    p=none record that passes is not a missing record: dmarc=none would mean
    no record at all, and this domain has one.
  * Subject is an RFC 2047 encoded word because the Spanish half carries an
    ordinal sign, "n" with the masculine ordinal indicator, which is not
    ASCII. It is written as two adjacent encoded words rather than one,
    because one word for the whole line would be 76 characters and RFC 2047
    sec. 2 caps an encoded word at 75. Adjacent encoded words separated by
    folding white space decode with that white space removed (sec. 6.2), so
    the second word opens with an encoded space and the two decode to one
    line.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 3.2 match the
    received_path_hint in the manifest. The score is nonzero because the body
    is money and bank numbers, and low because everything a filter can measure
    about this message is in order.
  * X-Sentrywick-Removed-Attachment records the bill with action=quarantined
    and reason=archived-to-vault, which is normal document policy at this
    gateway and not evidence of anything. 016 and 043 carry the same header on
    a compromised-partner message and on a benign one. Both body parts end
    with the notice naming the file, the way section 2 of
    docs/email-header-realism.md fixes it.
  * Message-ID names webmail.slatemoor-supply.example, the host at the bottom
    of the Received chain, because that front end is what composed the message
    and stamped the id.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because the record carries neither sender:reply_to_differs nor
sender:reply_to_lookalike_domain and this attacker has no need of one, the
From domain being his already; no In-Reply-To and no References, so thread:new
holds and nothing in the file resolves against known_threads.json; no
X-Originating-IP, because the record carries no header:x_originating_ip and
this front end records the submitting host in its Received line instead; no
Thread-Topic, which section 9 gives to the organization's own submission host
and never to mail that arrived through the gateway; no X-Priority and no
Importance, because a receivables notice does not flag itself and this record
scores no urgency.

Two departures from the manifest as authored, both recorded rather than
hidden. Neither touches a semantic field.

  1. The manifest's subject field held the wire form, the encoded word itself.
     tools/validate_corpus.py compares a record's subject with the value
     email.policy.default hands back for the header, which is the decoded
     text, and it also requires the manifest and the ground truth to agree on
     that field. Both cannot hold at once while the manifest carries the
     encoded form, so main() writes the decoded line into the manifest and the
     ground truth carries the same string. Nothing is lost: the record's
     received_path_hint already states that the subject is an encoded word and
     gives the decoded reading, and header:encoded_word_subject is checked
     against the raw header in the rendered file, not against this field.
  2. The word "invoice" does not appear in either body part, which is the one
     place the wording departs from the brief. "invoice" is a
     content:payment_request phrase in spec/enums.json, this record carries no
     payment_request code, and validate_corpus.py fails a phrase whose code is
     absent as loudly as a code whose phrase is absent. The Spanish half says
     "factura", which is on no phrase list, and the English half says "bill".
     The subject keeps "Invoice 44170-118", because the phrase pass reads the
     decoded body parts and not the header. The ask itself is unchanged.

Run:  python3 corpus/tools/generators/gen_031_slatemoor_invoice_ach_update.py
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

EMAIL_ID = "031-slatemoor-invoice-ach-update"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "ar@slatemoor-supply.example"
SENDER_DISPLAY = "Slatemoor Industrial Supply AR"
# The envelope sender is the From mailbox. The attacker owns the domain he
# sends from, so there is no envelope-versus-author split anywhere in the file
# and no Reply-To to explain.
ENVELOPE_SENDER = SENDER
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

# The Subject on the wire, and the same line as a reader and a parser see it.
# RFC 2047 sec. 2 caps one encoded word at 75 characters and the whole line
# needs 76, so it is written as two adjacent words; sec. 6.2 removes the
# folding white space between them, which is why the second word opens with an
# encoded space.
SUBJECT_WORD_1 = "=?UTF-8?Q?Factura_n=C2=BA_44170-118_y_nuevos_datos_ACH?="
SUBJECT_WORD_2 = "=?UTF-8?Q?_/_Invoice_44170-118?="
SUBJECT = "Factura nº 44170-118 y nuevos datos ACH / Invoice 44170-118"

# The look-alike, and the domain it imitates. One hyphen is the whole trick.
SENDER_DOMAIN = "slatemoor-supply.example"
IMITATED_DOMAIN = "slatemoorsupply.example"
SENDER_HOST = "mail.slatemoor-supply.example"
SENDER_SUBMIT_HOST = "webmail.slatemoor-supply.example"
SENDER_IP = "203.0.113.165"
SENDER_SUBMIT_IP = "192.0.2.165"
DKIM_SELECTOR = "k1"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SCAN_RESULT = "clean"
SPAM_SCORE = "3.2"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 20:33 +0000 is the same instant as 15:33 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree.
DATE_HEADER = "Wed, 22 Apr 2026 15:33:00 -0500"
SUBMIT_STAMP = "Wed, 22 Apr 2026 20:33:03 +0000"
SUBMIT_UTC = "2026-04-22 20:33:03"
GATEWAY_STAMP = "Wed, 22 Apr 2026 15:33:06 -0500"
STORE_STAMP = "Wed, 22 Apr 2026 15:33:08 -0500"
MESSAGE_ID_STAMP = "20260422203300"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break. Both parts are quoted-printable here, because the
# Spanish text is not ASCII and the file has to stay seven-bit clean.
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
# content:non_english_body, so no phrase from any other content list may appear
# anywhere in either decoded part. validate_corpus.py runs every list against
# the two decoded parts joined together and fails both a phrase with no code
# and a code with no phrase. content:non_english_body is skipped by that pass,
# because its list is Spanish stopwords that sit inside ordinary English words;
# it is a judgment about the message, and the message opens in Spanish, runs
# its whole ask in Spanish first, and repeats it in English underneath.
#
#   The five phrases that carry payment_change_request are "nueva cuenta",
#   "new ACH", "new bank", "new routing" and "new account number", each sitting
#   whole on one line of both parts.
#   "invoice" is out, and it is the one place this file departs from the
#   wording the manifest's body_brief suggested. "invoice" is a
#   content:payment_request phrase and this record carries no payment_request
#   code, so the Spanish half says "factura", which is on no list, and the
#   English half says "bill". The subject still reads "Invoice 44170-118",
#   because the phrase pass reads the decoded body parts and not the header.
#   "past due", "remit", "amount due", "payment is due", "net 15" and "net 30"
#   are out for the same reason, and "remit" rules out "remittance" and the
#   Spanish "remite" and "remitir" with it, since the pass matches substrings.
#   "today" is out. The Spanish "hoy" carries the same meaning in the sentence
#   the brief fixes, "A partir de hoy", and is not on any list; the English
#   half says "Effective with this message" rather than repeating it.
#   "urgent" is out, and so is the Spanish "urgente" that contains it.
#   "credit hold", "immediately", "as soon as possible", "by friday" and the
#   rest of content:urgency_keywords are out. There is no deadline in this
#   message at all: it asks for the change before the next payment run,
#   whenever that is, which is how a real receivables clerk asks and which is
#   also why the record scores no pressure.
#   "sign in", "log in", "password" and "credentials" are out: nothing here
#   wants an identity.
#   "download", "shared with you" and the rest of content:file_share_lure are
#   out. The bill is described as attached, and the gateway notice says the
#   gateway removed it.
#   "was changed" and "if you did not" (content:account_change_notice) are out.
#   This message is not a notice that something changed on an account of the
#   reader's; it is an instruction to change one.
#   "call me" and "call the number on file" are out. The telephone number in
#   the signature is a signature line, not an invitation, and that is the
#   point: the playbook's answer to a bank change is a callback on the number
#   already on file, which is not this one.
#   "wire", "gift card", "confidential", "quietly", "personal address", "email
#   only", "reply by email" and every content:payment_timing_request phrase are
#   out as well. Nothing asks for a payment to move earlier or later; the ask
#   is only about where the money lands.
#
# The register is a receivables department writing to a payables department in
# two languages, which is what the supplier's real team does; the manifest says
# so, and that is why the Spanish is not a tell. It is polite, unhurried and
# specific about numbers, and it never explains itself.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

SALUTATION = "Buenas tardes:"

PARA_ES_BILL = [
    "Adjunto la factura nº 44170-118 de la cuenta 44170, con los",
    "términos habituales.",
]

PARA_ES_ACH = [
    "A partir de hoy, los pagos se envían a la nueva cuenta ACH indicada",
    "abajo. Los datos bancarios anteriores ya no reciben transferencias, y",
    "lo que se envíe allí nos vuelve con dos semanas de retraso.",
]

PARA_ES_ASK = [
    "Le rogamos actualizar la ficha del proveedor 44170 con estos datos",
    "antes del próximo envío de pagos, y confirmarnos por respuesta",
    "cuando quede hecho.",
]

# The hinge between the two halves. Both parts carry the same words on the same
# line; the plain part sets it off with dashes and the HTML part with a
# paragraph of its own, which is as close as the two renderings get.
SEPARATOR = "-- English follows --"

# Broken after "usual" rather than run to the full stop, so that the HTML copy
# of the same sentence, which carries a "<p>" and a "</p>" the plain copy does
# not, still fits inside one quoted-printable line and the closing tag is not
# split across a soft break. The words are identical in both parts.
PARA_EN_BILL = [
    "Attached is our bill 44170-118 for account 44170, on the usual",
    "terms.",
]

PARA_EN_ACH = [
    "Effective with this message, payments go to the new ACH account shown",
    "below. The previous bank details no longer receive transfers, and",
    "anything sent there comes back to us about two weeks later.",
]

PARA_EN_ASK = [
    "Please update the vendor record for 44170 with these details before",
    "your next payment run, and confirm by reply when it is done.",
]

# The four lines a vendor file is updated from. The routing number begins with
# 55, which no real routing number can, and the account number is invented;
# both sit inside the fiction the way the ones in 016 and 021 do. The account
# number opens 4471 0118, which is the account and the document number read
# back at accounts payable, and that is the whole trick of this message: every
# number in it is a number they already recognise.
BANK_LINES = [
    "New ACH details / Nueva cuenta ACH",
    "New bank / Banco nuevo: Halbrook Savings Bank",
    "New routing number / Número de ruta nuevo: 555018619",
    "New account number / Número de cuenta nuevo: 4471 0118 2265",
]

PARA_THANKS = ["Gracias por su ayuda. / Thank you for your help."]

# A department signature, not a person's: there is no name to ask for and no
# extension to dial back on, which is what the callback rule is for. 555-0182
# is inside the 555-0100 through 555-0199 fictional range, and it is not the
# 555-0147 that data/recipients.json and 005 put on the real supplier.
SIGNATURE_LINES = [
    "Cuentas por cobrar / Accounts Receivable",
    "Slatemoor Industrial Supply",
    "555-0182",
]

NOTICE_HEAD = "[Sentrywick Gateway removed 1 attachment:"
NOTICE_TAIL = "Details are in the message headers.]"

# The phrases from spec/enums.json the ground truth records for
# content:payment_change_request. main() rebuilds this set from the rendered
# parts and fails if the two disagree, so the recorded value can never drift
# away from the text.
PAYMENT_CHANGE_PHRASES = ["nueva cuenta", "new ACH", "new bank", "new routing",
                          "new account number"]


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
    lines += PARA_ES_BILL + [""]
    lines += PARA_ES_ACH + [""]
    lines += PARA_ES_ASK + [""]
    lines += [SEPARATOR, ""]
    lines += PARA_EN_BILL + [""]
    lines += PARA_EN_ACH + [""]
    lines += PARA_EN_ASK + [""]
    lines += BANK_LINES + [""]
    lines += PARA_THANKS + [""]
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
    # has nothing to dress up and no product to brand the mail with. The two
    # parts carry the same words in the same order, so a part-to-part diff is
    # empty.
    lines = ["<html>", "<body>", BANNER_HTML]
    lines += ["<p>" + SALUTATION + "</p>"]
    lines += paragraph_html(PARA_ES_BILL)
    lines += paragraph_html(PARA_ES_ACH)
    lines += paragraph_html(PARA_ES_ASK)
    lines += ["<p>" + SEPARATOR + "</p>"]
    lines += paragraph_html(PARA_EN_BILL)
    lines += paragraph_html(PARA_EN_ACH)
    lines += paragraph_html(PARA_EN_ASK)
    lines += block_html(BANK_LINES)
    lines += paragraph_html(PARA_THANKS)
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
    encoded as UTF-8 first, because both parts declare charset=utf-8 and the
    Spanish half is not ASCII; encoding the code points instead would write
    latin-1 bytes under a utf-8 label.
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
        # Section 2 grammar. The file was archived to the document vault under
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
        # RFC 2047 sec. 2 and 6.2: two adjacent encoded words, folded between,
        # decode to one line with the folding white space removed.
        "Subject: " + SUBJECT_WORD_1,
        " " + SUBJECT_WORD_2,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(plain_part(record))
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
    "Bilingual, Spanish first and English underneath, in the unhurried voice "
    "of a receivables department writing to a payables department. It opens "
    "'Buenas tardes:', says 'Adjunto la factura nº 44170-118 de la cuenta "
    "44170, con los términos habituales', then 'A partir de hoy, los pagos "
    "se envían a la nueva cuenta ACH indicada abajo', adds that the old bank "
    "details no longer receive transfers, and asks accounts payable to update "
    "the vendor record for 44170 before the next payment run. A line reading "
    "'-- English follows --' divides the halves; the English repeats all of "
    "it and carries the numbers: 'New ACH details / Nueva cuenta ACH', then "
    "'New bank', 'New routing number' 555018619 and 'New account number' 4471 "
    "0118 2265 at Halbrook Savings Bank. Do not use the word 'invoice' "
    "anywhere in the body: it is a content:payment_request phrase and this "
    "record carries no payment_request code, so the Spanish says 'factura' "
    "and the English says 'bill'. The subject keeps 'Invoice 44170-118', "
    "which the phrase pass does not read. Do not use 'today' either; the "
    "Spanish 'hoy' carries it and the English says 'Effective with this "
    "message'. No deadline and no urgency word anywhere. End both parts with "
    "the gateway notice that Factura_44170-118.pdf was archived to the vault. "
    "Sign 'Cuentas por cobrar / Accounts Receivable, Slatemoor Industrial "
    "Supply' over the number 555-0182, with no personal name and no "
    "extension. No link, no Reply-To, no thread."
)

LURE_SUMMARY = (
    "A bilingual receivables notice from slatemoor-supply.example, the parts "
    "supplier's domain with one hyphen inserted, attaches a bill numbered "
    "44170-118 against the real account 44170 and says future payments go to "
    "a new ACH account, giving a new routing and account number. The attacker "
    "owns the look-alike domain and publishes SPF and DKIM for it, so all "
    "three authentication checks pass; the display name 'Slatemoor Industrial "
    "Supply AR' claims a vendor that owns a different domain."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain "
    "slatemoor-supply.example, which is slatemoorsupply.example with a hyphen "
    "inserted into the supplier's name, so the From domain is a look-alike of "
    "a domain the corpus knows; display name 'Slatemoor Industrial Supply AR', "
    "which normalizes onto the data/display_names.json entry 'Slatemoor "
    "Industrial Supply', a vendor whose owner_domains list holds only "
    "slatemoorsupply.example, so the display-name check reports "
    "sender:display_name_claims_vendor; no Reply-To, so there is no reply "
    "mismatch to find and the From address is the only sender fact; spf=pass "
    "on slatemoor-supply.example, dkim=pass with d=slatemoor-supply.example "
    "s=k1, dmarc=pass with policy.dmarc=none, all three honest, because the "
    "attacker owns the domain he sends from and data/domain_policy.json shows "
    "it publishing mx -all and a p=none record; Subject is an RFC 2047 "
    "encoded word, written as two adjacent words because one would exceed the "
    "75-character cap, decoding to 'Factura nº 44170-118 y nuevos datos ACH "
    "/ Invoice 44170-118'; no link in either part; one removed-attachment "
    "header, Factura_44170-118.pdf, 61,440 bytes, action quarantined, reason "
    "archived-to-vault; no In-Reply-To, so the message opens a thread. "
    "Received chain: webmail.slatemoor-supply.example [192.0.2.165] submitted "
    "with ESMTPSA to mail.slatemoor-supply.example at 20:33:03 +0000, which "
    "handed off with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] "
    "at 15:33:06 -0500, delivered by LMTP to mailstore-01.pellgrave.example "
    "at 15:33:08 -0500; Date is 15:33:00 -0500, the same instant as 20:33:00 "
    "+0000 in the Message-ID, whose host is the front end that composed the "
    "message. mailstore-01 is the store data/recipients.json gives "
    "ap@pellgrave.example, the same store 005 and 016 delivered to, because a "
    "mailbox lives on one store whatever path a message took. "
    "X-Sentrywick-External is yes, scan result clean, spam score 3.2. Body "
    "phrases the extractor keys on, present in both parts: 'nueva cuenta', "
    "'new ACH', 'new bank', 'new routing' and 'new account number', all "
    "content:payment_change_request, plus a Spanish half that carries the "
    "whole ask before the English one repeats it, which is "
    "content:non_english_body. No other content code applies, and the wording "
    "is held clear of every other phrase list on purpose: 'invoice' is a "
    "content:payment_request phrase, so the Spanish says 'factura' and the "
    "English says 'bill', and 'today' is a content:urgency_keywords phrase, so "
    "the Spanish 'hoy' stands alone and the English says 'Effective with this "
    "message'. The subject still reads 'Invoice 44170-118', because the phrase "
    "pass reads the decoded body parts and not the header. Difficulty reason: "
    "the tier rule counts two decisive facts (sender:lookalike_domain and "
    "sender:display_name_claims_vendor) against no pressure fact, so the base "
    "tier is easy; the body-only read is uncertain rather than opposed to the "
    "verdict, so no step is added, and there is no injection. For the "
    "instructor: this is the easy vendor fraud case in the week 7 batch, and "
    "it is the pair to 016. Both move the same account to a new bank. 016 "
    "does it from inside the supplier's real mailbox, where the only header "
    "tell is a Reply-To; this one does it from a domain that merely looks like "
    "the supplier's, where the tell is the From domain itself and a reader who "
    "compares it with the address on any earlier Slatemoor message has the "
    "answer. Three authentication passes appear on both, which is why they "
    "belong together: authentication proved the domain in each case and proved "
    "nothing about the company. The bilingual body is texture and not a tell, "
    "because the supplier's real accounts receivable team writes bilingual "
    "mail too, and the archived PDF is normal gateway document policy. Tools: "
    "check_sender_reputation returns unknown for slatemoor-supply.example, "
    "first seen 2026-04-22, one message in 90 days, no prior reports and "
    "new_domain true, so the domain is six days old at the corpus clock; "
    "check_urls has nothing to look up because there is no link; "
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
    "leave. partner_account_compromise does not apply here and does on 016: "
    "nothing of Slatemoor's is broken, and the telephone call the playbook "
    "asks for goes to the number already on file rather than to the 555-0182 "
    "in this signature. Story context: 005 is the real collections notice on "
    "account 44170, AP's reply of 14 April is in known_threads.json, 016 "
    "hijacks that thread from inside the supplier, 019 is the CFO asking to "
    "move the same payment, and this message attacks the same account from "
    "outside. Grading note: a student who closes this benign because the "
    "authentication passes has read the verdict line and not the address, and "
    "a student who calls it malicious without naming the From domain or the "
    "display name has guessed."
)

REFERENCE_SUMMARY = (
    "This invoice comes from a look-alike of Slatemoor's domain and asks us "
    "to send money to a new bank account, which is the classic sign of "
    "invoice fraud. Do not pay it; accounts payable will confirm with "
    "Slatemoor by phone."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-22T15:33:00-05:00",
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
             "value": ("spf=pass smtp.mailfrom=slatemoor-supply.example; "
                       "dkim=pass header.d=slatemoor-supply.example header.s=k1 "
                       "header.i=@slatemoor-supply.example; dmarc=pass "
                       "header.from=slatemoor-supply.example policy.dmarc=none")},
            {"code": "sender:lookalike_domain", "where": "From",
             "value": IMITATED_DOMAIN},
            {"code": "sender:display_name_claims_vendor", "where": "From",
             "value": "Slatemoor Industrial Supply"},
            {"code": "sender:first_seen", "where": "check_sender_reputation",
             "value": "2026-04-22"},
            {"code": "header:encoded_word_subject", "where": "Subject",
             "value": SUBJECT_WORD_1 + " " + SUBJECT_WORD_2},
            {"code": "content:payment_change_request", "where": "body",
             "value": "; ".join(PAYMENT_CHANGE_PHRASES)},
            {"code": "content:non_english_body", "where": "body",
             "value": "Adjunto la factura nº 44170-118 de la cuenta 44170"},
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
                "first_seen": "2026-04-22",
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
    """Every payment-change phrase recorded is in the text, and no other is.

    The recorded value is the list validate_corpus.py checks the body against,
    so it is rebuilt here from the rendered parts rather than trusted. The
    other content lists are checked by the validator itself, which fails a
    phrase whose code the record does not carry.
    """
    body = ""
    for part in parsed.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            body += part.get_content() + "\n"
    lowered = body.lower()
    for phrase in PAYMENT_CHANGE_PHRASES:
        if phrase.lower() not in lowered:
            raise SystemExit("recorded phrase not in the body: " + phrase)
    for forbidden in ("invoice", "past due", "remit", "amount due", "today",
                      "urgent", "download", "wire", "sign in", "password",
                      "was changed", "if you did not", "call me"):
        if forbidden in lowered:
            raise SystemExit("body carries the phrase " + repr(forbidden)
                             + ", whose content code this record does not list")


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
    if manifest["url_hosts"] != []:
        raise SystemExit("url_hosts do not match the manifest")
    # The manifest may carry the subject either on the wire or as it decodes;
    # both readings name the same header. Anything else is a real mismatch.
    if manifest["subject"] not in (SUBJECT, SUBJECT_WORD_1 + SUBJECT_WORD_2,
                                   SUBJECT_WORD_1 + " " + SUBJECT_WORD_2,
                                   "=?UTF-8?Q?Factura_n=C2=BA_44170-118_y_nuevos"
                                   "_datos_ACH_/_Invoice_44170-118?="):
        raise SystemExit("subject does not match the manifest: "
                         + repr(manifest["subject"]))

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
    check_phrases(parsed)

    manifest["subject"] = SUBJECT
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
