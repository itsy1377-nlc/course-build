#!/usr/bin/env python3
"""Regenerate 009-ceo-are-you-available.

Rebuilds emails/teaching/009-ceo-are-you-available.eml byte for byte from the
corpus seed, refreshes the prose fields of the matching manifest record in
spec/corpus-spec.json, and upserts the ground truth record in
ground_truth.json. It touches no other record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = sha256("<seed>|<id>|<label>|<block>") for block 0, 1 ...
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_lmw_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    webmail Received id   = hex("sender-id", 12)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    DKIM t=               = the sender-side Received timestamp in epoch seconds

Two conventions here come from the sending platform rather than from the
generic table, and they match 021-direct-deposit-change-request, the other
Lanternmail message already rendered:

  * the boundary prefix is "=_lmw_", the webmail client's own, not the
    "=_swk_" our submission host writes, because this message was composed in
    a browser on lanternmail.example;
  * the webmail hop's Received id is twelve hex digits, the width a Lanternmail
    SMTP host writes, rather than the eight an attacker's own submission host
    writes elsewhere in the corpus. One product, one id format.

The Message-ID right side is webapp-07.lanternmail.example, the front end named
in the innermost hop, and that hop stamps UTC while the gateway and the store
stamp -0500.

Neither DKIM value verifies. They are seeded bytes of the right length (44
base64 characters of body hash, 344 of signature), because no .example domain
can publish a key and no lab checks a signature. That the signature verifies
nothing is the whole point of this record: SPF, DKIM and DMARC all pass and
prove only that the mail really came from the webmail provider whose name is
on the envelope, never that Adaeze Whitcombe wrote it.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

What this run changes in the manifest record, and why:

1. body_brief opened the message with "Beatrix, are you in the office today?".
   The word "today" is an entry in the content:urgency_keywords phrase list in
   spec/enums.json, and tools/validate_corpus.py runs those lists both ways: a
   phrase in the rendered body whose code the record does not list is a
   failure, because a student's own extractor would produce a fact the answer
   key denies. This record deliberately lists no urgency code, and it should
   not: the whole lesson of the message is that it applies no deadline, makes
   no ask and carries no link, so that only the recipient tool settles it. The
   rendered first sentence is therefore "Beatrix, are you in the office?" and
   the brief now says so. Nothing the labels turn on moved: the indicator list,
   the difficulty derivation, the loop and the escalation are unchanged.
2. lure_summary said the favor was asked for "today" for the same reason and
   now says "while she is out", which is what the body actually offers. It
   stays two sentences, as tools/check_spec.py requires.
3. notes now records the phrase-list constraint above, so that the next person
   to edit this body knows why the word is absent.

No semantic field changed: verdict, category, difficulty, indicators,
required_indicators, url_hosts, attachment, injection, tool_expectations,
expected_loop, escalate_expected, escalation_reasons, recommended_action and
reference_summary are exactly as authored.

Run:  python3 corpus/tools/generators/gen_009_ceo_are_you_available.py
"""

import base64
import calendar
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "009-ceo-are-you-available"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER_DISPLAY = "Adaeze Whitcombe"
SENDER = "adaeze.whitcombe.pmg@lanternmail.example"
RECIPIENT = "b.onwuka@pellgrave.example"
RECIPIENT_DISPLAY = "Beatrix Onwuka"
REPORTER = "b.onwuka@pellgrave.example"
SUBJECT = "Are you available?"

