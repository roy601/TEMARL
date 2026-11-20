# -*- coding: utf-8 -*-
"""Read the plotted values of Wang et al. 2020, Figs. 10-14, from the vector drawings in the article PDF.

    python reproductions/wang2020/checks/extract_figures.py [PDF]     # writes data/figure_values.json

The figures are vector graphics (not images), so each curve is a polyline whose vertices are the plotted
points. Each panel's axes are calibrated from its tick marks: a linear fit of the tick positions to the
printed tick labels (the labels themselves are drawn as glyph outlines, so their values are typed here from
the page; the number of ticks found must equal the number of labels). The largest fit residual is reported.
Each curve is identified by its colour; the legend order (green, red, blue, magenta = the four FNR/FPR
settings) is checked against the legend's line samples. Nothing here is a result of ours: these are the
published numbers, measured. The PDF is not committed (licence CC BY 4.0, but the file is the publisher's).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent.parent
PDF_SHA256 = "4e62488b763d328e89dd677d4cf20491d13ba6de685e996c4f1f9f34b1eb34ff"
OUT = ROOT / "data" / "figure_values.json"
SETTINGS = {(0.0, 1.0, 0.0): "FNR=0.05,FPR=0.02", (1.0, 0.0, 0.0): "FNR=0.10,FPR=0.06",
            (0.0, 0.0, 1.0): "FNR=0.15,FPR=0.10", (1.0, 0.0, 1.0): "FNR=0.20,FPR=0.14"}
LEGEND_ORDER = ["FNR=0.05,FPR=0.02", "FNR=0.10,FPR=0.06", "FNR=0.15,FPR=0.10", "FNR=0.20,FPR=0.14"]
STEPS = [0, 2000, 5000, 10000, 20000, 30000]
# panel: page index, approximate frame (x0, y0, x1, y1) in PDF points, x tick labels, y tick labels (bottom to top)
PANELS = {
    "fig10_static": (9, (320.54, 553.45, 532.78, 695.45), list(range(1, 22)), [round(0.1 * i, 1) for i in range(11)],
                     "x = static policy number (1-21), y = dsp"),
    "fig11_random_dynamic": (10, (59.12, 179.62, 269.32, 334.86), list(range(1, 11)), [round(0.1 * i, 1) for i in range(11)],
                             "x = experiment number (1-10), y = dsp"),
    "fig12_following_alarm": (10, (62.18, 540.46, 265.99, 689.83), list(range(1, 11)), [round(0.1 * i, 1) for i in range(11)],
                              "x = experiment number (1-10), y = dsp"),
    "fig13_q_learning": (10, (320.88, 179.97, 525.72, 322.13), STEPS, [round(0.5 + 0.05 * i, 2) for i in range(9)],
                         "x = Q-learning training steps, y = dsp"),
    "fig14_training_time": (10, (326.26, 565.07, 526.11, 695.76), STEPS, [1000 * i for i in range(12)],
                            "x = Q-learning training steps, y = training time (s)"),
}


def _close(a, b, tol=0.6):
    return abs(a - b) < tol


def panel(page, frame, xlab, ylab):
    x0, y0, x1, y1 = frame
    dr = page.get_drawings()
    yt, xt, curves, legend = set(), set(), {}, []
    for d in dr:
        if d["type"] != "s":
            continue
        col = tuple(round(v, 2) for v in (d.get("color") or ()))
        items = d["items"]
        if col == (0.0, 0.0, 0.0) and len(items) == 1 and items[0][0] == "l":
            a, b = items[0][1:]
            if abs(a.y - b.y) < 1e-3 and _close(a.x, x0, 0.05) and 1 < abs(b.x - a.x) < 4 and y0 - 1 < a.y < y1 + 1:
                yt.add(round(a.y, 3))
            if abs(a.x - b.x) < 1e-3 and _close(a.y, y1, 0.05) and 1 < abs(b.y - a.y) < 4 and x0 - 1 < a.x < x1 + 1:
                xt.add(round(a.x, 3))
        elif col in SETTINGS and all(it[0] == "l" for it in items):
            pts = [items[0][1]] + [it[2] for it in items]
            xs, ys = np.array([p.x for p in pts]), np.array([p.y for p in pts])
            if xs.min() < x0 - 1 or xs.max() > x1 + 1 or ys.min() < y0 - 1 or ys.max() > y1 + 1:
                continue
            if len(items) == 1 and abs(ys[0] - ys[1]) < 1e-3 and (xs[1] - xs[0]) < 15:
                legend.append((ys[0], SETTINGS[col]))                     # legend line sample
            elif len(items) > len(curves.get(SETTINGS[col], ((),))[0]) - 1:  # the curve is the longest path
                curves[SETTINGS[col]] = (xs, ys)                               # (marker outlines are short)
    yt, xt = sorted(yt, reverse=True), sorted(xt)                         # y: bottom (largest) first
    if len(yt) != len(ylab) or len(xt) != len(xlab):
        raise RuntimeError(f"tick detection failed: {len(yt)} y ticks for {len(ylab)} labels, {len(xt)} x ticks for {len(xlab)}")
    if [s for _, s in sorted(legend)] != LEGEND_ORDER:
        raise RuntimeError(f"legend order differs: {sorted(legend)}")
    ay, ax = np.polyfit(yt, ylab, 1), np.polyfit(xt, xlab, 1)
    out = {"frame_pt": [x0, y0, x1, y1], "y_ticks_pt": yt, "y_labels": ylab, "x_ticks_pt": xt, "x_labels": xlab,
           "y_fit_max_residual": float(np.max(np.abs(np.polyval(ay, yt) - ylab))),
           "x_fit_max_residual": float(np.max(np.abs(np.polyval(ax, xt) - xlab))), "curves": {}}
    for name in LEGEND_ORDER:
        xs, ys = curves[name]
        out["curves"][name] = {"x": [float(v) for v in np.polyval(ax, xs)], "y": [float(v) for v in np.polyval(ay, ys)]}
    return out


def measure(pdf: Path) -> dict:
    import pymupdf
    raw = pdf.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PDF_SHA256:
        raise SystemExit("not the PDF recorded in SOURCES.md (SHA-256 differs)")
    doc = pymupdf.open(stream=raw, filetype="pdf")
    res = {"source": "Wang et al. 2020, IEEE Access 8:35792-35804, Figs. 10-14 (vector drawings, pages 10-11)",
           "pdf_sha256": PDF_SHA256, "legend": LEGEND_ORDER}
    for key, (pg, frame, xlab, ylab, what) in PANELS.items():
        res[key] = {"what": what, **panel(doc[pg], frame, xlab, ylab)}
    return res


if __name__ == "__main__":
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "PDF" / "Wang et al. 2020,.pdf"
    res = measure(pdf)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, v in res.items():
        if isinstance(v, dict) and "curves" in v:
            print(f"{k}: axis residual x {v['x_fit_max_residual']:.4g}, y {v['y_fit_max_residual']:.4g}")
            for s, c in v["curves"].items():
                print(f"   {s}: " + " ".join(f"{y:.3f}" for y in c["y"]))
