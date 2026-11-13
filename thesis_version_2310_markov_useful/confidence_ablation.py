"""Validation-calibrated entropy intervention; see CONFIDENCE_PROTOCOL.md."""
import json
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp, softmax

from encoders_marl import H_DIM
from markov_data import NT, windows, evaluation_specs, ReplaySource
from markov_training import load_encoder, write_json, save_checkpoint
from pretrain_marl import HistoryBank
from report_markov_study import table, mean_sd, paired, holm

METRICS = ("episode_reward", "dwell", "depth", "protected", "exposed",
           "lure_chains", "dead_ends", "capacity_violations", "length", "decoys_deployed")


def entropy(prob):
    return np.clip(-(prob * np.log(np.maximum(prob, 1e-300))).sum(-1) / np.log(NT), 0, 1)


@torch.no_grad()
def logits_for(enc, data, device):
    enc.eval()
    X,L,_,_ = data
    return np.concatenate([enc.pretrain_forward(torch.as_tensor(X[i:i+512],device=device),
                           torch.as_tensor(L[i:i+512],device=device))[1][:,:NT].cpu().double().numpy()
                           for i in range(0,len(X),512)])


def calibration_metrics(logits, targets, temperature):
    z = logits / temperature
    p = softmax(z,axis=-1)
    confidence = p.max(-1); correct = p.argmax(-1) == targets
    reliability = []
    for b in range(10):
        mask = np.minimum((confidence*10).astype(int),9) == b
        reliability.append(dict(bin=b,n=int(mask.sum()),
            confidence=float(confidence[mask].mean()) if mask.any() else None,
            accuracy=float(correct[mask].mean()) if mask.any() else None))
    ece = sum(r["n"]/len(targets)*abs(r["confidence"]-r["accuracy"]) for r in reliability if r["n"])
    return dict(n=len(targets),nll=float(np.mean(logsumexp(z,axis=1)-z[np.arange(len(targets)),targets])),
                top1=float(correct.mean()),ece=float(ece),
                brier=float(np.mean(np.sum(p*p,axis=1)-2*p[np.arange(len(targets)),targets]+1)),
                reliability=reliability)


def fit_temperature(logits, targets):
    def objective(log_t):
        z = logits / np.exp(log_t)
        return float(np.mean(logsumexp(z,axis=1)-z[np.arange(len(targets)),targets]))
    result = minimize_scalar(objective,bounds=(-4.,4.),method="bounded")
    if not result.success:
        raise RuntimeError("Temperature fitting failed")
    # Identity is an explicit fallback, not a test-driven choice.
    value = float(np.exp(result.x)) if result.fun < objective(0.) else 1.
    return value


def group(value, thresholds):
    return ("low", "medium", "high")[int(np.searchsorted(thresholds,value,side="right"))]


class ConfidenceHistoryBank(HistoryBank):
    """65th feature is predictive entropy, never the true next label."""
    width = H_DIM + 1

    def __init__(self, encoder, temperature, device="cpu"):
        super().__init__(encoder,device)
        if encoder is None or temperature <= 0 or not np.isfinite(temperature):
            raise ValueError("Requires a frozen encoder and positive temperature")
        self.temperature = temperature

    def tables(self, specs):
        embeddings = super().tables(specs)
        out = [np.concatenate([h,np.ones((len(h),1),np.float32)],axis=1) for h in embeddings]
        # windows() produces targets for scoring, but only X/L enter inference.
        runs = [dict(id=str(i),seq=sp.tau.tolist()) for i,sp in enumerate(specs)]
        if not any(len(r["seq"]) > 1 for r in runs):
            return out
        data = windows(runs)
        values = entropy(softmax(logits_for(self.enc,data,self.device)/self.temperature,axis=-1))
        offset = 0
        for sp,tb in zip(specs,out):
            n = sp.horizon-1
            tb[1:,H_DIM] = values[offset:offset+n]
            offset += n
        return out


def diagnostic(logits, targets, owners, temperature, thresholds):
    p = softmax(logits/temperature,axis=-1)
    certainty = 1-entropy(p)
    groups = [group(x,thresholds) for x in certainty]
    return [dict(group=g,n=groups.count(g),
                 accuracy=float(np.mean((p.argmax(-1)==targets)[np.array(groups)==g])) if g in groups else None,
                 certainty=float(certainty[np.array(groups)==g].mean()) if g in groups else None)
            for g in ("low","medium","high")]


