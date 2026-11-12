# -*- coding: utf-8 -*-
"""Independent audit, 2026-11-11. Rebuilds the study from the authors' CSV with its own code.

    python report/audit/independent_audit.py

Parts 1-7 import nothing from the project: the CSV parser, sequences, labels, folds, windows, copy
marks, metrics and statistics are written again here. They are then compared with what the project
stored (steps.jsonl, vocab.json, side file, result.json, STAGE1_RESULTS.json). Part 8 imports the
project's data module only to compare the model-input arrays bit for bit.

It changes no project file. Test outputs are read: Stage 1 was opened on 2026-11-10.
"""
import collections
import csv
import hashlib
import json
import os
import re
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(REPO, *a)
OUT = P("camlds_encoder", "out")
W, GRID, SEEDS = 16, (0.1, 0.2, 0.3, 0.4, 0.5), tuple(range(10))
MIN_DELTA, VAL_EVERY = 1e-4, 64
checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{'  ' + str(detail) if detail else ''}")


def head(t):
    print(f"\n== {t} ==")


# ── 1. the CSV, parsed from scratch ───────────────────────────────────────────
head("1. Source file and sequences")
raw = open(P("camlds_real", "attack_times.csv"), "rb").read()
print("  attack_times.csv sha256", hashlib.sha256(raw).hexdigest())
rows = list(csv.DictReader(raw.decode("utf-8").splitlines(), delimiter=";"))
check("904 data rows, 8 columns", len(rows) == 904 and len(rows[0]) == 8, f"{len(rows)} rows")
TECH = re.compile(r"^T\d{4}(\.\d{3})?$")
bad = [r for r in rows if not r["techniques"] or any(not TECH.match(t) for t in r["techniques"].split("_"))]
check("every row has valid technique IDs", not bad, f"{len(bad)} bad")
check("no empty field, no duplicate row", all(all(v != "" for v in r.values()) for r in rows)
      and len({tuple(r.values()) for r in rows}) == 904)
for i, r in enumerate(rows):
    r["i"] = i
    r["sub"] = r["techniques"].split("_")
    r["par"] = tuple(sorted({t.split(".")[0] for t in r["sub"]}))
    r["t0"] = float(r["start"])
by_run = collections.defaultdict(list)
for r in rows:
    by_run[r["scenario"]].append(r)
SEQ = {run: sorted(rs, key=lambda r: (r["t0"], int(r["event_id"]))) for run, rs in by_run.items()}
scen = lambda run: run.split("_")[0]
check("34 runs in 7 scenarios", len(SEQ) == 34 and len({scen(r) for r in SEQ}) == 7)
check("no two steps of a run start at the same time",
      all(len({r["t0"] for r in s}) == len(s) for s in SEQ.values()))
LABELS = sorted({t for r in rows for t in r["par"]})
check("81 parent techniques from 97 sub-techniques",
      len(LABELS) == 81 and len({t for r in rows for t in r["sub"]}) == 97)
for s in SEQ.values():                                   # occurrence of each (run, event_id), in time order
    seen = collections.Counter()
    for r in s:
        seen[r["event_id"]] += 1
        r["occ"] = seen[r["event_id"]]
n_rep = sum(r["occ"] > 1 for r in rows)
check("21 repeated executions, 883 steps without them", n_rep == 21 and 904 - n_rep == 883)

head("2. Compared with the project's stored corpus")
steps = [json.loads(l) for l in open(P("camlds_real", "out", "steps.jsonl"), encoding="utf-8")]
vocab = json.load(open(P("camlds_real", "out", "vocab.json"), encoding="utf-8"))["parent_techniques"]
check("vocab.json equals the 81 labels rebuilt here, same order", vocab == LABELS)
st_run = collections.defaultdict(list)
for s in steps:
    st_run[s["run"]].append(s)
off = steps[0]["source_row"] - SEQ[steps[0]["run"]][0]["i"] if steps[0]["exec_index"] == 0 else None
same = len(steps) == 904 and set(st_run) == set(SEQ)
for run, mine in SEQ.items():
    theirs = sorted(st_run[run], key=lambda s: s["exec_index"])
    same &= len(theirs) == len(mine) and all(
        tuple(sorted(a["techniques_parent"])) == b["par"] and a["source_row"] - b["i"] == off
        and a["occurrence"] == b["occ"] and int(a["event_id"]) == int(b["event_id"]) for a, b in zip(theirs, mine))
