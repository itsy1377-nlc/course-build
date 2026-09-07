#!/usr/bin/env python3
"""Regenerate 029-ceo-gift-cards.

Renders emails/batch/029-ceo-gift-cards.eml from the corpus seed, refreshes the
prose fields of its own manifest record in spec/corpus-spec.json, and upserts
its ground truth record in ground_truth.json. It touches no other record and no
data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n)  = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = sha256("<seed>|<id>|<label>|<block>") for block 0, 1 ...
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_lmw_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    webmail Received id   = hex("sender-id", 12)
    store LMTP id         = UUID(hex=sha256("<seed>|<id>|store-id")[:32],
                            version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    DKIM t=               = the sender-side Received timestamp in epoch seconds

Nothing here is a literal the seed cannot explain except the mail store, which
is read back from data/recipients.json: a mailbox lives on exactly one store,
so the LMTP hop is a property of the recipient rather than of the path the
message arrived on (docs/email-header-realism.md sec. 7).

Two conventions in this file follow the webmail provider rather than the
generic derivation the corpus-wide note states, and both follow 021, the only
other rendered Lanternmail message:

  * The boundary prefix is "=_lmw_", not the "=_swk_" our own submission host
    writes. The boundary belongs to the client that composed the message, and
    this one was composed in Lanternmail webmail. The same reasoning puts the
    Message-ID right side on the webmail front end named in the innermost
    Received hop and stamps that hop in UTC while the gateway and the store
    stamp in -0500.
  * The Lanternmail SMTP id is twelve hex digits, not eight. An id's width is a
    property of the MTA that writes it, and smtp-out-04.lanternmail.example
    already writes twelve in 021. An eight digit id here would put two widths
    on one host inside one corpus, which is the kind of detail an analyst reads
    a Received chain for.

Neither DKIM value verifies. They are seeded bytes of the right length, the
same convention the rest of the corpus uses, because no .example domain can
publish a key and no lab checks a signature. That is the point of this record:
SPF, DKIM and DMARC all pass and prove only that the mail really came from the
webmail provider, never that the person named in the display name wrote it.

Why the message looks the way it does. It is the follow-through to 009's
pretext: the same operator, the same webmail provider, the same client address
in X-Originating-IP (203.0.113.88), and this time the ask. The From address
adaeze.whitcombe.office@lanternmail.example is the one b.onwuka reported on
2026-03-31, so data/sender_reputation.json holds it at address level with
status known_bad and the campaign tag ceo-impersonation, while the provider
domain lanternmail.example stays neutral. That address level override is the
week 7 lesson in this file: one call to check_sender_reputation is decisive and
the loop stops, which is why expected_loop names one tool and stop_reason is
decisive_malicious.

The body carries no excuse for the outside address, unlike 021 and 009. The
pretext already explained it two days earlier, and a second explanation would
add content:excuse_for_external_address, which this record does not carry.

Run:  python3 corpus/tools/generators/gen_029_ceo_gift_cards.py
"""

import base64
import calendar
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "029-ceo-gift-cards"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER_DISPLAY = "Adaeze Whitcombe"
SENDER = "adaeze.whitcombe.office@lanternmail.example"
RECIPIENT = "b.onwuka@pellgrave.example"
RECIPIENT_DISPLAY = "Beatrix Onwuka"
REPORTER = RECIPIENT
SUBJECT = "Need this done today"

# The path in the manifest's received_path_hint, host by host. The webmail
# front end at the bottom of the chain is not named in the hint, so it is named
# here: a provider runs a pool of them, and this one is not the node 021 came
# through. Both addresses sit in RFC 5737 documentation blocks.
WEBAPP_HOST = "webapp-07.lanternmail.example"
WEBAPP_IP = "192.0.2.57"
PROVIDER_SMTP = "smtp-out-04.lanternmail.example"
PROVIDER_IP = "198.51.100.77"
GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"
# The client address the webmail front end recorded. It is the same address
# 009 carries, which is what ties the two messages to one operator.
ORIGINATING_IP = "203.0.113.88"

SCAN_RESULT = "clean"
SPAM_SCORE = "3.9"

