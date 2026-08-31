# -*- coding: utf-8 -*-
"""
TEMARL v3 — Entity training & four-regime evaluation
=====================================================
Trains the full 2x3 factorial (network encoder x history encoder) on a
DISTRIBUTION of topologies and evaluates every arm on four regimes:

    A  the frozen canonical 5-zone control (identical to env_v2)
    B  new topologies at TRAINED sizes
    C  unseen structure  (different firewall density)
    D  unseen sizes      (9 / 11 / 13 zones, never trained on)

Everything is fixed in advance by `prereg_v3.py`. All arms see the IDENTICAL
topology sets and the IDENTICAL paired seeds, so per-seed differences are
attributable to the architecture and a paired test is the right instrument.

HISTORY ENCODERS ARE PRETRAINED AND FROZEN, exactly as in v2: representation
learning must not chase the value function (two-timescale argument, Borkar 1997).
For each model seed the three history encoders are pretrained once on simulated
rollouts and shared by both network encoders, so the two network arms are handed
an identical h.

Checkpoints go to `runs_v3/`, results to `results_v3/`. Nothing in `runs/` or
`results_v2/` is read or written. No pre-vocabulary-expansion checkpoint is
reused: the vocabulary is now 84 techniques wide and old heads are 80.

Paths are resolved relative to this file; sizes and seeds come from the
pre-registration or the command line.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import prereg_v3 as PR
from encoders import build_matched_suite
from entity_encoders import match_entity_capacity
from env_entity import EntityDeceptionEnv
from policy_entity import EntityAgentNet, stack_obs
from topology import Topology, canonical_topology, generate_topology
from vocab_v2 import NUM_TECHNIQUES

from env_v2 import build_profiles_from_camlds

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs_v3")
RESULTS = os.path.join(HERE, "results_v3")
DEVICE = "cpu"

# Built ONCE. EntityDeceptionEnv(profiles=None) rebuilds the CAM-LDS profiles
# from JSON on construction; with one env per episode that dominated runtime.
_PROFILES = None


def profiles():
    global _PROFILES
    if _PROFILES is None:
        _PROFILES, _ = build_profiles_from_camlds()
    return _PROFILES


# ── topology sets ────────────────────────────────────────────────────────────

def build_topologies(spec_key: str) -> List[Topology]:
    spec = PR.topology_spec()[spec_key]
    if spec.get("canonical"):
        return [canonical_topology(n_agents=PR.N_AGENTS)]
    out = []
    for i, s in enumerate(spec["seeds"]):
        nz = spec["sizes"][i % len(spec["sizes"])]
        out.append(generate_topology(seed=s, n_zones=nz, n_agents=PR.N_AGENTS,
                                     p_firewall_block=spec["p_firewall_block"]))
    return out


# ── history encoder: pretrain then FREEZE ───────────────────────────────────

def pretrain_history(name: str, seed: int, topos: Sequence[Topology],
                     n_seq: int = 400, steps: int = 800, verbose: bool = False):
    """Next-technique pretraining on simulated rollouts, then freeze.

    The encoder never receives gradient from the policy loss afterwards, which is
    what keeps the representation stationary while the policy learns.
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    X, L, Y = [], [], []
    for i in range(n_seq):
        t = topos[i % len(topos)]
        env = EntityDeceptionEnv(topology=t, profiles=profiles(),
                                 max_steps=PR.MAX_STEPS,
                                 seed=int(rng.integers(1 << 30)))
        env.reset()
        done = False
        while not done:
            acts = [(int(rng.integers(0, 6)), int(env.legal_targets(a)[0]))
                    for a in range(env.n_agents)]
            ids, ln = env.padded_sequence()
            prev_tau = env.tau
            _, _, done, info = env.step(acts)
            X.append(ids); L.append(ln); Y.append(info["technique_id"])
    X = np.asarray(X); L = np.asarray(L); Y = np.asarray(Y)

    suite, _, _ = build_matched_suite()
    enc = suite[name].to(DEVICE)
    opt = torch.optim.AdamW(enc.parameters(), lr=5e-4, weight_decay=1e-4)
    Xt = torch.as_tensor(X, dtype=torch.long, device=DEVICE)
    Lt = torch.as_tensor(L, dtype=torch.long, device=DEVICE)
    Yt = torch.as_tensor(Y, dtype=torch.long, device=DEVICE)
    enc.train()
    for st in range(steps):
        b = torch.randint(0, len(Y), (128,), device=DEVICE)
        _, lg = enc.pretrain_forward(Xt[b], Lt[b])
        loss = F.cross_entropy(lg, Yt[b])
        opt.zero_grad(); loss.backward()
        nn.utils.clip_grad_norm_(enc.parameters(), 1.0)
        opt.step()
    enc.freeze()
    if verbose:
        with torch.no_grad():
            _, lg = enc.pretrain_forward(Xt[:2048], Lt[:2048])
            acc = (lg.argmax(-1) == Yt[:2048]).float().mean().item()
        print(f"      history[{name}] pretrain top1={acc:.3f} (frozen)")
    return enc


