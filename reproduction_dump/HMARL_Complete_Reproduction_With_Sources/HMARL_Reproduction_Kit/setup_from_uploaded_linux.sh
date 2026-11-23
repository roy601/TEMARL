#!/usr/bin/env bash
# Uses bundled source trees; only Python dependencies require online download.
set -euo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3.10}"
test -f sources/Hierarchical-MARL/README.md
test -f sources/cage-challenge-4/CybORG/__init__.py
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install numpy==1.26.4
python -m pip install 'ray[rllib]==2.10.0'
python -m pip install -r sources/cage-challenge-4/Requirements.txt
python -m pip install -e sources/cage-challenge-4
python -m pip freeze > results/pip_freeze_after_install.txt
python scripts/patch_metrics.py --repo sources/Hierarchical-MARL
python scripts/instrument_metrics.py --repo sources/Hierarchical-MARL
python -m unittest discover -s tests -v
python scripts/preflight.py --repo sources/Hierarchical-MARL --cage sources/cage-challenge-4 --out results/preflight.json
echo 'Ready: python scripts/run_evaluation.py --max-eps 100 --seed 42'
echo 'Then: python scripts/compare_results.py'
