"""Turn authored quiz YAML into QTI that Canvas will import.

Two things about this file are worth knowing before you change it.

**Classic Quizzes only.** New Quizzes has a fully documented API at
`/api/quiz/v1/`, and there is no such route anywhere in the open-source Canvas
code, because it is served by Instructure's separate hosted service. Two GitHub
issues asking whether it will be open-sourced have been open since 2020 and
2021 with no official answer. So a cartridge that has to import into a local
Canvas carries Classic Quizzes, and that decision is not reversible from here.

**Two dialects, on purpose.** The NLC template's own cartridge carries every
quiz twice: once as a Common Cartridge profile assessment under
`non_cc_assessments/`, and once in Canvas's own richer dialect. A generator
that emits only one of them produces a cartridge that imports somewhere and not
somewhere else. This emits both.

The question types below go beyond what the NLC template demonstrates. The
template's quizzes use only multiple choice, true or false, and essay, so
multiple answers, short answer, and numerical items here were written from the
QTI specification rather than adapted from a working example. They import
correctly in the local Canvas this was tested against; verify them once against
the college's Canvas before a term depends on them.
"""

from __future__ import annotations

import hashlib
from xml.sax.saxutils import escape

QTI_NS = "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
QTI_SCHEMA = ("http://www.imsglobal.org/xsd/ims_qtiasiv1p2 "
              "http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_qtiasiv1p2p1_v1p0.xsd")

CANVAS_TYPE = {
    "multiple_choice": "multiple_choice_question",
    "true_false": "true_false_question",
    "multiple_answers": "multiple_answers_question",
    "short_answer": "short_answer_question",
    "numerical": "numerical_question",
    "essay": "essay_question",
}


def ident(*parts: str) -> str:
    """A stable identifier. Same input, same id, every rebuild.

    Canvas matches content on re-import by identifier, so these must not move
    between builds or a second import creates duplicates instead of updates.
    """
    return "g" + hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()


def _html(text: str) -> str:
    """Wrap plain text as the HTML fragment QTI expects, escaped once."""
    import markdown as markdown_lib
    rendered = markdown_lib.markdown(str(text or "").strip(),
                                     extensions=["fenced_code", "tables", "sane_lists"])
    return escape(rendered)


def _mattext(text: str, indent: str) -> str:
    return (f'{indent}<material>\n'
            f'{indent}  <mattext texttype="text/html">{_html(text)}</mattext>\n'
            f'{indent}</material>')


def _feedback(fid: str, text: str) -> str:
    if not text:
        return ""
    return (f'      <itemfeedback ident="{fid}">\n'
            f'        <flow_mat>\n{_mattext(text, "          ")}\n        </flow_mat>\n'
            f'      </itemfeedback>\n')


def _metadata(question: dict, ref: str) -> str:
    fields = [
        ("question_type", CANVAS_TYPE[question["type"]]),
        ("points_possible", f'{float(question.get("points", 1)):.1f}'),
        ("assessment_question_identifierref", ident("bank", ref, question["id"])),
    ]
    if question["type"] in ("multiple_choice", "true_false", "multiple_answers"):
        fields.append(("original_answer_ids",
                       ",".join(str(i + 1) for i in range(len(question.get("answers", []))))))
    rows = "".join(
        f'        <qtimetadatafield>\n'
        f'          <fieldlabel>{label}</fieldlabel>\n'
        f'          <fieldentry>{escape(str(value))}</fieldentry>\n'
        f'        </qtimetadatafield>\n'
        for label, value in fields
    )
    return f'      <itemmetadata>\n      <qtimetadata>\n{rows}      </qtimetadata>\n      </itemmetadata>\n'


# ---------------------------------------------------------------------------
# One item per question type
# ---------------------------------------------------------------------------


