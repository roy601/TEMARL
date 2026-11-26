# -*- coding: utf-8 -*-
"""Hawkeyes (Do Hoang et al., Computer Networks 2026) environment, rebuilt from the paper.
Every rule cites the DECISIONS.md entry it implements. Readings R1-R5 are switched by `Reading`."""
import random
from dataclasses import dataclass

import numpy as np

# --- Table 2 (CVE, attack type, obtained privilege, CVSS, EPSS) ------------------------------------
HIGH = {"Root", "System"}
CVES = {
    "Tablet": [("CVE-2019-8689", "Root", 8.8, 0.9392), ("CVE-2018-4441", "Root", 8.8, 0.9183)],
    "Host1": [("CVE-2019-13720", "User", 8.8, 0.9703), ("CVE-2019-1458", "System", 7.8, 0.9714)],
    "Host2": [("CVE-2018-8174", "User", 7.5, 0.9666), ("CVE-2018-8550", "System", 7.8, 0.9556),
              ("CVE-2018-8626", "System", 9.3, 0.088)],
    "Host3": [("CVE-2018-8174", "System", 7.5, 0.9666), ("CVE-2018-8550", "System", 7.8, 0.9556),
              ("CVE-2018-8626", "System", 9.3, 0.088)],
    "Host4": [("CVE-2018-8174", "System", 7.5, 0.9666), ("CVE-2018-8550", "System", 7.8, 0.9556),
              ("CVE-2018-8626", "System", 9.3, 0.088)],
    "Print": [("CVE-2021-34527", "System", 8.8, 0.9584)],
    "LDAP": [("CVE-2021-40444", "System", 8.8, 0.9693), ("CVE-2021-34498", "System", 7.8, 0.8764)],
    "File": [("CVE-2021-44142", "Root", 9.0, 0.1805), ("CVE-2021-44731", "Root", 7.8, 0.1292)],
    "API": [],                                                     # in Fig. 8, not in Table 2 (decision 4)
    "Web": [("CVE-2019-11043", "Root", 9.8, 0.9669), ("CVE-2019-6340", "User", 8.1, 0.9737)],
    "DB": [("CVE-2018-12613", "User", 8.8, 0.9732), ("CVE-2021-3156", "Root", 7.8, 0.9637)],
    "HP1": [("CVE-2019-0887", "System", 8.8, 0.9732), ("CVE-2019-11043", "System", 9.8, 0.9669)],
    "HP2": [("CVE-2019-0887", "System", 8.8, 0.9732), ("CVE-2018-12613", "User", 8.8, 0.9732)],
}
NEW_S2 = [("CVE-2021-34527", "System", 8.8, 0.9584), ("CVE-2021-34498", "System", 7.8, 0.8764)]  # decision 20

GROUPS = [["Tablet", "Host1"], ["Host2", "Host3", "Host4"], ["Web"], ["Print", "LDAP", "File", "API", "DB"]]
REAL = [n for g in GROUPS for n in g]                               # 11 real nodes (decision 4)
GROUP_OF = {n: gi for gi, g in enumerate(GROUPS) for n in g}
HONEYPOTS = ["HP1", "HP2"]
CRITICAL = "DB"
ALPHA_H = 0.5                                                       # decision 11
FNR_FPR = [(0.05, 0.02), (0.10, 0.06), (0.15, 0.10), (0.20, 0.14)]  # decision 10
STRATEGIES = ["HiE", "HiC", "Ran", "RanE", "RanC"]
POLICIES = STRATEGIES + ["Mix"]
MAX_STEPS = 30                                                      # decision 9


@dataclass(frozen=True)
class Reading:
    mix_per_episode: bool = False      # R1
    exploit_prob_epss: bool = False    # R2
    crit_contains_only: bool = False   # R3
    hp_inherits_inbound: bool = False  # R4
    sample_eval: bool = False          # R5


PRIMARY = Reading()
READINGS = {"primary": PRIMARY, "R1": Reading(mix_per_episode=True), "R2": Reading(exploit_prob_epss=True),
            "R3": Reading(crit_contains_only=True), "R4": Reading(hp_inherits_inbound=True),
            "R5": Reading(sample_eval=True)}


