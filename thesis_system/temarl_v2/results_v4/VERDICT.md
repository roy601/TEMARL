# The Verdict

*Written after `PHASE4_FINAL_RESULT.md`, and it supersedes that document's
central interpretation. Everything below is **exploratory** — it is not part of
`prereg_v4.py` (commit `7499d29`), adds no declared contrast and drops none. The
pre-registered result stands exactly as reported. What changes is what it means.*

---

## 0. The one-sentence verdict

**The thesis's central hypothesis was never testable in this environment, and
separately, five of the six arms that were meant to test it never learned the
task — so the Phase 4 null is not evidence that attention ties recurrence; it is
evidence that the experiment could not tell them apart.**

Two independent facts establish this. Either alone would be sufficient.

---

## 1. The environment cannot reward sequence modelling

The reference ladder (`baselines_entity.py`, 10 seeds × 200 episodes, same env
seed stream as the trained arms):

| Policy | A | B | C | D | information used |
|---|---|---|---|---|---|
| null | 0.315±0.022 | 0.309±0.022 | 0.311±0.020 | 0.303±0.020 | none (floor) |
| random | 0.424±0.023 | 0.409±0.017 | 0.399±0.022 | 0.350±0.018 | none |
| **best_fixed** | **0.454±0.029** | **0.434±0.028** | **0.434±0.027** | **0.362±0.027** | **none — no history, no intent** |
| **profile** | **0.625±0.021** | **0.582±0.022** | **0.582±0.017** | **0.447±0.024** | **perfect 3-way profile label** |
| **transition** | **0.625±0.020** | **0.583±0.021** | **0.583±0.016** | **0.447±0.024** | **perfect NEXT-TECHNIQUE model** |
| clairvoyant | 0.661±0.019 | 0.620±0.022 | 0.618±0.018 | 0.480±0.021 | the realised technique (unattainable) |

Read the two bold middle rows against each other.

**A perfect next-technique model is worth +0.0005 DSR over a three-way profile
label. In every regime.**

The reason is structural, not statistical. The optimal decoy is constant within
a campaign profile:

| profile | distinct optimal actions over its 84 reachable techniques |
|---|---|
| decoy_persona | **2** (decoy_persona for 83 of 84) |
| decoy_file | **1** (decoy_file for all 84) |
| decoy_credential | **1** (decoy_credential for all 84) |

In expected-payoff terms:

| information level | payoff | over best-fixed |
|---|---|---|
| best-fixed (no information) | 0.3584 | — |
| profile known | 0.7426 | **+0.3842** |
| + perfect next-technique model | 0.7427 | **+0.3843** |

**Value of knowing the profile: +0.3842. Value of sequence modelling on top of
that: +0.0001 — 0.0% of it.**

The task is three-way classification wearing a sequence costume. No history
architecture can distinguish itself on it, however good. The Transformer was not
beaten; it was never given anything to win.

### Where this came from

The profiles are *named after their own optimal responses* —
`decoy_persona`, `decoy_file`, `decoy_credential`. That is not a coincidence:
`consolidate_intent_classes()` in `d3fend_payoff.py` merged the seven CAM-LDS
scenarios into intent classes **grouped by which decoy is optimal for them**.
The consolidation that made the environment's headroom gate pass is the same
step that destroyed the technique-level structure a sequence model would need.

And note the pre-registered gate did not catch this, because it was not built to.
`payoff_headroom_min = 0.15` asks *is intent information worth anything?*
(answer: 0.2698, a clear pass). It never asks *is intent information worth
anything beyond a class label?* — which is the thesis's actual question.
**The gate passed while the environment was degenerate for the hypothesis under
test.** That is a design lesson worth reporting on its own.

---

## 2. Five of six arms never beat a constant action

Every arm, paired against `best_fixed` on the same 10 seeds
(`verdict_v4.py`). `capture` is the fraction of available intent headroom
(`best_fixed → profile oracle`) that the arm actually took.

