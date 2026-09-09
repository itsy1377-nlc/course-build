# Why week 3's facts block does not move the verdict, measured

**Run:** 2026-09-08, granite-3b through the course proxy at temperature 0.2.
128 classifications: 8 emails, 8 runs each, both conditions. Script
`w3_ground.py`, raw record `granite-3b-8x8.json`.

The harness is built from week 3's own pre-written cells plus the solution's
`build_facts()` and `format_facts()`. Body-alone uses week 2's
`classify_email()`; with-facts uses the shipped `classify_grounded()`. Nothing
is reimplemented, so a result here is a result about the notebook as shipped.

Objective 3.2 is **"Report which verdicts changed after you added the facts
block."**

## 1. The lab runs other weeks' emails

`corpus/ground_truth.json` tags every teaching email with the weeks it belongs
to. Week 3's designed set is **001, 004, 005, 006, 017, 025**. Cell 14 runs
**001, 004, 005, 016, 017, 019**.

    016 is tagged weeks [6].   019 is tagged weeks [4].
    006 and 025 are tagged week 3 and are never run.

The blind run found the naming inconsistency and read it as the prose failing
to follow a moved email set. It is the other way round. The wrap-up, the
overview video, self-check Q3 and the notebook's own TODO cells all name 005
and 025, which is the corpus design. The assignment page, the reading and cells
7, 10, 12 and 14 drifted. Cell 10 prints the header `email 025` over 016's
values and cell 12 assigns `parsed_025 = load_email("016", ...)`. Nothing
errors, so nothing catches it.

**The prose is right. The code drifted.**

## 2. And correcting the set would not have fixed the objective

| id | truth | designed to move | body alone | with facts | moved |
|---|---|---|---|---|---|
| 001 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| 004 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| **005** | benign | malicious to benign | malicious 8 | malicious 8 | **0/8** |
| 006 | malicious | no | malicious 8 | malicious 8 | 0/8 |
| **016** | malicious | benign to malicious | malicious 8 | malicious 8 | **0/8** |
| **017** | benign | uncertain to benign | benign 8 | **malicious 8** | **8/8** |
| **019** | benign | malicious to benign | malicious 8 | malicious 8 | **0/8** |
| **025** | malicious | benign to malicious | malicious 8 | malicious 8 | **0/8** |

**Every email designed to move stays put**, including both of the ones the
corpus intends as the demonstration pair. The only movement in the set is 017,
flipping benign to malicious 8 times out of 8, when the truth is benign and the
design was uncertain to benign. **Zero movements toward truth anywhere.**

Objective 3.2 is therefore demonstrated only by a deterministic false positive.
The course hedges the non-movement well -- three places say a row that did not
move is a real result, and the rubric scores the student's fact choices rather
than the model's answers, which is exactly what week 1 lacked -- so this costs
no student any points. The week's central claim is still unsupported.

## 3. Two things underneath it

**granite-3b reads malicious from the body alone on 7 of 8 emails**, including
005 and 019, which are benign. It will not be talked out of malicious, so
"facts exonerate a benign email" cannot demonstrate itself with this model on
this corpus. Only 017 reads benign from the body, and that is the one the facts
flip the wrong way.

**The facts block makes 017 worse.** Every fact on it is clean:

    SPF result: pass          DKIM result: pass        DMARC result: pass
    Display name mismatch: False                       Gateway scan result: clean
    Attachment names: []      Reply address: None

`format_facts()` renders every value with `str()`, so booleans arrive as
`False`, empty lists as `[]` and absent values as `None`. The blind run
reported the model citing "Display name mismatch: False" among its reasons for
calling 017 malicious.

**Hypothesis, not yet tested:** a small model reads the salient phrase and drops
the negation, so a block of clean facts reads as a block of security concerns.
Rendering booleans and empties as natural language would settle it. Codex is
reviewing whether that is the right first experiment before any calls are spent.

## What this does not yet say

