# -*- coding: utf-8 -*-
"""FROZEN protocol for Idea 01: TEMARL's prediction module vs an adapted Kuwano baseline.

Pre-registration. Frozen and committed BEFORE any result is computed on test data. The
reasoning for every constant is in PROTOCOL.md (frozen as v0.3 there, version 1.0 here).
Changing anything below means a new PROTOCOL_VERSION and a new commit, never an edit in
place.

    python idea01_kuwano/spec.py      # re-checks every measured fact this protocol relies on

The self-check reads inputs and corpus labels only. It never touches a model output.
"""
from __future__ import annotations

import collections
import hashlib
import os
import sys
from fractions import Fraction

PROTOCOL_VERSION = "1.0"
FROZEN_ON = "2026-11-03"
PROTOCOL_DOC = "idea01_kuwano/PROTOCOL.md (draft v0.3, frozen as 1.0)"
TITLE = "Comparison of TEMARL's prediction module with an adapted Kuwano baseline"

# ── inputs, pinned. SHA-256 after normalising CRLF to LF, so a git checkout on any OS
#    gives the same value ─────────────────────────────────────────────────────────
INPUTS = {
    "camlds_real/out/steps.jsonl":
        "2d0886115d8082ef9dba5d2d001cd65f241ef5a84e4c0bf16d173e71fa0bff42",
    "kuwano_repro/data/derived/matrix_v11.0.csv":
        "9e81ad014faa190c3737647e669da047cb2b692214958127e2e54b86580edec0",
    "kuwano_repro/data/derived/groups_v11.0.csv":
        "211f31dae8f15bfed27acfbd72a0a08461d56f40fd3c7bfa4cb3c13e2abe0371",
    "kuwano_repro/data/derived/techniques_v11.0.csv":
        "f12314c0a969a5b5450fe0e95dd3e43e9109c6948d1c1d374d02e789d961a983",
}

# ── S2 · splits: the frozen split protocol v1.0, with one declared exclusion ─────
SPLIT_PROTOCOL = "camlds_real/split_spec.py"
SPLIT_PROTOCOL_VERSION = "1.0"
PRIMARY_FAMILY = "variant_held_out"
SECONDARY_FAMILY = "scenario_held_out"
EXCLUDED_VARIANT_FOLDS = {
    "2_cron": "S2 has 2 runs; holding one out leaves 1 training run and an EMPTY "
              "validation set, so no threshold, checkpoint or early stop can be selected.",
    "2_rootkit": "same as 2_cron.",
}
EXPECTED = {
    "variant_folds": 29, "variant_folds_by_scenario": {"1": 18, "3": 6, "6": 5},
    "variant_test_steps": 819, "variant_points": 790,
    "scenario_folds": ("S2", "S3", "S6"), "scenario_test_steps": 344, "scenario_points": 331,
}
CLAIM_PRIMARY = ("new variant of a known campaign; NOT generalisation to unseen scenarios "
                 "(within-scenario Jaccard 0.858 for S1)")
CLAIM_SECONDARY = "unseen campaign; 3 folds, descriptive only"

# ── S3/S4 · the task, identical for every model ─────────────────────────────────
WINDOW = 16                                # previous steps visible at a prediction point
WINDOW_SENSITIVITY = "full_history"        # Kuwano only: all previous steps of the run
LABEL_SPACE = "parent"                     # 81 parent techniques, from the corpus vocabulary
N_LABELS = 81
PREDICTION_POINTS = "every step of a test run except its first"
TARGET = "the set of parent techniques on that step"
OBSERVED_TECHNIQUES_ELIGIBLE = True        # 47.2% of target labels are already in the window
TACTIC_FILTER = False                      # it would drop 72.9% of target labels
REPEATS = "kept"                           # sensitivity: collapse_repeats

# ── S3.1 · our model: TEMARL's prediction module (the frozen encoder of the CTDE framework)
OUR_MODEL = "TEMARL prediction module: frozen command-level encoder inside MAPPO (CTDE)"
PRIMARY_ENCODER = "Transformer"
SECONDARY_ENCODERS = ("GRU", "LSTM")       # only if run; decided BEFORE any test result is opened
SEEDS = tuple(range(10))
OUR_THRESHOLD_GRID = (0.1, 0.2, 0.3, 0.4, 0.5)
THRESHOLD_RULE = "maximise validation micro-F1; ties take the smallest value; never on test"
CHECKPOINT_RULE = "validation-best (as Temarl_Test_v1_L1/study_spec.py)"

