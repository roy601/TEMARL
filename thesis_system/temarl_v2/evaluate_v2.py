# -*- coding: utf-8 -*-
"""
TEMARL v2 — Pre-Registered Evaluation
=====================================
Closes F-EVL-01..08, F-ENV-01, F-ARC-07.

=============================================================================
                        P R E - R E G I S T R A T I O N
        (fixed BEFORE any result is observed; do not edit after running)
=============================================================================
v1 chose its primary metric in Sec. 5.1 AFTER observing which of four candidates
favoured the method, using an uncited "discrimination threshold of 0.3". That is
outcome-selective metric choice (HARKing). The metric roles below are therefore
fixed here, in source, ahead of execution:

  PRIMARY   (outcome)   Deception Success Rate (DSR)
                        -- the real defensive outcome. Usable ONLY because the
                        v2 environment de-saturated it: measured spread
                        oracle-random = +0.218 (v1: 0.013, all policies 0.90-0.97).
  MECHANISM (process)   Alignment Score
                        -- explains HOW a DSR difference arises. Reported for
                        every method; never substituted for the primary.
  Both are reported for every method in every table. No metric is dropped.

PRE-REGISTERED HYPOTHESES (family of 5, Holm-Bonferroni corrected, alpha=0.05):
  H1  Model A  >  Step-Counter Oracle    (intent beats timing)
  H2  Model A  >  Best-Fixed Action      (intent beats no information)
  H3  Model A  >  NoTrans (h = 0)        (the intent vector is load-bearing)
  H4  Model A  >  Model C (SetEncoder)   ("why Transformer": order matters)
  H5  Model A  >  Model B (GRU)          ("why Transformer": attention > recurrence)

DECISION RULE, fixed in advance:
  * H1 and H2 failing  => intent modelling does not pay in this environment.
  * H3 failing         => h is not load-bearing; the thesis premise is refuted.
  * H4 failing         => order is NOT the mechanism. The contribution must be
                          reframed from "sequence modelling" to "intent
                          representation". This is a REPORTABLE result, not a
                          failure to be hidden.
  Effect sizes (Cohen's d) are reported for every comparison. An uncorrected
  p < 0.05 that does not survive Holm is reported as NOT significant.

BASELINE CORRECTION (F-ENV-01) -- the defect that inflated v1's headline:
  v1's "static baseline" was documented as fake_vulnerability but its reported
  value (0.136) matches the column mean of minimal_response (0.135), not
  fake_vulnerability (0.530). The "600% improvement" was therefore measured
  against the NULL ACTION. Here BOTH references are always reported:
      Static-Null  (floor)      and  Best-Fixed  (the correct comparator).
  Percent-improvement claims are computed against Best-Fixed only.
=============================================================================
"""

import itertools
import json
import os
from collections import Counter, defaultdict

import numpy as np
import torch
from scipy import stats as st

from d3fend_payoff import ACTIONS, N_ACTIONS, PAYOFF
from encoders import build_matched_suite
from env_v2 import (DeceptionEnvV2, N_AGENTS, build_profiles_from_camlds)
from policy import MultiAgentController
from vocab_v2 import NUM_TECHNIQUES

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_v2")
os.makedirs(OUT, exist_ok=True)

SEEDS = list(range(10))          # F-EVL-07
EPISODES = 200                   # F-EVL-07
ALPHA = 0.05

PRIMARY_METRIC = "dsr"
MECHANISM_METRIC = "alignment"
HYPOTHESES = [("H1", "Step-Counter Oracle"), ("H2", "Best-Fixed"),
              ("H3", "NoTrans (h=0)"), ("H4", "Model C SetEncoder"),
              ("H5", "Model B GRU")]


# ── policy factories ─────────────────────────────────────────────────────────

def make_static(action):
    return lambda obs, h, env: [action] * N_AGENTS


def make_random(rng):
    return lambda obs, h, env: [int(rng.integers(N_ACTIONS)) for _ in range(N_AGENTS)]


def fit_counter_oracle(profiles, n_eps=400, seed=0, max_steps=40):
    """F-EVL-04 — THE NULL MODEL v1 OMITTED.
    A defender with a PERFECT CLOCK and NO intent model: it knows p(tau | step)
    and plays the Bayes action for the step index. In v1 this baseline BEAT the
    Transformer (0.692 vs 0.557), which is why omitting it was fatal."""
    env = DeceptionEnvV2(profiles, max_steps=max_steps, seed=seed)
    cnt = defaultdict(lambda: np.zeros(NUM_TECHNIQUES))
    for _ in range(n_eps):
        env.reset(); done = False; t = 0
        while not done:
            _, _, done, info = env.step([0] * N_AGENTS)
            if info["technique_id"] < NUM_TECHNIQUES:
                cnt[min(t, max_steps - 1)][info["technique_id"]] += 1
            t += 1
    A = PAYOFF[:NUM_TECHNIQUES]
    table = {k: int(((v / max(v.sum(), 1)) @ A).argmax()) for k, v in cnt.items()}
    tot = sum(cnt.values())
    default = int(((tot / max(tot.sum(), 1)) @ A).argmax())
    return lambda obs, h, env: [table.get(min(env.step_count, max_steps - 1),
                                          default)] * N_AGENTS


