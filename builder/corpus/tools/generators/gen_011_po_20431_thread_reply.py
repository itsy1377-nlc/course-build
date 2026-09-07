#!/usr/bin/env python3
"""Regenerate 011-po-20431-thread-reply.

Rebuilds emails/teaching/011-po-20431-thread-reply.eml byte for byte from the
corpus seed, refreshes the matching manifest fields in spec/corpus-spec.json,
and upserts the ground truth record in ground_truth.json.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex12(label) = sha256("<seed>|<email id>|<label>").hexdigest()[:12]
    Message-ID left side  = <UTC stamp>.hex12("message-id")
    MIME boundary         = "=_swk_" + hex12("boundary")
    gateway Received id   = hex12("gateway-id"), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

The delivering mail store is read from data/recipients.json, because a mailbox
lives on exactly one store and the LMTP hop is a property of the mailbox rather
than of the path the message arrived on.

Run:  python3 corpus/tools/generators/gen_011_po_20431_thread_reply.py
"""

import hashlib
import json
import os
import uuid

EMAIL_ID = "011-po-20431-thread-reply"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "teaching", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"


def hex12(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:12]


def store_id(seed):
    digest = hashlib.sha256((seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


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

# The verb is "billed", not the noun "invoice": "invoice" sits in the
# content:payment_request phrase list in spec/enums.json and this record
# carries no content code. "Billing" as a mass noun is how the trade writes it,
# which is why the quoted lines below keep it, but a document number belongs to
# a verb here rather than to that mass noun.
PARA_1 = [
    "Slatemoor billed PO 20431 on 44170-112 and every line matches, so it goes",
    "out on the 4/24 run with the rest of that batch.",
]

# Priya works the shared AP mailbox (data/recipients.json, ap@ worked_by
# p.castellanos@). The reply gives the reason for the Cc and nothing else: a
# body claim about which mailbox sent a message is the sender fact the week 5
# stop condition turns on, and narrating it here would let a model answer
# without calling check_sender_reputation. "today" is avoided on the same
# grounds as "invoice": it is a content:urgency_keywords phrase.
PARA_2 = [
    "I kept ap@ on copy so whoever is at the desk can pick the thread up if",
    "I am out.",
]

# House signature pattern for internal mail: name, role from
# data/recipients.json, organization, four-digit extension. 4102 is the CFO
# and 4400 the help desk; 4118 is unused.
SIGNATURE = [
    "Priya Castellanos",
    "Accounts Payable Specialist, Pellgrave Mechanical Group, ext. 4118",
]

# Two quote levels, parent first, matching In-Reply-To. The outer level is
# AP's reply of 13 April (known_threads.json); the 9 April grandparent from
# Emeric Dawodu is nested one level inside it, which is the shape a client
# produces when it replies to the 13 April message.
QUOTE_OUTER_ATTRIB = "On Mon, 13 Apr 2026 at 10:12, Accounts Payable wrote:"
QUOTE_OUTER_BODY = [
    "Received, thanks. Nothing goes on a run until Slatemoor's billing",
    "lines up with the PO.",
]
QUOTE_INNER_ATTRIB = "On Thu, 9 Apr 2026 at 16:15, Emeric Dawodu wrote:"
QUOTE_INNER_BODY = [
    "PO 20431 went over to Slatemoor for the two compressors and the",
    "mounting kit, delivery to the head office dock. Please match their",
    "billing to this PO before anything goes on a run.",
]


def plain_part():
    lines = ["Emeric,", ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += ["Priya", ""]
    lines += SIGNATURE + [""]
    lines += [QUOTE_OUTER_ATTRIB]
    lines += ["> " + line for line in QUOTE_OUTER_BODY]
    lines += [">"]
    # The attribution line sits at the level of the message doing the quoting,
    # so the 13 April message owns it and it stays at one ">". Emeric's own
    # words are one level deeper. The HTML part nests the same two levels.
    lines += ["> " + QUOTE_INNER_ATTRIB]
    lines += [">> " + line for line in QUOTE_INNER_BODY]
    return lines


def html_part():
    lines = ["<html>", "<body>", "<p>Emeric,</p>"]
    lines += ["<p>" + PARA_1[0], PARA_1[1] + "</p>"]
    lines += ["<p>" + PARA_2[0], PARA_2[1] + "</p>"]
    lines += ["<p>Priya</p>"]
    lines += ["<p>" + SIGNATURE[0] + "<br>", SIGNATURE[1] + "</p>"]
    lines += ["<p>" + QUOTE_OUTER_ATTRIB + "</p>", "<blockquote>"]
    lines += ["<p>" + QUOTE_OUTER_BODY[0], QUOTE_OUTER_BODY[1] + "</p>"]
    lines += ["<p>" + QUOTE_INNER_ATTRIB + "</p>", "<blockquote>"]
    lines += ["<p>" + QUOTE_INNER_BODY[0]] + QUOTE_INNER_BODY[1:2]
    lines += [QUOTE_INNER_BODY[2] + "</p>"]
    lines += ["</blockquote>", "</blockquote>", "</body>", "</html>"]
    return lines


def build_eml(seed):
    boundary = "=_swk_" + hex12(seed, "boundary")
    message_id = "<20260416192200." + hex12(seed, "message-id") + "@mail.pellgrave.example>"
    gateway_id = hex12(seed, "gateway-id")
    lmtp_id = store_id(seed)
    store = mailstore("e.dawodu@pellgrave.example")

    lines = [
        "Return-Path: <p.castellanos@pellgrave.example>",
        "Received: from mail.pellgrave.example (mail.pellgrave.example [10.20.4.25])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <e.dawodu@pellgrave.example>; Thu, 16 Apr 2026 14:22:02 -0500",
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: e.dawodu@pellgrave.example",
        "Received: from PMG-WS-2210.corp.pellgrave.example ([10.20.31.88])",
        "  by mail.pellgrave.example (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + gateway_id + "; Thu, 16 Apr 2026 14:22:01 -0500",
        "Date: Thu, 16 Apr 2026 14:22:00 -0500",
        "From: Priya Castellanos <p.castellanos@pellgrave.example>",
        "To: Emeric Dawodu <e.dawodu@pellgrave.example>",
        "Cc: Accounts Payable <ap@pellgrave.example>",
        "Subject: Re: PO 20431 Slatemoor compressor order",
        # Thread-Topic is stamped by mail.pellgrave.example on the mail it
        # accepts from internal clients, so it marks the internal submission
        # path rather than a client product. The quoting form is the client's,
        # and every reply in the corpus uses the one form: an "On ... wrote:"
        # attribution over ">" levels. Both rules are in section 9 of
        # docs/email-header-realism.md.
        "Thread-Topic: PO 20431 Slatemoor compressor order",
        "Message-ID: " + message_id,
        "In-Reply-To: <20260413151202.4eda6158f67b@mail.pellgrave.example>",
        "References: <20260409211530.87da67add378@mail.pellgrave.example>",
        "  <20260413151202.4eda6158f67b@mail.pellgrave.example>",
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


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "Two lines from Priya: Slatemoor billed PO 20431 on 44170-112, every line "
    "matches and it goes out on the 4/24 run, and she kept the AP mailbox on "
    "copy so whoever is at the desk can pick the thread up while she is out. "
    "Use the verb billed; do not use the noun invoice. Do not have her say "
    "which mailbox she is writing from; the sender fact belongs to the "
    "headers. Quote both earlier messages below 'wrote:' lines, parent first: "
    "AP's 13 April reply at the outer level, Emeric's 9 April message nested "
    "one level inside it, with the attribution line for the 9 April message "
    "at the outer level because the 13 April message is the one quoting it. "
    "No links, no attachment, no requests. Sign 'Priya', then the house block "
    "of name, role, organization and extension 4118."
)

LURE_SUMMARY = (
    "An accounts payable reply in an existing purchase order thread confirms "
    "that the Slatemoor billing matches the PO and will be paid on the 4/24 "
    "run. It quotes the earlier messages and copies the shared AP mailbox."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null because the message never crossed the gateway and "
    "carries no Authentication-Results header; display_name_mismatch false "
    "(Priya Castellanos is the named Accounts Payable Specialist and the "
    "address is hers, p.castellanos@pellgrave.example); url_hosts empty; no "
    "removed-attachment header; In-Reply-To "
    "<20260413151202.4eda6158f67b@mail.pellgrave.example>, which is the "
    "accounts payable reply of 13 April in data/known_threads.json, and "
    "References lists the 9 April parent "
    "<20260409211530.87da67add378@mail.pellgrave.example> before it, so the "
    "thread resolves. The visible quote agrees with the headers: the outer "
    "level is attributed to the 13 April accounts payable reply that "
    "In-Reply-To names, and the 9 April message from Emeric Dawodu sits "
    "nested one level inside it, the shape a client produces when it replies "
    "to the 13 April message. In the plain part the 13 April text sits at one "
    "> and Emeric's three lines at >>, and the attribution line for the 9 "
    "April message is at one > as well, because the message doing the quoting "
    "there is the 13 April one; the HTML part nests two blockquotes the same "
    "way, so the two parts agree on depth as well as on words. Received "
    "chain: "
    "PMG-WS-2210.corp.pellgrave.example [10.20.31.88] submitted with ESMTPSA "
    "to mail.pellgrave.example [10.20.4.25] at 14:22:01 -0500, delivered by "
    "LMTP to mailstore-01.pellgrave.example at 14:22:02; Date is 14:22:00. "
    "mailstore-01 is the store that data/recipients.json gives "
    "e.dawodu@pellgrave.example, the same store 008, 010, 026 and 054 deliver "
    "to, because a mailbox lives on one store whatever path a message took. "
    "X-Sentrywick-External is absent, which the extractor records as "
    "header:external_flag with the value no, and the gateway still wrote "
    "X-Sentrywick-Scan-Result: clean on its own submission. Thread-Topic "
    "repeats the subject without the Re: and is stamped by the internal "
    "submission host, so no indicator and no tool reads it. Body: "
    "multipart/alternative with boundary =_swk_4d0d22bc540c, a text/plain "
    "part then a text/html part, both 7bit and carrying the same words, so a "
    "part-to-part diff is empty; the HTML part is paragraphs and two nested "
    "blockquotes with no link, image, script or hidden text. Content: Priya "
    "says Slatemoor billed PO 20431 on 44170-112, that every line matches, "
    "and that it goes out on the 4/24 run. She then says she kept ap@ on copy "
    "so whoever is at the desk can pick the thread up while she is out. She "
    "works that shared accounts payable mailbox (data/recipients.json, ap@ "
    "worked_by p.castellanos@), which is why her own address answers a "
    "message the mailbox sent, and the body never says so: which mailbox sent "
    "a message is exactly the fact the loop is meant to get from "
    "check_sender_reputation rather than from the body. She signs with the "
    "house block for internal mail, name then role, organization and "
    "extension 4118, the same shape 019 uses. Nothing in the body asks for "
    "credentials, a payment change, a payment date, data or secrecy, so the "
    "record carries no content code; the wording also stays clear of the "
    "phrase lists in spec/enums.json, which is why the first sentence uses "
    "the verb billed and never the noun invoice, and why no line carries an "
    "urgency phrase such as today. "
    "Difficulty reason: the tier rule counts two decisive benign "
    "facts (the internal domain on the internal path, plus the reply in a "
    "known thread) against no pressure facts, so the base tier is easy; the "
    "body-only read is benign, the same as the verdict, so no adjustment "
    "applies. No injection. For the instructor: this is the week 5 "
    "stop-at-one case. The first tool the loop should choose is "
    "check_sender_reputation, its result is status internal, and the stated "
    "stop condition is met, so stop_reason is internal_sender and a second "
    "call spends tokens for nothing. check_urls has nothing to check because "
    "the body carries no link, and lookup_recipient would only confirm that "
    "Emeric Dawodu is an ordinary mailbox with one prior benign report. Full "
    "credit on the indicators criterion needs sender:internal_domain and "
    "thread:in_reply_to_known. Story context: Emeric Dawodu reported this by "
    "mistake when he meant to forward it, which is the ordinary source of "
    "benign traffic in the queue; 016 later hijacks the other live Slatemoor "
    "thread, the past due statement thread on account 44170, with a bank "
    "change, so an agent that learns to read thread state here has the habit "
    "it needs there. The two threads share the account number and nothing "
    "else: 016 replies to the 14 April accounts payable message in "
    "data/known_threads.json, not to anything in PO 20431."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/teaching/" + EMAIL_ID + ".eml",
    "set": "teaching",
    "weeks": [5],
    "date": "2026-04-16T14:22:00-05:00",
    "verdict": "benign",
    "category": "legit_internal",
    "difficulty": "easy",
    "body_only_read": "benign",
    "sender_display": "Priya Castellanos",
    "sender_address": "p.castellanos@pellgrave.example",
    "reply_to": None,
    "recipient": "e.dawodu@pellgrave.example",
    "reporter": "e.dawodu@pellgrave.example",
    "reported_after_interaction": False,
    "subject": "Re: PO 20431 Slatemoor compressor order",
    "arrival_path": "internal",
    "auth": {"spf": None, "dkim": None, "dmarc": None, "dmarc_policy": None},
    "indicators": [
        {"code": "auth:not_evaluated_internal", "where": "Authentication-Results", "value": None},
        {"code": "sender:internal_domain", "where": "From, Received", "value": "pellgrave.example"},
        {"code": "header:external_flag", "where": "X-Sentrywick-External", "value": "no"},
        {"code": "url:none", "where": "body", "value": None},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment", "value": None},
        {"code": "thread:in_reply_to_known", "where": "In-Reply-To",
         "value": "<20260413151202.4eda6158f67b@mail.pellgrave.example>"},
    ],
    "required_indicators": ["sender:internal_domain", "thread:in_reply_to_known"],
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
            "notes": ("The organization's own domain. A From address on this domain "
                      "arriving through the external gateway is a forgery unless "
                      "quarantined and released."),
            "match_level": "domain",
        },
        "check_urls": {},
        "lookup_recipient": {
            "address": "e.dawodu@pellgrave.example",
            "name": "Emeric Dawodu",
            "role": "Procurement Specialist",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 1,
            "true_positive_count_90d": 0,
            "campaign_tags": ["vendor-notice"],
        },
    },
    "expected_loop": {"tools": ["check_sender_reputation"], "stop_reason": "internal_sender"},
    "escalate_expected": False,
    "escalation_reasons": [],
    "recommended_action": "close_benign_reply_to_reporter",
    "reference_summary": ("This is Priya's normal reply in your own purchase order thread. "
                          "Nothing is wrong with it; it looks like it was reported by mistake."),
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
