# Sources

- Paper (authors, venue, year, DOI): Z. Wang, S. Lv, H. Wang, J. You, S. Liu, T. Yuan, X. Lu, L. Sun, "Unveiling Evolving Threats: A Data Analysis for Next-Generation Honeypot Development", 44th IEEE SRDS 2025, pp. 207–217, DOI 10.1109/SRDS69199.2025.00032
- Version read (date, file SHA-256): IEEE Xplore version, downloaded 2026-11-12 through BRAC University, read in full 2026-11-13; `PDF/Unveiling_Evolving_Threats_A_Data_Analysis_for_Next-Generation_Honeypot_Development.pdf`, SHA-256 e58e260c72754ee99722dda98112a85630659b1dd5b3b6b96fd8e08e1163e758
- Code (URL and commit, or "none released"): https://github.com/zyw-286/shell-attack-evolution-dataset, commit d5f7fe120ebd921e04026b6348c3ec5d399c5df6 (MIT licence for code)
- Data (DOI, checksum and licence, or "none released"): the same repository and commit, `dataset/` (CC BY 4.0) and the raw Cowrie logs `2021,2022/cowrie/`, `2024/cowrie/`; `run.py` records the SHA-256 of every input file it reads
- Type (Reproduced / Replicated / Not reproducible; see STANDARD.md Section 1): Reproduced (the authors' own released data and code)
- Stochastic (yes = training seeds needed, no = deterministic): no

## Notes on the materials

- `dataset/attack_ttp/paper_tactics.jsonl` and `paper_techniques.jsonl` are **not data**. The authors'
  `scripts/build_paper_tables.py` says they are "transcribed directly from the published paper ... NOT
  recomputed". They are never used as inputs here. My transcription of Tables VI and VII into
  `TARGETS.csv` was compared with theirs and is identical (2026-11-13).
- The intermediate files the analysis scripts read (`session_dict.json`, `5-session归类.json`,
  `7-session_tech.json`, ...) are **not released**. Route A therefore starts from the released
  `dataset/sessions/` and `dataset/commands/`; route B (stage 2) rebuilds them from the raw logs.
