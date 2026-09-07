#!/usr/bin/env python3
"""Regenerate 055-board-prep-reschedule.

Rebuilds builder/instructor/exam-emails/055-board-prep-reschedule.eml byte for
byte from the corpus seed, refreshes the prose fields of its own record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json.

This is an exam-only email. It renders into the instructor package rather than
under corpus/emails/, so nothing a student can reach holds it before the week 8
exam. The corpus validator, pointed at its default folder, warns that an exam
record has no file under emails/; that warning is correct. The file is checked
the way tools/build_corpus.py checks it:

    python3 corpus/tools/validate_corpus.py --no-dns \\
        --emails builder/instructor/exam-emails \\
        --ground-truth builder/corpus/release/ground_truth_exam.json

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_swk_" + hex("boundary", 12)
    gateway Received id   = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

There is no sender-side Received id and no DKIM body hash in this file: the
message never left the organization, so there is no sending relay to stamp one
and nothing signed it. Nothing else here is a literal the seed cannot explain
except the values the data files already fix, and those are read back rather
than typed: data/recipients.json gives the two people their names and gives
mailstore-01 as the one store that holds the recipient's mailbox, and
data/known_threads.json gives the parent message its Message-ID, its date and
its author, which is where In-Reply-To, References and the attribution line
over the quote all come from.

The boundary prefix is "=_swk_", the prefix gen_001 reserves for the messages
the Sentrywick stack itself composes. This one was typed on a Pellgrave
workstation and submitted through the organization's own host, so it takes the
internal prefix, the same one 002, 011, 015 and 019 carry.

WHY THE HEADER BLOCK LOOKS THE WAY IT DOES

Beatrix's workstation on the head office client range handed this message to
mail.pellgrave.example over an authenticated submission, so the gateway never
authenticated it and never stamped it as external. That is why the file carries
no Authentication-Results, no Received-SPF, no DKIM-Signature and no
X-Sentrywick-External, and why neither body part carries the gateway banner.
Missing is not failed, which is playbook rule 11 and the whole point of putting
this message on the exam. The gateway still writes X-Sentrywick-Scan-Result on
its own submissions, and X-Sentrywick-Reported-By, because every corpus message
was reported.

Thread-Topic is stamped by mail.pellgrave.example on the threaded mail it
accepts from internal clients, so it marks the internal submission path rather
than a client product, and it repeats the subject without the "Re:". The
quoting form belongs to the client: an "On ... wrote:" attribution line over
one ">" level in the plain part and one <blockquote> in the HTML part, the one
form every client in the corpus uses. Both rules are section 9 of
docs/email-header-realism.md.

Headers deliberately absent, matching the manifest indicator list: no Reply-To,
no X-Sentrywick-Removed-Attachment (attachment:none), no X-Originating-IP,
which is reserved for webmail submissions, no X-Mailer, no Auto-Submitted, no
X-Priority and no Importance. A note about a meeting time carries no urgency
header, and Return-Path and From are the same mailbox because an ordinary
person answering her own thread from her own client has no reason to split the
RFC 5321 envelope identity from the RFC 5322 author.

BODY

The manifest brief fixes two short paragraphs and the quoted block below them.
Beatrix signs with her first name and no block of her own, which is what the
brief asks for and what an assistant writes two messages into a thread she
started; the only signature block in the file is the CFO's, inside the quote,
where the brief puts it. So the one extension the file names is ext. 4102, his,
the same number 019 and 039 print.

The five days between the parent and this reply are accounted for in the body
rather than left to look odd: the CEO was at an industry conference from 20 to
23 April, so Beatrix could not answer for her until she was back. That is the
kind of small irregularity real mail carries, and it costs the record nothing,
because the record claims no content code at all. check_body_phrases() below
runs every body phrase list in spec/enums.json against both decoded parts and
fails on any hit, which is the same test validate_corpus.py runs; it is what
keeps "3:00" from drifting into "before 3" and "Thursday" from drifting into
"today", both of them content:urgency_keywords entries.

Run:  python3 corpus/tools/generators/gen_055_board_prep_reschedule.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "055-board-prep-reschedule"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
THREADS_PATH = os.path.join(CORPUS, "data", "known_threads.json")
REPUTATION_PATH = os.path.join(CORPUS, "data", "sender_reputation.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EML_DIR, EMAIL_ID + ".eml")

# The ground truth file field names the release path every record carries, the
# one spec/ground_truth.schema.json fixes. The .eml itself ships in the
# instructor package, so the validator warns that the two differ; that warning
# is the same one every exam record raises.
GT_FILE = "emails/exam/" + EMAIL_ID + ".eml"

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

CRLF = "\r\n"

ORG_DOMAIN = "pellgrave.example"
SENDER = "b.onwuka@" + ORG_DOMAIN
SENDER_DISPLAY = "Beatrix Onwuka"
ENVELOPE_SENDER = SENDER
RECIPIENT = "r.palomares@" + ORG_DOMAIN
RECIPIENT_DISPLAY = "Rutger Palomares"
# The person who received it is the person who reported it, so the mailbox the
# corpus copy was pulled from is the To address itself.
REPORTER = RECIPIENT

SUBJECT = "Re: Board prep, moving to Thursday 3:00"
THREAD_TOPIC = "Board prep, moving to Thursday 3:00"

# Beatrix's workstation, named the way the head office asset tag names it, on
# the corporate client range 10.20.30.0/23. RFC 1918 throughout, and the
# submission host is the same 10.20.4.25 the rest of the internal path uses.
SUBMISSION_HOST = "PMG-WS-3020.corp." + ORG_DOMAIN
SUBMISSION_IP = "10.20.30.20"
GATEWAY_HOST = "mail." + ORG_DOMAIN
GATEWAY_IP = "10.20.4.25"

SCAN_RESULT = "clean"

# Date is 09:12:00 -0500, so the UTC stamp on the Message-ID left side is
# 14:12:00. The gateway accepts the submission a second later and the store
# hands it to the mailbox a second after that.
MESSAGE_ID_STAMP = "20260427141200"
DATE_HEADER = "Mon, 27 Apr 2026 09:12:00 -0500"
GATEWAY_STAMP = "Mon, 27 Apr 2026 09:12:01 -0500"
STORE_STAMP = "Mon, 27 Apr 2026 09:12:02 -0500"

# The parent, as data/known_threads.json records it. Read back rather than
# typed: parent_message() checks every field below against the data file.
PARENT_ID = "<20260422190115.5301729428f5@mail.pellgrave.example>"
PARENT_SUBJECT = THREAD_TOPIC
PARENT_DATE = "2026-04-22T14:01:15-05:00"


# ------------------------------------------------------------ seed helpers

def digest(seed, label):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode("ascii")).digest()


def hexid(seed, label, length=12):
    return digest(seed, label).hex()[:length]


def store_id(seed):
    return str(uuid.UUID(hex=digest(seed, "store-id").hex()[:32], version=4))


# ------------------------------------------------------------- data files

def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def recipient_record(address):
    for record in load(RECIPIENTS_PATH)["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(address):
    """The mailbox the copy was delivered to and the one store that holds it.

    The recipient is a person and he is also the reporter, so there is no list
    expansion to unwind: the mailbox the file was pulled from is the To
    address, and its store is the store recipients.json records for it.
    """
    entry = recipient_record(address)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + address)
    return entry["name"], store


def reputation(domain):
    for record in load(REPUTATION_PATH)["domains"]:
        if record["domain"] == domain:
            return record
    raise SystemExit("sender_reputation.json has no record for " + domain)


def parent_message():
    """The 22 April message this one replies to, from data/known_threads.json.

    Everything the reply says about its parent comes from here: In-Reply-To,
    the single id in References, and the date and author on the attribution
    line over the quote. If the data file ever moves that message, this script
    stops rather than rendering a thread that no longer resolves.
    """
    for record in load(THREADS_PATH)["threads"]:
        if record["message_id"] == PARENT_ID:
            break
    else:
        raise SystemExit("known_threads.json has no message " + PARENT_ID)
    if record["subject"] != PARENT_SUBJECT:
        raise SystemExit("known_threads.json gives the parent the subject "
                         + repr(record["subject"]))
    if record["date"] != PARENT_DATE:
        raise SystemExit("known_threads.json dates the parent " + record["date"])
    if record["from"] != RECIPIENT or record["to"] != SENDER:
        raise SystemExit("the parent is not the CFO writing to the assistant")
    return record


# Weekday and month names are spelled out here rather than taken from
# strftime, whose %a and %b read the C library's locale. The attribution line
# has to be the same bytes on every machine that runs this script.
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def attribution(record, name):
    """The client's one quoting form: On <date> at <time>, <name> wrote:."""
    stamp = record["date"]
    year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
    hour, minute = stamp[11:13], stamp[14:16]
    weekday = WEEKDAYS[(_days_from_civil(year, month, day) + 3) % 7]
    return ("On " + weekday + ", " + str(day) + " " + MONTHS[month - 1] + " "
            + str(year) + " at " + hour + ":" + minute + ", " + name + " wrote:")


