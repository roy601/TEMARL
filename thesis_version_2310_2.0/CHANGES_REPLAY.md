# Changes from thesis_version_2310

1. replay_data.py adds strict label loading, source matching, duplicate grouping,
   deterministic split assignments, counts and cross-split similarity reporting.
2. scripts_marl.py now supplies scenario metadata only. Removed chain estimation
   from the live attacker path. Historical objective and target rules are retained.
3. env_marl.py uses whole playbook sequences, paired with independently drawn
   simulator uniforms. EpisodeSpec records run ID, full source labels and split.
   Run selection cycles deterministically; no technique order is shuffled. The
   previous uniform-scenario sampling is replaced by uniform-run cycling.
4. pretrain_marl.py creates windows once per original train/validation run.
   Optimization resamples these existing windows. Fixed optimization budget is
   retained, though fewer independent examples may increase overfitting.
   Final prediction testing uses the held-out test runs after training.
5. mappo.py uses separate playbook partitions for policy training, checkpoint
   validation and final testing, rather than merely different random seeds.
6. run_experiment.py audits provenance before training and stores the split audit
   in the run manifest. LOSO is disabled because the old runner would not implement
   a valid separate replay LOSO protocol. Main six arms and controls are unchanged.
7. report_results.py retains requested deception/ablation tables and adds held-out
   prediction percentages. It identifies repetition, variant overlap and limits.
8. Added replay tests and validate_replay.py; adjusted obsolete Markov identity
   assertion and unsupported LOSO test. Existing architecture and mechanic tests
   remain. No training run has been used to validate or tune this new design.
9. Bundled official AttackBed source and parser. Parser output is a local candidate
   file and cannot overwrite frozen grounding. Archived obsolete docs/baselines/
   gates; omitted caches, checkpoints and previous results from active outputs.
10. Added portable lab instructions and optional PowerShell launcher.
11. Added human-readable prediction examples to RESULTS.md: matched histories,
    actual next labels, technique names, top-three probabilities and correctness.
    Example selection is fixed by run position and shared seed, not accuracy.
    Each cell saves every held-out prediction; reports also explain deception
    metrics in plain English. These additions do not change model training.

Unchanged: encoders_marl.py, env_config.json, experiment.py, frozen dependency
files and payoff, MARL network definitions and PPO update equations. Environment
step/observation/reward/termination logic is unchanged; added run/split statistics.

Exact replay does not validate physical executability of a technique on the zone
chosen by the simulator. Engagement, movement, asset protection and the objective
definition remain modeled outcomes. The older calibrated constants were retained,
not retuned for replay. Historical performance/headroom gates are not claimed to
pass in this new attack distribution; learning quality must be measured afresh.
