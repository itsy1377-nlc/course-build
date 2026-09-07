#!/usr/bin/env python3
"""Recompute every derived field in spec/corpus-spec.json from the data files and fail on any mismatch.

Run from the repository root:
    python3 builder/corpus/tools/check_spec.py

The checks mirror the rules written in docs/phase0-corpus-design.md: the difficulty tier, the escalation
expectation and recommended action, the three week 4 tool results, list and reputation agreement, recipient
flags and the prior-similar-report rule, attachment stubs, injection markers, decoy isolation, an SPF record
for every MAIL FROM domain, tracking hosts, and prose hygiene. Exit status 1 means the spec must not be used
to generate .eml files until the listed problems are fixed.
"""
import datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


spec = load("spec/corpus-spec.json")
enums = load("spec/enums.json")
categories = load("spec/categories.json")
recipients = load("data/recipients.json")
reputation = load("data/sender_reputation.json")
allow = load("data/url_allowlist.json")
block = load("data/url_blocklist.json")
unlisted = load("data/url_unlisted.json")
known_good = load("data/known_good_domains.json")
attachments = load("data/attachments.json")
threads = load("data/known_threads.json")
policy = load("data/domain_policy.json")

ORG = spec["organization"]
CLOCK = datetime.date.fromisoformat(spec["corpus_clock"][:10])
NEW_DAYS = reputation["new_domain_days"]
VOCAB = {v["code"]: v["polarity"] for v in enums["indicator_vocabulary"]}
ASK = set(enums["ask_codes"])
PSR = enums["prior_similar_report_rule"]
CAT_VERDICT = {c["id"]: c["verdict"] for c in categories["categories"]}
RECIP = {r["address"]: r for r in recipients["recipients"]}
STORES = ("mailstore-01", "mailstore-02")
STORES_SEEN = {}
REP_DOM = {d["domain"]: d for d in reputation["domains"]}
REP_ADDR = {a["address"]: a for a in reputation["addresses"]}
ALLOW = {h["host"] for h in allow["hosts"]}
BLOCK = {h["host"] for h in block["hosts"]}
INTERNAL = set(known_good["internal_hosts"])
POLICY = {d["domain"]: d for d in policy["domains"]}
TRACKING = {h for d in policy["domains"] for h in d.get("tracking_hosts", [])}
ATT = {a["email_id"]: a for a in attachments["attachments"]}
DECOY_DOMAINS = {d["domain"] for d in reputation["domains"] if "(decoy)" in (d["notes"] or "")}
DECOY_HOSTS = {h["host"] for h in allow["hosts"] + block["hosts"] if "(decoy)" in h["reason"]}
DM = {c for c, p in VOCAB.items() if p == "DM"}
PM = {c for c, p in VOCAB.items() if p == "PM"}
PB = {c for c, p in VOCAB.items() if p == "PB"}
ESC_ORDER = enums["escalation_reason"]

problems = []


def bad(msg):
    problems.append(msg)


def split_ind(s):
    p = s.split(":", 2)
    return p[0] + ":" + p[1], (p[2] if len(p) > 2 else None)


def org_domain(host):
    return ".".join(host.split(".")[-2:])


def rep_lookup(address):
    if address in REP_ADDR:
        d = dict(REP_ADDR[address]); d["match_level"] = "address"; return d
    dom = address.split("@", 1)[1]
    for cand, level in ((dom, "domain"), (org_domain(dom), "organizational_domain")):
        if cand in REP_DOM:
            d = dict(REP_DOM[cand]); d["match_level"] = level; return d
    return {"status": "unknown", "match_level": "none", "new_domain": True, "first_seen": None}


def url_lookup(hosts):
    out = {}
    for h in hosts:
        if h in BLOCK: out[h] = "blocklisted"
        elif h in ALLOW: out[h] = "allowlisted"
        elif h in INTERNAL or h.endswith("." + ORG): out[h] = "internal"
        else: out[h] = "unlisted"
    return out


