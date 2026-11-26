from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_experiments import (
    FIGURES,
    PALETTE,
    POLICIES,
    RESULTS,
)


OUTPUT_STEM = "figure3_robustness_annotation_adjusted"


def configure_plotting() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
            "figure.dpi": 150,
        }
    )


def save_adjusted(fig: plt.Figure) -> None:
    output = FIGURES / OUTPUT_STEM
    fig.savefig(output.with_suffix(".svg"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".tiff"), dpi=600, bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_adjusted(primary: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Reproduce Figure 3 while moving only the fallback annotation."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.65))

    cado = primary[primary.policy == "CADO"]
    gate_means = cado[
        ["gate_insufficient", "gate_ood", "gate_noninferiority", "personalized_rate"]
    ].mean()
    gate_labels = ["Sparse", "OOD", "Non-inferior", "Personalized"]
    gate_colors = ["#8C8C8C", "#B35C44", "#4C78A8", "#2A9D8F"]
    axes[0].bar(np.arange(4), gate_means, color=gate_colors, width=0.72)
    axes[0].set_xticks(np.arange(4), gate_labels, rotation=28, ha="right")
    axes[0].set_ylabel("fraction of decisions")
    axes[0].set_title("Safety-gate routing", loc="left", fontsize=9, fontweight="bold")
    axes[0].text(
        -0.16, 1.05, "a", transform=axes[0].transAxes, fontsize=10, fontweight="bold"
    )

    unsafe = (
        summary[(summary.dataset == "ood") & (summary.metric == "unsafe_action_rate")]
        .set_index("policy")
        .loc[POLICIES]
    )
    unsafe_values = np.maximum(unsafe["mean"].to_numpy(), 1e-5)
    axes[1].bar(
        np.arange(4),
        unsafe_values,
        color=[PALETTE[policy] for policy in POLICIES],
        width=0.7,
    )
    axes[1].set_yscale("log")
    axes[1].set_xticks(np.arange(4), POLICIES, rotation=25, ha="right")
    axes[1].set_ylabel("unsafe action rate (log scale)")
    axes[1].set_title("Held-out attacker", loc="left", fontsize=9, fontweight="bold")
    cado_fallback = summary[
        (summary.dataset == "ood")
        & (summary.policy == "CADO")
        & (summary.metric == "fallback_rate")
    ].iloc[0]["mean"]
    axes[1].text(
        1.04,
        0.95,
        f"CADO fallback: {cado_fallback:.1%}",
        transform=axes[1].transAxes,
        ha="right",
        va="top",
        fontsize=7,
        color="#253746",
        clip_on=False,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1.5},
    )
    axes[1].text(
        -0.16, 1.05, "b", transform=axes[1].transAxes, fontsize=10, fontweight="bold"
    )

    fault_metric = (
        summary[
            (summary.dataset == "fault")
            & (summary.metric == "failed_action_persistence_steps")
        ]
        .set_index("policy")
        .loc[POLICIES]
    )
    axes[2].bar(
        np.arange(4),
        fault_metric["mean"],
        color=[PALETTE[policy] for policy in POLICIES],
        width=0.7,
    )
    axes[2].set_xticks(np.arange(4), POLICIES, rotation=25, ha="right")
    axes[2].set_ylabel("mean persistence (steps)")
    axes[2].set_title(
        "Actuation fault containment", loc="left", fontsize=9, fontweight="bold"
    )
    axes[2].text(
        -0.16, 1.05, "c", transform=axes[2].transAxes, fontsize=10, fontweight="bold"
    )

    for axis in axes:
        axis.grid(axis="y", color="#D9DEE3", linewidth=0.5)

    fig.tight_layout()
    save_adjusted(fig)


def main() -> None:
    configure_plotting()
    primary = pd.read_csv(RESULTS / "primary_episode_metrics.csv")
    summary = pd.read_csv(RESULTS / "summary_statistics.csv")
    plot_adjusted(primary, summary)
    print(FIGURES / f"{OUTPUT_STEM}.png")


if __name__ == "__main__":
    main()
