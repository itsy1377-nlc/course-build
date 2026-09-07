#!/usr/bin/env python3
"""Regenerate 006-helpdesk-password-expiry.

Rebuilds emails/teaching/006-helpdesk-password-expiry.eml byte for byte from
the corpus seed and upserts the ground truth record in ground_truth.json. The
manifest record in spec/corpus-spec.json is already complete for this email and
is read, never written, so the label and the file cannot drift.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    sender Received id    = hex12("relay-id")[:8]
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

Every identifier in the committed file derives from the seed; none is pinned as
an unexplained literal. The one label that differs from the rest of the corpus
is the sender-side Received id: this file derives it from "relay-id" where the
later external files derive theirs from "sender-id". The label is part of the
derivation, so it is kept as it is rather than renamed, which would change the
committed bytes.

No DKIM-Signature, because the forgery is unsigned: dkim=none is the recorded
result, so there are no seeded bh= and b= values here.

Two more things this file does its own way, both pinned to what is committed:

  * The quoted-printable fold is a hard break at 75 characters plus the soft
    line break, never inside an =XX escape. It never prefers a space. The
    later external files (001, 007, 012) break at the last space that fits,
    which is why their copy of the same gateway banner folds after "[External"
    and this one folds inside "font-size:12px". Only one line in this HTML part
    is long enough to fold at all.
  * The plain part and the HTML part are authored as two line lists rather than
    one, because the HTML part puts <b> around "expires in 24 hours" and that
    shifts every line break in the first paragraph. build_eml checks that the
    two carry the same words once the tags come off, so the parts cannot drift.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. Lenora Vashti is on mailstore-01, and
that is the store whatever path a message took to reach her.

Return-Path carries helpdesk@pellgrave.example, the same address as From. That
is the forgery: the attacker set both to the real shared help desk mailbox, so
the envelope sender aligns with the header sender and the message still fails
SPF, because 198.51.100.201 is not in the pellgrave.example record. The SPF
mechanism on the Received-SPF line and the DMARC policy on the
Authentication-Results line are both read from data/domain_policy.json, so the
rendered headers cannot disagree with the published record the corpus claims.

The store hop is stamped Wed, 15 Apr 2026 07:46:12 -0500, a day after the
gateway hop, and X-Sentrywick-Scan-Result reads released-from-quarantine: the
gateway quarantined the message on Tuesday afternoon, it appeared in the
Wednesday 06:00 digest, and the recipient released it at 07:46 and then
reported it without clicking. Timestamps still never increase from the top of
the chain downward, because release is a delivery, not a second receipt.

Headers deliberately absent, matching the manifest indicator list: no
X-Originating-IP (reserved for webmail submissions), no Auto-Submitted, no
X-Priority and no Importance. The pressure is in the words, not in a flag.

Run:  python3 corpus/tools/generators/gen_006_helpdesk_password_expiry.py
"""

import email
import email.policy
import hashlib
import json
import os
import re
import uuid

EMAIL_ID = "006-helpdesk-password-expiry"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
DOMAIN_POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
UNLISTED_PATH = os.path.join(CORPUS, "data", "url_unlisted.json")
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
SENDER = "helpdesk@" + ORG_DOMAIN
# The envelope sender is the From mailbox. A forgery that sets both to the real
# shared mailbox keeps the two aligned, which is exactly why the SPF result is
# the fact that separates this message from the real help desk notice: the
# address is right and the path is wrong.
ENVELOPE_SENDER = SENDER
RECIPIENT = "l.vashti@" + ORG_DOMAIN
REPORTER = RECIPIENT

SUBJECT = "Your password expires in 24 hours"

# The lookalike host: the letter l in the company name replaced by the digit 1.
# data/url_unlisted.json carries it, so "unlisted" is a checked state here
# rather than an accident of the two lists not mentioning it.
LINK_HOST = "pel1grave.example"
LINK = "https://" + LINK_HOST + "/sso/renew"

# The attacker relay. data/domain_policy.json records bulkhost-nine.example as
# Received-chain infrastructure only, never a From, Reply-To, Return-Path,
# DKIM d= or link domain, and names relay19 at 198.51.100.201 as the hop behind
# this message.
RELAY_HOST = "relay19.bulkhost-nine.example"
RELAY_IP = "198.51.100.201"
ORIGIN_HOST = "api-node-07.bulkhost-nine.example"
ORIGIN_IP = "192.0.2.77"

