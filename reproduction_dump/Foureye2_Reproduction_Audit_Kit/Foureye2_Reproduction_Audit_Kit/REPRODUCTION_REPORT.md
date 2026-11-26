# Foureye 2 — Evidence-Based Reproducibility Report

**Audit date:** 2026-11-23 (Asia/Dhaka)  
**Target publication:** Z. Wan et al., *Resisting Multiple Advanced Persistent Threats via Hypergame-Theoretic Defensive Deception*, IEEE TNSM (2023). DOI 10.1109/TNSM.2023.3240366.  
**Authors' original repository:** https://github.com/Wan-ZL/Foureye-2-simulation  
**Observed main HEAD:** `8b6f02961e5f7202e094f9c25514c9e5a65ee4b4` (2023-08-26).  
**Provenance:** Repository ownership and README connect the source to the paper. Code audited through a read-only GitHub connector.

## Executive verdict

**SOURCE VERIFIED; ORIGINAL EXPERIMENT EXECUTION BLOCKED IN THIS SESSION; PAPER TABLES NOT REPRODUCED.**

Unlike BAAHS, Foureye 2 has a substantive author-released simulation package. Files `main.py`, `game_function.py`, `graph_function.py`, `attacker_function.py`, `defender_function.py`, `ML_train_strat_sep.py`, and plotting scripts are present. However, required serialized model files are absent, dependencies are not pinned in the repo, and the GitHub repository is not present locally to execute. No claim of numerical agreement is warranted.

## Journal experiment (paper section V–VI)

- 100 legitimate nodes with 15 honeypots (5 high-interaction and 10 low-interaction).
- Network uses an Erdős–Rényi graph; node vulnerability classes and attack-defense hypergames represented explicitly.
- Paper reports 1,000 simulation repetitions. Parameter sweep for attacker arrival probability `PA`.
- Python 3.6, scikit-learn 0.19.1 (the author's reported setup).
- Eight comparisons: DD/No-DD and HG/G/Random, including ML variants.
- Published Figure 3 compares mean time to security failure (MTTSF), NIDS true positive rate (TPR), and false positive rate (FPR) versus attacker arrival probability.
- Figure 4 compares player uncertainties and hypergame expected utilities (C-HEU).
- HNE hitting ratio is the fraction of overlapping equilibrium solutions, NOT a honeypot contact or trap rate.

## Original source implementation map

| Scientific item | Author code location | Audit finding |
|---|---|---|
| Main single simulation | `main.py:13-70` (`game_start`) | Source present; executes attacker/defender repeated game |
| Main 1,000-run experimental protocol | `main.py:1093-1131` | Present; default active call is ML AAP sweep |
| Static scheme runner | `main.py:73+` (`run_sumulation_group_1`) | Present; `ProcessPoolExecutor`/per-run pickle output |
| Attacker arrival probability | `main.py:522+` (`run_sumulation_group_vary_AAP`) | Six published-style AAP settings present |
| Result objects | `game_function.py:29+` | Includes lifetime, TPR/FPR histories, equilibrium match |
| Honeypots and network topology | `graph_function.py:795+` | 100 nodes, 10 low/5 high honeypots, connection parameters |
| Attacker strategy behavior | `attacker_function.py` | Actual source available; 8 strategy actions |
| Defender choice mechanisms | `defender_function.py:538-612` | Random, utility-based, ML decisions |
| ML classifier loading | `defender_function.py:552-583` | Requires pickle artifacts absent from inspected tree |
| Classifier training | `ML_train_strat_sep.py:290-346` | Training code exists; fixed-setting pickle-saving is commented out |
| HNE equilibrium-matching computation | `game_function.py:575-615` | Boolean strategy-index agreements; do not call honeypot capture |
| Figure source | `Foureye display.py`, `Figure/*` | Plotting code and published images, no corresponding serialized raw results |

**Important:** Locations refer to audited HEAD. The code paths have been inspected; this does not imply successful execution of all functions.

## Actual tests performed in this session

- `python -m unittest discover -s tests -v`: **5 of 5 harness tests passed**.
- Current available environment: Python 3.13.5, NumPy 2.3.5, NetworkX 3.6.1, scikit-learn 1.8.0, Matplotlib 3.10.8.
- `from networkx import nx` **failed** in this environment, confirming a necessary compatibility fix when running the old source under NetworkX 3.6.1.
- No Foureye original process ran: source bytes could not be cloned/downloaded within the execution environment; only the remote GitHub connector inspection was available.
- No `.pkl` model files or experimental outputs were found in the inspected repository Git tree.
- This kit contains a patched-copy preparer, original-`game_start` runner, and non cherry-picked aggregation/logging, **not the author's original repository**.

## Current reproducibility gates

| Gate | Verdict | Evidence / limitation |
|---|---|---|
| Peer-reviewed journal | PASS | IEEE TNSM 2023 / DOI |
| Authentic author source | PASS | Repo README and paper link; GitHub author branch |
| Cyber deception action | PASS | Defense and honeypot strategy code |
| Real quantitative effectiveness | PASS | MTTSF versus DD/No-DD baselines; NIDS performance |
| Network topology and attacker model | PASS (source present) | Graph and attacker Python modules |
| Eight compared schemes | PASS (source present) | Main.py configuration list |
| Original metric implementation | PARTIAL | Lifetime, TPR/FPR, HNE stored; equation equivalence untested |
| Original evaluation scripts | PASS (source present) | Main.py and figure code; not run |
| Original ML checkpoints | FAIL | Not committed as `.pkl` |
| Original training protocol reproducible | UNVERIFIED | Data generation available in code; classifier save block commented |
| Exact pinned historical environment | FAIL | No requirements file; historical Python 3.6/sklearn 0.19.1 |
| Source actually executable here | BLOCKED | Repository ZIP not present; no network download |
| Published baseline ranking replicated | NOT TESTED | No experimental execution |
| Published figures/table results reproduced | **NO** | No runs or raw outputs generated |

## Next protocol (when original repo ZIP becomes available)

1. Materialize the original repository ZIP in the working container; verify the observed commit if `.git` available or SHA256 manifest otherwise.
2. Run source preflight and preserve all original file SHA256 hashes.
3. Prepare an isolated copy and perform compatibility-only changes. Confirm that the original `main.game_start` imports.
4. Run one `DD-IPI` no-ML episode, inspect full traceback/log, fix incompatibilities explicitly without changing defense science.
5. Run paired non-ML `DD-IPI` vs `No-DD-IPI` with predefined seeds; verify the MTTSF and FPR/TPR functions.
6. Trace `ML_train_strat_sep.py` through its original data collection inputs. Restore model-saving only if its documented intent and metric equivalence are established. Do not create dummy models.
7. Repeat on the paper's original 1,000-simulation scale with all eight methods and six AAP settings if verified.
8. Compare Figure 3 and Figure 4 output **including baseline ordering**, not only one attractive number.
9. If the original environment cannot be restored, label the compatibility-port results explicitly as *partial independent execution of author code*.

## References

1. Publisher: https://doi.org/10.1109/TNSM.2023.3240366
2. Author repo: https://github.com/Wan-ZL/Foureye-2-simulation
3. Full paper text / methodology: https://www.researchgate.net/publication/368343221_Resisting_Multiple_Advanced_Persistent_Threats_via_Hypergame-Theoretic_Defensive_Deception
4. Secondary parent research repo: https://github.com/Wan-ZL/ARO-Foureye

**Scientific verdict: Original-code reproduction remains unverified. No numerical outcomes should be attributed to actual reproduction.**
