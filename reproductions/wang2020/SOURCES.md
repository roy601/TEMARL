# Sources

- Paper (authors, venue, year, DOI): S. Wang, Q. Pei, J. Wang, G. Tang, Y. Zhang, X. Liu, "An Intelligent Deployment Policy for Deception Resources Based on Reinforcement Learning", IEEE Access 8:35792-35804 (2020), DOI 10.1109/ACCESS.2020.2974786 (licence CC BY 4.0, as stated in the article)
- Version read (date, file SHA-256): published version (current version dated 2020-02-28), read 2026-11-20; PDF/Wang et al. 2020,.pdf, SHA-256 4e62488b763d328e89dd677d4cf20491d13ba6de685e996c4f1f9f34b1eb34ff
- Code (URL and commit, or "none released"): none released (the article has no code link or availability statement)
- Data (DOI, checksum and licence, or "none released"): none released; the method is a simulation on the network of Table 1, Table 2 and Fig. 8 (Nessus scan output not released). Fig. 8 transcribed in `data/ntpg.json`
- Type (Reproduced / Replicated / Not reproducible; see STANDARD.md Section 1): Replicated (rebuilt from the paper); a calibrated replication (STANDARD.md Section 3a) if unpublished settings must be calibrated
- Stochastic (yes = training seeds needed, no = deterministic): yes
- Published numbers: every target is a figure value, read from the article's vector drawings by `checks/extract_figures.py` (exact polyline vertices, axes calibrated from tick marks; largest residual 0.0015 dsp) into `data/figure_values.json`; Fig. 8's edge labels are glyph outlines and were read by eye at 5x zoom
