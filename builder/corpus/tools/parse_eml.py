#!/usr/bin/env python3
"""
parse_eml.py: read one .eml file and return the facts a triage agent needs.

An .eml file is an email saved as plain text: a block of headers, one blank
line, and then the body. A header is one named line such as "Subject: ..." or
"From: ...". This helper turns one .eml file into a Python dictionary, so a
notebook can look up each fact by name, for example parsed["from_domain"].

How to use it in a notebook:

    from parse_eml import parse_eml
    parsed = parse_eml("emails/teaching/001-payroll-deposit-verify.eml")
    print(parsed["subject"])
    print(parsed["auth"]["spf"])

How to use it from the command line:

    python3 parse_eml.py path/to/one.eml path/to/another.eml

The dictionary has these keys:

    subject                the Subject line with any encoding undone, or None
    from_display           the display name in From (the friendly name that
                           appears before the address), or "" when there is none
    from_address           the address in From, or None
    from_domain            the part of from_address after the @, in lowercase
    reply_to               the address in Reply-To, or None
    return_path            the address in Return-Path, or None
    to                     list of addresses in To (usually one)
    cc                     list of addresses in Cc (often empty)
    date                   the Date header as an ISO 8601 string, which looks
                           like "2026-04-13T07:41:00-05:00", or None
    message_id             the Message-ID with its angle brackets, or None
    in_reply_to            the In-Reply-To id, or None
    references             list of ids from the References header
    auth                   the sender checks as the gateway wrote them:
                           {"spf", "dkim", "dmarc", "dmarc_policy", "raw"}.
                           Internal mail has no such header, so all are None.
    received               list of hops, top (most recent) first, each
                           {"from_host", "by_host", "ip", "timestamp"}
    x_originating_ip       the client address a webmail provider recorded,
                           or None
    gateway                what the mail gateway stamped: {"external",
                           "scan_result", "spam_score", "reported_by",
                           "message_uid"}
    body_text              the text/plain part; when there is none, the HTML
                           part converted to text
    body_html              the text/html part exactly as written, or None
    body_html_text         the HTML part converted to text (tags removed)
    hidden_html_text       text the HTML hides from a reader: comments, and
                           anything styled display:none or font-size:0
    urls                   every http or https link in order of appearance,
                           plain part first, then the HTML part
    url_hosts              the host of each link, with repeats removed
    attachments            one dict per X-Sentrywick-Removed-Attachment header:
                           {"filename", "size", "sha256", "action", "type",
                           "reason"}. The gateway removed the file; only the
                           facts about it remain.
    display_name_mismatch  True when the name on the message points at a
                           different organization than from_domain, or when
                           Reply-To goes to a different domain. The rules are
                           in check_display_name_mismatch below.
    raw_headers            every header as [name, value], in file order

SPF, DKIM and DMARC are the three checks a mail gateway runs on an incoming
message. SPF asks whether the sending server may send for the sender's domain.
DKIM checks a signature on the message. DMARC asks whether either of those
passed for the domain shown in From, and applies the domain owner's policy.
This helper only reads the results the gateway wrote; it never repeats them.

Only the Python standard library is used. Nothing needs to be installed.
"""

import email
import email.policy
import email.utils
import html
import re
import sys
from html.parser import HTMLParser


# The gateway writes one of these headers for every file it removed.
REMOVED_ATTACHMENT_HEADER = "X-Sentrywick-Removed-Attachment"

# Finds an http or https link. It stops at whitespace, quotes and angle brackets.
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+")

# Characters that often sit right after a link in a sentence but are not part of it.
URL_TRAILING = ".,;:!?)]}>'\""

# HTML tags that start a new line when HTML is turned into text.
BLOCK_TAGS = ("p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "table",
              "ul", "ol", "blockquote", "hr")

# HTML tags whose content a reader never sees.
SKIP_TAGS = ("style", "script", "head", "title")

# HTML tags that never have a closing tag.
VOID_TAGS = ("br", "hr", "img", "meta", "link", "input")

# A style value that hides text from a reader.
HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none|font-size\s*:\s*0(?![.0-9]*[1-9])|visibility\s*:\s*hidden")


# ---------------------------------------------------------------------------
# Reading the file and its headers
# ---------------------------------------------------------------------------

