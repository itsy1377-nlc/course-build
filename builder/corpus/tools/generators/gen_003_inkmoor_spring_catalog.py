#!/usr/bin/env python3
"""Regenerate 003-inkmoor-spring-catalog.

Rebuilds emails/teaching/003-inkmoor-spring-catalog.eml byte for byte from the
corpus seed and upserts the ground truth record in ground_truth.json. The
manifest record in spec/corpus-spec.json is already complete for this email and
is read, never written, so the label and the file cannot drift.

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

Every one of those reproduces the committed file exactly except the last. The
store LMTP id is pinned as a literal below rather than derived. The seed
derivation yields

    69a976a6-8487-4851-8780-6ba71ebc47fc

and the committed file carries

    69a976a6-8487-4851-9780-6ba71ebc47fc

which is the same value in all 31 other hex digits and differs only in the
RFC 4122 variant nibble, 8 against 9. That nibble is not free: sha256 puts a 4
at that position, and uuid.UUID(..., version=4) clears the top two bits and
sets them to 10, which can only produce 8 from a 4. A 9 there would need a
1, 5, 9 or d out of the hash. No label, and no other input to the same
construction, can produce a 9 while leaving the other 31 digits alone, so the
committed value is a hand edit that cannot be derived from the seed. The task
here is to make the file regenerable without changing it, so the literal is
pinned and the derived value is computed alongside it and compared, purely so
that a later change to the seed or to the derivation shows up as a loud
mismatch instead of silently rewriting the file. 019 carries the same
one-nibble divergence; the other teaching files derive cleanly.

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab checks a signature. The DKIM t= value is the Unix
time of the Date header, 1776078120 for Mon, 13 Apr 2026 11:02:00 +0000, so
the signature timestamp and the stamped time are the same instant.

The account number 2231, the campaign number 9074 and the catalog link's
variant segment a1 are design constants: spec/corpus-spec.json pins them in
this record's received_path_hint and body_brief, so they are read as literals
from the design rather than derived. The per-recipient token is the one part
of those identifiers that is opaque, and it does come out of the seed. It ends
the bounce address, all three tracking links, the List-Unsubscribe URL and the
unsubscribe mailto, which is what makes the footer's one-click unsubscribe and
the envelope sender read as the same mailing to the same subscriber.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. Here the To address, the reporter and
the mailbox the file was pulled from are all Casimir Hallowden, so there is no
list expansion to unwind: recipients.json gives him mailstore-01 and the LMTP
hop names it.

Why the authentication headers read the way they do. The message crosses the
border gateway, so it carries Authentication-Results, Received-SPF and
X-Sentrywick-External: yes, and both body parts open with the gateway banner.
The bulk provider signs and bounces under its own domain, so SPF passes on
bounce.sendbarrow-mail.example and DKIM passes with d=sendbarrow-mail.example.
Neither identity aligns with the From domain's organizational domain,
inkmoor-office.example, and that domain publishes no DMARC record, so the
result is dmarc=none with no policy value, which is why dmarc_policy is null in
the record. A missing record is not a failed check, and that is the single most
common wrong reading of this file.

Two lines run past the 78 character fold width that section 10.1 of the design
recommends: the Return-Path, at 79, and the Received-SPF envelope-from, at 83.
Both are one unfoldable address token, the 61 character bounce address, inside
a header that has nowhere left to fold. RFC 5322 sec. 2.1.1 allows up to 998,
so validate_corpus.py reports them as a fold-length warning and not a failure,
and the guard in build_eml checks the 998 hard limit and counts those two.
The committed ground truth record puts that rendering note on the HTML part
instead of on these two header lines; the record is reproduced here exactly as
committed rather than edited, since the corpus labels are approved.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
no In-Reply-To and no References (thread:new), no X-Sentrywick-Removed-Attachment
(attachment:none), no X-Priority and no Importance, and no X-Originating-IP,
which is reserved for webmail submissions. Auto-Submitted is absent as well: a
campaign platform sending an opt-in commercial mailing marks itself with
Precedence: bulk and the RFC 8058 list headers, not with the RFC 3834 field for
system-generated replies.

Run:  python3 corpus/tools/generators/gen_003_inkmoor_spring_catalog.py
"""

