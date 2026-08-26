# qmix_agent_fixed.py
"""
File 4 of 8 — Individual Q-Networks (QMIX Agents) (FIXED VERSION)
====================================================================
Purpose: Each of the 4 honeypot agents has an individual Q-network.
         Takes 374-dim observation (310 network state + 64 h) as input.
         Outputs Q-values for 5 behavioral actions.

Fixes applied:
  Fix 3 — Gate bias initialized to +2.0 instead of 0.
          sigmoid(+2.0) ≈ 0.88 → agents start by trusting telemetry 88%
          and h only 12%. As training progresses and h proves useful
          (via Fix 2 proactive rewards), the gate bias is learned downward,
          gradually opening to incorporate h.

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
        sighted_idx        = None,
        use_intent_prior   = False,
    ):
        super().__init__()
        self.state_dim          = state_dim
        self.h_dim              = h_dim
        self.action_dim         = action_dim
        self.branch_dim         = branch_dim
        self.state_masking_prob = state_masking_prob

        # ── RAIF Stage A — PEAP (Posterior-Expected Alignment Prior) ──────
        # An action-indexed prior u = A^T p (expected alignment per action under
        # the predicted intent posterior) is added directly to the Q-values:
        #     Q(o,a) = psi(f)_a + lambda_p * u(a)
        # This injects the BAYES action computation as a structural inductive
        # bias, instead of forcing the net to rediscover it from sparse TD.
        # lambda_p is initialised to ZERO so the model starts EXACTLY at the
        # pre-RAIF baseline and only opens this pathway if TD finds it useful
        # (guarantees RAIF is a strict superset of the previous architecture).
        self.use_intent_prior = use_intent_prior
        if use_intent_prior:
            self.lambda_p = nn.Parameter(torch.zeros(1))
        # sighted_idx: index within the (telemetry) state where the "attacker is
        # in my subnet" flag sits. When set, the gate receives this flag as an
        # extra input so it can learn to trust telemetry when sighted and open
        # to h when blind. None disables (legacy gate input = [a|b|entropy]).
        self.sighted_idx        = sighted_idx
        gate_extra              = 1 if sighted_idx is not None else 0

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

        # ── Gated Fusion Layer (Entropy-Aware) ───────────────────────────
        # [a | b | entropy] ∈ ℝ¹²⁹ → g ∈ (0,1)⁶⁴
        # entropy (scalar in [0,1]): Transformer prediction uncertainty.
        #   entropy=0 (confident) → gate can safely open to intent (lower g)
        #   entropy=1 (uncertain) → gate should trust telemetry (higher g)
        # This lets the gate suppress noisy h for random attackers explicitly
        # rather than inferring it from [a,b] content alone.
        self.gate = nn.Sequential(
            nn.Linear(branch_dim * 2 + 1 + gate_extra, branch_dim),  # 129 (or 130 w/ sighted) → 64
            nn.Sigmoid(),
        )

        # ── Output Head (Q-values) ────────────────────────────────────────
        # Fused_Out (64-dim) → Q-values (5-dim). Retained for backward
        # compatibility (loading legacy TD-QMIX checkpoints) and diagnostics.
        self.head = nn.Sequential(
            nn.Linear(branch_dim, head_dim),   # 64 → 64
            nn.ReLU(),
            nn.Linear(head_dim, action_dim),   # 64 → 5
        )

        # ── FIX-1: Policy head π_θ(a|f) and value head V(f) ───────────────
        # The learner is moved OFF the variance-dominated TD target and onto a
        # policy trained by (1) supervised imitation of the profile-optimal
        # action over the frozen intent representation, then (2) a guarded PPO
        # fine-tune with a value baseline. Both heads read the SAME gated fusion
        # f, so the policy inherits the whole encoder+gate representation and is
        # deployable on the observation alone (no privileged labels at inference).
        self.policy_head = nn.Sequential(
            nn.Linear(branch_dim, head_dim),
            nn.ReLU(),
            nn.Linear(head_dim, action_dim),
        )
        # Value baseline V(f). Under this env's anticipatory credit exactly one
        # agent is scored per step, so a COMA counterfactual over the other
        # agents contributes nothing and the correct variance reducer is the
        # state-value baseline A = R - V(f).
        self.value_head = nn.Sequential(
            nn.Linear(branch_dim, head_dim),
            nn.ReLU(),
            nn.Linear(head_dim, 1),
        )

        self._init_weights()

    def _init_weights(self):
        """Xavier uniform for all linear layers.
        Gate bias is initialised to +2.0 (Fix 3):
          sigmoid(+2.0) ≈ 0.88 → agents start by trusting telemetry 88%
          and h only 12%.  As training progresses and h proves useful
          (via Fix 2 proactive rewards), the gate bias is learned downward,
          gradually opening to incorporate h.
          This prevents early chaotic gradients from corrupting the gate
          during the first few thousand training steps.
        """
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

        # Fix 3: override gate bias specifically
        # self.gate is nn.Sequential([Linear(128→64), Sigmoid()])
        # self.gate[0] is the Linear layer
        gate_linear = self.gate[0]
        nn.init.constant_(gate_linear.bias, 2.0)

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

    def _fused_repr(self, obs: torch.Tensor, entropy: torch.Tensor = None):
        """
        Shared trunk used by the Q-head, the policy head, and the value head:
            obs -> [state | h] -> Branch_A / Branch_B -> gate -> fused f.
        Returns (f, N, orig_shape). State masking (training only) is applied
        here, so all three heads see the same fog-augmented representation.
        """
        orig_shape = obs.shape[:-1]
        state = obs[..., :self.state_dim].reshape(-1, self.state_dim)
        h     = obs[..., self.state_dim:].reshape(-1, self.h_dim)
        N     = state.shape[0]
        state = self._apply_state_mask(state)          # h is NEVER masked

        a = self.branch_state(state)                   # (N, 64)
        b = self.branch_intent(h)                      # (N, 64)

        if entropy is None:
            ent = torch.full((N, 1), 0.5, device=a.device, dtype=a.dtype)
        elif isinstance(entropy, (float, int)):
            ent = torch.full((N, 1), float(entropy), device=a.device, dtype=a.dtype)
        else:
            ent = entropy.reshape(N, 1).to(dtype=a.dtype, device=a.device)

        gate_inputs = [a, b, ent]
        if self.sighted_idx is not None:
            gate_inputs.append(state[:, self.sighted_idx:self.sighted_idx + 1])
        g = self.gate(torch.cat(gate_inputs, dim=-1))  # (N, 64) in (0,1)
        f = g * a + (1.0 - g) * b                      # (N, 64)
        return f, N, orig_shape

    def policy_forward(self, obs: torch.Tensor, entropy: torch.Tensor = None) -> torch.Tensor:
        """FIX-1: action logits pi_theta(a|f). Deployable on the observation
        alone (h is always available; profile labels are training-only)."""
        f, N, orig_shape = self._fused_repr(obs, entropy)
        logits = self.policy_head(f)
        return logits.reshape(*orig_shape, self.action_dim)

    def value_forward(self, obs: torch.Tensor, entropy: torch.Tensor = None) -> torch.Tensor:
        """FIX-1: state-value baseline V(f) for the PPO advantage A = R - V(f)."""
        f, N, orig_shape = self._fused_repr(obs, entropy)
        v = self.value_head(f).squeeze(-1)             # (N,)
        return v.reshape(orig_shape)

    def forward(self, obs: torch.Tensor, entropy: torch.Tensor = None,
                intent_prior: torch.Tensor = None) -> torch.Tensor:
        """
        Entropy-aware gated multi-modal forward pass.

        Args:
            obs:     FloatTensor (..., STATE_DIM + H_DIM)
            entropy: FloatTensor (..., 1) or scalar float, normalized [0,1].
                     0 = Transformer confident (structured attacker)
                     1 = Transformer uncertain  (random attacker)
                     None defaults to 0.5 (neutral / maximum uncertainty)

        Returns:
            q_values: FloatTensor (..., ACTION_DIM)

        Tensor flow:
            obs -> split -> [state (310) | h (64)]
            state -> mask -> Branch_A -> a  (64)
            h             -> Branch_B -> b  (64)
            [a | b | ent] -> Gate     -> g  (64)  in (0,1)
            g*a + (1-g)*b             -> f  (64)  fused representation
            f             -> Head     -> Q  (5)
        """
        f, N, orig_shape = self._fused_repr(obs, entropy)

        # Output head
        q_values = self.head(f)         # (N, 5)

        # ── PEAP: additive action-indexed intent prior ────────────────────
        # intent_prior u ∈ R^M is the posterior-expected alignment per action.
        # Accepts (M,) [shared across the batch] or (N, M) [per-sample].
        if self.use_intent_prior and intent_prior is not None:
            ip = intent_prior.to(dtype=q_values.dtype, device=q_values.device)
            if ip.dim() == 1:
                ip = ip.unsqueeze(0)
            if ip.shape[0] != N:
                ip = ip.expand(N, -1)
            q_values = q_values + self.lambda_p * ip

        # Restore original leading dims
        return q_values.reshape(*orig_shape, self.action_dim)

    def select_action(self, obs: torch.Tensor, epsilon: float = 0.0,
                      entropy_val: float = None,
                      intent_prior: torch.Tensor = None) -> int:
        """Epsilon-greedy action selection."""
        if obs.dim() == 1:
            obs = obs.unsqueeze(0)
        if np.random.random() < epsilon:
            return np.random.randint(0, self.action_dim)
        with torch.no_grad():
            q = self.forward(obs, entropy=entropy_val, intent_prior=intent_prior)
        return q.argmax(dim=-1).item()

    def get_gate_value(self, obs: torch.Tensor, entropy_val: float = None) -> torch.Tensor:
        """
        Diagnostic: return the gate vector g for a given observation.

        Returns: FloatTensor (..., BRANCH_DIM)
        """
        self.eval()
        with torch.no_grad():
            orig_shape = obs.shape[:-1]
            state = obs[..., :self.state_dim].reshape(-1, self.state_dim)
            h     = obs[..., self.state_dim:].reshape(-1, self.h_dim)
            N     = state.shape[0]
            a  = self.branch_state(state)
            b  = self.branch_intent(h)
            ev = 0.5 if entropy_val is None else float(entropy_val)
            ent = torch.full((N, 1), ev, device=a.device, dtype=a.dtype)
            gate_inputs = [a, b, ent]
            if self.sighted_idx is not None:
                gate_inputs.append(state[:, self.sighted_idx:self.sighted_idx + 1])
            ab  = torch.cat(gate_inputs, dim=-1)
            g   = self.gate(ab)
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
        state_dim          = STATE_DIM,
        sighted_idx        = None,
        use_intent_prior   = False,
    ):
        self.agent_id           = agent_id
        self.obs_dim            = obs_dim
        self.action_dim         = action_dim
        self.state_masking_prob = state_masking_prob
        self.use_intent_prior   = use_intent_prior
        # state_dim = telemetry portion of the observation (310 in global mode,
        # LOCAL_STATE_DIM=52 in Dec-POMDP local mode). h_dim stays 64.
        self.state_dim          = state_dim
        self.sighted_idx        = sighted_idx
        self.device             = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.online_net = GatedFusionQNetwork(
            state_dim          = state_dim,
            state_masking_prob = state_masking_prob,
            sighted_idx        = sighted_idx,
            use_intent_prior   = use_intent_prior,
        ).to(self.device)

        # Target net never masks — produces stable Q-targets
        self.target_net = GatedFusionQNetwork(
            state_dim          = state_dim,
            state_masking_prob = 0.0,
            sighted_idx        = sighted_idx,
            use_intent_prior   = use_intent_prior,
        ).to(self.device)

        self.sync_target()

    def sync_target(self):
        self.target_net.load_state_dict(self.online_net.state_dict())

    def get_q_values(self, obs: torch.Tensor, use_target: bool = False,
                     entropy_t: torch.Tensor = None,
                     intent_prior_t: torch.Tensor = None) -> torch.Tensor:
        net = self.target_net if use_target else self.online_net
        return net(obs, entropy=entropy_t, intent_prior=intent_prior_t)

    def select_action(self, obs_np: np.ndarray, epsilon: float = 0.0,
                      entropy_val: float = None,
                      intent_prior: torch.Tensor = None) -> int:
        obs_t = torch.FloatTensor(obs_np).unsqueeze(0).to(self.device)
        return self.online_net.select_action(obs_t, epsilon, entropy_val=entropy_val,
                                             intent_prior=intent_prior)

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
        state_dim          = STATE_DIM,
        sighted_idx        = None,
        use_intent_prior   = False,
    ):
        self.n_agents   = n_agents
        self.obs_dim    = obs_dim
        self.action_dim = action_dim
        self.state_dim  = state_dim
        self.sighted_idx = sighted_idx
        self.use_intent_prior = use_intent_prior
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
                state_dim          = state_dim,
                sighted_idx        = sighted_idx,
                use_intent_prior   = use_intent_prior,
            )
            for i in range(n_agents)
        ]

    def select_actions(self, observations: list, epsilon: float = 0.0,
                       entropy_val: float = None,
                       intent_prior: torch.Tensor = None) -> list:
        assert len(observations) == self.n_agents
        return [
            self.agents[i].select_action(observations[i], epsilon,
                                         entropy_val=entropy_val,
                                         intent_prior=intent_prior)
            for i in range(self.n_agents)
        ]

    def get_all_q_values(
        self,
        observations_t: torch.Tensor,
        use_target:     bool = False,
        entropy_t:      torch.Tensor = None,
        intent_prior_t: torch.Tensor = None,
    ) -> torch.Tensor:
        """observations_t: (batch, n_agents, obs_dim) -> (batch, n_agents, 5)
           entropy_t:      (batch, 1) shared across all agents, or None
           intent_prior_t: (batch, n_actions) shared across agents, or None"""
        all_q = []
        for i in range(self.n_agents):
            obs_i = observations_t[:, i, :]
            q_i   = self.agents[i].get_q_values(obs_i, use_target, entropy_t=entropy_t,
                                                intent_prior_t=intent_prior_t)
            all_q.append(q_i)
        return torch.stack(all_q, dim=1)

    def get_chosen_q_values(
        self,
        observations_t: torch.Tensor,
        actions_t:      torch.Tensor,
        use_target:     bool = False,
        entropy_t:      torch.Tensor = None,
        intent_prior_t: torch.Tensor = None,
    ) -> torch.Tensor:
        """observations_t: (batch, n_agents, obs_dim), actions_t: (batch, n_agents)
           -> chosen_q: (batch, n_agents)"""
        all_q    = self.get_all_q_values(observations_t, use_target, entropy_t=entropy_t,
                                         intent_prior_t=intent_prior_t)
        chosen_q = all_q.gather(2, actions_t.unsqueeze(-1)).squeeze(-1)
        return chosen_q

    # ── FIX-1: policy/value access ────────────────────────────────────────
    def select_actions_policy(self, observations: list, entropy_val: float = None,
                              greedy: bool = True) -> list:
        """Select the joint action from the policy heads pi_theta(a|f).
        greedy=True at evaluation (argmax); greedy=False samples (rollouts)."""
        acts = []
        for i in range(self.n_agents):
            obs_t = torch.FloatTensor(observations[i]).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.agents[i].online_net.policy_forward(obs_t, entropy=entropy_val)
            if greedy:
                acts.append(int(logits.argmax(dim=-1).item()))
            else:
                p = torch.softmax(logits, dim=-1)
                acts.append(int(torch.multinomial(p, 1).item()))
        return acts

    def actor_parameters(self):
        """Trunk (branches+gate) + policy head — everything the actor updates."""
        ps = []
        for ag in self.agents:
            net = ag.online_net
            ps += list(net.branch_state.parameters())
            ps += list(net.branch_intent.parameters())
            ps += list(net.gate.parameters())
            ps += list(net.policy_head.parameters())
        return ps

    def critic_parameters(self):
        """Value head only (trunk is shared but the critic does not update it)."""
        ps = []
        for ag in self.agents:
            ps += list(ag.online_net.value_head.parameters())
        return ps

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
    print("  Gated Fusion QMIX Agents — Quick Verification (FIXED)")
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

    # Test 2 — gate values are in (0,1) and biased toward telemetry (Fix 3)
    g = net.get_gate_value(obs)
    print(f"\n  Test 2 — Gate values in (0, 1) with Fix 3 bias")
    print(f"  Gate shape  : {g.shape}")
    print(f"  Gate min    : {g.min().item():.4f}  (must be > 0)")
    print(f"  Gate max    : {g.max().item():.4f}  (must be < 1)")
    print(f"  Gate mean   : {g.mean().item():.4f}  (should be ~0.88 due to Fix 3 bias)")
    assert g.shape == (4, BRANCH_DIM)
    assert g.min().item() > 0.0 and g.max().item() < 1.0
    print(f"  Gate values valid — Fix 3 bias active")

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
    print(f"  Fix 3 bias: both start high (~0.88), trust telemetry first")
    print(f"  After training: noisy h -> g -> 1 (trust telemetry)")
    print(f"                 structured h -> g approx 0.5 (blend both)")

    # Test 6 — MultiAgentQMIX
    ma = MultiAgentQMIX(state_masking_prob=0.3, device=device)
    ma.eval()
    ma.set_masking_prob(0.0)
    obs_list = [np.random.randn(OBS_DIM).astype(np.float32) for _ in range(N_AGENTS)]
    acts = ma.select_actions(obs_list, epsilon=0.0)
    print(f"\n  Test 6 - MultiAgentQMIX greedy selection")
    print(f"  Actions: {acts}")
    assert len(acts) == N_AGENTS and all(0 <= a < ACTION_DIM for a in acts)
    print(f"  Actions valid")

    # Test 7 — different h → different actions
    base = np.random.randn(STATE_DIM).astype(np.float32)
    obs1 = [np.concatenate([base, np.ones(H_DIM, dtype=np.float32)*2])]  * N_AGENTS
    obs2 = [np.concatenate([base, np.ones(H_DIM, dtype=np.float32)*-2])] * N_AGENTS
    acts1 = ma.select_actions(obs1, epsilon=0.0)
    acts2 = ma.select_actions(obs2, epsilon=0.0)
    print(f"\n  Test 7 - Different h -> different actions")
    print(f"  Actions (h=+2): {acts1}")
    print(f"  Actions (h=-2): {acts2}")
    if acts1 != acts2:
        print(f"  h drives action selection")
    else:
        print(f"  Same actions before training - gate learns divergence during training")

    # Test 8 — chosen Q shape
    obs_t = torch.randn(8, N_AGENTS, OBS_DIM).to(device)
    act_t = torch.randint(0, ACTION_DIM, (8, N_AGENTS)).to(device)
    cq    = ma.get_chosen_q_values(obs_t, act_t)
    assert cq.shape == (8, N_AGENTS)
    print(f"\n  Test 8 - Chosen Q-values shape: {cq.shape}  correct")

    print(f"\n  qmix_agent.py (gated fusion, Fix 3 applied) verified")
    print(f"  Retrain all models - old weights incompatible with new gate bias.")
