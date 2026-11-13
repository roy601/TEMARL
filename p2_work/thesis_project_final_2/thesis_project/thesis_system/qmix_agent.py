# qmix_agent.py
"""
File 4 of 8 — Individual Q-Networks (QMIX Agents)
====================================================
Purpose: Each of the 4 honeypot agents has an individual Q-network.
         Takes 374-dim observation (310 network state + 64 h) as input.
         Outputs Q-values for 5 behavioral actions.

Architecture (GATED MULTI-MODAL FUSION — Problem 1 fix v2):

  Previous dual-branch used simple concatenation of branch outputs into
  a 128-dim vector. This fixed feature dominance but caused alignment
  collapse on the Random attacker strategy (0.475) because state masking
  forced the network to rely on h even when h was pure noise.

  Gated fusion solves this by letting the network LEARN how much to trust
  h vs telemetry based on the actual input content:

    Branch A (Telemetry):  310 → Linear(64) → LayerNorm → ReLU → a ∈ ℝ⁶⁴
    Branch B (Intent):      64 → Linear(64) → LayerNorm → ReLU → b ∈ ℝ⁶⁴

    Gate:  [a | b] ∈ ℝ¹²⁸ → Linear(128→64) → Sigmoid → g ∈ (0,1)⁶⁴

    Fused: f = g ⊙ a + (1−g) ⊙ b  ∈ ℝ⁶⁴

    Head:  f → Linear(64→64) → ReLU → Linear(64→5) → Q-values ∈ ℝ⁵

  Mathematical properties of gated fusion:
    - When h is informative (structured attacker): gate learns g ≈ 0.5,
      blending both branches, giving h equal influence over Q-values.
    - When h is noise (random attacker): gate learns g → 1.0 for those
      dimensions, suppressing Branch B and routing through telemetry only.
    - State masking (prob=0.3) still fires during training, so the network
      still learns to use h when it IS clean — but the gate provides an
      architectural escape hatch when h is not useful.
    - Gradient flows through both branches at all times (unlike hard
      switching), so neither branch is ever fully starved of updates.

State masking:
  Applied to raw state input before Branch A only.
  h is never masked — it is always fully available to Branch B and Gate.
  When state is zeroed: a = Branch_A(0) ≈ constant, gate adjusts toward
  b, so the network defaults to intent-driven policy.
  When state is present: gate blends both inputs proportionally to their
  predictive value for the current attacker context.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

# ── Constants ─────────────────────────────────────────────────────────────────
STATE_DIM  = 310   # Network state (M_com + M_con + M_vul)
H_DIM      = 64    # Transformer intent vector
OBS_DIM    = STATE_DIM + H_DIM   # 374 — full concatenated observation
ACTION_DIM = 5     # Behavioral actions
N_AGENTS   = 4
BRANCH_DIM = 64    # Both branches project to this common dimension
HEAD_DIM   = 64    # Fusion head hidden dimension


# ── Gated Multi-Modal Fusion Q-Network ────────────────────────────────────────

class GatedFusionQNetwork(nn.Module):
    """
    Q-network with gated multi-modal fusion.

    The gate vector g ∈ (0,1)⁶⁴ is computed from BOTH branch outputs,
    allowing the network to dynamically suppress h when it carries no
    useful signal (e.g. random attacker) and amplify it when it does
    (e.g. structured kill-chain attacker).

    Input layout:
        obs[..., :STATE_DIM]  — network telemetry (310-dim)
        obs[..., STATE_DIM:]  — Transformer intent vector h (64-dim)
    """

    def __init__(
        self,
        state_dim          = STATE_DIM,
        h_dim              = H_DIM,
        action_dim         = ACTION_DIM,
        branch_dim         = BRANCH_DIM,
        head_dim           = HEAD_DIM,
        state_masking_prob = 0.3,
    ):
        super().__init__()
        self.state_dim          = state_dim
        self.h_dim              = h_dim
        self.action_dim         = action_dim
        self.branch_dim         = branch_dim
        self.state_masking_prob = state_masking_prob

        # ── Branch A: Telemetry ───────────────────────────────────────────
        # 310 → 64: projects high-dim state to same space as h.
        self.branch_state = nn.Sequential(
            nn.Linear(state_dim, branch_dim),
            nn.LayerNorm(branch_dim),
            nn.ReLU(),
        )

        # ── Branch B: Intent ──────────────────────────────────────────────
        # 64 → 64: independent projection of Transformer output.
        self.branch_intent = nn.Sequential(
            nn.Linear(h_dim, branch_dim),
            nn.LayerNorm(branch_dim),
            nn.ReLU(),
        )

        # ── Gated Fusion Layer ────────────────────────────────────────────
        # [a | b] ∈ ℝ¹²⁸ → g ∈ (0,1)⁶⁴
        # g is computed jointly from BOTH branches, so the gate responds
        # to the relationship between telemetry and intent, not just one.
        # Sigmoid output guarantees g ∈ (0,1) strictly, enabling smooth
        # interpolation between pure-telemetry (g→1) and pure-intent (g→0).
        self.gate = nn.Sequential(
            nn.Linear(branch_dim * 2, branch_dim),  # 128 → 64
            nn.Sigmoid(),
        )

        # ── Output Head ───────────────────────────────────────────────────
        # Fused_Out (64-dim) → Q-values (5-dim)
        self.head = nn.Sequential(
            nn.Linear(branch_dim, head_dim),   # 64 → 64
            nn.ReLU(),
            nn.Linear(head_dim, action_dim),   # 64 → 5
        )

        self._init_weights()

    def _init_weights(self):
        """Xavier uniform for linear layers; gate bias initialised to 0."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

    def _apply_state_mask(self, state: torch.Tensor) -> torch.Tensor:
        """
        Randomly zero the state branch input during training.
        Returns state unchanged in eval mode or when prob=0.
        h is NEVER masked.
        """
        if not self.training or self.state_masking_prob <= 0.0:
            return state
        # Per-sample Bernoulli mask, shape (N, 1), broadcast over features.
        mask = torch.bernoulli(
            torch.full(
                (state.shape[0], 1),
                1.0 - self.state_masking_prob,
                device=state.device,
                dtype=state.dtype,
            )
        )
        return state * mask

    def forward(self, obs: torch.Tensor) -> torch.Tensor:
        """
        Gated multi-modal forward pass.

        Args:
            obs: FloatTensor (..., STATE_DIM + H_DIM)

        Returns:
            q_values: FloatTensor (..., ACTION_DIM)

        Tensor flow:
            obs → split → [state (310) | h (64)]
            state → mask → Branch_A → a  (64)
            h              → Branch_B → b  (64)
            [a | b]        → Gate     → g  (64)  ∈ (0,1)
            g⊙a + (1-g)⊙b            → f  (64)  fused representation
            f              → Head     → Q  (5)
        """
        orig_shape = obs.shape[:-1]

        # Split and flatten leading dims
        state = obs[..., :self.state_dim].reshape(-1, self.state_dim)  # (N, 310)
        h     = obs[..., self.state_dim:].reshape(-1, self.h_dim)       # (N,  64)

        # State masking (training only, never applied to h)
        state = self._apply_state_mask(state)

        # Branch A: telemetry representation
        a = self.branch_state(state)    # (N, 64)

        # Branch B: intent representation
        b = self.branch_intent(h)       # (N, 64)

        # Gated fusion
        # Gate is conditioned on BOTH branches — it can see when they agree
        # or conflict, and weight accordingly.
        ab = torch.cat([a, b], dim=-1)  # (N, 128)
        g  = self.gate(ab)              # (N,  64), values ∈ (0,1)

        # Element-wise weighted blend
        # g → 1.0: trust telemetry (Branch A), ignore intent
        # g → 0.0: trust intent (Branch B), ignore telemetry
        f = g * a + (1.0 - g) * b      # (N, 64)

        # Output head
        q_values = self.head(f)         # (N, 5)

        # Restore original leading dims
        return q_values.reshape(*orig_shape, self.action_dim)

    def select_action(self, obs: torch.Tensor, epsilon: float = 0.0) -> int:
        """Epsilon-greedy action selection."""
        if obs.dim() == 1:
            obs = obs.unsqueeze(0)
        if np.random.random() < epsilon:
            return np.random.randint(0, self.action_dim)
        with torch.no_grad():
            q = self.forward(obs)
        return q.argmax(dim=-1).item()

    def get_gate_value(self, obs: torch.Tensor) -> torch.Tensor:
        """
        Diagnostic: return the gate vector g for a given observation.
        Useful for verifying that g approaches 1 (telemetry dominant)
        on random attacker sequences and 0.5 on structured sequences.

        Returns: FloatTensor (..., BRANCH_DIM)
        """
        self.eval()
        with torch.no_grad():
            orig_shape = obs.shape[:-1]
            state = obs[..., :self.state_dim].reshape(-1, self.state_dim)
            h     = obs[..., self.state_dim:].reshape(-1, self.h_dim)
            a = self.branch_state(state)
            b = self.branch_intent(h)
            ab = torch.cat([a, b], dim=-1)
            g  = self.gate(ab)
        return g.reshape(*orig_shape, self.branch_dim)


