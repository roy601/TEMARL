#!/usr/bin/env bash
set -euo pipefail
python -m unittest discover -s tests -v
python -m baahs.cli run --steps 20 --seeds-per-batch 3 --holdout-seeds 3 --output results/smoke
