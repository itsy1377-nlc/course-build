"""Create the quizzes in Canvas over the API, and fix up module items.

    python -m tools.populate_canvas --course 1

WHY THIS EXISTS, because it is not obvious and it cost real time to find.

The Common Cartridge carries the quizzes correctly. Canvas will not read them.

Canvas converts QTI on import by shelling out to an external Python program,
`migrate.py` from the QTIMigrationTool. `gems/plugins/qti_exporter/lib/qti.rb`
looks for it in two vendored locations and then on PATH, and registers the
`qti_converter` plugin as `enabled: python_converter_found`. Open-source Canvas
does not ship that program. So the plugin is disabled, and **every quiz in
every cartridge is silently dropped**. The import still reports "completed",
with no error, no warning, and no migration issue.

This is not a defect in the cartridge. The NLC template's own export, produced
by Instructure's own Canvas, imports zero of its two quizzes into this
instance. That was the test that separated "my file is wrong" from "this Canvas
cannot read any file", and it is the reason the import tool reads the course
back instead of trusting the word completed.

Consequences worth stating plainly:

  - On Alamo's Canvas, which is Instructure-hosted and has the converter, the
    cartridge carries everything including quizzes. Nothing here is needed.
  - On a local open-source Canvas, quizzes have to come over the REST API
    instead. That is what this script does.
  - So the deliverable is the cartridge, and this script is what makes the
    local demo complete. Both are needed, for different reasons, and the
    runbook says so.

Classic Quizzes only. New Quizzes has a documented API at `/api/quiz/v1/` and
no route anywhere in the open-source code, because it is a separate hosted
service.
"""

from __future__ import annotations

import os
import argparse
import re
import sys
from html import unescape
import time
from pathlib import Path
from typing import Any

import requests
import yaml

from tools.dates import DateMap
from tools.import_cartridge import Canvas, ImportError_, credentials, public_url

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / os.environ.get("ITSY_CONTENT", "content")

def _staging_dir(root):
    """Per course tree. This was shared between the two courses, and the second
    build's pages were written over the first course after a correct import."""
    rel = os.environ.get("ITSY_CONTENT", "content").rsplit("/", 1)[-1]
    return root / "build" / ("cartridge" if rel == "content" else f"cartridge-{rel}")



CANVAS_TYPE = {
    "multiple_choice": "multiple_choice_question",
    "true_false": "true_false_question",
    "multiple_answers": "multiple_answers_question",
    "short_answer": "short_answer_question",
    "numerical": "numerical_question",
    "essay": "essay_question",
}


def _html(text: str) -> str:
    import markdown as markdown_lib
    return markdown_lib.markdown(str(text or "").strip(),
                                 extensions=["fenced_code", "tables", "sane_lists"])


def _question_payload(question: dict, position: int) -> dict[str, Any]:
    kind = question["type"]
    # The outcome tag rides in the question name so the item analysis export is
    # the per-outcome score matrix program assessment asks for. Classic Quizzes
    # has no per-item outcome field, so this is a workaround, and knowing it is
    # one matters more than hiding it.
    data: dict[str, Any] = {
        "question[question_name]": f"{question.get('outcome', 'O?')} | {question['id']}",
        "question[question_text]": _html(question["text"]),
        "question[question_type]": CANVAS_TYPE[kind],
        "question[points_possible]": float(question.get("points", 1)),
        "question[position]": position,
    }
    if question.get("general_feedback"):
        data["question[neutral_comments_html]"] = _html(question["general_feedback"])

    if kind in ("multiple_choice", "true_false", "multiple_answers"):
        for index, answer in enumerate(question.get("answers", [])):
            data[f"question[answers][{index}][answer_text]"] = answer["text"]
            data[f"question[answers][{index}][answer_html]"] = _html(answer["text"])
            data[f"question[answers][{index}][answer_weight]"] = (
                100 if answer.get("correct") else 0)
            if answer.get("feedback"):
                data[f"question[answers][{index}][answer_comment_html]"] = _html(
                    answer["feedback"])

    elif kind == "short_answer":
        accepted = question.get("accepted") or []
        if not accepted:
            # The right answer is different for every student, so Canvas cannot
            # score it. Collected here, checked by the instructor against the
            # student ID. Canvas has no way to express "recompute per student",
            # and pretending otherwise would be worse than saying so.
            data["question[question_type]"] = "essay_question"
        for index, value in enumerate(accepted):
            data[f"question[answers][{index}][answer_text]"] = str(value)
            data[f"question[answers][{index}][answer_weight]"] = 100

    elif kind == "numerical":
        data["question[answers][0][numerical_answer_type]"] = "exact_answer"
        data["question[answers][0][answer_exact]"] = float(question.get("value", 0))
        data["question[answers][0][answer_error_margin]"] = float(
            question.get("tolerance", 0))
        data["question[answers][0][answer_weight]"] = 100

    return data