# The sender-side hop stamps 13:03:02 UTC, which is the 08:03:02 -0500 the
# gateway would have written. The DKIM t= tag is that instant in epoch seconds,
# so the signature and the Received chain cannot drift apart.
DKIM_T = calendar.timegm((2026, 4, 20, 13, 3, 2, 0, 0, 0))

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break. Only the HTML part is encoded here, and its long
# lines are a style attribute and one paragraph of prose, so the wrap is a hard
# cut that steps back if a break would land inside an "=XX" escape.
QP_MAX = 76


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


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
#
# Three sentences and an initial. There is no ask, no amount, no link and no
# attachment, because this is the first message of a gift-card pair and the
# ask is what the second one carries; a pretext that already asked for
# something would settle itself from the body alone, and this record's
# body_only_read is uncertain on purpose.
#
# The wording carries exactly the three content codes the record lists, each
# matched from the phrase lists in spec/enums.json:
#
#   content:secrecy_request           "quietly"
#   content:channel_restriction       "can't take calls"
#   content:excuse_for_external_address  "wifi blocks" and "personal mail"
#
# and it carries no phrase from any other list. validate_corpus.py runs those
# lists in both directions, so a stray "today", "invoice", "call me" or
# "download" would fail the file even though it reads harmlessly; check_no_
# stray_phrases() below refuses to write the file when one appears. The plain
# part's line breaks are placed so that no phrase is split across a physical
# line, because the decoded plain part keeps its newlines.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# The name and nothing else. A CEO writing to her own assistant does not open
# with "Hi Beatrix," and does not sign her full name, and the attacker who has
# read enough to know the assistant's first name writes it the way the real
# sender would.
OPENING = "Beatrix, are you in the office?"

# The body of the pretext. "quietly" is the secrecy phrase and "can't take
# calls" is the channel restriction; together they are the two halves of the
# pattern the playbook's rule 6 names, an executive asking for secrecy by
# email, and the reason the assistant cannot close the case with one phone
# call to the conference hotel.
PARA = [
    "I need you to handle something for me quietly and I can't take calls",
    "between sessions. The conference wifi blocks the VPN so I'm on my",
    "personal mail; just reply here.",
]

# One initial. It is what a hurried executive signs, it gives the reader no
# extension to dial, and it keeps the message short enough that nothing in it
# can be checked.
SIGN_OFF = "A."


def plain_part():
    lines = [BANNER_PLAIN, "", OPENING, ""]
    lines += PARA + [""]
    lines += [SIGN_OFF]
    return lines


def html_part():
    """The same words, in the plain paragraphs a webmail client writes."""
    return [
        BANNER_HTML,
        '<div style="font-family:sans-serif;font-size:14px;color:#222222">',
        "<p>" + OPENING + "</p>",
        "<p>" + " ".join(PARA) + "</p>",
        "<p>" + SIGN_OFF + "</p>",
        "</div>",
    ]


# ------------------------------------------------------- quoted-printable

