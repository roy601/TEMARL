# Report: Shell Attack Evolution (SRDS 2025), route A

**Paper verdict: partially reproduced.** From the authors' released data, the session-level numbers
reproduce exactly; the MITRE ATT&CK numbers (Tables VI, VII, VIII and the technique counts) do not,
under the primary definition or under any of the alternates. The released ATT&CK labels use a
different set of techniques from the one the paper's tables were computed on.

Run on GPU PC 2 (commit e24406f) and on a second PC: `results.json` and `REPORT_TABLE.md` are
**byte-identical** (SHA-256 0e1fafab… and a5fbf3b3…). Targets and decisions were committed before
any code existed (36e4575); `run.py` before any result (653f6a6).

## Summary

| | targets | MATCH | CLOSE | NO MATCH | NOT ATTEMPTED |
|---|---|---|---|---|---|
| all | 116 | 14 | 2 | 94 | 6 |
| primary | 16 | 4 | 0 | 12 | 0 |

**Reproduced (MATCH):**
- sessions: 5,365 (2021–22, Table I) and 6,658 (2024); Table V's 5,363 does not match;
- average session length: 12.655 → 12.65 and 4.995 → 5.00;
- session kinds 2021–22: 4,161;
- most frequent command 2024: `cd ~; chattr -ia .ssh; lockr -ia .ssh`.

**Not reproduced:**
- *Technique counts:* the released labels hold 24 distinct technique IDs in each period; the paper says
  22 and 27. Six released IDs never appear in Table VII (T1036, T1037, T1057, T1120, T1531, T1590), and
  several Table VII IDs are absent from the released 2024 labels (for example T1124, T1518, T1614,
  T1655). No definition of "usage frequency" can turn one label set into the other.
- *Technique shares (Table VII):* for example T1070 2024 is 17.176% in the paper; we get 21.578%
  (primary). The alternates give 18.162% (each occurrence), 13.370% (command-weighted) and 83.433%
  (share of sessions). None is within tolerance for the primary targets.
- *Tactic shares (Table VI):* Defense Evasion 2024 is 38.77%; we get 27.84% (primary) or 44.15% (sum of
  technique shares). The paper's tactic shares are not the sum of its own technique shares either
  (Discovery 2021–22: 43.73% summed from Table VII against 33.13% in Table VI), so the tactic definition
  is unknown.
- *Session kinds 2024* 1,458 against 3,118; *most frequent command 2021–22* is
  `cat /proc/cpuinfo | grep name | wc -l` (3,225 times), not `uname`.

**What does hold:**
- *Order of technique pairs (Table VIII):* the three most frequent ordered pairs are the same pairs in
  the same order in both periods. 2021–22: T1082→T1098, T1087→T1082, T1098→T1059; 2024: T1222→T1070,
  T1098→T1222, T1070→T1098. The percentages differ (2024 rank 1: 15.25% against 14.02%).
- *The paper's direction of change:* Defense Evasion and T1070/T1222 rise sharply, Discovery falls, and
  sessions get shorter. These trends reproduce, but the exact values do not.

## Findings about the paper itself (no data needed)

- The Discovery standard deviations (0.0645, 0.0239) are the **sample** standard deviations of the
  paper's own Table VII values (0.06452, 0.02390). The paper is consistent with itself here; our
  pre-registered population standard deviation was the other reading. From the data neither matches
  (sample: 0.051 and 0.027).
- Tables VI and VII each sum to 100% (±0.01).
- The five inconsistencies listed in DECISIONS.md stand. Additionally, our count of distinct
  `session_pattern` values for 2021–22 is 245, the number Table V prints for 2024 in the undefined
  "Session pattern" row; this may be a swapped cell, but it cannot be checked without the authors.

## What this means for Idea 02

- The released per-session technique sequences are usable data, but the paper's ATT&CK statistics
  cannot be used to validate them: they were computed from a different labelling.
