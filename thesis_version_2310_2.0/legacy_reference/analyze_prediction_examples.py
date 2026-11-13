"""Produce human-readable next-technique predictions from saved encoder checkpoints."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

import _frozen  # noqa: F401
from encoders_marl import build_encoder
from env_marl import EpisodeSource, SCRIPT_IDS
from pretrain_marl import windows
from vocab_v2 import ID_TO_META, ID_TO_TECHNIQUE, NUM_TECHNIQUES


ENCODERS = ("Transformer", "GRU", "LSTM")
DISPLAY_SEED = 910_000
DISPLAY_EPISODES = 100


def label(tid: int, short: bool = False) -> str:
    code = ID_TO_TECHNIQUE[int(tid)]
    meta = ID_TO_META[int(tid)]
    return code if short else f"{code} {meta['name']}"


def load_probabilities(results: Path, encoder: str, x: np.ndarray,
                       lengths: np.ndarray, batch: int = 2048) -> tuple[np.ndarray, list[float]]:
    checkpoint_paths = sorted((results / "checkpoints").glob(f"{encoder}_MAPPO_s*.pt"))
    if len(checkpoint_paths) != 10:
        raise RuntimeError(f"Expected 10 {encoder} MAPPO checkpoints, found {len(checkpoint_paths)}")
    probability_sum = np.zeros((len(x), NUM_TECHNIQUES), dtype=np.float64)
    seed_accuracies: list[float] = []
    for path in checkpoint_paths:
        payload = torch.load(path, map_location="cpu", weights_only=True)
        model = build_encoder(encoder)
        model.load_state_dict(payload["encoder"])
        model.eval()
        parts = []
        with torch.inference_mode():
            for start in range(0, len(x), batch):
                _, logits = model.pretrain_forward(
                    torch.as_tensor(x[start:start + batch]),
                    torch.as_tensor(lengths[start:start + batch]),
                )
                parts.append(torch.softmax(logits[:, :NUM_TECHNIQUES], -1).numpy())
        probs = np.concatenate(parts).astype(np.float64)
        probability_sum += probs
        seed_accuracies.append(float((probs.argmax(1) == TARGETS).mean()))
    return probability_sum / len(checkpoint_paths), seed_accuracies


def pct(value: float) -> str:
    return f"{100.0 * value:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", type=Path, help="Full-run results/main directory")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    results = args.results.resolve()
    out = args.out or (results / "PREDICTION_EXAMPLES.md")

    specs = EpisodeSource(DISPLAY_SEED, SCRIPT_IDS).take(DISPLAY_EPISODES)
    x, lengths, targets = windows(specs)
    global TARGETS
    TARGETS = targets

    probabilities: dict[str, np.ndarray] = {}
    seed_accuracies: dict[str, list[float]] = {}
    for encoder in ENCODERS:
        probabilities[encoder], seed_accuracies[encoder] = load_probabilities(
            results, encoder, x, lengths
        )

    lines = [
        "# Human-Readable Next-Technique Predictions",
        "",
        "This is a post-hoc descriptive analysis of the saved full-run checkpoints. "
        f"It uses {DISPLAY_EPISODES} newly generated CAM-LDS-derived episodes "
        f"(fixed seed {DISPLAY_SEED}), producing {len(targets):,} next-technique windows. "
        "For each architecture, probabilities are averaged over its 10 independently "
        "trained MAPPO checkpoints. IPPO is not repeated because the frozen encoder "
        "is pretrained before PPO and is identical for the matching encoder/seed.",
        "",
        "The percentages below are model confidence, not a guarantee that the event will occur. "
        "The display set is synthetic from the project's CAM-LDS Markov generator, not raw logs.",
        "",
        "## Primary Logged Validation Results",
        "",
        "These are the original full-run results averaged over ten seeds. Each seed used its own "
        "fixed validation stream. This is the primary architecture comparison.",
        "",
        "| Encoder | Top-1, mean +/- seed SD | Top-3, mean +/- seed SD |",
        "|---|---:|---:|",
    ]
    logged = {}
    for encoder in ENCODERS:
        records = []
        for path in sorted((results / "cells").glob(f"{encoder}_MAPPO_s*.json")):
            records.append(json.loads(path.read_text(encoding="utf-8"))["pretrain"])
        if len(records) != 10:
            raise RuntimeError(f"Expected 10 logged {encoder} records, found {len(records)}")
        top1 = np.asarray([r["top1"] for r in records], dtype=float)
        top3 = np.asarray([r["top3"] for r in records], dtype=float)
        logged[encoder] = (float(top1.mean()), float(top3.mean()))
        lines.append(
            f"| {encoder} | {pct(top1.mean())} +/- {100*top1.std(ddof=1):.2f} pp | "
            f"{pct(top3.mean())} +/- {100*top3.std(ddof=1):.2f} pp |"
        )

    lines += [
        "",
        "## Common Display-Set Accuracy",
        "",
        "This second table is a post-hoc checkpoint-ensemble demonstration on one common "
        "new stream. It is useful for showing probabilities, but it does not replace the "
        "primary logged validation table above.",
        "",
        "| Encoder | Ensemble Top-1 | Ensemble Top-3 | Individual-checkpoint Top-1, mean +/- SD |",
        "|---|---:|---:|---:|",
    ]
    for encoder in ENCODERS:
        p = probabilities[encoder]
        top1 = float((p.argmax(1) == targets).mean())
        top3 = float(np.any(np.argsort(p, axis=1)[:, -3:] == targets[:, None], axis=1).mean())
        a = np.asarray(seed_accuracies[encoder])
        lines.append(f"| {encoder} | {pct(top1)} | {pct(top3)} | {pct(a.mean())} +/- {100*a.std(ddof=1):.2f} pp |")

    lines += [
        "",
        "## Confidence and Reliability",
        "",
        "Confidence is the probability assigned to the selected Top-1 technique. "
        "Accuracy is how often that selected technique was correct inside the band.",
        "",
        "| Encoder | Confidence band | Windows | Coverage | Accuracy within band |",
        "|---|---|---:|---:|---:|",
    ]
    bands = ((0.0, 0.4, "Low (<40%)"), (0.4, 0.7, "Medium (40-70%)"),
             (0.7, 1.0000001, "High (>=70%)"))
    for encoder in ENCODERS:
        p = probabilities[encoder]
        conf, pred = p.max(1), p.argmax(1)
        for lo, hi, name in bands:
            mask = (conf >= lo) & (conf < hi)
            accuracy = float((pred[mask] == targets[mask]).mean()) if mask.any() else float("nan")
            acc_text = pct(accuracy) if mask.any() else "N/A"
            lines.append(f"| {encoder} | {name} | {int(mask.sum()):,} | {pct(mask.mean())} | {acc_text} |")

    # Fixed evenly spaced rows prevent result-dependent cherry-picking.
    example_idx = np.linspace(0, len(targets) - 1, num=10, dtype=int)
    lines += [
        "",
        "## Deterministic Example Predictions",
        "",
        "Examples are ten evenly spaced windows across the display set; they were not selected "
        "because a particular model was correct. The history column shows the last three observed techniques.",
        "",
        "| # | Recent observed history | Actual next technique | Transformer prediction | GRU prediction | LSTM prediction |",
        "|---:|---|---|---|---|---|",
    ]
    for number, idx in enumerate(example_idx, 1):
        hist = x[idx, :lengths[idx]][-3:]
        history_text = " -> ".join(label(int(v), short=True) for v in hist)
        cells = []
        for encoder in ENCODERS:
            pred = int(probabilities[encoder][idx].argmax())
            conf = float(probabilities[encoder][idx, pred])
            mark = "correct" if pred == int(targets[idx]) else "wrong"
            cells.append(f"{label(pred, short=True)} ({pct(conf)}, {mark})")
        lines.append(f"| {number} | {history_text} | {label(int(targets[idx]))} | " + " | ".join(cells) + " |")

    detail_idx = int(example_idx[len(example_idx) // 2])
    lines += [
        "",
        "## One Example in Detail: Top-3 Probabilities",
        "",
        f"Observed history: {' -> '.join(label(int(v)) for v in x[detail_idx, :lengths[detail_idx]][-4:])}",
        "",
        f"Actual next technique: **{label(int(targets[detail_idx]))}**",
        "",
        "| Encoder | Rank 1 | Rank 2 | Rank 3 | Actual technique probability |",
        "|---|---|---|---|---:|",
    ]
    for encoder in ENCODERS:
        p = probabilities[encoder][detail_idx]
        top = np.argsort(p)[-3:][::-1]
        cells = [f"{label(int(i))} ({pct(float(p[i]))})" for i in top]
        lines.append(f"| {encoder} | {' | '.join(cells)} | {pct(float(p[targets[detail_idx]]))} |")

    lines += [
        "",
        "## Interpretation Rules",
        "",
        "- Top-1 means the single highest-probability next ATT&CK technique.",
        "- Top-3 means the actual next technique appears among the three highest probabilities.",
        "- A wrong prediction can still assign meaningful probability to the actual technique.",
        "- These probabilities concern next-technique prediction only; they are not dwell, asset-protection, or attack-risk probabilities.",
        "- This additional checkpoint-ensemble analysis was not the original pretraining evaluation and should be labelled post hoc.",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    metadata = {
        "display_seed": DISPLAY_SEED,
        "display_episodes": DISPLAY_EPISODES,
        "windows": int(len(targets)),
        "checkpoints_per_encoder": 10,
        "results": str(results),
    }
    out.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
