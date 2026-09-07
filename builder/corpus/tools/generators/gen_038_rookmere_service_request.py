#!/usr/bin/env python3
"""Regenerate 038-rookmere-service-request.

Rebuilds emails/batch/038-rookmere-service-request.eml byte for byte from the
corpus seed, refreshes the matching manifest fields in spec/corpus-spec.json,
and upserts the ground truth record in ground_truth.json. It touches no other
record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the corpus
derives them, so rerunning this script reproduces the same bytes:

    hex(label, n)         = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    stream(label, n)      = sha256("<seed>|<id>|<label>|<block>") for block 0, 1, 2 ...

Neither DKIM value verifies. They are seeded bytes of the right length, the same
convention the rest of the corpus uses, because no .example domain can publish a
key and no lab checks a signature.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

The boundary prefix is "=_part_", the generic one 007, 013, 017, 018, 022, 026
and 028 use, and not the "=_swk_" our own submission host writes: this message
was composed on a customer's own client and never touched a Pellgrave host until
the gateway accepted it.

What makes this one worth reporting is the gateway, not the writer. Rookmere's
SPF record chases more DNS lookups than RFC 7208 sec. 4.6.4 allows, so the check
ends in permerror rather than pass, and the gateway answers a result it cannot
evaluate with X-Sentrywick-Scan-Result: suspect and a spam score of 5.0. The
DKIM signature still verifies and still aligns with the From domain, which is
all DMARC needs, so dmarc=pass with policy.dmarc=none. Everything under the
banner is an ordinary Friday morning service call from a customer of four years,
and the only thing in it that a phrase list can see is the hurry: this morning,
today, as soon as possible. There is no link, no attachment, no account word and
no money word, which is what makes it the medium case it is labelled. The
pressure the analyst has to hold is the tone plus the gateway verdict against
one decisive benign fact, a known_good sender whose DMARC passes.

There is no X-Originating-IP header. The sender is the customer's own mail
server rather than a webmail provider, and the manifest lists no
header:x_originating_ip indicator, so the client address 192.0.2.118 appears in
the bottom Received line instead.

Run:  python3 corpus/tools/generators/gen_038_rookmere_service_request.py
"""

import base64
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "038-rookmere-service-request"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "facilities@rookmeremedical.example"
SENDER_DISPLAY = "Rookmere Medical Plaza Facilities"
SENDER_DOMAIN = "rookmeremedical.example"
SENDER_HOST = "mail.rookmeremedical.example"
SENDER_IP = "203.0.113.90"
RECIPIENT = "h.quintanilla@pellgrave.example"
RECIPIENT_DISPLAY = "Hollis Quintanilla"
SUBJECT = "Chiller 2 alarm again this morning, can someone come out today?"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters.
QP_MAXLEN = 76


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def signature(seed):
    """344 base64 characters, the length of a 2048 bit RSA signature."""
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


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


# ---------------------------------------------------------------- body text
#
# This is a customer with a service contract typing at twenty past seven with
# the plant already warming up, so the register is short sentences, one fact
# per sentence, a detail he repeats because he is worried about it, and an
# apology at the end. It is not course prose and it does not argue that it is
# safe; nothing in a real service call ever does.
#
# The record names exactly one content code, content:urgency_keywords, and the
# corpus verifier reads every phrase list in spec/enums.json against both
# decoded parts in both directions. So three phrases have to be here, whole and
# findable, and nothing from any other list may be. Two near misses are
# deliberate and both are the wording a facilities man would actually use:
# the chiller "dropped out again", never "not working", which is a
# content:excuse_for_external_address phrase; and "give it a call on the way
# in", never "call me", which is content:phone_verification_offered. The words
# invoice, wire, sign in, password, download, account and confidential are
# absent for the same reason.
#
# Line breaks are placed so that no urgency phrase is split across a line in
# the plain part: "this morning", "today" and "as soon as possible" each sit
# whole on one line. The HTML part joins the same lines with single spaces, so
# the two parts carry the same words and the HTML hides nothing.

SALUTATION = "Hello Hollis,"

