# ITSY-1377-000 synthetic email corpus

This folder holds the fake email set for the course "Agentic AI and Security Operations." Students build a phishing triage agent over seven weeks. Every email that agent reads comes from here.

Nothing in the corpus is real. The company, Pellgrave Mechanical Group at `pellgrave.example`, is invented. So are its people, its vendors, the attackers, the mail gateway product, and every domain, address and file name. Every domain ends in `.example`. That ending is reserved for documentation and never resolves.

## License

License to be set by the college; see the course risk register. Until then the files are course material for Northeast Lakeview College and carry no other license statement.

## Layout

```
corpus/
  README.md                       this file
  ground_truth.json               ground truth for the rendered emails (Phase 0: the six sample records)
  spec/
    corpus-spec.json              the manifest: one record per planned email (56), the single source of truth
    enums.json                    every enumerated value and the indicator vocabulary with polarity
    categories.json               the seven categories, their definitions and the verdict each maps to
    ground_truth.schema.json      JSON Schema (draft 2020-12) for ground truth records
    phase0-sample-manifest.json   every rendered .eml file with its byte count and sha256 digest
  data/
    known_good_domains.json       the organization and its internal hosts (the week 3 list)
    url_allowlist.json            trusted link hosts, with decoys
    url_blocklist.json            blocked link hosts, with decoys
    url_unlisted.json             corpus hosts that are deliberately on neither list
    sender_reputation.json        domain and address reputation records, with decoys
    recipients.json               employees, shared mailboxes and lists, with flags and prior reports
    display_names.json            the names table the week 3 display-name check reads, with decoys
    attachments.json              every stub attachment: filename, size, synthetic sha256, what the gateway did
    known_threads.json            Message-IDs of earlier messages the corpus replies to
    domain_policy.json            every domain with its owner class and DMARC policy
    playbook.md                   the playbook excerpt the week 3 prompt carries (under 250 words)
  tools/
    parse_eml.py                  the pre-written helper the week 1 notebook imports
    validate_corpus.py            checks every .eml file against the header specification
    check_spec.py                 recomputes every derived field and fails on any mismatch
    gen_sample_manifest.py        rebuilds spec/phase0-sample-manifest.json from the rendered files
  emails/
    teaching/                     .eml files used in weeks 1 to 6 (Phase 0: five of the six sample files)
    batch/                        .eml files for the week 7 batch (Phase 0: one sample file, 032; the rest arrive with the full build)
```

Exam-only emails go into the instructor package, never into `emails/`.

## How the manifest becomes emails

`spec/corpus-spec.json` describes each email. It says who sent it, to whom, and when. It says what the headers show and what the body must contain (`body_brief`). It lists the facts an extractor will find (`indicators`), what each week 4 tool returns (`tool_expectations`), and the path the week 5 loop should take (`expected_loop`). It carries the labels a student's output is graded against: `verdict`, `category`, `difficulty`, `escalate_expected`, `recommended_action` and `reference_summary`.

A generator turns each record into a `.eml` file. The header rules are in `docs/email-header-realism.md`. Two checks run on every build: `tools/validate_corpus.py` on the files and `tools/check_spec.py` on the manifest and data files. A file that fails either check does not ship.

## How ground truth is used

Ground truth comes in three files with different release times. `ground_truth_teaching.json` goes in the instructor package and the weekly answer keys. `ground_truth_batch.json` is released with the week 7 page, because nothing in the course locks. `ground_truth_exam.json` stays in the instructor package. Each record follows `spec/ground_truth.schema.json`.

Week 7 scores the verdict first, with false positives and false negatives counted apart. It reports escalation agreement on a separate line. A triage note earns partial credit on indicators when it names the `required_indicators`. The `reference_summary` is the model answer for the two-sentence plain-language summary.

## Safety statement

Every file is plain text: seven-bit bytes, two text parts, no attachment parts, no base64, no scripts, no images. An attachment exists only as a header line with a filename, a size and a digest. The digest was computed from a seed string, never from a file. Every domain is under `.example`. Every address sits in a documentation or private block. No URL resolves.

No person, company, product, phone number or place in the corpus is real. The organization, vendor, provider, attacker and gateway product names were checked by web search before use. Open `.eml` files in a text editor or in the course notebook, never in a mail client.
