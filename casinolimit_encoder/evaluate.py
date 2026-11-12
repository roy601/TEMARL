# -*- coding: utf-8 -*-
"""PROTOCOL_CL_1.0.md, Section 7: score the CasinoLimit runs.

    python casinolimit_encoder/evaluate.py --validation-dry-run   # validation only; checks the scorer
    python casinolimit_encoder/evaluate.py --open-test            # ONCE, after the dry run passes
    python casinolimit_encoder/evaluate.py --open-test --smoke    # on out_smoke/; NOT a result

--validation-dry-run  scores the VALIDATION outputs with exactly the code that will score the test,
                      and checks every micro-F1 equals the one recorded at training time. No test
                      file is read. Writes out/DRY_RUN_VALIDATION.txt.
--open-test           refuses unless: the frozen files are unchanged (spec_cl.py), the dry run has
                      passed, every training and baseline output exists, and the test has not been
                      opened before. Then checks every test file's SHA-256 and alignment, scores,
                      and writes out_test/CL_RESULTS.{txt,json} and CL_RESULTS_PER_ATTACKER.csv.

Scoring (all fixed in Section 7):
  unit          the attacker: micro-F1 over the attacker's points, averaged over the 10 seeds
  subsets       all points; novel / copy points (copy = same window and target in the fold's other
                attackers); reviewed points (every label of the target step was labelled by a human
                reviewer and none is marked "doubt")
  family 1      Transformer, GRU, LSTM each vs the best simple baseline (3 comparisons)
  family 2      Transformer vs GRU, Transformer vs LSTM (2 comparisons)
  statistics    mean difference over attackers, 95% bootstrap CI (10,000 resamples of attackers,
                seed 20261103), two-sided Wilcoxon signed-rank, Holm within each family and table.
                "X outperforms Y" only if Holm p < 0.05 AND the CI excludes 0.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import os
import sys
import time

import numpy as np
import scipy
import scipy.stats as sps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cl_data as CD  # noqa: E402
import cl_split as S  # noqa: E402
import lookup as LK  # noqa: E402
from cl_port import NT, STEPS, Mx, SPEC  # noqa: E402

ENCODERS = ("allpos", "gru_allpos", "lstm_allpos")
BASELINE = "baseline"                                  # descriptive only
SIMPLE = "simple"                                      # best simple baseline per fold (Section 4)
MODELS = (*ENCODERS, BASELINE, SIMPLE, *LK.RULES)
NAMES = {"allpos": "Transformer", "gru_allpos": "GRU", "lstm_allpos": "LSTM", "baseline": "Old Transformer",
         "simple": "Best simple baseline", "longest": "Lookup, longest match", "previous": "Lookup, previous step",
         "repeat_last": "Repeat last step"}
FAMILY_1 = [("allpos", SIMPLE), ("gru_allpos", SIMPLE), ("lstm_allpos", SIMPLE)]
FAMILY_2 = [("allpos", "gru_allpos"), ("allpos", "lstm_allpos")]
SUBSETS = ("all", "novel", "copy", "reviewed")
PRIMARY = ("main", "all")
ALPHA, BOOTSTRAP_RESAMPLES, BOOTSTRAP_SEED = 0.05, 10_000, 20261103
RESULTS = "CL_RESULTS"
DRY_RUN = "DRY_RUN_VALIDATION"


# ── statistics (as camlds_encoder/evaluate_test.py, with the attacker as the unit) ──

def bootstrap_ci(d):
    d = np.asarray(d, np.float64)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    means = d[rng.integers(0, len(d), (BOOTSTRAP_RESAMPLES, len(d)))].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def wilcoxon_p(d):
    d = np.asarray(d, np.float64)
    if np.count_nonzero(d) < 2:
        return None
    return float(sps.wilcoxon(d, zero_method="wilcox", correction=False, alternative="two-sided",
                              method="auto").pvalue)


def holm(ps):
    order, adj, running = np.argsort(ps), [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = running
    return adj


def contrast(a: dict, b: dict) -> dict:
    """a, b: attacker -> value. Difference a - b over the attackers both have."""
    keys = sorted(set(a) & set(b))
    d = np.array([a[k] - b[k] for k in keys])
    lo, hi = bootstrap_ci(d)
    return {"mean": float(d.mean()), "ci": [lo, hi], "p": wilcoxon_p(d), "n_attackers": len(keys),
            "attackers_a_better": int((d > 0).sum()), "attackers_b_better": int((d < 0).sum())}


def family(rows: dict, pairs) -> list[dict]:
    out = [{"a": a, "b": b, **contrast(rows[a], rows[b])} for a, b in pairs]
    ps = [c["p"] if c["p"] is not None else 1.0 for c in out]
    for c, ph in zip(out, holm(ps)):
        c["p_holm"] = ph
        c["verdict"] = verdict(c)
    return out


def verdict(c) -> str:
    excludes_zero = c["ci"][0] > 0 or c["ci"][1] < 0
    if not (excludes_zero and c["p_holm"] < ALPHA):
        return "no difference shown"
    win, lose = (c["a"], c["b"]) if c["mean"] > 0 else (c["b"], c["a"])
    return f"{NAMES[win]} outperforms {NAMES[lose]}"


# ── truth and point flags ────────────────────────────────────────────────────

def truth(fold: dict, split: str) -> dict:
    """Targets and flags of one fold's validation or test points, in window order."""
    st = fold["_steps"]
    runs = fold["val_runs"] if split == "val" else fold["test_runs"]
    seen_runs = fold["train_runs"] if split == "val" else fold["train_runs"] + fold["val_runs"]
    _, _, Y, owners, rows = CD.windows(st, runs)
    seqs = CD.sequences(st, runs)
    marks = CD.mark(CD.label_seqs(st, runs), CD.label_seqs(st, seen_runs))
    target_steps = [q[i] for q in seqs.values() for i in range(1, len(q))]
    if not (len(marks) == len(target_steps) == len(Y) == len(rows)):
        raise SystemExit(f"{fold['fold']} {split}: points do not line up")
    if [s["source_row"] for s in target_steps] != rows or [m["run"] for m in marks] != owners:
        raise SystemExit(f"{fold['fold']} {split}: point order differs")
    copy = np.array([m["copy"] for m in marks], bool)
    reviewed = np.array(["auto-triggers" not in s["labelled_by"] and not s["doubt"] for s in target_steps], bool)
    train_runs = set(fold["train_runs"])
    train_labels = {t for s in st if s["run"] in train_runs for t in s["techniques_parent"]}
    return {"Y": Y, "owners": np.array(owners), "rows": rows,
            "subset": {"all": np.ones(len(Y), bool), "novel": ~copy, "copy": copy, "reviewed": reviewed},
            "unseen_label_slots": sum(t not in train_labels for s in target_steps for t in s["techniques_parent"]),
            "label_slots": int(Y.sum())}


