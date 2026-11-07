"""Report all raw metrics, distinguishing episode variability from seed variability."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parent
METHODS = ['Static','Random','Heuristic','DQN_Individual','Deception_Only','Stackelberg','Tabular_QL','CoADAM_DQN']
METRICS = ['AMR','InfectionRate','CumulativeReward','DSR','FAR','MTTD','AttackerDwellTime','DefenseCostEfficiency','AttackerCumulativeReward','EpisodeLength']

def extract(path, expected=None):
    data = loadmat(path, simplify_cells=True)
    rows = []
    for table, key in [(5,'results_tableA'), (6,'results_tableB')]:
        results = list(data[key])
        if len(results) != 8:
            raise ValueError(f'{path}: expected eight methods')
        for method, result in zip(METHODS, results):
            if result['name'] != method:
                raise ValueError('Method order/name mismatch')
            for metric in METRICS:
                values = np.atleast_1d(result[metric]['raw']).astype(float)
                if not np.isfinite(values).all() or (expected is not None and len(values) != expected):
                    raise ValueError(f'Invalid or incomplete raw results: {method}/{metric}')
                for episode, value in enumerate(values, 1):
                    rows.append(dict(table=table,method=method,metric=metric,episode=episode,value=float(value)))
    return rows

def report(output):
    output = Path(output)
    manifest = json.loads((output/'manifest.json').read_text())
    with (ROOT/'paper_targets.csv').open(encoding='utf-8') as handle:
        targets = list(csv.DictReader(handle))
    allrows, cells = [], []
    for cell in sorted(output.glob('*/seed_*')):
        if not (cell/'complete.json').exists():
            continue
        settings = json.loads((cell/'settings.json').read_text())
        rows = extract(cell/'results/baseline_results_final.mat', settings['eval_episodes'])
        for row in rows:
            row.update(track=settings['track'],seed=settings['seed'])
        allrows.extend(rows)
        cells.append(settings)
    grouped = defaultdict(list)
    for row in allrows:
        grouped[row['track'],row['seed'],row['table'],row['method'],row['metric']].append(row['value'])
    lines = ['# Co-ADAM Tables 5 and 6 reproduction attempt', '',
        f"Mode: **{manifest['mode']}**. Completed cells: **{len(cells)}/{manifest['expected_cells']}**.", '',
        'This is an assumption-documented reimplementation around released code, not a certified exact reproduction. '
        'Smoke results are software checks only. Published values are targets, never training criteria.', '',
        'Primary tables below: mean ± sample SD of independent training-seed means. '
        'The paper reports evaluation variability; these SDs have different meanings. '
        'Per-seed episode SDs appear below. All rates are fractions (multiply by 100 for percent).', '']
    summary = []
    for track in manifest['protocol']['tracks']:
        for table in (5,6):
            lines += [f'## {track}: Table {table} — '+('random attacker' if table==5 else 'adaptive attacker'), '',
                '| Method | Seeds | AMR | Infection | Reward | DSR |', '|---|---:|---:|---:|---:|---:|']
            for method in METHODS:
                display = []
                for metric in METRICS:
                    values = []
                    for setting in cells:
                        if setting['track'] != track: continue
                        raw = grouped[track,setting['seed'],table,method,metric]
                        if raw:
                            values.append(float(np.mean(raw)))
                            summary.append(dict(track=track,table=table,method=method,metric=metric,seed=setting['seed'],mean=np.mean(raw),episode_sd=np.std(raw,ddof=1),episodes=len(raw)))
                    mean = np.mean(values) if values else float('nan')
                    sd = np.std(values,ddof=1) if len(values)>1 else float('nan')
                    if metric in METRICS[:4]: display.append(f'{mean:.4f} ± {sd:.4f}' if values else 'Pending')
                n = sum(s['track']==track for s in cells)
                lines.append(f'| {method} | {n} | '+' | '.join(display)+' |')
            lines += ['', '| Method | Metric | Published mean | Our seed mean | Difference |', '|---|---|---:|---:|---:|']
            for target in targets:
                if int(target['table']) != table: continue
                for metric in METRICS[:4]:
                    reference = target.get(metric+'_mean','')
                    if not reference: continue
                    means=[s['mean'] for s in summary if s['track']==track and s['table']==table and s['method']==target['method'] and s['metric']==metric]
                    actual=np.mean(means) if means else None
                    lines.append(f"| {target['method']} | {metric} | {float(reference):.4f} | "+(f'{actual:.4f} | {actual-float(reference):+.4f} |' if actual is not None else 'Pending | Pending |'))
            lines.append('')
    lines += ['## Every seed: all recorded metrics', '', '| Track | Table | Method | Seed | Metric | Mean | Episode SD | Episodes |', '|---|---:|---|---:|---|---:|---:|---:|']
    for s in summary:
        lines.append(f"| {s['track']} | {s['table']} | {s['method']} | {s['seed']} | {s['metric']} | {s['mean']:.6f} | {s['episode_sd']:.6f} | {s['episodes']} |")
    lines += ['', '## Degradation score (source formula; correspondence to paper remains unconfirmed)', '',
        'AMR(random) − AMR(adaptive) + Infection(adaptive) − Infection(random) + 0.5 × |DSR(random) − DSR(adaptive)|.', '',
        '| Track | Method | Seed | Calculated | Published Table 6 |', '|---|---|---:|---:|---:|']
    lookup={(s['track'],s['method'],s['seed'],s['table'],s['metric']):s['mean'] for s in summary}
    for setting in cells:
        for method in METHODS:
            def val(t,m): return lookup[setting['track'],method,setting['seed'],t,m]
            score=val(5,'AMR')-val(6,'AMR')+val(6,'InfectionRate')-val(5,'InfectionRate')+.5*abs(val(5,'DSR')-val(6,'DSR'))
            target=next(t['DegradationScore'] for t in targets if t['table']=='6' and t['method']==method)
            lines.append(f"| {setting['track']} | {method} | {setting['seed']} | {score:.6f} | {target} |")
    lines += ['', '## Training curves', '', '| Cell | Curve | Column | First | Last | Minimum | Maximum |', '|---|---|---|---:|---:|---:|---:|']
    for cell in sorted(output.glob('*/seed_*')):
        for filename in ('training.csv','tabular_training.csv'):
            path=cell/'results'/filename
            if not path.exists(): continue
            with path.open(encoding='utf-8-sig') as handle: curve=list(csv.DictReader(handle))
            if not curve: continue
            for column in curve[0]:
                if column=='episode': continue
                values=np.array([float(r[column]) for r in curve])
                lines.append(f'| {cell.parent.name}/{cell.name} | [{filename}]({path.relative_to(output).as_posix()}) | {column} | {values[0]:.5f} | {values[-1]:.5f} | {min(values):.5f} | {max(values):.5f} |')
    lines += ['', '## Interpretation', '',
        'Do not select matching seeds or tune assumptions against these tables. Numerical proximity cannot establish that the original experiment was recovered. '
        'The two tracks change several settings together, so their difference cannot isolate a single mechanism. '
        'No significance or equivalence claim is made automatically. Review all seeds and the unresolved release differences before comparison with TEMARL.', '',
        'Training curves, checkpoints, generated source patches and stage logs are retained within every cell. Failed/incomplete cells are not silently counted as completed.']
    (output/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    for name,rows in [('episodes.csv',allrows),('seed_summary.csv',summary)]:
        if rows:
            with (output/name).open('w',newline='',encoding='utf-8') as handle:
                writer=csv.DictWriter(handle,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return len(cells)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('output'); args=parser.parse_args(); report(args.output)
