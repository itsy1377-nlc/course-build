"""Build the Common Cartridge that carries the whole course.

    python -m tools.cartridge                 build build/itsy1377.imscc
    python -m tools.cartridge --check         validate everything, build nothing
    python -m tools.cartridge --out <path>    somewhere else

Why a cartridge rather than an API script. The brief asked for an API
population script, and the program approved the change to a cartridge, for two
reasons. It is how the institution actually moves a course, so the artifact a
reviewer sees is the artifact the college would use. And it carries modules,
pages, assignments, quizzes, rubrics, and outcomes in one pass, where the REST
API needs a different call for each and handles rubrics particularly badly:
create is an alias for update, validation failures come back as HTTP 200 with
an error body, and criteria have to be an index-keyed hash rather than a JSON
array, which is documented nowhere.

The API script still exists, at tools/populate_canvas.py, for fast incremental
edits while authoring. The cartridge is the deliverable.

Everything comes from content/course.yaml. Nothing about the course structure
is written down twice.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import yaml

from tools import qti
from tools.blocks import BlockError, render_document
from tools.dates import DateMap
from tools.qti import ident

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
BUILD = ROOT / "build"

CC_NS = "http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1"
CANVAS_NS = "http://canvas.instructure.com/xsd/cccv1p0"
CANVAS_SCHEMA = f"{CANVAS_NS} https://canvas.instructure.com/xsd/cccv1p0.xsd"

# The template marks every unfinished placeholder with this highlight colour.
# A build that still contains one is a build somebody forgot to finish.
PLACEHOLDER_MARKERS = ["#fbeeb8", "phpally-ignore", "[Insert ", "[List ", "[Briefly",
                       "TODO:", "TBD"]


class BuildError(Exception):
    pass


def load_course() -> dict[str, Any]:
    return yaml.safe_load((CONTENT / "course.yaml").read_text(encoding="utf-8"))


def _slug(ref: str) -> str:
    return ref.replace("_", "-").lower()


def _read_page(ref: str, kind: str) -> str:
    folder = {"page": "pages", "assignment": "assignments", "discussion": "discussions"}[kind]
    path = CONTENT / folder / f"{ref}.md"
    if not path.exists():
        raise BuildError(f"{kind} '{ref}' is in course.yaml but {path.relative_to(ROOT)} "
                         f"does not exist")
    return path.read_text(encoding="utf-8")


def _titles(course: dict) -> dict[str, str]:
    """Every ref's human title, from wherever course.yaml declares it."""
    titles: dict[str, str] = {}
    for group in ("assignments", "quizzes", "discussions"):
        for row in course.get(group, []):
            titles[row["ref"]] = row["title"]
    for module in course["modules"]:
        for item in module["items"]:
            titles.setdefault(item["ref"], _title_from_ref(item["ref"]))
    return titles


def _title_from_ref(ref: str) -> str:
    words = ref.replace("-", " ").split()
    fixed = {"w1": "Week 1", "w2": "Week 2", "w3": "Week 3", "w4": "Week 4",
             "w5": "Week 5", "w6": "Week 6", "w7": "Week 7", "ai": "AI", "qa": "Q and A",
             "kb": "Knowledge Base"}
    out = []
    for word in words:
        out.append(fixed.get(word, word.capitalize()))
    return " ".join(out)


# ---------------------------------------------------------------------------
# Checks that run before anything is written
# ---------------------------------------------------------------------------


