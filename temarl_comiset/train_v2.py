# -*- coding: utf-8 -*-
"""
TEMARL v2 — Two-Stage Training
==============================
Closes F-ARC-03 (encoder co-training divergence), F-DAT-06 (class imbalance),
F-EVL-01/02 (missing trivial baselines), and carries FIX-1 (policy learner).

STAGE 1  supervised encoder adaptation  -> then FREEZE (requires_grad=False + eval())
STAGE 2a policy imitation of a*(profile) over the frozen h
STAGE 2b guarded PPO fine-tune (value baseline; best-by-eval checkpoint)
   [alt] TD-QMIX arm, retained as a COMPARISON POINT on the corrected environment

WHY TWO STAGES (F-ARC-03)
-------------------------
v1 put encoder + agents + mixer in ONE Adam at lr 1e-3 with L = L_TD + 0.1*L_aux.
The encoder therefore received TD gradients, so h moved every step and the
Q-network's input distribution was non-stationary; `encoder.train()` also left
dropout live, so h was stochastic per forward pass. Measured consequence:

    Thesis  TD loss 4.3 -> 7.9   (rising, never converges)
    NoTrans TD loss 9.6 -> 0.84  (h frozen at 0 => stationary => converges)

with flat Q (range ~0.1) and near-uniform actions. Two-timescale stochastic
approximation (Borkar 1997) requires the representation to move on a SLOWER
timescale than the value function; a single shared lr provides no such
separation. v2 adapts the encoder first, then freezes it, so h is deterministic
and stationary. assert_encoder_frozen() enforces this at every call site.

WHY A POLICY LEARNER (FIX-1)
---------------------------
Reward is credited to a post-decision, stochastically-selected agent. Measured
SNR was 0.57 in v1 (signal 0.13 / noise 0.23) -- below the regime where
bootstrapped value iteration converges. The corrected env raises SNR to ~0.85,
but the policy route additionally avoids bootstrapping entirely for stage 2a.

F-EVL-01/02 — THE BASELINES v1 OMITTED
--------------------------------------
v1 reported encoder Top-1 = 0.341 and Top-3 = 0.715 as evidence of "genuine
predictive representations". Against the COMISET marginal those are:
    majority class (T1574)      = 0.372   -> the model was WORSE than a constant
    top-3 frequency prior       = 0.678   -> the model gained only +3.7pp
evaluate_encoder() therefore ALWAYS reports majority / frequency-prior / uniform
alongside the model, and macro-F1 (F-DAT-06) because the corpus is ~200:1
imbalanced and micro-accuracy is dominated by one class.
"""

import copy
import json
import os
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from d3fend_payoff import ACTIONS, N_ACTIONS
from encoders import ENCODERS, build_matched_suite
from env_v2 import (DeceptionEnvV2, N_AGENTS, build_profiles_from_camlds)
from policy import MultiAgentController
from vocab_v2 import NUM_TECHNIQUES, PAD_ID

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
os.makedirs(RESULTS, exist_ok=True)

# ── hyperparameters (all disclosed) ──────────────────────────────────────────
ENC_EPISODES, ENC_STEPS, ENC_LR, ENC_BATCH = 1200, 4000, 5e-4, 128
IL_EPISODES, IL_STEPS, IL_LR, IL_BATCH = 1200, 3000, 1e-3, 128
PPO_ITERS, PPO_ROLLOUT, PPO_EPOCHS, PPO_MB = 30, 40, 4, 256
PPO_LR, CRITIC_LR, PPO_CLIP, PPO_ENT, PPO_VAL = 1e-4, 1e-3, 0.2, 0.005, 0.5
EVAL_EPISODES = 150
STATE_MASK_TRAIN = 0.30       # ModDrop (Neverova et al. 2016); swept in eval


def set_seed(s):
    random.seed(s); np.random.seed(s); torch.manual_seed(s)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(s)


