# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- command-level replay deception environment
================================================================
Four defender agents, one per defended zone, deploy D3FEND decoys against an
attacker that REPLAYS a recorded playbook. The mechanics (capacity coupling,
breadcrumb lures, shared exposure) are carried over from the previous study's
`env_marl.py`; three things change.

1. ONE COMMAND = ONE STEP
   Previously each technique LABEL consumed a step, so a single command
   annotated with 13 techniques produced 13 steps and up to 13 dwell. Dwell
   therefore counted label-steps, not attacker actions, and long label lists
   inflated it. Here a command is one step earning AT MOST ONE engagement
   reward, so dwell counts commands engaged.

   Dwell numbers are consequently NOT comparable with the previous study
   (which reported ~15 label-steps). Different unit, different quantity.

2. SET-BASED ENGAGEMENT
   A command carries a set of techniques, so its decoy compatibility must
   aggregate several payoff entries:

       max  (primary)     rho = phi * max_{tau in S} PAYOFF[tau, d]
       mean (sensitivity) rho = phi * mean_{tau in S} PAYOFF[tau, d]

   `max` is the primary assumption: a decoy engages if it is convincing for
   ANY technique the command attempts. `mean` is a separately trained
   sensitivity condition, never a post-hoc re-scoring. NEITHER is a measured
   real-world engagement probability; both are modelling assumptions.

3. REPLAY ONLY -- NO GENERATED ATTACKERS
   There is no Markov chain. An episode replays one recorded playbook. The
   defence may change where the attacker goes, whether it engages, and may end
   the episode early, but it can NEVER invent the next command or extend the
   sequence. An exhausted replay pool raises rather than resampling.

   Goal progress uses the goal tactic of the scenario, taken from the CAM-LDS
   reconstruction (the playbooks record no network zones). That provenance
   split is a limitation of the corpus, disclosed in the audit.

COMMON RANDOM NUMBERS
   Every uniform an episode needs is drawn up front into the `EpisodeSpec`, so
   two policies acting identically see identical outcomes and paired
   comparisons between arms are sharp.

OBSERVABILITY
   Agents see their own zone only, plus two infrastructure signals, plus the
   shared PAST-ONLY history embedding h. Future commands are never observable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import _frozen  # noqa: F401
from d3fend_payoff import ACTIONS, N_ACTIONS, PAYOFF
from env_v2 import DEFENDED_ZONES, ZONES
from vocab_v2 import NUM_TECHNIQUES as NT

N_ZONES = len(ZONES)
N_AGENTS = len(DEFENDED_ZONES)
AGENT_ZONE = list(DEFENDED_ZONES)
ZONE_AGENT = {z: i for i, z in enumerate(AGENT_ZONE)}
NULL = 0
LURES = (ACTIONS.index("decoy_credential"), ACTIONS.index("decoy_file"))

U_MOVE, U_LATERAL, U_ENGAGE, U_BURN, U_DEAD, U_WIRE = range(6)
N_U = 6

AGGREGATIONS = ("max", "mean")


@dataclass(frozen=True)
class EnvConfig:
    """Calibrated parameters, carried over from the previous study's
    architecture-blind calibration and frozen here."""
    beta: float = 0.2
    p_goal: float = 0.7
    p_stay: float = 0.8
    k_capacity: int = 2
    goal_steps: int = 1
    aggregation: str = "max"

    def __post_init__(self):
        if self.aggregation not in AGGREGATIONS:
            raise ValueError(f"aggregation must be one of {AGGREGATIONS}")

    def to_dict(self):
        return asdict(self)


@dataclass
class EpisodeSpec:
    """One recorded playbook plus its pre-drawn uniforms."""
    run_id: str
    scenario: str
    commands: Tuple[Tuple[int, ...], ...]   # per step: the command's label set
    u: np.ndarray                           # (N_U, horizon)
    entry: int
    target: int
    goal_mask: np.ndarray                   # (NT,) bool

    @property
    def horizon(self) -> int:
        return len(self.commands)


def command_payoff(labels: Sequence[int], action: int, how: str) -> float:
    """Aggregate PAYOFF over a command's technique set."""
    if action == NULL or not labels:
        return 0.0
    vals = PAYOFF[np.asarray(labels, np.int64), action]
    return float(vals.max() if how == "max" else vals.mean())


# ── scenario metadata (zones and goal tactic) ──────────────────────────────

