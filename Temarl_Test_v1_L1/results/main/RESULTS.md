# Temarl_Test_v1_L1 -- results

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


## Completion

- prediction cells: **200**
- deception cells (reference window): **100**
- deception cells (context window): **60**
- smoke run: **False**

- environment: `{'beta': 0.2, 'p_goal': 0.7, 'p_stay': 0.8, 'k_capacity': 2, 'goal_steps': 1, 'aggregation': 'max'}`

## Declared hypotheses

Frozen in `study_spec.py` before any confirmatory run.

- **H1_history**: Encoder arms beat NoHistory on dwell. (Replication: the previous study found ~+33% under flattened labels.)
- **H2_order**: Sequence encoders differ from the OrderFree control, which sees WHICH commands occurred but not their order. If null, the finding is 'history matters, order does not detectably' -- a legitimate outcome, and the question the previous study could not answer because this control was dropped.
- **H3_architecture**: No prediction given. Previous studies found no clear difference; two-sided and direction-aware.
- **H4_window**: No prediction given. Longer windows may or may not help; a prediction gain need not transfer to deception.
- **H5_learner**: No prediction given for MAPPO vs IPPO.
- **H6_patience**: No prediction given; the patience study selects a shared budget, it does not test a hypothesis.
- **H7_overlap**: No prediction given. Overlap repeats windows within the same update budget; it adds optimisation, not information.

_Null and negative results are valid outcomes and are reported in full, whatever their direction._

## Reports

- [Data audit](DATA_AUDIT.md)
- [Patience and budget](PATIENCE_RESULTS.md)
- [Prediction](PREDICTION_RESULTS.md)
- [Window sensitivity](WINDOW_RESULTS.md)
- [Deception](RL_RESULTS.md)
- [Statistics](STATISTICS.md)
- [Training curves](TRAINING_CURVES.md)
- [Prediction examples](PREDICTION_EXAMPLES.md)

