"""Combine evaluation-only repeats without choosing results by performance."""
import argparse
import json
from pathlib import Path
import numpy as np
import experiment as spec


def est(x):
    x = np.asarray(x, float)
    return float(x.mean()), float(x.std(ddof=1))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path('results/reevaluations'))
    args = ap.parse_args()
    files = sorted(args.root.glob('repeat_*/evaluation.json'))
    if not files:
        raise RuntimeError('No reevaluation files found')
    runs = [json.loads(p.read_text()) for p in files]
    lines = ['# Combined evaluation-only repeats', '',
             f'Repeats: {len(runs)}; trained checkpoints were unchanged.',
             'Each seed is averaged across repeats before mean +/- SD is calculated across 10 training seeds.', '',
             '| Model | Dwell time (steps) | Interaction depth (techniques) | Asset protection | Seeds |',
             '|---|---:|---:|---:|---:|']
    output = []
    for encoder,learner in spec.MAIN_ARMS + spec.CONTROL_ARMS:
        by_seed = {}
        for run in runs:
            for row in run['records']:
                c = row['cell']
                if (c['encoder'],c['learner']) == (encoder,learner):
                    by_seed.setdefault(c['seed'], []).append(row['summary'])
        metrics = {}
        for key in spec.METRICS:
            values = [np.mean([r[key] for r in by_seed[s]]) for s in sorted(by_seed)]
            metrics[key] = est(values)
        lines.append(f"| {encoder} + {learner} | {metrics['dwell'][0]:.3f} +/- {metrics['dwell'][1]:.3f} | "
                     f"{metrics['depth'][0]:.3f} +/- {metrics['depth'][1]:.3f} | "
                     f"{100*metrics['protected'][0]:.3f} +/- {100*metrics['protected'][1]:.3f}% | {len(by_seed)} |")
        output.append(dict(encoder=encoder,learner=learner,metrics=metrics))
    target = args.root / 'COMBINED_RESULTS.md'
    target.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (args.root/'combined_results.json').write_text(json.dumps(dict(repeats=len(runs), results=output),indent=2)+'\n')
    print('Wrote',target)
