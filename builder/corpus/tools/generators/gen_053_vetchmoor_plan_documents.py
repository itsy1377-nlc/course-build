#!/usr/bin/env python3
"""Regenerate 053-vetchmoor-plan-documents.

Rebuilds the exam-only file 053-vetchmoor-plan-documents.eml byte for byte from
the corpus seed, refreshes the prose fields of its own record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

This one is exam-only, so the rendered message ships in the instructor package
and never under corpus/emails/. EML_PATH therefore points at
builder/instructor/exam-emails/, three levels above the corpus folder, and
tools/validate_corpus.py is pointed at that folder with --emails. The corpus
validator warns that an exam record has no file under emails/; that warning is
correct and expected for every record in the exam set.

Every identifier in the file that looks random is derived from the corpus
seed, so rerunning this script reproduces the same bytes:

    hexid(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]

    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    sender-side Received  = hexid("sender-id", 8)
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

No DKIM value is derived, because this message carries no DKIM-Signature at
all. The gateway wrote dkim=none, and section 10 item 14 of
docs/email-header-realism.md fails a file that says dkim=none over a signature.
Nothing else in the file varies between runs: no clock is read, nothing is
randomized, and every timestamp is a literal fixed by the manifest record.

Two values are read back from the data files rather than typed here, so the
rendered headers cannot disagree with the corpus: data/recipients.json gives
mailstore-01 as the one store that holds the coordinator's mailbox, and
data/domain_policy.json gives the DMARC policy the broker publishes and the
SPF record whose "~all" is the reason the gateway could write softfail rather
than fail.

Why the headers look the way they do. This is the real annual plan document
notice from the benefits broker, and every authentication check on it fails:

  * The broker's document system does not send through the broker's own mail
    hosts. It sends through docs-relay.hostedforms-nine.example
    [198.51.100.180], the outbound relay of the hosted document platform the
    broker buys, and that host is not an MX for the broker, so it matches no
    mechanism of the SPF record domain_policy.json publishes for
    vetchmoorbenefits.example, "mx ~all". The record ends "~all", so the
    gateway wrote spf=softfail and the Received-SPF mechanism is that "~all".
  * The same platform does not sign for the broker: there is no key under
    vetchmoorbenefits.example for it, so no DKIM-Signature is applied and the
    gateway wrote dkim=none. This is the one difference from 037, where the
    signature exists and the body is rewritten after signing (dkim=fail). A
    missing signature and a broken signature look equally bad in the DMARC
    line and mean different things about the sender.
  * Neither an aligned SPF pass nor an aligned DKIM pass is left, so DMARC
    fails against the quarantine policy vetchmoorbenefits.example publishes.
    The From domain is the broker's own, so the failure is
    auth:dmarc_fail_owned_domain: the domain that failed is a domain we have
    done business with since 2021.

One note for whoever revisits this file, in the same form gen_037 records its
own. The record domain_policy.json publishes for the broker read
"mx include:sendbarrow-mail.example ~all" until the 2026-09 manifest pass, and
the record it included, sendbarrow-mail.example, is "ip4:198.51.100.0/24 -all".
The relay address the manifest's received_path_hint fixes, 198.51.100.180, sits
inside that /24, so a strict evaluation of the include returned pass and made
the softfail this record asserts unreachable. The include was dropped, leaving
"mx ~all": docs-relay.hostedforms-nine.example is not an MX for the broker, so
the softfail is now reachable. Nothing in the rendered file moved, because
Received-SPF quotes only client-ip=198.51.100.180 and mechanism=~all, never the
block. 056 is unaffected: its envelope is bounce.sendbarrow-mail.example, which
publishes its own SPF record, and its dmarc=pass rests on DKIM alignment.

The gateway quarantined the message on that verdict at 10:20 on Tuesday 28
April. The coordinator was waiting for the annual plan documents, found the
notice in the quarantine list that afternoon and released it at 13:52:41,
then reported it. That is why X-Sentrywick-Scan-Result reads
released-from-quarantine and why the store's LMTP hop is stamped three and a
half hours after the gateway hop: release is a delivery, not a second receipt,
so timestamps still never increase from the top of the chain downward. 006 and
037 render the same gap for the same reason.

Auto-Submitted: auto-generated is here because the message is written by the
platform's document system rather than by a person, which is also why the
message closes on a service footer instead of a personal signature block
(RFC 3834 sec. 5).

Headers deliberately absent, matching the manifest indicator list: no
DKIM-Signature, as above; no Reply-To, because replies to the From mailbox
reach the client service desk and the record's reply_to is null; no In-Reply-To
and no References, so thread:new holds; no X-Originating-IP, which is reserved
for webmail submissions; no X-Priority and no Importance, because an annual
document notice applies no urgency and the body carries no urgency phrase
either; no list headers, because a transactional notice to one plan contact is
not bulk mail; no X-Sentrywick-Removed-Attachment, so attachment:none holds.

Run:  python3 corpus/tools/generators/gen_053_vetchmoor_plan_documents.py
"""