def counts(pred: np.ndarray, Y: np.ndarray):
    t = Y > 0.5
    return (pred & t).sum(1), (pred & ~t).sum(1), (~pred & t).sum(1)


def f1(tp, fp, fn):
    return 0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn)


# ── loading ──────────────────────────────────────────────────────────────────

def cell_dir(out, cond, model, fold, seed):
    return os.path.join(out, "train", cond, model, fold, f"s{seed}")


def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def seeds_for(smoke):
    return SPEC.MAIN_SEEDS[:1] if smoke else SPEC.MAIN_SEEDS


def folds_for(cond, smoke):
    fs = CD.folds(cond)
    return [f for f in fs if f["fold"] in ("F1", "F2")] if smoke else fs


def preflight(out, smoke, split):
    """Every output must exist before any is read."""
    missing = []
    for cond in S.CONDITIONS:
        for f in folds_for(cond, smoke):
            for m in (*ENCODERS, BASELINE):
                for s in seeds_for(smoke):
                    d = cell_dir(out, cond, m, f["fold"], s)
                    for name in ("result.json", f"{split}_logits.npy"):
                        if not os.path.exists(os.path.join(d, name)):
                            missing.append(os.path.join(d, name))
            lk = os.path.join(out, "lookup", cond, f["fold"])
            for name in ("result.json", *[f"{split}_{r}.npy" for r in LK.RULES]):
                if not os.path.exists(os.path.join(lk, name)):
                    missing.append(os.path.join(lk, name))
    if missing:
        raise SystemExit(f"{len(missing)} outputs missing, e.g. {missing[:3]}. Finish run.py first.")
    if not smoke and read_json(os.path.join(out, "budget.json")).get("smoke"):
        raise SystemExit("budget.json is from a smoke run.")


