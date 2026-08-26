# simulation_env_fixed.py
"""
File 2 of 8 — Simulation Environment (FIXED VERSION)
======================================================
Purpose: Simulates the 12-node Hawkeyes network with 4 honeypot agents
         and an attacker progressing through MITRE ATT&CK techniques.

Fixes applied:
  Fix 2 — Proactive alignment reward with t-1 timeline.
          step() now accepts predicted_technique parameter.
          _compute_reward() computes r5 proactive bonus by comparing
          prev_predicted_technique (from t-1) with actual current technique
          AND agent actions (Option B: reward successful USE of prediction).
  Fix 4 — Rebalanced reward weights.
          Thesis model:  R = 0.2*r1 + 0.15*r2 + 0.1*r3 + 0.05*r4 + 0.5*r5
          NoTrans:       R = 0.3*r1 + 0.40*r2 + 0.2*r3 + 0.1*r4

Key differences from Hawkeyes faithful reproduction:
  - Behavioral action space (5 actions) instead of node-placement actions
  - Attacker sequence tracked as list of technique IDs → fed to Transformer
  - State = 374-dim = 310 (Hawkeyes M_com+M_con+M_vul) + 64 (h from Transformer)

Network: Same 12-node Hawkeyes topology (Figure 8, Table 2)
         4 subnets, DBServer as critical node
         Entry nodes: Tablet, Host1, WebServer

VOCAB NOTE (post real-data expansion):
  The MITRE vocabulary was expanded from 22 to 25 tokens (NUM_TECHNIQUES=23)
  to support the real-data COMISET pipeline. The SIMULATION, however, models
  attacker behavior over the ORIGINAL 20 kill-chain techniques (ids 0-19), to
  remain consistent with the models trained before the expansion. The attacker
  samplers below are capped at SIM_NUM_TECHNIQUES=20. ALIGNMENT_MATRIX is
  extended to 23 rows purely as a safety guard so any stray id cannot crash
  the reward lookup; rows 20-22 mirror the real-data pipeline matrix.

METRIC TRACKING (Step 1 fix — decoupled engagement / depth):
  engagement_length (Dwell Time):
      Operational cycles the attacker spends inside the environment.
      When agents pick a high-affinity action that matches the attacker's
      current technique, the attacker is caught in a deceptive feedback loop
      and the counter is advanced by (1 + 2*affinity_score) instead of 1.
      This means a well-decoyed attacker accrues MORE dwell time per step
      than one who is ignored, naturally separating MARL from the static baseline.

  interaction_depth (Unique Techniques):
      Defined strictly as len(set(attacker_sequence)) — the count of
      DISTINCT MITRE ATT&CK techniques attempted during the episode.
      Repeated techniques during a honeypot stall do NOT increment this
      counter, breaking the 1-step == 1-depth coupling that caused duplication.

  Together these two counters satisfy the defensive-utility goal:
      • High-performing MARL: HIGH engagement_length, LOW/STALLED depth
      • Static baseline (no deception):  LOW engagement_length, HIGH depth
"""

import numpy as np
import random
import os
import json
from mitre_techniques import (
    TOKENS, ID_TO_TECHNIQUE, NUM_TECHNIQUES,
    PAD_ID, UNK_ID, VOCAB_SIZE, MAX_SEQ_LEN, TACTIC_TO_IDS
)

# Simulation operates on the original 20 kill-chain techniques only.
SIM_NUM_TECHNIQUES = 20

# Exfiltration technique IDs (techniques 15-17 in the kill-chain mapping).
# Used by Step 2 termination logic: an un-trapped attacker who attempts
# exfiltration is considered a successful escape.
# Only ACTUAL data egress counts as an escape. T1005 (Data from Local System) and
# T1560 (Archive Collected Data) are COLLECTION/staging — the data has not left the
# network — whereas T1041 (Exfiltration Over C2) is genuine egress. The previous
# set {15,16,17} ended the episode the moment an attacker merely staged data, which
# both mis-modelled MITRE semantics and made Collection-focused campaigns
# self-terminating (they could never express their behaviour).
EXFIL_TECHNIQUE_IDS = {17}           # T1041 Exfiltration Over C2 only

# ── Network Topology (12 nodes, same as Hawkeyes) ────────────────────────────

NODES = {
    0:  "Tablet",        # Entry node — Subnet 1
    1:  "Host1",         # Entry node — Subnet 1
    2:  "WebServer",     # Entry node — Subnet 2
    3:  "AppServer",     # Subnet 2
    4:  "FileServer",    # Subnet 2
    5:  "Host2",         # Subnet 3
    6:  "Host3",         # Subnet 3
    7:  "PrintServer",   # Subnet 3
    8:  "DBServer",      # CRITICAL — Subnet 4
    9:  "Honeypot1",     # Honeypot — Subnet 1
    10: "Honeypot2",     # Honeypot — Subnet 2
    11: "Honeypot3",     # Honeypot — Subnet 3
}

HONEYPOT_NODES = [9, 10, 11]
CRITICAL_NODE  = 8  # DBServer
ENTRY_NODES    = [0, 1, 2]

# ── Subnet Partition (Dec-POMDP local-observation mode) ──────────────────────
# Each of the 4 agents is assigned to one subnet and, in local_obs mode, can
# ONLY observe the nodes within its own subnet. Global attacker intent is then
# available exclusively through the shared Transformer vector h — making h
# mathematically non-redundant (unlike the fully-observable global mode, where
# every agent already sees the whole state and h adds nothing).
#
# Agent 3 guards Subnet 4 (the critical DBServer) and rarely sees the attacker
# directly until it is about to arrive; it must rely on h to pre-position,
# which is exactly what the proactive r5 reward pays for.
SUBNET_NODES = {
    0: [0, 1, 9],        # Subnet 1 — entry-side (Tablet, Host1, Honeypot1)
    1: [2, 3, 4, 10],    # Subnet 2 — web tier (WebServer, AppServer, FileServer, Honeypot2)
    2: [5, 6, 7, 11],    # Subnet 3 — internal tier (Host2, Host3, PrintServer, Honeypot3)
    3: [8],              # Subnet 4 — CRITICAL (DBServer)
}
MAX_SUBNET_NODES = 4   # padding width so every agent has a fixed-size local view

