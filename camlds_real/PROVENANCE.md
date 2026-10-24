# CAM-LDS — provenance and extraction record

Everything here was verified against the files, not transcribed from a paper or
a description. Where something is carried over rather than verified, it says so.

Last verified: 2026-10-24.

---

## 1. Dataset version — FROZEN

**Version in use: v1.**

| | |
|---|---|
| Record | `10.5281/zenodo.18390561` |
| Published | 2026-01-27 |
| Files | 36 |
| Size | 7.41 GB |
| Licence | CC BY 4.0 |

A **newer version exists** and is deliberately not used: `10.5281/zenodo.18861762`
(2026-03-04), which adds `runc init` audit events to Scenario 7. Switching
versions changes Scenario 7 and nothing else, so it must not be done silently.

### Integrity

All 36 archives were MD5-checked against the published values. **35 matched
both versions byte-for-byte; 1 pins the version:**

| File | Disk | v1 (18390561) | v2 (18861762) |
|---|---|---|---|
| `manifestations_filtered.zip` | 213,728,643 / `e9d17ad99897b952abddb25838a56a7b` | **identical** | 213,771,977 / `cfc14140b2e396a60989b8379eafca1f` |

This file is the only one that differs between versions, which is exactly what
v2's release note says it changed. An earlier check that compared only against
v2 reported this as corruption; it is not. **No archive is damaged.**

The 182 GB packet-capture record (`10.5281/zenodo.18701095`) is **not used** —
packets feed nothing the models read.

## 2. Labels

| | |
|---|---|
| Source | `attack_times.csv` |
| From | `github.com/ait-aecid/attack-manifestations-interpretation` |
| Licence | code GPL-3.0, data CC BY 4.0 |
| Rows | 904 |

> **Repository commit: NOT YET RECORDED.** The analysis repo was downloaded as
> a GitHub ZIP rather than cloned, so no commit hash was captured. Record it
> before any confirmatory run.

`attackmate.json` inside the scenario archives is **not** a label source. Across
all 34 runs and 1,806 records it carries exactly four keys — `start-datetime`,
`type`, `cmd`, `parameters` — with **no technique label and no execution
outcome**. `parameters` holds playbook configuration written *before* the run
(`exit_on_error`, `error_if`, `loop_count`), so success and failure are not
recoverable from it. It is useful only for untruncated command text and for the
setup/sleep steps `attack_times.csv` omits.

## 3. Extraction rules

Produced by `extract_camlds.py`. Every rule is forced by a measurement.

**D1 — order is the `start` timestamp.**
`event_id` is a playbook step *identifier*, not an execution index: it is
non-monotonic in **27 of 34 runs**, and sorting by it breaks timestamp order in
**28 of 34**. CSV row order is closer but still wrong in 4 runs (the scenario-6
variants, 2 positions each). This matters more than usual because the research
question is whether order carries signal.

Integrity of that key: **0 duplicate start timestamps** within any run, and
**1** step across the whole corpus that starts before its predecessor ends.

**D2 — all 904 rows kept.**
904 rows span 883 distinct `(run, event_id)` keys. All 18 repeated keys have
fully distinct timestamps, with gaps of 16–60 s, so each repetition genuinely
executed. Keying on `(run, event_id)` would drop 21 rows silently. Each row
carries an `occurrence` index; **nothing is merged**.

**D3 — vocabulary rebuilt from the release.** 97 sub-techniques collapsing to
81 parent. Both forms are emitted. The prior 84-label vocabulary is not imposed.

**D4 — zones and goals are carried, not derived.** See §5.

**D5 — no windows, no splits, no collapsing.** Modelling choices live downstream.

### Reconciliation

| | |
|---|---|
| Source rows | 904 |
| Emitted steps | 904 |
| Dropped | 0 |
| Merged | 0 |
| **Lossless** | **yes** |

Every step carries `source_row`, its line index in `attack_times.csv`.

Totals: 34 runs, 1,351 technique instances, 203 multi-technique steps (22.5%).

## 4. Relationship to our earlier corpus

Our previous corpus was parsed independently from the AttackBed playbooks
(`github.com/ait-testbed/attackbed`, commit `4d43354`). It is **not** the same
as the release, and the difference is in ordering:

| | Released | Ours |
|---|---|---|
| Runs | 34 | 36 |
| Steps | 904 | 889 |
| Technique instances | 1,351 | 1,347 |

Aligning by content (names do not correspond — ours are `scenario_1_a_a.j2`,
the release says `1_autostart_localaccount`):

- **5 of 34** runs are order-identical
- **23** have identical technique *sets* in a different order or multiplicity
- **6** differ genuinely (J 0.90–0.95)