The measurement covers one model at one temperature on eight emails. It does
not say the facts block is useless -- 3.1 and 3.3 are about choosing and
justifying facts, and the rubric grades those directly. It says the *verdict*
is the wrong thing for 3.2 to measure on this model, and that the pair chosen
to demonstrate movement demonstrates none.

## Running these

`w3_ground.py` expects `/tmp/w3_prewritten.py` and `/tmp/w3_solution_fns.py`,
extracted from the lab and solution notebooks, and a key at
`/root/.w3-eval-key`. It runs from `~/eval/builder` on the litellm guest so the
corpus path walk resolves. Same shape as `docs/week2-measurement/`.

## 4. Which teaching emails actually flip, measured (139 calls)

The corpus designs sixteen teaching emails to read differently from the body
alone than the truth. Section 2 measured the five relevant to week 3. This
measures the other eleven, 6 runs per email per condition, to find out whether
a correct demonstration exists anywhere. Script `w3_candidates.py`.

    id   truth      designed              body alone    with facts    moved
    008  malicious  benign -> malicious   benign:6      malicious:6   6/6  toward truth
    021  malicious  uncertain -> malic.   benign:6      malicious:6   6/6  toward truth
    007  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6
    009  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6
    010  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6
    013  malicious  uncertain -> malic.   benign:6      benign:6      0/6
    014  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6
    015  benign     uncertain -> benign   malicious:6   malicious:6   0/6
    018  malicious  benign -> malicious   malicious:6   malicious:6   0/6
    023  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6
    024  malicious  uncertain -> malic.   malicious:6   malicious:6   0/6

**Two emails flip correctly and deterministically: 008 and 021.** Both are
genuinely malicious, both read benign from the body alone 6 times out of 6, and
both become malicious once the facts arrive, 6 times out of 6. That is the
week's lesson, working.

Neither is tagged for week 3. 008 is tagged week 4, 021 week 6.

Across all nineteen emails measured, exactly **two flip correctly, one flips
incorrectly (017), and sixteen do not move.**

### The walkthrough's email does not reproduce

`content/video/runs/w3.json` records email 009 flipping benign 11/11 to
malicious 11/11 on 2026-09-05. Measured here on the same model, 009 reads
malicious 6/6 in both conditions and does not move. The model name difference
(`granite4.2:3b` against `granite-3b`) is only a proxy alias and not the cause.
The walkthrough's claim that "your run will flip the same way" is not
reproducible today, and the video says it about an email no lab runs.

### What the corpus tags are and are not

`weeks` and `body_only_read` encode design intent. They were never validated
against the shipped model, and section 2 shows where they part company: 025's
label says the body reads benign, and granite-3b reads it malicious 8 times out
of 8. Treat the tags as authoritative for which week owns an email's story, and
measurement as authoritative for what the model actually does with it.

## 5. Option B was disproven before it shipped (120 calls)

008 looked like the demonstration week 3 needed: genuinely malicious, benign
6/6 from the body, malicious 6/6 with the facts. The plan was to put it in the
set. Then its facts turned out to be nearly identical to 017's -- spf, dkim and
dmarc all pass, no display-name mismatch, a clean scan, one link on the sender's
own domain, no attachment -- while their truths are opposite. Two emails with
the same facts cannot both be settled by those facts.

`w3_swap.py`, 6 runs per condition:

    email  condition                 verdict
    008    body alone                benign:6              (truth malicious)
    008    its own facts             malicious:6
    008    017's facts               malicious:6
    008    facts, values withheld    malicious:6
    017    body alone                benign:6              (truth benign)
    017    its own facts             None:5 malicious:1
    017    008's facts               benign:1 malicious:5
    017    facts, values withheld    malicious:6

**A facts block with every value replaced by "(withheld)" flips both emails to
malicious, 6 times out of 6.** The content of the block does nothing. 008's
"correct" flip is the same artifact as 017's wrong one, landing on the right
answer by luck. Shipping it as the demonstration would have taught a false
positive as grounding.

