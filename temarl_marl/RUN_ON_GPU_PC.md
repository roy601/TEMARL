# Running the TEMARL v7 confirmatory study on the GPU PC

Both pre-registered studies run on this machine, **main first, then LOSO**:

| Study | What it measures | Cells | Rough time (12-thread CPU) |
|---|---|---|---|
| `main` | Proposal metrics 1 and 2: dwell time and interaction depth. 6 arms × 10 seeds | 60 | ~6–8 h |
| `loso` | Proposal metric 3: generalisation to an unseen attack script. 4 arms × 7 held-out scripts × 5 seeds | 140 | ~15–18 h |

Both studies are **resumable**. After a crash, a reboot or Ctrl+C, run the same command again and finished cells are skipped. Nothing is lost.

---

## 1. Get the pre-registered code

```bash
git pull
git log --oneline -3      # the top commit must be "TEMARL v7: pre-registration ..."
cd temarl_marl
```

The runner fingerprints the code and refuses to mix cells produced by different code. **Do not edit any `.py` or `.json` file in `temarl_marl/`** at any point.

## 2. Python environment, with the CUDA build of PyTorch

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1                 # PowerShell   (Git Bash: source .venv/Scripts/activate)
python -m pip install --upgrade pip
nvidia-smi                                 # note the CUDA version in the top-right corner
pip install torch --index-url https://download.pytorch.org/whl/cu124   # CUDA 12.x
pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"   # must print True
```

For CUDA 11.8, use `--index-url https://download.pytorch.org/whl/cu118` instead.

## 3. Verify: all three must pass

```bash
python _frozen.py          # every line OK; fingerprint 351bf22ec2b4e86f
python tests_marl.py       # 27 / 27 passed
python prereg_marl.py      # prereg v7-2026-09-19 | budget 2000000 env-steps
```

If any of these fails, **stop and send me the output**. Never edit a hash, a test or the pre-registration to make it pass.

## 4. Choose CPU or CUDA: a 2-minute timing test

The environment itself runs on the CPU, and the networks are small. So the GPU may or may not be faster; measure it:

```bash
python mappo.py --arm Transformer-RoPE --steps 100000 --smoke --device cpu --threads 3
python mappo.py --arm Transformer-RoPE --steps 100000 --smoke --device cuda --threads 3
```

Compare the `NN s` figure in each run's last line, and use the **faster** device for everything below. The device does not change what is measured; each cell records the device it ran on. Keep one device for the whole study.

## 5. Smoke test (about 2 minutes)

```bash
python run_marl.py --study main --smoke --arms GRU NoHistory --seeds 0 --workers 2 --threads 2 --device DEVICE
```

Replace `DEVICE` with `cpu` or `cuda`, as chosen in step 4. The smoke writes only to `results_marl/smoke_main/` and never touches the real results.

## 6. Main study

Set `--workers` to the number of logical CPU threads ÷ 3, rounded down. For 12 threads that is 4; for 16 threads, 5; for 24 threads, 8.

```bash
python run_marl.py --study main --workers 4 --threads 3 --device DEVICE
python evaluate_marl.py --study main > results_marl/main/RESULT.txt
```

## 7. LOSO study (after main has finished)

```bash
python run_marl.py --study loso --workers 4 --threads 3 --device DEVICE
python evaluate_marl.py --study loso > results_marl/loso/RESULT.txt
```

## 8. Send back

Zip these two folders and send them. Results are git-ignored on purpose, so do not commit them.

```
results_marl/main/     (cells/, checkpoints/, baselines_main.json, RESULT.txt)
results_marl/loso/     (cells/, checkpoints/, baselines_loso.json, RESULT.txt)
```

If you want to check progress mid-run, send a partial zip; the analysis works on whatever cells exist.

---

### Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `frozen input CHANGED` | The repository is not at the pre-registered commit. Run `git status`, then `git pull` |
| `finished cells were produced under a DIFFERENT fingerprint` | Code changed after cells were produced. Do not delete anything; send me the list |
| `ENV_STEPS is not set` | The pull did not include the pre-registration commit |
| `torch.cuda.is_available()` prints `False` | The CPU build of torch is installed. Reinstall with the `--index-url` from step 2 |
| CUDA out of memory | Use fewer `--workers` (each worker holds its own small CUDA context) |
| Everything very slow | Too many workers for the cores. Use fewer `--workers` |
