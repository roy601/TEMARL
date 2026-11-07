# Corrections to DEEP_AUDIT.md

`DEEP_AUDIT.md` is the unedited output of `deep_audit.py` (commit 6781b46), run on
2026-10-25 over the 37 downloaded archives. It is kept as produced. **Its inventory is
correct; two of its three verdict statements, and its size and line totals, are not.**
This note records what is wrong, the evidence, and what to use instead.

Every number below was re-measured on 2026-11-03 from `FULL_INVENTORY.csv` (written by the
same run, not in git because it is 103.6 MB) and from `deep_audit.py`.

## What stands

| Claim in DEEP_AUDIT.md | Status |
|---|---|
| 37 archives, 549,625 entries (406,915 files, 142,710 directories) | **correct** |
| 49.45 GB uncompressed, 7.27 GB compressed | **correct** as stored totals; but see correction 3 |
| 6,157 distinct kinds of file, each with examples in FILE_CLASSES.md | **correct** |
| Hosts and the number of archives each appears in (Pass 2) | **correct** |
| attackmate.json in the scenario archives has only the keys `start-datetime`, `type`, `cmd`, `parameters` | **correct**, and consistent with `PROVENANCE.md` §2 |

## Correction 1: "NO technique label in ANY record of ANY run. Confirmed by full read, not by sampling."

> **Partly wrong; see Correction 5.** attackmate.json does carry technique labels.

**This is true of attackmate.json only. It is false of the dataset.**

- **The labels exist, in two places:**
  - `attack-manifestations-interpretation-main/attack_times.csv`: 904 labelled events. It is
    the label source `extract_camlds.py` uses (904 rows in, 904 out).
  - The `techniques/` folders of `manifestations_filtered.zip` and `manifestations_raw.zip`:
    97 technique IDs across 34 scenario runs.
- **The check looked only at key names.** `deep_audit.py:486` searches the record *keys* for
  "techniq|tactic|mitre|label". It never reads the values of `cmd` or `parameters`.
- **"Full read" overstates it.** `deep_audit.py:377` reads the *first* attackmate.json in each
  archive. That covers every scenario run (one file each). But the two manifestation
  archives hold **5,520** attackmate.json files, and only 1 was read from each.

**Use instead:** "The labels in attack_times.csv are generated from `parameters.metadata` in
attackmate.json." (Replaced 2026-11-07. The earlier wording here was wrong; see Correction 5.)

## Correction 2: "facts.json describes the ATTACKER host, so it cannot identify targets."

**This sentence was never tested. It is printed unconditionally.**

- `deep_audit.py:490` prints it as a fixed string.
- The code meant to check it (`deep_audit.py:412–417`) looks only in `zips[:1]`, the first
  archive. That is the analysis repository's ZIP, which contains no facts.json, so the section
  printed nothing (see the empty "attacker/facts.json — what it describes" in Pass 4).
- **facts.json exists for every host, not only the attacker:** 183 files, namely wazuh 34,
  inetfw 34, attacker 34, corpdns 34, videoserver 26, linuxshare 7, reposerver 7, client 5,
  adminpc 1, docker 1.

**Use instead:** "facts.json exists for every host (183 files). Whether the target hosts'
files identify targets has not been checked." Nothing in the current pipeline reads facts.json.

## Correction 3: the totals count the same data several times

**Only 26,173 of the 406,915 files have distinct content** (by CRC-32 and size). Together they
are **21.82 GB of the 49.45 GB**. The rest repeats:

- **Manifestation archives:** every file under `steps/` is identical to a file under
  `techniques/` (4,637 of 4,637 in filtered, 13,026 of 13,026 in raw). Most of `sequences/`
  repeats them too (2,853 of 3,418; 7,349 of 9,068). They are three indexings of the same
  extracted logs.
- **Configuration snapshots:** the same system files recur across hosts and scenarios. The
  seven vim names in `/etc/alternatives` (vim, vi, view, ex, rvim, rview, vimdiff) are 1,281
  files and 4.90 GB, but only **5 distinct binaries**.

**Use instead:** "49.45 GB as stored, about 21.8 GB of distinct content". Never add the
manifestation archives' sizes or line counts to the scenario archives'.

## Correction 4: "TOTAL LINES: 213,373,457" is not a measure of log data

Pass 5 skips a file only if its extension is in `BINARY_EXT` (`deep_audit.py:58`). Files
without such an extension were "line-counted" even when binary:

- the vim binaries (2,266,314 "lines" per name);
- systemd journals (`system.journal`, 4,347,642 "lines");
- dictionary word lists, CA certificates, Suricata rules and Filebeat field definitions.

The total also includes the duplication of correction 3.

**Use instead:** no corpus-wide line count. If log volume is needed, count named log files
(for example `audit.log`, `eve.json`) in the scenario archives only.

## Minor

- In the Pass 3 and Pass 5 tables, kinds of file are truncated to 56–60 characters, so several
  different `MANIFEST/techniques/.../logs/l…` rows look identical. FILE_CLASSES.md has the full
  names.
- FILE_CLASSES.md has 16,754 examples against 17,182 expected (3 per kind, fewer for kinds
  with fewer files). The 428 missing are most likely skipped empty files; this has not been
  confirmed.

## Two corrections to my own earlier review of this audit

Earlier statements in the review that prompted this note, now re-measured and superseded:

1. "The same 3.17 MB vim binary is stored 1,281 times." **Wrong.** The 1,281 files are 5
   distinct binaries (4.90 GB). Only one archive's files had been compared.
2. "5,554 attackmate.json files in the manifestation archives." **Wrong.** 5,554 is the total
   over all archives; the manifestation archives hold 5,520.

## Correction 5 (2026-11-07): attackmate.json does carry labels

Found by reading all 1,806 records (`out/ATTACKMATE_RECONCILE.txt`, from `reconcile_attackmate.py`).

- **The wrong claim.** `DEEP_AUDIT.md`, Correction 1 above and `PROVENANCE.md` §2 all said
  attackmate.json has no technique labels. **907 records have them**, in
  `parameters.metadata.techniques`. Correction 1 noted that values were never read, and still
  repeated the conclusion. That was my error.
- **How they relate to the CSV.** 904 of the 907 are the 904 rows of attack_times.csv, with
  identical labels in the same order. The authors' `extract_attack_logs.py` generates the CSV
  from these records. The other 3 are `sleep` records (T1546), which that script folds into the
  previous step's time window. So the agreement shows correct copying, not independent proof
  that the labels are right.
- **Record count.** "1,808 records across 36 runs" in `DEEP_AUDIT.md` is wrong: it is **1,806
  across 34**. The audit also read one file from each of the 2 manifestation archives, which
  explains 36. The 2 extra records fit that, but were not measured separately.

## Effect on the thesis pipeline

**None.**

- `extract_camlds.py` reads `attack_times.csv`, the correct label source.
- attack_times.csv and attackmate.json hold the same labels, so the corpus does not change.
- No step uses facts.json, the totals or the line counts.

These corrections matter only where `DEEP_AUDIT.md` itself is cited.
