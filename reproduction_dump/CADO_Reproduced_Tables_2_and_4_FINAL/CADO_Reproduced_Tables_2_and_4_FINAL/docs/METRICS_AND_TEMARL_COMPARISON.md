# Experimental methods, metrics, and fair TEMARL comparison

## Research design

The author's simulator (`publisher_source/code/run_experiments.py`) sets `MASTER_SEED=20260818`, `N_SEEDS=30`, `EVENTS_PER_EPISODE=120`, and `BOOTSTRAP_RESAMPLES=10000`. Three scenarios (`office`, `research`, `data_service`) and four in-distribution attackers (`credential`, `lateral`, `web`, `hybrid`) form the primary grid. A `slow_blend` attacker is held out for the additional OOD experiment. Policies are `Static`, `Adaptive`, `Consensus`, and `CADO`; ablation variants are also included. The synthetic event generator uses reproducible separate RNG streams derived from the master seed.

The source explicitly separates policy-visible alert fields from the simulator's latent malicious label and ideal deception action, which are used only to score outcomes. This design constraint matters when porting TEMARL: do not leak simulator ground-truth fields to the defender.

## Deception levels

0. **Observe** — no deception exposure.
1. **Honeypoint** — a limited lure.
2. **Honeyproxy** — redirection into a decoy path.
3. **Honeytrace** — deeper engagement/tracing.

## Reported outcomes

The main archived primary Table 2 and held-out comparison use: defensive utility, redirection precision, engagement rate, benign false-redirect rate, unsafe action rate, and normalized resource cost. Values are computed per episode and then averaged per paired seed. Primary means and bootstrap confidence intervals are provided in `tables/table2_primary_independently_reproduced.csv`. Held-out means, paired differences, confidence intervals and tests are in `tables/table4_heldout_independently_reproduced.csv`.

The author's bootstrap uses 10,000 resamples of the **30 seed-level means**, not 120-event observations treated as independent replicates. We did not replace the original statistical code.

## Suggested TEMARL benchmark protocol

1. Preserve the CADO episode generator and exact seed/attacker/scenario schedule.
2. Map TEMARL defense actions to the same four levels before scoring, or implement an explicitly justified mapping of CADO into the TEMARL environment.
3. Use exactly the same observation fields as a CADO policy; do not expose `malicious`, `ideal`, or `capture_draw` to TEMARL.
4. Fix training, validation and evaluation split boundaries; exclude the held-out `slow_blend` attacker from TEMARL training.
5. Evaluate both policies on paired episodes and report mean, bootstrap 95% CI, paired-difference CI, nonzero pairs, Holm-corrected p-values, utility, precision, false redirects, unsafe actions and cost.
6. Label any architecture/parameter changes as independent adaptations rather than exact reproductions. Report poor or divergent results transparently.

## Limitations

These outcomes are synthetic. CADO does not provide a trained MARL policy, checkpoint or replay-network weights. Its source is policy code, not a learned model. The official paper and uploaded supplementary archive are the evidentiary sources; this document's TEMARL guidance is our recommended adaptation plan, not something already executed.
