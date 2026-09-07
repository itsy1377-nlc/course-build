#!/usr/bin/env python3
"""Regenerate 001-payroll-deposit-verify.

Rebuilds emails/teaching/001-payroll-deposit-verify.eml byte for byte from the
corpus seed and upserts the ground truth record in ground_truth.json. The
manifest record in spec/corpus-spec.json is already complete for this email and
is read, never written, so the label and the file cannot drift.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_fwp_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    sender Received id    = hex12("sender-id")[:8]
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh               = base64(stream("dkim-bh")[:32])
    DKIM b                = base64(stream("dkim-b")[:256])
    stream(label)         = sha256("<seed>|<id>|<label>|<n>") for n = 0, 1, 2 ...

The boundary prefix is "=_fwp_" rather than the "=_swk_" our own Sentrywick
hosts write, because this message is composed on the sender's side, at
WEB-CLIENT-7.fenwright-pay.example, and handed to mail.fenwright-pay.example.
The boundary belongs to whatever composed the message, so a message from
outside cannot carry the prefix of the product Pellgrave runs. "=_swk_" is
reserved for the messages the Sentrywick stack actually composes, which in the
teaching set are the internal ones: 002, 011 and 019.

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab checks a signature.

Run:  python3 corpus/tools/generators/gen_001_payroll_deposit_verify.py
"""

import base64
import hashlib
import json
import os
import uuid

EMAIL_ID = "001-payroll-deposit-verify"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

LINK = "https://my.fenwrightpay.example.secure-verify-login.example/account/login"


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


# ---------------------------------------------------------------- body text
#
# Each paragraph is written once as the plain-part lines. The HTML part joins
# the same lines with single spaces, so the two parts cannot drift and the
# HTML part hides nothing.
#
# Line breaks are placed so that no content phrase from spec/enums.json is
# split across a line: "action required", "within 24 hours",
# "confirm your direct deposit" and "sign in" each sit whole on one line. The
# phrase pass in tools/validate_corpus.py matches against the decoded part, so
# a phrase broken by a newline would be a phrase the extractor cannot find.

MASTHEAD = "Fenwright Payroll"

GREETING = "Hello Hollis,"

# The pressure sentence. "Action required" opens it, because the manifest's
# body_brief opens the message with those words and the subject repeats them.
# The claim is a failed routine check rather than a threat, which is the
# register a real payroll notice uses.
#
# The timing follows the payroll calendar in section 2.3 of
# docs/phase0-corpus-design.md: pay date Friday 17 April, timesheet cutoff
# Tuesday noon. This message is dated Monday 13 April, so on the day it lands
# the 4/17 run has not been prepared yet and the lure has to point forward at
# the cutoff rather than back at a run that already closed. Noon on Tuesday is
# a little over a day out, which is what puts the 24 hour deadline in the next
# paragraph inside the window rather than past it.
#
# One consequence, stated once: the pay for that run is held, which is what
# the manifest body_brief asks for. A sentence that holds the pay and issues
# it in the same breath threatens nothing.
PARA_1 = [
    "Action required. The routine verification of the direct deposit",
    "account we hold for you has not completed, and the 4/17 payroll is",
    "prepared after the timesheet cutoff at noon tomorrow. If the",
    "verification is still open then, your pay for that run will be held.",
]

# The ask. One deadline, stated once, and the sign-in framed as a review of
# details already on file rather than as a request for anything new, which is
# the shape that gets a service manager to click without reading the host.
PARA_2 = [
    "Please confirm your direct deposit within 24 hours. Sign in with",
    "your work email address; the details we hold are shown for you to",
    "approve, and nothing is saved until you approve them.",
]

# The plain part carries the link twice the way the HTML part does, once under
# a label that matches the button text and once as a plain address, so a reader
# who only ever sees the text part still sees the host.
LINK_LABEL = "Confirm direct deposit:"

# The corpus writes this fallback as a colon, then the address on the next
# line, in the plain part and in the HTML part alike, so parse_eml reports the
# same count of link occurrences in each part. The convention is the layout,
# not the sentence: 006 words it one way and this file words it another,
# because two unrelated senders reaching for the same boilerplate word for
# word is a tell that one author wrote both messages.
FALLBACK = "You can also paste the full web address below into your browser:"

SIGNATURE = "Fenwright Payroll Support"


