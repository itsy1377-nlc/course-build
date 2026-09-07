#!/usr/bin/env python3
"""
validate_corpus.py: check every .eml file in the corpus against the header
specification (docs/email-header-realism.md, section 10), the conventions in
docs/phase0-corpus-design.md, the ground truth, and the data files.

Run it from anywhere:

    python3 builder/corpus/tools/validate_corpus.py
    python3 builder/corpus/tools/validate_corpus.py --emails some/folder --no-dns

Options:
    --corpus DIR         the corpus folder; default is the parent of this tools folder
    --emails DIR         where the .eml files are; default <corpus>/emails, searched
                         recursively; files named *.eml.txt are accepted too
    --ground-truth FILE  one ground truth file; default is <corpus>/ground_truth.json
                         plus every <corpus>/ground_truth_*.json that exists
    --tld-list FILE      use this copy of the IANA top-level-domain list instead of
                         the newest snapshot in <corpus>/data/tlds (one name per
                         line, comment lines start with #)
    --no-dns             skip the name-resolution check
    --verbose            also print one PASS line per file with no failures

Output: one line per problem, "FAIL <file> [check] message" for a rule the file
breaks and "WARN <file> [check] message" for something a person should look at,
then one summary line. Exit status is 1 when any FAIL was printed, else 0.
A folder with no .eml files is not an error; the script says so and exits 0.

Check names: "s10.N" is item N of the specification's section 10 checklist.
"design.*" are conventions from the corpus design. "data.*" cross-check the
data files. "record.*" compare the file with its ground truth record, or with
its manifest record when no ground truth exists yet. "gt.*" check the ground
truth files themselves. "corpus.*" span all files, including
"corpus.manifest", which holds spec/phase0-sample-manifest.json to every
rendered file and every recorded byte count and digest to the file on disk.

The safety net in check 9 needs the IANA list of delegated top-level domains.
It is read from the newest dated snapshot in <corpus>/data/tlds, a file named
iana-tlds-YYYY-MM-DD.txt recorded in that folder's PROVENANCE.txt. The first
line of the output names the snapshot in use. Nothing is fetched at validation
time: when no snapshot is on disk the run fails and says so instead of quietly
checking less.

Only the Python standard library is used. Nothing is fetched from the network
except the optional name-resolution check, which only asks whether the corpus
domains resolve.
"""

import argparse
import datetime
import email
import email.policy
import email.utils
import glob
import hashlib
import ipaddress
import json
import os
import re
import shutil
import socket
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_eml  # noqa: E402  (the student helper; the validator reuses its parsing)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_V4 = [ipaddress.ip_network(block) for block in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
ALLOWED_V6 = ipaddress.ip_network("2001:db8::/32")

SPF_RESULTS = ("none", "neutral", "pass", "policy", "fail", "softfail", "temperror", "permerror")
DKIM_RESULTS = ("none", "pass", "fail", "policy", "neutral", "temperror", "permerror")
DMARC_RESULTS = ("pass", "fail", "none", "temperror", "permerror")
DMARC_POLICIES = ("none", "quarantine", "reject")

# Section 10 item 8, exactly as written in the specification.
AUTH_RESULTS_RE = re.compile(
    r"^mx\.[a-z0-9.-]+\.example;(\s*(spf|dkim|dmarc)=(none|pass|fail|softfail|neutral|policy|"
    r"temperror|permerror)(\s+[a-z]+\.[a-z]+=\S+)*;?)+$")
MESSAGE_ID_RE = re.compile(r"^<[A-Za-z0-9._+-]+@[a-z0-9.-]+\.example>$")
MESSAGE_ID_CONVENTION_RE = re.compile(r"^<(\d{14})\.[0-9a-f]{12}@([a-z0-9.-]+\.example)>$")

# Section 2 grammar for the removed-attachment header, on a whitespace-collapsed value.
TOKEN = r"[A-Za-z0-9!#$%&'*+.^_`|~-]+"
REMOVED_RE = re.compile(
    r'^filename="([^"\\]*(?:\\.[^"\\]*)*)"; size=(\d+); sha256=([0-9a-f]{64}); '
    r'action=(stripped|quarantined)(?:; type=(' + TOKEN + '/' + TOKEN + r'))?'
    r'(?:; reason=(' + TOKEN + r'))?$')
REMOVED_HEADER = "X-Sentrywick-Removed-Attachment"

SCAN_RESULTS = ("clean", "suspect", "released-from-quarantine")
GATEWAY_PRODUCT = "Sentrywick Gateway"
BANNER = "[External message. " + GATEWAY_PRODUCT + "]"
# Section 2: the one fixed paragraph the gateway stamps into every external HTML part.
HTML_BANNER_SNIPPET = ('<p style="margin:0;padding:6px 12px;background-color:#fff4d6;font-size:12px;'
                       'color:#5a4a00;">' + BANNER + '</p>')
FORBIDDEN_HTML = ("<script", "<iframe", "<form", "<img", "<link", "<meta", "<object",
                  "<embed", "javascript:")

# Authentication-Results property names that look like domains to the safety net.
PROPERTY_TOKENS = {"smtp.mailfrom", "smtp.helo", "smtp.auth", "header.from", "header.d",
                   "header.s", "header.i", "header.b", "header.a", "policy.dmarc",
                   "body.smime-part", "body.smime-identifier"}

FILE_EXTENSIONS = {"pdf", "exe", "doc", "docx", "docm", "xls", "xlsx", "xlsm", "ppt",
                   "pptx", "zip", "rar", "iso", "img", "txt", "csv", "json", "xml",
                   "html", "htm", "png", "jpg", "jpeg", "gif", "rtf", "msg", "eml",
                   "js", "vbs", "bat", "cmd", "scr", "lnk", "dll", "ps", "py", "sh",
                   "ics", "vcf", "log", "md"}

# The vendored IANA snapshot in data/tlds is the list the safety net uses. The
# set below is a last resort, reached only after the validator has already failed
# the run for having no snapshot on disk. It holds the legacy and sponsored
# top-level domains plus generic-word ones that are easy to type by accident.
# Brand and place names are left out, which is one reason a run on this set is a
# failing run. Two-letter suffixes are treated as country codes by rule, so they
# are not listed here.
FALLBACK_TLDS = {
    "com", "net", "org", "edu", "gov", "mil", "int", "arpa", "info", "biz", "name",
    "pro", "aero", "coop", "museum", "jobs", "mobi", "travel", "cat", "tel", "asia",
    "post", "app", "dev", "cloud", "online", "site", "xyz", "top", "shop", "store",
    "tech", "club", "live", "news", "email", "link", "click", "download", "zip",
    "mov", "page", "blog", "support", "help", "bank", "finance", "services",
    "solutions", "systems", "network", "digital", "agency", "company", "business",
    "center", "global", "group", "media", "today", "world", "one", "plus", "best",
    "buzz", "fun", "icu", "life", "work", "works", "zone", "space", "website", "host",
    "hosting", "tools", "software", "chat", "exchange", "university", "school",
    "education", "academy", "training", "guru", "ninja", "expert", "review",
    "reviews", "team", "win", "vip", "art", "design", "photo", "photos", "video",
    "pics", "wiki", "law", "legal", "money", "cash", "pay", "card", "loans", "credit",
    "insure", "security", "care", "health", "doctor", "dental", "clinic", "fit",
    "fitness", "run", "bike", "golf", "tennis", "football", "soccer", "basketball",
    "sport", "games", "game", "play", "toys", "family", "baby", "mom", "dad", "love",
    "wedding", "party", "events", "tickets", "flights", "hotel", "vacations", "tours",
    "city", "town", "place", "land", "earth", "eco", "green", "energy", "solar",
    "farm", "garden", "house", "apartments", "rent", "lease", "sale", "deals",
    "discount", "coupons", "cheap", "free", "gratis", "promo", "market", "markets",
    "trade", "auction", "bid", "express", "delivery", "shipping", "cargo", "auto",
    "car", "cars", "moto", "racing", "taxi", "limo", "bus", "train", "boats", "yachts",
    "fish", "fishing", "camp", "ski", "surf", "lol", "wtf", "sucks", "fail", "rocks",
    "cool", "hot", "new", "now", "fyi", "ceo", "cfo", "cpa", "mba", "inc", "llc", "ltd",
    "gmbh", "sarl", "srl", "ltda", "ooo", "onl", "foundation", "charity", "church",
    "bible", "faith", "bio", "organic", "vet", "pet", "dog", "cafe", "bar", "pub",
    "restaurant", "pizza", "kitchen", "recipes", "wine", "beer", "vodka", "coffee",
    "menu", "food", "fashion", "style", "shoes", "jewelry", "watch", "glass",
    "furniture", "lighting", "tires", "parts", "repair", "cleaning", "plumbing",
    "construction", "contractors", "engineering", "industries", "supply", "supplies",
    "equipment", "machines", "management", "consulting", "marketing", "accountant",
    "accountants", "tax", "capital", "fund", "investments", "ventures", "holdings",
    "partners", "estate", "realty", "properties", "mortgage", "broker", "insurance",
    "claims", "report", "audio", "radio", "film", "movie", "music", "band", "show",
    "theater", "studio", "gallery", "camera", "pictures", "graphics", "press",
    "author", "book", "webcam", "phone", "mobile", "computer", "data", "domains",
    "science", "technology", "engineer", "moda", "vin", "black", "blue", "red",
    "pink", "gold", "silver", "diamonds", "lat", "wow", "wed", "how", "kiwi", "rest",
    "casino", "bet", "poker", "bingo", "lotto", "gives", "gift", "gifts", "christmas",
    "holiday", "cruises", "voyage", "map", "navy", "army", "airforce", "rip",
    "memorial", "condos", "villas", "immo", "immobilien", "haus", "casa", "hospital",
    "surgery", "pharmacy", "physio", "dentist", "diet", "beauty", "hair", "salon",
    "skin", "spa", "yoga", "tattoo", "boutique", "clothing", "dress", "luxury",
    "lifestyle", "living", "rentals", "homes", "storage", "moving", "limited",
    "international", "associates", "enterprises", "coach", "college", "courses",
    "degree", "institute", "phd", "study", "scholarships", "kids",
}


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

class Report:
    """Collects failures and warnings and prints each one as it arrives."""

    def __init__(self):
        self.failures = []
        self.warnings = []
        self.failed_files = set()

    def fail(self, where, check, message):
        line = "FAIL " + where + " [" + check + "] " + message
        self.failures.append(line)
        self.failed_files.add(where)
        print(line)

    def warn(self, where, check, message):
        line = "WARN " + where + " [" + check + "] " + message
        self.warnings.append(line)
        print(line)


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def organization_domain(domain):
    return parse_eml.organization_domain(domain)


