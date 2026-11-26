#!/usr/bin/env python3
"""Generate side-by-side CSV using only SUCCESSFULLY recorded baseline runs.
The published CAGE scores are reference-only and cannot be used as TEMARL runs.
"""
import csv
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
TARGETS = {
    "punch": {"name": "PUNCH Analyse Restore v1", "mean": -142.0, "sd": 44.0},
    "cybermonic": {"name": "Cybermonic KEEP", "mean": -193.0, "sd": 84.0},
}

def compile_rows(root=ROOT):
    rows = []
    for agent, target in TARGETS.items():
        for path in sorted((root / "results" / agent).glob("episodes_*_seed_*")):
            invfile = path / "invocation.json"
            summaryfile = path / "summary.json"
            if not summaryfile.exists() or not invfile.exists(): continue
            invocation = json.loads(invfile.read_text(encoding="utf-8"))
            if invocation.get("status") != "completed": continue
            summary = json.loads(summaryfile.read_text(encoding="utf-8"))
            reward = summary.get("reward") or {}
            avg = reward.get("mean")
            sd = reward.get("stdev")
            if not isinstance(avg, (int, float)): continue
            rows.append({
                "method": target["name"],
                "episodes": invocation["episodes"],
                "steps": invocation["steps_per_episode"],
                "seed": invocation["seed"],
                "published_mean": target["mean"],
                "published_sd": target["sd"],
                "reproduced_mean": avg,
                "reproduced_sd": sd,
                "difference_reproduced_minus_published": avg - target["mean"],
                "source": str(path.relative_to(root)),
            })
    return rows


def main():
    rows = compile_rows()
    output = ROOT / "results" / "comparison.csv"
    fields = ["method","episodes","steps","seed","published_mean","published_sd","reproduced_mean","reproduced_sd","difference_reproduced_minus_published","source"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fields)
        wr.writeheader()
        wr.writerows(rows)
    print(f"Wrote {len(rows)} completed baseline evaluations to {output}")
    if not rows: print("No reproduction results yet. Published numbers are not represented as reproduced.")

if __name__ == "__main__":
    main()
