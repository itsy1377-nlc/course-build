#!/usr/bin/env python3
"""Regenerate 018-hollinvale-site-access-link.

Rebuilds emails/teaching/018-hollinvale-site-access-link.eml byte for byte from
the corpus seed, refreshes the matching manifest fields in spec/corpus-spec.json,
and upserts the ground truth record in ground_truth.json. It touches no other
record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the corpus
derives them, so rerunning this script reproduces the same bytes:

    hex(label, n)         = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hex("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    stream(label, n)      = sha256("<seed>|<id>|<label>|<block>") for block 0, 1, 2 ...

Neither DKIM value verifies. They are seeded bytes of the right length, the same
convention the rest of the corpus uses, because no .example domain can publish a
key and no lab checks a signature.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

This is a compromised customer mailbox. Every header is honest: Hollinvale's own
server really sent it, so spf, dkim and dmarc all pass and the reputation record
still says known_good. The only fact that turns the verdict is the link host,
which check_urls answers from the blocklist. That is why the body is written to
be unremarkable: it carries no urgency phrase, no credential phrase and no
attachment, and a body-only read of it is benign.

Run:  python3 corpus/tools/generators/gen_018_hollinvale_site_access_link.py
"""

import base64
import hashlib
import json
import os
import uuid

EMAIL_ID = "018-hollinvale-site-access-link"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

