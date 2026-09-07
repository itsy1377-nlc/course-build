#!/usr/bin/env python3
"""Regenerate 012-elmhollow-badge-access.

Rebuilds emails/teaching/012-elmhollow-badge-access.eml byte for byte from the
corpus seed, refreshes the matching manifest fields in spec/corpus-spec.json,
and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    sender Received id    = hex12("sender-id")[:8]
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh               = base64(stream("dkim-bh")[:32])
    DKIM b                = base64(stream("dkim-b")[:256])
    stream(label)         = sha256("<seed>|<id>|<label>|<n>") for n = 0, 1, 2 ...

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab checks a signature.

Run:  python3 corpus/tools/generators/gen_012_elmhollow_badge_access.py
"""

import base64
import hashlib
import json
import os
import uuid

EMAIL_ID = "012-elmhollow-badge-access"
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
# Line breaks are placed so that no content:data_request phrase from
# spec/enums.json is split across a line: "badge access list",
# "confirm which technicians", "send me the names" and
# "names and truck numbers" each sit whole on one line.

GREETING = "Hello Hollis,"

# The bare quote number is the checkable reference a service manager matches
# against his own schedule, the way 005 cites account 44170 and 011 cites
# PO 20431. No data file records jobs or quotes, so nothing looks it up.
#
# Two sentences, not one. A single "badges for X, your quote Y, and our
# security office wants Z" reads as a three-item list until the verb arrives,
# so the quote number moves into a parenthesis and the ask starts its own
# sentence. Dates are written the way an American facilities coordinator
# writes them, month before day, the same register 003 and 005 use.
PARA_1 = [
    "Elmhollow is issuing contractor badges for the summer chiller",
    "replacement (your quote 4712). Our security office wants the",
    "badge access list from every contractor on file before the crew",
    "starts on May 5.",
]

# One office, then "we". A community with a single Facilities Coordinator does
# not run a security office and a badge office as separate bodies; naming both
# inflates the organization and reads assembled rather than typed. The front
# desk stays, because it is a place a badge is picked up rather than a third
# department.
PARA_2 = [
    "Could you confirm which technicians from Pellgrave will be on the",
    "campus for that job? We need a first and last name for each one,",
    "plus the truck number the technician drives, so the gate log and",
    "the badge agree. Please send me the names and truck numbers by",
    "Thursday, April 23 and the badges will be printed and waiting at",
    "the front desk.",
]

# "easiest" is the word a facilities coordinator writes to a contractor.
PARA_3 = [
    "Our vendor portal is the easiest way to do it. Open the contractor",
    "page, pick Pellgrave Mechanical Group from the company list, and add a",
    "row for each technician",
]

LINK = "https://vendors.elmhollow-living.example/contractors"

# One sentence, and one statement about timing in the whole message: the
# deadline in PARA_2. The message must not argue its own innocence, because
# 012 is the week 5 no-decisive-result case and one of the two week 6
# low-confidence cases; a body that disclaims urgency hands a 3B model a
# confident benign read that the escalation threshold is built to withhold.
PARA_4 = [
    "A reply to this message with the same details is just as good if the",
    "portal gives you trouble.",
]

CLOSING = "Thank you,"

# The house block for an external human signer, the shape 005 uses: name,
# role, organization, a dialable number. A bare internal extension is what
# internal senders sign with; an outside recipient cannot dial one, and a
# first-contact customer message whose authored action is
# verify_out_of_band_then_close has to leave a channel to verify on.
# 555-0163 is unused elsewhere in the corpus.
SIGNATURE = [
    "Dolores Achebe-Ferrante",
    "Facilities Coordinator",
    "Elmhollow Senior Living",
    "555-0163",
]

