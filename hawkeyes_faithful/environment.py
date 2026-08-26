


# environment.py
# Hawkeyes faithful reproduction — Do Hoang et al. (2026)
# Implements: Sections 3, 4.2, 4.3.2, 4.3.3, 4.3.4, Algorithm 1

import numpy as np
import random
from network_topology import (
    NODES, GROUPS, GROUP_MEMBERSHIP, ACCESS_RULES,
    ENTRY_NODES, CRITICAL_NODES, HYPERPARAMS, compute_H_scores
)

# =============================================================
# NODE INDEX — maps node names to integer indices
# Used for matrix construction
# =============================================================

# Only real nodes (not honeypots) form the base network
REAL_NODES = [n for n, d in NODES.items() if not d["is_honeypot"]]
HONEYPOT_NODES = [n for n, d in NODES.items() if d["is_honeypot"]]
NODE_INDEX = {name: i for i, name in enumerate(REAL_NODES)}
N_NODES = len(REAL_NODES)   # 10

# =============================================================
# BUILD STATIC MATRICES
# These do not change during an episode unless topology changes
# (Scenario 3 modifies these)
# =============================================================

def build_connection_matrix(access_rules=None):
    """
    M_con — Equation 8
    Shape: (N_NODES, N_NODES)
    c[i][j] = 1 if node i can attack node j
    """
    if access_rules is None:
        access_rules = ACCESS_RULES

    M_con = np.zeros((N_NODES, N_NODES), dtype=np.float32)
    for src, dst in access_rules:
        if src in NODE_INDEX and dst in NODE_INDEX:
            i = NODE_INDEX[src]
            j = NODE_INDEX[dst]
            M_con[i][j] = 1.0
    return M_con


def build_vulnerability_matrix():
    """
    M_vul — Equation 9, 10
    Shape: (N_NODES, N_NODES, 2)
    For each edge (i,j): [H_CVSS of j, H_EPSS of j]
    Represents the vulnerability of destination node j
    when attacked from node i
    """
    M_vul = np.zeros((N_NODES, N_NODES, 2), dtype=np.float32)
    M_con = build_connection_matrix()

    for i in range(N_NODES):
        for j in range(N_NODES):
            if M_con[i][j] == 1.0:
                dst_name = REAL_NODES[j]
                h_cvss, h_epss = compute_H_scores(dst_name)
                M_vul[i][j][0] = h_cvss
                M_vul[i][j][1] = h_epss
    return M_vul


# =============================================================
# NMS — Network Monitoring System (Section 4.2)
# Models imperfect detection with FPR and FNR
# =============================================================

class NMS:
    """
    Network Monitoring System with uncertainty.
    FNR: probability of missing a real attack (false negative)
    FPR: probability of flagging benign traffic (false positive)
    """
    def __init__(self, fnr=0.05, fpr=0.02):
        self.fnr = fnr
        self.fpr = fpr

    def observe(self, truly_compromised):
        """
        Given ground truth compromised nodes,
        return noisy observation vector.

        truly_compromised: list of node names actually compromised
        Returns: dict {node_name: observed_status (0 or 1)}
        """
        observation = {}
        for node in REAL_NODES:
            if node in truly_compromised:
                # Real attack — might be missed (FNR)
                detected = random.random() > self.fnr
                observation[node] = 1 if detected else 0
            else:
                # No attack — might be falsely flagged (FPR)
                false_alarm = random.random() < self.fpr
                observation[node] = 1 if false_alarm else 0
        return observation


# =============================================================
# ATTACKER — 6 strategies from Section 4.2
# =============================================================

