# Data audit

> **Scope.** Source-derived annotated playbook sequences from the AttackBed
> repository, evaluated in a simulator. NOT real-world attacker telemetry. The
> environment's engagement, movement and exposure rules are modelling
> assumptions, not measured quantities.
>
> **Representation.** Command-level and multi-label: one step is one annotated
> attacker command, and the techniques within a command are an unordered set.
> Within-command label order is discarded by construction, so the 34.9%
> label-order artefact of the earlier flattened corpus cannot be learned here.
>
> **Not comparable with the earlier study.** Its Top-1 scored one token out of
> a flattened stream; these targets are label SETS over command transitions.
> Its dwell counted label-steps; here dwell counts commands. Different units.
>
> **Sample size.** 36 playbooks from 7 scenarios. Seeds, environment repeats
> and prediction windows are not independent attack campaigns.


## Corpus

- **source**: AttackBed AttackMate playbooks (github.com/ait-testbed/attackbed, GPL-3.0), parsed directly. CAM-LDS: Landauer et al., arXiv:2603.04186v1.
- **provenance**: SOURCE-DERIVED ANNOTATED PLAYBOOK SEQUENCES, command-level. Each record is one annotated attacker command; the technique list within a command is an UNORDERED annotation set, not an observed execution order. These are scripted playbooks, not real-world attack traces.
- **n_playbooks**: 36
- **n_commands**: 889
- **n_technique_labels**: 1347
- **n_unlabelled_commands**: 945
- **labels_per_command_histogram**: {'1': 678, '2': 156, '3': 26, '4': 10, '5': 1, '13': 18}
- **distinct_parent_techniques**: 82

- **reproduces the earlier flat corpus exactly**: `True` (representation is the only thing that changed)

## Splits

| split | runs | groups | commands | targets | unseen transitions % |
|---|---:|---:|---:|---:|---:|
| train | 22 | 22 | 516 | 494 | 0.00 |
| validation | 7 | 7 | 203 | 196 | 5.61 |
| test | 7 | 7 | 170 | 163 | 6.13 |

Scenarios per split: train {'S1': 10, 'S2': 2, 'S3': 4, 'S4': 1, 'S5': 1, 'S6': 3, 'S7': 1}; validation {'S1': 4, 'S3': 2, 'S6': 1}; test {'S1': 4, 'S3': 2, 'S6': 1}

Notes:

- S2: 2 independent group(s); training only.
- S4: 1 independent group(s); training only.
- S5: 1 independent group(s); training only.
- S7: 1 independent group(s); training only.

## Command structure

| split | mean labels/command | max | multi-label % | self-loop % |
|---|---:|---:|---:|---:|
| train | 1.502 | 13 | 23.4 | 33.2 |
| validation | 1.517 | 13 | 26.6 | 36.7 |
| test | 1.488 | 13 | 20.0 | 34.4 |

## Nearest training run (THE headline caveat)

A held-out run with high overlap is a near-copy of a training run. Its score measures prediction within a known scenario variant, not generalisation to a new campaign.

| split | run | nearest training run | command-bigram Jaccard |
|---|---|---|---:|
| validation | `scenario_1_a_a.j2` | `scenario_1_a_b.j2` | 0.760 |
| validation | `scenario_1_b_b.j2` | `scenario_1_a_b.j2` | 0.760 |
| validation | `scenario_1_d_b.j2` | `scenario_1_d_a.j2` | 0.833 |
| validation | `scenario_1_e_b.j2` | `scenario_1_e_a.j2` | 0.833 |
| validation | `scenario_3_a_c.j2` | `scenario_3_b_c.j2` | 0.643 |
| validation | `scenario_3_b_b.j2` | `scenario_3_b_a.j2` | 0.714 |
| validation | `scenario_6_b_a.j2` | `scenario_6_b_b.j2` | 0.759 |
| test | `scenario_1_b_c.j2` | `scenario_1_a_c.j2` | 0.760 |
| test | `scenario_1_c_c.j2` | `scenario_1_c_a.j2` | 0.826 |
| test | `scenario_1_d_c.j2` | `scenario_1_d_a.j2` | 0.833 |
| test | `scenario_1_f_c.j2` | `scenario_1_a_c.j2` | 0.760 |
| test | `scenario_3_a_d.j2` | `scenario_3_a_a.j2` | 0.636 |
| test | `scenario_3_b_d.j2` | `scenario_3_b_a.j2` | 0.500 |
| test | `scenario_6_a_a.j2` | `scenario_6_a_b.j2` | 0.800 |

## Label support

- labels in vocabulary: 84
- labels present in corpus: 82
- labels in train: 82, in test: 52
- **test labels never seen in training**: 0 []

Macro-F1 averages only labels with support in the evaluated split; the averaged-label count is reported beside every score.

## Window coverage

`full history %` is the share of prediction targets whose entire available history fits inside the window. A window may only be called "full history" at 100%.

| window | split | targets | full history % | mean available | truncated |
|---:|---|---:|---:|---:|---:|
| 8 | train | 494 | 34.4 | 12.8 | 324 |
| 8 | validation | 196 | 28.6 | 14.9 | 140 |
| 8 | test | 163 | 34.4 | 13.0 | 107 |
| 16 | train | 494 | 67.0 | 12.8 | 163 |
| 16 | validation | 196 | 57.1 | 14.9 | 84 |
| 16 | test | 163 | 68.7 | 13.0 | 51 |
| 32 | train | 494 | 99.6 | 12.8 | 2 |
| 32 | validation | 196 | 97.4 | 14.9 | 5 |
| 32 | test | 163 | 98.8 | 13.0 | 2 |
| 64 | train | 494 | 100.0 | 12.8 | 0 |
| 64 | validation | 196 | 100.0 | 14.9 | 0 |
| 64 | test | 163 | 100.0 | 13.0 | 0 |

## Caveats

- Scripted playbook annotations, not real-world attack traces.
- Absent label means absent annotation, not absence of behaviour.
- Default split holds out VARIANTS; see similarity[]. Scenario-level generalisation requires --held-out and is reported separately.
- Seeds and repeated episodes are not independent attack campaigns.

## Environment

- python 3.12.3, torch 2.10.0+cu128, numpy 2.5.3
- Windows-11-10.0.26200-SP0
- CUDA: NVIDIA GeForce RTX 4080 SUPER

