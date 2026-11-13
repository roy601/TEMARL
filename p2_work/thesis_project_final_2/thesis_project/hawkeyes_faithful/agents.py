
# agents.py
# Hawkeyes faithful reproduction — Do Hoang et al. (2026)
# Implements: Section 5.1 — A2C network architecture
# "four fully connected layers with decreasing dimensions
#  (2048-1024-512-64), each followed by ReLU activations"

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from network_topology import HYPERPARAMS

# =============================================================
# DEVICE — use GPU if available (Colab T4)
# =============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")


# =============================================================
# A2C NETWORK — Section 5.1
# Shared backbone + separate actor and critic heads
# =============================================================

class A2CNetwork(nn.Module):
    """
    A2C network with architecture from Section 5.1:
    - 4 fully connected layers: 2048 → 1024 → 512 → 64
    - ReLU activations after each layer
    - Actor head: softmax probability distribution over actions
    - Critic head: scalar state value estimate
    """

    def __init__(self, state_dim, action_dim):
        super(A2CNetwork, self).__init__()

        self.state_dim  = state_dim
        self.action_dim = action_dim

        # --- Shared backbone (Section 5.1) ---
        # "four fully connected layers with decreasing dimensions
        #  (2048-1024-512-64), each followed by ReLU activations"
        self.shared = nn.Sequential(
            nn.Linear(state_dim, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, 64),
            nn.ReLU(),
        )

        # --- Actor head ---
        # "actor head outputs an action probability distribution
        #  via a softmax layer"
        self.actor_head = nn.Linear(64, action_dim)

        # --- Critic head ---
        # "critic head estimates the state value through
        #  a linear layer"
        self.critic_head = nn.Linear(64, 1)

        # Move to GPU
        self.to(DEVICE)

    def forward(self, x):
        """
        Forward pass.
        Returns: (action_probs, state_value)
        """
        # Ensure input is on correct device
        if not isinstance(x, torch.Tensor):
            x = torch.FloatTensor(x).to(DEVICE)
        if x.dim() == 1:
            x = x.unsqueeze(0)  # add batch dimension

        # Shared layers
        features = self.shared(x)

        # Actor — softmax over valid actions
        action_logits = self.actor_head(features)
        action_probs  = F.softmax(action_logits, dim=-1)

        # Critic — scalar value
        state_value = self.critic_head(features)

        return action_probs, state_value

    def get_action(self, state, valid_actions=None):
        """
        Sample an action from the policy.
        Masks invalid actions if valid_actions is provided.

        Returns: (action, log_prob, state_value)
        """
        with torch.no_grad():
            action_probs, state_value = self.forward(state)

        action_probs = action_probs.squeeze(0)  # remove batch dim

        # --- Mask invalid actions ---
        # Only allow actions in valid_actions list
        if valid_actions is not None:
            mask = torch.zeros(self.action_dim).to(DEVICE)
            for a in valid_actions:
                mask[a] = 1.0
            # Zero out invalid actions and renormalize
            masked_probs = action_probs * mask
            prob_sum = masked_probs.sum()
            if prob_sum > 0:
                masked_probs = masked_probs / prob_sum
            else:
                # Fallback: uniform over valid actions
                masked_probs = mask / mask.sum()
            action_probs = masked_probs

        # Sample action from distribution
        dist   = torch.distributions.Categorical(action_probs)
        action = dist.sample()

        return (
            action.item(),
            dist.log_prob(action),
            state_value.squeeze()
        )

    def evaluate_action(self, state, action):
        """
        Evaluate a specific action.
        Used during A2C update to compute loss.

        Returns: (log_prob, state_value, entropy)
        """
        action_probs, state_value = self.forward(state)
        action_probs = action_probs.squeeze(0)

        dist     = torch.distributions.Categorical(action_probs)
        log_prob = dist.log_prob(
            torch.tensor(action).to(DEVICE)
        )
        entropy  = dist.entropy()

        return log_prob, state_value.squeeze(), entropy

    def count_parameters(self):
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters()
                   if p.requires_grad)


# =============================================================
# A2C AGENT — one agent per honeypot
# Each agent controls one honeypot's placement
# =============================================================

