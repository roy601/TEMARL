"""Recorded CAM-LDS prediction -> frozen history -> IPPO/MAPPO replay study."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / 'camlds_encoder'))
import port
import data
import variants
# port inserts its frozen dependency directory. Prefer our explicit 81-label port.
sys.path.insert(0, str(HERE))
import env_cmd as env
import mappo_cmd as marl
import argparse
import dataclasses
import hashlib
import json
import os
import time
import uuid
import math
import numpy as np
import torch

ARMS = ('allpos', 'baseline', 'gru_allpos', 'lstm_allpos', 'NoHistory')

def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    def clean(value):
        if isinstance(value, float) and not math.isfinite(value):
            return None  # First validation improvement is measured from +infinity.
        if isinstance(value, dict): return {k: clean(v) for k,v in value.items()}
        if isinstance(value, (list,tuple)): return [clean(v) for v in value]
        return value
    tmp.write_text(json.dumps(clean(obj), indent=2, allow_nan=False), encoding='utf-8')
    for attempt in range(12):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(min(.1 * 2**attempt, 2))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()

def runs(fold, split):
    # Command sets are retained intact; fold['_steps'] fixes the chosen order.
    out = data._runs(fold['_steps'], fold[split + '_runs'])
    scenario = {s['run']: 'S' + str(s['base_scenario']) for s in fold['_steps']}
    for r in out:
        r['scenario'] = scenario[r['id']]
    return out

def specs(rs, seed, repeats):
    rng = np.random.default_rng(seed)
    meta = env.scenario_metadata()
    return [env.make_spec(r, rng, meta) for r in rs for _ in range(repeats)]

def audit():
    port.verify()
    steps = data.steps_for('main')
    fs = data.folds()
    for f in fs:
        tr, va, te = [set(f[k + '_runs']) for k in ('train', 'val', 'test')]
        assert not (tr & va or tr & te or va & te)
        for split in ('train', 'val', 'test'):
            assert runs(f, split), (f['fold'], split)
    assert env.PAYOFF.shape[0] == port.NT == marl.NT == 81
    meta = env.scenario_metadata()
    return {'source': 'CAM-LDS v1 recorded testbed execution metadata, DOI 10.5281/zenodo.18390561',
            'steps': len(steps), 'runs': len({s['run'] for s in steps}),
            'labels': port.NT, 'folds': len(fs),
            's4_rl_replay': 'included; inherited topology maps its unavailable target zone to the scenario entry zone',
            'order': 'Frozen exec_index (CSV adjusted-time order); 4 known S6 adjacent swaps versus execution rank. Not corrected silently.',
            'payoff_mapping': {t: env.TECHNIQUES[t]['id'] for t in port.LABELS},
            'scenario_metadata': {k: {n: v for n, v in m.items() if n != 'goal_mask'} for k, m in meta.items()},
            'hashes': {str(p.relative_to(REPO)): sha(p) for p in [
                REPO/'camlds_real/out/steps.jsonl', REPO/'camlds_real/out/vocab.json',
                REPO/'camlds_real/split_spec.py', REPO/'camlds_encoder/variants.py',
                HERE/'pipeline.py', HERE/'env_cmd.py', HERE/'mappo_cmd.py']}}

def checkpoint(arm, fold, seed, root):
    if arm == 'baseline':
        return root/'train'/'main'/'Transformer'/fold/f's{seed}'/'encoder.pt'
    return root/'variants'/arm/fold/f's{seed}'/'encoder.pt'

def ordered_folds(order):
    fs = data.folds()
    if order == 'execution':
        path = REPO/'camlds_real/out/sidecar/steps_link.jsonl'
        links = [json.loads(s) for s in path.read_text(encoding='utf-8').splitlines() if s.strip()]
        ranks = {(s['run'], s['source_row']): s['execution_rank'] for s in links}
        if len(ranks) != len(data.steps_for('main')):
            raise ValueError('Execution sidecar does not uniquely cover all steps')
        for f in fs:
            f['_steps'] = [dict(s, exec_index=ranks[(s['run'],s['source_row'])]) for s in f['_steps']]
    return fs

def encoder(arm, f, seed, args, cell):
    if arm == 'NoHistory':
        return None, None
    d = data.fold_data(f)
    existing = checkpoint(arm, f['fold'], seed, Path(args.encoder_root))
    local = cell/'encoder.pt'
    if args.order == 'execution' or local.exists():
        existing = local
    if not existing.exists():
        if not args.train_missing:
                raise FileNotFoundError(f'{existing}: use --train-missing. Execution-order mode requires fresh checkpoints.')
        budget = 2 if args.smoke else (18304 if arm in ('gru_allpos', 'lstm_allpos') else 9152)
        res, model = variants.train_variant(arm, data.W, seed, d['train'], d['val'], budget,
                    device=torch.device(args.device), checkpoint_dir=str(cell), patience_checks=16, progress=True)
        write(cell/'training.json', dataclasses.asdict(res))
        existing = local
    ck = torch.load(existing, map_location='cpu', weights_only=False)
    if ck.get('window', data.W) != data.W or ck.get('seed', seed) != seed:
        raise ValueError('Checkpoint window/seed mismatch')
    if 'variant' in ck and ck['variant'] != arm:
        raise ValueError('Checkpoint variant mismatch')
    model = variants.build_variant(arm, data.W).to(args.device)
    model.load_state_dict(ck['state_dict'], strict=True)
    model.eval()
    va = variants.numpy_logits(model, *d['val'][:2], torch.device(args.device))
    measured = port.Mx.bce(va, d['val'][2])
    expected = ck.get('validation_bce')
    if expected is not None and abs(measured - expected) > 1e-4:
        raise ValueError('Checkpoint does not reproduce validation BCE')
    threshold = port.Mx.select_threshold(port.Mx._sigmoid(va), d['val'][2])
    X, M, Y, owners, rows = data.windows(f['_steps'], f['test_runs'])
    logits = variants.numpy_logits(model, X, M, torch.device(args.device))
    prediction = port.Mx.evaluate(logits, Y, owners, threshold)
    prediction.update(threshold=threshold, checkpoint=str(existing), checkpoint_sha256=sha(existing),
                      validation_bce=measured, test_source_rows=rows)
    write(cell/'prediction.json', prediction)
    return model, prediction

def report(out):
    lines = ['# CAM-LDS full architecture results', '',
             'Recorded testbed sequences; simulated defender outcomes. No Markov generation.',
             'Dwell counts engaged commands; depth counts distinct engaged technique labels. Protection is simulated.',
             'Each row is a fold and seed. Repeated episodes are not independent campaigns.', '',
             '| Fold | Seed | Encoder | Learner | Dwell | Depth | Protection % | Actual steps |',
             '|---|---:|---|---|---:|---:|---:|---:|']
    manifest_path = out/'MANIFEST.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        settings = manifest['arguments']
        expected = len(manifest['folds'])*len(settings['arms'])*len(settings['seeds'])*len(settings['learners'])
        completed = len(list(out.glob('cells/*/*/s*/*/result.json')))
        lines[2:2] = [f'Completed RL cells: {completed}/{expected}. Order: {settings["order"]}.',
                       '**SMOKE TEST ONLY: these are not research results.**' if settings['smoke'] else 'Full/subset run as specified in MANIFEST.json.', '']
    rows = []
    for p in sorted(out.glob('cells/*/*/s*/*/result.json')):
        r = json.loads(p.read_text()); s = r['test_summary']; rows.append(r)
        lines.append(f"| {r['fold']} | {r['seed']} | {r['arm']} | {r['learner']} | {s['dwell']:.3f} | {s['depth']:.3f} | {100*s['protected']:.2f} | {r['env_steps']} |")
    lines += ['', '## Additional deception metrics (episode means)', '',
              '| Fold / seed / arm / learner | Reward | Exposed | Length | Lure chains | Dead ends | Capacity violations | Decoys deployed | Dwell with history zeroed at evaluation |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        s = r['test_summary']
        values = [s[k] for k in ('episode_reward','exposed','length','lure_chains','dead_ends','capacity_violations','decoys_deployed')]
        values.append(r['test_h0_summary']['dwell'])
        lines.append('| ' + f"{r['fold']} / {r['seed']} / {r['arm']} / {r['learner']}" + ' | ' + ' | '.join(f'{v:.3f}' for v in values) + ' |')
    lines += ['', '## Deception summary (fold means per seed, then mean +/- sample SD)', '',
              'Known-variant and unseen-scenario families are never pooled. Incomplete coverage is shown; these are descriptive, not significance tests.', '',
              '| Family | Encoder | Learner | Seeds | Cells | Dwell | Depth | Protection % |',
              '|---|---|---|---:|---:|---:|---:|---:|']
    groups = {}
    for r in rows:
        groups.setdefault((r['family'],r['arm'],r['learner']), []).append(r)
    for key, group in sorted(groups.items()):
        seeds = sorted({r['seed'] for r in group})
        cells = []
        for metric, scale in [('dwell',1),('depth',1),('protected',100)]:
            values = [np.mean([r['test_summary'][metric]*scale for r in group if r['seed']==s]) for s in seeds]
            cells.append(f'{np.mean(values):.3f} +/- {np.std(values,ddof=1):.3f}' if len(values)>1 else f'{values[0]:.3f} (one seed)')
        lines.append('| ' + ' | '.join([*key,str(len(seeds)),str(len(group)),*cells]) + ' |')
    lines += ['', '## Prediction (validation-selected checkpoint and threshold)', '',
              '| Fold | Seed | Encoder | Micro-F1 % | Macro-F1 % | Exact set % | BCE |',
              '|---|---:|---|---:|---:|---:|---:|']
    for p in sorted(out.glob('cells/*/*/s*/prediction.json')):
        r = json.loads(p.read_text()); arm, fold, seed = p.parts[-4:-1]
        lines.append(f"| {fold} | {seed} | {arm} | {100*r['micro_f1']:.2f} | {100*r['macro_f1']:.2f} | {100*r['exact_set_accuracy']:.2f} | {r['bce']:.5f} |")
    lines += ['', '## Training and validation curves', '']
    for p in sorted(out.glob('cells/*/*/s*/training.json')):
        r = json.loads(p.read_text())
        lines += [f'### {p.parent.relative_to(out)}', '', '| Update | Epoch equivalents | Training loss | Validation BCE |', '|---:|---:|---:|---:|']
        for c in r['curve']:
            lines.append(f"| {c['update']} | {c['epoch_equivalents']:.2f} | {c['train_loss_running']:.5f} | {c['validation_bce']:.5f} |")
    for r in rows:
        lines += [f"### RL {r['arm']} {r['fold']} s{r['seed']} {r['learner']}", '',
                  '| Update | Train dwell | Validation dwell | Validation depth |', '|---:|---:|---:|---:|']
        for c in r['curve']:
            lines.append(f"| {c['update']} | {c['train_dwell']:.3f} | {c['val_dwell']:.3f} | {c['val_depth']:.3f} |")
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--device', default='cpu', choices=['cpu','cuda'])
    p.add_argument('--output', type=Path, default=HERE/'results'/'main')
    p.add_argument('--encoder-root', default=str(REPO/'camlds_encoder'/'out'))
    p.add_argument('--train-missing', action='store_true')
    p.add_argument('--order', choices=['execution','frozen'], default='execution')
    p.add_argument('--audit-only', action='store_true')
    p.add_argument('--report-only', action='store_true')
    p.add_argument('--smoke', action='store_true')
    p.add_argument('--folds', nargs='+')
    p.add_argument('--arms', nargs='+', choices=ARMS, default=list(ARMS))
    p.add_argument('--seeds', nargs='+', type=int, default=list(range(10)))
    p.add_argument('--learners', nargs='+', choices=['IPPO','MAPPO'], default=['IPPO','MAPPO'])
    p.add_argument('--env-steps', type=int, default=2000000)
    p.add_argument('--eval-repeats', type=int, default=20)
    p.add_argument('--threads', type=int, default=4)
    args = p.parse_args()
    torch.set_num_threads(args.threads)
    if args.smoke:
        args.output = args.output/'smoke'
        args.train_missing = True
        args.seeds = [0]
        marl.HP.update(n_envs=2, rollout_len=4, ppo_epochs=1, n_evals=1)
        args.env_steps, args.eval_repeats = 8, 1
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    if args.report_only:
        report(out); return
    a = audit()
    a['selected_order'] = args.order
    a['hashes']['camlds_real/out/sidecar/steps_link.jsonl'] = sha(REPO/'camlds_real/out/sidecar/steps_link.jsonl')
    if args.audit_only:
        write(out/'DATA_AUDIT.json', a)
        print(json.dumps(a, indent=2)); return
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise RuntimeError('CUDA is unavailable; install a compatible GPU PyTorch build first.')
    fs = [f for f in ordered_folds(args.order) if not args.folds or f['fold'] in args.folds]
    if args.folds and set(args.folds) - {f['fold'] for f in fs}:
        raise ValueError('Unknown fold; use --audit-only and inspect split_spec')
    if args.smoke: fs = fs[:1]
    manifest = {'arguments': {k: str(v) if isinstance(v, Path) else v for k,v in vars(args).items()},
                'audit': a, 'folds': [{k:v for k,v in f.items() if k != '_steps'} for f in fs], 'hp': marl.HP}
    mp = out/'MANIFEST.json'
    if mp.exists() and json.loads(mp.read_text()) != manifest:
        raise RuntimeError('Configuration/source changed: use a new output directory.')
    write(mp, manifest)
    write(out/'DATA_AUDIT.json', a)
    lock = out/'RUNNING.lock'
    with lock.open('x') as fh: fh.write(str(os.getpid()))
    try:
        for f in fs:
            for seed in args.seeds:
                va = specs(runs(f,'val'), 100000+seed, args.eval_repeats)
                te = specs(runs(f,'test'), 200000+seed, args.eval_repeats)
                for arm in args.arms:
                    cell = out/'cells'/arm/f['fold']/f's{seed}'
                    cell.mkdir(parents=True, exist_ok=True)
                    pending = [l for l in args.learners if not (cell/l/'result.json').exists()]
                    if not pending: continue
                    print(f'Encoder: {arm} {f["fold"]} s{seed}', flush=True)
                    model, _ = encoder(arm, f, seed, args, cell)
                    for learner in pending:
                        print(f'Deception: {arm} {learner} {f["fold"]} s{seed}', flush=True)
                        result = marl.train(model, env.EnvConfig(), runs(f,'train'), va, te, seed,
                            args.env_steps, data.W, 64, learner=='MAPPO', args.device, True)
                        dest = cell/learner; dest.mkdir(parents=True, exist_ok=True)
                        torch.save(result.pop('actor_state'), dest/'actor.pt')
                        result.update(arm=arm, fold=f['fold'], learner=learner, family=f['family'])
                        write(dest/'result.json', result)
                        report(out)
    finally:
        lock.unlink(missing_ok=True)
    report(out)
    print(f'FINISHED: {out / "RESULTS.md"}')

if __name__ == '__main__':
    main()
