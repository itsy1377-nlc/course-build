"""Contractions in narration, and nowhere else in a scene list.

A scene list is mostly not narration. It carries headings, body lines that are
rendered onto a slide, diagram labels, terminal commands and alt text. Only the
spoken lines should contract: a slide heading is a label, and "Don't" on a
slide reads as shouting where it reads as speech.

Narration appears two ways, and both are handled:

    narration:
      - a bare string
      - text: a string with a reveal
        reveal: 2
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from warm_pass import warm_line  # noqa: E402


def warm(text: str) -> tuple[str, int]:
    out, in_narration, changed = [], False, 0
    for line in text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        indent = len(stripped) - len(stripped.lstrip())

        if re.match(r"^\s*narration:\s*$", stripped):
            in_narration = True
            narration_indent = indent
            out.append(line)
            continue

        if in_narration:
            # A key at or left of narration's own indent ends the block.
            if stripped.strip() and indent <= narration_indent and not stripped.lstrip().startswith("-"):
                in_narration = False
            elif re.match(r"^\s*(reveal|hold|pause):", stripped):
                out.append(line)
                continue

        if in_narration and stripped.strip():
            match = re.match(r"^(\s*-\s+text:\s+|\s*-\s+)(.*)$", stripped)
            if match:
                head, body = match.groups()
                new_body = warm_line(body)
                if new_body != body:
                    changed += 1
                out.append(head + new_body + "\n")
                continue
        out.append(line)
    return "".join(out), changed


def main(argv: list[str]) -> int:
    total = 0
    for name in argv:
        path = Path(name)
        new, changed = warm(path.read_text(encoding="utf-8"))
        if changed:
            path.write_text(new, encoding="utf-8")
        total += changed
        print(f"  {path.name:<26}{changed} cue(s) contracted")
    print(f"  {total} cue(s) in total")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
