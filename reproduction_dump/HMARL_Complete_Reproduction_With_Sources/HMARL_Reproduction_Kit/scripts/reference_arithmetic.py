#!/usr/bin/env python3
"""Compute ONLY arithmetic changes between rows of PUBLISHED Table 3."""
from pathlib import Path
import csv
import json
import sys

def calculate(path):
    with open(path,newline='',encoding='utf-8') as f:
        rows={r['strategy']:r for r in csv.DictReader(f)}
    a,b,c=(rows[key] for key in ['H-MARL Expert','H-MARL Meta','MARL Decentralized'])
    def reduction(baseline, improved, metric):
        before=float(baseline[metric]); after=float(improved[metric]);return {
         'baseline':before,'new':after,'absolute_reduction':round(before-after,4),
         'relative_reduction_percent':round((before-after)/before*100,2)}
    return {'source':'PUBLISHED TABLE 3 VALUES ONLY, NOT AN INDEPENDENT SIMULATION',
            'red_impact_expert_vs_meta':reduction(b,a,'red_impact_count'),
            'red_impact_expert_vs_decentralized':reduction(c,a,'red_impact_count'),
            'wasted_recoveries_expert_vs_decentralized':reduction(c,a,'wasted_recoveries'),
            'wasted_recoveries_expert_vs_meta':reduction(b,a,'wasted_recoveries')}
if __name__=='__main__':
    source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('paper_reference/table3_published.csv')
    report=calculate(source)
    output=Path('results/published_arithmetic.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
