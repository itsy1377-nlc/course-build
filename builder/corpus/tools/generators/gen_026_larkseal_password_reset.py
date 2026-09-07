#!/usr/bin/env python3
"""Regenerate 026-larkseal-password-reset.

Rebuilds emails/batch/026-larkseal-password-reset.eml byte for byte from the
corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record and edits no data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

No DKIM-Signature, because the forgery is unsigned: dkim=none is the recorded
result, so this file derives no bh= and no b= value.

The message is a direct forgery of the electronic signature vendor's own
domain. Return-Path and From both read security@larkseal.example, so the
envelope sender aligns with the header sender and the message still fails SPF,
because 198.51.100.205 is not in the larkseal.example record. The SPF mechanism
on the Received-SPF line and the DMARC policy on the Authentication-Results
line are both read from data/domain_policy.json, so the rendered headers cannot
disagree with the record the corpus claims the vendor publishes. The link host
is checked against the three URL lists at render time, so the url:host_unlisted
claim is a checked state rather than an accident of two lists not mentioning it.

That combination is the trap inside the trap. check_sender_reputation matches
larkseal.example, an allowlisted vendor with 158 messages in 90 days, and
answers trusted; the reputation belongs to a domain this message only claims to
come from. The header decides it and the tool does not.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. Emeric Dawodu is on mailstore-01.

The store hop is stamped Tue, 21 Apr 2026 07:38:20 -0500, the day after the
gateway hop, and X-Sentrywick-Scan-Result reads released-from-quarantine: the
gateway quarantined the message on Monday morning, it appeared in the Tuesday
06:00 digest, and the recipient released it at 07:38 and then reported it
without clicking. Timestamps still never increase from the top of the chain
downward, because release is a delivery and not a second receipt.

The plain part is 7bit: it is ASCII and every line fits inside 78 characters,
which is the convention in docs/email-header-realism.md section 2. The HTML
part is quoted-printable, because the gateway's banner snippet is one source
line longer than that on its own.

Headers deliberately absent, matching the manifest indicator list: no
X-Priority and no Importance (the pressure is in the words), no Auto-Submitted,
no X-Originating-IP, no List-* headers, and no Reply-To, since replies to a
forged vendor alert would land in the vendor's own mailbox and the attacker
wants a click rather than an answer.

Run:  python3 corpus/tools/generators/gen_026_larkseal_password_reset.py
"""

import email
import email.policy
import hashlib
import json
import os
import re
import uuid

