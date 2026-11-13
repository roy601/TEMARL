"""CasinoLimit trace replay with simulated resource allocation outcomes."""
from pathlib import Path
import sys, json, hashlib, importlib.util, argparse, dataclasses, os, time, uuid
import numpy as np
import torch
from torch import nn
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT/'casinolimit_encoder'))
import cl_port as P
import cl_data as D
V = P.V
sys.path.insert(0, str(ROOT/'kuwano_repro'))
import kuwano
N_AGENTS, LOCAL_DIM, GLOBAL_DIM = 4, 77, 85
MACHINES = ('start','bastion','meet','intranet')
ARMS = ('allpos','baseline','gru_allpos','lstm_allpos','Kuwano','NoHistory')

@dataclasses.dataclass
class EnvConfig:
    fog: float = 0
    efficacy: float = .5
    k_capacity: int = 2

@dataclasses.dataclass
class EpisodeSpec:
    run_id: str
    commands: tuple
    machines: tuple
    u: np.ndarray
    scenario: str = 'casinolimit'
    @property
    def horizon(self): return len(self.commands)

def make_spec(r, rng):
    return EpisodeSpec(r['id'],r['commands'],r['machines'],rng.random((2,len(r['commands']))))

class ReplayPool:
    def __init__(self,runs,seed): self.runs,self.rng=runs,np.random.default_rng(seed)
    def next(self): return make_spec(self.runs[int(self.rng.integers(len(self.runs)))],self.rng)

class CommandEngagementEnv:
    def __init__(self,cfg,max_steps=482): self.cfg=cfg
    def reset(self,spec):
        self.spec=spec; self.t=0; self.done=False; self.dwell=0; self.depth=set()
        self.acts=np.zeros(4,int); self.visible=False; self.last=-1; self.labels=()
        self.deploy=0; self.violations=0
        return self
    def step(self,actions):
        if self.done: raise RuntimeError('Replay exhausted')
        a=np.asarray(actions)
        if a.shape!=(4,) or np.any((a<0)|(a>1)): raise ValueError('Invalid actions')
        zone=self.spec.machines[self.t]; labels=self.spec.commands[self.t]
        n=int(a.sum()); factor=min(1,self.cfg.k_capacity/max(1,n))
        engaged=bool(a[zone] and self.spec.u[0,self.t]<self.cfg.efficacy*factor)
        self.visible=bool(self.spec.u[1,self.t]>=self.cfg.fog)
        self.last=zone; self.labels=labels; self.acts=a.copy()
        self.deploy+=n; self.violations+=int(n>self.cfg.k_capacity)
        if engaged: self.dwell+=1; self.depth.update(labels)
        self.t+=1; self.done=self.t==self.spec.horizon
        return float(engaged)-.01*n,self.done,{'labels':labels,'machine':zone,'engaged':engaged}
    def local_obs(self,out=None):
        o=np.zeros((4,LOCAL_DIM),np.float32) if out is None else out; o[:]=0
        for i in range(4):
            o[i,i]=1; o[i,4]=self.acts[i]; o[i,5]=self.acts.sum()/4; o[i,6]=self.t/482
            if self.visible and self.last==i: o[i,7]=1; o[i,8+np.asarray(self.labels,int)]=1
        return o
    def global_state(self,out=None):
        o=np.zeros(GLOBAL_DIM,np.float32) if out is None else out; o[:]=0
        o[:4]=self.acts; o[4]=self.t/482
        if self.last>=0: o[5+self.last]=1
        o[9+np.asarray(self.labels,int)]=1
        return o
    def episode_stats(self):
        return dict(run=self.spec.run_id,dwell=float(self.dwell),depth=float(len(self.depth)),
            protected=float(self.dwell/max(1,self.t)),exposed=0.,length=float(self.t),
            lure_chains=0.,dead_ends=0.,capacity_violations=float(self.violations),decoys_deployed=float(self.deploy))

# Reuse the existing PPO/GAE/CTDE implementation with this environment interface.
sys.modules['env_cmd']=sys.modules[__name__]
spec=importlib.util.spec_from_file_location('cl_marl',ROOT/'camlds_real_full_arch/mappo_cmd.py')
R=importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
R.N_ACTIONS=2; R.NT=P.NT
class SmallQueue(R.Episodes):
    def __init__(self,pool,bank,chunk=2): super().__init__(pool,bank,chunk)