class Attacker:
    """
    Implements all 6 attack strategies from Section 4.2.
    Moves through the network using ACCESS_RULES.
    """
    def __init__(self, strategy="Ran"):
        assert strategy in ["HiE", "HiC", "Ran", "RanE", "RanC", "Mix"]
        self.strategy = strategy
        self.current_strategy = strategy  # changes each step if Mix
        self.position = None              # current node name
        self.compromised = set()          # all nodes attacker controls

    def reset(self):
        """Start at a random entry node."""
        self.position = random.choice(ENTRY_NODES)
        self.compromised = {self.position}
        return self.position

    def get_reachable_nodes(self, current_node, honeypot_positions):
        """
        From current_node, find all nodes reachable via ACCESS_RULES.
        Includes honeypots if they are deployed in reachable groups.
        Excludes already-compromised nodes.
        """
        reachable = []
        for src, dst in ACCESS_RULES:
            if src == current_node:
                if dst not in self.compromised:
                    reachable.append(dst)

        # Add honeypots deployed in reachable groups
        current_group = get_node_group(current_node)
        for hp_name, hp_group in honeypot_positions.items():
            if hp_group is not None and hp_name not in self.compromised:
                # Honeypot is reachable if it is in a group
                # adjacent to current position
                if is_group_reachable(current_node, hp_group):
                    reachable.append(hp_name)

        return reachable

    def select_target(self, reachable_nodes):
        """
        Select next target based on current strategy.
        Equations 3 and 4 for weighted random strategies.
        """
        if not reachable_nodes:
            return None

        # If Mix strategy, randomly switch each step
        if self.strategy == "Mix":
            self.current_strategy = random.choice(
                ["HiE", "HiC", "Ran", "RanE", "RanC"]
            )
        else:
            self.current_strategy = self.strategy

        # Separate honeypots from real nodes in reachable list
        real_reachable = [n for n in reachable_nodes
                          if n not in HONEYPOT_NODES]
        all_reachable = reachable_nodes
        if self.current_strategy == "HiE":
            # FIX: pick randomly among tied nodes (not just first max)
            max_epss = max(get_node_epss(n) for n in all_reachable)
            tied = [n for n in all_reachable
                    if get_node_epss(n) == max_epss]
            return random.choice(tied)

        elif self.current_strategy == "HiC":
            # FIX: pick randomly among tied nodes
            max_cvss = max(get_node_cvss(n) for n in all_reachable)
            tied = [n for n in all_reachable
                    if get_node_cvss(n) == max_cvss]
            return random.choice(tied)

        elif self.current_strategy == "Ran":
            # Random target — uniform distribution
            return random.choice(all_reachable)

        elif self.current_strategy == "RanE":
            # Equation 3 — weighted random by EPSS
            weights = [get_node_epss(n) for n in all_reachable]
            total = sum(weights)
            if total == 0:
                return random.choice(all_reachable)
            probs = [w / total for w in weights]
            return random.choices(all_reachable, weights=probs, k=1)[0]

        elif self.current_strategy == "RanC":
            # Equation 4 — weighted random by CVSS
            weights = [get_node_cvss(n) for n in all_reachable]
            total = sum(weights)
            if total == 0:
                return random.choice(all_reachable)
            probs = [w / total for w in weights]
            return random.choices(all_reachable, weights=probs, k=1)[0]

    def step(self, honeypot_positions):
        """
        Move to next target. Returns (target, is_honeypot, is_critical).
        """
        reachable = self.get_reachable_nodes(
            self.position, honeypot_positions
        )
        if not reachable:
            return None, False, False

        target = self.select_target(reachable)
        if target is None:
            return None, False, False

        self.position = target
        self.compromised.add(target)

        is_honeypot = target in HONEYPOT_NODES
        is_critical = target in CRITICAL_NODES

        return target, is_honeypot, is_critical


# =============================================================
# HELPER FUNCTIONS
# =============================================================

def get_node_group(node_name):
    """Return which group index a node belongs to."""
    for group_id, members in GROUP_MEMBERSHIP.items():
        if node_name in members:
            return group_id
    return None


def is_group_reachable(from_node, target_group):
    """
    Check if target_group is reachable from from_node
    based on ACCESS_RULES.
    """
    target_members = GROUP_MEMBERSHIP.get(target_group, [])
    for src, dst in ACCESS_RULES:
        if src == from_node and dst in target_members:
            return True
    return False


def get_node_epss(node_name):
    """Get max EPSS score for a node."""
    if node_name in NODES:
        cves = NODES[node_name]["cves"]
        if cves:
            return max(c["epss"] for c in cves)
    return 0.0


def get_node_cvss(node_name):
    """Get max CVSS score for a node."""
    if node_name in NODES:
        cves = NODES[node_name]["cves"]
        if cves:
            return max(c["cvss"] for c in cves)
    return 0.0