import email
import email.policy
import hashlib
import json
import os
import re
import uuid

EMAIL_ID = "053-vetchmoor-plan-documents"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
POLICY_PATH = os.path.join(CORPUS, "data", "domain_policy.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
# Exam-only: the file ships in the instructor package, never under emails/.
EML_PATH = os.path.join(BUILDER, "instructor", "exam-emails", EMAIL_ID + ".eml")
# The path the ground truth records, which is where an exam file would sit if
# the exam set were ever released into the corpus tree. The schema pattern in
# spec/ground_truth.schema.json accepts emails/teaching, emails/batch and
# emails/exam and nothing else.
GT_FILE = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

SENDER = "plandocs@vetchmoorbenefits.example"
SENDER_DISPLAY = "Vetchmoor Benefits Plan Documents"
SENDER_DOMAIN = "vetchmoorbenefits.example"
# The envelope sender is the From mailbox. The document platform sends as the
# broker, which is the whole reason DMARC has something to fail on: the
# identity the message claims is the broker's own, and the host carrying it is
# not one the broker published.
ENVELOPE_SENDER = SENDER
RECIPIENT = "t.nkemelu@pellgrave.example"
RECIPIENT_DISPLAY = "Tobias Nkemelu"
REPORTER = RECIPIENT

SUBJECT = "2026 summary plan descriptions ready for download"

# The hosted document platform the broker buys. Its relay is the host the
# broker never put in its SPF record; 198.51.100.180 is RFC 5737 TEST-NET-2 and
# 192.0.2.148 is TEST-NET-1, so neither address routes anywhere.
SENDER_RELAY = "docs-relay.hostedforms-nine.example"
SENDER_RELAY_IP = "198.51.100.180"
SENDER_APP_HOST = "docgen-04.hostedforms-nine.example"
SENDER_APP_IP = "192.0.2.148"

GATEWAY = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"
SCAN_RESULT = "released-from-quarantine"
SPAM_SCORE = "5.2"

# The one link. Its host is the broker's own site, the fact url:host_allowlisted
# keys on, and its path is a client document path rather than a sign-in path.
LINK = "https://vetchmoorbenefits.example/clients/pellgrave/plan-documents"
LINK_LABEL = "Open the plan documents page"

# Timestamps. The platform stamps UTC and the receiving side stamps -0500, and
# 15:20 +0000 is the same instant as 10:20 -0500, so the Message-ID stamp, the
# Date and the two upper Received lines agree. The store hop is the afternoon
# of the same day, because the gateway quarantined the message on arrival and
# the coordinator released it when he went looking for the annual documents.
DATE_HEADER = "Tue, 28 Apr 2026 10:20:00 -0500"
SUBMIT_STAMP = "Tue, 28 Apr 2026 15:20:02 +0000"
GATEWAY_STAMP = "Tue, 28 Apr 2026 10:20:06 -0500"
STORE_STAMP = "Tue, 28 Apr 2026 13:52:41 -0500"
MESSAGE_ID_STAMP = "20260428152000"

# RFC 2045 sec. 6.7: a quoted-printable line is at most 76 characters including
# the trailing soft break.
QP_MAX = 76


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    return str(uuid.UUID(hex=hexid(seed, "store-id", 32), version=4))


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


def domain_policy(domain):
    """The published DMARC policy and SPF record for one domain."""
    with open(POLICY_PATH, encoding="utf-8") as handle:
        policy = json.load(handle)
    for entry in policy["domains"]:
        if entry["domain"] == domain:
            return entry
    raise SystemExit("domain_policy.json has no record for " + domain)


# ---------------------------------------------------------------- body text
#
# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# manifest record carries no content code at all, so no phrase from any body
# list may appear in either decoded part. validate_corpus.py checks that from
# the rendered file and content_phrase_audit() below checks it again before the
# file is written. The traps worth naming, because each one is a word an
# ordinary benefits notice would reach for:
#
#   "download" is content:file_share_lure, and it is a substring test, so the
#   word cannot appear anywhere in either part. The Subject keeps it, because
#   the phrase pass reads the two body parts and not the header block, and the
#   Subject is an authored field of the manifest record. In the body the link
#   is labelled "Open the plan documents page" and the documents are described
#   as posted to the client page. See NOTES: the manifest's body_brief asked
#   for a link labelled "Download plan documents", which no record without
#   content:file_share_lure can carry, so the label moved and body_brief was
#   rewritten to match the rendered text.
#   "today", "immediately", "action needed" and the rest of
#   content:urgency_keywords are out. The two deadlines in the text are the
#   distribution rule a plan sponsor already lives under, written as 30 days
#   and 90 days, which is on no phrase list and applies no pressure of its own.
#   "sign in", "log in", "password" and "credentials" are out: a document
#   notice points at a client page the coordinator already has an account on
#   and never asks for an identity.
#   "invoice", "remit", "amount due" and the rest of content:payment_request
#   are out, and so is every content:payment_change_request phrase. Nothing in
#   this message is about money.
#   "employee list" (content:data_request) is out, so the merge file for the
#   enrollment packets is called a mail merge file.
#   "confidential" (content:secrecy_request) is out, which is why the service
#   footer says what it has to say in plainer words.
#   "call me" and the rest of content:phone_verification_offered are out. The
#   number in the footer is a service desk line, not an instruction, and it is
#   the channel the out of band verification this record expects will use.
#   "not working" (content:excuse_for_external_address) is out, so the fallback
#   line under the button says "does not open" instead.
#
# The result is a body that reads exactly as benign as it is. The whole
# difficulty of this email lives in the header block, which is what makes it
# the hard case: a model that reads dmarc=fail as a verdict calls a real
# benefits notice from a vendor of five years a phish.

BANNER_PLAIN = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">[External message. Sentrywick '
               'Gateway]</p>')