def check(course: dict) -> list[str]:
    problems: list[str] = []
    titles = _titles(course)

    by_ref = {row["ref"]: row for group in ("assignments", "quizzes", "discussions")
              for row in course.get(group, [])}
    groups = {group["id"] for group in course["assignment_groups"]}

    # Weights have to add to 100, or Canvas silently scales them.
    total_weight = sum(group["weight"] for group in course["assignment_groups"])
    if total_weight != 100:
        problems.append(f"assignment group weights add to {total_weight}, not 100")

    # Points inside a group have to be proportional to the intended weight,
    # because Canvas computes a group score as earned over possible.
    for group in course["assignment_groups"]:
        members = [r for r in by_ref.values()
                   if r.get("group") == group["id"] and not r.get("omit_from_final_grade")]
        points = sum(r.get("points", 0) for r in members)
        if points and points != group["weight"] * 10:
            problems.append(
                f"group '{group['id']}' is weighted {group['weight']}% and its items "
                f"add to {points} points. The convention here is weight times ten, "
                f"so that should be {group['weight'] * 10}.")

    # Every module item has to resolve to something on disk.
    for module in course["modules"]:
        for item in module["items"]:
            ref, kind = item["ref"], item["type"]
            if kind in ("page", "discussion"):
                if not (CONTENT / ("pages" if kind == "page" else "discussions") /
                        f"{ref}.md").exists():
                    problems.append(f"{module['id']}: {kind} '{ref}' has no markdown file")
            elif kind == "assignment":
                if not (CONTENT / "assignments" / f"{ref}.md").exists():
                    problems.append(f"{module['id']}: assignment '{ref}' has no markdown file")
                if ref not in by_ref:
                    problems.append(f"{module['id']}: assignment '{ref}' is not declared "
                                    f"in the assignments list")
            elif kind == "quiz":
                if not (CONTENT / "quizzes" / f"{ref}.yaml").exists():
                    problems.append(f"{module['id']}: quiz '{ref}' has no YAML file")
                if ref not in by_ref:
                    problems.append(f"{module['id']}: quiz '{ref}' is not declared in the "
                                    f"quizzes list")

    for ref, row in by_ref.items():
        if row.get("group") and row["group"] not in groups:
            problems.append(f"{ref}: assignment group '{row['group']}' does not exist")
        if row.get("rubric") and not (CONTENT / "rubrics" / f"{row['rubric']}.yaml").exists():
            problems.append(f"{ref}: rubric '{row['rubric']}' has no YAML file")

    # Quizzes: points, outcome tags, feedback, question shapes.
    for row in course.get("quizzes", []):
        path = CONTENT / "quizzes" / f"{row['ref']}.yaml"
        if not path.exists():
            continue
        quiz = yaml.safe_load(path.read_text(encoding="utf-8"))
        problems.extend(qti.validate(quiz, row["ref"], row["points"]))

    # Rubrics: points have to add up to the assignment they are attached to.
    for path in sorted((CONTENT / "rubrics").glob("*.yaml")):
        rubric = yaml.safe_load(path.read_text(encoding="utf-8"))
        total = sum(c["points"] for c in rubric["criteria"])
        if total != rubric["points"]:
            problems.append(f"rubric {rubric['ref']}: criteria add to {total}, "
                            f"declared {rubric['points']}")

    # Every page has to render, and none may still contain a placeholder.
    for folder, kind in (("pages", "page"), ("assignments", "assignment"),
                         ("discussions", "discussion")):
        for path in sorted((CONTENT / folder).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            try:
                html = render_document(text, titles.get(path.stem, path.stem), str(path))
            except BlockError as exc:
                problems.append(str(exc))
                continue
            for marker in PLACEHOLDER_MARKERS:
                if marker in html:
                    problems.append(f"{path.relative_to(ROOT)} still contains a "
                                    f"placeholder: {marker!r}")
    return problems


# ---------------------------------------------------------------------------
# The cartridge
# ---------------------------------------------------------------------------


def _xml(tag: str, value: Any) -> str:
    if value is None or value == "":
        return f"    <{tag}/>\n"
    if isinstance(value, bool):
        value = "true" if value else "false"
    return f"    <{tag}>{escape(str(value))}</{tag}>\n"


def build(out_path: Path, session: str = "fall-flex-2", quiet: bool = False) -> Path:
    course = load_course()
    problems = check(course)
    if problems:
        raise BuildError("\n".join(["The course does not validate:"] +
                                   [f"  - {p}" for p in problems]))

    dates = DateMap(session)
    titles = _titles(course)
    staging = BUILD / "cartridge"
    if staging.exists():
        shutil.rmtree(staging)
    (staging / "course_settings").mkdir(parents=True)
    (staging / "wiki_content").mkdir()
    (staging / "non_cc_assessments").mkdir()

    resources: list[str] = []
    organizations: list[str] = []

    by_ref = {row["ref"]: row for group in ("assignments", "quizzes", "discussions")
              for row in course.get(group, [])}

    course_id = ident("course", course["course"]["code"])

    # -- pages, assignments, discussions, quizzes -------------------------
    for module in course["modules"]:
        items_xml = []
        for position, item in enumerate(module["items"], start=1):
            ref, kind = item["ref"], item["type"]
            title = titles.get(ref, _title_from_ref(ref))
            rid = ident(kind, ref)

            if kind == "page":
                slug = _slug(ref)
                html = render_document(_read_page(ref, "page"), title,
                                       f"content/pages/{ref}.md")
                (staging / "wiki_content" / f"{slug}.html").write_text(
                    _page_document(html, title, rid), encoding="utf-8")
                resources.append(
                    f'    <resource identifier="{rid}" type="webcontent" '
                    f'href="wiki_content/{slug}.html">\n'
                    f'      <file href="wiki_content/{slug}.html"/>\n'
                    f'    </resource>\n')
                content_type = "WikiPage"

            elif kind == "assignment":
                row = by_ref[ref]
                folder = staging / rid
                folder.mkdir()
                slug = _slug(ref)
                html = render_document(
                    _with_rubric(_read_page(ref, "assignment"), row, course),
                    title, f"content/assignments/{ref}.md")
                (folder / f"{slug}.html").write_text(
                    _page_document(html, title, rid), encoding="utf-8")
                (folder / "assignment_settings.xml").write_text(
                    _assignment_settings(rid, row, title, slug, dates, position),
                    encoding="utf-8")
                resources.append(
                    f'    <resource identifier="{rid}" '
                    f'type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
                    f'href="{rid}/{slug}.html">\n'
                    f'      <file href="{rid}/{slug}.html"/>\n'
                    f'      <file href="{rid}/assignment_settings.xml"/>\n'
                    f'    </resource>\n')
                content_type = "Assignment"

            elif kind == "quiz":
                row = by_ref[ref]
                quiz = yaml.safe_load(
                    (CONTENT / "quizzes" / f"{ref}.yaml").read_text(encoding="utf-8"))
                folder = staging / rid
                folder.mkdir()
                # Canvas dialect.
                (folder / "assessment_qti.xml").write_text(
                    qti.assessment(quiz, ref, canvas_dialect=True), encoding="utf-8")
                (folder / "assessment_meta.xml").write_text(
                    _quiz_meta(rid, quiz, row, title, dates), encoding="utf-8")
                # The same quiz in the Common Cartridge profile dialect as well.
                # The NLC template carries both, and a cartridge with only one
                # imports somewhere and not somewhere else.
                #
                # Three details here are load-bearing, and getting any of them
                # wrong makes Canvas report a completed import that contains no
                # quizzes at all, with no error anywhere. Found by reading the
                # course back rather than by trusting the word "completed".
                #
                #   1. The assessment resource carries NO href attribute. Only
                #      a <file> and a <dependency>.
                #   2. The profile copy is named after the quiz's own resource
                #      id, not an id of its own.
                #   3. The meta resource has a DIFFERENT identifier, and it is
                #      the one the assessment depends on.
                meta_id = ident("quiz-meta", ref)
                (staging / "non_cc_assessments" / f"{rid}.xml.qti").write_text(
                    qti.assessment(quiz, ref, canvas_dialect=False), encoding="utf-8")
                resources.append(
                    f'    <resource identifier="{rid}" '
                    f'type="imsqti_xmlv1p2/imscc_xmlv1p1/assessment">\n'
                    f'      <file href="{rid}/assessment_qti.xml"/>\n'
                    f'      <dependency identifierref="{meta_id}"/>\n'
                    f'    </resource>\n'
                    f'    <resource identifier="{meta_id}" '
                    f'type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
                    f'href="{rid}/assessment_meta.xml">\n'
                    f'      <file href="{rid}/assessment_meta.xml"/>\n'
                    f'      <file href="non_cc_assessments/{rid}.xml.qti"/>\n'
                    f'    </resource>\n')
                content_type = "Quiz"

            elif kind == "discussion":
                row = by_ref.get(ref, {})
                slug = _slug(ref)
                html = render_document(_read_page(ref, "discussion"), title,
                                       f"content/discussions/{ref}.md")
                (staging / f"{rid}.xml").write_text(
                    _discussion_topic(rid, title, html), encoding="utf-8")
                (staging / f"{rid}-meta.xml").write_text(
                    _discussion_meta(rid, row, title, dates), encoding="utf-8")
                resources.append(
                    f'    <resource identifier="{rid}" '
                    f'type="imsdt_xmlv1p1" href="{rid}.xml">\n'
                    f'      <file href="{rid}.xml"/>\n'
                    f'      <dependency identifierref="{rid}-meta"/>\n'
                    f'    </resource>\n'
                    f'    <resource identifier="{rid}-meta" '
                    f'type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
                    f'href="{rid}-meta.xml">\n'
                    f'      <file href="{rid}-meta.xml"/>\n'
                    f'    </resource>\n')
                content_type = "DiscussionTopic"
            else:
                raise BuildError(f"unknown item type {kind!r} in {module['id']}")

            items_xml.append((ident("item", module["id"], ref), content_type, title,
                              rid, position))

        organizations.append(_organization_module(module, items_xml))

    # -- course settings ---------------------------------------------------
    settings = staging / "course_settings"
    settings.write_bytes(b"") if False else None
    (settings / "course_settings.xml").write_text(
        _course_settings(course, course_id, dates), encoding="utf-8")
    (settings / "module_meta.xml").write_text(
        _module_meta(course, by_ref, titles), encoding="utf-8")
    (settings / "assignment_groups.xml").write_text(
        _assignment_groups(course), encoding="utf-8")
    (settings / "learning_outcomes.xml").write_text(
        _learning_outcomes(course), encoding="utf-8")
    (settings / "rubrics.xml").write_text(_rubrics(course), encoding="utf-8")
    (settings / "files_meta.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<fileMeta xmlns="{CANVAS_NS}"/>\n', encoding="utf-8")
    (settings / "media_tracks.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<media_tracks xmlns="{CANVAS_NS}"/>\n', encoding="utf-8")
    (settings / "context.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<context_info xmlns="{CANVAS_NS}">\n'
        f'  <course_id>{course_id}</course_id>\n'
        f'  <course_name>{escape(course["course"]["title"])}</course_name>\n'
        f'</context_info>\n', encoding="utf-8")
    (settings / "canvas_export.txt").write_text(
        "Q: Why does this file exist?\n"
        "A: Canvas uses it to recognise its own cartridges on import.\n",
        encoding="utf-8")
    (settings / "syllabus.html").write_text(
        _page_document(_syllabus(course, dates), "Syllabus", ident("syllabus", "itsy1377")),
        encoding="utf-8")

    resources.append(
        f'    <resource identifier="{course_id}_syllabus" '
        f'type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
        f'href="course_settings/syllabus.html" intendeduse="syllabus">\n'
        f'      <file href="course_settings/syllabus.html"/>\n'
        f'    </resource>\n'
        f'    <resource identifier="{course_id}" '
        f'type="associatedcontent/imscc_xmlv1p1/learning-application-resource" '
        f'href="course_settings/canvas_export.txt">\n'
        + "".join(f'      <file href="course_settings/{name}"/>\n' for name in
                  ("course_settings.xml", "module_meta.xml", "assignment_groups.xml",
                   "learning_outcomes.xml", "rubrics.xml", "files_meta.xml",
                   "media_tracks.xml", "context.xml", "canvas_export.txt"))
        + '    </resource>\n')

    (staging / "imsmanifest.xml").write_text(
        _manifest(course, course_id, organizations, resources), encoding="utf-8")

    # -- zip ---------------------------------------------------------------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        out_path.unlink()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(staging).as_posix())

    if not quiet:
        counts: dict[str, int] = {}
        for module in course["modules"]:
            for item in module["items"]:
                counts[item["type"]] = counts.get(item["type"], 0) + 1
        size = out_path.stat().st_size / 1024
        print(f"Built {out_path.relative_to(ROOT)}  ({size:.0f} KB)")
        print(f"  modules      {len(course['modules'])}")
        for kind in sorted(counts):
            print(f"  {(kind + chr(115) if not kind.endswith(chr(122)) else kind + chr(101) + chr(115)):13}{counts[kind]}")
        print(f"  rubrics      {len(list((CONTENT / 'rubrics').glob('*.yaml')))}")
        print(f"  outcomes     {len(course['outcomes'])}")
        print(f"  session      {session} ({dates.describe()})")
    return out_path


# ---------------------------------------------------------------------------
# XML fragments
# ---------------------------------------------------------------------------


def _page_document(inner_html: str, title: str, identifier: str) -> str:
    return inner_html.replace(
        "<head>\n", f'<head>\n<meta name="identifier" content="{identifier}"/>\n', 1)


def _with_rubric(markdown_text: str, row: dict, course: dict) -> str:
    """Put the rubric table into the assignment description as well.

    Not redundancy for its own sake. It puts the criteria in front of the
    student without a second click, and it means the criteria survive whichever
    import path the course takes.
    """
    ref = row.get("rubric")
    if not ref:
        return markdown_text
    rubric = yaml.safe_load((CONTENT / "rubrics" / f"{ref}.yaml").read_text(encoding="utf-8"))
    lines = ["", "::: grading | How this is scored",
             f"The rubric below is attached to this assignment in Canvas as well. "
             f"It totals {rubric['points']} points.", "",
             "| Criterion | Points | What full credit looks like |", "|---|---|---|"]
    for criterion in rubric["criteria"]:
        best = max(criterion["ratings"], key=lambda r: r["points"])
        lines.append(f"| {criterion['description']} | {criterion['points']} | "
                     f"{best.get('long_description') or best['description']} |")
    lines.append(":::")
    return markdown_text.rstrip() + "\n" + "\n".join(lines) + "\n"


def _assignment_settings(rid: str, row: dict, title: str, slug: str,
                         dates: DateMap, position: int) -> str:
    due = dates.at(row["due_day"]) if row.get("due_day") else None
    body = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<assignment identifier="{rid}" xmlns="{CANVAS_NS}" '
        f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n'
    )
    body += _xml("title", title)
    body += _xml("due_at", due)
    body += _xml("lock_at", None)
    body += _xml("unlock_at", None)
    body += _xml("module_locked", False)
    body += _xml("assignment_group_identifierref", ident("group", row["group"]))
    body += _xml("workflow_state", "published")
    body += "    <assignment_overrides>\n    </assignment_overrides>\n"
    body += _xml("allowed_extensions", "")
    body += _xml("has_group_category", False)
    body += _xml("points_possible", f'{float(row["points"]):.1f}')
    body += _xml("grading_type", row.get("grading_type", "points"))
    body += _xml("all_day", False)
    body += _xml("submission_types", ",".join(row.get("submission_types", ["online_upload"])))
    body += _xml("position", position)
    body += _xml("omit_from_final_grade", row.get("omit_from_final_grade", False))
    for flag in ("turnitin_enabled", "vericite_enabled", "peer_reviews",
                 "automatic_peer_reviews", "anonymous_peer_reviews",
                 "grade_group_students_individually", "freeze_on_copy",
                 "hide_in_gradebook", "intra_group_peer_reviews",
                 "only_visible_to_overrides", "post_to_sis", "moderated_grading",
                 "anonymous_grading", "graders_anonymous_to_graders",
                 "anonymous_instructor_annotations"):
        body += _xml(flag, False)
    body += _xml("peer_review_count", 0)
    body += _xml("grader_count", 0)
    body += _xml("grader_comments_visible_to_graders", True)
    body += _xml("grader_names_visible_to_final_grader", True)
    if row.get("rubric"):
        body += _xml("rubric_identifierref", ident("rubric", row["rubric"]))
        body += _xml("rubric_use_for_grading", True)
        body += _xml("rubric_hide_score_total", False)
    body += "    <post_policy>\n      <post_manually>false</post_manually>\n    </post_policy>\n"
    body += "</assignment>\n"
    return body


def _quiz_meta(rid: str, quiz: dict, row: dict, title: str, dates: DateMap) -> str:
    attempts = row.get("allowed_attempts", 1)
    body = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<quiz identifier="{rid}" xmlns="{CANVAS_NS}" '
        f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n'
    )
    body += _xml("title", title)
    body += _xml("description", quiz.get("description", ""))
    body += _xml("shuffle_answers", row.get("shuffle_answers",
                                            quiz.get("shuffle_answers", False)))
    body += _xml("scoring_policy", row.get("scoring_policy", "keep_highest"))
    body += _xml("hide_results", "")
    body += _xml("quiz_type", "assignment")
    body += _xml("points_possible", f'{float(row["points"]):.1f}')
    body += _xml("allowed_attempts", attempts)
    body += _xml("assignment_group_identifierref", ident("group", row["group"]))
    body += _xml("available", True)
    body += _xml("published", True)
    body += _xml("one_question_at_a_time", False)
    body += _xml("cant_go_back", False)
    body += _xml("show_correct_answers", True)
    if row.get("time_limit_minutes"):
        body += _xml("time_limit", row["time_limit_minutes"])
    if row.get("due_day"):
        body += _xml("due_at", dates.at(row["due_day"]))
    if row.get("unlock_day"):
        body += _xml("unlock_at", dates.at(row["unlock_day"], hour=0, minute=1))
    for flag in ("require_lockdown_browser", "require_lockdown_browser_for_results",
                 "require_lockdown_browser_monitor", "anonymous_submissions",
                 "could_be_locked", "only_visible_to_overrides", "omit_from_final_grade"):
        body += _xml(flag, False)
    body += "</quiz>\n"
    return body


def _discussion_topic(rid: str, title: str, html: str) -> str:
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<topic xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
            f'  <title>{escape(title)}</title>\n'
            f'  <text texttype="text/html">{escape(html)}</text>\n'
            f'</topic>\n')


