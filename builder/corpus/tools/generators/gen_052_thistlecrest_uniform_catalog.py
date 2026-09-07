#!/usr/bin/env python3
"""Regenerate 052-thistlecrest-uniform-catalog.

Renders builder/instructor/exam-emails/052-thistlecrest-uniform-catalog.eml
byte for byte from the corpus seed, refreshes the prose fields of its own
record in spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. Every semantic field in the manifest record, the sender,
the recipient, the date, the authentication results, the received path, the
indicators, the link host, the tool expectations and the expected loop, is
read and never written, so the label and the file cannot drift.

This is an exam-only email. It ships in the instructor package and never under
corpus/emails/, so nothing a student can reach holds it before the week 8
exam. tools/validate_corpus.py warns that an exam record has no file under
emails/ and that the ground truth file field does not match the path on disk;
both warnings are correct for an exam file and tools/build_corpus.py checks
this one with

    validate_corpus.py --no-dns --emails builder/instructor/exam-emails
                       --ground-truth builder/corpus/release/ground_truth_exam.json

The ground truth file field still reads emails/exam/<id>.eml because
spec/ground_truth.schema.json pins that shape for all three sets; the instructor
package is where the bytes actually live.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n)       = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, count)  = sha256("<seed>|<id>|<label>|<n>") for n = 0, 1, 2 ...
    recipient token       = hexid("recipient-token", 16)
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_sb_" + hexid("boundary", 16)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    provider Received id  = hexid("mta-id", 8)
    DKIM bh               = base64(stream("dkim-bh", 32))
    DKIM b                = base64(stream("dkim-b", 256))
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

Nothing here calls time, random or uuid4(). The store LMTP id derives cleanly
from the seed on this record, unlike 003 and 019, so no literal is pinned.

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab checks a signature. The DKIM t= value is the Unix time
of the Date header, 1777373100 for Tue, 28 Apr 2026 10:45:00 +0000, so the
signature timestamp and the stamped time are the same instant.

The account number 7710, the campaign number 2205 and the catalog link's
variant segment c3 are design constants: spec/corpus-spec.json pins them in
this record's received_path_hint and body_brief, so they are read as literals
from the design rather than derived. The per-recipient token is the one part of
those identifiers that is opaque, and it does come out of the seed. It ends the
bounce address, all three tracking links, the List-Unsubscribe URL and the
unsubscribe mailto, which is what makes the footer's one-click unsubscribe, a
bounce and a click all identify the same subscriber (RFC 8058 sec. 3.1).

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. The To address, the reporter and the
mailbox the file was pulled from are all Casimir Hallowden, so there is no list
expansion to unwind: recipients.json gives him mailstore-01 and the LMTP hop
names it. He is also the corpus chronic reporter, eleven reports in the window
and no true positive among them, which is the point of giving him this email.

Why the authentication headers read the way they do, and what the exam asks.
The message crosses the border gateway, so it carries Authentication-Results,
Received-SPF and X-Sentrywick-External: yes, and both body parts open with the
gateway banner. The bulk provider bounces and signs under its own domain, so
SPF passes on bounce.sendbarrow-mail.example. The signature is present and the
gateway parsed it, which is why header.d and header.s are reported, but the
lookup of s2026a._domainkey.sendbarrow-mail.example timed out, so the result is
dkim=temperror (RFC 8601 sec. 2.7.1). A temporary error is not a failed check:
it says the verifier could not reach an answer, not that the answer was no.
That is the question this exam email asks, and it is the one place in the
corpus where a student can confuse the two. This file and 038 are the only two
messages allowed to carry temperror or permerror at all; validate_corpus.py
fails the corpus at three.

Neither the SPF identity nor the signing domain aligns with the From
organizational domain thistlecrest-uniforms.example, and that domain publishes
no DMARC record, so the result is dmarc=none with no policy value and
dmarc_policy is null. A missing record is not a failed check either.

The DKIM-Signature header stays even though the verdict is temperror: the
signature is what the sender attached, and RFC 8058 sec. 3.1 requires it to
cover List-Unsubscribe and List-Unsubscribe-Post before a one-click POST means
anything, so h= names both. validate_corpus.py enforces that pair whenever
List-Unsubscribe-Post is present, and removing the signature to match the
temperror would break it.

Two lines run past the 78 character fold width that section 10.1 of the design
recommends: the Return-Path, at 79, and the Received-SPF envelope-from, at 83.
Both are one unfoldable address token, the 64 character bounce address, inside
a header that has nowhere left to fold. RFC 5322 sec. 2.1.1 allows up to 998,
section 7 of docs/email-header-realism.md says these two lines may run long for
exactly this reason, so validate_corpus.py reports them as a fold-length
warning and not a failure; build_eml raises if the count ever changes.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
no In-Reply-To and no References (thread:new), no X-Sentrywick-Removed-Attachment
(attachment:none), no X-Priority and no Importance, and no X-Originating-IP,
which is reserved for webmail submissions. Auto-Submitted is absent as well: a
campaign platform sending a commercial mailing marks itself with Precedence:
bulk and the RFC 8058 list headers, not with the RFC 3834 field for
system-generated replies. Thread-Topic is absent because it belongs to the
organization's own submission host and this message arrived through the
gateway.

Run:  python3 corpus/tools/generators/gen_052_thistlecrest_uniform_catalog.py
"""