import base64
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "003-inkmoor-spring-catalog"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "offers@news.inkmoor-office.example"
SENDER_DISPLAY = "Inkmoor Office Supply"
FROM_HOST = "news.inkmoor-office.example"
ORG_DOMAIN = "inkmoor-office.example"
RECIPIENT = "c.hallowden@pellgrave.example"
REPORTER = "c.hallowden@pellgrave.example"

SUBJECT = "Spring catalog: 20% off breakroom and shipping supplies through 4/30"

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
# Unix time of the Date header, Mon, 13 Apr 2026 11:02:00 +0000.
DKIM_TIME = "1776078120"

GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# Design constants, pinned by this record's received_path_hint and body_brief in
# spec/corpus-spec.json: the provider account, the campaign, and the variant
# segment on the catalog link. They are numbers a platform assigns, not opaque
# per-recipient material, so they are read from the design and not derived.
ACCOUNT = "2231"
CAMPAIGN = "9074"
CATALOG_VARIANT = "a1"

# The store LMTP id in the committed file. See the module docstring: the seed
# derivation produces the same value with an 8 in the RFC 4122 variant nibble
# and the file carries a 9, which no derivation over this seed can produce, so
# the literal is pinned here rather than the file being changed to match.
# check_store_id() below compares the two and reports the divergence.
STORE_LMTP_ID = "69a976a6-8487-4851-9780-6ba71ebc47fc"

# The two header lines that run past the 78 character fold width, both because
# the 61 character bounce address is a single unfoldable token. See the module
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


def derived_store_id(seed):
    """What the house derivation gives for the LMTP id. Not what the file has."""
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def check_store_id(seed):
    """Pin the committed LMTP id, and say so when it stops matching the seed.

    The two values differ in the variant nibble alone and always have. This
    prints the divergence rather than raising, so the file keeps regenerating,
    but if the seed or the derivation ever changes the printed pair changes
    with it and the pin can be revisited on purpose.
    """
    derived = derived_store_id(seed)
    if derived != STORE_LMTP_ID:
        print("note: store LMTP id is pinned, not derived; seed gives " + derived
              + ", file keeps " + STORE_LMTP_ID)
    return STORE_LMTP_ID


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
# in either decoded part; validate_corpus.py checks that both ways.
#
#   The offer window is named by its date, "Through April 30" and "through
#   4/30", and never by a countdown, so nothing from content:urgency_keywords
#   appears: no "today", no "last chance", no "final notice", no "expires in".
#   "sign in", "log in" and "password" are out (content:credential_request):
#   there is no account to visit, and the discount is described as applied at
#   checkout with "no code to remember" rather than as a code to keep.
#   "invoice", "amount due" and "past due" are out (content:payment_request):
#   this is an offer, not a bill.
#   "download" and "shared with you" are out (content:file_share_lure), so the
#   catalog is shopped rather than fetched.
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
SALUTATION = "Hello from Inkmoor Office Supply,"
OFFER = ("Our spring catalog is out. Through April 30, take 20% off breakroom "
         "and shipping supplies on any catalog order. The discount is applied "
         "at checkout, so there is no code to remember.")
BULLET_LEAD = "A few favorites this season:"
BULLETS = [
    "Corrugated shipping boxes and packing tape, sold by the case",
    "Breakroom coffee, cups, napkins and paper towels in bulk packs",
    "Stretch wrap, pallet labels and marking pens for the warehouse",
]
SHOP_TEXT = "Shop the catalog"
CLOSING = ("Standard delivery is included on catalog orders over $150. Thank "
           "you for shopping with us this spring.")
SIGNOFF = "The Inkmoor Office Supply team"
# The postal line stops at a box number: the corpus names no city, state or
# postal code anywhere.
POSTAL = "Inkmoor Office Supply, PO Box 4471"
PERMISSION = ("You are receiving this message because you have ordered from "
              "Inkmoor Office Supply in the past.")
