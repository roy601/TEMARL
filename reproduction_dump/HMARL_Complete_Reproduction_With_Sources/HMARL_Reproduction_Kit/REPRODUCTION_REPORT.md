# H-MARL (RLJ 2025): Reproduction Audit, Uploaded-Source Package and Step-by-Step Execution

**Updated:** 22 November 2026 (UTC)  
**Paper:** *Hierarchical Multi-agent Reinforcement Learning for Cyber Network Defense* — A. V. Singh, E. Rathbun, E. Graham, L. Oakley, S. Boboila, P. Chin, A. Oprea, *Reinforcement Learning Journal* 6 (2025), pp. 790–810.  
**Reproduction target:** Table 3: H-MARL Expert versus H-MARL Meta against Default Red, each evaluated over **100 episodes** in **CybORG CAGE 4**.  
**Package status:** Original source trees **present and cryptographically verified**; offline tests **9/9 passed**; full learned-policy evaluation **NOT EXECUTED SUCCESSFULLY** due to missing Python dependencies in the evaluation environment.

---

## 1. Executive conclusion (do not misreport this)

| Claim | Current verified status | Evidence |
|---|---|---|
| Both user-provided original ZIPs read successfully | **YES** | ZIP CRC checks in `results/source_tree_audit.json` |
| Uploaded files exactly correspond to checked official Git tree snapshots | **YES** | Both computed Git tree object IDs match official reference trees |
| 65 pretrained policy checkpoints present in H-MARL | **YES** | Local file inventory and source audit |
| 15 checkpoint policy files needed by 3-policy Expert/Meta evaluators present | **YES** | `results/uploaded_preflight.json` |
| Paper's Table 3 values verified against publisher PDF | **YES** | Page 13 (zero-index PDF page 12); `paper_reference/table3_published.csv` |
| Reduction percentages calculated from published Table 3 | **YES (ARITHMETIC ONLY)** | `results/published_arithmetic.json` |
| Offline helper/unit tests | **9/9 PASS** | `logs/uploaded_attempts/offline_tests.txt` |
| Original evaluator invocation attempted | **YES; EXIT 1** | `logs/uploaded_attempts/direct_subpolicies.log`, `direct_master.log` |
| Original simulator ran 100 episodes | **NO** | `results/run_status.json` says `BLOCKED` |
| New independently measured red impact / defense reward values | **NO** | `results/comparison.json` says `NOT_EXECUTED` |
| Experimentally reproduced the red-impact reduction | **NO** | No completed simulation for either method |
| Entire paper, including retraining, transfer, and ablations, reproduced | **NO** | Those experiments not run |

**Unambiguous final verdict:** The uploaded research assets are complete and their source versions are verified, but **the 100-episode Table 3 evaluation and the experimental reduction were NOT successfully reproduced here**. It would be false to claim full reproduction or 22.81% new experimental reduction. That figure is computed from *published* aggregates only.

### What remains blocked, specifically?

- Environment here runs **Python 3.13.5**, whereas the older **Ray/RLlib 2.10.0** stack is expected to work with **Python 3.10**. Python 3.10 is not installed here.
- **`ray` / RLlib** and **`gym`** are not installed. `CybORG` is present in **source form**, but its Python package is not installed into this environment.
- This container cannot resolve `pypi.org` or `github.com`, so the missing dependencies cannot be installed here. **No substitute or simulated policy runs were fabricated.**
- Direct attempts to run the authors' actual `subpolicies/evaluation_metrics.py` and `master/evaluation_metrics.py` fail at import with `ModuleNotFoundError: No module named 'gym'` originating from `CybORG/env.py` (even with source on `PYTHONPATH`). Both logs are saved verbatim.

## 2. Authoritative source links and exact revisions

