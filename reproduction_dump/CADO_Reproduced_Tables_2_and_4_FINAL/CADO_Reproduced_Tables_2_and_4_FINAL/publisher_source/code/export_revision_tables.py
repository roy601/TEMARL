"""Generate LaTeX tables from archived CSVs (standard library only)."""
from pathlib import Path
import csv,json,collections
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'revision_results/latex_tables'
OUT.mkdir(exist_ok=True)
def read(path):
    with (ROOT/path).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(name,text): (OUT/name).write_text(text,encoding='utf-8')
def table(caption,label,cols,head,rows,note=''):
    return (r'\begin{table}[t]'+'\n'+r'\caption{\revised{'+caption+r'}}\label{'+label+'}\n'+
      r'\begin{adjustwidth}{-\extralength}{0cm}'+'\n'+r'\begin{revision}\footnotesize\setlength{\tabcolsep}{4pt}\renewcommand{\arraystretch}{1.2}'+'\n'+
      r'\begin{tabularx}{\fulllength}{'+cols+'}\n'+r'\toprule'+'\n'+head+r'\\\midrule'+'\n'+'\n'.join(rows)+'\n'+r'\bottomrule\end{tabularx}'+'\n'+
      (r'\par\vspace{3pt}\noindent '+note+'\n' if note else '')+r'\end{revision}\end{adjustwidth}\end{table}'+'\n')
MET=['utility','redirection_precision','engagement_rate','benign_false_redirect_rate','unsafe_action_rate','normalized_cost']
LABEL=['Defensive utility','Redirection precision','Engagement rate','Benign false redirects','Unsafe actions','Normalized cost']
fmt=lambda m,x: f'{float(x):.{6 if m in MET[3:5] else 5 if m==MET[5] else 4}f}'
primary=read('submitted_results/summary_statistics.csv')
rows=[]
for m,label in zip(MET,LABEL):
    cells=[label]
    for policy in ['Static','Adaptive','Consensus','CADO']:
        r=next(x for x in primary if x['dataset']=='primary' and x['policy']==policy and x['metric']==m)
        cells.append(fmt(m,r['mean'])+r'\newline ['+fmt(m,r['ci_low'])+', '+fmt(m,r['ci_high'])+']')
    rows.append(' & '.join(cells)+r'\\\addlinespace[3pt]')
write('primary.tex',table(r'Primary results: means and percentile bootstrap 95\% confidence intervals; 30 paired seeds.','tab2','@{}L{1.2}L{0.95}L{0.95}L{0.95}L{0.95}@{}',r'\textbf{Metric} & \textbf{Static} & \textbf{Adaptive} & \textbf{Consensus} & \textbf{CADO}',rows))
abl=read('submitted_results/ablation_summary.csv')
summ=read('revision_results/heldout_summary_statistics.csv')
rows=[]
policy_order={'primary':['Consensus','CADO','CADO-NoEvidence','CADO-NoNoninferiority','CADO-BoundedOnly'],'ood':['Consensus','CADO','CADO-NoOOD','CADO-BoundedOnly']}
names={'Consensus':'Consensus','CADO':'Full CADO','CADO-NoEvidence':'No evidence gate','CADO-NoNoninferiority':'No confidence/value gates','CADO-NoOOD':'No OOD gate','CADO-BoundedOnly':'Bounded residual only'}
for ds,order in policy_order.items():
    for policy in order:
        if policy=='Consensus':
            source=primary if ds=='primary' else summ
            r={m:next(x['mean'] for x in source if x['policy']==policy and x['metric']==m and (ds!='primary' or x['dataset']=='primary')) for m in MET}
            r['fallback_rate']=1
        else:r=next(x for x in abl if x['dataset']==ds and x['policy']==policy)
        cells=['Primary' if ds=='primary' else 'Held-out',names[policy]]+[fmt(m,r[m]) for m in ['utility','redirection_precision','benign_false_redirect_rate','unsafe_action_rate']]+[f'{float(r["fallback_rate"]):.4f}']
        rows.append(' & '.join(cells)+r'\\\addlinespace[2pt]')
    if ds=='primary': rows.append(r'\midrule')
write('ablation.tex',table(r'Safety-gate ablation and the Consensus reference for both datasets. Values are means of 30 seed-level summaries.','tab3','@{}l L{1.6}L{0.8}L{0.9}L{0.9}L{0.9}L{0.9}@{}',r'\textbf{Dataset} & \textbf{Variant} & \textbf{Utility} & \textbf{Precision} & \textbf{Benign false redirects} & \textbf{Unsafe actions} & \textbf{Fallback}',rows,'For Consensus, fallback 1.0000 denotes selection of its own reference action by definition, not a measured gate-rejection rate. For CADO variants, fallback denotes rejection of personalization.'))
pairs=read('revision_results/heldout_paired_statistical_comparisons.csv')
rows=[]
for m,label in zip(MET,LABEL):
    cells=[label]
    for policy in ['Consensus','CADO']:
        r=next(x for x in summ if x['policy']==policy and x['metric']==m)
        cells.append(fmt(m,r['mean'])+r'\newline ['+fmt(m,r['ci_low'])+', '+fmt(m,r['ci_high'])+']')
    r=next(x for x in pairs if x['metric']==m and x['comparison']=='CADO - Consensus')
    cells.append(f'{float(r["mean_difference"]):.6f}'+r'\newline ['+f'{float(r["ci_low"]):.6f}, {float(r["ci_high"]):.6f}]')
    p=float(r['p_holm']);cells.extend([f'{p:.6f}' if p<1 else '1.000',f'{float(r["effect_size_dz"]):.3f}'])
    rows.append(' & '.join(cells)+r'\\\addlinespace[3pt]')
