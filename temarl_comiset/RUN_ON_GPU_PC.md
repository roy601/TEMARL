# Running the COMISET Lab encoder comparison on the GPU machine

Everything needed is in this folder. **The raw 149 GB COMISET file is NOT
required** — the corpus was already extracted here and ships as a 604 KB
gzipped file (`data_local/comiset_lab_sessions.json.gz`, 6,796 sessions,
27,315 windows, 19 techniques). The runner expands it on first use.

Expected total runtime on a modern GPU: **about 1–2 hours** for the full
4 arms × 10 seeds × 3000 steps.

---

## 1. Clone

```bash
git clone <your-repo-url> thesis_project
cd thesis_project/temarl_comiset
```

## 2. Create an environment

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Git Bash / Linux:
source .venv/Scripts/activate
python -m pip install --upgrade pip
```

## 3. Install PyTorch for YOUR GPU (do this before requirements.txt)

Check the driver first:

```bash
nvidia-smi
```

Then pick the matching wheel — **CUDA 12.x** is the usual case:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

For CUDA 11.8: use `--index-url https://download.pytorch.org/whl/cu118`.
For an AMD card on Linux: `--index-url https://download.pytorch.org/whl/rocm6.1`.
For an Intel Arc card: `pip install torch --index-url https://download.pytorch.org/whl/xpu`.

Then the rest:

```bash
pip install -r requirements.txt
```

## 4. Verify the GPU is visible

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"
```

If this prints `False`, the run will still work but on CPU and will take many
hours. Fix the wheel before continuing.

## 5. Smoke test (about 1 minute — always do this first)

```bash
python run_comiset_encoders.py --smoke
```

**Check these three lines before going on.** They identify the corpus, and a run
against the wrong corpus is worthless:

```
sessions    : 6796 | windows: 27315
corpus id   : {'sha256_16': '35c89d20c5be4a8d', 'sessions_kept': 6796, 'n_windows': 27315}
  Transformer-RoPE   seed 0  top1 0.5352 ...  maj 0.3363  bigram 0.5388
```

`sessions` must be **6796**, not 5637. 5637 is the old pre-repair corpus, which
was missing 43 of the raw file's 53 techniques. If the machine already held an
older `data_local/comiset_lab_sessions.json`, the runner now detects it, prints
`!! on-disk corpus does not match the shipped .gz`, and replaces it — let it.

If this fails, stop and send me the traceback — do not run step 6.

### If you have run this before on this machine

Delete previous results first. Cells produced from a different corpus cannot be
mixed with new ones, and the runner will refuse to continue rather than silently
combine them:

```bash
del results_comiset\encoders_comiset.json      # PowerShell / cmd
rm -f results_comiset/encoders_comiset.json    # Git Bash
```

## 6. The real run

```bash
python run_comiset_encoders.py
```

It prints one line per (arm, seed) and saves after every cell to
`results_comiset/encoders_comiset.json`. **It is resumable**: if the machine
sleeps or you press Ctrl+C, just run the same command again and it skips the
cells already done.

To force the device: `--device cuda` (or `cpu`, `xpu`).

## 7. Analysis

```bash
python evaluate_comiset.py > results_comiset/RESULT.txt
type results_comiset\RESULT.txt      # Windows;  cat on Git Bash
```

## 8. Send back

Commit and push, or just send me these two files:

```
results_comiset/encoders_comiset.json
results_comiset/RESULT.txt
```

---

## What this experiment is

A pre-registered comparison of four history encoders on **next-technique
prediction** over real attacker behaviour: Transformer-RoPE, GRU, LSTM, and a
SetEncoder (order-free control).

The hypotheses, metrics, splits, seeds and statistical tests are fixed in
[`prereg_comiset.py`](prereg_comiset.py), which is committed **before** the run.
Do not edit that file. If something about the design needs to change, that is a
new pre-registration in a new commit, and the change must be disclosed.

**This is not a DSR experiment.** COMISET's campaign profiles give headroom
+0.0391, below the 0.05 validity gate, so it cannot support a decoy-type
decision problem. DSR remains the CAM-LDS environment's job. The measurement
behind that statement is reproducible with `python comiset_grounding_check.py
--path data_local/comiset_lab_sessions.json`.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: torch` | Step 3 was skipped or the venv is not active |
| `cuda.is_available() == False` | CPU wheel installed; reinstall with the `--index-url` for your CUDA version |
| `FileNotFoundError: comiset_lab_sessions.json` | Run from inside `temarl_comiset/`; the runner expands the `.gz` itself |
| Out of memory | `--device cpu`, or lower `BATCH` in `prereg_comiset.py` — but changing it invalidates the pre-registration, so tell me first |
| Run interrupted | Re-run the same command; completed cells are skipped |
