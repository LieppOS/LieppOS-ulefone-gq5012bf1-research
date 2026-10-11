#!/usr/bin/env python3
"""Durable exact development evidence; NEVER promotes before independent proof."""
from pathlib import Path
import csv,json,subprocess,shutil
P=Path(__file__).resolve().parents[1];R=P.parents[2];ROOT=R.parent;W=Path('/home/armol/kernel-work/next-dg-batch-01');rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));result=[];source=[]
for group,repo,tag,folder in [('MTK-SYSTEM-DIAGNOSTICS','android_kernel_modules_platform_diagnostics_ulefone_gq5012bf1','D1','development-D1'),('MET-INSTRUMENTATION','android_kernel_modules_met_instrumentation_ulefone_gq5012bf1','D3','development-MET-D3')]:
 d=ROOT/repo;commit=subprocess.check_output(['git','-C',str(d),'rev-parse','HEAD'],text=True).strip();assert not subprocess.check_output(['git','-C',str(d),'status','--porcelain'],text=True)
 source.append(dict(family=group,repository=repo,commit=commit,source_pin=d.joinpath('SOURCE-PINS.tsv').read_text().splitlines()[-1],development_acceptance='ALL_OWNED_WHOLE_STOCK_GNU20_PASS',independent_status='PENDING'))
 for r in rows:
  if r['source_family']!=group:continue
  m=r['filename'].removesuffix('.ko');a=json.loads((P/'evidence'/folder/m/'acceptance.json').read_text())[m];assert a['unresolved']==0 and a['stock_sha256']==r['stock_sha256']
  result.append(dict(module_id=r['module_id'],module=m,initial_class='D',final_class='D',classification_note='DEVELOPMENT_EXACT_NOT_YET_INDEPENDENTLY_CERTIFIED',functions=str(a['functions'])+'/'+str(a['functions']),data=str(a['data'])+'/'+str(a['data']),crc_kcfi='EXACT_'+str(a['imports'])+'_IMPORTS_'+str(a['exports'])+'_EXPORTS_'+str(a['kcfi_abs_ids'])+'_KCFI_IDS',relocations='RAW_AND_SEMANTIC_EXACT_'+str(a['relocations']),source_repo=repo,source_commit=commit,residual='NONE_IN_DEVELOPMENT_GNU20_ONLY; B1/B2/bundle proof pending',evidence='evidence/'+folder+'/'+m+'/acceptance.json'))
for f,rs in [('BATCH-PARITY.tsv',result),('SOURCE-REPOSITORIES.tsv',source)]:
 with (P/f).open('w') as fp:w=csv.DictWriter(fp,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
s=json.loads((P/'BATCH-STATE.json').read_text());s.update(phase='ALL_22_DEVELOPMENT_EXACT_SOURCE_COMMITTED_INDEPENDENT_PROOF_PENDING',targets_processed=22,source_reconstruction_state='All22 complete genuine sources compiled and whole-stock GNU20-only accepted; no final A promotion before B1/B2',independent_build_state='NEXT_FRESH_CLONES_NO_DEV_REUSE',source_commits={r['repository']:r['commit'] for r in source},next_action='Quarantine only own development workspaces; fresh committed-source B1/B2 for both families, compare all objects/config/source/natural symvers; run mutations/bundles; narrow audit')
s['targets']={r['module_id']:dict(build='DEVELOPMENT_COMPLETE',parity='WHOLE_STOCK_GNU20_EXACT',source_commit=r['source_commit'],final_class='D_PENDING_INDEPENDENT_PROOF',next='B1/B2') for r in result};(P/'BATCH-STATE.json').write_text(json.dumps(s,indent=2)+'\n')
E=P/'evidence/development-driver-logs';E.mkdir(exist_ok=True)
for p in (W/'dev').glob('*.log'):shutil.copyfile(p,E/p.name)
for family in ['diagnostics','met']:
 for tag in (W/'dev'/family/'out').iterdir():
  dest=E/family/tag.name;dest.mkdir(parents=True,exist_ok=True)
  for f in tag.iterdir():
   if f.is_file() and f.suffix not in ['.ko','.stripped']:shutil.copyfile(f,dest/f.name)
  if (tag/'provider').exists():shutil.copytree(tag/'provider',dest/'provider',dirs_exist_ok=True)
print('All22 development exact; maintained source committed; independent promotion still0')
