#!/usr/bin/env python3
"""Regenerate 051-it-password-expiry-notice.

Renders instructor/exam-emails/051-it-password-expiry-notice.eml byte for byte
from the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record in either file.

This email is exam only. It ships in the instructor package and never under
corpus/emails/, so nothing a student can reach holds it before the week 8
final. The corpus validator warns that an exam record has no file under
emails/; that warning is correct. Validate the file by pointing the validator
at the folder the file is in:

    python3 corpus/tools/validate_corpus.py --no-dns \\
        --emails builder/instructor/exam-emails \\
        --ground-truth builder/corpus/release/ground_truth_exam.json

The ground truth file field stays emails/exam/051-it-password-expiry-notice.eml
because spec/ground_truth.schema.json pins that shape for every record. The
bytes live in the instructor package; the field names the slot.

Identifiers are derived from the corpus seed the same way the rest of the
corpus derives them, so rerunning this script reproduces the same bytes:

    hex(label, n) = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hex("message-id", 12)
    MIME boundary         = "=_part_" + hex("boundary", 12)
    submission Received id = hex("gateway-id", 12), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

Nothing in the file is pinned as an unexplained literal; every identifier above
is recomputed on each run. There is no DKIM signature and no sender-side hop,
because the message never left the organization.

What this email is. It is the help desk ticket system's scheduled password
reminder, and it is the honest twin of 006, the forgery that reached the same
mailbox two weeks earlier with the same subject shape and the same signature.
Everything a reader can check inside the words is close to identical in both
files: a password deadline, a link, and "Pellgrave IT Help Desk, ext. 4400" at
the bottom. What separates them sits outside the prose. This one was composed
on helpdesk-app.corp.pellgrave.example and handed to mail.pellgrave.example
over an authenticated submission, so it never crossed the border and the
gateway never authenticated it; and its one link goes to
portal.pellgrave.example, which is on the internal known-good list in
data/known_good_domains.json. 006 arrived through the gateway from
relay19.bulkhost-nine.example, failed SPF and DMARC against the organization's
own published policy, and linked to pel1grave.example.

Why the body says "expires on" and never "expires in". "expires in" is an
entry in the content:urgency_keywords list in spec/enums.json, and this record
carries no urgency code, so validate_corpus.py fails the file if the phrase
appears in either decoded part. The manifest body_brief asks for the word
"expires" for that reason: the deadline is named by its date, the way a
scheduled notice that runs three times names it, and the countdown lives in
the Subject line, which the phrase pass does not read. That is not a dodge. A
genuine scheduled reminder states a date because it will send the same message
again on two later dates; a lure counts down because the countdown is the
lure. 006 says "expires in 24 hours" and carries the urgency code.

Why the body does carry "password" and therefore content:credential_request.
The manifest lists that code, its polarity is PB, and it is the single
pressure fact that moves this record from easy to medium: an extractor that
reads phrase lists flags a credential request on a message that is completely
benign. That is the exam item. The body says the word plainly, and states just
as plainly that the help desk will never ask for it, which is what a real
help desk notice says and what a forger can copy word for word.

Why this message carries no Authentication-Results, no Received-SPF, no
DKIM-Signature and no X-Sentrywick-External: the ticket host handed it to
mail.pellgrave.example over an authenticated submission, so the gateway never
authenticated it and never stamped it as external, and neither body part
carries the gateway banner. Missing is not failed. The gateway still writes
X-Sentrywick-Scan-Result on its own submissions, and X-Sentrywick-Reported-By,
because every corpus message was reported.

Auto-Submitted: auto-generated is present, and the record carries the matching
header:auto_submitted indicator. RFC 3834 sec. 5 defines the field for system
notices, and the ticket system sets it on a reminder it will send three times
to every mailbox whose password is aging, so that out-of-office replies do not
land in the shared help desk mailbox. It creates no real-versus-fake tell
against 006: a forger can write the header too, and 006 is already separated by
its authentication block, its arrival path and its link host.

Return-Path carries noreply@pellgrave.example while From stays the shared help
desk mailbox that signs the notice, exactly as in 002, which the same ticket
system sent. data/recipients.json records noreply@pellgrave.example with
worked_by null and helpdesk@pellgrave.example as a mailbox Yves Strickmoor
works, so the bounces and the vacation replies from a scheduled run go to the
mailbox nobody reads rather than into the queue somebody does. Return-Path is
an RFC 5321 envelope identity and From is the RFC 5322 author, so the two
differ without a Sender header and without any indicator: both addresses sit
on pellgrave.example, which is the organizational domain sender:internal_domain
keys on. 006 sets both to helpdesk@pellgrave.example, because a forgery that
aligns its envelope with its header still fails SPF on the path.

Headers deliberately absent, matching the manifest indicator list: no Reply-To
(reply_to is null), no In-Reply-To and no References (thread:new), no
X-Sentrywick-Removed-Attachment (attachment:none), no Thread-Topic (the
internal submission host stamps it only on threaded mail and this message
starts a thread), no X-Originating-IP (reserved for webmail submissions), no
X-Priority, no Importance, and no X-Sentrywick-Spam-Score, which the gateway
writes only on mail it authenticated at the border.

Run:  python3 corpus/tools/generators/gen_051_it_password_expiry_notice.py
"""

