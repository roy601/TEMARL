# CADO (Future Internet 2026): reproduction from the authors' Supplementary Material S1

CADO is a rule-based alert-to-deception orchestrator evaluated in a synthetic simulator. The authors
released the simulator and the analysis code (S1), so the paper's tables can be **reproduced** in the ACM
sense: their own code, unchanged, rerun by us and compared with the printed numbers. Decisions 1-14 are in
`DECISIONS.md`; the standard is `../STANDARD.md`.

| file | what it is |
|---|---|
| `SOURCES.md`, `TARGETS.csv`, `DECISIONS.md`, `AUTHOR_CONTACT.md` | as in every reproduction |
| `fetch.py` | unpacks S1 into `external/s1` after checking its SHA-256 and the authors' file manifest |
| `run.py` | `check`, `run`, `report`, `recheck` (standard library only; the authors' code runs in the venv) |
| `tests/` | the comparison, verdict, hashing and lookup rules, and the S1 check (no venv needed) |
| `out/` | `ENVIRONMENT.json`, `fresh/` (fresh simulation), `revision/` (held-out analysis from our episodes), `ARCHIVE_COMPARISON.json`, `SCIENTIFIC_SHA256.json`, `RUN.json`, `logs/`, `results.json`, `HASHES.txt` |

## Run (Windows, CPU only, PowerShell from the repository root; no admin rights)

```powershell
python -m pip install --user uv
python reproductions/cado/fetch.py
python -m uv venv --python 3.13.5 reproductions/cado/external/venv
python -m uv pip install --python reproductions/cado/external/venv/Scripts/python.exe --exclude-newer 2026-10-07 -r reproductions/cado/external/s1/requirements.txt
python -m unittest discover -s reproductions/cado/tests
python reproductions/cado/run.py check
python reproductions/cado/run.py run
python reproductions/cado/run.py report
python reproductions/audit.py
```

`run` refuses until `TARGETS.csv` and `DECISIONS.md` are committed, and never overwrites `out/fresh`.

## Second machine (STANDARD requirement 5)

After `git pull --no-rebase --no-edit` and the first four lines above:

```powershell
python reproductions/cado/run.py recheck
python reproductions/cado/run.py report
```

`recheck` repeats the whole run in `external/` and compares the SHA-256 of every scientific CSV (timing
columns removed) with the first run; it must print `IDENTICAL`. Commit `out/` and `REPORT.md`.
