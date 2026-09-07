#!/usr/bin/env python3
"""Regenerate 028-hollinvale-shared-invoice.

Rebuilds emails/batch/028-hollinvale-shared-invoice.eml byte for byte from the
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

This is the second wave from the customer mailbox 018 already sent from, six days
later and to a different employee. Every header is honest again: Hollinvale's own
server really sent it, so spf, dkim and dmarc all pass and the reputation record
still says known_good. What changed is the payload host. 018 pointed at
secure-doc-viewer.example, which the SOC blocked on 2026-03-19, so check_urls
answered the question. docshare-review.example is on no list at all, so check_urls
answers "unlisted" and settles nothing, every tool is spent, and the loop stops on
tools_exhausted with the pattern as the only evidence. That is why this one is in
the week 7 batch rather than in the teaching set.

The link text carries url:login_path rather than the path. The vocabulary entry in
spec/enums.json reads "a link path or text asks for a sign-in"; the path here is
/s/hollinvale-q1, an ordinary share path, and the sentence beside the link is what
asks. 008 and 017 record the code the same way.

This record used to carry recipient:reported_after_interaction, and it no longer does.
The vocabulary entry sources that code from lookup_recipient, but that tool answers
about a mailbox rather than about a single report: l.vashti@pellgrave.example receives
seven emails in this corpus and reported six of them without touching anything, so a
flag on her record would be wrong six times over. Nothing else a student's agent can
reach carries the fact either. X-Sentrywick-Reported-By is byte for byte the reporter
header every other file has, and no data file records it. So the code, the required
indicator built on it, the user_interacted escalation reason it derived and the
password-reset sentence in reference_summary are all gone, and the record now claims
only what the message, the tools and the data files can show.

Run:  python3 corpus/tools/generators/gen_028_hollinvale_shared_invoice.py
"""

import base64
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "028-hollinvale-shared-invoice"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "r.solheim@hollinvalepm.example"
SENDER_DISPLAY = "Renata Solheim"
SENDER_DOMAIN = "hollinvalepm.example"
RECIPIENT = "l.vashti@pellgrave.example"
RECIPIENT_DISPLAY = "Lenora Vashti"
REPORTER = RECIPIENT

SUBJECT = "Invoice review for Hollinvale properties (secure share)"

# The payload host. data/url_unlisted.json holds it and data/domain_policy.json
# classes it attacker owned with no SPF, no DKIM selector and no DMARC record, so
# check_urls returns unlisted and the host signs nothing. The path is an ordinary
# share path; the sign-in ask is in the prose beside the link.
LINK_HOST = "docshare-review.example"
LINK = "https://" + LINK_HOST + "/s/hollinvale-q1"

# The customer's own hosts. The submission hop is Hollinvale's webmail front end,
# which is how a stolen password gets used: the attacker signs in to the real
# service and sends from the real mailbox.
WEBMAIL_HOST = "webmail." + SENDER_DOMAIN
WEBMAIL_IP = "192.0.2.88"
RELAY_HOST = "mail." + SENDER_DOMAIN
RELAY_IP = "203.0.113.96"

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
# Renata's register, the same one 018 renders: a salutation, two short
# paragraphs, one link, a sign-off and the block her webmail client appends.
# Nothing hurries, nothing argues and nothing explains itself, because the
# attacker holding the mailbox has her sent items to copy the voice from. That is
# what makes body_only_read benign on a malicious message and what makes this one
# hard.
#
# Two content codes are recorded and exactly two phrase lists in spec/enums.json
# may match, which build_eml() checks against the rendered parts:
#
#   content:file_share_lure, from "shared them securely" in the first paragraph
#   and "secure share" in the link text. Both are entries in that list.
#   content:credential_request, from "sign in" in the second paragraph. The share
#   asking her to sign in with her work email address is the whole mechanism, so
#   the phrase has to be in the body and not only in the Subject.
#
# Everything else stays out, and the near misses are deliberate. The Subject says
# "Invoice review" because that is what the thread is about, but the body says
# "bills" throughout: "invoice" is a content:payment_request phrase, the record
# names no payment code, and a phrase in the body that no indicator names is a
# fact a student's own extractor finds and the ground truth misses. The board
# meeting is a week out and named by date, so no phrase from
# content:urgency_keywords appears. The ask is to confirm the amounts, which is
# nothing like "confirm your account", and there is no "if you did not", no
# "reply by email" and no "call me".