class Data:
    """Everything the validator knows from spec/ and data/."""

    def __init__(self, corpus_dir, report):
        self.corpus_dir = corpus_dir
        loaded = {}
        for rel in ("spec/corpus-spec.json", "spec/enums.json", "spec/categories.json",
                    "spec/ground_truth.schema.json", "data/recipients.json",
                    "data/sender_reputation.json", "data/url_allowlist.json",
                    "data/url_blocklist.json", "data/url_unlisted.json",
                    "data/known_good_domains.json", "data/attachments.json",
                    "data/known_threads.json", "data/domain_policy.json"):
            try:
                loaded[rel] = load_json(os.path.join(corpus_dir, rel))
            except (OSError, ValueError) as error:
                report.fail(rel, "data.load", "could not read: " + str(error))
                loaded[rel] = None
            if loaded[rel] is None:
                report.warn(rel, "data.load", "missing; checks that need it are skipped")

        self.spec = loaded["spec/corpus-spec.json"]
        self.enums = loaded["spec/enums.json"]
        self.categories = loaded["spec/categories.json"]
        self.schema = loaded["spec/ground_truth.schema.json"]
        recipients = loaded["data/recipients.json"]
        reputation = loaded["data/sender_reputation.json"]
        allow = loaded["data/url_allowlist.json"]
        block = loaded["data/url_blocklist.json"]
        unlisted = loaded["data/url_unlisted.json"]
        known_good = loaded["data/known_good_domains.json"]
        attachments = loaded["data/attachments.json"]
        threads = loaded["data/known_threads.json"]
        policy = loaded["data/domain_policy.json"]

        self.org = None
        if self.spec:
            self.org = self.spec.get("organization")
        if self.org is None and known_good:
            self.org = known_good.get("organization")
        if self.org is None:
            report.warn("(corpus)", "data.load", "organization unknown; assuming pellgrave.example")
            self.org = "pellgrave.example"
        self.gateway_host = "mx." + self.org
        self.submit_host = "mail." + self.org

        self.spec_records = {}
        self.window = None
        if self.spec:
            for record in self.spec.get("emails", []):
                self.spec_records[record["id"]] = record
            window = self.spec.get("corpus_window")
            if window:
                self.window = (datetime.date.fromisoformat(window["start"]),
                               datetime.date.fromisoformat(window["end"]))

        self.cat_verdict = {}
        if self.categories:
            for cat in self.categories.get("categories", []):
                self.cat_verdict[cat["id"]] = cat["verdict"]

        self.have_recipients = recipients is not None
        self.recipients = {}
        if recipients:
            for rec in recipients.get("recipients", []):
                self.recipients[rec["address"].lower()] = rec

        self.have_reputation = reputation is not None
        self.rep_domains = {}
        self.rep_addresses = {}
        self.decoy_domains = set()
        if reputation:
            for rec in reputation.get("domains", []):
                self.rep_domains[rec["domain"].lower()] = rec
                if "(decoy)" in (rec.get("notes") or ""):
                    self.decoy_domains.add(rec["domain"].lower())
            for rec in reputation.get("addresses", []):
                self.rep_addresses[rec["address"].lower()] = rec

        self.have_url_lists = allow is not None and block is not None
        self.allow_hosts = set()
        self.block_hosts = set()
        self.decoy_hosts = set()
        for source, target in ((allow, self.allow_hosts), (block, self.block_hosts)):
            if source:
                for entry in source.get("hosts", []):
                    target.add(entry["host"].lower())
                    if "(decoy)" in (entry.get("reason") or ""):
                        self.decoy_hosts.add(entry["host"].lower())
        self.have_unlisted = unlisted is not None
        self.unlisted_hosts = set()
        if unlisted:
            for host in unlisted.get("hosts", []):
                self.unlisted_hosts.add(host.lower())
        self.internal_hosts = set()
        if known_good:
            for host in known_good.get("internal_hosts", []):
                self.internal_hosts.add(host.lower())

        self.have_attachments = attachments is not None
        self.attachments_by_id = {}
        if attachments:
            for entry in attachments.get("attachments", []):
                self.attachments_by_id.setdefault(entry["email_id"], []).append(entry)

        self.thread_ids = set()
        if threads:
            for entry in threads.get("threads", []):
                self.thread_ids.add(entry["message_id"])

        self.have_policy = policy is not None
        self.policy = {}
        if policy:
            for entry in policy.get("domains", []):
                self.policy[entry["domain"].lower()] = entry

        self.attachment_reasons = None
        if self.enums and "attachment_reason" in self.enums:
            self.attachment_reasons = set(self.enums["attachment_reason"])

    def rep_lookup(self, address):
        """Exact address, then exact domain, then organizational domain."""
        if address is None:
            return None
        address = address.lower()
        if address in self.rep_addresses:
            return self.rep_addresses[address]
        domain = parse_eml.domain_of(address)
        if domain is None:
            return None
        if domain in self.rep_domains:
            return self.rep_domains[domain]
        org = organization_domain(domain)
        if org in self.rep_domains:
            return self.rep_domains[org]
        return None

    def policy_lookup(self, domain):
        if domain is None:
            return None
        domain = domain.lower()
        if domain in self.policy:
            return self.policy[domain]
        org = organization_domain(domain)
        if org in self.policy:
            return self.policy[org]
        return None

    def url_status(self, host):
        """The same rule as check_spec.py and the week 4 check_urls tool."""
        host = host.lower()
        if host in self.block_hosts:
            return "blocklisted"
        if host in self.allow_hosts:
            return "allowlisted"
        if host in self.internal_hosts or host.endswith("." + self.org):
            return "internal"
        return "unlisted"


# The vendored snapshots of the IANA root zone list. The date in the file name is
# the date in the file's own version line, so sorting the names sorts by version.
TLD_DIR = os.path.join("data", "tlds")
TLD_SNAPSHOT_RE = re.compile(r"^iana-tlds-(\d{4})-(\d{2})-(\d{2})\.txt$")
TLD_SOURCE_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"


def find_tld_snapshot(corpus_dir):
    """The newest vendored IANA snapshot by file name, or None. Nothing is fetched."""
    folder = os.path.join(corpus_dir, TLD_DIR)
    names = []
    try:
        for name in os.listdir(folder):
            if TLD_SNAPSHOT_RE.match(name):
                names.append(name)
    except OSError:
        return None
    if not names:
        return None
    return os.path.join(folder, sorted(names)[-1])


class TldList:
    """Answers whether a suffix is a delegated top-level domain.

    The names come from a dated snapshot of the IANA root zone list kept in
    <corpus>/data/tlds. The snapshot is read from disk and never fetched, so the
    validator gives the same answer on a machine with no network. With no
    snapshot the run fails and says what to do; it falls back to the small
    built-in set only so the rest of the run still reports, and the failure keeps
    that weaker pass from reading as a clean one.
    """

    def __init__(self, corpus_dir, explicit, report):
        self.strict = False
        self.names = set(FALLBACK_TLDS)
        self.source = None
        self.version = None
        self.count = len(self.names)

        path = explicit
        if not path:
            path = find_tld_snapshot(corpus_dir)
        if not path:
            report.fail("(corpus)", "tld.snapshot",
                        "no top-level domain snapshot in " + os.path.join(corpus_dir, TLD_DIR)
                        + "; the section 10 item 9 safety net needs one. Save "
                        + TLD_SOURCE_URL + " as " + os.path.join(TLD_DIR, "iana-tlds-YYYY-MM-DD.txt")
                        + ", taking the date from the file's own version line, and record the"
                        " source, date, version line and sha256 in " + os.path.join(TLD_DIR, "PROVENANCE.txt")
                        + ". This run falls back to a small built-in set, so the check is weaker"
                        " than it should be and the run is failed on purpose.")
            return

        names = set()
        version = None
        try:
            with open(path, encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line.startswith("#"):
                        if version is None and "version" in line.lower():
                            version = line.lstrip("#").strip()
                        continue
                    if line:
                        names.add(line.lower())
        except OSError as error:
            report.fail("(corpus)", "tld.snapshot",
                        "could not read the top-level domain snapshot " + path + ": " + str(error)
                        + "; this run falls back to a small built-in set, so the section 10 item 9"
                        " safety net is weaker than it should be and the run is failed on purpose.")
            return
        if not names:
            report.fail("(corpus)", "tld.snapshot",
                        "the top-level domain snapshot " + path + " holds no names; replace it with a"
                        " copy of " + TLD_SOURCE_URL + ". This run falls back to a small built-in set,"
                        " so the section 10 item 9 safety net is weaker than it should be and the run"
                        " is failed on purpose.")
            return

        self.names = names
        self.strict = True
        self.source = path
        self.version = version
        self.count = len(names)

        found = TLD_SNAPSHOT_RE.match(os.path.basename(path))
        if found and version:
            stamp = re.search(r"\b(\d{8})", version)
            if stamp and stamp.group(1) != found.group(1) + found.group(2) + found.group(3):
                report.warn("(corpus)", "tld.snapshot",
                            os.path.basename(path) + " is named for a different day than its version"
                            " line says (" + version + "); name a snapshot for the date in its own"
                            " version line so the newest file by name is the newest list")

    def describe(self, corpus_dir):
        """One line naming the snapshot in use, for the top of the output."""
        if not self.strict:
            return ("top-level domain list: NO SNAPSHOT; falling back to " + str(self.count)
                    + " built-in suffixes plus every two-letter suffix (see the failure above)")
        where = nice_path(self.source, corpus_dir)
        version = self.version or "no version line"
        return ("top-level domain list: " + where + " (" + version + "), "
                + str(self.count) + " names")

    def is_delegated(self, label):
        if label in self.names:
            return True
        if not self.strict and len(label) == 2:
            return True
        return False


# ---------------------------------------------------------------------------
# Ground truth files
# ---------------------------------------------------------------------------

def load_ground_truth(corpus_dir, explicit, report):
    """Return ({id: record}, [paths]). Accepts a list or an object holding a list."""
    if explicit:
        paths = [explicit]
    else:
        paths = sorted(glob.glob(os.path.join(corpus_dir, "ground_truth.json"))
                       + glob.glob(os.path.join(corpus_dir, "ground_truth_*.json")))
    records = {}
    for path in paths:
        rel = nice_path(path, corpus_dir)
        try:
            payload = load_json(path)
        except (OSError, ValueError) as error:
            report.fail(rel, "gt.load", "could not read: " + str(error))
            continue
        if payload is None:
            report.fail(rel, "gt.load", "file not found")
            continue
        if isinstance(payload, dict):
            for key in ("records", "emails", "ground_truth"):
                if isinstance(payload.get(key), list):
                    payload = payload[key]
                    break
        if not isinstance(payload, list):
            report.fail(rel, "gt.shape", "expected a list of records or an object holding one")
            continue
        for index, record in enumerate(payload):
            if not isinstance(record, dict) or "id" not in record:
                report.fail(rel, "gt.shape", "record " + str(index) + " has no id")
                continue
            if record["id"] in records:
                report.fail(rel, "gt.duplicate", "id " + record["id"] + " appears more than once")
                continue
            record["_source"] = rel
            records[record["id"]] = record
    return records, paths


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def to_aware(moment):
    """Give a naive datetime a UTC zone so comparisons never fail."""
    if moment is None:
        return None
    if moment.tzinfo is None:
        return moment.replace(tzinfo=datetime.timezone.utc)
    return moment


def parse_iso(text):
    if text is None:
        return None
    try:
        return to_aware(datetime.datetime.fromisoformat(text))
    except ValueError:
        return None


def domain_part(value):
    """'user@host' -> 'host', '@host' -> 'host', 'host' -> 'host', all lowercase."""
    if value is None:
        return None
    value = value.strip().strip('"<>')
    if "@" in value:
        value = value.rsplit("@", 1)[1]
    return value.lower()


def hget(ctx, name):
    """First flat value of a header, or None."""
    name = name.lower()
    for header_name, value in ctx["headers"]:
        if header_name.lower() == name:
            return value
    return None


def hall(ctx, name):
    name = name.lower()
    values = []
    for header_name, value in ctx["headers"]:
        if header_name.lower() == name:
            values.append(value)
    return values


def hindex(ctx, name, start=0):
    """Index of the first header with this name at or after start, or None."""
    name = name.lower()
    for index in range(start, len(ctx["headers"])):
        if ctx["headers"][index][0].lower() == name:
            return index
    return None


def hcount(ctx, name):
    return len(hall(ctx, name))


def first_line(text):
    if text is None:
        return ""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def decoded_text(ctx):
    """All header values plus both decoded body parts, for text-wide scans."""
    pieces = []
    for name, value in ctx["headers"]:
        pieces.append(value)
    if ctx.get("plain"):
        pieces.append(ctx["plain"])
    if ctx.get("html"):
        pieces.append(ctx["html"])
    return "\n".join(pieces)


def parse_auth_results(flat):
    """Return (authserv_id, {method: (result, {property: value})})."""
    clauses = flat.split(";")
    head = clauses[0].strip().split()
    authserv = head[0].lower() if head else ""
    results = {}
    for clause in clauses[1:]:
        tokens = clause.split()
        if not tokens or "=" not in tokens[0]:
            continue
        method, result = tokens[0].split("=", 1)
        props = {}
        for token in tokens[1:]:
            if "=" in token:
                key, value = token.split("=", 1)
                props[key.lower()] = value
        results[method.lower()] = (result.lower(), props)
    return authserv, results


def received_spf_pairs(flat):
    """Return (result, {key: value}) from a Received-SPF value."""
    tokens = flat.split()
    result = tokens[0].lower() if tokens else ""
    without_comment = re.sub(r"\([^)]*\)", " ", flat)
    pairs = {}
    for found in re.finditer(r'([A-Za-z][A-Za-z0-9-]*)=("[^"]*"|[^;\s]+)', without_comment):
        pairs[found.group(1).lower()] = found.group(2).strip('"')
    return result, pairs


def dkim_tags(flat):
    tags = {}
    for piece in flat.split(";"):
        if "=" not in piece:
            continue
        key, value = piece.split("=", 1)
        tags[key.strip().lower()] = re.sub(r"\s+", "", value)
    return tags


def received_id(text):
    without_comment = re.sub(r"\([^)]*\)", " ", text)
    found = re.search(r"\bid\s+(\S+?)(?:;|$|\s)", without_comment)
    if found:
        return found.group(1)
    return None


def record_indicators(record):
    """[(code, value)] from either the ground truth shape or the manifest shape."""
    out = []
    for item in record.get("indicators", []) or []:
        if isinstance(item, dict):
            out.append((item.get("code"), item.get("value")))
        else:
            parts = str(item).split(":", 2)
            code = ":".join(parts[:2])
            value = parts[2] if len(parts) > 2 else None
            out.append((code, value))
    return out


# ---------------------------------------------------------------------------
# Building the per-file context
# ---------------------------------------------------------------------------

def find_eml_files(emails_dir):
    files = []
    if not os.path.isdir(emails_dir):
        return files
    for root, dirs, names in os.walk(emails_dir):
        dirs.sort()
        for name in sorted(names):
            if name.endswith(".eml") or name.endswith(".eml.txt"):
                files.append(os.path.join(root, name))
    return files


def file_stem(path):
    name = os.path.basename(path)
    if name.endswith(".eml.txt"):
        return name[:-8]
    return name[:-4]


def build_context(path, corpus_dir, report):
    ctx = {"path": path, "rel": nice_path(path, corpus_dir),
           "stem": file_stem(path), "msg": None, "parsed": None, "headers": [],
           "plain": None, "html": None, "domains": set()}
    with open(path, "rb") as handle:
        ctx["raw"] = handle.read()
    try:
        msg = email.message_from_bytes(ctx["raw"], policy=email.policy.default)
    except Exception as error:
        report.fail(ctx["rel"], "s10.2", "message_from_bytes raised " + type(error).__name__ + ": " + str(error))
        return ctx
    ctx["msg"] = msg
    try:
        ctx["parsed"] = parse_eml.parse_eml(path)
    except Exception as error:
        report.fail(ctx["rel"], "parse_eml", "parse_eml raised " + type(error).__name__ + ": " + str(error))
        return ctx
    headers = []
    try:
        for name, value in msg.items():
            headers.append((name, " ".join(str(value).split())))
    except Exception:
        headers = []
        for name, value in msg.raw_items():
            headers.append((name, " ".join(str(value).split())))
    ctx["headers"] = headers
    ctx["plain"], ctx["html"] = parse_eml.body_parts(msg)
    ctx["html_text"] = parse_eml.html_to_text(ctx["html"])
    return ctx


# ---------------------------------------------------------------------------
# Per-file checks: the section 10 checklist
# ---------------------------------------------------------------------------

def check_bytes_and_lines(ctx, report):
    rel = ctx["rel"]
    raw = ctx["raw"]
    if not raw.endswith(b"\r\n"):
        report.fail(rel, "s10.1", "file does not end with CRLF")
    bare_lf = len(re.findall(rb"(?<!\r)\n", raw))
    bare_cr = len(re.findall(rb"\r(?!\n)", raw))
    if bare_lf:
        report.fail(rel, "s10.1", str(bare_lf) + " bare LF line ending(s); every line must end with CRLF")
    if bare_cr:
        report.fail(rel, "s10.1", str(bare_cr) + " bare CR byte(s)")
    lines = raw.split(b"\r\n")
    over_998 = 0
    over_78 = 0
    for line in lines:
        if len(line) > 998:
            over_998 += 1
        elif len(line) > 78:
            over_78 += 1
    if over_998:
        report.fail(rel, "s10.1", str(over_998) + " line(s) over 998 bytes")
    if over_78:
        report.warn(rel, "s10.1", str(over_78) + " line(s) over 78 characters; the specification says lines should fold at 78")
    bad = set()
    for byte in raw:
        if not (0x20 <= byte <= 0x7E or byte in (0x09, 0x0A, 0x0D)):
            bad.add(byte)
    if bad:
        shown = ", ".join("0x%02x" % b for b in sorted(bad)[:8])
        report.fail(rel, "s10.12", "bytes outside 0x20 to 0x7E plus CR, LF, TAB: " + shown)


def check_parse_defects(ctx, report):
    rel = ctx["rel"]
    msg = ctx["msg"]
    if msg.defects:
        report.fail(rel, "s10.2", "message defects: " + "; ".join(type(d).__name__ for d in msg.defects))
    for part in msg.walk():
        if part is msg:
            continue
        if part.defects:
            report.fail(rel, "s10.2", "part " + part.get_content_type() + " defects: "
                        + "; ".join(type(d).__name__ for d in part.defects))


def check_date(ctx, data, report):
    rel = ctx["rel"]
    # email.policy.default rewrites Date when it is read (it fixes the weekday and
    # turns a zone name into an offset), so the wording checks use the raw text.
    text = raw_header_value(ctx["raw"], "Date")
    if text is None:
        text = hget(ctx, "Date")
    ctx["date"] = None
    if text is None:
        report.fail(rel, "s10.3", "no Date header")
        return
    try:
        moment = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        moment = None
    if moment is None:
        report.fail(rel, "s10.3", "Date does not parse: " + text)
        return
    if not re.search(r"[+-]\d{4}\s*(?:\([^)]*\))?\s*$", text):
        report.fail(rel, "s10.3", "Date has no numeric zone (+HHMM or -HHMM): " + text)
    if moment.tzinfo is None:
        report.warn(rel, "s10.3", "Date zone is -0000 (unknown local time); treated as UTC")
    moment = to_aware(moment)
    ctx["date"] = moment
    found = re.match(r"^\s*([A-Za-z]{3}),", text)
    if found:
        expected = moment.strftime("%a")
        if found.group(1).lower() != expected.lower():
            report.fail(rel, "s10.3", "Date says " + found.group(1) + " but that date is a " + expected)
    if data.window:
        day = moment.date()
        if day < data.window[0] or day > data.window[1]:
            report.fail(rel, "design.window", "Date " + day.isoformat() + " is outside the corpus window "
                        + data.window[0].isoformat() + " to " + data.window[1].isoformat())


def check_required_headers(ctx, report):
    rel = ctx["rel"]
    for name in ("From", "Date", "Message-ID"):
        count = hcount(ctx, name)
        if count != 1:
            report.fail(rel, "s10.4", name + " appears " + str(count) + " time(s); must be exactly once")
    if hcount(ctx, "MIME-Version") != 1 or hget(ctx, "MIME-Version") != "1.0":
        report.fail(rel, "s10.11", "MIME-Version: 1.0 is required")
    message_id = hget(ctx, "Message-ID")
    if message_id is not None and not MESSAGE_ID_RE.match(message_id):
        report.fail(rel, "s10.4", "Message-ID does not match <id-left@domain.example>: " + message_id)
    if message_id is not None:
        found = MESSAGE_ID_CONVENTION_RE.match(message_id)
        if not found:
            report.warn(rel, "design.message-id", "Message-ID does not follow the corpus convention "
                        "<UTC timestamp.12 hex@originating host>: " + message_id)
        else:
            stamp = found.group(1)
            date = ctx.get("date")
            if date is not None:
                try:
                    left = datetime.datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=datetime.timezone.utc)
                    gap = abs((left - date).total_seconds())
                    if gap > 120:
                        report.warn(rel, "design.message-id", "Message-ID timestamp " + stamp
                                    + " is " + str(int(gap)) + " seconds from Date in UTC")
                except ValueError:
                    report.warn(rel, "design.message-id", "Message-ID timestamp is not a date: " + stamp)


