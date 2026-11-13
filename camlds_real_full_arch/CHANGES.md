# Integration changes

Original folders were not edited.

- `env_cmd.py`: copied command replay simulator; changed NT to the new 81-label vocabulary, remapped payoff rows by ATT&CK strings, and remapped goal masks through those strings. All observation offsets are computed with 81. No unknown technique fallback.
- `mappo_cmd.py`: copied PPO/IPPO/MAPPO implementation; history tensor NT comes from the 81-label port. Actor/critic structure, hyperparameters and training equations unchanged.
- `pipeline.py`: uses existing encoder implementations, split definitions and metrics. Supplies executed-record sequences instead of the old playbook reconstruction, excludes unsupported firewall scenario from RL, selects reconciled ordering by default, handles checkpoints, paired episode randomness, reports and cell resume.
- `test_pipeline.py`: audits counts, label-to-payoff mapping, split disjointness, execution rank integrity, exact consumed prefixes, termination, input shapes, no-future history, frozen encoders and matched episode uniforms.

The dataset metadata retains original technique sets and provenance. Default ordering changes require new encoder training. The old CSV-order checkpoint study can be reproduced with explicit `--order frozen` in a separate output folder.

No full training or scientific evaluation has been performed for this new package. CPU smoke cells have tiny artificial training budgets; they establish that the integration executes, not that it learns an effective defense.
