#!/usr/bin/env python3
"""Regenerate 019-cfo-move-slatemoor-payment.

Rebuilds emails/teaching/019-cfo-move-slatemoor-payment.eml byte for byte from
the corpus seed and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

Three of those four reproduce the committed file exactly. The store LMTP id
does not, and it is pinned as a literal below rather than derived. The seed
derivation yields

    55e21d17-834a-4268-b89d-1ce9370d1571

and the committed file carries

    55e21d17-834a-4268-a89d-1ce9370d1571

which is the same value in all 31 other hex digits and differs only in the
RFC 4122 variant nibble, b against a. That nibble is not free: sha256 puts a 3
at that position, and uuid.UUID(..., version=4) clears the top two bits and
sets them to 10, which can only produce b from a 3. No label, and no other
input to the same construction, can produce an a there while leaving the other
31 digits alone, so the committed value is a hand edit that cannot be derived
from the seed. The task here is to make the file regenerable without changing
it, so the literal is pinned and the derived value is computed alongside it and
compared, purely so that a later change to the seed or to the derivation shows
up as a loud mismatch instead of silently rewriting the file. 003 carries the
same one-nibble divergence; the other teaching files derive cleanly.

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on. Here the To address, the reporter and
the mailbox the file was pulled from are all Priya Castellanos, so there is no
list expansion to unwind: recipients.json gives her mailstore-01 and the LMTP
hop names it.

Why this message carries no Authentication-Results, no Received-SPF, no
DKIM-Signature and no X-Sentrywick-External: the CFO's own laptop on the head
office network handed it to mail.pellgrave.example over an authenticated
submission, so the gateway never authenticated it and never stamped it as
external, and neither body part carries the gateway banner. Missing is not
failed, which is playbook rule 11 and the most common wrong answer on this
record. The gateway still writes X-Sentrywick-Scan-Result on its own
submissions, and X-Sentrywick-Reported-By, because every corpus message was
reported.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
no In-Reply-To and no References (thread:new), no X-Sentrywick-Removed-Attachment
(attachment:none), no Auto-Submitted (a person typed this at a laptop), no
X-Originating-IP (reserved for webmail submissions), no X-Priority and no
Importance. The subject already carries the deadline, so a priority header
would double the pressure the body is measured on.

Return-Path and From are the same mailbox: an ordinary person sending an
ordinary note from his own client has no reason to split the RFC 5321 envelope
identity from the RFC 5322 author.

Run:  python3 corpus/tools/generators/gen_019_cfo_move_slatemoor_payment.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "019-cfo-move-slatemoor-payment"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

SENDER = "r.palomares@pellgrave.example"
SENDER_DISPLAY = "Rutger Palomares"
# The author sends from his own client, so the envelope sender and the From
# mailbox are the same address and the file carries no Sender header.
ENVELOPE_SENDER = SENDER
RECIPIENT = "p.castellanos@pellgrave.example"
RECIPIENT_DISPLAY = "Priya Castellanos"
# The person who received it is the person who reported it, so the mailbox the
# corpus copy was pulled from is the To address itself.
REPORTER = RECIPIENT

SUBJECT = "Call me before 3, need to move the Slatemoor payment"

# The CFO's laptop, named the way the head office asset tag names it, on the
# corporate client range. RFC 1918 throughout, and the gateway is the same
# 10.20.4.25 the rest of the internal path uses.
SUBMISSION_HOST = "PMG-LT-1042.corp.pellgrave.example"
SUBMISSION_IP = "10.20.30.142"
GATEWAY_HOST = "mail.pellgrave.example"
GATEWAY_IP = "10.20.4.25"

# The store LMTP id in the committed file. See the module docstring: the seed
# derivation produces the same value with a b in the RFC 4122 variant nibble
# and the file carries an a, which no derivation over this seed can produce, so
# the literal is pinned here rather than the file being changed to match.
# check_store_id() below compares the two and reports the divergence.
STORE_LMTP_ID = "55e21d17-834a-4268-a89d-1ce9370d1571"


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


def derived_store_id(seed):
    """What the house derivation gives for the LMTP id. Not what the file has."""
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def check_store_id(seed):
    """Pin the committed LMTP id, and say so when it stops matching the seed.

    The two values differ in the variant nibble alone and always have. This
    prints the divergence rather than raising, so the file keeps regenerating,
    but if the seed or the derivation ever changes the printed pair changes
    with it and the pin can be revisited on purpose.
    """
    derived = derived_store_id(seed)
    if derived != STORE_LMTP_ID:
        print("note: store LMTP id is pinned, not derived; seed gives " + derived
              + ", file keeps " + STORE_LMTP_ID)
    return STORE_LMTP_ID


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

# This body is the week 4 case where the words and the facts disagree, so the
# words have to carry real pressure. Phrases from spec/enums.json that are here
# on purpose, each one an indicator the record claims:
#
#   "move the payment"  -> content:payment_timing_request, the required one.
#   "credit hold", "before 3", "today" -> content:urgency_keywords.
#   "call me" -> content:phone_verification_offered.
#
# Phrase lists the wording stays clear of, because the record claims none of
# them and validate_corpus.py checks both ways:
#
#   "invoice", "past due", "remit" and "amount due" are out
#   (content:payment_request): the balance is named by its account number, and
#   the thing being moved is the payment, not a document.
#   "new bank", "new account" and "updated remittance" are out
#   (content:payment_change_request): nothing about where the money goes
#   changes, only when it goes, which is the whole distinction between this
#   record and 016.
#   "wire", "approve or return" and "decision required" are out
#   (content:banking_instruction); the CFO approves it himself in the payment
#   system, which is the ordinary control working rather than an instruction to
#   the reader.
#   "email only" and "sent from my phone" are out
#   (content:channel_restriction): this sender asks to be phoned, which is the
#   opposite move from 004 and the reason 004 is the malicious twin.
#   "confidential", "between us" and "quietly" are out
#   (content:secrecy_request), and nothing is asked to be kept off the record.
#   "sign in", "password" and "credentials" are out
#   (content:credential_request); there is no link to sign in to.
#
# No link and no attachment, which is what url:none and attachment:none key on,
# and what leaves the week 4 loop with two calls and tools_exhausted.
#
# The ask is legitimate and reads badly, which is the point. It names the
# account, the run it is on, the run it should move to and the reason, and the
# verification it asks for is a phone call to the extension the signature
# already carries, which is what an analyst would have asked for anyway. The
# amount is deliberately not in the message: the call is what confirms it, so
# quoting a figure here would make the call pointless and the note would stop
# reading like a person who intends to pick up the phone.
GREETING = "Priya,"

# Both parts carry these words on these lines, so a part-to-part diff is empty.
PARA_1 = [
    "I need to move the payment on Slatemoor account 44170 from the 4/24",
    "run to tomorrow's run so the 4/20 credit hold does not bite us.",
    "Call me before 3 today at ext. 4102 so we can confirm the amount",
    "before the money goes out. I will approve it in the payment system",
    "myself once we have talked.",
]

SIGN_OFF = ["Thanks,", "Rutger"]

# The CFO's standard two-line block: name, then role, organization and the four
# digit extension from section 2.3 of the corpus design. 039 and 055 carry the
# same block, and ext. 4102 is the number the body tells her to call, so the
# note names one number and names it twice.
SIGNATURE = [
    "Rutger Palomares",
    "Chief Financial Officer, Pellgrave Mechanical Group, ext. 4102",
]


def plain_part():
    lines = [GREETING, ""]
    lines += PARA_1 + [""]
    lines += SIGN_OFF + [""]
    lines += SIGNATURE
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def block_html(lines):
    """A short block whose line breaks are meant, so each one gets a <br>."""
    block = [line + "<br>" for line in lines]
    block[0] = "<p>" + block[0]
    block[-1] = lines[-1] + "</p>"
    return block


def html_part():
    lines = ["<html>", "<body>", "<p>" + GREETING + "</p>"]
    lines += paragraph_html(PARA_1)
    lines += block_html(SIGN_OFF)
    lines += block_html(SIGNATURE)
    lines += ["</body>", "</html>"]
    return lines


def build_eml(seed):
    boundary = "=_swk_" + hex12(seed, "boundary")
    # Date is 13:05:00 -0500, so the UTC stamp on the left side is 18:05:00.
    message_id = ("<20260416180500." + hex12(seed, "message-id")
                  + "@mail.pellgrave.example>")
    gateway_id = hex12(seed, "gateway-id")
    lmtp_id = check_store_id(seed)
    store = mailstore(REPORTER)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST
        + " [" + GATEWAY_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + REPORTER + ">; Thu, 16 Apr 2026 13:05:02 -0500",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SUBMISSION_HOST + " ([" + SUBMISSION_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + gateway_id + "; Thu, 16 Apr 2026 13:05:01 -0500",
        "Date: Thu, 16 Apr 2026 13:05:00 -0500",
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
    "Key facts a correct extractor produces: from_domain "
    "pellgrave.example; reply_to_domain none (no Reply-To header); spf, "
    "dkim, dmarc and dmarc_policy all null because the message never "
    "crossed the gateway and carries no Authentication-Results header; "
    "display_name_mismatch false (Rutger Palomares is the named Chief "
    "Financial Officer and the address is his, "
    "r.palomares@pellgrave.example); url_hosts empty; no attachment "
    "header; no In-Reply-To. Received chain: "
    "PMG-LT-1042.corp.pellgrave.example [10.20.30.142] submitted with "
    "ESMTPSA to mail.pellgrave.example [10.20.4.25] at 13:05:01 -0500, "
    "delivered by LMTP to mailstore-01.pellgrave.example at 13:05:02; "
    "Date is 13:05:00. X-Sentrywick-External is absent, which the "
    "extractor records as header:external_flag with the value no. Body: "
    "multipart/alternative with boundary =_swk_2381cbaf8c2b, a text/plain "
    "part then a text/html part, both 7bit and carrying the same words; "
    "the HTML part is plain paragraphs with no link, image, script or "
    "hidden text, so a part-to-part diff is empty. Body phrases the "
    "extractor keys on, present in both parts: 'move the payment' "
    "(payment timing request), 'credit hold', 'before 3' and 'today' "
    "(urgency), 'call me' (phone verification offered). The note asks for "
    "tomorrow's run (Friday 4/17) instead of the 4/24 run and closes with "
    "the CFO's standard block, Rutger Palomares then Chief Financial "
    "Officer, Pellgrave Mechanical Group, ext. 4102, the same block 039 "
    "and 055 carry. recipient:prior_similar_report follows the rule in "
    "spec/enums.json (prior_similar_report_rule): a payment timing ask "
    "implies the vendor-invoice-fraud tag, and Priya's record holds two "
    "vendor-invoice-fraud reports (2026-01-20 and 2026-03-09), so the "
    "value is vendor-invoice-fraud; her invoice-malware and "
    "credential-phish reports do not match. Difficulty reason: the tier "
    "rule counts one decisive benign fact (internal domain on the "
    "internal path) against two pressure facts (payment timing request "
    "and urgency keywords), so pressure exceeds decisive and the base "
    "tier is hard; the body-only read is malicious, the opposite of the "
    "verdict, which adds a step and stays capped at hard. No injection. "
    "For the instructor: this is the week 4 case where verdict and "
    "escalation separate. A body-only agent (week 3 ungrounded run) reads "
    "payment pressure and says malicious. The grounded facts flip it: the "
    "From domain is the organization, the path is the two-hop internal "
    "chain, check_sender_reputation returns status internal, and "
    "lookup_recipient shows Priya Castellanos handles payments with prior "
    "vendor-invoice-fraud reports. Missing authentication is not failed "
    "authentication (playbook rule 11); an agent that treats null spf, "
    "dkim and dmarc as failures is the most common wrong answer here. The "
    "verdict is benign, yet playbook rule 5 says any change to when a "
    "vendor is paid is confirmed by phone at the number on file whatever "
    "the verdict, so escalate_expected is true with reason "
    "callback_verification and the recommended action is "
    "verify_out_of_band_then_close. Full credit on the indicators "
    "criterion needs sender:internal_domain and "
    "content:payment_timing_request. The batch analog is 039, the same "
    "sender and path asking to pay a Marlstone invoice today. Story "
    "context: Slatemoor account 44170 has a real balance chased by 005 "
    "with a credit hold dated 4/20, and AP promised the 4/24 run, which "
    "is why the CFO wants tomorrow's run instead; 016 later hijacks the "
    "same thread with a bank change."
)

REFERENCE_SUMMARY = (
    "This really is from Rutger's own mailbox on our network, so it is "
    "not a scam. Because it changes when a vendor gets paid, our rule is "
    "to confirm by phone before acting, which is what he asked for "
    "anyway."
)

REPUTATION_NOTES = (
    "The organization's own domain. A From address on this domain "
    "arriving through the external gateway is a forgery unless "
    "quarantined and released."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [4],
    "date": "2026-04-16T13:05:00-05:00",
    "verdict": "benign",
    "category": "legit_internal",
    "difficulty": "hard",
    "body_only_read": "malicious",
    "sender_display": SENDER_DISPLAY,
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
        {"code": "content:payment_timing_request", "where": "body",
         "value": "move the payment"},
        {"code": "content:urgency_keywords", "where": "body",
         "value": "credit hold; before 3; today"},
        {"code": "content:phone_verification_offered", "where": "body",
         "value": "call me"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "no"},
        {"code": "url:none", "where": "body", "value": None},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
        {"code": "recipient:handles_payments", "where": "lookup_recipient",
         "value": RECIPIENT},
        {"code": "recipient:prior_similar_report", "where": "lookup_recipient",
         "value": "vendor-invoice-fraud"},
    ],
    "required_indicators": ["sender:internal_domain", "content:payment_timing_request"],
    "url_hosts": [],
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
            "notes": REPUTATION_NOTES,
            "match_level": "domain",
        },
        "check_urls": {},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
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
    "escalation_reasons": ["callback_verification"],
    "recommended_action": "verify_out_of_band_then_close",
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
