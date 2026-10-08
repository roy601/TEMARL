"""Scenario metadata for exact replay. No generative transition model."""
import json
from functools import lru_cache
from pathlib import Path
import numpy as np
import _frozen
from env_v2 import DEFENDED_ZONES, ZONES
from vocab_v2 import NUM_TECHNIQUES, TACTIC_ORDER, tactic_of
from replay_data import records


def verified_runs():
    out = {}
    for r in records().values():
        out.setdefault(r['scenario'], []).append(list(r['ids']))
    return out


@lru_cache(None)
def scripts():
    metadata = json.loads((Path(_frozen.DATA_DIR) / 'camlds_grounding.json').read_text())
    runs = verified_runs()
    out = {}
    for row in metadata['scenarios']:
        sid = row['id']
        entry = ZONES.index(row['entry_zone'])
        target = ZONES.index(row['target_zone']) if row['target_zone'] in ZONES else entry
        if target not in DEFENDED_ZONES:
            target = entry
        declared = row['terminal_tactic'].strip()
        if '(' in declared and ')' in declared:
            declared = declared[declared.index('(')+1:declared.index(')')]
        declared = declared.split('/')[0].strip()
        if declared not in TACTIC_ORDER:
            raise ValueError(declared)
        goal = 'Collection' if sid == 'S6' and declared == 'Exfiltration' else declared
        goal_ids = [j for j in range(NUM_TECHNIQUES) if tactic_of(j) == goal]
        out[sid] = dict(id=sid, name=row['name'], entry=entry, target=target,
                        target_raw=row['target_zone'], goal_tactic=goal,
                        goal_declared=declared,
                        goal_rule='declared' if goal == declared else 'fallback: Exfiltration unobserved -> Collection',
                        goal_ids=goal_ids, goal_mask=np.isin(np.arange(NUM_TECHNIQUES), goal_ids),
                        horizons=sorted(map(len, runs[sid])), n_runs=len(runs[sid]))
    return out


def script_ids():
    return sorted(scripts())


def max_horizon():
    return max(len(r['ids']) for r in records().values())


def loso_folds():
    """Legacy metadata helper only; LOSO is not an enabled experiment protocol."""
    return [{'held_out': s, 'train': [t for t in script_ids() if t != s]}
            for s in script_ids()]
