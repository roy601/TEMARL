#!/usr/bin/env python3
"""Independently check CADO reproducibility evidence, without altering scientific data.

Reads the user-supplied publisher source and independently generated outputs.
It deliberately accepts host-specific timing drift and reports (never masks) other
numeric differences. Requires numpy/pandas, as does the author's package.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

METRICS = ['utility', 'redirection_precision', 'engagement_rate',
           'benign_false_redirect_rate', 'unsafe_action_rate', 'normalized_cost']
PRIMARY_FILES = ['primary_episode_metrics.csv', 'ood_episode_metrics.csv',
                 'primary_seed_summary.csv', 'ood_seed_summary.csv',
                 'summary_statistics.csv', 'ablation_episode_metrics.csv',
                 'ablation_seed_summary.csv', 'ablation_summary.csv',
                 'fault_injection_metrics.csv', 'normalization_benchmark.csv',
                 'paired_statistical_comparisons.csv']
REVISION_FILES = ['primary_heldout_consensus_paired.csv',
                  'heldout_summary_statistics.csv',
                  'heldout_paired_statistical_comparisons.csv',
                  'default_episode_reanalysis.csv',
                  'sensitivity_seed_metrics.csv',
                  'sensitivity_paired_comparisons.csv']


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def publisher_hash_check(src: Path):
    rows = []
    for line in (src / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        digest, relative_path = line.split('  ', 1)
        candidate = (src / relative_path).resolve()
        if not candidate.is_relative_to(src.resolve()):
            rows.append({'path': relative_path, 'status': 'UNSAFE_PATH'})
        elif not candidate.exists():
            rows.append({'path': relative_path, 'status': 'MISSING'})
        elif sha256(candidate) == digest:
            rows.append({'path': relative_path, 'status': 'MATCH'})
        else:
            rows.append({'path': relative_path, 'status': 'HASH_MISMATCH'})
    return {'declared': len(rows),
            'matched': sum(r['status'] == 'MATCH' for r in rows),
            'missing': [r['path'] for r in rows if r['status'] == 'MISSING'],
            'mismatched': [r['path'] for r in rows if r['status'] == 'HASH_MISMATCH'],
            'entries': rows}


def compare_csv(old: Path, new: Path, atol: float=1e-12):
    if not old.exists() or not new.exists():
        return {'file': old.name, 'status': 'MISSING', 'old_exists': old.exists(), 'new_exists': new.exists()}
    a, b = pd.read_csv(old), pd.read_csv(new)
    entry = {'file': old.name, 'archived_rows': len(a), 'rerun_rows': len(b),
             'excluded_host_timing_columns': [], 'failed_columns': [], 'max_scientific_abs_error': 0.,
             'per_column_differences': []}
    if list(a.columns) != list(b.columns) or a.shape != b.shape:
        entry['status'] = 'STRUCTURE_MISMATCH'
        entry['columns_original'] = list(a.columns)
        entry['columns_new'] = list(b.columns)
        return entry
    for col in a.columns:
        lower = col.lower()
        if any(marker in lower for marker in ['latency', 'throughput', 'elapsed', 'records_s']) or (
            old.name == 'normalization_benchmark.csv' and any(z in lower for z in ['_us', '_ms', 'seconds'])
        ):
            entry['excluded_host_timing_columns'].append(col)
            continue
        if pd.api.types.is_bool_dtype(a[col]):
            matches = a[col].equals(b[col])
            abs_err = 0.
        elif pd.api.types.is_numeric_dtype(a[col]):
            av, bv = a[col].to_numpy(), b[col].to_numpy()
            matches = bool(np.allclose(av, bv, atol=atol, rtol=0, equal_nan=True))
            delta = np.abs(av.astype(float) - bv.astype(float))
            abs_err = float(np.nanmax(delta)) if np.isfinite(delta).any() else 0.
        else:
            matches = a[col].fillna('').equals(b[col].fillna(''))
            abs_err = 0.
        entry['max_scientific_abs_error'] = max(entry['max_scientific_abs_error'], abs_err)
        if not matches:
            entry['failed_columns'].append(col)
            entry['per_column_differences'].append({'column': col, 'max_abs_error': abs_err})
    entry['status'] = 'PASS' if not entry['failed_columns'] else 'NUMERIC_DIFFERENCES'
    return entry


def audit(root: Path, independent_root: Path | None = None):
    root = root.resolve()
    src = root / 'publisher_source'
    target = independent_root.resolve() if independent_root else root / 'independent_results'
    sub = [compare_csv(src / 'submitted_results' / fn, target / 'reproduced_results' / fn)
           for fn in PRIMARY_FILES]
    rev = [compare_csv(src / 'revision_results' / fn, target / 'revision_results' / fn)
           for fn in REVISION_FILES]
    target_tables = ['primary_episode_metrics.csv', 'ood_episode_metrics.csv',
                     'primary_seed_summary.csv', 'ood_seed_summary.csv', 'summary_statistics.csv']
    table2_ok = all(x['status'] == 'PASS' for x in sub if x['file'] in ['primary_episode_metrics.csv', 'primary_seed_summary.csv', 'summary_statistics.csv'])
    table4_ok = all(x['status'] == 'PASS' for x in sub if x['file'] in ['ood_episode_metrics.csv', 'ood_seed_summary.csv']) and \
        all(x['status'] == 'PASS' for x in rev if x['file'] in ['primary_heldout_consensus_paired.csv', 'heldout_summary_statistics.csv', 'heldout_paired_statistical_comparisons.csv'])
    metadata = {'root': str(root), 'independent_root': str(target),
                'published_reference': 'https://doi.org/10.3390/fi18100552',
                'supplement_url': 'https://www.mdpi.com/article/10.3390/fi18100552/s1',
                'source_archive_sha256': sha256(root/'original_archive/futureinternet-18-00552-s001.zip'),
                'publisher_manifest': publisher_hash_check(src),
                'scientific_tolerance': 1e-12,
                'main_scientific_csv_comparisons': sub,
                'revision_csv_comparisons': rev,
                'table2_reproduced': table2_ok,
                'table4_heldout_reproduced': table4_ok,
                'all_original_submitted_csv_agree_to_tolerance': all(x['status']=='PASS' for x in sub),
                'non_timing_differences': [dict(file=x['file'], failed_columns=x.get('failed_columns'),
                                                errors=x.get('per_column_differences'))
                                           for x in sub+rev if x['status'] not in ('PASS',)]}
    return metadata


def main():
    parser = argparse.ArgumentParser(description='Verify CADO independently reproduced Tables 2 and 4.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--independent-root', type=Path, default=None)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    report = audit(args.root, args.independent_root)
    result = {'table2_reproduced': report['table2_reproduced'],
              'table4_heldout_reproduced': report['table4_heldout_reproduced'],
              'all_submitted_csv_agree': report['all_original_submitted_csv_agree_to_tolerance'],
              'original_manifest_matched': report['publisher_manifest']['matched'],
              'original_manifest_missing': report['publisher_manifest']['missing'],
              'scientific_differences': report['non_timing_differences']}
    print(json.dumps(result, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    if not (report['table2_reproduced'] and report['table4_heldout_reproduced']):
        raise SystemExit(1)

if __name__ == '__main__':
    main()
