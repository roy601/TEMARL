# Kuwano et al. (2023): reproduction

Reimplementation of the attacker-based collaborative filter (weighted kNN with Sørensen–Dice
similarity, k = 60, support-rate threshold 0.17) from Kuwano, Okuma, Okada & Mitsunaga,
*J. Information Processing* 31, 802–811 (2023), doi:10.2197/ipsjjip.31.802.

**The claim this folder must support:** "Our implementation of Algorithm 1 reproduces the
paper's Tables 5–7 (TP/FP/TN/FN at every input count, three CISA advisories)." No code was
released, so this is a reimplementation, validated against the published confusion matrices.
Using the validated method as a baseline on our own data is a later, separate step.

## Phases and gates

Each phase ends at a gate. Do not start the next phase until the gate is met.

| Phase | Work | Gate |
|---|---|---|
| 0. Acquire | `download.py` fetches the inputs and hashes them | `--verify --reference` passes: same bytes as the dev machine |
| 1. Audit | Read every source in full: STIX objects, relations, CISA tables. Report counts and anomalies | Every row of `DECISIONS.md` has its evidence |
| 2. Preprocess | Scripts turn raw → `data/derived/` (group × technique matrix, ordered test lists). Raw is never edited | Derived counts match the paper: 133 groups, 191 techniques, 26 / 12 / 13 test techniques |
| 3. Implement | Algorithm 1, plus the evaluation loop of §6.2 | Unit tests on hand-computed cases |
| 4. Validate | Run all three advisories against `paper/tables_5_7.csv` | All 48 rows match exactly, or every difference is explained in `DECISIONS.md` |

## Rules

- `data/raw/` is read-only. Everything in `data/derived/` is produced by a script in this folder.
- Every unspecified choice is recorded in `DECISIONS.md` with the evidence that settled it.
- Nothing is tuned against the target tables beyond the open decisions listed there.

## Running it on the GPU PC

There is no GPU work here. The whole method is a 133 × 191 binary matrix and finishes in
seconds on a CPU. Python 3.10 or newer, standard library only for Phase 0.

```
git pull
cd kuwano_repro
python download.py                                                    # ~75 MB
python download.py --verify --reference reference/REFERENCE_MANIFEST.json
```

`--verify` must report **7/15 verified, 0 missing or changed**. The 8 "manual pending"
files are the cisa.gov cross-checks: cisa.gov blocks scripts, so save each one from a
browser to the path `download.py` prints, then rerun `python download.py`. See `SOURCES.md`.

## Layout

```
download.py                     Phase 0: fetch + hash every input
SOURCES.md                      every link, version and why it is the right copy
DECISIONS.md                    the paper's unspecified points, and how each is settled
paper/tables_5_7.csv            the reproduction target (Tables 5-7, 48 rows, checked against the PDF)
reference/REFERENCE_MANIFEST.json   SHA-256 of every auto source as fetched on the dev machine
data/raw/                       downloaded inputs (not in git)
data/derived/                   preprocessing outputs (Phase 2)
```