# Date is 2026-04-22T08:21:00-05:00. The webmail node stamps its hop in UTC,
# two seconds later; the gateway and the store stamp in -0500.
DATE_HEADER = "Wed, 22 Apr 2026 08:21:00 -0500"
SENDER_HOP_TIME = "Wed, 22 Apr 2026 13:21:02 +0000"
GATEWAY_HOP_TIME = "Wed, 22 Apr 2026 08:21:05 -0500"
STORE_HOP_TIME = "Wed, 22 Apr 2026 08:21:07 -0500"
MESSAGE_ID_STAMP = "20260422132102"
DKIM_T = calendar.timegm((2026, 4, 22, 13, 21, 2, 0, 0, 0))

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break. Only the HTML part is encoded here, and its long
# lines are a style attribute and a sentence, neither improved by breaking at a
# space, so the wrap is a hard cut that steps back off an "=XX" escape.
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
# Each paragraph is written once, as the lines of the plain part. The HTML part
# joins the same lines with single spaces, so the two parts cannot drift and
# the HTML part hides nothing: a diff of the decoded text is empty apart from
# the tags.
#
# The wording carries the four content codes the record lists, and every line
# break is placed so that no phrase from spec/enums.json is split across a
# line, because validate_corpus.py looks for each phrase whole in the decoded
# part:
#
#   content:gift_card_request     "gift cards", on one line.
#   content:urgency_keywords      "this morning" and "today", each on one line.
#   content:secrecy_request       "between us" and "surprise", one line each.
#   content:channel_restriction   "cannot take a call", on one line.
#
# The wording also stays clear of every other phrase list, because the phrase
# pass runs both ways and a stray phrase is a fact the record does not carry:
# no "personal address", "acting up" or "not working"
# (content:excuse_for_external_address, and the pretext in 009 already did that
# work); no "call me" (content:phone_verification_offered), which would hand
# the assistant the callback the message exists to prevent; no "invoice" or
# "remit" (content:payment_request); no "pay today" or "today's run"
# (content:payment_timing_request); no "new account" or "new bank"
# (content:payment_change_request); no "wire" (content:banking_instruction); no
# "download" (content:file_share_lure).
#
# There is no link and no attachment, which is what url:none and
# attachment:none key on. It is also what makes the message look ordinary: an
# assistant reads a short note from her own chief executive, and nothing in it
# is a file to open or a page to sign into.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# First name only. Whoever wrote this knows that Beatrix Onwuka keeps the chief
# executive's calendar, and a note between those two would never open with a
# surname or a title.
GREETING = "Beatrix,"

# The occasion, before the ask. A reason a reader can picture is what carries a
# gift card request: eight guests, one lunch, a round number for each of them.
PARA_1 = [
    "I need a favor this morning. We are hosting eight customer guests at",
    "Friday's client appreciation lunch, and I want to hand each of them a",
    "card for 200 dollars.",
]

# The ask, and the part that keeps it off the company's books: the assistant's
# own card, with a reimbursement promised for a run that has not happened yet.
PARA_2 = [
    "Can you pick up the eight gift cards today and put them on your own",
    "card? Finance will reimburse you on next week's expense run.",
]

# The theft. Scratching the panel and photographing the code hands over the
# money itself, and it is the sentence that separates this from an errand.
PARA_3 = [
    "When you have them, scratch the panel off the back of each card and",
    "email me photos of the codes. I need the code and the serial number",
    "readable in the picture so I can get them loaded before Friday.",
]

# The secrecy, dressed as thoughtfulness. A surprise is the one reason a chief
# executive could give for asking an assistant not to mention a purchase.
PARA_4 = [
    "Please keep this between us. The cards are a surprise and I do not",
    "want them turning up on an invitation before the lunch.",
]

# The closed channel. The conference is real, which is what makes it work: the
# assistant knows her own calendar says the same thing.
PARA_5 = [
    "I am in sessions all day and cannot take a call until this evening,",
    "so this is the quickest way to reach me.",
]

# The close the manifest asks for: a first name, no title, no extension. A
# signature block with a telephone number would give the assistant the one move
# that ends the attack, so the message does not offer it.
CLOSING = "Thank you,"
SIGN_OFF = "Adaeze"


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    for paragraph in (PARA_1, PARA_2, PARA_3, PARA_4, PARA_5):
        lines += paragraph + [""]
    lines += [CLOSING, SIGN_OFF]
    return lines


def html_part():
    """The same words, in the plain paragraphs a webmail client writes."""
    lines = [
        BANNER_HTML,
        '<div style="font-family:sans-serif;font-size:14px;color:#222222">',
        "<p>" + GREETING + "</p>",
    ]
    for paragraph in (PARA_1, PARA_2, PARA_3, PARA_4, PARA_5):
        lines.append("<p>" + " ".join(paragraph) + "</p>")
    lines += ["<p>" + CLOSING + "<br>", SIGN_OFF + "</p>", "</div>"]
    return lines


# ------------------------------------------------------- quoted-printable

