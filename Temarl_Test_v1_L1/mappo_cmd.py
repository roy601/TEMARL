# -*- coding: utf-8 -*-
"""
Temarl_Test_v1_L1 -- MAPPO / IPPO over the command-level replay environment
=============================================================================
Centralised training, decentralised execution (Yu et al., NeurIPS 2022 D&B).

  ACTOR   decentralised, parameter-shared. Agent i sees ONLY its local
          observation (its own zone, its own decoy, two infrastructure
          signals, its id) concatenated with the shared PAST-ONLY history
          embedding h. Followed by a categorical head over six decoy types.
  CRITIC  MAPPO: centralised, V(global state, h, agent id). Training only.
          IPPO : local, V(local obs, h) -- de Witt et al. (2020).
  h       produced by the FROZEN command-level encoder. Frozen means frozen:
          `requires_grad_(False)` and `eval()`, asserted in tests, so RL can
          never backpropagate into the representation being compared.

Observability
-------------
`history_table` precomputes h for every PREFIX of a replayed run, so at step t
the policy receives the embedding of commands [0, t) only. Future commands
cannot reach the policy through h. The episode's command list is fixed in
advance (it is a replay), but the policy never sees beyond the current step.

Hyperparameters are identical for every arm and are not tuned per arm.
"""

from __future__ import annotations

import copy
import time
from collections import deque
from typing import Dict, List, Optional, Sequence

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import _frozen
from d3fend_payoff import N_ACTIONS
from encoders_cmd import H_DIM
from env_cmd import (GLOBAL_DIM, LOCAL_DIM, N_AGENTS, CommandEngagementEnv,
                     EnvConfig, EpisodeSpec, ReplayPool)
from vocab_v2 import NUM_TECHNIQUES as NT

HP = {
    "lr": 5e-4, "ppo_epochs": 10, "n_minibatch": 1, "clip": 0.2,
    "gamma": 0.99, "gae_lambda": 0.95, "entropy_coef": 0.01,
    "max_grad_norm": 10.0, "huber_delta": 10.0,
    "n_envs": 64, "rollout_len": 64,
    "critic_hidden": 128, "head_hidden": 64,
    "n_evals": 10,
}
EYE = np.eye(N_AGENTS, dtype=np.float32)


def _ortho(m, gain):
    nn.init.orthogonal_(m.weight, gain)
    nn.init.zeros_(m.bias)
    return m


class Actor(nn.Module):
    """Local observation + shared history -> decoy type."""

    def __init__(self):
        super().__init__()
        inp = LOCAL_DIM + H_DIM
        self.net = nn.Sequential(
            nn.LayerNorm(inp),
            _ortho(nn.Linear(inp, HP["head_hidden"]), np.sqrt(2)), nn.ReLU(),
            _ortho(nn.Linear(HP["head_hidden"], HP["head_hidden"]), np.sqrt(2)), nn.ReLU(),
            _ortho(nn.Linear(HP["head_hidden"], N_ACTIONS), 0.01))

    def forward(self, local, h):
        return self.net(torch.cat([local, h], -1))


class Critic(nn.Module):
    def __init__(self, in_dim: int):
        super().__init__()
        H = HP["critic_hidden"]
        self.net = nn.Sequential(
            nn.LayerNorm(in_dim),
            _ortho(nn.Linear(in_dim, H), np.sqrt(2)), nn.ReLU(),
            _ortho(nn.Linear(H, H), np.sqrt(2)), nn.ReLU(),
            _ortho(nn.Linear(H, 1), 1.0))

    def forward(self, x):
        return self.net(x).squeeze(-1)


