"""Slide scenes: Jinja to HTML to PNG, one PNG per reveal state.

Rendered by headless Chrome rather than a screenshot library, for one practical
reason: Chrome is already on this machine and its browser binaries are already
cached, so the slide renderer adds no download. It is also the same engine that
will render the Canvas page the video sits on, which means a font that resolves
here resolves there.

Bullets reveal one at a time by rendering the same slide once per reveal state
and cutting between the stills at measured cue boundaries. That costs a few
extra screenshots and is what stops a static deck from feeling static. There is
no animation and no video filter involved.
"""

from __future__ import annotations

import os
import html
import re
import shutil
import subprocess
from pathlib import Path

from jinja2 import Environment
from markupsafe import Markup

from . import config as _config

ROOT = _config.find_root()
VIDEO_DIR = ROOT / os.environ.get("ITSY_CONTENT", "content") / "video"

WIDTH, HEIGHT = 1920, 1080

# Chrome, in the order we prefer it. The cached headless shells come from
# Playwright and Puppeteer installs that already happened on this machine; the
# app bundle is the reliable fallback. Whichever answers first is used.
# The full app bundle first, deliberately. chrome-headless-shell starts faster
# but does not resolve the user font book on macOS, so Inter and JetBrains Mono
# fell back to a serif and every slide shipped in the wrong typeface. Nothing
# errored; the frames just looked wrong.
CHROME_CANDIDATES = [
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-mac-arm64/chrome-headless-shell",
]


class SlideError(Exception):
    pass


def _nl2br(value: str) -> Markup:
    """Escape each line, then join with a real line break.

    The return has to be Markup. Returning a plain string meant Jinja escaped
    the filter's own output a second time, and slides shipped showing a literal
    <br> and &quot; where a line break and a quotation mark belonged. Caught by
    looking at a rendered frame, which is the only way that class of bug shows.
    """
    return Markup("<br>".join(html.escape(line) for line in str(value).split("\n")))


def _env() -> Environment:
    env = Environment(autoescape=True)
    env.filters["nl2br"] = _nl2br
    env.filters["trim"] = lambda s: str(s).strip()
    return env


def find_chrome() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    found = shutil.which("chromium") or shutil.which("google-chrome")
    if found:
        return Path(found)
    raise SlideError(
        "No Chrome found for slide rendering. Install Google Chrome, or run\n"
        "  python -m playwright install chromium")


def render_html(scene, reveal: int) -> str:
    """Slide HTML for one reveal state.

    The stylesheet is passed as Markup, not as a string. Autoescape turned
    --sans:"Inter" into --sans:&#34;Inter&#34;, which is not a valid font stack,
    so every slide silently fell back to the browser's default serif. The
    palette still looked right because hex colours contain nothing to escape,
    which is exactly why it survived a look at the frames.
    """
    template = _env().from_string((VIDEO_DIR / "slide.html.j2").read_text(encoding="utf-8"))
    html_out = template.render(
        scene=scene, reveal=reveal,
        theme=Markup((VIDEO_DIR / "theme.css").read_text(encoding="utf-8")),
        course_code=_config.load().course_code,
        course_name=_config.load().course_name)
    _assert_css_intact(html_out)
    return html_out


# An escaped stylesheet produces a page that renders, so nothing downstream can
# notice. This is the check that would have caught it.
ENTITY_RE = re.compile(r"&(?:#\d+|amp|quot|lt|gt|#x[0-9a-fA-F]+);")


def _assert_css_intact(document: str) -> None:
    start = document.find("<style>")
    end = document.find("</style>", start)
    if start == -1 or end == -1:
        raise SlideError("The slide template lost its <style> block.")
    found = ENTITY_RE.search(document[start:end])
    if found:
        raise SlideError(
            f"The stylesheet reached the page HTML escaped, at {found.group(0)!r}.\n"
            f"  Pass it through markupsafe.Markup. An escaped font stack does not "
            f"error, it just renders every slide in the wrong typeface.")


def render_png(scene, reveal: int, out: Path) -> Path:
    """One reveal state to one PNG. Deterministic: same input, same bytes."""
    # Resolve first. Path.as_uri() raises on a relative path, so calling this
    # with anything repo relative failed on a file:// URL rather than on
    # anything to do with rendering.
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    page = out.with_suffix(".html")
    page.write_text(render_html(scene, reveal), encoding="utf-8")
    result = subprocess.run(
        [str(find_chrome()), "--headless", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", "--default-background-color=FFFAF9F7",
         f"--window-size={WIDTH},{HEIGHT}", f"--screenshot={out}", page.as_uri()],
        capture_output=True, text=True)
    if not out.exists():
        raise SlideError(f"Chrome produced no screenshot for {out.name}.\n{result.stderr[-600:]}")
    return out
