# DesignPLUS CSS shim

A visual stand-in for Cidi Labs DesignPLUS, so that ITSY 1377 course pages render
as a designed course in the local open-source Canvas.

| File | What it is |
|---|---|
| `designplus-shim.css` | The stylesheet. 43 KB, self-contained, zero external requests. |
| `apply_theme.py` | Installs it into the running Canvas as account-level custom CSS. |
| `preview.html` | Every block type and callout flavour on one page. Opens from the filesystem. |
| `README.md` | This file. |

Start here:

```bash
open canvas/theme/preview.html                  # see the whole visual system
python canvas/theme/apply_theme.py              # install it into local Canvas
python canvas/theme/apply_theme.py --check      # what is installed right now
python canvas/theme/apply_theme.py --manual     # by-hand instructions
```

---

## 1. Read this before anything else

These constraints come from blueprint section 5.7. They are not style preferences.

**No Cidi Labs CSS or JavaScript is copied or redistributed.** Every line of
`designplus-shim.css` was written from scratch. It happens to target the same
class names, because those class names are what the content carries. No
DesignPLUS stylesheet was fetched, inspected, or reproduced in building it. This
is not a DesignPLUS reimplementation and it does not attempt to be one.

**The class names in the authored content do not change.** `dp-wrapper`,
`dp-callout`, `kl_custom_block_1` and the rest stay exactly as the NLC template
uses them. That is the important half of the fix: every page is drop-in
compatible with the college's production Canvas, where the real DesignPLUS will
style it with no rework. The content is authored for production, not for the
demo.

**This is a visual stand-in for the local demo only.** It will not match Alamo
Colleges' theme. Not the colours, not the typography, not the spacing, not the
component behaviour. A reviewer looking at the local demo is looking at *a*
designed course, not at *the* course as students will see it. Production styling
comes from the college's DesignPLUS license. Do not let anyone conclude
otherwise from a screenshot.

**Nothing here makes an external request.** The NLC template pulls at least one
banner image from `designtools.ciditools.com`, which fails offline and will fail
on any Canvas that is not Alamo's. This shim introduces no equivalent
dependency: no `@import`, no CDN, no remote `url()`, no web font fetch. The
icon font is embedded in the stylesheet itself. Verified by scanning the file
with comments stripped: zero non-`data:` URLs.

**Interactive DesignPLUS components do not work, and cannot.** DesignPLUS
accordions, tabs, and modals are driven by licensed JavaScript. There is no
JavaScript here by design. The template's `dp-panel-group` accordions are
styled to render **open**, as a readable labelled stack, rather than collapsed
and un-openable. That is a deliberate degradation, not an oversight.

---

## 2. What gets styled

Everything `tools/blocks.py` emits, which was verified by rendering every
authored page and assignment under `content/` and taking an inventory of the
classes that actually appear in the output.

**Structure:** `dp-wrapper`, `dp-basic-bar`, `dp-header`, `dp-heading`,
`dp-header-title`, `dp-content-block`, `dp-has-icon`, `dp-icon-content`,
`dp-i-size-small`

**Callouts:** `dp-callout` plus `dp-callout-warning`, `-note`, `-tip`, `-stop`,
`-time`

**Block families:** `kl_introduction`, `kl_objectives2`, `kl_assignments2`, and
`kl_custom_block_0` through `kl_custom_block_7`

**Tables:** `ic-Table`, `table-bordered`, `ic-Table--striped`,
`ic-Table--hover-row`, `ic-Table--condensed`, plus `<th scope="row">` row
headers and `dp-caption-t` captions

**Code:** `pre`, inline `code`, and the `language-python` / `language-json` /
`language-yaml` classes the markdown build emits

**Icons:** the 18 Font Awesome classes the course uses (section 4)

Also styled, because the template's boilerplate pages are carried over as-is and
have to be readable: `dp-panel-group` / `dp-panel-heading` / `dp-panel-content`,
`dp-image-bordered` / `-padded` / `-shadow`, `dp-embed-wrapper`,
`dp-header-pre-1` / `-2`, and the handful of Bootstrap utilities the template
sprinkles around (`card`, `btn`, `row`, `text-center`, `float-end`, `mb-3`,
`ms-3`, `container-fluid`).

