# Installing Canvas LMS on a bare VM

Notes from building the `canvas` guest on remotelab, 2026-09-12, against
`instructure/canvas-lms` tag `release/2026-05-20.143` on Debian 13 (trixie).

Everything below was verified against the source tree or observed as a real
failure. Where it contradicts Instructure's wiki, the wiki is wrong or stale.

---

## Install from a release tag, not from `prod`

The Production-Start guide says `git checkout prod`. Don't. The tip of `prod`
is a moving target and was **broken** on 2026-09-12 at `44bfdc26`:

```
[rspack-cli] [Error: × Module not found:
  Can't resolve '@instructure/platform-alerts'
  in '/var/canvas/ui/features/discovery_page/react/components'
```

`@instructure/platform-alerts` was undeclared in all five in-tree
`package.json` files, absent from `node_modules`, not a workspace package, and
had no bundler alias — yet one file still imported it
(`ui/features/discovery_page/react/components/ConfigureModal.tsx`). The
dependency had been removed upstream and a single import left behind. At
`release/2026-05-20.143` the same package is properly declared in
`package.json` and used by 689 files, so the tag is coherent where the branch
tip is not.

Release tags are named `release/YYYY-MM-DD.NNN`, highest `NNN` being the most
patched build of that release:

```sh
git ls-remote --tags --refs https://github.com/instructure/canvas-lms \
  | sed 's|.*refs/tags/||' | grep '^release/' | sort -V | tail -5

git fetch --depth 1 origin \
  refs/tags/release/2026-05-20.143:refs/tags/release/2026-05-20.143
git checkout release/2026-05-20.143
```

Note the `release/` prefix — `awk -F/ '{print $NF}'` on the ref list silently
strips it and gives you a tag name that `git fetch` will reject.

**Failure mode to expect:** a broken branch tip does not announce itself. The
parallel task runner in `canvas:compile_assets` swallows child output and
reports only `Parallel::UndumpableException: RuntimeError: Error running
js:webpack_production:` with an empty message. Run the failing subtask directly
(`rake js:webpack_production`) to see the real error.

---

## The ordering trap

**A fresh install cannot complete `db:migrate` until assets are compiled, and
cannot compile assets with brand configs until the database is migrated.**

The cycle:

1. `rake db:initial_setup` runs migrations and aborts partway with

   ```
   StandardError: An error has occurred, this and all later migrations canceled:
   you must run "gulp rev" first
   ```

   from `db/migrate/937157303960263479_regenerate_brand_files_based_on_new_defaults_predeploy.rb:51`.
   That migration reads the asset manifest, which only exists after
   `js:gulp_rev` has run.

2. `rake canvas:compile_assets` would produce the manifest — but its
   `brand_configs` step needs the database, which is now half-migrated.

It fails quietly in a way that looks like success: the rake exit code is often
masked if the output is piped through `tail`, and the database ends up with a
loaded schema, hundreds of tables, and **no admin user** — so the first symptom
is usually "I can't log in" rather than "migrations failed".

### The sequence that works

```sh
# 1. migrate as far as it will go; expect it to abort at the brand files migration
RAILS_ENV=production bundle exec rake db:initial_setup

# 2. compile assets WITHOUT brand configs, breaking the dependency on the db
RAILS_ENV=production \
  COMPILE_ASSETS_BRAND_CONFIGS=0 \
  COMPILE_ASSETS_NPM_INSTALL=0 \
  COMPILE_ASSETS_STYLEGUIDE=0 \
  COMPILE_ASSETS_API_DOCS=0 \
  bundle exec rake canvas:compile_assets

# 3. now the manifest exists, so the migration can finish
RAILS_ENV=production bundle exec rake db:migrate

# 4. and the account/admin setup can run
RAILS_ENV=production bundle exec rake db:load_initial_data
```

`db:load_initial_data` (`lib/tasks/db_load_data.rake:218`) chains
`create_default_accounts`, `configure_admin`, `configure_account_name`,
`configure_statistics_collection` and `generate_data` — it is the part of
`initial_setup` that never got to run. `db:configure_admin` alone creates only
the user, leaving you without a root account. Both accept the same env vars, so
the run is non-interactive:

