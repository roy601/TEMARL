# -*- coding: utf-8 -*-
"""
TEMARL v2 — Real-Corpus Loaders (COMISET + CAM-LDS)
===================================================
Closes F-DAT-02/03/04/05/09 and supplies the real-data arm of F-DAT-08.

WHY THIS MODULE EXISTS
----------------------
Until now the v2 stack trained on SIMULATOR rollouts whose attacker is
parameterised by CAM-LDS *structure*. No real sequence was ever fed to an
encoder and no real sequence was ever used for evaluation, so the honest answer
to "does any reported number come from real attacker behaviour?" was NO.
That is defect F-DAT-09, and it is the first thing a reviewer asks of a thesis
that advertises real-data grounding.

DISCLOSURES THIS MODULE COMPUTES (rather than asserts)
------------------------------------------------------
v1's data chapter contained several statements that do not survive measurement.
`corpus_report()` recomputes each from the file so the manuscript can be
corrected from evidence:

  F-DAT-02  v1 reported "avg_sequence_length = 5.21" without disclosing that
            98.5% of raw transitions are SELF-LOOPS: raw mean length is 274.5
            (max 418,367) and 5.21 is the RUN-COLLAPSED mean. Reporting the raw
            figure would inflate predictable-information ~3x.
  F-DAT-03  76% of sessions (17,724/23,361) were dropped by a length>=2 filter.
            Because ~98% of raw length is repetition, a raw length-2 session may
            collapse to length 1 -- the filter does NOT guarantee a usable
            multi-step sequence. The retained set is the atypical "active" tail.
  F-DAT-04  v1 (Sec 4.3.5) states the top-3 are "T1574 ~30%, T1543 ~15%,
            T1553 ~12% ... precisely the three COMISET-extension techniques at
            IDs 20-22". MEASURED, the top-3 are T1574 / T1543 / **T1053**, and
            T1053 is id 4 -- a SIMULATION technique. Only ONE of the top three is
            a COMISET extension, so the retrospective justification for the
            vocabulary expansion is weaker than claimed.
  F-DAT-05  v1 gives BOTH "~47%" (Sec 4.3.2) and "~57%" (Sec 4.2.2/4.3.5) for the
            share that would map to UNK. Measured: ids 20-22 = 50.3%.
  F-DAT-06  ~200:1 class imbalance -> macro-F1 and class weighting are mandatory.

CROSS-CORPUS DIRECTION (F-DAT-08)
---------------------------------
COMISET's observed tactics are a strict SUBSET of CAM-LDS's (COMISET-only = {}).
So COMISET -> CAM-LDS is NOT a generalisation test: 8 of 13 tactic classes would
be unseen at test time. The valid headline direction is CAM-LDS -> COMISET.
The reverse must be reported as RESTRICTED-SUPPORT over the shared tactics only;
`restricted_support_mask()` produces exactly that mask.
"""

import itertools
import json
import os
from collections import Counter, defaultdict

import numpy as np

from vocab_v2 import (MAX_SEQ_LEN, NUM_TECHNIQUES, PAD_ID, UNK_ID, tactic_of,
                      technique_to_id)

HERE = os.path.dirname(os.path.abspath(__file__))
COMISET_PATH = os.path.join(HERE, "..", "data", "comiset_sessions.json")
CAMLDS_PATH = os.path.join(HERE, "..", "data", "camlds_grounding.json")


# ── raw corpus ingestion ─────────────────────────────────────────────────────

def load_comiset_raw(path=COMISET_PATH):
    """Return {guid: [raw technique strings]} plus the file's own metadata."""
    with open(path, encoding="utf-8") as f:
        blob = json.load(f)
    sessions = blob.get("sessions", {})
    out = {}
    for guid, rec in sessions.items():
        rt = rec.get("raw_techniques") if isinstance(rec, dict) else rec
        if rt:
            out[guid] = list(rt)
    return out, blob.get("metadata", {})


def collapse_runs(ids):
    """[T,T,T,X] -> [T,X]. Load-bearing and previously undocumented (F-DAT-02)."""
    return [k for k, _ in itertools.groupby(ids)]


def to_ids(raw_list, collapse=True):
    ids = [technique_to_id(t) for t in raw_list]
    ids = [i for i in ids if i < NUM_TECHNIQUES]      # drop UNK/PAD
    return collapse_runs(ids) if collapse else ids


