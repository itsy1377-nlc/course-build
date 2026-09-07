#!/usr/bin/env python3
"""Regenerate 032-cindermill-invoice-executable.

Rebuilds emails/batch/032-cindermill-invoice-executable.eml byte for byte from
the corpus seed and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hexid(label, n)  = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side = <UTC stamp>.hexid("message-id", 12)
    MIME boundary        = "=_swk_" + hexid("mime-boundary", 12)
    gateway Received id  = hexid("gateway-message-uid", 12), which is also
                           X-Sentrywick-Message-UID
    relay Received id    = hexid("relay-smtp-id", 8)
    store LMTP id        = UUID(bytes=sha256(seed|id|store-lmtp-id)[:16],
                           version=4)
    attachment sha256    = sha256("<seed>|<email id>|<filename>"), the rule
                           data/attachments.json states for every stub file

Nothing in this file is a literal that the seed cannot explain. The two values
that are not hashes are read back from the data files rather than typed here:
data/recipients.json gives mailstore-01 as the one store that holds the
recipient's mailbox, and data/attachments.json gives the removed file's name,
size, action, type and reason, with its sha256 checked against the derivation
above before the header is written.

A note on the label strings, because they are not the ones 002 and 012 use.
Those two hash the labels "boundary", "gateway-id", "sender-id" and
"store-id"; this file was rendered against "mime-boundary",
"gateway-message-uid", "relay-smtp-id" and "store-lmtp-id". The label is an
input to the hash, so adopting the shorter forms would change four of the five
derived values in a file that is already committed and already referenced by
ground truth, and one of those four, the gateway id, appears twice. The
rendered file wins. Nothing in the corpus ever reads a label back, so the
only requirement on it is that it stay fixed, and these are the ones that
reproduce the bytes.

Both body parts are quoted-printable, and both were encoded with
email.quoprimime.body_encode(text, maxlinelen=76, eol=CRLF). That encoder
breaks an over-long line at 75 characters and appends the soft break without
looking for a space first, so several lines in this file split in the middle
of a word: "by=" then "tes)." in the plain part, "12=" then "px;" and "at="
then "tachment:" in the HTML part. A wrapper that preferred to break at spaces
would decode to the same text and would not reproduce the file, so the encoder
call is kept exactly as it was. Both parts need the encoding: the gateway's
fixed HTML banner snippet and the first line of the removal notice each run
past 78 characters in source.

Why the header block looks the way it does. The message arrives through the
border gateway, so it carries Authentication-Results, Received-SPF and
X-Sentrywick-External: yes, and the gateway inserts its banner into both
parts. cindermill-signs.example is spoofed rather than compromised: the
sending relay sits outside the domain's SPF record, which ends in ~all, so the
result is softfail rather than fail, and there is no DKIM-Signature header at
all because dkim=none means nothing was signed. The domain publishes no DMARC
record, so the dmarc clause carries no policy.dmarc and the record's
dmarc_policy is null. Message-ID names api-node-02.cheapsend-relay.example,
the originating host at the bottom of the Received chain, which is the
convention docs/email-header-realism.md section 1 states; the relay provider
appears only in Received lines, the helo value and that Message-ID host, never
as a From, Reply-To, Return-Path or link domain.

The LMTP hop is simpler than the one in 002. The recipient is a person rather
than a distribution list and she is also the reporter, so there is no list
expansion to reason about: the mailbox the file was pulled from is the To
address, and its store is the store recipients.json records for it.

Headers deliberately absent, matching the manifest indicator list: no
X-Originating-IP, which is reserved for webmail submissions; no X-Mailer; no
Auto-Submitted; no X-Priority; and no DKIM-Signature, for the reason above.

Run:  python3 corpus/tools/generators/gen_032_cindermill_invoice_executable.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid
from email import quoprimime

EMAIL_ID = "032-cindermill-invoice-executable"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ATTACHMENTS_PATH = os.path.join(CORPUS, "data", "attachments.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

CRLF = "\r\n"

SENDER = "billing@cindermill-signs.example"
SENDER_DISPLAY = "Cindermill Signs Billing"
SENDER_DOMAIN = "cindermill-signs.example"
RECIPIENT = "p.castellanos@pellgrave.example"
REPORTER = RECIPIENT
SUBJECT = "Invoice 88213 attached, net 15"

# The relay the spoofed mail actually came from, and the node behind it that
# the Message-ID names. 198.51.100.146 is RFC 5737 TEST-NET-2 and 192.0.2.93
# is TEST-NET-1, so neither address can route anywhere.
RELAY_HOST = "mta-9.cheapsend-relay.example"
RELAY_IP = "198.51.100.146"
ORIGIN_HOST = "api-node-02.cheapsend-relay.example"
ORIGIN_IP = "192.0.2.93"
GATEWAY_HOST = "mx.pellgrave.example"
GATEWAY_IP = "10.20.4.10"

SCAN_RESULT = "suspect"
SPAM_SCORE = "6.9"


def digest(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode("ascii")).digest()


def hexid(seed, label, length):
    return digest(seed, label).hex()[:length]


def store_id(seed):
    return str(uuid.UUID(bytes=digest(seed, "store-lmtp-id")[:16], version=4))


def attachment_digest(seed, filename):
    """The stub file's sha256, the rule data/attachments.json states.

    No file exists. The digest is SHA-256 over seed|email id|filename, so it
    matches no threat-intelligence list and the week 4 attachment tool can
    still look it up.
    """
    return digest(seed, filename).hex()


def attachment_record(seed):
    with open(ATTACHMENTS_PATH, encoding="utf-8") as handle:
        attachments = json.load(handle)
    for record in attachments["attachments"]:
        if record["email_id"] == EMAIL_ID:
            break
    else:
        raise SystemExit("attachments.json has no record for " + EMAIL_ID)
    derived = attachment_digest(seed, record["filename"])
    if record["sha256"] != derived:
        raise SystemExit("attachments.json sha256 is not sha256(seed|id|filename)")
    return record


def mailstore(address):
    """The one store that holds this mailbox.

    The recipient is a person and she is also the reporter, so the copy the
    corpus keeps is the copy delivered to the To address and there is no list
    expansion to account for.
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


