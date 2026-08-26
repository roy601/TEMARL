# transformer_encoder.py
"""
File 3 of 8 — Transformer Encoder
====================================
Purpose: Encodes attacker's MITRE technique sequence into hidden state h ∈ ℝ⁶⁴.
         h captures attacker intent from the full sequence history.

Architecture (locked):
  - Embedding:      VOCAB_SIZE(22) → 64
  - Positional enc: sinusoidal, max_len=16
  - Encoder:        2 layers, 4 heads, d_model=64, d_ff=128
  - Pooling:        Last Token Pooling (position MAX_SEQ_LEN-1)
  - Output:         h ∈ ℝ⁶⁴

Reference: FlowTransformer [8] — Last Token Pooling guidance
           Thesis architecture section (Transformer h ∈ ℝ⁶⁴, 2 enc layers, 4 heads)
"""

import torch
import torch.nn as nn
import math
import numpy as np
from mitre_techniques import VOCAB_SIZE, MAX_SEQ_LEN, PAD_ID

# ── Constants ────────────────────────────────────────────────────────────────

D_MODEL   = 64    # Transformer hidden dimension — matches h_dim
N_HEADS   = 4     # Attention heads
N_LAYERS  = 2     # Encoder layers
D_FF      = 128   # Feed-forward inner dimension (2 × D_MODEL)
DROPOUT   = 0.1


# ── Sinusoidal Positional Encoding ────────────────────────────────────────────

class PositionalEncoding(nn.Module):
    """
    Standard sinusoidal positional encoding.
    Adds position information to token embeddings.
    """

    def __init__(self, d_model=D_MODEL, max_len=MAX_SEQ_LEN, dropout=DROPOUT):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        # Build PE matrix — shape (max_len, d_model)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        # Register as buffer — not a parameter, but saved with model
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        x: (batch, seq_len, d_model)
        Returns: (batch, seq_len, d_model) — with positional info added
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


# ── Transformer Encoder ───────────────────────────────────────────────────────

