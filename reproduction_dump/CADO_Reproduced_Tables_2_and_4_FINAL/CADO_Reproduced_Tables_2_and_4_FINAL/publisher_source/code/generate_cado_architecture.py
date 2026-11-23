"""Generate a publication-ready CADO architecture diagram.

Outputs are created next to this script as editable SVG/PDF and high-resolution
PNG/TIFF files. All coordinates use a normalized canvas so spacing remains
consistent when the physical figure size is changed.
"""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


# Final double-column size: 183 mm x 98 mm.
FIG_WIDTH_MM = 183
FIG_HEIGHT_MM = 98
FIGURE_SIZE_IN = (FIG_WIDTH_MM / 25.4, FIG_HEIGHT_MM / 25.4)

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "font.size": 7.0,
        "font.style": "normal",
        "font.weight": "normal",
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


COLORS = {
    "ink": "#263746",
    "muted": "#657786",
    "rule": "#A8B6C3",
    "neutral_fill": "#F7F9FB",
    "neutral_card": "#FFFFFF",
    "blue": "#2C6FA3",
    "blue_fill": "#F1F6FA",
    "teal": "#16867E",
    "teal_fill": "#F1F9F8",
    "gold": "#B87312",
    "gold_rule": "#C99543",
    "gold_fill": "#FCF8F1",
    "red": "#B94E3A",
    "white": "#FFFFFF",
}


def rounded_box(
    ax,
    x,
    y,
    w,
    h,
    *,
    edge,
    face="white",
    linewidth=0.9,
    radius=0.010,
    zorder=1,
):
    """Add a consistently padded rounded rectangle."""
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        linewidth=linewidth,
        edgecolor=edge,
        facecolor=face,
        joinstyle="round",
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def label(
    ax,
    x,
    y,
    text,
    *,
    size=7.0,
    color=None,
    weight="normal",
    ha="center",
    va="center",
    linespacing=1.12,
    bbox=None,
    zorder=5,
):
    """Add upright sans-serif text with consistent line spacing."""
    return ax.text(
        x,
        y,
        text,
        fontsize=size,
        color=color or COLORS["ink"],
        fontstyle="normal",
        fontweight=weight,
        ha=ha,
        va=va,
        linespacing=linespacing,
        rotation=0,
        bbox=bbox,
        zorder=zorder,
    )


