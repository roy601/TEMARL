# Report: Shell Attack Evolution, route B (the authors' pipeline on the raw logs)

**Verdict: the authors' released pipeline does not run to the end on their released raw logs.** It
stops at the step that assigns MITRE ATT&CK techniques (`07a_map_attack_techniques.py`), so the
paper's technique tables (VI, VII, VIII) and the technique counts cannot be regenerated from the
release, and no per-command labels can be produced with the released code.

Decisions 18–29 (commit 0a077b2) were written before the runner existed; the runner (689bc36)
before any route B result. Nothing in the authors' code was changed: only `MPLBACKEND=Agg`.

## The three runs

| run | machine | Python | pandas | numpy | result | SHA-256 of results (without timings) |
|---|---|---|---|---|---|---|
| `out_route_b/` (bbeafc2) | GPU PC 2 | 3.13.15 | 3.1.1 | 2.5.4 | stops at 07a | 459ec3c9… |
| `out_route_b_check_pc1/` (e286d2f) | GPU PC 1 | 3.12.3 | 3.1.1 | 2.5.4 | stops at 07a | 459ec3c9… |
| `out_route_b_pandas22/` (30a7e7d) | GPU PC 2 | 3.13.15 | 2.2.3 | 2.2.6 | stops at 07a | 459ec3c9… |

The outputs are byte-identical on two machines and two pandas versions, so the failure is neither a
machine effect nor a library-version effect. The authors' `requirements.txt` asks only for
`pandas>=1.5`, `numpy>=1.23`, `openpyxl>=3.0`.

## What happened, step by step

| step | what it does | status |
|---|---|---|
| read-raw-logs block of 01 | loads the 236 raw 2024 Cowrie files | ok: **5,598,628 records** |
| 01 | groups commands into one session per attacker | ok |
| 02, 03, 04 | command frequencies; simple vs complex; complex-command patterns | ok |
| 05 | groups sessions by their sequence of command patterns | ok |
| **07a** | maps each command pattern to ATT&CK techniques | **FAILED** |
| 07b | technique frequencies | not attempted |

**The failure.** `07a` looks every complex-command pattern up in its hand-written rule table. One
pattern produced by the authors' own step 04 from the released logs has no entry:

```
attck_value = compound_commands_attck[comd_patt_dict[key]]
KeyError: "('-o', ';', '>', '&&', 'cd', ';', '(', '/bin/busybox', 'echo', '-e', '||', 'echo', '-e', ')')"
```

The script has no fallback for a missing pattern, so it stops. The rule table therefore was not
built from the command set that the released raw logs and the released steps 01–04 produce. Some
filtering, cleaning or log selection must have happened that is not in the release. The paper
mentions manual repair of segmentation errors and removal of echo noise and of repeated requests
(Sec. III.B); none of those steps is in the released pipeline before 07a.

## Targets (route B)

| id | quantity | published | ours | difference | verdict |
|---|---|---|---|---|---|
| T1.attacks.2024 | Number of Attacks, cowrie-2024 | 3914173 | 5598628 | 1684455 | NO MATCH |
| all other 2024 targets | sessions, lengths, kinds, techniques, pairs, top command | (see TARGETS.csv) | - | - | NOT ATTEMPTED: the pipeline stopped at 07a (decision 20) |
| all 2021–2022 targets | — | — | - | - | NOT ATTEMPTED: raw logs not obtainable (decision 18) |
| S4B.ubuntu_share.* | Ubuntu share | 41.43 / 48.44 | - | - | NOT ATTEMPTED: no list or computation in the release (decision 27) |

`T1.attacks.2024` uses decision 21: the number of records the authors' own read block loads, which
it prints as "the number of commands in the dataset". The released 2024 logs hold 1,684,455 more
records than the paper's Table I.

The session-level outputs of steps 01 and 05 do exist on both PCs. They are not scored here, because
decision 20 fixed that steps after a failure are not attempted, and scoring them now would be a
choice made after the result. If they are ever scored, that will be a separate, dated analysis,
marked "after results".

## What this means

1. **For the reproduction.** Route A showed that the released *processed* data reproduce the
   paper's session numbers but not its ATT&CK numbers. Route B shows that the released *code* cannot
   rebuild the ATT&CK labels from the released *raw* data at all. Together: the paper's ATT&CK
   tables cannot be checked from anything in the release.
2. **For Idea 02 (Q3, per-command labels).** **Not met as released.** The labelling code exists, but
   it does not run on the release, and the released labels are per session, not per command. Q3
   could pass only if the authors supply the missing preprocessing or a complete rule table.
3. **For the 2021–2022 period.** Its raw logs are not in the release (two notes point to third-party
   sources: one behind a Kaggle login, one returning HTTP 404). The README's "full raw capture
   preserved" does not hold for this period.

## Checklist (STANDARD.md, Section 2)

| # | requirement | met? | where |
|---|---|---|---|
| 1 | targets committed before any result | yes | the same `TARGETS.csv` as route A (36e4575) |
| 2 | gaps decided before the run | yes, after route A results, before route B code | DECISIONS.md 18–29 (0a077b2) |
| 3 | authors asked | **not yet**: add the 07a failure to the draft issue | `AUTHOR_CONTACT.md` |
| 4 | exact sources | yes | `SOURCES.md` |
| 5 | identical on two machines | yes, and on two pandas versions | table above |
| 6 | every target reported | yes | table above |
| 7 | environment recorded | yes | `out_route_b*/ENVIRONMENT.json` |
| 8 | one command, outputs hashed | yes | `run_route_b.py`, `HASHES.txt` |
| 9 | unit tests | yes | `tests/test_route_b.py` |
| 10 | comparison only after the report | not started | — |
