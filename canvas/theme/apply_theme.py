#!/usr/bin/env python3
"""Install designplus-shim.css into the local Canvas as account-level custom CSS.

    python canvas/theme/apply_theme.py            # install / update the shim
    python canvas/theme/apply_theme.py --check    # report what is installed now
    python canvas/theme/apply_theme.py --remove   # detach the shim from the account
    python canvas/theme/apply_theme.py --manual   # print the by-hand steps and exit

WHY THIS SCRIPT LOOKS THE WAY IT DOES
-------------------------------------
Three findings about Canvas drove every design decision here. All three were
read out of the Canvas source in canvas/canvas-lms and then confirmed against
the running instance.

1. There is no token-authenticated API for brand configs.
   The theme routes live at /accounts/:id/brand_configs, outside /api/, and
   Canvas only honours `Authorization: Bearer` on paths matching %r{\\A/api/}
   (lib/authentication_methods.rb, load_pseudonym_from_access_token). Under
   /api/v1 the only brand endpoints are read-only (`brand_variables`) or merely
   name an existing config (`shared_brand_configs`). So CANVAS_TOKEN cannot do
   this job. The script logs in with a username and password to get a session
   cookie, and sends the CSRF token Canvas requires on non-API POSTs.

2. Uploading the CSS as a file produces a URL the browser cannot fetch.
   Canvas stores `css_overrides` as a URL string and emits it as a <link>. When
   you upload a file, that URL is built from config/domain.yml, which on this
   Docker deployment is "canvas.docker" -- a name that does not resolve from
   the host browser at localhost:3000. The download also redirects through a
   short-lived signed JWT. Both were observed failing.

   So the CSS is installed as a `data:text/css;base64,...` URI instead. Rails'
   asset helper passes `data:` URIs through untouched, the stylesheet is then
   self-contained in the page head, there is no second request to fail, no host
   to resolve, and nothing to expire. This was verified end to end: the bytes
   in the rendered page match this repo's CSS file exactly.

3. Custom CSS is ignored unless the account allows it.
   Account#allow_global_includes? defaults to false. The script turns the
   `global_includes` setting on first and verifies it stuck.

Activation uses PUT /accounts/:id with account[brand_config_md5], which assigns
the config synchronously. The Theme Editor's own two-step
(save_to_user_session then save_to_account) defers the real work to a
Delayed::Job, so it silently does nothing when no jobs worker is running.
"""

from __future__ import annotations

import argparse
import base64
import getpass
import os
import re
import sys
import urllib.parse
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("This script needs the 'requests' package.\n  pip install requests")


HERE = Path(__file__).resolve().parent
CSS_PATH = HERE / "designplus-shim.css"
CREDENTIALS = HERE.parent / ".canvas-credentials"

# Defaults from canvas/deploy/setup.sh, which creates this admin.
DEFAULT_URL = "http://localhost:3000"
DEFAULT_USER = "admin@itsy1377.local"

TIMEOUT = 180


# ---------------------------------------------------------------------------
# output helpers
# ---------------------------------------------------------------------------

def say(msg: str) -> None:
    print(f"  {msg}")


def step(msg: str) -> None:
    print(f"\n\033[1;36m==>\033[0m {msg}")


def warn(msg: str) -> None:
    print(f"\033[1;33mWARNING:\033[0m {msg}", file=sys.stderr)


