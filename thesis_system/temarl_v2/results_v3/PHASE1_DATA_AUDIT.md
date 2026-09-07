# Phase 1 — CAM-LDS Dataset Selection and Line-by-Line Audit

Date: 2026-09-07. Method: an **independent second parser** (block-structure walk)
was written and cross-checked against the production parser
(`parse_attackbed.py`). Disagreements were resolved by reading the raw playbook
lines, not by trusting either implementation.

**Headline: the audit found three real parser defects that were silently
dropping labelled data, and one claim in the prior write-up must be withdrawn.**

---

## 1. Defects found and fixed

All three caused the production parser to **silently drop real, labelled attack
steps** — no warning, no error.

| # | Defect | Evidence | Lost |
|---|---|---|---|
| A | `tactics:` appears **before** `techniques:` in a metadata block. The old sequential state machine armed on `techniques:` and emitted on `tactics:`, so a block in the other order emitted nothing. | `scenario_7.j2` L93–95 | T1190, T1059.004, **T1095** |
| B | Inline `#` comment after a quoted `tactics:` value broke the anchored regex, so the emit never fired. | `scenario_6_a_a.j2` L238 | 1 × T1222.002 |
| C | Same inline-comment problem on `techniques:`. | `scenario_6_b_a.j2`, `scenario_6_b_b.j2` L326, L344 | 4 × T1219 |

**Fix:** `parse_playbook()` was rewritten to be **block-aware** (collect all keys
in a `metadata:` block, then emit) with a quote-aware `_value()` extractor that
takes the quoted span when present and otherwise truncates at an unquoted `#`.

**Recovered: 8 technique instances and 1 parent technique.**

Both parsers now agree exactly: 1,347 instances, 36 runs, 0 files differing.

### Consequence: T1095 is vindicated

The prior write-up recorded T1095 as *"invented by the hand reconstruction"*.
That was wrong — it is present at `scenario_7.j2:95` and was dropped by defect A.
**Reconstruction precision is therefore 100.0%** (was reported as 98.7%), recall
92.7%.

---

## 2. A claim that must be withdrawn

The prior write-up stated that the parse yields *"81 techniques and 13 tactics,
matching the CAM-LDS paper's Table 3 exactly"* and treated that as independent
confirmation of correctness.

**That agreement was an artefact of the parser bugs.** With the bugs fixed:

| | Corrected parse | Paper Table 3 |
|---|---|---|
| Parent techniques | **82** | 81 |
| Tactics | **13** | 13 |
| Simulations | **36** | 34 |

The tactic count still matches. The technique count does not, and the run count
never did — the repository ships more scenario-3 variants than the paper's 34
simulations, so a small excess is expected. **The "matches exactly" claim is not
usable and has been withdrawn.** The defensible statement is: *the tactic
inventory matches the paper; the technique count is 82 against the paper's 81,
consistent with the repository shipping 36 variants against the paper's 34.*

---

## 3. Corrected corpus statistics

Every figure below supersedes the previously documented value.

| Statistic | Corrected | Previously stated |
|---|---|---|
| Labelled technique instances | **1,347** | 1,339 |
| Runs / campaigns | 36 / 7 | 36 / 7 |
| Parent techniques | **82** | 81 |
| With sub-techniques | **99** | 98 |
| Tactics | 13 | 13 |
| Self-loop rate | **21.2%** | 18.6% |
| Majority baseline | **0.107** | 0.108 |
| Within-scenario Jaccard | **0.809** | 0.871 |
| Across-scenario Jaccard | **0.109** | 0.078 |
| Within/across ratio | **7.4×** | 10.4× |
| UNK against the 84-technique vocabulary | **0 (0.00%)** | 0 |

### Information-theoretic ceiling (new)

```
H(next)            = 5.496 bits
H(next | current)  = 1.491 bits
predictable info   = 4.006 bits  = 72.9% of H(next)
```

This matters: **72.9% of the next-technique uncertainty is resolvable from the
current technique alone.** The task is genuinely learnable — a model that fails
here is not defeated by an unpredictable corpus.

### Effective sample size (new, and the binding constraint)

