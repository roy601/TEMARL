# -*- coding: utf-8 -*-
"""Corpus measures for DATASET_REPORT.md: structure, exact-copy test points, old vs new corpus,
manifestation coverage. Read-only; no model output. Run from the repo root:
    python camlds_real/measure_corpus.py
"""
import json,collections,sys,csv
sys.path.insert(0,'camlds_real'); import split_spec as sp
steps=sp.load('.'); R=collections.defaultdict(list)
for s in steps: R[s['run']].append(s)
for v in R.values(): v.sort(key=lambda s:s['start'])
# overlap vs end rounding
for r,v in R.items():
    for a,b in zip(v,v[1:]):
        if b['start']<a['end']: print('overlap',r,a['event_id'],b['event_id'],a['start'],a['end'],b['start'],b['end'])
# end rounding direction: does floor(end) precede next start
over=sum(1 for v in R.values() for a,b in zip(v,v[1:]) if b['start']<a['end']); print('n overlap',over)
# step templates
tmpl=collections.defaultdict(set)
for s in steps: tmpl[(s['base_scenario'],s['event_id'])].add(s['run'])
print('templates',len(tmpl)); print('by scenario',collections.Counter(k[0] for k in tmpl))
print('steps with occurrence>1',sum(s['occurrence']>1 for s in steps))
# sequences as parent tuples
seq={r:tuple(tuple(s['techniques_parent']) for s in v) for r,v in R.items()}
c=collections.Counter(seq.values()); print('runs',len(seq),'distinct parent sequences',len(c),'dups',[v for v in c.values() if v>1])
# exact context duplicates per family (no model output)
def pts(names,w=16):
    o=[]
    for r in names:
        v=R[r]
        for i in range(1,len(v)):
            ctx=tuple(tuple(s['techniques_parent']) for s in v[max(0,i-w):i]); o.append((ctx,tuple(v[i]['techniques_parent'])))
    return o
for fam,ex in ((sp.FAMILY_PRIMARY,('2_cron','2_rootkit')),(sp.FAMILY_SECONDARY,())):
    tot=dup=dupctx=0; by=collections.Counter(); byn=collections.Counter()
    for f in sp.folds(steps,fam):
        if f['fold'] in ex: continue
        tr=pts(sorted({s['run'] for s in f['train']})); te=pts(sorted({s['run'] for s in f['test']}))
        T=set(tr); C={x[0] for x in tr}
        d=sum(x in T for x in te); dc=sum(x[0] in C for x in te); tot+=len(te); dup+=d; dupctx+=dc
        k=f['fold'].split('_')[0]; by[k]+=d; byn[k]+=len(te)
    print(fam,'points',tot,'exact (window+target) also in train',dup,f'{dup/tot:.1%}','window also in train',dupctx,f'{dupctx/tot:.1%}',{k:f'{by[k]/byn[k]:.0%}' for k in byn})
# label frequency
par=collections.Counter(t for s in steps for t in s['techniques_parent'])
print('labels',len(par),'once',sum(v==1 for v in par.values()),'<=3',sum(v<=3 for v in par.values()),'top5',par.most_common(5))
# which labels occur in only one scenario
sc=collections.defaultdict(set)
for s in steps:
    for t in s['techniques_parent']: sc[t].add(s['base_scenario'])
print('labels in one scenario only',sum(len(v)==1 for v in sc.values()))
print('step label count dist',sorted(collections.Counter(len(s['techniques_parent']) for s in steps).items()))
same=sum(1 for v in R.values() for a,b in zip(v,v[1:]) if a['techniques_parent']==b['techniques_parent']); tot=sum(len(v)-1 for v in R.values()); print('self-loop transitions',same,tot,f'{same/tot:.1%}')

# ---- old vs new corpus, manifestation coverage ----
import json,collections,sys,csv,re
sys.path.insert(0,'camlds_real'); import split_spec as sp
new=sp.load('.'); N=collections.defaultdict(list)
for s in new: N[s['run']].append(s)
for v in N.values(): v.sort(key=lambda s:s['start'])
newseq={r:[(frozenset(s['techniques_parent']),tuple(s['techniques_sub'])) for s in v] for r,v in N.items()}
d=json.load(open('Temarl_Test_v1_L1/thesis_system/data/camlds_commands.json',encoding='utf-8'))
R=d['runs']; R=R if isinstance(R,list) else list(R.values())
oldseq={r['source_path']:[(frozenset(t.split('.')[0] for t in c['techniques']),tuple(c['techniques'])) for c in r['commands']] for r in R}
def m(q):
    st=[x for v in q.values() for x in v]; tr=[(a[0],b[0]) for v in q.values() for a,b in zip(v,v[1:])]
    c=collections.Counter(tr); par=collections.Counter(t for x in st for t in x[0]); sub={t for x in st for t in x[1]}
    return dict(runs=len(q),steps=len(st),sub_labels=len(sub),parent_labels=len(par),sub_instances=sum(len(x[1]) for x in st),parent_instances=sum(par.values()),
      multi_label_steps=sum(len(x[1])>1 for x in st),transitions=len(tr),distinct_transitions=len(c),singleton_transitions=sum(v==1 for v in c.values()),self_loops=sum(a==b for a,b in tr),labels_once=sum(v==1 for v in par.values()),labels_le3=sum(v<=3 for v in par.values()),per_scenario=dict(sorted(collections.Counter(k.replace('scenario_','')[0] for k,v in q.items() for _ in v).items())),runs_by_scen=dict(sorted(collections.Counter(k.replace('scenario_','')[0] for k in q).items())))
a,b=m(oldseq),m(newseq)
for k in a: print(f'{k:<24} old {a[k]}  | new {b[k]}')
po={t for v in oldseq.values() for x in v for t in x[0]}; pn={t for v in newseq.values() for x in v for t in x[0]}
print('parents only old',sorted(po-pn)); print('parents only new',sorted(pn-po)); print('shared',len(po&pn))
so={t for v in oldseq.values() for x in v for t in x[1]}; sn={t for v in newseq.values() for x in v for t in x[1]}
print('subs only old',sorted(so-sn)); print('subs only new',sorted(sn-so))
print('vocab in old study', len(json.load(open('Temarl_Test_v1_L1/thesis_system/data/camlds_grounding_verified.json',encoding='utf-8')).get('vocab',[])) if 0 else '')
# manifestation coverage
ev=collections.defaultdict(set)
for s in new: ev[s['run']].add(s['event_id'])
step=collections.defaultdict(set); seqf=collections.defaultdict(set)
pat=re.compile(r'^manifestations_(filtered|raw)/(steps|sequences)/([^/]+)-([0-9_]+)/')
seen=set()
for r in csv.DictReader(open('camlds_real/FULL_INVENTORY.csv',newline='',encoding='utf-8')):
    if r['archive'].startswith('manifest') and r['path'] not in seen:
        m_=pat.match(r['path'])
        if m_:
            f=m_.group(1)+'/'+m_.group(2)+'/'+m_.group(3)+'-'+m_.group(4)
            if f in seen: continue
            seen.add(f)
            for e in m_.group(4).split('_'):
                (step if m_.group(2)=='steps' else seqf)[(m_.group(1),m_.group(3))].add(int(e))
for kind in('filtered','raw'):
    tot=mis=0; ms=[]
    for r,e in ev.items():
        h=step.get((kind,r),set())|seqf.get((kind,r),set()); tot+=len(e); x=e-h; mis+=len(x)
        if x: ms.append((r,sorted(x)[:8]))
    print(kind,'events',tot,'without a manifestation folder',mis,ms[:6])