# ── S3.2 · the adapted Kuwano baseline ───────────────────────────────────────────
K = 60
PUBLISHED_THRESHOLD = Fraction(17, 100)
KUWANO_THRESHOLD_GRID = tuple(Fraction(x) for x in
                              ("0.05", "0.10", "0.17", "0.25", "0.35", "0.50", "0.75", "1.00", "1.50"))
ATTACK_VERSION = "11.0"
CONDITIONS = {
    "K-A-val": {"reference": "attack_v11.0_groups", "threshold": "validation", "tiebreak": "name"},
    "K-A-pub": {"reference": "attack_v11.0_groups", "threshold": "published", "tiebreak": "name"},
    "K-B-val": {"reference": "training_runs", "threshold": "validation", "tiebreak": "run_name"},
}
PRIMARY_COMPARATOR = "K-A-val"
KUWANO_FUNCTION = "kuwano_repro/kuwano.py::recommend_limit"   # similarity 1 -> limit rule
SIMILARITY_ONE_RULE = ("limit: each technique scored (n identical neighbours using it, "
                       "SupportRate of the rest), compared lexicographically; n > 0 is recommended")
OUTPUT_RESTRICTED_TO_LABEL_SPACE = True
UNSUPPORTED_BY_ATTACK_V11 = ("T1490", "T1525", "T1531", "T1599")   # no v11 group uses them
CONTEXT_BASELINES = ("repeat_previous", "label_prior")

# ── S6 · metrics, the same code for every model ─────────────────────────────────
METRIC_CODE = "Temarl_Test_v1_L1/metrics_cmd.py"
PRIMARY_METRIC = "micro_f1"
SECONDARY_METRICS = ("exact_set_accuracy", "macro_f1")
THRESHOLD_FREE_METRICS = ("precision_at_1", "recall_at_3", "recall_at_5")
CEILINGS = {"TEMARL": "unseen-label rate of the fold", "K-B-val": "unseen-label rate of the fold",
            "K-A": "share of test labels in UNSUPPORTED_BY_ATTACK_V11"}

# ── S7 · analysis ───────────────────────────────────────────────────────────────
PRIMARY_CONTRAST = ("per fold: TEMARL Transformer micro-F1 (mean over SEEDS) minus "
                    "K-A-val micro-F1, over the 29 variant folds")
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_SEED = 20261103
TEST = "Wilcoxon signed-rank, two-sided"
ALPHA = 0.05
OUTPERFORMS_RULE = "95% bootstrap CI of the mean difference excludes 0 AND p < ALPHA"
HOLM_FAMILY = ("Transformer vs K-A-val", "Transformer vs K-A-pub", "Transformer vs K-B-val",
               "GRU vs K-A-val (if run)", "LSTM vs K-A-val (if run)")
SCENARIO_FAMILY = "descriptive only, per fold with ceilings; no significance test (n = 3)"
REPORT_PER_SCENARIO = ("1", "3", "6")      # beside the pooled result; S1 folds are not independent

# ── S8 · order of work and blinding ─────────────────────────────────────────────
ORDER_OF_WORK = (
    "1 freeze this file and commit it with the code it refers to",
    "2 implement Kuwano conditions and context baselines; tests pass; reproduction hashes unchanged",
    "3 run them; write per-fold outputs and SHA-256; DO NOT open test-split numbers",
    "4 port TEMARL's encoder pipeline to camlds_real (B2); freeze its configuration; record GRU/LSTM decision",
    "5 train and evaluate TEMARL; then open all test numbers together and apply S7",
)
PRECONDITIONS_OPEN = {
    "B1": "record the commit hash of the CAM-LDS analysis repository (camlds_real/PROVENANCE.md)",
    "B2": "port TEMARL's encoder pipeline to camlds_real (81 labels, these folds) and test it",
}

