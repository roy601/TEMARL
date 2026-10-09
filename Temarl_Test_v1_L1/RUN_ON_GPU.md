# Running on the GPU machine (RTX 4080)

The same machine that ran `thesis_version_2310_markov_useful`. This folder is
self-contained: it vendors its own copy of `thesis_system/` and its own corpus,
so nothing outside the folder is needed.

## 1. Copy and verify

Copy the whole `Temarl_Test_v1_L1/` folder across, then:

```bash
cd Temarl_Test_v1_L1
pip install -r requirements.txt
python tests_cmd.py
```

Expect **68 tests, OK**, in about 6 seconds.

The first import verifies the sha256 of every frozen input. If a file was
corrupted in transit the run halts immediately with the offending path — do not
bypass it, re-copy the file.

Check the GPU is visible:

```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Expect `True NVIDIA GeForce RTX 4080 SUPER`.

## 2. Smoke test first

```bash
python run_study.py --stage all --smoke --device cuda --output results/smoke
```

A few minutes. It exercises every stage end-to-end and writes all nine reports.
Smoke output is **excluded from scientific conclusions** — it exists to prove
the pipeline runs on this machine before you commit hours to it.

Delete it afterwards: `rm -rf results/smoke`.

## 3. The real run

```bash
python run_study.py --stage all --device cuda --output results/main
```

### What it does, in order

| Stage | Cells | Notes |
|---|---:|---|
| audit | - | corpus, splits, similarity, window coverage |
| pilots | 57 | 4 arms x 4 windows x 3 seeds, plus 9 overlap pilots |
| budget | - | picks shared patience and update budget from pilots only |
| predict | 200 | 160 main + 10 NoHistory + 30 overlap |
| ladder | - | 1296 fixed joint actions searched on validation |
| rl | 100 | 6 arms + 4 controls, 10 seeds, 2M env-steps each |
| context | 60 | 6 arms at one preselected longer window |
| report | - | nine Markdown files |

### Rough timing

The previous study measured ~187 s per RL cell at 2M steps on this GPU. On that
basis:

- pilots: **2-4 h** (57 cells, 8192-update cap)
- prediction: **3-6 h** (200 cells, budget set by the pilots)
- ladder: **10-30 min** (1296 joint actions x validation episodes, CPU-bound)
- RL: **8-10 h** (160 cells x ~190 s)

**Total: roughly 15-20 hours.** Run it overnight, or stage by stage.

### Stage by stage

Every stage is resumable and a completed cell is never retrained, so you can
stop and restart freely:

```bash
python run_study.py --stage pilots  --device cuda --output results/main
python run_study.py --stage predict --device cuda --output results/main
python run_study.py --stage ladder  --device cuda --output results/main
python run_study.py --stage rl      --device cuda --output results/main
python run_study.py --stage context --device cuda --output results/main
python run_study.py --stage report                --output results/main
```

If a run is interrupted, delete the stale lock before restarting:

```bash
rm results/main/.running
```

Only do that once you have confirmed the recorded process is actually gone —
two processes writing one output directory will corrupt it.

## 4. The additional runs

Each question gets its OWN output directory. Never mix them.

```bash
# Sensitivity: mean instead of max set-aggregation. A separately TRAINED
# condition, not a re-scoring of the main run.
python run_study.py --stage all --device cuda \
    --aggregation mean --output results/sensitivity_mean

# Scenario-level generalisation (much harder than the default variant split).
# Only S1, S3 and S6 have enough independent groups to be held out.
python run_study.py --stage all --device cuda --held-out S1 --output results/loso_S1
python run_study.py --stage all --device cuda --held-out S3 --output results/loso_S3
python run_study.py --stage all --device cuda --held-out S6 --output results/loso_S6
```

Three LOSO folds are three separate reports. They are **not** a pooled
seven-fold cross-validation and must not be described as one.

## 5. What to copy back

```
results/main/*.md               the nine reports
results/main/audit.json         corpus and split audit
results/main/budget.json        patience and budget selection
results/main/ladder.json        reference ladder
results/main/*/*/result.json    every cell
```

`encoder.pt` and `actor.pt` are large. Keep them **on the GPU machine** — the
previous study's checkpoints went missing, which made it impossible to
re-score anything without retraining. Do not delete them, and note where they
live.

## Troubleshooting

**`RuntimeError: Frozen input verification FAILED`** — a vendored file changed.
Re-copy it. Never edit the hashes to make the error go away; that is the exact
confound the check exists to catch.

**`FileNotFoundError: Missing encoder checkpoint`** — the RL stage ran before
the prediction stage. Run `--stage predict` first. The guard is deliberate: RL
must not silently train on a freshly initialised encoder.

**CUDA out of memory** — lower `n_envs` in `mappo_cmd.HP` (64 by default).
Changing it changes the experiment, so record the change in the report.

**Slow on CPU** — `--threads N` sets the torch thread count (default 4).
