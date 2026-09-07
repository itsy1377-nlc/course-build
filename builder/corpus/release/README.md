# Ground truth, split by release time

These three files are written by `tools/build_corpus.py` from
`../ground_truth.json`. Do not edit them by hand. Edit a generator,
rerun the build, and they are rewritten.

| File | Who gets it, and when |
|---|---|
| `ground_truth_teaching.json` | The instructor package, with the weekly answer keys. |
| `ground_truth_batch.json` | Released with the week 7 page. The week 7 lab scores against it. |
| `ground_truth_exam.json` | The instructor package only. The emails ship in `builder/instructor/exam-emails/`. |

They sit here rather than beside `ground_truth.json` because the
corpus validator loads `ground_truth.json` and `ground_truth_*.json`
together and fails any id it sees twice. `ground_truth.json` stays the
working master that the generators write to.
