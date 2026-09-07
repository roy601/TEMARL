# TEMARL — What the thesis can claim, and the evidence for each

Every claim below is stated in the exact form it should appear in the thesis,
with its evidence, its statistical test, and its limitation. Nothing here is
softer or stronger than the data supports.

Written 2026-09-08. The v6 replication (§2) was still running; that section is
marked and must be completed before submission.

---

## The headline

> **Attention achieves statistically equivalent deception performance to
> recurrence at 44% of the parameters**, on a task demonstrably capable of
> rewarding sequence modelling, with learners demonstrably capable of learning
> it.

This is a **positive** claim — equivalence, not a failure to find a difference —
and it is what the title's "Transformer-Enhanced" can honestly mean: matched
capability at less than half the parameter cost.

---

## 1. Primary claim — demonstrated equivalence at 44% of the parameters

**Statement.** The Transformer-RoPE history encoder achieves deception success
statistically equivalent to the GRU, using 156,310 encoder parameters against
351,702 — **44.4%, or 2.25× fewer**.

**Test.** TOST (two one-sided tests), equivalence margin 0.02 DSR, declared as
the smallest difference that would plausibly change a deployment decision. n = 10
paired seeds, 200 evaluation episodes each.

| Regime | Δ (T − GRU) | p_TOST | Verdict |
|---|---|---|---|
| A canonical 5-zone | −0.0010 | **0.0001** | **EQUIVALENT** |
| B new topologies, trained sizes | −0.0060 | **0.0124** | **EQUIVALENT** |
| C unseen structure | −0.0055 | **0.0029** | **EQUIVALENT** |
| D unseen sizes (9/11/13 zones) | +0.0045 | 0.0527 | bounded below 0.0203 |

**Why this is a positive result.** A non-significant NHST cannot separate "no
effect" from "too small a study." TOST can. p = 0.0001 at the canonical topology
is a stronger statistical statement than most positive results in this
literature.

**Limitation to state.** Equivalence is demonstrated at a 0.02 margin, not at
zero; regime D reaches only "bounded below 0.0203." Cost is 2–2.5× wall-clock
(115–126 s vs 48–64 s per run).

**Source.** `equivalence_v5.py`, `results_v5/equivalence_v5.json`.

---

## 2. Entity attention at unseen topology sizes — REPLICATION PENDING

**v5 result (pre-registered, reported as declared).** GRU/EntityTransformer vs
GRU/DeepSets at unseen sizes: Δ +0.0180, *d* = 0.61, two-sided **p_holm =
0.690, NOT SIGNIFICANT**. 90% CI [+0.0009, +0.0351].

**Status.** Underpowered, not refuted: n = 10 has 80% power only for *d* ≥ 1.00.
Power analysis gives n = 24 (80%), **n = 31 (90%)**, n = 38 (95%).

**Replication.** Pre-registered in `prereg_v6.py` (commit `7261a4a`) at
n = 31 **fixed in advance**, fresh seeds 100–130 disjoint from v5's, one
pre-declared contrast, one-sided (direction predicted in advance by
arXiv:2410.17647). Reports the independent replication *and* the pooled n = 41
estimate, whatever they show.

> **⚠ FILL IN BEFORE SUBMISSION.** If the replication is significant, this
> becomes a second positive claim with independent published corroboration. If
> not, the pooled estimate is the final word and this claim is retired — the
> thesis then rests on §1 and §3–5, which is sufficient.

**Integrity note that must appear in the thesis.** The v5 data, re-tested
one-sided, gives p = 0.0431. **That number must never be quoted as a result.**
v5 was pre-registered two-sided with Holm correction and stands at p_holm =
0.690. A one-sided test is valid only for the fresh v6 seeds, where the
direction was fixed before the data existed.

---

## 3. Methodological contribution — a headroom gate can pass while the task is degenerate

**Statement.** A pre-registered environment-validation gate can pass while the
environment is incapable of discriminating the hypotheses under test.

**Evidence.** The v4 gate asked *"is intent information worth anything?"* —
δ = 0.2698, a clear pass. It never asked *"is **sequence** information worth
anything beyond a class label?"* — which measures **+0.0001** expected payoff
(+0.0005 DSR). The optimal decoy was constant within a campaign: 84/84 techniques
for two campaigns, 83/84 for the third. No history architecture could have been
distinguished on that task, however good.

**Consequence.** v4 spent 60 arms and 2 GPU-hours producing 8 null contrasts
that carried no information about attention vs recurrence.

**Source.** `instrument_analysis.py`, `baselines_entity.py`,
`results_v4/VERDICT.md`.

---

## 4. Methodological contribution — architecture comparisons need a baseline ladder and a validity gate

**Statement.** A null result between trained arms is uninterpretable without
(a) a reference ladder placing the numbers on a scale and (b) a validity gate
proving each arm learned the task.

**Evidence.** In v4, **5 of 6 arms never beat a memoryless fixed action**; only
GRU/action did (p = 0.021–0.050), capturing 11–21% of available headroom. The
pre-registered analysis reported the architecture contrasts without checking
this. In v5, with the gate declared and reported *first*, **5 of 5 arms passed**
(p ≤ 0.0018, 62–77% of headroom) — so v5's null is evidence and v4's was not.

**The ladder** (`baselines_entity.py`): null / random / best-fixed /
campaign-oracle / transition-oracle / clairvoyant.

---

## 5. Data contribution — a source-verified CAM-LDS grounding and its audit

**Statement.** The CAM-LDS grounding was rebuilt by parsing the 36 published
AttackBed playbooks directly, and five parser defects were found and fixed across
two rounds, the second via an independently written second parser.