def _discussion_meta(rid: str, row: dict, title: str, dates: DateMap) -> str:
    body = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<topicMeta identifier="{rid}-meta" xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n')
    body += _xml("topic_id", rid)
    body += _xml("title", title)
    body += _xml("posted_at", None)
    body += _xml("discussion_type", "threaded" if row.get("threaded") else "side_comment")
    body += _xml("pinned", row.get("pinned", False))
    body += _xml("workflow_state", "active")
    body += _xml("type", "topic")
    if row.get("graded"):
        body += (f'    <assignment identifier="{ident("discussion-assignment", rid)}">\n'
                 f'      <title>{escape(title)}</title>\n'
                 f'      <points_possible>{float(row.get("points", 1)):.1f}</points_possible>\n'
                 f'      <grading_type>points</grading_type>\n'
                 f'      <workflow_state>published</workflow_state>\n'
                 f'      <submission_types>discussion_topic</submission_types>\n'
                 f'      <omit_from_final_grade>'
                 f'{str(row.get("omit_from_final_grade", False)).lower()}'
                 f'</omit_from_final_grade>\n'
                 + (f'      <due_at>{dates.at(row["due_day"])}</due_at>\n'
                    if row.get("due_day") else "")
                 + f'    </assignment>\n')
    body += "</topicMeta>\n"
    return body


