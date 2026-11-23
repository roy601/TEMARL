"""Transparent synthetic attack network and fixed-trajectory generator.

All structures and transition/emission probabilities are ORIGINAL DESIGN
ASSUMPTIONS. These are not claimed to be the BAAHS authors' exact inputs.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np

STAGES = (
    "reconnaissance", "initial_access", "execution", "persistence",
    "privilege_escalation", "defense_evasion", "credential_access",
    "discovery", "lateral_movement", "collection", "exfiltration",
)
ROLES = ("workstation", "server", "database", "admin", "dmz", "application")
# Exactly 25 synthetic nodes: 8+5+4+3+3+2
ROLE_COUNTS = (8, 5, 4, 3, 3, 2)
# Rows sum to one. Role priors are deliberately hand-designed illustrative data.
ROLE_STAGE = np.array([
    [.30, .00, .00, .00, .50, .20],
    [.30, .00, .00, .00, .60, .10],
    [.42, .28, .00, .00, .00, .30],
    [.40, .40, .00, .00, .00, .20],
    [.20, .45, .00, .35, .00, .00],
    [.30, .35, .00, .00, .35, .00],
    [.55, .20, .00, .25, .00, .00],
    [.50, .25, .00, .00, .25, .00],
    [.35, .30, .00, .20, .00, .15],
    [.00, .25, .65, .10, .00, .00],
    [.00, .00, .30, .00, .45, .25],
], dtype=float)


def transition_matrix() -> np.ndarray:
    """A synthetic forward-progression stage transition matrix."""
    n = len(STAGES)
    a = np.zeros((n, n), dtype=float)
    for s in range(n):
        a[s, s] += .40
        a[s, (s+1) % n] += .40
        a[s, (s+2) % n] += .15
        a[s, 0] += .05
    return a


def emission_matrix() -> np.ndarray:
    """Synthetic discrete alarm emission probabilities."""
    n = len(STAGES)
    e = np.ones((n, n), dtype=float) * (.10/n)
    for s in range(n):
        e[s, s] += .70
        e[s, (s+1) % n] += .10
        e[s, (s-1) % n] += .10
    return e


@dataclass(frozen=True)
class Event:
    """A recorded attacker visit; hidden_state is never passed to policies."""
    node: int
    alert: int
    hidden_state: int


class World:
    def __init__(self, nodes: int = 25):
        if nodes != 25:
            raise ValueError("The current illustrative topology has exactly 25 nodes")
        self.n = nodes
        self.roles = np.array(sum(([role] * count for role, count in enumerate(ROLE_COUNTS)), []), dtype=int)
        self.adjacency = np.zeros((nodes, nodes), dtype=float)
        # Role-local rings, then cross-role bridges for a connected enterprise.
        i = 0
        for count in ROLE_COUNTS:
            ids = list(range(i, i + count))
            for p in range(count):
                self._edge(ids[p], ids[(p + 1) % count])
            i += count
        for a, b in [(0, 8), (2, 9), (4, 10), (6, 11),
                     (8, 13), (10, 15), (12, 16), (11, 17),
                     (0, 18), (3, 19), (8, 20), (10, 20),
                     (18, 21), (19, 22), (22, 23), (20, 24),
                     (23, 12), (24, 9), (14, 17), (7, 21)]:
            self._edge(a, b)
        # Two types of proximity: direct neighbors and two hops.
        one = (self.adjacency > 0).astype(float)
        two = ((one @ one) > 0).astype(float)
        np.fill_diagonal(two, 0)
        self.proximity = .70 * one + .25 * two
        self.proximity = np.maximum(self.proximity, 0)
        self.proximity /= np.maximum(self.proximity.sum(axis=1, keepdims=True), 1e-12)
        # Hand-chosen operational risk and data-quality proxies, not paper values.
        self.risk = np.array([.18, .32, .55, .82, .42, .26])[self.roles]
        self.quality = np.array([.45, .76, .88, .83, .68, .79])[self.roles]
        self.state_node = self._state_node_matrix()
        self.transition = transition_matrix()
        self.emission = emission_matrix()

    def _edge(self, a: int, b: int) -> None:
        if a != b:
            self.adjacency[a, b] = self.adjacency[b, a] = 1.

    def _state_node_matrix(self) -> np.ndarray:
        out = np.zeros((len(STAGES), self.n))
        for s in range(len(STAGES)):
            for r in range(len(ROLES)):
                ids = np.where(self.roles == r)[0]
                out[s, ids] = ROLE_STAGE[s, r] / len(ids)
        assert np.allclose(out.sum(axis=1), 1), out.sum(axis=1)
        return out

    def predict_visits(self, belief: np.ndarray, last_node: int) -> np.ndarray:
        """Forecast next target using ONLY current belief and last observed node."""
        belief = np.asarray(belief, dtype=float)
        next_state = belief @ self.transition
        prob = .60 * (next_state @ self.state_node)
        prob += .30 * self.proximity[last_node]
        prob += .10 / self.n
        return prob / prob.sum()

    def make_trajectory(self, seed: int, steps: int) -> list[Event]:
        """Generate the full attack path BEFORE any policy runs (open-loop attacker)."""
        if steps < 2:
            raise ValueError("steps must be >= 2")
        rng = np.random.default_rng(seed)
        state = 0
        node = int(rng.choice(self.n, p=self.state_node[state]))
        path = []
        for i in range(steps):
            if i:
                state = int(rng.choice(len(STAGES), p=self.transition[state]))
                nxt = .60 * self.state_node[state] + .30 * self.proximity[node] + .10 / self.n
                node = int(rng.choice(self.n, p=nxt / nxt.sum()))
            alert = int(rng.choice(len(STAGES), p=self.emission[state]))
            path.append(Event(node=node, alert=alert, hidden_state=state))
        return path
