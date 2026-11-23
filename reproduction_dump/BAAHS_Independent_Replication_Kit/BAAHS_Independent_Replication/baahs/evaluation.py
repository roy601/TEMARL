"""Paired, pre-generated fixed-trajectory evaluation and transparent reporting."""
from __future__ import annotations
import csv
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from .world import World
from .policies import POLICIES, K

PAPER_REFERENCE = {
    "baahs_hit_rate": .2589,
    "strongest_baseline_hit_rate": .1532,
    "reference_source": "https://doi.org/10.1109/ACCESS.2026.3740819",
    "role": "reference_only_not_fitted_or_used_in_simulator",
}


def evaluate_one_seed(world: World, seed: int, steps: int, split: str):
    path = world.make_trajectory(seed, steps)
    outcomes = []
    event_records = []
    # One trajectory is generated once and shared across all policies (paired comparison).
    for ix, cls in enumerate(POLICIES):
        policy = cls(world, (seed * 1009 + 31 * (ix + 1)) % (2**32))
        successes = 0
        near_misses = 0
        for t in range(steps - 1):
            current = path[t]
            future = path[t + 1]
            placement = policy.select(current.node, current.alert)
            assert len(placement) == K and len(set(placement)) == K
            hit = int(future.node in placement)
            successes += hit
            near_miss = int(not hit and any(world.adjacency[p, future.node] for p in placement))
            near_misses += near_miss
            policy.feedback(placement, future.node)
            event_records.append({
                "split": split, "seed": seed, "policy": policy.name, "t": t,
                "observed_node": current.node, "observed_alert": current.alert,
                "selected_for_next": list(placement), "next_node": future.node,
                "hit": hit, "near_miss": near_miss,
            })
        outcomes.append({
            "split": split, "seed": seed, "policy": policy.name,
            "opportunities": steps - 1, "hits": successes,
            "hit_rate": successes/(steps-1), "near_misses": near_misses,
            "mode_counts": dict(policy.mode_counts),
        })
    return outcomes, event_records


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {}
    methods = sorted(set(r["policy"] for r in rows))
    result = {}
    for name in methods:
        vals = [float(r["hit_rate"]) for r in rows if r["policy"] == name]
        n = len(vals)
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals) if n > 1 else 0.
        half = 1.959963984540054 * sd / math.sqrt(n) if n > 1 else None
        result[name] = {
            "seeds": n,
            "mean_hit_rate": mean,
            "std_across_seeds": sd,
            "ci95_normal": ([max(0., mean-half), min(1., mean+half)] if half is not None else None),
            "total_hits": int(sum(r["hits"] for r in rows if r["policy"] == name)),
            "total_opportunities": int(sum(r["opportunities"] for r in rows if r["policy"] == name)),
        }
    return result


def selected_baseline(stats: dict) -> str:
    # Selection on development only; frozen for the held-out validation.
    keys = [k for k in stats if k != "baahs_independent"]
    return max(keys, key=lambda k: stats[k]["mean_hit_rate"])


def exploratory_match(stats: dict, tolerance_pp: float):
    baseline = selected_baseline(stats)
    means = stats["baahs_independent"]["mean_hit_rate"], stats[baseline]["mean_hit_rate"]
    refs = PAPER_REFERENCE["baahs_hit_rate"], PAPER_REFERENCE["strongest_baseline_hit_rate"]
    diffs = [(a-b)*100 for a, b in zip(means, refs)]
    return (all(abs(diff) <= tolerance_pp for diff in diffs), baseline, diffs)


def _save_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        for x in rows:
            writer.writerow({key: json.dumps(x[key], sort_keys=True) if isinstance(x.get(key), (dict, list)) else x.get(key) for key in fields})