def predictions(out, cond, fold, split, tr, smoke):
    """model -> list over seeds of (pred 0/1 matrix, logits or None). Checks hashes and alignment."""
    key = "val" if split == "val" else "sealed_test"
    preds, checks = {}, []
    for m in (*ENCODERS, BASELINE):
        preds[m] = []
        for s in seeds_for(smoke):
            d = cell_dir(out, cond, m, fold["fold"], s)
            rec = read_json(os.path.join(d, "result.json"))
            if rec.get("smoke", False) != smoke:
                raise SystemExit(f"{d}: smoke flag does not match")
            path = os.path.join(d, f"{split}_logits.npy")
            if sha_file(path) != rec[key]["sha256"]:
                raise SystemExit(f"{path}: SHA-256 differs from result.json")
            rows = rec["val_source_rows"] if split == "val" else rec["sealed_test"]["source_rows"]
            if rows != tr["rows"]:
                raise SystemExit(f"{d}: {split} points differ from the corpus")
            if rec["threshold"] not in SPEC.THRESHOLD_GRID:
                raise SystemExit(f"{d}: threshold {rec['threshold']} not in the frozen grid")
            lo = np.load(path).astype(np.float64)
            if lo.shape != tr["Y"].shape:
                raise SystemExit(f"{path}: shape {lo.shape}, expected {tr['Y'].shape}")
            pred = Mx._sigmoid(lo) >= rec["threshold"]
            preds[m].append((pred, lo))
            if split == "val":
                checks.append(abs(Mx.threshold_metrics(Mx._sigmoid(lo), tr["Y"], rec["threshold"])["micro_f1"]
                                  - rec["validation"]["micro_f1"]))
    lk_dir = os.path.join(out, "lookup", cond, fold["fold"])
    lk = read_json(os.path.join(lk_dir, "result.json"))
    if lk.get("smoke", False) != smoke:
        raise SystemExit(f"{lk_dir}: smoke flag does not match")
    for r in LK.RULES:
        rows = lk["val_source_rows"] if split == "val" else lk[f"sealed_test_{r}"]["source_rows"]
        if rows != tr["rows"]:
            raise SystemExit(f"{lk_dir}: {split} points of {r} differ from the corpus")
        path = os.path.join(lk_dir, f"{split}_{r}.npy")
        meta = lk[f"val_{r}"] if split == "val" else lk[f"sealed_test_{r}"]
        if sha_file(path) != meta["sha256"]:
            raise SystemExit(f"{path}: SHA-256 differs from result.json")
        p = np.load(path) >= 0.5
        if p.shape != tr["Y"].shape:
            raise SystemExit(f"{path}: shape mismatch")
        preds[r] = [(p, None)]
        if split == "val":
            checks.append(abs(Mx.threshold_metrics(p.astype(np.float64), tr["Y"], 0.5)["micro_f1"]
                              - lk["validation_micro_f1"][r]))
    preds[SIMPLE] = preds[lk["comparator"]]
    return preds, lk["comparator"], checks


# ── scoring ──────────────────────────────────────────────────────────────────

