#!/usr/bin/env python3
"""Regenerate 004-cfo-quick-task.

Rebuilds emails/teaching/004-cfo-quick-task.eml from the corpus seed, refreshes
the matching manifest fields in spec/corpus-spec.json, and upserts the ground
truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_swk_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM t=               = the sender-side Received timestamp in epoch seconds

The DKIM b= value is the seed-derived signature this file already carried. It
is kept verbatim as a constant: it is 2048 bit synthetic signature bytes that
verify nothing (no .example domain can publish a key), it does not depend on
the body text, and the verifiers did not object to it.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

What this run changes, and why:

1. The payee named in the body was Larkhollow Controls. That name belongs to
   attacker infrastructure elsewhere in the corpus: data/sender_reputation.json
   gives larkhollow-controls.example status known_bad with three prior reports
   and the campaign tag fake-quote-portal, and record 008 is a teaching
   credential phish sent from that domain. This record asserted no campaign
   link and no second reputation expectation, so an agent that read the payee
   out of the body in week 5 and looked it up would land on a decisive
   known_bad result that the answer key does not hold, spend a third loop step
   and score wrong against expected_loop and stop_reason. The payee is now
   Quillbeck Controls, a name that appears in no other manifest record and in
   none of data/sender_reputation.json, data/domain_policy.json,
   data/url_allowlist.json, data/url_blocklist.json or data/url_unlisted.json.
   It carries no domain, no address and no link, so the body offers the loop
   nothing to look up and the two-call path stands. Renaming, rather than
   writing the crossover up as one campaign, is what keeps the week 5 lesson
   this email exists for: no link, so check_urls is the wrong second move and
   the loop stops on tools_exhausted after two calls.
2. The ground truth notes cited playbook rule 5 as a deciding rule. Rule 5 in
   data/playbook.md covers a change to a vendor's bank details or to when a
   payment goes out. This message sets up a first payment to a vendor with no
   details on file and no scheduled run, so the rule's text does not reach it,
   and the record now cites rule 2 alone and says why rule 5 is out.
   data/playbook.md is unchanged: it ships inside the week 3 prompt for every
   email, so widening rule 5 would have to be re-checked against every record
   that cites it.
3. The notes now record the authored tell that had no home: X-Mailer names a
   desktop client and the bottom Received hop is a workstation submission,
   while the body claims a phone. The indicator vocabulary in spec/enums.json
   has no code for that contradiction, so it is corroborating context for an
   analyst rather than a scored indicator, and an instructor can now see it.

No fact the labels turn on changed, so verdict, category, difficulty,
indicators, required_indicators, url_hosts, tool_expectations, expected_loop,
escalation and reference_summary are unchanged.

Run:  python3 corpus/tools/generators/gen_004_cfo_quick_task.py
"""

import base64
import hashlib
import json
import os
import uuid

EMAIL_ID = "004-cfo-quick-task"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break. The HTML part here is already written as short source
# lines, so only the gateway banner runs long, and it holds no space that a
# break could land on. The wrap is therefore a hard one at 75 characters plus
# the "=", stepping back if a break would fall inside an "=XX" escape.
QP_MAX = 76

DKIM_B = (
    "ZWa9DN+yNcRJ2rUnljjr7O6AwYkuugzXX4+WajqgH8nfAOzfomprp1TOLQIT+RYmfVmiImow"
    "pT03NcvY8F6iWyodxJm0T7gPf2W8xypV6tvGV8kAFG61wVyYBmcQ6dajZIjB0tnQrShZGYUI"
    "7WJcM3+1pQU7/uSq+VDgXd2oTp0tayxhhYFGhOeUPz0rSwf5sjDjPxJOkRVOG1Ch1brrDz6V"
    "LMDK+CfrxdguVhgnx1X76y/EcYpgiaj1AxCD4b75uuhU2A0S4/28z8HFORThhUuJWerAYTrj"
    "hNvzD/yImoSig0HEOcpbSEvn0U9PniqNDQtKn5qaCiv/kGWbPkRfEA=="
)


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


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

