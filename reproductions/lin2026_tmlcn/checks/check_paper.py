# -*- coding: utf-8 -*-
"""Internal-consistency checks of Lin et al. 2026 (IEEE TMLCN), from the published text and Table 6 only.
No environment, no attacker, no result of a reproduction: every check is arithmetic on printed numbers, or a
property of Algorithm 1 as printed that holds for EVERY attacker (shown by proof in DECISIONS.md and
exercised here on random attackers). Standard library only.

    python reproductions/lin2026_tmlcn/checks/check_paper.py      -> checks/CHECKS.txt
"""
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from make_targets import ACTIONS, TABLE6, TACTICS  # noqa: E402

ALPHA, GAMMA, EPS0, EPS_MIN, RHO = 1e-4, 0.90, 0.8, 0.01, 0.95      # Sec. VI-A defaults
N_T = len(TACTICS)                                                  # |T| = 12, tau_T = Impact
PENALTY = -5.0


def algorithm1(attacker, episodes, rng, alpha=ALPHA, gamma=GAMMA, rho=RHO, track=None):
    """Algorithm 1 exactly as printed. attacker(t, a, rng) -> next tactic index, or None (= disconnect).
    Tactic indices 0..11; index 11 = tau_T (Impact). Lines refer to Algorithm 1."""
    Q = [[0.0] * len(ACTIONS) for _ in range(N_T)]                   # line 1
    for _ in range(episodes):                                       # line 2
        eps, t = EPS0, 0                                            # line 3: epsilon reset EVERY episode
        while t != N_T - 1:                                         # line 4
            if rng.random() < eps:                                  # line 8
                a = rng.randrange(len(ACTIONS))
            else:                                                   # line 9
                a = max(range(len(ACTIONS)), key=lambda j: Q[t][j])
            nxt = attacker(t, a, rng)                               # line 10 (proxy executes a)
            if nxt is None:                                         # line 12
                r = PENALTY                                         # line 13
                break                                               # line 14: leaves BEFORE the Q-update
            if nxt == N_T - 1:                                      # line 18
                r = N_T + 1
            elif nxt > t:                                           # line 20
                r = nxt + 1                                         # index(t') + 1 (0-based index)
            else:
                r = 1.0                                             # line 23
            y = r + (gamma * max(Q[nxt]) if nxt != N_T - 1 else 0.0)  # line 26
            Q[t][a] += alpha * (y - Q[t][a])                        # line 27
            if track is not None:
                track(Q)
            eps = max(eps * rho, EPS_MIN)                           # line 28
            t = nxt                                                 # line 29
    return Q


def random_attacker(seed):
    """A random attacker: per (tactic, action) fixed probabilities of disconnecting, staying, advancing."""
    g = random.Random(seed)
    table = {}
    for t in range(N_T):
        for a in range(len(ACTIONS)):
            p_off, p_stay = g.uniform(0, 0.3), g.uniform(0, 0.8)
            table[t, a] = (p_off, p_stay)

    def step(t, a, rng):
        p_off, p_stay = table[t, a]
        u = rng.random()
        if u < p_off:
            return None
        if u < p_off + p_stay * (1 - p_off):
            return t
        return min(N_T - 1, t + 1 + rng.randrange(2))
    return step


def penalties_needed(q_final, alpha):
    """Fewest -5 updates that can take a cell from >= -3.5 down to q_final (< -3.5), when (unlike
    Algorithm 1) the penalty IS applied. Non-penalty targets are >= 1 + gamma * (-5) = -3.5 (all Q >= -5 by
    induction), so below -3.5 only penalty updates move a cell down; each maps q -> (1-alpha) q - 5 alpha."""
    if q_final >= -3.5:
        return 0
    return math.ceil(math.log((q_final + 5) / 1.5) / math.log(1 - alpha))


