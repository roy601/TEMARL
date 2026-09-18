# Can COMISET ground the deception environment? Measured answer: no

Everything here is exploratory and architecture-blind — no trainable model was
involved in any of it, so none of it can favour one encoder over another. It was
all measured **before** `prereg_comiset.py` was written.

Reproduce with:

```bash
python comiset_grounding_check.py --path data_local/comiset_lab_sessions.json
python lab_full_ceiling.py
python real_full_ceiling.py
```

## 1. A bug in our own pipeline, found first

`thesis_system/extract_comiset_sessions.py` mapped techniques through the
25-token **v1** vocabulary (`mitre_techniques.py`) and silently dropped every
record it could not place. A full stream of the raw 149 GB Lab file
(`probe_lab_techniques.py`, 2,743 s) shows what that cost:

| | shipped corpus | raw file |
|---|---|---|
| labelled records | 1,691,011 | **1,713,709** (matches the data paper exactly) |
| distinct techniques | **10** | **53** |
| top technique | T1574 (~30%) | **T1036 Masquerading (45.53%)** |

T1036 (45.5% of all labelled records) and T1059.001 (24.2%) were being discarded
entirely. The 86-token union vocabulary covers 25 of the 53 techniques, and those
25 carry **99.7% of the mass**.

Deprecated ATT&CK ids (T1086, T1073, T1093, …) were a second, much smaller
problem, worth only +0.0001 on the Lab corpus. They are repaired anyway, using
MITRE's own `revoked-by` relationships (`build_deprecation_map.py`, 149 ids).

## 2. Re-extraction

`extract_comiset_lab.py` re-reads the raw file with the union vocabulary plus
label normalisation (it also fixes malformed labels such as
`"T1055; Possible Cobalt Strike post-exploitation jobs."`, `"Port Monitors"` and
a bare `"1210"`).

| | before | after |
|---|---|---|
| sessions | 5,637 | **6,796** |
| techniques | 10 | **19** |
| tactics | 5 | **8** |
| history information I(next;prev) | 0.578 bits | **0.688 bits** |
| sequence value | +0.0682 | **+0.1198** (CAM-LDS: +0.1776) |

## 3. The verdict on grounding

| | headroom | gate (> 0.05) |
|---|---|---|
| CAM-LDS (the v5 environment) | **+0.2698** | pass |
| COMISET Lab, shipped | +0.0423 | fail |
| COMISET Lab, re-extracted | **+0.0391** | **fail** |
| COMISET Lab, theoretical ceiling | +0.1420 | — |
| COMISET Real, whole corpus ceiling | +0.0576 | — |

The re-extracted corpus clusters into profiles whose optimal responses collapse
onto **two** decoy types (persona, environment), where CAM-LDS gives three. A
single fixed decoy therefore captures almost all of the available value, so the
environment would fail the same validity gate the CAM-LDS environment passes.

**The gate threshold of 0.05 was fixed in advance and has not been moved.**
+0.0391 is close to it, and moving the line after seeing that number would be
exactly the p-hacking this project exists to avoid.

## 4. What follows

- COMISET Lab **is** used — for next-technique prediction, which is what
  `prereg_comiset.py` tests. History is clearly worth modelling here
  (0.688 bits, sequence value +0.1198).
- COMISET Lab is **not** used to produce DSR. That remains the CAM-LDS
  environment's job, and the external comparison against Li et al. (2025) stays
  on CAM-LDS.
- COMISET **Real** (the student-lab corpus, no executed attacks) is not used for
  either: 596 usable chains out of 149,496, 88% of records a single technique.
  Its one legitimate use is a false-alarm-rate test on attack-free activity.

## 5. Open item

The gap between the ceiling (+0.1420) and what clustering extracts (+0.0391)
suggests k-means on technique histograms is a poor way to recover campaign
profiles from short sessions (median length 3). A transition-structure
clustering has **not** been tried. If it is tried, it must be done before any
architecture is run against the resulting environment, and disclosed here.