# ── Agent Wrapper ─────────────────────────────────────────────────────────────

class QMIXAgent:
    """
    Wrapper around GatedFusionQNetwork with target network and update logic.
    """

    def __init__(
        self,
        agent_id           = 0,
        obs_dim            = OBS_DIM,
        action_dim         = ACTION_DIM,
        state_masking_prob = 0.3,
        device             = None,
    ):
        self.agent_id           = agent_id
        self.obs_dim            = obs_dim
        self.action_dim         = action_dim
        self.state_masking_prob = state_masking_prob
        self.device             = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.online_net = GatedFusionQNetwork(
            state_masking_prob = state_masking_prob,
        ).to(self.device)

        # Target net never masks — produces stable Q-targets
        self.target_net = GatedFusionQNetwork(
            state_masking_prob = 0.0,
        ).to(self.device)

        self.sync_target()

    def sync_target(self):
        self.target_net.load_state_dict(self.online_net.state_dict())

    def get_q_values(self, obs: torch.Tensor, use_target: bool = False) -> torch.Tensor:
        net = self.target_net if use_target else self.online_net
        return net(obs)

    def select_action(self, obs_np: np.ndarray, epsilon: float = 0.0) -> int:
        obs_t = torch.FloatTensor(obs_np).unsqueeze(0).to(self.device)
        return self.online_net.select_action(obs_t, epsilon)

    def set_masking_prob(self, prob: float):
        self.online_net.state_masking_prob = prob

    def parameters(self):
        return self.online_net.parameters()

    def train(self):
        self.online_net.train()

    def eval(self):
        self.online_net.eval()
        self.target_net.eval()