HEADING = "Vetchmoor Benefits, plan document delivery"
SALUTATION = "Hello Tobias,"

PARA_READY = [
    "The 2026 summary plan descriptions for Pellgrave Mechanical Group are",
    "finished and posted to your client page. They cover the four plans you",
    "renewed in February, and they replace the 2025 set, which stays on the",
    "page under Prior years.",
]

# The five documents, as the platform lists them. The HTML part renders these
# as one paragraph with <br> between the lines, so both parts carry the same
# five lines in the same order and a part-to-part diff is empty.
DOCUMENT_LINES = [
    "2026 SPD, medical and prescription plan",
    "2026 SPD, dental and vision plans",
    "2026 SPD, group life and long term disability",
    "2026 SPD, health savings account",
    "Summary of material modifications, medical plan, effective 1/1/26",
]

PARA_DISTRIBUTE = [
    "A plan sponsor hands a summary plan description to a participant within",
    "30 days of a written request, and to a newly covered participant within",
    "90 days of the day coverage starts. Print ready copies and a mail merge",
    "file for your enrollment packets are on the same page.",
]

PARA_CHANGES = [
    "If a plan name or a group number looks wrong for your groups, reply to",
    "this message and your account team will pick it up.",
]

# A service footer rather than a personal signature block, because the platform
# wrote this message and Auto-Submitted says so. 555-0192 is inside the
# 555-0100 through 555-0199 fictional range and is used by no other file in the
# corpus.
FOOTER_LINES = [
    "Vetchmoor Benefits, plan document service",
    "Client service desk 555-0192",
    "Sent to the plan contact on file for Pellgrave Mechanical Group.",
    "Replies to this address reach the client service desk.",
]


def joined(lines):
    return " ".join(lines)


def plain_part():
    lines = [BANNER_PLAIN, ""]
    lines += [HEADING, ""]
    lines += [SALUTATION, ""]
    lines += PARA_READY + [""]
    lines += [LINK_LABEL + ":", LINK, ""]
    lines += ["This year's set:", ""]
    lines += DOCUMENT_LINES + [""]
    lines += PARA_DISTRIBUTE + [""]
    lines += PARA_CHANGES + [""]
    lines += FOOTER_LINES
    return lines