def _choice_item(question: dict, ref: str, multiple: bool) -> str:
    answers = question.get("answers", [])
    cardinality = "Multiple" if multiple else "Single"

    labels = "".join(
        f'          <response_label ident="{index + 1}">\n'
        f'{_mattext(answer["text"], "            ")}\n'
        f'          </response_label>\n'
        for index, answer in enumerate(answers)
    )

    conditions = [
        '        <respcondition continue="Yes">\n'
        '          <conditionvar><other/></conditionvar>\n'
        '          <displayfeedback feedbacktype="Response" linkrefid="general_fb"/>\n'
        '        </respcondition>\n'
    ]
    for index, answer in enumerate(answers):
        if answer.get("feedback"):
            conditions.append(
                f'        <respcondition continue="Yes">\n'
                f'          <conditionvar><varequal respident="response1">{index + 1}</varequal></conditionvar>\n'
                f'          <displayfeedback feedbacktype="Response" linkrefid="{index + 1}_fb"/>\n'
                f'        </respcondition>\n'
            )

    correct = [i + 1 for i, a in enumerate(answers) if a.get("correct")]
    if multiple:
        # Every correct one chosen, and no incorrect one chosen. Partial
        # credit is deliberately not offered: a student who marks every box is
        # not demonstrating anything.
        wrong = [i + 1 for i, a in enumerate(answers) if not a.get("correct")]
        clauses = "".join(f'              <varequal respident="response1">{n}</varequal>\n'
                          for n in correct)
        clauses += "".join(f'              <not><varequal respident="response1">{n}</varequal></not>\n'
                           for n in wrong)
        conditionvar = f'            <and>\n{clauses}            </and>\n'
    else:
        conditionvar = (f'            <varequal respident="response1">'
                        f'{correct[0] if correct else 1}</varequal>\n')

    conditions.append(
        f'        <respcondition continue="No">\n'
        f'          <conditionvar>\n{conditionvar}          </conditionvar>\n'
        f'          <setvar action="Set" varname="SCORE">100</setvar>\n'
        f'        </respcondition>\n'
    )

    feedback = _feedback("general_fb", question.get("general_feedback", ""))
    for index, answer in enumerate(answers):
        feedback += _feedback(f"{index + 1}_fb", answer.get("feedback", ""))

    return (
        f'{_metadata(question, ref)}'
        f'      <presentation>\n'
        f'{_mattext(question["text"], "        ")}\n'
        f'        <response_lid ident="response1" rcardinality="{cardinality}">\n'
        f'          <render_choice>\n{labels}          </render_choice>\n'
        f'        </response_lid>\n'
        f'      </presentation>\n'
        f'      <resprocessing>\n'
        f'        <outcomes>\n'
        f'          <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>\n'
        f'        </outcomes>\n'
        f'{"".join(conditions)}'
        f'      </resprocessing>\n'
        f'{feedback}'
    )


def _fib_item(question: dict, ref: str) -> str:
    """Short answer. Canvas calls this fill in the blank."""
    accepted = question.get("accepted") or []
    conditions = [
        '        <respcondition continue="Yes">\n'
        '          <conditionvar><other/></conditionvar>\n'
        '          <displayfeedback feedbacktype="Response" linkrefid="general_fb"/>\n'
        '        </respcondition>\n'
    ]
    if accepted:
        clauses = "".join(
            f'            <varequal respident="response1" case="No">{escape(str(a))}</varequal>\n'
            for a in accepted)
        conditions.append(
            f'        <respcondition continue="No">\n'
            f'          <conditionvar>\n            <or>\n{clauses}            </or>\n          </conditionvar>\n'
            f'          <setvar action="Set" varname="SCORE">100</setvar>\n'
            f'        </respcondition>\n'
        )
    else:
        # No accepted list. The value is different for every student, so it is
        # collected here and checked by the instructor against their student
        # ID. Canvas has no way to express "recompute this per student", and
        # inventing one would be worse than saying so.
        conditions.append(
            '        <respcondition continue="No">\n'
            '          <conditionvar><other/></conditionvar>\n'
            '        </respcondition>\n'
        )

    return (
        f'{_metadata(question, ref)}'
        f'      <presentation>\n'
        f'{_mattext(question["text"], "        ")}\n'
        f'        <response_str ident="response1" rcardinality="Single">\n'
        f'          <render_fib>\n'
        f'            <response_label ident="answer1" rshuffle="No"/>\n'
        f'          </render_fib>\n'
        f'        </response_str>\n'
        f'      </presentation>\n'
        f'      <resprocessing>\n'
        f'        <outcomes>\n'
        f'          <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>\n'
        f'        </outcomes>\n'
        f'{"".join(conditions)}'
        f'      </resprocessing>\n'
        f'{_feedback("general_fb", question.get("general_feedback", ""))}'
    )