# ── Multi-Agent Container ─────────────────────────────────────────────────────

class MultiAgentQMIX:
    """Container for all 4 QMIX agents with gated fusion networks."""

    def __init__(
        self,
        n_agents           = N_AGENTS,
        obs_dim            = OBS_DIM,
        action_dim         = ACTION_DIM,
        state_masking_prob = 0.3,
        device             = None,
    ):
        self.n_agents   = n_agents
        self.obs_dim    = obs_dim
        self.action_dim = action_dim
        self.device     = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.agents = [
            QMIXAgent(
                agent_id           = i,
                obs_dim            = obs_dim,
                action_dim         = action_dim,
                state_masking_prob = state_masking_prob,
                device             = self.device,
            )
            for i in range(n_agents)
        ]

    def select_actions(self, observations: list, epsilon: float = 0.0) -> list:
        assert len(observations) == self.n_agents
        return [
            self.agents[i].select_action(observations[i], epsilon)
            for i in range(self.n_agents)
        ]

    def get_all_q_values(
        self,
        observations_t: torch.Tensor,
        use_target: bool = False,
    ) -> torch.Tensor:
        """observations_t: (batch, n_agents, 374) → (batch, n_agents, 5)"""
        all_q = []
        for i in range(self.n_agents):
            obs_i = observations_t[:, i, :]
            q_i   = self.agents[i].get_q_values(obs_i, use_target)
            all_q.append(q_i)
        return torch.stack(all_q, dim=1)

    def get_chosen_q_values(
        self,
        observations_t: torch.Tensor,
        actions_t:      torch.Tensor,
        use_target:     bool = False,
    ) -> torch.Tensor:
        """observations_t: (batch, n_agents, 374), actions_t: (batch, n_agents)
           → chosen_q: (batch, n_agents)"""
        all_q    = self.get_all_q_values(observations_t, use_target)
        chosen_q = all_q.gather(2, actions_t.unsqueeze(-1)).squeeze(-1)
        return chosen_q

    def sync_all_targets(self):
        for agent in self.agents:
            agent.sync_target()

    def set_masking_prob(self, prob: float):
        for agent in self.agents:
            agent.set_masking_prob(prob)

    def all_parameters(self):
        params = []
        for agent in self.agents:
            params.extend(list(agent.parameters()))
        return params

    def train(self):
        for agent in self.agents:
            agent.train()

    def eval(self):
        for agent in self.agents:
            agent.eval()


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  Gated Fusion QMIX Agents — Quick Verification")
    print("=" * 65)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  Device: {device}")

    # Test 1 — forward pass shape
    net = GatedFusionQNetwork(state_masking_prob=0.0).to(device)
    n_p = sum(p.numel() for p in net.parameters())
    obs = torch.randn(4, OBS_DIM).to(device)
    net.eval()
    q   = net(obs)
    print(f"\n  Test 1 — GatedFusionQNetwork forward pass")
    print(f"  Parameters  : {n_p:,}")
    print(f"  Input shape : {obs.shape}")
    print(f"  Output shape: {q.shape}")
    assert q.shape == (4, ACTION_DIM), f"Shape mismatch: {q.shape}"
    print(f"  Output shape correct")

    # Test 2 — gate values are in (0,1)
    g = net.get_gate_value(obs)
    print(f"\n  Test 2 — Gate values in (0, 1)")
    print(f"  Gate shape  : {g.shape}")
    print(f"  Gate min    : {g.min().item():.4f}  (must be > 0)")
    print(f"  Gate max    : {g.max().item():.4f}  (must be < 1)")
    assert g.shape == (4, BRANCH_DIM)
    assert g.min().item() > 0.0 and g.max().item() < 1.0
    print(f"  Gate values valid")

    # Test 3 — state masking changes output during training
    net.train()
    net.state_masking_prob = 0.9
    q_masked = net(obs)
    net.eval()
    net.state_masking_prob = 0.0
    q_clean  = net(obs)
    diff = (q_masked - q_clean).abs().mean().item()
    print(f"\n  Test 3 — State masking changes output")
    print(f"  Mean |Q_masked - Q_clean| : {diff:.4f}")
    assert diff > 0.0
    print(f"  State masking works correctly")

    # Test 4 — both branches contribute
    net.eval()
    obs_no_h     = obs.clone(); obs_no_h[:, STATE_DIM:] = 0.0
    obs_no_state = obs.clone(); obs_no_state[:, :STATE_DIM] = 0.0
    q_no_h     = net(obs_no_h)
    q_no_state = net(obs_no_state)
    q_full     = net(obs)
    diff_h = (q_full - q_no_h).abs().mean().item()
    diff_s = (q_full - q_no_state).abs().mean().item()
    print(f"\n  Test 4 — Both branches contribute")
    print(f"  |Q_full - Q_h_zeroed|    : {diff_h:.4f}  (h contribution)")
    print(f"  |Q_full - Q_state_zeroed|: {diff_s:.4f}  (state contribution)")
    assert diff_h > 0.0 and diff_s > 0.0
    print(f"  Both branches active")

    # Test 5 — gate behavior under structured vs noisy h
    # Structured h: clear directional signal
    # Noisy h: random values (simulates random attacker)
    base_state  = torch.randn(1, STATE_DIM).to(device)
    struct_h    = torch.ones(1, H_DIM).to(device) * 2.0   # strong signal
    noise_h     = torch.randn(1, H_DIM).to(device) * 0.01  # near-zero noise

    obs_struct = torch.cat([base_state, struct_h], dim=-1)
    obs_noisy  = torch.cat([base_state, noise_h],  dim=-1)

    g_struct = net.get_gate_value(obs_struct).mean().item()
    g_noisy  = net.get_gate_value(obs_noisy).mean().item()
    print(f"\n  Test 5 — Gate adapts to h quality (before training)")
    print(f"  Mean gate (structured h): {g_struct:.4f}")
    print(f"  Mean gate (noisy h)     : {g_noisy:.4f}")
    print(f"  Note: gate direction learned during training.")
    print(f"  After training: noisy h → g→1 (trust telemetry)")
    print(f"                 structured h → g≈0.5 (blend both)")

    # Test 6 — MultiAgentQMIX
    ma = MultiAgentQMIX(state_masking_prob=0.3, device=device)
    ma.eval()
    ma.set_masking_prob(0.0)
    obs_list = [np.random.randn(OBS_DIM).astype(np.float32) for _ in range(N_AGENTS)]
    acts = ma.select_actions(obs_list, epsilon=0.0)
    print(f"\n  Test 6 — MultiAgentQMIX greedy selection")
    print(f"  Actions: {acts}")
    assert len(acts) == N_AGENTS and all(0 <= a < ACTION_DIM for a in acts)
    print(f"  Actions valid")

    # Test 7 — different h → different actions
    base = np.random.randn(STATE_DIM).astype(np.float32)
    obs1 = [np.concatenate([base, np.ones(H_DIM, dtype=np.float32)*2])]  * N_AGENTS
    obs2 = [np.concatenate([base, np.ones(H_DIM, dtype=np.float32)*-2])] * N_AGENTS
    acts1 = ma.select_actions(obs1, epsilon=0.0)
    acts2 = ma.select_actions(obs2, epsilon=0.0)
    print(f"\n  Test 7 — Different h → different actions")
    print(f"  Actions (h=+2): {acts1}")
    print(f"  Actions (h=-2): {acts2}")
    if acts1 != acts2:
        print(f"  h drives action selection")
    else:
        print(f"  Same actions before training — gate learns divergence during training")

    # Test 8 — chosen Q shape
    obs_t = torch.randn(8, N_AGENTS, OBS_DIM).to(device)
    act_t = torch.randint(0, ACTION_DIM, (8, N_AGENTS)).to(device)
    cq    = ma.get_chosen_q_values(obs_t, act_t)
    assert cq.shape == (8, N_AGENTS)
    print(f"\n  Test 8 — Chosen Q-values shape: {cq.shape}  correct")

    print(f"\n  qmix_agent.py (gated fusion) verified")
    print(f"  Retrain all models — old weights incompatible with new gate layer.")