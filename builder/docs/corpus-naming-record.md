# Corpus naming record

`corpus/README.md` tells the reader that nothing in the corpus is real. The
Phase 0 design tells the program manager that every business name was
web-searched. Neither one showed its working. This file is the working.

It records how an invented name is cleared, what each search returned, and
which sources could not be reached. It is written so a reader can repeat the
checks rather than take the claim on trust.

Last updated 2026-09-04.

## The rule

No real brand, company, product, person or trademark. Every proper noun is
invented. Every domain ends in `.example`, which is reserved for documentation
and never resolves.

The rule has no exception for a dissolved company, a tiny company, or a company
in an unrelated industry. An exact token match fails it.

## The register

The corpus names are two-part compounds of a nature word and a craft or place
word:

Pellgrave, Slatemoor, Larkseal, Ferncrate, Hollinvale, Elmhollow, Cindermill,
Inkmoor, Sandmarsh, Marlstone, Rookmere, Thistlecrest, Redcedar, Cottonmoor,
Peakwright, Fenwright, Larkhollow, Sentrywick, Lanternmail, Sendbarrow,
Vetchmoor.

This register is not the whole set of invented nouns. Email bodies also name
payees, projects, mailers and decoy hosts that no register tracks. Section
"What this record does not cover" says what follows from that.

## What went wrong: Tidefern

Tidefern Benefits was the corpus benefits broker, on
`tidefernbenefits.example`, with `tidefern-benefits.example` as the
hyphen-insertion look-alike an attacker spoofs in a credential phish.

The token is an exact match for TIDEFERN LIMITED, a real New Zealand company.
NZBN 9429049122558, company number 8168656, registered 10 March 2021 to
2 May 2022, status Removed, industry "G425310 Jewellery retailing". Confirmed
from two independent sources.

Three facts point the other way and none of them changed the decision. The
company is dissolved. It is a one-person jewellery retailer. No trademark was
found for it.

They did not change the decision because the match is exact rather than near,
and because of where the name sits. In this corpus the name is attached to a
vendor whose domain is spoofed in a credential phish. Tying a real company name
to a phishing lure is the association the rule exists to prevent.

The deeper defect is that no search was ever recorded. The Phase 0 claim rested
on nothing a reader could check.

## The replacement: Vetchmoor

Vetchmoor Benefits, on `vetchmoorbenefits.example`, with
`vetchmoor-benefits.example` as the look-alike.

Vetch is a legume. A moor is open upland. Both are ordinary English nouns, and
the compound matches the register: Inkmoor, Cottonmoor and Slatemoor already
use the same second element.

The name is nine characters, one more than Tidefern. That matters because the
generators refuse any header line over 78 characters. The longest affected line
is the `From` header of email 053, which carries the name twice and now renders
at 76 characters.

### Rejected candidates

| Candidate | Why it was rejected |
|---|---|
| Quillmarsh | Exact token match. It is a named location in a published novel, *Whispers of the Forgotten Realm* Book 3, sold on Amazon. |

## The searches that cleared Vetchmoor

Run 2026-09-04.

| Search | Source | Result |
|---|---|---|
| Bare token `"Vetchmoor"` | General web | No exact match. Results split into `vetch`, the legume, and unrelated `-moor` place names. |
| `"Vetchmoor" limited OR ltd OR inc OR LLC OR company` | General web | No exact match. Only generic entity-type explainers and unrelated `Vet-` companies. |
| `vetchmoor` | New Zealand Companies Register | "Your search returned no results." |
| `vetchmoor` | UK Companies House | "There are no results that match your search." |
| `vetchmoor` | Australian ABN Lookup | "Your search for vetchmoor found no matching names." |
| `vetchmoor` | OpenGovUS, covering US business entities, licences and marks | No results. |
| `vetchmoor` | Canadian Trademarks Database, CIPO | Results table empty. |
| `vetchmoor.com`, `.co.uk`, `.co.nz`, plus brand and product wording | General web | No match. No site, brand or product carries the name. |
| Token scoped to USPTO, Justia Trademarks, EUIPO, UK IPO, OpenCorporates, Bizapedia and the NZ register | General web | No exact match. |

The New Zealand register is the source that caught Tidefern, so it was checked
first.

### Sources that could not be reached

Recorded rather than hidden, because a check that did not run is not a pass.

| Source | Why |
|---|---|
| OpenCorporates | CAPTCHA. Its API returned 401 without a key. |
| Bizapedia | CAPTCHA. |
| Trademarkia | HTTP 403. |
| WIPO Global Brand Database | CAPTCHA on load. |
| UK IPO trade mark text search | HTTP 403. |
| USPTO trademark search API | No public unauthenticated endpoint. |

Trademark coverage therefore rests on CIPO, on OpenGovUS, and on a web search
scoped to the trademark sites. That is weaker than a direct USPTO query. A
reader who needs a stronger answer should query USPTO and EUIPO by hand.

## What this record does not cover

Three gaps, stated plainly.

**The other twenty register names have no recorded evidence.** Phase 0 says
they were web-searched. This record does not re-clear them. Clearing them to
this standard is a separate job, and Phase 0 section 15 item 6 already asks for
the search to be re-run before the corpus ships.

**Names inside email bodies are not registered anywhere.** Payees, projects,
mailers and decoy hosts are invented per email. Nothing tracks them as a set.
One consequence is already visible in the build: `gen_004` carries its own
uniqueness guard for its payee name, and that guard is currently failing
against a body name in email 033.

**Employee names were never searched.** Phase 0 section 15 item 3 already says
so and asks the college to decide.

## How to clear the next name

1. Coin a two-part compound in the register style.
2. Search the bare token in general web search.
3. Search the token with `limited`, `ltd`, `inc`, `LLC` and `company`.
4. Search the New Zealand register, UK Companies House, and one general company
   directory that is not blocked. Australian ABN Lookup answers reliably.
5. Search the token as a domain and as a product or brand name.
6. Run a trademark search. Record which databases answered and which blocked.
7. Reject on any exact token match anywhere, including fiction and place names.
8. Write the searches and their results into this file before using the name.

Reject on the exact token. A near match is allowed, and the register is built
from near matches to real English place names on purpose.

## What changed in the corpus

The rename touched 320 occurrences across 17 source files, and the build
re-rendered four emails from them.

- Generators `gen_013`, `gen_024`, `gen_027`, `gen_053`, `gen_056`. Four of the
  five carried the old name in their filename and were renamed.
- Data files `display_names.json`, `domain_policy.json`,
  `sender_reputation.json`, `url_allowlist.json`, `url_unlisted.json`.
- `spec/corpus-spec.json` and `ground_truth.json`.
- `docs/phase0-corpus-design.md` and its rendered HTML,
  `docs/phase1-blueprint.html`, `docs/phase1-blueprint/exam-blueprint.md`.
- `lab/eval/week6_injection_test.py`, whose case list keys on email ids.

Email ids changed with the names: `013-vetchmoor-census-correction`,
`024-vetchmoor-census-control`, `053-vetchmoor-plan-documents`,
`056-vetchmoor-quarterly-update`.

The DKIM selector for the broker changed from `tf1` to `vm1`. It was the old
name's initials. It is a data field only and is rendered into no message.

Emails 013 and 024 are a deliberate control pair: 024 repeats 013's body
without the injection paragraph. Both were renamed in one pass and re-rendered
together, and the rendered pair still shares every body line in both parts.

None of the six emails whose digests the week 5 measurement recorded was
touched. `build_corpus.py` confirms it on every run.