def assert_encoder_frozen(enc):
    """F-ARC-03/04 guard: called before every policy update."""
    assert not any(p.requires_grad for p in enc.parameters()), \
        "encoder must be frozen during policy training (F-ARC-03)"
    assert not enc.training, "encoder must be in eval() so dropout is OFF (F-ARC-04)"


# ── data collection ──────────────────────────────────────────────────────────

def collect_sequences(profiles, n_eps=ENC_EPISODES, seed=0, max_steps=40):
    """(right-padded prefix, true_length) -> next technique, plus the profile."""
    env = DeceptionEnvV2(profiles, max_steps=max_steps, seed=seed)
    X, L, Y, P = [], [], [], []
    for _ in range(n_eps):
        env.reset(); done = False
        while not done:
            ids, ln = env.padded_sequence()          # history BEFORE this step
            _, _, done, info = env.step([0] * N_AGENTS)
            t = info["technique_id"]
            if t < NUM_TECHNIQUES:
                X.append(ids); L.append(ln); Y.append(t); P.append(info["profile"])
    return (np.array(X), np.array(L), np.array(Y), P)


# ── Stage 1 — supervised encoder adaptation ─────────────────────────────────

def evaluate_encoder(enc, X, L, Y, idx, device=DEVICE):
    """Model vs the trivial baselines v1 omitted (F-EVL-01/02, F-DAT-06)."""
    enc.eval()
    xb = torch.as_tensor(X[idx], dtype=torch.long, device=device)
    lb = torch.as_tensor(L[idx], dtype=torch.long, device=device)
    yb = torch.as_tensor(Y[idx], dtype=torch.long, device=device)
    with torch.no_grad():
        _, lg = enc.pretrain_forward(xb, lb)
        p = torch.softmax(lg, -1)
        top1 = (lg.argmax(-1) == yb).float().mean().item()
        k = min(3, lg.shape[-1])
        top3 = (lg.topk(k, -1).indices == yb.unsqueeze(-1)).any(-1).float().mean().item()
        nll = F.cross_entropy(lg, yb).item()
        ppl = float(np.exp(nll))
        pred = lg.argmax(-1).cpu().numpy()

    # trivial baselines computed on the TRAIN marginal, scored on this split
    tr = np.setdiff1d(np.arange(len(Y)), idx)
    cnt = np.bincount(Y[tr], minlength=NUM_TECHNIQUES)
    order = np.argsort(-cnt)
    ytrue = Y[idx]
    maj = float((ytrue == order[0]).mean())
    freq3 = float(np.isin(ytrue, order[:3]).mean())

    # macro-F1 over classes present in this split
    f1s = []
    for c in np.unique(ytrue):
        tp = float(((pred == c) & (ytrue == c)).sum())
        fp = float(((pred == c) & (ytrue != c)).sum())
        fn = float(((pred != c) & (ytrue == c)).sum())
        f1s.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return {"top1": top1, "top3": top3, "perplexity": ppl, "nll": nll,
            "macro_f1": float(np.mean(f1s)), "n_classes": int(len(f1s)),
            "majority": maj, "freq_top3": freq3,
            "uniform_ppl": float(enc.vocab_size),
            "beats_majority": top1 > maj, "beats_freq3": top3 > freq3}


