# The shell, and making a term section from it

Canvas course **6** (`ITSY-1377-000`, currently named "Agentic AI Shell") is the master
shell. It is unpublished, has no students, and is the only course this repo builds:
`builder/content/course.yaml` sets `canvas_id: 6`. Every term section is a Canvas **course
copy** of it — `ITSY-1377-001` (course 10) is the first.

Established 2026-09-12. Everything below was measured on this install, shell 6 against
section 10, not taken from documentation.

## The rule, and why the publisher enforces it

**Never point `build_course.py` at a section.** It now refuses: `main()` reads the target
course before any write and exits if it is published or has active students, unless
`--allow-published` says otherwise.

The refusal is not caution, it is arithmetic. `build_modules` deletes every module item and
re-creates it on each run, so module progression resets and **every module item id changes**,
breaking any link a student bookmarked or an announcement quoted. It forces modules, pages,
assignments and discussions to published, including anything an instructor hid for staged
release. And the spine is the only source of a module's item list, so an item a section added
by hand — a proctor link, a campus policy page — is deleted with nothing in the repo able to
put it back. On an unpublished shell with no students every one of those is harmless, which is
exactly why it was written this way.

Two things follow. Content changes go into the repo and are published to the **shell**, then
copied down. And the container's identity belongs to the container: the publisher no longer
sends `course[name]` or `course[course_code]`, because it used to rename the shell to the
section name in `course.yaml` on every run — including a scoped `--week` run — and the shell's
own name is recorded nowhere in this repo.

## Per-term procedure

1. **Create the section course.** Name and code for the term. Do it in the sub-account you
   want it in — course 10 landed in account 3 ("Manually-Created Courses") while the shell
   sits in account 1, which is harmless but not obviously intentional.

2. **Course copy from course 6, everything.** This requires the QTI migration tool on the
   Canvas host. Without it the copy drops all ten quizzes, their question banks and the eight
   assignment shells the graded quizzes own, imports everything else, and reports `completed`
   with **zero** migration issues — see `canvas-vm-install.md`. Confirm before trusting it:

   ```sh
   curl -s -H "Authorization: Bearer $CANVAS_TOKEN" \
     "$CANVAS_BASE/api/v1/courses/<section>/quizzes" | jq length     # expect 10
   ```

3. **Run the fixups.** This repairs what copy mangles and prints what it drops:

   ```sh
   python3 builder/canvas/section_fixups.py --section <id> --check   # look first
   python3 builder/canvas/section_fixups.py --section <id>
   ```

   Run it after **every** copy, including a re-copy over an existing section.

4. **Set the per-term container state.** `section_fixups.py` prints these and deliberately
   does not guess them: term, `start_at`/`conclude_at` plus
   `restrict_enrollments_to_course_dates`, the late policy, the section's own name, license,
   and finally `course[event]=offer` to publish.

   **Assignment dates have to be entered, not shifted.** The shell holds no dates anywhere —
   no `due_at`, `unlock_at` or `lock_at` on any of the 23 assignments or 10 quizzes, no
   overrides, no calendar events, no module `unlock_at`. Canvas's `date_shift_options` only
   rewrites dates that already exist, so the usual "copy last term and shift the dates"
   pattern has nothing to work on. Both copies so far recorded `date_shift_options: null`.

5. **Cloudflare Access.** `canvas.bashtion.dev` is gated by a single-email Allow policy for
   the build period. Students cannot reach Canvas's own login through it. Removal procedure
   and the ordering that avoids an outage: `infra/runbooks/course-dmz-onboarding.md` in the
   remotelab repo.

## What course copy does, measured

| | |
|---|---|
| carried intact | pages, assignments, discussions, files, modules and their items, rubrics, outcomes, syllabus body, `default_view`, front-page selection, assignment groups **and their weights** |
| carried but transformed | file ids remapped (`src`, `href` rewritten); grading standard **duplicated** as a new per-course row; files become clone rows sharing the shell's blobs |
| dropped silently | `public_description`, publish state, term, all dates, enrollments, sections, license, late policy |
| dropped with no error but visible damage | **nothing, once the QTI tool is installed** — before it, all quizzes |

## Traps, each one measured here

- **`<video poster>` survives as an untranslated macro.** Canvas's importer rewrites `src`
  and `href` but not `poster`, so 14 of the 44 pages arrived holding
  `$CANVAS_COURSE_REFERENCE$/file_ref/<migration-id>/download?download_frd=1`, which returns
  404. Substituting the macro does not help — the `file_ref` route 404s as well — so
  `section_fixups.py` re-derives the file from the shell's copy of the same page and maps it
  by filename. The repo already documents the same Canvas omission on the cartridge path in
  `tools/populate_canvas.py`.

- **`public_description` vanishes with no visual cue.** Nothing in the Canvas UI shows a
  course's catalog blurb as missing. `verify` now checks it — the check existed but was
  dead-coded behind `if False:` on the belief that Canvas does not store the field on a
  private course. It does store it; it just omits it from `GET /courses/:id` unless
  `include[]=public_description` is passed.

- **Group weights copy; group contents might not.** Weights are course settings, assignments
  are content, so a partial content copy leaves a weighted group empty and Canvas silently
  renormalizes the rest. The gradebook then shows a plausible percentage that does not match
  the syllabus. `section_fixups.py` compares object counts against the shell for exactly this
  reason: before the QTI fix, `Self-Checks` (8%) and `Final Exam` (20%) were weighted groups
  with nothing in them — 28% of the grade.

- **The grading standard is duplicated per copy.** Shell owns standard id 1; section 10 owns
  id 5, same title, both `Course`-scoped, and no account-level standard exists. Editing the
  letter-grade scale in the shell reaches no section already copied. An account-level standard
  that both reference is the only way to have one scale.

- **Section files share the shell's blobs.** Both courses list 114 files with an identical
  manifest. Deleting or replacing a file in the shell can therefore affect a live section, and
  `storage_quota_used_mb` is not a meaningful guard on a copy.

- **Quiz publication depends on a Canvas cascade.** `make_quiz` sends
  `quiz[published]=false` so all 46 exam items can be deleted and re-posted while the quiz is
  hidden, and the module publish in `build_modules` re-publishes it. Measured 2026-09-12: that
  cascade fires even when the module is already published, and through the builder's exact
  delete-and-re-add sequence. `verify` now asserts the end state, because a quiz left
  unpublished in the shell copies into every section as a hidden assessment.

## Two decisions, settled 2026-09-12

- **The clock follows the wording: Central.** Course 6's `time_zone` was `America/Denver`,
  inherited from account 1's default, while the course promises "11:59 PM Central" in 47
  places across 27 content files. ITSY 1377 is a Texas TCCNS number, so the wording is right
  and the setting was wrong. Both the shell and section 10 are now `America/Chicago`. Nothing
  shifted, because neither course holds a single `due_at` — which is the only safe moment to
  change a course's time zone. The **account default is still `America/Denver`**, so a course
  created fresh rather than copied starts on the wrong clock; `section_fixups.py` flags a
  section whose zone differs from the shell's.

- **Plain course copy, not Blueprint.** Blueprint is available here
  (`manage_master_courses` is true, core rather than flag-gated) and was declined on purpose.
  A blueprint push carries whatever is in the shell into associated live sections, and this
  shell is rebuilt by a publisher that deletes and re-creates every module item — so a routine
  build during term would push a full module rebuild, with new item ids, into a course
  students are working in. Copy-once-per-term keeps that churn on the shell where it is
  harmless. Revisit only if mid-term content fixes become frequent enough to be worth the
  coupling.
