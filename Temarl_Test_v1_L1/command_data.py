# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- command-level corpus, splits and multi-label windows
==========================================================================
Loads the command-level corpus, builds leakage-controlled splits, and emits
prediction windows for the multi-label next-command task.

The task
--------
Given the previous W annotated commands, predict the SET of ATT&CK parent
techniques annotated on the next command. Each command is an unordered label
set on both sides:

    input   : W commands, each a multi-hot vector over 84 parent techniques
    target  : multi-hot vector over 84 parent techniques (the next command)
    loss    : binary cross-entropy over the 84 labels

Why not the old single-label task
---------------------------------
The old corpus flattened `techniques: "T1087,T1083,T1201"` into three
consecutive steps and asked the model to predict one label at a time. 34.9% of
the resulting transitions were transitions *within* one command -- an artefact
of metadata typing order. Here, label order inside a command never enters the
data, so that artefact cannot be learned or scored.

Consequence for metrics: Top-1 accuracy from the old study is NOT comparable
with anything here. The targets are different objects (a set, not a token) and
the number of prediction points differs (889 - 36 commands, not 1347 - 36
tokens). Do not place the two side by side.

What "no label" means
---------------------
A technique absent from a command's annotation means the playbook did not
annotate it. It is NOT evidence that the technique did not occur. BCE treats
absent labels as negatives because it must; that assumption is a limitation of
the corpus, recorded here and reported in the audit.

Window lengths
--------------
W is a free parameter (8/16/32/64 in the study). For every W the set of
prediction targets is IDENTICAL -- short prefixes are kept and left-padded,
never discarded -- so results across W are paired on the same targets.
`window_coverage()` reports the fraction of targets whose entire available
history fits inside W.

No Markov
---------
There is no chain estimation, no smoothing, no synthetic generation anywhere
in this module or this study.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import _frozen
from vocab_v2 import NUM_TECHNIQUES as NT, technique_to_id

COMMANDS_PATH = _frozen.COMMANDS_PATH

# Scenario-stratified split. A scenario needs at least this many independent
# groups to contribute held-out data; below it, every group stays in training.
MIN_GROUPS_FOR_HOLDOUT = 3
VALIDATION_FRACTION = 0.2
TEST_FRACTION = 0.2
DEFAULT_SPLIT_SEED = 2310


# ── corpus ──────────────────────────────────────────────────────────────────

def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load_runs(path: str = COMMANDS_PATH) -> List[dict]:
    """Load the corpus as runs of command label-sets (parent-technique ids).

    Each command becomes a sorted tuple of distinct parent ids. Sorting is a
    canonical form for hashing and comparison only -- the model never sees an
    order, because commands enter as multi-hot vectors.

    Raises if any label falls outside the frozen vocabulary: an unmapped
    technique silently collapsing to UNK would corrupt the corpus.
    """
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    runs = []
    for name, record in sorted(raw["runs"].items()):
        cmds = []
        for cmd in record["commands"]:
            ids = sorted({technique_to_id(t) for t in cmd["techniques"]})
            if any(i >= NT or i < 0 for i in ids):
                bad = [t for t in cmd["techniques"]
                       if technique_to_id(t) >= NT or technique_to_id(t) < 0]
                raise ValueError(f"Unknown technique(s) {bad} in {name}")
            if ids:
                cmds.append(tuple(ids))
        if len(cmds) < 2:
            # A run with one command yields no prediction target.
            continue
        runs.append({
            "id": name,
            "scenario": record["scenario"],
            "commands": cmds,
            "group": _digest([list(c) for c in cmds]),
            "source_sha256": record.get("source_sha256"),
        })
    if not runs:
        raise ValueError(f"No usable runs in {path}")
    return runs


def corpus_metadata(path: str = COMMANDS_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if k not in ("runs", "scenarios")}


# ── splits ──────────────────────────────────────────────────────────────────

