# Lin et al. 2026 (IEEE TMLCN): RL-driven ICS honeypot

**Status: not reproducible as published** (2026-11-26). No code, attack scripts, Conpot patch, mapper prompt or
logs are released, and the paper does not say how its scripted attacks react to each deception action, which
decides every result (DECISIONS 1). The 115 targets are pre-registered so that a run with the authors'
materials is bound to them. Table 6 cannot come from Algorithm 1 as printed (DECISIONS C1-C3).

| file | what it is |
|---|---|
| `SOURCES.md`, `TARGETS.csv`, `DECISIONS.md`, `AUTHOR_CONTACT.md` | as in every reproduction |
| `make_targets.py` | writes `TARGETS.csv` from the numbers typed from the PDF (text + Table 6) |
| `checks/check_paper.py`, `checks/CHECKS.txt` | internal-consistency checks C1-C8 (arithmetic and Algorithm 1 as printed; no reproduction run) |
| `tests/` | the targets file and the checks |

```powershell
python reproductions/lin2026_tmlcn/make_targets.py
python reproductions/lin2026_tmlcn/checks/check_paper.py
python -m unittest discover -s reproductions/lin2026_tmlcn/tests
```

Use in the thesis: Algorithm 1 is fully specified as a learner, so it can be an adapted baseline in our own
environment under a separate comparison protocol (DECISIONS 5), not as a reproduction.
