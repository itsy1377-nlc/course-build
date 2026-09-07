#!/usr/bin/env python3
"""Regenerate 045-job-applicant-portfolio.

Rebuilds emails/batch/045-job-applicant-portfolio.eml byte for byte from the
corpus seed, refreshes the prose fields of the matching manifest record in
spec/corpus-spec.json, and upserts the ground truth record in
ground_truth.json. It touches no other record and no data file.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n)  = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    stream(label, n) = sha256("<seed>|<id>|<label>|<block>") for block 0, 1 ...
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_lmw_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    webmail Received id   = hexid("sender-id", 12)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)
    DKIM bh=              = base64(sha256("<seed>|<id>|dkim-bh"))
    DKIM b=               = base64(stream("dkim-b", 256))
    DKIM t=               = the sender-side Received timestamp in epoch seconds

Two of those come from the sending platform rather than from the generic
table, and they are the ones 009-ceo-are-you-available and
021-direct-deposit-change-request already use, because this message was
composed in a browser on the same webmail product:

  * the boundary prefix is "=_lmw_", the Lanternmail Web client's own, not the
    "=_swk_" the organization's submission host writes;
  * the webmail hop's Received id is twelve hex digits, the width a Lanternmail
    SMTP host writes, not the eight an attacker's own submission host writes
    elsewhere in the corpus. One product, one id format.

Nothing in this file is a literal the seed cannot explain, except the values
read back from the data files: data/recipients.json gives mailstore-01 as the
one store that holds hr@pellgrave.example, and the Lanternmail SPF range,
selector and DMARC policy in the Authentication-Results block are the ones
data/domain_policy.json publishes for lanternmail.example.

Neither DKIM value verifies. They are seeded bytes of the right length (44
base64 characters of body hash, 344 of signature), because no .example domain
can publish a key and no lab checks a signature. That the three checks pass
and still settle nothing is half of what this record teaches: the pass names
lanternmail.example, a free webmail provider, and says nothing at all about
the person whose name is on the message.

Why the header block looks the way it does. The message arrives through the
border gateway, so it carries Authentication-Results, Received-SPF and
X-Sentrywick-External: yes, and the gateway inserts its banner into both
parts. The chain is the three hops the manifest's received_path_hint fixes:
webapp-05.lanternmail.example hands the message to
smtp-out-02.lanternmail.example [198.51.100.71], which is inside the
ip4:198.51.100.64/26 that lanternmail.example publishes, so spf=pass with
mechanism=ip4:198.51.100.64/26; the gateway takes it over TLS; the store
delivers it to the mailbox by LMTP. The sender side stamps UTC and the two
organization hops stamp -0500, which is why the middle Received line is dated
the 22nd while Date is the evening of the 21st. Message-ID names the composing
front end at the bottom of the chain, the convention
docs/email-header-realism.md section 1 states.

The recipient is the shared HR mailbox and the reporter is the person who
works it, so the LMTP hop names the store recipients.json gives
hr@pellgrave.example and the "for" clause carries the shared address. A shared
mailbox is not a distribution list: it is one mailbox on one store, so there
is no list expansion to reason about and X-Sentrywick-Reported-By names
Tobias Nkemelu, the named person who pulled the copy.

Headers deliberately present or absent, matching the manifest indicator list:
X-Originating-IP and X-Mailer are there because a webmail provider records the
composing client and stamps its own name, and header:x_originating_ip is a
listed indicator; there is no Reply-To, no Auto-Submitted, no X-Priority, no
list header and no X-Sentrywick-Removed-Attachment, because the record lists
attachment:none and nothing else.

A note on the body. The record lists no content indicator at all, and
tools/validate_corpus.py runs the spec/enums.json phrase lists in both
directions, so a stray "today", "download", "call me", "personal address" or
"new account" would add a fact the answer key denies and fail the file.
check_no_stray_phrases() below refuses to write the file when one appears.
That constraint is also the reason the applicant offers "a call at whatever
time works for your team" rather than asking anyone to call her, and says her
samples are "on my own site" rather than at a personal address.

Run:  python3 corpus/tools/generators/gen_045_job_applicant_portfolio.py
"""