class ValueNorm:
    """MAPPO's running value-target normalisation (float64 on CPU)."""

    def __init__(self, beta=0.99999, eps=1e-5):
        self.beta, self.eps = beta, eps
        self.m = self.m2 = self.debias = 0.0

    def update(self, x: torch.Tensor):
        x = x.detach().cpu().double()
        self.m = self.beta * self.m + (1 - self.beta) * float(x.mean())
        self.m2 = self.beta * self.m2 + (1 - self.beta) * float((x ** 2).mean())
        self.debias = self.beta * self.debias + (1 - self.beta)

    def stats(self):
        mean = self.m / max(self.debias, self.eps)
        var = max(self.m2 / max(self.debias, self.eps) - mean ** 2, 1e-2)
        return mean, var ** 0.5

    def normalize(self, x):
        mu, sd = self.stats()
        return (x - mu) / sd

    def denormalize(self, x):
        mu, sd = self.stats()
        return x * sd + mu


def critic_dim(centralised: bool) -> int:
    return (GLOBAL_DIM + H_DIM + N_AGENTS) if centralised else (LOCAL_DIM + H_DIM)


def critic_input(centralised: bool, local, h, glob):
    n = local.shape[0]
    hr = np.repeat(h[:, None, :], N_AGENTS, 1)
    if centralised:
        g = np.repeat(glob[:, None, :], N_AGENTS, 1)
        ids = np.broadcast_to(EYE, (n, N_AGENTS, N_AGENTS))
        x = np.concatenate([g, hr, ids], -1)
    else:
        x = np.concatenate([local, hr], -1)
    return x.reshape(n * N_AGENTS, -1)


# ── frozen history embedding ────────────────────────────────────────────────

class HistoryBank:
    """Precomputes h for every prefix of a replayed run.

    Row t of the returned table is the embedding of commands [0, t). Row 0 is
    the empty history: a zero vector, the same convention the predictor uses
    for "nothing seen yet". The encoder is frozen and in eval mode.
    """

    def __init__(self, model, window: int, device="cpu", h_zero: bool = False):
        self.window, self.device, self.h_zero = window, device, h_zero
        self.model = model
        self.width = H_DIM
        self._cache: Dict[str, np.ndarray] = {}
        if model is not None:
            model.to(device).eval()
            for p in model.parameters():
                p.requires_grad_(False)

    @torch.no_grad()
    def table(self, spec: EpisodeSpec) -> np.ndarray:
        key = spec.run_id
        cached = self._cache.get(key)
        if cached is not None and len(cached) >= spec.horizon + 1:
            return cached
        n = spec.horizon + 1
        out = np.zeros((n, H_DIM), np.float32)
        if self.model is not None and not self.h_zero:
            W = self.window
            X = np.zeros((n - 1, W, NT), np.float32)
            M = np.zeros((n - 1, W), np.float32)
            for t in range(1, n):
                hist = spec.commands[max(0, t - W):t]
                start = W - len(hist)
                for k, c in enumerate(hist):
                    X[t - 1, start + k, list(c)] = 1.0
                    M[t - 1, start + k] = 1.0
            x = torch.from_numpy(X).to(self.device)
            m = torch.from_numpy(M).to(self.device)
            out[1:] = self.model.history(x, m).float().cpu().numpy()
        self._cache[key] = out
        return out

    def tables(self, specs: Sequence[EpisodeSpec]) -> List[np.ndarray]:
        return [self.table(s) for s in specs]


# ── vectorised environment ──────────────────────────────────────────────────

class Episodes:
    def __init__(self, pool: ReplayPool, bank: HistoryBank, chunk: int = 256):
        self.pool, self.bank, self.chunk = pool, bank, chunk
        self.q = deque()

    def next(self):
        if not self.q:
            specs = [self.pool.next() for _ in range(self.chunk)]
            for sp, tb in zip(specs, self.bank.tables(specs)):
                self.q.append((sp, tb))
        return self.q.popleft()


