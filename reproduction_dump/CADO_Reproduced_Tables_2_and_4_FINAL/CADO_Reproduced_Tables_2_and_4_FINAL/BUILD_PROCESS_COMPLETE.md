# BUILD_PROCESS_COMPLETE.md — CADO Tables 2 and 4 full reproducibility package

Prepared 22 November 2026. **The supplementary source was uploaded by the user and has not been modified.**

## 1. Research target and result

- Paper: **CADO: Constraint-Aware Alert-to-Deception Orchestration for Heterogeneous Security Controls**, *Future Internet* 18(10), article 552 (2026).
- Publisher: https://www.mdpi.com/1999-5903/18/10/552
- DOI: https://doi.org/10.3390/fi18100552
- Official supplementary archive (S1): https://www.mdpi.com/article/10.3390/fi18100552/s1
- User-provided input: `futureinternet-18-00552-s001.zip` (624,999 bytes; SHA-256 `edac2fa9db714c6ab7bcad7d0f83a2dd68e52d2760daa8a2ab4172d8252c6447`).

**Scope of successful reproduction:** 1,440 primary episode records, 360 held-out episode records, 1,710 ablation episode records and the original seed-level summary statistics and held-out paired statistical results. The primary Table 2 and held-out Table 4 metric numbers match. The original synthetic simulator was genuinely executed, not mimicked by a table transcription. The independent files are in `independent_results/` and `tables/`.

**Caveats:** A missing `README.md` in the official manifest and tiny differences in two primary paired-test p-value columns prevent a claim of universal byte-for-byte numerical reproduction. Timings cannot be reproduced across hardware.

## 2. Step-by-step construction procedure (exactly what was done)

1. **Obtain authentic source.** Took the uploaded `futureinternet-18-00552-s001.zip` from this conversation; it corresponds to the publisher S1 download linked above. Saved it unchanged in `original_archive/`.
2. **Validate input ZIP.** Used Python `zipfile.ZipFile.testzip()`; result `None` (no CRC error). Enumerated 63 archive entries, including directory entries.
3. **Safely extract.** Checked every archive member stays within the intended extraction folder and extracted without modifying the source. Copied extracted bytes to `publisher_source/`.
4. **Check author manifest.** Read `publisher_source/SHA256SUMS.txt`; 57 declarations, 56 SHA-256 matches, one absent path (`README.md`), zero hash mismatches for available paths. The author `code/verify_manifest.py` cannot pass without that absent file. Did not invent a replacement.
5. **Inspect primary code and requirements.** Read `run_experiments.py`, `reproduce_submitted.py`, `revision_analysis.py`, `export_revision_tables.py`, local prototype scripts and `requirements.txt`. Confirmed the experiment is synthetic with four policies; no pretrained neural or MARL model is required.
6. **Record software environment.** Used Python 3.13.5 (Linux), NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, matplotlib 3.10.8; author pins different versions in `requirements.txt`. Exact details in `evidence/environment_and_source_integrity.json`.
7. **Create isolated working copy.** Made a temporary copy of the entire extracted supplement. All original files remained unmodified. Source functions were called only inside that temporary working directory.
8. **Rerun simulation.** Started `python code/reproduce_submitted.py`. It generated new primary, OOD and fault CSVs but exceeded a command time limit while processing ablations. Saved that partial progress log as `evidence/reproduction_run.log`. Then finished the ablation, normalization and statistical stages via the **same original** `run_experiments.py` functions without touching fixed model parameters. See `ablation_run.log`.
9. **Rerun revision/OOD analyses.** Executed `python code/revision_analysis.py`. This regenerated the 26-setting sensitivity grid, 30-seed held-out paired inference, exact episode reanalysis and model decision checks. Saved console output in `evidence/revision_run.log`.
10. **Rerun original LaTeX exporter.** Executed `python code/export_revision_tables.py`. Original archived and freshly exported LaTeX table bodies match; only CRLF versus LF differences remain. The source exporter reads author submitted summary for primary formatting; independent numeric checks compare that summary to independently generated summaries at tolerance 1e-12.
11. **Rerun prototype.** Executed `python prototype/run_poc.py` against localhost only; all 300 expected outcomes passed. Executed `python code/verify_claims.py`, and saved both logs.
12. **Compare true outputs.** Created `tools/verify_package.py`, which reads every original and new scientific CSV and checks numeric values with absolute tolerance 1e-12 and relative tolerance zero. Timing measurements are explicitly excluded. The primary and held-out target tables passed.
13. **Record discrepancies instead of adjusting data.** The author strict `reproduce_submitted.py --verify-only` was executed and failed in the primary `paired_statistical_comparisons.csv` p-value columns. We kept its traceback in `evidence/full_verify.log`; wrote precise differences into `evidence/independent_scientific_comparison.json`. No posthoc tuning or hard-coded target values were used.
14. **Make tables from our own outputs.** Authored and ran `tools/export_tables.py`, generating `tables/table2_primary_independently_reproduced.csv`, `tables/table4_heldout_independently_reproduced.csv`, `tables/REPRODUCED_TABLES.md`.
15. **Audit and validate package.** Wrote the Devil’s Advocate analysis and a standalone rerun helper, and ran 9 package tests. All passed. Exported the full Markdown record and SHA-256 inventory, then constructed and CRC-tested the final ZIP.

