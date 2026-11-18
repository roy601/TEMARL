# NOT a protocol result: exploratory CasinoLimit deception run (GPU PC 2, 2026-11-18)

This folder holds a complete run (1,800 cells: 6 arms x IPPO/MAPPO x fog 0, 0.5, 0.9 x 5 folds x 10 seeds)
of `../../pipeline.py` with `--device cuda --train-missing`, made on GPU PC 2 without a frozen protocol.
Results commit `5980bfde`.

- **Test outcomes are not sealed here.** Each `cells/*/result.json` (`test`, `test_summary`,
  `test_h0_summary`) and `RESULTS.md` contain test numbers. The test instances are the five
  whole-instance splits of CasinoLimit protocol CL 1.0.
- **Do not read, cite or analyse the test numbers.** Nobody had read them when this note was written
  (2026-11-18); the check of this run used code, file structure and validation fields only.
- **Why it is not a result** (checked 2026-11-18, validation only):
  1. No protocol, validity gate, reference baselines (static, random) or statistics.
  2. The environment is saturated. At the best validation checkpoint every arm, NoHistory included,
     reaches a validation E1 of about 35.4 at fog 0, against a ceiling of about 36.0 (efficacy 0.5 x mean
     validation instance length). No history effect can be shown.
  3. The encoders were retrained on PC 2 (CL 1.0 budget: 3,136 updates, patience 16), because the
     CL 1.0 checkpoints are on PC 1. They are not the CL 1.0 checkpoints and were not compared with
     CL 1.0's recorded validation BCE.
  4. `protected` is the engaged fraction of steps, not asset protection. There is one episode per
     instance and seed, and the policies are trained under the fog level they are tested on.
- It is an engineering run: it shows that the pipeline runs on a GPU. Any CasinoLimit deception study
  needs its own frozen protocol first, and that protocol must disclose this run as earlier exposure of
  the test instances.
