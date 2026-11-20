# Wang et al. 2020, RL deployment of deception resources (IEEE Access 8:35792): replication

Everything for this paper is in this folder. No code or data was released, so the method is rebuilt from the
paper. Status: **targets, consistency findings and gaps written; no simulator yet, nothing run.**

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

Re-measure and re-check (repository root, the PDF in `PDF/`):

```powershell
python reproductions/wang2020/checks/extract_figures.py
python reproductions/wang2020/checks/consistency.py
```