## 3. Published-target experiment configuration

| Parameter | Original source setting |
|---|---|
| Synthetic master seed | `20260818` |
| Independent statistical unit | 30 paired random seeds |
| Alerts/events in each simulated episode | 120 |
| Primary scenario grid | office, research, data_service |
| Primary attacker profiles | credential, lateral, web, hybrid |
| Held-out attacker | slow_blend |
| Policies | Static, Adaptive, Consensus, CADO |
| Policy action levels | Observe / Honeypoint / Honeyproxy / Honeytrace |
| Confidence intervals | 10,000 seed-level bootstrap resamples |
| Target significance tests | Paired Wilcoxon with Holm correction where authored |
| Input type | Simulated alerts and attack outcomes, **not real attack logs** |

## 4. Final numeric result — Table 2 (primary)

| Metric | Static | Adaptive | Consensus | CADO |
|---|---:|---:|---:|---:|
| Defensive utility | 0.6853 | 0.6213 | 0.6953 | **0.7020** |
| Redirection precision | 0.6847 | 0.5908 | 0.6978 | **0.7282** |
| Engagement rate | 0.9416 | 0.9993 | 0.9999 | 0.9999 |
| Benign false redirects | 0.002897 | 0.105962 | 0.000082 | 0.000082 |
| Unsafe actions | 0.001944 | 0.065000 | 0.000046 | 0.000046 |
| Normalized cost | 0.05788 | 0.09618 | 0.07573 | **0.07538** |

These match the published rounded values; machine-precision unrounded values and CI columns are in `tables/table2_primary_independently_reproduced.csv`. Generated by the original simulator and postprocessed, not copied from a table.

## 5. Final numeric result — held-out Table 4

| Metric | Consensus | CADO | Paired difference | Holm-adjusted p |
|---|---:|---:|---:|---:|
| Defensive utility | 0.6572 | **0.6590** | +0.001792 | 0.000505 |
| Redirection precision | 0.5549 | **0.5745** | +0.019640 | 0.001571 |
| Engagement rate | 1.0000 | 1.0000 | 0 | 1.000000 |
| Benign false redirects | 0.000299 | 0.000299 | 0 | 1.000000 |
| Unsafe actions | 0.000185 | 0.000185 | 0 | 1.000000 |
| Normalized cost | **0.07108** | 0.07288 | +0.001800 | 0.000182 |

This experiment does not uniformly favor CADO: held-out redirection/utility improved, **cost increased**. See the paper for the original evaluation interpretation. Exact intervals, effect sizes and p-values: `tables/table4_heldout_independently_reproduced.csv`.

## 6. Independent verification status, missing materials, and how they were handled