# ── Neighbor-subnet early-warning (observability fix) ─────────────────────────
# Each agent additionally observes a coarse, decayed "attacker was recently
# active in an adjacent subnet" signal — no exact node, no technique. This
# bridges the "h predicts WHAT technique but not WHERE" gap: a blind agent gets
# a faint directional cue and can pre-position selectively rather than hedging
# over all subnets. Realistic (SOCs see cross-segment alerts) and it AMPLIFIES
# the intent advantage — NoTrans still cannot act on it (it has no technique
# prediction), while an h-equipped agent can turn "attacker approaching" into
# the right pre-positioned response.
# REVERTED for the clean RAIF Stage A experiment. Retrain #5 showed this
# (bundled with calibration) collapsed the HiE/Mix flagship result. It is a
# Stage C candidate — and should be re-tested only as a LEARNED arrival head
# (SAG), not this hand-crafted decayed proxy. Set True only to reproduce #5.
USE_NEIGHBOR_WARNING = False
MAX_SUBNET_NEIGHBORS = 2      # max adjacent subnets any agent has (chain topology)
NEIGHBOR_DECAY       = 0.7    # per-step decay of the neighbor-activity signal
_NEIGHBOR_DIMS       = MAX_SUBNET_NEIGHBORS if USE_NEIGHBOR_WARNING else 0

# Reverse map: node_id -> the single agent responsible for it (its subnet owner).
# Used for CREDIT ASSIGNMENT in the reward: only the agent whose subnet contains
# the attacker's current node gets alignment credit for this step. Without this,
# scoring alignment as max() over ALL 4 agents' actions lets an agent in an
# unrelated subnet earn full credit for a lucky/generalist action that has
# nothing to do with actually engaging the attacker — which lets a static
# "diversify actions across agents" policy game the metric without any real
# prediction or localization, defeating the point of local observations.
NODE_TO_AGENT = {
    node_id: agent_id
    for agent_id, nodes in SUBNET_NODES.items()
    for node_id in nodes
}

# Local observation layout (per agent), fixed size regardless of subnet size:
#   own_compromise      : MAX_SUBNET_NODES            (binary, padded)
#   own_vulnerability   : MAX_SUBNET_NODES            (CVSS per own node, padded)
#   own_connectivity    : MAX_SUBNET_NODES^2          (local adjacency, padded)
#   attacker_present    : 1                           (1.0 if attacker in my subnet)
#   attacker_local_pos  : MAX_SUBNET_NODES            (one-hot within my subnet)
#   observed_technique  : NUM_TECHNIQUES              (one-hot; only if the technique
#                                                      was EXECUTED in my subnet)
LOCAL_STATE_DIM = (
    MAX_SUBNET_NODES            # own_compromise
    + MAX_SUBNET_NODES          # own_vulnerability
    + MAX_SUBNET_NODES ** 2     # own_connectivity
    + 1                         # attacker_present
    + MAX_SUBNET_NODES          # attacker_local_pos
    + NUM_TECHNIQUES            # observed_technique
    + _NEIGHBOR_DIMS            # neighbor-subnet early-warning (appended last)
)  # = 4 + 4 + 16 + 1 + 4 + 23 (+2 if neighbor warning) = 52 or 54

# Index of the attacker_present flag within the local state vector. The gated
# Q-network reads this as an explicit "am I currently sighted?" signal so it can
# learn to suppress h (trust local telemetry) when the attacker is in its own
# subnet and open to h (anticipate) when blind. Sits right after
# own_compromise(4) + own_vulnerability(4) + own_connectivity(16) = 24.
LOCAL_ATTACKER_PRESENT_IDX = 2 * MAX_SUBNET_NODES + MAX_SUBNET_NODES ** 2  # = 24

ADJACENCY = {
    0: [1, 9],
    1: [0, 2, 9],
    2: [1, 3, 10],
    3: [2, 4, 5],
    4: [3, 10],
    5: [3, 6, 11],
    6: [5, 7, 11],
    7: [6, 8],
    8: [7],       # DBServer — final target
    9: [0, 1],    # Honeypot1
    10: [2, 4],   # Honeypot2
    11: [5, 6],   # Honeypot3
}

# Subnet adjacency (which subnets border each other), derived from the node
# graph: subnet A borders subnet B if any node in A links to any node in B.
# Used for the neighbor-subnet early-warning signal. For the Hawkeyes chain
# topology this yields 0-1-2-3 (each agent has 1-2 neighbors).
SUBNET_ADJACENCY = {a: [] for a in SUBNET_NODES}
for _src, _nbrs in ADJACENCY.items():
    _sa = NODE_TO_AGENT.get(_src)
    for _dst in _nbrs:
        _da = NODE_TO_AGENT.get(_dst)
        if _sa is not None and _da is not None and _da != _sa and _da not in SUBNET_ADJACENCY[_sa]:
            SUBNET_ADJACENCY[_sa].append(_da)
for _a in SUBNET_ADJACENCY:
    SUBNET_ADJACENCY[_a] = sorted(SUBNET_ADJACENCY[_a])

NODE_CVSS = {
    0: 0.72, 1: 0.68, 2: 0.85, 3: 0.74, 4: 0.61,
    5: 0.69, 6: 0.71, 7: 0.58, 8: 0.90,
    9: 0.50, 10: 0.50, 11: 0.50  # Honeypots — neutral
}

# ── Behavioral Actions ────────────────────────────────────────────────────────

ACTIONS = {
    0: "minimal_response",
    1: "banner_modification",
    2: "fake_vulnerability",
    3: "credential_store",
    4: "data_exfil_bait",
}
N_ACTIONS = len(ACTIONS)
N_AGENTS  = 4
STATE_DIM = 310

# ── Alignment Matrix (23 × 5) ─────────────────────────────────────────────────
# Measures semantic fit between attacker technique and honeypot response.
# Values in [0.0, 1.0] — higher = better deception match.
# Rows 0-19: original kill-chain techniques (used by the simulation).
# Rows 20-22: real-data pipeline techniques (T1036/T1574/T1553) — included as a
#             safety guard and to keep one consistent matrix across sim and
#             real-data evaluation. The simulation attacker never samples these.

