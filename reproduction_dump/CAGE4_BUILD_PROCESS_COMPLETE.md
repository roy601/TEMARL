# CAGE 4 × TEMARL Reproduction Kit — Complete Build, File, Source, and Gap Guide

**Documentation date:** 2026-11-22  
**Scope:** the ZIP named `CAGE4_TEMARL_Reproduction_Kit.zip` and all of its packaged members.  
**Important status:** This archive is a **reproduction scaffold**, *not* a proven end-to-end replication of CAGE 4 Table 3 and *not* a trained CAGE-compatible TEMARL submission. Four small offline harness tests pass; the actual CAGE evaluations have **not** been executed in the build environment. There are **no reproduced scientific reward numbers** in this ZIP.

> **Read this before running anything.** A ZIP file cannot itself run a simulation. Extract it first. `START_LINUX.sh` or `START_WINDOWS.ps1` will *attempt* to fetch the official code and run **two-episode smoke tests**. A clean execution is not guaranteed because of upstream dependency/version compatibility. A full 100-episode baseline run is a **separate manual command**. Integrating and training TEMARL in CAGE 4 remains separate engineering and research work.

## 1. Why this package exists

The goal is to reproduce the **standard-environment** portion of **Table 3** in the CAGE Challenge 4 journal paper as far as source availability allows, then later compare a **newly ported and trained** TEMARL agent against those baselines under the same CAGE 4 protocol. This kit starts with the **PUNCH Analyse-Restore v1** heuristic and **Cybermonic KEEP** graph-based RL defender, because source code is available for both. It **does not** solve the missing UC and Lancer submissions.

- **Target paper:** [CAGE Challenge 4: A Scalable Multi-Agent Reinforcement Learning Gym for Autonomous Cyber Defence](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021), especially Table 3.
- **Published standard-environment numbers used as reference targets:** PUNCH **−142 ± 44**, Cybermonic **−193 ± 84** (mean cumulative reward ± reported spread; **published**, not measured by this kit). These values were copied into `run_baselines.py`, `make_comparison.py` and the protocol document for reference only.
- **Official evaluation unit:** **100 episodes**, **500 simulation steps each**; higher (less negative) cumulative reward is better.
- **Not a direct deception metric:** CAGE cumulative reward is not automatically honeypot engagement, time deceived, or decoy success. Measuring deception requires additional instrumentation and consistent definitions for every competing agent.

## 2. Source-of-truth links and exact upstream versions

All three repositories are **downloaded on the user's machine at runtime** by `bootstrap.py`; their contents are **not bundled** or represented as independently tested. The tool pins them to these exact Git commits (recorded in `sources.json`):

