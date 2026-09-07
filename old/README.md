# Retired course versions

Nothing in here is built, deployed or checked any more. The live course is
`builder/`, which ships to Canvas as **ITSY-1377-000** (course id 6) and to
notebook.bashtion.dev.

| Folder | What it was |
|---|---|
| `content/` | The funded and constrained variants. Canvas courses 3 and 4, both deleted. |
| `labs/` | The first version of the course, kept while the rebuild referred to it. |
| `archive/` | v1 course content, including the pages the rebuild was measured against. |
| `build/` | Cartridges, video caches and review artifacts for the two retired variants. |

Two of these are still worth reading rather than deleting. `archive/` holds the
v1 glossary and rubrics, and the rebuild has already borrowed from them once:
v1 defined "rate limit" and autograded a retry, and the rebuild dropped both.
`labs/` holds the original notebooks.

**The shared `tools/` directory did not move.** `builder/` calls it, and so did
these. `tools/readability.py` now works out which course it is measuring from
the directory it is run in, and prints it.