def scenario_metadata() -> Dict[str, dict]:
    """Entry zone, target zone and goal tactic per scenario.

    Sourced from the CAM-LDS paper reconstruction, because the AttackBed
    playbooks annotate techniques and tactics but no network zones. This is
    the one place the study depends on the hand-reconstructed file, and the
    dependence is recorded in the audit rather than hidden.

    Disambiguation rules, declared here and applied uniformly:
      * a target zone that is not a defended zone maps to the entry zone
      * a parenthesised terminal tactic takes the text inside the parentheses
      * a slash-separated terminal tactic takes the FIRST listed tactic
    """
    import json
    import os
    from env_v2 import ZONES as _Z
    from vocab_v2 import tactic_of

    path = os.path.join(_frozen.DATA_DIR, "camlds_grounding.json")
    with open(path, encoding="utf-8") as f:
        scen = json.load(f)["scenarios"]
    zone_id = {z: i for i, z in enumerate(_Z)}

    out = {}
    for s in scen:
        entry = zone_id[s["entry_zone"]]
        raw_target = s["target_zone"]
        if raw_target in zone_id and zone_id[raw_target] in AGENT_ZONE:
            target = zone_id[raw_target]
        else:
            target = entry                      # rule 1
        declared = s["terminal_tactic"]
        if "(" in declared:                     # rule 2
            goal = declared[declared.index("(") + 1:declared.rindex(")")].strip()
        else:                                   # rule 3
            goal = declared.split("/")[0].strip()
        mask = np.array([tactic_of(i) == goal for i in range(NT)], bool)
        out[s["id"]] = {"entry": entry, "target": target, "target_raw": raw_target,
                        "goal_tactic": goal, "goal_declared": declared,
                        "goal_mask": mask, "goal_label_count": int(mask.sum())}
    return out


def make_spec(run: dict, rng: np.random.Generator,
              meta: Dict[str, dict]) -> EpisodeSpec:
    m = meta[run["scenario"]]
    cmds = tuple(run["commands"])
    return EpisodeSpec(run_id=run["id"], scenario=run["scenario"], commands=cmds,
                       u=rng.random((N_U, len(cmds))), entry=m["entry"],
                       target=m["target"], goal_mask=m["goal_mask"])


class ReplayPool:
    """Training episode source: samples recorded runs with replacement.

    Sampling a finite recorded pool is the only attacker behaviour in this
    study. Randomness selects WHICH recorded run to replay and the
    environment's own uniforms; it never alters a run's commands.
    """

    def __init__(self, runs: Sequence[dict], seed: int,
                 meta: Optional[Dict[str, dict]] = None):
        if not runs:
            raise ValueError("Replay pool is empty: no runs to replay")
        self.runs = list(runs)
        self.rng = np.random.default_rng(seed)
        self.meta = meta or scenario_metadata()

    def next(self) -> EpisodeSpec:
        r = self.runs[int(self.rng.integers(len(self.runs)))]
        return make_spec(r, self.rng, self.meta)


def evaluation_specs(runs: Sequence[dict], repeats: int, seed: int,
                     meta: Optional[Dict[str, dict]] = None):
    """Every run, `repeats` times, with matched uniforms across policies.

    Repeats add simulation variance only. They are NOT additional attack
    campaigns and must never be treated as independent samples.
    """
    meta = meta or scenario_metadata()
    rng = np.random.default_rng(seed)
    specs, labels = [], []
    for r in runs:
        for rep in range(repeats):
            specs.append(make_spec(r, rng, meta))
            labels.append({"run": r["id"], "scenario": r["scenario"],
                           "group": r["group"], "environment_repeat": rep})
    return specs, labels


# ── observation layout (local, per agent) ──────────────────────────────────
O_AGENT = 0
O_SIGHTED = O_AGENT + N_AGENTS
O_TECH = O_SIGHTED + 1                 # multi-hot: the command just executed
O_MYDECOY = O_TECH + NT
O_MYENGAGED = O_MYDECOY + N_ACTIONS
O_WIRED = O_MYENGAGED + 1
O_MYCOMP = O_WIRED + 1
O_LOAD = O_MYCOMP + 1
O_STEP = O_LOAD + 1
LOCAL_DIM = O_STEP + 1