def split_runs(runs: Sequence[dict],
               seed: int = DEFAULT_SPLIT_SEED,
               held_out: Optional[str] = None) -> Tuple[Dict[str, List[dict]], List[str]]:
    """Group-aware, scenario-stratified split.

    Runs whose command sequences are identical form one group and never cross
    the split boundary -- otherwise the "held-out" run is a copy of a training
    run. Cross-scenario duplicate groups stay in training.

    `held_out` ("S1".."S7") puts an entire scenario in test: the scenario-level
    generalisation condition, which is a different and much harder question
    than the default variant-level split. Report them separately; never pool.

    NOTE: near-duplicate variants are NOT removed. Identical sequences are
    grouped; variants sharing most of their commands remain. `similarity()`
    quantifies what is left and the number is large (bigram Jaccard up to 0.90
    in the flat corpus). Treat default-split results as "prediction within
    known scenario variants", not generalisation.
    """
    groups: Dict[str, List[dict]] = defaultdict(list)
    for r in runs:
        groups[r["group"]].append(r)

    split: Dict[str, List[dict]] = {"train": [], "validation": [], "test": []}
    buckets: Dict[str, List[str]] = defaultdict(list)
    notes: List[str] = []
    rng = np.random.default_rng(seed)

    for group, members in sorted(groups.items()):
        scenarios = {m["scenario"] for m in members}
        if held_out is not None and held_out in scenarios:
            split["test"].extend(members)
        elif len(scenarios) > 1:
            split["train"].extend(members)
            notes.append(f"Cross-scenario duplicate group {group[:10]} kept in training.")
        else:
            buckets[next(iter(scenarios))].append(group)

    for sid, ids in sorted(buckets.items()):
        ids = list(rng.permutation(sorted(ids)))
        if len(ids) < MIN_GROUPS_FOR_HOLDOUT:
            notes.append(f"{sid}: {len(ids)} independent group(s); training only.")
            n_test, n_val = 0, 0
        else:
            n_test = 0 if held_out else max(1, int(round(TEST_FRACTION * len(ids))))
            n_val = max(1, int(round(VALIDATION_FRACTION * len(ids))))
        for i, group in enumerate(ids):
            part = "test" if i < n_test else \
                   "validation" if i < n_test + n_val else "train"
            split[part].extend(groups[group])

    for part in split:
        split[part].sort(key=lambda r: r["id"])
        if not split[part]:
            raise ValueError(
                f"Empty {part} split (held_out={held_out}). A fold with no "
                f"{part} data cannot be evaluated."
            )

    sets = [{r["group"] for r in split[k]} for k in ("train", "validation", "test")]
    for i in range(3):
        for j in range(i):
            if sets[i] & sets[j]:
                raise AssertionError("Identical runs crossed a split boundary")
    return split, notes


def subset(runs: Sequence[dict], fraction: float, seed: int) -> List[dict]:
    """Scenario-stratified nested subsample, keeping >=1 group per scenario."""
    by_scn: Dict[str, Dict[str, List[dict]]] = defaultdict(dict)
    for r in runs:
        by_scn[r["scenario"]].setdefault(r["group"], []).append(r)
    rng = np.random.default_rng(seed)
    out: List[dict] = []
    for sid, groups in sorted(by_scn.items()):
        ids = list(rng.permutation(sorted(groups)))
        take = max(1, int(np.ceil(len(ids) * fraction)))
        for g in ids[:take]:
            out.extend(groups[g])
    return sorted(out, key=lambda r: r["id"])


# ── windows ─────────────────────────────────────────────────────────────────

def windows(runs: Sequence[dict], window: int):
    """Build multi-label prediction windows.

    Returns
    -------
    X     : (n, window, NT) float32 multi-hot history, LEFT-padded with zeros
    mask  : (n, window)     float32, 1 where a real command sits
    Y     : (n, NT)         float32 multi-hot target (the next command)
    owners: list[str]       run id per window, for per-run reporting
    avail : (n,) int32      commands actually available as history
                            (avail > window means the window truncates)

    Every command index t >= 1 of every run yields exactly one window, for any
    `window`. Short prefixes are padded, never dropped, so the target set is
    identical across window lengths and results are paired.
    """
    if window < 1:
        raise ValueError("window must be >= 1")
    X, M, Y, owners, avail = [], [], [], [], []
    for r in runs:
        cmds = r["commands"]
        for t in range(1, len(cmds)):
            hist = cmds[max(0, t - window):t]
            x = np.zeros((window, NT), np.float32)
            m = np.zeros(window, np.float32)
            # Left-pad: the most recent command is always at index -1, so a
            # recurrent encoder's final state and a transformer's last
            # position always refer to "the command just executed".
            start = window - len(hist)
            for k, c in enumerate(hist):
                x[start + k, list(c)] = 1.0
                m[start + k] = 1.0
            y = np.zeros(NT, np.float32)
            y[list(cmds[t])] = 1.0
            X.append(x); M.append(m); Y.append(y)
            owners.append(r["id"]); avail.append(t)
    return (np.asarray(X), np.asarray(M), np.asarray(Y),
            owners, np.asarray(avail, np.int32))


def window_coverage(runs: Sequence[dict], window: int) -> dict:
    """How much of the available history each window actually sees."""
    avail = [t for r in runs for t in range(1, len(r["commands"]))]
    if not avail:
        return {}
    a = np.asarray(avail)
    return {
        "window": window,
        "n_targets": int(a.size),
        "full_history_pct": float(100.0 * np.mean(a <= window)),
        "mean_available": float(a.mean()),
        "median_available": float(np.median(a)),
        "max_available": int(a.max()),
        "mean_used": float(np.minimum(a, window).mean()),
        "truncated_targets": int(np.sum(a > window)),
    }


# ── audit ───────────────────────────────────────────────────────────────────