# The alarm, the time, and what they already tried. A service manager reads the
# second sentence first: it tells him whether this is a reset or a repair.
PARA_1 = [
    "Chiller 2 tripped the high pressure alarm again at 6:10 this morning",
    "and the panel locked it out. Our building mechanic reset it once, it",
    "ran about twenty minutes and dropped out again, so we have left it",
    "off rather than keep cycling the machine.",
]

# Why it matters, in the terms a medical plaza measures: rooms, departments
# and clinic hours. No dollar figure and no contract language, because a man
# with a warm imaging suite is not writing about either.
PARA_2 = [
    "That leaves us on chiller 1 alone. The west corridor is already warm,",
    "imaging has called twice about their room temperatures, and by the",
    "middle of the afternoon the second floor will be uncomfortable for the",
    "patients waiting in it. We have clinic running until 6.",
]

# The ask, and the checkable reference: the third alarm since the end of March
# is the thing Hollis can match against his own service history, the way 012
# cites quote 4712 and 011 cites PO 20431. No data file records service calls,
# so nothing looks it up.
PARA_3 = [
    "Is there any chance of getting a technician out here today? This is",
    "the third alarm on that machine since the end of March and I would",
    "rather someone looked at the head pressure properly than have us keep",
    "resetting the panel and hoping.",
]

# The fallback, which is what makes the hurry ordinary rather than a lever: he
# says plainly what he will do if the answer is no.
PARA_4 = [
    "If nobody is free, please tell me as soon as possible and I will chase",
    "portable units for imaging instead. Sorry to land this on you first",
    "thing.",
]

# Practical arrival instructions. The plant room extension is the number the
# manifest asks for, and it is the channel an out of band check would use.
PARA_5 = [
    "Whoever comes out can reach the plant room on extension 2140. Give it",
    "a call on the way in and I will meet you at the north dock with the",
    "keys, because the service corridor stays locked until 7.",
]

CLOSING = "Thanks,"

# The house block for an external human signer, the shape 012 and 018 use:
# name, role, organization, a dialable number. 555-0139 is unused elsewhere in
# the corpus, and the extension repeats the one in the body because that is
# what a signature block does. This block read 555-0148 until the 2026-09
# manifest pass, when a scan of every decoded body found 042 already using
# that number for Cottonmoor Facilities Show: two unrelated external
# organizations on one main line. 038 moved because its own brief was the one
# claiming the number was unique.
SIGNATURE_BLOCK = [
    "Curtis Nwachukwu-Bell",
    "Facilities Supervisor",
    "Rookmere Medical Plaza",
    "555-0139, ext. 2140",
]

PARAGRAPHS = [PARA_1, PARA_2, PARA_3, PARA_4, PARA_5]

# The content:urgency_keywords phrases this body carries, in the order they are
# written. The ground truth value is built from this list, and build_eml()
# proves that these three and only these three match spec/enums.json.
URGENCY_PHRASES = ["this morning", "today", "as soon as possible"]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", SALUTATION, ""]
    for paragraph in PARAGRAPHS:
        lines += paragraph + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE_BLOCK
    return lines


