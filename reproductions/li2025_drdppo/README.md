# Li, Zhao & Wu 2025, DRD-PPO (Sci. Rep. 15:16830): calibrated replication

Everything for this paper is in this folder. No code or dataset was released, so the method is rebuilt from the
paper, and the settings the paper does not publish are **calibrated** under a pre-registered protocol.

| file | what it is |
|---|---|
| `SOURCES.md` | paper, version read (PDF SHA-256), licence (CC BY-NC-ND 4.0), data sources |
| `TARGETS.csv` | the 11 published numbers (Tables 3 and 4), committed before anything else |
| `DECISIONS.md` | every gap and our choice (decisions 1-16), findings F1-F2, calibration protocol C1-C9, amendments A1-A10 |
| `AUTHOR_CONTACT.md` | questions for the corresponding author (no reply to earlier requests) |
| `data/nvd/` | NVD records of the 7 CVEs of Table 1 (the paper's only external data), with SHA-256 |
| `drdppo.py` | simulator (network, attacker of Eq. 2, constraints Eqs. 10-14, reward Eqs. 5-6), baselines, DRD-PPO |
| `calibrate.py` | stage 1, stage 2, held-out run; enforces the protocol's order and logs every trial |
| `report.py` | writes `REPORT.md` from `out/` |
| `EXTRA_TRIALS.csv` | your own guesses (see below) |
| `tests/` | 18 tests |
| `out/` | results: `calibration_log.csv` (every trial), `stage1.json`, `stage2.json`, `heldout.json` |

## The protocol in one paragraph

Stage 1 tunes the **environment** (w, host-server links, attack timing: 24 settings) on the two baselines that
do not learn (Table 3 Alg1 28.43, Alg3 55.19). Stage 2 tunes the **learner** (R1, R2, clip: 12 settings) on
Table 3 DRD-PPO 97.09. Then, **once**, the held-out targets are computed: Table 3 Alg2 98.31 and Table 4
DRD-PPO 98.61. Tuned numbers are reported as CALIBRATION TARGET (never as matches). A held-out target is
UNINFORMATIVE if a trivial scripted policy or an untrained PPO also lands within 2 points of it. Every trial is
appended to `out/calibration_log.csv`.

## Run on GPU PC 2 (about 10 minutes; CPU only, the networks are tiny)

PowerShell, from the repository root:

```powershell
cd C:\Users\CMR\TEMARL
git pull --no-rebase --no-edit
python -m unittest discover -s reproductions/li2025_drdppo/tests          # expect: Ran 18 tests ... OK
python reproductions/li2025_drdppo/calibrate.py smoke                      # code check, keeps nothing

python reproductions/li2025_drdppo/calibrate.py stage1
git add reproductions/li2025_drdppo/out
git commit -m "Li 2025: stage 1 (environment calibration)"
git pull --no-rebase --no-edit; git push

python reproductions/li2025_drdppo/calibrate.py stage2
git add reproductions/li2025_drdppo/out
git commit -m "Li 2025: stage 2 (learner calibration)"
git pull --no-rebase --no-edit; git push
```

Then **stop and send the stage-1 and stage-2 lines to Claude** before the held-out run. The held-out run
happens once, and nothing can be calibrated after it:

```powershell
python reproductions/li2025_drdppo/calibrate.py heldout
python reproductions/audit.py
git add reproductions/li2025_drdppo
git commit -m "Li 2025: held-out targets (computed once) and REPORT.md"
git pull --no-rebase --no-edit; git push
```

`heldout` refuses unless `out/stage1.json`, `out/stage2.json` and `out/calibration_log.csv` are committed and
unchanged, and it refuses to run a second time.

## Your own guesses (trial and error, protocol C6 / A10)

1. Add a row to `EXTRA_TRIALS.csv`. Stage-1 rows may set `w`, `links` (P1/P2/P3), `timing` (last/random),
   `cvss` (v2/v3) and `h_links` (f_only/f_plus_server); stage-2 rows may set only `R1`, `R2` and `clip`.
2. **Commit and push it before running** (`calibrate.py` refuses uncommitted guesses).
3. Run `calibrate.py stage1` (or `stage2`) again. Trials already in the log are reused, never re-run; your new
   rows are added and the selection is made again over the grid plus every committed guess. If stage 1's choice
   changes, run stage 2 again too.
4. Not allowed after `heldout` has run.

Every guess stays in the log and in the report's trial count, including the ones that did not fit.