import email
import email.policy
import email.utils
import hashlib
import json
import os
import uuid

EMAIL_ID = "051-it-password-expiry-notice"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUILDER = os.path.dirname(CORPUS)
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
KNOWN_GOOD_PATH = os.path.join(CORPUS, "data", "known_good_domains.json")
DISPLAY_NAMES_PATH = os.path.join(CORPUS, "data", "display_names.json")
ENUMS_PATH = os.path.join(CORPUS, "spec", "enums.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EXAM_DIR = os.path.join(BUILDER, "instructor", "exam-emails")
EML_PATH = os.path.join(EXAM_DIR, EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-03"
REVIEWED_BY = "not yet reviewed"

ORG_DOMAIN = "pellgrave.example"
TICKET_HOST = "helpdesk-app.corp." + ORG_DOMAIN
TICKET_IP = "10.20.8.15"
SUBMIT_HOST = "mail." + ORG_DOMAIN
SUBMIT_IP = "10.20.4.25"

SENDER = "helpdesk@" + ORG_DOMAIN
SENDER_DISPLAY = "Pellgrave IT Help Desk"
# The envelope sender is not the From mailbox. A scheduled run that touches
# every mailbox whose password is aging puts its bounce address on a mailbox
# nobody works, so the delivery failures and the vacation replies do not land
# in the monitored shared help desk mailbox the notice is signed with. That is
# the same reason the message carries Auto-Submitted. data/recipients.json
# records noreply@pellgrave.example as the ticket system sender with worked_by
# null, and helpdesk@pellgrave.example as a mailbox somebody works. 002 splits
# the two the same way, because the same ticket system sent it.
ENVELOPE_SENDER = "noreply@" + ORG_DOMAIN

RECIPIENT = "l.vashti@" + ORG_DOMAIN
# The person the notice was addressed to is the person who reported it, so the
# mailbox the corpus copy was pulled from is the To address itself.
REPORTER = RECIPIENT

SUBJECT = "Your password expires in 7 days"

# Date is 06:00:00 -0500, so the Message-ID stamp reads 11:00:00 UTC.
MESSAGE_ID_STAMP = "20260428110000"
DATE_HEADER = "Tue, 28 Apr 2026 06:00:00 -0500"
SUBMIT_STAMP = "Tue, 28 Apr 2026 06:00:01 -0500"
STORE_STAMP = "Tue, 28 Apr 2026 06:00:02 -0500"

# The one link host. It is on the internal known-good list, which is the fact
# url:host_internal_known_good keys on and the fact that separates this file
# from 006, whose link host is the lookalike pel1grave.example.
LINK_HOST = "portal." + ORG_DOMAIN
LINK = "https://" + LINK_HOST + "/account"

BANNER = "[External message. Sentrywick Gateway]"


def hexid(seed, label, length=12):
    return hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    digest = hashlib.sha256(
        (seed + "|" + EMAIL_ID + "|store-id").encode()).hexdigest()
    return str(uuid.UUID(hex=digest[:32], version=4))


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def recipient_record(address):
    for record in load(RECIPIENTS_PATH)["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(address):
    """The mailbox this file was pulled from and the one store that holds it.

    The To address is a person rather than a list, so the message is delivered
    to that mailbox itself and the LMTP hop names the store recipients.json
    gives it. Every mailbox in the corpus lives on exactly one store, whatever
    path a message took to reach it, which is why this file and 006 both land
    on mailstore-01.
    """
    entry = recipient_record(address)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + address)
    return entry["name"], store


def check_link_host_is_internal():
    """The link host is on the internal known-good list, which is the whole point."""
    known_good = load(KNOWN_GOOD_PATH)
    if (LINK_HOST not in known_good["internal_hosts"]
            and not LINK_HOST.endswith(known_good["internal_suffix"])):
        raise SystemExit(LINK_HOST + " is not on the internal known-good list")


def check_envelope_split():
    """The envelope sender is a mailbox nobody works; the From mailbox is worked.

    That is the whole reason the two differ, so it is read from
    data/recipients.json rather than asserted in a comment.
    """
    envelope = recipient_record(ENVELOPE_SENDER)
    author = recipient_record(SENDER)
    if envelope.get("worked_by") is not None:
        raise SystemExit(ENVELOPE_SENDER + " is now a worked mailbox, so it is no"
                         " longer the right bounce address for a scheduled run")
    if author.get("worked_by") is None:
        raise SystemExit(SENDER + " is no longer worked by anyone, so there is"
                         " nothing for the envelope split to protect")


def check_display_name_is_owned():
    """The display name is owned by the From domain, so no mismatch fires.

    data/display_names.json records "Pellgrave IT Help Desk" as an
    organization name owned by pellgrave.example and sourced from this very
    mailbox. 006 carries the same display name and the same From address; the
    name is no help at all, which is why the record lists no sender display
    code and why the student has to reach the path.
    """
    table = load(DISPLAY_NAMES_PATH)
    for entry in table["names"]:
        if entry["display_name"] == SENDER_DISPLAY:
            if ORG_DOMAIN not in entry["owner_domains"]:
                raise SystemExit(SENDER_DISPLAY + " is no longer owned by " + ORG_DOMAIN)
            return
    raise SystemExit("display_names.json has no entry for " + SENDER_DISPLAY)


# ---------------------------------------------------------------- body text
#
# The wording is the manifest body_brief: the password expires in seven days,
# change it with Ctrl+Alt+Del on a company computer or on the account page at
# https://portal.pellgrave.example/account, the help desk will never ask for
# the password by email, signed "Pellgrave IT Help Desk, ext. 4400".
#
# The record carries exactly one content code, content:credential_request, so
# the word "password" has to appear and no phrase from any other content list
# in spec/enums.json may. validate_corpus.py checks that both ways. What the
# lists rule out here, and how the text works around it:
#
#   "expires in" is out (content:urgency_keywords), which is why the deadline
#   is a date, "expires on Tuesday 5/5", and why the notice names the two
#   later sending dates instead of counting down. "today", "immediately",
#   "action required", "by friday" and the rest of that list are out for the
#   same reason. The countdown that the subject line carries is the manifest's,
#   and the phrase pass reads only the decoded body parts.
#   "sign in", "log in", "credentials", "re-authenticate" and "verify your
#   account" are out, even though they sit in the one content list this record
#   does carry, because the recorded indicator value has to be built from the
#   phrase list and this file records the single word it actually says. A real
#   password reminder does not need a sign-in step: the change happens on the
#   machine in front of you, and the portal page is the alternative for someone
#   away from the network.
#   "download" and "shared with you" are out (content:file_share_lure), so
#   nothing is offered as a file.
#   "was changed" and "if you did not" are out (content:account_change_notice);
#   this notice reports a deadline, not a change somebody already made.
#   "call me" and "call the number on file" are out
#   (content:phone_verification_offered); ext. 4400 is a route for a password
#   change that did not take, not an offer to confirm anything by phone, and no
#   phrase from that list appears.
#
# The link host also appears as bare text in the prose, so a week 1 reader who
# is handed only the body can see that the link goes to the company's own
# portal without opening it.
#
# Two things in this body are there for the exam. The first is the plain
# statement that the help desk will never ask for the password, which is what a
# real notice says and what a forger copies; it is the reason body_only_read is
# uncertain rather than benign, because nothing a reader can check inside the
# words separates this file from 006. The second is the overnight paragraph: a
# scheduled system builds its run from a snapshot, so a reminder can cross a
# change the reader already made. Nobody invents that detail for a lure,
# because a lure wants the reader to act rather than to conclude that there is
# nothing to do.

PARA_1 = [
    "Your Pellgrave network password expires on Tuesday 5/5, seven days from",
    "now. This is the first of three reminders; the other two go out on",
    "Friday 5/1 and on Monday 5/4.",
]

PARA_2 = [
    "The quickest way to change it is from a company computer: press",
    "Ctrl+Alt+Del, choose Change a password, and follow the prompt. If you",
    "are away from the network, the account page on portal.pellgrave.example",
    "does the same thing:",
]

PARA_3 = [
    "These go out overnight from the account record, so if you changed it",
    "yesterday this one crossed with you and there is nothing to do.",
]

PARA_4 = [
    "One line goes on every one of these: the help desk will never ask you",
    "for your password, by email or over the phone. A message in our name",
    "that does belongs on the Report Phish button.",
]

PARA_5 = [
    "If the change does not take, or something still asks you for the old",
    "one, call the help desk at ext. 4400.",
]

# House signature for a shared mailbox: the mailbox's own name and the four
# digit extension from section 2.3 of the corpus design. 006 copies this line
# byte for byte, which is why it is no help to a reader.
SIGNATURE = "Pellgrave IT Help Desk, ext. 4400"


def greeting(name):
    """Hello, then the first name from data/recipients.json.

    006 opens the same way. The forgery copied the genuine notice, so the
    genuine notice is the one that sets the form.
    """
    return "Hello " + name.split()[0] + ","


def plain_part(name):
    lines = [greeting(name), ""]
    lines += PARA_1 + [""]
    lines += PARA_2 + [""]
    lines += [LINK, ""]
    lines += PARA_3 + [""]
    lines += PARA_4 + [""]
    lines += PARA_5 + [""]
    lines += [SIGNATURE]
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def html_part(name):
    lines = ["<html>", "<body>", "<p>" + greeting(name) + "</p>"]
    lines += paragraph_html(PARA_1)
    lines += paragraph_html(PARA_2)
    # The href and the visible text are the same address, the way a plain
    # internal notice writes a link, so a reader of either part sees the host.
    lines += ['<p><a href="' + LINK + '"', "  >" + LINK + "</a></p>"]
    lines += paragraph_html(PARA_3)
    lines += paragraph_html(PARA_4)
    lines += paragraph_html(PARA_5)
    lines += ["<p>" + SIGNATURE + "</p>"]
    lines += ["</body>", "</html>"]
    return lines


# ------------------------------------------------------------------- render

def check_phrase_lists(plain_text, html_text):
    """Run spec/enums.json content_phrases the way validate_corpus.py will.

    The record carries one content code. Every phrase list whose code is not
    that one has to miss both parts, and that code's list has to hit both. The
    check lives here as well as in the validator so that a change to the body
    fails at the generator, where the fix is.
    """
    enums = load(ENUMS_PATH)
    phrases = enums["content_phrases"]
    where_of = {entry["code"]: entry.get("where")
                for entry in enums["indicator_vocabulary"]}
    # The validator skips these two: one is a proportion judgment over Spanish
    # stopwords, the other holds single words the corpus also puts inside
    # quoted examples on benign mail.
    skip = {"content:non_english_body", "content:instruction_to_ai"}
    body = (plain_text + "\n" + html_text).lower()
    for code in sorted(phrases):
        if code in skip or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if code == CONTENT_CODE:
            if hits != [CONTENT_VALUE]:
                raise SystemExit(code + " matches " + repr(hits)
                                 + ", but the record records "
                                 + repr(CONTENT_VALUE))
        elif hits:
            raise SystemExit("the body carries the " + code + " phrase "
                             + repr(hits[0]) + ", which this record does not list")


CONTENT_CODE = "content:credential_request"
CONTENT_VALUE = "password"


def build_eml(seed):
    check_link_host_is_internal()
    check_envelope_split()
    check_display_name_is_owned()

    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SUBMIT_HOST + ">")
    submit_id = hexid(seed, "gateway-id")
    lmtp_id = store_id(seed)
    name, store = delivery(RECIPIENT)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        "Received: from " + SUBMIT_HOST + " (" + SUBMIT_HOST
        + " [" + SUBMIT_IP + "])",
        "  by " + store + "." + ORG_DOMAIN + " (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + RECIPIENT + ">; " + STORE_STAMP,
        # The gateway writes its own verdict even on the mail it never
        # authenticated, because the scan runs on submission too.
        "X-Sentrywick-Scan-Result: clean",
        "X-Sentrywick-Message-UID: " + submit_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        # The ticket system composed the notice and handed it to the submission
        # host over an authenticated hop. No line is by mx.pellgrave.example,
        # so nothing here crossed the border inbound and the message carries no
        # gateway authentication block.
        "Received: from " + TICKET_HOST + " ([" + TICKET_IP + "])",
        "  by " + SUBMIT_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + submit_id + "; " + SUBMIT_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + name + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT,
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
    lines += plain_part(name)
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: 7bit",
        "",
    ]
    lines += html_part(name)
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")

    plain_text = "\n".join(plain_part(name))
    html_text = "\n".join(html_part(name))
    # Section 10 item 17 the other way round: an internal message never carries
    # the gateway's external banner.
    if BANNER in plain_text or BANNER in html_text:
        raise SystemExit("an internal message must not carry the external banner")
    for phrase in ("password", "expires on", "Ctrl+Alt+Del", LINK_HOST, SIGNATURE):
        if phrase not in plain_text or phrase not in html_text:
            raise SystemExit("a part lost the phrase: " + phrase)
    if plain_text.count(LINK) != 1 or html_text.count(LINK) != 2:
        raise SystemExit("the link appears once in the plain part and twice in the"
                         " HTML part")
    check_phrase_lists(plain_text, html_text)

    return "\r\n".join(lines).encode("ascii")