import base64
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "052-thistlecrest-uniform-catalog"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
# Exam-only: the bytes live in the instructor package, never under emails/.
EML_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EML_DIR, EMAIL_ID + ".eml")
# What the ground truth file field carries. spec/ground_truth.schema.json pins
# the shape emails/<set>/<id>.eml for every set, exam included.
GT_FILE = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "hello@promo.thistlecrest-uniforms.example"
SENDER_DISPLAY = "Thistlecrest Uniforms"
FROM_HOST = "promo.thistlecrest-uniforms.example"
ORG_DOMAIN = "thistlecrest-uniforms.example"
RECIPIENT = "c.hallowden@pellgrave.example"
REPORTER = "c.hallowden@pellgrave.example"

SUBJECT = "New summer uniform catalog for warehouse teams"

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
DKIM_SELECTOR = "s2026a"
# Unix time of the Date header, Tue, 28 Apr 2026 10:45:00 +0000.
DKIM_TIME = "1777373100"

GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SPAM_SCORE = "4.8"

# Design constants, pinned by this record's received_path_hint and body_brief in
# spec/corpus-spec.json: the provider account, the campaign, and the variant
# segment on the catalog link. They are numbers a platform assigns, not opaque
# per-recipient material, so they are read from the design and not derived.
ACCOUNT = "7710"
CAMPAIGN = "2205"
CATALOG_VARIANT = "c3"

# The two header lines that run past the 78 character fold width, both because
# the 64 character bounce address is a single unfoldable token. See the module
# docstring; build_eml raises if the count changes.
LONG_LINE_COUNT = 2


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
# record carries no content code, so no phrase from any content list may appear
# in either decoded part; validate_corpus.py checks that both ways and
# check_no_content_phrases() below fails the render first.
#
#   Nothing in the message is dated, counted down or capped, so no phrase from
#   content:urgency_keywords appears: no "today", no "last chance", no
#   "expires in", no "by end of day". The offer is open and the mailing says so.
#   "sign in", "log in" and "password" are out (content:credential_request):
#   there is no account, no portal and no order status page to visit. The word
#   "catalog" is never followed by "in", because "catalog in" carries "log in"
#   inside it and the phrase check reads the body as one lowercased string.
#   "invoice", "remit", "amount due" and "net 30" are out
#   (content:payment_request): this is a catalog, not a bill, and the one price
#   in it is the free-logo threshold.
#   "download", "shared with you" and "secure share" are out
#   (content:file_share_lure), so the catalog is browsed rather than fetched.
#   "send me the names" and the rest of content:data_request are out: the
#   mailing asks for nothing at all, which is what keeps the category spam and
#   the verdict benign under the spam rule in spec/categories.json.
#
# The words are written once and shared by both parts, so a part-to-part diff
# is empty. The two parts differ only in where the lines break, because the
# plain part folds at 72 and the HTML source folds at 76.
PLAIN_WIDTH = 72
HTML_WIDTH = 76

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

