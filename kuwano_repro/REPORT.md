# Reproduction of Kuwano et al. (2023): ATT&CK behaviour forecasting by attacker-based collaborative filtering

**Prepared by:** Apurba Roy, BRAC University
**Date:** 2 November 2026
**Code and data records:** `kuwano_repro/` in the thesis repository (github.com/roy601/TEMARL)

---

## 1. Summary

We reimplemented the technique-prediction method of Kuwano, Okuma, Okada and Mitsunaga (2023) from the paper alone, because the authors did not release code. We rebuilt their training and test data from the same public sources and checked our implementation against the paper's published confusion matrices (Tables 5–7: 48 rows, three test cases).

**Result**

- **Prediction, TP, FP and FN match the paper in all 48 rows.** Recall is therefore reproduced exactly at every step of all three test cases.
- **TN matches in 44 of 48 rows.** In the other 4 rows our TN is exactly 1 lower than the paper's. This shifts specificity and accuracy by at most 0.0015 and traces to one candidate technique (Section 7.2).
- The method has no randomness. One run is final. The full pipeline was run on two machines from independently downloaded data and produced **byte-identical** results (same SHA-256).

Every point the paper leaves unspecified was settled by evidence (the data, or agreement with the published tables), not by choice. The evidence for each is recorded in Section 8.

---

## 2. The paper and why it was chosen

**Citation.** M. Kuwano, M. Okuma, S. Okada, T. Mitsunaga, "The Attacker Might Also Do Next: ATT&CK Behavior Forecasting by Attacker-based Collaborative Filtering and Graph Databases," *Journal of Information Processing*, vol. 31, pp. 802–811, Dec. 2023. DOI: 10.2197/ipsjjip.31.802.

**Task.** Given the MITRE ATT&CK techniques already observed in an ongoing attack, predict which techniques the attacker will use next. This is the same prediction task as our thesis: observed techniques in, a set of techniques out.

**Why this paper.** We screened 32 published papers for a method we could run ourselves as an external baseline. This was the only one that met all four conditions:

1. **Its only input is the set of observed techniques**, which we can compute from our own data.
2. **Its output is a set of ATT&CK techniques**, the same kind of label we predict.
3. **It is completely specified.** Algorithm 1 is printed in full, with both hyperparameters (k = 60, threshold = 0.17).
4. **It is deterministic** and uses only public data.

It also publishes **exact confusion matrices** (TP, FP, TN, FN at every step) instead of only plots. That is what makes a number-for-number check possible.

**What the authors did not release.** There is no code repository. Everything here was implemented from the paper's text and pseudocode.

**Scope of this reproduction.**

- **Reproduced:** the proposed method (WkNN, k = 60, threshold 0.17) and its evaluation in the paper's Section 6, i.e. Tables 5–7.
- **Not reproduced:** the k = 20/40/60 preliminary experiment (paper Section 4, Fig. 5), the comparison with their 2022 method (Figs. 9–11), and the Neo4j graph visualisation (paper Section 5.3), which does not affect any reported number.

---

## 3. What the method is (the "model")

The method is **not a neural network** and has **no training phase**. It is memory-based, user-based collaborative filtering: the recommender-system idea of "users who bought similar items", applied to attackers.

| Recommender-system term | In this paper |
|---|---|
| User | An ATT&CK threat group (for example APT28) |
| Item | An ATT&CK technique (for example T1059 Command and Scripting Interpreter) |
| Purchase history | The techniques that group is documented to use |
| New user | The ongoing attack ("adversary"), described by the techniques observed so far |

The "model" is therefore just a reference table: a binary **group × technique matrix** built from ATT&CK, plus two fixed hyperparameters (k = 60, threshold = 0.17). Nothing is learned or fitted.

### 3.1 Algorithm 1, step by step

Let O be the set of techniques observed so far, and T_g the set of techniques used by group g.

**Step 1: similarity to every group (Sørensen–Dice coefficient, eq. 1 of the paper).**

```
SDC(O, T_g) = 2 · |O ∩ T_g| / (|O| + |T_g|)
```

**Step 2: nearest neighbours.** Sort the groups by similarity, highest first, and keep the top k = 60.

**Step 3: weighted vote for every technique t.** Each neighbour with non-zero similarity votes with weight 1/d, where d = 1 − similarity (distance-weighted kNN, Dudani 1976). A neighbour with similarity 0 gets weight 0.