def run(args, split, out, manifest):
    from env_marl import EnvConfig, SCRIPT_IDS
    from mappo import train, HP
    from run_markov_study import ENCODERS, ROOT, file_hash, completed
    cfg = EnvConfig(**json.loads((ROOT/"env_config.json").read_text())["config"])
    for arm in ENCODERS:
        for seed in args.seeds:
            enc_folder = out/"prediction"/f"real_100_{arm}_s{seed}"
            enc = load_encoder(enc_folder,args.device)
            val_data, test_data = windows(split["validation"]),windows(split["test"])
            vl = logits_for(enc,val_data,args.device)
            temperature = fit_temperature(vl,val_data[2])
            thresholds = np.quantile(1-entropy(softmax(vl/temperature,axis=-1)),[1/3,2/3]).tolist()
            tl = logits_for(enc,test_data,args.device)
            bank = ConfidenceHistoryBank(enc,temperature,args.device)
            va,_ = evaluation_specs(split["validation"],args.val_repeats,200000+seed)
            te,labels = evaluation_specs(split["test"],args.test_repeats,300000+seed)
            # Fixed run groups: identical for both policies, independent of termination.
            va_tables = bank.tables(va)
            va_cert = [float((1-t[1:,H_DIM]).mean()) for t in va_tables if len(t)>1]
            episode_thresholds = np.quantile(va_cert,[1/3,2/3]).tolist()
            te_tables = bank.tables(te)
            for label,tb in zip(labels,te_tables):
                c = float((1-tb[1:,H_DIM]).mean()) if len(tb)>1 else None
                label.update(sequence_certainty=c,confidence_group=group(c,episode_thresholds) if c is not None else "no_history")
            calibration = dict(encoder=arm,seed=seed,temperature=temperature,
                window_thresholds=thresholds,episode_thresholds=episode_thresholds,
                encoder_sha256=file_hash(enc_folder/"encoder.pt"),
                validation_raw=calibration_metrics(vl,val_data[2],1.),
                validation_scaled=calibration_metrics(vl,val_data[2],temperature),
                test_raw=calibration_metrics(tl,test_data[2],1.),
                test_scaled=calibration_metrics(tl,test_data[2],temperature),
                prediction_groups=diagnostic(tl,test_data[2],test_data[3],temperature,thresholds))
            write_json(out/"confidence"/"calibration"/f"{arm}_s{seed}.json",calibration)
            for learner in ("IPPO","MAPPO"):
                for mode in ("baseline","confidence"):
                    folder = out/"confidence"/"cells"/f"{arm}_{learner}_{mode}_s{seed}"
                    if completed(folder,manifest) is not None:
                        continue
                    print("Confidence ablation:",folder.name,flush=True)
                    result = train(enc,cfg,SCRIPT_IDS,seed,16 if args.smoke else args.rl_steps,
                        centralised=learner=="MAPPO",device=args.device,verbose=True,
                        train_source=ReplaySource(split["train"],100000+seed),
                        validation_specs=va,evaluation_specs=te,history_bank=bank,
                        confidence_aware=mode=="confidence")
                    save_checkpoint(folder/"policy.pt",dict(actor=result["actor"].state_dict(),
                        confidence_aware=mode=="confidence",temperature=temperature,
                        encoder_sha256=calibration["encoder_sha256"]))
                    rows = [dict(**r,**label) for r,label in zip(result["test_rows"],labels)]
                    write_json(folder/"result.json",dict(fingerprint=manifest["fingerprint"],
                        encoder=arm,learner=learner,mode=mode,seed=seed,temperature=temperature,
                        actor_params=result["actor_params"],critic_params=result["critic_params"],
                        env_steps=result["env_steps"],best_update=result["best_update"],
                        val_best=result["val_best"],curve=result["curve"],test=rows,
                        test_summary={k:float(np.mean([r[k] for r in rows])) for k in METRICS},
                        checkpoint="policy.pt",checkpoint_sha256=file_hash(folder/"policy.pt")))
                    report(out)


