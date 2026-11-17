# -*- coding: utf-8 -*-
"""Writes TARGETS.csv from the DeepOP paper (Electronics 14(2):257). Run once, before any result."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []


def add(i, src, q, v, tol, primary=False):
    rows.append([i, src, q, v, tol, "yes" if primary else "no"])


T = "+-0.005 (mean of 10 seeds; CLOSE if inside our 95% CI)"
table3 = [("LSTM", "0.867", "0.779", "0.972", "0.865"), ("GRU", "0.841", "0.769", "0.913", "0.835"),
          ("Bayesian network", "0.608", "0.549", "0.695", "0.614"), ("Transformer", "0.857", "0.783", "0.956", "0.861"),
          ("DeepOP", "0.898", "0.822", "0.978", "0.894")]
for m, a, p, r, f in table3:
    k = m.split()[0]
    for name, v in (("accuracy", a), ("precision", p), ("recall", r), ("F1", f)):
        add(f"T3.{k}.{name}", "Table 3", f"{m}, {name}, next-step prediction", v, T,
            name == "F1" and m in ("DeepOP", "LSTM", "Transformer"))
for m, v in (("DeepOP", "0.767"), ("LSTM", "0.647"), ("Transformer", "0.663"), ("GRU", "0.617"), ("Bayesian", "0.393")):
    add(f"S44.J6.{m}", "Sec. 4.4 text (Fig. 6)", f"F1 at prediction step J = 6, {m}", v, T)
add("S44.gain_vs_LSTM", "Sec. 4.4 text", "DeepOP F1 gain over LSTM, relative %", "3.35", "+-0.01 (arithmetic check of the paper, no data)")
add("S44.gain_vs_GRU", "Sec. 4.4 text", "DeepOP F1 gain over GRU, relative %", "5.9", "+-0.01 (arithmetic check of the paper, no data)")
for m, v in (("DeepOP", "0.526"), ("Transformer", "0.421"), ("LSTM", "0.452"), ("GRU", "0.397"), ("Bayesian", "0.272")):
    add(f"S44.miss60.{m}", "Sec. 4.4 text (Fig. 7)", f"F1 at 60% missing techniques, {m}", v, T)
add("S44.miss0.DeepOP", "Sec. 4.4 text (Fig. 7)", "DeepOP F1 at 0% missing", "0.894", T)
add("T1.total", "Table 1", "attack-description samples used to retrain rcATT", "17302", "exact")
add("S31.coverage", "Sec. 3.1 text", "technique coverage of the 17,302 samples, %", "93.2", "exact")
add("S31.reports", "Sec. 3.1 text", "expert-annotated threat reports", "1500", "exact")
add("S31.reports_raw", "Sec. 3.1 text", "original threat reports collected 2006-2024 (approximately, as printed)", "2200", "exact")

with open(os.path.join(HERE, "TARGETS.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["id", "table_or_figure", "quantity", "published", "tolerance", "primary"])
    w.writerows(rows)
print(len(rows), "targets")
