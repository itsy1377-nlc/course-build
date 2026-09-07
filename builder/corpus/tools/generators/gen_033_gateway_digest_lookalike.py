#!/usr/bin/env python3
"""Regenerate 033-gateway-digest-lookalike.

Renders emails/batch/033-gateway-digest-lookalike.eml byte for byte from the
corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    the three release ids = hex("release-id-1", 12), -2, -3

Nothing in the file is pinned as an unexplained literal; every identifier
above is recomputed on each run. There is no DKIM-Signature and there are no
seeded bh= and b= values, because the recorded result is dkim=none: the
attacker signs nothing. sentrywick-release.example publishes no DKIM selector
in data/domain_policy.json either, so a signature here would contradict the
data file.

What this email is. It is a fake copy of the organization's own quarantine
digest. The gateway product Pellgrave runs is called Sentrywick, and its
digest sender writes the display name "Sentrywick Gateway"; the attacker
registered sentrywick-release.example, put that same display name on it, and
mailed a digest fifteen minutes after the genuine 06:00 one (040). The lie is
not in the authentication line. SPF passes, because the attacker owns the
domain he is sending from and publishes "mx ~all" for it; there is no DKIM
signature and no DMARC record, so dkim=none and dmarc=none, which is what an
unremarkable small sending domain looks like. The lie is that an outside
domain is wearing the name of an inside system, and that the three Release
links go to release.sentrywick-release.example, a host already on the SOC
blocklist from a threat-sharing feed, where the reader is asked to sign in
with a Pellgrave account.

Three facts decide it and all three are in this file or one tool call away:
the display name claims an internal system, the From domain imitates the
organization's own gateway product, and the link host is blocklisted. Nothing
in the body pushes the other way, so the tier rule gives easy. The body-only
read is uncertain on purpose: read without the headers this is a competent
copy of a digest, and the reader who has only the prose cannot tell it from
the real one that arrived at 06:00. That is the pairing with 040 the manifest
names, and it is why this email is in the week 7 batch rather than in a
teaching week.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox
rather than of the path the message arrived on. Devin Crowmarden is on
mailstore-02, and that is the store whatever path a message took to reach him.
The SPF mechanism comes from data/domain_policy.json, so the rendered
Received-SPF line cannot disagree with the record the corpus claims
sentrywick-release.example publishes, and the blocklist entry for the link
host is read from data/url_blocklist.json rather than asserted here.

The three held messages the digest lists are furniture the attacker invented:
brimwold-tooling.example, tarnfield-castings.example and
velladown-forms.example appear nowhere else in the corpus, in no data file and
in no other email. They have to be somewhere, because a digest with no rows is
not a digest, and they must not be corpus senders, because a student who looks
one up and finds a reputation record would be chasing the attacker's fiction
instead of the three facts that decide the case.

Wording rules the body obeys, all from spec/enums.json content_phrases. The
record carries exactly one content code, content:credential_request, matched
on "sign in", and validate_corpus.py checks the content lists both ways, so no
phrase from any other list may appear. In particular there is no "today", no
"immediately", no "action required" and no "within 24 hours" (a real digest
does not push, and this copy does not either, which is part of why it works);
no "download", no "invoice", no "past due"; and nothing in the row subjects
trips a list, which is why the shipment row says "has left the yard" rather
than naming a document. The footer line "Sentrywick Gateway 7.4, automated
notice" holds the word "automated", which is on the content:instruction_to_ai
list; that list is in the validator's PHRASE_PASS_SKIP set because its entries
are single words that appear in ordinary prose, and this footer is ordinary
prose in a system notice rather than text aimed at a model. The record carries
no injection, and the body says nothing to an automated reader.

Headers deliberately absent, matching the manifest indicator list: no
Auto-Submitted, although the genuine digest in 040 carries it and a real
system notice would (RFC 3834 sec. 5) - the manifest lists no
header:auto_submitted indicator here, the validator checks that code both
ways, and the omission is also the kind of small thing a forger leaves out; no
X-Originating-IP, which is reserved for webmail submissions; no X-Priority and
no Importance; no DKIM-Signature; no List-* headers, because this is not bulk
mail.

Run:  python3 corpus/tools/generators/gen_033_gateway_digest_lookalike.py
"""

import email
import email.policy
import email.utils
import hashlib
import json
import os
import uuid