class VecEnv:
    def __init__(self, n: int, cfg: EnvConfig, episodes: Episodes, max_steps: int):
        self.envs = [CommandEngagementEnv(cfg, max_steps) for _ in range(n)]
        self.episodes = episodes
        self.h = [None] * n
        self.local = np.zeros((n, N_AGENTS, LOCAL_DIM), np.float32)
        self.glob = np.zeros((n, GLOBAL_DIM), np.float32)
        self.hcur = np.zeros((n, H_DIM), np.float32)
        for i in range(n):
            self._reset(i)

    def _reset(self, i):
        sp, tb = self.episodes.next()
        self.envs[i].reset(sp)
        self.h[i] = tb
        self._obs(i)

    def _obs(self, i):
        e = self.envs[i]
        e.local_obs(out=self.local[i])
        e.global_state(out=self.glob[i])
        self.hcur[i] = self.h[i][e.t] if e.t < len(self.h[i]) else 0.0

    def step(self, actions: np.ndarray):
        n = len(self.envs)
        rew = np.zeros(n, np.float32)
        done = np.zeros(n, np.float32)
        finished = []
        for i, e in enumerate(self.envs):
            r, d, _ = e.step(actions[i])
            rew[i] = r
            if d:
                done[i] = 1.0
                finished.append(e.episode_stats())
                self._reset(i)
            else:
                self._obs(i)
        return rew, done, finished


# ── evaluation ──────────────────────────────────────────────────────────────

@torch.no_grad()
def evaluate_team(actor, cfg: EnvConfig, specs: Sequence[EpisodeSpec],
                  bank: HistoryBank, max_steps: int, device="cpu",
                  h_zero: bool = False, batch: int = 128) -> List[Dict]:
    actor.eval()
    out: List[Optional[Dict]] = [None] * len(specs)
    tables = bank.tables(specs)
    for s0 in range(0, len(specs), batch):
        idx = list(range(s0, min(len(specs), s0 + batch)))
        envs = [CommandEngagementEnv(cfg, max_steps).reset(specs[k]) for k in idx]
        rewards = np.zeros(len(idx), np.float64)
        local = np.zeros((len(idx), N_AGENTS, LOCAL_DIM), np.float32)
        while True:
            live = [j for j, e in enumerate(envs) if not e.done]
            if not live:
                break
            for j in live:
                envs[j].local_obs(out=local[j])
            L = torch.as_tensor(local[live], device=device)
            H = np.stack([np.zeros(H_DIM, np.float32) if h_zero
                          else tables[idx[j]][envs[j].t] for j in live])
            Ht = torch.as_tensor(H, device=device)
            acts = np.zeros((len(live), N_AGENTS), np.int64)
            for ag in range(N_AGENTS):
                acts[:, ag] = actor(L[:, ag], Ht).argmax(-1).cpu().numpy()
            for k, j in enumerate(live):
                r, _, _ = envs[j].step(acts[k])
                rewards[j] += r
        for j, k in enumerate(idx):
            out[k] = envs[j].episode_stats()
            out[k]["episode_reward"] = float(rewards[j])
    return [o for o in out if o is not None]


def mean_of(rows, key="dwell"):
    return float(np.mean([r[key] for r in rows])) if rows else 0.0


def compute_gae(rewards, done, values, last_value, gamma, lam):
    advantages = np.zeros_like(values)
    carry = np.zeros_like(last_value)
    for t in reversed(range(len(rewards))):
        nxt = last_value if t == len(rewards) - 1 else values[t + 1]
        live = (1.0 - done[t])[:, None]
        delta = rewards[t][:, None] + gamma * nxt * live - values[t]
        carry = delta + gamma * lam * live * carry
        advantages[t] = carry
    return advantages, advantages + values


def clipped_policy_loss(log_prob, old_log_prob, advantages, entropy,
                        clip, entropy_coef):
    ratio = torch.exp(log_prob - old_log_prob)
    surrogate = torch.minimum(ratio * advantages,
                              ratio.clamp(1 - clip, 1 + clip) * advantages)
    return -surrogate.mean() - entropy_coef * entropy.mean()


# ── training ────────────────────────────────────────────────────────────────