EMAIL_ID = "026-larkseal-password-reset"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
REPUTATION_PATH = os.path.join(CORPUS, "data", "sender_reputation.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
ALLOWLIST_PATH = os.path.join(CORPUS, "data", "url_allowlist.json")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
UNLISTED_PATH = os.path.join(CORPUS, "data", "url_unlisted.json")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

ORG_DOMAIN = "pellgrave.example"
VENDOR_DOMAIN = "larkseal.example"
SENDER = "security@" + VENDOR_DOMAIN
# The envelope sender is the From mailbox. A forgery that sets both to the
# vendor's real alert address keeps the two aligned, which is why the SPF result
# is the fact that separates this message from a genuine Larkseal alert: the
# address is right and the path is wrong.
ENVELOPE_SENDER = SENDER
SENDER_DISPLAY = "Larkseal Security"
RECIPIENT = "e.dawodu@" + ORG_DOMAIN
REPORTER = RECIPIENT

SUBJECT = "Larkseal: unusual sign-in detected, reset your password"

# The lookalike host: the vendor's name with the word esign added. It is on
# neither URL list, and data/url_unlisted.json carries it so that state is
# recorded rather than assumed.
LINK_HOST = "larkseal-esign.example"
LINK = "https://" + LINK_HOST + "/account/reset"

# The attacker relay. data/domain_policy.json records bulkhost-nine.example as
# Received-chain infrastructure only, never a From, Reply-To, Return-Path,
# DKIM d= or link domain, and names relay04 at 198.51.100.205 as the hop behind
# this message.
RELAY_HOST = "relay04.bulkhost-nine.example"
RELAY_IP = "198.51.100.205"
ORIGIN_HOST = "api-node-11.bulkhost-nine.example"
ORIGIN_IP = "192.0.2.114"

GATEWAY = "mx." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.10"

SPAM_SCORE = "7.4"

# Date is 09:14:00 -0500, so the attacker's node stamps 14:14 UTC while the
# gateway and the store stamp local time. The Message-ID left side is that UTC
# stamp and its right side is the originating host at the bottom of the Received
# chain, which is the convention in docs/email-header-realism.md section 7.
MESSAGE_ID_STAMP = "20260420141400"
DATE_HEADER = "Mon, 20 Apr 2026 09:14:00 -0500"
ORIGIN_STAMP = "Mon, 20 Apr 2026 14:14:02 +0000"
GATEWAY_STAMP = "Mon, 20 Apr 2026 09:14:05 -0500"
STORE_STAMP = "Tue, 21 Apr 2026 07:38:20 -0500"


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
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

    The recipient is a person, so the message is delivered to that mailbox
    directly and the LMTP hop names its own store. No list expansion is
    involved.
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
    """The last mechanism of the published SPF record, as SPF evaluation reports it.

    larkseal.example publishes "mx -all", so a client that is not one of the
    domain's own mail exchangers falls through to -all and the gateway reports
    mechanism=-all.
    """
    record = domain_policy(domain)["spf"]
    if not record:
        raise SystemExit(domain + " publishes no SPF record")
    return record.split()[-1]


def check_sender_is_allowlisted_vendor():
    """The two facts the record's contradiction rests on, read from the data files.

    sender:allowlisted_domain says check_sender_reputation answers trusted for
    larkseal.example, and auth:dmarc_fail_owned_domain says the From domain
    belongs to a vendor. If either data file ever stops saying so, the rendered
    message stops teaching what the record claims it teaches.
    """
    for record in load(REPUTATION_PATH)["domains"]:
        if record["domain"] == VENDOR_DOMAIN:
            if record["status"] != "trusted":
                raise SystemExit(VENDOR_DOMAIN + " is " + record["status"]
                                 + " in sender_reputation.json, not trusted")
            break
    else:
        raise SystemExit("sender_reputation.json has no record for " + VENDOR_DOMAIN)
    entry = domain_policy(VENDOR_DOMAIN)
    if entry["owner_class"] != "vendor":
        raise SystemExit(VENDOR_DOMAIN + " is owner_class " + entry["owner_class"]
                         + " in domain_policy.json, not vendor")
    if entry["dmarc_policy"] is None:
        raise SystemExit(VENDOR_DOMAIN + " publishes no DMARC policy, so dmarc=fail "
                         "cannot carry one")


def check_link_host_is_unlisted():
    """The link host is on neither list, which is what url:host_unlisted means."""
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
# The wording is the manifest body_brief: a security alert that reports a
# sign-in from a new location and asks for an immediate password reset, one
# button "Reset password" on the lookalike host, and a footer copied from the
# vendor's own alert mail. Two phrase lists in spec/enums.json are hit on
# purpose and the ground truth records both:
#
#   content:urgency_keywords, on "immediately", which is the whole ask.
#   content:credential_request, on "password" and "sign in".
#
# No other phrase list matches, which tools/validate_corpus.py checks in both
# directions for every code whose vocabulary entry says where=body. In
# particular the notice never says "download", which belongs to
# content:file_share_lure, and never says "if you did not", which belongs to
# content:account_change_notice; a real alert would reach for both, and either
# one would add a fact the record does not claim.
#
# The lie is the link host and the path the message took, not the prose. This
# reads exactly like the vendor's own alert, which is why the body-only read is
# malicious for one reason only: a password reset link that does not lead to the
# vendor's own domain (playbook rules 3 and 7). The host is spelled out in both
# parts, under the button and again in the fallback line, so a reader who never
# hovers a link still sees it.

BRAND = "Larkseal"

ALERT = ("We detected a sign-in to your Larkseal account from a new location. "
         "Reset your password immediately to keep your documents safe.")

DETAIL = [
    "Account: " + RECIPIENT,
    "When: Monday 20 April 2026 at 8:52 AM CDT",
    "Where: Ravensmoor, about two states from where you usually work",
    "Device: desktop web browser",
]

FOLLOW_UP = ("You will be asked to sign in with the email address on the account "
             "and then choose a new password. Documents already out for signature "
             "are not affected.")

LINK_LABEL = "Reset password"
FALLBACK = "If the link does not open, copy this address into your browser:"

# Copied from the vendor's genuine alert mail, tagline, postal line, support
# number and all, so the footer is no help at all and the student has to reach
# the header and the link host.
FOOTER = [
    "Larkseal, secure signatures",
    "Larkseal Software Group, 90 Fennimore Row, Ashcroft Bay",
    "Account support 555-0132",
]
FOOTER_NOTE = ("This alert was sent to the address on the account. Replies to this "
               "message are not monitored.")
FOOTER_NOTE_PLAIN = [
    "This alert was sent to the address on the account. Replies to this",
    "message are not monitored.",
]

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;'
               'color:#5a4a00;">[External message. Sentrywick Gateway]</p>')

