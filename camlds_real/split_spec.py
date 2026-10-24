# -*- coding: utf-8 -*-
"""FROZEN split protocol for the CAM-LDS corpus.

Pre-registration. Committed BEFORE any confirmatory run, so the folds, the
exclusions, the metrics and the reporting rules cannot be chosen after seeing
results. Changing anything here means a new PROTOCOL_VERSION and a new commit,
never an edit in place.

Everything below is forced by a measurement on the extracted corpus
(camlds_real/out/steps.jsonl, 904 steps, 34 runs, 7 scenarios). The measurements
are reproduced in the docstrings so the reasoning travels with the rule.

────────────────────────────────────────────────────────────────────────────
THE MEASUREMENT THAT SHAPES EVERYTHING
────────────────────────────────────────────────────────────────────────────

Holding out a whole scenario, how many test technique instances carry a label
that NEVER appears in training?

    fold   test  train   unseen instances        verdict
    S1      522    382   237/819  (28.9%)   train < test  -> EXCLUDED
    S2       47    857    14/64   (21.9%)   usable
    S3      160    744    64/204  (31.4%)   usable
    S4       22    882     5/27   (18.5%)   test too small -> EXCLUDED
    S5        3    901     3/5    (60.0%)   test too small -> EXCLUDED
    S6      137    767   117/199  (58.8%)   usable, severe ceiling
    S7       13    891     5/23   (21.7%)   test too small -> EXCLUDED

An unseen label cannot be predicted by a classifier that never saw it, so the
unseen rate is a CEILING ON RECALL, not a model failure. On S6 the ceiling is
41.2%. Reporting micro-F1 on such a fold without stating the ceiling would be
misleading, so R3 below makes it mandatory.

By contrast, holding out one VARIANT within a scenario:

    scenario  runs  mean test  mean train  unseen instances
    S1          18       29.0      493.0        0.0%
    S3           6       26.7      133.3        1.1%
    S6           5       27.4      109.6       14.3%
    S2           2       23.5       23.5       13.4%

Healthy ratios and almost no unseen-label problem. This is a different and
easier question, which is exactly why it cannot carry the generalisation claim.
"""

from __future__ import annotations

import collections
import json
import os

PROTOCOL_VERSION = "1.0"
FROZEN_ON = "2026-10-24"
CORPUS = "camlds_real/out/steps.jsonl"
CORPUS_FACTS = {"steps": 904, "runs": 34, "scenarios": 7,
                "technique_instances": 1351, "parent_techniques": 81}

# ── S1 ─ the two families, and what each is allowed to claim ────────────────

FAMILY_PRIMARY = "variant_held_out"
FAMILY_SECONDARY = "scenario_held_out"

CLAIMS = {
    "variant_held_out":
        "Performance on a NEW VARIANT OF A KNOWN CAMPAIGN. Within-scenario "
        "technique-set Jaccard is 0.858 (S1), so train and test share most of "
        "their vocabulary. This is a legitimate question and NOT leakage -- 0 "
        "of 153 S1 variant pairs are order-identical, so the sequences are not "
        "duplicates -- but it must never be reported as generalisation to "
        "unseen attacks.",
    "scenario_held_out":
        "Performance on an UNSEEN CAMPAIGN. Cross-scenario Jaccard is 0.110, "
        "about 8x lower than within-scenario. ONLY this family supports a "
        "generalisation claim.",
}

# ── S2 ─ exclusions, each with the number that forces it ────────────────────

SCENARIO_HELD_OUT_EXCLUDED = {
    "1": "train (382 steps) < test (522 steps). A fold that trains on 42% of "
         "the corpus to predict the other 58% does not measure generalisation.",
    "4": "test n = 22 steps.",
    "5": "test n = 3 steps.",
    "7": "test n = 13 steps.",
}
MIN_TEST_STEPS = 25          # S4=22, S5=3, S7=13 fall below; S2=47 passes
MIN_TRAIN_OVER_TEST = 1.5    # train must be at least 1.5x test

SCENARIO_HELD_OUT_FOLDS = ("2", "3", "6")

# Excluded scenarios are NOT discarded -- they stay in training for every fold.
# They are 38 steps, 4.2% of the corpus.
ALWAYS_TRAIN_ONLY = ("4", "5", "7")

VARIANT_HELD_OUT_SCENARIOS = ("1", "3", "6", "2")   # every scenario with >= 2 runs

# ── S3 ─ reporting rules ────────────────────────────────────────────────────

