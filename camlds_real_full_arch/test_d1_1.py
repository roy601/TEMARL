# -*- coding: utf-8 -*-
"""Tests for protocol D1.1 (hyperparameter sensitivity): grid, HP plumbing, equivalence with a D1.0
cell, nested selection, scoring, the single opening, the spec and the stage driver."""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pipeline as p  # noqa: E402
import run_d1 as R  # noqa: E402
import run_d1_1 as T  # noqa: E402
import evaluate_d1_1 as V  # noqa: E402
import spec_d1_1 as S  # noqa: E402

marl = p.marl
FOLDS = p.ordered_folds("frozen")
TINY = {"n_envs": 2, "rollout_len": 4, "n_evals": 1}


class tiny_hp:
    """Small rollouts for fast cells; the swept settings are left to the grid. Restores HP after."""
    def __enter__(self):
        self.old = dict(marl.HP)
        marl.HP.update(TINY)

    def __exit__(self, *exc):
        marl.HP.clear()
        marl.HP.update(self.old)


def args(**kw):
    return argparse.Namespace(**{"eval_repeats": 1, "encoder_root": str(HERE / "no_encoders"), "device": "cpu",
                                 "env_steps": 8, "verbose": False, "sensitivity": None, **kw})


class D11Grid(unittest.TestCase):
    def test_grid_is_a_subset_of_the_mappo_authors_sweep_centred_on_d10(self):
        self.assertEqual(len(T.GRID), 9)
        self.assertEqual(T.DEFAULT, {"lr": 5e-4, "ppo_epochs": 10})
        self.assertEqual({k: marl.HP[k] for k in T.DEFAULT}, T.DEFAULT)          # D1.0 setting
        self.assertIn(T.DEFAULT_NAME, T.GRID)
        for c in T.GRID.values():
            self.assertEqual(set(c), {"lr", "ppo_epochs"})                       # nothing else is swept
            self.assertIn(c["lr"], (1e-4, 5e-4, 7e-4, 1e-3))                     # Yu et al. 2022, Table 13
            self.assertIn(c["ppo_epochs"], (5, 10, 15))
        keys = [(c["lr"], c["ppo_epochs"]) for c in T.GRID.values()]
        self.assertEqual(keys, sorted(keys))                                     # grid (tie-break) order
        self.assertEqual(T.SEEDS, (0, 1, 2))
        self.assertEqual(T.ARMS, ("allpos", "NoHistory"))
        self.assertEqual(len(T.GRID) * len(T.ARMS) * len(FOLDS) * len(T.SEEDS), 1728)

    def test_hp_sets_only_the_swept_settings_and_restores_them(self):
        before = dict(marl.HP)
        with T.hp("lr1e-03_ep15") as used:
            self.assertEqual((marl.HP["lr"], marl.HP["ppo_epochs"]), (1e-3, 15))
            self.assertEqual({k: v for k, v in used.items() if k not in ("lr", "ppo_epochs")},
                             {k: v for k, v in before.items() if k not in ("lr", "ppo_epochs")})
        self.assertEqual(marl.HP, before)
        with self.assertRaises(ZeroDivisionError):
            with T.hp("lr1e-04_ep05"):
                1 / 0
        self.assertEqual(marl.HP, before)                                        # restored on an exception

    def test_the_setting_reaches_the_optimiser_and_the_ppo_loop(self):
        seen, calls = [], []
        orig_adam, orig_loss = torch.optim.Adam, marl.clipped_policy_loss

        class SpyAdam(orig_adam):
            def __init__(self, params, lr, **kw):
                seen.append(lr)
                super().__init__(params, lr=lr, **kw)

        def spy_loss(*a, **kw):
            calls.append(1)
            return orig_loss(*a, **kw)
        torch.optim.Adam, marl.clipped_policy_loss = SpyAdam, spy_loss
        try:
            with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
                for config, lr, ep in (("lr1e-03_ep15", 1e-3, 15), ("lr1e-04_ep05", 1e-4, 5)):
                    seen.clear(), calls.clear()
                    T.run_cell("NoHistory", config, FOLDS[0], 0, args(), Path(tmp) / config, test=False)
                    self.assertEqual(seen, [lr, lr])                             # actor and critic
                    self.assertEqual(len(calls), ep * marl.HP["n_minibatch"])    # one update, ep epochs
        finally:
            torch.optim.Adam, marl.clipped_policy_loss = orig_adam, orig_loss


