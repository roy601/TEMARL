# -*- coding: utf-8 -*-
"""Protocol CL-D1.0: the CasinoLimit deception world.

D1.0's environment (camlds_real_full_arch/env_cmd.py), learner (camlds_real_full_arch/mappo_cmd.py)
and reference policies (Temarl_Test_v1_L1/baselines_cmd.py) are loaded UNCHANGED: each file must be
byte-identical (after CRLF -> LF) to the version pinned in D1.0's SPEC_D1.json, or nothing runs. Only
their inputs differ, supplied when each file is loaded:

  labels   CasinoLimit's 66 parent techniques (casinolimit_real/out/vocab.json), not CAM-LDS's 81
  payoff   D1.0's rule (d3fend_payoff: four constants and the PRIMARY / ADJACENT tactic sets) applied
           to each technique's tactic: the frozen vocabulary's tactic for the 45 techniques it has (rows
           identical to D1.0's), and ATT&CK v15.1's tactic for the other 21 (each has exactly one)
  zones    the four CasinoLimit machines start, bastion, meet, intranet; one agent each
  goals    none: CasinoLimit records no attacker goal, so no command is a goal command and there is no
           protection outcome (P1); there is no target zone
  entry    start (113 of the 114 attackers begin there; with recorded movement the entry only sets the
           zone before the first command)

This is how CL 1.0 reused the frozen encoder (cl_port sets NT in the frozen modules): the code is
D1.0's, the data are CasinoLimit's. Import this module first in a CasinoLimit process: it registers the
CasinoLimit environment as `env_cmd`, where the learner looks for it, and it refuses to load if
CAM-LDS's env_cmd, learner or reference policies are already loaded in the process.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
for _name in ("env_cmd", "mappo_cmd", "baselines_cmd"):
    if _name in sys.modules and not getattr(sys.modules[_name], "CL_WORLD", False):
        raise RuntimeError(f"{_name} (CAM-LDS) is already loaded in this process: run CasinoLimit in its own process")

sys.path.insert(0, str(REPO / "casinolimit_encoder"))
import cl_port as CP  # noqa: E402  (checks the corpus; frozen encoder modules with NT = 66)
import cl_data as CD  # noqa: E402
import _frozen  # noqa: E402,F401  (Temarl_Test_v1_L1: verifies and puts the frozen v2 modules on sys.path)
import d3fend_payoff as DP  # noqa: E402
import vocab_v2 as VOC  # noqa: E402

D10_SPEC = REPO / "camlds_real_full_arch" / "SPEC_D1.json"
FROZEN = {"env_cmd": "camlds_real_full_arch/env_cmd.py",
          "mappo_cmd": "camlds_real_full_arch/mappo_cmd.py",
          "baselines_cmd": "Temarl_Test_v1_L1/baselines_cmd.py"}
ATTACK_PATH = HERE / "attack_v15_1_tactics.json"
MACHINES = ("start", "bastion", "meet", "intranet")
SCENARIO = "casinolimit"
W = CD.W                                   # 16, the encoder's window (CL 1.0)
MAX_STEPS = 512                            # normaliser only (t / MAX_STEPS), >= the longest run (482);
                                           #   D1.0 passes 64 for a longest run of 42
LABELS, NT, LABEL_ID = CP.LABELS, CP.NT, CP.LABEL_ID


def verify_frozen():
    """Every reused D1.0 file must equal its SPEC_D1.json pin."""
    pinned = json.loads(D10_SPEC.read_text(encoding="utf-8"))["sha256"]
    bad = [rel for rel in FROZEN.values() if CP.sha_lf(str(REPO / rel)) != pinned[rel]]
    if bad:
        raise RuntimeError(f"not the frozen D1.0 files: {bad}. Restore them; do not bypass this check.")


verify_frozen()
ATTACK = json.loads(ATTACK_PATH.read_text(encoding="utf-8"))
if list(ATTACK["techniques"]) != LABELS:
    raise RuntimeError("attack_v15_1_tactics.json does not list CasinoLimit's 66 techniques in order")


def tactic_table() -> dict:
    """technique -> its tactic and where the tactic comes from."""
    out = {}
    for t in LABELS:
        if t in VOC.TECHNIQUES:
            out[t] = {"tactic": VOC.TECHNIQUES[t]["tactic"], "source": "D1.0 frozen vocabulary (vocab_v2)"}
        else:
            tac = ATTACK["techniques"][t]["tactics"]
            if len(tac) != 1:
                raise RuntimeError(f"{t}: {len(tac)} ATT&CK tactics; the protocol expects exactly one")
            out[t] = {"tactic": tac[0], "source": "ATT&CK v15.1"}
    return out


TACTICS = tactic_table()


def build_payoff() -> np.ndarray:
    """d3fend_payoff.build_payoff's rule, row by row, over CasinoLimit's labels."""
    A = np.full((NT, DP.N_ACTIONS), DP.W_OTHER, dtype=np.float64)
    A[:, 0] = DP.W_NULL
    for i, t in enumerate(LABELS):
        tac = TACTICS[t]["tactic"]
        for ai, act in enumerate(DP.ACTIONS):
            if ai == 0:
                continue
            if tac in DP.PRIMARY[act]:
                A[i, ai] = DP.W_PRIMARY
            elif tac in DP.ADJACENT[act]:
                A[i, ai] = DP.W_ADJACENT
    return A


PAYOFF = build_payoff()
PERMUTE_SEED = 20261122                    # Section 8, payoff_permuted: declared before the freeze


def _best(row) -> list:
    """The best decoy(s) of a payoff row (action indices 1-5)."""
    return sorted(int(j) + 1 for j in np.flatnonzero(np.isclose(row[1:], row[1:].max())))


def permuted_payoff(seed: int = PERMUTE_SEED):
    """Section 8 sensitivity `payoff_permuted`: for each tactic (sorted by name), one permutation of the 5
    decoy columns from a generator seeded with `seed`, redrawn until the tactic's best decoy changes
    (a tactic whose row is constant, Resource Development, keeps its first draw: it has no best decoy).
    The permutation is applied to every technique of that tactic. Each row keeps its multiset of values
    and its 'none' column, and techniques of one tactic still share a best decoy; only which decoy suits
    which tactic changes. Returns (table, {tactic: {"permutation", "draws", "best_before", "best_after"}})."""
    rng = np.random.default_rng(seed)
    first_row = {}
    for i, t in enumerate(LABELS):
        first_row.setdefault(TACTICS[t]["tactic"], i)
    perms, info = {}, {}
    for tac in sorted(first_row):
        row, draws = PAYOFF[first_row[tac]], 0
        constant = len(_best(row)) == DP.N_ACTIONS - 1
        while True:
            p, draws = rng.permutation(DP.N_ACTIONS - 1), draws + 1
            if constant or _best(row[np.r_[0, 1 + p]]) != _best(row):
                break
        perms[tac] = p
        info[tac] = {"permutation": [int(x) + 1 for x in p], "draws": draws, "best_before": _best(row),
                     "best_after": _best(row[np.r_[0, 1 + p]])}
    A = PAYOFF.copy()
    for i, t in enumerate(LABELS):
        A[i, 1:] = PAYOFF[i, 1 + perms[TACTICS[t]["tactic"]]]
    return A, info


PAYOFF_PERMUTED, PERMUTATION_INFO = permuted_payoff()


def table_sha256(table: np.ndarray) -> str:
    import hashlib
    return hashlib.sha256(np.ascontiguousarray(table, np.float64).tobytes()).hexdigest()


def _module(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    return m


def _exec(name: str, rel: str, inputs: dict):
    """Load REPO/rel as module `name` (registered in sys.modules) with `inputs` standing in for the
    modules it imports; the real modules are put back afterwards."""
    saved = {k: sys.modules.get(k) for k in inputs}
    sys.modules.update(inputs)
    try:
        spec = importlib.util.spec_from_file_location(name, str(REPO / rel))
        mod = importlib.util.module_from_spec(spec)
        mod.CL_WORLD = True
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod


_port = _module("port", NT=NT, LABELS=list(LABELS))
_vocab = _module("vocab_v2", TECHNIQUES={t: {"id": i, "tactic": TACTICS[t]["tactic"]} for i, t in enumerate(LABELS)})
_payoff = _module("d3fend_payoff", ACTIONS=list(DP.ACTIONS), N_ACTIONS=DP.N_ACTIONS, PAYOFF=PAYOFF)
_zones = _module("env_v2", ZONES=list(MACHINES), DEFENDED_ZONES=list(range(len(MACHINES))))

env = _exec("env_cmd", FROZEN["env_cmd"], {"port": _port, "vocab_v2": _vocab, "d3fend_payoff": _payoff, "env_v2": _zones})
META = {SCENARIO: {"entry": env.POS_ID["start"], "target": -1, "target_raw": None, "goal_tactic": None,
                   "goal_declared": None, "goal_mask": None, "goal_label_count": None, "p1": False}}


def scenario_metadata(version: str = "d1") -> dict:
    """CasinoLimit's one scenario: entry start, no target zone, no goal (replaces env_cmd's CAM-LDS table)."""
    if version != "d1":
        raise ValueError("CasinoLimit has one scenario metadata version ('d1')")
    return {k: dict(v) for k, v in META.items()}


env.scenario_metadata = scenario_metadata
marl = _exec("mappo_cmd", FROZEN["mappo_cmd"], {"port": _port, "d3fend_payoff": _payoff})
B = _exec("baselines_cmd", FROZEN["baselines_cmd"], {"d3fend_payoff": _payoff})

# the loaded files must have taken CasinoLimit's inputs, and nothing else
assert env.NT == marl.NT == NT == 66 and env.LABELS == list(LABELS)
assert np.array_equal(env.PAYOFF, PAYOFF)
assert env.POSITIONS == [*MACHINES, "Firewall"] and env.AGENT_ZONE == [0, 1, 2, 3] and env.N_AGENTS == 4
assert marl.N_ACTIONS == env.N_ACTIONS == 6 and marl.LOCAL_DIM == env.LOCAL_DIM and marl.GLOBAL_DIM == env.GLOBAL_DIM
assert B.CommandEngagementEnv is env.CommandEngagementEnv and marl.CommandEngagementEnv is env.CommandEngagementEnv
assert sys.modules["env_cmd"] is env


def folds():
    """The 5 CL 1.0 folds (casinolimit_encoder/cl_split.py), main condition."""
    return CD.folds("main")


def runs(fold: dict, split: str) -> list:
    """The fold's runs of one split, as env_cmd.make_spec reads them. Command order is exec_index (as the
    encoder's windows); positions are the recorded machines; no command is a goal command."""
    seqs = CD.sequences(fold["_steps"], fold[split + "_runs"])
    out = []
    for r, q in seqs.items():
        out.append({"id": r, "scenario": SCENARIO, "group": fold["fold"],
                    "commands": tuple(tuple(sorted(LABEL_ID[t] for t in s["techniques_parent"])) for s in q),
                    "positions": [s["machine"] for s in q], "goal": [False] * len(q)})
    return out


def all_runs() -> list:
    out = {}
    for f in folds():
        for split in ("train", "val", "test"):
            for r in runs(f, split):
                out[r["id"]] = r
    return [out[k] for k in sorted(out)]


def specs(rs, seed: int, repeats: int, cfg=None) -> list:
    """Every run `repeats` times, uniforms from one generator seeded with `seed` (as run_d1.specs)."""
    rng = np.random.default_rng(seed)
    meta = scenario_metadata()
    return [env.make_spec(r, rng, meta) for r in rs for _ in range(repeats)]
