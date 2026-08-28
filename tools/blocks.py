"""Turn authored markdown into the HTML the NLC template expects.

Course pages are written as markdown with block directives:

    ::: intro
    One or two sentences saying what this page is for.
    :::

    ::: objectives
    - Do the thing
    - Do the other thing
    :::

    ::: callout warning | Read this before you start
    Everything in here is a warning.
    :::

Each directive becomes one `dp-content-block` div carrying the exact Cidi Labs
DesignPLUS class names used by the NLC Online Course Template, plus the Font
Awesome icon that template pairs with that kind of block.

Why keep the DesignPLUS class names when the local demo has no DesignPLUS
license? Because the content is authored for production, not for the demo.
Every page here is drop-in compatible with the college's real Canvas, where
DesignPLUS styles it correctly with no rework. Locally, canvas/theme/ supplies
a small openly licensed stylesheet that reproduces the structure so the demo
reads as a designed course. No Cidi Labs CSS or JavaScript is copied.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import markdown as markdown_lib

# The kinds of block this course uses, with the class and icon the template
# pairs with each. Names on the left are what an author writes.
BLOCKS = {
    "intro":      {"cls": "kl_introduction",   "icon": None,                        "title": None},
    "objectives": {"cls": "kl_objectives2",    "icon": "fas fa-bullseye",           "title": "Learning Objectives"},
    "tasks":      {"cls": "kl_assignments2",   "icon": "fas fa-tasks",              "title": "Tasks"},
    "section":    {"cls": "kl_custom_block_1", "icon": None,                        "title": None},
    "directions": {"cls": "kl_custom_block_1", "icon": "fas fa-list-alt",           "title": "Directions"},
    "grading":    {"cls": "kl_custom_block_2", "icon": "fas fa-check-square",       "title": "Grading Criteria"},
    "submit":     {"cls": "kl_custom_block_3", "icon": "fas fa-upload",             "title": "How to Submit"},
    "sources":    {"cls": "kl_custom_block_3", "icon": "far fa-folder-open",        "title": "Sources"},
    "learned":    {"cls": "kl_custom_block_0", "icon": "fas fa-book-open",          "title": "What You Learned"},
    "did":        {"cls": "kl_custom_block_1", "icon": "fas fa-clipboard-check",    "title": "What You Did"},
    "next":       {"cls": "kl_custom_block_2", "icon": "fas fa-arrow-alt-circle-right", "title": "What's Next"},
    "callout":    {"cls": "kl_custom_block_4", "icon": "fas fa-exclamation-circle", "title": None},
    "reading":    {"cls": "kl_custom_block_5", "icon": "fas fa-book-reader",        "title": "Before You Read This"},
    "checkpoint": {"cls": "kl_custom_block_6", "icon": "fas fa-flag-checkered",     "title": "Check Yourself"},
    "scope":      {"cls": "kl_custom_block_7", "icon": "fas fa-user-shield",        "title": "Authorization and Scope"},
}

CALLOUT_ICONS = {
    "warning": "fas fa-exclamation-triangle",
    "note":    "fas fa-info-circle",
    "tip":     "fas fa-lightbulb",
    "stop":    "fas fa-hand-paper",
    "time":    "far fa-clock",
}

OPEN_RE = re.compile(r"^:::\s*(?P<name>[a-z_]+)(?:\s+(?P<arg>[^|\n]+?))?(?:\s*\|\s*(?P<title>.+?))?\s*$")
CLOSE_RE = re.compile(r"^:::\s*$")

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "attr_list", "md_in_html"]


class BlockError(Exception):
    """A page used a directive that does not exist, or forgot to close one."""


@dataclass
class Block:
    name: str
    arg: str | None
    title: str | None
    body: str
    line: int


def parse_blocks(text: str, source: str = "<page>") -> list[Block]:
    blocks: list[Block] = []
    current: Block | None = None
    buffer: list[str] = []

    for number, line in enumerate(text.splitlines(), start=1):
        if current is None:
            match = OPEN_RE.match(line)
            if match:
                name = match.group("name")
                if name not in BLOCKS:
                    raise BlockError(
                        f"{source}:{number}: there is no block called ':::{name}'.\n"
                        f"  Available: {', '.join(sorted(BLOCKS))}"
                    )
                current = Block(name, match.group("arg"), match.group("title"), "", number)
                buffer = []
            elif line.strip():
                raise BlockError(
                    f"{source}:{number}: text outside a block.\n"
                    f"  Every line on a page has to sit inside a ::: block. Got: {line[:60]!r}"
                )
        else:
            if CLOSE_RE.match(line):
                current.body = "\n".join(buffer).strip("\n")
                blocks.append(current)
                current = None
            else:
                buffer.append(line)

    if current is not None:
        raise BlockError(f"{source}:{current.line}: block ':::{current.name}' was never closed.")
    if not blocks:
        raise BlockError(f"{source}: no blocks found. A page needs at least one.")
    return blocks


def _icon_html(icon: str) -> str:
    return (f'<i class="{icon} dp-i-size-small" aria-hidden="true">'
            f'<span class="dp-icon-content" style="display: none;">&nbsp;</span></i>')


def _heading(icon: str | None, title: str) -> str:
    if icon:
        return (f'<h3 class="dp-has-icon">{_icon_html(icon)}'
                f'<span style="font-size: 14pt;"> {html.escape(title)}</span></h3>')
    return f'<h3><span style="font-size: 14pt;">{html.escape(title)}</span></h3>'


def render_block(block: Block) -> str:
    spec = BLOCKS[block.name]
    cls = spec["cls"]
    icon = spec["icon"]
    title = block.title or spec["title"]

    if block.name == "callout":
        flavor = (block.arg or "note").strip()
        if flavor not in CALLOUT_ICONS:
            raise BlockError(
                f"line {block.line}: '{flavor}' is not a callout kind.\n"
                f"  Use one of: {', '.join(sorted(CALLOUT_ICONS))}"
            )
        icon = CALLOUT_ICONS[flavor]
        cls = f"kl_custom_block_4 dp-callout dp-callout-{flavor}"

    body = markdown_lib.markdown(block.body, extensions=MD_EXTENSIONS)
    body = body.replace("<table>", '<table class="ic-Table table-bordered ic-Table--striped '
                                   'ic-Table--hover-row ic-Table--condensed">')

    parts = [f'<div class="dp-content-block {cls}">']
    if title:
        parts.append(_heading(icon, title))
    parts.append(body)
    parts.append("</div>")
    return "\n".join(parts)


def render_page(text: str, page_title: str, source: str = "<page>") -> str:
    """Full page HTML, wrapped the way every template page is wrapped."""
    blocks = parse_blocks(text, source)
    inner = "\n".join(render_block(block) for block in blocks)
    escaped = html.escape(page_title)
    return (
        f'<div id="dp-wrapper" class="dp-wrapper dp-basic-bar">'
        f'<header class="dp-header dp-basic-bar ">\n'
        f'<h2 class="dp-heading"><span class="dp-header-title" style="font-size: 18pt;">'
        f'{escaped}</span></h2>\n'
        f'</header>\n'
        f'{inner}\n'
        f'</div>'
    )


def render_document(text: str, page_title: str, source: str = "<page>") -> str:
    """A complete standalone HTML file, as a Common Cartridge carries it."""
    body = render_page(text, page_title, source)
    return (
        '<html>\n<head>\n'
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
        f'<title>{html.escape(page_title)}</title>\n'
        '<meta name="editing_roles" content="teachers"/>\n'
        '<meta name="workflow_state" content="active"/>\n'
        '</head>\n<body>\n'
        f'{body}\n'
        '</body>\n</html>'
    )