def coverage(runs: Sequence[dict], training: Sequence[dict]) -> dict:
    """Command-level coverage of an evaluation split against training.

    All quantities are over COMMAND LABEL SETS and transitions between
    consecutive commands. Nothing here counts within-command label order,
    because that information no longer exists in the representation.
    """
    def sets_of(rs):
        return [c for r in rs for c in r["commands"]]

    def bigrams_of(rs):
        return [(a, b) for r in rs
                for a, b in zip(r["commands"], r["commands"][1:])]

    ev_sets, tr_sets = sets_of(runs), set(sets_of(training))
    ev_bg = bigrams_of(runs)
    tr_bg = set(bigrams_of(training))
    labels = [t for c in ev_sets for t in c]
    tr_labels = {t for c in sets_of(training) for t in c}
    n_bg = max(1, len(ev_bg))
    uniq_bg = set(ev_bg)
    bg_counts = Counter(ev_bg)

    return {
        "runs": len(runs),
        "independent_groups": len({r["group"] for r in runs}),
        "commands": len(ev_sets),
        "technique_label_instances": len(labels),
        "prediction_targets": sum(len(r["commands"]) - 1 for r in runs),
        "mean_labels_per_command": float(np.mean([len(c) for c in ev_sets])),
        "max_labels_per_command": int(max(len(c) for c in ev_sets)),
        "multi_label_command_pct":
            float(100.0 * np.mean([len(c) > 1 for c in ev_sets])),
        "unique_techniques": len(set(labels)),
        "unique_command_sets": len(set(ev_sets)),
        "unseen_command_set_pct":
            float(100.0 * np.mean([c not in tr_sets for c in ev_sets])),
        "unique_command_bigrams": len(uniq_bg),
        "singleton_command_bigrams": int(sum(v == 1 for v in bg_counts.values())),
        "unseen_transition_occurrence_pct":
            float(100.0 * sum(v for k, v in bg_counts.items() if k not in tr_bg) / n_bg),
        "unseen_transition_type_pct":
            float(100.0 * np.mean([k not in tr_bg for k in uniq_bg])) if uniq_bg else 0.0,
        "unseen_technique_occurrence_pct":
            float(100.0 * np.mean([t not in tr_labels for t in labels])) if labels else 0.0,
        "self_loop_pct":
            float(100.0 * np.mean([a == b for a, b in ev_bg])) if ev_bg else 0.0,
    }


def label_support(split: Dict[str, List[dict]]) -> dict:
    """Per-label counts. Labels with no test support cannot be scored."""
    def counts(rs):
        return Counter(t for r in rs for c in r["commands"] for t in c)
    tr, va, te = (counts(split[k]) for k in ("train", "validation", "test"))
    present = sorted(set(tr) | set(va) | set(te))
    return {
        "n_labels_in_vocabulary": NT,
        "n_labels_in_corpus": len(present),
        "n_labels_in_train": len(tr),
        "n_labels_in_test": len(te),
        "test_labels_absent_from_train": sorted(set(te) - set(tr)),
        "train_labels_absent_from_test": len(set(tr) - set(te)),
        "per_label": {int(t): {"train": tr.get(t, 0), "validation": va.get(t, 0),
                               "test": te.get(t, 0)} for t in present},
    }


def similarity(split: Dict[str, List[dict]]) -> List[dict]:
    """Nearest training run for each held-out run, by command-bigram Jaccard.

    This is the headline caveat of the default split. A held-out run scoring
    0.9 here is a near-copy of a training run and its score measures
    memorisation of a known variant, not generalisation.
    """
    def bg(r):
        return set(zip(r["commands"], r["commands"][1:]))

    train = split["train"]
    out = []
    for part in ("validation", "test"):
        for r in split[part]:
            a = bg(r)
            best, best_j = None, -1.0
            for t in train:
                b = bg(t)
                union = len(a | b)
                j = (len(a & b) / union) if union else 0.0
                if j > best_j:
                    best, best_j = t["id"], j
            out.append({"split": part, "run": r["id"],
                        "nearest_training_run": best,
                        "command_bigram_jaccard": round(best_j, 5)})
    return out


def audit(split: Dict[str, List[dict]], notes: Sequence[str],
          windows_to_report: Sequence[int] = (8, 16, 32, 64)) -> dict:
    meta = corpus_metadata()
    return {
        "corpus": meta,
        "representation": "command-level multi-label; within-command label "
                          "order is discarded by construction",
        "split_seed": DEFAULT_SPLIT_SEED,
        "notes": list(notes),
        "splits": {k: [r["id"] for r in v] for k, v in split.items()},
        "scenarios_per_split": {
            k: dict(Counter(r["scenario"] for r in v)) for k, v in split.items()},
        "coverage": {k: coverage(v, split["train"]) for k, v in split.items()},
        "label_support": label_support(split),
        "similarity": similarity(split),
        "window_coverage": {
            str(w): {k: window_coverage(v, w) for k, v in split.items()}
            for w in windows_to_report},
        "caveats": [
            "Scripted playbook annotations, not real-world attack traces.",
            "Absent label means absent annotation, not absence of behaviour.",
            "Default split holds out VARIANTS; see similarity[]. Scenario-level "
            "generalisation requires --held-out and is reported separately.",
            "Seeds and repeated episodes are not independent attack campaigns.",
        ],
    }