def _days_from_civil(year, month, day):
    """Days since 1970-01-01, so the weekday needs no locale and no library."""
    year -= month <= 2
    era = (year if year >= 0 else year - 399) // 400
    yoe = year - era * 400
    doy = (153 * (month + (-3 if month > 2 else 9)) + 2) // 5 + day - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


# ---------------------------------------------------------------- body text
#
# Two short paragraphs, the ones the manifest brief fixes, then the first name
# the brief asks her to sign with, then the parent quoted at one level under
# its attribution line. Both body parts carry these words on these lines, so a
# part-to-part diff is empty and the two parts agree on depth as well as on
# wording.
#
# The record claims no content code, so every phrase list in spec/enums.json
# has to stay out of both parts, and check_body_phrases() enforces that against
# the enums file rather than against a list typed here. The wording that costs:
# the meeting is "at 3:00" and never "before 3"; the answer comes "Thursday"
# and never "today" or "this morning"; the room is "booked" rather than held
# for a run; and the CFO's Tuesday conflict is an "audit call at 4:00", which
# is a noun and not the "call me" of content:phone_verification_offered.

GREETING = "Rutger,"

# The five day gap between the parent and this reply is explained inside the
# sentence rather than left to look odd: the CEO was at an industry conference
# from 20 to 23 April, which is section 2.3 of the corpus design.
PARA_1 = [
    "Thursday at 3:00 works for Adaeze -- I held off answering until she was",
    "back from the conference -- and I have the boardroom booked from 2:45 so",
    "we are not standing in the hall again.",
]