def _organization_module(module: dict, items: list[tuple]) -> str:
    rows = "".join(
        f'          <item identifier="{item_id}" identifierref="{rid}">\n'
        f'            <title>{escape(title)}</title>\n'
        f'          </item>\n'
        for item_id, _kind, title, rid, _position in items
    )
    return (f'        <item identifier="{ident("module", module["id"])}">\n'
            f'          <title>{escape(module["title"])}</title>\n'
            f'{rows}        </item>\n')


def _module_meta(course: dict, by_ref: dict, titles: dict) -> str:
    modules = []
    for position, module in enumerate(course["modules"], start=1):
        items = []
        for item_position, item in enumerate(module["items"], start=1):
            ref, kind = item["ref"], item["type"]
            content_type = {"page": "WikiPage", "assignment": "Assignment",
                            "quiz": "Quiz", "discussion": "DiscussionTopic"}[kind]
            items.append(
                f'      <item identifier="{ident("item", module["id"], ref)}">\n'
                f'        <content_type>{content_type}</content_type>\n'
                f'        <workflow_state>active</workflow_state>\n'
                f'        <title>{escape(titles.get(ref, _title_from_ref(ref)))}</title>\n'
                f'        <identifierref>{ident(kind, ref)}</identifierref>\n'
                f'        <position>{item_position}</position>\n'
                f'        <new_tab/>\n'
                f'        <indent>0</indent>\n'
                f'      </item>\n')
        state = "active" if module.get("published", True) else "unpublished"
        modules.append(
            f'  <module identifier="{ident("module", module["id"])}">\n'
            f'    <title>{escape(module["title"])}</title>\n'
            f'    <workflow_state>{state}</workflow_state>\n'
            f'    <position>{position}</position>\n'
            f'    <require_sequential_progress>false</require_sequential_progress>\n'
            f'    <locked>false</locked>\n'
            f'    <items>\n{"".join(items)}    </items>\n'
            f'  </module>\n')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<modules xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n{"".join(modules)}</modules>\n')


