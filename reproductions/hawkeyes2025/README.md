# Hawkeyes (Do Hoang et al., Computer Networks 2026): replication

No code is released; the simulation is rebuilt from the paper (DECISIONS 3-25): one primary reading, five
declared alternative readings (R1-R5) reported as sensitivity only.

| file | what it is |
|---|---|
| `SOURCES.md`, `TARGETS.csv`, `DECISIONS.md`, `AUTHOR_CONTACT.md` | as in every reproduction |
| `hawk_env.py` | network (Fig. 8, Table 2), attacker strategies, NMS, high-level gate |
| `run.py` | A2C agents (Table 1), training, evaluation, all 940 jobs (`smoke`, `list`, `run --workers 10`) |
| `tests/` | network, gate, and the analytic prediction of decision 24 |
| `out/runs/` | one JSON per job |

```powershell
python -m unittest discover -s reproductions/hawkeyes2025/tests
python reproductions/hawkeyes2025/run.py run --workers 10
```
