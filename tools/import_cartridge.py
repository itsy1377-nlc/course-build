"""Import the cartridge into a running Canvas, and check what actually arrived.

    python -m tools.import_cartridge                    build, import, verify
    python -m tools.import_cartridge --no-build         import what is in build/
    python -m tools.import_cartridge --course 1

Credentials come from canvas/.canvas-credentials, written by the deploy script.

The last step is the one that matters. An import that reports "completed" has
told you the job finished, not that the course is right. So after the migration
finishes this reads the course back through the API and checks it against
content/course.yaml: the modules, the item counts, the assignment groups and
their weights, the points on every graded item, the quiz question counts, and
the rubrics. Anything that did not survive the trip is printed.

Verifying a deployment by reading it back is the same habit the course teaches
about attacks. The tool said it worked is not evidence.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
CREDENTIALS = ROOT / "canvas" / ".canvas-credentials"
DEFAULT_CARTRIDGE = ROOT / "build" / "itsy1377.imscc"


class ImportError_(Exception):
    pass


def credentials() -> tuple[str, str]:
    if not CREDENTIALS.exists():
        raise ImportError_(
            f"No credentials at {CREDENTIALS.relative_to(ROOT)}.\n"
            f"Run ./canvas/deploy/setup.sh, or write the file by hand:\n"
            f"  CANVAS_URL=http://localhost:3000\n"
            f"  CANVAS_TOKEN=<a token minted from the Rails console>"
        )
    values = {}
    for line in CREDENTIALS.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values["CANVAS_URL"].rstrip("/"), values["CANVAS_TOKEN"]


def public_url() -> str:
    """The address a browser uses to reach Canvas, which is not always ours.

    Canvas canonicalises file links when a page is saved, and it builds the
    absolute URL from the host on the incoming request rather than from
    config/domain.yml. Saving a page over http://localhost:3000 therefore
    stamps localhost into every file link in it, and anyone opening the course
    from another computer gets a link to their own machine. Measured directly:
    the same PUT sent to the LAN address stored the LAN address instead.

    So writes that touch file links go through this, and it defaults to
    CANVAS_URL when nothing else is set.
    """
    values = {}
    if CREDENTIALS.exists():
        for line in CREDENTIALS.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return (values.get("CANVAS_PUBLIC_URL") or values.get("CANVAS_URL", "")).rstrip("/")


class Canvas:
    def __init__(self, url: str, token: str):
        self.url = url
        # Kept so a second client can be built for the same Canvas on a
        # different host. See populate_canvas.fix_media_links.
        self.token = token
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, **params) -> Any:
        """A GET that follows pagination.

        per_page=100 with no Link following silently truncates, and every
        caller assumed it had the whole list. The course's media folder held
        136 files while this returned 100, so a cleanup pass believed it had
        removed everything and left 36 behind.
        """
        response = self.session.get(f"{self.url}/api/v1{path}",
                                    params={"per_page": 100, **params}, timeout=60)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            return payload
        while True:
            link = response.headers.get("Link", "")
            match = re.search(r'<([^>]+)>;\s*rel="next"', link)
            if not match:
                return payload
            response = self.session.get(match.group(1), timeout=60)
            response.raise_for_status()
            payload.extend(response.json())

    def post(self, path: str, **data) -> Any:
        response = self.session.post(f"{self.url}/api/v1{path}", data=data, timeout=60)
        response.raise_for_status()
        return response.json()


def upload(canvas: Canvas, course_id: int, cartridge: Path) -> dict:
    """Canvas takes a file in two steps: ask permission, then send it."""
    size = cartridge.stat().st_size
    migration = canvas.post(
        f"/courses/{course_id}/content_migrations",
        **{
            "migration_type": "common_cartridge_importer",
            "pre_attachment[name]": cartridge.name,
            "pre_attachment[size]": str(size),
            "settings[overwrite_quizzes]": "true",
        },
    )
    pre = migration.get("pre_attachment") or {}
    upload_url = pre.get("upload_url")
    if not upload_url:
        raise ImportError_(f"Canvas did not offer an upload URL: {migration}")

    fields = {k: (None, str(v)) for k, v in (pre.get("upload_params") or {}).items()}
    with cartridge.open("rb") as handle:
        fields["file"] = (cartridge.name, handle, "application/zip")
        response = requests.post(upload_url, files=fields, timeout=300,
                                 allow_redirects=False)
    if response.status_code not in (200, 201, 302):
        raise ImportError_(f"Upload failed: HTTP {response.status_code} {response.text[:300]}")
    # Canvas answers the upload with a redirect that finalises the attachment.
    if response.status_code == 302 and response.headers.get("Location"):
        follow = requests.get(response.headers["Location"], timeout=120)
        follow.raise_for_status()
    return migration


def wait(canvas: Canvas, course_id: int, migration_id: int, timeout: int = 600) -> dict:
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        state = canvas.get(f"/courses/{course_id}/content_migrations/{migration_id}")
        workflow = state.get("workflow_state", "")
        if workflow != last:
            print(f"  {workflow}")
            last = workflow
        if workflow in ("completed", "failed"):
            return state
        time.sleep(3)
    raise ImportError_("The migration did not finish in time.")


# ---------------------------------------------------------------------------
# Reading it back
# ---------------------------------------------------------------------------


def verify(canvas: Canvas, course_id: int) -> list[str]:
    course = yaml.safe_load((ROOT / "content" / "course.yaml").read_text(encoding="utf-8"))
    problems: list[str] = []

    modules = canvas.get(f"/courses/{course_id}/modules", include=["items"])
    by_title = {m["name"]: m for m in modules}
    for expected in course["modules"]:
        found = by_title.get(expected["title"])
        if not found:
            problems.append(f"module missing: {expected['title']}")
            continue
        items = canvas.get(f"/courses/{course_id}/modules/{found['id']}/items")
        if len(items) != len(expected["items"]):
            problems.append(
                f"module '{expected['title']}' has {len(items)} items, "
                f"course.yaml says {len(expected['items'])}")

    groups = canvas.get(f"/courses/{course_id}/assignment_groups")
    groups_by_title = {g["name"]: g for g in groups}
    for expected in course["assignment_groups"]:
        found = groups_by_title.get(expected["title"])
        if not found:
            problems.append(f"assignment group missing: {expected['title']}")
        elif float(found.get("group_weight") or 0) != float(expected["weight"]):
            problems.append(
                f"group '{expected['title']}' imported at weight "
                f"{found.get('group_weight')}, should be {expected['weight']}")

    assignments = canvas.get(f"/courses/{course_id}/assignments")
    assignments_by_title = {a["name"]: a for a in assignments}
    for row in course.get("assignments", []):
        found = assignments_by_title.get(row["title"])
        if not found:
            problems.append(f"assignment missing: {row['title']}")
            continue
        if float(found.get("points_possible") or 0) != float(row["points"]):
            problems.append(
                f"assignment '{row['title']}' imported at "
                f"{found.get('points_possible')} points, should be {row['points']}")
        if row.get("rubric") and not found.get("rubric"):
            problems.append(f"assignment '{row['title']}' has no rubric attached")

    quizzes = canvas.get(f"/courses/{course_id}/quizzes")
    quizzes_by_title = {q["title"]: q for q in quizzes}
    for row in course.get("quizzes", []):
        found = quizzes_by_title.get(row["title"])
        if not found:
            problems.append(f"quiz missing: {row['title']}")
            continue
        expected_questions = len(
            yaml.safe_load((ROOT / "content" / "quizzes" / f"{row['ref']}.yaml")
                           .read_text(encoding="utf-8"))["questions"])
        actual = found.get("question_count")
        if actual != expected_questions:
            problems.append(
                f"quiz '{row['title']}' imported {actual} questions, "
                f"the file has {expected_questions}")
        if float(found.get("points_possible") or 0) != float(row["points"]):
            problems.append(
                f"quiz '{row['title']}' imported at {found.get('points_possible')} "
                f"points, should be {row['points']}")

    pages = canvas.get(f"/courses/{course_id}/pages")
    expected_pages = sum(1 for m in course["modules"]
                         for i in m["items"] if i["type"] == "page")
    if len(pages) < expected_pages:
        problems.append(f"{len(pages)} pages imported, expected at least {expected_pages}")

    # Nothing may carry a template placeholder into a published course.
    for page in pages[:80]:
        body = canvas.get(f"/courses/{course_id}/pages/{page['url']}").get("body") or ""
        if "#fbeeb8" in body or "phpally-ignore" in body:
            problems.append(f"page '{page['title']}' still contains a template placeholder")

    return problems


def summarize(canvas: Canvas, course_id: int) -> None:
    counts = {
        "modules": len(canvas.get(f"/courses/{course_id}/modules")),
        "pages": len(canvas.get(f"/courses/{course_id}/pages")),
        "assignments": len(canvas.get(f"/courses/{course_id}/assignments")),
        "quizzes": len(canvas.get(f"/courses/{course_id}/quizzes")),
        "discussions": len(canvas.get(f"/courses/{course_id}/discussion_topics")),
        "assignment groups": len(canvas.get(f"/courses/{course_id}/assignment_groups")),
        "rubrics": len(canvas.get(f"/courses/{course_id}/rubrics")),
        "outcomes": len(canvas.get(f"/courses/{course_id}/outcome_group_links")),
    }
    print("\nWhat is in the course now:")
    for name, count in counts.items():
        print(f"  {name:20} {count}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import the cartridge into Canvas.")
    parser.add_argument("--course", type=int, default=1)
    parser.add_argument("--cartridge", default=str(DEFAULT_CARTRIDGE))
    parser.add_argument("--session", default="fall-flex-2")
    parser.add_argument("--no-build", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--skip-quizzes", action="store_true",
                        help="Do not create the quizzes over the API afterwards. "
                             "Only useful against a Canvas that has the QTI converter.")
    args = parser.parse_args(argv)

    try:
        url, token = credentials()
    except ImportError_ as exc:
        print(exc)
        return 2
    canvas = Canvas(url, token)

    if args.verify_only:
        problems = verify(canvas, args.course)
        summarize(canvas, args.course)
        return _report(problems, url, args.course)

    cartridge = Path(args.cartridge)
    if not args.no_build:
        from tools.cartridge import BuildError, build
        try:
            build(cartridge, session=args.session)
        except BuildError as exc:
            print(exc)
            return 1
    if not cartridge.exists():
        print(f"No cartridge at {cartridge}")
        return 1

    # Canvas renames rather than replaces on re-import, so stale media has to
    # go before the upload or the course keeps serving the first cut forever.
    from tools.populate_canvas import clear_media
    removed = clear_media(canvas, args.course)
    if removed:
        print(f"\nCleared {removed} existing media file(s) so this import replaces "
              f"rather than duplicates.")

    print(f"\nImporting into course {args.course} at {url}")
    try:
        migration = upload(canvas, args.course, cartridge)
        state = wait(canvas, args.course, migration["id"])
    except (ImportError_, requests.RequestException) as exc:
        print(f"\nImport failed: {exc}")
        return 1

    if state.get("workflow_state") != "completed":
        print(f"\nThe migration ended in state {state.get('workflow_state')!r}")
        for issue in state.get("migration_issues") or []:
            print(f"  {issue}")
        return 1

    issues = canvas.get(
        f"/courses/{args.course}/content_migrations/{migration['id']}/migration_issues")
    if issues:
        print(f"\nCanvas reported {len(issues)} migration issue(s):")
        for issue in issues[:10]:
            print(f"  [{issue.get('issue_type')}] {issue.get('description')}")

    # The cartridge carries the quizzes, and a Canvas with no QTI converter
    # drops all of them without saying so. See tools/populate_canvas.py for the
    # whole story. On Alamo's Canvas this step is unnecessary and harmless.
    if not args.skip_quizzes:
        from tools.populate_canvas import sync_quizzes
        print("\nCreating the quizzes over the API, because this Canvas cannot read "
              "them from the cartridge.")
        for problem in sync_quizzes(canvas, args.course, args.session):
            print(f"  - {problem}")

    # Canvas rewrites a cartridge's file references in some HTML attributes and
    # not others, and makes one of them absolute. Both leave a course that
    # imported cleanly and still shows a broken player, so the media links get
    # one pass afterwards. See fix_media_links for what and why.
    from tools.populate_canvas import fix_media_links
    print("\nResolving the media links the importer left behind.")
    media_problems = fix_media_links(canvas, args.course)
    for problem in media_problems:
        print(f"  - {problem}")
    if not media_problems:
        print("  every media reference resolves, and none is host specific")

    print("\nReading the course back to check what actually arrived.")
    problems = verify(canvas, args.course)
    summarize(canvas, args.course)
    return _report(problems, url, args.course)


def _report(problems: list[str], url: str, course_id: int) -> int:
    if problems:
        print(f"\n{len(problems)} thing(s) did not survive the import:\n")
        for problem in problems:
            print(f"  - {problem}")
        print()
        return 1
    print(f"\nEverything in course.yaml is present and correct in Canvas.")
    print(f"  {url}/courses/{course_id}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
