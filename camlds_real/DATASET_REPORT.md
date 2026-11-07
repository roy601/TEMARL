# CAM-LDS dataset report

**Status: labels fully audited; raw logs awaiting the GPU PC scan. No data file has been changed.**
Evidence: `out/LINE_AUDIT.txt` (`audit_lines.py`), `out/CORPUS_MEASURES.txt` (`measure_corpus.py`).

## 1. What has been read

| Data | Size | Read so far |
|---|---|---|
| `attack_times.csv`, the only file the pipeline uses | 904 rows | **Every row and field** |
| `out/steps.jsonl`, our extracted corpus | 904 steps | **Every row, against the source** |
| File list of all 37 archives | 549,625 entries | **Every entry** |
| Raw logs, on the GPU PC | 49.45 GB | **Not line by line.** Sampled only. `scan_all_lines.py` will read every byte |
| `attackmate.json` (34 scenario files) | about 1,800 records | **Not yet.** Exported by the scan |
| `facts.json` (183 files) | one per host per run | **Not yet.** Summarised by the scan |

## 2. Findings

**Clean (all 904 rows pass):**

- No malformed rows, duplicate rows, empty fields, stray spaces or non-ASCII bytes.
- All 97 technique IDs are valid and live in the latest ATT&CK (v20.1).
- Every tactic belongs to a technique in its row, and every technique has a tactic in its row.
- `steps.jsonl` matches the source exactly. Nothing was lost or changed in extraction.
- All 883 distinct events have log folders in both manifestation archives.

**Resolved:**

- **243 steps.** Our old notes listed the paper's "243 steps" as a mismatch. There are 243 distinct
  scenario steps, each identical across its variants. The 904 rows are those steps across all runs.
- **`cmd` "conflicts" are not label errors.** 21 commands carry more than one label set (`id`, `rm`,
  `key`). The text is shortened and generic, and the same step always has the same labels (243 of 243).

**Real issues:**

| # | Finding | Measured | Why it matters |
|---|---|---|---|
| 1 | **Test points that are exact copies of training** (same 16-step window and same target) | **53.8%** of variant-held-out points (S1 67%, S6 39%, S3 24%); **0%** of scenario-held-out | A model can score well by memorising. **The biggest validity issue** |
| 2 | Target labels already in the window | 47.2% | Repeating is easy; new techniques are the hard part. Results need both |
| 3 | Next step has the same labels as the current step | 37.6% of transitions | Same point: a simple "repeat" scores well |
| 4 | Labels seen in one scenario only | 47 of 81 | No model can learn them for an unseen scenario |
| 5 | Unseen-label limit on recall, scenario-held-out | S2 78.1%, S3 68.6%, **S6 41.2%** | A hard ceiling for every model |
| 6 | Rare labels | 10 occur once; 18 occur 3 times or fewer | Macro-F1 is unstable |
| 7 | `tactics` cell is unseparated text | e.g. `reconnaissancereconnaissance` | Unusable until parsed |
| 8 | `end` is in whole seconds | all 904 rows; one 0.64 s overlap | Durations are approximate |
| 9 | Unlabelled commands are missing | 945 in the old corpus; new count pending the scan | The sequence is not the attacker's full activity |
| 10 | Limited diversity | 34 runs, 7 scenarios; S1 is 58% of steps | No preprocessing can fix this |

## 3. Preprocessing to do

**Rule: `steps.jsonl` is not edited.** It is pinned by SHA-256 in the frozen Idea 01 protocol and underlies
the sealed Kuwano predictions. New information goes in a separate file, keyed by `source_row`.

| # | Action | Fixes | When |
|---|---|---|---|
| 1 | Run the full scan; record the results | Section 1 gaps | **First (GPU PC)** |
| 2 | Match `attackmate.json` to the 904 steps; count unlabelled commands; recover full command text | 9 | After the scan |
| 3 | Parse `tactics` into a clean list | 7 | Now |
| 4 | Add `gap_prev` and `duration`; clip the one overlap to 0 | 8 | Now |
| 5 | Mark each test point, per fold, as **copy** or **novel** | 1 | Now |
| 6 | Mark each target label as **repeat** or **new** | 2, 3 | Now |
| 7 | Fix the label vocabulary at 81 for every model | old vocabulary | Before the encoder port |
| 8 | Define `collapse_repeats`: keep the first occurrence (21 rows removed, 883 left) | sensitivity | Now |
| 9 | Record the analysis-repository commit hash | B1 | You |
| 10 | Check the S4 `Firewall` zone against `facts.json` | open since 2026-10-24 | After the scan |

**Do not do:**

- **Do not drop rare labels** (it would hide finding 5).
- **Do not delete copy points** (the frozen protocol keeps them; report novel points beside them).
- **Do not use `cmd` as model input** (shortened text; see step 2).
- **Do not preprocess the raw logs.** No model reads them.

**Protocol impact.** Items 5 and 6 add reporting, so they need a new protocol version **before any test
result is opened**. They do not change the sealed predictions.

## 4. Before and after the download

| | Before (old corpus) | Now (`camlds_real`) |
|---|---|---|
| Source | Our parse of AttackBed playbooks | Released `attack_times.csv` |
| Nature | Static playbook text | **Recorded executions** |
| Timestamps | None | Start and end for every step |
| Order | Playbook order | True time order |
| Repeated executions | Not visible | Kept (21 extra rows) |
| Runs | 36 | **34** |
| Steps | 889 | **904** |
| S3 runs / S3 steps | 8 / 165 | **6 / 160** |
| S6 steps | 114 | **137** |
| S1 steps | 525 | 522 |
| S2, S4, S5, S7 steps | 47, 22, 3, 13 | same |
| Sub-techniques | 99 | **97** |
| Parent techniques | 82 (84-slot model vocabulary) | **81** |
| Sub-technique instances | 1,347 | 1,351 |
| Multi-label steps | 211 | 203 |
| Distinct transitions | 187 | 183 |
| Transitions seen once | 59 | 55 |
| Same-label transitions | 292 of 853 (34.2%) | 327 of 870 (37.6%) |
| Labels seen once | 9 | 10 |
| Raw logs | None | **49.45 GB** (21.82 GB distinct) |
| Integrity | Playbook hashes recorded | MD5-verified against Zenodo (v1) |
| Split | Variant-level | **Two families, frozen before any run** |

**What the download did not change:** the same 81 parent techniques (T1572 exists only in the old
corpus), the same 7 scenarios, the same S1 dominance, and the same scripted origin. It improves
**validity**, not **diversity**. Only 5 of 34 runs have the same order as our old parse, so old results
must not be pooled with new ones.