check("steps.jsonl: same runs, same order, same labels, same row links, same repeat marks", same)
ID = {t: k for k, t in enumerate(LABELS)}
ROW = {r["i"] + off: r for r in rows}                    # project's source_row -> my row


# ── 3. folds, rebuilt from the written rule ───────────────────────────────────
def sequences(condition):
    return {run: [r for r in s if condition == "main" or r["occ"] == 1] for run, s in SEQ.items()}


def val_rule(train_runs):
    by = collections.defaultdict(list)
    for r in train_runs:
        by[scen(r)].append(r)
    return sorted(sorted(v)[0] for v in by.values() if len(v) >= 2)


def folds():
    out = []
    for b in ("1", "2", "3", "6"):                       # scenarios with more than one run
        runs = sorted(r for r in SEQ if scen(r) == b)
        for r in runs:
            pool = [x for x in runs if x != r]
            va = val_rule(pool)
            if va:                                       # a fold with no validation run is excluded
                out.append({"family": "variant_held_out", "fold": r, "test": [r], "val": va,
                            "train": [x for x in pool if x not in va]})
    for b in ("2", "3", "6"):
        pool = sorted(r for r in SEQ if scen(r) != b)
        va = val_rule(pool)
        out.append({"family": "scenario_held_out", "fold": f"S{b}", "test": sorted(r for r in SEQ if scen(r) == b),
                    "val": va, "train": [x for x in pool if x not in va]})
    return out


head("3. Folds")
FOLDS = folds()
single = sorted(b for b in {scen(r) for r in SEQ} if sum(scen(r) == b for r in SEQ) == 1)
check("29 variant folds + 3 scenario folds", [f["family"] for f in FOLDS].count("variant_held_out") == 29 and len(FOLDS) == 32,
      f"single-run scenarios {single}")
check("train, validation and test runs never overlap, in every fold",
      all(not (set(f["train"]) & set(f["val"])) and not (set(f["test"]) & (set(f["train"]) | set(f["val"]))) for f in FOLDS))
check("every fold has training and validation runs", all(f["train"] and f["val"] for f in FOLDS))
check("a variant fold trains only on other runs of the same scenario",
      all({scen(r) for r in f["train"] + f["val"]} == {scen(f["fold"])} for f in FOLDS if f["family"] == "variant_held_out"))
check("a scenario fold never trains on the tested scenario",
      all(f["fold"][1:] not in {scen(r) for r in f["train"] + f["val"]} for f in FOLDS if f["family"] == "scenario_held_out"))


# ── 4. windows, targets and marks ─────────────────────────────────────────────
def build(seqs, runs):
    X, M, Y, rws, wins = [], [], [], [], []
    for run in sorted(runs):
        s = seqs[run]
        for t in range(1, len(s)):
            hist = s[max(0, t - W):t]
            x, m = np.zeros((W, 81), np.float32), np.zeros(W, np.float32)
            for k, r in enumerate(hist):
                x[W - len(hist) + k, [ID[a] for a in r["par"]]] = 1
                m[W - len(hist) + k] = 1
            y = np.zeros(81, np.float32)
            y[[ID[a] for a in s[t]["par"]]] = 1
            X.append(x), M.append(m), Y.append(y), rws.append(s[t]["i"] + off)
            wins.append((tuple(r["par"] for r in hist), s[t]["par"]))
    return np.array(X), np.array(M), np.array(Y), rws, wins


head("4. Prediction points, copies and repeats (labels only, no model output)")
DATA = {}
for cond in ("main", "collapse_repeats"):
    seqs = sequences(cond)
    for f in FOLDS:
        d = {k: build(seqs, f[k]) for k in ("train", "val", "test")}
        seen = set(d["train"][4]) | set(d["val"][4])
        d["copy"] = np.array([w in seen for w in d["test"][4]])
        d["val_copy"] = np.array([w in set(d["train"][4]) for w in d["val"][4]])
        d["in_window"] = d["test"][0].max(axis=1) > 0.5
        DATA[cond, f["fold"]] = d
allp = build(sequences("main"), list(SEQ))
check("870 prediction points, 1,270 target labels, 600 of them already in the window",
      len(allp[2]) == 870 and int(allp[2].sum()) == 1270 and int((allp[2] * allp[0].max(axis=1)).sum()) == 600)