One extra: `.phpally-ignore` gets a dashed red outline. Those are unfilled
template placeholders. The content build already asserts that zero survive to
publication; this makes any survivor impossible to miss in review.

---

## 3. Design decisions

The audience is a program manager and a curriculum committee looking at a
community-college cybersecurity course. The target is calm, current, and
institutional.

**Header bar.** Each page opens with a solid deep-navy band carrying the page
title, with a brighter cyan edge beneath it. It reads as a masthead and it is
what visually separates one page from the next.

**Content blocks as quiet cards.** A tinted surface, a hairline border, and a
4px coloured keyline down the left edge. No heavy boxes. The keyline colour is
what distinguishes a block family at a glance, and the block's icon is tinted to
match, so the two cues reinforce each other. `kl_introduction` is deliberately
*not* a card: it is the page's lead paragraph, set slightly larger against a
bare keyline.

**"Authorization and Scope" is treated differently.** `kl_custom_block_7` gets a
full outline and a 6px keyline, so it reads as a formal clause. It deliberately
does **not** read as an alarm; urgency is reserved for the callouts, and the
Rules of Engagement page would otherwise be a wall of red.

**Five callouts, distinguishable without colour.** Colour alone fails an
accessibility review, and these pages get printed in greyscale. Each flavour
carries three independent cues:

| Flavour | Left rule | Full outline | Printed label | Icon |
|---|---|---|---|---|
| note | 4px solid | none | NOTE | info circle |
| tip | 4px **dashed** | none | TIP | lightbulb |
| time | 4px **dotted** | none | TIMING | clock |
| warning | **7px** solid | 1px | WARNING | warning triangle |
| stop | **7px** solid | **2px** | STOP | raised hand |

Rule weight and outline weight both climb toward `stop`, so the urgency ordering
survives greyscale printing and every form of colour vision. The uppercase label
is real generated text, so screen readers announce it too.

**Tables.** Uppercase tinted header row with a 2px rule under it, zebra striping,
hover highlight, and row headers kept bold but visually distinct from the header
row. Nowrap on header cells until the viewport gets narrow.

**Code.** A darker slab, monospace, its own left keyline, and `overflow-x: auto`
with `white-space: pre` so a command line is never silently wrapped into
something that would not run if pasted. Fenced blocks get a small uppercase
language tag in the corner. No syntax highlighting is attempted, because doing
it in CSS alone would require markup this build does not produce.

**Type at Canvas's width.** Canvas hands page content a container of roughly
1100px. The wrapper caps at 1100px, but prose is capped at a 68ch *measure*
while tables and code use the full width, so line length stays readable without
wasting the container.

The NLC template hard-codes `font-size: 18pt` on page titles and `14pt` on block
headings. `tools/blocks.py` deliberately does not reproduce those, because a
fixed point size ignores a reader who has raised their default font — a real
part of this audience. Sizing is therefore the stylesheet's job, and it is
expressed in `rem` throughout: page titles at `1.5rem` and block headings at
`1.17rem`, which land on the same 24px and 18.7px the template's point sizes
produced at a default font size, but now scale with the reader. Block heading
size is set explicitly rather than left to the browser so the icon, which
inherits the heading's font size, lines up with the text beside it.

**Light and dark.** Both palettes are defined as CSS custom properties on
`.dp-wrapper`. Dark mode triggers on `prefers-color-scheme: dark`, and also on
an explicit `data-dp-theme="dark"` attribute so a reviewer can force either mode
(the toggle in `preview.html` uses this).

One honest wrinkle: **Canvas has no dark theme.** Dark cards floating on a white
Canvas page would look broken, so in dark mode the wrapper paints its own
background and becomes an explicit dark canvas. It is internally consistent but
it does not restyle Canvas's own chrome, which stays light.

Canvas's "High Contrast UI" user setting only swaps which stylesheet bundle
Canvas loads (`new_styles_high_contrast`); it adds **no class to the DOM**, so
user CSS has no hook to key off. Verified in
`app/helpers/application_helper.rb`. The shim therefore keys off the browser's
`prefers-contrast: more` instead, thickening borders and rules rather than just
darkening ink. There is also a `forced-colors: active` block for Windows High
Contrast that hands colour back to the OS while keeping the border structure,
which is what carries the meaning here.

