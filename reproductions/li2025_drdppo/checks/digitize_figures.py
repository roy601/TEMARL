# -*- coding: utf-8 -*-
"""Measure the plateaus of the paper's Figs. 5 and 6 from the figure images embedded in the PDF (A13).

    python reproductions/li2025_drdppo/checks/digitize_figures.py [PDF]     # writes data/figure_values.json

The figures are raster images (2008 px wide) inside the article PDF (SHA-256 checked against SOURCES.md). Each
panel's y axis is calibrated from its tick marks (a linear fit to the printed tick labels; the largest residual
is reported) and each curve is found by its colour. The plateau is the median value of the curve's pixels over
episodes 400-500 (p10 and p90 are reported too). The images are not committed (licence CC BY-NC-ND 4.0).
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parent.parent
PDF_SHA256 = "6cc7f82febeeb9e365d17251661db49a22cbbba3927218da7351848ed76e6f9c"
OUT = ROOT / "data" / "figure_values.json"
DARK = 600                                    # sum of RGB below this = axis ink
COLORS = {"blue": (0, 0, 255), "red": (255, 0, 0), "green": (0, 128, 0), "orange": (255, 165, 0)}
EPISODES = [0, 100, 200, 300, 400, 500]


def _groups(idx):
    out, cur = [], []
    for i in idx:
        if cur and i != cur[-1] + 1:
            out.append(cur)
            cur = []
        cur.append(i)
    if cur:
        out.append(cur)
    return [float(np.mean(g)) for g in out]


def plateau(im, frame, labels_y, colors, ep_from=400, ep_to=500, tol=60):
    x0, x1, y0, y1 = frame
    dark = im.sum(-1) < DARK
    ty = _groups([y for y in range(y0 + 3, y1 - 2) if dark[y, x0 - 5:x0 - 2].all()])
    tx = _groups([x for x in range(x0 - 2, x1 + 3) if dark[y1 + 2:y1 + 5, x].all()])
    if len(ty) != len(labels_y) or len(tx) != len(EPISODES):
        raise RuntimeError(f"tick detection failed: {len(ty)} y ticks, {len(tx)} x ticks")
    ay, ax = np.polyfit(ty, labels_y, 1), np.polyfit(tx, EPISODES, 1)
    res = {"frame_px": list(frame), "y_ticks_px": ty, "y_labels": labels_y,
           "y_fit_max_residual": float(np.max(np.abs(np.polyval(ay, ty) - labels_y))), "curves": {}}
    for name, c in colors.items():
        ys, xs = np.nonzero(np.abs(im - np.array(c)).sum(-1) < tol)
        keep = (xs > x0 + 2) & (xs < x1 - 2) & (ys > y0 + 2) & (ys < y1 - 2)
        ys, xs = ys[keep], xs[keep]
        ep = np.polyval(ax, xs)
        sel = (ep >= ep_from) & (ep <= ep_to)
        if sel.sum() >= 20:
            v = np.polyval(ay, ys[sel])
            res["curves"][name] = {"median": float(np.median(v)), "p10": float(np.percentile(v, 10)),
                                   "p90": float(np.percentile(v, 90)), "pixels": int(sel.sum())}
    return res


def images(pdf: Path):
    import fitz
    from PIL import Image
    raw = pdf.read_bytes()
    if hashlib.sha256(raw).hexdigest() != PDF_SHA256:
        raise SystemExit("not the PDF recorded in SOURCES.md (SHA-256 differs)")
    d = fitz.open(stream=raw, filetype="pdf")

    def img(page, k):
        pix = fitz.Pixmap(d, d[page].get_images(full=True)[k][0])
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        return np.asarray(Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")).astype(int)
    return {"fig5": img(11, 0), "fig6": img(11, 1)}


def measure(pdf: Path) -> dict:
    im = images(pdf)
    two = {"blue": COLORS["blue"], "red": COLORS["red"]}
    return {
        "source": "Li, Zhao & Wu 2025, Sci. Rep. 15:16830, Figs. 5-6 (embedded images, page 12)",
        "pdf_sha256": PDF_SHA256, "episodes": [400, 500], "legend": {"blue": "DRD-PPO", "red": "Algorithm1 (Fig. 6) / "
                                                                    "DRD-PPO without F-honeypot (Fig. 5)",
                                                                    "green": "Algorithm2", "orange": "Algorithm3"},
        "fig6a_reward": plateau(im["fig6"], (71, 648, 8, 439), [0.0, -0.5, -1.0, -1.5, -2.0], COLORS),
        "fig6b_attack_probability": plateau(im["fig6"], (746, 1324, 8, 439), [0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35], COLORS),
        "fig6c_cost": plateau(im["fig6"], (1422, 1999, 8, 439), [1.8, 1.6, 1.4, 1.2, 1.0], COLORS),
        "fig5a_reward": plateau(im["fig5"], (103, 979, 8, 662), [0.0, -0.5, -1.0, -1.5, -2.0], two),
        "fig5b_attack_probability": plateau(im["fig5"], (1122, 1998, 8, 662), [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4], two),
    }


if __name__ == "__main__":
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "PDF" / "Li et al.—DRD-PPO.pdf"
    res = measure(pdf)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, v in res.items():
        if isinstance(v, dict) and "curves" in v:
            print(k, f"(axis residual {v['y_fit_max_residual']:.4f}):",
                  {c: round(s["median"], 3) for c, s in v["curves"].items()})