# The plain part is 7bit, so its lines are wrapped here rather than by the
# encoder. The HTML part carries the same sentences as single logical lines and
# the quoted-printable fold breaks them wherever it must; build_eml checks that
# the two parts still say the same words.
ALERT_PLAIN = [
    "We detected a sign-in to your Larkseal account from a new location.",
    "Reset your password immediately to keep your documents safe.",
]

FOLLOW_UP_PLAIN = [
    "You will be asked to sign in with the email address on the account and",
    "then choose a new password. Documents already out for signature are not",
    "affected.",
]


def greeting(name):
    """Hello, then the first name from data/recipients.json."""
    return "Hello " + name.split()[0] + ","


def plain_part(name):
    lines = [BANNER_PLAIN, "", BRAND, "", greeting(name), ""]
    lines += ALERT_PLAIN + [""]
    lines += DETAIL + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += FOLLOW_UP_PLAIN + [""]
    lines += [FALLBACK, LINK, ""]
    lines += FOOTER + FOOTER_NOTE_PLAIN
    return lines


def html_part(name):
    return [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;font-family:sans-serif;'
         'font-size:15px;line-height:1.5;color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        ('<p style="margin:0 0 20px 0;font-size:20px;font-weight:bold;color:#1b4f8a;">'
         + BRAND + "</p>"),
        "<p>" + greeting(name) + "</p>",
        "<p>" + ALERT + "</p>",
        ('<p style="margin:0 0 16px 0;">' + "<br>".join(DETAIL) + "</p>"),
        ('<p style="margin:24px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:12px 22px;background-color:#1b4f8a;'
         'color:#ffffff;text-decoration:none;font-weight:bold;border-radius:4px;">'
         + LINK_LABEL + "</a></p>"),
        "<p>" + FOLLOW_UP + "</p>",
        ('<p style="font-size:13px;color:#555555;">' + FALLBACK + "<br>" + LINK + "</p>"),
        ('<p style="margin-top:28px;padding-top:12px;border-top:1px solid #d9dee3;'
         'font-size:13px;color:#444444;">' + "<br>".join(FOOTER)
         + "<br>" + FOOTER_NOTE + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters. The
# generator breaks at the last space that leaves the line at 72 characters or
# fewer, so the soft break lands between words wherever the text allows one, and
# falls back to a hard break at 75 characters plus the trailing "=" for unbroken
# runs such as a CSS declaration.

SOFT_MAX = 76
SPACE_MAX = 72


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

def words(lines):
    """The visible words of an HTML or plain block, tags and entities removed."""
    text = " ".join(lines)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def build_eml(seed):
    check_sender_is_allowlisted_vendor()
    check_link_host_is_unlisted()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + ORIGIN_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)
    policy = domain_policy(VENDOR_DOMAIN)["dmarc_policy"]
    mechanism = spf_mechanism(VENDOR_DOMAIN)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=fail smtp.mailfrom=" + VENDOR_DOMAIN + ";",
        "  dkim=none;",
        "  dmarc=fail header.from=" + VENDOR_DOMAIN + " policy.dmarc=" + policy,
        "Received-SPF: fail (" + GATEWAY + ": domain of",
        "  " + SENDER + " does not designate " + RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + RELAY_IP + '; envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=" + mechanism,
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: released-from-quarantine",
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + RELAY_HOST + " with ESMTP id " + sender_id + ";",
        "  " + ORIGIN_STAMP,
        "Date: " + DATE_HEADER,
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
    lines += plain_part(name)
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(name))
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    # The two parts say the same thing. The plain part wraps its sentences by
    # hand and the HTML part carries them whole, so compare the words.
    if words(ALERT_PLAIN) != words([ALERT]):
        raise SystemExit("the alert paragraph differs between the parts")
    if words(FOLLOW_UP_PLAIN) != words([FOLLOW_UP]):
        raise SystemExit("the follow-up paragraph differs between the parts")
    if words(FOOTER_NOTE_PLAIN) != words([FOOTER_NOTE]):
        raise SystemExit("the footer note differs between the parts")

    plain_text = "\n".join(plain_part(name))
    html_text = "\n".join(html_part(name))
    for phrase in ("reset your password", "sign in", "immediately"):
        if phrase not in plain_text.lower():
            raise SystemExit("plain part lost the phrase: " + phrase)
        if phrase not in html_text.lower():
            raise SystemExit("html part lost the phrase: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if plain_text.count(LINK) != 2 or html_text.count(LINK) != 2:
        raise SystemExit("the link must appear twice in each part")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Imitate a Larkseal security alert. Brand line 'Larkseal', then 'Hello Emeric,' "
    "on the line after it, the way every other person-addressed external message in "
    "the corpus opens. First paragraph: 'We detected a sign-in to your Larkseal "
    "account from a new location. Reset your password immediately to keep your "
    "documents safe.', which carries the content:urgency_keywords phrase "
    "'immediately' and the content:credential_request phrase 'password' in the body "
    "and not only in the Subject. Detail block of Account, When, Where and Device, "
    "the four lines a real sign-in alert shows, with the sign-in placed 22 minutes "
    "before the Date and two states away. One button 'Reset password' to "
    "https://larkseal-esign.example/account/reset, the only link in the message, "
    "repeated under a fallback line in both parts so a reader who never hovers a "
    "link still sees the host. Then a line saying the recipient will be asked to "
    "sign in with the email address on the account and then choose a new password, "
    "which is where the second content:credential_request phrase 'sign in' sits. "
    "Footer copies the vendor's own alert footer: the tagline 'Larkseal, secure "
    "signatures', the postal line, the support number, and a note that replies are "
    "not monitored. No second link host, no unsubscribe, no wording from the "
    "content:file_share_lure list ('download') and none from the "
    "content:account_change_notice list ('if you did not'), because a real alert "
    "would reach for both and either would add a fact the record does not claim."
)