def prior_similar(rec, rep):
    """The campaign tag that makes recipient:prior_similar_report true, or None (rule in enums.json)."""
    cset = {split_ind(i)[0] for i in rec["indicators"]}
    implied = set()
    for code, tags in PSR["ask_to_campaign_tags"].items():
        if code in cset: implied.update(tags)
    if rep.get("campaign_tag") in PSR["sender_campaign_tags"]: implied.add(rep["campaign_tag"])
    held = {p["campaign_tag"] for p in RECIP[rec["recipient"]]["prior_reports"]}
    hits = [t for t in PSR["value_order"] if t in implied and t in held]
    return hits[0] if hits else None


def tier(rec):
    cs = [split_ind(i)[0] for i in rec["indicators"]]
    cset = set(cs)
    has_ask = bool(cset & ASK)
    if rec["verdict"] == "malicious":
        decisive = sum(1 for c in cs if c in DM)
        pressure = sum(1 for c in cs if c in PM) + (1 if {"url:none", "attachment:none"} <= cset else 0)
    else:
        decisive = 0
        if "sender:internal_domain" in cset and rec["arrival_path"] == "internal":
            decisive += 1 + (1 if "thread:in_reply_to_known" in cset else 0)
        if ({"sender:allowlisted_domain", "sender:known_good"} & cset) and rec["auth"]["dmarc"] == "pass":
            decisive += 1
        if "header:list_headers_present" in cset and not has_ask:
            decisive += 1
        for i in rec["indicators"]:
            c, v = split_ind(i)
            if c == "header:spam_score" and float(v) >= 5.0 and not has_ask:
                decisive += 1
        pressure = sum(1 for c in cs if c in PB)
    base = 2 if (decisive == 0 or pressure > decisive) else (0 if pressure == 0 else 1)
    steps = base + (1 if rec["injection"] else 0)
    opposite = {"malicious": "benign", "benign": "malicious"}[rec["verdict"]]
    steps += 1 if rec["body_only_read"] == opposite else 0
    return ["easy", "medium", "hard"][min(steps, 2)]


def escalation(rec, rep):
    cset = {split_ind(i)[0] for i in rec["indicators"]}
    reasons = []
    if rec["injection"]:
        reasons.append("injection_detected")
    recip = RECIP[rec["recipient"]]
    if rec["verdict"] == "malicious":
        if rec["category"] in ("bec", "vendor_fraud", "malware_delivery"): reasons.append("financial_or_endpoint_impact")
        if recip["executive"]: reasons.append("executive_target")
        if "recipient:reported_after_interaction" in cset: reasons.append("user_interacted")
        if "sender:internal_domain_via_external_path" in cset: reasons.append("org_domain_forged")
        if rec["auth"]["dmarc"] == "pass" and ({"sender:known_good", "sender:allowlisted_domain"} & cset): reasons.append("partner_account_compromise")
        if "header:webmail_submission_external_ip" in cset: reasons.append("internal_account_compromise")
        reasons = [r for r in ESC_ORDER if r in reasons]
        return bool(reasons), reasons, ("escalate_incident" if reasons else "block_and_purge")
    if rec["category"] == "spam":
        return bool(reasons), reasons, "close_spam_reply_to_reporter"
    if rec["auth"]["dmarc"] == "fail" and ({"sender:known_good", "sender:allowlisted_domain"} & cset): reasons.append("auth_failure_on_trusted_sender")
    if cset & {"content:payment_change_request", "content:payment_timing_request", "content:banking_instruction"}: reasons.append("callback_verification")
    if rep["status"] == "unknown" and "content:data_request" in cset: reasons.append("unknown_sender_asks_for_data")
    reasons = [r for r in ESC_ORDER if r in reasons]
    return bool(reasons), reasons, ("verify_out_of_band_then_close" if reasons else "close_benign_reply_to_reporter")