import base64
import calendar
import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "045-job-applicant-portfolio"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER_DISPLAY = "Oona Adebayo-Ferris"
SENDER = "oona.adebayo.ferris@lanternmail.example"
SENDER_DOMAIN = "lanternmail.example"
RECIPIENT = "hr@pellgrave.example"
REPORTER = "t.nkemelu@pellgrave.example"
SUBJECT = "Application: Service Coordinator (posting SC-0426)"

# The webmail provider's hosts. 198.51.100.71 is inside the
# ip4:198.51.100.64/26 that domain_policy.json publishes for
# lanternmail.example, and 192.0.2.55 is the provider's own private-facing
# front end; both are RFC 5737 documentation addresses and neither routes.
WEBAPP_HOST = "webapp-05.lanternmail.example"
WEBAPP_IP = "192.0.2.55"
RELAY_HOST = "smtp-out-02.lanternmail.example"
RELAY_IP = "198.51.100.71"
SPF_MECHANISM = "ip4:198.51.100.64/26"
DKIM_SELECTOR = "lm2026a"
GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

# The composing browser's address, the value the manifest's
# received_path_hint fixes. A consumer address in 203.0.113.0/24, not the
# provider's own range, because it is the applicant's home connection.
ORIGINATING_IP = "[203.0.113.140]"

SCAN_RESULT = "clean"
SPAM_SCORE = "3.5"

# The sender-side hop stamps 00:48:02 UTC on 22 April, which is the 19:48:02
# -0500 of 21 April that the gateway would have written. The DKIM t= tag is
# that instant in epoch seconds, so the signature and the chain cannot drift.
DKIM_T = calendar.timegm((2026, 4, 22, 0, 48, 2, 0, 0, 0))

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters counting
# the trailing soft break.
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
    """The one store that delivers this mailbox, from data/recipients.json.

    The recipient is a shared mailbox rather than a distribution list, so it
    is one mailbox on one store: the copy the corpus keeps is the copy
    delivered to the To address and there is no expansion to account for.
    """
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            store = record.get("mailstore")
            if not store:
                raise SystemExit("recipients.json has no mailstore for " + address)
            return store
    raise SystemExit("recipients.json has no record for " + address)


def open_posting(mailbox):
    """The posting this application answers, from data/recipients.json.

    The subject cites a posting number, and a number that named nothing would
    be a fact a student could check and find missing. recipients.json records
    one open posting against the HR mailbox; this reads it back rather than
    typing it here, and the render fails if the two ever disagree.
    """
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients.get("open_job_postings", []):
        if record.get("mailbox") == mailbox:
            return record
    raise SystemExit("recipients.json records no open posting for " + mailbox)


# ---------------------------------------------------------------- body text
#
# A real application, written in the evening from a free webmail account by a
# private person who has no company domain to write from. Five short
# paragraphs, one link, a signature with a dialable number, and nothing to act
# on: no deadline, no attachment, no sign-in, no ask beyond being read.
#
# The record lists no content indicator, so every phrase list in
# spec/enums.json has to miss. That is a live constraint on the wording rather
# than a formality: "today", "download", "personal address", "call me" and
# "new account" are all phrases an application like this would reach for, and
# each one would add a content code the answer key denies.
#
# Line breaks in the plain part sit under 78 characters, so the part stays
# 7bit (docs/email-header-realism.md sec. 2). The HTML part carries the fixed
# gateway banner snippet, which is longer than 78, so that part is
# quoted-printable.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

# No name, because the careers page gives a shared mailbox and not a person.
GREETING = "Hello,"

