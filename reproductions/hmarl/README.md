# H-MARL (Singh et al., RLJ 2025): reproduction of Tables 2 and 3

The authors released trained policies for three methods (H-MARL Expert, H-MARL Meta, MARL Decentralized) and
an evaluator for the Default Red agent, so those cells of Tables 2 and 3 can be **reproduced** in the ACM sense:
their policies and evaluation code, unchanged, in the CAGE 4 environment. Everything else is NOT ATTEMPTED, with
the reason (DECISIONS 3). Decisions 1-13: `DECISIONS.md`; the standard: `../STANDARD.md`.

| file | what it is |
|---|---|
| `SOURCES.md`, `TARGETS.csv`, `DECISIONS.md`, `AUTHOR_CONTACT.md` | as in every reproduction |
| `fetch.py`, `POLICY_SHA256.txt` | clones H-MARL (6fe960f) and CAGE 4 (8c3c50c); checks the 87 policy and code files |
| `requirements_hmarl.txt` | the environment's requirements (same as `../cage4/`), Ray 2.10.0 |
| `run.py`, `report_hmarl.py` | `check`, `verify`, `run`, `seed`, `recheck`, `report` |
| `tests/` | parsing of the authors' output, statistics, verdict rule, target ids, pins |
| `out/` | `ENVIRONMENT.json`, `VERIFY.json`, `seeds/`, `logs/` (the authors' printed output), `results.json`, `HASHES.txt` |

## Run (Windows, CPU only, PowerShell from the repository root; no admin rights)

```powershell
python -m pip install --user uv
python reproductions/hmarl/fetch.py
python -m uv venv --python 3.10 reproductions/hmarl/external/venv
python -m uv pip install --python reproductions/hmarl/external/venv/Scripts/python.exe --exclude-newer 2024-06-15 -r reproductions/hmarl/requirements_hmarl.txt
$py = "reproductions/hmarl/external/venv/Scripts/python.exe"
python -m unittest discover -s reproductions/hmarl/tests
& $py -W ignore reproductions/hmarl/run.py check
& $py -W ignore reproductions/hmarl/run.py verify
python reproductions/hmarl/run.py run --workers 4
python reproductions/hmarl/run.py report
python reproductions/audit.py
```

Python 3.10 is required: the released policy files contain pickled code objects that do not load under 3.11.
`run` refuses until `TARGETS.csv` and `DECISIONS.md` are committed, keeps every finished seed, and can be
started again after a stop.

## Second machine

After `git pull --no-rebase --no-edit` and the set-up lines above:

```powershell
& $py -W ignore reproductions/hmarl/run.py recheck --method HMARL_Expert --seed 0
& $py -W ignore reproductions/hmarl/run.py recheck --method HMARL_Meta --seed 0
& $py -W ignore reproductions/hmarl/run.py recheck --method MARL_Decentralized --seed 0
python reproductions/hmarl/run.py report
```