var = [f for f in FOLDS if f["family"] == "variant_held_out"]
n_pts = sum(len(DATA["main", f["fold"]]["copy"]) for f in var)
n_copy = sum(int(DATA["main", f["fold"]]["copy"].sum()) for f in var)
check("variant family: 790 test points, 425 copies (53.8%)", (n_pts, n_copy) == (790, 425), f"{n_pts}, {n_copy}")
check("scenario family: 331 test points, 0 copies",
      sum(len(DATA["main", f["fold"]]["copy"]) for f in FOLDS if f not in var) == 331
      and sum(int(DATA["main", f["fold"]]["copy"].sum()) for f in FOLDS if f not in var) == 0)
side = collections.defaultdict(list)
for line in open(P("camlds_real", "out", "sidecar", "points.jsonl"), encoding="utf-8"):
    p = json.loads(line)
    side[p["condition"], p["fold"]].append(p)
ok = True
for (cond, fold), d in DATA.items():
    sp_ = side[cond, fold]
    ok &= [p["source_row"] for p in sp_] == d["test"][3] and [p["copy"] for p in sp_] == d["copy"].tolist()
    for p, y, iw in zip(sp_, d["test"][2], d["in_window"]):
        ok &= sorted(t["label"] for t in p["targets"]) == sorted(LABELS[j] for j in np.where(y > 0.5)[0])
        ok &= all(t["repeat"] == bool(iw[ID[t["label"]]]) for t in p["targets"])
check("the project's side file agrees on every point: rows, targets, copy and repeat marks (2,212 points)", ok,
      f"{sum(len(v) for v in side.values())} points")


# ── 5. model outputs: thresholds, stopping, seeds ─────────────────────────────
def cell(cond, arm, fold, seed):
    if arm == "baseline":
        return os.path.join(OUT, "train", "main", "Transformer", fold, f"s{seed}")
    return os.path.join(OUT, "variants" if cond == "main" else "variants_collapse_repeats", arm, fold, f"s{seed}")


def sig(z):
    return 1.0 / (1.0 + np.exp(-z.astype(np.float64)))


def tpfpfn(pred, t, sel=None, lab=None):
    if sel is not None:
        pred, t = pred[sel], t[sel]
        lab = lab[sel] if lab is not None else None
    if lab is not None:
        return np.array([(pred & t & lab).sum(), (pred & ~t & lab).sum(), (~pred & t & lab).sum()], float)
    return np.array([(pred & t).sum(), (pred & ~t).sum(), (~pred & t).sum()], float)


def f1(c):
    return 0.0 if c[0] == 0 else 2 * c[0] / (2 * c[0] + c[1] + c[2])


def replay(curve, patience=16):
    best, since, best_u = float("inf"), 0, None
    for p in curve:
        v = p["validation_bce"]
        if v < best:
            gain, best, best_u = best - v, v, p["update"]
            since = 0 if gain > MIN_DELTA else since + 1
        else:
            since += 1
        if since >= patience:
            return p["update"], best_u, best
    return curve[-1]["update"], best_u, best


head("5. Every training (2,240): threshold from validation only, stopping rule, seeds")
ARMS = {"main": ("allpos", "gru_allpos", "lstm_allpos", "baseline"), "collapse_repeats": ("allpos", "gru_allpos", "lstm_allpos")}
LIMIT = {("main", "allpos"): 9152, ("main", "baseline"): 9152}
RES, n_cells, th_bad, stop_bad, row_bad, fin_bad, dup = {}, 0, 0, 0, 0, 0, 0
for cond, arms in ARMS.items():
    for f in FOLDS:
        d = DATA[cond, f["fold"]]
        for arm in arms:
            shas = set()
            for s in SEEDS:
                c = cell(cond, arm, f["fold"], s)
                r = json.load(open(os.path.join(c, "result.json"), encoding="utf-8"))
                vrows = r["val_source_rows"] if arm != "baseline" else json.load(
                    open(os.path.join(c, "val_outputs.json"), encoding="utf-8"))["val_source_rows"]
                lv, lt = np.load(os.path.join(c, "val_logits.npy")), np.load(os.path.join(c, "test_logits.npy"))
                shas.add(hashlib.sha256(lt.tobytes()).hexdigest())
                row_bad += vrows != d["val"][3] or r["sealed_test"]["source_rows"] != d["test"][3]
                fin_bad += not (np.isfinite(lv).all() and np.isfinite(lt).all() and lt.shape == (len(d["test"][3]), 81))
                pv, tv = sig(lv), d["val"][2] > 0.5
                best_t, best_f = None, -1.0
                for t in GRID:                               # the frozen rule: best micro-F1, ties to the smallest
                    fv = f1(tpfpfn(pv >= t, tv))
                    if fv > best_f + 1e-12:
                        best_t, best_f = t, fv
                th_bad += best_t != r["threshold"]
                stop, best_u, best_v = replay(r["curve"])
                lim = LIMIT.get((cond, arm), 18304)
                stop_bad += not (min(stop, lim) == r["updates_completed"] and best_u == r["best_update"]
                                 and abs(best_v - r["best_validation_bce"]) < 1e-12)
                RES[cond, arm, f["fold"], s] = (sig(lt) >= r["threshold"], sig(lt))
                n_cells += 1
            dup += len(shas) != len(SEEDS)
