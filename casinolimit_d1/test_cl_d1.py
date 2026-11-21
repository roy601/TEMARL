# -*- coding: utf-8 -*-
"""Tests for protocol CL-D1.0 (CasinoLimit deception): the world built from D1.0's frozen files, the
payoff rule, the data, the history inputs, the gate, the runner, the scorer, the spec and the driver.

    cd casinolimit_d1 && python -m unittest test_cl_d1
"""
import argparse
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cl_world as C  # noqa: E402  (first)
import gate_cl as G  # noqa: E402
import run_cl as R  # noqa: E402
import evaluate_cl as V  # noqa: E402
import spec_cl_d1 as S  # noqa: E402

env, marl, B = C.env, C.marl, C.B
REPO = C.REPO
FOLDS = C.folds()
RUNS = C.all_runs()
TINY = {"n_envs": 2, "rollout_len": 4, "n_evals": 1}


class tiny_hp:
    def __enter__(self):
        self.old = dict(marl.HP)
        marl.HP.update(TINY)

    def __exit__(self, *exc):
        marl.HP.clear()
        marl.HP.update(self.old)


def args(**kw):
    return argparse.Namespace(**{"eval_repeats": 1, "encoder_root": str(HERE / "no_encoders"),
                                 "records": str(R.CL10_RECORDS), "device": "cpu", "env_steps": 8,
                                 "verbose": False, **kw})


def tiny_encoder(root: Path, fold, seed=0, arm="allpos"):
    """A small encoder in the CL 1.0 layout, and the validation BCE it reproduces."""
    d = C.CD.fold_data(fold)
    cell = R.checkpoint(arm, fold["fold"], seed, root).parent
    C.CP.V.train_variant(arm, C.W, seed, d["train"], d["val"], 64, device=torch.device("cpu"),
                         checkpoint_dir=str(cell), patience_checks=16, progress=False)
    ck = torch.load(cell / "encoder.pt", map_location="cpu", weights_only=False)
    m = C.CP.V.build_variant(arm, C.W)
    m.load_state_dict(ck["state_dict"])
    m.eval()
    return float(C.CP.Mx.bce(C.CP.V.numpy_logits(m, *d["val"][:2], torch.device("cpu")), d["val"][2]))


def fake_records(root: Path, fd, enc_root: Path, seed=0, arm="allpos", bce_shift=0.0, logit_shift=0.0, **override):
    """A CL 1.0-style record of the encoder in enc_root: identity fields, validation rows, the validation
    logits file with its SHA-256, and the validation BCE (shifts and overrides fake a wrong record)."""
    d = C.CD.fold_data(fd)
    ck = torch.load(R.checkpoint(arm, fd["fold"], seed, enc_root), map_location="cpu", weights_only=False)
    m = C.CP.V.build_variant(arm, C.W)
    m.load_state_dict(ck["state_dict"])
    m.eval()
    lo = np.asarray(C.CP.V.numpy_logits(m, *d["val"][:2], torch.device("cpu")), np.float32)
    cell = root / arm / fd["fold"] / f"s{seed}"
    cell.mkdir(parents=True, exist_ok=True)
    np.save(cell / "val_logits.npy", lo + np.float32(logit_shift))
    rec = {"variant": arm, "fold": fd["fold"], "seed": seed, "window": C.W, "labels": C.NT,
           "val_source_rows": json.loads(json.dumps(d["val_source_rows"])),
           "val": {"file": "val_logits.npy", "sha256": R.sha_file(cell / "val_logits.npy"), "points": int(len(lo))},
           "validation": {"bce": float(C.CP.Mx.bce(lo, d["val"][2])) + bce_shift}, **override}
    (cell / "result.json").write_text(json.dumps(rec), encoding="utf-8")
    return rec


