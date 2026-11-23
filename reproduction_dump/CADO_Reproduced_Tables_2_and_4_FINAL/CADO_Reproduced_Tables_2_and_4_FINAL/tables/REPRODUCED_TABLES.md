# Independently reproduced CADO results

Source: the user-uploaded CADO official supplementary archive; original simulation and revision-analysis scripts executed here.

## Main manuscript Table 2 — primary evaluation

| Metric | Static | Adaptive | Consensus | CADO |
|---|---:|---:|---:|---:|
| Defensive utility | 0.6853 | 0.6213 | 0.6953 | 0.7020 |
| Redirection precision | 0.6847 | 0.5908 | 0.6978 | 0.7282 |
| Engagement rate | 0.9416 | 0.9993 | 0.9999 | 0.9999 |
| Benign false redirects | 0.0029 | 0.1060 | 0.0001 | 0.0001 |
| Unsafe actions | 0.0019 | 0.0650 | 0.0000 | 0.0000 |
| Normalized cost | 0.0579 | 0.0962 | 0.0757 | 0.0754 |

Values are means across 30 paired seeds. Exact bootstrap CI endpoints appear in the CSV.

## Held-out attacker table (Table 4 in manuscript discussion)

| Metric | Consensus | CADO | CADO minus Consensus | Holm adjusted p |
|---|---:|---:|---:|---:|
| Defensive utility | 0.6572 | 0.6590 | 0.001792 | 0.000505 |
| Redirection precision | 0.5549 | 0.5745 | 0.019640 | 0.001571 |
| Engagement rate | 1.0000 | 1.0000 | 0.000000 | 1.000000 |
| Benign false redirects | 0.0003 | 0.0003 | 0.000000 | 1.000000 |
| Unsafe actions | 0.0002 | 0.0002 | 0.000000 | 1.000000 |
| Normalized cost | 0.0711 | 0.0729 | 0.001800 | 0.000182 |

Comparison uses the same 30 paired seeds and the author-provided 10,000-resample convention.

**Scope:** generated synthetic events, not real network traffic. Model is deterministic/constraint-aware, not a trained neural or MARL policy.

**Limitations:** host-dependent timing excluded; the separate primary `paired_statistical_comparisons.csv` differs in two p-value rows under this environment (see evidence/independent_scientific_comparison.json). The held-out paired table above matches its archived counterpart.
