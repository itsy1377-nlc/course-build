# NICE verification record for the ITSY 1377 alignment matrix

Prepared 2026-09-03 from the verifier and skeptic reports plus the author's own checks.

## Citation for the matrix

NICE Framework Components v2.2.0 (NIST, April 28, 2026), implementing NIST SP 800-181 Rev. 1 (November 2020); work role PD-WRL-001 Defensive Cybersecurity, Protection and Defense; retrieved 2026-09-03 from niccs.cisa.gov and nist.gov.

Date caveat. The NIST Current Versions heading reads "2.2.0 (April 28, 2025)", but the change log dates 2.2.0 to 28 April 2026 and 2.1.0 to 3 December 2025, and the release note URL is under /2026/04/. The heading year is a typo; cite the change log.

## Work role confirmation

The NICCS page shows Defensive Cybersecurity, NICE Framework ID PD-WRL-001, category Protection and Defense (PD), source line "Workforce Framework for Cybersecurity (NICE Framework) (NIST SP 800-181 Rev 1) (Version: 2.2.0)". The saved JSON (doc_identifier SP_800_181_2_2_0) links PD-WRL-001 to 43 tasks, 38 skills, and 124 knowledge statements; the NICCS task and skill lists match exactly.

## Result

All 21 IDs exist in v2.2.0 and are linked to PD-WRL-001. Missing or outside the role: none. No substitutions. Source URLs are per-element pages; the role page and JSON also confirm each row.

## CLO1 (Apply): Extract the header, authentication, sender, and URL facts an AI model needs to judge a suspicious email

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T1085 | task | Identify potential threats to network resources | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1085 | Moderate primary. Evidence step of a phishing threat; network wording, user-layer CLO. |
| T1084 | task | Identify anomalous network activity | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1084 | Weak to moderate, supporting only. Header and URL mismatches are message-level. |
| S0600 | skill | Skill in collecting relevant data from a variety of sources | yes | yes | https://niccs.cisa.gov/tools/nice-framework/skill/S0600 | Strong. Collecting facts from several sources inside one email. |
| S0712 | skill | Skill in evaluating data source quality | yes | yes | https://niccs.cisa.gov/tools/nice-framework/skill/S0712 | Good. Judging which header facts to trust is source-quality evaluation. |

## CLO2 (Analyze): Classify a suspicious email as malicious or benign using an AI model, then validate the model's output before trusting it

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T1348 | task | Distinguish between benign and potentially malicious cybersecurity attacks and intrusions | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1348 | Strong primary. State that a phishing email is treated as an attack; supporting tasks carry the validate clause. |
| T1112 | task | Validate network alerts | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1112 | Partial, supporting only. Verb matches; network wording does not. State the mismatch. |
| T1387 | task | Validate intrusion detection system alerts | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1387 | Partial, supporting only. Holds if the AI classifier counts as a detection system. Also under PD-WRL-002. |

## CLO3 (Create): Build an AI agent that selects and runs triage tools in a bounded loop to reach a verdict

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T0020 | task | Develop content for cyber defense tools | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T0020 | Strong at Create level. Agent, tools, prompts, and loop are cyber defense tool content. |
| T1299 | task | Determine causes of network alerts | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1299 | Partial supporting. Says network alerts; omits tool selection and the bounded loop. Also under PD-WRL-003. |

## CLO4 (Evaluate): Judge whether an agent's guardrails reduce prompt injection risk to an acceptable level

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T1177 | task | Determine if security control technologies reduce identified risk to acceptable levels | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1177 | Near-verbatim primary. Guardrails are control technologies; prompt injection is the risk. |
| T1176 | task | Determine if cybersecurity-enabled products reduce identified risk to acceptable levels | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1176 | Good supporting. Same judgment at product level. |
| S0509 | skill | Skill in evaluating security products | yes | yes | https://niccs.cisa.gov/tools/nice-framework/skill/S0509 | Moderate supporting. Holds only if agent plus guardrails counts as a product. |
| S0667 | skill | Skill in assessing security controls | yes | yes | https://niccs.cisa.gov/tools/nice-framework/skill/S0667 | Strong supporting. Guardrails are controls; the CLO assesses their adequacy. |

## CLO5 (Apply): Document a triage decision, its indicators, and its recommended action so another analyst can act on it

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T1241 | task | Document cybersecurity incidents | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1241 | Direct primary. The only role task naming documenting; the CLO is narrower. |
| T1349 | task | Communicate cybersecurity attacks and intrusions alerts | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1349 | Good supporting. Handing a record to another analyst communicates an alert. |
| T1242 | task | Escalate incidents that may cause ongoing and immediate impact to the environment | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1242 | Partial supporting. Covers the recommended action; limited to immediate impact. |
| T1428 | task | Notify designated managers, cyber incident responders, and cybersecurity service provider team members of suspected cybersecurity incidents | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1428 | Partial supporting. Matches the handoff; silent on indicators. |

