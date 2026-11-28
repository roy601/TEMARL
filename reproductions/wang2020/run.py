# -*- coding: utf-8 -*-
"""Wang et al. 2020: calibration on Fig. 10, then the held-out targets once (DECISIONS Section 4).

    python reproductions/wang2020/run.py calibrate --workers 8   # 144 attacker readings x 21 static policies
    python reproductions/wang2020/run.py heldout --workers 8     # once, after out/CALIBRATION.json is committed
    python reproductions/wang2020/run.py report                  # REPORT.md from out/

Each stage refuses to run if its inputs are not committed unchanged, and refuses to run twice.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wang_env as W  # noqa: E402

OUT = HERE / "out"
N_EXP = 1000                     # Table 3: 1000 experiments per evaluation
SEEDS = range(10)                # D14
REPEATS = 10                     # Figs. 11-12: ten repeats per setting
CHECKPOINTS = [0, 500, 1000, 2000, 5000, 10000, 20000, 30000]
ADEQUATE_RMSE = 5.0              # Section 4: calibration adequate if the best RMSE is at most 5 points
CLOSE_BAND = 2.0                 # TARGETS.csv: CLOSE if within 2 percentage points
T975_DF9 = 2.2621571627          # t quantile for a 95% CI over 10 seeds

# Section 4: the committed calibration grid (144 readings).
GRID = [W.Attacker(choice, j, interest, d_i, alpha, ties)
        for choice in ("argmax", "proportional")
        for j in ("UP", "RP")
        for interest in ("uniform", "role", "outdegree", "random")
        for d_i in ("data", "location")
        for alpha in (0.2, 0.5, 0.8)
        for ties in (("index", "random") if choice == "argmax" else ("none",))]


# ----------------------------------------------------------------------------- guards
def committed_unchanged(paths):
    for f in paths:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(f)], cwd=HERE, capture_output=True).returncode == 0
        clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(f)], cwd=HERE).returncode == 0
        if not (tracked and clean):
            sys.exit(f"refusing to run: {f} is not committed unchanged")


def environment():
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=HERE, capture_output=True, text=True).stdout.strip()
    return {"python": sys.version, "platform": platform.platform(), "processor": platform.processor(),
            "commit": commit, "time": time.strftime("%Y-%m-%d %H:%M:%S")}


def targets():
    with open(HERE / "TARGETS.csv", encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


def fig10_means():
    t = targets()
    return [float(t[f"F10.P{k:02d}"]["published"]) for k in range(1, 22)]


# ----------------------------------------------------------------------------- calibration
def calibrate_one(att):
    dsp, to = [], []
    for k in range(1, 22):
        row = [W.evaluate(att, st, W.static_policy(k), N_EXP, W.seed_of("cal", att.name, k, si))
               for si, st in enumerate(W.SETTINGS)]
        dsp.append([100 * d for d, _ in row])
        to.append(sum(t for _, t in row) / len(row))
    return att, dsp, to


def rmse(ours, published):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(ours, published)) / len(published))


def stage_calibrate(workers):
    committed_unchanged(["TARGETS.csv", "DECISIONS.md", "wang_env.py", "run.py", "data/ntpg.json"])
    if (OUT / "CALIBRATION.json").exists():
        sys.exit("refusing: out/CALIBRATION.json exists (the calibration runs once)")
    OUT.mkdir(exist_ok=True)
    pub = fig10_means()
    null = statistics.pstdev(pub)
    t0 = time.time()
    with Pool(workers) as pool:
        results = pool.map(calibrate_one, GRID, chunksize=1)
    rows = []
    for i, (att, dsp, to) in enumerate(results):
        means = [sum(r) / len(r) for r in dsp]
        rows.append(dict(trial=i + 1, **{k: getattr(att, k) for k in ("choice", "j", "interest", "decoy_interest", "alpha", "ties")},
                         rmse=round(rmse(means, pub), 4), max_abs_err=round(max(abs(a - b) for a, b in zip(means, pub)), 4),
                         timeout_share=round(sum(to) / len(to), 5),
                         **{f"P{k:02d}": round(m, 3) for k, m in enumerate(means, 1)}))
    with open(OUT / "calibration_log.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    best = min(rows, key=lambda r: (r["rmse"], r["trial"]))      # Section 4: lowest RMSE; ties -> first trial
    ranked = sorted(rows, key=lambda r: (r["rmse"], r["trial"]))
    cal = {"selected_trial": best["trial"], "selected": {k: best[k] for k in ("choice", "j", "interest", "decoy_interest", "alpha", "ties")},
           "rmse": best["rmse"], "max_abs_err": best["max_abs_err"], "null_rmse_constant_predictor": round(null, 4),
           "adequate": best["rmse"] <= ADEQUATE_RMSE, "adequacy_rule": f"RMSE <= {ADEQUATE_RMSE} points",
           "next_best": [{k: r[k] for k in ("trial", "rmse", "choice", "j", "interest", "decoy_interest", "alpha", "ties")} for r in ranked[1:6]],
           "trials": len(rows), "seconds": round(time.time() - t0, 1), "environment": environment()}
    (OUT / "CALIBRATION.json").write_text(json.dumps(cal, indent=1), encoding="utf-8")
    print(json.dumps({k: cal[k] for k in ("selected_trial", "selected", "rmse", "null_rmse_constant_predictor", "adequate", "seconds")}, indent=1))


# ----------------------------------------------------------------------------- held-out (once)
def selected_attacker():
    c = json.loads((OUT / "CALIBRATION.json").read_text(encoding="utf-8"))["selected"]
    return W.Attacker(c["choice"], c["j"], c["interest"], c["decoy_interest"], float(c["alpha"]), c["ties"])


def heldout_job(job):
    kind, seed, si = job
    att = selected_attacker()
    st = W.SETTINGS[si] if si is not None else None
    if kind == "static":
        return job, [[100 * W.evaluate(att, s, W.static_policy(k), N_EXP, W.seed_of("static", att.name, k, i, seed))[0]
                      for i, s in enumerate(W.SETTINGS)] for k in range(1, 22)]
    if kind == "fa":
        import random
        return job, [[100 * W.evaluate(att, s, W.following_alarm(random.Random(W.seed_of("fa-agent", att.name, i, seed, r))),
                                       N_EXP, W.seed_of("fa-env", att.name, i, seed, r))[0] for r in range(REPEATS)]
                     for i, s in enumerate(W.SETTINGS)]
    if kind in ("rd_a", "rd_b"):
        import random
        reading = kind[-1]
        return job, [[100 * W.evaluate(att, s, W.random_dynamic(random.Random(W.seed_of("rd-seq", reading, att.name, i, seed, r)), reading),
                                       N_EXP, W.seed_of("rd-env", reading, att.name, i, seed, r))[0] for r in range(REPEATS)]
                     for i, s in enumerate(W.SETTINGS)]
    if kind == "q":
        res = W.q_learning(att, st, max(CHECKPOINTS), CHECKPOINTS, N_EXP, seed)
        return job, {str(t): 100 * v for t, v in res.items()}
    raise ValueError(kind)


def stage_heldout(workers):
    committed_unchanged(["TARGETS.csv", "DECISIONS.md", "wang_env.py", "run.py", "data/ntpg.json",
                         "out/CALIBRATION.json", "out/calibration_log.csv"])
    if (OUT / "heldout.json").exists():
        sys.exit("refusing: out/heldout.json exists (held-out targets are computed once)")
    jobs = [(k, s, None) for s in SEEDS for k in ("static", "fa", "rd_a", "rd_b")]
    jobs += [("q", s, i) for s in SEEDS for i in range(len(W.SETTINGS))]
    t0 = time.time()
    with Pool(workers) as pool:
        done = pool.map(heldout_job, jobs, chunksize=1)
    res = {"static": {}, "fa": {}, "rd_a": {}, "rd_b": {}, "q": {}}
    for (kind, seed, si), v in done:
        if kind == "q":
            res["q"].setdefault(str(seed), {})[str(si)] = v
        else:
            res[kind][str(seed)] = v
    res["attacker"] = selected_attacker().name
    res["checkpoints"] = CHECKPOINTS
    res["seconds"] = round(time.time() - t0, 1)
    res["environment"] = environment()
    (OUT / "heldout.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"held-out done in {res['seconds']} s")


# ----------------------------------------------------------------------------- report
def mean_ci(v):
    assert len(v) == 10, "the CI rule assumes 10 seeds"
    m = statistics.fmean(v)
    h = T975_DF9 * statistics.stdev(v) / math.sqrt(len(v))
    return m, m - h, m + h


def held_verdict(published, values, refs):
    m, lo, hi = mean_ci(values)
    if any(abs(r - published) <= CLOSE_BAND for r in refs):
        return "UNINFORMATIVE"
    if lo <= published <= hi:
        return "MATCH"
    return "CLOSE" if abs(m - published) <= CLOSE_BAND else "NO MATCH"


def per_seed(h):
    """Per-seed values (percent) of every quantity the targets use."""
    S = [str(s) for s in SEEDS]
    static = {k: [statistics.fmean(h["static"][s][k - 1]) for s in S] for k in range(1, 22)}
    static_si = {(k, i): [h["static"][s][k - 1][i] for s in S] for k in range(1, 22) for i in range(4)}
    best = max(range(1, 22), key=lambda k: statistics.fmean(static[k]))
    fa_si = {i: [statistics.fmean(h["fa"][s][i]) for s in S] for i in range(4)}
    rd = {r: [statistics.fmean(sum(h[f"rd_{r}"][s], [])) for s in S] for r in "ab"}
    rd_si = {i: [statistics.fmean(h["rd_b"][s][i]) for s in S] for i in range(4)}
    q = {t: {i: [h["q"][s][str(i)][str(t)] for s in S] for i in range(4)} for t in h["checkpoints"]}
    q_mean = {t: [statistics.fmean(q[t][i][n] for i in range(4)) for n in range(len(S))] for t in h["checkpoints"]}
    return dict(static=static, static_si=static_si, best=best, fa_si=fa_si, rd=rd, rd_si=rd_si, q=q, q_mean=q_mean)


def stage_report():
    cal = json.loads((OUT / "CALIBRATION.json").read_text(encoding="utf-8"))
    h = json.loads((OUT / "heldout.json").read_text(encoding="utf-8"))
    T = targets()
    P = per_seed(h)
    avg = statistics.fmean
    best = P["best"]
    fa_mean = [avg(P["fa_si"][i][n] for i in range(4)) for n in range(10)]
    ref_mean = {"best static": avg(P["static"][best]), "following-alarm": avg(fa_mean),
                "random-dynamic (b)": avg(P["rd"]["b"]), "untrained Q": avg(P["q_mean"][0])}
    rows = []

    def add(tid, values, refs, kind="held"):
        pub = float(T[tid]["published"])
        m, lo, hi = mean_ci(values)
        if kind == "cal":
            v = "CALIBRATION TARGET"
        else:
            v = held_verdict(pub, values, refs)
        rows.append((tid, pub, m, lo, hi, v, refs))

    for k in range(1, 22):
        add(f"F10.P{k:02d}", P["static"][k], [], "cal")
    add("F10.best_text", P["static_si"][(1, 0)], [], "cal")
    add("F13.Q_30000_mean", P["q_mean"][30000], [ref_mean[r] for r in ref_mean])
    claim = [P["q_mean"][30000][n] - P["static"][best][n] for n in range(10)]
    add("CLAIM.Q_minus_best_static", claim, [0.0] + [ref_mean[r] - ref_mean["best static"] for r in ("following-alarm", "random-dynamic (b)", "untrained Q")])
    for i in range(4):
        add(f"F13.Q_30000.S{i + 1}", P["q"][30000][i],
            [avg(P["static_si"][(best, i)]), avg(P["fa_si"][i]), avg(P["rd_si"][i]), avg(P["q"][0][i])])
    add("F13.Q_2000_mean", P["q_mean"][2000], [ref_mean[r] for r in ref_mean])
    add("F13.Q_0_mean", P["q_mean"][0], [ref_mean[r] for r in ("best static", "following-alarm", "random-dynamic (b)")])
    for i in range(4):
        add(f"F12.FA.S{i + 1}", P["fa_si"][i], [avg(P["static_si"][(best, i)]), avg(P["rd_si"][i]), avg(P["q"][0][i])])
    add("F11.RD_mean", P["rd"]["b"], [ref_mean[r] for r in ("best static", "following-alarm", "untrained Q")])

    primary = [r for r in rows if T[r[0]]["primary"].strip().lower() == "yes"]
    informative = [r for r in primary if r[5] != "UNINFORMATIVE"]
    ok = cal["adequate"] and informative and all(r[5] in ("MATCH", "CLOSE") for r in informative)
    if not cal["adequate"]:
        paper = f"NOT calibrated-replicated: the calibration is not adequate (best RMSE {cal['rmse']:.2f} > {ADEQUATE_RMSE} points)"
    elif not informative:
        paper = "UNINFORMATIVE: no primary held-out target passes the informativeness test"
    elif ok:
        paper = "calibrated-replicated (every informative primary held-out target is MATCH or CLOSE)"
    else:
        paper = "NOT calibrated-replicated: " + ", ".join(f"{r[0]} {r[5]}" for r in informative if r[5] not in ("MATCH", "CLOSE"))

    sel = cal["selected"]
    lines = ["# Report: Wang et al. 2020 (IEEE Access 8:35792), calibrated replication", "",
             "Generated by `run.py report` from `out/CALIBRATION.json` and `out/heldout.json`. Rules: DECISIONS.md Section 4.", "",
             f"**Paper verdict: {paper}.**", "",
             "## Calibration (Fig. 10, 21 static policies, 144 committed readings, every trial in `out/calibration_log.csv`)", "",
             f"- Selected reading (trial {cal['selected_trial']}): " + ", ".join(f"{k} = {v}" for k, v in sel.items()),
             f"- RMSE over the 21 policy means: {cal['rmse']:.2f} points (largest error {cal['max_abs_err']:.2f}); "
             f"a constant predictor gives {cal['null_rmse_constant_predictor']:.2f}; adequate (<= {ADEQUATE_RMSE}): {cal['adequate']}",
             f"- Best static policy in our environment: policy {best} {W.ACTIONS[best - 1]} (locations numbered from 0)",
             "", "## Every target", "",
             "Ours = mean over 10 seeds with the 95% CI (t). Reference policies (best static, following-alarm, random-dynamic (b), untrained Q) "
             "decide UNINFORMATIVE: any reference within 2 points of the published value.", "",
             "| id | published | ours | 95% CI | references | verdict |", "|---|---|---|---|---|---|"]
    for tid, pub, m, lo, hi, v, refs in rows:
        lines.append(f"| {tid} | {pub:.2f} | {m:.2f} | [{lo:.2f}, {hi:.2f}] | {', '.join(f'{r:.1f}' for r in refs) or '-'} | {v} |")
    lines.append(f"| F14.time_30000 | {float(T['F14.time_30000']['published']):.0f} | - | - | - | NOT ATTEMPTED |")
    lines += ["", "## Sensitivity (reported, not judged)", "",
              f"- Random-dynamic reading (a), one random deployment per repeat: mean {avg(P['rd']['a']):.2f} "
              f"(reading (b): {avg(P['rd']['b']):.2f}; published 51.14)",
              "- Q-learning curve (mean of 4 settings, 10 seeds): " + ", ".join(f"{t}: {avg(P['q_mean'][t]):.1f}" for t in h["checkpoints"]),
              "", "## Environment", "", f"- calibration: {cal['environment']}", f"- held-out: {h['environment']}", ""]
    (HERE / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {"paper": paper, "rows": [(r[0], r[1], round(r[2], 2), r[5]) for r in rows]}
    (OUT / "results.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(paper)
    for r in rows:
        print(f"{r[0]:28s} {r[1]:7.2f} {r[2]:7.2f} [{r[3]:6.2f}, {r[4]:6.2f}] {r[5]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["calibrate", "heldout", "report", "grid"])
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.stage == "grid":
        print(len(GRID), "readings")
    elif a.stage == "calibrate":
        stage_calibrate(a.workers)
    elif a.stage == "heldout":
        stage_heldout(a.workers)
    else:
        stage_report()


if __name__ == "__main__":
    main()
