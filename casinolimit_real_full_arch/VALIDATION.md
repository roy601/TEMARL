# Validation performed

Three automated tests pass: exact replay/exhaustion and fully masked local
telemetry; five split disjointness; past-only history and fully masked history.

CPU smoke runs completed for all 36 combinations: six representations,
IPPO/MAPPO, fog 0/.5/.9. Each used eight environment steps and one fold/seed.
Neural smoke checkpoints used two training updates in isolated output paths.
These demonstrate execution, not convergence or scientific effectiveness.

A mask-gap error discovered during testing was fixed: hidden observations now
retain their time slots with zero technique values. Missing production encoder
checkpoints fail explicitly unless retraining is requested. No full study run.

Not established: long-run numerical stability, GPU execution on the lab machine,
empirical decoy efficacy, asset protection, statistical superiority, or faithful
reproduction of a published CasinoLimit deception experiment (none is supplied).
