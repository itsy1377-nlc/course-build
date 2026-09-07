#!/usr/bin/env python3
"""Regenerate 040-quarantine-digest-genuine.

Renders emails/batch/040-quarantine-digest-genuine.eml byte for byte from the
corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    submission Received id = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    held message ids      = hex("held-1", 12) and hex("held-2", 12)

Nothing in the file is pinned as an unexplained literal; every identifier
above is recomputed on each run. There is no DKIM signature and no sender-side
hop, because the message never left the organization.

What this email is. It is the gateway's own daily quarantine digest, and it is
the honest twin of 033, the forged digest that arrives fifteen minutes later.
Everything a reader can check inside the words is the same in both files: a
list of held messages, a Release link on each row, and a product footer. What
separates them sits outside the prose. This one was composed on
mx.pellgrave.example and handed to mail.pellgrave.example over an authenticated
submission, so it never crossed the border and the gateway never authenticated
it; its two links go to quarantine.pellgrave.example, which is on the internal
known-good list in data/known_good_domains.json; and it asks for no sign-in,
because a release page reached from inside the network has nobody to
authenticate. 033 arrives through the gateway from an attacker-owned domain,
links to a blocklisted host, and asks the reader to sign in.

Why the Message-ID right side is mx.pellgrave.example and not the submission
host: the digest has no human author and no client. The border gateway composes
it, so the gateway is the originating mail host and stamps its own id, and the
submission host below it only accepts and forwards. 030 does the same thing
with webaccess.pellgrave.example for a message composed in webmail.

Why this message carries no Authentication-Results, no Received-SPF, no
DKIM-Signature and no X-Sentrywick-External: the gateway submitted its own
digest to the store over an authenticated internal hop, so nothing
authenticated it and nothing stamped it as external, and neither body part
carries the gateway banner. Missing is not failed. The gateway still writes
X-Sentrywick-Scan-Result on its own submissions, and X-Sentrywick-Reported-By,
because every corpus message was reported.

Auto-Submitted: auto-generated is present, and the record carries the matching
header:auto_submitted indicator. RFC 3834 sec. 5 defines the field for system
notices, and a digest that goes to every mailbox every morning sets it so that
out-of-office replies do not come back to a mailbox nobody works.

The first held message in the digest is a quarantined forgery of the
organization's own domain. That is not decoration: data/domain_policy.json
records pellgrave.example at DMARC policy quarantine with the note that
forgeries are quarantined and can be released from the daily digest, and
data/sender_reputation.json says the same thing from the other side. This file
is the daily digest those two records describe, so it shows the mechanism doing
its job rather than only asserting it.

Headers deliberately absent, matching the manifest indicator list: no Reply-To
(reply_to is null and a digest mailbox takes no replies), no In-Reply-To and no
References (thread:new), no X-Sentrywick-Removed-Attachment (attachment:none),
no X-Originating-IP (reserved for webmail submissions), no X-Priority, no
Importance, and no X-Sentrywick-Spam-Score, which the gateway writes only on
mail it authenticated at the border.

Return-Path and From are the same mailbox. data/recipients.json records
sentrywick-digest@pellgrave.example as a shared mailbox with worked_by null, so
the envelope sender already points at a mailbox nobody reads and there is
nothing for a separate bounce address to protect.

Run:  python3 corpus/tools/generators/gen_040_quarantine_digest_genuine.py
"""

import email
import email.policy
import email.utils
import hashlib
import json
import os
import uuid

EMAIL_ID = "040-quarantine-digest-genuine"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

ORG_DOMAIN = "pellgrave.example"
BORDER_HOST = "mx." + ORG_DOMAIN
BORDER_IP = "10.20.4.10"
SUBMIT_HOST = "mail." + ORG_DOMAIN
SUBMIT_IP = "10.20.4.25"

SENDER = "sentrywick-digest@" + ORG_DOMAIN
SENDER_DISPLAY = "Sentrywick Gateway Digest"
# The digest mailbox is its own envelope sender. data/recipients.json records it
# as a shared mailbox with worked_by null, so bounces already land where nobody
# is working; there is no second mailbox to split the RFC 5321 envelope
# identity onto and the file carries no Sender header.
ENVELOPE_SENDER = SENDER

