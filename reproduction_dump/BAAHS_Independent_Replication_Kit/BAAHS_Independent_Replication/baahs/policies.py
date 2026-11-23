"""Independent illustrative BAAHS-inspired placement policies and baselines.

All policies see only events up to time t, never the node of event t+1.
Posterior updates use the observed next event only AFTER its hit is scored.
"""
from __future__ import annotations
from collections import Counter
import numpy as np
from .world import World
from .belief import HMMFilter, normalized_entropy, information_gain_if_hit

K = 4


def topk(score: np.ndarray, k: int = K) -> tuple[int, ...]:
    return tuple(int(x) for x in np.argsort(-np.asarray(score), kind="stable")[:k])


class BasePolicy:
    name = "base"
    def __init__(self, world: World, seed: int):
        self.world = world
        self.rng = np.random.default_rng(seed)
        self.last_node = None
        self.nsteps = 0
        self.mode_counts: Counter = Counter()

    def select(self, node: int, alert: int) -> tuple[int, ...]:
        raise NotImplementedError

    def feedback(self, placement: tuple[int, ...], target: int) -> None:
        pass

    def _observed(self, node: int) -> None:
        self.last_node = node
        self.nsteps += 1


class RandomPolicy(BasePolicy):
    name = "random"
    def select(self, node, alert):
        self._observed(node)
        return tuple(int(i) for i in self.rng.choice(self.world.n, K, replace=False))


class StaticPolicy(BasePolicy):
    name = "static"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.fixed = tuple(int(i) for i in self.rng.choice(world.n, K, replace=False))
    def select(self, node, alert):
        self._observed(node)
        return self.fixed


class CentralityPolicy(BasePolicy):
    name = "centrality"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.fixed = topk(world.adjacency.sum(axis=0))
    def select(self, node, alert):
        self._observed(node)
        return self.fixed


class ContextualBanditPolicy(BasePolicy):
    name = "contextual_bandit"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.alpha = np.ones((11, world.n))
        self.beta = np.ones((11, world.n))
        self.context = 0
    def select(self, node, alert):
        self.context = alert  # noisy observation, NOT true attacker state
        sample = self.rng.beta(self.alpha[alert], self.beta[alert])
        score = .70 * sample + .30 * self.world.proximity[node]
        self._observed(node)
        return topk(score)
    def feedback(self, placement, target):
        for p in placement:
            reward = 1.0 if p == target else 0.0
            self.alpha[self.context, p] += reward
            self.beta[self.context, p] += 1 - reward


class DiscountedTSPolicy(BasePolicy):
    name = "discounted_ts"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.alpha = np.ones(world.n)
        self.beta = np.ones(world.n)
    def select(self, node, alert):
        # Forget evidence over time, but never future events.
        self.alpha = 1 + .975 * (self.alpha - 1)
        self.beta = 1 + .975 * (self.beta - 1)
        sample = self.rng.beta(self.alpha, self.beta)
        score = .65 * sample + .35 * self.world.proximity[node]
        self._observed(node)
        return topk(score)
    def feedback(self, placement, target):
        for p in placement:
            reward = float(p == target)
            self.alpha[p] += reward
            self.beta[p] += 1 - reward


class HMMGreedyPolicy(BasePolicy):
    name = "hmm_greedy"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.hmm = HMMFilter(world)
    def select(self, node, alert):
        belief = self.hmm.update(node, alert)
        score = self.world.predict_visits(belief, node) - .012 * self.world.risk
        self._observed(node)
        return topk(score)


class POMDPProxyPolicy(BasePolicy):
    name = "pomdp_proxy"
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.hmm = HMMFilter(world)
    def select(self, node, alert):
        belief = self.hmm.update(node, alert)
        interact = self.world.predict_visits(belief, node)
        info = information_gain_if_hit(self.world, belief)
        score = .70 * (interact / max(interact.max(), 1e-9))
        score += .30 * (info / max(info.max(), 1e-9))
        self._observed(node)
        return topk(score)


class BAAHSInspiredPolicy(BasePolicy):
    name = "baahs_independent"
    MODES = ("interaction", "data_quality", "information_gain", "deception_value", "risk_aware")
    # Explicit, original author-made weights—not sourced from BAAHS paper.
    WEIGHTS = {
        "interaction":      (.55, .10, .10, .20, .05),
        "data_quality":     (.25, .45, .10, .15, .05),
        "information_gain": (.25, .10, .45, .15, .05),
        "deception_value":  (.30, .10, .10, .45, .05),
        "risk_aware":       (.30, .10, .10, .15, .35),
    }
    def __init__(self, world, seed):
        super().__init__(world, seed)
        self.hmm = HMMFilter(world)
        self.alpha = np.ones(world.n)
        self.beta = np.ones(world.n)
        self.prev_belief = np.ones(11) / 11
        self.posterior_decay_strength = 1.8

    def _choose_mode(self, belief, step):
        # Cyclic schedule guarantees all five objectives are studied; illustrative.
        # A real author-equivalent mode controller requires full paper methods.
        return self.MODES[(step // 8) % len(self.MODES)]

    def select(self, node, alert):
        belief = self.hmm.update(node, alert)
        shift = float(np.abs(belief - self.prev_belief).sum() / 2)
        # Evidence decay for nonstationarity. Alpha/Beta always >= 1.
        decay = float(np.exp(-self.posterior_decay_strength * shift))
        self.alpha = 1.0 + (self.alpha - 1.0) * decay
        self.beta = 1.0 + (self.beta - 1.0) * decay
        self.prev_belief = belief.copy()
        mode = self._choose_mode(belief, self.nsteps)
        self.mode_counts[mode] += 1
        w_inter, w_quality, w_info, w_decep, w_risk = self.WEIGHTS[mode]
        next_prob = self.world.predict_visits(belief, node)
        info = information_gain_if_hit(self.world, belief)
        center = self.world.adjacency.sum(axis=0)
        center = center / max(center.max(), 1e-12)
        stage_value = belief @ self.world.state_node
        # Thompson sampling is a stochastic *component*, not an oracle.
        ts_draw = self.rng.beta(self.alpha, self.beta)
        interaction = .60 * (next_prob / next_prob.max()) + .40 * ts_draw
        quality = self.world.quality
        knowledge = info / max(info.max(), 1e-9)
        deception = .70 * (stage_value / max(stage_value.max(), 1e-9)) + .30 * center
        # Higher operational risk is penalized.
        scores = (w_inter * interaction + w_quality * quality +
                  w_info * knowledge + w_decep * deception -
                  w_risk * self.world.risk)
        scores = np.asarray(scores, dtype=float)
        self._observed(node)
        return topk(scores)

    def feedback(self, placement, target):
        # Fractional credit for near misses—a modeling choice, not original code.
        for p in placement:
            if p == target:
                reward = 1.
            elif self.world.adjacency[p, target] > 0:
                reward = .20
            else:
                reward = 0.
            self.alpha[p] += reward
            self.beta[p] += 1 - reward


POLICIES = (
    BAAHSInspiredPolicy, RandomPolicy, StaticPolicy, CentralityPolicy,
    ContextualBanditPolicy, DiscountedTSPolicy, HMMGreedyPolicy,
    POMDPProxyPolicy,
)
