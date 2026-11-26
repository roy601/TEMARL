# -*- coding: utf-8 -*-
"""Hawkeyes replication: A2C agents (decisions 14-16), training and evaluation, all jobs (decision 21).

    python reproductions/hawkeyes2025/run.py smoke                 # 300 steps, nothing kept
    python reproductions/hawkeyes2025/run.py run --workers 8       # every job; finished jobs are skipped
    python reproductions/hawkeyes2025/run.py list                  # job count and how many are done
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hawk_env as H  # noqa: E402

OUT = HERE / "out" / "runs"
TRAIN_STEPS, EVAL_EPISODES, SEEDS = 30_000, 1_000, range(10)
LR, GAMMA, VALUE_COEF = 1e-3, 0.99, 0.5                     # Table 1 (decision 15)


class ActorCritic(nn.Module):                               # decision 14
    def __init__(self, n_in, n_act=len(H.GROUPS)):
        super().__init__()
        dims = [n_in, 2048, 1024, 512, 64]
        layers = []
        for a, b in zip(dims, dims[1:]):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.trunk = nn.Sequential(*layers)
        self.actor = nn.Linear(64, n_act)
        self.critic = nn.Linear(64, 1)

    def forward(self, x, mask):
        h = self.trunk(x)
        logits = self.actor(h).masked_fill(~mask, float("-inf"))
        return logits, self.critic(h).squeeze(-1)


def mask_of(groups):
    m = torch.zeros(len(H.GROUPS), dtype=torch.bool)
    m[groups] = True
    return m


class Agents:
    """D = 2 independent A2C agents with a shared reward (decisions 14-15)."""

    def __init__(self, n_in, gated):
        self.nets = [ActorCritic(n_in) for _ in H.HONEYPOTS]
        self.opts = [torch.optim.Adam(n.parameters(), lr=LR) for n in self.nets]
        self.gated = gated

    def act(self, env, obs, greedy=False, sample_rng=None):
        groups, _ = env.allowed_groups(self.gated)
        m = mask_of(groups)
        x = torch.as_tensor(obs).unsqueeze(0)
        acts = []
        for net in self.nets:
            with torch.no_grad():
                logits, _ = net(x, m.unsqueeze(0))
            p = torch.softmax(logits[0], -1)
            if greedy:
                acts.append(int(torch.argmax(p)))
            else:
                acts.append(int(torch.multinomial(p, 1, generator=sample_rng)))
        return acts, m

    def update(self, obs_list, mask_list, act_list, reward):
        """Monte-Carlo returns; rewards are 0 until the terminal step (Eq. 11)."""
        T = len(obs_list)
        G = torch.tensor([reward * GAMMA ** (T - 1 - t) for t in range(T)], dtype=torch.float32)
        X, M = torch.as_tensor(np.stack(obs_list)), torch.stack(mask_list)
        for d, (net, opt) in enumerate(zip(self.nets, self.opts)):
            logits, v = net(X, M)
            logp = torch.log_softmax(logits, -1).gather(1, torch.tensor([a[d] for a in act_list]).unsqueeze(1)).squeeze(1)
            adv = G - v
            loss = -(logp * adv.detach()).sum() + VALUE_COEF * (adv ** 2).sum()
            opt.zero_grad()
            loss.backward()
            opt.step()


def seed_all(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)


def train(agents, env, steps):
    done_steps, episodes = 0, 0
    while done_steps < steps:
        obs = env.reset()
        O, Mk, A = [], [], []
        while True:
            acts, m = agents.act(env, obs)
            O.append(obs), Mk.append(m), A.append(acts)
            obs, r, done, _ = env.step(acts)
            done_steps += 1
            if done:
                agents.update(O, Mk, A, r)
                episodes += 1
                break
    return episodes


def evaluate(env, chooser, episodes):
    counts = {"trap": 0, "fail": 0, "stuck": 0, "cap": 0}
    placements = {}
    for _ in range(episodes):
        obs = env.reset()
        while True:
            acts = chooser(env, obs)
            key = "".join(str(a) for a in sorted(acts))
            placements[key] = placements.get(key, 0) + 1
            obs, r, done, out = env.step(acts)
            if done:
                counts[out or "cap"] += 1
                break
    return {"dsr": 100.0 * counts["trap"] / episodes, "outcomes": counts, "placements": placements}


def baseline_chooser(kind, rng):
    def choose(env, obs):
        if kind == "Random":
            return [rng.randrange(len(H.GROUPS)) for _ in H.HONEYPOTS]
        return [H.GROUP_OF[H.CRITICAL]] * len(H.HONEYPOTS)   # Critical (decision 18)
    return choose


def job_list():
    jobs = []
    for pol in H.POLICIES:
        for fnr, fpr in H.FNR_FPR:
            for s in SEEDS:
                jobs.append(dict(scenario="S1", reading="primary", method="HMARL", policy=pol, fnr=fnr, fpr=fpr, seed=s))
                jobs.append(dict(scenario="S1", reading="primary", method="baselines", policy=pol, fnr=fnr, fpr=fpr, seed=s))
    for pol, (fnr, fpr) in [("HiE", H.FNR_FPR[0]), ("HiE", H.FNR_FPR[3]), ("Ran", H.FNR_FPR[0]),
                            ("RanE", H.FNR_FPR[0]), ("Mix", H.FNR_FPR[0])]:
        for s in SEEDS:
            jobs.append(dict(scenario="S2", reading="primary", method="MARL", policy=pol, fnr=fnr, fpr=fpr, seed=s))
    for pol in ("Ran", "RanE", "Mix"):
        for s in SEEDS:
            jobs.append(dict(scenario="S3", reading="primary", method="SO", policy=pol, fnr=0.05, fpr=0.02, seed=s))
    for rd in ("R1", "R2", "R3", "R4"):                     # R5 is evaluated inside the primary S1 jobs
        for pol in (["Mix"] if rd == "R1" else H.POLICIES):
            for s in SEEDS:
                jobs.append(dict(scenario="S1", reading=rd, method="HMARL", policy=pol, fnr=0.05, fpr=0.02, seed=s))
                jobs.append(dict(scenario="S1", reading=rd, method="baselines", policy=pol, fnr=0.05, fpr=0.02, seed=s))
    return jobs


def job_name(j):
    return f"{j['scenario']}_{j['reading']}_{j['method']}_{j['policy']}_fnr{j['fnr']:.2f}_s{j['seed']}"


def run_job(j):
    torch.set_num_threads(1)
    s = j["seed"]
    seed_all(s)
    reading = H.READINGS[j["reading"]]
    old, new = H.Network(False), H.Network(True)
    rng_train = random.Random(1_000_003 * s + 17)
    t0 = time.time()
    res = dict(j, train_steps=TRAIN_STEPS, eval_episodes=EVAL_EPISODES)

    def env_for(net, rng, state="full"):
        return H.Env(net, j["policy"], j["fnr"], j["fpr"], reading, rng, state)

    if j["method"] == "baselines":
        for kind in ("Random", "Critical"):
            rng = random.Random(1_000_003 * s + 29)
            res[kind] = evaluate(env_for(old, rng), baseline_chooser(kind, random.Random(1_000_003 * s + 31)), EVAL_EPISODES)
        res["seconds"] = round(time.time() - t0, 1)
        return res
    state = "so" if j["method"] == "SO" else "full"
    agents = Agents(len(H.REAL) if state == "so" else H.STATE_DIM, gated=(j["method"] != "MARL"))
    res["train_episodes"] = train(agents, env_for(old, rng_train, state), TRAIN_STEPS)
    res["train_seconds"] = round(time.time() - t0, 1)
    gen = torch.Generator().manual_seed(1_000_003 * s + 37)

    def greedy(env, obs):
        return agents.act(env, obs, greedy=True)[0]

    def sampled(env, obs):
        return agents.act(env, obs, greedy=False, sample_rng=gen)[0]

    primary_eval = sampled if reading.sample_eval else greedy
    res["eval"] = evaluate(env_for(old, random.Random(1_000_003 * s + 29), state), primary_eval, EVAL_EPISODES)
    if j["reading"] == "primary" and j["scenario"] == "S1" and j["fnr"] == 0.05:
        res["eval_R5_sampled"] = evaluate(env_for(old, random.Random(1_000_003 * s + 29), state), sampled, EVAL_EPISODES)
    if (j["scenario"] == "S3") or (j["scenario"] == "S1" and j["reading"] == "primary" and j["fnr"] == 0.05
                                   and j["policy"] in ("Ran", "RanE", "Mix")):
        res["eval_new"] = evaluate(env_for(new, random.Random(1_000_003 * s + 41), state), greedy, EVAL_EPISODES)
    res["seconds"] = round(time.time() - t0, 1)
    return res


def worker(names):
    jobs = {job_name(j): j for j in job_list()}
    for n in names:
        path = OUT / f"{n}.json"
        if path.exists():
            continue
        res = run_job(jobs[n])
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(res, indent=1), encoding="utf-8")
        os.replace(tmp, path)
        print(f"{n}: done in {res['seconds']} s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["smoke", "run", "list", "worker"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()
    if a.stage == "smoke":
        global TRAIN_STEPS, EVAL_EPISODES
        TRAIN_STEPS, EVAL_EPISODES = 300, 50
        for j in (job_list()[0], job_list()[1]):
            r = run_job(j)
            print(job_name(j), {k: v for k, v in r.items() if k in ("train_episodes", "seconds")},
                  r.get("eval", {}).get("dsr"), r.get("Random", {}).get("dsr"), r.get("Critical", {}).get("dsr"))
        return
    jobs = job_list()
    names = [job_name(j) for j in jobs]
    assert len(set(names)) == len(names)
    todo = [n for n in names if not (OUT / f"{n}.json").exists()]
    if a.stage == "list":
        print(f"{len(names)} jobs, {len(names) - len(todo)} done, {len(todo)} to do")
        return
    if a.stage == "worker":
        worker(a.names)
        return
    for f in ("TARGETS.csv", "DECISIONS.md", "hawk_env.py", "run.py"):
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", f], cwd=HERE).returncode != 0 or \
                subprocess.run(["git", "ls-files", "--error-unmatch", f], cwd=HERE, capture_output=True).returncode != 0:
            sys.exit(f"refusing to run: {f} is not committed unchanged")
    OUT.mkdir(parents=True, exist_ok=True)
    def priority(n):                                         # Table 3 first, then text targets, then the rest
        if "baselines" in n:
            return 4
        if n.startswith("S1_primary") and "fnr0.05" in n:
            return 0
        if n.startswith(("S2_", "S3_")):
            return 1
        return 2 if n.startswith("S1_primary") else 3
    todo.sort(key=lambda n: (priority(n), n))
    chunks = [todo[i::a.workers] for i in range(a.workers)]
    procs = [subprocess.Popen([sys.executable, __file__, "worker", *c]) for c in chunks if c]
    for p in procs:
        p.wait()
    print("all jobs finished" if all(p.returncode == 0 for p in procs) else "some worker failed")


if __name__ == "__main__":
    main()