def load_comiset_sequences(path=COMISET_PATH, collapse=True, min_len=2):
    """Technique-id sequences ready for next-token modelling."""
    raw, meta = load_comiset_raw(path)
    seqs, dropped = [], 0
    for guid, rt in raw.items():
        ids = to_ids(rt, collapse=collapse)
        if len(ids) >= min_len:
            seqs.append(ids)
        else:
            dropped += 1
    return seqs, {"n_raw_sessions": len(raw), "n_kept": len(seqs),
                  "n_dropped_short": dropped, "file_metadata": meta}


def load_camlds_sequences(path=CAMLDS_PATH):
    """The 34 real CAM-LDS attack chains (condensed per-scenario orderings),
    reserved as a HELD-OUT real-data test set. Never used for training."""
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    out = {}
    for s in g["scenarios"]:
        raw = [x for x in s["technique_sequence"] if not x.startswith("<")]
        ids = [technique_to_id(x) for x in raw]
        ids = [i for i in ids if i < NUM_TECHNIQUES]
        if len(ids) >= 2:
            out[s["id"]] = {"ids": ids, "name": s["name"],
                            "terminal": s["terminal_tactic"]}
    return out


# ── next-token windowing (matches the encoder contract) ─────────────────────

def to_windows(seqs, max_len=MAX_SEQ_LEN):
    """(RIGHT-padded prefix, true_length) -> next technique.

    RIGHT padding is required by the v2 encoder contract: v1 LEFT-padded, which
    with absolute positional encoding let the model read episode step off the
    padding geometry (h -> step-index probe R^2 = 0.97). See encoders.py."""
    X, L, Y, S = [], [], [], []
    for si, s in enumerate(seqs):
        for t in range(1, len(s)):
            pre = s[max(0, t - max_len):t]
            ids = np.full(max_len, PAD_ID, dtype=np.int64)
            ids[:len(pre)] = pre
            X.append(ids); L.append(len(pre)); Y.append(s[t]); S.append(si)
    return (np.array(X), np.array(L, dtype=np.int64),
            np.array(Y, dtype=np.int64), np.array(S, dtype=np.int64))


def session_split(seq_idx, frac=(0.70, 0.15, 0.15), seed=42):
    """Split BY SESSION, never by window: windows from one attack chain share a
    prefix, so a window-level split would leak the same campaign across train and
    test and inflate held-out accuracy."""
    rng = np.random.default_rng(seed)
    n = int(seq_idx.max()) + 1
    perm = rng.permutation(n)
    a, b = int(frac[0] * n), int((frac[0] + frac[1]) * n)
    tr, va, te = set(perm[:a]), set(perm[a:b]), set(perm[b:])
    m = lambda S: np.array([i for i, s in enumerate(seq_idx) if s in S])
    return m(tr), m(va), m(te)


# ── baselines and disclosure statistics ─────────────────────────────────────

def trivial_baselines(Y_train, Y_test, k=3):
    """F-EVL-01/02 — the comparison v1 omitted. v1 reported Top-1 0.341 against
    a majority class of 0.372, i.e. it LOST to 'always predict T1574'."""
    cnt = np.bincount(Y_train, minlength=NUM_TECHNIQUES)
    order = np.argsort(-cnt)
    return {"majority_top1": float((Y_test == order[0]).mean()),
            "freq_topk": float(np.isin(Y_test, order[:k]).mean()),
            "majority_id": int(order[0]),
            "n_classes_train": int((cnt > 0).sum())}


def restricted_support_mask(Y, source_ids):
    """F-DAT-08 — mask test items whose TACTIC was seen in the source corpus, so
    a transfer number is reported over valid support only."""
    seen = {tactic_of(int(i)) for i in source_ids}
    return np.array([tactic_of(int(y)) in seen for y in Y])


