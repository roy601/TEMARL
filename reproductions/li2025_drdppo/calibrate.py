# -*- coding: utf-8 -*-
"""Li 2025 DRD-PPO: the calibrated replication (DECISIONS.md, protocol C1-C9 and amendments A1-A10).

    python reproductions/li2025_drdppo/calibrate.py smoke        # tiny code check, temporary folder, no effect
    python reproductions/li2025_drdppo/calibrate.py stage1       # environment on Alg1 28.43 + Alg3 55.19
    python reproductions/li2025_drdppo/calibrate.py stage2       # learner on DRD-PPO 97.09
    #   commit and push out/stage1.json, out/stage2.json and out/calibration_log.csv, then:
    python reproductions/li2025_drdppo/calibrate.py heldout      # ONCE: Alg2 98.31 and Table 4 DRD-PPO 98.61
                                                                 #   (+ references, sensitivity, REPORT.md)

Rules enforced here:
  * every trial (setting x policy x seed) is appended to out/calibration_log.csv; logged trials are reused, never
    re-run, so the log is the complete record of what was tried;
  * the user's own guesses run only from EXTRA_TRIALS.csv, and only while that file is committed and unchanged;
  * `heldout` refuses unless stage1.json and stage2.json are committed and unchanged, and it runs only once:
    after it, nothing can be calibrated again (out/heldout.json exists).
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import drdppo as D  # noqa: E402

OUT = HERE / "out"
EXTRA = HERE / "EXTRA_TRIALS.csv"
SEEDS = tuple(range(10))
T_975_DF9 = 2.2621571628          # Student t, 97.5%, 9 degrees of freedom (10 seeds)
CLOSE_POINTS = 2.0                # TARGETS.csv: CLOSE if within 2 percentage points
# C2: stage-1 grid in tie-break order (w = 0.1 first, P1 first, last step first)
STAGE1_GRID = [D.Setting(w=w, links=l, timing=t) for w, l, t in
               itertools.product((0.1, 0.05, 0.2, 0.5), ("P1", "P2", "P3"), ("last", "random"))]
# C3: stage-2 grid (R1, R2, clip) in the order listed
STAGE2_GRID = list(itertools.product((1.0, 5.0, 10.0), (0.0, 0.5), (0.2, 0.9)))
LOG_FIELDS = ["stage", "setting", "policy", "seed", "episodes", "dsp_train", "dsp_eval", "seconds"]


def targets() -> dict:
    with (HERE / "TARGETS.csv").open(encoding="utf-8") as fh:
        return {r["id"]: float(r["published"]) for r in csv.DictReader(fh)}


def git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(HERE), capture_output=True, text=True)


def committed_unchanged(path: Path) -> bool:
    rel = os.path.relpath(path, HERE)
    return git("ls-files", "--error-unmatch", rel).returncode == 0 and git("diff", "--quiet", "HEAD", "--", rel).returncode == 0


def git_head():
    r = git("rev-parse", "HEAD")
    return r.stdout.strip() or None


# ── the log: complete record and cache ───────────────────────────────────────

def read_log(out: Path) -> dict:
    p = out / "calibration_log.csv"
    if not p.exists():
        return {}
    with p.open(encoding="utf-8") as fh:
        return {(r["stage"], r["setting"], r["policy"], int(r["seed"]), int(r["episodes"])): r for r in csv.DictReader(fh)}


def append_log(out: Path, rows: list):
    p = out / "calibration_log.csv"
    new = not p.exists()
    out.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LOG_FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


def _job(args):
    """One trial (top-level for the process pool)."""
    stage, s_dict, policy, seed, episodes, eval_episodes = args
    s = D.Setting(**s_dict)
    t0 = time.time()
    if policy in ("alg1", "alg3", "scripted"):
        tr, ev = D.run_policy(s, 10_000 * ("alg1", "alg3", "scripted").index(policy) + seed, episodes, policy), []
    else:
        variant, learn = {"drdppo": ("drd", True), "alg2": ("alg2", True),
                          "drdppo_init": ("drd", False), "alg2_init": ("alg2", False)}[policy]
        r = D.train_ppo(s, seed, episodes, variant=variant, learn=learn, eval_episodes=eval_episodes)
        tr, ev = r["train"], r["eval"]
    return {"stage": stage, "setting": s.key(), "policy": policy, "seed": seed, "episodes": episodes,
            "dsp_train": D.dsp(tr), "dsp_eval": D.dsp(ev) if ev else "", "seconds": round(time.time() - t0, 2)}


def run_trials(out: Path, stage: str, settings: list, policies: tuple, episodes: int, workers: int,
               eval_episodes: int = 0, seeds=SEEDS) -> dict:
    """Run every (setting, policy, seed) not yet in the log; return {(setting key, policy): [dsp per seed]}."""
    log = read_log(out)
    todo = [(stage, vars_of(s), p, sd, episodes, eval_episodes) for s in settings for p in policies for sd in seeds
            if (stage, s.key(), p, sd, episodes) not in log]
    if todo:
        print(f"[{stage}] {len(todo)} new trials ({len(log)} already logged), {workers} workers", flush=True)
        rows = []
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for i, row in enumerate(ex.map(_job, todo), 1):
                rows.append(row)
                if i % 20 == 0 or i == len(todo):
                    print(f"  {i}/{len(todo)}", flush=True)
                    append_log(out, rows)
                    rows = []
        log = read_log(out)
    res = {}
    for s in settings:
        for p in policies:
            res[(s.key(), p)] = [float(log[(stage, s.key(), p, sd, episodes)]["dsp_train"]) for sd in seeds]
    return res


def vars_of(s: D.Setting) -> dict:
    import dataclasses
    return dataclasses.asdict(s)


def summary(vals) -> dict:
    v = np.asarray(vals, float)
    m, sd = float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0
    h = T_975_DF9 * sd / np.sqrt(len(v)) if len(v) == 10 else 1.96 * sd / np.sqrt(max(len(v), 1))
    return {"mean": m, "sd": sd, "ci": [m - h, m + h], "n_seeds": len(v), "per_seed": [float(x) for x in v]}


def extra_settings(stage: int, base: D.Setting = None) -> list:
    """Committed rows of EXTRA_TRIALS.csv for this stage (A10). Refuses if the file has uncommitted changes."""
    if not EXTRA.exists():
        return []
    with EXTRA.open(encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("stage", "").strip() == str(stage)]
    if rows and not committed_unchanged(EXTRA):
        raise SystemExit("EXTRA_TRIALS.csv has uncommitted changes: commit your guesses BEFORE running them (C6)")
    out = []
    for r in rows:
        kw = {k: r[k].strip() for k in ("w", "links", "timing", "cvss", "h_links", "R1", "R2", "clip") if r.get(k, "").strip()}
        if stage == 2 and set(kw) - {"R1", "R2", "clip"}:
            raise SystemExit("a stage-2 extra trial may set only R1, R2 and clip (the environment is stage 1's)")
        for k in ("w", "R1", "R2", "clip"):
            if k in kw:
                kw[k] = float(kw[k])
        start = vars_of(base) if base else {}
        out.append(D.Setting(**{**start, **kw}))
    return out


# ── stages ───────────────────────────────────────────────────────────────────

def stage1(out: Path, workers: int, episodes: int = 500, seeds=SEEDS) -> dict:
    if (out / "heldout.json").exists():
        raise SystemExit("the held-out targets have been computed: no further calibration (C6)")
    T = targets()
    grid = STAGE1_GRID + [s for s in extra_settings(1) if s.key() not in {g.key() for g in STAGE1_GRID}]
    res = run_trials(out, "stage1", grid, ("alg1", "alg3", "scripted"), episodes, workers, seeds=seeds)
    rows = []
    for order, s in enumerate(grid):
        a1, a3, sc = (summary(res[(s.key(), p)]) for p in ("alg1", "alg3", "scripted"))
        loss = (a1["mean"] - T["T3.Alg1_random_deployment"]) ** 2 + (a3["mean"] - T["T3.Alg3_random_full_deployment"]) ** 2
        rows.append({"order": order, "setting": vars_of(s), "key": s.key(), "loss": loss, "alg1": a1, "alg3": a3,
                     "scripted": sc, "extra": order >= len(STAGE1_GRID)})
    best = min(rows, key=lambda r: (round(r["loss"], 9), r["order"]))
    near = [r["key"] for r in rows if abs(r["alg1"]["mean"] - T["T3.Alg1_random_deployment"]) <= CLOSE_POINTS
            and abs(r["alg3"]["mean"] - T["T3.Alg3_random_full_deployment"]) <= CLOSE_POINTS]
    # attack 2 of the devil's-advocate review: discrimination of the held-out targets, scripted policy only
    held = {k: T[k] for k in ("T3.Alg2_intelligent_full_deployment", "T4.DRD-PPO")}
    scripted_close = {k: sum(abs(r["scripted"]["mean"] - v) <= CLOSE_POINTS for r in rows) for k, v in held.items()}
    rec = {"stage": 1, "targets": {"T3.Alg1_random_deployment": T["T3.Alg1_random_deployment"],
                                   "T3.Alg3_random_full_deployment": T["T3.Alg3_random_full_deployment"]},
           "selected": best["setting"], "selected_key": best["key"], "selected_loss": best["loss"],
           "identifiability_settings_within_2_points_of_both": near, "n_settings": len(rows),
           "scripted_within_2_points_of_heldout_targets_n_settings": scripted_close,
           "rows": rows, "episodes": episodes, "seeds": list(seeds), "git_head": git_head()}
    D_write(out / "stage1.json", rec)
    print(f"stage 1 selected {best['key']} (loss {best['loss']:.2f}); Alg1 {best['alg1']['mean']:.2f} "
          f"(target 28.43), Alg3 {best['alg3']['mean']:.2f} (target 55.19); {len(near)} of {len(rows)} settings within "
          f"2 points of both")
    return rec


def stage2(out: Path, workers: int, episodes: int = 500, seeds=SEEDS) -> dict:
    if (out / "heldout.json").exists():
        raise SystemExit("the held-out targets have been computed: no further calibration (C6)")
    s1 = json.loads((out / "stage1.json").read_text(encoding="utf-8"))
    base = D.Setting(**s1["selected"])
    T = targets()
    grid = [D.Setting(**{**vars_of(base), "R1": r1, "R2": r2, "clip": c}) for r1, r2, c in STAGE2_GRID]
    grid += [s for s in extra_settings(2, base) if s.key() not in {g.key() for g in grid}]
    res = run_trials(out, "stage2", grid, ("drdppo",), episodes, workers, seeds=seeds)
    rows = [{"order": i, "setting": vars_of(s), "key": s.key(), "drdppo": summary(res[(s.key(), "drdppo")]),
             "extra": i >= len(STAGE2_GRID)} for i, s in enumerate(grid)]
    target = T["T3.DRD-PPO"]
    best = min(rows, key=lambda r: (round(abs(r["drdppo"]["mean"] - target), 9), r["order"]))
    near = [r["key"] for r in rows if abs(r["drdppo"]["mean"] - target) <= CLOSE_POINTS]
    rec = {"stage": 2, "target": {"T3.DRD-PPO": target}, "stage1_selected_key": s1["selected_key"],
           "selected": best["setting"], "selected_key": best["key"], "identifiability_settings_within_2_points": near,
           "n_settings": len(rows), "rows": rows, "episodes": episodes, "seeds": list(seeds), "git_head": git_head()}
    D_write(out / "stage2.json", rec)
    print(f"stage 2 selected {best['key']}: DRD-PPO {best['drdppo']['mean']:.2f} (target 97.09); {len(near)} of "
          f"{len(rows)} settings within 2 points")
    return rec


def verdict(s: dict, published: float, refs: dict) -> tuple:
    """A2: UNINFORMATIVE if any reference is within 2 points; else MATCH (inside our 95% CI), CLOSE, NO MATCH."""
    if any(abs(v - published) <= CLOSE_POINTS for v in refs.values()):
        return "UNINFORMATIVE", "a reference policy is within 2 points of the published value (A2)"
    if s["ci"][0] <= published <= s["ci"][1]:
        return "MATCH", "published value inside our 95% CI over 10 seeds"
    if abs(s["mean"] - published) <= CLOSE_POINTS:
        return "CLOSE", "within 2 percentage points"
    return "NO MATCH", "outside the tolerance"


def heldout(out: Path, workers: int, check_git: bool = True, seeds=SEEDS, episodes=(500, 1500)) -> dict:
    if (out / "heldout.json").exists():
        raise SystemExit("the held-out targets were already computed; they are computed once (C4)")
    for f in ("stage1.json", "stage2.json", "calibration_log.csv"):
        if not (out / f).exists():
            raise SystemExit(f"out/{f} is missing: run stage1 and stage2 first")
        if check_git and not committed_unchanged(out / f):
            raise SystemExit(f"out/{f} is not committed or has changed: commit and push the closed calibration first (C4)")
    s1 = json.loads((out / "stage1.json").read_text(encoding="utf-8"))
    s2 = json.loads((out / "stage2.json").read_text(encoding="utf-8"))
    if s2["stage1_selected_key"] != s1["selected_key"]:
        raise SystemExit("stage2.json was made on another stage-1 selection: rerun stage2")
    final = D.Setting(**s2["selected"])
    T = targets()
    e3, e4 = episodes
    log_rows = []

    def trials(policy, n_eps, setting=final, eval_eps=0):
        jobs = [("heldout", vars_of(setting), policy, sd, n_eps, eval_eps) for sd in seeds]
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rows = list(ex.map(_job, jobs))
        log_rows.extend(rows)
        return rows

    alg2 = trials("alg2", e3, eval_eps=e3)
    drd = trials("drdppo", e4, eval_eps=e4)
    refs = {"T3.Alg2_intelligent_full_deployment": {"scripted": trials("scripted", e3), "random_init": trials("alg2_init", e3)},
            "T4.DRD-PPO": {"scripted": trials("scripted", e4), "random_init": trials("drdppo_init", e4)}}
    sens_v3 = trials("drdppo", e3, setting=D.Setting(**{**vars_of(final), "cvss": "v3"}))
    append_log(out, log_rows)
    res = {}
    for tid, rows in (("T3.Alg2_intelligent_full_deployment", alg2), ("T4.DRD-PPO", drd)):
        s = summary([r["dsp_train"] for r in rows])
        ev = summary([r["dsp_eval"] for r in rows])
        rv = {k: summary([r["dsp_train"] for r in v])["mean"] for k, v in refs[tid].items()}
        v, why = verdict(s, T[tid], rv)
        res[tid] = {"published": T[tid], "ours_train": s, "ours_eval": ev, "references": rv, "verdict": v, "why": why}
    rec = {"final_setting": vars_of(final), "final_key": final.key(), "heldout": res,
           "sensitivity_cvss_v3_drdppo_500": summary([r["dsp_train"] for r in sens_v3]),
           "stage1_key": s1["selected_key"], "stage2_key": s2["selected_key"], "git_head": git_head(),
           "computed": time.strftime("%Y-%m-%d %H:%M:%S")}
    D_write(out / "heldout.json", rec)
    for tid, r in res.items():
        print(f"{tid}: ours {r['ours_train']['mean']:.2f} [{r['ours_train']['ci'][0]:.2f}, {r['ours_train']['ci'][1]:.2f}] "
              f"vs {r['published']}; references {r['references']} -> {r['verdict']}")
    import report
    report.write(out)
    return rec


def D_write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["smoke", "stage1", "stage2", "heldout"])
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args()
    t0 = time.time()
    if a.stage == "smoke":
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            global STAGE1_GRID, STAGE2_GRID
            STAGE1_GRID, STAGE2_GRID = STAGE1_GRID[:2], STAGE2_GRID[:2]
            stage1(out, a.workers, episodes=6, seeds=(0, 1))
            stage2(out, a.workers, episodes=6, seeds=(0, 1))
            heldout(out, a.workers, check_git=False, seeds=(0, 1), episodes=(6, 9))
            print(f"smoke OK in {time.time() - t0:.0f} s (temporary folder, nothing kept)")
        return
    {"stage1": stage1, "stage2": stage2, "heldout": heldout}[a.stage](OUT, a.workers)
    print(f"{a.stage} finished in {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