```sh
CANVAS_LMS_ADMIN_EMAIL=...  CANVAS_LMS_ADMIN_PASSWORD=...
CANVAS_LMS_ACCOUNT_NAME=... CANVAS_LMS_STATS_COLLECTION=opt_out
```

Check step 3 actually finished rather than trusting the exit code:

```sh
bundle exec rake db:migrate:status | awk '$1=="down"' | wc -l   # want 0
```

### Why the other two skips

- `COMPILE_ASSETS_STYLEGUIDE=0` — `css:styleguide` shells out to `dress_code`
  (`Gemfile.d/assets.rb`, group `:development, :test`). The styleguide is
  developer documentation; a production LMS doesn't serve it. If the binary is
  missing the whole task dies with
  `Parallel::UndumpableException: RuntimeError: error running dress_code`.
- `COMPILE_ASSETS_API_DOCS=0` — same reasoning, same gem group.

Both are honoured by `lib/tasks/canvas.rake` (lines 27–34).

---

## Do not exclude gem groups

The instinct on a production box is:

```sh
bundle config set --local without development:test   # DON'T
```

It produces a bundle that cannot load **anything**:

```
Bundler::GitError: https://github.com/wrapbook/crystalball.git
  is not yet checked out. Run `bundle install` first.
```

`crystalball` is declared in `Gemfile.d/test.rb` but appears as a `GIT` source
in the *primary* `Gemfile.lock`, and bundler requires every git source in the
lockfile to be checked out regardless of which groups you excluded. `bundle
install` skips fetching it, then every subsequent `bundle exec` — including
`rails`, `rake` and Puma — dies on the missing checkout.

Confusingly, `bundle check` prints **"The Gemfile's dependencies are
satisfied"** on its first line and *then* raises. The reassuring line is about
the primary bundle; the exception comes from `bundler-multilock` reconciling
`Gemfile.rails80.plugins.lock`. Read past the first line.

Install all groups. A handful of unused development gems costs less than a
bundle that won't boot.

---

## Where the published docs are wrong

| Instructure's wiki | What the tree actually requires |
|---|---|
| Quick-Start: "Canvas LMS currently requires Ruby version 3.1. Ruby versions 3.2 and above are not supported." | `Gemfile.d/_before.rb`: `ruby ">= 3.4.1"`. The Quick-Start page is years stale. |
| Production-Start: `apt install ruby3.4` via `ppa:instructure/ruby` | That PPA is Ubuntu-only and will not add to Debian. Build with `ruby-build` instead. |
| Production-Start: Apache + Phusion Passenger | Passenger is not in `Gemfile.lock` at all. Puma 7.2.0 is, and `config/puma.rb` ships in the tree. |
| Production-Start: PostgreSQL 14 | 14 is the floor, not the target. Trixie's PostgreSQL 17 works. |
| `config/redis.yml.example` | Its `production:` block is commented out, so it is easy to copy the shape from the prose above it and write `servers:`. That key is rejected by `redis-client` 0.28 with `unknown keyword: :servers (ArgumentError)`. The correct key is `url:`, taking a list. |

## Versions that worked