def assert_encoder_frozen(enc):
    bad = [n for n, p in enc.named_parameters() if p.requires_grad]
    if bad:
        raise RuntimeError(f"history encoder is NOT frozen: {bad[:3]}")


# ── rollout ──────────────────────────────────────────────────────────────────

def _h_for(enc, env):
    ids, ln = env.padded_sequence()
    with torch.no_grad():
        h, ent = enc.get_h_and_entropy_numpy(
            np.asarray(ids)[None, :], DEVICE, np.asarray([ln]))
    return h[0], float(ent[0])


def rollout(net: EntityAgentNet, hist_enc, env: EntityDeceptionEnv,
            rng: np.random.Generator, greedy: bool = False, collect: bool = True):
    """One episode. All agents share `net`, so their observations are stacked
    into a single batched forward pass."""
    h, ent = _h_for(hist_enc, env)
    obs = env.observations(h)
    traj = {"obs": [], "types": [], "targets": [], "logp": [], "rew": [],
            "val": [], "ent": []}
    ep_align, n_steps, ep_return = 0.0, 0, 0.0
    done = False
    while not done:
        batch = stack_obs(obs, DEVICE)
        if collect:
            tl, gl, _ = net(batch, ent)
            v = net.value(batch, ent)
        else:
            with torch.no_grad():
                tl, gl, _ = net(batch, ent)
                v = net.value(batch, ent)
        pt, pg = F.softmax(tl, -1), F.softmax(gl, -1)
        if greedy:
            ti = tl.argmax(-1); gi = gl.argmax(-1)
        else:
            ti = torch.multinomial(pt, 1).squeeze(-1)
            gi = torch.multinomial(pg, 1).squeeze(-1)
        logp = (torch.log(pt.gather(1, ti[:, None]).squeeze(1) + 1e-10)
                + torch.log(pg.gather(1, gi[:, None]).squeeze(1) + 1e-10))
        acts = [(int(ti[a]), int(gi[a])) for a in range(env.n_agents)]

        obs_next, rw, done, info = env.step(acts)
        ep_align += info["alignment"]; n_steps += 1
        ep_return += float(rw[0])       # accumulated ALWAYS, not only when
                                        # collecting: evaluation runs with
                                        # collect=False and must still report it
        if collect:
            traj["obs"].append(batch); traj["types"].append(ti)
            traj["targets"].append(gi); traj["logp"].append(logp)
            traj["val"].append(v); traj["ent"].append(ent)
            traj["rew"].append(float(rw[0]))
        h, ent = _h_for(hist_enc, env)
        obs = env.observations(h)
    stats = {"dsr": float(env.captured), "alignment": ep_align / max(n_steps, 1),
             "episode_return": ep_return,
             "engagement_length": n_steps,
             "capture_rate": float(env.captured),
             "reached_objective": float(env.reached_objective)}
    return traj, stats


