"""Every measured value has a human-readable Markdown report; no invented scores."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from markov_training import write_json


def read(p):
    return json.loads(p.read_text(encoding="utf-8"))


def table(headers,rows):
    def cell(x):
        if x is None:
            return "N/A"
        if isinstance(x,float):
            return f"{x:.5f}"
        return str(x).replace("|","/").replace("\n"," ")
    return ["| "+" | ".join(headers)+" |","|"+"---|"*len(headers)]+["| "+" | ".join(cell(x) for x in row)+" |" for row in rows]


def mean_sd(x,scale=1.):
    a=np.asarray(x,float)*scale
    return "Pending" if not len(a) else f"{a.mean():.3f} +/- {a.std(ddof=1):.3f}" if len(a)>1 else f"{a.mean():.3f} (n=1; SD N/A)"


def paired(a,b,name,metric):
    seeds=sorted(set(a)&set(b))
    d=np.array([a[s]-b[s] for s in seeds])
    if len(d)<2:
        return dict(contrast=name,metric=metric,n=len(d),delta=float(d.mean()) if len(d) else None,ci95=None,p_raw=None,p_holm=None)
    sd=float(d.std(ddof=1)); mean=float(d.mean())
    half=float(stats.t.ppf(.975,len(d)-1)*sd/np.sqrt(len(d)))
    p=float(stats.ttest_1samp(d,0).pvalue) if sd>1e-15 else (1. if abs(mean)<1e-15 else 0.)
    return dict(contrast=name,metric=metric,n=len(d),delta=mean,ci95=[mean-half,mean+half],p_raw=p,p_holm=None)


def holm(rows):
    valid=[r for r in rows if r["p_raw"] is not None]
    last=0.
    for i,r in enumerate(sorted(valid,key=lambda r:r["p_raw"])):
        last=max(last,min(1.,r["p_raw"]*(len(valid)-i))); r["p_holm"]=last


def records(out,kind,fp):
    rows=[]
    for p in sorted((out/kind).glob("*/result.json")):
        r=read(p)
        if r["fingerprint"] != fp:
            raise ValueError(f"Mismatched result: {p}")
        rows.append(r)
    return rows


def epoch_report(out,rows):
    lines=["# Every encoder epoch", "", "All values are measured on training or validation data. No test curve is used for selection.",
           "Percent columns are percentages; loss is mean negative log likelihood (nats).", ""]
    for r in rows:
        name=f"{r.get('condition',{}).get('name','pilot')} / {r['encoder']} / seed {r['seed']}"
        lines += [f"## {name}","",f"Primary checkpoint epoch: {r['epochs_completed']}; validation-best (secondary): {r['selected_epoch']}.",""]
        lines += table(["Epoch","Updates","Train NLL","Val NLL","Train Top-1 %","Val Top-1 %","Val Top-3 %","Val Top-5 %","Val Macro-F1 %","Val PPL","Seconds"],
                       [[c["epoch"],c["updates"],c["train"]["nll"],c["validation"]["nll"],100*c["train"]["top1"],100*c["validation"]["top1"],
                         100*c["validation"]["top3"],100*c["validation"]["top5"],100*c["validation"]["macro_f1"],c["validation"]["perplexity"],c["seconds"]] for c in r["curve"]])
        lines += [""]
    (out/"EPOCH_RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


def report(out):
    out=Path(out); manifest=read(out/"manifest.json"); audit=read(out/"audit.json")
    cfg=manifest["config"]
    pred=records(out,"prediction",manifest["fingerprint"])
    rl=records(out,"rl",manifest["fingerprint"])
    pilot=records(out,"pilot",manifest["fingerprint"])
    complete=len(pred)==manifest["expected_prediction_cells"] and len(rl)==manifest["expected_rl_cells"]
    confidence_cells=records(out/"confidence","cells",manifest["fingerprint"])
    confidence_expected=manifest.get("expected_confidence_cells",0)
    complete=complete and len(confidence_cells)==confidence_expected
    epoch=read(out/"epoch_selection.json") if (out/"epoch_selection.json").exists() else None
    lines=["# Markov augmentation usefulness study", "",
           "**SMOKE TEST ONLY: NOT THESIS EVIDENCE.**" if cfg["smoke"] else "**COMPLETE**" if complete else "**INCOMPLETE: pending cells must not be interpreted as final results.**", "",
           f"Prediction cells: {len(pred)}/{manifest['expected_prediction_cells']}. Deception cells: {len(rl)}/{manifest['expected_rl_cells']}.",
           f"Confidence ablation cells: {len(confidence_cells)}/{confidence_expected}. [Confidence results](CONFIDENCE_RESULTS.md) | [All confidence records](CONFIDENCE_DETAILS.md).",
           f"Training seeds: {cfg['seeds']}. Source SHA256: `{audit['source_sha256']}`.", "",
           "The source is an AttackBed-derived playbook corpus. Test sequences are original held-out playbook sequences, not raw real-world logs.",
           "Means +/- sample SD are across training seeds. Repeated windows and environment rollouts are not additional independent attack campaigns.", "",
           "## Exact Markov model", "",audit["markov"]["name"]+".",
           "`P(j|i,s) = (0.02 + 4*C_s(i,j)) / (84*0.02 + 4*sum_k C_s(i,k))`.",
           "`P(first=j|s) = (0.02 + 2*start_count_s(j)) / (84*0.02 + 2*n_runs_s)`.",
           "This is an observed-state first-order chain, fitted separately for each training scenario. It is not an HMM or MCMC sampler.",
           "Lengths are sampled from same-scenario training runs. Smoothing permits unseen transitions; these are not newly observed attack evidence.", "",
           "## Protocol and epoch budget", "",
           "Split complete runs before windowing; group duplicates after the existing parent-technique mapping. Same held-out runs across all cells.",
           "The 25/50/75/100% learning curve uses nested scenario-stratified training groups; small scenarios are retained, so achieved fractions differ from requested percentages.",
           "Augmentation doses add 25/50/100/200% as many synthetic sequences as original training sequences (rounded up). No concatenation into artificial long campaigns.",
           "Repeat controls use original prediction windows repeated to exactly match each augmented condition's windows, batches and updates per epoch.",
           "Main cells complete every epoch. PRIMARY results use the final common epoch. Validation-best checkpoint results are secondary and separately labeled. Test loss never selects anything.",
           "PPO epochs are separate: the same PPO passes per rollout and environment-step budget apply to every IPPO/MAPPO arm.", ""]
    if epoch:
        lines += [f"**Shared encoder budget: {epoch['epochs']} epochs.** Selection: {epoch['method']}.",
                  "Pilot cap reached/approached: "+str(epoch["cap_warning"])+". A cap warning means convergence has not been established.", ""]
    else:
        lines += ["Epoch budget pending. Default: real-only validation pilots for all three encoders, capped at 100 epochs; take the maximum validation-best epoch across pilots.", ""]
    lines += ["[Every epoch](EPOCH_RESULTS.md) | [Per-seed and per-run metrics](DETAILED_RESULTS.md) | [Human-readable predictions](PREDICTION_EXAMPLES.md) | [Every RL validation point](RL_LEARNING_CURVES.md)", "",
              "## 1. Transition sparsity and coverage", ""]
    keys=["runs","independent_groups","steps","unique_techniques","unique_bigrams","unique_trigrams","singleton_bigrams","unseen_transition_occurrence_pct","unseen_transition_type_pct","unseen_technique_occurrence_pct","mean_outgoing","mathematical_pair_coverage_pct"]
    lines += table(["Measure","Train","Validation","Test"],[[k]+[audit["coverage"][s][k] for s in ("train","validation","test")] for k in keys])
    lines += ["", "Unseen means absent from training. The 84 x 84 denominator is a mathematical upper bound, not the set of operationally possible transitions. Sparsity alone does not prove augmentation is needed.", ""]
    lines += ["- "+n for n in audit["notes"]]
    lines += ["", "### Remaining similarity between variants", ""]
    lines += table(["Split","Held-out run","Nearest training run","Bigram Jaccard"],[[r[k] for k in ("split","run","nearest_training_run","bigram_jaccard")] for r in audit["similarities"]])
    lines += ["", "## 2. Markov order and held-out next-technique performance", "",
              "Order-0 and order-1 baselines pool training scenarios and never receive test scenario identity. The validation winner is descriptive; the tested generator remains the inherited per-scenario first-order model.", ""]
    rows=[]
    for part in ("validation","test"):
        for order,m in audit["baseline"][part].items():
            rows.append([part,order,m["n"],m["log_likelihood"],m["nll"],m["perplexity"],100*m["top1"],100*m["top3"],100*m["top5"]])
    lines += table(["Split","Order","Windows","Log likelihood","NLL","PPL","Top-1 %","Top-3 %","Top-5 %"],rows)
    lines += ["", "Validation-selected baseline: **"+audit["baseline"]["validation_selected_order"]+"**.",
              "AIC/BIC are omitted: the inherited weighted, smoothed estimator is not an unconstrained maximum-likelihood fit. Held-out log likelihood is the selection criterion.", "",
              "## 3. Original-data learning curve and augmentation ablation", "",
              "All three encoders use the same selected epoch budget. Accuracy equals Top-1 and is not duplicated as a separate statistic. Macro-F1 averages labels with test support.", ""]
    grouped=defaultdict(list)
    for r in pred:
        grouped[(r["condition"]["name"],r["encoder"])].append(r)
    rows=[]
    for c in manifest["conditions"]:
        for arm in ("Transformer","GRU","LSTM"):
            rs=grouped[(c["name"],arm)]
            rows.append([c["name"],arm,len(rs)]+[mean_sd([r["test"][k] for r in rs],100 if k in ("top1","top3","top5","macro_f1","run_macro_top1") else 1) for k in ("top1","top3","top5","macro_f1","nll","perplexity","run_macro_top1")])
    lines += table(["Condition","Encoder","Seeds","Top-1 %","Top-3 %","Top-5 %","Macro-F1 %","NLL","PPL","Run-macro Top-1 %"],rows)
    lines += ["", "### Secondary: validation-best checkpoints", "",
              "These checkpoints may have different selected epochs. Primary comparisons and downstream encoders use the final common epoch instead.", ""]
    secondary=[]
    for (name,arm),rs in sorted(grouped.items()):
        if rs:
            secondary.append([name,arm,len(rs),mean_sd([r["selected_epoch"] for r in rs]),
                              mean_sd([r["test_best"]["top1"] for r in rs],100),
                              mean_sd([r["test_best"]["nll"] for r in rs])])
    lines += table(["Condition","Encoder","Seeds","Selected epoch","Test Top-1 %","Test NLL"],secondary)
    lines += ["", "## 4. Paired evidence for augmentation", "",
              "Primary prediction metric: Top-1. Paired tests compare matched training seeds; 95% t intervals describe seed variability conditional on this fixed split. Holm correction covers all listed prediction contrasts. These intervals do not establish population-wide campaign generalization.", ""]
    tests=[]
    for c in manifest["conditions"]:
        if c["kind"] != "markov":
            continue
        for arm in ("Transformer","GRU","LSTM"):
            a={r["seed"]:r["test"]["top1"] for r in grouped[(c["name"],arm)]}
            for control in ("real_100",c["name"].replace("markov","repeat")):
                b={r["seed"]:r["test"]["top1"] for r in grouped[(control,arm)]}
                tests.append(paired(a,b,f"{arm}: {c['name']} minus {control}","top1"))
    pred_complete=len(pred)==manifest["expected_prediction_cells"]
    if pred_complete and not cfg["smoke"]:
        holm(tests)
    lines += table(["Contrast","Paired seeds","Delta (fraction)","95% CI","Raw p","Holm p"],[[t[k] for k in ("contrast","n","delta","ci95","p_raw","p_holm")] for t in tests])
    verdicts=[]
    for c in manifest["conditions"]:
        if c["kind"] != "markov":
            continue
        for arm in ("Transformer","GRU","LSTM"):
            pair=[t for t in tests if t["contrast"].startswith(f"{arm}: {c['name']} minus ")]
            if cfg["smoke"]:
                verdict="Smoke only; no scientific verdict"
            elif not pred_complete or any(t["p_holm"] is None for t in pair):
                verdict="Pending sufficient completed seeds"
            elif all(t["delta"] >= .01 and t["ci95"][0] > 0 and t["p_holm"] < .05 for t in pair):
                verdict="Prediction benefit criteria met; operational validity still untested"
            else:
                verdict="Benefit criteria not met under this protocol"
            verdicts.append([c["name"],arm,verdict])
    lines += [""]+table(["Dose","Encoder","Decision against both controls"],verdicts)
    lines += ["", "Interpretation rule: a positive mean alone is inconclusive. A candidate benefit needs a positive paired interval, Holm p < 0.05, and at least +0.01 absolute Top-1 against both original-only and its repeat control. This is a predeclared practical threshold, not a universal standard. Sequence plausibility must be evaluated separately.",
              "A flat/noisy curve gives no evidence of benefit; it does not prove equivalence or establish that real additional campaigns would be useless.", "",
              "## 5. Synthetic sequence quality", "",
              "Every generated corpus is saved under synthetic/. Statistical resemblance does not validate causal or executable attack behavior. AEP validity is N/A because no AEP validator is bundled.", ""]
    qrows=[]
    for r in pred:
        if r["encoder"]=="Transformer" and r["quality"]:
            q=r["quality"]
            qrows.append([r["condition"]["name"],r["seed"]]+[q[k] for k in ("n_sequences","unique_sequences","duplicate_pct","training_copy_pct","mean_length","min_length","max_length","known_token_pct","train_observed_bigram_pct","bigram_js_divergence_nats","unique_techniques","aep_valid_pct")])
    lines += table(["Dose","Seed","Sequences","Unique","Duplicate %","Train-copy %","Mean length","Min","Max","Known IDs %","Train-observed bigrams %","Bigram JS (nats)","Techniques","AEP-valid %"],qrows)
    lines += ["", "## 6. Downstream deception: IPPO and MAPPO", "",
              "Primary downstream comparison: original-only, +100% Markov, and the +100% matched-repeat encoder control. Markov condition changes both encoder training data and policy training episodes; this estimates full-system augmentation, not an isolated encoder effect.",
              "Every policy is evaluated on identical held-out original sequences and matched environment uniforms. Repeats add simulation variation, not new attack data.",
              "Dwell = decoy-engaged steps; depth = distinct parent techniques engaged; protection = configured attacker objective not reached before termination.", ""]
    rg=defaultdict(list)
    for r in rl:
        rg[(r["condition"],r["encoder"],r["learner"])].append(r)
    rows=[]
    for cond in ("real_100","markov_100","repeat_100"):
        for arm in ("Transformer","GRU","LSTM")+(("NoHistory",) if cond=="real_100" else ()):
            for learner in ("IPPO","MAPPO"):
                rs=rg[(cond,arm,learner)]
                rows.append([cond,f"{arm} + {learner}",len(rs)]+[mean_sd([r["test_summary"][k] for r in rs],100 if k=="protected" else 1) for k in ("dwell","depth","protected")])
    lines += table(["Condition","Model","Seeds","Dwell (steps)","Depth (techniques)","Asset protection %"],rows)
    rt=[]
    for arm in ("Transformer","GRU","LSTM"):
        for learner in ("IPPO","MAPPO"):
            for control in ("real_100","repeat_100"):
                for metric in ("dwell","depth","protected"):
                    a={r["seed"]:r["test_summary"][metric] for r in rg[("markov_100",arm,learner)]}
                    b={r["seed"]:r["test_summary"][metric] for r in rg[(control,arm,learner)]}
                    rt.append(paired(a,b,f"{arm}+{learner}: markov_100 minus {control}",metric))
    if complete and not cfg["smoke"]:
        holm(rt)
    lines += ["", "### Downstream paired tests", "", "Holm correction is separate from the prediction family and includes all 36 downstream comparisons. Protection deltas are fractions, not percentage points.", ""]
    lines += table(["Contrast","Metric","Seeds","Delta","95% CI","Raw p","Holm p"],[[t[k] for k in ("contrast","metric","n","delta","ci95","p_raw","p_holm")] for t in rt])
    if complete and rl:
        scores={a:np.mean([r["val_best"] for r in rg[("real_100",a,"MAPPO")]]) for a in ("Transformer","GRU","LSTM")}
        best=max(scores,key=scores.get)
        lines += ["", "### Validation-selected original-only ablation", "",f"Selected encoder: {best}. Selection uses mean validation dwell; test results do not select the winner.", ""]
        lines += table(["Model","Dwell","Depth","Protection %"],[[f"{a}+{l}"]+[mean_sd([r["test_summary"][k] for r in rg[("real_100",a,l)]],100 if k=="protected" else 1) for k in ("dwell","depth","protected")] for a,l in ((best,"IPPO"),("NoHistory","IPPO"),(best,"MAPPO"),("NoHistory","MAPPO"))])
    lines += ["", "## 7. Generalization and limitations", "",
              f"Held-out scenario: {cfg['held_out'] or 'None: grouped variant holdout, not LOSO'}.",
              "Use --held-out S1 ... S7 in separate output folders for optional scenario holdout. Single-fold or variant results must not be labeled seven-fold LOSO.",
              "Singleton scenarios are training-only in the main split. Variant similarity remains and is reported above. Test-set size limits generalization claims.",
              audit["metadata_caveat"],
              "This source bundle contains a fixed five-zone coordinated-engagement simulator; it is not the earlier variable-topology v3 experiment.",
              "No new raw telemetry or independent incidents are created by augmentation. Preserving the estimator does not establish the validity of every generated chain.",
              "No full experiment was run during package construction. Only smoke/test outputs may be present until the lab run completes.", ""]
    (out/"RESULTS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    epoch_report(out,pilot+pred)
    detail=["# Per-seed prediction and per-original-run results","","Probabilities/accuracies are fractions unless marked percent.",""]
    examples=["# Deterministic human-readable prediction examples","","Same evenly spaced test-window indices for each model. No selection based on correctness. These are examples, not extra independent evaluations.",""]
    for r in pred:
        label=f"{r['condition']['name']} / {r['encoder']} / seed {r['seed']}"
        detail += [f"## {label}","",f"Original runs: {r['n_training_runs']}; independent groups: {r['n_original_groups']}; synthetic runs: {r['n_synthetic']}; train windows: {r['n_train_windows']}; optimizer updates: {r['optimizer_updates']}.",""]
        ms=("top1","top3","top5","macro_f1","nll","log_likelihood","perplexity","run_macro_top1","n","f1_label_count")
        detail += table(["Metric","Final-epoch validation","Final-epoch test","Validation-best test (secondary)"],[[k,r["validation"][k],r["test"][k],r["test_best"][k]] for k in ms])
        detail += [""]+table(["Test run","Windows","Top-1 %","NLL"],[[k,v["n"],100*v["top1"],v["nll"]] for k,v in r["test"]["per_run"].items()])+[""]
        examples += [f"## {label}",""]+table(["Run / window","Recent history","Actual next","Top-3 predictions and probabilities","Actual probability","Correct Top-1"],
                    [[f"{e['run']} / {e['window']}"," -> ".join(e["history"]),e["actual"]+" "+e["actual_name"],
                      "; ".join(f"{v['technique']} {v['name']} ({100*v['probability']:.2f}%)" for v in e["top3"]),f"{100*e['actual_probability']:.2f}%",e["correct"]] for e in r["examples"]])+[""]
    curves=["# Every RL validation point","","These are PPO rollout updates, not encoder epochs. Validation selects policy checkpoints.",""]
    for r in rl:
        label=f"{r['condition']} / {r['encoder']}+{r['learner']} / seed {r['seed']}"
        detail += [f"## {label}","",f"Environment steps: {r['env_steps']}; PPO epochs per rollout: {r['ppo_epochs']}; selected update: {r['best_update']}.",""]
        detail += table(["Metric","Test","Test with history zeroed"],[[k,v,r["test_h0_summary"][k]] for k,v in r["test_summary"].items()])+[""]
        detail += table(["Run","Environment repeat","Dwell","Depth","Protected","Exposed","Length"],[[v[k] for k in ("run","environment_repeat","dwell","depth","protected","exposed","length")] for v in r["test"]])+[""]
        curves += [f"## {label}",""]+table(["Update","Steps","Train dwell","Val dwell","Val depth","Seconds"],[[v[k] for k in ("update","env_steps","train_dwell","val_dwell","val_depth","seconds")] for v in r["curve"]])+[""]
    (out/"DETAILED_RESULTS.md").write_text("\n".join(detail)+"\n",encoding="utf-8")
    (out/"PREDICTION_EXAMPLES.md").write_text("\n".join(examples)+"\n",encoding="utf-8")
    (out/"RL_LEARNING_CURVES.md").write_text("\n".join(curves)+"\n",encoding="utf-8")
    write_json(out/"analysis.json",dict(complete=complete,prediction_tests=tests,rl_tests=rt))


if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("folder",type=Path)
    report(ap.parse_args().folder)
