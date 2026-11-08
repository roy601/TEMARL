# Rule for keeping a Transformer improvement

**Declared 2026-11-07, before any variant result exists. Validation data only. Implemented in
`compare_validation.py`.**

## The candidates, tested in this order

| # | Candidate | What changes | Paper |
|---|---|---|---|
| 1 | `allpos` | Causal attention, and the loss at every position, not only the last | SASRec (Kang & McAuley, ICDM 2018) |
| 2 | Repeat/new head | A gate that separates repeating a technique from predicting a new one | RepeatNet (AAAI 2019) |
| 3 | Asymmetric Loss | Replaces plain BCE | Ridnik et al. (ICCV 2021) |

Each candidate is compared with the **current design**: the baseline at first, then whatever has
been kept. `causal` (causal attention, last-position loss) is a **control** reported beside
candidate 1, to show whether a change comes from the mask or from the extra training signal. It
is not a candidate.

## The score

1. **Validation points** are split into **novel** and **copy** by the protocol 1.1 definition: a
   copy is a validation point whose window and target also occur in the fold's training runs.
2. Each training cell uses its own threshold, chosen on all its validation points, as always.
3. **Micro-F1 is pooled within 4 groups:** S1 variants, S3 variants, S6 variants, and the
   scenario-held-out folds. The groups are then averaged with **equal weight**. This stops S1 from
   dominating: 17 of its 18 folds validate on the same run.
4. Seeds are paired: seed *s* starts from the same weights for every variant.

## Keep the candidate only if all three hold

| # | Condition |
|---|---|
| 1 | **Novel points improve:** the score on novel validation points, averaged over the 10 seeds, is higher than the current design's |
| 2 | **Consistently:** it is higher in **at least 8 of the 10 seeds** |
| 3 | **No harm overall:** the score on all validation points does not fall by more than **0.01** |

Otherwise the current design stays.

**Also reported, but not part of the rule:** scores on copy points, micro-F1 on repeat and new
target labels, each group separately, and training length.

The kept design, and whether GRU/LSTM are run, are then frozen as **protocol 1.2** before any test
result is opened.

## Record of decisions

| Date | Candidate | Compared with | Decision | Report |
|---|---|---|---|---|
| 2026-11-08 | 1 `allpos` | baseline | **Kept** (novel +0.044, 10 of 10 seeds; all points +0.038) | `out/VALIDATION_COMPARISON_allpos.txt` |
| 2026-11-08 | 2 `repeat` | `allpos` | **Rejected** (novel −0.068, 0 of 10 seeds; all points −0.058) | `out/VALIDATION_COMPARISON_repeat.txt` |

`repeat` failed on the labels it was built for: on already-seen labels its false positives rose
from 362 to 1,302 (precision 0.942 → 0.816), i.e. it predicts that seen techniques come back.

The current design is now `allpos`. Its S1 group fell on novel points (−0.033, the same 8 steps of
one validation run); S1 will be reported on its own when the test results are opened.

## Candidate 2 as built (declared 2026-11-08, before it runs)

`repeat` = `allpos` + RepeatNet's repeat/new split, compared with `allpos` under the rule above.

- **Two output layers** on the same 64-D state. A label that already occurs at or before the
  position, inside the window, is scored by the **repeat** layer; any other label by the **new**
  layer (the existing head). As in RepeatNet, each side scores only its own labels.
- **Not used: RepeatNet's soft repeat-or-new switch.** With one yes/no score per label, it would
  hold at least one label of a step at 0.5 or below whenever the step mixes a seen and a new label.
  Measured: 50 of the 870 CAM-LDS targets are such steps.
- **Everything else is `allpos`:** same encoder, same starting weights for each seed, same loss at
  every position, same training rules and budget. One layer is added (5,265 parameters); the 64-D
  state used by MAPPO is unchanged.