def html_part():
    return [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#f5f5f5;">',
        BANNER_HTML,
        ('<div style="max-width:620px;margin:18px auto;padding:20px 24px;'
         'background-color:#ffffff;border:1px solid #d8dcdf;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#1f1f1f;">'),
        ('<p style="margin:0 0 16px 0;font-size:17px;font-weight:bold;'
         'color:#1d4f6c;">Rookmere Medical Plaza</p>'),
        "<p>" + SALUTATION + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        "<p>" + joined(PARA_3) + "</p>",
        "<p>" + joined(PARA_4) + "</p>",
        "<p>" + joined(PARA_5) + "</p>",
        "<p>" + CLOSING + "</p>",
        '<p style="color:#555555;">' + "<br>".join(SIGNATURE_BLOCK) + "</p>",
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start of
    the next line; when no space fits, hard-break at 75 characters plus the soft
    line break, never inside an =XX escape.
    """
    out = []
    rest = line
    while len(rest) > QP_MAXLEN:
        cut = rest.rfind(" ", 1, QP_MAXLEN)
        if cut <= 0:
            cut = QP_MAXLEN - 1
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


# ------------------------------------------------------------------- checks

def assert_content_phrases(plain_text, html_text):
    """Exactly one content list may match, and it has to match exactly URGENCY_PHRASES.

    validate_corpus.py runs the phrase lists in spec/enums.json over the decoded
    parts in both directions: a phrase with no indicator is a fact the record
    does not name, and an indicator with no phrase is a fact the extractor
    cannot find. The two lists the phrase pass skips are skipped here too.
    content:non_english_body is Spanish stopwords that sit inside English words,
    and content:instruction_to_ai is single words the corpus also uses inside
    quoted examples.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    phrases = enums["content_phrases"]
    haystack = (plain_text + "\n" + html_text).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in haystack]
        if code == "content:urgency_keywords":
            if hits != URGENCY_PHRASES and sorted(hits) != sorted(URGENCY_PHRASES):
                raise SystemExit("the body matches the urgency phrases " + repr(hits)
                                 + " but the record records " + repr(URGENCY_PHRASES))
        elif hits:
            raise SystemExit("the body carries the " + code + " phrase " + repr(hits[0])
                             + " but this record names no such content code")
    # Each recorded phrase has to survive the line breaks in the plain part too,
    # so a reader of the .eml sees the same fact the extractor found.
    for phrase in URGENCY_PHRASES:
        if phrase.lower() not in plain_text.lower():
            raise SystemExit("the plain part splits the urgency phrase " + repr(phrase))
        if phrase.lower() not in html_text.lower():
            raise SystemExit("the html part lost the urgency phrase " + repr(phrase))


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<20260424121900." + hexid(seed, "message-id")
                  + "@" + SENDER_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Fri, 24 Apr 2026 07:19:07 -0500",
        # rookmeremedical.example publishes SPF (mx -all), signs with selector
        # rm1 and publishes DMARC p=none, all three from data/domain_policy.json.
        # The SPF record chases more than the ten DNS lookups RFC 7208 sec.
        # 4.6.4 permits, so the evaluation ends in permerror: not a failure, an
        # answer the checker could not reach. DKIM verifies and d= equals the
        # From domain, so one aligned pass is enough for dmarc=pass.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=permerror smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=rm1",
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=none",
        "Received-SPF: permerror (mx.pellgrave.example: permanent error while",
        "  evaluating the SPF record of " + SENDER_DOMAIN + ": DNS lookup",
        "  limit exceeded) receiver=mx.pellgrave.example;",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom",
        "X-Sentrywick-External: yes",
        # The gateway will not call a message clean when one of the three checks
        # returned an error it cannot interpret, so the verdict is suspect and
        # the score sits on the reporting threshold. That verdict, and not
        # anything in the body, is why this message reached the queue.
        "X-Sentrywick-Scan-Result: suspect",
        "X-Sentrywick-Spam-Score: 5.0",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + RECIPIENT,
        "Received: from " + SENDER_HOST,
        "  (" + SENDER_HOST + " [" + SENDER_IP + "])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Fri, 24 Apr 2026 07:19:05 -0500",
        # The customer's own facilities workstation, submitting to the customer's
        # own server. Sender-side stamps are UTC, which is 07:19 local here.
        "Received: from RMP-FAC-0231.rookmeremedical.example ([192.0.2.118])",
        "  by " + SENDER_HOST + " with ESMTPSA id " + sender_id + ";",
        "  Fri, 24 Apr 2026 12:19:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SENDER_DOMAIN + "; s=rm1; t=1777033142;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash(seed) + ";",
    ]
    chunks = signature(seed)
    for index in range(0, len(chunks), 72):
        lines.append(("  b=" if index == 0 else "   ") + chunks[index:index + 72])
    lines += [
        "Date: Fri, 24 Apr 2026 07:19:00 -0500",
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
    lines += plain_part()
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += qp_body(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part())
    html_text = "\n".join(html_part())
    for text, label in ((plain_text, "plain"), (html_text, "html")):
        if text.count(BANNER_PLAIN) != 1:
            raise SystemExit("the gateway banner must appear once in the " + label + " part")
        if "http" in text or "mailto:" in text:
            raise SystemExit("the " + label + " part carries a link; this record is url:none")
    if plain_text.splitlines()[0] != BANNER_PLAIN:
        raise SystemExit("the plain part must open with the gateway banner")
    if plain_text.splitlines()[1] != "":
        raise SystemExit("the banner must be followed by one empty line")
    assert_content_phrases(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A harried facilities note in five short paragraphs, opening 'Hello Hollis,' the "
    "way every person-addressed external message opens. Chiller 2 tripped its high "
    "pressure alarm again at 6:10 this morning and the panel locked it out; the "
    "building mechanic reset it once, it ran about twenty minutes and dropped out "
    "again, so they have left it off. They are on chiller 1 alone, the west corridor "
    "is warm, imaging has called twice about room temperatures, and by the middle of "
    "the afternoon the second floor will be uncomfortable for patients, with clinic "
    "running until 6. Ask whether a technician can come out today, and give the "
    "checkable reference: this is the third alarm on that machine since the end of "
    "March, so he would rather someone looked at the head pressure than keep "
    "resetting the panel. Say that if nobody is free he needs to know as soon as "
    "possible so he can chase portable units instead, and apologise for landing it "
    "first thing. Close with arrival instructions: reach the plant room on extension "
    "2140, give it a call on the way in, and he will meet the technician at the north "
    "dock with the keys because the service corridor stays locked until 7. Use "
    "'this morning', 'today' and 'as soon as possible', and no other phrase from any "
    "list in spec/enums.json: write 'dropped out again' rather than 'not working', "
    "and 'give it a call on the way in' rather than 'call me'. No link, no "
    "attachment, no account, sign-in or payment word. Sign with a name (Curtis "
    "Nwachukwu-Bell, Facilities Supervisor), the organization, and the direct line "
    "555-0139 with extension 2140."
)

LURE_SUMMARY = (
    "A long-standing customer's facilities office reports a chiller alarm and asks "
    "for a same-day visit, with no link and no attachment. SPF returns permerror "
    "because the customer's record exceeds the DNS lookup limit; DKIM passes and "
    "aligns, so DMARC passes."
)

MANIFEST_NOTES = (
    "The customer is known_good (service contract since 2022, 61 messages, one "
    "benign report). One of at most two permerror messages in the corpus. Reported "
    "because the gateway marked it suspect and the tone was anxious. Rendering "
    "notes: SPF returns permerror because rookmeremedical.example publishes a record "
    "that chases more than the ten DNS lookups RFC 7208 sec. 4.6.4 allows, so the "
    "gateway wrote Received-SPF: permerror with no mechanism pair and no aligned SPF "
    "pass; DKIM verifies with selector rm1 and d= equals the From domain, and one "
    "aligned pass is all DMARC needs, so dmarc=pass with policy.dmarc=none from "
    "data/domain_policy.json. The gateway will not call a message clean when a check "
    "returned an error it cannot interpret, so X-Sentrywick-Scan-Result is suspect "
    "and X-Sentrywick-Spam-Score is 5.0; neither is an indicator, because the "
    "authored list scores this record on one decisive benign fact, the known_good "
    "sender with dmarc=pass, against one pressure fact, the urgency wording. The "
    "body carries exactly three content:urgency_keywords phrases, 'this morning', "
    "'today' and 'as soon as possible', and no phrase from any other list in "
    "spec/enums.json: the chiller 'dropped out again' rather than 'not working', "
    "which is a content:excuse_for_external_address phrase, and the reader is asked "
    "to 'give it a call on the way in' rather than 'call me', which is "
    "content:phone_verification_offered. There is no link in either part, no "
    "removed-attachment header and no In-Reply-To. The boundary prefix is '=_part_', "
    "not the '=_swk_' our own submission host writes, because the message was "
    "composed on the customer's client; the plain part is 7bit with hard wraps under "
    "78 characters and the HTML part is quoted printable, because the fixed gateway "
    "banner snippet is longer than 78 characters. Line breaks in the plain part are "
    "placed so that no urgency phrase is split across a line. Every identifier that "
    "looks random is derived from a SHA-256 over the corpus seed, the email id and a "
    "label, so the file regenerates byte for byte."
)

MANIFEST_INDICATORS = [
    "auth:spf_permerror",
    "auth:dkim_pass",
    "auth:dmarc_pass",
    "sender:known_good",
    "content:urgency_keywords",
    "header:external_flag:yes",
    "url:none",
    "attachment:none",
    "thread:new",
]

GT_INDICATORS = [
    {"code": "auth:spf_permerror", "where": "Authentication-Results",
     "value": "spf=permerror smtp.mailfrom=" + SENDER_DOMAIN},
    {"code": "auth:dkim_pass", "where": "Authentication-Results",
     "value": ("dkim=pass header.d=" + SENDER_DOMAIN + " header.s=rm1 "
               "header.i=@" + SENDER_DOMAIN)},
    {"code": "auth:dmarc_pass", "where": "Authentication-Results",
     "value": ("dmarc=pass header.from=" + SENDER_DOMAIN
               + " policy.dmarc=none")},
    {"code": "sender:known_good", "where": "check_sender_reputation",
     "value": SENDER_DOMAIN},
    {"code": "content:urgency_keywords", "where": "body",
     "value": "; ".join(URGENCY_PHRASES)},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "url:none", "where": "body", "value": None},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
]