# ── PPO ──────────────────────────────────────────────────────────────────────

def train_arm(net_name: str, hist_name: str, seed: int, train_topos, hist_enc,
              episodes: int = None, gamma: float = 0.99, clip: float = 0.2,
              lr: float = 3e-4, epochs: int = 4, ent_coef: float = 0.01,
              verbose: bool = False) -> EntityAgentNet:
    episodes = episodes or PR.TRAIN_EPISODES
    torch.manual_seed(seed); np.random.seed(seed)
    suite, _ = match_entity_capacity()
    net = EntityAgentNet(suite[net_name]).to(DEVICE)
    opt = torch.optim.AdamW(net.parameters(), lr=lr, weight_decay=1e-5)
    rng = np.random.default_rng(seed)
    assert_encoder_frozen(hist_enc)

    for ep in range(episodes):
        topo = train_topos[int(rng.integers(len(train_topos)))]
        env = EntityDeceptionEnv(topology=topo, profiles=profiles(),
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 seed=int(rng.integers(1 << 30)))
        env.reset()
        traj, _ = rollout(net, hist_enc, env, rng, greedy=False, collect=True)
        T = len(traj["rew"])
        if T == 0:
            continue
        ret, R = [], 0.0
        for r in reversed(traj["rew"]):
            R = r + gamma * R
            ret.append(R)
        ret.reverse()
        rets = torch.tensor(ret, dtype=torch.float32, device=DEVICE)
        vals = torch.stack([v.mean() for v in traj["val"]])
        adv = (rets - vals.detach())
        if adv.numel() > 1:
            adv = (adv - adv.mean()) / (adv.std() + 1e-8)
        old_logp = torch.stack([lp.detach().mean() for lp in traj["logp"]])

        for _ in range(epochs):
            new_lp, new_v, ents = [], [], []
            for t in range(T):
                b = traj["obs"][t]
                tl, gl, _ = net(b, traj["ent"][t])
                pt, pg = F.softmax(tl, -1), F.softmax(gl, -1)
                lp = (torch.log(pt.gather(1, traj["types"][t][:, None]).squeeze(1) + 1e-10)
                      + torch.log(pg.gather(1, traj["targets"][t][:, None]).squeeze(1) + 1e-10))
                new_lp.append(lp.mean())
                new_v.append(net.value(b, traj["ent"][t]).mean())
                e = -(pt * torch.log(pt + 1e-10)).sum(-1).mean()
                ents.append(e)
            new_lp = torch.stack(new_lp); new_v = torch.stack(new_v)
            ratio = torch.exp(new_lp - old_logp)
            l_pi = -torch.min(ratio * adv,
                              torch.clamp(ratio, 1 - clip, 1 + clip) * adv).mean()
            l_v = F.mse_loss(new_v, rets)
            loss = l_pi + 0.5 * l_v - ent_coef * torch.stack(ents).mean()
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(net.parameters(), 0.5)
            opt.step()
        if verbose and (ep + 1) % max(1, episodes // 4) == 0:
            print(f"        ep {ep+1}/{episodes}")
    return net


# ── evaluation ───────────────────────────────────────────────────────────────

def evaluate(net, hist_enc, topos, n_episodes: int, seed: int) -> Dict[str, float]:
    net.eval()
    rng = np.random.default_rng(1_000_000 + seed)
    acc = {k: [] for k in ("dsr", "alignment", "episode_return",
                           "engagement_length", "capture_rate")}
    for i in range(n_episodes):
        topo = topos[i % len(topos)]
        env = EntityDeceptionEnv(topology=topo, profiles=profiles(),
                                 max_steps=PR.MAX_STEPS,
                                 max_entities=PR.MAX_ENTITIES,
                                 seed=int(rng.integers(1 << 30)))
        env.reset()
        _, st = rollout(net, hist_enc, env, rng, greedy=True, collect=False)
        for k in acc:
            acc[k].append(st[k])
    net.train()
    return {k: float(np.mean(v)) for k, v in acc.items()}


# ── driver ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="TEMARL v3 entity training")
    ap.add_argument("--seeds", type=int, nargs="*", default=list(PR.SEEDS))
    ap.add_argument("--episodes", type=int, default=PR.TRAIN_EPISODES)
    ap.add_argument("--eval-episodes", type=int, default=PR.EVAL_EPISODES)
    ap.add_argument("--out", default=os.path.join(RESULTS, "entity_results.json"))
    ap.add_argument("--save-checkpoints", action="store_true")
    ap.add_argument("--quick", action="store_true",
                    help="tiny budget for a smoke test")
    args = ap.parse_args()
    if args.quick:
        args.seeds, args.episodes, args.eval_episodes = [0], 40, 20

    os.makedirs(RUNS, exist_ok=True); os.makedirs(RESULTS, exist_ok=True)
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=" * 94)
    print("  TEMARL v3 — ENTITY TRAINING (2 network x 3 history encoders)")
    print("=" * 94)
    sets = {k: build_topologies(k) for k in ("train", "A", "B", "C", "D")}
    for k, v in sets.items():
        sizes = sorted({t.n_zones for t in v})
        print(f"  regime {k:<6} {len(v):>3} topologies, zone sizes {sizes}")
    print(f"  seeds {args.seeds}  train_eps={args.episodes}  "
          f"eval_eps={args.eval_episodes}\n")

    rows = []
    t0 = time.time()
    for seed in args.seeds:
        print(f"  ── model seed {seed} ──")
        hist = {}
        for hname in PR.HISTORY_ENCODERS:
            hist[hname] = pretrain_history(hname, seed, sets["train"],
                                           verbose=True)
        for net_name in PR.NETWORK_ENCODERS:
            for hist_name in PR.HISTORY_ENCODERS:
                ts = time.time()
                net = train_arm(net_name, hist_name, seed, sets["train"],
                                hist[hist_name], episodes=args.episodes)
                train_s = time.time() - ts
                row = {"seed": seed, "network_encoder": net_name,
                       "history_encoder": hist_name,
                       "n_params": net.n_params(), "train_seconds": train_s}
                for rk in ("A", "B", "C", "D"):
                    m = evaluate(net, hist[hist_name], sets[rk],
                                 args.eval_episodes, seed)
                    for k, v in m.items():
                        row[f"{rk}_{k}"] = v
                rows.append(row)
                print(f"    {net_name:<18}+{hist_name:<12} "
                      f"A={row['A_dsr']:.3f} B={row['B_dsr']:.3f} "
                      f"C={row['C_dsr']:.3f} D={row['D_dsr']:.3f}  "
                      f"({train_s:.0f}s, {net.n_params():,}p)")
                if args.save_checkpoints:
                    torch.save({"net": net.state_dict(), "arm": [net_name, hist_name],
                                "seed": seed},
                               os.path.join(RUNS, f"{net_name}_{hist_name}_s{seed}.pt"))
        # free the seed's history encoders before the next seed
        del hist

    payload = {"prereg": {"hypotheses": PR.HYPOTHESES, "arms": PR.ARMS,
                          "primary": PR.PRIMARY_METRIC,
                          "contrast_family": PR.CONTRAST_FAMILY,
                          "declaration": PR.DECLARATION},
               "config": {"seeds": args.seeds, "train_episodes": args.episodes,
                          "eval_episodes": args.eval_episodes},
               "topologies": {k: [{"name": t.name, "n_zones": t.n_zones,
                                   "n_hosts": t.n_hosts,
                                   "hash": t.content_hash()} for t in v]
                              for k, v in sets.items()},
               "rows": rows,
               "total_seconds": time.time() - t0}
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, default=float)
    print(f"\n  wrote -> {os.path.relpath(args.out, HERE)}  "
          f"({time.time() - t0:.0f}s total)")
    print("=" * 94)


if __name__ == "__main__":
    main()
