#!/usr/bin/env python3
"""Preserve complete independent proof and all owned ledgers; never source stock bytes."""
from pathlib import Path
import csv,json,shutil,lzma,hashlib,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-02-cleancheck');W=C/'ws';M=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));Q=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));clean=json.loads((C/'cleancheck-result.json').read_text());assert clean['result']=='PASS_ALL27_FOUR_INDEPENDENT_FAMILY_ENGINES_B1_B2'
E=P/'evidence';(E/'build').mkdir(exist_ok=True);shutil.copyfile(C/'cleancheck-result.json',E/'cleancheck-result.json');shutil.copyfile(C.parent/'platform-batch-02-cleancheck.log',E/'build/cleancheck.log');accept={};parity=[]
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
  m=r['filename'].removesuffix('.ko');src=C/f'comparison-F{i}-B1'/m;dst=FE/'acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'acceptance.json').read_text())[m];accept[m]=v
  parity.append({'module_id':r['module_id'],'module':r['filename'],'initial_class':r['initial_class'],'final_class':'A','functions_exact':f"{v['functions']}/{r['stock_functions']}",'data_exact':f"{v['data']}/{r['stock_data_objects']}",'crc_kcfi':'IMPORT_EXPORT_CRC_LICENCE_NAMESPACE_KCFI_EXACT','relocations':str(v['relocations'])+' RAW_AND_SEMANTIC_EXACT','maintained_source':q['repository'],'source_commit':q['commit'],'residual':'Parsed GNU20-byte build-ID descriptor only'})
 n=(R/q['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==q['commit'];S=P/family/'source';S.mkdir(exist_ok=True);subprocess.run(['git','-C',str(n),'bundle','create',str(S/f'{n.name}.bundle'),'--all'],check=True);(S/'COMMIT').write_text(q['commit']+'\n');shutil.copyfile(n/'SOURCE-PINS.tsv',S/'SOURCE-PINS.tsv')
 (P/family/'README.md').write_text(f'# {family} — independently accepted\n\nSource:`{q["repository"]}` at `{q["commit"]}`.\n{q["owned_count"]} owned modules full-stock-exact, GNU20-byte ID only.\nThis committed engine independently compiled joint27 B1/B2, originals unavailable.\nFull per-module function/data/ABI/section/relocation ledgers in evidence/acceptance.\nNo whole external provider or firmware/runtime closure. See batch report.\n')
# Read command bytes from the final fresh compile, not cached source objects.
for f in (W/'src/kdm').rglob('*.cmd'):
 if not f.name.endswith('.o.cmd'):continue
 d=E/'build/compiler-commands'/f.relative_to(W/'src/kdm');d=d.with_name(d.name+'.xz');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(lzma.compress(f.read_bytes()))
source=[]
for f in (W/'src/kdm').rglob('*'):
 if f.is_file() and f.suffix in ['.c','.h'] and not f.name.endswith('.mod.c'):source.append([str(f.relative_to(W/'src/kdm')),hashlib.sha256(f.read_bytes()).hexdigest()])
with (E/'SOURCE-FILES.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['path','sha256']);w.writerows(sorted(source))
with (P/'BATCH-PARITY.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(parity[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(sorted(parity,key=lambda r:next(i for i,x in enumerate(M) if x['module_id']==r['module_id'])))
(P/'BLOCKERS.tsv').write_text('module_id\tmodule\tclassification\tblocker\tmismatching_records\tevidence\tnext_experiment\n');(E/'acceptance.json').write_text(json.dumps(accept,indent=2,sort_keys=True)+'\n')
state=json.loads((P/'BATCH-STATE.json').read_text());state.update(phase='ALL27_INDEPENDENT_ACCEPTED_AUDIT_PENDING',completed_modules=[r['filename'] for r in M],remaining_modules=[],current_module='Canonical audit update',failed_modules={},latest_successful_verification=clean['result'],next_immediate_action='Certify only exact27 identities;validate audit/mutations/scope;publish next batch');(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('Preserved27 independent modules, four bundles, eight fresh compilations; totals',{k:sum(v[k] for v in accept.values()) for k in ['functions','data','imports','exports','kcfi_abs_ids','relocations']})
