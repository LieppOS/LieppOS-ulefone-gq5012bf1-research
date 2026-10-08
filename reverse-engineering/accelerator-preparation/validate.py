#!/usr/bin/env python3
"""Fail-closed offline preparation validator. No reconstruction or hardware execution."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote
from inventory import HERE, REPO, WS, CA, rows

REQ=['README.md','STATUS.md','hardware-contract.md','source-lineage.md','kernel-abi.md','dependencies.md','proprietary-boundary.md','RE-PLAN.md','CLAUDE-HANDOFF.md','stock-modules.tsv','dt-nodes.tsv','source-candidates.tsv','parity-gaps.tsv']

def require(cond,msg):
 if not cond:raise AssertionError(msg)

def links(path):
 bad=[]
 for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text()):
  target=unquote(target.strip().strip('<>').split('#',1)[0])
  if target and not target.startswith(('http:','https:','mailto:')) and not (path.parent/target).exists():bad.append(str(path)+' -> '+target)
 return bad

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scope');ap.add_argument('--inputs-only',action='store_true');args=ap.parse_args()
 scopes=json.loads((HERE/'scopes.json').read_text())['scopes'];selected=[s for s in scopes if not args.scope or s['component']==args.scope];require(bool(selected),'unknown scope')
 targets={m:s['component'] for s in scopes for m in s['modules']};require(len(targets)==sum(len(s['modules']) for s in scopes),'duplicate module owner')
 owners={r['module']:r for r in rows(CA/'kernel-modules.tsv')};dt={r['compatible']:r for r in rows(CA/'device-tree.tsv')}
 for s in selected:
  n=s['component'];d=HERE/n
  require(all((d/f).is_file() and (d/f).stat().st_size for f in REQ),f'incomplete canonical scope {n}')
  handoff=(d/'CLAUDE-HANDOFF.md').read_text();require(all(f'## {i}.' in handoff for i in range(1,15)),f'incomplete fourteen-point handoff {n}')
  require('no new reconstruction' in handoff.lower() and 'PARTIAL' in handoff,f'fabricated preparation state {n}')
  mods=rows(d/'stock-modules.tsv');require({x['module'] for x in mods}==set(s['modules']),f'target inventory mismatch {n}')
  for x in mods:
   for rel in x['stock_paths'].split(';'):
    p=REPO/rel;require(p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'] and p.stat().st_size==int(x['bytes']),f'stock operand changed {rel}')
   require(x['module'] in owners,f'invented module {x["module"]}')
   if not args.inputs_only:require(owners[x['module']]['component']==n and owners[x['module']]['component_status']=='PARTIAL',f'coverage primary mismatch {x["module"]}')
  for x in rows(d/'source-candidates.tsv'):
   path=Path(x['donor']);root=Path(x['repository']);require(path.exists(),f'absent donor {path}')
   files=[path] if path.is_file() else sorted(p for p in path.rglob('*') if p.is_file() and (p.suffix in ('.c','.h','.S') or p.name in ('Makefile','Kbuild','Kconfig','BUILD.bazel')))
   digest=hashlib.sha256(''.join(f'{p.relative_to(root)}\t{hashlib.sha256(p.read_bytes()).hexdigest()}\n' for p in files).encode()).hexdigest()
   require(digest==x['input_fingerprint'],f'donor input changed since prepared snapshot {path}')
  if not args.inputs_only:
   found=[st for st in ('DONE','PARTIAL','BLOCKED','TODO') if (WS/f'Reverse Engineer - {st}'/n).is_dir()];require(found==['PARTIAL'],f'non-singleton status {n}')
   pack=WS/'Reverse Engineer - PARTIAL'/n;require(all((pack/f).is_file() for f in REQ),f'pack incomplete {n}')
   for p in pack.rglob('*.md'):require(not links(p),'pack link: '+str(links(p)))
  for p in d.rglob('*.md'):require(not links(p),'canonical link: '+str(links(p)))
 if not args.inputs_only:
  transfers=rows(HERE/'dt-ownership.tsv');keys={x['compatible'] for x in transfers};require(len(keys)==len({(x['compatible'],x['new_owner']) for x in transfers}),'duplicate compatible owner')
  for x in transfers:require(dt[x['compatible']]['component']==x['new_owner'],f'DT transfer not applied {x["compatible"]}')
  tracking=json.loads((HERE/'workspace-sync.json').read_text());mf=rows(WS/'COPY-MANIFEST.tsv');by_path={}
  for x in mf:by_path.setdefault(x['local_path'],[]).append(x)
  for rel,h in tracking.items():
   rr=by_path.get(rel,[]);p=WS/rel;require(len(rr)==1 and rr[0]['current_sha256']==h==hashlib.sha256(p.read_bytes()).hexdigest() and rr[0]['bytes']==str(p.stat().st_size),f'new pack manifest drift {rel}')
  registration=json.loads((HERE/'registration.json').read_text())
  if pin:=registration.get('metadata_source_commit'):
   for rel in tracking:
    record=by_path[rel][0];source=Path(record['original_path'])
    committed=subprocess.check_output(['git','show',pin+':'+str(source.relative_to(REPO))],cwd=REPO)
    require(record['relevant_commit']==pin and record['original_sha256']==hashlib.sha256(committed).hexdigest()==hashlib.sha256(source.read_bytes()).hexdigest(),f'committed metadata source pin drift {rel}')
  comps=rows(CA/'components.tsv');new={s['component'] for s in scopes};require(new<={x['component'] for x in comps},'new registrations missing from database')
  for x in comps:
   if x['component'] in new:require(x['status']=='PARTIAL' and x['partial_class']=='A','incorrect new component state')
  require(next(x for x in comps if x['component']=='CAMERA-HAL-ISP')['status']=='PARTIAL','parent status changed')
  require(not links(HERE.parent/'accelerator-re-roadmap.md'),'roadmap links')
  for p in HERE.rglob('*'):
   if p.is_file():require(p.suffix not in ('.ko','.img','.bin','.so','.dtb','.dtbo','.c','.o'),f'payload/private source entered preparation {p}')
 print(f'PASS: {len(selected)} complete scope handoffs; exact stock/donor inputs'+ (' (read-only inputs mode)' if args.inputs_only else '; singleton module/DT owners, PARTIAL registration, manifests, links and no payloads'))

if __name__=='__main__':main()
