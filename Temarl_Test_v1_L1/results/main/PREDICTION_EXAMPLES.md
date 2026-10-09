# Prediction examples

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


Per-run test scores at the validation-selected threshold. Runs are listed in full, not cherry-picked.

## GRU W8 ordinary seed 0 (threshold 0.4)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9286 | 0.8462 | 0.9231 | 0.00777 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00420 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00636 |
| `scenario_1_f_c.j2` | 26 | 0.9286 | 0.8846 | 0.9615 | 0.00616 |
| `scenario_3_a_d.j2` | 18 | 0.6190 | 0.6667 | 0.7778 | 0.05445 |
| `scenario_3_b_d.j2` | 16 | 0.6286 | 0.6875 | 0.6875 | 0.03642 |
| `scenario_6_a_a.j2` | 16 | 0.7333 | 0.6875 | 0.7500 | 0.03195 |

## GRU W8 ordinary seed 1 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9268 | 0.8462 | 0.9615 | 0.00751 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00402 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00575 |
| `scenario_1_f_c.j2` | 26 | 0.9286 | 0.8846 | 1.0000 | 0.00617 |
| `scenario_3_a_d.j2` | 18 | 0.7083 | 0.7222 | 0.8889 | 0.04551 |
| `scenario_3_b_d.j2` | 16 | 0.6667 | 0.6875 | 0.7500 | 0.03626 |
| `scenario_6_a_a.j2` | 16 | 0.6429 | 0.5625 | 0.6250 | 0.03333 |

## GRU W8 ordinary seed 2 (threshold 0.4)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9268 | 0.8462 | 0.9615 | 0.00742 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00447 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00640 |
| `scenario_1_f_c.j2` | 26 | 0.9398 | 0.8846 | 1.0000 | 0.00631 |
| `scenario_3_a_d.j2` | 18 | 0.6000 | 0.6667 | 0.7778 | 0.04012 |
| `scenario_3_b_d.j2` | 16 | 0.6286 | 0.6875 | 0.6875 | 0.03427 |
| `scenario_6_a_a.j2` | 16 | 0.6000 | 0.5625 | 0.7500 | 0.02672 |

## GRU W8 ordinary seed 3 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9268 | 0.8462 | 0.9615 | 0.00772 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00433 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00556 |
| `scenario_1_f_c.j2` | 26 | 0.9630 | 0.8846 | 1.0000 | 0.00579 |
| `scenario_3_a_d.j2` | 18 | 0.6222 | 0.7222 | 0.7778 | 0.05705 |
| `scenario_3_b_d.j2` | 16 | 0.6316 | 0.5625 | 0.7500 | 0.04233 |
| `scenario_6_a_a.j2` | 16 | 0.5385 | 0.4375 | 0.5625 | 0.03822 |

## GRU W8 ordinary seed 4 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9398 | 0.8846 | 0.9615 | 0.00761 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00409 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00640 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00582 |
| `scenario_3_a_d.j2` | 18 | 0.6047 | 0.7222 | 0.7222 | 0.05484 |
| `scenario_3_b_d.j2` | 16 | 0.6471 | 0.6875 | 0.6875 | 0.03798 |
| `scenario_6_a_a.j2` | 16 | 0.6429 | 0.5625 | 0.6875 | 0.03425 |

## GRU W8 ordinary seed 5 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9398 | 0.8846 | 0.9615 | 0.00750 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00431 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00600 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00560 |
| `scenario_3_a_d.j2` | 18 | 0.6500 | 0.6667 | 0.7778 | 0.05217 |
| `scenario_3_b_d.j2` | 16 | 0.6667 | 0.6250 | 0.7500 | 0.03829 |
| `scenario_6_a_a.j2` | 16 | 0.6429 | 0.5625 | 0.7500 | 0.03201 |

## GRU W8 ordinary seed 6 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9268 | 0.8462 | 0.9615 | 0.00806 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00435 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00602 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00634 |
| `scenario_3_a_d.j2` | 18 | 0.6087 | 0.6667 | 0.7778 | 0.06147 |
| `scenario_3_b_d.j2` | 16 | 0.6857 | 0.6875 | 0.6875 | 0.03963 |
| `scenario_6_a_a.j2` | 16 | 0.5926 | 0.5000 | 0.6250 | 0.03295 |

## GRU W8 ordinary seed 7 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9398 | 0.8846 | 0.9615 | 0.00801 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00416 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00560 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00583 |
| `scenario_3_a_d.j2` | 18 | 0.6512 | 0.7222 | 0.7778 | 0.05318 |
| `scenario_3_b_d.j2` | 16 | 0.6857 | 0.6875 | 0.8125 | 0.03919 |
| `scenario_6_a_a.j2` | 16 | 0.6429 | 0.5625 | 0.6875 | 0.03365 |

## GRU W8 ordinary seed 8 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9398 | 0.8846 | 0.9615 | 0.00732 |
| `scenario_1_c_c.j2` | 27 | 0.9756 | 0.9259 | 0.9630 | 0.00437 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00647 |
| `scenario_1_f_c.j2` | 26 | 0.9630 | 0.8846 | 1.0000 | 0.00589 |
| `scenario_3_a_d.j2` | 18 | 0.7000 | 0.7222 | 0.8333 | 0.04685 |
| `scenario_3_b_d.j2` | 16 | 0.6667 | 0.6875 | 0.7500 | 0.03532 |
| `scenario_6_a_a.j2` | 16 | 0.5926 | 0.5000 | 0.6875 | 0.03214 |

## GRU W8 ordinary seed 9 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9286 | 0.8462 | 0.9615 | 0.00701 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00389 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9412 | 0.00564 |
| `scenario_1_f_c.j2` | 26 | 0.9630 | 0.8846 | 0.9615 | 0.00641 |
| `scenario_3_a_d.j2` | 18 | 0.5909 | 0.7222 | 0.7778 | 0.04695 |
| `scenario_3_b_d.j2` | 16 | 0.6471 | 0.6875 | 0.7500 | 0.03326 |
| `scenario_6_a_a.j2` | 16 | 0.6897 | 0.6250 | 0.6250 | 0.03206 |

## GRU W16 ordinary seed 0 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9398 | 0.8846 | 0.9615 | 0.00733 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 0.9630 | 0.00396 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9706 | 0.00541 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00613 |
| `scenario_3_a_d.j2` | 18 | 0.6522 | 0.6111 | 0.7778 | 0.04379 |
| `scenario_3_b_d.j2` | 16 | 0.7059 | 0.6875 | 0.8750 | 0.02990 |
| `scenario_6_a_a.j2` | 16 | 0.6897 | 0.6250 | 0.8125 | 0.03255 |

## GRU W16 overlap seed 0 (threshold 0.5)

| test run | windows | micro-F1 | exact-set | p@1 | BCE |
|---|---:|---:|---:|---:|---:|
| `scenario_1_b_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00658 |
| `scenario_1_c_c.j2` | 27 | 0.9639 | 0.9259 | 1.0000 | 0.00346 |
| `scenario_1_d_c.j2` | 34 | 0.9485 | 0.9118 | 0.9706 | 0.00545 |
| `scenario_1_f_c.j2` | 26 | 0.9512 | 0.8846 | 0.9615 | 0.00581 |
| `scenario_3_a_d.j2` | 18 | 0.6250 | 0.6111 | 0.7778 | 0.04838 |
| `scenario_3_b_d.j2` | 16 | 0.7059 | 0.6875 | 0.7500 | 0.03169 |
| `scenario_6_a_a.j2` | 16 | 0.6429 | 0.5625 | 0.6875 | 0.03441 |