def read_message(path):
    """Open the file and let Python's email library split headers from body."""
    with open(path, "rb") as handle:
        data = handle.read()
    return email.message_from_bytes(data, policy=email.policy.default)


def header_text(msg, name):
    """Return one header as a plain string, or None when it is missing.

    When a header appears more than once, the first copy wins. The first copy
    is the one nearest the top of the file, which for gateway headers is the
    copy the gateway itself wrote.
    """
    try:
        value = msg.get(name)
    except Exception:
        value = None
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def header_texts(msg, name):
    """Return every copy of a header as a list of strings, top copy first."""
    texts = []
    try:
        values = msg.get_all(name)
    except Exception:
        values = None
    if values is None:
        return texts
    for value in values:
        texts.append(str(value).strip())
    return texts


def split_address(text):
    """Split 'Some Name <user@host>' into ("Some Name", "user@host")."""
    if text is None:
        return "", None
    display, address = email.utils.parseaddr(text)
    if address == "":
        return display.strip(), None
    return display.strip(), address.strip()


def address_list(text):
    """Return every address in a To or Cc header as a list."""
    addresses = []
    if text is None:
        return addresses
    for display, address in email.utils.getaddresses([text]):
        if address != "":
            addresses.append(address.strip())
    return addresses


def domain_of(address):
    """Return the part of an address after the @, in lowercase, or None."""
    if address is None or "@" not in address:
        return None
    return address.rsplit("@", 1)[1].strip().lower()


def organization_domain(domain):
    """Return the last two labels of a domain: mail.pellgrave.example -> pellgrave.example.

    The last two labels are the part an organization registers. Anything in
    front of them is a host or a department inside that organization.
    """
    if domain is None:
        return None
    labels = domain.split(".")
    if len(labels) <= 2:
        return domain
    return labels[-2] + "." + labels[-1]


def parse_date(text):
    """Turn an email date such as 'Mon, 13 Apr 2026 07:41:00 -0500' into ISO 8601."""
    if text is None:
        return None
    try:
        moment = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    if moment is None:
        return None
    return moment.isoformat()


def message_ids(text):
    """Return every <id> found in a header such as References."""
    ids = []
    if text is None:
        return ids
    for found in re.findall(r"<[^<>\s]+>", text):
        ids.append(found)
    return ids


# ---------------------------------------------------------------------------
# Headers with structure inside them
# ---------------------------------------------------------------------------

def parse_auth(text):
    """Read the SPF, DKIM and DMARC results out of an Authentication-Results header."""
    auth = {"spf": None, "dkim": None, "dmarc": None, "dmarc_policy": None, "raw": None}
    if text is None:
        return auth
    # Header lines can be folded over several lines; join them with single spaces.
    flat = " ".join(text.split())
    auth["raw"] = flat
    for method in ("spf", "dkim", "dmarc"):
        found = re.search(r"\b" + method + r"=([a-z]+)", flat)
        if found:
            auth[method] = found.group(1)
    found = re.search(r"policy\.dmarc=([a-z]+)", flat)
    if found:
        auth["dmarc_policy"] = found.group(1)
    return auth


def parse_received(text):
    """Pull the hop facts out of one Received header.

    Each server that handles a message adds one Received line at the top, so
    the first Received line in the file is the last server the message met.
    """
    hop = {"from_host": None, "by_host": None, "ip": None, "timestamp": None}
    flat = " ".join(text.split())
    # The server's address sits in square brackets, for example [203.0.113.57].
    found = re.search(r"\[(?:IPv6:)?([0-9A-Fa-f.:]+)\]", flat)
    if found:
        hop["ip"] = found.group(1)
    # The time of the hop comes after the last semicolon.
    if ";" in flat:
        hop["timestamp"] = parse_date(flat.rsplit(";", 1)[1].strip())
    # Drop comments in parentheses so a product name cannot be mistaken for a host.
    no_comments = re.sub(r"\([^)]*\)", " ", flat)
    found = re.search(r"\bfrom\s+(\S+)", no_comments)
    if found:
        hop["from_host"] = found.group(1).rstrip(";,")
    found = re.search(r"\bby\s+(\S+)", no_comments)
    if found:
        hop["by_host"] = found.group(1).rstrip(";,")
    return hop


