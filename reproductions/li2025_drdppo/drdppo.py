# -*- coding: utf-8 -*-
"""Li, Zhao & Wu 2025 (Sci. Rep. 15:16830), DRD-PPO: the simulator, the baselines and the learner, rebuilt from
the paper under DECISIONS.md (decisions 3-16, protocol C1-C9, amendments A1-A10). No code was released.

Network (decision 3; Table 1, Fig. 3): Host1-2 (subnet1), Host3-5 (subnet2), Server1-2 (subnet3), each with the
CVE of Table 1. Defender: up to 2 H-honeypots (clone a server: same CVE) and 10 F-honeypots (fake traffic to an
H-honeypot, raising its correlation score). Attacker (Eq. 2, decision 8): computes for every node
    importance_i = [1 - (1-VC)(1-VI)(1-VA)] + NL_i * w        (normalised; the argmax is unchanged)
and attacks the highest one (ties uniformly at random); the defence succeeds iff that node is a honeypot.
Reward (Eqs. 5-6, decision 9): R_t - (n_d * 0.5 + n_v * 0.1) every step; R_t = +R1 / -R1 at the attack, R2 before.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
NVD = HERE / "data" / "nvd"

HOSTS = ("Host1", "Host2", "Host3", "Host4", "Host5")
SERVERS = ("Server1", "Server2")
REAL = HOSTS + SERVERS
SUBNET = {"Host1": 1, "Host2": 1, "Host3": 2, "Host4": 2, "Host5": 2, "Server1": 3, "Server2": 3}
CVE = {"Host1": "CVE-2018-8245", "Host2": "CVE-2015-1769", "Host3": "CVE-2014-0226", "Host4": "CVE-2016-4729",
       "Host5": "CVE-2018-8174", "Server1": "CVE-2016-1930", "Server2": "CVE-2016-1935"}       # Table 1
ALPHA, BETA = 2, 10                       # Table 2: maximum H- and F-honeypots
COST_H, COST_F = 0.5, 0.1                 # Table 2
STEPS = 30                                # Table 2: timesteps per episode
IMPACT = {"v2": {"NONE": 0.0, "PARTIAL": 0.275, "COMPLETE": 0.660},
          "v3": {"NONE": 0.0, "LOW": 0.22, "HIGH": 0.56}}
# decision 6 / C2: which servers each host communicates with
LINKS = {"P1": {h: SERVERS for h in HOSTS},
         "P2": {h: ("Server1",) if SUBNET[h] == 1 else ("Server2",) for h in HOSTS},
         "P3": {h: SERVERS if SUBNET[h] == 1 else ("Server2",) for h in HOSTS}}

# actions (A8): 0 no change, 1 add H, 2 remove H, 3 add F, 4 remove F, 5-8 retarget, 9-28 relink
NOOP, ADD_H, REM_H, ADD_F, REM_F = range(5)
RETARGET0 = 5                             # 5 + 2*i + j : H-honeypot i -> server j
RELINK0 = RETARGET0 + ALPHA * len(SERVERS)  # 9 + 2*k + i : F-honeypot k -> H-honeypot i
N_ACTIONS = RELINK0 + BETA * ALPHA        # 29
RELATION_ACTIONS = tuple(range(RETARGET0, N_ACTIONS))


@dataclasses.dataclass(frozen=True)
class Setting:
    """Everything that decides an episode's outcome or reward. Defaults = DECISIONS.md primary choices."""
    w: float = 0.1                # decision 5
    links: str = "P1"             # decision 6
    timing: str = "last"          # decision 9 / A6: "last" or "random"
    cvss: str = "v2"              # decision 4
    h_links: str = "f_only"       # decision 7 / A10: "f_only" or "f_plus_server"
    R1: float = 10.0              # decision 9
    R2: float = 0.0
    clip: float = 0.2             # decision 11

    def __post_init__(self):
        assert self.links in LINKS and self.timing in ("last", "random") and self.cvss in IMPACT
        assert self.h_links in ("f_only", "f_plus_server")

    def key(self) -> str:
        return (f"w={self.w}|links={self.links}|timing={self.timing}|cvss={self.cvss}|h_links={self.h_links}"
                f"|R1={self.R1}|R2={self.R2}|clip={self.clip}")


