#!/usr/bin/env python3
"""Orchestrate the original author's H-MARL 3-policy evaluation (no mock data)."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from preflight import run_check

COMMANDS = {
    'expert': ['subpolicies/evaluation_metrics.py', 'subpolicies/submission.py'],
    'meta': ['master/evaluation_metrics.py', 'master/submission.py'],
}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,default=Path('sources/Hierarchical-MARL'))
    p.add_argument('--cage',type=Path,default=Path('sources/cage-challenge-4'))
    p.add_argument('--out',type=Path,default=Path('results'))
    p.add_argument('--policies',nargs='+',choices=['expert','meta'],default=['expert','meta'])
    p.add_argument('--max-eps',type=int,default=100)
    p.add_argument('--seed',type=int,default=42)
    p.add_argument('--timeout-seconds',type=int,default=0)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    status={'utc':datetime.now(timezone.utc).isoformat(), 'requested_policies':args.policies,
            'max_eps':args.max_eps,'seed':args.seed,'runs':{},'outcome':'NOT_EXECUTED'}
    def save():
        (args.out/'run_status.json').write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
    if args.max_eps < 1: p.error('--max-eps must be positive')
    checks=run_check(args.repo.resolve(),args.cage.resolve())
    (args.out/'preflight.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    if not checks['ready_for_100_episode_metrics_run']:
        status['reason']='Preflight failed; no simulator results have been generated.'
        status['outcome']='BLOCKED'
        save()
        print('BLOCKED: preflight failed. Inspect results/preflight.json and see REPRODUCTION_REPORT.md',file=sys.stderr)
        return 2
    if args.max_eps != 100:
        status['warning']='Not directly comparable with 100-episode averages in published Table 3.'
    cwd=(args.repo/'h-marl-3policy').resolve()
    for name in args.policies:
        out=(args.out/name).resolve()
        out.mkdir(parents=True,exist_ok=True)
        cmd=[sys.executable, '-u', *COMMANDS[name], str(out),'--seed',str(args.seed),'--max-eps',str(args.max_eps)]
        log=out/'console.log'
        status['runs'][name]={'command':cmd,'cwd':str(cwd),'log':str(log),'outcome':'STARTED'}
        save()
        print(f'RUN: {name} | cwd={cwd} | command={" ".join(cmd)}',flush=True)
        with open(log,'w',encoding='utf-8') as output:
            output.write('$ '+' '.join(cmd)+'\n')
            output.flush()
            try:
                completed=subprocess.run(cmd,cwd=str(cwd),stdout=output,stderr=subprocess.STDOUT,
                                         timeout=args.timeout_seconds or None,check=False)
                status['runs'][name]['exit_code']=completed.returncode
                summary=out/'summary.json'
                status['runs'][name]['summary_exists']=summary.exists()
                status['runs'][name]['outcome']='COMPLETED' if completed.returncode==0 and summary.exists() else 'FAILED'
            except subprocess.TimeoutExpired:
                status['runs'][name]['outcome']='TIMEOUT'
            except Exception as e:
                status['runs'][name]['outcome']='FAILED'
                status['runs'][name]['error']=repr(e)
        save()
    status['outcome']='FINISHED' if all(r['outcome']=='COMPLETED' for r in status['runs'].values()) else 'PARTIAL_OR_FAILED'
    save()
    print(json.dumps(status,indent=2))
    return 0 if status['outcome']=='FINISHED' else 1

if __name__=='__main__': sys.exit(main())
