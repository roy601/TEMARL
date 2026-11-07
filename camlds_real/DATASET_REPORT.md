# CAM-LDS dataset report

**Status: every file has been read and the dataset is intact. No data file has been changed.
Preprocessing approved and built on 2026-11-07, in `out/sidecar/` (protocol 1.1).**
Evidence: `out/LINE_AUDIT.txt`, `out/CORPUS_MEASURES.txt`, `out/scan/`, `out/ATTACKMATE_RECONCILE.txt`,
`out/sidecar/SIDECAR_REPORT.txt`.

## 1. What has been read

| Data | Size | Read |
|---|---|---|
| `attack_times.csv`, the only file the pipeline uses | 904 rows | **Every row and field** |
| `out/steps.jsonl`, our extracted corpus | 904 steps | **Every row, against the source** |
| All 37 archives | 406,915 files, 215,236,713 lines, 49.45 GB | **Every line.** 0 read errors |
| `attackmate.json`, the 34 command logs | 1,806 records | **Every record**, matched to the steps |
| Copies of those logs in the manifestation archives | 5,520 files, 9,582 records | **Every record.** None is missing from the 34 logs |
| `facts.json`, host details | 183 files | **Every file.** 0 errors |
| The authors' script that built the CSV | commit `42bbd2c` | Its time and label logic |

**What "every line" means.** Each line was decompressed, counted and checked for encoding. Only the
command logs, `facts.json` and the timestamps in `audit.log` and `eve.json` were interpreted. The meaning of
other log lines was not checked, and no model reads them.

## 2. Findings

**Clean:**

- No malformed rows, duplicate rows, empty fields, stray spaces or non-ASCII bytes (904 of 904).
- All 97 technique IDs are valid and live in the latest ATT&CK (v20.1).
- Every tactic belongs to a technique in its row, and every technique has a tactic in its row.
- `steps.jsonl` matches the source exactly. All 883 distinct events have log folders in both manifestation archives.
- **Every step matches one command record** (904 of 904, none used twice), with **identical labels in the
  same order**. The CSV is generated from these records, so this proves correct copying. It does not
  independently prove the labels are right: the authors wrote them into the attack scripts.
- Logs cover the whole attack in all 182 ranges measured. Only the first and last timestamps were tested.
- All 87,284 non-UTF-8 lines are in system files (87,237 in `compose.ISO-8859-*.inc`, 47 in `Xedit`), not logs.

**Resolved:**

| Question | Answer |
|---|---|
| The paper's "243 steps" | 243 distinct scenario steps, identical across variants. The 904 rows are those steps across all runs |
| 21 commands with several label sets | Not label errors. The `cmd` text is shortened; the same step always has the same labels (243 of 243) |
| S4 `Firewall` target | Confirmed. The implant's `auditf.service` is on `inetfw`, which has addresses on 5 networks. It sits between zones, so it stays `Firewall` |
| 3 labelled commands missing from the CSV | All are `sleep` records (T1546). The label is already on the step before, so nothing is lost |
| Analysis repository commit (B1) | `42bbd2c`, confirmed by file checksums |
| Dataset version | We use v1. v2 only adds `runc init` audit events to S7 logs, which no model reads |

**Corrected:** our notes said `attackmate.json` has no labels. It does (see `DEEP_AUDIT_CORRECTIONS.md`, Correction 5).

**Real issues:**

| # | Finding | Measured | Why it matters |
|---|---|---|---|
| 1 | **Test points that are exact copies of training** (same 16-step window and target) | **53.8%** of variant-held-out points (S1 67%, S6 39%, S3 24%); **0%** of scenario-held-out | A model can score well by memorising. **The biggest validity issue** |
| 2 | Target labels already in the window | 47.2% | Repeating is easy; new techniques are the hard part |
| 3 | Next step has the same labels as the current step | 37.6% of transitions | A simple "repeat" scores well |
| 4 | Labels seen in one scenario only | 47 of 81 | No model can learn them for an unseen scenario |
| 5 | Unseen-label limit on recall, scenario-held-out | S2 78.1%, S3 68.6%, **S6 41.2%** | A hard ceiling for every model |
| 6 | Rare labels | 10 occur once; 18 occur 3 times or fewer | Macro-F1 is unstable |
| 7 | **CSV times are log windows, not command times** | `start` = command start − 2 s; `end` = output + 4 s + any following sleep; 11 starts moved by hand | CSV `end` − `start` is not how long a command ran |
| 8 | **CSV order differs from execution** | 4 of 34 runs (all S6): one pair swapped, 4 of 870 transitions | The authors moved `:wq!` 40 s later to capture an effect. Our sequences inherit this |
| 9 | **Nearly half of the timing is scripted** | 47.9% of attack time is fixed `sleep`; 0 of 361 sleeps are random | Time gaps partly reflect the script, not the attacker |
| 10 | **The sequence is not the attacker's full activity** | 902 records have no step: 430 control (sleeps, variables, local setup) and 472 interactive (clicks, keystrokes, `cd`, `exit`, and some real commands such as `chmod`) | A 16-step window counts labelled steps, not all actions |
| 11 | Limited diversity | 34 runs, 7 scenarios; S1 is 58% of steps | No preprocessing can fix this |

