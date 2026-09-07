# Phase 5 — Final Result on the Repaired Instrument

Pre-registration committed as **`1413afb`**, before this experiment ran.
50/50 runs complete (5 arms × 10 paired seeds, 6,856 s). Every declared contrast
is reported below, as promised — including the two whose direction the pilot had
already contradicted.

---

## 1. Verdict

**H16, H17, H18 and H19 are all NOT SUPPORTED. No declared contrast reached
significance.** With a task that demonstrably rewards sequence modelling, and
five arms that demonstrably learn, attention confers no measurable advantage over
recurrence on Deception Success Rate.

| Contrast | Regime | Δ DSR | 95% CI | *d* | p_holm |
|---|---|---|---|---|---|
| H16-D Transformer vs GRU, unseen sizes | D | +0.0045 | [−0.0124, +0.0214] | +0.17 | 1.000 |
| H16-C same, unseen structure | C | −0.0055 | [−0.0134, +0.0024] | −0.43 | 1.000 |
| H17-B same, trained sizes | B | −0.0060 | [−0.0162, +0.0042] | −0.36 | 1.000 |
| H17-A same, canonical | A | −0.0010 | [−0.0073, +0.0053] | −0.10 | 1.000 |
| H18-D Transformer vs width-matched GRU-d32 | D | −0.0055 | [−0.0231, +0.0121] | −0.19 | 1.000 |
| H18-B same | B | −0.0015 | [−0.0182, +0.0152] | −0.06 | 1.000 |
| H19-DT EntityTransformer vs DeepSets (Transf.) | D | −0.0055 | [−0.0239, +0.0129] | −0.18 | 1.000 |
| **H19-DG EntityTransformer vs DeepSets (GRU)** | D | **+0.0180** | [−0.0003, +0.0363] | **+0.61** | 0.690 |

DSR by arm (mean ± 95% CI, n = 10):

| History | Network | A | B | C | D |
|---|---|---|---|---|---|
| Transformer-RoPE | DeepSets | 0.654±0.026 | 0.604±0.026 | 0.603±0.029 | 0.487±0.029 |
| GRU | DeepSets | 0.655±0.027 | 0.610±0.029 | 0.608±0.031 | 0.482±0.022 |
| GRU-d32 | DeepSets | 0.652±0.027 | 0.606±0.032 | 0.605±0.029 | 0.492±0.027 |
| Transformer-RoPE | EntityTransformer | 0.652±0.027 | 0.608±0.024 | 0.607±0.028 | 0.481±0.027 |
| **GRU** | **EntityTransformer** | 0.657±0.026 | **0.618±0.027** | 0.613±0.030 | **0.500±0.027** |

Five architectures span **0.011 DSR** at unseen sizes and **0.005** at the
canonical topology.

---

## 2. Why this null is worth incomparably more than v4's

**The validity gate passed 5 of 5** — the check v4 never had, and would have
failed:

| History | Network | DSR-B | vs best_fixed | headroom | p |
|---|---|---|---|---|---|
| Transformer-RoPE | DeepSets | 0.6040 | +0.0565 | 61.7% | 0.0004 |
| GRU | DeepSets | 0.6100 | +0.0625 | 68.3% | 0.0000 |
| GRU-d32 | DeepSets | 0.6055 | +0.0580 | 63.4% | 0.0018 |
| Transformer-RoPE | EntityTransformer | 0.6075 | +0.0600 | 65.6% | 0.0001 |
| GRU | EntityTransformer | 0.6175 | +0.0700 | 76.5% | 0.0001 |

| | v4 | v5 |
|---|---|---|
| Sequence value in the task | +0.0005 | **+0.0800** |
| Arms beating a memoryless baseline | **1 of 6** | **5 of 5** |
| Headroom captured | ~11% | **62–77%** |
| Transformer − GRU on DSR-B | −0.0200 | −0.0060 |
| Widest CI on the main contrast | ±0.042 | **±0.021** |

v4's null was uninterpretable: the task could not reward sequence modelling and
the arms had not learned. **This null is interpretable.** The task rewards
sequence modelling 160× more strongly, every arm clears the memoryless baseline
by p ≤ 0.0018, and the effect is bounded inside **±0.007 DSR** at the canonical
topology.

That tight CI is the result. It is not "we failed to detect a difference"; it is
**"any difference is smaller than 0.007 DSR."**

---

## 3. Cost, and the one thing the Transformer does win

| History encoder | Encoder params | Train time | Alignment (B) |
|---|---|---|---|
| Transformer-RoPE | **156,310** | 115–126 s | 0.403–0.408 |
| GRU | 351,702 | **48–64 s** | **0.418–0.420** |

The Transformer matches the GRU's DSR at **44% of the parameters** — the Phase
2.4 finding, now confirmed on the deception objective rather than only on
next-technique prediction. It pays for that with **2–2.5× the wall-clock** and
slightly *lower* step alignment.