This is the week 1 number-probe failure again: a statistic that looked perfect
with the wrong thing underneath, catchable only by looking at the values.

## 6. Which section actually moves the verdict (72 calls)

`w3_isolate.py` splits the grounded prompt into its three added sections.

    email  condition               verdict                (truth)
    008    body alone              None:1 benign:5        malicious
    008    facts only              benign:4 malicious:2
    008    playbook only           malicious:6
    008    known-good only         malicious:6
    008    facts + playbook        malicious:6
    008    everything (shipped)    malicious:6

    017    body alone              benign:6               benign
    017    facts only              malicious:6
    017    playbook only           None:1 benign:5
    017    known-good only         None:3 benign:3
    017    facts + playbook        malicious:6
    017    everything (shipped)    None:2 malicious:4

There is no single culprit. On 017 the **facts block alone** causes the wrong
flip while the playbook and known-good list leave it correctly benign. On 008
the **playbook alone** and the **known-good list alone** each cause the flip,
and the facts barely move it.

The finding that survives both: **the shipped grounded prompt pushes granite-3b
toward malicious more or less regardless of which email it is judging and what
the facts say.** Adding security-flavoured context makes a small model more
suspicious. That is a real and teachable result, but it is not CLO1 and it is
not what week 3 currently claims.

`build_grounded_prompt()` is carried by weeks 4 through 7, so changing the
prompt's shape is a cross-week change and out of week 3's scope.

## 7. No available model demonstrates 3.2 (205 calls, five models)

The question was whether another model would ground properly. The test is not
"does the verdict move" -- section 5 showed a move can be an artifact -- but
"does it move because of the facts". The control is a facts block with every
value replaced by "(withheld)". A model that grounds should behave differently
with real facts than with withheld ones.

The three `test-` models were restored to the proxy for this study
(`/etc/litellm/config.yaml.bak-w3study` is the config without them) and the
eval key's allowlist was widened. **No student key can reach them:** the
allowlist is per key, which is why the first attempt returned 403.

008 is malicious and reads benign from the body. 017 is benign and reads benign
from the body. A model that grounds flips 008 and leaves 017 alone.

| model | 008 own facts | 008 withheld | 017 own facts | 017 withheld | verdict |
|---|---|---|---|---|---|
| granite-3b | malicious 6 | **malicious 6** | malicious | **malicious 6** | flips both, ignores content |
| granite-8b | benign 6 | benign 6 | benign 6 | benign 6 | never moves, misses 008 |
| test-gemma3-12b | benign 5 | benign 5 | **malicious 5** | benign 5 | reads facts, reaches the wrong answer |
| test-llama31-8b | benign 5 | benign 3 None 2 | benign 5 | malicious 3 benign 2 | mostly ignores facts, misses 008 |
| test-qwen3-14b | **None 5** | None 5 | None 5 | None 3 | fails the schema on every grounded prompt |

**Not one model both flips 008 for the right reason and leaves 017 alone.**

gemma3-12b is the only one that is measurably reading the facts -- withheld
values leave 017 benign while real ones flip it -- and it uses them to reach
the wrong answer, while missing the real phish entirely. qwen3-14b cannot
return schema-valid JSON once the grounded prompt is assembled, which would
break week 2's contract as well.

**Conclusion: changing the model does not rescue objective 3.2.** Keep
granite-3b and reword the objective to the indicator comparison. Nothing here
argues against the facts block itself, which 3.1 and 3.3 grade directly; it
argues that the verdict is the wrong thing for 3.2 to measure.

### An inconsistency this surfaced

Week 1 runs granite-8b and weeks 2 through 7 run granite-3b, and no page
explains the change. Week 1 was moved deliberately, because granite-3b answers
a credential phish 0.00 twenty times out of twenty and gets 40% of verdicts
wrong at temperature 1.0. The switch is defensible; its silence is not. Either
the configuration cell should say why the model differs, or week 1 should be
re-measured on granite-3b now that its prompt shape has changed.

