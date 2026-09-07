#!/usr/bin/env python3
"""Regenerate 016-slatemoor-remit-to-update.

Rebuilds emails/teaching/016-slatemoor-remit-to-update.eml byte for byte from
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
    MIME boundary         = "=_swk_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also
                            X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Only the b= tag needs the block indexed stream, because a 2048 bit signature
is 256 bytes and one digest is 32. bh= is one digest and is taken as one,
which is the form gen_007 uses. Neither value verifies anything: no .example
domain can publish a DKIM key, and the course reads the gateway's
Authentication-Results verdict rather than recomputing a signature.

The DKIM t= value is not seed derived and is not meant to be. It is the Unix
time of the sender-side Received timestamp, computed here from that same stamp
string so the two cannot drift apart.

Two values are read back from the data files rather than typed here:
data/recipients.json gives the one store that holds ap@pellgrave.example, and
data/attachments.json gives the removed file's name, size, action, type and
reason, with its sha256 checked against sha256("<seed>|<id>|<filename>")
before the header is written. The recipient is a shared mailbox rather than a
distribution list, so the LMTP hop names the recipient itself; the reporter
appears only in X-Sentrywick-Reported-By, because a shared mailbox is worked
by several people and the person who pressed report is not the addressee.

What this message is, and why the headers are honest.

This is the vendor fraud case where nothing in the trace layer is forged. The
attacker is inside Marisol Etxeberria's mailbox at the parts supplier, and the
message really was composed in the supplier's webmail and really was sent by
the supplier's own outbound server. So SPF passes on slatemoorsupply.example,
the supplier's own key signs it, DMARC passes against the published quarantine
policy, and check_sender_reputation returns trusted. An agent that treats
"three green checks" as a verdict gets this one wrong, which is the whole
point of putting it in week 6.

The two facts that do settle it are both deterministic:

  * Reply-To is m.etxeberria@slatemoorsuply.example, the supplier's domain
    with one letter dropped from "supply". The DKIM h= list this signer uses
    is the vendor's standard from:to:subject:date:message-id:mime-version:
    content-type, the same list 005 carries, and it does not cover Reply-To,
    so a look-alike reply address rides through a dkim=pass untouched. That is
    not a flaw in the corpus; it is why analysts read Reply-To by hand.
  * The body asks accounts payable to change where the money goes, which the
    playbook answers with a callback rule no email can satisfy.

Header shape, and why each field is here:

  * Authentication-Results, Received-SPF, DKIM-Signature and
    X-Sentrywick-External are all present because the message crossed the
    border gateway. spf=pass on the envelope domain, dkim=pass with
    d=slatemoorsupply.example s=sm2026, dmarc=pass with policy quarantine,
    exactly as domain_policy.json publishes them.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Spam-Score: 2.4 match the
    received_path_hint in the manifest. The score is low because there is
    nothing for a filter to dislike: no link, an ordinary PDF, a real thread,
    an authenticated sender.
  * X-Sentrywick-Removed-Attachment records the signed bank letter with
    action=quarantined and reason=archived-to-vault, which is normal document
    policy at this gateway and not evidence of anything. Both body parts end
    with the notice naming the file, the way section 2 of
    docs/email-header-realism.md fixes it.
  * In-Reply-To names the accounts payable reply of 14 April in
    data/known_threads.json, and References lists 005's Message-ID before it,
    so the thread resolves two levels deep and the visible quote agrees with
    the headers.
  * Message-ID names webmail.slatemoorsupply.example, the host at the bottom
    of the Received chain, because the webmail front end is what composed the
    message and stamped the id.

Headers deliberately absent, matching the manifest indicator list: no
X-Originating-IP, because the record carries no header:x_originating_ip and
this webmail product records the submitting host in its Received line instead
of writing a client address header; no Thread-Topic, which section 9 gives to
the organization's own submission host and never to mail that arrived through
the gateway; no X-Priority and no Importance, because a real accounts
receivable clerk does not flag a routine reply, and because urgency is not one
of this record's indicators.

Run:  python3 corpus/tools/generators/gen_016_slatemoor_remit_to_update.py
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

EMAIL_ID = "016-slatemoor-remit-to-update"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "m.etxeberria@slatemoorsupply.example"
SENDER_DISPLAY = "Marisol Etxeberria"
# The envelope sender is the From mailbox: the supplier's own server sent this,
# so there is no envelope-versus-author split. The Reply-To is the one address
# in the file that does not belong to the supplier.
ENVELOPE_SENDER = SENDER
REPLY_TO = "m.etxeberria@slatemoorsuply.example"
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

SUBJECT = "Re: Past due statement, account 44170: updated remittance details"

SENDER_DOMAIN = "slatemoorsupply.example"
REPLY_TO_DOMAIN = "slatemoorsuply.example"
SENDER_HOST = "mail.slatemoorsupply.example"
SENDER_SUBMIT_HOST = "webmail.slatemoorsupply.example"
SENDER_IP = "203.0.113.30"
SENDER_SUBMIT_IP = "192.0.2.31"
DKIM_SELECTOR = "sm2026"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The thread. 005 opened it, accounts payable answered on 14 April
# (data/known_threads.json), and this message replies to that answer, so
# References lists 005 first and In-Reply-To repeats the last id.
PARENT_STATEMENT_ID = "<20260414143100.88e138a5c614@mail.slatemoorsupply.example>"
PARENT_REPLY_ID = "<20260414163344.54ccc40f4134@mail.pellgrave.example>"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 13:44 +0000 is the same instant as 08:44 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree.
DATE_HEADER = "Tue, 21 Apr 2026 08:44:00 -0500"
SUBMIT_STAMP = "Tue, 21 Apr 2026 13:44:03 +0000"
SUBMIT_UTC = "2026-04-21 13:44:03"
GATEWAY_STAMP = "Tue, 21 Apr 2026 08:44:06 -0500"
STORE_STAMP = "Tue, 21 Apr 2026 08:44:08 -0500"
MESSAGE_ID_STAMP = "20260421134400"

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
# record carries exactly one content code, content:payment_change_request, so
# no phrase from any other content list may appear anywhere in either decoded
# part, quoted text included: validate_corpus.py runs every list against the
# whole decoded body and fails both a phrase with no code and a code with no
# phrase.
#
#   The five phrases that carry the code are "changed banks", "new bank",
#   "new routing", "new account number" and "update the vendor account", each
#   sitting whole on one line.
#   "remit" is out, and that is the one place this file departs from the
#   wording the manifest's body_brief suggested. "remit" is a
#   content:payment_request phrase and it is a substring of "remittance", so
#   the brief's "updated remittance" and "update the remit-to" would both put
#   content:payment_request into a record that does not carry it. The subject
#   line still reads "updated remittance details", because the phrase pass
#   reads the body parts and not the header. The ask itself is unchanged: the
#   body asks accounts payable to update the vendor account for 44170 to a new
#   bank, with a new routing number and a new account number.
#   "invoice", "past due" and "amount due" are out for the same reason, which
#   is why the quoted thread below is trimmed to the lines of 005 and of the
#   accounts payable reply that carry none of them. Trimming a quote to the
#   part being answered is what a person does anyway.
#   "credit hold", "today", "by friday" and the rest of
#   content:urgency_keywords are out. The pressure here is a date already
#   agreed in the thread, not a countdown, and the record scores no urgency.
#   "call me" and "call the number on file" are out: this sender does not want
#   a phone call. The number in the signature is a signature line, the same one
#   005 carries, and not an instruction. 043 is the record that does invite the
#   callback, and it is benign.
#   "wire" (content:banking_instruction), "download" and "shared with you"
#   (content:file_share_lure), "sign in" and "password"
#   (content:credential_request), "was changed" and "if you did not"
#   (content:account_change_notice), "confidential" and "quietly"
#   (content:secrecy_request), "personal address" and "not working"
#   (content:excuse_for_external_address) and every
#   content:payment_timing_request phrase are all out. Nothing asks for the
#   payment to move; it stays on 4/24, which is what makes the change of bank
#   the only thing being asked for.
#
# The tone is Marisol's tone from 005: friendly, apologetic about the timing,
# and specific about numbers. That is the point of a compromised mailbox. The
# attacker is answering a real message in a real thread, so the register is
# right because it was learned from the thread.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

SALUTATION = "Priya,"

PARA_THANKS = [
    "Thank you - that is what I needed to hear, and I have noted 4/24",
    "against 44170.",
]

PARA_MOVE = [
    "One thing before it goes out. Slatemoor changed banks on 4/15 and our",
    "receivables now land at Dunmarrow Regional. The Sandmarsh details you",
    "have on file for us are the old ones, and anything sent there after",
    "4/15 comes back to us a week later.",
]

# The three lines a vendor file is updated from. The routing number begins
# with 55, which no real routing number can, and the account number is
# invented; both sit inside the fiction the same way the ones in 021 do.
BANK_LINES = [
    "New bank: Dunmarrow Regional",
    "New routing number: 555018842",
    "New account number: 7714 3260 5589",
]

PARA_LETTER = [
    "Our controller signed the letter that is attached. It is on our",
    "letterhead and it carries both numbers, so your vendor file has",
    "something to sit behind the change.",
]

PARA_ASK = [
    "Please update the vendor account for 44170 with the new bank before",
    "the 4/24 run goes out. If that is awkward at this stage, take 44170",
    "off that run and put it on the next one on the new details.",
]

PARA_APOLOGY = [
    "Sorry for the timing on this. The move has been in the works since",
    "January and the letters went out later than they should have.",
]

# The same four line signature 005 carries, because it is the same person's
# signature and the attacker is sending from her mailbox. 555-0147 is inside
# the 555-0100 through 555-0199 fictional range.
SIGNATURE_LINES = [
    "Marisol Etxeberria",
    "Accounts Receivable",
    "Slatemoor Industrial Supply",
    "555-0147",
]

# Two quote levels, parent first, matching In-Reply-To. The outer level is the
# accounts payable reply of 14 April (known_threads.json); the 005 statement
# of the same morning is nested one level inside it, which is the shape a
# client produces when it replies to the accounts payable message. Section 9
# of docs/email-header-realism.md puts the attribution line for a nested
# message at the level of the message that quotes it, so the line naming 005
# sits at one ">" and only its text goes to two.
QUOTE_OUTER_ATTRIB = "On Tue, 14 Apr 2026 at 11:33, Accounts Payable wrote:"
QUOTE_OUTER_BODY = [
    "Marisol, thank you for the statement. Account 44170 is scheduled on",
    "the 4/24 run and the whole balance goes with it. I will send the",
    "reference lines over once it is cut.",
]
QUOTE_OUTER_SIGNATURE = [
    "Priya Castellanos",
    "Accounts Payable Specialist, Pellgrave Mechanical Group, ext. 4118",
]
# The attribution names 005's From display name, which is the accounts
# receivable mailbox rather than Marisol herself. She answered from her own
# mailbox this time, the way Priya answers from hers in 011.
QUOTE_INNER_ATTRIB = [
    "On Tue, 14 Apr 2026 at 09:31, Slatemoor Industrial Supply - Accounts",
    "Receivable wrote:",
]
QUOTE_INNER_BODY = [
    "If a payment is already scheduled, reply to this message with the date",
    "and the amount and I will note it on the account.",
]
QUOTE_INNER_SIGNATURE = list(SIGNATURE_LINES)

NOTICE_HEAD = "[Sentrywick Gateway removed 1 attachment:"
NOTICE_TAIL = "Details are in the message headers.]"


def notice_lines(record):
    """The section 2 removal notice, wrapped so no line passes 78 characters.

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
    lines += PARA_THANKS + [""]
    lines += PARA_MOVE + [""]
    lines += BANK_LINES + [""]
    lines += PARA_LETTER + [""]
    lines += PARA_ASK + [""]
    lines += PARA_APOLOGY + [""]
    lines += SIGNATURE_LINES + [""]
    lines += [QUOTE_OUTER_ATTRIB]
    lines += ["> " + line for line in QUOTE_OUTER_BODY]
    lines += [">"]
    lines += ["> " + line for line in QUOTE_OUTER_SIGNATURE]
    lines += [">"]
    lines += ["> " + line for line in QUOTE_INNER_ATTRIB]
    lines += [">> " + line for line in QUOTE_INNER_BODY]
    lines += [">>"]
    lines += [">> " + line for line in QUOTE_INNER_SIGNATURE]
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
    lines = ["<html>", "<body>", BANNER_HTML]
    lines += ["<p>" + SALUTATION + "</p>"]
    lines += paragraph_html(PARA_THANKS)
    lines += paragraph_html(PARA_MOVE)
    lines += block_html(BANK_LINES)
    lines += paragraph_html(PARA_LETTER)
    lines += paragraph_html(PARA_ASK)
    lines += paragraph_html(PARA_APOLOGY)
    lines += block_html(SIGNATURE_LINES)
    # The two quote levels the plain part sets with ">" and ">>", set here as
    # one nested blockquote per level, so the two parts agree on depth as well
    # as on words. No link, no image, no script, no hidden text.
    lines += ["<p>" + QUOTE_OUTER_ATTRIB + "</p>", "<blockquote>"]
    lines += paragraph_html(QUOTE_OUTER_BODY)
    lines += block_html(QUOTE_OUTER_SIGNATURE)
    lines += paragraph_html(QUOTE_INNER_ATTRIB) + ["<blockquote>"]
    lines += paragraph_html(QUOTE_INNER_BODY)
    lines += block_html(QUOTE_INNER_SIGNATURE)
    lines += ["</blockquote>", "</blockquote>"]
    notice = notice_lines(record)
    lines += ['<p style="font-size:12px;color:#6b6b6b;">' + notice[0],
              notice[1] + "</p>"]
    lines += ["</body>", "</html>"]
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


