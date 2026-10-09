# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- Markdown reports
======================================
Writes every table the thesis needs, with the caveats attached to the numbers
rather than buried in a footnote:

  RESULTS.md         headline: audit, budget, prediction, ladder, deception
  DATA_AUDIT.md      corpus, splits, label support, similarity, coverage
  WINDOW_RESULTS.md  window-length sensitivity and history coverage
  PATIENCE_RESULTS.md the stopping-rule study
  TRAINING_CURVES.md every recorded validation point
  PREDICTION_EXAMPLES.md readable predicted-vs-true label sets
  RL_RESULTS.md      deception, ladder-relative, context window
  STATISTICS.md      every contrast with Holm correction

Invoked by `run_study.py --stage report`, or directly:
    python report_study.py --output results/run
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from typing import Dict, List, Optional, Sequence

import numpy as np

import stats_cmd as St
import study_spec as SPEC

HERE = os.path.dirname(os.path.abspath(__file__))


def read_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _w(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _load_cells(out: str, sub: str) -> List[dict]:
    root = os.path.join(out, sub)
    if not os.path.isdir(root):
        return []
    cells = []
    for name in sorted(os.listdir(root)):
        p = os.path.join(root, name, "result.json")
        if os.path.exists(p):
            cells.append(read_json(p))
    return cells


def _fmt(v, nd=4):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _ms(vals: Sequence[float], nd=4) -> str:
    v = np.asarray(list(vals), float)
    if v.size == 0:
        return "-"
    sd = v.std(ddof=1) if v.size > 1 else 0.0
    return f"{v.mean():.{nd}f} +/- {sd:.{nd}f}"


HEADER_CAVEAT = """
> **Scope.** Source-derived annotated playbook sequences from the AttackBed
> repository, evaluated in a simulator. NOT real-world attacker telemetry. The
> environment's engagement, movement and exposure rules are modelling
> assumptions, not measured quantities.
>
> **Representation.** Command-level and multi-label: one step is one annotated
> attacker command, and the techniques within a command are an unordered set.
> Within-command label order is discarded by construction, so the 34.9%
> label-order artefact of the earlier flattened corpus cannot be learned here.
>
> **Not comparable with the earlier study.** Its Top-1 scored one token out of
> a flattened stream; these targets are label SETS over command transitions.
> Its dwell counted label-steps; here dwell counts commands. Different units.
>
> **Sample size.** 36 playbooks from 7 scenarios. Seeds, environment repeats
> and prediction windows are not independent attack campaigns.
"""


# ── data audit ──────────────────────────────────────────────────────────────

def report_audit(out: str) -> str:
    p = os.path.join(out, "audit.json")
    if not os.path.exists(p):
        return ""
    a = read_json(p)
    L = ["# Data audit", HEADER_CAVEAT, "",
         "## Corpus", ""]
    c = a["corpus"]
    for k in ("source", "provenance", "n_playbooks", "n_commands",
              "n_technique_labels", "n_unlabelled_commands",
              "labels_per_command_histogram", "distinct_parent_techniques"):
        if k in c:
            L.append(f"- **{k}**: {c[k]}")
    eq = c.get("equality_with_flat_corpus", {})
    L += ["", f"- **reproduces the earlier flat corpus exactly**: "
              f"`{eq.get('identical')}` "
              f"(representation is the only thing that changed)", ""]

    L += ["## Splits", "",
          "| split | runs | groups | commands | targets | unseen transitions % |",
          "|---|---:|---:|---:|---:|---:|"]
    for part in ("train", "validation", "test"):
        v = a["coverage"][part]
        L.append(f"| {part} | {v['runs']} | {v['independent_groups']} | "
                 f"{v['commands']} | {v['prediction_targets']} | "
                 f"{v['unseen_transition_occurrence_pct']:.2f} |")
    L += ["", "Scenarios per split: "
          + "; ".join(f"{k} {v}" for k, v in a["scenarios_per_split"].items()), ""]
    if a.get("notes"):
        L += ["Notes:", ""] + [f"- {n}" for n in a["notes"]] + [""]

    L += ["## Command structure", "",
          "| split | mean labels/command | max | multi-label % | self-loop % |",
          "|---|---:|---:|---:|---:|"]
    for part in ("train", "validation", "test"):
        v = a["coverage"][part]
        L.append(f"| {part} | {v['mean_labels_per_command']:.3f} | "
                 f"{v['max_labels_per_command']} | "
                 f"{v['multi_label_command_pct']:.1f} | {v['self_loop_pct']:.1f} |")

    L += ["", "## Nearest training run (THE headline caveat)", "",
          "A held-out run with high overlap is a near-copy of a training run. "
          "Its score measures prediction within a known scenario variant, not "
          "generalisation to a new campaign.", "",
          "| split | run | nearest training run | command-bigram Jaccard |",
          "|---|---|---|---:|"]
    for s in a["similarity"]:
        L.append(f"| {s['split']} | `{s['run']}` | `{s['nearest_training_run']}` "
                 f"| {s['command_bigram_jaccard']:.3f} |")

    ls = a["label_support"]
    L += ["", "## Label support", "",
          f"- labels in vocabulary: {ls['n_labels_in_vocabulary']}",
          f"- labels present in corpus: {ls['n_labels_in_corpus']}",
          f"- labels in train: {ls['n_labels_in_train']}, in test: {ls['n_labels_in_test']}",
          f"- **test labels never seen in training**: "
          f"{len(ls['test_labels_absent_from_train'])} "
          f"{ls['test_labels_absent_from_train']}",
          "", "Macro-F1 averages only labels with support in the evaluated "
              "split; the averaged-label count is reported beside every score.",
          ""]

    L += ["## Window coverage", "",
          "`full history %` is the share of prediction targets whose entire "
          "available history fits inside the window. A window may only be "
          "called \"full history\" at 100%.", "",
          "| window | split | targets | full history % | mean available | truncated |",
          "|---:|---|---:|---:|---:|---:|"]
    for w in sorted(a["window_coverage"], key=int):
        for part in ("train", "validation", "test"):
            v = a["window_coverage"][w][part]
            L.append(f"| {w} | {part} | {v['n_targets']} | "
                     f"{v['full_history_pct']:.1f} | {v['mean_available']:.1f} | "
                     f"{v['truncated_targets']} |")

    L += ["", "## Caveats", ""] + [f"- {c}" for c in a["caveats"]]
    env = a.get("environment", {})
    L += ["", "## Environment", "",
          f"- python {env.get('python')}, torch {env.get('torch')}, "
          f"numpy {env.get('numpy')}",
          f"- {env.get('platform')}",
          f"- CUDA: {env.get('cuda_device') or 'not available'}", ""]
    return "\n".join(L)


# ── budget / patience ───────────────────────────────────────────────────────

def report_patience(out: str) -> str:
    p = os.path.join(out, "budget.json")
    if not os.path.exists(p):
        return ""
    b = read_json(p)
    ps, bs = b["patience_selection"], b["budget_selection"]
    L = ["# Patience and budget selection", HEADER_CAVEAT, "",
         "Both are chosen on VALIDATION only, from pilot runs, before any main "
         "run. The numbers below are OUR protocol, not published optima.", "",
         f"- pilot cap: **{b['cap']}** updates across **{b['n_pilot_cells']}** cells",
         f"- rule: {ps['rule']}",
         f"- **chosen patience: {b['shared_patience']} validation checks** "
         f"(= {b['shared_patience'] * SPEC.VAL_EVERY_UPDATES} updates without "
         f"a meaningful improvement)", "",
         "## Mean validation BCE by candidate patience", "",
         "| patience (checks) | updates | mean validation BCE |",
         "|---:|---:|---:|"]
    for k, v in sorted(ps["mean_validation_bce_by_patience"].items(),
                       key=lambda kv: int(kv[0])):
        L.append(f"| {k} | {int(k) * SPEC.VAL_EVERY_UPDATES} | {v:.6f} |")

    L += ["", "## Shared update budget", "",
          f"- rule: {bs['rule']}",
          f"- **shared budget: {bs['shared_update_budget']} updates**", "",
          "| configuration | median validation-best update |", "|---|---:|"]
    for k, v in sorted(bs["median_best_update_by_configuration"].items()):
        L.append(f"| `{k}` | {v:.0f} |")

    unresolved = b.get("convergence_unresolved") or []
    L += ["", "## Convergence", ""]
    if unresolved:
        L += ["**Unresolved.** These configurations reached the pilot cap with "
              "their best still near the end, so convergence is NOT "
              "established and the budget is a heuristic:", ""]
        L += [f"- `{k}`" for k in unresolved]
    else:
        L += ["No configuration had its validation best in the last 10% of the "
              "cap, so the cap did not visibly truncate training. This is "
              "evidence against truncation, not proof of convergence."]

    L += ["", "## Per-configuration stopping simulation", "",
          "Each pilot trajectory replayed under every candidate rule, using "
          "only information available before its own simulated stop.", "",
          "| configuration | patience | stopped at | selected update | val BCE | triggered |",
          "|---|---:|---:|---:|---:|---|"]
    for cfgk, per in sorted(ps["per_configuration"].items()):
        for pat, sim in sorted(per.items(), key=lambda kv: int(kv[0])):
            L.append(f"| `{cfgk}` | {pat} | {sim['stopped_at_update']} | "
                     f"{sim['selected_update']} | {sim['validation_bce']:.6f} | "
                     f"{sim['triggered']} |")
    return "\n".join(L)


# ── prediction ──────────────────────────────────────────────────────────────

def _pred_index(cells: List[dict]):
    idx = defaultdict(dict)
    for c in cells:
        idx[(c["arm"], c["window"], c["sampler"])][c["seed"]] = c
    return idx


def _metric(cell: dict, metric: str, split="test", which="primary"):
    return cell[which][split][metric]


def report_prediction(out: str) -> str:
    cells = _load_cells(out, "prediction")
    if not cells:
        return ""
    idx = _pred_index(cells)
    M = SPEC.PRIMARY_PREDICTION_METRIC

    L = ["# Prediction results", HEADER_CAVEAT, "",
         f"Primary metric: **{M}** on the held-out test split, at the "
         "validation-selected threshold, from the validation-best checkpoint. "
         "The final checkpoint is reported as secondary.", "",
         "`precision@1` is the nearest relative of the earlier study's Top-1, "
         "and is still a different measurement. Do not tabulate them together.",
         "",
         "## Main table (mean +/- SD across seeds)", "",
         "| arm | window | sampler | seeds | micro-F1 | macro-F1 | exact-set | p@1 | r@3 | BCE |",
         "|---|---:|---|---:|---|---|---|---|---|---|"]
    for (arm, w, samp), per in sorted(idx.items()):
        seeds = sorted(per)
        g = lambda k: [_metric(per[s], k) for s in seeds]
        L.append(f"| {arm} | {w} | {samp} | {len(seeds)} | "
                 f"{_ms(g('micro_f1'))} | {_ms(g('macro_f1'))} | "
                 f"{_ms(g('exact_set_accuracy'))} | {_ms(g('precision_at_1'))} | "
                 f"{_ms(g('recall_at_3'))} | {_ms(g('bce'), 5)} |")

    L += ["", "## Equal-weight views", "",
          "Pooled metrics weight long runs more heavily (one window per "
          "command). These weight each run, and each scenario, equally.", "",
          "| arm | window | sampler | pooled micro-F1 | run-macro | scenario-macro |",
          "|---|---:|---|---|---|---|"]
    for (arm, w, samp), per in sorted(idx.items()):
        seeds = sorted(per)
        pooled = [_metric(per[s], "micro_f1") for s in seeds]
        runm = [_metric(per[s], "run_macro_micro_f1") for s in seeds]
        scn = [per[s]["primary"]["test"].get("scenario_macro_micro_f1")
               for s in seeds]
        scn = [x for x in scn if x is not None]
        L.append(f"| {arm} | {w} | {samp} | {_ms(pooled)} | {_ms(runm)} | "
                 f"{_ms(scn) if scn else '-'} |")

    L += ["", "## Secondary: final checkpoint", "",
          "| arm | window | sampler | micro-F1 (final) | micro-F1 (val-best) |",
          "|---|---:|---|---|---|"]
    for (arm, w, samp), per in sorted(idx.items()):
        seeds = sorted(per)
        fin = [_metric(per[s], "micro_f1", which="secondary") for s in seeds]
        bst = [_metric(per[s], "micro_f1") for s in seeds]
        L.append(f"| {arm} | {w} | {samp} | {_ms(fin)} | {_ms(bst)} |")

    L += ["", "## Thresholds and training effort", "",
          "| arm | window | sampler | threshold | best update | updates | "
          "mean window exposure | seconds |",
          "|---|---:|---|---|---|---|---|---|"]
    for (arm, w, samp), per in sorted(idx.items()):
        seeds = sorted(per)
        L.append(f"| {arm} | {w} | {samp} | "
                 f"{_ms([per[s]['primary']['threshold'] for s in seeds], 2)} | "
                 f"{_ms([per[s]['best_update'] for s in seeds], 0)} | "
                 f"{_ms([per[s]['updates_completed'] for s in seeds], 0)} | "
                 f"{_ms([per[s]['exposure']['mean'] for s in seeds], 1)} | "
                 f"{_ms([per[s]['seconds'] for s in seeds], 0)} |")

    L += ["", "## Capacity, runtime and memory", "",
          "Trainable parameters are matched across arms; the positional-encoding "
          "buffer is NOT trainable and grows with the window, so a window "
          "result is never a capacity result.", "",
          "| arm | window | trunk params | total trainable | PE buffer elements | peak MB |",
          "|---|---:|---:|---:|---:|---:|"]
    seen = set()
    for (arm, w, samp), per in sorted(idx.items()):
        if (arm, w) in seen:
            continue
        seen.add((arm, w))
        p = per[sorted(per)[0]]["parameters"]
        mem = np.mean([per[s]["peak_memory_mb"] for s in sorted(per)])
        L.append(f"| {arm} | {w} | {p['trunk_trainable']} | "
                 f"{p['total_trainable']} | "
                 f"{p['non_trainable_buffer_elements']} | {mem:.1f} |")
    return "\n".join(L)


def report_windows(out: str) -> str:
    cells = [c for c in _load_cells(out, "prediction") if c["sampler"] == "ordinary"]
    if not cells:
        return ""
    idx = _pred_index(cells)
    M = SPEC.PRIMARY_PREDICTION_METRIC
    audit_p = os.path.join(out, "audit.json")
    cov = read_json(audit_p)["window_coverage"] if os.path.exists(audit_p) else {}

    L = ["# Window-length sensitivity", HEADER_CAVEAT, "",
         "Every window predicts the SAME targets: short prefixes are padded, "
         "never discarded, so the comparison is paired. Equal update budgets "
         "equalise optimisation effort, not runtime.", "",
         "| arm | window | test full-history % | micro-F1 | BCE |",
         "|---|---:|---:|---|---|"]
    for (arm, w, samp), per in sorted(idx.items()):
        seeds = sorted(per)
        fh = cov.get(str(w), {}).get("test", {}).get("full_history_pct")
        L.append(f"| {arm} | {w} | {_fmt(fh, 1)} | "
                 f"{_ms([_metric(per[s], M) for s in seeds])} | "
                 f"{_ms([_metric(per[s], 'bce') for s in seeds], 5)} |")

    L += ["", f"## Paired contrasts vs the reference window "
              f"({SPEC.REFERENCE_WINDOW})", "",
          "| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |",
          "|---|---:|---:|---|---:|---:|---|"]
    fam = []
    for arm in SPEC.PREDICTION_ARMS:
        ref = idx.get((arm, SPEC.REFERENCE_WINDOW, "ordinary"))
        if not ref:
            continue
        for w in SPEC.WINDOWS:
            if w == SPEC.REFERENCE_WINDOW:
                continue
            cur = idx.get((arm, w, "ordinary"))
            if not cur:
                continue
            seeds = sorted(set(ref) & set(cur))
            if len(seeds) < 2:
                continue
            fam.append(St.paired_test([_metric(cur[s], M) for s in seeds],
                                      [_metric(ref[s], M) for s in seeds],
                                      f"{arm}: W{w} - W{SPEC.REFERENCE_WINDOW}"))
    for r in St.holm(fam, SPEC.ALPHA):
        L.append(f"| {r['contrast']} | {r['pairs']} | {r['delta']:+.5f} | "
                 f"[{r['ci_low']:+.5f}, {r['ci_high']:+.5f}] | "
                 f"{r['p_raw']:.5f} | {r['p_holm']:.5f} | {St.verdict(r)} |")
    L += ["", f"_{SPEC.EQUIVALENCE_NOTE}_", ""]
    return "\n".join(L)


def report_curves(out: str) -> str:
    cells = _load_cells(out, "prediction")
    if not cells:
        return ""
    L = ["# Training curves", HEADER_CAVEAT, "",
         "Every recorded validation point, for every main cell.", ""]
    for c in sorted(cells, key=lambda c: (c["arm"], c["window"], c["sampler"], c["seed"])):
        L += [f"## {c['arm']} W{c['window']} {c['sampler']} seed {c['seed']}", "",
              f"best update {c['best_update']}, best validation BCE "
              f"{c['best_validation_bce']:.6f}, "
              f"{len(c['improvements'])} strict improvements, "
              f"{len(c['patience_resets'])} patience resets", "",
              "| update | epoch-equivalents | train BCE | validation BCE |",
              "|---:|---:|---:|---:|"]
        for p in c["curve"]:
            L.append(f"| {p['update']} | {p['epoch_equivalents']:.2f} | "
                     f"{p['train_bce_running']:.6f} | {p['validation_bce']:.6f} |")
        L.append("")
    return "\n".join(L)


def report_examples(out: str, n: int = 12) -> str:
    cells = _load_cells(out, "prediction")
    if not cells:
        return ""
    L = ["# Prediction examples", HEADER_CAVEAT, "",
         "Per-run test scores at the validation-selected threshold. "
         "Runs are listed in full, not cherry-picked.", ""]
    for c in sorted(cells, key=lambda c: (c["arm"], c["window"], c["seed"]))[:n]:
        L += [f"## {c['arm']} W{c['window']} {c['sampler']} seed {c['seed']} "
              f"(threshold {c['primary']['threshold']})", "",
              "| test run | windows | micro-F1 | exact-set | p@1 | BCE |",
              "|---|---:|---:|---:|---:|---:|"]
        for run, v in sorted(c["primary"]["test"]["per_run"].items()):
            L.append(f"| `{run}` | {v['n']} | {v['micro_f1']:.4f} | "
                     f"{v['exact_set_accuracy']:.4f} | "
                     f"{v['precision_at_1']:.4f} | {v['bce']:.5f} |")
        L.append("")
    return "\n".join(L)


# ── deception ───────────────────────────────────────────────────────────────

def _rl_index(cells: List[dict]):
    idx = defaultdict(dict)
    for c in cells:
        idx[(c["arm"], c["learner"], c["window"])][c["seed"]] = c
    return idx


def report_rl(out: str) -> str:
    cells = _load_cells(out, "rl") + _load_cells(out, "context")
    lad_p = os.path.join(out, "ladder.json")
    if not cells and not os.path.exists(lad_p):
        return ""
    L = ["# Deception results", HEADER_CAVEAT, "",
         "**Dwell counts COMMANDS engaged, not technique labels.** One command "
         "is one step and earns at most one unit of reward, however many "
         "labels it carries. The earlier study's dwell counted label-steps and "
         "is a different quantity.", ""]

    if os.path.exists(lad_p):
        lad = read_json(lad_p)
        L += ["## Reference ladder", "",
              f"_{SPEC.BASELINE_NOTE}_", "",
              f"Tuned on validation: best fixed joint action "
              f"`{lad['selected_on_validation']['best_fixed_joint']}`, "
              f"static action `{lad['selected_on_validation']['static_action']}`.",
              "", "| rung | dwell | depth | protection % | lure chains | exposed |",
              "|---|---:|---:|---:|---:|---:|"]
        for name in SPEC.BASELINES:
            v = lad["test"].get(name)
            if v:
                L.append(f"| {name} | {v['dwell']:.3f} | {v['depth']:.3f} | "
                         f"{100*v['protected']:.1f} | {v['lure_chains']:.2f} | "
                         f"{v['exposed']:.3f} |")
        h = lad["headroom_test"]["dwell"]
        L += ["", f"- floor (best fixed): **{h['floor_best_fixed']:.3f}**, "
                  f"ceiling (coordinated clairvoyant): **{h['ceiling']:.3f}**, "
                  f"headroom **{h['headroom']:.3f}**",
              f"- value of coordination (coordinated - uncoordinated "
              f"clairvoyant): **{h['coordination_value']:+.3f}** dwell", ""]

    if cells:
        idx = _rl_index(cells)
        lad = read_json(lad_p) if os.path.exists(lad_p) else None
        L += ["## Policies", "",
              "| arm | learner | window | seeds | dwell | depth | protection % | "
              "dwell at h=0 | headroom captured |",
              "|---|---|---:|---:|---|---|---|---|---|"]
        for (arm, learner, w), per in sorted(idx.items()):
            seeds = sorted(per)
            dw = [per[s]["test_summary"]["dwell"] for s in seeds]
            dp = [per[s]["test_summary"]["depth"] for s in seeds]
            pr = [100 * per[s]["test_summary"]["protected"] for s in seeds]
            h0 = [per[s]["test_h0_summary"]["dwell"] for s in seeds]
            cap = "-"
            if lad:
                import baselines_cmd as B
                cap = f"{100 * B.capture(float(np.mean(dw)), lad['test']):.1f}%"
            L.append(f"| {arm} | {learner} | {w} | {len(seeds)} | {_ms(dw, 3)} | "
                     f"{_ms(dp, 3)} | {_ms(pr, 1)} | {_ms(h0, 3)} | {cap} |")

        L += ["", "`dwell at h=0` zeroes the history embedding at test time. A "
                  "large drop means the policy genuinely uses the history "
                  "channel; no drop means it learned to ignore it.", "",
              "## Guards", "",
              "| arm | learner | window | exposed | lure chains | dead ends | "
              "capacity violations | episode length |",
              "|---|---|---:|---|---|---|---|---|"]
        for (arm, learner, w), per in sorted(idx.items()):
            seeds = sorted(per)
            g = lambda k: [per[s]["test_summary"][k] for s in seeds]
            L.append(f"| {arm} | {learner} | {w} | {_ms(g('exposed'), 3)} | "
                     f"{_ms(g('lure_chains'), 2)} | {_ms(g('dead_ends'), 2)} | "
                     f"{_ms(g('capacity_violations'), 2)} | {_ms(g('length'), 1)} |")

    ctx_p = os.path.join(out, "context_window.json")
    if os.path.exists(ctx_p):
        ctx = read_json(ctx_p)
        L += ["", "## Context window", "",
              f"- selected window: **{ctx['window']}**",
              f"- rule: {ctx['rule']}", ""]
    return "\n".join(L)


# ── statistics ──────────────────────────────────────────────────────────────

def report_statistics(out: str) -> str:
    L = ["# Statistics", HEADER_CAVEAT, "",
         f"- test: {SPEC.TEST}", f"- correction: {SPEC.CORRECTION}, "
         f"alpha = {SPEC.ALPHA}", "",
         f"_{SPEC.EQUIVALENCE_NOTE}_", "", f"_{SPEC.INDEPENDENCE_NOTE}_", ""]

    pred = [c for c in _load_cells(out, "prediction") if c["sampler"] == "ordinary"]
    over = [c for c in _load_cells(out, "prediction") if c["sampler"] == "overlap"]
    M = SPEC.PRIMARY_PREDICTION_METRIC
    if pred:
        idx = _pred_index(pred)
        oidx = _pred_index(over)
        fam = []
        W = SPEC.REFERENCE_WINDOW
        arms = [a for a in SPEC.PREDICTION_ARMS if (a, W, "ordinary") in idx]
        for i, a in enumerate(arms):
            for b in arms[i + 1:]:
                pa, pb = idx[(a, W, "ordinary")], idx[(b, W, "ordinary")]
                seeds = sorted(set(pa) & set(pb))
                if len(seeds) >= 2:
                    fam.append(St.paired_test([_metric(pa[s], M) for s in seeds],
                                              [_metric(pb[s], M) for s in seeds],
                                              f"prediction W{W}: {a} - {b}"))
        nh = idx.get((SPEC.NO_HISTORY, W, "ordinary"))
        if nh:
            for a in arms:
                pa = idx[(a, W, "ordinary")]
                seeds = sorted(set(pa) & set(nh))
                if len(seeds) >= 2:
                    fam.append(St.paired_test([_metric(pa[s], M) for s in seeds],
                                              [_metric(nh[s], M) for s in seeds],
                                              f"prediction W{W}: {a} - NoHistory"))
        for a in SPEC.ENCODERS:
            oa, pa = oidx.get((a, W, "overlap")), idx.get((a, W, "ordinary"))
            if oa and pa:
                seeds = sorted(set(oa) & set(pa))
                if len(seeds) >= 2:
                    fam.append(St.paired_test([_metric(oa[s], M) for s in seeds],
                                              [_metric(pa[s], M) for s in seeds],
                                              f"prediction W{W}: {a} overlap - ordinary"))
        if fam:
            L += [f"## Prediction family ({M})", "",
                  f"_{SPEC.PREDICTION_FAMILY}_", "",
                  "| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |",
                  "|---|---:|---:|---|---:|---:|---|"]
            for r in St.holm(fam, SPEC.ALPHA):
                L.append(f"| {r['contrast']} | {r['pairs']} | {r['delta']:+.5f} | "
                         f"[{r['ci_low']:+.5f}, {r['ci_high']:+.5f}] | "
                         f"{r['p_raw']:.5f} | {r['p_holm']:.5f} | {St.verdict(r)} |")

    rl = _load_cells(out, "rl") + _load_cells(out, "context")
    if rl:
        idx = _rl_index(rl)
        fam = []
        for metric in ("dwell",) + SPEC.RL_SECONDARY_METRICS:
            keys = sorted(idx)
            for i, ka in enumerate(keys):
                for kb in keys[i + 1:]:
                    if ka[2] != kb[2]:
                        continue                      # same window only
                    same_arm = ka[0] == kb[0]
                    same_learn = ka[1] == kb[1]
                    if not (same_arm or same_learn):
                        continue                      # one factor at a time
                    pa, pb = idx[ka], idx[kb]
                    seeds = sorted(set(pa) & set(pb))
                    if len(seeds) < 2:
                        continue
                    label = (f"{metric} W{ka[2]}: {ka[0]}+{ka[1]} - "
                             f"{kb[0]}+{kb[1]}")
                    fam.append(St.paired_test(
                        [pa[s]["test_summary"][metric] for s in seeds],
                        [pb[s]["test_summary"][metric] for s in seeds], label))
        if fam:
            L += ["", "## Deception family", "", f"_{SPEC.RL_FAMILY}_", "",
                  "| contrast | pairs | delta | 95% CI | p raw | p Holm | verdict |",
                  "|---|---:|---:|---|---:|---:|---|"]
            for r in St.holm(fam, SPEC.ALPHA):
                L.append(f"| {r['contrast']} | {r['pairs']} | {r['delta']:+.4f} | "
                         f"[{r['ci_low']:+.4f}, {r['ci_high']:+.4f}] | "
                         f"{r['p_raw']:.5f} | {r['p_holm']:.5f} | {St.verdict(r)} |")
    return "\n".join(L)


# ── headline ────────────────────────────────────────────────────────────────

def report_main(out: str) -> str:
    man_p = os.path.join(out, "manifest.json")
    man = read_json(man_p) if os.path.exists(man_p) else {}
    pred = _load_cells(out, "prediction")
    rl = _load_cells(out, "rl")
    ctx = _load_cells(out, "context")

    L = ["# Temarl_Test_v1_L1 -- results", HEADER_CAVEAT, "",
         "## Completion", "",
         f"- prediction cells: **{len(pred)}**",
         f"- deception cells (reference window): **{len(rl)}**",
         f"- deception cells (context window): **{len(ctx)}**",
         f"- smoke run: **{man.get('smoke')}**"
         + ("  <- NOT a scientific result" if man.get("smoke") else ""), ""]
    if man.get("env_config"):
        L += [f"- environment: `{man['env_config']}`", ""]

    L += ["## Declared hypotheses", "",
          "Frozen in `study_spec.py` before any confirmatory run.", ""]
    for k, v in SPEC.HYPOTHESES.items():
        L.append(f"- **{k}**: {v}")
    L += ["", f"_{SPEC.NEGATIVE_RESULTS_NOTE}_", "",
          "## Reports", "",
          "- [Data audit](DATA_AUDIT.md)",
          "- [Patience and budget](PATIENCE_RESULTS.md)",
          "- [Prediction](PREDICTION_RESULTS.md)",
          "- [Window sensitivity](WINDOW_RESULTS.md)",
          "- [Deception](RL_RESULTS.md)",
          "- [Statistics](STATISTICS.md)",
          "- [Training curves](TRAINING_CURVES.md)",
          "- [Prediction examples](PREDICTION_EXAMPLES.md)", ""]
    return "\n".join(L)


def build(out: str) -> None:
    pages = {
        "RESULTS.md": report_main,
        "DATA_AUDIT.md": report_audit,
        "PATIENCE_RESULTS.md": report_patience,
        "PREDICTION_RESULTS.md": report_prediction,
        "WINDOW_RESULTS.md": report_windows,
        "RL_RESULTS.md": report_rl,
        "STATISTICS.md": report_statistics,
        "TRAINING_CURVES.md": report_curves,
        "PREDICTION_EXAMPLES.md": report_examples,
    }
    for name, fn in pages.items():
        text = fn(out)
        if text:
            _w(os.path.join(out, name), text + "\n")
            print(f"    wrote {name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=os.path.join(HERE, "results", "run"))
    args = ap.parse_args()
    build(os.path.abspath(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