REPORTING = {
    "R1": "Report BOTH families, always labelled with the claim from CLAIMS. "
          "Never present a variant-held-out number as generalisation.",
    "R2": "Report per-fold n (test steps, test technique instances). A mean "
          "over folds of wildly different size hides which fold drove it.",
    "R3": "MANDATORY: report the unseen-label CEILING beside every "
          "scenario-held-out metric -- the share of test technique instances "
          "whose label never appears in that fold's training set. Recall "
          "cannot exceed 1 - that rate.",
    "R4": "Report metrics BOTH raw and ceiling-adjusted (restricted to test "
          "instances whose label was seen in training). The gap between them "
          "is the cost of unseen labels, and is itself a finding.",
    "R5": "Primary metric: micro-F1 over parent techniques. Secondary: "
          "exact-set accuracy, macro-F1. Macro-F1 is fragile here -- 10 of 81 "
          "parent techniques appear exactly once in the whole corpus -- so it "
          "is reported, never relied on.",
    "R6": "State the label-frequency skew once: T1059 alone is 234 of 1,351 "
          "technique instances (17.3%), and 18 of 81 parent techniques appear "
          "3 times or fewer.",
}

# ── S4 ─ validation, repeats, and the decisions that must not drift ─────────

VALIDATION = (
    "Model selection uses ONE RUN PER TRAINING SCENARIO that has >= 2 runs, "
    "taken in sorted order so the choice is deterministic and seed-independent. "
    "Spanning the scenarios matters: taking simply the first training run would "
    "put every validation step in S1, which is 58% of the corpus, so a fold "
    "testing S6 would select its checkpoint on a distribution unlike its test "
    "set. A scenario with a single run contributes nothing to validation, "
    "because removing its only run would delete that scenario from training. "
    "The test scenario is never touched during selection, and no hyperparameter "
    "is tuned per arm."
)

REPEAT_HANDLING = {
    "main": "KEEP repeated executions as separate steps. They are recorded "
            "sequence: all 18 repeated (run, event_id) keys have distinct "
            "timestamps with 16-60s gaps, so each really executed. Collapsing "
            "them would change the prediction task.",
    "sensitivity": "collapse_repeats -- a SEPARATE condition reported beside "
                   "the main result, never substituted for it.",
}

ORDERING = (
    "Steps are ordered by ascending `start` timestamp. NEVER by event_id, "
    "which is a playbook step identifier: it is non-monotonic in 27 of 34 runs "
    "and sorting by it breaks timestamp order in 28 of 34. Verified: 0 "
    "duplicate start timestamps within any run; 1 step corpus-wide starts "
    "before its predecessor ends, and that case is left in place rather than "
    "reordered."
)

LABEL_SPACE = (
    "Parent techniques (81). Sub-techniques (97) are retained in the corpus "
    "and may be used in a separate condition, but the headline label space is "
    "fixed to parent here so it cannot be chosen after seeing results."
)

WINDOWS = (
    "Windows are built WITHIN a run and never cross a run boundary. Left-"
    "padded. W = 16 primary; 8 / 32 / 64 as the window study."
)


# ── fold construction ───────────────────────────────────────────────────────

def load(repo: str) -> list[dict]:
    p = os.path.join(repo, *CORPUS.split("/"))
    return [json.loads(l) for l in open(p, encoding="utf-8")]


def folds(steps: list[dict], family: str) -> list[dict]:
    """Enumerate the frozen folds. No randomness, no seed."""
    out = []
    if family == FAMILY_SECONDARY:
        for b in SCENARIO_HELD_OUT_FOLDS:
            te = [s for s in steps if s["base_scenario"] == b]
            tr = [s for s in steps if s["base_scenario"] != b]
            out.append({"family": family, "fold": f"S{b}", "test": te, "train": tr})
    elif family == FAMILY_PRIMARY:
        for b in VARIANT_HELD_OUT_SCENARIOS:
            runs = sorted({s["run"] for s in steps if s["base_scenario"] == b})
            for r in runs:
                te = [s for s in steps if s["run"] == r]
                tr = [s for s in steps
                      if s["base_scenario"] == b and s["run"] != r]
                out.append({"family": family, "fold": r, "test": te, "train": tr})
    else:
        raise ValueError(family)
    return out