# The posting number is the checkable reference every legitimate first-contact
# message in the corpus carries, the way 012 cites quote 4712 and 011 cites
# PO 20431. This one is checkable for real: recipients.json records posting
# SC-0426 for the Service Coordinator against the HR mailbox, and
# open_posting() reads it back before the file is written.
PARA_1 = [
    "I am applying for the Service Coordinator opening, posting SC-0426. I",
    "saw it on your careers page earlier this month, and it lines up almost",
    "exactly with the work I do now.",
]

# The experience the brief asks for, in the register a dispatcher writes.
# The second sentence is a fragment on purpose; real mail has them, and a
# paragraph of four clean sentences would read assembled rather than typed.
PARA_2 = [
    "I have spent four years as the dispatcher at Thornbeck Plumbing, running",
    "the daily board for eleven service trucks. Intake, routing, permit",
    "paperwork, parts runs, and the part nobody puts in a posting, which is",
    "calling a customer back when a technician is going to run late and then",
    "making the new window stick.",
]

# Why there is no attachment. One sentence, stated as a fact about the posting
# rather than as an argument for the message being safe: this record is hard
# on purpose, and a body that reassured the reader would hand a small model
# the confident benign read the difficulty rule is built to withhold.
PARA_3 = [
    "Rather than send an attachment I keep work samples on my own site, since",
    "the posting asked for a link:",
]

LINK = "https://oona-adebayo-ferris.example/work"

# What is behind the link, said plainly. The host is on neither list, which is
# the whole difficulty of the email, and nothing in the body can settle that
# either way.
PARA_4 = [
    "Two of the dispatch boards I rebuilt are on there, a route sheet with the",
    "customer names taken out, and a short write up of how we brought our",
    "repeat visit rate down over one season.",
]

# References on request, and an offer to talk. "at whatever time works for
# your team" rather than "call me", which is a content:phone_verification_
# offered phrase this record does not list.
PARA_5 = [
    "References are available on request, including my last two supervisors at",
    "Thornbeck. I am glad to talk any of it through at whatever time works for",
    "your team.",
]

CLOSING = "Thank you for your time,"