class CLWorld(unittest.TestCase):
    def test_the_environment_learner_and_baselines_are_d10s_frozen_files(self):
        pinned = json.loads(C.D10_SPEC.read_text(encoding="utf-8"))["sha256"]
        for name, rel in C.FROZEN.items():
            self.assertEqual(S.sha_lf(REPO / rel), pinned[rel], rel)
            self.assertEqual(Path(sys.modules[name].__file__).resolve(), (REPO / rel).resolve())
        self.assertIs(sys.modules["env_cmd"], env)
        self.assertIs(B.CommandEngagementEnv, env.CommandEngagementEnv)
        self.assertIs(marl.CommandEngagementEnv, env.CommandEngagementEnv)
        self.assertEqual((env.NT, marl.NT, env.N_AGENTS, env.N_ACTIONS), (66, 66, 4, 6))
        self.assertEqual(env.POSITIONS, ["start", "bastion", "meet", "intranet", "Firewall"])
        self.assertEqual(env.LOCAL_DIM, 4 + 1 + 66 + 6 + 5)
        self.assertEqual(marl.HP["lr"], 5e-4)                        # D1.0's learner settings, unchanged

    def test_a_cam_lds_environment_in_the_same_process_is_refused(self):
        code = ("import sys; sys.path.insert(0, r'%s'); import pipeline; sys.path.insert(0, r'%s'); "
                "import cl_world") % (REPO / "camlds_real_full_arch", HERE)
        r = subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True, timeout=300)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("run CasinoLimit in its own process", r.stderr)

    def test_payoff_rows_equal_d10s_for_shared_techniques_and_follow_the_rule(self):
        DP, VOC = C.DP, C.VOC
        shared = [t for t in C.LABELS if t in VOC.TECHNIQUES]
        self.assertEqual(len(shared), 45)
        for t in shared:
            np.testing.assert_array_equal(C.PAYOFF[C.LABEL_ID[t]], DP.PAYOFF[VOC.TECHNIQUES[t]["id"]], t)
        new = [t for t in C.LABELS if t not in VOC.TECHNIQUES]
        self.assertEqual(len(new), 21)
        for t in new:
            self.assertEqual(C.ATTACK["techniques"][t]["tactics"], [C.TACTICS[t]["tactic"]])
            self.assertEqual(C.TACTICS[t]["source"], "ATT&CK v15.1")
        for t in shared:                                          # the frozen tactic is one of ATT&CK's
            self.assertIn(C.TACTICS[t]["tactic"], C.ATTACK["techniques"][t]["tactics"])
        rd = [t for t in C.LABELS if C.TACTICS[t]["tactic"] == "Resource Development"]
        self.assertEqual(sorted(rd), ["T1587", "T1608"])
        for t in rd:                                              # no D3FEND decoy is listed for it
            np.testing.assert_array_equal(C.PAYOFF[C.LABEL_ID[t]], [DP.W_NULL] + [DP.W_OTHER] * 5)
        np.testing.assert_array_equal(env.PAYOFF, C.PAYOFF)

    def test_the_permuted_payoff_changes_only_which_decoy_suits_which_tactic(self):
        A, info = C.PAYOFF_PERMUTED, C.PERMUTATION_INFO
        again, _ = C.permuted_payoff(C.PERMUTE_SEED)
        np.testing.assert_array_equal(A, again)                    # deterministic from the declared seed
        self.assertEqual(C.PERMUTE_SEED, 20261122)
        np.testing.assert_array_equal(A[:, 0], C.PAYOFF[:, 0])      # 'none' column kept
        for i in range(C.NT):
            self.assertEqual(sorted(A[i]), sorted(C.PAYOFF[i]))     # each row keeps its values
        for tac, v in info.items():                                 # one permutation per tactic
            p = np.array(v["permutation"])
            for i, t in enumerate(C.LABELS):
                if C.TACTICS[t]["tactic"] == tac:
                    np.testing.assert_array_equal(A[i, 1:], C.PAYOFF[i, p])
            if tac == "Resource Development":
                self.assertEqual(v["best_before"], [1, 2, 3, 4, 5])
            else:
                self.assertNotEqual(v["best_before"], v["best_after"], tac)
        self.assertEqual(len(info), 14)
        self.assertEqual(sum(v["best_before"] != v["best_after"] for v in info.values()), 13)
        self.assertEqual(int((~np.isclose(A, C.PAYOFF)).any(1).sum()), 64)
        self.assertEqual((info["Discovery"]["best_before"], info["Discovery"]["best_after"]), ([1], [2]))
        self.assertEqual(C.DP.ACTIONS[1:3], ["decoy_network_resource", "decoy_environment"])
        self.assertNotEqual(C.table_sha256(A), C.table_sha256(C.PAYOFF))

    def test_attack_extract_is_the_pinned_release(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("attack_extract", HERE / "checks" / "attack_extract.py")
        X = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(X)
        self.assertEqual(C.ATTACK["version"], "15.1")
        self.assertEqual(C.ATTACK["bundle_sha256"], X.BUNDLE_SHA256)
        self.assertEqual(list(C.ATTACK["techniques"]), C.LABELS)

    def test_runs_follow_the_cl10_folds_and_the_recorded_machines(self):
        self.assertEqual(len(RUNS), 114)
        self.assertEqual(sum(len(r["commands"]) for r in RUNS), 8201)
        tested = Counter(r for f in FOLDS for r in f["test_runs"])
        self.assertEqual(set(tested.values()), {1})                 # every run is tested exactly once
        self.assertEqual(len(tested), 114)
        import cl_split
        self.assertEqual([{k: f[k] for k in ("fold", "test_runs", "val_runs", "train_runs")} for f in FOLDS],
                         cl_split.folds(C.CP.STEPS))
        steps = {(s["run"], s["exec_index"]): s for s in C.CP.STEPS}
        for r in RUNS:
            self.assertEqual(r["positions"], [steps[(r["id"], i)]["machine"] for i in range(len(r["commands"]))])
            self.assertFalse(any(r["goal"]))
            for i, c in enumerate(r["commands"]):
                self.assertEqual(c, tuple(sorted(C.LABEL_ID[t] for t in steps[(r["id"], i)]["techniques_parent"])))

    def test_history_inputs_equal_the_encoders_windows(self):
        class Spy(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.w = torch.nn.Parameter(torch.zeros(1))
                self.seen = []

            def history(self, x, m):
                self.seen.append((x.numpy().copy(), m.numpy().copy()))
                return torch.zeros(x.shape[0], 64)
        f = FOLDS[0]
        for r in C.runs(f, "val")[:4]:
            spy = Spy()
            bank = marl.HistoryBank(spy, C.W, "cpu")
            spec = C.specs([r], 1, 1)[0]
            bank.table(spec)
            X, M = spy.seen[0]
            Xw, Mw, _, _, _ = C.CD.windows(f["_steps"], [r["id"]])
            n = len(r["commands"])
            np.testing.assert_array_equal(X[:n - 1], Xw)          # prefix [0, t) predicts command t
            np.testing.assert_array_equal(M[:n - 1], Mw)

    def test_agents_never_see_the_next_command_or_machine(self):
        e = env.CommandEngagementEnv(env.EnvConfig(reward="proposal"), C.MAX_STEPS)
        joint = (1, 2, 3, 4)                                       # every agent deploys: lures can fire
        for r in [x for x in RUNS if len(set(x["positions"])) > 1][:8]:
            n = len(r["commands"])
            for k in (1, n // 2, n - 1):
                alt = dict(r)
                cmds, pos = list(r["commands"]), list(r["positions"])
                cmds[k] = tuple(sorted({(c + 7) % C.NT for c in cmds[k]}))
                pos[k] = next(z for z in C.MACHINES if z != pos[k])
                alt["commands"], alt["positions"] = tuple(cmds), pos
                seen = []
                for run in (r, alt):
                    s = C.specs([run], 11, 1)[0]
                    e.reset(s)
                    for _ in range(k):
                        e.step(list(joint))
                    seen.append((e.local_obs().copy(), e.history_window(C.W)))
                np.testing.assert_array_equal(seen[0][0], seen[1][0])   # local observations before step k
                np.testing.assert_array_equal(seen[0][1][0], seen[1][1][0])   # history window before step k
                np.testing.assert_array_equal(seen[0][1][1], seen[1][1][1])

    def test_the_attacker_follows_the_recorded_machines(self):
        e = env.CommandEngagementEnv(env.EnvConfig(reward="proposal"), C.MAX_STEPS)
        for r in RUNS[:20]:
            s = C.specs([r], 3, 1)[0]
            e.reset(s)
            zones = []
            while not e.done:
                e.step([env.NULL] * 4)
                zones.append(env.POSITIONS[e.zone])
            self.assertEqual(zones, r["positions"])
            st = e.episode_stats()
            self.assertEqual((st["undefended_commands"], st["protected"], st["p1"], st["dwell"]), (0, 1.0, 0.0, 0.0))

    def test_reward_choice_changes_no_outcome_of_a_fixed_policy(self):
        for joint in ((1, 1, 0, 0), (3, 4, 0, 2)):
            out = {}
            for rw in ("engagement", "proposal"):
                cfg = env.EnvConfig(reward=rw)
                e = env.CommandEngagementEnv(cfg, C.MAX_STEPS)
                out[rw] = [env.run_episode(e, s, B.FixedJointPolicy(joint)) for s in C.specs(RUNS[:10], 5, 2)]
            strip = lambda rows: [{k: v for k, v in x.items()} for x in rows]
            self.assertEqual(strip(out["engagement"]), strip(out["proposal"]))


class CLGate(unittest.TestCase):
    def test_the_planner_is_d10s_planner(self):
        """gate_cl.TransitionPlanner's text, run on D1.0's CAM-LDS environment, makes D1.0's decisions."""
        src = (HERE / "gate_cl.py").read_text(encoding="utf-8")
        node = next(n for n in ast.parse(src).body if isinstance(n, ast.ClassDef) and n.name == "TransitionPlanner")
        cls_src = ast.get_source_segment(src, node)
        code = f'''
import sys, json
sys.path.insert(0, r"{REPO / 'camlds_real_full_arch'}")
import gate_d1 as GD
import numpy as np
from collections import Counter, defaultdict
ns = {{"np": np, "Counter": Counter, "defaultdict": defaultdict, "env": GD.env}}
exec({cls_src!r}, ns)
runs = GD.all_runs()
cfg = GD.env.EnvConfig(reward="proposal")
same = 0
for k, r in enumerate(runs[:12]):
    train = [x for x in runs if x["id"] != r["id"]]
    a, b = GD.TransitionPlanner(train, cfg), ns["TransitionPlanner"](train, cfg)
    for c in r["commands"]:
        assert a._best_for(tuple(c)) == b._best_for(tuple(c)), (r["id"], c)
        same += 1
print("SAME", same)
'''
        r = subprocess.run([sys.executable, "-W", "ignore", "-c", code], capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertIn("SAME", r.stdout)

    def test_gate_randomness_is_disjoint_and_the_gate_needs_the_freeze(self):
        self.assertNotIn(G.GATE_SEED, {R.VAL_SEED + s for s in range(10)} | {R.TEST_SEED + s for s in range(10)})
        self.assertNotIn(G.GATE_SEED, {V.FIT_SEED})
        r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "gate_cl.py"), "--smoke"],
                           capture_output=True, text=True, timeout=600)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertIn("smoke OK", r.stdout)
        self.assertNotIn("GATE:", r.stdout)                       # no gate number before the freeze
        if not S.SPEC.exists():
            with tempfile.TemporaryDirectory() as tmp:
                r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "gate_cl.py"), "--output", tmp],
                                   capture_output=True, text=True, timeout=600)
                self.assertNotEqual(r.returncode, 0)
                self.assertFalse((Path(tmp) / "GATE_RESULT.json").exists())


