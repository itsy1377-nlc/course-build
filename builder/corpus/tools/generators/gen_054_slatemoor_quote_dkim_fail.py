#!/usr/bin/env python3
"""Regenerate 054-slatemoor-quote-dkim-fail.

Rebuilds the exam-only file 054-slatemoor-quote-dkim-fail.eml byte for byte
from the corpus seed, refreshes the prose fields of its own record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

This one is exam-only, so it does not ship under corpus/emails/. It is written
into the instructor package at instructor/exam-emails/, which is why EML_PATH
climbs out of the corpus folder. The corpus validator, run over corpus/emails,
warns that an exam record has no file there; that warning is correct. Point it
at the folder instead to check this file:

    python3 corpus/tools/validate_corpus.py --emails <folder> --no-dns

The ground truth record still writes the logical corpus path
emails/exam/054-slatemoor-quote-dkim-fail.eml in its file field, because
spec/ground_truth.schema.json fixes that pattern for every record and an exam
record has no other name inside the corpus.

Every identifier in the file that looks random is derived from the corpus
seed, so rerunning this script reproduces the same bytes:

    hexid(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = the first n bytes of
                       sha256("<seed>|<email id>|<label>|0")
                       || sha256("<seed>|<email id>|<label>|1") || ...

    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=hexid("store-id", 32), version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Only the 2048 bit signature needs the block indexed stream, because a single
SHA-256 digest is 32 bytes and b= is 256. bh= is exactly one digest, so it is
taken from the plain hash. Neither value verifies: no .example domain can
publish a key, and on this message the gateway wrote dkim=fail anyway. The
DKIM t= value is not seed derived and is not meant to be. It is the Unix time
of the sender-side Received stamp, computed here from that same stamp string
so the two cannot drift apart.

Four values are read back from the data files rather than typed here, so the
rendered headers cannot disagree with the corpus: data/recipients.json gives
mailstore-01 as the one store that holds the procurement specialist's mailbox;
data/attachments.json gives the archived file's name, size, action, type and
reason, with its sha256 checked against the rule
sha256("<seed>|<email id>|<filename>") before the header is written;
data/domain_policy.json gives the supplier's DKIM selector and the DMARC
policy the Authentication-Results line quotes.

Why the headers look the way they do. This is the supplier's real quote, sent
from the supplier's own server, and exactly one of the three checks failed:

  * The quoting application signs the message on the submission hop, at
    SMS-QT-05.slatemoorsupply.example. mail.slatemoorsupply.example then
    appends the company's legal disclaimer paragraph on the way out. The body
    hash in bh= no longer describes the body that arrived, so the gateway
    wrote dkim=fail. The disclaimer is the last paragraph of the author's text
    in both parts, which is where an outbound appender lands it.
  * SPF still passes: mail.slatemoorsupply.example [203.0.113.30] is an MX of
    the envelope sender's domain and domain_policy.json publishes "mx ~all",
    so Received-SPF carries mechanism=mx.
  * That SPF pass is aligned, because the envelope sender and the From header
    are the same mailbox, so DMARC passes on the SPF side alone against the
    quarantine policy the supplier publishes. That is the whole stem of the
    exam item: a fail on one method is not a fail on the message, and reading
    dkim=fail as a verdict produces a false positive here.

X-Sentrywick-Removed-Attachment carries action=quarantined with
reason=archived-to-vault, which is the gateway doing its normal document
policy rather than finding anything wrong: the quote PDF went to the file
vault and the recipient retrieves it there. The body notice in both parts says
so in those words. 037 renders the same pair for the same reason, and 032 is
the file where a removed attachment really is the verdict.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because an inside sales rep sends from the mailbox she reads and the
record's reply_to is null; no In-Reply-To and no References, so thread:new
holds and the quote opens its own thread rather than hanging off the PO 20431
thread 011 works in; no X-Originating-IP, which is reserved for webmail
submissions; no X-Mailer; no Auto-Submitted, because a person pressed send on
a quote the quoting system prepared; no X-Priority and no Importance, because
a quote applies no urgency and the body carries no urgency phrase either.

Run:  python3 corpus/tools/generators/gen_054_slatemoor_quote_dkim_fail.py
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

EMAIL_ID = "054-slatemoor-quote-dkim-fail"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
# Exam-only: the file ships in the instructor package, never under emails/.
EML_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EML_DIR, EMAIL_ID + ".eml")
# The path the ground truth record names. spec/ground_truth.schema.json fixes
# the pattern emails/(teaching|batch|exam)/<id>.eml for every record.
GT_FILE = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "quotes@slatemoorsupply.example"
SENDER_DISPLAY = "Slatemoor Industrial Supply Quotes"
SENDER_DOMAIN = "slatemoorsupply.example"
# The envelope sender is the From mailbox. The quotes desk sends from the
# mailbox it reads, so Return-Path and From are one address, the record's
# reply_to is null rather than a repeat of From, and the SPF pass is aligned
# with the From domain, which is what carries DMARC here.
ENVELOPE_SENDER = SENDER
RECIPIENT = "e.dawodu@pellgrave.example"
RECIPIENT_DISPLAY = "Emeric Dawodu"
REPORTER = "e.dawodu@pellgrave.example"

SUBJECT = "Quote Q-5518: compressor parts for the Rookmere project"

# The supplier's own hosts. 203.0.113.30 is the outbound server 005 also sends
# from, and 192.0.2.32 is the quoting desk's submission host, unused elsewhere
# in the corpus. Both are RFC 5737 documentation addresses, so neither routes.
SENDER_HOST = "mail.slatemoorsupply.example"
SENDER_IP = "203.0.113.30"
SENDER_SUBMIT_HOST = "SMS-QT-05.slatemoorsupply.example"
SENDER_SUBMIT_IP = "192.0.2.32"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"
SCAN_RESULT = "clean"
SPAM_SCORE = "2.7"

# The one link. Its host is the supplier's own quote portal, which is on
# neither url list, so check_urls answers unlisted rather than allowlisted:
# the billing host in 005 is allowlisted, this one has simply never been
# submitted. The path is a quote path and not a sign-in path.
LINK = "https://quotes.slatemoorsupply.example/q/5518"
LINK_LABEL = "View quote"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 18:42 +0000 is the same instant as 13:42 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree.
DATE_HEADER = "Mon, 27 Apr 2026 13:42:00 -0500"
SUBMIT_STAMP = "Mon, 27 Apr 2026 18:42:03 +0000"
SUBMIT_UTC = "2026-04-27 18:42:03"
GATEWAY_STAMP = "Mon, 27 Apr 2026 13:42:07 -0500"
STORE_STAMP = "Mon, 27 Apr 2026 13:42:09 -0500"
MESSAGE_ID_STAMP = "20260427184200"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break.
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
    return base64.b64encode(
        hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()).decode("ascii")


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


def attachment_record(seed):
    """The archived document, from data/attachments.json.

    No file exists. The digest is SHA-256 over seed|email id|filename, the rule
    the data file states for every stub, so it matches no threat-intelligence
    list and the week 4 attachment lookup still has something to find.
    """
    with open(ATTACHMENTS_PATH, encoding="utf-8") as handle:
        attachments = json.load(handle)
    for record in attachments["attachments"]:
        if record["email_id"] == EMAIL_ID:
            break
    else:
        raise SystemExit("attachments.json has no record for " + EMAIL_ID)
    derived = hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|" + record["filename"]).encode()).hexdigest()
    if record["sha256"] != derived:
        raise SystemExit("attachments.json sha256 is not sha256(seed|id|filename)")
    if record["action"] != "quarantined" or record["reason"] != "archived-to-vault":
        raise SystemExit("attachments.json does not describe an archived document")
    return record


def domain_policy(domain):
    """The published DMARC policy and DKIM selector for one domain."""
    with open(POLICY_PATH, encoding="utf-8") as handle:
        policy = json.load(handle)
    for entry in policy["domains"]:
        if entry["domain"] == domain:
            return entry
    raise SystemExit("domain_policy.json has no record for " + domain)


# ---------------------------------------------------------------- body text
#
# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries no content code at all, so no phrase from any body list may
# appear in either decoded part; validate_corpus.py checks both ways and
# main() checks it again here before the file is written. A quote note is the
# one piece of routine business mail that can be written that way, and this
# record needs it written that way, because the whole difficulty has to sit in
# the header block.
#
#   "invoice", "remit", "past due", "net 30" and "amount due" are out
#   (content:payment_request). Nothing is owed yet: a quote is a price, not a
#   bill, so the money words here are "prices", "quote total" and "purchase
#   order number".
#   Every content:urgency_keywords phrase is out, "today" and "as soon as
#   possible" included. The prices hold for 30 days and the lead time is
#   stated as a fact about the maker, not as a countdown.
#   "sign in", "log in" and "password" are out: a quote asks for an order
#   number and never for an identity.
#   "download" is out (content:file_share_lure), so the quote is described as
#   attached and as sitting on the portal, and the link is labelled "View
#   quote".
#   "new account", "new bank" and the rest of content:payment_change_request
#   are out. This message changes nothing about where money goes, which is
#   what separates it from 016, 031 and 049.
#   "confidential" is out (content:secrecy_request), which is why the appended
#   legal disclaimer is written without the word every real disclaimer opens
#   with. It says the same thing in plainer words.
#   "call me" and the rest of content:phone_verification_offered are out. The
#   number in the signature is a signature line and not an instruction.
#   "wire" is out (content:banking_instruction), and it is a substring rather
#   than a word, so the parts list says "gaskets, filter driers and compressor
#   oil" and never names anything with wiring in it.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

HEADING = "Slatemoor Industrial Supply, Quotes Desk"
SALUTATION = "Hello Emeric,"

PARA_OPENING = [
    "Here is quote Q-5518 for the compressor parts on the Rookmere job,",
    "priced off the list you sent through on Thursday.",
]

# The four priced lines and the total. The HTML part renders these as one
# paragraph with <br> between the lines and the total in bold, so both parts
# carry the same six lines in the same order and a part-to-part diff is empty.
# 3,240.00 plus 2,960.00 plus 1,120.00 plus 560.00 is 7,880.00, the figure the
# manifest fixes.
QUOTE_LINES = [
    "Quote Q-5518, prepared 4/27, for the Rookmere project",
    "Valve plate kits, 4 sets: $3,240.00",
    "Discharge and suction service valves, 8 units: $2,960.00",
    "Gaskets, filter driers and compressor oil, one job lot: $1,120.00",
    "Freight, two day service to the site: $560.00",
]
TOTAL_LINE = "Quote total: $7,880.00"

PARA_VALIDITY = [
    "The prices hold for 30 days from the date on the quote. After that we",
    "price it again off the current sheet, which on compressor parts has",
    "been moving a little every quarter.",
]

PARA_STOCK = [
    "Everything on the list is on the shelf here except the valve plate",
    "kits, which run a two week lead time from the maker. Order inside the",
    "next week and the kits still land ahead of your start date.",
]

PARA_ATTACHED = [
    "The full quote is attached, with the part numbers and our terms on the",
    "back page, and the same copy sits on our quote portal.",
]

PARA_ORDER = [
    "Send a purchase order number back on this message when you are ready",
    "and I will release it to the warehouse that afternoon.",
]

CLOSING = "Thanks,"

# A person's signature, not a mailbox signature: the name, the function, the
# company and a dialable number. 555-0154 is inside the 555-0100 through
# 555-0199 fictional range and is used by no other file in the corpus.
SIGNATURE_LINES = [
    "Wilhelmina Sarratt-Oduya",
    "Inside Sales, Quotes Desk",
    "Slatemoor Industrial Supply",
    "555-0154",
]

# The paragraph mail.slatemoorsupply.example appends after the quoting
# application has signed the message. It is the reason the gateway wrote
# dkim=fail, so it renders as the last paragraph of the author's text in both
# parts, below the signature and above the gateway's own notice.
DISCLAIMER = [
    "This message and anything sent with it are meant for the person named",
    "above. If it has reached you in error, please delete it and tell us.",
    "Slatemoor Industrial Supply takes no responsibility for any change made",
    "to this message after it left our systems.",
]

# The gateway's notice, in the pieces the two parts assemble it from. Section 2
# of docs/email-header-realism.md fixes the shape, not where a source line may
# end; the verb is "archived to the file vault" rather than "removed" because
# action=quarantined with reason=archived-to-vault is the gateway filing a
# document under normal policy, not stripping a threat.
NOTICE_HEAD = "[Sentrywick Gateway archived 1 attachment to the file vault:"
NOTICE_TAIL = "Details are in the message headers.]"


def notice_file(record):
    return record["filename"] + " ({:,} bytes).".format(record["size"])


def plain_part(record):
    lines = [BANNER_PLAIN, ""]
    lines += [HEADING, ""]
    lines += [SALUTATION, ""]
    lines += PARA_OPENING + [""]
    lines += QUOTE_LINES + [TOTAL_LINE, ""]
    lines += PARA_VALIDITY + [""]
    lines += PARA_STOCK + [""]
    lines += PARA_ATTACHED + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_ORDER + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE_LINES + [""]
    lines += DISCLAIMER + [""]
    lines += [NOTICE_HEAD, notice_file(record), NOTICE_TAIL]
    return lines


def joined(lines):
    return " ".join(lines)


def quote_html():
    block = [line + "<br>" for line in QUOTE_LINES]
    block[0] = "<p>" + block[0]
    block.append("<b>" + TOTAL_LINE + "</b></p>")
    return block


def html_part(record):
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f2f2f2;">',
        BANNER_HTML,
        '<div style="max-width:620px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#1f1f1f;">',
        '<p style="margin:0 0 18px 0;font-size:17px;font-weight:bold;',
        '  color:#5b3a1a;">' + HEADING + "</p>",
        "<p>" + SALUTATION + "</p>",
        "<p>" + joined(PARA_OPENING) + "</p>",
    ]
    lines += quote_html()
    lines += ["<p>" + joined(PARA_VALIDITY) + "</p>"]
    lines += ["<p>" + joined(PARA_STOCK) + "</p>"]
    lines += ["<p>" + joined(PARA_ATTACHED) + "</p>"]
    # The href is the same address the plain part prints and the button text is
    # the same label, and the address is repeated underneath in plain sight, so
    # a reader of either part can see where the link goes. No image, no script,
    # no form, no hidden text.
    lines += [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#5b3a1a;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
        '<p style="font-size:13px;color:#555555;">If the button does not open,',
        "the address is " + LINK + "</p>",
    ]
    lines += ["<p>" + joined(PARA_ORDER) + "</p>"]
    lines += ["<p>" + CLOSING + "</p>"]
    lines += ["<p>" + "<br>".join(SIGNATURE_LINES) + "</p>"]
    lines += ['<p style="font-size:12px;color:#6b6b6b;">' + joined(DISCLAIMER)
              + "</p>"]
    lines += ["</div>"]
    lines += ['<p style="font-size:12px;color:#6b6b6b;">' + NOTICE_HEAD,
              notice_file(record), NOTICE_TAIL + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start
    of the next line so no line ends in white space; when no space fits,
    hard-break at 75 characters plus the soft line break, never inside an =XX
    escape.
    """
    out = []
    rest = line
    while len(rest) > QP_MAX:
        cut = rest.rfind(" ", 1, QP_MAX)
        if cut <= 0:
            cut = QP_MAX - 1
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
    record = attachment_record(seed)
    policy = domain_policy(SENDER_DOMAIN)
    selector = policy["dkim_selector"]
    dmarc_policy = policy["dmarc_policy"]
    store = mailstore(RECIPIENT)

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
        # own trace field. One method failed and the message still passed, and
        # that is the fact the week 8 exam turns on: DMARC needs one aligned
        # pass, not three, and the aligned pass here is SPF on the supplier's
        # own domain.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=fail header.d=" + SENDER_DOMAIN + " header.s=" + selector,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN
        + " policy.dmarc=" + dmarc_policy,
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
        # The quoting application signed the message on that hop.
        # mail.slatemoorsupply.example then appended the legal disclaimer, so
        # bh= describes a body that is no longer the body that arrived and the
        # gateway wrote dkim=fail.
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SENDER_DOMAIN + "; s=" + selector + "; t=" + str(dkim_time()) + ";",
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
    lines += qp_body(html_part(record))
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii"), record


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "The quotes desk's usual note: quote Q-5518 for the compressor parts on "
    "the Rookmere job, priced off the list procurement sent through on "
    "Thursday. Five priced lines and a total: valve plate kits 3,240.00, "
    "discharge and suction service valves 2,960.00, gaskets and filter driers "
    "and compressor oil 1,120.00, two day freight 560.00, quote total "
    "7,880.00. Say once that the prices hold for 30 days from the date on the "
    "quote and that the valve plate kits run a two week lead time, and ask "
    "for a purchase order number back on this message. One link, 'View "
    "quote', to https://quotes.slatemoorsupply.example/q/5518, printed as an "
    "address in both parts. Carry no phrase from any content list in "
    "spec/enums.json, so the prose reads exactly as benign as it is and the "
    "whole difficulty sits in the header block: a quote is a price and not a "
    "bill, so the money words are 'prices', 'quote total' and 'purchase order "
    "number' rather than any of the content:payment_request phrases. Sign "
    "with a name (Wilhelmina Sarratt-Oduya, Inside Sales, Quotes Desk), the "
    "company and a direct number. Below the signature, the legal disclaimer "
    "paragraph the outbound server appends after signing, which is what broke "
    "DKIM; it avoids the word confidential so that content:secrecy_request "
    "stays absent. End both parts with the gateway notice that "
    "Quote_Q-5518_Compressor_Parts.pdf (44,032 bytes) was archived to the "
    "file vault."
)