class AttackerIntentEncoder(nn.Module):
    """
    Transformer encoder that maps attacker technique sequence → h ∈ ℝ⁶⁴.

    Input:  token sequence of MITRE technique IDs, shape (batch, MAX_SEQ_LEN)
    Output: h, shape (batch, 64) — attacker intent embedding

    Pooling strategy: Last Token Pooling
      - The last non-PAD token carries the most recent attacker intent
      - Consistent with FlowTransformer [8] approach
      - Alternative (CLS token) requires extra token — avoided for simplicity

    Pre-training objective (in train_thesis.py):
      - Next technique prediction: given sequence [t1,...,tn], predict t_{n+1}
      - Forces h to encode sequential attacker behavior patterns
    """

    def __init__(
        self,
        vocab_size = VOCAB_SIZE,
        d_model    = D_MODEL,
        n_heads    = N_HEADS,
        n_layers   = N_LAYERS,
        d_ff       = D_FF,
        max_len    = MAX_SEQ_LEN,
        dropout    = DROPOUT,
        pad_id     = PAD_ID,
    ):
        super().__init__()
        self.d_model = d_model
        self.pad_id  = pad_id
        self.max_len = max_len

        # Confidence calibration temperature (intent-mechanism fix). The raw
        # next-technique predictor is over-confident for some strategies (e.g.
        # HiC: ~49% top-1 accuracy but low entropy), which makes the entropy-aware
        # gate wrongly trust h and commit to specialized actions on mispredictions.
        # A fitted temperature > 1 flattens the softmax so the reported entropy
        # reflects true reliability, letting the gate hedge when h is unreliable.
        # 1.0 = uncalibrated. Set via set_temperature() (fit offline, saved to
        # results/encoder_temperature.json). Kept as a plain attribute (NOT a
        # buffer) so it never affects state_dict load/save compatibility.
        self.temperature = 1.0

        # Token embedding
        self.embedding = nn.Embedding(
            num_embeddings = vocab_size,
            embedding_dim  = d_model,
            padding_idx    = pad_id,   # PAD tokens get zero gradient
        )

        # Positional encoding
        self.pos_enc = PositionalEncoding(d_model, max_len, dropout)

        # Transformer encoder stack
        encoder_layer = nn.TransformerEncoderLayer(
            d_model         = d_model,
            nhead           = n_heads,
            dim_feedforward = d_ff,
            dropout         = dropout,
            batch_first     = True,    # input shape: (batch, seq, d_model)
            norm_first      = False,   # Post-LN (standard)
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers = n_layers,
            norm       = nn.LayerNorm(d_model),
            enable_nested_tensor = False,  # disable nested tensor — crashes on all-PAD
        )

        # Pre-training head: predict next technique (not used after pre-training)
        self.pretrain_head = nn.Linear(d_model, vocab_size)

        self._init_weights()

    def _init_weights(self):
        """Xavier initialization for embedding and output head."""
        nn.init.xavier_uniform_(self.embedding.weight)
        nn.init.xavier_uniform_(self.pretrain_head.weight)
        nn.init.zeros_(self.pretrain_head.bias)

    def _make_padding_mask(self, token_ids):
        """
        Create boolean padding mask for Transformer.
        True = position should be IGNORED (is PAD).

        token_ids: (batch, seq_len)
        Returns:   (batch, seq_len) bool tensor
        """
        return token_ids == self.pad_id

    def _guard_all_pad(self, token_ids):
        """
        Guard against all-PAD sequences which crash PyTorch nested tensor.
        If every token in a sequence is PAD, replace the last position with
        technique 0 (T1190) so the Transformer has at least one real token.

        This edge case occurs at episode start before attacker has acted.
        h output for these sequences is meaningless anyway — agents will
        use epsilon-greedy random actions at episode start.
        """
        all_pad = (token_ids == self.pad_id).all(dim=1)  # (batch,) bool
        if all_pad.any():
            token_ids = token_ids.clone()
            token_ids[all_pad, -1] = 0  # replace last PAD with T1190 (id=0)
        return token_ids

    def forward(self, token_ids):
        """
        Encode token sequence → h.

        Args:
            token_ids: LongTensor (batch, MAX_SEQ_LEN)
                       PAD tokens have id=PAD_ID (20)

        Returns:
            h: FloatTensor (batch, D_MODEL=64)
               Last Token Pooling output — attacker intent vector
        """
        # Guard: replace all-PAD sequences to avoid nested tensor crash
        token_ids = self._guard_all_pad(token_ids)

        # Build padding mask
        pad_mask = self._make_padding_mask(token_ids)  # (batch, seq)

        # Embed tokens
        x = self.embedding(token_ids)   # (batch, seq, 64)
        x = self.pos_enc(x)             # (batch, seq, 64) + position

        # Scale embeddings (standard Transformer practice)
        x = x * math.sqrt(self.d_model)

        # Transformer encoder — self-attention over full sequence
        x = self.transformer(
            x,
            src_key_padding_mask = pad_mask,
        )  # (batch, seq, 64)

        # Last Token Pooling — extract the last non-PAD position
        h = self._last_token_pool(x, token_ids)  # (batch, 64)

        return h

    def _last_token_pool(self, encoded, token_ids):
        """
        Extract the representation at the last non-PAD position.

        For a sequence [PAD, PAD, T1190, T1566, T1059]:
          Last non-PAD position = index 4 (T1059)
          h = encoded[:, 4, :]

        This is the most recent attacker technique — carries current intent.

        encoded:   (batch, seq, d_model)
        token_ids: (batch, seq) — used to find last non-PAD position
        Returns:   (batch, d_model)
        """
        # Find last non-PAD position for each sequence in batch
        is_not_pad     = (token_ids != self.pad_id).long()  # (batch, seq)
        last_positions = is_not_pad.sum(dim=1) - 1          # (batch,)
        last_positions = last_positions.clamp(min=0)        # safety clamp

        # Gather encoding at last position for each batch item
        idx = last_positions.unsqueeze(1).unsqueeze(2).expand(-1, 1, encoded.size(2))
        h   = encoded.gather(1, idx).squeeze(1)  # (batch, d_model)

        return h

    def encode(self, token_ids):
        """
        Convenience method — same as forward() but named explicitly.
        Used in training loop to distinguish from pretrain_forward().
        """
        return self.forward(token_ids)

    def pretrain_forward(self, token_ids):
        """
        Pre-training forward pass.
        Returns logits over vocab for next-technique prediction.

        Used ONLY during pre-training phase in train_thesis.py.
        After pre-training, only encode() is used.

        Returns:
            h:      (batch, 64)         — intent embedding
            logits: (batch, vocab_size) — next technique prediction
        """
        h      = self.forward(token_ids)
        logits = self.pretrain_head(h)   # (batch, vocab_size)
        return h, logits

    def set_temperature(self, t: float):
        """Set the calibration temperature (>1 = less confident, more entropy)."""
        self.temperature = float(max(t, 1e-3))

    def calibrated_entropy(self, logits: torch.Tensor) -> torch.Tensor:
        """Normalized [0,1] predictive entropy of logits AFTER temperature scaling.
        Shared by the numpy helper and the QMIX update so training and inference
        use identical calibrated entropy. logits: (..., VOCAB_SIZE)."""
        probs = torch.softmax(logits / self.temperature, dim=-1)
        ent   = -(probs * torch.log(probs + 1e-8)).sum(dim=-1)
        return ent / math.log(VOCAB_SIZE)

    def get_h_numpy(self, token_ids_np, device):
        """
        Utility: Convert numpy sequence → h numpy array.
        Used in environment step loop.

        token_ids_np: np.ndarray shape (MAX_SEQ_LEN,) or (batch, MAX_SEQ_LEN)
        device:       torch.device
        Returns:      np.ndarray shape (64,) or (batch, 64)
        """
        single = (token_ids_np.ndim == 1)
        if single:
            token_ids_np = token_ids_np[np.newaxis, :]  # (1, seq)

        with torch.no_grad():
            t    = torch.LongTensor(token_ids_np).to(device)
            h    = self.forward(t)           # (batch, 64)
            h_np = h.cpu().numpy()

        return h_np[0] if single else h_np

    def get_h_and_entropy_numpy(self, token_ids_np, device):
        """
        Returns h and normalized prediction entropy in a single forward pass.

        Entropy measures how uncertain the Transformer is about the next technique:
          entropy=0.0  Transformer fully confident (structured attacker, e.g. HiE)
          entropy=1.0  Transformer fully uncertain (random attacker, e.g. Ran)

        Normalization: entropy / log(VOCAB_SIZE) -> [0, 1]

        token_ids_np: np.ndarray shape (MAX_SEQ_LEN,)
        device:       torch.device
        Returns:      h np.ndarray (64,), entropy float in [0, 1]
        """
        single = (token_ids_np.ndim == 1)
        if single:
            token_ids_np = token_ids_np[np.newaxis, :]

        with torch.no_grad():
            t      = torch.LongTensor(token_ids_np).to(device)
            h      = self.forward(t)                                     # (batch, 64)
            logits = self.pretrain_head(h)                               # (batch, VOCAB_SIZE)
            ent_norm = self.calibrated_entropy(logits)                   # temperature-scaled [0,1]
            h_np     = h.cpu().numpy()
            ent_np   = ent_norm.cpu().numpy()

        if single:
            return h_np[0], float(ent_np[0])
        return h_np, ent_np