def build_eml(seed, record):
    boundary = "=_swk_" + hexid(seed, "boundary")
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
        # supplier's own domain, because the supplier's own server sent this.
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
        "X-Sentrywick-Spam-Score: 2.4",
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
        # The signer's h= list is the supplier's standard one, the same list
        # 005 carries. It does not name reply-to, so the look-alike reply
        # address below is outside the signature and dkim still passes.
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
        # The one dishonest header in the file, and the only one a parser can
        # catch: slatemoorsuply.example is slatemoorsupply.example with a
        # letter dropped from "supply".
        "Reply-To: " + REPLY_TO,
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # RFC 5322 sec. 3.6.4: References carries the parent's References
        # followed by the parent's Message-ID, and In-Reply-To repeats the
        # last of them.
        "In-Reply-To: " + PARENT_REPLY_ID,
        "References: " + PARENT_STATEMENT_ID,
        "  " + PARENT_REPLY_ID,
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
    "Marisol's tone from 005, warm and specific: she thanks Priya for the "
    "4/24 promise, then says Slatemoor 'changed banks' on 4/15 and that "
    "receivables now land at Dunmarrow Regional, so the Sandmarsh details on "
    "file are the old ones. Three lines give the 'new bank', the 'new "
    "routing' number and the 'new account number'. She says the controller "
    "signed the attached letter, then asks Priya to 'update the vendor "
    "account' for 44170 with the new bank before the 4/24 run, offering to "
    "let it slip to the next run instead; nothing asks for the payment to "
    "move earlier. She apologises for the timing. Do not use 'remit' or "
    "'remittance' anywhere in the body: 'remit' is a content:payment_request "
    "phrase and this record carries no payment_request code, so the ask is "
    "worded 'update the vendor account' instead. The subject keeps 'updated "
    "remittance details', which the phrase pass does not read. Sign with the "
    "same four-line block 005 uses. Quote the accounts payable reply of 14 "
    "April at one level and the tail of the 4/14 statement nested one level "
    "inside it, trimmed to lines that carry no phrase from another content "
    "list. End both parts with the gateway notice that "
    "Bank_Letter_Slatemoor_0415.pdf was archived to the vault. No link. "
    "Reply-To header carries m.etxeberria@slatemoorsuply.example."
)

