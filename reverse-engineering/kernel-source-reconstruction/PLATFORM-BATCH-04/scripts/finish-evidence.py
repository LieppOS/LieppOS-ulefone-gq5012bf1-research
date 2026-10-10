#!/usr/bin/env python3
"""Preserve all30 independent builds; only25 whole-accepted candidates certify A."""
from pathlib import Path
import csv,json,shutil,subprocess,lzma,hashlib,collections
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-04-cleancheck');W=C/'ws';M=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));Q=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));clean=json.loads((C/'cleancheck-result.json').read_text());assert clean['fresh_complete_compilations']==6 and clean['accepted_each_run']==25 and clean['explicit_unaccepted_each_run']==5
E=P/'evidence';(E/'build').mkdir(exist_ok=True);shutil.copyfile(C/'cleancheck-result.json',E/'cleancheck-result.json');shutil.copyfile(C.parent/'platform-batch-04-cleancheck.log',E/'build/cleancheck.log');accept={};parity=[];blockers=[]
for i,q in enumerate(Q):
 family=q['family'];FE=P/family/'evidence';FE.mkdir(parents=True,exist_ok=True)
 for tag in ['B1','B2']:
  O=W/f'out/F{i}-{tag}'
  for f in O.rglob('*'):
   if f.is_file() and f.suffix not in ['.ko','.stripped']:
    d=E/f'build/F{i}-{tag}'/f.relative_to(O);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
  shutil.copyfile(C/f'comparison-F{i}-{tag}/comparison.json',FE/f'comparison-{tag}.json')
 for r in M:
  if r['dependency_group']!=family:continue
  m=r['filename'].removesuffix('.ko');src=C/f'comparison-F{i}-B1'/m
  if src.exists():
   dst=FE/'acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'acceptance.json').read_text())[m];accept[m]=v;cls='A';fns=f"{v['functions']}/{r['stock_functions']}";data=f"{v['data']}/{r['stock_data_objects']}";rel=str(v['relocations'])+' RAW_AND_SEMANTIC_EXACT';res='Parsed GNU20-byte build-ID descriptor only'
  else:
   src=C/f'comparison-F{i}-B1/incomplete'/m;dst=FE/'incomplete-acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'incomplete-acceptance.json').read_text());cls='C';fns=f"{v['axes']['functions']['named_body_exact']}/{r['stock_functions']}";data=f"{v['axes']['data']['named_body_exact']}/{r['stock_data_objects']}";rel=str(v['relocation_records_stock'])+(' RAW_AND_SEMANTIC_EXACT' if v['raw_and_semantic_relocations_exact'] else ' UNMATCHED_SEE_LEDGER');res='Eight TCPC function bodies, timer data, source tokens and consequent ELF layout/relocations' if m=='tcpc_class' else 'Source tokens/srcversion plus counter-symbol/modinfo differences' if m=='tcpc_mt6375' else 'Srcversion-only source-token mismatch beyond GNU20; strict C, never normalized';blockers.append({'module_id':r['module_id'],'module':r['filename'],'classification':'C','blocker':res,'mismatching_records':','.join(v['unmatched_names']['functions']+v['unmatched_names']['data']),'evidence':str((dst/'incomplete-acceptance.json').relative_to(P)),'next_experiment':v['next_experiment']})
  parity.append({'module_id':r['module_id'],'module':r['filename'],'initial_class':r['initial_class'],'final_class':cls,'functions_exact':fns,'data_exact':data,'crc_kcfi':'IMPORT_EXPORT_CRC_LICENSE_NAMESPACE_KCFI_EXACT','relocations':rel,'maintained_source':q['repository'],'source_commit':q['commit'],'residual':res})
 n=(R/q['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==q['commit'];S=P/family/'source';S.mkdir(exist_ok=True);subprocess.run(['git','-C',str(n),'bundle','create',str(S/f'{n.name}.bundle'),'--all'],check=True);(S/'COMMIT').write_text(q['commit']+'\n');shutil.copyfile(n/'SOURCE-PINS.tsv',S/'SOURCE-PINS.tsv')
 (P/family/'README.md').write_text(f'# {family} — independent full-source builds\n\nSource:`{q["repository"]}` at `{q["commit"]}`.\n{q["owned_count"]} owned compiled;{q["development_exact"]} whole-stock accepted A candidates; other owned targets explicitly C with complete mismatch ledgers. This committed engine independently built all30B1/B2, originals unavailable. No external provider/firmware/runtime closure. See batch report.\n')
for f in (W/'src/kdm').rglob('*.cmd'):
 if f.name.endswith('.o.cmd'):
  d=E/'build/compiler-commands'/f.relative_to(W/'src/kdm');d=d.with_name(d.name+'.xz');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(lzma.compress(f.read_bytes()))
source=[]
for f in (W/'src/kdm').rglob('*'):
 if f.is_file() and f.suffix in ['.c','.h'] and not f.name.endswith('.mod.c'):source.append([str(f.relative_to(W/'src/kdm')),hashlib.sha256(f.read_bytes()).hexdigest()])
with (E/'SOURCE-FILES.tsv').open('w') as f:w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['path','sha256']);w.writerows(sorted(source))
shutil.copyfile(W/'kout/.config',E/'generated-vendor.config')
with (P/'BATCH-PARITY.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(parity[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(sorted(parity,key=lambda r:next(i for i,x in enumerate(M) if x['module_id']==r['module_id'])))
with (P/'BLOCKERS.tsv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(blockers[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(blockers)
(E/'acceptance.json').write_text(json.dumps(accept,indent=2,sort_keys=True)+'\n')
state=json.loads((P/'BATCH-STATE.json').read_text());state.update(phase='ALL30_INDEPENDENT_SOURCE_BUILT_25_ACCEPTED_FIVE_C_AUDIT_PENDING',processed_modules=[r['filename'] for r in M],completed_modules=[r['module'] for r in parity if r['final_class']=='A'],pending_modules=[r['module'] for r in parity if r['final_class']=='C'],current_module='Preserve hardware/source proof; certify25 only; bounded remaining5 revisit',latest_parity_result=clean['result'],independent_validation_status='PASS30deterministic/25wholeaccepted/5explicitunaccepted',next_immediate_action='Verify every C/H against public5e/public31/complete169historical sources/commonIIO and freshrecover3bundles; actualsource/hardware/provider contracts, strict23ELFcases. Update exact30rows25A5C, all428nonselectedunchanged incloldCMDQ/ADC. Bounded5revisit thenreport/next25-40/localcommits.');(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n');print('Preserved30 independent source builds,25accepted5strictC,3bundles; accepted totals',{k:sum(v[k] for v in accept.values()) for k in ['functions','data','imports','exports','kcfi_abs_ids','relocations']})