def _numerical_item(question: dict, ref: str) -> str:
    value = float(question.get("value", 0))
    tolerance = float(question.get("tolerance", 0))
    low, high = value - tolerance, value + tolerance
    return (
        f'{_metadata(question, ref)}'
        f'      <presentation>\n'
        f'{_mattext(question["text"], "        ")}\n'
        f'        <response_str ident="response1" rcardinality="Single">\n'
        f'          <render_fib fibtype="Decimal">\n'
        f'            <response_label ident="answer1"/>\n'
        f'          </render_fib>\n'
        f'        </response_str>\n'
        f'      </presentation>\n'
        f'      <resprocessing>\n'
        f'        <outcomes>\n'
        f'          <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>\n'
        f'        </outcomes>\n'
        f'        <respcondition continue="Yes">\n'
        f'          <conditionvar><other/></conditionvar>\n'
        f'          <displayfeedback feedbacktype="Response" linkrefid="general_fb"/>\n'
        f'        </respcondition>\n'
        f'        <respcondition continue="No">\n'
        f'          <conditionvar>\n'
        f'            <or>\n'
        f'              <varequal respident="response1">{value:g}</varequal>\n'
        f'              <and>\n'
        f'                <vargte respident="response1">{low:g}</vargte>\n'
        f'                <varlte respident="response1">{high:g}</varlte>\n'
        f'              </and>\n'
        f'            </or>\n'
        f'          </conditionvar>\n'
        f'          <setvar action="Set" varname="SCORE">100</setvar>\n'
        f'        </respcondition>\n'
        f'      </resprocessing>\n'
        f'{_feedback("general_fb", question.get("general_feedback", ""))}'
    )


def _essay_item(question: dict, ref: str) -> str:
    return (
        f'{_metadata(question, ref)}'
        f'      <presentation>\n'
        f'{_mattext(question["text"], "        ")}\n'
        f'        <response_str ident="response1" rcardinality="Single">\n'
        f'          <render_fib>\n'
        f'            <response_label ident="answer1" rshuffle="No"/>\n'
        f'          </render_fib>\n'
        f'        </response_str>\n'
        f'      </presentation>\n'
        f'      <resprocessing>\n'
        f'        <outcomes>\n'
        f'          <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>\n'
        f'        </outcomes>\n'
        f'        <respcondition continue="No">\n'
        f'          <conditionvar><other/></conditionvar>\n'
        f'        </respcondition>\n'
        f'      </resprocessing>\n'
        f'{_feedback("general_fb", question.get("general_feedback", ""))}'
    )


def item(question: dict, ref: str) -> str:
    """One QTI item, whatever type it is."""
    kind = question["type"]
    if kind in ("multiple_choice", "true_false"):
        body = _choice_item(question, ref, multiple=False)
    elif kind == "multiple_answers":
        body = _choice_item(question, ref, multiple=True)
    elif kind == "short_answer":
        body = _fib_item(question, ref)
    elif kind == "numerical":
        body = _numerical_item(question, ref)
    elif kind == "essay":
        body = _essay_item(question, ref)
    else:
        raise ValueError(
            f"{ref}/{question['id']}: unknown question type {kind!r}. "
            f"Known types: {', '.join(sorted(CANVAS_TYPE))}"
        )

    # The outcome tag rides in the title. Canvas has no per-item outcome field
    # in Classic Quizzes, and the exam export is meant to be the per-student,
    # per-outcome score matrix that program assessment asks for. Putting the
    # outcome in the title is what makes that export sortable without any extra
    # instrumentation. It is a workaround and it is worth knowing it is one.
    title = f"{question.get('outcome', 'O?')} | {question['id']}"
    return (f'    <item ident="{ident(ref, question["id"])}" title="{escape(title)}">\n'
            f'{body}'
            f'    </item>\n')