```
Score(t)       = sum over the 60 neighbours g with SDC > 0 of  M[g, t] / (1 − SDC(O, T_g))
SupportRate(t) = Score(t) / k
```

M[g, t] is 1 if group g uses technique t, and 0 otherwise.

**Step 4: threshold.** Recommend every technique with SupportRate(t) ≥ 0.17.

### 3.2 Which techniques count as predictions

The paper only evaluates predictions about what comes *later* in the attack (paper Section 4.1): techniques "after the most late-stage tactic observed at that time". ATT&CK tactics have a fixed order (Reconnaissance, Resource Development, Initial Access, Execution, … , Exfiltration, Impact).

At each step:

1. Let L be the latest tactic among the observed techniques.
2. The **candidates** are the techniques not yet observed that belong to **any** tactic at or after L.
3. The **prediction** is the recommended techniques that are also candidates.

This filter is not part of Algorithm 1. It is described only in words, so its exact form had to be determined (Section 8).

### 3.3 Evaluation procedure (Section 6.2 of the paper)

For an advisory listing N techniques in tactic order, and for i = 1, 2, … , N − 1:

- **Observed:** the first i techniques.
- **Positives:** the remaining N − i techniques (what the attacker really did next).
- **Counts:**
  - TP = predicted and really used later
  - FP = predicted, not used
  - FN = used later, not predicted
  - TN = candidate, neither predicted nor used
- **Metrics (paper eqs. 2–4):**
  - Recall = TP / (TP + FN)
  - Specificity = TN / (TN + FP)
  - Accuracy = (TP + TN) / (TP + FP + TN + FN)

---

## 4. Data: sources and integrity

All inputs are public. A download script fetches them and records the size and SHA-256 of each file. A second machine downloaded everything independently and verified identical hashes (7 of 7 files).

### 4.1 Training data: MITRE ATT&CK Enterprise

The paper says ATT&CK v11 (April 25, 2022), 133 groups and 191 techniques. It also cites the ATT&CK website as accessed on 2023-01-31, when v12.1 was live. We therefore obtained three versions from MITRE's official repository, each pinned by its release tag:

| Version | Role | Source | SHA-256 (first 16) |
|---|---|---|---|
| **v11.0** | Primary | github.com/mitre/cti, tag ATT&CK-v11.0, `enterprise-attack/enterprise-attack.json` | e31694f24943a2de |
| v11.3 | Check | same repository, tag ATT&CK-v11.3 | 5308b90f31df0231 |
| v12.1 | Check | same repository, tag ATT&CK-v12.1 | f4d709b097b1b4b8 |

### 4.2 Test data: three CISA advisories

The paper's test cases are three U.S. CISA advisories. To get the pages exactly as the authors would have seen them, we used Internet Archive snapshots taken closest to their access date (2023-01-31). Each advisory's "Last Revised" date is before the snapshot.

| Advisory | Title | Snapshot | Last revised | SHA-256 (first 16) |
|---|---|---|---|---|
| AA22-277A | Impacket and Exfiltration Tool Used to Steal Sensitive Information from Defense Industrial Base Organization | 2023-01-29 | 2022-10-05 | ed48dec24520b09a |
| AA22-138B | Threat Actors Chaining Unpatched VMware Vulnerabilities for Full System Control | 2023-01-29 | 2022-06-02 | 8729be7bad1ce85c |
| AA22-174A | Malicious Cyber Actors Continue to Exploit Log4Shell in VMware Horizon Systems | 2023-02-01 | 2022-07-18 | 44b0165389d9fd91 |

The current cisa.gov pages, PDFs and STIX files were listed as optional cross-checks. cisa.gov blocks scripted downloads, so these were not obtained.

### 4.3 The reproduction target

We typed the paper's Tables 5–7 (48 rows) into a CSV file and checked it by script against the text extracted from the PDF: 0 mismatches. Every row also satisfies two identities that any correct transcription must: Prediction = TP + FP, and TP + FN = N − input.

---

## 5. Audit of the data, before writing any method code

Every source was read in full by an audit script, and the paper's own numbers were used to determine how the authors built their data.

### 5.1 ATT&CK version: v11.0

| | v11.0 | v11.3 | v12.1 | Paper |
|---|---|---|---|---|
| Active parent techniques | **191** | **191** | 193 | 191 |
| Groups (active / deprecated / revoked) | 131 / 1 / 5 | 130 / 2 / 5 | 133 / 9 / 5 | 133 |
| Paper's five cold-start counts reproduced | **5 of 5** | **5 of 5** | 4 of 5 | – |