Matching totals is **not** sequence agreement, and an earlier claim that the two
"agree to within ~2%" was about totals only.

The two extra playbooks are `scenario_3_a_b.j2` and `scenario_3_b_b.j2` — our S3
has 8 playbooks, the release has 6 S3 runs. The variant mapping recovered from
content is **not alphabetical**: `autostart↔c`, `cron↔e`, `pwnkit↔a`,
`racecondition↔d`, `sudo↔b`, `validaccount↔f`; `localaccount↔b`, `pam↔c`,
`sshkey↔a`.

## 5. Zones and goals — carried, NOT derived

| Scenario | Entry | Target | Target host | Goal |
|---|---|---|---|---|
| S1 | Internet | DMZ | VideoServer | Persistence |
| S2 | DMZ | DMZ | VideoServer | Exfiltration |
| S3 | Internet | LAN | FileShare | Impact |
| S4 | DMZ | Firewall | Firewall | Network Boundary Bridging |
| S5 | LAN | DMZ | VideoServer | Credential Access |
| S6 | User | User | Client | Exfiltration |
| S7 | Internet | DMZ | DockerServer | Credential Access / Exfiltration |

**Source: hand-typed from the CAM-LDS paper (Sec. 3.4, Figs. 5–11). Not derived
from the release.**

Two derivation routes were attempted and both failed:

1. **Host folders** in `manifestations_filtered/steps/…` — 2 of 7 matched. The
   path is ordered by first appearance of a host that *wrote a log*, not by
   attack progression. `corpdns` leads nearly every run because step 1 is a DNS
   lookup; `inetfw` appears because traffic crosses the firewall.
2. **Hostnames in command text** — only 121 of 904 commands (13.4%) name a host,
   and the last one is almost always `192.42.1.174`, the attacker's own address.

**Log volume is corroborating evidence only.** Excluding infrastructure, the
heaviest-logging host agrees with the hand-typed `target_host` in most
scenarios, but volume is confounded by per-service logging verbosity (a web
server under `nikto`/`ffuf` logs thousands of requests regardless of whether it
is the objective) and by collection settings. **Agreement with an existing
annotation does not independently validate that annotation.**

> **Open: S4.** Its target is `Firewall`, which fails every derivation route and
> is not one of the five defended zones. It needs checking against the paper's
> topology directly, which is not machine-verifiable here.

## 6. Measured structure — read before choosing a split

### Balance

| Scenario | Runs | Steps | Share |
|---|---|---|---|
| S1 | 18 | 522 | 57.7% |
| S3 | 6 | 160 | 17.7% |
| S6 | 5 | 137 | 15.2% |
| S2 | 2 | 47 | 5.2% |
| S4 | 1 | 22 | 2.4% |
| S7 | 1 | 13 | 1.4% |
| S5 | 1 | 3 | 0.3% |

### Similarity — technique-set Jaccard over parent techniques

**Within a base scenario** (what a *variant*-held-out split tests):

| Scenario | Variants | Jaccard mean (min–max) | Order-identical pairs |
|---|---|---|---|
| S1 | 18 | **0.858** (0.800–0.931) | **0 / 153** |
| S2 | 2 | 0.750 | 0 / 1 |
| S3 | 6 | 0.687 (0.500–0.842) | 0 / 15 |
| S6 | 5 | 0.515 (0.067–0.923) | 0 / 10 |

**Across base scenarios** (what a *scenario*-held-out split tests):

| | |
|---|---|
| 21 pairs | Jaccard mean **0.110**, max 0.267, min 0.000 |

**The two splits differ by roughly 8× in overlap, so they answer different
questions:**

- **Variant-held-out** → "a new variant of a known campaign." Legitimate, and
  not trivial: *no* pair of variants is order-identical, so the sequences are
  not duplicates. But they share ~86% of their technique vocabulary in S1.
- **Scenario-held-out** → "an unseen campaign." Only this supports a
  generalisation claim about new attacks.

Note these are **technique-set** Jaccards. Earlier project records quote
*bigram* Jaccard (0.900 within-scenario, 0.011 cross-scenario), which is a
different quantity on the old corpus — do not compare the two directly.

S4, S5 and S7 have a single run each, so they can only ever be held out whole.

## 7. Standing limitation

**34 runs from 7 scenarios is limited independent diversity, and correct
extraction does not change that.** One scenario is 58% of the corpus. Three
scenarios have a single run. Everything here improves the validity of what is
measured; none of it adds campaigns.

## 8. Not yet done

- [ ] Record the analysis-repo commit hash (downloaded as a ZIP, so unknown)
- [ ] Verify the S4 `Firewall` zone against the paper's topology
- [ ] Freeze the split protocol, including validation selection
- [ ] Report unseen test labels once the split exists
