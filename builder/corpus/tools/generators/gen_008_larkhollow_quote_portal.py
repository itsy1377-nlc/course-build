#!/usr/bin/env python3
"""Regenerate 008-larkhollow-quote-portal.

Rebuilds emails/teaching/008-larkhollow-quote-portal.eml byte for byte from the
corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record and edits no data file: every
supporting fact this email needs is already in data/, and the generator reads
those files rather than restating them.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n)    = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = the first n bytes of
                       sha256("<seed>|<email id>|<label>|0")
                       || sha256("<seed>|<email id>|<label>|1") || ...

    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 72

Nothing calls time, random or uuid4 without a seeded hex. The only value in the
file that is not seed derived is the DKIM t= tag, and it is not meant to be: it
is the Unix time of the sender-side Received stamp, computed here from that
same stamp string so the two cannot drift apart.

The synthetic 2048 bit signature verifies nothing. No .example domain can
publish a DKIM key, and the course reads the gateway's Authentication-Results
verdict rather than recomputing a signature, which is what an analyst does.

What this email is, and why every header looks innocent:

  * larkhollow-controls.example is attacker owned. data/domain_policy.json
    records it with owner_class attacker, its own SPF record (mx -all), the
    DKIM selector lh1 and a published DMARC record with policy none. The
    attacker owns the domain, so he publishes for it and collects spf=pass,
    dkim=pass and dmarc=pass. The three passes prove the mail came from the
    domain it names. They prove nothing about whether that domain should be
    trusted, which is the whole lesson of the week 4 reputation case.
  * The SPF mechanism on the Received-SPF line, the DKIM selector on the
    signature and the DMARC policy on the Authentication-Results line are all
    read from data/domain_policy.json, so the rendered headers cannot disagree
    with the record the corpus claims the domain publishes.
  * The scan result is clean and the spam score is 2.2, both from the manifest
    received_path_hint. The gateway had nothing to complain about, and a
    student who waits for the gateway to call this one bad waits forever.
  * The display name Larkhollow Controls Quotes is the attacker's own invented
    brand. data/display_names.json carries it under unowned_display_names, so
    the week 3 display-name check resolves it to no owner and reports nothing.
    That is a checked state here, not an oversight, and the generator asserts
    it.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. Emeric Dawodu is on mailstore-01, and
that is the store whatever path a message took to reach him.

Body wording rules, all from the content_phrases lists in spec/enums.json. The
record carries exactly one content code, content:credential_request on the
phrase "sign in", so no phrase from any other content list may appear in either
decoded part; tools/validate_corpus.py checks that both ways.

  * Every content:urgency_keywords phrase is out. There is no deadline, no
    "today", no "expires in" and no "as soon as possible". The quote is simply
    good for 30 days, which is how a quote is normally written, and the lead
    time is stated as a fact about the controllers rather than as a countdown.
  * "invoice", "past due", "remit", "net 30" and "amount due" are out
    (content:payment_request). A quote is not a bill: it carries a total and a
    validity period and asks for no money.
  * "download" and "shared with you" are out (content:file_share_lure). The
    quote is described as being in the vendor's portal and the link is
    labelled "View quote in portal".
  * "new account", "new bank" and the rest of content:payment_change_request
    are out, as are the content:banking_instruction phrases. Note that "wire"
    is one of them and would match inside "wiring", so no wiring is mentioned
    anywhere in a controls quote that could easily have named some.
  * "was changed" and "if you did not" are out
    (content:account_change_notice). The line that invites a correction is
    written as "If the counts look off against your list".
  * "call me" and "reply by email" are out (content:phone_verification_offered
    and content:channel_restriction). The extension in the signature is a
    signature line, not an instruction, and the reply invitation names this
    message, which is the channel it arrived on.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
because a real inside sales mailbox sends from and reads one address; no
In-Reply-To and no References, so thread:new holds; no
X-Sentrywick-Removed-Attachment, so attachment:none holds; no Auto-Submitted,
because a person wrote this one; no X-Priority and no Importance, because there
is no pressure in this email at all. That absence is the point: the body is
clean, the headers are clean, and only check_sender_reputation exposes it.

Run:  python3 corpus/tools/generators/gen_008_larkhollow_quote_portal.py
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

EMAIL_ID = "008-larkhollow-quote-portal"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
DISPLAY_NAMES_PATH = os.path.join(CORPUS, "data", "display_names.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
ALLOWLIST_PATH = os.path.join(CORPUS, "data", "url_allowlist.json")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
UNLISTED_PATH = os.path.join(CORPUS, "data", "url_unlisted.json")
REPUTATION_PATH = os.path.join(CORPUS, "data", "sender_reputation.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

ORG_DOMAIN = "pellgrave.example"

SENDER_DISPLAY = "Larkhollow Controls Quotes"
SENDER_DOMAIN = "larkhollow-controls.example"
SENDER = "quotes@" + SENDER_DOMAIN
# The envelope sender is the From mailbox. The attacker owns the domain, so he
# has no reason to split the two: an aligned MAIL FROM is what turns his own
# published SPF record into spf=pass and then into dmarc=pass.
ENVELOPE_SENDER = SENDER
RECIPIENT = "e.dawodu@" + ORG_DOMAIN
REPORTER = RECIPIENT

SUBJECT = "Quote Q-2291 ready: Rookmere chiller controls"

# The sending infrastructure, all inside the attacker's own domain. The border
# hop uses an RFC 5737 documentation address and so does the node behind it.
SENDER_HOST = "mail." + SENDER_DOMAIN
SENDER_IP = "203.0.113.155"
ORIGIN_HOST = "app-02." + SENDER_DOMAIN
ORIGIN_IP = "192.0.2.155"

GATEWAY = "mx." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.10"

SCAN_RESULT = "clean"
SPAM_SCORE = "2.2"

# The one link. Its host is a subdomain of the sending domain, so it is not a
# lookalike of anything and it is on neither URL list: check_urls returns
# unlisted, which is the second half of the week 4 lesson. The two tools cover
# different things, and the tool that settles this message is the other one.
LINK_HOST = "portal." + SENDER_DOMAIN
LINK = "https://" + LINK_HOST + "/quotes/Q-2291"
LINK_LABEL = "View quote in portal"

# Timestamps. The sender side stamps UTC and the receiving side stamps -0500,
# and 18:26 +0000 is the same instant as 13:26 -0500, so the Message-ID stamp,
# the Date and the whole Received chain agree. Date sits three seconds before
# the bottom hop, well inside the 120 second window the verifier allows.
DATE_HEADER = "Wed, 15 Apr 2026 13:26:00 -0500"
SUBMIT_STAMP = "Wed, 15 Apr 2026 18:26:03 +0000"
SUBMIT_UTC = "2026-04-15 18:26:03"
GATEWAY_STAMP = "Wed, 15 Apr 2026 13:26:06 -0500"
STORE_STAMP = "Wed, 15 Apr 2026 13:26:08 -0500"
MESSAGE_ID_STAMP = "20260415182600"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break. The HTML part here is written as short source lines,
# so only the gateway banner runs long, and it holds no space a break could
# usefully land on. The wrap is a hard one at 75 characters plus the "=",
# stepping back if a break would otherwise fall inside an "=XX" escape.
QP_MAX = 76

# RFC 6376 sec. 3.5 folds the b= tag across continuation lines. 72 base64
# characters per line keeps every line inside the 78 character fold width.
DKIM_FOLD = 72


# ---------------------------------------------------------------- seed values

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
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def signature(seed):
    """A 2048 bit synthetic signature: 256 seed bytes, 344 base64 characters."""
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


def dkim_time():
    """Unix time of the sender-side Received stamp, so the two cannot drift."""
    return calendar.timegm(time.strptime(SUBMIT_UTC, "%Y-%m-%d %H:%M:%S"))


# ------------------------------------------------------------- data files

def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def recipient_record(address):
    for record in load(RECIPIENTS_PATH)["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(address):
    """The mailbox this file was pulled from and the one store that holds it.

    The recipient is a person, so the message is delivered to him directly and
    the LMTP hop names his own store. No list expansion is involved, so the
    addressee and the reporter are the same mailbox.
    """
    entry = recipient_record(address)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + address)
    return entry["name"], store


def domain_policy(domain):
    for record in load(DOMAIN_POLICY_PATH)["domains"]:
        if record["domain"] == domain:
            return record
    raise SystemExit("domain_policy.json has no record for " + domain)


def spf_mechanism(domain):
    """The mechanism an SPF pass is credited to, as the evaluator reports it.

    larkhollow-controls.example publishes "mx -all", so a client that is one of
    the domain's own MX hosts matches the leading mx mechanism and the gateway
    reports mechanism=mx. The terminal -all is what a non-matching client would
    have fallen through to, and is not what happened here.
    """
    record = domain_policy(domain)["spf"]
    if not record:
        raise SystemExit(domain + " publishes no SPF record")
    return record.split()[0]


def check_display_name_is_unowned():
    """The display name resolves to no owner, so the week 3 check reports nothing."""
    table = load(DISPLAY_NAMES_PATH)
    for entry in table["names"]:
        names = [entry["display_name"]] + list(entry.get("aliases") or [])
        for name in names:
            if name.lower() == SENDER_DISPLAY.lower():
                raise SystemExit(SENDER_DISPLAY + " has an owner entry in display_names.json")
    for entry in table["unowned_display_names"]:
        if entry["display_name"] == SENDER_DISPLAY:
            if entry["sending_domain"] != SENDER_DOMAIN:
                raise SystemExit(SENDER_DISPLAY + " is recorded on another sending domain")
            return
    raise SystemExit(SENDER_DISPLAY + " is missing from unowned_display_names in display_names.json")


def check_link_host_is_unlisted():
    """The link host is on neither list, which is what url:host_unlisted means."""
    good = load(KNOWN_GOOD_PATH)
    if LINK_HOST in good["internal_hosts"] or LINK_HOST.endswith(good["internal_suffix"]):
        raise SystemExit(LINK_HOST + " is on the internal known-good list")
    for entry in load(BLOCKLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL blocklist")
    for entry in load(ALLOWLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL allowlist")
    if LINK_HOST not in load(UNLISTED_PATH)["hosts"]:
        raise SystemExit(LINK_HOST + " is missing from data/url_unlisted.json")


def reputation(domain):
    for record in load(REPUTATION_PATH)["domains"]:
        if record["domain"] == domain:
            return record
    raise SystemExit("sender_reputation.json has no record for " + domain)


# ---------------------------------------------------------------- body text
#
# The manifest body_brief is the brief: a plain business note that the quote is
# ready, a total, a validity period, one link into the vendor portal, and the
# sentence that the portal wants a work email address. The register is an
# inside sales rep writing to a buyer he believes he is quoting, so the message
# carries the small specifics such mail carries: a quote number, a line count,
# a lead time and a direct extension. Nothing in it argues for itself, and
# nothing in it hurries the reader. That is what makes the record medium rather
# than easy: read on its own the body is benign, and the verdict comes from a
# tool.

HEADING = "Quote Q-2291: Rookmere chiller controls package"

PARA_READY = [
    "Your quote Q-2291 for the Rookmere chiller controls package is",
    "ready. It covers the six BAS controllers, the two differential",
    "pressure sensors and the panel retrofit, with commissioning labor",
    "priced on its own line.",
]

# The detail block. The HTML part renders these four lines as one paragraph
# with <br> between them and the total in bold, so both parts carry the same
# four lines in the same order.
DETAIL_LINES = [
    "Quote number: Q-2291",
    "Prepared for: Pellgrave Mechanical Group",
]
TOTAL_LINE = "Total: 42,750.00 USD"
VALID_LINE = "Good for: 30 days from the date of this message"

PARA_LEAD = [
    "Lead time on the controllers is running six to eight weeks from",
    "release, so the schedule in the quote assumes a release in the",
    "first half of May.",
]

# The credential ask, and the only content phrase in the file: "sign in". It is
# written the way a portal notice writes it, as a fact about the site rather
# than as a demand, which is why the body-only read of this email is benign.
PARA_PORTAL = [
    "The portal will ask you to sign in with your work email address the",
    "first time you open a quote. From there you can accept it, ask for",
    "a revision, or leave a note on any line item and it comes straight",
    "to me.",
]

PARA_COUNTS = [
    "If the counts look off against your list, reply to this message",
    "with what you have and I will reprice it.",
]

# A person's signature: a name, a function, the company and a direct extension.
# 555-0163 is inside the 555-0100 through 555-0199 fictional range.
SIGNATURE_LINES = [
    "Dale Okorie",
    "Inside Sales",
    "Larkhollow Controls",
    "555-0163 ext. 218",
]


def greeting(name):
    """Hello, then the first name from data/recipients.json."""
    return "Hello " + name.split()[0] + ","


def plain_part(name):
    lines = [BANNER_PLAIN, ""]
    lines += [HEADING, ""]
    lines += [greeting(name), ""]
    lines += PARA_READY + [""]
    lines += DETAIL_LINES + [TOTAL_LINE, VALID_LINE, ""]
    lines += PARA_LEAD + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += PARA_PORTAL + [""]
    lines += PARA_COUNTS + [""]
    lines += SIGNATURE_LINES
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def detail_html():
    block = [line + "<br>" for line in DETAIL_LINES]
    block[0] = "<p>" + block[0]
    block.append("<b>" + TOTAL_LINE + "</b><br>")
    block.append(VALID_LINE + "</p>")
    return block


def signature_html():
    block = [line + "<br>" for line in SIGNATURE_LINES[:-1]]
    block[0] = "<p>" + block[0]
    block.append(SIGNATURE_LINES[-1] + "</p>")
    return block


def html_part(name):
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f2f2f2;">',
        BANNER_HTML,
        '<div style="max-width:600px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#222222;">',
        '<p style="margin:0 0 18px 0;font-size:17px;font-weight:bold;',
        '  color:#1b4f8a;">' + HEADING + "</p>",
        "<p>" + greeting(name) + "</p>",
    ]
    lines += paragraph_html(PARA_READY)
    lines += detail_html()
    lines += paragraph_html(PARA_LEAD)
    # The href is the same address the plain part prints and the button text is
    # the same label, so a reader of either part sees where the link goes. No
    # image, no script, no form, no hidden text.
    lines += [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#1b4f8a;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
    ]
    lines += paragraph_html(PARA_PORTAL)
    lines += paragraph_html(PARA_COUNTS)
    lines += signature_html()
    lines += ["</div>", "</body>", "</html>"]
    return lines


# ------------------------------------------------------- quoted-printable

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


# ------------------------------------------------------------------- render

def words(lines):
    """The visible words of an HTML or plain block, tags removed."""
    text = " ".join(lines)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


# Phrase lists in spec/enums.json whose codes this record does not carry. If any
# of these strings turns up in either rendered part, validate_corpus.py fails the
# file, so the generator refuses to write it first and says which phrase it was.
FORBIDDEN_PHRASES = (
    "action required", "action needed", "immediately", "within 24 hours",
    "within the hour", "urgent", "final notice", "expires in", "lapses on",
    "last chance", "before the cutoff", "by end of day", "ends in 48 hours",
    "same-day", "today", "as soon as possible", "credit hold",
    "past due", "invoice", "remit", "payment is due", "net 15", "net 30",
    "amount due", "new bank", "new account", "updated remittance", "new ach",
    "changed banks", "new routing", "move the payment", "pay today",
    "earlier run", "hold the run", "hold the payment", "positive pay exception",
    "approve or return", "decision required", "wire", "send me the names",
    "w-2", "employee list", "badge access list", "gift card", "between us",
    "don't mention", "confidential", "keep it quiet", "quietly", "surprise",
    "email only", "can't take calls", "cannot take a call", "reply by email",
    "phone lines are down", "sent from my phone", "new cell", "personal mail",
    "personal address", "acting up", "wifi blocks", "not working",
    "shared a file", "shared with you", "a file was shared",
    "sent you a document", "download", "secure share", "was changed",
    "if you did not", "call the number on file", "call me", "call his extension",
)

REQUIRED_PHRASE = "sign in"


def build_eml(seed):
    check_display_name_is_unowned()
    check_link_host_is_unlisted()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + ORIGIN_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)
    policy = domain_policy(SENDER_DOMAIN)
    dmarc_policy = policy["dmarc_policy"]
    selector = policy["dkim_selector"]
    mechanism = spf_mechanism(SENDER_DOMAIN)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        # RFC 5321 sec. 4.4: the mailbox store prepends the final delivery hop.
        # A mailbox lives on exactly one store, so this host follows the
        # recipient and never the arrival path.
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # RFC 8601 sec. 4: the gateway writes Authentication-Results above its
        # own trace field. All three checks pass, and they pass for a domain
        # the attacker owns, which is exactly the point of this email.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + selector,
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN
        + " policy.dmarc=" + dmarc_policy,
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=" + mechanism,
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_HOST,
        "  (" + SENDER_HOST + " [" + SENDER_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + SENDER_HOST + " with ESMTPSA id " + sender_id + ";",
        "  " + SUBMIT_STAMP,
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
        "To: " + name + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        # 76 characters on one line, so the field never folds. Nothing in the
        # corpus folds a Message-ID, and the tools that scan for one read it
        # off a single line, which is why the originating host is app-02 rather
        # than a longer name that would have pushed the field past 78.
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain_part(name)
    lines += [
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(name))
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    # The two parts say the same thing. The HTML part bolds the total and wraps
    # the detail block in one paragraph, so compare the words rather than the
    # lines.
    for label, plain_block, html_block in (
            ("ready", PARA_READY, paragraph_html(PARA_READY)),
            ("detail", DETAIL_LINES + [TOTAL_LINE, VALID_LINE], detail_html()),
            ("lead", PARA_LEAD, paragraph_html(PARA_LEAD)),
            ("portal", PARA_PORTAL, paragraph_html(PARA_PORTAL)),
            ("counts", PARA_COUNTS, paragraph_html(PARA_COUNTS)),
            ("signature", SIGNATURE_LINES, signature_html())):
        if words(plain_block) != words(html_block):
            raise SystemExit("the two parts differ in the " + label + " block")

    plain_text = "\n".join(plain_part(name)).lower()
    html_text = "\n".join(html_part(name)).lower()
    both = plain_text + "\n" + html_text
    if REQUIRED_PHRASE not in plain_text or REQUIRED_PHRASE not in html_text:
        raise SystemExit("both parts must carry the phrase: " + REQUIRED_PHRASE)
    for phrase in FORBIDDEN_PHRASES:
        if phrase in both:
            raise SystemExit("the body carries a phrase this record does not list: " + phrase)
    if plain_text.count(BANNER_PLAIN.lower()) != 1 or html_text.count(BANNER_PLAIN.lower()) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if plain_text.count(LINK.lower()) != 1 or html_text.count(LINK.lower()) != 1:
        raise SystemExit("the link must appear once in each part")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A plain business note from an inside sales rep, with nothing in it that "
    "argues for itself. Heading 'Quote Q-2291: Rookmere chiller controls "
    "package', then 'Hello Emeric,' the way every other person-addressed "
    "external message in the teaching set opens. First paragraph: the quote "
    "for the Rookmere chiller controls package is ready, and it covers six BAS "
    "controllers, two differential pressure sensors and the panel retrofit, "
    "with commissioning labor priced on its own line. A four line detail block "
    "of quote number, 'Prepared for: Pellgrave Mechanical Group', 'Total: "
    "42,750.00 USD' and 'Good for: 30 days from the date of this message', so "
    "the total and the validity period are stated the way a quote states them "
    "and not as a deadline. A lead time of six to eight weeks on the "
    "controllers. One link, labelled 'View quote in portal', to "
    "https://portal.larkhollow-controls.example/quotes/Q-2291, the only link "
    "in either part. Then the sentence that carries the whole lure: the portal "
    "will ask you to sign in with your work email address the first time you "
    "open a quote. Close by inviting a correction if the counts look off, and "
    "sign it 'Dale Okorie, Inside Sales, Larkhollow Controls, 555-0163 ext. "
    "218'. No urgency phrase, no misspelling, no attachment and no second link "
    "host. Every content phrase list in spec/enums.json other than "
    "content:credential_request is deliberately avoided, so the body reads as "
    "ordinary vendor mail and only check_sender_reputation exposes it."
)

LURE_SUMMARY = (
    "A calm quote notification from a controls vendor the procurement "
    "specialist does not remember contacting, with one link to view the quote "
    "in the vendor's portal. The portal asks the reader to sign in with a work "
    "email address, and the sending domain already carries three reports for "
    "the same trick."
)

MANIFEST_NOTES = (
    "Week 4 reputation case: headers are clean and the body is ordinary; "
    "check_sender_reputation returns known_bad (3 prior reports, campaign "
    "fake-quote-portal, last verdict malicious 2026-03-30) and alone flips the "
    "verdict. The portal host is not yet on the blocklist, so students see "
    "that the two tools cover different things. Auto-contain."
)

# Unchanged from the manifest. The generator writes the list back so that the
# rendered file and the record cannot drift apart, and asserts first that what
# it is about to write is what the record already holds.
MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:known_bad",
    "url:host_unlisted:" + LINK_HOST,
    "url:login_path",
    "content:credential_request",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
]


# ------------------------------------------------------------ ground truth

GT_NOTES = (
    "Attacker-owned domain with a clean record on every header a gateway "
    "writes. larkhollow-controls.example publishes its own SPF record (mx "
    "-all), signs with selector lh1 and publishes a DMARC record with policy "
    "none, so spf, dkim and dmarc all pass for the domain the message names. "
    "The passes prove only that the attacker owns larkhollow-controls.example, "
    "which is why auth:all_pass carries polarity N and counts for nothing in "
    "the tier rule. The display name Larkhollow Controls Quotes is the "
    "attacker's own invented brand: display_names.json carries it under "
    "unowned_display_names, no legitimate sender owns it, so the week 3 "
    "display-name check resolves it to no entry and reports nothing, and there "
    "is no sender:display_name_claims_vendor here to find. Key facts: "
    "from_domain larkhollow-controls.example; reply_to none; spf pass; dkim "
    "pass; dmarc pass (policy none); scan result clean and spam score 2.2, so "
    "the gateway verdict argues for the message rather than against it; "
    "url_hosts portal.larkhollow-controls.example, one link that appears once "
    "in each body part; no attachment; no In-Reply-To. Received chain: "
    "app-02.larkhollow-controls.example [192.0.2.155] submitted with ESMTPSA "
    "to mail.larkhollow-controls.example at 18:26:03 +0000, which handed off "
    "with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] at 13:26:06 "
    "-0500, delivered by LMTP to mailstore-01.pellgrave.example at 13:26:08 "
    "-0500; Date is 13:26:00 -0500, the same instant as 18:26:00 +0000 in the "
    "Message-ID. url:login_path is recorded on the strength of the link text "
    "rather than the path: the vocabulary entry in spec/enums.json reads 'a "
    "link path or text asks for a sign-in', the path /quotes/Q-2291 is an "
    "ordinary quote path, and the sentence beside the link is what asks, so "
    "the recorded value names both. The only content phrase in the file is "
    "'sign in' (content:credential_request, polarity PB), and no phrase from "
    "any other list in spec/enums.json appears in either part, which is what "
    "keeps the body innocent. Playbook rule 7: an unlisted host is unknown, "
    "not clean, and unknown is not what settles this one. Difficulty medium: "
    "one decisive malicious fact (sender:known_bad), no pressure toward "
    "benign, and no injection, so the base tier is easy; body_only_read is "
    "benign, the opposite of the verdict, and that reversal adds the step that "
    "makes it medium. body_only_read is benign because the body alone is an "
    "ordinary quote notification: it names a real job, states a total and a "
    "validity period, hurries nobody and asks for nothing but a click, so a "
    "careful reader with no tools closes it. Week 4 loop: "
    "check_sender_reputation returns known_bad at domain level, first seen "
    "2026-03-02, four messages in 90 days, three prior reports, last report "
    "malicious on 2026-03-30, campaign tag fake-quote-portal, which is "
    "decisive on the first call, so the loop stops after one step with "
    "stop_reason decisive_malicious. check_urls would return unlisted for "
    "portal.larkhollow-controls.example and settle nothing, which is the "
    "contrast the week 4 lesson needs: the two tools cover different things, "
    "and the host of a brand new phishing portal is normally on neither list. "
    "Does not escalate: an ordinary credential phish to an ordinary mailbox "
    "with no interaction and no financial or endpoint impact is auto-contained "
    "under the rule table, so escalate_expected is false and the action is "
    "block_and_purge: block the host, purge copies, reply to the reporter. The "
    "recipient is the procurement specialist, an ordinary mailbox with no "
    "flags; his one prior report is tagged vendor-notice and closed benign, "
    "and a credential ask implies no campaign tag under "
    "prior_similar_report_rule, so recipient:prior_similar_report does not "
    "apply. Deliberate omissions, matching the manifest indicator list: no "
    "Reply-To, no X-Priority, no Importance, no Auto-Submitted, no "
    "X-Originating-IP, and no attachment stub. There is no pressure anywhere "
    "in this file, which is the point of it."
)

GT_INDICATORS = [
    {"code": "auth:all_pass", "where": "Authentication-Results",
     "value": ("spf=pass smtp.mailfrom=larkhollow-controls.example; dkim=pass "
               "header.d=larkhollow-controls.example header.s=lh1 "
               "header.i=@larkhollow-controls.example; dmarc=pass "
               "header.from=larkhollow-controls.example policy.dmarc=none")},
    {"code": "sender:known_bad", "where": "check_sender_reputation",
     "value": SENDER_DOMAIN},
    {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
    {"code": "url:login_path", "where": "body",
     "value": (LINK + "; The portal will ask you to sign in with your work "
               "email address")},
    {"code": "content:credential_request", "where": "body", "value": "sign in"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External",
     "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
     "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
]

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [4],
    "date": "2026-04-15T13:26:00-05:00",
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
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:known_bad", "content:credential_request"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "known_bad",
            "first_seen": "2026-03-02",
            "messages_90d": 4,
            "prior_reports": 3,
            "last_report_verdict": "malicious",
            "last_report_date": "2026-03-30",
            "campaign_tag": "fake-quote-portal",
            "new_domain": False,
            "notes": "Fake controls vendor; quote portal harvests credentials.",
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "unlisted"},
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
    "expected_loop": {"tools": ["check_sender_reputation"],
                      "stop_reason": "decisive_malicious"},
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "block_and_purge",
    "reference_summary": ("This quote is bait: the sender's domain has been "
                          "reported three times for fake quote portals that "
                          "steal passwords. We have blocked it, and you did "
                          "not lose anything by reporting it."),
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
    spec = load(SPEC_PATH)
    seed = spec["seed"]

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)

    # The manifest is the specification. Every semantic field the file renders
    # is read from it and checked, never redecided here.
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_address"] != SENDER or record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender does not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("the manifest carries a Reply-To this file does not render")
    if record["date"] != GROUND_TRUTH["date"]:
        raise SystemExit("date does not match the manifest")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest carries an attachment or an injection")
    if sorted(record["indicators"]) != sorted(MANIFEST_INDICATORS):
        raise SystemExit("the indicator list this file writes back differs from the manifest")
    for field in ("verdict", "category", "difficulty", "body_only_read",
                  "arrival_path", "escalate_expected", "escalation_reasons",
                  "recommended_action", "required_indicators", "weeks"):
        if record[field] != GROUND_TRUTH[field]:
            raise SystemExit("ground truth " + field + " differs from the manifest")
    for method in ("spf", "dkim", "dmarc"):
        if record["auth"][method] != GROUND_TRUTH["auth"][method]:
            raise SystemExit("auth " + method + " differs from the manifest")
    if record["tool_expectations"] != GROUND_TRUTH["tool_expectations"]:
        raise SystemExit("tool_expectations differ from the manifest")
    if record["expected_loop"] != GROUND_TRUTH["expected_loop"]:
        raise SystemExit("expected_loop differs from the manifest")
    # The reputation record is the fact the whole email turns on, so the
    # expectation is compared with data/sender_reputation.json rather than
    # trusted.
    rep = reputation(SENDER_DOMAIN)
    expected = GROUND_TRUTH["tool_expectations"]["check_sender_reputation"]
    for key in ("status", "first_seen", "messages_90d", "prior_reports",
                "last_report_verdict", "last_report_date", "campaign_tag",
                "new_domain", "notes"):
        if rep[key] != expected[key]:
            raise SystemExit("check_sender_reputation " + key
                             + " disagrees with sender_reputation.json")

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
    if str(parsed["Message-ID"]).strip() != ("<" + MESSAGE_ID_STAMP + "."
                                             + hexid(seed, "message-id") + "@"
                                             + ORIGIN_HOST + ">"):
        raise SystemExit("unfolded Message-ID is " + repr(str(parsed["Message-ID"])))
    # Checklist item 17: the decoded HTML part carries the banner snippet on one
    # line, so the quoted-printable fold has to come back out.
    html = parsed.get_payload(1).get_content()
    if html.count(BANNER_HTML) != 1:
        raise SystemExit("the decoded HTML part lost the banner snippet")

    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            entry["indicators"] = list(MANIFEST_INDICATORS)
            entry["body_brief"] = BODY_BRIEF
            entry["lure_summary"] = LURE_SUMMARY
            entry["notes"] = MANIFEST_NOTES
            break
    write_json(SPEC_PATH, spec)

    truth = load(GT_PATH)
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
    print("updated the manifest record and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
