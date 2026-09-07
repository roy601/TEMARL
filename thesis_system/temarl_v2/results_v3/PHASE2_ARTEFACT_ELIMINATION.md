# Phase 2 — Artefact Elimination

Every experiment below asks the same question: **is the Transformer's loss a
property of the problem, or of how we configured the experiment?** Each states a
hypothesis and a falsifiable prediction *before* the run, applies every change
fairly to all architectures, and is reported whichever way it falls.

**Headline: the CAM-LDS result that this project has been treating as decisive
does not survive artefact elimination.** The previously reported
GRU − Transformer gap of **+0.1388 (d = 1.65, p_holm = 5.7e-14)** was measured on
a Transformer using absolute sinusoidal positional encoding at untuned defaults.
Correct those two things and the gap becomes **+0.0000**.

---

## 2.1 Data scale — **REFUTED**

*Hypothesis:* ~1.3k windows is below the regime where attention pays off.
*Prediction if true:* the gap closes as N grows.

Compute-matched (fixed 1,500 optimiser steps at every N), fixed test set,
session-level split, 3 paired seeds.

| Corpus | N | Transformer | GRU | SetEncoder | T − G |
|---|---|---|---|---|---|
| CAM-LDS | ~940 | 0.846 | 0.903 | 0.854 | −0.057 |
| COMISET | 500 | 0.658 | 0.682 | 0.493 | −0.024 |
| COMISET | 1,000 | 0.668 | 0.697 | 0.521 | −0.030 |
| COMISET | 2,000 | 0.678 | 0.721 | 0.529 | −0.044 |
| COMISET | 5,000 | 0.681 | 0.726 | 0.535 | −0.045 |
| COMISET | 10,000 | 0.685 | 0.732 | 0.538 | −0.047 |

**Slope = −0.0187 per decade — the gap WIDENS with data.** Both architectures
improve; the GRU improves faster. Never non-negative in range.

*Limitation:* the curve tops out at N = 10,000 (see the COMISET correction
below), so the very-large-data regime is untested.

### Correction to a figure used throughout this project

**COMISET yields 23,754 usable windows, not 1.5M.** `load_comiset_sequences`
collapses consecutive repeats, and at a 98.5% self-loop rate 1,547,359 raw steps
collapse to ~24k windows (mean 4.2 per session). The real data advantage over
CAM-LDS is **≈18×, not the 1156× quoted in HANDOFF.md and the v3 report.** That
figure counted raw steps and materially overstates the usable difference.

---

## 2.2 Context length — **REFUTED (and it points the other way)**

*Hypothesis:* `MAX_SEQ_LEN = 16` is too short for attention to express anything
recurrence cannot.

Best-Transformer minus GRU, by context length:

| Context | CAM-LDS | COMISET |
|---|---|---|
| 8 | **−0.0001** | −0.0071 |
| 16 | **+0.0037** | −0.0261 |
| 32 | −0.0070 | −0.0187 |
| 64 | −0.0132 | −0.0178 |

**Longer context makes things worse for every architecture.** `L = 16` was not a
handicap; if anything **L = 8 is the better setting**. Hypothesis refuted, with
the effect in the opposite direction to the prediction.

---

## 2.5 Positional encoding — **SUPPORTED, and this is the large effect**

*Hypothesis:* absolute sinusoidal PE — the same design that produced the v1 clock
leak — is the wrong choice, and relative/rotary position should do better.

CAM-LDS Top-1, mean of 3 seeds:

| Context | Trans-Sin | **Trans-RoPE** | Trans-NoPE | GRU | RoPE − Sin |
|---|---|---|---|---|---|
| 8 | 0.860 | **0.886** | 0.871 | 0.886 | **+0.026** |
| 16 | 0.837 | **0.881** | 0.855 | 0.878 | **+0.044** |
| 32 | 0.809 | 0.868 | 0.827 | 0.875 | **+0.059** |
| 64 | 0.796 | 0.866 | 0.804 | 0.879 | **+0.070** |

**RoPE beats absolute sinusoidal at every context length on both corpora, and the
advantage grows with length.** Absolute PE degrades badly as sequences lengthen;
rotary is robust. Dropping PE entirely (NoPE) also beats sinusoidal, which is
itself evidence that the absolute encoding was actively harmful rather than
merely suboptimal.

At L = 8 and L = 16 — the useful range per 2.2 — **RoPE matches or beats the GRU.**

---

## 2.4 Hyperparameters — **SUPPORTED (closes the remainder on CAM-LDS)**

*Fairness protocol:* **16 random trials per architecture** — equal budget, so
tuning is not applied only to the favoured model. Configuration selected on a
validation split, reported on a held-out test split it never saw, so the number
is not the upward-biased maximum of a search. The search space and trial count
were declared in source before the run, so "how many things did you try?" has the
written answer: exactly 16 each.

| Corpus | Best Transformer (TEST) | Tuned GRU (TEST) | Δ | Transformer params | GRU params |
|---|---|---|---|---|---|
| CAM-LDS | **0.881** (RoPE) | 0.881 | **+0.0000** | **156,310** | 351,702 |
| COMISET | 0.714 (RoPE) | 0.738 | −0.0242 | **418,902** | 1,026,102 |

On CAM-LDS the result is an **exact tie, with the Transformer using 44% of the
GRU's parameters**. On COMISET the GRU remains ahead by 0.024, using 2.4× the
parameters.