def ceiling(fold: dict, key: str = "techniques_parent") -> dict:
    """R3: the unseen-label ceiling on recall for one fold."""
    seen = {t for s in fold["train"] for t in s[key]}
    inst = [t for s in fold["test"] for t in s[key]]
    unseen = [t for t in inst if t not in seen]
    return {
        "test_steps": len(fold["test"]),
        "train_steps": len(fold["train"]),
        "test_instances": len(inst),
        "unseen_instances": len(unseen),
        "unseen_rate": (len(unseen) / len(inst)) if inst else 0.0,
        "max_recall": 1 - (len(unseen) / len(inst)) if inst else 1.0,
        "unseen_labels": sorted(set(unseen)),
    }


def validation_runs(fold: dict) -> list[str]:
    """Deterministic: first run, in sorted order, of each training scenario
    that has >= 2 runs. See VALIDATION for why it spans scenarios."""
    by_sc: dict[str, set[str]] = collections.defaultdict(set)
    for s in fold["train"]:
        by_sc[s["base_scenario"]].add(s["run"])
    return sorted(sorted(rs)[0] for rs in by_sc.values() if len(rs) >= 2)


def split_train_val(fold: dict) -> tuple[list[dict], list[dict]]:
    """Apply VALIDATION to one fold. Test is untouched."""
    val = set(validation_runs(fold))
    tr = [s for s in fold["train"] if s["run"] not in val]
    va = [s for s in fold["train"] if s["run"] in val]
    return tr, va


def _main() -> int:
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    steps = load(repo)
    n = len(steps)
    print(f"FROZEN SPLIT PROTOCOL v{PROTOCOL_VERSION}  (frozen {FROZEN_ON})")
    print(f"corpus: {n} steps, {len({s['run'] for s in steps})} runs, "
          f"{len({s['base_scenario'] for s in steps})} scenarios")
    assert n == CORPUS_FACTS["steps"], f"corpus changed: {n} != {CORPUS_FACTS['steps']}"

    print()
    print("=" * 76)
    print(f"SECONDARY FAMILY — {FAMILY_SECONDARY}  (carries the generalisation claim)")
    print("=" * 76)
    print(f"  {'fold':<6} {'test':>6} {'train':>6} {'val':>5} {'inst':>6} "
          f"{'unseen':>8} {'ceiling':>9}  validation runs")
    for f in folds(steps, FAMILY_SECONDARY):
        c = ceiling(f)
        tr, va = split_train_val(f)
        vr = validation_runs(f)
        print(f"  {f['fold']:<6} {c['test_steps']:>6} {len(tr):>6} {len(va):>5} "
              f"{c['test_instances']:>6} {c['unseen_rate']:>7.1%} "
              f"{c['max_recall']:>8.1%}  {', '.join(vr)}")
    print()
    print("  EXCLUDED from this family (still used for training):")
    for b, why in SCENARIO_HELD_OUT_EXCLUDED.items():
        print(f"    S{b}: {why}")

    print()
    print("=" * 76)
    print(f"PRIMARY FAMILY — {FAMILY_PRIMARY}  (a different, easier question)")
    print("=" * 76)
    fs = folds(steps, FAMILY_PRIMARY)
    by = collections.defaultdict(list)
    for f in fs:
        by[f["fold"].split("_")[0]].append(ceiling(f))
    print(f"  {'scenario':<9} {'folds':>6} {'mean test':>10} {'mean train':>11} "
          f"{'mean unseen':>12}")
    for b in VARIANT_HELD_OUT_SCENARIOS:
        cs = by[b]
        print(f"  S{b:<8} {len(cs):>6} {sum(c['test_steps'] for c in cs)/len(cs):>10.1f} "
              f"{sum(c['train_steps'] for c in cs)/len(cs):>11.1f} "
              f"{sum(c['unseen_rate'] for c in cs)/len(cs):>11.1%}")
    print(f"\n  total folds: {len(fs)}")

    print()
    print("=" * 76)
    print("FROZEN DECISIONS")
    print("=" * 76)
    print(f"  ordering   : {ORDERING}")
    print(f"  labels     : {LABEL_SPACE}")
    print(f"  windows    : {WINDOWS}")
    print(f"  validation : {VALIDATION}")
    print(f"  repeats    : {REPEAT_HANDLING['main']}")
    print(f"  sensitivity: {REPEAT_HANDLING['sensitivity']}")
    print()
    for k in sorted(REPORTING):
        print(f"  {k}: {REPORTING[k]}")
    print()
    print("  Changing any of the above requires a new PROTOCOL_VERSION and a")
    print("  new commit. Never edit this file in place after a run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