| Asset | Link | Identifying revision |
|---|---|---|
| Journal publication | https://rlj.org/papers/singh2025hierarchical | *Reinforcement Learning Journal*, 2025 |
| Full publisher paper PDF | https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_77.pdf | Table 3, PDF page 13 |
| Authors' H-MARL repository | https://github.com/adityavs14/Hierarchical-MARL | Commit `6fe960f5931f2d7dc5ef522f09ca4a179f377ee4` |
| H-MARL source snapshot ZIP | https://github.com/adityavs14/Hierarchical-MARL/archive/refs/heads/main.zip | Snapshot is unpinned; this upload matched the commit above |
| CAGE 4 simulator repository | https://github.com/cage-challenge/cage-challenge-4 | Commit `8c3c50ca54b176c2de199847944e8dcc035497e3` |
| CAGE 4 source snapshot ZIP | https://github.com/cage-challenge/cage-challenge-4/archive/refs/heads/main.zip | Snapshot is unpinned; this upload matched the commit above |
| Original H-MARL instructions | https://github.com/adityavs14/Hierarchical-MARL/blob/main/README.md | Install and evaluation commands |
| Original Expert evaluator | https://github.com/adityavs14/Hierarchical-MARL/blob/main/h-marl-3policy/subpolicies/evaluation_metrics.py | Exact script used by our runner |
| Original Meta evaluator | https://github.com/adityavs14/Hierarchical-MARL/blob/main/h-marl-3policy/master/evaluation_metrics.py | Exact script used by our runner |

**Important provenance qualification:** We checked the uploaded archive Git object **trees** against the remote snapshots. An archive does not carry its `.git` history; thus a Git object tree match proves the exact file tree, not the historical date or training provenance of the weights. The CAGE 4 snapshot might differ from the unpublished exact environment revision used to obtain Table 3, and old Ray checkpoint formats can be sensitive to dependency versions.

### 2.1 Git-tree verification results

Git computes a SHA-1 tree object from the **actual extracted file names, bytes, permissions and hierarchy**. This is stronger than matching just a few filenames.

| Repository | Calculated tree | Expected official tree | Match |
|---|---|---|---|
| H-MARL | `90976d80a306be666892b21979ada40402f5724b` | `90976d80a306be666892b21979ada40402f5724b` | **Yes** |
| CAGE 4 | `3b10ab4380eef36cccad56d8a86b66053fb006a1` | `3b10ab4380eef36cccad56d8a86b66053fb006a1` | **Yes** |

Archive SHA256 from the uploaded ZIPs:

- `Hierarchical-MARL-main.zip`: `4768eda6ce4e31dcbd78f02fb2c42aaff01c4a82b59db173b14b2e14a1a43737`
- `cage-challenge-4-main (5).zip`: `bf9bbae5c26a3d4add4ec487935d1fb7f515f228362f2ca32070fcf5dda4d882`

Both ZIP CRC tests passed. The source manifest verifies **464 file hashes** across the **192 H-MARL files and 272 CAGE 4 files**. The H-MARL repository contains **65 `policy_state.pkl` files** over its saved-policy variants. Our targeted 3-policy Expert/Meta workflows require **15** of those files (five investigate, five recover, five learned-master).

The full per-file inventory, source SHA256s and original file sizes are in `FILE_INVENTORY.csv` and `source_manifest.json`. Prior to patching, run:

```bash
python scripts/verify_source_manifest.py
```

The bundled `sources/` directories have been restored to the original verified versions; **they are not prepatched**. Setup scripts intentionally enable metric collection and optionally add passive metric exports afterward. Therefore manifest verification must be performed **before** running setup/patching.

## 3. What is being reproduced scientifically?

H-MARL is a hierarchical multi-agent reinforcement learning cyber-defense method evaluated in **CAGE 4**, not a direct honeypot engagement benchmark. There are five blue agents. **H-MARL Expert** selects Recover versus Investigate by a fixed expert master rule; **H-MARL Meta** uses a learned master policy. Both use pretrained lower-level policies. The Default Red agent in the authors' evaluator is `FiniteStateRedAgent`.

For Table 3:

- Evaluate **100 episodes** per strategy, with nominal **500 environment steps** per episode.
- Use **`h-marl-3policy`** (one master and two subpolicies), **not** the optional `h-marl-4policy` traffic-control experiment.
- The Expert evaluator internally iterates two decision calls per environment action, so its loop over `2 * EPISODE_LENGTH` is not 1,000 independent environment steps.
- The authors' code saves `summary.json` for reward and emits many other security metrics to the console. The basic summary alone does **not** reproduce all nine Table 3 columns.
- A fixed seed, such as `42`, is a reproducible *new evaluation condition*; the published Table 3 did not establish this exact seed. Stochastic 100-episode means need not match to the last digit.

