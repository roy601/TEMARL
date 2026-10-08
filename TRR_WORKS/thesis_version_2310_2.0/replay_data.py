"""Exact source-label replay and deterministic, duplicate-grouped run splits."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import _frozen
from env_v2 import technique_to_id
from vocab_v2 import NUM_TECHNIQUES

ROOT = Path(__file__).resolve().parent
SPLIT_SEED = 2310


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


@lru_cache(None)
def records():
    data = json.loads((Path(_frozen.DATA_DIR) / 'camlds_grounding_verified.json').read_text())
    out = {}
    for key, row in sorted(data['runs'].items()):
        labels = tuple(row['sequence'])
        ids = tuple(technique_to_id(t) for t in labels)
        if not labels or any(not 0 <= t < NUM_TECHNIQUES for t in ids):
            raise ValueError(f'Empty or unknown sequence: {key}')
        out[key] = dict(run_id=key, scenario=row['scenario'], labels=labels, ids=ids,
                        raw_hash=digest(labels), model_hash=digest(ids))
    return out


@lru_cache(None)
def split_manifest():
    # Group at the model-visible resolution too: sub-technique differences must
    # not leak identical parent-ID sequences across splits.
    groups = {}
    for key, r in records().items():
        groups.setdefault(r['model_hash'], []).append(key)
    by_scenario = {}
    for h, keys in groups.items():
        scenarios = tuple(sorted({records()[k]['scenario'] for k in keys}))
        by_scenario.setdefault(scenarios, []).append(h)
    assignment = {}
    for scenarios, hashes in sorted(by_scenario.items()):
        hashes.sort(key=lambda h: digest([SPLIT_SEED, h]))
        # Small strata cannot populate three disjoint splits. Singletons stay
        # in training; two-group strata get train/test, without fabricated runs.
        n = len(hashes)
        nv = max(1, int(n * .2)) if n >= 3 else 0
        nt = max(1, int(n * .2)) if n >= 2 else 0
        for i, h in enumerate(hashes):
            split = 'validation' if i < nv else ('test' if i < nv + nt else 'train')
            for key in groups[h]:
                assignment[key] = split
    return dict(protocol='parent-sequence-grouped variant holdout', split_seed=SPLIT_SEED,
                assignments=assignment,
                records={k: {n: r[n] for n in ('scenario','raw_hash','model_hash')}
                         for k, r in records().items()})


def run_ids(split='train', scenarios=None):
    if split not in ('train', 'validation', 'test', 'all'):
        raise ValueError(f'Unknown split {split}')
    assignment = split_manifest()['assignments']
    keys = [k for k, r in records().items()
            if (split == 'all' or assignment[k] == split)
            and (scenarios is None or r['scenario'] in scenarios)]
    if not keys:
        raise ValueError(f'No playbooks in {split} for {scenarios}')
    return keys


def audit():
    from difflib import SequenceMatcher
    from parse_attackbed import parse_playbook
    source = ROOT / 'source_attackbed' / 'ansible' / 'run'
    if not source.is_dir():
        raise ValueError('Bundled official playbook sources are missing')
    parsed = {}
    source_hashes = {}
    for p in sorted(source.rglob('scenario_*.j2*')):
        seq = tuple(x[0] for x in parse_playbook(p))
        if seq:
            if p.name in parsed:
                raise ValueError(f'Ambiguous source basename: {p.name}')
            parsed[p.name] = seq
            source_hashes[p.relative_to(ROOT).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    for key, r in records().items():
        if parsed.get(key) != r['labels']:
            raise ValueError(f'Official source/verified JSON mismatch: {key}')
    aliases = {}
    for key in sorted(set(parsed) - set(records())):
        matches = [k for k, r in records().items() if parsed[key] == r['labels']]
        if not matches:
            raise ValueError(f'Unaccounted source playbook: {key}')
        aliases[key] = matches
    splits = {s: run_ids(s) for s in ('train','validation','test')}
    overlap = []
    for a, b in (('train','validation'), ('train','test'), ('validation','test')):
        if {records()[k]['model_hash'] for k in splits[a]} & {records()[k]['model_hash'] for k in splits[b]}:
            raise ValueError('Duplicate leakage')
        best = max((SequenceMatcher(None, records()[x]['ids'], records()[y]['ids'],
                                    autojunk=False).ratio(), x, y)
                   for x in splits[a] for y in splits[b])
        overlap.append(dict(splits=[a,b], max_sequence_similarity=best[0], runs=list(best[1:])))
    train_labels = {t for k in splits['train'] for t in records()[k]['ids']}
    support = {}
    for split in ('validation','test'):
        tokens = [t for k in splits[split] for t in records()[k]['ids'][1:]]
        support[split] = dict(prediction_targets=len(tokens),
                              targets_unseen_in_training=sum(t not in train_labels for t in tokens))
    return dict(source_verified=True, runs=len(records()), unknown_tokens=0,
                upstream_url='https://github.com/ait-testbed/attackbed',
                source_commit='4d43354115019427e74b8df5f2c3237cd7c38e3d',
                source_sha256=source_hashes, held_out_label_support=support,
                labelled_steps=sum(len(r['ids']) for r in records().values()),
                unique_parent_sequences=len({r['model_hash'] for r in records().values()}),
                duplicate_source_aliases=aliases, split_counts={s: len(v) for s,v in splits.items()},
                scenario_coverage={s: sorted({records()[k]['scenario'] for k in v}) for s,v in splits.items()},
                similarity=overlap, manifest=split_manifest())


if __name__ == '__main__':
    result = audit()
    (ROOT / 'REPLAY_DATA_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'manifest'}, indent=2))
