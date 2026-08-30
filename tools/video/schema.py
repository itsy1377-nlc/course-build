"""The scene list: one YAML file per video, and the only thing authored by hand.

A video is an ordered list of scenes. Each scene is either a slide or a
terminal recording, and each carries its own narration. That single structure
drives four outputs that would otherwise drift apart:

    the visuals      how long each slide holds, and when a bullet appears
    the audio        what is said, in order
    the captions     cue text and cue timing
    the transcript   the text alternative a student reads instead of watching

They cannot disagree, because all four are read off the same list and the same
measured audio durations. Nothing here is written twice.

Why narration is a list of cues rather than a paragraph: a cue is the unit of
synthesis, the unit of caption timing, and the unit of slide reveal. Splitting
prose into cues after the fact means guessing where the model will breathe.
Authoring cues means the timing is exact.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import config as _config

ROOT = _config.find_root()
VIDEO_DIR = ROOT / "content" / "video"

LAYOUTS = {"title", "statement", "numbered", "compare", "code", "closing", "diagram"}
DIAGRAM_KINDS = {"flow", "split", "stack", "svg"}
KINDS = {"concept", "walkthrough"}

# Kokoro's American English voices that were auditioned for this course. Held
# as a set so a typo in a scene list fails at load rather than producing a
# video in a voice nobody chose.
VOICES = {"af_heart", "af_bella", "af_nicole", "af_sarah",
          "am_michael", "am_puck", "am_adam", "am_onyx",
          "bf_emma", "bm_george"}


class SceneError(Exception):
    """A scene list is malformed. The message says which file and what to fix."""


@dataclass
class Cue:
    """One spoken line. The unit of synthesis, captioning, and slide reveal."""
    text: str
    reveal: int | None = None      # slide scenes: how many items are lit
    hold: float = 0.35             # seconds of silence after, so lines do not run together


@dataclass
class Node:
    """One box in a diagram."""
    label: str
    sub: str = ""
    mark: bool = False       # the one thing that matters, drawn in the accent
    code: bool = False       # render the label monospaced


@dataclass
class Diagram:
    """A picture, described rather than drawn.

    Authors give structure, never geometry or colour, for the same reason they
    pick a slide layout instead of writing CSS: seventeen diagrams drawn by hand
    look like seventeen diagrams, and a picture that quietly uses a different
    grey is the kind of thing nobody reports and everybody notices.

    `alt` is required and the build fails without it. A diagram is the one slide
    element that carries meaning a listener cannot get from the narration by
    accident, so the text alternative is not a nicety here, it is the content.
    """
    kind: str
    alt: str
    direction: str = "right"                      # flow: right | down
    nodes: list[Node] = field(default_factory=list)
    loop: str = ""                                # flow: the return path label
    source: Node | None = None                    # split: what branches
    tracks: list[Node] = field(default_factory=list)
    layers: list[Node] = field(default_factory=list)
    svg: str = ""                                 # kind: svg, themed by CSS vars

    @property
    def parts(self) -> list[Node]:
        """Everything a reveal can light, in order."""
        return self.nodes or self.tracks or self.layers

    @property
    def steps(self) -> int:
        return len(self.parts) + (1 if self.loop else 0)


@dataclass
class Scene:
    type: str                      # "slide" or "terminal"
    cues: list[Cue] = field(default_factory=list)
    # slide scenes
    layout: str = "statement"
    eyebrow: str = ""
    heading: str = ""
    body: str = ""
    items: list[str] = field(default_factory=list)
    diagram: Diagram | None = None
    # terminal scenes
    setup: list[str] = field(default_factory=list)   # run hidden, never on camera
    steps: list[dict] = field(default_factory=list)  # {run, wait, settle, typing}
    cwd: str = "/work"

    @property
    def revealable(self) -> int:
        """How many things on this slide a reveal can light."""
        return self.diagram.steps if self.diagram else len(self.items)

    @property
    def reveal_states(self) -> list[int]:
        return sorted({c.reveal for c in self.cues if c.reveal is not None}) or [self.revealable]


@dataclass
class Video:
    id: str
    title: str
    kind: str
    module: str
    embed_on: str                  # the page carrying the ::: video block
    blurb: str                     # the one line inside that block
    scenes: list[Scene]
    voice: str = "af_heart"
    explains: list[str] = field(default_factory=list)   # pages this must stay true to
    source: Path | None = None

    @property
    def cues(self) -> list[Cue]:
        return [c for s in self.scenes for c in s.cues]

    @property
    def words(self) -> int:
        return sum(len(c.text.split()) for c in self.cues)

    @property
    def commands(self) -> list[str]:
        """Every command that appears on camera. What verify_content checks."""
        return [step["run"] for s in self.scenes for step in s.steps]

    @property
    def hidden_commands(self) -> list[str]:
        return [c for s in self.scenes for c in s.setup]


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise SceneError(message)


def _cue(raw, where: str) -> Cue:
    if isinstance(raw, str):
        return Cue(text=raw.strip())
    _require(isinstance(raw, dict), f"{where}: a cue is a string or a mapping, got {type(raw).__name__}")
    _require("text" in raw, f"{where}: a cue mapping needs a 'text' key")
    return Cue(text=str(raw["text"]).strip(),
               reveal=raw.get("reveal"),
               hold=float(raw.get("hold", 0.35)))


NODE_KEYS = {"label", "sub", "mark", "code"}


def _node(raw, where: str) -> Node:
    if isinstance(raw, str):
        return Node(label=raw.strip())
    _require(isinstance(raw, dict), f"{where}: a diagram node is a string or a mapping")
    _require("label" in raw, f"{where}: a diagram node needs a 'label'")
    unknown = sorted(set(raw) - NODE_KEYS)
    if unknown:
        # Almost always the YAML flow mapping comma trap. Written inline as
        # {label: A, sub: words, and more words}, YAML splits on the comma and
        # "and more words" becomes a key with no value. The text silently
        # disappears from the slide and nothing else notices.
        _require(False,
                 f"{where}: unexpected key(s) in a diagram node: {', '.join(repr(k) for k in unknown)}\n"
                 f"  If the text contains a comma, an inline mapping breaks on it. Write\n"
                 f"    - label: The system prompt\n"
                 f"      sub: words, and words only ask\n"
                 f"  rather than putting it all inside braces on one line.")
    return Node(label=str(raw["label"]).strip(), sub=str(raw.get("sub", "")).strip(),
                mark=bool(raw.get("mark", False)), code=bool(raw.get("code", False)))


def _diagram(raw: dict, where: str) -> Diagram:
    _require(isinstance(raw, dict), f"{where}: 'diagram' is a mapping")
    kind = raw.get("kind")
    _require(kind in DIAGRAM_KINDS,
             f"{where}: '{kind}' is not a diagram kind.\n  Available: {', '.join(sorted(DIAGRAM_KINDS))}")
    alt = str(raw.get("alt", "")).strip()
    _require(bool(alt),
             f"{where}: this diagram has no 'alt'.\n"
             f"  A diagram carries meaning that a listener cannot recover from the "
             f"narration, so the text alternative is required. Describe what the "
             f"picture shows, not that a picture exists.")
    diagram = Diagram(kind=kind, alt=alt)

    if kind == "flow":
        diagram.direction = raw.get("direction", "right")
        _require(diagram.direction in ("right", "down"),
                 f"{where}: flow direction is 'right' or 'down'")
        diagram.nodes = [_node(n, where) for n in raw.get("nodes", [])]
        _require(len(diagram.nodes) >= 2, f"{where}: a flow needs at least two nodes")
        _require(len(diagram.nodes) <= 5,
                 f"{where}: {len(diagram.nodes)} nodes is too many to read at a glance. "
                 f"Five is the practical limit; split the idea across two slides.")
        diagram.loop = str(raw.get("loop", "")).strip()
    elif kind == "split":
        _require("from" in raw and "tracks" in raw,
                 f"{where}: a split needs 'from' and 'tracks'")
        diagram.source = _node(raw["from"], where)
        diagram.tracks = [_node(n, where) for n in raw["tracks"]]
        _require(2 <= len(diagram.tracks) <= 3,
                 f"{where}: a split shows two or three tracks")
    elif kind == "stack":
        diagram.layers = [_node(n, where) for n in raw.get("layers", [])]
        _require(2 <= len(diagram.layers) <= 5,
                 f"{where}: a stack shows two to five layers")
    else:
        diagram.svg = str(raw.get("svg", "")).strip()
        _require(bool(diagram.svg), f"{where}: kind 'svg' needs an 'svg' body")
        _require("<script" not in diagram.svg.lower(),
                 f"{where}: inline SVG may not contain a script element")
    return diagram


def _scene(raw: dict, index: int, source: str) -> Scene:
    where = f"{source}: scene {index + 1}"
    _require(isinstance(raw, dict), f"{where}: a scene is a mapping")
    kind = raw.get("type")
    _require(kind in ("slide", "terminal"), f"{where}: type must be 'slide' or 'terminal', got {kind!r}")

    cues = [_cue(c, where) for c in raw.get("narration", [])]
    _require(bool(cues), f"{where}: every scene needs narration. A silent scene has no duration and no caption.")

    scene = Scene(type=kind, cues=cues)

    if kind == "slide":
        scene.layout = raw.get("layout", "statement")
        _require(scene.layout in LAYOUTS,
                 f"{where}: '{scene.layout}' is not a layout.\n  Available: {', '.join(sorted(LAYOUTS))}")
        scene.eyebrow = raw.get("eyebrow", "")
        scene.heading = str(raw.get("heading", "")).strip()
        scene.body = str(raw.get("body", "")).strip()
        scene.items = [str(i) for i in raw.get("items", [])]
        if "diagram" in raw:
            scene.diagram = _diagram(raw["diagram"], where)
            _require(scene.layout == "diagram",
                     f"{where}: a scene with a diagram uses layout: diagram")
        _require(scene.layout != "diagram" or scene.diagram is not None,
                 f"{where}: layout 'diagram' needs a 'diagram' block")
        _require(bool(scene.heading or scene.body or scene.items or scene.diagram),
                 f"{where}: a slide needs a heading, body, items, or a diagram")
        for c in scene.cues:
            if c.reveal is not None:
                _require(0 <= c.reveal <= scene.revealable,
                         f"{where}: reveal {c.reveal} but this slide has "
                         f"{scene.revealable} thing(s) to reveal")
    else:
        scene.cwd = raw.get("cwd", "/work")
        scene.setup = [str(c) for c in raw.get("setup", [])]
        steps = raw.get("steps", [])
        _require(bool(steps), f"{where}: a terminal scene needs at least one step")
        for j, st in enumerate(steps):
            _require(isinstance(st, dict) and "run" in st,
                     f"{where}: step {j + 1} needs a 'run' key")
            scene.steps.append({
                "run": str(st["run"]).strip(),
                "wait": st.get("wait"),
                "settle": float(st.get("settle", 1.2)),
                "typing": st.get("typing", "55ms"),
            })
    return scene


def load(path: Path) -> Video:
    """Read one scene list, or raise SceneError saying exactly what is wrong."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        # A raw scanner traceback tells an author nothing useful. The mark
        # carries the line and column, so say those and stop.
        mark = getattr(error, "problem_mark", None)
        where = f" at line {mark.line + 1}, column {mark.column + 1}" if mark else ""
        problem = getattr(error, "problem", str(error))
        raise SceneError(f"{path.name}: not valid YAML{where}.\n  {problem}") from None
    source = path.name
    _require(isinstance(raw, dict), f"{source}: the file must be a mapping")

    for key in ("id", "title", "kind", "module", "embed_on", "blurb", "scenes"):
        _require(key in raw, f"{source}: missing required key '{key}'")

    _require(raw["id"] == path.stem,
             f"{source}: id is {raw['id']!r} but the filename says {path.stem!r}. "
             f"They have to match, because the ::: video block names the id.")
    _require(raw["kind"] in KINDS, f"{source}: kind must be one of {sorted(KINDS)}")
    voice = raw.get("voice") or _config.load().voice.partition(":")[2] or "af_heart"
    _require(voice in VOICES, f"{source}: {voice!r} is not an audited voice.\n  Available: {', '.join(sorted(VOICES))}")

    embed = ROOT / raw["embed_on"]
    _require(embed.exists(), f"{source}: embed_on points at {raw['embed_on']}, which does not exist")
    for page in raw.get("explains", []):
        _require((ROOT / page).exists(), f"{source}: explains lists {page}, which does not exist")

    blurb = str(raw["blurb"]).strip()
    _require("\n" not in blurb, f"{source}: blurb is one line. It sits in a word-budgeted block.")

    scenes = [_scene(s, i, source) for i, s in enumerate(raw["scenes"])]
    _require(bool(scenes), f"{source}: a video needs at least one scene")

    video = Video(
        id=raw["id"], title=str(raw["title"]).strip(), kind=raw["kind"],
        module=raw["module"], embed_on=raw["embed_on"], blurb=blurb,
        scenes=scenes, voice=voice,
        explains=[str(p) for p in raw.get("explains", [])],
        source=path,
    )

    # An em dash reaches a student two ways here, on screen and in the caption
    # file, and AUTHORING.md rules it out in both. Cheaper to catch at load.
    for c in video.cues:
        _require("—" not in c.text and "–" not in c.text,
                 f"{source}: narration uses a dash character. Use commas, colons, "
                 f"parentheses or semicolons.\n  {c.text[:70]}")
    return video


def load_all() -> list[Video]:
    """Every scene list in the project.

    config.yaml and anything starting with an underscore are not scene lists.
    Without this the pipeline tried to load the course's own configuration as a
    video and reported a missing 'id' key, which is a confusing way to say
    "that is not a video".
    """
    if not VIDEO_DIR.exists():
        return []
    return [load(p) for p in sorted(VIDEO_DIR.glob("*.yaml"))
            if p.name != _config.CONFIG_NAME and not p.name.startswith("_")]


VIDEO_BLOCK_RE = re.compile(r"^:::\s*video\s+([a-z0-9-]+)\s*(?:\|.*)?$", re.MULTILINE)


def embedded_ids(page_text: str) -> list[str]:
    """Every video id a page embeds. Used by the orphan and resolve gates."""
    return VIDEO_BLOCK_RE.findall(page_text)