class D11Cells(unittest.TestCase):
    def test_the_d10_setting_reproduces_a_d10_cell_exactly(self):
        with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
            a = R.run_cell("NoHistory", "MAPPO", FOLDS[0], 0, args(env_steps=64), Path(tmp) / "d10", test=False)
            b = T.run_cell("NoHistory", T.DEFAULT_NAME, FOLDS[0], 0, args(env_steps=64), Path(tmp) / "d11",
                           test=False)
            strip = lambda c: [{k: v for k, v in x.items() if k != "seconds"} for x in c]
            self.assertEqual(strip(a["curve"]), strip(b["curve"]))
            self.assertEqual((a["best_update"], a["best_validation_dwell"]),
                             (b["best_update"], b["best_validation_dwell"]))
            sa = torch.load(Path(tmp) / "d10" / "actor.pt")
            sb = torch.load(Path(tmp) / "d11" / "actor.pt")
            self.assertTrue(all(torch.equal(sa[k], sb[k]) for k in sa))
            for k in ("env_config", "order", "val_seed", "test_seed", "eval_repeats", "arm", "learner", "fold"):
                self.assertEqual(a[k], b[k], k)
            self.assertEqual((b["protocol"], b["config"]), ("D1.1", T.DEFAULT_NAME))

    def test_cells_seal_the_test_and_record_their_setting(self):
        with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "c"
            r = T.run_cell("NoHistory", "lr1e-03_ep05", FOLDS[0], 1, args(), dest, test=True)
            res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
            self.assertNotIn("test", res)
            self.assertNotIn("test_summary", res)
            blob = (dest / "sealed_test.json").read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(), res["sealed_test_sha256"])
            self.assertEqual((res["hp"]["lr"], res["hp"]["ppo_epochs"]), (1e-3, 5))
            self.assertEqual((res["test_seed"], res["val_seed"]), (R.TEST_SEED + 1, R.VAL_SEED + 1))
            self.assertEqual(res["env_config"], R.setting(None)[0].to_dict())      # D1.0 primary setting
            self.assertEqual(res["env_config"]["reward"], "proposal")
            self.assertEqual(res["order"], "frozen")
            self.assertEqual(r["config"], "lr1e-03_ep05")

    def test_smoke_runs_without_freeze_and_seals_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_d1_1.py"), "--smoke",
                                "--output", str(Path(tmp) / "x")], capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            res = sorted((Path(tmp) / "x" / "smoke").rglob("result.json"))
            self.assertEqual(len(res), 2)
            got = {json.loads(x.read_text(encoding="utf-8"))["config"] for x in res}
            self.assertEqual(got, {T.DEFAULT_NAME, T.TIMING_CONFIG})
            self.assertFalse(list(Path(tmp).rglob("sealed_test.json")))

    def test_a_real_run_refuses_without_freeze_and_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_d1_1.py"), "--output",
                                str(Path(tmp) / "x"), "--folds", FOLDS[0]["fold"], "--seeds", "0"],
                               capture_output=True, text=True, timeout=600)
            self.assertNotEqual(r.returncode, 0)
            self.assertTrue("not frozen" in r.stderr + r.stdout or "--preflight first" in r.stderr + r.stdout,
                            r.stderr[-1500:])
            self.assertFalse(list(Path(tmp).rglob("result.json")))
        r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_d1_1.py"), "--smoke", "--seeds", "5"],
                           capture_output=True, text=True, timeout=600)
        self.assertNotEqual(r.returncode, 0)                                     # seeds 0-2 only
        self.assertIn("seeds 0-2", r.stderr + r.stdout)

    def test_preflight_needs_96_allpos_checkpoints_and_the_run_requires_it(self):
        need = T.needed_checkpoints(T.ARMS, FOLDS, T.SEEDS)
        self.assertEqual(len(need), 96)
        self.assertEqual({a for a, _, _ in need}, {"allpos"})
        fold = FOLDS[0]
        with tempfile.TemporaryDirectory() as tmp:
            root, out = Path(tmp) / "enc", Path(tmp) / "d11"
            d = p.data.fold_data(fold)
            p.variants.train_variant("allpos", p.data.W, 0, d["train"], d["val"], 64, device=torch.device("cpu"),
                                     checkpoint_dir=str(root / "variants" / "allpos" / fold["fold"] / "s0"),
                                     patience_checks=16, progress=False)
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_d1_1.py"), "--preflight",
                                "--encoder-root", str(root), "--output", str(out), "--folds", fold["fold"],
                                "--seeds", "0", "1"], capture_output=True, text=True, timeout=600)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr[-1500:])           # seed 1 is missing
            rep = json.loads((out / "PREFLIGHT.json").read_text(encoding="utf-8"))
            self.assertEqual(rep["ok"], [["allpos", fold["fold"], 0]])
            self.assertEqual([(b["seed"], b["error"].split(":")[0]) for b in rep["failures"]],
                             [(1, "FileNotFoundError")])
            ok = {("allpos", fold["fold"], 0)}
            with self.assertRaises(SystemExit):
                T.require_preflight(out, ok)                                      # last preflight failed
            (out / "PREFLIGHT.json").write_text(json.dumps(
                {"pass": True, "spec_sha256": T.spec_sha(), "ok": [["allpos", fold["fold"], 0]]}), encoding="utf-8")
            T.require_preflight(out, ok)
            with self.assertRaises(SystemExit):
                T.require_preflight(out, ok | {("allpos", fold["fold"], 1)})
            (out / "PREFLIGHT.json").write_text(json.dumps(
                {"pass": True, "spec_sha256": "another spec", "ok": [["allpos", fold["fold"], 0]]}), encoding="utf-8")
            with self.assertRaises(SystemExit):
                T.require_preflight(out, ok)                                      # made under another spec

    def test_restart_refuses_a_changed_grid(self):
        orig = (R.spec_d1.SPEC, S.SPEC)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            R.spec_d1.SPEC, S.SPEC = tmp / "SPEC_D1.json", tmp / "SPEC_D1_1.json"
            R.spec_d1.SPEC.write_text(json.dumps({"frozen_on": "x"}), encoding="utf-8")
            S.SPEC.write_text(json.dumps({"frozen_on": "y"}), encoding="utf-8")
            grid = dict(T.GRID)
            try:
                a = argparse.Namespace(env_steps=2_000_000, eval_repeats=20)
                out = tmp / "d11"
                out.mkdir()
                R.write_manifest(out, T.identity_of(a, FOLDS), {"arguments": {"device": "cuda"}})
                R.write_manifest(out, T.identity_of(a, FOLDS), {"arguments": {"device": "cpu"}})   # restart
                T.GRID["lr7e-04_ep10"] = {"lr": 7e-4, "ppo_epochs": 10}
                with self.assertRaises(RuntimeError):
                    R.write_manifest(out, T.identity_of(a, FOLDS), {})
                T.GRID.clear(), T.GRID.update(grid)
                with self.assertRaises(RuntimeError):
                    R.write_manifest(out, T.identity_of(argparse.Namespace(env_steps=1_000_000, eval_repeats=20),
                                                        FOLDS), {})
            finally:
                T.GRID.clear(), T.GRID.update(grid)
                R.spec_d1.SPEC, S.SPEC = orig