*(A labelling bug printed "GRU still ahead" for the +0.0000 CAM-LDS row on the
first run; the comparison used `>` where a three-way tie/ahead/behind label was
needed. Fixed in `phase2_hparams.py`; the number was always correct.)*

---

## 2.6 Pretraining objective — **SUPPORTED (and it decides the design of Phase 4)**

*Hypothesis:* the encoder is optimised for the wrong target. It is trained to
predict the next technique, but the reward term that drives DSR is
`PAYOFF[tau_next, a]`, so what the policy needs is `argmax_a PAYOFF[tau_next, a]`.
Phase 1 / v3 measured no positive relationship between next-technique accuracy
and DSR (*r* = -0.175, p = 0.18), which is what a misaligned objective looks like.

*Method:* four objectives, each trained then **frozen**, then read out by a
**linear** probe. Four architectures, 3 seeds. Majority baselines on this split:
next 0.141, action 0.414, profile 0.714.

### Probe: OPTIMAL DECOY ACTION — the quantity that drives reward

| Training objective | Trans-Sin | **Trans-RoPE** | GRU | SetEncoder | best T − GRU |
|---|---|---|---|---|---|
| `next` (current) | 0.825 | 0.867 | 0.844 | 0.831 | **+0.0227** |
| **`action` (aligned)** | 0.902 | **0.934** | 0.921 | 0.887 | **+0.0126** |
| `masked` | 0.757 | 0.724 | 0.769 | 0.753 | −0.0127 |
| `contrastive` | 0.541 | 0.550 | 0.533 | 0.538 | +0.0169 |

**Two findings, both material:**

1. **The current objective is measurably the wrong one.** Switching from
   next-technique to the aligned action objective raises action-decodability for
   every architecture — RoPE 0.867 → **0.934**, GRU 0.844 → 0.921. Roughly 7
   points of the quantity the policy needs were being left on the table by the
   pretraining objective alone.
2. **On this probe the Transformer leads in 3 of 4 objectives**, including the
   best cell overall (RoPE + action, 0.934 vs GRU 0.921).

### Probe: NEXT TECHNIQUE — what we have been measuring

| Objective | Trans-Sin | Trans-RoPE | GRU | best T − GRU |
|---|---|---|---|---|
| `next` | 0.824 | 0.871 | 0.869 | +0.0029 |
| `action` | 0.759 | 0.761 | 0.820 | −0.0597 |
| `masked` | 0.684 | 0.617 | 0.799 | −0.1152 |
| `contrastive` | 0.187 | 0.280 | 0.198 | +0.0825 |

### Probe: CAMPAIGN PROFILE

The GRU is better at recovering campaign identity under most objectives
(0.978 vs 0.939 under `next`), and the contrastive objective saturates every
architecture at ~1.000. **But campaign identity is not what the reward depends
on** — this is a good illustration of why choosing the metric by what a model is
good at, rather than by what the objective needs, is misleading.

**Overall: the Transformer wins 6 of 12 (probe × objective) cells.** The ranking
is objective-dependent, which was the hypothesis.

### Consequence for the final experiment

Every architecture comparison this project has run — including the tie in 2.4 —
was measured on next-technique prediction, an objective now shown to be
misaligned with the deception goal. The final experiment must pretrain on the
**action** objective, and the artefact-corrected Transformer is:

```
positional encoding : ROTARY (2.5)
context length      : 8      (2.2 - shorter is better)
pretraining         : ACTION objective (2.6)
hyperparameters     : per-architecture equal-budget tuned (2.4)
```

*Caveats:* these are linear probes on frozen `h`, a proxy for DSR rather than DSR
itself; margins on the action probe are small (+0.013 at the best cell) against
seed variance of ±0.02-0.04; and nothing here is significance-tested. That is
what the pre-registered final experiment is for.

---

## What Phase 2 has established so far

1. **The decisive CAM-LDS finding was largely our own artefact.** +0.1388 →
   +0.0000 after replacing absolute PE with rotary and giving both architectures
   an equal tuning budget. The strong claim that "the Transformer has never won
   across four independent tests" cannot stand in that form — one of those four
   tests was measuring a handicapped configuration.
2. **Two candidate explanations are refuted, not merely unsupported.** Data scale
   (gap widens) and context length (longer is worse) both fail with the effect
   pointing opposite to the prediction.
3. **A methodological hazard worth reporting in its own right:** at 150 training
   steps RoPE scored 0.472 and looked broken; at 1,200 steps it leads at 0.886.
   **Training length can invert an architecture ranking.** The original v3
   experiment pretrained its history encoders for 800 steps and may sit in that
   same regime.

## What Phase 2 has *not* established

- **A tie is not a win.** CAM-LDS 0.881 vs 0.881; COMISET still −0.024.
- **These are next-technique accuracies, not DSR.** Phase 1 measured no positive
  relationship between the two (*r* = −0.175, p = 0.18), so none of this yet
  transfers to the deception objective.
- **No significance testing.** These are exploratory artefact-elimination runs.
  The inferential test is pre-registered separately.

## Status

| Item | Verdict |
|---|---|
| 2.1 Data scale | Refuted |
| 2.2 Context length | Refuted (opposite direction) |
| 2.4 Hyperparameters | Supported |
| 2.5 Positional encoding | **Supported — largest effect** |
| 2.6 Pretraining objective | **Supported** — objective was misaligned; ranking is objective-dependent |
| 2.3 RL training budget | Deferred to the final experiment |
| 2.7 History vs entity encoder | Already separated in v3 (H6/H7) |
