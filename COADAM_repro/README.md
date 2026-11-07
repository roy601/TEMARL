# Co-ADAM reproduction attempt — Tables 5 and 6

One launcher runs **two tracks × ten fixed training seeds**, each including all eight methods and both attacker regimes. This is not two individual training jobs. The package does not search for seeds/settings that match the paper. No TEMARL changes are made.

**Status:** Python packaging/report tests can run here. MATLAB is unavailable on the preparation PC; MATLAB training has NOT been executed or certified. A mandatory two-track smoke test must pass on the lab PC before the full study starts. The author's original table-generating configuration remains unconfirmed; assumptions are listed in [PROTOCOL.md](PROTOCOL.md).

## Quick start on the lab PC

Install **Python 3.12**, **MATLAB R2025b or newer**, and **Statistics and Machine Learning Toolbox**. The source uses handwritten numeric DQN, not PyTorch; installing CUDA PyTorch does not help this runner. The upstream README also recommends Deep Learning Toolbox, although the selected execution path does not call its network APIs. Keep sufficient RAM/disk for tabular Q matrices and 20 sets of checkpoints; 16 GB RAM and several GB free disk are prudent starting provisions, not measured requirements. Runs are sequential.

Copy this entire folder, then open PowerShell inside it:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1
```

If MATLAB is elsewhere:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1 -Matlab "C:\Program Files\MATLAB\R2025b\bin\matlab.exe"
```

The command installs Python reporting dependencies, runs tests, runs smoke checks, trains/evaluates both tracks and writes reports. MATLAB progress streams to the terminal and timestamped logs. There is no GPU requirement and no reliable runtime estimate before the smoke test.

## Dataset

**No external dataset download is required for this default run.** It uses the official release's `environment_config.mat` and `threat_profiles.mat`. The environment generates interactions from that configuration; it does not train directly on CSV traffic rows. The `dataset/` folder is provided for your downloads, but files placed there are **not silently loaded**. See [dataset/README.md](dataset/README.md).

To use independently regenerated author-format configuration files, supply both MAT files in one folder:

```powershell
.\.venv\Scripts\python.exe -u run_study.py --config-dir .\dataset\processed --output .\outputs\rebuilt_config --matlab "C:\Program Files\MATLAB\R2025b\bin\matlab.exe"
```

That is a separate experiment and cannot be presented as the unchanged released configuration. The original preprocessing scripts are included for inspection; their local absolute paths require adaptation and their raw-input versions have not been validated here. This package does not claim to rebuild the raw-data preprocessing experiments.

## Outputs

- `outputs/main/RESULTS.md`: both target tables for both tracks, published-versus-obtained differences, every seed's ten metrics, degradation score and training summaries.
- `outputs/main/episodes.csv`: every evaluation episode and metric.
- `outputs/main/seed_summary.csv`: means and episode SDs for every seed.
- `outputs/main/<track>/seed_XX/results/`: MATLAB model artifacts, raw baseline metrics, training curves.
- Each cell also has generated source, diffs against upstream, settings, stage markers and logs.
- `outputs/main/manifest.json`: frozen protocol and source/configuration SHA-256 hashes.
- `outputs/main_smoke/`: software checks only; never mix with full results.

The main report uses **mean ± SD across training-seed means**. Separate per-seed tables show **mean ± SD across evaluation episodes**, which is closer to the paper's reporting unit. Neither SD should be substituted for the other.

## Resume and errors

Repeat the same launch command. Completed stages are skipped only after their artifacts pass hash checks. A failed stage restarts from its beginning; mid-episode/mid-stage optimizer state is NOT resumed. Completed seeds are retained. There is no automatic retry of failed scientific runs with a new seed. Windows atomic-write failures receive bounded retries; do not disable antivirus.

If interrupted or the PC crashes, a `RUNNING.lock` may remain. Confirm the study's Python/MATLAB processes have stopped, then remove **only** that lock in the output directory before resuming. Changed code/protocol/configuration requires a new output directory. Do not delete markers to force changed results into an old experiment.

Generate the report without training:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\run_lab.ps1 -ReportOnly
```

Smoke only: add `-SmokeOnly`. Inspect generated source without MATLAB: `python run_study.py --prepare-only` (does not simulate a successful run).

## Scope and sources

Targets: [paper DOI](https://doi.org/10.1038/s41598-026-60920-0), Tables 5 and 6. Source: [official GitHub repository](https://github.com/Usmanjibril09/CoADAM), pinned commit `69defb709190547c99ff54ca4f9fb6ade7e510d6`.

The archived upstream results are historical evidence, not fresh reproduction results. The launcher never imports them as trained models. Additional paper tables, cross-dataset studies and physical testbed validation are outside this package's execution scope. Two interpretations cannot prove which code produced the published tables; that still requires provenance from the authors.
