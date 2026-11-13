"""Generate requested result tables, without selecting models on test scores."""
import argparse
import csv
import io
import json
from pathlib import Path

import numpy as np
from scipy import stats

import experiment as spec

LABELS = dict(dwell='Dwell time (steps)', depth='Interaction depth (techniques)',
              protected='Asset protection')


def estimate(values):
    x = np.asarray(values, float)
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if len(x) > 1 else None
    half = float(stats.t.ppf(.975, len(x)-1) * sd / np.sqrt(len(x))) if len(x) > 1 else None
    return dict(mean=mean, sd=sd, ci95=None if half is None else [mean-half, mean+half], n=len(x))


def table(records, arms, scenario=None):
    lines = ['| Model | Dwell time (steps) | Interaction depth (techniques) | Asset protection | Seeds |',
             '|---|---:|---:|---:|---:|']
    export = []
    for encoder, learner in arms:
        rows = [r for r in records if (r['cell']['encoder'], r['cell']['learner']) == (encoder, learner)]
        # Folds/episodes are repeated observations, not independent seeds.
        per_seed = {}
        for r in rows:
            trial = [t for t in r['test'] if scenario is None or t['script'] == scenario]
            if trial:
                per_seed.setdefault(r['cell']['seed'], []).append(
                    {k: float(np.mean([t[k] for t in trial])) for k in spec.METRICS})
        if not per_seed:
            lines.append(f'| {encoder} + {learner} | Pending | Pending | Pending | 0 |')
            continue
        cells = []
        for metric in spec.METRICS:
            e = estimate([np.mean([v[metric] for v in values]) for values in per_seed.values()])
            export.append(dict(encoder=encoder, learner=learner, scenario=scenario, metric=metric, **e))
            scale = 100 if metric == 'protected' else 1
            suffix = '%' if metric == 'protected' else ''
            cell = f"{e['mean']*scale:.3f}"
            cell += f" +/- {e['sd']*scale:.3f}" if e['sd'] is not None else ' (SD unavailable)'
            cells.append(cell + suffix)
        lines.append(f"| {encoder} + {learner} | " + ' | '.join(cells) + f' | {len(per_seed)} |')
    return '\n'.join(lines), export


def paired_tests(records):
    contrasts = [(f'{e}: MAPPO - IPPO', (e,'MAPPO'), (e,'IPPO')) for e in spec.ENCODERS]
    contrasts += [(f'{l}: {a} - {b}', (a,l), (b,l)) for l in spec.LEARNERS
                  for a,b in [('Transformer','GRU'), ('Transformer','LSTM'), ('GRU','LSTM')]]
    result = []
    for name,a,b in contrasts:
        for metric in spec.METRICS:
            arms = []
            for arm in (a,b):
                by_seed = {}
                for r in records:
                    if (r['cell']['encoder'],r['cell']['learner']) == arm:
                        by_seed.setdefault(r['cell']['seed'], []).append(r['test_summary'][metric])
                arms.append({k:np.mean(v) for k,v in by_seed.items()})
            seeds = sorted(set(arms[0]) & set(arms[1]))
            if len(seeds) < 2:
                continue
            d = np.array([arms[0][s]-arms[1][s] for s in seeds])
            sd = float(d.std(ddof=1))
            p = float(stats.ttest_1samp(d, 0).pvalue) if sd else (1.0 if np.all(d==0) else 0.0)
            result.append(dict(contrast=name, metric=metric, difference=estimate(d),
                               p_raw=p, effect_d=float(d.mean()/sd) if sd else None))
    last = 0.0
    for rank,i in enumerate(sorted(range(len(result)), key=lambda i:result[i]['p_raw'])):
        last = max(last, min(1., (len(result)-rank)*result[i]['p_raw']))
        result[i]['p_holm'] = last
    return result


