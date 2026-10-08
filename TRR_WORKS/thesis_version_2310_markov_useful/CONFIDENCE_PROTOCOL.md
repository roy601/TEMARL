# Confidence ablation protocol and paper backing

## Question and scope

Does providing calibrated predictive uncertainty to the actor's existing fusion
gate improve deception compared with the same gate receiving a constant?
This is a project-specific intervention, not a reproduction of a published
confidence-aware honeypot algorithm. An improvement is not assumed.

This experiment is enabled by default after the Markov study. It uses the
real_100 encoders only, to avoid confounding uncertainty with augmentation.
Use `--no-confidence-ablation` to omit it explicitly, or `--prediction-only`
to omit all policy training. Existing Markov experiments remain separate.

## Paired design

For each Transformer/GRU/forget-gate LSTM, IPPO/MAPPO, and ten seeds:

| Property | Baseline | Confidence-aware |
|---|---|---|
| Encoder | Same frozen real_100 checkpoint | Identical checkpoint |
| Actor | Local observation + 64-D history embedding | Same |
| Existing scalar gate input | Constant 0.5 | Calibrated normalized prediction entropy |
| Actor parameter count | Identical | Identical |
| Critic | Original inputs | Identical; no added entropy input |
| Training | Same original training runs and seed | Same |
| Budget | Same environment steps and PPO epochs | Same |
| Validation/test | Same held-out run specs and environment random numbers | Same |
| Policy selection | Highest validation dwell | Same |

Total: 120 additional policy cells, not 120 new encoder trainings. The policies
are trained anew for both sides; existing results from another code version are
not substituted. The extra entropy slot already existed in the fusion network.
This tests the value of an explicit uncertainty feature, not an increase in size.
Episodes can terminate differently under different actions, so trajectories may
diverge despite matched initial specs and random-number tables.

## Equations and calibration

From frozen encoder logits z over the 84 valid technique labels:

```text
T = argmin validation mean[-log softmax(z/T)[actual_next_label]]
p = softmax(z/T)
u = -sum_k p_k log(p_k) / log(84)
gate_input = u                     # confidence-aware
gate_input = 0.5                   # baseline
```

Positive T is fitted with bounded scalar minimization of log(T) in [-4,4].
T=1 is the fallback if it achieves lower validation NLL. Both arms use the same
embedding; temperature changes only the probability distribution used for the
extra scalar, never the encoder weights. PAD/UNK logits are excluded. At empty
history, the embedding is zero and u=1 (an explicit conservative convention).
Only the observed prefix enters probability calculation. The true next technique
is used for offline calibration/scoring, never as a policy observation.

Validation is reused for encoder epoch selection, temperature fitting and policy
selection because the corpus is small. This is disclosed, not an independent
calibration assessment. Test runs remain untouched by fitting/selection.
Report held-out NLL, multiclass Brier score, Top-1 and 10-bin ECE before/after
scaling. Calibration need not improve on test data. Temperature scaling does
not alter the predicted argmax. Predictive entropy is not epistemic uncertainty
or a guarantee of correctness.

## Confidence-group diagnostics

Prediction groups use low/medium/high `1-u` with validation-window tertile
thresholds. Report counts, accuracy and mean certainty on test windows.
These certainty scores are not probabilities that the prediction is correct.

Policy groups use each fixed playbook's mean prefix certainty, excluding empty
history. Thresholds are validation-playbook tertiles. Group membership is fixed
for both policies, regardless of early termination. Full-playbook certainty is
only an offline grouping variable, not an input available during an episode.
Report all existing metrics within groups, with seed-level means and SDs.
Empty groups remain N/A; ties may create uneven groups. These are descriptive
associations: differences in scenario, attack difficulty and lengths can explain
group performance. They do not establish a causal confidence effect.

## Outcomes and statistics

Primary outcome: held-out mean dwell per seed. Six predeclared paired contrasts:
confidence minus baseline for each encoder x learner combination. Report mean
difference, paired-t 95% interval, two-sided p and Holm-corrected p across six.
Inference is withheld for n=1; Holm is withheld until all six contrasts have all
requested seeds. Individual intervals are not simultaneous adjusted intervals.
Small seed counts and correlated playbook variants limit inference.