def parse_attachment_stub(text):
    """Read filename, size, sha256, action, type and reason from one removed-file header."""
    stub = {"filename": None, "size": None, "sha256": None, "action": None,
            "type": None, "reason": None}
    flat = " ".join(text.split())
    for found in re.finditer(r'([A-Za-z0-9_-]+)=("([^"]*)"|[^;]*)', flat):
        name = found.group(1).lower()
        if found.group(3) is not None:
            value = found.group(3)
        else:
            value = found.group(2).strip()
        if name in stub:
            stub[name] = value
    if stub["size"] is not None and stub["size"].isdigit():
        stub["size"] = int(stub["size"])
    return stub


def to_float(text):
    """Turn text such as '6.8' into a number, or None when it is not a number."""
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------

def find_urls(text):
    """Return every http or https link in a piece of text, in order."""
    urls = []
    if text is None:
        return urls
    for found in URL_PATTERN.findall(text):
        # HTML writes & as &amp; inside links; undo that, then drop trailing punctuation.
        url = html.unescape(found).rstrip(URL_TRAILING)
        if url != "":
            urls.append(url)
    return urls


def host_of_url(url):
    """Return the host part of a link in lowercase, without the path or a port."""
    rest = url.split("://", 1)[1]
    host = rest.split("/", 1)[0]
    host = host.split("?", 1)[0]
    host = host.split("#", 1)[0]
    # A link can hide a real-looking name before an @; the true host is after it.
    if "@" in host:
        host = host.rsplit("@", 1)[1]
    host = host.split(":", 1)[0]
    return host.lower()


def unique_in_order(items):
    """Return the list with repeats removed, keeping the first appearance."""
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


# ---------------------------------------------------------------------------
# HTML to text
# ---------------------------------------------------------------------------