# =============================================================
# HAWKEYES ENVIRONMENT — Main simulation class
# Implements Algorithm 1 from the paper
# =============================================================

class HawkeyesEnv:
    """
    Full Hawkeyes simulation environment.

    State: S_t = (M_com, M_con, M_vul) — Equation 6
    Action: group index for each agent (honeypot)
    Reward: +1 success, -1 failure, 0 otherwise — Equation 11
    """

    def __init__(self, fnr=0.05, fpr=0.02,
                 attack_strategy="Ran",
                 access_rules=None):
        self.fnr = fnr
        self.fpr = fpr
        self.attack_strategy = attack_strategy

        # Use modified access rules for Scenario 3
        self.access_rules = access_rules or ACCESS_RULES

        # Build static matrices
        self.M_con = build_connection_matrix(self.access_rules)
        self.M_vul = build_vulnerability_matrix()

        # NMS and attacker
        self.nms = NMS(fnr=fnr, fpr=fpr)
        self.attacker = Attacker(strategy=attack_strategy)

        # Honeypot positions: {honeypot_name: group_id or None}
        self.honeypot_positions = {
            "Honeypot1": None,
            "Honeypot2": None
        }

        # State
        self.compromised_ground_truth = set()
        self.observed_compromised = {}
        self.done = False
        self.success = False

        # State dimension calculation
        # M_com: N_NODES = 10
        # M_con: N_NODES * N_NODES = 100
        # M_vul: N_NODES * N_NODES * 2 = 200
        # Total: 310
        self.state_dim = N_NODES + N_NODES * N_NODES + N_NODES * N_NODES * 2
        self.action_dim = len(GROUPS)  # 4 groups

    def reset(self):
        """
        Reset environment for new episode.
        Returns initial state vector.
        """
        # Reset honeypot positions
        self.honeypot_positions = {
            "Honeypot1": None,
            "Honeypot2": None
        }

        # Reset attacker
        self.attacker.reset()
        self.compromised_ground_truth = set([self.attacker.position])

        # Reset NMS observation
        self.observed_compromised = self.nms.observe(
            self.compromised_ground_truth
        )

        self.done = False
        self.success = False
        self.step_count = 0
        return self._get_state()

    def step(self, actions):
        """
        Execute one step of Algorithm 1.

        actions: list of group indices [agent1_action, agent2_action]
        Returns: (next_state, reward, done, info)
        """
        if self.done:
            return self._get_state(), 0.0, True, {}
        self.step_count +=1
            # Add max steps safety limit — prevent infinite episodes
        if self.step_count >= 500:          # ← add these 4 lines
            self.done = True
            self.success = False
            return self._get_state(), -1.0, True, {"success": False,
                  "target": None, "is_honeypot": False,
                  "is_critical": False,
                  "attacker_position": self.attacker.position,
                  "compromised": len(self.compromised_ground_truth)}

        # --- Deploy honeypots (Algorithm 1, line 29) ---
        honeypot_names = list(self.honeypot_positions.keys())
        for i, hp_name in enumerate(honeypot_names):
            if i < len(actions):
                self.honeypot_positions[hp_name] = actions[i]

        # --- Attacker moves (Algorithm 1, line 31) ---
        target, is_honeypot, is_critical = self.attacker.step(
            self.honeypot_positions
        )

        # --- NMS observes (Algorithm 1, line 30) ---
        if target is not None:
            self.compromised_ground_truth.add(target)
        self.observed_compromised = self.nms.observe(
            self.compromised_ground_truth
        )

        # --- Compute reward (Algorithm 1, line 33 / Equation 11) ---
        if is_honeypot:
            # Attacker trapped — defense success
            reward = 1.0
            self.done = True
            self.success = True
        elif is_critical:
            # Attacker reached critical asset — defense failure
            reward = -1.0
            self.done = True
            self.success = False
        elif target is None:
            # Attacker stuck — treat as success
            reward = 1.0
            self.done = True
            self.success = True
        else:
            reward = 0.0

        next_state = self._get_state()
        info = {
            "target": target,
            "is_honeypot": is_honeypot,
            "is_critical": is_critical,
            "success": self.success,
            "attacker_position": self.attacker.position,
            "compromised": len(self.compromised_ground_truth)
        }

        return next_state, reward, self.done, info

    def _get_state(self):
        """
        Build state vector S_t = (M_com, M_con, M_vul)
        Equation 6 — flattened to 1D vector of size 310
        """
        # M_com — Equation 7
        # Shape: (10,) — 1 if node observed as compromised
        M_com = np.array([
            float(self.observed_compromised.get(n, 0))
            for n in REAL_NODES
        ], dtype=np.float32)

        # M_con — Equation 8
        # Shape: (10, 10) — already built, stays static
        M_con_flat = self.M_con.flatten()

        # M_vul — Equations 9, 10
        # Shape: (10, 10, 2) — already built, stays static
        M_vul_flat = self.M_vul.flatten()

        # Concatenate into single state vector
        state = np.concatenate([M_com, M_con_flat, M_vul_flat])

        return state.astype(np.float32)

    def get_high_level_strategy(self):
        """
        High-level gating mechanism — Equation 5
        Returns: 'init', 'crit', or 'low'
        """
        observed_list = [
            n for n, v in self.observed_compromised.items() if v == 1
        ]

        # Condition 1: no compromised nodes observed
        if not observed_list:
            return "init"

        # Condition 2: critical node is reachable from attacker
        for comp_node in observed_list:
            for crit_node in CRITICAL_NODES:
                for src, dst in self.access_rules:
                    if src == comp_node and dst == crit_node:
                        return "crit"

        return "low"

    def get_valid_actions(self, strategy):
        """
        Return valid group indices for each agent
        based on high-level strategy — Algorithm 1 lines 13-27
        """
        if strategy == "init":
            # Only groups containing entry nodes
            valid = set()
            for group_id, members in GROUP_MEMBERSHIP.items():
                if any(m in ENTRY_NODES for m in members):
                    valid.add(group_id)
            return list(valid) if valid else list(GROUPS.keys())

        elif strategy == "crit":
            # Only groups containing critical nodes
            valid = set()
            for group_id, members in GROUP_MEMBERSHIP.items():
                if any(m in CRITICAL_NODES for m in members):
                    valid.add(group_id)
            return list(valid) if valid else list(GROUPS.keys())

        else:  # "low"
            # All groups available
            return list(GROUPS.keys())

    def evaluate_dsr(self, policy_fn, n_trials=1000):
        """
        Evaluate Defense Success Rate — Equation 12
        DSR = N_succ / N_total

        policy_fn: function that takes state and returns actions
        n_trials: number of attack attempts
        """
        n_succ = 0
        for _ in range(n_trials):
            state = self.reset()
            done = False
            while not done:
                strategy = self.get_high_level_strategy()
                valid_actions = self.get_valid_actions(strategy)
                actions = policy_fn(state, valid_actions)
                state, reward, done, info = self.step(actions)
            if info["success"]:
                n_succ += 1
        dsr = n_succ / n_trials * 100.0
        return dsr