def document_html():
    block = [line + "<br>" for line in DOCUMENT_LINES[:-1]]
    block[0] = "<p>" + block[0]
    block.append(DOCUMENT_LINES[-1] + "</p>")
    return block


def footer_html():
    block = ['<p style="font-size:12px;color:#6b6b6b;">' + FOOTER_LINES[0] + "<br>"]
    for line in FOOTER_LINES[1:-1]:
        block.append(line + "<br>")
    block.append(FOOTER_LINES[-1] + "</p>")
    return block


def html_part():
    lines = [
        "<html>",
        '<body style="margin:0;padding:0;background:#f2f4f5;">',
        BANNER_HTML,
        '<div style="max-width:620px;margin:0 auto;padding:24px;',
        "  background:#ffffff;font-family:sans-serif;font-size:15px;",
        '  line-height:1.5;color:#1f1f1f;">',
        '<p style="margin:0 0 18px 0;font-size:17px;font-weight:bold;',
        '  color:#1d5a52;">' + HEADING + "</p>",
        "<p>" + SALUTATION + "</p>",
        "<p>" + joined(PARA_READY) + "</p>",
    ]
    # The href is the same address the plain part prints and the button text is
    # the same label, and the address is repeated underneath in plain sight, so
    # a reader of either part can see where the link goes. No image, no script,
    # no form, no hidden text.
    lines += [
        '<p><a href="' + LINK + '"',
        '  style="display:inline-block;padding:10px 22px;background:#1d5a52;',
        '  color:#ffffff;text-decoration:none;border-radius:4px;"',
        "  >" + LINK_LABEL + "</a></p>",
        '<p style="font-size:13px;color:#555555;">If the button does not open,',
        "the address is " + LINK + "</p>",
        "<p>This year's set:</p>",
    ]
    lines += document_html()
    lines += ["<p>" + joined(PARA_DISTRIBUTE) + "</p>"]
    lines += ["<p>" + joined(PARA_CHANGES) + "</p>"]
    lines += footer_html()
    lines += ["</div>", "</body>", "</html>"]
    return lines


# ------------------------------------------------------- quoted-printable

def qp_escape(line):
    return line.replace("=", "=3D")


def qp_wrap(line):
    """Fold one escaped logical line into quoted-printable physical lines.

    Break at the last space that still fits, carrying the space to the start
    of the next line so no line ends in white space; when no space fits,
    hard-break at 75 characters plus the soft line break, never inside an =XX
    escape.
    """
    out = []
    rest = line
    while len(rest) > QP_MAX:
        cut = rest.rfind(" ", 1, QP_MAX)
        if cut <= 0:
            cut = QP_MAX - 1
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
    policy = domain_policy(SENDER_DOMAIN)
    dmarc_policy = policy["dmarc_policy"]
    spf_record = policy["spf"]
    if dmarc_policy is None:
        raise SystemExit("dmarc=fail needs a published policy for " + SENDER_DOMAIN)
    if spf_record is None or not spf_record.strip().endswith("~all"):
        raise SystemExit("spf=softfail needs an SPF record ending ~all; "
                         + SENDER_DOMAIN + " has " + str(spf_record))
    store = mailstore(RECIPIENT)

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SENDER_RELAY + ">")
    gateway_id = hexid(seed, "gateway-id")
    sender_id = hexid(seed, "sender-id", 8)
    lmtp_id = store_id(seed)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY + " (" + GATEWAY + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # RFC 8601 sec. 4: the gateway writes Authentication-Results above its
        # own trace field. All three checks fail here, and they fail for the
        # broker's own domain, which is the fact the exam question turns on: a
        # failure names a domain, and this domain has been a vendor since 2021.
        "Authentication-Results: " + GATEWAY + ";",
        "  spf=softfail smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=none;",
        "  dmarc=fail header.from=" + SENDER_DOMAIN
        + " policy.dmarc=" + dmarc_policy,
        "Received-SPF: softfail (" + GATEWAY + ": domain of transitioning",
        "  " + ENVELOPE_SENDER + " does not designate " + SENDER_RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY + ";",
        "  client-ip=" + SENDER_RELAY_IP + ";",
        '  envelope-from="' + ENVELOPE_SENDER + '";',
        "  helo=" + SENDER_RELAY + "; identity=mailfrom; mechanism=~all",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SENDER_RELAY,
        "  (" + SENDER_RELAY + " [" + SENDER_RELAY_IP + "])",
        "  by " + GATEWAY + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_id + ";",
        "  " + GATEWAY_STAMP,
        # The platform's document node handing the run to the platform's own
        # outbound relay, the same shape section 7 scenario C gives a hosted
        # provider. Nothing signs it on the way past, which is why the file
        # carries no DKIM-Signature and the gateway wrote dkim=none.
        "Received: from " + SENDER_APP_HOST + " ([" + SENDER_APP_IP + "])",
        "  by " + SENDER_RELAY + " with ESMTP id " + sender_id + ";",
        "  " + SUBMIT_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        # RFC 3834 sec. 5: a system notice says so, and the manifest lists
        # header:auto_submitted for exactly this line.
        "Auto-Submitted: auto-generated",
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
    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "The platform's annual document notice: the 2026 summary plan "
    "descriptions for Pellgrave Mechanical Group are finished and posted to "
    "the client page, they cover the four plans renewed in February, and they "
    "replace the 2025 set. One link, labelled 'Open the plan documents page', "
    "to https://vetchmoorbenefits.example/clients/pellgrave/plan-documents, "
    "printed as an address in both parts. List the five documents in the set, "
    "four summary plan descriptions and one summary of material "
    "modifications. State the distribution rule once, as 30 days from a "
    "written request and 90 days from the start of coverage, and say that "
    "print ready copies and a mail merge file are on the same page. Close on "
    "a service footer naming the plan document service, a client service desk "
    "number in the 555-01xx block and the plan contact on file, not on a "
    "person's signature, because the platform wrote the message and "
    "Auto-Submitted says so. No sign-in wording, no money, no attachment, and "
    "no phrase from any content list in spec/enums.json, because the record "
    "carries no content indicator. In particular the word download appears in "
    "the Subject and nowhere in either body part: it is a "
    "content:file_share_lure phrase, and this record lists no content code."
)

