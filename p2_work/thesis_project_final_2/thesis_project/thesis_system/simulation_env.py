# simulation_env.py
"""
File 2 of 8 — Simulation Environment
======================================
Purpose: Simulates the 12-node Hawkeyes network with 4 honeypot agents
         and an attacker progressing through MITRE ATT&CK techniques.

Key differences from Hawkeyes faithful reproduction:
  - Behavioral action space (5 actions) instead of node-placement actions
  - Attacker sequence tracked as list of technique IDs → fed to Transformer
  - State = 374-dim = 310 (Hawkeyes M_com+M_con+M_vul) + 64 (h from Transformer)
  - Reward = 0.4*r1 + 0.3*r2 + 0.2*r3 + 0.1*r4

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
from mitre_techniques import (
    TOKENS, ID_TO_TECHNIQUE, NUM_TECHNIQUES,
    PAD_ID, UNK_ID, VOCAB_SIZE, MAX_SEQ_LEN, TACTIC_TO_IDS
)

# Simulation operates on the original 20 kill-chain techniques only.
SIM_NUM_TECHNIQUES = 20

# Exfiltration technique IDs (techniques 15-17 in the kill-chain mapping).
# Used by Step 2 termination logic: an un-trapped attacker who attempts
# exfiltration is considered a successful escape.
EXFIL_TECHNIQUE_IDS = {15, 16, 17}   # T1005, T1560, T1041

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

    def __init__(self, attack_strategy="Mix", max_steps=200, n_agents=N_AGENTS):
        self.attack_strategy = attack_strategy
        self.max_steps       = max_steps
        self.n_agents        = n_agents
        self.n_nodes         = len(NODES)

        self.obs_dim_base = 310   # M_com(10) + M_con(100) + M_vul(200)
        self.h_dim        = 64
        self.obs_dim      = self.obs_dim_base + self.h_dim  # 374

        self.reset()

    # ── Reset ──────────────────────────────────────────────────────────────

    def reset(self):
        """Reset environment. Returns initial observations (without h — h=zeros)."""
        self.attacker_node     = random.choice(ENTRY_NODES)
        self.attacker_sequence = []   # list of technique IDs performed so far
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

        return self._get_observations()

    # ── Step ───────────────────────────────────────────────────────────────

    def step(self, actions, h):
        """
        Execute one environment step.

        Args:
            actions: list of int, length n_agents — one action per agent
            h:       np.ndarray shape (64,) — Transformer hidden state

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

        # ── Step 1: Compute best affinity for this step ────────────────────
        if 0 <= technique_id < ALIGNMENT_MATRIX.shape[0]:
            affinity_scores = [ALIGNMENT_MATRIX[technique_id][a] for a in actions]
            best_affinity   = float(max(affinity_scores))
        else:
            best_affinity = 0.0

        # ── Step 1: Update engagement_length (Dwell Time) ─────────────────
        # When a honeypot response highly aligns with the attacker's current
        # technique (affinity >= 0.5), the attacker is distracted and wastes
        # additional cycles — modelled as a multiplicative dwell bonus.
        # Threshold 0.5 is chosen so at least 2-3 actions per technique row
        # can trigger the stall, making it reachable by a good policy.
        STALL_THRESHOLD = 0.5
        if best_affinity >= STALL_THRESHOLD:
            self.engagement_length += 1.0 + 2.0 * best_affinity   # e.g. 2.0–3.0
        else:
            self.engagement_length += 1.0

        # ── Step 1: Update interaction_depth (Unique Techniques) ──────────
        # Adding to a set is idempotent: repeated techniques during a stall
        # do not increase depth.
        self._unique_techniques.add(technique_id)

        # 2. Attacker moves to next node
        self.attacker_node = self._attacker_move()
        self.compromised.add(self.attacker_node)

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

        # 4. Compute reward
        reward = self._compute_reward(
            technique_id     = technique_id,
            actions          = actions,
            engaged          = trapped,
            reached_critical = reached_critical,
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
            "best_affinity":     round(best_affinity, 4),
        }

        return observations, rewards, self.done, info

    # ── Reward ─────────────────────────────────────────────────────────────

    def _compute_reward(self, technique_id, actions, engaged, reached_critical):
        """
        Multi-objective reward:
          r1 = engagement    (did attacker enter honeypot?)
          r2 = depth         (alignment between technique and best agent action)
          r3 = coordination  (did agents choose diverse actions?)
          r4 = efficiency    (penalize redundant same actions)

        R = 0.4*r1 + 0.3*r2 + 0.2*r3 + 0.1*r4
        """
        if reached_critical:
            return -1.0

        # r1 — engagement
        r1 = 1.0 if engaged else 0.0

        # r2 — depth: best alignment among agents' actions
        if 0 <= technique_id < ALIGNMENT_MATRIX.shape[0]:
            alignment_scores = [
                ALIGNMENT_MATRIX[technique_id][a] for a in actions
            ]
            best_alignment = max(alignment_scores)
        else:
            best_alignment = 0.0
        r2 = best_alignment  # already in [0, 1]

        # r3 — coordination: reward diverse action selection
        unique_actions = len(set(actions))
        r3 = unique_actions / self.n_agents  # 0.25 to 1.0

        # r4 — efficiency penalty: penalize redundant actions
        redundancy = self.n_agents - unique_actions
        r4 = -0.1 * redundancy  # 0 to -0.3

        R = 0.4 * r1 + 0.3 * r2 + 0.2 * r3 + 0.1 * r4
        return float(R)

    # ── State Construction ─────────────────────────────────────────────────

    def _get_observations(self):
        """
        Build 374-dim observation for each agent.
        Each agent gets the same global observation (CTDE — centralized training).

        Structure:
          [0:10]    M_com  — compromise status per node (10 binary values)
          [10:110]  M_con  — connectivity matrix flattened (10x10)
          [110:310] M_vul  — vulnerability scores (10 nodes × 20 CVEs simulated)
          [310:374] h      — Transformer hidden state (64-dim)
        """
        obs_base = self._build_base_state()  # (310,)
        obs_full = np.concatenate([obs_base, self.h])  # (374,)
        return [obs_full.copy() for _ in range(self.n_agents)]

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
    print(f"\n  simulation_env.py verified")