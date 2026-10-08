"""Re-evaluate saved policies with new matched test randomness; never trains."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

import _frozen  # noqa: F401
import experiment as spec
from encoders_marl import build_encoder
from env_marl import EngagementEnv, EnvConfig, EpisodeSource, N_AGENTS, SCRIPT_IDS
from mappo import Actor, evaluate_team
from pretrain_marl import HistoryBank
from run_experiment import cell_name


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def evaluate_fixed(joint, cfg, specs):
    rows = []
    for sp in specs:
        env = EngagementEnv(cfg).reset(sp)
        while not env.done:
            env.step(joint)
        rows.append(env.episode_stats())
    return rows


def mean(rows, key):
    return float(np.mean([r[key] for r in rows]))


def estimate(values):
    x = np.asarray(values, float)
    return dict(mean=float(x.mean()), sd=float(x.std(ddof=1)), n=len(x))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, default=Path('results/main'))
    ap.add_argument('--repeat-id', type=int, required=True)
    ap.add_argument('--episodes', type=int, default=500)
    ap.add_argument('--device', choices=['cpu','cuda'], default='cuda')
    ap.add_argument('--output-root', type=Path, default=Path('results/reevaluations'))
    args = ap.parse_args()
    if args.repeat_id < 1 or args.episodes < 1:
        ap.error('repeat-id and episodes must be positive')
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA requested but unavailable')
    destination = args.output_root / f'repeat_{args.repeat_id:03d}'
    if destination.exists():
        raise RuntimeError(f'{destination} already exists; choose a new repeat-id')
    manifest = json.loads((args.source / 'manifest.json').read_text())
    cfg = EnvConfig(**manifest['env_config'])
    records = []
    # Repeat id changes simulator randomness only. All arms with the same model
    # seed receive the same EpisodeSpec objects.
    specs_by_seed = {seed: EpisodeSource(1_000_000 * args.repeat_id + 300_000 + seed,
                                         SCRIPT_IDS, 'test').take(args.episodes)
                     for seed in manifest['seeds']}
    for cell in manifest['expected_cells']:
        name = cell_name(cell)
        cp_path = args.source / 'checkpoints' / f'{name}.pt'
        rec_path = args.source / 'cells' / f'{name}.json'
        prior = json.loads(rec_path.read_text())
        if hashlib.sha256(cp_path.read_bytes()).hexdigest() != prior['checkpoint_sha256']:
            raise RuntimeError(f'Checkpoint hash mismatch: {name}')
        checkpoint = torch.load(cp_path, map_location=args.device, weights_only=False)
        if checkpoint['cell'] != cell:
            raise RuntimeError(f'Checkpoint cell mismatch: {name}')
        encoder = None
        if cell['encoder'] != 'NoHistory':
            encoder = build_encoder(cell['encoder']).to(args.device)
            encoder.load_state_dict(checkpoint['encoder'])
            encoder.freeze()
        actor = Actor().to(args.device)
        actor.load_state_dict(checkpoint['actor'])
        rows = evaluate_team(actor, cfg, specs_by_seed[cell['seed']],
                             HistoryBank(encoder, args.device), args.device)
        summary = {k: mean(rows, k) for k in spec.METRICS}
        records.append(dict(cell=cell, checkpoint=str(cp_path), summary=summary))
        print(f"{name}: dwell={summary['dwell']:.3f} depth={summary['depth']:.3f} "
              f"protection={100*summary['protected']:.2f}%", flush=True)
    grouped = []
    lines = [f'# Evaluation-only repeat {args.repeat_id}', '',
             f'Loaded 80 saved checkpoints; no model training or parameter updates occurred.',
             f'Each cell used {args.episodes} held-out exact-replay episodes with new matched simulator randomness.', '',
             '| Model | Dwell time (steps) | Interaction depth (techniques) | Asset protection | Seeds |',
             '|---|---:|---:|---:|---:|']
    for encoder, learner in spec.MAIN_ARMS + spec.CONTROL_ARMS:
        arm = [r for r in records if (r['cell']['encoder'],r['cell']['learner']) == (encoder,learner)]
        stats = {k: estimate([r['summary'][k] for r in arm]) for k in spec.METRICS}
        grouped.append(dict(encoder=encoder, learner=learner, metrics=stats))
        lines.append(f"| {encoder} + {learner} | {stats['dwell']['mean']:.3f} +/- {stats['dwell']['sd']:.3f} | "
                     f"{stats['depth']['mean']:.3f} +/- {stats['depth']['sd']:.3f} | "
                     f"{100*stats['protected']['mean']:.3f} +/- {100*stats['protected']['sd']:.3f}% | {len(arm)} |")
    static_path = args.source / 'static_honeypot.json'
    static = None
    if static_path.exists():
        selected = {r['seed']: r['joint'] for r in json.loads(static_path.read_text())['rows']}
        per_seed = []
        for seed in manifest['seeds']:
            rows = evaluate_fixed(selected[seed], cfg, specs_by_seed[seed])
            per_seed.append({k: mean(rows,k) for k in spec.METRICS})
        static = dict(per_seed=[dict(seed=seed, **row)
                                for seed,row in zip(manifest['seeds'], per_seed)],
                      metrics={k: estimate([r[k] for r in per_seed]) for k in spec.METRICS})
        sm = static['metrics']
        lines += ['', '## Static-honeypot baseline', '',
                  '| Dwell time (steps) | Interaction depth (techniques) | Asset protection | Seeds |',
                  '|---:|---:|---:|---:|',
                  f"| {sm['dwell']['mean']:.3f} +/- {sm['dwell']['sd']:.3f} | "
                  f"{sm['depth']['mean']:.3f} +/- {sm['depth']['sd']:.3f} | "
                  f"{100*sm['protected']['mean']:.3f} +/- {100*sm['protected']['sd']:.3f}% | 10 |"]
    result = dict(repeat_id=args.repeat_id, source=str(args.source), episodes=args.episodes,
                  trained=False, randomness_seed_base=1_000_000*args.repeat_id+300_000,
                  records=records, grouped=grouped, static_honeypot=static)
    write_json(destination / 'evaluation.json', result)
    (destination / 'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('FINISHED:', destination / 'RESULTS.md')


if __name__ == '__main__':
    main()
