#!/usr/bin/env python3
"""Regenerate 042-cottonmoor-early-bird-pricing.

Rebuilds emails/batch/042-cottonmoor-early-bird-pricing.eml byte for byte from
the corpus seed, refreshes the prose fields this generator owns in
spec/corpus-spec.json, and upserts the ground truth record in
ground_truth.json. Every semantic field in the manifest record is read and
never written, so the label and the file cannot drift, and no other record is
touched.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n)       = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, count)  = sha256("<seed>|<id>|<label>|<n>") for n = 0, 1, 2 ...
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh               = base64(stream("dkim-bh", 32))
    DKIM b                = base64(stream("dkim-b", 256))

Nothing calls time, random or uuid4(). Neither DKIM value verifies: they are
seeded bytes of the right length, the convention the rest of the corpus uses,
because no .example domain can publish a key and no lab checks a signature.
The DKIM t= value is the Unix time of the Date header, 1776878760 for
Wed, 22 Apr 2026 12:26:00 -0500, so the signature timestamp and the stamped
time are the same instant.

What this email is. A trade show organizer the company exhibited with last
year pushes its early-bird booth rate with a countdown. It is spam by the
corpus definition, unwanted commercial mail, and benign by the verdict,
because it impersonates nobody, asks for no credential, no payment change and
no data, carries no attachment and links only to the organizer's own
registration page. The medium tier comes out of the tier rule and not out of
a judgment call: one decisive benign fact, the gateway spam score of 5.9 at
or above the 5.0 threshold with no ask code in the body, and one point of
pressure the other way, content:urgency_keywords, which gives base medium.

Why the authentication headers read the way they do. The message crosses the
border gateway on the ordinary external path, so it carries
Authentication-Results, Received-SPF, X-Sentrywick-External: yes and the
gateway banner at the top of both body parts. The organizer sends from its
own mail host, which its SPF record covers on the mx mechanism, and signs
with the selector data/domain_policy.json records for it, so spf and dkim
both pass on cottonmoor-show.example, both align with the From domain, and
DMARC passes against the policy that domain publishes, none. All three
passing is the lesson: authentication proves the mail came from the domain it
names and says nothing about whether the mail is wanted.

Why there are no list headers. The manifest fixes arrival_path
external_gateway and lists neither header:list_headers_present nor
header:precedence_bulk, so this file carries no List-Unsubscribe, no
List-Unsubscribe-Post, no List-Id, no Precedence and no Feedback-ID. That is
what separates it from 003, which is the same category through a bulk
provider: this one is a person at the show office writing from the show's own
mail server to one returning exhibitor, so there is no campaign platform, no
per-recipient tracking token and no bounce domain. The absence is also what
makes the case medium rather than easy, because the bulk list headers that
settle 003 are not here to settle this one.

Headers deliberately absent, matching the manifest indicator list: no
Reply-To, no In-Reply-To and no References (thread:new), no
X-Sentrywick-Removed-Attachment (attachment:none), no X-Priority and no
Importance, no Auto-Submitted, no X-Originating-IP, which is reserved for
webmail submissions, and no X-Mailer, which would only invite a reader to
link this sender to an unrelated one that shares a client name.

Run:  python3 corpus/tools/generators/gen_042_cottonmoor_early_bird_pricing.py
"""

import base64
import email
import email.policy
import email.utils
import hashlib
import json
import os
import uuid

