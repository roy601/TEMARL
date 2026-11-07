# Validation before lab execution

Checked on the preparation PC:

- Three Python unit tests pass: both source-patch paths and fail-closed anchors; all eight-method MAT parsing and report tables using clearly synthetic test fixtures; rejection of missing completed-stage artifacts.
- `--prepare-only` generates both tracks and all 20 full experiment cells without executing MATLAB.
- PowerShell launch script parses without syntax errors.
- The released processed MAT configuration loads and declares 12 defender features, 4 defender actions, 45 attacker actions and a 100-step cap.
- Historical archived results are inspected separately in `ARCHIVE_AUDIT.md` and not treated as new results.

Not executed locally: MATLAB syntax/runtime checks, simulator training, model evaluation and end-to-end numerical reproduction. MATLAB is not installed on this PC. The lab launcher runs a mandatory two-track smoke test before any full training; errors stop execution and retain logs. Passing Python checks does not establish that MATLAB execution or scientific reproduction will succeed.

No new scientific results are supplied with this folder. The first lab run freezes hashes and creates fresh output directories. The source's remaining assumptions/limitations are in `PROTOCOL.md`.
