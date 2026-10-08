#!/usr/bin/env python3
"""Explain every normalized ownership/class change against the pinned discovery commit."""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent;REPO=HERE.parent.parent;CA=HERE.parent/'coverage-audit'
sys.path.insert(0,str(CA/'scripts'))
from accelerator_owners import KERNEL_OVERRIDES,DT_OVERRIDES,COMPONENTS
cfg=json.loads((HERE/'scopes.json').read_text());baseline=cfg['discovery_head']
raw=subprocess.check_output(['git','show',baseline+':reverse-engineering/coverage-audit/artifact-map.tsv'],cwd=REPO,text=True)
old={(r['artifact_type'],r['artifact']):r for r in csv.DictReader(io.StringIO(raw),delimiter='\t')}
new={(r['artifact_type'],r['artifact']):r for r in csv.DictReader((CA/'artifact-map.tsv').open(),delimiter='\t')}
assert old.keys()==new.keys(),'unexpected global artifact discovery/removal'
changes=[]
for key,r in sorted(new.items()):
 b=old[key]
 if (b['component'],b['coverage'])==(r['component'],r['coverage']):continue
 kind,name=key
 if kind=='kernel-module':
  assert name[:-3] in KERNEL_OVERRIDES,'unexplained kernel change '+name
  reason=KERNEL_OVERRIDES[name[:-3]][2]
 elif kind=='dt-compatible':
  assert name in DT_OVERRIDES,'unexplained DT change '+name
  reason=DT_OVERRIDES[name][2]
 else:
  assert r['component'] in COMPONENTS or (kind=='firmware' and name=='firmware/ccu.img' and r['component']=='CAMERA-HAL-ISP'),'unexplained other change '+str(key)
  reason='Retained proprietary consumer/firmware assigned to its normal-world kernel-facing boundary; no source, algorithm or execution closure'
  if name=='firmware/ccu.img':reason='CCU algorithm retention is camera HAL scope; host loader/protocol is camera kernel child, not sensorhub'
 changes.append(dict(artifact_type=kind,artifact=name,previous_owner=b['component'],previous_class=b['coverage'],new_owner=r['component'],new_class=r['coverage'],reason=reason,evidence=r['evidence'],baseline_commit=baseline))
with (HERE/'ownership-delta.tsv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(changes[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(changes)
print('PASS:',len(changes),'explicitly explained ownership/class changes;',dict(Counter(x['artifact_type'] for x in changes)))