def load_impacts(version: str) -> dict:
    """CVE -> (C, I, A) impact values from the NVD records in data/nvd/ (decision 4). For v3, CVE-2014-0226 has
    no v3 record and keeps its v2 values (A10)."""
    out = {}
    for cve in sorted(set(CVE.values())):
        m = json.loads((NVD / f"{cve}.json").read_text(encoding="utf-8"))["vulnerabilities"][0]["cve"]["metrics"]
        v2 = m["cvssMetricV2"][0]["cvssData"]
        vals = tuple(IMPACT["v2"][v2[k]] for k in ("confidentialityImpact", "integrityImpact", "availabilityImpact"))
        if version == "v3":
            v3 = (m.get("cvssMetricV31") or m.get("cvssMetricV30") or [None])[0]
            if v3 is not None:
                d = v3["cvssData"]
                vals = tuple(IMPACT["v3"][d[k]] for k in ("confidentialityImpact", "integrityImpact", "availabilityImpact"))
        out[cve] = vals
    return out


def vuln_term(cia) -> float:
    c, i, a = cia
    return 1.0 - (1.0 - c) * (1.0 - i) * (1.0 - a)


class World:
    """The fixed part of a setting: vulnerability terms and communication counts of the real nodes."""

    def __init__(self, s: Setting):
        imp = load_impacts(s.cvss)
        self.s = s
        self.vuln = {n: vuln_term(imp[CVE[n]]) for n in REAL}
        self.nl = {h: len(LINKS[s.links][h]) for h in HOSTS}
        for sv in SERVERS:
            self.nl[sv] = sum(sv in LINKS[s.links][h] for h in HOSTS)
        self.real_scores = np.array([self.vuln[n] + self.nl[n] * s.w for n in REAL])
        self.top_server = max(range(len(SERVERS)), key=lambda j: self.real_scores[len(HOSTS) + j])
        self.L1 = np.array([[float(sv in LINKS[s.links][h]) for sv in SERVERS] for h in HOSTS], np.float32)