The unmodified author's evaluation scripts are in `sources/Hierarchical-MARL/h-marl-3policy/`; our kit only orchestrates their execution, enables existing metric flags, and offers an optional **passive** JSON metric exporter whose aggregation requires independent audit before scientific claims.

## 4. The published Table 3 reference (NOT reproduced results)

Values checked against the publisher PDF's Table 3, titled *Interpretable metrics for various blue strategies against Default Red, 100-episode averages*:

| Metric | H-MARL Expert (published) | H-MARL Meta (published) | What it measures |
|---|---:|---:|---|
| Clean hosts ratio | 0.81 | 0.77 | Hosts without red presence |
| Non-escalated hosts ratio | 0.99 | 0.97 | Hosts without root-level red sessions |
| Mean time to recover | 44.76 | 62.63 | Mean compromised-state duration |
| Useful recoveries | 6.07 | 5.79 | Recoveries on compromised machines |
| Wasted recoveries | 2.20 | 3.74 | Recoveries on clean machines |
| Recovery precision | 0.73 | 0.61 | True positives / all recoveries |
| Recovery error | 0.27 | 0.39 | False positives / all recoveries |
| Red impact count | 0.88 | 1.14 | OT-service impacts |
| Defense reward | -129.53 | -181.62 | Blue-team total episode reward |

The other baselines, H-MARL Collective and MARL Decentralized, are also transcribed in `paper_reference/table3_published.csv`. Neither of those baselines was evaluated here. Distinguish **Table 2** (reward summaries across red variants) from **Table 3** (interpretable metrics against Default Red).

### 4.1 Published-only reduction arithmetic

The following is mathematically correct **but is not independent experimental reproduction**:

- Expert versus Meta, **red impact**: `(1.14 - 0.88) / 1.14 * 100` = **22.81% lower**.
- Expert versus MARL Decentralized, **red impact**: `(1.54 - 0.88) / 1.54 * 100` = **42.86% lower**.
- Expert versus Meta, **wasted recoveries**: `(3.74 - 2.20) / 3.74 * 100` = **41.18% lower**.
- Expert versus MARL Decentralized, **wasted recoveries**: `(27.99 - 2.20) / 27.99 * 100` = **92.14% lower**.

These percentages use rounded means from Table 3, so additional decimal places would convey unwarranted precision.

### 4.2 Newly measured results from this attempt

| Metric | Expert new measurement | Meta new measurement | Verdict |
|---|---|---|---|
| Red impact count | **Not available** | **Not available** | No evaluation completed |
| Reward | **Not available** | **Not available** | No evaluation completed |
| Other seven metrics | **Not available** | **Not available** | No evaluation completed |
| Empirical red impact reduction | **Not available** | **Not available** | **NOT REPRODUCED** |

`results/comparison.json` deliberately records `null` values. The published numbers are not placed into any measured-results field.

## 5. What the original uploaded ZIPs contain

All original file bytes are included in this new package (there is **no need to download the two repositories again**):

```
HMARL_Reproduction_Kit/
  sources/
    Hierarchical-MARL/
      README.md
      LICENSE
      h-marl-3policy/
        subpolicies/
          evaluation_metrics.py
          submission.py
          Ray_BlueAgent.py
          BlueFlatWrapper_CC4.py
          ... (original supporting wrappers, policy/model/training files)
        master/
          evaluation_metrics.py
          submission.py
          Ray_BlueAgent.py
          BlueFlatWrapper_CC4.py
          ... (original supporting wrappers, policy/model/training files)
        saved_policies/
          sub/iter_49/policies/Agent0_investigate/policy_state.pkl
          ... (all other original saved checkpoints)
          master/iter_49/policies/Agent0_master/policy_state.pkl
      h-marl-4policy/ ... (all original files/checkpoints, not Table 3 target)
      marl-1policy/ ... (all original files/checkpoints)
    cage-challenge-4/
      CybORG/ ... (complete original simulator package)
      Requirements.txt
      setup.py
      ... (all original challenge files)
  scripts/ ... (our reproduction scripts)
  results/ ... (observed attempt logs/results, NOT fabricated simulation)
  logs/ ... (original stdout/stderr from attempted run)
  paper_reference/ ... (published-only CSV baselines)
  tests/ ... (offline helper tests)
  setup_from_uploaded_windows.ps1
  setup_from_uploaded_linux.sh
  README.md
  REPRODUCTION_REPORT.md
  source_manifest.json
  FILE_INVENTORY.csv
```

