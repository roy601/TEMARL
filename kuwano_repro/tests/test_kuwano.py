"""Phase 3 tests. Toy cases are computed by hand in the comments; real-data tests check
invariants that must hold for every setting of the open decisions.

    python -m unittest discover -s tests -v
"""
import itertools
import os
import sys
import unittest
from fractions import Fraction as F

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import kuwano as kw  # noqa: E402

EXE, PER, DEF = (kw.TACTIC_ORDER.index(x) for x in ("execution", "persistence", "defense-evasion"))


def toy():
    # A = {t1,t2}, B = {t1,t3}, C = {t3}.  Names sort B < A < C; ids sort A < B < C.
    groups = {"A": frozenset({"t1", "t2"}), "B": frozenset({"t1", "t3"}), "C": frozenset({"t3"})}
    names = {"A": "beta", "B": "alpha", "C": "gamma"}
    rank = {"name": {g: i for i, g in enumerate(sorted(groups, key=lambda g: names[g]))},
            "id": {g: i for i, g in enumerate(sorted(groups))},
            "stix": {"C": 0, "A": 1, "B": 2}}
    tactics = {"t1": (EXE,), "t2": (PER,), "t3": (EXE, DEF)}
    return kw.Data(("t1", "t2", "t3"), tactics, groups, rank)


class Similarity(unittest.TestCase):
    def test_sdc(self):
        a, b = frozenset({"x", "y"}), frozenset({"y", "z", "w"})
        self.assertEqual(kw.sdc(a, b), F(2, 5))           # 2*1 / (2+3)
        self.assertEqual(kw.sdc(a, frozenset()), 0)
        self.assertEqual(kw.sdc(a, a), 1)
        self.assertEqual(kw.sdc(frozenset(), frozenset()), 0)


class Algorithm1(unittest.TestCase):
    # observed {t1}: SDC A = 2/3, B = 2/3, C = 0; weight 1/(1-2/3) = 3
    def test_k2_support(self):
        sup, _ = kw.recommend({"t1"}, toy(), k=2, threshold=F(3, 2))
        self.assertEqual(sup, {"t1": F(3), "t2": F(3, 2), "t3": F(3, 2)})   # (3+3)/2, 3/2, 3/2

    def test_threshold_inclusive_vs_strict(self):
        _, ge = kw.recommend({"t1"}, toy(), k=2, threshold=F(3, 2), inclusive=True)
        _, gt = kw.recommend({"t1"}, toy(), k=2, threshold=F(3, 2), inclusive=False)
        self.assertEqual(ge, {"t1", "t2", "t3"})
        self.assertEqual(gt, {"t1"})

    def test_zero_similarity_neighbour_adds_nothing_but_counts_in_k(self):
        sup, _ = kw.recommend({"t1"}, toy(), k=3, threshold=F(1))
        self.assertEqual(sup, {"t1": F(2), "t2": F(1), "t3": F(1)})          # divided by k = 3; C adds 0

    def test_tiebreak_decides_who_is_kept(self):
        # k = 1, A and B tie at 2/3. name: B first -> t3 gets 3; id: A first -> t2 gets 3
        by_name, _ = kw.recommend({"t1"}, toy(), k=1, tiebreak="name")
        by_id, _ = kw.recommend({"t1"}, toy(), k=1, tiebreak="id")
        self.assertEqual((by_name["t2"], by_name["t3"]), (0, 3))
        self.assertEqual((by_id["t2"], by_id["t3"]), (3, 0))

    def test_similarity_one_raises(self):
        d = toy()
        d.groups["D"] = frozenset({"t2"})
        for r in d.rank.values():
            r["D"] = 9
        with self.assertRaises(ZeroDivisionError):
            kw.recommend({"t2"}, d, k=4)

    def test_limit_rule_for_similarity_one(self):
        # D = {t2} is identical to the observed {t2}. Hand computation, k = 4, top = D, A, B, C:
        #   D: SDC 1 -> infinite weight on t2 (n = 1)
        #   A = {t1,t2}: SDC 2*1/3 = 2/3 -> weight 3 on t1 and t2
        #   B = {t1,t3}: SDC 0;  C = {t3}: SDC 0
        # so t1 = (0, 3/4), t2 = (1, 3/4), t3 = (0, 0)
        d = toy()
        d.groups["D"] = frozenset({"t2"})
        for r in d.rank.values():
            r["D"] = 9
        scores, rec = kw.recommend_limit({"t2"}, d, k=4, threshold=F(1))
        self.assertEqual(scores, {"t1": (0, F(3, 4)), "t2": (1, F(3, 4)), "t3": (0, F(0))})
        self.assertEqual(rec, {"t2"})                      # n > 0 wins; 3/4 < 1 for the rest
        ranked = sorted(scores, key=lambda t: scores[t], reverse=True)
        self.assertEqual(ranked[0], "t2")
        with self.assertRaises(ZeroDivisionError):         # the validated path is unchanged
            kw.recommend({"t2"}, d, k=4)

    def test_limit_rule_equals_validated_path_without_similarity_one(self):
        d = toy()
        # none of these equals a toy group's set ({"t3"} would: it is group C)
        for obs, k in (({"t1"}, 1), ({"t1"}, 2), ({"t1"}, 3), ({"t2"}, 2), ({"t1", "t2", "t3"}, 3)):
            sup, rec = kw.recommend(obs, d, k=k, threshold=F(3, 2))
            lim, rec_l = kw.recommend_limit(obs, d, k=k, threshold=F(3, 2))
            self.assertEqual({t: (0, r) for t, r in sup.items()}, lim)
            self.assertEqual(rec, rec_l)

    def test_observed_technique_can_be_recommended(self):
        # Algorithm 1 itself does not drop inputs; evaluate() does, through candidates().
        _, rec = kw.recommend({"t1"}, toy(), k=2, threshold=F(1))
        self.assertIn("t1", rec)