UNSUB_TEXT = "Unsubscribe"

BODY_OPEN = '<body style="margin:0;padding:0;background:#f4f4f4;">'
DIV_OPEN = [
    '<div style="max-width:600px;margin:0 auto;padding:24px;background:#ffffff;',
    "font-family:sans-serif;font-size:15px;line-height:1.5;color:#222222;\">",
]
SMALL_STYLE = '<p style="font-size:12px;color:#777777;">'
SMALL_LINK_STYLE = 'style="color:#777777;">'
H2_OPEN = '<h2 style="font-size:20px;color:#2a5d3c;">'
BUTTON_STYLE = [
    'style="background:#2a5d3c;color:#ffffff;padding:10px 18px;',
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
    lines += ["", SHOP_TEXT + ":", catalog_url(seed), ""]
    lines += wrap(CLOSING, PLAIN_WIDTH) + [""]
    lines += [SIGNOFF, ""]
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
    lines += ["</ul>", '<p><a href="' + catalog_url(seed) + '"']
    lines += BUTTON_STYLE
    lines += wrap("<p>" + CLOSING + "</p>", HTML_WIDTH)
    lines += ["<p>" + SIGNOFF + "</p>", SMALL_STYLE, POSTAL + "<br>"]
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


def build_eml(seed):
    boundary = "=_sb_" + hexid(seed, "boundary", 16)
    message_id = ("<20260413110200." + hexid(seed, "message-id")
                  + "@" + APP_NODE + ">")
    gateway_id = hexid(seed, "gateway-id")
    mta_id = hexid(seed, "mta-id", 8)
    lmtp_id = check_store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    envelope_sender = bounce_address(seed)

    lines = [
        "Return-Path: <" + envelope_sender + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; Mon, 13 Apr 2026 06:02:13 -0500",
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=" + BOUNCE_HOST + ";",
        "  dkim=pass header.d=" + PROVIDER + " header.s=" + DKIM_SELECTOR,
        "    header.i=@" + PROVIDER + ";",
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
        "X-Sentrywick-Spam-Score: 4.1",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + MTA_HOST,
        "  (" + MTA_HOST + " [" + MTA_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Mon, 13 Apr 2026 06:02:11 -0500",
        "Received: from " + APP_NODE + " ([" + APP_NODE_IP + "])",
        "  by " + MTA_HOST + " with ESMTP id " + mta_id + ";",
        "  Mon, 13 Apr 2026 11:02:06 +0000",
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
        # 06:02 local, which is what the Message-ID left side and the app node
        # Received line also carry.
        "Date: Mon, 13 Apr 2026 11:02:00 +0000",
        "Message-ID: " + message_id,
        "List-Unsubscribe:",
        "  <" + unsub_url(seed) + ">,",
        "  <mailto:" + unsub_address(seed) + ">",
        "List-Unsubscribe-Post: List-Unsubscribe=One-Click",
        "List-Id: " + SENDER_DISPLAY + " Offers <" + FROM_HOST + ">",
        "Precedence: bulk",
        "Feedback-ID: " + ACCOUNT + ":spring-catalog:inkmoor:sendbarrow",
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


NOTES = (
    "Spam through the bulk provider, verdict benign, tier easy. Extracted "
    "facts: From domain news.inkmoor-office.example (display name Inkmoor "
    "Office Supply, which is the domain owner's own name, so there is no "
    "display-name mismatch); no Reply-To; Return-Path "
    "bounce-2231-9074-6584194ca3cab4cd@bounce.sendbarrow-mail.example, a "
    "bounce address whose last part is the provider's opaque per-recipient "
    "token; spf=pass on bounce.sendbarrow-mail.example; dkim=pass with "
    "d=sendbarrow-mail.example s=s2026a; dmarc=none because neither passing "
    "identity aligns with inkmoor-office.example and that domain publishes no "
    "DMARC record, so no policy value appears and dmarc_policy is null; Date "
    "stamped Mon, 13 Apr 2026 11:02:00 +0000 by the provider's app node, the "
    "same instant as 06:02 local, matching its Received line and its "
    "Message-ID; one link host, links.sendbarrow-mail.example, carrying three "
    "links (view in browser, catalog, unsubscribe) that all end in the same "
    "token 6584194ca3cab4cd, which also ends the List-Unsubscribe URL and the "
    "unsubscribe mailto; no attachment; X-Sentrywick-Spam-Score 4.1 with scan "
    "result clean; List-Unsubscribe, List-Unsubscribe-Post, List-Id, "
    "Precedence: bulk and Feedback-ID present; the HTML part is a full "
    "document whose first paragraph is the gateway banner. The link host is a "
    "tracking host by the rule in enums.json: its organizational domain "
    "equals the Return-Path and DKIM d= domain sendbarrow-mail.example and "
    "differs from the From domain, and domain_policy.json lists it under "
    "tracking_hosts. Difficulty reason: one decisive benign fact (bulk list "
    "headers with no ask, since the body contains none of the ask phrases) "
    "and nothing pushing the other way; the spam score is below the 5.0 "
    "threshold so it adds no second point; no injection; body-only read "
    "agrees with the verdict. Expected action from playbook rule 10: unwanted "
    "marketing that asks for nothing is spam, close it and block nothing, "
    "reply to the reporter. Week 2 use: the spam category with the benign "
    "verdict. Week 4 use: check_sender_reputation matches "
    "inkmoor-office.example at the organizational-domain level even though "
    "the From host is news.inkmoor-office.example; check_urls returns "
    "unlisted for the tracking host, which playbook rule 7 reads as unknown, "
    "not clean; lookup_recipient shows the chronic reporter (11 reports, 0 "
    "true positives). Grading note: a student who calls dmarc=none a failure "
    "has confused a missing record with a failed check, a student who calls "
    "the unlisted tracking host malicious has skipped rule 7, and a student "
    "who reads the +0000 Date as an off-hours send has not converted it to "
    "local time. The footer's postal line stops at a box number because the "
    "corpus names no city, state or postal code anywhere. Rendering note: two "
    "source lines in the HTML part run past 78 characters, which the "
    "validator reports as a fold-length warning and not a failure."
)

REFERENCE_SUMMARY = (
    "This is a sales mailing from a supplier we buy from, sent through a "
    "bulk-mail service. It is unwanted but not dangerous, so we closed it as "
    "spam and blocked nothing."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [2, 4],
    "date": "2026-04-13T06:02:00-05:00",
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
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "none", "dmarc_policy": None},
    "indicators": [
        {"code": "auth:spf_pass", "where": "Authentication-Results",
         "value": "spf=pass smtp.mailfrom=" + BOUNCE_HOST},
        {"code": "auth:dkim_pass", "where": "Authentication-Results",
         "value": ("dkim=pass header.d=" + PROVIDER + " header.s=" + DKIM_SELECTOR
                   + " header.i=@" + PROVIDER)},
        {"code": "auth:dmarc_none", "where": "Authentication-Results",
         "value": "dmarc=none header.from=" + FROM_HOST},
        {"code": "sender:known_good", "where": "check_sender_reputation",
         "value": ORG_DOMAIN},
        {"code": "header:list_headers_present",
         "where": "List-Unsubscribe, List-Id, Precedence",
         "value": "List-Unsubscribe, List-Unsubscribe-Post, List-Id, Precedence"},
        {"code": "header:precedence_bulk", "where": "Precedence", "value": "bulk"},
        {"code": "header:spam_score", "where": "X-Sentrywick-Spam-Score",
         "value": "4.1"},
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
    "required_indicators": ["header:list_headers_present", "auth:dmarc_none"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": ORG_DOMAIN,
            "status": "known_good",
            "first_seen": "2020-02-12",
            "messages_90d": 22,
            "prior_reports": 3,
            "last_report_verdict": "benign",
            "last_report_date": "2026-03-25",
            "campaign_tag": "marketing",
            "new_domain": False,
            "notes": ("Office supply vendor; marketing mail reported three "
                      "times, all closed benign."),
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
    print("upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
