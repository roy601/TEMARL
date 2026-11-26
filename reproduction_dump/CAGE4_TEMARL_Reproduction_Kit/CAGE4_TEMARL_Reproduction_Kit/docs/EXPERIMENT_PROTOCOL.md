# Reproduction and comparison protocol

## Phase 1: reproduce actual CAGE 4 baseline numbers

1. Install pinned upstream revisions in an isolated Python 3.11 environment.
2. Run two episodes (smoke) of each baseline; inspect stderr, score, agent validity, and checkpoints.
3. Run 100 × 500 episode official evaluation for PUNCH and Cybermonic, one command per policy. Record seeds, package versions, CPU/GPU, all logs and git commits.
4. Compare published standard reward: PUNCH -142 ± 44, Cybermonic -193 ± 84 (values rounded as in journal Table 3; underlying submission README lists -142.72 and -193.68 respectively). Assess differences, do not force matching numbers.
5. Investigate and report version differences and statistical uncertainty. Without original score distribution and exact experiment revision, matching rounded averages alone is not proof of strict reproduction.

## Phase 2: legitimate TEMARL comparison

1. Expose CAGE 4's **five blue agents** (note: different from CAM-LDS's four zone agents) to TEMARL via a registered `Submission.AGENTS` class and a wrapper that preserves the official observation and action semantics. Include communication constraints.
2. Map TEMARL output head to actual CAGE 4 legal blue actions (Sleep, Monitor, Analyse, DeployDecoy, Remove, Restore, BlockTraffic, AllowTraffic), respecting agent-specific action masks and durations. **Do not map all 6 CAM-LDS decoy categories to CAGE action indices directly.**
3. Train TEMARL in the CAGE environment using training seeds disjoint from evaluation seeds; freeze the encoder during RL only if consistent with the declared experiment. No-history and static/random baselines must use the same scenario and budgets.
4. Fix reward, evaluation horizon, red agents, action constraints, version and seed-generation protocol across methods. Run both unmodified published agents and TEMARL under this matching protocol.
5. To study **deception** rather than only total defense reward, instrument executed Blue `DeployDecoy` actions, Red interactions with deployed decoys, and decoy discovery; define denominators and duration. Some outcomes will need careful simulator introspection. Do not substitute 'number of DeployDecoy actions' for 'successful deception.'
6. Report total CAGE reward + decoy engagement events/rates + attacker goal success + actions/cost, with per-episode distributions and multiple seeds. Clearly separate paper-reproduction metrics from your novel metrics.
7. Only once standard baseline reproduction is trustworthy, consider the paper's five modified environments. Document exact patch provenance; do not claim paper-equivalent robustness results from unverified hand-built variants.

## Readiness

- Original PUNCH v1 source: publicly released and pinned (download by bootstrap).
- Original Cybermonic source & weights: publicly released and pinned (download by bootstrap).
- Original CAGE 4 simulator and scoring implementation: publicly released and pinned (download by bootstrap).
- **TEMARL running in CAGE: not implemented**.
- Reproduced published numbers: **not run**.
- Exact official journal Table 3 experiment revision/seed/variation patches: **not fully verified**.

This kit intentionally does not invent experimental outcomes.