def score(out, split, smoke):
    """Everything Section 7 reports, for one split ('val' = dry run, 'test')."""
    res = {"split": split, "conditions": {}, "max_recorded_difference": 0.0}
    for cond in S.CONDITIONS:
        att = {sub: {m: collections.defaultdict(list) for m in MODELS} for sub in SUBSETS}  # attacker -> per-seed F1
        pooled = {sub: {m: collections.defaultdict(lambda: np.zeros(3)) for m in MODELS} for sub in SUBSETS}
        stacks = {m: collections.defaultdict(list) for m in MODELS}       # seed -> [(pred, Y, logits)]
        comparators, ceiling = {}, [0, 0]
        for f in folds_for(cond, smoke):
            tr = truth(f, split)
            ceiling[0] += tr["unseen_label_slots"]
            ceiling[1] += tr["label_slots"]
            preds, comp, checks = predictions(out, cond, f, split, tr, smoke)
            comparators[f["fold"]] = comp
            res["max_recorded_difference"] = max([res["max_recorded_difference"], *checks])
            for m in MODELS:
                for s, (pred, lo) in enumerate(preds[m]):
                    tp, fp, fn = counts(pred, tr["Y"])
                    stacks[m][s].append((pred, tr["Y"], lo, tr["subset"]))
                    for sub in SUBSETS:
                        sel = tr["subset"][sub]
                        pooled[sub][m][s] += [tp[sel].sum(), fp[sel].sum(), fn[sel].sum()]
                        for a in np.unique(tr["owners"][sel]):
                            ix = sel & (tr["owners"] == a)
                            att[sub][m][a].append(f1(tp[ix].sum(), fp[ix].sum(), fn[ix].sum()))
        block = {"comparator_per_fold": comparators,
                 "recall_ceiling": 1 - ceiling[0] / max(ceiling[1], 1), "subsets": {}}
        for sub in SUBSETS:
            per_att = {m: {a: float(np.mean(v)) for a, v in att[sub][m].items()} for m in MODELS}
            table = {}
            for m in MODELS:
                pooled_f1 = [f1(*c) for c in pooled[sub][m].values()]
                extra = secondary(stacks[m], sub)
                table[m] = {"pooled_micro_f1": float(np.mean(pooled_f1)), "attacker_mean_micro_f1":
                            float(np.mean(list(per_att[m].values()))) if per_att[m] else None,
                            "n_attackers": len(per_att[m]), "n_seeds": len(pooled_f1), **extra}
            block["subsets"][sub] = {"n_points": int(sum(len(x[1][x[3][sub]]) for x in stacks[ENCODERS[0]][0])),
                                     "models": table, "per_attacker": per_att,
                                     "family_1": family(per_att, FAMILY_1), "family_2": family(per_att, FAMILY_2)}
        res["conditions"][cond] = block
    return res


def secondary(stack_by_seed, sub):
    """Pooled macro-F1, exact-set accuracy and BCE (encoders only), mean over seeds; frozen metric code."""
    macro, exact, bce = [], [], []
    for parts in stack_by_seed.values():
        pred = np.concatenate([p[0][p[3][sub]] for p in parts])
        Y = np.concatenate([p[1][p[3][sub]] for p in parts])
        if not len(Y):
            continue
        m = Mx.threshold_metrics(pred.astype(np.float64), Y, 0.5)
        macro.append(m["macro_f1"])
        exact.append(m["exact_set_accuracy"])
        if parts[0][2] is not None:
            bce.append(Mx.bce(np.concatenate([p[2][p[3][sub]] for p in parts]), Y))
    return {"macro_f1": float(np.mean(macro)) if macro else None,
            "exact_set_accuracy": float(np.mean(exact)) if exact else None,
            "bce": float(np.mean(bce)) if bce else None}


# ── report ───────────────────────────────────────────────────────────────────

def _f(x, spec=".3f"):
    return "-" if x is None else format(x, spec)


