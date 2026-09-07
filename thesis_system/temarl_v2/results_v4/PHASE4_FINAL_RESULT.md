# Phase 4 — Final Pre-Registered Result

> ## ⚠ SUPERSEDED IN PART — read `VERDICT.md` alongside this document
>
> The pre-registered numbers below are correct and unchanged. **Their
> interpretation in §2 is not.** A reference-baseline ladder run afterwards
> (`baselines_entity.py`, `verdict_v4.py` — both exploratory, neither in the
> pre-registration) established two things this document gets wrong:
>
> 1. **§2's claim that "the intent encoder is decoupled from the deception
>    objective" is WITHDRAWN.** Intent is worth **+0.171 DSR** (regime A) and
>    **+0.148** (regime B), measured as `best_fixed → profile oracle`. It is
>    strongly coupled. What is worth ≈0 is a *perfect sequence model on top of a
>    3-way profile label*: **+0.0005 DSR**.
> 2. **Five of the six arms never beat a memoryless fixed action.** Only
>    GRU/action does (p = 0.021–0.050, all four regimes). Both Transformer arms
>    are indistinguishable from playing one decoy forever, so the H9–H12 nulls
>    are not evidence that the architectures are equivalent.
>
> The verdict is therefore **not** "attention ties recurrence." It is *"the
> experiment could not tell them apart, for two independent and now-measured
> reasons."* See `VERDICT.md`.

Pre-registration committed as **`7499d29`**, before this experiment was run.
60/60 runs complete (6 arms × 10 paired seeds, 2.0 h). Every declared contrast is
reported below, as promised.

---

## 1. Verdict

**H9, H10, H11 and H12 are all NOT SUPPORTED. No declared contrast reached
significance.** The artefact-corrected Transformer does not beat the GRU on
Deception Success Rate.

| Contrast | Regime | Δ DSR | 95% CI | *d* | p_holm |
|---|---|---|---|---|---|
| H9-B RoPE+action vs GRU+action | B | −0.0200 | [−0.062, +0.022] | −0.30 | 1.000 |
| H9-A same | A | −0.0200 | [−0.064, +0.024] | −0.28 | 1.000 |
| H10-D same | D | −0.0150 | [−0.038, +0.008] | −0.41 | 1.000 |
| H10-C same | C | −0.0235 | [−0.065, +0.018] | −0.35 | 1.000 |
| H11-T action vs next (Transformer) | B | −0.0110 | [−0.046, +0.024] | −0.20 | 1.000 |
| H11-G action vs next (GRU) | B | +0.0155 | [−0.006, +0.037] | +0.44 | 1.000 |
| H12-B RoPE vs sinusoidal | B | −0.0020 | [−0.038, +0.034] | −0.03 | 1.000 |
| H12-D RoPE vs sinusoidal | D | +0.0080 | [−0.015, +0.031] | +0.21 | 1.000 |

DSR by arm (mean ± 95% CI, n = 10):

| History encoder | Objective | A | B | C | D |
|---|---|---|---|---|---|
| Transformer-RoPE | action | 0.452±0.028 | 0.430±0.024 | 0.429±0.026 | 0.365±0.016 |
| Transformer-RoPE | next | 0.469±0.025 | 0.441±0.024 | 0.442±0.023 | 0.368±0.019 |
| Transformer-Sin | action | 0.459±0.026 | 0.432±0.027 | 0.436±0.027 | 0.358±0.023 |
| Transformer-Sin | next | 0.443±0.033 | 0.422±0.034 | 0.424±0.035 | 0.365±0.029 |
| **GRU** | **action** | **0.473±0.035** | **0.450±0.034** | **0.453±0.035** | **0.380±0.024** |
| GRU | next | 0.455±0.029 | 0.435±0.030 | 0.436±0.028 | 0.366±0.023 |

Every CI overlaps every other. The GRU is nominally ahead everywhere, by margins
smaller than their own confidence intervals.

**Power:** n = 10 detects only *d* ≥ 1.00; every observed |*d*| ≤ 0.44. The
p-values therefore cannot exclude a small effect — but the CIs bound it. Any true
Transformer advantage on DSR-B is **at most +0.022**.

---

## 2. The result that matters more than the verdict

**Every encoder improvement established in Phase 2 failed to transfer to DSR.**

| Improvement | Encoder-level gain (Phase 2) | DSR effect (Phase 4) |
|---|---|---|
| Rotary vs sinusoidal PE | **+0.026 to +0.070** Top-1 | **−0.002** (H12-B) |
| Action vs next objective | **+0.067** action-decodability | **−0.011 / +0.016** (H11) |
| Equal-budget tuning | closed a **0.139** CAM-LDS gap | no DSR effect |

This is the third independent measurement of the same phenomenon:

1. **Phase 1 / v3:** intent accuracy vs DSR, *r* = −0.175 (p = 0.18) — no relationship.
2. **v3:** the best next-technique predictor (GRU, 0.558) gave the *worst* DSR;
   the worst predictor (Transformer, 0.361) gave the best.
3. **Phase 4 (here):** improving the encoder by every available measure moves DSR
   by approximately zero.

**The intent encoder is decoupled from the deception objective in this
environment.** That is a mechanism claim about the thesis's central pipeline, and
it is now supported by three separate lines of evidence rather than one
correlation.

The mechanism metric corroborates it: the GRU achieves the highest step
alignment (0.319 ± 0.023 under the action objective vs 0.279 ± 0.051 for RoPE),
yet the DSR difference remains inside the noise. Better alignment is not
converting into better containment.

---

## 3. On the v3 → v4 comparison

The analysis prints:

```
v3 (sinusoidal, next, L=16, untuned) : Transformer - GRU on DSR-B = +0.0205
v4 (rotary, action, L=8, tuned)      : Transformer - GRU on DSR-B = -0.0200
shift                                : -0.0405
```

**This shift must not be read as "the correction made things worse."** Both
endpoints are non-significant quantities whose CIs span zero, measured under
different configurations; their difference is noise-on-noise. It is reported for
completeness, not as a finding.

It does, however, correct something I previously asserted: on DSR with the
DeepSets network encoder, the v3 history Transformer was already nominally
*ahead* (0.459 vs 0.439). **The claim that "the Transformer never won across four
tests" was too strong** — on the DSR metric the history encoders were always
within noise of each other, in both v3 and v4.

---

## 4. What can now be claimed, and what cannot

### Defensible

1. **The CAM-LDS encoder deficit was substantially our own artefact.** The
   reported GRU advantage of +0.1388 (*d* = 1.65, p_holm = 5.7e-14) was measured
   on a Transformer handicapped by absolute sinusoidal PE at untuned defaults.
   With rotary position and an equal 16-trial tuning budget the gap is
   **+0.0000**, with the Transformer at **44% of the GRU's parameters**.
2. **On deception success the two architectures are indistinguishable**, with any
   Transformer advantage bounded above by +0.022 DSR.
3. **The intent encoder does not drive deception success in this environment** —
   three independent lines of evidence, above.
4. **Two candidate explanations are refuted, not merely unsupported:** data scale
   (gap widens, −0.0187/decade) and context length (longer is worse; L = 8 best).
5. **A methodological finding worth reporting on its own:** at 150 training steps
   RoPE scored 0.472 and looked broken; at 1,200 steps it led at 0.886. Training
   length can invert an architecture ranking, so any short-run architecture
   comparison — including several of our own earlier ones — is unreliable.

### Not defensible

- That the Transformer beats the GRU, on CAM-LDS next-technique prediction
  (it ties) or on DSR (all contrasts null).
- That better attacker-intent modelling improves deception performance. Measured
  three ways, it does not.
- The title's implied claim that the Transformer is what makes TEMARL work.

---

## 5. Honest answer to the question that was asked

The task was to give the Transformer its strongest legitimate chance and report
the outcome honestly. Six artefacts were tested; two were real and were removed;
the corrected Transformer then **tied** on the CAM-LDS encoder task at less than
half the parameters, and **did not win** on the deception objective.

Under the success criteria set out in advance, this is the third listed outcome:
*the Transformer does not win, and we can say precisely why, with the effect
bounded rather than merely undetected.* The bound is +0.022 DSR.

It is not the outcome the thesis title wants. It is a defensible one, and the
route to it — a pre-registered test of six named confounds, two of which
overturned a previously headline result — is stronger evidence than the original
claim ever was.

---

## 6. Limitations

1. **n = 10 detects only *d* ≥ 1.00.** Small DSR effects are not excluded by the
   p-values; the CIs, not the p-values, carry the argument.
2. **One environment, one attacker model.** The attacker is a scripted CAM-LDS
   profile sampler. A learning attacker might reward intent modelling differently.
3. **The attacker profiles still derive from the older hand reconstruction**
   (`camlds_grounding.json`), not the Phase-1-corrected file — the two use
   incompatible schemas. Every DSR number rests on the reconstruction-derived
   attacker.
4. **The scaling curve tops out at N = 10,000** usable windows, so the
   very-large-data regime is untested.
5. **`upgrade.yml` is missing** for 12 of 36 CAM-LDS runs (Phase 1), so a third
   of the corpus has known-incomplete content.
6. **The DSR proxy chain** — action-decodability was used as a cheap stand-in for
   DSR in Phase 2.6, and Phase 4 shows that proxy did not transfer. Any future
   use of it should account for that.