# ── Quick Test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import torch

    print("=" * 55)
    print("  AttackerIntentEncoder — Quick Verification")
    print("=" * 55)

    device  = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder = AttackerIntentEncoder().to(device)

    n_params = sum(p.numel() for p in encoder.parameters() if p.requires_grad)
    print(f"  Device          : {device}")
    print(f"  Parameters      : {n_params:,}")
    print(f"  D_MODEL         : {D_MODEL}")
    print(f"  N_HEADS         : {N_HEADS}")
    print(f"  N_LAYERS        : {N_LAYERS}")
    print(f"  MAX_SEQ_LEN     : {MAX_SEQ_LEN}")
    print(f"  VOCAB_SIZE      : {VOCAB_SIZE}")

    batch_size = 4
    token_ids  = torch.full((batch_size, MAX_SEQ_LEN), PAD_ID, dtype=torch.long).to(device)
    token_ids[0, 12:] = torch.tensor([0, 1, 2, 9])
    token_ids[1, 8:]  = torch.tensor([0, 2, 4, 7, 9, 12, 14, 15])
    token_ids[2, :]   = torch.arange(0, MAX_SEQ_LEN)
    token_ids[3, :]   = PAD_ID  # all-PAD edge case — must not crash

    # Test 1 — forward pass including all-PAD
    h = encoder(token_ids)
    print(f"\n  Test 1 — Forward pass (including all-PAD row)")
    print(f"  Input shape   : {token_ids.shape}")
    print(f"  Output h shape: {h.shape}")
    assert h.shape == (batch_size, D_MODEL)
    print(f"  ✅ Output shape correct: {h.shape}")

    # Test 2 — pre-training forward
    h2, logits = encoder.pretrain_forward(token_ids)
    print(f"\n  Test 2 — Pre-training forward")
    print(f"  h shape     : {h2.shape}")
    print(f"  Logits shape: {logits.shape}")
    assert logits.shape == (batch_size, VOCAB_SIZE)
    print(f"  ✅ Pre-training head correct")

    # Test 3 — numpy utility
    seq_np = np.array([PAD_ID]*12 + [0, 1, 9, 12], dtype=np.int64)
    h_np   = encoder.get_h_numpy(seq_np, device)
    print(f"\n  Test 3 — Numpy utility")
    assert h_np.shape == (D_MODEL,)
    print(f"  ✅ Numpy utility correct: {h_np.shape}")

    # Test 4 — all-PAD does not crash
    all_pad_seq = np.array([PAD_ID]*MAX_SEQ_LEN, dtype=np.int64)
    h_pad = encoder.get_h_numpy(all_pad_seq, device)
    assert h_pad.shape == (D_MODEL,)
    print(f"\n  Test 4 — All-PAD sequence (episode start edge case)")
    print(f"  ✅ All-PAD handled correctly, no crash")

    # Test 5 — sequence sensitivity
    h1   = encoder(token_ids[0:1])
    h2   = encoder(token_ids[1:2])
    diff = (h1 - h2).abs().mean().item()
    print(f"\n  Test 5 — Sequence sensitivity")
    print(f"  Mean |h1 - h2| : {diff:.4f}")
    assert diff > 0.0
    print(f"  ✅ Different sequences → different h")

    print(f"\n  ✅ transformer_encoder.py verified")