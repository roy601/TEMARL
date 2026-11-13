"""True epoch training, validation-only selection, and held-out predictions."""
import copy
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from encoders_marl import build_encoder
from markov_data import metrics, windows, NT
from vocab_v2 import ID_TO_TECHNIQUE, ID_TO_META

TRAINING = dict(batch=64, lr=5e-4, weight_decay=1e-4, grad_clip=1.0)


def write_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(value,indent=2,allow_nan=False),encoding="utf-8")
    os.replace(tmp,path)


def save_checkpoint(path, value):
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp = path.with_suffix(path.suffix+".tmp")
    torch.save(value,tmp); os.replace(tmp,path)


@torch.no_grad()
def predict(enc, dataset, device):
    enc.eval()
    X,L,Y,owners = dataset
    output = []
    for i in range(0,len(Y),512):
        _,lg = enc.pretrain_forward(torch.as_tensor(X[i:i+512],device=device),
                                   torch.as_tensor(L[i:i+512],device=device))
        output.append(lg[:,:NT].softmax(-1).cpu().numpy())
    p = np.concatenate(output)
    return metrics(p,Y,owners),p


def train_encoder(arm,seed,training,validation,epochs,device,folder):
    """Primary checkpoint is the common final epoch; also save validation-best."""
    folder = Path(folder)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    enc = build_encoder(arm).to(device)
    opt = torch.optim.AdamW(enc.parameters(),lr=TRAINING["lr"],weight_decay=TRAINING["weight_decay"])
    X,L,Y,_ = training
    X,L,Y = [torch.as_tensor(a,device=device) for a in (X,L,Y)]
    rng = np.random.default_rng(seed)
    curve = []; best = float("inf"); state = None; best_epoch = 0; updates = 0
    t0 = time.time()
    for epoch in range(1,epochs+1):
        enc.train()
        indices = rng.permutation(len(Y))
        online_loss = 0.
        for start in range(0,len(Y),TRAINING["batch"]):
            ix = torch.as_tensor(indices[start:start+TRAINING["batch"]],device=device)
            _, logits = enc.pretrain_forward(X[ix],L[ix])
            loss = F.cross_entropy(logits[:,:NT],Y[ix])
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(enc.parameters(),TRAINING["grad_clip"])
            opt.step(); updates += 1
            online_loss += float(loss.detach())*len(ix)
        tr,_ = predict(enc,training,device)
        va,_ = predict(enc,validation,device)
        curve.append(dict(epoch=epoch,updates=updates,online_train_nll=online_loss/len(Y),
                          train={k:v for k,v in tr.items() if k != "per_run"},
                          validation={k:v for k,v in va.items() if k != "per_run"},seconds=time.time()-t0))
        if va["nll"] < best:
            best, best_epoch = va["nll"],epoch
            state = {k:v.detach().cpu().clone() for k,v in enc.state_dict().items()}
        write_json(folder/"epochs.json",curve)
        if epoch == 1 or epoch % 10 == 0 or epoch == epochs:
            print(f"    {arm} s{seed} epoch {epoch}/{epochs}: train loss {tr['nll']:.4f}, val loss {va['nll']:.4f}, val Top-1 {va['top1']:.3f}",flush=True)
    save_checkpoint(folder/"encoder_best.pt",dict(arm=arm,seed=seed,state=state,selected_epoch=best_epoch))
    final_state = {k:v.detach().cpu().clone() for k,v in enc.state_dict().items()}
    save_checkpoint(folder/"encoder.pt",dict(arm=arm,seed=seed,state=final_state,selected_epoch=epochs))
    enc.freeze(); enc.eval()
    return enc,dict(epochs_completed=epochs,primary_epoch=epochs,selected_epoch=best_epoch,best_validation_nll=best,
                    optimizer_updates=updates,n_train_windows=len(Y),seconds=time.time()-t0,curve=curve)


def load_encoder(folder,device,checkpoint="encoder.pt"):
    ck = torch.load(Path(folder)/checkpoint,map_location="cpu",weights_only=True)
    enc = build_encoder(ck["arm"]).to(device); enc.load_state_dict(ck["state"])
    enc.freeze(); enc.eval()
    return enc


def readable_examples(prob,dataset,limit=10):
    X,L,Y,owners = dataset
    # Fixed evenly spaced indices, selected independently of model outcomes.
    indices = np.unique(np.linspace(0,len(Y)-1,min(limit,len(Y)),dtype=int))
    rows = []
    for i in indices:
        top = np.argsort(-prob[i],kind="stable")[:3]
        rows.append(dict(window=int(i),run=owners[i],
                         history=[ID_TO_TECHNIQUE[int(t)] for t in X[i,:L[i]][-5:]],
                         actual=ID_TO_TECHNIQUE[int(Y[i])],
                         actual_name=ID_TO_META[int(Y[i])]["name"],
                         actual_probability=float(prob[i,Y[i]]),
                         top3=[dict(technique=ID_TO_TECHNIQUE[int(t)],name=ID_TO_META[int(t)]["name"],probability=float(prob[i,t])) for t in top],
                         correct=bool(top[0] == Y[i])))
    return rows