| history encoder | objective | regime | arm DSR | vs fixed | capture | 95% CI | p |
|---|---|---|---|---|---|---|---|
| Transformer-RoPE | action | A | 0.452 | −0.0015 | −0.9% | [−0.044, +0.041] | 0.946 |
| Transformer-RoPE | action | B | 0.430 | −0.0040 | −2.7% | [−0.045, +0.037] | 0.852 |
| Transformer-RoPE | action | C | 0.429 | −0.0045 | −3.0% | [−0.045, +0.036] | 0.832 |
| Transformer-RoPE | action | D | 0.365 | +0.0030 | +3.6% | [−0.020, +0.026] | 0.805 |
| Transformer-RoPE | next | A | 0.469 | +0.0155 | +9.1% | [−0.003, +0.034] | 0.134 |
| Transformer-Sin | next | B | 0.422 | −0.0120 | −8.1% | [−0.042, +0.018] | 0.446 |
| **GRU** | **action** | **A** | **0.473** | **+0.0185** | **+10.9%** | **[+0.006, +0.032]** | **0.021** |
| **GRU** | **action** | **B** | **0.450** | **+0.0160** | **+10.8%** | **[+0.002, +0.030]** | **0.050** |
| **GRU** | **action** | **C** | **0.453** | **+0.0190** | **+12.8%** | **[+0.004, +0.034]** | **0.035** |
| **GRU** | **action** | **D** | **0.380** | **+0.0180** | **+21.3%** | **[+0.005, +0.031]** | **0.025** |
| GRU | next | B | 0.435 | +0.0005 | +0.3% | [−0.023, +0.024] | 0.967 |

*(Full 24-row table in `results_v4/verdict_v4.json`.)*

**4 of 24 arm×regime cells beat a memoryless fixed action, uncorrected — and all
four are the same arm, GRU + action objective.** Both Transformer arms, in every
regime, are statistically indistinguishable from playing one decoy forever.

So the Phase 4 contrast H9-B — "Transformer-RoPE/action vs GRU/action" —
was a comparison between an arm that learned nothing and an arm that learned
about a tenth of what was available. That contrast returning *p* = 1.000 tells us
nothing about attention versus recurrence.

---

## 3. What this overturns in `PHASE4_FINAL_RESULT.md`

That report's headline mechanism claim was:

> **The intent encoder is decoupled from the deception objective in this
> environment.**

**That is wrong, and I am withdrawing it.** Intent is worth **+0.171 DSR** in
regime A and **+0.148** in regime B (best_fixed → profile oracle). It is very
strongly coupled to the objective. Three corrections follow:

1. What is decoupled is *marginal encoder quality*, not intent — and only because
   the intent that matters is a 3-way label that both architectures already
   reach, while a perfect sequence model adds +0.0005 on top.
2. The *r* = −0.175 correlation and "the best next-technique predictor gave the
   worst DSR" now have a mechanism rather than being a curiosity: those
   correlations were measured across a set of policies **none of which was using
   the encoder** — five of six sit at the memoryless baseline. A correlation
   computed over policies that all ignore the variable is uninformative about it.
3. The bound "any true Transformer DSR advantage is at most +0.022" stands
   arithmetically but should not be quoted as an architecture result. It is a
   bound on a difference between two arms, at least one of which did not learn.

---

## 4. What can be claimed

### Defensible, and now better supported than before

1. **The task, as constructed, cannot discriminate sequence architectures.**
   Quantified: perfect next-technique prediction is worth +0.0005 DSR / +0.0001
   payoff over a three-way class label. This is a property of the environment,
   measured, not an inference from a null.
2. **The previously reported CAM-LDS Transformer deficit was our own artefact.**
   +0.1388 (*d* = 1.65, p_holm = 5.7e-14) → **+0.0000** at 44% of the GRU's
   parameters, once rotary position and an equal 16-trial tuning budget were
   applied to both arms. This stands, and it is the strongest single result in
   the project.
3. **Two candidate explanations are refuted, not merely unsupported:** data
   scale (gap widens, −0.0187/decade) and context length (L = 8 best).
