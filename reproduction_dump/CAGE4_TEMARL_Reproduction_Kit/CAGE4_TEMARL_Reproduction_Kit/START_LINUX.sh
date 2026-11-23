#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3.11 -m venv .venv
. .venv/bin/activate
python bootstrap.py --install
python preflight.py
python run_baselines.py --agents all --episodes 2 --seed 12501
python make_comparison.py
printf '2-episode smoke runs complete. Full runs: python run_baselines.py --agents all --episodes 100 --seed 12502\n'