check("all trainings present and readable", n_cells == 2240, f"{n_cells}")
check("each output lines up with the points rebuilt here; no NaN", row_bad == 0 and fin_bad == 0)
check("each threshold is exactly the validation-best one by the frozen rule", th_bad == 0, f"{th_bad} differ")
check("each training stopped exactly where the patience rule says, and kept its validation-best update",
      stop_bad == 0, f"{stop_bad} differ")
check("the 10 seeds of a fold give 10 different outputs (no seed reused)", dup == 0, f"{dup} repeated")


# ── 6. test scores, computed again ────────────────────────────────────────────
def fold_scores(cond, arm, subset):
    out = {}
    for f in FOLDS:
        d = DATA[cond, f["fold"]]
        sel = {"all": np.ones(len(d["copy"]), bool), "novel": ~d["copy"], "copy": d["copy"]}[subset]
        if sel.any():
            t = d["test"][2] > 0.5
            out[f["fold"]] = float(np.mean([f1(tpfpfn(RES[cond, arm, f["fold"], s][0], t, sel)) for s in SEEDS]))
    return out


VAR = [f["fold"] for f in var]
mean_var = lambda sc: float(np.mean([sc[k] for k in VAR if k in sc]))
head("6. Stage 1 test scores, recomputed with this file's own metric code")
stage1 = json.load(open(P("camlds_encoder", "out_test", "STAGE1_RESULTS.json"), encoding="utf-8"))["summary"]
worst, table = 0.0, {}
for cond, arms in ARMS.items():
    for arm in arms:
        for sub in ("all", "novel", "copy"):
            mine = mean_var(fold_scores(cond, arm, sub))
            table[cond, arm, sub] = mine
            if arm != "baseline":
                worst = max(worst, abs(mine - stage1["encoders"][cond][arm][f"micro_f1|{sub}"]))
print("  main, variant held out:   " + "   ".join(
    f"{a} all {table['main', a, 'all']:.3f} novel {table['main', a, 'novel']:.3f}" for a in ARMS["main"]))
print("  collapse_repeats:         " + "   ".join(
    f"{a} all {table['collapse_repeats', a, 'all']:.3f} novel {table['collapse_repeats', a, 'novel']:.3f}"
    for a in ARMS["collapse_repeats"]))
check("micro-F1 on all, novel and copy points equals the published Stage 1 file (18 numbers)", worst < 1e-9,
      f"largest difference {worst:.1e}")
b = stage1["baseline"]
check("old Transformer: fold means equal the published ones",
      abs(table["main", "baseline", "all"] - b["all"]["old"]) < 1e-9 and abs(table["main", "baseline", "novel"] - b["novel"]["old"]) < 1e-9)
print("  scenario held out (all points):")
for f in FOLDS:
    if f["family"] == "scenario_held_out":
        d = DATA["main", f["fold"]]
        t = d["test"][2] > 0.5
        seen_l = d["train"][2].sum(0) + d["val"][2].sum(0) + d["train"][0].sum((0, 1)) + d["val"][0].sum((0, 1)) > 0
        ceil = float((t & seen_l).sum() / t.sum())
        top5 = np.mean([np.mean([(t[i, np.argsort(-RES['main', 'allpos', f['fold'], s][1][i])[:5]]).sum() / t[i].sum()
                                 for i in range(len(t))]) for s in SEEDS])
        print(f"    {f['fold']}: " + "  ".join(f"{a} {fold_scores('main', a, 'all')[f['fold']]:.3f}" for a in ARMS['main'][:3])
              + f"  | Transformer recall@5 {top5:.3f} | ceiling {ceil:.3f}")