# ---------------------------------------------------------------- body text
#
# One sentence of author text. The lure is the attachment, not the prose, and
# a body that argued for itself would give a week 7 reader something to weigh
# against the stripped-file header, which is the fact this message exists to
# teach. "invoice" and "net 15" are the two content:payment_request phrases
# from spec/enums.json that the record keys on; the message carries no link,
# so there is no url indicator to find and check_urls has nothing to answer.

BANNER = "[External message. Sentrywick Gateway]"
BANNER_HTML = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;'
               'font-size:12px;color:#5a4a00;">' + BANNER + '</p>')

AUTHOR_LINE = "Please find attached invoice 88213, net 15. Thank you for your business."
SIGNATURE = "Cindermill Signs, Billing"

PAYMENT_PHRASES = ["invoice", "net 15"]


# The gateway's removal notice, in the three pieces the two parts assemble it
# from. Section 2 of docs/email-header-realism.md fixes the wording, not where
# a source line may end, and the two parts do not break it in the same place:
# the plain part carries the file name up on the first line, while the HTML
# part ends its first line after the colon so that the opening <p> tag and the
# file name are not crowded onto one over-long source line. Both decode to the
# same sentence, so a part-to-part diff is still empty.
NOTICE_HEAD = "[Sentrywick Gateway removed 1 attachment:"
NOTICE_TAIL = "Details are in the message headers.]"


def notice_file(record):
    return record["filename"] + " ({:,} bytes).".format(record["size"])


def plain_part(record):
    return [
        BANNER,
        "",
        AUTHOR_LINE,
        "",
        SIGNATURE,
        "",
        NOTICE_HEAD + " " + notice_file(record),
        NOTICE_TAIL,
    ]


