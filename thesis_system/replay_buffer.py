# replay_buffer.py
"""
File 6 of 8 — Shared Experience Replay Buffer
================================================
Purpose: Stores transitions from all 4 agents and samples mini-batches
         for QMIX training.

Each transition stores:
  - observations:      (n_agents, 374)  — state + h at time t
  - actions:           (n_agents,)      — actions taken
  - rewards:           (n_agents,)      — shared reward per agent
  - next_observations: (n_agents, 374)  — state + h at time t+1
  - dones:             scalar bool      — episode ended?
  - global_state:      (310,)           — network state only (for mixer)
  - next_global_state: (310,)           — next network state
  - h:                 (64,)            — Transformer h at time t
  - next_h:            (64,)            — Transformer h at time t+1
  - token_seq:         (MAX_SEQ_LEN,)   — attacker sequence for Transformer
  - next_token_seq:    (MAX_SEQ_LEN,)   — next attacker sequence

Design: Circular buffer (oldest transitions overwritten when full).
        Shared across all agents — QMIX is cooperative MARL.
"""

import numpy as np
import torch
from mitre_techniques import MAX_SEQ_LEN

# ── Constants ────────────────────────────────────────────────────────────────
N_AGENTS    = 4
OBS_DIM     = 374
STATE_DIM   = 310
H_DIM       = 64
ACTION_DIM  = 5