LURE_SUMMARY = (
    "The real benefits broker's document system says the annual plan "
    "descriptions are ready and links to the broker's allowlisted site. The "
    "system sends from a relay that is in neither mechanism of the broker's "
    "SPF record and signs nothing, so DMARC fails and the gateway quarantined "
    "the notice until the coordinator released it."
)

MANIFEST_NOTES = (
    "Exam-only twin of 037 with a different vendor and dkim=none instead of "
    "dkim=fail. Benign, verify then close. The stem asks what the analyst "
    "does when a trusted vendor fails DMARC, and the difference from 037 is "
    "worth a sentence in the key: a missing signature and a broken signature "
    "read the same in the DMARC line and say different things about the "
    "sender. Rendering: spf=softfail for "
    "docs-relay.hostedforms-nine.example [198.51.100.180], the outbound relay "
    "of the hosted document platform the broker buys, which is in neither the "
    "mx nor the include mechanism of the SPF record domain_policy.json "
    "publishes for vetchmoorbenefits.example; dkim=none with no DKIM-Signature "
    "in the file at all, because that platform holds no key for the broker; "
    "dmarc=fail against the published quarantine policy because neither "
    "aligned check passed, on the broker's own From domain, which is "
    "auth:dmarc_fail_owned_domain. The gateway quarantined it on that verdict "
    "at 10:20 and the coordinator released it at 13:52:41 the same afternoon "
    "because he was waiting for the annual documents, so "
    "X-Sentrywick-Scan-Result is released-from-quarantine and the store's "
    "LMTP hop is stamped three and a half hours after the gateway hop; "
    "release is a delivery, not a second receipt. Auto-Submitted: "
    "auto-generated, spam score 5.2, no attachment, no Reply-To, new thread. "
    "One caution recorded and not acted on: the broker's SPF record includes "
    "sendbarrow-mail.example, whose own record is ip4:198.51.100.0/24 -all, "
    "and the relay address sits inside that block, so a strict evaluation of "
    "the include would return pass. The manifest fixes softfail and the file "
    "renders softfail; reconciling the two means narrowing the block "
    "Sendbarrow publishes, moving the document relay outside it, or dropping "
    "the include, and that is a data file decision. Escalation reasons: "
    "auth_failure_on_trusted_sender."
)


# ------------------------------------------------------------ ground truth

REFERENCE_SUMMARY = (
    "This is a real notice from Vetchmoor's document system, but it failed our "
    "mail checks because their system sends from a server they have not "
    "registered. We will confirm with Vetchmoor and then close it; the link "
    "itself goes to their real site."
)

