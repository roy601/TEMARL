"""Idea 01, step 2: run the adapted Kuwano conditions and the context baselines, blind.

    python idea01_kuwano/run_kuwano.py

Writes
  out/validation.json         per condition and fold: the threshold selected on VALIDATION, and
                              the validation micro-F1 at every grid value
  sealed/predictions.jsonl    per TEST prediction point: the predicted label set and the top-10
                              ranking. No targets, and no test metric.
  sealed/MANIFEST.json        SHA-256 of the sealed file (CRLF normalised to LF)

Blinding (spec.ORDER_OF_WORK step 3): no test metric is computed here. Test points are built
without their targets. Test metrics are computed once, at unblinding (step 5), from the
sealed predictions, by the same code for every model.

Settings come from spec.py (frozen protocol 1.0); nothing is set here.
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(REPO, "camlds_real"), os.path.join(REPO, "kuwano_repro"),
                os.path.join(REPO, "Temarl_Test_v1_L1")]

import numpy as np  # noqa: E402

import kuwano as kw  # noqa: E402
import metrics_cmd as mc  # noqa: E402
import spec  # noqa: E402
import split_spec as sp  # noqa: E402

OUT = os.path.join(HERE, "out")
SEALED = os.path.join(HERE, "sealed")
TOP = 10                                     # ranking depth kept; recall@5 needs 5

with open(os.path.join(REPO, "camlds_real", "out", "vocab.json"), encoding="utf-8") as fh:
    LABELS = tuple(json.load(fh)["parent_techniques"])
IDX = {t: i for i, t in enumerate(LABELS)}

# (condition, window): window None = full history; "n/a" = the baseline ignores the window
RUNS = [("K-A-val", spec.WINDOW), ("K-A-pub", spec.WINDOW), ("K-B-val", spec.WINDOW),
        ("K-A-val", None), ("K-A-pub", None), ("K-B-val", None),
        ("repeat_previous", "n/a"), ("label_prior", "n/a")]


def by_run(steps):
    runs = collections.defaultdict(list)
    for s in steps:
        runs[s["run"]].append(s)
    for r in runs.values():
        r.sort(key=lambda s: s["start"])
    return runs


def points(runs, names, window, with_target):
    """Prediction points of the given runs: every step but the first of each run."""
    out = []
    for r in sorted(names):
        ss = runs[r]
        for i in range(1, len(ss)):
            hist = ss[:i] if window in (None, "n/a") else ss[max(0, i - window):i]
            p = {"run": r, "exec_index": ss[i]["exec_index"], "pos": i,
                 "observed": frozenset(t for s in hist for t in s["techniques_parent"]),
                 "previous": frozenset(ss[i - 1]["techniques_parent"])}
            if with_target:
                p["target"] = frozenset(ss[i]["techniques_parent"])
            out.append(p)
    return out


def decide(score, thr):
    """score: label -> (n identical neighbours, SupportRate). Exact comparison."""
    return [t for t in LABELS if score[t][0] > 0 or score[t][1] >= thr]


def ranking(score):
    return sorted(LABELS, key=lambda t: (-score[t][0], -score[t][1], IDX[t]))[:TOP]


def select_threshold(grid, val_pts, scorer):
    """Same rule as Temarl_Test_v1_L1/metrics_cmd.select_threshold: maximise validation
    micro-F1, ties to the smallest value. Decisions are made exactly; the metric code then
    receives 0/1 decisions at 0.5."""
    y = np.array([[t in p["target"] for t in LABELS] for p in val_pts], np.float64)
    scores = [scorer(p) for p in val_pts]
    best_t, best, curve = None, -1.0, []
    for thr in sorted(grid):
        sets = [set(decide(s, thr)) for s in scores]
        dec = np.array([[t in d for t in LABELS] for d in sets], np.float64)
        f1 = mc.threshold_metrics(dec, y, 0.5)["micro_f1"]
        curve.append([str(thr), f1])
        if f1 > best + 1e-12:
            best_t, best = thr, f1
    return best_t, best, curve


def norm_sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def main():
    for p, h in spec.INPUTS.items():          # the pinned inputs, or stop
        got = norm_sha(os.path.join(REPO, *p.split("/")))
        if got != h:
            print(f"INPUT CHANGED: {p}\n  got {got}\n  pinned {h}")
            return 1

    steps = sp.load(REPO)
    runs = by_run(steps)
    folds = [("variant", f) for f in sp.folds(steps, sp.FAMILY_PRIMARY)
             if f["fold"] not in spec.EXCLUDED_VARIANT_FOLDS]
    folds += [("scenario", f) for f in sp.folds(steps, sp.FAMILY_SECONDARY)]

    da = kw.load(os.path.join(REPO, "kuwano_repro", "data", "derived"), spec.ATTACK_VERSION)
    ka_cache, identical = {}, collections.Counter()

    def ka(obs):
        if obs not in ka_cache:
            s, _ = kw.recommend_limit(obs, da, k=spec.K, tiebreak="name")
            ka_cache[obs] = ({t: s[t] for t in LABELS}, any(n for n, _ in s.values()))
        return ka_cache[obs][0]

    kuwano_grid = spec.KUWANO_THRESHOLD_GRID
    our_grid = tuple(Fraction(str(x)) for x in spec.OUR_THRESHOLD_GRID)
    validation, sealed = {}, []

    for cond, window in RUNS:
        key = f"{cond}@{'W' + str(window) if isinstance(window, int) else window}"
        validation[key] = {}
        for family, f in folds:
            tr, va = sp.split_train_val(f)
            tr_runs = sorted({s["run"] for s in tr})
            va_runs = sorted({s["run"] for s in va})
            te_runs = sorted({s["run"] for s in f["test"]})
            assert not (set(tr_runs) & set(te_runs)) and not (set(va_runs) & set(te_runs))
            vp = points(runs, va_runs, window, with_target=True)
            tp = points(runs, te_runs, window, with_target=False)

            if cond.startswith("K-A"):
                scorer = lambda p: ka(p["observed"])  # noqa: E731
            elif cond == "K-B-val":
                ref = {r: frozenset(t for s in runs[r] for t in s["techniques_parent"]) for r in tr_runs}
                db = kw.Data(LABELS, {}, ref, {"name": {r: i for i, r in enumerate(tr_runs)}})
                cache = {}

                def scorer(p, db=db, cache=cache):
                    if p["observed"] not in cache:
                        cache[p["observed"]] = kw.recommend_limit(p["observed"], db, k=spec.K,
                                                                  tiebreak="name")[0]
                    return cache[p["observed"]]
            elif cond == "label_prior":
                n = len(tr)
                cnt = collections.Counter(t for s in tr for t in s["techniques_parent"])
                prior = {t: (0, Fraction(cnt[t], n)) for t in LABELS}
                scorer = lambda p, prior=prior: prior  # noqa: E731
            else:  # repeat_previous: the previous step's set; ranked previous-first, then by label order
                scorer = lambda p: {t: (int(t in p["previous"]), Fraction(0)) for t in LABELS}  # noqa: E731

            if cond in ("K-A-val", "K-B-val"):
                thr, best, curve = select_threshold(kuwano_grid, vp, scorer)
            elif cond == "label_prior":
                thr, best, curve = select_threshold(our_grid, vp, scorer)
            elif cond == "K-A-pub":
                thr = spec.PUBLISHED_THRESHOLD
                _, best, curve = select_threshold((thr,), vp, scorer)
            else:
                thr, best, curve = Fraction(1), None, []    # n = 1 for every previous-step label
            grid = kuwano_grid if cond in ("K-A-val", "K-B-val") else our_grid
            validation[key][f["fold"]] = {
                "family": family, "threshold": str(thr), "validation_micro_f1": best,
                "at_grid_edge": cond in ("K-A-val", "K-B-val", "label_prior") and thr in (min(grid), max(grid)),
                "validation_curve": curve, "validation_points": len(vp), "test_points": len(tp),
                "reference_runs": tr_runs if cond == "K-B-val" else None, "validation_runs": va_runs,
            }
            for p in tp:
                s = scorer(p)
                if cond.startswith("K-A"):
                    identical[(key, family)] += ka_cache[p["observed"]][1]
                elif cond == "K-B-val":
                    identical[(key, family)] += any(v[0] for v in s.values())
                sealed.append({"condition": key, "family": family, "fold": f["fold"], "run": p["run"],
                               "exec_index": p["exec_index"], "pos": p["pos"],
                               "predicted": sorted(decide(s, thr), key=IDX.get), "top10": ranking(s)})

    # point counts must match the frozen protocol, per condition
    cnt = collections.Counter((r["condition"], r["family"]) for r in sealed)
    for (key, family), n in sorted(cnt.items()):
        want = spec.EXPECTED["variant_points" if family == "variant" else "scenario_points"]
        assert n == want, (key, family, n, want)

    os.makedirs(OUT, exist_ok=True)
    os.makedirs(SEALED, exist_ok=True)
    with open(os.path.join(OUT, "validation.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"protocol": spec.PROTOCOL_VERSION, "labels": len(LABELS),
                   "identical_neighbour_test_points": {f"{k}|{fam}": v for (k, fam), v in sorted(identical.items())},
                   "conditions": validation}, fh, indent=1, sort_keys=True)
    sealed.sort(key=lambda r: (r["condition"], r["family"], r["fold"], r["run"], r["pos"]))
    path = os.path.join(SEALED, "predictions.jsonl")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        for r in sealed:
            fh.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    man = {"file": "predictions.jsonl", "sha256_lf": norm_sha(path), "lines": len(sealed),
           "protocol": spec.PROTOCOL_VERSION,
           "note": "SEALED. No targets and no test metric inside. Open only at spec.ORDER_OF_WORK step 5."}
    with open(os.path.join(SEALED, "MANIFEST.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(man, fh, indent=1, sort_keys=True)

    print(f"sealed {len(sealed)} test predictions over {len(RUNS)} conditions; sha256 {man['sha256_lf']}")
    print("validation-selected thresholds (validation only):")
    for key, per in validation.items():
        ts = collections.Counter(v["threshold"] for v in per.values())
        edge = sum(v["at_grid_edge"] for v in per.values())
        print(f"  {key:<24} {dict(ts)}{'  edge in ' + str(edge) + ' folds' if edge else ''}")
    print("test points with an identical neighbour (inputs only):",
          {f"{k}|{fam}": v for (k, fam), v in sorted(identical.items()) if v})
    return 0


if __name__ == "__main__":
    sys.exit(main())
