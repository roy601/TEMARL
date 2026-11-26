# CADO — independently reproduced deception results (Tables 2 and 4)

**Result:** The main primary and held-out **scientific** results have been independently rerun using the official original CADO simulator from your uploaded `futureinternet-18-00552-s001.zip`. All 1,440 primary and 360 held-out episode records match the archived author values exactly (excluding host-dependent timing measurements). We also reran 1,710 ablation records, 120 fault tests, the 26-setting sensitivity analysis, and 300 local HTTP integration trials.

**Important limits:** The original publisher archive's `SHA256SUMS.txt` lists one missing file (`README.md`): 56/57 listed files check out, so its own `code/verify_manifest.py` cannot pass unchanged. Also, two primary paired-comparison statistical p-value columns have tiny differences in the newer SciPy environment (max abs difference 5.71803005819257e-7 for adjusted p-values). These are **not** hidden or substituted with reference numbers. The held-out paired results and both target scientific tables match. Network/CPU timings are not expected to match across machines.

## Files to read first

1. **`BUILD_PROCESS_COMPLETE.md`** — exact step-by-step workflow, every individual file, source links, checks, results and missing-item handling.
2. **`tables/REPRODUCED_TABLES.md`** — reproduced Table 2 and held-out table values.
3. **`docs/DEVILS_ADVOCATE_REVIEW.md`** — critical reproducibility limitations and how they were evaluated.
4. **`evidence/independent_scientific_comparison.json`** — per-file and per-column scientific reproducibility comparisons.
5. **`publisher_source/`** and **`original_archive/`** — untouched extracted authors' files and the byte-for-byte uploaded ZIP.

## Verify the included outputs

Install the dependencies from `publisher_source/requirements.txt` in a Python environment, then run:

```bash
python tools/verify_package.py
python tools/export_tables.py
```

On Windows: `powershell -ExecutionPolicy Bypass -File .\RUN_WINDOWS.ps1`.

## Independently rerun the simulator

```bash
python tools/reproduce_again.py --output local_rerun
```

Optional complete ablation: `--full`; optional local prototype: `--prototype`. This copies the original code into a fresh output folder and **never modifies** the included publisher archive. The rerun can be computationally substantial.

## Source and license

Publication: https://doi.org/10.3390/fi18100552  
MDPI page: https://www.mdpi.com/1999-5903/18/10/552  
Official supplement: https://www.mdpi.com/article/10.3390/fi18100552/s1

The supplementary ZIP was provided by the user in this conversation. Its file bytes are preserved. No LICENSE file is present within the supplied archive, so this package makes no representation about rights beyond sharing for this user-requested reproduction; check the publisher's reuse terms for redistribution.