# ── 7. statistics, computed again ─────────────────────────────────────────────
def wilcoxon_exact(d):
    """Exact two-sided signed-rank p by counting all sign patterns (ties get mid-ranks)."""
    d = np.array([x for x in d if x != 0.0])
    a = np.abs(d)
    order = np.argsort(a)
    ranks2 = np.empty(len(a), int)
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and a[order[j + 1]] == a[order[i]]:
            j += 1
        ranks2[order[i:j + 1]] = i + j + 2                 # twice the mid-rank, an integer
        i = j + 1
    total = int(ranks2.sum())
    ways = np.zeros(total + 1)
    ways[0] = 1
    for r in ranks2:
        ways[r:] = ways[r:] + ways[:-r].copy() if r else ways * 2
    wplus = int(ranks2[d > 0].sum())
    dist = abs(wplus - total / 2)
    idx = np.arange(total + 1)
    return float(ways[np.abs(idx - total / 2) >= dist - 1e-9].sum() / ways.sum())


head("7. Transformer against GRU and LSTM, statistics recomputed")
T = fold_scores("main", "allpos", "all")
ps = {}
for other in ("gru_allpos", "lstm_allpos"):
    O = fold_scores("main", other, "all")
    dd = np.array([T[k] - O[k] for k in VAR])
    pub = stage1["contrasts"]["main"][other]
    rng = np.random.default_rng(20261103)
    ci = np.percentile(dd[rng.integers(0, 29, (10000, 29))].mean(1), [2.5, 97.5])
    rng2 = np.random.default_rng(7)
    ci2 = np.percentile(dd[rng2.integers(0, 29, (200000, 29))].mean(1), [2.5, 97.5])
    ps[other] = wilcoxon_exact(dd)
    print(f"  vs {other}: mean {dd.mean():+.4f}  CI [{ci[0]:+.4f}, {ci[1]:+.4f}]  (other seed, 200,000 resamples: "
          f"[{ci2[0]:+.4f}, {ci2[1]:+.4f}])  exact p {ps[other]:.4f} (published, approximate: {pub['p']:.4f})  "
          f"Transformer ahead in {(dd > 0).sum()}/29 folds")
    check(f"vs {other}: mean and interval equal the published ones; the interval includes 0 under both bootstraps",
          abs(dd.mean() - pub["mean"]) < 1e-9 and np.allclose(ci, pub["ci"], atol=1e-9) and ci[0] < 0 < ci[1] and ci2[0] < 0 < ci2[1])
holm = max(2 * min(ps.values()), max(ps.values()))
print(f"  Holm-corrected exact p: {min(1.0, 2 * min(ps.values())):.4f} and {min(1.0, holm):.4f}")
check('verdict "no difference shown" follows from the frozen rule with the exact test too',
      all(v["verdict"] == "no difference shown" for v in stage1["contrasts"]["main"].values()))

head("7b. Why unseen scenarios fail (labels only)")
for f in FOLDS:
    d = DATA["main", f["fold"]]
    if f["family"] == "scenario_held_out" or f["fold"] in ("1_autostart_localaccount", "3_ssh_apt", "6_macro_binary"):
        tr_big = {(w[0][-1], w[1]) for w in d["train"][4]}
        hit = np.mean([(w[0][-1], w[1]) in tr_big for w in d["test"][4]])
        print(f"    {f['fold']:<28} test steps whose (previous step -> next step) pair occurs in training: {hit:6.1%}")

# ── 8. the arrays the models were given ───────────────────────────────────────
head("8. Model inputs: the project's arrays against the ones rebuilt here")
sys.path.insert(0, P("camlds_encoder"))
import data as PD  # noqa: E402

ok, n = True, 0
for cond in ("main", "collapse_repeats"):
    pf = {f["fold"]: f for f in PD.folds(cond)}
    ok &= list(pf) == [f["fold"] for f in FOLDS]
    for f in FOLDS:
        g = pf[f["fold"]]
        ok &= g["train_runs"] == sorted(f["train"]) and g["val_runs"] == sorted(f["val"]) and g["test_runs"] == sorted(f["test"])
        pd_, d = PD.fold_data(g), DATA[cond, f["fold"]]
        for k in range(3):
            ok &= np.array_equal(pd_["train"][k], d["train"][k]) and np.array_equal(pd_["val"][k], d["val"][k])
        ok &= np.array_equal(pd_["test_inputs"][0], d["test"][0]) and np.array_equal(pd_["test_inputs"][1], d["test"][1])
        n += len(d["train"][0]) + len(d["val"][0]) + len(d["test"][0])
check("same folds, same runs, and bit-identical inputs, masks and targets in all 64 fold-conditions", ok, f"{n:,} windows")

fails = [n_ for n_, ok_ in checks if not ok_]
print(f"\nAUDIT: {len(checks) - len(fails)} of {len(checks)} checks passed" + (f"; FAILED: {fails}" if fails else ""))
raise SystemExit(1 if fails else 0)