class A2CAgent:
    """
    Single A2C agent controlling one honeypot.
    Implements the low-level policy pi_low from Algorithm 1.

    Paper uses:
    - Learning rate: 1e-3
    - Discount factor: 0.99
    - Value loss coefficient: 0.5
    - Optimizer: Adam
    """

    def __init__(self, state_dim, action_dim, agent_id=0):
        self.agent_id   = agent_id
        self.state_dim  = state_dim
        self.action_dim = action_dim

        # Neural network
        self.network = A2CNetwork(state_dim, action_dim)

        # Optimizer — Table 1: Adam
        self.optimizer = optim.Adam(
            self.network.parameters(),
            lr=HYPERPARAMS["learning_rate"]   # 1e-3
        )

        # Hyperparameters — Table 1
        self.gamma   = HYPERPARAMS["gamma"]           # 0.99
        self.cv      = HYPERPARAMS["value_loss_coef"] # 0.5

        # Episode memory — stores (state, action, reward, value)
        self.memory = []

    def select_action(self, state, valid_actions=None):
        """Select action using current policy."""
        return self.network.get_action(state, valid_actions)

    def store(self, state, action, reward, log_prob, value):
        """Store one step of experience. log_prob/value kept for compatibility."""
        self.memory.append({
            "state":  state,
            "action": action,
            "reward": reward,
            # log_prob and value will be RECOMPUTED during update()
            # storing them here just for reference
        })

    def update(self):
        """
        A2C policy update — called at end of episode.
        Recomputes log_probs through network to maintain grad graph.
        """
        if not self.memory:
            return 0.0

        # --- Compute discounted returns ---
        returns = []
        R = 0.0
        for step in reversed(self.memory):
            R = step["reward"] + self.gamma * R
            returns.insert(0, R)

        returns = torch.FloatTensor(returns).to(DEVICE)

        # Normalize returns for stable training
        if len(returns) > 1:
            returns = (returns - returns.mean()) / \
                      (returns.std() + 1e-8)

        # --- Recompute log_probs through network ---
        # Cannot use stored log_probs — they were computed under
        # torch.no_grad() and have no gradient graph
        actor_losses  = []
        critic_losses = []

        for step, R in zip(self.memory, returns):

            # Recompute through network WITH gradient tracking
            state  = step["state"]
            action = step["action"]

            if not isinstance(state, torch.Tensor):
                state = torch.FloatTensor(state).to(DEVICE)
            if state.dim() == 1:
                state = state.unsqueeze(0)

            action_probs, value = self.network(state)
            action_probs = action_probs.squeeze(0)
            value        = value.squeeze()

            # Recompute log_prob WITH grad
            dist     = torch.distributions.Categorical(action_probs)
            log_prob = dist.log_prob(
                torch.tensor(action, dtype=torch.long).to(DEVICE)
            )

            # Advantage = return - baseline (detach value for actor)
            advantage = R - value.detach()

            # Actor loss
            actor_losses.append(-log_prob * advantage)

            # Critic loss — both must be same shape
            critic_losses.append(
                F.mse_loss(value, R)
            )

        # Total loss
        actor_loss  = torch.stack(actor_losses).mean()
        critic_loss = torch.stack(critic_losses).mean()
        total_loss  = actor_loss + self.cv * critic_loss

        # Backpropagation
        self.optimizer.zero_grad()
        total_loss.backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(
            self.network.parameters(), max_norm=0.5
        )

        self.optimizer.step()

        # Clear memory
        self.memory = []

        return total_loss.item()

    def save(self, path):
        """Save model weights."""
        torch.save({
            "network_state":    self.network.state_dict(),
            "optimizer_state":  self.optimizer.state_dict(),
            "agent_id":         self.agent_id,
        }, path)
        print(f"Agent {self.agent_id} saved to {path}")

    def load(self, path):
        """Load model weights."""
        checkpoint = torch.load(path, map_location=DEVICE)
        self.network.load_state_dict(
            checkpoint["network_state"]
        )
        self.optimizer.load_state_dict(
            checkpoint["optimizer_state"]
        )
        print(f"Agent {self.agent_id} loaded from {path}")


# =============================================================
# MULTI-AGENT SYSTEM — coordinates all honeypot agents
# =============================================================

