# -*- coding: utf-8 -*-
"""Wang et al. 2020 (IEEE Access 8:35792), rebuilt from the paper: network, attacker, alarms, the four
deployment policies and the Q-learner. Every rule names the DECISIONS.md entry it implements.

Pure Python (random, no NumPy), so a run is identical on every machine with the same Python.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent

LOCATIONS = ["Web Server", "Pad", "Host 1", "Host 2", "Host 3", "File Server", "Data Server"]   # D1
DATA = 6                                                   # location 7 = the data server (D1, F3)
ATTACKER = -1
ACTIONS = list(itertools.combinations(range(7), 2))       # D3: static policy k = ACTIONS[k - 1]
SETTINGS = [(0.05, 0.02), (0.10, 0.06), (0.15, 0.10), (0.20, 0.14)]   # (FNR, FPR), Table 3 / Figs. 10-13
MAX_STEPS = 20                                            # D8
N_STATES = 2 ** 7


def _load_edges():
    d = json.loads((HERE / "data" / "ntpg.json").read_text(encoding="utf-8"))
    idx = {n: i for i, n in enumerate(LOCATIONS)}
    idx["Attacker"] = ATTACKER
    into = {n: [] for n in range(7)}
    out_degree = [0] * 7
    for s, t, up, rp in d["edges"]:                       # D2: Fig. 8 as printed
        into[idx[t]].append((idx[s], float(up), float(rp)))
        if idx[s] != ATTACKER:
            out_degree[idx[s]] += 1
    return into, out_degree


IN_EDGES, OUT_DEGREE = _load_edges()
J_COL = {"UP": 1, "RP": 2}
# D16: a decoy "is the same as n_cr" and its location does not change J: J(decoy) = the data server's best
# incoming edge under the same privilege reading.
J_DECOY = {k: max(e[c] for e in IN_EDGES[DATA]) for k, c in J_COL.items()}
# D17: the fixed interestingness readings (a random reading is drawn per experiment in Env.reset).
INTEREST = {
    "uniform": (1.0,) * 7,
    "role": (1.0, 0.5, 0.5, 0.5, 0.5, 1.0, 1.0),          # servers 1, pad and hosts 0.5
    "outdegree": tuple(d / max(OUT_DEGREE) for d in OUT_DEGREE),
}


def seed_of(*parts) -> int:
    """A stable seed from any labels (Python's hash() of a string changes between runs)."""
    return int.from_bytes(hashlib.sha256(repr(parts).encode()).digest()[:8], "big")


@dataclass(frozen=True)
class Attacker:
    """One reading of Eq. 1 and its unpublished inputs (DECISIONS D4-D7, D15-D18; grid in Section 4)."""
    choice: str            # "argmax" (Eq. 1) | "proportional" (Sec. II.B: p_n grows with I(n) and J(n))
    j: str                 # "UP" | "RP": which Fig. 8 probability is J (D4)
    interest: str          # "uniform" | "role" | "outdegree" | "random" (D5, D17)
    decoy_interest: str    # "data" (as the data server) | "location" (as the node it sits behind) (D6)
    alpha: float           # weight of I; beta = 1 - alpha (Eq. 1, 0 < alpha, beta < 1)
    ties: str              # "index" | "random": ties in argmax (D7); unused by "proportional"

    @property
    def name(self):
        return "|".join(f"{k}={v}" for k, v in asdict(self).items())


class Env:
    """One attack at a time (an "experiment"). The defender places both decoys before every attack action
    (D13); the attacker picks one target (Eq. 1 reading), the exploit succeeds with probability J (D15);
    then the NMS raises the alarms that form the next state (D9)."""

    def __init__(self, att: Attacker, setting, rng: random.Random):
        self.att, self.rng = att, rng
        self.fnr, self.fpr = setting
        self.jc = J_COL[att.j]
        self.reset()

    def reset(self):
        self.comp = [False] * 7
        self.t = 0
        if self.att.interest == "random":                 # D17: one interest vector per attacker (experiment)
            self.I = tuple(self.rng.random() for _ in range(7))
        else:
            self.I = INTEREST[self.att.interest]
        self.state = 0                                    # Table 3: initial state [0 0 0 0 0 0 0]
        return self.state

    def targets(self, action):
        """(kind, location, I, J) of every node the attacker can invade now. Real nodes in location order,
        then decoys in the order of their locations (D18)."""
        c = self.comp
        out = []
        for n in range(7):
            if c[n]:
                continue
            js = [e[self.jc] for e in IN_EDGES[n] if e[0] == ATTACKER or c[e[0]]]
            if js:
                out.append(("real", n, self.I[n], max(js)))          # D15: the best edge from any foothold
        for x in sorted(action):
            if c[x]:                                                  # a decoy behind x is reachable once x is held
                i_d = self.I[DATA] if self.att.decoy_interest == "data" else self.I[x]
                out.append(("decoy", x, i_d, J_DECOY[self.att.j]))
        return out

    def choose(self, cands):
        a = self.att
        scores = [a.alpha * i + (1.0 - a.alpha) * j for _, _, i, j in cands]
        if a.choice == "argmax":
            m = max(scores)
            tied = [k for k, s in enumerate(scores) if s >= m - 1e-12]
            k = tied[0] if a.ties == "index" else tied[self.rng.randrange(len(tied))]
            return cands[k]
        total = sum(scores)
        r = self.rng.random() * total
        acc = 0.0
        for k, s in enumerate(scores):
            acc += s
            if r < acc:
                return cands[k]
        return cands[-1]

    def step(self, action):
        """action = (x, y), two different locations (one-to-one mapping). Returns (state, reward, done, outcome)."""
        cands = self.targets(action)
        assert cands, "the attacker always has a target (Web, Pad and Host 1 face the Internet)"
        kind, n, _, j = self.choose(cands)
        self.t += 1
        outcome = None
        if self.rng.random() < j:                         # D15: the exploit succeeds with probability J
            if kind == "decoy":
                outcome = "trap"
            elif n == DATA:
                outcome = "fail"
            else:
                self.comp[n] = True
        if outcome is None and self.t >= MAX_STEPS:      # D8 / D19: the limit counts as a failed defence
            outcome = "timeout"
        s = 0
        for i in range(7):                                # D9: fresh alarms after every attack action
            p = 1.0 - self.fnr if self.comp[i] else self.fpr
            if self.rng.random() < p:
                s |= 1 << i
        self.state = s
        reward = 1 if outcome == "trap" else (-1 if outcome is not None else 0)   # Eq. 10
        return s, reward, outcome is not None, outcome


ACTION_INDEX = {a: k for k, a in enumerate(ACTIONS)}


# ----------------------------------------------------------------------------- defenders (Eqs. 3-6)
def static_policy(k):
    """Eq. 3: static policy k (1-21) is the fixed pair ACTIONS[k - 1]."""
    a = k - 1
    return lambda state, t: a


def random_dynamic(rng: random.Random, reading="b"):
    """Eq. 4, one repeat of Fig. 11 (D11). (b): a random A_t for every time t, drawn once and used for all
    the repeat's attacks. (a): one random deployment for the whole repeat."""
    if reading == "b":
        seq = [rng.randrange(len(ACTIONS)) for _ in range(MAX_STEPS)]
    else:
        seq = [rng.randrange(len(ACTIONS))] * MAX_STEPS
    return lambda state, t: seq[t]


def following_alarm(rng: random.Random):
    """Eq. 5 with D10."""
    def act(state, t):
        al = [i for i in range(7) if state >> i & 1]
        if len(al) >= 2:
            pair = rng.sample(al, 2)
        elif len(al) == 1:
            pair = [al[0], rng.choice([i for i in range(7) if i != al[0]])]
        else:
            return rng.randrange(len(ACTIONS))
        return ACTION_INDEX[tuple(sorted(pair))]
    return act


def greedy(qrow, rng: random.Random):
    """argmax with ties broken at random (F5, D12)."""
    m = max(qrow)
    tied = [a for a, q in enumerate(qrow) if q == m]
    return tied[rng.randrange(len(tied))] if len(tied) > 1 else tied[0]


def evaluate(att, setting, policy, n, env_seed):
    """dsp (Eq. 16) of a policy over n experiments, and the share of experiments that hit the step limit."""
    env = Env(att, setting, random.Random(env_seed))
    traps = timeouts = 0
    for _ in range(n):
        s = env.reset()
        while True:
            s, _, done, out = env.step(ACTIONS[policy(s, env.t)])
            if done:
                traps += out == "trap"
                timeouts += out == "timeout"
                break
    return traps / n, timeouts / n


def q_learning(att, setting, steps, checkpoints, eval_n, seed, gamma=0.9, epsilon=0.1):
    """Algorithm 1 with Eqs. 14-15 (D12, D20). A training step is one defender decision; an episode
    restarts from s0. At each checkpoint the greedy policy is evaluated on eval_n new experiments."""
    env = Env(att, setting, random.Random(seed_of("q-train-env", att.name, setting, seed)))
    rng = random.Random(seed_of("q-train-agent", att.name, setting, seed))
    Q = [[0.0] * len(ACTIONS) for _ in range(N_STATES)]
    visits = [[0] * len(ACTIONS) for _ in range(N_STATES)]
    marks = sorted(set(checkpoints))
    res = {}
    s = env.reset()
    for t in range(steps + 1):
        if t in marks:
            erng = random.Random(seed_of("q-eval-agent", att.name, setting, seed, t))
            res[t] = evaluate(att, setting, lambda st, _t: greedy(Q[st], erng), eval_n,
                              seed_of("q-eval-env", att.name, setting, seed, t))[0]
        if t == steps:
            break
        a = rng.randrange(len(ACTIONS)) if rng.random() < epsilon else greedy(Q[s], rng)
        s2, r, done, _ = env.step(ACTIONS[a])
        q_update(Q, visits, s, a, r, s2, done, gamma)
        s = env.reset() if done else s2
    return res


def q_update(Q, visits, s, a, r, s2, done, gamma):
    """Eq. 14 with the learning rate of Eq. 15, whose visit count includes the current update (D20)."""
    visits[s][a] += 1
    alpha = 1.0 / (1.0 + visits[s][a])
    target = r if done else r + gamma * max(Q[s2])         # a final state has value 0
    Q[s][a] += alpha * (target - Q[s][a])
    return alpha