def qp_wrap(line):
    """Fold one logical line into quoted-printable physical lines.

    A hard break at QP_MAX - 1 characters plus the soft line break, stepping
    back so a break never lands inside an "=XX" escape.
    """
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


def qp_body(lines):
    out = []
    for line in lines:
        out += qp_wrap(line)
    return out


# ------------------------------------------------------------------- render

def build_eml(seed):
    boundary = "=_lmw_" + hexid(seed, "boundary")
    message_id = "<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id") + "@" + WEBAPP_HOST + ">"
    gateway_id = hexid(seed, "gateway-id")
    webmail_id = hexid(seed, "sender-id")
    lmtp_id = store_id(seed)
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    store = mailstore(RECIPIENT)

    lines = [
        # A webmail account sends its own bounces, so the envelope sender is
        # the From mailbox and there is no Sender header.
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_HOP_TIME,
        # The gateway writes Authentication-Results above its own trace fields
        # (RFC 8601 sec. 4). All three pass for lanternmail.example, and that
        # is the trap: the provider really did send this, and authentication
        # says nothing at all about who wrote it.
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=lanternmail.example;",
        "  dkim=pass header.d=lanternmail.example header.s=lm2026a",
        "  header.i=@lanternmail.example;",
        "  dmarc=pass header.from=lanternmail.example policy.dmarc=quarantine",
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + SENDER + " designates " + PROVIDER_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + PROVIDER_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + PROVIDER_SMTP + "; identity=mailfrom;",
        "  mechanism=ip4:198.51.100.64/26",
        # The gateway's own verdict, in headers. Nothing in the body contradicts
        # it and nothing in the body imitates it; this record carries no
        # injection.
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + PROVIDER_SMTP,
        "  (" + PROVIDER_SMTP + " [" + PROVIDER_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_HOP_TIME,
        "Received: from " + WEBAPP_HOST + " ([" + WEBAPP_IP + "])",
        "  by " + PROVIDER_SMTP + " (Lanternmail SMTP) with ESMTPSA",
        "  id " + webmail_id + "; " + SENDER_HOP_TIME,
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
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # A webmail client stamps the composing browser's address. It is a
        # consumer address in 203.0.113.0/24 rather than one of the provider's
        # own, and header:x_originating_ip is a recorded fact, not decoration.
        "X-Originating-IP: [" + ORIGINATING_IP + "]",
        "X-Mailer: Lanternmail Web",
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        # The plain part is pure ASCII under 78 characters a line, so it stays
        # 7bit (docs/email-header-realism.md sec. 2). The HTML part carries the
        # gateway's banner snippet, which is longer than 78, so that part is
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
    lines += qp_body(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Five short paragraphs in the chief executive's voice, opening 'Beatrix,'. "
    "Ask a favor 'this morning': eight customer guests are coming to Friday's "
    "client appreciation lunch and each is to get a card for 200 dollars. Ask "
    "her to pick up the eight 'gift cards' 'today' and put them on her own "
    "card, with Finance reimbursing her on next week's expense run. Then the "
    "theft: scratch the panel off the back of each card and email photos of "
    "the codes, with the code and the serial number readable. Then the "
    "secrecy: keep this 'between us' because the cards are a 'surprise'. Then "
    "the closed channel: in sessions all day and 'cannot take a call' until "
    "this evening, so this address is the quickest way to reach her. No "
    "client, vendor or project is named, so the body hands the week 7 loop "
    "nothing to look up beyond the sender; no link, no attachment, and no "
    "excuse for the outside address, because 009's pretext already gave one "
    "two days earlier. Close with 'Thank you,' and the name Adaeze, with no "
    "title and no extension: a telephone number would end the attack."
)

LURE_SUMMARY = (
    "Someone using the CEO's name asks her assistant to buy eight gift cards "
    "for a client appreciation event, scratch the backs, and email photos of "
    "the codes. It asks her to keep it quiet as a surprise and says the CEO "
    "is in sessions all day."
)

MANIFEST_NOTES = (
    "The follow-through to 009's pretext, from the webmail address b.onwuka "
    "reported on 2026-03-31, so check_sender_reputation returns known_bad at "
    "the address level while the provider domain stays neutral (the "
    "address-level override). Rendered with the same client address as 009, "
    "X-Originating-IP [203.0.113.88], which is what ties the two messages to "
    "one operator; the message arrived through the gateway with a clean scan "
    "and a spam score of 3.9, and it carries no link, no attachment, no "
    "In-Reply-To and no Reply-To. Escalation reasons: "
    "financial_or_endpoint_impact, executive_target."
)

# ------------------------------------------------------------- ground truth

AUTH_VALUE = (
    "spf=pass smtp.mailfrom=lanternmail.example; dkim=pass "
    "header.d=lanternmail.example header.s=lm2026a "
    "header.i=@lanternmail.example; dmarc=pass "
    "header.from=lanternmail.example policy.dmarc=quarantine"
)

REFERENCE_SUMMARY = (
    "This is the same gift-card scam you reported in March, from the same "
    "webmail address using Adaeze's name. Do not buy anything, and thank you "
    "for catching it again."
)

NOTES = (
    "Gift card business email compromise, the week 7 batch case where one tool "
    "call settles it. Key facts: the display name Adaeze Whitcombe is the "
    "company's real Chief Executive Officer, whose address is "
    "a.whitcombe@pellgrave.example, while the From address is "
    "adaeze.whitcombe.office@lanternmail.example on a free webmail provider; "
    "no Reply-To; SPF, DKIM and DMARC all pass for lanternmail.example, which "
    "publishes a quarantine policy, and that pass proves only that the mail "
    "really came from that provider; X-Originating-IP [203.0.113.88] is the "
    "webmail user's client address and is the same address 009 carries, which "
    "is what ties the two messages to one operator; the message arrived "
    "through the gateway (X-Sentrywick-External: yes) with a clean scan and a "
    "spam score of 3.9; there is no link, no removed attachment and no "
    "In-Reply-To. Difficulty medium by the tier rule: two decisive facts "
    "(sender:display_name_matches_employee and sender:known_bad) against one "
    "pressure point (no link and no attachment, so check_urls has nothing to "
    "check), which is decisive over pressure without a tie, and neither "
    "adjustment applies because there is no injection and the body-only read "
    "already lands on malicious. Playbook rules that decide the case: rule 2, "
    "an employee's name over an address outside pellgrave.example is "
    "impersonation until a phone call proves otherwise, and rule 6, executives "
    "do not ask for gift cards, wire transfers or secrecy by email. This "
    "message asks for two of the three. Body signals: the "
    "ask is eight gift cards on the assistant's own card with a reimbursement "
    "promised later, the codes are to be scratched and photographed, which is "
    "the money itself rather than an errand, the matter is to stay between "
    "the two of them as a surprise, and the sender rules out the telephone "
    "for the day. The close is a first name with no title and no extension, "
    "because a telephone number in the signature would hand the assistant the "
    "one move that ends the attack. No client, vendor or project is named in "
    "the body, so nothing in it resolves to a domain, an address or a link, "
    "and the loop is left with the sender and nothing else. Tools: "
    "check_sender_reputation matches at address level and returns known_bad, "
    "first seen 2026-03-31, one prior report, last verdict malicious, "
    "campaign tag ceo-impersonation, so the loop stops on decisive_malicious "
    "after one call; the provider domain lanternmail.example would have "
    "returned neutral, and the address record overriding the domain record is "
    "the lesson this file carries. lookup_recipient would show Beatrix Onwuka "
    "is the Executive Assistant to the CEO with the executive flag, four "
    "reports and three true positives in 90 days, and check_urls has nothing "
    "to look up, but neither is needed once the sender comes back known_bad. "
    "recipient:prior_similar_report follows the prior_similar_report_rule: "
    "content:gift_card_request implies ceo-impersonation and "
    "cfo-impersonation, the sender record's ceo-impersonation tag is added, "
    "and the mailbox holds a ceo-impersonation report, so that is the value. "
    "Expected action: escalate_incident with reasons "
    "financial_or_endpoint_impact, because a malicious BEC always escalates, "
    "and executive_target, because Beatrix carries the executive flag. She "
    "reported the message before acting on it, so user_interacted does not "
    "apply. The correct close is to confirm with Adaeze's office by telephone, "
    "block the address, and tell Beatrix that nothing should be purchased."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-22T08:21:00-05:00",
    "verdict": "malicious",
    "category": "bec",
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
    "auth": {
        "spf": "pass",
        "dkim": "pass",
        "dmarc": "pass",
        "dmarc_policy": "quarantine",
    },
    "indicators": [
        {"code": "auth:all_pass", "where": "Authentication-Results",
         "value": AUTH_VALUE},
        {"code": "sender:display_name_matches_employee", "where": "From",
         "value": "Adaeze Whitcombe"},
        {"code": "sender:freemail_domain", "where": "check_sender_reputation",
         "value": "lanternmail.example"},
        {"code": "sender:known_bad", "where": "check_sender_reputation",
         "value": "adaeze.whitcombe.office@lanternmail.example"},
        {"code": "header:x_originating_ip", "where": "X-Originating-IP",
         "value": "[203.0.113.88]"},
        {"code": "content:gift_card_request", "where": "body",
         "value": "gift cards"},
        {"code": "content:secrecy_request", "where": "body",
         "value": "between us; surprise"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "this morning; today"},
        {"code": "content:channel_restriction", "where": "body",
         "value": "cannot take a call"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "yes"},
        {"code": "url:none", "where": "body", "value": None},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:executive", "where": "lookup_recipient",
         "value": "b.onwuka@pellgrave.example"},
        {"code": "recipient:prior_similar_report", "where": "lookup_recipient",
         "value": "ceo-impersonation"},
    ],
    "required_indicators": [
        "content:gift_card_request",
        "sender:display_name_matches_employee",
    ],
    "url_hosts": [],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "address": SENDER,
            "status": "known_bad",
            "first_seen": "2026-03-31",
            "messages_90d": 1,
            "prior_reports": 1,
            "last_report_verdict": "malicious",
            "last_report_date": "2026-03-31",
            "campaign_tag": "ceo-impersonation",
            "new_domain": True,
            "notes": ("Reported by b.onwuka on 2026-03-31 (CEO impersonation); "
                      "lanternmail.example is a free webmail provider and its "
                      "domain reputation stays neutral."),
            "match_level": "address",
        },
        "check_urls": {},
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
        "tools": ["check_sender_reputation"],
        "stop_reason": "decisive_malicious",
    },
    "escalate_expected": True,
    "escalation_reasons": ["financial_or_endpoint_impact", "executive_target"],
    "recommended_action": "escalate_incident",
    "reference_summary": REFERENCE_SUMMARY,
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": NOTES,
}


