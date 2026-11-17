# -*- coding: utf-8 -*-
"""Decision D4 check: how much do the frozen and the execution command orders differ?

    python camlds_real_full_arch/checks/order_check.py      # writes checks/ORDER_CHECK.txt

No model and no outcome is involved: only the two orders of the same 904 recorded commands.
  frozen     exec_index of steps.jsonl (CSV adjusted-time order), used by the protocol 1.2 encoders
  execution  execution_rank of camlds_real/out/sidecar/steps_link.jsonl (AttackMate record order)
Reported, per order pair: runs that differ, commands at another position, positions where what the
environment and the encoder see changes (label set, recorded zone, goal flag), adjacent transpositions
(Kendall distance), and the share of encoder inputs (W-command history windows) and next-command
targets that differ.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import pipeline as P  # noqa: E402

W = P.data.W


def runs_in(order):
    out = {}
    for f in P.ordered_folds(order):
        for split in ("train", "val", "test"):
            for r in P.runs(f, split):
                out[r["id"]] = r
    return out


def kendall(a, b):
    pos = {x: i for i, x in enumerate(b)}
    seq = [pos[x] for x in a]
    return sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])


def windows(cmds):
    return [tuple(cmds[max(0, t - W):t]) for t in range(1, len(cmds))]


def report() -> str:
    fr, ex = runs_in("frozen"), runs_in("execution")
    assert sorted(fr) == sorted(ex) and len(fr) == 34
    tot = defaultdict(int)
    per_run = []
    for rid in sorted(fr):
        a, b = fr[rid], ex[rid]
        assert sorted(a["source_rows"]) == sorted(b["source_rows"]), rid
        n = len(a["source_rows"])
        moved = sum(x != y for x, y in zip(a["source_rows"], b["source_rows"]))
        lab = sum(x != y for x, y in zip(a["commands"], b["commands"]))
        zone = sum(x != y for x, y in zip(a["positions"], b["positions"]))
        goal = sum(bool(x) != bool(y) for x, y in zip(a["goal"], b["goal"]))
        kd = kendall(a["source_rows"], b["source_rows"])
        wa, wb = windows(a["commands"]), windows(b["commands"])
        win = sum(x != y for x, y in zip(wa, wb))
        tgt = sum(x != y for x, y in zip(a["commands"][1:], b["commands"][1:]))
        for k, v in (("commands", n), ("moved", moved), ("labels", lab), ("zone", zone), ("goal", goal),
                     ("kendall", kd), ("points", len(wa)), ("windows", win), ("targets", tgt),
                     ("runs_differ", int(moved > 0)), ("runs_see_differ", int(lab + zone + goal > 0))):
            tot[k] += v
        if moved:
            where = [i for i, (x, y) in enumerate(zip(a["source_rows"], b["source_rows"])) if x != y]
            gf = [int(bool(a["goal"][i])) for i in where]
            ge = [int(bool(b["goal"][i])) for i in where]
            per_run.append(f"{rid} ({a['scenario']}): positions {where} of 0-{n - 1}; goal flag there "
                           f"frozen {gf}, execution {ge}; {moved} at another position, "
                           f"{kd} adjacent transposition(s); label set differs at {lab}, zone at {zone}, "
                           f"goal flag at {goal}; encoder windows differ {win}/{len(wa)}, targets {tgt}/{len(wa)}")
    L = ["Decision D4 check: frozen vs execution command order (no model, no outcome)", "",
         f"runs: 34; commands: {tot['commands']}",
         f"runs whose order differs: {tot['runs_differ']}",
         f"runs where what the environment or encoder sees differs (label set, zone or goal flag): {tot['runs_see_differ']}",
         f"commands at another position: {tot['moved']} ({100 * tot['moved'] / tot['commands']:.2f}%)",
         f"adjacent transpositions (Kendall distance, all runs): {tot['kendall']}",
         f"positions whose label set differs: {tot['labels']}; recorded zone differs: {tot['zone']}; "
         f"goal flag differs: {tot['goal']}",
         f"encoder inputs (history windows, W={W}) that differ: {tot['windows']} of {tot['points']} "
         f"({100 * tot['windows'] / tot['points']:.2f}%); next-command targets that differ: {tot['targets']} "
         f"({100 * tot['targets'] / tot['points']:.2f}%)", "", "runs that differ:"] + ["  " + s for s in per_run]
    return "\n".join(L) + "\n"


def main():
    text = report()
    (HERE / "ORDER_CHECK.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