For a literal list of *every* file including sizes and SHA256, open `FILE_INVENTORY.csv`. It covers the original source directories and other kit files as at inventory generation time (the inventory does not hash itself). For strong verification of all original source files, use `source_manifest.json`.

### 5.1 Toolkit file-by-file guide

| File | Use |
|---|---|
| `README.md` | First-run checklist and honest conclusion |
| `REPRODUCTION_REPORT.md` | This report: methodology, provenance, commands, findings, blockers |
| `setup_from_uploaded_windows.ps1` | Installs required Python packages and patches the **bundled** original source on Windows |
| `setup_from_uploaded_linux.sh` | Equivalent for Linux/WSL2; uses Python 3.10 |
| `bootstrap_windows.ps1`, `bootstrap_linux_macos.sh` | Legacy scripts to fetch sources from GitHub; **not needed** now that sources are bundled |
| `scripts/verify_source_manifest.py` | SHA256-verifies every original source file before modification |
| `scripts/patch_metrics.py` | Turns on two original `COMPUTE_METRICS` flags, with `.original.bak` backups |
| `scripts/instrument_metrics.py` | Optionally saves approximate Table 3 metric aggregates as a JSON file, with evaluator backups |
| `scripts/preflight.py` | Checks Python, dependencies, original checkpoints, metric flags, and evaluator existence |
| `scripts/run_evaluation.py` | Launches authors' actual 100-episode Expert/Meta evaluators and records return codes/logs |
| `scripts/compare_results.py` | Compares published and measured metrics; refuses to mark missing measurements as success |
| `scripts/reference_arithmetic.py` | Computes reductions using **published values only** |
| `tests/test_reference.py` | No-false-reproduction tests, reference arithmetic, table verification |
| `tests/test_patch.py` | Metric-flag patch tests |
| `tests/test_instrument.py` | Metric exporter insertion tests |
| `paper_reference/table3_published.csv` | Authors' reference Table 3, all four rows and nine metrics |
| `paper_reference/default_red_rewards_table2.csv` | Reference rewards from Table 2, not experiment output |
| `paper_reference/measured_metrics_TEMPLATE.csv` | Empty placeholder for separately audited measurement entry |
| `results/source_tree_audit.json` | ZIP CRC, official Git tree matches, checkpoint counts, static compile audit |
| `results/uploaded_preflight.json` | Real dependency/checkpoint status for the uploaded-source attempt |
| `results/run_status.json` | Real runner attempt status, blocked at preflight |
| `results/comparison.json` / `.md` | Real missing-measurement comparison |
| `results/published_arithmetic.json` | Published-only reduction check |
| `logs/uploaded_attempts/` | Direct original evaluator failures, other attempted commands, unit test output |
| `source_manifest.json` | SHA256 expected for all 464 original source files |
| `FILE_INVENTORY.csv` | Complete per-file paths/bytes/SHA256 inventory |
| `SHA256SUMS.txt` | Legacy toolkit-only checksums (from first build); use source manifest and final ZIP checksum for uploaded-source verification |

## 6. Reproduction instructions — Windows 10/11 (PowerShell)

### 6.1 Prerequisites

