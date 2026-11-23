# CAGE Challenge 4 (Kiely et al., AI Magazine 2025): reproduction of Teams cybermonic and punch

Team cybermonic released its code and trained weights, and Team punch its heuristic (decision 15), so their
Table 3 numbers can be **reproduced** in the ACM sense: the authors' own agents, in the unchanged environment,
under the official evaluation. Teams UC and lancer released nothing (NOT ATTEMPTED), and the five scenario
variations are not provided by the environment (NOT ATTEMPTED). Decisions 1-15 are in `DECISIONS.md`.

| file | what it is |
|---|---|
| `SOURCES.md`, `TARGETS.csv`, `DECISIONS.md`, `AUTHOR_CONTACT.md` | as in every reproduction (`../STANDARD.md`) |
| `fetch.py` | clones the environment and both submissions at their pinned commits into `external/` and checks the released files' SHA-256 |
| `requirements_cage4.txt` | the environment's requirements with the declared changes (DECISIONS 8) |
| `run.py` | `check`, `verify`, `run` (2 teams x 10 seeds x 100 episodes), `report` |
| `tests/` | the loop, the statistics, the verdict rule and the pins (no CybORG needed) |
| `out/` | `ENVIRONMENT.json`, `VERIFY.json`, `episodes_<team>_seed<k>.json`, `results.json` |

## Run (any Windows PC; CPU only; about 1-2 h with 10 cores)

PowerShell, from the repository root. `uv` installs Python 3.11 for the user, no admin rights needed.

```powershell
python -m pip install --user uv
python reproductions/cage4/fetch.py
python -m uv venv --python 3.11 reproductions/cage4/external/venv
python -m uv pip install --python reproductions/cage4/external/venv/Scripts/python.exe --exclude-newer 2024-06-15 -r reproductions/cage4/requirements_cage4.txt
$py = "reproductions/cage4/external/venv/Scripts/python.exe"
python -m unittest discover -s reproductions/cage4/tests
& $py -W ignore reproductions/cage4/run.py check
& $py -W ignore reproductions/cage4/run.py verify
& $py -W ignore reproductions/cage4/run.py run --workers 10
python reproductions/cage4/run.py report
python reproductions/audit.py
```

`run` keeps every finished seed and can be started again after a stop; `report` refuses until all ten
seeds exist.