# A private person signs a name and a number and nothing else: she has no
# role, no organization and no extension to give. 555-0176 is inside the
# reserved 555-01xx block and is used by no other message in the corpus.
SIGNATURE = [
    "Oona Adebayo-Ferris",
    "555-0176",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, "", GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += PARA_3 + [""]
    lines += [LINK, ""]
    lines += PARA_4 + [""]
    lines += PARA_5 + [""]
    lines += [CLOSING, ""]
    lines += SIGNATURE
    return lines


def html_part():
    """The same words in the plain paragraphs a webmail client writes.

    Lanternmail Web is a browser client, not a marketing template engine, so
    there is no wrapper table, no button and no colour: one banner, one div,
    and a paragraph per paragraph. The link is an anchor whose text is the
    address it goes to, so the HTML hides nothing the plain part shows.
    """
    return [
        BANNER_HTML,
        '<div style="font-family:sans-serif;font-size:14px;color:#222222">',
        "<p>" + GREETING + "</p>",
        "<p>" + joined(PARA_1) + "</p>",
        "<p>" + joined(PARA_2) + "</p>",
        "<p>" + joined(PARA_3) + "</p>",
        '<p><a href="' + LINK + '">' + LINK + "</a></p>",
        "<p>" + joined(PARA_4) + "</p>",
        "<p>" + joined(PARA_5) + "</p>",
        "<p>" + CLOSING + "</p>",
        "<p>" + "<br>".join(SIGNATURE) + "</p>",
        "</div>",
    ]


# ------------------------------------------------------- quoted-printable

def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits and carry the space to the start
    of the next line, so no physical line ends in white space (RFC 2045 sec.
    6.7 rule 3); when no space fits, hard-break at 75 characters, stepping
    back so the break never lands inside an "=XX" escape.
    """
    text = line.replace("=", "=3D")
    out = []
    while len(text) > QP_MAX:
        cut = text.rfind(" ", 1, QP_MAX)
        if cut <= 0:
            cut = QP_MAX - 1
            while text[cut - 2:cut - 1] == "=" or text[cut - 3:cut - 2] == "=":
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
    message_id = ("<20260422004802." + hexid(seed, "message-id")
                  + "@" + WEBAPP_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    webmail_id = hexid(seed, "sender-id")
    lmtp_id = store_id(seed)
    signature = base64.b64encode(stream(seed, "dkim-b", 256)).decode("ascii")
    store = mailstore(RECIPIENT)

    lines = [
        # A webmail account sends its own bounces, so the envelope sender is
        # the From mailbox: no Return-Path split, no Sender, no Reply-To.
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Tue, 21 Apr 2026 19:48:07 -0500",
        # The gateway writes Authentication-Results above its own trace fields
        # (RFC 8601 sec. 4). All three pass for lanternmail.example, which
        # publishes a quarantine policy. The pass is honest and useless: the
        # provider really did send this, and that names no person.
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=pass smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=pass header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR,
        "  header.i=@" + SENDER_DOMAIN + ";",
        "  dmarc=pass header.from=" + SENDER_DOMAIN + " policy.dmarc=quarantine",
        "Received-SPF: pass (" + GATEWAY_HOST + ": domain of",
        "  " + SENDER + " designates " + RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + RELAY_IP + ";",
        '  envelope-from="' + SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom;",
        "  mechanism=" + SPF_MECHANISM,
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  Tue, 21 Apr 2026 19:48:05 -0500",
        # The composing front end handing the message to the provider's
        # outbound host over an authenticated session, stamped in UTC.
        # Nothing below this line is ours.
        "Received: from " + WEBAPP_HOST + " ([" + WEBAPP_IP + "])",
        "  by " + RELAY_HOST + " (Lanternmail SMTP) with ESMTPSA",
        "  id " + webmail_id + "; Wed, 22 Apr 2026 00:48:02 +0000",
        "DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=" + SENDER_DOMAIN + ";",
        "  s=" + DKIM_SELECTOR + "; t=" + str(DKIM_T) + ";",
        "  h=from:to:subject:date:message-id:mime-version:content-type:",
        "   x-originating-ip:x-mailer;",
        "  bh=" + body_hash(seed) + ";",
    ]
    for index in range(0, len(signature), 72):
        chunk = signature[index:index + 72]
        lines.append(("  b=" if index == 0 else "   ") + chunk)
    lines += [
        "Date: Tue, 21 Apr 2026 19:48:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT,
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # The webmail client stamps the composing browser's address and its
        # own name. Both are signed, which is why they are in the DKIM h=.
        "X-Originating-IP: " + ORIGINATING_IP,
        "X-Mailer: Lanternmail Web",
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
    lines += encode(html_part())
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part())
    html_text = "\n".join(html_part())
    if plain_text.count(BANNER_PLAIN) != 1 or html_text.count(BANNER_PLAIN) != 1:
        raise SystemExit("the gateway banner must appear once in each part")
    if LINK not in plain_text or LINK not in html_text:
        raise SystemExit("both parts must carry the portfolio link")
    if "http" in plain_text.replace(LINK, "") or "http" in html_text.replace(LINK, ""):
        raise SystemExit("this message carries exactly one link")
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "A polite application in five short paragraphs and a signature. She is "
    "applying for the Service Coordinator opening, posting SC-0426, seen on "
    "the careers page earlier in the month; she has spent four years as the "
    "dispatcher at Thornbeck Plumbing running the daily board for eleven "
    "service trucks, covering intake, routing, permit paperwork, parts runs "
    "and the callbacks when a technician runs late; and rather than send an "
    "attachment she keeps work samples on her own site at "
    "https://oona-adebayo-ferris.example/work, which is what the posting "
    "asked for. She closes by offering references on request and a talk at "
    "whatever time suits the team. No deadline, no attachment, no sign-in "
    "and no ask beyond being read: the body carries no phrase from any "
    "content list in spec/enums.json, because this record lists no content "
    "indicator and tools/validate_corpus.py runs those lists both ways, so "
    "'today', 'download', 'personal address' and 'call me' are all "
    "deliberately absent. Sign with her name and the reserved number "
    "555-0176."
)

LURE_SUMMARY = (
    "A job applicant writes to the HR mailbox about a posted opening, "
    "summarizes her experience, and links to a personal portfolio site on a "
    "domain that is on no list. No attachment, no urgency, nothing to sign "
    "in to."
)

MANIFEST_NOTES = (
    "Teaches that freemail plus an unknown link host is not malicious by "
    "itself; the posting number matches the open posting recorded in "
    "recipients.json under the hr mailbox, and the generator reads that "
    "record back rather than typing SC-0426, so the one checkable fact in "
    "the message cannot drift from the data file. Hard by the fact rule "
    "because no decisive benign fact exists; the analyst reads it and closes "
    "it. Rendering notes: the message was composed in Lanternmail Web, so it "
    "follows the webmail conventions 009 and 021 use, the =_lmw_ boundary "
    "prefix and a twelve hex digit id on the submission hop; the plain part "
    "is 7bit with hard wraps under 78 characters and the HTML part is quoted "
    "printable, because the fixed gateway banner snippet is longer than 78; "
    "the HTML is the plain paragraphs a browser client writes, with the link "
    "as an anchor whose text is the address it goes to, so nothing is "
    "hidden. The one link host, oona-adebayo-ferris.example, carries its own "
    "row in data/domain_policy.json, owner class individual, the class "
    "data/display_names.json already gives her; a private person's site "
    "sends no mail, so the row publishes no SPF record, no DKIM selector and "
    "no DMARC policy."
)


# ------------------------------------------------------------ ground truth

AUTH_VALUE = ("spf=pass smtp.mailfrom=" + SENDER_DOMAIN + "; dkim=pass "
              "header.d=" + SENDER_DOMAIN + " header.s=" + DKIM_SELECTOR + " "
              "header.i=@" + SENDER_DOMAIN + "; dmarc=pass "
              "header.from=" + SENDER_DOMAIN + " policy.dmarc=quarantine")

NOTES = (
    "The batch set's benign application from a stranger, and the case that "
    "shows a free webmail address and an unknown link host are two ordinary "
    "facts about private people rather than two findings. Key facts: the "
    "From address oona.adebayo.ferris@lanternmail.example is a free webmail "
    "account, and display_names.json records Oona Adebayo-Ferris as an "
    "individual who owns both lanternmail.example and "
    "oona-adebayo-ferris.example, because a private person has no company "
    "domain to write from; there is no Reply-To; SPF, DKIM and DMARC all "
    "pass for lanternmail.example, which publishes a quarantine policy, and "
    "the pass proves only that the provider really sent the message; "
    "X-Originating-IP [203.0.113.140] is the composing browser's address and "
    "X-Mailer is Lanternmail Web; the message arrived through the gateway "
    "(X-Sentrywick-External: yes) with a clean scan and a spam score of 3.5; "
    "the one link is https://oona-adebayo-ferris.example/work, a path with "
    "no sign-in on a host that is on neither list; there is no removed "
    "attachment and no In-Reply-To; the recipient is the shared HR mailbox "
    "and the reporter is Tobias Nkemelu, the coordinator who works it. "
    "Difficulty hard by the tier rule: a benign record scores a decisive "
    "fact only from the derived combinations in section 5.2, and none of "
    "them is present, so decisive is 0 and the base tier is hard; there is "
    "no injection and the body only read agrees with the verdict, so neither "
    "adjustment applies. The body only read is benign because the prose is "
    "an ordinary job application: it names the posting, describes four years "
    "of dispatch work at Thornbeck Plumbing, links her own work samples, "
    "offers references on request and asks for nothing. Playbook rules 1 and "
    "7 both apply and neither settles it: three passes name a domain and not "
    "a person, and a host on neither list is unknown rather than clean. "
    "Tools: check_sender_reputation matches at domain level, because "
    "oona.adebayo.ferris@lanternmail.example has no address record of its "
    "own, and returns neutral for the provider with nine prior reports, the "
    "last one malicious and tagged ceo-impersonation, which is history about "
    "the provider and not about this sender; check_urls returns unlisted for "
    "oona-adebayo-ferris.example; lookup_recipient shows the Human Resources "
    "shared mailbox with one prior report, no true positives, no executive "
    "or payments flag. Every tool answers and none of them is decisive, so "
    "the loop runs all three and ends on tools_exhausted, which is the shape "
    "week 5 teaches and week 7 has to reproduce without a teaching page in "
    "front of it. recipient:prior_similar_report is absent under the "
    "prior_similar_report_rule: the message carries no ask code, the sender "
    "record's campaign tag ceo-impersonation is in sender_campaign_tags, but "
    "the HR mailbox holds only a benefits-notice report, so no tag matches. "
    "Nothing escalates: the verdict is benign, the category is not spam, "
    "DMARC did not fail on a trusted sender, there is no payment or banking "
    "ask, and the reputation status is neutral rather than unknown, so "
    "unknown_sender_asks_for_data does not apply and would not apply anyway, "
    "since the message asks for no data. Expected action: "
    "close_benign_reply_to_reporter, and the reply to Tobias is that it is a "
    "real application and belongs in the hiring folder. The near neighbour "
    "worth naming for instructors is 009 and 029, the CEO impersonation pair "
    "on the same provider: same neutral domain record, same three passes, "
    "and the difference is entirely in who the display name claims to be. "
    "Deliberate omissions, matching the manifest indicator list: no "
    "Reply-To, no Auto-Submitted, no X-Priority, no list header, no removed "
    "attachment header, and no content indicator, so the rendered body "
    "carries no phrase from any list in spec/enums.json."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-21T19:48:00-05:00",
    "verdict": "benign",
    "category": "legit_external",
    "difficulty": "hard",
    "body_only_read": "benign",
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
            "code": "sender:freemail_domain",
            "where": "check_sender_reputation",
            "value": SENDER_DOMAIN,
        },
        {
            "code": "header:x_originating_ip",
            "where": "X-Originating-IP",
            "value": ORIGINATING_IP,
        },
        {
            "code": "url:host_unlisted",
            "where": "check_urls",
            "value": "oona-adebayo-ferris.example",
        },
        {
            "code": "header:external_flag",
            "where": "X-Sentrywick-External",
            "value": "yes",
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
            "code": "recipient:shared_mailbox",
            "where": "lookup_recipient",
            "value": RECIPIENT,
        },
    ],
    "required_indicators": [
        "sender:freemail_domain",
        "url:host_unlisted",
    ],
    "url_hosts": ["oona-adebayo-ferris.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": SENDER_DOMAIN,
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
            "oona-adebayo-ferris.example": "unlisted",
        },
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Human Resources Shared Mailbox",
            "role": "shared mailbox",
            "mailbox_type": "shared",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 1,
            "true_positive_count_90d": 0,
            "campaign_tags": ["benefits-notice"],
        },
    },
    "expected_loop": {
        # Three tools exist, each one answers, and none of the answers is
        # decisive, so the run ends because there is no tool left to try.
        "tools": ["check_sender_reputation", "check_urls", "lookup_recipient"],
        "stop_reason": "tools_exhausted",
    },
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_benign_reply_to_reporter",
    "reference_summary": (
        "This is a job application for the posting HR opened this month, "
        "sent from a personal email address with a link to the applicant's "
        "own portfolio site. It asks for nothing and is safe to handle as a "
        "normal application."
    ),
    "labeled_by": LABELED_BY,
    "reviewed_by": REVIEWED_BY,
    "review_agreement": False,
    "label_version": LABEL_VERSION,
    "notes": NOTES,
}


# ------------------------------------------------------------------- checks

# This record lists no content indicator, so every phrase list in
# spec/enums.json has to miss. A hit whose code the record does not list is a
# fact a student's own extractor would produce and the answer key would deny,
# and validate_corpus.py fails the file for it.
ALLOWED_CONTENT_CODES = set()

# Lists the validator skips: one is a proportion judgment over Spanish
# stopwords that appear inside ordinary English words, the other is single
# words the corpus also puts inside quoted examples.
PHRASE_PASS_SKIP = {"content:non_english_body", "content:instruction_to_ai"}


def check_no_stray_phrases(parsed):
    """Fail the render when the body carries a phrase this record does not claim."""
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


def decoded_lines(text):
    """A decoded part back as the source lines it was written from."""
    return text.replace("\r\n", "\n").rstrip("\n").split("\n")


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
                  "reporter", "verdict", "category", "difficulty",
                  "body_only_read", "arrival_path", "date", "url_hosts",
                  "escalate_expected", "escalation_reasons",
                  "recommended_action", "required_indicators"):
        if record[field] != GROUND_TRUTH[field]:
            raise SystemExit(field + " does not match the manifest: "
                             + repr(record[field]) + " against "
                             + repr(GROUND_TRUTH[field]))
    if record["attachment"] is not None:
        raise SystemExit("the manifest now carries an attachment; this record had none")
    if record["injection"] is not None:
        raise SystemExit("the manifest now carries an injection; this record had none")
    if record["auth"] != {"spf": "pass", "dkim": "pass", "dmarc": "pass"}:
        raise SystemExit("the manifest authentication results moved: "
                         + repr(record["auth"]))
    if record["tool_expectations"] != GROUND_TRUTH["tool_expectations"]:
        raise SystemExit("tool_expectations drifted from the manifest")
    if record["expected_loop"] != GROUND_TRUTH["expected_loop"]:
        raise SystemExit("expected_loop drifted from the manifest")
    manifest_codes = [item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]]
    truth_codes = [item["code"] for item in GROUND_TRUTH["indicators"]]
    if manifest_codes != truth_codes:
        raise SystemExit("indicator codes drifted from the manifest: "
                         + repr(manifest_codes) + " against " + repr(truth_codes))

    posting = open_posting(RECIPIENT)
    if posting["posting"] not in SUBJECT:
        raise SystemExit("the subject does not cite the open posting "
                         + posting["posting"])
    if posting["title"] not in SUBJECT:
        raise SystemExit("the subject does not name the open posting's title")
    if posting["posting"] not in "\n".join(plain_part()):
        raise SystemExit("the body does not cite the open posting "
                         + posting["posting"])

    data = build_eml(seed)
    with open(EML_PATH, "wb") as handle:
        handle.write(data)

    # Read it back the way the week 1 helper does.
    parsed = email.message_from_bytes(data, policy=email.policy.default)
    if parsed.defects:
        raise SystemExit("defects: " + repr(parsed.defects))
    parts = []
    for part in parsed.walk():
        if part.defects:
            raise SystemExit("part defects: " + repr(part.defects))
        if part.get_content_maintype() == "text":
            parts.append(part.get_content())
    if len(parts) != 2:
        raise SystemExit("expected exactly two text parts")
    if decoded_lines(parts[0]) != plain_part():
        raise SystemExit("the plain part does not decode to its source lines")
    if decoded_lines(parts[1]) != html_part():
        raise SystemExit("the html part does not decode to its source lines")
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    if parsed["Reply-To"] is not None:
        raise SystemExit("this message carries no Reply-To")
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