---

## 4. Icons: self-hosted, pinned, subsetted, renamed

The template uses Font Awesome 5 class names and the export ships no font. The
brief requires the font be self-hosted and pinned, never pulled from a CDN,
because the demo has to work offline.

**What was done.** Font Awesome Free **6.7.2** was downloaded from the npm
registry, the 18 glyphs this course actually uses were extracted with
`fonttools`, and the two resulting subsets are embedded in the stylesheet as
`woff2` `data:` URIs. Total added weight: **3.8 KB** (2,736 bytes solid + 1,084
bytes regular). Nothing is fetched at runtime, so this works with the network
unplugged, and there is no separate font file to lose or mis-path.

Pinned source, for reproducibility:

```
https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.7.2.tgz
sha256  794284b4ac7f3e30825bbeea1a073f542c45dff83f8146625f600f1015c9d52b
```

**Licenses**, as stated in the package's own `LICENSE.txt`:

| Part | License |
|---|---|
| Icons (SVG / JS) | CC BY 4.0 |
| Fonts (web / desktop font files) | SIL OFL 1.1 |
| Code | MIT |

Copyright (c) 2024 Fonticons, Inc. — <https://fontawesome.com>

**Why the font family is renamed.** Font Awesome's OFL grant declares a
**Reserved Font Name: "Font Awesome"**. OFL 1.1 forbids a modified version from
carrying the reserved name. A subset is a modification, so the embedded font is
named **`ITSY Shim Icons`** and its name table records that it is a subset of
Font Awesome Free 6.7.2, under OFL 1.1, not endorsed by Fonticons. This is a
license requirement, not a preference.

**Font Awesome 6 renamed several of these icons**, but the content carries the
FA5 names and must keep them for production compatibility. The stylesheet maps
the FA5 class the content uses to the codepoint, and notes the FA6 name in a
comment:

| Class in content | FA6 name | Codepoint |
|---|---|---|
| `fa-arrow-alt-circle-right` | `circle-right` | U+F35A |
| `fa-book-reader` | `book-open-reader` | U+F5DA |
| `fa-check-square` | `square-check` | U+F14A |
| `fa-exclamation-circle` | `circle-exclamation` | U+F06A |
| `fa-exclamation-triangle` | `triangle-exclamation` | U+F071 |
| `fa-hand-paper` | `hand` | U+F256 |
| `fa-info-circle` | `circle-info` | U+F05A |
| `fa-list-alt` | `rectangle-list` | U+F022 |
| `fa-tasks` | `list-check` | U+F0AE |

Unchanged: `fa-book-open`, `fa-bullseye`, `fa-clipboard-check`, `fa-clock`,
`fa-flag-checkered`, `fa-folder-open`, `fa-lightbulb`, `fa-upload`,
`fa-user-shield`.

**No empty boxes, ever.** Any `fa-*` class not in the subset falls back to a
typographic bullet drawn in the body font, never a tofu square. All 18 glyphs
were confirmed rendering in a headless browser; see `preview.html`, which lists
the complete set at the bottom.

**To regenerate the subset:**

```bash
curl -sLO https://registry.npmjs.org/@fortawesome/fontawesome-free/-/fontawesome-free-6.7.2.tgz
tar xzf fontawesome-free-6.7.2.tgz
python -m fontTools.subset package/webfonts/fa-solid-900.woff2 \
  --unicodes=F35A,F518,F5DA,F140,F14A,F46C,F071,F11E,F256,F05A,F0EB,F022,F0AE,F093,F505,F06A \
  --flavor=woff2 --no-hinting --desubroutinize --name-IDs='*' --output-file=solid.woff2
python -m fontTools.subset package/webfonts/fa-regular-400.woff2 \
  --unicodes=F017,F07C \
  --flavor=woff2 --no-hinting --desubroutinize --name-IDs='*' --output-file=regular.woff2
# then rewrite the name table to "ITSY Shim Icons" (OFL reserved-name clause)
# and base64 the results into the two @font-face rules.
```