- Q3 stays open: `attack_techniques` is one sequence per session (consecutive repeats collapsed), not
  one label set per command. Route B (stage 2: raw logs through the authors' mapping script
  `07a_map_attack_techniques.py`) can show whether per-command labels can be rebuilt, and whether that
  script reproduces Table VII.

## All targets

| id | quantity | published | ours | difference | verdict |
|---|---|---|---|---|---|
| T1.attacks.2021_2022 | Number of Attacks, cowrie-2021,2022 | 5099153 | - | - | NOT ATTEMPTED |
| T1.attacks.2024 | Number of Attacks, cowrie-2024 | 3914173 | - | - | NOT ATTEMPTED |
| T1.sessions.2021_2022 | Effective Attack Sessions, 2021-2022 | 5365 | 5365 | 0.0000 | MATCH |
| T1.sessions.2024 | Effective Attack Sessions, 2024 | 6658 | 6658 | 0.0000 | MATCH |
| T5.session_counts.2021_2022 | Session counts, 2021-2022 | 5363 | 5365 | 2.0000 | NO MATCH |
| T5.session_counts.2024 | Session counts, 2024 | 6658 | 6658 | 0.0000 | MATCH |
| T5.session_kinds.2021_2022 | Session Kinds, 2021-2022 | 4161 | 4161 | 0.0000 | MATCH |
| T5.session_kinds.2024 | Session Kinds, 2024 | 3118 | 1458 | -1660.0000 | NO MATCH |
| T5.session_pattern_row.2021_2022 | Session pattern (row 3, undefined), 2021-2022 | 144 | - | - | NOT ATTEMPTED |
| T5.session_pattern_row.2024 | Session pattern (row 3, undefined), 2024 | 245 | - | - | NOT ATTEMPTED |
| T5.n_session_patterns.2021_2022 | Number of Session Patterns, 2021-2022 | 145 | 245 | 100.0000 | NO MATCH |
| T5.n_session_patterns.2024 | Number of Session Patterns, 2024 | 156 | 199 | 43.0000 | NO MATCH |
| T5.avg_session_length.2021_2022 | Average Session Length (commands), 2021-2022 | 12.65 | 12.6550 | 0.0050 | MATCH |
| T5.avg_session_length.2024 | Average Session Length (commands), 2024 | 5.00 | 4.9953 | -0.0047 | MATCH |
| T5.avg_length_per_kind.2021_2022 | Average Length per Session Kind, 2021-2022 | 10.97 | 15.5477 | 4.5777 | NO MATCH |
| T5.avg_length_per_kind.2024 | Average Length per Session Kind, 2024 | 11.80 | 14.4390 | 2.6390 | NO MATCH |
| T6.Discovery.2021_2022 | Discovery tactic usage frequency %, 2021-2022 | 33.13 | 17.0826 | -16.0474 | NO MATCH |
| T6.Discovery.2024 | Discovery tactic usage frequency %, 2024 | 18.05 | 10.8712 | -7.1788 | NO MATCH |
| T6.Collection.2021_2022 | Collection tactic usage frequency %, 2021-2022 | 0.02 | 15.7575 | 15.7375 | NO MATCH |
| T6.Collection.2024 | Collection tactic usage frequency %, 2024 | 0.21 | 0.3326 | 0.1226 | NO MATCH |
| T6.Command_and_Control.2021_2022 | Command and Control tactic usage frequency %, 2021-2022 | 1.60 | 4.4115 | 2.8115 | NO MATCH |
| T6.Command_and_Control.2024 | Command and Control tactic usage frequency %, 2024 | 1.79 | 2.8146 | 1.0246 | NO MATCH |
| T6.Credential_Access.2021_2022 | Credential Access tactic usage frequency %, 2021-2022 | 0.00 | 0.0000 | 0.0000 | MATCH |
| T6.Credential_Access.2024 | Credential Access tactic usage frequency %, 2024 | 0.01 | 0.0347 | 0.0247 | NO MATCH |
| T6.Defense_Evasion.2021_2022 | Defense Evasion tactic usage frequency %, 2021-2022 | 7.58 | 15.8210 | 8.2410 | NO MATCH |
| T6.Defense_Evasion.2024 | Defense Evasion tactic usage frequency %, 2024 | 38.77 | 27.8382 | -10.9318 | NO MATCH |
| T6.Execution.2021_2022 | Execution tactic usage frequency %, 2021-2022 | 18.01 | 20.7879 | 2.7779 | NO MATCH |
| T6.Execution.2024 | Execution tactic usage frequency %, 2024 | 14.88 | 8.9303 | -5.9497 | NO MATCH |
| T6.Impact.2021_2022 | Impact tactic usage frequency %, 2021-2022 | 0.02 | 0.0238 | 0.0038 | MATCH |
| T6.Impact.2024 | Impact tactic usage frequency %, 2024 | 0.07 | 0.1340 | 0.0640 | NO MATCH |
| T6.Persistence.2021_2022 | Persistence tactic usage frequency %, 2021-2022 | 19.75 | 12.8655 | -6.8845 | NO MATCH |
| T6.Persistence.2024 | Persistence tactic usage frequency %, 2024 | 13.11 | 24.5073 | 11.3973 | NO MATCH |
| T6.Privilege_Escalation.2021_2022 | Privilege Escalation tactic usage frequency %, 2021-2022 | 19.88 | 13.2503 | -6.6297 | NO MATCH |
| T6.Privilege_Escalation.2024 | Privilege Escalation tactic usage frequency %, 2024 | 13.12 | 24.5371 | 11.4171 | NO MATCH |
| T7.T1016.2021_2022 | T1016 technique usage frequency %, 2021-2022 | 0.085 | 0.1301 | 0.0451 | NO MATCH |
| T7.T1016.2024 | T1016 technique usage frequency %, 2024 | 1.751 | 1.6314 | -0.1196 | NO MATCH |
| T7.T1033.2021_2022 | T1033 technique usage frequency %, 2021-2022 | 0.004 | 0.0000 | -0.0040 | NO MATCH |
| T7.T1033.2024 | T1033 technique usage frequency %, 2024 | 1.589 | 0.0039 | -1.5851 | NO MATCH |
| T7.T1069.2021_2022 | T1069 technique usage frequency %, 2021-2022 | 0 | 0.0000 | 0.0000 | MATCH |
| T7.T1069.2024 | T1069 technique usage frequency %, 2024 | 0.016 | 0.0272 | 0.0112 | NO MATCH |
| T7.T1082.2021_2022 | T1082 technique usage frequency %, 2021-2022 | 18.294 | 10.8641 | -7.4299 | NO MATCH |
| T7.T1082.2024 | T1082 technique usage frequency %, 2024 | 6.894 | 5.2012 | -1.6928 | NO MATCH |
| T7.T1083.2021_2022 | T1083 technique usage frequency %, 2021-2022 | 8.058 | 11.4985 | 3.4405 | NO MATCH |
| T7.T1083.2024 | T1083 technique usage frequency %, 2024 | 4.499 | 6.6384 | 2.1394 | NO MATCH |
| T7.T1087.2021_2022 | T1087 technique usage frequency %, 2021-2022 | 11.551 | 9.0448 | -2.5062 | NO MATCH |
| T7.T1087.2024 | T1087 technique usage frequency %, 2024 | 4.382 | 5.1585 | 0.7765 | NO MATCH |
| T7.T1124.2021_2022 | T1124 technique usage frequency %, 2021-2022 | 0.004 | 0.0081 | 0.0041 | NO MATCH |
| T7.T1124.2024 | T1124 technique usage frequency %, 2024 | 0.002 | 0.0000 | -0.0020 | CLOSE |
| T7.T1424.2021_2022 | T1424 technique usage frequency %, 2021-2022 | 5.726 | 0.1085 | -5.6175 | NO MATCH |
| T7.T1424.2024 | T1424 technique usage frequency %, 2024 | 1.835 | 0.6137 | -1.2213 | NO MATCH |
| T7.T1518.2021_2022 | T1518 technique usage frequency %, 2021-2022 | 0.004 | 0.0054 | 0.0014 | CLOSE |
| T7.T1518.2024 | T1518 technique usage frequency %, 2024 | 0.133 | 0.0000 | -0.1330 | NO MATCH |
| T7.T1614.2021_2022 | T1614 technique usage frequency %, 2021-2022 | 0 | 0.0000 | 0.0000 | MATCH |
| T7.T1614.2024 | T1614 technique usage frequency %, 2024 | 0.006 | 0.0000 | -0.0060 | NO MATCH |
| T7.T1005.2021_2022 | T1005 technique usage frequency %, 2021-2022 | 0.023 | 10.7692 | 10.7462 | NO MATCH |
| T7.T1005.2024 | T1005 technique usage frequency %, 2024 | 0.240 | 0.2603 | 0.0203 | NO MATCH |
| T7.T1071.2021_2022 | T1071 technique usage frequency %, 2021-2022 | 0 | 0.0000 | 0.0000 | MATCH |
| T7.T1071.2024 | T1071 technique usage frequency %, 2024 | 0.019 | 0.0078 | -0.0112 | NO MATCH |
| T7.T1105.2021_2022 | T1105 technique usage frequency %, 2021-2022 | 2.113 | 3.0149 | 0.9019 | NO MATCH |
| T7.T1105.2024 | T1105 technique usage frequency %, 2024 | 2.070 | 2.2025 | 0.1325 | NO MATCH |
| T7.T1003.2021_2022 | T1003 technique usage frequency %, 2021-2022 | 0 | 0.0000 | 0.0000 | MATCH |
| T7.T1003.2024 | T1003 technique usage frequency %, 2024 | 0.017 | 0.0272 | 0.0102 | NO MATCH |
| T7.T1059.2021_2022 | T1059 technique usage frequency %, 2021-2022 | 18.043 | 14.2071 | -3.8359 | NO MATCH |
| T7.T1059.2024 | T1059 technique usage frequency %, 2024 | 15.815 | 6.9880 | -8.8270 | NO MATCH |
| T7.T1053.2021_2022 | T1053 technique usage frequency %, 2021-2022 | 5.731 | 8.7276 | 2.9966 | NO MATCH |
| T7.T1053.2024 | T1053 technique usage frequency %, 2024 | 1.583 | 2.8395 | 1.2565 | NO MATCH |
| T7.T1098.2021_2022 | T1098 technique usage frequency %, 2021-2022 | 20.268 | 8.7927 | -11.4753 | NO MATCH |
| T7.T1098.2024 | T1098 technique usage frequency %, 2024 | 13.740 | 19.1773 | 5.4373 | NO MATCH |
| T7.T1547.2021_2022 | T1547 technique usage frequency %, 2021-2022 | 0.069 | 0.0000 | -0.0690 | NO MATCH |
| T7.T1547.2024 | T1547 technique usage frequency %, 2024 | 0.005 | 0.0000 | -0.0050 | NO MATCH |
| T7.T1548.2021_2022 | T1548 technique usage frequency %, 2021-2022 | 0.173 | 0.2630 | 0.0900 | NO MATCH |
| T7.T1548.2024 | T1548 technique usage frequency %, 2024 | 0.019 | 0.0272 | 0.0082 | NO MATCH |
| T7.T1027.2021_2022 | T1027 technique usage frequency %, 2021-2022 | 0.499 | 0.3470 | -0.1520 | NO MATCH |
| T7.T1027.2024 | T1027 technique usage frequency %, 2024 | 1.582 | 0.0388 | -1.5432 | NO MATCH |
| T7.T1070.2021_2022 | T1070 technique usage frequency %, 2021-2022 | 1.834 | 2.4076 | 0.5736 | NO MATCH |
| T7.T1070.2024 | T1070 technique usage frequency %, 2024 | 17.176 | 21.5778 | 4.4018 | NO MATCH |
| T7.T1222.2021_2022 | T1222 technique usage frequency %, 2021-2022 | 5.840 | 8.7384 | 2.8984 | NO MATCH |
| T7.T1222.2024 | T1222 technique usage frequency %, 2024 | 22.948 | 19.4958 | -3.4522 | NO MATCH |
| T7.T1562.2021_2022 | T1562 technique usage frequency %, 2021-2022 | 0 | 0.0000 | 0.0000 | MATCH |
| T7.T1562.2024 | T1562 technique usage frequency %, 2024 | 1.585 | 2.8473 | 1.2623 | NO MATCH |
| T7.T1564.2021_2022 | T1564 technique usage frequency %, 2021-2022 | 0.005 | 0.0081 | 0.0031 | NO MATCH |
| T7.T1564.2024 | T1564 technique usage frequency %, 2024 | 0.146 | 0.1670 | 0.0210 | NO MATCH |
| T7.T1655.2021_2022 | T1655 technique usage frequency %, 2021-2022 | 1.650 | 0.0081 | -1.6419 | NO MATCH |
| T7.T1655.2024 | T1655 technique usage frequency %, 2024 | 1.874 | 0.0000 | -1.8740 | NO MATCH |
| T7.T1489.2021_2022 | T1489 technique usage frequency %, 2021-2022 | 0.021 | 0.0163 | -0.0047 | NO MATCH |
| T7.T1489.2024 | T1489 technique usage frequency %, 2024 | 0.073 | 0.1049 | 0.0319 | NO MATCH |
| T7.T1496.2021_2022 | T1496 technique usage frequency %, 2021-2022 | 0.005 | 0.0000 | -0.0050 | NO MATCH |
| T7.T1496.2024 | T1496 technique usage frequency %, 2024 | 0.004 | 0.0000 | -0.0040 | NO MATCH |
| S4D.n_techniques.2021_2022 | number of ATT&CK techniques, 2021-2022 | 22 | 24 | 2.0000 | NO MATCH |
| S4D.n_techniques.2024 | number of ATT&CK techniques, 2024 | 27 | 24 | -3.0000 | NO MATCH |
| S4D.discovery_std.2021_2022 | std of Discovery technique usage, 2021-2022 | 0.0645 | 0.0482 | -0.0163 | NO MATCH |
| S4D.discovery_std.2024 | std of Discovery technique usage, 2024 | 0.0239 | 0.0252 | 0.0013 | NO MATCH |
| S4B.ubuntu_share.2021_2022 | share of commands that are standard Ubuntu commands %, 2021-2022 | 41.43 | - | - | NOT ATTEMPTED |
| S4B.ubuntu_share.2024 | share of commands that are standard Ubuntu commands %, 2024 | 48.44 | - | - | NOT ATTEMPTED |
| T8.rank1.2021_2022 | rank 1 ordered pair T1082->T1098 share %, 2021-2022 | 12.016 | 10.0402 | -1.9758 | NO MATCH |
| T8.rank2.2021_2022 | rank 2 ordered pair T1087->T1082 share %, 2021-2022 | 12.006 | 10.0305 | -1.9755 | NO MATCH |
| T8.rank3.2021_2022 | rank 3 ordered pair T1098->T1059 share %, 2021-2022 | 10.159 | 8.4867 | -1.6723 | NO MATCH |
| T8.rank4.2021_2022 | rank 4 ordered pair T1059->T1098 share %, 2021-2022 | 7.523 | 6.2816 | -1.2414 | NO MATCH |
| T8.rank5.2021_2022 | rank 5 ordered pair T1053->T1087 share %, 2021-2022 | 6.216 | 5.1927 | -1.0233 | NO MATCH |
| T8.rank6.2021_2022 | rank 6 ordered pair T1083->T1053 share %, 2021-2022 | 6.214 | 5.1911 | -1.0229 | NO MATCH |
| T8.rank7.2021_2022 | rank 7 ordered pair T1082->T1424 share %, 2021-2022 | 6.115 | 0.0000 | -6.1150 | NO MATCH |
| T8.rank8.2021_2022 | rank 8 ordered pair T1424->T1087 share %, 2021-2022 | 5.994 | 0.0016 | -5.9924 | NO MATCH |
| T8.rank9.2021_2022 | rank 9 ordered pair T1098->T1222 share %, 2021-2022 | 5.806 | 4.8507 | -0.9553 | NO MATCH |
| T8.rank10.2021_2022 | rank 10 ordered pair T1098->T1083 share %, 2021-2022 | 4.418 | 0.0000 | -4.4180 | NO MATCH |
| T8.rank1.2024 | rank 1 ordered pair T1222->T1070 share %, 2024 | 14.024 | 15.2465 | 1.2225 | NO MATCH |
| T8.rank2.2024 | rank 2 ordered pair T1098->T1222 share %, 2024 | 12.288 | 15.1451 | 2.8571 | NO MATCH |
| T8.rank3.2024 | rank 3 ordered pair T1070->T1098 share %, 2024 | 12.286 | 15.1359 | 2.8499 | NO MATCH |
| T8.rank4.2024 | rank 4 ordered pair T1059->T1070 share %, 2024 | 3.784 | 3.9715 | 0.1875 | NO MATCH |
| T8.rank5.2024 | rank 5 ordered pair T1098->T1059 share %, 2024 | 3.706 | 3.9807 | 0.2747 | NO MATCH |
| T8.rank6.2024 | rank 6 ordered pair T1082->T1098 share %, 2024 | 2.614 | 3.1262 | 0.5122 | NO MATCH |
| T8.rank7.2024 | rank 7 ordered pair T1083->T1083 share %, 2024 | 2.564 | 0.0000 | -2.5640 | NO MATCH |
| T8.rank8.2024 | rank 8 ordered pair T1059->T1105 share %, 2024 | 2.278 | 1.7859 | -0.4921 | NO MATCH |
| T8.rank9.2024 | rank 9 ordered pair T1036->T1059 share %, 2024 | 2.184 | 1.9089 | -0.2751 | NO MATCH |
| T8.rank10.2024 | rank 10 ordered pair T1083->T1036 share %, 2024 | 2.125 | 1.7798 | -0.3452 | NO MATCH |
| T4.rank1.2021_2022 | most frequent command, 2021-2022 | uname | cat /proc/cpuinfo \| grep name \| wc -l | - | NO MATCH |
| T4.rank1.2024 | most frequent command, 2024 | cd ~ ; chattr -ia .ssh ; lockr -ia .ssh | cd ~; chattr -ia .ssh; lockr -ia .ssh | - | MATCH |

Primary definitions only; the alternates for every target are in `out/results.json`.
Numbers in "ours" are rounded to 4 decimals here; full precision is in `out/results.json`.

## Checklist (STANDARD.md, Section 2)

| # | requirement | met? | where |
|---|---|---|---|
| 1 | targets committed before any result | yes | 36e4575 before e24406f; `audit.py` |
| 2 | gaps decided before the run | yes | `DECISIONS.md` (36e4575) |
| 3 | authors asked about every gap | **not yet**: questions drafted, to be posted by the user | `AUTHOR_CONTACT.md` |
| 4 | exact sources and licence | yes | `SOURCES.md`, input SHA-256 in `out/results.json` |
| 5 | variance: two machines identical | yes | identical SHA-256 on GPU PC 2 and a second PC |
| 6 | every target reported | yes | table above, `audit.py` |
| 7 | environment recorded | yes | `out/ENVIRONMENT.json` |
| 8 | one command from public inputs, outputs hashed | yes | `run.py`, `out/HASHES.txt` |
| 9 | unit tests for each rule | yes | `tests/test_run.py` (10 tests) |
| 10 | comparison only after this report | not started | — |

Route B (stage 2) is pre-registered in DECISIONS.md 1 and covers the 4 "route B" targets.