class CLRunner(unittest.TestCase):
    def test_studies_cells_and_seeds(self):
        n = {s: len(R.all_cells(R.OUT, s, FOLDS)) for s in R.STUDIES}
        self.assertEqual(n, {"main": 350, "efficacy_0.5": 50, "efficacy_0.75": 50, "mean": 50,
                             "reward_engagement": 50, "payoff_permuted": 50, "tune": 270})
        self.assertEqual(sum(n.values()), 870)
        self.assertEqual(set(R.PAYOFF_TABLES), {"payoff_permuted"})
        for s in R.STUDIES:
            want = C.PAYOFF_PERMUTED if s == "payoff_permuted" else C.PAYOFF
            np.testing.assert_array_equal(R.table(s), want)
        self.assertEqual(R.SEEDS["main"], tuple(range(10)))
        self.assertEqual(R.SEEDS["tune"], (0, 1, 2))
        self.assertEqual(len(R.needed_checkpoints(FOLDS)), 200)
        order = R.order("main", FOLDS)
        first_other = next(i for i, x in enumerate(order) if (x[1], x[2]) not in R.PRIMARY_CELLS)
        self.assertEqual(first_other, 100)                         # all primary cells run first
        self.assertEqual(R.setting("main").reward, "proposal")     # D1.0 decision D6
        for s, kw in R.SENSITIVITIES.items():
            d0, d1 = R.setting("main").to_dict(), R.setting(s).to_dict()
            self.assertEqual({k for k in d0 if d0[k] != d1[k]}, set(kw))
        self.assertEqual(len(R.GRID), 9)
        self.assertIn(R.DEFAULT_NAME, R.GRID)

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
        before = dict(marl.HP)
        try:
            with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
                for config, lr, ep in (("lr1e-03_ep15", 1e-3, 15), ("lr1e-04_ep05", 1e-4, 5)):
                    seen.clear(), calls.clear()
                    R.run_cell("tune", config, "NoHistory", "MAPPO", FOLDS[0], 0, args(), Path(tmp) / config, test=False)
                    self.assertEqual(seen, [lr, lr])
                    self.assertEqual(len(calls), ep)
        finally:
            torch.optim.Adam, marl.clipped_policy_loss = orig_adam, orig_loss
        self.assertEqual(marl.HP, before)

    def test_the_study_payoff_is_in_force_and_restored(self):
        seen, orig_train, orig_eval = [], marl.train, marl.evaluate_team

        def spy_train(*a, **kw):
            seen.append(("train", env.PAYOFF.copy()))
            return orig_train(*a, **kw)

        def spy_eval(*a, **kw):
            seen.append(("eval", env.PAYOFF.copy()))
            return orig_eval(*a, **kw)
        marl.train, marl.evaluate_team = spy_train, spy_eval
        try:
            with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
                for study in ("payoff_permuted", "main"):
                    seen.clear()
                    dest = Path(tmp) / study
                    res = R.run_cell(study, R.DEFAULT_NAME, "NoHistory", "MAPPO", FOLDS[0], 0, args(), dest, test=False)
                    np.testing.assert_array_equal(env.PAYOFF, C.PAYOFF)            # restored after training
                    self.assertEqual(res["payoff_sha256"], R.table_sha(study))
                    got, rec = R.revalidate(dest, FOLDS[0], 0, None, "cpu", R.setting(study))
                    self.assertAlmostEqual(got, rec, places=9)                    # the dry run reproduces it
                    np.testing.assert_array_equal(env.PAYOFF, C.PAYOFF)
                    self.assertTrue(seen)
                    for _, tab in seen:
                        np.testing.assert_array_equal(tab, R.table(study))
        finally:
            marl.train, marl.evaluate_team = orig_train, orig_eval
        with self.assertRaises(KeyError):
            with R.payoff("payoff_permuted"):
                raise KeyError("boom")
        np.testing.assert_array_equal(env.PAYOFF, C.PAYOFF)                        # restored on an exception
        a = argparse.Namespace(env_steps=2_000_000, eval_repeats=20)
        orig = S.SPEC
        with tempfile.TemporaryDirectory() as tmp:
            S.SPEC = Path(tmp) / "SPEC_CL_D1.json"
            S.SPEC.write_text(json.dumps({"frozen_on": "x"}), encoding="utf-8")
            try:
                ids = {s: R.identity_of(a, s, FOLDS)["payoff_sha256"] for s in ("main", "payoff_permuted")}
            finally:
                S.SPEC = orig
        self.assertNotEqual(ids["main"], ids["payoff_permuted"])

    def test_cells_seal_the_test(self):
        with tiny_hp(), tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "c"
            R.run_cell("efficacy_0.5", R.DEFAULT_NAME, "NoHistory", "IPPO", FOLDS[1], 2, args(), dest, test=True)
            res = json.loads((dest / "result.json").read_text(encoding="utf-8"))
            self.assertNotIn("test", res)
            self.assertNotIn("test_summary", res)
            blob = (dest / "sealed_test.json").read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(), res["sealed_test_sha256"])
            self.assertEqual((res["test_seed"], res["val_seed"]), (R.TEST_SEED + 2, R.VAL_SEED + 2))
            self.assertEqual((res["env_config"]["efficacy"], res["env_config"]["reward"]), (0.5, "proposal"))
            self.assertEqual((res["protocol"], res["study"], res["learner"]), ("CL-D1.0", "efficacy_0.5", "IPPO"))
            test_runs = {x["run"] for x in json.loads(blob)["test"]}
            self.assertEqual(test_runs, set(FOLDS[1]["test_runs"]))

    def test_smoke_runs_without_freeze_and_seals_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_cl.py"), "--smoke", "--output", tmp],
                               capture_output=True, text=True, timeout=900)
            self.assertEqual(r.returncode, 0, r.stderr[-2000:])
            self.assertEqual(len(list(Path(tmp).rglob("result.json"))), 4)
            self.assertFalse(list(Path(tmp).rglob("sealed_test.json")))

    def test_a_real_run_refuses_without_freeze_and_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_cl.py"), "--output", tmp,
                                "--study", "main"], capture_output=True, text=True, timeout=600)
            self.assertNotEqual(r.returncode, 0)
            self.assertTrue(any(s in r.stdout + r.stderr for s in ("not frozen", "gate has not passed",
                                                                    "--preflight first")), r.stderr[-1500:])
            self.assertFalse(list(Path(tmp).rglob("result.json")))

    def test_only_the_cl10_checkpoint_is_accepted(self):
        f = FOLDS[0]
        with tempfile.TemporaryDirectory() as tmp:
            root, rec = Path(tmp) / "enc", Path(tmp) / "rec"
            bce = tiny_encoder(root, f)
            fake_records(rec, f, root)
            model, info = R.load_encoder("allpos", f, 0, root, "cpu", rec)
            self.assertAlmostEqual(info["validation_bce"], bce, places=7)
            self.assertLessEqual(info["validation_logits_max_abs_diff"], 1e-6)
            self.assertEqual(len(info["checkpoint_sha256"]), 64)
            bad = {"BCE": {"bce_shift": 1e-3},                             # e.g. PC 2's retrained encoder
                   "logits": {"logit_shift": 0.01},
                   "variant": {"variant": "gru_allpos"},
                   "fold": {"fold": "F2"},
                   "window": {"window": 8},
                   "labels": {"labels": 81},
                   "validation rows": {"val_source_rows": [0, 1, 2]}}
            for what, kw in bad.items():
                fake_records(rec, f, root, **kw)
                with self.assertRaises(ValueError, msg=what) as cm:
                    R.load_encoder("allpos", f, 0, root, "cpu", rec)
                self.assertTrue(any(s in str(cm.exception) for s in ("not the CL 1.0 checkpoint", "preprocessing changed")),
                                (what, str(cm.exception)))
            fake_records(rec, f, root)
            vfile = rec / "allpos" / f["fold"] / "s0" / "val_logits.npy"
            arr = np.load(vfile)
            arr[0, 0] += 1.0
            np.save(vfile, arr)                                              # the committed file changed
            with self.assertRaises(ValueError) as cm:
                R.load_encoder("allpos", f, 0, root, "cpu", rec)
            self.assertIn("missing or changed", str(cm.exception))
            with self.assertRaises(FileNotFoundError):
                R.load_encoder("allpos", f, 1, root, "cpu", rec)
            self.assertEqual(R.load_encoder("NoHistory", f, 0, root, "cpu", rec)[0], None)

    def test_timing_checks_the_dry_run_on_this_device(self):
        f = FOLDS[0]
        with tempfile.TemporaryDirectory() as tmp:
            root, rec, out = Path(tmp) / "enc", Path(tmp) / "rec", Path(tmp) / "out"
            tiny_encoder(root, f)
            fake_records(rec, f, root)
            r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "run_cl.py"), "--timing", "--encoder-root",
                                str(root), "--records", str(rec), "--output", str(out), "--env-steps", "4096",
                                "--eval-repeats", "2"], capture_output=True, text=True, timeout=900)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr[-1500:])
            rep = json.loads(next(out.rglob("TIMING_DRY_RUN.json")).read_text(encoding="utf-8"))
            self.assertTrue(rep["pass"])

    def test_restart_refuses_what_decides_a_cell(self):
        orig = S.SPEC
        with tempfile.TemporaryDirectory() as tmp:
            S.SPEC = Path(tmp) / "SPEC_CL_D1.json"
            S.SPEC.write_text(json.dumps({"frozen_on": "x"}), encoding="utf-8")
            try:
                a = argparse.Namespace(env_steps=2_000_000, eval_repeats=20)
                out = Path(tmp) / "main"
                R.write_manifest(out, R.identity_of(a, "main", FOLDS), {"arguments": {"device": "cuda"}})
                R.write_manifest(out, R.identity_of(a, "main", FOLDS), {"arguments": {"device": "cpu"}})
                with self.assertRaises(RuntimeError):
                    R.write_manifest(out, R.identity_of(argparse.Namespace(env_steps=10, eval_repeats=20), "main", FOLDS), {})
                with self.assertRaises(RuntimeError):
                    R.write_manifest(out, R.identity_of(a, "mean", FOLDS), {})
            finally:
                S.SPEC = orig