EMAIL_ID = "033-gateway-digest-lookalike"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
ALLOWLIST_PATH = os.path.join(CORPUS, "data", "url_allowlist.json")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

ORG_DOMAIN = "pellgrave.example"
GATEWAY = "mx." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.10"

# The attacker's domain. It is not a misspelling of pellgrave.example; it is
# the name of the gateway product the organization runs, with a word added, so
# that the display name "Sentrywick Gateway" and the sending domain agree with
# each other and disagree only with the company. data/domain_policy.json
# records it as attacker owned with an SPF record and no DKIM selector and no
# DMARC record, which is exactly the pass/none/none this file renders.
LOOKALIKE = "sentrywick-release.example"
SENDER = "quarantine@" + LOOKALIKE
# data/display_names.json records "Sentrywick Gateway" as an organization name
# owned by pellgrave.example whose only legitimate writer is the digest sender
# sentrywick-digest@pellgrave.example, with the mismatch indicator
# sender:display_name_claims_internal_system. That is the name on this message.
SENDER_DISPLAY = "Sentrywick Gateway"
# The envelope sender is the From mailbox: the attacker owns the domain, so
# there is nothing to hide behind a bounce address and no Reply-To split.
ENVELOPE_SENDER = SENDER

RECIPIENT = "d.crowmarden@" + ORG_DOMAIN
REPORTER = RECIPIENT

SUBJECT = "Quarantine digest: 3 messages held for your review"

# The sending path. mail.<domain> is the host in the domain's SPF record, so
# SPF passes on the mx mechanism; mta-01 is the attacker's own node behind it.
SENDER_HOST = "mail." + LOOKALIKE
SENDER_IP = "203.0.113.166"
ORIGIN_HOST = "mta-01." + LOOKALIKE
ORIGIN_IP = "192.0.2.166"

# The one link host, on the blocklist since 2026-04-09 from a threat-sharing
# feed. Three links, one per held row, all on this host.
LINK_HOST = "release." + LOOKALIKE
LINK_BASE = "https://" + LINK_HOST + "/release?id="

# Date is 06:15:00 -0500, so the attacker's node and the Message-ID stamp read
# 11:15 UTC while the gateway and the store stamp in local time.
MESSAGE_ID_STAMP = "20260423111500"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">'
               "[External message. Sentrywick Gateway]</p>")