| | |
|---|---|
| Playbooks / runs | 36 |
| Labelled technique steps | **1,347** (was 1,339) |
| Campaigns | 7 |
| Parent techniques / tactics | **82** / 13 |
| Kish effective *n* | **3.09** — 36 runs ≈ 3 independent campaigns |
| I(τ′;τ) in raw sequences | **4.83 bits**, 85.4% predictable |

**Defects fixed.** Round 1: singular `tactic:` in two files (dropped a whole
campaign); `.j2`/`.j2.yml` double-counting. Round 2: a block-order bug
(`tactics:` before `techniques:` emitted nothing — lost T1190, T1059.004, T1095)
and two inline-`#`-comment bugs (lost 1× T1222.002, 4× T1219).

**Vocabulary** extended append-only 78 → 84; the 6 added techniques were **6.20%
of all instances silently falling to UNK**. Payoff extended by the identical
D3FEND rule with rows 0–77 verified **bit-identical**. Never refitted.

**Claims explicitly withdrawn** (state these; they appeared in earlier drafts):
- "82 techniques / 13 tactics match Table 3 **exactly**" — the match was an
  artefact of the bugs cancelling. It is 82 against the paper's 81.
- "The reconstruction invented T1095" — T1095 is real at `scenario_7.j2:95`.
  Reconstruction precision is 100%, not 98.7%.
- "COMISET is 1156× larger" — 98.5% self-loops; 23,754 usable windows; **≈18×**.

---

## 6. Data contribution — an estimator defect that destroyed 87% of the corpus's sequential structure

**Statement.** The attacker-model estimator added a column-constant to every row
of the campaign transition matrix, which carries zero information about the
transition by construction and outweighed the real bigram evidence ~2:1.

```python
T[:, j] += 1.2   # added identically to EVERY row
```

| | before | after removal |
|---|---|---|
| I(τ′;τ \| campaign) | 0.627 bits | **1.935 bits** (raw data: 4.83) |
| Sequence value, payoff | +0.0002 | **+0.1776** |
| Sequence value, DSR | +0.0005 | **+0.0800** |
| Distinct optimal actions per campaign | 1.33 | **4.33** |

**Verified single-factor change:** restoring the constant to 1.2 reproduces the
v2 profiles **bit-for-bit** (max diff 0.000e+00).

**Not outcome-tuning:** a 2×2×2 factorial over {class granularity} × {estimator}
× {goal drift} tested three candidate repairs. Two were **rejected** — backoff
smoothing (−0.0588) and finer class granularity (−0.0305) — because they
*reduced* sequence value, despite both having been predicted to help.

---

## 7. What must NOT be claimed

- That the Transformer **beats** the GRU on deception success. It does not, in
  any regime, with or without entity attention.
- That the crossover result (Transformer winning at unseen sizes) is real. It
  was an n = 3 pilot; at n = 10 it is Δ +0.0045, *d* = 0.17, p_holm = 1.000.
- That the width-matched control established the effect was architectural. That
  control was also n = 3; at n = 10 GRU-d32 is nominally the *best* arm.
- That improved intent modelling does not help deception. **Intent is worth
  +0.148 to +0.171 DSR.** What buys ≈0 is a better *sequence* model on top of a
  campaign label.
- Any v5 number re-tested one-sided (see §2).

---

## 8. Limitations to state plainly in Chapter 5

1. **Training is behaviour cloning on the transition oracle, not RL.** Under PPO
   no arm cleared the memoryless baseline at any budget tried (240 eps → 0.510,
   1,200 eps → 0.523, baseline 0.5475). v2 also trained by imitation, so there
   is precedent — but a result under BC is a statement about **encoder quality
   under matched supervision**, not about multi-agent RL.
2. **Why PPO fails here is unresolved.** Two hypotheses were tested and both
   were false: reward/metric misalignment (corr(return, DSR) = **+0.983**) and
   PPO's agent-averaged log-prob collapse (fixing it made DSR *worse*, 0.5400 →
   0.5167). A third is measured but untested: the composite action's target
   dimension is provably irrelevant to reward — every legal target of the
   responsible agent is necessarily in-zone — yet contributes ~1.17 bits/agent of
   variance to the PPO ratio.
3. **n = 10 detects only *d* ≥ 1.00.** Every observed |*d*| ≤ 0.61.
4. **Effect sizes here are smaller than seed noise at n = 3.** Two
   mutually-confirming n = 3 results both evaporated at n = 10. Report seed SD
   beside any pilot effect.
5. **One environment, one scripted attacker.** A learning attacker could change
   the structure of the task entirely.
6. **Attacker profiles derive from the older hand reconstruction**
   (`camlds_grounding.json`), not the Phase-1-corrected file; the schemas are
   incompatible.
7. **The v5 environment is calibrated, not free.** `goal_steps=3`,
   `cap_scale=0.35` were selected from a 20-cell grid against four criteria fixed
   in advance using baseline policies only — but a different calibration might
   give a different answer.

---

## 9. Provenance — the audit trail an examiner will check

| Commit | Content |
|---|---|
| `7499d29` | v4 pre-registration, committed **before** the v4 run |
| `1413afb` | v5 pre-registration + instrument repair, **before** the v5 run |
| `0c25e12` | v5 confirmatory result, all 8 contrasts reported |
| `15fbf61` | Phase 1/2/4/5 corrections propagated into v3-era documents |
| `7261a4a` | Equivalence testing + v6 pre-registration, **before** the v6 run |

Every pre-registration is committed before its experiment. Every declared
contrast is reported. Two failed hypotheses and two withdrawn n = 3 claims are
recorded rather than deleted.