def check_thread_headers(ctx, data, report):
    rel = ctx["rel"]
    in_reply_to = hget(ctx, "In-Reply-To")
    references = hget(ctx, "References")
    if in_reply_to is None:
        return
    ids = parse_eml.message_ids(references)
    if references is None or not ids:
        report.fail(rel, "s10.5", "In-Reply-To is present but References is missing")
        return
    if ids[-1] != in_reply_to.strip():
        report.fail(rel, "s10.5", "last References id " + ids[-1] + " does not equal In-Reply-To " + in_reply_to)


def check_return_path(ctx, report):
    rel = ctx["rel"]
    if not ctx["headers"]:
        report.fail(rel, "s10.6", "no headers at all")
        return
    if ctx["headers"][0][0].lower() != "return-path":
        report.fail(rel, "s10.6", "first header is " + ctx["headers"][0][0] + ", must be Return-Path")
    count = hcount(ctx, "Return-Path")
    if count != 1:
        report.fail(rel, "s10.6", "Return-Path appears " + str(count) + " time(s)")
        return
    display, address = parse_eml.split_address(hget(ctx, "Return-Path"))
    domain = parse_eml.domain_of(address)
    if domain is None or not domain.endswith(".example"):
        report.fail(rel, "s10.6", "Return-Path domain must end in .example: " + str(hget(ctx, "Return-Path")))


def check_received_chain(ctx, data, report):
    rel = ctx["rel"]
    hops = ctx["parsed"]["received"]
    ctx["hops"] = hops
    ctx["stamps"] = []
    ctx["gateway_index"] = None
    if not hops:
        report.fail(rel, "s10.7", "no Received header")
        return
    stamps = []
    for index, hop in enumerate(hops):
        if hop["timestamp"] is None:
            report.fail(rel, "s10.7", "Received line " + str(index + 1)
                        + ": the text after the last ';' does not parse as a date")
            stamps.append(None)
        else:
            stamps.append(parse_iso(hop["timestamp"]))
        if hop["by_host"] is not None and hop["by_host"].lower() == data.gateway_host and ctx["gateway_index"] is None:
            ctx["gateway_index"] = index
    ctx["stamps"] = stamps
    for index in range(len(hops) - 1):
        upper = stamps[index]
        lower = stamps[index + 1]
        if upper is not None and lower is not None and upper < lower:
            report.fail(rel, "s10.7", "Received line " + str(index + 1) + " (" + upper.isoformat()
                        + ") is earlier than line " + str(index + 2) + " (" + lower.isoformat()
                        + "); top to bottom must not increase")
        from_host = hops[index]["from_host"]
        by_host = hops[index + 1]["by_host"]
        if from_host is None or by_host is None or from_host.lower() != by_host.lower():
            report.fail(rel, "s10.7", "Received line " + str(index + 1) + " says from " + str(from_host)
                        + " but line " + str(index + 2) + " says by " + str(by_host))
    date = ctx.get("date")
    bottom = stamps[-1]
    if date is not None and bottom is not None:
        gap = (date - bottom).total_seconds()
        if abs(gap) > 120:
            report.fail(rel, "s10.7", "Date " + date.isoformat() + " is " + str(int(abs(gap)))
                        + " seconds from the bottom Received time " + bottom.isoformat() + "; limit 120")
        elif gap > 0:
            report.warn(rel, "s10.7", "Date is after the first hop's time; a client stamps Date before the first server accepts the message")