def readable_predictions(records):
    """Fixed first/middle/last test windows, never chosen by prediction quality."""
    import _frozen
    from vocab_v2 import ID_TO_TECHNIQUE, ID_TO_META

    def technique(tid):
        return f"{ID_TO_TECHNIQUE[tid]} ({ID_TO_META[tid]['name']})".replace('|', '/')

    lines = ['', '## Prediction examples in plain language', '',
             'These are next-technique predictions from observed technique labels, not generated text or raw-log interpretation.',
             'Probabilities are softmax model scores, not calibrated guarantees. Correctness is checked at parent-technique level.',
             'Main accuracy above uses all held-out windows and seeds. These examples use one shared seed, without ensembling.', '']
    available = {e: {r['cell']['seed']: r for r in records
                      if r['cell']['encoder'] == e and r['cell']['learner'] == 'MAPPO'
                      and (r.get('prediction_test') or {}).get('examples')}
                 for e in spec.ENCODERS}
    common = set.intersection(*(set(v) for v in available.values()))
    if not common:
        return lines + ['Pending: saved prediction examples for all three encoders at a common seed are required.']
    seed = min(common)
    indexes = {e: {(x['run_id'], x['next_step']): x
                   for x in available[e][seed]['prediction_test']['examples']}
               for e in spec.ENCODERS}
    keys = set(indexes[spec.ENCODERS[0]])
    if any(set(v) != keys for v in indexes.values()):
        raise ValueError('Prediction examples do not use identical test windows')
    lines += [f'Example seed: {seed}. Display rule: first, middle and last prediction window of every test run.', '']
    for run in sorted({k[0] for k in keys}):
        steps = sorted(k[1] for k in keys if k[0] == run)
        for step in sorted({steps[0], steps[len(steps)//2], steps[-1]}):
            x = indexes[spec.ENCODERS[0]][run, step]
            for encoder in spec.ENCODERS:
                other = indexes[encoder][run, step]
                if any(other[field] != x[field] for field in ('history_ids','actual_id','actual_source','source_history')):
                    raise ValueError('Prediction context mismatch across encoders')
            lines += [f'### {run}: predict step {step}', '',
                      '**Observed history (oldest to newest):** ' + ' -> '.join(map(technique, x['history_ids'])), '',
                      '**Original source labels:** ' + ' -> '.join(x['source_history']), '',
                      f"**Actual next technique:** {technique(x['actual_id'])}; original label: {x['actual_source']}.", '',
                      '| Model | First prediction | Probability | Second prediction | Probability | Third prediction | Probability | First prediction correct? |',
                      '|---|---|---:|---|---:|---|---:|---|']
            for encoder in spec.ENCODERS:
                row = indexes[encoder][run, step]
                cells = []
                for tid,p in zip(row['top3_ids'], row['top3_probabilities']):
                    cells += [technique(tid), f'{100*p:.2f}%']
                lines.append(f"| {encoder} | {' | '.join(cells)} | {'Yes' if row['correct'] else 'No'} |")
            lines += ['']
    return lines


def generate(folder):
    from run_experiment import write_json, cell_name
    folder = Path(folder)
    manifest = json.loads((folder/'manifest.json').read_text())
    records = []
    missing = []
    for c in manifest['expected_cells']:
        p = folder/'cells'/(cell_name(c)+'.json')
        if not p.exists():
            missing.append(cell_name(c)); continue
        r = json.loads(p.read_text())
        if r['cell'] != c or r['fingerprint'] != manifest['fingerprint'] or r['smoke'] != manifest['smoke']:
            raise ValueError(f'Stale or mismatched result: {p}')
        if len(r['test']) != manifest['n_test'] or not np.isfinite(r['val_best']):
            raise ValueError(f'Invalid evaluation count or validation score: {p}')
        for k in spec.METRICS:
            values = np.array([t[k] for t in r['test']], float)
            if not np.isfinite(values).all() or not np.isclose(values.mean(), r['test_summary'][k]):
                raise ValueError(f'Invalid metric: {p}, {k}')
        records.append(r)
    title = 'SMOKE CHECK ONLY - NOT THESIS RESULTS' if manifest['smoke'] else 'Thesis version 2310 results'
    lines = [f'# {title}', '', f"Study: {manifest['study']}; completed cells: {len(records)}/{len(manifest['expected_cells'])}.", '',
             'Values are mean +/- sample SD of seed means. JSON/CSV include 95% t intervals.',
             'Asset protection means the attacker did not reach its configured objective before the horizon.',
             'Dwell counts decoy-engaged steps; depth counts distinct technique IDs engaged by decoys.', '',
             '## Six model combinations', '']
    t, export = table(records, spec.MAIN_ARMS)
    lines += [t, '', '## No-intent controls', '']
    t, rows = table(records, spec.CONTROL_ARMS); export += rows; lines += [t]
    lines += ['', '## What the defence results mean', '',
              'Dwell is the number of simulator steps engaged with decoys, not seconds. Depth counts distinct engaged parent techniques.',
              'Protection is the percentage of episodes ending without the configured attacker objective being reached; it does not mean no host was touched.',
              'Higher values are desirable for these three metrics. +/- shows variation across training seeds, not prediction confidence.', '',
              '| Combination | Plain-language reading of average test performance |', '|---|---|']
    for encoder, learner in spec.MAIN_ARMS + spec.CONTROL_ARMS:
        arm = [r for r in records if (r['cell']['encoder'],r['cell']['learner']) == (encoder,learner)]
        if arm:
            means = {k: np.mean([r['test_summary'][k] for r in arm]) for k in spec.METRICS}
            lines.append(f"| {encoder} + {learner} | Engaged the attacker for {means['dwell']:.2f} steps and {means['depth']:.2f} distinct techniques per episode; prevented the configured objective in {100*means['protected']:.1f}% of episodes. |")
    lines += ['', '## Held-out next-technique prediction', '',
              'MAPPO cells only: IPPO repeats the same encoder/seed pretraining and is not an independent replicate.',
              'Top-1 is the percentage with the correct first prediction. Top-3 is the percentage with the answer among the three highest-scored techniques.',
              '',
              '| Encoder | Top-1 (%) | Top-3 (%) | Seeds |', '|---|---:|---:|---:|']
    for encoder in spec.ENCODERS:
        pred = [r['prediction_test'] for r in records
                if r['cell']['encoder'] == encoder and r['cell']['learner'] == 'MAPPO'
                and r.get('prediction_test')]
        if pred:
            values = []
            for key in ('top1','top3'):
                e = estimate([p[key] for p in pred])
                values.append(f"{100*e['mean']:.2f}" +
                              (f" +/- {100*e['sd']:.2f}" if e['sd'] is not None else ' (one seed)'))
            lines.append(f"| {encoder} | {' | '.join(values)} | {len(pred)} |")
        else:
            lines.append(f'| {encoder} | Pending | Pending | 0 |')
    lines += readable_predictions(records)
    selected = None
    if not missing and manifest['study'] == 'main':
        scores = {e:float(np.mean([r['val_best'] for r in records if r['cell']['encoder']==e
                                  and r['cell']['learner']=='MAPPO'])) for e in spec.ENCODERS}
        selected = max(spec.ENCODERS, key=lambda e:scores[e])
        lines += ['', '## Requested ablation', '', f'Validation-selected encoder: **{selected}**.',
                  'Selection uses mean validation dwell only; test outcomes are not used for selection.', '']
        t, _ = table(records, [(selected,'IPPO'), ('NoHistory','IPPO'), (selected,'MAPPO')])
        lines += [t, '', 'The first two rows isolate intent under IPPO; first versus third isolates critic information.',
                  'NoHistory + MAPPO above additionally isolates intent under MAPPO.',
                  'These selected-model ablations are descriptive/exploratory. Non-significance does not prove equivalence.']
        write_json(folder/'selection.json', dict(encoder=selected, validation_scores=scores, rule=spec.SELECTION))
    elif manifest['study'] == 'main':
        lines += ['', 'Ablation selection is pending until every expected cell has completed.']
    for sid in sorted({t['script'] for r in records for t in r['test']}):
        lines += ['', f'## Scenario {sid}', '']
        t, rows = table(records, spec.MAIN_ARMS + spec.CONTROL_ARMS, sid)
        export += rows; lines += [t]
    tests = paired_tests(records) if not missing and not manifest['smoke'] else []
    if tests:
        lines += ['', '## Fixed comparisons', '',
                  'Two-sided paired seed tests; Holm correction across all 27 architecture/learner/metric comparisons.',
                  'For LOSO, each seed is averaged over its seven folds before testing.', '',
                  '| Contrast | Metric | Mean difference | Holm p |', '|---|---|---:|---:|']
        for t in tests:
            lines.append(f"| {t['contrast']} | {LABELS[t['metric']]} | {t['difference']['mean']:.4f} | {t['p_holm']:.5f} |")
    lines += ['', '## Limits', '',
              '- Fixed five-zone engagement simulator, with four parameter-sharing agents.',
              '- Exact ordered playbook-label replay with the frozen parent-technique vocabulary; no synthetic attack sequence generation.',
              '- Grouped run holdout; near-duplicate variants may share prefixes. See REPLAY_DATA_AUDIT.json.',
              '- Repeated episodes vary simulator randomness, not independent source attacks. Intervals summarize training seeds on a fixed split.',
              '- NoHistory still observes local telemetry and recent locally observed technique; it removes the shared history embedding.',
              '- Reward optimizes dwell only. Depth and asset protection are evaluated outcomes, not guaranteed improvements.',
              '- Architecture choices differ from historical v7; old checkpoints and reported scores are not reused.',
              '- A small smoke run verifies execution only. It does not measure learning quality or support thesis claims.']
    write_json(folder/'analysis.json', dict(complete=not missing, missing=missing, selected_encoder=selected,
                                         smoke=manifest['smoke'], estimates=export, tests=tests))
    (folder/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=['encoder','learner','scenario','metric','mean','sd','ci95','n'])
    writer.writeheader(); writer.writerows(export)
    (folder/'metrics.csv').write_text(buf.getvalue(), encoding='utf-8')
    print('Report:', folder/'RESULTS.md', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('folder', type=Path)
    generate(ap.parse_args().folder)
