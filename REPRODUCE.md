# TEMARL v2 — Reproduction Guide

What to run after cloning on a fresh machine.

**Steps 1–5 work immediately after clone.** Only Step 6 needs a dataset you must
obtain separately (COMISET is not redistributed here — see below).

---

## 0. Environment

```bash
git clone <your-repo-url>
cd thesis_project

python -m venv thesis_env
# Windows:
thesis_env\Scripts\activate
# Linux/macOS:
source thesis_env/bin/activate

pip install -r requirements.txt
```

Verified on Python 3.11.9, torch 2.4.1+cpu, numpy 2.4.6, scipy 1.17.1.
The whole pipeline runs on **CPU** — no GPU required.

All commands below are run from `thesis_system/temarl_v2/`:

```bash
cd thesis_system/temarl_v2
```

On Windows, prefix with `PYTHONUTF8=1` (or `set PYTHONUTF8=1`) so the
box-drawing characters in the reports don't hit a cp1252 encoding error.

---

## 1–3. Validate the foundation (no dataset required, seconds)

Each module self-tests when run directly. **Run them in this order** — later
modules import earlier ones, and each prints a pass/fail gate.

```bash
python parse_attackbed.py # (optional) regenerate the source-verified CAM-LDS grounding
python vocab_v2.py        # union vocabulary: 84 techniques, ZERO UNK on both corpora
python d3fend_payoff.py   # D3FEND payoff + PRE-REGISTERED headroom gate (delta >= 0.15)
python env_v2.py          # environment: 4 gates (clock / DSR / SNR / identifiability)
python encoders.py        # Model A/B/C parity, capacity match, PAD-invariance
python policy.py          # GMU trunk, gate sweep, IGM monotonicity (autograd)
```

`parse_attackbed.py` needs the AttackBed repo cloned at the project root
(`git clone https://github.com/ait-testbed/attackbed`). It is optional because
`data/camlds_grounding_verified.json` is committed; re-run it only to re-derive
that file from source.

**Expected gate results** (these are the pre-registered thresholds — if any FAIL,
stop and investigate rather than proceeding):

| Module | Gate | Expected |
|---|---|---|
| `vocab_v2` | ids 0–22 frozen, UNK on both corpora | **0 / 0** |
| `d3fend_payoff` | headroom delta | **0.2698** (>= 0.15) |
| `env_v2` | attacker is not a clock | counter 0.08, bigram 0.27, gain **+0.20** |
| `env_v2` | DSR de-saturated | spread **+0.18** |
| `env_v2` | reward SNR | **~0.88** (>= 0.57) |
| `encoders` | PAD-invariance | **0.00e+00** on all three |
| `policy` | IGM dQtot/dQi | all **>= 0** |

> **Vocabulary changed on 2026-09-01.** Source verification against the published
> AttackBed playbooks found 6 techniques the paper-based reconstruction had missed
> (T1069/T1218/T1518/T1572/T1614/T1615 — 6.20% of CAM-LDS technique instances were
> falling to UNK). They were **appended** at ids 78–83, so `NUM_TECHNIQUES` is now
> **84** and `VOCAB_SIZE` **86**. Ids 0–77 are unchanged, and rows 0–77 of
> `payoff_frozen.json` were verified **bit-identical** before rows 78–83 were
> appended by the identical rule. This is an extension of the frozen matrix, not a
> refit. Checkpoints trained before this date have a 80-wide output layer and must
> be retrained.

---

## 4. Train the simulator arms (~3 min, no dataset required)

```bash
python run_all.py            # 4 arms: Transformer / GRU / SetEncoder / NoTrans
```

Writes `runs/*.pt` and `results_v2/train_all.log`. Took **187 s** on CPU.

---

## 5. Pre-registered evaluation (~5 min, no dataset required)

```bash
python evaluate_v2.py --seeds 10 --episodes 200
```

