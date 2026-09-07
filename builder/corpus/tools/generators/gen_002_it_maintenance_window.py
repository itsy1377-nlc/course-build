#!/usr/bin/env python3
"""Regenerate 002-it-maintenance-window.

Rebuilds emails/teaching/002-it-maintenance-window.eml byte for byte from the
corpus seed and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. The mailbox this file was pulled from
is not the To address: recipients.json gives the list a store of its own for
lookup_recipient, but a list is delivered by expansion at the submission host,
every member's store takes a copy, and the corpus keeps the copy the reporter
had in front of him when he reported it. So the LMTP hop
delivers for the reporter, on the reporter's store, while To stays the list and
the record keeps the list as the recipient.

Return-Path carries noreply@pellgrave.example, the ticket system's own
mailbox in data/recipients.json, while From stays the shared help desk
mailbox that signs the notice. A broadcast to a several-hundred-member list
aims its bounces at a mailbox nobody works rather than at the queue the help
desk reads, which is the same reason it sets Auto-Submitted.

Why this message carries no Authentication-Results, no Received-SPF, no
DKIM-Signature and no X-Sentrywick-External: the ticket host handed it to
mail.pellgrave.example over an authenticated submission, so the gateway never
authenticated it and never stamped it as external. Missing is not failed. The
gateway still writes X-Sentrywick-Scan-Result on its own submissions, and
X-Sentrywick-Reported-By, because every corpus message was reported.

Auto-Submitted: auto-generated is present, and the record carries the matching
header:auto_submitted indicator. RFC 3834 sec. 5 defines the field for system
notices, and the ticket system sets it on a broadcast so that out-of-office
replies from several hundred mailboxes do not land back in the shared help desk
mailbox. It creates no real-versus-fake tell against 006, which arrives through
the gateway and is already separated by X-Sentrywick-External, its From domain
and its lookalike link host.

Headers deliberately absent, matching the manifest indicator list: no
Thread-Topic (the internal submission host stamps it only on threaded mail and
this message starts a thread), no X-Originating-IP (reserved for webmail
submissions, and header:x_originating_ip is checked both ways), no X-Priority
and no Importance.

Run:  python3 corpus/tools/generators/gen_002_it_maintenance_window.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "002-it-maintenance-window"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "helpdesk@pellgrave.example"
# The envelope sender is not the From mailbox. A ticket system that broadcasts
# to a several-hundred-member list puts the bounce address on a mailbox nobody
# works, so the delivery failures from those mailboxes do not land in the
# monitored shared help desk mailbox the notice is signed with. That is the
# same reason the message carries Auto-Submitted. data/recipients.json records
# noreply@pellgrave.example as the ticket system sender with worked_by null.
# Return-Path is an RFC 5321 envelope identity and From is the RFC 5322 author,
# so the two differ without a Sender header and without any indicator: both
# addresses are on pellgrave.example, so the organizational domain is the same
# one the internal-path facts key on.
ENVELOPE_SENDER = "noreply@pellgrave.example"
RECIPIENT = "all-staff@pellgrave.example"
REPORTER = "c.hallowden@pellgrave.example"

SUBJECT = ("Planned maintenance: portal and field app offline Saturday 4/18, "
           "6:00 to 9:00 AM")
# RFC 5322 sec. 2.2.3: fold by inserting CRLF before existing white space, so
# the continuation line keeps the single space the subject already had and the
# unfolded value is the subject byte for byte.
SUBJECT_HEAD = "Planned maintenance: portal and field app offline Saturday 4/18,"
SUBJECT_TAIL = "6:00 to 9:00 AM"

STATUS_URL = "https://portal.pellgrave.example/status"


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient, reporter):
    """The mailbox this file was pulled from and the one store that holds it.

    A person or a shared mailbox receives the message itself. A distribution
    list is delivered by expansion instead: recipients.json records a store for
    the list, and the message expands at the submission host so that every
    member's store takes a copy. The file the corpus keeps is the copy in the
    reporter's mailbox, so the LMTP hop names the reporter and the reporter's
    store.
    """
    entry = recipient_record(recipient)
    if entry.get("mailbox_type") == "list":
        entry = recipient_record(reporter)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


# ---------------------------------------------------------------- body text

# Wording rules this text obeys, all from spec/enums.json content_phrases. The
# record carries no content code, so no phrase from any content list may appear
# in either decoded part; validate_corpus.py checks that both ways.
#
#   "today", "immediately", "expires in", "action required", "urgent" and the
#   rest of content:urgency_keywords are out, which is why the window is named
#   by its date and its clock times and never by a countdown.
#   "sign in", "log in", "password" and "credentials" are out: an internal
#   notice that asked for any of them would carry content:credential_request,
#   and a help desk that never links to a sign-in page is the contrast this
#   message exists to draw against 006.
#   "download" is out (content:file_share_lure), so the status page is named
#   as a page to read.
#   "not working" is out (content:excuse_for_external_address), so the field
#   app "will not respond".
#   "was changed" and "if you did not" are out (content:account_change_notice).
#   "call me" and "call the number on file" are out
#   (content:phone_verification_offered); the help desk extension is a contact
#   route for a service that did not come back, not an offer to confirm a
#   request by phone, and no phrase from that list appears.
#
# The one link is the internal status page, which is the fact
# url:host_internal_known_good keys on, and the bare host name appears in the
# prose as well so a week 1 reader who is given only the body can see that the
# link goes to the company's own portal.
#
# The status page is carved out of the outage in the same sentence that names
# the outage, because a maintenance page that goes down with the service it
# reports on is either careless or fabricated, and this is the file whose whole
# job is to read as ordinary. Saturday morning is working time at a mechanical
# contractor with roughly 420 field technicians, so the notice says the Saturday
# crews take their assignments from dispatch by phone as usual instead of
# asserting that nothing is affected. Dispatch is an operations function and IT
# owns no dispatch extension, so the notice names no number for it: the only
# extension in the body is the help desk's own, in the closing line and in the
# signature. The paragraph names the window once and then stops qualifying: a
# real notice does not repeat its own condition inside four lines, and this is
# the first body a student ever sends, so it cannot read as generated text.
GREETING = "All,"

PARA_1 = [
    "The intranet portal and the field service app go offline for planned",
    "maintenance on Saturday 4/18, from 6:00 to 9:00 AM. Both come back on",
    "their own when the work finishes, and there is nothing anyone needs to",
    "do before or after.",
]

PARA_2 = [
    "While the window is open, portal.pellgrave.example serves only the",
    "status page, and the field app will not respond. Everything else keeps",
    "running: email, phones, the warehouse scanners and the badge readers.",
    "Saturday crews get their assignments from dispatch by phone as usual.",
]

PARA_3 = [
    "That status page stays up through the whole window and is the quickest",
    "place to see where the work stands:",
]

PARA_4 = [
    "If part of the portal or the app is still down after 9:00, call the",
    "help desk at ext. 4400 and reference PMG-HD-20488, and we will pick it",
    "up from there.",
]

# House signature for a shared mailbox: the mailbox's own name and the four
# digit extension from section 2.3 of the corpus design.
SIGNATURE = "Pellgrave IT Help Desk, ext. 4400"


def plain_part():
    lines = [GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += PARA_3 + [""]
    lines += [STATUS_URL, ""]
    lines += PARA_4 + [""]
    lines += [SIGNATURE]
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def html_part():
    lines = ["<html>", "<body>", "<p>" + GREETING + "</p>"]
    lines += paragraph_html(PARA_1)
    lines += paragraph_html(PARA_2)
    lines += paragraph_html(PARA_3)
    # The href and the visible text are the same address, the way a plain
    # internal notice writes a link, so a reader of either part sees the host.
    lines += ['<p><a href="' + STATUS_URL + '"', "  >" + STATUS_URL + "</a></p>"]
    lines += paragraph_html(PARA_4)
    lines += ["<p>" + SIGNATURE + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


def build_eml(seed):
    boundary = "=_swk_" + hex12(seed, "boundary")
    message_id = ("<20260413131500." + hex12(seed, "message-id")
                  + "@mail.pellgrave.example>")
    gateway_id = hex12(seed, "gateway-id")
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from mail.pellgrave.example (mail.pellgrave.example [10.20.4.25])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; Mon, 13 Apr 2026 08:15:02 -0500",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from helpdesk-app.corp.pellgrave.example ([10.20.8.15])",
        "  by mail.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + gateway_id + "; Mon, 13 Apr 2026 08:15:01 -0500",
        "Date: Mon, 13 Apr 2026 08:15:00 -0500",
        "From: Pellgrave IT Help Desk <" + SENDER + ">",
        "To: All Staff Distribution List <" + RECIPIENT + ">",
        "Subject: " + SUBJECT_HEAD,
        " " + SUBJECT_TAIL,
        "Message-ID: " + message_id,
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
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += html_part()
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null, because the message never crossed the border "
    "gateway and the file carries no Authentication-Results header at all; "
    "display_name_mismatch false, since Pellgrave IT Help Desk is an owned "
    "name in data/display_names.json, owned by pellgrave.example and sourced "
    "from the shared mailbox helpdesk@pellgrave.example; url_hosts "
    "portal.pellgrave.example, from one link that appears once in the plain "
    "part and once in the HTML part, where the href and the visible text are "
    "the same address; no removed-attachment header; no In-Reply-To and no "
    "References, so the thread is new. Received chain: "
    "helpdesk-app.corp.pellgrave.example [10.20.8.15], the ticket system's "
    "submission host, handed the message to mail.pellgrave.example "
    "[10.20.4.25] with ESMTPSA at 08:15:01 -0500, and mail.pellgrave.example "
    "delivered it by LMTP to mailstore-01.pellgrave.example at 08:15:02; Date "
    "is 08:15:00. The list expanded at the submission host, so this file is "
    "the copy delivered to the reporter's own mailbox: the LMTP hop reads for "
    "<c.hallowden@pellgrave.example> and names mailstore-01, the store "
    "data/recipients.json gives that mailbox, while To stays "
    "all-staff@pellgrave.example, which is what recipient:distribution_list "
    "and the lookup_recipient expectation key on. recipients.json records "
    "mailstore-02 for the list itself, but the copy the corpus keeps is the "
    "one delivered to an individual member, so the LMTP hop names the "
    "reporter's own store, mailstore-01; every mailbox in the corpus lives on "
    "exactly one store whatever path a message took. Return-Path is "
    "<noreply@pellgrave.example> while From is helpdesk@pellgrave.example: "
    "the ticket system puts the envelope sender on its own mailbox, the one "
    "data/recipients.json records with worked_by null, so the delivery "
    "failures from several hundred list members go to a mailbox nobody works "
    "instead of the monitored shared help desk mailbox the notice is signed "
    "with. It is the same reason the message carries Auto-Submitted. The "
    "envelope sender is an RFC 5321 identity and the From mailbox is the "
    "RFC 5322 author, so the two differ on purpose, with no Sender header and "
    "no indicator: both addresses sit on pellgrave.example, which is the "
    "organizational domain sender:internal_domain keys on. "
    "X-Sentrywick-External is absent, "
    "which the extractor records as header:external_flag with the value no, "
    "and neither body part carries the gateway banner, because the gateway "
    "inserts it only into the mail it stamps as external. The gateway still "
    "wrote X-Sentrywick-Scan-Result: clean on its own submission, and "
    "X-Sentrywick-Reported-By names Casimir Hallowden, who reported it. The "
    "ticket system broadcasts this notice to a distribution list, so it also "
    "carries Auto-Submitted: auto-generated, the RFC 3834 section 5 header "
    "that keeps out-of-office replies from several hundred mailboxes out of "
    "the shared help desk mailbox; the extractor records it as "
    "header:auto_submitted. Body: multipart/alternative, a text/plain part "
    "then a text/html part, both 7bit and carrying the same words, so a "
    "part-to-part diff is empty; the HTML part is plain paragraphs with one "
    "anchor and no image, script, form, styling trick or hidden text. Content: "
    "the help desk announces that the intranet portal and the field service "
    "app go offline for planned maintenance on Saturday 4/18 from 6:00 to 9:00 "
    "AM, that both come back on their own and nothing is required of anyone, "
    "that portal.pellgrave.example serves only the status page while the "
    "window is open and the field app will not respond, that everything else "
    "keeps running and Saturday crews get their assignments from dispatch by "
    "phone as usual, "
    "that the status page at https://portal.pellgrave.example/status stays up "
    "through the window and shows where the work stands, and that anything still "
    "down after 9:00 goes to the help desk on ext. 4400 with a reference to "
    "ticket PMG-HD-20488. It signs with the shared mailbox name and extension "
    "4400. The status page is carved out of the outage in the sentence that "
    "names the outage, so the one link in the message does not point at a host "
    "the message has just called unreachable, and the Saturday crews on phone "
    "dispatch keep a Saturday morning window credible at a contractor whose "
    "field technicians work Saturdays. Dispatch is an operations function and "
    "IT owns no dispatch extension, so the notice names no number for it and "
    "the help desk extension appears only in the closing line and the "
    "signature. Nothing in it asks for credentials, a payment, a payment "
    "date, data, secrecy or a reply on another channel; that extension is a "
    "contact route for a service that did not come back, not an offer to "
    "confirm a request by phone, so content:phone_verification_offered does "
    "not fire and no phrase from its list appears. The wording stays clear of "
    "every phrase list in spec/enums.json, which is why the window is named by "
    "its date and its clock times rather than by a countdown, why the field "
    "app will not respond rather than stop working, and why the record carries "
    "no content code. Difficulty reason: the tier rule counts one decisive "
    "benign fact, the organization's own domain on the internal path, against "
    "no pressure facts, so the base tier is easy; the body-only read is "
    "benign, the same as the verdict, so no adjustment applies. No injection. "
    "For the instructor: this is the week 1 contrast body. In week 1 the "
    "students send this body to the model with no extracted facts and no "
    "tools, and it has to read as ordinary internal housekeeping on its own "
    "words alone, against 001, the payroll deposit lure that is the other "
    "week 1 body. The forged copy of this help desk name is 006, which "
    "arrives in week 3, and its honest twin is 051 in the exam set; neither "
    "of those is in front of a student in week 1 or week 2. "
    "In week 2 the same body has to come back as "
    "strict JSON with verdict benign and category legit_internal. Full credit "
    "on the indicators criterion needs sender:internal_domain and "
    "url:host_internal_known_good, the two facts that separate this notice "
    "from an imitation of it: the sender is the organization's own domain "
    "arriving on the internal path, and the one link goes to a host on the "
    "internal known-good list in data/known_good_domains.json. The week 4 loop "
    "should stop after one call: check_sender_reputation returns status "
    "internal at domain level, which is the stated stop condition, so "
    "stop_reason is internal_sender; check_urls would only confirm that "
    "portal.pellgrave.example is internal, and lookup_recipient would only "
    "confirm that all-staff@pellgrave.example is a distribution list with no "
    "report history of its own. Escalation: none. The verdict is benign, the "
    "category is legit_internal, and no benign escalation rule fits, since "
    "nothing here fails authentication on a trusted sender, touches a banking "
    "item or asks an unknown sender's question, so recommended_action is "
    "close_benign_reply_to_reporter. Story context: Casimir Hallowden reports "
    "almost every message that carries a link, and his record shows 11 prior "
    "reports with 0 true positives, so a benign internal notice is exactly "
    "what his reports usually are. The queue needs that traffic: an agent that "
    "never sees a real help desk notice learns to treat the help desk name "
    "itself as the tell."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [1, 2],
    "date": "2026-04-13T08:15:00-05:00",
    "verdict": "benign",
    "category": "legit_internal",
    "difficulty": "easy",
    "body_only_read": "benign",
    "sender_display": "Pellgrave IT Help Desk",
    "sender_address": SENDER,
    "reply_to": None,
    "recipient": RECIPIENT,
    "reporter": REPORTER,
    "reported_after_interaction": False,
    "subject": SUBJECT,
    "arrival_path": "internal",
    "auth": {"spf": None, "dkim": None, "dmarc": None, "dmarc_policy": None},
    "indicators": [
        {"code": "auth:not_evaluated_internal", "where": "Authentication-Results",
         "value": None},
        {"code": "sender:internal_domain", "where": "From, Received",
         "value": "pellgrave.example"},
        {"code": "url:host_internal_known_good", "where": "check_urls",
         "value": "portal.pellgrave.example"},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "no"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:distribution_list", "where": "lookup_recipient",
         "value": RECIPIENT},
    ],
    "required_indicators": ["sender:internal_domain", "url:host_internal_known_good"],
    "url_hosts": ["portal.pellgrave.example"],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": "pellgrave.example",
            "status": "internal",
            "first_seen": "2019-05-01",
            "messages_90d": 0,
            "prior_reports": 0,
            "last_report_verdict": None,
            "last_report_date": None,
            "campaign_tag": None,
            "new_domain": False,
            "notes": ("The organization's own domain. A From address on this domain "
                      "arriving through the external gateway is a forgery unless "
                      "quarantined and released."),
            "match_level": "domain",
        },
        "check_urls": {"portal.pellgrave.example": "internal"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "All Staff Distribution List",
            "role": "distribution list",
            "mailbox_type": "list",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 0,
            "true_positive_count_90d": 0,
            "campaign_tags": [],
        },
    },
    "expected_loop": {"tools": ["check_sender_reputation"], "stop_reason": "internal_sender"},
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_benign_reply_to_reporter",
    "reference_summary": ("This is a real notice from our own help desk about "
                          "Saturday's maintenance. Nothing needs to be done, and "
                          "thank you for checking before clicking."),
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