LURE_SUMMARY = (
    "A reply inside the real collections thread, from the supplier's real "
    "mailbox and past all three authentication checks, says Slatemoor "
    "changed banks on 4/15 and asks accounts payable to update the vendor "
    "account before the 4/24 run. A signed bank letter is named as the "
    "attachment the gateway archived, and the Reply-To address drops one "
    "letter from the vendor's domain."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain "
    "slatemoorsupply.example under the display name Marisol Etxeberria, "
    "which data/display_names.json gives that domain, so "
    "display_name_mismatch is false; reply_to "
    "m.etxeberria@slatemoorsuply.example, a different mailbox on a different "
    "domain, and that domain is slatemoorsupply.example with one letter "
    "dropped from 'supply'; spf=pass on slatemoorsupply.example, dkim=pass "
    "with d=slatemoorsupply.example s=sm2026, dmarc=pass with policy "
    "quarantine, so all three checks pass and the message is aligned; no "
    "link in either part; one removed-attachment header, "
    "Bank_Letter_Slatemoor_0415.pdf, 48,211 bytes, action quarantined, "
    "reason archived-to-vault; In-Reply-To "
    "<20260414163344.54ccc40f4134@mail.pellgrave.example>, the accounts "
    "payable reply of 14 April in data/known_threads.json, with References "
    "listing 005's Message-ID "
    "<20260414143100.88e138a5c614@mail.slatemoorsupply.example> before it, so "
    "the thread resolves. Received chain: "
    "webmail.slatemoorsupply.example [192.0.2.31] submitted with ESMTPSA to "
    "mail.slatemoorsupply.example at 13:44:03 +0000, which handed off with "
    "ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 08:44:06 "
    "-0500, delivered by LMTP to mailstore-01.pellgrave.example at 08:44:08 "
    "-0500; Date is 08:44:00 -0500, the same instant as 13:44:00 +0000 in "
    "the Message-ID, whose host is the webmail front end that composed the "
    "message. mailstore-01 is the store data/recipients.json gives "
    "ap@pellgrave.example, the same store 005 delivered to, because a mailbox "
    "lives on one store whatever path a message took. X-Sentrywick-External "
    "is yes, scan result clean, spam score 2.4. Body phrases the extractor "
    "keys on, present in both parts: 'changed banks', 'new bank', 'new "
    "routing', 'new account number' and 'update the vendor account', all "
    "content:payment_change_request. No other content code applies, and the "
    "wording is held clear of every other phrase list on purpose, quoted "
    "text included: the word 'remit' is a content:payment_request phrase and "
    "a substring of 'remittance', so the ask is written 'update the vendor "
    "account' and the quoted thread is trimmed to the lines that carry no "
    "phrase from another list. The subject still reads 'updated remittance "
    "details', because the phrase pass reads the decoded body parts and not "
    "the header. Difficulty reason: the tier rule counts one decisive fact "
    "(sender:reply_to_lookalike_domain) against two pressure facts (an "
    "allowlisted sender and a reply in a known thread), so pressure exceeds "
    "decisive and the base tier is hard; the body-only read is benign, the "
    "opposite of the verdict, which adds a step and stays capped at hard. No "
    "injection. For the instructor: this is the week 6 fact-validation case. "
    "The headers are honest because the supplier's own server really did send "
    "the message: Marisol's mailbox is compromised, so authentication proves "
    "the domain and proves nothing about the sender's intent. A model that "
    "reads the body and the three passes will answer benign, and the "
    "validation step has to overturn that on one field it can quote, the "
    "Reply-To domain, plus the playbook rule that no bank change is accepted "
    "without a callback. The archived PDF is normal gateway document policy "
    "and is not evidence; 043 carries the same header on a benign message. "
    "Tools: check_sender_reputation returns trusted for "
    "slatemoorsupply.example, first seen 2022-06-14, 96 messages in 90 days "
    "and two prior reports both closed benign, which is a fact that argues "
    "the wrong way and has to be weighed rather than obeyed; check_urls has "
    "nothing to look up because there is no link; lookup_recipient shows ap@ "
    "is a shared mailbox that handles payments with three prior reports, all "
    "true positives, two of them tagged vendor-invoice-fraud. The loop "
    "therefore runs check_sender_reputation and lookup_recipient and stops on "
    "tools_exhausted; neither tool contradicts the body, which is the lesson. "
    "recipient:prior_similar_report follows the prior_similar_report_rule: "
    "the payment change ask implies vendor-invoice-fraud and "
    "direct-deposit-change, the mailbox holds vendor-invoice-fraud, so that "
    "is the value. Full credit on the indicators criterion needs "
    "sender:reply_to_lookalike_domain and content:payment_change_request. "
    "Expected action: escalate_incident, with reasons "
    "financial_or_endpoint_impact and partner_account_compromise, the second "
    "because a dmarc=pass message from an allowlisted partner asking for "
    "money to move means the partner's mailbox is the thing that is broken "
    "and someone has to telephone Slatemoor. Story context: 005 is the real "
    "collections notice that opened this thread, the accounts payable reply "
    "of 14 April in known_threads.json is what this message answers, 019 is "
    "the CFO asking to move the same payment, and 031 attacks the same "
    "account from a hyphen-insertion look-alike domain instead of from "
    "inside the supplier. Grading note: a student who closes this benign "
    "because the authentication passes has read the header and not the "
    "Reply-To, and a student who calls it malicious without naming the "
    "Reply-To domain has guessed."
)