- **The cold-start counts.** In its Section 6.4 the paper reports how many groups use five techniques it could not predict: T1129 = 0, T1497 = 6, T1039 = 7, T1095 = 7, T1029 = 1. v11.0 reproduces all five. v12.1 gives 5 for T1497, which rules it out.
- **The advisories' own links.** AA22-138B and AA22-174A link only to `attack.mitre.org/versions/v11/`; AA22-277A does so in 20 of its 35 technique links (the other 15 are unversioned).
- **v11.0 versus v11.3.** They give the same technique set for every group; v11.3 only deprecates one group (G0141). We use v11.0.
- **Groups.** The paper's "133 groups" matches no v11 count. This cannot affect any prediction: a group with no techniques has similarity 0 and weight 0.

### 5.2 What counts as "a group uses a technique"

The paper does not say how the matrix was built. ATT&CK distinguishes techniques (T1059) from sub-techniques (T1059.003), and the paper's 191 columns are parent techniques only. We tested the alternatives against the paper's numbers.

**Rule adopted:** a group uses a technique if ATT&CK has a direct "uses" link from the group to that technique *or to any of its sub-techniques*, ignoring revoked and deprecated objects and techniques used only through malware or tools.

- **Cold-start counts:** 5 of 5 reproduced. Without the sub-technique roll-up, T1497 would be 1 instead of 6, because five of its six groups use only its sub-techniques.
- **The paper's Table 1 excerpt** (5 groups × 5 techniques; its first data row is printed in the header row): our matrix matches 4 of the 5 rows exactly, against 0 of 5 without roll-up. The one differing cell (APT1 × T1059) is listed in Section 10.

The resulting matrix has **131 groups × 191 techniques with 2,369 ones**. 128 of the groups use at least one technique.

### 5.3 The test sequences

Each advisory contains a table of ATT&CK techniques by tactic. Following the paper, sub-techniques were counted as their parent technique, each technique was kept once at its first appearance, and techniques before Initial Access were removed.

| Advisory | Techniques after processing | Removed (pre-access) | Paper |
|---|---|---|---|
| AA22-277A | **26** | none | 26 ✓ |
| AA22-138B | **12** | T1588 Obtain Capabilities | 13, of which 12 used ✓ |
| AA22-174A | **13** | none | 13 ✓ |

As an independent check, the paper's worked example (paper Section 5.3) uses the first four inputs of AA22-277A: T1078, T1047, T1059, T1129. These are exactly the first four of our sequence.

**Faults found in the advisory pages, and how they were handled:**

| Advisory | Fault | Handling |
|---|---|---|
| AA22-174A | The two Collection rows have their visible text and link targets swapped (the row reading "T1560.001" links to T1056.001, and the reverse) | Both orders were kept and tested against the paper's table (Section 8) |
| AA22-174A | "Encrypted Channel [1573.001]" is missing its "T"; the link is correct | Technique ids are read from the links, not the visible text |
| AA22-174A | The Credential Access row lists no technique | Confirmed in the raw HTML; nothing to add |
| AA22-138B | One cell contains a second technique, T1070, as a separate link | Included; the paper's count of 13 requires it |
| AA22-138B | The Exfiltration row carries the wrong tactic id (TA0004) and is empty | No effect |
| AA22-277A | Three rows show a parent id but link a sub-technique, or the reverse | No effect: the parent technique is the same |

The final sequences:

- **AA22-277A:** T1078 T1047 T1059 T1129 T1569 T1543 T1036 T1070 T1497 T1562 T1574 T1016 T1033 T1049 T1057 T1082 T1083 T1021 T1560 T1039 T1074 T1095 T1105 T1090 T1029 T1567
- **AA22-138B:** T1059 T1203 T1505 T1068 T1222 T1070 T1003 T1560 T1071 T1573 T1090 T1105
- **AA22-174A:** T1190 T1059 T1053 T1505 T1036 T1021 T1560 T1056 T1071 T1573 T1105 T1571 T1090

### 5.4 Edge cases on the real test data

- **Similarity exactly 1** would make the weight 1/(1 − 1) undefined, and the paper does not say what to do. It **never occurs** on any step of any test case. The implementation stops with an error if it ever did, rather than inventing a weight.
- **Ties at the k = 60 boundary** (groups with equal, non-zero similarity on both sides of the cut) occur at **22 of the 48 steps** of the final sequences. The order used to break ties therefore changes the results and had to be determined (Section 8).

---

## 6. Implementation

