#!/usr/bin/env python3
"""Regenerate 010-ferncrate-rfq-share.

Rebuilds emails/teaching/010-ferncrate-rfq-share.eml byte for byte from the
corpus seed and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_swk_" + hex("mime-boundary", 12)
    gateway Received id   = hex("gateway-message-uid", 12), also
                            X-Sentrywick-Message-UID
    relay Received id     = hex("relay-smtp-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-lmtp-id)[:32], version=4)

Every identifier in the file is derived; none is pinned as a literal. The
label strings this file keys on are not the ones 001, 002, 011 and 012 use
("boundary", "gateway-id", "sender-id", "store-id"). The four labels above are
the ones that reproduce the committed bytes, so they stay as they are: the
point of this script is that the file regenerates rather than that the label
vocabulary is uniform, and renaming a label would change five identifiers in
an approved file for no reader-visible gain.

Two values in the file are pinned from the manifest rather than derived,
because spec/corpus-spec.json fixes them and the ground truth quotes them:
the download URL https://dl.quickdrop-files.example/get/rfq-q2-88213.zip,
written out in the manifest body_brief and in the url:archive_download
indicator, and the Subject. The script reads the manifest and fails if either
has drifted.

The Message-ID right side is api-node-05.cheapsend-relay.example, the
originating host at the bottom of the Received chain, which is the section 1
convention in docs/email-header-realism.md. The relay provider appears only in
the Received lines, the helo value and the Message-ID host, never as a From,
Reply-To, Return-Path or link domain.

Quoted-printable: the HTML part is written as source lines and each escaped
line is folded by a hard break at 75 characters plus the soft line break,
never inside an =XX escape. That is not the space-preferring fold 012 uses,
and it is what this file was rendered with: the two folded lines break mid
token, at column 76 counting the trailing "=". RFC 2045 sec. 6.7 allows a soft
break at any point, and the decoded part is identical either way, so the fold
rule is the one that reproduces the bytes.

The delivering store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox
rather than of the path the message arrived on. Emeric Dawodu is both the
recipient and the reporter here, so the hop, the To address and
X-Sentrywick-Reported-By all name the same mailbox.

Run:  python3 corpus/tools/generators/gen_010_ferncrate_rfq_share.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "010-ferncrate-rfq-share"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

# The From domain is an added-word lookalike of the file-sharing vendor's real
# domain, ferncrate.example in data/display_names.json and in
# data/sender_reputation.json. The display name is the vendor's, which is what
# sender:display_name_claims_vendor keys on; the domain under it is not.
SENDER = "notify@ferncrate-files.example"
SENDER_DISPLAY = "Ferncrate"
LOOKALIKE_OF = "ferncrate.example"
RECIPIENT = "e.dawodu@pellgrave.example"
RECIPIENT_DISPLAY = "Emeric Dawodu"
REPORTER = RECIPIENT

SUBJECT = "Emeric, a file was shared with you: RFQ_Response_Q2.zip"

# The payload host. data/url_blocklist.json records it as added 2026-03-19
# after an earlier file-share lure, which is what check_urls answers and what
# url:host_blocklisted keys on.
LINK = "https://dl.quickdrop-files.example/get/rfq-q2-88213.zip"
LINK_HOST = "dl.quickdrop-files.example"

# The relay the message actually entered on, and the node that stamped the
# Message-ID. Both are the bulk sending provider, never a From or link domain.
RELAY_HOST = "mta-3.cheapsend-relay.example"
RELAY_IP = "198.51.100.140"
ORIGIN_HOST = "api-node-05.cheapsend-relay.example"
ORIGIN_IP = "192.0.2.97"

# The gateway banner, byte for byte from section 2 of
# docs/email-header-realism.md. One product stamps one snippet, so the markup
# never varies between files and nothing is ever folded inside the banner.
BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-lmtp-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient):
    """The mailbox this file was pulled from and the one store that holds it.

    The recipient is a person, so the message is delivered to that mailbox
    itself and the LMTP hop names the store recipients.json gives it. No
    expansion happens here, unlike the list case in 002.
    """
    entry = recipient_record(recipient)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


# ---------------------------------------------------------------- body text
#
# The whole body imitates a file-sharing vendor's share notice, which is the
# lure: a supplier has left the procurement specialist a quote response, and
# the one button in the message leads to an archive on a blocked download
# host. The body carries no verdict of its own, and that is deliberate. This
# is the week 5 email whose body_only_read is uncertain: read alone it is an
# ordinary share notice, and only check_sender_reputation and check_urls
# settle it. Anything in the wording that leaned malicious would hand a small
# model the answer the tool loop is supposed to earn.
#
# Wording rules from spec/enums.json content_phrases. The record carries
# content:file_share_lure and nothing else, so "shared with you" and
# "download" are required and every other list stays out:
#
#   No urgency keyword. The 48 hour line is the vendor's own expiry sentence,
#   written as a statement of how long the link is good for rather than as a
#   countdown, and no phrase from content:urgency_keywords appears.
#   No "sign in", "log in", "password" or "credentials": a share notice that
#   asked for any of them would carry content:credential_request as well, and
#   the loop would stop on the sender instead of on the URL.
#   Nothing from content:payment_change, content:secrecy_request,
#   content:data_request, content:account_change_notice,
#   content:phone_verification_offered or
#   content:excuse_for_external_address appears.
#
# The note supposedly left with the file names Slatemoor Industrial Supply, a
# real supplier in the corpus, and a Q2 request for quote, so the pretext
# lands on the procurement specialist's actual work. No number, account or
# quote reference is invented that a data file would have to back.

HEADLINE = [
    "Slatemoor Industrial Supply shared RFQ_Response_Q2.zip with",
    "you.",
]

GREETING = "Hello Emeric,"

PARA_1 = [
    "A file has been shared with you through Ferncrate. The note left",
    'with the file reads: "Response to your Q2 request for quote. Parts',
    'list and lead times are in the folder."',
]

# The vendor's detail block. Each entry is its own line in the plain part and
# its own <br> row in the HTML part, so the two parts carry the same rows.
DETAILS = [
    ["File name: RFQ_Response_Q2.zip"],
    ["File size: 4.2 MB"],
    ["Shared on: 16 April 2026"],
]

PARA_2 = [
    "The share link is good for 48 hours from the time it was sent.",
    "After that, the sender has to share the file again.",
]

# The imitated vendor footer. The last block runs to two lines, which is why
# the footer is written as blocks rather than as flat lines: the <br> goes
# between blocks, not between the wrapped lines inside one.
FOOTER = [
    ["Ferncrate"],
    ["File sharing for business teams"],
    ["You received this message because a file was shared with your",
     "address."],
]

FOOTER_OPEN = [
    '<p style="margin-top:28px;padding-top:12px;border-top:1px solid',
    '  #d9dee3;font-size:12px;color:#6b6b6b;">',
]


def joined(lines):
    return " ".join(lines)


def flatten(blocks):
    out = []
    for block in blocks:
        out += block
    return out


def plain_part():
    lines = [BANNER_PLAIN, "", joined(HEADLINE), "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += flatten(DETAILS) + [""]
    lines += ["Download file: " + LINK, ""]
    lines += PARA_2 + [""]
    lines += flatten(FOOTER)
    return lines


def paragraph_html(lines, open_tag="<p>", close_tag="</p>"):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = open_tag + block[0]
    block[-1] = block[-1] + close_tag
    return block


def br_block(blocks, open_tag, close_tag):
    """Blocks joined by <br>, one <br> between blocks and none inside one."""
    out = []
    for index, block in enumerate(blocks):
        rows = list(block)
        if index < len(blocks) - 1:
            rows[-1] = rows[-1] + "<br>"
        out += rows
    out[0] = open_tag + out[0]
    out[-1] = out[-1] + close_tag
    return out


def html_part():
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f4f5f7;">',
        BANNER_HTML,
        '<div style="max-width:600px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#222222;">',
        '<p style="margin:0 0 18px 0;font-size:18px;font-weight:bold;',
        '  color:#1f6f6b;">Ferncrate</p>',
    ]
    lines += paragraph_html(HEADLINE)
    lines += ["<p>" + GREETING + "</p>"]
    lines += paragraph_html(PARA_1)
    lines += br_block(DETAILS, "<p>", "</p>")
    # The href and the button text are the same link. The visible text says
    # only "Download file", so the plain part is where the address shows in
    # full, which is why the plain part writes it out on its own line.
    lines += [
        '<p style="margin:24px 0;"><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#1f6f6b;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >Download file</a></p>",
    ]
    lines += paragraph_html(PARA_2)
    lines += FOOTER_OPEN[:-1]
    lines += br_block(FOOTER, FOOTER_OPEN[-1], "</p>")
    lines += ["</div>", "</body>", "</html>"]
    return lines


# ------------------------------------------------------- quoted-printable

QP_MAXLEN = 76


def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Hard break at 75 characters plus the soft line break, so a folded physical
    line is 76 characters including the trailing "=", the RFC 2045 sec. 6.7
    limit. The break steps back rather than land on or inside an =XX escape.
    """
    out = []
    rest = line
    while len(rest) > QP_MAXLEN:
        cut = QP_MAXLEN - 1
        while rest[cut - 1:cut] == "=" or rest[cut - 2:cut - 1] == "=":
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
    boundary = "=_swk_" + hexid(seed, "mime-boundary")
    message_id = ("<20260416164000." + hexid(seed, "message-id")
                  + "@" + ORIGIN_HOST + ">")
    gateway_id = hexid(seed, "gateway-message-uid")
    relay_id = hexid(seed, "relay-smtp-id", 8)
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT)

    lines = [
        "Return-Path: <" + SENDER + ">",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; Thu, 16 Apr 2026 11:40:08 -0500",
        # ferncrate-files.example publishes an SPF record ending ~all and the
        # relay is outside it, so the gateway writes softfail rather than
        # fail. No signature, so dkim=none. The domain publishes no DMARC
        # record, so dmarc=none and no policy.dmarc is written.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=softfail smtp.mailfrom=ferncrate-files.example;",
        "  dkim=none;",
        "  dmarc=none header.from=ferncrate-files.example",
        "Received-SPF: softfail (mx.pellgrave.example: domain of transitioning",
        "  notify@ferncrate-files.example does not designate " + RELAY_IP + " as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=" + RELAY_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=~all",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: suspect",
        "X-Sentrywick-Spam-Score: 6.4",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Thu, 16 Apr 2026 11:40:06 -0500",
        # The sending side stamps in UTC, which is 11:40:02 local.
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + RELAY_HOST + " with ESMTP id " + relay_id + ";",
        "  Thu, 16 Apr 2026 16:40:02 +0000",
        "Date: Thu, 16 Apr 2026 11:40:00 -0500",
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
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if plain_text.count(LINK) != 1 or html_text.count(LINK) != 1:
        raise SystemExit("the one link must appear once in each part")
    return "\r\n".join(lines).encode("ascii")


NOTES = (
    "The week 5 two-step loop, and the teaching set's link-delivered malware "
    "case. A share notice imitating the file-sharing vendor tells the "
    "procurement specialist that a parts supplier has left him a quote "
    "response, and the one button in the message leads to an archive on a "
    "download host the SOC blocked on 2026-03-19. Key facts: the From domain "
    "is ferncrate-files.example, an added-word lookalike of the vendor's real "
    "domain ferncrate.example, under the display name Ferncrate; no Reply-To; "
    "the message entered through mta-3.cheapsend-relay.example "
    "(198.51.100.140), a relay outside the lookalike domain's SPF record (mx "
    "~all), so spf=softfail; no signature, so dkim=none; "
    "ferncrate-files.example publishes no DMARC record, so dmarc=none with no "
    "policy.dmarc and dmarc_policy null; scan result suspect, spam score 6.4; "
    "one link host, dl.quickdrop-files.example; no removed file, because the "
    "payload sits behind the link; a new thread. Message-ID names "
    "api-node-05.cheapsend-relay.example, the originating host at the bottom "
    "of the Received chain, following the header specification convention; "
    "the relay provider appears only in the Received lines, the helo value "
    "and the Message-ID host, never as a From, Reply-To, Return-Path or link "
    "domain, the same treatment records 025 and 032 give it. Both body parts "
    "open with the gateway's canonical banner, [External message. Sentrywick "
    "Gateway]; the plain part is 7bit because every line fits in 78 "
    "characters, and the HTML part is quoted-printable because the banner "
    "snippet runs past that. Difficulty easy: three decisive malicious facts "
    "(sender:lookalike_domain, sender:display_name_claims_vendor, "
    "url:host_blocklisted), no pressure toward benign, no injection, and no "
    "misleading body. The body carries no verdict of its own, which is why "
    "body_only_read is uncertain: read alone it is an ordinary share notice, "
    "and only the tool results settle it. That is the point of the email in "
    "week 5. The loop runs check_sender_reputation first and learns only that "
    "ferncrate-files.example is unknown and first seen 2026-04-16, inside the "
    "window and thirteen days before the corpus clock, so new_domain is true; "
    "nothing decisive yet, and a link is present, so the second step is "
    "check_urls, which returns blocklisted for dl.quickdrop-files.example and "
    "stops the loop on decisive_malicious after two calls. lookup_recipient "
    "is never needed, and calling it would waste a step: Emeric Dawodu "
    "carries no flag, and his single prior report is tagged vendor-notice, "
    "which the prior_similar_report_rule does not imply from a file-share "
    "lure, so recipient:prior_similar_report is absent. Escalates under "
    "financial_or_endpoint_impact: malware delivery always sends the case to "
    "a human, who checks the proxy log for anyone who followed the link. "
    "Deliberate omissions, matching the manifest indicator list: no "
    "DKIM-Signature (dkim=none), no X-Originating-IP, no X-Mailer, no "
    "Auto-Submitted, no X-Priority, no attachment header and no removal "
    "notice, since nothing was removed."
)

REFERENCE_SUMMARY = (
    "This share notice is fake and the download link leads to a site that has "
    "spread malware before. Do not download anything from it; our team is "
    "checking that nobody else clicked."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [5],
    "date": "2026-04-16T11:40:00-05:00",
    "verdict": "malicious",
    "category": "malware_delivery",
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
    "auth": {"spf": "softfail", "dkim": "none", "dmarc": "none",
             "dmarc_policy": None},
    "indicators": [
        {"code": "auth:spf_softfail", "where": "Authentication-Results",
         "value": "spf=softfail smtp.mailfrom=ferncrate-files.example"},
        {"code": "auth:dkim_none", "where": "Authentication-Results",
         "value": "dkim=none"},
        {"code": "auth:dmarc_none", "where": "Authentication-Results",
         "value": "dmarc=none header.from=ferncrate-files.example"},
        {"code": "sender:lookalike_domain", "where": "From",
         "value": LOOKALIKE_OF},
        {"code": "sender:display_name_claims_vendor", "where": "From",
         "value": SENDER_DISPLAY},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-16"},
        {"code": "url:host_blocklisted", "where": "check_urls",
         "value": LINK_HOST},
        {"code": "url:archive_download", "where": "body", "value": LINK},
        {"code": "content:file_share_lure", "where": "body",
         "value": "shared with you; download file"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["url:host_blocklisted", "sender:lookalike_domain"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "ferncrate-files.example",
            "status": "unknown",
            "first_seen": "2026-04-16",
            "messages_90d": 1,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "blocklisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
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
    "expected_loop": {"tools": ["check_sender_reputation", "check_urls"],
                      "stop_reason": "decisive_malicious"},
    "escalate_expected": True,
    "escalation_reasons": ["financial_or_endpoint_impact"],
    "recommended_action": "escalate_incident",
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
    if LINK not in record["body_brief"]:
        raise SystemExit("the manifest body_brief no longer names " + LINK)
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("manifest url_hosts is " + repr(record["url_hosts"]))

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
    decoded_html = parsed.get_payload(1).get_content()
    if BANNER_HTML not in decoded_html:
        raise SystemExit("the decoded HTML part lost the gateway banner")

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