def _assignment_groups(course: dict) -> str:
    groups = "".join(
        f'  <assignmentGroup identifier="{ident("group", group["id"])}">\n'
        f'    <title>{escape(group["title"])}</title>\n'
        f'    <position>{position}</position>\n'
        f'    <group_weight>{float(group["weight"]):.1f}</group_weight>\n'
        f'  </assignmentGroup>\n'
        for position, group in enumerate(course["assignment_groups"], start=1)
    )
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<assignmentGroups xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n{groups}</assignmentGroups>\n')


def _learning_outcomes(course: dict) -> str:
    outcomes = "".join(
        f'  <learningOutcome identifier="{ident("outcome", o["id"])}">\n'
        f'    <title>{escape(o["id"])}</title>\n'
        f'    <description>{escape(" ".join(o["text"].split()))}</description>\n'
        f'    <calculation_method>decaying_average</calculation_method>\n'
        f'    <calculation_int>65</calculation_int>\n'
        f'    <mastery_points>3.0</mastery_points>\n'
        f'    <ratings>\n'
        f'      <rating><description>Meets</description><points>3.0</points></rating>\n'
        f'      <rating><description>Approaching</description><points>2.0</points></rating>\n'
        f'      <rating><description>Does not meet</description><points>0.0</points></rating>\n'
        f'    </ratings>\n'
        f'  </learningOutcome>\n'
        for o in course["outcomes"]
    )
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<learningOutcomes xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n{outcomes}</learningOutcomes>\n')