- **Language:** Python, standard library only. No machine-learning framework is needed.
- **Exact arithmetic.** All similarities, weights and support rates are exact fractions (Python `fractions.Fraction`), not floating-point numbers. Ties and the 0.17 threshold are decided on exact values. This matters in practice: the closest support rate to the threshold on the test data is only 5.7 × 10⁻⁶ away from 0.17.
- **No hidden choices.** Every point the paper leaves open is an explicit setting of the code, and all of them were tested (Section 8).
- **Tests.** 13 unit tests, all passing on both machines:
  - hand-computed toy cases for similarity, support rate, the threshold, tie-breaking, zero-similarity neighbours and the candidate filter;
  - checks on the real data: the matrix shape, the 173 candidates of Table 5 row 1, determinism, and the identities Prediction = TP + FP and TP + FN = N − input under every combination of settings.

---

## 7. Validation against Tables 5–7

All 156 combinations of the open settings were run against all 48 rows. A row counts as matched only if all five numbers (Prediction, TP, FP, TN, FN) equal the paper's.

| Rows matched (of 48) | Number of settings |
|---|---|
| 44 | 4 |
| 43 | 4 |
| 40 | 4 |
| 39 | 4 |
| 28–37 | 20 |
| 3 or fewer | 120 |

Only a narrow family of settings comes close. The best value of each switch:

| Setting | Best rows matched, by value |
|---|---|
| Tie-break order | **group name: 44**, group id: 40, file order: 36 |
| Candidate filter | **any tactic at or after the latest: 44**; all tactics at or after: 3; strictly after, or no filter: 0 |
| Tactic of an observed multi-tactic technique | **as listed in the advisory: 44**, earliest: 44, latest: 37 |
| AA22-174A Collection order | **visible text (T1560, T1056): 44**, links (T1056, T1560): 43 |
| Threshold comparison | ≥ 0.17: 44, > 0.17: 44 (identical everywhere: no support rate equals 0.17 exactly) |

The four best settings differ only in choices that produce identical numbers on this data ("listed" or "earliest" tactic; ≥ or >). We report "listed" and ≥ as the more literal readings of the paper.

### 7.1 Reproduced tables

Generated directly by the code. The "Paper" column shows the published value only where ours differs.

**Table 5: Confusion matrix (AA22-277A)**

| Input | Prediction | TP | FP | TN | FN | Paper |
|---|---|---|---|---|---|---|
| 1 | 47 | 18 | 29 | 119 | 7 | same |
| 2 | 49 | 18 | 31 | 111 | 6 | TN 112 |
| 3 | 29 | 12 | 17 | 125 | 11 | TN 126 |
| 4 | 29 | 12 | 17 | 125 | 10 | TN 126 |
| 5 | 37 | 15 | 22 | 120 | 6 | TN 121 |
| 6 | 40 | 14 | 26 | 111 | 6 | same |
| 7 | 33 | 13 | 20 | 103 | 6 | same |
| 8 | 37 | 13 | 24 | 99 | 5 | same |
| 9 | 37 | 13 | 24 | 99 | 4 | same |
| 10 | 37 | 12 | 25 | 98 | 4 | same |
| 11 | 35 | 11 | 24 | 99 | 4 | same |
| 12 | 27 | 10 | 17 | 61 | 4 | same |
| 13 | 27 | 9 | 18 | 60 | 4 | same |
| 14 | 27 | 8 | 19 | 59 | 4 | same |
| 15 | 26 | 7 | 19 | 59 | 4 | same |
| 16 | 26 | 6 | 20 | 58 | 4 | same |
| 17 | 26 | 5 | 21 | 57 | 4 | same |
| 18 | 20 | 5 | 15 | 40 | 3 | same |
| 19 | 17 | 4 | 13 | 34 | 3 | same |
| 20 | 18 | 4 | 14 | 33 | 2 | same |
| 21 | 17 | 3 | 14 | 33 | 2 | same |
| 22 | 11 | 3 | 8 | 25 | 1 | same |
| 23 | 11 | 2 | 9 | 24 | 1 | same |
| 24 | 10 | 1 | 9 | 24 | 1 | same |
| 25 | 3 | 1 | 2 | 18 | 0 | same |

**Table 6: Confusion matrix (AA22-138B)**

