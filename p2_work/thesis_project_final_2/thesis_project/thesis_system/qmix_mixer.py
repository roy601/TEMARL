# qmix_mixer.py
"""
File 5 of 8 — QMIX Mixing Network
=====================================
Purpose: Combines individual agent Q-values into global Q_total.
         Uses h as hypernetwork input — h dynamically changes mixing weights.

Two roles of h in this file:
  1. Hypernetwork weights: h generates W1, b1, W2, b2 of the mixer
     → different attacker intents → different mixing strategies
  2. Coordination signal: when h="credential-seeking", mixer weights
     the agent who placed credential_store more heavily

Architecture:
  Input:   agent_qs (batch, 4) + global_state (batch, 310) + h (batch, 64)
  Hyper 1: Linear(374, 128) → ReLU → Linear(128, 4×64) → reshape W1 (4,64)
  Hyper 2: Linear(374, 64)  → b1
  Hyper 3: Linear(374, 128) → ReLU → Linear(128, 64)  → W2 (64,1)
  Hyper 4: Linear(374, 64)  → ReLU → Linear(64, 1)    → b2
  Mix:     hidden = ELU(W1 @ qs + b1), Q_total = W2 @ hidden + b2

Monotonicity constraint: abs() on W1 and W2 ensures
  ∂Q_total/∂Q_i ≥ 0 for all agents i
  (individual agents always contribute positively to global value)

Reference: QMIX paper (Rashid et al., 2018)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

# ── Constants ────────────────────────────────────────────────────────────────
N_AGENTS      = 4
STATE_DIM     = 310   # Hawkeyes network state (without h)
H_DIM         = 64    # Transformer hidden state
EMBED_DIM     = 64    # Mixing network hidden dimension
STATE_H_DIM   = STATE_DIM + H_DIM   # 374 — hypernetwork input


class QMIXMixer(nn.Module):
    """
    QMIX mixing network with Transformer h as hypernetwork input.

    Key insight: h does NOT just add information — it GENERATES the mixing
    weights themselves. This means the coordination strategy (how to combine
    agent Q-values) changes dynamically based on attacker intent.

    Example:
      h = "credential-seeking pattern"
      → hyper_w1 outputs weights that upweight Agent 3 (credential_store)
      → Q_total reflects that Agent 3's action is most valuable this step

      h = "reconnaissance pattern"
      → hyper_w1 upweights Agent 1 (banner_modification)
      → Different coordination for different attacker behavior
    """

    def __init__(
        self,
        n_agents   = N_AGENTS,
        state_dim  = STATE_DIM,
        h_dim      = H_DIM,
        embed_dim  = EMBED_DIM,
    ):
        super().__init__()
        self.n_agents  = n_agents
        self.state_dim = state_dim
        self.h_dim     = h_dim
        self.embed_dim = embed_dim
        input_dim = state_dim + h_dim  # 374

        # ── Hypernetwork 1 — generates W1 (n_agents × embed_dim) ──────────
        # W1 shape: (n_agents, embed_dim) = (4, 64)
        self.hyper_w1 = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, n_agents * embed_dim),
        )

        # ── Hypernetwork 2 — generates b1 (embed_dim,) ────────────────────
        self.hyper_b1 = nn.Linear(input_dim, embed_dim)

        # ── Hypernetwork 3 — generates W2 (embed_dim,) ────────────────────
        # W2 shape: (embed_dim, 1) = (64, 1)
        self.hyper_w2 = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, embed_dim),
        )

        # ── Hypernetwork 4 — generates b2 (scalar) ────────────────────────
        self.hyper_b2 = nn.Sequential(
            nn.Linear(input_dim, embed_dim),
            nn.ReLU(),
            nn.Linear(embed_dim, 1),
        )

        self._init_weights()

    def _init_weights(self):
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self, agent_qs, global_state, h):
        """
        Mix individual Q-values into global Q_total.

        Args:
            agent_qs:     FloatTensor (batch, n_agents)     — individual Q-values
            global_state: FloatTensor (batch, state_dim)    — network state (310-dim)
            h:            FloatTensor (batch, h_dim)        — Transformer output (64-dim)

        Returns:
            Q_total: FloatTensor (batch, 1)
        """
        batch_size = agent_qs.size(0)

        # Concatenate state and h for hypernetwork input
        state_h = torch.cat([global_state, h], dim=-1)  # (batch, 374)

        # ── Layer 1 ───────────────────────────────────────────────────────
        # Generate W1 from hypernetwork — abs() enforces monotonicity
        w1 = torch.abs(self.hyper_w1(state_h))               # (batch, n_agents*embed)
        w1 = w1.view(batch_size, self.n_agents, self.embed_dim)  # (batch, 4, 64)

        b1 = self.hyper_b1(state_h).unsqueeze(1)             # (batch, 1, embed_dim)

        # agent_qs: (batch, n_agents) → (batch, 1, n_agents) for bmm
        qs = agent_qs.unsqueeze(1)                            # (batch, 1, 4)

        # First mixing: hidden = ELU(qs @ W1 + b1)
        hidden = F.elu(torch.bmm(qs, w1) + b1)               # (batch, 1, embed_dim)

        # ── Layer 2 ───────────────────────────────────────────────────────
        # Generate W2 from hypernetwork — abs() enforces monotonicity
        w2 = torch.abs(self.hyper_w2(state_h))               # (batch, embed_dim)
        w2 = w2.unsqueeze(-1)                                 # (batch, embed_dim, 1)

        b2 = self.hyper_b2(state_h)                          # (batch, 1)

        # Final mixing: Q_total = hidden @ W2 + b2
        Q_total = torch.bmm(hidden, w2).squeeze(-1) + b2     # (batch, 1)

        return Q_total

    def get_mixing_weights(self, global_state, h):
        """
        Diagnostic utility — returns W1 weights for analysis.
        Used in ablation experiments to show h changes mixing strategy.

        Returns: w1 (batch, n_agents, embed_dim) normalized row weights
        """
        state_h = torch.cat([global_state, h], dim=-1)
        w1 = torch.abs(self.hyper_w1(state_h))
        batch_size = global_state.size(0)
        w1 = w1.view(batch_size, self.n_agents, self.embed_dim)
        return w1


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import torch

    print("=" * 55)
    print("  QMIXMixer — Quick Verification")
    print("=" * 55)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mixer  = QMIXMixer().to(device)

    n_params = sum(p.numel() for p in mixer.parameters())
    print(f"  Device      : {device}")
    print(f"  Parameters  : {n_params:,}")

    batch = 8

    # Test 1 — forward pass
    agent_qs = torch.randn(batch, N_AGENTS).to(device)
    state    = torch.randn(batch, STATE_DIM).to(device)
    h        = torch.randn(batch, H_DIM).to(device)
    Q_total  = mixer(agent_qs, state, h)

    print(f"\n  Test 1 — Forward pass")
    print(f"  agent_qs shape : {agent_qs.shape}")
    print(f"  state shape    : {state.shape}")
    print(f"  h shape        : {h.shape}")
    print(f"  Q_total shape  : {Q_total.shape}")
    assert Q_total.shape == (batch, 1)
    print(f"  ✅ Q_total shape correct")

    # Test 2 — monotonicity (key QMIX constraint)
    # Increase one agent's Q-value — Q_total must increase or stay same
    agent_qs_higher         = agent_qs.clone()
    agent_qs_higher[:, 0]  += 10.0  # boost Agent 0
    Q_total_higher          = mixer(agent_qs_higher, state, h)
    monotone = (Q_total_higher >= Q_total - 1e-5).all()
    print(f"\n  Test 2 — Monotonicity constraint")
    print(f"  Q_total original : {Q_total.mean().item():.4f}")
    print(f"  Q_total higher   : {Q_total_higher.mean().item():.4f}")
    print(f"  Monotone         : {monotone.item()}")
    assert monotone.item(), "❌ Monotonicity violated"
    print(f"  ✅ Monotonicity satisfied")

    # Test 3 — h changes Q_total (key thesis property)
    h_zero  = torch.zeros(batch, H_DIM).to(device)
    h_real  = torch.randn(batch, H_DIM).to(device)
    Q_zero  = mixer(agent_qs, state, h_zero)
    Q_real  = mixer(agent_qs, state, h_real)
    diff    = (Q_zero - Q_real).abs().mean().item()
    print(f"\n  Test 3 — h changes Q_total")
    print(f"  Q_total (h=0)   : {Q_zero.mean().item():.4f}")
    print(f"  Q_total (h=real): {Q_real.mean().item():.4f}")
    print(f"  Mean |diff|     : {diff:.4f}")
    assert diff > 0.0, "❌ h has no effect on Q_total"
    print(f"  ✅ h changes mixing (Transformer integration confirmed)")

    # Test 4 — gradient flow through mixer
    optimizer = torch.optim.Adam(mixer.parameters(), lr=1e-3)
    loss = Q_total.mean()
    loss.backward()
    grad_norm = sum(
        p.grad.norm().item() for p in mixer.parameters() if p.grad is not None
    )
    print(f"\n  Test 4 — Gradient flow")
    print(f"  Gradient norm : {grad_norm:.4f}")
    assert grad_norm > 0.0, "❌ No gradients flowing"
    print(f"  ✅ Gradients flow correctly")

    print(f"\n  ✅ qmix_mixer.py verified")