def sync_quizzes(canvas: Canvas, course_id: int, session: str,
                 quiet: bool = False) -> list[str]:
    course = yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))
    dates = DateMap(session)
    problems: list[str] = []

    groups = {g["name"]: g["id"] for g in canvas.get(f"/courses/{course_id}/assignment_groups")}
    existing = {q["title"]: q for q in canvas.get(f"/courses/{course_id}/quizzes")}

    for row in course.get("quizzes", []):
        path = CONTENT / "quizzes" / f"{row['ref']}.yaml"
        quiz = yaml.safe_load(path.read_text(encoding="utf-8"))
        title = row["title"]

        group_title = next(g["title"] for g in course["assignment_groups"]
                           if g["id"] == row["group"])
        group_id = groups.get(group_title)
        if group_id is None:
            problems.append(f"{title}: assignment group '{group_title}' is not in Canvas yet")
            continue

        attempts = row.get("allowed_attempts", 1)
        payload = {
            "quiz[title]": title,
            "quiz[description]": _html(quiz.get("description", "")),
            "quiz[quiz_type]": "assignment",
            "quiz[assignment_group_id]": group_id,
            "quiz[allowed_attempts]": attempts,
            "quiz[scoring_policy]": row.get("scoring_policy", "keep_highest"),
            "quiz[shuffle_answers]": str(bool(row.get("shuffle_answers", False))).lower(),
            "quiz[show_correct_answers]": "true",
            "quiz[one_question_at_a_time]": "false",
            "quiz[published]": "false",
        }
        if row.get("time_limit_minutes"):
            payload["quiz[time_limit]"] = row["time_limit_minutes"]
        if row.get("due_day"):
            payload["quiz[due_at]"] = dates.at(row["due_day"])
        if row.get("unlock_day"):
            payload["quiz[unlock_at]"] = dates.at(row["unlock_day"], hour=0, minute=1)

        if title in existing:
            quiz_id = existing[title]["id"]
            canvas.session.put(f"{canvas.url}/api/v1/courses/{course_id}/quizzes/{quiz_id}",
                               data=payload, timeout=60).raise_for_status()
            # Remove old questions so a rebuild is a replacement, not a pile-up.
            for question in canvas.get(
                    f"/courses/{course_id}/quizzes/{quiz_id}/questions"):
                canvas.session.delete(
                    f"{canvas.url}/api/v1/courses/{course_id}/quizzes/{quiz_id}"
                    f"/questions/{question['id']}", timeout=60)
            action = "updated"
        else:
            created = canvas.post(f"/courses/{course_id}/quizzes", **payload)
            quiz_id = created["id"]
            action = "created"

        for position, question in enumerate(quiz["questions"], start=1):
            try:
                canvas.post(f"/courses/{course_id}/quizzes/{quiz_id}/questions",
                            **_question_payload(question, position))
            except requests.HTTPError as exc:
                problems.append(f"{title} / {question['id']}: {exc}")

        # Publishing last. A quiz published before its questions exist is a
        # quiz students can open and score zero on.
        canvas.session.put(
            f"{canvas.url}/api/v1/courses/{course_id}/quizzes/{quiz_id}",
            data={"quiz[published]": "true", "quiz[notify_of_update]": "false"},
            timeout=60).raise_for_status()

        # Canvas recomputes question_count and points_possible in a background
        # job, and quiz.points_possible is what the GRADEBOOK scores against.
        # Reading it straight after the publish is worthless: it returns the
        # stale value from before the rebuild, which matches, so the check
        # passes and the job then lands on a wrong number nobody looks at
        # again. That is exactly how the final exam sat at 117 of 120 points,
        # one question short, through a clean import that reported success.
        #
        # So: wait for the counters to settle, and re-save once if they do not.
        # A quiz save with no submissions is safe and forces the recompute.
        expected_questions = len(quiz["questions"])
        expected_points = float(row["points"])
        settled = False
        for attempt in range(2):
            for _ in range(15):
                after = canvas.get(f"/courses/{course_id}/quizzes/{quiz_id}")
                if (after.get("question_count") == expected_questions
                        and abs(float(after.get("points_possible") or 0)
                                - expected_points) <= 0.01):
                    settled = True
                    break
                time.sleep(1)
            if settled:
                break
            # Nudge it. The false to true transition is what triggers the
            # recompute, and it has to happen after every question exists.
            for state in ("false", "true"):
                canvas.session.put(
                    f"{canvas.url}/api/v1/courses/{course_id}/quizzes/{quiz_id}",
                    data={"quiz[published]": state,
                          "quiz[notify_of_update]": "false"},
                    timeout=60).raise_for_status()

        if not settled:
            problems.append(
                f"{title}: Canvas settled on {after.get('question_count')} questions "
                f"and {float(after.get('points_possible') or 0):g} points; the file "
                f"has {expected_questions} questions and course.yaml says "
                f"{row['points']} points")

        if not quiet:
            print(f"  {action:8} {title:58} "
                  f"{after.get('question_count')} items, "
                  f"{float(after.get('points_possible') or 0):g} points")

        _place_in_module(canvas, course_id, course, row["ref"], quiz_id, title, problems)

    return problems


