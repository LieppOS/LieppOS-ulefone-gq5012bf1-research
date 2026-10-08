#!/usr/bin/env python3
"""Scoped, non-destructive synchronization of six accelerator preparation packs.
No status moves, source reconstruction, blanket manifest rebuild or unrelated repair.
Use --copy-packs, then --register --research-commit <committed preparation revision>.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote
from inventory import HERE, REPO, WS

def digest(b):return hashlib.sha256(b).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--copy-packs',action='store_true');ap.add_argument('--register',action='store_true');ap.add_argument('--refresh-registration',action='store_true');ap.add_argument('--research-commit');args=ap.parse_args()
 cfg=json.loads((HERE/'scopes.json').read_text());scopes=cfg['scopes'];names={s['component'] for s in scopes}
 tracking=HERE/'workspace-sync.json';old=json.loads(tracking.read_text()) if tracking.exists() else {}
 if args.copy_packs:
  written={}
  for s in scopes:
   src=HERE/s['component'];pack=WS/'Reverse Engineer - PARTIAL'/s['component']
   assert pack.is_dir(),f'create authorized PARTIAL directory first: {pack}'
   for other in ('DONE','BLOCKED','TODO'):assert not (WS/f'Reverse Engineer - {other}'/s['component']).exists(),'component already exists in another status'
   files=sorted(p for p in src.rglob('*') if p.is_file())
   assert all(p.suffix in ('.md','.tsv') for p in files),'payload/nonmetadata file in preparation'
   for p in files:
    dest=pack/p.relative_to(src);b=p.read_bytes()
    if p.suffix=='.md':
     def link(m):
      target=m.group(1).strip().strip('<>');raw=unquote(target.split('#',1)[0])
      if not raw or raw.startswith(('http:','https:','mailto:')):return m.group(0)
      resolved=(p.parent/raw).resolve()
      if resolved.is_relative_to(src):return m.group(0)
      new=os.path.relpath(resolved,dest.parent);frag='#'+target.split('#',1)[1] if '#' in target else ''
      return '](<'+new+frag+'>)'
     b=re.sub(r'\]\(([^)]+)\)',link,b.decode()).encode()
    rel=str(dest.relative_to(WS))
    if dest.exists():assert digest(dest.read_bytes())==old.get(rel),f'concurrent/foreign modification: {dest}'
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);written[rel]=digest(b)
  tracking.write_text(json.dumps(written,indent=2,sort_keys=True)+'\n');print('copied',len(written),'metadata/doc files; external links rebased, no payloads')
 if args.register:
  assert args.research_commit,'pin committed research source'
  assert tracking.exists(),'copy and verify packs before registration'
  original_status=(WS/'REVERSE-ENGINEERING-STATUS.md').read_bytes();text=original_status.decode()
  for s in scopes:
   n=s['component']
   if re.search(r'^\| \[`'+re.escape(n)+r'`\]',text,re.M):raise AssertionError(f'already registered: {n}; do not overwrite')
  newrows=[]
  for s in scopes:
   n=s['component'];pre=f'Reverse Engineer - PARTIAL/{n}'
   newrows.append(f'| [`{n}`](<{pre}/README.md>) | Accelerators / {s["title"]} normal-world kernel | PARTIAL | Exact stock/DT/source metadata and singleton ownership; no new parity | Preparation/handoff only; existing proof axes retained | Complete module/ABI/B1-B2 closure | UNKNOWN until parity accepted | Local candidate, not accepted replacement | [`CLAUDE-HANDOFF.md`](<{pre}/CLAUDE-HANDOFF.md>) | {cfg["date"]} |')
  pos=text.index('\n## BLOCKED');text=text[:pos].rstrip()+'\n'+'\n'.join(newrows)+'\n'+text[pos:]
  counts={s:len([p for p in (WS/f'Reverse Engineer - {s}').iterdir() if p.is_dir()]) for s in ('DONE','PARTIAL','BLOCKED','TODO')}
  for s,c in counts.items():text=re.sub(r'^\| '+s+r' \| \d+ \|$',f'| {s} | {c} |',text,flags=re.M)
  text=re.sub(r'^\| \*\*Total\*\* \| \*\*\d+\*\* \|$',f'| **Total** | **{sum(counts.values())}** |',text,flags=re.M)
  text+=f'\n## Accelerator preparation ({cfg["date"]})\n\nSix justified PARTIAL additions ({", ".join(sorted(names))}); CAMERA-HAL-ISP remains PARTIAL for proprietary HAL/3A/tuning. Module/DT ownership transfers are recorded in research `reverse-engineering/accelerator-preparation/`; no unrelated merges/removals/renames or source reconstruction. Preparation source commit `{args.research_commit}`. Current directory total: {sum(counts.values())}. Historical 133-component snapshot remains historical.\n'
  mf=WS/'COPY-MANIFEST.tsv';original_manifest=mf.read_bytes();dr=csv.DictReader(io.StringIO(original_manifest.decode()),delimiter='\t');fields=dr.fieldnames;records=list(dr)
  existing={x['local_path'] for x in records};adds=[]
  for rel,h in sorted(json.loads(tracking.read_text()).items()):
   assert rel not in existing,'existing manifest registration; do not overwrite'
   p=WS/rel;assert digest(p.read_bytes())==h,'pack changed after sync'
   n=p.relative_to(WS).parts[1];src=HERE/n/Path(*p.relative_to(WS).parts[2:]);row={k:'' for k in fields}
   row.update(status='PARTIAL',component=n,local_path=rel,current_sha256=h,bytes=str(p.stat().st_size),artifact_origin='research-derived',original_path=str(src),original_repo='ulefone-gq5012bf1-research',relevant_commit=args.research_commit,original_sha256=digest(src.read_bytes()),kind_or_provenance='accelerator preparation metadata/doc; external Markdown links rebased only')
   adds.append(row)
  out=io.StringIO();wr=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(records+adds)
  # Fail if concurrent global edits happened since the read; never replace foreign rows.
  assert (WS/'REVERSE-ENGINEERING-STATUS.md').read_bytes()==original_status and mf.read_bytes()==original_manifest,'concurrent global edit: reconcile before registering'
  (WS/'REVERSE-ENGINEERING-STATUS.md').write_text(text);mf.write_text(out.getvalue())
  (HERE/'registration.json').write_text(json.dumps(dict(date=cfg['date'],research_commit=args.research_commit,added_components=sorted(names),status_counts=counts,manifest_rows_added=len(adds),previous_status_sha256=digest(original_status),previous_manifest_sha256=digest(original_manifest),current_status_sha256=digest(text.encode()),current_manifest_sha256=digest(out.getvalue().encode())),indent=2,sort_keys=True)+'\n')
  (HERE/'registration-manifest.tsv').write_text('\t'.join(fields)+'\n'+''.join('\t'.join(x[k] for k in fields)+'\n' for x in adds))
  print('registered',len(scopes),'PARTIAL components;',len(adds),'actual files; totals',counts)

 if args.refresh_registration:
  # Update only our 146 rows plus the explicitly changed parent/status index.
  import subprocess
  mf=WS/'COPY-MANIFEST.tsv';before=mf.read_bytes();dr=csv.DictReader(io.StringIO(before.decode()),delimiter='\t');fields=dr.fieldnames;records=list(dr)
  previous={x['local_path']:x for x in csv.DictReader((HERE/'registration-manifest.tsv').open(),delimiter='\t')}
  tracking_data=json.loads(tracking.read_text());registration=json.loads((HERE/'registration.json').read_text());changed=[]
  for row in records:
   rel=row['local_path']
   if rel in tracking_data:
    assert row['current_sha256']==previous[rel]['current_sha256'],'foreign manifest edit'
    p=WS/rel;src=Path(row['original_path']);assert digest(p.read_bytes())==tracking_data[rel],'foreign pack edit'
    if args.research_commit:
     committed=subprocess.check_output(['git','show',args.research_commit+':'+str(src.relative_to(REPO))],cwd=REPO)
     assert committed==src.read_bytes(),'source is not committed at the requested pin'
     row['relevant_commit']=args.research_commit
    changed.append(dict(local_path=rel,previous_sha256=row['current_sha256'],current_sha256=tracking_data[rel],reason='owned accelerator metadata refreshed'))
    row.update(current_sha256=tracking_data[rel],bytes=str(p.stat().st_size),original_sha256=digest(src.read_bytes()))
   elif rel=='Reverse Engineer - PARTIAL/CAMERA-HAL-ISP/README.md':
    p=WS/rel;body=p.read_text();marker='\n## Current ownership correction — 2026-10-08\n';end='Source reconstruction and prior function/data proofs remain in their original paths; no private source or firmware was copied or deleted.\n'
    assert marker in body and end in body,'unexpected parent edit'
    original=body[:body.index(marker)]+body[body.index(end)+len(end):]
    expected=registration.get('camera_parent_sha256',row['current_sha256'])
    assert digest(original.encode())==row['current_sha256'] or digest(p.read_bytes())==expected,'concurrent parent modification'
    h=digest(p.read_bytes());changed.append(dict(local_path=rel,previous_sha256=row['current_sha256'],current_sha256=h,reason='authorized parent ownership correction; historical evidence retained'))
    row.update(current_sha256=h,bytes=str(p.stat().st_size));registration['camera_parent_sha256']=h
   elif rel=='REVERSE-ENGINEERING-STATUS.md':
    p=WS/rel;h=digest(p.read_bytes());assert h==registration['current_status_sha256'],'concurrent global status edit'
    changed.append(dict(local_path=rel,previous_sha256=row['current_sha256'],current_sha256=h,reason='six authorized PARTIAL additions and current totals'))
    row.update(current_sha256=h,bytes=str(p.stat().st_size))
  assert set(previous)==set(tracking_data),'unexpected registration file set'
  out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(records)
  assert mf.read_bytes()==before,'concurrent manifest edit'
  mf.write_text(out.getvalue());registration['current_manifest_sha256']=digest(out.getvalue().encode())
  if args.research_commit:registration['metadata_source_commit']=args.research_commit
  (HERE/'registration.json').write_text(json.dumps(registration,indent=2,sort_keys=True)+'\n')
  (HERE/'manifest-refresh.json').write_text(json.dumps(changed,indent=2,sort_keys=True)+'\n')
  out=io.StringIO();w=csv.DictWriter(out,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x for x in records if x['local_path'] in tracking_data)
  (HERE/'registration-manifest.tsv').write_text(out.getvalue());print('refreshed',len(changed),'explicitly owned manifest records; unrelated drift preserved')

if __name__=='__main__':main()
