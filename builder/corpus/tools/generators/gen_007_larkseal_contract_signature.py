#!/usr/bin/env python3
"""Regenerate 007-larkseal-contract-signature.

Rebuilds emails/teaching/007-larkseal-contract-signature.eml from the corpus
seed, refreshes the matching manifest fields in spec/corpus-spec.json, upserts
the ground truth record in ground_truth.json, and applies the two data file
corrections this record depends on.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    envelope reference    = hex("reference", 16)

The DKIM b= value is the seed-derived signature this file already carried. It
is kept verbatim as a constant: it is 2048 bit synthetic signature bytes that
verify nothing (no .example domain can publish a key), it does not depend on
the body text, and the verifiers did not object to it.

Run:  python3 corpus/tools/generators/gen_007_larkseal_contract_signature.py
"""

import base64
import hashlib
import json
import os
import uuid

EMAIL_ID = "007-larkseal-contract-signature"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")
BLOCKLIST_PATH = os.path.join(CORPUS, "data", "url_blocklist.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters. The
# generator breaks at the last space that leaves the line at 72 characters or
# fewer, so the soft break lands between words wherever the text allows one,
# and falls back to a hard break at 75 characters plus the trailing "=" for
# unbroken runs such as a CSS declaration.
SOFT_MAX = 76
SPACE_MAX = 72

DKIM_B = (
    "vmrZm5GDnNAJ1uLmDb589gD6x5kWpUrdKSx74dEFZDiHL+ciufU0I4P+MTdubNeBUpuOSCM0"
    "DFyxp3sN1pAN1UyrezNFfpsQZEJk0L579ULN+lqWYsrwyuaJkaN9Fax4N35tQuqxN5aa1GDs"
    "LwH6YtXNXwfOv3TW6Urz/EVZ2ysslBWwkIaZX8VZ1A2K7VCyFZVl+SOYPkx+Sc38ovDVYlJN"
    "c8aVt4ZBfws5wh88kPZzWU3gvYzqbuvs1L8u0TTOvfJUIoONyGpSpyywsocNc2J3An/jXQhx"
    "WDp45/Qud9IXMmx3DVAIQPtLJpyeUK45aq+SkSDanSOLoF2UlDLdPA=="
)


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


# ---------------------------------------------------------------- body text

# The opening sentence carries the content:file_share_lure phrase "sent you a
# document" from the phrase list in spec/enums.json. The code is recorded with
# where=body, so the phrase has to sit in the body and not only in the Subject.
OPENING = "Adaeze Whitcombe has sent you a document to sign: Rookmere Service Agreement 2026."

# "Hello Beatrix," matches the salutation every other person-addressed external
# message in the teaching set opens with. A real signing notice greets the
# signer by name, and the attacker has the name: it is in the To display name.
SALUTATION = "Hello Beatrix,"

DETAIL = [
    "Document: Rookmere Service Agreement 2026",
    "Sent by: Adaeze Whitcombe, Chief Executive Officer, Pellgrave Mechanical Group",
]

# "expires in" is a content:urgency_keywords phrase and "sign in" is a
# content:credential_request phrase, both from spec/enums.json.
CLOSING = ("This request expires in 3 days. If the document does not open, you may need to "
           "sign in with your work email address first.")

FOOTER_TAGLINE = "Larkseal, secure signatures"
# Text only, so the message keeps exactly one link host. The wording avoids the
# content:account_change_notice phrase "if you did not".
FOOTER_NOTE = "If you were not expecting this document, contact the sender before opening it."

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;'
               'color:#5a4a00;">[External message. Sentrywick Gateway]</p>')


def link(reference):
    return "https://larkseal-docs.example/sign/request/" + reference


def plain_part(reference):
    return [
        BANNER_PLAIN,
        "",
        "Larkseal",
        "",
        SALUTATION,
        "",
        OPENING,
        "",
        DETAIL[0],
        DETAIL[1],
        "Reference: " + reference,
        "",
        "Review document: " + link(reference),
        "",
        CLOSING,
        "",
        FOOTER_TAGLINE,
        FOOTER_NOTE,
    ]