def check_arrival_path(ctx, data, report):
    """Decide external or internal from the file and check the gateway block."""
    rel = ctx["rel"]
    flag = hget(ctx, "X-Sentrywick-External")
    external = flag is not None and flag.lower() == "yes"
    if flag is not None and flag.lower() != "yes":
        report.fail(rel, "design.gateway", "X-Sentrywick-External must be 'yes' when present, not " + flag)
    gateway_index = ctx.get("gateway_index")
    if external and gateway_index is None:
        report.fail(rel, "design.gateway", "X-Sentrywick-External: yes but no Received line by " + data.gateway_host)
    if not external and gateway_index is not None:
        report.fail(rel, "design.gateway", "a Received line by " + data.gateway_host
                    + " but no X-Sentrywick-External: yes; external mail carries the flag")
    ctx["external"] = external

    if hcount(ctx, "X-Sentrywick-Reported-By") != 1:
        report.fail(rel, "design.gateway", "X-Sentrywick-Reported-By must appear exactly once; every corpus email was reported")
    else:
        display, reporter = parse_eml.split_address(hget(ctx, "X-Sentrywick-Reported-By"))
        if parse_eml.domain_of(reporter) != data.org:
            report.fail(rel, "design.gateway", "X-Sentrywick-Reported-By must be an address at " + data.org)

    scan = hget(ctx, "X-Sentrywick-Scan-Result")
    if scan is None:
        report.fail(rel, "design.gateway", "X-Sentrywick-Scan-Result is missing; the gateway writes it on every message")
    elif scan not in SCAN_RESULTS:
        report.fail(rel, "design.gateway", "X-Sentrywick-Scan-Result must be one of " + ", ".join(SCAN_RESULTS) + ": " + scan)

    if external:
        for name in ("Authentication-Results", "Received-SPF", "X-Sentrywick-Spam-Score"):
            if hcount(ctx, name) == 0:
                report.fail(rel, "design.gateway", name + " is missing on an external message")
        score = hget(ctx, "X-Sentrywick-Spam-Score")
        if score is not None:
            if not re.fullmatch(r"\d{1,2}\.\d", score) or float(score) > 10.0:
                report.fail(rel, "design.gateway", "X-Sentrywick-Spam-Score must be a decimal 0.0 to 10.0: " + score)
        uid = hget(ctx, "X-Sentrywick-Message-UID")
        if uid is None:
            report.warn(rel, "design.gateway", "X-Sentrywick-Message-UID is missing")
        elif gateway_index is not None:
            gateway_text = hall(ctx, "Received")[gateway_index]
            if received_id(gateway_text) != uid:
                report.warn(rel, "design.gateway", "X-Sentrywick-Message-UID " + uid
                            + " does not match the gateway Received id " + str(received_id(gateway_text)))
        # Ordering: the gateway writes its block above its own Received line.
        if gateway_index is not None:
            received_positions = []
            for index, (name, value) in enumerate(ctx["headers"]):
                if name.lower() == "received":
                    received_positions.append(index)
            gateway_pos = received_positions[gateway_index]
            for name in ("Authentication-Results", "Received-SPF", "X-Sentrywick-External",
                         "X-Sentrywick-Scan-Result", "X-Sentrywick-Spam-Score",
                         "X-Sentrywick-Message-UID", "X-Sentrywick-Reported-By", REMOVED_HEADER):
                pos = hindex(ctx, name)
                if pos is not None and pos > gateway_pos:
                    report.fail(rel, "design.ordering", name + " sits below the gateway's Received line; "
                                "the gateway's headers go above it")
            ar_pos = hindex(ctx, "Authentication-Results")
            spf_pos = hindex(ctx, "Received-SPF")
            if ar_pos is not None and spf_pos is not None and spf_pos < ar_pos:
                report.fail(rel, "design.ordering", "Authentication-Results must come before Received-SPF in the gateway block")
            if len(received_positions) >= 1 and gateway_index == 0:
                report.fail(rel, "design.ordering", "the gateway's Received line is the top one; the mail store's LMTP line should be above it")
        if len(ctx["hops"]) >= 1:
            top = ctx["hops"][0]["by_host"] or ""
            if not top.lower().startswith("mailstore"):
                report.warn(rel, "design.received", "top Received line is by " + top + "; final delivery is normally by a mailstore host")
    else:
        for name in ("Authentication-Results", "Received-SPF", "DKIM-Signature", "X-Sentrywick-External"):
            if hcount(ctx, name) != 0:
                report.fail(rel, "s10.8" if name == "Authentication-Results" else "design.internal",
                            name + " is present on an internal message; the gateway does not authenticate its own submissions")
        if ctx["hops"]:
            bottom_by = ctx["hops"][-1]["by_host"] or ""
            if bottom_by.lower() not in (data.submit_host, "webaccess." + data.org):
                report.warn(rel, "design.internal", "internal message: bottom Received line is by " + bottom_by
                            + "; expected " + data.submit_host + " or webaccess." + data.org)


def check_authentication_results(ctx, data, report):
    rel = ctx["rel"]
    values = hall(ctx, "Authentication-Results")
    ctx["auth_results"] = {}
    ctx["auth_props"] = {}
    if ctx["external"] and len(values) != 1:
        report.fail(rel, "s10.8", "external message must carry exactly one Authentication-Results; found " + str(len(values)))
    if not values:
        return
    for flat in values:
        if not AUTH_RESULTS_RE.match(flat):
            report.fail(rel, "s10.8", "Authentication-Results does not match the section 10 grammar: " + flat[:120])
        authserv, results = parse_auth_results(flat)
        if authserv != data.gateway_host:
            report.fail(rel, "s10.16", "Authentication-Results authserv-id is " + authserv + ", not " + data.gateway_host)
    authserv, results = parse_auth_results(values[0])
    ctx["auth_results"] = results
    from_domain = ctx["parsed"]["from_domain"]

    spf = results.get("spf", (None, {}))
    dkim = results.get("dkim", (None, {}))
    dmarc = results.get("dmarc", (None, {}))
    for method, vocab in (("spf", SPF_RESULTS), ("dkim", DKIM_RESULTS), ("dmarc", DMARC_RESULTS)):
        if method not in results:
            report.fail(rel, "s10.8", "Authentication-Results has no " + method + "= clause")
        elif results[method][0] not in vocab:
            report.fail(rel, "s10.8", method + "=" + results[method][0] + " is not a registered result")

    mailfrom = domain_part(spf[1].get("smtp.mailfrom"))
    dkim_d = domain_part(dkim[1].get("header.d"))
    header_from = domain_part(dmarc[1].get("header.from"))
    dmarc_policy = dmarc[1].get("policy.dmarc")
    ctx["auth_props"] = {"mailfrom": mailfrom, "dkim_d": dkim_d, "header_from": header_from,
                         "dmarc_policy": dmarc_policy}

    if "spf" in results and spf[0] != "none" and mailfrom is None:
        report.fail(rel, "s10.8", "spf=" + str(spf[0]) + " without smtp.mailfrom")
    if "dkim" in results and dkim[0] in ("pass", "fail", "policy", "neutral") and dkim_d is None:
        report.fail(rel, "s10.8", "dkim=" + str(dkim[0]) + " without header.d")
    if "dmarc" in results and header_from is None:
        report.fail(rel, "s10.8", "dmarc clause has no header.from")
    if header_from is not None and from_domain is not None and header_from != from_domain:
        report.fail(rel, "s10.8", "dmarc header.from=" + header_from + " but the From domain is " + from_domain)
    if dmarc_policy is not None and dmarc_policy not in DMARC_POLICIES:
        report.fail(rel, "s10.8", "policy.dmarc must be none, quarantine or reject: " + dmarc_policy)

    # Section 3 combination rules.
    from_org = organization_domain(header_from or from_domain)
    spf_aligned = spf[0] == "pass" and mailfrom is not None and organization_domain(mailfrom) == from_org
    dkim_aligned = dkim[0] == "pass" and dkim_d is not None and organization_domain(dkim_d) == from_org
    if dmarc[0] == "pass" and not (spf_aligned or dkim_aligned):
        report.fail(rel, "s10.8", "dmarc=pass needs an aligned spf=pass or dkim=pass (From " + str(from_domain)
                    + ", smtp.mailfrom " + str(mailfrom) + ", header.d " + str(dkim_d) + ")")
    if dmarc[0] == "fail" and (spf_aligned or dkim_aligned):
        report.fail(rel, "s10.8", "dmarc=fail although an aligned check passed")
    if dmarc[0] == "none" and dmarc_policy is not None:
        report.fail(rel, "s10.8", "dmarc=none means no record, so policy.dmarc must be absent")
    if dmarc[0] == "fail" and dmarc_policy is None:
        report.fail(rel, "s10.8", "dmarc=fail must carry policy.dmarc")

    if data.have_policy:
        entry = data.policy_lookup(header_from or from_domain)
        if entry is None:
            report.warn(rel, "data.policy", "From domain " + str(from_domain) + " has no domain_policy.json entry; DMARC policy not checked")
        else:
            published = entry.get("dmarc_policy")
            if dmarc[0] == "none" and published is not None:
                report.fail(rel, "s10.8", "dmarc=none but domain_policy.json says " + str(entry["domain"])
                            + " publishes policy " + str(published))
            if dmarc[0] in ("pass", "fail") and published is None:
                report.fail(rel, "s10.8", "dmarc=" + dmarc[0] + " but domain_policy.json says "
                            + str(entry["domain"]) + " has no DMARC record")
            if dmarc_policy is not None and published is not None and dmarc_policy != published:
                report.fail(rel, "s10.8", "policy.dmarc=" + dmarc_policy + " but domain_policy.json says "
                            + str(entry["domain"]) + " publishes " + str(published))
        if mailfrom is not None:
            spf_entry = data.policy_lookup(mailfrom)
            if spf_entry is None:
                report.warn(rel, "data.policy", "smtp.mailfrom domain " + mailfrom + " has no domain_policy.json entry; SPF record not checked")
            else:
                record = spf_entry.get("spf")
                if spf[0] == "softfail" and (record is None or not record.strip().endswith("~all")):
                    report.fail(rel, "s10.8", "spf=softfail needs an SPF record ending ~all; "
                                + spf_entry["domain"] + " has " + str(record))
                if spf[0] == "neutral" and (record is None or not record.strip().endswith("?all")):
                    report.fail(rel, "s10.8", "spf=neutral needs an SPF record ending ?all; "
                                + spf_entry["domain"] + " has " + str(record))
                if spf[0] == "none" and record is not None:
                    report.fail(rel, "s10.8", "spf=none means no SPF record, but " + spf_entry["domain"] + " has one")
                if spf[0] in ("pass", "fail") and record is None:
                    report.fail(rel, "s10.8", "spf=" + spf[0] + " needs a published SPF record; "
                                + spf_entry["domain"] + " has none")

    # Received-SPF must agree with the gateway's own verdict and its own Received line.
    rspf = hget(ctx, "Received-SPF")
    if rspf is not None:
        result, pairs = received_spf_pairs(rspf)
        if result not in SPF_RESULTS:
            report.fail(rel, "design.received-spf", "Received-SPF result " + result + " is not a registered result")
        if "spf" in results and result != spf[0]:
            report.fail(rel, "design.received-spf", "Received-SPF says " + result + " but Authentication-Results says spf=" + str(spf[0]))
        gateway_index = ctx.get("gateway_index")
        if gateway_index is not None:
            gateway_ip = ctx["hops"][gateway_index]["ip"]
            if pairs.get("client-ip") is not None and gateway_ip is not None and pairs["client-ip"] != gateway_ip:
                report.fail(rel, "design.received-spf", "Received-SPF client-ip " + pairs["client-ip"]
                            + " differs from the gateway Received address " + gateway_ip)
        if pairs.get("receiver") is not None and pairs["receiver"].lower() != data.gateway_host:
            report.fail(rel, "design.received-spf", "Received-SPF receiver is " + pairs["receiver"] + ", not " + data.gateway_host)
        envelope = pairs.get("envelope-from")
        if envelope is not None:
            if mailfrom is not None and domain_part(envelope) != mailfrom:
                report.fail(rel, "design.received-spf", "Received-SPF envelope-from " + envelope
                            + " is not in the smtp.mailfrom domain " + mailfrom)
            display, return_path = parse_eml.split_address(hget(ctx, "Return-Path"))
            if return_path is not None and envelope.strip("<>").lower() != return_path.lower():
                report.fail(rel, "design.received-spf", "Received-SPF envelope-from " + envelope
                            + " differs from Return-Path " + return_path)
        if pairs.get("identity") is not None and pairs["identity"].lower() != "mailfrom":
            report.warn(rel, "design.received-spf", "Received-SPF identity is " + pairs["identity"] + "; DMARC uses mailfrom")
    elif ctx["external"]:
        pass  # already reported as missing in check_arrival_path


def gather_domain_positions(ctx):
    """Every place a domain appears, as (label, domain)."""
    positions = []

    def add_address(label, address):
        domain = parse_eml.domain_of(address)
        if domain:
            positions.append((label, domain))

    for name in ("From", "To", "Cc", "Reply-To", "Return-Path", "Sender", "X-Sentrywick-Reported-By"):
        for text in hall(ctx, name):
            for address in parse_eml.address_list(text):
                add_address(name, address)
    for index, text in enumerate(hall(ctx, "Received")):
        hop = parse_eml.parse_received(text)
        for key in ("from_host", "by_host"):
            host = hop[key]
            if host and not host.startswith("["):
                positions.append(("Received " + str(index + 1) + " " + key.split("_")[0], host.lower()))
        found = re.search(r"\bfor\s+<([^>]+)>", text)
        if found:
            add_address("Received " + str(index + 1) + " for", found.group(1))
    rspf = hget(ctx, "Received-SPF")
    if rspf is not None:
        result, pairs = received_spf_pairs(rspf)
        for key in ("envelope-from", "receiver", "helo"):
            if pairs.get(key):
                positions.append(("Received-SPF " + key, domain_part(pairs[key])))
    for flat in hall(ctx, "Authentication-Results"):
        authserv, results = parse_auth_results(flat)
        if authserv:
            positions.append(("Authentication-Results authserv-id", authserv))
        for method in results:
            props = results[method][1]
            for key in ("smtp.mailfrom", "smtp.helo", "header.d", "header.from", "header.i"):
                if key in props:
                    positions.append(("Authentication-Results " + key, domain_part(props[key])))
    for flat in hall(ctx, "DKIM-Signature"):
        tags = dkim_tags(flat)
        for key in ("d", "i"):
            if key in tags:
                positions.append(("DKIM-Signature " + key + "=", domain_part(tags[key])))
    for name in ("Message-ID", "In-Reply-To", "References"):
        for text in hall(ctx, name):
            for message_id in parse_eml.message_ids(text):
                inner = message_id.strip("<>")
                if "@" in inner:
                    positions.append((name, inner.rsplit("@", 1)[1].lower()))
    list_id = hget(ctx, "List-Id")
    if list_id is not None:
        found = re.search(r"<([^>]+)>", list_id)
        if found:
            positions.append(("List-Id", found.group(1).strip().lower()))
    for text in hall(ctx, "List-Unsubscribe"):
        for target in re.findall(r"<([^>]+)>", text):
            target = target.strip()
            if target.lower().startswith("http"):
                positions.append(("List-Unsubscribe", parse_eml.host_of_url(target)))
            elif target.lower().startswith("mailto:"):
                add_address("List-Unsubscribe", target[7:].split("?", 1)[0])
    for label, text in (("plain body", ctx.get("plain")), ("HTML body", ctx.get("html"))):
        if not text:
            continue
        for url in parse_eml.find_urls(text):
            positions.append((label + " link", parse_eml.host_of_url(url)))
        for found in re.finditer(r"mailto:([^\s<>\"'?]+)", text):
            add_address(label + " mailto", found.group(1))
    return positions