RECIPIENT = "h.quintanilla@pellgrave.example"

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters.
QP_MAXLEN = 76


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def body_hash(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|dkim-bh").encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def stream(seed, label, count):
    out = b""
    block = 0
    while len(out) < count:
        out += hashlib.sha256(
            (seed + "|" + EMAIL_ID + "|" + label + "|" + str(block)).encode()).digest()
        block += 1
    return out[:count]


def signature(seed):
    """344 base64 characters, the length of a 2048 bit RSA signature."""
    return base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")


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
# The whole message is a salutation, one short paragraph, one link, a sign-off
# and Renata's own signature block. Nothing argues, nothing hurries and nothing
# explains itself, because this is the mailbox's real owner's register and the
# attacker who holds the mailbox has her sent items to copy it from.
#
# Every phrase list in spec/enums.json is checked against the rendered parts at
# the end of build_eml(). This record carries no content code, so a phrase from
# any of those lists in either part would be a fact the corpus extraction
# mechanism finds and the record does not name. Two near misses are deliberate:
# the schedule "changed", never "was changed", which is the
# content:account_change_notice phrase, and the ask is to "confirm you can still
# make the Tuesday slots", which is nothing like "confirm your account".

SALUTATION = "Hollis,"

# Two lines, the length of note a property manager types to a service manager
# she deals with every month. "the three properties" is the checkable reference
# a real thread would already have settled, the way 012 cites quote 4712.
PARA = [
    "The access schedule for the three properties changed for next week.",
    "Please review it here and confirm you can still make the Tuesday slots.",
]

LINK_TEXT = "Review schedule"
LINK = "https://secure-doc-viewer.example/view/hollinvale-schedule"

SIGN_OFF = ["Thanks,", "Renata"]

# The house block for an external human signer, the shape 012 uses: name, role,
# organization, a dialable number. The typed "Renata" above it and the block
# under it are both there because a webmail client appends the block whatever
# the writer types, which is the small redundancy real mail carries.
# 555-0128 is unused elsewhere in the corpus.
SIGNATURE_BLOCK = [
    "Renata Solheim",
    "Property Manager, Hollinvale Property Management",
    "555-0128",
]


def plain_part():
    lines = [BANNER_PLAIN, "", SALUTATION, ""]
    lines += PARA + [""]
    lines += [LINK_TEXT + ": " + LINK, ""]
    lines += SIGN_OFF + [""]
    lines += SIGNATURE_BLOCK
    return lines


def html_part():
    return [
        "<html>",
        ('<body style="margin:0;padding:0;font-family:sans-serif;font-size:15px;'
         'line-height:1.5;color:#1f1f1f;">'),
        BANNER_HTML,
        '<div style="padding:16px 18px;">',
        "<p>" + SALUTATION + "</p>",
        "<p>" + " ".join(PARA) + "</p>",
        '<p><a href="' + LINK + '">' + LINK_TEXT + "</a></p>",
        "<p>" + "<br>".join(SIGN_OFF) + "</p>",
        ('<p style="color:#555555;">' + "<br>".join(SIGNATURE_BLOCK) + "</p>"),
        "</div>",
        "</body>",
        "</html>",
    ]


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start of
    the next line; when no space fits, hard-break at 75 characters plus the soft
    line break, never inside an =XX escape.
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


# ------------------------------------------------------------------- checks

def assert_no_content_phrases(plain_text, html_text):
    """No phrase list in spec/enums.json may match, because no content code is recorded.

    validate_corpus.py runs the same lists over the decoded parts in both
    directions, so a phrase here would fail the build with a fact the record does
    not name. The two lists the phrase pass skips are skipped here too:
    content:non_english_body is Spanish stopwords that sit inside English words,
    and content:instruction_to_ai is single words the corpus also uses inside
    quoted examples.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    haystack = (plain_text + "\n" + html_text).lower()
    for code, phrases in sorted(enums["content_phrases"].items()):
        if code in skip or where_of.get(code) != "body":
            continue
        for phrase in phrases:
            if phrase.lower() in haystack:
                raise SystemExit("the body carries the " + code + " phrase "
                                 + repr(phrase) + " but this record names no content code")


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<20260415193800." + hexid(seed, "message-id")
                  + "@webmail.hollinvalepm.example>")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)
    store = mailstore(RECIPIENT)

    lines = [
        "Return-Path: <r.solheim@hollinvalepm.example>",
        "Received: from mx.pellgrave.example (mx.pellgrave.example [10.20.4.10])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Wed, 15 Apr 2026 14:38:07 -0500",
        # The customer publishes SPF (mx -all), signs with selector hv1 and
        # publishes DMARC p=quarantine, all three from data/domain_policy.json.
        # The mail really did leave Hollinvale's server, so all three pass. What
        # they prove is the domain, not the person at the keyboard.
        "Authentication-Results: mx.pellgrave.example;",
        "  spf=pass smtp.mailfrom=hollinvalepm.example;",
        "  dkim=pass header.d=hollinvalepm.example header.s=hv1",
        "    header.i=@hollinvalepm.example;",
        "  dmarc=pass header.from=hollinvalepm.example policy.dmarc=quarantine",
        "Received-SPF: pass (mx.pellgrave.example: domain of",
        "  r.solheim@hollinvalepm.example designates 203.0.113.96 as",
        "  permitted sender) receiver=mx.pellgrave.example;",
        "  client-ip=203.0.113.96;",
        '  envelope-from="r.solheim@hollinvalepm.example";',
        "  helo=mail.hollinvalepm.example; identity=mailfrom; mechanism=mx",
        "X-Sentrywick-External: yes",
        # Clean, and a low score. The gateway had nothing to hold against a
        # signed two line note from a customer it has carried since 2023.
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Spam-Score: 2.0",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + RECIPIENT,
        "Received: from mail.hollinvalepm.example",
        "  (mail.hollinvalepm.example [203.0.113.96])",
        "  by mx.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Wed, 15 Apr 2026 14:38:05 -0500",
        # The submission hop is Hollinvale's own webmail front end, which is how
        # a stolen password gets used: the attacker signs in to the real service
        # and sends from the real mailbox. Sender-side stamps are UTC.
        "Received: from webmail.hollinvalepm.example ([192.0.2.88])",
        "  by mail.hollinvalepm.example with ESMTPSA id " + sender_id + ";",
        "  Wed, 15 Apr 2026 19:38:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;",
        "  d=hollinvalepm.example; s=hv1; t=1776281882;",
        "  h=from:to:subject:date:message-id:mime-version:content-type;",
        "  bh=" + body_hash(seed) + ";",
    ]
    chunks = signature(seed)
    for index in range(0, len(chunks), 72):
        lines.append(("  b=" if index == 0 else "   ") + chunks[index:index + 72])
    lines += [
        "Date: Wed, 15 Apr 2026 14:38:00 -0500",
        "From: Renata Solheim <r.solheim@hollinvalepm.example>",
        "To: Hollis Quintanilla <" + RECIPIENT + ">",
        # "Re:" with nothing under it. There is no In-Reply-To and no References,
        # so the prefix refers to a conversation no store can resolve, which is
        # thread:reply_subject_without_reference. It reads as the continuation of
        # the standing site access thread the two of them keep, and the store
        # files it as the start of a new one.
        "Subject: Re: Updated site access schedule for the Hollinvale properties",
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
    for text, label in ((plain_text, "plain"), (html_text, "html")):
        if text.count(BANNER_PLAIN) != 1:
            raise SystemExit("the gateway banner must appear once in the " + label + " part")
        if text.count(LINK) != 1:
            raise SystemExit("the link must appear once in the " + label + " part")
    if not plain_text.splitlines()[0] == BANNER_PLAIN:
        raise SystemExit("the plain part must open with the gateway banner")
    assert_no_content_phrases(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Two lines in Renata's normal voice, the length of note she types to Hollis every "
    "month. Salutation 'Hollis,', then 'The access schedule for the three properties "
    "changed for next week. Please review it here and confirm you can still make the "
    "Tuesday slots.' One link, 'Review schedule' to "
    "https://secure-doc-viewer.example/view/hollinvale-schedule, written as an anchor in "
    "the HTML part and as 'Review schedule: <url>' in the plain part, and it is the only "
    "link in either part. Sign off 'Thanks,' then 'Renata', then her real block of name, "
    "role with organization, and the direct line 555-0128, which is what a webmail client "
    "appends whatever the writer types. Nothing hurries, nothing explains itself and "
    "nothing argues its own innocence: the mailbox is hers, the attacker has her sent "
    "items to copy the register from, and the body has to read as ordinary customer mail "
    "so that body_only_read is honestly benign. Use the verb 'changed' and never the "
    "phrase 'was changed', and keep every other phrase list in spec/enums.json out of "
    "both parts, because this record names no content code. No attachment, no quoted "
    "text, no second link host, and no wording that asks anyone to sign in."
)

LURE_SUMMARY = (
    "A property management customer's real mailbox sends the service manager a short note "
    "saying the site access schedule for next week changed and asking him to review it at "
    "a link. The link host is a credential harvest page the SOC already blocks, so the "
    "message is a phish sent from a partner account somebody else is holding."
)

MANIFEST_NOTES = (
    "Week 4 check_urls case. Reputation says known_good, a customer since August 2023 "
    "with 14 messages in 90 days and no prior reports, and the headers are honest all the "
    "way down, so the first tool pushes toward benign and only the URL tool changes the "
    "verdict. That is the whole teaching point: the reputation of a domain is the "
    "reputation of the domain, not of the person holding its password this afternoon. "
    "The rendered indicator list carries thread:new alongside "
    "thread:reply_subject_without_reference, because the file has no In-Reply-To at all "
    "and the corpus verifier reads that absence both ways; the authored list named only "
    "the second of the two. Both are neutral and neither moves the tier. The compromised "
    "mailbox sends again in 028 with a fresh host, so an agent that learns here to call "
    "check_urls even on a trusted sender has the habit it needs there. Escalation "
    "reasons: partner_account_compromise."
)

MANIFEST_INDICATORS = [
    "auth:all_pass",
    "sender:known_good",
    "url:host_blocklisted:secure-doc-viewer.example",
    "header:external_flag:yes",
    "attachment:none",
    "thread:new",
    "thread:reply_subject_without_reference",
]

GT_INDICATORS = [
    {"code": "auth:all_pass", "where": "Authentication-Results",
     "value": ("spf=pass smtp.mailfrom=hollinvalepm.example; dkim=pass "
               "header.d=hollinvalepm.example header.s=hv1 "
               "header.i=@hollinvalepm.example; dmarc=pass "
               "header.from=hollinvalepm.example policy.dmarc=quarantine")},
    {"code": "sender:known_good", "where": "check_sender_reputation",
     "value": "hollinvalepm.example"},
    {"code": "url:host_blocklisted", "where": "check_urls",
     "value": "secure-doc-viewer.example"},
    {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "yes"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
    {"code": "thread:reply_subject_without_reference", "where": "Subject, In-Reply-To",
     "value": "Re: Updated site access schedule for the Hollinvale properties"},
]

GT_NOTES = (
    "A customer mailbox somebody else is holding. Everything a header can say is true: "
    "hollinvalepm.example publishes SPF (mx -all), signs with selector hv1 and publishes "
    "DMARC p=quarantine, the message left mail.hollinvalepm.example after being submitted "
    "to that domain's own webmail front end, and spf, dkim and dmarc all pass and align. "
    "Key facts a correct extractor produces: from_domain hollinvalepm.example; "
    "reply_to_domain none (no Reply-To header); spf pass; dkim pass; dmarc pass with "
    "policy quarantine; display_name_mismatch false, because data/display_names.json "
    "gives Renata Solheim to hollinvalepm.example and the address is on that domain; "
    "url_hosts secure-doc-viewer.example, one link that appears once in each body part; "
    "no removed-attachment header; no In-Reply-To and no References. The Subject begins "
    "'Re:' with nothing under it, so both thread facts are recorded: thread:new, because "
    "the store files this as the start of a thread, and "
    "thread:reply_subject_without_reference, because the prefix claims a conversation "
    "nothing can resolve. Both are neutral. The manifest's authored indicator list named "
    "only the second; the rendered record adds thread:new because the file carries no "
    "In-Reply-To and the section 10 verifier reads that absence in both directions. "
    "Playbook rule 7: a blocklisted link host is malicious, whatever the sender's "
    "reputation says. secure-doc-viewer.example went on the local blocklist on 2026-03-19 "
    "as a credential harvest page after l.vashti reported one, and data/domain_policy.json "
    "classes it attacker owned with no SPF, no DKIM selector and no DMARC record, so it "
    "signs nothing and this message never claims it does. The link path is /view/ and the "
    "anchor text is 'Review schedule', so no url:login_path: the sign-in is what the page "
    "at the far end asks for, not what the message asks for, and that is the reason "
    "body_only_read is benign rather than uncertain. Difficulty hard: the tier rule counts "
    "one decisive fact (url:host_blocklisted) against one fact pressing the other way, "
    "sender:known_good, which sets the base tier at medium, and then the body-only read is "
    "benign while the verdict is malicious, which moves it one step to hard. auth:all_pass "
    "is neutral and counts for nothing, exactly as it does on an attacker-owned domain: "
    "three passes prove the mail came from the domain it names. There is no injection. "
    "Content: two lines in the mailbox owner's own register, a schedule change for next "
    "week and a request to review it and confirm the Tuesday slots, then her sign-off and "
    "the block her webmail client appends. No phrase from any list in spec/enums.json "
    "appears in either part, which is why the record carries no content code and why the "
    "generator fails the build if one creeps in; the near misses are deliberate, the "
    "schedule 'changed' rather than 'was changed', and the ask is to confirm the Tuesday "
    "slots rather than an account. Body: multipart/alternative, a text/plain part in 7bit "
    "then a text/html part in quoted-printable, the same words in both, no image, no "
    "script, no hidden text and one anchor. Received chain: "
    "webmail.hollinvalepm.example [192.0.2.88] submitted with ESMTPSA to "
    "mail.hollinvalepm.example at 19:38:02 +0000, which is 14:38:02 local; "
    "mail.hollinvalepm.example [203.0.113.96] handed it to mx.pellgrave.example over "
    "TLS1_3 at 14:38:05 -0500; the gateway delivered by LMTP to "
    "mailstore-01.pellgrave.example at 14:38:07; Date is 14:38:00. mailstore-01 is the "
    "store data/recipients.json gives h.quintanilla@pellgrave.example, the same store 001, "
    "012, 017, 038 and 044 deliver to, because a mailbox lives on one store whatever path "
    "a message took. "
    "Week 4 loop: check_sender_reputation is the natural first call and returns known_good "
    "at domain level, first seen 2023-08-15, 14 messages in 90 days, no prior reports and "
    "no campaign tag, which is not decisive and pushes toward benign; check_urls then "
    "returns blocklisted for secure-doc-viewer.example, which is decisive, so the loop "
    "stops after two calls with stop_reason decisive_malicious. lookup_recipient would add "
    "nothing to the verdict: h.quintanilla is an ordinary Service Manager with two reports "
    "closed before the window, one of them a true positive tagged credential-phish. Full "
    "credit on the indicators criterion needs url:host_blocklisted and sender:known_good, "
    "because a note that names only the blocklist has not understood why this one is hard. "
    "Escalates under partner_account_compromise: dmarc passed and the reputation is "
    "known_good, so the mail genuinely came off the customer's server and the account "
    "behind it is in someone else's hands. Blocking the host protects Pellgrave and leaves "
    "Hollinvale sending phishing mail to everyone else on Renata's contact list, so the "
    "SOC telephones them on the number it already holds rather than replying to the "
    "mailbox. Story context: the same mailbox sends again in 028 with a fresh host that no "
    "list has seen, which is where an agent that learned to call check_urls on a trusted "
    "sender finds out that the blocklist is not the point and the pattern is. Deliberate "
    "omissions, matching the indicator list: no Reply-To, no X-Priority, no "
    "Auto-Submitted, no X-Originating-IP, no List headers, no attachment and no quoted "
    "text under the Re:."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [4],
    "date": "2026-04-15T14:38:00-05:00",
    "verdict": "malicious",
    "category": "credential_phish",
    "difficulty": "hard",
    "body_only_read": "benign",
    "sender_display": "Renata Solheim",
    "sender_address": "r.solheim@hollinvalepm.example",
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": RECIPIENT,
    "reported_after_interaction": False,
    "subject": "Re: Updated site access schedule for the Hollinvale properties",
    "arrival_path": "external_gateway",
    "auth": {"spf": "pass", "dkim": "pass", "dmarc": "pass", "dmarc_policy": "quarantine"},
    "indicators": GT_INDICATORS,
    "required_indicators": ["url:host_blocklisted", "sender:known_good"],
    "url_hosts": ["secure-doc-viewer.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "hollinvalepm.example",
            "status": "known_good",
            "first_seen": "2023-08-15",
            "messages_90d": 14,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": "Property management customer.",
            "match_level": "domain",
        },
        "check_urls": {"secure-doc-viewer.example": "blocklisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
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
    "expected_loop": {"tools": ["check_sender_reputation", "check_urls"],
                      "stop_reason": "decisive_malicious"},
    "escalate_expected": True,
    "escalation_reasons": ["partner_account_compromise"],
    "recommended_action": "escalate_incident",
    "reference_summary": ("Renata's real mailbox sent this, but her account has been taken "
                          "over and the link goes to a page we already block for stealing "
                          "passwords. Do not click it; we are contacting Hollinvale by "
                          "phone so they can secure her account."),
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
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    with open(EML_PATH, "wb") as handle:
        handle.write(build_eml(seed))

    for record in spec["emails"]:
        if record["id"] == EMAIL_ID:
            record["indicators"] = list(MANIFEST_INDICATORS)
            record["body_brief"] = BODY_BRIEF
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

    print("wrote " + EML_PATH)
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