class Network:
    """Nodes, CVEs and edges of the old (Scenario 1) or new (Scenario 3) network (decisions 4, 5, 20)."""

    def __init__(self, new=False):
        self.new = new
        self.cves = {n: list(v) for n, v in CVES.items()}
        s1, s2, s3, s4 = GROUPS
        if new:
            for h in s2:
                self.cves[h] = list(NEW_S2)
        self.entry = list(s1) + ["Web"] + (list(s2) if new else [])
        edges = set()
        for g in GROUPS:                                            # every pair inside a subnet
            edges |= {(a, b) for a in g for b in g if a != b}
        edges |= {(a, "Web") for a in s1}
        if not new:
            edges |= {(a, b) for a in s1 for b in s2}
        edges |= {(a, b) for a in s2 for b in s3 + s4}
        edges.add(("Web", "DB"))
        self.edges = {(a, b) for a, b in edges if self.cves[b]}     # only into nodes with a CVE
        self.out = {n: [b for (a, b) in sorted(self.edges) if a == n] for n in REAL}
        self.inbound_groups = {gi: {GROUP_OF[a] for (a, b) in self.edges if GROUP_OF[b] == gi and GROUP_OF[a] != gi}
                               for gi in range(len(GROUPS))}
        # attacker scores (decision 8) and state scores (Eqs. 9-10, decision 11)
        self.max_epss = {n: max((c[3] for c in v), default=0.0) for n, v in self.cves.items()}
        self.max_cvss = {n: max((c[2] for c in v), default=0.0) for n, v in self.cves.items()}
        self.mean_epss = {n: (sum(c[3] for c in v) / len(v) if v else 0.0) for n, v in self.cves.items()}
        self.mean_cvss = {n: (sum(c[2] for c in v) / len(v) if v else 0.0) for n, v in self.cves.items()}
        idx = {n: i for i, n in enumerate(REAL)}
        k = len(REAL)
        self.m_con = np.zeros((k, k), np.float32)
        self.m_vul = np.zeros((k, k, 2), np.float32)
        for a, b in self.edges:
            self.m_con[idx[a], idx[b]] = 1.0
            hc = sum((1.0 if c[1] in HIGH else ALPHA_H) * c[2] for c in self.cves[b])
            he = sum((1.0 if c[1] in HIGH else ALPHA_H) * c[3] for c in self.cves[b])
            self.m_vul[idx[a], idx[b]] = (hc, he)                   # raw Eq. 9-10 values (no scaling stated)
        self.static = np.concatenate([self.m_con.ravel(), self.m_vul.ravel()])
        self.init_groups = sorted({GROUP_OF[n] for n in self.entry})  # decision 12
        adj = {GROUP_OF[a] for (a, b) in self.edges if b == CRITICAL}
        self.crit_groups = sorted(adj | {GROUP_OF[CRITICAL]})
        self.crit_only = [GROUP_OF[CRITICAL]]


STATE_DIM = len(REAL) + len(REAL) ** 2 * 3                         # 11 + 121 + 242 = 374


class Env:
    def __init__(self, net, policy, fnr, fpr, reading=PRIMARY, rng=None, state="full"):
        self.net, self.policy, self.fnr, self.fpr, self.r = net, policy, fnr, fpr, reading
        self.rng = rng or random.Random(0)
        self.state_kind = state                                     # "full" or "so" (decision 20)

    def reset(self):
        self.comp = set()
        self.steps = 0
        self.mix_strategy = self.rng.choice(STRATEGIES) if self.r.mix_per_episode else None
        self.alerts = self._observe()
        return self.obs()

    def _observe(self):                                             # decision 10
        out = []
        for n in REAL:
            p = (1 - self.fnr) if n in self.comp else self.fpr
            out.append(1.0 if self.rng.random() < p else 0.0)
        return np.array(out, np.float32)

    def obs(self):
        if self.state_kind == "so":
            return self.alerts.copy()
        return np.concatenate([self.alerts, self.net.static])

    def allowed_groups(self, gated=True):                           # decision 12 (gate), 19 (no gate)
        all_g = list(range(len(GROUPS)))
        if not gated:
            return all_g, "none"
        alerted = [n for n, a in zip(REAL, self.alerts) if a > 0]
        if not alerted:
            return self.net.init_groups, "init"
        if any((n, CRITICAL) in self.net.edges for n in alerted):
            return (self.net.crit_only if self.r.crit_contains_only else self.net.crit_groups), "crit"
        return all_g, "low"

    def frontier(self, hp_groups):
        """Targets the attacker can select now (decisions 5-7)."""
        reach = set(self.net.entry)
        for n in self.comp:
            reach |= set(self.net.out[n])
        reach -= self.comp
        hps = []
        for hp, g in zip(HONEYPOTS, hp_groups):
            members = set(GROUPS[g])
            ok = bool(members & self.comp)                          # connected to every real node of g
            if self.r.hp_inherits_inbound:                          # R4
                ok = ok or any(GROUP_OF[c] in self.net.inbound_groups[g] for c in self.comp)
                ok = ok or bool(members & set(self.net.entry))
            if ok:
                hps.append(hp)
        return sorted(reach), hps

    def _choose(self, cands, strategy):                             # decision 8
        if strategy == "Ran":
            return self.rng.choice(cands)
        if strategy in ("HiE", "HiC"):
            score = self.net.max_epss if strategy == "HiE" else self.net.max_cvss
            best = max(score[c] for c in cands)
            return self.rng.choice([c for c in cands if score[c] == best])
        w = [(self.net.mean_epss if strategy == "RanE" else self.net.mean_cvss)[c] for c in cands]
        return self.rng.choices(cands, weights=w, k=1)[0]

    def step(self, hp_groups):
        """Attacker acts against honeypots in hp_groups; returns (obs, reward, done, outcome)."""
        self.steps += 1
        real, hps = self.frontier(hp_groups)
        cands = real + hps
        if not cands:
            return self.obs(), 0.0, True, "stuck"
        strategy = self.policy
        if strategy == "Mix":
            strategy = self.mix_strategy or self.rng.choice(STRATEGIES)
        target = self._choose(cands, strategy)
        if target in HONEYPOTS:
            return self.obs(), 1.0, True, "trap"                    # decision 9
        if self.r.exploit_prob_epss and self.rng.random() >= self.net.max_epss[target]:   # R2
            self.alerts = self._observe()
            return self.obs(), 0.0, self.steps >= MAX_STEPS, ("cap" if self.steps >= MAX_STEPS else "")
        self.comp.add(target)
        if target == CRITICAL:
            return self.obs(), -1.0, True, "fail"
        self.alerts = self._observe()
        if self.steps >= MAX_STEPS:
            return self.obs(), 0.0, True, "cap"
        return self.obs(), 0.0, False, ""