| Source key | Why needed | Official repository | Commit used by bootstrap | Direct upstream implementation reference |
|---|---|---|---|---|
| `cage` | Official simulator, blue/red agent API, reward function, evaluation runner | [cage-challenge/cage-challenge-4](https://github.com/cage-challenge/cage-challenge-4) | `8c3c50ca54b176c2de199847944e8dcc035497e3` | [Official `CybORG/Evaluation/evaluation.py`](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/evaluation.py), [evaluation README](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/README.md), [Requirements.txt](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/Requirements.txt) |
| `punch` | PUNCH Analyse-Restore v1 heuristic submitted for CAGE 4 | [PUNCH-Cyber/cage-4-submissions](https://github.com/PUNCH-Cyber/cage-4-submissions) | `9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0` | [PUNCH v1 submission](https://github.com/PUNCH-Cyber/cage-4-submissions/blob/9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0/punch_analyse_restore_v1/submission.py), [agent code](https://github.com/PUNCH-Cyber/cage-4-submissions/blob/9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0/punch_analyse_restore_v1/punchagents.py), [wrapper](https://github.com/PUNCH-Cyber/cage-4-submissions/blob/9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0/punch_analyse_restore_v1/punchwrappers.py) |
| `cybermonic` | Cybermonic KEEP model and released checkpoint weights | [cybermonic/cage-4-submission](https://github.com/cybermonic/cage-4-submission) | `2afd652d80ce9d4051a07c23c2538f3dec6bb6c6` | [Submission entrypoint](https://github.com/cybermonic/cage-4-submission/blob/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/submission.py), [model sources](https://github.com/cybermonic/cage-4-submission/tree/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/models), [five checkpoint files](https://github.com/cybermonic/cage-4-submission/tree/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/weights), [requirements](https://github.com/cybermonic/cage-4-submission/blob/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/requirements.txt) |

Additional **documentation** (not used as installed dependencies): [CAGE 4 published documentation](https://cage-challenge.github.io/cage-challenge-4/). The **reference TEMARL archive** is from the **user's uploaded `camlds_real_full_arch (2).zip`**, not any external web URL. Do not mistake its CAM-LDS results for CAGE 4 results.

### How the upstream code is used

1. `bootstrap.py` reads `sources.json` and clones the repositories to `external/cage`, `external/punch` and `external/cybermonic`.
2. For each repo it checks out the **exact commit** and refuses to proceed on an unexpected revision.
3. `bootstrap.py --install` additionally invokes pip against the CAGE and Cybermonic upstream requirements; it installs the official CAGE package editable, without changing its code.
4. `run_baselines.py` invokes `python -m CybORG.Evaluation.evaluation` from the **official CAGE repository** with the source PUNCH or Cybermonic `submission.py` folder, `--seed`, `--max-eps`, and the output directory.
5. This package does **not** implement a replacement reward evaluator. It delegates cumulative reward calculation to the pinned CAGE evaluator.

**Limits on claims:** Pinning a currently available Git commit does *not* establish that it is the exact CAGE simulator revision used for the journal Table 3. No official source snapshot, evaluation random-seed list, or modified-environment patches from that particular publication were verified for the kit.

## 3. Original build process — reconstruct the kit step by step

These are the **steps used to assemble the supplied scaffold** (not a claim that the external experiments were executed):

1. **Select the research objective.** Choose the CAGE 4 journal Table 3 **standard-environment** reward as the first reproducibility target. Identify PUNCH v1 and Cybermonic as available source baselines; leave UC, Lancer, the five robustness variants, and TEMARL for later.
2. **Inspect source entrypoints.** Confirm PUNCH v1 has `submission.py`, `punchagents.py`, `punchwrappers.py`; Cybermonic has `submission.py`, graph wrapper, models, and `weights/gnn_ppo-0.pt` through `gnn_ppo-4.pt`; CAGE has `CybORG/Evaluation/evaluation.py`.
3. **Record permanent source IDs.** Save all three repository URLs and their precise Git hashes in `sources.json` so that `bootstrap.py` does not silently track `main` as it changes.
4. **Write the source fetcher (`bootstrap.py`).** It runs Git clone/fetch/checkout; checks the hashes; writes `results/source_provenance.json`; optionally installs unmodified upstream dependencies into a dedicated Python 3.11 virtual environment.
5. **Write the safety check (`preflight.py`).** Verify Git hashes, the existence and approximate size of five Cybermonic weights, and imports for `torch`, `torch_geometric`, `ray`, `gymnasium`, `CybORG`, `numpy`.
6. **Write the evaluator (`run_baselines.py`).** Point to the PUNCH v1 submission folder and Cybermonic root, run the official `CybORG.Evaluation.evaluation` module with a configured seed and 500-step episodes, capture stdout/stderr to `runner.log`, save `invocation.json`, and reject failed runs.
7. **Write the comparison exporter (`make_comparison.py`).** Only import genuine `summary.json` files from **completed** invocations; include published scores in separate reference columns; write `results/comparison.csv`.
8. **Write startup scripts** for Linux/WSL2 (`START_LINUX.sh`) and Windows (`START_WINDOWS.ps1`). They create a virtual environment, download/install upstream projects, run preflight, and perform only **2-episode** smoke tests before building a CSV.
9. **Write the experiment plan** (`docs/EXPERIMENT_PROTOCOL.md`). State the standard 100 × 500 reproduction design, the proposed CAGE-compatible TEMARL port, deception metrics and fairness requirements.
10. **Write basic offline tests** (`tests/test_harness.py`). Check commit pins, constructed official evaluator command, exclusion of nonexistent results, and exclusion of failed runs.
11. **Preserve the user's exact CAM-LDS archive** as `reference/CAM_LDS_TEMARL_SOURCE_UNMODIFIED.zip`, without applying a CAGE conversion. Its SHA-256 is `b43bd0bee9d112e1219ba5867b4fb111db760cf948ad4c5415f6b4ee69dbd603`; it contains **2,274 file entries**.
12. **Create documentation and placeholders.** Add `README.md`, `.gitignore`, `.gitkeep` files under `external/` and `results/`, and a **header-only** `results/comparison.csv` to show the output schema without fabricating results.
13. **Package it.** Put the described project directory inside `CAGE4_TEMARL_Reproduction_Kit.zip` with relative paths. No `external/` repo checkout, pip environment, CAGE results, or trained TEMARL policy is included.
14. **Offline verification.** Run `python -m unittest discover -s tests -v` (four tests passed), `python run_baselines.py --agents all --episodes 2 --seed 12501 --dry-run` (command construction only), and check ZIP integrity. None of these tests exercises the CAGE runtime or the trained Cybermonic model.
15. **Add this guide and the inventory in the updated archive.** The complete embedded archive inventory appears in `docs/REFERENCE_ARCHIVE_FILES.csv`; `README.md` now points here.

### File integrity

You can verify the preserved source ZIP with Python (run from the extracted kit root):

```bash
python -c "import hashlib,pathlib; p=pathlib.Path('reference/CAM_LDS_TEMARL_SOURCE_UNMODIFIED.zip'); print(hashlib.sha256(p.read_bytes()).hexdigest())"
```

Expected: `b43bd0bee9d112e1219ba5867b4fb111db760cf948ad4c5415f6b4ee69dbd603`.

## 4. Every file included in the **outer** ZIP, what it does, and where it came from

**Provenance convention:** **Locally authored** means a new script or document created to orchestrate the official public sources, **not a copy** of an original PUNCH/Cybermonic script. For locally authored files, the links in the last column indicate the **upstream APIs or published experiment they are based on**; there is no original GitHub URL for those new files. **User upload** means preserved supplied content; no invented public download URL.

| Relative path inside kit | Provenance / exact purpose | Basis or upstream link |
|---|---|---|
| `README.md` | Locally authored top-level quickstart, status, prerequisite and limitation guide; now links to this document. | [Official CAGE evaluator docs](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/README.md); [Table 3](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021) |
| `BUILD_PROCESS_COMPLETE.md` | **This document**; records every outer-archive file, the original build, commands, known gaps and provenance. | Locally authored; sources in Section 2 |
| `sources.json` | Locally authored manifest holding three Git URLs, 40-character commits and target directories. Controls exact source fetching. | [CAGE GitHub](https://github.com/cage-challenge/cage-challenge-4), [PUNCH GitHub](https://github.com/PUNCH-Cyber/cage-4-submissions), [Cybermonic GitHub](https://github.com/cybermonic/cage-4-submission) |
| `bootstrap.py` | Locally authored clone/checkout/commit-verification and **optional** virtualenv dependency installation; emits `results/source_provenance.json`. | Upstream CAGE [requirements](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/Requirements.txt), Cybermonic [requirements](https://github.com/cybermonic/cage-4-submission/blob/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/requirements.txt) |
| `preflight.py` | Locally authored fast checker for repo hashes, five checkpoint files and needed Python imports; **not** a performance test. | Cybermonic [weights directory](https://github.com/cybermonic/cage-4-submission/tree/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/weights), official [CAGE dependencies](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/Requirements.txt) |
| `run_baselines.py` | Locally authored runner for PUNCH and Cybermonic, via **official** evaluator module; writes run metadata and logs; does not train TEMARL. | [CAGE evaluation.py](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/evaluation.py); [PUNCH submission](https://github.com/PUNCH-Cyber/cage-4-submissions/blob/9cc4ff83d600b0c810dad2ec428e35c0f3a0b6b0/punch_analyse_restore_v1/submission.py); [KEEP submission](https://github.com/cybermonic/cage-4-submission/blob/2afd652d80ce9d4051a07c23c2538f3dec6bb6c6/submission.py) |
| `make_comparison.py` | Locally authored result merger; refuses to turn missing/failed runs into scores; generates CSV with separate **published** and **measured** columns. | [Table 3](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021); [official summary.json writer](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/evaluation.py) |
| `START_WINDOWS.ps1` | Locally authored PowerShell entrypoint; Python 3.11 venv → fetch/install → preflight → 2-episode smoke → CSV. Requires Git, network, PowerShell and compatible wheels. | Delegates to local `bootstrap.py`, `preflight.py`, `run_baselines.py`, `make_comparison.py`; installation inputs are linked in Section 2 |
| `START_LINUX.sh` | Locally authored Linux/WSL2 equivalent of Windows script; runs `python3.11 -m venv` and the same smoke workflow. | Same local scripts and official upstream repos as above |
| `.gitignore` | Locally authored guard against committing `.venv/`, `external/`, `__pycache__`, generated result folders and `.pyc`. Not a comprehensive secrets scanner. | Local packaging hygiene; **no upstream source file** |
| `tests/test_harness.py` | Locally authored four Python `unittest` smoke checks for harness logic and result truthfulness. Does not execute CAGE episodes. | Local scripts `bootstrap.py`, `run_baselines.py`, `make_comparison.py`; Python standard library [`unittest`](https://docs.python.org/3/library/unittest.html) |
| `docs/EXPERIMENT_PROTOCOL.md` | Locally authored research plan: reproduction, TEMARL port, same-environment comparison and additional deception measures. | [CAGE journal paper](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021), [official evaluation program](https://github.com/cage-challenge/cage-challenge-4/blob/8c3c50ca54b176c2de199847944e8dcc035497e3/CybORG/Evaluation/evaluation.py) |
| `docs/REFERENCE_ARCHIVE_FILES.csv` | Generated file-by-file catalog for **all 2,274 entries** inside the user-supplied TEMARL reference ZIP, with path, original size, and coarse file role. | User-uploaded `camlds_real_full_arch (2).zip`; **no public source link**; classifications are indicative, not an audit of each file's code semantics |
| `reference/CAM_LDS_TEMARL_SOURCE_UNMODIFIED.zip` | **Exact preserved user upload**, containing original CAM-LDS TEMARL code/results. Included for provenance and future porting. Not consumed by `START_*` or the CAGE evaluator. | User upload `camlds_real_full_arch (2).zip`; SHA-256 in Section 3; **no external URL** |
| `external/.gitkeep` | Zero-byte placeholder so empty `external/` directory exists in ZIP. Real source repositories downloaded later. | Locally authored packaging placeholder; actual code URLs in Section 2 |
| `results/.gitkeep` | Zero-byte placeholder so `results/` exists before running. | Locally authored packaging placeholder; **no external URL** |
| `results/comparison.csv` | **Header only**, not a scientific result; shows fields `method,episodes,steps,seed,published_mean,published_sd,reproduced_mean,reproduced_sd,difference_reproduced_minus_published,source`. | Generated by local `make_comparison.py`; reference labels from [Table 3](https://onlinelibrary.wiley.com/doi/full/10.1002/aaai.70021) |

**Every other member** of the nested user archive is individually catalogued in `docs/REFERENCE_ARCHIVE_FILES.csv`. It is impractical to assign a distinct external paper link to 2,274 user-uploaded files, and many are experiment checkpoints, cache/compiled files or logs. The inventory makes the contents auditable without falsely attributing them to an outside source.

## 5. What happens if you RUN the extracted kit?

### A. Prerequisites

- **Preferred:** Ubuntu 22.04 or WSL2 on Windows, Python **3.11**, Git, internet access, free disk space for upstream code and Python packages, compatible CPU/GPU PyTorch installation.
- **Windows alternative:** PowerShell and the Python launcher (`py -3.11`), Git in PATH. Windows builds of Ray/PyTorch-Geometric can be problematic; WSL2 is recommended if dependency resolution fails.
- Do not run with a pre-existing `external/` directory containing unrelated non-Git files, because the source fetcher refuses to overwrite it.

### B. Extract and run the **smoke tests**

Linux / WSL2 (from the extracted kit root):

```bash
bash START_LINUX.sh
```

Windows PowerShell (from the extracted kit root):

```powershell
.\START_WINDOWS.ps1
```

What these scripts *attempt*, in order:

1. Create isolated `.venv/` Python 3.11 environment.
2. Clone and checkout the **exact** CAGE, PUNCH and Cybermonic commits under `external/`.
3. Install CAGE and Cybermonic dependency requirements; pip may produce an upstream incompatibility.
4. Check source hashes, imports and Cybermonic model weight files.
5. Run PUNCH and Cybermonic **2 episodes × 500 steps each** through the official CAGE evaluator, with seed `12501`.
6. Write a comparison CSV from successfully completed runs.

**Expected success artifacts (only if the real runtime succeeds):**

```text
external/cage/                    (fetched upstream simulator)
external/punch/                   (fetched upstream PUNCH code)
external/cybermonic/              (fetched upstream KEEP code/weights)
results/source_provenance.json
results/punch/episodes_2_seed_12501/
    invocation.json
    runner.log
    summary.json                  (plus full.txt, actions.txt, scores.txt from upstream evaluator)
results/cybermonic/episodes_2_seed_12501/
    invocation.json
    runner.log
    summary.json                  (plus upstream output files)
results/comparison.csv
```

If a dependency or evaluation fails, consult the displayed error and `runner.log`; the script stops without inventing a score. `invocation.json` records **failed** when the evaluator returns unsuccessfully. A successful 2-episode run is only an installation/functional smoke check, **not** a reproduction of a 100-episode journal statistic.

### C. Run the actual **standard** baseline evaluation

After smoke success, activate `.venv` and execute:

```bash
# Linux/WSL2
. .venv/bin/activate
python run_baselines.py --agents all --episodes 100 --seed 12502
python make_comparison.py
```

```powershell
# Windows PowerShell (from extracted kit root)
.\.venv\Scripts\python.exe run_baselines.py --agents all --episodes 100 --seed 12502
.\.venv\Scripts\python.exe make_comparison.py
```

Expected **only if completed successfully**:

- `results/punch/episodes_100_seed_12502/summary.json` and associated logs;
- `results/cybermonic/episodes_100_seed_12502/summary.json` and associated logs;
- new rows for those runs in `results/comparison.csv`, with reported mean and sample standard deviation and difference from **published** rounded reference values.

The comparison script currently expects exactly the upstream `summary.json` reward fields. It cannot manufacture the paper's **exact** original seeds or its original evaluation population. **A single user-chosen seed does not prove numerical equivalence with Table 3.** Same numeric seed for PUNCH and KEEP does not guarantee identical simulator trajectories once policies choose different actions. For strong statistical conclusions, expand the evaluation to a declared paired-seed/episode design with appropriate analysis.

### D. Run only the offline harness diagnostics

```bash
python -m unittest discover -s tests -v
python run_baselines.py --agents all --episodes 2 --seed 12501 --dry-run
python preflight.py
```

The **first** command tests local harness logic; the **second** merely prints the planned evaluation commands; the **third** checks whether source repos, checkpoints and Python imports are present. The third **will fail before setup**: that is expected.

## 6. How the previously discussed missing parts were handled (no gaps hidden)

| Known missing element / potential scientific gap | What was actually handled in this ZIP | What is **still missing** / what you must do next |
|---|---|---|
| **UC original policy** | Excluded from the automated baseline list. No replacement agent or invented UC results. | Locate a legally distributable original policy with the correct submission wrapper, or explicitly limit thesis comparison to PUNCH/KEEP. |
| **Lancer original policy and priority details** | Excluded, not approximated. | Find original code/configuration or omit the row; don't claim all-four-team reproduction. |
| **PUNCH runnable source** | Linked to the original `punch_analyse_restore_v1` directory; pinned repo commit, loads the original `submission.py`, wrapper and agent class. | Actually install compatible dependencies and run it; confirm the selected v1 was the submitted paper variant. |
| **Cybermonic trained weights** | Linked to original `weights/gnn_ppo-{0..4}.pt`; preflight checks all five. | Actually download model weights, verify compatibility and test inference under pinned environment. |
| **Table 3 simulator revision** | Uses a **precisely pinned current public revision** to avoid moving-head experiments; records provenance. | Establish its relationship to authors' original journal evaluation revision; any difference is a replication threat. |
| **Five robustness environment patches** | Documented as *deferred*; no unverified custom patch is passed off as official. | Obtain exact published modifications and setup; evaluate already trained agents under them, or report as independent reconstruction only. |
| **Published seeds / episode sampling** | Runner supports an explicit seed (`--seed`) and records the invocation. | Verify original journal seed protocol; run multiple independent seeds and report uncertainty where appropriate. |
| **PUNCH/Cybermonic dependency mismatch** | Explicit install attempts from both upstream requirements; errors are exposed, not silently suppressed. | Resolve Python/Ray/PyTorch/PyG version compatibility in a documented environment; freeze a `pip freeze` lock after successful validation. |
| **TEMARL CAGE 4 integration** | User's complete uploaded CAM-LDS project is included **unmodified for reference**; protocol describes required adapter and retraining. | **No functioning TEMARL agent in this ZIP.** Implement CAGE five-agent observation/action wrappers, policy/network changes, train new CAGE model, and produce genuine results. |
| **CAGE 4's five blue defenders vs CAM-LDS four zones** | Explicitly called out as a mismatch. | Do not relabel four zones as five agents; design and validate proper CAGE agent mapping. |
| **Deception success / attacker interaction / engagement duration** | Not fabricated. Protocol identifies the telemetry that would be needed. | Instrument actual decoy deployments and red-decoy interactions, choose objective denominators, evaluate every agent consistently; reward alone is insufficient. |
| **CasinoLimit dataset and five splits** | Not used for CAGE 4 Table 3 reproduction. Its use in your separate encoder study remains distinct. | If desired, retain CasinoLimit five-split experiments as a **separate** trace-driven evaluation; do not copy their scores into CAGE reward tables. |
| **No observed human response to new decoys** | Does not claim such data exist. | Label simulator outcomes as simulation; evaluate model assumptions and, if possible, run a controlled interactive study. |
| **Comparability and generalization** | One official evaluator and explicit source hashes for both available baselines. | To compare TEMARL fairly, run it in the **same** CAGE environment/scoring/action space/seeds with additional decoy-specific metrics. |
| **Source licensing** | Upstream repositories are **not redistributed**, only downloaded via clone. | Review each upstream license before code redistribution or derivative publication. |

**Bottom line:** This kit *addresses available-code procurement and documentation gaps*, but it **does not overcome** missing policy source, unverified original experimental revisions, dependency conflicts, or the absent CAGE 4 TEMARL port. Any claim that the ZIP already reproduces the Table 3 scores or compares deception outcomes would be false.

## 7. Expected **final research result** after completing missing work

Once the baseline code really executes and TEMARL has been implemented and trained **inside CAGE 4**, the scientifically valid comparison is a **new table with measurements obtained in the same environment**:

| Method | CAGE mean cumulative reward (100 × 500) | Decoy interaction rate | Attacker goal success | Decoy resource cost |
|---|---|---|---|---|
| PUNCH v1 | To reproduce | To measure | To measure | To measure |
| Cybermonic KEEP | To reproduce | To measure | To measure | To measure |
| TEMARL / adapted encoder + RL | **Not implemented** | Not measured | Not measured | Not measured |
| TEMARL NoHistory | **Not implemented** | Not measured | Not measured | Not measured |

The first **two** rows can be attempted with this scaffold. The TEMARL rows **cannot** be produced by the existing scripts. The paper's original published scores must remain in a **separate reference column**, not be presented as newly measured data.

## 8. Troubleshooting and practical checks

- **`py -3.11` or `python3.11` not found:** install Python 3.11; do not silently switch to an arbitrary installed Python version.
- **Git clone/fetch cannot reach GitHub:** check internet/proxy/certificate setup. No upstream repo copies are bundled in this ZIP.
- **PyTorch / PyTorch Geometric / Ray conflict:** upstream requirements differ; use a clean Python 3.11 environment, inspect pip errors, record any version changes in a lockfile. Do not claim exact reproduction if you alter tested software versions without validation.
- **Missing `gnn_ppo-*.pt`:** verify `external/cybermonic/weights` was fetched correctly and the paths match source `submission.py`; do not substitute random weights.
- **`summary.json` missing:** the evaluation failed or did not finish; inspect `runner.log`, `invocation.json`, output directory and imports. No numeric result is valid until evaluation completes.
- **Existing output directory:** the script blocks overwriting completed results; choose a new seed or archive old runs manually, preserving provenance.
- **Near-but-not-identical paper reward:** check upstream commit, dependencies, evaluation wrapper, seed protocol, runtime stochasticity and score definition; investigate rather than modifying scores.
- **To see all files inside the bundled CAM-LDS project:** open `docs/REFERENCE_ARCHIVE_FILES.csv` with a spreadsheet or text viewer; it records **each** nested file and its coarse role.

## 9. Validation summary for this revised archive

- Identified and documented the exact outer kit files (see Section 4).
- Verified the preserved source ZIP's SHA-256 against the user upload: **match**.
- Unit-tested local harness logic: **4 tests passed**.
- Checked dry-run command construction: **PUNCH and Cybermonic commands printed**.
- Checked ZIP format integrity after repackaging: see delivery message.
- **Not performed:** Git source cloning in a reproducibility-ready environment, pip compatibility installation, 2-episode CAGE runtime, 100-episode CAGE reproduction, CAGE-adapted TEMARL training, or any head-to-head deception evaluation.

**Accurate deliverable label: “documented and offline-tested CAGE 4 baseline reproduction kit.”** It is not a “fully reproduced Table 3” or a “fully functioning TEMARL-vs-PUNCH-vs-KEEP experiment.”