ids = [e["id"] for e in spec["emails"]]
if len(ids) != len(set(ids)): bad("duplicate ids")
used = set()
for n, rec in enumerate(spec["emails"], 1):
    rid = rec["id"]
    if int(rid[:3]) != n: bad(f"{rid}: out of sequence")
    if CAT_VERDICT.get(rec["category"]) != rec["verdict"]: bad(f"{rid}: category and verdict disagree")
    cset = {split_ind(i)[0] for i in rec["indicators"]}
    for c in cset:
        if c not in VOCAB: bad(f"{rid}: unknown indicator {c}")
    for c in rec["required_indicators"]:
        if c not in cset: bad(f"{rid}: required indicator {c} absent")
    rep = rep_lookup(rec["sender_address"])
    if rep["match_level"] == "none": bad(f"{rid}: sender has no reputation record")
    if rec["tool_expectations"]["check_sender_reputation"]["status"] != rep["status"]: bad(f"{rid}: reputation expectation stale")
    st = rep["status"]
    from_dom = rec["sender_address"].split("@")[1]
    for code, want in (("sender:known_bad", st == "known_bad"), ("sender:allowlisted_domain", st == "trusted"), ("sender:known_good", st == "known_good"),
                       ("sender:first_seen", bool(rep.get("new_domain")) and st not in ("known_bad", "internal")), ("sender:internal_domain", st == "internal" and rec["arrival_path"] == "internal")):
        if (code in cset) != want: bad(f"{rid}: {code} disagrees with sender_reputation.json")
    urls = url_lookup(rec["url_hosts"])
    if rec["tool_expectations"]["check_urls"] != urls: bad(f"{rid}: url expectation stale")
    for h, s in urls.items():
        want = {"blocklisted": "url:host_blocklisted", "allowlisted": "url:host_allowlisted", "unlisted": "url:host_unlisted", "internal": "url:host_internal_known_good"}[s]
        if f"{want}:{h}" not in rec["indicators"]: bad(f"{rid}: missing {want}:{h}")
        if s == "unlisted" and h not in unlisted["hosts"]: bad(f"{rid}: {h} unlisted but not in url_unlisted.json")
    for h in rec["url_hosts"]:
        if (f"url:tracking_host:{h}" in rec["indicators"]) != (h in TRACKING): bad(f"{rid}: url:tracking_host:{h} disagrees with tracking_hosts in domain_policy.json")
    for i in rec["indicators"]:
        if i.startswith("url:tracking_host:") and split_ind(i)[1] not in rec["url_hosts"]: bad(f"{rid}: {i} names a host outside url_hosts")
    if rec["arrival_path"] != "internal" and rec["auth"]["spf"] not in (None, "none"):
        # SPF is evaluated on the MAIL FROM domain and a record never covers subdomains, so that exact domain needs one
        m = re.search(r"Return-Path <([^>]+)>", rec["received_path_hint"])
        mailfrom = (m.group(1) if m else rec["sender_address"]).split("@")[1]
        if mailfrom not in POLICY or POLICY[mailfrom]["spf"] is None: bad(f"{rid}: MAIL FROM domain {mailfrom} has no SPF record in domain_policy.json")
    if rec["recipient"] not in RECIP: bad(f"{rid}: recipient missing")
    else:
        r = RECIP[rec["recipient"]]
        for code, want in (("recipient:executive", r["executive"]), ("recipient:handles_payments", r["handles_payments"]), ("recipient:chronic_reporter", r["chronic_reporter"]),
                           ("recipient:distribution_list", r["mailbox_type"] == "list"), ("recipient:shared_mailbox", r["mailbox_type"] == "shared")):
            if (code in cset) != bool(want): bad(f"{rid}: {code} disagrees with recipients.json")
        psr = prior_similar(rec, rep)
        if ("recipient:prior_similar_report" in cset) != bool(psr): bad(f"{rid}: recipient:prior_similar_report disagrees with the rule (rule gives {psr})")
        for i in rec["indicators"]:
            c, v = split_ind(i)
            if c == "recipient:prior_similar_report" and v is not None and v != psr: bad(f"{rid}: recipient:prior_similar_report value {v} but the rule gives {psr}")
        # The week 4 lookup_recipient result is copied from recipients.json, so it has to equal a fresh lookup
        lr = rec["tool_expectations"].get("lookup_recipient")
        if lr is not None:
            if lr.get("address") != rec["recipient"]: bad(f"{rid}: lookup_recipient expectation names {lr.get('address')} but the recipient is {rec['recipient']}")
            for key in ("name", "role", "mailbox_type", "executive", "handles_payments", "chronic_reporter", "report_count_90d", "true_positive_count_90d"):
                if lr.get(key) != r.get(key): bad(f"{rid}: lookup_recipient {key} is {lr.get(key)} but recipients.json says {r.get(key)}")
            tags = sorted({p["campaign_tag"] for p in r["prior_reports"]})
            if sorted(lr.get("campaign_tags") or []) != tags: bad(f"{rid}: lookup_recipient campaign_tags {lr.get('campaign_tags')} but recipients.json holds {tags}")
    # A mailbox lives on exactly one mail store, so the LMTP hop follows the mailbox the copy was delivered to,
    # never the arrival path. A distribution list is not a mailbox: it expands at the submission host and every
    # member's store takes a copy, so the file the corpus keeps is the copy in the reporter's mailbox and the hop
    # names the reporter's store while To stays the list address.
    delivered = rec["reporter"] if (RECIP.get(rec["recipient"]) or {}).get("mailbox_type") == "list" else rec["recipient"]
    want_store = (RECIP.get(delivered) or {}).get("mailstore")
    found_store = re.search(r"mailstore-\d+", rec["received_path_hint"] or "")
    if found_store: STORES_SEEN.setdefault(delivered, set()).add(found_store.group(0))
    if delivered in RECIP and want_store is None: bad(f"{rid}: mailbox {delivered} has no mailstore in recipients.json")
    elif not found_store: bad(f"{rid}: received_path_hint names no mailstore host for the LMTP hop")
    elif want_store is not None and found_store.group(0) != want_store:
        bad(f"{rid}: delivered by {found_store.group(0)} but recipients.json puts {delivered} on {want_store}")
    if rec["reporter"] not in RECIP or RECIP[rec["reporter"]]["mailbox_type"] != "person": bad(f"{rid}: reporter must be a named person")
    att = rec["attachment"]
    if att:
        a = ATT.get(rid)
        if not a or a["filename"] != att["filename"] or a["sha256"] != att["sha256"] or a["size"] != att["size"]: bad(f"{rid}: attachment stub disagrees with attachments.json")
    elif rid in ATT: bad(f"{rid}: attachments.json has an entry but the spec has none")
    if bool(rec["injection"]) != ("content:instruction_to_ai" in cset): bad(f"{rid}: injection marker mismatch")
    if rec["injection"] and rec["verdict"] != "malicious": bad(f"{rid}: injection on a benign email")
    if rec["arrival_path"] == "internal":
        if any(v is not None for v in rec["auth"].values()): bad(f"{rid}: internal path with authentication results")
    else:
        pol = POLICY.get(from_dom) or POLICY.get(org_domain(from_dom))
        if not pol: bad(f"{rid}: From domain not in domain_policy.json")
        else:
            if rec["auth"]["dmarc"] == "fail" and pol["dmarc_policy"] is None: bad(f"{rid}: dmarc fail without a published policy")
            if rec["auth"]["dmarc"] == "none" and pol["dmarc_policy"] is not None: bad(f"{rid}: dmarc none but a policy exists")
        if rec["auth"]["dmarc"] == "pass" and "pass" not in (rec["auth"]["spf"], rec["auth"]["dkim"]): bad(f"{rid}: dmarc pass needs an aligned pass")
    t = tier(rec)
    if t != rec["difficulty"]: bad(f"{rid}: difficulty {rec['difficulty']} but the rule gives {t}")
    esc, reasons, action = escalation(rec, rep)
    if esc != rec["escalate_expected"] or reasons != rec["escalation_reasons"] or action != rec["recommended_action"]:
        bad(f"{rid}: escalation {rec['escalate_expected']}/{rec['escalation_reasons']}/{rec['recommended_action']} but the rule gives {esc}/{reasons}/{action}")
    if rec["set"] == "batch" and rec["weeks"] != [7]: bad(f"{rid}: batch email outside week 7")
    if rec["set"] == "exam" and rec["weeks"] != [8]: bad(f"{rid}: exam email outside week 8")
    if rec["set"] == "teaching" and not all(1 <= w <= 6 for w in rec["weeks"]): bad(f"{rid}: teaching email outside weeks 1 to 6")
    for fld in ("lure_summary", "reference_summary"):
        if len([s for s in re.split(r"(?<=[.!?])\s+", rec[fld].strip()) if s]) != 2: bad(f"{rid}: {fld} is not two sentences")
    used.add(from_dom); used.update(rec["url_hosts"])
    if rec["reply_to"]: used.add(rec["reply_to"].split("@")[1])