| Input | Prediction | TP | FP | TN | FN | Paper |
|---|---|---|---|---|---|---|
| 1 | 27 | 7 | 20 | 136 | 4 | same |
| 2 | 24 | 6 | 18 | 138 | 4 | same |
| 3 | 26 | 6 | 20 | 129 | 3 | same |
| 4 | 25 | 6 | 19 | 123 | 2 | same |
| 5 | 26 | 7 | 19 | 117 | 0 | same |
| 6 | 34 | 6 | 28 | 108 | 0 | same |
| 7 | 27 | 5 | 22 | 79 | 0 | same |
| 8 | 12 | 4 | 8 | 42 | 0 | same |
| 9 | 6 | 3 | 3 | 31 | 0 | same |
| 10 | 5 | 2 | 3 | 31 | 0 | same |
| 11 | 5 | 1 | 4 | 30 | 0 | same |

**Table 7: Confusion matrix (AA22-174A)**

| Input | Prediction | TP | FP | TN | FN | Paper |
|---|---|---|---|---|---|---|
| 1 | 21 | 8 | 13 | 148 | 4 | same |
| 2 | 27 | 8 | 19 | 137 | 3 | same |
| 3 | 31 | 7 | 24 | 132 | 3 | same |
| 4 | 32 | 7 | 25 | 123 | 2 | same |
| 5 | 27 | 5 | 22 | 113 | 3 | same |
| 6 | 10 | 5 | 5 | 51 | 2 | same |
| 7 | 11 | 6 | 5 | 43 | 0 | same |
| 8 | 12 | 5 | 7 | 41 | 0 | same |
| 9 | 7 | 4 | 3 | 30 | 0 | same |
| 10 | 6 | 3 | 3 | 30 | 0 | same |
| 11 | 4 | 2 | 2 | 31 | 0 | same |
| 12 | 4 | 1 | 3 | 30 | 0 | same |

**Rows identical on all five numbers: 44 of 48.** In the remaining 4 rows, Prediction, TP, FP and FN are identical and TN differs by 1.

### 7.2 The four differing rows

| AA22-277A input | Recall (paper = ours) | Specificity paper / ours | Accuracy paper / ours |
|---|---|---|---|
| 2 | 0.7500 | 0.7832 / 0.7817 | 0.7784 / 0.7771 |
| 3 | 0.5217 | 0.8811 / 0.8803 | 0.8313 / 0.8303 |
| 4 | 0.5455 | 0.8811 / 0.8803 | 0.8364 / 0.8354 |
| 5 | 0.7143 | 0.8462 / 0.8451 | 0.8293 / 0.8282 |

**Why they differ.** These are exactly the four steps where the latest observed tactic is Execution (inputs T1047, T1059, T1129, T1569 after T1078). Every other row matches, including row 1 and rows 6–25. So at those four steps the paper's candidate set contained **one more technique** than ours, and that technique was neither predicted nor really used.

**Which technique it could be.** It has to belong only to Initial Access in ATT&CK v11.0 (otherwise our filter would already include it) and never be recommended at those steps (otherwise it would show up as an FP). Only three techniques fit: **T1195 Supply Chain Compromise, T1199 Trusted Relationship and T1200 Hardware Additions**. All three give identical counts, so the published numbers cannot tell them apart.

**Checked and ruled out:**

- A version difference: these techniques have the same tactics in v11.0 and v12.1.
- Tactics inherited from sub-techniques: in v11.0, no sub-technique adds a tactic to its parent.

We did not force a match by assigning one of these techniques to Execution. Nothing in the data supports any of them, so that would be fitting the answer rather than reproducing it. We have written to the authors (Prof. T. Mitsunaga) to ask which tactic list they used; there is no reply yet.

---

## 8. Points the paper leaves unspecified, and how each was settled

| # | Question | Decision | Evidence |
|---|---|---|---|
| D1 | Which ATT&CK version | v11.0 | 191 techniques; reproduces all 5 cold-start counts (v12.1 fails one); the advisories' versioned links all point to v11 |
| D2 | When does a group "use" a technique | Direct links, active objects only, no software-mediated use | 5/5 cold-start counts; 4/5 rows of Table 1 |
| D3 | Sub-techniques | Rolled up to the parent technique | Without roll-up: T1497 = 1, not 6; 0/5 Table 1 rows |
| D4 | Technique list and order per advisory | Parents in order of first appearance, pre-access removed; AA22-174A in visible-text order | Counts 26 / 12 / 13 exact; 174A order gives 12/12 rows (link order 11/12) |
| D5 | Candidate filter ("after the most late-stage tactic") | Any tactic at or after the latest observed one, using the advisory's tactic for observed techniques | Best of 5 filters × 3 tactic rules; Prediction/TP/FP/FN 48/48 |
| D6 | Weight when similarity = 1 | Never occurs | Checked on every step |
| D7 | Threshold: > or ≥ 0.17 | ≥ (no effect) | Identical results; no support rate equals 0.17 exactly |
| D8 | Tie-breaking in the top-60 | Group name (case-insensitive), then id | 44 rows, against 40 (id) and 36 (file order); also the order of the paper's Table 1 |
| D9 | Are observed techniques excluded from predictions | Yes | Required for the 173 candidates of Table 5 row 1, and by the 48-row match |