VIEW_PROMPT = "Having trouble reading this?"
VIEW_TEXT = "View it in your browser"
SALUTATION = "Hello from Thistlecrest Uniforms,"
OFFER = ("Our summer catalog is out, and this one leans on the crews who spend "
         "the whole shift on a concrete floor. The work shirts are cut from a "
         "lighter poplin this year, and the hi-vis vests hold their color "
         "through a season of industrial laundering.")
BULLET_LEAD = "New this season:"
BULLETS = [
    "Short and long sleeve work shirts in a lighter summer poplin",
    "Class 2 hi-vis vests with a mesh back panel and two radio loops",
    "Cotton twill work pants cut for a boot, in three inseams",
]
# The one number in the message. A threshold on an open offer, with no date on
# it, so it reads as a standing term rather than as pressure.
SETUP = ("Logo setup is free on any order over $500, so a company crest on the "
         "left chest costs nothing extra. Sizes run small through 5XL in every "
         "line, and we will send a fit sample in any size if a crew wants to "
         "try one on before ordering.")
SHOP_TEXT = "See the catalog"
CLOSING = ("Thanks for taking a look. We are glad to price out a whole crew if "
           "that is easier than working down the list line by line.")
# A named signer with a role, the way a small supplier's catalog mailing is
# signed. No phone number and no extension: the corpus reserves the 555-01xx
# block for senders whose authored action is an out-of-band callback, and this
# one closes as spam with nothing to verify.
SIGNOFF = [
    "Odalys Wrenfield",
    "Customer Accounts, Thistlecrest Uniforms",
]
# The postal line stops at a box number: the corpus names no city, state or
# postal code anywhere.
POSTAL = "Thistlecrest Uniforms, PO Box 1188"
PERMISSION = ("You are receiving this message because your company is on the "
              "Thistlecrest Uniforms catalog mailing list.")
UNSUB_TEXT = "Unsubscribe"