GATEWAY = "mx." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.10"

# Date is 16:05:00 -0500, so the sender-side hop and the Message-ID stamp read
# 21:05 UTC: the attacker's node stamps in UTC and the gateway and store stamp
# in local time. The Message-ID left side is that UTC stamp, and its right side
# is the originating host at the bottom of the Received chain, which is the
# convention in docs/email-header-realism.md section 7.
MESSAGE_ID_STAMP = "20260414210500"


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


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

    The recipient is a person, so the message is delivered to her directly and
    the LMTP hop names her own store. No list expansion is involved.
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

    pellgrave.example publishes "ip4:203.0.113.8/29 -all", so a client outside
    that range falls through to -all and the gateway reports mechanism=-all.
    """
    record = domain_policy(domain)["spf"]
    if not record:
        raise SystemExit(domain + " publishes no SPF record")
    return record.split()[-1]


def check_link_host_is_unlisted():
    """The link host is on neither list, which is what url:host_unlisted means."""
    known_good = load(KNOWN_GOOD_PATH)
    if (LINK_HOST in known_good["internal_hosts"]
            or LINK_HOST.endswith(known_good["internal_suffix"])):
        raise SystemExit(LINK_HOST + " is on the internal known-good list")
    for entry in load(BLOCKLIST_PATH)["hosts"]:
        if entry["host"] == LINK_HOST:
            raise SystemExit(LINK_HOST + " is on the URL blocklist")
    if LINK_HOST not in load(UNLISTED_PATH)["hosts"]:
        raise SystemExit(LINK_HOST + " is missing from data/url_unlisted.json")


# ---------------------------------------------------------------- body text
#
# The wording is the manifest body_brief: the password expires in 24 hours,
# mailbox access stops when it does, one link labelled "Keep my password", and
# the real help desk signature copied exactly. Three phrase lists in
# spec/enums.json are hit on purpose, and the ground truth records all three:
#
#   content:urgency_keywords, on "expires in", which is the whole lure. The
#   deadline is stated in the subject and again in the first sentence, and
#   never counted down a third time.
#   content:credential_request, on "password" and "sign in".
#
# The lie is the path and the link host, not the prose: this reads exactly like
# a help desk notice, which is why the body-only read is malicious only because
# a real help desk does not link to a sign-in page (playbook rule 3), and why
# the exam twin 051 can say almost the same words honestly.
#
# The signature is copied from the genuine notice byte for byte, so the
# display name and the extension are no help at all and the student has to
# reach the header and the link host.

GREETING_HTML = "Hello Lenora,"

PARA_1_PLAIN = [
    "Your Pellgrave network password expires in 24 hours. When it expires,",
    "your mailbox access stops, and you will not be able to sign in to",
    "email, the intranet or the field app until the help desk resets it.",
]

# The same sentence with <b> around the deadline, which is why the HTML part
# breaks its lines in different places than the plain part.
PARA_1_HTML = [
    "<p>Your Pellgrave network password <b>expires in 24 hours</b>. When it",
    "expires, your mailbox access stops, and you will not be able to sign in",
    "to email, the intranet or the field app until the help desk resets",
    "it.</p>",
]

PARA_2_PLAIN = [
    "To keep your current password and avoid an interruption, sign in",
    "through single sign-on and confirm it before it expires. This takes",
    "less than a minute.",
]

PARA_2_HTML = [
    "<p>To keep your current password and avoid an interruption, sign in",
    "through single sign-on and confirm it before it expires. This takes",
    "less than a minute.</p>",
]

# The plain part carries the link twice the way the HTML part does, once under
# a label that matches the button text and once as a plain address, so a reader
# who only ever sees the text part still sees the host.
LINK_LABEL = "Keep my password"
FALLBACK = "If the link does not open, copy this address into your browser:"

# Copied from the genuine help desk signature, extension and all.
SIGNATURE = "Pellgrave IT Help Desk, ext. 4400"


def greeting(name):
    """Hello, then the first name from data/recipients.json."""
    return "Hello " + name.split()[0] + ","


def plain_part(name):
    lines = [BANNER_PLAIN, "", greeting(name), ""]
    lines += PARA_1_PLAIN + [""]
    lines += PARA_2_PLAIN + [""]
    lines += [LINK_LABEL + ": " + LINK, ""]
    lines += [FALLBACK, LINK, ""]
    lines += [SIGNATURE]
    return lines


def html_part(name):
    return [
        "<html>",
        '<body style="margin:0;padding:0;background:#f2f2f2;">',
        BANNER_HTML,
        '<div style="max-width:600px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#222222;">',
        "<p>" + greeting(name) + "</p>",
    ] + PARA_1_HTML + PARA_2_HTML + [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#1f4e79;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
        "<p>" + FALLBACK + "<br>",
        LINK + "</p>",
        "<p>" + SIGNATURE + "</p>",
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable

QP_MAXLEN = 76
QP_CUT = 75


def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    A hard break at 75 characters plus the soft line break, backed off far
    enough never to land inside an =XX escape. This file does not prefer a
    space; the later external files do, and that is why their fold of the
    gateway banner lands in a different place than this one.
    """
    out = []
    rest = line
    while len(rest) > QP_MAXLEN:
        cut = QP_CUT
        while cut > 1 and "=" in rest[max(0, cut - 2):cut]:
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


