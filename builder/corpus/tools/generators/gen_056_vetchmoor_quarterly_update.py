#!/usr/bin/env python3
"""Regenerate 056-vetchmoor-quarterly-update.

Rebuilds builder/instructor/exam-emails/056-vetchmoor-quarterly-update.eml byte
for byte from the corpus seed, refreshes the prose fields of its own manifest
record in spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

This one is exam-only, so it renders into builder/instructor/exam-emails/ and
never under corpus/emails/. Nothing a student can reach holds it before the
week 8 exam. tools/validate_corpus.py warns that an exam record has no file
under emails/; that warning is correct, and tools/build_corpus.py validates the
rendered file by pointing the validator at the instructor folder with
release/ground_truth_exam.json.

Every identifier in the file that looks random is derived from the corpus seed,
so rerunning this script reproduces the same bytes:

    hexid(label, n)      = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, count) = the first count bytes of
                           sha256("<seed>|<id>|<label>|0")
                           || sha256("<seed>|<id>|<label>|1") || ...

    recipient token       = hexid("recipient-token", 16)
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_sb_" + hexid("boundary", 16)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    provider Received id  = hexid("mta-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(stream("dkim-bh", 32))
    DKIM b=               = base64(stream("dkim-b", 256)), folded at 70

Three of those spellings differ from the shorthand in the build prompt, and all
three follow gen_003_inkmoor_spring_catalog.py, the corpus's other Sendbarrow
mailing and this file's primary template, rather than the shorthand. The same
three divergences are written out in gen_027_benefits_portal_update.py, the
third Sendbarrow file, for the same reason:

    Boundary prefix. The prompt's generic form is "=_part_" plus twelve hex.
    The prefix belongs to whatever composed the message: "=_swk_" is reserved
    for mail the Sentrywick stack composes, "=_part_" is the neutral prefix for
    a third-party platform that composes its own mail, and the two mailings
    Sendbarrow Campaigns 3.8 composed already carry "=_sb_" plus sixteen hex.
    One platform stamping one boundary convention across its mailings is a fact
    an analyst can use; the same platform disagreeing with itself is noise.

    Provider-side Received id. The prompt calls the sender-side id
    hexid("sender-id", 8). Both Sendbarrow files label the outbound MTA hop
    "mta-id", because the hop is stamped by the provider's MTA and not by a
    sender's own submission host, and this file keeps that label.

    DKIM bh=. The prompt's shorthand is base64(sha256("<seed>|<id>|dkim-bh")).
    One digest is 32 bytes, which is the right length for bh=, but b= needs
    256, which no single digest supplies, so 003 and 027 take both tags from
    the block stream and this file does too, so that one construction covers
    both tags.

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab in the course checks a signature. The course reads the
gateway's Authentication-Results verdict instead, which is what RFC 9989
sec. 5.3.6 asks a receiver to write. The DKIM t= value is not seed derived and
is not meant to be: it is the Unix time of the Date header, computed here from
that same stamp string so the signature time and the stamped time cannot drift
apart.

The account 3304, the campaign, the link variant d4 and the compliance path
/compliance/q2-2026 are design constants: the record's received_path_hint and
body_brief pin them, so they are read from the design and not derived. The
campaign appears in two forms, which the design also pins: 0219 in the envelope
sender the received_path_hint fixes, and 219 in the link path the body_brief
fixes. The bounce address and its unsub- mailto twin carry the zero-padded form
and the three tracking links carry the short form, each exactly as its own
pinned string writes it. 027 pins the same pair of forms, 0042 and 42, so the
platform's habit of padding the campaign in a bounce local part and not in a
URL path is a corpus convention rather than a one-off. The per-recipient token
is the one identifier here that is opaque, and it does come out of the seed:
hexid("recipient-token", 16) is 39bf8d1a3a1f59c6, the value the
received_path_hint and the body_brief both already name, so the seed and the
design agree without an edit to either. It ends the bounce address, all three
tracking links, the List-Unsubscribe URL and the unsubscribe mailto, which is
what makes the footer's one-click unsubscribe, a bounce and a click read as the
same mailing to the same subscriber (RFC 8058 sec. 3.1).

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. The To address, the reporter and the
mailbox this file was pulled from are all Tobias Nkemelu, so there is no list
expansion to unwind: recipients.json gives him mailstore-01 and the LMTP hop
names it.

Why the authentication headers read the way they do, and why they are the whole
exam question. The mailing crosses the border gateway, so it carries
Authentication-Results, Received-SPF and X-Sentrywick-External: yes, and both
body parts open with the gateway banner. The provider bounces under its own
domain, so SPF passes on bounce.sendbarrow-mail.example, which does not align.
The signature is the difference from 003 and 027: Sendbarrow signs this mailing
with a key published under the broker's own name, d=vetchmoorbenefits.example
s=sb1, so the DKIM identity is identical to the From domain and DMARC passes on
it. The broker publishes policy quarantine, so the clause carries
policy.dmarc=quarantine, the policy data/domain_policy.json records for
vetchmoorbenefits.example. Three passes on a mailing sent by a third party is
exactly what an aligned provider-hosted key produces, and it still says nothing
about whether the reader wanted the mail. That is the stem: bulk headers are not
a spam verdict, and authentication is not a wantedness verdict. The reader
subscribed, so the category is legit_external rather than spam.

The selector sb1 is the provider's name for a key it hosts on the customer's
behalf, the shape a campaign platform gets from a CNAME under the customer's
_domainkey namespace. data/domain_policy.json records vetchmoorbenefits.example
with dkim_selector vm1, which is the broker's own key on its own mail server;
that field holds one selector per domain, so it cannot also carry the hosted
one. The manifest's received_path_hint pins s=sb1 for this message, so this file
renders sb1 and the divergence is reported rather than fixed here.

The gateway is not suspicious of it: scan result clean and spam score 2.3, both
fixed by the received_path_hint. The score is below the 5.0 threshold, so it
adds nothing to the benign side of the tier rule in tools/check_spec.py; the two
decisive facts are the allowlisted sender with dmarc=pass and the list headers
on a message that asks for nothing.

Headers deliberately absent, matching the record's indicator list: no Reply-To,
because reply_to is null and the platform bounces to its own VERP address; no
In-Reply-To and no References (thread:new); no X-Sentrywick-Removed-Attachment
(attachment:none); no X-Priority and no Importance, because a quarterly
newsletter carries no urgency flag and the body carries no urgency word; and no
X-Originating-IP, which belongs to webmail submissions. Auto-Submitted is absent
as well: a campaign platform sending an opted-in mailing marks itself with
Precedence: bulk and the RFC 8058 list headers, not with the RFC 3834 field for
system-generated replies.

Two header lines run past the 78 character fold width that section 10.1 of the
design recommends, exactly as they do in 003 and 027 and for the same reason:
the 64 character bounce address is one unfoldable token inside a header with
nowhere left to fold. RFC 5322 sec. 2.1.1 allows up to 998, so
validate_corpus.py reports them as a fold-length warning and not a failure, and
build_eml() counts them so that a third one would stop the render.

Run:  python3 corpus/tools/generators/gen_056_vetchmoor_quarterly_update.py
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

EMAIL_ID = "056-vetchmoor-quarterly-update"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EXAM_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EXAM_DIR, EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "newsletter@vetchmoorbenefits.example"
SENDER_DISPLAY = "Vetchmoor Benefits"
# The broker's own domain is the From domain, the DKIM d= domain and the host of
# the one non-tracking link, so there is no envelope-versus-author split for a
# student to chase beyond the provider's bounce address.
BROKER_DOMAIN = "vetchmoorbenefits.example"
RECIPIENT = "t.nkemelu@pellgrave.example"
RECIPIENT_DISPLAY = "Tobias Nkemelu"
RECIPIENT_FIRST_NAME = "Tobias"
REPORTER = "t.nkemelu@pellgrave.example"

SUBJECT = "Q2 compliance update: new dependent verification rules"

# The bulk provider. It owns the bounce domain, the tracking host, the outbound
# MTA and the app node that stamps the Date; it is never a From domain, which is
# what data/domain_policy.json records for it.
PROVIDER = "sendbarrow-mail.example"
BOUNCE_HOST = "bounce." + PROVIDER
LINK_HOST = "links." + PROVIDER
MTA_HOST = "o17.mta." + PROVIDER
MTA_IP = "198.51.100.23"
APP_NODE = "app-node-03." + PROVIDER
APP_NODE_IP = "192.0.2.140"

# The provider-hosted key, published under the broker's name, so the signature
# aligns with the From domain and DMARC passes on DKIM alone. See the docstring.
DKIM_SELECTOR = "sb1"

GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# Design constants. See the module docstring for the two campaign forms.
ACCOUNT = "3304"
CAMPAIGN_ENVELOPE = "0219"
CAMPAIGN_PATH = "219"
LINK_VARIANT = "d4"
COMPLIANCE_PATH = "/compliance/q2-2026"

# Timestamps. The provider's app node stamps the Date, its own Received line and
# the Message-ID in UTC; 13:05 +0000 is the same instant as 08:05 local, which is
# the time the manifest's date field carries. Top to bottom the chain never
# increases in UTC, and the Date sits six seconds before the bottom hop, which is
# how long the app node's queue held the message.
DATE_HEADER = "Tue, 28 Apr 2026 13:05:00 +0000"
DATE_UTC = "2026-04-28 13:05:00"
MESSAGE_ID_STAMP = "20260428130500"
APP_NODE_STAMP = "Tue, 28 Apr 2026 13:05:06 +0000"
GATEWAY_STAMP = "Tue, 28 Apr 2026 08:05:11 -0500"
STORE_STAMP = "Tue, 28 Apr 2026 08:05:13 -0500"

SCAN_RESULT = "clean"
SPAM_SCORE = "2.3"

# The two header lines that run past the 78 character fold width, both because
# the 64 character bounce address is a single unfoldable token. See the module
# docstring; build_eml raises if the count changes.
LONG_LINE_COUNT = 2

# RFC 6376 sec. 3.5 folds the b= tag across continuation lines. 70 base64
# characters per line keeps every line inside the 78 character fold width.
DKIM_FOLD = 70


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


def dkim_time():
    """Unix time of the Date header, so the signature and the stamp agree."""
    return calendar.timegm(time.strptime(DATE_UTC, "%Y-%m-%d %H:%M:%S"))


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient, reporter):
    """The mailbox this file was pulled from and the one store that holds it.

    A person or a shared mailbox receives the message itself, so the LMTP hop
    names the recipient. Only a distribution list needs the reporter's own
    mailbox substituted, because a list is delivered by expansion and the copy
    the corpus keeps is the one that landed in a member's store.
    """
    entry = recipient_record(recipient)
    if entry.get("mailbox_type") == "list":
        entry = recipient_record(reporter)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


# ---------------------------------------------------------------- body text
#
# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries no content code at all, so no phrase from any content list may
# appear in either decoded part. validate_corpus.py checks that both ways, and
# check_no_content_phrases() below runs the same lists over the rendered text so
# the generator fails before the validator does. The lists that came closest to
# being tripped, in a message whose whole subject is verification paperwork:
#
#   "verify your account" and "confirm your account" are out
#   (content:credential_request), along with "sign in", "log in", "password"
#   and "credentials". The subject and the body say "dependent verification",
#   which is the plan's own term for checking a relationship document, and
#   there is no account here to visit and nothing to type: a newsletter that
#   asked the reader to sign in would be a different email, and 013 and 027 are
#   that email.
#   "download" is out (content:file_share_lure). The full write-up is read on
#   the broker's site, not fetched, and the two link labels say "Read the full
#   update" and name the page.
#   "was changed" and "if you did not" are out
#   (content:account_change_notice). The items report rules that changed, in
#   the active voice, because the passive form is the shape a deposit-change
#   scare wears and 050 is the file that wears it honestly.
#   "employee list" and "w-2" are out (content:data_request): nothing is asked
#   for, which is also what keeps header:list_headers_present decisive under
#   the tier rule, since that rule only counts list headers when the message
#   carries no ask code.
#   Every urgency phrase is out (content:urgency_keywords). The one date in the
#   message is the plan-year date the rules attach to, and the deadlines the
#   items describe are the member's ninety days, not the reader's. There is no
#   "today", no "action needed", no "by friday", and nothing "expires in".
#   "call me" is out (content:phone_verification_offered), which also rules out
#   "call member services" in a footer, because the phrase list matches on a
#   run of characters and that line would carry the phrase inside it.
#
# The words are written once and shared by both parts, so a part-to-part diff
# is empty. The two parts differ only in where the lines break, because the
# plain part folds at 72 and the HTML source folds at 76.
PLAIN_WIDTH = 72
ITEM_WIDTH = 69
ITEM_INDENT = "   "
HTML_WIDTH = 76

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

VIEW_PROMPT = "Having trouble reading this?"
VIEW_TEXT = "View it in your browser"
SALUTATION = "Hello " + RECIPIENT_FIRST_NAME + ","

INTRO = ("Three things changed in dependent verification this quarter. Here "
         "is the short version; the full write-up, with the plan language "
         "beside each item, is on our site.")

# Three items, each a numbered heading and one paragraph. A quarterly
# compliance letter from a broker reads like this: what moved, what it replaces,
# and who does the work. Every rule described here is the plan's rule about a
# member's paperwork, so nothing in the items asks the reader for anything.
ITEMS = [
    ("1. Proof of relationship",
     "A court order or an adoption decree now stands in for a birth "
     "certificate when a member adds a stepchild or a foster child. The "
     "documents we took before are still good; this adds two to the list."),
    ("2. Ninety days for a mid-year addition",
     "A member who adds a dependent after a qualifying life event now has "
     "ninety days to send the paperwork, up from sixty. The clock starts on "
     "the date of the event, not the date the member tells us about it."),
    ("3. Sample audits move to a yearly cycle",
     "Starting this fall we review a sample of covered dependents once a "
     "year rather than once every third year. Vetchmoor writes to the member "
     "directly and reports what came back in your quarterly file."),
]

READ_TEXT = "Read the full update"
DIRECT_LEAD = "Or go straight to the compliance page on our site:"

CLOSING = ("Nothing here needs a reply. We will fold the new wording into the "
           "2027 enrollment packet, and your service team will walk through "
           "it with you at the July check-in.")

# A named signer, the way a broker's compliance letter is signed, rather than a
# bare team line: the mailing is a campaign send, but a person wrote it.
SIGNATURE = [
    "Odile Thorsby",
    "Compliance Director, Vetchmoor Benefits",
]

# The postal line stops at a box number: the corpus names no city, state or
# postal code anywhere.
POSTAL = "Vetchmoor Benefits, PO Box 6704"
PERMISSION = ("You are receiving this update because you are the benefits "
              "contact for Pellgrave Mechanical Group.")
UNSUB_TEXT = "Unsubscribe"

BODY_OPEN = '<body style="margin:0;padding:0;background:#f2f5f4;">'
DIV_OPEN = [
    '<div style="max-width:600px;margin:0 auto;padding:24px;background:#ffffff;',
    "font-family:sans-serif;font-size:15px;line-height:1.5;color:#222222;\">",
]
SMALL_STYLE = '<p style="font-size:12px;color:#6b6b6b;">'
SMALL_LINK_STYLE = 'style="color:#6b6b6b;">'
H2_OPEN = '<h2 style="font-size:20px;color:#1f4f5f;">'
ITEM_HEAD_OPEN = '<p style="margin:18px 0 4px 0;font-weight:bold;">'
ITEM_BODY_OPEN = '<p style="margin:0;">'
BUTTON_STYLE = [
    'style="background:#1f4f5f;color:#ffffff;padding:10px 18px;',
    'text-decoration:none;">' + READ_TEXT + "</a></p>",
]


def wrap(text, width):
    """Greedy fold on single spaces, the way a mail composer breaks a line."""
    lines = []
    current = ""
    for word in text.split(" "):
        candidate = (current + " " + word) if current else word
        if current and len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines


def token(seed):
    return hexid(seed, "recipient-token", 16)


def view_url(seed):
    return ("https://" + LINK_HOST + "/v/" + ACCOUNT + "/" + CAMPAIGN_PATH
            + "/" + token(seed))


def update_url(seed):
    return ("https://" + LINK_HOST + "/c/" + ACCOUNT + "/" + CAMPAIGN_PATH + "/"
            + LINK_VARIANT + "/" + token(seed))


def unsub_url(seed):
    return ("https://" + LINK_HOST + "/u/" + ACCOUNT + "/" + CAMPAIGN_PATH
            + "/" + token(seed))


def direct_url():
    return "https://" + BROKER_DOMAIN + COMPLIANCE_PATH


def bounce_address(seed):
    return ("bounce-" + ACCOUNT + "-" + CAMPAIGN_ENVELOPE + "-" + token(seed)
            + "@" + BOUNCE_HOST)


def unsub_address(seed):
    return ("unsub-" + ACCOUNT + "-" + CAMPAIGN_ENVELOPE + "-" + token(seed)
            + "@" + BOUNCE_HOST)


def plain_part(seed):
    lines = [BANNER_PLAIN, ""]
    lines += [VIEW_PROMPT + " " + VIEW_TEXT + ":", view_url(seed), ""]
    lines += [SUBJECT, ""]
    lines += [SALUTATION, ""]
    lines += wrap(INTRO, PLAIN_WIDTH) + [""]
    for heading, text in ITEMS:
        lines += [heading]
        lines += [ITEM_INDENT + line for line in wrap(text, ITEM_WIDTH)]
        lines += [""]
    lines += [READ_TEXT + ":", update_url(seed), ""]
    lines += [DIRECT_LEAD, direct_url(), ""]
    lines += wrap(CLOSING, PLAIN_WIDTH) + [""]
    lines += SIGNATURE
    lines += [""]
    # A signature separator, not a MIME delimiter: a delimiter is "--" followed
    # by the boundary, and this line is the two characters on their own.
    lines += ["--", POSTAL]
    lines += wrap(PERMISSION, PLAIN_WIDTH)
    lines += [UNSUB_TEXT + ":", unsub_url(seed)]
    return lines


def html_part(seed):
    """The HTML source lines, before quoted-printable encoding.

    The footer permission sentence folds at 72 here, not 76, so the plain part
    and the footer break in the same places and the two parts stay comparable
    line by line where a reader would compare them.
    """
    permission = wrap(PERMISSION, PLAIN_WIDTH)
    permission[-1] = permission[-1] + "<br>"

    lines = ["<html>", BODY_OPEN, BANNER_HTML]
    lines += DIV_OPEN
    lines += [
        SMALL_STYLE + VIEW_PROMPT,
        '<a href="' + view_url(seed) + '"',
        SMALL_LINK_STYLE + VIEW_TEXT + "</a>.</p>",
        H2_OPEN,
        SUBJECT + "</h2>",
        "<p>" + SALUTATION + "</p>",
    ]
    lines += wrap("<p>" + INTRO + "</p>", HTML_WIDTH)
    for heading, text in ITEMS:
        lines += [ITEM_HEAD_OPEN + heading + "</p>"]
        lines += wrap(ITEM_BODY_OPEN + text + "</p>", HTML_WIDTH)
    lines += ['<p style="margin:22px 0;"><a href="' + update_url(seed) + '"']
    lines += BUTTON_STYLE
    lines += ["<p>" + DIRECT_LEAD + "<br>",
              '<a href="' + direct_url() + '">' + direct_url() + "</a></p>"]
    lines += wrap("<p>" + CLOSING + "</p>", HTML_WIDTH)
    lines += ["<p>" + "<br>".join(SIGNATURE) + "</p>", SMALL_STYLE, POSTAL + "<br>"]
    lines += permission
    lines += ['<a href="' + unsub_url(seed) + '"',
              SMALL_LINK_STYLE + UNSUB_TEXT + "</a></p>"]
    lines += ["</div>", "</body>", "</html>"]
    return lines


# --------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: an encoded line may not exceed 76 characters including the
# trailing soft break, and a soft break may not split an =XX escape. A break
# point is either immediately before a space, so the space leads the next line
# and is never left trailing, or immediately after a double quote, which is
# where an HTML attribute ends and a long unbreakable value such as a URL
# begins. The rightmost break point at or before column 72 wins, which is what
# puts each tracking link alone on its own line under its href attribute.
SOFT_MAX = 76
BREAK_MAX = 72


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks."""
    text = line.replace("=", "=3D")
    out = []
    while len(text) > SOFT_MAX:
        cut = None
        for index in range(min(BREAK_MAX, len(text) - 1), 0, -1):
            if text[index] == " " or text[index - 1] == '"':
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


