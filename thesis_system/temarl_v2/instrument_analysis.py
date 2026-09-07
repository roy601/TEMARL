# -*- coding: utf-8 -*-
"""
TEMARL — INSTRUMENT ANALYSIS  (EXPLORATORY)
============================================
STATUS: exploratory. Not part of `prereg_v4.py` (commit 7499d29). Changes no
declared contrast. The Phase 4 null stands exactly as reported.

WHAT THIS MEASURES
------------------
Before comparing architectures, one must know whether the task can tell them
apart. The quantity that decides it:

    seq_value = E[payoff | perfect next-technique model]
              - E[payoff | perfect campaign-class label]

If seq_value is ~0, the optimal action is a function of the class label alone,
every history architecture converges to the same policy, and an architecture
comparison on that task is uninformative NO MATTER how well each arm is trained.

The shipped environment measures **+0.0001** (and +0.0005 DSR on the reference
ladder, `baselines_entity.py`). It cannot discriminate history architectures.

WHY: `build_profiles_from_camlds()` in env_v2.py estimates each campaign's
Markov chain as

    T = 0.02 (flat floor, x84 states)      ->  1.68 mass/row, no information
      + 1.2 per goal technique, EVERY ROW  ->  7.2-8.4 mass/row, no information
      + 4.0 per observed bigram            ->  the only term carrying sequence
                                               information

The row-independent goal drift contributes ~2x the mass of the real bigrams and
is identical in every row, so it dilutes sequential structure while concentrating
each campaign's stationary distribution onto its goal tactic -- whose techniques
share one optimal decoy. That is what makes the class label sufficient.

Measured against the source data: the raw CAM-LDS sequences carry
I(tau_next; tau) = 4.83 bits (85.4% predictable, sequences 4-23 techniques).
The environment's chains retain 0.627 bits within-campaign, and the decision
structure makes even that worth +0.0001. **The data has the structure; the
environment construction discards it.**

THE FACTORIAL BELOW
-------------------
2 (class granularity) x 2 (estimator) x 2 (goal drift), on the same sequences.
Its "SHIPPED" cell is an APPROXIMATION of the shipped design, not the shipped
design itself: goal ids here come from each class's most common terminal tactic,
whereas env_v2 uses `PRIMARY[cls] & present`. The shipped design's true value is
+0.0001, measured directly. The factorial is for ranking design levers, not for
reproducing the shipped number.

Result: goal drift is the dominant lever (+0.0717 main effect). Backoff
estimation and finer class granularity both REDUCE seq_value, because each makes
the class label itself more informative -- the opposite of what I expected before
running it.

USE: any successor environment must clear a seq_value threshold declared in
advance, BEFORE any architecture is trained on it. Removing the drift is
justified as an estimator correction (a row-independent additive constant is not
a transition model), never as "so the Transformer wins."
"""
import os, sys, json
sys.path.insert(0, r"c:\Users\User\thesis_project_pev_V2\thesis_project_pev"
                   r"\thesis_project\thesis_system\temarl_v2")
os.chdir(sys.path[0])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from collections import Counter
from env_v2 import NUM_TECHNIQUES, technique_to_id, tactic_of
from d3fend_payoff import PAYOFF, consolidate_intent_classes

NT = NUM_TECHNIQUES
g = json.load(open(os.path.join("..", "data", "camlds_grounding.json"),
                   encoding="utf-8"))
seqs, dists, term = {}, {}, {}
for s in g["scenarios"]:
    ids = [technique_to_id(x) for x in s["technique_sequence"]
           if not x.startswith("<")]
    ids = [i for i in ids if i < NT]
    if len(ids) < 2:
        continue
    seqs[s["id"]] = ids
    term[s["id"]] = s["terminal_tactic"].split("(")[0].split("/")[0].strip()
    d = np.zeros(NT)
    for i in ids:
        d[i] += 1.0
    gi = [j for j in range(NT) if tactic_of(j) == term[s["id"]]]
    for j in gi:
        d[j] += 0.6 * d.sum() / len(gi)
    dists[s["id"]] = d
con = consolidate_intent_classes(dists)

CLASSES = {"3 consolidated": con["members"], "7 scenarios": {s: [s] for s in seqs}}


def goal_ids_for(members):
    tac = Counter(term[m] for m in members).most_common(1)[0][0]
    return [j for j in range(NT) if tactic_of(j) == tac]


