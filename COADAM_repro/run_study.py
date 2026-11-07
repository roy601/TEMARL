"""Single entry point: smoke, two tracks, ten seeds, resumable stage boundaries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from prepare import ROOT, prepare
from report_results import extract, report

def write_json(path, value):
    path=Path(path); tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,indent=2,sort_keys=True),encoding='utf-8')
    for attempt in range(12):
        try:
            os.replace(tmp,path); return
        except PermissionError:
            if attempt==11: raise
            print(f'Windows delayed file replacement; retry {attempt+1}: {path}',flush=True)
            time.sleep(min(.25*2**attempt,4))

def fingerprint(config):
    files=list(ROOT.glob('*.py'))+list(ROOT.glob('*.json'))+list(ROOT.glob('*.csv'))+list((ROOT/'matlab').glob('*.m'))+list((ROOT/'upstream').glob('*.m'))
    files += [config/'environment_config.mat',config/'threat_profiles.mat']
    hashes={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    return hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),hashes

def matlab_stage(matlab,cell,name,expression):
    marker=cell/(name+'.done.json')
    if marker.exists():
        saved=json.loads(marker.read_text())
        for relative,digest in saved['artifacts'].items():
            p=cell/relative
            if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
                raise RuntimeError(f'Completed stage artifact changed/missing: {p}. Restore it or use a NEW output directory.')
        print(f'SKIP completed {cell.parent.name}/{cell.name}: {name}',flush=True); return
    env=os.environ.copy(); env.update(COADAM_CELL=str(cell),COADAM_PACKAGE=str(ROOT))
    quote=lambda p:str(p).replace("'","''")
    command=f"addpath('{quote(cell/'code')}'); addpath('{quote(ROOT/'matlab')}'); {expression}"
    print(f'RUN {cell.parent.name}/{cell.name}: {name}',flush=True)
    with (cell/'logs'/f'{name}_{time.strftime("%Y%m%d_%H%M%S")}.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen([matlab,'-batch',command],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=env,encoding='utf-8',errors='replace')
        try:
            for line in process.stdout:
                print(line,end='',flush=True); log.write(line); log.flush()
            if process.wait()!=0: raise RuntimeError(f'MATLAB stage failed: {name}. Same command resumes completed stages.')
        except BaseException:
            process.terminate(); process.wait(); raise
    expected={'initialize':['data/processed/environment_config.mat','data/processed/threat_profiles.mat'],
        'check':['runtime.json'], 'tabular':['results/cotraining_results.mat','results/tabular_training.csv'],
        'dqn':['results/dqn_cotraining_results.mat','results/training.csv'],
        'baselines':['results/baseline_results_final.mat']}[name]
    artifacts={p:hashlib.sha256((cell/p).read_bytes()).hexdigest() for p in expected}
    if name=='baselines':
        settings=json.loads((cell/'settings.json').read_text()); extract(cell/'results/baseline_results_final.mat',settings['eval_episodes'])
    write_json(marker,{'artifacts':artifacts,'finished':time.strftime('%Y-%m-%dT%H:%M:%S')})

def run(output,mode,matlab,config,prepare_only=False):
    protocol=json.loads((ROOT/'protocol.json').read_text()); digest,hashes=fingerprint(config)
    output=output.resolve(); output.mkdir(parents=True,exist_ok=True)
    seeds=[0] if mode=='smoke' else protocol['seeds']
    manifest={'mode':mode,'fingerprint':digest,'hashes':hashes,'protocol':protocol,'expected_cells':len(seeds)*len(protocol['tracks'])}
    path=output/'manifest.json'
    if path.exists() and json.loads(path.read_text())!=manifest:
        raise RuntimeError('Frozen protocol/source/config changed. Use a new output directory; do not mix results.')
    write_json(path,manifest)
    lock=output/'RUNNING.lock'
    try:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:
        raise RuntimeError(f'Run lock exists: {lock}. If its process is no longer running, remove ONLY this lock and resume.')
    os.write(fd,f'PID {os.getpid()}\n'.encode()); os.close(fd)
    try:
        for track in protocol['tracks']:
            for seed in seeds:
                cell=output/track/f'seed_{seed:02d}'
                settings=dict(track=track,seed=seed,seed_offset=seed*protocol['seed_stride'],config_source=str(config),
                    train_episodes=protocol['train_episodes'],max_steps=protocol['steps_per_episode'],
                    eval_episodes=protocol['release_eval_episodes'] if track=='release' else protocol['paper_eval_episodes'],
                    baseline_episodes=protocol['baseline_train_episodes'],finetune_episodes=protocol['attacker_finetune_episodes'],
                    stack_simulations=protocol['stackelberg_simulations'],
                    tabular_episodes=protocol['release_tabular_episodes'] if track=='release' else protocol['paper_tabular_episodes'])
                if mode=='smoke':
                    settings.update(train_episodes=8,max_steps=20,eval_episodes=3,baseline_episodes=8,finetune_episodes=4,stack_simulations=2,tabular_episodes=8)
                prepare(cell,settings)
                if prepare_only: continue
                for name,expression in [('initialize','repro_initialize'),('check','repro_check'),('tabular','repro_tabular'),
                        ('dqn','Phase_3and4; repro_training_export'),('baselines','Phase5_Baselines')]:
                    matlab_stage(matlab,cell,name,expression)
                write_json(cell/'complete.json',{'fingerprint':digest})
                count=report(output)
                print(f'COMPLETED {count}/{manifest["expected_cells"]} cells. Report: {output / "RESULTS.md"}',flush=True)
        report(output)
    finally:
        lock.unlink(missing_ok=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/main')
    parser.add_argument('--matlab',default=shutil.which('matlab'))
    parser.add_argument('--config-dir',type=Path,default=ROOT/'upstream/data/processed')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--report-only',action='store_true')
    parser.add_argument('--smoke-only',action='store_true')
    args=parser.parse_args()
    if args.report_only: report(args.output); return
    if not args.prepare_only and not args.matlab:
        parser.error('MATLAB R2025b+ is required. Supply --matlab "C:\\Program Files\\MATLAB\\R2025b\\bin\\matlab.exe"')
    config=args.config_dir.resolve()
    for name in ('environment_config.mat','threat_profiles.mat'):
        if not (config/name).is_file(): parser.error(f'Missing {config/name}')
    smoke=args.output.parent/(args.output.name+'_smoke')
    run(smoke,'smoke',args.matlab,config,args.prepare_only)
    if not args.smoke_only: run(args.output,'full',args.matlab,config,args.prepare_only)

if __name__=='__main__': main()