4. **One arm did learn:** GRU + aligned action-objective pretraining beats a
   memoryless fixed action in all four regimes (p = 0.021–0.050), capturing
   11–21% of available headroom. Small, real, and reportable.
5. **A pre-registered headroom gate can pass while the environment is degenerate
   for the hypothesis under test.** Ours did. The gate asked whether intent is
   worth anything; it never asked whether *sequence* information is worth
   anything beyond a class label.
6. **Training length can invert an architecture ranking** (RoPE: 0.472 at 150
   steps, 0.886 at 1,200) — so short-run architecture comparisons, including
   several of our own, are unreliable.
7. **Three real parser defects** in the AttackBed reconstruction, found and
   fixed; corrected corpus statistics; Kish effective *n* = 3.09, i.e. 36 runs
   are ≈ 3 independent campaigns.

### Not defensible

- That the Transformer beats the GRU — on CAM-LDS (it ties) or on DSR (null).
- That the Transformer *ties* the GRU on DSR **as an architecture finding**. The
  arms tie because neither used intent, not because they are equivalent.
- **That better attacker-intent modelling does not improve deception.** The
  opposite is true and now measured: +0.148 to +0.171 DSR. Our agents just did
  not capture it.
- The title's implied claim that the Transformer is what makes TEMARL work.

---

## 5. The two honest paths forward

### Path A — retitle and report the negative result *(recommended)*

Nothing new needs to be run. The contribution becomes:

> *Why attention does not help attacker-intent modelling in honeypot deception:
> a pre-registered null with an identified mechanism.*

It carries four things a positive result would not have: an environment-level
proof that the task cannot discriminate the architectures (+0.0005), a
demonstration that our own prior headline result was a configuration artefact,
a reusable diagnostic ladder, and a design lesson about headroom gates. This is
publishable as methodology and reproducibility work, and it is defensible under
examination in a way the original claim never was.

### Path B — make the task discriminative *(future work, new pre-registration)*

For a sequence model to be able to win, the optimal response must depend on
*where in a campaign* the attacker is, not only *which* campaign it is. That
requires intent classes **not defined by their own optimal action** (the current
consolidation groups scenarios by optimal decoy, which is the root cause) and a
payoff whose argmax varies across techniques within a class.

**This is future work and must not be done inside this thesis.** `payoff_frozen.json`
is frozen, and redesigning the environment after seeing that the Transformer lost
is precisely the forbidden move. If it is ever done, the justification is *"the
task must be able to discriminate the hypotheses"* — established here, before any
redesign — and never *"so the Transformer wins."* It needs its own
pre-registration, and the null reported here stands regardless of its outcome.

---

## 6. Limitations of this verdict

1. **Exploratory.** None of section 1 or 2 was pre-registered. The
   pre-registered result is unchanged; this reinterprets it.
2. **The paired test in section 2 is uncorrected** across 24 cells. Holm would
   only weaken it — and it is already a null for 20 of 24, so correction does
   not change the conclusion. The four GRU/action cells sit at p = 0.021–0.050
   and would not all survive correction; the claim "one arm learned something"
   rests on their consistency across four regimes, not on any single p-value.
3. **`clairvoyant` peeks** at the technique the env is about to emit by cloning
   and restoring the RNG state. It is a bound, not an attainable policy.
4. **Why the arms failed to learn is not established here.** Candidates: a 600-episode
   PPO budget, the frozen two-timescale encoder, credit assignment through a
   single responsible agent, or the composite action space. The v2 pipeline
   reached ~0.60 DSR, but by **imitation learning against the profile oracle**
   (`train_v2.py`, `IL_EPISODES = 1200`), i.e. it was handed the answer — so it
   is not evidence that RL can find this policy either.
5. **One environment, one scripted attacker.** A learning attacker would change
   the structure of section 1, possibly a great deal.
6. **The attacker profiles still derive from the older hand reconstruction**
   (`camlds_grounding.json`), not the Phase-1-corrected file; the schemas are
   incompatible. Every DSR number here rests on that reconstruction.
