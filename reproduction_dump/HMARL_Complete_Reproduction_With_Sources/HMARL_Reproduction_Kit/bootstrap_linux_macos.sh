#!/usr/bin/env bash
# Gets unmodified upstream author code and CAGE 4, pins them, installs dependencies.
# Must be run from the root of the extracted HMARL_Reproduction_Kit.
set -Eeuo pipefail
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3.10}"
HMARL_COMMIT=6fe960f5931f2d7dc5ef522f09ca4a179f377ee4
CAGE_COMMIT=8c3c50ca54b176c2de199847944e8dcc035497e3
mkdir -p sources logs results
log_file="logs/bootstrap.log"
exec > >(tee -a "$log_file") 2>&1
printf 'Source acquisition started at %s\n' "$(date -u +%FT%TZ)"
command -v git
"$PYTHON_BIN" --version
fetch_repo() {
  local url="$1" path="$2" ref="$3"
  if [ ! -d "$path/.git" ]; then
    git clone --depth 1 --branch main "$url" "$path"
  fi
  git -C "$path" fetch --depth 1 origin "$ref" || git -C "$path" fetch --unshallow origin
  git -C "$path" -c advice.detachedHead=false checkout --detach "$ref"
  test "$(git -C "$path" rev-parse HEAD)" = "$ref"
}
fetch_repo https://github.com/adityavs14/Hierarchical-MARL.git sources/Hierarchical-MARL "$HMARL_COMMIT"
fetch_repo https://github.com/cage-challenge/cage-challenge-4.git sources/cage-challenge-4 "$CAGE_COMMIT"
"$PYTHON_BIN" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r sources/cage-challenge-4/Requirements.txt
python -m pip install -e sources/cage-challenge-4
# The H-MARL authors explicitly require Ray 2.10.
python -m pip install 'ray[rllib]==2.10.0'
python -m pip freeze > results/pip_freeze_after_install.txt
python scripts/patch_metrics.py --repo sources/Hierarchical-MARL --out results/metrics_patch.json
python scripts/preflight.py --repo sources/Hierarchical-MARL --cage sources/cage-challenge-4 --out results/preflight.json
printf 'Setup succeeded. Run: .venv/bin/python scripts/run_evaluation.py --max-eps 100 --seed 42\n'