def check_domains(ctx, data, tlds, report):
    rel = ctx["rel"]
    positions = gather_domain_positions(ctx)
    ctx["positions"] = positions
    reported = set()
    for label, domain in positions:
        ctx["domains"].add(domain)
        if not domain.endswith(".example") and (label, domain) not in reported:
            reported.add((label, domain))
            report.fail(rel, "s10.9", label + ": " + domain + " does not end in .example")

    # Safety net over the decoded text.
    text = decoded_text(ctx).lower()
    for stub in ctx["parsed"]["attachments"]:
        if stub["filename"]:
            text = text.replace(stub["filename"].lower(), " ")
    seen = set()
    # The lookahead skips the local part of an address (c.hallowden in c.hallowden@...).
    for token in re.findall(r"(?<![a-z0-9.-])[a-z0-9-]+(?:\.[a-z0-9-]+)+(?![a-z0-9.@-])", text):
        if token in seen:
            continue
        seen.add(token)
        last = token.split(".")[-1]
        if not re.fullmatch(r"[a-z]{2,}", last):
            continue
        if last == "example" or token in PROPERTY_TOKENS or last in FILE_EXTENSIONS:
            continue
        if tlds.is_delegated(last):
            report.fail(rel, "s10.9", "'" + token + "' ends in the delegated top-level domain ." + last)
        else:
            report.warn(rel, "s10.9", "'" + token + "' looks like a domain but does not end in .example")


def check_ip_literals(ctx, report):
    rel = ctx["rel"]
    text = decoded_text(ctx).lower()
    seen = set()
    for found in re.finditer(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])", text):
        candidate = found.group(1)
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            address = ipaddress.IPv4Address(candidate)
        except ValueError:
            continue
        if not any(address in block for block in ALLOWED_V4):
            report.fail(rel, "s10.10", "IPv4 address " + candidate + " is outside the private and documentation blocks")
    for found in re.finditer(r"(?<![0-9a-f:])((?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4})(?![0-9a-f:])", text):
        candidate = found.group(1)
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            address = ipaddress.IPv6Address(candidate)
        except ValueError:
            continue
        if address not in ALLOWED_V6:
            report.fail(rel, "s10.10", "IPv6 address " + candidate + " is outside 2001:db8::/32")


def check_mime(ctx, report):
    rel = ctx["rel"]
    msg = ctx["msg"]
    if msg.get_content_type() != "multipart/alternative":
        report.fail(rel, "s10.11", "top-level Content-Type is " + msg.get_content_type() + ", must be multipart/alternative")
    boundary = msg.get_boundary()
    if boundary is not None and len(boundary) > 70:
        report.fail(rel, "s10.11", "multipart boundary is " + str(len(boundary)) + " characters; limit 70")
    if msg.is_multipart():
        types = []
        for part in msg.iter_parts():
            types.append(part.get_content_type())
        if types != ["text/plain", "text/html"]:
            report.fail(rel, "s10.11", "parts are " + str(types) + "; expected exactly text/plain then text/html")
    try:
        attachments = list(msg.iter_attachments())
    except Exception:
        attachments = []
    if attachments:
        report.fail(rel, "s10.11", "iter_attachments() is not empty")
    for part in msg.walk():
        disposition = part.get("Content-Disposition")
        if disposition is not None and str(disposition).strip().lower().startswith("attachment"):
            report.fail(rel, "s10.11", "a part carries Content-Disposition: attachment")
        if part.get_content_maintype() == "multipart":
            continue
        encoding = part.get("Content-Transfer-Encoding")
        encoding = "7bit" if encoding is None else str(encoding).strip().lower()
        if encoding not in ("7bit", "quoted-printable"):
            report.fail(rel, "s10.12", "Content-Transfer-Encoding " + encoding + " on a " + part.get_content_type()
                        + " part; only 7bit and quoted-printable are allowed")
        if encoding == "base64":
            payload = part.get_payload(decode=True) or b""
            if len(payload) > 2048:
                report.fail(rel, "s10.12", "base64 body of " + str(len(payload)) + " bytes; over 2 KB")
        charset = part.get_content_charset()
        if charset is not None and charset.lower() != "utf-8":
            report.warn(rel, "s10.11", part.get_content_type() + " charset is " + charset + "; the convention is utf-8")
        encoded = part.get_payload(decode=False)
        if isinstance(encoded, str):
            if encoding == "quoted-printable":
                long_lines = 0
                for line in encoded.splitlines():
                    if len(line) > 76:
                        long_lines += 1
                if long_lines:
                    report.fail(rel, "s10.12", str(long_lines) + " quoted-printable line(s) over 76 characters in the "
                                + part.get_content_type() + " part")
            if encoding == "7bit":
                long_lines = 0
                for line in encoded.splitlines():
                    if len(line) > 78:
                        long_lines += 1
                if long_lines:
                    report.fail(rel, "s10.12", str(long_lines) + " line(s) over 78 characters in a 7bit "
                                + part.get_content_type() + " part; use quoted-printable")

    # HTML restriction from the corpus design, section 11.
    html_source = ctx.get("html")
    if html_source:
        lower = html_source.lower()
        for marker in FORBIDDEN_HTML:
            if marker in lower:
                report.fail(rel, "design.html", "HTML part contains '" + marker + "'")
        for found in re.finditer(r'style\s*=\s*"([^"]*)"', lower):
            style = found.group(1)
            if re.search(r"visibility\s*:\s*hidden", style) or re.search(r"opacity\s*:\s*0(?![.0-9]*[1-9])", style):
                report.fail(rel, "design.html", "hidden text must use display:none or font-size:0 only: style=\"" + style + "\"")


def check_banner(ctx, report):
    """Section 10 item 17: the external banner, exactly once, in the fixed place."""
    rel = ctx["rel"]
    plain = ctx.get("plain") or ""
    html_source = ctx.get("html") or ""
    if not ctx["external"]:
        for label, text in (("plain", plain), ("HTML", html_source)):
            if BANNER in text:
                report.fail(rel, "s10.17", "internal message: the " + label + " part contains the external banner text")
        return
    lines = plain.splitlines()
    if not lines or lines[0] != BANNER:
        report.fail(rel, "s10.17", "plain part does not begin with the line " + BANNER + "; first line: " + first_line(plain)[:80])
    elif len(lines) < 2 or lines[1] != "":
        report.fail(rel, "s10.17", "plain part: the banner line must be followed by one empty line")
    count = plain.count(BANNER)
    if count != 1:
        report.fail(rel, "s10.17", "plain part contains the banner text " + str(count) + " times; exactly once is required")
    count = html_source.count(BANNER)
    if count != 1:
        report.fail(rel, "s10.17", "HTML part contains the banner text " + str(count) + " times; exactly once is required")
    index = html_source.find(HTML_BANNER_SNIPPET)
    if index < 0:
        report.fail(rel, "s10.17", "HTML part does not contain the section 2 banner snippet byte for byte")
        return
    line_start = html_source.rfind("\n", 0, index) + 1
    line_end = html_source.find("\n", index)
    if line_end < 0:
        line_end = len(html_source)
    if html_source[line_start:line_end].rstrip("\r ") != HTML_BANNER_SNIPPET:
        report.fail(rel, "s10.17", "the banner snippet must stand alone on one line of the HTML part")
    before = html_source[:index]
    body_tag = re.search(r"<body\b[^>]*>", before, re.IGNORECASE)
    if body_tag is not None:
        gap = before[body_tag.end():]
        place = "immediately after the <body> tag"
    elif re.search(r"<body\b", before, re.IGNORECASE):
        gap = "x"
        place = "after an unterminated <body> tag"
    else:
        gap = before
        place = "the first line when there is no <body> tag"
    if gap.strip() != "":
        report.fail(rel, "s10.17", "the banner snippet must be " + place + "; found other content before it")


def check_removed_attachments(ctx, data, report):
    rel = ctx["rel"]
    stubs = hall(ctx, REMOVED_HEADER)
    entries = data.attachments_by_id.get(ctx["stem"], [])
    filenames = []
    ctx["stubs"] = []
    for index, flat in enumerate(stubs):
        found = REMOVED_RE.match(flat)
        if not found:
            report.fail(rel, "s10.13", REMOVED_HEADER + " " + str(index + 1) + " does not match the grammar: " + flat[:100])
            continue
        filename, size, sha256, action, mime_type, reason = found.groups()
        size = int(size)
        filenames.append(filename)
        ctx["stubs"].append({"filename": filename, "size": size, "sha256": sha256, "action": action,
                             "type": mime_type, "reason": reason})
        if reason is not None and data.attachment_reasons is not None and reason not in data.attachment_reasons:
            report.fail(rel, "s10.13", "reason=" + reason + " is not in enums.json")
        if reason == "blocked-extension" and action != "stripped":
            report.fail(rel, "s10.13", "a blocked extension is always stripped, not " + action)
        if reason in ("macro-detected", "archived-to-vault") and action != "quarantined":
            report.fail(rel, "s10.13", "reason " + reason + " goes with action=quarantined, not " + action)
        for label, text in (("plain", ctx.get("plain")), ("HTML", ctx.get("html_text"))):
            collapsed = " ".join((text or "").split())
            if not re.search(re.escape(GATEWAY_PRODUCT) + r"[^\]]{0,160}?" + re.escape(filename), collapsed):
                report.fail(rel, "s10.13", label + " part has no gateway notice naming " + filename)
        if data.have_attachments:
            entry = None
            for candidate in entries:
                if candidate["filename"] == filename:
                    entry = candidate
            if entry is None:
                report.fail(rel, "data.attachments", filename + " is not in attachments.json for " + ctx["stem"])
            else:
                if not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256"))):
                    report.fail(rel, "data.attachments", "attachments.json sha256 for " + filename + " is not 64 hex digits")
                for key, value in (("sha256", sha256), ("size", size), ("action", action)):
                    if entry.get(key) != value:
                        report.fail(rel, "data.attachments", key + " for " + filename + " is " + str(value)
                                    + " in the header but " + str(entry.get(key)) + " in attachments.json")
                for key, value in (("type", mime_type), ("reason", reason)):
                    if value is None:
                        report.warn(rel, "data.attachments", "header for " + filename + " omits " + key
                                    + "; attachments.json has " + str(entry.get(key)))
                    elif entry.get(key) != value:
                        report.fail(rel, "data.attachments", key + " for " + filename + " is " + value
                                    + " in the header but " + str(entry.get(key)) + " in attachments.json")
    for entry in entries:
        if entry["filename"] not in filenames:
            report.fail(rel, "data.attachments", "attachments.json lists " + entry["filename"]
                        + " for this email but the file has no matching " + REMOVED_HEADER)