| Item | Outcome and handling |
|---|---|
| Earlier unavailable MDPI download | Resolved by the user uploading the official S1 ZIP. Kept complete original and extracted copy. |
| Original official ZIP | Integrity checked: 63 entries and clean CRC. |
| Source files needed to rerun Tables 2 and 4 | Present (`code/run_experiments.py`, `revision_analysis.py`, original results). |
| Source archive manifest | 56 present checksums match; **README.md missing**. Preserved original without changing hashes. |
| Table 2 primary and Table 4 held-out | Fresh run **matches** archived scientific CSVs within 1e-12; held-out paired values match. |
| All original scientific statistics | Not strictly identical: two primary paired p-value rows differ by at most 5.71803005819257e-7 in adjusted p. Exact-diagnostic JSON and traceback retained. |
| Execution time limit | One-line rerun interrupted during ablation; resumed using original source functions, completed and checked results. |
| Statistical environment | Author pins SciPy 1.15.3; this run uses 1.17.0. This may explain p-value drift, but that cause was **not experimentally verified**. |
| Host/CPU timings | Intentionally not treated as reproducible across machines; recorded in CSV but excluded from numerical matching. |
| Live attacker/field data | Not part of CADO experiment; synthetic outcomes only. No real traffic or real hardware claims made. |
| Learned model checkpoints | Not applicable: CADO is a policy/orchestration baseline rather than a trained neural/MARL model. |
| Full replay into TEMARL | Not performed. Requires a fair shared simulator, compatible action mapping and unchanged seeds, observations and metric definitions. |
| Missing LICENSE | No explicit LICENSE file in the uploaded source; refer to publisher reuse conditions before redistribution. |

## 7. End-user instructions and expected end result

### Quick offline validation (uses included rerun data)

```powershell
python -m pip install -r publisher_source/requirements.txt
python tools/verify_package.py
python -m unittest discover -s tests -v
python tools/export_tables.py
```
Expected `verify_package.py` result: `table2_reproduced=true`, `table4_heldout_reproduced=true`, `all_submitted_csv_agree=false` (only the two known primary p-value columns), `original_manifest_matched=56`, `original_manifest_missing=["README.md"]`. The latter two are **expected reported limitations, not suppressed successes**.

### New independent rerun from original simulator

```powershell
python tools/reproduce_again.py --output local_rerun
# Additional ablations and normalization:
python tools/reproduce_again.py --output local_rerun_full --full
# Optional 300 local HTTP prototype tests (isolated 127.0.0.1):
python tools/reproduce_again.py --output local_rerun_http --prototype
```
This makes **new directories** and refuses to overwrite any existing path. It runs the author source in a private working copy and then checks the generated outputs. It never replaces the uploaded original.

### Original upstream commands, if you want to replicate the whole protocol manually

```bash
cd publisher_source
python code/reproduce_submitted.py   # can be computationally substantial; strict p-value equality may fail under different SciPy
python code/revision_analysis.py
python code/export_revision_tables.py
python prototype/run_poc.py
python code/verify_claims.py
python code/verify_manifest.py       # KNOWN FAILURE: archive lacks README.md
```
The included source and its files are **authored by CADO researchers**, not newly invented here. The new independent tooling and accompanying explanation are clearly separated.

## 8. File-by-file inventory, sources and exact purpose

Every delivered file is individually identified below. `Original S1` means the unchanged user-uploaded official MDPI supplement. `Independent` means the original source code was executed in this session to generate that output. `Local` means created as an audit/documentation tool here. Source links point to the **public original publisher record** for provenance; our local scripts are not attributed to that publisher.