ALIGNMENT_MATRIX = np.array([
    # min   banner  fake_v  cred    exfil     Technique
    [0.1,   0.4,    1.0,    0.2,    0.3],   # 0  T1190 Exploit Public-Facing
    [0.1,   0.6,    0.7,    0.1,    0.1],   # 1  T1566 Phishing
    [0.2,   0.3,    0.5,    0.3,    0.4],   # 2  T1059 Command Interpreter
    [0.1,   0.5,    0.4,    0.2,    0.3],   # 3  T1204 User Execution
    [0.2,   0.3,    0.4,    0.4,    0.3],   # 4  T1053 Scheduled Task
    [0.1,   0.4,    0.5,    0.3,    0.3],   # 5  T1543 Create System Process
    [0.1,   0.5,    0.4,    0.3,    0.2],   # 6  T1547 Boot Autostart
    [0.1,   0.2,    0.8,    0.4,    0.3],   # 7  T1068 Exploit Priv Escalation
    [0.1,   0.2,    0.6,    0.5,    0.3],   # 8  T1055 Process Injection
    [0.2,   0.8,    0.5,    0.1,    0.2],   # 9  T1046 Network Scanning
    [0.2,   0.9,    0.4,    0.1,    0.1],   # 10 T1016 Network Config Discovery
    [0.2,   0.7,    0.6,    0.1,    0.2],   # 11 T1083 File/Dir Discovery
    [0.1,   0.5,    0.6,    0.7,    0.4],   # 12 T1021 Remote Services
    [0.1,   0.4,    0.5,    0.6,    0.4],   # 13 T1072 Software Deploy Tools
    [0.1,   0.3,    0.4,    0.9,    0.3],   # 14 T1550 Alt Auth Material
    [0.1,   0.2,    0.3,    0.5,    0.9],   # 15 T1005 Data from Local System
    [0.1,   0.2,    0.3,    0.4,    0.8],   # 16 T1560 Archive Collected Data
    [0.1,   0.1,    0.2,    0.3,    1.0],   # 17 T1041 Exfil Over C2
    [0.1,   0.2,    0.6,    0.3,    0.5],   # 18 T1486 Data Encrypted (Ransom)
    [0.2,   0.3,    0.5,    0.2,    0.4],   # 19 T1489 Service Stop
    [0.2,   0.5,    0.7,    0.4,    0.3],   # 20 T1036 Masquerading (Defense Evasion)
    [0.1,   0.4,    0.6,    0.5,    0.3],   # 21 T1574 Hijack Execution Flow (Persistence)
    [0.2,   0.6,    0.7,    0.3,    0.2],   # 22 T1553 Subvert Trust Controls (Defense Evasion)
], dtype=np.float32)  # shape: (23, 5)

# ── Attack Strategy Sequences ─────────────────────────────────────────────────

ATTACK_STRATEGIES = {
    "HiE": {   # High Exploit — favors vulnerability exploitation
        "weights": {
            "Initial Access":       [0.9, 0.1],
            "Execution":            [0.7, 0.3, 0.0],
            "Persistence":          [0.3, 0.5, 0.2],
            "Privilege Escalation": [0.9, 0.1],
            "Discovery":            [0.2, 0.3, 0.5],
            "Lateral Movement":     [0.4, 0.2, 0.4],
            "Collection":           [0.4, 0.6],
            "Exfiltration":         [1.0],
            "Impact":               [0.6, 0.4],
        }
    },
    "HiC": {   # High Credential — favors credential theft
        "weights": {
            "Initial Access":       [0.5, 0.5],
            "Execution":            [0.4, 0.4, 0.2],
            "Persistence":          [0.2, 0.3, 0.5],
            "Privilege Escalation": [0.3, 0.7],
            "Discovery":            [0.3, 0.4, 0.3],
            "Lateral Movement":     [0.3, 0.2, 0.5],
            "Collection":           [0.5, 0.5],
            "Exfiltration":         [1.0],
            "Impact":               [0.4, 0.6],
        }
    },
    "Ran": {   # Random — uniform over all techniques
        "weights": None  # uniform sampling
    },
    "Mix": {   # Mixed — balanced across all phases
        "weights": {
            "Initial Access":       [0.5, 0.5],
            "Execution":            [0.34, 0.33, 0.33],
            "Persistence":          [0.34, 0.33, 0.33],
            "Privilege Escalation": [0.5, 0.5],
            "Discovery":            [0.34, 0.33, 0.33],
            "Lateral Movement":     [0.34, 0.33, 0.33],
            "Collection":           [0.5, 0.5],
            "Exfiltration":         [1.0],
            "Impact":               [0.5, 0.5],
        }
    },
}

TACTIC_ORDER = [
    "Initial Access", "Execution", "Persistence", "Privilege Escalation",
    "Discovery", "Lateral Movement", "Collection", "Exfiltration", "Impact"
]

# ── HYBRID ATTACKER: COMISET-grounded Markov chain + latent campaign profiles ──
# WHY THIS EXISTS. The legacy strategies above set the tactic from
# min(len(attacker_sequence), 8) — i.e. the TACTIC IS A DETERMINISTIC FUNCTION OF
# THE STEP INDEX and techniques are drawn from fixed weights independent of
# history:  p(tau_t | history) = p(tau_t | t).  That process is MEMORYLESS given a
# counter, so there is nothing for a sequence model to learn. Measured on the
# legacy env: an oracle step-counter BEAT the Transformer on all four strategies
# (HiE .692 vs .557), and a linear probe recovered the step index from h with
# R^2 = 0.97-0.98, with h adding +0.000 once the step was known.
#
# THE FIX. Each episode samples a HIDDEN campaign profile c; techniques then
# follow a genuine Markov chain  tau_t ~ T_c[tau_{t-1}, .]  with NO dependence on
# the step index. Transitions among the 7 techniques attested in COMISET
# (Execution -> Persistence -> PrivEsc -> Lateral) are estimated from 6,268 real
# transitions; the profile-specific tails use a kill-chain prior. Profiles target
# tactics with DIFFERENT optimal deception actions (a2/a1/a3/a4), so inferring the
# hidden profile changes the correct response — which is precisely what makes
# intent modelling necessary rather than decorative.
#
# Validated properties (frozen before any training; see attacker_profiles.json):
#   counter accuracy 0.130  <<  bigram 0.299   (history gain +0.170)
#   decision headroom from knowing the profile : +0.0959
#   profile identifiable from a 3-step prefix  : ~0.94 (ambiguous at step 1)
_PROFILE_PATH        = os.path.join("results", "attacker_profiles.json")
HYBRID_PROFILES      = {}     # name -> (20, 20) row-stochastic transition matrix
HYBRID_INIT          = None   # initial technique distribution (shared by all profiles)
HYBRID_PROFILE_NAMES = []
try:
    with open(_PROFILE_PATH) as _f:
        _pdata = json.load(_f)
    HYBRID_PROFILES      = {n: np.asarray(m, dtype=np.float64)
                            for n, m in _pdata["T"].items()}
    HYBRID_INIT          = np.asarray(_pdata["init"], dtype=np.float64)
    HYBRID_PROFILE_NAMES = list(_pdata["profiles"].keys())
