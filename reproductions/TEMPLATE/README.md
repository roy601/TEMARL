# Reproduction template

Copy this folder to `reproductions/<paper>/` and fill the files **in this order**:

| file | filled when | content |
|---|---|---|
| `SOURCES.md` | first | paper (DOI, version read), code (URL + commit), data (DOI, checksum), licence |
| `TARGETS.csv` | before any run | every published number we try to match: `id,table_or_figure,quantity,published,tolerance` |
| `DECISIONS.md` | before any run | each gap in the paper, the choice made, and why; never changed to improve a match |
| `run.py` | — | one command; writes only to `out/`; fixed seeds; saves raw outputs and their SHA-256 |
| `REPORT.md` | after the run | for every target: published, ours, difference, MATCH / CLOSE / NO MATCH; all failures listed |

Tolerance is set in `TARGETS.csv` before running (for example: exact for counts, ±1 unit of the
last published digit for rounded values, the paper's own CI for stochastic results). A decision
added after a run is marked as such in `DECISIONS.md` with the date, and its effect reported.
