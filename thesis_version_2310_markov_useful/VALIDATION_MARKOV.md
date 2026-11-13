# Build verification (2026-10-08)

No full scientific experiment was started. All measured training outputs in
this delivered folder are explicitly labeled software smoke checks.

| Check | Result |
|---|---|
| New Markov/split/training tests | 13/13 passed |
| Existing architecture/bundle tests | 13/13 passed |
| Existing environment checks | 27/27 passed |
| Frozen dependencies and payoff hashes | Passed |
| Python syntax | All 19 root Python files parsed |
| PowerShell launcher syntax | Passed |
| Final end-to-end CPU smoke | 9/9 prediction cells and 20/20 policy cells completed |
| Shared epoch requirement | Every smoke encoder completed 2 epochs; primary checkpoint at epoch 2 |
| Validation-best checkpoint | Saved separately and reported as secondary |
| Generated Markdown | All five reports present and nonempty |
| Completed-cell resume | Verified; completed cells were skipped |
| Full lab experiment | Not run |
| CUDA execution on lab hardware | Not tested on this CPU-only machine |

Verification runtime: Python 3.13, PyTorch 2.10.0+cpu, NumPy 2.4.2,
SciPy 1.18.1. Lab setup uses Python 3.12 and PyTorch 2.10.0+cu128.

## Verified data split

22 original training runs (796 steps), seven validation runs (272 steps),
seven test runs (279 steps). Original total remains 36 runs and 1,347 steps.
No encoded duplicate group crosses a split. S2/S4/S5/S7 are training-only due
to insufficient distinct groups for a three-way split. Remaining similarities
between variants and label-support gaps are visible in the audit report.

## Reviewable reports

- [Data audit and full pending-table preview](results_markov/audit_preview/RESULTS.md)
- [Final execution smoke report](results_markov/final_validation_smoke/RESULTS.md)
- [Smoke epoch tables](results_markov/final_validation_smoke/EPOCH_RESULTS.md)
- [Smoke human-readable predictions](results_markov/final_validation_smoke/PREDICTION_EXAMPLES.md)

Earlier development artifacts under `results_markov/smoke` and
`results_markov/validation_smoke` are superseded; an automatic policy blocked
their optional cleanup. Their manifests use older code fingerprints and they
must not be resumed or used as scientific evidence. The lab script uses its
own `smoke_cuda` output and a fresh `main` output.

`SOURCE_COPY_AUDIT.json` records hashes of 38 copied source files. Only the
copied README, requirements, mappo and run_experiment files intentionally differ
from their source counterparts; new modules are additional. The source folder
was never a target of an edit operation.
