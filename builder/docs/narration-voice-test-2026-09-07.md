# A warmer voice for the course, and what it costs

**Written:** 2026-09-07
**Status:** judged. The rewrite is adopted; the engine is rejected and removed.
Nothing in the taught course has changed yet.

Two separate questions got tested together, because they arrived together:
does the *writing* read less robotic with contractions, and does a different
*narration engine* sound less robotic than Kokoro. They are independent, and
they should be judged independently. The test module holds one video script
read by both engines so the voice can be compared with the words held constant.


## 0. Verdict, 2026-09-07

**The warm rewrite is adopted. VoxCPM is rejected.**

Voice A (Kokoro, the existing engine) reading the rewritten script was judged
clearly better. Voice B (VoxCPM) was judged bad on listening, which no
measurement in section 2 predicted: every number there says the two engines
were equivalent on faithfulness, pace and level. They agree on everything a
spectrum and a transcript can see, and disagree on the thing that matters.
Recorded because it is the honest limit of this kind of testing, and because it
is the reason take 3 being promoted "on measurements, not taste" was a weaker
result than it sounded.

Everything VoxCPM touched has been removed. `tools/video/tts.py`, `schema.py`,
`build.py` and `config.py` are byte-identical to their committed versions,
confirmed with `git diff`. The worker, the voice-design tool, the voice profile,
the second virtualenv, the second scene list and the built video are deleted.
The pipeline renders with `kokoro:af_heart` exactly as before.

What survives is the writing, and section 2 is kept only as the record of an
engine that was tried and rejected.

---

## 1. What was deployed

A thirteenth module, `Test: Module 1 rewritten (review only)`, holding warm
rewrites of the three week 1 pages and both week 1 videos. Every file is a new
`test-` name. No existing page, module, assignment, quiz or video was edited.

| Page | Words | Budget | Grade | Original |
|---|---|---|---|---|
| `test-w1-overview` | 397 | 400 | 3.39 | 395 words, grade 2.89 |
| `test-w1-content` | 1395 | 1400 | 4.98 | 1397 words, grade 4.33 |
| `test-w1-wrap-up` | 382 | 550 | 3.39 | 371 words, grade 2.97 |

All three stay inside their budgets and far under the grade 8.0 ceiling.

**The rewrite costs about half a grade level.** Mean sentence length went from
9.4 words to 10.5. That is the warmth: connective tissue ("so", "because",
"and") joins clauses that used to sit as separate flat statements. Contractions
pull the other way and are free. Whether half a grade is worth it is the
judgement being asked for.

**One correction rode along.** The original overview said "Your notebook work
stays on the notebook server for the whole term. Nothing you write disappears."
That is false on JupyterLite: work lives in the browser profile. The test page
says so and points at the backup instructions.

---

## 2. The narration engine

`VoxCPM 2.0.3` (`openbmb/VoxCPM2`), installed in its own virtualenv at
`tools/video/.venv-voxcpm`. It needs torch 2.14 and Kokoro is pinned to 2.13,
so they cannot share an environment. The existing Kokoro venv was not touched.

### It designs a new speaker on every call, which is the thing to know

VoxCPM is a cloning model. Asked only for a description, it invents a voice
that matches the description and then invents a different one on the next cue.
Measured across six cues, on mel-spectrum similarity:

| Mode | Mean pairwise timbre similarity | Worst pair |
|---|---|---|
| Description only | 0.66 | 0.25 |
| Cloned from one committed reference clip | **0.97** | **0.92** |

0.25 is a different narrator between one slide and the next. So the written
description authors the voice **once**, offline, and the chosen take is
committed as `tools/video/voices/course-warm.wav`. Every cue in the course
clones that file. `design_voice.py` does the authoring and records the
description in `course-warm.json`, so the voice is reproducible from the
repository rather than from somebody's shell history.