def train_encoder(enc, X, L, Y, steps=ENC_STEPS, lr=ENC_LR, batch=ENC_BATCH,
                  device=DEVICE, seed=0, verbose=True, class_weighted=True):
    """Next-technique CE. Class-weighted because the corpus is ~200:1 imbalanced
    (F-DAT-06): unweighted CE would let the model collapse onto the majority
    class -- which is exactly how v1 ended up BELOW a majority-class predictor."""
    set_seed(seed)
    n = len(Y)
    perm = np.random.permutation(n)
    cut = int(0.8 * n)
    tr, va = perm[:cut], perm[cut:]

    w = None
    if class_weighted:
        # NOTE: the weight vector must span the FULL logit dimension
        # (VOCAB_SIZE, incl. PAD/UNK), not just the technique block --
        # torch requires weights for all classes or none. PAD/UNK get weight 0
        # so they can never be predicted as a next technique.
        cnt = np.bincount(Y[tr], minlength=enc.vocab_size).astype(np.float64)
        inv = np.zeros(enc.vocab_size, dtype=np.float64)
        nz = cnt > 0
        inv[nz] = 1.0 / cnt[nz]
        if nz.any():
            inv[nz] = inv[nz] / inv[nz].mean()
        inv[NUM_TECHNIQUES:] = 0.0
        w = torch.as_tensor(inv, dtype=torch.float32, device=device)

    before = evaluate_encoder(enc, X, L, Y, va, device)
    opt = torch.optim.Adam(enc.parameters(), lr=lr)
    Xt = torch.as_tensor(X, dtype=torch.long, device=device)
    Lt = torch.as_tensor(L, dtype=torch.long, device=device)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=device)
    enc.train()
    for st in range(steps):
        b = tr[np.random.randint(0, len(tr), batch)]
        _, lg = enc.pretrain_forward(Xt[b], Lt[b])
        loss = F.cross_entropy(lg, Yt[b], weight=w)
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(enc.parameters(), 1.0)
        opt.step()
        if verbose and (st + 1) % max(1, steps // 3) == 0:
            m = evaluate_encoder(enc, X, L, Y, va, device); enc.train()
            print(f"      step {st+1:5d}/{steps} loss={loss.item():.4f} "
                  f"top1={m['top1']:.3f} macroF1={m['macro_f1']:.3f}")
    after = evaluate_encoder(enc, X, L, Y, va, device)
    enc.freeze()                      # F-ARC-03/04
    assert_encoder_frozen(enc)
    return {"before": before, "after": after, "n_train": len(tr), "n_val": len(va)}


# ── Stage 2a — policy imitation over the frozen encoder ─────────────────────

def astar_for_profile(name):
    """The consolidated intent class IS named for its D3FEND-optimal action."""
    return ACTIONS.index(name)


def collect_imitation(enc, profiles, n_eps=IL_EPISODES, seed=0, device=DEVICE,
                      use_h=True, max_steps=40):
    assert_encoder_frozen(enc)
    env = DeceptionEnvV2(profiles, max_steps=max_steps, seed=seed)
    X = [[] for _ in range(N_AGENTS)]; Y = []
    zeros = np.zeros(env.h_dim, np.float32)
    for _ in range(n_eps):
        obs = env.reset(); done = False
        tgt = astar_for_profile(env._profile)
        while not done:
            ids, ln = env.padded_sequence()
            h = enc.get_h_numpy(ids, device, lengths=[ln]) if use_h else zeros
            full = [o.copy() for o in obs]
            for o in full:
                o[-env.h_dim:] = h
            for i in range(N_AGENTS):
                X[i].append(full[i])
            Y.append(tgt)
            obs, _, done, _ = env.step([0] * N_AGENTS, h)
    return ([np.array(x, np.float32) for x in X], np.array(Y))


def eval_policy(enc, ctl, profiles, n_eps=EVAL_EPISODES, seed=12345,
                device=DEVICE, use_h=True, max_steps=40):
    """In-env alignment + DSR of the greedy policy — the guard metric."""
    set_seed(seed)
    if use_h:
        assert_encoder_frozen(enc)
    ctl.eval(); ctl.set_masking(0.0)
    env = DeceptionEnvV2(profiles, max_steps=max_steps, seed=seed)
    zeros = np.zeros(env.h_dim, np.float32)
    al, dsr = [], []
    for _ in range(n_eps):
        obs = env.reset(); done = False; ep = []
        while not done:
            ids, ln = env.padded_sequence()
            h = enc.get_h_numpy(ids, device, lengths=[ln]) if use_h else zeros
            full = [o.copy() for o in obs]
            for o in full:
                o[-env.h_dim:] = h
            a = ctl.act_policy(full, greedy=True)
            obs, _, done, info = env.step(a, h)
            if info["responsible_agent"] is not None:
                ep.append(info["alignment"])
        if ep:
            al.append(float(np.mean(ep)))
        dsr.append(1.0 if env.captured else 0.0)
    return {"alignment": float(np.mean(al)) if al else 0.0,
            "dsr": float(np.mean(dsr))}


def train_policy_imitation(enc, ctl, profiles, steps=IL_STEPS, lr=IL_LR,
                           batch=IL_BATCH, device=DEVICE, seed=0, use_h=True,
                           verbose=True):
    """CE on a*(profile) over the FROZEN encoder. State masking stays ON so the
    policy learns to act from h even when telemetry is fogged."""
    if use_h:
        assert_encoder_frozen(enc)
    X, Y = collect_imitation(enc, profiles, seed=seed, device=device, use_h=use_h)
    n = len(Y); perm = np.random.permutation(n); cut = int(0.85 * n)
    tr, va = perm[:cut], perm[cut:]
    Xt = [torch.as_tensor(x, device=device) for x in X]
    Yt = torch.as_tensor(Y, dtype=torch.long, device=device)
    opt = torch.optim.Adam(ctl.actor_parameters(), lr=lr)
    ctl.train(); ctl.set_masking(STATE_MASK_TRAIN)
    for st in range(steps):
        b = torch.as_tensor(tr[np.random.randint(0, len(tr), batch)], device=device)
        loss = sum(F.cross_entropy(ctl.agents[i].policy_logits(Xt[i][b]), Yt[b])
                   for i in range(N_AGENTS)) / N_AGENTS
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(ctl.actor_parameters(), 1.0)
        opt.step()
        if verbose and (st + 1) % max(1, steps // 3) == 0:
            ctl.eval()
            with torch.no_grad():
                acc = np.mean([(ctl.agents[i].policy_logits(Xt[i][va]).argmax(-1)
                                == Yt[va]).float().mean().item()
                               for i in range(N_AGENTS)])
            ctl.train(); ctl.set_masking(STATE_MASK_TRAIN)
            print(f"      step {st+1:5d}/{steps} CE={loss.item():.4f} a*-acc={acc:.3f}")
    return eval_policy(enc, ctl, profiles, device=device, use_h=use_h)


# ── Stage 2b — guarded PPO with a value baseline ────────────────────────────

def train_policy_ppo(enc, ctl, profiles, baseline, iters=PPO_ITERS, device=DEVICE,
                     seed=0, use_h=True, verbose=True):
    """On-policy PPO. Only the responsible agent is scored per step, so each
    scored step is a single-agent bandit sample and A = R - V(f) is the correct
    baseline (COMA's counterfactual degenerates to this; see policy.py).

    A best-by-eval GUARD makes fine-tuning unable to regress below imitation."""
    if use_h:
        assert_encoder_frozen(enc)
    aopt = torch.optim.Adam(ctl.actor_parameters(), lr=PPO_LR)
    copt = torch.optim.Adam(ctl.critic_parameters(), lr=CRITIC_LR)
    best = baseline["alignment"]
    best_sd = [copy.deepcopy(a.state_dict()) for a in ctl.agents]
    zeros = np.zeros(64, np.float32)
    hist = []

    for it in range(iters):
        ctl.eval(); ctl.set_masking(0.0)
        buf = {i: {"o": [], "a": [], "r": [], "lp": []} for i in range(N_AGENTS)}
        env = DeceptionEnvV2(profiles, max_steps=40, seed=seed * 1000 + it)
        with torch.no_grad():
            for _ in range(PPO_ROLLOUT):
                obs = env.reset(); done = False
                while not done:
                    ids, ln = env.padded_sequence()
                    h = enc.get_h_numpy(ids, device, lengths=[ln]) if use_h else zeros
                    full = [o.copy() for o in obs]
                    for o in full:
                        o[-env.h_dim:] = h
                    acts, lps = [], []
                    for i in range(N_AGENTS):
                        t = torch.as_tensor(full[i], device=device).unsqueeze(0)
                        lg = ctl.agents[i].policy_logits(t).squeeze(0)
                        pr = torch.softmax(lg, -1)
                        ai = int(torch.multinomial(pr, 1))
                        acts.append(ai); lps.append(float(F.log_softmax(lg, -1)[ai]))
                    obs, rw, done, info = env.step(acts, h)
                    r = info["responsible_agent"]
                    if r is not None:
                        buf[r]["o"].append(full[r]); buf[r]["a"].append(acts[r])
                        buf[r]["r"].append(float(rw[0])); buf[r]["lp"].append(lps[r])

        ctl.train(); ctl.set_masking(0.0)
        for i in range(N_AGENTS):
            if len(buf[i]["a"]) < 16:
                continue
            O = torch.as_tensor(np.array(buf[i]["o"], np.float32), device=device)
            A = torch.as_tensor(buf[i]["a"], dtype=torch.long, device=device)
            R = torch.as_tensor(buf[i]["r"], dtype=torch.float32, device=device)
            LP = torch.as_tensor(buf[i]["lp"], dtype=torch.float32, device=device)
            net = ctl.agents[i]
            for _ in range(PPO_EPOCHS):
                pm = torch.randperm(len(A), device=device)
                for s in range(0, len(A), PPO_MB):
                    mb = pm[s:s + PPO_MB]
                    lg = net.policy_logits(O[mb]); v = net.value(O[mb])
                    logp = F.log_softmax(lg, -1).gather(1, A[mb, None]).squeeze(1)
                    ent = -(F.softmax(lg, -1) * F.log_softmax(lg, -1)).sum(-1).mean()
                    adv = (R[mb] - v).detach()
                    adv = (adv - adv.mean()) / (adv.std() + 1e-6)
                    ratio = torch.exp(logp - LP[mb])
                    l_pol = -torch.min(ratio * adv,
                                       torch.clamp(ratio, 1 - PPO_CLIP, 1 + PPO_CLIP) * adv).mean()
                    loss = l_pol + PPO_VAL * F.mse_loss(v, R[mb]) - PPO_ENT * ent
                    aopt.zero_grad(); copt.zero_grad(); loss.backward()
                    nn.utils.clip_grad_norm_(ctl.actor_parameters(), 1.0)
                    nn.utils.clip_grad_norm_(ctl.critic_parameters(), 1.0)
                    aopt.step(); copt.step()

        if (it + 1) % 5 == 0 or it == iters - 1:
            m = eval_policy(enc, ctl, profiles, device=device, use_h=use_h)
            hist.append(m)
            flag = ""
            if m["alignment"] > best + 1e-4:
                best = m["alignment"]
                best_sd = [copy.deepcopy(a.state_dict()) for a in ctl.agents]
                flag = "  <- kept"
            if verbose:
                print(f"      ppo {it+1:3d}/{iters} align={m['alignment']:.4f} "
                      f"dsr={m['dsr']:.3f} best={best:.4f}{flag}")

    for a, sd in zip(ctl.agents, best_sd):
        a.load_state_dict(sd)
    return {"best_alignment": best, "history": hist,
            "imitation_alignment": baseline["alignment"]}


# ── full pipeline for one (encoder, arm) cell ───────────────────────────────

def train_arm(encoder_name, profiles, seed=0, use_h=True, device=DEVICE,
              enc_eps=ENC_EPISODES, enc_steps=ENC_STEPS, il_steps=IL_STEPS,
              ppo_iters=PPO_ITERS, verbose=True):
    set_seed(seed)
    suite, tgt, cfg = build_matched_suite()
    enc = suite[encoder_name].to(device)
    tag = f"{encoder_name}{'' if use_h else '_NoTrans'}_s{seed}"
    if verbose:
        print(f"\n  === {tag} ===")

    X, L, Y, P = collect_sequences(profiles, n_eps=enc_eps, seed=seed)
    if verbose:
        print(f"    stage 1: encoder adaptation on {len(Y):,} transitions")
    encm = train_encoder(enc, X, L, Y, steps=enc_steps, device=device,
                         seed=seed, verbose=verbose)

    env0 = DeceptionEnvV2(profiles)
    ctl = MultiAgentController(N_AGENTS, env0.local_dim, N_ACTIONS, env0.h_dim,
                               sighted_idx=env0.ATTACKER_PRESENT_IDX,
                               state_masking_prob=STATE_MASK_TRAIN, device=device)
    if verbose:
        print(f"    stage 2a: policy imitation")
    il = train_policy_imitation(enc, ctl, profiles, steps=il_steps, device=device,
                                seed=seed, use_h=use_h, verbose=verbose)
    if verbose:
        print(f"      imitation: align={il['alignment']:.4f} dsr={il['dsr']:.3f}")
        print(f"    stage 2b: guarded PPO")
    ppo = train_policy_ppo(enc, ctl, profiles, il, iters=ppo_iters, device=device,
                           seed=seed, use_h=use_h, verbose=verbose)

    path = os.path.join(RESULTS, f"{tag}.pt")
    torch.save({"encoder": enc.state_dict(),
                "agents": [a.state_dict() for a in ctl.agents],
                "encoder_name": encoder_name, "use_h": use_h, "seed": seed,
                "encoder_metrics": encm, "imitation": il, "ppo": ppo}, path)
    return {"tag": tag, "path": path, "encoder": encm, "imitation": il, "ppo": ppo}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("=" * 78)
    print("  TEMARL v2 — TRAINING PIPELINE (smoke test)")
    print("=" * 78)
    print(f"  device={DEVICE}")
    profiles, _ = build_profiles_from_camlds()

    r = train_arm("Transformer", profiles, seed=0, use_h=True,
                  enc_eps=250, enc_steps=600, il_steps=500, ppo_iters=5)

    b, a = r["encoder"]["before"], r["encoder"]["after"]
    print(f"\n  [F-EVL-01/02] ENCODER vs TRIVIAL BASELINES "
          f"(the comparison v1 omitted)")
    print(f"    {'metric':<22} {'before':>9} {'after':>9} {'baseline':>10}  verdict")
    print(f"    {'Top-1':<22} {b['top1']:>9.3f} {a['top1']:>9.3f} "
          f"{a['majority']:>10.3f}  {'BEATS majority' if a['beats_majority'] else 'LOSES to majority'}")
    print(f"    {'Top-3':<22} {b['top3']:>9.3f} {a['top3']:>9.3f} "
          f"{a['freq_top3']:>10.3f}  {'BEATS freq-prior' if a['beats_freq3'] else 'LOSES to freq-prior'}")
    print(f"    {'macro-F1':<22} {b['macro_f1']:>9.3f} {a['macro_f1']:>9.3f} "
          f"{'':>10}  ({a['n_classes']} classes)")
    print(f"    {'perplexity':<22} {b['perplexity']:>9.2f} {a['perplexity']:>9.2f} "
          f"{a['uniform_ppl']:>10.1f}  (uniform; >uniform = worse than random)")
    print(f"\n  policy: imitation align={r['imitation']['alignment']:.4f} "
          f"-> PPO best={r['ppo']['best_alignment']:.4f} "
          f"(guard: cannot regress)")
    print(f"  checkpoint -> {os.path.basename(r['path'])}")
    print("=" * 78)
