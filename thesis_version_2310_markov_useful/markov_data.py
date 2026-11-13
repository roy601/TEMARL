"""Leakage-controlled playbook splits and the inherited first-order generator."""
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import _frozen
from scripts_marl import estimate_chain, FLOOR, BIGRAM_WEIGHT, INIT_WEIGHT
from vocab_v2 import NUM_TECHNIQUES as NT, MAX_SEQ_LEN, PAD_ID, technique_to_id

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "thesis_system/data/camlds_grounding_verified.json"
MARKOV_DESCRIPTION = {
    "name": "Scenario-conditioned, time-homogeneous, first-order categorical Markov chain",
    "order": 1, "hidden_states": False, "mcmc": False,
    "floor": FLOOR, "bigram_weight": BIGRAM_WEIGHT, "initial_weight": INIT_WEIGHT,
    "transition_formula": "P(j|i,s)=(0.02+4*C_s(i,j))/(84*0.02+4*sum_k C_s(i,k))",
    "initial_formula": "P(j|s)=(0.02+2*start_count_s(j))/(84*0.02+2*n_runs_s)",
    "length": "Sample a complete training-run length from the same scenario",
    "scope": "Fit only training runs; no goal drift, HMM, MCMC, AEP or causal constraints",
    "caution": "Smoothing allows unobserved techniques and transitions; validity is not guaranteed.",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def load_runs():
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    runs = []
    for name, record in sorted(raw["runs"].items()):
        seq = [technique_to_id(t) for t in record["sequence"]]
        if len(seq) < 2 or any(t >= NT or t < 0 for t in seq):
            raise ValueError(f"Invalid/unknown technique in {name}")
        runs.append(dict(id=name, scenario=record["scenario"], seq=seq,
                         original=record["sequence"], group=digest(seq), synthetic=False))
    return runs


def split_runs(runs, seed=2310, held_out=None):
    """Group identical model-input sequences before splitting, including cross-scenario duplicates."""
    groups = defaultdict(list)
    for r in runs:
        groups[r["group"]].append(r)
    buckets = defaultdict(list)
    split = {k: [] for k in ("train", "validation", "test")}
    rng = np.random.default_rng(seed)
    notes = []
    for group, members in sorted(groups.items()):
        scenarios = {r["scenario"] for r in members}
        if held_out in scenarios:
            split["test"].extend(members)
        elif len(scenarios) > 1:
            split["train"].extend(members)
            notes.append(f"Cross-scenario duplicate group {group[:10]} retained in training.")
        else:
            buckets[next(iter(scenarios))].append(group)
    for sid, ids in sorted(buckets.items()):
        ids = list(rng.permutation(sorted(ids)))
        if len(ids) < 3:
            notes.append(f"{sid}: {len(ids)} independent groups; training only.")
            nt, nv = 0, 0
        else:
            nt = 0 if held_out else max(1, int(round(.2 * len(ids))))
            nv = max(1, int(round(.2 * len(ids))))
        for i, group in enumerate(ids):
            part = "test" if i < nt else "validation" if i < nt + nv else "train"
            split[part].extend(groups[group])
    for part in split:
        split[part].sort(key=lambda r: r["id"])
        if not split[part]:
            raise ValueError(f"Empty {part} split")
    sets = [{r["group"] for r in split[k]} for k in split]
    if any(sets[i] & sets[j] for i in range(3) for j in range(i)):
        raise AssertionError("Identical model-input sequences crossed split boundaries")
    return split, notes


def subset(runs, fraction, seed):
    by_scenario = defaultdict(dict)
    for r in runs:
        by_scenario[r["scenario"]].setdefault(r["group"], []).append(r)
    rng = np.random.default_rng(seed)
    out = []
    for sid, groups in sorted(by_scenario.items()):
        ids = list(rng.permutation(sorted(groups)))
        take = max(1, math.ceil(len(ids) * fraction))
        for g in ids[:take]:
            out.extend(groups[g])
    return sorted(out, key=lambda r: r["id"])


def grams(runs, n=2):
    return Counter(tuple(r["seq"][i:i+n]) for r in runs for i in range(len(r["seq"])-n+1))


def coverage(runs, training):
    bg, tg, train_bg = grams(runs), grams(runs, 3), grams(training)
    tokens = {x for r in runs for x in r["seq"]}
    train_tokens = {x for r in training for x in r["seq"]}
    counts = Counter(x for r in runs for x in r["seq"])
    n = sum(bg.values())
    return dict(runs=len(runs), independent_groups=len({r["group"] for r in runs}),
                steps=sum(len(r["seq"]) for r in runs), unique_techniques=len(tokens),
                unique_bigrams=len(bg), unique_trigrams=len(tg),
                singleton_bigrams=sum(v == 1 for v in bg.values()),
                unseen_transition_occurrence_pct=100*sum(v for k,v in bg.items() if k not in train_bg)/max(1,n),
                unseen_transition_type_pct=100*sum(k not in train_bg for k in bg)/max(1,len(bg)),
                unseen_technique_occurrence_pct=100*sum(v for k,v in counts.items() if k not in train_tokens)/max(1,sum(counts.values())),
                mean_outgoing=len(bg)/max(1,len({k[0] for k in bg})),
                mathematical_pair_coverage_pct=100*len(bg)/(NT*NT))


def similarity(split):
    tr = split["train"]
    result = []
    for part in ("validation", "test"):
        for r in split[part]:
            a = set(grams([r]))
            scores = [(len(a & set(grams([t])))/max(1,len(a | set(grams([t])))), t["id"]) for t in tr]
            score, name = max(scores)
            result.append(dict(split=part, run=r["id"], nearest_training_run=name, bigram_jaccard=score))
    return result


def generate(training, ratio, seed):
    """Ratios refer to number of sequences. Prefix-nested draws across doses."""
    rng = np.random.default_rng(seed)
    by_sid = defaultdict(list)
    for r in training:
        by_sid[r["scenario"]].append(r)
    models = {s: estimate_chain([r["seq"] for r in rs]) for s, rs in by_sid.items()}
    output = []
    for i in range(math.ceil(len(training) * ratio)):
        template = training[int(rng.integers(len(training)))]
        sid = template["scenario"]
        T, init = models[sid]
        seq = [int(rng.choice(NT, p=init))]
        for _ in range(len(template["seq"])-1):
            seq.append(int(rng.choice(NT, p=T[seq[-1]])))
        output.append(dict(id=f"markov_{seed}_{i}", scenario=sid, seq=seq,
                           group=digest(seq), synthetic=True, length_source=template["id"]))
    return output


def quality(synthetic, training):
    seqs = [tuple(r["seq"]) for r in synthetic]
    originals = {tuple(r["seq"]) for r in training}
    bg, base = grams(synthetic), grams(training)
    keys = sorted(set(bg) | set(base))
    p = np.array([base[k] for k in keys], float); p /= max(1,p.sum())
    q = np.array([bg[k] for k in keys], float); q /= max(1,q.sum())
    m = (p+q)/2
    def kl(a):
        live = a > 0
        return float(np.sum(a[live]*np.log(a[live]/m[live])))
    lengths = [len(s) for s in seqs]
    return dict(n_sequences=len(seqs), unique_sequences=len(set(seqs)),
                duplicate_pct=100*(len(seqs)-len(set(seqs)))/max(1,len(seqs)),
                training_copy_pct=100*sum(s in originals for s in seqs)/max(1,len(seqs)),
                mean_length=float(np.mean(lengths)) if lengths else 0,
                min_length=min(lengths, default=0), max_length=max(lengths, default=0),
                known_token_pct=100*sum(0 <= t < NT for s in seqs for t in s)/max(1,sum(lengths)),
                train_observed_bigram_pct=100*sum(v for k,v in bg.items() if k in base)/max(1,sum(bg.values())),
                bigram_js_divergence_nats=(kl(p)+kl(q))/2,
                unique_techniques=len({t for s in seqs for t in s}),
                aep_valid_pct=None, operational_validity="Not evaluated; observed adjacency is not causal validity")


def windows(runs):
    X, L, Y, owners = [], [], [], []
    for r in runs:
        for t in range(1,len(r["seq"])):
            w = r["seq"][max(0,t-MAX_SEQ_LEN):t]
            row = np.full(MAX_SEQ_LEN, PAD_ID, np.int64); row[:len(w)] = w
            X.append(row); L.append(len(w)); Y.append(r["seq"][t]); owners.append(r["id"])
    return np.asarray(X), np.asarray(L), np.asarray(Y), owners


def repeat_windows(original_windows, target_count):
    """Exactly match augmented windows and optimizer updates without new information."""
    X,L,Y,owners = original_windows
    idx = np.arange(target_count) % len(Y)
    return X[idx],L[idx],Y[idx],[owners[i] for i in idx]


def metrics(prob, y, owners):
    y = np.asarray(y)
    prob = np.asarray(prob, np.float64)
    order = np.argsort(-prob, axis=1, kind="stable")
    pred = order[:,0]
    nll = -np.log(np.maximum(prob[np.arange(len(y)),y], 1e-300))
    f1 = []
    # Macro F1 over labels present in the evaluation set, with explicit support.
    for t in sorted(set(y.tolist())):
        tp = np.sum((pred == t) & (y == t))
        f1.append(float(2*tp/max(1,np.sum(pred == t)+np.sum(y == t))))
    per_run = {}
    for name in sorted(set(owners)):
        ix = np.array([o == name for o in owners])
        per_run[name] = dict(n=int(ix.sum()),top1=float(np.mean(pred[ix] == y[ix])),nll=float(nll[ix].mean()))
    return dict(n=len(y), top1=float(np.mean(pred == y)),
                top3=float(np.mean(np.any(order[:,:3] == y[:,None],axis=1))),
                top5=float(np.mean(np.any(order[:,:5] == y[:,None],axis=1))),
                macro_f1=float(np.mean(f1)), f1_label_count=len(f1),
                nll=float(nll.mean()), log_likelihood=float(-nll.sum()),
                perplexity=float(np.exp(min(700,nll.mean()))),
                run_macro_top1=float(np.mean([v["top1"] for v in per_run.values()])), per_run=per_run)


def markov_baselines(split):
    """Pooled baselines do not get the held-out scenario identity as privileged input."""
    train = split["train"]
    T,_ = estimate_chain([r["seq"] for r in train])
    _,_,y,_ = windows(train)
    p0 = FLOOR + BIGRAM_WEIGHT*np.bincount(y,minlength=NT)
    p0 /= p0.sum()
    output = {}
    for part in ("validation","test"):
        X,L,Y,owners = windows(split[part])
        output[part] = {
            "order0": metrics(np.tile(p0,(len(Y),1)),Y,owners),
            "order1": metrics(T[X[np.arange(len(Y)),L-1]],Y,owners)}
    output["validation_selected_order"] = min(("order0","order1"),key=lambda k:output["validation"][k]["nll"])
    return output


class ReplaySource:
    def __init__(self, runs, seed):
        if not runs:
            raise ValueError("Replay pool is empty")
        self.runs, self.rng = runs, np.random.default_rng(seed)

    def next(self):
        from env_marl import EpisodeSpec, N_U
        r = self.runs[int(self.rng.integers(len(self.runs)))]
        seq = np.asarray(r["seq"],np.int64)
        return EpisodeSpec(r["scenario"],len(seq),seq.copy(),self.rng.random((N_U,len(seq))))

    def take(self,n):
        return [self.next() for _ in range(n)]


def evaluation_specs(runs, repeats, seed):
    from env_marl import EpisodeSpec,N_U
    rng = np.random.default_rng(seed)
    specs, labels = [], []
    for r in runs:
        for rep in range(repeats):
            seq = np.asarray(r["seq"],np.int64)
            specs.append(EpisodeSpec(r["scenario"],len(seq),seq.copy(),rng.random((N_U,len(seq)))))
            labels.append(dict(run=r["id"],group=r["group"],environment_repeat=rep))
    return specs,labels