# ------------------------------------------------------------------ guards

# The two phrase lists validate_corpus.py skips, for the reasons its
# PHRASE_PASS_SKIP comment gives: content:non_english_body is a proportion
# judgment over Spanish stopwords that hide inside ordinary English words, and
# content:instruction_to_ai holds single words that honest mail also uses.
PHRASE_PASS_SKIP = ("content:non_english_body", "content:instruction_to_ai")


def check_no_content_phrases(text):
    """Fail if the body carries any phrase from a list the record does not claim.

    The record lists no content code, so every phrase list is forbidden except
    the two the validator skips. Reading the lists out of spec/enums.json rather
    than copying them here means an edit to the vocabulary reaches this guard.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    lowered = text.lower()
    for code in sorted(enums.get("content_phrases") or {}):
        if code in PHRASE_PASS_SKIP:
            continue
        for phrase in enums["content_phrases"][code]:
            if phrase.lower() in lowered:
                raise SystemExit("the body carries the " + code + " phrase "
                                 + repr(phrase) + ", which the record does not claim")


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_sb_" + hexid(seed, "boundary", 16)
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + APP_NODE + ">")
    gateway_id = hexid(seed, "gateway-id")
    mta_id = hexid(seed, "mta-id", 8)
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    envelope_sender = bounce_address(seed)

    lines = [
        "Return-Path: <" + envelope_sender + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; " + STORE_STAMP,
        # RFC 8601 sec. 4: the gateway writes Authentication-Results above its
        # own trace field. SPF passes on the provider's bounce domain, which
        # does not align; the signature carries the broker's own domain, which
        # does, so DMARC passes on DKIM and quotes the broker's policy.
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=" + BOUNCE_HOST + ";",
        "  dkim=pass header.d=" + BROKER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + BROKER_DOMAIN + ";",
        "  dmarc=pass header.from=" + BROKER_DOMAIN + " policy.dmarc=quarantine",
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + envelope_sender + " designates",
        "  " + MTA_IP + " as permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + MTA_IP + ";",
        '  envelope-from="' + envelope_sender + '";',
        "  helo=" + MTA_HOST + "; identity=mailfrom;",
        "  mechanism=ip4:198.51.100.0/24",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + MTA_HOST,
        "  (" + MTA_HOST + " [" + MTA_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + APP_NODE + " ([" + APP_NODE_IP + "])",
        "  by " + MTA_HOST + " with ESMTP id " + mta_id + ";",
        "  " + APP_NODE_STAMP,
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + BROKER_DOMAIN + "; s=" + DKIM_SELECTOR + "; t=" + str(dkim_time()) + ";",
        # RFC 8058 sec. 3.1: the one-click headers have to be inside the
        # signature, or a receiver cannot trust the POST target.
        "  h=from:to:subject:date:message-id:mime-version:content-type:",
        "   list-unsubscribe:list-unsubscribe-post:list-id;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), DKIM_FOLD):
        chunk = signature[index:index + DKIM_FOLD]
        lines.append(("  b=" if index == 0 else "     ") + chunk)
    lines += [
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        # The provider's app node stamps the Date in UTC, the same instant as
        # 08:05 local, which is what the Message-ID left side and the app node
        # Received line also carry.
        "Date: " + DATE_HEADER,
        "Message-ID: " + message_id,
        "List-Unsubscribe:",
        "  <" + unsub_url(seed) + ">,",
        "  <mailto:" + unsub_address(seed) + ">",
        "List-Unsubscribe-Post: List-Unsubscribe=One-Click",
        "List-Id: " + SENDER_DISPLAY + " Quarterly Update <" + BROKER_DOMAIN + ">",
        "Precedence: bulk",
        "Feedback-ID: " + ACCOUNT + ":q2-compliance:vetchmoor:sendbarrow",
        "X-Mailer: Sendbarrow Campaigns 3.8",
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain_part(seed)
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(seed))
    lines += ["--" + boundary + "--", ""]

    long_lines = 0
    for line in lines:
        if len(line) > 998:
            raise SystemExit("line over 998 characters: " + line)
        if len(line) > 78:
            long_lines += 1
        line.encode("ascii")
    if long_lines != LONG_LINE_COUNT:
        raise SystemExit("expected " + str(LONG_LINE_COUNT)
                         + " line(s) over 78 characters, found " + str(long_lines))

    # The plain part is 7bit, so every one of its lines has to fit on its own.
    for line in plain_part(seed):
        if len(line) > 78:
            raise SystemExit("7bit plain line over 78 characters: " + line)

    plain_text = "\n".join(plain_part(seed))
    html_text = "\n".join(html_part(seed))
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    for url in (view_url(seed), update_url(seed), direct_url(), unsub_url(seed)):
        if url not in plain_text:
            raise SystemExit("the plain part lost the link " + url)
        if 'href="' + url + '"' not in html_text:
            raise SystemExit("the HTML part lost the link " + url)
    # The manifest fixes the two link hosts and their order, and the record's
    # url_hosts field is read in first-appearance order, the plain part first.
    hosts = []
    for chunk in (plain_text + "\n" + html_text).split("https://")[1:]:
        host = chunk.split("/")[0]
        if host not in hosts:
            hosts.append(host)
    if hosts != [LINK_HOST, BROKER_DOMAIN]:
        raise SystemExit("link hosts are " + str(hosts) + " in the wrong order")
    check_no_content_phrases(plain_text + "\n" + html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

LURE_SUMMARY = (
    "The benefits broker's opted-in quarterly newsletter, sent through the "
    "bulk provider with a custom DKIM signature published under the broker's "
    "own domain, so the signature aligns and DMARC passes. Links mix the "
    "provider's tracking host with the broker's own allowlisted site, and "
    "nothing in the message asks the reader for anything."
)

BODY_BRIEF = (
    "A newsletter greeted to Tobias by first name, since he subscribed. Open "
    "with a view-in-browser line through "
    "https://links.sendbarrow-mail.example/v/3304/219/39bf8d1a3a1f59c6, then "
    "the subject as a heading, then one sentence saying three things changed "
    "in dependent verification this quarter and the full write-up is on the "
    "site. Three numbered items, one paragraph each: a court order or an "
    "adoption decree now stands in for a birth certificate when a member adds "
    "a stepchild or a foster child; a member who adds a dependent after a "
    "qualifying life event now has ninety days to send the paperwork, up from "
    "sixty, with the clock starting on the date of the event; and sample "
    "audits of covered dependents move from once every third year to once a "
    "year starting this fall, with Vetchmoor writing to the member and "
    "reporting the result in the quarterly file. One link labeled 'Read the "
    "full update' through "
    "https://links.sendbarrow-mail.example/c/3304/219/d4/39bf8d1a3a1f59c6 and "
    "a direct link to https://vetchmoorbenefits.example/compliance/q2-2026. "
    "Close by saying nothing here needs a reply and the wording goes into the "
    "2027 enrollment packet, sign with a named compliance director (Odile Thorsby), and end "
    "with a postal line, a permission line and a one-click unsubscribe. No "
    "sign-in, no deadline, no attachment, and no phrase from any content list "
    "in spec/enums.json, because the record claims no content code."
)

MANIFEST_NOTES = (
    "Exam-only, so it renders under builder/instructor/exam-emails/ and never "
    "under corpus/emails/. Bulk headers do not make spam; the recipient "
    "subscribed, so the category is legit_external. Stem: an aligned DKIM key "
    "through a bulk provider passes DMARC, and authentication says nothing "
    "about wantedness. Rendered: From is Vetchmoor Benefits over "
    "vetchmoorbenefits.example, the domain display_names.json gives that name, "
    "so no display-name indicator applies; Return-Path is "
    "bounce-3304-0219-39bf8d1a3a1f59c6@bounce.sendbarrow-mail.example, so "
    "spf=pass names the provider's bounce domain and does not align; the "
    "signature is d=vetchmoorbenefits.example s=sb1, a provider-hosted key "
    "published under the broker's name, so dkim=pass aligns and dmarc=pass "
    "carries policy.dmarc=quarantine, the policy domain_policy.json publishes "
    "for the broker; three tracking links on "
    "links.sendbarrow-mail.example and one direct link on "
    "vetchmoorbenefits.example, which url_allowlist.json has held since "
    "2021-11-02; List-Unsubscribe, List-Unsubscribe-Post, List-Id, "
    "Precedence: bulk and Feedback-ID present, with the RFC 8058 one-click "
    "pair inside the DKIM h= list; scan result clean and spam score 2.3. The "
    "body carries no phrase from any content list, which is what keeps "
    "header:list_headers_present decisive under the tier rule, since that "
    "rule counts list headers only on a message with no ask code. The tier "
    "rule counts two decisive benign facts, the allowlisted sender with "
    "dmarc=pass and the list headers with no ask, against no pressure fact, "
    "so the base tier is easy; there is no injection and body_only_read "
    "agrees with the verdict, so nothing is added. The provider account 3304 "
    "and the campaign are pinned by this record: 0219 in the bounce local "
    "part and 219 in the link paths, the same pair of forms 027 carries as "
    "0042 and 42."
)

# ------------------------------------------------------------- ground truth

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=" + BOUNCE_HOST + "; dkim=pass header.d="
    + BROKER_DOMAIN + " header.s=" + DKIM_SELECTOR + " header.i=@"
    + BROKER_DOMAIN + "; dmarc=pass header.from=" + BROKER_DOMAIN
    + " policy.dmarc=quarantine"
)

REFERENCE_SUMMARY = (
    "This is the quarterly newsletter you subscribed to from our benefits "
    "broker, sent through their mailing service. It is safe and needs nothing "
    "from you."
)

NOTES = (
    "The exam case where every authentication check passes on a message a "
    "third party sent, and the passes are not the reason it is safe. Key "
    "facts a correct extractor produces: from_domain vetchmoorbenefits.example, "
    "the benefits broker's own domain, with the display name Vetchmoor "
    "Benefits, which display_names.json puts on that domain, so "
    "display_name_mismatch is false; no Reply-To, so there is no Reply-To "
    "mismatch to find; Return-Path "
    "bounce-3304-0219-39bf8d1a3a1f59c6@bounce.sendbarrow-mail.example, a "
    "bounce address whose last part is the provider's opaque per-recipient "
    "token; spf=pass on bounce.sendbarrow-mail.example, which is the "
    "provider's domain and does not align with the From domain; dkim=pass "
    "with d=vetchmoorbenefits.example s=sb1, a key the provider hosts under the "
    "broker's own name, so the signing domain equals the From domain and the "
    "message is aligned on DKIM; dmarc=pass with policy.dmarc=quarantine, the "
    "policy domain_policy.json publishes for vetchmoorbenefits.example. That "
    "split is the whole point of the file: SPF passes for one organization and "
    "DKIM for another, and DMARC needs only one of them to align. Two link "
    "hosts: links.sendbarrow-mail.example carries the view-in-browser link, "
    "the 'Read the full update' link and the unsubscribe link, all three "
    "ending in the token 39bf8d1a3a1f59c6 that also ends the "
    "List-Unsubscribe URL and the unsubscribe mailto; "
    "vetchmoorbenefits.example carries the one direct link, "
    "https://vetchmoorbenefits.example/compliance/q2-2026. The link host is a "
    "tracking host by the rule in enums.json: its organizational domain equals "
    "the Return-Path domain sendbarrow-mail.example and differs from the From "
    "organizational domain, and domain_policy.json lists it under "
    "tracking_hosts. No attachment header; no In-Reply-To, so the message "
    "opens a thread. Received chain: app-node-03.sendbarrow-mail.example "
    "[192.0.2.140] handed the message to o17.mta.sendbarrow-mail.example at "
    "13:05:06 +0000, which handed off with ESMTPS and TLS1_3 to "
    "mx.pellgrave.example [10.20.4.10] at 08:05:11 -0500, delivered by LMTP to "
    "mailstore-01.pellgrave.example at 08:05:13 -0500; Date is 13:05:00 +0000, "
    "stamped by the app node in UTC, which is 08:05 local and the same instant "
    "the Message-ID left side carries. X-Sentrywick-External is yes, scan "
    "result clean, spam score 2.3, and the list headers are "
    "List-Unsubscribe, List-Unsubscribe-Post, List-Id, Precedence: bulk and "
    "Feedback-ID, with list-unsubscribe and list-unsubscribe-post inside the "
    "DKIM h= list as RFC 8058 sec. 3.1 requires. Body content: no content code "
    "at all. Nothing in the three items asks the reader to sign in, send a "
    "list, pay anything or move a date, and no phrase from any list in "
    "spec/enums.json content_phrases appears in either decoded part, which the "
    "generator proves before it writes the file. That absence is not "
    "decoration: the tier rule counts list headers as a decisive benign fact "
    "only when the message carries no ask code, so a single ask phrase would "
    "change the tier. Difficulty reason: two decisive benign facts, the "
    "allowlisted sender with dmarc=pass and the bulk list headers with no ask, "
    "against no pressure fact, so the base tier is easy; the spam score 2.3 is "
    "below the 5.0 threshold so it adds no third point; there is no injection, "
    "and body_only_read is benign, the same as the verdict, so neither "
    "adjustment applies. Week 8 use: check_sender_reputation returns trusted "
    "for vetchmoorbenefits.example, first seen 2021-11-02, 34 messages in 90 "
    "days and one prior report closed benign on 2026-02-11, and check_urls "
    "returns allowlisted for vetchmoorbenefits.example and unlisted for "
    "links.sendbarrow-mail.example, so the loop stops after two steps with "
    "stop_reason decisive_benign. lookup_recipient would add nothing to the "
    "verdict: it says Tobias Nkemelu is the Payroll and Benefits Coordinator, "
    "handles payments, five reports and three true positives in the window, "
    "which is context for how the reply is written and not evidence about the "
    "message. Playbook rules 1, 2 and 7 close it: the passes name a domain, "
    "the broker's name sits over the domain the broker owns, and the one link "
    "host that is not on the allowlist is the provider's tracking host, which "
    "rule 7 reads as unknown rather than clean and which no other fact turns "
    "into evidence. escalate_expected is false and the action is "
    "close_benign_reply_to_reporter: the newsletter asks for nothing, moves no "
    "money and names no deadline, so no callback rule fires even though the "
    "recipient handles payments. Full credit on the indicators criterion needs "
    "sender:allowlisted_domain and header:list_headers_present. Story context: "
    "this mailbox is the one 013 aimed a hyphen-insertion lookalike at eight "
    "days earlier, from enrollment@vetchmoor-benefits.example. The exam stem "
    "puts the two side by side and asks which facts separate them, and the "
    "answer is the From domain, the reputation record and the link hosts, not "
    "the authentication block, because both messages collect three passes. "
    "Grading note: a student who calls this spam because it carries "
    "Precedence: bulk has read the header and not the subscription, a student "
    "who calls it malicious because the tracking host is unlisted has skipped "
    "playbook rule 7, and a student who treats dmarc=pass as proof the mail "
    "was wanted has read authentication as a wantedness verdict. Rendering "
    "notes: the plain part is 7bit with hard wraps under 78 characters and the "
    "HTML part is quoted-printable, because the fixed gateway banner snippet "
    "is longer than 78 characters; the banner is the first line of the plain "
    "part and the first line after the body tag in the HTML part; both parts "
    "carry the same words in the same order and the HTML part hides nothing, "
    "so there is no content:html_hidden_text. The MIME boundary prefix is "
    "=_sb_, the prefix the two other Sendbarrow mailings carry, because the "
    "prefix belongs to the platform that composed the message. Two header "
    "lines, the Return-Path and the Received-SPF envelope-from, run past 78 "
    "characters because the 64 character bounce address is one unfoldable "
    "token; the validator reports that as a fold-length warning and not a "
    "failure. There is no X-Originating-IP: the sender is a campaign platform "
    "rather than a webmail provider, so the app node address 192.0.2.140 "
    "appears in the bottom Received line instead. Every identifier that looks "
    "random is derived from a SHA-256 over the corpus seed, the email id and a "
    "label, so the file regenerates byte for byte."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/exam/" + EMAIL_ID + ".eml",
    "set": "exam",
    "weeks": [8],
    "date": "2026-04-28T08:05:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "easy",
    "body_only_read": "benign",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "bulk_provider",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass",
             "dmarc_policy": "quarantine"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": AUTH_VALUE},
        {"code": "sender:allowlisted_domain", "where": "check_sender_reputation",
         "value": BROKER_DOMAIN},
        {"code": "header:list_headers_present",
         "where": "List-Unsubscribe, List-Id, Precedence",
         "value": "List-Unsubscribe, List-Unsubscribe-Post, List-Id, Precedence"},
        {"code": "header:precedence_bulk", "where": "Precedence", "value": "bulk"},
        {"code": "header:spam_score", "where": "X-Sentrywick-Spam-Score",
         "value": SPAM_SCORE},
        {"code": "url:tracking_host", "where": "body", "value": LINK_HOST},
        {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
        {"code": "url:host_allowlisted", "where": "check_urls",
         "value": BROKER_DOMAIN},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": RECIPIENT},
    ],
    "required_indicators": ["sender:allowlisted_domain",
                            "header:list_headers_present"],
    "url_hosts": [LINK_HOST, BROKER_DOMAIN],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": BROKER_DOMAIN,
            "status": "trusted",
            "first_seen": "2021-11-02",
            "messages_90d": 34,
            "prior_reports": 1,
            "last_report_verdict": "benign",
            "last_report_date": "2026-02-11",
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Benefits broker; allowlisted.",
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "unlisted", BROKER_DOMAIN: "allowlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
            "role": "Payroll and Benefits Coordinator",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": True,
            "chronic_reporter": False,
            "report_count_90d": 5,
            "true_positive_count_90d": 3,
            "campaign_tags": ["benefits-notice", "credential-phish",
                              "direct-deposit-change", "payroll-notice"],
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
                         ("weeks", GROUND_TRUTH["weeks"]),
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
                         ("escalate_expected", GROUND_TRUTH["escalate_expected"]),
                         ("escalation_reasons", GROUND_TRUTH["escalation_reasons"]),
                         ("required_indicators", GROUND_TRUTH["required_indicators"]),
                         ("reference_summary", REFERENCE_SUMMARY)):
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
    for name, text in (("lure_summary", LURE_SUMMARY),
                       ("reference_summary", REFERENCE_SUMMARY)):
        if not two_sentences(text):
            raise SystemExit(name + " must be exactly two sentences")

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