# ------------------------------------------------ manifest and ground truth

BODY_BRIEF = (
    "The scheduled notice: the password expires in 7 days; change it by "
    "pressing Ctrl+Alt+Del on a company computer and choosing Change a "
    "password, or at https://portal.pellgrave.example/account. Use 'password' "
    "and 'expires'. State plainly that the help desk will never ask for the "
    "password by email. Sign 'Pellgrave IT Help Desk, ext. 4400'. As rendered "
    "the notice opens 'Hello Lenora,' and names the deadline as a date rather "
    "than a countdown, 'expires on Tuesday 5/5, seven days from now', because "
    "'expires in' is a content:urgency_keywords phrase and this record carries "
    "no urgency code; the countdown stays in the Subject line, which the phrase "
    "pass does not read. It says this is the first of three reminders and that "
    "the other two go out on Friday 5/1 and Monday 5/4, gives Ctrl+Alt+Del and "
    "Change a password as the quickest route from a company computer and the "
    "account page on portal.pellgrave.example as the route from off the "
    "network, carries the link once as bare text, then adds that the reminders "
    "are built overnight from the account record so one can cross a change the "
    "reader already made. The never-ask line reads 'the help desk will never "
    "ask you for your password, by email or over the phone' and sends anything "
    "in the help desk's name that does to the Report Phish button. It closes "
    "by sending a change that did not take to the help desk on ext. 4400, and "
    "signs with the shared mailbox name and extension."
)

