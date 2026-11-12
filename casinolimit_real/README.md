# casinolimit_real

CasinoLimit (Kilian et al., RAID 2025; Zenodo 17256954, CC BY 4.0) in the same step format as
`camlds_real/out/steps.jsonl`, so the CAM-LDS encoder pipeline can read it.

```
python casinolimit_real/build_steps.py                        # about 2 seconds
python -m unittest discover -s casinolimit_real/tests
```

Input: `dataset_survey/out/casinolimit_steps/steps.csv` (made by `dataset_survey/casinolimit_steps.py`
from the raw auditd logs, md5 checked against Zenodo).

| Output | What it is |
|---|---|
| `out/steps.jsonl` | one row per command, CAM-LDS fields plus `machine`, `first_event`, `doubt`, `labelled_by` |
| `out/vocab.json` | the 66 techniques |
| `out/runs.json` | one entry per attacker (114): length, machines, machine switches |
| `out/CORPUS_REPORT.txt` | measures side by side with CAM-LDS, and the checks |

How each field is defined is written at the top of `build_steps.py`.
No split, no training and no test scores are made here. The split must be fixed and written down
before any model sees this corpus.