---

## 5. Contrast

Every colour pair in the stylesheet was computed against WCAG 2.1. Text pairs are
measured against AA (4.5:1); borders, keylines, and decorative icons against the
3:1 non-text threshold. **Nothing fails, and most text clears AAA (7:1).**

### Light

| Pair | Ratio |
|---|---|
| Body text `#1a2027` on page `#ffffff` | **16.41:1** |
| Body text on block surface `#f5f7f9` | **15.28:1** |
| Body text on code panel `#eceff4` | **14.24:1** |
| Body text on table header `#e4e9f0` | **13.45:1** |
| Body text on table stripe `#f7f9fb` | **15.55:1** |
| Page title `#ffffff` on header bar `#14384f` | **12.29:1** |
| Link `#0a5a8a` on page / on block | **7.39:1** / **6.88:1** |
| Muted text `#4d5866` on block / code panel / page | **6.74:1** / **6.28:1** / **7.23:1** |
| note body text / kicker label | **11.71:1** / **6.22:1** |
| tip body text / kicker label | **12.35:1** / **5.83:1** |
| time body text / kicker label | **13.18:1** / **7.46:1** |
| warning body text / kicker label | **11.96:1** / **11.96:1** |
| stop body text / kicker label | **13.22:1** / **13.22:1** |
| Callout rules and icons (non-text) | **4.94:1** – **7.46:1** |
| Block keylines and icons (non-text) | **6.07:1** – **8.93:1** |

Lowest text pair: **5.83:1**. Lowest non-text pair: **4.94:1**.

### Dark

| Pair | Ratio |
|---|---|
| Body text `#e4eaf1` on page `#12161b` | **14.99:1** |
| Body text on block surface `#1b212a` | **13.36:1** |
| Body text on code panel `#232c37` | **11.66:1** |
| Body text on table header `#28323e` | **10.73:1** |
| Body text on table stripe `#1f2731` | **12.45:1** |
| Page title `#eef4f8` on header bar `#1b465f` | **9.07:1** |
| Link `#79c2ee` on page / on block | **9.31:1** / **8.30:1** |
| Muted text `#a3b0be` on block / code panel / page | **7.33:1** / **6.40:1** / **8.23:1** |
| note body text / kicker label | **12.68:1** / **5.95:1** |
| tip body text / kicker label | **13.66:1** / **7.35:1** |
| time body text / kicker label | **13.07:1** / **6.08:1** |
| warning body text / kicker label | **13.18:1** / **13.18:1** |
| stop body text / kicker label | **13.24:1** / **13.24:1** |
| Callout rules and icons (non-text) | **5.77:1** – **7.35:1** |
| Block keylines and icons (non-text) | **5.57:1** – **7.24:1** |

Lowest text pair: **5.95:1**. Lowest non-text pair: **5.57:1**.

The single lowest number anywhere is the light-mode warning rule at 4.94:1. That
colour is used for a border and a decorative `aria-hidden` icon, never for text;
the warning callout's own label and body text sit at 11.96:1.

---

## 6. How `apply_theme.py` installs it, and why it works that way

**Short version: there is no clean token-authenticated API path, so the script
uses a session login. It was implemented and tested against the running
instance, and it works.**

Three findings drove the design. All three were read out of the Canvas source in
`canvas/canvas-lms` and then confirmed by observing the live instance.

### 6.1 Bearer tokens cannot install a theme

The theme routes live at `/accounts/:id/brand_configs`, declared in
`config/routes.rb:762-768`, **outside** the `/api/` namespace. Canvas only
honours `Authorization: Bearer` on paths matching `%r{\A/api/}`
(`lib/authentication_methods.rb`, `load_pseudonym_from_access_token`), and
`BrandConfigsController` is not one of the few controllers that opt out. Under
`/api/v1` the only brand endpoints are read-only (`brand_variables`) or merely
name an existing config (`shared_brand_configs`). `BrandConfigsController` has no
`@API` annotation at all — it is deliberately not public API.

`brand_config_md5` is also silently dropped by the JSON API: `AccountsController#update`
returns `update_api` early for API requests, and that path only applies
`name`, `default_time_zone`, and `settings`.