SALUTATION = "Lenora,"

PARA_1 = [
    "The three bills from the winter service calls are ready for review and I",
    "need them checked before our board meeting on the 28th. Rather than send",
    "them as attachments, I have shared them securely.",
]

LINK_TEXT = "Open secure share"

PARA_2 = [
    "The share will ask you to sign in with your work email address before the",
    "folder opens. If the amounts match what your office has on file, send me",
    "a line back and I will put them in the board packet.",
]

SIGN_OFF = ["Thanks,", "Renata"]

# The same block 018 renders, because it is the same person and the same webmail
# client, which appends it whatever the writer types above it.
SIGNATURE_BLOCK = [
    "Renata Solheim",
    "Property Manager, Hollinvale Property Management",
    "555-0128",
]


def plain_part():
    lines = [BANNER_PLAIN, "", SALUTATION, ""]
    lines += PARA_1 + [""]
    lines += [LINK_TEXT + ": " + LINK, ""]
    lines += PARA_2 + [""]
    lines += SIGN_OFF + [""]
    lines += SIGNATURE_BLOCK
    return lines


def html_part():
    return [
        "<html>",
        ('<body style="margin:0;padding:0;font-family:sans-serif;font-size:15px;'
         'line-height:1.5;color:#1f1f1f;">'),
        BANNER_HTML,
        '<div style="padding:16px 18px;">',
        "<p>" + SALUTATION + "</p>",
        "<p>" + " ".join(PARA_1) + "</p>",
        '<p><a href="' + LINK + '">' + LINK_TEXT + "</a></p>",
        "<p>" + " ".join(PARA_2) + "</p>",
        "<p>" + "<br>".join(SIGN_OFF) + "</p>",
        ('<p style="color:#555555;">' + "<br>".join(SIGNATURE_BLOCK) + "</p>"),
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

# The content codes this record names, and the phrase from each list that has to
# be in the rendered body for it. validate_corpus.py runs the enums.json lists
# over the decoded parts in both directions, so a list that matches and is not
# here fails the build, and a code here whose list does not match fails it too.
CONTENT_CODES = {
    "content:credential_request": ["sign in"],
    "content:file_share_lure": ["shared them securely", "secure share"],
}


def assert_content_phrases(plain_text, html_text):
    """Exactly the recorded content codes may match a phrase list in enums.json.

    The two lists the phrase pass skips are skipped here too:
    content:non_english_body is Spanish stopwords that sit inside English words,
    and content:instruction_to_ai is single words the corpus also uses inside
    quoted examples.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    haystack = (plain_text + "\n" + html_text).lower()
    for code, phrases in sorted(enums["content_phrases"].items()):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases if phrase.lower() in haystack]
        if hits and code not in CONTENT_CODES:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + " but this record does not name " + code)
        if code in CONTENT_CODES and not hits:
            raise SystemExit("this record names " + code
                             + " but no phrase from its list appears in the body")
    for code, wanted in CONTENT_CODES.items():
        for phrase in wanted:
            if phrase.lower() not in haystack:
                raise SystemExit("the recorded " + code + " value names " + repr(phrase)
                                 + ", which is not in the rendered body")


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<20260421150700." + hexid(seed, "message-id")
                  + "@" + WEBMAIL_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Tue, 21 Apr 2026 10:07:07 -0500",
        # The customer publishes SPF (mx -all), signs with selector hv1 and
        # publishes DMARC p=quarantine, all three from data/domain_policy.json.
        # The mail really did leave Hollinvale's server, so all three pass. What
        # they prove is the domain, not the person at the keyboard.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=hv1",
        "    header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=quarantine",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  " + SENDER + " designates " + RELAY_IP + " as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=" + RELAY_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        # Clean again, and a score only a little above 018's. A signed note from
        # a customer the gateway has carried since 2023 gives it nothing to hold,
        # and the one link is to a host no list has an opinion about.
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 2.3",
        "X-Sentrywick-Message-UID: " + gateway_id,
        # Set when she reported the message. It records who reported and nothing
        # else, and it is byte for byte the reporter line every other file in the
        # corpus carries, so no artifact here says what she did before reporting.
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Tue, 21 Apr 2026 10:07:05 -0500",
        # Sender-side stamps are UTC; 15:07:02 +0000 is 10:07:02 local.
        "Received: from " + WEBMAIL_HOST + " ([" + WEBMAIL_IP + "])",
        "  by " + RELAY_HOST + " with ESMTPSA id " + sender_id + ";",
        "  Tue, 21 Apr 2026 15:07:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=" + SENDER_DOMAIN + "; s=hv1; t=1776784022;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash(seed) + ";",
    ]
    chunks = signature(seed)
    for index in range(0, len(chunks), 72):
        lines.append(("  b=" if index == 0 else "   ") + chunks[index:index + 72])
    lines += [
        "Date: Tue, 21 Apr 2026 10:07:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        # No "Re:" this time and no In-Reply-To: the store files it as the start
        # of a thread, and the Subject names the topic rather than claiming a
        # conversation, which is thread:new and nothing else.
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
        if text.count(LINK) != 1:
            raise SystemExit("the link must appear once in the " + label + " part")
    if plain_text.splitlines()[0] != BANNER_PLAIN:
        raise SystemExit("the plain part must open with the gateway banner")
    assert_content_phrases(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Renata's normal voice again, six days after 018 and to a different employee. "
    "Salutation 'Lenora,', then two short paragraphs. First: 'The three bills from the "
    "winter service calls are ready for review and I need them checked before our board "
    "meeting on the 28th. Rather than send them as attachments, I have shared them "
    "securely.' One link, 'Open secure share' to " + LINK + ", written as an anchor in "
    "the HTML part and as 'Open secure share: <url>' in the plain part, and it is the "
    "only link in either part. Second paragraph: 'The share will ask you to sign in with "
    "your work email address before the folder opens. If the amounts match what your "
    "office has on file, send me a line back and I will put them in the board packet.' "
    "The sentence beside the link is what carries url:login_path, because the path "
    "/s/hollinvale-q1 is an ordinary share path and the vocabulary entry reads 'a link "
    "path or text asks for a sign-in'. Sign off 'Thanks,' then 'Renata', then the same "
    "block 018 renders: name, role with organization, and the direct line 555-0128. Only "
    "two phrase lists in spec/enums.json may match: content:file_share_lure through "
    "'shared them securely' and 'secure share', and content:credential_request through "
    "'sign in'. Say 'bills' and never 'invoice', which is a content:payment_request "
    "phrase the record does not name; the Subject carries the word instead. No urgency "
    "wording, no attachment, no quoted text and no second link host."
)

LURE_SUMMARY = (
    "A property management customer's real mailbox sends the sales director three "
    "service bills to review in a secure document share, and the share asks her to sign "
    "in with her work email address. The tone is the mailbox owner's own and every "
    "authentication check passes, so the only thing out of place is a document host that "
    "is on no list at all."
)

MANIFEST_NOTES = (
    "Week 7 batch, and the second wave from the mailbox 018 sends from. The same "
    "customer, the same honest headers and the same known_good reputation, but a fresh "
    "payload host that is on neither list, so check_urls returns unlisted and settles "
    "nothing. The loop spends all three tools and stops on tools_exhausted with no "
    "decisive fact at all: the verdict has to come from the pattern, which is a trusted "
    "partner's mailbox asking an employee to sign in on a host nobody has heard of. An "
    "agent that learned in 018 to call check_urls on a trusted sender finds out here "
    "that the blocklist was never the point. Nothing a student's agent can reach records "
    "what the reporter did before she reported, so this record claims nothing about it. "
    "Escalation reason: partner_account_compromise, which dmarc pass over a known_good "
    "customer domain gives on its own."
)

MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:known_good",
    "url:host_unlisted:" + LINK_HOST,
    "url:login_path",
    "content:credential_request",
    "content:file_share_lure",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
]

# ------------------------------------------------------------- ground truth

AUTH_VALUE = ("spf=pass smtp.mailfrom=" + SENDER_DOMAIN + "; dkim=pass header.d="
              + SENDER_DOMAIN + " header.s=hv1 header.i=@" + SENDER_DOMAIN
              + "; dmarc=pass header.from=" + SENDER_DOMAIN
              + " policy.dmarc=quarantine")

GT_INDICATORS = [
    {"code": "auth:all_pass", "where": "Authentication-Results", "value": AUTH_VALUE},
    {"code": "sender:known_good", "where": "check_sender_reputation",
     "value": SENDER_DOMAIN},
    {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
    {"code": "url:login_path", "where": "body",
     "value": (LINK + "; The share will ask you to sign in with your work email "
               "address before the folder opens")},
    {"code": "content:credential_request", "where": "body", "value": "sign in"},
    {"code": "content:file_share_lure", "where": "body",
     "value": "shared them securely; secure share"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
]

GT_NOTES = (
    "The second message from a customer mailbox somebody else is holding, and the week 7 "
    "case where no tool answers the question. Everything a header can say is true: "
    "hollinvalepm.example publishes SPF (mx -all), signs with selector hv1 and publishes "
    "DMARC p=quarantine, the message left mail.hollinvalepm.example after being submitted "
    "to that domain's own webmail front end, and spf, dkim and dmarc all pass and align. "
    "Key facts a correct extractor produces: from_domain hollinvalepm.example; "
    "reply_to_domain none (no Reply-To header); spf pass; dkim pass; dmarc pass with "
    "policy quarantine; display_name_mismatch false, because data/display_names.json "
    "gives Renata Solheim to hollinvalepm.example and the address is on that domain; "
    "url_hosts docshare-review.example, one link that appears once in each body part; no "
    "removed-attachment header; no In-Reply-To, no References and no Re: prefix, so the "
    "only thread fact is thread:new. auth:all_pass is neutral and counts for nothing: "
    "three passes prove the mail came from the domain it names, and the domain is not the "
    "thing that changed. "
    "The link host is the whole difference from 018. secure-doc-viewer.example went on "
    "the local blocklist on 2026-03-19, so check_urls closed that case in two calls. "
    "docshare-review.example is in data/url_unlisted.json and on neither list, and "
    "data/domain_policy.json classes it attacker owned with no SPF, no DKIM selector and "
    "no DMARC record, so it signs nothing and this message never claims it does. "
    "check_urls returns unlisted, which is not clean and not dirty, and playbook rule 7 "
    "says an unlisted host is unknown rather than safe. The path is /s/hollinvale-q1, an "
    "ordinary share path, so url:login_path is recorded on the link text rather than the "
    "path: the vocabulary entry in spec/enums.json reads 'a link path or text asks for a "
    "sign-in', and the sentence beside the link is what asks. 008 and 017 record it the "
    "same way. "
    "Difficulty hard: for a malicious verdict the tier rule counts no decisive fact at "
    "all and one fact pressing the other way, sender:known_good, so the base tier is "
    "already the top of the scale, and the benign body-only read would move it a further "
    "step if the scale went that far. There is no injection. Content: the mailbox owner's "
    "own register, two short paragraphs about bills from the winter service calls and a "
    "board meeting a week out, then her sign-off and the block her webmail client "
    "appends. Exactly two phrase lists in spec/enums.json match, which is why the record "
    "carries exactly two content codes and why the generator fails the build if a third "
    "creeps in: content:file_share_lure from 'shared them securely' and 'secure share', "
    "and content:credential_request from 'sign in'. Both carry polarity PB, which the "
    "tier rule counts only toward a benign verdict, so neither moves the malicious tier. "
    "The word 'invoice' is deliberately kept out of both parts and left in the Subject "
    "alone, because it is a content:payment_request phrase and this record names no "
    "payment code. No urgency phrase appears: the board meeting is named by date and is a "
    "week away. body_only_read is benign because the body alone is ordinary customer "
    "mail: a share notice from a contact she deals with every month, and the sign-in ask "
    "belongs to the document service she is being sent to rather than to the sender. "
    "Body: multipart/alternative, a text/plain part in 7bit then a text/html part in "
    "quoted-printable, the same words in both, no image, no script, no hidden text and "
    "one anchor. Received chain: webmail.hollinvalepm.example [192.0.2.88] submitted with "
    "ESMTPSA to mail.hollinvalepm.example at 15:07:02 +0000, which is 10:07:02 local; "
    "mail.hollinvalepm.example [203.0.113.96] handed it to mx.pellgrave.example over "
    "TLS1_3 at 10:07:05 -0500; the gateway delivered by LMTP to "
    "mailstore-01.pellgrave.example at 10:07:07; Date is 10:07:00, the same instant as "
    "15:07:00 +0000 in the Message-ID. mailstore-01 is the store data/recipients.json "
    "gives l.vashti@pellgrave.example. Scan result clean, spam score 2.3. "
    "Week 7 loop: check_sender_reputation returns known_good at domain level, first seen "
    "2023-08-15, 14 messages in 90 days, no prior reports and no campaign tag, which is "
    "not decisive and pushes toward benign; check_urls returns unlisted, which is not "
    "decisive either; lookup_recipient returns an ordinary Director of Sales with three "
    "reports closed before the window, one of them a true positive tagged "
    "credential-phish, and nothing whatever about the message in hand, because the tool "
    "answers about a mailbox and not about a report. No call is decisive, so the loop "
    "stops with stop_reason tools_exhausted "
    "after all three, and the verdict rests on the pattern rather than on a list: a "
    "trusted partner's mailbox sending an employee to a sign-in page on a host nobody has "
    "an opinion about. recipient:prior_similar_report is absent, and correctly so: the "
    "rule in spec/enums.json maps a credential ask to no campaign tag, because a prior "
    "credential-phish report is the ordinary state of a mailbox and says nothing about "
    "the message in hand. Full credit on the indicators criterion needs "
    "sender:known_good and url:host_unlisted, because a note that stops at the unlisted "
    "host has not seen who the sender really is. recipient:reported_after_interaction is "
    "deliberately absent, and this record is where it used to sit. The vocabulary entry "
    "in spec/enums.json sources that code from lookup_recipient; lookup_recipient answers "
    "about a mailbox rather than about one report, l.vashti@pellgrave.example is the "
    "recipient of seven emails in this corpus and reported six of them without touching "
    "anything, and no header, tool result or data file records what she did before she "
    "reported this one. Scoring a student on it would score a fact no artifact carries, "
    "so the code is gone from the indicator list and from required_indicators. Escalates "
    "once, under partner_account_compromise, because dmarc passed and the reputation is "
    "known_good, so the mail genuinely came off the customer's server and the account "
    "behind it is in someone else's hands. Blocking the "
    "host protects Pellgrave and leaves Hollinvale sending this to everyone else on "
    "Renata's contact list, so the SOC telephones them on the number it already holds "
    "rather than replying to the mailbox. Story context: 018 taught the agent to call "
    "check_urls on a trusted sender; this is where that habit runs out and the pattern "
    "has to carry the verdict. Deliberate omissions, matching the indicator list: no "
    "Reply-To, no X-Priority, no Auto-Submitted, no X-Originating-IP, no List headers, no "
    "attachment and no quoted text."
)

REFERENCE_SUMMARY = (
    "Renata's real mailbox sent this, but the link goes to a sign-in page on a host we "
    "have no record of, so we are treating her account as taken over. Do not open it, "
    "and tell us if you already have; we are calling Hollinvale by phone so they can "
    "secure her account."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-21T10:07:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
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
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "quarantine"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:known_good", "url:host_unlisted"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
            "status": "known_good",
            "first_seen": "2023-08-15",
            "messages_90d": 14,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Property management customer.",
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "unlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
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
    "expected_loop": {"tools": ["check_sender_reputation", "check_urls",
                                "lookup_recipient"],
                      "stop_reason": "tools_exhausted"},
    "escalate_expected": True,
    "escalation_reasons": ["partner_account_compromise"],
    "recommended_action": "escalate_incident",
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
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("manifest url_hosts is " + repr(record["url_hosts"]))
    if record["sender_address"] != SENDER or record["recipient"] != RECIPIENT:
        raise SystemExit("manifest sender or recipient has drifted")

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