def html_part(record):
    return [
        "<html>",
        '<body style="margin:0;padding:0;background:#ffffff;">',
        BANNER_HTML,
        '<div style="font-family:sans-serif;font-size:14px;color:#222222;">',
        "<p>" + AUTHOR_LINE + "</p>",
        "<p>" + SIGNATURE + "</p>",
        "</div>",
        '<p style="font-size:12px;color:#6b6b6b;">' + NOTICE_HEAD,
        notice_file(record) + " " + NOTICE_TAIL + "</p>",
        "</body>",
        "</html>",
    ]


def qp(lines):
    """Quoted-printable body, 76-character limit, CRLF soft breaks.

    body_encode is the encoder the file was rendered with. It breaks at 75
    characters and appends the soft break rather than looking for a space, so
    the mid-word splits in the committed file come from here.
    """
    return quoprimime.body_encode("\n".join(lines), maxlinelen=76, eol=CRLF)


# ------------------------------------------------------------------- render

def build_eml(seed):
    record = attachment_record(seed)
    store = mailstore(RECIPIENT)
    lmtp_id = store_id(seed)
    gateway_uid = hexid(seed, "gateway-message-uid", 12)
    relay_id = hexid(seed, "relay-smtp-id", 8)
    boundary = "=_swk_" + hexid(seed, "mime-boundary", 12)
    message_id = ("<20260423121200." + hexid(seed, "message-id", 12)
                  + "@" + ORIGIN_HOST + ">")

    headers = [
        "Return-Path: <" + SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; Thu, 23 Apr 2026 07:12:08 -0500",
        "Authentication-Results: " + GATEWAY_HOST + ";",
        "  spf=softfail smtp.mailfrom=" + SENDER_DOMAIN + ";",
        "  dkim=none;",
        "  dmarc=none header.from=" + SENDER_DOMAIN,
        "Received-SPF: softfail (" + GATEWAY_HOST + ": domain of transitioning",
        "  " + SENDER + " does not designate " + RELAY_IP + " as",
        "  permitted sender) receiver=" + GATEWAY_HOST + ";",
        "  client-ip=" + RELAY_IP + '; envelope-from="' + SENDER + '";',
        "  helo=" + RELAY_HOST + "; identity=mailfrom; mechanism=~all",
        "X-Sentrywick-External: yes",
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Spam-Score: " + SPAM_SCORE,
        "X-Sentrywick-Message-UID: " + gateway_uid,
        "X-Sentrywick-Reported-By: " + REPORTER,
        'X-Sentrywick-Removed-Attachment: filename="' + record["filename"] + '";',
        "  size=" + str(record["size"]) + ";",
        "  sha256=" + record["sha256"] + ";",
        "  action=" + record["action"] + "; type=" + record["type"]
        + "; reason=" + record["reason"],
        "Received: from " + RELAY_HOST,
        "  (" + RELAY_HOST + " [" + RELAY_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPS",
        "  (TLS1_3 TLS_AES_256_GCM_SHA384) id " + gateway_uid + ";",
        "  Thu, 23 Apr 2026 07:12:06 -0500",
        "Received: from " + ORIGIN_HOST + " ([" + ORIGIN_IP + "])",
        "  by " + RELAY_HOST + " with ESMTP id " + relay_id + ";",
        "  Thu, 23 Apr 2026 12:12:02 +0000",
        "Date: Thu, 23 Apr 2026 07:12:00 -0500",
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT,
        "Subject: " + SUBJECT,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
    ]

    def part(subtype, lines):
        return (
            "--" + boundary + CRLF
            + "Content-Type: text/" + subtype + "; charset=utf-8" + CRLF
            + "Content-Transfer-Encoding: quoted-printable" + CRLF
            + CRLF
            + qp(lines) + CRLF
        )

    message = (
        CRLF.join(headers) + CRLF
        + CRLF
        + part("plain", plain_part(record))
        + part("html", html_part(record))
        + "--" + boundary + "--" + CRLF
    )

    data = message.encode("ascii")
    if b"\n" in data.replace(b"\r\n", b"") or b"\r" in data.replace(b"\r\n", b""):
        raise SystemExit("a line ends with something other than CRLF")
    for raw in data.split(b"\r\n"):
        if len(raw) > 78:
            raise SystemExit("line over 78 characters: " + raw.decode("ascii"))
        for byte in raw:
            if byte != 9 and not 0x20 <= byte <= 0x7E:
                raise SystemExit("byte outside the seven-bit printable range")
    return data, record


