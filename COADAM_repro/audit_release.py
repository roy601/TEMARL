"""Recompute historical release statistics. Never called as fresh evaluation."""
import csv
from collections import defaultdict
from pathlib import Path
import numpy as np
from report_results import ROOT, extract

def main():
    rows=extract(ROOT/'upstream/results/baseline_results_final.mat')
    grouped=defaultdict(list)
    for row in rows: grouped[row['table'],row['method'],row['metric']].append(row['value'])
    with (ROOT/'paper_targets.csv').open() as handle: targets=list(csv.DictReader(handle))
    lines=['# Historical release audit — NOT new experiment results','',
        'Source: upstream/results/baseline_results_final.mat. Means and sample SDs below are recomputed from the saved raw episode arrays. These files are never used to populate a fresh run.', '',
        '| Table | Method | Metric | Episodes | Archived mean | Published mean | Difference | Archived SD | Published SD |',
        '|---:|---|---|---:|---:|---:|---:|---:|---:|']
    for target in targets:
        for metric in ('AMR','InfectionRate','CumulativeReward','DSR'):
            ref=target[metric+'_mean']
            if not ref: continue
            raw=grouped[int(target['table']),target['method'],metric]
            sd=target[metric+'_std']
            lines.append(f"| {target['table']} | {target['method']} | {metric} | {len(raw)} | {np.mean(raw):.6f} | {ref} | {np.mean(raw)-float(ref):+.6f} | {np.std(raw,ddof=1):.6f} | {sd} |")
    lines += ['', 'These discrepancies and the 100-episode archive do not establish which exact configuration produced the published 200-episode tables. Similar means do not resolve missing provenance.']
    (ROOT/'ARCHIVE_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__': main()