def _save_jsonl(path: Path, events: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for e in events:
            f.write(json.dumps(e, separators=(",", ":")) + "\n")


def write_report(outdir: Path, dev: dict, holdout: dict, picked: str,
                 met: bool, batches: int, tolerance_pp: float):
    target_a = PAPER_REFERENCE["baahs_hit_rate"]
    target_b = PAPER_REFERENCE["strongest_baseline_hit_rate"]
    def pct(x): return f"{x*100:.2f}%"
    def fmt_ci(item):
        ci = item["ci95_normal"]
        return "n/a (n<2)" if ci is None else f"[{pct(ci[0])}, {pct(ci[1])}]"
    lines = [
        "# Independent BAAHS-style replication: experimental report", "",
        "**Status: INDEPENDENT SIMULATION, NOT ORIGINAL-AUTHOR REPRODUCTION.**", "",
        "Original BAAHS experimental assets, equations, seeds, and complete protocol were not available.",
        "This code therefore uses explicit synthetic assumptions. Similar numeric means do not establish equivalence.", "",
        "## Published reference (not used in policy selection)", "",
        f"- Paper BAAHS: {pct(target_a)}",
        f"- Paper strongest baseline: {pct(target_b)}",
        "- Reference: https://doi.org/10.1109/ACCESS.2026.3740819", "",
        "## Development / exploratory runs", "",
        f"- Completed batches: {batches} (each 50 seeds, except custom sizes)",
        f"- Exploratory within ±{tolerance_pp:.2f} percentage points for both rates: **{met}**",
        "- This condition is ONLY an exploratory flag, not a reproduction claim.", "",
        "| Method | Seeds | Hit rate (per-seed mean) | Across-seed SD | Normal 95% CI |", "|---|---:|---:|---:|---|",
    ]
    for name, obj in sorted(dev.items(), key=lambda x: -x[1]["mean_hit_rate"]):
        lines.append(f'| {name} | {obj["seeds"]} | {pct(obj["mean_hit_rate"])} | {pct(obj["std_across_seeds"])} | {fmt_ci(obj)} |')
    lines += ["", "## Frozen held-out validation", "", f"Development-selected baseline: **{picked}**", "",
              "| Method | Seeds | Hit rate | Normal 95% CI | Difference from paper (percentage points) |",
              "|---|---:|---:|---|---:|"]
    for name in ("baahs_independent", picked):
        obj = holdout[name]
        ref = target_a if name == "baahs_independent" else target_b
        lines.append(f'| {name} | {obj["seeds"]} | {pct(obj["mean_hit_rate"])} | {fmt_ci(obj)} | {(obj["mean_hit_rate"]-ref)*100:+.2f} |')
    lines += ["", "All other held-out baselines are also in `summary.json`.",
              "Held-out seeds never influence model parameters, stopping, or baseline selection.", "",
              "## Scientific interpretation", "",
              "A numerically close result is not proof of having reproduced the original BAAHS study.",
              "Differences in attacker trajectories, HMM probabilities, role mapping, objective weights,",
              "reward updates, and baseline choices can dominate outcomes. The correct evidence level",
              "is an independent simulated method comparison with reference-value diagnostics.", "",
              "## Outputs", "",
              "- `dev_runs.csv` / `holdout_runs.csv`: full per-seed results for every policy",
              "- `dev_events.jsonl` / `holdout_events.jsonl`: every placement, outcome and hit",
              "- `summary.json`: full aggregates, configuration, and provenance", ""]
    (outdir / "EVALUATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def run_experiment(outdir: str | Path, *, steps: int = 80, seeds_per_batch: int = 50,
                   max_batches: int = 1, repeat_until_match: bool = False,
                   tolerance_pp: float = 1., holdout_seeds: int = 50,
                   dev_seed_start: int = 0, holdout_seed_start: int = 1_000_000,
                   verbose: bool = True):
    if steps < 2 or seeds_per_batch < 1 or max_batches < 1 or holdout_seeds < 2:
        raise ValueError("steps>=2, seeds/batch>=1, max_batches>=1 and holdout>=2 required")
    if tolerance_pp < 0:
        raise ValueError("tolerance_pp must be nonnegative")
    dev_end = dev_seed_start + seeds_per_batch * max_batches
    assert holdout_seed_start >= dev_end or (holdout_seed_start+holdout_seeds <= dev_seed_start), "Seed ranges overlap"
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    world = World()
    dev_rows, dev_events = [], []
    dev_history = []
    met = False
    for batch in range(max_batches):
        for ix in range(seeds_per_batch):
            seed = dev_seed_start + batch*seeds_per_batch + ix
            rows, events = evaluate_one_seed(world, seed, steps, "development")
            dev_rows.extend(rows)
            dev_events.extend(events)
        dev_stats = summarize(dev_rows)
        met, best, diffs = exploratory_match(dev_stats, tolerance_pp)
        hist = {"batch": batch+1, "seeds_evaluated": (batch+1)*seeds_per_batch,
                "mean_baahs": dev_stats["baahs_independent"]["mean_hit_rate"],
                "best_baseline": best, "mean_best_baseline": dev_stats[best]["mean_hit_rate"],
                "differences_from_published_pp": diffs,
                "exploratory_match": met}
        dev_history.append(hist)
        if verbose:
            print(f'Batch {batch+1}/{max_batches}: {seeds_per_batch*(batch+1)} dev seeds; '
                  f'BAAHS={hist["mean_baahs"]:.2%}, strongest baseline '
                  f'({best})={hist["mean_best_baseline"]:.2%}; '
                  f'reference differences={diffs[0]:+.2f}/{diffs[1]:+.2f} pp')
        # Optional sequential exploratory stop, with mandatory fresh holdout below.
        if repeat_until_match and met:
            if verbose: print("Exploratory threshold reached; independent holdout still required.")
            break
    picked = selected_baseline(summarize(dev_rows))
    holdout_rows, holdout_events = [], []
    for ix in range(holdout_seeds):
        seed = holdout_seed_start + ix
        rows, events = evaluate_one_seed(world, seed, steps, "held_out")
        holdout_rows.extend(rows)
        holdout_events.extend(events)
    dev = summarize(dev_rows)
    holdout = summarize(holdout_rows)
    _save_csv(outdir / "dev_runs.csv", dev_rows,
              ["split", "seed", "policy", "opportunities", "hits", "hit_rate", "near_misses", "mode_counts"])
    _save_csv(outdir / "holdout_runs.csv", holdout_rows,
              ["split", "seed", "policy", "opportunities", "hits", "hit_rate", "near_misses", "mode_counts"])
    _save_jsonl(outdir / "dev_events.jsonl", dev_events)
    _save_jsonl(outdir / "holdout_events.jsonl", holdout_events)
    summary = {
        "artifact_status": "independent_BAAHS_inspired_simulator_NOT_original_code_reproduction",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "reference_only": PAPER_REFERENCE,
        "config": {"nodes": 25, "honeypots": 4, "latent_stages": 11,
                   "steps": steps, "seeds_per_batch": seeds_per_batch,
                   "max_batches": max_batches, "repeat_until_match": repeat_until_match,
                   "tolerance_pp": tolerance_pp, "holdout_seeds": holdout_seeds,
                   "dev_seed_start": dev_seed_start, "holdout_seed_start": holdout_seed_start},
        "completed_batches": len(dev_history), "history": dev_history,
        "development": dev, "held_out": holdout,
        "frozen_baseline_chosen_on_development": picked,
        "exploratory_match_found": met,
        "heldout_diffs_pp": {
            "baahs": (holdout["baahs_independent"]["mean_hit_rate"] - PAPER_REFERENCE["baahs_hit_rate"]) * 100,
            "baseline": (holdout[picked]["mean_hit_rate"] - PAPER_REFERENCE["strongest_baseline_hit_rate"]) * 100},
        "scientific_conclusion": "no_published_experiment_reproduction_claim",
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(outdir, dev, holdout, picked, met, len(dev_history), tolerance_pp)
    if verbose:
        print(f'HELD-OUT: BAAHS={holdout["baahs_independent"]["mean_hit_rate"]:.2%}; '
              f'{picked}={holdout[picked]["mean_hit_rate"]:.2%}')
        print(f'Generated: {outdir / "EVALUATION_REPORT.md"}')
    return summary
