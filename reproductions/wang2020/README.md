# Wang et al. 2020, RL deployment of deception resources (IEEE Access 8:35792): replication

Everything for this paper is in this folder. No code or data was released, so the method is rebuilt from the
paper. Status: **simulator, calibration grid (144 readings) and held-out protocol committed 2026-11-28 before any run (DECISIONS D15-D22, Section 4).**

| file | what it is |
|---|---|
| `SOURCES.md` | paper, version read (PDF SHA-256), licence (CC BY 4.0) |
| `TARGETS.csv` | 36 published numbers (all from Figs. 10-14; 2 primary), committed before anything else |
| `DECISIONS.md` | what the paper gives, findings F1-F8 from its own numbers, gaps D1-D14, calibration plan |
| `AUTHOR_CONTACT.md` | questions for the corresponding author (draft, not sent) |
| `data/figure_values.json` | every plotted point of Figs. 10-14, read exactly from the PDF's vector drawings |
| `data/ntpg.json` | Fig. 8's attack graph (20 edges with <UP, RP>) |
| `data/consistency.json` | output of `checks/consistency.py` (findings F1-F6) |
| `checks/extract_figures.py` | measures the figures (needs the PDF; checks its SHA-256) |
| `checks/consistency.py` | the internal-consistency checks |
| `wang_env.py` | the rebuilt simulation: network, attacker readings, alarms, the four policies, Q-learning |
| `run.py` | `calibrate` (once), `heldout` (once, after the calibration is committed), `report` |
| `tests/` | the rules taken from the paper and DECISIONS |

Re-measure and re-check (repository root, the PDF in `PDF/`):

```powershell
python reproductions/wang2020/checks/extract_figures.py
python reproductions/wang2020/checks/consistency.py
```

Run (repository root; pure Python, CPU):

```powershell
python -m unittest discover -s reproductions/wang2020/tests
python reproductions/wang2020/run.py calibrate --workers 10
# commit out/CALIBRATION.json and out/calibration_log.csv, then:
python reproductions/wang2020/run.py heldout --workers 10
python reproductions/wang2020/run.py report
```