def report(res, title):
    L = [title, f"made {time.strftime('%Y-%m-%d %H:%M')} | scipy {scipy.__version__} | labels {NT}", ""]
    for cond, block in res["conditions"].items():
        for sub, b in block["subsets"].items():
            star = "  <- PRIMARY" if (cond, sub) == PRIMARY else ""
            L += [f"== {cond} | {sub} points ({b['n_points']:,} points){star}",
                  f"   {'model':<24}{'micro-F1':>10}{'per-attacker':>14}{'macro-F1':>10}{'exact set':>11}{'BCE':>8}"]
            for m in MODELS:
                t = b["models"][m]
                L.append(f"   {NAMES[m]:<24}{_f(t['pooled_micro_f1']):>10}{_f(t['attacker_mean_micro_f1']):>14}"
                         f"{_f(t['macro_f1']):>10}{_f(t['exact_set_accuracy']):>11}{_f(t['bce']):>8}")
            for fam in ("family_1", "family_2"):
                for c in b[fam]:
                    L.append(f"   {NAMES[c['a']]} - {NAMES[c['b']]}: {c['mean']:+.3f} "
                             f"[{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}]  p {_f(c['p'], '.4f')}  Holm {_f(c['p_holm'], '.4f')}"
                             f"  better in {c['attackers_a_better']}/{c['n_attackers']} attackers -> {c['verdict']}")
            L.append("")
        L += [f"   {cond}: best simple baseline per fold: {block['comparator_per_fold']}",
              f"   {cond}: recall ceiling (test label slots whose label occurs in the fold's training): "
              f"{block['recall_ceiling']:.3f}", ""]
    L.append("micro-F1 = pooled over all points of all folds, mean over seeds. per-attacker = mean over attackers "
             "(the unit of the tests). Differences are per-attacker micro-F1.")
    return "\n".join(L) + "\n"


def per_attacker_csv(res, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["condition", "subset", "attacker", *MODELS])
        for cond, block in res["conditions"].items():
            for sub, b in block["subsets"].items():
                for a in sorted(b["per_attacker"][ENCODERS[0]]):
                    w.writerow([cond, sub, a, *[_f(b["per_attacker"][m].get(a), ".6f") for m in MODELS]])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--validation-dry-run", action="store_true")
    g.add_argument("--open-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    out = os.path.join(HERE, "out_smoke" if a.smoke else "out")
    if not a.smoke:
        import spec_cl
        if spec_cl.check() != 0:
            raise SystemExit("Frozen files changed (spec_cl.py). Stop.")
    if a.validation_dry_run:
        preflight(out, a.smoke, "val")
        res = score(out, "val", a.smoke)
        ok = res["max_recorded_difference"] < 1e-9
        text = report(res, "CASINOLIMIT: VALIDATION DRY RUN (validation only; no test file read)"
                      + ("  SMOKE: NOT A RESULT" if a.smoke else ""))
        text += (f"\nEvery validation micro-F1 recomputed here equals the one recorded at training time "
                 f"(largest difference {res['max_recorded_difference']:.2e}): {'PASS' if ok else 'FAIL'}\n")
        with open(os.path.join(out, f"{DRY_RUN}.txt"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        with open(os.path.join(out, f"{DRY_RUN}.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"pass": ok, "max_recorded_difference": res["max_recorded_difference"]}, fh, indent=1)
        print(text)
        return 0 if ok else 1
    folder = os.path.join(out, "eval") if a.smoke else os.path.join(HERE, "out_test")
    if os.path.exists(os.path.join(folder, f"{RESULTS}.json")):
        raise SystemExit(f"The test has already been opened ({folder}). It is never scored twice.")
    dry = os.path.join(out, f"{DRY_RUN}.json")
    if not (os.path.exists(dry) and read_json(dry)["pass"]):
        raise SystemExit("Run --validation-dry-run first; it must PASS.")
    preflight(out, a.smoke, "test")
    res = score(out, "test", a.smoke)
    os.makedirs(folder, exist_ok=True)
    text = report(res, "CASINOLIMIT: TEST RESULTS (PROTOCOL_CL_1.0.md)" + ("  SMOKE: NOT A RESULT" if a.smoke else ""))
    per_attacker_csv(res, os.path.join(folder, f"{RESULTS}_PER_ATTACKER.csv"))
    with open(os.path.join(folder, f"{RESULTS}.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    with open(os.path.join(folder, f"{RESULTS}.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, indent=1)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
