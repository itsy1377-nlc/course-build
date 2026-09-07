#!/usr/bin/env python3
"""Regenerate 037-marlstone-april-invoice.

Rebuilds emails/batch/037-marlstone-april-invoice.eml byte for byte from the
corpus seed, refreshes the prose fields of its own record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

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
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Only the 2048 bit signature needs the block indexed stream, because a single
SHA-256 digest is 32 bytes and b= is 256. bh= is exactly one digest, so it is
taken from the plain hash. Neither value verifies: no .example domain can
publish a key, and this message is one where the gateway said dkim=fail
anyway. The DKIM t= value is not seed derived and is not meant to be. It is
the Unix time of the sender-side Received stamp, computed here from that same
stamp string so the two cannot drift apart.

Three values are read back from the data files rather than typed here, so the
rendered headers cannot disagree with the corpus:
data/recipients.json gives mailstore-01 as the one store that holds the
accounts payable mailbox; data/attachments.json gives the archived file's
name, size, action, type and reason, with its sha256 checked against the rule
sha256("<seed>|<email id>|<filename>") before the header is written; and
data/domain_policy.json gives the DMARC policy on the Authentication-Results
line and the vendor's DKIM selector.

Why the headers look the way they do. This is the real monthly invoice from a
vendor the organization has paid since 2022, and every authentication check on
it fails:

  * Marlstone moved its outbound mail to relay-2.marlstonefleet.example on
    2026-04-13, and data/domain_policy.json records that its SPF and DKIM were
    not updated with the move. The gateway therefore writes spf=softfail, the
    result a record ending "~all" produces for a sender it does not list, and
    the Received-SPF mechanism is that ~all. The record domain_policy.json
    publishes for the vendor is "ip4:203.0.113.44/31 ~all", and that block
    runs from 203.0.113.44 through 203.0.113.45, so it does not cover
    relay-2 at 203.0.113.47, the relay address the manifest's
    received_path_hint fixes, and the softfail is reachable under a strict
    evaluation. The published block read "/30" until the 2026-09 manifest
    pass: /30 runs through .47 and so covered the relay, which made the
    softfail unreachable and contradicted the data file's own note, "Moved
    to relay-2 on 2026-04-13; SPF and DKIM not yet updated". Narrowing it
    moved no bytes here, because Received-SPF quotes only
    client-ip=203.0.113.47 and mechanism=~all, never the block.
  * relay-2 appends the company's new legal disclaimer paragraph to the body
    on the way out, after the billing application signed the message. The body
    hash in bh= no longer describes the body that arrived, so the gateway
    writes dkim=fail. The disclaimer is the last paragraph of the author's
    text in both parts, which is where a relay appended footer lands.
  * Neither an aligned SPF pass nor an aligned DKIM pass is left, so DMARC
    fails against the quarantine policy marlstonefleet.example publishes.

The gateway quarantined it on that verdict at 06:48 on Friday 24 April. It
appeared in the next working day's quarantine digest, and the accounts payable
specialist released it on Monday 27 April at 07:41:20 because the April
invoice was expected and had not arrived, then reported it. That is why
X-Sentrywick-Scan-Result reads released-from-quarantine and why the store's
LMTP hop is stamped three days after the gateway hop: release is a delivery,
not a second receipt, so timestamps still never increase from the top of the
chain downward. 006 renders a one day gap for the same reason.

X-Sentrywick-Removed-Attachment carries action=quarantined with
reason=archived-to-vault, which is the gateway doing its normal document
policy rather than finding anything wrong: the invoice PDF went to the file
vault and the recipient retrieves it there. The body notice in both parts says
so in those words. This is the fact the record exists to teach, next to 032,
where a removed attachment really is the verdict.

The recipient is a shared mailbox rather than a distribution list, so the
message is delivered to it directly and the LMTP hop names the mailbox itself.
The reporter appears only in X-Sentrywick-Reported-By, because a shared
mailbox is worked by several people and the person who pressed report is not
the addressee.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, because a billing clerk sends from the mailbox she reads and the
record's reply_to is null; no In-Reply-To and no References, so thread:new
holds; no X-Originating-IP, which is reserved for webmail submissions; no
X-Mailer; no Auto-Submitted, because a person pressed send on a run the
billing system prepared; no X-Priority and no Importance, because a monthly
invoice applies no urgency and the body carries no urgency phrase either.

Run:  python3 corpus/tools/generators/gen_037_marlstone_april_invoice.py
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

EMAIL_ID = "037-marlstone-april-invoice"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "billing@marlstonefleet.example"
SENDER_DISPLAY = "Marlstone Fleet Services Billing"
SENDER_DOMAIN = "marlstonefleet.example"
# The envelope sender is the From mailbox. A billing coordinator sends from the
# mailbox she reads, so Return-Path and From are one address and the record's
# reply_to is null rather than a repeat of From.
ENVELOPE_SENDER = SENDER
RECIPIENT = "ap@pellgrave.example"
RECIPIENT_DISPLAY = "Accounts Payable"
REPORTER = "p.castellanos@pellgrave.example"

SUBJECT = "April lease invoice 2026-04-PMG and telematics statement"

# The vendor's new outbound relay, the one the SPF record does not cover, and
# the billing host behind it that submitted the run. 203.0.113.47 is RFC 5737
# TEST-NET-3 and 192.0.2.64 is TEST-NET-1, so neither address routes anywhere.
SENDER_RELAY = "relay-2.marlstonefleet.example"
SENDER_RELAY_IP = "203.0.113.47"
SENDER_SUBMIT_HOST = "MFS-BILL-04.marlstonefleet.example"
SENDER_SUBMIT_IP = "192.0.2.64"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"
SCAN_RESULT = "released-from-quarantine"
SPAM_SCORE = "5.3"

# The one link. Its host is the vendor's own customer portal, the fact
# url:host_allowlisted keys on, and its path is an invoice path rather than a
# sign-in path.
LINK = "https://portal.marlstonefleet.example/invoices/2026-04-PMG"
LINK_LABEL = "View in portal"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 11:48 +0000 is the same instant as 06:48 -0500, so the Message-ID stamp,
# the Date and the two upper Received lines agree. The store hop is Monday,
# because the gateway quarantined the message on Friday and the mailbox owner
# released it from the next working day's digest.
DATE_HEADER = "Fri, 24 Apr 2026 06:48:00 -0500"
SUBMIT_STAMP = "Fri, 24 Apr 2026 11:48:02 +0000"
SUBMIT_UTC = "2026-04-24 11:48:02"
GATEWAY_STAMP = "Fri, 24 Apr 2026 06:48:06 -0500"
STORE_STAMP = "Mon, 27 Apr 2026 07:41:20 -0500"
MESSAGE_ID_STAMP = "20260424114800"

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
# record carries content:payment_request and no other content code, so no
# phrase from any other content list may appear in either decoded part;
# validate_corpus.py checks both ways and main() checks it again here.
#
#   Every content:urgency_keywords phrase is out, "today" and "by friday"
#   included. A monthly invoice on net 30 terms applies no pressure, and the
#   pressure this record is scored on is the authentication block, not the
#   prose.
#   "sign in", "log in", "password" and "credentials" are out: an invoice asks
#   for money on terms already agreed and never for an identity.
#   "download" is out (content:file_share_lure), so the invoice is described as
#   being on the portal and the link is labelled "View in portal".
#   "new bank", "new account", "new routing", "changed banks" and the rest of
#   content:payment_change_request are out, and the remit-to is stated as the
#   one already on file. That is the whole point of the file: the real vendor
#   invoice changes nothing about where money goes, and 023 is the forged CFO
#   note that tries to change exactly that for this vendor.
#   "confidential" is out (content:secrecy_request), which is why the appended
#   legal disclaimer is written without the word every real disclaimer opens
#   with. It says the same thing in plainer words.
#   "call me" and the rest of content:phone_verification_offered are out. The
#   number in the signature is a signature line, not an instruction, and it is
#   the channel the out of band verification this record expects will use.
#   "wire" is out (content:banking_instruction): the remit is to a bank account
#   the organization already pays.
#
# The result is a body that reads exactly as benign as it is. The difficulty
# lives entirely in the header block, which is what makes this the hard case:
# a model that treats dmarc=fail as proof of phishing produces a false
# positive here.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

HEADING = "Marlstone Fleet Services, Billing"
SALUTATION = "Hello,"

PARA_OPENING = [
    "Attached is invoice 2026-04-PMG for the April lease period on the",
    "eight service units, and with it the April telematics statement for",
    "the same units.",
]

# The three charge lines and the total. The HTML part renders these as one
# paragraph with <br> between the lines and the total in bold, so both parts
# carry the same four lines in the same order and a part-to-part diff is empty.
CHARGE_LINES = [
    "Invoice 2026-04-PMG, issued 4/24, terms net 30",
    "Lease, 8 units, April: $10,760.00",
    "Telematics and data plan, 8 units, April: $1,180.00",
]
TOTAL_LINE = "Amount due by 5/24: $11,940.00"

PARA_STATEMENT = [
    "The telematics statement is a summary sheet behind the second line,",
    "with mileage and idle hours per unit. It carries no separate charge.",
]

PARA_REMIT = [
    "Our remit-to has not moved: Kettleford Trust, account ending 6041,",
    "with 2026-04-PMG in the payment reference.",
]

# The vendor's own account of the relay move. It is here because a real vendor
# whose mail started landing in junk on 4/13 would say so, and because it is
# the one line in the body that points at the reason the header block looks
# the way it does. It states the fact and claims nothing about security.
PARA_RELAY = [
    "One housekeeping note. We moved to a new outbound mail relay on 4/13,",
    "and a few customers have told us our mail has been landing in junk",
    "since. Our systems group is on it.",
]

CLOSING = "Thanks,"

# A person's signature, not a mailbox signature: the name, the function, the
# company and a dialable number with the extension the switchboard answers on.
# 555-0178 is inside the 555-0100 through 555-0199 fictional range and is used
# by no other file in the corpus.
SIGNATURE_LINES = [
    "Ines Bramhall-Okonjo",
    "Billing Coordinator",
    "Marlstone Fleet Services",
    "555-0178 ext. 214",
]

# The paragraph relay-2 appends after the billing application has signed the
# message. It is the reason the gateway wrote dkim=fail, so it renders as the
# last paragraph of the author's text in both parts, below the signature and
# above the gateway's own notice.
DISCLAIMER = [
    "This message is meant for the addressee named above. If it reached you",
    "in error, please delete it and tell us. Marlstone Fleet Services takes",
    "no responsibility for any alteration made to this message after it left",
    "our systems.",
]

# The gateway's notice, in the pieces the two parts assemble it from. Section 2
# of docs/email-header-realism.md fixes the shape, not where a source line may
# end; the verb is "archived to the file vault" rather than "removed" because
# action=quarantined with reason=archived-to-vault is the gateway filing a
# document under normal policy, not stripping a threat.
NOTICE_HEAD = "[Sentrywick Gateway archived 1 attachment to the file vault:"
NOTICE_TAIL = "Details are in the message headers.]"

# Phrases the week 3 extractor keys on, all from content_phrases
# content:payment_request. The generator proves they survive the line breaks
# in both parts.
PAYMENT_PHRASES = ["invoice", "amount due", "net 30", "remit"]


def notice_file(record):
    return record["filename"] + " ({:,} bytes).".format(record["size"])


def plain_part(record):
    lines = [BANNER_PLAIN, ""]
    lines += [HEADING, ""]
    lines += [SALUTATION, ""]
    lines += PARA_OPENING + [""]
    lines += CHARGE_LINES + [TOTAL_LINE, ""]
    lines += PARA_STATEMENT + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_REMIT + [""]
    lines += PARA_RELAY + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE_LINES + [""]
    lines += DISCLAIMER + [""]
    lines += [NOTICE_HEAD, notice_file(record), NOTICE_TAIL]
    return lines


def joined(lines):
    return " ".join(lines)


def charge_html():
    block = [line + "<br>" for line in CHARGE_LINES]
    block[0] = "<p>" + block[0]
    block.append("<b>" + TOTAL_LINE + "</b></p>")
    return block


def html_part(record):
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f1f2f3;">',
        BANNER_HTML,
        '<div style="max-width:620px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#1f1f1f;">',
        '<p style="margin:0 0 18px 0;font-size:17px;font-weight:bold;',
        '  color:#1f4a5a;">' + HEADING + "</p>",
        "<p>" + SALUTATION + "</p>",
        "<p>" + joined(PARA_OPENING) + "</p>",
    ]
    lines += charge_html()
    lines += ["<p>" + joined(PARA_STATEMENT) + "</p>"]
    # The href is the same address the plain part prints and the button text is
    # the same label, and the address is repeated underneath in plain sight, so
    # a reader of either part can see where the link goes. No image, no script,
    # no form, no hidden text.
    lines += [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#1f4a5a;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
        '<p style="font-size:13px;color:#555555;">If the button does not open,',
        "the address is " + LINK + "</p>",
    ]
    lines += ["<p>" + joined(PARA_REMIT) + "</p>"]
    lines += ["<p>" + joined(PARA_RELAY) + "</p>"]
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
                  + "@" + SENDER_RELAY + ">")
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
        # own trace field. All three checks fail here, and they fail for the
        # vendor's own domain, which is the fact the week 7 batch turns on: a
        # failure names a domain, and this domain is one we have paid since
        # 2022.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=softfail smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=fail header.d=" + SENDER_DOMAIN + " header.s=" + selector,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=fail header.from=" + SENDER_DOMAIN
        + " policy.dmarc=" + dmarc_policy,
        "Received-SPF: softfail (" + GATEWAY + ": domain of transitioning",
        "  " + ENVELOPE_SENDER + " does not designate " + SENDER_RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_RELAY_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_RELAY + "; identity=mailfrom; mechanism=~all",
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
        "Received: from " + SENDER_RELAY,
        "  (" + SENDER_RELAY + " [" + SENDER_RELAY_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + SENDER_SUBMIT_HOST + " ([" + SENDER_SUBMIT_IP + "])",
        "  by " + SENDER_RELAY + " with ESMTPSA id " + sender_id + ";",
        "  " + SUBMIT_STAMP,
        # The billing application signed the message on that hop. relay-2 then
        # appended the legal disclaimer, so bh= describes a body that is no
        # longer the body that arrived and the gateway wrote dkim=fail.
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
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += qp_body(html_part(record))
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii"), record


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "The vendor's usual invoice mail: April lease invoice 2026-04-PMG, eight "
    "service units, lease 10,760.00 plus telematics and data 1,180.00, "
    "'amount due by 5/24' 11,940.00 on 'net 30', with the April telematics "
    "statement described as a summary sheet behind the second line. The "
    "remit-to is stated as the one already on file and unmoved (Kettleford "
    "Trust, account ending 6041). One link, 'View in portal', to "
    "https://portal.marlstonefleet.example/invoices/2026-04-PMG, printed as "
    "an address in both parts. Use 'invoice', 'amount due', 'net 30' and "
    "'remit' and no phrase from any other content list, so the body reads as "
    "benign as it is. One housekeeping line says the company moved to a new "
    "outbound mail relay on 4/13 and that customer mail has been landing in "
    "junk since. Sign with a name (Ines Bramhall-Okonjo, Billing "
    "Coordinator), the company and a direct number with an extension. Below "
    "the signature, the legal disclaimer paragraph relay-2 appends after "
    "signing, which is what broke DKIM; it avoids the word confidential so "
    "that content:secrecy_request stays absent. End both parts with the "
    "gateway notice that Marlstone_Invoice_2026-04-PMG.pdf (52,994 bytes) was "
    "archived to the file vault."
)

LURE_SUMMARY = (
    "The real fleet vendor's monthly invoice arrives with every "
    "authentication check failing, because the vendor moved to a new outbound "
    "relay on 4/13 and that relay appends a legal disclaimer after the "
    "billing system has signed the message. The one link goes to the vendor's "
    "allowlisted portal, the amounts match the lease, the remit-to is "
    "unchanged, and the invoice PDF was archived to the vault rather than "
    "stripped."
)

MANIFEST_NOTES = (
    "Benign with escalation: an authentication failure on a trusted sender "
    "means someone confirms with the vendor and closes. The archived invoice "
    "PDF shows that a removed attachment is not evidence. A model that treats "
    "dmarc=fail as proof of phishing produces a false positive here. "
    "Rendering: spf=softfail for relay-2.marlstonefleet.example "
    "[203.0.113.47], the outbound relay the vendor moved to on 2026-04-13 "
    "without updating its published SPF and its signing; dkim=fail with "
    "d=marlstonefleet.example s=mfs1 because that relay appends the legal "
    "disclaimer after the billing system signs; "
    "dmarc=fail against the published quarantine policy because neither "
    "aligned check passed. The gateway quarantined it on that verdict and "
    "accounts payable released it from the next working day's digest, so "
    "X-Sentrywick-Scan-Result is released-from-quarantine and the store's "
    "LMTP hop is stamped Mon 27 Apr while the gateway hop is Fri 24 Apr; "
    "release is a delivery, not a second receipt. Escalation reasons: "
    "auth_failure_on_trusted_sender."
)


# ------------------------------------------------------------ ground truth

REFERENCE_SUMMARY = (
    "This is Marlstone's real April invoice, but their mail failed our "
    "authentication checks because they changed mail servers this month. We "
    "will confirm with them by phone before it is paid; nothing about it "
    "looks like fraud."
)

NOTES = (
    "The week 7 batch case that punishes reading the authentication block as "
    "a verdict. Key facts a correct extractor produces: from_domain "
    "marlstonefleet.example under the display name Marlstone Fleet Services "
    "Billing, which display_names.json records as a name that domain owns, so "
    "display_name_mismatch is false; no Reply-To, so there is no Reply-To "
    "mismatch to find; spf=softfail on marlstonefleet.example, dkim=fail with "
    "d=marlstonefleet.example s=mfs1, dmarc=fail with policy quarantine, so "
    "all three checks fail and nothing is aligned; one link host, "
    "portal.marlstonefleet.example, carrying the single link "
    "https://portal.marlstonefleet.example/invoices/2026-04-PMG, whose path "
    "is an invoice path and not a sign-in path; one "
    "X-Sentrywick-Removed-Attachment naming Marlstone_Invoice_2026-04-PMG.pdf "
    "with action quarantined and reason archived-to-vault; scan result "
    "released-from-quarantine, spam score 5.3; no In-Reply-To, so the message "
    "opens a thread. Why every check failed, and why none of it is an attack: "
    "domain_policy.json records that Marlstone moved to relay-2 on 2026-04-13 "
    "and updated neither its SPF record nor its signing, so the gateway "
    "resolved the relay against a record ending ~all and wrote softfail with "
    "mechanism ~all, and that same relay appends the company's legal "
    "disclaimer to the body after the billing application signed it, which is "
    "why the body hash no longer matches (dkim=fail) and why neither aligned "
    "check is left for DMARC. Received chain: "
    "MFS-BILL-04.marlstonefleet.example [192.0.2.64] submitted with ESMTPSA "
    "to relay-2.marlstonefleet.example at 11:48:02 +0000, which handed off "
    "with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 06:48:06 "
    "-0500, and the message was quarantined there; accounts payable released "
    "it from the digest on Monday, so the LMTP hop to "
    "mailstore-01.pellgrave.example is stamped 07:41:20 -0500 on 27 April. "
    "Timestamps still never increase from the top of the chain downward, "
    "because release is a delivery and not a second receipt; 006 renders the "
    "same gap for the same reason. Date is 06:48:00 -0500, the same instant "
    "as 11:48:00 +0000 in the Message-ID. Body phrases the extractor keys on, "
    "present in both parts: 'invoice', 'amount due', 'net 30' and 'remit', "
    "all content:payment_request. The body carries no urgency phrase, no "
    "credential ask, no data ask and no bank change: it names the invoice "
    "number, the eight service units, the two charge lines and the total, "
    "states the remit-to as the one already on file at Kettleford Trust, and "
    "says once that the company moved to a new outbound mail relay on 4/13 "
    "and that its mail has been landing in junk since. The appended legal "
    "disclaimer is written without the word confidential on purpose, because "
    "that word would add content:secrecy_request to a message that keeps no "
    "secret. recipient:prior_similar_report does not apply: a plain payment "
    "request implies no campaign tag under prior_similar_report_rule, and the "
    "sender record carries no campaign tag either, even though the mailbox "
    "holds two vendor-invoice-fraud reports and one invoice-malware report. "
    "Difficulty reason: the tier rule counts no decisive benign fact, because "
    "the allowlisted sender is only decisive when dmarc passes and here it "
    "fails, against four pressure facts (auth:dkim_fail, auth:dmarc_fail, "
    "header:released_from_quarantine and content:payment_request), so "
    "pressure exceeds decisive and the base tier is hard; the body-only read "
    "is benign, which agrees with the verdict, and there is no injection, so "
    "neither adjustment applies and it stays hard. For the instructor: this "
    "is the false positive the week 7 batch is built to catch. Ungrounded, "
    "three failed checks and a quarantine release read as phishing. Grounded, "
    "the facts answer: check_sender_reputation returns trusted for "
    "marlstonefleet.example, first seen 2022-09-01, 41 messages in 90 days, "
    "one prior report closed benign on 2026-02-05; check_urls returns "
    "allowlisted for portal.marlstonefleet.example; lookup_recipient shows a "
    "shared accounts payable mailbox that handles payments. Nothing in the "
    "body states any tool result, so the loop has to fetch them, and no "
    "single result is decisive against a header block this bad, so the run "
    "calls all three tools in turn and ends on tools_exhausted. The verdict "
    "is benign because no fact points at an attack, and it still escalates "
    "under auth_failure_on_trusted_sender, which is the rule that says a "
    "human confirms with the vendor by phone before the invoice is paid and "
    "then closes it. Full credit on the indicators criterion needs "
    "auth:dmarc_fail, sender:allowlisted_domain and url:host_allowlisted. "
    "Story context: this is the invoice 039 asks accounts payable to pay "
    "early and the one 023 forges a CFO note about, claiming Marlstone "
    "changed banks; this message is the record that shows the remit-to never "
    "moved. Grading note: a student who calls this malicious because three "
    "checks failed has skipped the tools, and a student who treats the "
    "archived PDF as evidence has read a removed-attachment header without "
    "reading its reason."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-24T06:48:00-05:00",
        "verdict": "benign",
        "category": "legit_external",
        "difficulty": "hard",
        "body_only_read": "benign",
        "sender_display": SENDER_DISPLAY,
        "sender_address": SENDER,
        "reply_to": None,
        "recipient": RECIPIENT,
        "reporter": REPORTER,
        "reported_after_interaction": False,
        "subject": SUBJECT,
        "arrival_path": "external_gateway",
        "auth": {"spf": "softfail", "dkim": "fail", "dmarc": "fail",
                 "dmarc_policy": "quarantine"},
        "indicators": [
            {"code": "auth:spf_softfail", "where": "Authentication-Results",
             "value": "spf=softfail smtp.mailfrom=marlstonefleet.example"},
            {"code": "auth:dkim_fail", "where": "Authentication-Results",
             "value": ("dkim=fail header.d=marlstonefleet.example "
                       "header.s=mfs1 header.i=@marlstonefleet.example")},
            {"code": "auth:dmarc_fail", "where": "Authentication-Results",
             "value": ("dmarc=fail header.from=marlstonefleet.example "
                       "policy.dmarc=quarantine")},
            {"code": "auth:dmarc_fail_owned_domain",
             "where": "Authentication-Results",
             "value": "header.from=marlstonefleet.example"},
            {"code": "header:released_from_quarantine",
             "where": "X-Sentrywick-Scan-Result",
             "value": "released-from-quarantine"},
            {"code": "sender:allowlisted_domain",
             "where": "check_sender_reputation", "value": SENDER_DOMAIN},
            {"code": "url:host_allowlisted", "where": "check_urls",
             "value": "portal.marlstonefleet.example"},
            {"code": "content:payment_request", "where": "body",
             "value": "invoice; amount due; net 30; remit"},
            {"code": "attachment:archived_to_vault",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:shared_mailbox", "where": "lookup_recipient",
             "value": RECIPIENT},
        ],
        "required_indicators": ["auth:dmarc_fail", "sender:allowlisted_domain",
                                "url:host_allowlisted"],
        "url_hosts": ["portal.marlstonefleet.example"],
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
                "first_seen": "2022-09-01",
                "messages_90d": 41,
                "prior_reports": 1,
                "last_report_verdict": "benign",
                "last_report_date": "2026-02-05",
                "campaign_tag": None,
                "new_domain": False,
                "notes": "Fleet vendor; allowlisted.",
                "match_level": "domain",
            },
            "check_urls": {"portal.marlstonefleet.example": "allowlisted"},
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
        # No tool result is decisive against a header block with three failed
        # checks in it, so all three run and the loop ends with no tool left to
        # try rather than on a decisive result or the step cap.
        "expected_loop": {
            "tools": ["check_sender_reputation", "check_urls",
                      "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
        "escalate_expected": True,
        "escalation_reasons": ["auth_failure_on_trusted_sender"],
        "recommended_action": "verify_out_of_band_then_close",
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


def content_phrase_audit(seed, record):
    """Every content phrase list in enums.json, run against both parts.

    The record carries content:payment_request and nothing else, so the four
    phrases it names have to be present and every phrase on every other body
    list has to be absent. validate_corpus.py checks the same thing from the
    rendered file; this catches it before the file is written.
    """
    with open(os.path.join(CORPUS, "spec", "enums.json"), encoding="utf-8") as handle:
        enums = json.load(handle)
    phrases = enums["content_phrases"]
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    # The design excludes these two from the phrase pass: one is a proportion
    # judgment over Spanish stopwords that sit inside English words, and the
    # other is a single-word list the corpus also puts inside quoted examples.
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = ("\n".join(plain_part(record)) + "\n"
            + "\n".join(html_part(record))).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if code == "content:payment_request":
            if not hits:
                raise SystemExit("the body carries no content:payment_request phrase")
        elif hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")
    for phrase in PAYMENT_PHRASES:
        if phrase not in phrases["content:payment_request"]:
            raise SystemExit(phrase + " is not in the content:payment_request list")


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
    if entry["url_hosts"] != ["portal.marlstonefleet.example"]:
        raise SystemExit("url_hosts do not match the manifest")
    if entry["attachment"]["filename"] != "Marlstone_Invoice_2026-04-PMG.pdf":
        raise SystemExit("attachment filename does not match the manifest")
    if entry["auth"] != {"spf": "softfail", "dkim": "fail", "dmarc": "fail"}:
        raise SystemExit("auth results do not match the manifest")
    if sentence_count(LURE_SUMMARY) != 2:
        raise SystemExit("lure_summary must be exactly two sentences")
    if sentence_count(REFERENCE_SUMMARY) != 2:
        raise SystemExit("reference_summary must be exactly two sentences")
    for text in (BODY_BRIEF, LURE_SUMMARY, MANIFEST_NOTES):
        if "—" in text or "–" in text or "TODO" in text:
            raise SystemExit("manifest prose must hold no dash character and no TODO")

    content_phrase_audit(seed, attachment_record(seed))

    data, record = build_eml(seed)
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
            raise SystemExit("a part lost the portal link")
        for phrase in PAYMENT_PHRASES:
            if phrase not in text.lower():
                raise SystemExit("a part lost the phrase: " + phrase)
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