def arrow(ax, start, end, *, color, linewidth=1.25, mutation_scale=10, zorder=3):
    """Draw a straight, filled directional arrow between module boundaries."""
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=mutation_scale,
        linewidth=linewidth,
        color=color,
        shrinkA=0,
        shrinkB=0,
        connectionstyle="arc3,rad=0",
        capstyle="round",
        joinstyle="round",
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def build_figure():
    fig = plt.figure(figsize=FIGURE_SIZE_IN, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ------------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------------
    rounded_box(
        ax,
        0.020,
        0.205,
        0.165,
        0.720,
        edge=COLORS["rule"],
        face=COLORS["neutral_fill"],
        linewidth=1.05,
        radius=0.012,
    )
    label(
        ax,
        0.042,
        0.865,
        "INPUTS",
        size=8.2,
        color=COLORS["blue"],
        weight="bold",
        ha="left",
    )

    input_items = ["IDS / IPS", "WAF", "EDR", "Firewall / SDN", "Threat intelligence"]
    input_y = [0.750, 0.635, 0.520, 0.405, 0.290]
    for text, y in zip(input_items, input_y):
        rounded_box(
            ax,
            0.040,
            y,
            0.125,
            0.082,
            edge=COLORS["rule"],
            face=COLORS["white"],
            linewidth=0.85,
            radius=0.008,
        )
        label(ax, 0.1025, y + 0.041, text, size=6.9)

    # ------------------------------------------------------------------
    # CADO control plane
    # ------------------------------------------------------------------
    rounded_box(
        ax,
        0.225,
        0.205,
        0.500,
        0.765,
        edge=COLORS["teal"],
        face=COLORS["teal_fill"],
        linewidth=1.15,
        radius=0.014,
    )
    label(
        ax,
        0.250,
        0.905,
        "CADO CONTROL PLANE",
        size=8.5,
        color=COLORS["teal"],
        weight="bold",
        ha="left",
    )

    # Normalize stage.
    rounded_box(
        ax,
        0.255,
        0.505,
        0.120,
        0.255,
        edge=COLORS["blue"],
        face=COLORS["blue_fill"],
        linewidth=1.0,
        radius=0.010,
    )
    label(ax, 0.315, 0.690, "NORMALIZE", size=7.2, color=COLORS["blue"], weight="bold")
    label(
        ax,
        0.315,
        0.605,
        "Adapters → NSE\ncontext | confidence\nprovenance",
        size=6.3,
        weight="bold",
        linespacing=1.18,
    )

    # Constrained decision stage.
    rounded_box(
        ax,
        0.405,
        0.390,
        0.190,
        0.490,
        edge=COLORS["teal"],
        face=COLORS["white"],
        linewidth=1.05,
        radius=0.010,
    )
    label(
        ax,
        0.500,
        0.822,
        "CONSTRAINED DECISION",
        size=7.0,
        color=COLORS["teal"],
        weight="bold",
    )

    rounded_box(
        ax,
        0.430,
        0.675,
        0.140,
        0.090,
        edge="#72AAA5",
        face=COLORS["teal_fill"],
        linewidth=0.85,
        radius=0.008,
    )
    label(ax, 0.500, 0.720, "Consensus (a_c)", size=6.5, weight="bold")

    rounded_box(
        ax,
        0.430,
        0.545,
        0.140,
        0.090,
        edge="#72AAA5",
        face=COLORS["teal_fill"],
        linewidth=0.85,
        radius=0.008,
    )
    label(ax, 0.500, 0.590, "Residual (a_p), ±1 level", size=6.25)

    label(ax, 0.500, 0.485, "ADMISSION GATES", size=6.2, color=COLORS["muted"], weight="bold")
    label(
        ax,
        0.500,
        0.435,
        "n ≥ 6  |  OOD ≤ 2.20\nconf. ≥ 0.55  |  LCB ≥ 0",
        size=5.9,
        color=COLORS["ink"],
        linespacing=1.20,
    )

    # Typed deception action transaction.
    rounded_box(
        ax,
        0.625,
        0.470,
        0.072,
        0.320,
        edge=COLORS["teal"],
        face=COLORS["white"],
        linewidth=1.05,
        radius=0.010,
    )
    label(ax, 0.661, 0.725, "DAT", size=7.2, color=COLORS["teal"], weight="bold")
    label(
        ax,
        0.661,
        0.605,
        "typed\nscope\nTTL\nverify\nrollback",
        size=6.4,
        weight="bold",
        linespacing=1.16,
    )

    # Forward control flow. Endpoints stop outside each border.
    arrow(ax, (0.185, 0.635), (0.248, 0.635), color=COLORS["blue"], linewidth=1.35)
    arrow(ax, (0.375, 0.635), (0.398, 0.635), color=COLORS["teal"], linewidth=1.25)
    arrow(ax, (0.595, 0.635), (0.618, 0.635), color=COLORS["teal"], linewidth=1.25)

    # ------------------------------------------------------------------
    # H4 actuation
    # ------------------------------------------------------------------
    rounded_box(
        ax,
        0.765,
        0.205,
        0.215,
        0.720,
        edge=COLORS["gold_rule"],
        face=COLORS["gold_fill"],
        linewidth=1.05,
        radius=0.012,
    )
    label(
        ax,
        0.790,
        0.865,
        "H4 ACTUATION",
        size=8.2,
        color=COLORS["gold"],
        weight="bold",
        ha="left",
    )

    cards = [
        (0.790, 0.655, "Honeypoint", "near-asset\ndecoy"),
        (0.880, 0.655, "Honeyproxy", "redirect /\nobserve"),
        (0.790, 0.445, "Honeytrace", "persistent\ntrace"),
        (0.880, 0.445, "Honeycenter", "coordinate\nH4"),
    ]
    for x, y, title, subtitle in cards:
        rounded_box(
            ax,
            x,
            y,
            0.077,
            0.145,
            edge=COLORS["gold_rule"],
            face=COLORS["white"],
            linewidth=0.85,
            radius=0.008,
        )
        label(ax, x + 0.0385, y + 0.095, title, size=6.0, color=COLORS["gold"], weight="bold")
        label(ax, x + 0.0385, y + 0.046, subtitle, size=5.5, linespacing=1.12)

    label(
        ax,
        0.8725,
        0.315,
        "LEAST-SCOPE DEPLOYMENT",
        size=6.25,
        color=COLORS["gold"],
        weight="bold",
    )
    arrow(ax, (0.725, 0.635), (0.758, 0.635), color=COLORS["gold"], linewidth=1.35)

    # ------------------------------------------------------------------
    # Assurance and audit bus
    # ------------------------------------------------------------------
    rounded_box(
        ax,
        0.225,
        0.055,
        0.755,
        0.105,
        edge="#C2CDD6",
        face=COLORS["neutral_fill"],
        linewidth=0.95,
        radius=0.010,
    )
    label(ax, 0.250, 0.108, "ASSURANCE", size=7.2, weight="bold", ha="left")

    bus_y = 0.108
    bus_x0, bus_x1 = 0.365, 0.942
    ax.plot([bus_x0, bus_x1], [bus_y, bus_y], color=COLORS["rule"], linewidth=0.85, zorder=2)

    events = [
        (0.385, "ACK", COLORS["teal"]),
        (0.490, "state", COLORS["teal"]),
        (0.595, "telemetry", COLORS["teal"]),
        (0.710, "expiry", COLORS["teal"]),
        (0.815, "rollback", COLORS["red"]),
        (0.925, "audit", COLORS["gold"]),
    ]
    for x, text, color in events:
        ax.scatter([x], [bus_y], s=18, color=color, edgecolor="white", linewidth=0.45, zorder=4)
        label(
            ax,
            x + 0.013,
            bus_y,
            text,
            size=5.9,
            ha="left",
            bbox={"facecolor": COLORS["neutral_fill"], "edgecolor": "none", "pad": 0.20},
        )

    # Audit descends from H4; failure/expiry returns to DAT. Labels remain horizontal.
    arrow(ax, (0.925, 0.205), (0.925, 0.166), color=COLORS["gold"], linewidth=1.15, mutation_scale=9)
    arrow(ax, (0.661, 0.166), (0.661, 0.462), color=COLORS["red"], linewidth=1.15, mutation_scale=9)
    label(
        ax,
        0.674,
        0.285,
        "failure / expiry",
        size=5.8,
        color=COLORS["red"],
        ha="left",
    )

    return fig


def save_architecture(output_dir: Path, stem: str = "figure1_architecture") -> None:
    """Export Figure 1 to the experiment figure directory."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_stem = output_dir / stem
    fig = build_figure()
    fig.savefig(output_stem.with_suffix(".svg"), facecolor="white")
    fig.savefig(output_stem.with_suffix(".pdf"), facecolor="white")
    fig.savefig(output_stem.with_suffix(".png"), dpi=300, facecolor="white")
    fig.savefig(output_stem.with_suffix(".tiff"), dpi=600, facecolor="white", format="tiff")
    plt.close(fig)


def main():
    save_architecture(Path(__file__).resolve().parents[1] / "figures")


if __name__ == "__main__":
    main()