# =============================================================
# SCENARIO 3 — Modified network topology
# Section 5.4.3: changed access rules and new vulnerabilities
# =============================================================

# New access rules for Scenario 3
# "Hosts in Subnet 2 are now allowed to access the Internet"
# "Hosts in Subnet 1 can no longer connect through Subnet 2"
SCENARIO3_ACCESS_RULES = [
    # Internet → entry points (Subnet2 now also entry)
    ("INTERNET", "WebServer"),
    ("INTERNET", "Tablet"),
    ("INTERNET", "Host1"),
    ("INTERNET", "Host2"),   # NEW — Subnet2 can reach Internet
    ("INTERNET", "Host3"),   # NEW
    ("INTERNET", "Host4"),   # NEW

    # Subnet1 → WebServer only (no longer through Subnet2)
    ("Tablet",   "WebServer"),
    ("Host1",    "WebServer"),

    # Subnet2 → Subnet3 and Subnet4 (unchanged)
    ("Host2",    "PrintServer"),
    ("Host2",    "LDAPServer"),
    ("Host2",    "FileServer"),
    ("Host2",    "WebServer"),
    ("Host2",    "DBServer"),
    ("Host3",    "PrintServer"),
    ("Host3",    "LDAPServer"),
    ("Host3",    "FileServer"),
    ("Host3",    "WebServer"),
    ("Host3",    "DBServer"),
    ("Host4",    "PrintServer"),
    ("Host4",    "LDAPServer"),
    ("Host4",    "FileServer"),
    ("Host4",    "WebServer"),
    ("Host4",    "DBServer"),

    # WebServer → DBServer (unchanged)
    ("WebServer", "DBServer"),

    # Subnet3 → Subnet4 (unchanged)
    ("PrintServer", "DBServer"),
    ("LDAPServer",  "DBServer"),
    ("FileServer",  "DBServer"),
]