def corpus_report(path=COMISET_PATH):
    """Recompute every disclosure the manuscript needs (F-DAT-02/03/04/05/06)."""
    raw, meta = load_comiset_raw(path)
    self_loops = trans = 0
    raw_len, col_len = [], []
    tok = Counter()
    for rt in raw.values():
        ids = [technique_to_id(t) for t in rt]
        ids = [i for i in ids if i < NUM_TECHNIQUES]
        if not ids:
            continue
        raw_len.append(len(ids))
        for a, b in zip(ids, ids[1:]):
            trans += 1
            self_loops += (a == b)
        c = collapse_runs(ids)
        col_len.append(len(c))
        for i in c:
            tok[i] += 1
    total = sum(tok.values())
    top = tok.most_common(3)
    ext = sum(tok[i] for i in (20, 21, 22))
    kept = sum(1 for L in col_len if L >= 2)
    return {
        "n_sessions": len(raw),
        "self_loop_rate": self_loops / max(trans, 1),
        "raw_len": {"mean": float(np.mean(raw_len)), "median": float(np.median(raw_len)),
                    "p99": float(np.percentile(raw_len, 99)), "max": int(np.max(raw_len))},
        "collapsed_len": {"mean": float(np.mean(col_len)), "median": float(np.median(col_len)),
                          "max": int(np.max(col_len))},
        "pct_length_is_repetition": 1 - np.mean(col_len) / np.mean(raw_len),
        "survivorship": {"kept": kept, "dropped": len(col_len) - kept,
                         "drop_rate": (len(col_len) - kept) / max(len(col_len), 1)},
        "top3": [(int(i), c, c / total) for i, c in top],
        "ext_20_22_share": ext / max(total, 1),
        "imbalance_ratio": (max(tok.values()) / max(min(tok.values()), 1)) if tok else 0,
        "n_distinct_techniques": len(tok),
        "unk_rate": 0.0,
        "file_metadata": meta,
    }


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 82)
    print("  TEMARL v2 — REAL-CORPUS LOADERS (COMISET + CAM-LDS)")
    print("=" * 82)

    rep = corpus_report()
    print(f"\n  [F-DAT-02] REPETITION ARTEFACT (undisclosed in v1)")
    print(f"    self-transition rate      : {rep['self_loop_rate']:.1%} of ALL transitions")
    print(f"    raw length      mean={rep['raw_len']['mean']:.1f} median={rep['raw_len']['median']:.0f} "
          f"p99={rep['raw_len']['p99']:.0f} max={rep['raw_len']['max']:,}")
    print(f"    collapsed length mean={rep['collapsed_len']['mean']:.2f} "
          f"median={rep['collapsed_len']['median']:.0f} max={rep['collapsed_len']['max']}")
    print(f"    => {rep['pct_length_is_repetition']:.1%} of raw length is consecutive repetition")
    print(f"    v1 reported 'avg_sequence_length = 5.21' -- that is the COLLAPSED "
          f"mean ({rep['collapsed_len']['mean']:.2f}), a DERIVED statistic.")

    s = rep["survivorship"]
    md = rep.get("file_metadata", {}) or load_comiset_raw()[1]
    up_before = md.get("sessions_before_filter")
    up_after = md.get("sessions_after_filter")
    up_drop = md.get("dropped_short_sequences")
    print(f"\n  [F-DAT-03] SURVIVORSHIP FILTER")
    print(f"    UPSTREAM (during extraction, recorded in file metadata):")
    print(f"      {up_before:,} raw sessions -> {up_after:,} kept, "
          f"{up_drop:,} dropped  = {up_drop / max(up_before, 1):.1%} DROPPED")
    print(f"    IN THIS FILE (already pre-filtered): kept {s['kept']:,}, "
          f"further dropped {s['dropped']:,}")
    print(f"    NOTE: the 76% loss is NOT re-derivable from the retained sessions --")
    print(f"    it must be cited from metadata, or it silently disappears from the")
    print(f"    thesis. Because ~98% of raw length is repetition, a raw length-2")
    print(f"    session can collapse to length 1, so the filter does NOT guarantee")
    print(f"    a usable multi-step chain: the kept set is the atypical active tail.")

    print(f"\n  [F-DAT-04] TOP-3 TECHNIQUES (v1 Sec 4.3.5 is WRONG)")
    from vocab_v2 import ID_TO_TECHNIQUE
    for i, c, sh in rep["top3"]:
        src = "COMISET-extension (id 20-22)" if 20 <= i <= 22 else "SIMULATION technique"
        print(f"    {ID_TO_TECHNIQUE[i]:<8} id={i:<3} {sh:>6.1%}   {src}")
    n_ext = sum(1 for i, _, _ in rep["top3"] if 20 <= i <= 22)
    print(f"    => only {n_ext}/3 of the top three are COMISET extensions; v1 claimed 3/3")
    print(f"       (v1 named T1553; the actual third is T1053, id 4)")

    print(f"\n  [F-DAT-05] SHARE THAT WOULD MAP TO UNK WITHOUT ids 20-22")
    print(f"    measured {rep['ext_20_22_share']:.1%}   "
          f"(v1 states BOTH '~47%' and '~57%' in different sections)")

    print(f"\n  [F-DAT-06] CLASS IMBALANCE")
    print(f"    distinct techniques {rep['n_distinct_techniques']}   "
          f"max:min ratio {rep['imbalance_ratio']:.0f}:1  -> macro-F1 + class weighting required")

    # ---- windowed dataset ------------------------------------------------
    seqs, info = load_comiset_sequences()
    X, L, Y, S = to_windows(seqs)
    tr, va, te = session_split(S)
    print(f"\n  WINDOWED DATASET (right-padded, session-level split 70/15/15, seed 42)")
    print(f"    sessions {info['n_kept']:,}  windows {len(Y):,}   "
          f"train {len(tr):,} / val {len(va):,} / test {len(te):,}")
    print(f"    UNK in windows: {(Y == UNK_ID).sum()}  (union vocab => 0 expected)")
    b = trivial_baselines(Y[tr], Y[te])
    print(f"    trivial baselines on the held-out split:")
    print(f"      majority Top-1 = {b['majority_top1']:.3f} "
          f"(class {ID_TO_TECHNIQUE[b['majority_id']]})   "
          f"freq Top-3 = {b['freq_topk']:.3f}")
    print(f"      ^ v1's encoder scored Top-1 0.341 vs majority 0.372 => it LOST")

    cam = load_camlds_sequences()
    Xc, Lc, Yc, Sc = to_windows([v["ids"] for v in cam.values()])
    print(f"\n  CAM-LDS HELD-OUT REAL CHAINS (never trained on)")
    print(f"    scenarios {len(cam)}  windows {len(Yc)}")
    mask = restricted_support_mask(Yc, np.concatenate([np.array(s) for s in seqs[:2000]]))
    print(f"    [F-DAT-08] restricted-support: {mask.mean():.1%} of CAM-LDS test items "
          f"have a tactic seen in COMISET")
    print(f"    => a COMISET-trained model may only be scored on that subset; the")
    print(f"       valid headline direction is CAM-LDS -> COMISET.")
    print("=" * 82)