def _place_in_module(canvas: Canvas, course_id: int, course: dict, ref: str,
                     quiz_id: int, title: str, problems: list[str]) -> None:
    """Put the quiz back where course.yaml says it goes.

    The cartridge already built the module with everything else in it, in
    order. The quiz has to land in the same position, or the module reads as
    though a step is missing.
    """
    for module_spec in course["modules"]:
        refs = [item["ref"] for item in module_spec["items"]]
        if ref not in refs:
            continue
        position = refs.index(ref) + 1

        modules = {m["name"]: m for m in canvas.get(f"/courses/{course_id}/modules")}
        module = modules.get(module_spec["title"])
        if not module:
            problems.append(f"{title}: module '{module_spec['title']}' is not in Canvas")
            return

        items = canvas.get(f"/courses/{course_id}/modules/{module['id']}/items")
        for item in items:
            if item.get("title") == title:
                return  # already there
        try:
            canvas.post(
                f"/courses/{course_id}/modules/{module['id']}/items",
                **{"module_item[title]": title,
                   "module_item[type]": "Quiz",
                   "module_item[content_id]": quiz_id,
                   "module_item[position]": position,
                   "module_item[indent]": 0,
                   "module_item[published]": "true"})
        except requests.HTTPError as exc:
            problems.append(f"{title}: could not add to module: {exc}")
        return


# ---------------------------------------------------------------------------
# Media links
# ---------------------------------------------------------------------------

FILEBASE = "$IMS-CC-FILEBASE$"
# Canvas rewrites the cartridge's file token in some attributes and not others.
# Measured on this instance after a clean import: <source src> and <track src>
# were rewritten to /courses/1/files/77/preview, and an <a href> was rewritten
# but made absolute. `poster` was left holding the raw token, because it is not
# on the importer's list of attributes to translate. So two things need fixing
# after every import, and neither is a defect in the cartridge.
ABSOLUTE_FILE_RE = re.compile(r'https?://[^/\s]+(/courses/\d+/files/\d+/[a-z_]+)')