def fake_folds(n=6):
    return [{"fold": f"X{i}", "test_runs": [f"r{i}a", f"r{i}b"]} for i in range(n)]


def rows(fold, value):
    return [{"run": run, "dwell": value, "protected": 1.0, "p1": 0.0, "length": 10.0, "depth": 1.0, "exposed": 0.0,
             "lure_chains": 0.0, "dead_ends": 0.0, "capacity_violations": 0.0, "multi_decoy_steps": 0.0,
             **{f"decoy_steps_{z}": 1.0 for z in C.MACHINES}, **{f"engaged_{z}": 0.0 for z in C.MACHINES}}
            for run in fold["test_runs"] for _ in range(2)]


class CLEvaluation(unittest.TestCase):
    def test_selection_is_nested_and_follows_the_tie_rule(self):
        g, folds, seeds = list(R.GRID), fake_folds(), [0, 1, 2]
        val = {(c, a, f["fold"], s): 1.0 for c in g for a in ("allpos", "NoHistory") for f in folds for s in seeds}
        for s in seeds:
            val[(g[1], "allpos", "X0", s)] = 4.0
        val[(g[0], "allpos", "X0", 0)] = 9.0                       # best single seed, not best mean
        val[(g[8], "allpos", "X1", 0)] = 100.0
        sel = V.select(val, folds, seeds, g, ("allpos", "NoHistory"), R.DEFAULT_NAME)
        self.assertEqual(sel["allpos"]["X0"]["chosen"], g[1])
        self.assertEqual(sel["allpos"]["X1"]["chosen"], g[8])
        self.assertTrue(all(sel["allpos"][f["fold"]]["chosen"] == R.DEFAULT_NAME for f in folds[2:]))
        self.assertTrue(all(v["chosen"] == R.DEFAULT_NAME for v in sel["NoHistory"].values()))

    def test_scoring_on_synthetic_rows(self):
        folds, seeds = fake_folds(), [0, 1]
        rng = np.random.default_rng(0)
        sealed = {(a, l, f["fold"], s): rows(f, (6.0 if a == "allpos" else 4.0) + rng.normal() * 0.01)
                  for a, l in R.MAIN_CELLS for f in folds for s in seeds}
        refs = {(n, f["fold"], s): rows(f, 2.0) for n in (*V.REFERENCES, "clairvoyant") for f in folds for s in seeds}
        res = V.score_main(sealed, folds, seeds, refs)
        self.assertEqual(res["n_units"], 12)
        self.assertEqual([len(res[k]) for k in ("family_1", "family_2", "family_3")], [1, 6, 1])
        self.assertGreater(res["family_1"][0]["mean"], 1.9)
        self.assertTrue(all("p" not in c for c in res["q4_descriptive"]))
        self.assertIn("decoy_share_intranet", res["team_activity_descriptive"]["allpos"])
        d = res["family_1_descriptive"]
        self.assertAlmostEqual(d["engaged_fraction"]["mean"], 0.2, places=2)       # (6 - 4) / length 10
        self.assertEqual([g["runs"] for g in d["by_length_tertile"]], [4, 4, 4])
        self.assertEqual([x["seed"] for x in d["per_seed"]], seeds)
        self.assertEqual(d["per_seed_summary"]["seeds_positive"], 2)
        self.assertTrue(all("p" not in g for g in d["by_length_tertile"]))
        lengths = {"a": 3.0, "b": 9.0, "c": 1.0, "d": 5.0, "e": 7.0, "f": 2.0}
        self.assertEqual(V.length_tertiles(lengths), [["c", "f"], ["a", "d"], ["e", "b"]])
        sens = V.score_sensitivity({(a, "MAPPO", f["fold"], s): sealed[(a, "MAPPO", f["fold"], s)]
                                    for a in ("allpos", "NoHistory") for f in folds for s in seeds}, folds, seeds)
        self.assertIn("family_1_descriptive", sens)
        text = "\n".join(V.report({"main": res, "sensitivity": {"payoff_permuted": sens}, "tune": V.score_tune(
            {(c, a, f["fold"], s): rows(f, 3.0) for c in R.GRID for a in ("allpos", "NoHistory") for f in folds for s in [0, 1, 2]},
            {a: {f["fold"]: {"chosen": R.DEFAULT_NAME} for f in folds} for a in ("allpos", "NoHistory")},
            folds, [0, 1, 2], list(R.GRID), R.DEFAULT_NAME)}))
        self.assertIn("engaged fraction allpos - NoHistory", text)
        self.assertIn("per training seed", text)
        self.assertIn("Sensitivity payoff_permuted, descriptive", text)
        tune = {(c, a, f["fold"], s): rows(f, 5.0 if (a == "allpos" and c == "lr1e-03_ep15") else 3.0)
                for c in R.GRID for a in ("allpos", "NoHistory") for f in folds for s in [0, 1, 2]}
        sel = {a: {f["fold"]: {"chosen": "lr1e-03_ep15" if a == "allpos" else R.DEFAULT_NAME} for f in folds}
               for a in ("allpos", "NoHistory")}
        t = V.score_tune(tune, sel, folds, [0, 1, 2], list(R.GRID), R.DEFAULT_NAME)
        self.assertAlmostEqual(t["means_tuned"]["allpos"], 5.0)
        self.assertAlmostEqual(t["family_H"][0]["mean"], 2.0)
        self.assertEqual(len(t["allpos_minus_NoHistory_by_setting"]), 9)

    def test_the_opening_checks_every_cell_including_its_payoff_table(self):
        key = ("payoff_permuted", R.DEFAULT_NAME, "allpos", "F1", 3, "MAPPO")
        cfg = R.setting("payoff_permuted")
        good = {"protocol": "CL-D1.0", "study": "payoff_permuted", "config": R.DEFAULT_NAME, "hp": dict(R.DEFAULT),
                "arm": "allpos", "learner": "MAPPO", "test_seed": R.TEST_SEED + 3, "eval_repeats": R.EVAL_REPEATS,
                "env_config": cfg.to_dict(), "payoff_sha256": R.table_sha("payoff_permuted")}
        self.assertTrue(V.cell_matches(good, key, cfg))
        self.assertFalse(V.cell_matches({**good, "payoff_sha256": R.table_sha("main")}, key, cfg))
        self.assertFalse(V.cell_matches({k: v for k, v in good.items() if k != "payoff_sha256"}, key, cfg))
        self.assertFalse(V.cell_matches({**good, "test_seed": R.TEST_SEED}, key, cfg))

    def test_static_and_fixed_are_fitted_on_training_runs_only(self):
        asked, orig = [], C.runs

        def spy(fold, split):
            asked.append(split)
            return orig(fold, split)
        C.runs = spy
        try:
            ch = V.fit_static_fixed(FOLDS[0], env.EnvConfig(reward="proposal"), joints=[(0, 0, 0, 0), (1, 1, 0, 0)])
        finally:
            C.runs = orig
        self.assertEqual(set(asked), {"train"})
        self.assertIn(ch["static"], range(1, 6))

    def test_reference_policies_use_the_arms_test_episodes(self):
        f, cfg = FOLDS[0], env.EnvConfig(reward="proposal")
        rr = V.reference_rows(f, 3, 2, cfg, {"static": 1, "fixed": [1, 0, 0, 0]})
        want = C.specs(C.runs(f, "test"), R.TEST_SEED + 3, 2)
        self.assertEqual([r["run"] for r in rr["none"]], [s.run_id for s in want])
        self.assertEqual(set(rr), {"none", "random", "greedy", "planner", "clairvoyant", "static", "fixed"})

    def test_the_opening_refuses_until_every_study_is_ready(self):
        if S.SPEC.exists():
            self.skipTest("frozen: the real refusal path is exercised by the protocol run")
        r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "evaluate_cl.py"), "--open-test"],
                           capture_output=True, text=True, timeout=600)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not frozen", r.stdout + r.stderr)