# ── global state layout (centralised critic only) ──────────────────────────
S_ZONE = 0
S_TECH = S_ZONE + N_ZONES
S_DECOYS = S_TECH + NT
S_BURNED = S_DECOYS + N_AGENTS * N_ACTIONS
S_PROGRESS = S_BURNED + 1
S_COMP = S_PROGRESS + 1
S_LOAD = S_COMP + N_ZONES
S_PENDING = S_LOAD + 1
S_STEP = S_PENDING + N_ZONES
S_REMAIN = S_STEP + 1
GLOBAL_DIM = S_REMAIN + 1


class CommandEngagementEnv:
    """One replayed playbook at a time."""

    def __init__(self, cfg: EnvConfig = EnvConfig(), max_steps: int = 64):
        self.cfg = cfg
        self.max_steps = max_steps          # normalisation only, not a cap
        self.spec: Optional[EpisodeSpec] = None
        self.done = True

    def reset(self, spec: EpisodeSpec):
        self.spec = spec
        self.zone = spec.entry
        self.target = spec.target
        self.goal_mask = spec.goal_mask
        self.t = 0
        self.burned = False
        self.pending = -1
        self.decoys = np.zeros(N_AGENTS, np.int64)
        self.my_engaged = np.zeros(N_AGENTS, bool)
        self.compromised = np.zeros(N_ZONES, np.float32)
        self.load = 0
        self.progress = 0
        self.cur_cmd: Tuple[int, ...] = ()
        self.done = False
        self.objective = False
        self._chain_open = False
        self.dwell = 0
        self.depth_set = set()
        self.st = {"capacity_violations": 0, "lure_engagements": 0,
                   "lure_chains": 0, "dead_ends": 0, "decoys_deployed": 0,
                   "engaged_in_target": 0, "exposed_at": -1,
                   "labels_engaged": 0}
        return self

    def _move(self, u_move: float, u_lat: float) -> int:
        cur, tgt = self.zone, self.target
        if cur == tgt:
            if u_move < self.cfg.p_stay:
                return cur
            cands = [z for z in AGENT_ZONE if z != cur]
        else:
            if u_move < self.cfg.p_goal:
                return tgt
            cands = [z for z in AGENT_ZONE if z != tgt]
        if not cands:
            return cur
        return cands[min(int(u_lat * len(cands)), len(cands) - 1)]

    def peek_next_zone(self) -> int:
        """Where the attacker will be next step. Clairvoyant baselines only."""
        if self.pending >= 0:
            return self.pending
        u = self.spec.u[:, self.t]
        return self._move(u[U_MOVE], u[U_LATERAL])

    def peek_next_command(self) -> Tuple[int, ...]:
        """The next command's label set. Clairvoyant baselines only."""
        return self.spec.commands[self.t]

    def step(self, actions: Sequence[int]):
        if self.done:
            raise RuntimeError("step() on a finished episode; call reset()")
        acts = np.asarray(actions, np.int64)
        if acts.shape != (N_AGENTS,) or acts.min() < 0 or acts.max() >= N_ACTIONS:
            raise ValueError(f"bad joint action {actions}")
        t = self.t
        labels = self.spec.commands[t]
        u = self.spec.u[:, t]
        cfg = self.cfg

        n_active = int((acts != NULL).sum())
        phi = 1.0 if n_active <= cfg.k_capacity else cfg.k_capacity / n_active

        followed = self.pending >= 0
        nz = self.pending if followed else self._move(u[U_MOVE], u[U_LATERAL])
        self.pending = -1
        self.zone = nz
        ag = ZONE_AGENT[nz]
        d = int(acts[ag])

        engaged = exposed = False
        wired = -1
        rho = 0.0
        if d != NULL and not self.burned:
            rho = phi * command_payoff(labels, d, cfg.aggregation)
            if u[U_ENGAGE] < rho:
                engaged = True
                if u[U_BURN] < cfg.beta * (1.0 - rho):
                    exposed = True
                if d in LURES:
                    self.st["lure_engagements"] += 1
                    partners = [z for z in AGENT_ZONE
                                if z != nz and acts[ZONE_AGENT[z]] != NULL]
                    if partners:
                        wired = partners[min(int(u[U_WIRE] * len(partners)),
                                             len(partners) - 1)]
                    else:
                        self.st["dead_ends"] += 1
                        if u[U_DEAD] < cfg.beta:
                            exposed = True
        if exposed:
            self.burned = True
            wired = -1
            self.st["exposed_at"] = t

        if engaged:
            # ONE command, ONE engagement step, ONE unit of reward -- however
            # many technique labels the command carries.
            self.dwell += 1
            self.depth_set.update(labels)
            self.st["labels_engaged"] += len(labels)
            if nz == self.target:
                self.st["engaged_in_target"] += 1
            if followed and self._chain_open:
                self.st["lure_chains"] += 1
        else:
            self.compromised[nz] = 1.0
            if nz == self.target and bool(self.goal_mask[list(labels)].any()):
                self.progress += 1

        self._chain_open = wired >= 0
        if wired >= 0:
            self.pending = wired

        self.decoys = acts.copy()
        self.my_engaged[:] = False
        if engaged:
            self.my_engaged[ag] = True
        self.load = n_active
        self.cur_cmd = labels
        self.st["decoys_deployed"] += n_active
        if n_active > cfg.k_capacity:
            self.st["capacity_violations"] += 1
        self.t += 1

        if self.progress >= cfg.goal_steps:
            self.objective = True
            self.done = True
        elif self.t >= self.spec.horizon:
            self.done = True

        info = {"engaged": engaged, "exposed": exposed, "zone": nz,
                "labels": labels, "rho": rho, "phi": phi, "wired": wired,
                "followed": followed}
        return (1.0 if engaged else 0.0), self.done, info

    def local_obs(self, out: Optional[np.ndarray] = None) -> np.ndarray:
        """(N_AGENTS, LOCAL_DIM) -- strictly local, strictly past."""
        o = np.zeros((N_AGENTS, LOCAL_DIM), np.float32) if out is None else out
        if out is not None:
            o[:] = 0.0
        for i, z in enumerate(AGENT_ZONE):
            o[i, O_AGENT + i] = 1.0
            if self.zone == z:
                o[i, O_SIGHTED] = 1.0
                for tau in self.cur_cmd:
                    o[i, O_TECH + tau] = 1.0
            o[i, O_MYDECOY + int(self.decoys[i])] = 1.0
            o[i, O_MYENGAGED] = float(self.my_engaged[i])
            o[i, O_WIRED] = 1.0 if self.pending == z else 0.0
            o[i, O_MYCOMP] = self.compromised[z]
            o[i, O_LOAD] = self.load / self.cfg.k_capacity
            o[i, O_STEP] = self.t / self.max_steps
        return o

    def global_state(self, out: Optional[np.ndarray] = None) -> np.ndarray:
        g = np.zeros(GLOBAL_DIM, np.float32) if out is None else out
        if out is not None:
            g[:] = 0.0
        g[S_ZONE + self.zone] = 1.0
        for tau in self.cur_cmd:
            g[S_TECH + tau] = 1.0
        for i in range(N_AGENTS):
            g[S_DECOYS + i * N_ACTIONS + int(self.decoys[i])] = 1.0
        g[S_BURNED] = float(self.burned)
        g[S_PROGRESS] = self.progress / self.cfg.goal_steps
        g[S_COMP:S_COMP + N_ZONES] = self.compromised
        g[S_LOAD] = self.load / self.cfg.k_capacity
        if self.pending >= 0:
            g[S_PENDING + self.pending] = 1.0
        g[S_STEP] = self.t / self.max_steps
        g[S_REMAIN] = (self.spec.horizon - self.t) / self.max_steps
        return g

    def history_window(self, window: int):
        """PAST-ONLY command history, as the encoder's (W, NT) multi-hot.

        Only commands with index < t are included, so no future information
        can reach a policy. Left-padded, matching `command_data.windows`.
        """
        hist = self.spec.commands[max(0, self.t - window):self.t]
        x = np.zeros((window, NT), np.float32)
        m = np.zeros(window, np.float32)
        start = window - len(hist)
        for k, c in enumerate(hist):
            x[start + k, list(c)] = 1.0
            m[start + k] = 1.0
        return x, m

    def episode_stats(self) -> Dict[str, float]:
        return {"dwell": float(self.dwell),
                "depth": float(len(self.depth_set)),
                "protected": float(not self.objective),
                "exposed": float(self.burned),
                "length": float(self.t),
                "horizon": float(self.spec.horizon),
                "run": self.spec.run_id,
                "scenario": self.spec.scenario,
                **{k: float(v) for k, v in self.st.items()}}


def run_episode(env: CommandEngagementEnv, spec: EpisodeSpec, policy):
    """Roll one episode with `policy(env) -> joint action` (baselines)."""
    env.reset(spec)
    if hasattr(policy, "begin"):
        policy.begin(env)
    while not env.done:
        env.step(policy(env))
    return env.episode_stats()