def qp_wrap(line):
    """Fold one logical line into quoted-printable physical lines."""
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


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_lmw_" + hexid(seed, "boundary")
    message_id = ("<20260420130302." + hexid(seed, "message-id")
                  + "@webapp-07.lanternmail.example>")
    gateway_id = hexid(seed, "gateway-id")
    webmail_id = hexid(seed, "sender-id")
    lmtp_id = store_id(seed)
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    store = mailstore(RECIPIENT)

    lines = [
        # A webmail account sends its own bounces, so the envelope sender is
        # the From mailbox and there is no Return-Path split and no Sender.
        "Return-Path: <" + SENDER + ">",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Mon, 20 Apr 2026 08:03:07 -0500",
        # The gateway writes Authentication-Results above its own trace fields
        # (RFC 8601 sec. 4). All three pass, for lanternmail.example, which is
        # the trap: the provider really did send this, and that says nothing
        # about whose name is on it.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=lanternmail.example;",
        "  dkim=pass header.d=lanternmail.example header.s=lm2026a",
        "  header.i=@lanternmail.example;",
        "  dmarc=pass header.from=lanternmail.example policy.dmarc=quarantine",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  " + SENDER + " designates 198.51.100.77 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=198.51.100.77;",
        '  envelope-from="' + SENDER + '";',
        "  helo=smtp-out-04.lanternmail.example; identity=mailfrom;",
        "  mechanism=ip4:198.51.100.64/26",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 3.0",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from smtp-out-04.lanternmail.example",
        "  (smtp-out-04.lanternmail.example [198.51.100.77])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Mon, 20 Apr 2026 08:03:05 -0500",
        # The composing front end, on the provider's own private-facing range,
        # handing the message to the provider's outbound host over an
        # authenticated session. Nothing below this line is ours.
        "Received: from webapp-07.lanternmail.example ([192.0.2.57])",
        "  by smtp-out-04.lanternmail.example (Lanternmail SMTP) with ESMTPSA",
        "  id " + webmail_id + "; Mon, 20 Apr 2026 13:03:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=lanternmail.example;",
        "  s=lm2026a; t=" + str(DKIM_T) + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type:",
        "   x-originating-ip:x-mailer;",
        "  bh=" + body_hash(seed) + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: Mon, 20 Apr 2026 08:03:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # The webmail client stamps the composing browser's address. It is a
        # consumer address in 203.0.113.0/24 and not the provider's own range,
        # and it is the same client address 029 carries, because the same
        # person sent both halves of the pair.
        "X-Originating-IP: [203.0.113.88]",
        "X-Mailer: Lanternmail Web",
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        # The plain part is pure ASCII under 78 characters a line, so it stays
        # 7bit (docs/email-header-realism.md sec. 2). The HTML part carries the
        # gateway banner snippet, which is longer than 78, so that part is
        # quoted-printable.
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
    lines += encode(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Three sentences and an initial: 'Beatrix, are you in the office? I need "
    "you to handle something for me quietly and I can't take calls between "
    "sessions. The conference wifi blocks the VPN so I'm on my personal mail; "
    "just reply here.' Use 'quietly', 'can't take calls', 'wifi blocks' and "
    "'personal mail', which are the phrase-list entries behind the three "
    "content indicators. No link, no attachment, no amount, no deadline word "
    "and no ask beyond the reply: the word 'today' is deliberately absent "
    "because it is a content:urgency_keywords phrase and this record lists no "
    "urgency code, the message applying pressure through familiarity rather "
    "than through a clock. Sign 'A.'"
)

LURE_SUMMARY = (
    "Three sentences in the CEO's name ask her assistant whether she is in "
    "the office and can handle a discreet favor while she is out. It explains "
    "the personal address by saying the conference wifi blocks the company "
    "VPN, and asks for a reply."
)

MANIFEST_NOTES = (
    "Pretext-only BEC: no ask yet, no link, no attachment, and every "
    "authentication check passes for the webmail provider. The CEO really is "
    "at a conference 20 to 23 April, which is why it lands. Week 4 "
    "lookup_recipient case: the reputation tool returns neutral for the "
    "domain and no address record, so only the recipient tool (executive "
    "flag, three prior CEO-impersonation reports) settles it. Week 6 "
    "low-confidence threshold case. Escalation reasons: "
    "financial_or_endpoint_impact, executive_target. Rendering note: the body "
    "carries no phrase from any content list except the three the indicators "
    "name, because tools/validate_corpus.py runs the spec/enums.json phrase "
    "lists in both directions. That is why the opening sentence asks 'are you "
    "in the office?' and not 'in the office today?': 'today' is a "
    "content:urgency_keywords entry, and this message applies no deadline at "
    "all."
)


# ------------------------------------------------------------ ground truth

AUTH_VALUE = ("spf=pass smtp.mailfrom=lanternmail.example; dkim=pass "
              "header.d=lanternmail.example header.s=lm2026a "
              "header.i=@lanternmail.example; dmarc=pass "
              "header.from=lanternmail.example policy.dmarc=quarantine")

NOTES = (
    "Business email compromise as pretext alone: the first half of a "
    "gift-card pair, where the ask is still to come and nothing in the "
    "message can be checked. It is the week 4 lookup_recipient case, the one "
    "email where that tool alone changes the verdict, and a week 6 "
    "low-confidence case for the escalation threshold. Key facts: the display "
    "name Adaeze Whitcombe is the company's real Chief Executive Officer, "
    "whose address is a.whitcombe@pellgrave.example, while the From address "
    "is adaeze.whitcombe.pmg@lanternmail.example at a free webmail provider; "
    "no Reply-To; SPF, DKIM and DMARC all pass for lanternmail.example, which "
    "publishes a quarantine policy, and that pass proves only that the "
    "provider really sent the message; X-Originating-IP [203.0.113.88] is the "
    "webmail user's client address, the same one 029 carries; the message "
    "arrived through the gateway (X-Sentrywick-External: yes) with a clean "
    "scan and a spam score of 3.0; there is no link, no removed attachment "
    "and no In-Reply-To. Difficulty medium by the tier rule: one decisive "
    "fact (sender:display_name_matches_employee) against one pressure point "
    "(no link and no attachment together, so check_urls has nothing to "
    "check), which is decisive over pressure without a tie, and neither "
    "adjustment applies because there is no injection and the body-only read "
    "is uncertain rather than benign. Playbook rules that decide the case: "
    "rule 2, an employee's name over an address outside pellgrave.example is "
    "impersonation until a phone call proves otherwise, and rule 6, "
    "executives do not ask for gift cards, wire transfers or secrecy by "
    "email, which the word 'quietly' triggers on its own; rule 1 is the "
    "background, that three passes name a domain and never a person. Body "
    "signals: the message asks only whether the assistant is in the office, "
    "asks her to handle something quietly, rules out the telephone for the "
    "day, and explains the outside address with the conference wifi. There is "
    "no amount, no vendor, no deadline word and no link, so a body-only "
    "reading lands on uncertain: a chief executive at a conference really "
    "might write a short note from a personal account, and nothing in the "
    "text is false on its face. Tools: check_sender_reputation matches at "
    "domain level, because adaeze.whitcombe.pmg@lanternmail.example has no "
    "address record of its own, and returns neutral for the provider with "
    "nine prior reports, the last one malicious and tagged ceo-impersonation; "
    "lookup_recipient shows Beatrix Onwuka is the Executive Assistant to the "
    "CEO with the executive flag set and three prior CEO-impersonation "
    "reports, all true positives, which is the fact that settles the case; "
    "check_urls has nothing to look up, so the loop stops on tools_exhausted "
    "after two calls. The near neighbour is a trap worth naming for "
    "instructors: adaeze.whitcombe.office@lanternmail.example, the address 029 "
    "uses two days later, does carry a known_bad address record, and this "
    "message deliberately uses a different local part so that the reputation "
    "tool cannot decide it. recipient:prior_similar_report follows the "
    "prior_similar_report_rule: the message carries no ask code, so no tag "
    "comes from the ask, but the sender reputation record's campaign tag is "
    "ceo-impersonation, which is in sender_campaign_tags, and the recipient "
    "holds three prior reports under that tag, so the value is "
    "ceo-impersonation. Expected action: escalate_incident, with reasons "
    "financial_or_endpoint_impact, because a malicious BEC always escalates, "
    "and executive_target, because the CEO's assistant carries the executive "
    "flag; she reported the message before replying, so user_interacted does "
    "not apply. The correct close is to leave the message unanswered, warn "
    "the executive office that a second message with the ask is likely, and "
    "confirm with Adaeze on her known extension rather than at the address "
    "that wrote."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [4, 6],
    "date": "2026-04-20T08:03:00-05:00",
    "verdict": "malicious",
    "category": "bec",
    "difficulty": "medium",
    "body_only_read": "uncertain",
    "sender_display": SENDER_DISPLAY,
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "external_gateway",
    "auth": {
        "spf": "pass",
        "dkim": "pass",
        "dmarc": "pass",
        "dmarc_policy": "quarantine",
    },
    "indicators": [
        {
            "code": "auth:all_pass",
            "where": "Authentication-Results",
            "value": AUTH_VALUE,
        },
        {
            "code": "sender:display_name_matches_employee",
            "where": "From",
            "value": SENDER_DISPLAY,
        },
        {
            "code": "sender:freemail_domain",
            "where": "check_sender_reputation",
            "value": "lanternmail.example",
        },
        {
            "code": "header:x_originating_ip",
            "where": "X-Originating-IP",
            "value": "[203.0.113.88]",
        },
        {
            "code": "content:secrecy_request",
            "where": "body",
            "value": "quietly",
        },
        {
            "code": "content:channel_restriction",
            "where": "body",
            "value": "can't take calls",
        },
        {
            "code": "content:excuse_for_external_address",
            "where": "body",
            "value": "wifi blocks; personal mail",
        },
        {
            "code": "header:external_flag",
            "where": "X-Sentrywick-External",
            "value": "yes",
        },
        {
            "code": "url:none",
            "where": "body",
            "value": None,
        },
        {
            "code": "attachment:none",
            "where": "X-Sentrywick-Removed-Attachment",
            "value": None,
        },
        {
            "code": "thread:new",
            "where": "In-Reply-To",
            "value": None,
        },
        {
            "code": "recipient:executive",
            "where": "lookup_recipient",
            "value": RECIPIENT,
        },
        {
            "code": "recipient:prior_similar_report",
            "where": "lookup_recipient",
            "value": "ceo-impersonation",
        },
    ],
    "required_indicators": [
        "sender:display_name_matches_employee",
        "sender:freemail_domain",
        "recipient:executive",
    ],
    "url_hosts": [],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "lanternmail.example",
            "status": "neutral",
            "first_seen": "2019-06-11",
            "messages_90d": 340,
            "prior_reports": 9,
            "last_report_verdict": "malicious",
            "last_report_date": "2026-03-31",
            "campaign_tag": "ceo-impersonation",
            "new_domain": False,
            "notes": ("Free webmail provider. Domain reputation is neutral; "
                      "address records override it."),
            "match_level": "domain",
        },
        "check_urls": {
        },
        "lookup_recipient": {
            "address": RECIPIENT,
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
    "expected_loop": {
        "tools": ["check_sender_reputation", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": True,
    "escalation_reasons": [
        "financial_or_endpoint_impact",
        "executive_target",
    ],
    "recommended_action": "escalate_incident",
    "reference_summary": (
        "This note is not from Adaeze; it came from a free webmail account "
        "using her name, and it matches the start of the gift-card scams you "
        "have reported before. Do not reply, and we have already told her "
        "office."
    ),
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": NOTES,
}


# ------------------------------------------------------------------- checks

# The content codes this body is allowed to trigger. Every other phrase list in
# spec/enums.json has to miss, because validate_corpus.py reads a hit whose code
# the record does not list as a fact the answer key denies.
ALLOWED_CONTENT_CODES = {
    "content:secrecy_request",
    "content:channel_restriction",
    "content:excuse_for_external_address",
}

# Lists the validator skips: one is a proportion judgment over Spanish
# stopwords that appear inside ordinary English words, the other is single
# words the corpus also puts inside quoted examples.
PHRASE_PASS_SKIP = {"content:non_english_body", "content:instruction_to_ai"}


def check_no_stray_phrases(parsed):
    """Fail the render when the body carries a phrase this record does not claim.

    The body is three sentences, so it is easy to edit and easy to break: one
    "today", "invoice", "call me" or "download" would add a content code the
    manifest does not list, and validate_corpus.py would fail the file. The
    check runs on every render rather than once, on the decoded parts, which is
    where the validator looks.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    body = ""
    for part in parsed.walk():
        if part.get_content_maintype() == "text":
            body += part.get_content() + "\n"
    body = body.lower()
    for code, phrases in sorted(enums["content_phrases"].items()):
        if code in PHRASE_PASS_SKIP or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases if phrase.lower() in body]
        if hits and code not in ALLOWED_CONTENT_CODES:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")
        if code in ALLOWED_CONTENT_CODES and not hits:
            raise SystemExit("the body carries no phrase for " + code)
    for indicator in GROUND_TRUTH["indicators"]:
        code = indicator["code"]
        value = indicator["value"]
        if code not in enums["content_phrases"] or not value:
            continue
        known = {phrase.lower() for phrase in enums["content_phrases"][code]}
        for piece in str(value).split("; "):
            if piece.lower() not in known:
                raise SystemExit(code + " records " + repr(piece)
                                 + ", which is not an entry in its phrase list")
            if piece.lower() not in body:
                raise SystemExit(code + " records " + repr(piece)
                                 + ", which is not in the rendered body")


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
    for field in ("subject", "sender_address", "sender_display", "recipient",
                  "reporter", "verdict", "category", "difficulty"):
        if record[field] != GROUND_TRUTH[field]:
            raise SystemExit(field + " does not match the manifest: "
                             + repr(record[field]) + " against "
                             + repr(GROUND_TRUTH[field]))
    if record["injection"] is not None:
        raise SystemExit("the manifest now carries an injection; this record had none")
    manifest_codes = [item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]]
    truth_codes = [item["code"] for item in GROUND_TRUTH["indicators"]]
    if manifest_codes != truth_codes:
        raise SystemExit("indicator codes drifted from the manifest: "
                         + repr(manifest_codes) + " against " + repr(truth_codes))

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
    check_no_stray_phrases(parsed)

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
    print("updated manifest prose and upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