def train(encoder, cfg: EnvConfig, train_runs, validation_specs, test_specs,
          seed: int, env_steps: int, window: int, max_steps: int,
          centralised: bool = True, device: str = "cpu",
          verbose: bool = False) -> Dict:
    """Train one policy. `encoder=None` is the NoHistory control (h = 0)."""
    torch.manual_seed(seed)
    np.random.seed(seed % (2 ** 32))
    t0 = time.time()

    bank = HistoryBank(encoder, window, device, h_zero=(encoder is None))
    pool = ReplayPool(train_runs, seed=900_000 + seed)
    vec = VecEnv(HP["n_envs"], cfg, Episodes(pool, bank), max_steps)

    actor = Actor().to(device)
    critic = Critic(critic_dim(centralised)).to(device)
    opt_a = torch.optim.Adam(actor.parameters(), lr=HP["lr"], eps=1e-5)
    opt_c = torch.optim.Adam(critic.parameters(), lr=HP["lr"], eps=1e-5)
    vnorm = ValueNorm()

    T, E, A = HP["rollout_len"], HP["n_envs"], N_AGENTS
    n_updates = max(1, env_steps // (T * E))
    eval_at = {int(round(n_updates * k / HP["n_evals"]))
               for k in range(1, HP["n_evals"] + 1)}
    curve, recent = [], deque(maxlen=400)
    best = {"val": -float("inf"), "actor": None, "update": 0}
    cdim = critic_dim(centralised)

    for upd in range(1, n_updates + 1):
        buf_l = np.zeros((T, E, A, LOCAL_DIM), np.float32)
        buf_h = np.zeros((T, E, H_DIM), np.float32)
        buf_c = np.zeros((T, E * A, cdim), np.float32)
        buf_a = np.zeros((T, E, A), np.int64)
        buf_lp = np.zeros((T, E, A), np.float32)
        buf_v = np.zeros((T, E, A), np.float32)
        buf_r = np.zeros((T, E), np.float32)
        buf_d = np.zeros((T, E), np.float32)

        actor.eval(); critic.eval()
        with torch.no_grad():
            for t in range(T):
                buf_l[t], buf_h[t] = vec.local, vec.hcur
                buf_c[t] = critic_input(centralised, vec.local, vec.hcur, vec.glob)
                Lt = torch.as_tensor(buf_l[t].reshape(E * A, LOCAL_DIM), device=device)
                Ht = torch.as_tensor(np.repeat(buf_h[t], A, 0), device=device)
                dist = torch.distributions.Categorical(logits=actor(Lt, Ht))
                act = dist.sample()
                buf_lp[t] = dist.log_prob(act).cpu().numpy().reshape(E, A)
                buf_v[t] = critic(torch.as_tensor(buf_c[t], device=device)
                                  ).cpu().numpy().reshape(E, A)
                buf_a[t] = act.cpu().numpy().reshape(E, A)
                r, d, fin = vec.step(buf_a[t])
                buf_r[t], buf_d[t] = r, d
                for st in fin:
                    recent.append(st["dwell"])
            v_last = critic(torch.as_tensor(
                critic_input(centralised, vec.local, vec.hcur, vec.glob),
                device=device)).cpu().numpy().reshape(E, A)

        vals = (np.asarray(vnorm.denormalize(buf_v), np.float32)
                if vnorm.debias > 0 else buf_v)
        vlast = (np.asarray(vnorm.denormalize(v_last), np.float32)
                 if vnorm.debias > 0 else v_last)
        adv, ret = compute_gae(buf_r, buf_d, vals, vlast,
                               HP["gamma"], HP["gae_lambda"])

        actor.train(); critic.train()
        N = T * E * A
        Lb = torch.as_tensor(buf_l.reshape(N, LOCAL_DIM), device=device)
        Hb = torch.as_tensor(np.repeat(buf_h.reshape(T * E, H_DIM), A, 0), device=device)
        Cb = torch.as_tensor(buf_c.reshape(N, -1), device=device)
        Ab = torch.as_tensor(buf_a.reshape(N), device=device)
        LPb = torch.as_tensor(buf_lp.reshape(N), device=device)
        Vold = torch.as_tensor(buf_v.reshape(N), device=device)
        Rb = torch.as_tensor(ret.reshape(N), device=device)
        vnorm.update(Rb)
        Rn = torch.as_tensor(np.asarray(vnorm.normalize(Rb.cpu().numpy()), np.float32),
                             device=device)
        advb = torch.as_tensor(adv.reshape(N), device=device)
        advb = (advb - advb.mean()) / (advb.std() + 1e-8)
        mb = N // HP["n_minibatch"]

        for _ in range(HP["ppo_epochs"]):
            perm = torch.randperm(N, device=device)
            for k in range(HP["n_minibatch"]):
                ix = perm[k * mb:(k + 1) * mb]
                dist = torch.distributions.Categorical(logits=actor(Lb[ix], Hb[ix]))
                loss_pi = clipped_policy_loss(dist.log_prob(Ab[ix]), LPb[ix],
                                              advb[ix], dist.entropy(),
                                              HP["clip"], HP["entropy_coef"])
                opt_a.zero_grad(set_to_none=True)
                loss_pi.backward()
                nn.utils.clip_grad_norm_(actor.parameters(), HP["max_grad_norm"])
                opt_a.step()

                v = critic(Cb[ix])
                vc = Vold[ix] + torch.clamp(v - Vold[ix], -HP["clip"], HP["clip"])
                loss_v = torch.max(
                    F.huber_loss(v, Rn[ix], delta=HP["huber_delta"], reduction="none"),
                    F.huber_loss(vc, Rn[ix], delta=HP["huber_delta"], reduction="none")
                ).mean()
                opt_c.zero_grad(set_to_none=True)
                loss_v.backward()
                nn.utils.clip_grad_norm_(critic.parameters(), HP["max_grad_norm"])
                opt_c.step()

        if upd in eval_at:
            rows = evaluate_team(actor, cfg, validation_specs, bank, max_steps, device)
            vd = mean_of(rows)
            curve.append({"update": upd, "env_steps": upd * T * E,
                          "train_dwell": float(np.mean(recent)) if recent else 0.0,
                          "val_dwell": vd, "val_depth": mean_of(rows, "depth"),
                          "val_protected": mean_of(rows, "protected"),
                          "seconds": time.time() - t0})
            if vd > best["val"]:
                best = {"val": vd, "actor": copy.deepcopy(actor.state_dict()),
                        "update": upd}
            if verbose:
                print(f"      upd {upd:4d}/{n_updates}  steps {upd*T*E:8d}  "
                      f"train {curve[-1]['train_dwell']:6.2f}  val {vd:6.2f}  "
                      f"({time.time()-t0:.0f}s)", flush=True)

    if best["actor"] is not None:
        actor.load_state_dict(best["actor"])
    test_rows = evaluate_team(actor, cfg, test_specs, bank, max_steps, device)
    h0_rows = evaluate_team(actor, cfg, test_specs, bank, max_steps, device, h_zero=True)

    def summarise(rows):
        keys = ("dwell", "depth", "protected", "exposed", "length",
                "lure_chains", "dead_ends", "capacity_violations",
                "decoys_deployed", "episode_reward")
        return {k: mean_of(rows, k) for k in keys}

    return {
        "seed": seed, "centralised": centralised, "window": window,
        "env_steps": n_updates * T * E, "updates": n_updates,
        "curve": curve,
        "best_update": best["update"], "best_validation_dwell": best["val"],
        "test": test_rows, "test_summary": summarise(test_rows),
        "test_h0_summary": summarise(h0_rows),
        "seconds": time.time() - t0,
        "actor_state": actor.state_dict(),
    }
