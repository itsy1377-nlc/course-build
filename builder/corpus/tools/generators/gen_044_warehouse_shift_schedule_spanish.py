#!/usr/bin/env python3
"""Regenerate 044-warehouse-shift-schedule-spanish.

Rebuilds emails/batch/044-warehouse-shift-schedule-spanish.eml byte for byte
from the corpus seed, refreshes the prose fields of its own manifest record in
spec/corpus-spec.json, and upserts its ground truth record in
ground_truth.json. It touches no other record and no data file.

Every identifier in the file that looks random is derived from the corpus seed,
so rerunning this script reproduces the same bytes:

    hexid(label, n)       = sha256("<seed>|<email id>|<label>").hexdigest()[:n]
    Message-ID left side  = <UTC stamp>.hexid("message-id", 12)
    MIME boundary         = "=_part_" + hexid("boundary", 12)
    gateway Received id   = hexid("gateway-id", 12), also X-Sentrywick-Message-UID
    store LMTP id         = UUID(hex=sha256(...|store-id)[:32], version=4)

There is no DKIM bh= or b= here and no sender-side Received id: the message
never leaves the organization, so nothing signs it and the only hop below the
mail store is the submission the workstation made to mail.pellgrave.example,
whose id is the one the gateway also writes into X-Sentrywick-Message-UID.

What this message is.

Casimir Hallowden, the warehouse supervisor, mails the weekend shift schedule
to the warehouse distribution list on the Thursday afternoon before it. He
writes it in Spanish, because most of his crew reads Spanish first, and he has
written it in Spanish every week for years. Nothing in it asks for anything:
there is a list of docks, times and names, one note about a delivery, one note
about a swap, and the standing reminder to put hours in the payroll portal
before Tuesday noon. The one link is the payroll vendor's employee portal,
my.fenwrightpay.example, which data/url_allowlist.json has carried since
2021-03-08.

The file exists so that a model which treats Spanish as a signal produces an
instructive false positive, and so that students see internal mail whose only
link leaves the company and is still trusted. Both facts are deterministic:
check_sender_reputation returns internal for pellgrave.example and check_urls
returns allowlisted for the portal host.

Header shape, and why each field is here:

  * No Authentication-Results, no Received-SPF, no DKIM-Signature and no
    X-Sentrywick-External. The workstation submitted over an authenticated
    session to mail.pellgrave.example, so the border gateway never saw the
    message, never authenticated it and never stamped it external. Missing is
    not failed, and the record says so with auth:not_evaluated_internal and
    header:external_flag:no. Neither body part carries the gateway banner,
    because the gateway inserts it only into the mail it flags.
  * X-Sentrywick-Scan-Result: clean and X-Sentrywick-Reported-By are written on
    internal submissions too: the first because the gateway scans everything it
    accepts, the second because every corpus message was reported. No spam
    score, which the gateway writes on external mail only.
  * Subject is one RFC 2047 encoded word, the form the manifest fixes. The
    decoded line is ASCII, so the encoding is the composer's habit rather than
    a necessity: this client encodes the whole Subject whenever the body it is
    about to send is not ASCII, and it Q-encodes the comma along with it. The
    word is 66 characters, inside the 75 character cap of RFC 2047 sec. 2, so
    it ships as one word on one line and needs no continuation.
  * Both body parts are quoted-printable, as the manifest's received_path_hint
    says, because the Spanish carries accented characters and the file has to
    stay seven-bit clean.

The delivering mail store is read from data/recipients.json rather than typed
here, because a mailbox lives on exactly one store and the LMTP hop is a
property of the mailbox and not of the path the message took. The To address is
a distribution list, and a list is not a mailbox: it expands at the submission
host and every member's store takes a copy. The copy the corpus keeps is the
one in the reporter's own mailbox, so the LMTP hop reads for
<h.quintanilla@pellgrave.example> and names mailstore-01, the store
recipients.json gives him, while To stays warehouse-staff@pellgrave.example and
the record keeps the list as the recipient. Hollis Quintanilla is the service
manager; he is on the warehouse list because his technicians pick up parts at
the dock, and he is the one who pressed report.

Headers deliberately absent, matching the manifest indicator list: no Reply-To;
no In-Reply-To and no References, so thread:new holds; no
X-Sentrywick-Removed-Attachment (attachment:none); no X-Priority and no
Importance, because a shift schedule does not flag itself; no X-Originating-IP,
which belongs to webmail submissions; no Auto-Submitted, because a person wrote
this and RFC 3834 sec. 5 marks system notices; and no Thread-Topic, which
section 9 of docs/email-header-realism.md gives to threaded internal mail and
this message starts a thread.

Wording. The record carries content:non_english_body and no other content code,
so no phrase from any other list in spec/enums.json may appear in either
decoded part; check_phrases() below proves that on the rendered file and
tools/validate_corpus.py proves it again. The Spanish does the work of avoiding
them by itself, but three are worth naming: the timesheet cutoff is written as
"antes del martes al mediodía" and never as a countdown, so nothing from
content:urgency_keywords appears and in particular no "today"; the portal is a
place to record hours and never a place to sign in, so nothing from
content:credential_request appears; and the link is named by its address in
both parts, so a reader of either one sees the host.

One departure from the manifest as authored, recorded rather than hidden, and
it touches no semantic field. The manifest's subject field held the wire form,
the encoded word itself. tools/validate_corpus.py compares a record's subject
with the value email.policy.default hands back for the header, which is the
decoded text, and it also requires the manifest and the ground truth to agree
on that field, so both cannot hold while the manifest carries the encoded form.
main() writes the decoded line into the manifest and the ground truth carries
the same string. Nothing is lost: the record's received_path_hint already gives
the decoded reading, the manifest notes record the wire form, and
header:encoded_word_subject is checked against the raw header in the rendered
file rather than against this field. 025 and 031 carry the same departure for
the same reason.

Run:  python3 corpus/tools/generators/gen_044_warehouse_shift_schedule_spanish.py
"""

