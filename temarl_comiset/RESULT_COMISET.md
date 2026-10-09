# Result — COMISET Lab encoder comparison

Pre-registration: `prereg_comiset.py`, committed as `bfde727` before the run.
Corpus: the re-extracted COMISET Lab corpus, fingerprint `35c89d20c5be4a8d`
(6,796 sessions, 27,315 windows, 19 techniques). Device: Intel Arc (xpu),
3,000 steps, batch 256, 10 paired seeds. Full output: `results_comiset/RESULT.txt`.

## Validity gate — 4 of 4 arms pass

Every arm beats both the majority-class baseline (0.3322) and the bigram lookup
table (0.5088) at p < 0.002. The comparison is therefore interpretable.

## All four pre-registered contrasts

| | Contrast | Δ Top-1 | 95% CI | d_z | p_holm | Verdict |
|---|---|---|---|---|---|---|
| H1 | Transformer − GRU | **−0.0090** | [−0.0107, −0.0074] | −3.83 | 0.0000 | **CONTRADICTED** |
| H2 | Transformer − LSTM | **−0.0084** | [−0.0115, −0.0052] | −1.90 | 0.0004 | **CONTRADICTED** |
| H3 | Transformer − SetEncoder | **+0.1609** | [+0.1454, +0.1765] | +7.42 | 0.0000 | **SUPPORTED** |
| H4 | GRU − LSTM | +0.0007 | [−0.0022, +0.0036] | +0.17 | 0.6094 | not significant; TOST-equivalent (p = 0.0000) |

## Per-arm

| Arm | Top-1 | Top-3 | macro-F1 | Perplexity | Params | s/seed |
|---|---|---|---|---|---|---|
| GRU | **0.7295** | 0.9331 | 0.6438 | 2.184 | **50,048** | 121 |
| LSTM | 0.7288 | **0.9341** | 0.6400 | **2.179** | 66,688 | 122 |
| Transformer-RoPE | 0.7205 | 0.9272 | 0.6353 | 2.271 | 67,072 | **61** |
| SetEncoder | 0.5595 | 0.9087 | 0.5647 | 2.989 | 66,240 | 21 |

## What can be claimed

1. **Order in the attacker's technique history carries large predictive value.**
   The order-free SetEncoder loses 16.1 Top-1 points (d_z = 7.42). This is the
   largest effect measured anywhere in the project, and it is a positive result:
   the sequential structure attention is supposed to exploit is demonstrably
   present in real attacker data.
2. **Attention does not exploit it better than recurrence — it does slightly
   worse.** The Transformer loses to both the GRU and the LSTM by roughly 0.9
   Top-1 points, and the difference is significant after Holm correction. This is
   stronger than the CAM-LDS finding, which could only bound the difference near
   zero; here the sign is resolved and it runs against the thesis hypothesis.
3. **GRU and LSTM are interchangeable** (TOST-equivalent within 0.01 Top-1), so
   nothing rests on which recurrent model is used.

## What must NOT be claimed

- That the Transformer is more parameter-efficient here. In this configuration it
  uses **67,072** trunk parameters against the GRU's **50,048** — it is the
  larger model *and* the weaker one. The v5 parameter-efficiency finding
  (Transformer at 44% of GRU parameters) came from a different configuration and
  does not transfer to this one.
- That the Transformer is faster. On this machine it was ~2× faster per seed
  (61 s vs 121 s), but on the CUDA machine it was ~40% *slower* (14 s vs 10 s).
  Relative speed is hardware-dependent and should be reported as such, not as a
  property of the architecture.
- Any DSR claim from this corpus. See `GROUNDING.md`: COMISET's campaign
  headroom is +0.0391, below the 0.05 gate.

## Replication note

An earlier run on the **pre-repair** corpus (5,637 sessions, 10 techniques) on a
different machine and a different GPU gave H1 = −0.0107 and H2 = −0.0068. The
repaired corpus gives −0.0090 and −0.0084. The finding is therefore stable
across two corpora, two machines and two accelerators.