class Env:
    """One defender, one reconnaissance attacker, one episode of up to 30 steps."""

    def __init__(self, s: Setting, rng: np.random.Generator):
        self.s, self.rng, self.world = s, rng, World(s)
        self.state_dim = len(self.observe_template())

    # ── state ────────────────────────────────────────────────────────────────
    def reset(self, start: str = "empty"):
        self.h_on = np.zeros(ALPHA, bool)
        self.h_target = np.zeros(ALPHA, int)
        self.f_on = np.zeros(BETA, bool)
        self.f_link = np.zeros(BETA, int)
        if start == "full_random":                     # A7: Alg2 and Alg3
            self.h_on[:] = True
            self.h_target[:] = self.rng.integers(0, len(SERVERS), ALPHA)
            self.f_on[:] = True
            self.f_link[:] = self.rng.integers(0, ALPHA, BETA)
        elif start != "empty":
            raise ValueError(start)
        self.t = 0
        self.attack_at = STEPS if self.s.timing == "last" else int(self.rng.integers(1, STEPS + 1))   # A6
        self.done = False
        self.success = None
        return self.observe()

    def observe_template(self):
        return np.zeros(2 + 10 + BETA * ALPHA + ALPHA * len(SERVERS) + ALPHA + BETA + len(REAL) + 1, np.float32)

    def observe(self) -> np.ndarray:
        """Eq. (3) flattened (decision 10): counts, L1, L2, Aim, active flags, node states T, time."""
        L2 = np.zeros((BETA, ALPHA), np.float32)
        L2[np.flatnonzero(self.f_on), self.f_link[self.f_on]] = 1.0
        aim = np.zeros((ALPHA, len(SERVERS)), np.float32)
        aim[np.flatnonzero(self.h_on), self.h_target[self.h_on]] = 1.0
        return np.concatenate([[self.h_on.sum() / ALPHA, self.f_on.sum() / BETA], self.world.L1.ravel(), L2.ravel(),
                               aim.ravel(), self.h_on.astype(np.float32), self.f_on.astype(np.float32),
                               np.ones(len(REAL), np.float32), [self.t / STEPS]]).astype(np.float32)

    # ── constraints (Eqs. 10-14, A8) ─────────────────────────────────────────
    def mask(self, allowed=None) -> np.ndarray:
        m = np.zeros(N_ACTIONS, bool)
        m[NOOP] = True
        nd, nv = int(self.h_on.sum()), int(self.f_on.sum())
        m[ADD_H] = nd < ALPHA                                           # Eq. (10)
        m[REM_H] = nd > 1 or (nd == 1 and nv == 0)                      # Eqs. (10), (14)
        m[ADD_F] = nd > 0 and nv < BETA                                 # Eqs. (11), (12)
        m[REM_F] = nv > 0                                               # Eq. (11)
        for i in range(ALPHA):
            for j in range(len(SERVERS)):
                m[RETARGET0 + 2 * i + j] = self.h_on[i] and self.h_target[i] != j        # Eq. (13)
        for k in range(BETA):
            for i in range(ALPHA):
                m[RELINK0 + ALPHA * k + i] = self.f_on[k] and self.h_on[i] and self.f_link[k] != i   # Eq. (14)
        if allowed is not None:
            keep = np.zeros(N_ACTIONS, bool)
            keep[list(allowed)] = True
            m &= keep
            if not m.any():
                m[NOOP] = True
        return m

    def apply(self, a: int):
        if not self.mask()[a]:
            raise ValueError(f"action {a} is not allowed in this state")
        if a == ADD_H:
            i = int(np.flatnonzero(~self.h_on)[0])
            self.h_on[i], self.h_target[i] = True, 0
        elif a == REM_H:
            i = int(np.flatnonzero(self.h_on)[-1])
            self.h_on[i] = False
            rest = np.flatnonzero(self.h_on)
            if len(rest):
                self.f_link[self.f_on & (self.f_link == i)] = int(rest[0])
        elif a == ADD_F:
            k = int(np.flatnonzero(~self.f_on)[0])
            self.f_on[k], self.f_link[k] = True, int(np.flatnonzero(self.h_on)[0])
        elif a == REM_F:
            self.f_on[int(np.flatnonzero(self.f_on)[-1])] = False
        elif RETARGET0 <= a < RELINK0:
            i, j = divmod(a - RETARGET0, len(SERVERS))
            self.h_target[i] = j
        elif a >= RELINK0:
            k, i = divmod(a - RELINK0, ALPHA)
            self.f_link[k] = i

    # ── the attacker (Eq. 2, decision 8) ─────────────────────────────────────
    def scores(self):
        """(node names, scores, is_honeypot) of every node the attacker sees."""
        names, sc, hp = list(REAL), list(self.world.real_scores), [False] * len(REAL)
        w = self.s.w
        for i in np.flatnonzero(self.h_on):
            server = SERVERS[self.h_target[i]]
            nl = int((self.f_on & (self.f_link == i)).sum())
            if self.s.h_links == "f_plus_server":
                nl += self.world.nl[server]
            names.append(f"H{i}")
            sc.append(self.world.vuln[server] + nl * w)
            hp.append(True)
        for k in np.flatnonzero(self.f_on):
            names.append(f"F{k}")
            sc.append(0.0 + 1 * w)                                       # decision 7: no vulnerability, NL = 1
            hp.append(True)
        return names, np.asarray(sc), np.asarray(hp)

    def attack(self) -> bool:
        _, sc, hp = self.scores()
        best = np.flatnonzero(np.isclose(sc, sc.max(), rtol=0, atol=1e-12))
        return bool(hp[int(self.rng.choice(best))])

    # ── one step ─────────────────────────────────────────────────────────────
    def step(self, a: int):
        if self.done:
            raise RuntimeError("episode finished")
        self.apply(a)
        self.t += 1
        r = self.s.R2
        if self.t >= self.attack_at:
            self.success = self.attack()
            r = self.s.R1 if self.success else -self.s.R1
            self.done = True
        r -= self.h_on.sum() * COST_H + self.f_on.sum() * COST_F           # Eq. (5): counts after the action
        return self.observe(), float(r), self.done


# ── non-learning policies ─────────────────────────────────────────────────────

def random_action(env: Env, allowed=None) -> int:
    return int(env.rng.choice(np.flatnonzero(env.mask(allowed))))


def scripted_action(env: Env) -> int:
    """A2's scripted reference: one H-honeypot on the top server, then F-honeypots linked to it until it
    outranks every real node, then no change."""
    if not env.h_on.any():
        return ADD_H
    i = int(np.flatnonzero(env.h_on)[0])
    if env.h_target[i] != env.world.top_server:
        return RETARGET0 + 2 * i + env.world.top_server
    names, sc, hp = env.scores()
    if sc[hp].max() > sc[~hp].max() + 1e-12:
        return NOOP
    return ADD_F if env.mask()[ADD_F] else NOOP