# ── measured facts, re-checked by _main() ───────────────────────────────────────
MEASURED = {
    "corpus_parent_labels_in_attack_v11": (81, 81),
    "parent_instances": 1341,
    "unsupported_instances": 15,
    "points_corpus_wide": 870,
    "target_instances": 1270,
    "target_instances_already_in_window": 600,
    "target_instances_dropped_by_tactic_filter": 926,
    "points_with_similarity_one_for_K_A": 4,
    "max_training_runs_per_fold": 29,
}


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def _main() -> int:
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path[:0] = [os.path.join(repo, "camlds_real"), os.path.join(repo, "kuwano_repro"),
                    os.path.join(repo, "Temarl_Test_v1_L1")]
    import kuwano as kw
    import split_spec as sp
    import study_spec as ss

    problems = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {got}" + ("" if ok else f"   (expected {want})"))
        if not ok:
            problems.append(name)

    print(f"IDEA 01 PROTOCOL v{PROTOCOL_VERSION} (frozen {FROZEN_ON}): {TITLE}\n")
    print("inputs")
    for p, h in INPUTS.items():
        check(p, _sha(os.path.join(repo, *p.split("/"))), h)

    print("\nsplits")
    check("split protocol version", sp.PROTOCOL_VERSION, SPLIT_PROTOCOL_VERSION)
    steps = sp.load(repo)
    var = sp.folds(steps, sp.FAMILY_PRIMARY)
    check("excluded folds have no validation run",
          all(not sp.split_train_val(f)[1] for f in var if f["fold"] in EXCLUDED_VARIANT_FOLDS), True)
    var = [f for f in var if f["fold"] not in EXCLUDED_VARIANT_FOLDS]
    sce = sp.folds(steps, sp.FAMILY_SECONDARY)
    pts = lambda fs: sum(len(f["test"]) - len({s["run"] for s in f["test"]}) for f in fs)
    check("variant folds", len(var), EXPECTED["variant_folds"])
    check("variant folds by scenario", dict(collections.Counter(f["fold"].split("_")[0] for f in var)),
          EXPECTED["variant_folds_by_scenario"])
    check("variant test steps", sum(len(f["test"]) for f in var), EXPECTED["variant_test_steps"])
    check("variant prediction points", pts(var), EXPECTED["variant_points"])
    check("every variant fold has validation", all(sp.split_train_val(f)[1] for f in var), True)
    check("scenario folds", tuple(f["fold"] for f in sce), EXPECTED["scenario_folds"])
    check("scenario test steps", sum(len(f["test"]) for f in sce), EXPECTED["scenario_test_steps"])
    check("scenario prediction points", pts(sce), EXPECTED["scenario_points"])
    maxrun = max(len({s["run"] for s in sp.split_train_val(f)[0]}) for f in var + sce)
    check("max training runs per fold", maxrun, MEASURED["max_training_runs_per_fold"])
    check("K exceeds every fold's training runs (K-B: all runs are neighbours)", maxrun < K, True)

    print("\nour model's settings agree with Temarl_Test_v1_L1/study_spec.py")
    check("threshold grid", tuple(ss.THRESHOLD_GRID), OUR_THRESHOLD_GRID)
    check("reference window", ss.REFERENCE_WINDOW, WINDOW)
    check("seeds", tuple(ss.MAIN_SEEDS), SEEDS)
    check("primary encoder is a study arm", PRIMARY_ENCODER in ss.ENCODERS, True)

    print("\nlabels and corpus descriptives (inputs and labels only)")
    d = kw.load(os.path.join(repo, "kuwano_repro", "data", "derived"))
    par = collections.Counter(t for s in steps for t in s["techniques_parent"])
    check("corpus parent labels in ATT&CK v11.0", (sum(t in d.techniques for t in par), len(par)),
          MEASURED["corpus_parent_labels_in_attack_v11"])
    check("parent instances", sum(par.values()), MEASURED["parent_instances"])
    used = set().union(*d.groups.values())
    unsup = tuple(sorted(t for t in par if t not in used))
    check("labels no v11 group uses", unsup, UNSUPPORTED_BY_ATTACK_V11)
    check("their instances", sum(par[t] for t in unsup), MEASURED["unsupported_instances"])

    runs = collections.defaultdict(list)
    for s in steps:
        runs[s["run"]].append(s)
    n = inst = rep = filt = one = 0
    for ss_ in runs.values():
        ss_.sort(key=lambda s: s["start"])
        for i in range(1, len(ss_)):
            obs = frozenset(t for s in ss_[max(0, i - WINDOW):i] for t in s["techniques_parent"])
            tgt = set(ss_[i]["techniques_parent"])
            n += 1
            inst += len(tgt)
            rep += len(tgt & obs)
            latest = max(min(d.tactics[t]) for t in obs)
            filt += sum(1 for t in tgt if max(d.tactics[t]) < latest)
            one += any(kw.sdc(obs, T) == 1 for T in d.groups.values())
    check("prediction points, corpus-wide", n, MEASURED["points_corpus_wide"])
    check("target label instances", inst, MEASURED["target_instances"])
    check("target labels already in the window", rep, MEASURED["target_instances_already_in_window"])
    check("target labels the tactic filter would drop", filt,
          MEASURED["target_instances_dropped_by_tactic_filter"])
    check("points with similarity 1 for K-A", one, MEASURED["points_with_similarity_one_for_K_A"])

    print(f"\nopen preconditions: {', '.join(PRECONDITIONS_OPEN)}")
    if problems:
        print(f"\nPROTOCOL CHECK FAILED: {len(problems)} item(s): {', '.join(problems)}")
        return 1
    print("\nPROTOCOL CHECK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