class _HtmlTextCollector(HTMLParser):
    """Collects the visible text and the hidden text of an HTML part.

    This helper uses a class, which the course does not teach. You do not
    need to read it. Call html_to_text() and hidden_html_text() instead.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.visible = []
        self.hidden = []
        self.open_tags = []

    def _inside(self, want_hidden):
        for tag, is_hidden in self.open_tags:
            if want_hidden and is_hidden:
                return True
            if not want_hidden and tag in SKIP_TAGS:
                return True
        return False

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK_TAGS:
            self.visible.append("\n")
        if tag in VOID_TAGS:
            return
        is_hidden = False
        for name, value in attrs:
            if name == "style" and value is not None and HIDDEN_STYLE.search(value.lower()):
                is_hidden = True
            if name == "hidden":
                is_hidden = True
        self.open_tags.append((tag, is_hidden))

    def handle_endtag(self, tag):
        if tag in BLOCK_TAGS:
            self.visible.append("\n")
        index = len(self.open_tags) - 1
        while index >= 0:
            if self.open_tags[index][0] == tag:
                del self.open_tags[index:]
                break
            index = index - 1

    def handle_data(self, data):
        if self._inside(False):
            return
        # Inside HTML text a line break is just a space; only tags start new lines.
        data = re.sub(r"[ \t\r\n]+", " ", data)
        if self._inside(True):
            self.hidden.append(data)
        else:
            self.visible.append(data)

    def handle_comment(self, data):
        self.hidden.append(data)


def _tidy_text(pieces, separator):
    """Join text pieces and clean up the spacing."""
    text = separator.join(pieces)
    lines = []
    for line in text.split("\n"):
        lines.append(" ".join(line.split()))
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_text(html_text):
    """Return the text a reader would see, with tags removed."""
    if html_text is None:
        return ""
    collector = _HtmlTextCollector()
    collector.feed(html_text)
    collector.close()
    return _tidy_text(collector.visible, "")


def hidden_html_text(html_text):
    """Return text the HTML keeps out of sight: comments and hidden elements."""
    if html_text is None:
        return ""
    collector = _HtmlTextCollector()
    collector.feed(html_text)
    collector.close()
    return _tidy_text(collector.hidden, "\n")


# ---------------------------------------------------------------------------
# Body parts
# ---------------------------------------------------------------------------

def part_text(part):
    """Decode one MIME part to a string, whatever its transfer encoding.

    MIME is the rule set that lets one email carry several parts, such as a
    plain-text version and an HTML version of the same message. A transfer
    encoding such as quoted-printable is how non-ASCII text is written using
    only plain characters; the email library undoes it here.
    """
    try:
        return part.get_content()
    except Exception:
        payload = part.get_payload(decode=True)
        if payload is None:
            return ""
        return payload.decode("utf-8", errors="replace")


def body_parts(msg):
    """Find the first text/plain part and the first text/html part."""
    plain = None
    html_part = None
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        content_type = part.get_content_type()
        if content_type == "text/plain" and plain is None:
            plain = part_text(part)
        elif content_type == "text/html" and html_part is None:
            html_part = part_text(part)
    return plain, html_part


# ---------------------------------------------------------------------------
# Display name versus domain
# ---------------------------------------------------------------------------

def check_display_name_mismatch(from_display, from_domain, reply_to_domain, known_names=None):
    """Decide whether the name on the message disagrees with its domain.

    Three rules. Any one of them returns True.

    1. Reply-To points at a different organization than From does. Replies
       would go somewhere other than the place the message claims to be from.
    2. The display name itself contains an address or a domain that belongs
       to a different organization than from_domain. Example: a display name
       of "helpdesk@pellgrave.example" over a webmail address.
    3. A name from known_names appears in the display name, and that name
       belongs to a different organization. known_names is an optional
       dictionary of {"Name": "domain.example"}, for example the company's
       employees and its vendors. Without it, rule 3 is skipped, because a
       file alone cannot say which organization a name belongs to.
    """
    if from_domain is None:
        return False
    from_org = organization_domain(from_domain)
    if reply_to_domain is not None and organization_domain(reply_to_domain) != from_org:
        return True
    display = (from_display or "").lower()
    for token in re.findall(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", display):
        last_label = token.split(".")[-1]
        if not re.search(r"[a-z]", last_label):
            continue  # a version number such as 7.4, not a domain
        if organization_domain(token) != from_org:
            return True
    if known_names:
        for name in known_names:
            real_domain = known_names[name].lower()
            if name.lower() in display and organization_domain(real_domain) != from_org:
                return True
    return False


# ---------------------------------------------------------------------------
# The main function
# ---------------------------------------------------------------------------

def parse_eml(path, known_names=None):
    """Read one .eml file and return a dictionary of facts about it.

    path is the file to read. known_names is optional; see
    check_display_name_mismatch for what it does.
    """
    msg = read_message(path)
    parsed = {}

    # Who sent it, and where replies go.
    from_display, from_address = split_address(header_text(msg, "From"))
    from_domain = domain_of(from_address)
    reply_display, reply_to = split_address(header_text(msg, "Reply-To"))
    return_display, return_path = split_address(header_text(msg, "Return-Path"))

    parsed["subject"] = header_text(msg, "Subject")
    parsed["from_display"] = from_display
    parsed["from_address"] = from_address
    parsed["from_domain"] = from_domain
    parsed["reply_to"] = reply_to
    parsed["return_path"] = return_path
    parsed["to"] = address_list(header_text(msg, "To"))
    parsed["cc"] = address_list(header_text(msg, "Cc"))
    parsed["date"] = parse_date(header_text(msg, "Date"))
    parsed["message_id"] = header_text(msg, "Message-ID")
    parsed["in_reply_to"] = header_text(msg, "In-Reply-To")
    parsed["references"] = message_ids(header_text(msg, "References"))

    # The gateway's sender checks.
    parsed["auth"] = parse_auth(header_text(msg, "Authentication-Results"))

    # The path the message took, one hop per Received header, top first.
    received = []
    for text in header_texts(msg, "Received"):
        received.append(parse_received(text))
    parsed["received"] = received

    originating = header_text(msg, "X-Originating-IP")
    if originating is not None:
        originating = originating.strip("[]")
    parsed["x_originating_ip"] = originating

    # Other facts the gateway stamped on the message.
    external_value = header_text(msg, "X-Sentrywick-External")
    reported_display, reported_by = split_address(header_text(msg, "X-Sentrywick-Reported-By"))
    parsed["gateway"] = {
        "external": external_value is not None and external_value.lower() == "yes",
        "scan_result": header_text(msg, "X-Sentrywick-Scan-Result"),
        "spam_score": to_float(header_text(msg, "X-Sentrywick-Spam-Score")),
        "reported_by": reported_by,
        "message_uid": header_text(msg, "X-Sentrywick-Message-UID"),
    }

    # The body, in both forms.
    plain, html_source = body_parts(msg)
    html_text = html_to_text(html_source)
    if plain is not None:
        parsed["body_text"] = plain
    else:
        parsed["body_text"] = html_text
    parsed["body_html"] = html_source
    parsed["body_html_text"] = html_text
    parsed["hidden_html_text"] = hidden_html_text(html_source)

    # Links, from the plain part first and then the HTML part.
    urls = find_urls(plain) + find_urls(html_source)
    hosts = []
    for url in urls:
        hosts.append(host_of_url(url))
    parsed["urls"] = urls
    parsed["url_hosts"] = unique_in_order(hosts)

    # Files the gateway removed. Only the facts about each file remain.
    attachments = []
    for text in header_texts(msg, REMOVED_ATTACHMENT_HEADER):
        attachments.append(parse_attachment_stub(text))
    parsed["attachments"] = attachments

    parsed["display_name_mismatch"] = check_display_name_mismatch(
        from_display, from_domain, domain_of(reply_to), known_names)

    # Every header, in the order the file has them.
    raw_headers = []
    try:
        for name, value in msg.items():
            raw_headers.append([name, " ".join(str(value).split())])
    except Exception:
        for name, value in msg.raw_items():
            raw_headers.append([name, " ".join(str(value).split())])
    parsed["raw_headers"] = raw_headers

    return parsed


# ---------------------------------------------------------------------------
# Command line use
# ---------------------------------------------------------------------------

def describe(parsed):
    """Return a readable summary of one parsed email."""
    lines = []
    lines.append("Subject:       " + str(parsed["subject"]))
    lines.append("From:          " + parsed["from_display"] + " <" + str(parsed["from_address"]) + ">")
    lines.append("From domain:   " + str(parsed["from_domain"]))
    lines.append("Reply-To:      " + str(parsed["reply_to"]))
    lines.append("Return-Path:   " + str(parsed["return_path"]))
    lines.append("To:            " + ", ".join(parsed["to"]))
    if parsed["cc"]:
        lines.append("Cc:            " + ", ".join(parsed["cc"]))
    lines.append("Date:          " + str(parsed["date"]))
    lines.append("Message-ID:    " + str(parsed["message_id"]))
    if parsed["in_reply_to"] is not None:
        lines.append("In-Reply-To:   " + parsed["in_reply_to"])
    auth = parsed["auth"]
    lines.append("Auth:          spf=" + str(auth["spf"]) + " dkim=" + str(auth["dkim"])
                 + " dmarc=" + str(auth["dmarc"]) + " policy=" + str(auth["dmarc_policy"]))
    gateway = parsed["gateway"]
    lines.append("Gateway:       external=" + str(gateway["external"])
                 + " scan=" + str(gateway["scan_result"])
                 + " spam_score=" + str(gateway["spam_score"])
                 + " reported_by=" + str(gateway["reported_by"]))
    if parsed["x_originating_ip"] is not None:
        lines.append("Originating IP: " + parsed["x_originating_ip"])
    lines.append("Received chain (most recent first):")
    for hop in parsed["received"]:
        lines.append("    from " + str(hop["from_host"]) + " by " + str(hop["by_host"])
                     + " [" + str(hop["ip"]) + "] at " + str(hop["timestamp"]))
    lines.append("Links:")
    for url in parsed["urls"]:
        lines.append("    " + url)
    lines.append("Link hosts:    " + ", ".join(parsed["url_hosts"]))
    lines.append("Removed files:")
    for stub in parsed["attachments"]:
        lines.append("    " + str(stub["filename"]) + " (" + str(stub["size"]) + " bytes, "
                     + str(stub["action"]) + ", " + str(stub["reason"]) + ") sha256="
                     + str(stub["sha256"]))
    lines.append("Display name mismatch: " + str(parsed["display_name_mismatch"]))
    if parsed["hidden_html_text"] != "":
        lines.append("Hidden HTML text: " + parsed["hidden_html_text"][:200])
    lines.append("Body (first 400 characters):")
    lines.append(parsed["body_text"][:400])
    return "\n".join(lines)


if __name__ == "__main__":
    paths = sys.argv[1:]
    if not paths:
        print("Usage: python3 parse_eml.py FILE.eml [FILE.eml ...]")
        sys.exit(0)
    for path in paths:
        print("=" * 72)
        print(path)
        print("=" * 72)
        try:
            print(describe(parse_eml(path)))
        except OSError as error:
            print("Could not read the file: " + str(error))
        print()