R.Episodes=SmallQueue

class Bank(R.HistoryBank):
    fog=0.; seed=0
    @torch.no_grad()
    def table(self,sp):
        key=sp.run_id
        if key in self._cache: return self._cache[key]
        out=np.zeros((sp.horizon+1,64),np.float32)
        if self.model is not None and not self.h_zero:
            # Same episode visibility uniforms as the local observation channel.
            x=np.zeros((sp.horizon,16,P.NT),np.float32); m=np.zeros((sp.horizon,16),np.float32)
            for t in range(1,sp.horizon+1):
                for j in range(max(0,t-16),t):
                    k=16-(t-j)
                    m[t-1,k]=1
                    if sp.u[1,j]>=self.fog: x[t-1,k,list(sp.commands[j])]=1
            valid=m.sum(1)>0
            for start in range(0,len(x),128):
                ids=np.flatnonzero(valid[start:start+128])+start
                if len(ids): out[ids+1]=self.model.history(torch.tensor(x[ids],device=self.device),torch.tensor(m[ids],device=self.device)).cpu().numpy()
        # Visibility changes across episode repeats: never cache by run alone.
        return out
R.HistoryBank=Bank

class KuwanoAdapter(nn.Module):
    def __init__(self):
        super().__init__(); self.data=kuwano.load(); self.cache={}
        q=np.random.default_rng(2310).normal(size=(P.NT,64)).astype(np.float32)/8
        self.register_buffer('projection',torch.tensor(q))
    def history(self,x,m):
        rows=[]
        for a,b in zip(x.cpu().numpy(),m.cpu().numpy()):
            ids=tuple(np.flatnonzero((a*b[:,None]).sum(0)>0))
            if ids not in self.cache:
                scores,_=kuwano.recommend_limit([P.LABELS[i] for i in ids],self.data)
                vals=[]
                for t in P.LABELS:
                    n,s=scores.get(t,(0,0)); vals.append(1. if n else float(s)/(1+float(s)))
                self.cache[ids]=vals
            rows.append(self.cache[ids])
        return torch.tensor(rows,device=x.device,dtype=x.dtype)@self.projection

def runs(f,split):
    return [dict(id=name,commands=tuple(tuple(P.LABEL_ID[t] for t in s['techniques_parent']) for s in q),
                 machines=tuple(MACHINES.index(s['machine']) for s in q))
            for name,q in D.sequences(f['_steps'],f[split+'_runs']).items()]

def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp'); tmp.write_text(json.dumps(obj,indent=2),encoding='utf8')
    for attempt in range(12):
        try: os.replace(tmp,p); break
        except PermissionError:
            if attempt==11: raise
            time.sleep(min(.1*2**attempt,2))

def model(arm,f,seed,args):
    if arm=='NoHistory': return None
    if arm=='Kuwano': return KuwanoAdapter()
    path=(args.output/'smoke_encoders'/arm/f['fold']/f's{seed}'/'encoder.pt' if args.smoke else args.encoder_root/'train/main'/arm/f['fold']/f's{seed}'/'encoder.pt')
    if not path.exists():
        if not args.train_missing: raise FileNotFoundError(f'{path}; supply checkpoints or --train-missing')
        budget=json.loads((args.encoder_root/'budget.json').read_text())
        d=D.fold_data(f)
        V.train_variant(arm,16,seed,d['train'],d['val'],2 if args.smoke else budget['shared_update_budget'],
            device=torch.device(args.device),checkpoint_dir=str(path.parent),patience_checks=budget['shared_patience'],progress=True)
    ck=torch.load(path,map_location='cpu',weights_only=False)
    net=V.build_variant(arm,16); net.load_state_dict(ck['state_dict']); net.eval()
    d=D.fold_data(f)
    logits=V.numpy_logits(net,*d['val'][:2],torch.device('cpu'))
    measured=P.Mx.bce(logits,d['val'][2])
    if 'validation_bce' in ck and abs(measured-ck['validation_bce'])>1e-4:
        raise ValueError('Checkpoint validation BCE mismatch')
    return net