import email
import email.policy
import hashlib
import json
import os
import uuid

EMAIL_ID = "044-warehouse-shift-schedule-spanish"
CORPUS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(CORPUS, "spec", "corpus-spec.json")
RECIPIENTS_PATH = os.path.join(CORPUS, "data", "recipients.json")
GT_PATH = os.path.join(CORPUS, "ground_truth.json")
EML_PATH = os.path.join(CORPUS, "emails", "batch", EMAIL_ID + ".eml")

LABEL_VERSION = "phase0-1.0"
LABELED_BY = "Phase 0 generator, from spec/corpus-spec.json 1.0, rendered 2026-09-04"
REVIEWED_BY = "not yet reviewed"

# ------------------------------------------------------------------ parties

SENDER = "c.hallowden@pellgrave.example"
SENDER_DISPLAY = "Casimir Hallowden"
# The envelope sender is the From mailbox. A person writing to a list from his
# own workstation has no reason to aim the bounces anywhere else, which is what
# separates this file from 002, where a ticket system broadcasting to several
# hundred mailboxes puts Return-Path on a mailbox nobody works.
ENVELOPE_SENDER = SENDER
ORG_DOMAIN = "pellgrave.example"
RECIPIENT = "warehouse-staff@pellgrave.example"
RECIPIENT_DISPLAY = "Warehouse Staff Distribution List"
REPORTER = "h.quintanilla@pellgrave.example"

SUBMIT_HOST = "mail.pellgrave.example"
SUBMIT_IP = "10.20.4.25"
WORKSTATION = "PMG-WS-2451.corp.pellgrave.example"
WORKSTATION_IP = "10.20.31.140"

SCAN_RESULT = "clean"

# ---------------------------------------------------------------- timestamps
#
# The manifest fixes the Date at 2026-04-23T16:20:00-05:00, a Thursday
# afternoon, which is 21:20:00 UTC. Everything inside the organization stamps
# local time, so the chain reads 16:20:01 at the submission host and 16:20:02
# at the store, and the Message-ID left side carries the UTC form of the Date.
DATE_HEADER = "Thu, 23 Apr 2026 16:20:00 -0500"
SUBMIT_STAMP = "Thu, 23 Apr 2026 16:20:01 -0500"
STORE_STAMP = "Thu, 23 Apr 2026 16:20:02 -0500"
MESSAGE_ID_STAMP = "20260423212000"

# ------------------------------------------------------------------ subject
#
# The wire form, fixed by the manifest, and the line a parser and a reader both
# see. The encoded word is 66 characters, inside the 75 character cap of
# RFC 2047 sec. 2, and "Subject: " plus the word is 75 characters, inside the
# 78 character fold width, so it ships whole on one line.
SUBJECT_WORD = ("=?UTF-8?Q?Horario_de_turnos_de_fin_de_semana=2C_25_y_26_de_"
                "abril?=")
SUBJECT = "Horario de turnos de fin de semana, 25 y 26 de abril"

# --------------------------------------------------------------------- link
#
# The payroll vendor's employee portal, on data/url_allowlist.json since
# 2021-03-08 and the same host 017 links to. The path names the thing the
# reminder is about and asks for no sign-in, so url:login_path does not fire
# and the record does not carry it.
LINK = "https://my.fenwrightpay.example/timesheets"
LINK_HOST = "my.fenwrightpay.example"

# --------------------------------------------------------- quoted-printable
#
# RFC 2045 sec. 6.7: an encoded line is at most 76 characters counting the
# trailing "=" soft break, a soft break may not split an "=XX" escape, and
# white space may not sit at the end of an encoded line.
QP_MAX = 76


def qp_tokens(line):
    """One logical line as a list of quoted-printable atoms.

    An atom is one printable ASCII character or one three character "=XX"
    escape, so a wrap between atoms can never split an escape. The text is
    encoded as UTF-8 first, because both parts declare charset=utf-8 and the
    Spanish is not ASCII; encoding the code points instead would write latin-1
    bytes under a utf-8 label.
    """
    out = []
    for byte in line.encode("utf-8"):
        if byte == 0x3D:
            out.append("=3D")
        elif 0x20 <= byte <= 0x7E:
            out.append(chr(byte))
        else:
            out.append("=%02X" % byte)
    return out


