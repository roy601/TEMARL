# Decisions

Written 2026-11-13, before `run.py` existed and before any paper number was computed from the data.
Each decision names its **primary** definition. Verdicts use only the primary definition; the
alternates are computed and reported next to it, so a reader can see whether another reading of the
paper would change the verdict. No alternate may replace a primary after the run.

## What I had seen before writing this (disclosure)

- The 2026-11-12 dataset survey (`dataset_survey/out/shell_attack_evolution/`) showed file sizes and
  line counts: the two session files have 5,365 and 6,658 lines, the two command files 12,923 and
  4,236 lines, and each session file contains 24 distinct ATT&CK-shaped IDs.
- The authors' scripts (read 2026-11-13). `analysis/period_2024/07b_technique_frequency.py` carries a
  printed output in a comment that lists techniques absent from Table VII (for example T1531 with
  11,971 and T1057 with 3,180).
- No share, average, count of kinds or pair frequency had been computed from the data.

## Route

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 1 | Which data to start from | **Route A (this run):** the released `dataset/sessions/{2021_2022,2024}.jsonl` and `dataset/commands/{...}.jsonl` at commit d5f7fe1. **Route B (stage 2, separate run, same targets):** the raw Cowrie logs through the authors' numbered scripts, with path changes only. The targets marked "route B" in `TARGETS.csv` are NOT ATTEMPTED until stage 2. | Route A tests whether the paper's numbers follow from the released data. Route B tests whether the released data follow from the raw logs. The scripts' intermediate files are not released, so route A cannot use the scripts directly. | 2026-11-13 |
| 2 | `paper_*.jsonl` files | Never read as data. | They are transcriptions of the paper (their own docstring). | 2026-11-13 |

## Definitions

| # | gap | primary | alternates reported | why | decided on |
|---|---|---|---|---|---|
| 3 | Session | one row of a session file (= all commands of one attacker IP; paper Sec. III.A) | — | stated in the paper | 2026-11-13 |
| 4 | Session count (Table I 5,365 vs Table V 5,363, text 6,659) | number of rows | — | the paper gives two values for 2021–2022; both are targets, so at most one can match | 2026-11-13 |
| 5 | Average Session Length | mean of `len(commands)` over sessions | mean of `command_count`; the authors' `08_session_length.py` (mean length over distinct session patterns) | the paper text says "commands per session" | 2026-11-13 |
| 6 | Session Kinds | number of distinct ordered `commands` lists | number of distinct command sets | "kind" is not defined; identical command sequences are the most literal reading | 2026-11-13 |
| 7 | Number of Session Patterns | number of distinct `session_pattern` values | — | the released field has this name; the paper says "sessions with the same pattern ... belong to the same attack entity" | 2026-11-13 |
| 8 | Table V row "Session pattern" (144 / 245) | **no primary**: verdict NOT ATTEMPTED | number of `session_pattern` values shared by 2 or more sessions (shown as information only) | the row is not defined anywhere and differs from the next row | 2026-11-13 |
| 9 | Average Length per Session Kind | mean length over distinct `commands` lists (decision 6) | mean length over distinct `session_pattern` values | follows decision 6 | 2026-11-13 |
| 10 | Technique usage frequency (Table VII) | **per-session presence**: share of technique t = (sessions whose `attack_techniques` contain t) / (sum of that count over all techniques), in % | (b) every occurrence in `attack_techniques`; (c) presence weighted by the session's `command_count` ("command-weighted", the authors' script docstrings); (d) presence / number of sessions | the paper (Sec. IV.D) says the techniques of a session are "consolidated into one occurrence"; the scripts say otherwise, so the paper's own text is primary | 2026-11-13 |
| 11 | Tactic usage frequency (Table VI) | per-session presence of a tactic, share of all tactic presences, with the technique-to-tactic mapping printed in Table VI (T1098, T1053, T1547 count for Persistence and Privilege Escalation; T1548 for Privilege Escalation and Defense Evasion) | sum of the decision-10 technique shares inside each tactic | same reading as decision 10; techniques not in Table VI's mapping are counted as "unmapped" and reported | 2026-11-13 |
| 12 | Number of techniques | distinct IDs in `attack_techniques`, per period, as written | — | IDs are compared exactly as written: T1036 and T1655 are not merged, T1424 is kept | 2026-11-13 |
| 13 | Discovery standard deviation | population standard deviation (ddof 0) of the decision-10 shares, as fractions, of the 10 Discovery techniques in Table VI | sample standard deviation (ddof 1); the same from the published Table VII (an internal check of the paper, no data) | the paper does not say which | 2026-11-13 |
| 14 | Ordered technique pairs (Table VIII) | every consecutive pair (a, b) inside each session's `attack_techniques`, counted per occurrence; share = count / all pairs of the period, in % | per-session presence of a pair | "ordered 2-tuples ... share of all observed two-technique combinations" | 2026-11-13 |
| 15 | Most frequent command (Table IV, rank 1) | the command with the largest `frequency` in `dataset/commands/<period>.jsonl`, compared as text with spaces around `;` ignored | the most frequent `command_pattern` | Table IV shows commands with parameters abstracted; rank 1 has no parameters in either period | 2026-11-13 |