# The payee. Checked against every manifest record and against
# data/sender_reputation.json, data/domain_policy.json, data/url_allowlist.json,
# data/url_blocklist.json and data/url_unlisted.json: the name appears in none
# of them, and check_payee_is_unused() below refuses to write the file if that
# stops being true. It is a name only. No domain, no address and no link stands
# behind it, which is the point: the body must not hand the loop a fourth thing
# to look up when the lesson is that it has nothing left to call.
PAYEE = "Quillbeck Controls"

# Phrases the deterministic extractor keys on, all from the lists in
# spec/enums.json: "same-day" and "before my 2:00" carry
# content:urgency_keywords, "invoice" carries content:payment_request, and
# "email only", "can't take calls" and "Sent from my phone" carry
# content:channel_restriction. The wording stays clear of every other list:
# no "today" or "pay today" (content:payment_timing_request), no "new account"
# (content:payment_change_request), no "call me"
# (content:phone_verification_offered), no "not working"
# (content:excuse_for_external_address).
PARA_1 = ["Are you at your desk?"]
PARA_2_PLAIN = [
    "I need a same-day payment set up for a new vendor on the Rookmere",
    "chiller project. The company is " + PAYEE + " and their",
    "invoice is $18,400. It has to go out before my 2:00. I will send",
    "the remittance details in a few minutes.",
]
PARA_3_PLAIN = [
    "I am between meetings and working from my phone, so handle this by",
    "email only. I can't take calls until after 3. Let me know as soon",
    "as you see this.",
]
PARA_2_HTML = [
    "I need a same-day payment set up for a new vendor on the Rookmere",
    "chiller project. The company is " + PAYEE + " and their invoice",
    "is $18,400. It has to go out before my 2:00. I will send the",
    "remittance details in a few minutes.",
]
PARA_3_HTML = [
    "I am between meetings and working from my phone, so handle this by",
    "email only. I can't take calls until after 3. Let me know as soon as",
    "you see this.",
]
SIGN_OFF = "Rutger"
PHONE_LINE = "Sent from my phone"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;'
               'color:#5a4a00;">[External message. Sentrywick Gateway]</p>')


def plain_part():
    lines = [BANNER_PLAIN, "", "Priya,", ""]
    lines += PARA_1 + [""]
    lines += PARA_2_PLAIN + [""]
    lines += PARA_3_PLAIN + [""]
    lines += [SIGN_OFF, "", PHONE_LINE]
    return lines