def fake_folds():
    fs = [{"fold": f"v{i}", "family": "variant_held_out", "test_runs": [f"r{i}"]} for i in range(8)]
    return fs + [{"fold": "S9", "family": "scenario_held_out", "test_runs": ["u1", "u2"]}]


class D11Selection(unittest.TestCase):
    def test_choose_takes_the_best_then_the_d10_setting_then_grid_order(self):
        g = list(T.GRID)
        sc = {c: 1.0 for c in g}
        self.assertEqual(V.choose(sc, g, T.DEFAULT_NAME), T.DEFAULT_NAME)        # all tied: D1.0 setting
        sc[g[-1]] = 2.0
        self.assertEqual(V.choose(sc, g, T.DEFAULT_NAME), g[-1])
        sc[g[2]] = 2.0
        self.assertEqual(V.choose(sc, g, T.DEFAULT_NAME), g[2])                  # tie without D1.0: grid order
        sc[T.DEFAULT_NAME] = 2.0
        self.assertEqual(V.choose(sc, g, T.DEFAULT_NAME), T.DEFAULT_NAME)

    def test_selection_is_nested_in_each_fold_and_averages_seeds(self):
        g, folds, seeds = list(T.GRID), fake_folds(), [0, 1, 2]
        val = {(c, a, f["fold"], s): 1.0 for c in g for a in T.ARMS for f in folds for s in seeds}
        # fold v0: g[1] wins on the seed mean although g[0] has the single best seed
        val[(g[0], "allpos", "v0", 0)] = 9.0
        for s in seeds:
            val[(g[1], "allpos", "v0", s)] = 4.0
        # fold v1: a huge value in g[8] for v1 must not move any other fold's choice
        val[(g[8], "allpos", "v1", 0)] = 100.0
        sel = V.select(val, folds, seeds, g, T.ARMS, T.DEFAULT_NAME)
        self.assertEqual(sel["allpos"]["v0"]["chosen"], g[1])
        self.assertAlmostEqual(sel["allpos"]["v0"]["validation_E1"][g[0]], 11.0 / 3)
        self.assertEqual(sel["allpos"]["v1"]["chosen"], g[8])
        for f in folds[2:]:
            self.assertEqual(sel["allpos"][f["fold"]]["chosen"], T.DEFAULT_NAME)
        self.assertTrue(all(v["chosen"] == T.DEFAULT_NAME for v in sel["NoHistory"].values()))
        rec = V.selection_record(sel, folds, g, T.ARMS)
        self.assertEqual(rec["counts"]["allpos"]["variant_folds"], {g[1]: 1, g[8]: 1, T.DEFAULT_NAME: 6})
        self.assertEqual(rec["counts"]["allpos"]["all_folds"][T.DEFAULT_NAME], 7)

    def test_selection_reads_validation_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cs = {("c", "allpos", "v0", 0): Path(tmp) / "a"}
            cs[("c", "allpos", "v0", 0)].mkdir()
            (cs[("c", "allpos", "v0", 0)] / "result.json").write_text(json.dumps({"best_validation_dwell": 3.5}),
                                                                       encoding="utf-8")
            self.assertEqual(V.read_validation(cs), {("c", "allpos", "v0", 0): 3.5})   # no sealed file exists


