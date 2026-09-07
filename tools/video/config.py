"""Everything about a particular course, in one file the pipeline reads.

The rest of this package is course agnostic on purpose. Slide layouts, caption
timing, the drift reconciliation, the spoiler gate: none of that is specific to
one subject. What changes between courses is the name in the slide footer,
where the runnable code lives, and which files count as answers a student is
supposed to produce themselves.

Keeping that in one YAML file rather than scattered through the modules is what
lets this pipeline move to another course without a fork. It also means the
values are visible and reviewable rather than buried in a constant somewhere.

Defaults are chosen so a course with no config file still builds: slides render
with no footer text, terminal scenes are disabled rather than silently
recording the wrong thing, and the spoiler gate says so instead of passing
vacuously. A gate that cannot see anything must not report success.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import os

import yaml

CONFIG_NAME = "config.yaml"

def _content_rel() -> str:
    """The course tree this build is for, relative to the project root.

    Two courses live side by side in this project, so the video directory is
    per course rather than a single content/video/. Defaults to the historical
    single-course layout.
    """
    return os.environ.get("ITSY_CONTENT", "content")


def _variant_suffix() -> str:
    """The per-course suffix on build/video and build/video-cache.

    This has to agree with tools/cartridge.py, which reads the same variable
    and takes the last path segment before comparing it. Comparing the whole
    relative path instead sent a course tree at builder/content to
    build/video-content while the cartridge builder looked in build/video, so
    a page carrying a video block failed with "has not been built" even after
    the video rendered. Both now compare the last segment.
    """
    variant = _content_rel().rsplit("/", 1)[-1]
    return "" if variant == "content" else "-" + variant


def _video_rel() -> Path:
    return Path(_content_rel()) / "video"




def find_root(start: Path | None = None) -> Path:
    """The project root, meaning the directory that holds content/video/.

    Walked upward rather than assumed from __file__, because this package is
    installed into a host project rather than living at a fixed depth.
    """
    here = (start or Path(__file__)).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / _video_rel()).is_dir():
            return candidate
    # Fall back to the historical layout, tools/video/ inside the project.
    return Path(__file__).resolve().parents[2]


@dataclass
class Config:
    root: Path
    course_code: str = ""
    course_name: str = ""
    voice: str = "kokoro:af_heart"
    # Where runnable code lives, for terminal scenes and command checking.
    code_dir: Path | None = None
    # Files whose contents must never appear on camera.
    answer_globs: list[str] = field(default_factory=list)
    # Whether answer_globs was written down at all. An absent key is an
    # oversight and the no-spoiler gate has to fail on it. An explicitly empty
    # list is a decision, and config.yaml.example tells authors to make that
    # decision when a course genuinely has no student-produced answer files.
    # Held separately because [] and "never mentioned" are otherwise the same
    # value, which left the documented "set it to [] on purpose" impossible.
    answer_globs_declared: bool = False
    # Cases or exercises a walkthrough must not demonstrate, keyed by the page
    # that assigns them. Left empty, the gate falls back to scanning the page.
    recorder_image: str = "coursevideo/recorder:latest"
    recorder_base: str = "mcr.microsoft.com/devcontainers/python:3.12-bookworm"
    library_budget_mb: int = 400

    @property
    def video_dir(self) -> Path:
        return self.root / _video_rel()

    @property
    def build_dir(self) -> Path:
        # Per course tree, because two courses in one project use the same
        # video ids and would otherwise overwrite each other's renders.
        return self.root / "build" / f"video{_variant_suffix()}"

    @property
    def cache_dir(self) -> Path:
        return self.root / "build" / f"video-cache{_variant_suffix()}"

    @property
    def records_terminal(self) -> bool:
        """Terminal scenes need somewhere real to run."""
        return self.code_dir is not None and self.code_dir.is_dir()

    def answer_files(self) -> list[Path]:
        """Resolve answer_globs, preferring code_dir over the project root.

        config.yaml.example pairs `code_dir: labs` with
        `answer_globs: solution/**/*.py`, which reads as code_dir relative and
        is how anyone filling in that file will write it. This resolved from
        the project root only, so those patterns matched nothing and the gate
        failed with "those patterns match no files" while the files sat one
        directory down. Both bases are searched now, code_dir first, so a
        config written either way finds its files.
        """
        bases = [b for b in (self.code_dir, self.root) if b]
        found: list[Path] = []
        for pattern in self.answer_globs:
            for base in bases:
                hits = sorted(base.glob(pattern))
                if hits:
                    found.extend(hits)
                    break
        seen, unique = set(), []
        for p in found:
            if p.is_file() and p.resolve() not in seen:
                seen.add(p.resolve())
                unique.append(p)
        return unique

    def unmatched_answer_globs(self) -> list[str]:
        """Answer patterns that found nothing under any base.

        answer_files() drops a pattern that matches nothing and says so to
        nobody. That is silence in the one place it cannot be afforded: this
        list is what the no-spoiler gate compares the captured screen against,
        so a pattern pointing at the wrong folder means the gate runs, passes,
        and has checked nothing. It happened. ITSY 1377 pointed
        `solutions/**/*.ipynb` at a folder one level outside both bases, a
        third pattern matched, and the gate reported clean while every solution
        notebook was invisible to it.

        The gate now fails on anything this returns.
        """
        bases = [b for b in (self.code_dir, self.root) if b]
        missing = []
        for pattern in self.answer_globs:
            if not any(any(base.glob(pattern)) for base in bases):
                missing.append(pattern)
        return missing


@lru_cache(maxsize=1)
def load(root: Path | None = None) -> Config:
    root = root or find_root()
    path = root / _video_rel() / CONFIG_NAME
    raw = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    code_dir = raw.get("code_dir")
    return Config(
        root=root,
        course_code=str(raw.get("course_code", "")),
        course_name=str(raw.get("course_name", "")),
        voice=str(raw.get("voice", "kokoro:af_heart")),
        code_dir=(root / code_dir) if code_dir else None,
        answer_globs=[str(g) for g in raw.get("answer_globs") or []],
        answer_globs_declared="answer_globs" in raw,
        recorder_image=str(raw.get("recorder_image", "coursevideo/recorder:latest")),
        recorder_base=str(raw.get("recorder_base",
                                 "mcr.microsoft.com/devcontainers/python:3.12-bookworm")),
        library_budget_mb=int(raw.get("library_budget_mb", 400)),
    )