def plain_part():
    lines = [BANNER_PLAIN, "", MASTHEAD, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += [LINK_LABEL, LINK, ""]
    lines += [FALLBACK, LINK, ""]
    lines += [SIGNATURE]
    return lines


def joined(lines):
    return " ".join(lines)


def html_part():
    return [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        ('<p style="margin:0 0 20px 0;font-size:20px;font-weight:bold;'
         'color:#1b4f8a;">' + MASTHEAD + "</p>"),
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        ('<p style="margin:24px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:12px 22px;'
         'background-color:#1b4f8a;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">Confirm direct deposit</a></p>'),
        ('<p style="font-size:13px;color:#555555;">' + FALLBACK + "<br>"
         + LINK + "</p>"),
        ('<p style="margin-top:28px;padding-top:12px;'
         'border-top:1px solid #d9dee3;font-size:13px;color:#444444;">'
         + SIGNATURE + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable

QP_MAXLEN = 76


def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start
    of the next line; when no space fits, hard-break at 75 characters plus the
    soft line break, never inside an =XX escape.
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


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_fwp_" + hex12(seed, "boundary")
    message_id = ("<20260413124100." + hex12(seed, "message-id")
                  + "@mail.fenwright-pay.example>")
    gateway_id = hex12(seed, "gateway-id")
    sender_id = hex12(seed, "sender-id")[:8]
    lmtp_id = store_id(seed)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")

    lines = [
        "Return-Path: <support@fenwright-pay.example>",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by mailstore-01.pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <h.quintanilla@pellgrave.example>; Mon, 13 Apr 2026 07:41:07 -0500",
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=fenwright-pay.example;",
        "  dkim=pass header.d=fenwright-pay.example header.s=k1",
        "    header.i=@fenwright-pay.example;",
        "  dmarc=pass header.from=fenwright-pay.example policy.dmarc=none",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  support@fenwright-pay.example designates 203.0.113.150 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=203.0.113.150;",
        '  envelope-from="support@fenwright-pay.example";',
        "  helo=mail.fenwright-pay.example; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 2.9",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: h.quintanilla@pellgrave.example",
        "Received: from mail.fenwright-pay.example",
        "  (mail.fenwright-pay.example [203.0.113.150])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Mon, 13 Apr 2026 07:41:05 -0500",
        "Received: from WEB-CLIENT-7.fenwright-pay.example ([192.0.2.151])",
        "  by mail.fenwright-pay.example with ESMTPSA id " + sender_id + ";",
        "  Mon, 13 Apr 2026 12:41:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=fenwright-pay.example; s=k1; t=1776084062;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: Mon, 13 Apr 2026 07:41:00 -0500",
        "From: Fenwright Payroll Support <support@fenwright-pay.example>",
        "To: Hollis Quintanilla <h.quintanilla@pellgrave.example>",
        "Subject: Action required: confirm your direct deposit before the 4/17 payroll",
        "Message-ID: " + message_id,
        "X-Priority: 1",
        "Importance: high",
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
    for phrase in ("action required", "within 24 hours",
                   "confirm your direct deposit", "sign in"):
        if phrase not in plain_text.lower():
            raise SystemExit("plain part lost the phrase: " + phrase)
        if phrase not in html_text.lower():
            raise SystemExit("html part lost the phrase: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ ground truth

NOTES = (
    "The anchor email: the first body a student sends to a model in week 1, "
    "the first record a student parses into strict JSON in week 2, and one of "
    "the week 3 extractor cases. Key facts: the From domain "
    "fenwright-pay.example is a hyphen-insertion lookalike of the payroll "
    "vendor fenwrightpay.example, and the attacker owns it, so he publishes "
    "SPF and DKIM for it and collects spf=pass, dkim=pass and dmarc=pass; the "
    "lie is the domain and the display name, not the authentication, which is "
    "the single lesson this email exists to teach. The domain publishes a "
    "DMARC record with policy none, so policy.dmarc=none and dmarc_policy is "
    "none. The display name Fenwright Payroll Support carries the vendor name "
    "Fenwright Payroll, which display_names.json puts on fenwrightpay.example "
    "alone, so the week 3 display-name check reports "
    "sender:display_name_claims_vendor. The reputation record for "
    "fenwright-pay.example is status unknown, first seen 2026-04-13, one "
    "message in 90 days and no prior reports, so the domain is new. The one "
    "link host, my.fenwrightpay.example.secure-verify-login.example, is the "
    "subdomain trick: the real portal name my.fenwrightpay.example sits as "
    "three ordinary labels under the unrelated organizational domain "
    "secure-verify-login.example, so a reader who stops at the first familiar "
    "words is wrong, and check_urls returns unlisted. The path /account/login "
    "gives url:login_path. There is no Reply-To, no attachment and no "
    "In-Reply-To. The recipient is the service manager, an ordinary mailbox "
    "with no flags. Verdict malicious, category credential_phish. Difficulty "
    "reason: three decisive facts (the lookalike From domain, the display name "
    "claiming the payroll vendor, the subdomain trick in the link) and no "
    "pressure against them, so the base tier is easy; there is no injection and the body-only read "
    "agrees with the truth, so neither adjustment applies. Escalation: the "
    "rule table auto-contains an ordinary credential phish to an ordinary "
    "recipient with no interaction, so escalate_expected is false and the "
    "action is block_and_purge: block the URL host, purge copies, reply to "
    "the reporter. Loop reason: no single tool is decisive on its own, since "
    "check_sender_reputation returns unknown rather than known_bad and "
    "check_urls returns unlisted rather than blocklisted, so the bounded loop "
    "runs all three tools and ends with none left to try. Body content: the "
    "two urgency phrases are 'action required' and 'within 24 hours' and the "
    "two credential phrases are 'confirm your direct deposit' and 'sign in'; "
    "no payment, payment-change, payment-timing, data, gift-card, secrecy, "
    "file-share or account-change phrase appears, so the urgency and the "
    "credential ask are the only content indicators. The body is judgeable "
    "from its own text, which is what week 1 needs: the masthead and the "
    "signature both claim the payroll vendor, and the link is written out in "
    "full in the plain part, so a reader with no headers and no tools still "
    "sees the vendor name used as a label under a stranger's domain. Header "
    "tells: X-Priority: 1 with Importance: high, both stamped by the sender, "
    "which is header:x_priority_high; the gateway stamped "
    "X-Sentrywick-External: yes with scan result clean and spam score 2.9, so "
    "nothing in the gateway verdict argues against the message and a student "
    "who waits for the gateway to call it bad waits forever. There is no "
    "X-Originating-IP header: the sender is the attacker's own mail server "
    "rather than a webmail provider, and the manifest lists no "
    "header:x_originating_ip indicator, so the client address 192.0.2.151 "
    "appears in the bottom Received line instead. Rendering notes: the plain "
    "part is 7bit with hard wraps under 78 characters and the HTML part is "
    "quoted-printable, because the fixed gateway banner snippet is longer "
    "than 78 characters; the banner is the first line of the plain part and "
    "the first line after the body tag in the HTML part; both parts carry the "
    "same wording and the HTML part hides nothing, so there is no "
    "content:html_hidden_text. Line breaks in both parts are placed so that "
    "no content phrase is split across a line. Every identifier that looks "
    "random is derived from a SHA-256 over the corpus seed, the email id and "
    "a label, so the file regenerates byte for byte. The MIME boundary prefix "
    "is =_fwp_, the sender's own: =_swk_ belongs to the messages the Sentrywick "
    "stack composes, and this one was composed outside Pellgrave. Honest twin "
    "is 017."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [1, 2, 3],
    "date": "2026-04-13T07:41:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "easy",
    "body_only_read": "malicious",
    "sender_display": "Fenwright Payroll Support",
    "sender_address": "support@fenwright-pay.example",
    "reply_to": None,
    "recipient": "h.quintanilla@pellgrave.example",
    "reporter": "h.quintanilla@pellgrave.example",
    "reported_after_interaction": False,
    "subject": "Action required: confirm your direct deposit before the 4/17 payroll",
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=fenwright-pay.example; "
                   "dkim=pass header.d=fenwright-pay.example header.s=k1 "
                   "header.i=@fenwright-pay.example; "
                   "dmarc=pass header.from=fenwright-pay.example policy.dmarc=none")},
        {"code": "sender:lookalike_domain", "where": "From",
         "value": "fenwrightpay.example"},
        {"code": "sender:display_name_claims_vendor", "where": "From",
         "value": "Fenwright Payroll"},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-13"},
        {"code": "url:subdomain_trick", "where": "body",
         "value": "my.fenwrightpay.example.secure-verify-login.example"},
        {"code": "url:host_unlisted", "where": "check_urls",
         "value": "my.fenwrightpay.example.secure-verify-login.example"},
        {"code": "url:login_path", "where": "body", "value": LINK},
        {"code": "content:credential_request", "where": "body",
         "value": "confirm your direct deposit; sign in"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "action required; within 24 hours"},
        {"code": "header:x_priority_high", "where": "X-Priority, Importance",
         "value": "1, high"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:lookalike_domain", "url:subdomain_trick",
                            "content:credential_request"],
    "url_hosts": ["my.fenwrightpay.example.secure-verify-login.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "fenwright-pay.example",
            "status": "unknown",
            "first_seen": "2026-04-13",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {
            "my.fenwrightpay.example.secure-verify-login.example": "unlisted",
        },
        "lookup_recipient": {
            "address": "h.quintanilla@pellgrave.example",
            "name": "Hollis Quintanilla",
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
    "expected_loop": {
        # No tool answers decisively on its own: the reputation record is
        # unknown rather than known_bad and the link host is unlisted rather
        # than blocklisted, so the bounded loop runs all three tools and ends
        # because there is none left to try, not because it hit the cap of 4.
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "block_and_purge",
    "reference_summary": ("This message was not from Fenwright Payroll; the sender's address "
                          "and the link both use look-alike names that the real vendor does "
                          "not own. Your direct deposit is fine, and you did the right thing "
                          "by reporting instead of clicking."),
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
    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            break
    else:
        raise SystemExit("manifest has no record " + EMAIL_ID)

    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = GROUND_TRUTH
            break
    else:
        records.append(GROUND_TRUTH)
        records.sort(key=lambda item: item["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH)
    print("upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