def run_policy(s: Setting, seed: int, episodes: int, policy: str) -> list:
    """policy: 'alg1' (random, from empty), 'alg3' (random relations, full counts), 'scripted'.
    Returns one bool per episode (defence success)."""
    rng = np.random.default_rng(seed)
    env = Env(s, rng)
    out = []
    for _ in range(episodes):
        env.reset("full_random" if policy == "alg3" else "empty")
        while not env.done:
            if policy == "alg1":
                a = random_action(env)
            elif policy == "alg3":
                a = random_action(env, RELATION_ACTIONS)
            elif policy == "scripted":
                a = scripted_action(env)
            else:
                raise ValueError(policy)
            env.step(a)
        out.append(env.success)
    return out


# ── DRD-PPO (Algorithm 1, decision 11, A9) ────────────────────────────────────

def make_nets(state_dim: int):
    import torch.nn as nn
    actor = nn.Sequential(nn.Linear(state_dim, 32), nn.Tanh(), nn.Linear(32, N_ACTIONS))
    critic = nn.Sequential(nn.Linear(state_dim, 32), nn.Tanh(), nn.Linear(32, 1))
    return actor, critic


def train_ppo(s: Setting, seed: int, episodes: int, variant: str = "drd", learn: bool = True,
              eval_episodes: int = 0, lr: float = 0.005, gamma: float = 0.9, lam: float = 0.95, epochs: int = 4):
    """variant 'drd' = DRD-PPO (full action set, starts empty); 'alg2' = PPO over relations at full counts.
    learn=False gives the random-initialised reference (A2). Returns a dict with the success list of the
    training episodes and, if eval_episodes > 0, of separate evaluation episodes (sampled actions, A5)."""
    import torch
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    rng = np.random.default_rng(seed)
    env = Env(s, rng)
    actor, critic = make_nets(env.state_dim)
    opt_a = torch.optim.Adam(actor.parameters(), lr=lr)
    opt_c = torch.optim.Adam(critic.parameters(), lr=lr)
    allowed = RELATION_ACTIONS if variant == "alg2" else None
    start = "full_random" if variant == "alg2" else "empty"

    def act(obs, m):
        with torch.no_grad():
            logits = actor(torch.as_tensor(obs)).masked_fill(~torch.as_tensor(m), -1e9)
            dist = torch.distributions.Categorical(logits=logits)
            a = dist.sample()
            return int(a), float(dist.log_prob(a))

    def episode():
        obs = env.reset(start)
        traj = []
        while not env.done:
            m = env.mask(allowed)
            a, lp = act(obs, m)
            nxt, r, done = env.step(a)
            traj.append((obs, m, a, lp, r, done))
            obs = nxt
        return traj, env.success

    def update(traj):
        S = torch.as_tensor(np.stack([x[0] for x in traj]))
        M = torch.as_tensor(np.stack([x[1] for x in traj]))
        A = torch.as_tensor([x[2] for x in traj])
        LP = torch.as_tensor([x[3] for x in traj])
        R = np.array([x[4] for x in traj], np.float32)
        with torch.no_grad():
            V = critic(S).squeeze(-1).numpy()
        adv = np.zeros_like(R)
        gae = 0.0
        for t in reversed(range(len(R))):
            nxt = 0.0 if t == len(R) - 1 else V[t + 1]          # the episode ends at the attack
            delta = R[t] + gamma * nxt - V[t]
            gae = delta + gamma * lam * gae
            adv[t] = gae
        ret = torch.as_tensor(adv + V)
        adv = torch.as_tensor(adv)
        if len(adv) > 1:
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        for _ in range(epochs):
            logits = actor(S).masked_fill(~M, -1e9)
            lp = torch.distributions.Categorical(logits=logits).log_prob(A)
            ratio = torch.exp(lp - LP)
            loss_a = -torch.min(ratio * adv, ratio.clamp(1 - s.clip, 1 + s.clip) * adv).mean()
            opt_a.zero_grad()
            loss_a.backward()
            opt_a.step()
            loss_c = ((critic(S).squeeze(-1) - ret) ** 2).mean()
            opt_c.zero_grad()
            loss_c.backward()
            opt_c.step()

    train = []
    for _ in range(episodes):
        traj, ok = episode()
        train.append(ok)
        if learn:
            update(traj)
    evals = [episode()[1] for _ in range(eval_episodes)]
    return {"train": train, "eval": evals}


def dsp(successes) -> float:
    """Defensive success probability in percent."""
    return 100.0 * float(np.mean(successes)) if len(successes) else float("nan")
