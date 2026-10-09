# Temarl_Test_v1_L1

Command-level, multi-label deception study. A rebuild of the attacker-sequence
representation, with the Markov generator removed.

> **Scope.** Source-derived annotated playbook sequences from the AttackBed
> repository, evaluated in a simulator. NOT real-world attacker telemetry. The
> environment's engagement, movement and exposure rules are modelling
> assumptions, not measured quantities.

## What changed, and why

### 1. One command is one step

The previous corpus flattened a command's technique labels into consecutive
steps. A command annotated

```
techniques: "T1087,T1083,T1201,T1069,T1057,T1518,T1082,T1614,T1016,T1049,T1033,T1007,T1615"
```

(one `linpeas` invocation, present once per S1 run, 18 times in the corpus)
became 13 "steps" and 12 transitions in an order nobody executed. Measured on
that corpus, **458 of 1,311 transitions (34.9%) were within-command label-order
artefacts**, and they inflated the order-1 vs order-0 perplexity advantage from
~10x (real command-to-command transitions) to 19x.

Here a command is one step carrying an **unordered set** of techniques. Order
inside a command is discarded by construction, so the artefact cannot be
learned or scored. `tests_cmd.py` asserts order invariance numerically.

### 2. No Markov anywhere

No chain estimation, no smoothing, no synthetic sequences, no generated
episodes. Attackers are **replayed recordings only**. An exhausted replay pool
raises rather than resampling. A test greps the source for the banned
machinery and fails if any reappears.

The previous study tested Markov augmentation across 24 contrasts and found
no benefit at any dose; it is kept there as a completed ablation, not repeated.

### 3. The order-free control is back

`OrderFree` sees **which** commands occurred but not in what order. Without it,
beating `NoHistory` only shows that history helps:

| Comparison | What it licenses |
|---|---|
| any encoder > NoHistory | history content matters |
| sequence arms > OrderFree | **order** additionally matters |
| sequence arms = OrderFree | "history matters, order does not detectably" |

The previous study dropped this arm, which is why its claim could only be
stated as "history matters".

### 4. Window length and patience are tested, not inherited

Windows 8/16/32/64 (W=64 verified as genuine full history: 100% of test targets
fit). Patience 16/32/64 validation checks, evaluated retrospectively from pilot
curves so one trajectory scores every rule without leaking the future.

## Layout

| File | Role |
|---|---|
| `parse_commands.py` | Build step: AttackBed `.j2` -> `camlds_commands.json`. Asserts it reproduces the old flat corpus exactly |
| `_frozen.py` | sha256 verification of every frozen input; refuses to run on a mismatch |
| `command_data.py` | Corpus, splits, multi-hot windows, audit |
| `encoders_cmd.py` | Set embedding + Transformer / Cho GRU / Gers LSTM / OrderFree / NoHistory, capacity-matched |
| `metrics_cmd.py` | BCE, micro/macro-F1, exact-set accuracy, ranking metrics, threshold selection |
| `train_cmd.py` | Ordinary and overlap samplers, training loop, retrospective patience |
| `env_cmd.py` | Command-level replay deception environment |
| `baselines_cmd.py` | Reference ladder: null -> static -> random -> best-fixed -> reactive -> clairvoyant |
| `mappo_cmd.py` | MAPPO / IPPO with a frozen history encoder |
| `stats_cmd.py` | Paired t, Holm, TOST |
| `study_spec.py` | **Pre-registration.** Arms, metrics, families, decision rules |
| `run_study.py` | Runner (resumable) |
| `report_study.py` | Markdown reports |
| `tests_cmd.py` | 68 tests |

## Running

```bash
python tests_cmd.py                                  # 68 tests, ~6 s
python run_study.py --stage all --smoke               # end-to-end, minutes
python run_study.py --stage all --device cuda         # the real run
```

Stages run in order and are individually resumable:
`audit -> pilots -> predict -> ladder -> rl -> context -> report`.
A completed cell is never retrained.

Separate output directories for separate questions:

```bash
python run_study.py --stage all --device cuda --output results/main
python run_study.py --stage all --device cuda --aggregation mean --output results/sensitivity_mean
python run_study.py --stage all --device cuda --held-out S1 --output results/loso_S1
```

### Rebuilding the corpus

Only needed if the AttackBed checkout changes; the committed JSON is what the
study loads.

```bash
git clone https://github.com/ait-testbed/attackbed
python parse_commands.py --attackbed ./attackbed --check
```

`_frozen.py` pins its sha256, so a changed corpus halts every run until a human
records the new hash deliberately.

## Corpus facts

- 36 playbooks, 7 scenarios, **889 annotated commands**, 1,347 technique labels
- 1,347 sub-technique labels collapse to **1,336** distinct (command, parent)
  pairs: 11 commands annotate two sub-techniques of one parent
- 945 unlabelled commands are excluded and counted; **absence of a label is
  absence of annotation, not evidence that no technique occurred**
- labels per command: 678x1, 156x2, 26x3, 10x4, 1x5, **18x13**
- splits: 22 train / 7 validation / 7 test runs (494 / 196 / 163 targets)
- S2, S4, S5, S7 have too few independent groups and stay training-only, so the
  test split covers S1, S3 and S6 only

## Reading the results honestly

- **Not comparable with the previous study.** Its Top-1 scored one token from a
  flattened stream; these targets are label sets over command transitions. Its
  dwell counted label-steps; here dwell counts commands. Different units.
- **The default split holds out variants, not scenarios.** Test runs overlap
  their nearest training run at Jaccard 0.50-0.83. Read default-split scores as
  "prediction within known scenario variants". Scenario-level generalisation
  needs `--held-out` and is reported separately.
- **Non-significance is not equivalence.** The reports say "no clear difference
  detected" unless a TOST with a predeclared margin was run.
- **The real sample size is 36 playbooks from 7 scenarios.** Seeds, environment
  repeats and windows are not independent attack campaigns.

## Provenance

- Attack data: [AttackBed](https://github.com/ait-testbed/attackbed), AIT
  Austrian Institute of Technology, **GPL-3.0**
- Dataset paper: CAM-LDS, Landauer et al., arXiv:2603.04186v1
- Zone metadata (entry / target / goal tactic) comes from a reconstruction of
  the CAM-LDS paper, because the playbooks encode no network zones. This is the
  one place the study depends on the hand-reconstructed file, and it is
  recorded in `DATA_AUDIT.md` rather than hidden.
