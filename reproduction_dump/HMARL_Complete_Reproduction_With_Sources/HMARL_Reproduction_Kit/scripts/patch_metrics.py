#!/usr/bin/env python3
"""Make a minimal, reversible change from False to True in authors' metric wrappers."""
import argparse
import difflib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

def patch(path, dry_run=False):
    before = path.read_text(encoding='utf-8')
    pat = re.compile(r'^(COMPUTE_METRICS\s*=\s*)False\b', flags=re.M)
    after, n = pat.subn(r'\g<1>True', before)
    if n != 1:
        if re.search(r'^COMPUTE_METRICS\s*=\s*True\b', before, re.M):
            return {'path': str(path), 'change': 'already_enabled', 'backup': None}
        raise ValueError(f'{path}: expected exactly one False setting; found {n}')
    if dry_run:
        return {'path': str(path), 'change':'would_enable', 'backup':None,
                'diff':''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                      fromfile=str(path)+'.original',tofile=str(path)+'.updated'))}
    backup = path.with_suffix(path.suffix + '.original.bak')
    if backup.exists() and backup.read_text(encoding='utf-8') != before:
        raise RuntimeError(f'Backup exists but is not identical to current original: {backup}')
    if not backup.exists(): backup.write_text(before, encoding='utf-8')
    path.write_text(after, encoding='utf-8')
    return {'path': str(path), 'change': 'enabled', 'backup': str(backup)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, default=Path('sources/Hierarchical-MARL'))
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--out',type=Path, default=Path('results/metrics_patch.json'))
    a=p.parse_args()
    files=[a.repo/'h-marl-3policy'/x/'BlueFlatWrapper_CC4.py' for x in ('subpolicies','master')]
    result={'utc':datetime.now(timezone.utc).isoformat(),'dry_run':a.dry_run,'changes':[patch(x, a.dry_run) for x in files]}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