BODY_OPEN = '<body style="margin:0;padding:0;background:#f4f4f4;">'
DIV_OPEN = [
    '<div style="max-width:600px;margin:0 auto;padding:24px;background:#ffffff;',
    "font-family:sans-serif;font-size:15px;line-height:1.5;color:#222222;\">",
]
SMALL_STYLE = '<p style="font-size:12px;color:#777777;">'
SMALL_LINK_STYLE = 'style="color:#777777;">'
H2_OPEN = '<h2 style="font-size:20px;color:#23406b;">'
BUTTON_STYLE = [
    'style="background:#23406b;color:#ffffff;padding:10px 18px;',
    'text-decoration:none;">' + SHOP_TEXT + "</a></p>",
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
    return "https://" + LINK_HOST + "/v/" + ACCOUNT + "/" + CAMPAIGN + "/" + token(seed)


def catalog_url(seed):
    return ("https://" + LINK_HOST + "/c/" + ACCOUNT + "/" + CAMPAIGN + "/"
            + CATALOG_VARIANT + "/" + token(seed))


def unsub_url(seed):
    return "https://" + LINK_HOST + "/u/" + ACCOUNT + "/" + CAMPAIGN + "/" + token(seed)


def bounce_address(seed):
    return "bounce-" + ACCOUNT + "-" + CAMPAIGN + "-" + token(seed) + "@" + BOUNCE_HOST


def unsub_address(seed):
    return "unsub-" + ACCOUNT + "-" + CAMPAIGN + "-" + token(seed) + "@" + BOUNCE_HOST


def plain_part(seed):
    lines = [BANNER_PLAIN, ""]
    lines += [VIEW_PROMPT + " " + VIEW_TEXT + ":", view_url(seed), ""]
    lines += [SUBJECT, ""]
    lines += [SALUTATION, ""]
    lines += wrap(OFFER, PLAIN_WIDTH) + [""]
    lines += [BULLET_LEAD, ""]
    lines += ["  * " + item for item in BULLETS]
    lines += [""]
    lines += wrap(SETUP, PLAIN_WIDTH) + [""]
    lines += [SHOP_TEXT + ":", catalog_url(seed), ""]
    lines += wrap(CLOSING, PLAIN_WIDTH) + [""]
    lines += SIGNOFF + [""]
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
    lines += wrap("<p>" + OFFER + "</p>", HTML_WIDTH)
    lines += ["<p>" + BULLET_LEAD + "</p>", "<ul>"]
    lines += ["<li>" + item + "</li>" for item in BULLETS]
    lines += ["</ul>"]
    lines += wrap("<p>" + SETUP + "</p>", HTML_WIDTH)
    lines += ['<p><a href="' + catalog_url(seed) + '"']
    lines += BUTTON_STYLE
    lines += wrap("<p>" + CLOSING + "</p>", HTML_WIDTH)
    lines += ["<p>" + "<br>".join(SIGNOFF) + "</p>", SMALL_STYLE, POSTAL + "<br>"]
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


def check_no_content_phrases(seed):
    """No content: phrase may appear, because the record lists no content code.

    validate_corpus.py runs this pass both ways on the rendered file. Running it
    here as well means a wording change that drifts into a phrase list fails at
    the render rather than at the corpus check, with the phrase named.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    where_of = {entry["code"]: entry.get("where")
                for entry in enums.get("indicator_vocabulary", [])}
    # The two lists the validator skips: content:non_english_body is Spanish
    # stopwords that sit inside ordinary English words, and content:instruction_to_ai
    # is single words the corpus also quotes on benign mail.
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = ("\n".join(plain_part(seed)) + "\n" + "\n".join(html_part(seed))).lower()
    for code, items in sorted(enums.get("content_phrases", {}).items()):
        if code in skip or where_of.get(code) != "body":
            continue
        for phrase in items:
            if phrase.lower() in body:
                raise SystemExit("the body carries the " + code + " phrase "
                                 + repr(phrase) + " but the record lists no content code")


def build_eml(seed):
    boundary = "=_sb_" + hexid(seed, "boundary", 16)
    message_id = ("<20260428104500." + hexid(seed, "message-id")
                  + "@" + APP_NODE + ">")
    gateway_id = hexid(seed, "gateway-id")
    mta_id = hexid(seed, "mta-id", 8)
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    envelope_sender = bounce_address(seed)

    check_no_content_phrases(seed)

    lines = [
        "Return-Path: <" + envelope_sender + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; Tue, 28 Apr 2026 05:45:13 -0500",
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=" + BOUNCE_HOST + ";",
        # The signature parsed, so header.d and header.s are reported; only the
        # key lookup timed out. RFC 8601 sec. 2.7.1.
        "  dkim=temperror header.d=" + PROVIDER + " header.s=" + DKIM_SELECTOR + ";",
        "  dmarc=none header.from=" + FROM_HOST,
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + envelope_sender + " designates",
        "  " + MTA_IP + " as permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + MTA_IP + ";",
        '  envelope-from="' + envelope_sender + '";',
        "  helo=" + MTA_HOST + "; identity=mailfrom;",
        "  mechanism=ip4:198.51.100.0/24",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + MTA_HOST,
        "  (" + MTA_HOST + " [" + MTA_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Tue, 28 Apr 2026 05:45:11 -0500",
        "Received: from " + APP_NODE + " ([" + APP_NODE_IP + "])",
        "  by " + MTA_HOST + " with ESMTP id " + mta_id + ";",
        "  Tue, 28 Apr 2026 10:45:06 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + PROVIDER + "; s=" + DKIM_SELECTOR + "; t=" + DKIM_TIME + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type:",
        "   list-unsubscribe:list-unsubscribe-post:list-id;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), 70):
        chunk = signature[index:index + 70]
        lines.append(("  b=" if index == 0 else "     ") + chunk)
    lines += [
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT,
        "Subject: " + SUBJECT,
        # The provider's app node stamps the Date in UTC, the same instant as
        # 05:45 local, which is what the Message-ID left side and the app node
        # Received line also carry.
        "Date: Tue, 28 Apr 2026 10:45:00 +0000",
        "Message-ID: " + message_id,
        "List-Unsubscribe:",
        "  <" + unsub_url(seed) + ">,",
        "  <mailto:" + unsub_address(seed) + ">",
        "List-Unsubscribe-Post: List-Unsubscribe=One-Click",
        "List-Id: " + SENDER_DISPLAY + " Catalog <" + FROM_HOST + ">",
        "Precedence: bulk",
        "Feedback-ID: " + ACCOUNT + ":summer-catalog:thistlecrest:sendbarrow",
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
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A short catalog mailing through the bulk provider. It opens with the "
    "view-in-browser line the provider puts on every campaign, then says the "
    "summer catalog is out: lighter poplin work shirts, Class 2 hi-vis vests "
    "with a mesh back and radio loops, and cotton twill work pants in three "
    "inseams. Free logo setup on any order over $500, sizes small through "
    "5XL, and a fit sample offered to any crew that wants to try one on. One "
    "'See the catalog' link to "
    "https://links.sendbarrow-mail.example/c/7710/2205/c3/c23372ccc3cd8de7, "
    "signed by a named person in Customer Accounts, then a footer with a "
    "postal box line, the permission sentence and an unsubscribe link. No "
    "sign-in, no deadline, no attachment, and nothing asked for beyond the "
    "click. The tone is cheerful and generic, and 'catalog' appears in the "
    "first line of the message."
)

LURE_SUMMARY = (
    "A uniform supplier's catalog mailing through the bulk provider, with list "
    "headers, an unsubscribe link, and a temporary DNS error on the signature "
    "check. Nothing is asked for beyond a click on a tracking link."
)

MANIFEST_NOTES = (
    "Exam-only. One of at most two temperror messages in the corpus: the stem "
    "asks whether a temporary DNS error is a failure (it is not). Marketing "
    "pattern from the header specification with the signature check replaced "
    "by temperror. Rendering: the DKIM-Signature header stays, because the "
    "signature is what the sender attached and only the key lookup failed, and "
    "because RFC 8058 section 3.1 requires it to cover List-Unsubscribe and "
    "List-Unsubscribe-Post before the one-click POST means anything; the "
    "gateway therefore reports header.d and header.s alongside the temperror. "
    "The body carries no phrase from any content list in spec/enums.json, so "
    "the mailing asks for nothing and the spam rule in spec/categories.json "
    "holds the verdict at benign. The Return-Path and the Received-SPF "
    "envelope-from run to 79 and 83 characters because the 64 character bounce "
    "address cannot fold; section 7 of docs/email-header-realism.md allows "
    "both and the validator reports a fold-length warning."
)

# ------------------------------------------------------------- ground truth

NOTES = (
    "Spam through the bulk provider, verdict benign, tier easy, exam only. "
    "Extracted facts: From domain promo.thistlecrest-uniforms.example (display "
    "name Thistlecrest Uniforms, which display_names.json gives to "
    "thistlecrest-uniforms.example, and the From host ends in that domain, so "
    "there is no display-name mismatch); no Reply-To; Return-Path "
    "bounce-7710-2205-c23372ccc3cd8de7@bounce.sendbarrow-mail.example, a "
    "bounce address whose last part is the provider's opaque per-recipient "
    "token; spf=pass on bounce.sendbarrow-mail.example; dkim=temperror with "
    "header.d=sendbarrow-mail.example and header.s=s2026a, which means the "
    "gateway parsed the signature and then could not reach the DNS key, not "
    "that the signature was wrong; dmarc=none because neither identity aligns "
    "with thistlecrest-uniforms.example and that domain publishes no DMARC "
    "record, so no policy value appears and dmarc_policy is null; Date stamped "
    "Tue, 28 Apr 2026 10:45:00 +0000 by the provider's app node, the same "
    "instant as 05:45 local, matching its Received line and its Message-ID; "
    "one link host, links.sendbarrow-mail.example, carrying three links (view "
    "in browser, catalog, unsubscribe) that all end in the same token "
    "c23372ccc3cd8de7, which also ends the List-Unsubscribe URL and the "
    "unsubscribe mailto; no attachment; X-Sentrywick-Spam-Score 4.8 with scan "
    "result clean; List-Unsubscribe, List-Unsubscribe-Post, List-Id, "
    "Precedence: bulk and Feedback-ID present; the HTML part is a full "
    "document whose first paragraph is the gateway banner. The link host is a "
    "tracking host by the rule in enums.json: its organizational domain equals "
    "the Return-Path domain sendbarrow-mail.example and differs from the From "
    "domain, and domain_policy.json lists it under tracking_hosts. Difficulty "
    "reason: one decisive benign fact (bulk list headers with no ask, since "
    "the body contains no phrase from any content list) and nothing pushing "
    "the other way; the spam score is below the 5.0 threshold so it adds no "
    "second point; no injection; body-only read agrees with the verdict. "
    "Expected action from playbook rule 10: unwanted marketing that asks for "
    "nothing is spam, close it and block nothing, reply to the reporter. Week "
    "8 use: the spam category with the benign verdict, and the one question "
    "this file exists to ask, whether dkim=temperror is a failed check. It is "
    "not. A temporary error says the verifier could not reach an answer; a "
    "fail says it reached one and the answer was no. The corpus allows "
    "temperror and permerror in at most two messages each, and this file and "
    "038 are the two. check_sender_reputation matches "
    "thistlecrest-uniforms.example at the organizational-domain level even "
    "though the From host is promo.thistlecrest-uniforms.example, and returns "
    "unknown with first_seen 2026-04-28, one message in 90 days and no prior "
    "report, so sender:first_seen is present and sender:known_good is not; "
    "check_urls returns unlisted for the tracking host, which playbook rule 7 "
    "reads as unknown, not clean; lookup_recipient shows the chronic reporter "
    "(11 reports, 0 true positives). Grading note: a student who calls "
    "dkim=temperror a failure has confused a transient DNS error with a bad "
    "signature, a student who calls dmarc=none a failure has confused a "
    "missing record with a failed check, a student who calls the unlisted "
    "tracking host malicious has skipped rule 7, and a student who reads the "
    "+0000 Date as an off-hours send has not converted it to local time. The "
    "footer's postal line stops at a box number because the corpus names no "
    "city, state or postal code anywhere. Rendering note: two header lines, "
    "the Return-Path and the Received-SPF envelope-from, run past 78 "
    "characters because the 64 character bounce address is one unfoldable "
    "token, which the validator reports as a fold-length warning and not a "
    "failure."
)

REFERENCE_SUMMARY = (
    "This is a catalog mailing from a uniform company, sent through a "
    "bulk-mail service. It is unwanted but harmless, so it was closed as spam."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": GT_FILE,
    "set": "exam",
    "weeks": [8],
    "date": "2026-04-28T05:45:00-05:00",
    "verdict": "benign",
    "category": "spam",
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
    "auth": {"spf": "pass", "dkim": "temperror", "dmarc": "none", "dmarc_policy": None},
    "indicators": [
        {"code": "auth:spf_pass", "where": "Authentication-Results",
         "value": "spf=pass smtp.mailfrom=" + BOUNCE_HOST},
        {"code": "auth:dkim_temperror", "where": "Authentication-Results",
         "value": ("dkim=temperror header.d=" + PROVIDER
                   + " header.s=" + DKIM_SELECTOR)},
        {"code": "auth:dmarc_none", "where": "Authentication-Results",
         "value": "dmarc=none header.from=" + FROM_HOST},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-28"},
        {"code": "header:list_headers_present",
         "where": "List-Unsubscribe, List-Id, Precedence",
         "value": "List-Unsubscribe, List-Unsubscribe-Post, List-Id, Precedence"},
        {"code": "header:precedence_bulk", "where": "Precedence", "value": "bulk"},
        {"code": "header:spam_score", "where": "X-Sentrywick-Spam-Score",
         "value": SPAM_SCORE},
        {"code": "url:tracking_host", "where": "body", "value": LINK_HOST},
        {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:chronic_reporter", "where": "lookup_recipient",
         "value": "11 reports in 90 days, 0 true positives"},
    ],
    "required_indicators": ["header:list_headers_present", "auth:dkim_temperror"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": ORG_DOMAIN,
            "status": "unknown",
            "first_seen": "2026-04-28",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "Bulk marketer; first seen inside the window.",
            "match_level": "organizational_domain",
        },
        "check_urls": {LINK_HOST: "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Casimir Hallowden",
            "role": "Warehouse Supervisor",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": True,
            "report_count_90d": 11,
            "true_positive_count_90d": 0,
            "campaign_tags": ["internal-notice", "marketing", "vendor-notice"],
        },
    },
    "expected_loop": {
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_spam_reply_to_reporter",
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

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_address"] != SENDER:
        raise SystemExit("sender does not match the manifest")

    data = build_eml(seed)
    os.makedirs(EML_DIR, exist_ok=True)
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

    # Prose fields only. Every semantic field in the record is the design's.
    record["body_brief"] = BODY_BRIEF
    record["lure_summary"] = LURE_SUMMARY
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
