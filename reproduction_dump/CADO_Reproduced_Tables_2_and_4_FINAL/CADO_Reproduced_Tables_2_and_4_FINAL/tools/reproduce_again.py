#!/usr/bin/env python3
"""Regenerate CADO published Tables 2 and 4 using archived simulator files.

This creates a NEW working directory and never changes publisher_source.
Run: python tools/reproduce_again.py --output local_rerun [--full] [--prototype]
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def call(*args, cwd):
    print('\n> '+' '.join(str(x) for x in args), flush=True)
    subprocess.run([str(x) for x in args],cwd=cwd,check=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('local_rerun'))
    parser.add_argument('--full',action='store_true',help='also regenerate ablations and normalization benchmarks')
    parser.add_argument('--prototype',action='store_true',help='run loopback HTTP prototype trials')
    args=parser.parse_args()
    work=args.output.resolve()
    if work.exists():
        raise SystemExit(f'Output directory already exists, refusing to overwrite: {work}')
    shutil.copytree(ROOT/'publisher_source',work)
    code='''from pathlib import Path
import run_experiments as sim
sim.RESULTS=Path('reproduced_results')
sim.RESULTS.mkdir(exist_ok=True)
sim.write_config()
print('Running primary',flush=True)
primary=sim.run_primary()
print('Running held-out',flush=True)
ood=sim.run_ood()
print('Running faults',flush=True)
faults=sim.run_fault_injection()
'''
    if args.full:
        code += "print('Running ablations',flush=True)\nsim.run_ablation()\nprint('Running normalization',flush=True)\nsim.run_normalization_benchmark()\n"
    code += "print('Regenerating summary statistics',flush=True)\nsim.summarize_and_test(primary,ood,faults)\n"
    call(sys.executable,'-c',"import sys;sys.path.insert(0,'code');"+code,cwd=work)
    call(sys.executable,'code/revision_analysis.py',cwd=work)
    call(sys.executable,'code/export_revision_tables.py',cwd=work)
    if args.prototype:
        call(sys.executable,'prototype/run_poc.py',cwd=work)
        call(sys.executable,'code/verify_claims.py',cwd=work)
    cmd=[sys.executable,str(ROOT/'tools/verify_package.py'),'--root',str(ROOT),
         '--independent-root',str(work),'--output',str(work/'our_comparison.json')]
    call(*cmd,cwd=work)
    print('\nReproduction verified. New output:',work)
    print('Note: script does not force or calibrate numerical agreement with the manuscript.')

if __name__=='__main__':
    main()