---

## 4. Two claims I made during this work and have to withdraw

Both were made on n = 3 and both were wrong. They are recorded because the record
should show them.

**(a) "The Transformer wins at unseen topology sizes."** The pilot measured
Δ = +0.0333 with headroom 82–90% vs 27–31%. At 10 seeds it is **+0.0045**,
*d* = 0.17, p_holm = 1.000 — an eighth the size. Regime-D seed variance
(SD ≈ 0.068) was larger than the effect being claimed.

**(b) "The confound is dead; the effect is architectural."** The width-matched
control appeared to settle it at n = 3 (GRU-d32 27.6% vs Transformer 82.2%). At
n = 10 GRU-d32 reaches **79.8%** — nominally the *best* of the three. The control
run was noise as well. The confound question was never resolved by that run; it
dissolved because there is no effect to attribute.

The lesson generalises to the whole project: **n = 3 was inadequate for every
claim built on it**, including the ones that appeared to confirm each other.

---

## 5. An exploratory lead (LABELLED EXPLORATORY, not a result)

The largest effect in the family is **H19-DG**: the GRU with an
**EntityTransformer** network encoder, at unseen sizes — Δ = +0.0180, *d* = 0.61,
p_holm = 0.690, CI [−0.0003, +0.0363]. That arm captures **93.9%** of the
unseen-size headroom, the best of the five, and is nominally best at every regime.

It is **not significant** and no claim rests on it. But it is the only contrast
whose CI is nearly clear of zero, and its direction matches the entity-attention
half of arXiv:2410.17647 — attention over *entities in varying topologies*,
rather than over the attacker's technique history. If any part of this thesis
deserves a follow-up with more power, it is that one, and it would need its own
pre-registration.

---

## 6. What the thesis can now claim

### Defensible

1. **Attention confers no advantage over recurrence for attacker-intent
   modelling in honeypot deception**, on a task that demonstrably rewards
   sequence modelling, with learners that demonstrably learn — bounded within
   ±0.007 DSR (canonical) to ±0.024 (unseen sizes), across 5 architectures and
   8 Holm-corrected contrasts.
2. **The Transformer matches the GRU at 44% of the parameters**, at 2–2.5× the
   wall-clock.
3. **A pre-registered headroom gate can pass while the environment is degenerate
   for the hypothesis under test.** The v4 gate asked "is intent worth
   anything?" (0.2698, pass) and never asked "is *sequence* information worth
   anything beyond a class label?" (+0.0001). That is a reusable methodological
   finding.
4. **An architecture comparison is meaningless without a baseline ladder and a
   validity gate.** v4 ran 60 arms and 2 GPU-hours to produce a null that could
   not distinguish "both good" from "neither learned." Five of its six arms had
   not beaten a constant action.
5. **The estimator defect is real and quantified.** A column-constant added to
   every row of a transition matrix destroyed 87% of the corpus's sequential
   information; removing it raised within-campaign I(τ′;τ) from 0.627 to 1.935
   bits and the sequence value from +0.0002 to +0.1776 payoff.
6. **Effect sizes in this domain are smaller than seed noise at n = 3.** Two
   mutually-confirming n = 3 results both evaporated at n = 10.

### Not defensible

- That the Transformer beats the GRU on deception success — on any regime, at
  any topology size, with or without entity attention.
- That the earlier crossover result was real.
- The title's implied claim that the Transformer is what makes TEMARL work.

---

## 7. Limitations

1. **n = 10 detects only *d* ≥ 1.00.** Every observed |*d*| ≤ 0.61. The CIs, not
   the p-values, carry the argument.
2. **Training is behaviour cloning on the transition oracle, not RL.** Under PPO
   no arm cleared the memoryless baseline at any budget tried, so the comparison
   was not possible there. v2 also trained by imitation, so this has precedent —
   but a result under BC is a statement about **encoder quality under matched
   supervision**, not about multi-agent RL.
3. **Why PPO fails here is unresolved.** Two hypotheses were tested and both
   were false: reward/metric misalignment (corr = +0.983) and PPO's
   agent-averaged log-prob collapse (fixing it made DSR *worse*). A third
   candidate is measured but untested: the composite action's target dimension
   is provably irrelevant to reward yet contributes ~1.17 bits/agent of variance
   to the PPO ratio.
4. **One environment, one scripted attacker.** A learning attacker could change
   the structure of the task entirely.
5. **The attacker profiles derive from the older hand reconstruction**
   (`camlds_grounding.json`), not the Phase-1-corrected file; the schemas are
   incompatible.
6. **The v5 environment is calibrated, not free.** `goal_steps=3` and
   `cap_scale=0.35` were selected from a 20-cell grid against four criteria fixed
   in advance using baseline policies only — but a different calibration might
   give a different answer.