class Universe(unittest.TestCase):
    def test_rules(self):
        d = toy()
        # observe t2 (persistence): t1 is execution only; t3 is execution + defense evasion
        c = lambda u: kw.candidates(["t2"], ["persistence"], d, universe=u, observed_tactic="listed")
        self.assertEqual(c("any_ge"), {"t3"})       # max(t3) = defense evasion >= persistence
        self.assertEqual(c("all_ge"), set())        # min(t3) = execution < persistence
        self.assertEqual(c("everything"), {"t1", "t3"})

    def test_observed_tactic(self):
        d = toy()
        # observe t3 listed under execution: latest = execution (listed/min) or defense evasion (max)
        c = lambda how: kw.candidates(["t3"], ["execution"], d, universe="any_ge", observed_tactic=how)
        self.assertEqual(c("listed"), {"t1", "t2"})
        self.assertEqual(c("max"), set())


class RealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = kw.load()
        cls.s = kw.load_sequences()

    def test_shapes(self):
        self.assertEqual(len(self.d.techniques), 191)
        self.assertEqual(len(self.d.groups), 131)
        self.assertEqual({a: len(v["sequence"]) for a, v in self.s.items()},
                         {"AA22-277A": 26, "AA22-138B": 12, "AA22-174A": 13})

    def test_universe_row1_277A(self):
        # Table 5 row 1: TP+FP+TN+FN = 173 = 191 - 17 pre-access - 1 input
        v = self.s["AA22-277A"]
        c = kw.candidates(v["sequence"][:1], v["listed_tactic"][:1], self.d,
                          universe="any_ge", observed_tactic="listed")
        self.assertEqual(len(c), 173)

    def test_invariants_every_setting(self):
        for tb, inc, uni, ot in itertools.product(kw.TIEBREAKS, (True, False), kw.UNIVERSES, kw.OBSERVED_TACTICS):
            for adv, v in self.s.items():
                n = len(v["sequence"])
                rows = kw.evaluate(v["sequence"], v["listed_tactic"], self.d, tiebreak=tb, inclusive=inc,
                                   universe=uni, observed_tactic=ot)
                self.assertEqual(len(rows), n - 1)
                for r in rows:
                    self.assertEqual(r["prediction"], r["tp"] + r["fp"])
                    self.assertEqual(r["tp"] + r["fn"], n - r["input"])
                    self.assertGreaterEqual(min(r.values()), 0)

    def test_limit_rule_equals_validated_path_on_paper_data(self):
        # Similarity 1 never occurs on the paper's test sequences, so both paths must agree exactly.
        for v in self.s.values():
            seq = v["sequence"]
            for i in range(1, len(seq)):
                sup, rec = kw.recommend(seq[:i], self.d)
                lim, rec_l = kw.recommend_limit(seq[:i], self.d)
                self.assertEqual({t: (0, r) for t, r in sup.items()}, lim)
                self.assertEqual(rec, rec_l)

    def test_deterministic(self):
        v = self.s["AA22-138B"]
        a = kw.evaluate(v["sequence"], v["listed_tactic"], self.d)
        b = kw.evaluate(v["sequence"], v["listed_tactic"], self.d)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