MEDIA_FOLDER = "video"


def clear_media(canvas: Canvas, course_id: int, folder: str = MEDIA_FOLDER) -> int:
    """Remove the media folder before an import. Returns how many files went.

    Canvas does not replace a file on re-import. It renames the incoming one,
    so a second import of w5-concept.mp4 lands as w5-concept-1.mp4 and the page
    stays bound to the id it got the first time. The course then serves the
    FIRST cut of every video forever while each import reports success.
    Measured here: four copies of w5-concept.mp4 with four different hashes,
    the page pointing at the oldest, and 40 MB of orphans.

    Deleting file by file was not enough. Some come back on the next upload
    because Canvas matches an incoming name against a soft deleted attachment,
    so the whole folder goes instead, with force. It is scoped to the one
    folder this pipeline creates and owns.
    """
    folders = canvas.get(f"/courses/{course_id}/folders")
    doomed = [f for f in folders
              if f.get("name") == folder or (f.get("full_name") or "").endswith(f"/{folder}")]
    removed = 0
    for entry in doomed:
        removed += int(entry.get("files_count") or 0)
        response = canvas.session.delete(
            f"{canvas.url}/api/v1/folders/{entry['id']}", params={"force": "true"}, timeout=120)
        if not response.ok:
            raise ImportError_(
                f"Could not clear the {folder} folder (HTTP {response.status_code}).\n"
                f"  Without this the import duplicates every file and the pages keep "
                f"pointing at the previous version.")
    return removed


def _staged_assignments() -> dict[str, str]:
    """Staged assignment HTML keyed by title.

    Assignments are staged one per resource directory rather than in a single
    folder, and the title is the only stable key shared with the API, so it is
    read back out of the document Canvas was given.
    """
    staging = _staging_dir(ROOT)
    out: dict[str, str] = {}
    if not staging.exists():
        return out
    for path in staging.glob("*/*.html"):
        html = path.read_text(encoding="utf-8")
        match = re.search(r"<title>(.*?)</title>", html, re.S)
        if match:
            out[unescape(match.group(1)).strip()] = html
    return out


def _all_assignments(canvas: Canvas, course_id: int) -> list[dict]:
    """Every assignment, even when the list endpoint is refusing to serialize.

    One dangling file reference in one description makes Canvas raise while
    rewriting user content, and the whole /assignments list returns 500. That
    is exactly the state this function exists to repair, so it cannot depend on
    that endpoint. assignment_groups carries the same records by a different
    serializer and keeps working.
    """
    try:
        return canvas.get(f"/courses/{course_id}/assignments")
    except Exception:                                   # noqa: BLE001
        found: list[dict] = []
        for group in canvas.get(f"/courses/{course_id}/assignment_groups",
                                **{"include[]": "assignments"}):
            found.extend(group.get("assignments") or [])
        return found


def _staged_html() -> dict[str, str]:
    """The HTML the cartridge build produced, keyed by page slug.

    Used as a fallback source when Canvas cannot serialize a page. It is the
    same content the import uploaded, still carrying its $IMS-CC-FILEBASE$
    tokens, which repair() then resolves against the live files.
    """
    staging = _staging_dir(ROOT) / "wiki_content"
    if not staging.exists():
        return {}
    return {path.stem: path.read_text(encoding="utf-8") for path in staging.glob("*.html")}


