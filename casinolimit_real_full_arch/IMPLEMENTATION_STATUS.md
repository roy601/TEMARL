# CasinoLimit full architecture: implementation status

Status: runnable simplified replay allocation implementation added in pipeline.py.
See README.md and SIMULATION_ENVIRONMENT.md for the implemented scope. The list
below preserves the original audit requirements; not every research extension
listed below is implemented (notably static/random baselines, clean-trained fog
transfer, empirical calibration, and statistical summary testing).

## Verified source

Use the exact corpus loaded by `casinolimit_encoder/cl_port.py`:
`casinolimit_real/out/steps.jsonl`, LF-normalized SHA-256
`399ef563db0223a5fe85d8668ed6fce925fbd43240f79ef7c9b0bc9cbe823c2d`.
Reuse the five whole-instance splits from `casinolimit_encoder/cl_split.py`.
The corpus contains recorded, labelled human CTF activity. Defender responses
are absent and must be identified as simulation assumptions.

## Required arms

Both existing Transformer variants (`allpos`, `baseline`), `gru_allpos`,
`lstm_allpos`, Kuwano recommendation adapter, and NoHistory control; each with
IPPO and MAPPO, ten seeds and five folds. Evaluate fog probabilities 0, .5, .9.
Kuwano is a deterministic recommender, not a neural encoder. Its adapter must
document label coverage, similarity-one treatment, score scaling and feature
dimensions. Do not silently describe an adapted recommender as an exact
reproduction of its original prediction experiment.

## Problems found in a direct CAM-LDS copy

- `env_cmd.py` imports CAM-LDS vocabulary, zone definitions and payoff rows.
- Scenario entry/target/goal metadata comes from CAM-LDS, not CasinoLimit.
- Its movement model invents next zones and breadcrumb rerouting; these cannot
  be represented as CasinoLimit's recorded movement.
- `mappo_cmd.py` imports NT from CAM-LDS `port`, whereas CasinoLimit has 66 labels.
- Cached history is keyed by run ID. Episode-dependent fog needs an observation
  mask-aware cache or fresh masked history; otherwise fog tests can leak data.
- Fog must hide both local telemetry and shared encoder history, with visibility
  masks recorded; hiding only the local vector leaves a privileged history channel.
- Absent recorded decoy interventions prevent empirical calibration of engagement
  and protection. Simulator sensitivity tests are required, not fabricated calibration.
- Intranet coverage is too sparse for a strong intranet-protection conclusion.

## Required implementation and verification

1. Audit corpus hash, split disjointness, machine IDs and Kuwano label coverage.
2. Load the existing per-fold, per-seed CasinoLimit checkpoints, validate their
   validation BCE and source metadata; explicitly train missing checkpoints using
   the frozen CasinoLimit budget, not the CAM-LDS budget.
3. Build a command replay environment preserving recorded command/machine order.
   Define resource allocation, costs, intervention outcomes and metric denominators
   in SIMULATION_ENVIRONMENT.md before obtaining results.
4. Use past-only policy inputs and separate random streams for visibility and
   engagement. Match test episodes and random seeds across arms.
5. Implement the Kuwano adapter using the released algorithm and declare every
   adaptation. Report unsupported techniques, never invent ATT&CK mappings.
6. Connect IPPO/MAPPO; keep encoders frozen and test gradient isolation.
7. Evaluate clean-trained policies at 0/50/90 percent telemetry masking as the
   primary robustness test. Any fog-trained policies must have separate results.
8. Add static/random allocation baselines and NoHistory. Report per-instance
   episode outcomes, fold/seed summaries, encoder metrics, and training curves.
9. Test exact replay, exhaustion, no future leakage, fog in all input channels,
   seed pairing, checkpoint compatibility, resumption and finite PPO updates.
10. Run all-arm smoke tests before providing the full lab command. Full experiments
    have not been started. This document is not evidence of working software.