def html_part():
    lines = ["<html>", "<body>", BANNER_HTML,
             '<div style="font-family:sans-serif;font-size:15px;color:#222222">',
             "<p>Priya,</p>",
             "<p>" + PARA_1[0] + "</p>"]
    lines += ["<p>" + PARA_2_HTML[0]] + PARA_2_HTML[1:3] + [PARA_2_HTML[3] + "</p>"]
    lines += ["<p>" + PARA_3_HTML[0]] + PARA_3_HTML[1:2] + [PARA_3_HTML[2] + "</p>"]
    lines += ["<p>" + SIGN_OFF + "</p>", "<p>" + PHONE_LINE + "</p>"]
    lines += ["</div>", "</body>", "</html>"]
    return lines


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks."""
    text = line.replace("=", "=3D")
    out = []
    while len(text) > QP_MAX:
        cut = QP_MAX - 1
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
    boundary = "=_swk_" + hexid(seed, "boundary")
    message_id = ("<20260414174700." + hexid(seed, "message-id")
                  + "@smtp.pellgrave-corp.example>")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore("p.castellanos@pellgrave.example")

    lines = [
        "Return-Path: <r.palomares@pellgrave-corp.example>",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <p.castellanos@pellgrave.example>; Tue, 14 Apr 2026 12:47:07 -0500",
        # The gateway writes Authentication-Results above its own trace fields
        # (RFC 8601 sec. 4). All three pass for the attacker's own domain, which
        # is the week 3 lesson: a pass names the domain, never the person.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=pellgrave-corp.example;",
        "  dkim=pass header.d=pellgrave-corp.example header.s=k1",
        "    header.i=@pellgrave-corp.example;",
        "  dmarc=pass header.from=pellgrave-corp.example policy.dmarc=none",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  r.palomares@pellgrave-corp.example designates 203.0.113.151 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=203.0.113.151;",
        '  envelope-from="r.palomares@pellgrave-corp.example";',
        "  helo=smtp.pellgrave-corp.example; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 3.4",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: p.castellanos@pellgrave.example",
        "Received: from smtp.pellgrave-corp.example",
        "  (smtp.pellgrave-corp.example [203.0.113.151])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Tue, 14 Apr 2026 12:47:05 -0500",
        # The bottom hop is a desktop client on the attacker's own submission
        # host, and X-Mailer below names a desktop mail client, while the body
        # says the sender is on a phone. That contradiction is deliberate and
        # the ground truth notes record it; no indicator code carries it.
        "Received: from client-04.pellgrave-corp.example ([192.0.2.62])",
        "  by smtp.pellgrave-corp.example with ESMTPSA id " + sender_id + ";",
        "  Tue, 14 Apr 2026 17:47:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=pellgrave-corp.example; s=k1; t=1776188822;",
        "  h=from:to:subject:date:message-id:mime-version:content-type:x-mailer;",
        "  bh=" + body_hash(seed) + ";",
    ]
    signature = [DKIM_B[i:i + 72] for i in range(0, len(DKIM_B), 72)]
    lines.append("  b=" + signature[0])
    for chunk in signature[1:]:
        lines.append("   " + chunk)
    lines += [
        "Date: Tue, 14 Apr 2026 12:47:00 -0500",
        "From: Rutger Palomares <r.palomares@pellgrave-corp.example>",
        "To: Priya Castellanos <p.castellanos@pellgrave.example>",
        "Subject: Quick task before my 2:00",
        "Message-ID: " + message_id,
        "X-Mailer: Marrowdale Mail 5.2",
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    # The plain part is pure ASCII under 78 characters a line, so it stays 7bit
    # (docs/email-header-realism.md sec. 2). The HTML part carries the banner
    # snippet, which is longer than 78, so that part is quoted-printable.
    lines += plain_part()
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += encode(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Three short paragraphs in the CFO's voice: ask Priya if she is at her "
    "desk, say a same-day payment of 18,400 to a new vendor (" + PAYEE + ") "
    "for the Rookmere chiller project has to go out before his 2:00, and say "
    "he is between meetings on his phone so she should handle it by email "
    "only and not call. Use the phrases 'same-day', 'before my 2:00' and "
    "'email only'. The payee is " + PAYEE + ", a name that appears in no "
    "other manifest record and in no data file: it has no domain, no address "
    "and no reputation entry, so the body names nothing a tool can look up "
    "and the week 5 loop still stops after two calls. The Rookmere chiller "
    "project is the customer job other records also name, and it appears here "
    "as a project name only, with no domain behind it. No link, no "
    "attachment, no bank details yet. Close with 'Sent from my phone' and the "
    "name Rutger."
)

LURE_SUMMARY = (
    "Someone using the CFO's name asks the accounts payable specialist "
    "whether she is at her desk and says a same-day payment to a new vendor, "
    + PAYEE + ", on the Rookmere chiller project must go out before his "
    "meeting. He says he is on his phone and to handle it by email only."
)

NOTES = (
    "Business email compromise with no link and no attachment: the fourth "
    "category week 2 needs, the display-name versus sender-domain case in "
    "week 3, and the week 5 loop path where calling check_urls is the wrong "
    "second move. Key facts: the display name Rutger Palomares is the "
    "company's real Chief Financial Officer, whose address is "
    "r.palomares@pellgrave.example, while the From domain is "
    "pellgrave-corp.example, an added-word lookalike the attacker registered "
    "and published SPF and DKIM for; no Reply-To; SPF, DKIM and DMARC all "
    "pass for pellgrave-corp.example, which publishes a DMARC record with "
    "policy none, and that pass proves only that the mail came from the "
    "attacker's own domain; the message arrived through the gateway "
    "(X-Sentrywick-External: yes) with a clean scan and a spam score of 3.4; "
    "there is no link, no removed attachment and no In-Reply-To. Difficulty "
    "medium by the tier rule: two decisive facts "
    "(sender:display_name_matches_employee and sender:lookalike_domain) "
    "against one pressure point (no link and no attachment, so check_urls has "
    "nothing to check), which is decisive over pressure without a tie, and "
    "neither adjustment applies because there is no injection and the "
    "body-only read already lands on malicious. Playbook rule that decides "
    "the case: rule 2, an employee's name over an address outside "
    "pellgrave.example is impersonation until a phone call proves otherwise, "
    "which is also where the callback in the close comes from. Rule 5 is not "
    "cited and does not reach this message: it covers a change to a vendor's "
    "bank details or to when a payment goes out, and this is a first payment "
    "to a vendor with no details on file and no scheduled run, which is why "
    "the record carries content:payment_request and neither "
    "content:payment_change_request nor content:payment_timing_request. A "
    "student who cites rule 2 alone has the whole answer. Body signals: the "
    "ask is a same-day payment before a named meeting, the amount and the "
    "vendor are given, the remittance details are promised in a later "
    "message, and the sender rules out the phone and asks for email only, "
    "which is the pattern that keeps the real Rutger from being reached. The "
    "payee named in the body, " + PAYEE + ", appears in no other record and "
    "in none of data/sender_reputation.json, data/domain_policy.json, "
    "data/url_allowlist.json, data/url_blocklist.json or "
    "data/url_unlisted.json. It is a name with no domain, no address and no "
    "link behind it, so the body hands the loop nothing further to look up "
    "and no fourth fact hides outside the answer key; the Rookmere chiller "
    "project, which 008 and 054 also name, is likewise a project name with no "
    "domain in this body. That is deliberate: the whole week 5 lesson here is "
    "that the agent has nothing left to call. Corroborating context rather "
    "than a scored indicator: X-Mailer says Marrowdale Mail 5.2 and the "
    "bottom Received hop is client-04.pellgrave-corp.example [192.0.2.62] "
    "handing the message in over ESMTPSA, both the shape of a desktop client, "
    "while the body closes 'Sent from my phone' and uses the phone as the "
    "reason the sender cannot be called. An analyst should read that "
    "contradiction and a student who finds it is right, but the indicator "
    "vocabulary in spec/enums.json has no code for a mailer or hop that "
    "disagrees with the body, so nothing scores it; the phrase itself is "
    "already carried by content:channel_restriction. Tools: "
    "check_sender_reputation matches at domain level and returns status "
    "unknown with new_domain true and first_seen 2026-04-14, the day this "
    "message arrived; lookup_recipient shows Priya Castellanos is an ordinary "
    "mailbox that handles payments, with six reports and four true positives "
    "in 90 days; check_urls has nothing to look up, so the loop stops on "
    "tools_exhausted after two calls rather than spending a step on a tool "
    "with no input. That is the week 5 lesson this email carries. "
    "recipient:prior_similar_report is absent by the prior_similar_report_rule: "
    "content:payment_request is not an ask code, the message carries no "
    "payment change, timing or gift card ask, and the sender record has no "
    "campaign tag, so no tag is collected and no campaign ties this message "
    "to any other record. Expected action: escalate_incident for "
    "financial_or_endpoint_impact, because a malicious BEC always escalates "
    "whatever the recipient's flags say. Priya is not an executive, so "
    "executive_target does not apply, and she reported the message before "
    "acting on it, so user_interacted does not apply. The correct close is to "
    "confirm with Rutger at his extension, block pellgrave-corp.example, and "
    "tell accounts payable that no payment was set up."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [2, 3, 5],
    "date": "2026-04-14T12:47:00-05:00",
    "verdict": "malicious",
    "category": "bec",
    "difficulty": "medium",
    "body_only_read": "malicious",
    "sender_display": "Rutger Palomares",
    "sender_address": "r.palomares@pellgrave-corp.example",
    "reply_to": None,
    "recipient": "p.castellanos@pellgrave.example",
    "reporter": "p.castellanos@pellgrave.example",
    "reported_after_interaction": False,
    "subject": "Quick task before my 2:00",
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "none"},
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": ("spf=pass smtp.mailfrom=pellgrave-corp.example; dkim=pass "
                   "header.d=pellgrave-corp.example header.s=k1 "
                   "header.i=@pellgrave-corp.example; dmarc=pass "
                   "header.from=pellgrave-corp.example policy.dmarc=none")},
        {"code": "sender:display_name_matches_employee", "where": "From",
         "value": "Rutger Palomares"},
        {"code": "sender:lookalike_domain", "where": "From", "value": "pellgrave.example"},
        {"code": "sender:first_seen", "where": "check_sender_reputation",
         "value": "2026-04-14"},
        {"code": "content:payment_request", "where": "body", "value": "invoice"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "same-day; before my 2:00"},
        {"code": "content:channel_restriction", "where": "body",
         "value": "email only; can't take calls; sent from my phone"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
        {"code": "url:none", "where": "body", "value": None},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": "p.castellanos@pellgrave.example"},
    ],
    "required_indicators": ["sender:display_name_matches_employee", "sender:lookalike_domain"],
    "url_hosts": [],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "pellgrave-corp.example",
            "status": "unknown",
            "first_seen": "2026-04-14",
            "messages_90d": 2,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": True,
            "notes": "First seen inside the window.",
            "match_level": "domain",
        },
        "check_urls": {},
        "lookup_recipient": {
            "address": "p.castellanos@pellgrave.example",
            "name": "Priya Castellanos",
            "role": "Accounts Payable Specialist",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": True,
            "chronic_reporter": False,
            "report_count_90d": 6,
            "true_positive_count_90d": 4,
            "campaign_tags": ["credential-phish", "invoice-malware",
                              "vendor-invoice-fraud", "vendor-notice"],
        },
    },
    "expected_loop": {"tools": ["check_sender_reputation", "lookup_recipient"],
                      "stop_reason": "tools_exhausted"},
    "escalate_expected": True,
    "escalation_reasons": ["financial_or_endpoint_impact"],
    "recommended_action": "escalate_incident",
    "reference_summary": ("This did not come from Rutger; the address is on a look-alike "
                          "domain that is not ours, and it pushes for a fast payment by "
                          "email only. We are treating it as an attempted fraud, and no "
                          "payment should be made."),
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": NOTES,
}


# ------------------------------------------------------------------- checks

DATA_FILES = ("data/sender_reputation.json", "data/domain_policy.json",
              "data/url_allowlist.json", "data/url_blocklist.json",
              "data/url_unlisted.json", "data/recipients.json",
              "data/known_good_domains.json", "data/attachments.json",
              "data/known_threads.json", "data/playbook.md")


def check_payee_is_unused(spec):
    """Refuse to write a payee name that anything else in the corpus uses.

    The whole point of the rename is that the body names no party a tool can
    resolve. A future edit that gives this name a domain, a reputation record
    or another record of its own would put back the trap the rename removed,
    so the check runs on every render rather than once.
    """
    needles = [PAYEE.lower()] + [word.lower() for word in PAYEE.split() if len(word) > 4]
    needles = [n for n in needles if n != "controls"]
    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            continue
        text = json.dumps(record).lower()
        for needle in needles:
            if needle in text:
                raise SystemExit("payee name " + PAYEE + " already appears in record "
                                 + record["id"] + "; pick a name nothing else uses")
    for rel in DATA_FILES:
        path = os.path.join(CORPUS, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf-8").read().lower()
        for needle in needles:
            if needle in text:
                raise SystemExit("payee name " + PAYEE + " appears in " + rel
                                 + "; the payee must resolve to nothing")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    check_payee_is_unused(spec)

    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            record["body_brief"] = BODY_BRIEF
            record["lure_summary"] = LURE_SUMMARY
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
