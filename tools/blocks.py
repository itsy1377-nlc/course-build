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
    # The two below exist to make a page scannable rather than readable, which
    # is a different job. A student opening an orientation page is looking for
    # one fact. These put the facts where they can be found without reading.
    "keyfacts":   {"cls": "kl_custom_block_8 dp-keyfacts", "icon": "fas fa-bolt",        "title": "The short version"},
    "steps":      {"cls": "kl_custom_block_9 dp-steps",    "icon": "fas fa-shoe-prints", "title": "Do this now"},
}

# Read aloud by a screen reader, invisible on screen. The wording says what the
# reader should do with the block, not what colour it is.
CALLOUT_SEVERITY = {
    "warning": "Warning.",
    "stop":    "Stop. Read this before going further.",
    "note":    "Note.",
    "tip":     "Tip.",
    "time":    "How long this takes.",
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
    """An icon that carries no meaning, and says so.

    aria-hidden is correct here only because the icon is always next to a text
    heading that says the same thing. An icon is never the only carrier of
    meaning on these pages, which is what keeps this from being a WCAG failure.
    """
    return (f'<i class="{icon} dp-i-size-small" aria-hidden="true">'
            f'<span class="dp-icon-content" style="display: none;">&nbsp;</span></i>')


def _heading(icon: str | None, title: str) -> str:
    """A heading with no inline font size.

    The NLC template's pages carry `style="font-size: 14pt;"` on every heading,
    which are artifacts of the rich text editor rather than anything DesignPLUS
    needs. They are dropped here for two reasons. A fixed point size ignores a
    reader who has set a larger default font, which is a real accessibility
    problem for a real part of this audience. And the class names are what make
    a page drop-in compatible with the college's DesignPLUS, not the inline
    styles, so nothing is lost by leaving sizing to the stylesheet.
    """
    label = html.escape(title)
    if icon:
        return f'<h3 class="dp-has-icon">{_icon_html(icon)}<span> {label}</span></h3>'
    return f"<h3>{label}</h3>"


def render_block(block: Block, source: str = "<page>") -> str:
    spec = BLOCKS[block.name]
    cls = spec["cls"]
    icon = spec["icon"]
    title = block.title or spec["title"]

    severity = ""
    if block.name == "callout":
        flavor = (block.arg or "note").strip()
        if flavor not in CALLOUT_ICONS:
            raise BlockError(
                f"{source}:{block.line}: '{flavor}' is not a callout kind.\n"
                f"  Use one of: {', '.join(sorted(CALLOUT_ICONS))}"
            )
        icon = CALLOUT_ICONS[flavor]
        cls = f"kl_custom_block_4 dp-callout dp-callout-{flavor}"
        # How urgent this is has to live in the HTML, not in a stylesheet.
        #
        # A callout carries its severity three ways: colour, an icon, and a
        # generated text label. The icon is aria-hidden, and the label comes
        # from the local demo stylesheet. In production the styling comes from
        # the college's DesignPLUS licence, which may not supply that label at
        # all. A screen reader user would then get the heading and no sense of
        # whether it was a warning or a tip.
        #
        # So the word goes in the markup, visually hidden, and survives
        # whatever stylesheet is in front of it.
        severity = CALLOUT_SEVERITY[flavor]

    body = markdown_lib.markdown(block.body, extensions=MD_EXTENSIONS)
    body = _accessible_tables(body, block, source)

    parts = [f'<div class="dp-content-block {cls}">']
    if severity:
        parts.append(f'<span class="dp-sr-only">{severity}</span>')
    if title:
        parts.append(_heading(icon, title))
    parts.append(body)
    parts.append("</div>")
    return "\n".join(parts)


TABLE_CLASSES = ("ic-Table table-bordered ic-Table--striped "
                 "ic-Table--hover-row ic-Table--condensed")


def _accessible_tables(body: str, block: Block, source: str = "<page>") -> str:
    """Make every generated table readable by a screen reader.

    Markdown produces a bare `<table>` with `<th>` cells and nothing else. A
    screen reader then has no way to tell which header belongs to which cell,
    which turns a comparison table into a flat list of words. Three additions
    fix it, and the NLC template's own tables do all three:

      - a <caption>, so the table announces what it is
      - scope="col" on every header cell in the head
      - scope="row" on the first cell of every body row, so each row announces
        what it is about before reading its values

    The caption text is the block's heading, or the block kind's default
    heading when it has none. Every block that contains a table in this course
    has a title, so the "Table" fallback never fires in practice.
    """
    if "<table>" not in body:
        return body

    caption = block.title or BLOCKS[block.name]["title"] or "Table"
    if body.count("<table>") > 1:
        raise BlockError(
            f"{source}:{block.line}: this block has more than one table, and they "
            f"would share a caption.\n"
            f"  Split it into one ::: block per table, each with its own heading."
        )
    body = body.replace(
        "<table>",
        f'<table class="{TABLE_CLASSES}">\n'
        f'<caption class="dp-caption-t">{html.escape(caption)}</caption>',
    )
    # A two-column table of facts has no column headings, only row ones, and
    # markdown has no way to express that. Authors write an empty header row to
    # get the table at all. Leaving it produces empty <th> cells, which every
    # accessibility checker flags and which a screen reader announces as
    # nothing. So an all-empty header row is dropped, and the row headers below
    # carry the meaning on their own.
    empty_head = re.search(r"<thead>\s*<tr>(?:\s*<th[^>]*>\s*</th>)+\s*</tr>\s*</thead>",
                           body)
    if empty_head:
        body = body.replace(empty_head.group(0), "")

    # Header cells announce their column. Matching `<th` rather than `<th>`
    # because a markdown table with alignment colons emits
    # `<th style="text-align: right;">`, and a plain `<th>` pattern would skip
    # it and silently drop the scope.
    body = re.sub(r"<th(\s|>)", r'<th scope="col"\1', body)

    # The first cell of each body row announces the row.
    def row_header(match: re.Match) -> str:
        # Not anchored with ^. Markdown puts a newline after <tr>, so an
        # anchored pattern silently matches nothing and every row quietly
        # loses its header. Caught by counting the scope attributes in the
        # output rather than by reading the code.
        inner = match.group(1)
        return re.sub(r"<td(\s[^>]*)?>(.*?)</td>",
                      lambda m: f'<th scope="row"{m.group(1) or ""}>{m.group(2)}</th>',
                      inner, count=1, flags=re.DOTALL)

    head, sep, rest = body.partition("<tbody>")
    if sep:
        rest = re.sub(r"<tr>(.*?)</tr>", lambda m: f"<tr>{row_header(m)}</tr>", rest,
                      flags=re.DOTALL)
        body = head + sep + rest
    return body


def render_page(text: str, page_title: str, source: str = "<page>") -> str:
    """Full page HTML, wrapped the way every template page is wrapped."""
    blocks = parse_blocks(text, source)
    inner = "\n".join(render_block(block, source) for block in blocks)
    escaped = html.escape(page_title)
    return (
        f'<div id="dp-wrapper" class="dp-wrapper dp-basic-bar">'
        f'<header class="dp-header dp-basic-bar ">\n'
        f'<h2 class="dp-heading"><span class="dp-header-title">{escaped}</span></h2>\n'
        f'</header>\n'
        f'{inner}\n'
        f'</div>'
    )


def render_document(text: str, page_title: str, source: str = "<page>") -> str:
    """A complete standalone HTML file, as a Common Cartridge carries it."""
    body = render_page(text, page_title, source)
    return (
        '<html lang="en">\n<head>\n'
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>\n'
        f'<title>{html.escape(page_title)}</title>\n'
        '<meta name="editing_roles" content="teachers"/>\n'
        '<meta name="workflow_state" content="active"/>\n'
        '</head>\n<body>\n'
        f'{body}\n'
        '</body>\n</html>'
    )
