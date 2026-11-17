# -*- coding: utf-8 -*-
"""Tests for the protocol D1.0 environment changes (recorded positions, dataset goals, undefended zones)."""
import unittest
from collections import Counter

import numpy as np

import pipeline as p
import d1_data

env = p.env


def all_runs():
    out = {}
    for f in p.data.folds():
        for split in ("train", "val", "test"):
            for r in p.runs(f, split):
                out[r["id"]] = r
    return out


RUNS = all_runs()
META = env.scenario_metadata()


def spec_of(run_id, seed=0):
    return env.make_spec(RUNS[run_id], np.random.default_rng(seed), META)


class D1Data(unittest.TestCase):
    def test_every_command_has_a_position(self):
        self.assertEqual(len(RUNS), 34)
        c = Counter(z for r in RUNS.values() for z in r["positions"])
        self.assertEqual(sum(c.values()), 904)
        # regression: the numbers reported in checks/MOVEMENT_CHECK.txt and ZONE_GOAL_CHECK.md
        self.assertEqual(dict(c), {"DMZ": 549, "Internet": 132, "User": 118, "LAN": 93, "Firewall": 12})

    def test_goal_reachable_in_every_p1_run(self):
        for rid, r in RUNS.items():
            entry, target, goal, p1 = d1_data.SCENARIOS[r["scenario"]]
            hits = sum(z == target and g for z, g in zip(r["positions"], r["goal"]))
            if p1:
                self.assertGreater(hits, 0, rid)
        self.assertFalse(META["S4"]["p1"])
        self.assertEqual(sum(META[s]["p1"] for s in META), 6)

    def test_positions_follow_the_command_not_the_order(self):
        # execution order permutes S6 commands; positions and goals must move with them
        ex = {r["id"]: r for f in p.ordered_folds("execution")[:1] for s in ("train", "val", "test")
              for r in p.runs(f, s)}
        for rid, r in ex.items():
            a = dict(zip(r["source_rows"], zip(r["positions"], r["goal"])))
            b = dict(zip(RUNS[rid]["source_rows"], zip(RUNS[rid]["positions"], RUNS[rid]["goal"])))
            self.assertEqual(a, b, rid)