# ------------------------------------------------------------------- checks

def check_no_stray_phrases(spec, plain, html_source):
    """Refuse to write a body that carries a phrase the record does not claim.

    validate_corpus.py runs the spec/enums.json phrase lists both ways over the
    decoded parts, so one stray phrase turns into a failure that reads as a
    labelling error rather than as a wording accident. Checking it here names
    the phrase and the code while the body is still in front of the author.
    """
    enums_path = os.path.join(CORPUS, "spec", "enums.json")
    with open(enums_path, encoding="utf-8") as handle:
        enums = json.load(handle)
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    # The two lists that are not membership tests; validate_corpus.py skips
    # them for the same reason.
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    claimed = {item["code"] for item in GROUND_TRUTH["indicators"]}
    body = (plain + "\n" + html_source).lower()
    for code, phrases in sorted(enums["content_phrases"].items()):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases if phrase.lower() in body]
        if hits and code not in claimed:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + " but the record does not list "
                             + code)
        if code in claimed and not hits:
            raise SystemExit("the record lists " + code
                             + " but no phrase from its list appears in the body")
    for item in GROUND_TRUTH["indicators"]:
        phrases = enums["content_phrases"].get(item["code"])
        if item["code"] in skip or not phrases or not item["value"]:
            continue
        known = {phrase.lower() for phrase in phrases}
        for part in item["value"].split("; "):
            if part.lower() not in known:
                raise SystemExit(item["code"] + " records the value " + repr(part)
                                 + ", which is not an entry in its phrase list")
            if part.lower() not in body:
                raise SystemExit(item["code"] + " records the value " + repr(part)
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
    for key in ("subject", "sender_address", "sender_display", "recipient",
                "reporter", "verdict", "category", "difficulty", "set"):
        if record[key] != GROUND_TRUTH[key]:
            raise SystemExit(key + " does not match the manifest: "
                             + repr(record[key]) + " against " + repr(GROUND_TRUTH[key]))
    if record["injection"] is not None:
        raise SystemExit("the manifest now carries an injection; this generator renders none")
    if record["url_hosts"] or record["attachment"] is not None:
        raise SystemExit("the manifest now carries a link or an attachment")

    data = build_eml(seed)
    os.makedirs(os.path.dirname(EML_PATH), exist_ok=True)
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
    plain = None
    html_source = None
    for part in parsed.walk():
        if part.get_content_type() == "text/plain" and plain is None:
            plain = part.get_content()
        elif part.get_content_type() == "text/html" and html_source is None:
            html_source = part.get_content()
    if plain is None or html_source is None:
        raise SystemExit("the rendered message is missing a body part")
    if BANNER_PLAIN not in plain or BANNER_PLAIN not in html_source:
        raise SystemExit("the gateway banner did not survive the encoding")
    check_no_stray_phrases(spec, plain, html_source)

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
