# -*- coding: utf-8 -*-
"""Tests for the protocol D1.0 environment changes (recorded positions, dataset goals, undefended zones)."""
import sys
import unittest
from collections import Counter
from pathlib import Path

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



class D1RunnerAndEvaluation(unittest.TestCase):
    def test_spec_refuses_until_frozen(self):
        import spec_d1
        if not spec_d1.SPEC.exists():
            with self.assertRaises(SystemExit):
                spec_d1.require()
        else:
            self.assertTrue(spec_d1.check())

    def test_statistics_follow_the_casinolimit_rules(self):
        import evaluate_d1 as E
        rng = np.random.default_rng(0)
        runs = [f"r{i}" for i in range(29)]
        a = {r: 5 + rng.normal() for r in runs}
        b = {r: a[r] - 1.0 + 0.1 * rng.normal() for r in runs}
        fam = E.family({("allpos", "E1"): a, ("NoHistory", "E1"): b, ("allpos", "P1"): a, ("NoHistory", "P1"): a},
                       [("allpos", "NoHistory", "E1"), ("allpos", "NoHistory", "P1")])
        self.assertEqual(fam[0]["verdict"], "history agents (allpos) outperforms agents without history")
        self.assertEqual(fam[1]["verdict"], "no difference shown")       # identical values: p is None
        self.assertEqual(E.holm([0.01, 0.04]), [0.02, 0.04])

    def test_per_run_averages_repeats_then_seeds_and_skips_p1_runs(self):
        import evaluate_d1 as E
        rows = {0: [{"run": "x", "dwell": 2, "protected": 1, "p1": 1.0}, {"run": "x", "dwell": 4, "protected": 0, "p1": 1.0},
                    {"run": "4", "dwell": 1, "protected": 0, "p1": 0.0}],
                1: [{"run": "x", "dwell": 6, "protected": 1, "p1": 1.0}, {"run": "4", "dwell": 3, "protected": 0, "p1": 0.0}]}
        pr = E.per_run(rows)
        self.assertEqual(pr["E1"], {"x": 4.5, "4": 2.0})
        self.assertEqual(pr["P1"], {"x": 0.75})

    def test_runner_smoke_seals_nothing_and_needs_no_checkpoint(self):
        import subprocess, sys, tempfile, json, pathlib
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "main"
            r = subprocess.run([sys.executable, "-W", "ignore", str(pathlib.Path(__file__).with_name("run_d1.py")),
                                "--smoke", "--output", str(out)], capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            res = list((pathlib.Path(tmp) / "smoke").rglob("result.json"))
            self.assertEqual(len(res), 1)
            d = json.loads(res[0].read_text(encoding="utf-8"))
            self.assertIsNone(d["sealed_test_sha256"])
            self.assertNotIn("test", d)
            self.assertNotIn("test_summary", d)
            self.assertEqual(d["order"], "frozen")
            self.assertEqual(d["env_config"]["movement"], "recorded")
            self.assertEqual(d["env_config"]["reward"], "proposal")          # D6



class D1Sensitivity(unittest.TestCase):
    def test_efficacy_scales_every_engagement_probability(self):
        s = spec_of("3_ssh_apt", 2)
        s.u[env.U_ENGAGE] = 1.0                  # never engage, so both runs follow the same path
        rhos = {}
        for eff in (1.0, 0.5):
            e = env.CommandEngagementEnv(env.EnvConfig(efficacy=eff)).reset(s)
            rhos[eff] = []
            while not e.done:
                _, _, info = e.step([1, 2, 3, 4])
                rhos[eff].append(info["rho"])
        np.testing.assert_allclose(np.array(rhos[0.5]), 0.5 * np.array(rhos[1.0]))
        self.assertGreater(max(rhos[1.0]), 0)
        with self.assertRaises(ValueError):
            env.EnvConfig(efficacy=0.0)

    def test_hand_goals_count_only_runs_with_goal_commands(self):
        hand = env.scenario_metadata("hand")
        p1 = {rid: env.make_spec(r, np.random.default_rng(0), hand).p1 for rid, r in RUNS.items()}
        self.assertFalse(p1["6_plugin"])          # S6 'Exfiltration': no goal command (the 8 runs)
        self.assertFalse(p1["1_sudo_pam"])
        self.assertEqual(sum(not v for v in p1.values()), 8)
        d1 = {rid: spec_of(rid).p1 for rid in RUNS}
        self.assertEqual([rid for rid, v in d1.items() if not v], ["4"])

    def test_runner_smoke_for_three_sensitivities(self):
        import subprocess, sys, tempfile, json, pathlib
        for name in ("random_walk", "execution", "reward_engagement"):
            with tempfile.TemporaryDirectory() as tmp:
                out = pathlib.Path(tmp) / name
                r = subprocess.run([sys.executable, "-W", "ignore",
                                    str(pathlib.Path(__file__).with_name("run_d1.py")),
                                    "--smoke", "--sensitivity", name, "--output", str(out)],
                                   capture_output=True, text=True, timeout=600)
                self.assertEqual(r.returncode, 0, r.stderr[-2000:])
                d = json.loads(next((pathlib.Path(tmp) / "smoke").rglob("result.json")).read_text(encoding="utf-8"))
                self.assertEqual(d["setting"], name)
                if name == "random_walk":
                    self.assertEqual(d["env_config"]["movement"], "random_walk")
                    self.assertEqual(d["env_config"]["goals"], "hand")
                elif name == "execution":
                    self.assertEqual(d["order"], "execution")
                else:
                    self.assertEqual(d["env_config"]["movement"], "recorded")
                    self.assertEqual(d["order"], "frozen")
                expected = "engagement" if name == "reward_engagement" else "proposal"
                self.assertEqual(d["env_config"]["reward"], expected, name)



class D1Reward(unittest.TestCase):
    def test_proposal_reward_adds_depth_bonus_and_exposure_penalty(self):
        base = spec_of("3_ssh_apt", 4)
        for burn in (1.0, 0.0):                       # 1.0: never exposed; 0.0: exposed when engaged (rho < 1)
            s = spec_of("3_ssh_apt", 4)
            s.u[env.U_ENGAGE] = 0.0
            s.u[env.U_BURN] = burn
            s.u[env.U_DEAD] = 1.0
            got = {}
            for rw in ("engagement", "proposal"):
                e = env.CommandEngagementEnv(env.EnvConfig(reward=rw)).reset(s)
                seen, rows = set(), []
                while not e.done:
                    r, _, info = e.step([1, 2, 3, 4])
                    new = info["engaged"] and bool(set(info["labels"]) - seen)
                    if info["engaged"]:
                        seen |= set(info["labels"])
                    rows.append((r, info["engaged"], new, info["exposed"]))
                got[rw] = rows
            self.assertEqual(len(got["engagement"]), len(got["proposal"]))
            for (re_, eng, new, exp), (rp, _, _, _) in zip(got["engagement"], got["proposal"]):
                self.assertEqual(re_, 1.0 if eng else 0.0)
                self.assertAlmostEqual(rp, re_ + 1.0 * new - 5.0 * exp)
        with self.assertRaises(ValueError):
            env.EnvConfig(reward="other")



class D1Decisions(unittest.TestCase):
    """Decisions D4, D6 and D7 (2026-11-17) as the runner and the scorer implement them."""

    def test_primary_reward_is_proposal_and_each_sensitivity_changes_only_what_it_names(self):
        import run_d1 as R
        prim, order = R.setting(None)
        self.assertEqual((prim.reward, order), ("proposal", "frozen"))
        self.assertEqual((prim.depth_bonus, prim.exposure_penalty), (1.0, 5.0))
        base = prim.to_dict()
        self.assertEqual(len(R.SENSITIVITIES), 6)
        for name, (kw, o) in R.SENSITIVITIES.items():
            cfg, got = R.setting(name)
            self.assertEqual(got, o, name)
            changed = {k for k, v in cfg.to_dict().items() if base[k] != v}
            self.assertEqual(changed, set(kw), name)
        self.assertEqual(R.setting("reward_engagement")[0].reward, "engagement")
        self.assertEqual(R.setting("execution"), (prim, "execution"))

    def test_reward_changes_no_outcome_of_a_fixed_policy(self):
        # D6: the reward only trains the agents. The environment, and every outcome of a policy that
        # does not learn, is identical under both rewards.
        import gate_d1 as G
        B = G.B
        specs = [spec_of(rid, k) for k, rid in enumerate(("1_cron_pam", "3_vnc_apt", "6_macro_cron", "4"))]
        makers = (lambda c: B.ReactivePolicy(c), lambda c: B.FixedJointPolicy((1, 2, 3, 4)),
                  lambda c: B.RandomPolicy(7), lambda c: B.ClairvoyantCoordPolicy(c))
        for make in makers:
            stats = {}
            for rw in ("engagement", "proposal"):
                cfg = env.EnvConfig(reward=rw)
                e = env.CommandEngagementEnv(cfg)
                stats[rw] = [env.run_episode(e, s, make(cfg)) for s in specs]
            self.assertEqual(stats["engagement"], stats["proposal"])

    def test_main_arms_families_and_cell_counts(self):
        import run_d1 as R
        import evaluate_d1 as E
        self.assertEqual(R.PRIMARY_ARMS, ("allpos", "NoHistory"))
        self.assertEqual(R.MAIN_ARMS, ("allpos", "NoHistory", "lstm_allpos"))
        self.assertEqual((E.PRIMARY_ARMS, E.MAIN_ARMS), (R.PRIMARY_ARMS, R.MAIN_ARMS))
        fam = E.family_pairs()
        self.assertEqual({k: len(v) for k, v in fam.items()}, {"family_1": 2, "family_2": 12, "family_3": 2})
        self.assertEqual({r for _, r, _ in fam["family_2"]},
                         {"none", "random", "static", "fixed", "greedy", "planner"})
        self.assertEqual(fam["family_3"], [("allpos", "lstm_allpos", "E1"), ("allpos", "lstm_allpos", "P1")])
        folds = p.ordered_folds("frozen")
        self.assertEqual((E.MAIN_CELLS, E.SENSITIVITY_CELLS), (R.MAIN_CELLS, R.SENSITIVITY_CELLS))
        self.assertEqual([n for n, _ in R.PHASES], ["primary (Family 1)", "Family 3", "descriptive (Q4)"])
        self.assertEqual(R.PHASES[0][1], (("allpos", "MAPPO"), ("NoHistory", "MAPPO")))   # D5: run first
        self.assertEqual(R.PHASES[1][1], (("lstm_allpos", "MAPPO"),))
        self.assertEqual(set(R.PHASES[2][1]), {("gru_allpos", "MAPPO"), ("baseline", "MAPPO"),
                                               ("allpos", "IPPO"), ("NoHistory", "IPPO")})       # D8
        self.assertEqual(len(E.cells(Path("x"), folds, range(10), R.MAIN_CELLS)), 2240)
        self.assertEqual(len(E.cells(Path("x"), folds, range(10), R.PHASES[0][1])), 640)
        self.assertEqual(len(E.cells(Path("x"), folds, range(5), R.SENSITIVITY_CELLS)), 320)

    def test_q4_is_described_never_tested(self):
        import evaluate_d1 as E
        rng = np.random.default_rng(3)
        runs = [f"r{i}" for i in range(29)]
        names = {E.unit_name(a, lr) for a, lr in E.MAIN_CELLS}
        self.assertEqual(names, {"allpos", "NoHistory", "lstm_allpos", "gru_allpos", "baseline",
                                 "allpos_IPPO", "NoHistory_IPPO"})
        values = {(n, m): {r: float(rng.normal()) for r in runs} for n in names for m in E.OUTCOMES}
        rows = E.describe(values)
        self.assertEqual(len(rows), 10)
        for c in rows:
            self.assertNotIn("p", c)
            self.assertNotIn("p_holm", c)
            self.assertNotIn("verdict", c)
            self.assertIn(c["a"], names)
            self.assertIn(c["b"], names)

    def test_every_encoder_gives_the_agents_a_history(self):
        # all four history encoders of the main run produce the 64-dim h; row 0 (no history) is zero
        import torch
        s = spec_of("1_cron_pam")
        for arm, n_params in (("allpos", 77713), ("baseline", 77713), ("gru_allpos", 77920),
                              ("lstm_allpos", 77793)):
            torch.manual_seed(0)
            m = p.variants.build_variant(arm, p.data.W)
            self.assertEqual(sum(x.numel() for x in m.parameters()), n_params, arm)
            tab = p.marl.HistoryBank(m, p.data.W).table(s)
            self.assertEqual(tab.shape, (s.horizon + 1, p.marl.H_DIM), arm)
            self.assertTrue(np.isfinite(tab).all(), arm)
            self.assertFalse(tab[0].any(), arm)
            self.assertTrue(tab[1:].any(), arm)

    def test_runner_smoke_with_ippo(self):
        import subprocess, json, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "main"
            r = subprocess.run([sys.executable, "-W", "ignore", str(Path(__file__).with_name("run_d1.py")),
                                "--smoke", "--learners", "IPPO", "--output", str(out)],
                               capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            d = json.loads(next((Path(tmp) / "smoke").rglob("result.json")).read_text(encoding="utf-8"))
            self.assertEqual((d["arm"], d["learner"]), ("NoHistory", "IPPO"))
            self.assertIsNone(d["sealed_test_sha256"])

    def test_static_and_fixed_are_fitted_on_training_runs_only(self):
        import evaluate_d1 as E
        import gate_d1 as G
        import run_d1 as R

        class Spy:                      # stands in for pipeline and records every split it is asked for
            def __init__(self):
                self.splits = []

            def runs(self, fold, split):
                self.splits.append(split)
                return p.runs(fold, split)

        spy = Spy()
        fold = p.ordered_folds("frozen")[0]
        joints = [(0, 0, 0, 0), (1, 2, 0, 0), (3, 3, 3, 3)]
        ch = E.fit_static_fixed(fold, env, spy, G, R, R.setting(None)[0], joints=joints)
        self.assertEqual(set(spy.splits), {"train"})
        for m in E.OUTCOMES:
            self.assertIn(ch["static"][m], range(1, env.N_ACTIONS))
            self.assertIn(tuple(ch["fixed"][m]), joints)

    def test_reference_policies_are_scored_on_the_arms_episodes(self):
        # same runs, seed rule, repeats and setting as run_d1.run_cell's test episodes (paired comparison).
        # Seed 777 is outside the protocol's seeds 0-9, so no protocol test episode is built here.
        import evaluate_d1 as E
        import gate_d1 as G
        import run_d1 as R
        fold = p.ordered_folds("frozen")[0]
        cfg = R.setting(None)[0]
        chosen = {"static": {"E1": 1, "P1": 2}, "fixed": {"E1": [1, 2, 0, 0], "P1": [0, 0, 3, 4]}}
        rr = E.reference_rows(fold, 777, 2, env, p, G, R, cfg, chosen)
        self.assertEqual(set(rr), set(E.SIMPLE) | {f"{n}_{m}" for n in E.FITTED for m in E.OUTCOMES})
        specs = R.specs(p.runs(fold, "test"), R.TEST_SEED + 777, 2, cfg)
        e = env.CommandEngagementEnv(cfg)
        self.assertEqual(rr["none"], [env.run_episode(e, s, G.B.NullPolicy()) for s in specs])
        self.assertEqual(rr["static_P1"], [env.run_episode(e, s, G.B.StaticPolicy(2)) for s in specs])
        self.assertEqual(rr["fixed_P1"], [env.run_episode(e, s, G.B.FixedJointPolicy([0, 0, 3, 4])) for s in specs])
        self.assertEqual({r["run"] for r in rr["none"]}, set(fold["test_runs"]))

    def test_order_check_reproduces_its_report(self):
        # D4: checks/ORDER_CHECK.txt is what checks/order_check.py computes from the pinned data
        sys.path.insert(0, str(Path(__file__).resolve().parent / "checks"))
        import order_check
        text = (Path(__file__).resolve().parent / "checks" / "ORDER_CHECK.txt").read_text(encoding="utf-8")
        self.assertEqual(order_check.report(), text)
        self.assertIn("runs whose order differs: 4", text)


if __name__ == "__main__":
    unittest.main()