## 3. Preprocessing

**Rule: `steps.jsonl` is not edited.** It is pinned by SHA-256 in the frozen Idea 01 protocol and underlies
the sealed Kuwano predictions. New information goes in a separate file, keyed by `source_row`.

**Approved and built 2026-11-07** (`build_sidecar.py`; all 9 checks pass; 13 tests in `tests/`):

| # | Action | Fixes | Result |
|---|---|---|---|
| 1 | Link each step to its record: log file, position, type, exact start, full command | Shortened `cmd`, issue 8 | `sidecar/steps_link.jsonl`, 904 of 904 |
| 2 | Mark each test point, per fold, as **copy** or **novel** | Issue 1 | `sidecar/points.jsonl` |
| 3 | Mark each target label as **repeat** or **new** | Issues 2, 3 | `sidecar/points.jsonl` |
| 4 | Define `collapse_repeats`: keep the first occurrence (21 rows removed, 883 left) | Sensitivity check | Defined; marks built for it too |
| 5 | Fix the label vocabulary at 81 for every model | Old 84-slot vocabulary | `out/vocab.json`, pinned. The encoder still has 84 slots until the port (B2) |

**Finished or dropped:**

| Item | Outcome |
|---|---|
| Full scan | Done |
| Match command logs to steps; count unlabelled commands | Done (904 matched, 902 unlabelled) |
| Record the analysis-repository commit (B1) | Done |
| Check S4 | Done |
| Parse `tactics` | **Dropped.** No model uses tactics |
| Add `gap_prev` and `duration` | **Dropped.** CSV times are log windows. Any time feature would have to use the command records, and issue 9 argues against one |

**Decided 2026-11-07:** keep the CSV order in `steps.jsonl` (issue 8) and report it as a limitation. It
touches 4 of 870 transitions.

**Do not do:**

- **Do not drop rare labels** (it would hide issue 5).
- **Do not delete copy points** (the frozen protocol keeps them; report novel points beside them).
- **Do not use `cmd` as model input** (shortened text, and it would let a model memorise commands).
- **Do not use CSV `end` − `start` as a duration** (issue 7).
- **Do not preprocess the raw logs.** No model reads them.

**Protocol impact.** Recorded as protocol 1.1 (`idea01_kuwano/PROTOCOL_1.1.md`). It must be committed and
pushed **before any test result is opened**.

## 4. Before and after the download

| | Before (old corpus) | Now (`camlds_real`) |
|---|---|---|
| Source | Our parse of AttackBed playbooks | Released `attack_times.csv` |
| Nature | Static playbook text | **Recorded executions** |
| Timestamps | None | **Log windows** for every step, plus exact command start times |
| Order | Playbook order | Log-window time order (matches execution in 30 of 34 runs) |
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
| Unlabelled commands | 945 | **902** (430 control, 472 interactive) |
| Raw logs | None | **49.45 GB** (21.82 GB distinct) |
| Integrity | Playbook hashes recorded | MD5-verified against Zenodo (v1); every file CRC-checked |
| Split | Variant-level | **Two families, frozen before any run** |

**What the download did not change:** the same 81 parent techniques (T1572 exists only in the old
corpus), the same 7 scenarios, the same S1 dominance, and the same scripted origin. It improves
**validity**, not **diversity**. Only 5 of 34 runs have the same order as our old parse, so old results
must not be pooled with new ones.