class CLSpecAndDriver(unittest.TestCase):
    def test_spec_pins_every_file_and_cl10s_records(self):
        for rel in S.FILES:
            self.assertTrue((REPO / rel).exists(), rel)
        self.assertIn("camlds_real_full_arch/SPEC_D1.json", S.FILES)
        n = len(list((REPO / S.RECORDS).glob("*/*/s*/result.json")))
        self.assertEqual(n, 200)
        self.assertNotEqual(S.records_digest(), "missing")

    def test_freeze_and_check(self):
        orig = S.SPEC
        with tempfile.TemporaryDirectory() as tmp:
            S.SPEC = Path(tmp) / "SPEC_CL_D1.json"
            try:
                S.freeze("2026-11-18")
                self.assertTrue(S.check())
                with self.assertRaises(SystemExit):
                    S.freeze("2026-11-18")
                spec = json.loads(S.SPEC.read_text(encoding="utf-8"))
                spec["sha256"]["casinolimit_d1/run_cl.py"] = "0" * 64
                S.SPEC.write_text(json.dumps(spec), encoding="utf-8")
                self.assertFalse(S.check())
            finally:
                S.SPEC = orig

    def test_driver_order_and_only_open_opens(self):
        import run_all_cl as D
        self.assertEqual(D.STUDIES, R.STUDIES)
        for stage in ("diagnostics", "run"):
            self.assertFalse(any("--open-test" in " ".join(c) for _, c, _ in D.plan(stage, "cuda") if c))
        opens = [c for _, c, _ in D.plan("open", "cuda") if c]
        self.assertEqual(len(opens), 1)
        labels = [l for l, _, _ in D.plan("run", "cuda")]
        idx = lambda k: next(i for i, l in enumerate(labels) if l.startswith(k))
        self.assertLess(idx("validity gate"), idx("preflight"))
        self.assertLess(idx("preflight"), idx("main: cells"))
        for s in R.STUDIES:
            self.assertLess(idx(f"{s}: cells"), idx(f"{s}: validation dry run"))

    def test_driver_stops_at_the_first_failure(self):
        import run_all_cl as D
        ok = [sys.executable, "-c", "print('step one ran')"]
        fail = [sys.executable, "-c", "import sys; print('step two fails'); sys.exit(3)"]
        never = [sys.executable, "-c", "print('STEP THREE MUST NOT RUN')"]
        orig_plan, orig_out = D.plan, D.OUT
        with tempfile.TemporaryDirectory() as tmp:
            D.OUT = Path(tmp)
            D.plan = lambda stage, device: [("one", ok, None), ("two", fail, None), ("three", never, None)]
            argv = sys.argv
            sys.argv = ["run_all_cl.py", "run", "--device", "cpu"]
            try:
                with self.assertRaises(SystemExit) as cm:
                    D.main()
            finally:
                sys.argv, D.plan, D.OUT = argv, orig_plan, orig_out
            self.assertEqual(cm.exception.code, 1)
            text = next((Path(tmp) / "logs").glob("run_*.log")).read_text(encoding="utf-8")
            self.assertIn("STOPPED at [2/3] two: exit code 3", text)
            self.assertNotIn("STEP THREE MUST NOT RUN", text)

    def test_open_waits_for_every_dry_run(self):
        import run_all_cl as D
        orig = D.OUT
        with tempfile.TemporaryDirectory() as tmp:
            D.OUT = Path(tmp)
            try:
                self.assertEqual(D._open_pre()[0], "skip")
                for s in D.STUDIES:
                    (Path(tmp) / s).mkdir()
                    (Path(tmp) / s / "DRY_RUN_VALIDATION.json").write_text(json.dumps({"pass": True}), encoding="utf-8")
                self.assertIsNone(D._open_pre())
                (Path(tmp) / "TEST_OPENED.json").write_text("{}", encoding="utf-8")
                self.assertEqual(D._open_pre()[0], "skip")
            finally:
                D.OUT = orig

    def test_protocol_states_the_key_facts(self):
        text = (HERE / "PROTOCOL_CL_D1.0.md").read_text(encoding="utf-8")
        for s in ("870", "350", "250", "270", "114", "ATT&CK v15.1", "README_NOT_PROTOCOL.md", "no protection outcome",
                  "20261122", "previously exposed", "simulated engaged-command counts", "stop rule"):
            self.assertIn(s, text)


if __name__ == "__main__":
    unittest.main()