NOTES = (
    "The exam case that asks what an analyst does when a trusted vendor fails "
    "DMARC. Key facts a correct extractor produces: from_domain "
    "vetchmoorbenefits.example under the display name Vetchmoor Benefits Plan "
    "Documents, which display_names.json records as a name that domain owns, "
    "so display_name_mismatch is false; no Reply-To, so there is no Reply-To "
    "mismatch to find; spf=softfail on vetchmoorbenefits.example, dkim=none "
    "with no DKIM-Signature in the file, dmarc=fail with policy quarantine, "
    "so nothing is aligned and the domain that failed is the broker's own; "
    "one link host, vetchmoorbenefits.example, carrying the single link "
    "https://vetchmoorbenefits.example/clients/pellgrave/plan-documents, whose "
    "path is a client document path and not a sign-in path; no "
    "X-Sentrywick-Removed-Attachment; Auto-Submitted: auto-generated; scan "
    "result released-from-quarantine, spam score 5.2; no In-Reply-To, so the "
    "message opens a thread. Why every check failed, and why none of it is an "
    "attack: the broker's document system sends through "
    "docs-relay.hostedforms-nine.example [198.51.100.180], the outbound relay "
    "of a hosted document platform, and that host is in neither mechanism of "
    "the SPF record domain_policy.json publishes for the broker, which ends "
    "~all, so the gateway wrote softfail with mechanism ~all; the platform "
    "holds no signing key for the broker, so the message is unsigned and the "
    "gateway wrote dkim=none; with no aligned pass left, DMARC failed against "
    "the quarantine policy the broker publishes. Received chain: "
    "docgen-04.hostedforms-nine.example [192.0.2.148] handed the run to "
    "docs-relay.hostedforms-nine.example with ESMTP at 15:20:02 +0000, which "
    "handed off with ESMTPS and TLS1_3 to mx.pellgrave.example [10.20.4.10] "
    "at 10:20:06 -0500, where the message was quarantined; the coordinator "
    "released it that afternoon, so the LMTP hop to "
    "mailstore-01.pellgrave.example is stamped 13:52:41 -0500 the same day. "
    "Timestamps still never increase from the top of the chain downward, "
    "because release is a delivery and not a second receipt; 006 and 037 "
    "render the same gap for the same reason. Date is 10:20:00 -0500, the "
    "same instant as 15:20:00 +0000 in the Message-ID. Body: the record "
    "carries no content code, so no phrase from any content list in "
    "spec/enums.json appears in either decoded part. The text says the 2026 "
    "summary plan descriptions are finished and posted to the client page, "
    "lists the five documents in the set, states the distribution rule once "
    "as 30 days from a written request and 90 days from the start of "
    "coverage, and closes on a service footer with a client service desk "
    "number, which is the channel the out of band verification will use. The "
    "word download is in the Subject and in neither body part, because it is "
    "a content:file_share_lure phrase and this record lists no content code; "
    "the link is labelled 'Open the plan documents page' for the same reason. "
    "recipient:prior_similar_report does not apply: a message with no ask "
    "implies no campaign tag under prior_similar_report_rule, and the sender "
    "record carries no campaign tag either, even though the mailbox holds a "
    "benefits-notice report closed benign on 2026-02-11 and three true "
    "positives. Difficulty reason: the tier rule counts no decisive benign "
    "fact, because an allowlisted sender is decisive only when dmarc passes "
    "and here it fails, against two pressure facts (auth:dmarc_fail and "
    "header:released_from_quarantine), so decisive is zero and the base tier "
    "is hard; the body only read is benign, which agrees with the verdict, "
    "and there is no injection, so neither adjustment applies and it stays "
    "hard. For the instructor: this is the false positive the exam is built "
    "to catch, and it is the twin of 037, so a student who learned the vendor "
    "invoice case has seen the shape once. Ungrounded, two failed checks, a "
    "missing signature and a quarantine release read as phishing. Grounded, "
    "the facts answer: check_sender_reputation returns trusted for "
    "vetchmoorbenefits.example, first seen 2021-11-02, 34 messages in 90 days, "
    "one prior report closed benign on 2026-02-11; check_urls returns "
    "allowlisted for vetchmoorbenefits.example; lookup_recipient shows the "
    "payroll and benefits coordinator, a named person who handles payments "
    "and is not a chronic reporter. Nothing in the body states any tool "
    "result, so the loop has to fetch them, and no single result is decisive "
    "against a header block this bad, so the run calls all three tools in "
    "turn and ends on tools_exhausted. The verdict is benign because no fact "
    "points at an attack, and it still escalates under "
    "auth_failure_on_trusted_sender, which is the rule that says a human "
    "confirms with the broker on the service desk number before the plan "
    "documents are distributed, and then closes it. Full credit on the "
    "indicators criterion needs auth:dmarc_fail, sender:allowlisted_domain "
    "and url:host_allowlisted. Story context: 013 and 024 are the lookalike "
    "vetchmoor-benefits.example census phish against the same coordinator "
    "earlier in the month, and 056 is the broker's genuine newsletter that "
    "passes DMARC through the bulk provider; this record is the third face of "
    "the same vendor, the real sender that fails. Grading note: a student who "
    "calls this malicious because two checks failed has skipped the tools, "
    "and a student who calls it benign and closes it without a callback has "
    "skipped the escalation rule."
)


