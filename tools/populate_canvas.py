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

import argparse
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

from tools.dates import DateMap
from tools.import_cartridge import Canvas, ImportError_, credentials

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

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

        # Canvas recomputes points_possible from the questions. Check it.
        after = canvas.get(f"/courses/{course_id}/quizzes/{quiz_id}")
        actual_points = float(after.get("points_possible") or 0)
        if abs(actual_points - float(row["points"])) > 0.01:
            problems.append(
                f"{title}: Canvas made it {actual_points:g} points, course.yaml "
                f"says {row['points']}")
        if after.get("question_count") != len(quiz["questions"]):
            problems.append(
                f"{title}: {after.get('question_count')} questions landed, "
                f"the file has {len(quiz['questions'])}")

        if not quiet:
            print(f"  {action:8} {title:58} "
                  f"{after.get('question_count')} items, {actual_points:g} points")

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
