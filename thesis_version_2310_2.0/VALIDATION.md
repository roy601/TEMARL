# Validation of the replay bundle

Checked locally on 2026-09-21 using Python 3.12 and PyTorch 2.4.1+cpu.

- Official source-label comparison: 36/36 playbooks, 1,347 instances matched.
- Vocabulary: zero unknown labels after the unchanged parent-technique mapping.
- Split: 25 training, 5 validation, 6 test runs; no identical full sequences
  cross splits at either source-label or parent-ID resolution.
- Replay/bundle tests: 19 passed, without a training run, including probability
  output, source-label matching and fixed-example Markdown rendering.
- Existing environment mechanic assertions: 27/27 passed.
- Frozen input hashes and payoff equality: passed.
- All 15 active top-level Python files parsed successfully.
- Encoder architecture, environment config, experiment specification,
  requirements and frozen-integrity module match the original files by hash.

No encoder pretraining, PPO training, smoke experiment or full experiment was
started. Tests exercise inference, gradients, exact replay and hand-built
environment cases; they do not establish learning performance. CUDA has not
been tested on this machine. Run the optional smoke experiment on the lab PC
before the long run.

The held-out test has 237 next-technique targets, including 36 instances of
parent labels absent from training (15.19%). Validation has 177 targets and
zero unseen labels. This affects achievable prediction accuracy and must be
reported rather than fixing the split after seeing results. Near-duplicate
variants and shared windows are another limitation; see the data audit.

Previous Markov-distribution performance gates and previous result values are
not validated for replay. The source folder has not been modified.