write('heldout.tex',table(r'Held-out CADO versus Consensus: means, paired differences, 95\% bootstrap intervals, and two-sided paired tests ($n=30$ seeds).','tab:heldout','@{}L{1.16}L{1.12}L{1.12}L{1.3}L{0.8}L{0.5}@{}',r'\textbf{Metric} & \textbf{Consensus} & \textbf{CADO} & \textbf{CADO minus Consensus} & \textbf{Holm $p$} & \textbf{$d_z$}',rows,'Intervals use 10,000 seed-level resamples. Holm adjustment covers all 18 held-out baseline--metric comparisons, as in the primary analysis. All-zero paired differences are reported with $p=1$ and $d_z=0$ by convention, not as proof of equivalence.'))
comp=read('revision_results/sensitivity_paired_comparisons.csv')
settings=json.loads((ROOT/'revision_results/sensitivity_settings.json').read_text())
families=collections.defaultdict(list)
for s in settings:families[s['family']].append(s['name'])
rows=[]
order=['default','risk weights','action thresholds','evidence gate','OOD gate','confidence gate','uncertainty margin','residual bound','outcome capture','outcome resource cost','outcome benign harm','joint threshold and margin']
for family in order:
    labels=families[family];cells=[family if family.startswith('OOD') else family.capitalize(),str(len(labels))]
    for ds,m in [('primary','utility'),('ood','utility'),('primary','unsafe_action_rate')]:
        values=[float(r['difference']) for r in comp if r['setting'] in labels and r['dataset']==ds and r['metric']==m]
        lo,hi=min(values),max(values)
        cells.append(f'{lo:.6f}' if lo==hi else f'{lo:.6f} to {hi:.6f}')
    rows.append(' & '.join(cells)+r'\\\addlinespace[2pt]')
write('sensitivity.tex',table('Descriptive sensitivity ranges for CADO-minus-Consensus mean differences across all 26 configurations. Each configuration uses the same 30 paired seeds.','tab:sensitivity','@{}L{1.2}L{0.45}L{1.15}L{1.15}L{1.05}@{}',r'\textbf{Perturbation family} & \textbf{Settings} & \textbf{Primary utility difference} & \textbf{Held-out utility difference} & \textbf{Primary unsafe-rate difference}',rows,'These are ranges across configurations, not confidence intervals. The held-out unsafe-rate difference was zero in every tested configuration. Configuration-level paired intervals, precision, costs, and fallback rates are provided in S1.'))
poc=json.loads((ROOT/'revision_results/poc_summary.json').read_text())
descriptions={'verified_expiry':('Verified expiry','Route expired; protected path restored'),'duplicate_apply':('Duplicate application','One mutation; duplicate acknowledged idempotently'),'ack_lost':('Lost acknowledgement','Installed state found; compensation verified'),'state_divergence':('Divergent state','Wrong destination rejected by verification'),'telemetry_unavailable':('Unavailable telemetry','Probe failure triggered compensation'),'stale_ttl':('Stale actuator TTL','Coordinator detected residual route and removed it'),'rollback_transient':('Transient rollback error','Second deletion attempt restored the path'),'rollback_persistent':('Persistent rollback error','Failure retained after three attempts; escalation required'),'unauthorized_scope':('Unauthorized scope','HTTP 403; no route installed'),'idempotency_conflict':('Conflicting identifier reuse','HTTP 409; original request not overwritten')}
rows=[]
for x in poc['cases']:
    title,desc=descriptions[x['case']]
    restored='Not applicable' if x['case']=='unauthorized_scope' else str(x['restored'])+'/30'
    rows.append(f'{title} & {x["passed"]}/30 & {restored} & {desc}'+r'\\\addlinespace[3pt]')
write('prototype.tex',table('Local HTTP prototype: expected protocol outcomes in 30 repetitions per case.','tab:poc','@{}L{1.0}L{0.65}L{0.85}L{1.5}@{}',r'\textbf{Test case} & \textbf{Expected outcome met} & \textbf{Path restored} & \textbf{Observed behavior}',rows,'All 300 trials met their stated acceptance criteria. Persistent rollback failure is an expected failure outcome, not successful recovery. Unauthorized requests made no state change. Test-fixture cleanup after persistent failure is excluded from recovery counts.'))
print('Generated five tables from archived results:',OUT)