Five takes were generated from the description "warm, friendly female
instructor, clear and encouraging, speaking at a steady pace". Take 3 was
promoted on measurements, not taste: it was the only one with an exact
transcript match, the closest pace to Kokoro (2.76 vs 2.58 words/sec), a
healthy peak (0.317, no clipping) and the lowest noise floor (-90.8 dB).
**Nobody has listened to it yet.** Re-run `design_voice.py course-warm
--description "..." --choose N` to pick a different take.

### Does it say what the script says

This mattered more than it sounds. Captions in this pipeline are authored from
the script, never transcribed, so a word the engine invents desynchronises
them. In description-only mode VoxCPM did paraphrase: one take opened a line
with a "But" the script never wrote.

Both finished videos were transcribed and diffed against their own scene list:

| Engine | Words heard | Matched | Differences |
|---|---|---|---|
| Kokoro | 356 | 352/356 (98.9%) | four, all "1" heard as "one" |
| VoxCPM | 356 | 352/356 (98.9%) | the same four |

Identical. Cloning from a fixed reference reads the script exactly; the
paraphrasing is a description-only behaviour. That is a second reason the
reference clip is not optional.

### What it costs

| | Kokoro | VoxCPM |
|---|---|---|
| Build time, one 2-minute video | 53s | 215s cold, 40s warm |
| Model load | in-process | ~100s once per build |
| Output rate | 24 kHz | 48 kHz, resampled to 24 kHz |
| Video length, same script | 123.8s | 128.2s |

About four times slower on a cold build. The worker loads the model once and
answers cues over a pipe for the life of the build, so the load cost is paid
per run rather than per cue; per cue it would have added forty minutes a course.

---

## 3. How it is wired, and how to undo it

Additive throughout. `voice` still defaults to `kokoro:af_heart`, and the two
lines removed from `tts.py` were a docstring and an error message that now name
the new engine. Kokoro was re-run after the edit and renders identically.

- `tts.py` gains `VoxCPMVoice`, which talks to a worker in the other venv and
  resamples 48 kHz to the pipeline's 24 kHz the same way `say` already does.
- `voxcpm_worker.py` is that worker.
- `design_voice.py` authors a voice profile from a written description.
- `schema.py`'s voice audit is now per engine. A Kokoro voice must be in the
  auditioned set; a VoxCPM profile must exist as a committed `.wav`/`.json`
  pair. Both still fail at load rather than after a render, which was the
  point of the check. Verified by feeding it a typo in each engine.
- `build.py` resolves the engine in one function, `resolve_voice_spec`, used by
  both the renderer and the cache fingerprint. **The fingerprint previously
  omitted the engine**, so switching engines would have reused the cached audio
  and silently produced a comparison of one voice with itself.
- A scene list may now carry `voice: voxcpm:course-warm`, which is how
  `test-w1-overview-voxcpm.yaml` differs from `test-w1-overview.yaml`. The
  A/B lives in content, not in an environment variable.
- `ITSY_VIDEO_VOICE` overrides the course default for a one-off build.

To remove the experiment entirely: delete the test module from `course.yaml`,
the `content/pages/test-w1-*.md` files, and the `content/video/test-w1-*.yaml`
files. The engine support can stay; nothing uses it unless a scene list asks.

---

## 4. One thing I got wrong, recorded because it is the house defect

The first measurements said VoxCPM spoke at half speed and produced gibberish.
Both were false. I wrote its output at 16 kHz because I assumed the rate
instead of reading `model.tts_model.sample_rate`, which is 48000. Every file
played three times too slow and two octaves down.

Nothing raised. `soundfile` writes whatever header it is given, the duration
looked plausible, and my own word-count check passed on the gibberish because
the counts were roughly right. It was caught only by transcribing the audio and
reading the words back, against a Kokoro control that transcribed cleanly.

Same shape as the four defects in the infrastructure memo: **a value that was
sent but never read back**. The worker now reports the model's own rate and
`tts.py` resamples on that number rather than on an assumption.
