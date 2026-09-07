#!/usr/bin/env python3
"""
triage_tools.py: the three triage tools this course provides.

You do not write these three functions. They are provided, finished and
working, so that the agent you build has something real to call.

Three promises hold for all three tools:

    Provided.      The code is written for you. You read it and call it.
    Deterministic. The same input always gives the same output. There is no
                   model, no randomness, and no clock. Run a tool a hundred
                   times and you get the same answer a hundred times.
    Offline.       Nothing here touches the network. Every answer comes from
                   the JSON data files that ship with the course, which are
                   the security team's own records for this company.

The three tools:

    check_sender_reputation(sender)
        What the security team already knows about a sender. Pass either a
        whole address such as "support@fenwright-pay.example" or just the
        domain such as "fenwright-pay.example".

    check_urls(hosts)
        Whether each link host is allowed, blocked, internal, or on neither
        list. Pass a list of hosts. You get back one dictionary whose keys
        are the hosts you passed in.

    lookup_recipient(address)
        Who the message was sent to: their role, their flags, and how many
        suspicious messages they have reported before.

How to use them in a notebook:

    from triage_tools import check_sender_reputation, check_urls, lookup_recipient

    sender = check_sender_reputation("support@fenwright-pay.example")
    print(sender["status"])          # "unknown"
    print(sender["new_domain"])      # True

    links = check_urls(["my.fenwrightpay.example", "portal.pellgrave.example"])
    print(links["my.fenwrightpay.example"])   # "allowlisted"

    person = lookup_recipient("h.quintanilla@pellgrave.example")
    print(person["executive"])       # False

Three words the tools use, in plain language:

    allowlisted   The security team trusts this link host.
    blocklisted   The security team blocks this link host.
    unlisted      This link host is on neither list. That means unknown, not
                  clean. The playbook says to treat it as unknown.

Missing records never raise an error. When a sender has no record the tool
returns the usual keys with status "unknown". When a recipient has no record
the tool returns the usual keys with mailbox_type "unknown". A link host that
is on neither list returns "unlisted".

Only the Python standard library is used. Nothing needs to be installed.
"""

import json
import os
from datetime import date
from datetime import timedelta


# The folder this file sits in. Used to find the data files next to it.
HERE = os.path.dirname(os.path.abspath(__file__))

# An environment variable can point the tools at the data folder. The hosted
# notebook setup sets it. When it is not set, the tools look in the usual
# places instead.
DATA_DIR_VARIABLE = "TRIAGE_DATA_DIR"

# The data files these tools read. Every answer comes from one of them.
REPUTATION_FILE = "sender_reputation.json"
BLOCKLIST_FILE = "url_blocklist.json"
ALLOWLIST_FILE = "url_allowlist.json"
KNOWN_GOOD_FILE = "known_good_domains.json"
RECIPIENTS_FILE = "recipients.json"

# Files already read, so each file is read from disk only once.
_loaded_files = {}

# The data folder, once we have found it.
_data_directory = None


# ---------------------------------------------------------------------------
# Finding and reading the data files
# ---------------------------------------------------------------------------

def data_directory_candidates():
    """List the folders where the data files might be, best guess first."""
    candidates = []
    from_variable = os.environ.get(DATA_DIR_VARIABLE)
    if from_variable:
        candidates.append(from_variable)
    candidates.append(os.path.join(HERE, "data"))
    candidates.append(os.path.join(HERE, os.pardir, "data"))
    candidates.append(os.path.join(HERE, os.pardir, os.pardir, "corpus", "data"))
    candidates.append(os.path.join(os.getcwd(), "data"))
    candidates.append(os.path.join(os.getcwd(), "corpus", "data"))
    return candidates


