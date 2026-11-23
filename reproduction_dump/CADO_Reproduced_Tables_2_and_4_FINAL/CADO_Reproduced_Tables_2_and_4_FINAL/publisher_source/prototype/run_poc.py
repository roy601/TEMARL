"""Run 300 local HTTP DAT trials and save auditable logs and assertions.

Usage: python prototype/run_poc.py
Three separate services are created on loopback. They are terminated at exit.
No administrative OS changes or external connections are performed.
"""
from pathlib import Path
import csv, hashlib, http.client, json, os, subprocess, sys, time
import urllib.error, urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
import run_experiments as sim
import numpy as np

OUT=ROOT/'revision_results'
OUT.mkdir(exist_ok=True)
TRIALS=30
CASES=['verified_expiry','duplicate_apply','ack_lost','state_divergence',
       'telemetry_unavailable','stale_ttl','rollback_transient','rollback_persistent',
       'unauthorized_scope','idempotency_conflict']

def canonical(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'))

def main():
    processes=[]; journal=[]; checks=[]; requests=[]
    prev='0'*64
    def record(txn,state,**kwargs):
        nonlocal prev
        body={'sequence':len(journal),'transaction_id':txn,'state':state,'monotonic_time':time.monotonic(),
              'previous_hash':prev,**kwargs}
        prev=hashlib.sha256(canonical(body).encode()).hexdigest()
        journal.append({**body,'entry_hash':prev})
    def start(role,*args):
        flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
        p=subprocess.Popen([sys.executable,str(Path(__file__).with_name('poc_services.py')),role,*map(str,args)],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=flags)
        processes.append(p)
        line=p.stdout.readline()
        if not line: raise RuntimeError(p.stderr.read())
        return json.loads(line)['port']
    def req(port,path,method='GET',data=None):
        request=urllib.request.Request(f'http://127.0.0.1:{port}{path}',
                    data=None if data is None else canonical(data).encode(),method=method,
                    headers={'Content-Type':'application/json','X-Test-Management-Key':'local-integration-test'})
        t=time.perf_counter()
        try:
            with urllib.request.urlopen(request,timeout=2) as r: status,obj=r.status,json.load(r)
        except urllib.error.HTTPError as e:
            status,obj=e.code,json.load(e)
        except (http.client.RemoteDisconnected,urllib.error.URLError,ConnectionError) as e:
            status,obj=0,{'transport_error':type(e).__name__}
        requests.append({'sequence':len(requests),'method':method,'path':path,'port':port,
                         'status':status,'elapsed_ms':(time.perf_counter()-t)*1000,'response':obj})
        return status,obj
    try:
        protected=start('protected'); decoy=start('decoy')
        proxy=start('proxy','--protected',protected,'--decoy',decoy)
        raw='CEF:0|Test|WAF|1.0|web|alert|7|src=192.0.2.10 dst=192.0.2.20 cs1=web cn1=0.850 cn2=0.800 rt=1800000000'
        nse=sim.normalize_alert('cef',raw)
        profile=np.array([.92,.28,.22,.58,.38])
        context={'criticality':.78,'stage':2,'capacity':.78,'completeness':1.}
        risk=.34*nse['confidence']+.27*nse['severity']+.22*context['criticality']+.17*context['stage']/3
        event={**nse,**context,'risk':risk,'event_id':8,'observed_features':profile}
        policy_state=sim.PolicyState(seen=8,qualified_seen=8,feature_sum=8*profile)
        action,gate=sim.choose_action('CADO',event,policy_state)
        assert action==2,'This controlled workflow requires Honeyproxy action level 2.'
        example={'raw_alert':raw,'nse':nse,'trusted_context':context,'qualified_history_count':8,
                 'qualified_history_mean':profile.tolist(),'risk':risk,'consensus_action':sim.consensus_action(event),
                 'selected_action':action,'policy_path':gate,
                 'note':'History and stage are explicit test fixtures; not inferred from the six parsed fields.'}
        (OUT/'poc_workflow_example.json').write_text(json.dumps(example,indent=2),encoding='utf-8')
        def state(): return req(proxy,'/_admin/state')[1]
        def compensate(txn):
            record(txn,'rollback_pending')
            for attempt in range(1,4):
                status,obj=req(proxy,'/_admin/routes/'+txn,'DELETE')
                current=state()
                restored_status,restored_probe=req(proxy,f'/test-session/{txn}')
                if status==200 and txn not in current['routes'] and restored_status==200 and restored_probe.get('service')=='protected':
                    record(txn,'rolled_back',attempts=attempt)
                    return True,attempt
            record(txn,'rollback_failed',attempts=3,escalation_required=True)
            return False,3
        for case in CASES:
            for index in range(TRIALS):
                req(proxy,'/_admin/reset','POST',{})
                req(decoy,'/_admin/health','POST',{'healthy':True})
                txn=f'{case}-{index:02d}'
                match=f'/test-session/{txn}'
                ttl=.20 if case in ['verified_expiry','stale_ttl'] else 5.
                dat={'transaction_id':txn,'zone':'isolated-test','match':match,'destination':decoy,'ttl':ttl,
                     'fault':case,'action':action,'expected_service':'decoy',
                     'provenance_hash':hashlib.sha256(raw.encode()).hexdigest()}
                if case=='unauthorized_scope': dat['zone']='production'
                record(txn,'proposed',dat=dat)
                record(txn,'authorized' if case!='unauthorized_scope' else 'authorization_test')
                before=state()['counts']['apply_mutations']
                t0=time.perf_counter()
                status,ack=req(proxy,'/_admin/apply','POST',dat)
                restored=False; retries=0; pass_check=False; verified=False
                unaffected=req(proxy,'/unrelated-benign-session')[1].get('service')=='protected'
                assert unaffected
                if case=='unauthorized_scope':
                    record(txn,'rejected',http_status=status)
                    pass_check=status==403 and not state()['routes']
                    # Nothing was installed: rejection is not a restoration.
                    restored=False
                elif case=='ack_lost':
                    record(txn,'ack_unknown',transport_status=status)
                    installed=txn in state()['routes']
                    restored,retries=compensate(txn)
                    pass_check=status==0 and installed and restored
                else:
                    assert status==200
                    record(txn,'applied',ack=ack)
                    if case=='duplicate_apply':
                        s2,a2=req(proxy,'/_admin/apply','POST',dat)
                        assert s2==200 and a2['replayed']
                        assert state()['counts']['apply_mutations']==before+1
                        record(txn,'duplicate_suppressed')
                    if case=='idempotency_conflict':
                        s2,a2=req(proxy,'/_admin/apply','POST',{**dat,'ttl':4.})
                        assert s2==409
                        record(txn,'conflicting_retry_rejected',http_status=s2)
                    observed=state()['routes'][txn]
                    matches=(observed['match']==match and observed['destination']==decoy
                             and observed['zone']=='isolated-test' and observed['expires_at']>time.monotonic())
                    if case=='telemetry_unavailable': req(decoy,'/_admin/health','POST',{'healthy':False})
                    probe_status,probe=req(proxy,match)
                    verified=matches and probe_status==200 and probe.get('service')=='decoy'
                    record(txn,'verified' if verified else 'verification_failed',state_match=matches,probe_status=probe_status)
                    if case in ['verified_expiry','stale_ttl']:
                        time.sleep(max(0.,observed['expires_at']-time.monotonic())+.04)
                        residual=txn in state()['routes']
                        record(txn,'expired',residual_state=residual)
                        if case=='verified_expiry':
                            restored=not residual; pass_check=verified and restored
                        else:
                            restored,retries=compensate(txn)
                            pass_check=verified and residual and restored
                    else:
                        restored,retries=compensate(txn)
                        pass_check=(not verified if case in ['state_divergence','telemetry_unavailable'] else verified)
                        if case=='rollback_persistent':
                            pass_check=pass_check and not restored and retries==3 and txn in state()['routes']
                        else: pass_check=pass_check and restored
                        if case=='rollback_transient': pass_check=pass_check and retries==2
                req(decoy,'/_admin/health','POST',{'healthy':True})
                restored_path=req(proxy,match)[1].get('service')=='protected'
                if case!='rollback_persistent': pass_check=pass_check and restored_path
                checked_other=req(proxy,'/unrelated-benign-session')[1].get('service')=='protected'
                pass_check=pass_check and checked_other
                checks.append({'case':case,'trial':index,'transaction_id':txn,'criterion_pass':pass_check,
                               'verified':verified,'route_installed':case!='unauthorized_scope',
                               'restored_by_protocol':restored,'rollback_attempts':retries,
                               'unaffected_session_preserved':unaffected and checked_other,
                               'elapsed_ms':(time.perf_counter()-t0)*1000})
                assert pass_check,(case,index,checks[-1])
                if case=='rollback_persistent':
                    # Test-fixture cleanup is explicitly outside the protocol result.
                    req(proxy,'/_admin/reset','POST',{})
                    record(txn,'test_fixture_cleanup_after_recorded_failure')
            print(case,f'{TRIALS}/{TRIALS} expected outcomes',flush=True)
    finally:
        for p in reversed(processes):
            p.terminate()
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: p.kill(); p.wait(timeout=5)
        if checks:
            with (OUT/'poc_trials.csv').open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
        for name,data in [('poc_state_journal.jsonl',journal),('poc_http_requests.jsonl',requests)]:
            (OUT/name).write_text('\n'.join(canonical(row) for row in data)+'\n',encoding='utf-8')
    summary={'trials_per_case':TRIALS,'trials':len(checks),'passed_criteria':sum(c['criterion_pass'] for c in checks),
             'requests':len(requests),'journal_entries':len(journal),
             'persistent_rollback_failures':sum(c['case']=='rollback_persistent' and not c['restored_by_protocol'] for c in checks),
             'installed_routes':sum(c['route_installed'] for c in checks),
             'restored_installed_routes':sum(c['route_installed'] and c['restored_by_protocol'] for c in checks),
             'scope':'isolated loopback HTTP software integration; not H4 or SDN hardware validation',
             'service_processes':3,'bind_address':'127.0.0.1','python':sys.version,
             'cases':[{ 'case':case,'passed':sum(c['criterion_pass'] for c in checks if c['case']==case),
                       'restored':sum(c['restored_by_protocol'] for c in checks if c['case']==case)} for case in CASES]}
    # Verify the append-only hash-chain representation without claiming secure storage.
    prev='0'*64
    for item in journal:
        body={k:v for k,v in item.items() if k!='entry_hash'}
        assert body['previous_hash']==prev
        assert hashlib.sha256(canonical(body).encode()).hexdigest()==item['entry_hash']
        prev=item['entry_hash']
    summary['journal_hash_chain_valid']=True
    (OUT/'poc_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__': main()
