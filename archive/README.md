# Archive: two superseded designs, kept for their research

Nothing in here describes the current course. It is kept because a lot of it
was expensive to establish and some of it is still true.

The current proposal is `docs/itsy1377-course-proposal.md`. The facts that
survived both rewrites are in `docs/runtime-and-model.md` and
`docs/browser-runtime-assessment.md`, which are live documents, not archive.

## What is in here

### `v1-itsy1377/` The first design

`course-blueprint.md` and its rendered `blueprint.html`, plus
`proof-of-concept.html`. This is the course that was actually built and
deployed to Canvas: eleven modules, 45 pages, six quizzes, seventeen videos.
Four weeks of it were agent construction, which assumed students could program.

**Still worth recycling:** the framework research (OWASP LLM 2026 and Agentic
2026 edition names, the MITRE ATLAS pinning and attribution problem, the NIST
AI RMF subcategory mapping), the licence audit of every external resource, and
section 8's account of what the maintenance actually costs per term.

**Do not reuse:** the week structure, the outcomes, or the assumption that
students arrive able to write Python.

### `v2-itsy2377/` The second design

`itsy2377-course-design.md`, thirteen sections. Never built. It rebuilt the
course around the NCAE-C CyberAI knowledge units AIS and DFA, assumed a
scripting prerequisite would land, and would have renumbered the course to
sophomore level. The program dropped the knowledge unit pursuit and the
coordinator declined the prerequisite, so both premises are gone.

**Still worth recycling, and some of it was extracted rather than left here:**

- Sections 11 and 12, the model measurements and the portable bundle, were
  moved to `docs/runtime-and-model.md` and remain live.
- Section 13 and the browser assessment remain live in `docs/`.
- Section 3's assessment plan, in particular the argument for why AI assistance
  stays permitted but unprofitable.
- Section 9's analysis of what the video pipeline can and cannot record. The
  constraint is unchanged: the recorder is a Linux container and records a
  terminal, so no GUI step can be filmed.
- Section 10's three portfolio hazards. All three still apply: a published
  canary is reversible to a student ID against the published default salt,
  neither repository has a LICENSE file, and detection logic transfers between
  students in a way a seeded target does not.

**Do not reuse:** the six outcomes, the knowledge unit mapping, the week
structure, or anything that assumes a prerequisite.

### `ku-mapping/` The knowledge unit work

`aicyber-ku-mapping.md`, `ku-coverage-analysis.md` and `.html`, and
`ku-coverage-addenda.md`. The full NCAE-C CyberAI mapping: every AICyber
knowledge unit, what the course satisfied in full and in part, and the costed
addenda for closing the gaps.

**Superseded in its entirety.** The program is keeping its existing CAE-CD
credential and is not pursuing the AI designation. Kept because the research
into what the knowledge units actually require took real work, and because a
future program director may revisit it.

## A note on the tooling

Two build tools used to write into `v1-itsy1377/course-blueprint.md` and
`blueprint.html`. They no longer do, and `tools/verify_content.py` does not
scan this directory. That is deliberate: an archived document is a snapshot of
what was believed when it was written. Regenerating into one would rewrite
history, and holding one to today's case files would either falsify the record
or block the build on it.