def find_data_directory():
    """Return the folder that holds the JSON data files.

    A folder counts as the data folder when the sender reputation file is in
    it. The answer is remembered, so the search runs once.
    """
    global _data_directory
    if _data_directory is not None:
        return _data_directory
    for candidate in data_directory_candidates():
        folder = os.path.abspath(candidate)
        if os.path.exists(os.path.join(folder, REPUTATION_FILE)):
            _data_directory = folder
            return _data_directory
    # Nothing was found. Say where we looked, so the fix is obvious.
    places = ", ".join(data_directory_candidates())
    raise FileNotFoundError(
        "triage_tools could not find the course data files. Looked in: " + places)


def load_data_file(name):
    """Read one JSON data file and return it as a dictionary."""
    if name in _loaded_files:
        return _loaded_files[name]
    path = os.path.join(find_data_directory(), name)
    with open(path, encoding="utf-8") as handle:
        contents = json.load(handle)
    _loaded_files[name] = contents
    return contents


# ---------------------------------------------------------------------------
# Small helpers the three tools share
# ---------------------------------------------------------------------------

def clean_text(value):
    """Turn any input into a tidy lowercase string.

    Students paste addresses with stray spaces and capital letters. This makes
    every lookup behave the same way whatever arrives.
    """
    if value is None:
        return ""
    text = str(value).strip()
    text = text.strip("<>")
    return text.lower()


def domain_part(domain_or_address):
    """Return the domain of an address, or the text itself when it has no @."""
    text = clean_text(domain_or_address)
    if "@" in text:
        return text.split("@")[-1]
    else:
        return text


def organizational_domain(domain):
    """Return the last two labels of a domain.

    "news.inkmoor-office.example" becomes "inkmoor-office.example". Mail from a
    subdomain belongs to the organization that owns the domain above it, so a
    subdomain with no record of its own falls back to that record.
    """
    labels = domain.split(".")
    if len(labels) <= 2:
        return domain
    else:
        return labels[-2] + "." + labels[-1]


def is_new_domain(first_seen):
    """True when the gateway first saw this sender recently.

    "Recently" is the number of days the reputation file itself names, counted
    back from the fixed corpus clock in that same file. Nothing here reads
    today's date, so the answer never changes as time passes.
    """
    if not first_seen:
        return False
    reputation = load_data_file(REPUTATION_FILE)
    # The clock looks like "2026-04-29T09:00:00-05:00". The first ten
    # characters are the calendar day, which is all this rule needs.
    clock_day = date.fromisoformat(reputation["corpus_clock"][0:10])
    window_days = reputation["new_domain_days"]
    cutoff_day = clock_day - timedelta(days=window_days)
    first_seen_day = date.fromisoformat(first_seen)
    if first_seen_day >= cutoff_day:
        return True
    else:
        return False


def find_record(records, field, wanted):
    """Return the first record whose field equals wanted, or None."""
    for record in records:
        if clean_text(record.get(field)) == wanted:
            return record
    return None


# ---------------------------------------------------------------------------
# Tool 1: check_sender_reputation
# ---------------------------------------------------------------------------

def reputation_result(record, key_name, key_value, match_level):
    """Build the answer for a sender that does have a record.

    key_name is "address" when an address record matched and "domain" when a
    domain record matched. match_level says which lookup found it, so the agent
    can tell an exact address hit from a fallback to the domain above it.
    """
    result = {}
    result[key_name] = key_value
    result["status"] = record["status"]
    result["first_seen"] = record["first_seen"]
    result["messages_90d"] = record["messages_90d"]
    result["prior_reports"] = record["prior_reports"]
    result["last_report_verdict"] = record["last_report_verdict"]
    result["last_report_date"] = record["last_report_date"]
    result["campaign_tag"] = record["campaign_tag"]
    result["new_domain"] = is_new_domain(record["first_seen"])
    result["notes"] = record["notes"]
    result["match_level"] = match_level
    return result