Also report episode reward (sum of actual environment rewards), interaction
depth, asset protection, exposure, lure chains, dead ends, capacity violations,
episode length and decoys deployed. Protected/exposed aggregate columns use
percentages. Raw per-seed/episode records use fractions. There is no newly
invented generic "deception success rate": engagement and protection are distinct.
The retained environment's reward equals dwell; these two columns are redundant,
not independent evidence. The environment regression test confirms this identity.

## Paper and implementation audit

| Part | Source | What the source supports / limit |
|---|---|---|
| Temperature scaling | [Guo et al., ICML 2017](https://proceedings.mlr.press/v70/guo17a.html) | Calibration by a positive scalar fitted on validation NLL; does not establish benefits in our RL task. |
| Learned fusion | [Arevalo et al., GMU, 2017](https://arxiv.org/abs/1702.01992) | Gated combination of representations. Adding predictive entropy and using LayerNorm/ReLU branches are our adaptations, not the paper's original equations. |
| Transformer | [Vaswani et al., 2017](https://arxiv.org/pdf/1706.03762) | Scaled dot-product attention, multi-head projection, residuals, post-normalization and FFN. Explicit numeric checks now cover attention and a full encoder layer. Shallow dimensions, ATT&CK tokens, last-prefix pooling and extra final LayerNorm are adaptations. |
| PPO | [Schulman et al., 2017](https://arxiv.org/pdf/1707.06347) | Clipped surrogate. A test checks both advantage signs and clipping directions in the actual loss helper used by training. |
| GAE | [Schulman et al.](https://arxiv.org/abs/1506.02438) | Advantage recursion. Tests cover terminal reset and nonterminal rollout bootstrap in the actual training helper. |
| MAPPO | [Yu et al.](https://arxiv.org/abs/2103.01955) | Centralized training and local execution; our history-conditioned actors/environment are adaptations. |
| IPPO | [de Witt et al.](https://arxiv.org/abs/2011.09533) | Independent/local-value PPO comparison. Current policy sharing and shared observed history are disclosed choices. |

Entropy normalization and threshold selection are explicit project design choices.
No cited paper demonstrates this exact confidence-conditioned deception system.
Model equations, modern LSTM backing, and remaining limitations are also recorded
in [MODEL_EQUATION_REVIEW.md](MODEL_EQUATION_REVIEW.md).

## Code and output

- `confidence_ablation.py`: calibration, prefix entropy, paired study and reports.
- `mappo.py`: optional entropy routing in rollout/update/evaluation; critic unchanged;
  actual episode-return recording; testable PPO and GAE helpers.
- `test_confidence.py`: entropy, calibration, equal capacity, ignored baseline
  feature, critic isolation, future-token leakage, PPO, GAE and Transformer checks.
- `run_markov_study.py`: integrated default confidence experiment.
- `run_lab.ps1`: full tests and fresh timestamped output folders.

`RESULTS.md` links the confidence outputs and marks the whole study incomplete
until its confidence cells also finish. `CONFIDENCE_RESULTS.md` contains aggregate,
paired, calibration, confidence-group and every-seed tables.
`CONFIDENCE_DETAILS.md` contains every calibration bin, recorded policy validation
point, and test episode. `EPOCH_RESULTS.md` retains every encoder epoch.
JSON/checkpoints are retained for machine-readable provenance. There is no claim
to log every optimizer minibatch or every training episode.

Use a fresh output folder: code fingerprints changed. Prior runs are not overwritten
or compatible with this updated experiment. Actor checkpoints for the confidence
study include mode, temperature and encoder hash; they are inference artifacts,
not full optimizer/critic training-resume snapshots.

## Verification completed

- 35 combined bundle, Markov-study and confidence tests passed on CPU.
- 27 environment checks passed separately.
- End-to-end CPU smoke completed 9 prediction cells, 20 existing policy cells
  and 12 confidence-ablation cells; two encoder epochs and 16 policy steps per
  smoke cell. This is an execution check, not performance evidence.
- Verified 12/12 confidence result fingerprints, episode reward/dwell identity,
  and nonempty main, epoch, confidence summary and confidence detail reports.
- [Smoke confidence report](results_markov/confidence_integration_smoke/CONFIDENCE_RESULTS.md).
- CUDA/full-budget execution remains for the lab PC. No full experiment ran here.