LURE_SUMMARY = (
    "The parts supplier's real quote arrives with dkim=fail, because the "
    "outbound server appends the company's legal disclaimer after the quoting "
    "application has signed the message, while the aligned SPF pass still "
    "carries DMARC. The one link goes to the supplier's own quote portal, "
    "which is on neither url list, and the quote PDF was archived to the "
    "vault rather than stripped."
)

MANIFEST_NOTES = (
    "Exam-only. Stem: dkim=fail with spf=pass and dmarc=pass; tests reading "
    "of alignment rather than reflex on any fail. The quotes host is not on "
    "the allowlist, which makes the URL result unlisted rather than "
    "allowlisted. Rendering: the quoting application signs on the submission "
    "hop at SMS-QT-05.slatemoorsupply.example [192.0.2.32] and "
    "mail.slatemoorsupply.example [203.0.113.30] appends the legal disclaimer "
    "on the way out, so the body hash no longer describes the body that "
    "arrived and the gateway wrote dkim=fail; SPF passes on mechanism mx for "
    "the same domain the From header names, so the one aligned pass carries "
    "dmarc=pass against the published quarantine policy. Scan result clean, "
    "spam score 2.7, and one X-Sentrywick-Removed-Attachment with action "
    "quarantined and reason archived-to-vault, which is normal document "
    "policy and not evidence."
)


