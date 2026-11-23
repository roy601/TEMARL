"""Online HMM filter with no hidden-state access."""
import numpy as np
from .world import World, STAGES


class HMMFilter:
    def __init__(self, world: World):
        self.world = world
        self.belief = np.ones(len(STAGES), dtype=float) / len(STAGES)

    def update(self, node: int, alert: int) -> np.ndarray:
        """P(s_t | alerts<=t, visited_nodes<=t), using only observed evidence."""
        prior = self.belief @ self.world.transition
        emission = self.world.emission[:, alert]
        # Node likelihood uses synthetic role-stage affinities.
        node_likelihood = self.world.state_node[:, node]
        unnormalized = prior * emission * np.maximum(node_likelihood, 1e-6)
        if unnormalized.sum() < 1e-100:
            unnormalized = prior * emission + 1e-12
        self.belief = unnormalized / unnormalized.sum()
        return self.belief.copy()


def normalized_entropy(belief: np.ndarray) -> float:
    p = np.clip(belief, 1e-12, 1)
    return float(-(p * np.log(p)).sum() / np.log(len(p)))


def information_gain_if_hit(world: World, belief: np.ndarray) -> np.ndarray:
    """One-step binary hit/miss information gain for each node (approximation)."""
    future = belief @ world.transition
    probs = .60 * world.state_node + .30 * world.proximity.mean(axis=0)[None, :] + .10 / world.n
    probs /= np.maximum(probs.sum(axis=1, keepdims=True), 1e-12)
    marginal = future @ probs
    def h_binary(p):
        p = np.clip(p, 1e-9, 1-1e-9)
        return -p*np.log(p) - (1-p)*np.log(1-p)
    return np.maximum(0.0, h_binary(marginal) - future @ h_binary(probs))