REFERENCE_SUMMARY = (
    "Slatemoor's real mailbox was used to send this, but the reply address "
    "is a look-alike and the bank change was not confirmed by phone, so we "
    "are treating it as fraud. Do not update any bank details; accounts "
    "payable will call Marisol at the number on file."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": "emails/teaching/" + EMAIL_ID + ".eml",
        "set": "teaching",
        "weeks": [6],
        "date": "2026-04-21T08:44:00-05:00",
        "verdict": "malicious",
        "category": "vendor_fraud",
        "difficulty": "hard",
        "body_only_read": "benign",
        "sender_display": SENDER_DISPLAY,
        "sender_address": SENDER,
        "reply_to": REPLY_TO,
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
            {"code": "sender:reply_to_differs", "where": "Reply-To",
             "value": REPLY_TO},
            {"code": "sender:reply_to_lookalike_domain", "where": "Reply-To",
             "value": SENDER_DOMAIN},
            {"code": "content:payment_change_request", "where": "body",
             "value": ("changed banks; new bank; new routing; new account number; "
                       "update the vendor account")},
            {"code": "attachment:archived_to_vault",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "thread:in_reply_to_known", "where": "In-Reply-To",
             "value": PARENT_REPLY_ID},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:shared_mailbox", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:prior_similar_report", "where": "lookup_recipient",
             "value": "vendor-invoice-fraud"},
        ],
        "required_indicators": ["sender:reply_to_lookalike_domain",
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
        "escalation_reasons": ["financial_or_endpoint_impact",
                               "partner_account_compromise"],
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
    if manifest["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if manifest["sender_address"] != SENDER or manifest["reply_to"] != REPLY_TO:
        raise SystemExit("From or Reply-To does not match the manifest")
    if manifest["url_hosts"] != []:
        raise SystemExit("url_hosts do not match the manifest")

    stub = attachment_stub(seed)
    for key in ("filename", "size", "sha256", "action", "type", "reason"):
        if manifest["attachment"][key] != stub[key]:
            raise SystemExit("attachment " + key + " disagrees with attachments.json")

    data = build_eml(seed, stub)
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
    if str(parsed["Reply-To"]) != REPLY_TO:
        raise SystemExit("unfolded Reply-To is " + repr(str(parsed["Reply-To"])))

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