# ------------------------------------------------------------ ground truth

REFERENCE_SUMMARY = (
    "This is a real quote from Slatemoor; one of the three mail checks failed "
    "for a technical reason, but the overall check passed and the message "
    "came from their own server. It is safe to handle as a normal quote."
)

NOTES = (
    "The week 8 exam item that punishes reading one failed check as a "
    "verdict. Key facts a correct extractor produces: from_domain "
    "slatemoorsupply.example under the display name Slatemoor Industrial "
    "Supply Quotes, which display_names.json resolves to the entry Slatemoor "
    "Industrial Supply, owned by that same domain, so display_name_mismatch "
    "is false; no Reply-To, so there is no Reply-To mismatch to find; "
    "spf=pass on slatemoorsupply.example, dkim=fail with "
    "d=slatemoorsupply.example s=sm2026, dmarc=pass with policy quarantine, "
    "so one method failed and the message still authenticated; one link host, "
    "quotes.slatemoorsupply.example, carrying the single link "
    "https://quotes.slatemoorsupply.example/q/5518, whose path is a quote "
    "path and not a sign-in path; one X-Sentrywick-Removed-Attachment naming "
    "Quote_Q-5518_Compressor_Parts.pdf with action quarantined and reason "
    "archived-to-vault; scan result clean, spam score 2.7; no In-Reply-To, so "
    "the message opens a thread. Why DKIM failed, and why none of it is an "
    "attack: the quoting application signs the message when the desk submits "
    "it, and the supplier's outbound server then appends the company's legal "
    "disclaimer paragraph, so the body hash in bh= describes a body that is "
    "no longer the body that arrived. Nothing about the sending path changed, "
    "so SPF still passes on the mx mechanism the domain publishes, that pass "
    "is aligned with the From domain, and DMARC needs exactly one aligned "
    "pass. Received chain: SMS-QT-05.slatemoorsupply.example [192.0.2.32] "
    "submitted with ESMTPSA to mail.slatemoorsupply.example at 18:42:03 "
    "+0000, which handed off with ESMTPS and TLS1_3 to mx.pellgrave.example "
    "[10.20.4.10] at 13:42:07 -0500, delivered by LMTP to "
    "mailstore-01.pellgrave.example at 13:42:09 -0500; Date is 13:42:00 "
    "-0500, the same instant as 18:42:00 +0000 in the Message-ID. Body "
    "phrases the extractor keys on: none. The record carries no content code, "
    "and the body carries no phrase from any content list in "
    "spec/enums.json, which is deliberate. A quote is a price and not a bill, "
    "so the money words are 'prices', 'quote total' and 'purchase order "
    "number' rather than 'invoice', 'remit' or 'amount due'; the prices hold "
    "for 30 days and the two week lead time is stated as a fact about the "
    "maker rather than as a countdown; and the appended legal disclaimer is "
    "written without the word confidential on purpose, because that word "
    "would add content:secrecy_request to a message that keeps no secret. "
    "recipient:prior_similar_report does not apply: no ask code is listed, so "
    "nothing implies a campaign tag under prior_similar_report_rule, and the "
    "sender record carries no campaign tag either, even though the mailbox "
    "holds one vendor-notice report closed benign. Difficulty reason: the "
    "tier rule counts one decisive benign fact, an allowlisted sender with "
    "dmarc=pass, against one pressure fact, auth:dkim_fail, so pressure "
    "equals decisive and is not zero, and the base tier is medium; the "
    "body-only read is benign, which agrees with the verdict, and there is no "
    "injection, so neither adjustment applies and it stays medium. For the "
    "instructor: this is the false positive the exam is built to catch. "
    "Ungrounded, a failed DKIM check next to an attachment the gateway "
    "removed reads as phishing. Grounded, the facts answer: "
    "check_sender_reputation returns trusted for slatemoorsupply.example, "
    "first seen 2022-06-14, 96 messages in 90 days, two prior reports both "
    "closed benign, the last on 2026-04-02; check_urls returns unlisted for "
    "quotes.slatemoorsupply.example, because the supplier's quote portal has "
    "never been submitted to the list while its billing portal has; "
    "lookup_recipient shows an ordinary procurement mailbox with no flags. "
    "Nothing in the body states any tool result, so the loop has to fetch "
    "them, and no single result is decisive on its own against a failed "
    "check, so the run calls all three tools in turn and ends on "
    "tools_exhausted. The verdict is benign and escalate_expected is false: "
    "DMARC passed, so the auth_failure_on_trusted_sender rule does not fire, "
    "the message asks for nothing but a purchase order number, and it changes "
    "nothing about how or where money moves. Full credit on the indicators "
    "criterion needs auth:dmarc_pass, auth:dkim_fail and "
    "sender:allowlisted_domain. Story context: this is the quote behind the "
    "next Rookmere compressor order, sent to the procurement specialist who "
    "raised PO 20431 in 011; 005 is the same supplier's collections notice "
    "and 016 is the hijack of that thread. Grading note: a student who calls "
    "this malicious because DKIM failed has read one method as the message, "
    "and a student who treats the archived PDF as evidence has read a "
    "removed-attachment header without reading its reason."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": GT_FILE,
        "set": "exam",
        "weeks": [8],
        "date": "2026-04-27T13:42:00-05:00",
        "verdict": "benign",
        "category": "legit_external",
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
        "auth": {"spf": "pass", "dkim": "fail", "dmarc": "pass",
                 "dmarc_policy": "quarantine"},
        "indicators": [
            {"code": "auth:spf_pass", "where": "Authentication-Results",
             "value": "spf=pass smtp.mailfrom=slatemoorsupply.example"},
            {"code": "auth:dkim_fail", "where": "Authentication-Results",
             "value": ("dkim=fail header.d=slatemoorsupply.example "
                       "header.s=sm2026 header.i=@slatemoorsupply.example")},
            {"code": "auth:dmarc_pass", "where": "Authentication-Results",
             "value": ("dmarc=pass header.from=slatemoorsupply.example "
                       "policy.dmarc=quarantine")},
            {"code": "sender:allowlisted_domain",
             "where": "check_sender_reputation", "value": SENDER_DOMAIN},
            {"code": "url:host_unlisted", "where": "check_urls",
             "value": "quotes.slatemoorsupply.example"},
            {"code": "attachment:archived_to_vault",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
        ],
        "required_indicators": ["auth:dmarc_pass", "auth:dkim_fail",
                                "sender:allowlisted_domain"],
        "url_hosts": ["quotes.slatemoorsupply.example"],
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
            "check_urls": {"quotes.slatemoorsupply.example": "unlisted"},
            "lookup_recipient": {
                "address": RECIPIENT,
                "name": "Emeric Dawodu",
                "role": "Procurement Specialist",
                "mailbox_type": "person",
                "executive": False,
                "handles_payments": False,
                "chronic_reporter": False,
                "report_count_90d": 1,
                "true_positive_count_90d": 0,
                "campaign_tags": ["vendor-notice"],
            },
        },
        # A trusted sender is decisive only next to a clean authentication
        # block, and this one carries a failed method, so no single result
        # settles the message on its own. All three tools run and the loop ends
        # with no tool left to try rather than on a decisive result or the cap.
        "expected_loop": {
            "tools": ["check_sender_reputation", "check_urls",
                      "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
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


# ------------------------------------------------------------------- checks

def sentence_count(text):
    """The count check_spec.py applies to lure_summary and reference_summary."""
    return len([piece for piece in re.split(r"(?<=[.!?])\s+", text.strip()) if piece])


def content_phrase_audit(record):
    """Every content phrase list in enums.json, run against both parts.

    The record carries no content code, so every phrase on every body list has
    to be absent from both decoded parts. validate_corpus.py checks the same
    thing from the rendered file; this catches it before the file is written.
    The two lists the design excludes from the phrase pass are excluded here
    too: one is a proportion judgment over Spanish stopwords that sit inside
    English words, and the other is a single-word list the corpus also puts
    inside quoted examples.
    """
    with open(os.path.join(CORPUS, "spec", "enums.json"), encoding="utf-8") as handle:
        enums = json.load(handle)
    phrases = enums["content_phrases"]
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = ("\n".join(plain_part(record)) + "\n"
            + "\n".join(html_part(record))).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    entry = None
    for candidate in spec["emails"]:
        if candidate["id"] == EMAIL_ID:
            entry = candidate
            break
    if entry is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if entry["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if entry["sender_address"] != SENDER or entry["recipient"] != RECIPIENT:
        raise SystemExit("addresses do not match the manifest")
    if entry["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if entry["reply_to"] is not None:
        raise SystemExit("the manifest gives a Reply-To; this file renders none")
    if entry["url_hosts"] != ["quotes.slatemoorsupply.example"]:
        raise SystemExit("url_hosts do not match the manifest")
    if entry["attachment"]["filename"] != "Quote_Q-5518_Compressor_Parts.pdf":
        raise SystemExit("attachment filename does not match the manifest")
    if entry["auth"] != {"spf": "pass", "dkim": "fail", "dmarc": "pass"}:
        raise SystemExit("auth results do not match the manifest")
    if entry["injection"] is not None:
        raise SystemExit("the manifest carries an injection; this file renders none")
    if sentence_count(LURE_SUMMARY) != 2:
        raise SystemExit("lure_summary must be exactly two sentences")
    if sentence_count(REFERENCE_SUMMARY) != 2:
        raise SystemExit("reference_summary must be exactly two sentences")
    for text in (BODY_BRIEF, LURE_SUMMARY, MANIFEST_NOTES):
        if "—" in text or "–" in text or "TODO" in text:
            raise SystemExit("manifest prose must hold no dash character and no TODO")

    content_phrase_audit(attachment_record(seed))

    data, record = build_eml(seed)
    os.makedirs(EML_DIR, exist_ok=True)
    with open(EML_PATH, "wb") as handle:
        handle.write(data)

    # Read it back the way the week 1 helper does.
    parsed = email.message_from_bytes(data, policy=email.policy.default)
    if parsed.defects:
        raise SystemExit("defects: " + repr(parsed.defects))
    parts = []
    for part in parsed.walk():
        if part.defects:
            raise SystemExit("part defects: " + repr(part.defects))
        if part.get_content_maintype() == "text":
            parts.append(part.get_content())
    if len(parts) != 2:
        raise SystemExit("expected exactly two text parts")
    for text in parts:
        if text.count(BANNER_PLAIN) != 1:
            raise SystemExit("the gateway banner must appear once in each part")
        if text.count(record["filename"]) != 1:
            raise SystemExit("the gateway notice must name the file once per part")
        if text.count(LINK) < 1:
            raise SystemExit("a part lost the quote portal link")
        if TOTAL_LINE not in text:
            raise SystemExit("a part lost the quote total")
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    if str(parsed["From"]) != SENDER_DISPLAY + " <" + SENDER + ">":
        raise SystemExit("unfolded From is " + repr(str(parsed["From"])))
    if parsed["Reply-To"] is not None or parsed["In-Reply-To"] is not None:
        raise SystemExit("this message carries neither Reply-To nor In-Reply-To")

    entry["body_brief"] = BODY_BRIEF
    entry["lure_summary"] = LURE_SUMMARY
    entry["notes"] = MANIFEST_NOTES
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    new_record = ground_truth(record)
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = new_record
            break
    else:
        records.append(new_record)
        records.sort(key=lambda existing: existing["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