RECIPIENT = "d.crowmarden@" + ORG_DOMAIN
RECIPIENT_DISPLAY = "Devin Crowmarden"
# The person the digest was addressed to is the person who reported it, so the
# mailbox the corpus copy was pulled from is the To address itself.
REPORTER = RECIPIENT

SUBJECT = "Quarantine digest: 2 messages held"

# Date is 06:00:00 -0500, so the Message-ID stamp reads 11:00:00 UTC.
MESSAGE_ID_STAMP = "20260423110000"
DATE_HEADER = "Thu, 23 Apr 2026 06:00:00 -0500"
SUBMIT_STAMP = "Thu, 23 Apr 2026 06:00:01 -0500"
STORE_STAMP = "Thu, 23 Apr 2026 06:00:03 -0500"

# The one link host. It is on the internal known-good list, which is the fact
# url:host_internal_known_good keys on and the fact that separates this file
# from 033, whose release host is blocklisted.
LINK_HOST = "quarantine." + ORG_DOMAIN
RELEASE_PREFIX = "https://" + LINK_HOST + "/release?id="

BANNER = "[External message. Sentrywick Gateway]"


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
    gives it. Every mailbox in the corpus lives on exactly one store, whatever
    path a message took to reach it.
    """
    entry = recipient_record(address)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + address)
    return entry["name"], store


def check_link_host_is_internal():
    """The link host is on the internal known-good list, which is the whole point."""
    known_good = load(KNOWN_GOOD_PATH)
    if (LINK_HOST not in known_good["internal_hosts"]
            and not LINK_HOST.endswith(known_good["internal_suffix"])):
        raise SystemExit(LINK_HOST + " is not on the internal known-good list")


def check_org_is_quarantine_policy():
    """The first held row only makes sense if the organization publishes p=quarantine.

    data/domain_policy.json is the record that says a forged pellgrave.example
    message is held rather than rejected, and therefore that it can appear in
    this digest with a Release link beside it. If that policy ever changes, the
    row below stops being true and this generator says so instead of rendering
    a digest the data files contradict.
    """
    for record in load(DOMAIN_POLICY_PATH)["domains"]:
        if record["domain"] == ORG_DOMAIN:
            if record["dmarc_policy"] != "quarantine":
                raise SystemExit(ORG_DOMAIN + " no longer publishes p=quarantine, so a"
                                 " forged copy of it would not appear in a digest")
            return
    raise SystemExit("domain_policy.json has no record for " + ORG_DOMAIN)


# ---------------------------------------------------------------- body text
#
# The wording is the manifest body_brief: two held messages with their sender,
# their subject and the reason they were held, a Release link each on the
# internal quarantine host, a note that releasing delivers the message to the
# inbox, and the footer "Sentrywick Gateway 7.4 at mx.pellgrave.example".
#
# The record carries no content code, so no phrase from any content list in
# spec/enums.json may appear in either decoded part; validate_corpus.py checks
# that both ways. What that rules out here, and how the text works around it:
#
#   "sign in", "log in", "password" and "credentials" are out
#   (content:credential_request). They are also the single loudest difference
#   between this file and 033, which asks the reader to sign in on an outside
#   host, so the release paragraph says the opposite in plain words: the pages
#   run inside the company network and the link is the only step.
#   "today", "immediately", "within 24 hours", "action required" and the rest
#   of content:urgency_keywords are out, which is why the digest window is
#   named by its two clock times and its two dates, and why the retention line
#   says mail is deleted after 30 days rather than counting down to it.
#   "download" is out (content:file_share_lure), so nothing is offered as a
#   file; a held message is released to the inbox instead.
#   "invoice", "past due" and "remit" are out (content:payment_request), so the
#   held subjects name a storage notice and a tool clearance and no money.
#   "was changed" and "if you did not" are out (content:account_change_notice),
#   which is why the digest never asks the reader whether the held mail was
#   expected; a digest reports what the gateway did and offers the reversal.
#   "call me" and "call the number on file" are out
#   (content:phone_verification_offered); ext. 4400 is a route for a question
#   about a held message, not an offer to confirm anything by phone, and no
#   phrase from that list appears.
#
# The first held row is a forgery of the organization's own domain, held under
# the DMARC policy data/domain_policy.json records for pellgrave.example. The
# second is ordinary bulk mail held on its spam score. Two different reasons
# are what a real digest looks like, and the forged row is the one that makes
# the Release link worth having: an analyst releases a quarantined message to
# read it, which is why the honest digest has links at all and why the forged
# copy is worth building.

HEADING = "Quarantine digest for d.crowmarden@pellgrave.example"

PARA_INTRO = [
    "Two messages addressed to you were held between 6:00 AM Wednesday 4/22",
    "and 6:00 AM Thursday 4/23. They are not in your inbox, and nothing from",
    "them has been delivered to you.",
]

HELD_1 = {
    "sender": "helpdesk@pellgrave.example",
    "subject": "Mail system notice: storage review",
    "held": "Wed 4/22 5:12 PM, DMARC failure, policy quarantine",
    "label": "held-1",
}

HELD_2 = {
    "sender": "sales@coppervane-tools.example",
    "subject": "Spring clearance on hand tools and shop consumables",
    "held": "Thu 4/23 3:41 AM, bulk sender, spam score 7.6",
    "label": "held-2",
}

PARA_RELEASE = [
    "Releasing a message delivers it to your inbox exactly as it arrived. The",
    "release pages run inside the company network, so the link is the only",
    "step.",
]

PARA_RETENTION = [
    "Held mail that is left alone stays in quarantine for 30 days and is then",
    "deleted, so a message you do not want needs nothing from you.",
]

PARA_CONTACT = [
    "Questions about a held message go to the IT help desk on ext. 4400.",
]

# The product footer. 033 forges this line as "Sentrywick Gateway 7.4,
# automated notice"; the real one names the host that wrote the digest, which
# is a host on the internal known-good list.
FOOTER = "Sentrywick Gateway 7.4 at mx.pellgrave.example"


def release_url(seed, held):
    """The Release link for one held message, keyed by its own gateway id.

    The id is the twelve hex digits the gateway would have written in
    X-Sentrywick-Message-UID on the held message itself, so the digest names
    each held message the same way the headers of every other corpus file name
    theirs, and the value is derived from the seed rather than invented.
    """
    return RELEASE_PREFIX + hexid(seed, held["label"])


def held_lines(seed, number, held):
    """One held message as four labelled lines, the same words in both parts."""
    return [
        str(number) + ". From: " + held["sender"],
        "   Subject: " + held["subject"],
        "   Held: " + held["held"],
        "   Release: " + release_url(seed, held),
    ]


def plain_part(seed):
    lines = [HEADING, ""]
    lines += PARA_INTRO + [""]
    lines += held_lines(seed, 1, HELD_1) + [""]
    lines += held_lines(seed, 2, HELD_2) + [""]
    lines += PARA_RELEASE + [""]
    lines += PARA_RETENTION + [""]
    lines += PARA_CONTACT + [""]
    lines += [FOOTER]
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def held_html(seed, number, held):
    """One held message as one <p> with a <br> at each line break.

    The anchor is written over three source lines so that no line of the 7bit
    part runs past 78 characters (RFC 5322 sec. 2.1.1), and the href and the
    visible text are the same address, so a reader of either part sees the
    host the link goes to.
    """
    url = release_url(seed, held)
    rows = held_lines(seed, number, held)
    return [
        "<p>" + rows[0].strip() + "<br>",
        rows[1].strip() + "<br>",
        rows[2].strip() + "<br>",
        "Release: <a",
        '  href="' + url + '"',
        "  >" + url + "</a></p>",
    ]


def html_part(seed):
    lines = ["<html>", "<body>", "<p>" + HEADING + "</p>"]
    lines += paragraph_html(PARA_INTRO)
    lines += held_html(seed, 1, HELD_1)
    lines += held_html(seed, 2, HELD_2)
    lines += paragraph_html(PARA_RELEASE)
    lines += paragraph_html(PARA_RETENTION)
    lines += paragraph_html(PARA_CONTACT)
    lines += ["<p>" + FOOTER + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


# ------------------------------------------------------------------- render

def build_eml(seed):
    check_link_host_is_internal()
    check_org_is_quarantine_policy()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + BORDER_HOST + ">")
    submit_id = hexid(seed, "gateway-id")
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + SUBMIT_HOST + " (" + SUBMIT_HOST
        + " [" + SUBMIT_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # The gateway writes its own verdict even on the mail it sends itself.
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Message-UID: " + submit_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        # The border gateway composed the digest and handed it to the
        # submission host over an authenticated hop. No line is by
        # mx.pellgrave.example, so nothing here crossed the border inbound and
        # the message carries no gateway authentication block.
        "Received: from " + BORDER_HOST + " (" + BORDER_HOST
        + " [" + BORDER_IP + "])",
        "  by " + SUBMIT_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + submit_id + "; " + SUBMIT_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + name + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "Auto-Submitted: auto-generated",
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
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += html_part(seed)
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part(seed))
    html_text = "\n".join(html_part(seed))
    # Section 10 item 17 the other way round: an internal message never carries
    # the gateway's external banner, and this one talks about the gateway in
    # every paragraph, so the check is worth making here.
    if BANNER in plain_text or BANNER in html_text:
        raise SystemExit("an internal message must not carry the external banner")
    for phrase in ("held", "Release", LINK_HOST, FOOTER):
        if phrase not in plain_text or phrase not in html_text:
            raise SystemExit("a part lost the phrase: " + phrase)
    for url in (release_url(seed, HELD_1), release_url(seed, HELD_2)):
        if plain_text.count(url) != 1 or html_text.count(url) != 2:
            raise SystemExit("each release link appears once in the plain part and"
                             " twice in the HTML part: " + url)
    # No sign-in wording anywhere: the release pages are reached from inside the
    # network, and the absence is the contrast 033 is built against.
    for marker in ("sign in", "log in", "password", "credential"):
        if marker in plain_text.lower() or marker in html_text.lower():
            raise SystemExit("the body carries sign-in wording: " + marker)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------ manifest and ground truth

BODY_BRIEF = (
    "The digest table: two held messages (sender, subject, reason quarantined) "
    "with a 'Release' link each to https://quarantine.pellgrave.example/release?id=... "
    "and a note that releasing a message delivers it to the inbox. Use 'held' "
    "and 'release'. No sign-in wording: the links work from inside the network. "
    "Footer: 'Sentrywick Gateway 7.4 at mx.pellgrave.example'. As rendered the "
    "digest heads itself 'Quarantine digest for d.crowmarden@pellgrave.example', "
    "gives the window as 6:00 AM Wednesday 4/22 to 6:00 AM Thursday 4/23, and "
    "lists row 1 helpdesk@pellgrave.example, 'Mail system notice: storage "
    "review', held Wed 4/22 5:12 PM on a DMARC failure at policy quarantine, "
    "and row 2 sales@coppervane-tools.example, 'Spring clearance on hand tools "
    "and shop consumables', held Thu 4/23 3:41 AM as a bulk sender at spam "
    "score 7.6. It says the release pages run inside the company network so the "
    "link is the only step, that held mail left alone is deleted after 30 days, "
    "and that questions go to the IT help desk on ext. 4400."
)

LURE_SUMMARY = (
    "The gateway's real daily digest lists two held messages with Release links "
    "on the internal quarantine host. Auto-submitted, internal path, no sign-in."
)

MANIFEST_NOTES = (
    "Pairs with 033. The internal path and internal link host decide it. "
    "Submitted by the SOC analyst himself as the reference case for the fake "
    "digest. The first held row is a quarantined forgery of the organization's "
    "own domain, which is the mechanism domain_policy.json and "
    "sender_reputation.json both describe for pellgrave.example at DMARC policy "
    "quarantine."
)

# The reference_summary is the model answer the reporter is graded against, and
# every other benign record addresses the reporter directly. Here the reporter
# and the recipient are the same person, d.crowmarden@pellgrave.example, so the
# second sentence speaks to her rather than about "the analyst" in the third
# person. corpus/spec/corpus-spec.json carries the same two sentences; this
# generator does not write that field back, so the two are edited together.
REFERENCE_SUMMARY = (
    "This is the gateway's real daily digest, sent from inside the company to "
    "the internal quarantine page. It is safe, and you submitted it yourself "
    "as the reference copy for the fake digest that arrived fifteen minutes "
    "later."
)

REPUTATION_NOTES = (
    "The organization's own domain. A From address on this domain arriving "
    "through the external gateway is a forgery unless quarantined and released."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null, because the message never crossed the border "
    "gateway and the file carries no Authentication-Results header at all; "
    "display_name_mismatch false, since Sentrywick Gateway is a name "
    "data/display_names.json records as owned by pellgrave.example and sourced "
    "from this very mailbox, sentrywick-digest@pellgrave.example, and the "
    "display name carries no domain of its own; url_hosts "
    "quarantine.pellgrave.example, from two links that appear once each in the "
    "plain part and twice each in the HTML part, where the href and the visible "
    "text are the same address; no removed-attachment header; no In-Reply-To "
    "and no References, so the thread is new. Received chain: "
    "mx.pellgrave.example [10.20.4.10], the border gateway that composed the "
    "digest, handed it to mail.pellgrave.example [10.20.4.25] with ESMTPSA at "
    "06:00:01 -0500, and mail.pellgrave.example delivered it by LMTP to "
    "mailstore-02.pellgrave.example at 06:00:03; Date is 06:00:00. No Received "
    "line is by mx.pellgrave.example, which is what makes this an internal path "
    "rather than an inbound one: the gateway sent this message, it did not "
    "accept it. The LMTP hop reads for <d.crowmarden@pellgrave.example> and "
    "names mailstore-02, the store data/recipients.json gives that mailbox. "
    "Return-Path and From are both sentrywick-digest@pellgrave.example, the "
    "shared digest mailbox recipients.json records with worked_by null, so "
    "there is no envelope split and no Sender header. The Message-ID right side "
    "is mx.pellgrave.example, the host that composed the digest, not the "
    "submission host below it. X-Sentrywick-External is absent, which the "
    "extractor records as header:external_flag with the value no, and neither "
    "body part carries the gateway banner, because the gateway inserts it only "
    "into the mail it stamps as external. The gateway still wrote "
    "X-Sentrywick-Scan-Result: clean on its own submission, and "
    "X-Sentrywick-Reported-By names Devin Crowmarden, who reported it. "
    "Auto-Submitted: auto-generated is present, the RFC 3834 section 5 header a "
    "daily digest to every mailbox sets so that out-of-office replies do not "
    "come back to a mailbox nobody works; the extractor records it as "
    "header:auto_submitted. There is no X-Sentrywick-Spam-Score, because the "
    "gateway writes one only on mail it authenticated at the border, and no "
    "X-Originating-IP, X-Priority or Importance. Body: multipart/alternative, a "
    "text/plain part then a text/html part, both 7bit and carrying the same "
    "words, so a part-to-part diff is empty; the HTML part is plain paragraphs "
    "with two anchors and no image, script, form, styling trick or hidden text. "
    "Content: the digest heads itself Quarantine digest for "
    "d.crowmarden@pellgrave.example, says two messages addressed to him were "
    "held between 6:00 AM Wednesday 4/22 and 6:00 AM Thursday 4/23 and that "
    "nothing from them was delivered, then lists both rows with sender, "
    "subject, the time and reason each was held, and a Release link on "
    "quarantine.pellgrave.example. Row 1 is helpdesk@pellgrave.example, Mail "
    "system notice: storage review, held on a DMARC failure at policy "
    "quarantine, which is a forged copy of the organization's own help desk "
    "address; that row is the mechanism data/domain_policy.json describes when "
    "it records pellgrave.example at p=quarantine with the note that forgeries "
    "are quarantined and can be released from the daily digest. Row 2 is "
    "sales@coppervane-tools.example, a tool clearance mailing held as a bulk "
    "sender at spam score 7.6. The message then says releasing delivers a held "
    "message to the inbox exactly as it arrived, that the release pages run "
    "inside the company network so the link is the only step, that held mail "
    "left alone is deleted after 30 days, and that questions go to the IT help "
    "desk on ext. 4400. It closes with the product footer Sentrywick Gateway "
    "7.4 at mx.pellgrave.example. The wording stays clear of every phrase list "
    "in spec/enums.json, which is why the window is named by its clock times "
    "rather than by a countdown, why retention is a date rather than an expiry, "
    "and why the record carries no content code; the absence of any sign-in "
    "wording is the deliberate one, because it is the loudest difference "
    "between this file and 033. Difficulty reason: the tier rule counts one "
    "decisive benign fact, the organization's own domain on the internal path, "
    "against no pressure facts, so the base tier is easy; the body-only read is "
    "uncertain rather than the opposite of the verdict, so no adjustment "
    "applies. No injection. For the instructor: this is the reference half of "
    "the week 7 digest pair. 033 arrives fifteen minutes later with the same "
    "shape, three held rows instead of two, a Release link on a blocklisted "
    "outside host and a sign-in step, and the same product name in its footer. "
    "Read body against body the two are hard to separate, which is why "
    "body_only_read is uncertain here: a digest that invites a click is exactly "
    "the shape of the phish. The facts separate them at once. Full credit on "
    "the indicators criterion needs sender:internal_domain and "
    "url:host_internal_known_good, the two that do the separating: the sender "
    "is the organization's own domain on the internal path, and the only link "
    "host is on the internal known-good list in data/known_good_domains.json. "
    "The week 4 loop should stop after one call: check_sender_reputation "
    "returns status internal at domain level, which is the stated stop "
    "condition, so stop_reason is internal_sender; check_urls would only "
    "confirm that quarantine.pellgrave.example is internal, and "
    "lookup_recipient would only confirm that Devin Crowmarden is an ordinary "
    "mailbox with no report history. Escalation: none. The verdict is benign, "
    "the category is legit_internal, and no benign escalation rule fits, since "
    "nothing here fails authentication on a trusted sender, touches a banking "
    "item or asks an unknown sender's question, so recommended_action is "
    "close_benign_reply_to_reporter. Story context: Devin Crowmarden is the SOC "
    "analyst, and his recipients.json record holds no prior reports at all. He "
    "did not report this because he was fooled by it. He reported it so the "
    "queue would hold the genuine article beside the forgery, which is the only "
    "way an agent learns that the product name in a footer is not the tell."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-23T06:00:00-05:00",
    "verdict": "benign",
    "category": "legit_internal",
    "difficulty": "easy",
    "body_only_read": "uncertain",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "internal",
    "auth": {"spf": None, "dkim": None, "dmarc": None, "dmarc_policy": None},
    "indicators": [
        {"code": "auth:not_evaluated_internal", "where": "Authentication-Results",
         "value": None},
        {"code": "sender:internal_domain", "where": "From, Received",
         "value": ORG_DOMAIN},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "url:host_internal_known_good", "where": "check_urls",
         "value": LINK_HOST},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "no"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:internal_domain",
                            "url:host_internal_known_good"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": ORG_DOMAIN,
            "status": "internal",
            "first_seen": "2019-05-01",
            "messages_90d": 0,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": REPUTATION_NOTES,
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "internal"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
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
    "expected_loop": {"tools": ["check_sender_reputation"],
                      "stop_reason": "internal_sender"},
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
    # Every semantic field is read and checked, never written.
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if record["sender_address"] != SENDER:
        raise SystemExit("sender_address does not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("the manifest now carries a Reply-To")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest now carries an attachment or an injection")
    if record["arrival_path"] != "internal":
        raise SystemExit("arrival_path is no longer internal")
    if record["date"] != GROUND_TRUTH["date"]:
        raise SystemExit("the manifest date is not the rendered Date")

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
    for name in ("Authentication-Results", "Received-SPF", "DKIM-Signature",
                 "X-Sentrywick-External", "Reply-To", "In-Reply-To"):
        if parsed[name] is not None:
            raise SystemExit(name + " must not appear on this message")

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