def unknown_reputation_result(domain):
    """Build the answer for a sender with no record at all.

    The keys are the same as a found sender's keys. Only the values are empty.
    Code that reads the answer never has to check whether a record existed.
    """
    result = {}
    result["domain"] = domain
    result["status"] = "unknown"
    result["first_seen"] = None
    result["messages_90d"] = 0
    result["prior_reports"] = 0
    result["last_report_verdict"] = None
    result["last_report_date"] = None
    result["campaign_tag"] = None
    result["new_domain"] = False
    result["notes"] = "No reputation record for this sender."
    result["match_level"] = "none"
    return result


def check_sender_reputation(sender):
    """Return what the security team knows about a sender.

    The parameter is named `sender` because that is the name the code ledger
    fixes for it, and six notebooks are written against that contract. It was
    `domain_or_address` here, which described the value well and matched
    nothing else in the course, so a student calling it by keyword got a
    TypeError from a tool they never wrote.

    Pass a whole address or just a domain. Three lookups run in order, and the
    first one that finds a record wins:

        1. the exact address, so one bad mailbox at a normal provider can be
           marked bad without condemning the provider
        2. the exact domain
        3. the organizational domain, meaning the last two labels

    The returned "match_level" says which of the three matched: "address",
    "domain", "organizational_domain", or "none" when nothing matched.

    The status is one of internal, trusted, known_good, neutral, unknown or
    known_bad. Internal means the company's own domain.
    """
    reputation = load_data_file(REPUTATION_FILE)
    text = clean_text(sender)
    domain = domain_part(text)

    # 1. An exact address record beats every domain record.
    if "@" in text:
        record = find_record(reputation["addresses"], "address", text)
        if record is not None:
            return reputation_result(record, "address", text, "address")

    # 2. The exact domain.
    record = find_record(reputation["domains"], "domain", domain)
    if record is not None:
        return reputation_result(record, "domain", domain, "domain")

    # 3. The domain above it, for a sender on a subdomain.
    parent = organizational_domain(domain)
    if parent != domain:
        record = find_record(reputation["domains"], "domain", parent)
        if record is not None:
            return reputation_result(record, "domain", parent, "organizational_domain")

    # Nothing matched. Say so plainly instead of raising an error.
    return unknown_reputation_result(domain)


# ---------------------------------------------------------------------------
# Tool 2: check_urls
# ---------------------------------------------------------------------------

def host_list(hosts):
    """Return the hosts to check as a plain list.

    A list comes back unchanged. One host passed as a string is treated as a
    list holding that one host. None is treated as no hosts at all.
    """
    if hosts is None:
        return []
    if isinstance(hosts, str):
        return [hosts]
    return list(hosts)


def check_one_host(host):
    """Return the status of one link host.

    The order of the checks matters. Internal is decided first, because a
    company host is never a third party. Blocked is decided before allowed, so
    that a host somehow on both lists is still treated as blocked.
    """
    known_good = load_data_file(KNOWN_GOOD_FILE)
    text = clean_text(host)

    # Is it the company's own?
    if text == clean_text(known_good["organization"]):
        return "internal"
    if text.endswith(clean_text(known_good["internal_suffix"])):
        return "internal"
    for internal_host in known_good["internal_hosts"]:
        if text == clean_text(internal_host):
            return "internal"

    # Is it blocked?
    blocklist = load_data_file(BLOCKLIST_FILE)
    for entry in blocklist["hosts"]:
        if text == clean_text(entry["host"]):
            return "blocklisted"

    # Is it allowed?
    allowlist = load_data_file(ALLOWLIST_FILE)
    for entry in allowlist["hosts"]:
        if text == clean_text(entry["host"]):
            return "allowlisted"

    # On neither list. That is unknown, not clean. There is a data file named
    # url_unlisted.json, but this tool never reads it. A host is unlisted
    # because both lists were searched and neither held it.
    return "unlisted"