# ------------------------------------------------------------ ground truth

REFERENCE_SUMMARY = (
    "The 'invoice' attached to this message was a program file disguised "
    "as a PDF, and our mail gateway removed it before it reached you. "
    "Nothing ran on your computer, and we are checking whether anyone else "
    "got a copy."
)

NOTES = (
    "The batch set's easy malware delivery case. A one-line invoice email "
    "spoofs Cindermill Signs, a small sign company the organization has "
    "never dealt with, and carries a file named Invoice_88213.pdf.exe, a "
    "program file dressed as a PDF. The gateway stripped it for a blocked "
    "extension and left the filename, size and digest in "
    "X-Sentrywick-Removed-Attachment, so the .eml holds only text; this is "
    "the sample chosen to prove that the stripped-attachment convention "
    "downloads cleanly. Key facts: From domain cindermill-signs.example "
    "under the display name Cindermill Signs Billing; no Reply-To; the "
    "message entered through mta-9.cheapsend-relay.example "
    "(198.51.100.146), a relay outside the sign company's SPF record (mx "
    "~all), so spf=softfail; no DKIM signature, so dkim=none; the domain "
    "publishes no DMARC record, so dmarc=none with no policy.dmarc and "
    "dmarc_policy null; scan result suspect, spam score 6.9; no link; a "
    "new thread. Message-ID names api-node-02.cheapsend-relay.example, the "
    "originating host at the bottom of the Received chain, following the "
    "header specification convention; the relay provider appears only in "
    "the Received lines, the helo value and the Message-ID host, never as "
    "a From, Reply-To, Return-Path or link domain, the same treatment "
    "records 010 and 025 give it. Both body parts open with the gateway's "
    "canonical banner, [External message. Sentrywick Gateway], and close "
    "with the gateway's removal notice naming Invoice_88213.pdf.exe "
    "(184,320 bytes); both parts are quoted-printable because the banner "
    "snippet and the first notice line each run past 78 characters in "
    "source. Playbook rule 8 decides the case: a file removed for a "
    "blocked extension is malicious. Difficulty easy: one decisive "
    "malicious fact (attachment:blocked_extension), no pressure toward "
    "benign, no injection, and the body alone already reads as an "
    "unsolicited invoice with a double-extension attachment. Softfail is "
    "common and weak on its own; the lesson is that the attachment header, "
    "not the authentication line, carries the verdict. Tools: "
    "check_sender_reputation matches at domain level and returns unknown, "
    "first seen 2026-04-23, inside the window and six days before the "
    "corpus clock, so new_domain is true; lookup_recipient shows Priya "
    "Castellanos handles payments with six prior reports and four true "
    "positives, one of them tagged invoice-malware; check_urls has nothing "
    "to look up, so the loop stops on tools_exhausted after two calls. "
    "content:payment_request is not an ask code and the sender record "
    "carries no campaign tag, so recipient:prior_similar_report is absent "
    "under the prior_similar_report_rule even though the mailbox holds an "
    "invoice-malware report. Escalates under financial_or_endpoint_impact: "
    "malware sent to an accounts payable mailbox means the SOC searches "
    "the gateway log for the same filename and relay and confirms that "
    "nothing ran. Deliberate omissions, matching the manifest indicator "
    "list: no X-Originating-IP (reserved for webmail submissions), no "
    "X-Mailer, no Auto-Submitted, no X-Priority, no DKIM-Signature."
)