def fake_rows(fold, value, protected=1.0):
    return [{"run": run, "dwell": value, "protected": protected, "p1": 1.0} for run in fold["test_runs"]
            for _ in range(2)]


class D11Scoring(unittest.TestCase):
    def test_tuned_units_use_the_setting_selected_in_their_own_fold(self):
        g, folds, seeds = list(T.GRID), fake_folds(), [0, 1, 2]
        rng = np.random.default_rng(0)
        sealed, sel = {}, {a: {} for a in T.ARMS}
        for i, f in enumerate(folds):
            pick = g[i % len(g)]
            sel["allpos"][f["fold"]] = {"chosen": pick}
            sel["NoHistory"][f["fold"]] = {"chosen": T.DEFAULT_NAME}
            for c in g:
                for s in seeds:
                    sealed[(c, "allpos", f["fold"], s)] = fake_rows(f, 10.0 + i if c == pick else 0.0)
                    sealed[(c, "NoHistory", f["fold"], s)] = fake_rows(f, 3.0 + rng.normal() * 0.01, 0.5)
        res = V.score(sealed, sel, folds, seeds, g, T.ARMS, T.DEFAULT_NAME)
        self.assertEqual(res["n_units"], {"E1": 8, "P1": 8})                     # the scenario fold is apart
        self.assertAlmostEqual(res["means_tuned_primary"]["allpos|E1"], np.mean([10.0 + i for i in range(8)]))
        fam = {c["outcome"]: c for c in res["family_H"]}
        self.assertGreater(fam["E1"]["mean"], 0)
        self.assertIn("p_holm", fam["E1"])
        self.assertEqual(len(res["allpos_minus_NoHistory_by_setting"]), 18)
        self.assertTrue(all("p" not in c and "verdict" not in c for c in res["allpos_minus_NoHistory_by_setting"]))
        self.assertTrue(all("p" not in c for c in res["tuned_minus_D1_0_setting"]))
        self.assertEqual(sorted(res["unseen_scenarios_descriptive_tuned"]["allpos|E1"]), ["u1", "u2"])
        self.assertEqual(res["unseen_scenarios_descriptive_tuned"]["allpos|E1"]["u1"], 18.0)   # fold 8: g[8]

    def test_open_once_with_every_check(self):
        g, seeds = list(T.GRID), list(T.SEEDS)
        cfg, order = R.setting(None)
        orig = (S.require, V.RESULTS, S.SPEC)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "d11"
            S.require, V.RESULTS, S.SPEC = (lambda: None), Path(tmp) / "res", Path(tmp) / "SPEC_D1_1.json"
            S.SPEC.write_text(json.dumps({"frozen_on": "test"}), encoding="utf-8")
            cs = V.cells(out, FOLDS, seeds, g, T.ARMS)
            test_ids = {f["fold"]: [r["id"] for r in p.runs(f, "test")] for f in FOLDS}
            for (c, arm, fold_id, s), d in cs.items():
                runs = test_ids[fold_id]
                blob = json.dumps({"test": [{"run": r, "dwell": 5.0 if arm == "allpos" else 4.0, "protected": 1.0,
                                             "p1": 1.0} for r in runs], "test_summary": {}, "test_h0_summary": {}},
                                  sort_keys=True).encode("utf-8")
                d.mkdir(parents=True)
                (d / "sealed_test.json").write_bytes(blob)
                (d / "result.json").write_text(json.dumps(
                    {"protocol": "D1.1", "config": c, "hp": dict(T.GRID[c]), "arm": arm, "learner": "MAPPO",
                     "test_seed": R.TEST_SEED + s, "eval_repeats": 20, "env_config": cfg.to_dict(), "order": order,
                     "best_validation_dwell": 1.0, "sealed_test_sha256": hashlib.sha256(blob).hexdigest()}),
                    encoding="utf-8")
            run = lambda: self._main(["--open-test", "--output", str(out)])
            try:
                with self.assertRaises(SystemExit) as cm:
                    run()
                self.assertIn("dry run has not passed", str(cm.exception))
                (out / "DRY_RUN_VALIDATION.json").write_text(json.dumps({"pass": True}), encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    run()
                self.assertIn("SELECTION.json is missing", str(cm.exception))
                sel = V.select(V.read_validation(cs), FOLDS, seeds, g, T.ARMS, T.DEFAULT_NAME)
                rec = V.selection_record(sel, FOLDS, g, T.ARMS)
                bad = json.loads(json.dumps(rec))
                bad["selection"]["allpos"][FOLDS[0]["fold"]]["chosen"] = g[0]
                (out / "SELECTION.json").write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    run()
                self.assertIn("differs", str(cm.exception))
                (out / "SELECTION.json").write_text(json.dumps(rec), encoding="utf-8")
                first = cs[("lr1e-03_ep15", "NoHistory", FOLDS[5]["fold"], 2)] / "result.json"
                keep = first.read_text(encoding="utf-8")
                self.assertIn('"ppo_epochs": 15', keep)
                first.write_text(keep.replace('"ppo_epochs": 15', '"ppo_epochs": 10'), encoding="utf-8")
                with self.assertRaises(RuntimeError):                            # the cell's HP disagree
                    run()
                first.write_text(keep, encoding="utf-8")
                run()                                                            # opens
                res = json.loads((Path(tmp) / "res" / "D1_1_RESULTS.json").read_text(encoding="utf-8"))
                self.assertEqual(res["n_units"], {"E1": 29, "P1": 29})          # the 29 variant folds
                fam = {c["outcome"]: c for c in res["family_H"]}
                self.assertAlmostEqual(fam["E1"]["mean"], 1.0)
                self.assertTrue((out / "TEST_OPENED.json").exists())
                with self.assertRaises(SystemExit) as cm:
                    run()
                self.assertIn("never opened again", str(cm.exception))
            finally:
                S.require, V.RESULTS, S.SPEC = orig

    @staticmethod
    def _main(argv):
        old = sys.argv
        sys.argv = ["evaluate_d1_1.py", *argv]
        try:
            V.main()
        finally:
            sys.argv = old


class D11SpecAndDriver(unittest.TestCase):
    def test_spec_pins_d10s_freeze_record_and_every_d11_file(self):
        self.assertIn("camlds_real_full_arch/SPEC_D1.json", S.FILES)
        for name in ("PROTOCOL_D1.1.md", "run_d1_1.py", "evaluate_d1_1.py", "run_all_d1_1.py", "test_d1_1.py",
                     "spec_d1_1.py"):
            self.assertIn(f"camlds_real_full_arch/{name}", S.FILES)
        self.assertTrue(all((p.REPO / rel).exists() for rel in S.FILES))

    def test_freeze_refuses_after_the_d10_test_opening_and_when_frozen(self):
        orig = (S.SPEC, S.D10_MAIN_OPENED)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            S.SPEC, S.D10_MAIN_OPENED = tmp / "SPEC_D1_1.json", tmp / "TEST_OPENED.json"
            try:
                S.D10_MAIN_OPENED.write_text("{}", encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    S.freeze("2026-11-18")
                self.assertIn("D1.0 main test has been opened", str(cm.exception))
                S.D10_MAIN_OPENED.unlink()
                S.freeze("2026-11-18")
                self.assertTrue(S.check())
                spec = json.loads(S.SPEC.read_text(encoding="utf-8"))
                self.assertFalse(spec["d10_main_test_opened_at_freeze"])
                with self.assertRaises(SystemExit):
                    S.freeze("2026-11-18")                                       # already frozen
                spec["sha256"]["camlds_real_full_arch/run_d1_1.py"] = "0" * 64
                S.SPEC.write_text(json.dumps(spec), encoding="utf-8")
                self.assertFalse(S.check())                                      # a pinned file "changed"
            finally:
                S.SPEC, S.D10_MAIN_OPENED = orig

    def test_only_open_opens_and_tune_runs_in_order(self):
        import run_all_d1_1 as DD
        cmds = [" ".join(c) for _, c, _ in DD.plan("tune", "cuda") if c]
        self.assertFalse(any("--open-test" in c for c in cmds))
        labels = [l for l, _, _ in DD.plan("tune", "cuda")]
        order = [next(i for i, l in enumerate(labels) if l.startswith(k)) for k in
                 ("protocols", "D1.0 validity gate", "preflight", "timing", "D1.1 run", "validation dry run")]
        self.assertEqual(order, sorted(order))
        opens = [c for _, c, _ in DD.plan("open", "cuda") if c]
        self.assertEqual(len(opens), 1)
        self.assertIn("--open-test", opens[0])

    def test_open_is_skipped_until_dry_run_and_selection_exist(self):
        import run_all_d1_1 as DD
        orig = DD.OUT
        with tempfile.TemporaryDirectory() as tmp:
            DD.OUT = Path(tmp)
            try:
                self.assertEqual(DD._open_pre()[0], "skip")
                (Path(tmp) / "DRY_RUN_VALIDATION.json").write_text(json.dumps({"pass": True}), encoding="utf-8")
                self.assertEqual(DD._open_pre()[0], "skip")                      # no selection yet
                (Path(tmp) / "SELECTION.json").write_text("{}", encoding="utf-8")
                self.assertIsNone(DD._open_pre())
                self.assertEqual(DD._dry_pre()[0], "skip")
                (Path(tmp) / "TEST_OPENED.json").write_text("{}", encoding="utf-8")
                self.assertEqual(DD._open_pre()[0], "skip")
            finally:
                DD.OUT = orig

    def test_driver_stops_at_the_first_failure(self):
        import run_all_d1_1 as DD
        ok = [sys.executable, "-c", "print('step one ran')"]
        fail = [sys.executable, "-c", "import sys; print('step two fails'); sys.exit(3)"]
        never = [sys.executable, "-c", "print('STEP THREE MUST NOT RUN')"]
        orig_plan, orig_out = DD.plan, DD.OUT
        with tempfile.TemporaryDirectory() as tmp:
            DD.OUT = Path(tmp)
            DD.plan = lambda stage, device: [("one", ok, None), ("two", fail, None), ("three", never, None)]
            argv = sys.argv
            sys.argv = ["run_all_d1_1.py", "tune", "--device", "cpu"]
            try:
                with self.assertRaises(SystemExit) as cm:
                    DD.main()
            finally:
                sys.argv, DD.plan, DD.OUT = argv, orig_plan, orig_out
            self.assertEqual(cm.exception.code, 1)
            text = next((Path(tmp) / "logs").glob("tune_*.log")).read_text(encoding="utf-8")
            self.assertIn("step one ran", text)
            self.assertIn("STOPPED at [2/3] two: exit code 3", text)
            self.assertNotIn("STEP THREE MUST NOT RUN", text)

    def test_protocol_text_states_the_grid_and_the_size(self):
        text = (HERE / "PROTOCOL_D1.1.md").read_text(encoding="utf-8")
        for s in ("1e-4, 5e-4, 1e-3", "5, 10, 15", "1,728", "seeds 0-2", "nested", "D1.2"):
            self.assertIn(s, text)


if __name__ == "__main__":
    unittest.main()
