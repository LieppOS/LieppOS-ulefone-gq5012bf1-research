#!/usr/bin/env python3
"""Preserve independent proof for every frozen identity; C residuals are not acceptance."""
import csv,json,shutil,hashlib,subprocess,lzma
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[2];C=Path('/home/armol/kernel-work/platform-batch-01-cleancheck');W=C/'ws';rows=list(csv.DictReader((P/'BATCH-MANIFEST.tsv').open(),delimiter='\t'));repo_rows=list(csv.DictReader((P/'SOURCE-REPOSITORIES.tsv').open(),delimiter='\t'));repos={x['family']:x for x in repo_rows};j=json.loads((C/'comparison-B1/comparison.json').read_text());clean=json.loads((C/'cleancheck-result.json').read_text());assert len(clean['independently_stock_accepted'])==31
E=P/'evidence';(E/'build').mkdir(parents=True,exist_ok=True)
shutil.copyfile(C/'cleancheck-result.json',E/'cleancheck-result.json');shutil.copyfile(C.parent/'platform-batch-01-cleancheck.log',E/'build/cleancheck.log')
for tag in ['B1','B2']:
 O=W/'out'/tag
 for f in O.rglob('*'):
  if f.is_file() and f.suffix not in ['.ko','.stripped']:
   d=E/'build'/tag/f.relative_to(O);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
 shutil.copyfile(C/f'comparison-{tag}/comparison.json',E/f'comparison-{tag}.json')
# Compiler commands and source-derived #SYMVER witnesses retain exact bytes, compressed.
for f in (W/'src/kdm').rglob('*.cmd'):
 if not f.name.endswith('.o.cmd'):continue
 d=E/'build/compiler-commands'/f.relative_to(W/'src/kdm');d=d.with_name(d.name+'.xz');d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(lzma.compress(f.read_bytes()))
# Source hashes are read from actual compiled source/dependency files, not old build caches.
source=[]
for f in (W/'src/kdm').rglob('*'):
 if f.is_file() and f.suffix in ['.c','.h'] and not f.name.endswith('.mod.c'):
  source.append([str(f.relative_to(W/'src/kdm')),hashlib.sha256(f.read_bytes()).hexdigest()])
with (E/'SOURCE-FILES.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['path','sha256']);w.writerows(sorted(source))
parity=[];blocked=[];accepted={}
for x in j:
 m=x['module'];r=next(r for r in rows if r['filename']==m+'.ko');f=x['family'];q=repos[f];ok=m in clean['independently_stock_accepted'];res='GNU20-byte build ID only' if ok else '; '.join(x['residual'])+'; '+','.join(x['different_sections'])
 v=None
 if ok:
  src=C/'comparison-B1'/m;dst=P/f/'evidence/acceptance'/m;shutil.copytree(src,dst,dirs_exist_ok=True);v=json.loads((src/'acceptance.json').read_text())[m];accepted[m]=v
  (P/f/'evidence/acceptance').mkdir(parents=True,exist_ok=True)
 parity.append({'module_id':r['module_id'],'module':r['filename'],'initial_class':'D','final_class':'A' if ok else 'C','functions':f"{x['functions_exact']}/{x['stock_functions']}",'data':f"{x['data_exact']}/{x['stock_data']}",'crc_kcfi':'EXACT' if ok else f"IMPORT_CRC:{len(x['import_crc_mismatches'])};EXPORT_CRC:{len(x['export_crc_mismatches'])};KCFI_ABS:{len(x['kcfi_abs_mismatches'])}",'relocations':str(v['relocations'])+' RAW_AND_SEMANTIC_EXACT' if ok else 'See preserved unaccepted comparison','source_repo':q['repository'],'source_commit':q['commit'],'residual':res})
 if not ok:blocked.append({'module_id':r['module_id'],'module':r['filename'],'final_class':'C','blocker':'Stock-compatible recursive source ABI incomplete; no missing-firmware inference','mismatching_import_crcs':';'.join(sorted(x['import_crc_mismatches'])),'mismatching_export_crcs':';'.join(sorted(x['export_crc_mismatches'])),'different_sections':';'.join(x['different_sections']),'missing_operand':'OEM-matching recursive CMDQ declarations/type graph; exact differing field not yet identified','next_experiment':'Compare preserved symtypes against OEM-matching header or additional public revision; recompile all four CMDQ members and validate CRC/KCFI/counter symbols/full ELF; never patch CRC bytes','evidence':'CMDQ-MAILBOX/evidence/type-investigation; evidence/comparison-B1.json'})
for name,rs in [('BATCH-PARITY.tsv',parity),('BLOCKERS.tsv',blocked)]:
 with (P/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
(E/'acceptance.json').write_text(json.dumps(accepted,indent=2,sort_keys=True)+'\n')
for family,q in repos.items():
 own=[x for x in parity if x['source_repo']==q['repository']];doc=f'# {family} — independent batch proof\n\nSource:{q["repository"]} at `{q["commit"]}`.\n'+f'{sum(x["final_class"]=="A" for x in own)} accepted / {sum(x["final_class"]=="C" for x in own)} unaccepted.\nFresh committed clones, original development workspace and all four original recipe paths unavailable.\nRaw/stripped B1/B2 and intermediate/provider/config/source identities deterministic.\nEach accepted module has complete functions/data/sections/raw+semantic relocations/ABI ledgers.\nNo runtime/firmware closure claimed. See parent batch summary and blockers.\n';(P/family/'README.md').write_text(doc)
 n=(R/q['repository']).resolve();assert subprocess.check_output(['git','-C',str(n),'rev-parse','HEAD'],text=True).strip()==q['commit'];(P/family/'source').mkdir(exist_ok=True);subprocess.run(['git','-C',str(n),'bundle','create',str(P/family/'source'/f'{n.name}.bundle'),'--all'],check=True);(P/family/'source/COMMIT').write_text(q['commit']+'\n');shutil.copyfile(n/'SOURCE-PINS.tsv',P/family/'source/SOURCE-PINS.tsv')
state=json.loads((P/'BATCH-STATE.json').read_text());state.update(phase='31_INDEPENDENT_ACCEPTED_4_C_BLOCKERS_AUDIT_PENDING',completed_modules=[m+'.ko' for m in clean['independently_stock_accepted']],remaining_modules=[],current_module='Audit certification and final validation',latest_successful_verification=clean['result']);(P/'BATCH-STATE.json').write_text(json.dumps(state,indent=2)+'\n')
print('Independent accepted',len(accepted),'C residuals',len(blocked),'source files',len(source),'intermediate objects',clean['intermediate_object_count'])