def html_part(reference):
    return [
        "<html>",
        ('<body style="margin:0;padding:0;background-color:#f2f4f6;font-family:sans-serif;'
         'font-size:15px;line-height:1.5;color:#222222;">'),
        BANNER_HTML,
        ('<div style="max-width:600px;margin:24px auto;padding:24px 32px;'
         'background-color:#ffffff;border:1px solid #d9dee3;">'),
        '<p style="margin:0 0 20px 0;font-size:20px;font-weight:bold;color:#1b4f8a;">Larkseal</p>',
        "<p>" + SALUTATION + "</p>",
        "<p>" + OPENING + "</p>",
        ('<p style="margin:0 0 16px 0;">' + DETAIL[0] + "<br>" + DETAIL[1]
         + "<br>Reference: " + reference + "</p>"),
        ('<p style="margin:24px 0;"><a href="' + link(reference) + '" '
         'style="display:inline-block;padding:12px 22px;background-color:#1b4f8a;'
         'color:#ffffff;text-decoration:none;font-weight:bold;border-radius:4px;">'
         "Review document</a></p>"),
        "<p>" + CLOSING + "</p>",
        ('<p style="margin-top:28px;padding-top:12px;border-top:1px solid #d9dee3;'
         'font-size:13px;color:#444444;">' + FOOTER_TAGLINE + "<br>" + FOOTER_NOTE + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


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


def build_eml(seed):
    reference = hexid(seed, "reference", 16)
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = "<20260415151200." + hexid(seed, "message-id") + "@app-01.larkseal-docs.example>"
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)

    lines = [
        "Return-Path: <no-reply@larkseal-docs.example>",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by mailstore-01.pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <b.onwuka@pellgrave.example>; Wed, 15 Apr 2026 10:12:08 -0500",
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=larkseal-docs.example;",
        "  dkim=pass header.d=larkseal-docs.example header.s=k1",
        "    header.i=@larkseal-docs.example;",
        "  dmarc=pass header.from=larkseal-docs.example policy.dmarc=none",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  no-reply@larkseal-docs.example designates 203.0.113.152 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=203.0.113.152;",
        '  envelope-from="no-reply@larkseal-docs.example";',
        "  helo=mail.larkseal-docs.example; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: suspect",
        "X-Sentrywick-Spam-Score: 5.2",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: b.onwuka@pellgrave.example",
        "Received: from mail.larkseal-docs.example",
        "  (mail.larkseal-docs.example [203.0.113.152])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Wed, 15 Apr 2026 10:12:06 -0500",
        "Received: from app-01.larkseal-docs.example ([192.0.2.153])",
        "  by mail.larkseal-docs.example with ESMTPSA id " + sender_id + ";",
        "  Wed, 15 Apr 2026 15:12:03 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=larkseal-docs.example; s=k1; t=1776265923;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash(seed) + ";",
    ]
    signature = [DKIM_B[i:i + 72] for i in range(0, len(DKIM_B), 72)]
    lines.append("  b=" + signature[0])
    for chunk in signature[1:]:
        lines.append("   " + chunk)
    lines += [
        "Date: Wed, 15 Apr 2026 10:12:00 -0500",
        "From: Larkseal <no-reply@larkseal-docs.example>",
        "To: Beatrix Onwuka <b.onwuka@pellgrave.example>",
        "Subject: Adaeze Whitcombe sent you a document to sign:",
        " Rookmere Service Agreement 2026",
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(plain_part(reference))
    lines += [
        "",
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part(reference))
    lines += ["", "--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 998:
            raise SystemExit("line over 998 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

def body_brief(reference):
    return (
        "Imitate a Larkseal signing request. Brand line 'Larkseal', then the salutation "
        "'Hello Beatrix,' on the line after it, the way every other person-addressed "
        "external message in the teaching set opens. First sentence: 'Adaeze Whitcombe "
        "has sent you a document to sign: Rookmere Service Agreement 2026.' so the body "
        "itself carries the content:file_share_lure phrase 'sent you a document' and not "
        "only the Subject. Detail block of Document, Sent by, and 'Reference: "
        + reference + "', the 16 hex character envelope identifier a signing platform "
        "issues, derived from the corpus seed as sha256(seed|id|reference) truncated to "
        "16. One button 'Review document' to https://larkseal-docs.example/sign/request/"
        + reference + ", the only link in either part. Add a line that the request "
        "expires in 3 days and that the recipient may need to sign in with her work "
        "email address; use the phrases 'expires in' and 'sign in'. Footer imitates the "
        "vendor's ('Larkseal, secure signatures') and adds one text-only line, 'If you "
        "were not expecting this document, contact the sender before opening it.', which "
        "is the reassurance a real signing notice carries. No unsubscribe, no second "
        "link host, and no wording from the content:account_change_notice phrase list."
    )


LURE_SUMMARY = (
    "Imitates the e-signature service the company uses and says the CEO has sent the "
    "executive assistant a contract to sign. The review button leads to a lookalike host "
    "that is already on the local blocklist from a report last month."
)

MANIFEST_NOTES = (
    "Week 5 short loop: the first tool (reputation known_bad, two March reports) is "
    "decisive, so the loop stops after one call; a loop that goes on to check_urls learns "
    "the same thing and wastes a step. Escalates because the recipient carries the "
    "executive flag as the CEO's assistant. Escalation reasons: executive_target. "
    "Campaign framing for the instructor: this is a commodity fake-esign campaign, not a "
    "timed executive impersonation. The domain was first seen 12 March with three "
    "messages in 90 days and two prior reports closed malicious, so the lure does not "
    "depend on the CEO being out of the office and lands on a Wednesday when she is in "
    "it. The CEO's name is authority decoration on a credential phish, which is what "
    "separates 007 from 009, 029 and 030; those three do depend on the 20 to 23 April "
    "conference absence."
)

GT_NOTES = (
    "Attacker-owned added-word lookalike of the electronic signature vendor. "
    "larkseal-docs.example publishes its own SPF record (mx -all), signs with selector k1 "
    "and publishes a DMARC record with policy none, so spf, dkim and dmarc all pass for "
    "the domain the message names. The passes prove only that the attacker owns "
    "larkseal-docs.example, which is why auth:all_pass counts for nothing in the tier "
    "rule. The display name Larkseal claims the vendor whose real domain is "
    "larkseal.example, and the notice imitates that vendor's signing request so the CEO "
    "appears to have sent her own assistant a customer contract. Key facts: from_domain "
    "larkseal-docs.example; reply_to none; spf pass; dkim pass; dmarc pass (policy none); "
    "url_hosts larkseal-docs.example, one link that appears once in each body part; no "
    "attachment; no In-Reply-To. Playbook rules 2 and 7: a vendor's name over a domain "
    "the vendor does not own is impersonation, and a blocklisted link host is malicious. "
    "Difficulty easy: four decisive malicious facts (sender:lookalike_domain, "
    "sender:display_name_claims_vendor, sender:known_bad, url:host_blocklisted), no "
    "pressure toward benign, no injection, and no body-only reversal. The three content "
    "codes are recorded because the phrase lists in spec/enums.json match the rendered "
    "body ('sent you a document', 'expires in', 'sign in'), and all three carry polarity "
    "PB, which the tier rule counts only for a benign verdict, so they leave the count at "
    "decisive 4 and pressure 0. No url:login_path: the only link is "
    "https://larkseal-docs.example/sign/request/<reference> with the anchor text 'Review "
    "document', where 'sign' is the electronic signature verb and neither the path nor "
    "the link text asks anyone to log in. The sign-in ask lives in the prose and is "
    "carried by content:credential_request. body_only_read is uncertain because the body "
    "alone is an ordinary signing notice: it names a real customer agreement and asks for "
    "nothing but a click, so nothing in the prose decides the case and every decisive "
    "fact comes from a tool or a header. Week 5 loop: check_sender_reputation returns "
    "known_bad at domain level, first seen 2026-03-12, two prior reports, last report "
    "malicious on 2026-03-19, campaign tag fake-esign-share, which is decisive on the "
    "first call, so the loop stops after one step with stop_reason decisive_malicious. A "
    "loop that goes on to check_urls learns the same thing from the blocklist and spends "
    "a step for nothing, which is the shortest path in the week 5 set and the contrast "
    "case for 012, where no tool is decisive and the run hits the cap of 4. Escalates "
    "under executive_target: b.onwuka carries the executive flag as the assistant to the "
    "CEO, and three of her four prior reports were true positives tagged "
    "ceo-impersonation, so the SOC treats a lure that borrows the CEO's name to her "
    "mailbox as a campaign rather than a single message. Timing, for the instructor who "
    "asks why a CEO-name lure lands on Wednesday 15 April while Adaeze Whitcombe is in "
    "the office: this is a commodity fake-esign campaign and not a timed executive "
    "impersonation. The sending domain was first seen 12 March, carries three messages in "
    "90 days and two reports already closed malicious, and the ask is a click on a "
    "signing link rather than anything only an absent executive could authorize, so the "
    "CEO's name is authority decoration on a credential phish. That is what separates it "
    "from 009, 029 and 030, which do depend on the 20 to 23 April conference absence. "
    "Deliberate omissions, matching the manifest indicator list: no Reply-To, no "
    "X-Priority, no Auto-Submitted, no X-Originating-IP, and no unsubscribe line, since a "
    "signing request is transactional mail."
)

MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:lookalike_domain:larkseal.example",
    "sender:display_name_claims_vendor:Larkseal",
    "sender:known_bad",
    "url:host_blocklisted:larkseal-docs.example",
    "content:credential_request",
    "content:urgency_keywords",
    "content:file_share_lure",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
    "recipient:executive",
]

GT_INDICATORS = [
    {"code": "auth:all_pass", "where": "Authentication-Results",
     "value": ("spf=pass smtp.mailfrom=larkseal-docs.example; dkim=pass "
               "header.d=larkseal-docs.example header.s=k1 "
               "header.i=@larkseal-docs.example; dmarc=pass "
               "header.from=larkseal-docs.example policy.dmarc=none")},
    {"code": "sender:lookalike_domain", "where": "From", "value": "larkseal.example"},
    {"code": "sender:display_name_claims_vendor", "where": "From", "value": "Larkseal"},
    {"code": "sender:known_bad", "where": "check_sender_reputation",
     "value": "larkseal-docs.example"},
    {"code": "url:host_blocklisted", "where": "check_urls", "value": "larkseal-docs.example"},
    {"code": "content:credential_request", "where": "body", "value": "sign in"},
    {"code": "content:urgency_keywords", "where": "body", "value": "expires in"},
    {"code": "content:file_share_lure", "where": "body", "value": "sent you a document"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
    {"code": "recipient:executive", "where": "lookup_recipient",
     "value": "b.onwuka@pellgrave.example"},
]

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [5],
    "date": "2026-04-15T10:12:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "easy",
    "body_only_read": "uncertain",
    "sender_display": "Larkseal",
    "sender_address": "no-reply@larkseal-docs.example",
    "reply_to": None,
    "recipient": "b.onwuka@pellgrave.example",
    "reporter": "b.onwuka@pellgrave.example",
    "reported_after_interaction": False,
    "subject": "Adaeze Whitcombe sent you a document to sign: Rookmere Service Agreement 2026",
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["url:host_blocklisted", "sender:lookalike_domain"],
    "url_hosts": ["larkseal-docs.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "larkseal-docs.example",
            "status": "known_bad",
            "first_seen": "2026-03-12",
            "messages_90d": 3,
            "prior_reports": 2,
            "last_report_verdict": "malicious",
            "last_report_date": "2026-03-19",
            "campaign_tag": "fake-esign-share",
            "new_domain": False,
            "notes": "Domain and host blocklisted after two reports in March.",
            "match_level": "domain",
        },
        "check_urls": {"larkseal-docs.example": "blocklisted"},
        "lookup_recipient": {
            "address": "b.onwuka@pellgrave.example",
            "name": "Beatrix Onwuka",
            "role": "Executive Assistant to the CEO",
            "mailbox_type": "person",
            "executive": True,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 4,
            "true_positive_count_90d": 3,
            "campaign_tags": ["ceo-impersonation", "marketing"],
        },
    },
    "expected_loop": {"tools": ["check_sender_reputation"], "stop_reason": "decisive_malicious"},
    "escalate_expected": True,
    "escalation_reasons": ["executive_target"],
    "recommended_action": "escalate_incident",
    "reference_summary": ("This signing request is fake: it comes from a look-alike of "
                          "Larkseal's address and the link goes to a site we already block. "
                          "Adaeze did not send you a contract, and we are looking into it "
                          "because you support the CEO."),
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": GT_NOTES,
}


# ------------------------------------------------------------- data fixes

# url_blocklist.json credited the March reports on larkseal-docs.example to
# b.onwuka, but her record in recipients.json holds no report on or near
# 2026-03-19 and no fake-esign-share tag. sender_reputation.json says the
# domain carries two prior reports, so the reason now states that and names no
# mailbox.
BLOCK_HOST = "larkseal-docs.example"
BLOCK_REASON_OLD = "Fake e-signature share notices; reported by b.onwuka"
BLOCK_REASON_NEW = "Fake e-signature share notices; two reports closed malicious in March"

# Her first prior report sat 105 days before the corpus clock of 2026-04-29,
# outside the 90 day window the field name asserts, while report_count_90d
# counted it. Moving it inside the window keeps the counts at 4 and 3, which is
# what phase0-corpus-design.md section 2.2 and this record's notes both state.
RECIPIENT_ADDRESS = "b.onwuka@pellgrave.example"
REPORT_DATE_OLD = "2026-01-14"
REPORT_DATE_NEW = "2026-02-03"
REPORT_REF_OLD = "<20260114010300.7b4be2930bb5@mail.pellgrave.example>"
REPORT_REF_NEW = "<20260203010300.7b4be2930bb5@mail.pellgrave.example>"


def fix_blocklist():
    with open(BLOCKLIST_PATH, encoding="utf-8") as handle:
        blocklist = json.load(handle)
    for host in blocklist["hosts"]:
        if host["host"] == BLOCK_HOST:
            if host["reason"] not in (BLOCK_REASON_OLD, BLOCK_REASON_NEW):
                raise SystemExit("url_blocklist.json reason for " + BLOCK_HOST + " is unexpected")
            host["reason"] = BLOCK_REASON_NEW
            break
    else:
        raise SystemExit("url_blocklist.json has no host " + BLOCK_HOST)
    write_json(BLOCKLIST_PATH, blocklist)


def fix_recipients():
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] != RECIPIENT_ADDRESS:
            continue
        first = record["prior_reports"][0]
        if first["date"] not in (REPORT_DATE_OLD, REPORT_DATE_NEW):
            raise SystemExit("recipients.json first prior report for " + RECIPIENT_ADDRESS
                             + " is unexpected")
        first["date"] = REPORT_DATE_NEW
        first["message_ref"] = REPORT_REF_NEW
        dates = [report["date"] for report in record["prior_reports"]]
        if dates != sorted(dates):
            raise SystemExit("recipients.json prior reports for " + RECIPIENT_ADDRESS
                             + " are out of order")
        if record["report_count_90d"] != len(record["prior_reports"]):
            raise SystemExit("recipients.json report_count_90d disagrees with the list")
        break
    else:
        raise SystemExit("recipients.json has no recipient " + RECIPIENT_ADDRESS)
    write_json(RECIPIENTS_PATH, recipients)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]
    reference = hexid(seed, "reference", 16)

    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            record["indicators"] = list(MANIFEST_INDICATORS)
            record["body_brief"] = body_brief(reference)
            record["lure_summary"] = LURE_SUMMARY
            record["notes"] = MANIFEST_NOTES
            break
    else:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    for index, record in enumerate(records):
        if record["id"] == EMAIL_ID:
            records[index] = GROUND_TRUTH
            break
    else:
        records.append(GROUND_TRUTH)
        records.sort(key=lambda record: record["id"])
    write_json(GT_PATH, truth)

    fix_blocklist()
    fix_recipients()

    print("wrote " + EML_PATH)
    print("updated manifest, ground truth, url_blocklist.json and recipients.json for "
          + EMAIL_ID)


if __name__ == "__main__":
    main()