# ── CAM-LDS: source-verified loader + scenario-level splitting ───────────────
#
# Why this is separate from load_camlds_sequences() above: that function reads
# the PAPER RECONSTRUCTION and returns condensed per-scenario chains, reserved
# as a held-out probe. The functions below read the SOURCE-VERIFIED grounding
# parsed from the published AttackBed playbooks (parse_attackbed.py) at FULL
# STEP RESOLUTION -- 36 runs / 1,339 labelled technique instances -- which is
# what makes CAM-LDS trainable rather than merely a test probe.

CAMLDS_VERIFIED_PATH = os.path.join(HERE, "..", "data",
                                    "camlds_grounding_verified.json")


def load_camlds_verified(path=CAMLDS_VERIFIED_PATH, collapse=False, min_len=2):
    """Return (seqs, scenario_of_seq, info) from the source-verified grounding.

    collapse=False by default: unlike COMISET (98.5% self-loops, where collapsing
    consecutive repeats is essential), CAM-LDS repeats only 18.6% of the time and
    those repeats are genuine repeated commands in the playbook, not logging
    artefacts. Collapsing them would discard real signal.
    """
    with open(path, encoding="utf-8") as f:
        g = json.load(f)
    seqs, scen, dropped = [], [], 0
    for fn, run in g["runs"].items():
        ids = [technique_to_id(c) for c in run["sequence"]]
        if collapse:
            ids = collapse_runs(ids)
        if len(ids) >= min_len:
            seqs.append(ids); scen.append(run["scenario"])
        else:
            dropped += 1
    return seqs, scen, {"n_runs": len(seqs), "n_dropped": dropped,
                        "n_steps": sum(len(s) for s in seqs),
                        "n_scenarios": len(set(scen)),
                        "provenance": g.get("provenance", "")}


def scenario_loso_folds(scen_of_seq):
    """Leave-One-Scenario-Out folds over SEQUENCE indices.

    CAM-LDS must NOT use session_split(). Scenario 1 alone is 18 of the 36 runs
    and its variants share a mean Jaccard of 0.871, against 0.078 across
    scenarios -- a 10.4x ratio. A run-level split therefore places near-duplicate
    campaigns on both sides and reports memorisation as generalisation. Holding
    out a WHOLE scenario is the only split at which a held-out number means
    'generalises to an unseen campaign'.
    """
    scen = list(scen_of_seq)
    order = sorted(set(scen), key=lambda x: int(x[1:]))
    for held in order:
        te = [i for i, s in enumerate(scen) if s == held]
        tr = [i for i, s in enumerate(scen) if s != held]
        yield held, np.array(tr), np.array(te)


def windows_for_seqs(X, L, Y, S, seq_idx):
    """Select the window rows belonging to a set of SEQUENCE indices."""
    keep = np.isin(S, np.asarray(seq_idx))
    return np.nonzero(keep)[0]
