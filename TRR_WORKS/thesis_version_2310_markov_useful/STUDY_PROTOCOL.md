# Markov usefulness experiment

Prepared 2026-10-08. No scientific outcome is assumed or promised.

## Question

Does the inherited Markov generator improve next-technique prediction and
downstream adaptive deception on held-out original playbook sequences?
This tests usefulness conditional on this corpus, split, model and budget.
It cannot prove that synthetic data is necessary in every setting.

## Generator

Scenario-conditioned, time-homogeneous, first-order categorical Markov chains.
The current observed technique is the state. There are no hidden states,
no learned higher-order memory, no MCMC and no goal drift.

For 84 parent-technique IDs:

    P(j | i,s) = (0.02 + 4*C_s(i,j)) / (84*0.02 + 4*sum_k C_s(i,k))
    P(first=j | s) = (0.02 + 2*start_count_s(j)) / (84*0.02 + 2*n_runs_s)

The constants and `scripts_marl.estimate_chain` are inherited unchanged.
Fit on training runs ONLY. Select a training-run template uniformly, use its
scenario and length, then draw the technique path from that scenario's chain.
This preserves the training run-frequency mixture and length support. The old
environment instead sampled scenarios uniformly; this intentional sampling
change makes the new augmentation dose a supplement to the original corpus.

Smoothing gives positive probability to unobserved transitions and even
techniques absent from that scenario's training data. Those outcomes are
assumptions, not newly discovered facts. No execution/causal/AEP validity claim
is made. AEP validity is reported N/A; adjacency resemblance is named as such.

## Data and splits

- Source: 36 AttackBed-derived playbooks, 1,347 labeled steps, seven scenarios.
- Preserve source order and repetitions. Existing parent-technique vocabulary
  is retained; sub-techniques remain recorded in the loaded source metadata.
- Group identical encoded sequences before any prediction windows or sampling.
- Fixed seed 2310; scenario-stratified approximately 60/20/20 split.
- Scenarios with fewer than three independent groups stay training-only.
- Cross-scenario duplicate groups stay training-only in the main split.
- Report exact groups, achieved counts, support gaps and nearest-train bigram
  Jaccard similarity; near-duplicate variants remain a limitation.
- Windows are causal prefixes of at most 16 tokens. An existing long playbook
  does not become a longer-context model; the inherited window is unchanged.
- Test and validation contain original playbooks only. Different environment
  random seeds do not create additional independent campaigns.
- Frozen vocabulary, D3FEND payoff, scenario goals and environment calibration
  were designed using the earlier corpus. New training isolation does not undo
  that historical design exposure; this is not a prospective external test.

## Epoch selection

An encoder epoch is one pass through every training prediction window, once,
with shuffling, including the last partial minibatch. It is not one RL rollout.

Default `--epochs auto`:

1. Fit real-only pilots for Transformer, GRU and LSTM at seeds 101, 102, 103.
2. Each pilot completes 100 epochs, evaluated on validation after every epoch.
3. Find each pilot's lowest-validation-NLL epoch (earliest on exact ties).
4. Set ONE shared budget to the maximum of those nine selected epochs.
5. Restart every main model from fresh initialization and complete that budget.
6. Use the final common-epoch checkpoint for primary prediction tests and RL.
   Also save and report the validation-best checkpoint as secondary analysis;
   it can have a different selected epoch. Neither choice uses test results.

The pilot is a practical budget rule, not proof all augmented models converge.
If any selected epoch is in the last 10% of the pilot, the report warns that
the cap may be insufficient. A larger cap is a new declared protocol/output;
never choose it by looking for better test results. An explicit `--epochs 50`
uses exactly 50 for all main conditions and skips the selection pilot. Fifty
is an example, not a claim that 50 is scientifically sufficient.

Same epochs with more windows mean MORE optimizer updates. Repeat controls
repeat only original training windows to EXACTLY match each augmentation
condition's window count and per-epoch update count. They add no information.
The training report records counts and updates, so extra optimization is visible.

## Prediction study

- Three unchanged encoders, ten main training seeds (0 through 9).
- Real-only data-size conditions: 25%, 50%, 75%, 100% of training groups.
  Nested subsets within a seed; retain at least one group per scenario.
  Report achieved data sizes rather than presenting nominal ratios as exact.