class ReplayBuffer:
    """
    Shared circular replay buffer for QMIX.

    Stores transitions as numpy arrays for memory efficiency.
    Converts to torch tensors on sample() call.
    """

    def __init__(self, capacity=50_000, n_agents=N_AGENTS, obs_dim=OBS_DIM,
                 state_dim=STATE_DIM, h_dim=H_DIM, max_seq_len=MAX_SEQ_LEN,
                 device=None):
        self.capacity    = capacity
        self.n_agents    = n_agents
        self.obs_dim     = obs_dim
        self.state_dim   = state_dim
        self.h_dim       = h_dim
        self.max_seq_len = max_seq_len
        self.device      = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.ptr  = 0      # write pointer
        self.size = 0      # current number of stored transitions

        # Pre-allocate arrays
        self.observations      = np.zeros((capacity, n_agents, obs_dim),    dtype=np.float32)
        self.actions           = np.zeros((capacity, n_agents),             dtype=np.int64)
        self.rewards           = np.zeros((capacity, n_agents),             dtype=np.float32)
        self.next_observations = np.zeros((capacity, n_agents, obs_dim),    dtype=np.float32)
        self.dones             = np.zeros((capacity,),                      dtype=np.float32)
        self.global_state      = np.zeros((capacity, state_dim),            dtype=np.float32)
        self.next_global_state = np.zeros((capacity, state_dim),            dtype=np.float32)
        self.h                 = np.zeros((capacity, h_dim),                dtype=np.float32)
        self.next_h            = np.zeros((capacity, h_dim),                dtype=np.float32)
        self.token_seq         = np.zeros((capacity, max_seq_len),          dtype=np.int64)
        self.next_token_seq    = np.zeros((capacity, max_seq_len),          dtype=np.int64)

    def push(
        self,
        observations,       # list of np.ndarray (374,), length n_agents
        actions,            # list of int, length n_agents
        rewards,            # list of float, length n_agents
        next_observations,  # list of np.ndarray (374,), length n_agents
        done,               # bool
        global_state,       # np.ndarray (310,)
        next_global_state,  # np.ndarray (310,)
        h,                  # np.ndarray (64,)
        next_h,             # np.ndarray (64,)
        token_seq,          # np.ndarray (MAX_SEQ_LEN,)
        next_token_seq,     # np.ndarray (MAX_SEQ_LEN,)
    ):
        """Store one transition."""
        idx = self.ptr

        self.observations[idx]      = np.stack(observations)       # (n_agents, 374)
        self.actions[idx]           = np.array(actions)            # (n_agents,)
        self.rewards[idx]           = np.array(rewards)            # (n_agents,)
        self.next_observations[idx] = np.stack(next_observations)  # (n_agents, 374)
        self.dones[idx]             = float(done)
        self.global_state[idx]      = global_state
        self.next_global_state[idx] = next_global_state
        self.h[idx]                 = h
        self.next_h[idx]            = next_h
        self.token_seq[idx]         = token_seq
        self.next_token_seq[idx]    = next_token_seq

        # Advance circular pointer
        self.ptr  = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        """
        Sample a random mini-batch of transitions.

        Returns dict of torch tensors on self.device:
          obs:            (batch, n_agents, 374)
          actions:        (batch, n_agents)
          rewards:        (batch, n_agents)
          next_obs:       (batch, n_agents, 374)
          dones:          (batch,)
          state:          (batch, 310)
          next_state:     (batch, 310)
          h:              (batch, 64)
          next_h:         (batch, 64)
          token_seq:      (batch, MAX_SEQ_LEN)
          next_token_seq: (batch, MAX_SEQ_LEN)
        """
        assert self.size >= batch_size, (
            f"Buffer has {self.size} transitions, need {batch_size}"
        )

        idxs = np.random.randint(0, self.size, size=batch_size)
        d    = self.device

        return {
            "obs":            torch.FloatTensor(self.observations[idxs]).to(d),
            "actions":        torch.LongTensor(self.actions[idxs]).to(d),
            "rewards":        torch.FloatTensor(self.rewards[idxs]).to(d),
            "next_obs":       torch.FloatTensor(self.next_observations[idxs]).to(d),
            "dones":          torch.FloatTensor(self.dones[idxs]).to(d),
            "state":          torch.FloatTensor(self.global_state[idxs]).to(d),
            "next_state":     torch.FloatTensor(self.next_global_state[idxs]).to(d),
            "h":              torch.FloatTensor(self.h[idxs]).to(d),
            "next_h":         torch.FloatTensor(self.next_h[idxs]).to(d),
            "token_seq":      torch.LongTensor(self.token_seq[idxs]).to(d),
            "next_token_seq": torch.LongTensor(self.next_token_seq[idxs]).to(d),
        }

    def __len__(self):
        return self.size

    def is_ready(self, batch_size):
        return self.size >= batch_size


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from mitre_techniques import PAD_ID
    import torch

    print("=" * 55)
    print("  ReplayBuffer — Quick Verification")
    print("=" * 55)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    buf    = ReplayBuffer(capacity=1000, device=device)

    print(f"  Device   : {device}")
    print(f"  Capacity : {buf.capacity}")

    # Push 100 fake transitions
    for i in range(100):
        obs      = [np.random.randn(OBS_DIM).astype(np.float32) for _ in range(N_AGENTS)]
        actions  = [np.random.randint(0, ACTION_DIM) for _ in range(N_AGENTS)]
        rewards  = [float(np.random.randn()) for _ in range(N_AGENTS)]
        next_obs = [np.random.randn(OBS_DIM).astype(np.float32) for _ in range(N_AGENTS)]
        state    = np.random.randn(STATE_DIM).astype(np.float32)
        nstate   = np.random.randn(STATE_DIM).astype(np.float32)
        h        = np.random.randn(H_DIM).astype(np.float32)
        nh       = np.random.randn(H_DIM).astype(np.float32)
        seq      = np.array([PAD_ID]*12 + [0, 1, 9, 12], dtype=np.int64)
        nseq     = np.array([PAD_ID]*11 + [0, 1, 9, 12, 14], dtype=np.int64)

        buf.push(obs, actions, rewards, next_obs, False, state, nstate, h, nh, seq, nseq)

    print(f"\n  Pushed 100 transitions")
    print(f"  Buffer size : {len(buf)}")
    assert len(buf) == 100

    # Sample batch
    batch = buf.sample(32)
    print(f"\n  Sampled batch of 32:")
    for k, v in batch.items():
        print(f"    {k:<16} : {tuple(v.shape)}")

    assert batch["obs"].shape        == (32, N_AGENTS, OBS_DIM)
    assert batch["actions"].shape    == (32, N_AGENTS)
    assert batch["h"].shape          == (32, H_DIM)
    assert batch["token_seq"].shape  == (32, MAX_SEQ_LEN)
    print(f"\n  ✅ All shapes correct")

    # Test circular buffer
    buf2 = ReplayBuffer(capacity=10, device=device)
    for i in range(15):
        buf2.push(obs, actions, rewards, next_obs, False, state, nstate, h, nh, seq, nseq)
    assert len(buf2) == 10, f"❌ Expected 10, got {len(buf2)}"
    print(f"  ✅ Circular overwrite correct (pushed 15, capacity 10, size={len(buf2)})")

    print(f"\n  ✅ replay_buffer.py verified")