## Verdict rules

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 16 | Tolerance | one unit of the last published digit (as in `TARGETS.csv`); CLOSE = within twice that | published values are rounded | 2026-11-13 |
| 17 | Variance | deterministic: `run.py` is run on GPU PC 2 and on a second PC; every output's SHA-256 must be identical | STANDARD.md requirement 5 | 2026-11-13 |

## Inconsistencies inside the paper (recorded before the run)

1. 2021–2022 sessions: Table I says 5,365, Table V 5,363; the text says session kinds rose "from 5,363 ... to 6,659" while Table V gives 4,161 → 3,118 session kinds and 6,658 sessions.
2. Table V has two rows, "Session pattern" (144 / 245) and "Number of Session Patterns" (145 / 156), with no definition.
3. Table VIII is headed "2020–2021"; the data are 2021–2022.
4. The paper says it uses the ATT&CK Enterprise matrix, but T1424 (Process Discovery) and T1655 are Mobile-matrix IDs; Table VIII uses T1036 for Masquerading where Table VII uses T1655.
5. The technique-frequency definition differs between the paper (one occurrence per session) and the scripts ("command-weighted", or weighted by the number of sessions per pattern).

## Route B (stage 2): decisions 18–29

Written 2026-11-13, **after the route A results were known** (report 499dc50) and **before any
route B code or result existed**. They add no target and change no route A decision; route B is
scored against the same `TARGETS.csv`, with the route A primary definitions.

What I had seen before writing these: the route A results; the layout of the raw logs in the
release (236 files, 1.7 GB, for 2024; two short source notes for 2021–2022); the code of the
2024 scripts. No raw log had been parsed.

| # | gap | choice | why | decided on |
|---|---|---|---|---|
| 18 | 2021–2022 raw logs | **NOT ATTEMPTED.** The release holds only two notes naming third-party sources: the 2021 logs (Başer et al.) now on Kaggle behind a login, and the 2022 logs (Priya et al.) on a personal OneDrive link that returns HTTP 404 (checked 2026-11-13). One of the two parts cannot be obtained, so the period cannot be rebuilt. | the README's "full raw capture preserved" does not hold for 2021–2022; this is recorded as a finding | 2026-11-13 |
| 19 | 2024 code | the authors' `analysis/period_2024/` scripts at commit d5f7fe1, copied unchanged into a work folder and run in their order: the read-raw-logs block of `01_extract_sessions.py` (commented out in the release; run as written with only the leading `# ` removed), then 01, 02, 03, 04, 05, 07a, 07b | their own pipeline; 06* (response replay) and 08 (plots) produce no target | 2026-11-13 |
| 20 | Allowed changes | **none to any logic.** Only: the environment variable `MPLBACKEND=Agg`, so `plt.show()` does not wait for a window. If a step fails for any other reason, it is recorded as failed with its error, later steps are NOT ATTEMPTED, and nothing is patched | a patched pipeline would no longer be the authors' | 2026-11-13 |
| 21 | Number of Attacks (Table I, 2024) | primary: the number of records their read-raw-logs block loads (`len(merged_df)`, which the block prints as "the number of commands in the dataset") | that is the count their code produces | 2026-11-13 |
| 22 | Sessions | primary: entries of the rebuilt `session_dict.json`; average length = mean list length | as route A, decision 3 and 5 | 2026-11-13 |
| 23 | Session kinds and patterns | kinds: distinct command lists in `session_dict.json`; patterns: keys of the rebuilt `5-session归类.json` | as route A, decisions 6–7 | 2026-11-13 |
| 24 | Techniques per session | the rebuilt `7-session_tech_no_dup.json` (techniques of a session pattern, consecutive repeats removed), given to every session of that pattern; then the route A primary definitions (decisions 10–14) | the same definitions on rebuilt labels | 2026-11-13 |
| 25 | The authors' own technique count | alternate: shares from the weighted counts that `07b_technique_frequency.py` prints | their code's own answer, next to the primary | 2026-11-13 |
| 26 | Most frequent command | primary: top of the rebuilt `2-sorted_cmd_counter.json` | as route A, decision 15 | 2026-11-13 |
| 27 | Ubuntu share (Sec. IV.B.2) | **NOT ATTEMPTED** for both periods: `03_2_system_commands.py` only prints word lists; no list of standard Ubuntu commands and no share computation exist in the release | nothing to run | 2026-11-13 |
| 28 | Do the released data follow from the raw logs? | compare rebuilt and released 2024 sessions by attacker IP: same IPs, identical command lists, identical technique sequences; report each as a count and share. Not a target, a finding | tests the release itself | 2026-11-13 |
| 29 | Per-command labels (Idea 02, Q3) | label each command of each rebuilt session with the authors' own tables, exactly as the loop in `07a_map_attack_techniques.py` does (complex command → `compound_pattern_mapped_attck`, simple command → first matching entry of `simple_commands_attck`), with the tables taken from running their 07a unchanged. Report: share of commands with at least one technique. Q3 passes if the procedure is deterministic (identical on two machines) | answers whether their released code gives per-command labels | 2026-11-13 |