def check_dkim(ctx, data, report):
    rel = ctx["rel"]
    signatures = hall(ctx, "DKIM-Signature")
    results = ctx.get("auth_results", {})
    dkim_result = results.get("dkim", (None, {}))[0]
    dkim_d = ctx.get("auth_props", {}).get("dkim_d")
    tags_list = []
    for flat in signatures:
        tags = dkim_tags(flat)
        tags_list.append(tags)
        if tags.get("v") != "1":
            report.fail(rel, "s10.14", "DKIM-Signature needs v=1")
        for key in ("a", "c", "d", "s", "h", "bh", "b"):
            if not tags.get(key):
                report.fail(rel, "s10.14", "DKIM-Signature is missing " + key + "=")
        if tags.get("d") and not tags["d"].lower().endswith(".example"):
            report.fail(rel, "s10.14", "DKIM d=" + tags["d"] + " does not end in .example")
        if tags.get("h") and "from" not in tags["h"].lower().split(":"):
            report.fail(rel, "s10.14", "DKIM h= does not include from")
        if tags.get("bh") and not re.fullmatch(r"[A-Za-z0-9+/]{43}=", tags["bh"]):
            report.fail(rel, "s10.14", "DKIM bh= must be 44 base64 characters (a SHA-256 digest): " + tags["bh"][:50])
        if tags.get("b") and not re.fullmatch(r"[A-Za-z0-9+/]+=*", tags["b"]):
            report.fail(rel, "s10.14", "DKIM b= is not base64")
        elif tags.get("b") and len(tags["b"]) != 344:
            report.warn(rel, "s10.14", "DKIM b= is " + str(len(tags["b"])) + " characters; a 2048-bit RSA signature is 344")
        if tags.get("a") and tags["a"].lower() != "rsa-sha256":
            report.warn(rel, "s10.14", "DKIM a=" + tags["a"] + "; the specification recommends rsa-sha256")
        if dkim_d is not None and tags.get("d") and tags["d"].lower() != dkim_d:
            report.fail(rel, "s10.14", "DKIM d=" + tags["d"] + " but Authentication-Results says header.d=" + dkim_d)
    if ctx["external"]:
        if dkim_result in ("pass", "fail", "policy", "neutral") and not signatures:
            report.fail(rel, "s10.14", "Authentication-Results says dkim=" + dkim_result + " but there is no DKIM-Signature")
        if dkim_result == "none" and signatures:
            report.fail(rel, "s10.14", "dkim=none means the message was not signed, but a DKIM-Signature is present")
    post = hget(ctx, "List-Unsubscribe-Post")
    if post is not None:
        unsubscribe = hget(ctx, "List-Unsubscribe")
        if unsubscribe is None or "https://" not in unsubscribe.lower():
            report.fail(rel, "design.list", "List-Unsubscribe-Post requires an https URL in List-Unsubscribe")
        if not tags_list:
            report.fail(rel, "design.list", "List-Unsubscribe-Post requires a DKIM signature covering the list headers")
        else:
            signed = tags_list[0].get("h", "").lower().split(":")
            for name in ("list-unsubscribe", "list-unsubscribe-post"):
                if name not in signed:
                    report.fail(rel, "design.list", "DKIM h= must cover " + name + " when List-Unsubscribe-Post is present")


def check_arc(ctx, report):
    rel = ctx["rel"]
    record = ctx.get("record") or {}
    forwarding = bool(record.get("forwarding_case"))
    for name, value in ctx["headers"]:
        if name.lower().startswith("arc-") and not forwarding:
            report.fail(rel, "s10.15", name + " is present; ARC appears only on a forwarding case flagged in the ground truth")
            return


def check_bulk_headers(ctx, data, report):
    rel = ctx["rel"]
    unsubscribe = hget(ctx, "List-Unsubscribe")
    if unsubscribe is None:
        return
    if not ctx["external"]:
        report.fail(rel, "design.list", "List-Unsubscribe on an internal message")
    precedence = hget(ctx, "Precedence")
    if precedence is None or precedence.lower() != "bulk":
        report.warn(rel, "design.list", "bulk mail normally carries Precedence: bulk")
    if hget(ctx, "List-Id") is None:
        report.warn(rel, "design.list", "bulk mail normally carries List-Id")


# ---------------------------------------------------------------------------
# Per-file checks: the data files and the record
# ---------------------------------------------------------------------------

def check_data_files(ctx, data, report):
    rel = ctx["rel"]
    parsed = ctx["parsed"]
    if data.have_reputation:
        if parsed["from_address"] is None:
            report.fail(rel, "data.reputation", "no From address to look up")
        elif data.rep_lookup(parsed["from_address"]) is None:
            report.fail(rel, "data.reputation", "sender domain " + str(parsed["from_domain"]) + " has no record in sender_reputation.json")
        if parsed["reply_to"] is not None and data.rep_lookup(parsed["reply_to"]) is None:
            report.fail(rel, "data.reputation", "Reply-To domain " + str(parse_eml.domain_of(parsed["reply_to"]))
                        + " has no record in sender_reputation.json")
    if data.have_recipients:
        for address in parsed["to"] + parsed["cc"]:
            if address.lower() not in data.recipients:
                report.fail(rel, "data.recipients", "recipient " + address + " is not in recipients.json")
        reporter = parsed["gateway"]["reported_by"]
        if reporter is not None:
            entry = data.recipients.get(reporter.lower())
            if entry is None:
                report.fail(rel, "data.recipients", "reporter " + reporter + " is not in recipients.json")
            elif entry.get("mailbox_type") != "person":
                report.fail(rel, "data.recipients", "reporter " + reporter + " must be a named person, not a " + str(entry.get("mailbox_type")))
        # A mailbox lives on exactly one store, so the LMTP hop follows the recipient, never the arrival path.
        delivery = hall(ctx, "Received")
        if delivery:
            flat = " ".join(delivery[0].split())
            by_host = re.search(r"\bby\s+(\S+)", re.sub(r"\([^)]*\)", " ", flat))
            envelope = re.search(r"\bfor\s+<([^>]+)>", flat)
            if by_host and envelope and by_host.group(1).lower().startswith("mailstore"):
                store = by_host.group(1).split(".")[0].lower()
                entry = data.recipients.get(envelope.group(1).lower())
                want = (entry or {}).get("mailstore")
                if want and store != want:
                    report.fail(rel, "data.recipients", "the LMTP hop delivers " + envelope.group(1) + " by "
                                + store + " but recipients.json puts that mailbox on " + want
                                + "; a mailbox lives on exactly one store")
    if data.have_url_lists:
        for host in parsed["url_hosts"]:
            status = data.url_status(host)
            if status == "unlisted" and data.have_unlisted and host not in data.unlisted_hosts:
                report.fail(rel, "data.urls", "link host " + host + " is on neither list and not in url_unlisted.json")
    if data.have_policy:
        display, return_path = parse_eml.split_address(hget(ctx, "Return-Path"))
        checks = [("From", parsed["from_domain"]), ("Reply-To", parse_eml.domain_of(parsed["reply_to"])),
                  ("Return-Path", parse_eml.domain_of(return_path)), ("DKIM d=", ctx.get("auth_props", {}).get("dkim_d"))]
        for label, domain in checks:
            if domain is not None and data.policy_lookup(domain) is None:
                report.fail(rel, "data.policy", label + " domain " + domain + " is not in domain_policy.json")
        for host in parsed["url_hosts"]:
            if data.policy_lookup(host) is None:
                report.warn(rel, "data.policy", "link host " + host + " has no domain_policy.json entry")
    text = decoded_text(ctx).lower()
    for decoy in sorted(data.decoy_domains | data.decoy_hosts):
        if re.search(r"(?<![a-z0-9-])" + re.escape(decoy) + r"(?![a-z0-9-])", text):
            report.fail(rel, "data.decoy", "decoy name " + decoy + " appears in the file; decoys never appear in the corpus")


def check_record(ctx, data, ground_truth, corpus_ids, report):
    rel = ctx["rel"]
    parsed = ctx["parsed"]
    record = ground_truth.get(ctx["stem"])
    source = "ground truth"
    if record is None:
        record = data.spec_records.get(ctx["stem"])
        source = "manifest"
    if record is None:
        report.fail(rel, "record", "no ground truth or manifest record has the id " + ctx["stem"])
        return
    ctx["record"] = record

    def mismatch(field, want, got):
        report.fail(rel, "record." + field, source + " says " + repr(want) + " but the file has " + repr(got))

    def same_address(a, b):
        return (a or "").lower() == (b or "").lower()

    if not same_address(record.get("sender_address"), parsed["from_address"]):
        mismatch("sender_address", record.get("sender_address"), parsed["from_address"])
    if record.get("sender_display") != parsed["from_display"]:
        mismatch("sender_display", record.get("sender_display"), parsed["from_display"])
    if not same_address(record.get("reply_to"), parsed["reply_to"]):
        mismatch("reply_to", record.get("reply_to"), parsed["reply_to"])
    recipients = []
    for address in parsed["to"] + parsed["cc"]:
        recipients.append(address.lower())
    if (record.get("recipient") or "").lower() not in recipients:
        mismatch("recipient", record.get("recipient"), parsed["to"] + parsed["cc"])
    if not same_address(record.get("reporter"), parsed["gateway"]["reported_by"]):
        mismatch("reporter", record.get("reporter"), parsed["gateway"]["reported_by"])
    if record.get("subject") != parsed["subject"]:
        mismatch("subject", record.get("subject"), parsed["subject"])
    want_date = parse_iso(record.get("date"))
    if want_date is not None and ctx.get("date") is not None and want_date != ctx["date"]:
        mismatch("date", record.get("date"), ctx["date"].isoformat())

    auth = record.get("auth") or {}
    for method in ("spf", "dkim", "dmarc"):
        if auth.get(method) != parsed["auth"][method]:
            mismatch("auth." + method, auth.get(method), parsed["auth"][method])
    if "dmarc_policy" in auth and auth["dmarc_policy"] != parsed["auth"]["dmarc_policy"]:
        mismatch("auth.dmarc_policy", auth["dmarc_policy"], parsed["auth"]["dmarc_policy"])

    path = record.get("arrival_path")
    has_list = hget(ctx, "List-Unsubscribe") is not None
    if path == "internal" and ctx["external"]:
        mismatch("arrival_path", "internal", "external (X-Sentrywick-External: yes)")
    if path in ("external_gateway", "bulk_provider") and not ctx["external"]:
        mismatch("arrival_path", path, "internal (no X-Sentrywick-External)")
    if path == "bulk_provider" and not has_list:
        mismatch("arrival_path", "bulk_provider with list headers", "no List-Unsubscribe")
    if path == "external_gateway" and has_list:
        report.warn(rel, "record.arrival_path", source + " says external_gateway but the file carries List-Unsubscribe")

    want_hosts = record.get("url_hosts") or []
    if set(want_hosts) != set(parsed["url_hosts"]):
        mismatch("url_hosts", want_hosts, parsed["url_hosts"])
    elif list(want_hosts) != list(parsed["url_hosts"]):
        report.warn(rel, "record.url_hosts", "same hosts in a different order: " + source + " " + str(want_hosts)
                    + ", file " + str(parsed["url_hosts"]))

    attachment = record.get("attachment")
    stubs = ctx.get("stubs", [])
    if attachment is None and stubs:
        mismatch("attachment", None, stubs[0]["filename"])
    elif attachment is not None and not stubs:
        mismatch("attachment", attachment.get("filename"), None)
    elif attachment is not None:
        stub = stubs[0]
        for key in ("filename", "size", "sha256", "action", "type", "reason"):
            if attachment.get(key) != stub.get(key):
                mismatch("attachment." + key, attachment.get(key), stub.get(key))

    # Indicators the headers decide.
    indicators = record_indicators(record)
    codes = {}
    for code, value in indicators:
        codes.setdefault(code, []).append(value)

    def has(code):
        return code in codes

    def expect(code, condition, description):
        if has(code) and not condition:
            report.fail(rel, "record.indicator", source + " lists " + code + " but the file " + description)
        if not has(code) and condition and code in REVERSIBLE:
            # description says what a file that CONTRADICTS the code looks like, so the
            # reverse message needs its opposite. Stripping "does not "/"has no " inverts
            # the negative descriptions; the affirmative ones cannot be inverted by
            # surgery and would otherwise print the opposite of what the file says, so
            # they are spelled out in INVERSE_DESCRIPTION.
            affirmative = INVERSE_DESCRIPTION.get(
                description,
                description.replace("does not ", "").replace("has no ", "has "))
            report.fail(rel, "record.indicator", "the file " + affirmative
                        + " but " + source + " does not list " + code)

    in_reply_to = hget(ctx, "In-Reply-To")
    resolves = in_reply_to is not None and (in_reply_to.strip() in data.thread_ids or in_reply_to.strip() in corpus_ids)
    subject = parsed["subject"] or ""
    scan = parsed["gateway"]["scan_result"]
    priority = hget(ctx, "X-Priority")
    importance = hget(ctx, "Importance")
    raw_subject = raw_header_value(ctx["raw"], "Subject")
    pairs = [
        ("thread:new", in_reply_to is None, "has an In-Reply-To header"),
        ("thread:in_reply_to_known", resolves, "has no In-Reply-To that resolves to known_threads.json or a corpus Message-ID"),
        ("thread:in_reply_to_unknown", in_reply_to is not None and not resolves, "does not have an unresolvable In-Reply-To"),
        ("thread:reply_subject_without_reference", subject.lower().startswith("re:") and in_reply_to is None
         and hget(ctx, "References") is None, "does not have a Re: subject without In-Reply-To"),
        ("header:released_from_quarantine", scan == "released-from-quarantine", "has no X-Sentrywick-Scan-Result: released-from-quarantine"),
        ("header:x_priority_high", (priority or "").startswith("1") or (importance or "").lower() == "high",
         "has no X-Priority: 1 or Importance: high"),
        ("header:auto_submitted", hget(ctx, "Auto-Submitted") is not None, "has no Auto-Submitted header"),
        ("header:list_headers_present", has_list, "has no List-Unsubscribe header"),
        ("header:precedence_bulk", (hget(ctx, "Precedence") or "").lower() == "bulk", "has no Precedence: bulk"),
        ("header:x_originating_ip", parsed["x_originating_ip"] is not None, "has no X-Originating-IP"),
        ("header:webmail_submission_external_ip", parsed["x_originating_ip"] is not None, "has no X-Originating-IP"),
        ("header:encoded_word_subject", "=?" in (raw_subject or ""), "has no encoded-word Subject"),
        ("attachment:none", not stubs, "has a removed-attachment header"),
        ("attachment:blocked_extension", any(s.get("reason") == "blocked-extension" for s in stubs), "has no blocked-extension stub"),
        ("attachment:macro_detected", any(s.get("reason") == "macro-detected" for s in stubs), "has no macro-detected stub"),
        ("attachment:archived_to_vault", any(s.get("reason") == "archived-to-vault" for s in stubs), "has no archived-to-vault stub"),
        ("url:none", not parsed["urls"], "has links"),
        ("url:multiple_hosts", len(parsed["url_hosts"]) > 1, "has fewer than two link hosts"),
        ("content:html_hidden_text", parsed["hidden_html_text"] != "", "has no hidden HTML text"),
        ("auth:not_evaluated_internal", not ctx["external"], "is external"),
        ("auth:all_pass", parsed["auth"]["spf"] == "pass" and parsed["auth"]["dkim"] == "pass"
         and parsed["auth"]["dmarc"] == "pass", "does not have all three checks passing"),
        ("sender:reply_to_differs", parsed["reply_to"] is not None
         and not same_address(parsed["reply_to"], parsed["from_address"]), "has no Reply-To that differs from From"),
        ("sender:internal_domain_via_external_path", ctx["external"] and parsed["from_domain"] == data.org,
         "is not the organization's domain arriving through the gateway"),
    ]
    for method in ("spf", "dkim", "dmarc"):
        for result in ("pass", "fail", "softfail", "none", "temperror", "permerror"):
            code = "auth:" + method + "_" + result
            pairs.append((code, parsed["auth"][method] == result, "has " + method + "=" + str(parsed["auth"][method])))
    for code, condition, description in pairs:
        expect(code, condition, description)
    for value in codes.get("header:external_flag", []):
        if value is not None and (value == "yes") != ctx["external"]:
            report.fail(rel, "record.indicator", source + " lists header:external_flag:" + value
                        + " but the file is " + ("external" if ctx["external"] else "internal"))
    for value in codes.get("header:spam_score", []):
        try:
            if value is not None and float(value) != parsed["gateway"]["spam_score"]:
                report.fail(rel, "record.indicator", source + " lists header:spam_score:" + str(value)
                            + " but the file says " + str(parsed["gateway"]["spam_score"]))
        except ValueError:
            pass
    if parsed["hidden_html_text"] != "" and not has("content:html_hidden_text"):
        report.fail(rel, "record.indicator", "the file has hidden HTML text (a comment or a hidden element) but "
                    + source + " does not list content:html_hidden_text")

    injection = record.get("injection")
    if injection:
        placement = injection.get("placement")
        part = injection.get("part")
        payload = injection.get("payload")
        if placement == "header_forged":
            gateway_index = ctx.get("gateway_index")
            received_positions = []
            for index, (name, value) in enumerate(ctx["headers"]):
                if name.lower() == "received":
                    received_positions.append(index)
            if gateway_index is not None and gateway_index < len(received_positions):
                gateway_pos = received_positions[gateway_index]
                forged = False
                for index in range(gateway_pos + 1, len(ctx["headers"])):
                    name = ctx["headers"][index][0].lower()
                    if name.startswith("x-sentrywick-") or name == "x-analyst-note":
                        forged = True
                if not forged:
                    report.fail(rel, "record.injection", source + " says header_forged but no forged gateway-style header sits below the gateway's Received line")
        if payload:
            needle = " ".join(payload.split())
            targets = []
            if part in ("plain", "both"):
                targets.append(("plain", " ".join((ctx.get("plain") or "").split())))
            if part in ("html", "both"):
                targets.append(("HTML", " ".join((ctx.get("html") or "").split())))
            if part == "header":
                targets.append(("headers", " ".join(decoded_text(ctx).split())))
            if placement == "attachment_filename":
                targets = [("attachment filename", " ".join(s.get("filename") or "" for s in stubs))]
            if placement == "subject_line":
                targets = [("subject and display name", (parsed["subject"] or "") + " " + parsed["from_display"])]
            for label, haystack in targets:
                if needle not in haystack:
                    report.fail(rel, "record.injection", "injection payload not found verbatim in the " + label + " part")
        if placement == "html_hidden" and parsed["hidden_html_text"] == "":
            report.fail(rel, "record.injection", source + " says html_hidden but the HTML part hides no text")