def hexid(seed, label, length=12):
    return hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


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

    The To address is a person rather than a list, so the message is delivered
    to that mailbox itself and the LMTP hop names the store recipients.json
    gives it. Every mailbox in the corpus lives on exactly one store.
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

    sentrywick-release.example publishes "mx ~all", so a client that is one of
    the domain's own MX hosts matches on mx and the gateway reports
    mechanism=mx. The trailing all mechanism is what a client outside the
    record would fall through to, so it is not the one that passes.
    """
    record = domain_policy(domain)["spf"]
    if not record:
        raise SystemExit(domain + " publishes no SPF record")
    mechanisms = [token for token in record.split() if not token.endswith("all")]
    if not mechanisms:
        raise SystemExit(domain + " has no SPF mechanism that can pass")
    return mechanisms[0]


def check_sender_domain_has_no_dkim():
    """dkim=none is a data-file fact, not a choice made in this generator."""
    if domain_policy(LOOKALIKE)["dkim_selector"]:
        raise SystemExit(LOOKALIKE + " publishes a DKIM selector; dkim=none is wrong")
    if domain_policy(LOOKALIKE)["dmarc_policy"] is not None:
        raise SystemExit(LOOKALIKE + " publishes a DMARC policy; dmarc=none is wrong")


def check_link_host_is_blocklisted():
    """The link host is on the blocklist, which is what url:host_blocklisted means."""
    known_good = load(KNOWN_GOOD_PATH)
    if (LINK_HOST in known_good["internal_hosts"]
            or LINK_HOST.endswith(known_good["internal_suffix"])):
        raise SystemExit(LINK_HOST + " is on the internal known-good list")
    for entry in load(ALLOWLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL allowlist")
    for entry in load(BLOCKLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            return
    raise SystemExit(LINK_HOST + " is missing from data/url_blocklist.json")


# ---------------------------------------------------------------- body text
#
# The wording is the manifest body_brief: the layout of the real digest, three
# held rows with sender, subject and reason, a Release link on each, and the
# sentence that turns a release into a sign-in. Two phrases the brief names
# appear word for word, "held for your review" in the opening line and "sign
# in" in the closing paragraph, and content:credential_request is recorded on
# the second of them.
#
# The register is a machine writing to one mailbox: no greeting, no signature,
# no person. What makes it convincing is that everything in it is checkable and
# dull - a window with two ends, a retention period, three rows with ordinary
# reasons - and that the one thing it asks for, a sign-in, is the one thing the
# real digest never asks for, because the real one links inside the network.

HEADING = "Sentrywick Gateway"
SUBHEAD = "Quarantine digest for " + RECIPIENT

INTRO = (
    "3 messages are held for your review. They were stopped between 18:00 on "
    "22 April and 06:00 on 23 April. Quarantined mail is kept for 14 days and "
    "then removed."
)

# The three rows. Every domain here is invented for this file alone: none of
# them appears in any data file or in any other email, because they are the
# attacker's furniture rather than corpus senders.
#
# The second row was quillbeck-castings.example and is now tarnfield-castings.
# "Quillbeck" is reserved: gen_004 uses Quillbeck Controls as the BEC payee
# precisely because it resolves to nothing, and it carries a guard that fails
# the build if the token appears in any other manifest record. Both authors
# followed a correct rule and neither rule covered the other's ground: this
# file checked the data files and the other emails, and the reservation lived
# in a generator constant and in manifest prose. Tarnfield was checked against
# the UK, New Zealand and Australian company registers before it was used;
# docs/corpus-naming-record.md holds that evidence.
ROWS = [
    {
        "sender": "news@brimwold-tooling.example",
        "subject": "Second mailing, spring tooling catalogue",
        "reason": "Bulk sender, not on the allow list",
        "label": "release-id-1",
    },
    {
        "sender": "dispatch@tarnfield-castings.example",
        "subject": "Shipment 88214 has left the yard",
        "reason": "Sender not seen before",
        "label": "release-id-2",
    },
    {
        "sender": "alerts@velladown-forms.example",
        "subject": "A form on your site was completed",
        "reason": "Link host on the block list",
        "label": "release-id-3",
    },
]

# The ask. "Sign in" is the credential request, and it is also the whole tell:
# a release from the real quarantine needs no account, because the page sits
# inside the network and the mail store already knows who is asking.
CLOSING = (
    "Each Release link opens the release page. Sign in with your Pellgrave "
    "account and the message is delivered to your inbox. Messages you leave in "
    "quarantine need no action."
)

FOOTER = "Sentrywick Gateway 7.4, automated notice"


def links(seed):
    """The three release URLs, one per row, in row order."""
    return [LINK_BASE + hexid(seed, row["label"]) for row in ROWS]


def plain_part(seed):
    lines = [
        BANNER_PLAIN,
        "",
        HEADING,
        SUBHEAD,
        "",
        INTRO,
        "",
    ]
    for index, (row, link) in enumerate(zip(ROWS, links(seed)), 1):
        lines += [
            str(index) + ". From:    " + row["sender"],
            "   Subject: " + row["subject"],
            "   Reason:  " + row["reason"],
            "   Release:",
            "     " + link,
            "",
        ]
    lines += [CLOSING, "", FOOTER]
    return lines


CELL = "padding:6px 10px;border-bottom:1px solid #e3e7eb;vertical-align:top;"
HEAD_CELL = ("padding:6px 10px;border-bottom:2px solid #c8ced5;"
             "text-align:left;font-weight:bold;color:#5b6570;")


def html_part(seed):
    out = [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:640px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        ('<p style="margin:0 0 2px 0;font-size:13px;letter-spacing:1px;'
         'text-transform:uppercase;color:#5b6570;">' + HEADING + "</p>"),
        ('<p style="margin:0 0 16px 0;font-size:17px;font-weight:bold;">'
         + SUBHEAD + "</p>"),
        "<p>" + INTRO + "</p>",
        ('<table cellpadding="0" cellspacing="0" style="width:100%;'
         'border-collapse:collapse;font-size:14px;">'),
        "<tr>",
        '<th style="' + HEAD_CELL + '">Sender</th>',
        '<th style="' + HEAD_CELL + '">Subject</th>',
        '<th style="' + HEAD_CELL + '">Reason</th>',
        '<th style="' + HEAD_CELL + '">&nbsp;</th>',
        "</tr>",
    ]
    for row, link in zip(ROWS, links(seed)):
        out += [
            "<tr>",
            '<td style="' + CELL + '">' + row["sender"] + "</td>",
            '<td style="' + CELL + '">' + row["subject"] + "</td>",
            '<td style="' + CELL + '">' + row["reason"] + "</td>",
            ('<td style="' + CELL + '"><a href="' + link + '" '
             'style="color:#2f5d8a;font-weight:bold;'
             'text-decoration:none;">Release</a></td>'),
            "</tr>",
        ]
    out += [
        "</table>",
        '<p style="margin-top:20px;">' + CLOSING + "</p>",
        ('<p style="margin:20px 0 0 0;font-size:12px;color:#7a828b;">'
         + FOOTER + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]
    return out


# ------------------------------------------------------- quoted-printable

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters. The
# generator breaks at the last space that leaves the line at 74 characters or
# fewer, so the soft break lands between words wherever the text allows one,
# and falls back to a hard break at 75 characters plus the trailing "=" for
# unbroken runs such as a CSS declaration. The space is carried to the start of
# the next physical line, so an unfolded paragraph is the same string it went
# in as and the raw file still reads cleanly in a text editor. The fallback
# guard never lets a break land inside an "=3D" escape, which matters here
# because every release URL carries one: the "=" of "?id=" encodes as "=3D".
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


# ------------------------------------------------------------------- render

def build_eml(seed):
    check_sender_domain_has_no_dkim()
    check_link_host_is_blocklisted()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)
    mechanism = spf_mechanism(LOOKALIKE)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Thu, 23 Apr 2026 06:15:07 -0500",
        # SPF passes for the domain the attacker owns and sends from. There is
        # no signature and no DMARC record, so the other two clauses are none.
        # Authentication answers "did this come from the domain it names", and
        # here the honest answer is yes; the domain is the problem.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=pass smtp.mailfrom=" + LOOKALIKE + ";",
        "  dkim=none;",
        "  dmarc=none header.from=" + LOOKALIKE,
        "Received-SPF: pass (" + GATEWAY + ": domain of",
        "  " + SENDER + " designates " + SENDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_HOST + "; identity=mailfrom; mechanism=" + mechanism,
        # The gateway did not call it clean. The content scanner scored it 6.2
        # and marked it suspect, which is the state a digest lookalike lands in
        # when it is checked against the shape of the real one.
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: suspect",
        "X-Sentrywick-Spam-Score: 6.2",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_HOST,
        "  (" + SENDER_HOST + " [" + SENDER_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Thu, 23 Apr 2026 06:15:05 -0500",
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + SENDER_HOST + " with ESMTP id " + sender_id + ";",
        "  Thu, 23 Apr 2026 11:15:03 +0000",
        "Date: Thu, 23 Apr 2026 06:15:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + name + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(plain_part(seed))
    lines += [
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(seed))
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part(seed))
    html_text = "\n".join(html_part(seed))
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    for phrase in ("held for your review", "sign in", "3 messages"):
        if phrase not in plain_text.lower() or phrase not in html_text.lower():
            raise SystemExit("a part lost the phrase: " + phrase)
    # Every row and every link has to be in both parts, at the same count, so
    # the plain reader and the HTML reader see one digest and one link host.
    for row, link in zip(ROWS, links(seed)):
        for value in (row["sender"], row["subject"], row["reason"], link):
            if plain_text.count(value) != 1 or html_text.count(value) != 1:
                raise SystemExit("row text is not in both parts exactly once: "
                                 + value)
    if plain_text.count(LINK_HOST) != 3 or html_text.count(LINK_HOST) != 3:
        raise SystemExit("each part must carry the link host three times")
    if FOOTER not in plain_text or FOOTER not in html_text:
        raise SystemExit("a part lost the footer")
    # The body must not talk to an automated reader: the record carries no
    # injection, so nothing here may read as an instruction to a model. The
    # footer's "automated notice" is checked as a whole phrase below rather
    # than by the single word, which is ordinary in a system notice.
    for marker in ("ai triage", "triage assistant", "ai:", "classify",
                   "verdict", "automated triage", "automated reviewers",
                   "automated systems", "pre-classification"):
        if marker in plain_text.lower() or marker in html_text.lower():
            raise SystemExit("the body carries instruction-to-AI wording: "
                             + marker)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------ manifest and ground truth

BODY_BRIEF = (
    "Copy the layout of the real digest: a table of three held messages "
    "(sender, subject, reason) and a 'Release' link for each, all pointing to "
    "https://release.sentrywick-release.example/release?id=... where the "
    "reader must sign in. Use 'held for your review' and 'sign in'. Footer: "
    "'Sentrywick Gateway 7.4, automated notice'. No attachment. As rendered "
    "the notice opens with the heading Sentrywick Gateway over 'Quarantine "
    "digest for d.crowmarden@pellgrave.example', says three messages are held "
    "for your review, gives the window (18:00 on 22 April to 06:00 on 23 "
    "April) and a 14 day retention period, and lists three invented rows: "
    "news@brimwold-tooling.example with a spring tooling catalogue, held as a "
    "bulk sender; dispatch@tarnfield-castings.example with a shipment notice, "
    "held because the sender was not seen before; and "
    "alerts@velladown-forms.example with a completed form, held for a "
    "blocklisted link host. It closes by telling the reader to sign in with a "
    "Pellgrave account so the released message is delivered to the inbox, and "
    "that messages left in quarantine need no action. There is no greeting "
    "and no signature, because a digest is written by a machine."
)

LURE_SUMMARY = (
    "Imitates the gateway's daily digest, listing three held messages with "
    "Release links that lead to a sign-in page on an external host. The real "
    "digest arrives internally and links only to the internal quarantine host."
)

MANIFEST_NOTES = (
    "Pairs with 040, the genuine digest, which arrived from inside the "
    "company fifteen minutes earlier. The lookalike here imitates the "
    "organization's own gateway system rather than a vendor, so the lookalike "
    "target recorded is the organization: sentrywick-release.example wears "
    "the product name Sentrywick and the display name of the internal digest "
    "sender. Auto-contain. No Auto-Submitted header, unlike the real digest, "
    "matching the indicator list."
)

REFERENCE_SUMMARY = (
    "This is a fake copy of the gateway's quarantine digest; the real one "
    "comes from inside the company and never links to an outside site. The "
    "release links go to a blocked page, so ignore it."
)

NOTES = (
    "The batch set's easy credential phish against the SOC's own analyst. It "
    "is a fake copy of the organization's quarantine digest, mailed fifteen "
    "minutes after the genuine 06:00 one that 040 holds, and it copies the "
    "genuine layout: a heading, a held-message table with sender, subject and "
    "reason, and a Release link on every row. Key facts: the From domain is "
    "sentrywick-release.example, which imitates Sentrywick, the mail gateway "
    "and store product the organization runs, by adding a word to the product "
    "name, so the lookalike target recorded in sender:lookalike_domain is "
    "pellgrave.example, the organization whose system is being imitated, "
    "rather than a vendor domain; the display name is Sentrywick Gateway, "
    "which data/display_names.json records as an organization name owned by "
    "pellgrave.example whose only legitimate writer is "
    "sentrywick-digest@pellgrave.example, so an outside address wearing it is "
    "sender:display_name_claims_internal_system; spf=pass because the "
    "attacker owns the domain and publishes 'mx ~all' for it and mail. under "
    "that domain is one of its own MX hosts; dkim=none because nothing is "
    "signed and the domain publishes no selector; dmarc=none with no "
    "policy.dmarc and dmarc_policy null because the domain publishes no DMARC "
    "record; the domain was first seen on 2026-04-23, inside the window, so "
    "reputation is unknown and new; there is no Reply-To; the one link host "
    "release.sentrywick-release.example carries all three Release links, with "
    "the path /release?id= and a seeded twelve hex digit id on each, and it "
    "has been on the SOC blocklist since 2026-04-09 from a threat-sharing "
    "feed; no attachment; a new thread; scan result suspect with a spam score "
    "of 6.2. The three held rows are the attacker's furniture: "
    "brimwold-tooling.example, tarnfield-castings.example and "
    "velladown-forms.example appear in no data file and in no other email. "
    "Playbook rules 3 and 7 apply: the real digest never asks for a sign-in, "
    "because its links sit inside the network, and a blocklisted host is not "
    "a judgment call. Difficulty easy: three decisive facts (a display name "
    "that claims the gateway, a lookalike From domain, and a blocklisted link "
    "host), no pressure toward benign, no injection, and no body-only step, "
    "because the body-only read is uncertain rather than benign. That read is "
    "the point of the pairing: with the headers hidden this is a competent "
    "copy of the 06:00 digest and the prose alone cannot separate it from the "
    "real one, which is why the analyst submitted both. Tools: "
    "check_sender_reputation matches at domain level and returns unknown, "
    "first seen 2026-04-23, six days before the corpus clock, so new_domain "
    "is true; check_urls returns blocklisted for the one link host and the "
    "loop stops there on decisive_malicious after two calls, without "
    "lookup_recipient, because a blocklisted link host settles the verdict "
    "and the recipient's history cannot change it. Does not escalate: no "
    "escalation reason applies, since the category is credential_phish rather "
    "than one with financial or endpoint impact, the recipient is neither an "
    "executive nor a payment handler, nobody interacted with it, the "
    "organization's own domain was not forged in From, and there is no "
    "injection, so the action is block_and_purge. Rendering notes: both parts "
    "are quoted-printable with soft breaks at word boundaries, so each "
    "decoded paragraph is a single line and the raw file still reads cleanly "
    "in a text editor; the '=' in each '?id=' encodes as '=3D'; the gateway "
    "banner is the first line of both parts. Deliberate omissions, matching "
    "the manifest indicator list: no Auto-Submitted, although the genuine "
    "digest carries it, no X-Originating-IP, no X-Priority, no "
    "DKIM-Signature and no List-* headers."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-23T06:15:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "easy",
    "body_only_read": "uncertain",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "none", "dmarc": "none",
             "dmarc_policy": None},
    "indicators": [
        {"code": "auth:spf_pass", "where": "Authentication-Results",
         "value": "spf=pass smtp.mailfrom=sentrywick-release.example"},
        {"code": "auth:dkim_none", "where": "Authentication-Results",
         "value": "dkim=none"},
        {"code": "auth:dmarc_none", "where": "Authentication-Results",
         "value": "dmarc=none header.from=sentrywick-release.example"},
        {"code": "sender:display_name_claims_internal_system", "where": "From",
         "value": "Sentrywick Gateway"},
        {"code": "sender:lookalike_domain", "where": "From",
         "value": ORG_DOMAIN},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-23"},
        {"code": "url:host_blocklisted", "where": "check_urls",
         "value": LINK_HOST},
        {"code": "url:login_path", "where": "body",
         "value": ("Sign in with your Pellgrave account and the message is "
                   "delivered to your inbox.")},
        {"code": "content:credential_request", "where": "body",
         "value": "sign in"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none",
         "where": "X-Sentrywick-Removed-Attachment", "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:display_name_claims_internal_system",
                            "url:host_blocklisted"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": LOOKALIKE,
            "status": "unknown",
            "first_seen": "2026-04-23",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": ("First seen inside the window; its release host is "
                      "already blocklisted from a feed."),
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "blocklisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Devin Crowmarden",
            "role": "Security Analyst (SOC)",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 0,
            "true_positive_count_90d": 0,
            "campaign_tags": [],
        },
    },
    "expected_loop": {
        # The second call settles it: a blocklisted link host is decisive on
        # its own, so the loop stops without calling lookup_recipient.
        "tools": ["check_sender_reputation", "check_urls"],
        "stop_reason": "decisive_malicious",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "block_and_purge",
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
    spec = load(SPEC_PATH)
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
    if record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if record["sender_address"] != SENDER:
        raise SystemExit("sender_address does not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest record carries an attachment or an injection")
    if record["auth"] != {"spf": "pass", "dkim": "none", "dmarc": "none"}:
        raise SystemExit("auth results do not match the manifest")

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
    html = parsed.get_payload(1).get_content()
    if html.count(BANNER_HTML) != 1:
        raise SystemExit("the decoded HTML part lost the banner snippet")
    # The three release URLs have to survive the fold in both parts, "=3D" and
    # all, or the link host a student reads is not the one this file renders.
    plain = parsed.get_payload(0).get_content()
    for link in links(seed):
        if plain.count(link) != 1 or html.count(link) != 1:
            raise SystemExit("a release link did not survive decoding: " + link)

    # The manifest keeps the prose this generator is the source of; every
    # semantic field is read, never written, so the label and the file cannot
    # drift and no other record is touched.
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