def main():
    L = ["Lin et al. 2026 (IEEE TMLCN): internal-consistency checks (no reproduction run)", ""]
    neg = [(TACTICS[i], ACTIONS[j], v) for i, row in enumerate(TABLE6) for j, v in enumerate(row) if v < 0]
    L += [f"C1. Table 6 has {len(neg)} negative entries: " + "; ".join(f"{t}/{a} {v}" for t, a, v in neg)]
    L += ["    Algorithm 1 as printed cannot give a negative Q: the -5 is set (line 13) and the loop breaks (line 14)",
          "    before the update; every other reward is >= 1 and Q starts at 0, so each update is a convex",
          "    combination of non-negative numbers."]
    impact = TABLE6[-1]
    L += [f"C2. Table 6 row 'Impact' (tau_T) = {impact}. In Algorithm 1 the loop ends when t' = tau_T (lines 4, 29),",
          "    so Q[tau_T, .] is never updated and stays 0."]
    # property test on random attackers
    rng, worst_min, impact_max, n_runs = random.Random(0), 0.0, 0.0, 30
    for s in range(n_runs):
        seen = []
        Q = algorithm1(random_attacker(s), 300, rng, alpha=0.05,
                       track=lambda Q: seen.append(min(min(r) for r in Q)))
        worst_min = min([worst_min] + seen)
        impact_max = max(impact_max, max(abs(v) for v in Q[-1]))
    L += [f"    Exercised: {n_runs} random attackers x 300 episodes (alpha raised to 0.05 so values move):",
          f"    lowest Q ever = {worst_min}, largest |Q[Impact, .]| = {impact_max} (both 0, as proved)."]
    L += ["", "C3. Even if the -5 penalty WERE applied (not Algorithm 1), Table 6 needs more penalties than sessions."]
    L += ["    A penalty ends its session, so there is at most one per session: at most 2000 (Sec. VI-B; 1200 in Sec. VII)."]
    for alpha in (1e-4, 2e-4, 5e-4, 1e-3):
        need = [(t, a, v, penalties_needed(v, alpha)) for t, a, v in neg]
        total = sum(n for *_, n in need)
        worst = max(need, key=lambda x: x[3])
        L += [f"    alpha {alpha:g}: cells below -3.5 need >= {total} penalty updates in total"
              f" (largest single cell {worst[0]}/{worst[1]} {worst[2]}: {worst[3]}); "
              + ("IMPOSSIBLE with <= 2000 sessions" if total > 2000 else "possible")]
    L += ["", "C4. Text vs Table 6 (greedy action = largest Q in the row):"]
    for i, row in enumerate(TABLE6):
        j = max(range(len(ACTIONS)), key=lambda k: row[k])
        L += [f"    {i + 1:2d} {TACTICS[i]:<27} best {ACTIONS[j]:<7} {row[j]}"]
    mid = [ACTIONS[max(range(7), key=lambda k: TABLE6[i][k])] for i in range(5, 9)]
    late = [ACTIONS[max(range(7), key=lambda k: TABLE6[i][k])] for i in (9, 10)]
    L += [f"    Text: tactics 6-9 'increasingly favors Modify' -> table's best there: {mid}",
          f"    Text: later stages 'shift toward Delay and Jitter' -> table's best in tactics 10-11: {late}"]
    steps = {rho: math.log(EPS_MIN / EPS0) / math.log(rho) for rho in (0.95, 0.99)}
    L += ["", f"C5. Epsilon is reset to 0.8 every episode (line 3) and decays per step (line 28): it reaches 0.01 after"
          f" {steps[0.95]:.1f} steps (rho 0.95) or {steps[0.99]:.1f} steps (rho 0.99), ratio {steps[0.99] / steps[0.95]:.2f}."
          " The text says rho 0.99 explores 'roughly twice as many episodes'; with the reset, exploration does not"
          " span episodes at all."]
    L += ["", "C6. Time: 'tactic 10 within 800 episodes (approximately 12 minutes)' = "
          f"{12 * 60 / 800:.2f} s per session; '300 episodes (around 4 minutes)' = {4 * 60 / 300:.2f} s; 'first 400"
          f" sessions = initial five minutes' = {5 * 60 / 400:.2f} s. Fig. 7 / Sec. VI-B: one session lasts 17-70 s,"
          f" so 800 consecutive sessions take {800 * 17 / 3600:.1f}-{800 * 70 / 3600:.1f} hours."]
    L += ["", "C7. Session counts: 2000 consecutive sessions (Sec. VI-B, Fig. 6); 1200 (Fig. 8, Sec. VII);"
          " 1000 (Figs. 7, 9, 10, 11); '700 attack-response cycles' (abstract)."]
    L += ["", "C8. Duration: abstract 'more than doubles the average engagement time'; Sec. VI-B/VII 'median ... factor"
          f" of two'. Fig. 7 (moving average): RL > 70 s vs Static1 ~40 s = {70 / 40:.2f}x, vs Static0 ~17 s ="
          f" {70 / 17:.2f}x. Medians are not shown."]
    text = "\n".join(L) + "\n"
    (HERE / "CHECKS.txt").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