class HawkeyesMARL:
    """
    Coordinates multiple A2C agents.
    Implements shared reward — all agents receive same reward.
    Section 4.3: "shared reward mechanism ensures all agents
    coordinate toward maximizing collective deception"
    """

    def __init__(self, state_dim, action_dim, n_agents=2):
        self.n_agents   = n_agents
        self.state_dim  = state_dim
        self.action_dim = action_dim

        # One A2C agent per honeypot
        self.agents = [
            A2CAgent(state_dim, action_dim, agent_id=i)
            for i in range(n_agents)
        ]

    def select_actions(self, state, valid_actions=None):
        """
        Each agent independently selects an action.
        Returns: list of (action, log_prob, value) per agent
        """
        results = []
        for agent in self.agents:
            action, log_prob, value = agent.select_action(
                state, valid_actions
            )
            results.append((action, log_prob, value))
        return results

    def store_experience(self, state, agent_results,
                         reward):
        """
        Store experience for all agents.
        Shared reward — all agents receive same reward.
        """
        for i, agent in enumerate(self.agents):
            action, log_prob, value = agent_results[i]
            agent.store(state, action, reward, log_prob, value)

    def update_all(self):
        """Update all agents. Returns average loss."""
        losses = [agent.update() for agent in self.agents]
        return np.mean(losses)

    def save_all(self, save_dir, prefix=""):
        """Save all agent models."""
        import os
        os.makedirs(save_dir, exist_ok=True)
        for agent in self.agents:
            path = os.path.join(
                save_dir,
                f"{prefix}agent_{agent.agent_id}.pt"
            )
            agent.save(path)

    def load_all(self, save_dir, prefix=""):
        """Load all agent models."""
        for agent in self.agents:
            path = os.path.join(
                save_dir,
                f"{prefix}agent_{agent.agent_id}.pt"
            )
            agent.load(path)

    def total_parameters(self):
        """Total parameters across all agents."""
        return sum(
            a.network.count_parameters()
            for a in self.agents
        )


# =============================================================
# QUICK VERIFICATION
# =============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AGENTS VERIFICATION")
    print("=" * 60)

    STATE_DIM  = 310   # from environment.py
    ACTION_DIM = 4     # 4 groups

    # Test single network
    net = A2CNetwork(STATE_DIM, ACTION_DIM)
    print(f"\nA2C Network architecture:")
    print(net)
    print(f"\nTotal parameters: {net.count_parameters():,}")

    # Test forward pass
    dummy_state = torch.zeros(STATE_DIM).to(DEVICE)
    probs, value = net(dummy_state)
    print(f"\nForward pass:")
    print(f"  Action probs shape: {probs.shape}")
    print(f"  Action probs sum:   {probs.sum().item():.4f}")
    print(f"  State value:        {value.item():.4f}")

    # Test action selection with masking
    action, log_prob, val = net.get_action(
        dummy_state, valid_actions=[0, 2]
    )
    print(f"\nAction selection (valid=[0,2]):")
    print(f"  Selected action: {action}")
    print(f"  Log prob:        {log_prob.item():.4f}")

    # Test full MARL system
    marl = HawkeyesMARL(STATE_DIM, ACTION_DIM, n_agents=2)
    print(f"\nMARL system:")
    print(f"  Agents:           {marl.n_agents}")
    print(f"  Params per agent: {marl.agents[0].network.count_parameters():,}")
    print(f"  Total params:     {marl.total_parameters():,}")

    # Test one episode
    from environment import HawkeyesEnv
    env = HawkeyesEnv(fnr=0.05, fpr=0.02, attack_strategy="Ran")
    state = env.reset()
    done  = False
    steps = 0

    while not done and steps < 100:
        strategy     = env.get_high_level_strategy()
        valid        = env.get_valid_actions(strategy)
        agent_results = marl.select_actions(state, valid)
        actions      = [r[0] for r in agent_results]
        next_state, reward, done, info = env.step(actions)
        marl.store_experience(state, agent_results, reward)
        state = next_state
        steps += 1

    loss = marl.update_all()
    print(f"\nOne episode test:")
    print(f"  Steps:   {steps}")
    print(f"  Reward:  {reward}")
    print(f"  Done:    {done}")
    print(f"  Loss:    {loss:.6f}")

    print("\nAgents verification complete.")