def assessment(quiz: dict, ref: str, canvas_dialect: bool = True) -> str:
    """A whole quiz as one QTI document."""
    items = "".join(item(q, ref) for q in quiz.get("questions", []))
    max_attempts = quiz.get("allowed_attempts", 1)
    if max_attempts in (-1, None):
        max_attempts = "unlimited"

    metadata = [
        ("cc_profile", "cc.exam.v0p1"),
        ("qmd_assessmenttype", "Examination"),
        ("qmd_scoretype", "Percentage"),
        ("cc_maxattempts", str(max_attempts)),
    ]
    if canvas_dialect:
        metadata.append(("qmd_timelimit", str(quiz.get("time_limit_minutes", ""))))
    fields = "".join(
        f'        <qtimetadatafield>\n'
        f'          <fieldlabel>{label}</fieldlabel>\n'
        f'          <fieldentry>{escape(str(value))}</fieldentry>\n'
        f'        </qtimetadatafield>\n'
        for label, value in metadata if str(value)
    )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<questestinterop xmlns="{QTI_NS}" '
        f'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        f'xsi:schemaLocation="{QTI_SCHEMA}">\n'
        f'  <assessment ident="{ident("quiz", ref)}" title="{escape(quiz["title"])}">\n'
        f'    <qtimetadata>\n{fields}    </qtimetadata>\n'
        f'    <section ident="root_section">\n{items}    </section>\n'
        f'  </assessment>\n'
        f'</questestinterop>\n'
    )


def validate(quiz: dict, ref: str, expected_points: int) -> list[str]:
    """Everything that has to be true before a quiz is worth generating."""
    problems = []
    questions = quiz.get("questions") or []
    if not questions:
        return [f"{ref}: no questions"]

    total = sum(float(q.get("points", 0)) for q in questions)
    if abs(total - expected_points) > 0.01:
        problems.append(f"{ref}: points add to {total:g}, course.yaml says {expected_points}")

    seen = set()
    for question in questions:
        qid = question.get("id", "(no id)")
        if qid in seen:
            problems.append(f"{ref}/{qid}: two questions share an id")
        seen.add(qid)

        if question.get("type") not in CANVAS_TYPE:
            problems.append(f"{ref}/{qid}: unknown type {question.get('type')!r}")
        if not question.get("outcome"):
            problems.append(f"{ref}/{qid}: no outcome tag. The exam export is the "
                            f"per-outcome score matrix, and it only works if every "
                            f"item is tagged.")
        if not question.get("text", "").strip():
            problems.append(f"{ref}/{qid}: no question text")

        if question.get("type") in ("multiple_choice", "true_false", "multiple_answers"):
            answers = question.get("answers") or []
            correct = [a for a in answers if a.get("correct")]
            if len(answers) < 2:
                problems.append(f"{ref}/{qid}: needs at least two answers")
            if not correct:
                problems.append(f"{ref}/{qid}: no answer is marked correct")
            if question["type"] != "multiple_answers" and len(correct) > 1:
                problems.append(f"{ref}/{qid}: more than one correct answer on a "
                                f"single-answer question")
            for answer in answers:
                if not answer.get("feedback"):
                    problems.append(f"{ref}/{qid}: an answer has no feedback. A wrong "
                                    f"answer with no feedback teaches nothing, and in "
                                    f"an asynchronous course it is the only teaching a "
                                    f"student gets after getting it wrong.")
                    break
    return problems
