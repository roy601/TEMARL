#!/usr/bin/env python3
"""Verify bundled original H-MARL and CAGE 4 bytes before optional patching."""
import argparse
import hashlib
import json
from pathlib import Path

def sha256(path):
 h=hashlib.sha256()
 with path.open('rb') as r:
  for block in iter(lambda: r.read(2**20),b''):
   h.update(block)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--root',type=Path,default=Path('.'))
 a=p.parse_args()
 root=a.root.resolve()
 manifest=json.loads((root/'source_manifest.json').read_text(encoding='utf-8'))
 checked=0; bad=[]
 for src,info in manifest['sources'].items():
  for name,expected in info['files'].items():
   f=root/name
   checked+=1
   if not f.is_file() or sha256(f)!=expected:
    bad.append(name)
 status={'status':'PASS' if not bad else 'FAIL','total_checked':checked,'mismatches':bad[:30],
         'note':'Run before metrics patch / instrumenting evaluators; these intentionally modify original files.'}
 print(json.dumps(status,indent=2))
 return 0 if not bad else 2
if __name__=='__main__':
 raise SystemExit(main())
