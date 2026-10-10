#!/usr/bin/env python3
"""Preserve independent all34 source/determinism proof; only full-accepted33 certify A."""
from pathlib import Path
import csv,json,shutil,lzma,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-03-cleancheck');W=C/'ws';M=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));Q=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));clean=json.loads((C/'cleancheck-result.json').read_text());assert clean['result']=='PASS_ALL34_FIVE_INDEPENDENT_FAMILY_ENGINES_B1_B2' and clean['accepted_each_run']==33 and clean['explicit_C_blockers_each_run']==1
E=P/'evidence';(E/'build').mkdir(exist_ok=True);shutil.copyfile(C/'cleancheck-result.json',E/'cleancheck-result.json');shutil.copyfile(C.parent/'platform-batch-03-cleancheck.log',E/'build/cleancheck.log');accept={};parity=[]
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
  m=r['filename'].removesuffix('.ko')
  if m=='thermal-generic-adc':
   src=C/f'native-F{i}-B1';dst=FE/'incomplete-acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'incomplete-acceptance.json').read_text());cls='C';residual='21 BTF type/string-reference bytes; all other axes exact, no full A/B'
  else:
   src=C/f'comparison-F{i}-B1'/m;dst=FE/'acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'acceptance.json').read_text())[m];accept[m]=v;cls='A';residual='Parsed GNU20-byte build-ID descriptor only'
  parity.append({'module_id':r['module_id'],'module':r['filename'],'initial_class':r['initial_class'],'final_class':cls,'functions_exact':f"{v['functions']}/{r['stock_functions']}",'data_exact':f"{v['data']}/{r['stock_data_objects']}",'crc_kcfi':'IMPORT_EXPORT_CRC_LICENCE_NAMESPACE_KCFI_EXACT','relocations':str(v['relocations'])+' RAW_AND_SEMANTIC_EXACT','maintained_source':q['repository'],'source_commit':q['commit'],'residual':residual})
 n=(R/q['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==q['commit'];S=P/family/'source';S.mkdir(exist_ok=True);subprocess.run(['git','-C',str(n),'bundle','create',str(S/f'{n.name}.bundle'),'--all'],check=True);(S/'COMMIT').write_text(q['commit']+'\n');shutil.copyfile(n/'SOURCE-PINS.tsv',S/'SOURCE-PINS.tsv')
 (P/family/'README.md').write_text(f'# {family} — independent full-source build\n\nSource:`{q["repository"]}` at `{q["commit"]}`.\n{q["owned_count"]} owned modules compiled; {q["development_exact"]} full-stock-exact A, GNU20-byte ID only.\nNative common ADC, if owned, remains C for 21 BTF bytes; all code/data/ABI/relocations/layout exact.\nThis committed engine independently compiled joint34 B1/B2 with originals unavailable.\nFull per-module ledgers in evidence/acceptance; incomplete ADC separately preserved.\nNo whole external provider or firmware/runtime closure. See batch report.\n')
for root,subdir in [(W/'src/kdm','vendor'),(W/'native-kout/drivers/thermal','native')]:
 for f in root.rglob('*.cmd'):
  if not f.name.endswith('.o.cmd'):continue
  d=E/'build/compiler-commands'/subdir/f.relative_to(root);d=d.with_name(d.name+'.xz');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(lzma.compress(f.read_bytes()))
source=[]
for f in (W/'src/kdm').rglob('*'):
 if f.is_file() and f.suffix in ['.c','.h'] and not f.name.endswith('.mod.c'):source.append([str(f.relative_to(W/'src/kdm')),hashlib.sha256(f.read_bytes()).hexdigest()])
with (E/'SOURCE-FILES.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['path','sha256']);w.writerows(sorted(source))
shutil.copyfile(W/'native-kout/.config',E/'native-generated.config');shutil.copyfile(W/'kout/.config',E/'generated-vendor.config')
with (P/'BATCH-PARITY.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(parity[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(sorted(parity,key=lambda r:next(i for i,x in enumerate(M) if x['module_id']==r['module_id'])))
native=json.loads((P/'THERMAL-COOLING/evidence/incomplete-acceptance/thermal-generic-adc/incomplete-acceptance.json').read_text())
with (P/'BLOCKERS.tsv').open('w') as f:
 fields=['module_id','module','classification','blocker','mismatching_records','evidence','next_experiment'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerow(dict(module_id=native['module_id'],module='thermal-generic-adc.ko',classification='C',blocker=native['blocker'],mismatching_records='21 bytes at .BTF offsets:'+','.join(map(str,native['btf_differing_offsets'])),evidence='THERMAL-COOLING/evidence/incomplete-acceptance/thermal-generic-adc/incomplete-acceptance.json',next_experiment=native['next_experiment']))
(E/'acceptance.json').write_text(json.dumps(accept,indent=2,sort_keys=True)+'\n')
state=json.loads((P/'BATCH-STATE.json').read_text());state.update(phase='ALL34_INDEPENDENT_SOURCE_BUILT_33_ACCEPTED_ONE_C_AUDIT_PENDING',processed_modules=[r['filename'] for r in M],completed_modules=[r['module'] for r in parity if r['final_class']=='A'],pending_modules=['thermal-generic-adc.ko'],current_module='Canonical audit update; preserve native ADC C',latest_parity_result=clean['result'],independent_validation_status='PASS34 deterministic,33 whole stock accepted;1 explicitly unaccepted C BTF',next_immediate_action='Update exact34 rows:33A and1C; validate all other424 rows unchanged; mutations, source/public hashes, bundles, hardware/provider research and next batch');(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('Preserved all34,33 accepted/1C, five bundles, ten fresh builds; accepted totals',{k:sum(v[k] for v in accept.values()) for k in ['functions','data','imports','exports','kcfi_abs_ids','relocations']})