LURE_SUMMARY = (
    "Forges the e-signature vendor's own domain and says an unusual sign-in from "
    "another state requires an immediate password reset. The reset button goes to a "
    "host that adds the word esign to the vendor name."
)

MANIFEST_NOTES = (
    "Trap inside the trap: check_sender_reputation rates larkseal.example trusted, "
    "but DMARC fails with policy quarantine, so the reputation belongs to a domain "
    "this message did not come from. Auto-contain: no interaction, not an executive, "
    "a vendor domain forged rather than the org's. Week 7 batch, medium: two decisive "
    "facts against one pressure fact, so an agent that stops at the reputation answer "
    "closes a live credential phish as benign. The rendered file is the second direct "
    "forgery in the corpus after 006 and takes the same shape, a spoofed domain "
    "arriving from bulkhost-nine.example and released from the quarantine digest, "
    "with one difference that carries the whole lesson: 006 forges the organization's "
    "own domain, which no tool calls trusted, and 026 forges an allowlisted vendor's."
)

MANIFEST_INDICATORS = [
    "auth:spf_fail",
    "auth:dkim_none",
    "auth:dmarc_fail",
    "auth:dmarc_fail_owned_domain",
    "sender:allowlisted_domain",
    "header:released_from_quarantine",
    "url:lookalike_host:larkseal-esign.example",
    "url:host_unlisted:larkseal-esign.example",
    "url:login_path",
    "content:credential_request",
    "content:urgency_keywords",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
]