def qp_wrap(line):
    """Encode one logical line as quoted-printable with soft line breaks.

    The break is taken at the start of a run of spaces wherever the text
    offers one before the limit, so the spaces lead the next line, no encoded
    line ends in white space and no word is cut in half. Decoding removes the
    soft break, which puts the spaces back where they were. The body of this
    message folds at FOLD_WIDTH and needs no soft break at all; this is here
    so the encoder is correct rather than merely unused.
    """
    atoms = qp_tokens(line)
    out = []
    start = 0
    while True:
        end = start
        length = 0
        while end < len(atoms) and length + len(atoms[end]) <= QP_MAX - 1:
            length += len(atoms[end])
            end += 1
        if end >= len(atoms):
            out.append("".join(atoms[start:]))
            return out
        cut = None
        for index in range(end, start, -1):
            if atoms[index] == " ":
                cut = index
                while cut > start and atoms[cut - 1] == " ":
                    cut -= 1
                break
        if cut is None or cut <= start:
            cut = end
            while cut > start + 1 and atoms[cut - 1] in (" ", "\t"):
                cut -= 1
        out.append("".join(atoms[start:cut]) + "=")
        start = cut


def encode(lines):
    out = []
    for line in lines:
        out += qp_wrap(line)
    return out


# ---------------------------------------------------------------- body text
#
# Wording rules, all from the content_phrases lists in spec/enums.json. The
# record carries content:non_english_body and nothing else, so no phrase from
# any other list may appear in either decoded part. validate_corpus.py runs
# every list against the two decoded parts joined together and fails a phrase
# with no code as loudly as a code with no phrase; check_phrases() below runs
# the same test inside this generator so the file cannot ship broken.
#
#   Nothing from content:urgency_keywords: the cutoff is named by its day and
#   its hour, "antes del martes al mediodía", and never counted down, so there
#   is no "today", no "as soon as possible", no "action required". The Spanish
#   "hoy" does not appear either, because nothing here is about today.
#   Nothing from content:credential_request: hours are recorded in the portal,
#   and the message never mentions an account, a sign-in or a password.
#   Nothing from content:file_share_lure: there is no file, nothing is shared
#   and nothing is downloaded; the schedule is in the message.
#   Nothing from content:payment_request or content:payment_change_request:
#   the payroll portal is where hours go, not where money moves.
#   Nothing from content:phone_verification_offered: the extension in the
#   signature is a signature line on internal mail, not an offer to confirm
#   anything by telephone, and no phrase from that list appears.
#
# The register is one supervisor writing to his own crew: he names people by
# first name in the prose and in full in the list, he explains one swap and one
# delivery because those are the two things that changed, he asks to be told by
# tomorrow if a shift does not work, and he signs with his first name over a
# four digit extension. The ten Spanish function words the manifest asks for
# (de, la, el, los, para, con, en, que, es, del) all stand as whole words.
#
# Every name below is invented for this file. None of them is in
# data/recipients.json, which holds mailbox owners; a warehouse crew of about
# ninety people has no corpus mailbox and needs none.

# Paragraphs are written whole and folded once, so the plain part and the HTML
# part break in the same places and a part to part diff is empty. The fold
# width counts quoted-printable characters rather than code points, because an
# accented letter is two UTF-8 bytes and costs six characters once encoded;
# 68 leaves room for the "<p>", "</p>" and "<br>" the HTML part adds and keeps
# every encoded line inside the 76 character limit of RFC 2045 sec. 6.7 without
# a single soft break.
FOLD_WIDTH = 68

OPENING_TEXT = (
    "Equipo, aquí está el horario de turnos para el sábado 25 y el domingo "
    "26 de abril. Es el mismo reparto de la semana pasada, con un cambio: "
    "Teodoro entra el domingo y no el sábado, porque el sábado tiene la "
    "revisión del montacargas."
)

# The schedule. The plain part lines the columns up with spaces and the HTML
# part carries the same strings between <br> tags, where a browser collapses
# the runs of spaces; that is what a mail client does with a hand typed table
# and it is why both parts say the same words.
SATURDAY_HEAD = "Sábado 25 de abril"
SATURDAY_ROWS = [
    "  Muelle 1    06:00 a 14:00   Nadia Quesalva, Rubén Barandas",
    "  Muelle 2    06:00 a 14:00   Ofelia Castroval",
    "  Muelle 1    14:00 a 22:00   Marco Delvenga, Inés Solveira",
    "  Recepción   07:00 a 15:00   Gaspar Verlanda",
]

SUNDAY_HEAD = "Domingo 26 de abril"
SUNDAY_ROWS = [
    "  Muelle 2    08:00 a 16:00   Teodoro Milvane, Nadia Quesalva",
    "  Recepción   08:00 a 16:00   Ofelia Castroval",
]

DELIVERY_TEXT = (
    "El camión de Slatemoor llega el sábado sobre las 09:00 con catorce "
    "paletas, así que dejen libre el muelle 2 hasta que lo descarguemos. Si "
    "alguien no puede con su turno, díganmelo mañana viernes y lo cambiamos "
    "entre los dos días."
)