## CLO6 (Evaluate): Measure agent triage accuracy across a batch of emails and recommend where human review stays required

| ID | Type | Statement | Exists (v2.2.0) | In PD-WRL-001 | Source URL | Fit note |
|---|---|---|---|---|---|---|
| T0164 | task | Perform cyber defense trend analysis and reporting | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T0164 | Strong primary. Batch accuracy plus an evaluation report is trend analysis and reporting. |
| T1020 | task | Determine the operational and safety impacts of cybersecurity lapses | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1020 | Moderate supporting. Safety wording reaches beyond what the batch measures. |
| T1290 | task | Communicate daily network event and activity reports | yes | yes | https://niccs.cisa.gov/tools/nice-framework/task/T1290 | Weak supporting. The week 7 report is one-time, not daily; keeping it is a design choice. |
| S0892 | skill | Skill in performing trend analysis | yes | yes | https://niccs.cisa.gov/tools/nice-framework/skill/S0892 | Good supporting. Finding where the agent fails systematically is trend analysis. |

## Disagreements and what settled them

1. CLO3 source inference. The verifier inferred from 404s at /tasks/T0020 and /tasks/T1299 that the role page was the only NICCS source. The skeptic reproduced the 404s, then fetched the singular /task/T0020 and /task/T1299, both HTTP 200 with matching text, which settled it; the tables cite them.

2. Release date. The CLO4 skeptic reported NIST saying April 28, 2025; the CLO2 skeptic and PROVENANCE.txt say 2026. The change log and URL paths above settled it.

3. Role page counts. WebFetch summaries reported 48 tasks and 42, 33, or 60 skills; every explicit ID list had 43 and 38, matching the JSON, which settled it.

4. Statement pairing and truncation. A CLO1 skeptic pass, the CLO5 verifier, and this record's own role-page fetch each saw the summary swap or truncate statements (T1085 and T1084, T1242, T1348, T1428). Per-element pages and the JSON settled it with correct full text every time. Quote from those, never from a role-page summary.

Not disputes: the build prompt's network-wording note omits T1085, so the rationale must say plainly that T1085 is also network-worded. T1348 says attacks and intrusions, so it is not literally layer-neutral. Knowledge IDs (124 in the JSON, 121 in one summary) were not reconciled; they are outside the mapping.

## Build prompt mapping notes, verbatim

- Several PD-WRL-001 tasks are worded around network activity. Phishing triage is a user-layer activity. T1348 and T0020 are the layer-neutral anchors and carry the weight; T1112 and T1084 are supporting only.
- No PD-WRL-001 task references AI, agents, or prompt injection, because the framework predates them. CLO4 therefore maps to the control evaluation tasks (T1176, T1177), since students are assessing whether a control reduces risk. State this openly.

## Sources read, all on 2026-09-03

NICCS, via WebFetch (direct curl returns HTTP 403): the role page https://niccs.cisa.gov/tools/nice-framework/work-role/defensive-cybersecurity (all reviewers, this record); the 21 per-element pages in the tables (lowercase ID paths for CLO1, CLO5, CLO6; uppercase for the rest and this record; both resolve); https://www.niccs.cisa.gov/tools/nice-framework. HTTP 404: /tools/nice-framework/tasks, /skills, /components, and every plural /tasks/ID or /skills/ID form.

NIST: https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/nice-framework-current-versions; https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/current-version/change-logs; https://www.nist.gov/news-events/news/2026/04/nice-releases-nice-framework-components-v220; https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center; https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center/workforce-framework-cybersecurity-nice; https://csrc.nist.gov/pubs/sp/800/181/r1/final; https://csrc.nist.gov/csrc/media/Projects/cprt/documents/nice/v2-2-0_nf_components.json (curl; sha256 3ad1d9d7e0d6b32895cb569f86c3bc05af2937a68e96eab4d1c9b3d9fa6e575e); https://www.nist.gov/document/nice-framework-components-v220, resolving to https://www.nist.gov/system/files/documents/2026/06/24/NICE%20Framework%20Components%20v2.2.0.xlsx (sha256 d33f76d262c039afbfb7b4b861204326a32c1e388b5c7bc9d15a43205125199d). HTTP 404: the singular nice-framework-current-version path. CPRT catalog and nudp graph URLs returned an application shell; not used.

Local copies and PROVENANCE.txt: /Users/aaron/workspace/dev/ITSY1377/builder/docs/nice-components/.