- Augmentation: full original training set plus 25%, 50%, 100%, 200% additional
  synthetic sequences. Ratios use original sequence counts, rounded up.
- Four repeat controls match each augmented window count. There are 12
  conditions x 3 encoders x 10 seeds = 360 prediction cells, plus nine pilots.
- Same generated sequences within a seed/dose for every encoder; dose samples
  are nested. The test set and validation set are identical across cells.
- Pooled order-0/order-1 diagnostic baselines use only training data and no
  privileged test scenario identity. Order comparison does not silently switch
  the generator. AIC/BIC are omitted for the non-MLE weighted smoothed fit.
- Report Top-1/3/5, macro-F1 over test-supported labels, NLL, log likelihood,
  perplexity, run-macro Top-1, per-run results, probabilities and examples.
- Accuracy equals Top-1. Prediction examples use fixed evenly spaced window
  indices, not cherry-picked correct cases. Probability is not calibrated certainty.

## Downstream deception study

Use the supplied fixed five-zone environment, all four defenders, existing
decoy actions, reward, capacity coupling, exposure and breadcrumbs unchanged.
This is not the earlier variable-topology v3 environment.

For real-only, +100% Markov and repeat-100, run all six combinations:
Transformer/GRU/LSTM x IPPO/MAPPO, with ten seeds. Add original-only NoHistory
IPPO and MAPPO controls: 200 policy cells total.

Policy training samples the corresponding finite original or original+synthetic
corpus. The repeat control uses the original policy-training corpus because
uniformly repeating it adds no distributional information. Every policy has
the same 2,000,000 requested environment-step budget, realized as 1,998,848
steps with inherited 64x64 rollouts, and 10 PPO epochs per rollout. Encoders
are frozen. Validation is every fixed rollout checkpoint, not an encoder epoch.

Validation evaluates every held-out validation run with ten environment repeats;
test evaluates every held-out test run with fifty environment repeats, using
matched seeds across policies. Store run IDs and repetition IDs with outcomes.
Episode sequence order is fixed; defense may change movement/engagement or end
an episode early, but cannot invent its next technique or extend its sequence.

Report dwell steps, interaction depth in distinct parent techniques, protection,
exposure, lures, dead ends, capacity violations, episode length and deployment
counts. Show the six combinations and validation-selected real-only ablation.
The augmentation condition changes both predictor data and policy episodes;
its effect is a full-system effect. It does not isolate the predictor alone.

## Inference and decision rule

Primary prediction metric: held-out Top-1. Pair seeds for each augmented dose
versus real-only and versus its dose-matched repeat control. Holm correct the
24 comparisons. Report mean differences, 95% paired t intervals and p-values.
A candidate practical benefit requires positive intervals, corrected p<0.05,
and at least 0.01 absolute Top-1 gain against both controls. Results remain
conditional on a small fixed test corpus; seed replication does not replace
independent campaign replication.

For the downstream test, dwell is primary; depth/protection are also reported.
Correct all 36 model/learner/control/metric contrasts as a separate family.
Assess whether engagement gains trade off asset protection; never infer better
deception from prediction accuracy alone. Quality diagnostics do not certify
generated paths as executable. Null results remain valid study outcomes.

## Optional LOSO

`--held-out S1` (through S7) holds a whole scenario out before any fitting.
All matching duplicate groups are held out together. Every fold needs a separate
output directory and its own training/validation pilot; results are per-fold.
Report label-support gaps. Seven separate reports are not a pooled independent
sample: do not treat folds x seeds x rollouts as independent trials.

## Output and resume

`RESULTS.md` links every measured epoch, raw per-seed/run table, RL curve and
readable prediction table. JSON artifacts store the generated corpora, split,
probabilities, checkpoint hashes, budgets, environment metadata and provenance.
Completed cells are resumed only after config/code/checkpoint checks. Interrupted
cells restart from initialization; completed cells are not retrained. A `.running`
lock prevents concurrent writers. Remove a stale lock only after checking that
its recorded process is no longer running. New code/config requires new output.
Smoke reports are explicitly excluded from scientific conclusions.