def _reconcile_media(canvas: Canvas, course_id: int, problems: list[str]) -> dict[str, int]:
    """One file per name, and it is the one this build produced.

    Deleting the folder before an import is not enough. Canvas soft deletes the
    attachments and then restores them when an incoming file matches the name,
    so the course ends up holding two attachments called w5-concept.mp4: the
    original id carrying the FIRST cut, and a new id carrying the current one.
    The API lists both, and which one a page points at is luck.

    So the reconciliation happens here, against the artifacts on disk, which is
    the only source that knows what the current build actually is. For every
    name, the copy whose size matches the local file is kept and the rest are
    deleted. If none matches, that is reported rather than guessed at, because
    picking the newest would quietly serve a file nobody built.
    """
    from collections import defaultdict

    build = ROOT / "build" / "video"
    sizes: dict[str, int] = {}
    for artifact in build.iterdir() if build.exists() else []:
        if artifact.suffix == ".md" and artifact.name.endswith(".transcript.md"):
            continue        # shipped as .html, generated at cartridge time
        sizes[artifact.name] = artifact.stat().st_size

    groups: dict[str, list[dict]] = defaultdict(list)
    for f in canvas.get(f"/courses/{course_id}/files"):
        groups[f["display_name"]].append(f)

    keep: dict[str, int] = {}
    for name, entries in groups.items():
        if len(entries) == 1:
            keep[name] = entries[0]["id"]
            continue
        expected = sizes.get(name)
        match = [e for e in entries if expected is not None and e["size"] == expected]
        if not match:
            # Transcripts are generated during the cartridge build and have no
            # local twin to size check, so the newest is the right answer there.
            match = [max(entries, key=lambda e: e["id"])]
        chosen = max(match, key=lambda e: e["id"])
        keep[name] = chosen["id"]
        for stale in entries:
            if stale["id"] == chosen["id"]:
                continue
            response = canvas.session.delete(
                f"{canvas.url}/api/v1/files/{stale['id']}", params={"force": "true"}, timeout=60)
            if not response.ok:
                problems.append(f"could not remove the stale copy of {name} "
                                f"(id {stale['id']}, HTTP {response.status_code})")
    return keep