# Recipient report counts are recomputed from the prior_reports list rather than trusted.
# The design defines both columns as the reports the employee filed that were closed
# before the corpus window opened, so every entry has to sit before the window start and
# the two counts are the length of that list and the true positives inside it. The field
# names still say 90d; the window that actually governs the data is this one.
WINDOW_START = datetime.date.fromisoformat(spec["corpus_window"]["start"])
for r in recipients["recipients"]:
    reports = r.get("prior_reports") or []
    if r["report_count_90d"] != len(reports):
        bad(f"{r['address']}: report_count_90d is {r['report_count_90d']} but prior_reports holds {len(reports)}")
    positives = sum(1 for p in reports if p["outcome"] == "true_positive")
    if r["true_positive_count_90d"] != positives:
        bad(f"{r['address']}: true_positive_count_90d is {r['true_positive_count_90d']} but prior_reports holds {positives}")
    for p in reports:
        if datetime.date.fromisoformat(p["date"]) >= WINDOW_START:
            bad(f"{r['address']}: prior report {p['date']} is not closed before the corpus window opens on {WINDOW_START}")
    dates = [p["date"] for p in reports]
    if dates != sorted(dates):
        bad(f"{r['address']}: prior_reports are not in date order")


# ---------------------------------------------------------------------------
# Every message_ref in the data files is a Message-ID a parser can read
# ---------------------------------------------------------------------------
#
# docs/email-header-realism.md section 1 fixes the field: a Message-ID is
# "<id-left@id-right>" with id-right a host the generator controls, and the
# convention on top of that, written just under the example header, is a UTC
# timestamp of 14 digits, a dot, and twelve hex digits. Section 10 rule 4
# enforces it on every rendered .eml, so a student who writes a parser against
# the corpus writes it against that grammar.
#
# The prior report entries in recipients.json carry Message-IDs too. They name
# messages that sit in the fictional mail store rather than in the corpus, so
# no .eml was ever written for them and section 10 never saw them. That is how
# all 56 of them came to hold a 13 digit stamp, an hour written "1" instead of
# "01", which no parser can read as a time. lookup_recipient hands these
# records to students, so the grammar has to hold here exactly as it holds in
# a header.
#
# The rules below apply to every message_ref anywhere in the data files,
# whatever the file and however deeply nested, and to the message_id values in
# known_threads.json, which are the parents In-Reply-To resolves to:
#
#   1. the value matches the Message-ID grammar, stamp and hex id and host;
#   2. the stamp is a real UTC date and time, so hour 25 or 20260231 fails;
#   3. where the entry carries its own date, the stamp agrees with it: a plain
#      date has to be the stamp's date, and a date with an offset has to be
#      the stamp itself once converted to UTC;
#   4. no message_ref is a Message-ID the corpus ships, because a prior report
#      is a different message from anything in emails/ or known_threads.json.

