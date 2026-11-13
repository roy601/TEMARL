"""Evaluate a validation-selected static honeypot on exact replay test episodes."""
import argparse
import itertools
import json
from multiprocessing import get_context
from pathlib import Path

import numpy as np

import _frozen  # sets the bundled v2 dependency path and verifies inputs
from d3fend_payoff import N_ACTIONS
from env_marl import EngagementEnv, EnvConfig, EpisodeSource, N_AGENTS, SCRIPT_IDS
from mappo import HP, SEED_TEST, SEED_VAL


class FixedPolicy:
    def __init__(self, joint):
        self.joint = joint

    def __call__(self, _env):
        return self.joint


def score(joint, specs, cfg):
    values = []
    for spec in specs:
        env = EngagementEnv(cfg).reset(spec)
        while not env.done:
            env.step(joint)
        values.append(env.episode_stats())
    return values


def one_seed(args):
    seed, cfg_dict, n_test = args
    cfg = EnvConfig(**cfg_dict)
    validation = EpisodeSource(SEED_VAL + seed, SCRIPT_IDS, 'validation').take(HP['val_episodes'])
    candidates = itertools.product(range(N_ACTIONS), repeat=N_AGENTS)
    best, best_value, best_active = None, -1.0, None
    for joint in candidates:
        rows = score(joint, validation, cfg)
        value = float(np.mean([r['dwell'] for r in rows]))
        active = sum(a != 0 for a in joint)
        if value > best_value or (value == best_value and active < best_active):
            best, best_value, best_active = joint, value, active
    test = EpisodeSource(SEED_TEST + seed, SCRIPT_IDS, 'test').take(n_test)
    rows = score(best, test, cfg)
    return dict(seed=seed, joint=list(best), validation_dwell=best_value,
                dwell=float(np.mean([r['dwell'] for r in rows])),
                depth=float(np.mean([r['depth'] for r in rows])),
                protected=float(np.mean([r['protected'] for r in rows])),
                n_test=n_test)


def estimate(values):
    x = np.asarray(values, float)
    return dict(mean=float(x.mean()), sd=float(x.std(ddof=1)), n=len(x))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, default=Path('results/main'))
    parser.add_argument('--workers', type=int, default=1)
    args = parser.parse_args()
    manifest = json.loads((args.results / 'manifest.json').read_text())
    jobs = [(seed, manifest['env_config'], manifest['n_test']) for seed in manifest['seeds']]
    if args.workers > 1:
        with get_context('spawn').Pool(args.workers) as pool:
            rows = pool.map(one_seed, jobs)
    else:
        rows = [one_seed(job) for job in jobs]
    result = dict(definition='One fixed joint decoy action for the whole episode; selected by validation dwell only.',
                  matched_test_protocol=True, rows=rows,
                  summary={key: estimate([r[key] for r in rows])
                           for key in ('dwell','depth','protected')})
    target = args.results / 'static_honeypot.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['summary'], indent=2))
    print('Wrote', target)
