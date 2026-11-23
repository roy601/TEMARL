#!/usr/bin/env python3
"""Create human-readable Table 2 and held-out Table 4 from independent CSVs.
No numbers are hardcoded to force matches. Re-running this overwrites only tables/.
"""
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[1]
METRICS=['utility','redirection_precision','engagement_rate','benign_false_redirect_rate','unsafe_action_rate','normalized_cost']
LABELS=['Defensive utility','Redirection precision','Engagement rate','Benign false redirects','Unsafe actions','Normalized cost']
POLICIES=['Static','Adaptive','Consensus','CADO']

def read(path):
    with path.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def write(path,rows,keys):
    path.parent.mkdir(exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def main():
    out=ROOT/'tables'
    summary=read(ROOT/'independent_results/reproduced_results/summary_statistics.csv')
    primary={ (r['policy'],r['metric']):r for r in summary if r['dataset']=='primary'}
    rowlist=[]
    for metric,label in zip(METRICS,LABELS):
        row={'metric':label,'metric_key':metric}
        for policy in POLICIES:
            value=primary[(policy,metric)]
            for k in ['mean','ci_low','ci_high']:
                row[f'{policy}_{k}']=value[k]
        rowlist.append(row)
    keys=['metric','metric_key']+[f'{p}_{k}' for p in POLICIES for k in ['mean','ci_low','ci_high']]
    write(out/'table2_primary_independently_reproduced.csv',rowlist,keys)
    paired=read(ROOT/'independent_results/revision_results/heldout_paired_statistical_comparisons.csv')
    held=read(ROOT/'independent_results/revision_results/heldout_summary_statistics.csv')
    hmap={(r['policy'],r['metric']):r for r in held}
    pmap={r['metric']:r for r in paired if r['comparison']=='CADO - Consensus'}
    table4=[]
    for metric,label in zip(METRICS,LABELS):
        r={'metric':label,'metric_key':metric}
        for policy in ['Consensus','CADO']:
            q=hmap[(policy,metric)]
            for k in ['mean','ci_low','ci_high']:
                r[f'{policy}_{k}']=q[k]
        q=pmap[metric]
        for k in ['mean_difference','ci_low','ci_high','p_raw','p_holm','effect_size_dz','n_paired_seeds']:
            r[f'paired_{k}']=q[k]
        table4.append(r)
    keys=['metric','metric_key']+[f'{p}_{k}' for p in ['Consensus','CADO'] for k in ['mean','ci_low','ci_high']]+[
        f'paired_{k}' for k in ['mean_difference','ci_low','ci_high','p_raw','p_holm','effect_size_dz','n_paired_seeds']]
    write(out/'table4_heldout_independently_reproduced.csv',table4,keys)

    def fmt(x,p=4): return f'{float(x):.{p}f}'
    report=['# Independently reproduced CADO results', '',
     'Source: the user-uploaded CADO official supplementary archive; original simulation and revision-analysis scripts executed here.',
     '', '## Main manuscript Table 2 — primary evaluation',
     '', '| Metric | Static | Adaptive | Consensus | CADO |', '|---|---:|---:|---:|---:|']
    for row in rowlist:
        report.append('| '+row['metric']+' | '+' | '.join(fmt(row[f'{p}_mean']) for p in POLICIES)+' |')
    report+=['','Values are means across 30 paired seeds. Exact bootstrap CI endpoints appear in the CSV.',
    '', '## Held-out attacker table (Table 4 in manuscript discussion)',
    '', '| Metric | Consensus | CADO | CADO minus Consensus | Holm adjusted p |',
    '|---|---:|---:|---:|---:|']
    for row in table4:
        report.append('| '+row['metric']+' | '+fmt(row['Consensus_mean'])+' | '+fmt(row['CADO_mean'])+' | '+fmt(row['paired_mean_difference'],6)+' | '+fmt(row['paired_p_holm'],6)+' |')
    report+=['','Comparison uses the same 30 paired seeds and the author-provided 10,000-resample convention.',
    '', '**Scope:** generated synthetic events, not real network traffic. Model is deterministic/constraint-aware, not a trained neural or MARL policy.',
    '', '**Limitations:** host-dependent timing excluded; the separate primary `paired_statistical_comparisons.csv` differs in two p-value rows under this environment (see evidence/independent_scientific_comparison.json). The held-out paired table above matches its archived counterpart.',
    '']
    (out/'REPRODUCED_TABLES.md').write_text('\n'.join(report),encoding='utf-8')
    print('Exported',len(rowlist),'primary metrics and',len(table4),'held-out metrics')

if __name__=='__main__':main()