REMINDER_TEXT = (
    "Recuerden registrar sus horas en el portal antes del martes al mediodía. "
    "Es el mismo enlace de siempre:"
)

CLOSING = "Gracias,"

# A person's signature: first name, then the role and the four digit extension
# that section 2.3 of the corpus design allows. No telephone number outside the
# extension, and no address.
SIGNATURE = [
    "Casimir",
    "Supervisor de almacén, ext. 4215",
]

# The opening sentence, as the ground truth quotes it for
# content:non_english_body. It is the first two lines of both parts read as one
# sentence, which is how a reader meets it.
NON_ENGLISH_QUOTE = ("Equipo, aquí está el horario de turnos para el "
                     "sábado 25 y el domingo 26 de abril")

# The ten Spanish function words the manifest asks for, checked as whole words
# against the rendered plain part.
FUNCTION_WORDS = ["de", "la", "el", "los", "para", "con", "en", "que", "es", "del"]


def hexid(seed, label, length=12):
    return hashlib.sha256((seed + "|" + EMAIL_ID + "|" + label).encode()).hexdigest()[:length]


def store_id(seed):
    return str(uuid.UUID(hex=hexid(seed, "store-id", 32), version=4))


def recipient_record(address):
    with open(RECIPIENTS_PATH, encoding="utf-8") as handle:
        recipients = json.load(handle)
    for record in recipients["recipients"]:
        if record["address"] == address:
            return record
    raise SystemExit("recipients.json has no record for " + address)


def delivery(recipient, reporter):
    """The mailbox this copy was delivered to and the one store that holds it.

    A person or a shared mailbox receives the message itself. A distribution
    list is delivered by expansion instead: it expands at the submission host
    and every member's store takes a copy, so the file the corpus keeps is the
    copy in the reporter's mailbox and the LMTP hop names the reporter and the
    reporter's store while To stays the list.
    """
    entry = recipient_record(recipient)
    if entry.get("mailbox_type") == "list":
        entry = recipient_record(reporter)
    store = entry.get("mailstore")
    if not store:
        raise SystemExit("recipients.json has no mailstore for " + entry["address"])
    return entry["address"], store


def encoded_length(text):
    """How long this text is once quoted-printable has encoded it."""
    return len("".join(qp_tokens(text)))


