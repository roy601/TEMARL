# Model equations, paper backing and LSTM upgrade

Update: the optional confidence-aware policy is now implemented and enabled in
the default study as a separate paired ablation. Findings below about the constant
entropy gate describe the retained baseline, not the new confidence arm.
See [CONFIDENCE_PROTOCOL.md](CONFIDENCE_PROTOCOL.md) for calibration, paper mapping,
explicit Transformer/PPO/GAE tests, outputs and scientific limits.

Reviewed and updated: 2026-10-08. Scope: the active `thesis_version_2310_markov_useful`
pipeline. The original `thesis_version_2310` folder was not changed.

## Verdict

The reviewed recurrent equations, padding behavior and PPO policy objective are
consistent with their stated methods. The original LSTM was intentionally a
1997 variant, not a coding error. At the user's request it is now replaced by a
standard forget-gate LSTM. These are small ATT&CK sequence models, not pretrained
natural-language large language models. Paper-backed components do not make
the whole custom deception system a reproduction of any one paper.

## Paper-to-code mapping

| Component | Primary paper / implementation source | What is supported; what is adapted |
|---|---|---|
| Transformer attention, FFN, residuals, sinusoidal positions | [Vaswani et al., Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) | Standard encoder components in `thesis_system/temarl_v2/encoders.py`. Two layers, four heads, d=64, FFN=128 and final pooling are project choices, not the original full encoder-decoder. |
| Flow-based Transformer precedent | [Manocchio et al., FlowTransformer](https://arxiv.org/abs/2304.14746) | Network-security Transformer design precedent. Our ATT&CK-token next-step task is not its flow-classification task; do not claim identical inputs or experimental reproduction. |
| GRU | [Cho et al. (2014), section 2.3, equations 5-8](https://arxiv.org/pdf/1406.1078) | `ChoGRUCell` uses reset-before U(r*h), matching those equations. Biases, stacking and projection are adaptations. It is not PyTorch's reset-after GRU. |
| LSTM origin | [Hochreiter and Schmidhuber (1997)](https://www.bioinf.jku.at/publications/older/2604.pdf) | Historical gated-memory foundation; no longer the complete cell used here. |
| LSTM forget gate | [Gers, Schmidhuber and Cummins (2000), Neural Computation](https://doi.org/10.1162/089976600300015015); [author PDF](https://sferics.idsia.ch/pub/juergen/FgGates-NC.pdf) | Supports adaptive forgetting. Our standard tanh, non-peephole `nn.LSTMCell` is a modern implementation, not a verbatim reproduction of their training algorithm or activation conventions. |
| LSTM component evidence | [Greff et al., LSTM: A Search Space Odyssey, TNNLS (2017)](https://arxiv.org/abs/1503.04069) | Evidence that the forget gate and output activation matter in their tasks, not proof of improvement on CAM-LDS. Their baseline includes details not all used here. |
| Exact modern LSTM equations | [PyTorch LSTMCell documentation](https://docs.pytorch.org/docs/2.14/generated/torch.nn.LSTMCell.html) | Built-in tested cell, independent gates, two affine bias vectors, no peepholes. Used by `ForgetGateLSTMCell`. |
| MAPPO | [Yu et al., The Surprising Effectiveness of PPO in Cooperative, Multi-Agent Games](https://arxiv.org/abs/2103.01955) | Centralized critic and decentralized parameter-shared actors. Our observations, history fusion, rewards and simulator are project adaptations. |
| IPPO | [de Witt et al., Is Independent Learning All You Need in the StarCraft Multi-Agent Challenge?](https://arxiv.org/abs/2011.09533) | Independent/local-value PPO comparison. Here actors are parameter-shared, and both actor and local critic receive shared observed history; not four isolated networks. |
| PPO clipping | [Schulman et al., Proximal Policy Optimization Algorithms (2017)](https://arxiv.org/abs/1707.06347) | Clipped surrogate in `mappo.py`. Entropy bonus and critic settings disclosed as implementation choices. |
| GAE | [Schulman et al., Generalized Advantage Estimation](https://arxiv.org/abs/1506.02438) | Discounted temporal-difference residual recursion, with terminal masks and rollout-end bootstrap. |
| Value normalization / clipped Huber critic | [Official MAPPO source](https://github.com/marlbenchmark/on-policy/blob/main/onpolicy/algorithms/r_mappo/r_mappo.py) | Implementation precedent; our update scheduling is not an exact copy of its trainer. |
| Gated fusion | [Arevalo et al., Gated Multimodal Units (2017)](https://arxiv.org/abs/1702.01992) | The weighted two-branch mixture is GMU-inspired. Our LayerNorm/ReLU branches and gate inputs differ from their tanh/raw-input formulation. |
| Layer normalization | [Ba, Kiros and Hinton (2016)](https://arxiv.org/abs/1607.06450) | Normalization operation; its placement after our recurrent projection is a project choice. |
| AdamW pretraining | [Loshchilov and Hutter, Decoupled Weight Decay Regularization](https://arxiv.org/abs/1711.05101) | Optimizer family. Batch 64, lr=0.0005, decay=0.0001 and clip=1 are experiment choices, not values justified by this citation. |

## Current equations

All multiplications marked `*` below are elementwise; W/U denote learned matrices.

### Upgraded LSTM

```text
i_t = sigmoid(W_i x_t + U_i h_(t-1) + b_i)
f_t = sigmoid(W_f x_t + U_f h_(t-1) + b_f)
g_t = tanh   (W_g x_t + U_g h_(t-1) + b_g)
o_t = sigmoid(W_o x_t + U_o h_(t-1) + b_o)
c_t = f_t * c_(t-1) + i_t * g_t
h_t = o_t * tanh(c_t)
```

Each b is the sum of PyTorch's input and recurrent biases. Initialization uses
the library default, not a specially forced positive forget bias. No peephole
connections or coupled input/forget gates. State resets for each history window.
This also replaces the 1997 scaled sigmoid candidate/output with standard tanh.

### Retained Cho GRU

```text
r_t = sigmoid(W_r x_t + U_r h_(t-1) + b_r)
z_t = sigmoid(W_z x_t + U_z h_(t-1) + b_z)
n_t = tanh(W_n x_t + U_n(r_t * h_(t-1)) + b_n)
h_t = z_t * h_(t-1) + (1-z_t) * n_t
```

### Transformer and prediction

```text
Attention(Q,K,V) = softmax(Q K^T / sqrt(d_k) + padding_mask) V
FFN(x) = ReLU(x W_1 + b_1) W_2 + b_2
p(next technique | observed prefix) = softmax(W_head h_prefix + b_head)
loss = mean negative log probability of the actual next technique
```

Multi-head attention, residual connections, post-layer normalization and dropout
are provided by PyTorch. The inherited encoder adds a final LayerNorm. Pooling
selects the last real token. All tokens supplied are already observed, so
bidirectional attention inside that past-only prefix does not expose the target.
Training/scoring exclude PAD/UNK output logits from the technique softmax.

### PPO and advantages

```text
ratio_t = exp(log pi_new(a_t|o_t) - log pi_old(a_t|o_t))
actor_loss = -mean(min(ratio_t*A_t, clip(ratio_t,1-eps,1+eps)*A_t))
             - entropy_coefficient * mean(policy_entropy)
delta_t = reward_t + gamma*(1-done_t)*V_(t+1) - V_t
A_t = delta_t + gamma*lambda*(1-done_t)*A_(t+1)
```

Values are denormalized for returns/GAE and return targets normalized for critic
training. MAPPO supplies global state to the critic; IPPO does not. The common
actor does not receive the privileged global critic state.

## Capacity and unchanged settings

| Encoder | Layers | Hidden width | Trunk parameters, excluding common embedding/head |
|---|---:|---:|---:|
| Transformer | 2 | 64 | 67,072 |
| Cho GRU | 2 | 73 | 67,279 |
| Forget-gate LSTM | 2 | 62 | 67,152 |

LSTM parameter matching now counts four gates and both PyTorch bias vectors.
GRU still counts three gates and one affine bias vector. The deterministic
search does not use validation/test performance or disturb the initialization RNG.
All arms keep the 64-dimensional output, vocabulary, 16-token window and shared
epoch protocol. Recurrent outputs retain their projection/LayerNorm, inter-layer
dropout and inherited sqrt(64) embedding scaling. These are disclosed project
adaptations, not features copied from the original recurrent papers.

## Review findings and limits

1. **Only 16 previous techniques are visible.** `markov_data.windows` and
   `pretrain_marl.HistoryBank` truncate history. Longer playbooks yield more
   windows but do not test dependencies longer than 16 steps. The LSTM upgrade
   does not change that limitation.
2. **Fusion is not an exact GMU reproduction.** The frozen legacy `policy.py`
   header overstates this. Its two-branch mixture is adapted, as explained above.
   Frozen files were not edited or their integrity hashes bypassed.
3. **No measured confidence signal is passed to the gate.** `mappo.Actor.forward`
   omits entropy, so the inherited gate receives a constant 0.5. It learns from
   telemetry and embeddings, but cannot be described as explicitly
   prediction-entropy-conditioned. Policy entropy regularization is a separate concept.
4. **Saved policy checkpoints are for evaluation, not full training resume.**
   `mappo.train` restores the validation-best actor but returns the final critic;
   `policy.pt` does not contain optimizer or value-normalizer state. Actor-only
   evaluation is unaffected. Do not interpret these as synchronized resumable
   actor/critic snapshots.
5. **Paper backing does not validate simulator assumptions.** Zone dynamics,
   deception payoffs, rewards, capacity penalty and metric definitions require
   their own explicit assumptions and sensitivity checks. None of the model
   papers proves the CAM-LDS Markov-generated episodes are realistic. The
   augmentation study tests usefulness, not causal or operational validity.
6. Equal encoder epochs do not imply equal optimizer updates when augmentation
   changes window counts. The retained repeated-original-window controls address
   this confound. No claim that the LSTM upgrade improves results is made yet.

## Compatibility and verification

- Old no-forget LSTM state dictionaries are incompatible; do not rename/reuse them.
- Existing results and historical validation documents remain unchanged evidence
  of their old fingerprints, not results for this upgraded model.
- Use a fresh output directory. Code fingerprint checking rejects mixing old cells.
- Re-run the epoch pilot and complete study before claiming upgraded-model results.
- `python -m unittest test_bundle test_markov_study -q`: 27 tests passed after
  the upgrade. Includes explicit four-gate equation, forget/retain behavior,
  actual parameter counts, padding, finite gradients, checkpoint round trip,
  future-history isolation, critic locality and Markov-study regressions.
- No full experiment was started. Tests do not establish empirical superiority.
- Independent double-precision LSTM input/state autograd gradcheck passed.
- End-to-end CPU smoke completed: 9 prediction cells (2 epochs each) and 20
  policy cells (16 environment steps each), including LSTM+IPPO and LSTM+MAPPO.
  Report: [smoke RESULTS.md](results_markov/forget_gate_smoke/RESULTS.md).
  These deliberately tiny checks are not scientific performance estimates.

Suggested thesis wording: "We compare a Transformer encoder, a reset-before
Cho GRU, and a standard non-peephole forget-gate LSTM, each adapted to ATT&CK
next-technique prediction with a shared representation interface. Their frozen
representations condition parameter-shared IPPO/MAPPO deception policies."
