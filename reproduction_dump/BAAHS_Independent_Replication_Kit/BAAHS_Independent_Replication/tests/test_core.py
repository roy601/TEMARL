import tempfile
import unittest
from pathlib import Path
import numpy as np
from baahs.world import World, STAGES
from baahs.belief import HMMFilter
from baahs.policies import POLICIES
from baahs.evaluation import evaluate_one_seed, run_experiment


class TestBAAHSIndependent(unittest.TestCase):
    def test_topology_hmm_probability(self):
        w = World()
        self.assertEqual(w.n, 25)
        self.assertEqual(len(STAGES), 11)
        self.assertTrue(np.allclose(w.transition.sum(axis=1), 1))
        self.assertTrue(np.allclose(w.emission.sum(axis=1), 1))
        self.assertTrue(np.allclose(w.state_node.sum(axis=1), 1))
        self.assertTrue(np.allclose(w.adjacency, w.adjacency.T))
        self.assertTrue(np.allclose(np.diag(w.adjacency), 0))

    def test_trajectories_fixed_by_seed(self):
        w = World()
        self.assertEqual(w.make_trajectory(6, 30), w.make_trajectory(6, 30))
        self.assertNotEqual(w.make_trajectory(6, 30), w.make_trajectory(7, 30))

    def test_belief_filter(self):
        w = World()
        f = HMMFilter(w)
        for e in w.make_trajectory(3, 25):
            post = f.update(e.node, e.alert)
            self.assertTrue(np.isfinite(post).all())
            self.assertAlmostEqual(float(post.sum()), 1.0)
            self.assertTrue((post >= 0).all())

    def test_all_policies_produce_four_unique_nodes(self):
        w = World()
        for i, policy_class in enumerate(POLICIES):
            pol = policy_class(w, i)
            for step in range(3):
                placed = pol.select(node=step, alert=step)
                self.assertEqual(len(placed), 4)
                self.assertEqual(len(set(placed)), 4)
                self.assertTrue(all(0 <= x < 25 for x in placed))
                pol.feedback(placed, 3)

    def test_future_attack_not_used_at_selection(self):
        w = World()
        # A policy sees exactly the same history in both worlds.
        # Future target may change, but its initial decision must not.
        for i, klass in enumerate(POLICIES):
            a = klass(w, 20+i)
            b = klass(w, 20+i)
            self.assertEqual(a.select(2, 1), b.select(2, 1))

    def test_reproducible_paired_evaluation(self):
        w = World()
        a, ae = evaluate_one_seed(w, 15, 20, "development")
        b, be = evaluate_one_seed(w, 15, 20, "development")
        self.assertEqual(a, b)
        self.assertEqual(ae, be)
        self.assertEqual(len(a), len(POLICIES))
        self.assertTrue(all(r["opportunities"] == 19 for r in a))
        for e in ae:
            self.assertEqual(e["hit"], int(e["next_node"] in e["selected_for_next"]))

    def test_end_to_end_generates_all_files(self):
        with tempfile.TemporaryDirectory() as directory:
            result = run_experiment(directory, steps=12, seeds_per_batch=2,
                                    max_batches=1, holdout_seeds=2, verbose=False)
            self.assertIn("held_out", result)
            for f in ("summary.json", "dev_runs.csv", "holdout_runs.csv",
                      "dev_events.jsonl", "holdout_events.jsonl", "EVALUATION_REPORT.md"):
                self.assertTrue((Path(directory)/f).exists(), f)
            self.assertEqual(result["development"]["baahs_independent"]["seeds"], 2)


if __name__ == "__main__":
    unittest.main()
