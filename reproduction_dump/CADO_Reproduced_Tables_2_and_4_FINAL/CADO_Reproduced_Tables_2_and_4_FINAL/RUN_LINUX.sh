#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 tools/verify_package.py
printf '\nRun new simulation: python3 tools/reproduce_again.py --output ./local_rerun\n'
printf 'Add --full for ablations and --prototype for isolated HTTP tests.\n'