# Content codes whose phrase list is not a membership test, so the phrase pass skips
# them. content:non_english_body is a proportion judgment and its list is Spanish
# stopwords ("de", "la", "en") that appear inside ordinary English words. The
# content:instruction_to_ai list holds single words ("automated", "classify",
# "verdict") that the corpus also puts inside quoted examples on benign mail, where
# the correct code is content:instruction_like_text_in_quote.
PHRASE_PASS_SKIP = {"content:non_english_body", "content:instruction_to_ai"}


def check_content_phrases(ctx, data, report):
    """Run the enums.json content phrase lists against the decoded body parts.

    The design calls the content codes deterministic: each one is matched from a fixed
    phrase list, the same way the header codes are read from headers. So the check runs
    both ways for every code whose vocabulary entry says where=body. A phrase in the
    rendered body with no indicator means the record is missing a fact a student's own
    extractor will produce. An indicator with no phrase in the rendered body means the
    record claims a fact the corpus extraction mechanism cannot find where it says to
    look.
    """
    record = ctx.get("record")
    if record is None or not data.enums:
        return
    phrases = data.enums.get("content_phrases") or {}
    if not phrases:
        return
    where_of = {}
    for entry in data.enums.get("indicator_vocabulary", []) or []:
        where_of[entry["code"]] = entry.get("where")
    source = record.get("_source", "the record")
    body = ((ctx.get("plain") or "") + "\n" + (ctx.get("html") or "")).lower()
    listed = {code for code, _value in record_indicators(record)}
    for code in sorted(phrases):
        if code in PHRASE_PASS_SKIP or where_of.get(code) != "body":
            continue
        hits = [phrase for phrase in phrases[code] if phrase.lower() in body]
        if hits and code not in listed:
            report.fail(ctx["rel"], "record.phrase", "the body carries the " + code
                        + " phrase " + repr(hits[0]) + " but " + source
                        + " does not list " + code)
        if code in listed and not hits:
            report.fail(ctx["rel"], "record.phrase", source + " lists " + code
                        + " but no phrase from its list in spec/enums.json appears in"
                        + " either decoded body part")
    # The recorded value names the matched phrases, so it has to be built from the list.
    for code, value in record_indicators(record):
        if code in PHRASE_PASS_SKIP or code not in phrases or not value:
            continue
        known = {phrase.lower() for phrase in phrases[code]}
        for part in str(value).split("; "):
            if part.lower() not in known:
                report.fail(ctx["rel"], "record.phrase", source + " records " + code
                            + " with the value " + repr(part)
                            + ", which is not an entry in its phrase list")


# Codes the manifest lists whenever the header fact is present, so the check runs both
# ways. Codes outside this set are checked one way only: listed means the file agrees.
# The manifest writes auth:all_pass instead of the three pass codes, and it lists
# header:precedence_bulk and url:multiple_hosts only for some emails, so those stay one way.
REVERSIBLE = {"thread:new", "header:released_from_quarantine", "header:list_headers_present",
              "header:x_originating_ip", "attachment:none", "attachment:blocked_extension",
              "attachment:archived_to_vault", "attachment:macro_detected", "url:none",
              "auth:not_evaluated_internal", "auth:all_pass", "header:auto_submitted",
              "header:x_priority_high", "header:encoded_word_subject",
              "sender:internal_domain_via_external_path", "auth:spf_fail", "auth:spf_softfail",
              "auth:spf_permerror", "auth:dkim_none", "auth:dkim_fail", "auth:dkim_temperror",
              "auth:dmarc_none", "auth:dmarc_fail"}

# The reverse direction of the indicator check reports what the file DOES carry, and
# the pair descriptions are written for the forward direction, where they say what a
# contradicting file carries. Descriptions phrased "does not ..." or "has no ..." are
# inverted by stripping that prefix. These are the affirmative ones, which stripping
# cannot invert: without the map the reverse message asserted the opposite of the
# file, so a record missing thread:new was told the file "has an In-Reply-To header"
# when the failure is that it has none.
INVERSE_DESCRIPTION = {
    "has an In-Reply-To header": "has no In-Reply-To header",
    "has a removed-attachment header": "has no removed-attachment header",
    "has links": "has no links",
    "is external": "is internal",
    "does not have all three checks passing": "has all three checks passing",
    "is not the organization's domain arriving through the gateway":
        "is the organization's domain arriving through the gateway",
    "has no encoded-word Subject": "has an encoded-word Subject",
}


def raw_header_value(raw, name):
    """The raw, still-encoded value of the first header with this name."""
    head = re.split(rb"\r?\n\r?\n", raw, maxsplit=1)[0].decode("ascii", errors="replace")
    unfolded = re.sub(r"\r?\n(?=[ \t])", "", head)
    for line in re.split(r"\r?\n", unfolded):
        if line.lower().startswith(name.lower() + ":"):
            return " ".join(line.split(":", 1)[1].split())
    return None


def nice_path(path, corpus_dir):
    """A path relative to the corpus when inside it, else the absolute path."""
    rel = os.path.relpath(path, corpus_dir)
    if rel.startswith(".."):
        return os.path.abspath(path)
    return rel.replace(os.sep, "/")


# ---------------------------------------------------------------------------
# Corpus-wide checks
# ---------------------------------------------------------------------------

def check_ground_truth_files(ground_truth, data, report):
    for record_id in sorted(ground_truth):
        record = ground_truth[record_id]
        where = record.get("_source", "(ground truth)") + ":" + record_id
        if data.schema:
            clean = dict(record)
            clean.pop("_source", None)
            for error in schema_errors(clean, data.schema, "$"):
                report.fail(where, "gt.schema", error)
        if data.cat_verdict:
            category = record.get("category")
            if category not in data.cat_verdict:
                report.fail(where, "gt.category", "category " + str(category) + " is not in categories.json")
            elif data.cat_verdict[category] != record.get("verdict"):
                report.fail(where, "gt.verdict", "verdict " + str(record.get("verdict")) + " but categories.json maps "
                            + category + " to " + data.cat_verdict[category])
        spec_record = data.spec_records.get(record_id)
        if spec_record is None:
            if data.spec_records:
                report.fail(where, "gt.manifest", "no manifest record with this id")
            continue
        for key in ("set", "verdict", "category", "difficulty", "sender_address", "subject",
                    "escalate_expected", "recommended_action", "arrival_path"):
            if spec_record.get(key) != record.get(key):
                report.fail(where, "gt.manifest", key + " is " + repr(record.get(key)) + " in the ground truth but "
                            + repr(spec_record.get(key)) + " in the manifest")