def die(msg: str) -> "None":
    print(f"\n\033[1;31mERROR:\033[0m {msg}", file=sys.stderr)
    print("\nRun with --manual for by-hand instructions.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# credentials
# ---------------------------------------------------------------------------

def read_credentials(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE lines. Missing file is not fatal; flags and env can fill in."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def resolve_settings(args: argparse.Namespace) -> dict[str, str]:
    creds = read_credentials(Path(args.credentials))

    def pick(*keys: str, default: str = "") -> str:
        for key in keys:
            if os.environ.get(key):
                return os.environ[key]
        for key in keys:
            if creds.get(key):
                return creds[key]
        return default

    url = args.url or pick("CANVAS_URL", default=DEFAULT_URL)
    return {
        "url": url.rstrip("/"),
        "token": pick("CANVAS_TOKEN"),
        "user": args.user or pick("CANVAS_ADMIN_EMAIL", "CANVAS_USER", default=DEFAULT_USER),
        "password": args.password or pick("CANVAS_ADMIN_PASSWORD", "CANVAS_PASSWORD"),
        "creds_path": str(args.credentials),
        "creds_found": str(bool(creds)),
    }


# ---------------------------------------------------------------------------
# Canvas session
# ---------------------------------------------------------------------------

class Canvas:
    """A logged-in Canvas session that can drive the non-API theme routes."""

    def __init__(self, base: str):
        self.base = base
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "itsy1377-apply-theme"

    def url(self, path: str) -> str:
        return f"{self.base}{path}"

    @property
    def csrf(self) -> str:
        """Canvas re-masks this cookie on every response, so always re-read it.

        The value is base64 and Rails percent-encodes it on the way out, so it
        has to be unquoted before it will compare equal server-side.
        """
        raw = self.s.cookies.get("_csrf_token")
        return urllib.parse.unquote(raw) if raw else ""

    def headers(self) -> dict[str, str]:
        return {"X-CSRF-Token": self.csrf, "Accept": "application/json"}

    def reachable(self) -> None:
        try:
            self.s.get(self.url("/login/canvas"), timeout=30)
        except requests.RequestException as exc:
            die(f"Cannot reach Canvas at {self.base}\n  {exc}\n\n"
                "  Is it running?   ./canvas/deploy/setup.sh --start")

    def check_token(self, token: str) -> None:
        """Read-only preflight with CANVAS_TOKEN.

        The token cannot install a theme (see the module docstring), but if one
        is configured it is worth confirming it works, because every other
        script in this repo depends on it.
        """
        if not token:
            say("no CANVAS_TOKEN configured - skipping token preflight")
            return
        r = requests.get(self.url("/api/v1/users/self"),
                         headers={"Authorization": f"Bearer {token}"}, timeout=30)
        if r.status_code == 200:
            say(f"CANVAS_TOKEN is valid (user: {r.json().get('name')})")
        else:
            warn(f"CANVAS_TOKEN did not authenticate (HTTP {r.status_code}). "
                 "Not fatal here, but other scripts in this repo will fail.")

    def login(self, user: str, password: str) -> None:
        r = self.s.get(self.url("/login/canvas"), timeout=60)
        m = re.search(r'name="authenticity_token"\s+value="([^"]+)"', r.text)
        if not m:
            die("Could not find the login form. Is this really a Canvas instance?")
        r = self.s.post(
            self.url("/login/canvas"),
            data={
                "utf8": "✓",
                "authenticity_token": m.group(1),
                "redirect_to_ssl": "1",
                "pseudonym_session[unique_id]": user,
                "pseudonym_session[password]": password,
            },
            allow_redirects=True, timeout=90,
        )
        who = self.s.get(self.url("/api/v1/users/self"), timeout=30)
        if who.status_code != 200:
            die(f"Login failed for {user} (HTTP {r.status_code}).\n"
                "  Check the username and password. The defaults come from\n"
                "  canvas/deploy/setup.sh (CANVAS_ADMIN_EMAIL / CANVAS_ADMIN_PASSWORD).")
        say(f"signed in as {who.json().get('name')} (user id {who.json().get('id')})")

    def root_account(self, override: int | None) -> int:
        if override:
            return override
        r = self.s.get(self.url("/api/v1/accounts?per_page=50"), timeout=60)
        if r.status_code == 200:
            for acct in r.json():
                if acct.get("parent_account_id") is None:
                    say(f"root account: {acct['id']} ({acct['name']})")
                    return int(acct["id"])
        warn("Could not resolve the root account; assuming 1.")
        return 1

    # -- the actual work ----------------------------------------------------

    def enable_global_includes(self, account: int) -> bool:
        """Account#allow_global_includes? defaults to false, and while it is
        false Canvas ignores this account's css_overrides entirely."""
        r = self.s.put(self.url(f"/accounts/{account}"), headers=self.headers(),
                       data={"account[settings][global_includes]": "1"}, timeout=90)
        if r.status_code >= 400:
            warn(f"Could not set global_includes (HTTP {r.status_code}). "
                 "Custom CSS may be ignored.")
            return False
        on = '"global_includes":true' in r.text
        say(f"custom CSS/JavaScript overrides enabled: {on}")
        if not on:
            warn("global_includes did not stick. This usually means the account\n"
                 "         needs an admin with the 'manage_site_settings' permission.")
        return on

    def upload_css(self, account: int, css: str) -> str:
        """Create a brand config whose css_overrides is a self-contained data: URI.

        Returns the new config's md5.
        """
        uri = "data:text/css;base64," + base64.b64encode(css.encode("utf-8")).decode("ascii")
        say(f"stylesheet: {len(css.encode('utf-8')):,} bytes -> {len(uri):,} byte data: URI")
        if len(uri) > 2_000_000:
            warn("That data: URI is very large. Consider trimming the stylesheet.")

        r = self.s.post(self.url(f"/accounts/{account}/brand_configs"),
                        headers=self.headers(), data={"css_overrides": uri}, timeout=TIMEOUT)
        if r.status_code >= 400:
            die(f"Creating the brand config failed (HTTP {r.status_code})\n  {r.text[:400]}")
        config = r.json()["brand_config"]
        if config.get("css_overrides") != uri:
            die("Canvas stored something other than what we sent. Aborting rather "
                "than activating a half-written theme.")
        say(f"brand config created: {config['md5']}")
        return config["md5"]

    def activate(self, account: int, md5: str | None) -> None:
        """Assign the config to the account. Synchronous: no jobs worker needed."""
        r = self.s.put(self.url(f"/accounts/{account}"), headers=self.headers(),
                       data={"account[brand_config_md5]": md5 or ""}, timeout=90)
        if r.status_code >= 400:
            die(f"Activating the theme failed (HTTP {r.status_code})\n  {r.text[:400]}")
        got = re.search(r'"brand_config_md5":"?([^",]*)"?', r.text)
        current = got.group(1) if got else ""
        if md5 and current != md5:
            die(f"Account brand_config_md5 is {current!r}, expected {md5!r}.")
        say("theme applied to the account" if md5 else "theme detached from the account")

    def verify(self, expected: str | None) -> bool:
        """Fetch a real page and check what the browser would actually receive.

        This is the only check that matters: not 'the API said OK' but 'the
        stylesheet is in the page and its bytes are the bytes on disk'.
        """
        r = self.s.get(self.url("/"), timeout=90)
        found = re.findall(r'<link[^>]+href="(data:text/css;base64,[^"]+)"', r.text)
        if expected is None:
            if found:
                warn("A data: stylesheet is still present in the page head.")
                return False
            say("no shim stylesheet in the page head, as expected")
            return True
        if not found:
            warn("No data: stylesheet found in the rendered page head.\n"
                 "         The theme was saved but Canvas is not serving it. The usual\n"
                 "         cause is that 'Custom CSS/JavaScript overrides' is off.")
            return False
        delivered = base64.b64decode(found[0].split(",", 1)[1]).decode("utf-8")
        if delivered != expected:
            warn("A stylesheet is being served, but it is not the current shim.")
            return False
        say(f"verified: {len(delivered.encode('utf-8')):,} bytes served in the page "
            "head, byte-for-byte identical to designplus-shim.css")
        return True

    def report(self, account: int) -> None:
        r = self.s.get(self.url(f"/api/v1/accounts/{account}"), timeout=60)
        acct = r.json() if r.status_code == 200 else {}
        say(f"account: {acct.get('name', '?')} (id {account})")
        r = self.s.get(self.url("/"), timeout=90)
        found = re.findall(r'<link[^>]+href="(data:text/css;base64,[^"]+)"', r.text)
        if not found:
            say("installed shim: none (no data: stylesheet in the page head)")
            return
        delivered = base64.b64decode(found[0].split(",", 1)[1]).decode("utf-8")
        local = CSS_PATH.read_text() if CSS_PATH.exists() else None
        say(f"installed shim: {len(delivered.encode('utf-8')):,} bytes")
        if local is None:
            say("local designplus-shim.css is missing, cannot compare")
        elif delivered == local:
            say("installed shim matches designplus-shim.css on disk")
        else:
            say("installed shim DIFFERS from designplus-shim.css on disk "
                "- re-run without --check to update it")


# ---------------------------------------------------------------------------
# manual fallback
# ---------------------------------------------------------------------------

MANUAL = """
Installing the shim by hand
===========================

Do this if the script cannot run, or if you would rather click through it.

Step 1. Allow custom CSS on the account.
  1. Sign in as an account admin.
  2. Admin > (your account) > Settings.
  3. Scroll to the checkbox labelled "Custom CSS/JavaScript overrides"
     and tick it.
  4. Click "Update Settings" at the bottom of the page.

  Without this, Canvas silently ignores the account's custom CSS.

Step 2. Load the stylesheet.
  1. Admin > (your account) > Themes.
  2. Open the current theme, then "Open in Theme Editor".
  3. In the "Upload" section, next to "CSS file", choose
       canvas/theme/designplus-shim.css
  4. "Preview Your Changes", then "Save theme", then "Apply theme".

  KNOWN PROBLEM WITH THIS DEPLOYMENT, and the reason the script does not use
  the file upload: Canvas builds the stylesheet's URL from config/domain.yml,
  which in this Docker setup is "canvas.docker". A browser pointed at
  http://localhost:3000 cannot resolve that name, so the <link> in the page
  head 404s and none of the styling appears. The download also redirects
  through a signed URL that expires.

  Two ways around it:

  (a) Let the script do it. It installs the CSS as a data: URI, so there is
      no second request to fail and nothing to resolve:

          python canvas/theme/apply_theme.py

  (b) Fix the hostname, then use the Theme Editor normally. Edit
      canvas/canvas-lms/config/domain.yml so the development block reads

          development:
            domain: "localhost:3000"

      then restart Canvas. This changes a file inside the vendored Canvas
      checkout, which is why the script does not do it for you.

Step 3. Check it worked.
  Open any course page and confirm the header bar is a solid navy band with
  the page title in it, and that callouts are tinted and labelled. Or run:

      python canvas/theme/apply_theme.py --check
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Install designplus-shim.css into a local Canvas as account CSS.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", help=f"Canvas base URL (default: {DEFAULT_URL})")
    p.add_argument("--user", help=f"admin login (default: {DEFAULT_USER})")
    p.add_argument("--password", help="admin password (prompted for if omitted)")
    p.add_argument("--account", type=int, help="root account id (default: auto-detect)")
    p.add_argument("--css", default=str(CSS_PATH), help="stylesheet to install")
    p.add_argument("--credentials", default=str(CREDENTIALS),
                   help="KEY=VALUE credentials file")
    p.add_argument("--check", action="store_true", help="report what is installed, change nothing")
    p.add_argument("--remove", action="store_true", help="detach the shim from the account")
    p.add_argument("--manual", action="store_true", help="print by-hand instructions and exit")
    args = p.parse_args()

    if args.manual:
        print(MANUAL)
        return 0

    cfg = resolve_settings(args)

    css_path = Path(args.css)
    css = ""
    if not args.check and not args.remove:
        if not css_path.exists():
            die(f"Stylesheet not found: {css_path}")
        css = css_path.read_text()
        if "@import" in re.sub(r"/\*.*?\*/", "", css, flags=re.S):
            die("The stylesheet contains an @import. The demo must work offline; "
                "inline the imported CSS instead.")

    step(f"Connecting to {cfg['url']}")
    if cfg["creds_found"] == "True":
        say(f"credentials file: {cfg['creds_path']}")
    else:
        say(f"no credentials file at {cfg['creds_path']} - using defaults, env, and flags")

    canvas = Canvas(cfg["url"])
    canvas.reachable()
    canvas.check_token(cfg["token"])

    password = cfg["password"]
    if not password:
        if not sys.stdin.isatty():
            die("No password available.\n"
                f"  Add CANVAS_ADMIN_PASSWORD to {cfg['creds_path']}, set it in the\n"
                "  environment, or pass --password. Brand configs cannot be installed\n"
                "  with CANVAS_TOKEN: Canvas only accepts bearer tokens on /api/ paths,\n"
                "  and the theme routes are not under /api/.")
        password = getpass.getpass(f"Password for {cfg['user']}: ")

    step("Signing in")
    say("CANVAS_TOKEN cannot install a theme; using a session login instead "
        "(see this script's docstring)")
    canvas.login(cfg["user"], password)
    account = canvas.root_account(args.account)

    if args.check:
        step("Current state")
        canvas.report(account)
        return 0

    if args.remove:
        step("Removing the shim")
        canvas.activate(account, None)
        step("Verifying")
        return 0 if canvas.verify(None) else 1

    step("Enabling custom CSS on the account")
    canvas.enable_global_includes(account)

    step("Uploading the stylesheet")
    md5 = canvas.upload_css(account, css)

    step("Applying it to the account")
    canvas.activate(account, md5)

    step("Verifying against a rendered page")
    ok = canvas.verify(css)

    print()
    if ok:
        print("\033[1;32mDone.\033[0m The shim is live at " + cfg["url"])
        print("Open any course page. Hard-refresh if you had the page open already.")
    else:
        print("\033[1;33mThe theme was saved but could not be verified.\033[0m")
        print("Run with --manual for the by-hand steps.")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