---

## 9. Reproducibility

### 9.1 Determinism

The method contains no random numbers, seeds or shuffling. It uses exact arithmetic, and ties are broken by a fixed rule. **A single run gives the final result**; repeated runs give byte-identical output, and there is no variance to report.

### 9.2 Cross-machine verification

The complete pipeline was run on a second PC (a GPU machine, though no GPU is used) from independently downloaded data. Both machines produced identical files:

| Output | SHA-256 |
|---|---|
| Predictions at every step (`results/PREDICTIONS.csv`) | 7b0edf75d4734a5bd7486113df28bc0f920d23e32d7b1486ae626a64f53ebc75 |
| Validation report (`results/VALIDATION.txt`) | 522cc940e5f10462a5bd0d64705182fda322f27a89c439bc9531c962ba72036a |

### 9.3 Running time (one ordinary PC)

| Step | Time |
|---|---|
| Download all inputs (about 75 MB) | depends on connection; normally under 2 minutes |
| Audit of all inputs | 1.1 s |
| Preprocessing | 0.5 s |
| Unit tests | 20–34 s |
| Predictions for all 48 steps | 0.4 s |
| Validation of all 156 settings | 1.9 s |

### 9.4 How to rerun

```
cd kuwano_repro
python download.py
python download.py --verify --reference reference/REFERENCE_MANIFEST.json
python preprocess.py
python -m unittest discover -s tests -v
python validate.py --detail --out results/VALIDATION.txt
python tables.py
```

---

## 10. Discrepancies inside the paper

These are recorded as found and were not corrected for:

1. **"133 groups".** ATT&CK v11.0 has 131 active groups, 128 of them with at least one technique. This has no effect on predictions, because groups without techniques never contribute.
2. **Table 1, APT1 × T1059.** The paper shows 0. In v11.0, APT1 uses T1059.003, which rolls up to T1059 = 1. The other 24 cells of Table 1 match.
3. **Table 5, TN in rows 2–5.** One higher than ours, explained in Section 7.2. No prediction is affected.

---

## 11. What this establishes, and what comes next

**Established:**

- The method can be run exactly as published, from public data, without the authors' code.
- Everything it predicts reproduces exactly: Prediction, TP, FP and FN in all 48 published rows.
- Every choice the paper left open was settled by evidence, and each is recorded.

**Limits:**

- TN, and therefore specificity and accuracy, differ by one in 4 of 48 rows. This is unresolved until the authors reply.
- The comparison with the authors' 2022 method and the k-sensitivity experiment were not reproduced.

**Next step (not yet done).** Use the validated implementation, unchanged, as an external baseline on our thesis dataset. The comparison will use the same metric for both models, with micro-F1 as the primary metric. Specificity and accuracy will be reported but not relied on, because with few positive labels among many they are dominated by true negatives.

---

## Appendix: files in `kuwano_repro/`

| File | Contents |
|---|---|
| `download.py`, `SOURCES.md` | Every input, its source, and its SHA-256 |
| `reference/REFERENCE_MANIFEST.json` | Hashes used to prove both machines hold identical inputs |
| `audit/audit_inputs.py`, `audit/AUDIT.md` | The audit of this report's Section 5, with its full output |
| `preprocess.py`, `data/derived/` | The group × technique matrix and the three test sequences |
| `kuwano.py` | Algorithm 1 and the evaluation procedure |
| `tests/test_kuwano.py` | The 13 unit tests |
| `validate.py`, `results/VALIDATION.md` | The 156-setting validation |
| `tables.py`, `results/TABLES_5_7.md` | The reproduced Tables 5–7 |
| `predictions.py`, `results/PREDICTIONS.md` | Every predicted technique at every step |
| `DECISIONS.md` | The nine unspecified points and their evidence |
| `paper/tables_5_7.csv` | The paper's Tables 5–7, transcribed and checked against the PDF |