def _rubrics(course: dict) -> str:
    entries = []
    for path in sorted((CONTENT / "rubrics").glob("*.yaml")):
        rubric = yaml.safe_load(path.read_text(encoding="utf-8"))
        criteria = []
        for position, criterion in enumerate(rubric["criteria"], start=1):
            ratings = "".join(
                f'        <rating>\n'
                f'          <description>{escape(r["description"])}</description>\n'
                f'          <long_description>'
                f'{escape(r.get("long_description", ""))}</long_description>\n'
                f'          <points>{float(r["points"]):.1f}</points>\n'
                f'          <criterion_id>{ident("criterion", rubric["ref"], str(position))}</criterion_id>\n'
                f'          <id>{ident("rating", rubric["ref"], str(position), r["description"])}</id>\n'
                f'        </rating>\n'
                for r in criterion["ratings"]
            )
            criteria.append(
                f'      <criterion>\n'
                f'        <criterion_id>{ident("criterion", rubric["ref"], str(position))}</criterion_id>\n'
                f'        <description>{escape(criterion["description"])}</description>\n'
                f'        <long_description>'
                f'{escape(" ".join(criterion.get("long_description", "").split()))}'
                f'</long_description>\n'
                f'        <points>{float(criterion["points"]):.1f}</points>\n'
                f'        <criterion_use_range>false</criterion_use_range>\n'
                f'        <ratings>\n{ratings}        </ratings>\n'
                f'      </criterion>\n')
        entries.append(
            f'  <rubric identifier="{ident("rubric", rubric["ref"])}">\n'
            f'    <title>{escape(rubric["title"])}</title>\n'
            f'    <points_possible>{float(rubric["points"]):.1f}</points_possible>\n'
            f'    <reusable>false</reusable>\n'
            f'    <public>false</public>\n'
            f'    <read_only>false</read_only>\n'
            f'    <free_form_criterion_comments>'
            f'{str(rubric.get("free_form_comments", True)).lower()}'
            f'</free_form_criterion_comments>\n'
            f'    <hide_score_total>false</hide_score_total>\n'
            f'    <criteria>\n{"".join(criteria)}    </criteria>\n'
            f'  </rubric>\n')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<rubrics xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n{"".join(entries)}</rubrics>\n')


