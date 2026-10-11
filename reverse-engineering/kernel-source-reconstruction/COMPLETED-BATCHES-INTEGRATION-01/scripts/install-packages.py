#!/usr/bin/env python3
"""Install committed original research+integration into a private owner worktree.
Default dry-run. Abort before writing on ANY existing differing package file.
No merges, evidence edits, stock writes or source repository modifications.
"""
from pathlib import Path
import argparse,subprocess,hashlib,json,os
os.sched_setaffinity(0,sorted(os.sched_getaffinity(0))[-4:]);os.nice(10)
P=Path(__file__).resolve().parents[1];R=P.parents[2]
p=argparse.ArgumentParser();p.add_argument('target',type=Path);p.add_argument('--commit',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--report',type=Path,required=True);a=p.parse_args();target=a.target.resolve()
assert target.name not in ['ulefone-gq5012bf1-research','ulefone-gq5012bf1-research-codex-all-c-closure'],'Private owner worktree required'
prefix='reverse-engineering/kernel-source-reconstruction/';packages=['AUDIO-BATCH-01','SCP-CONNECTIVITY-BATCH-01','AUDIO-DEPENDENCIES-BATCH-02','STOCK-INVENTORY-INTEGRITY','COMPLETED-BATCHES-INTEGRATION-01'];entries=[];conflicts=[]
for package in packages:
 raw=subprocess.check_output(['git','-C',str(R),'ls-tree','-rz',a.commit,'--',prefix+package])
 assert raw,'Package absent from claimed staging commit: '+package
 for record in raw.split(b'\0'):
  if not record:continue
  meta,name=record.split(b'\t',1);mode,kind,blob=meta.decode().split();assert kind=='blob' and mode in ['100644','100755']
  relative=os.fsdecode(name);data=subprocess.check_output(['git','-C',str(R),'cat-file','blob',blob]);path=target/relative
  assert path.resolve().is_relative_to(target)
  if path.exists() and path.read_bytes()!=data:conflicts.append(relative)
  entries.append((relative,mode,data))
report=dict(commit=a.commit,target=str(target),files=len(entries),conflicts=conflicts,apply=a.apply);a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
if conflicts:raise SystemExit('STOP: newer/different research overlaps; preserve both and request owner review before any writes')
if a.apply:
 for relative,mode,data in entries:
  path=target/relative
  if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data);path.chmod(0o755 if mode=='100755' else 0o644)
print(json.dumps(dict(result='INSTALLED' if a.apply else 'DRY_RUN_READY',files=len(entries),conflicts=0),indent=2))