REFERENCE_SUMMARY = (
    "This is a real service request from Rookmere; the gateway flagged it only "
    "because their mail setup has a technical error. Please handle it as a normal "
    "call."
)

GT_NOTES = (
    "The week 7 case where the gateway is the only thing wrong. Key facts a correct "
    "extractor produces: from_domain rookmeremedical.example; reply_to_domain none "
    "(no Reply-To header); spf permerror, dkim pass, dmarc pass, dmarc_policy none; "
    "display_name_mismatch false, because data/display_names.json gives the name "
    "Rookmere Medical Plaza to that domain and the address is the customer's own "
    "facilities mailbox; url_hosts empty; no removed-attachment header; no "
    "In-Reply-To, so the thread is new. SPF returns permerror because the customer "
    "publishes an SPF record that chases more than the ten DNS lookups RFC 7208 "
    "sec. 4.6.4 allows. That is a fault in their DNS, not a signal about this "
    "message: the check never reached a verdict, so it neither supports nor "
    "contradicts the sender. The DKIM signature verifies with selector rm1 and its "
    "d= equals the From domain, and DMARC needs only one aligned pass, so dmarc=pass "
    "with policy.dmarc=none, the policy data/domain_policy.json records for the "
    "domain. The gateway will not write clean over a check that errored, so "
    "X-Sentrywick-Scan-Result is suspect and X-Sentrywick-Spam-Score is 5.0, and "
    "that verdict plus an anxious tone is why Hollis Quintanilla reported it. "
    "Difficulty reason: the benign tier rule counts one decisive fact, a known_good "
    "sender whose DMARC passes, against one pressure fact, the "
    "content:urgency_keywords phrases in the body, so the base tier is medium; "
    "there is no injection and the body-only read is benign, the same as the "
    "verdict, so neither adjustment applies and it stays medium. Loop reason: "
    "check_sender_reputation answers known_good, which is pressure and not a stop "
    "condition, check_urls has nothing to check because the body carries no link, "
    "and lookup_recipient only confirms that Hollis is an ordinary mailbox with two "
    "prior reports and no flags, so the bounded loop runs the two tools that have "
    "anything to read and ends with no tool left to try. Escalation: none. A "
    "known_good sender with dmarc=pass and no ask trips no rule in the benign branch "
    "of the escalation table, so the action is close_benign_reply_to_reporter. "
    "Content: the body carries three content:urgency_keywords phrases, 'this "
    "morning', 'today' and 'as soon as possible', and no phrase from any other list "
    "in spec/enums.json, so the urgency code is the only content indicator. That is "
    "the whole difficulty of the file. Urgency is pressure against a benign verdict "
    "and a student's extractor will find it, but a building with one chiller left "
    "and a warm imaging suite on a Friday morning is entitled to hurry, and an agent "
    "that treats hurry as evidence closes real customer mail as phishing. The "
    "message names a checkable reference, the third alarm on that machine since the "
    "end of March, offers a fallback of its own if nobody is free, and gives a plant "
    "room extension to ring on the way in, which is what a lure does not do. Story "
    "context: the Rookmere chiller project is the customer job 004 names in the CFO "
    "impersonation, 008 quotes as Q-2291 for the controls package and 044 quotes as "
    "Q-5518 for compressor parts. Here the customer speaks for himself, from his own "
    "domain, and the only thing between him and an ordinary dispatch is a DNS record "
    "nobody at Rookmere has looked at in four years."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-24T07:19:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "medium",
    "body_only_read": "benign",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": RECIPIENT,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "permerror", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:known_good", "auth:dmarc_pass"],
    "url_hosts": [],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "known_good",
            "first_seen": "2022-04-04",
            "messages_90d": 61,
            "prior_reports": 1,
            "last_report_verdict": "benign",
            "last_report_date": "2026-03-20",
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Customer with a service contract.",
            "match_level": "domain",
        },
        "check_urls": {},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
            "role": "Service Manager, Head Office Branch",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 2,
            "true_positive_count_90d": 1,
            "campaign_tags": ["credential-phish", "customer-notice"],
        },
    },
    # Two tools have something to read and neither is decisive, so the run ends
    # because there is no tool left to try, not because it hit the cap of 4.
    # check_urls is not called: the body carries no link, so there is nothing to
    # pass it. spec/corpus-spec.json says tools_exhausted; this renders that.
    "expected_loop": {
        "tools": ["check_sender_reputation", "lookup_recipient"],
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
    "notes": GT_NOTES,
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

    # The semantic fields are the manifest's, not this script's. Every one of
    # them is asserted rather than written, so a drift in either direction stops
    # the build instead of being papered over.
    if record["subject"] != SUBJECT:
        raise SystemExit("manifest subject is " + repr(record["subject"]))
    if record["sender_address"] != SENDER or record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("manifest sender has drifted")
    if record["reply_to"] is not None:
        raise SystemExit("manifest carries a Reply-To; the rendered file has none")
    if record["recipient"] != RECIPIENT or record["reporter"] != RECIPIENT:
        raise SystemExit("manifest recipient or reporter has drifted")
    if record["date"] != GROUND_TRUTH["date"]:
        raise SystemExit("manifest date is " + repr(record["date"]))
    if record["url_hosts"] != [] or record["attachment"] is not None:
        raise SystemExit("manifest names a link host or an attachment")
    if record["injection"] is not None:
        raise SystemExit("manifest carries an injection; this record is benign")
    if sorted(record["indicators"]) != sorted(MANIFEST_INDICATORS):
        raise SystemExit("manifest indicators are " + repr(record["indicators"]))
    for method in ("spf", "dkim", "dmarc"):
        if record["auth"][method] != GROUND_TRUTH["auth"][method]:
            raise SystemExit("manifest auth." + method + " is " + repr(record["auth"][method]))
    if record["tool_expectations"] != GROUND_TRUTH["tool_expectations"]:
        raise SystemExit("manifest tool_expectations disagree with the ground truth")
    if record["expected_loop"] != GROUND_TRUTH["expected_loop"]:
        raise SystemExit("manifest expected_loop disagrees with the ground truth")
    if record["reference_summary"] != REFERENCE_SUMMARY:
        raise SystemExit("manifest reference_summary has drifted")

    data = build_eml(seed)
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
    if BANNER_HTML not in parsed.get_payload(1).get_content():
        raise SystemExit("the decoded HTML part lost the gateway banner")

    record["indicators"] = list(MANIFEST_INDICATORS)
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
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