def estimate(members, gids, backoff, drift, disc=0.75):
    if not backoff:
        T = np.full((NT, NT), 0.02)
        for m in members:
            for a, b in zip(seqs[m], seqs[m][1:]):
                T[a, b] += 4.0
    else:
        big, uni = Counter(), Counter()
        for m in members:
            for a, b in zip(seqs[m], seqs[m][1:]):
                big[(a, b)] += 1.0
            for t in seqs[m]:
                uni[t] += 1.0
        u = np.full(NT, 1e-3)
        for t, n in uni.items():
            u[t] += n
        u /= u.sum()
        T = np.zeros((NT, NT))
        for a in range(NT):
            succ = {b: n for (aa, b), n in big.items() if aa == a}
            tot = sum(succ.values())
            if tot == 0:
                T[a] = u
                continue
            for b, n in succ.items():
                T[a, b] = max(n - disc, 0.0) / tot
            T[a] += (disc * len(succ) / tot) * u
    if drift:
        for j in gids:
            T[:, j] += 1.2
    return T / T.sum(1, keepdims=True)


def measure(profiles, n_steps=60000, seed=0):
    rng = np.random.default_rng(seed)
    occ, pairs = {}, {}
    for c, p in profiles.items():
        s, tau = [], int(rng.choice(NT, p=p["init"]))
        for i in range(n_steps):
            nxt = int(rng.choice(NT, p=p["T"][tau]))
            s.append((tau, nxt)); tau = nxt
            if (i + 1) % 40 == 0:
                tau = int(rng.choice(NT, p=p["init"]))
        pairs[c] = np.array(s)
        occ[c] = np.bincount(pairs[c][:, 1], minlength=NT) / len(s)
    marg = np.mean([occ[c] @ PAYOFF for c in profiles], axis=0)
    bf = float(marg.max())
    po = float(np.mean([(occ[c] @ PAYOFF).max() for c in profiles]))
    tot, n = 0.0, 0
    for c, p in profiles.items():
        astar = (p["T"] @ PAYOFF).argmax(1)
        pr = pairs[c]
        tot += float(PAYOFF[pr[:, 1], astar[pr[:, 0]]].sum()); n += len(pr)
    to = tot / n
    # how many DISTINCT optimal actions does a class use across its techniques?
    nd = float(np.mean([len(set((p["T"] @ PAYOFF).argmax(1).tolist()))
                        for p in profiles.values()]))
    return bf, po, to, to - po, nd


print("=" * 116)
print("  CLEAN FACTORIAL: what makes the task able to reward sequence modelling?")
print("  seq value = (perfect next-technique model) - (perfect class label).")
print("  It must be non-zero for ANY history architecture to distinguish itself.")
print("=" * 116)
print("  %-16s %-10s %-8s %9s %9s %9s %11s %8s"
      % ("classes", "estimator", "drift", "best-fix", "class-orc", "seq-orc",
         "SEQ VALUE", "a*/class"))
print("  " + "-" * 112)
res = []
for cname, cls in CLASSES.items():
    for bname, backoff in (("flat", False), ("backoff", True)):
        for dname, drift in (("on", True), ("off", False)):
            profiles = {}
            for k, members in cls.items():
                gids = goal_ids_for(members)
                init = np.zeros(NT) + 0.02
                for m in members:
                    init[seqs[m][0]] += 2.0
                profiles[k] = {"T": estimate(members, gids, backoff, drift),
                               "init": init / init.sum()}
            bf, po, to, sv, nd = measure(profiles)
            tag = "  <-- SHIPPED" if (cname == "3 consolidated"
                                      and not backoff and drift) else ""
            print("  %-16s %-10s %-8s %9.4f %9.4f %9.4f %+11.4f %8.2f%s"
                  % (cname, bname, dname, bf, po, to, sv, nd, tag))
            res.append((cname, bname, dname, sv))

print("\n" + "=" * 116)
print("  MAIN EFFECTS ON SEQ VALUE")
print("=" * 116)
sv = {(a, b, c): v for a, b, c, v in res}
for factor, lo, hi, idx in (("goal drift  on -> off", "on", "off", 2),
                            ("estimator   flat -> backoff", "flat", "backoff", 1),
                            ("classes     3 -> 7", "3 consolidated", "7 scenarios", 0)):
    a = np.mean([v for k, v in sv.items() if k[idx] == lo])
    b = np.mean([v for k, v in sv.items() if k[idx] == hi])
    print("  %-30s %+.4f -> %+.4f   (%+.4f)" % (factor, a, b, b - a))
print("\n  shipped design seq value: %+.4f" % sv[("3 consolidated", "flat", "on")])
print("  best design    seq value: %+.4f (%s)"
      % (max(sv.values()), max(sv, key=sv.get)))