MESSAGE_ID_GRAMMAR = re.compile(r"^<(\d{14})\.[0-9a-f]{12}@[a-z0-9][a-z0-9.-]*\.example>$")


def find_refs(node, where, found):
    """Collect every message_ref and message_id string under one loaded file."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("message_ref", "message_id") and isinstance(value, str):
                found.append((where + "." + key, key, value, node))
            else:
                find_refs(value, where + "." + key, found)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            find_refs(item, where + "[" + str(index) + "]", found)


SHIPPED = {t["message_id"] for t in threads["threads"]}
SHIPPED.update(e["message_id"] for e in spec["emails"] if e.get("message_id"))
EML_DIR = os.path.join(ROOT, "emails")
if os.path.isdir(EML_DIR):
    for folder, _, names in os.walk(EML_DIR):
        for name in sorted(names):
            if not name.endswith(".eml"):
                continue
            with open(os.path.join(folder, name), encoding="utf-8", errors="replace") as f:
                SHIPPED.update(m.group(1) for m in
                               re.finditer(r"(?im)^message-id:[ \t]*(<[^>\s]+>)", f.read()))

DATA_DIR = os.path.join(ROOT, "data")
refs = []
for name in sorted(os.listdir(DATA_DIR)):
    if name.endswith(".json"):
        find_refs(load("data/" + name), "data/" + name, refs)
for where, key, ref, holder in refs:
    match = MESSAGE_ID_GRAMMAR.match(ref)
    if not match:
        bad(f"{where}: {ref} is not a Message-ID; the grammar is "
            f"<14 digit UTC stamp>.<12 hex digits>@<host>.example")
        continue
    try:
        stamp = datetime.datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
    except ValueError:
        bad(f"{where}: {ref} carries {match.group(1)}, which is not a UTC date and time")
        continue
    if key == "message_ref" and ref in SHIPPED:
        bad(f"{where}: {ref} is a Message-ID the corpus ships; a prior report names a "
            f"message that is not in the corpus")
    own = holder.get("date")
    if not isinstance(own, str):
        continue
    if len(own) == 10:
        if stamp.date().isoformat() != own:
            bad(f"{where}: {ref} is stamped {stamp.date().isoformat()} but the record is "
                f"dated {own}")
    else:
        try:
            local = datetime.datetime.fromisoformat(own)
        except ValueError:
            continue
        if local.utcoffset() is None:
            continue
        utc = (local - local.utcoffset()).replace(tzinfo=None)
        if stamp != utc:
            bad(f"{where}: {ref} is stamped {stamp:%Y%m%d%H%M%S} but {own} is "
                f"{utc:%Y%m%d%H%M%S} in UTC")


for address, stores in sorted(STORES_SEEN.items()):
    if len(stores) > 1: bad(f"{address}: delivered to {' and '.join(sorted(stores))}; a mailbox lives on exactly one mail store")
for r in recipients["recipients"]:
    if r.get("mailstore") not in STORES: bad(f"{r['address']}: mailstore is {r.get('mailstore')}; must name a Sentrywick Store host")
for d in DECOY_DOMAINS:
    if any(u == d or u.endswith("." + d) for u in used): bad(f"decoy domain {d} appears in the corpus")
for h in DECOY_HOSTS:
    if h in used: bad(f"decoy host {h} appears in the corpus")
batch = [e for e in spec["emails"] if e["set"] == "batch"]
if len(batch) != 20 or sum(1 for e in batch if e["verdict"] == "malicious") != 10: bad("batch is not 20 emails split 10 and 10")
for t in threads["threads"]:
    if any(t["message_id"] == e.get("message_id") for e in spec["emails"]): bad("known thread duplicates a corpus message")
for rel in ("spec/corpus-spec.json", "spec/enums.json", "spec/categories.json", "spec/ground_truth.schema.json", "data/playbook.md", "README.md"):
    p = os.path.join(ROOT, rel)
    if os.path.exists(p):
        txt = open(p, encoding="utf-8").read()
        if "\u2014" in txt or "\u2013" in txt: bad(f"{rel}: contains a dash character")
        if "TODO" in txt: bad(f"{rel}: contains TODO")
pb = os.path.join(ROOT, "data/playbook.md")
if os.path.exists(pb):
    words = len(open(pb, encoding="utf-8").read().split())
    if words > 250: bad(f"playbook.md is {words} words; limit 250")

# ---------------------------------------------------------------------------
# The decisive-fact list written in prose has to name the facts the tier rule scored
# ---------------------------------------------------------------------------
#
# Section 5.2 of the design fixes which indicator codes are decisive for a
# malicious verdict: the codes carrying polarity DM in enums.json. The tier
# rule counts those codes and nothing else, so difficulty_derivation.decisive
# is right whenever the indicator list is right, and the rule above already
# checks that. What nothing checked is the sentence a reader actually reads.
# A record can score three decisive facts and then name a different three in
# its notes, and every automated check still passes, because no check read the
# prose. That is how an anchor record came to tell students that a content
# phrase is decisive for malicious when its polarity is PB, pressure against a
# benign verdict, and the tier rule never counts it toward a malicious tier.
#
# So: wherever a ground truth record for a malicious email writes a decisive
# fact list in the form "<number> decisive facts (a, b, c)", every item in the
# parentheses has to resolve to an indicator code, that code has to carry
# polarity DM, it has to be in the record's own indicator list, and the items
# together have to be exactly the DM codes the tier rule counted.
#
# Benign records are outside this check. Their decisive facts are the derived
# combinations in section 5.2 (the internal domain on the internal path, an
# allowlisted sender with dmarc=pass, bulk list headers with no ask, a spam
# score at or above 5.0 with no ask), not single DM codes, so there is nothing
# for a code resolver to resolve.
#
# An item resolves either by naming its code outright, which is what most
# records do, or by matching a cue below. A cue is a set of words that all have
# to be in the item. The cues cover the DM codes and the codes most easily
# mistaken for them, so a wrong item fails on its polarity with the code named
# rather than falling through as unreadable. An item that matches nothing is a
# failure too: prose the checker cannot read is prose that can drift again, and
# the fix is to write the item the way the cues expect or to add a cue here.

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
DECISIVE_LIST = re.compile(r"\b(one|two|three|four|five|six)\s+decisive\s+"
                           r"(?:malicious\s+|benign\s+)?facts?\s*\(([^)]*)\)", re.I)
CODE_TOKEN = re.compile(r"\b([a-z]+:[a-z_]+)\b")

CUES = {
    # decisive for a malicious verdict (polarity DM)
    "sender:lookalike_domain": [("lookalike", "domain"), ("lookalike", "from")],
    "sender:display_name_matches_employee": [("display name", "employee"),
                                             ("employee", "name", "address")],
    "sender:display_name_claims_org": [("display name", "organization"),
                                       ("display name", "the org")],
    "sender:display_name_claims_vendor": [("display name", "vendor")],
    "sender:display_name_claims_internal_system": [("display name", "internal system"),
                                                   ("display name", "gateway")],
    "sender:internal_domain_via_external_path": [("internal domain", "external"),
                                                 ("own domain", "external"),
                                                 ("org domain", "external")],
    "sender:known_bad": [("known bad",), ("bad reputation",)],
    "sender:reply_to_lookalike_domain": [("reply-to", "lookalike")],
    "url:lookalike_host": [("lookalike", "host"), ("lookalike", "link")],
    "url:subdomain_trick": [("subdomain trick",), ("subdomain", "link")],
    "url:host_blocklisted": [("blocklist",)],
    "attachment:blocked_extension": [("blocked extension",), ("attachment", "extension")],
    "attachment:macro_detected": [("macro",)],
    "thread:in_reply_to_unknown": [("in-reply-to", "unknown"), ("reply", "unknown thread")],
    "header:forged_gateway_header": [("forged", "gateway")],
    "header:webmail_submission_external_ip": [("webmail", "external"), ("webmail submission",)],
    "auth:dmarc_fail_owned_domain": [("dmarc", "fail")],
    # not decisive; here so a wrong item fails on polarity with its code named
    "content:credential_request": [("credential ask",), ("credential request",),
                                   ("ask for credentials",), ("asks to sign in",),
                                   ("sign-in ask",)],
    "content:urgency_keywords": [("urgency",)],
    "content:payment_request": [("payment request",), ("payment ask",)],
    "content:payment_change_request": [("payment change",), ("change of bank",)],
    "content:payment_timing_request": [("payment timing",)],
    "content:banking_instruction": [("banking instruction",), ("bank details",)],
    "content:data_request": [("data request",), ("data ask",)],
    "content:gift_card_request": [("gift card",)],
    "content:secrecy_request": [("secrecy",)],
    "content:instruction_to_ai": [("injection",), ("instruction to the model",)],
    "auth:all_pass": [("all pass",), ("authentication passes",), ("three checks pass",)],
    "sender:first_seen": [("first seen",), ("new domain",)],
    "sender:freemail_domain": [("freemail",), ("consumer webmail",)],
    "url:host_unlisted": [("unlisted",)],
    "url:login_path": [("login path",)],
    "header:x_priority_high": [("x-priority",), ("high priority",)],
    "header:external_flag": [("external flag",), ("external banner",)],
}
for cue_code in CUES:
    if cue_code not in VOCAB:
        bad(f"check_spec: cue table names {cue_code}, which is not in the indicator vocabulary")


def normalize_item(text):
    text = " ".join(text.strip().lower().split())
    text = text.replace("look-alike", "lookalike").replace("look alike", "lookalike")
    for lead in ("the ", "an ", "a "):
        if text.startswith(lead):
            text = text[len(lead):]
    return text


def split_items(inner):
    parts = []
    for chunk in inner.split(","):
        for piece in re.split(r"\s+and\s+", chunk):
            piece = normalize_item(piece)
            if piece:
                parts.append(piece)
    return parts


def resolve_item(item):
    """The indicator code an item names, or None. Ambiguity is not a resolution."""
    named = CODE_TOKEN.search(item)
    if named and named.group(1) in VOCAB:
        return named.group(1)
    hits = []
    for code, cues in CUES.items():
        best = 0
        for cue in cues:
            if all(word in item for word in cue):
                best = max(best, sum(len(word) for word in cue))
        if best:
            hits.append((best, code))
    if not hits:
        return None
    hits.sort(reverse=True)
    if len(hits) > 1 and hits[0][0] == hits[1][0]:
        return None
    return hits[0][1]


gt_path = os.path.join(ROOT, "ground_truth.json")
if os.path.exists(gt_path):
    truth = load("ground_truth.json")
    spec_by_id = {e["id"]: e for e in spec["emails"]}
    for rec in truth["emails"]:
        rid = rec["id"]
        if rec.get("verdict") != "malicious":
            continue
        match = DECISIVE_LIST.search(rec.get("notes") or "")
        if not match:
            continue
        manifest_rec = spec_by_id.get(rid)
        if manifest_rec is None:
            bad(f"{rid}: ground truth record has no manifest record")
            continue
        claimed = NUMBER_WORDS[match.group(1).lower()]
        scored = manifest_rec["difficulty_derivation"]["decisive"]
        if claimed != scored:
            bad(f"{rid}: notes say {claimed} decisive fact(s) but the tier rule scored {scored}")
        items = split_items(match.group(2))
        resolved = []
        for item in items:
            code = resolve_item(item)
            if code is None:
                bad(f"{rid}: notes name the decisive fact '{item}', which resolves to no "
                    f"indicator code; write it the way the cue table in check_spec.py expects "
                    f"or add a cue")
                continue
            if VOCAB[code] != "DM":
                bad(f"{rid}: notes call '{item}' a decisive fact, but that is {code}, "
                    f"polarity {VOCAB[code]}; only DM codes are decisive for a malicious verdict")
                continue
            if code not in {split_ind(i)[0] for i in manifest_rec["indicators"]}:
                bad(f"{rid}: notes name {code} as a decisive fact but the indicator list has no such code")
                continue
            resolved.append(code)
        scored_codes = [split_ind(i)[0] for i in manifest_rec["indicators"]
                        if split_ind(i)[0] in DM]
        if len(resolved) == len(items) and sorted(resolved) != sorted(scored_codes):
            bad(f"{rid}: notes name the decisive facts {sorted(resolved)} but the tier rule "
                f"counted {sorted(scored_codes)}")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"check_spec: {len(spec['emails'])} records, all rules hold")
