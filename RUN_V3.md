# Running TEMARL v3 on another machine

Everything needed is already committed and pushed to
`https://github.com/roy601/TEMARL.git` (branch `main`).

**CPU only — no GPU required.** Verified on Python 3.11.9, torch 2.4.1+cpu,
numpy 2.4.6, scipy 1.17.1.

---

## Step 0 — Clone and set up (~5 min)

```bash
git clone https://github.com/roy601/TEMARL.git
cd TEMARL

python -m venv thesis_env

# Windows (PowerShell):
thesis_env\Scripts\Activate.ps1
# Windows (cmd):
thesis_env\Scripts\activate.bat
# Linux / macOS:
source thesis_env/bin/activate

pip install -r requirements.txt
```

Then move into the code directory — **every command below runs from here**:

```bash
cd thesis_system/temarl_v2
```

### Windows only: set UTF-8 first

The scripts print box-drawing characters. Without this you get a
`UnicodeEncodeError` on Windows when output is redirected to a file.

```powershell
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
```

```cmd
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
```

Linux/macOS: nothing to do.

---

## Step 1 — Validate everything (~30 seconds)

Run these in order. Each prints its own PASS/FAIL gates.

```bash
python prereg_v3.py         # prints the pre-registration (hypotheses fixed in source)
python topology.py          # topology generator self-test
python env_entity.py        # equivalence vs env_v2 — MUST report 0 mismatches
python entity_encoders.py   # EntityTransformer / DeepSets invariances
python policy_entity.py     # fusion, action masking, gradient flow
python tests_entity.py      # full suite — expect 26/26 PASSED
```

Or run all gates at once, including every inherited v2 gate:

```bash
python gates_v3.py          # writes results_v3/gates.json
```

**Expected results — stop and investigate if any differ:**

| Check | Expected |
|---|---|
| `env_entity.py` equivalence | **0 mismatches** over 1,126 steps, `EXACT EQUIVALENCE` |
| `tests_entity.py` | **26/26 PASSED** |
| entity encoder capacity spread | **0.7%** (74,369 vs 73,828 params) |
| padding / permutation invariance | **≤ 1e-06** |
| payoff headroom delta | **0.2698** (≥ 0.15) |
| CAM-LDS UNK | **0 / 1339** |
| frozen payoff rows 0–77 | bit-identical, sum **132.6000** |

---

## Step 2 — Smoke test (~2 min)

Always do this before the long run. It exercises the whole pipeline on 1 seed.

```bash
python train_entity.py --quick
```

Should finish in about two minutes and print a 6-row table
(`EntityTransformer`/`DeepSets` × `Transformer`/`GRU`/`SetEncoder`) with
A/B/C/D columns. The numbers will be poor — 40 training episodes is nothing.
You are only checking that it runs.

---

## Step 3 — The full experiment (~3 hours)

**Measured on this machine: 168–187 s per arm × 60 arms ≈ 3 hours.**

```bash
python train_entity.py --save-checkpoints
```

Writes `results_v3/entity_results.json` and 60 checkpoints to `runs_v3/`.

### Run it so a closed terminal doesn't kill it

**Windows (PowerShell)** — run in a separate window that survives:
```powershell
Start-Process -NoNewWindow python -ArgumentList "-u","train_entity.py","--save-checkpoints" -RedirectStandardOutput "results_v3\train.log" -RedirectStandardError "results_v3\train.err"
```

**Linux / macOS:**
```bash
nohup python -u train_entity.py --save-checkpoints > results_v3/train.log 2>&1 &
```

Watch progress (a line appears per arm):
```bash
tail -f results_v3/train.log        # Linux/macOS
Get-Content results_v3\train.log -Wait   # PowerShell
```

### If 3 hours is too long

Fewer seeds cuts time proportionally. **Use at least 5** — the paired t-tests
need enough pairs to detect anything.

```bash
python train_entity.py --seeds 0 1 2 3 4 --save-checkpoints    # ~1.5 h
```

Reducing `--episodes` below 600 is **not** recommended: 600 is the
pre-registered budget, and learning is still improving at 500
(DSR 0.370 random → 0.420 at 200 episodes → 0.460 at 500).

---

## Step 4 — Statistics (~10 seconds)

```bash
python evaluate_entity.py
```

Reads `results_v3/entity_results.json`, runs **exactly** the contrast family
declared in `prereg_v3.py`, applies Holm–Bonferroni, and writes
`results_v3/entity_analysis.json`.

Prints: DSR per arm per regime with 95% CIs, secondary metrics, parameter
counts, training time, the 7 declared contrasts with corrected p-values and
Cohen's *d*, and a verdict for H6 / H7 / H8.

---

## Step 5 — Per-size breakdown (~20 min, optional)

Needs Step 3 to have been run with `--save-checkpoints`.

```bash
python analyze_by_size.py --seeds 0 1 2
```

Splits regimes B/C/D by zone count (5/6/7 trained, 9/11/13 unseen), so you can
see whether degradation on unseen sizes is gradual or a cliff.

---

## What you do NOT need

| Thing | Why not |
|---|---|
| **COMISET dataset** | The entire v3 chain has zero COMISET dependency. Only the older `data_real.py` / `train_real.py` need it. |
| **AttackBed repo** | `data/camlds_grounding_verified.json` is committed. Only `parse_attackbed.py` needs AttackBed, and it merely regenerates that file. |
| **GPU** | Everything is CPU-only. |

> **Note:** `attackbed/` is recorded in git as a bare gitlink with no
> `.gitmodules`, so after cloning it will be an **empty directory**. That is
> expected and breaks nothing. If you do want to re-run `parse_attackbed.py`,
> clone it yourself into the repo root:
> `git clone https://github.com/ait-testbed/attackbed`

---

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `UnicodeEncodeError` on Windows | `PYTHONUTF8` not set — see Step 0. |
| `ModuleNotFoundError` | You are not in `thesis_system/temarl_v2/`. All scripts import siblings by name. |
| Equivalence reports non-zero mismatches | Do **not** proceed. Something changed in `env_v2.py` or `topology.py`; the control is broken. |
| Training seems stuck, no output | You forgot `-u`. Python buffers when redirected and flushes only at exit. |
| Very slow (>10 min for one arm) | Confirm `train_entity.py` has the `profiles()` cache. Without it the CAM-LDS profiles are rebuilt from JSON every episode. |
| `n_agents N exceeds defended zones` | A topology was requested with `n_zones <= n_agents`. Use `n_zones >= 5` with the default 4 agents. |

---

## One-shot: everything except the long run

```bash
cd thesis_system/temarl_v2
python gates_v3.py && python train_entity.py --quick
```

If that passes, the machine is ready for Step 3.