Writes `results_v2/evaluation_v2.json`. Reproduces the H1–H5 family with
Holm–Bonferroni correction. Expected: **H1/H2/H3 SUPPORTED**, **H4/H5 not
significant** (see the caveat in Step 6 — H4's null is a simulator artefact).

---

## 6. Real-data training — REQUIRES COMISET (not in this repo)

COMISET is a published dataset and is **not redistributed here**. Obtain it from
the original source:

> Pérez-Sánchez, Palacios & López, "COMISET: Dataset for the analysis of
> malicious events in Windows systems", *Data in Brief*, 2025.
> doi:10.1016/j.dib.2025.111723

Place the extracted session file at:

```
thesis_system/data/comiset_sessions.json
```

It must be a JSON object of the form
`{"metadata": {...}, "sessions": {"<guid>": {"raw_techniques": ["T1574.002", ...]}, ...}}`.

Then:

```bash
python data_real.py     # corpus disclosures (self-loop rate, filter, top-3, imbalance)
python train_real.py    # trains all 3 encoders on real COMISET + held-out eval
```

`data_real.py` runs without training and prints the Chapter-4 corrections
(98.5% self-loops, 75.9% upstream drop, true top-3, 50.3% extension share).

---

## 7. TEMARL v3 — variable-topology entity environment

v3 **adds** a variable-topology entity environment alongside v2. It does not
replace it: `env_v2.py` is untouched and remains the scientific control, and v3's
canonical configuration reproduces it exactly (0 mismatches over 1,126 steps).

Following Symes Thompson, Caron, Hicks & Mavroudis (2024), *Entity-based
Reinforcement Learning for Autonomous Cyber Defence*, arXiv:2410.17647.

```bash
cd thesis_system/temarl_v2

python prereg_v3.py       # print the pre-registration (hypotheses fixed in source)
python topology.py        # deterministic topology generator self-test
python env_entity.py      # fixed-environment equivalence vs env_v2 (must be 0)
python entity_encoders.py # EntityTransformer / DeepSets invariances
python policy_entity.py   # fusion, action masking, gradient flow
python tests_entity.py    # full v3 suite (26 tests)
python gates_v3.py        # re-run EVERY v2 + v3 gate, writes results_v3/gates.json
```

Then the experiment (writes `results_v3/`, checkpoints to `runs_v3/`):

```bash
python train_entity.py --save-checkpoints     # 2x3 factorial x 10 seeds
python evaluate_entity.py                     # pre-registered Holm-corrected stats
python analyze_by_size.py --seeds 0 1 2       # per-zone-size breakdown
```

`train_entity.py --quick` runs a 1-seed smoke test in about two minutes.
All entry points take `--seeds`, `--episodes` and `--out`, and resolve paths
relative to the module, so nothing depends on a drive letter or absolute path.

Emit a reproducible topology family for inspection:

```bash
python topology.py --emit results_v3/topologies.json --seeds 0 1 2 3 --zones 7
```

| v3 artefact | Location |
|---|---|
| results | `thesis_system/temarl_v2/results_v3/` |
| checkpoints | `thesis_system/temarl_v2/runs_v3/` |
| pre-registration | `thesis_system/temarl_v2/prereg_v3.py` |

v2 artefacts in `results_v2/` and `runs/` are neither read nor written by v3.
Checkpoints predating the vocabulary expansion (80-wide heads) are **not**
reusable and are never loaded.

---

## What is NOT in the repo, and why

| Excluded | Reason | How to regenerate |
|---|---|---|
| `thesis_env/` | ~4.7 GB virtualenv | Step 0 |
| `data/comiset_sessions.json` | published dataset, do not redistribute | Step 6 link |
| `runs/*.pt` | regenerable checkpoints | Steps 4 / 6 |
| `results/`, `results_02/` | v1 artefacts | not needed for v2 |
| `*.log` | run logs | regenerated on each run |

`data/camlds_grounding.json` **is** included — it is our own reconstruction from
the CAM-LDS paper (Landauer et al., arXiv:2603.04186) and is what makes the
environment reproducible.

---

## Reproducibility notes

* All seeds are locked (`set_seed()` covers `random`, `numpy`, `torch`, CUDA).
* The payoff matrix is **frozen** in `payoff_frozen.json`. It must not be re-tuned:
  fitting it once from D3FEND and freezing is what keeps the benchmark honest.
* The evaluation's primary metric and hypothesis family are **pre-registered in
  the source** of `evaluate_v2.py`. Do not edit them after seeing results.
* Step 6 is currently **single-seed**; the simulator results (Step 5) are 10-seed
  with Holm correction. Bring Step 6 to the same standard before publishing it.