So `CANVAS_TOKEN` genuinely cannot do this job. The script logs in with a
username and password, then sends the `X-CSRF-Token` header Canvas requires on
non-API POSTs. (Two mechanical traps, both handled: the `_csrf_token` cookie is
percent-encoded and must be unquoted before it compares equal server-side, and
Canvas re-masks it on every response, so it is re-read before each write.)

The token is still used for a read-only preflight, because every other script in
this repo depends on it and it is worth failing early if it has gone stale.

### 6.2 Uploading the CSS as a *file* produces a broken link

This is the interesting one, and it is a real trap for anyone doing this by hand.

Canvas stores `css_overrides` as a **URL string** and emits it as a `<link>`.
When you upload a file, the URL is built from `config/domain.yml`, which in this
Docker deployment says:

```yaml
development:
  domain: "canvas.docker"
```

So the theme's stylesheet link comes back as
`http://canvas.docker/accounts/1/files/38/download?verifier=...`. A browser
pointed at `http://localhost:3000` cannot resolve that hostname. Observed
directly: the `<link>` was present in the page head and the request failed with
`NameResolutionError`. The download also redirects through a signed JWT with a
five-minute expiry.

**This affects the Theme Editor UI too**, not just the script. Uploading
`designplus-shim.css` through Admin → Themes on this deployment produces a
stylesheet that does not load.

**The fix used instead:** install the CSS as a
`data:text/css;base64,...` URI. Rails' asset helper passes `data:` URIs through
untouched, so the whole stylesheet ends up inline in the page head. There is no
second request to fail, no hostname to resolve, and nothing to expire. It also
happens to be the most offline-proof option available.

Cost: the 43,800-byte stylesheet becomes a 58,421-byte `data:` URI. Canvas's
`css_overrides` column is `text`, so this is not close to a limit. Canvas's own
CSP (`frame-ancestors 'self' canvas.docker`) does not restrict stylesheet
sources, so `data:` stylesheets are not blocked.

### 6.3 Custom CSS is ignored unless the account allows it

`Account#allow_global_includes?` defaults to **false**, and while it is false
Canvas silently discards the account's `css_overrides` and falls back to Site
Admin's. The script turns the `global_includes` setting on first and verifies it
stuck. In the Canvas UI this is the checkbox labelled **"Custom CSS/JavaScript
overrides"** in Admin → Settings.

Activation uses `PUT /accounts/:id` with `account[brand_config_md5]`, which
assigns the config **synchronously**. The Theme Editor's own two-step
(`save_to_user_session` then `save_to_account`) defers the real assignment to a
`Delayed::Job` and silently does nothing when no jobs worker is running, so it is
not used.

### 6.4 Credentials

`apply_theme.py` reads `canvas/.canvas-credentials` (`KEY=VALUE` per line), then
environment variables, then command-line flags, in increasing order of
precedence. It understands:

| Key | Purpose |
|---|---|
| `CANVAS_URL` | Base URL. Default `http://localhost:3000`. |
| `CANVAS_TOKEN` | Read-only preflight only. **Cannot install the theme** — see 6.1. |
| `CANVAS_ADMIN_EMAIL` | Admin login. Default `admin@itsy1377.local`, from `setup.sh`. |
| `CANVAS_ADMIN_PASSWORD` | Admin password. Prompted for interactively if absent. |

`setup.sh` writes only `CANVAS_URL` and `CANVAS_TOKEN` into that file. **The
password is not stored there and the script does not write it there.** If you
run non-interactively, supply `CANVAS_ADMIN_PASSWORD` in the environment or pass
`--password`; otherwise the script prompts.

### 6.5 What it prints

```
==> Connecting to http://localhost:3000
  CANVAS_TOKEN is valid (user: admin@itsy1377.local)
==> Signing in
  signed in as admin@itsy1377.local (user id 2)
  root account: 1 (Northeast Lakeview College (ITSY 1377 Demo))
==> Enabling custom CSS on the account
  custom CSS/JavaScript overrides enabled: True
==> Uploading the stylesheet
  stylesheet: 43,800 bytes -> 58,421 byte data: URI
  brand config created: a6f9be07146e6abe6d4a1af527328f44
==> Applying it to the account
  theme applied to the account
==> Verifying against a rendered page
  verified: 43,800 bytes served in the page head, byte-for-byte identical to designplus-shim.css
```