def wrap(text, width=FOLD_WIDTH):
    """Greedy fold on single spaces, measured in quoted-printable characters."""
    lines = []
    current = ""
    for word in text.split(" "):
        candidate = (current + " " + word) if current else word
        if current and encoded_length(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    return lines


OPENING = wrap(OPENING_TEXT)
DELIVERY = wrap(DELIVERY_TEXT)
REMINDER = wrap(REMINDER_TEXT)


def plain_part():
    lines = list(OPENING) + [""]
    lines += [SATURDAY_HEAD] + SATURDAY_ROWS + [""]
    lines += [SUNDAY_HEAD] + SUNDAY_ROWS + [""]
    lines += DELIVERY + [""]
    lines += REMINDER + [""]
    lines += [LINK, ""]
    lines += [CLOSING, ""]
    lines += SIGNATURE
    return lines


def paragraph_html(lines):
    """One paragraph as one <p>, the same words on the same lines as the plain part."""
    block = list(lines)
    block[0] = "<p>" + block[0]
    block[-1] = block[-1] + "</p>"
    return block


def block_html(lines):
    """A run of short lines as one <p> with <br> between them."""
    block = [line + "<br>" for line in lines[:-1]]
    block[0] = "<p>" + block[0]
    block.append(lines[-1] + "</p>")
    return block


def html_part():
    """The HTML source lines, before quoted-printable encoding.

    Plain paragraphs and one anchor: no wrapper div, no table, no button, no
    image, no styling trick and no hidden text. The record does not carry
    content:html_hidden_text and validate_corpus.py fails a file that hides
    text the record does not declare.
    """
    lines = ["<html>", "<body>"]
    lines += paragraph_html(OPENING)
    lines += block_html([SATURDAY_HEAD] + SATURDAY_ROWS)
    lines += block_html([SUNDAY_HEAD] + SUNDAY_ROWS)
    lines += paragraph_html(DELIVERY)
    lines += paragraph_html(REMINDER)
    # The href and the visible text are the same address, so a reader of either
    # part sees the host the link goes to.
    lines += ['<p><a href="' + LINK + '"', "  >" + LINK + "</a></p>"]
    lines += ["<p>" + CLOSING + "</p>"]
    lines += block_html(SIGNATURE)
    lines += ["</body>", "</html>"]
    return lines


def build_eml(seed):
    boundary = "=_part_" + hexid(seed, "boundary")
    message_id = ("<" + MESSAGE_ID_STAMP + "." + hexid(seed, "message-id")
                  + "@" + SUBMIT_HOST + ">")
    gateway_id = hexid(seed, "gateway-id")
    lmtp_id = store_id(seed)
    mailbox, store = delivery(RECIPIENT, REPORTER)

    lines = [
        "Return-Path: <" + ENVELOPE_SENDER + ">",
        # RFC 5321 sec. 4.4: the store prepends Return-Path and its own
        # Received at final delivery, so those two are the top of the file.
        "Received: from " + SUBMIT_HOST + " (" + SUBMIT_HOST + " [" + SUBMIT_IP + "])",
        "  by " + store + ".pellgrave.example (Sentrywick Store 4.2) with LMTP",
        "  id " + lmtp_id,
        "  for <" + mailbox + ">; " + STORE_STAMP,
        # The gateway writes these on its own submissions too. There is no
        # Authentication-Results, no Received-SPF and no spam score, because
        # the message never crossed the border.
        "X-Sentrywick-Scan-Result: " + SCAN_RESULT,
        "X-Sentrywick-Message-UID: " + gateway_id,
        "X-Sentrywick-Reported-By: " + REPORTER,
        # RFC 3848 sec. 1: ESMTPSA is TLS plus authentication, which is what a
        # workstation on the corporate network does when it submits.
        "Received: from " + WORKSTATION + " ([" + WORKSTATION_IP + "])",
        "  by " + SUBMIT_HOST + " (Sentrywick Gateway 7.4) with ESMTPSA",
        "  id " + gateway_id + "; " + SUBMIT_STAMP,
        "Date: " + DATE_HEADER,
        "From: " + SENDER_DISPLAY + " <" + SENDER + ">",
        "To: " + RECIPIENT_DISPLAY + " <" + RECIPIENT + ">",
        "Subject: " + SUBJECT_WORD,
        "Message-ID: " + message_id,
        "MIME-Version: 1.0",
        'Content-Type: multipart/alternative; boundary="' + boundary + '"',
        "",
        "--" + boundary,
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    plain = encode(plain_part())
    html = encode(html_part())
    # RFC 2045 sec. 6.7: no encoded line over 76 characters, and no encoded
    # line ending in white space. The fold width above means neither part
    # carries a soft line break at all, so this also proves that.
    for label, part in (("plain", plain), ("HTML", html)):
        for line in part:
            if len(line) > QP_MAX:
                raise SystemExit("quoted-printable line over " + str(QP_MAX)
                                 + " characters in the " + label + " part: " + line)
            if line[-1:] in (" ", "\t"):
                raise SystemExit("quoted-printable line ends in white space in the "
                                 + label + " part: " + repr(line))
        if any(line.endswith("=") for line in part):
            raise SystemExit("the " + label + " part carries a soft line break; the "
                             "fold width is meant to make every logical line fit")

    lines += plain
    lines += [
        "--" + boundary,
        "Content-Type: text/html; charset=utf-8",
        "Content-Transfer-Encoding: quoted-printable",
        "",
    ]
    lines += html
    lines += ["--" + boundary + "--", ""]

    for line in lines:
        if len(line) > 78:
            raise SystemExit("line over 78 characters: " + line)
        line.encode("ascii")
    return "\r\n".join(lines).encode("ascii")


# --------------------------------------------------------------- self checks


def check_phrases(parsed, enums):
    """No phrase from a content list this record does not carry is in the body.

    validate_corpus.py runs the same test and fails a phrase with no code as
    loudly as a code with no phrase. It skips content:non_english_body, whose
    list is Spanish stopwords that sit inside ordinary English words and which
    is the one code this record does carry, so the test here skips it too and
    checks the ten function words the manifest asks for separately.
    """
    body = ""
    for part in parsed.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            body += part.get_content() + "\n"
    lowered = body.lower()
    for code, phrases in sorted((enums.get("content_phrases") or {}).items()):
        if code in ("content:non_english_body", "content:instruction_to_ai"):
            continue
        for phrase in phrases:
            if phrase.lower() in lowered:
                raise SystemExit("body carries the " + code + " phrase "
                                 + repr(phrase) + ", whose code this record does not list")
    words = set()
    for line in plain_part():
        for token in line.replace(",", " ").replace(":", " ").replace(".", " ").split():
            words.add(token.lower())
    missing = [word for word in FUNCTION_WORDS if word not in words]
    if missing:
        raise SystemExit("the body is missing the Spanish function words " + repr(missing))
    if NON_ENGLISH_QUOTE not in " ".join(" ".join(plain_part()).split()):
        raise SystemExit("the recorded non_english_body quote is not in the plain part")


def check_link(parsed):
    """The one link is in both parts, and its host is the allowlisted portal.

    url:host_allowlisted is one of the two required indicators, so the host is
    read back from data/url_allowlist.json rather than trusted: a link the SOC
    does not actually trust would make the record's decisive benign fact wrong.
    """
    for part in parsed.walk():
        if part.get_content_type() in ("text/plain", "text/html"):
            if part.get_content().count(LINK) < 1:
                raise SystemExit("the link is missing from the "
                                 + part.get_content_type() + " part")
    with open(os.path.join(CORPUS, "data", "url_allowlist.json"), encoding="utf-8") as handle:
        allowlist = json.load(handle)
    hosts = {entry["host"] for entry in allowlist["hosts"]}
    if LINK_HOST not in hosts:
        raise SystemExit(LINK_HOST + " is not in data/url_allowlist.json")


# ------------------------------------------------------------ manifest text

BODY_BRIEF = (
    "In Spanish, in the voice of one supervisor writing to his own crew. It "
    "opens 'Equipo, aquí está el horario de turnos para el sábado 25 y el "
    "domingo 26 de abril', says the split is the same as last week with one "
    "change, and explains the change: Teodoro comes in on Sunday instead of "
    "Saturday because the forklift inspection is on Saturday. Then a plain "
    "table under 'Sábado 25 de abril' and 'Domingo 26 de abril', one line per "
    "shift, each naming a dock or the receiving desk, a start and end time and "
    "the one or two people on it: Nadia Quesalva, Rubén Barandas, Ofelia "
    "Castroval, Marco Delvenga, Inés Solveira, Gaspar Verlanda and Teodoro "
    "Milvane, all invented for this file and none of them a mailbox in "
    "recipients.json. Then two short notes: the Slatemoor truck arrives "
    "Saturday around 09:00 with fourteen pallets so dock 2 stays clear until "
    "it is unloaded, and anyone who cannot work a shift should say so by "
    "Friday. Then the closing reminder 'Recuerden registrar sus horas en el "
    "portal antes del martes al mediodía', a line saying it is the usual link, "
    "and the link itself on its own line, https://my.fenwrightpay.example/"
    "timesheets, with the same address as the visible text in both parts. The "
    "ten Spanish function words the record asks for all stand as whole words: "
    "de, la, el, los, para, con, en, que, es and del. No word about a "
    "password, an account or a sign-in, and no urgency beyond the Tuesday "
    "timesheet cutoff, which is named by its day and its hour and never "
    "counted down. Signs 'Casimir' over 'Supervisor de almacén, ext. 4215'. "
    "No attachment, no thread, no Reply-To."
)

LURE_SUMMARY = (
    "The warehouse supervisor sends the weekend shift schedule to the "
    "warehouse list, written in Spanish, with dock times and names and a "
    "closing reminder to record hours in the payroll portal before Tuesday "
    "noon. No attachment, no thread and no request beyond that reminder, and "
    "the one link goes to the payroll vendor's allowlisted employee portal."
)

MANIFEST_NOTES = (
    "Included so a model that treats non-English text as suspicious produces "
    "an instructive false positive, and so students see internal mail that "
    "links to an external allowlisted host. Reported by the service manager, "
    "who is on the warehouse list because his technicians pick up parts there. "
    "Rendering: the Subject ships as one RFC 2047 encoded word, "
    "'" + SUBJECT_WORD + "', 66 characters and so inside the 75 character cap "
    "of RFC 2047 sec. 2, and it decodes to '" + SUBJECT + "'. The subject "
    "field above now holds that decoded text, which is what a parser and a "
    "reader both see and what tools/validate_corpus.py compares against the "
    "file; the wire form is kept here. The decoded line is ASCII, so the "
    "encoding is the composer's habit rather than a charset necessity: this "
    "client encodes the whole Subject whenever the body it is about to send is "
    "not ASCII. Both body parts are quoted-printable for that body. The list "
    "expands at the submission host, so the file the corpus keeps is the copy "
    "delivered to the reporter's own mailbox: the LMTP hop reads for "
    "<h.quintanilla@pellgrave.example> and names mailstore-01, the store "
    "recipients.json gives him, while To stays warehouse-staff@pellgrave."
    "example, which is what recipient:distribution_list and the "
    "lookup_recipient expectation key on. Week 7 use: the batch pair to 002 in "
    "the teaching set, an ordinary internal notice whose only link leaves the "
    "company and is still trusted."
)

MANIFEST_INDICATORS = [
    "auth:not_evaluated_internal",
    "sender:internal_domain",
    "header:encoded_word_subject",
    "content:non_english_body",
    "url:host_allowlisted:my.fenwrightpay.example",
    "header:external_flag:no",
    "attachment:none",
    "thread:new",
    "recipient:distribution_list",
]

# --------------------------------------------------------------- ground truth

GT_INDICATORS = [
    {"code": "auth:not_evaluated_internal", "where": "Authentication-Results",
     "value": None},
    {"code": "sender:internal_domain", "where": "From, Received",
     "value": ORG_DOMAIN},
    {"code": "header:encoded_word_subject", "where": "Subject",
     "value": SUBJECT_WORD},
    {"code": "content:non_english_body", "where": "body",
     "value": NON_ENGLISH_QUOTE},
    {"code": "url:host_allowlisted", "where": "check_urls", "value": LINK_HOST},
    {"code": "header:external_flag", "where": "X-Sentrywick-External",
     "value": "no"},
    {"code": "attachment:none", "where": "X-Sentrywick-Removed-Attachment",
     "value": None},
    {"code": "thread:new", "where": "In-Reply-To", "value": None},
    {"code": "recipient:distribution_list", "where": "lookup_recipient",
     "value": RECIPIENT},
]

REFERENCE_SUMMARY = (
    "This is Casimir's real weekend schedule for the warehouse team, sent from "
    "inside the company, with a link to the payroll portal we all use. Nothing "
    "is wrong with it."
)

GT_NOTES = (
    "Key facts a correct extractor produces: from_domain pellgrave.example, "
    "the organization's own domain, arriving on the internal path; "
    "display_name_mismatch false, because data/display_names.json owns the "
    "name Casimir Hallowden to pellgrave.example and sources it from "
    "recipients.json:c.hallowden@pellgrave.example; reply_to_domain none, "
    "since the file carries no Reply-To; spf, dkim, dmarc and dmarc_policy all "
    "null, because the message never crossed the border gateway and the file "
    "carries no Authentication-Results header at all, which is "
    "auth:not_evaluated_internal and not a failure of anything; Return-Path is "
    "the From mailbox, because a person writing to a list from his own "
    "workstation has no reason to aim the bounces anywhere else; one link "
    "host, my.fenwrightpay.example, carrying the single link "
    "https://my.fenwrightpay.example/timesheets, which appears once in the "
    "plain part and once in the HTML part where the href and the visible text "
    "are the same address; no removed-attachment header; no In-Reply-To and no "
    "References, so the thread is new. Received chain: "
    "PMG-WS-2451.corp.pellgrave.example [10.20.31.140], Casimir's workstation, "
    "submitted with ESMTPSA to mail.pellgrave.example [10.20.4.25] at 16:20:01 "
    "-0500, and mail.pellgrave.example delivered by LMTP to "
    "mailstore-01.pellgrave.example at 16:20:02; Date is 16:20:00 -0500, the "
    "same instant as the 20260423212000 stamp in the Message-ID. The list "
    "expanded at the submission host, so this file is the copy delivered to "
    "the reporter's own mailbox: the LMTP hop reads for "
    "<h.quintanilla@pellgrave.example> and names mailstore-01, the store "
    "data/recipients.json gives that mailbox, while To stays "
    "warehouse-staff@pellgrave.example, which is what "
    "recipient:distribution_list and the lookup_recipient expectation key on. "
    "recipients.json records mailstore-02 for the list itself, but the copy "
    "the corpus keeps is the one delivered to an individual member, so the "
    "hop names the reporter's own store; every mailbox in the corpus lives on "
    "exactly one store whatever path a message took. X-Sentrywick-External is "
    "absent, which the extractor records as header:external_flag with the "
    "value no, and neither body part carries the gateway banner, because the "
    "gateway inserts it only into the mail it stamps as external. The gateway "
    "still wrote X-Sentrywick-Scan-Result: clean on its own submission, and "
    "X-Sentrywick-Reported-By names Hollis Quintanilla, who reported it; there "
    "is no spam score, which the gateway writes on external mail only. The "
    "Subject is an RFC 2047 encoded word, "
    "'" + SUBJECT_WORD + "', which decodes to '" + SUBJECT + "'. It is "
    "extraction practice and not a signal of anything: the decoded line is "
    "ASCII, so the encoding is the composer's habit, this client encoding the "
    "whole Subject whenever the body it is about to send is not ASCII, and it "
    "Q-encodes the comma with it. Body: multipart/alternative, a text/plain "
    "part then a text/html part, both quoted-printable because the Spanish is "
    "not ASCII and the file has to stay seven-bit clean, both carrying the "
    "same words, and the HTML part is plain paragraphs with one anchor and no "
    "image, script, form, styling trick or hidden text. Content: the warehouse "
    "supervisor sends the weekend shift schedule for Saturday 25 and Sunday 26 "
    "April, says the split is the same as last week except that Teodoro moves "
    "from Saturday to Sunday because the forklift inspection is Saturday "
    "morning, lists each shift with its dock or the receiving desk, its start "
    "and end time and the one or two people on it, notes that the Slatemoor "
    "truck arrives Saturday around 09:00 with fourteen pallets so dock 2 stays "
    "clear until it is unloaded, asks anyone who cannot work a shift to say so "
    "by Friday, and closes with the standing reminder to record hours in the "
    "payroll portal before Tuesday noon over the one link. He signs with his "
    "first name over his role and extension 4215. Every crew name in the "
    "schedule is invented for this file and none of them is a mailbox in "
    "recipients.json, which holds mailbox owners rather than a ninety person "
    "warehouse crew. content:non_english_body is the only content code: the "
    "message is Spanish end to end, which is how this supervisor has always "
    "written to this list, and no phrase from any other list in "
    "spec/enums.json appears in either part. In particular the timesheet "
    "cutoff is named by its day and its hour and never counted down, so "
    "nothing from content:urgency_keywords fires; the portal is where hours go "
    "and never a place to sign in, so nothing from content:credential_request "
    "fires; and the extension in the signature is a signature line rather than "
    "an offer to confirm anything by telephone, so "
    "content:phone_verification_offered does not fire and no phrase from its "
    "list appears. Difficulty reason: the tier rule counts one decisive benign "
    "fact, the organization's own domain on the internal path, against no "
    "pressure fact, so the base tier is easy; the body-only read is benign, "
    "the same as the verdict, so no adjustment applies, and there is no "
    "injection. Week 7 loop: check_sender_reputation returns status internal "
    "at domain level for pellgrave.example, which is the stated stop "
    "condition, so the loop stops after one call with stop_reason "
    "internal_sender; check_urls would only confirm that my.fenwrightpay."
    "example is allowlisted, and lookup_recipient would only confirm that "
    "warehouse-staff@pellgrave.example is a distribution list with no report "
    "history of its own. Escalation: none. The verdict is benign, the category "
    "is legit_internal, and no benign escalation rule fits, since nothing here "
    "fails authentication on a trusted sender, touches a banking item or asks "
    "an unknown sender's question, so recommended_action is "
    "close_benign_reply_to_reporter. For the instructor: this is the batch "
    "pair to 002 in the teaching set. Both are ordinary internal housekeeping "
    "that a triage agent has to close; 002 links to the company's own status "
    "page and this one links off the company network to a vendor host that the "
    "SOC trusts anyway, which is the second thing an agent has to learn to "
    "read. Grading note: a model that calls this suspicious because the body "
    "is not in English has scored a language as a signal, and a model that "
    "calls the external link a tell has not run check_urls or has not read "
    "what allowlisted means. Story context: Hollis Quintanilla reported it, "
    "which is why the file exists at all; he is the service manager and he "
    "sits on the warehouse list because his technicians pick up parts at the "
    "dock, and his record shows two prior reports, one of them a true "
    "positive, so he is not a chronic reporter and the queue takes his reports "
    "seriously."
)

GROUND_TRUTH = {
    "id": EMAIL_ID,
    "file": "emails/batch/" + EMAIL_ID + ".eml",
    "set": "batch",
    "weeks": [7],
    "date": "2026-04-23T16:20:00-05:00",
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
    "indicators": GT_INDICATORS,
    "required_indicators": ["sender:internal_domain", "url:host_allowlisted"],
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
            "notes": ("The organization's own domain. A From address on this domain "
                      "arriving through the external gateway is a forgery unless "
                      "quarantined and released."),
            "match_level": "domain",
        },
        "check_urls": {LINK_HOST: "allowlisted"},
        "lookup_recipient": {
            "address": RECIPIENT,
            "name": RECIPIENT_DISPLAY,
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
    with open(os.path.join(CORPUS, "spec", "enums.json"), encoding="utf-8") as handle:
        enums = json.load(handle)

    manifest = None
    for entry in spec["emails"]:
        if entry["id"] == EMAIL_ID:
            manifest = entry
            break
    if manifest is None:
        raise SystemExit("manifest has no record " + EMAIL_ID)
    # The semantic fields are the specification and are read, never rewritten.
    # The indicator list is checked rather than written, so a later edit to the
    # manifest shows up as a loud failure here instead of being overwritten.
    if manifest["indicators"] != MANIFEST_INDICATORS:
        raise SystemExit("manifest indicator list for " + EMAIL_ID
                         + " differs from the list this generator renders")
    if manifest["sender_address"] != SENDER or manifest["reply_to"] is not None:
        raise SystemExit("From or Reply-To does not match the manifest")
    if manifest["sender_display"] != SENDER_DISPLAY:
        raise SystemExit("sender_display does not match the manifest")
    if manifest["recipient"] != RECIPIENT or manifest["reporter"] != REPORTER:
        raise SystemExit("recipient or reporter does not match the manifest")
    if manifest["url_hosts"] != [LINK_HOST]:
        raise SystemExit("url_hosts do not match the manifest")
    if manifest["attachment"] is not None or manifest["injection"] is not None:
        raise SystemExit("this record has no attachment and no injection")
    # The manifest may carry the subject on the wire or as it decodes; both
    # readings name the same header. Anything else is a real mismatch.
    if manifest["subject"] not in (SUBJECT, SUBJECT_WORD):
        raise SystemExit("subject does not match the manifest: "
                         + repr(manifest["subject"]))

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
        raise SystemExit("decoded Subject is " + repr(str(parsed["Subject"])))
    if str(parsed["From"]) != SENDER_DISPLAY + " <" + SENDER + ">":
        raise SystemExit("unfolded From is " + repr(str(parsed["From"])))
    if parsed["Reply-To"] is not None:
        raise SystemExit("a Reply-To was written; this record has none")
    if parsed["Authentication-Results"] is not None:
        raise SystemExit("an Authentication-Results was written on internal mail")
    check_phrases(parsed, enums)
    check_link(parsed)

    subject_rewritten = manifest["subject"] != SUBJECT
    manifest["subject"] = SUBJECT
    manifest["body_brief"] = BODY_BRIEF
    manifest["lure_summary"] = LURE_SUMMARY
    manifest["notes"] = MANIFEST_NOTES
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
    print("updated the manifest prose and upserted ground truth for " + EMAIL_ID)
    if subject_rewritten:
        print("note: the manifest subject field held the raw encoded word; it now "
              "holds the decoded text, and the wire form is recorded in the manifest "
              "notes and in the header:encoded_word_subject indicator value")


if __name__ == "__main__":
    main()