def ground_truth(record):
    return {
        "id": EMAIL_ID,
        "file": "emails/batch/" + EMAIL_ID + ".eml",
        "set": "batch",
        "weeks": [7],
        "date": "2026-04-23T07:12:00-05:00",
        "verdict": "malicious",
        "category": "malware_delivery",
        "difficulty": "easy",
        "body_only_read": "malicious",
        "sender_display": SENDER_DISPLAY,
        "sender_address": SENDER,
        "reply_to": None,
        "recipient": RECIPIENT,
        "reporter": REPORTER,
        "reported_after_interaction": False,
        "subject": SUBJECT,
        "arrival_path": "external_gateway",
        # No DMARC record exists, so the dmarc clause carries no policy.dmarc
        # and dmarc_policy stays null rather than none.
        "auth": {"spf": "softfail", "dkim": "none", "dmarc": "none",
                 "dmarc_policy": None},
        "indicators": [
            {"code": "auth:spf_softfail", "where": "Authentication-Results",
             "value": "spf=softfail smtp.mailfrom=" + SENDER_DOMAIN},
            {"code": "auth:dkim_none", "where": "Authentication-Results",
             "value": "dkim=none"},
            {"code": "auth:dmarc_none", "where": "Authentication-Results",
             "value": "dmarc=none header.from=" + SENDER_DOMAIN},
            {"code": "sender:first_seen", "where": "check_sender_reputation",
             "value": "2026-04-23"},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "yes"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "attachment:blocked_extension",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "attachment:double_extension",
             "where": "X-Sentrywick-Removed-Attachment",
             "value": record["filename"]},
            {"code": "content:payment_request", "where": "body",
             "value": "invoice; net 15"},
            {"code": "thread:new", "where": "In-Reply-To", "value": None},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
        ],
        "required_indicators": ["attachment:blocked_extension",
                                "attachment:double_extension"],
        "url_hosts": [],
        "attachment": {
            "filename": record["filename"],
            "size": record["size"],
            "sha256": record["sha256"],
            "action": record["action"],
            "type": record["type"],
            "reason": record["reason"],
        },
        "injection": None,
        "tool_expectations": {
            "check_sender_reputation": {
                "domain": SENDER_DOMAIN,
                "status": "unknown",
                "first_seen": "2026-04-23",
                "messages_90d": 1,
                "prior_reports": 0,
                "last_report_verdict": None,
                "last_report_date": None,
                "campaign_tag": None,
                "new_domain": True,
                "notes": "Small business domain; first seen inside the window (spoofed).",
                "match_level": "domain",
            },
            "check_urls": {},
            "lookup_recipient": {
                "address": RECIPIENT,
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
        # check_urls has nothing to answer, so the loop ends after two calls
        # with no tool left to try rather than on a decisive result.
        "expected_loop": {
            "tools": ["check_sender_reputation", "lookup_recipient"],
            "stop_reason": "tools_exhausted",
        },
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


def decoded_lines(text):
    """A decoded part back as the source lines it was written from.

    The soft line breaks the encoder inserted are gone by the time the parser
    hands the part back, so the only difference left is the line ending and a
    trailing newline the parser does not add.
    """
    return text.replace(CRLF, "\n").rstrip("\n").split("\n")


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
    if entry["attachment"]["filename"] != "Invoice_88213.pdf.exe":
        raise SystemExit("attachment filename does not match the manifest")

    data, record = build_eml(seed)
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
    if decoded_lines(parts[0]) != plain_part(record):
        raise SystemExit("the plain part does not decode to its source lines")
    if decoded_lines(parts[1]) != html_part(record):
        raise SystemExit("the html part does not decode to its source lines")
    for text in parts:
        if text.count(BANNER) != 1:
            raise SystemExit("the gateway banner must appear once in each part")
        if text.count(record["filename"]) != 1:
            raise SystemExit("the removal notice must name the file once per part")
        for phrase in PAYMENT_PHRASES:
            if phrase not in text:
                raise SystemExit("a part lost the phrase: " + phrase)
    if "http" in parts[0] or "http" in parts[1]:
        raise SystemExit("this message carries no link")
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))

    with open(GT_PATH, encoding="utf-8") as handle:
        truth = json.load(handle)
    records = truth["emails"]
    new_record = ground_truth(record)
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = new_record
            break
    else:
        records.append(new_record)
        records.sort(key=lambda existing: existing["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("upserted ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
