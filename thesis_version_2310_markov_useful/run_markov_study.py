"""Run the controlled Markov usefulness study. Default full experiment is for the lab PC."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform

import numpy as np
import torch

from markov_data import (ROOT, SOURCE, MARKOV_DESCRIPTION, load_runs, split_runs,
                         coverage, similarity, markov_baselines, subset, generate,
                         quality, windows, repeat_windows, ReplaySource, evaluation_specs)
from markov_training import (TRAINING, write_json, save_checkpoint, train_encoder,
                             predict, readable_examples, load_encoder)

ENCODERS = ("Transformer","GRU","LSTM")
FRACTIONS = (.25,.5,.75,1.)
RATIOS = (.25,.5,1.,2.)


def file_hash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fingerprint():
    paths = list(ROOT.glob("*.py")) + [ROOT/"env_config.json",ROOT/"requirements.txt"]
    paths += list((ROOT/"thesis_system").rglob("*.py")) + list((ROOT/"thesis_system").rglob("*.json"))
    return hashlib.sha256(b"".join(p.relative_to(ROOT).as_posix().encode()+p.read_bytes().replace(b"\r\n",b"\n") for p in sorted(paths))).hexdigest()


def conditions(smoke=False):
    fractions = (1.,) if smoke else FRACTIONS
    ratios = (1.,) if smoke else RATIOS
    return ([dict(name=f"real_{int(f*100)}",fraction=f,ratio=0.,kind="real") for f in fractions]
            + [dict(name=f"{kind}_{int(r*100)}",fraction=1.,ratio=r,kind=kind)
               for r in ratios for kind in ("markov","repeat")])


def prepare_audit(args,out):
    runs = load_runs()
    split,notes = split_runs(runs,args.split_seed,args.held_out)
    audit = dict(source_sha256=file_hash(SOURCE), source="AttackBed-derived ordered playbook annotations; not raw logs",
                 split_seed=args.split_seed,held_out=args.held_out,notes=notes,
                 splits={k:[dict(id=r["id"],scenario=r["scenario"],group=r["group"],length=len(r["seq"])) for r in v] for k,v in split.items()},
                 coverage={k:coverage(v,split["train"]) for k,v in split.items()},
                 similarities=similarity(split), markov=MARKOV_DESCRIPTION,
                 baseline=markov_baselines(split),
                 metadata_caveat="The inherited vocabulary, payoff, goals and environment calibration were fixed using the earlier corpus. The new split isolates estimator/encoder/policy fitting, not historical environment design.")
    write_json(out/"audit.json",audit)
    return split


def completed(folder,manifest):
    p = folder/"result.json"
    if not p.exists():
        return None
    r = json.loads(p.read_text(encoding="utf-8"))
    if r["fingerprint"] != manifest["fingerprint"]:
        raise RuntimeError(f"Result code mismatch: {folder}")
    ck = folder/r["checkpoint"]
    if not ck.exists() or file_hash(ck) != r["checkpoint_sha256"]:
        raise RuntimeError(f"Missing or changed checkpoint: {folder}")
    if "best_checkpoint_sha256" in r and file_hash(folder/"encoder_best.pt") != r["best_checkpoint_sha256"]:
        raise RuntimeError(f"Changed validation-best checkpoint: {folder}")
    return r


def choose_epochs(args,split,out,manifest):
    target = out/"epoch_selection.json"
    if target.exists():
        return json.loads(target.read_text())["epochs"]
    if args.smoke or args.epochs != "auto":
        value = 2 if args.smoke else int(args.epochs)
        write_json(target,dict(epochs=value,method="smoke" if args.smoke else "user-fixed",cap_warning=False))
        return value
    # Every pilot uses real training only and validation only; test is not evaluated.
    selected = []
    for arm in ENCODERS:
        for seed in args.pilot_seeds:
            folder = out/"pilot"/f"{arm}_s{seed}"
            result = completed(folder,manifest)
            if result is None:
                _,info = train_encoder(arm,seed,windows(split["train"]),windows(split["validation"]),args.pilot_cap,args.device,folder)
                result = dict(fingerprint=manifest["fingerprint"],encoder=arm,seed=seed,**info,
                              checkpoint="encoder.pt",checkpoint_sha256=file_hash(folder/"encoder.pt"))
                write_json(folder/"result.json",result)
            selected.append(result["selected_epoch"])
    budget = max(selected)
    write_json(target,dict(epochs=budget,method="Maximum validation-best epoch across all real-only pilots",
                           pilot_cap=args.pilot_cap,pilot_seeds=args.pilot_seeds,selected_epochs=selected,
                           cap_warning=any(v >= .9*args.pilot_cap for v in selected),
                           policy="Shared full epoch count; no per-condition early termination. Test is excluded from selection."))
    return budget


def prediction_cell(args,split,cond,seed,epochs,out,manifest):
    training = subset(split["train"],cond["fraction"],81000+seed)
    synthetic = generate(training,cond["ratio"],91000+seed)
    mixed = training+synthetic if cond["kind"] == "markov" else training
    dataset = windows(mixed)
    if cond["kind"] == "repeat":
        dataset = repeat_windows(dataset,len(windows(training+synthetic)[2]))
    if cond["kind"] == "markov":
        write_json(out/"synthetic"/f"{cond['name']}_s{seed}.json",dict(training_runs=[r["id"] for r in training],runs=synthetic))
    for arm in ENCODERS:
        folder = out/"prediction"/f"{cond['name']}_{arm}_s{seed}"
        if completed(folder,manifest) is not None:
            print("Already complete:",folder.name,flush=True); continue
        print("Prediction:",folder.name,flush=True)
        enc,info = train_encoder(arm,seed,dataset,windows(split["validation"]),epochs,args.device,folder)
        va,_ = predict(enc,windows(split["validation"]),args.device)
        te,prob = predict(enc,windows(split["test"]),args.device)
        best_enc = load_encoder(folder,args.device,"encoder_best.pt")
        best_va,_ = predict(best_enc,windows(split["validation"]),args.device)
        best_te,_ = predict(best_enc,windows(split["test"]),args.device)
        result = dict(fingerprint=manifest["fingerprint"],condition=cond,encoder=arm,seed=seed,**info,
                      validation=va,test=te,examples=readable_examples(prob,windows(split["test"])),
                      validation_best=best_va,test_best=best_te,
                      best_checkpoint_sha256=file_hash(folder/"encoder_best.pt"),
                      n_training_runs=len(training),n_original_groups=len({r["group"] for r in training}),
                      n_synthetic=len(synthetic) if cond["kind"] == "markov" else 0,
                      quality=quality(synthetic,training) if cond["kind"] == "markov" else None,
                      checkpoint="encoder.pt",checkpoint_sha256=file_hash(folder/"encoder.pt"))
        write_json(folder/"result.json",result)
    return mixed


def run_rl(args,split,out,manifest):
    from env_marl import EnvConfig,SCRIPT_IDS
    from mappo import train,summary,HP
    if args.smoke:
        HP.update(n_envs=2,rollout_len=8,ppo_epochs=1,n_evals=1,val_episodes=2)
    cfg = EnvConfig(**json.loads((ROOT/"env_config.json").read_text())["config"])
    for condition in ("real_100","markov_100","repeat_100"):
        for seed in args.seeds:
            original = subset(split["train"],1.,81000+seed)
            augmented = generate(original,1.,91000+seed)
            training = original+augmented if condition == "markov_100" else original
            val_specs,_ = evaluation_specs(split["validation"],args.val_repeats,200000+seed)
            test_specs,labels = evaluation_specs(split["test"],args.test_repeats,300000+seed)
            arms = ENCODERS + (("NoHistory",) if condition == "real_100" else ())
            for arm in arms:
                for learner in ("IPPO","MAPPO"):
                    folder = out/"rl"/f"{condition}_{arm}_{learner}_s{seed}"
                    if completed(folder,manifest) is not None:
                        print("Already complete:",folder.name,flush=True); continue
                    enc = None if arm == "NoHistory" else load_encoder(out/"prediction"/f"{condition}_{arm}_s{seed}",args.device)
                    print("Deception:",folder.name,flush=True)
                    result = train(enc,cfg,SCRIPT_IDS,seed,16 if args.smoke else args.rl_steps,
                                   centralised=learner == "MAPPO",device=args.device,verbose=True,
                                   train_source=ReplaySource(training,100000+seed),
                                   validation_specs=val_specs,evaluation_specs=test_specs)
                    save_checkpoint(folder/"policy.pt",dict(actor=result["actor"].state_dict(),
                                                            critic=result["critic"].state_dict()))
                    rows = [dict(**r,**label) for r,label in zip(result["test_rows"],labels)]
                    write_json(folder/"result.json",dict(fingerprint=manifest["fingerprint"],
                        condition=condition,encoder=arm,learner=learner,seed=seed,
                        env_steps=result["env_steps"],ppo_epochs=HP["ppo_epochs"],
                        best_update=result["best_update"],val_best=result["val_best"],curve=result["curve"],
                        test=rows,test_summary=summary(rows),test_h0_summary=summary(result["test_rows_h0"]),
                        checkpoint="policy.pt",checkpoint_sha256=file_hash(folder/"policy.pt")))
                    from report_markov_study import report
                    report(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--device",choices=("auto","cpu","cuda"),default="auto")
    ap.add_argument("--epochs",default="auto",help="auto: real-only validation pilot; or one positive integer for all conditions")
    ap.add_argument("--pilot-cap",type=int,default=100)
    ap.add_argument("--pilot-seeds",type=int,nargs="+",default=[101,102,103])
    ap.add_argument("--seeds",type=int,nargs="+",default=list(range(10)))
    ap.add_argument("--split-seed",type=int,default=2310)
    ap.add_argument("--held-out",choices=[f"S{i}" for i in range(1,8)],help="Optional LOSO fold; separate output required")
    ap.add_argument("--threads",type=int,default=4)
    ap.add_argument("--rl-steps",type=int,default=2000000)
    ap.add_argument("--val-repeats",type=int,default=10)
    ap.add_argument("--test-repeats",type=int,default=50)
    ap.add_argument("--prediction-only",action="store_true")
    ap.add_argument("--confidence-ablation",action=argparse.BooleanOptionalAction,default=True,
                    help="Run the paired real-only confidence ablation (default enabled)")
    ap.add_argument("--audit-only",action="store_true")
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--output",type=Path)
    args = ap.parse_args()
    if args.epochs != "auto" and (not args.epochs.isdigit() or int(args.epochs) < 1):
        ap.error("--epochs must be auto or a positive integer")
    if any(x < 1 for x in (args.threads,args.pilot_cap,args.rl_steps,args.val_repeats,args.test_repeats)):
        ap.error("Budgets must be positive")
    for seeds in (args.seeds,args.pilot_seeds):
        if not seeds or len(set(seeds)) != len(seeds) or any(s < 0 or s >= 1000 for s in seeds):
            ap.error("Seeds must be unique integers in 0..999")
    if args.smoke:
        args.seeds=[0]; args.val_repeats=1; args.test_repeats=1
    torch.set_num_threads(args.threads)
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG",":4096:8")
    torch.use_deterministic_algorithms(True,warn_only=True)
    torch.backends.cudnn.benchmark=False
    if args.device == "auto":
        args.device="cuda" if torch.cuda.is_available() else "cpu"
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; install a CUDA PyTorch build first")
    out = args.output or ROOT/"results_markov"/("smoke" if args.smoke else (args.held_out or "main"))
    out = out.resolve(); out.mkdir(parents=True,exist_ok=True)
    plan = conditions(args.smoke)
    manifest = dict(fingerprint=fingerprint(),config={k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items() if k not in ("output","audit_only")},
                    conditions=plan,training=TRAINING,
                    expected_prediction_cells=len(plan)*len(ENCODERS)*len(args.seeds),
                    expected_rl_cells=0 if args.prediction_only else 20*len(args.seeds),
                    expected_confidence_cells=12*len(args.seeds) if args.confidence_ablation and not args.prediction_only else 0,
                    runtime=dict(python=platform.python_version(),torch=torch.__version__,numpy=np.__version__,device=args.device))
    mp = out/"manifest.json"
    if mp.exists() and json.loads(mp.read_text()) != manifest:
        raise RuntimeError("Output already has different code/config/runtime. Use a fresh --output folder.")
    lock = out/".running"
    # Exclusive creation prevents two processes from writing to the same experiment.
    with lock.open("x") as f:
        f.write(str(os.getpid()))
    try:
        write_json(mp,manifest)
        split = prepare_audit(args,out)
        from report_markov_study import report
        report(out)
        if args.audit_only:
            return
        epochs = choose_epochs(args,split,out,manifest)
        print(f"Shared encoder budget: {epochs} full epochs. Test data never used for selection.",flush=True)
        for cond in plan:
            for seed in args.seeds:
                prediction_cell(args,split,cond,seed,epochs,out,manifest)
                report(out)
        if not args.prediction_only:
            run_rl(args,split,out,manifest)
            if args.confidence_ablation:
                from confidence_ablation import run as run_confidence
                run_confidence(args,split,out,manifest)
        report(out)
        print("FINISHED:",out/"RESULTS.md",flush=True)
    finally:
        lock.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
