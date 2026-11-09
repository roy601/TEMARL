# -*- coding: utf-8 -*-
"""Stage 1 of protocol 1.2: score our encoders on the test split, once, after the freeze.

    python camlds_encoder/evaluate_test.py --validation-dry-run --conditions main   # opens nothing
    python camlds_encoder/evaluate_test.py --open-test                              # once

--validation-dry-run runs the same code on validation outputs and must reproduce the validation
scores already on record. It never reads a test output.
--open-test refuses to run unless `idea01_kuwano/spec_1_2.py` passes, every training is present
and matches its fingerprint, and no result exists yet. It never changes a design, threshold or rule.

Metrics are the frozen functions of metrics_cmd.py (protocol 1.0, Section 6). Copy, novel, repeat
and new are protocol 1.1 (A1, A2). The statistics are protocol 1.0 Section 7 and 1.2 Section 7.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

import numpy as np
from scipy import stats as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import data  # noqa: E402
import run as R  # noqa: E402
import run_variants as RV  # noqa: E402
from port import Mx, REPO, SPEC  # noqa: E402

sys.path.insert(0, os.path.join(REPO, "idea01_kuwano"))
import spec as S10  # noqa: E402  protocol 1.0: bootstrap size and seed, alpha, metric names

PRIMARY, SECONDARY = "allpos", ("gru_allpos", "lstm_allpos")
ENCODERS = (PRIMARY, *SECONDARY)
BASELINE = "baseline"                                           # main condition only, descriptive
NAMES = {"allpos": "Transformer", "gru_allpos": "GRU", "lstm_allpos": "LSTM", "baseline": "Old Transformer"}
METRICS = (S10.PRIMARY_METRIC, *S10.SECONDARY_METRICS, *S10.THRESHOLD_FREE_METRICS)
METRIC_NAMES = {"micro_f1": "Micro-F1", "exact_set_accuracy": "Exact-set accuracy", "macro_f1": "Macro-F1",
                "precision_at_1": "Precision@1", "recall_at_3": "Recall@3", "recall_at_5": "Recall@5"}
SUBSETS = ("all", "novel", "copy")                              # protocol 1.1, A1
FAMILY, SCENARIO_FAMILY = data.sp.FAMILY_PRIMARY, data.sp.FAMILY_SECONDARY
SCENARIOS = S10.REPORT_PER_SCENARIO                             # "1", "3", "6"
LOGITS = {"val": "val_logits.npy", "test": "test_logits.npy"}
RESULTS = "STAGE1_RESULTS"
TEST_DIR, DRY_NAME = "out_test", "STAGE1_DRYRUN_ON_VALIDATION"
SPEC_1_2 = os.path.join(REPO, "idea01_kuwano", "spec_1_2.py")


# ── statistics ────────────────────────────────────────────────────────────────

def bootstrap_ci(d):
    """95% percentile CI of the mean, resampling folds (protocol 1.0, Section 7)."""
    d = np.asarray(d, np.float64)
    rng = np.random.default_rng(S10.BOOTSTRAP_SEED)
    means = d[rng.integers(0, len(d), (S10.BOOTSTRAP_RESAMPLES, len(d)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def wilcoxon_p(d):
    """Two-sided Wilcoxon signed-rank. Zero differences are dropped (scipy's default)."""
    d = np.asarray(d, np.float64)
    if np.count_nonzero(d) < 2:
        return None
    return float(sps.wilcoxon(d, zero_method="wilcox", correction=False, alternative="two-sided",
                              method="auto").pvalue)


def holm(ps):
    """Holm step-down adjusted p-values, in the order given."""
    order, adj, running = np.argsort(ps), [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def contrast(a, b):
    """a and b: fold -> value. Difference a - b per fold, as protocol 1.0 Section 7."""
    folds = sorted(set(a) & set(b))
    d = np.array([a[f] - b[f] for f in folds])
    lo, hi = bootstrap_ci(d)
    per = {s: float(np.mean([a[f] - b[f] for f in folds if f[0] == s])) for s in SCENARIOS
           if any(f[0] == s for f in folds)}
    return {"mean": float(d.mean()), "ci": [lo, hi], "p": wilcoxon_p(d), "n_folds": len(folds),
            "folds_a_better": int((d > 0).sum()), "per_scenario": per}


def verdict(c, name_a, name_b):
    """The only wording allowed. 'Outperforms' needs the CI to exclude 0 and corrected p < alpha."""
    excludes_zero = c["ci"][0] > 0 or c["ci"][1] < 0
    if not (excludes_zero and c.get("p_holm") is not None and c["p_holm"] < S10.ALPHA):
        return "no difference shown"
    winner, loser = (name_a, name_b) if c["mean"] > 0 else (name_b, name_a)
    same = all((v > 0) == (c["mean"] > 0) for v in c["per_scenario"].values())
    return f"{winner} outperforms {loser} (direction {'holds' if same else 'does NOT hold'} in every scenario)"


# ── scoring ───────────────────────────────────────────────────────────────────

def _micro(pred, t, mask):
    tp, fp, fn = float(np.sum(pred & t & mask)), float(np.sum(pred & ~t & mask)), float(np.sum(~pred & t & mask))
    return None if tp + fp + fn == 0 else Mx._prf(tp, fp, fn)[2]


def _points(prob, y, threshold, sel):
    if not sel.any():
        return None
    m = {**Mx.threshold_metrics(prob[sel], y[sel], threshold), **Mx.ranking_metrics(prob[sel], y[sel])}
    return {k: m[k] for k in METRICS}


def _counts(pred, t, sel):
    if not sel.any():
        return None
    p, q = pred[sel], t[sel]
    return [float(np.sum(p & q)), float(np.sum(p & ~q)), float(np.sum(~p & q))]


def score_cell(logits, threshold, tr):
    """All metrics of one training on one fold's points, at its validation-chosen threshold."""
    prob, y = Mx._sigmoid(np.asarray(logits, np.float64)), np.asarray(tr["y"], np.float64)
    copy, everything = tr["copy"], np.ones(len(y), bool)
    out = {"all": _points(prob, y, threshold, everything), "novel": _points(prob, y, threshold, ~copy),
           "copy": _points(prob, y, threshold, copy)}
    pred, t = prob >= threshold, y > 0.5
    out["labels"] = {"repeat": _micro(pred, t, tr["in_window"]), "new": _micro(pred, t, ~tr["in_window"])}
    out["counts"] = {"all": _counts(pred, t, everything), "novel": _counts(pred, t, ~copy)}
    return out


def truth(fold, split):
    """Targets and marks of one fold's points. Labels and windows only, no model output."""
    runs = fold["val_runs"] if split == "val" else fold["test_runs"]
    seen = fold["train_runs"] if split == "val" else fold["train_runs"] + fold["val_runs"]    # A1
    X, _, Y, owners, rows = data.windows(fold["_steps"], runs)
    seqs = data.bs.sequences(fold["_steps"])
    marks = data.bs.mark([seqs[r] for r in runs], [seqs[r] for r in seen])
    if [m["source_row"] for m in marks] != rows:
        raise SystemExit(f"{fold['fold']}: marks do not line up with the {split} windows")
    return {"y": Y, "rows": rows, "owners": owners, "marks": marks, "in_window": X.max(axis=1) > 0.5,
            "copy": np.array([m["copy"] for m in marks], bool)}


def side_file():
    """Protocol 1.1's pinned marks, by (condition, family, fold)."""
    out = {}
    with open(os.path.join(REPO, "camlds_real", "out", "sidecar", "points.jsonl"), encoding="utf-8") as fh:
        for line in fh:
            p = json.loads(line)
            out.setdefault((p["condition"], p["family"], p["fold"]), []).append(p)
    return out


def check_side_file(fold, tr, side):
    want = side[(fold["condition"], fold["family"], fold["fold"])]
    got = [{"source_row": m["source_row"], "copy": m["copy"], "targets": m["targets"]} for m in tr["marks"]]
    if got != [{"source_row": p["source_row"], "copy": p["copy"], "targets": p["targets"]} for p in want]:
        raise SystemExit(f"{fold['fold']}: test marks differ from protocol 1.1's side file")


def cell_dir(out, condition, arm, fold, seed):
    if arm == BASELINE:
        return os.path.join(out, "train", "main", "Transformer", fold, f"s{seed}")
    return RV.cell_path(out, condition, arm, fold, seed)


def load_cell(out, condition, arm, fold, seed, split, tr):
    """Logits and threshold of one training, after checking it is the complete, untouched one."""
    d = cell_dir(out, condition, arm, fold, seed)
    where = f"{condition} {arm} {fold} s{seed}"
    name = os.path.join(d, LOGITS[split])
    if not (os.path.exists(name) and os.path.exists(os.path.join(d, "result.json"))):
        raise SystemExit(f"{where}: output is missing")
    res = R.read_json(os.path.join(d, "result.json"))
    if split == "test":
        rec, rows = res["sealed_test"], res["sealed_test"]["source_rows"]
    else:
        side = res if arm != BASELINE else R.read_json(os.path.join(d, "val_outputs.json"))
        rec, rows = side["val"], side["val_source_rows"]
    if R.sha_file(name) != rec["sha256"]:
        raise SystemExit(f"{where}: file does not match its recorded fingerprint")
    if rows != tr["rows"]:
        raise SystemExit(f"{where}: its points are not the fold's points")
    if res["threshold"] not in Mx.THRESHOLD_GRID:
        raise SystemExit(f"{where}: threshold {res['threshold']} is not on the frozen grid")
    return np.load(name).astype(np.float64), res


def preflight(split, out, smoke, conditions, seeds):
    """Every output must exist before any is read, so a missing one can never leave a partial look."""
    for cond in conditions:
        for f in R.pick_folds(cond, smoke):
            for arm in ENCODERS + ((BASELINE,) if cond == "main" else ()):
                for s in seeds:
                    d = cell_dir(out, cond, arm, f["fold"], s)
                    if not (os.path.exists(os.path.join(d, LOGITS[split])) and os.path.exists(os.path.join(d, "result.json"))):
                        raise SystemExit(f"{cond} {arm} {f['fold']} s{s}: output is missing")


def score_all(split, out, smoke, conditions):
    """condition -> fold -> family, ceiling and per-seed scores of every arm."""
    seeds = SPEC.MAIN_SEEDS[:1] if smoke else SPEC.MAIN_SEEDS
    preflight(split, out, smoke, conditions, seeds)
    side, results, worst = (side_file() if split == "test" else None), {}, 0.0
    for cond in conditions:
        results[cond] = {}
        ceil = None
        for f in R.pick_folds(cond, smoke):
            if ceil is None:
                ceil = {g["fold"]: data.sp.ceiling(g) for fam in data.FAMILIES for g in data.sp.folds(f["_steps"], fam)}
            tr = truth(f, split)
            if split == "test":
                check_side_file(f, tr, side)
            arms = {}
            for arm in ENCODERS + ((BASELINE,) if cond == "main" else ()):
                arms[arm] = []
                for s in seeds:
                    lo, res = load_cell(out, cond, arm, f["fold"], s, split, tr)
                    if res.get("smoke") and not smoke:
                        raise SystemExit(f"{cond} {arm} {f['fold']} s{s}: this is a smoke run")
                    cell = score_cell(lo, res["threshold"], tr)
                    if split == "val":                 # must reproduce the score already on record
                        gap = abs(cell["all"]["micro_f1"] - res["validation"]["micro_f1"])
                        worst = max(worst, gap)
                        if gap > 1e-12:
                            raise SystemExit(f"{cond} {arm} {f['fold']} s{s}: dry run differs from the record")
                    arms[arm].append(cell)
            results[cond][f["fold"]] = {"family": f["family"], "n_points": len(tr["rows"]),
                                        "ceiling": {k: ceil[f["fold"]][k] for k in ("unseen_rate", "max_recall")},
                                        "arms": arms}
    return results, worst


# ── summaries ─────────────────────────────────────────────────────────────────

def per_fold(results, cond, family, arm, subset, metric):
    """fold -> mean over seeds. Folds with no such points are absent."""
    out = {}
    for fold, r in results[cond].items():
        if r["family"] != family or arm not in r["arms"]:
            continue
        vals = [c[subset][metric] for c in r["arms"][arm] if c[subset] is not None and c[subset][metric] is not None]
        if vals:
            out[fold] = float(np.mean(vals))
    return out


def _mean(fold_values, scenario=None):
    v = [x for f, x in fold_values.items() if scenario is None or f[0] == scenario]
    return float(np.mean(v)) if v else None


def selection_score(results, cond, arm, subset):
    """The score of SELECTION_RULE.md: micro-F1 pooled within 4 groups, groups weighted equally,
    then the mean over seeds."""
    n_seeds = len(next(iter(results[cond].values()))["arms"][arm])
    per_seed = []
    for i in range(n_seeds):
        groups = {}
        for fold, r in results[cond].items():
            c = r["arms"][arm][i]["counts"][subset]
            if c is not None:
                g = "scenario held out" if r["family"] == SCENARIO_FAMILY else f"S{fold[0]} variants"
                groups[g] = groups.get(g, np.zeros(3)) + np.array(c)
        per_seed.append(float(np.mean([Mx._prf(*v)[2] for v in groups.values()])))
    return float(np.mean(per_seed))


def summarise(results):
    S = {"encoders": {}, "contrasts": {}, "baseline": None}
    for cond in results:
        arms = ENCODERS
        S["encoders"][cond] = {}
        for arm in arms:
            row = {f"{m}|{sub}": _mean(per_fold(results, cond, FAMILY, arm, sub, m)) for m in METRICS for sub in SUBSETS}
            row.update({f"labels_{g}": _mean(per_fold(results, cond, FAMILY, arm, "labels", g)) for g in ("repeat", "new")})
            for sub in ("all", "novel"):
                fold_f1 = per_fold(results, cond, FAMILY, arm, sub, "micro_f1")
                row.update({f"scenario_{s}|{sub}": _mean(fold_f1, s) for s in SCENARIOS})
            S["encoders"][cond][arm] = row
        cs = {}
        for other in SECONDARY:
            cs[other] = contrast(per_fold(results, cond, FAMILY, PRIMARY, "all", "micro_f1"),
                                 per_fold(results, cond, FAMILY, other, "all", "micro_f1"))
        ps = [cs[o]["p"] for o in SECONDARY]
        if all(p is not None for p in ps):                     # Holm over the family of two
            for o, adj in zip(SECONDARY, holm(ps)):
                cs[o]["p_holm"] = adj
        for o in SECONDARY:
            cs[o]["verdict"] = verdict(cs[o], NAMES[PRIMARY], NAMES[o]) if cond == "main" else "sensitivity check, no claim"
        S["contrasts"][cond] = cs
    if "main" in results:
        out = {}
        for sub in ("all", "novel"):
            a = per_fold(results, "main", FAMILY, PRIMARY, sub, "micro_f1")
            b = per_fold(results, "main", FAMILY, BASELINE, sub, "micro_f1")
            folds = sorted(set(a) & set(b))
            out[sub] = {"new": _mean({f: a[f] for f in folds}), "old": _mean({f: b[f] for f in folds}),
                        "folds_better": int(sum(a[f] > b[f] for f in folds)), "n_folds": len(folds),
                        "per_scenario": {s: _mean({f: a[f] - b[f] for f in folds}, s) for s in SCENARIOS},
                        "selection_old": selection_score(results, "main", BASELINE, sub),
                        "selection_new": selection_score(results, "main", PRIMARY, sub)}
        S["baseline"] = out
    return S


def _f(x, spec=".3f"):
    return "n/a" if x is None else format(x, spec)


def report(results, S, title):
    log = [title, "Micro-F1 unless stated. Mean over the 10 seeds, then over the folds.", ""]
    say = log.append
    rows = [*[(f"{METRIC_NAMES[METRICS[0]]}, {sub}", f"{METRICS[0]}|{sub}") for sub in SUBSETS],
            ("Micro-F1, repeated labels", "labels_repeat"), ("Micro-F1, new labels", "labels_new"),
            *[(f"Micro-F1, S{s}, {sub}", f"scenario_{s}|{sub}") for sub in ("all", "novel") for s in SCENARIOS],
            *[(f"{METRIC_NAMES[m]}, {sub}", f"{m}|{sub}") for m in METRICS[1:] for sub in SUBSETS]]
    for cond in results:
        ceil = [r["ceiling"]["max_recall"] for r in results[cond].values() if r["family"] == FAMILY]
        n = sum(r["family"] == FAMILY for r in results[cond].values())
        say(f"== {cond}: variant held out, {n} folds =="
            + ("  (the primary result)" if cond == "main" else "  (beside the main result, never instead of it)"))
        say(f"  {'':<28}" + "".join(f"{NAMES[a]:>13}" for a in ENCODERS))
        for label, key in rows:
            say(f"  {label:<28}" + "".join(f"{_f(S['encoders'][cond][a][key]):>13}" for a in ENCODERS))
        say(f"  {'Recall ceiling, mean of folds':<28}{_f(float(np.mean(ceil))) if ceil else 'n/a':>13}   (labels unseen in training)")
        say("")
        say(f"  Transformer minus GRU / LSTM ({'family of two, Holm' if cond == 'main' else 'sensitivity check, no claim'})")
        for o in SECONDARY:
            c = S["contrasts"][cond][o]
            say(f"    vs {NAMES[o]:<5} mean {c['mean']:+.4f}  95% CI [{c['ci'][0]:+.4f}, {c['ci'][1]:+.4f}]  p {_f(c['p'], '.4f')}  "
                f"Holm p {_f(c.get('p_holm'), '.4f')}  folds Transformer ahead {c['folds_a_better']}/{c['n_folds']}  "
                + "  ".join(f"S{s} {v:+.3f}" for s, v in c["per_scenario"].items()))
            say(f"    -> {c['verdict']}")
        say("")
        scen = [(f, r) for f, r in results[cond].items() if r["family"] == SCENARIO_FAMILY]
        if scen:
            say(f"  Scenario held out, {len(scen)} folds, descriptive only (all points, recall ceiling beside each)")
            for f, r in scen:
                say(f"    {f:<4}" + "".join(f"  {NAMES[a]} {_f(float(np.mean([c['all']['micro_f1'] for c in r['arms'][a]])))}" for a in ENCODERS)
                    + f"  ceiling {_f(r['ceiling']['max_recall'])}")
            say("")
    if S["baseline"]:
        say("== Does the improvement hold? Transformer against the old Transformer, main condition, descriptive only ==")
        say("  The score that chose it (4 groups, equal weight, as SELECTION_RULE.md):")
        for sub, b in S["baseline"].items():
            say(f"    {sub:<6} points: old {_f(b['selection_old'], '.4f')} -> new {_f(b['selection_new'], '.4f')}")
        say("  Mean over the variant-held-out folds (18 of the 29 are S1):")
        for sub, b in S["baseline"].items():
            say(f"    {sub:<6} points: old {_f(b['old'])} -> new {_f(b['new'])}  folds better {b['folds_better']}/{b['n_folds']}  "
                + "  ".join(f"S{s} {_f(v, '+.3f')}" for s, v in b["per_scenario"].items()))
        say("")
    return "\n".join(log) + "\n"


def per_fold_report(results):
    log = ["Per fold: micro-F1 on all points, mean +/- SD over the seeds", ""]
    for cond in results:
        log.append(f"== {cond} ==")
        log.append(f"  {'fold':<32}" + "".join(f"{NAMES[a]:>18}" for a in ENCODERS) + f"{'ceiling':>9}")
        for fold, r in results[cond].items():
            cells = []
            for a in ENCODERS:
                v = [c["all"]["micro_f1"] for c in r["arms"][a]]
                cells.append(f"{np.mean(v):.3f} +/- {np.std(v, ddof=1) if len(v) > 1 else 0:.3f}")
            log.append(f"  {fold:<32}" + "".join(f"{c:>18}" for c in cells) + f"{r['ceiling']['max_recall']:>9.3f}")
        log.append("")
    return "\n".join(log) + "\n"


def open_gate(folder):
    """The test may be scored only after the freeze, and only once."""
    if os.path.exists(os.path.join(folder, RESULTS + ".json")):
        raise SystemExit("Stage 1 has already been opened. It is opened once.")
    r = subprocess.run([sys.executable, SPEC_1_2], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or "PROTOCOL 1.2 CHECK: PASS" not in r.stdout:
        raise SystemExit("Protocol 1.2 check did not pass; the test stays closed.\n" + r.stdout[-1500:])


def _write(folder, name, results, S, per_fold_text, text):
    R.write_json(os.path.join(folder, name + ".json"), {"summary": S, "results": results})
    for fname, content in ((name + ".txt", text), (name + "_PER_FOLD.txt", per_fold_text)):
        with open(os.path.join(folder, fname), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validation-dry-run", action="store_true")
    mode.add_argument("--open-test", action="store_true")
    ap.add_argument("--conditions", nargs="+", default=list(data.CONDITIONS), choices=data.CONDITIONS)
    ap.add_argument("--smoke", action="store_true", help="dry run on the smoke folder; NOT a result")
    a = ap.parse_args()
    out = os.path.join(HERE, "out_smoke" if a.smoke else "out")
    if a.open_test:
        if a.smoke or sorted(a.conditions) != sorted(data.CONDITIONS):
            raise SystemExit("--open-test scores every condition together, and never on smoke runs.")
        folder = os.path.join(HERE, TEST_DIR)
        open_gate(folder)
        results, _ = score_all("test", out, False, data.CONDITIONS)
        S, name = summarise(results), RESULTS
        title = "STAGE 1 RESULTS, protocol 1.2. TEST SPLIT, opened once."
    else:
        folder, name = out, DRY_NAME
        results, worst = score_all("val", out, a.smoke, a.conditions)
        S = summarise(results)
        title = (f"DRY RUN ON VALIDATION DATA. NOT A TEST RESULT. The code path of Stage 1, reproducing the "
                 f"recorded validation scores (largest difference {worst:.1e}).")
    text = report(results, S, title)
    os.makedirs(folder, exist_ok=True)
    _write(folder, name, results, S, per_fold_report(results), text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
