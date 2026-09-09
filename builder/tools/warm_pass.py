"""Apply contractions to course prose, and to nothing else.

The course reads flat because it never contracts. Contractions also lower the
reading grade, so this is one of the few edits that makes a page both warmer
and easier. What it must not do is reach into anything that is not prose:

  - fenced code blocks, and inline `code`
  - tables, which are terse by design and scanned rather than read
  - link text and URLs
  - ::: sources blocks, which carry citations word for word
  - headings and block directives

Connective tissue is not this tool's job. Joining two flat sentences with a
"so" or a "because" is a judgement about the argument, and it gets made by
hand, page by page.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Order matters. "is not" has to lose to "It is not" -> "It isn't" rather than
# winning first and leaving "It's not", which reads weaker in a definition.
PAIRS = [
    (r"\bIt is not\b", "It isn't"), (r"\bit is not\b", "it isn't"),
    (r"\bThat is not\b", "That isn't"), (r"\bthat is not\b", "that isn't"),
    (r"\bThere is not\b", "There isn't"), (r"\bthere is not\b", "there isn't"),
    (r"\bdoes not\b", "doesn't"), (r"\bDoes not\b", "Doesn't"),
    (r"\bdo not\b", "don't"), (r"\bDo not\b", "Don't"),
    (r"\bdid not\b", "didn't"), (r"\bDid not\b", "Didn't"),
    (r"\bis not\b", "isn't"), (r"\bIs not\b", "Isn't"),
    (r"\bare not\b", "aren't"), (r"\bAre not\b", "Aren't"),
    (r"\bwas not\b", "wasn't"), (r"\bWas not\b", "Wasn't"),
    (r"\bwere not\b", "weren't"), (r"\bWere not\b", "Weren't"),
    (r"\bhas not\b", "hasn't"), (r"\bhave not\b", "haven't"),
    (r"\bcannot\b", "can't"), (r"\bCannot\b", "Can't"),
    (r"\bwill not\b", "won't"), (r"\bWill not\b", "Won't"),
    (r"\bwould not\b", "wouldn't"), (r"\bcould not\b", "couldn't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bYou are\b", "You're"), (r"\byou are\b", "you're"),
    (r"\bYou will\b", "You'll"), (r"\byou will\b", "you'll"),
    (r"\bYou have\b", "You've"), (r"\byou have\b", "you've"),
    (r"\bThat is\b", "That's"), (r"\bthat is\b", "that's"),
    (r"\bThere is\b", "There's"), (r"\bthere is\b", "there's"),
    (r"\bHere is\b", "Here's"), (r"\bhere is\b", "here's"),
    (r"\bWhat is\b", "What's"), (r"\bIt is\b", "It's"), (r"\bit is\b", "it's"),
    (r"\bThey are\b", "They're"), (r"\bthey are\b", "they're"),
    (r"\bWe are\b", "We're"), (r"\bwe are\b", "we're"),
]

INLINE_CODE = re.compile(r"`[^`]*`")


# A contraction of "is" is only legal when the word it attaches to is the
# subject of its clause. This tool matches on the word alone and cannot see
# that, and it shipped eight broken sentences before anyone noticed:
#
#     Handling it is the work            -> Handling it's the work
#     What to take from it is the shape  -> ... from it's the shape
#     Nothing here is graded             -> Nothing here's graded
#     no numbers in it is a weak post    -> ... in it's a weak post
#
# Each one reads as garbage to a screen reader. The rule that catches them:
# when a preposition, a gerund or a quantifier sits in front, the pronoun is
# part of a longer phrase rather than the subject, so leave it alone.
#
# tools/readability.py enforces the same rule on the output, so a regression
# here fails the gate rather than reaching a student.
NEVER_BEFORE = re.compile(
    r"\b(?:from|of|with|about|for|in|on|at|to|into|than|"
    r"[Nn]othing|[Ee]verything|[Ss]omething|[Aa]nything|"
    r"\w+ing)\s+$")

SUBJECT_PRONOUNS = ("it", "here", "there", "that", "It", "Here", "There", "That")


def _guarded(pattern: str, replacement: str, line: str) -> str:
    """Apply one contraction, skipping any match that is not a subject."""
    def decide(match: re.Match) -> str:
        head = match.group(0).split()[0]
        if head in SUBJECT_PRONOUNS and NEVER_BEFORE.search(line[:match.start()]):
            return match.group(0)
        return replacement
    return re.sub(pattern, decide, line)


def warm_line(line: str) -> str:
    """Contract one line of prose, leaving inline code untouched."""
    held: list[str] = []

    def stash(match: re.Match) -> str:
        held.append(match.group(0))
        return f"\x00{len(held) - 1}\x00"

    line = INLINE_CODE.sub(stash, line)
    for pattern, replacement in PAIRS:
        line = _guarded(pattern, replacement, line)
    for index, original in enumerate(held):
        line = line.replace(f"\x00{index}\x00", original)
    return line


def warm(text: str) -> tuple[str, int]:
    out, in_code, in_sources, changed = [], False, False, 0
    for line in text.splitlines(keepends=True):
        bare = line.strip()
        if bare.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if bare.startswith("::: sources"):
            in_sources = True
        elif in_sources and bare == ":::":
            in_sources = False
        skip = (in_code or in_sources
                or bare.startswith("|")        # a table row
                or bare.startswith("#")        # a heading
                or bare.startswith(":::")      # a block directive
                or bare.startswith("[")        # a bare link line
                or bare.startswith("    "))    # an indented code block
        if skip:
            out.append(line)
            continue
        new = warm_line(line)
        if new != line:
            changed += 1
        out.append(new)
    return "".join(out), changed


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    total = 0
    for name in argv:
        path = Path(name)
        text = path.read_text(encoding="utf-8")
        new, changed = warm(text)
        if changed:
            path.write_text(new, encoding="utf-8")
        total += changed
        print(f"  {path.name:<26}{changed} line(s) contracted")
    print(f"  {total} line(s) in total")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
