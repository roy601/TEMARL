# CasinoLimit full architecture runner

Read SIMULATION_ENVIRONMENT.md before interpreting results. This folder adds
a simplified trace-replay allocation environment and reuses the repository's
IPPO/MAPPO trainer. Keep this folder inside the full TEMARL repository.

Run tests: `python casinolimit_real_full_arch/test_pipeline.py`

Smoke run: `python casinolimit_real_full_arch/pipeline.py --smoke --train-missing`

Full GPU run: `python casinolimit_real_full_arch/pipeline.py --device cuda --train-missing`

Results: `casinolimit_real_full_arch/results/main/RESULTS.md`.
Training curves and per-episode outcomes: each cell's `result.json`.
The original recorded corpus and five splits are reused without modification.
The existing checkpoints are absent on this PC; --train-missing explicitly
reconstructs missing encoders using the existing CasinoLimit budget. Smoke
checkpoints are isolated in the smoke output directory and never used for full runs.

This is not the old CAM-LDS honeypot environment. Actions are machine-local
decoy off/on and the outcome model is uncalibrated. Asset protection, adaptive
attacker rerouting and real deception effectiveness are not established.