The last step is the one that matters. It does not trust the API's "OK"; it
fetches a real page, pulls the stylesheet out of the head, decodes it, and
compares it byte-for-byte with the file on disk.

`--manual` prints by-hand Theme Editor steps, including the `canvas.docker`
caveat from 6.2 and how to fix it in `config/domain.yml` if you would rather use
the UI.

---

## 7. What was verified, and what was not

**Verified against the running Canvas at `http://localhost:3000`:**

- Session login, CSRF handling, and admin authorization.
- `global_includes` flipped on and read back as `true`.
- Brand config created; the stored `css_overrides` matched what was sent exactly.
- `brand_config_md5` assigned to root account 1 and read back.
- The stylesheet appears in the `<head>` of a real course page
  (`/courses/1/pages/rules-of-engagement`), and its decoded bytes are
  **byte-for-byte identical** to `designplus-shim.css` on disk.
- That page's markup carries `dp-wrapper`, `dp-header`, `dp-header-title`,
  `dp-content-block`, `dp-callout-stop`, `kl_custom_block_7`, `dp-has-icon`,
  and `fa-user-shield`, so the selectors match real content.
- `--check` and `--manual` both work; the no-password non-interactive path
  fails with a useful message rather than a traceback.
- The file-upload path is broken on this deployment (`canvas.docker` does not
  resolve) — confirmed by observing the failure, which is why the `data:` URI
  path exists.
- Rendering: `preview.html` was screenshotted in headless Chrome in both light
  and dark, and the real Week 5 Overview page body was rendered against
  Canvas's own five stylesheets plus the shim, confirming no conflict with
  Canvas's `ic-Table` and typography rules. All 18 icons render.

**Not verified:**

- **No screenshot of a logged-in Canvas page in a real browser session.** Canvas
  renders wiki page bodies client-side via XHR, which cannot run from a
  `file://` snapshot. The two renders above cover the same CSS against the same
  markup and the same Canvas stylesheets, but a human should still click through
  one page in a browser before showing this to anyone.
- **Not tested on any Canvas other than this one.** In particular the
  `canvas.docker` problem is specific to this deployment's `domain.yml`; a
  Canvas with a correct domain could use the file-upload path instead.
- **Not tested against Alamo's production Canvas**, and it must never be
  installed there. Alamo has a real DesignPLUS license; this would fight it.
- **Sub-accounts.** Only the root account was themed. Because
  `PUT /accounts/:id` is used instead of `BrandConfigRegenerator`, existing
  sub-account brand configs are not re-parented or regenerated. There are no
  sub-account themes in this deployment, so it does not arise here.
- **Browser coverage.** Verified in Chrome only. The stylesheet uses `:has()`
  for the code-block language tag, which degrades to no corner tag on older
  browsers; nothing else depends on it.

**Substituted or worked around:**

- **Font family renamed** from "Font Awesome" to "ITSY Shim Icons", as OFL 1.1
  requires for a modified font. See section 4.
- **`data:` URI instead of a file upload** for `css_overrides`, for the reason
  in 6.2.
- **A password is required** and the credentials file does not carry one, for
  the reason in 6.1. This is the one place where the deliverable could not use
  only what `.canvas-credentials` provides.
- **DesignPLUS accordions render open** rather than collapsed, since there is no
  JavaScript to open them.

---

## 8. License

`designplus-shim.css`, `apply_theme.py`, `preview.html`, and this README are
released under **CC0 1.0 Universal** (public domain dedication), so the college
can keep, modify, or discard them without conditions.

The embedded icon font is a renamed subset of **Font Awesome Free 6.7.2**,
Copyright (c) 2024 Fonticons, Inc., under **SIL OFL 1.1**. Font Awesome Free's
icons are **CC BY 4.0**, its fonts **SIL OFL 1.1**, and its code **MIT**. See
section 4.

No Cidi Labs intellectual property is included in any form.