EMAIL_ID = "042-cottonmoor-early-bird-pricing"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
REPUTATION_PATH = os.path.join(CORPUS, "data", "sender_reputation.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
ALLOWLIST_PATH = os.path.join(CORPUS, "data", "url_allowlist.json")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
UNLISTED_PATH = os.path.join(CORPUS, "data", "url_unlisted.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

ORG_DOMAIN = "pellgrave.example"
GATEWAY = "mx." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.10"

# The show organizer. data/sender_reputation.json holds it at status neutral,
# first seen 2025-03-11, two messages in 90 days and no prior reports: seen
# before, never reported, never vouched for. That is the status that leaves
# the reputation tool with nothing decisive to say.
SHOW_DOMAIN = "cottonmoor-show.example"
SENDER = "registration@" + SHOW_DOMAIN
SENDER_DISPLAY = "Cottonmoor Facilities Show"
# The envelope sender is the From mailbox. A small show office sending from
# its own server has no bounce domain to hide behind and no Reply-To split,
# so Return-Path, smtp.mailfrom and From are one address.
ENVELOPE_SENDER = SENDER

RECIPIENT = "l.vashti@" + ORG_DOMAIN
REPORTER = RECIPIENT

SUBJECT = "Early-bird booth pricing ends in 48 hours"

# The sending path. mail.<domain> is the host the domain's SPF record covers,
# so SPF passes on the mx mechanism; the sales desk workstation behind it
# submits over authenticated submission, which is what ESMTPSA records.
SENDER_HOST = "mail." + SHOW_DOMAIN
SENDER_IP = "203.0.113.171"
ORIGIN_HOST = "CM-SALES-0231." + SHOW_DOMAIN
ORIGIN_IP = "192.0.2.171"

# The one link, on the organizer's own registration page. No login path, no
# token, no query string: the address is the same for every exhibitor who
# reads it, which is one of the things that separates this from a phish.
LINK_HOST = SHOW_DOMAIN
LINK = "https://" + LINK_HOST + "/2026/exhibit"

# Date is 12:26:00 -0500, so the sales desk and the Message-ID stamp read
# 17:26 UTC while the gateway and the mail store stamp in local time.
MESSAGE_ID_STAMP = "20260422172600"
DATE_LOCAL = "Wed, 22 Apr 2026 12:26:00 -0500"
SENDER_STAMP = "Wed, 22 Apr 2026 17:26:02 +0000"
GATEWAY_STAMP = "Wed, 22 Apr 2026 12:26:04 -0500"
STORE_STAMP = "Wed, 22 Apr 2026 12:26:07 -0500"
# Unix time of the Date header.
DKIM_TIME = "1776878760"

SPAM_SCORE = "5.9"
SCAN_RESULT = "suspect"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">'
               "[External message. Sentrywick Gateway]</p>")


def hexid(seed, label, length=12):
    return hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def store_id(seed):
    digest = hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


# ------------------------------------------------------------- data files
#
# Every fact below is read out of corpus/data/ rather than repeated here, and
# the checks raise when a data file stops agreeing with the headers this
# generator writes. The data files are complete for all 56 emails and this
# generator writes to none of them.

def recipient_record(address):
    for record in load(RECIPIENTS_PATH)["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(address):
    """The mailbox this file was pulled from and the one store that holds it.

    The To address is a named person rather than a distribution list, so the
    message is delivered to that mailbox itself and the LMTP hop names the
    store recipients.json gives it. Every mailbox in the corpus lives on
    exactly one store, so this hop follows the recipient and never the path
    the message arrived on.
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
    """The mechanism an SPF evaluation reports for a permitted sender.

    cottonmoor-show.example publishes "mx -all", so a client that is one of
    the domain's own MX hosts matches on mx and the gateway reports
    mechanism=mx. The trailing all mechanism is the one a client outside the
    record falls through to, so it is never the mechanism that passes.
    """
    record = domain_policy(domain)["spf"]
    if not record:
        raise SystemExit(domain + " publishes no SPF record")
    mechanisms = [token for token in record.split() if not token.endswith("all")]
    if not mechanisms:
        raise SystemExit(domain + " has no SPF mechanism that can pass")
    return mechanisms[0]


def dkim_selector(domain):
    """dkim=pass needs a published selector, and the data file names it."""
    selector = domain_policy(domain)["dkim_selector"]
    if not selector:
        raise SystemExit(domain + " publishes no DKIM selector; dkim=pass is wrong")
    return selector


def dmarc_policy(domain):
    """dmarc=pass carries the policy the domain publishes, here none."""
    published = domain_policy(domain)["dmarc_policy"]
    if published is None:
        raise SystemExit(domain + " publishes no DMARC record; dmarc=pass is wrong")
    return published


def check_reputation_is_neutral():
    """No sender: indicator belongs on this file, and the data file says why.

    check_spec.py derives sender:known_good, sender:allowlisted_domain and
    sender:first_seen straight from this record, and the manifest lists none
    of them. Status neutral with new_domain false is the only combination
    that produces that, so the absence of a sender code is a data-file fact.
    """
    for record in load(REPUTATION_PATH)["domains"]:
        if record["domain"] == SHOW_DOMAIN:
            if record["status"] != "neutral":
                raise SystemExit(SHOW_DOMAIN + " is " + record["status"]
                                 + " in sender_reputation.json, not neutral")
            if record["new_domain"]:
                raise SystemExit(SHOW_DOMAIN + " is flagged new_domain; "
                                 "sender:first_seen would be required")
            return
    raise SystemExit(SHOW_DOMAIN + " has no sender_reputation.json record")


def check_link_host_is_unlisted():
    """url:host_unlisted means on neither list, not internal, and recorded."""
    known_good = load(KNOWN_GOOD_PATH)
    if (LINK_HOST in known_good["internal_hosts"]
            or LINK_HOST.endswith(known_good["internal_suffix"])):
        raise SystemExit(LINK_HOST + " is on the internal known-good list")
    for entry in load(ALLOWLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL allowlist")
    for entry in load(BLOCKLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL blocklist")
    if LINK_HOST not in load(UNLISTED_PATH)["hosts"]:
        raise SystemExit(LINK_HOST + " is missing from data/url_unlisted.json")


# ---------------------------------------------------------------- body text
#
# The register is one person at the show office writing to one returning
# exhibitor she can name: a greeting, a countdown, a reason the reader is
# being offered the good spaces first, a short list of what is left, one
# link, an aside about the hall moving, and a signature with a dialable
# number and an extension. It is pushy, which is what makes it spam, and it
# is ordinary, which is what makes it benign.
#
# Wording rules, all from spec/enums.json content_phrases. The record carries
# exactly one content code, content:urgency_keywords, so the body has to
# carry at least one phrase from that list and no phrase from any other list.
# check_body_phrases() below runs the same test validate_corpus.py runs, on
# every list at once, before the file is written.
#
#   Two urgency phrases appear and no others: "ends in 48 hours" in the first
#   sentence and "last chance" in the sentence that closes the offer. Nothing
#   says "today", "urgent", "immediately", "by Friday" or "this morning",
#   which are entries on the same list and would change the recorded value.
#   The rate change is dated instead, "on Friday, April 24", the way the rest
#   of the corpus writes a deadline: month before day, and checkable.
#   There is no ask code anywhere. No sign-in and no password
#   (content:credential_request), because the registration page is public and
#   the message never mentions an account. No invoice, remittance or amount
#   (content:payment_request) and no bank or account change
#   (content:payment_change_request): the one money sentence says nothing is
#   charged at the reservation step. No file to download or share
#   (content:file_share_lure) and no list of names to send back
#   (content:data_request). That absence is not decoration; the tier rule
#   only counts the 5.9 spam score as a decisive benign fact because no ask
#   code is present, and the playbook only closes a message as spam when it
#   asks for nothing.
#
# The words are written once as the plain-part lines and the HTML part joins
# the same lines with single spaces, so the two parts cannot drift and the
# HTML part hides nothing.

GREETING = "Hi Lenora,"

# The countdown, and the date it resolves to. "ends in 48 hours" is the
# subject line's own phrase, so the message opens on the thing it was named
# for, the way a sales note does.
PARA_1 = [
    "Early-bird booth pricing for the 2026 Cottonmoor Facilities Show",
    "ends in 48 hours. The standard rate sheet takes over on Friday,",
    "April 24, and the corner spaces on the main aisle are usually",
    "spoken for well before that.",
]

# The checkable reference, the way 005 cites an account number and 012 cites
# a quote: last year's stand number. No data file records stands, so nothing
# looks it up, and a director of sales either remembers it or does not.
PARA_2 = [
    "Pellgrave Mechanical Group had stand 214 with us last year, so you",
    "are on the returning exhibitor list. Returning exhibitors get first",
    "pick of the corner spaces before the floor plan opens to everyone",
    "else.",
]

LIST_LEAD = "Still open on the plan:"

BULLETS = [
    "Corner booths, 10 by 20, on the main aisle",
    "Inline booths, 10 by 10, in the mechanical services hall",
    "Two demonstration slots on the service bay stage",
]

LINK_LEAD = "Reserve your booth"

# The second urgency phrase. It is a claim about a price and nothing else:
# no account, no deadline for an action the reader has to take on a system,
# and no consequence beyond paying more for a booth.
PARA_3 = [
    "The early-bird rate is the lowest we publish all year, so this is",
    "the last chance to take a corner space at that price.",
]

# The one sentence about money, and it removes rather than adds an ask.
PARA_4 = [
    "Nothing is charged at the reservation step. The show office sends",
    "the exhibitor paperwork once your space is confirmed.",
]

# The small irregularity a real note carries: an aside that is about the
# reader rather than about the sale.
PARA_5 = [
    "We moved the mechanical hall to the north end of the building this",
    "year, which I think will suit a working demonstration better than",
    "the old room did.",
]

PARA_6 = [
    "If it is easier to talk it through, my extension is below. I am at",
    "my desk most of this week.",
]

CLOSING = "Thanks,"

# The house block for an external human signer: name, role, organization, a
# dialable number in the reserved 555-01xx block with the extension that
# reaches the desk. 555-0148 and extension 231 are used nowhere else in the
# corpus.
SIGNATURE = [
    "Ottoline Farrady",
    "Exhibitor Sales, Cottonmoor Facilities Show",
    "555-0148 ext. 231",
]

HEADING = "Cottonmoor Facilities Show 2026"

# The phrases the week 3 extractor keys on, and the only content list this
# body is allowed to match. build_eml proves both halves of that.
URGENCY_PHRASES = ["ends in 48 hours", "last chance"]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += [LIST_LEAD, ""]
    lines += ["  * " + item for item in BULLETS]
    lines += ["", LINK_LEAD + ":", LINK, ""]
    lines += PARA_3 + [""]
    lines += PARA_4 + [""]
    lines += PARA_5 + [""]
    lines += PARA_6 + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE
    return lines


def html_part():
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#f5f4f1;">',
        BANNER_HTML,
        ('<div style="max-width:620px;margin:20px auto;padding:22px 26px;'
         'background-color:#ffffff;border:1px solid #ded9d0;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#1f1f1f;">'),
        ('<p style="margin:0 0 18px 0;font-size:18px;font-weight:bold;'
         'color:#8a3b12;">' + HEADING + "</p>"),
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        "<p>" + LIST_LEAD + "</p>",
        "<ul>",
    ]
    lines += ["<li>" + item + "</li>" for item in BULLETS]
    lines += [
        "</ul>",
        ('<p style="margin:22px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:11px 20px;'
         'background-color:#8a3b12;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">' + LINK_LEAD + "</a></p>"),
        ('<p style="font-size:13px;color:#555555;">If the button does not '
         "open, the address is " + LINK + "</p>"),
        "<p>" + joined(PARA_3) + "</p>",
        "<p>" + joined(PARA_4) + "</p>",
        "<p>" + joined(PARA_5) + "</p>",
        "<p>" + joined(PARA_6) + "</p>",
        "<p>" + CLOSING + "</p>",
        "<p>" + "<br>".join(SIGNATURE) + "</p>",
        "</div>",
        "</body>",
        "</html>",
    ]
    return lines


# ------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters
# including the trailing soft break, and a soft break may not split an =XX
# escape. The generator breaks at the last space that leaves the line at 74
# characters or fewer, so the break lands between words wherever the text
# allows one, and falls back to a hard break for an unbroken run such as a
# CSS declaration. The space is carried to the start of the next physical
# line, so an unfolded paragraph is the same string it went in as. The
# fallback guard never lets a break land inside an "=3D" escape, which
# matters on every line of this part: each HTML attribute's "=" encodes as
# "=3D".
SOFT_MAX = 76
SPACE_MAX = 74


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks."""
    text = line.replace("=", "=3D")
    out = []
    while len(text) > SOFT_MAX:
        cut = None
        for index in range(min(SPACE_MAX, len(text) - 1), 0, -1):
            if text[index] == " ":
                cut = index
                break
        if cut is None:
            cut = SOFT_MAX - 1
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


# ------------------------------------------------------------ phrase guard

# The two content codes whose phrase lists validate_corpus.py does not treat
# as a membership test: content:non_english_body is Spanish stopwords that sit
# inside ordinary English words, and content:instruction_to_ai is single words
# that appear in quoted examples on benign mail.
PHRASE_PASS_SKIP = ("content:non_english_body", "content:instruction_to_ai")


def check_body_phrases(plain_text, html_text):
    """Run every enums.json body phrase list over both parts, as the validator does.

    validate_corpus.py fails a file whose body carries a phrase the record
    does not list, and fails a record that lists a code no phrase supports.
    This record lists exactly one content code, so the test here is exact:
    content:urgency_keywords matches, with the two phrases the ground truth
    value quotes and no third one, and every other list matches nothing.
    Running it before the file is written means a reworded sentence that
    happens to contain "today" or "download" stops the generator instead of
    surfacing as a validator failure later.
    """
    enums = load(ENUMS_PATH)
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    body = (plain_text + "\n" + html_text).lower()
    for code in sorted(enums["content_phrases"]):
        if code in PHRASE_PASS_SKIP or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in enums["content_phrases"][code]
                if phrase.lower() in body]
        if code == "content:urgency_keywords":
            if sorted(hits) != sorted(URGENCY_PHRASES):
                raise SystemExit("the body matches the urgency phrases "
                                 + repr(sorted(hits)) + "; the record records "
                                 + repr(sorted(URGENCY_PHRASES)))
        elif hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + " but the record lists no such code")


