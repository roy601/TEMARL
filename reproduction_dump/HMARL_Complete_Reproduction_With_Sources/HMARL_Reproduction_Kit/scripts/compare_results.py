#!/usr/bin/env python3
"""Compare ORIGINAL generated summaries with Table 3; never treat reference CSV as measured evidence.

Authors' summary.json records reward, not all nine Table 3 metrics. Other metrics
must be extracted/verified from the evaluator's console log and independently
recorded in measured_metrics.csv to qualify for full Table 3 cell comparison.
"""
import argparse
import csv
import json
import math
import sys
from pathlib import Path

COLUMNS=['clean_hosts_ratio','non_escalated_hosts_ratio','mean_time_to_recover','useful_recoveries',
         'wasted_recoveries','recovery_precision','recovery_error','red_impact_count','reward']
ALIASES={'expert':'H-MARL Expert','meta':'H-MARL Meta'}

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as handle:
        rows=list(csv.DictReader(handle))
    return {r['strategy']:r for r in rows}

def summarize(args):
    ref=read_csv(args.reference)
    measurements={}
    rows=[]
    for slug,strategy in ALIASES.items():
        summary=args.results/slug/'summary.json'
        if summary.exists():
            obj=json.loads(summary.read_text(encoding='utf-8'))
            eps=obj.get('parameters',{}).get('max_episodes')
            val=obj['reward']['mean']
            measurements[slug]={'reward':float(val),'episodes':eps,'source':str(summary),'kind':'ORIGINAL_SIMULATION'}
            instrumented=args.results/slug/'table3_instrumented.json'
            if instrumented.exists():
                inst=json.loads(instrumented.read_text(encoding='utf-8'))
                if inst.get('episode_count') != eps:
                    raise ValueError(f'{slug}: instrumented episode count disagrees with original summary.json')
                if not math.isclose(float(inst['reward']),float(val),abs_tol=1e-6):
                    raise ValueError(f'{slug}: instrumented reward disagrees with original summary.json')
                for col in COLUMNS:
                    if inst.get(col) is not None:
                        measurements[slug][col]=float(inst[col])
                measurements[slug]['metrics_source']=str(instrumented)
                measurements[slug]['metrics_kind']='INSTRUMENTED_ORIGINAL_SIMULATION'
    if args.measured_metrics and args.measured_metrics.exists():
        for name,row in read_csv(args.measured_metrics).items():
            for slug,target in ALIASES.items():
                if target!=name:continue
                measurements.setdefault(slug,{})
                for col in COLUMNS:
                    if row.get(col):
                        value=float(row[col]);
                        if col=='reward' and 'reward' in measurements[slug] and not math.isclose(value,measurements[slug]['reward'],abs_tol=0.01):
                            raise ValueError(f'{name} independently supplied reward conflicts with original summary.json')
                        measurements[slug][col]=value
                measurements[slug]['metrics_source']=str(args.measured_metrics)
    for slug,strategy in ALIASES.items():
        measured=measurements.get(slug,{})
        for col in COLUMNS:
            published=float(ref[strategy][col]); got=measured.get(col)
            rows.append({'strategy':strategy,'metric':col,'published':published,
                         'measured':got,'delta':round(got-published,6) if got is not None else None,
                         'status':'NOT_MEASURED' if got is None else 'MEASURED_NOT_EXACT' if abs(got-published)>args.abs_tolerance else 'CLOSE_BY_TOLERANCE',
                         'source':measured.get('source') if col=='reward' else measured.get('metrics_source')})
    complete=all(x['measured'] is not None for x in rows)
    eps_ok=all(measurements.get(x,{}).get('episodes')==100 for x in ALIASES)
    reward_from_original=all(measurements.get(x,{}).get('kind')=='ORIGINAL_SIMULATION' for x in ALIASES)
    close=all(x['status']=='CLOSE_BY_TOLERANCE' for x in rows)
    # Narrow distinction: user-supplied manual metric file must contain a documented method before claiming full.
    verdict = 'NOT_EXECUTED' if not reward_from_original else 'PARTIAL_REPRODUCTION'
    validated_instrumented=all(measurements.get(x,{}).get('metrics_kind')=='INSTRUMENTED_ORIGINAL_SIMULATION' for x in ALIASES)
    if complete and eps_ok and close and reward_from_original and validated_instrumented:
        verdict = 'TABLE3_NUMERICALLY_CLOSE_INSTRUMENTED_REPRODUCTION_NEEDS_INDEPENDENT_AUDIT'
    elif complete and eps_ok and reward_from_original and validated_instrumented:
        verdict = 'TABLE3_INSTRUMENTED_RUN_NOT_CLOSE_TO_PUBLISHED'
    elif complete and eps_ok and close and reward_from_original:
        verdict = 'NUMERIC_TABLE3_CLOSE_MANUAL_METRICS_REQUIRE_INDEPENDENT_AUDIT'
    experimental_reduction=None
    if validated_instrumented and eps_ok and reward_from_original:
        ex=measurements['expert'].get('red_impact_count'); me=measurements['meta'].get('red_impact_count')
        if ex is not None and me is not None and me>0:
            experimental_reduction=round((me-ex)/me*100,2)
    result={'status':verdict,'max_absolute_tolerance':args.abs_tolerance,
            'episode_count_verification':eps_ok,'original_reward_summaries_present':reward_from_original,
            'all_18_table3_cells_measured':complete,'instrumented_metrics_available_for_both':validated_instrumented,
            'experimental_red_impact_reduction_percent':experimental_reduction,
            'published_red_impact_reduction_percent':round((1.14-0.88)/1.14*100,2),
            'notes':[
            'Published table values are reference data and are never treated as simulation output.',
            'Authors summary.json saves reward only; other metrics need verified computation/recording.',
            'Equality within a numeric tolerance does not alone establish exact stochastic reproduction.',
            'Instrumented result fields use authors in-memory arrays; their aggregation definitions need independent auditing.',
            'Manual measured_metrics.csv is not independently authenticated by this script.'
            ],'comparison':rows}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reference',type=Path,default=Path('paper_reference/table3_published.csv'))
    p.add_argument('--results',type=Path,default=Path('results'))
    p.add_argument('--measured-metrics',type=Path)
    p.add_argument('--abs-tolerance',type=float,default=0.01)
    a=p.parse_args()
    r=summarize(a)
    a.results.mkdir(parents=True,exist_ok=True)
    out=a.results/'comparison.json'
    out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    md=['# Table 3 reproduction comparison','',f'**Status: {r["status"]}**','',
        'The following published numbers are not reproduced outcomes. Values appear in the measured column only when a local evaluator produced them or they were entered in an explicit independent-metrics file.','',
        '| Strategy | Metric | Published | Measured | Delta | Evidence status |',
        '|---|---|---:|---:|---:|---|']
    for x in r['comparison']:
        fmt=lambda z: '—' if z is None else str(z)
        md.append('| '+ ' | '.join(fmt(x[q]) for q in ['strategy','metric','published','measured','delta','status'])+' |')
    md+=['','The runner cannot certify the paper as fully reproduced just by consuming this comparison file.']
    (a.results/'comparison.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    print(r['status']); return 0

if __name__=='__main__':sys.exit(main())