# Phrases the week 3 extractor keys on. The generator proves they survive the
# line breaks in both parts.
DATA_REQUEST_PHRASES = [
    "badge access list",
    "confirm which technicians",
    "send me the names",
    "names and truck numbers",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += PARA_3[:-1] + [PARA_3[-1] + ":"] + [""]
    lines += [LINK, ""]
    lines += PARA_4 + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE
    return lines


def html_part():
    return [
        "<html>",
        '<body style="margin:0;padding:0;background-color:#f4f5f7;">',
        BANNER_HTML,
        ('<div style="max-width:620px;margin:20px auto;padding:22px 26px;'
         'background-color:#ffffff;border:1px solid #dcdfe3;'
         'font-family:sans-serif;font-size:15px;line-height:1.5;'
         'color:#212121;">'),
        ('<p style="margin:0 0 18px 0;font-size:18px;font-weight:bold;'
         'color:#2f5d50;">Elmhollow Senior Living</p>'),
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        "<p>" + joined(PARA_3) + ".</p>",
        ('<p style="margin:22px 0;"><a href="' + LINK + '" '
         'style="display:inline-block;padding:11px 20px;'
         'background-color:#2f5d50;color:#ffffff;text-decoration:none;'
         'font-weight:bold;border-radius:4px;">Open the contractor page</a>'
         '</p>'),
        ('<p style="font-size:13px;color:#555555;">If the button does not '
         'open, the address is ' + LINK + "</p>"),
        "<p>" + joined(PARA_4) + "</p>",
        "<p>" + CLOSING + "</p>",
        "<p>" + "<br>".join(SIGNATURE) + "</p>",
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
    boundary = "=_swk_" + hex12(seed, "boundary")
    message_id = "<20260417145500." + hex12(seed, "message-id") + "@mail.elmhollow-living.example>"
    gateway_id = hex12(seed, "gateway-id")
    sender_id = hex12(seed, "sender-id")[:8]
    lmtp_id = store_id(seed)
    body_hash = base64.b64encode(stream(seed, "dkim-bh", 32)).decode("ascii")
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")

    lines = [
        "Return-Path: <facilities@elmhollow-living.example>",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by mailstore-01.pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <h.quintanilla@pellgrave.example>; Fri, 17 Apr 2026 09:55:07 -0500",
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=elmhollow-living.example;",
        "  dkim=pass header.d=elmhollow-living.example header.s=eh1",
        "    header.i=@elmhollow-living.example;",
        "  dmarc=pass header.from=elmhollow-living.example policy.dmarc=none",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  facilities@elmhollow-living.example designates 203.0.113.101 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=203.0.113.101;",
        '  envelope-from="facilities@elmhollow-living.example";',
        "  helo=mail.elmhollow-living.example; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 2.6",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: h.quintanilla@pellgrave.example",
        "Received: from mail.elmhollow-living.example",
        "  (mail.elmhollow-living.example [203.0.113.101])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Fri, 17 Apr 2026 09:55:05 -0500",
        "Received: from EH-FAC-0117.elmhollow-living.example ([192.0.2.201])",
        "  by mail.elmhollow-living.example with ESMTPSA id " + sender_id + ";",
        "  Fri, 17 Apr 2026 14:55:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=elmhollow-living.example; s=eh1; t=1776437702;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: Fri, 17 Apr 2026 09:55:00 -0500",
        "From: Elmhollow Senior Living Facilities <facilities@elmhollow-living.example>",
        "To: Hollis Quintanilla <h.quintanilla@pellgrave.example>",
        "Subject: Badge access list for your technicians: confirm by Thursday",
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
    for phrase in DATA_REQUEST_PHRASES:
        if phrase not in plain_text:
            raise SystemExit("plain part lost the phrase: " + phrase)
        if phrase not in html_text:
            raise SystemExit("html part lost the phrase: " + phrase)
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A polite facilities note: Elmhollow is issuing contractor badges for the "
    "summer chiller replacement, named by the bare quote number 4712 so the "
    "service manager has one line item to match, and needs the names and "
    "truck numbers of the technicians who will be on site, entered in their "
    "vendor portal at https://vendors.elmhollow-living.example/contractors by "
    "Thursday. Use 'badge access list', 'confirm which technicians' and 'send "
    "me the names and truck numbers'. Say once that a reply carrying the same "
    "details also works, and state the deadline once; the message never "
    "argues that it is harmless. No password request, no urgency beyond the "
    "date, no attachment. Sign with a name (Dolores Achebe-Ferrante, "
    "Facilities Coordinator), the organization, and a direct number in the "
    "555-01xx block."
)

NOTES = (
    "The week 5 no-decisive-result case and one of the two low confidence "
    "cases the "
    "week 6 escalation threshold must catch. Key facts: the From domain "
    "elmhollow-living.example belongs to a real customer, but its reputation "
    "record is status unknown, first seen 2026-04-17, two messages in 90 days "
    "and no prior reports, so the domain is new rather than good; SPF, DKIM "
    "and DMARC all pass, which proves only that the mail came from the domain "
    "it names; the domain publishes a DMARC record with policy none, so "
    "dmarc_policy is none; there is no Reply-To; the one link host "
    "vendors.elmhollow-living.example is on neither list, so check_urls "
    "returns unlisted; no attachment; new thread; the recipient is the "
    "service manager, an ordinary mailbox with no flags. Expected action: "
    "verify_out_of_band_then_close. Playbook rules 1, 2 and 7 apply, and rule "
    "7 decides the action: a host on neither list is unknown, not clean. The "
    "verdict is benign because no fact points at an attack, and it still "
    "escalates because a sender with no history asks for a list of names, "
    "which is escalation reason unknown_sender_asks_for_data. Difficulty "
    "reason: no decisive fact points either way, so the base tier is hard; "
    "there is no injection and the body only read agrees with the truth, so "
    "neither adjustment applies and it stays hard. The body only read is "
    "benign because the prose is ordinary customer paperwork with no urgency "
    "and no credential ask. Loop reason: every tool answers with nothing "
    "decisive, so the bounded loop runs check_sender_reputation, check_urls "
    "and lookup_recipient in turn and ends with no tool left to try, at low "
    "confidence, which is the behavior week 5 is built to show. Three tools "
    "exist, so that is step 3; the cap of 4 is the guard that catches a "
    "repeated tool call. The body "
    "carries the four content:data_request phrases (badge access list, "
    "confirm which technicians, send me the names, names and truck numbers) "
    "and no urgency, credential, payment or file share phrase, so the data "
    "request is the only content indicator. The message states its deadline "
    "once and never argues that it is harmless, because a body that "
    "disclaims urgency would hand a 3B model the confident benign read this "
    "email exists to withhold. It names the job by the bare quote number "
    "4712, the checkable reference every other legitimate message in the set "
    "carries, and no data file records quotes, so nothing looks it up. The "
    "signature is the four line block an external human signer uses, ending "
    "in the reserved number 555-0163 rather than an internal extension, "
    "which is the channel the out of band verification calls. Rendering "
    "notes: the plain part is 7bit with hard wraps under 78 characters and "
    "the HTML part is quoted printable, because the fixed gateway banner "
    "snippet is longer than 78 characters; the banner is the first line of "
    "the plain part and the first line after the body tag in the HTML part; "
    "both parts carry the same text and the HTML part hides nothing, so "
    "there is no content:html_hidden_text. Line breaks in both parts are "
    "placed so that no content:data_request phrase is split across a line. "
    "There is no X-Originating-IP header: the sender is a customer's own "
    "mail server rather than a webmail provider, and the manifest lists no "
    "header:x_originating_ip indicator, so the client address 192.0.2.201 "
    "appears in the bottom Received line instead. Every identifier that "
    "looks random is derived from a SHA-256 over the corpus seed, the email "
    "id and a label, so the file regenerates byte for byte."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [5, 6],
    "date": "2026-04-17T09:55:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "hard",
    "body_only_read": "benign",
    "sender_display": "Elmhollow Senior Living Facilities",
    "sender_address": "facilities@elmhollow-living.example",
    "reply_to": None,
    "recipient": "h.quintanilla@pellgrave.example",
    "reporter": "h.quintanilla@pellgrave.example",
    "reported_after_interaction": False,
    "subject": "Badge access list for your technicians: confirm by Thursday",
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=elmhollow-living.example; "
                   "dkim=pass header.d=elmhollow-living.example header.s=eh1 "
                   "header.i=@elmhollow-living.example; "
                   "dmarc=pass header.from=elmhollow-living.example policy.dmarc=none")},
        {"code": "sender:first_seen", "where": "check_sender_reputation", "value": "2026-04-17"},
        {"code": "url:host_unlisted", "where": "check_urls",
         "value": "vendors.elmhollow-living.example"},
        {"code": "content:data_request", "where": "body",
         "value": "badge access list; confirm which technicians; send me the names; names and truck numbers"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:first_seen", "url:host_unlisted"],
    "url_hosts": ["vendors.elmhollow-living.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "elmhollow-living.example",
            "status": "unknown",
            "first_seen": "2026-04-17",
            "messages_90d": 2,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the corpus window.",
            "match_level": "domain",
        },
        "check_urls": {"vendors.elmhollow-living.example": "unlisted"},
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
        # Three tools exist and each one answers with nothing decisive, so the
        # run ends because there is no tool left to try, not because it hit the
        # cap of 4. The cap is the guard that catches a repeated tool call.
        # spec/corpus-spec.json and docs/phase0-corpus-design.md both say
        # tools_exhausted; this value is what renders that into ground truth.
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": True,
    "escalation_reasons": ["unknown_sender_asks_for_data"],
    "recommended_action": "verify_out_of_band_then_close",
    "reference_summary": ("This request looks like real customer paperwork, but the sender is "
                          "new to us and the portal is not one we have checked, so we are "
                          "confirming by phone with Elmhollow before you enter anything. "
                          "Please hold off until we get back to you today."),
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

    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            record["body_brief"] = BODY_BRIEF
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

    print("wrote " + EML_PATH)
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