# ------------------------------------------------------------------- render

def build_eml(seed):
    check_reputation_is_neutral()
    check_link_host_is_unlisted()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)
    mechanism = spf_mechanism(SHOW_DOMAIN)
    selector = dkim_selector(SHOW_DOMAIN)
    policy = dmarc_policy(SHOW_DOMAIN)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # Both identities are the show's own domain and both align with the
        # From domain, so DMARC passes against the policy that domain
        # publishes. Three passes prove the mail came from the organizer.
        # They prove nothing about whether the mail was wanted.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + SHOW_DOMAIN + ";",
        "  dkim=pass header.d=" + SHOW_DOMAIN + " header.s=" + selector,
        "    header.i=@" + SHOW_DOMAIN + ";",
        "  dmarc=pass header.from=" + SHOW_DOMAIN + " policy.dmarc=" + policy,
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + ENVELOPE_SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=" + mechanism,
        # The content scanner scored the countdown and the sales pressure at
        # 5.9 and marked the message suspect. It did not quarantine it, and
        # the score is the decisive benign fact the tier rule counts, because
        # no ask code sits under it.
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
        "  " + SENDER_STAMP,
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SHOW_DOMAIN + "; s=" + selector + "; t=" + DKIM_TIME + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: " + DATE_LOCAL,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + name + " <" + RECIPIENT + ">",
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
    lines += plain_part()
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part())
    html_text = "\n".join(html_part())
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    # One link host and one address, in both parts. The plain part carries it
    # once under its own label; the HTML part carries it in the button's href
    # and again as the address a reader can read, which is the same link and
    # the same host.
    if plain_text.count(LINK) != 1:
        raise SystemExit("the plain part must carry the link exactly once")
    if html_text.count(LINK) != 2:
        raise SystemExit("the HTML part must carry the link in the href and "
                         "in the fallback line")
    for phrase in URGENCY_PHRASES:
        if phrase not in plain_text.lower() or phrase not in html_text.lower():
            raise SystemExit("a part lost the urgency phrase: " + phrase)
    for block in (PARA_1, PARA_2, PARA_3, PARA_4, PARA_5, PARA_6):
        if joined(block) not in html_text:
            raise SystemExit("the HTML part lost a paragraph: " + joined(block))
    for item in BULLETS + SIGNATURE:
        if plain_text.count(item) != 1 or html_text.count(item) != 1:
            raise SystemExit("a list item or signature line is not in both "
                             "parts exactly once: " + item)
    check_body_phrases(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------ manifest and ground truth

BODY_BRIEF = (
    "A pushy but ordinary event pitch: early-bird booth pricing 'ends in 48 "
    "hours', last year's exhibitors get first pick of corner booths, one link "
    "'Reserve your booth' to https://cottonmoor-show.example/2026/exhibit. "
    "Use 'ends in 48 hours' and 'last chance'. No sign-in, no payment "
    "details, no attachment. As rendered it is signed mail from one person at "
    "the show office to one returning exhibitor: it opens 'Hi Lenora', says "
    "the early-bird price ends in 48 hours and that the standard rate sheet "
    "takes over on Friday, April 24, names last year's stand 214 as the "
    "reason Pellgrave is on the returning exhibitor list, lists three kinds "
    "of space still open (corner booths 10 by 20 on the main aisle, inline "
    "booths 10 by 10 in the mechanical services hall, two demonstration slots "
    "on the service bay stage), gives the one link under the label 'Reserve "
    "your booth', calls the early-bird rate the last chance at that price, "
    "says nothing is charged at the reservation step, adds an aside about the "
    "mechanical hall moving to the north end, and signs off with Ottoline "
    "Farrady, Exhibitor Sales, and the number 555-0148 ext. 231. The two "
    "urgency phrases are the only content phrases in the body: nothing asks "
    "for a sign-in, a payment, a bank change, a file or a list of names."
)

LURE_SUMMARY = (
    "The organizer of a trade show the company exhibited at last year pushes "
    "early-bird booth pricing with a 48-hour countdown. The link leads to the "
    "organizer's registration page; nothing is impersonated and no "
    "credentials or bank changes are requested."
)

MANIFEST_NOTES = (
    "The medium spam: urgency wording without impersonation, credential "
    "harvest, malware, or a payment change. The organizer is neutral in the "
    "reputation file (seen last year). Real queues carry these; the playbook "
    "closes them as spam and blocks nothing. As rendered the message takes "
    "the ordinary external path rather than a bulk provider, so it carries no "
    "List-Unsubscribe, no Precedence and no tracking token, which is what "
    "separates it from 003: the bulk list headers that settle 003 as easy are "
    "not here to settle this one. All three authentication checks pass on the "
    "organizer's own domain against its published policy of none, which is "
    "the lesson the file is for. The gateway marked it suspect at 5.9, and "
    "that score is the single decisive benign fact the tier rule counts, "
    "because no ask code appears anywhere in the body."
)

NOTES = (
    "The batch set's medium spam case, and the pair to 003. An event "
    "organizer the company exhibited with last year pushes its early-bird "
    "booth rate at a returning exhibitor with a countdown, and asks for "
    "nothing. Key facts: the From domain cottonmoor-show.example under the "
    "display name Cottonmoor Facilities Show, which data/display_names.json "
    "records as that domain's own name, so there is no display-name "
    "mismatch; no Reply-To; Return-Path, smtp.mailfrom and From are the one "
    "address registration@cottonmoor-show.example, because a small show "
    "office sending from its own server has no bounce domain; spf=pass on the "
    "mx mechanism of the record 'mx -all'; dkim=pass with "
    "d=cottonmoor-show.example s=cm1, the selector domain_policy.json "
    "publishes; both identities align with the From domain, so dmarc=pass "
    "with policy.dmarc=none and dmarc_policy none, a published policy of none "
    "rather than a missing record; scan result suspect, spam score 5.9; one "
    "link host, cottonmoor-show.example, carrying one address, "
    "https://cottonmoor-show.example/2026/exhibit, with no login path and no "
    "per-recipient token; no attachment; a new thread. The message arrived "
    "through the gateway on the ordinary external path, not through a bulk "
    "provider, so it carries no List-Unsubscribe, no List-Id, no Precedence "
    "and no Feedback-ID; that absence is deliberate and it is what makes the "
    "case medium rather than easy, since the bulk list headers that settle "
    "003 in one look are not available here. Difficulty reason: one decisive "
    "benign fact, the spam score of 5.9, which the tier rule counts only "
    "because the body carries no ask code, and one point of pressure the "
    "other way, content:urgency_keywords, so base medium; no injection, and "
    "the body-only read is benign, which agrees with the verdict, so neither "
    "adjustment applies. The body carries exactly two phrases from the "
    "urgency list, 'ends in 48 hours' in the opening sentence and 'last "
    "chance' in the sentence that closes the offer, and no phrase from any "
    "other content list: no sign-in or password, no invoice or amount, no "
    "bank or account change, no file to download and no list of names to send "
    "back. Expected action from playbook rule 10: unwanted marketing that "
    "asks for nothing is spam, close it and block nothing, reply to the "
    "reporter, and escalate_expected is false because a benign spam record "
    "collects no escalation reason. Week 7 use: the medium tier of the spam "
    "category, scored against a batch that also holds the easy and hard ends "
    "of it. Tools: check_sender_reputation matches cottonmoor-show.example at "
    "domain level and returns neutral, first seen 2025-03-11, two messages in "
    "90 days and no prior reports, which is the status that decides nothing; "
    "check_urls returns unlisted for the organizer's own host, which playbook "
    "rule 7 reads as unknown rather than clean; lookup_recipient shows Lenora "
    "Vashti, Director of Sales, an ordinary mailbox with three prior reports "
    "and one true positive and no flags. Every tool answers without settling "
    "the case, so the loop runs all three and stops on tools_exhausted. "
    "content:urgency_keywords is not an ask code and the sender record "
    "carries no campaign tag, so recipient:prior_similar_report is absent "
    "under the prior_similar_report_rule even though the mailbox holds two "
    "marketing reports. Grading note: a student who reads three passing "
    "authentication checks as proof the message is wanted has confused "
    "provenance with intent, a student who calls the unlisted link host "
    "malicious has skipped rule 7, and a student who escalates on the "
    "countdown has read a price deadline as an operational one. Rendering "
    "notes: the plain part is 7bit with hard wraps under 78 characters and "
    "the HTML part is quoted-printable, because the fixed gateway banner "
    "snippet is longer than 78 characters; the banner is the first line of "
    "the plain part and the first line after the body tag in the HTML part; "
    "both parts carry the same words and the HTML part hides nothing, so "
    "there is no content:html_hidden_text. The link appears once in the plain "
    "part and twice in the HTML part, in the button's href and in the "
    "fallback line that shows the address, which is one link and one host. "
    "Deliberate omissions, matching the manifest indicator list: no "
    "X-Originating-IP, which is reserved for webmail submissions, so the "
    "sales desk address 192.0.2.171 appears in the bottom Received line "
    "instead; no X-Mailer, no Auto-Submitted, no X-Priority and no "
    "Importance. Every identifier that looks random is a SHA-256 over the "
    "corpus seed, the email id and a label, so the file regenerates byte for "
    "byte."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-22T12:26:00-05:00",
    "verdict": "benign",
    "category": "spam",
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
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=" + SHOW_DOMAIN + "; "
                   "dkim=pass header.d=" + SHOW_DOMAIN + " header.s=cm1 "
                   "header.i=@" + SHOW_DOMAIN + "; "
                   "dmarc=pass header.from=" + SHOW_DOMAIN
                   + " policy.dmarc=none")},
        {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "ends in 48 hours; last chance"},
        {"code": "header:spam_score", "where": "X-Sentrywick-Spam-Score",
         "value": SPAM_SCORE},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["header:spam_score", "content:urgency_keywords"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SHOW_DOMAIN,
            "status": "neutral",
            "first_seen": "2025-03-11",
            "messages_90d": 2,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Trade show organizer; the company exhibited last year.",
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Lenora Vashti",
            "role": "Director of Sales",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 3,
            "true_positive_count_90d": 1,
            "campaign_tags": ["credential-phish", "marketing"],
        },
    },
    "expected_loop": {
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_spam_reply_to_reporter",
    "reference_summary": ("This is a sales push from the trade show we "
                          "exhibited at last year. The countdown is just "
                          "marketing; it asks for nothing sensitive, so we "
                          "closed it as spam."),
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
    spec = load(SPEC_PATH)
    seed = spec["seed"]

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    # Every semantic field is read from the manifest and checked, never
    # written. A disagreement stops the render rather than silently producing
    # a file the label does not describe.
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if record["sender_address"] != SENDER:
        raise SystemExit("sender_address does not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("the manifest record carries a Reply-To")
    if record["date"] != GROUND_TRUTH["date"]:
        raise SystemExit("date does not match the manifest")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest record carries an attachment or an injection")
    if record["auth"] != {"spf": "pass", "dkim": "pass", "dmarc": "pass"}:
        raise SystemExit("auth results do not match the manifest")
    if record["arrival_path"] != "external_gateway":
        raise SystemExit("arrival_path does not match the manifest")
    # An indicator in the manifest is "code" or "code:value", so the code is
    # the first two colon-separated parts. The ground truth carries the same
    # codes as objects with the rendered text in value.
    manifest_codes = {i.split(":")[0] + ":" + i.split(":")[1]
                      for i in record["indicators"]}
    truth_codes = {i["code"] for i in GROUND_TRUTH["indicators"]}
    if manifest_codes != truth_codes:
        raise SystemExit("indicator codes differ from the manifest: "
                         + repr(sorted(manifest_codes ^ truth_codes)))
    for field in ("verdict", "category", "difficulty", "body_only_read",
                  "set", "weeks", "escalate_expected", "escalation_reasons",
                  "recommended_action", "required_indicators",
                  "tool_expectations", "expected_loop", "reference_summary"):
        if record[field] != GROUND_TRUTH[field]:
            raise SystemExit(field + " differs from the manifest")
    # The selector in the recorded auth:all_pass value is the one
    # domain_policy.json publishes and the one the header carries, so the
    # ground truth quotes the rendered text rather than a copy of it.
    auth_value = [i["value"] for i in GROUND_TRUTH["indicators"]
                  if i["code"] == "auth:all_pass"][0]
    if "header.s=" + dkim_selector(SHOW_DOMAIN) not in auth_value:
        raise SystemExit("the recorded auth:all_pass value names a DKIM "
                         "selector domain_policy.json does not publish")

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
    display, address = email.utils.parseaddr(str(parsed["From"]))
    if display != SENDER_DISPLAY or address != SENDER:
        raise SystemExit("unfolded From is " + repr((display, address)))
    # Checklist item 17: the decoded HTML part carries the banner snippet on
    # one line, so the quoted-printable fold has to come back out.
    plain = parsed.get_payload(0).get_content()
    html = parsed.get_payload(1).get_content()
    if html.count(BANNER_HTML) != 1:
        raise SystemExit("the decoded HTML part lost the banner snippet")
    if plain.count(LINK) != 1 or html.count(LINK) != 2:
        raise SystemExit("the link did not survive decoding")
    check_body_phrases(plain, html)

    # The manifest keeps the prose this generator is the source of.
    record["body_brief"] = BODY_BRIEF
    record["lure_summary"] = LURE_SUMMARY
    record["notes"] = MANIFEST_NOTES
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
    print("updated manifest prose and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