| Scenario | Runs | Steps | Distinct sequences |
|---|---|---|---|
| S1 | 18 | 822 | 18 |
| S2 | 2 | 64 | 2 |
| S3 | 8 | 217 | 8 |
| S4 | 1 | 27 | 1 |
| S5 | 1 | 5 | 1 |
| S6 | 5 | 189 | 5 |
| S7 | 1 | 23 | 1 |
| **Total** | **36** | **1,347** | **36** |

**Kish effective n over campaigns = 3.09.** Nominally 36 runs, but the campaigns
are so unevenly sized that the effective independent sample is around **three**.
This is the single most important number for experiment design: any protocol
whose unit of independence is the campaign has n ≈ 3, and leave-one-scenario-out
cannot support an inferential claim.

---

## 4. Option A vs Option B — determination

**Prior claim (mine): "the log dataset adds instances, not sequences; the
playbooks are the generator, so Option B adds nothing the encoder can use."**

**That claim was too strong and is corrected here.** Three verifiable mechanisms
make executed order differ from file order:

| Mechanism | Count | Effect |
|---|---|---|
| `- type: include` → `upgrade.yml` | **12 of 36 runs** (8 × S3, 4 × S6) | **`upgrade.yml` is NOT shipped in the repository** (confirmed by exhaustive search). Whatever steps it contributes are missing from our corpus entirely. |
| `- type: loop` with `break_if` | 4 runs (S3 b-variants) | A VNC password-guessing loop over `LISTA` that breaks on success. Repetition count is data-dependent and **unknowable from the file**; our parse counts the body once. |
| `background: True` | 17 runs | Concurrent commands, so true temporal interleaving is not the file order. |

Against that, there are **0** conditional constructs (`when:`, `only_if:`,
`error_if:`, `condition:`), so no step is skipped on a branch.

### Verdict

- **Option B *would* add real information**: the missing `upgrade.yml` steps
  (affecting a third of the corpus), true loop repetition counts, and genuine
  temporal ordering for background commands.
- **Option B would *not* add campaign diversity.** The generator is still 7
  campaigns; the Kish effective n of ≈3 does not improve. The binding constraint
  on generalisation is unchanged.

**Decision: proceed with Option A (playbooks) for this work, and disclose the
gap.** Justification: the diversity ceiling — which is what actually limits every
result we have — is identical under both options, while Option B costs a
multi-GB download plus a log-to-technique alignment pipeline that would itself
need validating. The `upgrade.yml` gap is disclosed as a limitation rather than
silently carried.

**This decision is revisited if, and only if, Phase 2 shows the models are
data-limited in a way more instances of the same 7 campaigns would relieve.**

---

## 5. Preprocessing choices (declared, not optimised)

Two defensible options existed; neither was chosen by looking at model
performance.

1. **scenario-5 duplicate.** `scenario_5.j2` and `scenario_5.j2.yml` are the same
   playbook (byte-different comments, **identical** technique sequences —
   verified). Deduped to 1 run, matching the paper's Table 2 count for S5.
2. **Technique/tactic list-length mismatch.** 37 metadata blocks list more
   tactics than techniques (e.g. `T1105,T1098.004` with three tactics, because
   T1098.004 is both Persistence and Privilege Escalation). Assignment is
   positional with first-tactic fallback. This is a **documented heuristic**, not
   a tuned choice; it affects the auxiliary tactic label only, never the
   technique sequence the encoder consumes.

---

## 6. Validation state after the correction

- CAM-LDS UNK against the 84-technique vocabulary: **0 / 1,347 (0.00%)**
- `NUM_TECHNIQUES` unchanged at 84 (T1095 was already id 41 via the
  reconstruction, so no vocabulary change was needed)
- **All 10 gate modules pass**, including `env_entity` EXACT EQUIVALENCE
  (0 mismatches) and `tests_entity` 26/26
- `payoff_frozen.json` untouched; rows 0–77 still bit-identical

## 7. Carried-forward limitations

1. `upgrade.yml` content is missing for 12 of 36 runs.
2. Loop repetition counts are unknowable from the playbooks (4 runs).
3. True temporal interleaving of 38 background commands is not recoverable.
4. **The attacker profiles in `env_v2` are still built from the older hand
   reconstruction** (`camlds_grounding.json`), not from this corrected file —
   the two use incompatible schemas. Every DSR number to date rests on the
   reconstruction-derived attacker.
