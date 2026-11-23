#!/usr/bin/env python3
"""Check provenance, installed dependencies, and local H-MARL checkpoint completeness.

Only stdlib required. Can run before any pip install. Does not unpickle checkpoints.
"""
import argparse
import importlib.util
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

EXPECTED_COMMIT = {
    'Hierarchical-MARL': '6fe960f5931f2d7dc5ef522f09ca4a179f377ee4',
    'cage-challenge-4': '8c3c50ca54b176c2de199847944e8dcc035497e3',
}

def git_sha(path):
    try:
        return subprocess.run(['git', '-C', str(path), 'rev-parse', 'HEAD'], capture_output=True,
                              text=True, timeout=8, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None

def flag_value(file):
    try:
        s = file.read_text(encoding='utf-8')
    except OSError:
        return None
    m = re.search(r'^\s*COMPUTE_METRICS\s*=\s*(True|False)\b', s, flags=re.M)
    return (m.group(1) == 'True') if m else None

def run_check(root, cage):
    result = {'python': platform.python_version(), 'platform': platform.platform(), 'checks': {}, 'warnings': []}
    c = result['checks']
    c['python_3_10_compatible_recommendation'] = sys.version_info[:2] == (3, 10)
    if not c['python_3_10_compatible_recommendation']:
        result['warnings'].append('Use Python 3.10 for the original ray==2.10.0 + gym/torch dependency stack.')
    for name, path in [('Hierarchical-MARL', root), ('cage-challenge-4', cage)]:
        c[f'{name}_exists'] = path.is_dir()
        sha = git_sha(path) if path.is_dir() else None
        c[f'{name}_git_sha'] = sha
        c[f'{name}_pinned_commit'] = (sha == EXPECTED_COMMIT[name])
        if sha and not c[f'{name}_pinned_commit']:
            result['warnings'].append(f'{name}: commit differs from pinned {EXPECTED_COMMIT[name]}')
    for module in ['CybORG', 'ray', 'torch', 'gym', 'numpy']:
        try:
            c[f'module_{module}'] = importlib.util.find_spec(module) is not None
        except (ModuleNotFoundError, ValueError):
            c[f'module_{module}'] = False
    try:
        from importlib.metadata import version
        c['ray_version'] = version('ray')
    except Exception:
        c['ray_version'] = None
    c['ray_2_10_0'] = c['ray_version'] == '2.10.0'
    sub = root / 'h-marl-3policy' / 'saved_policies' / 'sub' / 'iter_49' / 'policies'
    master = root / 'h-marl-3policy' / 'saved_policies' / 'master' / 'iter_49' / 'policies'
    missing = []
    for i in range(5):
        for role in ['investigate', 'recover']:
            path = sub / f'Agent{i}_{role}' / 'policy_state.pkl'
            if not path.is_file() or path.stat().st_size < 1000: missing.append(str(path))
        path = master / f'Agent{i}_master' / 'policy_state.pkl'
        if not path.is_file() or path.stat().st_size < 1000: missing.append(str(path))
    c['checkpoint_policy_files_found'] = 15 - len(missing)
    c['checkpoint_policy_files_expected'] = 15
    c['checkpoint_files_complete'] = not missing
    c['missing_policy_files'] = missing
    for policy in ['subpolicies','master']:
        file = root / 'h-marl-3policy' / policy / 'BlueFlatWrapper_CC4.py'
        c[f'{policy}_COMPUTE_METRICS'] = flag_value(file)
    c['metric_flags_enabled'] = all(c[f'{p}_COMPUTE_METRICS'] is True for p in ['subpolicies', 'master'])
    c['evaluation_scripts_present'] = all((root / 'h-marl-3policy'/ p / 'evaluation_metrics.py').is_file()
                                           for p in ['subpolicies','master'])
    result['ready_for_100_episode_metrics_run'] = bool(
        c['Hierarchical-MARL_exists'] and c['cage-challenge-4_exists']
        and c['checkpoint_files_complete'] and c['evaluation_scripts_present']
        and c['metric_flags_enabled'] and c['module_CybORG']
        and c['module_ray'] and c['ray_2_10_0']
    )
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, default=Path('sources/Hierarchical-MARL'))
    p.add_argument('--cage', type=Path, default=Path('sources/cage-challenge-4'))
    p.add_argument('--out', type=Path, default=Path('results/preflight.json'))
    args = p.parse_args()
    report = run_check(args.repo.resolve(), args.cage.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    sys.exit(0 if report['ready_for_100_episode_metrics_run'] else 2)

if __name__ == '__main__': main()