LURE_SUMMARY = (
    "The real help desk's scheduled notice that the recipient's password "
    "expires in a week, with instructions to change it from a company computer "
    "with Ctrl+Alt+Del or on the internal portal. It has the internal two-hop "
    "path and no authentication header."
)

MANIFEST_NOTES = (
    "Exam-only twin of 006. Same recipient, same subject shape, same display "
    "name and same signature line, opposite path. content:credential_request "
    "fires on the word password, so the stem asks which facts make it benign "
    "anyway: the internal two-hop path with no Authentication-Results, and the "
    "one link host on the internal known-good list. Every word of this body "
    "could be copied into a forgery, which is why body_only_read is uncertain "
    "and why the two decisive facts are both outside the prose."
)

REFERENCE_SUMMARY = (
    "This is the real password reminder from our own help desk system, sent "
    "from inside the company to our own portal. It is safe, and it was wise to "
    "compare it against the fake one from two weeks ago."
)

REPUTATION_NOTES = (
    "The organization's own domain. A From address on this domain arriving "
    "through the external gateway is a forgery unless quarantined and released."
)

NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example; "
    "reply_to_domain none (no Reply-To header); spf, dkim, dmarc and "
    "dmarc_policy all null, because the message never crossed the border "
    "gateway and the file carries no Authentication-Results header at all; "
    "display_name_mismatch false, since Pellgrave IT Help Desk is an owned "
    "name in data/display_names.json, owned by pellgrave.example and sourced "
    "from the shared mailbox helpdesk@pellgrave.example; url_hosts "
    "portal.pellgrave.example, from one link that appears once in the plain "
    "part and twice in the HTML part, where the href and the visible text are "
    "the same address; no removed-attachment header; no In-Reply-To and no "
    "References, so the thread is new. Received chain: "
    "helpdesk-app.corp.pellgrave.example [10.20.8.15], the ticket system's "
    "submission host, handed the message to mail.pellgrave.example "
    "[10.20.4.25] with ESMTPSA at 06:00:01 -0500, and mail.pellgrave.example "
    "delivered it by LMTP to mailstore-01.pellgrave.example at 06:00:02; Date "
    "is 06:00:00. No Received line is by mx.pellgrave.example, which is what "
    "makes this an internal path rather than an inbound one. The LMTP hop "
    "reads for <l.vashti@pellgrave.example> and names mailstore-01, the store "
    "data/recipients.json gives that mailbox, and it is the same store 006 was "
    "delivered by, because a mailbox lives on exactly one store whatever path "
    "a message took. Return-Path is <noreply@pellgrave.example> while From is "
    "helpdesk@pellgrave.example: the ticket system puts the envelope sender on "
    "its own mailbox, the one data/recipients.json records with worked_by "
    "null, so the bounces and the vacation replies from a scheduled run go to "
    "a mailbox nobody works instead of the monitored shared help desk mailbox "
    "the notice is signed with, and it is the same reason the message carries "
    "Auto-Submitted. The envelope sender is an RFC 5321 identity and the From "
    "mailbox is the RFC 5322 author, so the two differ on purpose, with no "
    "Sender header and no indicator: both addresses sit on pellgrave.example, "
    "which is the organizational domain sender:internal_domain keys on. 002 "
    "splits the two the same way, because the same ticket system sent it; 006 "
    "sets both to helpdesk@pellgrave.example and still fails SPF, because the "
    "path is what fails, not the alignment. The Message-ID right side is "
    "mail.pellgrave.example, the submission host, following 002. "
    "X-Sentrywick-External is absent, which the extractor records as "
    "header:external_flag with the value no, and neither body part carries the "
    "gateway banner, because the gateway inserts it only into the mail it "
    "stamps as external. The gateway still wrote X-Sentrywick-Scan-Result: "
    "clean on its own submission, and X-Sentrywick-Reported-By names Lenora "
    "Vashti, who reported it. Auto-Submitted: auto-generated is present, the "
    "RFC 3834 section 5 header a scheduled reminder run sets so that "
    "out-of-office replies do not come back to the shared help desk mailbox; "
    "the extractor records it as header:auto_submitted. There is no "
    "X-Sentrywick-Spam-Score, because the gateway writes one only on mail it "
    "authenticated at the border, and no Thread-Topic, X-Originating-IP, "
    "X-Priority or Importance. Body: multipart/alternative, a text/plain part "
    "then a text/html part, both 7bit and carrying the same words, so a "
    "part-to-part diff is empty; the HTML part is plain paragraphs with one "
    "anchor and no image, script, form, styling trick or hidden text. Content: "
    "the help desk tells Lenora Vashti that her Pellgrave network password "
    "expires on Tuesday 5/5, seven days from now, that this is the first of "
    "three reminders and the other two go out on Friday 5/1 and Monday 5/4, "
    "that the quickest way to change it is Ctrl+Alt+Del on a company computer "
    "and Change a password, that the account page on portal.pellgrave.example "
    "does the same thing from off the network, and that the reminders are "
    "built overnight from the account record so one can cross a change already "
    "made. It then states plainly that the help desk will never ask for the "
    "password by email or over the phone and that a message in its name which "
    "does belongs on the Report Phish button, sends a change that did not take "
    "to ext. 4400, and signs Pellgrave IT Help Desk, ext. 4400. The one "
    "content code is content:credential_request, on the word password, which "
    "is the whole point of the file: the word is unavoidable in a genuine "
    "password reminder, so a phrase-list extractor flags a credential request "
    "on a message that is completely benign. The wording stays clear of every "
    "other phrase list in spec/enums.json, which is why the deadline is a date "
    "and not a countdown: expires in is a content:urgency_keywords phrase and "
    "this record carries no urgency code, so the body says expires on Tuesday "
    "5/5 and lets the Subject line carry the seven days, which the phrase pass "
    "does not read. There is no sign-in wording either, because the change "
    "happens on the machine in front of the reader and the portal page is the "
    "alternative for someone away from the network. Difficulty reason: the "
    "tier rule counts one decisive benign fact, the organization's own domain "
    "on the internal path, against one pressure fact, content:credential_request, "
    "so the base tier is medium; the body-only read is uncertain rather than "
    "the opposite of the verdict, so no adjustment applies. No injection. For "
    "the instructor: this is the honest half of the password pair and it is "
    "exam only, so no student sees it before week 8. 006 reached the same "
    "mailbox two weeks earlier with the same From address, the same display "
    "name, the same greeting form and the same signature line, and the two "
    "bodies say close to the same thing; that is why body_only_read is "
    "uncertain here rather than benign. Everything a reader can check inside "
    "the words, including the plain statement that the help desk will never "
    "ask for a password, is something a forger copies. The facts separate the "
    "two at once. Full credit on the indicators criterion needs "
    "sender:internal_domain and url:host_internal_known_good: the sender is "
    "the organization's own domain arriving on the internal path with no "
    "authentication block at all, and the one link host is on the internal "
    "known-good list in data/known_good_domains.json, where 006's "
    "pel1grave.example is on neither list. The week 4 loop should stop after "
    "one call: check_sender_reputation returns status internal at domain "
    "level, which is the stated stop condition, so stop_reason is "
    "internal_sender; check_urls would only confirm that "
    "portal.pellgrave.example is internal, and lookup_recipient would only "
    "confirm that Lenora Vashti is an ordinary mailbox with three prior "
    "reports and one true positive. Escalation: none. The verdict is benign, "
    "the category is legit_internal, and no benign escalation rule fits, since "
    "nothing here fails authentication on a trusted sender, touches a banking "
    "item or asks an unknown sender's question, so recommended_action is "
    "close_benign_reply_to_reporter. Story context: the true positive in "
    "Lenora Vashti's record is 006, the credential phish she released from "
    "quarantine and reported on 15 April. Two weeks later she reported the "
    "real reminder as well. That is the correct habit, and the reply the "
    "reference summary gives says so."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/exam/" + EMAIL_ID + ".eml",
    "set": "exam",
    "weeks": [8],
    "date": "2026-04-28T06:00:00-05:00",
    "verdict": "benign",
    "category": "legit_internal",
    "difficulty": "medium",
    "body_only_read": "uncertain",
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
         "value": ORG_DOMAIN},
        {"code": "header:auto_submitted", "where": "Auto-Submitted",
         "value": "auto-generated"},
        {"code": "url:host_internal_known_good", "where": "check_urls",
         "value": LINK_HOST},
        {"code": CONTENT_CODE, "where": "body", "value": CONTENT_VALUE},
        {"code": "header:external_flag", "where": "X-Sentrywick-External",
         "value": "no"},
        {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
         "value": None},
        {"code": "thread:new", "where": "In-Reply-To", "value": None},
    ],
    "required_indicators": ["sender:internal_domain",
                            "url:host_internal_known_good"],
    "url_hosts": [LINK_HOST],
    "attachment": None,
    "injection": None,
    "tool_expectations": {
        "check_sender_reputation": {
            "domain": ORG_DOMAIN,
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
        "check_urls": {LINK_HOST: "internal"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": "Lenora Vashti",
            "role": "Director of Sales",
            "mailbox_type": "person",
            "executive": False,
            "handles_payments": False,
            "chronic_reporter": False,
            "report_count_90d": 3,
            "true_positive_count_90d": 1,
            "campaign_tags": ["credential-phish", "marketing"],
        },
    },
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
    "notes": NOTES,
}


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    spec = load(SPEC_PATH)
    seed = spec["seed"]

    record = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            record = entry
            break
    if record is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    # Every semantic field is read and checked, never written.
    if record["set"] != "exam" or record["weeks"] != [8]:
        raise SystemExit("this is no longer an exam-only week 8 record")
    if record["subject"] != SUBJECT:
        raise SystemExit("subject does not match the manifest")
    if record["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if record["sender_address"] != SENDER:
        raise SystemExit("sender_address does not match the manifest")
    if record["recipient"] != RECIPIENT or record["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if record["reply_to"] is not None:
        raise SystemExit("the manifest now carries a Reply-To")
    if record["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if record["attachment"] is not None or record["injection"] is not None:
        raise SystemExit("the manifest now carries an attachment or an injection")
    if record["arrival_path"] != "internal":
        raise SystemExit("arrival_path is no longer internal")
    if record["date"] != GROUND_TRUTH["date"]:
        raise SystemExit("the manifest date is not the rendered Date")
    manifest_codes = [item.split(":", 2)[0] + ":" + item.split(":", 2)[1]
                      for item in record["indicators"]]
    if [item["code"] for item in GROUND_TRUTH["indicators"]] != manifest_codes:
        raise SystemExit("the ground truth indicator list is not the manifest's")

    data = build_eml(seed)
    os.makedirs(EXAM_DIR, exist_ok=True)
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
    display, address = email.utils.parseaddr(str(parsed["From"]))
    if display != SENDER_DISPLAY or address != SENDER:
        raise SystemExit("unfolded From is " + repr((display, address)))
    for name in ("Authentication-Results", "Received-SPF", "DKIM-Signature",
                 "X-Sentrywick-External", "X-Sentrywick-Spam-Score", "Reply-To",
                 "In-Reply-To", "References", "Thread-Topic", "X-Originating-IP",
                 "X-Priority", "Importance", "X-Sentrywick-Removed-Attachment"):
        if parsed[name] is not None:
            raise SystemExit(name + " must not appear on this message")

    # The manifest keeps the prose this generator is the source of; every
    # semantic field is read, never written, so the label and the file cannot
    # drift and no other record is touched.
    record["body_brief"] = BODY_BRIEF
    record["lure_summary"] = LURE_SUMMARY
    record["notes"] = MANIFEST_NOTES
    write_json(SPEC_PATH, spec)

    truth = load(GT_PATH)
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
    print("updated manifest prose and ground truth for " + EMAIL_ID)


if __name__ == "__main__":
    main()