1. Extract `HMARL_Complete_Reproduction_With_Sources.zip` to a short path, e.g. `C:\HMARL\`. Ensure the *inner* folder `HMARL_Reproduction_Kit` contains `README.md` and `sources\`.
2. Install **Python 3.10 (64-bit)**. Verify in PowerShell with `py -3.10 --version`.
3. Install Git for Windows only if you want to perform your own Git-tree checks. **This supplied-source setup does not require Git.**
4. Have internet connectivity to Python package indexes (PyPI). The H-MARL and CAGE source and checkpoints are bundled, but **Python dependencies are not**.
5. Reserve several GB of disk for Torch, Ray, and other scientific packages and sufficient memory for Ray worker processes. Consider **WSL2 Ubuntu** if native Windows Ray behavior is problematic.

### 6.2 Verify source before patching

```powershell
cd C:\HMARL\HMARL_Reproduction_Kit
py -3.10 scripts\verify_source_manifest.py
```

Expected: `"status": "PASS", "total_checked": 464`.

### 6.3 Install from bundled sources (no new GitHub downloads)

```powershell
powershell -ExecutionPolicy Bypass -File .\setup_from_uploaded_windows.ps1
```

The script creates `.venv`, installs PyTorch/Gym/CybORG and `ray[rllib]==2.10.0`, enables metric collection in both original wrappers, adds **passive JSON exports**, performs offline helper tests, saves a `pip freeze`, and runs preflight. It does not train any models; it uses the included checkpoint files. **This installer could not be end-to-end tested here, because the present environment has no PyPI connectivity.** If dependency resolution fails, keep the full console error rather than asserting a successful installation.

### 6.4 Execute the original H-MARL model (100 episodes each)

```powershell
.\.venv\Scripts\python.exe scripts\run_evaluation.py --repo sources\Hierarchical-MARL --cage sources\cage-challenge-4 --max-eps 100 --seed 42
.\.venv\Scripts\python.exe scripts\compare_results.py
```

**Do not start retraining** until pretrained-checkpoint evaluation is successfully verified. A completed run should produce `results\expert\summary.json`, `results\meta\summary.json`, their `console.log` files, and — if instrumentation succeeded — `table3_instrumented.json` for each.

**If you prefer to run only the original author evaluator, without instrumentation:** run `scripts/patch_metrics.py` but skip `scripts/instrument_metrics.py`, and then invoke the original scripts as shown in Section 8. Their raw stdout is preserved by our runner, but `summary.json` will contain only reward aggregate information.

## 7. Reproduction instructions — Linux / WSL2 / macOS

Requires Python **3.10**, working PyPI, a compatible CPU/GPU PyTorch installation and sufficient RAM. From the extracted inner directory:

```bash
cd HMARL_Reproduction_Kit
python3.10 scripts/verify_source_manifest.py
PYTHON_BIN=python3.10 bash setup_from_uploaded_linux.sh
source .venv/bin/activate
python scripts/run_evaluation.py --repo sources/Hierarchical-MARL --cage sources/cage-challenge-4 --max-eps 100 --seed 42
python scripts/compare_results.py
```

**Preflight:**

```bash
python scripts/preflight.py --repo sources/Hierarchical-MARL --cage sources/cage-challenge-4 --out results/preflight.json
```

Inspect `results/preflight.json`. You need `module_CybORG`, `module_ray`, `module_gym`, `checkpoint_files_complete`, `metric_flags_enabled` and `ray_2_10_0` to be true. The check `python_3_10_compatible_recommendation` should also be true. The uploaded ZIP directories are not Git clones, so the `..._pinned_commit` Boolean may be false even though the archive file-tree cryptographic verification passed. This discrepancy is expected and **does not mean files are missing**.

## 8. Exact author evaluation commands and configuration

Run with current working directory set to:

`HMARL_Reproduction_Kit/sources/Hierarchical-MARL/h-marl-3policy`

Then:

```bash
# Expert: expert master rule with Investigate and Recover subpolicies
python -u subpolicies/evaluation_metrics.py subpolicies/submission.py /ABSOLUTE/PATH/TO/results/expert --max-eps 100 --seed 42