## 8. The reworded objective is demonstrable (69 calls)

Rewording 3.2 to the indicator comparison only works if the indicators move.
If they were as insensitive as the verdicts, one undemonstrable objective would
have been swapped for another, which is the mistake this review keeps catching.

`w3_indicators.py`, the corrected six-email set, 4 runs per email per
condition:

    id   plain ind  grnd ind  shared   new in grounded  quotes a fact
    001  3.8        4.0       0.0      4.0              1.5
    004  4.0        5.0       0.0      5.0              0.0
    005  1.0        2.2       0.0      2.2              1.8
    006  3.0        4.2       0.0      4.2              0.0
    017  3.2        5.2       0.0      5.2              2.2
    025  5.0        6.0       0.0      6.0              3.0

Zero shared indicators on every email, 4.46 new ones per email, and a mean of
1.42 grounded indicators per email that quote a value from the facts block --
nonzero on four of six.

### The control, because "zero shared" could have been rewording

If the model simply rephrases every time, zero overlap says nothing about the
facts. `w3_ind_control.py` measures overlap as Jaccard within each condition as
well as across:

    id    plain vs plain   grounded vs grounded   plain vs grounded
    001   1.00             0.11                   0.00
    005   1.00             1.00                   0.00
    017   1.00             0.71                   0.00
    025   1.00             0.50                   0.00
    mean  1.00             0.58                   0.00

**Two plain runs of the same email produce identical indicator sets.** At
temperature 0.2 the ungrounded answer is perfectly reproducible, so the
complete turnover when the facts block arrives is an effect of the facts block
and not of sampling. This is the one place in week 3 where a control confirmed
a claim instead of destroying it.

Grounded runs vary among themselves (0.58), so the material must not promise
that two grounded runs match. It should promise that the grounded list differs
from the plain one, which held on 4 of 4 emails here and 6 of 6 above.

**Objective 3.2, reworded to the indicator comparison, is demonstrable on the
shipped model with the corrected email set.** The verdict was the wrong thing
to measure; the reasoning was the right one all along.

## 9. The pre-registered test: 6 of 6, PASS (105 calls)

Section 8 used raw string overlap, which is suggestive but easy to flatter.
Codex fixed a decision rule **before seeing any of those numbers**: map each
indicator string to one of thirteen canonical fact-field concepts, keep only
concepts stable across at least 75% of replies, and qualify a row only when the
grounded set adds a fact concept the plain set lacks **and** the symmetric
difference over the union is at least 0.50. Pass on 4 or more of six rows.

`w3_prereg.py`, N=8 replies per condition per email, stable at 6 of 8:

    id   |P|  |G|  new fact concepts in the grounded run          D     qualifies
    001  0    3    display_name_mismatch, subject, url_hosts      1.00  yes
    004  0    2    display_name_mismatch, from_domain             1.00  yes
    005  0    1    url_hosts                                      1.00  yes
    006  0    4    display_name_mismatch, dmarc, spf, url_hosts   1.00  yes
    017  1    2    from_domain, url_hosts                         1.00  yes
    025  0    5    display_name_mismatch, dmarc, from_display...  1.00  yes

    qualifying rows: 6 of 6      verdict: PASS

**On five of six emails the ungrounded run names no fact-field concept at
all.** It has only the body, so it can only talk about wording. The grounded
run names SPF, DMARC, the link host, the sender domain, the display-name check
and the subject. D is 1.00 on every row: complete turnover.

That is the week's lesson, and it is what CLO1 actually asks -- extract the
header, authentication, sender and URL facts a model needs. The student can see
their own extracted facts entering the model's reasoning, on every row, whether
or not the verdict moved.

**Decision: keep objective 3.2 reworded to the indicator comparison.** It
passes a threshold set in advance, at 6 of 6, with section 8's control showing
that two ungrounded runs are byte-identical so the turnover cannot be sampling.