def make_profile_oracle(profiles):
    """Ceiling: perfect knowledge of the hidden intent class."""
    idx = {c: ACTIONS.index(c) for c in profiles}
    return lambda obs, h, env: [idx[env._profile]] * N_AGENTS


def make_policy(ctl):
    return lambda obs, h, env: ctl.act_policy(obs, greedy=True)


# ── episode runner ───────────────────────────────────────────────────────────

def run_seed(policy_fn, profiles, encoder=None, use_h=True, seed=0,
             n_eps=EPISODES, fog=0.0, max_steps=40, collect_tuples=False):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    env = DeceptionEnvV2(profiles, max_steps=max_steps, seed=seed)
    zeros = np.zeros(env.h_dim, np.float32)
    al, dsr, dwell, tuples = [], [], [], Counter()
    for _ in range(n_eps):
        obs = env.reset(); done = False; ep = []
        while not done:
            if use_h and encoder is not None:
                ids, ln = env.padded_sequence()
                h = encoder.get_h_numpy(ids, DEVICE, lengths=[ln])
            else:
                h = zeros
            full = [o.copy() for o in obs]
            for o in full:
                o[-env.h_dim:] = h
            if fog > 0:                      # telemetry obstruction; h untouched
                for o in full:
                    m = rng.random(env.local_dim) < fog
                    o[:env.local_dim][m] = 0.0
            a = policy_fn(full, h, env)
            if collect_tuples:
                tuples[tuple(a)] += 1
            obs, _, done, info = env.step(a, h)
            if info["responsible_agent"] is not None:
                ep.append(info["alignment"])
        if ep:
            al.append(float(np.mean(ep)))
        dsr.append(1.0 if env.captured else 0.0)
        dwell.append(env.step_count)
    out = {"alignment": float(np.mean(al)) if al else 0.0,
           "dsr": float(np.mean(dsr)), "dwell": float(np.mean(dwell))}
    if collect_tuples:
        out["n_distinct_tuples"] = len(tuples)
        out["top_tuple_share"] = (tuples.most_common(1)[0][1] / sum(tuples.values())
                                  if tuples else 0.0)
    return out


def evaluate_method(name, policy_fn, profiles, encoder=None, use_h=True,
                    seeds=SEEDS, n_eps=EPISODES, fog=0.0, collect_tuples=False):
    rows = [run_seed(policy_fn, profiles, encoder, use_h, s, n_eps, fog,
                     collect_tuples=collect_tuples) for s in seeds]
    agg = {"method": name, "n_seeds": len(seeds), "n_eps": n_eps, "fog": fog}
    for k in ("alignment", "dsr", "dwell"):
        v = np.array([r[k] for r in rows])
        ci = st.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
        agg[k] = {"mean": float(v.mean()), "std": float(v.std(ddof=1)),
                  "ci95": float(ci), "per_seed": v.tolist()}
    if collect_tuples:
        agg["n_distinct_tuples"] = float(np.mean([r["n_distinct_tuples"] for r in rows]))
        agg["top_tuple_share"] = float(np.mean([r["top_tuple_share"] for r in rows]))
    return agg


# ── statistics (F-EVL-03/06/07) ──────────────────────────────────────────────

def cohens_d(a, b):
    """Paired Cohen's d = mean(diff) / sd(diff)."""
    d = np.asarray(a) - np.asarray(b)
    return float(d.mean() / (d.std(ddof=1) + 1e-12))


def compare(a_vals, b_vals):
    t, p = st.ttest_rel(a_vals, b_vals)
    d = cohens_d(a_vals, b_vals)
    diff = float(np.mean(a_vals) - np.mean(b_vals))
    mag = ("negligible" if abs(d) < 0.2 else "small" if abs(d) < 0.5 else
           "medium" if abs(d) < 0.8 else "large")
    return {"diff": diff, "t": float(t), "p": float(p), "d": d, "magnitude": mag}


def holm_bonferroni(pvals, alpha=ALPHA):
    """Step-down Holm correction. v1 reported one-of-four significant with NO
    correction; here the whole pre-registered family is corrected together."""
    idx = np.argsort(pvals)
    m = len(pvals)
    out = [None] * m
    prev = 0.0
    for rank, i in enumerate(idx):
        thr = alpha / (m - rank)
        adj = max(prev, min(1.0, pvals[i] * (m - rank)))
        prev = adj
        out[i] = {"p_raw": float(pvals[i]), "threshold": float(thr),
                  "p_holm": float(adj), "significant": bool(adj < alpha)}
    return out