- Debian 13 (trixie), 6 vCPU / 16 GB / 120 GB
- Ruby 3.4.10, built via packaged `ruby-build` into `/usr/local`
- Node 20.19.2 and PostgreSQL 17.11 and Redis 8.0.2, all from trixie
- Yarn 1.22.22 (classic — `package.json` says `"yarn": "^1.19.1"`)
- Bundler 2.6.7 (from `Gemfile.lock`'s `BUNDLED WITH`)
- nginx 1.26.3 reverse-proxying to Puma on `127.0.0.1:3000`

## Sizing note

`canvas:compile_assets` is the peak, not steady-state serving. It builds
production *and* development webpack bundles by default; `JS_BUILD_NO_FALLBACK=1`
skips the development pass if you want to halve it.

## Cloudflare in front

Cloudflare blocks Python's `urllib` by user-agent — API calls return `403` with
no useful body while `curl` against the identical URL returns `200`. Anything
scripted against the Canvas API through the tunnel needs a browser-ish
`User-Agent`. `requests` is *not* blocked (it sends `python-requests/x.y.z`),
so `builder/canvas/build_course.py` is unaffected; only hand-rolled `urllib`
callers need the header.

Since `cloudflared` terminates TLS and forwards plain HTTP to the origin, nginx
must set `X-Forwarded-Proto https` or Canvas — which has `ssl: true` in
`config/domain.yml` — will treat every request as insecure and redirect-loop.

### Access in front of that, and the error it produces

`canvas.bashtion.dev` sits behind Cloudflare Access for the build period. A browser logs
in; a script cannot, so `build_course.py` presents a service token instead:

```sh
export CF_ACCESS_CLIENT_ID=...       # the non-secret half
export CF_ACCESS_CLIENT_SECRET=...   # 1Password — Cloudflare shows it once, at mint time
python3 builder/canvas/build_course.py
```

Without them the failure is `requests.exceptions.JSONDecodeError`, not a `401` and not
anything Canvas said: Access answers with an HTML login page and the script asked for
JSON. Set exactly one of the two and it exits saying so, rather than handing you the same
puzzle. With both unset it behaves as it always did, so the script still works against an
ungated instance.

That gate allows a single email address and it stays that way: this instance is for
authoring, and the course is exported into the college's Canvas for delivery, so no
student ever reaches this hostname. What is dated is the service token — it expires
2027-09-12, and its failure looks like the same JSON parse error. The removal procedure,
for the day the instance becomes student-facing, and the ordering that avoids an outage
(route requirement off first, application second), live in the remotelab repo at
`infra/runbooks/course-dmz-onboarding.md`.

---

## Course copy drops every quiz until the QTI converter is installed

A manual install has no QTI migration tool, and nothing tells you. Copy a course and you
get its pages, files, assignments, rubrics, outcomes, modules and syllabus; you do **not**
get quizzes, question banks, or the assignment shells the graded quizzes own. The migration
reports `completed`, `migration_issues_count: 0`, and the progress bar reaches 100%.

Signature, in the order it is worth checking:

```sh
# the copy claims it imported everything...
curl -s -H "Authorization: Bearer $TOK" \
  "$BASE/api/v1/courses/<dest>/content_migrations/<id>" \
  | jq '.audit_info.migration_settings.migration_ids_to_import.copy.all_quizzes'   # "1"

# ...but no Quizzes::Quiz appears among the imported assets
curl -s -H "Authorization: Bearer $TOK" \
  "$BASE/api/v1/courses/<dest>/content_migrations/<id>" \
  | jq '.audit_info.imported_assets | keys'      # no Quizzes::Quiz, no AssessmentQuestionBank

# and every module is short exactly its quiz item
curl -s -H "Authorization: Bearer $TOK" "$BASE/api/v1/courses/<dest>/modules?include[]=items" \
  | jq -r '.[] | "\(.items|length)\t\([.items[]|select(.type=="Quiz")]|length)\t\(.name)"'
```

The export half is fine, which is worth confirming before suspecting it: the cartridge
carries each quiz as an `assessment_qti.xml` + `assessment_meta.xml` pair, so
`unzip -l export.imscc | grep assessment_qti` lists one per quiz. The loss is entirely on
import.

**Why.** `gems/plugins/qti_exporter` converts QTI 1.2 to 2.1 by shelling out to Instructure's
Python tool. `Qti` looks for `RAILS_ROOT/vendor/QTIMigrationTool/migrate.py`, then
`vendor/qti_migration_tool/migrate.py`, then `migrate.py` on `PATH`; if none is found
`migration_executable` is `nil` and the plugin registers itself with `enabled: false`.
Instructure's production-start notes mention this in one line, and it is easy to read as
optional. It is not optional for course copy.

**Install it.** The tool was ported to Python 3 in 2022 — the old warnings about needing
Python 2 are stale. `lxml` is its only runtime dependency, and on Debian it comes from apt,
not pip, because a trixie interpreter is externally managed:

```sh
apt-get install -y python3-lxml
git clone --depth 1 https://github.com/instructure/QTIMigrationTool.git /opt/QTIMigrationTool
chmod 0755 /opt/QTIMigrationTool/migrate.py
ln -sfn /opt/QTIMigrationTool /var/canvas/vendor/QTIMigrationTool

# Canvas execs migrate.py through its own shebang, so prove it runs as the app user
sudo -u canvas env PATH=/usr/local/bin:/usr/bin:/bin \
  /var/canvas/vendor/QTIMigrationTool/migrate.py --version

systemctl restart canvas canvas-jobs
```

`/opt` plus a symlink rather than a clone inside the tree: `vendor/` is in Canvas's own
`.gitignore`, so a foreign checkout there is invisible to git and a `git clean -xdf` during
an upgrade would delete it. The symlink is also what the plugin's Readme describes doing.

**The restart is load-bearing, and it is `canvas-jobs` that matters.** The probe is a
top-level `File.exist?` in `Qti`, evaluated when the class loads, and the plugin's `enabled`
default is computed from its result in `config.to_prepare`. A running process will never
notice a directory that appeared after boot. The import itself runs in a delayed job, so
restarting only the web app leaves the exact same silent failure in place.

Verified end to end on 2026-09-12 by copying the course into a scratch shell: 10 of 10
quizzes, question counts and points identical to the source (exam 40 items / 30 points, six
self-checks at 12), every module's Quiz item back in position, and `build_course.py --verify`
against the copy reporting one unrelated problem — the default `Assignments` group Canvas
adds to any new course.

---

## Uploaded files land in `tmp/` unless you say otherwise

There is no `config/file_store.yml` after a manual install, and Canvas falls back to
a hardcoded default (`app/models/attachment.rb`):

```ruby
@file_store_config ||= { "storage" => "local" }
@file_store_config["path_prefix"] ||= @file_store_config["path"] || "tmp/files"
```

So every uploaded file — for this course, 114 files and 86 MB including the
walkthrough videos — lands in `/var/canvas/tmp/files`, *inside the git checkout*
and matched by its own `.gitignore` (`/tmp/*`). A `git clean -fdx` during an
upgrade deletes the lot while the `attachments` rows survive, so the damage shows
up as broken links rather than an error. (Plain `git clean -fd` is safe, and
`rake tmp:clear` is scoped to `tmp/cache` and friends — it does not touch this.)

### An absolute `path_prefix` does not work

This is the trap. `file_system_backend.rb` builds the path as
`Rails.root.join(path_prefix, *partitioned_path(...))`, and `Pathname#join` does
discard the base for an absolute argument — so an absolute prefix *looks* correct.
But Canvas strips the leading slash between the two layers:

```
file_store_config    path_prefix: "/var/canvas-files"   # what you wrote
attachment_options   path_prefix: "var/canvas-files"    # what is used
full_filename        /var/canvas/var/canvas-files/0000/0081/...
```

The result is a path *inside* Rails root, every file 404s with
`Errno::ENOENT ... rb_file_s_size`, and downloads return HTTP 400 with an HTML
error page. Use a `../` relative prefix, which survives untouched and resolves to
the same place:

```yaml
production:
  storage: local
  path_prefix: ../canvas-files      # -> /var/canvas-files
```

Move the **contents** of `tmp/files` to the new root, not the directory itself —
the `0000/00NN/` segments are regenerated from the attachment id, so
`/var/canvas-files/0000/...` is right and `/var/canvas-files/files/0000/...`
breaks every link. Stop `canvas.service` and `canvas-jobs.service` for the move
(`file_store_config` is memoized per process, so all four Puma workers and the
job daemon hold the old value until restarted), and verify afterwards with:

```ruby
Attachment.where(file_state: "available").reject { |a| File.exist?(a.full_filename) }
```

Note the same config drives Thumbnail and purgatory paths, not just `files/`.

---

## Logging is unbounded and defaults to `debug`

`config/application.rb` defaults `log_level` to `debug` and only overrides it from
`config/logging.yml`, which a manual install does not create. Production then logs
every SQL statement — including the `delayed_job` queue-poll `UPDATE`, once or
twice a second, forever. Measured at zero load: **148 MiB/day**, unbounded, on the
same partition as PostgreSQL and the file store.

```yaml
# config/logging.yml
production:
  log_level: info
```

That alone took this install from 148 MiB/day to ~23 MiB/day. Debian ships
logrotate stanzas for nginx, postgresql and redis but nothing for Canvas, so add
one — with `copytruncate`, because `CanvasLogger` holds the descriptor open and a
plain rename leaves both processes writing to an unlinked inode until restart:

```
/var/canvas/log/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    su canvas canvas
}
```
