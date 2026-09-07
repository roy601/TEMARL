# TEMARL v3 — Experiment Report

> ## ⚠ SUPERSEDED — the v3 null was measured on an instrument that could not
> ## have detected the effect
>
> The pre-registered v3 numbers below are correct. Their *interpretation* is not,
> and §6 in particular has been overturned.
>
> Measured afterwards, by analyses that never reference which architecture wins:
>
> - **The task could not discriminate history architectures at all.** A perfect
>   next-technique model was worth **+0.0005 DSR** over a 3-way campaign label.
>   The optimal decoy was constant within a campaign (84/84 techniques for two
>   campaigns, 83/84 for the third). See `results_v4/VERDICT.md`.
> - **§6's headline — "intent accuracy and DSR are not related" — is wrong as
>   stated.** Intent is worth **+0.148 to +0.171 DSR** (memoryless baseline →
>   campaign oracle). What was worth ≈0 is a *perfect sequence model on top of a
>   class label*. The *r* = −0.175 correlation was computed across policies none
>   of which was using the encoder.
> - **The root cause was an estimator defect**, not a property of deception:
>   `build_profiles_from_camlds()` added a column-constant to every row of the
>   transition matrix, destroying ~87% of the corpus's sequential information.
>
> **The current result is `results_v5/PHASE5_RESULT.md`** — on a repaired and
> validated instrument (sequence value +0.0800, 5 of 5 arms clearing the
> memoryless baseline at 62–77% of headroom), all 8 pre-registered contrasts are
> null and the effect is bounded within ±0.007 DSR.

**Result: H6, H7 and H8 are all NOT SUPPORTED. The Entity Transformer does not
beat DeepSets, and attention costs 1.84× the training time for no measurable
gain.** This is a pre-registered negative result and is reported as such.

---

## 1. Provenance

| | |
|---|---|
| Hardware | NVIDIA GeForce RTX 4080 SUPER (run on a separate machine) |
| Wall time | 6,805 s (1.9 h) |
| Seeds | 10 (0–9), paired across all arms |
| Budget | 600 training episodes, 200 evaluation episodes per regime |
| Runs | 60 = 6 arms × 10 seeds — **all completed**, 30/30 history pretrains |
| Config match | Exactly the `prereg_v3.py` specification; topology sets identical |

**All 10 gate modules passed on the GPU machine**, including `env_entity`
**EXACT EQUIVALENCE** (0 mismatches vs `env_v2`), `tests_entity` **26/26**,
payoff headroom **0.2698**, and frozen payoff rows 0–77 unchanged.

The analysis was **independently re-run here** from the raw results; it
reproduces the shipped `entity_analysis_gpu.json` to **0.00e+00** on every
delta, Holm-corrected p-value and effect size.

---

## 2. Primary metric — DSR by arm and regime (mean ± 95% CI, n = 10)

| Network enc. | History enc. | A (control) | B (trained sizes) | C (unseen struct.) | D (unseen sizes) | Gen. gap B−D |
|---|---|---|---|---|---|---|
| EntityTransformer | Transformer | 0.469 ± 0.029 | 0.445 ± 0.029 | 0.454 ± 0.029 | 0.380 ± 0.031 | +0.066 |
| EntityTransformer | GRU | 0.458 ± 0.045 | 0.433 ± 0.039 | 0.431 ± 0.038 | 0.368 ± 0.024 | +0.066 |
| EntityTransformer | SetEncoder | 0.441 ± 0.030 | 0.424 ± 0.030 | 0.423 ± 0.029 | 0.365 ± 0.027 | +0.059 |
| **DeepSets** | **Transformer** | **0.485 ± 0.034** | **0.459 ± 0.034** | 0.455 ± 0.037 | **0.383 ± 0.032** | +0.076 |
| DeepSets | GRU | 0.463 ± 0.021 | 0.439 ± 0.017 | 0.445 ± 0.017 | 0.371 ± 0.019 | +0.068 |
| DeepSets | SetEncoder | 0.459 ± 0.029 | 0.440 ± 0.028 | 0.441 ± 0.026 | 0.363 ± 0.024 | +0.077 |

The best arm in every regime is a **DeepSets** arm. The generalisation gap is
essentially constant (+0.059 to +0.077) across all six arms: **no architecture
generalises to unseen network sizes better than any other.**

---

## 3. Pre-registered contrasts (paired t-test, Holm–Bonferroni, α = 0.05)

| Contrast | Regime | Δ DSR | *d* | p_holm | Verdict |
|---|---|---|---|---|---|
| H6-Transformer | B | −0.0145 | −0.37 | 1.000 | not significant |
| H6-GRU | B | −0.0055 | −0.10 | 1.000 | not significant |
| H6-SetEncoder | B | −0.0155 | −0.39 | 1.000 | not significant |
| H7-C-GRU | C | −0.0135 | −0.28 | 1.000 | not significant |
| H7-D-GRU | D | −0.0030 | −0.11 | 1.000 | not significant |
| H8-hist-B | B | −0.0115 | −0.18 | 1.000 | not significant |
| H8-hist-D | D | −0.0115 | −0.34 | 1.000 | not significant |

**All 7 of 7 contrasts point in the direction opposite to the hypothesis** —
every one favours the simpler model.