PARA_2 = [
    "Could you bring the Q1 numbers with you? She would like to walk the",
    "committee through them before the vote.",
]

# The brief says to sign "Beatrix", with no block of her own. That is what an
# assistant writes two messages into a thread she is already in, and it leaves
# the CFO's quoted block as the only signature in the file.
SIGN_OFF = "Beatrix"

QUOTE_BODY = [
    "Tuesday runs into the audit call at 4:00 and we will not get through",
    "the deck, so I would rather move board prep to Thursday at 3:00 if",
    "that is clear for Adaeze. Whatever she wants in front of the",
    "committee, I will have it with me.",
]

# The CFO's standard two-line block: name, then role, organization and the
# four digit extension from section 2.3 of the corpus design. 019 and 039
# carry the same block.
QUOTE_SIGNATURE = [
    "Rutger Palomares",
    "Chief Financial Officer, Pellgrave Mechanical Group, ext. 4102",
]


def plain_part(attrib):
    lines = [GREETING, ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += [SIGN_OFF, ""]
    lines += [attrib]
    lines += ["> " + line for line in QUOTE_BODY]
    lines += [">"]
    lines += ["> " + line for line in QUOTE_SIGNATURE]
    return lines


def paragraph(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def html_part(attrib):
    lines = ["<html>", "<body>", "<p>" + GREETING + "</p>"]
    lines += paragraph(PARA_1)
    lines += paragraph(PARA_2)
    lines += ["<p>" + SIGN_OFF + "</p>"]
    lines += ["<p>" + attrib + "</p>", "<blockquote>"]
    lines += paragraph(QUOTE_BODY)
    lines += ["<p>" + QUOTE_SIGNATURE[0] + "<br>", QUOTE_SIGNATURE[1] + "</p>"]
    lines += ["</blockquote>", "</body>", "</html>"]
    return lines


# ------------------------------------------------------------------- render

def build_eml(seed, attrib):
    name, store = delivery(RECIPIENT)
    if name != RECIPIENT_DISPLAY:
        raise SystemExit("recipients.json calls the recipient " + name)

    boundary = "=_swk_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + GATEWAY_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    lmtp_id = store_id(seed)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + GATEWAY_HOST + " (" + GATEWAY_HOST
        + " [" + GATEWAY_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        "Received: from " + SUBMISSION_HOST + " ([" + SUBMISSION_IP + "])",
        "  by " + GATEWAY_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + gateway_id + "; " + GATEWAY_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
        "Thread-Topic: " + THREAD_TOPIC,
        "Message-ID: " + message_id,
        "In-Reply-To: " + PARENT_ID,
        # The parent opened the thread, so it has no References of its own and
        # this list is that one id: RFC 5322 sec. 3.6.4 builds References from
        # the parent's References followed by the parent's Message-ID.
        "References: " + PARENT_ID,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        # Every line in both parts is pure ASCII and fits in 78 characters,
        # and no gateway banner is inserted into an internal message, so
        # neither part needs an encoding beyond 7bit.
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += plain_part(attrib)
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += html_part(attrib)
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    data = CRLF.join(lines).encode("ascii")
    if b"\n" in data.replace(b"\r\n", b"") or b"\r" in data.replace(b"\r\n", b""):
        raise SystemExit("a line ends with something other than CRLF")
    for byte in data:
        if byte not in (9, 13, 10) and not 0x20 <= byte <= 0x7E:
            raise SystemExit("byte outside the seven-bit printable range")
    return data, boundary


# ------------------------------------------------------------- body phrases

def check_body_phrases(parts):
    """The enums phrase pass, run here the way validate_corpus.py runs it.

    Every content code whose vocabulary entry says where=body is matched from
    a fixed phrase list. This record lists no content code at all, so a hit
    from any list is a fact the record fails to claim and the script stops.
    The two codes the validator skips are skipped here for the same reasons:
    content:non_english_body is a proportion judgment over Spanish stopwords
    that sit inside ordinary English words, and the content:instruction_to_ai
    list holds single words the corpus also puts inside quoted examples on
    benign mail.
    """
    enums = load(ENUMS_PATH)
    phrases = enums["content_phrases"]
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = "\n".join(parts).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")


# ------------------------------------------------------------ ground truth

REFERENCE_SUMMARY = (
    "This is Beatrix's normal reply in your own board prep thread. Nothing is "
    "wrong with it."
)

LURE_SUMMARY = (
    "The CEO's assistant replies inside an existing thread to confirm that the "
    "board prep move to Thursday at 3:00 works and to ask the CFO to bring the "
    "Q1 numbers. Internal two-hop path, a known thread, no link and no "
    "attachment."
)

BODY_BRIEF = (
    "Two short paragraphs from Beatrix under a first-name greeting: Thursday "
    "at 3:00 works for Adaeze, she held off answering until the CEO was back "
    "from the 20 to 23 April conference, and she has the boardroom booked from "
    "2:45; then a question asking Rutger to bring the Q1 numbers so the CEO "
    "can walk the committee through them before the vote. Quote the CFO's 22 "
    "April message below one attribution line, at one level, ending with his "
    "standard two-line block: 'Rutger Palomares' then 'Chief Financial "
    "Officer, Pellgrave Mechanical Group, ext. 4102'. No link, no attachment, "
    "no request beyond the meeting, and no phrase from any body list in "
    "spec/enums.json: the meeting is 'at 3:00' and never 'before 3', the "
    "answer comes 'Thursday' and never 'today'. Sign 'Beatrix', with no block "
    "of her own, which is what an assistant writes two messages into a thread "
    "she is already in."
)

MANIFEST_NOTES = (
    "Exam-only. The CFO reported it because the subject line matched a "
    "phishing simulation he remembered. Stem: an internal message with no "
    "Authentication-Results header, so the agent must not treat missing "
    "authentication as failed authentication. Rendered as the two-hop internal "
    "submission the path hint fixes, with Thread-Topic from the submission "
    "host, one quote level under an attribution line built from the parent "
    "record in data/known_threads.json, and both parts 7bit because an "
    "internal message carries no gateway banner. The only signature block in "
    "the file is the CFO's, inside the quote, which is where the brief puts "
    "it; Beatrix signs with her first name, so the one extension the file "
    "names is his, ext. 4102."
)

GT_NOTES_TEMPLATE = (
    "Exam-only, and the plainest benign case in the exam set. Key facts a "
    "correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null because the message never crossed the gateway and "
    "carries no Authentication-Results header; display_name_mismatch false "
    "(Beatrix Onwuka is the named Executive Assistant to the CEO and the "
    "address is hers, b.onwuka@pellgrave.example); url_hosts empty; no "
    "removed-attachment header; In-Reply-To "
    "<20260422190115.5301729428f5@mail.pellgrave.example>, which is the CFO's "
    "own message of 22 April in data/known_threads.json, and References "
    "carries that one id alone because that message opened the thread, so the "
    "thread resolves. The visible quote agrees with the headers: one level, "
    "attributed to Rutger Palomares at 14:01 on Wednesday 22 April, the date "
    "and author the thread record gives, and ending in his standard two-line "
    "block. Received chain: PMG-WS-3020.corp.pellgrave.example [10.20.30.20] "
    "submitted with ESMTPSA to mail.pellgrave.example [10.20.4.25] at "
    "09:12:01 -0500, delivered by LMTP to mailstore-01.pellgrave.example at "
    "09:12:02; Date is 09:12:00. mailstore-01 is the store "
    "data/recipients.json gives r.palomares@pellgrave.example, the same store "
    "019 and 039 deliver to, because a mailbox lives on one store whatever "
    "path a message took. X-Sentrywick-External is absent, which the "
    "extractor records as header:external_flag with the value no, and the "
    "gateway still wrote X-Sentrywick-Scan-Result: clean on its own "
    "submission. Thread-Topic repeats the subject without the Re: and is "
    "stamped by the internal submission host, so no indicator and no tool "
    "reads it. Body: multipart/alternative with boundary {boundary}, a "
    "text/plain part then a text/html part, both 7bit and carrying the same "
    "words at the same depth, so a part-to-part diff is empty; the HTML part "
    "is paragraphs and one blockquote with no link, image, script or hidden "
    "text. Content: Beatrix says Thursday at 3:00 works for Adaeze, that she "
    "held off answering until the CEO was back from the industry conference "
    "of 20 to 23 April, and that she has the boardroom booked from 2:45; she "
    "then asks Rutger to bring the Q1 numbers so the CEO can walk the "
    "committee through them before the vote. She signs with her first name "
    "and no block of her own, so the only signature block in the file is the "
    "CFO's, quoted: Rutger Palomares, then Chief Financial Officer, Pellgrave "
    "Mechanical Group, ext. 4102, the same block 019 and 039 carry. Nothing "
    "in the body asks for credentials, a payment, a payment change, data or "
    "secrecy, so the record carries no content code, and the wording stays "
    "clear of every phrase list in spec/enums.json: the meeting is at 3:00 "
    "rather than 'before 3', the answer comes on Thursday rather than "
    "'today', the room is 'booked' rather than held, and the CFO's Tuesday "
    "conflict is an audit call at 4:00, a noun rather than the 'call me' of "
    "content:phone_verification_offered. Difficulty reason: the tier rule "
    "counts two decisive benign facts (the internal domain on the internal "
    "path, plus the reply in a known thread) against no pressure facts, so "
    "the base tier is easy; the body-only read is benign, the same as the "
    "verdict, so no adjustment applies. No injection. For the instructor: "
    "this is the exam's stop-at-one case and its missing-authentication case. "
    "The first tool the loop should choose is check_sender_reputation, its "
    "result is status internal, the stated stop condition is met, so "
    "stop_reason is internal_sender and a second call spends tokens for "
    "nothing. check_urls has nothing to check because the body carries no "
    "link, and lookup_recipient would only confirm what the headers already "
    "show, that the reporter is the CFO. The wrong answer this record is "
    "built to catch is an agent that reads null spf, dkim and dmarc as "
    "failures: missing authentication is not failed authentication (playbook "
    "rule 11), and the gateway does not authenticate a submission it accepted "
    "from its own network. Full credit on the indicators criterion needs "
    "sender:internal_domain and thread:in_reply_to_known. "
    "recipient:executive and recipient:handles_payments sit on the record "
    "because data/recipients.json flags the CFO both ways, not because "
    "anything in the message is about money; neither is an escalation reason "
    "on its own, so escalate_expected is false and the action is "
    "close_benign_reply_to_reporter. Story context: the CEO was at an "
    "industry conference from 20 to 23 April, which is why an answer to a "
    "Wednesday message arrives the following Monday, and 030 uses the same "
    "conference to impersonate her. The reporter is the CFO whose name 004, "
    "019, 023, 034, 039 and 047 all borrow or carry, so the exam asks a "
    "candidate who has learned to distrust that name to notice that this one "
    "really is internal mail."
)

REPUTATION_NOTES = (
    "The organization's own domain. A From address on this domain arriving "
    "through the external gateway is a forgery unless quarantined and "
    "released."
)


def ground_truth(boundary, rep, recip):
    return {
        "id": EMAIL_ID,
        "file": GT_FILE,
        "set": "exam",
        "weeks": [8],
        "date": "2026-04-27T09:12:00-05:00",
        "verdict": "benign",
        "category": "legit_internal",
        "difficulty": "easy",
        "body_only_read": "benign",
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
            {"code": "auth:not_evaluated_internal",
             "where": "Authentication-Results", "value": None},
            {"code": "sender:internal_domain", "where": "From, Received",
             "value": ORG_DOMAIN},
            {"code": "header:external_flag", "where": "X-Sentrywick-External",
             "value": "no"},
            {"code": "url:none", "where": "body", "value": None},
            {"code": "attachment:none",
             "where": "X-Sentrywick-Removed-Attachment", "value": None},
            {"code": "thread:in_reply_to_known", "where": "In-Reply-To",
             "value": PARENT_ID},
            {"code": "recipient:executive", "where": "lookup_recipient",
             "value": RECIPIENT},
            {"code": "recipient:handles_payments", "where": "lookup_recipient",
             "value": RECIPIENT},
        ],
        "required_indicators": ["sender:internal_domain",
                                "thread:in_reply_to_known"],
        "url_hosts": [],
        "attachment": None,
        "injection": None,
        "tool_expectations": {
            "check_sender_reputation": {
                "domain": ORG_DOMAIN,
                "status": rep["status"],
                "first_seen": rep["first_seen"],
                "messages_90d": rep["messages_90d"],
                "prior_reports": rep["prior_reports"],
                "last_report_verdict": rep["last_report_verdict"],
                "last_report_date": rep["last_report_date"],
                "campaign_tag": rep["campaign_tag"],
                "new_domain": rep["new_domain"],
                "notes": rep["notes"],
                "match_level": "domain",
            },
            "check_urls": {},
            "lookup_recipient": {
                "address": recip["address"],
                "name": recip["name"],
                "role": recip["role"],
                "mailbox_type": recip["mailbox_type"],
                "executive": recip["executive"],
                "handles_payments": recip["handles_payments"],
                "chronic_reporter": recip["chronic_reporter"],
                "report_count_90d": recip["report_count_90d"],
                "true_positive_count_90d": recip["true_positive_count_90d"],
                "campaign_tags": sorted({report["campaign_tag"]
                                         for report in recip["prior_reports"]}),
            },
        },
        # The sender is the organization itself on the internal path, which is
        # the stated stop condition, so the loop stops on the first result and
        # the other two tools are never called.
        "expected_loop": {"tools": ["check_sender_reputation"],
                          "stop_reason": "internal_sender"},
        "escalate_expected": False,
        "escalation_reasons": [],
        "recommended_action": "close_benign_reply_to_reporter",
        "reference_summary": REFERENCE_SUMMARY,
        "labeled_by": LABELED_BY,
        "reviewed_by": REVIEWED_BY,
        "review_agreement": False,
        "label_version": LABEL_VERSION,
        "notes": GT_NOTES_TEMPLATE.format(boundary=boundary),
    }


# ------------------------------------------------------------------- output

def decoded_lines(text):
    """A decoded part back as the source lines it was written from."""
    return text.replace(CRLF, "\n").rstrip("\n").split("\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    spec = load(SPEC_PATH)
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
    if entry["sender_address"] != SENDER or entry["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender does not match the manifest")
    if entry["recipient"] != RECIPIENT or entry["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if entry["reply_to"] is not None:
        raise SystemExit("this record carries no Reply-To")
    if entry["date"] != "2026-04-27T09:12:00-05:00":
        raise SystemExit("date does not match the manifest")
    if entry["set"] != "exam" or entry["weeks"] != [8]:
        raise SystemExit("this record is the exam set, week 8")
    if entry["arrival_path"] != "internal":
        raise SystemExit("this record arrives on the internal path")
    if entry["auth"] != {"spf": None, "dkim": None, "dmarc": None}:
        raise SystemExit("an internal message carries no authentication results")
    if entry["url_hosts"] or entry["attachment"] or entry["injection"]:
        raise SystemExit("this record carries no link, no attachment and no injection")
    if entry["expected_loop"] != {"tools": ["check_sender_reputation"],
                                  "stop_reason": "internal_sender"}:
        raise SystemExit("the expected loop does not match the manifest")

    rep = reputation(ORG_DOMAIN)
    if rep["status"] != "internal":
        raise SystemExit("sender_reputation.json no longer calls " + ORG_DOMAIN
                         + " internal, which sender:internal_domain needs")
    recip = recipient_record(RECIPIENT)
    if not recip["executive"] or not recip["handles_payments"]:
        raise SystemExit("recipients.json no longer flags " + RECIPIENT
                         + " as an executive who handles payments")

    parent = parent_message()
    attrib = attribution(parent, RECIPIENT_DISPLAY)
    if attrib != "On Wed, 22 Apr 2026 at 14:01, Rutger Palomares wrote:":
        raise SystemExit("the attribution line came out as " + repr(attrib))

    data, boundary = build_eml(seed, attrib)
    os.makedirs(EML_DIR, exist_ok=True)
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
    if decoded_lines(parts[0]) != plain_part(attrib):
        raise SystemExit("the plain part does not decode to its source lines")
    if decoded_lines(parts[1]) != html_part(attrib):
        raise SystemExit("the html part does not decode to its source lines")
    if list(parsed.iter_attachments()):
        raise SystemExit("no part is ever an attachment")
    for text in parts:
        if "http" in text or "@" in text:
            raise SystemExit("this message carries no link and no address")
        if "Sentrywick Gateway" in text:
            raise SystemExit("an internal message never carries the gateway banner")
        if text.count("ext. 4102") != 1:
            raise SystemExit("the quoted block names the CFO's extension once")
    check_body_phrases(parts)
    if str(parsed["Subject"]) != SUBJECT:
        raise SystemExit("unfolded Subject is " + repr(str(parsed["Subject"])))
    for header in ("Authentication-Results", "Received-SPF", "DKIM-Signature",
                   "X-Sentrywick-External", "Reply-To", "X-Priority",
                   "Importance", "Auto-Submitted", "X-Originating-IP",
                   "X-Sentrywick-Removed-Attachment"):
        if parsed[header] is not None:
            raise SystemExit("this message carries no " + header + " header")
    if str(parsed["In-Reply-To"]) != PARENT_ID or str(parsed["References"]) != PARENT_ID:
        raise SystemExit("the thread headers do not name the parent")

    for candidate in spec["emails"]:
        if candidate["id"] == EMAIL_ID:
            candidate["body_brief"] = BODY_BRIEF
            candidate["lure_summary"] = LURE_SUMMARY
            candidate["notes"] = MANIFEST_NOTES
            break
    write_json(SPEC_PATH, spec)

    truth = load(GT_PATH)
    records = truth["emails"]
    new_record = ground_truth(boundary, rep, recip)
    for index, existing in enumerate(records):
        if existing["id"] == EMAIL_ID:
            records[index] = new_record
            break
    else:
        records.append(new_record)
        records.sort(key=lambda existing: existing["id"])
    write_json(GT_PATH, truth)

    print("wrote " + EML_PATH + " (" + str(len(data)) + " bytes)")
    print("updated manifest prose and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
