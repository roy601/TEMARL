# NOT protocol D1.0 results: a pre-protocol partial run (2026-11-15)

This folder holds a partial run (1,171 of 3,200 cells) of the earlier `pipeline.py --stage main`,
made on GPU PC 1 before protocol D1.0 existed, with the old environment: random-walk movement,
hand-typed goals, execution order, engagement reward. Commit `b6487fee`.

- **Test outcomes are not sealed here.** Each `result.json` (`test`, `test_summary`,
  `test_h0_summary`) and `RESULTS.md` contain test-run numbers, and the `prediction.json` files
  recompute the CAM-LDS encoder prediction test (same checkpoints and validation-selected thresholds
  as protocol 1.2).
- Nobody looked at these test numbers before the D1.0 freeze (user, 2026-11-17); the analyst read
  only the section headings of `RESULTS.md`.
- **Do not read, cite or analyse them.** They are not D1.0 results, and D1.0 needs nothing from them.
- Disclosed in `../../PROTOCOL_D1.0.md`, Section 2a. D1.0 results are written to `../../results_d1/`.