def headroom_pct(v, fixed, oracle):
    return 100.0 * (v - fixed) / max(oracle - fixed, 1e-9)


# ── main evaluation ──────────────────────────────────────────────────────────

def build_all(profiles, seeds=SEEDS, n_eps=EPISODES, ckpt_dir=None, verbose=True):
    rng = np.random.default_rng(0)
    suite, _, _ = build_matched_suite()
    env0 = DeceptionEnvV2(profiles)

    methods = {}
    methods["Static-Null (floor)"] = (make_static(0), None, False)
    best_fixed = int(np.argmax([PAYOFF[:NUM_TECHNIQUES, a].mean()
                                for a in range(N_ACTIONS)]))
    methods[f"Best-Fixed ({ACTIONS[best_fixed]})"] = (make_static(best_fixed), None, False)
    methods["Random Policy"] = (make_random(rng), None, False)
    methods["Step-Counter Oracle"] = (fit_counter_oracle(profiles), None, False)

    # learned arms, loaded from checkpoints when available
    ckpt_dir = ckpt_dir or os.path.join(HERE, "runs")
    for enc_name in ("Transformer", "GRU", "SetEncoder"):
        for use_h, tag in ((True, ""), (False, "_NoTrans")):
            if enc_name != "Transformer" and not use_h:
                continue                      # NoTrans arm needs only one encoder
            p = os.path.join(ckpt_dir, f"{enc_name}{tag}_s0.pt")
            if not os.path.exists(p):
                continue
            ck = torch.load(p, map_location=DEVICE, weights_only=False)
            enc = suite[enc_name].to(DEVICE)
            enc.load_state_dict(ck["encoder"]); enc.freeze()
            ctl = MultiAgentController(N_AGENTS, env0.local_dim, N_ACTIONS,
                                       env0.h_dim,
                                       sighted_idx=env0.ATTACKER_PRESENT_IDX,
                                       device=DEVICE)
            for a, sd in zip(ctl.agents, ck["agents"]):
                a.load_state_dict(sd)
            ctl.eval(); ctl.set_masking(0.0)
            label = {"Transformer": "Model A Transformer",
                     "GRU": "Model B GRU",
                     "SetEncoder": "Model C SetEncoder"}[enc_name]
            if not use_h:
                label = "NoTrans (h=0)"
            methods[label] = (make_policy(ctl), enc, use_h)

    methods["Profile Oracle (ceiling)"] = (make_profile_oracle(profiles), None, False)

    results = {}
    for name, (fn, enc, use_h) in methods.items():
        if verbose:
            print(f"    evaluating {name} ...")
        results[name] = evaluate_method(name, fn, profiles, enc, use_h,
                                        seeds, n_eps, collect_tuples=True)
    return results, best_fixed