def schema_errors(value, schema, path):
    """A small JSON Schema checker: type, enum, required, properties, items, pattern and sizes."""
    errors = []
    types = schema.get("type")
    if types is not None:
        if isinstance(types, str):
            types = [types]
        ok = False
        for kind in types:
            if json_type_ok(value, kind):
                ok = True
        if not ok:
            errors.append(path + ": expected type " + "/".join(types) + ", got " + type(value).__name__)
            return errors
    if "enum" in schema and value not in schema["enum"]:
        errors.append(path + ": " + repr(value) + " is not one of " + repr(schema["enum"]))
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(path + ": " + repr(value) + " does not match " + schema["pattern"])
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(path + ": longer than " + str(schema["maxLength"]))
        if schema.get("format") == "date-time" and parse_iso(value) is None:
            errors.append(path + ": not a date-time")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(path + ": below the minimum " + str(schema["minimum"]))
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(path + ": missing required key " + key)
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key in value:
            if key in properties:
                errors.extend(schema_errors(value[key], properties[key], path + "." + key))
            elif extra is False:
                errors.append(path + "." + key + ": not an allowed key")
            elif isinstance(extra, dict):
                errors.extend(schema_errors(value[key], extra, path + "." + key))
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(path + ": fewer than " + str(schema["minItems"]) + " items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(path + ": more than " + str(schema["maxItems"]) + " items")
        if schema.get("uniqueItems"):
            seen = set()
            for item in value:
                key = json.dumps(item, sort_keys=True)
                if key in seen:
                    errors.append(path + ": repeated item " + key[:60])
                seen.add(key)
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(schema_errors(item, schema["items"], path + "[" + str(index) + "]"))
    return errors


def json_type_ok(value, kind):
    if kind == "null":
        return value is None
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "string":
        return isinstance(value, str)
    if kind == "object":
        return isinstance(value, dict)
    if kind == "array":
        return isinstance(value, list)
    return True


def check_ids_and_files(contexts, ground_truth, data, report, default_emails_dir=True):
    by_stem = {}
    for ctx in contexts:
        by_stem[ctx["stem"]] = ctx
    if ground_truth:
        for record_id in sorted(ground_truth):
            record = ground_truth[record_id]
            ctx = by_stem.get(record_id)
            where = record.get("_source", "(ground truth)") + ":" + record_id
            if ctx is None:
                if record.get("set") == "exam":
                    report.warn(where, "corpus.ids", "exam-only record has no file under emails/ (exam emails ship in the instructor package)")
                else:
                    report.fail(where, "corpus.ids", "ground truth id has no .eml file")
                continue
            want = record.get("file")
            got = ctx["rel"]
            if got.endswith(".txt"):
                got = got[:-4]
            # nice_path() returns an absolute path for any file outside the corpus, so
            # pointed at a folder like instructor/exam-emails the comparison can never
            # be satisfied by any schema-legal value of the record's file field. The
            # field describes where the corpus keeps the file, and only the default
            # folder is the corpus, so the check runs only there.
            if want and want != got and default_emails_dir:
                report.warn(ctx["rel"], "corpus.ids", "ground truth file field is " + want + " but the file is at " + got)
        for stem in sorted(by_stem):
            if stem not in ground_truth:
                report.fail(by_stem[stem]["rel"], "corpus.ids", "no ground truth record has the id " + stem)
    elif data.spec_records:
        for stem in sorted(by_stem):
            if stem not in data.spec_records:
                report.fail(by_stem[stem]["rel"], "corpus.ids", "no manifest record has the id " + stem)
        missing = 0
        for record_id in data.spec_records:
            if record_id not in by_stem:
                missing += 1
        if missing and contexts:
            print("note: no ground truth file; " + str(missing) + " of " + str(len(data.spec_records))
                  + " manifest records have no .eml file yet")


def check_sample_manifest(contexts, corpus_dir, data, report):
    """spec/phase0-sample-manifest.json is the integrity record for the rendered files.

    It has to cover every rendered .eml under emails/ and nothing else, and
    every recorded byte count and digest has to equal the file on disk. Without
    this check the manifest can fall behind a render and say nothing: a file
    with no row has no recorded baseline at all, so the claim that it
    regenerates byte for byte from the seed has nothing to stand on.
    """
    rel = "spec/phase0-sample-manifest.json"
    path = os.path.join(corpus_dir, rel)
    if not os.path.exists(path):
        report.fail(rel, "corpus.manifest", "missing; the rendered files have no recorded byte count or digest")
        return
    try:
        manifest = load_json(path)
    except (OSError, ValueError) as error:
        report.fail(rel, "corpus.manifest", "could not read: " + str(error))
        return
    if not isinstance(manifest, dict) or not isinstance(manifest.get("emails"), list):
        report.fail(rel, "corpus.manifest", "has no emails list")
        return

    rows = {}
    for row in manifest["emails"]:
        row_id = row.get("id")
        if row_id is None:
            report.fail(rel, "corpus.manifest", "a row has no id")
            continue
        if row_id in rows:
            report.fail(rel, "corpus.manifest", "two rows carry the id " + row_id)
            continue
        rows[row_id] = row

    count = manifest.get("count")
    if count != len(manifest["emails"]):
        report.fail(rel, "corpus.manifest", "count is " + str(count) + " but the file holds "
                    + str(len(manifest["emails"])) + " row(s)")

    by_stem = {ctx["stem"]: ctx for ctx in contexts}
    for stem in sorted(by_stem):
        ctx = by_stem[stem]
        row = rows.get(stem)
        if row is None:
            report.fail(ctx["rel"], "corpus.manifest",
                        "rendered but absent from " + rel + "; it has no recorded byte count or digest")
            continue
        want_file = ctx["rel"]
        if want_file.endswith(".eml.txt"):
            want_file = want_file[:-4]
        if row.get("file") != want_file:
            report.fail(ctx["rel"], "corpus.manifest", rel + " records the path "
                        + str(row.get("file")) + " but the file is at " + want_file)
        raw = ctx.get("raw")
        if raw is None:
            continue
        if row.get("bytes") != len(raw):
            report.fail(ctx["rel"], "corpus.manifest", rel + " records " + str(row.get("bytes"))
                        + " bytes but the file is " + str(len(raw)) + " bytes")
        digest = hashlib.sha256(raw).hexdigest()
        if row.get("sha256") != digest:
            report.fail(ctx["rel"], "corpus.manifest", rel + " records sha256 "
                        + str(row.get("sha256")) + " but the file digests to " + digest)
        spec_record = data.spec_records.get(stem) if data else None
        if spec_record:
            for field in ("set", "category", "verdict", "difficulty"):
                if row.get(field) != spec_record.get(field):
                    report.fail(ctx["rel"], "corpus.manifest", rel + " records " + field + " "
                                + str(row.get(field)) + " but the manifest record says "
                                + str(spec_record.get(field)))

    for row_id in sorted(rows):
        if row_id not in by_stem:
            report.fail(rel, "corpus.manifest", "row " + row_id + " names no rendered .eml file")


def check_corpus_wide(contexts, report):
    seen_ids = {}
    temperror = 0
    permerror = 0
    for ctx in contexts:
        if ctx["parsed"] is None:
            continue
        message_id = ctx["parsed"]["message_id"]
        if message_id is not None:
            if message_id in seen_ids:
                report.fail(ctx["rel"], "corpus.message-id", "Message-ID " + message_id + " is also used by " + seen_ids[message_id])
            else:
                seen_ids[message_id] = ctx["rel"]
        results = ctx.get("auth_results", {})
        values = set()
        for method in results:
            values.add(results[method][0])
        if "temperror" in values:
            temperror += 1
        if "permerror" in values:
            permerror += 1
    if temperror > 2:
        report.fail("(corpus)", "corpus.auth", "temperror appears in " + str(temperror) + " messages; the limit is two")
    if permerror > 2:
        report.fail("(corpus)", "corpus.auth", "permerror appears in " + str(permerror) + " messages; the limit is two")


def check_dns(domains, report):
    """Ask the resolver about every domain; nothing may resolve."""
    if not domains:
        return
    dig = shutil.which("dig")
    checked = 0
    for domain in sorted(domains):
        if dig:
            try:
                done = subprocess.run([dig, "+time=2", "+tries=1", domain, "A"],
                                      capture_output=True, text=True, timeout=15)
            except (subprocess.TimeoutExpired, OSError) as error:
                report.warn("(corpus)", "corpus.dns", "dig failed (" + str(error) + "); name-resolution check skipped")
                return
            output = done.stdout + done.stderr
            if "no servers could be reached" in output or ("communications error" in output and "status:" not in output):
                report.warn("(corpus)", "corpus.dns", "resolver unreachable (offline?); name-resolution check skipped after "
                            + str(checked) + " domain(s)")
                return
            status = re.search(r"status: (\w+)", output)
            answers = re.search(r"ANSWER: (\d+)", output)
            checked += 1
            if status is None:
                report.warn("(corpus)", "corpus.dns", "could not read the dig answer for " + domain)
                continue
            if status.group(1) == "NXDOMAIN":
                continue
            if answers is not None and int(answers.group(1)) == 0:
                continue
            report.fail("(corpus)", "corpus.dns", domain + " resolves (" + status.group(1) + ", "
                        + (answers.group(1) if answers else "?") + " answer(s))")
        else:
            try:
                socket.getaddrinfo(domain, None)
                report.fail("(corpus)", "corpus.dns", domain + " resolves")
                checked += 1
            except socket.gaierror as error:
                if error.errno == socket.EAI_AGAIN:
                    report.warn("(corpus)", "corpus.dns", "temporary resolver failure (offline?); name-resolution check skipped after "
                                + str(checked) + " domain(s)")
                    return
                checked += 1
            except OSError as error:
                report.warn("(corpus)", "corpus.dns", "resolver error " + str(error) + "; name-resolution check skipped")
                return
    print("note: name-resolution check asked about " + str(checked) + " domain(s) with "
          + ("dig" if dig else "socket.getaddrinfo"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_file_checks(ctx, data, ground_truth, corpus_ids, tlds, report):
    check_bytes_and_lines(ctx, report)
    check_parse_defects(ctx, report)
    check_date(ctx, data, report)
    check_required_headers(ctx, report)
    check_thread_headers(ctx, data, report)
    check_return_path(ctx, report)
    check_received_chain(ctx, data, report)
    check_arrival_path(ctx, data, report)
    check_authentication_results(ctx, data, report)
    check_domains(ctx, data, tlds, report)
    check_ip_literals(ctx, report)
    check_mime(ctx, report)
    check_banner(ctx, report)
    check_removed_attachments(ctx, data, report)
    check_dkim(ctx, data, report)
    check_bulk_headers(ctx, data, report)
    check_data_files(ctx, data, report)
    check_record(ctx, data, ground_truth, corpus_ids, report)
    check_content_phrases(ctx, data, report)
    check_arc(ctx, report)


def main(argv):
    parser = argparse.ArgumentParser(description="Validate the synthetic email corpus.")
    parser.add_argument("--corpus", help="corpus folder (default: parent of this tools folder)")
    parser.add_argument("--emails", help="folder holding the .eml files (default: <corpus>/emails)")
    parser.add_argument("--ground-truth", help="ground truth file (default: <corpus>/ground_truth*.json)")
    parser.add_argument("--tld-list", help="use this copy of the IANA top-level-domain list "
                        "instead of the newest snapshot in <corpus>/data/tlds")
    parser.add_argument("--no-dns", action="store_true", help="skip the name-resolution check")
    parser.add_argument("--verbose", action="store_true", help="print a PASS line per clean file")
    args = parser.parse_args(argv)

    corpus_dir = os.path.abspath(args.corpus) if args.corpus else os.path.dirname(HERE)
    emails_dir = os.path.abspath(args.emails) if args.emails else os.path.join(corpus_dir, "emails")
    # The integrity manifest records paths under <corpus>/emails, so it only
    # describes the default folder. Pointed at any other folder the validator
    # says it skipped that check rather than reporting rows as missing files.
    default_emails_dir = os.path.normpath(emails_dir) == os.path.normpath(os.path.join(corpus_dir, "emails"))

    report = Report()
    data = Data(corpus_dir, report)
    ground_truth, gt_paths = load_ground_truth(corpus_dir, args.ground_truth, report)
    tlds = TldList(corpus_dir, args.tld_list, report)
    print("validate_corpus: " + tlds.describe(corpus_dir))

    files = find_eml_files(emails_dir)
    if not files:
        print("validate_corpus: no .eml files found under " + emails_dir + "; nothing to check")
    contexts = []
    for path in files:
        contexts.append(build_context(path, corpus_dir, report))

    corpus_ids = set()
    for ctx in contexts:
        if ctx["parsed"] is not None and ctx["parsed"]["message_id"] is not None:
            corpus_ids.add(ctx["parsed"]["message_id"])

    for ctx in contexts:
        if ctx["msg"] is None or ctx["parsed"] is None:
            continue
        run_file_checks(ctx, data, ground_truth, corpus_ids, tlds, report)
        if args.verbose and ctx["rel"] not in report.failed_files:
            print("PASS " + ctx["rel"])

    check_corpus_wide(contexts, report)
    if ground_truth:
        check_ground_truth_files(ground_truth, data, report)
    check_ids_and_files(contexts, ground_truth, data, report, default_emails_dir)
    if default_emails_dir:
        check_sample_manifest(contexts, corpus_dir, data, report)
    else:
        print("note: sample-manifest check skipped (--emails names a folder outside the corpus)")

    if args.no_dns:
        print("note: name-resolution check skipped (--no-dns)")
    else:
        domains = set()
        for ctx in contexts:
            domains.update(ctx["domains"])
        check_dns(domains, report)

    print("validate_corpus: " + str(len(files)) + " file(s), " + str(len(ground_truth)) + " ground truth record(s), "
          + str(len(report.failures)) + " failure(s), " + str(len(report.warnings)) + " warning(s)")
    if report.failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