def fix_media_links(canvas: Canvas, course_id: int,
                    browse_url: str | None = None) -> list[str]:
    """Resolve leftover file tokens and make every media URL host relative.

    Two separate problems, one pass.

    The token: `poster` still says $IMS-CC-FILEBASE$/video/x.jpg after import,
    so the player shows a black rectangle before it is pressed.

    The absolute URL: Canvas rewrote the transcript link to
    http://localhost:3000/courses/1/files/78/preview. That is correct only for
    a browser on the machine running Canvas. Anyone opening the course from
    another computer, which is the normal case for a demo, gets a link pointing
    at their own machine. A root relative URL works from every host, so the
    stored HTML is normalised to one.
    """
    problems: list[str] = []
    # Reads can go anywhere. Writes have to go through the address a browser
    # uses, because that is the host Canvas stamps into the file links it
    # rewrites on save.
    browse = (browse_url or public_url() or canvas.url).rstrip("/")
    writer = canvas if browse == canvas.url else Canvas(browse, canvas.token)
    by_name = _reconcile_media(canvas, course_id, problems)
    id_to_name = {f["id"]: f["display_name"]
                  for f in canvas.get(f"/courses/{course_id}/files")}

    live = set(by_name.values())
    # Canvas keeps a soft deleted attachment addressable by id, so a page can
    # go on pointing at a copy that reconciliation removed. That is not a
    # cosmetic dangling link: Canvas rewrites file URLs when it serializes a
    # description, and on a dangling one Addressable raised "comparison of
    # Array with Array failed" and the whole /assignments endpoint returned
    # 500. One stale link took out the API for every assignment in the course.
    dangling = re.compile(rf"/courses/{course_id}/files/(\d+)/(\w+)(\?[^\"']*)?")

    def repair(html: str) -> str:
        for name, file_id in by_name.items():
            html = html.replace(f"{FILEBASE}/video/{name}",
                                f"/courses/{course_id}/files/{file_id}/preview")
        html = ABSOLUTE_FILE_RE.sub(r"\1", html)

        def repoint(match: re.Match) -> str:
            file_id, verb, query = int(match.group(1)), match.group(2), match.group(3) or ""
            if file_id in live:
                return match.group(0)
            # Map the dead id back by the name it had, minus any -N suffix
            # Canvas appended when it renamed rather than replaced.
            name = id_to_name.get(file_id, "")
            base = re.sub(r"-\d+(\.[^.]+(\.[^.]+)?)$", r"\1", name)
            target = by_name.get(base) or by_name.get(name)
            return (f"/courses/{course_id}/files/{target}/{verb}"
                    if target else match.group(0))

        return dangling.sub(repoint, html)

    staged = _staged_html()
    for page in canvas.get(f"/courses/{course_id}/pages"):
        # The repo is the source of truth. Where the cartridge staged HTML that
        # still carries media tokens, that HTML is used rather than whatever
        # Canvas made of it.
        #
        # Patching Canvas's own copy does not work. Its importer resolves
        # $IMS-CC-FILEBASE$ against a soft deleted attachment when the name
        # matches, so a fresh import produced a page pointing at file id 86,
        # deleted two imports ago. Repointing that by name is impossible from
        # the API, which lists live files only, so the dead id cannot even be
        # identified. Rebuilding from source sidesteps the whole problem.
        source = staged.get(page["url"], "")
        if FILEBASE in source:
            body = source
        else:
            try:
                body = canvas.get(f"/courses/{course_id}/pages/{page['url']}").get("body") or ""
            except Exception:                           # noqa: BLE001
            # Reading a page can fail for the very reason we are here to fix.
            # Canvas rewrites file URLs while serializing, and one dangling
            # reference makes that raise, so the page cannot be read in order
            # to be repaired. The cartridge staged the correct HTML for this
            # page, so rebuild from that instead of giving up.
                body = source
                if not body:
                    problems.append(f"page {page['url']} cannot be read and has no staged source")
                    continue
        fixed = repair(body)
        if fixed != body:
            response = writer.session.put(
                f"{writer.url}/api/v1/courses/{course_id}/pages/{page['url']}",
                data={"wiki_page[body]": fixed}, timeout=60)
            if not response.ok and response.status_code != 500:
                problems.append(f"could not update page {page['url']}: {response.status_code}")

    staged_work = _staged_assignments()
    for assignment in _all_assignments(canvas, course_id):
        source = staged_work.get(assignment.get("name", ""), "")
        body = source if FILEBASE in source else (assignment.get("description") or source)
        fixed = repair(body)
        if fixed != body:
            response = writer.session.put(
                f"{writer.url}/api/v1/courses/{course_id}/assignments/{assignment['id']}",
                data={"assignment[description]": fixed}, timeout=60)
            # A 500 here is Canvas failing to serialize its RESPONSE after a
            # successful write, which is the state we are repairing. The
            # verification pass below is what decides whether it worked.
            if not response.ok and response.status_code != 500:
                problems.append(f"could not update assignment {assignment['id']}: "
                                f"{response.status_code}")

    # A token left anywhere means a file the page references was never
    # uploaded, which is a broken player rather than a cosmetic problem.
    remaining = 0
    for page in canvas.get(f"/courses/{course_id}/pages"):
        try:
            remaining += (canvas.get(f"/courses/{course_id}/pages/{page['url']}")
                          .get("body") or "").count(FILEBASE)
        except Exception:                               # noqa: BLE001
            problems.append(f"page {page['url']} still will not serialize after repair")
    for assignment in _all_assignments(canvas, course_id):
        remaining += (assignment.get("description") or "").count(FILEBASE)
    if remaining:
        problems.append(f"{remaining} unresolved {FILEBASE} reference(s) remain. "
                        f"A page points at a media file that was never built.")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create the quizzes in Canvas over the API.")
    parser.add_argument("--course", type=int, default=1)
    parser.add_argument("--session", default="fall-flex-2")
    args = parser.parse_args(argv)

    try:
        url, token = credentials()
    except ImportError_ as exc:
        print(exc)
        return 2
    canvas = Canvas(url, token)

    print(f"Creating quizzes in course {args.course} at {url}")
    print("(The cartridge carries these too, but this Canvas has no QTI converter,")
    print(" so it drops every quiz on import without saying so. See the docstring.)\n")
    problems = sync_quizzes(canvas, args.course, args.session)

    if problems:
        print(f"\n{len(problems)} problem(s):\n")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\nAll quizzes are in Canvas, published, with the right point totals.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