# New vulnerabilities for Subnet2 nodes in Scenario 3
# Section 5.4.3: "patched against previous vulnerabilities
# but remain exposed to two new ones"
SCENARIO3_NEW_CVES = {
    "Host2": [
        {"id": "CVE-2021-34527", "attack_type": "Remote",
         "req_priv": "User", "get_priv": "System",
         "cvss": 8.8, "epss": 0.9584},
        {"id": "CVE-2021-34498", "attack_type": "Local",
         "req_priv": "User", "get_priv": "System",
         "cvss": 7.8, "epss": 0.8764},
    ],
    "Host3": [
        {"id": "CVE-2021-34527", "attack_type": "Remote",
         "req_priv": "User", "get_priv": "System",
         "cvss": 8.8, "epss": 0.9584},
        {"id": "CVE-2021-34498", "attack_type": "Local",
         "req_priv": "User", "get_priv": "System",
         "cvss": 7.8, "epss": 0.8764},
    ],
    "Host4": [
        {"id": "CVE-2021-34527", "attack_type": "Remote",
         "req_priv": "User", "get_priv": "System",
         "cvss": 8.8, "epss": 0.9584},
        {"id": "CVE-2021-34498", "attack_type": "Local",
         "req_priv": "User", "get_priv": "System",
         "cvss": 7.8, "epss": 0.8764},
    ],
}


# =============================================================
# QUICK VERIFICATION
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ENVIRONMENT VERIFICATION")
    print("=" * 60)

    print(f"\nReal nodes:    {N_NODES}")
    print(f"State dim:     {HawkeyesEnv().state_dim}")
    print(f"Action dim:    {HawkeyesEnv().action_dim}")

    # Test reset
    env = HawkeyesEnv(fnr=0.05, fpr=0.02, attack_strategy="Ran")
    state = env.reset()
    print(f"\nReset state shape:  {state.shape}")
    print(f"State dtype:        {state.dtype}")
    print(f"State min/max:      {state.min():.4f} / {state.max():.4f}")

    # Test high-level strategy
    strategy = env.get_high_level_strategy()
    valid = env.get_valid_actions(strategy)
    print(f"\nHigh-level strategy: {strategy}")
    print(f"Valid actions:       {valid}")

    # Test one step
    actions = [valid[0], valid[0]]
    next_state, reward, done, info = env.step(actions)
    print(f"\nAfter 1 step:")
    print(f"  Reward:   {reward}")
    print(f"  Done:     {done}")
    print(f"  Target:   {info['target']}")
    print(f"  Success:  {info['success']}")

    # Test all 6 attack strategies for 5 episodes each
    print("\n--- Strategy smoke test (5 episodes each) ---")
    for strat in ["HiE", "HiC", "Ran", "RanE", "RanC", "Mix"]:
        successes = 0
        for _ in range(5):
            env2 = HawkeyesEnv(fnr=0.05, fpr=0.02,
                               attack_strategy=strat)
            s = env2.reset()
            done = False
            steps = 0
            while not done and steps < 50:
                strategy = env2.get_high_level_strategy()
                valid = env2.get_valid_actions(strategy)
                # Random policy for smoke test
                acts = [random.choice(valid),
                        random.choice(valid)]
                s, r, done, info = env2.step(acts)
                steps += 1
            if info["success"]:
                successes += 1
        print(f"  {strat:<6}: {successes}/5 episodes terminated")

    print("\nEnvironment verification complete.")