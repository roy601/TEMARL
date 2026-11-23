# CAGE 4 reproduction kit for TEMARL — baseline phase

**Status: supplied execution scaffold, offline unit-tested, NOT a completed reproduction; requires Internet, Git, Python 3.11, a compatible PyTorch/Ray environment, and sufficient computing resources.**

This kit automates pinning the three official repositories and attempting standard CAGE 4 evaluations of **PUNCH Analyse-Restore v1** and **Cybermonic KEEP** with the **original, unmodified CAGE 4 evaluator**. It stores the run logs and generates a comparison CSV. The zip also carries your original CAM-LDS TEMARL source archive **as reference only**, not as a working CAGE 4 policy. It does not claim that TEMARL has been ported/trained in CAGE 4.

## Quick start

For the most compatible environment, use Ubuntu 22.04 / WSL2 with Python 3.11 and Git. Internet access is required to clone the original repositories and install dependencies. Extract the entire ZIP to a working directory.

```bash
bash START_LINUX.sh
```

Windows PowerShell alternative (may encounter native PyTorch Geometric/Ray packaging issues):

```powershell
.\START_WINDOWS.ps1
```

**These commands perform a 2-episode smoke test first, not a scientific reproduction.**

If the automated dependency installation hits an upstream version incompatibility, the script fails and shows the error: this package does **not** conceal it by quietly substituting a different method. Resolve dependency conflicts in a separate virtual environment and document any deviation.

For the published **100 × 500-step** standard benchmark after a successful smoke:

```bash
# activate .venv first
python run_baselines.py --agents all --episodes 100 --seed 12502
python make_comparison.py
```

Outputs: `results/{punch,cybermonic}/episodes_100_seed_12502/summary.json`, `runner.log`, `invocation.json`; and `results/comparison.csv`. See `docs/EXPERIMENT_PROTOCOL.md` before making claims.

## Repository sources (read and pinned 2026-11-22)

* https://github.com/cage-challenge/cage-challenge-4 — official CybORG / CAGE 4 evaluator, `external/cage`.
* https://github.com/PUNCH-Cyber/cage-4-submissions — `punch_analyse_restore_v1` source, `external/punch`.
* https://github.com/cybermonic/cage-4-submission — KEEP + five `weights/gnn_ppo-*.pt` checkpoints, `external/cybermonic`.

Exact commit hashes are in `sources.json`, checked after clone. These repositories and their licenses are not redistributed inside the ZIP; instead, the kit downloads them from the original maintainers and keeps their code unmodified. Consult the upstream licenses (Apache-2.0 for PUNCH; GPL-2.0 for Cybermonic) before redistribution.

## Gaps and scientific limits

1. **No evaluation was executed in this restricted build environment** (external GitHub source clone and pip download were unavailable). We cannot label the reproduced values as achieved.
2. **No CAGE 4 TEMARL trained agent** is in this kit. Your CAM-LDS `env_cmd.py` / `mappo_cmd.py` use different zones, observations, and a different action space. A new CAGE 4 policy interface, training, and evaluation are still required.
3. The pinned CAGE mainline revision is **not verified as the exact version used for Table 3**. Therefore numerical differences could arise from versions, random seeds, policy wrappers, or dependencies. The published table is used as an external target, never as an observation.
4. Upstream dependency specifications differ (`torch_geometric` 2.5.0 in the CAGE requirements vs 2.3.1 in Cybermonic); setup takes upstream requirements in sequence and reports failures. Validate Python/GPU/PyTorch compatibility and maintain a version lockfile once resolved.
5. **Reproducing published reward is not automatically a deception comparison**. PUNCH's analyse/restore strategy is not a honeypot-first policy. Need a matched extension for decoy deployment, attacker interactions, cost, and success rates; see protocol.
6. `--seed` is an evaluator initialization seed. Using the same value for two agents does **not** guarantee step-by-step paired stochastic outcomes because their actions change simulator trajectories.
7. `summary.json` reports mean and sample standard deviation under the official evaluator's reward aggregation, not episode-level traces. Distinguish `std` from standard error; do not claim confidence intervals without the per-episode distribution.
8. Avoid comparing **original CAM-LDS or CasinoLimit rewards** to **CAGE 4 reward values**. Compare only agents tested in the same benchmark environment with aligned settings.

## Internal files

- `bootstrap.py`: clone and verify pinned upstream sources; optional dependency install.
- `preflight.py`: source/checkpoint/import sanity check.
- `run_baselines.py`: run original evaluation for PUNCH and KEEP, save logs and metadata.
- `make_comparison.py`: emit CSV only from successfully finished runs.
- `tests/`: offline tests for command construction and result reporting.
- `reference/CAM_LDS_TEMARL_SOURCE_UNMODIFIED.zip`: unchanged upload supplied by you; **not** a CAGE adaptation.
- `docs/EXPERIMENT_PROTOCOL.md`: required plan for a proper paper comparison.

## References

- Journal Table 3: https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021
- Official CAGE 4 docs: https://cage-challenge.github.io/cage-challenge-4/
- PUNCH repository: https://github.com/PUNCH-Cyber/cage-4-submissions
- Cybermonic repository: https://github.com/cybermonic/cage-4-submission
