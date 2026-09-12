"""Build the course in Canvas from builder/content/course.yaml.

    python3 builder/canvas/build_course.py --check     # say what would change
    python3 builder/canvas/build_course.py             # create or update
    python3 builder/canvas/build_course.py --verify    # read Canvas back and compare

Idempotent by design. Every object is found by its title or its page url and
updated in place, so running this again changes the course rather than
duplicating it.

It refuses to guess. If a source file for an item does not exist, the item is
skipped and named in the report rather than created empty. If Canvas rejects a
call, the error body is printed and the run stops, because a build that
half-succeeded and said nothing is the failure this project keeps hitting.

The credentials come from the environment, never from this repository:

    export CANVAS_BASE=https://your.canvas.host
    export CANVAS_TOKEN=...
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import markdown
import requests
import yaml

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "builder"
CONTENT = BUILDER / "content"
NOTEBOOKS = BUILDER / "lab" / "notebooks"
sys.path.insert(0, str(REPO))
from tools.blocks import render_page  # noqa: E402

NOTEBOOK_FOLDER = "notebooks"


class CanvasError(RuntimeError):
    pass


class Canvas:
    """A small client that follows pagination and never swallows an error."""

    def __init__(self, url: str, token: str):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers["Authorization"] = f"Bearer {token}"
        # Cloudflare Access sits in front of the host. A browser authenticates by logging
        # in; a script cannot, so it presents a service token instead and Access exchanges
        # it for the same JWT at the edge. Without these headers every request gets a 302
        # to the login page, and Canvas's own Bearer token never reaches the origin --
        # which looks like an auth failure against Canvas rather than a gate in front of it.
        #
        # Optional on purpose: absent the vars this behaves exactly as before, so the
        # script still works against an ungated instance. Set them for a gated one:
        #   export CF_ACCESS_CLIENT_ID=...    (the non-secret half)
        #   export CF_ACCESS_CLIENT_SECRET=...
        cf_id = os.environ.get("CF_ACCESS_CLIENT_ID")
        cf_secret = os.environ.get("CF_ACCESS_CLIENT_SECRET")
        if cf_id and cf_secret:
            self.session.headers["CF-Access-Client-Id"] = cf_id
            self.session.headers["CF-Access-Client-Secret"] = cf_secret
        elif cf_id or cf_secret:
            sys.exit("Set BOTH CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET, or neither. "
                     "One alone is not a usable credential and fails as a login redirect.")

    def _call(self, method: str, path: str, **kwargs) -> Any:
        response = self.session.request(method, f"{self.url}/api/v1{path}", timeout=90, **kwargs)
        if not response.ok:
            raise CanvasError(f"{method} {path} -> HTTP {response.status_code}: {response.text[:600]}")
        if not response.content:
            return None
        return response.json()

    def get(self, path: str, **params) -> Any:
        response = self.session.get(f"{self.url}/api/v1{path}",
                                    params={"per_page": 100, **params}, timeout=90)
        if not response.ok:
            raise CanvasError(f"GET {path} -> HTTP {response.status_code}: {response.text[:600]}")
        payload = response.json()
        if not isinstance(payload, list):
            return payload
        while True:
            match = re.search(r'<([^>]+)>;\s*rel="next"', response.headers.get("Link", ""))
            if not match:
                return payload
            response = self.session.get(match.group(1), timeout=90)
            if not response.ok:
                raise CanvasError(f"GET next page -> HTTP {response.status_code}")
            payload.extend(response.json())

    def post(self, path: str, data=None, json_body=None) -> Any:
        if json_body is not None:
            return self._call("POST", path, json=json_body)
        return self._call("POST", path, data=data)

    def put(self, path: str, data=None, json_body=None) -> Any:
        if json_body is not None:
            return self._call("PUT", path, json=json_body)
        return self._call("PUT", path, data=data)

    def delete(self, path: str) -> Any:
        return self._call("DELETE", path)


def slug(ref: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")


MODULE_WEEK_RE = re.compile(r"^Module (\d+):")


def module_week(name: str) -> str | None:
    """Which week a module belongs to, as a string.

    "Module 2: Structured Output" -> "2". Everything with no number is
    orientation, and it answers to the name "start" so a scoped run can still
    reach it.
    """
    m = MODULE_WEEK_RE.match(name)
    return m.group(1) if m else "start"


def page_source(ref: str) -> Path | None:
    p = CONTENT / "pages" / f"{ref}.md"
    return p if p.exists() else None


def notebook_source(ref: str) -> Path | None:
    p = NOTEBOOKS / f"{ref}.ipynb"
    return p if p.exists() else None


def yaml_source(kind: str, ref: str) -> Path | None:
    p = CONTENT / kind / f"{ref}.yaml"
    return p if p.exists() else None


def md_source(kind: str, ref: str) -> Path | None:
    p = CONTENT / kind / f"{ref}.md"
    return p if p.exists() else None


class Builder:
    def __init__(self, canvas: Canvas, spec: dict, dry: bool):
        self.canvas = canvas
        self.spec = spec
        self.dry = dry
        self.course_id = spec["course"]["canvas_id"]
        self.report: list[str] = []
        self.skipped: list[str] = []
        self.groups: dict[str, int] = {}
        self.outcomes: dict[str, int] = {}
        self.files: dict[str, int] = {}
        self._page_urls: dict[str, str] | None = None
        self._video_links: dict[str, str] | None = None
        # None means "every asset"; a set means a scoped build.
        self._wanted_video_ids: set[str] | None = None
        # None means the whole course; a set of module names means a scoped run.
        self.only_modules: set[str] | None = None
        self.scoped_files = False

    def scope_to(self, weeks: set[str]) -> None:
        """Limit this build to the modules for the named weeks.

        A one-week change used to cost a full-course push: 154 objects and
        86 MB of video, several minutes, every time a sentence moved. Nothing
        about that was safe either, because the blast radius of a typo was the
        whole course.

        Scoping narrows three things together, and they have to move together
        or the run is a lie: the modules written, the video assets uploaded,
        and the student lab files. Course settings, assignment groups and
        outcomes are cheap, idempotent and shared, so they still run.
        """
        names, wanted_ids = set(), set()
        for mod in self.spec["modules"]:
            if module_week(mod["name"]) in weeks:
                names.add(mod["name"])
                for item in mod["items"]:
                    if item["type"] in ("page", "assignment"):
                        src = (page_source(item["ref"]) if item["type"] == "page"
                               else md_source("assignments", item["ref"]))
                        if src and src.exists():
                            wanted_ids |= set(re.findall(r"^::: video (\S+)",
                                                         src.read_text(encoding="utf-8"),
                                                         re.MULTILINE))
        if not names:
            raise CanvasError(f"no module matches week(s) {sorted(weeks)}. "
                              f"Use --list-weeks to see the names.")
        self.only_modules = names
        self._wanted_video_ids = wanted_ids
        # A lab notebook belongs to a week, but student_files is one allowlist
        # for the whole course and the upload is cheap next to video. Send it
        # whenever a scoped run touches a week that has a lab.
        self.scoped_files = any(w.isdigit() for w in weeks)
        print(f"scope: {len(names)} module(s) -- " + ", ".join(sorted(names)))
        print(f"       {len(wanted_ids)} video(s) -- "
              + (", ".join(sorted(wanted_ids)) if wanted_ids else "none"))
        print(f"       student lab files: {'yes' if self.scoped_files else 'no'}\n")

    def say(self, line: str) -> None:
        self.report.append(line)
        print(line, flush=True)

    # ---------- course settings and groups ----------

    def item_title(self, ref: str) -> str | None:
        """What the spine calls this ref, so a rendered page keeps one title."""
        for mod in self.spec["modules"]:
            for item in mod["items"]:
                if item.get("ref") == ref:
                    return item.get("title")
        return None

    def grading_standard(self) -> int | None:
        """Create the letter scheme once and hand back its id.

        template-conflicts item 13: this course enables A/B/C/D/F at 90, 80,
        70, 60. Canvas has no update endpoint for a grading standard, so the
        existing one is found by title rather than replaced, which is what
        keeps a second run from stacking up copies.

        The entries go out as a list of pairs, not a dict. Canvas pairs each
        name with the value that follows it, so order matters and the repeated
        key has to survive to the wire.
        """
        spec = self.spec["course"].get("grading_standard")
        if not spec:
            return None
        if self.dry:
            self.say(f"[dry] grading standard {spec['title']}: "
                     f"{len(spec['scheme'])} entries")
            return None
        existing = self.canvas.get(f"/courses/{self.course_id}/grading_standards")
        found = next((g for g in existing if g["title"] == spec["title"]), None)
        if found:
            self.say(f"grading standard {spec['title']}: id {found['id']}, already present")
            return found["id"]
        payload: list[tuple[str, Any]] = [
            ("title", spec["title"]), ("points_based", "false"), ("scaling_factor", "1.0")]
        for entry in spec["scheme"]:
            payload.append(("grading_scheme_entry[][name]", entry["name"]))
            payload.append(("grading_scheme_entry[][value]", str(entry["value"])))
        obj = self.canvas.post(f"/courses/{self.course_id}/grading_standards", data=payload)
        self.say(f"grading standard {spec['title']}: id {obj['id']}, "
                 f"{len(spec['scheme'])} entries")
        return obj["id"]

    def settings(self, with_view: bool = True) -> None:
        """Every course-level setting the spine declares, applied.

        Four of these were declared in course.yaml and never sent, which is a
        setting that looks applied in the repository and is absent in Canvas.
        A key here that the builder does not read is a bug, so read them all.

        default_view is the exception and it is applied twice. Canvas refuses
        `default_view=wiki` with "A Front Page is required" until a page is
        actually flagged as the front page, so the first pass leaves it out and
        main() calls this again after the front page exists.
        """
        c = self.spec["course"]
        # Deliberately NOT sent: course[name] and course[course_code]. The course
        # in the spine is the master shell that every term section is copied from,
        # and the container's name is the only thing that tells the two apart in a
        # course list. Sending the spine's name renamed the shell to the section
        # name on every build -- including a scoped --week run -- and the shell's
        # own name is not recorded anywhere here, so nothing could put it back.
        # c["name"] stays in the spine because the front page and the syllabus
        # title fall back to it; it names the course in content, not the container.
        data: dict[str, Any] = {
            "course[apply_assignment_group_weights]": str(c.get("apply_group_weights", True)).lower(),
        }
        if c.get("default_view") and with_view:
            data["course[default_view]"] = c["default_view"]
        if c.get("description"):
            # The catalog description. The build prompt requires it to state
            # the enforced prerequisite, so course.yaml carries the sentence.
            data["course[public_description]"] = " ".join(c["description"].split())
        ref = c.get("description_page")
        if ref:
            src = page_source(ref)
            if not src:
                raise CanvasError(f"description_page {ref}: no source at "
                                  f"content/pages/{ref}.md")
            data["course[syllabus_body]"] = render_page(
                src.read_text(), self.item_title(ref) or c["name"], source=str(src))
        standard_id = self.grading_standard()
        if standard_id:
            data["course[grading_standard_id]"] = standard_id
        if self.dry:
            self.say(f"[dry] course {self.course_id}: " + ", ".join(
                sorted(k.replace("course[", "").rstrip("]") for k in data)))
            return
        self.canvas.put(f"/courses/{self.course_id}", data=data)
        self.say(f"course {self.course_id}: {len(data)} setting(s) applied")

    def front_page(self) -> None:
        """The course home page, which is a page and not a module item.

        conformance section 4.1: the template's home page is the front page,
        and course default_view is wiki. Without this the page exists nowhere
        and default_view points at nothing.
        """
        ref = self.spec["course"].get("front_page")
        if not ref:
            return
        self.make_page(ref, self.spec["course"]["name"], front=True)

    def assignment_groups(self) -> None:
        existing = {g["name"]: g for g in self.canvas.get(f"/courses/{self.course_id}/assignment_groups")}
        for g in self.spec["assignment_groups"]:
            found = existing.get(g["name"])
            data = {"name": g["name"], "group_weight": g["weight"]}
            if self.dry:
                self.say(f"[dry] group {g['name']} weight {g['weight']}")
                continue
            if found:
                obj = self.canvas.put(f"/courses/{self.course_id}/assignment_groups/{found['id']}", data=data)
            else:
                obj = self.canvas.post(f"/courses/{self.course_id}/assignment_groups", data=data)
            self.groups[g["key"]] = obj["id"]
            self.say(f"group {g['name']}: id {obj['id']}, weight {g['weight']}")

    # ---------- outcomes ----------

    def build_outcomes(self) -> None:
        spec = self.spec["outcomes"]
        scale = spec["scale"]
        root = self.canvas.get(f"/courses/{self.course_id}/root_outcome_group")
        links = self.canvas.get(f"/courses/{self.course_id}/outcome_group_links")
        by_title = {l["outcome"]["title"]: l["outcome"]["id"] for l in links}
        for item in spec["items"]:
            if self.dry:
                self.say(f"[dry] outcome {item['title']}")
                continue
            payload = {
                "title": item["title"],
                "display_name": item["title"],
                "description": item["description"],
                "calculation_method": scale["calculation_method"],
                "mastery_points": scale["mastery_points"],
                "ratings": scale["ratings"],
            }
            if item["title"] in by_title:
                oid = by_title[item["title"]]
                self.canvas.put(f"/outcomes/{oid}", json_body=payload)
            else:
                # The course-scoped path. The bare /outcome_groups/:id/outcomes route
                # is the account one and answers 404 for a course group.
                obj = self.canvas.post(
                    f"/courses/{self.course_id}/outcome_groups/{root['id']}/outcomes",
                    json_body=payload)
                oid = obj["outcome"]["id"] if "outcome" in obj else obj["id"]
            self.outcomes[item["key"]] = oid
            self.say(f"outcome {item['key']}: id {oid}")

    # ---------- files ----------

    def upload_file(self, path: Path, folder: str) -> int:
        init = self.canvas.post(f"/courses/{self.course_id}/files", data={
            "name": path.name, "size": path.stat().st_size,
            "content_type": "application/x-ipynb+json" if path.suffix == ".ipynb" else "application/octet-stream",
            "parent_folder_path": folder, "on_duplicate": "overwrite"})
        up = requests.post(init["upload_url"], data=init["upload_params"],
                           files={"file": (path.name, path.read_bytes())},
                           allow_redirects=False, timeout=180)
        if up.status_code in (301, 302, 303):
            done = self.canvas.session.get(up.headers["Location"], timeout=90).json()
        else:
            done = up.json()
        if "id" not in done:
            raise CanvasError(f"upload {path.name}: {str(done)[:300]}")
        return done["id"]

    def student_files(self) -> None:
        """Upload the corpus and the data files the labs read.

        The build brief requires the course to carry the synthetic email corpus
        and its supporting data files. `student_files` in the spine is the
        allowlist, and it is an allowlist rather than a folder walk on purpose:
        `corpus/spec/corpus-spec.json` holds the verdict, the category, the
        indicators, the tool returns and the expected loop for all 56 emails,
        and `corpus/ground_truth.json` holds the graded labels. Either one in
        the course files hands every student the answer key, and no test a
        student ever runs would notice.

        So nothing is uploaded that the spine does not name, and `never_ship`
        names the files whose presence is a build failure rather than a
        warning. Both lists are checked again by --verify against what Canvas
        actually holds.
        """
        if self.only_modules is not None and not self.scoped_files:
            print("student files: skipped, this run is scoped and no lab file changed")
            return
        entries = self.spec.get("student_files") or []
        banned = set(self.spec.get("never_ship") or [])
        planned: list[tuple[Path, str]] = []
        for entry in entries:
            folder = entry["folder"]
            if "glob" in entry:
                matches = sorted(BUILDER.glob(entry["glob"]))
                if not matches:
                    self.skipped.append(f"student file {entry['glob']}: nothing matches")
                planned.extend((p, folder) for p in matches)
            else:
                path = BUILDER / entry["path"]
                if not path.exists():
                    self.skipped.append(f"student file {entry['path']}: not on disk")
                    continue
                planned.append((path, folder))
        refused = [p.name for p, _ in planned if p.name in banned]
        if refused:
            raise CanvasError("the spine asks to upload files that must never reach a "
                              f"student: {sorted(set(refused))}. Fix student_files.")
        if self.dry:
            self.say(f"[dry] student files: {len(planned)} file(s) in "
                     f"{len({f for _, f in planned})} folder(s)")
            return
        by_folder: dict[str, int] = {}
        for path, folder in planned:
            self.upload_file(path, folder)
            by_folder[folder] = by_folder.get(folder, 0) + 1
        for folder in sorted(by_folder):
            self.say(f"files {folder}: {by_folder[folder]} uploaded")

    # ---------- item builders ----------

    VIDEO_BASE = "$IMS-CC-FILEBASE$/video"

    def video_links(self) -> dict[str, str]:
        """Upload every built video asset once and map its cartridge path.

        A page's video block renders the Common Cartridge placeholder
        $IMS-CC-FILEBASE$/video/<id>.mp4. A cartridge import resolves that; an
        API build has to, or the player points at a path that does not exist
        and the page shows a broken video with no error anywhere.
        """
        if self._video_links is not None:
            return self._video_links
        self._video_links = {}
        build_dir = REPO / "build" / "video"
        if not build_dir.is_dir():
            return self._video_links
        for asset in sorted(build_dir.iterdir()):
            if asset.suffix not in (".mp4", ".vtt", ".jpg"):
                continue
            if self._wanted_video_ids is not None:
                # A scoped build uploads only the assets its own pages cite.
                # Video is 86 MB across fourteen files and it dominates the
                # push, so a one-week run that re-sent all of them would be a
                # full build wearing a smaller name.
                if asset.name.split(".")[0] not in self._wanted_video_ids:
                    continue
            # A dry run uploaded every asset for real. --check is the command
            # you run to find out what a push would do, and it was quietly
            # sending 86 MB and creating Canvas files while reporting "[dry]"
            # for everything else. Map the placeholder to a name that cannot
            # be mistaken for a URL, and touch nothing.
            if self.dry:
                self._video_links[f"{self.VIDEO_BASE}/{asset.name}"] = (
                    f"[dry-run: {asset.name} would upload, "
                    f"{asset.stat().st_size // 1024} KB]")
                self.say(f"[dry] video asset {asset.name} "
                         f"({asset.stat().st_size // 1024} KB)")
                continue
            fid = self.upload_file(asset, "video")
            self._video_links[f"{self.VIDEO_BASE}/{asset.name}"] = (
                f"/courses/{self.course_id}/files/{fid}/download?download_frd=1")
            self.say(f"video asset {asset.name}: file id {fid}")
        # The transcript link the block writes is .transcript.html, and the
        # pipeline produces .transcript.md. Render each one and upload it, so a
        # student who cannot play video still reaches the words.
        for md in sorted(build_dir.glob("*.transcript.md")):
            if (self._wanted_video_ids is not None
                    and md.name.split(".")[0] not in self._wanted_video_ids):
                continue
            html_path = md.with_suffix(".html")
            if self.dry:
                self._video_links[f"{self.VIDEO_BASE}/{html_path.name}"] = (
                    f"[dry-run: {html_path.name} would upload]")
                continue
            # Two WCAG Level A failures lived in these four lines until
            # 2026-09-11. There was no lang attribute, so a screen reader
            # guessed the language (3.1.1), and the title was md.stem, which
            # renders as "w7-walkthrough.transcript" in the tab and in a
            # bookmark (2.4.2). tools/cartridge.py has always written both
            # correctly; only the Canvas path regressed. The video's own title
            # is the first heading of the transcript it is rendering.
            source = md.read_text()
            heading = next((line[2:].strip() for line in source.splitlines()
                            if line.startswith("# ")), md.stem)
            page_title = f"Transcript: {heading}"
            html_path.write_text(
                '<!doctype html>\n<html lang="en">\n<head>\n'
                '<meta charset="utf-8">\n'
                f"<title>{html.escape(page_title)}</title>\n</head>\n<body>\n"
                + markdown.markdown(source, extensions=["tables"])
                + "\n</body>\n</html>\n")
            fid = self.upload_file(html_path, "video")
            self._video_links[f"{self.VIDEO_BASE}/{html_path.name}"] = (
                f"/courses/{self.course_id}/files/{fid}/download?download_frd=1")
        return self._video_links

    def resolve_media(self, body: str, where: str) -> str:
        """Swap every cartridge placeholder for the real Canvas file URL.

        A real build stops on an unbuilt asset, because pushing the page would
        leave a player pointing at nothing and nothing would report it.

        A dry run does not stop. It is the thing you run to find out what is
        left to do, so raising on the first missing video answered one question
        and hid the other twenty. It records them and carries on instead.
        """
        if self.VIDEO_BASE not in body:
            return body
        links = self.video_links()
        for placeholder, url in links.items():
            body = body.replace(placeholder, url)
        left = sorted(set(re.findall(r"\$IMS-CC-FILEBASE\$/video/[\w.-]+", body)))
        if left:
            names = sorted({p.rsplit("/", 1)[-1].split(".")[0] for p in left})
            if self.dry:
                self.skipped.append(f"{where}: video not built yet: {', '.join(names)}")
                return body
            raise CanvasError(f"{where}: these video assets are referenced but not built: "
                              f"{left}. Build them before pushing the page, "
                              f"or the player points at nothing.")
        return body

    def make_page(self, ref: str, title: str, front: bool = False) -> dict | None:
        src = page_source(ref)
        if not src:
            self.skipped.append(f"page {ref}: no source at content/pages/{ref}.md")
            return None
        body = self.resolve_media(render_page(src.read_text(), title, source=str(src)),
                                  f"page {ref}")
        if self.dry:
            self.say(f"[dry] page {title} ({len(body)} bytes)"
                     + (", front page" if front else ""))
            return {"page_url": slug(ref)}
        data = {"wiki_page[title]": title, "wiki_page[body]": body,
                "wiki_page[published]": "true", "wiki_page[editing_roles]": "teachers"}
        if front:
            data["wiki_page[front_page]"] = "true"
        # Canvas derives a new page's url from its TITLE and ignores the url in
        # the path when it has to create the page. So a PUT to the ref slug
        # created the page at the title slug, and the next run's PUT to the ref
        # slug still found nothing and created a second copy with a "-2"
        # suffix. Look the page up by title and write to the url it actually
        # has; only fall back to the ref slug when the page is genuinely new.
        url = self.page_urls().get(title, slug(ref))
        obj = self.canvas.put(f"/courses/{self.course_id}/pages/{url}", data=data)
        self._page_urls[title] = obj["url"]
        self.say(f"page {title}: {obj['url']}" + (" (front page)" if front else ""))
        return obj

    def page_urls(self) -> dict[str, str]:
        """Every page in the course, by title. Fetched once."""
        if self._page_urls is None:
            self._page_urls = {p["title"]: p["url"]
                               for p in self.canvas.get(f"/courses/{self.course_id}/pages")}
        return self._page_urls

    def make_assignment(self, ref: str, title: str, group: str, points: int) -> dict | None:
        src = md_source("assignments", ref)
        if not src:
            self.skipped.append(f"assignment {ref}: no source at content/assignments/{ref}.md")
            return None
        body = render_page(src.read_text(), title, source=str(src))
        if self.dry:
            self.say(f"[dry] assignment {title} {points} pts")
            return None
        found = next((a for a in self.canvas.get(f"/courses/{self.course_id}/assignments")
                      if a["name"] == title), None)
        # A list of pairs, not a dict. Canvas reads an array parameter from a
        # repeated key, so a comma-joined string arrives as one invalid value
        # and the call fails with "Invalid submission types".
        data: list[tuple[str, Any]] = [
            ("assignment[name]", title),
            ("assignment[description]", body),
            ("assignment[points_possible]", points),
            ("assignment[assignment_group_id]", self.groups[group]),
            ("assignment[published]", "true"),
        ]
        for kind in ("online_upload", "online_text_entry"):
            data.append(("assignment[submission_types][]", kind))
        # The three things a lab submits: a screenshot, one exported file and a
        # written answer. No zip, no notebook, nothing that carries a key.
        for ext in ("png", "jpg", "jpeg", "pdf", "txt", "json"):
            data.append(("assignment[allowed_extensions][]", ext))
        obj = (self.canvas.put(f"/courses/{self.course_id}/assignments/{found['id']}", data=data)
               if found else self.canvas.post(f"/courses/{self.course_id}/assignments", data=data))
        self.say(f"assignment {title}: id {obj['id']}, {points} pts")
        self.attach_rubric(ref, obj)
        return obj

    def attach_rubric(self, ref: str, assignment: dict) -> None:
        src = yaml_source("rubrics", ref)
        if not src:
            self.skipped.append(f"rubric {ref}: no source at content/rubrics/{ref}.yaml")
            return
        spec = yaml.safe_load(src.read_text())
        data: dict[str, Any] = {
            "rubric[title]": spec.get("title", assignment["name"]),
            "rubric[free_form_criterion_comments]": "true",
            "rubric_association[association_id]": assignment["id"],
            "rubric_association[association_type]": "Assignment",
            "rubric_association[use_for_grading]": "true",
            "rubric_association[purpose]": "grading",
        }
        total = 0
        for i, crit in enumerate(spec["criteria"]):
            data[f"rubric[criteria][{i}][description]"] = crit["description"]
            data[f"rubric[criteria][{i}][long_description]"] = crit.get("long_description", "")
            data[f"rubric[criteria][{i}][points]"] = crit["points"]
            total += crit["points"]
            if crit.get("outcome"):
                oid = self.outcomes.get(crit["outcome"])
                if oid:
                    data[f"rubric[criteria][{i}][learning_outcome_id]"] = oid
            for j, level in enumerate(crit["levels"]):
                data[f"rubric[criteria][{i}][ratings][{j}][description]"] = level["description"]
                data[f"rubric[criteria][{i}][ratings][{j}][points]"] = level["points"]
        if total != assignment["points_possible"]:
            raise CanvasError(f"rubric {ref}: criteria sum to {total}, assignment is "
                              f"{assignment['points_possible']}. Fix the rubric, not this check.")
        # Update the rubric this assignment already has rather than posting a
        # new one. A plain POST every run left "... (1)" duplicates behind and
        # the association pointed at whichever copy was made first, so an
        # edited rubric silently did not reach the course.
        existing = next((r for r in self.canvas.get(f"/courses/{self.course_id}/rubrics")
                         if r["title"] in (data["rubric[title]"], assignment["name"])
                         or r["title"].startswith(data["rubric[title]"])), None)
        if existing:
            data["rubric[id]"] = existing["id"]
            self.canvas.put(f"/courses/{self.course_id}/rubrics/{existing['id']}", data=data)
        else:
            self.canvas.post(f"/courses/{self.course_id}/rubrics", data=data)
        self.say(f"  rubric {ref}: {len(spec['criteria'])} criteria, {total} pts, "
                 f"{sum(1 for c in spec['criteria'] if c.get('outcome'))} linked to an outcome")

    def make_discussion(self, ref: str, title: str, group: str | None = None,
                        points: int | None = None, ungraded: bool = False,
                        pinned: bool = False) -> dict | None:
        """A graded weekly board, or the ungraded pinned Q and A board.

        An ungraded board carries no assignment, so it takes no group and no
        points, and it does not require an initial post: a student reading the
        board to find an answer should not have to post one first.
        """
        src = md_source("discussions", ref)
        if not src:
            self.skipped.append(f"discussion {ref}: no source at content/discussions/{ref}.md")
            return None
        body = render_page(src.read_text(), title, source=str(src))
        if self.dry:
            self.say(f"[dry] discussion {title} "
                     + ("ungraded" if ungraded else f"{points} pts")
                     + (", pinned" if pinned else ""))
            return None
        found = next((d for d in self.canvas.get(f"/courses/{self.course_id}/discussion_topics")
                      if d["title"] == title), None)
        data: dict[str, Any] = {
            "title": title, "message": body, "discussion_type": "threaded",
            "published": "true",
        }
        if pinned:
            data["pinned"] = "true"
        if ungraded:
            data["require_initial_post"] = "false"
        else:
            if group is None or points is None:
                raise CanvasError(f"discussion {ref}: a graded board needs a group "
                                  f"and points in course.yaml, or ungraded: true")
            data["require_initial_post"] = "true"
            data["assignment[points_possible]"] = points
            data["assignment[assignment_group_id]"] = self.groups[group]
            data["assignment[submission_types][]"] = "discussion_topic"
        obj = (self.canvas.put(f"/courses/{self.course_id}/discussion_topics/{found['id']}", data=data)
               if found else self.canvas.post(f"/courses/{self.course_id}/discussion_topics", data=data))
        self.say(f"discussion {title}: id {obj['id']}, "
                 + ("ungraded" if ungraded else f"{points} pts")
                 + (", pinned" if pinned else ""))
        # Queue item Q5. The boards are 12 percent of the course grade and used
        # to reach Canvas with no rubric object at all: scoring lived in a prose
        # table on the page, with no levels and no partial credit, so a grader
        # had one box and a number. A graded discussion is backed by an
        # assignment, and that assignment is what a rubric attaches to.
        if not ungraded:
            aid = obj.get("assignment_id")
            if not aid:
                self.skipped.append(
                    f"discussion {ref}: graded, but Canvas returned no "
                    f"assignment_id, so no rubric could be attached")
            else:
                assignment = self.canvas.get(
                    f"/courses/{self.course_id}/assignments/{aid}")
                self.attach_rubric(ref, assignment)
        return obj

    def make_quiz(self, ref: str, title: str, group: str | None, points: int | None,
                  ungraded: bool) -> dict | None:
        src = yaml_source("quizzes", ref)
        if not src:
            self.skipped.append(f"quiz {ref}: no source at content/quizzes/{ref}.yaml")
            return None
        spec = yaml.safe_load(src.read_text())
        if self.dry:
            self.say(f"[dry] quiz {title} ({len(spec.get('questions', []))} questions)")
            return None
        found = next((q for q in self.canvas.get(f"/courses/{self.course_id}/quizzes")
                      if q["title"] == title), None)
        data = {
            "quiz[title]": title,
            "quiz[description]": spec.get("description", ""),
            "quiz[quiz_type]": "practice_quiz" if ungraded else "assignment",
            "quiz[published]": "false",
            "quiz[shuffle_answers]": str(spec.get("shuffle", True)).lower(),
            "quiz[allowed_attempts]": spec.get("attempts", -1),
            "quiz[scoring_policy]": "keep_highest",
            "quiz[hide_results]": "",
            "quiz[show_correct_answers]": str(spec.get("show_correct_answers", True)).lower(),
        }
        # Settings a self-check does not need and the final exam does. Each one
        # is only sent when the source names it, so the four existing quizzes
        # keep exactly the settings they were built with.
        for key, field in (("time_limit", "time_limit"),
                           ("one_question_at_a_time", "one_question_at_a_time"),
                           ("cant_go_back", "cant_go_back"),
                           ("one_time_results", "one_time_results"),
                           ("omit_from_final_grade", "omit_from_final_grade")):
            if key in spec:
                value = spec[key]
                data[f"quiz[{field}]"] = (str(value).lower()
                                          if isinstance(value, bool) else value)
        if not ungraded and group:
            data["quiz[assignment_group_id]"] = self.groups[group]
        obj = (self.canvas.put(f"/courses/{self.course_id}/quizzes/{found['id']}", data=data)
               if found else self.canvas.post(f"/courses/{self.course_id}/quizzes", data=data))
        qid = obj["id"]
        # Questions are replaced wholesale so an edited source cannot leave a
        # stale item. This used to be one pass: list them, delete each, then
        # post the new set. On 2026-09-11 a full-course push left the final
        # exam with 67 questions against a source of 46 -- 21 items duplicated,
        # points_possible 25.5 instead of 30, on a graded exam worth a fifth of
        # the course. Twenty-one had survived the delete pass and were then
        # written again beside their replacements.
        #
        # The cause does not have to be known to be closed: assume the delete
        # did not take, and check rather than trust. Re-list after deleting and
        # go again until the quiz is empty. If it will not empty, stop, because
        # posting a new set on top of an old one is how the duplicate exam got
        # made and a half-written exam is worse than a failed build.
        for attempt in range(5):
            leftover = self.canvas.get(
                f"/courses/{self.course_id}/quizzes/{qid}/questions")
            if not leftover:
                break
            for q in leftover:
                self.canvas.delete(
                    f"/courses/{self.course_id}/quizzes/{qid}/questions/{q['id']}")
        else:
            raise CanvasError(
                f"quiz {ref}: {len(leftover)} question(s) would not delete after "
                f"five passes. Refusing to write a new set on top of them, "
                f"because that is what duplicated the final exam on 2026-09-11.")
        n_pts = 0
        n_scored = 0
        for i, q in enumerate(spec.get("questions", [])):
            # A text block presents one artifact once, so the two or three items
            # that read it do not each repeat a header block. It holds no
            # answers, scores nothing, and is not a question, which is what
            # keeps the final exam multiple choice only as the brief requires.
            # Its position puts it directly above the items that read it.
            if q.get("type") == "text_only_question":
                self.canvas.post(f"/courses/{self.course_id}/quizzes/{qid}/questions",
                                 json_body={"question": {
                                     "question_name": q.get("name", f"Reference {i + 1}"),
                                     "question_text": q["text"],
                                     "question_type": "text_only_question",
                                     "points_possible": 0, "position": i + 1}})
                continue
            answers = []
            for a in q["answers"]:
                # The key is "comments". Canvas accepts "answer_comments"
                # without complaint and stores nothing, so every answer's
                # feedback was silently dropped. In an asynchronous course the
                # feedback on a wrong answer is the only teaching a student
                # gets after missing one, so this is worth a comment.
                answers.append({"answer_text": a["text"],
                                "answer_weight": 100 if a.get("correct") else 0,
                                "comments": a.get("feedback", "")})
            if not any(a["answer_weight"] == 100 for a in answers):
                raise CanvasError(f"quiz {ref} question {i + 1} has no correct answer")
            missing = [a["text"] for a in q["answers"] if not a.get("feedback")]
            if missing:
                raise CanvasError(f"quiz {ref} question {i + 1}: every answer needs its own "
                                  f"feedback, missing on {missing}")
            pts = q.get("points", 1)
            n_pts += pts
            n_scored += 1
            self.canvas.post(f"/courses/{self.course_id}/quizzes/{qid}/questions", json_body={
                "question": {"question_name": q.get("name", f"Question {i + 1}"),
                             "question_text": q["text"],
                             "question_type": "multiple_choice_question",
                             "points_possible": pts, "position": i + 1,
                             "answers": answers}})
        # Make Canvas recompute points_possible and question_count now that the
        # items exist. This used to be a POST to the questions endpoint with no
        # body, which is not a no-op: Canvas creates a real text-only question
        # from it, named "Question" and reading "Question text". Every quiz in
        # the course had one, at the end, where a student would see it. A plain
        # re-save does the same job and creates nothing.
        self.canvas.put(f"/courses/{self.course_id}/quizzes/{qid}",
                        data={"quiz[notify_of_update]": "false"})
        blocks = len(spec.get("questions", [])) - n_scored
        self.say(f"quiz {title}: id {qid}, {n_scored} questions"
                 + (f" and {blocks} text block(s)" if blocks else "")
                 + f", {n_pts} pts")
        if points is not None and n_pts != points and not ungraded:
            self.say(f"  WARNING quiz {ref} question points sum to {n_pts}, spine says {points}")
        return obj

    def make_notebook(self, ref: str, title: str) -> dict | None:
        src = notebook_source(ref)
        if not src:
            self.skipped.append(f"notebook {ref}: no source at lab/notebooks/{ref}.ipynb")
            return None
        if self.dry:
            self.say(f"[dry] notebook {title} ({src.stat().st_size} bytes)")
            return None
        fid = self.upload_file(src, NOTEBOOK_FOLDER)
        self.files[ref] = fid
        self.say(f"notebook {title}: file id {fid}")
        return {"id": fid}

    # ---------- modules ----------

    def build_modules(self) -> None:
        existing = {m["name"]: m for m in self.canvas.get(f"/courses/{self.course_id}/modules")}
        for position, mod in enumerate(self.spec["modules"], start=1):
            # A scoped build still walks the whole spine, so `position` stays
            # the module's real place in the course. Filtering the list instead
            # would renumber every later module and silently reorder Canvas.
            if self.only_modules is not None and mod["name"] not in self.only_modules:
                continue
            built: list[tuple[str, dict]] = []
            for item in mod["items"]:
                t = item["type"]
                if t == "page":
                    obj = self.make_page(item["ref"], item["title"])
                elif t == "assignment":
                    obj = self.make_assignment(item["ref"], item["title"], item["group"], item["points"])
                elif t == "discussion":
                    obj = self.make_discussion(item["ref"], item["title"], item.get("group"),
                                               item.get("points"),
                                               item.get("ungraded", False),
                                               item.get("pinned", False))
                elif t == "quiz":
                    obj = self.make_quiz(item["ref"], item["title"], item.get("group"),
                                         item.get("points"), item.get("ungraded", False))
                elif t == "notebook":
                    obj = self.make_notebook(item["ref"], item["title"])
                elif t == "url":
                    # The notebooks are baked into the notebook server now, so a
                    # module points at the one a student should open rather than
                    # handing them a file to download and upload again.
                    obj = {"id": None, "external_url": item["url"]}
                else:
                    raise CanvasError(f"unknown item type {t!r}")
                if obj:
                    built.append((t, obj, item["title"]))
            if self.dry:
                # `built` only holds the makers that return an object in dry
                # mode, and most of them return None, so counting it reported
                # 11 items for a 13 item module. A dry run is what somebody
                # reads to find out what is missing, so it counts the spine
                # instead and names anything with no source.
                have = [i for i in mod["items"] if self._exists(i)]
                missing = len(mod["items"]) - len(have)
                self.say(f"[dry] module {mod['name']}: {len(have)} items"
                         + (f", {missing} with no source yet" if missing else ""))
                continue
            if not built:
                self.skipped.append(f"module {mod['name']}: no items exist yet, module not created")
                continue
            found = existing.get(mod["name"])
            data = {"module[name]": mod["name"], "module[position]": position,
                    "module[published]": "true"}
            m = (self.canvas.put(f"/courses/{self.course_id}/modules/{found['id']}", data=data)
                 if found else self.canvas.post(f"/courses/{self.course_id}/modules", data=data))
            mid = m["id"]
            for old in self.canvas.get(f"/courses/{self.course_id}/modules/{mid}/items"):
                self.canvas.delete(f"/courses/{self.course_id}/modules/{mid}/items/{old['id']}")
            spine_titles = [title for _, _, title in built]
            for pos, (t, obj, _title) in enumerate(built, start=1):
                kind = {"page": "Page", "assignment": "Assignment", "discussion": "Discussion",
                        "quiz": "Quiz", "notebook": "File", "url": "ExternalUrl"}[t]
                # Every item carries the title the spine gives it. Without this
                # a File item shows its filename, so the module read
                # "w1-lab.ipynb" where the spine says "Week 1 lab notebook".
                data = {"module_item[type]": kind, "module_item[position]": pos,
                        "module_item[indent]": 0,
                        "module_item[title]": spine_titles[pos - 1]}
                if kind == "Page":
                    data["module_item[page_url]"] = obj["url"]
                elif kind == "ExternalUrl":
                    data["module_item[external_url]"] = obj["external_url"]
                    data["module_item[new_tab]"] = "true"
                else:
                    data["module_item[content_id]"] = obj["id"]
                self.canvas.post(f"/courses/{self.course_id}/modules/{mid}/items", data=data)
            self.canvas.put(f"/courses/{self.course_id}/modules/{mid}", data={"module[published]": "true"})
            self.say(f"module {mod['name']}: id {mid}, {len(built)} items, published")

    # ---------- verification ----------

    def verify(self) -> int:
        """Read the course back and compare it with the spine."""
        problems: list[str] = []
        course = self.canvas.get(f"/courses/{self.course_id}")
        c = self.spec["course"]
        if not course.get("apply_assignment_group_weights"):
            problems.append("course does not apply assignment group weights")
        if c.get("default_view") and course.get("default_view") != c["default_view"]:
            problems.append(f"course default_view is {course.get('default_view')!r}, "
                            f"want {c['default_view']!r}")
        # The prerequisite has to be stated where students read it, which is the
        # syllabus.
        syllabus = (self.canvas.get(f"/courses/{self.course_id}",
                                    **{"include[]": "syllabus_body"}).get("syllabus_body") or "")
        if "prerequisite" not in syllabus.lower():
            problems.append("the syllabus does not state the prerequisite, which the "
                            "build prompt requires the course description to carry")
        # This check was dead-coded behind `if False:` on the belief that Canvas
        # does not store public_description on a private course. It does store it
        # -- it just omits the field from GET /courses/:id unless
        # include[]=public_description is asked for, which the read-back above
        # does not do. Re-enabled with the include, because this is the only
        # automated guard on a field that has no visual cue anywhere in the
        # Canvas UI and that course copy drops silently: a section can look
        # complete and go live with an empty catalog description.
        if c.get("description"):
            blurb = (self.canvas.get(f"/courses/{self.course_id}",
                                     **{"include[]": "public_description"})
                     .get("public_description") or "")
            if not blurb.strip():
                problems.append("course has no public description, so the prerequisite "
                                "the build prompt requires is not published")
        if c.get("grading_standard"):
            standards = self.canvas.get(f"/courses/{self.course_id}/grading_standards")
            title = c["grading_standard"]["title"]
            if not any(g["title"] == title for g in standards):
                problems.append(f"grading standard missing: {title}")
            elif not course.get("grading_standard_id"):
                problems.append(f"grading standard {title} exists but the course does "
                                f"not use it")
        if c.get("front_page"):
            # Look it up by title, because Canvas names a page from its title
            # rather than from the ref this build uses.
            want = self.item_title(c["front_page"]) or c["name"]
            url = self.page_urls().get(want, slug(c["front_page"]))
            try:
                page = self.canvas.get(f"/courses/{self.course_id}/pages/{url}")
                if not page.get("front_page"):
                    problems.append(f"page {want} exists but is not the course front page")
            except CanvasError:
                problems.append(f"front page missing: {want}")
        groups = {g["name"]: g for g in self.canvas.get(f"/courses/{self.course_id}/assignment_groups")}
        for g in self.spec["assignment_groups"]:
            got = groups.get(g["name"])
            if not got:
                problems.append(f"assignment group missing: {g['name']}")
            elif got["group_weight"] != g["weight"]:
                problems.append(f"group {g['name']} weight is {got['group_weight']}, want {g['weight']}")
        total = sum(g["weight"] for g in self.spec["assignment_groups"])
        if total != 100:
            problems.append(f"group weights sum to {total}, not 100")
        # outcome_style=full, or Canvas returns an abbreviated outcome with no
        # calculation_method, no mastery_points and no ratings, and a check
        # against those reads None and fails for the wrong reason.
        links = self.canvas.get(f"/courses/{self.course_id}/outcome_group_links",
                                outcome_style="full")
        titles = {l["outcome"]["title"] for l in links}
        for item in self.spec["outcomes"]["items"]:
            if item["title"] not in titles:
                problems.append(f"outcome missing: {item['title']}")
        modules = {m["name"]: m for m in self.canvas.get(f"/courses/{self.course_id}/modules")}
        for mod in self.spec["modules"]:
            got = modules.get(mod["name"])
            if not got:
                if any(self._exists(i) for i in mod["items"]):
                    problems.append(f"module missing though its sources exist: {mod['name']}")
                continue
            want = [i for i in mod["items"] if self._exists(i)]
            items = self.canvas.get(f"/courses/{self.course_id}/modules/{got['id']}/items")
            if len(items) != len(want):
                problems.append(f"module {mod['name']}: Canvas has {len(items)} items, "
                                f"{len(want)} sources exist")
            got_titles = [i["title"] for i in items]
            want_titles = [i["title"] for i in want]
            if got_titles != want_titles:
                problems.append(f"module {mod['name']}: item titles differ.\n"
                                f"      Canvas: {got_titles}\n      spine:  {want_titles}")
            if got["published"] is False:
                problems.append(f"module {mod['name']} is unpublished")
        # Everything below was added after an independent read-back found four
        # defects this verifier had passed: a lab with no rubric, criteria not
        # linked to their outcome, every quiz answer's feedback silently
        # dropped, and Canvas's own default assignment group left behind. A
        # verifier that only checks what the builder sets cannot catch what
        # the builder never set.
        outcome_ids = {l["outcome"]["id"] for l in links}
        # How an Outcome rolls several results into one is the whole meaning of
        # the number the program reports. It was built as "highest", which the
        # approved plan considered and rejected by name because a strong
        # supporting week would mask a weak primary one. Nothing read it back,
        # so it sat wrong in Canvas while every document said otherwise.
        scale = self.spec["outcomes"]["scale"]
        want_ratings = [(r["description"], float(r["points"])) for r in scale["ratings"]]
        for link in links:
            o = link["outcome"]
            if o.get("calculation_method") != scale["calculation_method"]:
                problems.append(f"outcome {o['title']}: Canvas calculates "
                                f"{o.get('calculation_method')!r}, the spine says "
                                f"{scale['calculation_method']!r}. That changes what the "
                                f"program's outcome report says about every student.")
            if abs(float(o.get("mastery_points") or 0) - scale["mastery_points"]) > 0.01:
                problems.append(f"outcome {o['title']}: mastery is {o.get('mastery_points')}, "
                                f"the spine says {scale['mastery_points']}")
            got = [(r["description"], float(r["points"])) for r in (o.get("ratings") or [])]
            if got != want_ratings:
                problems.append(f"outcome {o['title']}: the rating scale in Canvas is "
                                f"{got}, the spine says {want_ratings}")
            # The six CLO texts are verbatim from the build brief, which says
            # plainly: do not add, remove, or reword them. Canvas stores the
            # description as HTML, so compare the text with the markup and the
            # entities taken back out.
            item = next((i for i in self.spec["outcomes"]["items"]
                         if i["title"] == o["title"]), None)
            if item:
                text = re.sub(r"<[^>]+>", "", o.get("description") or "")
                text = re.sub(r"\s+", " ", html.unescape(text)).strip()
                if text != re.sub(r"\s+", " ", item["description"]).strip():
                    problems.append(f"outcome {o['title']}: the description in Canvas is not "
                                    f"the course learning objective word for word. The brief "
                                    f"says these are not to be reworded.")
        assignments = {a["name"]: a for a in self.canvas.get(f"/courses/{self.course_id}/assignments")}
        for mod in self.spec["modules"]:
            for item in mod["items"]:
                if item["type"] != "assignment" or not self._exists(item):
                    continue
                a = assignments.get(item["title"])
                if not a:
                    problems.append(f"assignment missing: {item['title']}")
                    continue
                rubric = a.get("rubric") or []
                if not rubric:
                    problems.append(f"assignment {item['title']} has no rubric")
                    continue
                total = sum(r["points"] for r in rubric)
                if abs(total - a["points_possible"]) > 0.01:
                    problems.append(f"rubric for {item['title']} sums to {total}, "
                                    f"assignment is {a['points_possible']}")
                src = yaml_source("rubrics", item["ref"])
                want = sum(1 for c in yaml.safe_load(src.read_text())["criteria"] if c.get("outcome"))
                got = sum(1 for r in rubric
                          if (r.get("outcome_id") or r.get("learning_outcome_id")) in outcome_ids)
                if got != want:
                    problems.append(f"rubric for {item['title']}: {got} criteria linked to an "
                                    f"outcome, the source asks for {want}")
        for quiz in self.canvas.get(f"/courses/{self.course_id}/quizzes"):
            qs = self.canvas.get(f"/courses/{self.course_id}/quizzes/{quiz['id']}/questions")
            blank = sum(1 for q in qs for a in (q.get("answers") or [])
                        if not (a.get("comments") or a.get("comments_html")))
            if blank:
                problems.append(f"quiz {quiz['title']}: {blank} answer(s) carry no feedback")
            if not qs:
                problems.append(f"quiz {quiz['title']} has no questions")
            # Nothing here publishes a quiz on purpose: make_quiz sends
            # quiz[published]=false so all 46 exam items can be deleted and
            # re-posted while the quiz is hidden, and it is the module publish
            # in build_modules that re-publishes it. That cascade is Canvas's
            # behaviour, not ours -- measured 2026-09-12, it fires even when the
            # module is already published -- so assert the end state instead of
            # trusting it. A quiz left unpublished in the shell copies into every
            # section as a hidden assessment, and no other gate reads this field.
            if not quiz.get("published"):
                problems.append(f"quiz {quiz['title']} is not published; every section "
                                f"copied from this shell would ship it hidden")
            # Every scored item in the source has to be in Canvas. A dropped
            # question changes the exam's total without failing anything, and
            # a text block that lost its position no longer sits above the
            # items that read it.
            item = next((i for m in self.spec["modules"] for i in m["items"]
                         if i["type"] == "quiz" and i["title"] == quiz["title"]), None)
            if not item:
                continue
            src = yaml_source("quizzes", item["ref"])
            if not src:
                continue
            spec = yaml.safe_load(src.read_text())
            want_scored = [q for q in spec.get("questions", [])
                           if q.get("type") != "text_only_question"]
            want_blocks = len(spec.get("questions", [])) - len(want_scored)
            got_scored = [q for q in qs if q.get("question_type") != "text_only_question"]
            got_blocks = len(qs) - len(got_scored)
            if len(got_scored) != len(want_scored):
                problems.append(f"quiz {quiz['title']}: {len(got_scored)} scored question(s) "
                                f"in Canvas, the source has {len(want_scored)}")
            if got_blocks != want_blocks:
                problems.append(f"quiz {quiz['title']}: {got_blocks} text block(s) in Canvas, "
                                f"the source has {want_blocks}")
            want_points = sum(q.get("points", 1) for q in want_scored)
            if item.get("points") is not None and want_points != item["points"]:
                problems.append(f"quiz {quiz['title']}: the source sums to {want_points} points, "
                                f"the spine says {item['points']}")
        # What the course actually hands a student. A file here that should not
        # be here is the worst defect this build can ship, and it is invisible:
        # every page still renders, every quiz still scores, and the answer key
        # is a click away in Files.
        live = self.canvas.get(f"/courses/{self.course_id}/files")
        names = [f["display_name"] for f in live]
        for banned in self.spec.get("never_ship") or []:
            if banned in names:
                problems.append(f"{banned} is in the course files. It is on the never_ship "
                                f"list because it answers the labs. Delete it.")
        want: set[str] = set()
        for entry in self.spec.get("student_files") or []:
            if "glob" in entry:
                want.update(p.name for p in BUILDER.glob(entry["glob"]))
            elif (BUILDER / entry["path"]).exists():
                want.add(Path(entry["path"]).name)
        missing = sorted(want - set(names))
        if missing:
            problems.append(f"{len(missing)} student file(s) named in the spine are not in "
                            f"Canvas: {missing[:6]}{' ...' if len(missing) > 6 else ''}")
        # The upload is add-only: it puts every allowlisted file into Canvas
        # and never removes one that has stopped being allowlisted. So a file
        # that is renamed, retired or dropped stays in the course forever,
        # and nothing notices.
        #
        # It happened. The corpus renamed a vendor because the name matched a
        # real registered company, and 013-tidefern-census-correction.eml sat
        # in the course files afterwards, under the retired name, while every
        # gate reported clean. Deleting is not done here, because a course
        # file may have been put there deliberately by an instructor; it is
        # reported so a person decides.
        managed = {e["folder"] for e in self.spec.get("student_files") or []}
        folders = {f["id"]: f["full_name"] for f in
                   self.canvas.get(f"/courses/{self.course_id}/folders")}
        for f in live:
            folder = folders.get(f["folder_id"], "")
            rel = folder.split("course files/", 1)[-1]
            if rel in managed and f["display_name"] not in want:
                problems.append(f"{f['display_name']} is in {rel} and the spine does not "
                                f"name it. The upload never deletes, so a renamed or "
                                f"retired file stays until someone removes it.")
        # Canvas scales group weights that do not add to 100, silently, and a
        # gradebook that quietly renormalises is a grade dispute nobody can
        # answer. tools/cartridge.py checks this for the other two courses in
        # this repository; it cannot run against this spine, whose shape
        # differs, so the check lives here as well.
        weights = [(g["name"], g["weight"]) for g in self.spec["assignment_groups"]]
        total_weight = sum(w for _, w in weights)
        if total_weight != 100:
            problems.append(f"assignment group weights add to {total_weight}, not 100: "
                            + ", ".join(f"{n} {w}" for n, w in weights)
                            + ". Canvas scales them to 100 without saying so.")
        live_groups = {g["name"]: g for g in self.canvas.get(
            f"/courses/{self.course_id}/assignment_groups")}
        for name, weight in weights:
            found = live_groups.get(name)
            if found is None:
                problems.append(f"assignment group missing in Canvas: {name}")
            elif abs((found.get("group_weight") or 0) - weight) > 0.01:
                problems.append(f"assignment group {name}: Canvas has weight "
                                f"{found.get('group_weight')}, the spine says {weight}")
        course = self.canvas.get(f"/courses/{self.course_id}")
        if self.spec["course"].get("apply_group_weights") and not course.get(
                "apply_assignment_group_weights"):
            problems.append("the spine weights the groups, and Canvas has group weighting "
                            "switched off, so every weight above is being ignored")
        declared = {g["name"] for g in self.spec["assignment_groups"]}
        for g in self.canvas.get(f"/courses/{self.course_id}/assignment_groups"):
            if g["name"] not in declared:
                problems.append(f"assignment group {g['name']!r} is not in the spine. "
                                f"Canvas creates one by default; delete it or the gradebook "
                                f"shows a group the course does not use")
        for line in problems:
            print("FAIL " + line)
        print(f"\nverify: {len(problems)} problem(s)")
        return 1 if problems else 0

    def _exists(self, item: dict) -> bool:
        if item["type"] == "url":
            return True          # a link has no source file to look for
        t, ref = item["type"], item["ref"]
        return bool({"page": page_source(ref), "notebook": notebook_source(ref),
                     "assignment": md_source("assignments", ref),
                     "discussion": md_source("discussions", ref),
                     "quiz": yaml_source("quizzes", ref)}[t])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="say what would change, call nothing")
    ap.add_argument("--verify", action="store_true", help="read Canvas back and compare")
    ap.add_argument("--spec", default=str(CONTENT / "course.yaml"))
    ap.add_argument("--week", action="append", metavar="N",
                    help="build only this week's module. Repeatable, and a "
                         "comma-separated list works. Use 'start' for the "
                         "orientation modules. Course settings, assignment "
                         "groups and outcomes still run; they are idempotent.")
    ap.add_argument("--list-weeks", action="store_true",
                    help="print the week each module answers to, then stop")
    ap.add_argument("--allow-published", action="store_true",
                    help="build even though the target course is published or has "
                         "students. Only for a shell you have deliberately published; "
                         "never for a term section copied from the shell.")
    args = ap.parse_args(argv)

    if args.list_weeks:
        spec = yaml.safe_load(Path(args.spec).read_text())
        print(f"{'week':>6}  module")
        for mod in spec["modules"]:
            print(f"{module_week(mod['name']):>6}  {mod['name']}")
        return 0

    base, token = os.environ.get("CANVAS_BASE"), os.environ.get("CANVAS_TOKEN")
    if not base or not token:
        sys.exit("Set CANVAS_BASE and CANVAS_TOKEN in the environment. They are never stored here.")
    spec = yaml.safe_load(Path(args.spec).read_text())
    canvas = Canvas(base, token)
    who = canvas.get("/users/self")
    print(f"Canvas {base} as {who.get('name')} (id {who.get('id')}), "
          f"course {spec['course']['canvas_id']}\n")

    b = Builder(canvas, spec, dry=args.check)
    if args.week:
        weeks = {w.strip() for arg in args.week for w in arg.split(",") if w.strip()}
        b.scope_to(weeks)
    if args.verify:
        return b.verify()
    # The course in the spine is the MASTER SHELL, and every term section is a
    # copy of it. This builder must never be pointed at a section. build_modules
    # deletes and recreates every module item, so module progression resets and
    # every item id changes, which breaks any link a student or an announcement
    # already holds; it forces modules, pages, assignments and discussions to
    # published, including anything an instructor hid for staged release; and the
    # spine is the only source of a module's item list, so anything added to a
    # section by hand is deleted with nothing in the repo to restore it. All of
    # that is harmless on an unpublished shell with no students, which is why it
    # is written this way -- and none of it is undoable on a live course.
    if not args.check:
        cid = spec["course"]["canvas_id"]
        target = canvas.get(f"/courses/{cid}")
        students = canvas.get(f"/courses/{cid}/enrollments",
                              **{"type[]": "StudentEnrollment", "state[]": "active"})
        if not args.allow_published and (target.get("workflow_state") == "available"
                                         or students):
            sys.exit(
                f"REFUSING to build: course {cid} ({target.get('name')!r}) is "
                f"{target.get('workflow_state')} with {len(students)} active student(s).\n"
                "This builder rebuilds module items destructively and publishes what it\n"
                "touches, so it is meant for the unpublished master shell, not for a term\n"
                "section copied from it. Point canvas_id at the shell -- or pass\n"
                "--allow-published if this course really is the shell.")
    # The front page has to exist before Canvas will accept default_view=wiki,
    # so the course settings are applied in two passes around it.
    b.settings(with_view=False)
    b.assignment_groups()
    b.build_outcomes()
    b.front_page()
    b.settings()
    b.student_files()
    b.build_modules()
    if b.skipped:
        print("\nSkipped, no source yet:")
        for s in b.skipped:
            print("  " + s)
    scope = ("the whole course" if b.only_modules is None
             else f"{len(b.only_modules)} module(s)")
    print(f"\n{len(b.report)} object(s) built, {len(b.skipped)} skipped, in {scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
