"""Re-run every submitted experiment and compare scientific (not timing) outputs.

This independent verification does not replace the archived submitted results.
Usage: python code/reproduce_submitted.py
"""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import run_experiments as sim

ROOT=Path(__file__).resolve().parents[1]
sim.RESULTS=ROOT/'reproduced_results';sim.RESULTS.mkdir(exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--verify-only', action='store_true', help='Compare an already completed rerun.')
args = parser.parse_args()
if not args.verify_only:
    sim.write_config()
    print('Reproducing primary policies ...',flush=True)
    primary=sim.run_primary()
    print('Reproducing held-out policies ...',flush=True)
    ood=sim.run_ood()
    print('Reproducing fault simulation ...',flush=True)
    faults=sim.run_fault_injection()
    print('Reproducing gate ablations ...',flush=True)
    sim.run_ablation()
    print('Reproducing normalization ...',flush=True)
    sim.run_normalization_benchmark()
    print('Reproducing statistics ...',flush=True)
    sim.summarize_and_test(primary,ood,faults)
reports=[]
for new in sorted(sim.RESULTS.glob('*.csv')):
    old=ROOT/'submitted_results'/new.name
    if not old.exists():continue
    a,b=pd.read_csv(old),pd.read_csv(new)
    assert a.shape==b.shape,(new.name,a.shape,b.shape)
    excludes=[c for c in a if any(k in c.lower() for k in ['latency','throughput','elapsed','records_s'])]
    if new.name=='normalization_benchmark.csv':
        compares=[c for c in a if c not in excludes and not any(k in c for k in ['_us','_ms','seconds'])]
    else: compares=[c for c in a if c not in excludes]
    excludes = [c for c in a if c not in compares]
    maxima={}
    for col in compares:
        if pd.api.types.is_bool_dtype(a[col]):
            assert a[col].equals(b[col]), (new.name,col)
        elif pd.api.types.is_numeric_dtype(a[col]):
            av,bv=a[col].to_numpy(),b[col].to_numpy()
            assert np.allclose(av,bv,atol=1e-12,rtol=0,equal_nan=True),(new.name,col)
            diff=np.abs(av-bv);maxima[col]=float(np.nanmax(diff)) if np.isfinite(diff).any() else 0.
        else:assert a[col].fillna('').equals(b[col].fillna('')),(new.name,col)
    reports.append({'file':new.name,'rows':len(a),'excluded_host_timing_columns':excludes,'maximum_errors':maxima})
expected = {p.name for p in (ROOT/'submitted_results').glob('*.csv')}
assert {r['file'] for r in reports} == expected, 'Incomplete reproduction output'
old_config = json.loads((ROOT/'submitted_results/experiment_config.json').read_text())
new_config = json.loads((sim.RESULTS/'experiment_config.json').read_text())
environment_keys = {'python', 'platform', 'numpy', 'pandas', 'matplotlib'}
assert {k:v for k,v in old_config.items() if k not in environment_keys} == {k:v for k,v in new_config.items() if k not in environment_keys}, 'Scientific configuration differs'
result={'all_compared_scientific_values_reproduced':True,'absolute_tolerance':1e-12,'reports':reports,
        'scientific_configuration_matches':True,
        'environment_comparison':{k:{'submitted':old_config[k],'rerun':new_config[k]} for k in sorted(environment_keys)}}
(ROOT/'revision_results/full_reproduction_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('All scientific outputs match the submitted archive; timing is excluded.',flush=True)