class D1Environment(unittest.TestCase):
    def test_attacker_follows_the_recorded_path(self):
        for rid in RUNS:
            s = spec_of(rid)
            e = env.CommandEngagementEnv().reset(s)
            zones = []
            while not e.done:
                _, _, info = e.step([0] * env.N_AGENTS)
                zones.append(env.POSITIONS[info["zone"]])
            self.assertEqual(zones, RUNS[rid]["positions"][:len(zones)], rid)

    def test_undefended_commands_are_never_engaged(self):
        cfg = env.EnvConfig()
        for rid in ("4", "7", "6_screensharing_binary", "1_cron_pam"):
            s = spec_of(rid, 3)
            s.u[env.U_ENGAGE] = 0.0          # any decoy with payoff > 0 would engage
            s.u[env.U_BURN] = 1.0
            e = env.CommandEngagementEnv(cfg).reset(s)
            und = 0
            while not e.done:
                _, _, info = e.step([1, 2, 0, 0])
                if env.POSITIONS[info["zone"]] in ("Internet", "Firewall"):
                    und += 1
                    self.assertFalse(info["engaged"])
            self.assertEqual(e.episode_stats()["undefended_commands"], und)

    def test_null_policy_reaches_the_first_goal_command(self):
        for rid, r in RUNS.items():
            s = spec_of(rid)
            e = env.CommandEngagementEnv().reset(s)
            while not e.done:
                e.step([0] * env.N_AGENTS)
            target = d1_data.SCENARIOS[r["scenario"]][1]
            first = next(t for t, (z, g) in enumerate(zip(r["positions"], r["goal"])) if z == target and g)
            st = e.episode_stats()
            self.assertEqual(st["objective_at"], first, rid)
            self.assertEqual(st["protected"], 0.0)

    def test_lure_redirects_one_command_then_replay_resumes(self):
        lure = env.LURES[0]
        for rid in ("3_ssh_apt", "1_cron_pam", "6_macro_cron"):
            s = spec_of(rid, 5)
            r = RUNS[rid]
            pos = [env.POS_ID[z] for z in r["positions"]]
            cand = [t for t in range(len(pos) - 2)
                    if pos[t] in env.ZONE_AGENT and env.command_payoff(s.commands[t], lure, "max") > 0
                    and not s.goal_cmd[t] and not s.goal_cmd[t + 1]]
            if not cand:
                continue
            t0 = cand[0]
            s.u[env.U_ENGAGE] = 0.0
            s.u[env.U_BURN] = 1.0
            s.u[env.U_DEAD] = 1.0
            s.u[env.U_WIRE] = 0.0
            e = env.CommandEngagementEnv().reset(s)
            for _ in range(t0):
                e.step([0] * env.N_AGENTS)
            if e.done:
                continue
            ag = env.ZONE_AGENT[pos[t0]]
            partner = next(j for j in range(env.N_AGENTS) if j != ag)
            acts = [0] * env.N_AGENTS
            acts[ag], acts[partner] = lure, 1
            _, _, info = e.step(acts)
            self.assertTrue(info["engaged"], rid)
            self.assertEqual(info["wired"], env.AGENT_ZONE[partner])
            _, _, info2 = e.step([0] * env.N_AGENTS)
            self.assertEqual(info2["zone"], env.AGENT_ZONE[partner])   # redirected command
            self.assertTrue(info2["followed"])
            if not e.done:
                _, _, info3 = e.step([0] * env.N_AGENTS)
                self.assertEqual(info3["zone"], pos[t0 + 2])           # back on the recorded path
            return
        self.fail("no run offered a lure test point")

    def test_sensitivity_models_still_run(self):
        hand = env.scenario_metadata("hand")
        for rid in ("1_cron_pam", "3_vnc_apt", "6_plugin"):
            s = env.make_spec(RUNS[rid], np.random.default_rng(1), hand)
            for cfg in (env.EnvConfig(movement="random_walk"), env.EnvConfig()):
                e = env.CommandEngagementEnv(cfg).reset(s)
                while not e.done:
                    e.step([0] * env.N_AGENTS)
                self.assertLessEqual(e.t, s.horizon)
        with self.assertRaises(ValueError):
            env.EnvConfig(movement="teleport")

    def test_state_shapes(self):
        e = env.CommandEngagementEnv().reset(spec_of("4"))
        self.assertEqual(e.global_state().shape, (env.GLOBAL_DIM,))
        self.assertEqual(e.local_obs().shape, (env.N_AGENTS, env.LOCAL_DIM))
        while not e.done:
            e.step([1] * env.N_AGENTS)
            self.assertEqual(e.global_state().shape, (env.GLOBAL_DIM,))



class D1Gate(unittest.TestCase):
    def test_planner_never_sees_the_scored_run(self):
        import gate_d1 as G
        runs = G.all_runs()
        target = runs[0]
        others = [r for r in runs if r["id"] != target["id"]]
        pl = G.TransitionPlanner(others, env.EnvConfig())
        n_trans = sum(len(r["commands"]) - 1 for r in others)
        self.assertEqual(sum(sum(c.values()) for c in pl.next.values()), n_trans)

    def test_gate_randomness_is_disjoint_from_validation_and_test(self):
        import gate_d1 as G
        self.assertNotIn(G.GATE_SEED, {100000 + s for s in range(10)} | {200000 + s for s in range(10)})

    def test_gate_smoke_runs(self):
        import itertools
        import gate_d1 as G
        runs = G.all_runs()
        res = G.run_gate(runs[:2] + runs[-1:], env.EnvConfig(), repeats=1,
                         joints=list(itertools.product((0, 1), repeat=env.N_AGENTS))[:4])
        self.assertEqual(set(res["gates"]), {"G1", "G2", "G3"})
        self.assertEqual(res["n_runs"]["E1"], 3)


if __name__ == "__main__":
    unittest.main()