# ------------------------------------------------------------------- render

def words(lines):
    """The visible words of an HTML or plain block, tags and entities removed."""
    text = " ".join(lines)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def build_eml(seed):
    check_link_host_is_unlisted()

    boundary = "=_swk_" + hex12(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hex12(seed, "message-id")
                  + "@" + ORIGIN_HOST + ">")
    gateway_id = hex12(seed, "gateway-id")
    relay_id = hex12(seed, "relay-id")[:8]
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)
    policy = domain_policy(ORG_DOMAIN)["dmarc_policy"]
    mechanism = spf_mechanism(ORG_DOMAIN)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Wed, 15 Apr 2026 07:46:12 -0500",
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=fail smtp.mailfrom=" + ORG_DOMAIN + ";",
        "  dkim=none;",
        "  dmarc=fail header.from=" + ORG_DOMAIN + " policy.dmarc=" + policy,
        "Received-SPF: fail (" + GATEWAY + ": domain of",
        "  " + SENDER + " does not designate " + RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + RELAY_IP + '; envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=" + mechanism,
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: released-from-quarantine",
        "X-Sentrywick-Spam-Score: 7.8",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Tue, 14 Apr 2026 16:05:03 -0500",
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + RELAY_HOST + " with ESMTP id " + relay_id + ";",
        "  Tue, 14 Apr 2026 21:05:01 +0000",
        "Date: Tue, 14 Apr 2026 16:05:00 -0500",
        "From: Pellgrave IT Help Desk <" + SENDER + ">",
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
    lines += qp_body(html_part(name))
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    # The two parts say the same thing. The HTML part bolds the deadline and
    # breaks its lines elsewhere, so compare the words rather than the lines.
    if words(PARA_1_HTML) != words(PARA_1_PLAIN):
        raise SystemExit("paragraph 1 differs between the parts")
    if words(PARA_2_HTML) != words(PARA_2_PLAIN):
        raise SystemExit("paragraph 2 differs between the parts")

    plain_text = "\n".join(plain_part(name))
    html_text = "\n".join(html_part(name))
    for phrase in ("expires in 24 hours", "sign in", "password"):
        if phrase not in plain_text.lower():
            raise SystemExit("plain part lost the phrase: " + phrase)
        if phrase not in html_text.lower():
            raise SystemExit("html part lost the phrase: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if plain_text.count(LINK) != 2 or html_text.count(LINK) != 2:
        raise SystemExit("the link must appear twice in each part")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ ground truth

NOTES = (
    "Direct forgery of the organization's own domain. The From address is the "
    "real help desk mailbox, but the message entered through the external "
    "gateway from relay19.bulkhost-nine.example (198.51.100.201), which is not "
    "in the pellgrave.example SPF record (ip4:203.0.113.8/29 -all), so "
    "spf=fail, dkim=none, and dmarc=fail against the published quarantine "
    "policy, which is why dmarc_policy is quarantine. The gateway held it on "
    "Tuesday 14 April at 16:05; the daily digest goes out at 06:00, so it "
    "appeared in the Wednesday 15 April digest, and the store's Received line "
    "is stamped Wed 15 Apr 07:46 local, when Lenora released it, and she "
    "reported it afterwards without clicking, so reported_after_interaction is "
    "false. Message-ID names api-node-07.bulkhost-nine.example, the "
    "originating host at the bottom of the Received chain, following the "
    "header specification convention; bulkhost-nine.example is the attacker "
    "relay provider recorded in domain_policy.json as Received-chain "
    "infrastructure only, never a From domain. Both body parts open with the "
    "gateway's canonical banner, [External message. Sentrywick Gateway]; the "
    "HTML part is quoted-printable because that banner snippet is one source "
    "line longer than 78 characters. Key facts: from_domain pellgrave.example; "
    "reply_to none; spf fail; dkim none; dmarc fail (policy quarantine); "
    "display name matches the address, so no display-name mismatch (the lie is "
    "the path, not the name); url_hosts pel1grave.example (digit 1 for the "
    "letter l, on neither list), reached by one link that appears four times "
    "across the two parts; no attachment. Playbook rules 3 and 7: IT never "
    "links to a sign-in page, and an unlisted host is unknown, not clean. "
    "Difficulty easy: three decisive malicious facts "
    "(auth:dmarc_fail_owned_domain, "
    "sender:internal_domain_via_external_path, url:lookalike_host), no "
    "pressure toward benign, no injection, and the body alone already reads as "
    "a password lure. check_sender_reputation returns status internal at "
    "domain level, which on the external path is the deterministic tell the "
    "week 3 grounding lesson keys on. Escalates under org_domain_forged: a "
    "forged internal domain means a campaign against many mailboxes, so the "
    "SOC searches the gateway log for the same relay and subject. Exam twin: "
    "051, the genuine scheduled notice on the internal path with "
    "Auto-Submitted. Deliberate omissions, matching the manifest indicator "
    "list: no X-Originating-IP (reserved for webmail submissions), no "
    "Auto-Submitted, no X-Priority."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [3],
    "date": "2026-04-14T16:05:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "easy",
    "body_only_read": "malicious",
    "sender_display": "Pellgrave IT Help Desk",
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {"spf": "fail", "dkim": "none", "dmarc": "fail",
             "dmarc_policy": "quarantine"},
    "indicators": [
        {"code": "auth:spf_fail", "where": "Authentication-Results",
         "value": "spf=fail smtp.mailfrom=pellgrave.example"},
        {"code": "auth:dkim_none", "where": "Authentication-Results",
         "value": "dkim=none"},
        {"code": "auth:dmarc_fail", "where": "Authentication-Results",
         "value": ("dmarc=fail header.from=pellgrave.example "
                   "policy.dmarc=quarantine")},
        {"code": "auth:dmarc_fail_owned_domain",
         "where": "Authentication-Results", "value": "pellgrave.example"},
        {"code": "sender:internal_domain_via_external_path",
         "where": "From, Received",
         "value": ("helpdesk@pellgrave.example received by mx.pellgrave.example "
                   "from relay19.bulkhost-nine.example [198.51.100.201]")},
        {"code": "header:released_from_quarantine",
         "where": "X-Sentrywick-Scan-Result",
         "value": "released-from-quarantine"},
        {"code": "url:lookalike_host", "where": "body", "value": LINK_HOST},
        {"code": "url:host_unlisted", "where": "check_urls", "value": LINK_HOST},
        {"code": "url:login_path", "where": "body", "value": LINK},
        {"code": "content:credential_request", "where": "body",
         "value": "password; sign in"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "expires in"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": [
        "auth:dmarc_fail_owned_domain",
        "sender:internal_domain_via_external_path",
        "url:lookalike_host",
    ],
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
            "notes": ("The organization's own domain. A From address on this domain "
                      "arriving through the external gateway is a forgery unless "
                      "quarantined and released."),
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
    "escalate_expected": True,
    "escalation_reasons": ["org_domain_forged"],
    "recommended_action": "escalate_incident",
    "reference_summary": ("Someone outside the company forged our help desk "
                          "address; our mail system flagged it and you released "
                          "it from quarantine before reporting it. Our help desk "
                          "never sends password links, so please ignore it, and "
                          "we are checking whether anyone else received it."),
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
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")

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
    # Checklist item 17: the decoded HTML part carries the banner snippet on
    # one line, so the quoted-printable fold has to come back out.
    html = parsed.get_payload(1).get_content()
    if html.count(BANNER_HTML) != 1:
        raise SystemExit("the decoded HTML part lost the banner snippet")

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
    print("upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
