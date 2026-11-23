"""Isolated HTTP services for an executable DAT integration experiment.

All sockets bind to 127.0.0.1 on OS-assigned ports. Fault controls are deliberately
test-only endpoints. This is not a vendor H4 adapter or a production proxy.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse, hashlib, json, threading, time, urllib.request

def serve(role,protected=0,decoy=0):
    routes={}
    seen={}
    lock=threading.RLock()
    counts={'apply_mutations':0,'delete_mutations':0,'requests':0}
    service_state={'healthy':True}
    def digest(obj):
        return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    def expire():
        while True:
            with lock:
                for key,r in list(routes.items()):
                    if time.monotonic()>=r['expires_at'] and r['fault']!='stale_ttl':
                        del routes[key]
                        counts['delete_mutations']+=1
            time.sleep(.005)
    class Handler(BaseHTTPRequestHandler):
        protocol_version='HTTP/1.0'
        def log_message(self,*args): pass
        def reply(self,obj,code=200):
            data=json.dumps(obj,sort_keys=True).encode()
            self.send_response(code)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def read(self):
            length=int(self.headers.get('Content-Length','0'))
            if length>65536: raise ValueError('payload too large')
            return json.loads(self.rfile.read(length) or b'{}')
        def authorized(self):
            return self.headers.get('X-Test-Management-Key')=='local-integration-test'
        def do_GET(self):
            with lock: counts['requests']+=1
            if role!='proxy':
                self.reply({'service':role,'healthy':service_state['healthy'],'path':self.path},200 if service_state['healthy'] else 503)
                return
            if self.path=='/_admin/state':
                if not self.authorized(): self.reply({'error':'unauthorized'},403); return
                with lock:
                    self.reply({'routes':routes,'counts':counts})
                return
            with lock:
                r=next((dict(v) for v in routes.values() if v['match']==self.path),None)
            destination=r['destination'] if r else protected
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{destination}{self.path}',timeout=2) as res:
                    obj=json.load(res)
                self.reply(obj)
            except Exception as exc:
                self.reply({'error':'upstream_unavailable','type':type(exc).__name__},502)
        def do_POST(self):
            if not self.authorized(): self.reply({'error':'unauthorized'},403); return
            body=self.read()
            if role!='proxy':
                service_state['healthy']=body.get('healthy',True)
                self.reply({'healthy':service_state['healthy']}); return
            if self.path=='/_admin/reset':
                with lock: routes.clear(); seen.clear()
                self.reply({'reset':True}); return
            if self.path!='/_admin/apply': self.reply({'error':'not_found'},404); return
            if body.get('zone')!='isolated-test' or not body.get('match','').startswith('/test-session/') or body.get('destination')!=decoy:
                self.reply({'error':'scope_denied'},403); return
            if not .05<=float(body.get('ttl',0))<=5.:
                self.reply({'error':'ttl_denied'},403); return
            txn=body['transaction_id']; fingerprint=digest(body)
            with lock:
                if txn in seen:
                    if seen[txn]!=fingerprint: self.reply({'error':'idempotency_conflict'},409); return
                    self.reply({'ack':True,'replayed':True,'transaction_id':txn}); return
                if any(r['match']==body['match'] for r in routes.values()):
                    self.reply({'error':'scope_in_use'},409); return
                seen[txn]=fingerprint
                fault=body.get('fault','none')
                r={**body,'expires_at':time.monotonic()+body['ttl'],'version':1,'delete_attempts':0}
                if fault=='state_divergence': r['destination']=protected
                routes[txn]=r
                counts['apply_mutations']+=1
            if fault=='ack_lost':
                self.close_connection=True
                return
            self.reply({'ack':True,'replayed':False,'transaction_id':txn})
        def do_DELETE(self):
            if not self.authorized(): self.reply({'error':'unauthorized'},403); return
            txn=self.path.removeprefix('/_admin/routes/')
            with lock:
                r=routes.get(txn)
                if r:
                    r['delete_attempts']+=1
                    if r['fault']=='rollback_persistent' or (r['fault']=='rollback_transient' and r['delete_attempts']==1):
                        self.reply({'error':'injected_delete_rejection'},503); return
                    del routes[txn]
                    counts['delete_mutations']+=1
                self.reply({'removed':bool(r),'transaction_id':txn})
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    server.daemon_threads=True
    if role=='proxy': threading.Thread(target=expire,daemon=True).start()
    print(json.dumps({'port':server.server_port,'role':role}),flush=True)
    server.serve_forever(poll_interval=.05)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('role',choices=['protected','decoy','proxy'])
    p.add_argument('--protected',type=int,default=0)
    p.add_argument('--decoy',type=int,default=0)
    a=p.parse_args()
    serve(a.role,a.protected,a.decoy)