# Meta: learned master with pretrained Investigate and Recover subpolicies
python -u master/evaluation_metrics.py master/submission.py /ABSOLUTE/PATH/TO/results/meta --max-eps 100 --seed 42
```

**Why the working directory matters:** The authors' `Ray_BlueAgent.py` loads `saved_policies/sub/iter_49/policies/...` or `saved_policies/master/iter_49/policies/...` using paths relative to `h-marl-3policy`. Running from a different directory will falsely report checkpoints missing.

### Required flags and optional instrumentation

Two source files originally contain `COMPUTE_METRICS = False`:

- `sources/Hierarchical-MARL/h-marl-3policy/subpolicies/BlueFlatWrapper_CC4.py`
- `sources/Hierarchical-MARL/h-marl-3policy/master/BlueFlatWrapper_CC4.py`

These **must** be changed to `True` for the additional security metrics. The authors explicitly document this. The helper `scripts/patch_metrics.py` changes only these flags and writes backup copies.

Our separate **optional** exporter `scripts/instrument_metrics.py` appends logging code after the final reward computation and writes `table3_instrumented.json`, containing all candidate Table 3 metrics derived from the original evaluator's in-memory arrays. It is syntactically checked but **not empirically verified in a complete simulation here**. Specific caution: sums/means across subnets, red agents, and episodes and precision/error aggregation need to be checked before these values are reported as exact published-formula replications. The script does not alter agents or their actions.

### Original dependency information

- Source: `sources/cage-challenge-4/Requirements.txt` specifies, among others, `gym==0.26.2`, `gymnasium==0.28.1`, `numpy==1.26.4`, `torch==2.2.0` and graph/visualization dependencies.
- The H-MARL repository README asks for **Ray 2.10.0** and CAGE4 editable installation (`pip install -e .`).
- Using newer packages merely because they are available may break saved RLlib policy serialization, action masking, or PPO model reconstruction. Preserve the exact dependency versions and the `pip freeze` output when reporting results.
- Python 3.13 is **not the tested target** for this older stack. Use a Python 3.10 environment.

## 9. Evidence collected from the actual attempt

The attempts below were performed on the user-uploaded archive contents, not inferred from filenames.

1. **ZIP extraction and CRC tests:** Both source archives passed; 283 and 320 archive entries respectively. Their extracted trees match the official Git tree hashes (Section 2).
2. **Checkpoint inventory:** All 65 upstream `policy_state.pkl` files found; **15 of 15 required checkpoints** for the three-policy Expert and Meta variants detected. The checkpoints were **not loaded into Ray**.
3. **Static Python syntax audit:** 203 upstream `.py` files successfully compiled for syntax; **one unrelated upstream example file** has a syntax error: `sources/cage-challenge-4/CybORG/Evaluation/example_submission/submission.py` places `from __future__ import annotations` after other imports. This example file is **not** part of the H-MARL Expert/Meta evaluation path. We leave it unmodified to preserve the authoritative Git tree. See `results/source_tree_audit.json`.
4. **Offline helper tests:** 9 passed. These exercise patches, reference arithmetic, no-false-success logic and instrumentation insertion. They are **not** substitute simulation experiments.
5. **Metric patch and optional instrumentation:** Dry-run/patch syntax checks succeeded on copies of the authors' two evaluator files. The copies were then restored to pristine source bytes before packaging; the setup script applies them on the user's machine.
6. **Standard runner:** `scripts/run_evaluation.py --max-eps 100 --seed 42` refused to run because preflight saw missing dependencies (`results/run_status.json`). No 100-episode output produced.
7. **Direct original evaluator attempts:** with CAGE source placed on `PYTHONPATH`, each original evaluator immediately failed at `import gym` in `CybORG/env.py` (`logs/uploaded_attempts/direct_subpolicies.log` and `direct_master.log`). Even after obtaining Gym, Ray/RLlib also remains absent.
8. **Connectivity checks:** `pypi.org` and `github.com` name resolution failed; installing original required wheels and Ray could not proceed in this container.
9. **Post-attempt comparison:** `results/comparison.json` marks measurements absent and verdict `NOT_EXECUTED`; published table numbers are kept separate.

### What success would require

A defensible **Table 3 model evaluation reproduction** requires both Expert and Meta to complete **100 original CAGE 4 episodes** using the released checkpoints, plus saved console logs, `summary.json`, `table3_instrumented.json` or independently audited metric exports, dependency-version record, aggregation review, and a comparison to the published numbers accounting for randomness. Replicating *the entire paper* additionally requires training and the other adversary/transfer experiments; this kit focuses on Table 3, not the full publication.

## 10. Measured-result validation / report generation

Once the two 100-episode runs have **actually finished**, use:

```bash
python scripts/compare_results.py --reference paper_reference/table3_published.csv --results results
```

This script distinguishes:

- `NOT_EXECUTED` — no authentic completed original evaluator summaries.
- `PARTIAL_REPRODUCTION` — reward summaries exist but complete Table 3 metrics are unavailable.
- `TABLE3_INSTRUMENTED_RUN_NOT_CLOSE_TO_PUBLISHED` — measured instrumented metrics exist but do not satisfy the declared **per-cell tolerance**.
- `TABLE3_NUMERICALLY_CLOSE_INSTRUMENTED_REPRODUCTION_NEEDS_INDEPENDENT_AUDIT` — full 100-episode instrumented measurements are numerically close, **not** proof of fully reproduced training or matching random outcomes.

Numeric closeness uses the configured `--abs-tolerance` (default `0.01`) only as a transparent first comparison; it is **not a validated statistical equivalence test**. A real research report should show episode distributions, standard deviations/confidence intervals, seeds, and exact aggregation definitions, and should not loosen tolerance simply to achieve a positive status.

The comparison report also records the new experimental red-impact reduction as a number **only if both original-run evidence files exist**; otherwise the field remains `null`. Published-only reduction is separately labeled.

## 11. Troubleshooting and limitations

| Symptom | Correct interpretation/action |
|---|---|
| `No module named 'gym'` | Dependencies not installed; run source-based setup in Python 3.10 |
| `No module named 'ray'` | Ray/RLlib dependency missing; install pinned Ray 2.10.0 |
| `CybORG` not found | Editable simulator installation (`pip install -e sources/cage-challenge-4`) needed |
| Python 3.13 available but not Python 3.10 | Install/select Python 3.10; do not assume ancient Ray checkpoints work on 3.13 |
| `policy_state.pkl` / serialization fails | Confirm Ray 2.10.0, torch 2.2.0, original files and cwd; record stack trace; never overwrite original weights silently |
| `COMPUTE_METRICS` false | Run `scripts/patch_metrics.py`, with backups saved |
| Manifest verification fails after patching | Expected: two wrappers/two evaluators changed intentionally; compare against backups or restore before verification |
| ZIP has `sources/` but preflight says repo not pinned | The ZIP has no `.git` metadata; use the cryptographically verified tree results, not a missing Git checkout |
| Native Windows multiprocessing/Ray errors | Try WSL2 Linux with Python 3.10 and identical source/assets; log changes |
| Security metrics are missing from `summary.json` | Authors' summary stores only reward; enable and audit `table3_instrumented.json` / console metric diagnostics |
| Example submission source fails `compileall` | Unused upstream CAGE example has a misplaced future import; do not confuse with H-MARL evaluation failure |
| Results differ from paper slightly | Randomization/seed/version differences; analyze episode variance, not one rounded aggregate |

**Security:** PyTorch/Ray pickle checkpoint loading can execute code. Only use weights you trust, and evaluate in an isolated development environment. The tree audit verifies match to the public repository snapshot, not the safety of executing the repository.

## 12. Applicability to TEMARL / deception paper comparisons

H-MARL defends a simulated CAGE 4 enterprise network. Table 3 measures blue-team cyber-defense behavior and red impact, **not honeypot diversion, attacker dwell time or deception-engagement success rate**. TEMARL's CasinoLimit/CAMLDS replay data is a different data/environment interface. To claim a direct model-to-model score comparison, run both systems against **identical attack/environment conditions and metric definitions**. Do not compare rewards from different simulators as if they were on the same scale.

## 13. Packaging / provenance caveats

- This ZIP includes the **original H-MARL source and checkpoint files and the original CAGE 4 source**, so their downloads are no longer a blocker. Dependencies still must be installed on a capable machine.
- It does **not** include a Python 3.10 interpreter, prebuilt Torch/Gym/Ray wheels, a container image, trained checkpoints from experiments not present in the official repository, or any fabricated episode results.
- The setup scripts are best-effort and **untested end-to-end** here due to restricted network/install environment.
- No pretrained model inference, simulator rollout, or fresh Table 3 metric comparison has completed successfully in this environment.

---

**Research integrity verdict:** **SOURCE REPRODUCIBILITY VERIFIED; EXPERIMENTAL REPRODUCTION BLOCKED; REDUCTION VERIFIED ARITHMETICALLY ONLY.**