| Path in ZIP | Provenance / source link | Reason this file exists |
|---|---|---|
| `BUILD_PROCESS_COMPLETE.md` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | This comprehensive step-by-step, file-by-file construction/provenance/reproduction report. |
| `FILE_BY_FILE_INDEX.csv` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Machine-readable inventory of every packaged file, size, SHA-256 and its purpose and source. |
| `README.md` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Entry point, verified reproduction status, recommended commands and caveats. |
| `RUN_LINUX.sh` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Bash entry point to verify the packaged scientific outputs. |
| `RUN_WINDOWS.ps1` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | PowerShell entry point to verify current scientific outputs with clear rerun instructions. |
| `SHA256_PACKAGE.csv` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Checksums of all other packaged files; omits itself to avoid a circular hash. |
| `docs/DEVILS_ADVOCATE_REVIEW.md` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Adversarial audit of exact table matching, missing original README, p-value drift, simulation scope, and fairness concerns. |
| `docs/METRICS_AND_TEMARL_COMPARISON.md` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | CADO settings, metric definitions, 4 deception actions and instructions for fair TEMARL baseline experiments. |
| `evidence/ablation_run.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Console proof of resumed fresh ablation and normalization runs after the full-command timeout. |
| `evidence/claims_run.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Console output of the authors original claims verification script executed on the working copy. |
| `evidence/environment_and_source_integrity.json` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Python/platform/library versions, original archive SHA-256, size, CRC status and manifest discrepancy. |
| `evidence/full_verify.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Actual strict original verify-only failure demonstrating p-value discrepancy; never suppressed. |
| `evidence/independent_scientific_comparison.json` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Our independent file-wise numeric comparison, 1e-12 tolerance, mismatches and exact missing-file evidence. |
| `evidence/prototype_run.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Console output of fresh 300-case local HTTP integration reproduction. |
| `evidence/reproduction_run.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Partial initial author one-line rerun log; time limit interrupted full ablation stage, documented explicitly. |
| `evidence/revision_run.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Console output of 26-settings revision analysis and held-out statistical table generation. |
| `evidence/tables_export.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Console output from the source LaTeX table export script. |
| `evidence/unit_tests.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Nine local regression tests validating both target tables and known anomalies. |
| `evidence/verify_package.log` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Output from the independent package verification command. |
| `independent_results/reproduced_results/ablation_episode_metrics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Full gate/constraint ablation episode metrics across primary and held-out variants (1,710 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/ablation_seed_summary.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation results summarized at the seed level (210 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/ablation_summary.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation variant means for safety gate comparison (7 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/experiment_config.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Frozen simulation settings, attack scenarios, four policy names, master seed, libraries and statistical settings. Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/fault_injection_metrics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Fault-injection decision/recovery simulation metrics (120 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/normalization_benchmark.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Input-format normalization benchmark including host-dependent timing/throughput. Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/ood_episode_metrics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode slow_blend held-out attacker scores (360 rows); core raw evidence for held-out Table 4. Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/ood_seed_summary.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out per-seed averages (120 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/paired_statistical_comparisons.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary dataset paired Wilcoxon and corrected-p comparisons; tiny primary p-value drift in independent environment documented. Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/primary_episode_metrics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode primary attack/scenario/policy scores for 30 seeds (1,440 rows); core raw evidence for Table 2. Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/primary_seed_summary.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary per-seed means across the scenario/attacker grid (120 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/reproduced_results/summary_statistics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary and held-out summary statistics and bootstrap confidence intervals (45 rows); direct input to primary table. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/claim_verification.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Generated assertion results for specified policy invariants, local prototype and negative sensitivity case. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/default_episode_reanalysis.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Vectorized reanalysis of primary+held-out Consensus/CADO default decisions (900 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/heldout_paired_statistical_comparisons.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out paired comparison of CADO against Static, Adaptive and Consensus with corrected p-values (18 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/heldout_summary_statistics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out mean and 95% bootstrap CI per policy and deception metric (24 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/latex_tables/ablation.tex` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX safety-gate ablation table and Consensus references. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/latex_tables/heldout.tex` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX representation of the held-out comparison (Table 4), including paired differences and adjusted p-values. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/latex_tables/primary.tex` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX representation of the primary Table 2, including all four policies and 95% CIs. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/latex_tables/prototype.tex` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX local HTTP prototype acceptance table. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/latex_tables/sensitivity.tex` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX sensitivity configuration family ranges. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/poc_http_requests.jsonl` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Recorded local HTTP request-response events from 300 prototype trials (4,170 events). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/poc_state_journal.jsonl` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Hash-linked state journal from local rollback/verification workflow (1,770 entries). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/poc_summary.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Prototype aggregate acceptance results, counts and restoration outcomes (300/300 test criteria). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/poc_trials.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-trial local prototype acceptance, recovery and timing metrics (300 rows). Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/poc_workflow_example.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Illustrative single normalized-alert-to-CADO-action and proxy workflow fixture. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/primary_heldout_consensus_paired.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Paired CADO-versus-Consensus results for primary and held-out datasets; directly supports held-out table. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/reproduction_validation.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Independent vectorized-versus-scalar/source checks, including 4,200 scalar decisions. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/revision_environment.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Author revision environment, master seed, bootstrap count and code hash. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/sensitivity_paired_comparisons.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Seed-paired sensitivity analysis outputs for all 26 parameter settings. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/sensitivity_seed_metrics.csv` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-seed sensitivity data across datasets and configurations. Fresh independent run (not the author-provided reference). |
| `independent_results/revision_results/sensitivity_settings.json` | [Independent](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Exact 26 exploratory perturbation settings used by the authors. Fresh independent run (not the author-provided reference). |
| `original_archive/futureinternet-18-00552-s001.zip` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Unchanged exact user-uploaded official MDPI S1 archive, retained as byte-for-byte provenance. |
| `publisher_source/SHA256SUMS.txt` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Publisher-supplied per-file SHA256 manifest; 57 declarations, 56 present and matching, README.md missing. |
| `publisher_source/code/export_revision_tables.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Formats archived CSV results into five LaTeX manuscript tables, including primary and held-out tables. |
| `publisher_source/code/generate_cado_architecture.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Draws the CADO architecture schematic used in paper visualizations. |
| `publisher_source/code/plot_figure3_annotation_adjusted.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Recreates/adjusts annotated Figure 3 from source experiment data. |
| `publisher_source/code/reproduce_submitted.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Author-provided full rerun and 1e-12 comparison against archived results; host timing excluded. Our pinned-version drift prevents an unqualified pass. |
| `publisher_source/code/revision_analysis.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Original vectorized reanalysis, 26 sensitivity configurations, held-out paired tests, safety-gate and no-label-leakage checks. |
| `publisher_source/code/run_experiments.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Original simulation engine: synthetic event generation, four policies, 30 paired seeds, risk scoring, primary/OOD/fault/ablation runs, and summary statistics. |
| `publisher_source/code/verify_claims.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Original claim-checking assertions about bounded adaptations, benign invariance, sensitivity, and local-prototype counts. |
| `publisher_source/code/verify_manifest.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Original SHA256 integrity checker; reveals a missing README.md declared by the supplied SHA256SUMS.txt. |
| `publisher_source/prototype/poc_services.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Isolated loopback-only HTTP mock protected, decoy and proxy services for device/control-plane tests. |
| `publisher_source/prototype/run_poc.py` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Exercises 10 fault/control-plane cases x30 iterations and writes request, journal, trial and summary artifacts. |
| `publisher_source/reproduced_results/ablation_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Full gate/constraint ablation episode metrics across primary and held-out variants (1,710 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/ablation_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation results summarized at the seed level (210 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/ablation_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation variant means for safety gate comparison (7 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/experiment_config.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Frozen simulation settings, attack scenarios, four policy names, master seed, libraries and statistical settings. Author-provided previously rerun version. |
| `publisher_source/reproduced_results/fault_injection_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Fault-injection decision/recovery simulation metrics (120 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/normalization_benchmark.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Input-format normalization benchmark including host-dependent timing/throughput. Author-provided previously rerun version. |
| `publisher_source/reproduced_results/ood_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode slow_blend held-out attacker scores (360 rows); core raw evidence for held-out Table 4. Author-provided previously rerun version. |
| `publisher_source/reproduced_results/ood_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out per-seed averages (120 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/paired_statistical_comparisons.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary dataset paired Wilcoxon and corrected-p comparisons; tiny primary p-value drift in independent environment documented. Author-provided previously rerun version. |
| `publisher_source/reproduced_results/primary_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode primary attack/scenario/policy scores for 30 seeds (1,440 rows); core raw evidence for Table 2. Author-provided previously rerun version. |
| `publisher_source/reproduced_results/primary_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary per-seed means across the scenario/attacker grid (120 rows). Author-provided previously rerun version. |
| `publisher_source/reproduced_results/summary_statistics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary and held-out summary statistics and bootstrap confidence intervals (45 rows); direct input to primary table. Author-provided previously rerun version. |
| `publisher_source/requirements.txt` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Author-pinned Python dependency requirements: numpy, pandas, scipy, matplotlib. |
| `publisher_source/revision_results/claim_verification.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Generated assertion results for specified policy invariants, local prototype and negative sensitivity case. Original archived version. |
| `publisher_source/revision_results/default_episode_reanalysis.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Vectorized reanalysis of primary+held-out Consensus/CADO default decisions (900 rows). Original archived version. |
| `publisher_source/revision_results/full_reproduction_audit.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Authors own archived verification report; not independent evidence from this session. Original archived version. |
| `publisher_source/revision_results/heldout_paired_statistical_comparisons.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out paired comparison of CADO against Static, Adaptive and Consensus with corrected p-values (18 rows). Original archived version. |
| `publisher_source/revision_results/heldout_summary_statistics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out mean and 95% bootstrap CI per policy and deception metric (24 rows). Original archived version. |
| `publisher_source/revision_results/latex_tables/ablation.tex` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX safety-gate ablation table and Consensus references. Original author's archived version. |
| `publisher_source/revision_results/latex_tables/heldout.tex` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX representation of the held-out comparison (Table 4), including paired differences and adjusted p-values. Original author's archived version. |
| `publisher_source/revision_results/latex_tables/primary.tex` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX representation of the primary Table 2, including all four policies and 95% CIs. Original author's archived version. |
| `publisher_source/revision_results/latex_tables/prototype.tex` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX local HTTP prototype acceptance table. Original author's archived version. |
| `publisher_source/revision_results/latex_tables/sensitivity.tex` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | LaTeX sensitivity configuration family ranges. Original author's archived version. |
| `publisher_source/revision_results/poc_http_requests.jsonl` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Recorded local HTTP request-response events from 300 prototype trials (4,170 events). Original archived version. |
| `publisher_source/revision_results/poc_state_journal.jsonl` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Hash-linked state journal from local rollback/verification workflow (1,770 entries). Original archived version. |
| `publisher_source/revision_results/poc_summary.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Prototype aggregate acceptance results, counts and restoration outcomes (300/300 test criteria). Original archived version. |
| `publisher_source/revision_results/poc_trials.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-trial local prototype acceptance, recovery and timing metrics (300 rows). Original archived version. |
| `publisher_source/revision_results/poc_workflow_example.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Illustrative single normalized-alert-to-CADO-action and proxy workflow fixture. Original archived version. |
| `publisher_source/revision_results/primary_heldout_consensus_paired.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Paired CADO-versus-Consensus results for primary and held-out datasets; directly supports held-out table. Original archived version. |
| `publisher_source/revision_results/reproduction_validation.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Independent vectorized-versus-scalar/source checks, including 4,200 scalar decisions. Original archived version. |
| `publisher_source/revision_results/revision_environment.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Author revision environment, master seed, bootstrap count and code hash. Original archived version. |
| `publisher_source/revision_results/sensitivity_paired_comparisons.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Seed-paired sensitivity analysis outputs for all 26 parameter settings. Original archived version. |
| `publisher_source/revision_results/sensitivity_seed_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-seed sensitivity data across datasets and configurations. Original archived version. |
| `publisher_source/revision_results/sensitivity_settings.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Exact 26 exploratory perturbation settings used by the authors. Original archived version. |
| `publisher_source/submitted_results/ablation_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Full gate/constraint ablation episode metrics across primary and held-out variants (1,710 rows). Author-submitted version. |
| `publisher_source/submitted_results/ablation_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation results summarized at the seed level (210 rows). Author-submitted version. |
| `publisher_source/submitted_results/ablation_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Ablation variant means for safety gate comparison (7 rows). Author-submitted version. |
| `publisher_source/submitted_results/experiment_config.json` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Frozen simulation settings, attack scenarios, four policy names, master seed, libraries and statistical settings. Author-submitted version. |
| `publisher_source/submitted_results/fault_injection_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Fault-injection decision/recovery simulation metrics (120 rows). Author-submitted version. |
| `publisher_source/submitted_results/normalization_benchmark.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Input-format normalization benchmark including host-dependent timing/throughput. Author-submitted version. |
| `publisher_source/submitted_results/ood_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode slow_blend held-out attacker scores (360 rows); core raw evidence for held-out Table 4. Author-submitted version. |
| `publisher_source/submitted_results/ood_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Held-out per-seed averages (120 rows). Author-submitted version. |
| `publisher_source/submitted_results/paired_statistical_comparisons.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary dataset paired Wilcoxon and corrected-p comparisons; tiny primary p-value drift in independent environment documented. Author-submitted version. |
| `publisher_source/submitted_results/primary_episode_metrics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Per-episode primary attack/scenario/policy scores for 30 seeds (1,440 rows); core raw evidence for Table 2. Author-submitted version. |
| `publisher_source/submitted_results/primary_seed_summary.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary per-seed means across the scenario/attacker grid (120 rows). Author-submitted version. |
| `publisher_source/submitted_results/summary_statistics.csv` | [Original S1](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Primary and held-out summary statistics and bootstrap confidence intervals (45 rows); direct input to primary table. Author-submitted version. |
| `tables/REPRODUCED_TABLES.md` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Concise readable summary of reproduced primary and held-out deception results. |
| `tables/table2_primary_independently_reproduced.csv` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Six Table 2 metrics reaggregated from freshly rerun 30-seed primary summaries, with all four policy means and bootstrap CI bounds. |
| `tables/table4_heldout_independently_reproduced.csv` | [Local](https://www.mdpi.com/article/10.3390/fi18100552/s1) | Six held-out comparison metrics from freshly rerun seed-level revision analysis, with paired differences and tests. |
| `tests/test_package.py` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Nine automated regression tests for output shapes, values, missing-manifest file and p-value exception. |
| `tools/export_tables.py` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Our standalone, no-hardcoded-results table exporter from independent outputs into readable Markdown and CSV. |
| `tools/reproduce_again.py` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Our clean-workspace rerun orchestration, copying original code without altering the publisher source. |
| `tools/verify_package.py` | [Local](https://www.mdpi.com/1999-5903/18/10/552) | Our scientific-data comparison, publisher-manifest deficiency reporter and target-table pass/fail tests. |

## 9. Checksums and exact package contents

- `FILE_BY_FILE_INDEX.csv` provides a machine-readable inventory, SHA-256 digest and purpose for all files except the unavoidable self-referential inventory rows.
- `SHA256_PACKAGE.csv` contains SHA-256 digests of all other final package files, including this Markdown report. It omits its own SHA to avoid a circular reference.
- `original_archive/futureinternet-18-00552-s001.zip` exactly preserves the uploaded binary. The entire contents were additionally extracted verbatim into `publisher_source/`.
- The final ZIP was built with Python `zipfile` and CRC-tested after it was closed. There is no omitted source-code folder, hidden plugin, offsite training checkpoint or fabricated missing source data.

## 10. Interpret results correctly for the thesis

This evidence supports a rigorous **within-CADO-simulator** reproduction of the published primary and held-out deception outcomes. It does **not** establish external validation on real networks, reproduce hardware-dependent timings, or prove TEMARL superiority. For fair model comparison, keep random episodes, action semantics, observation visibility, reward functions, pairing and confidence-interval procedures identical. If modified policies are used, label them as adaptations rather than exact original models.

### Source references

- MDPI full article: https://www.mdpi.com/1999-5903/18/10/552
- Official DOI: https://doi.org/10.3390/fi18100552
- MDPI supplementary archive (user-uploaded file): https://www.mdpi.com/article/10.3390/fi18100552/s1
- Source root in package: `publisher_source/` (author-supplied unchanged).
- Source-derived independent run: `independent_results/` (freshly calculated).

*End of complete build, provenance and execution report.*