def report(out):
    lines=['# CasinoLimit full architecture','',
        'Recorded trace replay; simulated decoy interception. Interception % is NOT measured asset protection.', '',
        '| Arm | Fold | Seed | Learner | Fog | Dwell steps | Depth | Interception % |',
        '|---|---|---:|---|---:|---:|---:|---:|']
    for p in sorted(out.glob('cells/*/result.json')):
        r=json.loads(p.read_text()); s=r['test_summary']
        lines.append(f"| {r['arm']} | {r['fold']} | {r['seed']} | {r['learner']} | {r['fog']} | {s['dwell']:.3f} | {s['depth']:.3f} | {100*s['protected']:.2f} |")
    lines+=['','## Training curves','']
    for p in sorted(out.glob('cells/*/result.json')):
        r=json.loads(p.read_text()); lines += [f'### {p.parent.name}','','| Update | Env steps | Training dwell | Validation dwell |','|---:|---:|---:|---:|']
        for c in r['curve']: lines.append(f"| {c['update']} | {c['env_steps']} | {c['train_dwell']:.3f} | {c['val_dwell']:.3f} |")
    (out/'RESULTS.md').write_text('\n'.join(lines),encoding='utf8')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--device',default='cpu'); p.add_argument('--smoke',action='store_true')
    p.add_argument('--train-missing',action='store_true'); p.add_argument('--encoder-root',type=Path,default=ROOT/'casinolimit_encoder/out')
    p.add_argument('--output',type=Path,default=HERE/'results/main'); p.add_argument('--seeds',nargs='+',type=int,default=list(range(10)))
    p.add_argument('--arms',nargs='+',choices=ARMS,default=list(ARMS)); p.add_argument('--env-steps',type=int,default=2000000)
    args=p.parse_args(); torch.set_num_threads(4); P.verify(); fs=D.folds()
    if args.device=='cuda' and not torch.cuda.is_available(): raise RuntimeError('CUDA unavailable')
    if args.smoke: fs=fs[:1]; args.seeds=[0]; args.env_steps=8; R.HP.update(n_envs=2,rollout_len=4,ppo_epochs=1,n_evals=1); args.output=args.output/'smoke'
    args.output.mkdir(parents=True,exist_ok=True)
    kd=kuwano.load()
    write(args.output/'DATA_AUDIT.json',{'source':str(P.STEPS_PATH),'sha256':P.STEPS_SHA256,
        'steps':len(P.STEPS),'instances':len({s['run'] for s in P.STEPS}),'labels':P.NT,
        'kuwano_unsupported_labels':sorted(set(P.LABELS)-set(kd.techniques)),
        'outcomes':'simulated interception, not measured asset protection'})
    manifest={'args':{k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},'corpus_sha256':P.STEPS_SHA256,'splits':[{k:v for k,v in f.items() if k!='_steps'} for f in fs]}
    manifest['source_hashes']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        for q in (HERE/'pipeline.py',ROOT/'camlds_real_full_arch/mappo_cmd.py',ROOT/'casinolimit_encoder/cl_split.py',ROOT/'camlds_encoder/variants.py',ROOT/'kuwano_repro/kuwano.py',args.encoder_root/'budget.json') if q.is_relative_to(ROOT)}
    mp=args.output/'MANIFEST.json'
    if mp.exists() and json.loads(mp.read_text())!=manifest: raise RuntimeError('Changed configuration; choose new output')
    write(mp,manifest)
    for f in fs:
        assert not(set(f['train_runs'])&set(f['test_runs']))
        for seed in args.seeds:
            va=[make_spec(r,np.random.default_rng(100000+seed+i)) for i,r in enumerate(runs(f,'val'))]
            te=[make_spec(r,np.random.default_rng(200000+seed+i)) for i,r in enumerate(runs(f,'test'))]
            for arm in args.arms:
                net=model(arm,f,seed,args)
                for learner in ('IPPO','MAPPO'):
                    for fog in (0.,.5,.9):
                        dest=args.output/'cells'/f'{arm}_{f["fold"]}_s{seed}_{learner}_fog{fog}'
                        if (dest/'result.json').exists(): continue
                        print(dest.name,flush=True); Bank.fog=fog
                        result=R.train(net,EnvConfig(fog=fog),runs(f,'train'),va,te,seed,args.env_steps,16,482,learner=='MAPPO',args.device,True)
                        dest.mkdir(parents=True,exist_ok=True); torch.save(result.pop('actor_state'),dest/'actor.pt')
                        result.update(arm=arm,fold=f['fold'],learner=learner,fog=fog)
                        write(dest/'result.json',result); report(args.output)
    print('FINISHED',args.output/'RESULTS.md')
if __name__=='__main__': main()