def report(results, best_fixed, profiles, alpha=ALPHA):
    fixed_key = f"Best-Fixed ({ACTIONS[best_fixed]})"
    fixed = results[fixed_key][PRIMARY_METRIC]["mean"]
    oracle = results["Profile Oracle (ceiling)"][PRIMARY_METRIC]["mean"]
    fixed_a = results[fixed_key][MECHANISM_METRIC]["mean"]
    oracle_a = results["Profile Oracle (ceiling)"][MECHANISM_METRIC]["mean"]

    print("\n" + "=" * 96)
    print(f"  RESULTS  ({results[fixed_key]['n_seeds']} seeds x "
          f"{results[fixed_key]['n_eps']} episodes)")
    print(f"  PRIMARY = {PRIMARY_METRIC.upper()} (outcome)   "
          f"MECHANISM = {MECHANISM_METRIC} (process)   [pre-registered]")
    print("=" * 96)
    print(f"  {'method':<28} {'DSR (95% CI)':>20} {'%HR':>7} "
          f"{'Align (95% CI)':>20} {'%HR':>7}")
    print("  " + "-" * 92)
    order = sorted(results, key=lambda k: -results[k][PRIMARY_METRIC]["mean"])
    for k in order:
        r = results[k]
        d, a = r[PRIMARY_METRIC], r[MECHANISM_METRIC]
        print(f"  {k:<28} {d['mean']:>11.4f}+-{d['ci95']:<7.4f} "
              f"{headroom_pct(d['mean'], fixed, oracle):>6.1f}% "
              f"{a['mean']:>11.4f}+-{a['ci95']:<7.4f} "
              f"{headroom_pct(a['mean'], fixed_a, oracle_a):>6.1f}%")

    # ---- pre-registered hypothesis family ---------------------------------
    A = "Model A Transformer"
    if A not in results:
        print("\n  [!] Model A checkpoint missing; hypothesis tests skipped.")
        return None
    # EXPLICIT mapping. An earlier fuzzy matcher used
    #   `or k.startswith(target.split()[0])`
    # which made "Model C SetEncoder" match "Model A Transformer" first (both
    # begin with "Model"), hit the `tgt == A` guard, and be dropped SILENTLY --
    # so H4 and H5, the two DECISIVE hypotheses, were never tested and their
    # absence was not reported. Fuzzy matching is banned here: every hypothesis
    # must resolve to an exact key, and any missing arm is reported loudly.
    KEYMAP = {"Step-Counter Oracle": "Step-Counter Oracle",
              "Best-Fixed": fixed_key,
              "NoTrans (h=0)": "NoTrans (h=0)",
              "Model C SetEncoder": "Model C SetEncoder",
              "Model B GRU": "Model B GRU"}
    fam, pv, missing = [], [], []
    for hid, target in HYPOTHESES:
        tgt = KEYMAP.get(target)
        if tgt is None:
            raise KeyError(f"{hid}: no explicit key mapping for '{target}'")
        if tgt not in results:
            missing.append((hid, tgt))
            continue
        c = compare(results[A][PRIMARY_METRIC]["per_seed"],
                    results[tgt][PRIMARY_METRIC]["per_seed"])
        fam.append((hid, tgt, c)); pv.append(c["p"])
    holm = holm_bonferroni(pv, alpha)
    if missing:
        print("\n  [!] HYPOTHESES NOT TESTED (arm missing) — reported, not hidden:")
        for hid, tgt in missing:
            print(f"      {hid}: '{tgt}' absent from results")

    print(f"\n  PRE-REGISTERED HYPOTHESIS FAMILY  (primary metric = "
          f"{PRIMARY_METRIC.upper()}, Holm-Bonferroni, alpha={alpha})")
    print(f"  {'':<4} {'Model A vs':<28} {'diff':>8} {'d':>7} {'p_raw':>9} "
          f"{'p_holm':>9}  verdict")
    print("  " + "-" * 92)
    for (hid, tgt, c), h in zip(fam, holm):
        verdict = ("SUPPORTED" if h["significant"] and c["diff"] > 0 else
                   "REFUTED (A worse)" if h["significant"] and c["diff"] < 0 else
                   "not significant")
        print(f"  {hid:<4} {tgt:<28} {c['diff']:>+8.4f} {c['d']:>+7.2f} "
              f"{c['p']:>9.4f} {h['p_holm']:>9.4f}  {verdict} ({c['magnitude']})")

    print(f"\n  [F-EVL-08] ACTION-TUPLE DIVERSITY (with the h=0 control v1 lacked)")
    print(f"    {'method':<28} {'distinct tuples':>16} {'top-tuple share':>17}")
    for k in (A, "NoTrans (h=0)", fixed_key):
        if k in results:
            r = results[k]
            print(f"    {k:<28} {r.get('n_distinct_tuples', float('nan')):>16.1f} "
                  f"{r.get('top_tuple_share', float('nan')):>16.1%}")
    print(f"    (v1 reported 4 tuples of 5^4=625 as proof h drives coordination,")
    print(f"     with NO h=0 control and an unreconciled second figure of 23.)")
    return {"family": [(h, t, c) for (h, t, c) in fam], "holm": holm}


if __name__ == "__main__":
    import sys
    import argparse
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=len(SEEDS))
    ap.add_argument("--episodes", type=int, default=EPISODES)
    args = ap.parse_args()
    seeds = list(range(args.seeds))

    print("=" * 96)
    print("  TEMARL v2 — PRE-REGISTERED EVALUATION")
    print("=" * 96)
    print(f"  device={DEVICE}  seeds={len(seeds)}  episodes/seed={args.episodes}")
    print(f"  PRE-REGISTERED: primary={PRIMARY_METRIC.upper()}, "
          f"mechanism={MECHANISM_METRIC}, family of {len(HYPOTHESES)}, Holm alpha={ALPHA}")

    profiles, _ = build_profiles_from_camlds()
    res, bf = build_all(profiles, seeds, args.episodes)
    stats = report(res, bf, profiles)

    with open(os.path.join(OUT, "evaluation_v2.json"), "w") as f:
        json.dump({"preregistration": {
            "primary": PRIMARY_METRIC, "mechanism": MECHANISM_METRIC,
            "hypotheses": HYPOTHESES, "alpha": ALPHA,
            "seeds": seeds, "episodes": args.episodes},
            "results": res}, f, indent=1)
    print(f"\n  saved -> results_v2/evaluation_v2.json")
    print("=" * 96)
