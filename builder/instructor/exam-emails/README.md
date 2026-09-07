# Exam-only emails

The eleven emails numbered 046 to 056 are reserved for the week 8 final exam.
They live here, in the instructor package, and never under `corpus/emails/`,
so nothing a student can reach holds them before the exam.

Each one is rendered by its generator under
`builder/corpus/tools/generators/`, the same way every other corpus email is,
and each ground truth record is upserted into the master
`builder/corpus/ground_truth.json`, which `build_corpus.py` splits into
`builder/corpus/release/ground_truth_exam.json`. There is no
`builder/corpus/ground_truth_exam.json`: a second ground truth file beside the
master would be picked up by the validator's own `ground_truth*.json` glob and
collide with it, which is why the release copies sit under `release/`.

Validate them with the corpus validator pointed at this folder:

    python3 builder/corpus/tools/validate_corpus.py \
        --emails builder/instructor/exam-emails \
        --ground-truth builder/corpus/release/ground_truth_exam.json

The exam quotes header blocks and tool returns from these emails as question
stems. Students never receive the files.