# ------------------------------------------------------------ ground truth

GT_INDICATORS = [
    {"code": "auth:spf_fail", "where": "Authentication-Results",
     "value": "spf=fail smtp.mailfrom=larkseal.example"},
    {"code": "auth:dkim_none", "where": "Authentication-Results",
     "value": "dkim=none"},
    {"code": "auth:dmarc_fail", "where": "Authentication-Results",
     "value": "dmarc=fail header.from=larkseal.example policy.dmarc=quarantine"},
    {"code": "auth:dmarc_fail_owned_domain", "where": "Authentication-Results",
     "value": VENDOR_DOMAIN},
    {"code": "sender:allowlisted_domain", "where": "check_sender_reputation",
     "value": VENDOR_DOMAIN},
    {"code": "header:released_from_quarantine", "where": "X-Sentrywick-Scan-Result",
     "value": "released-from-quarantine"},
    {"code": "url:lookalike_host", "where": "body", "value": LINK_HOST},
    {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
    {"code": "url:login_path", "where": "body", "value": LINK},
    {"code": "content:credential_request", "where": "body", "value": "password; sign in"},
    {"code": "content:urgency_keywords", "where": "body", "value": "immediately"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
]

GT_NOTES = (
    "Direct forgery of an allowlisted vendor's own domain, and the batch set's "
    "answer to 006. The From address is Larkseal's real security alert mailbox, but "
    "the message entered through the external gateway from "
    "relay04.bulkhost-nine.example (198.51.100.205), which is not one of the "
    "larkseal.example mail exchangers the published record permits (mx -all), so "
    "spf=fail, dkim=none, and dmarc=fail against the quarantine policy the vendor "
    "publishes, which is why dmarc_policy is quarantine. The gateway held it on "
    "Monday 20 April at 09:14; the digest goes out at 06:00, so it appeared in the "
    "Tuesday 21 April digest, the store's Received line is stamped Tue 21 Apr "
    "07:38 local, when Emeric released it, and he reported it afterwards without "
    "clicking, so reported_after_interaction is false. Message-ID names "
    "api-node-11.bulkhost-nine.example, the originating host at the bottom of the "
    "Received chain, following the header specification convention; "
    "bulkhost-nine.example is the attacker relay provider recorded in "
    "domain_policy.json as Received-chain infrastructure only, never a From domain. "
    "Both body parts open with the gateway's canonical banner, [External message. "
    "Sentrywick Gateway]; the plain part is 7bit because every line is ASCII and "
    "under 78 characters, and the HTML part is quoted-printable because that banner "
    "snippet is one source line longer than that. Key facts: from_domain "
    "larkseal.example; reply_to none; spf fail; dkim none; dmarc fail (policy "
    "quarantine); display name Larkseal Security over the vendor's own address, so "
    "there is no display-name mismatch at all, and the lie is the path and the link; "
    "url_hosts larkseal-esign.example, the vendor's name with the word esign added, "
    "on neither list, reached by one link that appears twice in each part; no "
    "attachment; no In-Reply-To. Playbook rules 3 and 7: a password reset link that "
    "does not lead to the vendor's own domain is a credential phish, and an unlisted "
    "host is unknown rather than clean. Difficulty medium: two decisive malicious "
    "facts (auth:dmarc_fail_owned_domain, url:lookalike_host) against one fact "
    "pressing the other way, sender:allowlisted_domain, with no injection and no "
    "body-only reversal. That one pressure fact is the whole exercise. "
    "check_sender_reputation matches larkseal.example at domain level and answers "
    "trusted, first seen 2023-02-20, 158 messages in 90 days, two prior reports both "
    "closed benign, no campaign tag, because the vendor is genuinely allowlisted; the "
    "reputation belongs to a domain this message only claims to come from, and the "
    "Authentication-Results header already said so. An agent that treats the "
    "reputation answer as decisive closes a live credential phish as benign, which is "
    "why the loop here runs all three tools and stops with stop_reason "
    "tools_exhausted: no single tool is decisive, check_urls returns unlisted rather "
    "than blocklisted, and lookup_recipient returns an ordinary procurement mailbox. "
    "Does not escalate: the recipient did not interact, he is not an executive, the "
    "forged domain is a vendor's rather than the organization's, and the category is "
    "credential_phish rather than one of the three with financial or endpoint impact, "
    "so the SOC blocks the host and purges the message. The contrast case is 006, "
    "which forges pellgrave.example itself: there the reputation tool answers "
    "internal, the external path makes that answer damning rather than reassuring, "
    "and the message escalates under org_domain_forged. Deliberate omissions, "
    "matching the manifest indicator list: no Reply-To, no X-Priority, no Importance, "
    "no Auto-Submitted, no X-Originating-IP and no unsubscribe line, since a security "
    "alert is transactional mail and the pressure is in the words."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-20T09:14:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "medium",
    "body_only_read": "malicious",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "fail", "dkim": "none", "dmarc": "fail",
             "dmarc_policy": "quarantine"},
    "indicators": GT_INDICATORS,
    "required_indicators": [
        "auth:dmarc_fail_owned_domain",
        "url:lookalike_host",
    ],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": VENDOR_DOMAIN,
            "status": "trusted",
            "first_seen": "2023-02-20",
            "messages_90d": 158,
            "prior_reports": 2,
            "last_report_verdict": "benign",
            "last_report_date": "2026-03-26",
            "campaign_tag": None,
            "new_domain": False,
            "notes": "E-signature vendor; allowlisted.",
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
    "expected_loop": {
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "block_and_purge",
    "reference_summary": ("Someone forged Larkseal's address; our mail system caught "
                          "it and it was released from quarantine before being "
                          "reported. The reset link is fake, so ignore it and your "
                          "account is not affected."),
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
    # Everything semantic in the record is authored, so the generator reads it
    # and refuses to render a file that would disagree with it.
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_address"] != SENDER or record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender does not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("the manifest carries a Reply-To and this file renders none")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest carries an attachment or an injection")
    if record["indicators"] != MANIFEST_INDICATORS:
        raise SystemExit("the manifest indicator list has changed; it is authored, so "
                         "the generator stops rather than overwrite it")

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
    # Checklist item 17: the decoded HTML part carries the banner snippet on one
    # line, so the quoted-printable fold has to come back out.
    html = parsed.get_payload(1).get_content()
    if html.count(BANNER_HTML) != 1:
        raise SystemExit("the decoded HTML part lost the banner snippet")

    record["indicators"] = list(MANIFEST_INDICATORS)
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
    print("updated the manifest prose and upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