def ground_truth():
    return {
        "id": EMAIL_ID,
        "file": GT_FILE,
        "set": "exam",
        "weeks": [8],
        "date": "2026-04-28T10:20:00-05:00",
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
        "auth": {"spf": "softfail", "dkim": "none", "dmarc": "fail",
                 "dmarc_policy": "quarantine"},
        "indicators": [
            {"code": "auth:spf_softfail", "where": "Authentication-Results",
             "value": "spf=softfail smtp.mailfrom=vetchmoorbenefits.example"},
            {"code": "auth:dkim_none", "where": "Authentication-Results",
             "value": "dkim=none"},
            {"code": "auth:dmarc_fail", "where": "Authentication-Results",
             "value": ("dmarc=fail header.from=vetchmoorbenefits.example "
                       "policy.dmarc=quarantine")},
            {"code": "auth:dmarc_fail_owned_domain",
             "where": "Authentication-Results",
             "value": "header.from=vetchmoorbenefits.example"},
            {"code": "header:released_from_quarantine",
             "where": "X-Sentrywick-Scan-Result",
             "value": "released-from-quarantine"},
            {"code": "sender:allowlisted_domain",
             "where": "check_sender_reputation", "value": SENDER_DOMAIN},
            {"code": "url:host_allowlisted", "where": "check_urls",
             "value": "vetchmoorbenefits.example"},
            {"code": "header:auto_submitted", "where": "Auto-Submitted",
             "value": "auto-generated"},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "attachment:none",
             "where": "X-Sentrywick-Removed-Attachment", "value": None},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
        ],
        "required_indicators": ["auth:dmarc_fail", "sender:allowlisted_domain",
                                "url:host_allowlisted"],
        "url_hosts": ["vetchmoorbenefits.example"],
        "attachment": None,
        "injection": None,
        "tool_expectations": {
            "check_sender_reputation": {
                "domain": SENDER_DOMAIN,
                "status": "trusted",
                "first_seen": "2021-11-02",
                "messages_90d": 34,
                "prior_reports": 1,
                "last_report_verdict": "benign",
                "last_report_date": "2026-02-11",
                "campaign_tag": None,
                "new_domain": False,
                "notes": "Benefits broker; allowlisted.",
                "match_level": "domain",
            },
            "check_urls": {"vetchmoorbenefits.example": "allowlisted"},
            "lookup_recipient": {
                "address": RECIPIENT,
                "name": "Tobias Nkemelu",
                "role": "Payroll and Benefits Coordinator",
                "mailbox_type": "person",
                "executive": False,
                "handles_payments": True,
                "chronic_reporter": False,
                "report_count_90d": 5,
                "true_positive_count_90d": 3,
                "campaign_tags": ["benefits-notice", "credential-phish",
                                  "direct-deposit-change", "payroll-notice"],
            },
        },
        # No tool result is decisive against a header block with two failed
        # checks and a missing signature in it, so all three run and the loop
        # ends with no tool left to try rather than on a decisive result or the
        # step cap.
        "expected_loop": {
            "tools": ["check_sender_reputation", "check_urls",
                      "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
        "escalate_expected": True,
        "escalation_reasons": ["auth_failure_on_trusted_sender"],
        "recommended_action": "verify_out_of_band_then_close",
        "reference_summary": REFERENCE_SUMMARY,
        "labeled_by": LABELED_BY,
        "reviewed_by": REVIEWED_BY,
        "review_agreement": False,
        "label_version": LABEL_VERSION,
        "notes": NOTES,
    }


# ------------------------------------------------------------------- checks

def sentence_count(text):
    """The count check_spec.py applies to lure_summary and reference_summary."""
    return len([piece for piece in re.split(r"(?<=[.!?])\s+", text.strip()) if piece])


def content_phrase_audit():
    """Every content phrase list in enums.json, run against both parts.

    The record carries no content code, so every phrase on every body list has
    to be absent. validate_corpus.py checks the same thing from the rendered
    file; this catches it before the file is written.

    Two lists are excluded, the same two validate_corpus.py excludes: one is a
    proportion judgment over Spanish stopwords that sit inside English words,
    and the other is a single-word list the corpus also puts inside quoted
    examples.
    """
    with open(ENUMS_PATH, encoding="utf-8") as handle:
        enums = json.load(handle)
    phrases = enums["content_phrases"]
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = ("\n".join(plain_part()) + "\n" + "\n".join(html_part())).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")
    # Named separately because the Subject keeps the word and the body must not.
    if "download" in body:
        raise SystemExit("the body carries 'download', a content:file_share_lure phrase")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    with open(SPEC_PATH, encoding="utf-8") as handle:
        spec = json.load(handle)
    seed = spec["seed"]

    entry = None
    for candidate in spec["emails"]:
        if candidate["id"] == EMAIL_ID:
            entry = candidate
            break
    if entry is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    if entry["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if entry["sender_address"] != SENDER or entry["recipient"] != RECIPIENT:
        raise SystemExit("addresses do not match the manifest")
    if entry["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if entry["reporter"] != REPORTER or entry["reply_to"] is not None:
        raise SystemExit("reporter or reply_to does not match the manifest")
    if entry["url_hosts"] != ["vetchmoorbenefits.example"]:
        raise SystemExit("url_hosts do not match the manifest")
    if entry["attachment"] is not None or entry["injection"] is not None:
        raise SystemExit("this record carries no attachment and no injection")
    if entry["auth"] != {"spf": "softfail", "dkim": "none", "dmarc": "fail"}:
        raise SystemExit("auth results do not match the manifest")
    if entry["date"] != "2026-04-28T10:20:00-05:00":
        raise SystemExit("date does not match the manifest")
    if sentence_count(LURE_SUMMARY) != 2:
        raise SystemExit("lure_summary must be exactly two sentences")
    if sentence_count(REFERENCE_SUMMARY) != 2:
        raise SystemExit("reference_summary must be exactly two sentences")
    if REFERENCE_SUMMARY != entry["reference_summary"]:
        raise SystemExit("reference_summary must match the manifest word for word")
    for text in (BODY_BRIEF, LURE_SUMMARY, MANIFEST_NOTES):
        if "—" in text or "–" in text or "TODO" in text:
            raise SystemExit("manifest prose must hold no dash character and no TODO")

    content_phrase_audit()

    data = build_eml(seed)
    folder = os.path.dirname(EML_PATH)
    if not os.path.isdir(folder):
        os.makedirs(folder)
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
    for text in parts:
        if text.count(BANNER_PLAIN) != 1:
            raise SystemExit("the gateway banner must appear once in each part")
        if text.count(LINK) < 1:
            raise SystemExit("a part lost the plan documents link")
        if "download" in text.lower():
            raise SystemExit("a decoded part carries 'download'")
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    if str(parsed["From"]) != SENDER_DISPLAY + " <" + SENDER + ">":
        raise SystemExit("unfolded From is " + repr(str(parsed["From"])))
    if str(parsed["Auto-Submitted"]) != "auto-generated":
        raise SystemExit("Auto-Submitted must be auto-generated")
    for absent in ("Reply-To", "In-Reply-To", "References", "DKIM-Signature",
                   "X-Originating-IP", "X-Priority", "Importance",
                   "List-Unsubscribe", "X-Sentrywick-Removed-Attachment"):
        if parsed[absent] is not None:
            raise SystemExit("this message carries no " + absent)

    entry["body_brief"] = BODY_BRIEF
    entry["lure_summary"] = LURE_SUMMARY
    entry["notes"] = MANIFEST_NOTES
    write_json(SPEC_PATH, spec)

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    new_record = ground_truth()
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = new_record
            break
    else:
        records.append(new_record)
        records.sort(key=lambda existing: existing["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