def _course_settings(course: dict, course_id: str, dates: DateMap) -> str:
    meta = course["course"]
    body = (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<course identifier="{course_id}" xmlns="{CANVAS_NS}" '
            f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xsi:schemaLocation="{CANVAS_SCHEMA}">\n')
    body += _xml("title", f'{meta["code"]}: {meta["title"]}')
    body += _xml("course_code", meta["code"])
    body += _xml("start_at", dates.at(1, hour=0, minute=1))
    body += _xml("conclude_at", dates.at(55, hour=23, minute=59))
    body += _xml("time_zone", meta["timezone"])
    # The template ships two groups at weight 0.0, so weighting is not
    # inherited and has to be turned on explicitly.
    body += _xml("group_weighting_scheme", "percent")
    body += _xml("default_view", "modules")
    body += _xml("license", "cc_by")
    body += _xml("is_public", False)
    body += _xml("is_public_to_auth_users", False)
    body += _xml("public_syllabus", False)
    body += _xml("indexed", False)
    body += _xml("hide_final_grade", False)
    body += _xml("hide_distribution_graphs", True)
    body += _xml("allow_student_wiki_edits", False)
    body += _xml("allow_student_discussion_topics", True)
    body += _xml("allow_student_forum_attachments", True)
    body += _xml("open_enrollment", False)
    body += _xml("self_enrollment", False)
    body += _xml("syllabus_course_summary", True)
    body += _xml("show_total_grade_as_points", False)
    body += _xml("default_wiki_editing_roles", "teachers")
    body += _xml("grading_standard_enabled", False)
    body += "</course>\n"
    return body


def _syllabus(course: dict, dates: DateMap) -> str:
    meta = course["course"]
    outcomes = "\n".join(f"| **{o['id']}** | {' '.join(o['text'].split())} |"
                         for o in course["outcomes"])
    weights = "\n".join(f"| {g['title']} | {g['weight']}% |"
                        for g in course["assignment_groups"])

    rows = []
    for group in ("assignments", "quizzes", "discussions"):
        for row in course.get(group, []):
            if row.get("omit_from_final_grade") or not row.get("due_day"):
                continue
            rows.append((row["due_day"], row["title"], row.get("points", 0)))
    schedule = "\n".join(f"| Day {day} | {title} | {points} |"
                         for day, title, points in sorted(rows))

    markdown = f"""::: intro
{meta['code']}: {meta['title']}. {meta['credit_hours']} credit hours,
{meta['contact_hours']} contact hours. {meta['session']}, {meta['modality']}.
{meta['institution']}, {meta['district']}.
:::

::: section | What you will be able to do
| | |
|---|---|
{outcomes}
:::

::: section | How the grade is put together
| Part of the course | Share of the grade |
|---|---|
{weights}

Most of the grade is scored automatically, and you can run the same checks
yourself as many times as you like before a deadline.
:::

::: callout stop | The one rule
You may only attack the lab target on your own computer, your own copy of the
agent, and a model running on your own machine. Nothing else, ever.

Read the Rules of Engagement page in full. You have to pass a quiz on it before
Week 2 opens, and it is referenced in every attack lab.
:::

::: section | What is due, and when
Deadlines are {meta['deadline_time']} in the {meta['timezone'].split('/')[-1].replace('_', ' ')} time zone.

| Due | What | Points |
|---|---|---|
{schedule}
:::

::: section | Materials
There is no textbook to buy. Everything is instructor-authored or openly
licensed. See the Course Material page for the full list with licenses.
:::
"""
    return render_document(markdown, "Syllabus", "syllabus")


def _manifest(course: dict, course_id: str, organizations: list[str],
              resources: list[str]) -> str:
    meta = course["course"]
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<manifest identifier="{ident("manifest", meta["code"])}" xmlns="{CC_NS}" '
        f'xmlns:lom="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource" '
        f'xmlns:lomimscc="http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest" '
        f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:schemaLocation="{CC_NS} '
        f'http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd '
        f'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource '
        f'http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd '
        f'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/manifest '
        f'http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lommanifest_v1p0.xsd">\n'
        f'  <metadata>\n'
        f'    <schema>IMS Common Cartridge</schema>\n'
        f'    <schemaversion>1.1.0</schemaversion>\n'
        f'    <lomimscc:lom>\n'
        f'      <lomimscc:general>\n'
        f'        <lomimscc:title>\n'
        f'          <lomimscc:string>{escape(meta["code"])}: '
        f'{escape(meta["title"])}</lomimscc:string>\n'
        f'        </lomimscc:title>\n'
        f'      </lomimscc:general>\n'
        f'      <lomimscc:rights>\n'
        f'        <lomimscc:copyrightAndOtherRestrictions>\n'
        f'          <lomimscc:value>yes</lomimscc:value>\n'
        f'        </lomimscc:copyrightAndOtherRestrictions>\n'
        f'        <lomimscc:description>\n'
        f'          <lomimscc:string>CC Attribution 4.0 - '
        f'https://creativecommons.org/licenses/by/4.0/</lomimscc:string>\n'
        f'        </lomimscc:description>\n'
        f'      </lomimscc:rights>\n'
        f'    </lomimscc:lom>\n'
        f'  </metadata>\n'
        f'  <organizations>\n'
        f'    <organization identifier="org_1" structure="rooted-hierarchy">\n'
        f'      <item identifier="LearningModules">\n'
        f'{"".join(organizations)}'
        f'      </item>\n'
        f'    </organization>\n'
        f'  </organizations>\n'
        f'  <resources>\n{"".join(resources)}  </resources>\n'
        f'</manifest>\n'
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the ITSY 1377 Common Cartridge.")
    parser.add_argument("--out", default=str(BUILD / "itsy1377.imscc"))
    parser.add_argument("--session", default="fall-flex-2",
                        help="Which Flex session to date this build for.")
    parser.add_argument("--check", action="store_true",
                        help="Validate everything and build nothing.")
    args = parser.parse_args(argv)

    course = load_course()
    problems = check(course)
    if problems:
        print("The course does not validate:\n")
        for problem in problems:
            print(f"  - {problem}")
        print()
        return 1
    if args.check:
        print("Everything validates. Nothing was built.")
        return 0

    try:
        build(Path(args.out), session=args.session)
    except BuildError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
