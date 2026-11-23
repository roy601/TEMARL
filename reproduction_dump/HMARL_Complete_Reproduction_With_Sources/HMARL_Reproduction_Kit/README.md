# H-MARL reproduction package — original sources INCLUDED

**Status:** Original sources and 65 pretrained model checkpoint files received, ZIP integrity and both official Git tree hashes verified. **The 100-episode research experiment has NOT completed in this environment** because Python 3.10, Ray 2.10.0, Gym and online Python dependency installation are unavailable. Do **not** call this a successful experimental reproduction.

Read **[REPRODUCTION_REPORT.md](REPRODUCTION_REPORT.md)** for the full evidence, exact URLs/revisions, detailed instructions, per-file descriptions, logs and reduction calculations.

## Contents

- `sources/Hierarchical-MARL/` — FULL original authors' code and pretrained checkpoints (all variants).
- `sources/cage-challenge-4/` — FULL original CAGE 4 CybORG source.
- `scripts/` — source integrity verification, metric patching, optional instrumentation, preflight, original evaluator run and comparison.
- `results/` and `logs/` — *observed* audit/execution attempts, not simulated model results.
- `FILE_INVENTORY.csv` — individual file paths, sizes and SHA256; `source_manifest.json` — original-source integrity.

## Windows PowerShell (requires Python 3.10 and working PyPI)

```powershell
cd C:\path\to\HMARL_Reproduction_Kit
py -3.10 scripts\verify_source_manifest.py
powershell -ExecutionPolicy Bypass -File .\setup_from_uploaded_windows.ps1
.\.venv\Scripts\python.exe scripts\run_evaluation.py --max-eps 100 --seed 42
.\.venv\Scripts\python.exe scripts\compare_results.py
```

## Linux / WSL2 (requires Python 3.10 and working PyPI)

```bash
cd /path/to/HMARL_Reproduction_Kit
python3.10 scripts/verify_source_manifest.py
PYTHON_BIN=python3.10 bash setup_from_uploaded_linux.sh
source .venv/bin/activate
python scripts/run_evaluation.py --max-eps 100 --seed 42
python scripts/compare_results.py
```

The source-based installers do not download original GitHub repos, as both are already included. They **do** need to download Python dependencies. The original source has been kept **unmodified** so source manifest verification passes before the installation scripts apply metric patches.

**Published Table 3 reduction:** Expert's red impact is 22.81% lower than Meta's by arithmetic from published averages. **Experimentally reproduced reduction: NOT YET.**

Paper: https://rlj.org/papers/singh2025hierarchical  
PDF: https://rlj.cs.umass.edu/2025/papers/RLJ_RLC_2025_77.pdf  
H-MARL: https://github.com/adityavs14/Hierarchical-MARL  
CAGE 4: https://github.com/cage-challenge/cage-challenge-4