def check_urls(hosts):
    """Check a list of link hosts against the allowlist and the blocklist.

    Pass a list of hosts, for example the url_hosts that parse_eml found. You
    get back one dictionary. Its keys are the hosts you passed in, exactly as
    you passed them, and each value is one of:

        "internal"      a host belonging to this company
        "blocklisted"   a host the security team blocks
        "allowlisted"   a host the security team trusts
        "unlisted"      a host on neither list

    "unlisted" means the team has no opinion on this host. The playbook reads
    that as unknown, never as safe. A message with no links returns an empty
    dictionary, which is a fact about the message and not an error.
    """
    results = {}
    for host in host_list(hosts):
        results[host] = check_one_host(host)
    return results


# ---------------------------------------------------------------------------
# Tool 3: lookup_recipient
# ---------------------------------------------------------------------------

def campaign_tags_from(prior_reports):
    """Collect the campaign tags on a recipient's earlier reports.

    A campaign tag is the short name the security team gave to a run of
    similar messages, such as "ceo-impersonation". Repeats are dropped and the
    tags are sorted, so two mailboxes with the same history give the same list.
    """
    tags = []
    for report in prior_reports:
        tag = report.get("campaign_tag")
        if tag is not None and tag not in tags:
            tags.append(tag)
    tags.sort()
    return tags


def recipient_result(record):
    """Build the answer for a mailbox that does have a record."""
    result = {}
    result["address"] = record["address"]
    result["name"] = record["name"]
    result["role"] = record["role"]
    result["mailbox_type"] = record["mailbox_type"]
    result["executive"] = record["executive"]
    result["handles_payments"] = record["handles_payments"]
    result["chronic_reporter"] = record["chronic_reporter"]
    result["report_count_90d"] = record["report_count_90d"]
    result["true_positive_count_90d"] = record["true_positive_count_90d"]
    result["campaign_tags"] = campaign_tags_from(record["prior_reports"])
    return result


def unknown_recipient_result(address):
    """Build the answer for a mailbox with no record.

    Same keys as a found mailbox, empty values, and mailbox_type "unknown".
    """
    result = {}
    result["address"] = address
    result["name"] = None
    result["role"] = None
    result["mailbox_type"] = "unknown"
    result["executive"] = False
    result["handles_payments"] = False
    result["chronic_reporter"] = False
    result["report_count_90d"] = 0
    result["true_positive_count_90d"] = 0
    result["campaign_tags"] = []
    return result


def lookup_recipient(address):
    """Return the record for the mailbox a message was sent to.

    The answer carries three flags the playbook cares about. "executive" marks
    a leader, and the assistant who reads a leader's mail. "handles_payments"
    marks someone who can move money. "chronic_reporter" marks someone who
    reports a great deal, which is useful context and never a reason to
    dismiss a report.

    It also carries how many messages this mailbox reported in the last 90
    days, how many of those turned out to be real attacks, and the campaign
    tags on those earlier reports.
    """
    recipients = load_data_file(RECIPIENTS_FILE)
    text = clean_text(address)
    record = find_record(recipients["recipients"], "address", text)
    if record is not None:
        return recipient_result(record)
    else:
        return unknown_recipient_result(text)


# ---------------------------------------------------------------------------
# Running this file directly shows one example of each tool
# ---------------------------------------------------------------------------

def main():
    """Print one example call per tool, so the file can be run on its own."""
    print("data folder:", find_data_directory())
    print()
    print("check_sender_reputation('support@fenwright-pay.example')")
    print(json.dumps(check_sender_reputation("support@fenwright-pay.example"), indent=2))
    print()
    example_hosts = ["my.fenwrightpay.example", "portal.pellgrave.example"]
    print("check_urls(['my.fenwrightpay.example', 'portal.pellgrave.example'])")
    print(json.dumps(check_urls(example_hosts), indent=2))
    print()
    print("lookup_recipient('h.quintanilla@pellgrave.example')")
    print(json.dumps(lookup_recipient("h.quintanilla@pellgrave.example"), indent=2))


if __name__ == "__main__":
    main()