except (FileNotFoundError, KeyError, ValueError, TypeError):
    pass   # legacy strategies still work; hybrid modes raise if requested

# "Hybrid" samples a hidden profile per episode (the realistic setting the
# defender faces); the per-profile names force one profile for breakdowns.
HYBRID_MIXTURE = "Hybrid"


# ── Environment Class ─────────────────────────────────────────────────────────

class HoneypotEnv:
    """
    Honeypot deception environment.

    Observation space per agent: 374-dim
      - 310-dim: Hawkeyes network state (M_com + M_con + M_vul)
      - 64-dim:  Transformer hidden state h (injected externally each step)

    Action space per agent: Discrete(5) — behavioral responses

    Episode structure:
      - Attacker spawns at random entry node
      - Each step: attacker moves + performs technique
      - Agents observe and respond with behavioral action
      - Episode ends when attacker reaches DBServer, achieves un-trapped
        exfiltration (Step 2 failure condition), or max_steps reached.

    Metric tracking (decoupled — Step 1 fix):
      engagement_length : float
          Operational dwell time. Incremented by (1 + 2*affinity) when the
          best-aligned agent action matches the current technique (affinity >= 0.5),
          otherwise incremented by 1.  Repeated techniques during a stall
          naturally inflate this counter without advancing depth.

      interaction_depth : int
          len(set(attacker_sequence)) — count of UNIQUE techniques attempted.
          Repeated techniques (due to stalling) do NOT increase this value,
          breaking the 1-step == 1-depth coupling.
    """

    def __init__(self, attack_strategy="Mix", max_steps=200, n_agents=N_AGENTS,
                 local_obs=False):
        self.attack_strategy = attack_strategy
        self.max_steps       = max_steps
        self.n_agents        = n_agents
        self.n_nodes         = len(NODES)

        # Hybrid (COMISET-grounded Markov + latent profile) vs legacy strategies
        self._hybrid = (attack_strategy == HYBRID_MIXTURE
                        or attack_strategy in HYBRID_PROFILE_NAMES)
        if self._hybrid and not HYBRID_PROFILES:
            raise RuntimeError(
                f"attack_strategy='{attack_strategy}' needs {_PROFILE_PATH}, which was "
                f"not found. Build it before training (see attacker profile builder).")
        self._profile = None   # the hidden campaign profile for the current episode

        # local_obs=False → legacy fully-observable mode: every agent receives the
        #   full 310-dim global state ‖ h (backward compatible with old models).
        # local_obs=True  → Dec-POMDP mode: each agent sees only its own subnet
        #   (LOCAL_STATE_DIM) ‖ h; the mixer still receives the full global state
        #   centrally via get_global_state() (CTDE preserved).
        self.local_obs    = local_obs

        self.obs_dim_base = 310   # M_com(10) + M_con(100) + M_vul(200)
        self.h_dim        = 64
        self.agent_state_dim = LOCAL_STATE_DIM if local_obs else self.obs_dim_base
        self.obs_dim      = self.agent_state_dim + self.h_dim  # 116 (local) or 374 (global)

        self.reset()

    # ── Reset ──────────────────────────────────────────────────────────────

    def reset(self):
        """Reset environment. Returns initial observations (without h — h=zeros)."""
        self.attacker_node     = random.choice(ENTRY_NODES)
        self.attacker_sequence = []   # list of technique IDs performed so far

        # Sample the HIDDEN campaign profile for this episode. The defender never
        # observes it — it must be inferred from the technique sequence, which is
        # exactly the job the Transformer intent encoder exists to do.
        if self._hybrid:
            self._profile = (random.choice(HYBRID_PROFILE_NAMES)
                             if self.attack_strategy == HYBRID_MIXTURE
                             else self.attack_strategy)
        self.step_count        = 0
        self.done              = False
        self.attacker_trapped  = False

        # ── Step 1: decoupled metric accumulators ──────────────────────────
        # engagement_length (Dwell Time): floating-point; incremented by
        #   (1 + 2*affinity) on high-affinity stall steps, else by 1.
        self.engagement_length = 0.0

        # interaction_depth: integer; equals len(set(attacker_sequence))
        # at end of episode.  Tracked as a set internally.
        self._unique_techniques: set = set()

        self.compromised = set()
        self.compromised.add(self.attacker_node)
        self.honeypot_actions = [0] * self.n_agents

        self.h = np.zeros(self.h_dim, dtype=np.float32)

        # Fix 2: store previous-step Transformer prediction for proactive reward
        # At reset, there is no previous prediction — use None
        self.prev_predicted_technique = None

        # Local-obs bookkeeping: the technique just executed and the node it was
        # executed at, so an agent can observe the technique iff it happened in
        # its own subnet. None at reset (no activity yet).
        self._last_technique = None
        self._last_exec_node = None

        # Neighbor-warning: decayed per-subnet attacker-activity signal. Seed the
        # attacker's starting subnet so neighbors get an immediate faint cue.
        self._subnet_activity = {a: 0.0 for a in SUBNET_NODES}
        _start_sub = NODE_TO_AGENT.get(self.attacker_node)
        if _start_sub is not None:
            self._subnet_activity[_start_sub] = 1.0

        # Cache the base global state so get_global_state() is valid immediately
        # after reset and consistent with the observation just returned.
        self._last_base_state = self._build_base_state()

        return self._get_observations()

    # ── Step ───────────────────────────────────────────────────────────────

    def step(self, actions, h, predicted_technique=None):
        """
        Execute one environment step.

        Args:
            actions:               list of int, length n_agents — one action per agent
            h:                     np.ndarray shape (64,) — Transformer hidden state
            predicted_technique:   int or None — Transformer's prediction of NEXT
                                   technique, made at the PREVIOUS step (t-1).
                                   Used to compute proactive alignment bonus (r5).
                                   Pass None for NoTrans baseline (no prediction).

        Returns:
            observations: list of np.ndarray shape (374,)
            rewards:      list of float, one per agent (shared reward)
            done:         bool
            info:         dict with diagnostics including engagement_length
                          and interaction_depth
        """
        assert len(actions) == self.n_agents
        assert h.shape == (self.h_dim,)

        self.h = h
        self.honeypot_actions = actions
        self.step_count += 1

        # 1. Attacker selects and performs technique
        technique_id = self._attacker_select_technique()
        self.attacker_sequence.append(technique_id)

        # Record the technique and the node it was executed at (BEFORE the move),
        # so local_obs agents can observe the technique iff it occurred in their
        # own subnet.
        self._last_technique = technique_id
        self._last_exec_node = self.attacker_node

        # ── Reactive affinity (SECONDARY, reporting only) ─────────────────
        # The agent whose subnet the attacker currently occupies. This agent
        # already observed the attacker arrive last step, so it is ALWAYS sighted
        # and h is redundant for it. Kept only to contrast against the primary
        # anticipatory metric below (both models saturate this — see writeup).
        reactive_agent = NODE_TO_AGENT.get(self.attacker_node)
        if reactive_agent is not None and 0 <= technique_id < ALIGNMENT_MATRIX.shape[0]:
            reactive_affinity = float(ALIGNMENT_MATRIX[technique_id][actions[reactive_agent]])
        else:
            reactive_affinity = 0.0

        # ── Step 1: Update interaction_depth (Unique Techniques) ──────────
        # Adding to a set is idempotent: repeated techniques during a stall
        # do not increase depth.
        self._unique_techniques.add(technique_id)

        # 2. Attacker moves to next node
        self.attacker_node = self._attacker_move()
        self.compromised.add(self.attacker_node)

        # Neighbor-warning: decay all subnet-activity signals, then refresh the
        # subnet the attacker just entered. Agents read their neighbors' values.
        if USE_NEIGHBOR_WARNING:
            for _a in self._subnet_activity:
                self._subnet_activity[_a] *= NEIGHBOR_DECAY
            _cur_sub = NODE_TO_AGENT.get(self.attacker_node)
            if _cur_sub is not None:
                self._subnet_activity[_cur_sub] = 1.0

        # ── PRIMARY metric — ANTICIPATORY alignment (Path B credit assignment) ─
        # Credit the agent whose subnet the attacker MOVES INTO, scored against
        # this step's technique, using the action that agent already chose BEFORE
        # the move (while the attacker was still elsewhere — i.e. while BLIND).
        # This is the only credit assignment under which the Transformer intent
        # vector h is structurally NECESSARY: the responsible agent cannot see the
        # attacker at decision time and must anticipate the incoming technique
        # from h. NoTrans (h=zeros) has no forward signal and can only play a
        # fixed action. Physically: the honeypot at the attacker's next hop must
        # pre-present deception aligned with the incoming transition technique.
        antic_agent = NODE_TO_AGENT.get(self.attacker_node)
        if antic_agent is not None and 0 <= technique_id < ALIGNMENT_MATRIX.shape[0]:
            best_affinity = float(ALIGNMENT_MATRIX[technique_id][actions[antic_agent]])
        else:
            best_affinity = 0.0

        # ── Step 1: Update engagement_length (Dwell Time) ─────────────────
        # Keyed on the anticipatory affinity: a well-anticipated destination
        # honeypot traps the arriving attacker for additional cycles.
        # Threshold 0.5 is chosen so at least 2-3 actions per technique row
        # can trigger the stall, making it reachable by a good policy.
        STALL_THRESHOLD = 0.5
        if best_affinity >= STALL_THRESHOLD:
            self.engagement_length += 1.0 + 2.0 * best_affinity   # e.g. 2.0–3.0
        else:
            self.engagement_length += 1.0

        # 3. Check terminal conditions
        reached_critical = (self.attacker_node == CRITICAL_NODE)
        trapped          = (self.attacker_node in HONEYPOT_NODES)
        timeout          = (self.step_count >= self.max_steps)

        # ── Step 2: exfiltration escape condition ─────────────────────────
        # An un-trapped attacker who executes a deep exfiltration technique
        # has successfully escaped the honeypot sandbox — treat as failure.
        exfil_escape = (
            technique_id in EXFIL_TECHNIQUE_IDS
            and not trapped
            and not self.attacker_trapped
        )

        if trapped:
            self.attacker_trapped = True

        self.done = reached_critical or trapped or timeout or exfil_escape

        # 4. Compute reward (Fix 2: pass previous prediction for proactive bonus)
        reward = self._compute_reward(
            technique_id          = technique_id,
            actions               = actions,
            engaged               = trapped,
            reached_critical      = reached_critical,
            alignment_score       = best_affinity,        # responsible-agent-only
            prev_predicted_tech   = predicted_technique,  # from t-1
        )

        rewards = [reward] * self.n_agents

        # 5. Build observations
        observations = self._get_observations()

        # Expose both decoupled metrics in info
        interaction_depth = len(self._unique_techniques)

        info = {
            "technique_id":      technique_id,
            "technique_name":    ID_TO_TECHNIQUE.get(technique_id, "UNK"),
            "attacker_node":     self.attacker_node,
            "node_name":         NODES[self.attacker_node],
            "trapped":           trapped,
            "reached_critical":  reached_critical,
            "exfil_escape":      exfil_escape,
            "step":              self.step_count,
            "sequence_len":      len(self.attacker_sequence),
            # ── decoupled metrics (Step 1) ─────────────────────────────────
            "engagement_length": self.engagement_length,
            "interaction_depth": interaction_depth,
            "best_affinity":     round(best_affinity, 4),      # anticipatory (primary)
            "reactive_affinity": round(reactive_affinity, 4),  # current-node (secondary)
            "profile":           self._profile,                # HIDDEN campaign profile
        }

        return observations, rewards, self.done, info

    # ── Reward ─────────────────────────────────────────────────────────────

    def _compute_reward(self, technique_id, actions, engaged, reached_critical,
                        alignment_score, prev_predicted_tech=None):
        """
        Multi-objective reward (Fix 2 + Fix 4 + credit-assignment fix):
          r1 = engagement    (did attacker enter honeypot?)
          r2 = reactive alignment — credited ONLY to the agent whose subnet
               contains the attacker this step (alignment_score, computed by
               the caller via NODE_TO_AGENT). NOT max() over all 4 agents:
               that let an agent in an unrelated subnet earn full credit for
               an incidental action, which a static "diversify actions"
               policy can exploit without any real prediction/localization —
               defeating the point of local (Dec-POMDP) observations.
          r3 = coordination  (did agents choose diverse actions?)
          r4 = efficiency    (penalize redundant same actions)
          r5 = proactive alignment bonus (Fix 2):
               Reward agents whose actions matched the Transformer's
               prediction from the PREVIOUS step (t-1) AND that prediction
               turned out to be the actual current technique.
               Only available to the Thesis model (prev_predicted_tech != None).
               NoTrans baseline always gets r5 = 0.

        Thesis model  weights: R = 0.2*r1 + 0.15*r2 + 0.1*r3 + 0.05*r4 + 0.5*r5
        NoTrans baseline:      R = 0.3*r1 + 0.40*r2 + 0.2*r3 + 0.1*r4
        """
        if reached_critical:
            return -1.0

        # r1 — engagement
        r1 = 1.0 if engaged else 0.0

        # r2 — reactive alignment, precomputed by the caller for the single
        # agent responsible for the attacker's current subnet.
        r2 = alignment_score

        # r3 / r4 — RETIRED (kept only for logging; both carry ZERO weight).
        #
        # These were designed for the ORIGINAL credit assignment, where alignment
        # was max() over ALL FOUR agents' actions. In that regime spreading the
        # actions was rational: it raised the chance that SOME agent matched the
        # technique. Under the current ANTICIPATORY credit assignment exactly ONE
        # agent is scored (the owner of the subnet the attacker moves into), so a
        # diversity bonus pays three of four agents to play the WRONG action and
        # drags expected alignment toward the AVERAGE action instead of the best.
        #
        # Measured consequence before retirement: learned policies used 3.0-3.7
        # distinct actions per step and scored 0.38-0.42 alignment, BELOW the
        # no-information fixed-action value (0.495), while a step-counter oracle
        # playing ONE action for all agents scored 0.466 and beat them outright.
        # The freed weight is moved to r2 (alignment), the actual objective.
        unique_actions = len(set(actions))
        r3 = unique_actions / self.n_agents  # logged only, weight 0
        redundancy = self.n_agents - unique_actions
        r4 = -0.1 * redundancy               # logged only, weight 0

        # r5 — RETIRED (weight 0). It added +0.2 whenever the encoder's PREVIOUS
        # prediction happened to equal the current technique — an outcome the
        # agent's ACTION CANNOT INFLUENCE. That injected irreducible, action-
        # independent variance into the learning target, carried ONLY by the
        # Thesis model, and was a primary driver of the TD-divergence and the
        # sighted-step regression (Thesis worse than NoTrans even with full
        # visibility). Removing it makes the reward a pure function of the
        # responsible agent's action, so the objective is now learnable and
        # IDENTICAL for Thesis and NoTrans (h helps only by choosing a better
        # action, never by a free bonus). prev_predicted_tech is retained in the
        # signature for backward compatibility but no longer affects the reward.
        r5 = 0.0  # retired

        # Single, principled objective: engagement + anticipatory alignment of
        # the responsible agent. No action-independent terms.
        R = 0.3 * r1 + 0.70 * r2

        return float(R)

    # ── State Construction ─────────────────────────────────────────────────

    def _get_observations(self):
        """
        Build the per-agent observation list.

        Global mode (local_obs=False) — legacy, fully observable:
          Every agent receives the SAME 374-dim vector:
            [0:10]    M_com  — compromise status per node (10 binary values)
            [10:110]  M_con  — connectivity matrix flattened (10x10)
            [110:310] M_vul  — vulnerability scores (10 nodes × 20 CVEs simulated)
            [310:374] h      — Transformer hidden state (64-dim)

        Local mode (local_obs=True) — Dec-POMDP, partial observability:
          Each agent i receives a 116-dim vector:
            [0:LOCAL_STATE_DIM]  — its own subnet's local state only (52-dim)
            [LOCAL_STATE_DIM:]   — h (64-dim, shared global intent)
          The full global state is still exposed to the mixer via
          get_global_state() (centralized training, decentralized execution).
        """
        obs_base = self._build_base_state()  # (310,)
        self._last_base_state = obs_base

        if self.local_obs:
            return [
                np.concatenate([self._build_local_state(agent_id), self.h])
                for agent_id in range(self.n_agents)
            ]

        obs_full = np.concatenate([obs_base, self.h])  # (374,)
        return [obs_full.copy() for _ in range(self.n_agents)]

    def get_global_state(self):
        """
        Return the full 310-dim global network state for the mixer.

        In local_obs mode the agents no longer carry the global state in their
        observation, so the centralized mixer reads it from here. The value is
        cached each step to stay consistent with the observation just built
        (M_vul contains per-step noise, so re-building would differ).
        """
        return self._last_base_state.copy()

    def _build_local_state(self, agent_id):
        """
        Build the LOCAL_STATE_DIM (52) observation for one agent — its own
        subnet only. Attacker/technique fields are non-zero ONLY when the
        attacker is (or just acted) inside this agent's subnet; otherwise the
        agent is blind to attacker activity and must rely on h.

        Layout:
          own_compromise     [MAX_SUBNET_NODES]
          own_vulnerability  [MAX_SUBNET_NODES]
          own_connectivity   [MAX_SUBNET_NODES^2]
          attacker_present   [1]
          attacker_local_pos [MAX_SUBNET_NODES]  (one-hot within subnet)
          observed_technique [NUM_TECHNIQUES]    (one-hot; only if executed here)
        """
        own_nodes = SUBNET_NODES[agent_id]
        k = MAX_SUBNET_NODES

        own_compromise = np.zeros(k, dtype=np.float32)
        own_vuln       = np.zeros(k, dtype=np.float32)
        for idx, node_id in enumerate(own_nodes):
            own_compromise[idx] = 1.0 if node_id in self.compromised else 0.0
            own_vuln[idx]       = NODE_CVSS.get(node_id, 0.5)

        # Local connectivity: adjacency restricted to own subnet nodes.
        own_con = np.zeros((k, k), dtype=np.float32)
        for i_idx, src in enumerate(own_nodes):
            for j_idx, dst in enumerate(own_nodes):
                if dst in ADJACENCY.get(src, []):
                    own_con[i_idx][j_idx] = 1.0

        # Attacker presence within this subnet (post-move position).
        attacker_present   = np.zeros(1, dtype=np.float32)
        attacker_local_pos = np.zeros(k, dtype=np.float32)
        if self.attacker_node in own_nodes:
            attacker_present[0] = 1.0
            attacker_local_pos[own_nodes.index(self.attacker_node)] = 1.0

        # Observed technique: visible only if the technique was executed in this
        # subnet this step (agent "witnesses" activity in its own segment).
        observed_technique = np.zeros(NUM_TECHNIQUES, dtype=np.float32)
        if (self._last_technique is not None
                and self._last_exec_node in own_nodes
                and 0 <= self._last_technique < NUM_TECHNIQUES):
            observed_technique[self._last_technique] = 1.0

        parts = [
            own_compromise,
            own_vuln,
            own_con.flatten(),
            attacker_present,
            attacker_local_pos,
            observed_technique,
        ]

        # Neighbor-subnet early-warning: decayed activity of this agent's
        # adjacent subnets (padded to MAX_SUBNET_NEIGHBORS). Coarse "where"
        # signal that complements h's "what" — appended LAST so it never shifts
        # LOCAL_ATTACKER_PRESENT_IDX.
        if USE_NEIGHBOR_WARNING:
            neighbor_signal = np.zeros(MAX_SUBNET_NEIGHBORS, dtype=np.float32)
            for slot, j in enumerate(SUBNET_ADJACENCY.get(agent_id, [])[:MAX_SUBNET_NEIGHBORS]):
                neighbor_signal[slot] = self._subnet_activity.get(j, 0.0)
            parts.append(neighbor_signal)

        return np.concatenate(parts).astype(np.float32)

    def _build_base_state(self):
        """Build 310-dim Hawkeyes-compatible state vector."""
        n = self.n_nodes  # 12, but state uses first 10 (non-honeypot for M_con)

        # M_com (10-dim): compromise status of each node
        M_com = np.zeros(10, dtype=np.float32)
        for node_id in self.compromised:
            if node_id < 10:
                M_com[node_id] = 1.0

        # M_con (100-dim): flattened 10x10 connectivity matrix
        M_con = np.zeros((10, 10), dtype=np.float32)
        for src in range(10):
            for dst in ADJACENCY.get(src, []):
                if dst < 10:
                    M_con[src][dst] = 1.0
                    if src in self.compromised:
                        M_con[src][dst] *= 0.8

        # M_vul (200-dim): vulnerability feature matrix (10 nodes × 20 slots)
        M_vul = np.zeros((10, 20), dtype=np.float32)
        for node_id in range(10):
            base_score = NODE_CVSS.get(node_id, 0.5)
            for cve_slot in range(20):
                M_vul[node_id][cve_slot] = base_score + np.random.normal(0, 0.02)
            M_vul[node_id] = np.clip(M_vul[node_id], 0.0, 1.0)

        state = np.concatenate([
            M_com,
            M_con.flatten(),
            M_vul.flatten()
        ])  # (10 + 100 + 200) = 310
        return state

    # ── Attacker Logic ─────────────────────────────────────────────────────

    def _attacker_select_technique(self):
        """
        Select next MITRE technique based on attack strategy.
        Follows kill-chain ordering — early steps use early tactics.
        Capped at SIM_NUM_TECHNIQUES (20) — the simulation models the original
        kill-chain techniques only, consistent with the trained models.
        """
        # ── Hybrid mode: genuine Markov chain, conditioned on the HIDDEN profile
        # and the PREVIOUS technique — never on the step index. ────────────────
        if self._hybrid:
            if not self.attacker_sequence:
                probs = HYBRID_INIT                       # shared, profile-agnostic start
            else:
                probs = HYBRID_PROFILES[self._profile][self.attacker_sequence[-1]]
                if probs.sum() <= 0.0:                    # absorbing row safeguard
                    probs = HYBRID_INIT
            probs = probs / probs.sum()
            return int(np.random.choice(len(probs), p=probs))

        strategy = ATTACK_STRATEGIES.get(self.attack_strategy, ATTACK_STRATEGIES["Mix"])

        if strategy["weights"] is None:
            return random.randint(0, SIM_NUM_TECHNIQUES - 1)

        stage_idx    = min(len(self.attacker_sequence), len(TACTIC_ORDER) - 1)
        current_tact = TACTIC_ORDER[stage_idx]
        tactic_ids   = [tid for tid in TACTIC_TO_IDS.get(current_tact,
                        list(range(SIM_NUM_TECHNIQUES))) if tid < SIM_NUM_TECHNIQUES]
        if not tactic_ids:
            tactic_ids = list(range(SIM_NUM_TECHNIQUES))
        weights_map  = strategy["weights"]

        if current_tact in weights_map:
            weights = weights_map[current_tact]
            w = weights[:len(tactic_ids)]
            if len(w) < len(tactic_ids):
                w = w + [1.0 / len(tactic_ids)] * (len(tactic_ids) - len(w))
            total = sum(w)
            w = [x / total for x in w]
            return random.choices(tactic_ids, weights=w, k=1)[0]
        else:
            return random.choice(tactic_ids)

    def _attacker_move(self):
        """
        Move attacker to adjacent node.
        Prefers nodes with higher CVSS score (greedy attacker).
        Avoids honeypot nodes unless CVSS is very high (attacker can be fooled).
        """
        neighbors = ADJACENCY.get(self.attacker_node, [self.attacker_node])

        scores = []
        for n in neighbors:
            score = NODE_CVSS.get(n, 0.5)
            if n in HONEYPOT_NODES:
                score *= 0.6  # honeypots appear less attractive
            scores.append(score)

        total = sum(scores)
        weights = [s / total for s in scores]
        return random.choices(neighbors, weights=weights, k=1)[0]

    # ── Sequence Utilities ─────────────────────────────────────────────────

    def get_padded_sequence(self):
        """
        Return current attacker sequence padded to MAX_SEQ_LEN.
        Used as input to Transformer encoder.

        Returns: np.ndarray shape (MAX_SEQ_LEN,) dtype int64
        """
        seq = self.attacker_sequence[-MAX_SEQ_LEN:]
        pad_len = MAX_SEQ_LEN - len(seq)
        padded = [PAD_ID] * pad_len + seq
        return np.array(padded, dtype=np.int64)

    def get_sequence_length(self):
        """Return actual (non-padded) sequence length, capped at MAX_SEQ_LEN."""
        return min(len(self.attacker_sequence), MAX_SEQ_LEN)

    # ── Metric Accessors ───────────────────────────────────────────────────

    def get_engagement_length(self) -> float:
        """Return accumulated engagement length (dwell time) for this episode."""
        return self.engagement_length

    def get_interaction_depth(self) -> int:
        """Return count of unique MITRE techniques attempted this episode."""
        return len(self._unique_techniques)


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  HoneypotEnv — Quick Verification (Step 1 decoupling check)")
    print("=" * 60)

    env = HoneypotEnv(attack_strategy="HiE", max_steps=50)
    obs = env.reset()

    print(f"  Observation shape per agent : {obs[0].shape}")
    assert obs[0].shape == (374,), "Observation shape mismatch"
    print(f"  Observation shape correct")
    print(f"  ALIGNMENT_MATRIX shape      : {ALIGNMENT_MATRIX.shape}  (expected (23, 5))")
    assert ALIGNMENT_MATRIX.shape == (23, 5)
    print(f"  SIM_NUM_TECHNIQUES          : {SIM_NUM_TECHNIQUES}")

    print(f"\n  Running 20 steps — checking Engagement Length vs Interaction Depth...")
    h = np.zeros(64, dtype=np.float32)
    # Use a high-affinity policy for agent 0 to trigger stall bonuses more often
    high_affinity_actions = [2, 1, 3, 4]   # fake_vulnerability + varied

    for step_i in range(20):
        obs, rewards, done, info = env.step(high_affinity_actions, h)
        eng = info["engagement_length"]
        dep = info["interaction_depth"]
        print(f"  Step {step_i+1:2d} | Node: {info['node_name']:12s} | "
              f"Tech: {info['technique_name']:6s} (id={info['technique_id']}) | "
              f"Affinity: {info['best_affinity']:.2f} | "
              f"Eng: {eng:6.2f} | Depth: {dep:2d} | "
              f"Trapped: {info['trapped']}")
        if done:
            print(f"  Episode ended early at step {step_i+1} "
                  f"(exfil_escape={info['exfil_escape']})")
            break

    final_eng = env.get_engagement_length()
    final_dep = env.get_interaction_depth()
    steps_run = env.step_count

    print(f"\n  Final Engagement Length : {final_eng:.2f}")
    print(f"  Final Interaction Depth : {final_dep}")
    print(f"  Steps run               : {steps_run}")
    print()

    # Key invariant: engagement_length > steps_run when stalls occurred,
    # and interaction_depth <= steps_run (repeats don't increase depth).
    assert final_dep <= steps_run, \
        "Interaction depth cannot exceed step count"
    assert final_eng >= steps_run, \
        "Engagement length must be >= step count (stall bonus only adds)"

    # The duplication bug would manifest as final_eng == final_dep.
    # With stall bonuses active and repeated techniques possible, they diverge.
    print(f"  Duplication check (eng != dep): "
          f"{'PASS — metrics are decoupled' if final_eng != final_dep else 'WARNING — still equal (no stalls triggered)'}")

    # ── Local-observation (Dec-POMDP) mode verification ────────────────────────
    print("\n" + "=" * 60)
    print("  Local-Observation Mode (Dec-POMDP) — Verification")
    print("=" * 60)

    lenv = HoneypotEnv(attack_strategy="HiE", max_steps=50, local_obs=True)
    lobs = lenv.reset()

    _expect_local = 52 + (MAX_SUBNET_NEIGHBORS if USE_NEIGHBOR_WARNING else 0)
    print(f"  LOCAL_STATE_DIM             : {LOCAL_STATE_DIM}  (expected {_expect_local})")
    assert LOCAL_STATE_DIM == _expect_local
    print(f"  Neighbor-warning            : {USE_NEIGHBOR_WARNING}  | subnet adjacency {SUBNET_ADJACENCY}")
    print(f"  Per-agent obs dim           : {lobs[0].shape[0]}  (expected {LOCAL_STATE_DIM + 64})")
    assert lobs[0].shape == (LOCAL_STATE_DIM + 64,)
    print(f"  Global state (for mixer) dim: {lenv.get_global_state().shape[0]}  (expected 310)")
    assert lenv.get_global_state().shape == (310,)

    # Agents must see DIFFERENT local observations (unlike global mode).
    all_same = all(np.allclose(lobs[0][:LOCAL_STATE_DIM], lobs[i][:LOCAL_STATE_DIM])
                   for i in range(1, N_AGENTS))
    print(f"  Agents see distinct local views: {'FAIL (identical)' if all_same else 'PASS'}")
    assert not all_same, "Local observations must differ across agents/subnets"

    # Key property: exactly the subnet containing the attacker sees activity;
    # all other agents are blind (attacker fields all zero) and must use h.
    h = np.zeros(64, dtype=np.float32)
    print("\n  Tracking which agent 'sees' the attacker each step:")
    for step_i in range(8):
        lobs, _, ldone, linfo = lenv.step([2, 1, 3, 4], h)
        # attacker_present flag sits right after own_compromise+own_vuln+own_con
        pres_idx = LOCAL_ATTACKER_PRESENT_IDX
        seers = [i for i in range(N_AGENTS) if lobs[i][pres_idx] > 0.5]
        # observed_technique block: after attacker_present(1)+attacker_local_pos(K)
        tech_start = LOCAL_ATTACKER_PRESENT_IDX + 1 + MAX_SUBNET_NODES
        tech_seers = [i for i in range(N_AGENTS)
                      if lobs[i][tech_start:tech_start + NUM_TECHNIQUES].sum() > 0.5]
        print(f"    Step {step_i+1}: attacker@{NODES[linfo['attacker_node']]:11s} "
              f"| present-to agents {seers} | technique-visible-to {tech_seers}")
        assert len(seers) <= 1, "At most one subnet can contain the attacker"
        if ldone:
            print(f"    Episode ended at step {step_i+1}")
            break

    # NoTrans handicap check: with h=0, agents NOT co-located with the attacker
    # have an all-zero attacker/technique view — they are structurally blind,
    # which is the whole point of the redesign.
    _view_start = LOCAL_ATTACKER_PRESENT_IDX
    _view_end   = LOCAL_ATTACKER_PRESENT_IDX + 1 + MAX_SUBNET_NODES + NUM_TECHNIQUES
    blind_agents = [i for i in range(N_AGENTS)
                    if lobs[i][_view_start:_view_end].sum() == 0.0]
    print(f"\n  Agents blind to attacker this step (rely on h): {blind_agents}")
    print(f"  -> In global mode this set is always empty (h redundant);")
    print(f"     in local mode it is non-empty (h load-bearing).")

    print(f"\n  Local-observation mode verified")
    print(f"\n  simulation_env.py verified")
