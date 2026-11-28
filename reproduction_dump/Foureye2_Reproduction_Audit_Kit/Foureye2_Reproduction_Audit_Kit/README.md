# Foureye 2 — Controlled Original-Code Reproduction Kit

**Paper:** Z. Wan et al., *Resisting Multiple Advanced Persistent Threats via Hypergame-Theoretic Defensive Deception*, IEEE Transactions on Network and Service Management, 20(3), 3816–3830 (2023). DOI: https://doi.org/10.1109/TNSM.2023.3240366

**Author code:** https://github.com/Wan-ZL/Foureye-2-simulation

**Audited public branch HEAD (2026-11-23):** `8b6f02961e5f7202e094f9c25514c9e5a65ee4b4` (2023-08-26).

## Status

**NOT YET EXPERIMENTALLY REPRODUCED.** The authoritative GitHub code was inspected via the GitHub repository connector, but the complete repository bytes are not mounted in this execution environment and external GitHub downloads are not possible here. Consequently the actual original simulation was **not executed** and no published numbers have been reconstructed. Five tests of **this harness**, not of the paper's code, passed.

The original public repository contains attacker, defender, network, game, training, and output-generation scripts. However, it does **not** contain the serialized `.pkl` classifier files referenced for the ML-assisted methods, or the raw `.pkl` output used by plotting scripts. These artifacts can potentially be regenerated, but the original exact protocol has not been executed/validated.

## Installation (on a machine that can access GitHub)

```bash
# Run in a clean directory; original files remain unchanged.
git clone https://github.com/Wan-ZL/Foureye-2-simulation.git
cd Foureye-2-simulation
git checkout 8b6f02961e5f7202e094f9c25514c9e5a65ee4b4
cd ..

# Use your local Python environment; modern dependencies differ from the paper.
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install numpy networkx matplotlib scikit-learn pandas

python foureye2_runner.py audit \
  --source Foureye-2-simulation --output output/source_audit.json

# Copies source into separate working tree; applies only import compatibility patches.
python foureye2_runner.py prepare \
  --source Foureye-2-simulation --destination Foureye-2-compatible

# Genuine original main.game_start function, non-ML hypergame scheme, 1 seed only.
python foureye2_runner.py run --source Foureye-2-compatible \
  --scheme DD-IPI --runs 1 --timeout 300 \
  --stop-on-error --output output/smoke

# If smoke passes, compare the original DD and No-DD variants using 10 seeds.
python foureye2_runner.py run --source Foureye-2-compatible \
  --scheme DD-IPI --runs 10 --timeout 600 --output output/DD-IPI
python foureye2_runner.py run --source Foureye-2-compatible \
  --scheme No-DD-IPI --runs 10 --timeout 600 --output output/No-DD-IPI

# Only after resolving model assets and environment blockers, full sweep:
python foureye2_runner.py run --source Foureye-2-compatible \
  --scheme all --variation aap --runs 1000 --timeout 1800 \
  --output output/paper_vary_AAP
```

**Warning:** The publication reports 1,000 runs *per condition*. Eight schemes × six AAP conditions × 1,000 = 48,000 model runs. This may be computationally expensive. The bundled harness runs sequentially so it can record every failure; no claim of feasible wall time has been established.

Do not use the full command blindly. First restore/regenerate verified classifiers for the `DD-ML-IPI` and `DD-ML-PI` variants and confirm compatibility with the paper. The code intentionally refuses to replace trained checkpoints with heuristic or dummy models.

## Experiment and configuration mapping

| Scheme in code | Paper class | DD | Imperfect information | decision_scheme |
|---|---|---:|---:|---:|
| DD-Random | DD-Random | yes | n/a | 0 |
| No-DD-Random | No-DD-Random | no | n/a | 0 |
| DD-IPI | HG-DD-IPI | yes | yes | 1 |
| DD-ML-IPI | HG-DD-ML-IPI | yes | yes | 2 |
| No-DD-IPI | HG-No-DD-IPI | no | yes | 1 |
| DD-PI | G-DD-PI | yes | no | 1 |
| DD-ML-PI | G-DD-ML-PI | yes | no | 2 |
| No-DD-PI | G-No-DD-PI | no | no | 1 |

The mapping is based on the repository's own `main.py` commented invocation list; it does not establish numeric reproduction.

## Tracked outputs

Each run records its scheme, seed, AAP, outcome status, exception/timeout, and simulation trace. Successful runs record the original `game_start` object's `lifetime`, `TPR_history`, `FPR_history`, `hitting_result`, and failure reasons. The harness independently aggregates MTTSF and TPR/FPR.

**Important metric definition:** The paper's *HNE hitting ratio* is the probability that attacker and defender **hypergame Nash equilibria coincide**; it is **NOT** the rate of real attacks captured by honeypots. We label this value `mean_HNE_equilibrium_matching` to prevent misleading TEMARL comparisons.

This harness creates new outputs (`run_records.json`, `summary.json`, `summary.csv`, `manifest.json`) from whatever original simulations it can run. A run returning `status=ok` means the original `game_start` completed, **not** that a published table was reproduced. Paper-equivalent aggregation and precise error tolerances must still be audited.

## Known obstacles

1. **No repository archive here.** Source was reviewed remotely; original end-to-end simulations were not run in the assistant's environment.
2. **Missing trained decision-tree models.** `defender_function.py` loads `data/trained_ML_model/trained_classi_model_ML_collect_data_IPI.pkl` and the PI equivalent; AAP experiments require six corresponding model copies in `data_vary/AAP=<value>/trained_ML_model/`. No `.pkl` files were present in inspected public tree.
3. **Historical dependencies.** The paper states Python 3.6 + scikit-learn 0.19.1; there is no repository `requirements.txt`. Installing modern versions is an unverified port.
4. **Import compatibility.** `graph_function.py` and `game_function.py` use `from networkx import nx`, which fails under NetworkX 3.6.1. The **copied** source changes this to `import networkx as nx`. `main.py` is also given an early `display=False` to reduce circular-import risk.
5. **Default script selects an unavailable ML experiment.** The unmodified `main.py` executes `run_sumulation_group_vary_AAP("DD-ML-IPI", ..., simulation_time=1000)`, so running it unmodified is not a safe smoke test.
6. **ML training/output sequence is unresolved.** `ML_train_strat_sep.py` contains training functions, but the fixed-setting classifier-save block in `train_ML_predict_action` is commented out. Further author-code investigation is required before claiming faithful ML baseline reproduction.
7. **Plots are not raw data.** The GitHub tree contains generated plot images but no committed original `.pkl` run outputs. Those images cannot replace original experimental execution.
8. **Scientific output remains unverified.** Original Figure 3/4 metric equivalence, hypergame equilibria, exact seed behavior, and all eight baseline rankings must be verified against the article.

## Tests

```bash
python -m unittest discover -s tests -v
```

These tests validate this **harness only**. They do not constitute tests or execution of the authors' algorithms.

## Ethics and repeatability

All experimental failures must be preserved; no attempts to find a lucky seed that matches paper numbers. Fix the protocol **before** the final preregistered run, then report means, variability, baseline ordering, and all deviations. Train missing models faithfully rather than substituting approximations.

See `REPRODUCTION_REPORT.md` for the detailed code audit and evidence levels.