* **H6 — NOT SUPPORTED.** EntityTransformer does not beat DeepSets on new
  topologies at trained sizes.
* **H7 — NOT SUPPORTED.** Nor on unseen structure or unseen sizes.
* **H8 — NOT SUPPORTED.** The history-GRU advantage found on CAM-LDS
  (+0.139 Top-1, *d* = 1.65) **does not reproduce** here; on DSR the history
  Transformer is nominally ahead by 0.011–0.012, not significantly.

---

## 4. Is this a real null, or just underpowered?

Both questions must be answered, and the honest answer is *partly the second,
but the bound still settles the practical question*.

**Power.** With n = 10 paired seeds this design can only detect
Cohen's *d* ≥ **1.00** at 80 % power (α = 0.05), or *d* ≥ **1.41** under the
Holm-corrected α. Every observed effect is |*d*| ≤ 0.39. **The study was not
powered to detect small effects, and a small true effect cannot be excluded by
the p-values alone.**

**But the effect is bounded.** Pooling the three H6 contrasts (n = 30 pairs —
**exploratory, not pre-registered**):

```
EntityTransformer − DeepSets, regime B:  Δ = −0.0118,  d = −0.27,  p = 0.150
95% CI on Δ:  [−0.0275, +0.0039]
```

The upper confidence bound on any true benefit from attention is **+0.004 DSR**
— four tenths of one percentage point. So this is not merely "we failed to
detect something": the data **exclude a practically meaningful advantage**, even
though they cannot exclude a tiny one.

---

## 5. Compute cost

| Network encoder | Params | Mean train time / arm |
|---|---|---|
| EntityTransformer | 110,984 | **125 s** |
| DeepSets | 116,943 | **68 s** |

DeepSets is *slightly larger* in parameters (capacity was matched at the encoder
level: 74,369 vs 73,828, 0.7 % apart) yet trains **1.84× faster** and performs
at least as well. Attention is the more expensive option on every axis measured.

---

## 6. The finding that matters most for the thesis

Next-technique prediction accuracy and deception success are **not positively
related**, and the observed ordering is exactly inverted:

| History encoder | Pretrain Top-1 | Regime-B DSR |
|---|---|---|
| GRU | **0.558** (best predictor) | 0.436 |
| SetEncoder | 0.511 | **0.432** (worst DSR) |
| Transformer | **0.361** (worst predictor) | **0.452** (best DSR) |

Across all 60 runs: Pearson *r* = **−0.175** (p = 0.18), Spearman *ρ* = −0.104
(p = 0.43). The correlation is **not significantly different from zero**, so the
inversion should be read as *"no relationship"* rather than as a demonstrated
negative one.

That is still a serious result for a thesis whose pipeline assumes better
attacker-intent modelling produces better deception. **In this environment, a
54 % relative improvement in intent prediction (0.361 → 0.558) buys no
improvement in Deception Success Rate at all.** The link between the encoder
objective and the defence objective is not established, and should not be
asserted.

---

## 7. What should be claimed

**Defensible:**
1. A variable-topology entity environment that reproduces the fixed 5-zone
   control **exactly** (0 mismatches / 1,126 steps) — a genuine engineering and
   validity contribution.
2. A pre-registered, Holm-corrected, 10-seed factorial that **cleanly answers
   its question in the negative**, with the effect bounded, not merely undetected.
3. Attention — over network entities *and* over attacker history — does not earn
   its cost in this setting. Reported with the power caveat stated.

**Not defensible any more:**
- Any claim that the Transformer architecture is what makes TEMARL work.
  **[CORRECTED]** — this originally added "it has never won. On CAM-LDS it
  significantly *lost*." Both are too strong. On DSR with the DeepSets encoder
  the v3 history Transformer was nominally *ahead* (0.459 vs 0.439); and the
  CAM-LDS deficit of +0.1388 was our own configuration artefact, closing to
  **+0.0000** once rotary position and an equal tuning budget were applied to
  both arms (Phase 2.4/2.5). The conclusion survives; this evidence for it does
  not.
- **[CORRECTED]** "Any claim that improved intent prediction drives deception
  performance." **Withdrawn as stated** — intent is worth +0.148 to +0.171 DSR.
  What buys ≈0 is a better *sequence* model on top of a campaign label, in an
  environment whose optimal decoy was constant within a campaign. See the banner
  at the top of this file.

The honest framing is that the contribution is the **environment, the D3FEND
grounding, and the evaluation discipline** — not the architecture.

---

## 8. Limitations

1. **Power.** n = 10 detects only *d* ≥ 1.00. Small effects remain possible;
   the CI bound, not the p-value, is what rules out a useful effect.
2. **One training budget.** 600 episodes; DSR was still improving at 500 in a
   pilot (0.370 random → 0.460). A larger budget could in principle favour the
   higher-capacity model, and this was not tested.
3. **One reward and one attacker model.** The attacker is a scripted CAM-LDS
   profile sampler, not adaptive. A learning attacker might reward structural
   reasoning differently.
4. **Agent count fixed at 4** across all topology sizes (QMIX mixes a constant
   number of agents), so scale varied in entities, not in agents.
5. **CPU/GPU non-determinism.** The run used CUDA; the committed
   `train_entity.py` sets `DEVICE = "cpu"`. Re-running locally reproduces the
   protocol and the conclusions, not bitwise-identical numbers.