def report(out):
    from collections import defaultdict
    out = Path(out)
    manifest = json.loads((out/"manifest.json").read_text())
    cells = [json.loads(p.read_text()) for p in sorted((out/"confidence"/"cells").glob("*/result.json"))]
    if any(r["fingerprint"] != manifest["fingerprint"] for r in cells):
        raise ValueError("Confidence results have incompatible fingerprints")
    cal = [json.loads(p.read_text()) for p in sorted((out/"confidence"/"calibration").glob("*.json"))]
    groups = defaultdict(list)
    for r in cells:
        groups[(r["encoder"],r["learner"],r["mode"])].append(r)
    lines = ["# Confidence ablation results", "",
        f"Completed policy cells: {len(cells)}/{12*len(manifest['config']['seeds'])}.",
        "SMOKE CHECK ONLY; not thesis evidence." if manifest["config"]["smoke"] else "Mean +/- sample SD across training seeds; episodes are not independent training replicates.",
        "", "Actor-only intervention: same 64-D embedding; constant 0.5 versus calibrated normalized entropy in the existing gate slot. Critic unchanged.",
        "No generic deception-success metric is invented. Asset protection and engagement are reported separately.",
        "", "## Main results", "Percentages: protected/exposed. Other metrics use their original units.", ""]
    lines += table(["Encoder","RL","Mode","Seeds"]+list(METRICS),
        [[*key,len(rs)]+[mean_sd([r["test_summary"][m] for r in rs],100 if m in ("protected","exposed") else 1) for m in METRICS] for key,rs in sorted(groups.items())])
    contrasts=[]
    for arm,learner,_ in sorted(groups):
        if _ != "confidence": continue
        a={r["seed"]:r["test_summary"]["dwell"] for r in groups[(arm,learner,"confidence")]}
        b={r["seed"]:r["test_summary"]["dwell"] for r in groups[(arm,learner,"baseline")]}
        contrasts.append(paired(a,b,f"{arm}+{learner}","dwell"))
    if len(contrasts)==6 and all(r["n"]==len(manifest["config"]["seeds"]) for r in contrasts):
        holm(contrasts)
    lines += ["", "## Primary paired contrasts", "Confidence minus baseline dwell (steps); two-sided paired t intervals/tests. Holm across all six contrasts only when complete. n=1 has no inferential result.", ""]
    lines += table(["Contrast","Pairs","Delta","95% CI","p raw","p Holm"],[[r[k] for k in ("contrast","n","delta","ci95","p_raw","p_holm")] for r in contrasts])
    lines += ["", "## Calibration per seed", "Temperature fitted only on validation NLL; validation is also reused for encoder/policy selection, so only test scores are held-out estimates. ECE uses 10 equal-width max-probability bins, not entropy bins.", ""]
    lines += table(["Encoder","Seed","T","Partition","N","NLL","Top1 %","ECE %","Brier"],
        [[r["encoder"],r["seed"],r["temperature"],part,r[part]["n"],r[part]["nll"],100*r[part]["top1"],100*r[part]["ece"],r[part]["brier"]] for r in cal for part in ("validation_raw","validation_scaled","test_raw","test_scaled")])
    lines += ["", "## Prediction certainty groups", "Certainty = 1 - normalized entropy; not probability of being correct. Thresholds: validation-window tertiles. Empty bins are N/A.", ""]
    lines += table(["Encoder","Seed","Thresholds","Group","Windows","Accuracy","Mean certainty"],
        [[r["encoder"],r["seed"],r["window_thresholds"],b["group"],b["n"],b["accuracy"],b["certainty"]] for r in cal for b in r["prediction_groups"]])
    lines += ["", "## Policy results by fixed sequence-certainty group", "Groups use whole-playbook mean prefix certainty and validation-playbook tertiles, not policy-dependent visited prefixes. Grouping is retrospective, never input to the policy. Descriptive only: groups may differ in scenario/difficulty; no causal claim.", ""]
    rows=[]
    for key,rs in sorted(groups.items()):
        for g in ("low","medium","high","no_history"):
            selected=[[t for t in r["test"] if t["confidence_group"]==g] for r in rs]
            nonempty=[x for x in selected if x]
            rows.append([*key,g,len(nonempty),sum(map(len,selected))]+[mean_sd([np.mean([x[m] for x in ss]) for ss in nonempty],100 if m in ("protected","exposed") else 1) for m in METRICS])
    lines += table(["Encoder","RL","Mode","Group","Seeds with data","Episodes"]+list(METRICS),rows)
    lines += ["", "## Every policy seed", ""]
    lines += table(["Encoder","RL","Mode","Seed","Steps","Actor params","Critic params","Best update","Validation dwell"]+list(METRICS),
        [[r[k] for k in ("encoder","learner","mode","seed","env_steps","actor_params","critic_params","best_update","val_best")]+[r["test_summary"][m] for m in METRICS] for r in cells])
    lines += ["", "Full episode, calibration-bin and policy-learning records: [CONFIDENCE_DETAILS.md](CONFIDENCE_DETAILS.md). Encoder epoch results: [EPOCH_RESULTS.md](EPOCH_RESULTS.md).", ""]
    (out/"CONFIDENCE_RESULTS.md").write_text("\n".join(lines),encoding="utf-8")
    details=["# Confidence ablation: every measured record", ""]
    for r in cal:
        details += [f"## {r['encoder']} seed {r['seed']} calibration",f"Temperature: {r['temperature']}; episode thresholds: {r['episode_thresholds']}; encoder SHA256: {r['encoder_sha256']}",""]
        details += table(["Partition","Bin","Count","Mean max probability","Accuracy"],[[part,b['bin'],b['n'],b['confidence'],b['accuracy']] for part in ("validation_raw","validation_scaled","test_raw","test_scaled") for b in r[part]['reliability']])
    for r in cells:
        details += [f"## {r['encoder']} {r['learner']} {r['mode']} seed {r['seed']}",""]
        keys=list(r['curve'][0]) if r['curve'] else []
        details += table(keys,[[c[k] for k in keys] for c in r['curve']])
        keys=list(r['test'][0]) if r['test'] else []
        details += table(keys,[[c[k] for k in keys] for c in r['test']])
    (out/"CONFIDENCE_DETAILS.md").write_text("\n".join(details),encoding="utf-8")
